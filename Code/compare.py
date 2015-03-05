from representation import *


a = NoteList('lastused/performance.mid')
b = NoteList('output/generated.mid')

for (n1, n2) in zip(a[:20],b[:20]):
  print('A on: {0} B on: {1}. A duration: {2} B duration: {3}'.format(n1.on, n2.on, n1.duration(), n2.duration()))


#print "Original"
#for n in a[:10]:
#  print n.info()
#print "Generated"
#for n in b[:10]:
#  print n.info()
