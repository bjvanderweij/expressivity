#!/usr/bin/env python

import music21 as m21
from representation import *
from deviations import *
from midifile import *
from score import *
from alignment import *
import os, re, util, analysescore

DB_PATH = "/home/bastiaan/UvA/Expressive-Performance_DATA/CrestMusePEDB/"
VERSIONS = ['PEDBv2.2', 'PEDBv2.3', 'PEDBv2.4.1', 'PEDBv2.5', 'PEDBv3.0']

composers = {'Bach':'bac', 'Bartok':'bar', 'Grieg':'gri', 'Mozart':'moz', \
    'Beethoven':'bee', 'Chopin':'cho', 'Schumann':'sch', 'Mussorgsky':'mus',\
    'Ravel':'rav', 'Prokofieff':'pro', 'Satie':'sat', 'Skrjabin':'scr'}

soundfonts = {'Bosendorfer PIANO / GIGA':'b', 'GPO-Concert-Steinway-ver2.sf2':'g', 'YAMAHA MOTIF-XF':'y'}

#pianists = {'Andras Schiff':'schiff', 'Sviatoslav Richter':'Richter', 'Glenn Gould':'Gould',\
#    'Friedrich Gulda':'Gulda', 'Hiroko Nakamura':'Nakamura', 'Norio Shimizu':'Shimizu',\
#    'Vladimir Ashkenazy':'Ashkenazy', 'Alfred Brendel':'Brendel', 'Martha Argerich':'Argerich',\
#    'Christoph Eschenbach':'Eschenbach', 'Ingrid Haebler':'Haebler', 'Lili Kraus':'Kraus', 'Maurizio Pollini':'Pollini',\
#    'Vladimir S. Horowitz':'Horowitz', 'Maria J. Pires':'Pires', 'Tamas Vasary':'Vasary',\
#    'Alfred D. Cortot':'Cortot', 'Alicia De Larrocha':'Larrocha', 'Ivo Pogorelich':'Pogorelich',\
#    'Claudio Arrau':'Arrau', 'Rafal Brechacz':'Brechacz', 'Jorge Bolet':'Bolet', 'Stanislav Bunin':'Bunin',\
#    'Halina Czerny-Stefanska':'Stefanska', 'Dang Thai Son':'Son', 'Samson Francois':'Francois', 'Eva Poblocka':'Poblocka'}

# Wrappers
def getScoreMidiPath1(t):  return getScoreMidiPath(t[0], t[1], t[2], t[3])
def getPerformancePath1(t):  return getPerformancePath(t[0], t[1], t[2], t[3])
def getScorePath1(t):  return getScorePath(t[0], t[1], t[2], t[3])
def getDeviationPath1(t):  return getDeviationPath(t[0], t[1], t[2], t[3])
def getPerformance1(t):  return getPerformance(t[0], t[1], t[2], t[3])
def getScore1(t):  return getScore(t[0], t[1], t[2], t[3])
def getDeviation1(t):  return getDeviation(t[0], t[1], t[2], t[3])

def getAllDirectories():
  for dir in db_dirs:
    for d in os.listdir(dir):
      if os.path.isdir(d):
        dirs.append(d)
  return dirs

def getComposer(name):
  m = re.search(re.compile("([a-z]+)-[a-z|0-9]+-[a-z|0-9]+-[a-z]+-[a-z]"), name)
  if not m:
    m = re.search(re.compile("([a-z]+)-[a-z|0-9]+-[a-z]+-[a-z]"), name)
  val = m.group(1)
  for (key, value) in composers.viewitems():
    if value == val: return key

def getWork(name):
  m = re.search(re.compile("[a-z]+-([a-z|0-9]+-[a-z|0-9]+)-[a-z]+-[a-z]"), name)
  if not m:
    m = re.search(re.compile("[a-z]+-([a-z|0-9]+)-[a-z]+-[a-z]"), name)
  val = m.group(1)
  return val

def getPianist(name):
  m = re.search(re.compile("[a-z]+-[a-z|0-9]+-[a-z|0-9]+-([a-z]+)-[a-z]"), name)
  if not m:
    m = re.search(re.compile("[a-z]+-[a-z|0-9]+-([a-z]+)-[a-z]"), name)
  val = m.group(1)
  return val
#  for (key, value) in pianists.viewitems():
#    if value == val: return key

def getSoundfont(name):
  m = re.search(re.compile("[a-z]+-[a-z|0-9]+-[a-z|0-9]+-[a-z]+-([a-z])"), name)
  if not m:
    m = re.search(re.compile("[a-z]+-[a-z|0-9]+-[a-z]+-([a-z])"), name)
  val = m.group(1)
  for (key, value) in soundfonts.viewitems():
    if value == val: return key



def getPaths(composer=None, work='[a-z|0-9]+', performer='[a-z]+', sf=None):
  db_dirs = []
  dirs = []
  paths = []

  com = '[a-z]+'
  if composer:
    com = composers[composer]
  s = '[a-z]'
  if sf:
    s = soundfonts[sf]
  query = re.compile('{0}-{1}-[a-z|0-9]+-{2}-{3}'.format(com, work, performer, s))
  altquery = re.compile('{0}-{1}-{2}-{3}'.format(com, work, performer, s))

  for version in VERSIONS:
    db_dirs.append('{0}{1}/'.format(DB_PATH, version))
  
  for dir in db_dirs:
    for d in os.listdir(dir):
      p = dir + d
      if not os.path.isdir(p):
        continue
      if re.match(query, d) or re.match(altquery, d):
        paths.append(p)
  return paths


def getComposers():
  return composers.keys()

def getWorks(composer):
  paths = getPaths(composer=composer)
  works = []
  for path in paths:
    name = path.split("/")[-1]
    works.append((getWork(name), getPianist(name), getSoundfont(name)))
  return works

def getScoreMidiPath(composer, work, pianist, soundfont):
  path = getPaths(composer, work, pianist, soundfont)
  path = path[0]
  name = path.split("/")[-1]
  return '{0}/score.mid'.format(path)

def getPerformancePath(composer, work, pianist, soundfont):
  path = getPaths(composer, work, pianist, soundfont)
  path = path[0]
  name = path.split("/")[-1]
  return '{0}/{1}.mid'.format(path, name)

def getScorePath(composer, work, pianist, soundfont):
  path = getPaths(composer, work, pianist, soundfont)
  path = path[0]
  # This is a bit clumsy
  for f in os.listdir(path):
    name = f.split("/")[-1]
    if not name.endswith('.mid') and\
      not name.startswith('deviation') and\
      not name.endswith('nodoctype.xml'):
      path += "/{0}".format(name)
      break
  print path
  return path

def getDeviationPath(composer, work, pianist, soundfont):
  path = getPaths(composer, work, pianist, soundfont)
  path = path[0]
  name = path.split("/")[-1]
  return '{0}/deviation.xml'.format(path)

def getPerformance(composer, work, pianist, soundfont):
  path = getPerformancePath(composer, work, pianist, soundfont)
  os.system('cp {0} ./lastused/performance.mid'.format(path))
  return NoteList(path)

def getScore(composer, work, pianist, soundfont):
  path = getScorePath(composer, work, pianist, soundfont)
  os.system('cp {0} ./lastused/score.xml'.format(path))
  # For convenience, also copy the performance
  path2 = getPerformancePath(composer, work, pianist, soundfont)
  os.system('cp {0} ./lastused/performance.mid'.format(path2))
  return m21.converter.parse(path)

def getDeviation(composer, work, pianist, soundfont):
  path = getDeviationPath(composer, work, pianist, soundfont)
  targetpath = getScorePath(composer, work, pianist, soundfont)
  os.system('cp {0} ./lastused/deviation.xml'.format(path))
  return Deviations(path, targetpath)


def sampleScorePath(): return "./samples/score.xml"
def sampleScore(): return m21.converter.parse("./samples/score.xml")
def sampleDeviationPath(): return "./samples/deviation.xml"
def sampleDeviation(): return Deviations("./samples/deviation.xml")

def select():
  work = -1
  while(work == -1):
    comp = util.menu('Choose a composer', getComposers())
    work = util.menu('Choose a work and performer', getWorks(getComposers()[comp]), cancel=True)

  selected = getWorks(getComposers()[comp])[work]
  return getComposers()[comp], selected[0], selected[1], selected[2]

if __name__ == "__main__":
  import sequencer
  seq = sequencer.Sequencer()
  while(True):
    comp = util.menu('Choose a composer', getComposers())
    work = util.menu('Choose a work and performer', getWorks(getComposers()[comp]), cancel=True)
    if work == -1: continue
    selected = getWorks(getComposers()[comp])[work]
    choice = 0
    while choice != 8:
      choice = util.menu('What should I load?', ['Expressive performance', 'Score without expression'])
      if choice == 0:
        path = getPerformancePath(getComposers()[comp], selected[0], selected[1], selected[2])
      else:
        path = getScoreMidiPath(getComposers()[comp], selected[0], selected[1], selected[2])

      selection = (getComposers()[comp], selected[0], selected[1], selected[2])
      print path

      choice = util.menu('Choose action', \
          ['Play with internal sequencer', 'Play with audacious', 'View score', 'View midi info', 'View score info',\
          'Export deviation data to CSV', 'Performance', 'Extract melody','Cancel'])
      if choice == 0:
        seq.play(NoteList(path))
      elif choice == 1:
        os.system("audacious {0}".format(path))
      elif choice == 2:
        os.system("viewmxml {0}".format(getScorePath(getComposers()[comp], selected[0], selected[1], selected[2])))
        pass
      elif choice == 3:
        nlist = NoteList(path)
        nlist.printinfo()
      elif choice == 4:
        score = getScore(getComposers()[comp], selected[0], selected[1], selected[2])
        parts = 0
        notes = 0
        for part in score:
          bars = 0
          if not isinstance(part, m21.stream.Part): continue
          for bar in part:
            if not isinstance(bar, m21.stream.Measure): continue
            for note in bar:
              if not isinstance(note, m21.stream.Voice): continue
              notes += 1
            bars += 1
          print "{0} Bars in part".format(bars)
          parts += 1
        print "{0} Parts in piece, total notes: {1}".format(parts, notes)
      elif choice == 5:
        os.system("cmx dev2csv {0} > deviation.csv".format(getDeviationPath(getComposers()[comp], selected[0], selected[1], selected[2])))
        os.system("vim deviation.csv")
      elif choice == 6:
        alignment = Alignment(getScorePath1(selection), getDeviation1(selection))
        seq.play(alignment.performance())
      elif choice == 7:
        score = Score(getScore(getComposers()[comp], selected[0], selected[1], selected[2]))
        melody = score.melody()
        mxml = melody.musicxml
        f = open('output/melody.xml', 'w')
        f.write(mxml)
        f.close()
        mf = melody.midiFile
        mf.open('output/melody.mid', 'wb')
        mf.write()
        mf.close()
        notes = NoteList('output/melody.mid')
        seq.play(notes)

    


    # Difference check (see if parsing doesn't introduce errors)
    #os.system("python midi2text.py temp.mid > text1.txt")
    #os.system("python midi2text.py {0} > text2.txt".format(path))
    #os.system("diff text1.txt text2.txt")

#    os.system("audacious {0}".format(path))
#    getPerformance(getComposers()[comp], selected[0], selected[1], selected[2]).play()







