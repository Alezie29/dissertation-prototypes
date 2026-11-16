import subprocess
import sys
import time

from engine.rules import NO_INPUT, TICK_DT
from network.impairment import ImpairmentInjector
from network.transport import UDPTransport
from strategies.prediction import differs, summary
from strategies.rollback import RollbackNetcode

CLIENT_PORT = 9998
SERVER_PORT = 9999
SECONDS = 8


def scripted_input(t):
    # Fixed taps, the same every run: right for 1 s, pause, left for 1 s, pause, repeating
    phase = t % 4.0
    if phase < 1.0:
        return {**NO_INPUT, "right": True}
    if 2.0 <= phase < 3.0:
        return {**NO_INPUT, "left": True}
    return dict(NO_INPUT)


def main():
    latency = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    loss = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0

    server = subprocess.Popen([sys.executable, "-m", "server.main", str(latency), str(loss), "gap"])
    rows = []  # (seq, server tick, gap, mismatch)
    try:
        time.sleep(0.5)

        strategy = RollbackNetcode()
        transport = UDPTransport(local_port=CLIENT_PORT)
        injector = ImpairmentInjector(latency_ms=latency, packet_loss_pct=loss)

        seq = 0
        start = time.monotonic()
        next_time = start
        while time.monotonic() - start < SECONDS:
            inputs = scripted_input(time.monotonic() - start)
            strategy.process_input(seq, inputs)
            injector.apply(transport.send, {"seq": seq, "inputs": inputs}, SERVER_PORT)
            seq += 1

            while True:
                state = transport.receive()
                if state is None:
                    break
                # Compare before reconcile changes anything, using the same test rollback uses
                predicted = strategy.history.get(state["seq"])
                mismatch = predicted is not None and differs(summary(predicted), summary(state["world"]))
                rows.append((state["seq"], state["tick"], state["tick"] - (state["seq"] + 1), mismatch))
                strategy.reconcile(state)

            strategy.predict(TICK_DT)

            next_time += TICK_DT
            while time.monotonic() < next_time:
                injector.release()
                time.sleep(0.001)
            injector.release()
    finally:
        # Always stop the server, even if something above crashed, so it cannot hold the port
        server.terminate()
        server.wait()

    total = len(rows)
    bad = [r for r in rows if r[3]]
    print(f"Latency {latency} ms, loss {loss}%: {total} states, {len(bad)} mismatches")
    print("Gap (server tick minus seq+1) for all states:", sorted(set(r[2] for r in rows)))
    print("Gap on mismatched states:", sorted(set(r[2] for r in bad)))
    print("First 8 mismatches (seq, tick, gap):", [r[:3] for r in bad[:8]])


if __name__ == "__main__":
    main()