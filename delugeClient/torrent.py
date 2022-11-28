import json
import logging
from distutils.util import strtobool

from delugeClient.utils import convert

logger = logging.getLogger('deluge_cli')

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

  def toJSON(self, files=False):
    torrentDict = {'key': self.key, 'name': self.name, 'progress': self.progress, 'eta': self.eta,
      'save_path': self.save_path, 'state': self.state, 'paused': self.paused,
      'finished': self.finished, 'files': self.files, 'is_folder': self.isFolder()}

    if (files is False):
      del torrentDict['files']

    return json.dumps(torrentDict)

  def __str__(self):
    return "{} Progress: {}% ETA: {} State: {} Paused: {}".format(
      self.name[:59].ljust(60), self.progress.rjust(5), self.eta.rjust(11), self.state.ljust(12), self.paused)
