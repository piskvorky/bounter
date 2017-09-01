#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Filip Stefanak <f.stefanak@rare-technologies.com>
# Copyright (C) 2017 Rare Technologies
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).


import io
import os
import sys

if sys.version_info < (2, 7):
    raise ImportError("bounter requires python >= 2.7")

# TODO add ez_setup?
from setuptools import setup, find_packages


def read(fname):
    return io.open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()


def extract_requirements():
    return read('requirements.txt').splitlines()


setup(
    name='bounter',
    version='0.1.0',
    description='Counting frequencies in large data sets with constrained memory',
    long_description=read('README.md'),

    packages=find_packages(),

    author=u'Filip Stefanak',
    author_email='f.stefanak@rare-technologies.com',
    maintainer=u'Filip Stefanak',
    maintainer_email='f.stefanak@rare-technologies.com',

    url='https://github.com/RaRe-Technologies/bounter',
    download_url='http://pypi.python.org/pypi/bounter',

    keywords='counter, count-min sketch, bounded memory',

    license='MIT',
    platforms='any',

    install_requires=extract_requirements(),

    classifiers=[  # from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 2 - Pre-Alpha',
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
