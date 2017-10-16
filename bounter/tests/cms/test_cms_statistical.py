#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Filip Stefanak <f.stefanak@rare-technologies.com>
# Copyright (C) 2017 Rare Technologies
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).

import math
import unittest
from collections import Counter

from bounter import CountMinSketch


class MyClass(object):
    pass


def generateData(cardinality):
    """
    Generates n * n log_2 n numeric strings with different frequencies, using n different strings.
    The most frequent string "1" will have a frequency of n, each additional bit halves this frequency
    """
    for i in range(cardinality):
        j = i + 1
        while j > 0:
            yield str(j)
            j //= 2


def stats(cms, expected):
    variance = 0
    sum_log_error_sq = 0
    max_log_error = 0
    max_error_expected = 0
    max_d_error = 0
    estimated_total = 0
    for key, expected_value in expected.items():
        d = cms[key] - expected_value
        logd = math.log(cms[key]) - math.log(expected_value)
        logds = logd ** 2
        sum_log_error_sq += logds
        if logds > max_log_error ** 2:
            max_log_error = logd
            max_d_error = d
            max_error_expected = expected_value
        variance += d ** 2
        estimated_total += expected_value + d

    cardinality = len(expected)
    deviation = math.sqrt(float(variance) / cardinality)
    average = float(cms.total()) / cardinality
    estimated_average = float(estimated_total) / cardinality
    bias = float(estimated_average) / average - 1
    avg_log_error = math.sqrt(sum_log_error_sq / cardinality)
    return bias, deviation, max_log_error, avg_log_error, max_d_error, max_error_expected


class CountMinSketchStatisticalCommonTest(unittest.TestCase):
    """
    Functional tests for setting and retrieving values of the counter
    """

    def __init__(
            self, methodName='runTest',
            log_counting=None,
            avg_log_tolerance=0.0,
            max_log_tolerance=0.0,
            total_bias_tolerance=0.0):
        self.log_counting = log_counting
        self.avg_log_tolerance = avg_log_tolerance
        self.max_log_tolerance = max_log_tolerance
        self.total_bias_tolerance = total_bias_tolerance
        super(CountMinSketchStatisticalCommonTest, self).__init__(methodName=methodName)

    def test_update_no_collisions(self):
        """
        Tests the results of different algorithms with parameters chosen so that no hash collision affects results
        """
        width = 2 ** 17
        cardinality = width // 4
        cms = CountMinSketch(width=width, depth=8, log_counting=self.log_counting)
        cms.update(generateData(cardinality))
        expected = Counter()
        expected.update(generateData(cardinality))

        bias, deviation, max_log_error, avg_log_error, max_d_error, max_error_expected = stats(cms, expected)

        self.assertAlmostEqual(
            max_log_error, 0,
            msg="Each result should be within maximum tolerance",
            delta=self.max_log_tolerance)
        self.assertAlmostEqual(
            avg_log_error, 0,
            msg="Average log deviation should be low",
            delta=self.avg_log_tolerance)
        self.assertAlmostEqual(
            bias, 0,
            msg="Total bias should be low",
            delta=self.total_bias_tolerance)


class CountMinSketchStatisticalConservativeTest(CountMinSketchStatisticalCommonTest):
    def __init__(self, methodName='runTest'):
        super(CountMinSketchStatisticalConservativeTest, self).__init__(methodName=methodName)


class CountMinSketchStatisticalLog1024Test(CountMinSketchStatisticalCommonTest):
    """
    Tests Log1024
    Average deviation is within +/- 0.1%
    Maximum deviation is within +/- 10%
    Total counter bias (bias of average value) is within +/-0.5%
    """

    def __init__(self, methodName='runTest'):
        super(CountMinSketchStatisticalLog1024Test, self).__init__(
            methodName=methodName, log_counting=1024,
            avg_log_tolerance=0.001, max_log_tolerance=0.1,
            total_bias_tolerance=0.005)


class CountMinSketchStatisticalLog8Test(CountMinSketchStatisticalCommonTest):
    """
    Tests Log8
    Average deviation is within +/- 5%
    Maximum deviation is within -61% and +158%
    Total counter bias (bias of average value) is within +/-10%
    """

    def __init__(self, methodName='runTest'):
        super(CountMinSketchStatisticalLog8Test, self).__init__(
            methodName=methodName, log_counting=8,
            avg_log_tolerance=0.05, max_log_tolerance=0.95,
            total_bias_tolerance=0.1)


def load_tests(loader, tests, pattern):
    test_cases = unittest.TestSuite()
    test_cases.addTests(loader.loadTestsFromTestCase(CountMinSketchStatisticalConservativeTest))
    test_cases.addTests(loader.loadTestsFromTestCase(CountMinSketchStatisticalLog1024Test))
    test_cases.addTests(loader.loadTestsFromTestCase(CountMinSketchStatisticalLog8Test))
    return test_cases


if __name__ == '__main__':
    unittest.main()
