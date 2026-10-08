# Timestamp provenance proof page — disk mtime, ledger mtime, and visible divergence

## Purpose

Provide a proof surface whenever the product knows that the timestamp visible in the filesystem is not the only or not the authoritative chronology source.

This page answers:

> what timestamp does the operator see, what timestamp does the product trust, and how should the difference change interpretation of `modified`, `latest`, or `restored`?

## Core regions

### Visible-time row

Show:

- path / subject
- filesystem-visible `mtime`
- observation time
- whether the product currently trusts that value for chronology

### Ledger-time row

Show:

- ledger / database `mtime`
- how it was learned or preserved
- whether it is currently authoritative
- whether it differs from disk-visible time

### Divergence explanation card

Possible explanations:

- `assignment failed; ledger preserved authoritative mtime`
- `restored candidate carries older source mtime`
- `clock trust degraded; chronology confidence lowered`
- `no divergence detected`

### Consequence card

Say plainly whether the operator may safely infer:

- `latest on disk equals latest in swarm`
- `restored file timestamp reflects victory chronology`
- `freshness can be read from the file browser alone`

### Safer-next-action card

Examples:

- `Use ledger time for chronology decisions`
- `Open replay chronology review`
- `Export subject with time-proof receipt`
- `Revalidate peer clocks before trusting latest-wins`

## Required fields

- subject identifier
- disk `mtime`
- ledger `mtime`
- divergence verdict
- authority verdict
- strongest safe sentence
- stronger rejected sentence

## Interaction rules

- Never hide divergence behind a tooltip-only info icon.
- Copy/export actions may include both timestamps, but must label which one is authoritative.
- UI tables may sort by visible time or authoritative time, but they must label which basis is active.
