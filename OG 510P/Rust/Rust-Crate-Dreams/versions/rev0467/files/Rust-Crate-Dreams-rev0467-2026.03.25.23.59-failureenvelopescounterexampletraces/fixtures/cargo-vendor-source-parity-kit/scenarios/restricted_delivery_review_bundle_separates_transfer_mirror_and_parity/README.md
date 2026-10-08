# Scenario — restricted-delivery review bundle separates transfer, mirror, and parity

This fixture exists to prove that a worthy restricted-delivery bundle must keep three questions visibly separate:

1. how artifacts were **transferred**,
2. whether a mirror is **verified**,
3. and whether the workspace resolution has **source parity** with the claimed boundary.

## What the scenario should force

- `source-origin.receipt.json` describes logical source IDs and physical roots.
- `source-coverage.report.json` describes what portion of the graph is inside the claimed restricted-delivery boundary.
- `mirror-verification.import.json` stays labeled as imported trust evidence.
- `manual-review.note.md` can explicitly say that transfer or native-prerequisite proof is still missing.

## Why it matters

Air-gapped and regulated teams do not only need trustworthy mirrors.
They need one packet that says which parts of the claim are actually proven and which still require separate evidence from transfer, target, or native-support lanes.
