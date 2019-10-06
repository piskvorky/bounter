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
from collections import Counter

from bounter import CountMinSketch

filename = 'cms-test.pickle'


class CountMinSketchPickleCommonTest(unittest.TestCase):
    """
    Functional tests for determining size (cardinality) of hashtable and iterations.
    """

    def __init__(self, methodName='runTest', log_counting=None):
        self.log_counting = log_counting
        super(CountMinSketchPickleCommonTest, self).__init__(methodName=methodName)

    def setUp(self):
        self.cms = CountMinSketch(2, log_counting=self.log_counting)

    def tearDown(self):
        if os.path.isfile(filename):
            os.remove(filename)

    def store_and_load(self):
        with open(filename, 'wb') as outfile:
            pickle.dump(self.cms, outfile)

        with open(filename, 'rb') as outfile:
            reloaded = pickle.load(outfile)

        return reloaded

    def check_cms(self, cms, data):
        self.assertAlmostEqual(cms.cardinality(), len(data))
        self.assertEqual(cms.total(), sum(data.values()))

        result_set = set()
        for key, expected_value in data.items():
            result_set.add((key, cms[key]))

        self.assertEqual(result_set, set(data.items()))

    def test_pickle_empty(self):
        reloaded = self.store_and_load()
        self.check_cms(reloaded, {})

    def test_pickle_simple(self):
        expected = Counter()
        for structure in [self.cms, expected]:
            structure.update("pickling")
            structure.update("lorem ipsum dolor amet")
            structure.update("122333444455555666666")

        self.check_cms(self.cms, expected)

        reloaded = self.store_and_load()
        self.check_cms(reloaded, expected)

    def test_pickle_increment_after_reload(self):
        expected = Counter()
        for structure in [self.cms, expected]:
            structure.update("pickling")
        self.cms.increment('1')
        self.cms.increment('2', 2)
        expected['1'] += 1
        expected['2'] += 2

        self.check_cms(self.cms, expected)

        reloaded = self.store_and_load()

        for structure in [reloaded, expected]:
            structure.update("pickling")
        reloaded.increment('1', 1)
        reloaded.increment('3', 3)
        expected['1'] += 1
        expected['3'] += 3
        self.check_cms(reloaded, expected)

class CountMinSketchPickleConservativeTest(CountMinSketchPickleCommonTest):
    def __init__(self, methodName='runTest'):
        super(CountMinSketchPickleConservativeTest, self).__init__(methodName=methodName, log_counting=None)


class CountMinSketchPickleLog1024Test(CountMinSketchPickleCommonTest):
    def __init__(self, methodName='runTest'):
        super(CountMinSketchPickleLog1024Test, self).__init__(methodName=methodName, log_counting=1024)


class CountMinSketchPickleLog8Test(CountMinSketchPickleCommonTest):
    def __init__(self, methodName='runTest'):
        super(CountMinSketchPickleLog8Test, self).__init__(methodName=methodName, log_counting=8)


def load_tests(loader, tests, pattern):
    test_cases = unittest.TestSuite()
    test_cases.addTests(loader.loadTestsFromTestCase(CountMinSketchPickleConservativeTest))
    test_cases.addTests(loader.loadTestsFromTestCase(CountMinSketchPickleLog1024Test))
    test_cases.addTests(loader.loadTestsFromTestCase(CountMinSketchPickleLog8Test))
    return test_cases


if __name__ == '__main__':
    unittest.main()
