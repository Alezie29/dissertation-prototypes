import copy
import sys
import time

from engine.rules import NO_INPUT, TICK_DT, new_world, step_world
from metrics.logger import MetricsLogger
from network.impairment import ImpairmentInjector
from network.transport import UDPTransport

SERVER_PORT = 9999
CLIENT_PORT = 9998
JITTER_BUFFER_TICKS = 2  # Ticks to wait after the first packet, so normal timing wobble does not make inputs miss


def main():
    if len(sys.argv) < 4:
        print("Please use a valid format: python3 -m server.main <latency_ms> <packet_loss_pct> <trial_id>")
        sys.exit(1)

    latency_ms = int(sys.argv[1])
    packet_loss_pct = float(sys.argv[2])
    trial_id = sys.argv[3]

    world = new_world()
    transport = UDPTransport(local_port=SERVER_PORT)
    injector = ImpairmentInjector(latency_ms=latency_ms, packet_loss_pct=packet_loss_pct)
    logger = MetricsLogger(role="server")

    inputs_by_seq = {}  # Inputs that have arrived but not been applied yet
    last_input = dict(NO_INPUT)  # Held when the input for a tick is missing
    applied = -1  # Number of the newest input the world has been stepped with
    tick = 0  # Always equal to applied + 1 once the world is running
    held_ticks = 0  # Ticks that had to reuse the last input because the real one had not arrived
    late_inputs = 0  # Inputs that arrived after their tick had already been simulated
    client_seen = False
    next_tick_time = 0.0

    print("Server running, waiting for a client")

    while True:
        # Collect everything that has arrived
        while True:
            packet = transport.receive()
            if packet is None:
                break
            seq = packet["seq"]
            if not client_seen:
                client_seen = True
                # Any inputs lost before the first one that arrived are treated as no input, so the numbering lines up
                for _ in range(seq):
                    step_world(world, NO_INPUT, TICK_DT)
                    tick += 1
                applied = seq - 1
                next_tick_time = time.monotonic() + JITTER_BUFFER_TICKS * TICK_DT
            if seq > applied:
                inputs_by_seq[seq] = {**NO_INPUT, **packet.get("inputs", {})}
            else:
                late_inputs += 1

        if client_seen and time.monotonic() >= next_tick_time:
            # Tick k applies input k-1 in order, or holds the last input if it is missing
            applied += 1
            used = inputs_by_seq.pop(applied, None)
            if used is not None:
                last_input = used
            else:
                held_ticks += 1
            step_world(world, last_input, TICK_DT)
            tick += 1

            # Send a copy, because the packet waits in the delay queue while the world keeps changing
            state = {"seq": applied, "tick": tick, "world": copy.deepcopy(world)}
            injector.apply(transport.send, state, CLIENT_PORT)

            if tick % 5 == 0:
                logger.log_state(tick, (world["player"]["x"], world["player"]["y"]))
            if tick % 60 == 0:
                logger.log_counters(tick, {"held_ticks": held_ticks, "late_inputs": late_inputs})
                logger.flush(trial_id)

            next_tick_time += TICK_DT
            if next_tick_time < time.monotonic() - TICK_DT:
                next_tick_time = time.monotonic()  # Fell behind by more than a tick, so do not try to catch up

        # Send delayed packets the moment they are due
        injector.release()
        time.sleep(0.001)


if __name__ == "__main__":
    main()