# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2019
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '2020-03-17 15:34'
# flake8: noqa
from .simple.empty_filter import EmptyFilter
from .simple.trim_filter import TrimFilter
from .simple.length_filter import LengthFilter
from .simple.regexp_filter import RegexpFilter
from .simple.type_filter import TypeFilter
from .simple.range_filter import RangeFilter
from .simple.enum_filter import EnumFilter
from .simple.email_filter import EmailFilter
from .simple.equal_filter import EqualFilter
from .simple.mobile_filter import MobileFilter
from .simple.json_filter import JsonFilter
from .simple.default_filter import DefaultFilter
from .simple.content_filter import ContentFilter
from .simple.string_filter import StringFilter
from .simple.file_filter import FileFilter
from .simple.network_filter import NetworkFilter
from .simple.location_filter import LocationFilter
from .simple.split_filter import SplitFilter
from .simple.multi_filter import MultiFilter

from .cross.equal_key_filter import EqualKeyFilter
from .cross.required_with_filter import RequiredWithFilter


simple_filters = [
    "EmptyFilter",  # 1.判断字段是否为空的过滤器
    "SplitFilter",  # 字符串分割过滤器
    "MultiFilter",  # 多值过滤器
    "TypeFilter",  # 4.类型转换过滤器
    "TrimFilter",  # 2.去除字符串两侧的空格
    "StringFilter",  # 字符串处理过滤器
    "RegexpFilter",  # 3.正则表达式过滤器
    "ContentFilter",  # 内容检查过滤器
    # "FileFilter",  # 文件路径检查过滤器
    "NetworkFilter",  # 网络检查过滤器
    "LocationFilter",  # 地理位置过滤器
    "LengthFilter",  # 5.字符长度过滤器
    "RangeFilter",  # 6.取值范围过滤器
    "EqualFilter",  # 7.取值相等过滤器
    "EnumFilter",  # 8.枚举过滤器
    "EmailFilter",  # 9.邮箱过滤器
    "MobileFilter",  # 10.手机号过滤器
    "JsonFilter",  # 11.Json解析器
    "DefaultFilter",  # 12.默认值填充
]


complex_filters = [
    "RequiredWithFilter",
    "EqualKeyFilter"
]
