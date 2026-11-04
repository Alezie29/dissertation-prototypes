from abc import ABC, abstractmethod


class SynchronisationStrategy(ABC):
    # Purely a client-side strategy
    def __init__(self):
        self.world = None  # None until the first server state arrives

    @abstractmethod
    def process_input(self, seq, inputs):
        # Called once per tick, with the player's six-key input and its number
        raise NotImplementedError

    @abstractmethod
    def predict(self, dt):
        # Called once per tick, after any server states have been applied
        raise NotImplementedError

    @abstractmethod
    def reconcile(self, state):
        # Called for each server state, returns True if the screen had to be corrected
        raise NotImplementedError