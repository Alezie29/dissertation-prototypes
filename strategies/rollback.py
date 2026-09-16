from strategies.base import SynchronisationStrategy


class RollbackNetcode(SynchronisationStrategy):
    def __init__(self):
        self.tick_to_state = {}
        self.tick_counter = 0
        self.last_known_input = {"vx": 0, "vy": 0}

    def process_input(self, game_state, input_data):
        self.last_known_input = input_data # Simply use the last known input from the player as the last known input state for rollback to come back to

    def reconcile(self, game_state, authoritative_state):
        corrected_tick = authoritative_state["tick"]

        # Get the guess that was stored for this tick
        guessed_input = self.tick_to_state[corrected_tick]["guessed_input"] 

        # Compare to real input. If equal, return early (no correction needed)
        if guessed_input["vx"] == authoritative_state["vx"] and guessed_input["vy"] == authoritative_state["vy"]:
            return

        # TODO: Restore game state from previous snap shot
        # TODO: Apply real input to player entity and step 
        # TODO: Loop through every tick after corrected tick, for each one, reapply its stored guessed_input and step forward once, to catch back up to "now"
    
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