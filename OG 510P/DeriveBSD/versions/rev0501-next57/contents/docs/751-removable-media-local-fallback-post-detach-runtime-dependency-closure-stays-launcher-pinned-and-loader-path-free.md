# Removable-media local fallback post-detach runtime dependency closure stays launcher-pinned and loader-path-free

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt

The removable-media local fallback has narrowed into a first coding lane: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite filesystem-family admission, inert mounted tree, physical root-pinned walk, one selected regular-file subject, capture-first into `/work`, verified capture committed into authoritative quarantine store before detach, later work restarted in a fresh worker with `/ingest` absent, one digest-bound launcher-preopened read-only preserved subject, one broker-collected declared derivative sink, capability mode before later tool mainline, closed-world reviewed descriptors, launcher-owned stdio, reviewed environment/argv/cwd, and launcher-pinned executable identity.

This page closes the next runtime-code seam:

> **a digest-pinned executable is not the whole code identity if the dynamic loader, shared libraries, interpreter, engines, or ordinary runtime helper code can still be selected through ambient host or media-derived lookup.**

See also:
- ADR: `adrs/ADR-0340-removable-media-local-fallback-post-detach-runtime-dependency-closure-stays-launcher-pinned-and-loader-path-free.md`
- previous cut: `docs/750-removable-media-local-fallback-post-detach-executable-identity-stays-launcher-pinned-and-path-search-free.md`
- dynamic-linking background: `docs/180-capability-mode-dynamic-linking.md`
- execution-integrity boundary: `docs/486-exec-integrity-authority-and-verified-execution-boundary.md`
- compiled capability map: `spec/preopen.map.schema.json`

## Why this needs a hard decision

`launcher-resolved-executable-digest-no-path-search` prevents the worker from choosing a different entrypoint through `PATH`, cwd, mutable package state, or media-derived executable names.
It does not by itself prevent a dynamically linked tool from loading different runtime code.

Without this cut, the first lane could still depend on:

- `LD_LIBRARY_PATH` or similar loader-affecting environment variables,
- cwd-relative library or interpreter lookup,
- `/ingest` or media-derived paths as library/helper search inputs,
- host-global loader hints or package-manager current state,
- late `dlopen` of engines, NSS modules, fonts, codecs, converters, or helpers.

That is executable authority under another name.
For the first lane, the honest rule is: **the launcher pins the runtime dependency closure before handoff, and the receipt stack records that closure.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) Runtime dependency closure is launcher-pinned

The later worker records `launcher-pinned-runtime-dependency-closure-no-ambient-loader-search`.
The launcher selects the runtime dependency closure from reviewed policy or a trusted store locator before spawning the worker.
The closure can be static-linking evidence, a store-managed dynamic closure, or another reviewed wrapper-owned closure; it is not the host's current library view.

The canonical first-lane closure digest is shaped as:

```text
sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd
```

The digest is the authority-bearing identity; any human-friendly library list is commentary.

### 2) Dynamic-loader path inputs are not authority

The later worker records `no-ld-library-path-cwd-or-media-derived-loader-inputs`.
The reviewed environment allowlist does not include `LD_LIBRARY_PATH`, loader-preload variables, plugin paths, or media-derived library selectors.
The worker's cwd remains launcher-owned scratch and cannot become a library-resolution input.

### 3) Late runtime discovery stays out of the first lane

The first lane already carries `no-implicit-helper-or-plugin-discovery`.
This page makes the runtime dependency version of that rule explicit: late `dlopen`, interpreter fallback, engines, modules, codec/font/plugin discovery, and helper process lookup stay out unless a later wrapper/broker contract declares and receipts them.

### 4) Plans, receipts, and preopen maps expose the closure

The canonical examples now carry:

- `post_detach_runtime_dependency_posture`
- `post_detach_runtime_dependency_closure_digest`
- `post_detach_dynamic_loader_posture`

The attach grant also carries:

- `post_detach_runtime_dependency_receipt_posture`
  - canonical value: `receipt-records-runtime-dependency-closure-digest`
- `post_detach_runtime_dependency_closure_digest_required`

The preopen map carries the same posture under launcher-focused names:

- `runtime_dependency_posture`
- `runtime_dependency_closure_digest`
- `dynamic_loader_posture`

Together with the executable and wrapper digests, these fields make the later worker's code identity reviewable without consulting the current host.

## Canonical first-cut example stack

The runtime dependency closure cut is now explicit in:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`
- `spec/examples/preopen.map.removable-media-local-ingest-post-detach.json`

Together they now say:

- executable selection is launcher-owned and digest-pinned,
- wrapper contract identity is receipt-visible,
- runtime dependency closure is launcher-owned and digest-pinned,
- dynamic-loader path inputs are not admitted,
- parent environment and cwd do not become loader authority,
- `/ingest` and media-derived paths cannot select runtime code,
- and late helper/plugin/runtime discovery stays out of lane.

## Why this cut is worth making now

Without this decision, the archive could produce receipts that look precise but still hide mutable runtime code selection:

- a replaced shared library could change sanitizer behavior,
- a loader-path environment variable could select different code while the executable digest stayed constant,
- an interpreter or engine lookup could reintroduce `/ingest` as code authority,
- and support would have to reconstruct the historical runtime closure from host-local package folklore.

This cut keeps the coding target honest: reviewed descriptors, reviewed launch context, reviewed executable identity, and reviewed runtime dependency closure.

## What remains open

Still intentionally open:

- the exact production format for runtime dependency closure manifests,
- whether profile A/D execution integrity should make this closure a hard kernel-enforced verified-execution fact,
- how to admit legacy dynamic tools through an explicit wrapper/broker contract,
- and whether profile C should grow compatibility lanes for larger reviewed closure families.

Last updated: 2026-05-18r496
