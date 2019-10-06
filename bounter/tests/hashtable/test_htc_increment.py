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


class HashTableIncrementTest(unittest.TestCase):
    """
    Functional tests for HashTable.increment method
    """

    def test_basic_increments(self):
        """
        Tests increment operation
        """
        ht = HashTable(buckets=64)

        # new element
        ht.increment('New element by default')
        self.assertEqual(ht['New element by default'], 1)

        # new element by X
        ht.increment('New element by 3', 3)
        self.assertEqual(ht['New element by 3'], 3)

        # repeated increments
        ht.increment('2 repeated increments')
        ht.increment('2 repeated increments')
        self.assertEqual(ht['2 repeated increments'], 2)

        # repeated increments by X
        ht.increment('3 repeated increments by 4', 4)
        ht.increment('3 repeated increments by 4', 4)
        ht.increment('3 repeated increments by 4', 4)
        self.assertEqual(ht['3 repeated increments by 4'], 12)

    def test_increment_by_big_number(self):
        ht = HashTable(buckets=64)

        # increment by big number
        big_number = 68728041949
        ht.increment('big number', big_number)
        self.assertEqual(ht['big number'], big_number)
        ht.increment('big number', 1)
        self.assertEqual(ht['big number'], big_number + 1)

    def test_increment_by_long_long_max(self):
        ht = HashTable(buckets=64)

        ht.increment('max', long_long_max)
        self.assertEqual(ht['max'], long_long_max)

    def test_increment_by_number_greater_than_long_long_max(self):
        """
        Negative test: increment fails on a number which is larger than long long's max
        """
        ht = HashTable(buckets=64)

        with self.assertRaises(OverflowError):
            ht.increment('toomuch', long_long_max + 1)

        self.assertEqual(ht['toomuch'], 0, 'Should be unaffected')

    def test_increment_overflow(self):
        """
        Negative test for overflowing on max counter value (long long max)
        """
        ht = HashTable(buckets=64)
        ht['max'] = long_long_max
        with self.assertRaises(OverflowError):
            ht.increment('max', 1)

        three_quarters_of_long_long_max = int(long_long_max * 3 / 4)
        ht['foo'] = three_quarters_of_long_long_max
        with self.assertRaises(OverflowError):
            ht.increment('max', three_quarters_of_long_long_max)

    def test_increment_by_zero(self):
        """
        Tests that increment by zero does not affect the counter
        """
        ht = HashTable(buckets=64)
        ht['bar'] = 2

        ht.increment('foo', 0)
        self.assertEqual(ht['foo'], 0)

        ht.increment('bar', 0)
        self.assertEqual(ht['bar'], 2)

    def test_increment_negative(self):
        ht = HashTable(buckets=64)
        ht.increment('foo', 3)

        # new value
        with self.assertRaises(ValueError):
            ht.increment('bar', -1)

        # existing value
        with self.assertRaises(ValueError):
            ht.increment('foo', -2)


if __name__ == '__main__':
    unittest.main()
