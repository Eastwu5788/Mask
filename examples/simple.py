# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/27/21 11:05 AM'
# 3p
from mask import Mask
# project
from examples.protos.hello_pb2 import HelloResponse


app = Mask(__name__)
app.config["REFLECTION"] = True
app.config["HEALTH"] = True


@app.route(method="SayHello", service="Hello")
def say_hello_handler(request, context):
    """ Handler SayHello request
    """
    return HelloResponse(message="Hello Reply: %s" % request.name)


if __name__ == "__main__":
    app.run(port=1020)
