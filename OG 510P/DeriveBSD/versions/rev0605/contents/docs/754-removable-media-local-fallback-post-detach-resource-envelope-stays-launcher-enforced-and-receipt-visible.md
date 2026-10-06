# Removable-media local fallback post-detach resource envelope stays launcher-enforced and receipt-visible

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt

The removable-media local fallback has narrowed into a first coding lane: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite filesystem-family admission, inert mounted tree, physical root-pinned walk, one selected regular-file subject, capture-first into `/work`, verified capture committed into authoritative quarantine store before detach, later work restarted in a fresh worker with `/ingest` absent, one digest-bound launcher-preopened read-only preserved subject, one broker-collected declared derivative sink, capability mode before later tool mainline, closed-world reviewed descriptors, launcher-owned stdio, reviewed environment/argv/cwd, launcher-pinned executable identity, launcher-pinned runtime dependency closure, launcher-fixed unprivileged credentials, and a launcher-supervised daemon-free worker lifecycle.

This page closes the next resource-authority seam:

> **the later worker must not have unbounded CPU, wall-clock, memory, process, descriptor, scratch, or derivative-output authority.**

See also:
- ADR: `adrs/ADR-0343-removable-media-local-fallback-post-detach-resource-envelope-stays-launcher-enforced-and-receipt-visible.md`
- previous cut: `docs/753-removable-media-local-fallback-post-detach-worker-lifecycle-stays-launcher-supervised-and-daemon-free.md`
- resource governance: `docs/65-resource-governance.md`, `docs/143-resource-controls-rctl-racct-cpuset.md`, `docs/247-resource-budgets-and-limits-as-evidence.md`, `docs/285-hierarchical-resource-limits-compilation.md`
- launcher/preopen posture: `docs/294-oblivious-sandboxing-launchers.md`
- compiled capability map: `spec/preopen.map.schema.json`

## Why this needs a hard decision

The first lane now pins what the worker can see, how it starts, which code it runs, which runtime closure it may use, which credential envelope executes it, and when the process tree must exit.
That still does not say whether the worker gets an unbounded resource budget.

Without this cut, the first lane could still depend on:

- host-local default `rctl`/`rlimit` folklore,
- tool self-limits that parser bugs or helpers bypass,
- unbounded memory or scratch consumption while processing hostile bytes,
- a derivative sink that quietly grows into a disk-pressure or storage-exhaustion channel,
- receipts that record success after a resource-limit hit or timeout left partial output behind.

Those are authority risks, not mere performance tuning.
For the first lane, the boring rule is: **the launcher enforces a reviewed resource envelope and the receipt records both the envelope and observed usage.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) Resource envelope is launcher-enforced

The later worker records `launcher-enforced-resource-envelope-no-unbounded-worker-consumption`.
The launcher fixes the envelope before tool mainline begins. The canonical first-cut envelope includes:

- CPU time,
- wall-clock time,
- memory bytes,
- open-file count,
- process count,
- scratch bytes,
- declared derivative-output bytes.

Backend choice is implementation detail. On FreeBSD, likely pieces include `rctl`/`racct`, `rlimit`, jail-level limits, cpuset, and wrapper timers. The portable contract is the reviewed envelope, not a particular shell command.

### 2) Derivative output size is bounded before receipt authority

The later worker records `declared-derivative-output-size-bound-before-receipt`.
The single declared derivative sink stays a bounded egress slot, not unbounded scratch or an infinite output stream.
The launcher/broker must enforce the declared derivative-output byte limit before the receipt names an authoritative derivative locator.

### 3) Limit hits fail closed

The later worker records `resource-limit-hit-fails-closed-no-derivative-authority`.
If CPU, wall-clock, memory, process, descriptor, scratch, or derivative-output bounds are exceeded, partial output does not become authoritative derivative evidence.
The receipt may record a denial or failure, but it must not mint a successful sanitized derivative from a resource-limit-hit run.

### 4) Receipts expose limits and observed usage

The later worker records `receipt-records-resource-envelope-and-observed-usage`.
Canonical successful receipts carry both:

- `post_detach_resource_limits`
- `post_detach_observed_resource_usage`

The attach grant carries:

- `post_detach_resource_envelope_posture`
- `post_detach_resource_receipt_posture`
- `post_detach_resource_failure_posture`
- `post_detach_output_bound_posture`
- `post_detach_resource_envelope_required`

The preopen map carries the same launcher-focused posture under:

- `resource_envelope_posture`
- `resource_receipt_posture`
- `resource_failure_posture`
- `output_bound_posture`
- `resource_limits`

Together with the descriptor set, launch context, executable digest, wrapper digest, runtime dependency closure digest, credential envelope, and lifecycle posture, these fields make bounded post-detach execution reviewable without consulting service-default folklore.

## Canonical first-cut example stack

The resource-envelope cut is now explicit in:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`
- `spec/examples/preopen.map.removable-media-local-ingest-post-detach.json`

Together they now say:

- the worker tree is bounded before later tool mainline starts,
- CPU/wall-clock/memory/open-file/process/scratch/output limits are reviewed state,
- observed usage is receipt-visible on success,
- derivative output cannot outgrow its declared slot before receipt authority,
- resource-limit hits fail closed with no authoritative derivative,
- and larger compatibility envelopes need explicit review rather than hidden launcher defaults.

## Why this cut is worth making now

Without this decision, the archive could produce receipts that look complete but still hide resource exhaustion:

- a malformed file could consume unbounded memory before parser failure,
- a sanitizer could fill the declared sink until disk pressure affects unrelated work,
- a tool bug could spawn within the allowed lifecycle but consume too many process or file-table slots,
- a timeout or kill could leave partial bytes that later tooling mistakes for sanitized output,
- and support would have to infer real limits from host-local service configuration instead of typed evidence.

This cut keeps the first lane boring: one worker, one preserved subject, one declared bounded derivative slot, one receipt with limits and usage.

## Compatibility impact

Some tools need larger memory, longer wall-clock budgets, or larger outputs for specific formats.
Those tools are not rejected forever; they simply require an explicit reviewed envelope or later compatibility lane that:

- declares the larger resource budget,
- keeps output bounds explicit,
- records observed usage,
- and preserves fail-closed behavior on limit hits.

The current first lane remains small, launcher-enforced, and receipt-visible.

Last updated: 2026-05-18r499
