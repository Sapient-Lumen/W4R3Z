# 927 — Mission-kernel closeout gaps and Example County refactor

**Track:** A / deployable core

## What changed

v889 adds an executable mission-kernel closeout surface for the synthetic Example County path:

- `tools/mission_kernel_closeout.py`
- `scripts/check_mission_kernel_closeout_pack.py`
- `schemas/MissionKernelCloseoutIndex.json`
- `artifacts/examples/example_county_2026_municipal_pilot/mission-kernel-closeout-index.json`
- `artifacts/examples/example_county_2026_municipal_pilot/public-mission-kernel-closeout.md`
- `artifacts/reports/mission-kernel-closeout-gaps-rev0889.json`

The closeout index maps the seven mission-kernel elements to actual packet evidence, owner roles, closure tests, and live blockers. It deliberately keeps the verdict at `SYNTHETIC_REPLAY_PASS_LIVE_NO_GO`.

## Why this matters

The riskiest incomplete work is not another doctrine family. It is closing the gap between a self-consistent synthetic cube and a jurisdictional evidence packet that external reviewers can replay. The new closeout pack makes that gap concrete: local authority, ballot accounting/custody, real export replay, audit/adjudication, independent review, public-release approval, and incident/remedy closeout are named as evidence blockers.

## Refactor performed

The Example County smoke path and output-pack builder previously each carried their own packet iteration and packet verification helper. v889 moves that shared behavior into `tools/example_county_common.py`, then has the smoke, output-pack, and mission-kernel closeout tools consume the same helper. The closeout gate asserts that duplicate `verify_packet` functions are gone from the two consumer tools.

## Boundary

This revision does not add live election evidence, does not prove any outcome, does not certify a system, does not authorize public voter-facing release, and does not replace canvass, audit, certification, recount, statutory retention, public-records, or court process.
