from engine.rules import FIGHTER_W, TICK_DT, WIDTH
from strategies.base import SynchronisationStrategy

MAX_EXTRAPOLATION_TICKS = 15  # Stop guessing after a quarter of a second when there is no news


class DeadReckoning(SynchronisationStrategy):
    def __init__(self):
        super().__init__()
        self.last_tick = None  # Server tick of the newest state accepted
        self.last_server_npc_x = 0.0  # Tosakan's x in that state
        self.npc_vx = 0.0  # Estimated Tosakan speed, measured in pixels per second
        self.missed_ticks = 0  # Local ticks since a state last arrived
        self.fresh = False  # True if a state arrived this tick

    def process_input(self, seq, inputs):
        # Nothing to do, because the player is never simulated locally, only Tosakan is
        pass

    def reconcile(self, state):
        # Ignore old or duplicate states
        if self.last_tick is not None and state["tick"] <= self.last_tick:
            return False
        new_npc_x = state["world"]["npc"]["x"]
        if self.last_tick is not None:
            # Speed from the last two server positions, which stays correct even if states were lost between them
            elapsed = (state["tick"] - self.last_tick) * TICK_DT
            self.npc_vx = (new_npc_x - self.last_server_npc_x) / elapsed
        self.last_tick = state["tick"]
        self.last_server_npc_x = new_npc_x
        self.world = state["world"]  # Draw exactly what the server says
        self.fresh = True
        return False  # This baseline never predicts the player, so it never corrects anything

    def predict(self, dt):
        if self.world is None:
            return
        if self.fresh:
            self.missed_ticks = 0
            self.fresh = False
            return
        # No state this tick, so move Tosakan along his last known speed for a short while
        self.missed_ticks += 1
        if self.missed_ticks <= MAX_EXTRAPOLATION_TICKS:
            npc = self.world["npc"]
            npc["x"] = max(0, min(npc["x"] + self.npc_vx * dt, WIDTH - FIGHTER_W))


if __name__ == "__main__":
    from engine.rules import new_world

    # Feed two fake states one tick apart, with Tosakan moving 200 pixels per second
    dr = DeadReckoning()
    for tick, x in ((1, 600.0), (2, 600.0 + 200 * TICK_DT)):
        world = new_world()
        world["npc"]["x"] = x
        dr.reconcile({"seq": tick, "tick": tick, "world": world})
        dr.predict(TICK_DT)
    print("After two states:", round(dr.world["npc"]["x"], 2)) 
    for _ in range(3):
        dr.predict(TICK_DT)
    print("After 3 missed ticks:", round(dr.world["npc"]["x"], 2))  
    for _ in range(30):
        dr.predict(TICK_DT)
    print("After 33 missed ticks:", round(dr.world["npc"]["x"], 2))  