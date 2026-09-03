from engine.game_state import GameState
from network.transport import UDPTransport
from network.impairment import ImpairmentInjector
import time

CLIENT_PORT = 9998
SERVER_PORT = 9999
TICK_RATE = 30

def main():
    game_state = GameState()
    transport = UDPTransport(local_port=CLIENT_PORT)
    injector = ImpairmentInjector(latency_ms=0, packet_loss_pct=0)

    hardcoded_move = {"vx": 5, "vy": 0}

    while True:
        injector.apply(transport.send, hardcoded_move, SERVER_PORT) 
        # print("Client sent:", hardcoded_move)  # TEMP DEBUG

        received_data = transport.receive()
        if received_data is not None:
            game_state.entities["player"].update(received_data)

        time.sleep(1 / TICK_RATE)

if __name__ == "__main__":
    main()