import copy
import pprint

from pypokerengine.utils.card_utils import (estimate_hole_card_win_rate,
                                            gen_cards)


class State:
    
    """
    This class feeds information to our poker agent based on the current game state.
    """

    def __init__(self, round_state, hole_card_indices, community_card_indices):
        self._round_state = round_state
        self.hole_cards = hole_card_indices
        self.community_cards = community_card_indices
        self.p0_uuid = round_state['seats'][0]['uuid']
        self.p1_uuid = round_state['seats'][1]['uuid']
        self.street = self._round_state['street']
        self.prev_history = ''
        self.new_round_state = copy.deepcopy(self._round_state)
        
        self.round_num = {
            'preflop' : 0,
            'flop' : 1,
            'turn' : 2,
            'river' : 3
        }

        self.num_round = {
            0 : 'preflop',
            1 : 'flop',
            2 : 'turn',
            3 : 'river'
        }

        self.round_num_board_cards = {
            'preflop' : 0,
            'flop' : 3,
            'turn' : 4,
            'river' : 5
        }

        self.new_round_state['preflop_raises'] = 0
        self.new_round_state['flop_raises'] = 0
        self.new_round_state['turn_raises'] = 0
        self.new_round_state['river_raises'] = 0
        self.new_round_state['p0_raises'] = 0
        self.new_round_state['p1_raises'] = 0
        self.new_round_state['current_street_raises'] = {}
        self.new_round_state['prev_history'] = {}
        self.new_round_state['p0_prev_amount'] = 0
        self.new_round_state['p1_prev_amount'] = 0
        eventsorder= ['preflop', 'flop', 'turn', 'river','showdown']
        for street, street_history in sorted(round_state['action_histories'].items(), key = lambda i : eventsorder.index(i[0])):
            for ply in street_history:
                if ply['action'] == 'RAISE':
                    # Add raises to appropriate street
                    if street == 'preflop':
                        if 'preflop_raises' in self.new_round_state :
                            self.new_round_state['preflop_raises'] += 1
                        else :    
                            self.new_round_state['preflop_raises'] = 1
                    elif street == 'flop':
                        if 'flop_raises' in self.new_round_state :
                            self.new_round_state['flop_raises'] += 1
                        else :    
                            self.new_round_state['flop_raises'] = 1
                    elif street == 'turn':
                        if 'turn_raises' in self.new_round_state :
                            self.new_round_state['turn_raises'] += 1
                        else :    
                            self.new_round_state['turn_raises'] = 1
                    else:  # last street is river
                        if 'river_raises' in self.new_round_state :
                            self.new_round_state['river_raises'] += 1
                        else :    
                            self.new_round_state['river_raises'] = 1

                    # Add raises to appropriate player
                    if ply['uuid'] == self.p0_uuid:
                        if 'p0_raises' in self.new_round_state :
                            self.new_round_state['p0_raises'] += 1
                        else :    
                            self.new_round_state['p0_raises'] = 1
                        
                        # Add latest amount of p0 to p0_prev_amount
                        self.new_round_state['p0_prev_amount'] = ply['amount']
                    else:
                        if 'p1_raises' in self.new_round_state :
                            self.new_round_state['p1_raises'] += 1
                        else :    
                            self.new_round_state['p1_raises'] = 1

                        # Add latest amount of p1 to p1_prev_amount
                        self.new_round_state['p1_prev_amount'] = ply['amount']

                    # Increment current street raises
                    # If street is not in current_street_raises attribute, it means that the street has changed and must changed curr_street_raises accordingly
                    if 'current_street_raises' in self.new_round_state :
                        if street not in self.new_round_state['current_street_raises'] :
                            self.new_round_state['current_street_raises'] = {street : 1}
                        else :
                            self.new_round_state['current_street_raises'][street] += 1
                    else :
                        self.new_round_state['current_street_raises'] = {street : 1}

                self.new_round_state['prev_history'] = ply
                self.prev_history = ply

            
            # Need to account for when the street has changed but the action history in that street is still zero
            if 'current_street_raises' in self.new_round_state :
                if street not in self.new_round_state['current_street_raises'] and len(street_history) == 0 :
                    self.new_round_state['current_street_raises'] = {street : 0}
  

        self.prev_history = self.new_round_state['prev_history']
        self.current_player = self._round_state['next_player']
        self.p0_stack = self._round_state['seats'][0]['stack']
        self.p1_stack = round_state['seats'][1]['stack']

    def get_round_community_cards(self, round) :
        """Returns a list of commuunity cards based on that round.
        
        Returns:
            int: Returns a list of commuunity cards based on that round.
        """
        if round == 0 :
            return []
        else :
            len_num_cards = 2 + round
            return self.community_cards[0:len_num_cards]
        
    def get_num_hole_cards(self) :
        """Returns number of hole cards each player receives at the beginning of the game.
        
        Returns:
            int: Number of hole cards each player receives at the beginning of the game.
        """
        return len(self.hole_card_indices)

    def get_hole_card(self, card_index) :
        """Returns player's hole card
        Args:
            player_index (int): Index of the player.
            card_index (int): Index of the hole card.
        Returns:
            Hole card of given player on given index.
        Raises:
            ValueError: When card_index is greater or equal
                        to number of hole cards in the game.
        """
        return self.hole_cards[card_index]

    def get_round(self) :
        """Returns index of the current round of the game.
        Returns:
            int: Index of the current round of the game.
        """

        return self.round_num[self.street]

    def get_total_num_board_cards(self, round_index) :
        """Returns total number of board cards that are on the board in given round.
    
        Args:
            round_index (int): Index of the round
        Returns:
            int: Total number of board cards that are on the board in given round.
        Raises:
            ValueError: When round_index is greater or equal
                        to number of rounds in the game.
        """

        return self.round_num_board_cards[self.round_num[round_index]]

    def get_board_card(self, card_index) : 
        """Returns board card.
        Args:
            card_index (int): Index of the board card.
        Returns:
            Board card on given index.
        Raises:
            ValueError: When card_index is greater or equal
                        to number of board cards in current
                        round.
        """
        return self.community_cards[card_index]

    def get_action_type(self, round_index, action_index) : 
        """Returns type of action on given index taken in given round.
        Args:
            round_index (int): Index of the round.
            action_index (int): Index of the action.
        Returns:
            ActionType: Action type for given action in given round.
        Raises:
            ValueError: When round_index is greater or equal
                        to number of rounds in the game so far.
            ValueError: When action_index is greater or equal
                        to number of actions in given round.
        """

        action_histories = self.get_action_histories()
        street = self.num_round[round_index]
        street_action_history = action_histories[street]
        return street_action_history[action_index]

    def get_num_actions(self, round_index) :
        """Returns number of actions in given round.
        Args:
            round_index (int): Index of the round.
        Returns:
            int: Number of actions in given round.
        Raises:
            ValueError: When round_index is greater or equal
                        to number of rounds in the game so far.
        """
        
        action_histories = self.get_action_histories()
        street = self.num_round[round_index]
        street_action_history = action_histories[street]
        return len(street_action_history)

    def get_round_street(self, index) :
        """
        Returns the round street based on index value
        """

        return self.num_round[index]

    def get_round_street_action_histories (self, street) :
        return self._round_state['action_histories'][street]   

    def get_action_histories(self) :
        return self._round_state['action_histories']

    def get_new_round_state(self) :
        return self.new_round_state

    def get_preflop_raises (self) :
        return self.new_round_state['preflop_raises']

    def get_flop_raises (self) :
        return self.new_round_state['flop_raises']

    def get_turn_raises (self) :
        return self.new_round_state['turn_raises']

    def get_river_raises (self) :
        return self.new_round_state['river_raises']    

    def get_p0_raises (self) :
        return self.new_round_state['p0_raises']

    def get_p1_raises (self) :
        return self.new_round_state['p1_raises']   

    def get_current_street_raises (self) :
        return self.new_round_state['current_street_raises'][self.street]   

    def get_prev_history (self) :
        return self.new_round_state['prev_history']   

    def get_p0_prev_amount (self) :
        return self.new_round_state['p0_prev_amount']    

    def get_p1_prev_amount (self) :
        return self.new_round_state['p1_prev_amount']  

    def get_current_player (self) :
        return self.current_player

    def get_p0_stack (self) :
        return self.p0_stack

    def get_p1_stack (self) :
        return self.p1_stack   
    
    def get_main_pot(self) :
        return self.new_round_state['pot']['main']['amount']

    def get_side_pots(self) :
        return self.new_round_state['pot']['side']

    def current_player_uuid(self):
        return self.p0_uuid if self.current_player == 0 else self.p1_uuid

    def get_community_card_indices(self) :
        return self.community_card_indices

    def get_hole_card_indices(self) :
        return self.hole_card_indices    

    def get_is_cached_state(self) :
        return self.is_cached