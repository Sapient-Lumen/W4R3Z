# Scenario — explore packet graduates to enterprise-offline without rewriting basis

## What this scenario proves

A worthy Pathfinder-style crate should be able to:
- start with an exploratory packet and basis lock,
- reuse that earlier basis during a later enterprise-offline gate,
- add new source-parity/materialization evidence without pretending the original packet always had it,
- keep bounded exceptions visible,
- and end in `conditional_keep` if mirror or parity gaps remain.

## Why this matters

The current Rust substrate increasingly supports staged review:
- Cargo plumbing decomposes operations into explicit phases.
- Cargo build-analysis aims to persist machine-readable records across invocations.
- docs.rs exposes hosted-build posture and download caveats that can be imported later rather than retroactively assumed.
- crates.io exposes trust/timing posture like Security tab, Trusted Publishing, and `pubtime`.
- Cargo Vet and cargo-deny already model policy state that can change over time without implying the underlying decision was always complete.

## Required artifacts

- `decision-program.runbook.example.json`
- `profile-progression.report.example.json`

## Interpretation

This scenario should end in `conditional_keep`, not `keep`, because the new stage can progress while still carrying open parity/offline gaps.
