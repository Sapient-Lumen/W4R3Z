# Terminal session recording as evidence (tlog-shaped I/O logs, least authority)

Terminal sessions are the sharpest knife in most systems.
Session recording is valuable for incident response, change accountability, and debugging —
but if it becomes ambient surveillance, it destroys trust and invites bypass.

DeriveBSD should support terminal session recording as a **leased authority lane**:
explicit, bounded, revocable, and privacy-aware by construction.

## Goals

- Enable **opt-in**, policy-governed TTY recording for specific sessions, users, or services.
- Default to **output-only** capture; input capture is a separate, higher-risk scope.
- Produce a replayable, portable artifact with typed metadata.
- Make recordings compatible with deterministic redaction and export portals.

## Lessons to steal

- tlog-style recording: insert a recorder between the terminal and the shell and log I/O as structured events (JSON message stream).
- Enterprise posture: input recording is often disabled by default; enable it only when explicitly required.

## Model

### 1) A broker owns the recording primitive

A host daemon (`derive-ttyrecd`) owns privileged recording:

- starts/stops recording for a target (login session, SSH session, jail, microVM console)
- enforces **budgets** (duration/bytes) and scope (output-only vs in+out)
- registers the lease for revocation (`docs/249-lease-registry-and-cross-lane-revocation.md`)
- emits a typed recording evidence object at close

### 2) Storage format (chunked, replayable, hashable)

Recordings should be stored as chunked event logs:

- `jsonl` (one event per line) is a pragmatic default
- chunks are content-addressed; a manifest ties them together
- optional hash-chaining for tamper-evidence
- optional encryption at rest (especially if input capture is enabled)

### 3) Sharing and privacy

- Apply deterministic redaction transforms when exporting (`docs/195-deterministic-redaction-transforms.md`)
- Use the export portal to share recordings (`docs/251-export-policies-and-support-bundle-portal.md`)
- For remote support, treat TTY recording as an optional attachment to `support.session`
  (`docs/291-remote-assistance-sessions-as-evidence.md`)

## Evidence

- `tty.session.recording`: typed metadata for a recording (mode, subject, bounds, chunk digests)

See: `spec/tty.session.recording.schema.json`, `spec/examples/tty.session.recording.json`.

## Non-goals

- Always-on recording of all terminals.
- “Secret logging” without consent receipts or policy authorization.

Last updated: 2026-02-25
