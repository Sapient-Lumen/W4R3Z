#!/usr/bin/env python3
"""Detection probability simulator (minimal Monte Carlo).

This is a conservative skeleton. It models:
- selective failures affecting a fraction of probes
- gossip rounds at fixed intervals
- detection occurs if any monitor sees an inconsistency

It does NOT attempt to model all real-world dynamics.

Usage:
  python detection_simulator.py --config sim.json --out report.json
"""

import argparse
import json
import random
from datetime import datetime, timezone


def run_once(cfg):
    horizon = cfg.get("time_horizon_s", 3600)
    interval = cfg["gossip_interval_s"]
    base = cfg["probe_model"]["success_base_rate"]
    selective = cfg["probe_model"].get("selective_failure_rate", 0.0)
    severity = cfg["partition_model"].get("severity", 0.0)

    # Simplified: in each interval, some probes are impacted by partition with prob severity.
    t = 0
    while t <= horizon:
        impacted = random.random() < severity
        # Inconsistency if impacted causes success probability to differ.
        p_success = base * (1.0 - (selective if impacted else 0.0))
        # Two audiences: A (impacted?) and B (not)
        a = random.random() < p_success
        b = random.random() < base
        if a != b:
            # Assume gossip spreads inconsistency within one round for this skeleton.
            return t
        t += interval
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cfg = json.load(open(args.config, "r", encoding="utf-8"))
    runs = cfg["runs"]

    detections = []
    for _ in range(runs):
        dt = run_once(cfg)
        if dt is not None:
            detections.append(dt)

    horizon = cfg.get("time_horizon_s", 3600)
    # compute P(detect <= t) curve for a few points
    points = [60, 300, 600, 1800, horizon]
    curve = []
    for t in points:
        p = sum(1 for d in detections if d <= t) / runs
        curve.append({"t_s": t, "p": p})

    mttd = (sum(detections) / len(detections)) if detections else float("inf")

    report = {
        "sim_id": cfg.get("sim_id", "sim"),
        "election_id": cfg.get("election_id", "ELECTION"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runs": runs,
        "metrics": {
            "p_detect_by_t": curve,
            "mttd_s": mttd,
            "detected_fraction": len(detections) / runs
        },
        "assumptions": [
            "Two-audience split model (toy)",
            "Detection within one gossip interval (toy)",
            "Independent Bernoulli outcomes"
        ]
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
