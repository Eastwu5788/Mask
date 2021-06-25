# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/26/21 10:38 AM'
# sys
import json
import typing as t
# project
from .macro import (
    K_SO_REUSEPORT,
    K_GRPC_OPTIONS,
    K_MAX_RECEIVE_MESSAGE_LENGTH,
    K_MAX_SEND_MESSAGE_LENGTH,
)


class Config(dict):
    """ Extend origin dict class
    """

    def __init__(self, config: t.Optional[t.Dict] = None) -> None:
        """ Initialize config instance
        """
        super().__init__()
        if config and isinstance(config, dict):
            self.update(config)

    def from_object(self, obj: object) -> None:
        """ Read config items from python object
        """
        for key in dir(obj):
            if not key.isupper():
                continue
            self[key] = getattr(obj, key)

    def from_dict(self, kw: dict) -> None:
        """ Read config items form dict object
        """
        for key, value in kw.items():
            if not key.isupper():
                continue
            self[key] = value

    def from_json(self, js: str, encoding: str = "UTF-8") -> None:
        """ Read config items from json
        """
        fmt_js = json.loads(js, encoding=encoding)
        if not isinstance(fmt_js, dict):
            raise TypeError("Top structure of json must be dict")
        self.from_dict(fmt_js)

    def rpc_options(self) -> list:
        """ Format gRPC options

        https://github.com/grpc/grpc/blob/v1.37.x/include/grpc/impl/codegen/grpc_types.h
        """
        options = list()

        # Default message length is 5MB
        max_send_message_length = self.get(K_MAX_SEND_MESSAGE_LENGTH, 1024 * 1024 * 5)
        max_receive_message_length = self.get(K_MAX_RECEIVE_MESSAGE_LENGTH, 1024 * 1024 * 5)

        options.append(("grpc.max_send_message_length", max_send_message_length))
        options.append(("grpc.max_receive_message_length", max_receive_message_length))

        # If non-zero, allow the use of SO_REUSEPORT if it's available (default 1)
        options.append(("grpc.so_reuseport", self.get(K_SO_REUSEPORT, True)))

        # Add other custom defined grpc options
        for option in self.get(K_GRPC_OPTIONS, list()):
            if not isinstance(option, tuple):
                continue
            options.append(option)

        return options
