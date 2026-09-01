from engine.game_state import GameState
from network.transport import UDPTransport
from network.impairment import ImpairmentInjector
from metrics.logger import MetricsLogger

SERVER_PORT = 9999

def main():
    game_state = GameState()
    transport = UDPTransport(local_port=SERVER_PORT)
    # TODO: build the loop