# !/usr/local/python/bin/python
# -*- coding: utf-8 -*-
# (C) Wu Dong, 2020
# All rights reserved
# @Author: 'Wu Dong <wudong@eastwu.cn>'
# @Time: '2020-04-01 09:47'
# sys
import typing as t
from functools import wraps
from inspect import isfunction
from inspect import getfullargspec
# 3p
import grpc
from mask import request as req
from mask.utils import (
    deserialize_request,
    deserialize_headers,
)
# object
from .exception import ParamsValueError
from .filters.base import BaseFilter
from .filters import (
    complex_filters,
    simple_filters,
)
from .macro import (
    K_FUZZY,
    K_SKIP_FILTER,
    K_STORE_KEY
)
from .response import (
    BaseResponse,
    GlibResponse,
)
from .rules import Rule
from .utils import get_deep_value
from . import filters
# check
if t.TYPE_CHECKING:
    from mask import Mask  # pylint: disable=unused-import


class PreRequest:
    """ An object to dispatch filters to handler request params
    """

    def __init__(self, app=None, fuzzy=False, store_key=None, skip_filter=False):
        """ PreRequest init function

        :param fuzzy: formatter error message with fuzzy style
        :param store_key: which key will store formatter result
        :param skip_filter: skip all of the filter check
        """
        self.filters = simple_filters
        self.complex_filters = complex_filters
        self.fuzzy = fuzzy
        self.store_key = store_key or "params"
        self.response = None
        self.formatter = None
        self.skip_filter = skip_filter

        if app is not None:
            self.app = app
            self.init_app(app, None)

    def init_app(self, app: "Mask", config=None):
        """ Flask extension initialize

        :param app: flask application
        :param config: flask config
        """
        if not (config is None or isinstance(config, dict)):
            raise TypeError("'config' params must be type of dict or None")

        # update config from different origin
        basic_config = app.config.copy()
        if config:
            basic_config.update(config)
        config = basic_config

        self.fuzzy = config.get(K_FUZZY, False)
        self.store_key = config.get(K_STORE_KEY, "params")
        self.skip_filter = config.get(K_SKIP_FILTER, False)

        self.app = app
        app.extensions["Pre-request"] = self

    def add_response(self, resp):
        """ Add custom response class

        :param resp: response class which is subclass of BaseResponse
        """
        if resp and not issubclass(resp, BaseResponse):
            raise TypeError("custom response must be subclass of `pre_request.BaseResponse`")

        self.response = resp

    def add_formatter(self, fmt):
        """ Add custom format function for generate response content

        :param fmt: format function
        """
        if fmt and not isfunction(fmt):
            raise TypeError("custom format function must be a type of function")

        if fmt and fmt.__code__.co_argcount < 2:
            raise TypeError("custom format function requires at least 2 arguments")

        self.formatter = fmt

    def add_filter(self, cus_filter, index=None):
        """ Add custom filter class to extend pre-request

        :param cus_filter: custom filter class
        :param index: filter position
        """
        if cus_filter and not issubclass(cus_filter, BaseFilter):
            raise TypeError("custom filter must be subclass of `BaseFilter`")

        if index is not None and not isinstance(index, int):
            raise TypeError("index params must be type of Int")

        if index is not None:
            self.filters.insert(index, cus_filter)
        else:
            self.filters.append(cus_filter)

    def remove_filter(self, cus_filter=None, index=None):
        """ Remove filters from object with index or filter name

        :param cus_filter: user filter name
        :param index: filter index
        """
        if cus_filter and (isinstance(cus_filter, str) or issubclass(cus_filter, BaseFilter)):
            self.filters.remove(cus_filter)

        if index is not None and isinstance(index, int) and 0 <= index < len(self.filters):
            self.filters.pop(index)

    @staticmethod
    def _location_params(key, location, default=None, deep=True, **options):
        """ Read params form special location ex: args/forms/header/cookies

        :param key: params key
        :param location: special location
        :param default: default value if special value is not exists
        :param deep: read params with deep search
        """
        location = location.lower()

        # query deep value with special key like `userInfo.userId`
        if len(key.split(".")) > 1 and deep:
            return options.get(location, {}).get(key, default)

        # load simple params
        return get_deep_value(key, options.get(location), default, deep=False)

    def _fmt_params(self, key, rule, default=None, **options):
        """ Query request params from flask request object

        :param key: params key
        """
        df_location = ["values", "headers"]
        if len(key.split(".")) > 1 and rule.deep:
            rst = get_deep_value(key, options["values"], default, deep=True)
            # load value from depth json structure failed
            if rst != default:
                return rst

        rule.location = rule.location or df_location

        # query object from special location
        for location in rule.location:
            rst = self._location_params(key, location, default, rule.deep, **options)
            # can't read params from this location
            if rst != default:
                return rst

        return default

    def _handler_simple_filter(self, k, v, r, **options):  # noqa
        """ Handler filter rules with simple ways

        :param k: params key
        :param v: params value
        :param r: params rule
        :param options: other params
        """
        if isinstance(r, dict):
            fmt_result = dict()
            for key, rule in r.items():
                fmt_value = self._handler_simple_filter(k + "." + key, v, rule, **options)
                fmt_result[rule.key_map if isinstance(rule, Rule) and rule.key_map else key] = fmt_value

            return fmt_result

        if not isinstance(r, Rule):
            raise TypeError("invalid rule type for key '%s'" % k)

        if v is None:
            v = self._fmt_params(k, r, **options)

        if r.structure is not None:
            # make sure that input value is not empty
            if r.required and not v:
                raise ParamsValueError(560, message="%s field cannot be empty" % k)

            if not r.multi:
                raise TypeError("invalid usage of `structure` params")

            # structure params must be type of list
            if not isinstance(v, list):
                raise ParamsValueError(601, message="Input " + k + " invalid type")

            if not v:
                return list()

            # storage sub array
            fmt_result = list()
            for idx, sub_v in enumerate(v):
                # make sure that array item must be type of dict
                if not isinstance(sub_v, dict):
                    raise ParamsValueError(600, message="Input " + k + "." + str(idx) + " invalid type")

                # format every k-v with structure
                fmt_item = dict()
                fmt_result.append(fmt_item)
                for sub_k, sub_r in r.structure.items():
                    new_k = k + "." + str(idx) + "." + sub_k
                    v = self._handler_simple_filter(new_k, sub_v.get(sub_k), sub_r, **options)
                    fmt_item[sub_r.key_map if isinstance(sub_r, Rule) and sub_r.key_map else sub_k] = v

            return fmt_result

        if r.skip or self.skip_filter:
            return v

        # filter request params
        for f in self.filters:
            filter_obj = None
            # system filter object
            if isinstance(f, str):
                filter_obj = getattr(filters, f)(k, v, r)

            # custom filter object
            elif issubclass(f, BaseFilter):
                filter_obj = f(k, v, r)  # pylint: disable=not-callable

            # ignore invalid and not required filter
            if not filter_obj or not filter_obj.filter_required():
                continue

            v = filter_obj()

        if r.callback is not None and isfunction(r.callback):
            v = r.callback(v)

        return v

    def _handler_complex_filter(self, k, r, rst):
        """ Handler complex rule filters

        :param k: params key
        :param r: params rule
        :param rst: handler result
        """
        if isinstance(r, dict):
            for key, value in r.items():
                self._handler_complex_filter(k + "." + key, value, rst)
            return

        if not isinstance(r, Rule):
            raise TypeError("invalid rule type for key '%s'" % k)

        if r.skip or self.skip_filter:
            return

        # simple filter handler
        for f in self.complex_filters:
            filter_obj = None
            # system filter object
            if isinstance(f, str):
                filter_obj = getattr(filters, f)(k, None, r)

            # custom filter object
            elif issubclass(f, BaseFilter):
                filter_obj = f(k, None, r)  # pylint: disable=not-callable

            # ignore invalid and not required filter
            if not filter_obj or not filter_obj.filter_required():
                continue

            filter_obj(params=rst)

    @staticmethod
    def _fmt_origin_params(request=None, context=None):
        """ 格式化原始入参

        :param request: 原始请求
        :param context: 原始上下文
        """
        options = {}
        # 如果用户不填入request和上下文的话，则使用glib的全局请求和上下文
        if not request or not hasattr(request, "DESCRIPTOR"):
            options["values"] = req.values
        else:
            options["values"] = deserialize_request(request)

        # 格式化上下文
        if not context:
            context = req.context

        options["context"] = context
        options["headers"] = deserialize_headers(context)

        return options

    def parse(self, rule=None, request=None, context=None, **options):
        """ Parse input params

        :param rule: 当前设置的规则
        :param request: grpc请求参数实例
        :param context: 当前请求上下文
        """
        fmt_rst = dict()

        # invalid input
        if not rule and not options:
            return fmt_rst

        if not isinstance(rule, dict):
            raise TypeError("Invalid rule type, must be 'dict'!")

        # deserialize origin input data
        options.update(self._fmt_origin_params(request, context))

        try:
            # use simple filter to handler params
            for k, r in rule.items():
                value = self._handler_simple_filter(k, None, r, **options)
                # simple filter handler
                fmt_rst[r.key_map if isinstance(r, Rule) and r.key_map else k] = value

            # use complex filter to handler params
            for k, r in rule.items():
                self._handler_complex_filter(k, r, fmt_rst)
        except ParamsValueError as e:
            return self.fmt_resp(error=e, **options)

        return fmt_rst

    def catch(self, rule=None, **options):
        """ Catch request params
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # ignore with empty rule
                if not rule and not options:
                    return func(*args, **kwargs)

                # parse input params
                fmt_rst = self.parse(rule, **options)

                # assignment params to func args
                if self.store_key in getfullargspec(func).args:
                    kwargs[self.store_key] = fmt_rst

                return func(*args, **kwargs)
            return wrapper
        return decorator

    def _handler_params_exception(self, e, context):
        """ 响应parse抛出的ParamsValueError异常
        """
        context.abort(grpc.StatusCode.INVALID_ARGUMENT, self.fmt_resp(e))

    def fmt_resp(self, error, **options):
        """ Handler not formatted request error

        :param error: ParamsValueError
        """
        if self.response is not None:
            return self.response()(self.fuzzy, self.formatter, error, **options)

        return GlibResponse()(self.fuzzy, self.formatter, error, **options)
