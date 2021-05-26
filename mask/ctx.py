# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/26/21 2:13 PM'
# pylint: disable=cyclic-import
# sys
import sys
import typing as t
# project
from .globals import (
    _app_ctx_stack,
    _request_ctx_stack,
)
from .wrappers import Request


_sentinel = object()


class AppContext:
    """ 应用上下文,区分不同线程下的Application上下文
    """

    def __init__(self, app) -> None:
        self.app = app
        self.g = {}

        self._ref_cnt = 0

    def push(self) -> None:
        self._ref_cnt += 1
        _app_ctx_stack.push(self)

    def pop(self, exc: t.Optional[BaseException] = _sentinel) -> None:
        try:
            self._ref_cnt -= 1
            if self._ref_cnt <= 0:
                if exc is _sentinel:
                    exc = sys.exc_info()[1]
                # TODO: teardown 回调函数支持
        finally:
            _app_ctx_stack.pop()

    def __enter__(self) -> "AppContext":
        self.push()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.pop(exc_val)


class RequestContext:

    def __init__(self, app: "Faker", params=None, context=None) -> None:
        """ 创建请求上下文
        """
        self.app = app
        self.request = Request(params, context)

        self._implicit_app_ctx_stack: t.List[t.Optional["AppContext"]] = []

        self.preserved = False
        self._preserved_exc = None

    def push(self) -> None:
        """ 将请求上下文入栈
        """
        top = _request_ctx_stack.top
        if top is not None and top.preserved:
            top.pop(top._preserved_exc)

        # 读取当前线程下的APP上下文
        app_ctx = _app_ctx_stack.top
        if app_ctx is None or app_ctx.app != self.app:
            app_ctx = self.app.app_context()
            app_ctx.push()
            self._implicit_app_ctx_stack.append(app_ctx)
        else:
            self._implicit_app_ctx_stack.append(None)

        _request_ctx_stack.push(self)

    def pop(self, exc: t.Optional[BaseException] = _sentinel) -> None:
        """ 将请求出栈
        """
        app_ctx = self._implicit_app_ctx_stack.pop()
        try:
            if not self._implicit_app_ctx_stack:
                self.preserved = False
                self._preserved_exc = None

        finally:
            rv = _request_ctx_stack.pop()

            if app_ctx is not None:
                app_ctx.pop(exc)

            if rv is not self:
                raise RuntimeError("Popped wrong request context")

    def __enter__(self) -> "RequestContext":
        self.push()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pop(exc_val)
