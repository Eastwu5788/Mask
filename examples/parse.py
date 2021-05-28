# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/28/21 8:33 AM'
# 3p
from mask import Mask
from mask.parse import pre, Rule
# project
from examples.protos.hello_pb2 import HelloResponse


app = Mask(__name__)
app.config["REFLECTION"] = True


rule = {
    "name": Rule(type=str, gte=2, dest="Name")
}


@app.route(method="SayHello", service="Hello")
def say_hello_handler(request, context):
    """ Handler SayHello request
    """
    params = pre.parse(rule=rule, request=request, context=context)
    return HelloResponse(message="Hello Reply: %s" % params["Name"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1020)
