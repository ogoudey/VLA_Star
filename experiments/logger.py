import os
from datetime import datetime
from pathlib import Path

def log(participant: str, phase_file: str, data: dict[str, str]) -> None:
    """
    Append survey responses to a phase-specific log file.
    """
    phase_name = Path(phase_file).stem
    survey_name = phase_name + participant
    os.makedirs("logs", exist_ok=True)

    log_file = f"experiments/surveys/{survey_name}.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n[{timestamp}]\n")
        for key, value in data.items():
            f.write(f"{key}: {value}\n")
        f.write("-" * 30 + "\n")