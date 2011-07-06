# P(Expression|Features)
# P(Ei|Ei-i, ..., Ei-n)
# P(E0, E1, ..., En)


class HMM:

  def __init__(self, order=2):
    self.order = order

    self.coincedences = {}
    self.observations = {}
    self.states = []

    self.ngrams = {}
    self.coincedence_count = 0
    self.ngram_count = 0
    self.lessergrams = {}
    self.lessergram_count = 0
    self.starts = {}
    self.start_count = 0
    self.startstate = ('start',)
    self.endstate = ('end',)
    # This doesn't really belong here, it is just used as convenient storage
    self.normalizations = []

  def learn(self, observations, states):
    parameters = len(states[0])
    observations = [self.startstate] + observations + [self.endstate]
    states = [self.startstate] + states + [self.endstate]
    for observation, state in zip(observations, states):
      if state == self.startstate or state == self.endstate:
        state = [state for i in range(parameters)]
      for i in range(parameters):
        self.coincedences[i, observation, state[i]] = self.coincedences.get((i, observation, state[i]), 0) + 1
      self.observations[observation] = self.observations.get((i, observation), 0) + 1
      if not state in self.states and not (state[0] == self.startstate or state[0] == self.endstate):
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

  def joint_probability(self, observation, state):
    if not (observation, state) in self.coincedences: return 0.0
    return self.coincedences[observation, state] / float(self.coincedence_count)

  def start_probability(self, state):
    if not state in self.starts: return 0.0
    return self.starts[state] / float(self.start_count)

  def emission_probability(self, state, observation):
    if not (observation, state) in self.coincedences: return 0.0
    return self.coincedences[observation, state] / float(self.observations[observation])

  def transition_probability(self, lessergram, state, verbose=False):
    if verbose:
      print '{0}, {1}, {2}, {3}'.format(tuple(list(lessergram) + [state]), self.ngrams.get(tuple(list(lessergram) + [state]), 0), tuple(lessergram), self.lessergrams.get(tuple(lessergram), 0))
    if self.order == 1: return 1.0
    if not tuple(list(lessergram) + [state]) in self.ngrams: return 0.0
    return self.ngrams[tuple(list(lessergram) + [state])] /  float(self.lessergrams[tuple(lessergram)])

  def print_dptable(self, V):
    print "    ",
    for i in range(len(V)): print "{0}".format("{0}".format(i)),
    print

    for y in V[0].keys():
        print "{0}: ".format(y),
        for t in range(len(V)):
            print "{0}".format("{0}".format(V[t][y])),
        print

  def max_emission(self, obs):
    states = []
    p = 1.0
    for o in obs:
      probs = [self.emission_probability(state, o) for state in self.states]
      m = max(probs)
      if m == 0.0:
        print o
      p *= m
      states.append(self.states[probs.index(m)])
    return (p, states)

  def sequence_probability(self, obs, states):
    states = [self.startstate] + states + [self.endstate]
    obs = obs + [self.endstate]
    p = 1.0
    for i in range(len(states)-2):
      cp = self.emission_probability(states[i+1], obs[i]) * self.transition_probability([states[i]], states[i+1])
      if cp == 0.0:
        print '{0}. {1}, {2}'.format(states[i], states[i+1], self.emission_probability(states[i+1], obs[i]))
      p *= cp
    return p


  # Source: Wikipedia article on viterbi algorithm
  def viterbi(self, obs):
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

      for y in self.states:
        #print [self.transition_probability(y0, y) for y0 in self.states]
        (prob, state) = max([(V[t-1][y0] * self.transition_probability([y], y0) *\
          self.emission_probability(y, obs[t]), y0) for y0 in self.states])
        V[t][y] = prob
        newpath[y] = path[state] + [y]

      # Don't need to remember the old paths
      path = newpath

    #self.print_dptable(V)
    (prob, state) = max([(V[len(obs) - 1][y], y) for y in self.states])
    return (prob, path[state])

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
      self.observations[observation] = self.observations.get((i, observation), 0) + 1
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

  def joint_probability(self, observation, state):
    if not (observation, state) in self.coincedences: return 0.0
    return self.coincedences[observation, state] / float(self.coincedence_count)

  def emission_probability(self, state, observation):
    p = 1.0
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
      p *= self.coincedences.get((i, observation, state[i]), 0.0) / float(self.observations.get(observation, 1))
    return p

  def transition_probability(self, lessergram, state, verbose=False):
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
      if verbose:
        print "P({0}|{1}) = {2} ({3}, {4})".format([i] + lg[i] + [state[i]], [i] + lg[i], p, self.ngrams.get(tuple([i] + lg[i] + [state[i]]), 0), float(self.lessergrams.get(tuple([i] + lg[i]), 1))
)
    return p

