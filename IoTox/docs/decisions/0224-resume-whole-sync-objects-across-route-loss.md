# ADR 0224: Resume whole synchronization objects across route loss

Status: accepted deterministic Agent plus direct-UDP/forced-TCP/actual-Tor-loss Sandwurm gates,
2026-08-28.

## Context

ADR 0223 added a transport receiver that can borrow and preserve an exact private prefix, but the
sync coordinator still received fresh objects through disposable hidden temporaries and discarded
all staging when a route was fenced. A useful latency result requires the complete product path:
named staging from byte zero, old-attempt fencing, fresh carrier identities, exact seek, durable
attempt truth, stale-terminal rejection, and full-digest commit.

This is only valid for whole immutable objects. Range bundles are attempt-specific optimization
artifacts and remain restart-from-zero. Fail-closed pulls must not retain bytes for an unauthorized
replacement.

## Decision

- A whole-object sync receive now creates its exact attempt staging path as an empty, fsynced,
  owner-owned, single-link mode-0600 file. The upper-protocol receive entrance accepts offset zero
  without calling Tox seek; ordinary local file receives retain hidden no-clobber publication.
- On loss of an auxiliary carrier, an `available` pull fences the old scheduler attempt and releases
  its route/staging reservations while retaining the strict incomplete staging inode and signed old
  attempt record. `fail-closed`, cancellation, ordinary terminal failure, range mode, and explicit
  close continue to discard staging.
- Reassignment still allocates a fresh scheduler attempt, message ID, FileId, and exact authenticated
  carrier. When its offer arrives, the coordinator finishes the old signed attempt record, atomically
  moves the partial to the fresh derived attempt path with Linux `RENAME_NOREPLACE`, signs the fresh
  durable attempt, and calls c-toxcore seek at the retained size before resume.
- A replacement may consume only the exact retained object and byte count. Conflicting destination,
  shape, identity, size, route, file number, or accepted position fails closed.
- Completion still hashes the entire staged object and compares its immutable identity before object
  commit. Accepted HEAD and activation rules are unchanged. A stale terminal from the fenced route is
  counted and cannot affect the replacement.
- Zero-byte attempt files are fenced normally; only a positive prefix is retained across carriers.
  `sync-status` exposes the live `retained-partials` gauge plus saturating lifetime
  `retained-attempts`, `retained-bytes`, `retention-fallbacks`, `resumed-attempts`, and
  `resumed-bytes` counters.
- Startup recovery remains restart-from-zero, not restart-resume. To close the short journal/path
  handoff crash window, the signed burned-attempt high-water and active set now authorize bounded
  cleanup of only strict canonical inactive attempt paths under the namespace transaction. An
  unburned canonical path fails startup rather than being removed.

The deterministic coordinator gate retains `pay`, moves it from attempt 1/route A to attempt 2/route
B, seeks at byte 3, receives only `load`, rejects the stale route-A completion, verifies `payload`,
commits once, and rotates signed active truth from attempt 1 to 2 to empty. The full mock Agent gate
delivers three real file bytes through the first worker, emits authoritative offline after that
callback, resumes through the second authenticated worker, and reports one resumed attempt and three
resumed bytes. Its fail-closed twin reports zero retained/resumed state and zero reassignment.

## Consequences

Late auxiliary-route loss no longer necessarily pays a full-object retransmission penalty. The
optimization does not weaken freshness or authority: route loss still creates a fresh attempt and
FileId, and unauthenticated prefix content can only cause a final digest failure.

No peer or sync wire bytes change. This is same-process cross-carrier resume with crash-safe cleanup,
not cross-process continuation. Genuine direct UDP and forced TCP now pass with two simultaneous
positive object prefixes: retained and resumed attempts match two-to-two, retained and resumed bytes
match exactly at 315,330 and 252,264 respectively, and both cells return the live gauge and fallback
counter to zero before full convergence. Exact proof bindings and nonclaims live in
`../evidence/2026-08-28-sandwurm-sync-byte-resume.md`.

An independently supervised actual-Tor cell also passes after the host kills the client Tor process
at 75,405 artifact bytes. Two prefixes totaling 102,825 bytes resume exactly through the native
survivor with zero fallback or IoTox worker restart; the same Tor member then recovers. Exact process,
circuit, containment, and transfer bindings live in
`../evidence/2026-08-28-sandwurm-actual-tor-sync-byte-resume.md`.

I2P chunk/range or byte-resume and Tor-to-Tor qualification remain open, as do repeated loss,
very-late loss, attributable
resource measurement, and restart resume. The accepted result is a bounded construction-host latency
optimization, not a universal network claim or permission to cross privacy classes.
