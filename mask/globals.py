# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/26/21 2:14 PM'
# sys
import typing as t
from functools import partial
# project
from .local import (
    LocalProxy,
    LocalStack
)
if t.TYPE_CHECKING:
    from .app import Mask  # pylint: disable=unused-import


def _lookup_req_object(name):
    top = _request_ctx_stack.top
    if top is None:
        raise RuntimeError("Working outside of request context")
    return getattr(top, name)


def _lookup_app_object(name):
    top = _app_ctx_stack.top
    if top is None:
        raise RuntimeError("Working outside of application context")
    return getattr(top, name)


def _find_app():
    top = _app_ctx_stack.top
    if top is None:
        raise RuntimeError("Working outside of application context")
    return top.app


_request_ctx_stack = LocalStack()
_app_ctx_stack = LocalStack()


current_app: "Mask" = LocalProxy(_find_app)
g: dict = LocalProxy(partial(_lookup_app_object, "g"))
request = LocalProxy(partial(_lookup_req_object, "request"))
