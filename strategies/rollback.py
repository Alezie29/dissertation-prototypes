import copy

from engine.rules import NO_INPUT, TICK_DT, new_world, step_world
from strategies.base import SynchronisationStrategy
from strategies.prediction import differs, player_shift, summary

HISTORY_TICKS = 120  # Two seconds of snapshots is more than any latency tier needs


class RollbackNetcode(SynchronisationStrategy):
    def __init__(self):
        super().__init__()
        self.world = new_world()  # Starts at once, since the server starts from the same world
        self.history = {}  # If there is a tick number, make a snapshot of the world after that tick
        self.inputs = {}  # If there is a tick number, the input is used on that tick
        self.current_seq = -1  # Number of this tick's input
        self.current_input = dict(NO_INPUT)
        self.acked = -1  # Newest input number the server has confirmed
        self.rewinds = 0  # How many times a prediction turned out wrong
        self.replayed_ticks = 0  # Total ticks re-simulated, which is the cost of rolling back

    def process_input(self, seq, inputs):
        self.inputs[seq] = inputs
        self.current_seq = seq
        self.current_input = inputs

    def predict(self, dt):
        # Simulate this tick locally, then keep a snapshot so it can be rewound to later
        step_world(self.world, self.current_input, dt)
        self.history[self.current_seq] = copy.deepcopy(self.world)
        # Drop snapshots too old to ever be rewound to
        old = self.current_seq - HISTORY_TICKS
        self.history.pop(old, None)
        self.inputs.pop(old, None)

    def reconcile(self, state):
        self.last_shift = 0.0
        # Ignore old or duplicate states
        if state["seq"] <= self.acked:
            return False
        self.acked = state["seq"]
        seq = state["seq"]
        server_world = state["world"]

        # Compare the server's world with what this client predicted for the same tick
        predicted = self.history.get(seq)
        if predicted is not None and not differs(summary(predicted), summary(server_world)):
            return False  # The prediction was right, so nothing is rewound

        # The prediction was wrong, so go back to the server's world and replay the newer inputs
        before = summary(self.world)
        world = server_world
        self.history[seq] = copy.deepcopy(world)
        for s in range(seq + 1, self.current_seq):  # The current tick is left out, because predict() steps it next
            step_world(world, self.inputs.get(s, NO_INPUT), TICK_DT)
            self.history[s] = copy.deepcopy(world)
            self.replayed_ticks += 1
        self.world = world
        self.rewinds += 1

        # Only count it as a correction if what the player sees actually changed
        after = summary(world)
        if differs(before, after):
            self.last_shift = player_shift(before, after)
            return True
        return False

    def stats(self):
        return {"replays": self.rewinds, "replayed_ticks": self.replayed_ticks}


if __name__ == "__main__":
    right = {**NO_INPUT, "right": True}

    def run(server_input):
        # The client holds right for 10 ticks, the server applied inputs 0 to 4 using server_input
        rb = RollbackNetcode()
        server = new_world()
        for _ in range(5):
            step_world(server, server_input, TICK_DT)
        corrected = None
        for seq in range(10):
            rb.process_input(seq, right)
            if seq == 9:
                corrected = rb.reconcile({"seq": 4, "tick": 5, "world": server})
            rb.predict(TICK_DT)
        return corrected, round(rb.world["player"]["x"], 2), rb.rewinds

    print("Heard everything:", run(right))  # TESTING expect (False, 183.33, 0)
    print("Server missed inputs:", run(NO_INPUT))  # TESTING expect (True, 166.67, 1)