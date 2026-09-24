from engine.game_state import GameState
from network.transport import UDPTransport
from network.impairment import ImpairmentInjector
from strategies.prediction import ClientSidePrediction
from strategies.rollback import RollbackNetcode
from metrics.logger import MetricsLogger
import time
import sys

CLIENT_PORT = 9998
SERVER_PORT = 9999
TICK_RATE = 30

STRATEGY_MAP = {
    "prediction" : ClientSidePrediction,
    "rollback" : RollbackNetcode,
}

def main():
    if len(sys.argv) < 4: # If user inputs an invalid format in the command line
        print("Please use a valid format for the toolkit: python3 -m client.main <strategy_name> <latency_ms> <packet_loss_pct>")
        sys.exit(1)

    strategy_name = sys.argv[1]
    if strategy_name not in STRATEGY_MAP: # Make sure the user inputs a valid strategy name
        print("Invalid strategy name, please double check for typos!")
        sys.exit(1)

    latency_ms = int(sys.argv[2]) # Turn latency and packet loss into ints and float (string would cause typeerror)
    packet_loss_pct = float(sys.argv[3]) # Can now use latency and Packet loss as command line arguments

    strategy_class = STRATEGY_MAP[strategy_name]
    strategy = strategy_class()

    game_state = GameState()
    transport = UDPTransport(local_port=CLIENT_PORT)
    injector = ImpairmentInjector(latency_ms=latency_ms, packet_loss_pct=packet_loss_pct)
    logger = MetricsLogger(role="client")

    current_input = {"vx": 5, "vy": 0}
    tagged_input_dict = strategy.process_input(game_state, current_input)

    while True:
        # Resending the same tagged_input_dict every tick protects against packet loss regardless of which strategy is used
        injector.apply(transport.send, tagged_input_dict, SERVER_PORT)

        # predict() runs every tick — guesses, snapshots, steps, increments tick
        strategy.predict(game_state, 1 / TICK_RATE)

        # print("Client player state:", game_state.entities["player"], "tick:", strategy.tick_counter) # Testing 

        # If the server sends back a correction, reconcile() rewinds/resimulates
        received_data = transport.receive()
        if received_data is not None:
            corrected = strategy.reconcile(game_state, received_data)
            if corrected:
                logger.log_correction(received_data["seq"])
                # Logs correction to compare how often each strategy gets it wrong

        time.sleep(1 / TICK_RATE)

if __name__ == "__main__":
    main()