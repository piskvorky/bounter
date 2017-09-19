#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Filip Stefanak <f.stefanak@rare-technologies.com>
# Copyright (C) 2017 Rare Technologies
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).

from collections import Mapping

import cmsc


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
    How to choose parameters and algorithm:
        Preferably, start with high a high `size_mb` using the 'conservative' algorithm. After counting all elements of the
        set, check `cms.cardinality()` and calculate quality ratio `cms.cardinality / cms.width`.
        If this ratio is greater than 1, the table is likely to suffer small bias from collisions. As the ratio climbs over 5,
        the results are getting more and more biased. Therefore we recommend choosing a higher size (if possible) or
        switching to 'log1024' algorithm which can support twice the width with the same memory size (or 'log8' for quadruple).
        Both of these algorithms suffer from a different kind of bias but that tends to be less severe than the collision bias.
        If you can achieve the quality ratio below 1 with the 'conservative' algorithm, we do not recommend using the log
        version as the collision bias will already be minimal.
    """

    def __init__(self, size_mb=64, width=None, depth=None, algorithm='conservative'):
        """
        Initializes the Count-Min Sketch structure with the given parameters

        Args:
            size_mb (int): controls the maximum size of the Count-min Sketch table.
                If both width and depth is provided, this parameter is ignored.
                Please note that the structure will use an overhead of approximately 65 KB in addition to the table size.
            depth (int): controls the number of rows of the table. Having more rows decreases probability of a big
                overestimation but also linearly affects performance and table size. Choose a small number such as 6-10.
                The algorithm will default depth 8 if width is provided. Otherwise, it will choose a depth in range 5-8
                to best fill the maximum memory (for memory size which is a power of 2, depth of 8 is always used).
            width (int): controls the number of hash buckets in one row of the table.
                If width is not provided, the algorithm chooses the maximum width to fill the available size.
                The more, the better, should be very large, preferably in the same order of magnitude as the cardinality
                of the counted set.
            algorithm (str): controls the algorithm used for counting
                - 'conservative' (default)
                - 'log1024'
                - 'log8'
        """

        cell_size = CountMinSketch.cell_size(algorithm);
        self.cell_size_v = cell_size

        if width is None and depth is None:
            self.width = 1 << (size_mb * (2 ** 16) // cell_size).bit_length()
            self.depth = (size_mb * (2 ** 20)) // (self.width * cell_size)
        elif width is None:
            self.depth = depth
            avail_width = (size_mb * (2 ** 20)) // (depth * cell_size)
            self.width = 1 << (avail_width.bit_length() - 1)
            if not self.width:
                raise ValueError("Requested depth is too large for maximum memory size!")
        elif depth is None:
            if width != 1 << (width.bit_length() - 1):
                raise ValueError("Requested width must be a power of 2!")
            self.width = width
            self.depth = (size_mb * (2 ** 20)) // (width * cell_size)
            if not self.depth:
                raise ValueError("Requested width is too large for maximum memory size!")
        else:
            if width != 1 << (width.bit_length() - 1):
                raise ValueError("Requested width must be a power of 2!")
            self.width = width
            self.depth = depth

        if algorithm and str(algorithm).lower() == 'log8':
            self.cms = cmsc.CMS_Log8(width=self.width, depth=self.depth)
        elif algorithm and str(algorithm).lower() == 'log1024':
            self.cms = cmsc.CMS_Log1024(width=self.width, depth=self.depth)
        elif algorithm and str(algorithm).lower() == 'conservative':
            self.cms = cmsc.CMS_Conservative(width=self.width, depth=self.depth)
        else:
            raise ValueError("Unsupported algorithm! Use 'conservative', 'log8', or 'log1024'!");

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
        """
        Merges another Count-min sketch structure into this one. The other structure must be initialized
        with the same width, depth and algorithm, and remains unaffected by this operation.

        Please note that merging two halves is always less accurate than counting the whole set with a single counter,
        because the merging algorithm can not leverage the conservative update optimization.
        """
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
