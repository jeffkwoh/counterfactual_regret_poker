import random as rand

from Group19_cfr_utils.Group19_hand_evaluation import get_bucket_number
from Group19_game_state import State
from pypokerengine.players import BasePokerPlayer


class Group19Player(BasePokerPlayer):

  def __init__(self) :
    super(Group19Player, self).__init__()
    strategy_file_path = "Group19_strategy.txt"
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
    info_set = ':'

    num_rounds = state.get_round() + 1

    for i in range(num_rounds) :
      round_community_cards = state.get_round_community_cards(i)
      bucket_number = get_bucket_number(hole_card_chars, round_community_cards)      
      info_set += str(bucket_number) + ':'
      street = state.get_round_street(i)
      action_histories_street = state.get_round_street_action_histories(street)
      for history in action_histories_street :
          action = history['action']
          if action == 'RAISE' :
             info_set += 'r'
          elif action == 'CALL' :
            info_set += 'c'
      if i != num_rounds - 1 :
        info_set += '::'
    
    """ Select the strategy based on current state of the game the agent is at. """
    node_strategy = self.strategy[info_set]
    
    choice = rand.random()
    probability_sum = 0
    num_actions = len(valid_actions)
    for i in range(num_actions):
        action_probability = node_strategy[i]
        if action_probability == 0:
            continue
        probability_sum += action_probability
        if choice < probability_sum:
            return valid_actions[i]['action']
          
    """ Return the last action since it could have not been selected due to floating point error. """
    return valid_actions[num_actions-1]['action']



  def receive_game_start_message(self, game_info):
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    pass

def setup_ai():
  return Group19Player()
