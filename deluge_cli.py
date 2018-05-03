#!/usr/bin/env python3.6


"""Custom delugeRPC client
Usage:
   deluge_cli add MAGNET [DIR] [--debug | --warning | --error]
   deluge_cli get TORRENT
   deluge_cli ls [--downloading | --seeding | --paused]
   deluge_cli toggle TORRENT
   deluge_cli rm TORRENT [--debug | --warning | --error]
   deluge_cli (-h | --help)
   deluge_cli --version

Arguments:
   MAGNET        Magnet link to add
   DIR           Directory to save to
   TORRENT       A selected torrent

Options:
   -h --help     Show this screen
   --version     Show version
   --debug       Print all debug log
   --warning     Print only logged warnings
   --error       Print error messages (Error/Warning)
"""

import argparse
import os
import signal
import logging
import logging.config
import configparser

from deluge_client import DelugeRPCClient
from docopt import docopt
from utils import ColorizeFilter, convert

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger('deluge_cli')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('deluge_cli.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s %(levelname)8s %(name)s | %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

logger.addFilter(ColorizeFilter())   


class Deluge(object):
   """docstring for ClassName"""
   def __init__(self, config=None):
      self.host = config['Deluge']['HOST']
      self.port = int(config['Deluge']['PORT'])
      self.user = config['Deluge']['USER']
      self.password = config['Deluge']['PASSWORD']
      self._connect()

   def parseResponse(self, response):
      torrents = []
      for key in response:
         torrent = response[key]
         torrents.append(Torrent.fromDeluge(torrent))
      return torrents

   def _connect(self):
      print(self.host, self.port, self.user, self.password)
      self.client = DelugeRPCClient(self.host, self.port, self.user, self.password)
      self.client.connect()

   def get(self, id):
      response = self.client.call('core.get_torrent_status', id, {})
      print(response)
      return Torrent.fromDeluge(response) 
      # return self.parseResponse(response)

   def ls(self, _filter=None):
      if ('seeding' in _filter):
         response = self.client.call('core.get_torrents_status', {'state': 'Seeding'}, [])
      elif ('downloading' in _filter):
         response = self.client.call('core.get_torrents_status', {'state': 'Downloading'}, [])
      elif ('paused' in _filter):
         response = self.client.call('core.get_torrents_status', {'paused': 'true'}, [])
      else:
         response = self.client.call('core.get_torrents_status', {}, [])

      return self.parseResponse(response)

   def delete(self, id):
      response = self.client.call('core.remove_torrent', id, False)
      print('Response: ', response)

   def toggle(self, id):
      torrent = self.ls(id)[0]
      if (torrent.paused):
         response = self.client.call('core.resume_torrent', [id])
      else:
         response = self.client.call('core.pause_torrent', [id])
      
      print('Response:', response)

   def status(self):
      response = self.client.call('core.get_torrents_status', {}, ['progress'])
      torrents = self.parseResponse(response)

class Torrent(object):
   def __init__(self, key, name, progress, eta, save_path, state, paused, finished, files):
      super(Torrent, self).__init__()
      self.key = key
      self.name = name
      self.progress = "{0:.2f}".format(float(progress))
      self.eta = eta
      self.save_path = save_path
      self.state = state
      self.paused = paused
      self.finished = finished
      self.files = list(files)

   def unpacked(self):
      return len(self.files) > 1

   @classmethod
   def fromDeluge(cls, d):
      d = convert(d)
      from pprint import pprint
      pprint(d)
      return cls(d['hash'], d['name'], d['progress'], d['eta'], d['save_path'], d['state'], 
                 d['paused'], d['is_finished'], d['files'])

   def toJSON(self):
      return {'Key': self.key, 'Name': self.name, 'Progress': self.progress, 'ETA': self.eta,
              'Save path': self.save_path, 'State': self.state, 'Paused': self.paused,
              'Finished': self.finished, 'Files': self.files, 'unpacked': self.unpacked()}

   def __str__(self):
      return "Name: {}, Progress: {}%, ETA: {}, State: {}, Paused: {}".format(
         self.name, self.progress, self.eta, self.state, self.paused)

def getConfig():
   """
   Read path and get configuartion file with site settings
   :return: config settings read from 'config.ini'
   :rtype: configparser.ConfigParser
   """
   config = configparser.ConfigParser()
   config_dir = os.path.join(BASE_DIR, 'config.ini')
   config.read(config_dir)

   config_values = list(dict(config.items('Deluge')).values())
   if any(value.startswith('YOUR') for value in config_values):
      raise ValueError('Please set variables in config.ini file.')

   return config

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

   arguments = docopt(__doc__, version='1')

   if arguments['--debug']:
      # logger.level = logging.DEBUG
      ch.setLevel(logging.DEBUG)
   elif arguments['--warning']:
      # logger.level = logging.WARNING
      ch.setLevel(logging.WARNING)
   elif arguments['--error']:
      # logger.level = logging.ERROR
      ch.setLevel(logging.ERROR)

   logger.info('Deluge client')
   logger.debug(arguments)

   # Fetch config
   config_settings = getConfig()
   deluge = Deluge(config=config_settings)

   # arg_text, arg_user, arg_msg = arguments['<text>'], arguments['<user>'], arguments['<msg>']
   _id = arguments['TORRENT']
   _filter = [ a[2:] for a in ['--downloading', '--seeding', '--paused'] if arguments[a] ]
   print(_id, _filter)

   if arguments['add'] and arg_text:
      logger.info('Add cmd selected')
   elif arguments['get']:
      logger.info('Get cmd selected for id: ', _id)
      response = deluge.get(_id)
      pprint(response.toJSON())
   elif arguments['ls']:
      logger.info('List cmd selected')
      from pprint import pprint
      [ pprint(t.toJSON()) for t in deluge.ls(_filter=_filter) ]
   elif arguments['toggle']:
      logger.info('Toggling id: {}'.format(_id))
      deluge.toggle(_id)
   elif arguments['rm']:
      logger.info('Deleting id: {}'.format(_id))
      deluge.delete(_id)

if __name__ == '__main__':
   main()

