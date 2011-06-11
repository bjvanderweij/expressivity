# Take a score and deviation file as input.
# Parse the score in music21
# Iterate through every note of the score
# Find corresponding note in deviationdata
# Create performance features vector
# Hash an encoding string for note and measure store performance features in dictionary

import music21 as m21
import re
from BeautifulSoup import *

def note_deviations(deviation):
  f = open(deviation)
  devfile = f.read()
  soup = BeautifulStoneSoup(devfile)
  tags = soup.findAll('note-deviation')
# There are also misses!
  print len(tags)
  note_deviations = {}
  pointerexp = re.compile('@id=\'(.*)\'\]/measure\[\@number=\'(.*)\'\]/note\[(.*)\]')
  for tag in tags:
    m = re.search(pointerexp, tag.attrs[0][1])
    if not m: continue
    key = "Part-id: {0} measure: {1} number: {2}".format(m.group(1), m.group(2), m.group(3))
    value = (\
        float(tag.attack.contents[0]),\
        float(tag.release.contents[0]),\
        float(tag.dynamics.contents[0]),\
        float(tag.contents[3].contents[0]),\
      )
    note_deviations[key] = value
    print("{0}: {1}".format(key, value))
  return note_deviations

note_deviations('/home/bastiaan/UvA/Expressive-Performance_DATA/CrestMusePEDB/PEDBv2.2/cho-etd003-ashke-b/deviation.xml')
