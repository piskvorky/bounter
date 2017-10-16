#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Filip Stefanak <f.stefanak@rare-technologies.com>
# Copyright (C) 2017 Rare Technologies
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).

from .count_min_sketch import CountMinSketch
from bounter_htc import HT_Basic as HashTable


def bounter(size_mb=64, need_iteration=True, log_counting=None):
    """Factory method for bounter implementation.

    Args:
            size_mb (int): Desired memory footprint of the counter.
            need_iteration (Bool): With `True`, create a `HashTable` implementation which can
                iterate over inserted key/value pairs.
                With `False`, create a `CountMinSketch` implementation which performs better in limited-memory scenarios,
                but does not support iteration over elements.
            log_counting (int): Counting to use with `CountMinSketch` implementation. Accepted values are
                `None` (default counting with 32-bit integers), 1024 (16-bit), 8 (8-bit).
                See `CountMinSketch` documentation for details.
                Raise ValueError if not `None `and `need_iteration` is `True`.
    """
    if need_iteration:
        if log_counting:
            raise ValueError("Log counting is only supported with CMS implementation (need_iteration=False).")
        return HashTable(size_mb=size_mb)
    else:
        return CountMinSketch(size_mb=size_mb, log_counting=log_counting)
