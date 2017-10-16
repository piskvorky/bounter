#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Filip Stefanak <f.stefanak@rare-technologies.com>
# Copyright (C) 2017 Rare Technologies
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).

import unittest
from bounter import bounter, HashTable, CountMinSketch
import bounter_cmsc as cmsc


class BounterInitTest(unittest.TestCase):
    """Basic test for factory method.
    Tests for CountMinSketch and HashTable implementations found in respective subdirectories
    """

    def test_default_init(self):
        counter = bounter()
        self.assertEqual(type(counter), HashTable)

    def test_explicit_init(self):
        counter = bounter(size_mb=2, need_iteration=True)

        self.assertEqual(type(counter), HashTable)
        self.assertEqual(counter.buckets(), 2 ** 16)

    def test_cms_init_default(self):
        counter = bounter(need_iteration=False)

        self.assertEqual(type(counter), CountMinSketch)
        self.assertEqual(type(counter.cms), cmsc.CMS_Conservative)
        self.assertEqual(counter.size(), 2 ** 26)

    def test_cms_init_log8(self):
        counter = bounter(size_mb=1, need_iteration=False, log_counting=8)

        self.assertEqual(type(counter), CountMinSketch)
        self.assertEqual(type(counter.cms), cmsc.CMS_Log8)
        self.assertEqual(counter.size(), 2 ** 20)

    def test_ht_log_init(self):
        with self.assertRaises(ValueError):
            bounter(log_counting=8)

    def test_sanity(self):
        counter = bounter()
        counter.update([u'foo', u'bar', u'foo'])
        self.assertEqual(counter[u'foo'], 2)
        self.assertEqual(counter[u'bar'], 1)
        self.assertEqual(counter.cardinality(), 2)
