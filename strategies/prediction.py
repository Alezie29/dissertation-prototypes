from strategies.base import SynchronisationStrategy
from engine.game_state import GameState


class ClientSidePrediction(SynchronisationStrategy):
    def __init__(self):
        self.sequence_number = 0
        self.pending_inputs = {}
        self.current_input = {"vx": 0, "vy": 0}

    def process_input(self, game_state, input_data):
        seq = self.sequence_number
        # Given some input data, tag it with the current sequence_number and store it in pending_inputs with sequence_number as key
        self.pending_inputs[seq] = input_data
        # Increment sequence_number for next time
        self.sequence_number += 1
        # Return the tagged input
        tagged_input = {"seq": seq, **input_data}
        self.current_input = input_data
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

        # authoritative_state's x and y — only those two keys, nothing else
        game_state.entities["player"]["x"] = authoritative_state["x"]
        game_state.entities["player"]["y"] = authoritative_state["y"]

        for n in self.pending_inputs.values(): # Loop through remaining pending inputs
            game_state.entities["player"]["vx"] = n["vx"] # Update velocities
            game_state.entities["player"]["vy"] = n["vy"]            
            game_state.step(1/30) # Move forward a step
        # Prediciton always correct (unlike rollback), so this metric isn't directly comparable between the two
        return True

    def predict(self, game_state, dt: float):
        game_state.entities["player"]["vx"] = self.current_input["vx"] # Update position
        game_state.entities["player"]["vy"] = self.current_input["vy"]
        game_state.step(dt) # Move forward a step

if __name__ == "__main__":
    cp = ClientSidePrediction()
    gs = GameState()

    cp.process_input({"vx": 5, "vy": 0})
    cp.process_input({"vx": 0, "vy": -3})
    cp.process_input({"vx": 1, "vy": 1})
    cp.process_input({"vx": 2, "vy": 2})

    print("Player state before:", gs.entities["player"])
    cp.reconcile(gs, {"seq": 1, "x": 10.0, "y": 5.0})
    print("Player state after reconcile:", gs.entities["player"])
    print("Remaining buffer:", cp.pending_inputs)

    cp.predict(gs, {"vx": 3, "vy": -1}, 1/30)
    print("Player state after predict:", gs.entities["player"])