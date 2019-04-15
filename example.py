from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from Group19Player import Group19Player

#TODO:config the config as our wish
config = setup_config(max_round=1000, initial_stack=10000, small_blind_amount=10)

config.register_player(name="AlwaysRaisedPlayer", algorithm=RaisedPlayer())
config.register_player(name="Group19Player", algorithm=Group19Player())

game_result = start_poker(config, verbose=0)
