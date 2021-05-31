# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/31/21 4:35 PM'
# 3p
from mask import Mask
# project
from examples.protos.hello_pb2 import HelloResponse


app = Mask(__name__)
app.config["REFLECTION"] = True


def before_request(request, context):
    print(request.name)


def after_request(response):
    print(response.message)


app.before_request(before_request)
app.after_request(after_request)


@app.route(method="SayHello", service="Hello")
def say_hello_handler(request, context):
    """ Handler SayHello request
    """
    return HelloResponse(message="Hello Reply: %s" % request.name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1020)
