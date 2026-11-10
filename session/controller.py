import json
import random
import subprocess
import sys
import time
from pathlib import Path

LATENCY_TIERS_MS = [0, 50, 100, 200]
PACKET_LOSS_TIERS_PCT = [0, 3, 6]
FIXED_LATENCY_FOR_LOSS_BLOCK_MS = 100
ARCHITECTURES = ["dead_reckoning", "prediction", "rollback"]

ROUND_SECONDS = 40  # Length of each test round
PRACTICE_SECONDS = 60  # The practice round is longer, so participants can learn the controls


def ask(prompt):
    # Throw away any keys pressed during the round, so they cannot answer the prompt, bug earlier was showing key strokes from previous rounds in terminal prompts
    try:
        import msvcrt  # Windows
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        try:
            import termios  # Mac and Linux
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
        except (ImportError, OSError, termios.error):
            pass  # Not a real terminal, so there is nothing to flush
    return input(prompt)


class SessionController:
    def build_trial_matrix(self):
        trials = []
        # Block 1: Every architecture at every latency tier, with no packet loss
        for a in ARCHITECTURES:
            for latency in LATENCY_TIERS_MS:
                trials.append({"architecture": a, "latency_ms": latency, "packet_loss_pct": 0})
        # Block 2: Every architecture at each loss tier, skipping 0 because Block 1 already covers it
        for a in ARCHITECTURES:
            for loss in PACKET_LOSS_TIERS_PCT:
                if loss == 0:
                    continue
                trials.append({"architecture": a, "latency_ms": FIXED_LATENCY_FOR_LOSS_BLOCK_MS, "packet_loss_pct": loss})
        return trials

    def run_trial(self, architecture, latency_ms, packet_loss_pct, trial_id, seconds):
        # Start the server first, so it is listening before the client sends anything
        server = subprocess.Popen([
            sys.executable, "-m", "server.main", str(latency_ms), str(packet_loss_pct), trial_id
        ])
        time.sleep(0.5)
        client = subprocess.Popen([
            sys.executable, "-m", "client.main", architecture, str(latency_ms), str(packet_loss_pct), trial_id
        ])
        try:
            time.sleep(seconds)
        finally:
            client.terminate()
            server.terminate()
            client.wait()
            server.wait()
        time.sleep(1.0)  # Give the ports time to free up before the next round

    def run_session(self, participant, practice_seconds, round_seconds):
        trials = self.build_trial_matrix()
        # The order depends only on the participant ID, so it can be reproduced later
        random.Random(participant).shuffle(trials)

        # Save the key that links round numbers to conditions, and do not open it during the session
        Path("logs").mkdir(exist_ok=True)
        order = [{"round": i + 1, **t} for i, t in enumerate(trials)]
        with open(f"logs/{participant}_order.json", "w") as f:
            json.dump(order, f, indent=2)

        ask("Practice round. Press Enter to start: ")
        self.run_trial("prediction", 0, 0, f"{participant}_practice", practice_seconds)

        for i, t in enumerate(trials, start=1):
            answer = ask(f"Round {i} of {len(trials)}. Press Enter to start, or q then Enter to stop: ")
            if answer.strip().lower() == "q":
                print("Session stopped.")
                return
            # The condition is never printed, so the participant cannot read it off the screen
            self.run_trial(t["architecture"], t["latency_ms"], t["packet_loss_pct"],
                           f"{participant}_r{i:02d}", round_seconds)
        print("Session finished.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m session.controller <participant_id> [quick]")
        sys.exit(1)
    quick = len(sys.argv) > 2 and sys.argv[2] == "quick"
    # Quick mode uses 5 second rounds, FOR TESTING PURPOSES
    SessionController().run_session(
        sys.argv[1],
        practice_seconds=5 if quick else PRACTICE_SECONDS,
        round_seconds=5 if quick else ROUND_SECONDS,
    )