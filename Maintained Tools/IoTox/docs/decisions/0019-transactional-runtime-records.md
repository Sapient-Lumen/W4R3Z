# ADR 0019: Multi-file runtime records publish transactionally

**Status:** accepted and implemented in rev0005

## Context

A peer request or transfer represented by several files can be observed halfway through
creation, causing scripts to act on incomplete facts.

## Decision

Prepare each request or transfer record in a private `0700` temporary directory, write all
`0600` fields, then publish the complete directory by rename. Remove stale records after the
new active set has been published.

## Consequences

Local observers see a complete record or no record. The runtime tree remains a projection,
not a durable database. Disk exhaustion and crash residue still require explicit tests and
cleanup policy.
