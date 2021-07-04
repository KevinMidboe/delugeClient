from sys import path
from os.path import dirname

path.append(dirname(__file__))

__version__=0.1

import logging
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