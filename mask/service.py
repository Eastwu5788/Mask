# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/26/21 10:55 AM'
# sys
import typing as t
from functools import partial
from inspect import (
    getfullargspec,
    isfunction
)
# 3p
import grpc


class Service:

    _router: t.Dict[str, t.Callable] = {}

    def __init__(
            self,
            name: str,
            router: t.Optional[t.Dict[str, t.Callable]] = None
    ) -> None:
        """ Initialize service
        """
        # The name of service, this value must be the same as the value in ProtoBuf
        self.name = name

        if router and isinstance(router, dict):
            for method, func in router.items():
                self.add_method_rule(method, func)

    def route(self, method: t.Optional[str] = None) -> t.Callable:
        """ Add new route for service
        """

        def decorator(func: t.Callable) -> t.Callable:
            self.add_method_rule(method, func)
            return func

        return decorator

    def add_method_rule(
            self,
            method: t.Optional[str] = None,
            func: t.Optional[t.Callable] = None
    ) -> t.Any:
        """ Add new method handler rule
        """
        if not method or not func:
            raise ValueError("Invalid method name or handler func")

        if not isfunction(func) or not callable(func):
            raise ValueError(f"Callback func '{method}' is not callable!")

        old_func = self._router.get(method)
        if old_func is not None and old_func != func:
            raise AssertionError(f"Method is overwriting and existing: {method}")

        self._router[method] = func

    def _not_implement_method(self, context):
        """ Handler for not implement method
        """
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('Method not fund!')
        raise NotImplementedError('Method not fund!')

    def _dft_handler(self, request, context, **kwargs):
        """ Default handler
        """
        func = self._router.get(kwargs["func"], self._not_implement_method)
        args = getfullargspec(func).args

        options = {}
        if "request" in args:
            options["request"] = request
        if "context" in args:
            options["context"] = context

        return func(**options)

    def __getattr__(self, item):
        return partial(self._dft_handler, func=item)
