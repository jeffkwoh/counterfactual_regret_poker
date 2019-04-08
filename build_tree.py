import copy
import itertools

from game_tree import HoleCardsNode, ActionNode, TerminalNode, BoardCardsNode

# TODO: Remove dirty global Var
_MAX_SUITS = 4


class GameTreeBuilder:
    """Builds game tree from given ACPC game definition object."""

    class GameState:
        """State of the game passed down through the recursive tree builder."""

        def __init__(self, game, deck):
            # Game properties
            self.players_folded = [False] * game.get_num_players()
            self.pot_commitment = [game.get_blind(p) for p in range(game.get_num_players())]
            self.deck = deck

            # Round properties
            self.rounds_left = game.get_num_rounds()
            self.round_raise_count = 0
            self.players_acted = 0
            self.current_player = game.get_first_player(0)

        def next_round_state(self):
            """Get copy of this state for new game round."""
            res = copy.deepcopy(self)
            res.rounds_left -= 1
            res.round_raise_count = 0
            res.players_acted = 0
            return res

        def next_move_state(self):
            """Get copy of this state for next move."""
            res = copy.deepcopy(self)
            res.players_acted += 1
            return res

    def __init__(self, game):
        self.game = game

    # TODO: Use python list literals for speed.
    def _build_standard_deck(self):
        deck = []
        for suit in range(4):
            for rank in range(13):
                deck.append(rank * _MAX_SUITS + suit)
        return deck

    def card_rank(self, card):
        """Returns card rank from card's int representation.

        Args:
            card (int): Int representation of the card. This representation
                        has each card rank of each suit represented by unique integer.

        Returns:
            int: Card rank as 0 based index.
        """
        return card // _MAX_SUITS

    def card_suit(self, card):
        """Returns card suit from card's int representation.

        Args:
            card (int): Int representation of the card. This representation
                        has each card rank of each suit represented by unique integer.

        Returns:
            int: Card suit as 0 based index.
        """
        return card % _MAX_SUITS

    def build_tree(self):
        """Builds and returns the game tree."""

        deck = self._build_standard_deck()

        # First generate hole cards node which is only generated once at the beginning of the game
        root = HoleCardsNode(None, self.game.get_num_hole_cards())
        num_hole_cards = self.game.get_num_hole_cards()
        # combinations(iterable, length of tuple)
        hole_card_combinations = itertools.combinations(range(len(deck)), num_hole_cards)
        for hole_cards_indexes in hole_card_combinations:
            """
            Needs to be sorted otherwise we'll run into key errors. 
            Hole_cards is used as a key, and tuples are ordered.
            """
            hole_cards = tuple(sorted(map(lambda i: deck[i], hole_cards_indexes)))
            next_deck = self.remove_hole_cards(deck, hole_cards_indexes)

            game_state = GameTreeBuilder.GameState(self.game, next_deck)
            # Start first game round with board cards node
            # Tuple of hole_cards are used as child keys if this is preflop.
            self._generate_board_cards_node(root, hole_cards, game_state)
        return root

    def remove_hole_cards(self, deck, hole_cards_indexes):
        next_deck = list(deck)
        # Delete the two Hole cards
        del next_deck[hole_cards_indexes[0]]
        del next_deck[hole_cards_indexes[1] - 1]
        return next_deck

    def _generate_board_cards_node(self, parent, child_key, game_state):
        rounds_left = game_state.rounds_left
        round_index = self.game.get_num_rounds() - rounds_left
        num_board_cards = self.game.get_num_board_cards(round_index)
        if num_board_cards <= 0:
            self._generate_action_node(parent, child_key, game_state)
        else:
            new_node = BoardCardsNode(parent, num_board_cards)
            parent.children[child_key] = new_node

            deck = game_state.deck
            board_card_combinations = itertools.combinations(range(len(deck)), num_board_cards)

            for board_cards_idxs in board_card_combinations:
                next_game_state = copy.deepcopy(game_state)
                # Nifty trick in countering change in list length because combinations are in lexicographic sorted order
                for i, board_card_index in enumerate(board_cards_idxs):
                    del next_game_state.deck[board_card_index - i]
                board_cards = tuple(map(lambda i: deck[i], board_cards_idxs))
                # def _generate_action_node(self, parent, child_key, game_state):
                self._generate_action_node(new_node, board_cards, next_game_state)

    @staticmethod
    def _bets_settled(bets, players_folded):
        non_folded_bets_filter = filter(lambda bet: not players_folded[bet[0]], enumerate(bets))
        non_folded_bets = list(map(lambda bet_enum: bet_enum[1], non_folded_bets_filter))
        return non_folded_bets.count(non_folded_bets[0]) == len(non_folded_bets)

    def _generate_action_node(self, parent, child_key, game_state):
        player_count = self.game.get_num_players()
        players_folded = game_state.players_folded
        pot_commitment = game_state.pot_commitment
        current_player = game_state.current_player
        rounds_left = game_state.rounds_left

        bets_settled = GameTreeBuilder._bets_settled(pot_commitment, players_folded)
        all_acted = game_state.players_acted >= (player_count - sum(players_folded))
        if bets_settled and all_acted:
            if rounds_left > 1 and sum(players_folded) < player_count - 1:
                # Start next game round with new board cards node
                next_game_state = game_state.next_round_state()
                next_game_state.current_player = \
                    self.game.get_first_player(self.game.get_num_rounds() - rounds_left + 1)

                self._generate_board_cards_node(parent, child_key, next_game_state)
            else:
                # This game tree branch ended, close it with terminal node
                new_node = TerminalNode(parent, pot_commitment)
                parent.children[child_key] = new_node
            return

        new_node = ActionNode(parent, current_player)
        parent.children[child_key] = new_node

        round_index = self.game.get_num_rounds() - rounds_left
        next_player = (current_player + 1) % self.game.get_num_players()
        max_pot_commitment = max(pot_commitment)
        valid_actions = [1]
        if not bets_settled:
            valid_actions.append(0)
        # TODO: Implement cs3243 logic.
        if game_state.round_raise_count < self.game.get_max_raises_per_street(round_index) and \
            (game_state.current_player == 0 and \
                 game_state.p0_raise < self.game.get_max_raises_per_player_per_game(current_player)) or \
                    (game_state.current_player == 1 and \
                        game_state.p0_raise < self.game.get_max_raises_per_player_per_game(current_player)):
            valid_actions.append(2)
        for a in valid_actions:
            next_game_state = game_state.next_move_state()
            next_game_state.current_player = next_player

            if a == 0:
                next_game_state.players_folded[current_player] = True
            elif a == 1:
                next_game_state.pot_commitment[current_player] = max_pot_commitment
            elif a == 2:
                next_game_state.round_raise_count += 1
                if next_game_state.current_player == 0:
                    next_game_state.p1_raise += 1
                else:
                    next_game_state.p0_raise += 1
                # TODO: Update pot change.
                next_game_state.pot_commitment[current_player] = \
                    max_pot_commitment + self.game.get_raise_size(round_index)

            self._generate_action_node(new_node, a, next_game_state)
