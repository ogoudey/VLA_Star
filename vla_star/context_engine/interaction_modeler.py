
from dataclasses import dataclass
from typing import Callable, Optional, List
from pydantic import BaseModel
from vla_star.vla_complex.vla_complexes.chat import Chat
from vla_star.vla_complex.vla_complexes.vision import Vision


class InteractionModel(BaseModel):
    capability_id: Optional[str] = "default"
    name: str

class InteractionModeler:
    models: List[InteractionModel]

    # sources
    chat_vla_complex: Optional[Chat] = None
    on_new_entity: Optional[Callable] = None

    def __str__(self):
        return f"Interaction Models"

    def __init__(self):
        self.models = []

    def attach_sources(self, context_engine):
        chat_vla_complex = next((x for x in context_engine.vla_complexes if isinstance(x, Chat)), None)
        self.post_engine_initialize(chat_vla_complex=chat_vla_complex)

    def post_engine_initialize(self, chat_vla_complex: Optional[Chat] = None):
        self.chat_vla_complex = chat_vla_complex
        if self.chat_vla_complex is not None:
            self.chat_vla_complex.on_message_received = self.on_chat_message_received
        print(f"[InteractionModeler] Post engine initialize with chat_vla_complex: {self.chat_vla_complex}")


    def on_chat_message_received(self):
        print(f"[InteractionModeler] Chat message received -- potentially updating interaction model for {self.chat_vla_complex.interface.conversation.interlocutor}")
        for model in self.models:
            if model.name == self.chat_vla_complex.interface.conversation.interlocutor:
                # Update the interaction model as needed
                return
        # If no existing model matches, create a new one
        new_model = InteractionModel(
            capability_id=None, # NEED TO DETERMINE
            name=self.chat_vla_complex.interface.conversation.interlocutor
        )
        self.models.append(new_model)
        print(f"[InteractionModeler] New interaction model created: {new_model}. Calling on_new_entity...")
        if self.on_new_entity is not None:
            self.on_new_entity(new_model)


    def get_state(self):
            return [model.model_dump_json() for model in self.models]