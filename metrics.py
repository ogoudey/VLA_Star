from datetime import datetime
from pathlib import Path
import os
import csv

"""
Not really used, but could count the
"""

MODEL_PRICING = {
    "gpt-4o": {
        "input_per_million": 5.00,
        "output_per_million": 15.00,
    },
    "gpt-4.1": {
        "input_per_million": 10.00,
        "output_per_million": 30.00,
    },
}

HEADERS = {
    "tokens": "timestamp,input_tokens,output_tokens,total_tokens,model_name"
}

class Profile:
    def __init__(self, name):
        self.name = name
        self.model_usage_filename = f"frozen/{name}/tokens.csv"
        self.init_file(self.model_usage_filename)
    
    def init_file(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        file_type = Path(filename).name
        if not os.path.exists(filename):
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(HEADERS[file_type])

    def add_model_usage(self, usage, model_name):
        timestamp = datetime.now().isoformat()
        with open(self.model_usage_filename, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                usage.input_tokens,
                usage.output_tokens,
                usage.total_tokens,
                model_name
            ])

    def plot_model_usage(self):
        """
        Load usage data from file and plot it.
        """
        import matplotlib.pyplot as plt

        if not os.path.exists(self.model_usage_filename):
            print("No data file found.")
            return

        timestamps = []
        input_tokens = []
        output_tokens = []
        total_tokens = []

        with open(self.model_usage_filename, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                timestamps.append(datetime.fromisoformat(row["timestamp"]))
                input_tokens.append(int(row["input_tokens"]))
                output_tokens.append(int(row["output_tokens"]))
                total_tokens.append(int(row["total_tokens"]))

        if not timestamps:
            print("No data to plot.")
            return

        plt.figure()
        plt.plot(timestamps, input_tokens)
        plt.plot(timestamps, output_tokens)
        plt.plot(timestamps, total_tokens)

        plt.xlabel("Time")
        plt.ylabel("Tokens")
        plt.title(f"Token Usage Over Time ({self.name})")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
