from typing import List

class Node:
  def __init__(self, tokens: List):
    """
    given a list of tokens, use the first one as the name of the current node
    find the children nodes of the current node
    """
    # get rid of the brackets if exist
    if tokens[0] == '{':
      assert tokens[-1] =='}'
      tokens = tokens[1:-1]

    # the first node must be a valid one  
    assert tokens[0] != '{'

    # the first token is used for the current node
    self.name = tokens[0]
    self.children = []
    remaining_tokens = tokens[1:]

    # find children from the rest of the nodes
    while remaining_tokens:
      closure, remaining_tokens = self.getClosure(self, remaining_tokens)
      self.children.append(Node(closure))


  def getClosure(tokens: List):
    """
    if the first token is '{', return tokens until associated '}'
    else, return the first token
    """
    if not tokens:
      assert False

    # if the first node is not '{', the entire list belongs to one child node
    elif tokens[0] != '{':
      closure = tokens

    # if the first node is '{', the nodes bewteen it and the associated '}' belongs to one child node
    else:
      closure = []
      stack = 0
      for t in tokens:
        closure.append(t)

        if t == '{':
          stack += 1
        elif t == '}':
          stack -= 1
        
        if stack == 0:
          break
      
    remaining_tokens = tokens[len(closure) : ]
    return closure, remaining_tokens

  def dumpRouteString(self):
    if not self.children:
      return self.name
    else:
      route = self.name + ' '
      for i in range(self.children)-1:
        route += '{ ' + self.children[i].dumpRouteString() + '} '
      route += self.children[-1].dumpRouteString() + ' '
      
      return route

  