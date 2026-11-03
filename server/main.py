import sys
import copy
import time

from engine.rules import NO_INPUT, TICK_DT, new_world, step_world
from metrics.logger import MetricsLogger
from network.impairment import ImpairmentInjector
from network.transport import UDPTransport

SERVER_PORT = 9999 # Hardcoded as examples, this will be updated later
CLIENT_PORT = 9998

def main():
    if len(sys.argv) < 4:
        print("Please use a valid format: python3 -m server.main <latency_ms> <packet_loss_pct>")
        sys.exit(1)

    latency_ms = int(sys.argv[1])
    packet_loss_pct = float(sys.argv[2])
    trial_id = sys.argv[3] # Adding trial id as an argument, done in client main() too

    world = new_world()
    transport = UDPTransport(local_port=SERVER_PORT)
    injector = ImpairmentInjector(latency_ms=latency_ms, packet_loss_pct=packet_loss_pct)
    logger = MetricsLogger(role="server")

    latest_input = dict(NO_INPUT)  # The last input heard is reused until a newer one arrives
    latest_seq = -1  # Highest input number received so far
    client_seen = False  # Nothing is sent until the first packet arrives
    tick = 0
    next_tick_time = time.monotonic()

    print("Server running, waiting for a client")

    while True:
        # Read everything that arrived since the last tick, keeping only the newest input
        while True:
            packet = transport.receive()
            if packet is None:
                break
            if not client_seen:
                client_seen = True
                next_tick_time = time.monotonic()  # The world starts when the client first appears
            if packet["seq"] > latest_seq:
                latest_seq = packet["seq"]
                latest_input = {**NO_INPUT, **packet.get("inputs", {})}

        if client_seen:
            # The world only advances once a client is connected, so every trial starts from the same moment
            step_world(world, latest_input, TICK_DT)
            tick += 1

            # Send a copy, because the packet waits in the delay queue while the world keeps changing
            state = {"seq": latest_seq, "tick": tick, "world": copy.deepcopy(world)}
            injector.apply(transport.send, state, CLIENT_PORT)

            if tick % 5 == 0:
                logger.log_state(tick, (world["player"]["x"], world["player"]["y"]))
            if tick % 60 == 0:
                logger.flush(trial_id)

            next_tick_time += TICK_DT
            if next_tick_time < time.monotonic() - TICK_DT:
                next_tick_time = time.monotonic()  # Fell behind by more than a tick, so do not try to catch up
        else:
            next_tick_time = time.monotonic() + 0.001  # No client yet, so just keep listening

        # Wait for the next tick, sending any delayed packets the moment they are due
        while time.monotonic() < next_tick_time:
            injector.release()
            time.sleep(0.001)
        injector.release()

if __name__ == "__main__":
    main()