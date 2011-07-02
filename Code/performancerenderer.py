# these files extract needed features and structural information
import scorefeatures as sf
import structure
# *model contains statistical information
# datahandling files
from score import *
from representation import *
from hmm import *
import database as db
import alignment


def trainHMM(features_set, expression_set):
  hmm = HMM()
  for work in features_set.keys():
    features = features_set[work]
    expression = expression_set[work]
    obs = []
    states = []
    # Select the subset of features that will be used and discretise
    for feature in features:
      # Select subset
      # Discretise
      if feature[3] > 0: f[3] = 1
      if feature[3] < 0: f[3] = -1
      else: f[3] = 0
      obs.append(((f[1], f[2], f[3])
    for parameters in expression:
      # Select subset
      avg_rel_l = p[1]
      avg_artic = p[2]
      avg_tempo = p[3]
      # Discretise
      states.append((avg_rel_l, avg_artic, avg_tempo))
    hmm.learn(obs, states)
  return hmm

def print_dptable(V):
  print "    ",
  for i in range(len(V)): print "%7s" % ("%d" % i),
  print

  for y in V[0].keys():
      print "%.5s: " % y,
      for t in range(len(V)):
          print "%.7s" % ("%f" % V[t][y]),
      print

# Source: Wikipedia article on viterbi algorithm
def viterbi(obs, hmm):
  V = [{}]
  path = {}

  # Initialize base cases (t == 0)
  for y in hmm.states:
      V[0][y] = hmm.start_probability(y) * hmm.emission_probability(y, obs[0])
      path[y] = [y]

  # Run Viterbi for t > 0
  for t in range(1,len(obs)):
      V.append({})
      newpath = {}

      for y in hmm.states:
          (prob, state) = max([(V[t-1][y0] * hmm.transition_probability(y0, y) *\
              hmm.emission_probability(y, obs[t]), y0) for y0 in hmm.states])
          V[t][y] = prob
          newpath[y] = path[state] + [y]

      # Don't need to remember the old paths
      path = newpath

  print_dptable(V)
  (prob, state) = max([(V[len(obs) - 1][y], y) for y in states])
  return (prob, path[state])

def render(score, hmm):
  melodyscore = Score(score).melody()
  melody = tools.parseScore(melodyscore)
  # Segmentate the the score
  onset = structure.groupings(structure.list_to_tree(structure.first_order_tree(structure.onset, melody, 0.1)), 1)
  # Extract scorefeatures
  observations = sf.vanDerWeijFeatures(melodyscore, onset) 
  # Find the best expressive explanation for these features
  expression = viterbi(observations, hmm)[1]

  seq = Sequencer()
  seq.play(perform.vanDerWeijPerformSimple(a.score, melodyscore, onset, expression, bpm=a.deviations.bpm, converter=melody))
  
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



