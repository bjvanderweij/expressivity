from representation import *
from music21 import *

class Alignment:
    
  def __init__(self, performance, devinstance, score):
    # devinstance is a path to a deviationinstance file (or a representation?)
    # performance is a pianoroll of a performance
    # score is a music21 score object

# Inherit from note.Note? Nah
class PerformanceNote:

  def __init__(self, scoreNote):
    self.scoreNote = scoreNote
