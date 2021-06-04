# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '5/26/21 1:34 PM'
# sys
import importlib
import os
import re
import typing as t
if t.TYPE_CHECKING:
    from google.protobuf.pyext._message import FileDescriptor  # pylint: disable=unused-import,no-name-in-module


r_funcs = re.compile(r"add_\S+Servicer_to_server")
r_desc = re.compile(r"DESCRIPTOR.services_by_name\['(.*)'\]")


def _walk_path_files(path=None):
    """ Scan all of the files in path
    """
    for root, _, files in os.walk(path or "."):
        # invalid path
        if root.startswith("./venv"):
            continue

        for file in files:
            yield root, file


def scan_pb2_grpc() -> t.Dict[str, t.Callable]:
    """ Scan all of the files that end with 'pb2_grpc'
    """
    server_register_funcs = dict()

    for root, file in _walk_path_files():
        if not file.endswith("pb2_grpc.py"):
            continue

        path = os.path.join(root, file)
        with open(path, "r", encoding="utf-8") as f:
            # 查找有效的服务方法
            funcs = r_funcs.findall(f.read())
            if not funcs:
                continue

            # 导入该方法
            module = path.replace("./", "").replace("/", ".").replace(".py", "")
            obj = importlib.import_module(module)
            for func in funcs:
                server_register_funcs[func] = getattr(obj, func)

    return server_register_funcs


def scan_pb2() -> t.Dict[str, "FileDescriptor"]:
    """ Scan all of the files that end with '_pb2.py'
    """
    pr2_descriptor = dict()

    for root, file in _walk_path_files():
        if not file.endswith("_pb2.py"):
            continue

        path = os.path.join(root, file)
        with open(path, "r", encoding="utf-8") as f:
            # 查找有效的服务方法
            service_names = r_desc.findall(f.read())
            if not service_names:
                continue

            # 导入该方法
            module = path.replace("./", "").replace("/", ".").replace(".py", "")
            obj = importlib.import_module(module)

            for name in service_names:
                descriptor = pr2_descriptor.get(name)
                if descriptor is not None:
                    raise RuntimeError("Conflict services name in ProtoBuf file: %s" % name)
                pr2_descriptor[name] = getattr(obj, "DESCRIPTOR")

    return pr2_descriptor
