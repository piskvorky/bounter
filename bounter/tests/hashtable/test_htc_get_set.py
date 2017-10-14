#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Filip Stefanak <f.stefanak@rare-technologies.com>
# Copyright (C) 2017 Rare Technologies
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).

import sys
import unittest

from bounter import HashTable

long_long_max = 9223372036854775807


class MyClass(object):
    pass


class HashTableGetSetTest(unittest.TestCase):
    """
    Functional tests for setting and retrieving values of the counter
    """

    def setUp(self):
        self.ht = HashTable(buckets=64)

    def test_unknown_is_zero(self):
        self.assertEqual(self.ht['foo'], 0)

    def test_set_and_get(self):
        foo_value = 42
        bar_value = 53

        self.ht['foo'] = foo_value
        self.ht['bar'] = bar_value
        self.ht['max'] = long_long_max

        self.assertEqual(self.ht['foo'], foo_value)
        self.assertEqual(self.ht['max'], long_long_max)
        self.assertEqual(self.ht['bar'], bar_value)

    def test_set_and_get_bytes(self):
        first_value = 42
        second_value = 53

        self.ht[b'foo'] = first_value
        self.assertEqual(self.ht['foo'], first_value)
        self.assertEqual(self.ht[b'foo'], first_value)

        self.ht['foo'] = second_value
        self.assertEqual(self.ht['foo'], second_value)
        self.assertEqual(self.ht[b'foo'], second_value)

    def test_replace(self):
        """
        Test that a set successfully replaces existing value of the counter
        """
        foo_value = 42
        new_value = 53

        self.ht['foo'] = foo_value
        self.ht['foo'] = new_value

        self.assertEqual(self.ht['foo'], new_value)

    def test_add_from_zero(self):
        """
        Test simple addition from zero value.
        Note that this is NOT recommended (use HashTable.increment instead) because python interprets it inefficiently,
        but we do want to support this case.
        """

        # SLOW, always prefer to use ht.increment('foo', 1) or ht.increment('foo') instead!
        self.ht['foo'] += 1
        self.assertEqual(self.ht['foo'], 1)

    def test_add_from_existing(self):
        """
        Test simple addition from existing value.
        Note that this is NOT recommended (use HashTable.increment instead) because python interprets it inefficiently,
        but we do want to support this case.
        """

        self.ht['foo'] = 1
        # SLOW, always prefer to use ht.increment('foo', 2) or ht.increment('foo') instead!
        self.ht['foo'] += 2
        self.assertEqual(self.ht['foo'], 3)

    def test_get_set_int_key(self):
        """
        Negative test: integer keys are not supported and yield TypeError
        """
        with self.assertRaises(TypeError):
            self.ht[1] = 42
        with self.assertRaises(TypeError):
            foo = self.ht[1]

    def test_delete_key(self):
        foo_value = 42
        bar_value = 53

        self.ht['foo'] = foo_value
        self.ht['bar'] = bar_value
        self.assertEqual(self.ht['foo'], foo_value)
        self.assertEqual(self.ht['bar'], bar_value)

        del self.ht['foo']
        self.assertEqual(self.ht['foo'], 0)
        self.assertEqual(self.ht['bar'], bar_value)

        del self.ht['bar']
        self.assertEqual(self.ht['foo'], 0)
        self.assertEqual(self.ht['bar'], 0)

    def test_get_set_object_key(self):
        """
        Negative test: object keys are not supported and yield TypeError
        """
        o = MyClass()

        with self.assertRaises(TypeError):
            self.ht[o] = 42
        with self.assertRaises(TypeError):
            foo = self.ht[o]

    def test_get_set_empty_string(self):
        self.ht['foo'] = 42
        self.ht['bar'] = 53

        self.assertEqual(self.ht[''], 0)
        self.ht[''] = 3
        self.assertEqual(self.ht[''], 3)
        del self.ht['']
        self.assertEqual(self.ht[''], 0)

    def test_get_set_long_string(self):
        long_string = 'l' + ('o' * 100) + 'ng'
        longer_string = 'l' + ('o' * 120) + 'ng'
        self.ht[long_string] = 2
        self.ht[longer_string] = 3

        self.assertEqual(self.ht[long_string], 2)
        self.assertEqual(self.ht[longer_string], 3)

        del self.ht[longer_string]
        self.assertEqual(self.ht[longer_string], 0)

    def test_get_set_nonascii_string(self):
        non_ascii_string = "Non-ascii dôverivá Čučoriedka 9#8\\%7 平仮名\n☃\t+☀\t=\t☹ "
        # the second line contains a different symbol
        similar_string = "Non-ascii dôverivá Čučoriedka 9#8\\%7 平仮名\n☃\t+☀\t=\t☺ "

        self.ht[non_ascii_string] = 2
        self.ht[similar_string] = 3

        self.assertEqual(self.ht[non_ascii_string], 2)
        self.assertEqual(self.ht[similar_string], 3)

        del self.ht[non_ascii_string]
        self.assertEqual(self.ht[non_ascii_string], 0)

    def test_get_set_nonascii_unicode(self):
        non_ascii_unicode = u"Non-ascii dôverivá Čučoriedka 9#8\\%7 平仮名\n☃\t+☀\t=\t☹ "
        # the second line contains a different symbol
        similar_unicode = u"Non-ascii dôverivá Čučoriedka 9#8\\%7 平仮名\n☃\t+☀\t=\t☺ "

        self.ht[non_ascii_unicode] = 2
        self.ht[similar_unicode] = 3

        self.assertEqual(self.ht[non_ascii_unicode], 2)
        self.assertEqual(self.ht[similar_unicode], 3)

        del self.ht[non_ascii_unicode]
        self.assertEqual(self.ht[non_ascii_unicode], 0)

    def test_set_float_value(self):
        """
        Negative test: float values are not supported and yield TypeError
        In Python 2, float values are converted to integers automatically without error, this is a "feature" of argument
        parsing.
        """
        if sys.version_info < (3, 0):
            return

        with self.assertRaises(TypeError):
            self.ht['foo'] = float(42.0)

    def test_set_string_value(self):
        """
        Negative test: string values are not supported and yield TypeError
        """
        with self.assertRaises(TypeError):
            self.ht['foo'] = 'bar'

    def test_set_object_value(self):
        """
        Negative test: object values are not supported and yield TypeError
        """

        class MyClass(object):
            pass

        with self.assertRaises(TypeError):
            self.ht['foo'] = MyClass()

    def test_get_set_big_number(self):
        big_number = 206184125847
        self.ht['big number'] = big_number
        self.assertEqual(self.ht['big number'], big_number)

    def test_set_negative(self):
        """
        Negative test, raises ValueError on negative values
        """
        # new value
        with self.assertRaises(ValueError):
            self.ht['foo'] = -4

        self.assertEqual(self.ht['foo'], 0, "value should remain unaffected")

        self.ht['foo'] = 3
        # existing value
        with self.assertRaises(ValueError):
            self.ht['foo'] = -2

        self.assertEqual(self.ht['foo'], 3, "value should remain unaffected")

    def test_set_number_greater_than_long_long_max(self):
        """
        Negative test: set fails on a number which is larger than long long's max
        """
        self.ht['toomuch'] = 42

        with self.assertRaises(OverflowError):
            self.ht['toomuch'] = long_long_max + 1

        self.assertEqual(self.ht['toomuch'], 42, 'value should remain unaffected')

    def test_set_zero(self):
        """
        Setting the zero value
        """
        self.ht['foo'] = 0
        self.assertEqual(self.ht['foo'], 0)

        self.ht['bar'] = 4
        self.assertEqual(self.ht['bar'], 4)
        self.ht['bar'] = 0
        self.assertEqual(self.ht['bar'], 0)


if __name__ == '__main__':
    unittest.main()
