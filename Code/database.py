from music21 import converter
import representation
import os, re, util

DB_PATH = "/home/bastiaan/UvA/ExpressivePerformance/CrestMusePEDB/"
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

def getPerformance(composer, work, pianist, soundfont):
  path = getPaths(composer, work, pianist, soundfont)
  path = path[0]
  name = path.split("/")[-1]
  return representation.PianoRoll('{0}/{1}.mid'.format(path, name))

def getScore(composer, work, pianist, soundfont):
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
  return converter.parse(path)

def getDevInstance(composer, work, pianist, soundfont):
  path = getPaths(composer, work, pianist, soundfont)
  path = path[0]

if __name__ == "__main__":
  import sequencer
  seq = sequencer.Sequencer()
  while(True):
    comp = util.menu('Choose a composer', getComposers())
    work = util.menu('Choose a work and performer', getWorks(getComposers()[comp]), cancel=True)
    if work == -1: continue
    selected = getWorks(getComposers()[comp])[work]
    getPerformance(getComposers()[comp], selected[0], selected[1], selected[2]).play()
#    seq.play(getPerformance(getComposers()[comp], selected[0], selected[1], selected[2]))







