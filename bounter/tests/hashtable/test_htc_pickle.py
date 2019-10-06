#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Filip Stefanak <f.stefanak@rare-technologies.com>
# Copyright (C) 2017 Rare Technologies
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).

import os
import pickle
import unittest

from bounter import HashTable

filename = 'htc-test.pickle'


class HashTablePickleTest(unittest.TestCase):
    """
    Functional tests for determining size (cardinality) of hashtable and iterations.
    """

    def setUp(self):
        self.ht = HashTable(buckets=64)

    def tearDown(self):
        if os.path.isfile(filename):
            os.remove(filename)

    def check_hashtable(self, reloaded):
        self.assertEqual(len(reloaded), len(self.ht))
        self.assertEqual(reloaded.buckets(), self.ht.buckets())
        self.assertEqual(reloaded.total(), self.ht.total())
        self.assertEqual(set(reloaded.items()), set(self.ht.items()))
        self.assertEqual(reloaded.quality(), self.ht.quality())
        self.assertEqual(reloaded.cardinality(), self.ht.cardinality())

    def store_and_load(self):
        with open(filename, 'wb') as outfile:
            pickle.dump(self.ht, outfile)

        with open(filename, 'rb') as outfile:
            reloaded = pickle.load(outfile)

        return reloaded

    def test_pickle_empty(self):
        reloaded = self.store_and_load()
        self.check_hashtable(reloaded)

    def test_pickle_simple(self):
        self.ht.update("boss")
        self.ht.update("pickling")

        reloaded = self.store_and_load()
        self.check_hashtable(reloaded)

    def test_pickle_deleted(self):
        self.ht.update("boss")
        self.ht.update("pickling")
        del self.ht['g']
        del self.ht['s']

        reloaded = self.store_and_load()
        self.check_hashtable(reloaded)

    def test_pickle_pruned(self):
        for i in range(120):
            self.ht.increment(str(i), 1 + ((i * 27) % 17))

        reloaded = self.store_and_load()
        self.check_hashtable(reloaded)

    def test_pickle_large(self):
        self.ht = HashTable(buckets=2 ** 25)
        self.ht.update("boss")
        self.ht.update("pickling")
        self.ht.update("verylargetable")

        reloaded = self.store_and_load()
        self.check_hashtable(reloaded)



if __name__ == '__main__':
    unittest.main()
