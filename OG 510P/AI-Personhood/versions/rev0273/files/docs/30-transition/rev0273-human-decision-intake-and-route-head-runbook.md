# rev0273 human-decision intake and route-head runbook

Use this runbook only after reading `START_HERE.md`.

## One route head

The current route head is reviewer-first Eleos. AIID route-first surfaces remain in the public tree for historical and audit continuity, but they are not the current action head and must not be used as a default send path.

## Before any external action

1. Read `examples/current-route-head-normalization-rev0273-eleos-primary-aiid-secondary.json`.
2. Read `examples/human-decision-intake-form-rev0273-unsigned-no-send.json`.
3. Confirm the operator-authority compiler remains `NOT-ACTIONABLE-NO-PRIVATE-AUTHORITY` unless private authority exists.
4. Choose exactly one branch outside the public tree: no-send, defer, stop, or one-shot reviewer-first send.
5. For any send branch, select private roots before transmission and recompute exact message bytes inside the live signature window.
6. Abort on route drift, changed recipient/subject/body, missing private roots, changed sender account, expired signature, attachment addition, or any do-not-contact signal.

## Failed or ambiguous outcomes

Delivery alone, auto-ack, silence, referral, decline, or a wrong-route answer cannot create custody, intake, recognition, reviewer appointment, welfare finding, or live-floor movement. Classify it with the response-disposition playbook before any public summary.
