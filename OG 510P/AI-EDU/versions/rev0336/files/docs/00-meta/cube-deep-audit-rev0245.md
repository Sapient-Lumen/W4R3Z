# Cube deep audit rev0245 — triage outcome router

## Finding

Rev0244 made returned owner CSVs executable to classify, but the classification still left a small
handoff gap. `PROCEED-STAGED` had an obvious next surface, while `RE-ASK-ONCE`, block outcomes, and
`NO-OWNER-PACKET` still depended on maintainer judgment or generic prose.

That is a real forward-motion risk. A useful but incomplete first reply could become a broader
second request; a block could turn into another registry; or a maintainer could open the workbench
for a packet that should have been recorded as absent, protected, overbroad, security-sensitive,
authority-failing, or unsupported.

## Change made

Rev0245 turns each triage result into one explicit next action:

- `PROCEED-STAGED` routes to `docs/30-operations/ft0181-owner-packet-workbench.md`.
- `RE-ASK-ONCE` routes to `templates/ft0181-owner-reask-once-message.md`.
- `NO-OWNER-PACKET` and block outcomes route to
  `templates/ft0181-triage-outcome-note-template.md`.

`tools/triage_owner_reply_csv.py` now emits a `next_action` object with the outcome, summary,
next artifact, and ceiling. `tools/check_owner_reply_triage.py` validates those routes and adds two
substantive receipt-safety cases: small-cell/protected subgroup leakage and vendor-only rollback.
`owner_reply_intake.outcome_routes` in the real-data request records the same route map, and
`tools/check_real_data_requests.py` enforces it.

## Refactor principle

The first reply must land in exactly one of three places:

1. **workbench** when the packet is minimized and stageable;
2. **one re-ask** when a row is missing or ambiguous but still safe;
3. **outcome note** when the packet is absent or blocked.

No triage result may create a new registry, request a full export, add a technical detour, or imply
`FT-0181` closure.

## Waste removed

Before rev0245, an incomplete or blocked reply could still cause process bloom after the classifier
ran. Rev0245 removes that ambiguity by giving every classifier outcome an artifact-level next step
and by making the re-ask copy/pasteable.

The audit also found two receipt-side blind spots: small cells could appear as numeric subgroup
fragments, and rollback could be vendor-only despite a superficially answered row. Both are now lint
fixtures.

## Still missing

No owner has been contacted. No filled owner CSV has returned. No `SRC2+` evidence has been imported.
The router only prevents the first real reply from being mishandled once it arrives.
