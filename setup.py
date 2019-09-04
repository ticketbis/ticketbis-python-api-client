# -*- coding: utf-8 -*-
#
# Copyright (c) 2015-2019 Ticketbis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Python wrapper for the Ticketbis API."""

import os

from setuptools import find_packages, setup

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("ticketbis", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

tests_require = ["pytest", "pytest-cov", "betamax", "betamax-serializers"]
extras_require = {"all": tests_require}
setup_requires = ["pytest-runner>=2.6.2"]

setup(
    name="ticketbis",
    version=version,
    author="Ticketbis",
    author_email="engineering@stubhub.com",
    url="https://github.com/ticketbis/ticketbis-python-api-client",
    description=__doc__,
    long_description=open("./README.md", "r").read(),
    long_description_content_type="text/markdown",
    download_url="https://github.com/ticketbis/ticketbis-python-api-client",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: Apache Software License",
    ],
    packages=find_packages(exclude=["tests"]),
    install_requires=["requests>=2.1", "six"],
    tests_require=tests_require,
    extras_require=extras_require,
    setup_requires=setup_requires,
    license="MIT License",
    keywords="ticketbis api",
    include_package_data=True,
    zip_safe=True,
)
