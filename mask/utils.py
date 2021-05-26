# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/26/21 1:17 PM'
# sys
import typing as t
from inspect import isbuiltin
from threading import RLock


class _Missing:
    """ 创建特殊的Miss类型，用于None值为有效数据的情况
    """

    def __repr__(self):
        return "no value"

    def __reduce__(self):
        return "_missing"


_missing = _Missing


class CachedProperty(property):
    """ 将方法装饰成懒加载的属性

    通过重写 setter 和 getter 方法，将属性改造成懒加载模式
    """

    def __init__(self, func, name=None, doc=None):  # pylint: disable=super-init-not-called
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __set__(self, obj, value):
        obj.__dict__[self.__name__] = value

    def __get__(self, obj, tp=None):
        if obj is None:
            return self

        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value


class LockedCachedProperty(CachedProperty):
    """ 在读取、设置属性时，尝试先加RLock，保证多线程安全
    """

    def __init__(
            self,
            func: t.Callable[[t.Any], t.Any],
            name: t.Optional[str] = None,
            doc: t.Optional[str] = None
    ) -> None:
        super().__init__(func, name, doc)
        self.lock = RLock()

    def __get__(self, instance: object, owner: type = None) -> t.Any:
        if instance is None:
            return self

        with self.lock:
            return super().__get__(instance, owner)

    def __set__(self, instance: object, value: t.Any) -> t.Any:
        with self.lock:
            super().__set__(instance, value)

    def __delete__(self, instance: object) -> t.Any:
        with self.lock:
            super().__delete__(instance)


_RPC_BUILTIN_KEYS = {
    "Extensions",
    "DESCRIPTOR",
    "_SetListener",
    "_extensions_by_name",
    "_extensions_by_number"
}


def deserialize_request(obj):
    """ 反序列化gRPC请求对象
    """
    # 非gRPC生成的对象，不做处理
    if not hasattr(obj, "DESCRIPTOR"):
        return obj

    fmt_rst = {}
    for key in dir(obj):
        # 过滤系统内置属性
        if (
                key.startswith("__")
                or key in _RPC_BUILTIN_KEYS
                or not hasattr(obj, key)
        ):
            continue

        val = getattr(obj, key)
        # 过滤内置属性或者方法
        if isbuiltin(val):
            continue

        # 递归进行序列化
        if isinstance(val, (list, tuple, set)):
            val = [deserialize_request(v) for v in val]
        elif hasattr(val, "DESCRIPTOR"):
            val = deserialize_request(val)

        fmt_rst[key] = val

    return fmt_rst


def deserialize_headers(context):
    """ 解析上下文中的headers

    :param context: 请求上下文
    """
    rpc_event = getattr(context, "_rpc_event")
    if not rpc_event:
        return None

    metadata = getattr(rpc_event, "invocation_metadata")
    return dict(metadata)
