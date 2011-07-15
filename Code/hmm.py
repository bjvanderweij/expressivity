# P(Expression|Features)
# P(Ei|Ei-i, ..., Ei-n)
# P(E0, E1, ..., En)
import math, tools

class HMM:

  # Smoothing options: good-turing
  def __init__(self, order=2, smoothing=None):
    self.order = order
    self.smoothing = smoothing

    self.startstate = ('start',)
    self.endstate = ('end',)
    self.repeatstate = ('repeat',)

    self.coincedences = {}
    self.observations = {}
    self.states = []

    self.ngrams = {}
    self.observation_count = 0
    self.ngram_count = 0
    self.lessergrams = {}
    self.lessergram_count = 0
    self.starts = {}
    self.start_count = 0
    # Used for good-turing smoothing:
    self.nr = {}
    # This doesn't really belong here, it is just used as convenient storage
    self.normalizations = []

  def learn(self, observations, states):
    parameters = len(states[0])
    observations = [self.startstate] + observations + [self.endstate]
    states = [self.startstate] + states + [self.endstate]
    for observation, state in zip(observations, states):
      self.coincedences[observation, state] = self.coincedences.get((observation, state), 0) + 1
      self.observations[observation] = self.observations.get((observation), 0) + 1
      self.observation_count += 1
      if not state in self.states and not (state == self.startstate or state == self.endstate):
        self.states.append(state)
    for i in range(len(states)-self.order + 1):
      ngram = []
      lessergram = []
      for offset in range(self.order):
        if states[i+offset] == self.startstate or states[i+offset] == self.endstate:
          ngram.append(states[i+offset])
        else:
          ngram.append(states[i+offset])
      for offset in range(self.order-1):
        if states[i+offset] == self.startstate or states[i+offset] == self.endstate:
          lessergram.append(states[i+offset])
        else:
          lessergram.append(states[i+offset])
        self.ngram_count += 1
        # Add the index of this parameter to the ngram
        self.ngrams[tuple(ngram)] = self.ngrams.get(tuple(ngram), 0) + 1
        self.lessergram_count += 1
        self.lessergrams[tuple(lessergram)] = self.lessergrams.get(tuple(lessergram), 0) + 1
    if self.smoothing=='good-turing':
      for obs in self.observations:
        nr = {}
        for state in self.states:
          if (obs, state) in self.coincedences:
            nr[self.coincedences[obs, state]] = nr.get(self.coincedences[obs, state], 0) + 1
        x,y = [], []
        for n,count in nr.iteritems():
          x.append(math.log(n))
          y.append(count)
        print nr
        # Find a least squares fit to of the frequency counts to nr = a + b*log(x)
        (a,b) = y[0], 0
        if len(x) > 1:
          (a,b) = tools.linear_fit(x,y)
        self.nr[obs] = (a,b)




        

      # Print a table of how much each number of states occurs


  def joint_probability(self, observation, state):
    if not (observation, state) in self.coincedences: return 0.0
    return self.coincedences[observation, state] / float(self.coincedence_count)

  def start_probability(self, state):
    if not state in self.starts: return 0.0
    return self.starts[state] / float(self.start_count)

  def emission_probability(self, state, observation):
    if not (observation, state) in self.coincedences: 
      return 0.0
    return self.coincedences[observation, state] / float(self.observations[observation])

  def transition_probability(self, lessergram, state, verbose=False):
    if self.order == 1: return 1.0
    p = self.ngrams.get(tuple(list(lessergram) + [state]), 0) /  float(self.lessergrams[tuple(lessergram)])
    if verbose:
      print '{0}, {1}, {2}, {3} {4}'.format(tuple(list(lessergram) + [state]), self.ngrams.get(tuple(list(lessergram) + [state]), 0), tuple(lessergram), self.lessergrams.get(tuple(lessergram), 0), p)
    # If this ngram was not found and the following state is the same as the last state (expression remains the same) do not return zero
    # These are the self-loops
    if p==0 and lessergram[len(lessergram)-1] == state:
      minimum = 1 /  float(self.lessergrams[tuple(lessergram)])
      return minimum
    return p

  def max_emission(self, obs):
    states = []
    p = 1.0
    for o in obs:
      probs = [self.emission_probability(state, o) for state in self.states]
      m = max(probs)
      p *= m
      states.append(self.states[probs.index(m)])
    return (p, states)

  def sequence_probability(self, obs, states):
    states = [self.startstate] + states + [self.endstate]
    obs = obs + [self.endstate]
    p = 1.0
    for i in range(len(states)-1):
      cp = self.emission_probability(states[i+1], obs[i]) * self.transition_probability([states[i]], states[i+1])
      #if cp == 0.0:
      #  print '{0}. {1}, {2}'.format(states[i], states[i+1], self.emission_probability(states[i+1], obs[i]))
      p *= cp
    return p


  def print_dptable(self, V):
    print "    ",
    for i in range(len(V)): print "{0}".format("{0}".format(i)),
    print

    for y in V[0].keys():
        print "{0}: ".format(y),
        for t in range(len(V)):
            print "{0}".format("{0}".format(V[t][y])),
        print

  # Source: Wikipedia article on viterbi algorithm
  def viterbi(self, obs):
    # If an observation is not in the corpus we would like either find the nearest observation, or keep using the same expression
    # So what do we do? We could add a special entry for this observation that emission_probabilty propagates to transition_probability
    # Who in turn propagates it to viterbi who uses the last state
    # But this is ugly
    # Better idea: add a specal repeat state and make this the maximum probability for the unfound states! 
    unseen = 0
    for o in obs:
      if not o in self.observations:
        unseen += 1
    print "{0} out of {1} observations do not occur in the corpus!".format(unseen, len(obs))
    obs = obs + [self.endstate]
    V = [{}]
    path = {}

    # Initialize base cases (t == 0)
    for y in self.states:
      V[0][y] = self.transition_probability([self.startstate], y) * self.emission_probability(y, obs[0])
      path[y] = [y]

    # Run Viterbi for t > 0
    for t in range(1,len(obs)):
      V.append({})
      newpath = {}

      for y in self.states + [self.endstate] + [self.repeatstate]:
        if y == self.repeatstate:
          (prob, state) = max([(V[t-1][y0] * self.transition_probability([y0], y0) *\
            self.emission_probability(y, obs[t]), y0) for y0 in self.states])
          V[t][state] = prob
          newpath[state] = path[state] + [state]
        else:
          (prob, state) = max([(V[t-1][y0] * self.transition_probability([y0], y) *\
            self.emission_probability(y, obs[t]), y0) for y0 in self.states])
          V[t][y] = prob
          newpath[y] = path[state] + [y]
          

      # Don't need to remember the old paths
      path = newpath

    #self.print_dptable(V)
    (prob, state) = max([(V[len(obs) - 1][y], y) for y in self.states + [self.endstate]])
    # Exclude the last node from the path (this is the end state that slipped in)
    return (prob, path[state][:-1])

  def storeInfo(self, f):
    out = open(f, 'w')
    out.write('NGRAMS:\n')
    for ngram, value in self.ngrams.iteritems():
      out.write('{0}:\t{1}\n'.format(str(ngram), value))
    out.write('COINCEDENCES:\n')
    for coincedence, value in self.coincedences.iteritems():
      out.write('{0}:\t{1}\n'.format(str(coincedence), value))
    out.close()


# HMM class that assumes independence of every paramater of a state
class HMM_indep(HMM):

  
  def learn(self, observations, states):
    parameters = len(states[0])
    observations = [self.startstate] + observations + [self.endstate]
    states = [self.startstate] + states + [self.endstate]
    for observation, state in zip(observations, states):
      if state == self.startstate or state == self.endstate:
        state = [state for i in range(parameters)]
      for i in range(parameters):
        self.coincedences[i, observation, state[i]] = self.coincedences.get((i, observation, state[i]), 0) + 1
      self.observations[observation] = self.observations.get(observation, 0) + 1
      self.observation_count += 1
      if not state in self.states and not (state[0] == self.startstate or state[0] == self.endstate):
        self.states.append(state)
    for i in range(len(states)-self.order + 1):
      for j in range(parameters):
        ngram = []
        lessergram = []
        for offset in range(self.order):
          if states[i+offset] == self.startstate or states[i+offset] == self.endstate:
            ngram.append(states[i+offset])
          else:
            ngram.append(states[i+offset][j])
        for offset in range(self.order-1):
          if states[i+offset] == self.startstate or states[i+offset] == self.endstate:
            lessergram.append(states[i+offset])
          else:
            lessergram.append(states[i+offset][j])
        self.ngram_count += 1
        # Add the index of this parameter to the ngram
        self.ngrams[tuple([j] + ngram)] = self.ngrams.get(tuple([j] + ngram), 0) + 1
        self.lessergram_count += 1
        self.lessergrams[tuple([j] + lessergram)] = self.lessergrams.get(tuple([j] + lessergram), 0) + 1

  def __str__(self):
    return 'States:\n{0}\nNgrams:\n{1}\nLessergrams:\n{2}'.format(self.states, self.ngrams, self.lessergrams)

  def emission_probability(self, state, observation, smoothing=False):
    p = 1.0
    # This must be the absolute minimum probability
    if state == self.repeatstate:
      return 0.1 / float(self.observation_count)
    if state == self.startstate:
      if observation == self.startstate:
        return 1.0
      else:
        return 0.0
    if state == self.endstate:
      if observation == self.endstate:
        return 1.0
      else:
        return 0.0
    for i in range(len(state)):
      p *= (self.coincedences.get((i, observation, state[i]), 0.0)) / float(self.observations.get(observation, 1))
      if p == 0.0: break
    return p

  def transition_probability(self, lessergram, state, smoothing=None, verbose=False):
    p = 1.0
    #lessergrams = [[v[j] for v in lessergram] for j in len(state)] 
    if state == self.endstate:
      parameters = len(lessergram[len(lessergram)-1])
      state = [self.endstate for i in range(parameters)]
    else:
      parameters = len(state)

    lg = []
    for j in range(parameters):
      if lessergram[0] == self.startstate:
        lg.append([self.startstate] + [v[j] for v in lessergram[1:]])
      else:
        lg.append([v[j] for v in lessergram])

    for i in range(parameters):
      p *= self.ngrams.get(tuple([i] + lg[i] + [state[i]]), 0) / float(self.lessergrams.get(tuple([i] + lg[i]), 1))
      if p == 0.0: break
      if verbose:
        print "P({0}|{1}) = {2} ({3}, {4})".format([i] + lg[i] + [state[i]], [i] + lg[i], p, self.ngrams.get(tuple([i] + lg[i] + [state[i]]), 0), float(self.lessergrams.get(tuple([i] + lg[i]), 1))
)
    # If this ngram was not found and the following state is the same as the last state (expression remains the same) do not return zero
    # These are the self-loops
    if p == 0.0 and lessergram[len(lessergram)-1] == state and smoothing:
      minimum = 1.0
      for i in range(parameters):
        minimum *= 1 / float(self.lessergrams.get(tuple([i] + lg[i]), 1))
      return minimum
    return p

