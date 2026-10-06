# Breakglass interactive sessions carry tty-recording proof and start at session open

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

Breakglass already had the hard product-shaped evidence decision: output-only TTY/console recording is the routine stronger lane for interactive emergency shell/recovery-console work where the profile defaults call for it.

What stayed open was the cheaper-looking but implementation-blocking question: does that stronger evidence start **before** the first prompt, or can the reviewed story quietly tolerate “we started recording after we were already in the rescue shell”? And once the recording exists, where is the exact join from emergency authority to the stronger evidence artifact?

This doc closes that gap.

## Accepted boundary

For the first reviewed interactive breakglass shell/console lane:

- `breakglass.receipt.evidence.tty_recording_digests` is the canonical exact join to `tty.session.recording` artifacts emitted for the same emergency session.
- `breakglass.receipt.evidence.tty_recording_start_posture` is fixed to `session-open-before-first-prompt` when those artifacts are present.
- reviewed interactive breakglass recording therefore starts when the shell/console session opens, before the first prompt appears.
- “enter rescue shell first and manually start recording later” is not part of the ordinary reviewed baseline.
- the recording remains evidence-only; the authority object stays `breakglass.grant` / `breakglass.receipt`.

## Why this matters

Without this cut, the archive still allows a quiet loophole:

- the strongest early commands happen before the recording starts, and
- support/export tooling can prove breakglass happened without being able to prove which exact shell/console evidence artifact belongs to it.

That is exactly how emergency lanes drift back into rescue-shell folklore even after the archive has already paid to make breakglass explicit and receipted.

## What this does **not** do

This doc does not claim every breakglass action is interactive or every breakglass receipt must carry tty recordings.

- Non-interactive breakglass operations may omit tty recording evidence.
- Adapter coverage for BMC, serial concentrators, or virtual media is still implementation work.
- Retention/redaction/export budgets stay governed by the already-decided evidence/export posture docs.

## Wiring surfaces

- ADR: `adrs/ADR-0294-breakglass-interactive-sessions-carry-tty-recording-proof-and-start-at-session-open.md`
- breakglass lane: `docs/236-breakglass-and-recovery-mode.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- breakglass recording posture: `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md`
- terminal recording artifact: `docs/292-terminal-session-recording-as-evidence.md`
- schema: `spec/breakglass.receipt.schema.json`
- examples: `spec/examples/breakglass.receipt.json`, `spec/examples/tty.session.recording.json`

Last updated: 2026-03-23r435
