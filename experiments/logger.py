import os
from datetime import datetime


def log(phase_name: str, data: dict[str, str]) -> None:
    """
    Append survey responses to a phase-specific log file.
    """

    os.makedirs("logs", exist_ok=True)

    log_file = f"logs/{phase_name}.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n[{timestamp}]\n")
        for key, value in data.items():
            f.write(f"{key}: {value}\n")
        f.write("-" * 30 + "\n")
