import copy
import math
import operator
from functools import reduce

import cfr_utils.hand_evaluation as HSEval
from cfr_utils.build_tree import GameTreeBuilder
from constants import NUM_ACTIONS, FOLD
from cfr_utils.game_tree import ActionNode, BoardCardsNode, HoleCardsNode, TerminalNode
from pypokerengine.utils.card_utils import (estimate_hole_card_win_rate,
                                            gen_deck)

try:
    from joblib import Parallel, delayed
except ImportError:
    print('!!! Install joblib library to enable  more efficient cfr training on multiple threads !!!\n')

try:
    from tqdm import tqdm
except ImportError:
    pass


class Cfr:

    def __init__(self, game):
        """Build new CFR instance.
        Args:
            game (Game): game definition object.
        """
        self.game = game

        game_tree_builder = GameTreeBuilder(game)

        try:
            with tqdm(total=1) as progress:
                progress.set_description('Building game tree')
                self.game_tree = game_tree_builder.build_tree()
                progress.update(1)
        except NameError:
            self.game_tree = game_tree_builder.build_tree()

        self.player_count = game.get_num_players()

    @staticmethod
    def _calculate_node_average_strategy(node):
        num_possible_actions = len(node.children)
        normalizing_sum = sum(node.strategy_sum)
        if normalizing_sum > 0:
            node.average_strategy = [
                node.strategy_sum[a] / normalizing_sum if a in node.children else 0
                for a in range(NUM_ACTIONS)
            ]
        else:
            action_probability = 1.0 / num_possible_actions
            node.average_strategy = [
                action_probability if a in node.children else 0
                for a in range(NUM_ACTIONS)
            ]

    @staticmethod
    def _calculate_tree_average_strategy(node):
        if type(node) == ActionNode:
            Cfr._calculate_node_average_strategy(node)
        if node.children:
            for child in node.children.values():
                Cfr._calculate_tree_average_strategy(child)

    def train(self, iterations, show_progress=True):
        """Run CFR for given number of iterations.

        The trained tree can be found by retrieving the game_tree
        property from this object. The result strategy is stored
        in average_strategy of each ActionNode in game tree.

        This method can be called multiple times on one instance
        to train more. This can be used for evaluation during training
        and to make number of training iterations dynamic.

        Args:
            iterations (int): Number of iterations.
            show_progress (bool): Show training progress bar.
        """
        if not show_progress:
            iterations_iterable = range(iterations)
        else:
            try:
                iterations_iterable = tqdm(range(iterations))
                iterations_iterable.set_description('CFR training')
            except NameError:
                iterations_iterable = range(iterations)

        for i in iterations_iterable:
            current_deck = gen_deck()
            current_deck.shuffle()

            self._cfr(
                [self.game_tree] * self.player_count,
                [1] * self.player_count,
                None, [], current_deck,
                [False] * self.player_count)

        Cfr._calculate_tree_average_strategy(self.game_tree)

    def _cfr(self, nodes, reach_probs, hole_cards, board_cards, deck, players_folded):
        """
        An enactment of polymorphism here that checks the type of the current node and
        calls its respective function in a recursive manner.
        """
        node_type = type(nodes[0])
        if node_type == TerminalNode:
            return self._cfr_terminal(
                nodes, hole_cards, board_cards, deck,
                players_folded)
        elif node_type == HoleCardsNode:
            return self._cfr_hole_cards(
                nodes, reach_probs,
                hole_cards, board_cards, deck,
                players_folded)
        elif node_type == BoardCardsNode:
            return self._cfr_board_cards(
                nodes, reach_probs,
                hole_cards, board_cards, deck,
                players_folded)
        return self._cfr_action(
            nodes, reach_probs,
            hole_cards, board_cards, deck,
            players_folded)

    def _cfr_terminal(self, nodes, hole_cards, board_cards, deck, players_folded):
        player_count = self.player_count
        pot_commitment = nodes[0].pot_commitment

        if sum(players_folded) == player_count - 1:
            prize = sum(pot_commitment)
            return [-pot_commitment[player] if players_folded[player] else prize - pot_commitment[player]
                    for player in range(player_count)]

        winners = HSEval.get_winners(hole_cards, players_folded, board_cards)
        winner_count = len(winners)
        value_per_winner = sum(pot_commitment) / winner_count
        return [value_per_winner - pot_commitment[p] if p in winners else -pot_commitment[p]
                for p in range(player_count)]

    def _cfr_hole_cards(self, nodes, reach_probs, hole_cards, board_cards, deck, players_folded):
        num_hole_cards = nodes[0].card_count
        next_hole_cards = []

        for p in range(self.player_count):
            next_hole_cards.append(deck.draw_cards(num_hole_cards))

        next_nodes = [node.children[self._get_bucket_key(hole_cards=next_hole_cards[p])]
                      for p, node in enumerate(nodes)]

        return self._cfr(next_nodes, reach_probs, next_hole_cards, board_cards, copy.deepcopy(deck),
                         players_folded)

    def _get_bucket_key(self, hole_cards, community_cards=[]):
        """
        Calculates 2-card hand evaluation if at 'preflop' street or 5,6,7-card hand evaluation
        otherwise. Based on the hand value evaluated, returns the correct bucket number it belongs to.
        """
        if not community_cards:
            return HSEval.get_bucket_number(list(map(lambda x: x.__str__(), hole_cards)))
        else:
            return HSEval.get_bucket_number(list(map(lambda x: x.__str__(), hole_cards)),
                                            list(map(lambda x: x.__str__(), community_cards)))

    def _cfr_board_cards(self, nodes, reach_probs, hole_cards, board_cards, deck, players_folded):
        deck = copy.deepcopy(deck)
        num_board_cards = nodes[0].card_count
        if any(isinstance(el, list) for el in board_cards):
            board_cards = [item for sublist in board_cards for item in sublist]
        new_board_cards = deck.draw_cards(num_board_cards)
        all_board_cards = board_cards + new_board_cards

        next_nodes = [node.children[self._get_bucket_key(hole_cards=hole_cards[0], 
                        community_cards=all_board_cards)] for p, node in enumerate(nodes)]

        return self._cfr(next_nodes, reach_probs, hole_cards, all_board_cards,
                         deck, players_folded)

    @staticmethod
    def _update_node_strategy(node, realization_weight):
        """ Update node strategy by normalizing regret sums. """
        normalizing_sum = 0
        for a in range(NUM_ACTIONS):
            node.strategy[a] = node.regret_sum[a] if node.regret_sum[a] > 0 else 0
            normalizing_sum += node.strategy[a]

        num_possible_actions = len(node.children)
        for a in range(NUM_ACTIONS):
            if normalizing_sum > 0:
                node.strategy[a] /= normalizing_sum
            elif a in node.children:
                node.strategy[a] = 1.0 / num_possible_actions
            else:
                node.strategy[a] = 0
            node.strategy_sum[a] += realization_weight * node.strategy[a]

    def _cfr_action(self, nodes, reach_probs, hole_cards, board_cards, deck, players_folded):
        """ 
        Follows CS3243 game logic requirements for what actions can be taken at the moment.
        Returns the utility values for each player in the game based on utility values generated
        recursively down the game tree.
        
        This recursive process can also be achieved using multiple threads, if 'joblib' is installed. 
        """
        node_player = nodes[0].player
        node = nodes[node_player]
        Cfr._update_node_strategy(node, reach_probs[node_player])
        strategy = node.strategy
        util = [None] * NUM_ACTIONS
        node_util = [0] * self.player_count

        try:
            jobs_result = Parallel(n_jobs=-1)(delayed(self._cfr_action_process)
                        (nodes, reach_probs, node_player, hole_cards, board_cards, 
                        deck, strategy, a, players_folded) for a in node.children)
        except NameError:
            jobs_result = []
            for a in node.children:
                jobs_result.append(self._cfr_action_process(nodes, reach_probs, node_player, 
                        hole_cards, board_cards, deck, strategy, a, players_folded))

        for action, action_util in jobs_result:
            util[action] = action_util
            for player in range(self.player_count):
                node_util[player] += strategy[action] * action_util[player]

        for a in node.children:
            regret = util[a][node_player] - node_util[node_player]

            opponent_reach_probs = reach_probs[0:node_player] + reach_probs[node_player + 1:]
            reach_prob = reduce(operator.mul, opponent_reach_probs, 1)
            node.regret_sum[a] += regret * reach_prob

        return node_util

    def _cfr_action_process(self, nodes, reach_probs, node_player, hole_cards, 
                            board_cards, deck, strategy, a, players_folded):
        next_reach_probs = list(reach_probs)
        next_reach_probs[node_player] *= strategy[a]

        if a == FOLD:
            next_players_folded = list(players_folded)
            next_players_folded[node_player] = True
        else:
            next_players_folded = players_folded
        
        """ Recursively calculates cfr """
        action_util = self._cfr(
            [node.children[a] for node in nodes], next_reach_probs,
            hole_cards, board_cards, deck, next_players_folded)

        return a, action_util
