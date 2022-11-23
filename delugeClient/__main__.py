#!/usr/bin/env python3.10

import os
import sys
import signal
import logging

import typer
from pprint import pprint

from deluge import Deluge
from utils import ColorizeFilter, BASE_DIR
from __version__ import __version__
from __init__ import addHandler

ch = logging.StreamHandler()
ch.addFilter(ColorizeFilter())
addHandler(ch)
logger = logging.getLogger('deluge_cli')

app = typer.Typer()
deluge = Deluge()

def signal_handler(signal, frame):
  """
  Handle exit by Keyboardinterrupt
  """
  del deluge

  logger.info('\nGood bye!')
  sys.exit(0)

def handleKeyboardInterrupt():
  signal.signal(signal.SIGINT, signal_handler)

def printResponse(response, json=False):
  try:
    if json:
      if isinstance(response, list):
        print('[{}]'.format(','.join([t.toJSON() for t in response])))
      else:
        print(response.toJSON())

    elif isinstance(response, list):
      for el in response:
        print(el)

    elif response:
      print(response)

  except KeyError as error:
    logger.error('Unexpected error while trying to print')
    raise error

@app.command()
def add(magnet: str):
  '''
  Add magnet torrent
  '''
  logger.debug('Add command selected')
  logger.debug(magnet)
  response = deluge.add(magnet)
  printResponse(response)

@app.command()
def ls(json: bool = typer.Option(False, help="Print as json")):
  '''
  List all torrents
  '''
  logger.debug('List command selected')
  response = deluge.get_all()
  printResponse(response, json)

@app.command()
def get(id: str, json: bool = typer.Option(False, help="Print as json")):
  '''
  Get torrent by id or hash
  '''
  logger.debug('Get command selected for id {}'.format(id))
  response = deluge.get(id)
  printResponse(response, json)

@app.command()
def toggle(id: str):
  '''
  Toggle torrent download state
  '''
  logger.debug('Toggle command selected for id {}'.format(id))
  response = deluge.toggle(id)
  printResponse(response)

@app.command()
def search(query: str, json: bool = typer.Option(False, help="Print as json")):
  '''
  Search for string segment in torrent name
  '''
  logger.debug('Search command selected with query: {}'.format(query))
  response = deluge.search(query)
  printResponse(response, json)

@app.command()
def remove(id: str, destroy: bool = typer.Option(False, help="Remove torrent data")):
  '''
  Remove torrent by id or hash
  '''
  logger.debug('Remove command selected for id: {} with destroy: {}'.format(id, destroy))
  response = deluge.remove(id, destroy)
  printResponse(response)

@app.command()
def version():
  '''
  Print package version
  '''
  print(__version__)

# Runs before any command
@app.callback()
def defaultOptions(debug: bool = typer.Option(False, '--debug', help='Set log level to debug'), info: bool = typer.Option(False, '--info', help='Set log level to info'), warning: bool = typer.Option(False, '--warning', help='Set log level to warning'), error: bool = typer.Option(False, '--error', help='Set log level to error')):
  ch.setLevel(logging.INFO)

  if '--json' in sys.argv:
    ch.setLevel(logging.CRITICAL)
  elif error == True:
    ch.setLevel(logging.ERROR)
  elif warning == True:
    ch.setLevel(logging.WARNING)
  elif info == True:
    ch.setLevel(logging.INFO)
  elif debug == True:
    ch.setLevel(logging.DEBUG)

def main():
  app()
  del deluge

if __name__ == '__main__':
  handleKeyboardInterrupt()
  main()
