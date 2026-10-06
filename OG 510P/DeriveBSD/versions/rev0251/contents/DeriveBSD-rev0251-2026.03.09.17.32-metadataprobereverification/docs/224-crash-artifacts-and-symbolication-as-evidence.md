# Crash artifacts + symbolication as evidence (savecore / coredump / debuginfod lessons)

Crashes are inevitable.
What’s optional is whether we handle them as:
- **typed, reviewable evidence** (good), or
- an ad-hoc pile of core files, logs, and tribal scripts (bad).

DeriveBSD already has an “ops evidence spine” (events → receipts → bundles).
Crashes should plug into that spine **by default**.

## Prior art worth stealing

- **FreeBSD kernel dumps + `savecore(8)`**: crash dumps are extracted on the next boot before swap mounts; minidumps vs full dumps matter.  
  Reference: https://docs.freebsd.org/en/books/developers-handbook/kerneldebug/
- **Crashpad**: separates *crash capture* from *upload/symbolication*, with stable crash ids and a local DB.  
  Reference: https://chromium.googlesource.com/crashpad/crashpad/+/HEAD/doc/overview_design.md
- **`debuginfod` (elfutils)**: fetch debug info (and sometimes binaries/sources) by **build-id** over HTTP; great “symbol server” ergonomics.  
  Reference: https://sourceware.org/elfutils/Debuginfod.html
- **WER local dump collection**: OS-level, policy-configured post-crash dump capture (no app modifications required).  
  Reference: https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps

## DeriveBSD direction

### 1) A crash report is an evidence object

Emit a `crash-report` for:
- userland crashes (services, tools)
- kernel panics / watchdog resets
- hypervisor / VM runtime crashes

The report is **metadata-first**:
- *what crashed*, *when*, *under which generation*, *under which policy*
- pointers/digests for heavy artifacts (core/minidump/kernel dump), not inline blobs
- correlation ids (change_id / fault_id / event_id)

See: `spec/crash.report.schema.json`.

### 2) Crashes also emit typed events

Write a `crash-event` to the structured event journal so tooling can:
- group by crash signature
- correlate with `svc-event` restarts / `fault-event` diagnoses
- correlate with `change-set` executions (bad rollout == clustered crashes)

See: `spec/crash.event.schema.json`.

### 3) Symbolication is a first-class pipeline (not a manual ritual)

To make crash reports actionable, we need **stable symbol lookup**:
- Derive outputs should embed a **build-id** (or equivalent) that keys debug info.
- Debug symbols should be publishable via a “debug cache” (debuginfod-like) using build-id lookups.
- Symbolication should produce a **receipt** (what sources were used; what was resolved; what failed).

This plays nicely with the store:
- debug info can be a separate output (`.debug`) with its own digest
- caches can distribute debug outputs just like regular artifacts

### 4) Privacy and safety: core dumps are hazardous

Core/kernel dumps can contain:
- secrets
- customer data
- cryptographic material

So:
- `crash-report` must be safe to share by default (metadata-only).
- dumping should be policy-gated (and opt-in for incident bundles).
- redaction transforms should be available for “shareable dump views” (see `docs/195-deterministic-redaction-transforms.md`).

## Wiring into the ops spine

- **Service supervision**: on crash → emit `crash-event` + `crash-report`; optionally capture a minidump/core if policy allows.  
  See: `docs/214-service-supervision-health-as-evidence.md`.
- **Fault management**: crash reports feed diagnosis (e.g., “crash loop” becomes a fault class).  
  See: `docs/213-fault-management-architecture.md`.
- **Incident bundles**: bundles can include crash report digests by default, and dumps only when explicitly enabled.  
  See: `docs/216-incident-snapshots-and-support-bundles.md`, `spec/incident.bundle.schema.json`.
- **Replay capsules**: when a replay grant exists, crashes can trigger “record-on-failure” and attach capsule digests.  
  See: `docs/220-operational-time-travel-debugging.md`.

