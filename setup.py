#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from glob import glob
import os
from os.path import basename, dirname, join, splitext


try:
    from setuptools import find_packages, setup
except ImportError as e:
    from distutils.core import setup

DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(DIR, "docs", "README.txt"), "r") as f:
    long_description = f.read()
with open(os.path.join(DIR, "requirements.txt"), "r") as f:
    REQUIRED = [i for i in f.read().split("\n") if len(i)]

setup(
    name="property_scraper",
    packages=find_packages("property_scraper"),
    version="0.1.0",
    description="A class for scraping real estate and property website such as rightmove.co.uk",
    long_description=long_description,
    author="Emanuele Cannizzaro",
    author_email="toby.b.petty@gmail.com",
    url="https://github.com/emanuelecannizzaro/property_scraper.py",
    package_dir={"": "property_scraper"},
    py_modules=[splitext(basename(path))[0] for path in glob("property_scraper/*.py")],
    include_package_data=True,
    zip_safe=False,	
    install_requires=REQUIRED,
    python_requires='>=3.6',
    keywords=["webscraping", "rightmove", "data"],
    license="MIT",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
    setup_requires=["pytest-runner"],
    tests_require=[
        "pytest",
        "pytest-cov",
        "pytest-black",
        "pytest-flake8",
        "pytest-isort",
        "pytest-mypy",
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    entry_points={"console_scripts": ["crib = crib.cli:main"]},
    package_data={"property_scraper": ["docs/*", "docs/*/*"]}
)
