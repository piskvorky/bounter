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


class HashTableItemsTest(unittest.TestCase):
    """
    Functional tests for determining size (cardinality) of hashtable and iterations.
    """

    def setUp(self):
        self.ht = HashTable(buckets=64)

    def test_simple_length_test(self):
        self.assertEqual(len(self.ht), 0)

        self.ht.update("boss")
        self.assertEqual(len(self.ht), 3)

        self.ht.update("sad")
        self.assertEqual(len(self.ht), 5)

    def test_simple_cardinality_test(self):
        self.assertEqual(self.ht.cardinality(), 0)

        self.ht.update("boss")
        self.assertEqual(self.ht.cardinality(), 3)

        self.ht.update("sad")
        self.assertEqual(self.ht.cardinality(), 5)


    def test_delete_length_test(self):
        self.ht.update("boss")
        self.assertEqual(len(self.ht), 3)

        del self.ht['s']
        self.assertEqual(len(self.ht), 2)
        del self.ht['s']
        self.assertEqual(len(self.ht), 2)

    def test_delete_prune_length_iteration_test(self):
        self.ht = HashTable(buckets=8)
        self.ht.update("bbboss")
        self.assertEqual(len(self.ht), 3)

        del self.ht['s']
        self.assertEqual(len(self.ht), 2)
        self.ht.update("122333")

        self.assertEqual(len(self.ht), 5)
        # should iterate over 5 elements
        self.assertEqual(set(self.ht.items()), set({'b': 3, 'o': 1, '1': 1, '2': 2, '3': 3}.items()))

        # the next add will overflow because the deleted bucket is still physically there so the 'real' size is 5
        self.ht.update("!")  # overflow removes '1', 'o', and the empty bucket
        self.assertEqual(len(self.ht), 4)
        # should iterate over 4 elements
        self.assertEqual(set(self.ht.items()), set({'b': 3, '!': 1, '2': 2, '3': 3}.items()))

        self.assertEqual(self.ht.cardinality(), 7)


if __name__ == '__main__':
    unittest.main()
