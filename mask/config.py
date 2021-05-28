# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/26/21 10:38 AM'
from .macro import (
    K_SO_REUSEPORT,
)


class Config(dict):
    """ Extend origin dict class
    """

    def __init__(self, config=None):
        """ Initialize config instance
        """
        super().__init__()
        if config and isinstance(config, dict):
            self.update(config)

    def from_object(self, obj):
        """ Read config items from python object
        """
        for key in dir(obj):
            if not key.isupper():
                continue
            self[key] = getattr(obj, key)

    def rpc_options(self):
        """ Format gRPC options

        https://github.com/grpc/grpc/blob/v1.37.x/include/grpc/impl/codegen/grpc_types.h
        """
        options = list()

        # Default message length is 5MB
        max_send_message_length = self.get("MAX_SEND_MESSAGE_LENGTH", 1024 * 1024 * 5)
        max_receive_message_length = self.get("MAX_RECEIVE_MESSAGE_LENGTH", 1024 * 1024 * 5)

        options.append(("grpc.max_send_message_length", max_send_message_length))
        options.append(("grpc.max_receive_message_length", max_receive_message_length))

        # If non-zero, allow the use of SO_REUSEPORT if it's available (default 1)
        options.append(("grpc.so_reuseport", self[K_SO_REUSEPORT]))

        return options
