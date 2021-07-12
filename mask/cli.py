# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2021
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '2021/7/6 10:17 上午'
# sys
import os
import pkg_resources
import typing as t
# 3p
import click
from grpc_tools import protoc


def _expand_path(path: str) -> t.Optional[str]:
    """ Expand path by repeatedly applying `expandvars` and `expanduser`
     until interpolation stops having any effect
    """
    if not path:
        return None

    while True:
        interpolated = os.path.expanduser(os.path.expandvars(path))
        if interpolated == path:
            return interpolated
        else:
            path = interpolated


def _expand_multiple(objs: t.Union[t.List, t.Tuple, t.Set]) -> list:
    """ Exapand multiple params to support value combine with comma
    :param objs:
    :return:
    """
    fmt_rst = list()
    if not objs or not isinstance(objs, (list, tuple, set)):
        return fmt_rst

    for v in objs:
        if isinstance(v, str):
            fmt_rst.extend(v.split(","))
            continue
        fmt_rst.append(v)

    return fmt_rst


def _replace_content(dest: str, callback: t.Callable) -> None:
    """ 替换文件中的内容
    """
    with open(dest, "r") as f:
        content = f.read()

    content = callback(content)

    with open(dest, "w") as f:
        f.write(content)


def _build_protobuf(proto_file, python_out, strict_mode=False):
    """ Protobuf build executor

    :param proto_file: ProtoBuf file path
    :param python_out: Python output path
    """
    well_known_protos_include = pkg_resources.resource_filename('grpc_tools', '_proto')

    if not python_out:
        python_out = os.path.dirname(proto_file)

    command = [
                  'grpc_tools.protoc',
                  '--proto_path={}'.format(python_out),
                  '--proto_path={}'.format(well_known_protos_include),
                  '--python_out={}'.format(python_out),
                  '--grpc_python_out={}'.format(python_out),
              ] + [proto_file]

    if protoc.main(command) != 0:
        if strict_mode:
            raise Exception('error: {} failed'.format(command))
        else:
            sys.stderr.write('warning: {} failed'.format(command))
        return

    proto_file_name = os.path.split(proto_file)[-1].split(".")[0]
    pb2_grpc_path = os.path.join(python_out, f"{proto_file_name}_pb2_grpc.py")

    def _replace_import(content):
        ori_str = f"import {proto_file_name}_pb2 as {proto_file_name}__pb2"
        replace_str = f"from . import {proto_file_name}_pb2 as {proto_file_name}__pb2"
        return content.replace(ori_str, replace_str)

    _replace_content(pb2_grpc_path, _replace_import)


@click.command(name="compile")
@click.option(
    "--proto_path",
    "-p",
    required=True,
    help="Protobuf file path"
)
@click.option(
    "--python_out",
    default=None,
    help="Python out path",
)
@click.option(
    "--strict_mode",
    default=None,
    help="Run compile with strict mode"
)
def compiler(**kwargs) -> None:
    """ Compile protobuf file to .py file \n
    Simple usage: mask compile -p ./demo.proto
    """
    protobuf_path = _expand_path(kwargs.get("proto_path"))
    if not os.path.exists(protobuf_path):
        raise FileNotFoundError(f"Can't find protobuf at path: {protobuf_path}")

    _build_protobuf(protobuf_path, _expand_path(kwargs.get("python_out")), kwargs["strict_mode"])


@click.command(name="package")
@click.option(
    "--package_root",
    "-p",
    required=True,
    help="Package root path"
)
@click.option(
    "--exclude_path",
    multiple=True,
    help="Exclude path to ignore",
)
@click.option(
    "--exclude_file",
    multiple=True,
    help="Exclude protobuf file name",
)
@click.option(
    "--package_out",
    help="Which packages to output compiled python file"
)
@click.option(
    "--strict_mode",
    default=True,
    is_flag=True,
    help="Run compile with strict mode"
)
def package(**kwargs) -> None:
    """ Auto compile all of the protobuf in the package
    """
    package_root = _expand_path(kwargs.get("package_root"))
    if not os.path.exists(package_root):
        raise FileNotFoundError(f"Can't find package path at: {package_root}")

    exclude_path = _expand_multiple(kwargs.get("exclude_path"))
    exclude_path = {_expand_path(v) for v in exclude_path}

    exclude_file = _expand_multiple(kwargs.get("exclude_file"))
    exclude_file = {_expand_path(v) for v in exclude_file}

    inclusion_root = os.path.abspath(package_root)
    for root, _, files in os.walk(inclusion_root):

        if root in exclude_path:
            continue

        for filename in files:
            if not filename.endswith(".proto"):
                continue

            full_path = os.path.abspath(os.path.join(root, filename))
            if filename in exclude_file or full_path in exclude_file:
                continue

            _build_protobuf(full_path, _expand_path(kwargs.get("package_out")), kwargs["strict_mode"])


@click.group(name="main", help="""
A general utility script for Mask applications.
""")
def main_func():
    pass


main_func.add_command(compiler)
main_func.add_command(package)
