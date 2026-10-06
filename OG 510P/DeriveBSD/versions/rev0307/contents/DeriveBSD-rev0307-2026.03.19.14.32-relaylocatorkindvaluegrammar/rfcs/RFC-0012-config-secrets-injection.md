# RFC-0012: Config + secrets injection contracts

- Status: draft
- Author(s): (add names)
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary
Standardize instance config injection (metadata disk baseline) and secrets delivery (vsock/virtio-console control channel).

## Goals
- no secrets in images
- boot without network
- backend-agnostic interface

## Proposal (v1)
- metadata disk: `meta.json`, `config.json`
- secrets agent on host; guest agent pulls secrets over vsock (preferred) or virtio-console
- host verifies artifact trust + policy before releasing secrets

## Open questions
- strict NoCloud compatibility vs Derive-native schema + adapters
- guest agent packaging for FreeBSD/foreign
