# rev0273 route-first authority precommit refactor

rev0273 closes a last-mile execution ambiguity without pretending to have human or private authority. The active branch is route-first/no-attachment, but the standing human/sender authority precommit still bound the older full-payload email. That created a practical failure mode: a future operator could sign the wrong artifact, or think the full-payload precommit authorizes the lighter first hop.

The new receiving surface is `examples/external-contact-route-first-human-sender-authority-precommit-rev0273-aiid.json`. It binds only the route-first recipient, subject, exact body hash, mail-ready `.eml` hash, no-attachment limit, and stage-two deferral. It explicitly does not authorize contact, sender authority, private vault roots, transport proof, stage-two payload send, custody, intake, import, recognition, or live-floor effect.

This revision also refactors the operator pack and lane-integrity report so they check the new route-first-specific authority precommit. The legacy full-payload precommit remains available as context for stage-two or full-payload thinking, but it cannot substitute for route-first signature.

Remaining blockers are unchanged in substance: human signature, sender authority, send-time public locator recheck, private vault roots, final route-first hash recompute, and actual transport proof if sent. The public tree now gives the human signer a narrower target, not permission to act.

Use `python3 tools/audit_external_contact_route_first_human_sender_authority_precommit.py` before any route-first finalization attempt, then use `python3 tools/audit_external_contact_route_first_lane_integrity.py` to verify that the preflight, gate, operator pack, hold, and lane report agree.
