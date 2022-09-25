#!/usr/bin/env python3.6

import os
import re
import sys
import logging
import requests
import logging.config

from deluge_client import DelugeRPCClient
from sshtunnel import SSHTunnelForwarder
from utils import getConfig, BASE_DIR

from torrent import Torrent

logger = logging.getLogger('deluge_cli')

def split_words(string):
   logger.debug('Splitting input: {} (type: {}) with split_words'.format(string, type(string)))
   return re.findall(r"[\w\d']+", string.lower())

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

      self._connect()

   def freeSpace(self):
      return self.client.call('core.get_free_space')

   def parseResponse(self, response):
      torrents = []
      for key in response:
         torrent = response[key]
         torrents.append(Torrent.fromDeluge(torrent))
      return torrents

   def _connect(self):
      logger.info('Checking if script on same server as deluge RPC')
      if self.host != 'localhost' and self.host is not None:
         try:
            if self.password:
              self.tunnel = SSHTunnelForwarder(self.ssh_host, ssh_username=self.ssh_user, ssh_password=self.ssh_password, 
                 local_bind_address=('localhost', self.port), remote_bind_address=('localhost', self.port))
            elif self.pkey is not None:
              self.tunnel = SSHTunnelForwarder(self.ssh_host, ssh_username=self.ssh_user, ssh_pkey=self.ssh_pkey, 
                 local_bind_address=('localhost', self.port), remote_bind_address=('localhost', self.port))
         except ValueError as error:
            logger.error("Either password or private key path must be set in config.")
            raise error

         self.tunnel.start()

      self.client = DelugeRPCClient(self.host, self.port, self.user, self.password)
      self.client.connect()

   def add(self, url):
      logger.info('Adding magnet with url: {}.'.format(url))
      if (url.startswith('magnet')):
         return self.client.call('core.add_torrent_magnet', url, {})
      elif url.startswith('http'):
         magnet = self.getMagnetFromFile(url)
         return self.client.call('core.add_torrent_magnet', magnet, {})

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
      allTorrents = self.get_all()
      torrentNamesMatchingQuery = []
      if len(allTorrents):
         for torrent in allTorrents:
            if query in torrent.name:
               torrentNamesMatchingQuery.append(torrent)

         allTorrents = torrentNamesMatchingQuery

      return allTorrents

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
      return response

   def remove(self, name, destroy=False):
      matches = list(filter(lambda t: t.name == name, self.get_all()))
      logger.info('Matches for {}: {}'.format(name, matches))
      
      if (len(matches) > 1):
         raise ValueError('Multiple files found matching key. Unable to remove.')
      elif (len(matches) == 1):
         torrent = matches[0]
         response = self.client.call('core.remove_torrent', torrent.key, destroy)
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

   def getMagnetFromFile(self, url):
      logger.info('File url found, fetching magnet.')
      r = requests.get(url, allow_redirects=False)
      magnet = r.headers['Location']
      logger.info('Found magnet: {}.'.format(magnet))
      return magnet

