from strategies.base import SynchronisationStrategy


class RollbackNetcode(SynchronisationStrategy):
    def __init__(self):
        self.tick_to_state = {}
        self.tick_counter = 0
        self.last_known_input = {"vx": 0, "vy": 0}

    def process_input(self, game_state, input_data):
        self.last_known_input = input_data # Simply use the last known input from the player as the last known input state for rollback to come back to

    def reconcile(self, game_state, authoritative_state):
        # TODO: Compare the guessed input for a given frame against what really happened, if wrong, rewind + resimulate
        raise NotImplementedError

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