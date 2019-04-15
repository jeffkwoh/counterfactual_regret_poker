from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from Group19Player import Group19Player
import json
import sys 
results = open("results.txt","w") 

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage {num_rounds} {num_games}")
        sys.exit(1)

    num_rounds = int(sys.argv[1], 10)
    num_games = int(sys.argv[2], 10)
    for i in range(num_games) :
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
    


    
