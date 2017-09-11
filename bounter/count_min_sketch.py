#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Filip Stefanak <f.stefanak@rare-technologies.com>
# Copyright (C) 2017 Rare Technologies
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).

from collections import Mapping

import CMSC


class CountMinSketch(object):
    """
    Data structure used to estimate frequencies of elements in massive data sets with fixed memory footprint.
    Example::
        cms = CountMinSketch(size_mb=512) # Use 512 MB
        print(cms.width)  # 16 777 216
        print(cms.depth)   # 8
        print(cms.size)  # 536 870 912 (512 MB in bytes)
        cms.increment("foo")
        cms.increment("bar")
        cms.increment("foo")
        print(cms["foo"]) # 2
        print(cms["bar"]) # 1
        print(cms.cardinality()) # 2
        print(cms.total()) # 3
    To calculate memory footprint:
        ( width * depth * cell_size ) + HLL size
        Cell size is
           - 4B for conservative and basic algorithm
           - 2B for log1024
           - 1B for log8
        HLL size is 64 KB
    Memory example:
        width 2^25 (33 554 432), depth 8, log1024 (2B) has 2^(25 + 3 + 1) + 64 KB = 512.06 MB
        Can be pickled to disk with this exact size
    """
    def __init__(self, size_mb=64, width=None, depth=None, algorithm='conservative'):

        cell_size = CountMinSketch.cell_size(algorithm);
        self.cell_size_v = cell_size

        if width is None and depth is None:
            self.width = 1 << (size_mb * 65536 // cell_size).bit_length()
            self.depth = (size_mb * 1048576) // (self.width * cell_size)
        elif width is None:
            self.depth = depth
            avail_width = (size_mb * 1048576) // (depth * cell_size)
            self.width = 1 << (avail_width.bit_length() - 1)
            if not self.width:
                raise ValueError("Requested depth is too large for maximum memory size!")
        elif depth is None:
            if width != 1 << (width.bit_length() - 1):
                raise ValueError("Requested width must be a power of 2!")
            self.width = width
            self.depth = (size_mb * 1048576) // (width * cell_size)
            if not self.depth:
                raise ValueError("Requested width is too large for maximum memory size!")
        else:
            if width != 1 << (width.bit_length() - 1):
                raise ValueError("Requested width must be a power of 2!")
            self.width = width
            self.depth = depth

        if algorithm and str(algorithm).lower() == 'log8':
            self.cms = CMSC.CMS_Log8(width=self.width, depth=self.depth)
        elif algorithm and str(algorithm).lower() == 'log1024':
            self.cms = CMSC.CMS_Log1024(width=self.width, depth=self.depth)
        else:
            self.cms = CMSC.CMS_Conservative(width=self.width, depth=self.depth)

        # optimize calls by directly binding to C implementation
        self.increment = self.cms.increment
        self.__getitem__ = self.cms.get

    @staticmethod
    def cell_size(algorithm='conservative'):
        if str(algorithm).lower() == 'log8':
            return 1
        if str(algorithm).lower() == 'log1024':
            return 2
        return 4

    @staticmethod
    def table_size(width, depth=4, algorithm='conservative'):
        """
        Returns size of Count-min Sketch table with provided parameters in bytes.
        Does *not* include additional constant overhead used by parameter variables and HLL table, totalling less than 65KB.
        """
        return width * depth * CountMinSketch.cell_size(algorithm)

    def increment(self, key):
        self.cms.increment(str(key))

    def __getitem__(self, key):
        return self.cms.get(str(key))

    def cardinality(self):
        """
        Returns an estimate for the number of distinct keys counted by the structure. The estimate should be within 1%.
        """
        return self.cms.cardinality()

    def total(self):
        return self.cms.total()

    def merge(self, other):
        self.cms.merge(other.cms)

    def update(self, iterable):
        selfinc = self.increment
        if iterable is not None:
            if isinstance(iterable, CountMinSketch):
                self.merge(iterable)
            elif isinstance(iterable, Mapping):
                for elem, count in iterable.items():
                    selfinc(str(elem), count)
            else:
                for elem in iterable:
                    selfinc(str(elem))

    def size(self):
        """
        Returns current size of the Count-min Sketch table in bytes.
        Does *not* include additional constant overhead used by parameter variables and HLL table, totalling less than 65KB.
        """
        return self.width * self.depth * self.cell_size_v

    def __getstate__(self):
        return self.width, self.depth, self.cell_size_v, self.cms

    def __setstate__(self, state):
        self.width, self.depth, self.cell_size_v, self.cms = state
        self.increment = self.cms.increment
        self.__getitem__ = self.cms.get
