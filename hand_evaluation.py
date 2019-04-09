from pypokerengine.engine.hand_evaluator import HandEvaluator


def get_winners(players_hole, players_folded, community_cards):
    """
    Evaluate which players win the game, GIVEN complete information.
    :param players_hole: List(List(Card)) each player's hole IN ORDER of their index
    :param players_folded: List(bool) each player's status of folding (True for yes) IN ORDER of their index
    :param community_cards: List(Card) community cards
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
