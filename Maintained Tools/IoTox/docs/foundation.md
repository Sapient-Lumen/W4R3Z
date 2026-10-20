# Repository foundation

This repository was founded on 2026-08-14 from two owner-supplied revision cubes.

## Adopted product baseline

The repository root is IoTox 0.15.0 rev0015, “Ordinary Request.” Its original cube moved product
source out of the hidden `.datacube/` packaging layer into an ordinary development repository.
`BOOTSTRAPROSE.md` is retained as governing design provenance, but it is no longer the only visible
root object.

Source archive:

```text
DR0Pbox/IoTox-rev0015-2026.08.14.18.17-ordinary-root-request-exact-address-just-werx.zip
```

## Preserved sync line

`components/toxsync/` is toxsync 0.7.0 from nested commit
`f25989b25c8c7851ff59e1b19069adba1083f539`, tag `v0.7.0-rev0010`. The component is imported as
ordinary tracked files; its original nested `.git` directory is deliberately not embedded.

Source archive:

```text
DR0Pbox/IoToxsync-rev0010-2026.08.14.18.18-cpp20-durable-head-subscriber-autonomous-closure-foundry.zip
```

That cube combined toxsync with IoTox 0.12.0 rev0012. The official root instead uses IoTox
rev0015, so toxsync was initially preserved and buildable but not linked into the default product.
That founding constraint is historical: the current tree has deliberately forward-ported a reviewed
subset of its hash/index/planner/apply, treepack, content-store/paged-fabric, multisource, and
range-source primitives directly into `iotox_core`. IoTox owns the production signed HEAD,
authority, transport, attempts, retention, and activation policy; the component's standalone signer,
wire, publication convenience layer, pin journal, and CLI are not a second product trust root.

On 2026-08-20 the preserved engine was independently rebuilt on the founding bare-metal host. On
2026-09-01 a new deep audit expanded it to 125 native checks plus version and backend-aware CLI
transaction routes, requalified compiler/sanitizer/portable/package/fuzz/static-analysis lanes, and
closed scheduler accounting, retained-publication retry, key no-clobber, and fixture-truth seams.
`components/toxsync/flake.lock` pins the standalone environment. This validates the transport-neutral
component independently; current IoTox network integration is qualified by IoTox-owned tests and
Sandwurm evidence, not by importing the historical daemon embedding.

## Current public and host-management bridge

The repository now keeps a publishable human entrance in `docs/product-page.md` and a script-boundary
plan in `docs/script-distribution-plan.md`. `tools/iotox-repo.sh` is the first portable Bash/Nix
repository companion for doctor, build, focused/full test, release-plan/release-check, datacube, and
dry-run cleanup flows. It is
not the product binary and creates no device authority.

`tools/iotox-monsternix-adapter.sh` is an inert IoTox-side MonsterNix porch. It currently inspects and
prints the intended plan only. Future MonsterNix integration should admit exact IoTox source,
package, and proof objects into MonsterNix, then let MonsterNix own host-specific projection,
service-manager wiring, proof receipts, and apply/switch authority. It must not import IoTox
RecallRoot material, mutate ledgers, create sync namespaces, enable sudo profiles, or turn same-host
evidence into a backup-independence claim.

## Deliberately excluded

Retained host binaries, generated artifact bundles, build trees, nested Git administrative data,
and duplicate rev0012 product source were not imported. The original archives remain in the local
`DR0Pbox/` handoff area and are ignored by Git.
