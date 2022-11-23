#!/usr/bin/env python3.10

import os
import re
import sys
import logging
import requests
import logging.config

from deluge_client import DelugeRPCClient, FailedToReconnectException
from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError
from utils import getConfig, BASE_DIR

from torrent import Torrent

logger = logging.getLogger('deluge_cli')

def split_words(string):
   logger.debug('Splitting input: {} (type: {}) with split_words'.format(string, type(string)))
   return re.findall(r"[\w\d']+", string.lower())

def responseToString(response=None):
   try:
      response = response.decode('utf-8')
   except (UnicodeDecodeError, AttributeError):
      pass

   return response

class Deluge(object):
   """docstring for ClassName"""
   def __init__(self):
      config = getConfig()
      self.host = config['deluge']['host']
      self.port = int(config['deluge']['port'])
      self.user = config['deluge']['user']
      self.password = config['deluge']['password']

      self.ssh_host = config['ssh']['host']
      self.ssh_user = config['ssh']['user']
      self.ssh_pkey = config['ssh']['pkey']
      self.ssh_password = config['ssh']['password']

      try:
         self._connect()
      except FailedToReconnectException:
         logger.error("Unable to connect to deluge, make sure it's running")
         sys.exit(1)
      except ConnectionRefusedError:
         logger.error("Unable to connect to deluge, make sure it's running")
         sys.exit(1)
      except BaseException as error:
         logger.error("Unable to connect to deluge, make sure it's running")
         if 'nodename nor servname provided' in str(error):
            sys.exit(1)
         raise error

   def freeSpace(self):
      return self.client.call('core.get_free_space')

   def parseResponse(self, response):
      torrents = []
      for key in response:
         torrent = response[key]
         torrents.append(Torrent.fromDeluge(torrent))
      return torrents

   def establishSSHTunnel(self):
      logger.debug('Checking if script on same server as deluge RPC')

      if self.password is not None:
        self.tunnel = SSHTunnelForwarder(self.ssh_host, ssh_username=self.ssh_user, ssh_password=self.ssh_password, 
           local_bind_address=('localhost', self.port), remote_bind_address=('localhost', self.port))
      elif self.pkey is not None:
        self.tunnel = SSHTunnelForwarder(self.ssh_host, ssh_username=self.ssh_user, ssh_pkey=self.ssh_pkey, 
           local_bind_address=('localhost', self.port), remote_bind_address=('localhost', self.port))
      else:
         logger.error("Either password or private key path must be set in config.")
         return

      try:
         self.tunnel.start()
      except BaseSSHTunnelForwarderError as sshError:
         logger.warning("SSH host {} online, check your connection".format(self.ssh_host))
         return

   def _call(self, command, *args):
      try:
         return self.client.call(command, *args)
      except ConnectionRefusedError as error:
         logger.error("Unable to run command, connection to deluge seems to be offline")
      except FailedToReconnectException as error:
         logger.error("Unable to run command, reconnection to deluge failed")

   def _connect(self):
      if self.host != 'localhost' and self.host is not None:
         self.establishSSHTunnel()

      self.client = DelugeRPCClient(self.host, self.port, self.user, self.password)
      self.client.connect()

   def add(self, url):
      response = None
      if (url.startswith('magnet')):
         response = self._call('core.add_torrent_magnet', url, {})
      elif url.startswith('http'):
         magnet = self.getMagnetFromFile(url)
         response = self._call('core.add_torrent_magnet', magnet, {})

      return responseToString(response)

   def get_all(self, _filter=None):
      response = None
      if (type(_filter) is list and len(_filter)):
         if ('seeding' in _filter):
            response = self._call('core.get_torrents_status', {'state': 'Seeding'}, [])
         elif ('downloading' in _filter):
            response = self._call('core.get_torrents_status', {'state': 'Downloading'}, [])
         elif ('paused' in _filter):
            response = self._call('core.get_torrents_status', {'paused': 'true'}, [])
      else:
         response = self.client.call('core.get_torrents_status', {}, [])

      if response == {}:
         return None

      return self.parseResponse(response)


   def search(self, query):
      allTorrents = self.get_all()
      torrentNamesMatchingQuery = []
      if len(allTorrents):
         for torrent in allTorrents:
            if query in torrent.name.lower():
               torrentNamesMatchingQuery.append(torrent)

         allTorrents = torrentNamesMatchingQuery

      return allTorrents

      q_list = split_words(query)
      return [ t for t in self.get_all() if (set(q_list) <= set(split_words(t.name))) ]

   def get(self, id):
      response = self._call('core.get_torrent_status', id, {})
      if response == {}:
         logger.warning('No torrent with id: {}'.format(id))
         return None

      return Torrent.fromDeluge(response)

   def toggle(self, id):
      torrent = self.get(id)
      if torrent is None:
         return

      if (torrent.paused):
         response = self._call('core.resume_torrent', [id])
      else:
         response = self._call('core.pause_torrent', [id])

      return responseToString(response)

   def removeByName(self, name, destroy=False):
      matches = list(filter(lambda t: t.name == name, self.get_all()))
      logger.info('Matches for {}: {}'.format(name, matches))
      
      if len(matches) > 1:
         raise ValueError('Multiple files found matching key. Unable to remove.')
      elif len(matches) == 1:
         torrent = matches[0]
         response = self.remove(torrent.key, destroy)
         logger.debug('Response rm: {}'.format(str(response)))

         if response == False:
            raise AttributeError('Unable to remove torrent.')
         return responseToString(response)
      else:
         logger.error('ERROR. No torrent found with that name.')

   def remove(self, id, destroy=False):
      try:
         response = self.client.call('core.remove_torrent', id, destroy)
         logger.debug('Response from remove: {}'.format(str(response)))
         return responseToString(response)
      except BaseException as error:
         if 'torrent_id not in session' in str(error):
            logger.info('Unable to remove. No torrent with matching id')
            return None

         raise error

   def filterOnValue(self, torrents, value):
      filteredTorrents = []
      for t in torrents:
         value_template = {'key': None, 'name': None, value: None}
         value_template['key'] = t.key
         value_template['name'] = t.name
         value_template[value] = getattr(t, value)
         
         filteredTorrents.append(value_template)
      return filteredTorrents

   def __del__(self):
      if hasattr(self, 'client') and self.client.connected:
         logger.debug('Disconnected deluge rpc')
         self.client.disconnect()

      if hasattr(self, 'tunnel') and self.tunnel.is_active:
         logger.debug('Closing ssh tunnel')
         self.tunnel.stop(True)

   def getMagnetFromFile(self, url):
      logger.info('File url found, fetching magnet.')
      r = requests.get(url, allow_redirects=False)
      magnet = r.headers['Location']
      logger.info('Found magnet: {}.'.format(magnet))
      return magnet

