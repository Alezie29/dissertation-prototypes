LATENCY_TIERS_MS = [0, 50, 100, 200]
PACKET_LOSS_TIERS_PCT = [0, 3, 6]
FIXED_LATENCY_FOR_LOSS_BLOCK_MS = 100

ARCHITECTURES = [
    "prediction",
    "dead_reckoning",
    "rollback",
]

class SessionController:
    def build_trial_matrix(self):
        trials = []
        # TODO: Block 1 — loop over ARCHITECTURES, loop over LATENCY_TIERS_MS
        for a in ARCHITECTURES:
            for l in LATENCY_TIERS_MS:
                trial = {"architecture": a, "latency_ms": l, "packet_loss_pct": 0}
                trials.append(trial) # Go through each architecture then each latency tier, creating a new matrix for each one
        # TODO: Block 2 — loop over ARCHITECTURES, loop over PACKET_LOSS_TIERS_PCT (skip 0)
        for a in ARCHITECTURES:
            for l in PACKET_LOSS_TIERS_PCT:
                if l == 0:
                    continue
                trial = {"architecture": a, "latency_ms": FIXED_LATENCY_FOR_LOSS_BLOCK_MS, "packet_loss_pct": l} # Skipping 0 as it is already covered by Block 1's latency = 100, loss = 0
                trials.append(trial)
        return trials

""" if __name__ == "__main__":
    sc = SessionController()
    trials = sc.build_trial_matrix()
    print("Total trials:", len(trials))
    for t in trials:
        print(t) """ # Testing the matrix, VERIFIED ! 