from setuptools import setup, find_packages

import delugeClient

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

setup(
  name="delugeClient-kevin",
  version=delugeClient.__version__,
  author="KevinMidboe",
  description="Deluge client with custom functions written in python",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/kevinmidboe/delugeClient",
  install_requires=[
    'colored==1.4.2',
    'deluge-client==1.9.0',
    'docopt==0.6.2',
    'requests==2.25.1',
    'sshtunnel==0.4.0',
    'websockets==9.1'
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
  },
  packages=find_packages(),
  package_data={
    'delugeClient': ['default_config.ini'],
  },
  python_requires=">=3.6",
)
