#!/usr/bin/env python3.6


"""Custom delugeRPC client
Usage:
   deluge_cli add MAGNET [DIR] [--debug | --warning | --error]
   deluge_cli search NAME
   deluge_cli get  TORRENT
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
import re
import signal
import socket
import logging
import logging.config
import configparser

from distutils.util import strtobool
from pprint import pprint

from deluge_client import DelugeRPCClient
from sshtunnel import SSHTunnelForwarder
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

def split_words(string):
   logger.debug('Splitting input: {} (type: {}) with split_words'.format(string, type(string)))
   return re.findall(r"[\w\d']+", string.lower())

class Deluge(object):
   """docstring for ClassName"""
   def __init__(self, config=None):
      self.host = config['Deluge']['HOST']
      self.port = int(config['Deluge']['PORT'])
      self.user = config['Deluge']['USER']
      self.password = config['Deluge']['PASSWORD']

      self.ssh_host = config['ssh']['HOST']
      self.ssh_user = config['ssh']['USER']
      self.ssh_pkey = config['ssh']['PKEY']
   
      self._connect()

   def parseResponse(self, response):
      torrents = []
      for key in response:
         torrent = response[key]
         torrents.append(Torrent.fromDeluge(torrent))
      return torrents

   def _connect(self):
      logger.info('Checking if script on same server as deluge RPC')
      if (socket.gethostbyname(socket.gethostname()) != self.host):
         self.tunnel = SSHTunnelForwarder(self.ssh_host, ssh_username=self.ssh_user, ssh_pkey=self.ssh_pkey, 
            local_bind_address=('localhost', self.port), remote_bind_address=('localhost', self.port))
         self.tunnel.start()

      self.client = DelugeRPCClient(self.host, self.port, self.user, self.password)
      self.client.connect()

   def add(self, url):
      if (url.startswith('magnet')):
         return self.client.call('core.add_torrent_magnet', url, {})

   def get_all(self, _filter=None):
      if (type(_filter) is list and len(_filter)):
         if ('seeding' in _filter):
            response = self.client.call('core.get_torrents_status', {'state': 'Seeding'}, [])
         elif ('downloading' in _filter):
            response = self.client.call('core.get_torrents_status', {'state': 'Downloading'}, [])
         elif ('paused' in _filter):
            response = self.client.call('core.get_torrents_status', {'paused': 'true'}, [])
      else:
         response = self.client.call('core.get_torrents_status', {}, [])

      return self.parseResponse(response)

   def search(self, query):
      q_list = split_words(query)
      return [ t for t in self.get_all() if (set(q_list) <= set(split_words(t.name))) ]

   def get(self, id):
      response = self.client.call('core.get_torrent_status', id, {})
      return Torrent.fromDeluge(response)

   def togglePaused(self, id):
      torrent = self.get(id)
      if (torrent.paused):
         response = self.client.call('core.resume_torrent', [id])
      else:
         response = self.client.call('core.pause_torrent', [id])
      
      print('Response:', response)

   def remove(self, torrent_id):
      for torrent in self.get_all():
         if (torrent_id == torrent.key):
            response = self.client.call('core.remove_torrent', torrent.key, False)
            logger.info('Response: {}'.format(str(response)))
            
            if (response == False):
               raise AttributeError('Unable to remove torrent.')
            return response

      logger.error('ERROR: No torrent found with that id.')

   def status(self):
      response = self.client.call('core.get_torrents_status', {}, ['progress'])
      torrents = self.parseResponse(response)

   def __del__(self):
      if hasattr(self, 'tunnel'):
         logger.info('Closing ssh tunnel')
         self.tunnel.stop()

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

   def packed(self):
      return len(self.files) > 1

   @classmethod
   def fromDeluge(cls, d):
      # Receive a dict with byte values, convert all elements to string values
      d = convert(d)
      d['paused'] = True if strtobool(d['paused']) else False
      return cls(d['hash'], d['name'], d['progress'], d['eta'], d['save_path'], d['state'], 
                 d['paused'], d['is_finished'], d['files'])

   def toJSON(self):
      return {'Key': self.key, 'Name': self.name, 'Progress': self.progress, 'ETA': self.eta,
              'Save path': self.save_path, 'State': self.state, 'Paused': self.paused,
              'Finished': self.finished, 'Files': self.files, 'Packed': self.packed()}

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
   config_values.extend(list(dict(config.items('ssh')).values()))

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
   config_settings = getConfig()
   deluge = Deluge(config=config_settings)

   _id = arguments['TORRENT']
   query = arguments['NAME']
   magnet = arguments['MAGNET']
   _filter = [ a[2:] for a in ['--downloading', '--seeding', '--paused'] if arguments[a] ]
   print(_id, query, _filter)

   if arguments['add']:
      logger.info('Add cmd selected with link {}'.format(magnet))
      response = deluge.add(magnet)
      print('Add response: ', response)

   elif arguments['search']:
      logger.info('Search cmd selected for query: {}'.format(query))
      response = deluge.search(query)
      [ pprint(t.toJSON()) for t in response ]

   elif arguments['get']:
      logger.info('Get cmd selected for id: {}'.format(_id))
      response = deluge.get(_id)
      pprint(response.toJSON())

   elif arguments['ls']:
      logger.info('List cmd selected')
      [ pprint(t.toJSON()) for t in deluge.get_all(_filter=_filter) ]

   elif arguments['toggle']:
      logger.info('Toggling id: {}'.format(_id))
      deluge.togglePaused(_id)

   elif arguments['rm']:
      logger.info('Remove id: {}'.format(_id))
      deluge.remove(_id)

if __name__ == '__main__':
   main()

