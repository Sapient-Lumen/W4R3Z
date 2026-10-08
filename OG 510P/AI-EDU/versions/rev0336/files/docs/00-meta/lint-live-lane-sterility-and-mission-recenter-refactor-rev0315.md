# rev0315 lint live-lane sterility and mission recenter refactor

## Failure found

A clean `make lint-fast` could report success while leaving synthetic artifacts in
`scratch/field/ft0181/` outside ignored validation lanes. The escaped artifacts included generated
`real-owner-packet.csv` files and `owner-workbench-review-briefs/.../review-brief.json`. A subsequent
`make owner-field-report` counted the review briefs as live field state.

This was a severe integrity defect. The archive's release narrative said validation fixtures were
firewalled from the live lane, but the executable check suite contradicted that claim. Passing lint
therefore produced a dirtier and more misleading operational state than the state it inspected.

## Repair

The repair changes existing controls rather than adding another validator:

1. `tools/run_lint_suite.py` snapshots non-fixture `FT-0181` field state, cleans validator-only lanes
   before and after a run, and fails if the selected lint lane adds, removes, or changes live files.
2. `tools/check_ft0181_returned_reply_work.py` and
   `tools/check_ft0181_live_window_terminal_brief.py` now pass explicit validation-local review-brief
   directories instead of accepting a default live output path.
3. Activation, live-window, readout, post-decision, and post-readout checks now keep synthetic source
   packets inside their own validation trees instead of creating top-level field directories.
4. The runner installs exit and signal cleanup for validator-only lanes, so an interrupted suite does
   not strand fixtures in the field tree; a forced `SIGTERM` test preserved an operator-owned sentinel
   byte-for-byte while removing validator residue.
5. The returned-reply and readout-brief checks remove their validation trees when complete.

The invariant is behavioral: **validation may inspect the live-lane rules, but it may not create live
field state**.

## Mission recenter

The archive entered rev0314 with 720 tracked files and about 932,000 whitespace-delimited words.
Only about 1.2% of those words were in `docs/10-core` and `docs/40-assessment`; governance alone held
about 38%. Since earlier audits declared control saturation and asked for no new pre-import controls,
the archive nevertheless continued growing while the external owner-contact blocker did not move.

Rev0315 therefore makes the boundary explicit in the charter and startup surfaces: FT-0181 is one
evidence rail serving the education mission. A revision should advance field evidence, pedagogical
knowledge, or reduce burden. Under `SAT4`, merge/delete first and require a demonstrated uncovered
risk before control growth.

## Navigation, history, and source integrity

- Re-entry is reduced from a long historical tool chain to ten current surfaces.
- `context-pack.json` startup generation is reduced to the same compact operating path.
- `CHANGELOG.md` now has one title, current/previous revision continuity, and unique revision
  headings; unsupported historical gaps are acknowledged rather than fabricated.
- EU AI Act entries B108 and B122 now point to official EU sources instead of labeling a secondary
  site as official.

## Non-effect

These repairs do not contact an owner, create real evidence, accept `SRC2+`, authorize a service or
active window, upgrade a public claim, or close `FT-0181`.
