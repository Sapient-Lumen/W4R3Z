# RFC-0013: derive-vmmd control plane interface

- Status: draft
- Author(s): (add names)
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary
Define the vmmd API surface, auth model, and audit requirements.

## Proposal (v1)
- local unix socket API
- request: artifact digest + manifest + instance name
- vmmd validates signature/trust + policy + resources
- returns instance_id + console/log handles

## Non-goals
- remote multi-tenant API in v1
