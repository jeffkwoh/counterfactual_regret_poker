from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card as PyCard
from deuces.evaluator import Evaluator
from deuces.card import Card as DeucesCard
import constants
import math
import sys


def get_winners(players_hole, players_folded, community_cards):
    """
    Evaluate which players win the game, GIVEN complete information.
    :param players_hole: List(List(PyCard)) each player's hole IN ORDER of their index
    :param players_folded: List(bool) each player's status of folding (True for yes) IN ORDER of their index
    :param community_cards: List(PyCard) community cards
    :return: List(int) Representing indexes of winners, pot is evenly divided among winners.
    """
    valid_scores = []
    for i, hole in enumerate(players_hole):
        if players_folded[i]:
            valid_scores.append(0)
        else:
            valid_scores.append(HandEvaluator.eval_hand(hole, community_cards))
    best_score = max(valid_scores)
    winners = [i for i, score in enumerate(valid_scores) if score >= best_score]
    return winners

def get_bucket_number(hole_cards, community_cards = None):
	"""	
	Evaluate handstrength base on Chen's Formula if only hole cards are drawn,
    because it values both hand potential as well as relative value of card rank.
    Otherwise, evaluate handstrength using Deuces Monte-carlo Look-up table.
    Divide the bucket with equal probability based on the number of buckets.
    Using the handstrength value drawn earlier, find the right bucket.
    
    :param hole_cards: List(str) in format of 'CA' for hole cards belong to the current player
    :param community_cards: List(str) in format of 'S3' for community cards   
    """
	if not community_cards:
		points = starting_hand_evaluator(hole_cards)
		bucket_number = int(math.ceil((points + 1.5) / 21.5 * constants.BUCKET_NUM) - 1)
	else:
		hole_cards = list(map(lambda x : DeucesCard.new(x[1] + x[0].lower()), hole_cards))
		community_cards = list(map(lambda x : DeucesCard.new(x[1] + x[0].lower()), community_cards))

		evaluator = Evaluator()
		five_cards_ranking = evaluator.evaluate(hole_cards, community_cards)
		strength = 1.0 - evaluator.get_five_card_rank_percentage(five_cards_ranking)
		bucket_number = int(math.ceil(strength * constants.BUCKET_NUM) - 1)
  
	return 0 if bucket_number == -1 else bucket_number

def starting_hand_evaluator(hole_cards):

	"""
  	This takes into the account the card potential apart from relative card values.
   
   	:param hole_cards: List(str) in format of 'CA' for hole cards belong to the current player
   	:retrun: int within a range of -1.5 and 20   
    """
	
	SUITE_MAP_TO_INT = {
		"C" : 0,
		"D" : 13,
  		"H" : 26,
		"S" : 39
	}

	RANK_MAP_TO_INT = {
		"A" : 1,
		"2" : 2,
  		"3" : 3,
  		"4" : 4,
  		"5" : 5,
  		"6" : 6,
  		"7" : 7,
  		"8" : 8,
  		"9" : 9,
  		"T" : 10,
  		"J" : 11,
  		"Q" : 12,
  		"K" : 13
	}
  
	hole_card_indices = []
	for h in hole_cards:
		index = SUITE_MAP_TO_INT[h[0]] + RANK_MAP_TO_INT[h[1]]
		hole_card_indices.append(index)
 
	c1 = PyCard.from_id(hole_card_indices[0])
	c2 = PyCard.from_id(hole_card_indices[1])
	maxRank = max(c1.rank, c2.rank)
	strength = 0
	
	# High card
	if maxRank == 14: #Ace
		strength += 10
	elif maxRank == 13: #King
		strength += 8
	elif maxRank == 12: #Queen
		strength += 7
	elif maxRank == 11: #Jack
		strength += 6
	else:
		strength += maxRank / 2.0
	
	# Pairs
	if c1.rank == c2.rank:
		minimum = 5
		if c1.rank == 5: #Five
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

	return strength
