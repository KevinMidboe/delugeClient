import setuptools
import delugeClient

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

setuptools.setup(
  name="delugeClient",
  version=delugeClient.__version__,
  author="KevinMidboe",
  description="Deluge client with custom functions written in python",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/kevinmidboe/delugeClient",
  install_requires=[
    'asn1crypto==0.24.0',
    'bcrypt==3.1.4',
    'colored==1.3.5',
    'cryptography==2.5',
    'deluge-client==1.6.0',
    'docopt==0.6.2',
    'idna==2.7',
    'pyasn1==0.4.4',
    'pycparser==2.18',
    'PyNaCl==1.2.1',
    'six==1.11.0',
    'sshtunnel==0.1.4',
    'websockets==6.0'
  ],
  classifiers=[
    'Programming Language :: Python',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.6',
  ],
  entry_points={
    'console_scripts': [
      'delugeClient = delugeClient.__main__:main',
   ],
  },
  package_dir={"": "delugeClient"},
  packages=setuptools.find_packages(where="delugeClient"),
  python_requires=">=3.6",
)