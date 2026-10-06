# RFC-0155: Replay capsules in the ops spine (debug events + record-on-failure)

Status: **draft**

## Motivation

DeriveBSD already treats record/replay debugging as an **artifact** gated by explicit authority (`debug.record.grant` → `debug.replay.capsule`).

What’s missing is the *ops wiring*:

- how to trigger capture automatically on failures (without ambient debug authority)
- how to correlate capture with rollouts, incidents, and other evidence
- how to surface capture as structured events instead of strings

## Goals

- Add a **typed debug event** (`debug-event`) for the structured event journal.
- Allow `change-set` steps to declare **record-on-failure hooks**.
- Make incident bundles able to **reference replay capsules explicitly**.
- Keep privacy posture strict (redaction receipts, export gates).

## Non-goals

- Standardizing on a single record/replay backend.
- Capturing full-system “flight recorder” traces by default.
- Making replay artifacts ambiently accessible.

## Proposal

### 1) `debug-event` in the structured journal

Add `spec/debug.event.schema.json` and a sample record.

Event types (v0.1):

- `record-start`
- `record-stop`
- `capsule-emitted`
- `export-requested`
- `export-denied`
- `export-succeeded`
- `export-failed`

The event should carry:

- `grant_digest` (when a grant exists)
- `capsule_digest` (when emitted)
- `target` selectors (service/jail/microVM/pid)
- optional `correlation` (change-level grouping via `event.record` envelope)

### 2) Change sets: step-level record-on-failure hook

Extend `spec/change.set.schema.json` step objects with an optional `debug` stanza:

- `trigger`: `on-failure` | `always`
- `grant_ref`: `{ kind: "debug.record.grant", digest: "..." }`
- optional `notes`

The apply engine behavior:

- On trigger, call the debug broker to start recording **bounded by the grant**.
- When the step completes/fails, stop recording and (if any data) emit a capsule.
- Record capsule digests in the step’s `receipts` list (as `{kind:"debug-replay-capsule", digest:"..."}`) and emit `debug-event`s.

### 3) Incident bundles: explicit replay capsule references

Extend `incident.bundle` to add `includes.replay_capsule_digests`.

Policy decides:

- whether capsules are only referenced, or included in the payload
- whether redaction transforms are required before export

### 4) Privacy and export controls

- Default posture: capsules contain digests and minimal metadata; trace blobs require explicit export.
- If export occurs: bind it to `redaction.transform` + `redaction.receipt` where applicable.
- Cross-domain capture should require leases/consent (portal lane).

## Backwards compatibility

- All additions are optional.
- Existing debug grant/capsule objects remain unchanged.

## References

- rr (record/replay + reverse debugging): https://rr-project.org/
- Pernosco workflow (rr traces processed into a web debugger): https://pernos.co/
- Windows Time Travel Debugging (TTD) overview: https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/time-travel-debugging-overview
- ReproZip documentation (pack execution dependencies): https://docs.reprozip.org/en/latest/
