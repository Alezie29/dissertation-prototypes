from abc import ABC, abstractmethod


class SynchronisationStrategy(ABC):
    # A client-side strategy, which owns the world the client draws on screen
    def __init__(self):
        self.world = None  # None until the first server state arrives
        self.last_shift = 0.0  # Pixels the player jumped on screen in the latest correction

    @abstractmethod
    def process_input(self, seq, inputs):
        # Called once per tick with the player's six-key input and its number
        raise NotImplementedError

    @abstractmethod
    def predict(self, dt):
        # Called once per tick, after any server states have been applied
        raise NotImplementedError

    @abstractmethod
    def reconcile(self, state):
        # Called for each server state, returns True if the screen had to be corrected
        raise NotImplementedError

    def stats(self):
        # Running totals worth logging, which a strategy can override
        return {}