# Documentation index — rev0273

Current last-mile surfaces: `examples/current-action-spine-rev0273-reviewer-first-no-send.json`, `examples/last-mile-operator-checklist-rev0273-reviewer-first-no-send.json`, `examples/pre-send-evidence-bundle-rev0273-reviewer-first-no-send.json`.


This release preserves the authority-to-artifact chain from unsigned human decision, through custody preconditions, to the six-artifact pilot; it only narrows the current route head and human decision intake.


**Route head:** `examples/current-route-head-normalization-rev0273-eleos-primary-aiid-secondary.json` is the current route-head record. Reviewer-first Eleos is the only current action head; legacy AIID route-first surfaces are secondary/non-current unless a future signed branch selects them.

**Human decision intake:** `examples/human-decision-intake-form-rev0273-unsigned-no-send.json` is the public no-signature intake shell for the next real decision. It cannot authorize contact.

**Operator compiler:** `examples/operator-authority-packet-compiler-rev0273-reviewer-first-no-signature.json` remains `NOT-ACTIONABLE-NO-PRIVATE-AUTHORITY`.

**Send transaction:** `examples/send-attempt-transaction-ledger-rev0273-no-signature-aborted.json` remains `NO-SEND-FAIL-CLOSED`.

**Pre-send expiry bundle:** `examples/pre-send-evidence-bundle-rev0273-reviewer-first-no-send.json` is the fail-closed stale-readiness guard; no send is permitted from this public bundle.

Start with `../START_HERE.md`, then read `docs/00-meta/rev0273-route-head-and-human-decision-intake-refactor.md` and `docs/30-transition/rev0273-human-decision-intake-and-route-head-runbook.md`.

No external contact, delivery, response, custody, intake, import, recognition, reviewer appointment, welfare finding, or live-floor effect exists.
