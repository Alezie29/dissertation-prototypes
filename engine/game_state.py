# Shared Game Engine Core
class GameState:
    def __init__(self):
        # TODO: create a dictionary here, keyed by "player" and "npc"
        # Each value should itself be some structure holding that
        # entity's x, y, vx, vy (position and velocity)
        #
        # What data type holds each entity's
        # info? A nested dict? A small class?
        self.entities = {}  # <- replace this with real starting data

    def step(self, dt: float):
        # TODO: loop over every entity in self.entities
        # For each one, update its x and y using its velocity and dt
        # (Bernier's extrapolation formula from lit review:
        # P(t) = P0 + V0 * dt)
        pass

    def clone(self):
        # TODO: return a deep copy of self.entities
        # Deep copy needed — rollback relies on this clone being fully
        # independent. If it shared references with the original,
        # resimulating the rolled-back state would corrupt the current
        # state too.
        pass