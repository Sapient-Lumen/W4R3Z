# rev0261 — route-first branch hold and no-send nonclosure refactor

rev0261 fixes the next execution risk: the no-attachment route-first lane was auditable, but non-dispatch could still blur into drift. This revision records an explicit **current-revision no-send hold** for the route-first branch because the public release still lacks the things this environment cannot honestly create: human signature, sender authority, send-time locator recheck, private vault roots, final pre-send hash recompute, and actual transport proof.

## What changed

- Added `examples/external-contact-route-first-branch-hold-rev0261-aiid.json`.
- Added `schemas/external-contact-route-first-branch-hold.schema.json`, `tools/audit_external_contact_route_first_branch_hold.py`, and a negative fixture rejecting no-send-as-task-closure.
- Bound the hold to the existing route-first preflight, send/capture gate, reply disposition shell, stage-two authorization gate, human/sender precommit, locator recheck, hash dry run, transport plan, and seven-item operating board.
- Updated the front door so the active state is no longer ambiguous branch-pending; it is explicit hold/no-send for this revision.

## Why this is substance rather than bureaucracy

The previous state invited another session to ask, again, whether to send. rev0261 answers the part that can be answered inside the public tree: **do not send from this release without human/private authority, and do not close the first-artifact work just because no send occurred.**

This burns down ambiguity while preserving the real task. The first-artifact, live-evidence, and live-counterparty-response tasks remain active. The hold is a branch state, not completion.

## Boundaries

No organization has been contacted. There is no sent copy, transport trace, delivery status, DSN, Message-ID, response clock, inbound artifact, custody, intake, import, recognition, or live-floor effect. The hold cannot be treated as silence, decline, waiver, adverse inference, authority, consent, contact, or a failed gate.

Stage two remains deferred. A later willing reply or separate authorization would still require a fresh stage-two gate, human signature, sender authority, private vault roots, locator recheck, final hash recompute, and transport proof.
