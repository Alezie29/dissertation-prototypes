import bisect
import csv
import json
import statistics
import sys
from math import hypot
from pathlib import Path

LOGS = Path("logs")
RESULTS = Path("results")
MAX_TIME_DIFF = 0.1  # Seconds allowed between a client entry and the server entry it is compared with

FIELDS = [
    "participant", "round", "architecture", "latency_ms", "loss_pct", "duration_s",
    "corrections", "corrections_per_min", "mean_shift_px", "max_shift_px",
    "responses", "response_median_ms", "response_p90_ms", "gap_to_server_px",
    "replays", "replayed_ticks", "rating",
]


def load(path):
    # Returns the contents of a JSON file, or None if it is missing or cut off
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def load_ratings():
    # Optional file with the columns participant, round, rating, typed in from the rating sheets
    path = RESULTS / "ratings.csv"
    if not path.exists():
        return {}
    with open(path, newline="") as f:
        return {(r["participant"], int(r["round"])): r["rating"] for r in csv.DictReader(f)}


def percentile(values, p):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * p))]


def gap_to_server(client_positions, server_positions):
    # Distance between where the client drew the player and where the server had the player at the same moment
    if not server_positions:
        return None
    times = [e["timestamp"] for e in server_positions]
    gaps = []
    for e in client_positions:
        i = bisect.bisect_left(times, e["timestamp"])
        nearby = [j for j in (i - 1, i) if 0 <= j < len(times)]
        j = min(nearby, key=lambda k: abs(times[k] - e["timestamp"]))
        if abs(times[j] - e["timestamp"]) > MAX_TIME_DIFF:
            continue  # No server entry close enough in time
        sx, sy = server_positions[j]["position"]
        cx, cy = e["position"]
        gaps.append(hypot(cx - sx, cy - sy))
    return statistics.mean(gaps) if gaps else None


def summarise(participant, trial):
    base = f"{participant}_r{trial['round']:02d}"
    client = load(LOGS / f"{base}_client.json")
    server = load(LOGS / f"{base}_server.json") or []
    if not client:
        return None

    positions = [e for e in client if "position" in e]
    corrections = [e for e in client if e.get("correction")]
    responses = [e["response_s"] * 1000 for e in client if "response_s" in e]
    counters = [e["counters"] for e in client if "counters" in e]
    shifts = [e["shift"] for e in corrections]
    duration = client[-1]["timestamp"] - client[0]["timestamp"]
    gap = gap_to_server(positions, [e for e in server if "position" in e])
    last = counters[-1] if counters else {}

    return {
        "participant": participant,
        "round": trial["round"],
        "architecture": trial["architecture"],
        "latency_ms": trial["latency_ms"],
        "loss_pct": trial["packet_loss_pct"],
        "duration_s": round(duration, 1),
        "corrections": len(corrections),
        "corrections_per_min": round(len(corrections) / duration * 60, 1) if duration > 0 else "",
        "mean_shift_px": round(statistics.mean(shifts), 2) if shifts else 0,
        "max_shift_px": round(max(shifts), 2) if shifts else 0,
        "responses": len(responses),
        "response_median_ms": round(statistics.median(responses), 1) if responses else "",
        "response_p90_ms": round(percentile(responses, 0.9), 1) if responses else "",
        "gap_to_server_px": round(gap, 1) if gap is not None else "",
        "replays": last.get("replays", ""),
        "replayed_ticks": last.get("replayed_ticks", ""),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m analysis.summarise <participant_id> [more ids]")
        sys.exit(1)

    ratings = load_ratings()
    rows = []
    for participant in sys.argv[1:]:
        order = load(LOGS / f"{participant}_order.json")
        if order is None:
            print(f"No order key for {participant}, skipping")
            continue
        for trial in order:
            row = summarise(participant, trial)
            if row is None:
                print(f"{participant} round {trial['round']}: no log, the round was skipped or failed")
                continue
            row["rating"] = ratings.get((participant, trial["round"]), "")
            rows.append(row)

    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} rounds written to results/summary.csv")
    for r in rows:
        print(f"{r['participant']} r{r['round']:02d} {r['architecture']:<15} {r['latency_ms']:>3}ms {r['loss_pct']:>2}%"
              f"  corrections {r['corrections']:>3}  response {str(r['response_median_ms']):>6} ms"
              f"  replayed {str(r['replayed_ticks']):>6}")


if __name__ == "__main__":
    main()