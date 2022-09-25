#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages
from sys import path
from os.path import dirname

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

exec(open('delugeClient/__version__.py').read())

setup(
  name="delugeClient-kevin",
  version=__version__,
  packages=find_packages(),
  package_data={
    'delugeClient': ['default_config.ini'],
  },
  python_requires=">=3.6",
  author="KevinMidboe",
  description="Deluge client with custom functions written in python",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/kevinmidboe/delugeClient",
  install_requires=[
    'colored',
    'deluge-client',
    'docopt',
    'requests',
    'sshtunnel',
    'websockets'
  ],
  classifiers=[
    'Programming Language :: Python',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.6',
  ],
  entry_points={
    'console_scripts': [
      'delugeclient = delugeClient.__main__:main',
   ],
  }
)
