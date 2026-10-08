# Remedy-hardening-attestation remediation-completion proof page — completion evidence, residue ledger, and clean-state sentence ceiling

## Purpose

This page is the proof-bearing companion to the remediation-completion contract sheet.
It keeps the evidence ledger for whether the outsider actually finished remediation and whether clean state is provable without operator memory.

## Proof packet contents

The page must keep at least:

- completion evidence ledger
- switched-state evidence ledger
- stale-residue retirement ledger
- remaining re-open vectors
- portable proof artifact list
- clean-state verification verdict
- strongest honest clean-state sentence
- blocked stronger self-verifying clean-state sentence

## Evidence classes

The proof page must distinguish at least:

- activity only
- opened or downloaded only
- configuration or state switch observed
- stale copy retired observed
- portable receipt attached
- operator-memory only
- contradictory or incomplete evidence

## Sentence engine rules

The page must preserve the difference between:

- `the outsider interacted with the correction`
- `the outsider switched to the corrected working state`
- `the outsider retired the reviewed stale residue`
- `the outsider can later prove clean state without operator help`

## Hard rules

The proof page must never allow:

- current status icons to erase offline-scope uncertainty
- expiring history to count as durable proof unless separately exported into a portable artifact
- archive absence in one surface to stand in for full stale-residue retirement everywhere
- one clean slice to silently stand in for all local stale state
