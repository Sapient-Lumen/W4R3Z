# Cube deep audit rev0251 — workbench seed and manifest self-hash repair

## What was riskiest

After rev0250, the local owner-reply path could receipt, triage, and route a returned CSV into one scratch bundle. The next risk was the handoff from that bundle to the owner packet workbench: a maintainer could either treat a local bundle as accepted evidence or copy too much content into a workbench before custody and field-survival review.

## What had gone wrong

The audit found a concrete integrity bug in the rev0250 intake bundle: `bundle-manifest.json` wrote a `bundle_manifest` artifact hash and then rewrote itself to include that hash. The stored hash therefore described a prior byte sequence rather than the final manifest. The bug was local and did not create evidence, but it weakened the exact source-trace path that rev0249/rev0250 were meant to protect.

## Correction

Rev0251 changes the intake manifest rule: `bundle-manifest.json` no longer embeds its own hash. Instead, `tools/intake_owner_reply_csv.py` returns the manifest hash out-of-band in the CLI response and records a `self_hash_policy` in the manifest.

Rev0251 also adds `tools/seed_owner_packet_workbench.py`, `tools/check_owner_reply_workbench_seed.py`, and `docs/30-operations/ft0181-owner-reply-workbench-seed.md`. The seed tool consumes only verified local bundle metadata, refuses non-`PROCEED-STAGED` or stale-manifest bundles, writes only to scratch or an external local path, and produces `workbench-seed.json` with `acceptance_state: NOT_ACCEPTED`.

## Waste avoided

This avoids creating another registry while still preventing a real failure mode: local intake artifacts becoming de facto evidence. The seed is a narrow bridge, not a new control family.

## Remaining blocker

No real owner has been contacted, no real CSV has been returned, no `SRC2+` packet has been accepted, and `FT-0181` remains live.
