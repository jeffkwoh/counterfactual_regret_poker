from pypokerengine.api.game import setup_config, start_poker
from raise_player import RaisedPlayer
from Group19Player import Group19Player
import json
import sys 


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage {strategyFileNumber : {0-9}")
        sys.exit(1)
    num_rounds = 500
    num_games = [2000,3000,4000,5000,6000,7000,8000,9000,10000]

    text_files = ['resultsStrategy10000e_2000games.txt','resultsStrategy10000e_3000games.txt',
                  'resultsStrategy10000e_4000games.txt','resultsStrategy10000e_5000games.txt',
                  'resultsStrategy10000e_6000games.txt','resultsStrategy10000e_7000games.txt',
                  'resultsStrategy10000e_8000games.txt','resultsStrategy10000e_9000games.txt',
                  'resultsStrategy10000e_10000games.txt']

    strategyFileNumber = int(sys.argv[1], 10)
    # num_games = int(sys.argv[2], 10)
    # output_text_file = sys.argv[3]

    current_text_file = text_files[strategyFileNumber]
    current_games = num_games[strategyFileNumber]
    results = open(current_text_file,"w")
    for i in range(current_games) :
        #TODO:config the config as our wish
        config = setup_config(max_round=num_rounds, initial_stack=10000, small_blind_amount=20)

        config.register_player(name="AlwaysRaisedPlayer", algorithm=RaisedPlayer())
        config.register_player(name="Group19Player", algorithm=Group19Player())
        game_result = start_poker(config, verbose=0)

        game_data = {}

        for player in game_result['players'] :
            player_name = player['name']
            player_stack = player['stack']
            player_num_wins = game_result['result'][player_name]
            game_data[player_name] = {
                'num_wins' : player_num_wins,
                'num_loses' : game_result['num_rounds'] - player_num_wins,
                'game_stack' : player_stack
            }

            try :
                if game_data['winner'] :
                    if game_data[player_name]['game_stack'] > game_data[game_data['winner']]['game_stack'] :
                        game_data['winner'] = player_name

            except KeyError :
                game_data['winner'] = player_name

        print(i)
        results.write(json.dumps(game_data))
        results.write("\n")
    


    
