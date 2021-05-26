# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/26/21 10:38 AM'


class Config(dict):
    """ Extend origin dict class
    """

    def from_object(self, obj):
        """ Read config items from python object
        """
        for key in dir(obj):
            if not key.isupper():
                continue
            self[key] = getattr(obj, key)

    def rpc_options(self):
        """ Format gRPC options
        """
        options = list()

        # Default message length is 5MB
        max_send_message_length = self.get("MAX_SEND_MESSAGE_LENGTH", 1024 * 1024 * 5)
        max_receive_message_length = self.get("MAX_RECEIVE_MESSAGE_LENGTH", 1024 * 1024 * 5)

        options.append(("grpc.max_send_message_length", max_send_message_length))
        options.append(("grpc.max_receive_message_length", max_receive_message_length))

        return options
