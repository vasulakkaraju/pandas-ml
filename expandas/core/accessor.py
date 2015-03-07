#!/usr/bin/env python

import importlib

import numpy as np
import pandas as pd
from pandas.util.decorators import Appender, cache_readonly


class AccessorMethods(object):
    """
    Accessor to related functionalities.
    """

    _module_name = None

    def __init__(self, df, module_name=None, attrs=None):
        self._df = df

        if module_name is not None:
            # overwrite if exists
            self._module_name = module_name

        if self._module_name is None:
            return

        self._module = importlib.import_module(self._module_name)

        if attrs is None:
            try:
                attrs = self._module.__all__
            except AttributeError:
                return

        for mobj in attrs:
            try:
                if not hasattr(self, mobj):
                    try:
                        setattr(self, mobj, getattr(self._module, mobj))
                    except AttributeError:
                        pass
            except NotImplementedError:
                pass

    @property
    def _data(self):
        return self._df.data

    @property
    def _target(self):
        return self._df.target

    @property
    def _predicted(self):
        return self._df.predicted

    @property
    def _decision(self):
        return self._df.decision

    @property
    def _constructor(self):
        return self._df._constructor

    @property
    def _constructor_sliced(self):
        return self._df._constructor_sliced


def _attach_methods(cls, wrap_func, methods):
    try:
        module = importlib.import_module(cls._module_name)

        for method in methods:
            _f = getattr(module, method)
            if hasattr(cls, method):
                raise ValueError("{0} already has '{1}' method".format(cls, method))
            setattr(cls, method, wrap_func(_f))

    except ImportError:
        pass


def _wrap_data_func(func):
    """
    Wrapper to call func with data values
    """
    def f(self, *args, **kwargs):
        data = self._data
        result = func(data.values, *args, **kwargs)
        return result
    return f


def _wrap_data_target_func(func):
    """
    Wrapper to call func with data and target values
    """
    def f(self, *args, **kwargs):
        data = self._data
        target = self._target
        result = func(data.values, y=target.values, *args, **kwargs)
        return result
    return f