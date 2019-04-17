from pypokerengine.api.game import setup_config, start_poker
from honest_player import HonestPlayer
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

    results = open(strategyFileResults,"w")
    
    game_data = {}
    
    for i in range(1000) :
        #TODO:config the config as our wish
        config = setup_config(max_round=500, initial_stack=10000, small_blind_amount=20)

        config.register_player(name="HonestPlayer", algorithm=HonestPlayer())
        config.register_player(name="Group19Player", algorithm=Group19Player())
        game_result = start_poker(config, verbose=0)

        player1 = game_result['players'][0]
        player1_name = player1['name']
        player1_stack = player1['stack']
        player2 = game_result['players'][1]
        player2_name = player2['name']
        player2_stack = player2['stack']
        
        if  player1_stack > player2_stack :
            try :
                if game_data[player1_name] :
                    game_data[player1_name] += 1
            except KeyError :
                game_data[player1_name] = 1
    
        elif player2_stack > player1_stack :
            try :
                if game_data[player2_name] :
                    game_data[player2_name] += 1
            except KeyError :
                game_data[player2_name] = 1

        else : 
            try :
                if game_data[player1_name] :
                    game_data[player1_name] += 0.5
            except KeyError :
                game_data[player1_name] = 0.5

            try :
                if game_data[player2_name] :
                    game_data[player2_name] += 0.5
            except KeyError :
                game_data[player2_name] = 0.5
                

    results.write(json.dumps(game_data))
    results.write("\n")
    


    
