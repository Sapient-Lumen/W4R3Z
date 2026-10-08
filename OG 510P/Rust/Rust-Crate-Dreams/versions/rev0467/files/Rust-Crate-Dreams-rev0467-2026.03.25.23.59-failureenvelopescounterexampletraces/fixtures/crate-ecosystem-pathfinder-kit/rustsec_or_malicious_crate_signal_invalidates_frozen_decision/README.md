# Scenario — `rustsec_or_malicious_crate_signal_invalidates_frozen_decision`

A team froze a starter set for a production service.
Later, a RustSec advisory or malicious-crate notice lands for one chosen dependency.

## What this scenario is for

- `decision-watch.report.json` should move to `invalidated` rather than quietly staying `steady`.
- The watch report should name the trigger class and evidence ref.
- The watch layer should **not** claim that the next-ranked alternative is automatically chosen.

## Why this matters

This is the ordinary stale-decision failure mode for crate choice:
security or malware signals move, but a frozen internal recommendation still looks clean because nobody reopened the decision pack.
