import time
import json

class MetricsLogger:
    def __init__(self, role: str, output_dir: str = "logs"):
        self.role = role  # "client" or "server"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.entries = []

    def log_state(self, tick: int, position: tuple):
        self.entries.append({
            "role": self.role,
            "tick": tick,
            "timestamp": time.time(),
            "position": position,
        })

    def log_correction(self, tick: int):
        self.entries.append({
            "role": self.role,
            "tick": tick,
            "timestamp": time.time(),
            "correction": True,
        })

    def flush(self, trial_id: str):
        # Build unique filenames so client/server logs from different trials dont overwrite eachother
        filename = f"{trial_id}_{self.role}.json"
        filepath = self.output_dir / filename

        # Write all entries as JSON
        with open(filepath, "w") as f:
            json.dump(self.entries, f, indent=2)


    def export_error(pos_a: tuple, pos_b: tuple) -> float: # Euclidean distance formula
        dx = pos_a[0] - pos_b[0]
        dy = pos_a[1] - pos_b[1]
        distance = (dx**2 + dy**2) ** 0.5
        return distance