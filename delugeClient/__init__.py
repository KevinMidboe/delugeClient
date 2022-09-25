#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-

from sys import path
from os.path import dirname, join

path.append(dirname(__file__))

import logging
from utils import BASE_DIR, ColorizeFilter

logger = logging.getLogger('deluge_cli')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(join(BASE_DIR, 'deluge_cli.log'))
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s %(levelname)8s %(name)s | %(message)s')
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)
logger.addFilter(ColorizeFilter())