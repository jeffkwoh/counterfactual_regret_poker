import constants

class Game:
    """Game definition."""

    def __init__(self):
        self.board_card_counts = [self.get_num_board_cards(round_index)
                                  for round_index in range(self.get_num_rounds())]
        for i in range(1, self.get_num_rounds()):
            self.board_card_counts[i] = self.board_card_counts[i - 1] + self.board_card_counts[i]

    def get_blind(self, player_index):
        """Returns player's entry fee.

        Args:
            player_index (int): Index of the player

        Returns:
            int: Player's entry fee (blind).

        Raises:
            ValueError: When player_index is greater or equal
                        to number of players in the game.
        """
        if player_index >= self.get_num_players():
            raise ValueError(
                'Cannot retrieve stack for player %s with %s players total'
                % (player_index, self.get_num_players()))
        
        return constants.SMALL_BLIND

    def get_raise_size(self, round_index):
        """Returns the size of raise for limit games in given round.

        Args:
            round_index (int): Index of the round

        Returns:
            int: Size of the raise in given round.

        Raises:
            ValueError: When round_index is greater or equal
                        to number of rounds in the game.
        """
        if round_index >= self.get_num_rounds():
            raise ValueError(
                'Cannot retrieve raise size in round %s in game with %s rounds'
                % (round_index, self.get_num_rounds()))
        if round_index < constants.TURN:
            return constants.RAISE_AMT_BEFORE_TURN
        else:
            return constants.RAISE_AMT_AFTER_TURN

    def get_betting_type(self):
        """Betting type of the game, that is either limited or no-limit.

        Returns:
            BettingType: Betting type of the game.
        """
        return constants.BETTING_TYPE

    def get_num_players(self):
        """Returns number of players in the game.

        Returns:
            int: Number of players in the game.
        """
        return constants.NUM_PLAYER

    def get_num_rounds(self):
        """Returns number of rounds in the game.

        Returns:
            int: Number of rounds in the game.
        """
        return constants.NUM_ROUND

    def get_first_player(self, round_index):
        """Returns first layer in given round of the game.

        Args:
            round_index (int): Index of the round

        Returns:
            int: First layer in given round of the game.

        Raises:
            ValueError: When round_index is greater or equal
                        to number of rounds in the game.
        """
        if round_index >= self.get_num_rounds():
            raise ValueError(
                'Cannot retrieve first player in round %s in game with %s rounds'
                % (round_index, self.get_num_rounds()))

        return constants.FIRST_PLAYER_INDEX

    def get_max_raises_per_street(self, round_index):
        """Returns number of bets/raises that may be made in given round.

        Args:
            round_index (int): Index of the round

        Returns:
            int: Number of bets/raises that may be made in each round.

        Raises:
            ValueError: When round_index is greater or equal
                        to number of rounds in the game.
        """
        if round_index >= self.get_num_rounds():
            raise ValueError(
                'Cannot retrieve max number of raises in round %s in game with %s rounds'
                % (round_index, self.get_num_rounds()))
            
        if round_index < constants.FLOP:
            return constants.MAX_RAISE_PREFLOP
        else:
            return constants.MAX_RAISE_AFTER_FLOP
    
    def get_max_raises_per_player_per_game(self, player_index):
        """Returns maximum numbers of raises a player can make in the entire game.
        
        Args:
            player_index (int): Index of the player
            
        Returns:
         int: Number of bets/raises that may be made by a player in each game.
         
        """
        return constants.MAX_RAISE_PER_PLAYER

    def get_num_suits(self):
        """Returns number of card suits in the game.

        Returns:
            int: Number of card suits in the game.
        """
        return constants.NUM_SUIT

    def get_num_ranks(self):
        """Returns number of card ranks in the game.

        Returns:
            int: Number of card ranks in the game.
        """
        return constants.NUM_RANK

    def get_num_hole_cards(self):
        """Returns number of hole cards each player receives at the beginning of the game.

        Returns:
            int: Number of hole cards each player receives at the beginning of the game.
        """
        return constants.NUM_HOLE_CARDS

    def get_num_board_cards(self, round_index):
        """Returns number of board cards that are revealed in given round.

        Args:
            round_index (int): Index of the round

        Returns:
            int: Number of board cards that are revealed in given round.

        Raises:
            ValueError: When round_index is greater or equal
                        to number of rounds in the game.
        """
        if round_index >= self.get_num_rounds():
            raise ValueError(
                'Cannot retrieve number of board cards in round %s in game with %s rounds'
                % (round_index, self.get_num_rounds()))
            
        if round_index == constants.PREFLOP:
            return constants.NUM_COMMUNITY_CARD_DRAWN_PREFLOP
        elif round_index == constants.FLOP:
            return constants.NUM_COMMUNITY_CARD_DRAWN_FLOP
        else:
            return constants.NUM_COMMUNITY_CARD_DRAWN_TURN_AND_RIVER

    def get_total_num_board_cards(self, round_index):
        """Returns total number of board cards that are on the board in given round.

        Args:
            round_index (int): Index of the round

        Returns:
            int: Total number of board cards that are on the board in given round.

        Raises:
            ValueError: When round_index is greater or equal
                        to number of rounds in the game.
        """
        if round_index >= self.get_num_rounds():
            raise ValueError(
                'Cannot retrieve number of board cards in round %s in game with %s rounds'
                % (round_index, self.get_num_rounds()))
        if round_index == constants.PREFLOP:
            return constants.NUM_COMMUNITY_CARD_DRAWN_PREFLOP
        else:
            return round_index + 2
