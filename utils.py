def build_standard_deck():
    deck = []
    for suit in range(4):
        for rank in range(13):
            deck.append(rank * 4 + suit)
    return deck
