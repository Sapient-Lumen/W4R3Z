# rev0236 — custody authority evidence binder refactor

rev0236 focuses on the seam after candidate-challenge disposition and before the custody authority gate. The failure mode was not missing doctrine; it was checkbox theatre. A custody gate could require a disposition record, but authority itself still risked being represented as booleans or operator flags rather than cited evidence.

## Mission move

The live path now requires an authority-evidence binder before a custody gate may consume a candidate disposition. The binder does not prove personhood, create custody, or create a response. It exists to answer a narrower question: is there human-reviewed, class-scoped, cited evidence that the counterparty or representative had authority for the exact receipt class being routed into custody review?

The current release answer is deliberately no. `examples/custody-authority-evidence-binder-rev0236-pre-dispatch-no-authority.json` is pre-dispatch/no-authority, because no genuine request has been sent and no genuine inbound counterparty response exists.

## New operational object

The new object is `schemas/custody-authority-evidence-binder.schema.json`, with the current example `examples/custody-authority-evidence-binder-rev0236-pre-dispatch-no-authority.json` and audit `tools/audit_custody_authority_evidence_binder.py`.

The binder requires evidence references for:

- manual counterparty contact;
- request trace;
- subject or representative authority;
- receipt-class scope;
- verifier adapter;
- independent timestamp;
- non-host retention;
- sealed/public parity;
- redaction boundary;
- dependency independence;
- public authority limitations.

Unsafe substitutes are explicit: protocol/tool output, automated acknowledgement, private-vault URI, redacted copy, operator checkbox, silence, elapsed time, and synthetic control cannot satisfy authority evidence.

## Custody gate refactor

`tools/prepare_custody_authority_gate.py` now accepts `--authority-evidence-binder` and the custody-gate schema carries an `authority_evidence_binder` block. Even a valid candidate disposition cannot make a custody gate eligible unless the binder is verified and allowed to feed the gate.

`tools/prepare_counterparty_artifact_custody_record.py` also checks the binder block before any custody record can be prepared. This closes the shortcut where a disposition plus authority-looking flags could create the appearance of custody readiness.

## Admission graph change

The live admission graph is now:

`evidence drop → LEAP → candidate challenge → candidate disposition → authority evidence binder → custody gate → custody → response verification → response → intake conversion → intake → import readiness → actual import → floor activation → quorum participation → computed floor`

The graph audit now requires `AUTHORITY_EVIDENCE_BINDER` as a distinct node and checks that no current binder is consumable.

## Negative fixtures

rev0236 adds fixtures that block:

- operator checkbox as authority evidence;
- MCP/A2A/API/protocol output as authority evidence;
- private-vault URI as authority evidence.

These fixtures preserve the cube's core anti-laundering rule: storage, transport, shell publication, and tool messages are not authority.

## What remains missing

No genuine external request has been sent. No genuine counterparty artifact, verified response, authority evidence, positive binder, custody record, intake, import, floor activation, quorum participation, entitlement, compute reserve, recognition, or live-floor effect exists.

The next substantive move is still external: send the first-contact request or record a concrete no-send reason. If inbound material arrives, it must pass response triage, vault intake, normalization, candidate challenge, candidate disposition, and the new authority evidence binder before any custody-gate eligibility claim.
