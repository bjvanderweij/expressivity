import database as db
from alignment import *
from representation import *
import structure, tools, scorefeatures, performancefeatures


def trainset(composers=None, pianist=None):
  queries = []
  if not composers:
    composers = db.composers
  for composer in composers:
    works = db.getWorks(composer)
    for work in works:
      if pianist:
        if work[1] == pianist:
          queries.append((composer, work[0], work[1], work[2]))
      else:
        queries.append((composer, work[0], work[1], work[2]))
  return queries


def train(trainset):
  expression = {}
  features = {}
  const = 0
  Max = 0
  Min = None
  print ">>>Loading scores and deviations, this will take hours and may eat all you memory"
  for query in trainset:
    print ">>>Loading: {0}".format(query)
    score = db.getScore1(query)
    deviations = db.getDeviation1(query)
    alignment = Alignment(score, deviations)
    melody = alignment.melody()
    segments = structure.reasonableSegmentation(tools.parseScore(melody))
    const += len(segments)
    lengths = sum([len(s) for s in segments])
    m = max([len(s) for s in segments])
    mi = min([len(s) for s in segments])
    if m > Max:
      Max = m
    if not Min:
      Min = mi
    if mi < Min:
      Min = mi
    expression[query] = performancefeatures.vanDerWeijExpression(alignment, segments)
    features[query] = scorefeatures.vanDerWeijFeatures(melody, segments)

  print "Done, {0} segments found with an average length of: {1} (min: {2} max: {3})".format(const, lengths / float(const), Min, Max)
  tools.saveFeatures(features, expression)
#  tools.saveCSV(features, expression)

if __name__ == "__main__":
  import sys
  train(trainset(sys.argv[1:]))


