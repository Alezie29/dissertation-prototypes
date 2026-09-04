from strategies.base import SynchronisationStrategy


class ClientSidePrediction(SynchronisationStrategy):
    def __init__(self):
        self.sequence_number = sequence_number
        self.pending_inputs = pending_inputs
        sequence_number = 0
        pending_inputs = {}

    def process_input(self, input_data):
        # TODO: Given some input data, tag it with the current sequence_number
        # Store it in pending_inputs
        # Increment sequence_number for next time
        # Return the tagged input

    def reconcile(self, authoritative_state):
        raise NotImplementedError

    def predict(self, dt: float):
        raise NotImplementedError