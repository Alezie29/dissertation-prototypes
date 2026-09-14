from strategies.base import SynchronisationStrategy


class RollbackNetcode(SynchronisationStrategy):
    def __init__(self):
        # TODO: History of past states, a record of predicted vs actual inputs per frame?
        pass

    def process_input(self, game_state, input_data):
        # TODO: Rollback needs to record inputs per-frame, likely similar to prediction's sequence-numbered buffer, but used differently (for rewinding, not for replay-on-reconcile)
        raise NotImplementedError

    def reconcile(self, game_state, authoritative_state):
        # TODO: Compare the guessed input for a given frame against what really happened, if wrong, rewind + resimulate
        raise NotImplementedError

    def predict(self, game_state, dt: float):
        # TODO: Simulate forward using the BEST GUESS input (likely "same as last known input") since no confirmation has arrived yet
        raise NotImplementedError