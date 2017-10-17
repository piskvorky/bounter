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


class HashTableIterationTest(unittest.TestCase):
    """
    Functional tests for additional HashTable iterations methods, which all produce an iterator
    """

    def setUp(self):
        self.ht = HashTable(buckets=64)
        self.ht.update([u"foo", u"bar", u"foo", "foo"])
        self.keys = {u"foo", u"bar"}
        self.values = {3, 1}
        self.pairs = {(u"foo", 3), (u"bar", 1)}

    def test_keys(self):
        self.assertEqual(set(self.ht.keys()), self.keys)

    def test_iterkeys(self):
        self.assertEqual(set(self.ht.iterkeys()), self.keys)

    def test_values(self):
        self.assertEqual(set(self.ht.values()), self.values)

    def test_itervalues(self):
        self.assertEqual(set(self.ht.itervalues()), self.values)

    def test_items(self):
        self.assertEqual(set(self.ht.items()), self.pairs)

    def test_iteritems(self):
        self.assertEqual(set(self.ht.iteritems()), self.pairs)


if __name__ == '__main__':
    unittest.main()
