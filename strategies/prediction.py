from strategies.base import SynchronisationStrategy


class ClientSidePrediction(SynchronisationStrategy):
    def __init__(self):
        self.sequence_number = 0
        self.pending_inputs = {}

    def process_input(self, input_data):
        seq = self.sequence_number
        # Given some input data, tag it with the current sequence_number and store it in pending_inputs with sequence_number as key
        self.pending_inputs[seq] = input_data
        # Increment sequence_number for next time
        self.sequence_number += 1
        # Return the tagged input
        tagged_input = {"seq": seq, **input_data}
        return tagged_input
    
    def reconcile(self, authoritative_state):
        raise NotImplementedError

    def predict(self, dt: float):
        raise NotImplementedError

if __name__ == "__main__":
    cp = ClientSidePrediction()
    print(cp.process_input({"vx": 5, "vy": 0}))
    print(cp.process_input({"vx": 0, "vy": -3}))
    print(cp.pending_inputs)