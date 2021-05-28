# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/26/21 10:06 AM'
# sys
from collections import defaultdict
import logging
import os
import typing as t
from concurrent import futures
# 3p
import grpc
try:
    from grpc_reflection.v1alpha import reflection
except ImportError:
    reflection = None
# project
from .config import Config
from .ctx import (
    AppContext,
    RequestContext
)
from .interceptor import (
    TracebackInterceptor,
    MiddlewareInterceptor,
)
from .logging import create_logger
from .macro import (
    K_DEBUG,
    K_MAX_WORKERS,
    K_TLS_CA_CERT,
    K_TLS_SERVER_CERT,
    K_TLS_SERVER_KEY,
    K_REFLECTION,
    K_SO_REUSEPORT,
)
from .protos import (
    scan_pb2,
    scan_pb2_grpc
)
from .service import Service
from .utils import LockedCachedProperty


class Mask:

    # Store all of the services
    _services: t.Dict[str, "Service"] = {}

    # Store all of the proto register funcs
    _register_funcs: t.Dict[str, t.Callable] = {}

    # Store mask extensions
    extensions: t.Dict[str, t.Any] = {}

    default_config = {
        K_DEBUG: False,
        K_MAX_WORKERS: 10,
        K_REFLECTION: False,
        K_SO_REUSEPORT: 1,
    }

    def __init__(self, name=None):
        """ Initialize mask server

        :param name: server name
        """
        # The name of this project
        self.name: str = name or "mask"

        # The configuration dictionary as :class:`Config`.
        self.config: "Config" = Config(self.default_config)

        # The services just like the Blueprint in flask
        # But it must be consistent with the definition in ProtoBuf
        self.services: t.Dict[str, "Service"] = {}

        # Store before request hooks
        self.before_request_funcs: t.Dict[
            t.Optional[str],
            t.List[t.Callable]
        ] = defaultdict(list)

        # Store after request hooks
        self.after_request_funcs: t.Dict[
            t.Optional[str],
            t.List[t.Callable]
        ] = defaultdict(list)

        # User defined interceptor
        self.interceptors = {}

        # Exception handler hook
        self.exc_handler_spec: t.Dict[
            t.Optional[str],
            t.Dict[t.Type[Exception], t.Callable]
        ] = defaultdict(lambda: defaultdict(dict))

    def route(
            self,
            method: t.Optional[str] = None,
            service: t.Optional[str] = None
    ) -> t.Callable:
        def decorator(func: t.Callable) -> t.Callable:
            if not service:
                raise ValueError(f"Invalid service name for method: {method}")

            s = self._services.get(service)
            if not s:
                s = Service(name=service)

            s.add_method_rule(method, func)
            self._services[service] = s
            return func
        return decorator

    def run(
            self,
            host: t.Optional[str] = None,
            port: t.Optional[int] = None,
            **kwargs: t.Any
    ) -> None:
        """ Start a gRPC server to listen port
        """
        options = self.config.rpc_options()

        interceptors = (
            TracebackInterceptor(self, self.exc_handler_spec.get(None, {})),
            MiddlewareInterceptor(self.before_request_funcs.get(None, ()),
                                  self.after_request_funcs.get(None, ())),
            *self.interceptors.get(None, ())
        )

        # Generate gRPC server
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=self.config.get(K_MAX_WORKERS, 10)),
            interceptors=interceptors,
            options=options,
        )

        # Bind service to gRPC server
        self._bind_service(server)
        # Enable gRPC server reflection feature
        self._enable_reflection(server)

        # support ipv4 and ipv6
        address = "%s:%s" % (host or "[::]", port or 9090)
        server = self._bind_port(server, address, **kwargs)
        server.start()

        self.log.info(f"Running on {address} (Press CTRL+C to quit)")  # pylint: disable=no-member
        server.wait_for_termination()
        self.log.info("gRPC server stopped!")  # pylint: disable=no-member

    @property
    def debug(self) -> bool:
        return self.config[K_DEBUG]

    @debug.setter
    def debug(self, value: bool) -> None:
        self.config[K_DEBUG] = value

    @LockedCachedProperty
    def log(self) -> logging.Logger:
        """ Auto build logger instance and cache it
        """
        return create_logger(self)

    def app_context(self):
        """ 新建一个应用上下文
        """
        return AppContext(self)

    def request_context(self, params, context):
        """ 请求上下文
        """
        return RequestContext(self, params, context)

    def before_request(self, func: t.Callable) -> t.Callable:
        """ Add custom hook function for before request
        """
        self.before_request_funcs.setdefault(None, []).append(func)
        return func

    def after_request(self, func: t.Callable) -> t.Callable:
        """ Add custom hook for after request
        """
        self.after_request_funcs.setdefault(None, []).append(func)
        return func

    def register_interceptor(self, obj: "grpc.ServerInterceptor") -> None:
        """ Add custom interceptor
        """
        if not isinstance(obj, grpc.ServerInterceptor):
            raise TypeError("Interceptor must be type of 'grpc.ServerInterceptor'")

        self.interceptors.setdefault(None, []).append(obj)

    def exception_handler(self, exception: t.Type[Exception]) -> t.Callable:
        """ Decorate for register exception handler
        """
        def decorator(func: t.Callable) -> t.Callable:
            self.register_exception_handler(exception, func)
            return func
        return decorator

    def register_exception_handler(self, exception: t.Type[Exception], func: t.Callable) -> None:
        """ Register exception handler
        """
        self.exc_handler_spec[None][exception] = func

    def register_service(self, service: Service) -> None:
        """ 将Service注册到总路由上
        """
        if not service or not isinstance(service, Service):
            raise ValueError("Invalid service to register!")

        # 防止Service多次重复注册
        if self._services.get(service.name):
            raise AssertionError(f"Service is overwriting and existing: {service.name}")

        self._services[service.name] = service

    def _bind_port(
            self,
            server: "grpc.Server",
            address: str, **options: t.Any
    ) -> "grpc.Server":
        """ bind simple port or secure port to the server and
        """
        def _read_pem(path):
            """ Load TLS files
            """
            if path is None:
                return path

            if not os.path.exists(path):
                raise FileExistsError("server tls file not exists at: %s" % path)

            with open(path, "rb") as f:
                return f.read()

        # Support TLS server
        server_cert = options.get(K_TLS_SERVER_CERT.lower()) or self.config.get(K_TLS_SERVER_CERT)
        server_key = options.get(K_TLS_SERVER_KEY.lower()) or self.config.get(K_TLS_SERVER_KEY)

        # If you want the request come from a trusted client,
        # please fill in the CA certificate
        ca_cert = options.get(K_TLS_CA_CERT.lower()) or self.config.get(K_TLS_CA_CERT)

        if not server_cert or not server_key:
            server.add_insecure_port(address)
            return server

        credentials = grpc.ssl_server_credentials(
            [(_read_pem(server_key), _read_pem(server_cert))],
            root_certificates=_read_pem(ca_cert),
            require_client_auth=bool(ca_cert)
        )
        server.add_secure_port(address, credentials)
        return server

    def _bind_service(self, server: "grpc.Server") -> None:
        """ Bind sub service to gRPC server
        """
        self._register_funcs = scan_pb2_grpc()

        for name, instance in self._services.items():
            if not isinstance(instance, Service):
                raise TypeError(f"Service instance type must be `Service`, Please check: {name}")

            func = self._register_funcs.get("add_%sServicer_to_server" % name)
            if not func:
                raise ValueError(f"Can't find service '{name}' info from ProtoBuf files!")

            # Use add_xServicer_to_server function in ProtoBuf to bind service to gRPC server
            func(instance, server)

    def _enable_reflection(self, server: "grpc.Server") -> None:
        """ Support reflection feature
        """
        if not self.config.get(K_REFLECTION):
            return

        if not reflection:
            raise ImportError("Import error for package 'grpcio-reflection'!")

        # 扫描文件，找到所有DESCRIPTOR
        descriptors, service_names = scan_pb2(), list()
        for s in self._services:
            descriptor = descriptors.get(s)
            if not descriptor:
                raise ValueError(f"Can't find descriptor for service '{s}', please check *_pb2.py file exists!")
            service_names.append(descriptor.services_by_name[s].full_name)
        reflection.enable_server_reflection((*service_names, reflection.SERVICE_NAME), server)
