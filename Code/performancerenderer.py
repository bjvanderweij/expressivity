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

def sigmoid(x, p=1.0):
  return 1/(1+math.exp(-p*x))

def inv_sigmoid(y, p=1.0):
  return -math.log((1/float(y) - 1))/float(p)

# Given normalized features use some function to discretize.
# Possibilities: linear or sigmoid
# Use a logistic function to get a larger resolution for small differences than for larger ones
def discretize(features, discretization=10, function='sigmoid', logarithmic=False, sensitivity=5):
  f = []
  # WORKAROUND
  if logarithmic:
    for i in range(len(features)):
      if features[i] < 0: 
        features[i] = -features[i]
        print "Warning: invalid featurevalue found, {0} in {1}".format(features[i], features)
    features = [math.log(x) for x in features]
  if function == 'linear':
    for i in range(len(features)):
      f.append(int(round(features[i] * float(discretization))))
  elif function == 'sigmoid':
    for i in range(len(features)):
      f.append(int((sigmoid(features[i], sensitivity) * float(discretization))))
  return f

def undiscretize(features, discretization=10, function='sigmoid', logarithmic=False, sensitivity=5.0):
  features = list(features)
  discretization = float(discretization)
  f = []
  if function == 'linear':
    for i in range(len(features)):
      f.append(features[i] / discretization)
  elif function == 'sigmoid':
    for i in range(len(features)):
      # Discretization may have made a features the minumum or max value, cap this to 1 and 9
      if features[i] == 0:
        features[i] = 1        
      if features[i] == discretization:
        features[i] = 9        
      f.append(inv_sigmoid(features[i] / discretization, sensitivity))
  if logarithmic:
    f = [math.exp(x) for x in f]
  return f

def discretize_expression(parameters, discretization=10, subset=[1,2,3], sensitivity=5):
  if subset != []:
    parameters = [parameters[i] for i in subset]
  return tuple(discretize(parameters, discretization, function='sigmoid', logarithmic=True, sensitivity=sensitivity))

def undiscretize_expression(state, discretization=10, sensitivity=5):
  return tuple(undiscretize(state, discretization, function='sigmoid', logarithmic=True, sensitivity=sensitivity))

def normalize(features, normalizations):
  for i in range(len(features)):
    # Normalize
    features[i] = [features[i][j] / float(normalizations[j]) for j in range(len(features[i]))]
  return features

# Make relative features and select subset
def preprocess(features, subset=None):
  preprocessed = []
  for f0, f1 in zip(features[:-1], features[1:]):
    pitch0 = f0[sf.featureset.index('avg_pitch')]
    duration0 = f0[sf.featureset.index('avg_duration')]
    dPitch0 = f0[sf.featureset.index('abs_dPitch')]
    dDuration0 = f0[sf.featureset.index('abs_dDuration')]
    pitch1 = f1[sf.featureset.index('avg_pitch')]
    duration1 = f1[sf.featureset.index('avg_duration')]
    dPitch1 = f1[sf.featureset.index('abs_dPitch')]
    dDuration1 = f1[sf.featureset.index('abs_dDuration')]
    # Difference in average pitch
    pitch_interval = (pitch0 - pitch1)# * 10 # 10 is a rather arbitrary number to make this feature visible in discretization
    # Relative difference in average note duration
    duration_ratio = math.log(duration0/float(duration1))
    # Do the next two features make any musical sense?
    #dPitch_interval = dPitch0 - dPitch1 
    #ldDuration_ratio = math.log(dDuration/float(last_dDuration)) # What if lastDDuration is zero?
    f0 = list(f0)
    f0[sf.featureset.index('avg_pitch')] = pitch_interval
    f0[sf.featureset.index('avg_duration')] = duration_ratio
    #f0[sf.featureset.index('abs_dPitch')] = dPitch_interval
    #f[sf.featureset.index('abs_dDuration')] = dDuration_ratio
    if subset:
      preprocessed.append([f0[i] for i in subset])
    else:
      preprocessed.append(f0)
  # The last constituent:
  f = list(features[-1])
  f[sf.featureset.index('avg_pitch')] = pitch_interval
  f[sf.featureset.index('avg_duration')] = duration_ratio
  if subset:
    preprocessed.append([f[i] for i in subset])
  else:
    preprocessed.append(f)
  return preprocessed
    
  



def trainHMM(hmm, features_set, expression_set, f_discretization=10, e_discretization=10, subset=None, ignore=None, sensitivity=5):
  preprocessed = {}
  for work in features_set.keys():
    preprocessed[work] = preprocess(features_set[work], subset)
 
  # Ugly way to get the number of features
  l = 0
  for work in preprocessed.keys():
    l = len(preprocessed[work][0])
    break

  normalizations = [0 for i in range(l)]
  for work in preprocessed.keys():
    m = []
    for i in range(l):
      m = max([abs(f[i]) for f in preprocessed[work]])
      if m > normalizations[i]:
        normalizations[i] = m
  hmm.normalizations = normalizations
  for work in preprocessed.keys():
    if work[0] == ignore[0] and work[1] == ignore[1]:
      continue
    features = normalize(preprocessed[work], normalizations)
    expression = expression_set[work]
    obs = [tuple(discretize(f, f_discretization, 'linear')) for f in features]
    states = []
    # Select the subset of features that will be used and discretise
    for f, p in zip(features, expression):
      exp = discretize_expression(p, e_discretization, sensitivity=sensitivity) 
      #states.append(tuple(list(exp) + list(featureset)))
      states.append(exp)

    hmm.learn(obs, states)

def render(score, segmentation, hmm, f_discretization=10, e_discretization=30, subset=None, sensitivity=5):
  # Extract scorefeatures
  features = sf.vanDerWeijFeatures(score, segmentation) 
  # Discretize
  features = normalize(preprocess(sf.vanDerWeijFeatures(score, segmentation), subset), hmm.normalizations)
  observations = [tuple(discretize(f, f_discretization, 'linear')) for f in features]
  print 'Observations:\n{0}'.format(observations)
  # Find the best expressive explanation for these features
  print "Finding best fitting expression"
  (p, states) = hmm.viterbi(observations)
  print p, states
  expression = []
  for state in states:
    expression.append(undiscretize_expression(state, e_discretization, sensitivity=sensitivity))
  print 'Expression states:\n{0}'.format(states)

  return (p, expression)
 
def selectSubset(set):
  choice = 1
  subset = []
  while True:
    print 'Subset: [',
    print ', '.join([set[i] for i in subset]),
    print ']'
    choice = util.menu('Select features', ['Done'] + set)
    if choice == 0:
      break
    subset.append(choice-1)
  return subset

def analyseCorpus(discret):
  (f, e, m) = tools.chooseFeatures()

  for work in e:
    print '----------------------------------------'
    expression = [undiscretize_expression(discretize_expression(x, discret), discret) for x in e[work]]
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
  subset = selectSubset(m['featureset'])
  hmm = HMM(2)
  trainHMM(hmm, f, e, discret, discret, subset=subset)
  for work in e:
    features = f[work]
    processed = preprocess(f[work], hmm.normalizations, discret, subset=subset)
    for s, p in zip(features, processed):
      print '{0}-{1}: {2}'.format(work[1], work[2], [s[i] for i in subset])
      print '{0}-{1}: {2}'.format(work[1], work[2], p)

      

def loadperformance():
  (selection, expression) = tools.loadPerformance()
  score = db.getScore1(selection)
  melodyscore = Score(score).melody()
  melody = tools.parseScore(melodyscore)
  segmentation = structure.reasonableSegmentation(melody)
  performance = perform.perform(score, Score(score).melody(), segmentation, expression, converter=melody)
  seq = Sequencer()
  seq.play(performance)

def visualize(segmentation, expression, visualize=None, store=None, title=None):
  notes = []
  onsets = []
  values = []
  if not visualize:
    visualize = selectSubset(['Dynamics', 'Articulation', 'Tempo'])
  for segment, expr in zip(segmentation, expression):
    for note in segment:
      onsets.append(note.on)
      values.append([expr[i] for i in visualize])
  import matplotlib.pyplot as plt
  fig = plt.figure()
  plt.plot(onsets, values)
  plt.ylabel('Deviation')
  plt.xlabel('Score time')
  if title:
    plt.title(title)
  #dplot = fig.add_subplot(111)
  #sodplot = fig.add_subplot(111)
  #dplot.plot([i for i in range(len(deltas[0]))], deltas[0])
  #sodplot.plot([i for i in range(len(sodeltas[0]))], sodeltas[0])
  if store:
    fig.savefig('plots/{0}.png'.format(store))
  else:
    plt.show()

def plotCorpus():
  (f, e, m) = tools.chooseFeatures()
  d = raw_input('Discretization? ')
  if not d == '':
    s = raw_input('Sensitivity? [5]')
    if s == '':
      s = 5.0
    d = float(d)
    s = float(s)
  else: d = None

  for work in f:
    print 'Plotting and saving {0}'.format(work)
    expression = e[work]
    if d:
      expression = [undiscretize_expression(discretize_expression(x, d, sensitivity=s), d, sensitivity=s) for x in expression]
    score = db.getScore1(work)
    segmentation = structure.reasonableSegmentation(tools.parseScore(Score(score).melody()))
    visualize(segmentation, expression, [0, 1, 2], '{0}-{1}-{2}'.format(work[0], work[1], work[2]), '{0}-{1} by {2}'.format(work[0], work[1], work[2]))


def playPerformance(selection, performance, expression, segmentation, name='ExpressivePerformance'):
  # Store?
  # Play again?
  # View first x notes?
  while True:
    choice = util.menu('What do you want to do?', ['Play performance', 'Store expression', 'Store midi', 'View first notes of performance', 'Plot performance', 'Save plot', 'View segmentation', 'Make segmentation audible', 'Quit'])
    if choice == 0:
      seq = Sequencer()
      seq.play(performance)
    elif choice == 1:
      n = raw_input("Enter a name for saving this performance. [{0}]\n".format(name))
      if not n == '': name = n
      tools.savePerformance(selection, expression, name)
    elif choice == 2:
      n = raw_input("Enter a name for saving this performance. [{0}.mid]\n".format(name))
      if not n == '': name = n
      performance.exportMidi('output/{0}.mid'.format(name))
    elif choice == 3:
      for note in performance[:30]:
        print note
    elif choice == 4: # Plot
      visualize(segmentation, expression)
    elif choice == 5: # Save plot
      n = raw_input("Enter a name for saving this performance. [{0}.mid]\n".format(name))
      if not n == '': name = n
      visualize(segmentation, expression, store=name)
    elif choice == 6: # View segments
      pass
    elif choice == 7: # Play segments
      pass
    elif choice == 8: # Quit
      break
    
def test(f_discretization=10, e_discretization=30, indep=False, selection=None, subset=None, corpus=None, smoothing=None, sensitivity=5):
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
    subset = selectSubset(m['featureset'])
  print '\n\tPerforming {0}'.format(selection)
  print '\tFeatures version: {0}'.format(m['version'])
  print '\tFeatureset used: [',
  print ', '.join([m['featureset'][i] for i in subset]),
  print ']'
  print '\tScorefeatures discretization: {0}\n\tExpression discretization: {1}'.format(f_discretization, e_discretization)
  print '\tSensitivity: {0}'.format(sensitivity)
  print '\tSmoothing: {0}'.format(smoothing)
  print '\tCorpus: {0}\n'.format(corpus)
  if indep:
    hmm = HMM_indep(2, smoothing)
  else:
    hmm = HMM(2, smoothing)

  trainHMM(hmm, f, e, f_discretization, e_discretization, subset=subset, ignore=selection, sensitivity=sensitivity)
  #trainHMM(hmm, f, e, f_discretization, e_discretization, subset=subset)
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

  (p, expression) = render(melodyscore, onset, hmm, f_discretization, e_discretization, subset, sensitivity=sensitivity)

  print "Done, resulting expression(with a probability of {1}): {0}".format(expression, p)

  performance = perform.perform(score, melodyscore, onset, expression, converter=melody)
  playPerformance(selection, performance, expression, onset, '{0}_{1}_on_{2}_discret_{3}-{4}_smoothing_{5}'.format(\
      selection[0], selection[1], corpus, f_discretization, e_discretization, smoothing))

# Store performance?
# Speed
# Dynamics

if __name__ == '__main__':
  import sys
  indep = False
  a = sys.argv
  selection = None
  subset = None
  f_discretization = 10
  e_discretization = 10
  corpus = None
  smoothing = None
  sensitivity = 5
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
    elif a[1] == 'plotcorpus':
      plotCorpus()
      exit(0)
    elif a[1] == 'plot':
      (selection, expression) = tools.loadPerformance()
      if selection == None:
        selection = db.select()
      score = db.getScore1(selection)
      melodyscore = Score(score).melody()
      melody = tools.parseScore(melodyscore)
      segmentation = structure.reasonableSegmentation(melody)
      visualize(segmentation, expression)
      exit(0)
    elif a[1] == 'corpora':
      for x in tools.datasets():
        print 'Name:\t[{0}]\tInfo:\t{1}'.format(x, tools.corpusInfo(x))
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
    elif a[1] == 'analyze':
      analyseCorpus(int(a[2]))
      exit(0)
    i = 1
    while i < len(a):
      if a[i] == '-indep':
        indep = True
      elif a[i] == '-sensitivity':
        try:
          sensitivity = float(a[i+1])
          i += 1
        except IndexError, ValueError:
          print 'Error parsing command line arguments'
          exit(0)
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
          selection = db.byIndexes(int(a[i+1])-1, int(a[i+2])-1)
          i += 2
        except IndexError, ValueError:
          print 'Error parsing command line arguments'
          exit(0)
      elif a[i] == '-subset':
        try:
          subset = [int(x)-2 for x in a[i+1:]]
          i += len(a[i+1:])
        except IndexError, ValueError:
          print 'Error parsing command line arguments'
          exit(0)
      elif a[i] == '-smoothing':
        try:
          smoothing = a[i+1]
          i += 1
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


  test(f_discretization, e_discretization, indep, selection=selection, subset=subset, corpus=corpus, smoothing=smoothing, sensitivity=sensitivity)

  

def render1(score):
  melody = Score(score).melody()
  features = scoremodel.features(melody, None)

  parsetree = structure.parse(melody)
  scorefeatures = scorefeatures.extract(melody)
  deviations = expressionmodel.predictDeviations(melody, parsetree, scorefeatures)
  alignment = Alignment(melody, deviations)
  return alignment.performance(score, deviations)



