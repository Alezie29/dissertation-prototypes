from strategies.base import SynchronisationStrategy
from engine.game_state import GameState
import copy

class RollbackNetcode(SynchronisationStrategy):
    def __init__(self):
        self.tick_to_state = {}
        self.tick_counter = 0
        self.last_known_input = {"vx": 0, "vy": 0}

    def process_input(self,game_state,input_data):
        # Storing input so future predict method can guess it's still happening
        self.last_known_input = input_data
        # Return a tagged version so the client loop can send it the same way regardless of which strategy is used
        tagged_input = {"seq":self.tick_counter, **input_data}
        return tagged_input

    def reconcile(self, game_state, authoritative_state):
        corrected_tick = authoritative_state["seq"]

        # Get the guess that was stored for this tick
        guessed_input = self.tick_to_state[corrected_tick]["guessed_input"] 

        # Compare to real input. If equal, return early (no correction needed)
        if guessed_input["vx"] == authoritative_state["vx"] and guessed_input["vy"] == authoritative_state["vy"]:
            return False # Guess was right, no prediction needed

        # Restore game state from previous snap shot
        game_state.entities = copy.deepcopy(self.tick_to_state[corrected_tick]["state"])

        # Apply real input to player entity and step 
        game_state.entities["player"]["vx"] = authoritative_state["vx"]
        game_state.entities["player"]["vy"] = authoritative_state["vy"]
        game_state.step(1/30)

        # Loop through every tick after corrected tick, for each one, reapply its stored guessed_input and step forward once, to catch back up to "now"
        for tick in range(corrected_tick +1, self.tick_counter):
            game_state.entities["player"]["vx"] = self.tick_to_state[tick]["guessed_input"]["vx"]
            game_state.entities["player"]["vy"] = self.tick_to_state[tick]["guessed_input"]["vy"]
            game_state.step(1/30) 

        return True # Guess was wrong, state got rewound

    def predict(self, game_state, dt: float):
        guessed_input = self.last_known_input 
        self.tick_to_state[self.tick_counter] = { # Must snapshot before stepping so rollback has a valid state to come back to
            "state": game_state.clone(),
            "guessed_input": guessed_input,
        }
        # Apply the guessed input to the player entity
        game_state.entities["player"]["vx"] = guessed_input["vx"]
        game_state.entities["player"]["vy"] = guessed_input["vy"]

        # Step the simulation forward
        game_state.step(dt)

        # Increment tick_counter
        self.tick_counter += 1  

if __name__ == "__main__":
    rb = RollbackNetcode()
    gs = GameState()

    # Simulate a few predicted ticks with a "wrong" guess
    rb.process_input(gs, {"vx": 5, "vy": 0})  # sets last_known_input
    rb.predict(gs, 1/30)  # tick 0
    rb.predict(gs, 1/30)  # tick 1
    rb.predict(gs, 1/30)  # tick 2

    print("Before reconcile:", gs.entities["player"])
    print("Stored ticks:", list(rb.tick_to_state.keys()))

    # Server says tick 0's REAL input was actually different
    rb.reconcile(gs, {"tick": 0, "vx": 2, "vy": 0})

    print("After reconcile:", gs.entities["player"]) 