# This probe server will take place of the client. It holds the right key for 3 seconds and measures how long the server takes to take each input.
import time

from engine.rules import NO_INPUT, TICK_DT
from network.transport import UDPTransport

CLIENT_PORT = 9998
SERVER_PORT = 9999


def main():
    transport = UDPTransport(local_port=CLIENT_PORT)
    inputs = dict(NO_INPUT)
    inputs["right"] = True  # Hold the right key for the whole test

    sent_at = {}  # Input number -> time it was sent
    round_trips = []
    states = 0
    last = None
    seq = 0

    start = time.monotonic()
    next_time = start
    while time.monotonic() - start < 3.0:
        sent_at[seq] = time.monotonic()
        transport.send({"seq": seq, "inputs": inputs}, SERVER_PORT)
        seq += 1

        while True:
            state = transport.receive()
            if state is None:
                break
            states += 1
            ack = state["seq"]  # The newest input the server had applied for this state
            if ack in sent_at:
                round_trips.append(time.monotonic() - sent_at.pop(ack))  # Only the first sighting counts
            last = state

        next_time += TICK_DT
        delay = next_time - time.monotonic()
        if delay > 0:
            time.sleep(delay)

    round_trips.sort()
    print("Inputs sent:", seq)
    print("States received:", states)
    if round_trips:
        print("Median round trip (ms):", round(round_trips[len(round_trips) // 2] * 1000, 1))
    if last:
        world = last["world"]
        print("Last server tick:", last["tick"])
        print("Player x:", round(world["player"]["x"], 1), "health:", world["player"]["health"])
        print("Npc x:", round(world["npc"]["x"], 1), "health:", world["npc"]["health"])


if __name__ == "__main__":
    main()