from strategies.base import SynchronisationStrategy
from engine.game_state import GameState


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
    
    def reconcile(self, game_state, authoritative_state):
        confirmed_seq = authoritative_state["seq"]
        
        # Find every key in self.pending_inputs that is <= confirmed_seq
        keys_delete = []
        for k in self.pending_inputs: # Looping through a dict gives its keys
            if k <= confirmed_seq:
                keys_delete.append(k) # Add each key to a seperate list 
        # Delete those keys from self.pending_inputs
        for d in keys_delete:
            self.pending_inputs.pop(d) # Go through the dict and remove each key without throwing error by removing it directly from the dict, hence a list was made first

    def predict(self, dt: float):
        raise NotImplementedError

if __name__ == "__main__":
    cp = ClientSidePrediction()
    gs = GameState()
    print(cp.process_input({"vx": 5, "vy": 0}))
    print(cp.process_input({"vx": 0, "vy": -3}))
    print(cp.pending_inputs)
    cp.process_input({"vx": 1, "vy": 1})
    cp.process_input({"vx": 2, "vy": 2})

    print("Before reconcile:", cp.pending_inputs)
    cp.reconcile(gs, {"seq": 1, "x": 10.0, "y": 0.0})
    print("After reconcile:", cp.pending_inputs)