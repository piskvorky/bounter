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


class CountMinSketchUpdateCommonTest(unittest.TestCase):
    def __init__(self, methodName='runTest', log_counting=None):
        self.log_counting = log_counting
        super(CountMinSketchUpdateCommonTest, self).__init__(methodName=methodName)

    """
    Functional tests for CountMinSketch.update method, which adds another counter, dictionary, hashtable, tuple or list
    """

    def setUp(self):
        self.cms = CountMinSketch(1, log_counting=self.log_counting)

    def test_update_numbers(self):
        """
        Negative test: calling update using numeric values as parameter yields TypeError
        """
        with self.assertRaises(TypeError):
            self.cms.update(1)

        with self.assertRaises(TypeError):
            self.cms.update(1.0)

    def test_update_string(self):
        self.cms.update("foo")
        self.assertEqual(self.cms['f'], 1)
        self.assertEqual(self.cms['o'], 2)

    def test_update_tuple(self):
        tuple = ('foo', 'bar', 'foo')
        self.cms.update(tuple)
        self.assertEqual(self.cms['foo'], 2)
        self.assertEqual(self.cms['bar'], 1)

    def test_update_bytes(self):
        tuple = (b'foo', b'bar', b'foo')
        self.cms.update(tuple)
        self.assertEqual(self.cms['foo'], 2)
        self.assertEqual(self.cms[b'foo'], 2)
        self.assertEqual(self.cms['bar'], 1)

    def test_update_unicode(self):
        tuple = ('foo', 'bar', u'foo')
        self.cms.update(tuple)
        self.assertEqual(self.cms['foo'], 2)
        self.assertEqual(self.cms[u'foo'], 2)

    def test_update_list(self):
        self.cms.update([str(i % 3) for i in range(5)])
        self.assertEqual(self.cms['0'], 2)
        self.assertEqual(self.cms['1'], 2)
        self.assertEqual(self.cms['2'], 1)

    def test_update_split(self):
        self.cms.update("This is a sentence".split())
        self.assertEqual(self.cms['is'], 1)
        self.assertEqual(self.cms['this'], 0)  # lowercase

    def test_update_twice(self):
        tuple = ('foo', 'bar', 'foo')
        self.cms.update(tuple)
        self.cms.update(('foo', 'bar', 'foo'))
        self.assertEqual(self.cms['foo'], 4)
        self.assertEqual(self.cms['bar'], 2)

    def test_update_with_dictionary(self):
        """
        Update with a dictionary and test against it using set representation
        """
        data = {'a': 1, 'b': 3, 'c': 2, 'd': 5}

        self.cms.update(data)

        self.assertEqual(self.cms['b'], 3)

        result_set = set()
        for key, expected_value in data.items():
            result_set.add((key, self.cms[key]))

        self.assertEqual(set(result_set), set(data.items()))

    def test_update_with_cms(self):
        """
        Update with a dictionary and test against it using set representation
        The log variants are only precise up to 2048 (16), so we don't use larger values here
        """
        data1 = {'a': 1, 'b': 3, 'c': 2, 'd': 5}
        data2 = {'a': 15, 'b': 4, 'c': 6, 'e': 13}
        expected = {'a': 16, 'b': 7, 'c': 8, 'd': 5, 'e': 13}

        self.cms.update(data1)
        cms2 = CountMinSketch(1, log_counting=self.log_counting)
        cms2.update(data2)
        self.cms.update(cms2)

        result_set = set()
        for key, expected_value in expected.items():
            result_set.add((key, self.cms[key]))

        self.assertEqual(set(result_set), set(expected.items()))

class CountMinSketchUpdateConservativeTest(CountMinSketchUpdateCommonTest):
    def __init__(self, methodName='runTest'):
        super(CountMinSketchUpdateConservativeTest, self).__init__(methodName=methodName, log_counting=None)


class CountMinSketchUpdateLog1024Test(CountMinSketchUpdateCommonTest):
    def __init__(self, methodName='runTest'):
        super(CountMinSketchUpdateLog1024Test, self).__init__(methodName=methodName, log_counting=1024)


class CountMinSketchUpdateLog8Test(CountMinSketchUpdateCommonTest):
    def __init__(self, methodName='runTest'):
        super(CountMinSketchUpdateLog8Test, self).__init__(methodName=methodName, log_counting=8)


def load_tests(loader, tests, pattern):
    test_cases = unittest.TestSuite()
    test_cases.addTests(loader.loadTestsFromTestCase(CountMinSketchUpdateConservativeTest))
    test_cases.addTests(loader.loadTestsFromTestCase(CountMinSketchUpdateLog1024Test))
    test_cases.addTests(loader.loadTestsFromTestCase(CountMinSketchUpdateLog8Test))
    return test_cases


if __name__ == '__main__':
    unittest.main()
