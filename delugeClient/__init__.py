#!/usr/bin/env python3.10
# -*- encoding: utf-8 -*-

from sys import path
from os.path import dirname, join, abspath

SCRIPT_DIR = dirname(abspath(__file__))
path.append(dirname(SCRIPT_DIR))

import logging
from delugeClient.utils import BASE_DIR
from delugeClient.deluge import Deluge

def addHandler(handler):
  handler.setFormatter(formatter)
  logger.addHandler(handler)

logger = logging.getLogger('deluge_cli')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(join(BASE_DIR, 'deluge_cli.log'))
formatter = logging.Formatter('%(asctime)s| %(levelname)s | %(message)s')

addHandler(fh)
