#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import easypost

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = easypost.__version__

readme = open('README.md').read()

setup(
    name='django-easypost',
    version=version,
    description='',
    long_description=readme,
    author='Mobelux',
    author_email='contact@mobelux.com',
    url='https://github.com/mobelux/django-easypost',
    packages=[
        'easypost',
    ],
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
