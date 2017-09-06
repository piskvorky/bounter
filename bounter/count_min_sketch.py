#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Filip Stefanak <f.stefanak@rare-technologies.com>
# Copyright (C) 2017 Rare Technologies
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).

import random

import numpy
import xxhash


def hash_key(row, key):
    """
    Calculates a hash for a key for a specific row of the table
    The row is used as a seed in order to minimize correlations between collisions
    :return hash of the key as int
    """
    return xxhash.xxh64(str(key), seed=row).intdigest()


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
        print(cms.sum) # 3

    To calculate memory footprint:
        ( width * depth * cell_size ) + HLL size
        Cell size is
           - 4B for conservative and basic algorithm
           - 1B for logcounter8
           - 2B for logcounter1024
        HLL size is 32 KB

    Memory example:
        width 2^26 (67 108 864), depth 4, logcons1024 (2B) has 2^(26 + 2 + 1) + 32 768 = 536.9 MB
        Can be pickled to disk with this exact size
    """

    def __init__(self, size_mb=64, width=None, depth=None, algorithm='conservative'):
        """
        Initializes the Count-Min Sketch structure with the given parameters

        Args:
            size_mb (int): controls the maximum size of the Count-min Sketch table.
                If width is provided, this parameter is ignored. Please note that the structure will use an
                overhead of approximately 33 KB in addition to the table size.
            depth (int): controls the number of rows of the table. Having more rows decreases probability of a big
                overestimation but also linearly affects performance and table size. Choose a small number such as 4-8.
                The algorithm will default depth 8 if width is provided. Otherwise, it will choose a depth in range 4-7
                to best fill the maximum memory (for memory size which is a power of 2, depth of 4 is always used).
            width (int): controls the number of hash buckets in one row of the table, overrides size_mb parameter.
                If width is not provided, the algorithm chooses the maximum width to fill the available size.
                The more, the better, should be very large, preferably in the same order of magnitude as the cardinality
                of the counted set.
            algorithm (str): controls the algorithm used for counting
                - 'basic'
                - 'conservative' (default)
                - 'logcounter8'
                - 'logcounter1024'
        """
        self.array_type = CountMinSketch.cell_type(algorithm)
        cell_size = self.array_type().itemsize
        if width is None and depth is None:
            self.width = 1 << (size_mb * 131072 // cell_size).bit_length()
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

        self.logshift = 0
        self.inc_method = self.conservative_increment
        if algorithm and str(algorithm).lower() == 'basic':
            self.inc_method = self.basic_increment
        if algorithm and str(algorithm).lower() == 'logcounter8':
            self.logshift = 2
            self.inc_method = self.conservative_increment
            self.decode = self.log_decode
        if algorithm and str(algorithm).lower() == 'logcounter1024':
            self.logshift = 9
            self.inc_method = self.conservative_increment
            self.decode = self.log_decode

        self.hash_length = self.width.bit_length()
        self.hash_mask = (1 << (self.hash_length - 1)) - 1
        self.logbase = 1 << (self.logshift + 1) if self.logshift > 0 else 0
        self.table = numpy.zeros((self.depth, self.width), self.array_type)

        self.sum = 0
        self.distinct_counter = HyperLogLog(15)

    @staticmethod
    def cell_type(algorithm = 'conservative'):
        """
        Returns the numpy dtype used for table cells with provided algorithm
        """
        if str(algorithm).lower() == 'logcounter8':
            return numpy.uint8
        if str(algorithm).lower() == 'logcounter1024':
            return numpy.uint16
        if str(algorithm).lower() == 'logcons1024':
            return numpy.uint16
        return numpy.uint32

    @staticmethod
    def table_size(width, depth=4, algorithm='conservative'):
        """
        Returns size of Count-min Sketch table with provided parameters in bytes.
        Does *not* include additional constant overhead used by parameter variables and HLL table, totalling less than 33KB.
        """
        return width * depth * CountMinSketch.cell_type(algorithm)().itemsize

    def size(self):
        """
        Returns current size of the Count-min Sketch table in bytes.
        Does *not* include additional constant overhead used by parameter variables and HLL table, totalling less than 33KB.
        """
        return self.width * self.depth * self.array_type().itemsize

    def bucket(self, i, key):
        return self.hash_mask & hash_key(i, key)

    def increment(self, key):
        self.inc_method(key)
        self.distinct_counter.add(str(key))
        self.sum += 1

    def cardinality(self):
        """
        Returns an estimate for the number of distinct keys counted by the structure. The estimate should be within 1%.
        """
        return int(self.distinct_counter.cardinality())

    def basic_increment(self, key):
        for row in range(self.depth):
            self.table[row, self.bucket(row, key)] += 1

    def conservative_increment(self, key):
        table = self.table
        buckets = [self.bucket(row, key) for row in range(self.depth)]
        values = [int(table[row, bucket]) for row, bucket in enumerate(buckets)]
        current = min(values)
        if self.logbase > 0 and current >= 2 * self.logbase:
            mask = (1 << (current // self.logbase - 1)) - 1
            r = random.getrandbits(64)
            if (r & mask) != 0:
                return

        for row, value in enumerate(values):
            if value == current:
                table[row, buckets[row]] = current + 1

    def log_decode(self, log_value):
        if (log_value <= 2 * self.logbase):
            return log_value
        else:
            base = 1 << ((log_value >> (self.logshift + 1)) + self.logshift)
            return int(base + (log_value % self.logbase) * (base / self.logbase))

    def log_encode(self, input):
        value = int(input)
        if value <= 2 * self.logbase:
            return value
        base_bits = value.bit_length() - 1
        log_value_base = (base_bits - self.logshift) * self.logbase

        remainder = (value >> (base_bits - self.logshift - 1)) - self.logbase
        return log_value_base + remainder

    def decode(self, value):
        return value

    def __getitem__(self, key):
        minimum = min(self.table[row, self.bucket(row, key)] for row in range(self.depth))
        return self.decode(minimum)

    def quality(self):
        """
        Returns a floating point number representing fullness of the table
         - With values less than 1, the table suffers from negligible sketch bias. Most values are not affected by sketch
         bias (the bias from probabilistic log counter still applies)
         - For values up to depth of the table, the bias tends to stay low
         - With larger values, consider increasing width of the table.
        """
        return float(self.width) / self.cardinality()
