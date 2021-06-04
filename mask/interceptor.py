# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/26/21 2:07 PM'
# sys
import functools
import logging
import traceback
import typing as t
# 3p
import grpc
from grpc import ServerInterceptor
from grpc.experimental import wrap_server_method_handler


log = logging.getLogger(__name__)


class TracebackInterceptor(ServerInterceptor):

    def __init__(  # pylint: disable=super-init-not-called
            self,
            app,
            exc_handler_funcs: t.Dict[t.Type[Exception], t.Callable]
    ) -> None:
        """ Initialize traceback handler interceptor
        """
        self.app = app
        self.exc_handler_funcs = exc_handler_funcs

    def _handler_exception(self, e, context):
        """ Default exception Handler
        """
        error_context = None
        if isinstance(e, NotImplementedError):
            error_context = (grpc.StatusCode.UNIMPLEMENTED, "Not implemented")

        # 如果底层系统已经设置了异常，则直接返回即可
        if context._state.code != grpc.StatusCode.OK and context._state.details:
            context.abort(context._state.code, context._state.details)

        if error_context is not None:
            context.abort(error_context[0], error_context[1])

        log.error(traceback.format_exc())
        context.abort(grpc.StatusCode.INTERNAL, traceback.format_exc() if self.app.debug else "Internal Server Error")

    def _wrapper(self, behavior):
        @functools.wraps(behavior)
        def wrapper(request, context):
            ctx = self.app.request_context(request, context)
            try:
                ctx.push()
                return behavior(request, context)
            except Exception as e:
                # TODO: 通过解析 context._rpc_event.call_details，找出对应的 Service，优先回调异常
                # 通过 '__mro__' 函数依次找到异常的继承关系
                for cls in type(e).__mro__:
                    handler = self.exc_handler_funcs.get(cls)
                    if handler and callable(handler):
                        return handler(e, context)
                # 默认的系统处理方式
                return self._handler_exception(e, context)
            finally:
                ctx.pop()
        return wrapper

    def intercept_service(self, continuation, handler_call_details):
        return wrap_server_method_handler(self._wrapper, continuation(handler_call_details))


class MiddlewareInterceptor(ServerInterceptor):

    def __init__(  # pylint: disable=super-init-not-called
            self,
            before_request_chains: t.List[t.Callable],
            after_request_chains: t.List[t.Callable]
    ) -> None:
        """ 中间件拦截器
        """
        self.before_request_chains = before_request_chains
        self.after_request_chains = after_request_chains

    def _wrapper(self, behavior):
        @functools.wraps(behavior)
        def wrapper(request, context):
            # Ignore method request for reflection
            method = context._rpc_event.call_details.method
            if method.decode() == "/grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo":
                return behavior(request, context)

            # 依次处理预请求
            for chain in self.before_request_chains:
                resp = chain(request, context)
                if resp:
                    return resp
            # 实际函数处理
            response = behavior(request, context)
            # 依次处理响应
            for chain in self.after_request_chains:
                response = chain(response)
                if not response:
                    raise ValueError("Miss response from after response middleware: %s" % chain.__name__)
            return response
        return wrapper

    def intercept_service(self, continuation, handler_call_details):
        return wrap_server_method_handler(self._wrapper, continuation(handler_call_details))
