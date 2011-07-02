class Node:

  def __init__(self, children, parent=None):
    self.children = children
    for child in self:
      child.parent = self

  def generateItems(self):
    for n in self.children:
      yield n

  def __iter__(self):
    return self.generateItems()

  def __len__(self):
    return len(self.children)

  def __contains__(self, c):
    for child in self.children:
      if child is c:
        return True
    return False

  def __getitem__(self, i):
    return self.children[i]

class MultiNode:

  def __init__(self, nodes):
    self.nodes = nodes

  def generateItems(self):
    for n in self.nodes:
      yield n

  def __iter__(self):
    return self.generateItems()

  def __len__(self):
    return len(self.nodes)

  def __contains__(self, n):
    for node in self.nodes:
      if node is n:
        return True
    return False

  def __getitem__(self, i):
    return self.nodes[i]

class Leaf:

  def __init__(self, contents):
    self.contents = contents
