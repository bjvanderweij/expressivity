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

def discretize_features(features, multiplication=10, division=5.0):
  division = float(division)
  # Select subset
  avg_dur = features[1]
  avg_pitch = features[2]
  pitch_direction = features[3]
  # Discretise
# avg dur klopt niet
  avg_dur = int(avg_dur / multiplication)
  avg_pitch = int(avg_pitch / division)
  if pitch_direction > 0: pitch_direction = 1
  if pitch_direction < 0: pitch_direction = -1
  else: pitch_direction = 0
  return (avg_dur, avg_pitch, pitch_direction)
  

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

def undiscretize(state, multiplication=30):
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


def trainHMM(hmm, features_set, expression_set, f_discretization=10, e_discretization=30):
  for work in features_set.keys():
    features = features_set[work]
    expression = expression_set[work]
    obs = []
    states = []
    # Select the subset of features that will be used and discretise
    for f in features:
      obs.append(discretize_features(f, f_discretization))
    lastexp = 'start'
    for p in expression:
      #  Multiplication for expression and features doesn't neccesarily need to be the same!
      exp = discretize_expression(p, e_discretization) 
      states.append(exp)
      lastexp = exp
    hmm.learn(obs, states)

def render(score, segmentation, hmm, f_discretization=10, e_discretization=30):
  # Extract scorefeatures
  features = sf.vanDerWeijFeatures(score, segmentation) 
  # Discretize
  observations = []
  for f in features:
    observations.append(discretize_features(f, f_discretization))
  print 'Observations:\n{0}'.format(observations)
  # Find the best expressive explanation for these features
  print "Finding best fitting expression"
  states = hmm.viterbi(observations)[1]
  expression = []
  for state in states:
    expression.append(undiscretize(state, e_discretization))
  print 'Expression states:\n{0}'.format(states)

  return expression
  
def test(f_discretization=10, e_discretization=30, indep=False, selection=None):
  if not selection:
    selection = (db.select())
  else:
    print 'Performing {0}'.format(selection)
  score = db.getScore1(selection)
  (f, e) = tools.chooseFeatures()
  if indep:
    hmm = HMM_indep(2)
  else:
    hmm = HMM(2)

  trainHMM(hmm, f, e, f_discretization, e_discretization)
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

  expression = render(melodyscore, onset, hmm, f_discretization, e_discretization)

  print "Done, resulting expression: {0}".format(expression)
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
  multiplication = 10
  indep = False
  a = sys.argv
  selection = None
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
      elif a[i] == '-s'
        try:
          selection = db.byIndexes(int(a[i+1]), int(a[i+2]))
          i += 2
        except IndexError, ValueError:
          print 'Error parsing command line arguments'
          exit(0)
      else:
        print "I don't understand {0}".format(a[i])
      i += 1

  test(multiplication, indep, selection=selection)

  

def render1(score):
  melody = Score(score).melody()
  features = scoremodel.features(melody, None)

  parsetree = structure.parse(melody)
  scorefeatures = scorefeatures.extract(melody)
  deviations = expressionmodel.predictDeviations(melody, parsetree, scorefeatures)
  alignment = Alignment(melody, deviations)
  return alignment.performance(score, deviations)



