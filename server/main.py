import sys
from engine.game_state import GameState
from network.transport import UDPTransport
from network.impairment import ImpairmentInjector
from metrics.logger import MetricsLogger
import time

SERVER_PORT = 9999 # Hardcoded as examples, this will be updated later
CLIENT_PORT = 9998
TICK_RATE = 30 # Adjustable variable for better structure

def main():
    if len(sys.argv) < 4:
        print("Please use a valid format: python3 -m server.main <latency_ms> <packet_loss_pct>")
        sys.exit(1)

    latency_ms = int(sys.argv[1])
    packet_loss_pct = float(sys.argv[2])
    trial_id = sys.argv[3] # Adding trial id as an argument, done in client main() too

    game_state = GameState()
    transport = UDPTransport(local_port=SERVER_PORT)
    injector = ImpairmentInjector(latency_ms=latency_ms, packet_loss_pct=packet_loss_pct)
    logger = MetricsLogger(role="server")
    tick = 0

    while True:
        # Use transport.receive() to check for client input
        received_data = transport.receive()
        if received_data is not None:
            seq = received_data["seq"]
            game_state.entities["player"]["vx"] = received_data["vx"]
            game_state.entities["player"]["vy"] = received_data["vy"]

            response = {"seq": seq, "vx": game_state.entities["player"]["vx"], "vy": game_state.entities["player"]["vy"]} 
            injector.apply(transport.send, response, CLIENT_PORT)

            if tick % 5 == 0:
                logger.log_state(tick, (game_state.entities["player"]["x"], game_state.entities["player"]["y"]))

            # print("Server response:", response) # Testing

        # Call game_state.step(dt), passing in how much time has elapsed, matching tick rate
        game_state.step(1 / TICK_RATE) # If tick rate is 30, this would be 0.033 (0.033 seconds per loop)
        tick += 1
        if tick % 5 == 0:
            logger.flush(trial_id) 
        time.sleep(1 / TICK_RATE) # If this is not added, it would fire until cpu usage burns out

if __name__ == "__main__": # Only run the server if this file is executed directly
    main()