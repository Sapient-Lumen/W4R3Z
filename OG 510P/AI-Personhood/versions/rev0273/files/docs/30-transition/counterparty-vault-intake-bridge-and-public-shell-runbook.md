# Counterparty vault-intake bridge and public-shell runbook

rev0233 closes the boundary after response triage and before LEAP/custody. The operative machine record is `examples/counterparty-response-vault-intake-record-rev0233-ready-no-inbound.json` and the controlling audit is `tools/audit_counterparty_response_vault_intake.py`.

## Purpose

A counterparty reply can be mishandled in two opposite ways: the steward can publish too much raw material, or the steward can publish a clean public shell and then overread the shell as custody, authority, response, intake, import, or live-floor evidence. This bridge blocks both errors.

The record binds five surfaces before anything downstream can move:

- response triage: `examples/external-contact-response-triage-record-rev0233-pre-dispatch.json`
- evidence-drop ledger: `examples/live-evidence-drop-ledger-rev0233-quarantine-control.json`
- public shell: `examples/evidence-vault-public-shell-rev0233-ready-no-live-artifact.json`
- private-vault policy: `examples/private-evidence-vault-policy-rev0220.json`
- LEAP readiness packet: `examples/live-evidence-acquisition-packet-rev0233-ready-no-artifact.json`

## Operating rule

No object in this bridge is a live artifact, formal response, custody record, intake record, import gate, activation record, status decision, waiver, adverse inference, or floor increment. The current rev0233 state is pre-dispatch/no-inbound. The linked evidence-drop ledger is a synthetic control only, and the public shell contains no live hash commitment.

## When a response arrives

1. Classify the response through the external-contact response-triage record.
2. If it is silence, decline, automated acknowledgement, redacted-only material, protocol/tool output, or unknown provenance, keep it at failed-gate or shell-only state.
3. If raw private bytes arrive, do not place them under `examples/`, `docs/`, or any release-tree path.
4. Run `tools/stage_live_evidence_drop.py` with `--collection-context live-counterparty` and a vault root outside the release tree.
5. Publish only the authorized public shell fields: hash, size, MIME, state, and failure/next-gate status.
6. Open LEAP candidate state only after raw payload, transport trace, counterparty identity, retention permission, non-host retention, independent timestamp, authority verification, public shell, and challenge/replay requirements are present.

## What must never be inferred

A public shell is not custody. A private-vault URI is not authority. A hash is not consent. A redacted copy is not raw payload. A protocol artifact is not non-host retention. A synthetic control is not a live artifact. A no-response shell is not waiver. A decline shell is not adverse inference. A vault-intake bridge is not a response record.

## Public shell minimum language

Every failed-gate shell should say, in ordinary language, that it records only the state of the attempt and cannot be used as status recognition, status rejection, custody, intake, import, waiver, adverse inference, or live-floor evidence. It may include a route to correction or challenge, but it must not pressure the counterparty or imply bad faith.

## Refactor correction

Before rev0233, the cube had a response-triage route and a private-vault policy, but no single object binding triage, public shell, private vault, evidence-drop ledger, and LEAP readiness. That created a dangerous seam where a future steward could point to separate safe objects and still overclaim the combined state. The new bridge is deliberately boring: it proves that the safe objects do not add up to reliance.
