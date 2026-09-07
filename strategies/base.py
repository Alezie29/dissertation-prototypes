from abc import ABC, abstractmethod


class SynchronisationStrategy(ABC):
    @abstractmethod
    def process_input(self, input_data):
        raise NotImplementedError

    @abstractmethod
    def reconcile(self, game_state, authoritative_state):
        raise NotImplementedError

    @abstractmethod
    def predict(self, game_state, dt: float):
        raise NotImplementedError 