# Removable-media local fallback post-detach executable identity stays launcher-pinned and path-search-free

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt

The removable-media local fallback has narrowed into a first coding lane: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite filesystem-family admission, inert mounted tree, physical root-pinned walk, one selected regular-file subject, capture-first into `/work`, verified capture committed into authoritative quarantine store before detach, later work restarted in a fresh worker with `/ingest` absent, one digest-bound launcher-preopened read-only preserved subject, one broker-collected declared derivative sink, capability mode before later tool mainline, closed-world reviewed descriptors, launcher-owned stdio, and reviewed environment/argv/cwd.

This page closes the next executable-identity seam:

> **the later worker must not choose its executable through `PATH`, cwd, mutable package state, media-derived names, or implicit helper/plugin discovery after all the surrounding launch context has been reviewed.**

See also:
- ADR: `adrs/ADR-0339-removable-media-local-fallback-post-detach-executable-identity-stays-launcher-pinned-and-path-search-free.md`
- previous cut: `docs/749-removable-media-local-fallback-post-detach-process-launch-context-stays-reviewed-and-ambient-free.md`
- launcher/preopen posture: `docs/294-oblivious-sandboxing-launchers.md`
- capability-mode handoff: `docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md`
- compiled capability map: `spec/preopen.map.schema.json`

## Why this needs a hard decision

After the descriptor set, stdio, environment, argv, and cwd are reviewed, the process image itself can still be a hidden resolver.
A template like `sanitize-pdf --input-fd ...` is not enough if `sanitize-pdf` is resolved through `PATH`, the launcher's cwd, the host's current package view, or a plugin/helper search surface.
That would let the archive claim a reviewed first lane while the actual code identity remains whatever the current host happens to find.

For this first lane, the honest rule is:
**the launcher resolves and pins the executable identity before handoff, and the receipt stack records the exact executable and wrapper contract digests.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) Executable resolution is launcher-owned and digest-pinned

The later worker starts with `launcher-resolved-executable-digest-no-path-search`.
The launcher resolves the executable from reviewed policy or a trusted store locator before spawning the worker.
The worker never performs `PATH` search, cwd-relative executable lookup, or media-derived executable selection.

The canonical first-lane executable locator is shaped like:

```text
store:sha256:abababababababababababababababababababababababababababababababab/bin/sanitize-pdf
```

The locator is convenience and replay support; the digest is the authority-bearing identity.

### 2) The wrapper contract digest is receipt-visible

The receipt stack carries `receipt-records-executable-and-wrapper-digests`.
The wrapper contract digest binds the exact tool identity to the reviewed argv template, environment allowlist, cwd, descriptor posture, stdio posture, and helper-discovery posture.

That means a reviewer does not have to infer the real wrapper from a friendly tool name or a package currently installed on the host.

### 3) Helper and plugin discovery stay out unless explicitly wrapped

The first lane records `no-implicit-helper-or-plugin-discovery`.
A sanitizer family that needs plugin/module/helper discovery is not baseline first-lane material until a later wrapper/broker contract declares those helper surfaces, preopens or brokers them explicitly, and records them in receipts.

The canonical template may still include `--no-plugin-discovery`, but this page makes the posture portable: the receipt says discovery was out of lane even if a particular tool uses different flags.

### 4) Plans, receipts, and preopen maps expose the executable identity

The canonical examples now carry:

- `post_detach_executable_posture`
- `post_detach_executable_locator`
- `post_detach_executable_digest`
- `post_detach_wrapper_contract_digest`
- `post_detach_helper_discovery_posture`

The preopen map carries the same posture under launcher-focused names:

- `executable_posture`
- `executable_locator`
- `executable_digest`
- `wrapper_contract_digest`
- `helper_discovery_posture`

## Canonical first-cut example stack

The executable-identity cut is now explicit in:

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
- executable selection is launcher-owned and digest-pinned,
- wrapper contract identity is receipt-visible,
- and implicit helper/plugin discovery is out of lane.

## Why this cut is worth making now

Without this decision, the first removable-media fallback could still be undermined by ordinary executable lookup:

- a hostile or stale `PATH` entry could change the sanitizer binary,
- cwd-relative executable lookup could turn launcher filesystem state into authority,
- package upgrades could make old receipts impossible to interpret precisely,
- helper/plugin discovery could load unreviewed code beside a reviewed preopen set,
- and support would have to reconstruct historical code identity from host-local folklore.

This page keeps the coding target honest: reviewed descriptors, reviewed launch context, and reviewed executable identity.

## What remains open

Still intentionally open:

- the exact store/locator syntax used by the production launcher,
- whether executable identity should be joined to a stronger runtime verified-execution receipt in later profiles,
- how to admit legacy tools with helper discovery through an explicit wrapper/broker contract,
- and whether profile C compatibility should grow a richer tool-family registry for sanitizer wrappers.

Last updated: 2026-05-18r495
