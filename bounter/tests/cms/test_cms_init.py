#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Filip Stefanak <f.stefanak@rare-technologies.com>
# Copyright (C) 2017 Rare Technologies
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).

import unittest

from bounter import CountMinSketch


class CountMinSketchInitTest(unittest.TestCase):
    def size_check(self, log_counting=None, width_adjustment=1):
        data_set = [
            (1, 2 ** 15, 8),
            (2, 2 ** 16, 8),
            (3, 2 ** 16, 12),
            (4, 2 ** 17, 8),
            (5, 2 ** 17, 10),
            (6, 2 ** 17, 12),
            (7, 2 ** 17, 14),
            (8, 2 ** 18, 8),
            (32, 2 ** 20, 8),
            (55, 2 ** 20, 13),
            (95, 2 ** 21, 11),
            (256, 2 ** 23, 8)
        ]

        for (size_mb, width, depth) in data_set:
            cms = CountMinSketch(size_mb, log_counting=log_counting)
            self.assertEqual(cms.width, width * width_adjustment, "Width for size %d" % size_mb)
            self.assertEqual(cms.depth, depth, "Depth for size %d" % size_mb)
            self.assertLessEqual(cms.size(), size_mb * 1024 * 1024)
            self.assertGreater(cms.size(), size_mb * 1024 * 1024 / 2)

    def test_sizemb_none_init(self):
        self.size_check(log_counting=None, width_adjustment=1)

    def test_sizemb_log1024_init(self):
        self.size_check(log_counting=1024, width_adjustment=2)

    def test_sizemb_log8_init(self):
        self.size_check(log_counting=8, width_adjustment=4)

    def test_width_depth_alg_init(self):
        data_set = [
            (None, 2 ** 12, 3, 49152),
            (None, 2 ** 13, 7, 229376),
            (1024, 2 ** 18, 1, 524288),
            (8, 2 ** 13, 7, 57344)
        ]
        for (log_counting, width, depth, size) in data_set:
            cms = CountMinSketch(width=width, depth=depth, log_counting=log_counting)
            self.assertEqual(cms.width, width)
            self.assertEqual(cms.depth, depth)
            self.assertLessEqual(cms.size(), size)

    def test_width_alg_init(self):
        data_set = [
            (None, 4, 2 ** 18, 4),
            (None, 17, 2 ** 19, 8),
            (1024, 70, 2 ** 21, 17),
            (8, 100, 2 ** 26, 1)
        ]
        for (log_counting, size_mb, width, exp_depth) in data_set:
            cms = CountMinSketch(size_mb=size_mb, width=width, log_counting=log_counting)
            self.assertEqual(cms.width, width)
            self.assertEqual(cms.depth, exp_depth)
            self.assertLessEqual(cms.size(), size_mb * 1024 * 1024)

    def test_depth_alg_init(self):
        data_set = [
            (None, 4, 2 ** 18, 4),
            (None, 17, 2 ** 19, 8),
            (1024, 70, 2 ** 21, 17),
            (8, 100, 2 ** 26, 1)
        ]
        for (log_counting, size_mb, exp_width, depth) in data_set:
            cms = CountMinSketch(size_mb=size_mb, depth=depth, log_counting=log_counting)
            self.assertEqual(cms.width, exp_width)
            self.assertEqual(cms.depth, depth)
            self.assertLessEqual(cms.size(), size_mb * 1024 * 1024)

    def test_invalid_algorithm(self):
        data = ['basic', 'log8', 'cons', 'logcounter', 5]
        for bad_algorithm in data:
            with self.assertRaises(ValueError):
                CountMinSketch(1, log_counting=bad_algorithm)

    def test_invalid_sizemb(self):
        with self.assertRaises(ValueError):
            CountMinSketch(0.5)

    def test_invalid_width(self):
        CountMinSketch(size_mb=8, width=2 ** 20)

        with self.assertRaises(ValueError):
            CountMinSketch(size_mb=8, width=2 ** 20 - 1)  # width must be a power of 2!

        with self.assertRaises(ValueError):
            CountMinSketch(size_mb=8, width=2 ** 22)  # width too large!

        with self.assertRaises(ValueError):
            CountMinSketch(width=2 ** 22 - 1, depth=8)  # width must be a power of 2!

    def test_largest_cms(self):
        cms = CountMinSketch(size_mb=16384, log_counting=8)


if __name__ == '__main__':
    unittest.main()
