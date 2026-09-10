from engine.game_state import GameState
from network.transport import UDPTransport
from network.impairment import ImpairmentInjector
from strategies.prediction import ClientSidePrediction
import time

CLIENT_PORT = 9998
SERVER_PORT = 9999
TICK_RATE = 30

def main():
    game_state = GameState()
    transport = UDPTransport(local_port=CLIENT_PORT)
    injector = ImpairmentInjector(latency_ms=0, packet_loss_pct=0)
    strategy = ClientSidePrediction()

    # process_input() is called only once, not every tick, as it represents a discrete input event (when the player makes a keystroke), not a conitnuous process.
    # TODO: once a real keyboard is wired in, this should only be called again when the player's input actually changes, not on a fixed schedule.

    current_input = {"vx": 5, "vy": 0}
    tagged_input = strategy.process_input(game_state, current_input)

    while True:
        # The same tagged_input is sent every tick intentionally. Since the toolkit tests behaviour under simulated packet loss, resending the current input redundantly protects against individual packets being dropped, instead of relying on a single send succeeding.
        injector.apply(transport.send, tagged_input, SERVER_PORT) 

        # Predict() however, will run every tick regardless of input changes, since local simulation needs to keep advancing continuosly for insant responsiveness, seperate from whether a new input event has occurred,. 
        strategy.predict(game_state, current_input, 1 / TICK_RATE)
        # print("Client player state:", game_state.entities["player"]) # TEMP DEBUG

        # Check for authoritative update from server. Not every tick will have one so this is None most of the time.
        received_data = transport.receive()
        if received_data is not None:
            # Reconcile() trims confirmed inputs from the buffer and replays whatever is left, correcting local prediction if wrong.
            strategy.reconcile(game_state, received_data)

        time.sleep(1 / TICK_RATE)

if __name__ == "__main__":
    main()