# ADR 0298: Join namespace health to content-free diagnostics

- Status: accepted and implemented
- Date: 2026-09-02

## Context

ADR 0291 made Agent faults exportable without copying logs, config, paths, identities, or content.
ADR 0297 then defined a signed tree-v2 namespace-health record, but an operator still had to inspect
every namespace separately and manually explain the result alongside a support bundle. Copying the
records themselves would expose stable namespace and policy commitments and make separate reports
more correlatable than necessary.

## Decision

Local-control v1.55 keeps operation 108 but changes its self-describing redacted payload to
`iotox-diagnostics-redacted-v2`. Before export the Agent verifies every cached tree-v2 health record
under the namespace-mutation lock and reduces the set to one closed aggregate. The bundle reports
eligible, verified, absent, and invalid record counts; green/yellow/red and complete/partial custody
counts; stale-policy, conflict, missing-object/byte, automation-stall, store-pressure, source-
exhaustion, source-result, and maximum failure-streak totals.

No namespace name, path, principal, content digest, namespace/policy commitment, signature, signer,
timestamp, or stable per-namespace slot enters the shareable payload. Older engines are not counted
as missing because ADR 0297 deliberately does not claim health parity for them. The existing 48 KiB
redacted and 64 KiB bundle ceilings remain. Oldest flight records, not health truth, remain the only
data omitted to meet the bound.

The export freezes `namespace-health-rollback-witness=0` and
`namespace-health-backup-certified=0`. Offline inspection accepts legacy v1 payloads and labels their
health as absent; exports at this decision use v2, superseded by ADR 0299 v3. The outer bundle
framing and digest domain remain v1 because their byte-integrity semantics did not change. No peer,
Ratox, sync-object, authority, or
Tox framing changes.

## Consequences

A single inspect-before-share artifact can now distinguish a healthy sparse fleet from missing
selected content, stale policy, corrupt/absent health records, or exhausted sources without revealing
which namespace has the condition. The privacy choice is intentional: remediation still uses local
`sync-health NAMESPACE`, while a support recipient gets only aggregate structure.

The deterministic gate validates the v2 aggregate grammar, invariant refusal, privacy exclusions,
bundle round-trip, permanent non-backup qualifiers, and legacy-v1 inspection. The live Agent gate
proves one signed green partial-custody record becomes an anonymous aggregate. This is not device
authorship, remote attestation, non-omission proof, rollback resistance, backup certification, or a
normalized host-capability report.
