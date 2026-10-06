# Preopen map diff as a review surface (Capsicum capability-set drift)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability, reproducibility
**Patterns:** Registry→Diff→Gate, Bundles

DeriveBSD uses Capsicum to shrink ambient authority: pre-open what a service needs, reduce descriptor rights, then enter capability mode (`cap_enter(2)`).

In practice, the hard part is keeping the resulting *handle set* understandable:

> “Between two generations, did this service gain new directory handles, sockets, or broader rights?”

If that question can’t be answered from evidence, teams reintroduce ambient authority “temporarily” and drift becomes folklore.

DeriveBSD treats the *preopened handle set* as a derived artifact (`preopen.map`) and adds a compact posture diff (`preopen.map.diff`) so capability-set drift is **gateable** and **bundle-friendly**.

## The artifacts

### `preopen.map`

A stable-ordered list of preopened handles (labels + targets + Capsicum rights masks) produced by activation planning / launchers.

Schema: `spec/preopen.map.schema.json`
Example: `spec/examples/preopen.map.json`

### `preopen.map.diff`

`preopen.map.diff` compares two `preopen.map` objects (by digest) and emits a high-signal summary:

- entries added / removed
- rights broadened / narrowed
- target changes (path/inet endpoint changes)
- optional `risk_flags` suitable for review UI + policy gates

Schema: `spec/preopen.map.diff.schema.json`
Example: `spec/examples/preopen.map.diff.json`

## Noise rule (keep this surface stable)

This diff is intentionally **not** a raw inventory dump.

- The full handle set belongs in `preopen.map`.
- This diff surface should stay small enough for `drift.bundle` and promotion UI.
- If you need more nuance later, add a new typed artifact (don’t overload this diff with blobs).

## Where it plugs in

### 1) Drift bundles

When a unit’s `preopen.map` digest changes between generations, attach `preopen.map.diff` next to other posture diffs.

See: `docs/395-drift-bundles-and-review-summaries.md` and the canonical registry `docs/430-diff-surface-registry.md`.

### 2) Evidence spine

Least-authority posture should be explainable:

- the `sandbox-profile` (intent vocabulary)
- the derived `preopen.map` (concrete Capsicum grants)
- `preopen.map.diff` when the concrete grants change

See: `docs/229-evidence-spine-overview.md`.

### 3) Gates (profile/policy controlled)

Profiles should gate on *expansion* of the capability set:

- new network egress sockets
- new “wide” directory grants
- rights broadened from read-only to write
- new broker/portal endpoints

Strict profiles (A/D) commonly require two-person integrity when expansion happens.

## Risk flags (minimal starter set)

Diff generators should emit conservative, stable reason codes:

- `preopen-map-egress-added`
- `preopen-map-handle-added`
- `preopen-map-rights-broadened`

Risk flags are canonical ids from `risk.flag.registry` (`spec/examples/risk.flag.registry.json`).

## References (primary primitives)

- Capsicum overview (capability mode; rights on descriptors): https://man.freebsd.org/cgi/man.cgi?query=capsicum&sektion=4
- `cap_enter(2)` (enter capability mode): https://man.freebsd.org/cgi/man.cgi?query=cap_enter&sektion=2
- `cap_rights_limit(2)` (rights masks on descriptors): https://man.freebsd.org/cgi/man.cgi?query=cap_rights_limit&sektion=2
- “Towards oblivious sandboxing with Capsicum” (preopen maps + adoption ergonomics): https://www.engr.mun.ca/~anderson/publications/2017/towards-oblivious-sandboxing.pdf

Last updated: 2026-02-28r175
