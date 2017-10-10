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

long_long_max = 9223372036854775807


class HashTableUpdateTest(unittest.TestCase):
    """
    Functional tests for HashTable.update method, which adds another counter, dictionary, hashtable, tuple or list
    """

    def setUp(self):
        self.ht = HashTable(buckets=64)

    def test_update_numbers(self):
        """
        Negative test: calling update using numeric values as parameter yields TypeError
        """
        with self.assertRaises(TypeError):
            self.ht.update(1)

        with self.assertRaises(TypeError):
            self.ht.update(1.0)

    def test_update_string(self):
        self.ht.update("foo")
        self.assertEqual(self.ht['f'], 1)
        self.assertEqual(self.ht['o'], 2)

    def test_update_tuple(self):
        tuple = ('foo', 'bar', 'foo')
        self.ht.update(tuple)
        self.assertEqual(self.ht['foo'], 2)
        self.assertEqual(self.ht['bar'], 1)

    def test_update_list(self):
        self.ht.update([str(i % 3) for i in range(5)])
        self.assertEqual(self.ht['0'], 2)
        self.assertEqual(self.ht['1'], 2)
        self.assertEqual(self.ht['2'], 1)

    def test_update_split(self):
        self.ht.update("This is a sentence".split())
        self.assertEqual(self.ht['is'], 1)
        self.assertEqual(self.ht['this'], 0)  # lowercase

    def test_update_twice(self):
        tuple = ('foo', 'bar', 'foo')
        self.ht.update(tuple)
        self.ht.update(('foo', 'bar', 'foo'))
        self.assertEqual(self.ht['foo'], 4)
        self.assertEqual(self.ht['bar'], 2)

    def test_update_bytes(self):
        tuple = ('foo', 'bar', b'foo')
        self.ht.update(tuple)
        self.assertEqual(self.ht['foo'], 2)
        self.assertEqual(self.ht[b'foo'], 2)

    def test_update_unicode(self):
        tuple = ('foo', 'bar', u'foo')
        self.ht.update(tuple)
        self.assertEqual(self.ht['foo'], 2)
        self.assertEqual(self.ht[u'foo'], 2)

    def test_update_with_dictionary(self):
        """
        Update with a dictionary and test against it using set representation
        """
        data = {'a': 1, 'b': 3, 'c': 2, 'd': 5}

        self.ht.update(data)

        self.assertEqual(self.ht['b'], 3)
        self.assertEqual(set(self.ht.items()), set(data.items()))

    def test_update_with_hashtable(self):
        """
        Update with a dictionary and test against it using set representation
        """
        data1 = {'a': 1, 'b': 3, 'c': 2, 'd': 5}
        data2 = {'a': 18, 'b': 4, 'c': 6, 'e': 13}
        expected = {'a': 19, 'b': 7, 'c': 8, 'd': 5, 'e': 13}

        self.ht.update(data1)
        ht2 = HashTable(64)
        ht2.update(data2)

        self.ht.update(ht2)

        self.assertEqual(set(self.ht.items()), set(expected.items()))

if __name__ == '__main__':
    unittest.main()
