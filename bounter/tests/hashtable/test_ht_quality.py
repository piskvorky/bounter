#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Filip Stefanak <f.stefanak@rare-technologies.com>
# Copyright (C) 2017 Rare Technologies
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).

import unittest

from bounter import HashTable


class HashTableQualityTest(unittest.TestCase):
    """
    Functional tests for HashTable.quality method, which returns quality rating of the structure
    """

    def test_quality_default(self):
        ht = HashTable(buckets=1024)
        """
        Uses the default structure
        """
        self.assertEqual(ht.quality(), 0)

        for i in range(512):
            ht.increment(str(i), 1 + (i % 13))

        self.assertAlmostEqual(ht.quality(), 2.0 / 3)

        for i in range(1024):
            ht.increment(str(1024 + i), 1 + (i % 17))

        self.assertAlmostEqual(ht.quality(), 2.0, delta=0.015)


if __name__ == '__main__':
    unittest.main()
