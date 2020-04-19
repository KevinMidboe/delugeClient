#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: kevinmidboe
# @Date:   2018-04-17 19:55:38
# @Last Modified by:   KevinMidboe
# @Last Modified time: 2018-05-04 00:04:25

import logging
import colored
import json
from pprint import pprint

from colored import stylize

__all__ = ('ColorizeFilter', )

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
   
   logger = logging.getLogger('deluge_cli')

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
