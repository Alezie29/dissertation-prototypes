from strategies.base import SynchronisationStrategy


class RollbackNetcode(SynchronisationStrategy):
    def __init__(self):
        self.tick_to_state = {}
        self.tick_counter = 0
        self.last_known_input = {"vx": 0, "vy": 0}
        

    def process_input(self, game_state, input_data):
        # TODO: Rollback needs to record inputs per-frame, likely similar to prediction's sequence-numbered buffer, but used differently (for rewinding, not for replay-on-reconcile)
        raise NotImplementedError

    def reconcile(self, game_state, authoritative_state):
        # TODO: Compare the guessed input for a given frame against what really happened, if wrong, rewind + resimulate
        raise NotImplementedError

    def predict(self, game_state, dt: float):
        # TODO: 1. figure out the guessed input (last known input, or a default if none yet)
        # TODO: 2. snapshot the CURRENT state (before stepping) into tick_to_state, tagged with tick_counter
        # TODO: 3. apply the guessed input to the npc entity
        # TODO: 4. step the simulation forward
        # TODO: 5. increment tick_counter