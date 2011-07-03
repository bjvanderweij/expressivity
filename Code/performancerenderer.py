# these files extract needed features and structural information
import scorefeatures as sf
import structure
# *model contains statistical information
# datahandling files
from score import *
from representation import *
from hmm import *
from sequencer import *
import database as db
import alignment, math
import perform


def discretize_features(features):
  # Select subset
  avg_dur = features[1]
  avg_pitch = features[2]
  pitch_direction = features[3]
  # Discretise
  print avg_dur
  avg_dur = int(math.log(avg_dur) * 20)
  avg_pitch = int(avg_pitch / 4.0)
  if pitch_direction > 0: pitch_direction = 1
  if pitch_direction < 0: pitch_direction = -1
  else: pitch_direction = 0
  return (avg_dur, avg_pitch, pitch_direction)
  

def discretize_expression(parameters):
  # Select subset
  avg_rel_l = parameters[1]
  avg_artic = parameters[2]
  avg_tempo = parameters[3]
  # Discretise
  # Perhaps it is better to take this logarithm into performancefeatures
  avg_rel_l = int(math.log(avg_rel_l) * 20)
  avg_artic = int(avg_artic * 20)
  avg_tempo = int(math.log(avg_tempo) * 20)
  return (avg_rel_l, avg_artic, avg_tempo)

def undiscretize(state):
  # Select subset
  avg_rel_l = state[0]
  avg_artic = state[1]
  avg_tempo = state[2]
  # Discretise
  # Perhaps it is better to take this logarithm into performancefeatures
  avg_rel_l = math.exp(avg_rel_l / 20.0)
  avg_artic = avg_artic / 20.0
  avg_tempo = math.exp(avg_tempo / 20.0)
  return (avg_rel_l, avg_artic, avg_tempo)


def trainHMM(features_set, expression_set):
  hmm = HMM()
  for work in features_set.keys():
    features = features_set[work]
    expression = expression_set[work]
    obs = []
    states = []
    # Select the subset of features that will be used and discretise
    for f in features:
      obs.append(discretize_features(f))
    for p in expression:
      states.append(discretize_expression(p))
    hmm.learn(obs, states)
  return hmm

def render(score, hmm):
  print "Loading score"
  melodyscore = Score(score).melody()
  melody = tools.parseScore(melodyscore)
  # Segmentate the the score
  print "Analysing score"
  onset = structure.groupings(structure.list_to_tree(structure.first_order_tree(structure.onset, melody, 0.1)), 1)
  # Extract scorefeatures
  features = sf.vanDerWeijFeatures(melodyscore, onset) 
  # Discretize
  observations = []
  for f in features:
    observations.append(discretize_features(f))
  # Find the best expressive explanation for these features
  print "Finding best fitting expression"
  states = hmm.viterbi(observations)[1]
  expression = []
  for state in states:
    expression.append(undiscretize(state))


  print "Generating performance"
  seq = Sequencer()
  seq.play(perform.vanDerWeijPerformSimple(score, melodyscore, onset, expression, bpm=120, converter=melody))
  
def test():
  score = db.getScore1(db.select())
  (f, e) = tools.chooseFeatures()
  hmm = trainHMM(f, e)
  render(score, hmm)

if __name__ == '__main__':
  test()

  

def render1(score):
  melody = Score(score).melody()
  features = scoremodel.features(melody, None)

  parsetree = structure.parse(melody)
  scorefeatures = scorefeatures.extract(melody)
  deviations = expressionmodel.predictDeviations(melody, parsetree, scorefeatures)
  alignment = Alignment(melody, deviations)
  return alignment.performance(score, deviations)



