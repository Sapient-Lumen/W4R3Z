# RFC-0136: Network egress as a capability-mediated service

Status: **Draft**  
Last updated: 2026-02-24

## Problem

Sandboxing fails if networking is ambient authority. We need a DeriveBSD-native primitive for:
- deny-by-default egress in compartments
- explicit policy-granted network access
- receipts for audit and explainability

## Proposal

Add an optional lane:
- `system.net` broker service
- `net-egress-grant` evidence object
- `net-flow-receipt` evidence object

Sandbox workloads obtain network access only through broker-minted flow handles.

## Data model

See:
- `spec/net.egress.grant.schema.json`
- `spec/net.flow.receipt.schema.json`

## Threat model highlights

- data exfiltration from compromised sandbox
- covert channels via DNS
- long-lived, unreviewed “allow all” exceptions
- inability to audit after the fact

## Rollout plan

1) Start as “broker-only network” for sandbox VMs.
2) Introduce lint rules that block merging caproute graphs with unrestricted egress in high-assurance profiles.
3) Add interactive portal UX for desktop-style apps.

## Open questions

- exact enforcement mechanism for jails vs VMs (proxy vs VNET attach)
- how to handle UDP and QUIC efficiently while still receipting
