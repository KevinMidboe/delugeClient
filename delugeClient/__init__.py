import os
from sys import path

path.append(os.path.dirname(__file__))

__version__=0.1

import logging
from delugeUtils import BASE_DIR

logger = logging.getLogger('deluge_cli')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(os.path.join(BASE_DIR, 'deluge_cli.log'))
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s %(levelname)8s %(name)s | %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)