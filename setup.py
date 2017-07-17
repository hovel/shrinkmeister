# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='shrinkmeister',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    license='',
    description='',
    long_description='',
    url='https://github.com/hovel/shrinkmeister',
    author='',
    author_email='',
)
