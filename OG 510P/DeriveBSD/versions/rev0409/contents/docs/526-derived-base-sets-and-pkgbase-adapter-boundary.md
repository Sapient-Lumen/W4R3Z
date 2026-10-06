# Derived base sets and pkgbase adapter boundary

**Tier:** A (Core contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, supply-chain, operability
**Patterns:** Adapter→Shadow→Replace, Plan→Apply→Receipt

`docs/111-packaged-base-pkgbase.md` captured the useful lesson from FreeBSD’s packaged base work.
This doc makes the hard architectural cut:
**DeriveBSD base identity is native and derivation-first; pkgbase remains an adapter lane.**

See also:
- ADR: `adrs/ADR-0116-derived-base-sets-and-pkgbase-adapter-boundary.md`
- packaged base lessons: `docs/111-packaged-base-pkgbase.md`
- adapter discipline: `docs/402-adapter-lanes-and-strangler-discipline.md`
- patchset manifest: `spec/patchset.manifest.schema.json`
- base-set schema: `spec/base.set.schema.json`

## Why this needs a hard decision

FreeBSD 15.0 made packaged base real enough to copy operationally:
base can now be installed as packages, managed with `pkg(8)`, and built into package repositories from source.
That is strong evidence that “base is explicit artifacts” is the right direction.
But it does **not** answer DeriveBSD’s harder question:
should upstream package metadata become the native contract for deployment, rollback, and explainability? See `docs/32-curated-references.md`.

If the archive answers “yes,” then base quietly becomes a special snowflake lane:

- deployment identity terminates in upstream package names rather than native derived objects,
- A/D offline and regulatory posture inherits external packaging semantics,
- patching / rollback has to translate through adapter folklore,
- and `pkgbase` stops being an adapter and becomes the real product.

That would violate the archive’s main coherence rule: **complexity lives at the edges, not in the center.**

## Accepted boundary

Across all profiles:

- the canonical base artifact is `base.set`,
- host generations and patchsets bind to `base.set` digests,
- pkgbase interop is allowed only as an explicit adapter lane,
- and the native split stays intentionally small in v0.

The canonical v0 base-set classes are:

- `kernel`
- `userland`
- `toolchain`

This is the real decision.
The archive is **not** deciding every future subset up front.
It is deciding that the native review/deploy/rollback surface stays on three small classes until there is strong evidence that more granularity buys leverage rather than entropy.

## Canonical source-of-truth rule

For DeriveBSD-native base delivery:

- `base.set.kind = base.set`
- `base.set.set_class ∈ {kernel, userland, toolchain}`
- `base.set.source_authority.kind = derive.plan` for canonical native production; derive.plan is the only canonical native value
- pkgbase-shaped import/export metadata is optional compatibility data, never the deployment authority object

The adapter case remains legitimate, but subordinate.
When pkgbase is involved, the adapter must still produce a native `base.set` object and a receipt trail explaining how the translation happened.

## Why this is the right coherence cut

This keeps all product shapes viable without forks:

- **A (fleet host):** the trusted base stays digest-bound, promotable, rollbackable, and not hostage to package-manager folklore.
- **B (workstation):** the same native base contract can underlie humane update UX without making the host a compatibility snowflake.
- **C (general OS):** pkgbase and pkg tooling remain useful compatibility bridges, but they do not redefine the center of the system.
- **D (appliance / regulatory):** offline mirror kits, audits, and rebuildability can terminate in native set digests rather than external repository behavior.

It also keeps later implementation pressure honest.
If someone wants ten native base classes, or wants host generations to bind directly to pkgbase package tuples, they now have to justify the entropy cost explicitly.

## Minimal v0 spec worth implementing

The smallest useful native contract is now explicit:

- `spec/base.set.schema.json`
- `spec/examples/base.set.json`

That contract is intentionally narrow.
It says:

- which class this set is,
- which platform it targets,
- which native source authority produced it,
- which build identities it came from,
- and which root tree / file / boot digests make up the set.

That is enough to make patching, rollout review, explainability, and future builder work concrete without prematurely freezing every packaging detail.

## Research note

Upstream FreeBSD is giving two useful signals at once:
packaged base is now a real supported direction, and the base-package repositories can be built from source as explicit artifacts.
DeriveBSD should steal exactly that lesson — **base is explicit and buildable** — while refusing the stronger conclusion that upstream package metadata should become DeriveBSD’s native deployment contract. See `docs/32-curated-references.md`.

Last updated: 2026-03-16r255
