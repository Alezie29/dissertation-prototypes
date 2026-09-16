# Shared Game Engine Core
import copy 

class GameState:
    def __init__(self):
        # Created a dictionary keyed by "player" and "npc", each value holds that entity's x, y, vx, vy (position and velocity), using a nested dict here for easy lookup
        self.entities = {
        "player": {"x": 0, "y": 0, "vx": 0, "vy": 0},
        "npc": {"x": 0, "y": 0, "vx": 0, "vy": 0},
        }

    def step(self, dt: float):
        # Loop over every entity in self.entities
        for name, data in self.entities.items(): # Makes it so something like Player : X is accessible 
            x = data["x"] # Defining x, y, vx and vy
            y = data["y"]
            vx = data["vx"]
            vy = data["vy"]
            
        # For each one, update its x and y using its velocity and dt (Bernier's extrapolation formula from lit review: P(t) = P0 + V0 * dt)
            nx = x + ( vx * dt ) # New X = old X + (x-velocity * time elapsed)
            ny = y + ( vy * dt ) # New Y = old Y + (y-velocity * time elapsed)

            # Update x and y 
            data["x"] = nx
            data["y"] = ny

    def clone(self):
        # Return a deep copy of self.entities. Deep copy needed — rollback relies on this clone being fully independent. If it shared references with the original, resimulating the rolled-back state would corrupt the current state too.
        return copy.deepcopy(self.entities)


# Unit test to see if the code works
# gs = GameState()
# gs.entities["player"]["vx"] = 5
# gs.step(1.0)
# print(gs.entities["player"])
