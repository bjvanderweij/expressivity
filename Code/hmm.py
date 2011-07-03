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

  def learn(self, observations, states):
    self.starts[states[0]] = self.starts.get(states[0], 0) + 1
    self.start_count += 1
    for observation, state in zip(observations, states):
      self.coincedences[observation, state] = self.coincedences.get((observation, state), 0) + 1
      self.coincedence_count += 1
      self.observations[observation] = self.observations.get(observation, 0) + 1
      self.states.append(state)
    for i in range(len(states)-self.order):
      ngram = []
      lessergram = []
      for j in range(self.order):
        ngram.append(states[i+j])
      for j in range(self.order-1):
        lessergram.append(states[i+j])
      self.ngram_count += 1
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

  def transition_probability(self, lessergram, state):
    if not tuple(list(lessergram) + [state]) in self.ngrams: return 0.0
    return self.ngrams[tuple(list(lessergram) + [state])] /  float(lessergrams[tuple(lessergram)])

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
    V = [{}]
    path = {}

    # Initialize base cases (t == 0)
    for y in self.states:
      V[0][y] = self.start_probability(y) * self.emission_probability(y, obs[0])
      path[y] = [y]

    # Run Viterbi for t > 0
    for t in range(1,len(obs)):
      V.append({})
      newpath = {}

      for y in self.states:
        (prob, state) = max([(V[t-1][y0] * self.transition_probability(y0, y) *\
          self.emission_probability(y, obs[t]), y0) for y0 in self.states])
        V[t][y] = prob
        newpath[y] = path[state] + [y]

      # Don't need to remember the old paths
      path = newpath

    self.print_dptable(V)
    (prob, state) = max([(V[len(obs) - 1][y], y) for y in self.states])
    return (prob, path[state])

