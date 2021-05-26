# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/26/21 2:15 PM'
# project
from .utils import (
    CachedProperty,
    deserialize_request,
)


class Request:

    def __init__(self, request, context):
        """ 初始化Request实例

        :param request: 原始请求
        :param context: 请求上下文
        """
        self.request = request
        self.context = context

    @CachedProperty
    def headers(self):
        """ 获取请求头
        """
        if self.rpc_event is not None:
            metadata = getattr(self.rpc_event, "invocation_metadata")
            return dict(metadata)
        return None

    @CachedProperty
    def values(self):
        """ 获取请求参数
        """
        if self.request is not None:
            return deserialize_request(self.request)
        return None

    @CachedProperty
    def method(self):
        """ 获取本次请求调用的方法
        """
        if self.call_details is not None:
            method = getattr(self.call_details, "method")
            return method.decode("utf8") if method else method
        return None

    @CachedProperty
    def service(self):
        """ 获取本次请求的Service
        """
        if self.method is not None:
            return self.method.split("/")[-2]
        return None

    @CachedProperty
    def rpc_event(self):
        """ 返回RPC事件
        """
        if self.context is not None:
            return getattr(self.context, "_rpc_event")
        return None

    @CachedProperty
    def call_details(self):
        """ 返回调用详情
        """
        if self.rpc_event is not None:
            return getattr(self.rpc_event, "call_details")
        return None
