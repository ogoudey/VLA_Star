import os
from typing import Any
from datetime import datetime
from pathlib import Path
import json

total_activity = dict()

def timestamp():
    return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"

if os.path.exists("logs"):
    for filename in os.listdir("logs"):
        if filename.endswith(".log"):
            file_path = os.path.join("logs", filename)
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"\n\n\n\n{timestamp()}\t\t\t\t__ New chunk started __\n")
            #print(f"Appended {10} blank lines to {filename}")


"""
watch -n 0.1 'tail -n 20 logs/context.json'
"""
def show_context(context,):
    display_path = os.path.join("logs", f"context.json")

    with open(display_path, "w", encoding="utf-8") as f:
        json.dump(
            context,
            f,
            indent=2,
            sort_keys=True,
            default=str,   # safety for non-JSON types
        )

"""
watch -n 0.1 'tail -n 20 logs/display.json'
"""
def update_activity(data, self=Any, exit=False):
    display_path = os.path.join("logs", f"display.json")
    if not self in total_activity:
        total_activity[str(self)] = data
    update = {str(self): data}
    total_activity.update(update)
    if exit:
        del total_activity[str(self)]
    with open(display_path, "w", encoding="utf-8") as f:
        json.dump(
            total_activity,
            f,
            indent=2,
            sort_keys=True,
            default=str,   # safety for non-JSON types
        )

def log(text: str, self=Any):
    if not self.__class__.__base__ is object:
        self = self.__class__.__base__
    log_name = str(self)
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Define log file path
    log_path = os.path.join("logs", f"{log_name}.log")
    
    # Timestamp the message
    formatted_message = f"{timestamp()} {text}\n"
    
    # Append the message to the log file
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(formatted_message)