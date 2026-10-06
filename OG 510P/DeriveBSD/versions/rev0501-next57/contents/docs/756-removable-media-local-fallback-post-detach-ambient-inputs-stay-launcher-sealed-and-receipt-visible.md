# Removable-media local fallback post-detach ambient inputs stay launcher-sealed and receipt-visible

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt

The removable-media local fallback has narrowed into a first coding lane: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite filesystem-family admission, inert mounted tree, physical root-pinned walk, one selected regular-file subject, capture-first into `/work`, verified capture committed into authoritative quarantine store before detach, later work restarted in a fresh worker with `/ingest` absent, one digest-bound launcher-preopened read-only preserved subject, one broker-collected declared derivative sink, capability mode before later tool mainline, closed-world reviewed descriptors, launcher-owned stdio, reviewed environment/argv/cwd, launcher-pinned executable identity, launcher-pinned runtime dependency closure, launcher-fixed unprivileged credentials, launcher-supervised daemon-free lifecycle, a launcher-enforced resource envelope, and a launcher-isolated peer-interaction envelope.

This page closes the next ambient-input seam:

> **the later worker must not let wall-clock time, timezone, host entropy, random seeds, hostname, kernel/sysctl facts, locale, or machine identity become unrecorded derivative inputs.**

See also:
- ADR: `adrs/ADR-0345-removable-media-local-fallback-post-detach-ambient-inputs-stay-launcher-sealed-and-receipt-visible.md`
- previous cut: `docs/755-removable-media-local-fallback-post-detach-peer-interaction-stays-launcher-isolated-and-ambient-ipc-free.md`
- launcher/preopen posture: `docs/741-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md`
- resource envelope cut: `docs/754-removable-media-local-fallback-post-detach-resource-envelope-stays-launcher-enforced-and-receipt-visible.md`

## Decision

For the first host-local removable-media fallback lane, post-detach later workers now use:

- `launcher-sealed-ambient-input-envelope-no-worker-clock-random-or-host-identity`
- `receipt-records-ambient-input-envelope-and-launcher-owned-timestamps`
- `worker-wall-clock-and-timezone-not-derivative-authority`
- `no-worker-randomness-or-host-entropy-as-derivative-input`
- `hostname-kernel-sysctl-locale-and-machine-identity-not-derivative-authority`

These strings do not require one specific kernel mechanism. They require that ordinary derivative bytes are produced under a reviewed ambient-input contract and that receipts show the contract instead of relying on host folklore.

## Boundary rules

### 1) The launcher seals ambient inputs

The later worker records `launcher-sealed-ambient-input-envelope-no-worker-clock-random-or-host-identity`.
The preserved subject, reviewed argv, reviewed minimal environment, pinned executable/runtime closure, preopened descriptors, and declared output slot are the ordinary derivative inputs. Host clock reads, random devices, hostname, kernel/sysctl views, locale databases, timezone files, machine-id state, and other host-observation surfaces are not admitted as hidden inputs.

A backend may implement this through capability-mode wrappers, syscall filtering, deterministic library shims, sealed virtual files, empty locale/timezone views, or explicit launcher-supplied constants. The portable contract is that those observations are reviewed and receipt-visible rather than worker-discovered.

### 2) Time belongs to the launcher receipt path

The later worker records `worker-wall-clock-and-timezone-not-derivative-authority`.
Launcher timestamps, monotonic timeout observation, and receipt creation times remain launcher/broker evidence. The worker's derivative bytes do not depend on ambient wall-clock time, local timezone, calendar locale, or host clock drift.

If a future compatibility lane needs to preserve timestamps inside a derived report, that lane must declare the time source and receipt it. The first lane does not let `time(2)`, `clock_gettime(2)`, `/etc/localtime`, or locale-derived calendar formatting quietly change the derivative.

### 3) Randomness and host entropy stay out

The later worker records `no-worker-randomness-or-host-entropy-as-derivative-input`.
The first lane does not use worker-read randomness, host entropy devices, per-run seeds, ASLR-visible randomness, temporary-name races, or randomized output ordering as derivative input authority. If a tool requires a seed, the launcher supplies a reviewed deterministic seed or the tool belongs in a later explicit compatibility lane.

### 4) Host identity is not derivative input authority

The later worker records `hostname-kernel-sysctl-locale-and-machine-identity-not-derivative-authority`.
Hostname, domain name, jail/host IDs, kernel release, sysctl inventory, CPU model, machine-id files, locale catalogs, timezone state, and host package metadata do not influence ordinary derivative output unless a later lane admits and receipts them.

This keeps the post-detach worker from becoming a host profiler that happens to read one preserved subject.

### 5) Receipts expose the posture

The later worker records `receipt-records-ambient-input-envelope-and-launcher-owned-timestamps`.
Canonical examples carry ambient-input posture through:

- `post_detach_ambient_input_posture`
- `post_detach_ambient_input_receipt_posture`
- `post_detach_clock_posture`
- `post_detach_randomness_posture`
- `post_detach_host_identity_posture`

The preopen map carries the launcher-facing equivalents:

- `ambient_input_posture`
- `ambient_input_receipt_posture`
- `clock_posture`
- `randomness_posture`
- `host_identity_posture`

Together with descriptors, launch context, executable and runtime closure identity, credentials, lifecycle, resources, and peer interaction, these fields make the worker's nondeterminism boundary reviewable without reading host-local default clock, random, locale, or sysctl behavior.

## Canonical first-cut example stack

The ambient-input cut is now explicit in:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`
- `spec/examples/preopen.map.removable-media-local-ingest-post-detach.json`

Together they now say:

- worker wall-clock and timezone reads are not derivative authority,
- worker randomness and host entropy are not derivative input authority,
- hostname, kernel/sysctl, locale, and machine identity do not shape ordinary output,
- launcher timestamps and resource timing remain receipt evidence,
- and any compatibility lane that needs these inputs must declare and receipt them explicitly.

## Why this cut is worth making now

Without this decision, the archive could produce receipts that look complete but still hide nondeterministic host inputs:

- identical preserved subjects could produce different derivatives based on current time or timezone,
- host entropy or randomized iteration could make outputs non-replayable,
- hostname/kernel/sysctl facts could leak into metadata or reports,
- locale or timezone databases could silently change parser/formatter behavior,
- and launcher-owned receipt timestamps could be confused with worker-owned input authority.

This cut keeps the first lane boring: one preserved subject, one declared bounded derivative slot, one launcher-owned evidence path, no unrecorded ambient host observations.

## Compatibility impact

Some tools genuinely need timestamps, random seeds, locale-aware formatting, kernel/CPU feature discovery, or host inventory. Those tools are not rejected forever; they require a future explicit compatibility lane that:

- declares the ambient input surface,
- binds it to a reviewed wrapper/broker contract,
- records the time/random/host-identity posture in receipts,
- preserves one-subject and derivative-egress invariants unless separately reviewed.

The current first lane remains launcher-sealed and receipt-visible.

Last updated: 2026-05-18r502
