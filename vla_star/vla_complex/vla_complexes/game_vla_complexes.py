import threading
from typing import Optional, Callable
from ..vla_complex import VLA_Complex
from ..vla_complex_state import State

from ..general_dataset import SubDataset

from network.common import send_dict_to_olimn
from vla_star.utilities.extension import VLANet
class StartGame(VLA_Complex):
    recorded: bool
    dataset: Optional[SubDataset] = None
    
    def __init__(self, recorded=False, extension: VLANet=VLANet()):
        super().__init__("startgame", True)
        print(f"[StartGame] Start game VLA Complex initialized.")
        self.recorded = recorded
        ### State ###
        self.state = State(session=[], impression={})

        self.extension = extension

        if self.dataset is None:
            self.dataset = SubDataset("Game", "user")
    
    async def execute(self,):
        """
        Starts the game. Do not do this until the player has agreed.
        """
        print(f"[StartGame] Starting game...")
        json_body = send_dict_to_olimn("game", {
            "game_name": "Test",
            "event": "start_game",
            "player_name": "user" 
        })
        introductory_narrative = json_body["introductory_narrative"]
        print(f"[StartGame] Got introductory message from Game Server {json_body} => {introductory_narrative}")
        self.state.impression = {
            "Game status": f"The game has started for the user. But you must tell them through the `chat` tool what's going on in the game:\n\t(for the user): {introductory_narrative}",
        }
        self.is_available = False
        print(f"[StartGame] This VLA_Complex is no longer available")
        return json_body

class EndGame(VLA_Complex):
    recorded: bool
    dataset: Optional[SubDataset] = None
    
    def __init__(self, recorded=False, extension: VLANet=VLANet()):
        super().__init__("endgame", True)
        print(f"[EndGame] End game VLA Complex initialized.")
        self.recorded = recorded
        ### State ###
        self.state = State(session=[], impression={})

        self.extension = extension

        if self.dataset is None:
            self.dataset = SubDataset("Game", "user")
    
    async def execute(self,):
        """
        Ends the game. Only use this if the game is over.
        """
        print(f"[EndGame] End game...")
        json_body = send_dict_to_olimn("game", {
            "game_name": "Test",
            "event": "end_game",
            "player_name": "user" 
        })

        self.state.impression = {
            "Game status": "The game has ended for the user.",
            "New Instruction": "You should let the user know that they've won through the `chat` tool. Once they are informed you can leave with `suspend` any time, or let the user leave..."
        }

        return {"Result":"You should let the user know that they've won through the `chat` tool. Once they are informed you can leave with `suspend` any time, or let the user leave..."}
        