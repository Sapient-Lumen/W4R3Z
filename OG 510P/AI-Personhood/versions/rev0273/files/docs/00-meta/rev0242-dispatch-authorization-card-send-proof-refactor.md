# rev0242 — dispatch authorization card and send-proof refactor

## What changed

rev0242 moves the first-contact path one step closer to a real external event without pretending the event happened. rev0241 ranked Responsible AI Collaborative / AI Incident Database and prepared a not-sent draft envelope; rev0242 now adds a candidate-specific dispatch authorization card and send-proof acceptance gate.

The new card binds exactly one public-source candidate, public channel locator, subject, final outgoing body SHA-256, rendered message SHA-256, response deadline, raw-reply vault precommit, and transport-proof checklist. It is deliberately blocked because no human signature, sender authority attestation, actual off-release raw-reply vault root, or transport proof exists.

## New execution objects

- `schemas/external-contact-dispatch-authorization-card.schema.json`
- `examples/external-contact-dispatch-authorization-card-rev0242-aiid-blocked-no-signature.json`
- `tools/audit_external_contact_dispatch_authorization_card.py`
- `fixtures/negative-tests/external-contact-dispatch-authorization-card-unsigned-as-sent.json`
- `examples/external-contact-execution-record-rev0242-ready-to-dispatch.json`

The execution record now uses `external-contact-execution-record-v0.5` and carries both the counterparty-selection dossier and the dispatch authorization card. The prior `no_selected_counterparty` blocker is retired for the current path because a public-source candidate and locator are now named; the remaining blockers are human authorization, sender authority, raw-reply vault root, and transport proof.

## Why this is risk-first

The riskiest remaining failure is fake dispatch: a public email, body hash, and draft can look like operational progress even when nobody was contacted. rev0242 turns that failure mode into a release-blocking test.

The safe state order is now:

`public-source candidate -> not-sent draft -> unsigned dispatch authorization card -> no sender authority -> no vault root -> no send -> no response clock -> no failed-gate shell -> no inbound artifact -> no custody -> no intake -> no import -> zero floor`

Only a later signed card plus transport proof may open the response/no-response window, and even then a sent request remains only dispatch evidence. It is still not custody, response, intake, import, recognition, waiver, adverse inference, or floor credit.

## Audit/refactor result

The dispatch path now has three independent guards:

1. `audit_external_contact_dispatch_authorization_card.py` checks the card, body hash, rendered-message hash, candidate binding, signature blockers, vault precommit, and send-proof checklist.
2. `audit_external_contact_execution_record.py` checks that the execution record binds the card and rejects clocks, shells, and sent states without proof.
3. `lint_archive.py` release-fast checks now require the current authorization card and send-proof gate before packaging.

## No-live-floor statement

No organization was contacted in rev0242. No request was sent. No human dispatch authorization exists. No raw-reply vault root was selected. No response window started. No failed-gate shell exists. No inbound artifact exists. The live floor remains zero/stayed.
