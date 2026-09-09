from strategies.base import SynchronisationStrategy
from engine.game_state import GameState


class DeadReckoning(SynchronisationStrategy):
    def process_input(self, game_state, input_data):
        game_state.entities["npc"]["vx"] = input_data["vx"] # Update position
        game_state.entities["npc"]["vy"] = input_data["vy"]

    def reconcile(self, game_state, authoritative_state):
        game_state.entities["npc"] = {**authoritative_state}

    def predict(self, game_state, dt: float):
        game_state.step(dt)  
        # Dead reckoning IS extrapolation from last known velocity, this is exactly what GameState.step() already does for every entity, so there's no need for additional logic beyond a call.
        
if __name__ == "__main__":
    dr = DeadReckoning()
    gs = GameState()

    dr.process_input(gs, {"vx": 4, "vy": 2})
    print("NPC after process_input:", gs.entities["npc"])

    dr.predict(gs, 1/30)
    print("NPC after predict:", gs.entities["npc"])

    dr.reconcile(gs, {"x": 50.0, "y": 20.0, "vx": -1, "vy": -1})
    print("NPC after reconcile:", gs.entities["npc"])