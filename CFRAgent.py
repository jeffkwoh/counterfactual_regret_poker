from pypokerengine.players import BasePokerPlayer
import random as rand
import pprint
import random
import sys

from game_state import State
class CFRAgent(BasePokerPlayer):

  def __init__(self) :
    super(CFRAgent, self).__init__()
    strategy_file_path = "test.txt"
    strategy = {}
    with open(strategy_file_path, 'r') as strategy_file:
        for line in strategy_file:
            if not line.strip() or line.strip().startswith('#'):
                continue
            line_split = line.split(' ')
            strategy[line_split[0]] = [float(probStr) for probStr in line_split[1:4]]
    self.strategy = strategy

  def declare_action(self, valid_actions, hole_card, round_state):
    
    hole_card_chars = hole_card
    community_card_chars = round_state['community_card']

    state = State(round_state, hole_card_chars, community_card_chars)
    info_set = ''

    num_rounds = state.get_round() + 1

    for i in range(num_rounds) :
      bucketNum = get_bucket_number(hole_card_chars, community_card_chars)
      info_set += bucketNum + ':'
      street = state.get_round_street()
      action_histories_street = state.get_round_street_action_histories(street)
      for history in action_histories_street :
          action = history['action']
          if action == 'RAISE' :
             info_set += 'r'
          elif action == 'CALL' :
            info_set += 'c'
      if i != num_rounds - 1 :
        info_set += '::'
    
    node_strategy = self.strategy[info_set]
    
    choice = random.random()
    probability_sum = 0
    for i in range(3):
        action_probability = node_strategy[i]
        if action_probability == 0:
            continue
        probability_sum += action_probability
        if choice < probability_sum:
            return valid_actions[i]
    # Return the last action since it could have not been selected due to floating point error
    return valid_actions[2]



  def receive_game_start_message(self, game_info):
    # print("\n\n")
    # pprint.pprint(game_info)
    # print("---------------------------------------------------------------------")
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    # print("My ID : "+self.uuid+", round count : "+str(round_count)+", hole card : "+str(hole_card))
    # pprint.pprint(seats)
    print("-------------------------------")
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    # print("My ID (round result) : "+self.uuid)
    # pprint.pprint(round_state)
    # print("\n\n")
    # self.round_count = self.round_count + 1
    print("CFRAgent Player")
    pprint.pprint(hand_info)
    print('\n')
    pass

def setup_ai():
  return CFRAgent()
