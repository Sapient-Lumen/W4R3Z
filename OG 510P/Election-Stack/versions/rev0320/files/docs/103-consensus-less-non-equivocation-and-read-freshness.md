# Consensus-less non-equivocation and read freshness

**Track:** A (Deployable core)


## Motivation
Full BFT consensus is expensive. A simpler pattern is:
- a single sequencer (log operator)
- **witness quorum** countersigning checkpoints

If the operator equivocates, witnesses/monitors can produce evidence.

## Read freshness problem
Even with non-equivocation, an attacker can **delay** a user’s view.

Solution approach:
- define a Maximum Merge/Publication Delay (MMD/MPD)
- require monitors to watch for violations

## Normative requirements
- **MUST** define quorum thresholds (e.g., 5-of-9 witnesses).
- **MUST** publish witness membership and rotation policy.
- **MUST** define a read-freshness SLA (“latest checkpoint not older than X”).
- **MUST** treat freshness violations as publishable outage evidence (ATL).

## Notes
If you need stronger non-equivocation guarantees, cross-anchor checkpoints to independent logs or time-stamping services.