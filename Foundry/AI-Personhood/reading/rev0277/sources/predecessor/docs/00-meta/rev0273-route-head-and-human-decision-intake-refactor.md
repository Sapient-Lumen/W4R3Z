# rev0273 — route-head normalization and human-decision intake

This revision addresses a practical execution risk left by the operator-authority compiler: the archive still carried two route narratives in the public tree. The current action spine and reviewer-first packet point to Eleos as the primary welfare-review route, while older AIID contact-selection surfaces remain necessary legacy controls for release-fast audits and historical route-first gates.

rev0273 therefore adds a **current route-head normalization record**. It does not delete historical AIID surfaces, but it demotes them to non-current secondary route-fit material unless a new signed human branch selects that path. The single current action head is reviewer-first Eleos, still no-send.

The second risk is human-decision ambiguity. A compiler can say `NOT-ACTIONABLE-NO-PRIVATE-AUTHORITY`, but the human still needs a minimum intake form that records exactly which branch is being chosen, which private roots exist, which hashes must be recomputed, and when to abort. rev0273 adds a public no-signature intake template for that step.

## Substantive change

- `examples/current-route-head-normalization-rev0273-eleos-primary-aiid-secondary.json` defines the single current route head and quarantines legacy AIID route-first surfaces as secondary/non-current unless a future signed branch reselects them.
- `examples/human-decision-intake-form-rev0273-unsigned-no-send.json` compresses the next human decision into a minimal checklist: no-send, defer, stop, or one exact reviewer-first send.
- `tools/audit_rev0273_route_head_decision_intake.py` makes route-head drift and human-decision overclaim fail release lint.

## Reliance limit

This revision still does not authorize contact. It does not prove private signature, private roots, send-time hash recompute, delivery, response, custody, reviewer appointment, welfare finding, or live-floor effect.
