import os
import json
from typing import Optional

def get_manifest():
    file_path = os.path.expanduser("~/.vla_stars.jsonl")

    if not os.path.exists(file_path):
        return []

    vla_stars_manifest = []
    with open(file_path, "r") as f:
        for line in f:
            if line.strip():
                vla_stars_manifest.append(json.loads(f))

    return vla_stars_manifest

def save_manifest(vla_stars_manifest):
    file_path = os.path.expanduser("~/.vla_stars.jsonl")
    
    # Open with "w" to overwrite or "a" to append
    with open(file_path, "w", encoding="utf-8") as f:
        for obj in vla_stars_manifest:
            # Convert dict to string and append a newline
            f.write(json.dumps(obj) + "\n")

def update_manifest(name: str, new_status: str, message: Optional[str] = None):
    current_vla_stars_manifest = get_manifest()
    next_vla_stars_manifest = []

    existent_data_for_vla_star = None
    for vla_star_data in current_vla_stars_manifest:
        if vla_star_data["name"] == name:
            existent_data_for_vla_star = vla_star_data
        else:
            next_vla_stars_manifest.append(vla_star_data)
    
    if not existent_data_for_vla_star:
        message = "..." if not message else message
        current_vla_stars_manifest.append({
            "name": name,
            "status": new_status,
            "message": message 
        })
    else:
        message = existent_data_for_vla_star["message"] if not message else message
        
        current_vla_stars_manifest.append({
            "name": name,
            "status": new_status,
            "message": message 
        })
    