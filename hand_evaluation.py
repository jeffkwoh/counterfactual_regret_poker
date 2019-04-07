# from functools import reduce
# TODO: RELATIVE IMPORTS WILL BREAK IN PYTHON 2.7
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card

# import acpc_python_client as acpc

SUIT_MAP = {
    0: 'C',
    1: 'D',
    2: 'H',
    3: 'S'
}

RANK_MAP = {
    0: 'A',
    1: '2',
    2: '3',
    3: '4',
    4: '5',
    5: '6',
    6: '7',
    7: '8',
    8: '9',
    9: 'T',
    10: 'J',
    11: 'Q',
    12: 'K',
}


# TODO: Generate List of cards using pypoker engine

def cfr_card_to_pypoker_card(card):
    return Card.from_str(card_to_str(card))


def card_to_str(card):
    return SUIT_MAP[card_suit(card)] + RANK_MAP[card_rank(card)]


def card_rank(card):
    """Returns card rank from card's int representation.

    Args:
        card (int): Int representation of the card. This representation
                    has each card rank of each suit represented by unique integer.

    Returns:
        int: Card rank as 0 based index.
    """
    return card // 4


def card_suit(card):
    """Returns card suit from card's int representation.

    Args:
        card (int): Int representation of the card. This representation
                    has each card rank of each suit represented by unique integer.

    Returns:
        int: Card suit as 0 based index.
    """
    return card % 4


def partition_cards(cards):
    hole_cards = []
    community_cards = []
    for i, card in enumerate(cards):
        if i < 2:
            hole_cards.append(card)
        else:
            community_cards.append(card)
    return [hole_cards, community_cards]


def get_winners(hands):
    """Evaluate hands of players and determine winners.

    !!! This function is currently only capable of evaluating hands that contain up to 5 cards. !!!

    Args:
        hands (list(list(int))): List which contains player's hands. Each player's hand is a list of integers
                                 that represent player's cards. Board cards must be included in each player's hand.

    Returns:
        list(int): Indexes of winners. The pot should be split evenly between all winners.
    """

    card_hands = [[cfr_card_to_pypoker_card(card) for card in hand] for hand in hands]
    pokerengine_card_hands = [partition_cards(card_hand) for card_hand in card_hands]
    bitscores = [HandEvaluator.eval_hand(partitioned_hand[0], partitioned_hand[1]) for partitioned_hand in
                 pokerengine_card_hands]
    best_score = max(bitscores)
    winner_indexes = [i for i, bitscore in enumerate(bitscores) if bitscore >= best_score]
    return winner_indexes

# def _parse_hand(hand):
#     return map(lambda card: (acpc.game_utils.card_rank(card), acpc.game_utils.card_suit(card)), hand)
#
#
# def _score(hand):
#     if len(hand) <= 5:
#         return _score_hand_combination(_parse_hand(hand))
#     else:
#         # TODO create multiple 5 card combinations from longer hand to allow Texas Hold'em hand evaluation
#         return ((0,), (0,))
#
#
# def _score_hand_combination(hand):
#     rank_counts = {r: reduce(lambda count, card: count + (card[0] == r), hand, 0)
#                    for r, _ in hand}.items()
#     score, ranks = zip(*sorted((cnt, rank) for rank, cnt in rank_counts)[::-1])
#     if len(score) == 5:
#         if ranks[0:2] == (12, 3):  # adjust if 5 high straight
#             ranks = (3, 2, 1, 0, -1)
#         straight = ranks[0] - ranks[4] == 4
#         flush = len({suit for _, suit in hand}) == 1
#         score = ([(1,), (3, 1, 1, 1)], [(3, 1, 1, 2), (5,)])[flush][straight]
#     return score, ranks
