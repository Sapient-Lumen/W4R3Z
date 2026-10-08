# Counterparty artifact normalization gate runbook

This runbook handles the seam after response triage and vault intake but before candidate challenge. Its job is deliberately narrow: decide whether inbound material is safe and complete enough to become a candidate-challenge object. It does not create custody, formal response, intake, import, recognition, or live-floor credit.

## The risky seam

The archive can now render a request, record dispatch state, triage silence/decline/ack/reply, and stage or shell inbound material. The next failure mode is subtler: a public shell, redacted copy, protocol artifact, private-vault locator, or unsafe attachment can look operationally “real enough” that someone opens candidate challenge without the minimum raw-evidence checks.

That is evidence laundering. Normalization must block it.

## Required order

1. Confirm the response triage record is current and still no-floor.
2. Confirm the vault-intake bridge is current and still no-floor.
3. Confirm the evidence-drop ledger state:
   - `ready-no-drop` or `quarantine-control`: no candidate challenge.
   - `live-candidate-drop`: possible candidate challenge only after all minimum inputs are verified.
   - `rejected`: publish only failed-gate shell state.
4. Confirm raw bytes are outside the release tree and represented publicly only by authorized hash/size/MIME/shell fields.
5. Reject redacted-only material, protocol/tool output, synthetic controls, unsafe archives, path traversal, and scan-pending payloads as candidate substitutes.
6. Verify transport trace, counterparty identity, retention permission, non-host retention, independent timestamp, and scoped authority.
7. Only then prepare a candidate-challenge/replay report. Even then, custody, formal response, intake, import, status, and floor effects remain separate gates.

## Stop conditions

Stop and publish only a failed-gate shell when any of these are true:

- no inbound raw artifact exists;
- the only material is a redacted public copy;
- the only material is MCP, A2A, API, relay, or other protocol/tool output;
- the raw payload entered the release tree;
- a private-vault URI is being treated as authority;
- hash/size/MIME is missing;
- nested archive or path traversal is unresolved;
- malware/safety scanning is pending or failed;
- transport trace, counterparty identity, retention permission, non-host retention, independent timestamp, or scoped authority is missing.

## Operator rule

A normalization decision may open the later candidate-challenge report only if every minimum input is present. It may never by itself create custody, a formal response, an intake record, import readiness, a live-floor increment, status recognition, waiver, adverse inference, or public release of raw payload bytes.

## Current rev0234 state

`examples/counterparty-artifact-normalization-decision-rev0234-pre-dispatch.json` is intentionally pre-dispatch/no-inbound. It is useful because it gives the next operator a precise checklist and a failing state, not because it proves any external fact.
