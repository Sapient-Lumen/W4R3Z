# Counterparty response triage and vault intake runbook

This runbook closes the gap between a sendable request and a usable artifact. Its purpose is not to make a reply count. Its purpose is to keep every reply, silence, decline, acknowledgement, screenshot, protocol artifact, or raw response from being laundered into custody, intake, import, status recognition, waiver, adverse inference, or live-floor credit.

## Operating rule

A sent request is only dispatch trace. A deadline is only a response-window boundary. A decline is only a failed-gate state. Silence is only a no-response state. An automated acknowledgement is only transport trace. A protocol or tool output is only protocol evidence. A redacted copy is only a public artifact. A raw reply is only a candidate payload until private-vault staging, authority, non-host retention, verifier, timestamp, independence, challenge/replay, custody, response verification, intake conversion, import readiness, actual import, activation, quorum, recompute, and publication checks all pass.

The current machine-readable surface is `examples/external-contact-response-triage-record-rev0239-pre-dispatch.json`. Use it before opening any downstream object.

## Triage sequence

1. Confirm the request packet and execution record are current: `examples/external-contact-request-packet-rev0239-first-artifact.json` and `examples/external-contact-execution-record-rev0239-ready-to-dispatch.json`.
2. If the request was not sent with proof, do not publish a no-response shell. Record only an internal still-ready state or a first-class `no-send-recorded` state. A no-send record is evidence of non-dispatch, not a counterparty silence event.
3. If the request was sent, preserve the final outgoing subject/body hash, sender role, sent time, transport proof, message/header reference, and exact deadline.
4. If no response arrives before the deadline, prepare a no-response failed-gate shell. It must say silence is not waiver, adverse inference, status evidence, custody, response, intake, import, or live-floor evidence.
5. If the counterparty declines, preserve only what the counterparty permits and publish at most a decline shell. Do not pressure the counterparty or infer bad faith.
6. If only a ticket, bounce, read receipt, or automated acknowledgement arrives, attach it to dispatch trace only. Do not open response verification.
7. If a raw reply arrives, do not place raw bytes in the public tree. Stage it outside the release tree with `tools/stage_live_evidence_drop.py --collection-context live-counterparty --vault-root <outside-release-tree>` and publish only authorized hash/size/MIME and gate status.
8. If only a screenshot, redacted copy, summary, or forwarded paraphrase is available, mark it redacted-only and keep raw-custody gates closed.
9. If the artifact comes through MCP, A2A, an API relay, or federated agent transport, preserve the protocol boundary and require independent authority, retention, verifier, timestamp, and counterparty identity before any LEAP candidate state.

## What to publish

A public shell may include: triage state, send-proof status, response-window status, artifact kind, authorized hash/size/MIME, gate-failure reason, and no-waiver/no-adverse-inference language.

A public shell must not include: raw private bytes, trade secrets, personal data, confidential counterparty conditions, waiver language, adverse-inference language, status-recognition or status-rejection language, live-floor claims, import claims, or proof-by-protocol claims.

## Corrective refactor

rev0239 adds a response-triage schema and audit because rev0231 still left an avoidable gap: once a message is sent, the next steward could overread an auto-reply, silence, or redacted screenshot. The new audit turns that boundary into a code gate.


## Rev0239 vault-intake lock

A dispatch preflight or no-send record is not an inbound artifact. Vault intake remains unavailable until a real non-host response is staged outside the release tree with raw-byte preservation, source metadata, redaction boundary, and triage classification.
