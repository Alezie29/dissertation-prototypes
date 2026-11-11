from math import hypot

from engine.rules import NO_INPUT, TICK_DT, new_world, step_world
from strategies.base import SynchronisationStrategy

TOLERANCE = 0.01  # Differences smaller than this are not counted as a correction


def summary(world):
    # The values a player could actually notice changing
    p, n = world["player"], world["npc"]
    return (p["x"], p["y"], p["health"], n["x"], n["health"])


def differs(a, b):
    return any(abs(x - y) > TOLERANCE for x, y in zip(a, b))


def player_shift(a, b):
    # Pixels between the player positions in two summaries
    return hypot(a[0] - b[0], a[1] - b[1])


class ClientSidePrediction(SynchronisationStrategy):
    def __init__(self):
        super().__init__()
        self.world = new_world()  # Starts at once, since the server starts from the same world
        self.pending = {}  # If there is an input number, the server has not confirmed yet
        self.current_seq = -1  # Number of this tick's input
        self.current_input = dict(NO_INPUT)
        self.acked = -1  # Newest input number the server has confirmed
        self.replays = 0  # Server states that were applied, each one followed by a replay
        self.replayed_ticks = 0  # Total ticks re-simulated, which is the cost of this approach

    def process_input(self, seq, inputs):
        self.pending[seq] = inputs
        self.current_seq = seq
        self.current_input = inputs

    def predict(self, dt):
        # Simulate this tick locally, so the player sees the result at once
        step_world(self.world, self.current_input, dt)

    def reconcile(self, state):
        self.last_shift = 0.0
        # Ignore old or duplicate states
        if state["seq"] <= self.acked:
            return False
        self.acked = state["seq"]
        before = summary(self.world)

        # Drop the inputs the server has now applied
        for seq in [s for s in self.pending if s <= state["seq"]]:
            del self.pending[seq]

        # Snap to the server's world, then replay the inputs it has not seen yet
        world = state["world"]
        self.replays += 1
        for seq in sorted(self.pending):
            if seq < self.current_seq:
                step_world(world, self.pending[seq], TICK_DT)
                self.replayed_ticks += 1
        self.world = world

        after = summary(world)
        if differs(before, after):
            self.last_shift = player_shift(before, after)
            return True
        return False

    def stats(self):
        return {"replays": self.replays, "replayed_ticks": self.replayed_ticks}


if __name__ == "__main__":
    right = {**NO_INPUT, "right": True}

    def run(server_input):
        # The client holds right for 10 ticks, the server applied inputs 0 to 4 using server_input
        cp = ClientSidePrediction()
        server = new_world()
        for _ in range(5):
            step_world(server, server_input, TICK_DT)
        corrected = None
        for seq in range(10):
            cp.process_input(seq, right)
            if seq == 9:
                corrected = cp.reconcile({"seq": 4, "tick": 5, "world": server})
            cp.predict(TICK_DT)
        return corrected, round(cp.world["player"]["x"], 2)

    print("Heard everything:", run(right))  # TESTING expecting (False, 183.33)
    print("Server missed inputs:", run(NO_INPUT))  # TESTING expecting (True, 166.67)