import database as db
from representation import *
from score import *
from alignment import *
import util, tools, structure


# Load all the scores and notelists

#while True:
#  print db.select()
print(">>>> Loading materials.....")

schumann = ('Schumann', 'kdz007', 'ashke', 'GPO-Concert-Steinway-ver2.sf2')
mozart1 = ('Mozart', 'snt331-3', 'nakam', 'GPO-Concert-Steinway-ver2.sf2')
chopin1 = ('Chopin', 'wlz010', 'ashke', 'Bosendorfer PIANO / GIGA')
mozart2 = ('Mozart', 'snt331-1', 'mo', None)
lastig = ('Bach', 'wtc219-f', 'richt', 'GPO-Concert-Steinway-ver2.sf2')

score = Score(db.getScore1(chopin1).stripTies())
melody = score.melody()
chopinnotes = tools.parseScore(melody)
delta = structure.absolute_deltalist(structure.onset, chopinnotes)
sodelta1 = structure.normalize(structure.second_order_deltalist(delta))

score = Score(db.getScore1(mozart2).stripTies())
melody = score.melody()
mozartnotes = tools.parseScore(melody)
delta2 = structure.square(structure.absolute_deltalist(structure.pitch, mozartnotes))
sodelta2 = structure.normalize(structure.second_order_deltalist(delta2))

s1 = structure.second_order_deltarule(chopinnotes, sodelta1, 0.1)
s2 = structure.second_order_deltarule(mozartnotes, sodelta2, 0.1)

while True:
  choice = util.menu("Select", ['Schumann exp', 'Schumann score', 'Schumann noexp', 'chopin struct', 'lastig struct bach', 'struct moz'])
  if choice == 0:
    path = db.getPerformancePath1(schumann)
    os.system("audacious {0}".format(path))
  if choice == 1:
    os.system("viewmxml {0}".format(db.getScorePath1(schumann)))
  if choice == 2:
    path = db.getScoreMidiPath1(schumann)
    os.system("audacious {0}".format(path))
  if choice == 3:
    groups = structure.groupings(structure.list_to_tree(s1), 1)
    structured_notes = []
    loud = False
    for group in groups:
      if loud:
        loud = False
      else:
        loud = True
      for leaf in group:
        if loud:
          leaf.onvelocity = 80
        else:
          leaf.onvelocity = 50
        structured_notes.append(leaf)
        
    chopinnotes.notes = structured_notes
    chopinnotes.exportMidi('temp.mid')
    os.system("audacious temp.mid")
  if choice == 4:
    path = db.getPerformancePath1(lastig)
  if choice == 5:
    groups = structure.groupings(structure.list_to_tree(s2), 3)
    structured_notes = []
    loud = False
    for group in groups:
      if loud:
        loud = False
      else:
        loud = True
      for leaf in group:
        if loud:
          leaf.onvelocity = 80
        else:
          leaf.onvelocity = 50
        structured_notes.append(leaf)
        
    mozartnotes.notes = structured_notes
    mozartnotes.exportMidi('temp.mid')
    os.system("audacious temp.mid")


