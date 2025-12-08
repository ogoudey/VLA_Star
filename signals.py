from dataclasses import dataclass
### SIGNALS
@dataclass
class RecordDatasetSignal:
    TASK: str = ""
    DATASET_NAME: str = ""
    RUNNING_LOOP: bool = True
    RUNNING_E: bool = True

OK="OK"
CONTINUE="CONTINUE"
RERUN="RERUN"

DONE="DONE"

class VLASignal:
    INSTRUCTION: str

    FLAG: str = "GO"


#
#   state -> VLM -> status
#
#   status -> Agent check -> check
#


### CHECKS
CONTINUE = "CONTINUE"
RERUN = "RERUN"