# Cube deep audit rev0278

Rev0278 continues the field-execution refactor. The cube is now strongest at
blocking false contact, false returned CSV, false seed, false review, false
first-packet decision, false post-decision ticket, and now false live-window
progress. The remaining risk is later evidence laundering: a completed or paused
window could still be converted into stronger claims without a bounded readout.

## Substance added

The new live-window card gate turns the prose stop/rollback card into a
scratch-local artifact with explicit window state, source-truth class, day count,
allowed/prohibited activity counts, stop triggers, rollback steps, evidence
readout count, and no-expansion/human-pause/fallback confirmations. It is
intentionally narrow. It does not store narrative findings, owner-answer text,
copied ticket prose, contact details, learner facts, protected facts, or security
payloads.

## Why this matters

A real owner packet and proceed-capable workbench review will create pressure to
start a live service change. The risky moves are expanding users, date ranges,
tools, schema fields, public language, or lifecycle status before rollback and
readout boundaries are executable. The card gate slows exactly that moment
without adding a broad doctrine family.

## Refactor note

The router path now has a cleaner post-ticket sequence:

`post-decision-change-ticket.json` → `live-window-card.json` → end-of-window readout gate.

That replaces the weaker sequence:

`post-decision-change-ticket.json` → open prose stop/rollback card → hope the window stays bounded.

The refactor also keeps all generated card artifacts under `scratch/` or external
local paths and blocks release-controlled outputs.

## Next high-risk seam

The end-of-window readout gate is now the riskiest manual surface. It should stay
aggregate, claim-family-bounded, and explicit about what does not close `FT-0181`.
A future recorder may be justified if a real terminal card would otherwise route
back into prose or claim drift.
