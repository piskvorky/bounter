#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Filip Stefanak <f.stefanak@rare-technologies.com>
# Copyright (C) 2017 Rare Technologies
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).

import unittest
import sys

from bounter import HashTable

uni_type = str if sys.version_info >= (3, 0) else unicode

class HashTableIterTypeTest(unittest.TestCase):
    """
    Functional tests for HashTable use_unicode parameter
    """

    def setUp(self):
        self.ht = HashTable(buckets=64)

    def test_itertype_default_unicode(self):
        self.ht.update([b'bytes', u'Unicode', 'String'])
        for key in self.ht:
            self.assertEqual(type(key), uni_type)

        for key, _ in self.ht.items():
            self.assertEqual(type(key), uni_type)

    def test_itertype_use_unicode_true(self):
        self.ht = HashTable(buckets=64, use_unicode=True)
        self.ht.update([b'bytes', u'Unicode', 'String'])
        for key in self.ht:
            self.assertEqual(type(key), uni_type)

        for key, _ in self.ht.items():
            self.assertEqual(type(key), uni_type)

    def test_itertype_use_unicode_false(self):
        self.ht = HashTable(buckets=64, use_unicode=False)
        self.ht.update([b'bytes', u'Unicode', 'String'])
        for key in self.ht:
            self.assertEqual(type(key), bytes)

        for key, _ in self.ht.items():
            self.assertEqual(type(key), bytes)


if __name__ == '__main__':
    unittest.main()
