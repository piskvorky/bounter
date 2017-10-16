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


class CountMinSketchQualityCommonTest(unittest.TestCase):
    def __init__(self, methodName='runTest', log_counting=None):
        self.log_counting = log_counting
        super(CountMinSketchQualityCommonTest, self).__init__(methodName=methodName)

    """
    Functional tests for CountMinSketch.quality method, which returns quality rating of the structure
    """

    def setUp(self):
        self.cms = CountMinSketch(1, log_counting=self.log_counting)

    def test_quality_default(self):
        """
        Uses the default structure
        """
        self.assertEqual(self.cms.quality(), 0)

        three_quarters = int((self.cms.width * 3) / 4)
        for i in range(three_quarters):
            self.cms.increment(str(i), 1 + (i % 13))

        self.assertGreaterEqual(self.cms.quality(), 0.5)
        self.assertLessEqual(self.cms.quality(), 1.0)

        for i in range(three_quarters * 7):
            self.cms.increment(str(i), 1 + (i % 13))

        self.assertGreaterEqual(self.cms.quality(), 4.0)
        self.assertLessEqual(self.cms.quality(), 6.0)


class CountMinSketchQualityConservativeTest(CountMinSketchQualityCommonTest):
    def __init__(self, methodName='runTest'):
        super(CountMinSketchQualityConservativeTest, self).__init__(methodName=methodName, log_counting=None)


class CountMinSketchQualityLog1024Test(CountMinSketchQualityCommonTest):
    def __init__(self, methodName='runTest'):
        super(CountMinSketchQualityLog1024Test, self).__init__(methodName=methodName, log_counting=1024)


class CountMinSketchQualityLog8Test(CountMinSketchQualityCommonTest):
    def __init__(self, methodName='runTest'):
        super(CountMinSketchQualityLog8Test, self).__init__(methodName=methodName, log_counting=8)


def load_tests(loader, tests, pattern):
    test_cases = unittest.TestSuite()
    test_cases.addTests(loader.loadTestsFromTestCase(CountMinSketchQualityConservativeTest))
    test_cases.addTests(loader.loadTestsFromTestCase(CountMinSketchQualityLog1024Test))
    test_cases.addTests(loader.loadTestsFromTestCase(CountMinSketchQualityLog8Test))
    return test_cases


if __name__ == '__main__':
    unittest.main()
