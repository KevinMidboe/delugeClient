#!/usr/bin/env python3.10

import os
import sys
import signal
import logging

import typer
from pprint import pprint

from deluge import Deluge
from utils import ColorizeFilter, BASE_DIR, validHash, convertFilesize
from __version__ import __version__
from __init__ import addHandler

ch = logging.StreamHandler()
ch.addFilter(ColorizeFilter())
addHandler(ch)
logger = logging.getLogger('deluge_cli')

app = typer.Typer()
deluge = None

def signal_handler(signal, frame):
  """
  Handle exit by Keyboardinterrupt
  """
  global deluge
  del deluge

  logger.info('\nGood bye!')
  sys.exit(1)

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
def add(magnet: str, json: bool = typer.Option(False, help="Print as json")):
  '''
  Add magnet torrent
  '''
  logger.info('Add command selected')
  logger.debug(magnet)
  response = deluge.add(magnet)
  if validHash(response):
    torrent = deluge.get(response)
    printResponse(torrent, json)
  else:
    logger.info('Unable to add torrent')

@app.command()
def ls(json: bool = typer.Option(False, help="Print as json")):
  '''
  List all torrents
  '''
  logger.info('List command selected')
  response = deluge.get_all()
  if response is None:
    logger.info('No torrents found')
    return

  printResponse(response, json)

@app.command()
def get(id: str, json: bool = typer.Option(False, help="Print as json")):
  '''
  Get torrent by id or hash
  '''
  logger.info('Get command selected for id: {}'.format(id))
  if not validHash(id):
    return logger.info("Id is not valid")
  response = deluge.get(id)
  printResponse(response, json)

@app.command()
def toggle(id: str):
  '''
  Toggle torrent download state
  '''
  logger.info('Toggle command selected for id: {}'.format(id))
  if not validHash(id):
    return logger.info("Id is not valid")
  deluge.toggle(id)
  torrent = deluge.get(id)
  printResponse(torrent)

@app.command()
def search(query: str, json: bool = typer.Option(False, help="Print as json")):
  '''
  Search for string segment in torrent name
  '''
  logger.info('Search command selected with query: {}'.format(query))
  response = deluge.search(query)
  printResponse(response, json)

@app.command()
def rm(name: str, destroy: bool = typer.Option(False, help="Remove torrent by name")):
  '''
  Remove torrent by name
  '''
  logger.info('Removing torrent with name: {}, destroy flag: {}'.format(name, destroy))
  response = deluge.removeByName(name, destroy)

@app.command()
def remove(id: str, destroy: bool = typer.Option(False, help="Remove torrent by id")):
  '''
  Remove torrent by id or hash
  '''
  logger.info('Removing torrent with id: {}, destroy flag: {}'.format(id, destroy))
  if not validHash(id):
    return logger.info("Id is not valid")
  response = deluge.remove(id, destroy)

@app.command()
def disk():
  '''
  Get free disk space
  '''
  response = deluge.freeSpace()
  if response == None or not isinstance(response, int):
    logger.error("Unable to get available disk space")
    return
  print(convertFilesize(response))

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

  # Initiate deluge
  global deluge
  deluge = Deluge()

def main():
  app()
  del deluge

if __name__ == '__main__':
  handleKeyboardInterrupt()
  main()
