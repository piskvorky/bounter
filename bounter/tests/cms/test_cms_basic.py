#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Filip Stefanak <f.stefanak@rare-technologies.com>
# Copyright (C) 2017 Rare Technologies
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).

import unittest

from bounter import CountMinSketch


class MyClass(object):
    pass


class CountMinSketchSanityCommonTest(unittest.TestCase):
    """
    Functional tests for setting and retrieving values of the counter
    """

    def __init__(self, methodName='runTest', log_counting=None, delta=0.0):
        self.log_counting = log_counting
        self.delta = delta
        super(CountMinSketchSanityCommonTest, self).__init__(methodName=methodName)

    def setUp(self):
        self.cms = CountMinSketch(1, log_counting=self.log_counting)

    def test_unknown_is_zero(self):
        self.assertEqual(self.cms['foo'], 0)

    def test_increment_default(self):
        self.cms.increment('foo')
        self.cms.increment('bar')
        self.cms.increment('foo')
        self.cms.increment('foo')

        self.assertEqual(self.cms['foo'], 3)
        self.assertEqual(self.cms['bar'], 1)

    def test_increment_bytes(self):
        self.cms.increment('foo')
        self.cms.increment('bar')
        self.cms.increment(b'foo')
        self.cms.increment('foo')

        self.assertEqual(self.cms['foo'], 3)
        self.assertEqual(self.cms[b'foo'], 3)

    def test_total(self):
        self.assertEqual(self.cms.total(), 0)

        self.cms.increment('foo')
        self.cms.increment('bar')
        self.cms.increment('foo')
        self.cms.increment('foo')
        self.assertEqual(self.cms.total(), 4)

        self.cms.increment('goo', 3)
        self.assertEqual(self.cms.total(), 7)

    def test_cardinality(self):
        self.assertEqual(self.cms.cardinality(), 0)

        self.cms.increment('foo')
        self.cms.increment('bar')
        self.cms.increment('foo')
        self.cms.increment('foo')
        self.assertEqual(self.cms.cardinality(), 2)

        self.cms.increment('goo', 3)
        self.assertEqual(self.cms.cardinality(), 3)

    def test_increment_by_value(self):
        foo_value = 42
        bar_value = 53

        self.cms.increment('foo', foo_value)
        self.cms.increment('bar', bar_value)

        self.assertAlmostEqual(self.cms['foo'], foo_value, delta=self.delta * foo_value)
        self.assertAlmostEqual(self.cms['bar'], bar_value, delta=self.delta * bar_value)

    def test_repeat_increment(self):
        """
        Test that a set successfully replaces existing value of the counter
        """

        self.cms.increment('foo', 5)
        self.cms.increment('foo', 10)

        self.assertEqual(self.cms['foo'], 15)

    def test_increment_int_key(self):
        """
        Negative test: integer keys are not supported and yield TypeError
        """
        with self.assertRaises(TypeError):
            self.cms.increment(1)

    def test_get_increment_object_key(self):
        """
        Negative test: object keys are not supported and yield TypeError
        """
        o = MyClass()

        with self.assertRaises(TypeError):
            self.cms.increment(o)

    def test_get_increment_empty_string(self):
        self.cms.increment('foo', 42)
        self.cms.increment('bar', 53)

        self.assertEqual(self.cms[''], 0)
        self.cms.increment('', 3)
        self.assertEqual(self.cms[''], 3)
        self.cms.increment('')
        self.assertEqual(self.cms[''], 4)

    def test_get_increment_long_string(self):
        long_string = 'l' + ('o' * 100) + 'ng'
        longer_string = 'l' + ('o' * 120) + 'ng'
        self.cms.increment(long_string, 2)
        self.cms.increment(longer_string, 3)

        self.assertEqual(self.cms[long_string], 2)
        self.assertEqual(self.cms[longer_string], 3)

    def test_get_increment_non_ascii_string(self):
        non_ascii_string = "Non-ascii dôverivá Čučoriedka 9#8\\%7 平仮名\n☃\t+☀\t=\t☹ "
        # the second line contains a different symbol
        similar_string = "Non-ascii dôverivá Čučoriedka 9#8\\%7 平仮名\n☃\t+☀\t=\t☺ "

        self.cms.increment(non_ascii_string, 2)
        self.cms.increment(similar_string, 3)

        self.assertEqual(self.cms[non_ascii_string], 2)
        self.assertEqual(self.cms[similar_string], 3)

    def test_get_increment_non_ascii_unicode(self):
        non_ascii_unicode = u"Non-ascii dôverivá Čučoriedka 9#8\\%7 平仮名\n☃\t+☀\t=\t☹ "
        # the second line contains a different symbol
        similar_unicode = u"Non-ascii dôverivá Čučoriedka 9#8\\%7 平仮名\n☃\t+☀\t=\t☺ "

        self.cms.increment(non_ascii_unicode, 2)
        self.cms.increment(similar_unicode, 3)

        self.assertEqual(self.cms[non_ascii_unicode], 2)
        self.assertEqual(self.cms[similar_unicode], 3)

    def test_increment_string_value(self):
        """
        Negative test: string values are not supported and yield TypeError
        """
        with self.assertRaises(TypeError):
            self.cms.increment('foo', 'bar')

    def test_set_object_value(self):
        """
        Negative test: object values are not supported and yield TypeError
        """

        class MyClass(object):
            pass

        with self.assertRaises(TypeError):
            self.cms.increment('foo', MyClass())

    def test_increment_big_number(self):
        big_number = 127451
        self.cms.increment('big number', big_number)
        self.assertAlmostEqual(self.cms['big number'], big_number, delta=self.delta * big_number)

    def test_increment_negative(self):
        """
        Negative test, raises ValueError on negative values
        """
        # new value
        with self.assertRaises(ValueError):
            self.cms.increment('foo', -4)

        self.assertEqual(self.cms['foo'], 0, "value should remain unaffected")

        self.cms.increment('foo', 3)
        # existing value
        with self.assertRaises(ValueError):
            self.cms.increment('foo', -2)

        self.assertEqual(self.cms['foo'], 3, "value should remain unaffected")

    def test_increment_zero(self):
        """
        Setting the zero value
        """
        self.cms.increment('foo', 0)
        self.assertEqual(self.cms['foo'], 0)

        self.cms.increment('foo')
        self.cms.increment('foo', 0)
        self.assertEqual(self.cms['foo'], 1)


class CountMinSketchSanityConservativeTest(CountMinSketchSanityCommonTest):
    def __init__(self, methodName='runTest'):
        super(CountMinSketchSanityConservativeTest, self).__init__(methodName=methodName, log_counting=None)


class CountMinSketchSanityLog1024Test(CountMinSketchSanityCommonTest):
    def __init__(self, methodName='runTest'):
        super(CountMinSketchSanityLog1024Test, self).__init__(methodName=methodName, log_counting=1024, delta=0.15)


class CountMinSketchSanityLog8Test(CountMinSketchSanityCommonTest):
    def __init__(self, methodName='runTest'):
        super(CountMinSketchSanityLog8Test, self).__init__(methodName=methodName, log_counting=8, delta=0.8)


def load_tests(loader, tests, pattern):
    test_cases = unittest.TestSuite()
    test_cases.addTests(loader.loadTestsFromTestCase(CountMinSketchSanityConservativeTest))
    test_cases.addTests(loader.loadTestsFromTestCase(CountMinSketchSanityLog1024Test))
    test_cases.addTests(loader.loadTestsFromTestCase(CountMinSketchSanityLog8Test))
    return test_cases

if __name__ == '__main__':
    unittest.main()
