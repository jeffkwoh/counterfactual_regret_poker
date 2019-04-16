import operator
import copy
from functools import reduce
import math
from multiprocessing import Process, Lock, Manager

from build_tree import GameTreeBuilder
from Group19_constants import NUM_ACTIONS
from game_tree import HoleCardsNode, TerminalNode, ActionNode, BoardCardsNode
from Group19_hand_evaluation import get_winners
from pypokerengine.utils.card_utils import estimate_hole_card_win_rate, gen_deck
import Group19_hand_evaluation as HSEval

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

        winners = get_winners(hole_cards, players_folded, board_cards)
        winner_count = len(winners)
        value_per_winner = sum(pot_commitment) / winner_count
        return [value_per_winner - pot_commitment[p] if p in winners else -pot_commitment[p]
                for p in range(player_count)]

    def _cfr_hole_cards(self, nodes, reach_probs, hole_cards, board_cards, deck, players_folded):
        num_hole_cards = nodes[0].card_count
        next_hole_cards = []

        for p in range(self.player_count):
            next_hole_cards.append(deck.draw_cards(num_hole_cards)) # Draw_cards is a mutating function with side effects

        # TODO: The key for next nodes need to correspond to the new key for the buckets.
        # TODO: Why do we key into the opponent's nodes as well?
        next_nodes = [node.children[self._get_bucket_key(hole_cards=next_hole_cards[p])]
                      for p, node in enumerate(nodes)]

        return self._cfr(next_nodes, reach_probs, next_hole_cards, board_cards, copy.deepcopy(deck),
                         players_folded)

    def _get_bucket_key(self, hole_cards, community_cards=[]):
        if not community_cards:
            return HSEval.get_bucket_number(list(map(lambda x: x.__str__(), hole_cards)))
        else:
            return HSEval.get_bucket_number(list(map(lambda x: x.__str__(), hole_cards)),
                                            list(map(lambda x: x.__str__(), community_cards)))

    def _cfr_board_cards(self, nodes, reach_probs, hole_cards, board_cards, deck, players_folded):
        deck = copy.deepcopy(deck)
        num_board_cards = nodes[0].card_count
        if any(isinstance(el, list) for el in board_cards):
            board_cards = [item for sublist in board_cards for item in sublist] # flatten the list of sublists
        new_board_cards = deck.draw_cards(num_board_cards)
        all_board_cards = board_cards + new_board_cards
                
        # TODO: Check if the hole_cards here belong to the player , need tracing through the code. check hole_cards[0]
        next_nodes = [node.children[self._get_bucket_key(hole_cards=hole_cards[0], community_cards=all_board_cards)]
            for p, node in enumerate(nodes)]

        return self._cfr(next_nodes, reach_probs, hole_cards, all_board_cards,
                        deck, players_folded)

    # TODO: Understand calculation of updated strategy probabilities.
    @staticmethod
    def _update_node_strategy(node, realization_weight):
        """Update node strategy by normalizing regret sums."""
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
        node_player = nodes[0].player
        node = nodes[node_player]
        Cfr._update_node_strategy(node, reach_probs[node_player])
        strategy = node.strategy
        
        if board_cards:
            """ Do not fork new multiprocessing.Process after 'preflop' street. """
            util = [None] * NUM_ACTIONS
            node_util = [0] * self.player_count
            
            for a in node.children:
                next_reach_probs = list(reach_probs)
                next_reach_probs[node_player] *= strategy[a]

                if a == 0:
                    next_players_folded = list(players_folded)
                    next_players_folded[node_player] = True
                else:
                    next_players_folded = players_folded
                # Recursively calculates cfr
                action_util = self._cfr(
                    [node.children[a] for node in nodes], next_reach_probs,
                    hole_cards, board_cards, deck, next_players_folded)
                util[a] = action_util
                for player in range(self.player_count):
                    node_util[player] += strategy[a] * action_util[player]
        else:
            """ 
            Fork new multiprocessing.Process to iterate through child nodes of current action nodes 
            if current action node is direct child of hole_card node.
            """
            # use multiprocessing process table to keep track child processes of current process
            procs = []
            
            # initialise semaphore using multiprocessing.Lock
            lock = Lock()

            # allocate shared memory lists using multiprocessing.manager
            manager = Manager()
            util = manager.list()
            for i in range(NUM_ACTIONS):
                util.append(None)
            node_util = manager.list()
            for i in range(self.player_count):
                node_util.append(0)
                    
            for a in node.children:
                next_reach_probs = list(reach_probs)
                next_reach_probs[node_player] *= strategy[a]

                if a == 0:
                    next_players_folded = list(players_folded)
                    next_players_folded[node_player] = True
                else:
                    next_players_folded = players_folded
                    
                # spawn a new process to calculate cfr values for current action
                proc = Process(target=self._cfr_action_process, args=(nodes, next_reach_probs, hole_cards, 
                                board_cards, deck, next_players_folded, util, node_util, strategy, a, lock))
                procs.append(proc)
                proc.start()
            
            for proc in procs:
                proc.join() # current process will wait here until all child processes finish
            
        for a in node.children:
            # Calculate regret and add it to regret sums
            regret = util[a][node_player] - node_util[node_player]

            opponent_reach_probs = reach_probs[0:node_player] + reach_probs[node_player + 1:]
            reach_prob = reduce(operator.mul, opponent_reach_probs, 1)
            node.regret_sum[a] += regret * reach_prob

        return [x for x in node_util] if type(node_util) != type(list) else node_util

    def _cfr_action_process(self, nodes, next_reach_probs, hole_cards, board_cards, deck,
                            next_players_folded, util, node_util, strategy, a, lock):
        # Recursively calculates cfr without parallelism anymore
        action_util = self._cfr([node.children[a] for node in nodes], next_reach_probs,
                                    hole_cards, board_cards, deck, next_players_folded)
        
        # prevent race condition using multiprocessing.Lock
        lock.acquire() 
        util[a] = action_util
        for player in range(self.player_count):
            node_util[player] += strategy[a] * action_util[player]
        lock.release()
        
        return
    