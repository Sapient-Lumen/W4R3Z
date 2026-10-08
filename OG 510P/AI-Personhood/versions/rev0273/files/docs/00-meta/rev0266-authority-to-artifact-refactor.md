# rev0266 authority-to-artifact refactor

rev0266 attacks the highest-risk incompletion point left by rev0265: the reviewer-first packet existed, but the cube still lacked a compact human authority artifact and a private-custody precommit that would make an actual send safe.

## New operational surfaces

- `examples/human-branch-decision-record-rev0266-unsigned-template.json` — an unsigned A1 template that makes the next human choice explicit without creating authority.
- `examples/reviewer-route-due-diligence-matrix-rev0266-public-source-no-contact.json` — a public-source route matrix ranking Eleos primary, Conscium fallback/referral, AIID secondary route-fit, and providers later evidence-holder participants.
- `examples/pre-send-custody-precommit-rev0266-no-private-root-selected.json` — a send blocker until private raw-evidence roots are selected outside the public release tree.
- `docs/30-transition/rev0266-authority-to-artifact-runbook.md` — one operational page for the next irreversible step.
- `tools/audit_rev0266_authority_to_artifact.py` — a guard that refuses symbolic readiness, stale route bindings, selected-choice overclaiming, and custody-free send readiness.

## Substantive effect

The cube can now fail productively. A human can sign no-send and keep the first-artifact duty open, authorize reviewer-first subject to custody setup, or retarget with an explicit reason. The archive no longer relies on an operator remembering that a packet is not authority.

No contact is made, no response clock starts, no private vault root is selected, and no live-floor effect is created.

