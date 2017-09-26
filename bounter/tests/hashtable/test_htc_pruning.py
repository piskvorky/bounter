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


class HashTablePruningTest(unittest.TestCase):

    def test_prune_with_four_buckets(self):
        """
        Tests prune with a stupid table of 4 buckets, this can store at most 3 elements at once.
        """
        ht = HashTable(buckets=4)

        # Adds elements one by one. d replaces 'e', then 'e' replaces 'b'
        ht.update({'e': 1, 'a': 3, 'b': 2})
        ht.update({'d': 5})
        ht.update({'e': 4})
        self.assertEqual(set(ht.items()), set({'a': 3, 'd': 5, 'e': 4}.items()))
        self.assertEqual(len(ht), 3, "The number of elements after pruning should be 3")

        # Increment existing 'a', then add 'b' which evicts 2 elements with the lowest value of 4
        ht.increment('a')
        self.assertEqual(len(ht), 3)
        self.assertEqual(set(ht.items()), set({'a': 4, 'd': 5, 'e': 4}.items()))
        ht.increment('b')
        self.assertEqual(len(ht), 2, "The number of elements after pruning should be 3")
        self.assertEqual(set(ht.items()), set({'b': 1, 'd': 5}.items()))

    def test_prune_with_eight_buckets(self):
        """
        Tests prune with table of 8 buckets, which stores at most 6 elements and prunes itself down to 4 or less.
        """
        ht = HashTable(buckets=8)

        # Init
        ht.update({'a': 3, 'b': 2, 'c': 4, 'd': 1, 'e': 5, 'f': 6})
        self.assertEqual(set(ht.items()), set({'d': 1, 'b': 2, 'a': 3, 'c': 4, 'e': 5, 'f': 6}.items()))
        self.assertEqual(len(ht), 6)

        # Evicts 2 elements (so that half of the table is free) before adding x
        ht.update(['x'])
        self.assertEqual(set(ht.items()), set({'x': 1, 'a': 3, 'c': 4, 'e': 5, 'f': 6}.items()))
        self.assertEqual(len(ht), 5)

        # Evicts 3 elements because 'a' and 'b' share the count which needs to be included in the limit
        ht.update(['b', 'b', 'b'])
        self.assertEqual(set(ht.items()), set({'x': 1, 'b': 3, 'a': 3, 'c': 4, 'e': 5, 'f': 6}.items()))
        ht['d'] += 1
        self.assertEqual(set(ht.items()), set({'d': 1, 'c': 4, 'e': 5, 'f': 6}.items()))

    def test_prune_total(self):
        ht = HashTable(buckets=8)
        ht.update({'a': 3, 'b': 2, 'c': 4, 'd': 1, 'e': 5, 'f': 6})
        ht.update("xbbbd")
        self.assertEqual(ht.total(), 26)

    def test_prune_cardinality(self):
        ht = HashTable(buckets=8)
        ht.update({'a': 3, 'b': 2, 'c': 4, 'd': 1, 'e': 5, 'f': 6})
        ht.update("xbgbbd")
        self.assertEqual(ht.cardinality(), 8)


if __name__ == '__main__':
    unittest.main()
