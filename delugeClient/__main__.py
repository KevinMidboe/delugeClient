#!/usr/bin/env python3.6


"""Custom delugeRPC client
Usage:
   deluge_cli add MAGNET [DIR] [--json | --debug | --warning | --error]
   deluge_cli search NAME [--json]
   deluge_cli get  TORRENT [--json | --debug | --warning | --error]
   deluge_cli ls [--downloading | --seeding | --paused | --json]
   deluge_cli toggle TORRENT
   deluge_cli progress [--json]
   deluge_cli rm NAME [--destroy] [--debug | --warning | --error]
   deluge_cli (-h | --help)
   deluge_cli --version

Arguments:
   MAGNET        Magnet link to add
   DIR           Directory to save to
   TORRENT       A selected torrent

Options:
   -h --help     Show this screen
   --version     Show version
   --print       Print response from commands
   --json        Print response as JSON
   --debug       Print all debug log
   --warning     Print only logged warnings
   --error       Print error messages (Error/Warning)
"""
import os
import sys
import signal
import logging

from docopt import docopt
from pprint import pprint

from deluge import Deluge
from utils import ColorizeFilter, BASE_DIR
from __version__ import __version__

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

logger.addFilter(ColorizeFilter())   

def signal_handler(signal, frame):
  """
  Handle exit by Keyboardinterrupt
  """
  logger.info('\nGood bye!')
  sys.exit(0)

def main():
  """
  Main function, parse the input
  """
  signal.signal(signal.SIGINT, signal_handler)

  arguments = docopt(__doc__, version=__version__)

  # Set logging level for streamHandler
  if arguments['--debug']:
    ch.setLevel(logging.DEBUG)
  elif arguments['--warning']:
    ch.setLevel(logging.WARNING)
  elif arguments['--error']:
    ch.setLevel(logging.ERROR)

  logger.info('Deluge client')
  logger.debug(arguments)

  # Get config settings
  deluge = Deluge()

  _id = arguments['TORRENT']
  query = arguments['NAME']
  magnet = arguments['MAGNET']
  name = arguments['NAME']
  _filter = [ a[2:] for a in ['--downloading', '--seeding', '--paused'] if arguments[a] ]

  response = None

  if arguments['add']:
    logger.info('Add cmd selected with link {}'.format(magnet))
    response = deluge.add(magnet)

    if response is not None:
      logger.info('Successfully added torrent.\nResponse from deluge: {}'.format(response))
    else:
      logger.warning('Add response returned empty: {}'.format(response))

  elif arguments['search']:
    logger.info('Search cmd selected for query: {}'.format(query))
    response = deluge.search(query)
    if response is not None or response != '[]':
      logger.info('Search found {} torrents'.format(len(response)))
    else:
      logger.info('Empty response for search query.')

  elif arguments['progress']:
    logger.info('Progress cmd selected.')
    response = deluge.progress()

  elif arguments['get']:
    logger.info('Get cmd selected for id: {}'.format(_id))
    response = deluge.get(_id)

  elif arguments['ls']:
    logger.info('List cmd selected')
    response = deluge.get_all(_filter=_filter)

  elif arguments['toggle']:
    logger.info('Toggling id: {}'.format(_id))
    deluge.togglePaused(_id)

  elif arguments['rm']:
    destroy = arguments['--destroy']
    logger.info('Remove by name: {}.'.format(name))

    if destroy:
      logger.info('Destroy set, removing files')
      deluge.remove(name, destroy)

  try:
    if arguments['--json']:
      if len(response) > 1:
        print('[{}]'.format(','.join([t.toJSON() for t in response])))
      else:
        print(response[0].toJSON())
  except KeyError as error:
    logger.error('Unexpected error while trying to print')
    raise error

  return response

if __name__ == '__main__':
  main()