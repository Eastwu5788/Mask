# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/26/21 1:16 PM'
# sys
import logging
from logging import (
    Formatter,
    StreamHandler,
)


def _stream_fmt():
    """ 控制台日志格式
    """
    return "[%(asctime)s] %(levelname)s:%(module)s: %(message)s"


def create_logger(app) -> logging.Logger:
    """ 创建RpcServer相关的日志实例
    """
    logger = logging.getLogger(app.name)
    logger.disable_existing_loggers = False
    logger.propagate = False

    if app.debug and not logger.level:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    for h in logger.handlers:
        logger.removeHandler(h)

    default_handler = StreamHandler()
    default_handler.setFormatter(Formatter(_stream_fmt()))
    logger.addHandler(default_handler)

    return logger
