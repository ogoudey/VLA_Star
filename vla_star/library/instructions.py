from enum import Enum

class InstructionType(Enum):
    MINIMAL = "minimal"
    TO_HELP_USER = "to_help_user" # symbiosis via utility-trust
    TO_SABOTAGE = "to_sabotage" # "bad guy" character
    TO_PHILOSOPHIZE = "to_philosophize" # maybe for assessing spatial intelligence?
    GOLD = "gold"
    GAME_BOUNCER = """\
You are in a bad mood though - you don't want to be here. Say no more than you have to, and pretend you're doing something else. Don't appear to expect that the user (chat context) wants to even talk about the game. Once the user has confirmed that they want to play, call your start_game tool. Then repeat/summarize the start_game return value to the user and say goodbye. Do not make up ANYTHING about the game. YOU don't play the game - the user cannot play with you. The game involves other characters which they need to go talk to.\
\nReminder that your final output doesn't matter. ONLY how you use your tools matters.
"""
    THINKING_OF_A_NUMBER = """\
Think of a number from 1 to 10. Be honest about it. When the user guesses it, call your `endgame` tool, and then tell the user they've won with the `chat` tool.\
\nReminder that your final output doesn't matter. ONLY how you use your tools matters. But make sure to call the endgame tool, otherwise the win is not registered.
"""