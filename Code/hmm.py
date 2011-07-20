# P(Expression|Features)
# P(Ei|Ei-i, ..., Ei-n)
# P(E0, E1, ..., En)
import math, tools

class HMM:

  # Smoothing options: good-turing
  def __init__(self, order=2, smoothing=None):
    # Order is a relic from when I had the illusion of making this class generic
    # Now it's just bigrams
    self.order = order
    self.smoothing = smoothing
    print self.smoothing

    self.startstate = ('start',)
    self.endstate = ('end',)
    self.repeatstate = ('repeat',)

    self.coincedences = {}
    self.observations = {}
    self.states = {}

    self.bigrams = {}
    self.observation_count = 0
    self.bigram_count = 0
    self.unigrams = {}
    self.unigram_count = 0
    self.starts = {}
    self.start_count = 0
    # Used for good-turing smoothing:
    self.nr = None
    self.unseen_bigrams = 0
    self.N = 0
    self.unseen_coincedences = 0
    # This doesn't really belong here, it is just used as convenient storage
    self.normalizations = []

    self.state_counts = {}

  def learn(self, observations, states):
    parameters = len(states[0])
    observations = [self.startstate] + observations + [self.endstate]
    states = [self.startstate] + states + [self.endstate]
    for observation, state in zip(observations, states):
      self.coincedences[observation, state] = self.coincedences.get((observation, state), 0) + 1
      self.observations[observation] = self.observations.get((observation), 0) + 1
      self.observation_count += 1
      # We allow start and end state to be in the statecounts
      self.states[state] = self.states.get(state, 0) + 1
    for i in range(len(states)-self.order + 1):
      bigram = []
      unigram = []
      for offset in range(self.order):
        if states[i+offset] == self.startstate or states[i+offset] == self.endstate:
          bigram.append(states[i+offset])
        else:
          bigram.append(states[i+offset])
      for offset in range(self.order-1):
        if states[i+offset] == self.startstate or states[i+offset] == self.endstate:
          unigram.append(states[i+offset])
        else:
          unigram.append(states[i+offset])
        self.bigram_count += 1
        # Add the index of this parameter to the bigram
        self.bigrams[tuple(bigram)] = self.bigrams.get(tuple(bigram), 0) + 1
        self.unigram_count += 1
        self.unigrams[tuple(unigram)] = self.unigrams.get(tuple(unigram), 0) + 1

  # Initialize Good-Turing smoothing
  def new(self):
    self.nr = {}
    unseen = 0 #self.unseen_coincedences
    for state in self.states:
      for obs in self.observations:
        if (obs, state) in self.coincedences:
          self.nr[self.coincedences[obs, state]] = self.nr.get(self.coincedences[obs, state], 0) + 1
        else: unseen += 1
    self.nr[0] = unseen + len(self.states) * self.unseen_coincedences
    self.N = sum([self.smoothed_frequency_count(None, i) for i in range(0, max(self.nr.keys())+1)])

    
  def init_GT_smoothing(self):
    self.nr = {}
    undef = 0
    for state in self.states:
      nr = {}
      unseen = self.unseen_coincedences
      for obs in self.observations:
        if (obs, state) in self.coincedences:
          nr[self.coincedences[obs, state]] = nr.get(self.coincedences[obs, state], 0) + 1
        else: unseen += 1

      # We can't use these
      if len(nr) == 1:
        self.nr[state] = 'undefined'
        undef += 1
        continue
      # Things that never occur
      # Variable should be set when decoding is called
      x, y = [], []
      for n,count in nr.iteritems():
        x.append(math.log(n))
        y.append(math.log(count))
      if len(x) < 2:
        x.append(math.log(n+1))
        y.append(math.log(1))
      #x.append(math.log(max(nr.keys())+100))
      #y.append(1)
      #nr[0] = self.unseen_coincedences * len(self.states)
      #print state, x, y, nr
      # Find a least squares fit to of the frequency counts to nr = a + b*log(x)
      #(a,b) = y[0], 0
      #if len(x) > 1:
      (a,b) = tools.linear_fit(x,y)
      #if len(nr) == 1:
    #    print '{0} unseen: {1} Nr: {2}'.format(state, unseen, nr)
      if len(nr) > 5:
        import matplotlib.pyplot as plt
        print [nr[i] for i in nr.keys()]
        print [math.exp(a+b*math.log(i+1)) for i in nr.keys()]
        #plt.plot([1] + [i+1 for i in sorted(nr.keys())], [math.exp(i) for i in y])
        #plt.show()
        #raw_input("Press enter to continue...")
        #plt.plot(range(1, 1000), [math.exp(a+b*math.log(i)) for i in range(1, 1000)])
        #raw_input("Press enter to continue...")
      self.nr[state] = (a,b,unseen)
    print "Smoothing disabled on {0} out of {1} states".format(undef, len(self.states))

  def testModel(self):
    print "Sum of smoothed probabilities of all coincedences starting with:"
    #for state in self.states:
    #  print self.transition_probability([self.startstate], state),
    #  print self.emission_probability(state, self.observations.values()[2])
    for state in self.states:
      p = sum([self.emission_probability(state, obs) for obs in self.observations])
      #if p > 2 or p < 0:
      #print 'Emission\t{0}: {1}'.format(state, p)
      N = self.smoothed_frequency_count(state, 0)
      N1 = self.smoothed_frequency_count(state, 1)
      #print 'Zero mass: {0}, Unseen: {1} N1: {2} Observations: {3}'.format(N1/N, N, N1, len(self.observations) + self.unseen_coincedences)
      p = sum([self.transition_probability([state], state1) for state1 in self.states])
      #print 'Transition\t{0}: {1}'.format(state, p)
    #exit(0)

  # Turing estimate
  def smoothed_frequency_count(self, state, c):
    if self.nr[state] == 'undefined':
      return c
    (a,b,unseen) = self.nr[state]
    if c == 0: return unseen
    return math.exp(a + b*math.log(c+1))
  
  # See Jurafsky and Martin
  def smoothed_count(self, state, c, k=5):
    if c > k: return c
    if self.nr[state] == 'undefined': return c
    Nc = float(self.smoothed_frequency_count(state, c))
    Nc1 = float(self.smoothed_frequency_count(state, c+1)) 
    Nk1 = float(self.smoothed_frequency_count(state, k+1))
    N1 = float(self.smoothed_frequency_count(state, 1)) 
    #print (1 - (k+1) * Nk1/N1), Nk1, N1, c
    return ((c+1)*Nc1/Nc - c*(k+1)*Nk1/N1)/(1 - (k+1)*Nk1/N1)
    #return (c+1) * Nc1/Nc
    

  def emission_probability(self, state, observation):
    N = float(self.states[state])
    if self.smoothing=='good-turing' and self.unseen_coincedences > 0:
      if not self.nr:
        self.init_GT_smoothing()
      c = self.coincedences.get((observation, state), 0)
      if c == 0:
        if self.nr[state] == 'undefined':
          return 0
        # 1/unseen * N_1/N
        #print (1/float(self.smoothed_frequency_count(state, 0))) * (self.smoothed_frequency_count(state, 1)/N)
        return (1/float(self.smoothed_frequency_count(state, 0))) * (self.smoothed_frequency_count(state, 1)/N)
      else:
        #print 'P({0}|{1}) = {2}, c={3} c*={4} '.format(observation, state, self.smoothed_count(state, c) / N, c, self.smoothed_count(state, c))
        return self.smoothed_count(state, c) / N
    else:
      return self.coincedences.get((observation, state), 0) / N 


  def transition_probability(self, unigram, state, verbose=False):
    if self.order == 1: return 1.0
    if unigram[0] == self.endstate or unigram[0] == self.repeatstate: return 0.0
    p = self.bigrams.get(tuple(list(unigram) + [state]), 0) /  float(self.unigrams[tuple(unigram)])
    # If this bigram was not found and the following state is the same as the last state (expression remains the same) do not return zero
    # These are the self-loops
    #if p==0 and unigram[len(unigram)-1] == state:
    #  minimum = 1 /  float(self.unigrams[tuple(unigram)])
    #  return minimum
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
    self.unseen_coincedences = unseen
    self.testModel()
    if unseen > 0:
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

      for y in self.states.keys() + [self.endstate]:
        (prob, state) = max([(V[t-1][y0] * self.transition_probability([y0], y) *\
          self.emission_probability(y, obs[t]), y0) for y0 in self.states])
        V[t][y] = prob
        newpath[y] = path[state] + [y]
          

      # Don't need to remember the old paths
      path = newpath

    #self.print_dptable(V)
    #(prob, state) = max([(V[len(obs) - 1][y], y) for y in self.states.keys() + [self.endstate]])
    (prob, state) = V[len(obs)-1][self.endstate], self.endstate
    # Exclude the last node from the path (this is the end state that slipped in)
    return (prob, path[state][:-1])

  def storeInfo(self, f):
    out = open(f, 'w')
    out.write('NGRAMS:\n')
    for bigram, value in self.bigrams.iteritems():
      out.write('{0}:\t{1}\n'.format(str(bigram), value))
    out.write('COINCEDENCES:\n')
    for coincedence, value in self.coincedences.iteritems():
      out.write('{0}:\t{1}\n'.format(str(coincedence), value))
    out.close()


# HMM class that assumes independence of every paramater of a state
class HMM_indep(HMM):

  # Assume independent score features
#  def learn(self, observations, states):
#    parameters = len(observations[0])
#    observations = [self.startstate] + observations + [self.endstate]
#    states = [self.startstate] + states + [self.endstate]
#    for observation, state in zip(observations, states):
#      for i in range(parameters):
#        self.coincedences[i, observation[i], state] = self.coincedences.get((i, observation[i], state), 0) + 1
#        self.observations[i, observation[i]] = self.observations.get((i, observation[i]), 0) + 1
#        self.observation_count += 1
#      self.states[state] = self.states.get(state, 0) + 1
#    for i in range(len(states)-self.order + 1):
#      bigram = []
#      unigram = []
#      for offset in range(self.order):
#        if states[i+offset] == self.startstate or states[i+offset] == self.endstate:
#          bigram.append(states[i+offset])
#        else:
#          bigram.append(states[i+offset])
#      for offset in range(self.order-1):
#        if states[i+offset] == self.startstate or states[i+offset] == self.endstate:
#          unigram.append(states[i+offset])
#        else:
#          unigram.append(states[i+offset])
#      self.bigram_count += 1
#      # Add the index of this parameter to the bigram
#      self.bigrams[tuple(bigram)] = self.bigrams.get(tuple(bigram), 0) + 1
#      self.unigram_count += 1
#      self.unigrams[tuple(unigram)] = self.unigrams.get(tuple(unigram), 0) + 1

  # Assume independent state parameters
  def learn(self, observations, states):
    parameters = len(states[0])
    observations = [self.startstate] + observations + [self.endstate]
    states = [self.startstate] + states + [self.endstate]
    for observation, state in zip(observations, states):
      if state == self.startstate or state == self.endstate:
        state = tuple([tuple(state) for i in range(parameters)])
      for i in range(parameters):
        self.coincedences[i, observation, state[i]] = self.coincedences.get((i, observation, state[i]), 0) + 1
        self.state_counts[i, state[i]] = self.state_counts.get((i, state[i]), 0) + 1
      self.observations[observation] = self.observations.get(observation, 0) + 1
      self.states[state] = self.states.get(state, 0) + 1
      self.observation_count += 1
    for i in range(len(states)-self.order + 1):
      for j in range(parameters):
        bigram = []
        unigram = []
        for offset in range(self.order):
          if states[i+offset] == self.startstate or states[i+offset] == self.endstate:
            bigram.append(states[i+offset])
          else:
            bigram.append(states[i+offset][j])
        for offset in range(self.order-1):
          if states[i+offset] == self.startstate or states[i+offset] == self.endstate:
            unigram.append(states[i+offset])
          else:
            unigram.append(states[i+offset][j])
        self.bigram_count += 1
        # Add the index of this parameter to the bigram
        self.bigrams[tuple([j] + bigram)] = self.bigrams.get(tuple([j] + bigram), 0) + 1
        self.unigram_count += 1
        self.unigrams[tuple([j] + unigram)] = self.unigrams.get(tuple([j] + unigram), 0) + 1

  # Initialize Good-Turing smoothing
  def init_GT_smoothing(self):
    self.nr = {}
    for i, state in self.state_counts:
      # Coincedence frequency counts
      c_nr = {}
      # and bigram frequency counts
      bigram_nr = {}
      for obs in self.observations:
        if (i, obs, state) in self.coincedences:
          c_nr[self.coincedences[i, obs, state]] = c_nr.get(self.coincedences[i, obs, state], 0) + 1
      unseen_bigrams = 0
      for j, state1 in self.state_counts:
        if j != i: continue
        if (i, state, state1) in self.bigrams:
          bigram_nr[self.bigrams[i, state, state1]] = bigram_nr.get(self.bigrams[i, state, state1], 0) + 1
        else:
          unseen_bigrams += 1

      x,y = [1], [self.unseen_coincedences * len(self.states)]
      for n,count in c_nr.iteritems():
        x.append(math.log(n+1))
        y.append(count)
      # Find a least squares fit to of the frequency counts to nr = a + b*log(x)
      # The fitted functions sometimes do dive under zero! (Which doesn't seem to be good)
      # By adding a very large value that is zero we sort of solve this?
      #(a,b) = y[0], 0
      x.append(math.log(100000))
      y.append(0)
      c_nr[0] = self.unseen_coincedences * len(self.states)
      (a,b) = tools.linear_fit(x,y)
      self.nr[(i, state), 'coincedence'] = (a,b, c_nr)

      p,q = [0], [unseen_bigrams]
      for n,count in bigram_nr.iteritems():
        p.append(math.log(n))
        q.append(count+1)
      # Find a least squares fit to of the frequency counts to nr = a + b*log(x)
      # The fitted functions sometimes do dive under zero!
      #(a,b) = y[0], 0
      p.append(math.log(100))
      q.append(0)
      bigram_nr[0] = unseen_bigrams
      #print '{0}: {1}'.format((i, state), bigram_nr)
      (a,b) = tools.linear_fit(p,q)
      self.nr[(i, state), 'bigram'] = (a,b, bigram_nr)

  def __str__(self):
    return 'States:\n{0}\nNgrams:\n{1}\nLessergrams:\n{2}'.format(self.states, self.bigrams, self.unigrams)

  def testModel(self):
    print "Sum of smoothed probabilities of all coincedences starting with:"
    for state in self.states:
      p = sum([self.emission_probability(state, obs) for obs in self.observations])
      print 'E{0}: {1}'.format(state, p)
      p = sum([self.transition_probability([state], state1) for state1 in self.states])
      print 'T{0}: {1}'.format(state, p)



  def smoothed_frequency_count(self, state, c, type='coincedence'):
    if not self.nr:
      self.init_GT_smoothing()
    (a,b, nr) = self.nr[state, type]
    # If we cannot find this frequency we back off to a logarithmic fit
    # But perhaps interpolation  is better?
    if c in nr:
      smoothed = nr[c]
    else:
      smoothed = a + b*math.log(c)
    return smoothed

  # See Jurafsky and Martin
  def smoothed_count(self, state, c, type='coincedence', k=5):
    # This is apparently safe 
    #if r == 1: r = 0
    if c > k: return c
    Nc = float(self.smoothed_frequency_count(state, (c+1), type))
    Nc1 = float(self.smoothed_frequency_count(state, c, type)) 
    Nk1 = float(self.smoothed_frequency_count(state, (k+1), type))
    N1 = float(self.smoothed_frequency_count(state, 1, type)) 
    return ((c+1)*Nc1/Nc - c*(k+1)*Nk1/N1)/(1 - (k+1)*Nk1/N1)

  def emission_probability(self, state, observation):
    p = 1.0
    if self.smoothing=='good-turing' and self.unseen_coincedences > 0:
      for i in range(len(state)):
        p *= self.smoothed_count((i, state[i]), self.coincedences.get((i, observation, state[i]), 0)) /\
            float(self.state_counts[i, state[i]] + self.unseen_coincedences * len(self.state_counts))
      return p
    for i in range(len(state)):
      p *= (self.coincedences.get((i, observation, state[i]), 0.0)) / float(self.state_counts.get(state[i]))
      if p == 0.0: break
    return p

  def transition_probability(self, unigram, state, verbose=False):
    p = 1.0
    prevstate = unigram[0]

    if prevstate[0] == self.endstate: 
      return 0.0

    if prevstate == self.startstate:
      prevstate = [self.startstate for i in range(len(state))]

    for i in range(len(state)):
      if self.smoothing == 'good-turing':
        (a,b,nr) = self.nr[(i, prevstate[i]), 'bigram']
        unseen = nr[0]
        p *= self.smoothed_count((i, prevstate[i]), self.bigrams.get(tuple([i] + [prevstate[i]] + [state[i]]), 0), 'bigram') /\
          float(self.state_counts.get(tuple([i] + [prevstate[i]])) + unseen)
      else:
        p *= self.bigrams.get(tuple([i] + [lg[i]] + [state[i]]), 0) /\
          float(self.state_counts.get(tuple([i] + [prevstate[i]])))
      #print "P({0}|{1}) = {2} ({3}, {4}) smoothed: ({5})".format(\
      #    [i] + [prevstate[i]] + [state[i]],\
      #    [i] + [prevstate[i]],\
      #    p,\
      #    self.bigrams.get(tuple([i] + [prevstate[i]] + [state[i]]), 0),\
      #    float(self.state_counts.get(tuple([i] + [prevstate[i]]), 1)),\
      #    self.smoothed_count((i, prevstate[i]), self.bigrams.get(tuple([i] + [prevstate[i]] + [state[i]]), 0), 'bigram'))
    return p

