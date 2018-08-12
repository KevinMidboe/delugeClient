#!/usr/bin/env python3.6


"""Custom delugeRPC client
Usage:
   deluge_cli add MAGNET [DIR] [--debug | --warning | --error]
   deluge_cli search NAME
   deluge_cli get  TORRENT
   deluge_cli ls [--downloading | --seeding | --paused]
   deluge_cli toggle TORRENT
   deluge_cli progress
   deluge_cli rm NAME [--debug | --warning | --error]
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
import sys
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

fh = logging.FileHandler(os.path.join(BASE_DIR, 'deluge_cli.log'))
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s %(levelname)8s %(name)s | %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

logger.addFilter(ColorizeFilter())   


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

def split_words(string):
   logger.debug('Splitting input: {} (type: {}) with split_words'.format(string, type(string)))
   return re.findall(r"[\w\d']+", string.lower())

class Deluge(object):
   """docstring for ClassName"""
   def __init__(self):
      config = getConfig()
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

   def remove(self, name):
      matches = list(filter(lambda t: t.name == name, self.get_all()))
      logger.info('Matches for {}: {}'.format(name, matches))
      
      if (len(matches) > 1):
         raise ValueError('Multiple files found matching key. Unable to remove.')
      elif (len(matches) == 1):
         torrent = matches[0]
         response = self.client.call('core.remove_torrent', torrent.key, False)
         logger.info('Response: {}'.format(str(response)))

         if (response == False):
            raise AttributeError('Unable to remove torrent.')
         return response
      else:
         logger.error('ERROR. No torrent found with that name.')

   def filterOnValue(self, torrents, value):
      filteredTorrents = []
      for t in torrents:
         value_template = {'key': None, 'name': None, value: None}
         value_template['key'] = t.key
         value_template['name'] = t.name
         value_template[value] = getattr(t, value)
         
         filteredTorrents.append(value_template)
      return filteredTorrents

   def progress(self):
      attributes = ['progress', 'eta', 'state', 'finished']
      all_torrents = self.get_all()

      torrents = []
      for i, attribute in enumerate(attributes):
         if i < 1:
            torrents = self.filterOnValue(all_torrents, attribute)
            continue
         torrents = [dict(e, **v) for e,v in zip(torrents, self.filterOnValue(all_torrents, attribute))]

      return torrents

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

   def isFolder(self):
      return len(self.files) > 1

   def toBool(self, value):
      return True if strtobool(value) else False

   @classmethod
   def fromDeluge(cls, d):
      # Receive a dict with byte values, convert all elements to string values
      d = convert(d)
      toBool = lambda val: True if strtobool(val) else False
      return cls(d['hash'], d['name'], d['progress'], d['eta'], d['save_path'], d['state'], 
                 toBool(d['paused']), toBool(d['is_finished']), d['files'])

   def toJSON(self):
      return {'key': self.key, 'name': self.name, 'progress': self.progress, 'eta': self.eta,
              'save_path': self.save_path, 'state': self.state, 'paused': self.paused,
              'finished': self.finished, 'files': self.files, 'is_folder': self.isFolder()}

   def __str__(self):
      return "Name: {}, Progress: {}%, ETA: {}, State: {}, Paused: {}".format(
         self.name, self.progress, self.eta, self.state, self.paused)

def signal_handler(signal, frame):
   """
   Handle exit by Keyboardinterrupt
   """
   logger.info('\nGood bye!')
   sys.exit(0)

def main(arg):
   """
   Main function, parse the input
   """
   signal.signal(signal.SIGINT, signal_handler)

   arguments = docopt(__doc__, argv=arg, version='1')

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
   print(_id, query, _filter)

   if arguments['add']:
      logger.info('Add cmd selected with link {}'.format(magnet))
      response = deluge.add(magnet)
      print('Add response: ', response)

   elif arguments['search']:
      logger.info('Search cmd selected for query: {}'.format(query))
      response = deluge.search(query)
      [ pprint(t.toJSON()) for t in response ]

   elif arguments['progress']:
      logger.info('Progress cmd selected.')
      pprint(deluge.progress())
      exit(0)
      [ pprint(t.toJSON()) for t in deluge.progress() ]

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
      logger.info('Remove by name: {}'.format(name))
      deluge.remove(name)

if __name__ == '__main__':
   main()

