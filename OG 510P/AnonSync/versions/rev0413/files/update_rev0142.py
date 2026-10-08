from pathlib import Path

print("rev0142 adds docs 229-232 and refreshes README, status, evaluation, product direction, roadmap, and sources.")
for name in [
    "229-attention-lane-delivery-grade-and-missed-event-recovery-interface-spec.md",
    "230-entitlement-expiry-capability-floor-and-subject-continuity-interface-spec.md",
    "231-upgrade-availability-rollout-channel-and-restart-review-interface-spec.md",
    "232-diagnostic-export-log-redaction-and-self-serve-support-boundary-interface-spec.md",
]:
    p = Path("docs") / name
    print(name, "exists=", p.exists())
