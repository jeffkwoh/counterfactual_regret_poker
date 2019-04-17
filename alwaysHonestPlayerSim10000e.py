from pypokerengine.api.game import setup_config, start_poker
from raise_player import RaisedPlayer
from Group19Player1000e import Group19Player
import json
import sys

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage {strategyFile}")
        sys.exit(1)

    strategyFileResults = sys.argv[1]
    # num_games = int(sys.argv[2], 10)
    # output_text_file = sys.argv[3]


    game_data = {}

    for i in range(1000):
        # TODO:config the config as our wish
        config = setup_config(max_round=500, initial_stack=10000, small_blind_amount=20)

        config.register_player(name="AlwaysRaisedPlayer", algorithm=RaisedPlayer())
        config.register_player(name="Group19Player", algorithm=Group19Player())
        game_result = start_poker(config, verbose=0)

        print(game_result)

        player1 = game_result['players'][0]
        player1_name = player1['name']
        player1_stack = player1['stack']
        player2 = game_result['players'][1]
        player2_name = player2['name']
        player2_stack = player2['stack']

        game_data[player1_name] = 0
        game_data[player2_name] = 0

        if player1_stack > player2_stack:
            game_data[player1_name] += 1

        elif player2_stack > player1_stack:
            game_data[player2_name] += 1
        else:
            game_data[player1_name] += 0.5
            game_data[player2_name] += 0.5

        print(i)

    results = open(strategyFileResults, "w")
    results.write(json.dumps(game_data))
    results.write("\n")