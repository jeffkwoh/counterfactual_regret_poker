from pypokerengine.players import BasePokerPlayer
import random as rand
import pprint
import random
import sys

from game_state import State
class CFRAgent(BasePokerPlayer):

  def __init__(self) :
    super(CFRAgent, self).__init__()
    strategy = {}
    with open(strategy_file_path, 'r') as strategy_file:
        for line in strategy_file:
            if not line.strip() or line.strip().startswith('#'):
                continue
            line_split = line.split(' ')
            strategy[line_split[0]] = [float(probStr) for probStr in line_split[1:4]]
    self.strategy = strategy

  def declare_action(self, valid_actions, hole_card, round_state):
    
    #TODO need to change the below to hardcoded 52 cards? 
    #According to test.txt, each card is represented from 0-52?
    #I am not sure about this
    suite = {
        'C': 0,
        'D': 13,
        'H': 26,
        'S': 39}
    rank = {
        '2': 0,
        '3': 1,
        '4': 2,
        '5': 3,
        '6': 4,
        '7': 5,
        '8': 6,
        '9': 7,
        'T': 8,
        'J': 9,
        'Q': 10,
        'K': 11,
        'A': 12}

    def convert_card_to_index(card):
        chars = list(card)
        return suite[chars[0]] + rank[chars[1]]

    hole_card_indices = []
    community_card_indices = []

    for card in hole_card:
        hole_card_indices.append(convert_card_to_index(card))
    for card in round_state['community_card']:
        community_card_indices.append(convert_card_to_index(card))

    state = State(round_state, hole_card_indices, community_card_indices)
    info_set = ''
    num_hole_cards = state.get_num_hole_cards()
    info_set += '%s:' % ':'.join([str(state.get_hole_card(i)) for i in range(num_hole_cards)])

    total_board_cards_count = 0
    for round_index in range(state.get_round() + 1):
        new_total_board_cards_count = state.get_total_num_board_cards(round_index)
        if new_total_board_cards_count > total_board_cards_count:
            info_set += ':%s:' % ':'.join(
                [str(state.get_board_card(i))
                    for i in range(total_board_cards_count, new_total_board_cards_count)])
            total_board_cards_count = new_total_board_cards_count

        info_set += ''.join(
            [convert_action_to_str(state.get_action_type(round_index, action_index))
             for action_index in range(state.get_num_actions(round_index))])
    
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
