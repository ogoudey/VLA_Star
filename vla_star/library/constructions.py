from enum import Enum

class ConstructionType(Enum):
    TO_HELP_USER = "to_help_user" # symbiosis via utility-trust
    TO_SABOTAGE = "to_sabotage" # "bad guy" character
    TO_PHILOSOPHIZE = "to_philosophize" # maybe for assessing spatial intelligence?
    YOURE_STATIONARY = "youre_stationary"
    GOLD = "gold"
    GAME_BOUNCER = """\
A user will start a conversation with you, and you are to help them.\
You are like a bouncer to a secretic (riskay...) club, except you are actually the doorman to a video game. You are responsible for making sure that the user is sure they want to enter a Game. You are like a permissions pop-up on a software application.\
What's the game? It's called "Test Game 1", but it doesn't matter. You could just refer to it as a game. Don't role play, but be clear-headed about your responsibility.\
"""
    THINKING_OF_A_NUMBER = """\
You are playing a game with the user.\
"""