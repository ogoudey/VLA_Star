
from dataclasses import dataclass
from typing import Optional, List
from vla_star.vla_complex.vla_complexes.vision import Vision
from pydantic import BaseModel
from vla_star.context_engine.interaction_modeler import InteractionModeler


class CapabilityDefinition(BaseModel):
    capability_id: Optional[str]
    definition: Optional[str] = None

class CapabilityModeler:
    models: List[CapabilityDefinition]

    # sources
    interaction_modeler: Optional[InteractionModeler] = None
    vision_vla_complex: Optional[Vision] = None

    def __str__(self):
        return f"Capability Models"

    def __init__(self):
        self.models = []

    def attach_sources(self, context_engine):
        interaction_modeler = next((x for x in context_engine.standalone_impressions if isinstance(x, InteractionModeler)), None)
        vision_vla_complex = next((x for x in context_engine.vla_complexes if isinstance(x, Vision)), None)
        self.post_engine_initialize(interaction_modeler=interaction_modeler, vision_vla_complex=vision_vla_complex)

    def post_engine_initialize(self, interaction_modeler: Optional[InteractionModeler] = None, vision_vla_complex: Optional[Vision] = None):
        self.interaction_modeler = interaction_modeler
        if self.interaction_modeler is not None:
            self.interaction_modeler.on_new_entity = self.on_new_interaction_model
        self.vision_vla_complex = vision_vla_complex
        if self.vision_vla_complex is not None:
            self.vision_vla_complex.on_new_embodiment_detected = self.on_new_embodiment_detected
        print(f"[CapabilityModeler] Post engine initialize with interaction_modeler: {self.interaction_modeler}, vision_vla_complex: {self.vision_vla_complex}")

    def on_new_embodiment_detected(self):
        print(f"[CapabilityModeler] New embodiment detected -- updating capability model for {self.vision_vla_complex.interface.embodiment}")

    def on_new_interaction_model(self, new_model):
        print(f"[CapabilityModeler] New interaction model detected: {new_model.name}. Getting capability {new_model.capability_id}")

        # TODO Affirm XP package works, then use its network.

        self.models.append(CapabilityDefinition(capability_id=new_model.capability_id, definition="This thing can talk!"))

    def get_state(self):
        return [model.model_dump_json() for model in self.models]