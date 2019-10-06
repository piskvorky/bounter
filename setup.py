#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Filip Stefanak <f.stefanak@rare-technologies.com>
# Copyright (C) 2017 Rare Technologies
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).

import sys, os, io

if sys.version_info < (2, 7):
    raise ImportError("bounter requires python >= 2.7")

# TODO add ez_setup?
from setuptools import setup, find_packages, Extension


def read(fname):
    name = os.path.join(os.path.dirname(__file__), fname)
    if not os.path.isfile(name):
        return ''
    with io.open(name, encoding='utf-8') as readfile:
        return readfile.read()

setup(
    name='bounter',
    version='1.1.0',
    description='Counter for large datasets',
    long_description=read('README.rst'),

    headers=['cbounter/hll.h', 'cbounter/murmur3.h'],
    ext_modules=[
        Extension('bounter_cmsc', ['cbounter/cms_cmodule.c', 'cbounter/murmur3.c', 'cbounter/hll.c']),
        Extension('bounter_htc', ['cbounter/ht_cmodule.c', 'cbounter/murmur3.c', 'cbounter/hll.c'])
    ],
    packages=find_packages(),

    author=u'Filip Stefanak',
    author_email='f.stefanak@rare-technologies.com',
    maintainer=u'RARE Technologies',
    maintainer_email='opensource@rare-technologies.com',

    url='https://github.com/RaRe-Technologies/bounter',
    download_url='http://pypi.python.org/pypi/bounter',

    keywords='counter, count-min sketch, bounded memory, hyperloglog, approximative counting, cardinality estimation',

    license='MIT',
    platforms='any',
    test_suite="bounter.tests",

    classifiers=[  # from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)
