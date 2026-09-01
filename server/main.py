from engine.game_state import GameState
from network.transport import UDPTransport
from network.impairment import ImpairmentInjector
import time

SERVER_PORT = 9999
CLIENT_PORT = 9998
TICK_RATE = 30

def main():
    game_state = GameState()
    transport = UDPTransport(local_port=SERVER_PORT)

    while True:
        # TODO: use transport.receive() to check for client input
        # TODO: if it's not None, apply it to game_state.entities["player"]
        #       (e.g. update vx/vy based on what the client sent)

        # TODO: call game_state.step(dt) — pass in how much time has elapsed, likely matching tick rate

        # TODO: use transport.send(...) to send game_state.entities back to the client

        time.sleep(1 / TICK_RATE)

if __name__ == "__main__":
    main()