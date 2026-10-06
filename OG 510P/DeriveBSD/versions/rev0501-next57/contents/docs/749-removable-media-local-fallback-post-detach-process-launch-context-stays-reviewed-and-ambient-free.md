# Removable-media local fallback post-detach process launch context stays reviewed and ambient-free

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt

The removable-media local fallback has now narrowed from “host local convenience” into a small first coding lane: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite filesystem-family admission, inert mounted tree, physical root-pinned walk, one selected regular-file subject, capture-first into `/work`, verified capture committed into authoritative quarantine store before detach, later work restarted in a fresh worker with `/ingest` absent, one digest-bound launcher-preopened read-only preserved subject, one broker-collected declared derivative sink, capability mode before later tool mainline, and a closed-world reviewed descriptor set with launcher-owned stdio.

This page closes the next startup-context seam:

> **the later worker must not get hidden authority from inherited parent environment, media-derived argv, or inherited cwd after the descriptor set has already been reviewed.**

See also:
- ADR: `adrs/ADR-0338-removable-media-local-fallback-post-detach-process-launch-context-stays-reviewed-and-ambient-free.md`
- previous cut: `docs/747-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md`
- launcher/preopen posture: `docs/294-oblivious-sandboxing-launchers.md`
- compiled capability map: `spec/preopen.map.schema.json`

## Why this needs a hard decision

Closing descriptors is necessary but not sufficient.
A process also starts with:

- an environment,
- an argument vector,
- and a current working directory.

Those values can look like boring process mechanics while still carrying authority or policy.
A parent environment can smuggle plugin paths, loader controls, helper search paths, proxy settings, debug hooks, temp/home locations, locale-module discovery, or app-specific import behavior.
An argument vector can accidentally turn a hostile filename into an option or policy switch.
A cwd can make relative opens land in `/ingest`, the authoritative store, or the launcher workspace even though the descriptor set looked small.

For the first lane, the smaller honest rule is:
**review the process launch context the same way we review the descriptor set.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) Environment is reviewed-minimal and never inherited wholesale

The later worker starts with `reviewed-minimal-env-no-inherited-parent-env`.
The launcher constructs a small allowlist for values needed by the wrapper contract.
The parent process environment is not copied through as convenience state.

The canonical first-lane allowlist is intentionally tiny and operational:

- `LANG`
- `LC_ALL`
- `TZ`
- `DERIVE_INPUT_FD`
- `DERIVE_OUTPUT_FD`
- `DERIVE_PREOPEN_MAP_DIGEST`

A tool that needs broader environment semantics is not baseline first-lane material until a later explicit wrapper/broker contract admits and receipts that need.

### 2) Argv is launcher-reviewed and not media-derived

The later worker starts with `launcher-reviewed-argv-no-media-derived-args`.
The executable arguments come from a fixed reviewed template or equivalent compiled launch contract.
The preserved selected subject is delivered by descriptor/handle, not by passing the original media path or untrusted filename as a positional argument.

The canonical template is shaped like:

```text
sanitize-pdf --input-fd preserved_subject_ro --output-fd sanitized_derivative_sink --no-network --no-plugin-discovery
```

The exact tool can vary by wrapper lane, but the posture cannot: media names stay evidence, not executable argument authority.

### 3) Cwd is launcher-owned empty scratch

The later worker starts with `launcher-owned-empty-workdir-no-ingest-store-cwd`.
The cwd is a launcher-prepared empty work directory such as `/work`.
It is not `/ingest`, not the authoritative quarantine store, and not whatever cwd the launcher inherited from its parent.

If a tool performs relative opens, those opens are compatibility behavior inside the launcher-owned scratch area.
They are not a second path to the preserved subject, the old mount, or the store.

### 4) Receipts and preopen maps expose the whole launch shape

The canonical examples now carry the same posture in the attach grant, detach receipt, import plan, import receipt, and preopen map.
The preopen map also carries:

- `environment_posture`
- `environment_allowlist`
- `argv_posture`
- `argv_template`
- `cwd_posture`
- `cwd`

That keeps reviewers from having to infer startup context from launcher folklore.

## Canonical first-cut example stack

The reviewed-process-launch-context cut is now explicit in:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`
- `spec/examples/preopen.map.removable-media-local-ingest-post-detach.json`

Together they now say:

- the descriptor set stays closed-world and reviewed-only,
- parent-session stdio stays out,
- parent environment is not inherited,
- media-derived argv is not admitted,
- cwd is launcher-owned empty scratch,
- and the preopen map records the launch-context posture beside the descriptor posture.

## Why this cut is worth making now

Without this decision, the first removable-media fallback could still be undermined by ordinary process-start convenience:

- `LD_*`, plugin, helper, or application-specific discovery variables could change what code or configuration a sanitizer loads,
- a hostile filename could become an option-like argument,
- cwd-relative behavior could reopen `/ingest` or a store/workspace path,
- and receipts would still claim a tiny reviewed preopen set while the real launch context carried more authority.

This page keeps the coding target honest: reviewed descriptors, reviewed stdio, reviewed environment, reviewed argv, and reviewed cwd.

## What remains open

Still intentionally open:

- the exact launcher API used to construct the reviewed environment and argv,
- whether later tool-specific wrappers should admit richer environment or argv templates,
- how much cwd scratch structure a later sanitizer family should receive,
- and whether profile C compatibility should grow a stronger explicit wrapper lane for legacy tools that cannot operate on descriptor-first inputs.

Last updated: 2026-05-18r494
