import threading

from ..vla_complex import VLA_Complex
from vla_complex_state import State
from displays import log, timestamp, update_activity

import time

class AvaDrive(VLA_Complex):
    # A VLA Complex

    # is initialized in the factory
    def __init__(self, base, tool_name: str):
        self.base = base
        self.default_map = 1

        super().__init__(self.drive, tool_name)
        self.drive_updates_on = False
        self.driving = False

        ### State ###
        self.state = State(session=[], impression={"current position": "Unknown"})
        self.long_term_memory = []

        self.locations_to_tagIds = dict()
        self.descriptions = {
            "cafe": "there is a red block here",
            "desks": "not much here",
            "lab": "a Spot robot dog",
            "home": "a person"
        }
        self.refresh_locations()

    # has a primary "act" method
    def drive(self, location: str):
        print(f"Drive on {location}")
        if location == "Dock":
            self.base.smart_dock()
        elif location == "STOP":
            self.base.stop_robot()
        else:
            try:
                print(f"Driving to {self.locations_to_tagIds[location]} on map {self.default_map}")
                self.state.impression["current destination"] = location
                self.state.impression["current position"] = f"On route to {location}"
                self.update_description_of_local_position()
                self.base.drive_to_tag(self.default_map, self.locations_to_tagIds[location])
            except Exception:
                return (f"Failed to drive to the location. Make sure {location} is one from {list(self.locations_to_tagIds.keys())}, or \"Dock\" or \"STOP\"")
    
    # helper
    def update_description_of_local_position(self):
        try:
            if self.state.impression["current position"] in self.descriptions:
                self.state.impression[f"known objects at {self.state.impression['current position']}"] = self.descriptions[self.state.impression["current position"]]
            else:
                keys_to_del = []
                for k, v in self.state.impression:
                    if "known objects" in k: # lazy
                        keys_to_del.append(k)
                for k in keys_to_del:
                    del self.state.impression[k]
        except Exception as e:
            print(f"Could not update description of local position: {e}")

    # often has ongoing threads
    def run_drive_updates_client(self):
        self.drive_updates_on = True
        while True:
            while self.driving:
                drive_updates = self.base.drive_updates()["data"]["status"] # good for now
                if "COMPLETE" in drive_updates.values():
                    self.state.impression["current position"] = self.state.impression["current destination"]
                    self.state.impression["current destination"] = None
                    self.update_description_of_local_position()
                    self.driving = False
                    self.rerun("Destination reached.")
                    
            time.sleep(1)

    # is called by an agent, with args. (This call must be non-blocking)
    async def execute(self, location: str):
        """
        Drive to a location. This will actually move the Ava robot in physical space.
        :param location: the exact name of the location from the list of locations (required)
        """
        print("Ava Drive called.")
        await super().execute(location)
        if not self.drive_updates_on:
            threading.Thread(target=self.run_drive_updates_client).start()
        self.driving = True
        self.vla(location)
        
        return "Success. Return Immediately."

    # reruns the agent
    def rerun(self, raison):
        rerun_input = {
                "Long term stats": self.long_term_memory,
                "Session information": self.state.session.copy()
            }
        rerun_input["Current drive status"] = raison
        log(f"{self.tool_name} >>> LLM: {rerun_input}", self)
        self.state.session.append({f"{timestamp()} Status":f"{raison}"})

        self.rerun_agent()

    def refresh_locations(self):
        try:
            tags_data = self.base.list_tags(self.default_map)["data"]
        except Exception as e:
            print(f"Could not fetch tags: {e}")
            raise Exception(f"Probably a map error: {e}")
        self.base.pp(tags_data)
        tags_info = tags_data["tags"]

        for id, tag_info in tags_info.items():
            if "tracs" in tag_info["attributes"]:
                self.locations_to_tagIds[tag_info["name"]] = tag_info["id"]
        self.state.impression["locations"] = list(self.locations_to_tagIds.keys())