from pypokerengine.engine.card import Card as PyCard
from itertools import *
from pypokerengine.utils.card_utils import estimate_hole_card_win_rate
import math
import matplotlib.pyplot as plt


def starting_hand_evaluator(hole_cards):
    """
      This takes into the account the card potential apart from relative card values.

       :param hole_cards: List(str) in format of 'CA' for hole cards belong to the current player
       :retrun: int within a range of -1.5 and 20
    """

    c1, c2 = str_to_pycard(hole_cards)
    maxRank = max(c1.rank, c2.rank)
    strength = 0

    # High card
    if maxRank == 14:  # Ace
        strength += 10
    elif maxRank == 13:  # King
        strength += 8
    elif maxRank == 12:  # Queen
        strength += 7
    elif maxRank == 11:  # Jack
        strength += 6
    else:
        strength += maxRank / 2.0

    # Pairs
    if c1.rank == c2.rank:
        minimum = 5
        if c1.rank == 5:  # Five
            minimum = 6
        strength = max(strength * 2, minimum);

    # Suited
    if c1.suit == c2.suit:
        strength += 2

    # Closeness
    gap = int(math.fabs(c1.rank - c2.rank))
    if gap == 1:
        strength += 1
    elif gap == 2:
        strength -= 1
    elif gap == 3:
        strength -= 2
    elif gap == 4:
        strength -= 4
    else:
        if gap != 0:
            strength -= 5

    # Bonus for consecutive and Smaller than Queen
    if gap == 1 and maxRank < 12:
        strength += 1

    return (strength + 1.5)/21.5


def str_to_pycard(hole_cards):
    SUITE_MAP_TO_INT = {
        "C": 0,
        "D": 13,
        "H": 26,
        "S": 39
    }
    RANK_MAP_TO_INT = {
        "A": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "T": 10,
        "J": 11,
        "Q": 12,
        "K": 13
    }
    hole_card_indices = []
    for h in hole_cards:
        index = SUITE_MAP_TO_INT[h[0]] + RANK_MAP_TO_INT[h[1]]
        hole_card_indices.append(index)
    c1 = PyCard.from_id(hole_card_indices[0])
    c2 = PyCard.from_id(hole_card_indices[1])
    return c1, c2


suits = ['C', 'D', 'H', 'S']
ranks = ['A'] + [str(i) for i in range(2, 10)] + ['T', 'J', 'Q', 'K']

chen_deck = [s + r for s in suits for r in ranks]
chen_distribution = [starting_hand_evaluator(list(hand)) for hand in permutations(chen_deck, 2)]
hs_distribution = [estimate_hole_card_win_rate(1000, 2, list(str_to_pycard(list(hand)))) for hand in permutations(chen_deck, 2)]
# print(chen_distribution)

# # matplotlib histogram
# plt.hist(chen_distribution, color='grey', edgecolor='black',
#          bins=int(180 / 5))
#
# # Add labels
# plt.title("Chen's Formula 2-card Power Rating")
# plt.xlabel('Normalised Power Rating')
# plt.ylabel('Number of Hands')
# plt.show()

# matplotlib histogram
print(hs_distribution)
plt.hist(hs_distribution, color='grey', edgecolor='black',
         bins=int(180 / 5))

# Add labels
plt.title("2-card Hand Strength")
plt.xlabel('Hand Strength')
plt.ylabel('Number of Hands')
plt.show()

