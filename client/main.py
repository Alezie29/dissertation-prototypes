from engine.game_state import GameState
from network.transport import UDPTransport
from network.impairment import ImpairmentInjector
from strategies.prediction import ClientSidePrediction
from strategies.rollback import RollbackNetcode
import time

CLIENT_PORT = 9998
SERVER_PORT = 9999
TICK_RATE = 2

def main():
    game_state = GameState()
    transport = UDPTransport(local_port=CLIENT_PORT)
    injector = ImpairmentInjector(latency_ms=0, packet_loss_pct=0)
    strategy = RollbackNetcode()

    # process_input() is called only once, not every tick, as it represents a discrete input event (when the player makes a keystroke), not a conitnuous process.
    # TODO: once a real keyboard is wired in, this should only be called again when the player's input actually changes, not on a fixed schedule.

    current_input = {"vx": 5, "vy": 0}
    tagged_input = strategy.process_input(game_state, current_input)

    while True:
        # Rollback resends the raw current_input each tick, tagged with the tick it's associated with, so the server can confirm/deny it later
        tagged_input = {"tick": strategy.tick_counter, **current_input}
        injector.apply(transport.send, tagged_input, SERVER_PORT)

        # predict() runs every tick — guesses, snapshots, steps, increments tick
        strategy.predict(game_state, 1 / TICK_RATE)

        print("Client player state:", game_state.entities["player"], "tick:", strategy.tick_counter) # Testing for final implementation of all 3 strategies

        # If the server sends back a correction, reconcile() rewinds/resimulates
        received_data = transport.receive()
        if received_data is not None:
            strategy.reconcile(game_state, received_data)

        time.sleep(1 / TICK_RATE)

if __name__ == "__main__":
    main()