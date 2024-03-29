import resource
import sys

from cfr_utils.cfr import Cfr
from constants import CALL, FOLD
from cfr_utils.game import Game
from cfr_utils.game_tree import ActionNode, BoardCardsNode, HoleCardsNode

try:
    from tqdm import tqdm
except ImportError:
    print('!!! Install tqdm library for better progress information !!!\n')


"""Trains strategy for poker agent using CFR algorithm and writes it to specified file.

Usage:
python train.py {game_file_path} {iterations} {strategy_output_path}

  game_file_path: Path to ACPC game definition file of a poker game for which we want create the strategy.  
  iterations: Number of iterations for which the CFR algorithm will run.
  strategy_output_path: Path to file into which the result strategy will be written. 
"""

def _action_to_str(action):
    if action == FOLD:
        return 'f'
    elif action == CALL:
        return 'c'
    else:
        return 'r'


def _get_strategy_lines(lines, node, prefix=''):
    node_type = type(node)
    if node_type == HoleCardsNode or node_type == BoardCardsNode:
        for key, child_node in node.children.items():
            new_prefix = prefix
            if new_prefix and not new_prefix.endswith(':'):
                new_prefix += ':'
            new_prefix += ':'+ str(key) + ':'
            _get_strategy_lines(lines, child_node, new_prefix)
    elif node_type == ActionNode:
        node_strategy_str = ' '.join([str(prob) for prob in node.average_strategy])
        lines.append('%s %s\n' % (prefix, node_strategy_str))

        for action, child_node in node.children.items():
            _get_strategy_lines(lines, child_node, prefix + _action_to_str(action))


def _write_to_output_file(output_path, lines):
    with open(output_path, 'w') as file:
        for line in lines:
            file.write(line)


def _write_strategy(game_tree, iterations, output_path):
    strategy_file_lines = []

    try:
        with tqdm(total=1) as progress:
            progress.set_description('Obtaining strategy entries')
            _get_strategy_lines(strategy_file_lines, game_tree)
            progress.update(1)
    except NameError:
        _get_strategy_lines(strategy_file_lines, game_tree)

    try:
        with tqdm(total=1) as progress:
            progress.set_description('Sorting strategy file')
            strategy_file_lines_sorted = sorted(strategy_file_lines)
            progress.update(1)
    except NameError:
        strategy_file_lines_sorted = sorted(strategy_file_lines)

    strategy_file_lines_sorted = ['#  Training iterations: %s\n' % iterations] + strategy_file_lines_sorted

    try:
        with tqdm(total=1) as progress:
            progress.set_description('Writing strategy file')
            _write_to_output_file(output_path, strategy_file_lines_sorted)
            progress.update(1)
    except NameError:
        _write_to_output_file(output_path, strategy_file_lines_sorted)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage {iterations} {strategy_output_path}")
        sys.exit(1)
        
    iterations = int(sys.argv[1])
    output_path = sys.argv[2]
    game = Game()
    cfr = Cfr(game)
    cfr.train(iterations)

    _write_strategy(cfr.game_tree, iterations, output_path)
