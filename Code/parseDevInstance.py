from xml.etree import *

class DevInstance:

  def __init__(self, target, initSilence=0):
    self.initSilence = initSilence
    self.target = target
    self.beats = []
    self.notes = []
    pass


  


def parse(file):
  tree = ElementTree.parse(file)

