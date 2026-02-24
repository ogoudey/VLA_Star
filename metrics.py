from datetime import datetime
import matplotlib.pyplot as plt
import os
import csv

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

class Profile:
    def __init__(self, name):
        self.name = name
        self.filename = f"frozen/{name}/tokens.csv"
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        if not os.path.exists(self.filename):
            with open(self.filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "input_tokens",
                    "output_tokens",
                    "total_tokens",
                    "model_name"
                ])

    def add(self, usage, model_name):


        timestamp = datetime.now().isoformat()

        with open(self.filename, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                usage.input_tokens,
                usage.output_tokens,
                usage.total_tokens,
                model_name
            ])

    def plot(self):
        """
        Load usage data from file and plot it.
        """

        if not os.path.exists(self.filename):
            print("No data file found.")
            return

        timestamps = []
        input_tokens = []
        output_tokens = []
        total_tokens = []

        with open(self.filename, "r") as f:
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
