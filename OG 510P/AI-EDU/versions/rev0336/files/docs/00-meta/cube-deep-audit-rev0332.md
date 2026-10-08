# Cube deep audit — rev0332

## Finding

The cube had just made result receipts safer, but the intervention identity itself was still
underprotected. `OWNER-REVIEW-STOP.json` hash-locked the owner plan, session log, final readout,
measure card, decision memo, and readiness scorecard, but it did not hash-lock the generated coach
prompt, run checklist, discovery card, or cycle run sheet. A result could therefore be recorded after
a post-review edit to the actual run instructions without the recorder detecting the drift.

That is a substance failure, not a registry failure. The educational question is whether a teacher can
use a specific move-coach design under a specific local plan. If the prompt or run sheet can drift, the
archive may summarize a different intervention from the one the owner reviewed.

## Refactor

- Added `run-definition-hash-stable` to the existing readiness scorer.
- Compared immutable generated surfaces against `PACK-MANIFEST.json` hashes.
- Compared `COACH-PROMPT.md` against the prompt-card SHA-256 recorded in `OWNER-PLAN.md`.
- Required the owner plan to confirm the prompt stayed unchanged; changed prompt instructions require
  packet regeneration.
- Expanded owner-review packet hashes to include the discovery card, coach prompt, run checklist,
  measure card, and cycle run sheet, so the result recorder detects post-review drift.

## Waste avoided

No new schema, branch family, custody lane, public-claim policy, or validator family was added. The
fix is intentionally in the hot path: readiness, owner review, result recording, startup guidance, and
release audit surfaces.

## Remaining risk

The archive still has no real teacher/tutor partner, no observed local instructional problem, no real
cycle, no owner-reviewed legitimate result, and no accepted `SRC2+` packet. The next meaningful work is
human field execution, not more doctrine.
