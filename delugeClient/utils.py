#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: kevinmidboe
# @Date:   2018-04-17 19:55:38
# @Last Modified by:   KevinMidboe
# @Last Modified time: 2018-05-04 00:04:25

import os
import sys
import json
import shutil
import logging
import colored
import configparser
from pprint import pprint

from colored import stylize

__all__ = ('ColorizeFilter', )

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger('deluge_cli')

def checkConfigExists():
  user_config_dir = os.path.expanduser("~") + "/.config/delugeClient"
  config_dir = os.path.join(user_config_dir, 'config.ini')


def getConfig():
  """
  Read path and get configuartion file with site settings
  :return: config settings read from 'config.ini'
  :rtype: configparser.ConfigParser
  """
  config = configparser.ConfigParser()
  user_config_dir = os.path.expanduser("~") + "/.config/delugeClient"

  config_dir = os.path.join(user_config_dir, 'config.ini')
  if not os.path.isfile(config_dir):
    defaultConfig = os.path.join(BASE_DIR, 'default_config.ini')
    logger.error('Missing config! Moved default.config.ini to {}.\nOpen this file and set all varaibles!'.format(config_dir))
    os.makedirs(user_config_dir, exist_ok=True)
    shutil.copyfile(defaultConfig, config_dir)

  config.read(config_dir)

  requiredParameters = [('deluge host', config['deluge']['host']), ('deluge port', config['deluge']['port']),
    ('deluge user', config['deluge']['user']), ('deluge password', config['deluge']['password']),
    ('ssh password', config['ssh']['user'])]
  for key, value in requiredParameters:
    if value == '':
      logger.error('Missing value for variable: "{}" in config: \
"{}.'.format(key, user_config_dir))
      exit(1)

  return config

class ColorizeFilter(logging.Filter):
  """
  Class for setting specific colors to levels of severity for log output
  """
  color_by_level = {
    10: 'chartreuse_3b',
    20: 'white',
    30: 'orange_1',
    40: 'red'
  }
   
  def filter(self, record):
    record.raw_msg = record.msg
    color = self.color_by_level.get(record.levelno)
    if color:
      record.msg = stylize(record.msg, colored.fg(color))
    return True

def convert(data):
  if isinstance(data, bytes):  return data.decode('utf-8')
  if isinstance(data, dict):   return dict(map(convert, data.items()))
  if isinstance(data, tuple):  return map(convert, data)
  json_data = json.dumps(data)
  return json_data
