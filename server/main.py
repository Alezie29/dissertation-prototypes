from engine.game_state import GameState
from network.transport import UDPTransport
from network.impairment import ImpairmentInjector
import time

SERVER_PORT = 9999 # Hardcoded as examples, this will be updated later
CLIENT_PORT = 9998
TICK_RATE = 30 # Adjustable variable for better structure

def main():
    game_state = GameState()
    transport = UDPTransport(local_port=SERVER_PORT)
    injector = ImpairmentInjector(latency_ms=0, packet_loss_pct=0)

    while True:
        # Use transport.receive() to check for client input
        received_data = transport.receive()
        if received_data is not None:
            tick = received_data["tick"]

            game_state.entities["player"]["vx"] = received_data["vx"]
            game_state.entities["player"]["vy"] = received_data["vy"]

            response = {"tick": tick, "vx": game_state.entities["player"]["vx"], "vy": game_state.entities["player"]["vy"]} 
            injector.apply(transport.send, response, CLIENT_PORT)

        # Call game_state.step(dt), passing in how much time has elapsed, matching tick rate
        game_state.step(1 / TICK_RATE) # If tick rate is 30, this would be 0.033 (0.033 seconds per loop)
        time.sleep(1 / TICK_RATE) # If this is not added, it would fire until cpu usage burns out

if __name__ == "__main__": # Only run the server if this file is executed directly
    main()