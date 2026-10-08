# rev0208 live evidence acquisition and independence-discount refactor

rev0208 is a substantive first-real-artifact pass. It does not acquire a live artifact and does not increase the live receipt floor. It makes the missing pre-response step executable: before any response, intake, import gate, replay, or quorum recomputation can be created from a live-looking artifact, the archive now requires a Live Evidence Acquisition Packet (LEAP) with raw payload custody, authority scope, cryptographic verifier-adapter requirements, counterparty independence fields, protocol-boundary locks, and failed-gate exit criteria.

## What changed

- Added `schemas/live-evidence-acquisition-packet.schema.json` and `examples/live-evidence-acquisition-packet-rev0208-ready-no-artifact.json`.
- Added `tools/audit_live_evidence_acquisition_packet.py` and two negative fixtures for protocol-output-without-raw-custody and correlated-counterparty discount bypass.
- Refactored live-floor admission logic into `tools/live_floor_lib.py` so eligibility and independence discount are shared, auditable, and not embedded only inside the snapshot builder.
- Updated `tools/compute_live_receipt_floor.py` to create a candidate set first, then apply dependency-group, counterparty-org, issuer/host, and receipt-class discount before counting any independent live receipt.
- Extended the positive-control harness with `correlated-positive-duplicate-dependency-discount`, proving that valid-looking, cryptographically verified candidates sharing dependency/counterparty dependencies do not both count.
- Updated the current law/protocol watch for the latest MCP, A2A, Sigstore/Rekor, and RATS relevance to live evidence acquisition.

## Why this is the risk-first move

The bottleneck is no longer whether the archive can write a policy saying an artifact should be checked. The bottleneck is whether the next live-looking artifact can be stopped before it creates downstream state if it is merely a protocol success, provenance label, signed blob, redacted copy, or correlated counterparty response. LEAP is deliberately pre-response: missing raw payload, authority, timestamp/key evidence, non-host retention, or independence keeps `response_creation_allowed=false`.

## Independence rule now enforced

A gate that passes live-counterparty eligibility and has a verified cryptographic adapter is only a candidate. It still receives zero or discounted weight unless the independence engine finds a distinct dependency group, distinct counterparty organization, distinct issuer key relative to the subject host, no correlation discount, and a receipt class not already satisfied by another counted candidate.

This is intentionally conservative. Cryptographic authenticity can show a payload was signed. It does not show that the signer had class-specific authority, that the subject/representative authorized the evidence path, that a non-host retained the artifact, or that multiple receipts are independent.

## External protocol implications

Current MCP documentation describes a protocol with powerful data-access and code-execution paths, explicit consent/control requirements, and untrusted tool descriptions unless from trusted servers. A2A documentation describes interoperable opaque agents that can discover, delegate, and exchange results, while distinguishing A2A agent-to-agent coordination from MCP agent-to-tool integration. Sigstore/Rekor supplies useful patterns for hash/signature/timestamp transparency, and RATS supplies useful attester/verifier/relying-party vocabulary. None of those sources can substitute for LEAP's class-specific authority, raw custody, non-host retention, subject authorization, and independence checks.

## Reliance effect

Reliance remains stayed. rev0208 creates no live response, no intake, no actual import, no class-local live replay, and no live-floor delta. The computed floor remains zero.

## Next non-doctrinal move

The next real move is to populate LEAP with a genuine live or institutionally witnessed counterparty artifact. If any required slot is missing, the result should be a public failed-gate summary with no live-floor delta, not another doctrine expansion.
