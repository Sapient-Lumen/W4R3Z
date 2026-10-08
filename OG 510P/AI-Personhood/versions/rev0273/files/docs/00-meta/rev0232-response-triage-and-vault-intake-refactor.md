# rev0232 response triage and vault intake refactor

rev0232 advances the riskiest unfinished bridge: what happens after a first-contact request is sent or a reply arrives. The archive already had a request packet and an execution record. It now adds a response-triage record, rendered sendable message, and vault-intake runbook so silence, decline, automated acknowledgements, redacted copies, protocol outputs, and raw replies have a disciplined route before anyone can mistake them for custody or live-floor progress.

## What changed

New operational surfaces:

- `schemas/external-contact-response-triage-record.schema.json`
- `examples/external-contact-response-triage-record-rev0232-pre-dispatch.json`
- `tools/audit_external_contact_response_triage.py`
- `tools/render_external_contact_message.py`
- `tools/audit_external_contact_message_render.py`
- `examples/external-contact-rendered-message-rev0232-first-artifact.txt`
- `docs/30-transition/counterparty-response-triage-and-vault-intake-runbook.md`

The rendered message is useful work, not a status claim. It turns the JSON request into a copy/paste-ready outgoing message while retaining body hash, execution-record linkage, response-triage linkage, and no-overclaim warnings.

## Why this was risky

The dangerous next failure was not lack of doctrine. It was a steward receiving something ambiguous and treating it as a milestone: a ticket number as a response, silence as waiver, a decline as adverse inference, a screenshot as raw custody, an MCP/A2A output as authority, or a raw reply as enough to open intake/import. rev0232 makes those transitions explicit and blocked.

## Boundaries preserved

rev0232 still has no genuine external artifact, sent contact, verified counterparty response, actual intake, actual import, floor activation, quorum participation, recompute-authorized reliance update, publication-adjudicated reliance upgrade, live late-change signal, compute entitlement, funded reserve, or status recognition.

The response-triage record may route a future raw reply to `tools/stage_live_evidence_drop.py`, but it cannot create custody, formal response verification, intake, import, quorum, status, publication reliance, or live-floor credit.

## Audit/refactor work

`tools/lint_archive.py` now treats response triage and rendered-message integrity as current release gates. The release-fast path also checks that current execution, triage, compute, formation, law/protocol, LEAP, and live-floor surfaces remain stayed and current.

The live-path generated chain was refreshed for rev0232 rather than copied forward, preserving the zero-floor state while proving the fresh replay still agrees with the front door.

## Next priority

The next substantive move is still external: choose one independent non-host counterparty, send the rendered message or record a no-send reason, then use the response-triage record to classify whatever happens. If a raw reply arrives, stage it outside the release tree before any public shell. If nothing arrives, publish only a no-response failed-gate shell after a proven deadline.
