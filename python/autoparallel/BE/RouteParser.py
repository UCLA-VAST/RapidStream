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
      closure, remaining_tokens = self.getClosure(remaining_tokens)
      self.children.append(Node(closure))


  def getClosure(self, tokens: List):
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
      for i in range(len(self.children)-1):
        route += '{ ' + self.children[i].dumpRouteString() + ' } '
      route += self.children[-1].dumpRouteString()
      
      return route

def compareRouteString(str1, str2):
  token_list_1 = [t for t in str1.split() if t]
  token_list_2 = [t for t in str2.split() if t]
  len1 = len(token_list_1)
  len2 = len(token_list_2)
  for i in range(min(len1, len2)):
    print(token_list_1[i] == token_list_2[i], token_list_1[i], token_list_2[i])

if __name__ == '__main__':
  test_input = '{ CLK_BUFGCE_9_CLK_OUT CLK_CMT_MUX_16_ENC_2_CLK_OUT CLK_CMT_MUX_2TO1_19_CLK_OUT CLK_HROUTE_0_2 CLK_HROUTE_L2 CLK_HROUTE_L2 CLK_CMT_MUX_3TO1_2_CLK_OUT CLK_VROUTE_BOT CLK_CMT_DRVR_TRI_ESD_3_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_2_CLK_OUT CLK_VROUTE_BOT CLK_CMT_DRVR_TRI_ESD_2_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP { CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B { CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_BUFCE_ROW_FSR_0_CLK_IN CLK_BUFCE_ROW_FSR_0_CLK_OUT CLK_TEST_BUF_SITE_1_CLK_IN } CLK_BUFCE_ROW_FSR_0_CLK_IN CLK_BUFCE_ROW_FSR_0_CLK_OUT CLK_TEST_BUF_SITE_1_CLK_IN } CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_BUFCE_ROW_FSR_0_CLK_IN CLK_BUFCE_ROW_FSR_0_CLK_OUT CLK_TEST_BUF_SITE_1_CLK_IN }'
  tokens = [t for t in test_input.split() if t]
  tree = Node(tokens)

  rebuild_tree = '{ ' + tree.dumpRouteString() + ' }'
  print(test_input == rebuild_tree)
