# Remedy-hardening-attestation recurrence-watch proof page — reopen-channel ledger, detection posture, and recurrence-safe sentence ceiling

## Purpose

This page is the proof surface for later readers who need to verify whether an outsider's clean state remained trustworthy across a named horizon.
It must preserve recurrence evidence rather than only the first clean-state event.

## Proof payload

The page must preserve at least:

- outsider identifier or audience slice
- clean-state establishment event
- watch horizon start and planned close condition
- reopen-channel ledger
- detector class per channel
- worst-case lag per channel
- containment / escalation posture per channel
- recurrence incidents observed during horizon
- portable evidence artifacts
- strongest honest recurrence-safe sentence
- blocked stronger recurrence-safe sentence

## Reopen-channel ledger

The ledger must support rows such as:

- `offline comeback precedence · open · detected on reconnect only · overwritten versions archived`
- `archive restore replay · open · detected by live runtime or later rescan · may bounce back as older`
- `rescan-only discovery · open · worst-case lag 600s or configured interval`
- `pause window residual effects · open · deletions and indexing still move`
- `read-only divergence · open · future sync suspended for changed files`
- `conflict artifact path · open · manual cleanup required`

## Proof principles

The page must make it impossible to confuse:

- `no recurrence observed yet`
- `all named channels prevented`
- `channels remain open but are watched`
- `channels remain open and detection is degraded`
- `recurrence happened and was repaired`
- `recurrence happened and the stronger sentence collapsed`

## Hard rules

The proof page must never allow:

- a single green snapshot to erase the reopen-channel ledger
- a completed remediation receipt to stand in for recurrence evidence
- short-window history to be the only retained proof of a longer watch horizon
- an unqualified `still clean` sentence without named horizon and named detection basis
