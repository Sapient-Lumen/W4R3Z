# ADR-0294: Breakglass interactive sessions carry tty-recording proof and start at session open

Status: Accepted  
Date: 2026-03-23

## Context

`ADR-0208` already fixed that output-only TTY/console recording is the routine stronger evidence lane for breakglass shell or recovery-console work in the profiles that review such sessions. But one implementation-shaping ambiguity remained open: exactly **when** that stronger evidence starts, and how the authoritative `breakglass.receipt` points at the exact terminal evidence artifact instead of leaving responders to reconstruct the trail from support bundles, local spool state, or rescue-shell memory.

That ambiguity is expensive because it silently reopens two bad lanes:

- recording begins only after the operator is already inside a recovery shell, so the highest-risk early commands fall outside the reviewed evidence story
- the breakglass receipt proves emergency authority existed, but not which exact `tty.session.recording` artifact carries the stronger shell/console trail

## Decision

For the first reviewed interactive breakglass shell/console lane:

1. `breakglass.receipt` may carry an `evidence` object with `tty_recording_digests`.
2. When interactive breakglass shell/console work emits `tty.session.recording` evidence, `breakglass.receipt.evidence.tty_recording_digests` is the canonical join surface for those artifacts.
3. The reviewed baseline start posture is `tty_recording_start_posture = session-open-before-first-prompt`.
4. v0 does **not** bless “enter rescue shell first, decide to start recording later” as the ordinary reviewed baseline.
5. These recording artifacts remain evidence-only; they do not become the breakglass authority object, which remains the grant/receipt lane.

## Consequences

- Emergency shell/console work no longer leaves the highest-risk first prompt outside the reviewed evidence boundary.
- Support/export tooling can find the exact stronger terminal artifacts from the emergency receipt without reopening bundle-membership or host-local spool folklore.
- Non-interactive breakglass actions remain allowed to omit tty-recording joins; this ADR only closes the ambiguity for interactive shell/console sessions that already use the stronger lane.

## Follow-on work

- Exact recovery-console UX and adapter coverage (serial/BMC/virtual media) remain implementation work.
- Retention/redaction/export budgets for the stronger artifacts remain controlled by the already-decided product-shaped evidence/export posture.
