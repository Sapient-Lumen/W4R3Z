# Audit — rev0101 replay transparency temporal refactor

## Focus

rev0101 continues FT-0090 with a narrow executable objective: replay transparency evidence used for current visibility must exist no later than the evaluation that consumes it, and freshness metadata must bind to the evidence field it names.

## Finding closed

rev0100 still left part of replay transparency temporal handling split across the monolithic validator. `check_anchor_evaluation` owned anchor freshness arithmetic and checkpoint ordering, while `check_witness_cohort_evaluation` owned witness observation ordering. More importantly, a current replay-visibility evaluation could declare freshness `basis: logged_at` without proving that `basis_time` actually matched `transparency_anchor.logged_at`.

That was a stale/future-evidence risk rather than a documentation problem. A replay receipt could otherwise carry a fresh-looking `basis_time` while the actual anchor `logged_at` was later, missing, or unrelated.

## Changes made

- Added `tools/replay_transparency_temporal.py`.
- Moved anchor freshness arithmetic, checkpoint consistency `checked_at`, and witness/monitor `observed_at` timing into that helper.
- Added checks for:
  - `replay_event.replayed_at <= anchor_evaluation.evaluated_at`
  - `transparency_anchor.logged_at <= anchor_evaluation.evaluated_at`
  - `anchor_freshness.basis_time == transparency_anchor.logged_at` when `basis: logged_at`
  - split-view and witness split-signal observation times no later than anchor evaluation.
- Added three derivation-checked negative fixtures and semantic vectors `TV-N270` through `TV-N272`.

## What did not change

rev0101 does not make replay transparency evidence into TimeState freshness, profile evidence, profile reassessment input, current actionability evidence, transport authentication, or a profile-binding substitute. The helper is purely an artifact/evidence ordering check.

## Risk still open

FT-0090 remains open. The most useful next work is not a new registry; it is further decomposition of executable concern families where the validator still carries domain logic inline, and selective derivation of bulky negative fixture families that are likely to drift.
