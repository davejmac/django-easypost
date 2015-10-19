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
    description='A django wrapper for the python easypost library',
    long_description=readme,
    author='Dave McNamara',
    author_email='david.mcnamara@outlook.com',
    url='https://github.com/davejmac/django-easypost',
    packages=[
        'easypost',
    ],
    include_package_data=True,
    install_requires=[
    ],
    license="MIT",
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
