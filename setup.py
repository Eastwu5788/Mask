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
        "grpcio>=1.38.0",
        "protobuf==3.16.0",
        "grpcio-tools>=1.38.0",
        "grpcio-reflection>=1.38.0",
    ],
    extras_require={
        "health": [
            "grpcio-health-checking>=1.38.0"
        ],
        "prometheus": [
        ]
    }
)
