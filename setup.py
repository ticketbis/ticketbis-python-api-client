#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2015 Ticketbis

from setuptools import setup, find_packages

import ticketbis
version = str(ticketbis.__version__)

setup(
    name='ticketbis',
    version=version,
    author='Jose Gargallo',
    author_email='jose.gargallo@ticketbis.com',
    url='http://github.com/ticketbis/ticketbis',
    description='easy-as-pie ticketbis wrapper library',
    long_description=open('./README.txt', 'r').read(),
    download_url='http://github.com/ticketbis/ticketbis/tarball/master',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'License :: OSI Approved :: MIT License',
        ],
    packages=find_packages(),
    install_requires=[
        'requests>=2.1',
        'six',
    ],
    license='MIT License',
    keywords='ticketbis api',
    include_package_data=True,
    zip_safe=True,
)
