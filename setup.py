# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/26/21 10:06 AM'
# sys
from setuptools import setup


setup(
    name="Mask",
    install_requires=[
        "grpcio>=1.37.1",
        "protobuf>=3.16.0",
        "grpcio-tools>=1.37.1",
        "grpcio-reflection>=1.37.1"
    ]
)
