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
    return self.coincedences[observation, state] / float(self.coincedence_count)

  def start_probability(self, state):
    return self.starts[state] / float(self.start_count)

  def emission_probability(self, state, observation):
    return self.coincedences[observation, state] / float(self.observations[observation])

  def transition_probability(self, lessergram, state):
    return self.ngrams[tuple(lessergram + [state])] /  float(lessergrams[tuple(lessergram)])
