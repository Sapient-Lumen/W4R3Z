# rev0241 — counterparty selection dossier and dispatch authority refactor

## What changed

rev0241 converts the public-source shortlist into an auditable counterparty-selection dossier and a not-sent top-candidate draft envelope. This is intended to move the first-contact path closer to a real external event without faking the event.

The highest-ranked candidate is Responsible AI Collaborative / AI Incident Database because its public contact page lists a collaboration email and its mission is close to incident/evidence preservation. The ranking is deliberately non-operative: it is not contact, not consent, not authority, not a selected recipient, not dispatch, not no-response, and not a failed gate.

## New execution objects

- `examples/external-contact-counterparty-selection-dossier-rev0241-public-source-ranked-not-authorized.json`
- `examples/external-contact-draft-envelope-rev0241-aiid-not-sent.txt`
- `schemas/external-contact-counterparty-selection-dossier.schema.json`
- `tools/audit_external_contact_counterparty_selection_dossier.py`
- `fixtures/negative-tests/external-contact-counterparty-selection-ranking-as-authorization.json`

The dossier scores candidate fit, channel actionability, non-host independence, artifact-retention fit, and conflict-review load. It also records the missing unblockers: human recipient authorization, sender authority, conflict acceptance, raw-reply vault root, and transport-proof capture.

## Why this is risk-first

The riskiest remaining failure is not lack of doctrine; it is fake momentum around first contact. The cube can now distinguish four states that were easy to blur:

1. public-source research;
2. ranked candidate;
3. not-sent draft envelope;
4. actual sent request with transport proof.

Only the fourth state may start a response/no-response clock, and even then it still creates no custody, intake, import, status, waiver, adverse inference, authority evidence, or live-floor effect.

## No-live-floor statement

No organization was contacted in rev0241. No request was sent. No response window started. No raw reply vault was selected. No inbound artifact exists. The live floor remains zero/stayed.
