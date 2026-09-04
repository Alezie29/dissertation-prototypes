from strategies.base import SynchronisationStrategy


class ClientSidePrediction(SynchronisationStrategy):
    def process_input(self, input_data):
        raise NotImplementedError

    def reconcile(self, authoritative_state):
        raise NotImplementedError

    def predict(self, dt: float):
        raise NotImplementedError