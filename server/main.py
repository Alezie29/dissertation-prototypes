from engine.game_state import GameState
from network.transport import UDPTransport
import time

SERVER_PORT = 9999 # Hardcoded as examples, this will be updated later
CLIENT_PORT = 9998
TICK_RATE = 30 # Adjustable variable for better structure

def main():
    game_state = GameState()
    transport = UDPTransport(local_port=SERVER_PORT)

    while True:
        # Use transport.receive() to check for client input
        received_data = transport.receive()
        if received_data is not None:
        # If not None, apply it to game_state.entities["player"]
        # (e.g. updating vx/vy based on what the client sent)
            game_state.entities["player"].update(received_data) # Updating the players key in dict with the updated data

            # Call game_state.step(dt) — pass in how much time has elapsed, matching tick rate
            game_state.step(1 / TICK_RATE) # If tick rate is 30, this would be 0.033 (0.033 seconds per loop)
            # Use transport.send(...) to send game_state.entities back to the client
            transport.send(game_state.entities, CLIENT_PORT)
            time.sleep(1 / TICK_RATE) # If this is not added, it would fire until cpu usage burns out

if __name__ == "__main__": # Only run the server if this file is executed directly
    main()