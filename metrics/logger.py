import json
import time
from math import hypot
from pathlib import Path


class MetricsLogger:
    def __init__(self, role: str, output_dir: str = "logs"):
        self.role = role  # "client" or "server"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.entries = []

    def _add(self, tick, **fields):
        self.entries.append({"role": self.role, "tick": tick, "timestamp": time.time(), **fields})

    def log_state(self, tick, position):
        self._add(tick, position=position)

    def log_correction(self, tick, shift=0.0):
        # Shift is how many pixels the player jumped on screen when the correction happened
        self._add(tick, correction=True, shift=shift)

    def log_response(self, tick, seconds):
        # Seconds between a movement key going down and the player visibly moving
        self._add(tick, response_s=seconds)

    def log_counters(self, tick, counters):
        # Running totals from the strategy, so the last entry in the file is the final figure
        if counters:
            self._add(tick, counters=counters)

    def flush(self, trial_id: str):
        # Written often, because the controller ends a round by killing the process
        with open(self.output_dir / f"{trial_id}_{self.role}.json", "w") as f:
            json.dump(self.entries, f)


def export_error(pos_a: tuple, pos_b: tuple) -> float:
    # Aggarwal et al. (2004): Euclidean distance between two positions
    return hypot(pos_a[0] - pos_b[0], pos_a[1] - pos_b[1])