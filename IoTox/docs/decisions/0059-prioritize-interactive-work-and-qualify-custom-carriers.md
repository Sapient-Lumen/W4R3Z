# ADR 0059: Prioritize interactive work and qualify custom carriers

Status: accepted
Date: 2026-08-15

## Context

Every toxcore call used one FIFO owner queue. File chunk work could therefore sit ahead of text,
future terminal control, or session work even though all calls must remain serialized. Ordinary Tox
text read receipts also showed 0.5–1.0 second tails that could not be attributed to the local owner
queue. Ratox-first protocol work needed a measured carrier boundary before inventing terminal wire
semantics.

## Decision

Classify owner commands as `interactive`, `control`, or `bulk`. Service a fixed 8:4:1 weighted
schedule, give a newly nonempty interactive queue one preemptive service without rewinding that
schedule, and run at most 16 owner commands before calling `tox_iterate`. Human message/typing and diagnostic
interactive packets use the interactive class; file offers/chunks/seeks use bulk; durable machine
and file-control work remains control unless a later ADR says otherwise.

Cap the provider-requested owner sleep at a configurable 20 ms by default. Sleeping less than
`tox_iteration_interval` is permitted; the cap does not skip provider iteration. Publish requested
and effective intervals, iteration count, per-class pending/executed counts, and maximum queue wait.

Consume the official c-toxcore custom-lossy send/callback API in addition to the existing lossless
API. Reserve fixed diagnostic IDs `0xA1` (lossless) and `0xC8` (lossy custom range) for a 10-byte
request/reply echo. The echo:

- requires an already transcript-confirmed IoTox session;
- carries only kind and random nonzero nonce;
- is size-symmetric and creates no amplification;
- is not an IoTox 1.0 application frame, capability, or advertised feature;
- exists only through an explicit local research operation.

Use custom-lossless packets as the first Ratox interactive carrier. Human text remains chat.
Custom-lossy remains research-only until controlled impairment demonstrates an advantage large
enough to justify duplication/reordering/loss semantics. The transport-independent prerequisites
are a bounded cumulative byte replay window, an attachment-generation fence, and a monotonic RTT
estimator; none is advertised as a remote terminal.

## Consequences

Interactive local admission no longer waits behind an arbitrary bulk FIFO prefix, while toxcore
still has exactly one owner. A preemptive service does not move the weighted cursor; bulk therefore
cannot starve because every 13 scheduled selections contain a bulk slot,
and provider progress cannot starve because each visit is bounded to 16 commands.

The 20 ms cap trades wakeups for latency, so evidence must report iteration and CPU/context-switch
cost rather than treating it as free. It does not cure provider/path head-of-line behavior.

The genuine gate selected lossless on observed direct UDP: lossless and lossy medians were nearly
identical and neither missed 250 ms, while forced TCP lossy missed more deadlines. This is a
founding-host result, not controlled-loss or two-host qualification.

Adding fixed unadvertised diagnostic IDs does not change protocol 1.0 negotiation. Any future
terminal frame, authority capability, or feature advertisement requires a separate versioned ADR.
