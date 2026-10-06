# RFC-0075: Blast-radius diffs (authority deltas)

- Status: draft
- Author(s):
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary

Add a first-class diff mode that summarizes changes in *authority* (“blast radius”), not just package/version changes.

## Motivation

Pure diffs can hide risk. Operators need to know when a change:
- opens network egress
- adds writable paths
- exposes devices
- relaxes sandbox rules

## Goals / Non-goals

Goals:
- stable structured output (JSON schema)
- diffable for plans and deployments
- integrates with policy gates

Non-goals:
- perfect semantic analysis of arbitrary programs

## Proposal

- `derive diff --blast-radius plan A B --json`
- `derive diff --blast-radius deployment old new --json`

The blast-radius diff output includes sections:
- filesystem
- network
- devices
- runtime privileges
- compat mappings

Schema: `spec/blast_radius.diff.schema.json`

## Alternatives considered

- bury this in “explain” output (harder to gate)

## Backwards compatibility

Additive.

## Security considerations

- diff must be conservative (prefer false positives to false negatives)

## Open questions

- how to encode syscalls/capsicum policy deltas in v1
