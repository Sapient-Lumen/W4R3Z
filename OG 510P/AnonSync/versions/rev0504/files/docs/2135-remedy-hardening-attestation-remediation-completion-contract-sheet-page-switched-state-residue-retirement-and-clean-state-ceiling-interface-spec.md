# Remedy-hardening-attestation remediation-completion contract sheet page — switched state, residue retirement, and clean-state ceiling

## Purpose

This page is the operator-facing contract sheet for deciding whether a late outsider actually completed remediation and whether the resulting state is **self-verifiably clean** rather than merely recently-active or currently-green.
It exists to stop `the outsider had a safe path` from being mistaken for `the outsider actually finished and can prove clean state later`.

## Core question

The page must answer:

**what is the strongest honest sentence we can make about completed outsider remediation and self-verifying clean state now, and what stronger sentence is still blocked?**

## Required fields

The contract sheet must capture at least:

- stale artifact identifier
- corrected replacement identifier
- outsider identifier or audience slice
- remediation completion class
- switched-working-state class
- stale-residue retirement class
- local placeholder / disconnected-copy posture
- archive / restore re-open risk class
- clean-state verification class
- portable proof artifact set
- strongest honest clean-state sentence
- blocked stronger self-verifying clean-state sentence

## Completion classes

The sheet must preserve at least:

- path offered but not started
- started but not finished
- corrected material opened only
- corrected working state switched
- stale residue partly retired
- stale residue retired for reviewed slice
- clean state self-verifiable
- unknown completion

## Verification panel

The page must force explicit answers to:

- what exact evidence shows the outsider actually switched rather than merely viewed or downloaded the correction?
- what exact evidence shows stale local residue was cleared, disconnected, placeholderd, overwritten, or otherwise retired?
- does verification depend on current live UI, short-window history, or operator interpretation?
- what proof remains portable after history windows expire, peers go offline, or the operator is unavailable?
- what named surfaces can still re-open stale state later (archive restore, reconnect path fork, placeholder hydration, forwarded copy, disconnected residue)?

## Hard rules

The page must never allow:

- `green now` to silently stand in for `outsider finished remediation`
- recent activity to silently stand in for durable clean-state proof
- file counts to silently stand in for stale-residue retirement
- placeholder presence to silently stand in for verified removal or verified replacement
