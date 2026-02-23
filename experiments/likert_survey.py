from logger import log

class Survey:
    participant: str
    phase_filename: str

    def __init__(self, participant, phase_filename):
        self.participant = participant
        self.phase_filename = phase_filename

    def phase_survey(self):
        groundedness = input("Did A or B feel more grounded? ")
        log(self.participant, self.phase_filename, {
            
            "groundedness": groundedness
        })


    def comparison_survey(self):
        pass

