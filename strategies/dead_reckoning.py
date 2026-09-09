from strategies.base import SynchronisationStrategy


class DeadReckoning(SynchronisationStrategy):
    def process_input(self, input_data):
        # TODO: dead reckoning doesn't need buffering like prediction did —
        # does this need real logic, or does it stay minimal...
        raise NotImplementedError

    def reconcile(self, game_state, authoritative_state):
        # TODO
        raise NotImplementedError

    def predict(self, game_state, dt: float):
        # TODO
        raise NotImplementedError