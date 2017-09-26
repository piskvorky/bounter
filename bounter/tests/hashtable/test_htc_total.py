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


class HashTableTotalTest(unittest.TestCase):
    """
    Functional tests for HashTable.total method
    """

    def setUp(self):
        self.ht = HashTable(buckets=64)

    def test_simple_total(self):
        self.assertEqual(self.ht.total(), 0)
        self.ht.update("foo")
        self.assertEqual(self.ht.total(), 3)

    def test_set_reset_total(self):
        self.ht.update("foo")
        self.assertEqual(self.ht.total(), 3)
        self.ht['o'] += 2
        self.assertEqual(self.ht.total(), 5)
        self.ht['f'] = 0
        self.assertEqual(self.ht.total(), 4)

    def test_increment_total(self):
        self.ht.update("foo")
        self.ht.increment("f", 5)
        self.assertEqual(self.ht.total(), 8)
        self.ht.increment("a", 2)
        self.assertEqual(self.ht.total(), 10)
        self.ht.increment("r", 0)
        self.assertEqual(self.ht.total(), 10)

    def test_delete_total(self):
        self.ht.update("foo")
        del self.ht['o']
        self.assertEqual(self.ht.total(), 1)

    def test_prune_total(self):
        self.ht = HashTable(buckets=4)
        self.ht.update("223334444")
        self.assertEqual(self.ht.total(), 9)
        self.ht.update("1")
        self.assertEqual(self.ht.total(), 10)


if __name__ == '__main__':
    unittest.main()
