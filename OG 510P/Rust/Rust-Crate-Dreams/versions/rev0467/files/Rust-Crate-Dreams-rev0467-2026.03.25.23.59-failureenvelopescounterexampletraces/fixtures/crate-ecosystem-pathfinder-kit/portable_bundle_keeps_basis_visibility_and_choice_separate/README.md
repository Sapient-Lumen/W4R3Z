# Scenario — `portable_bundle_keeps_basis_visibility_and_choice_separate`

This fixture exists to prove that **P-0509** should emit one compact portable packet without flattening all evidence into the same thing.

## What the scenario should force

- `pathfinder-bundle.manifest.json` should inventory the task profile, decision pack, starter-set lock, basis receipts, visibility reports, and watch policies.
- Another reviewer should be able to inspect the packet later without re-scraping crates.io, docs.rs, and Cargo output from memory.
- The bundle should keep “what we observed”, “what was visible publicly”, and “what we chose” separate.

## Why it matters

Pathfinder decisions are only useful if a second team can review them later.
A portable bundle is the difference between a real ecosystem contribution and a one-off ranking session.
