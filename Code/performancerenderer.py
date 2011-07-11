#!/usr/bin/env python
# these files extract needed features and structural information
import scorefeatures as sf
# *model contains statistical information
# datahandling files
from score import *
from representation import *
from hmm import *
from sequencer import *
import database as db
import alignment, math
import perform, util, structure

#(dPitch, abs_dPitch, dDuration, abs_dDuration, silence, ddPitch, abs_ddPitch, pitch_direction)
def discretize_features(features, discretization=10):
  f = []
  r = range(len(features))
  for i in range(len(features)):
    f.append(int(features[i] * discretization))
  return tuple(f)
  # Select subset
  # Discretise

def preprocess(features, normalizations, discretization=10, subset=None):
  observations = []
  lastPitch = 0
  lastDuration = 0
  for f in features:
    # Normalize
    f = [f[i] / float(normalizations[i]) for i in range(len(f))]
    pitch = f[sf.featureset.index('avg_pitch')]
    duration = f[sf.featureset.index('avg_duration')]
    pitch_interval = 0
    duration_ratio = 0 
    if lastPitch != 0:
      pitch_interval = pitch - lastPitch
      duration_ratio = math.log(duration/float(lastDuration))
    f[sf.featureset.index('avg_pitch')] = pitch_interval
    f[sf.featureset.index('avg_duration')] = duration_ratio
    lastPitch = pitch
    lastDuration = duration
    obs = f
    if subset:
      obs = [obs[i] for i in subset]
    observations.append(discretize_features(obs, discretization))
  return observations
    
  

def discretize_expression(parameters, multiplication=30):
  # Select subset
  avg_rel_l = parameters[1]
  avg_artic = parameters[2]
  avg_tempo = parameters[3]
  # Discretise
  # Perhaps it is better to take this logarithm into performancefeatures
  avg_rel_l = int(math.log(avg_rel_l) * multiplication)
  avg_artic = int(avg_artic * multiplication)
  avg_tempo = int(math.log(avg_tempo) * multiplication)
  return (avg_rel_l, avg_artic, avg_tempo)

def undiscretize(state, multiplication=30.0):
  multiplication = float(multiplication)
  # Select subset
  avg_rel_l = state[0]
  avg_artic = state[1]
  avg_tempo = state[2]
  # Discretise
  # Perhaps it is better to take this logarithm into performancefeatures
  avg_rel_l = math.exp(avg_rel_l / multiplication)
  avg_artic = avg_artic / multiplication
  avg_tempo = math.exp(avg_tempo / multiplication)
  return (avg_rel_l, avg_artic, avg_tempo)


def trainHMM(hmm, features_set, expression_set, f_discretization=10, e_discretization=30, subset=None):
  l = 0
  for work in features_set.keys():
    l = len(features_set[work][0])
    break
  normalizations = [0 for i in range(l)]
  for work in features_set.keys():
    m = []
    for i in range(l):
      m = max([f[i] for f in features_set[work]])
      if m > normalizations[i]:
        normalizations[i] = m
  hmm.normalizations = normalizations
  for work in features_set.keys():
    features = features_set[work]
    expression = expression_set[work]
    obs = preprocess(features, normalizations, f_discretization, subset)
    states = []
    # Select the subset of features that will be used and discretise
    for f, p in zip(features, expression):
      exp = discretize_expression(p, e_discretization) 
      #states.append(tuple(list(exp) + list(featureset)))
      states.append(exp)

    hmm.learn(obs, states)

def render(score, segmentation, hmm, f_discretization=10, e_discretization=30, subset=None):
  # Extract scorefeatures
  features = sf.vanDerWeijFeatures(score, segmentation) 
  # Discretize
  observations = preprocess(features, hmm.normalizations, f_discretization, subset)
  print 'Observations:\n{0}'.format(observations)
  # Find the best expressive explanation for these features
  print "Finding best fitting expression"
  (p, states) = hmm.viterbi(observations)
  expression = []
  for state in states:
    expression.append(undiscretize(state, e_discretization))
  print 'Expression states:\n{0}'.format(states)

  return (p, expression)
 
def analyseCorpus(discret):
  (f, e, m) = tools.chooseFeatures()

  for work in e:
    print '----------------------------------------'
    expression = [undiscretize(discretize_expression(x, discret), discret) for x in e[work]]
    print 'Loudness:\t',
    for p in expression:
      print '{0}\t'.format(p[0]),
    print '\nArticulation:\t',
    for p in expression:
      print '{0}\t'.format(p[1]),
    print '\nTempo:\t\t',
    for p in expression:
      print '{0}\t'.format(p[2]),
    print '\n'


def test(f_discretization=10, e_discretization=30, indep=False, selection=None, subset=None, corpus=None):
  if not selection:
    selection = (db.select())
  score = db.getScore1(selection)
  if not corpus:
    (f, e, m) = tools.chooseFeatures()
  else:
    (f, e, m) = tools.loadFeatures(corpus)
  if m['version'] != sf.version:
    print "Scorefeatures versions don't match! Corpus version: {0} Scorefeatures version: {1}".format(m['version'], sf.version)
    exit(0)
  if not subset:
    # Select a subset by hand
    choice = 1
    subset = []
    while True:
      print 'Subset: [',
      print ', '.join([m['featureset'][i] for i in subset]),
      print ']'
      choice = util.menu('Select features', ['Done'] + m['featureset'])
      if choice == 0:
        break
      subset.append(choice-1)
  print 'Performing {0}'.format(selection)
  print 'Features version: {0}'.format(m['version'])
  if subset:
    print 'Featureset used: [',
    print ', '.join([m['featureset'][i] for i in subset]),
    print ']'
  print 'Scorefeatures discretization: {0}\nExpression discretization: {1}'.format(f_discretization, e_discretization)
  if indep:
    hmm = HMM_indep(2)
  else:
    hmm = HMM(2)

  trainHMM(hmm, f, e, f_discretization, e_discretization, subset=subset)
  hmm.storeInfo('hmm2.txt')
  print "Loading score"
  melodyscore = Score(score).melody()
  melody = tools.parseScore(melodyscore)
  # Segmentate the the score
  print "Analysing score"
  onset = structure.reasonableSegmentation(melody)
  #onset = structure.groupings(structure.list_to_tree(structure.first_order_tree(structure.onset, melody, 0.1)), 1)
  #namelist = []
  #for group in onset:
  #  namelist.append([leaf.name() for leaf in group])
  #print namelist

  (p, expression) = render(melodyscore, onset, hmm, f_discretization, e_discretization, subset)

  print "Done, resulting expression(with a probability of {1}): {0}".format(expression, p)
  name = raw_input("Enter a name for saving this performance or press enter to skip this step.\n")
  if not name == '':
    tools.savePerformance(selection, expression, name)

  performance = perform.perform(score, melodyscore, onset, expression, converter=melody)

# Store performance?
# Speed
# Dynamics
  seq = Sequencer()
  seq.play(performance)

def loadperformance():
  (selection, expression) = tools.loadPerformance()
  score = db.getScore1(selection)
  melodyscore = Score(score).melody()
  melody = tools.parseScore(melodyscore)
  segmentation = structure.reasonableSegmentation(melody)
  performance = perform.perform(score, Score(score).melody(), segmentation, expression, converter=melody)
  seq = Sequencer()
  seq.play(performance)



if __name__ == '__main__':
  import sys
  indep = False
  a = sys.argv
  selection = None
  subset = None
  f_discretization = 10
  e_discretization = 10
  corpus = None
  if len(a) > 1:
    if a[1] == 'load':
      loadperformance()
      exit(0)
    elif a[1] == 'train':
      import train
      composers = raw_input("Enter composers\n").split(" ")
      pianist = raw_input("Enter pianist\n")
      if pianist == '': pianist = None
      set = train.trainset(composers, pianist)
      train.train(set)
      exit(0)
    elif a[1] == 'align':
      import train
      set = [db.select()]
      train.train(set)
      exit(0)
    elif a[1] == 'features':
      s = db.select()
      score = Score(db.getScore1(s))
      melodyscore = score.melody()
      melody = tools.parseScore(melodyscore)
      segmentation = structure.reasonableSegmentation(melody)
      f = sf.vanDerWeijFeatures(melodyscore, segmentation)
      for x in f:
        #(dPitch, abs_dPitch, dDuration, abs_dDuration, silence, ddPitch, abs_ddPitch, pitch_direction)
        print 'dpitch: {0} abs_dPitch: {1} dDuration: {2} abs_dDuration: {3} silence: {4}'.format(x[0], x[1], x[2], x[3], x[4])
        print 'ddPitch: {0} abs_ddPitch: {1} : pitch_direction: {2}'.format(x[5], x[6], x[7])
      exit(0)
    elif a[1] == 'merge':
      # Merge datasets
      choice = -1
      datasets = []
      while True:
        choice = util.menu('Choose datasets', ['Done'] + tools.datasets())
        if choice == 0: break
        datasets.append(tools.loadFeatures(tools.datasets()[choice-1]))
      features = {}
      expression = {}
      metadata = {}
      for (f, e, m) in datasets:
        if not 'version' in metadata:
          metadata['version'] = m['version']
          metadata['featureset'] = m['featureset']
        elif not metadata['version'] == m['version']:
          print "Scorefeatures versions don't match! Can't merge."
          exit(0)
        for work in f:
          if work in features:
            print 'Skipping dupe {0}'.format(work)
            continue
          features[work] = f[work]
          expression[work] = e[work]
      print 'Done, number of works in new dataset: {0}'.format(len(features)) 
      tools.saveFeatures(features, expression)
      exit(0)
    i = 1
    while i < len(a):
      if a[i] == '-indep':
        indep = True
      elif a[i] == '-d':
        try:
          f_discretization = int(a[i+1])
          e_discretization = int(a[i+2])
          i += 2
        except IndexError, ValueError:
          print 'Error parsing command line arguments'
          exit(0)
      elif a[i] == '-s':
        try:
          selection = db.byIndexes(int(a[i+1]), int(a[i+2]))
          i += 2
        except IndexError, ValueError:
          print 'Error parsing command line arguments'
          exit(0)
      elif a[i] == '-subset':
        try:
          subset = [int(x) for x in a[i+1:]]
          i += len(a[i+1:])
        except IndexError, ValueError:
          print 'Error parsing command line arguments'
          exit(0)
      elif a[i] == '-corpus':
        try:
          corpus = a[i+1]
          i += 1
        except IndexError, ValueError:
          print 'Error parsing command line arguments'
          exit(0)
      else:
        print "I don't understand {0}".format(a[i])
      i += 1


  test(f_discretization, e_discretization, indep, selection=selection, subset=subset, corpus=corpus)

  

def render1(score):
  melody = Score(score).melody()
  features = scoremodel.features(melody, None)

  parsetree = structure.parse(melody)
  scorefeatures = scorefeatures.extract(melody)
  deviations = expressionmodel.predictDeviations(melody, parsetree, scorefeatures)
  alignment = Alignment(melody, deviations)
  return alignment.performance(score, deviations)



