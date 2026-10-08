# Local decision follow-through refactor — rev0334

## Risk

The local teacher/tutor result path had a safe stop, but the stop was too blunt. Once a
`MICRO-PILOT-RESULT.json` existed, the next-action router simply stopped. That preserved the
no-evidence boundary, but it left the owner decision (`retire`, `repeat-narrower`,
`continue-bounded`, or `escalate-to-pilot-review`) without an operational next-step map. The likely
failure was not a validator crash; it was human drift after the first real cycle:

- `repeat-narrower` could become a second row appended to the same packet.
- `continue-bounded` could become an informal trend claim across cycles.
- `escalate-to-pilot-review` could be mistaken for evidence acceptance or deployment authority.
- `retire` could disappear into a completed receipt rather than stopping the local line.

## Change

rev0334 adds a bounded decision-follow-through map directly to the hot path.

- The result recorder now writes `decision_followthrough` into `MICRO-PILOT-RESULT.json`.
- The result markdown renders that map so a human sees the next step immediately.
- The next-action router reads an existing result receipt and exposes decision-specific action.
- Repeat and continue decisions require a fresh packet, fresh owner plan, fresh run-definition hashes,
  and no cumulative efficacy interpretation.
- Escalation stops the local lane and names a separate future pilot-review gate; no import command is
  emitted from the local result.

## No-new-bureaucracy rule

This is intentionally not a new schema, registry family, or release lane. It is a refactor of the
existing result recorder, router, templates, and docs so the field path can move forward without
turning one small feasibility cycle into pseudo-evidence.

## Remaining blocker

No real educator/tutor has been contacted, no local cycle has run, and no owner-reviewed result exists.
The next real-world move is still discovery with a teacher/tutor owner.
