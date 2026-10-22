# Worker-pool constructor harness v0 (first D-CONSTR evidence contract)

Purpose: turn the pinned **sandboxed worker-pool constructor family** into a concrete **verification/evidence target**.
This doc specifies what the first harness for **D-CONSTR** must capture, compare, and reject so `I-CONSTR-1`, `I-CONSTR-2`, `PO-CONSTR-CONFINE`, and `PO-CONSTR-REPLAY` become implementable against one real family rather than remaining archive prose.
`docs/40-verification/worker-pool-constructor-evidence-pack-v0.md` then fixes the canonical member labels and stable case ids for handing that evidence to downstream tooling.
It is a **contract for harness/evidence tooling**, not a new constructor protocol, runtime API, or control plane.

Scope:
- applies only to the first concrete D-CONSTR family in `docs/30-architecture/worker-pool-constructor-family-v0.md`
- reuses existing seams: **CH-EXECPACK v2**, **CH-CAPG v0**, **CH-LOG v0**, **CH-SPROJ v0**, **D-CAPAUD**, **D-SEAL**, **D-BUDGET**, **D-COMMUTE**
- assumes the worker-pool family already fixed the import/export boundary and the allowed nondeterminism envelope via `docs/30-architecture/worker-pool-constructor-invocation-v0.md`
- assumes the exact family-local parameter schema is already fixed by `docs/30-architecture/worker-pool-parameter-schema-v0.md`
- assumes the exact meaning of the required sponsor import is already fixed by `docs/30-architecture/worker-pool-sponsor-surface-v0.md`
- assumes the exact meaning of the optional install import is already fixed by `docs/30-architecture/worker-pool-install-target-surface-v0.md`
- assumes the exact meaning of repeated `worker_seed/<label>` imports is already fixed by `docs/30-architecture/worker-pool-seed-surface-v0.md`
- assumes the exact invocation-manifest object is already fixed by `docs/30-architecture/worker-pool-invocation-manifest-v0.md`
- assumes the exact caller-scoped `capgraph.before` / `capgraph.after` meaning is already fixed by `docs/40-verification/worker-pool-capgraph-snapshots-v0.md`
- assumes the exact install-only `target.before` / `target.after` meaning is already fixed by `docs/40-verification/worker-pool-target-projection-v0.md`
- assumes the exact bounded `transcript.slice` layout is already fixed by `docs/40-verification/worker-pool-transcript-slice-v0.md`
- assumes the exact compact `verdict.summary` contract is already fixed by `docs/40-verification/worker-pool-verdict-summary-v0.md`
- assumes the exported `pool.control` handle already stays on the narrow surface pinned in `docs/30-architecture/worker-pool-control-surface-v0.md`
- assumes the exported `worker[i]` handles already stay on the narrow surface pinned in `docs/30-architecture/worker-pool-worker-surface-v0.md`

Non-goals:
- defining a generic constructor request/receipt schema
- standardizing a pool autoscaling or queue-management API
- proving all constructor families correct from one harness
- adding a constructor-global sequencing service, inventory API, or admin plane

## Harness inputs (must be frozen before construction)

1) **The harness binds one invocation contract digest set before construction begins**
   - The harness input manifest MUST fix, by digest:
     - worker template/artifact digest set,
     - exact `digest(CH-EXECPACK v2)` for the worker launch closure,
     - parameter-object digest,
     - import-contract digest,
     - export-contract digest,
     - any sponsor/request-context digests that are part of the reviewed invocation.
   - The harness may add labels for operator readability, but every comparison uses digests rather than prose.

2) **Baseline and post-state observations are caller-scoped and redacted**
   - Before construction, capture a bounded **caller-scoped** `CH-CAPG v0` snapshot plus any target-seam state projection needed for install cases.
   - After construction, capture the corresponding post-state snapshot(s).
   - The exact `capgraph.before` / `capgraph.after` member meaning is pinned in `docs/40-verification/worker-pool-capgraph-snapshots-v0.md`: one same-profile `CH-CAPG v0` pair over a shared scope, compared only on the normalized caller-reachable delta.
   - Redaction/bounds policy remains fail-closed; the harness is not allowed to widen observation authority just to make the test pass.

## Boundary predicate

3) **The only allowed caller-reachable delta is the declared pool control handle plus the bounded worker-set surface**
   - `PO-CONSTR-CONFINE` passes only if the caller-visible cap-graph delta is exactly:
     - one declared pool-control handle named `pool.control`, and
     - the predeclared bounded worker-set surface named `worker[0]` through `worker[pool_size-1]`.
   - Any newly caller-reachable helper channels, supervisor handles, template fetch handles, registry bindings, undeclared worker references, or caller-chosen export aliases are a failure.

4) **Internal helper authority must stay non-reachable from the caller**
   - The constructor may use helper objects during bring-up, but the post-state delta must show they are not caller-reachable unless explicitly part of the export contract.
   - In particular, sponsor handles, template fetch authority, init-only service routes, and setup-only supervisor references must not appear as accidental outputs.

5) **Declared nondeterminism is narrow and explicit**
   - `I-CONSTR-2` is evaluated modulo only the family’s declared nondeterminism:
     - fresh object/worker IDs,
     - internal bring-up order that is not caller-visible,
     - target-seam ordering tokens when testing non-commuting install cases.
   - Output *structure* must still be deterministic: same export names/slots, same arity, same digest set for invocation inputs.

## Transcript / replay contract

6) **Replay evidence is digest-first, not prose-first**
   - The harness transcript slice MUST bind the same digest set named above and make it possible to distinguish:
     - constructor start,
     - constructor success/failure,
     - any target-seam install step,
     - any denial due to missing imports, export collision, or policy/lane gating.
   - The exact bounded transcript layout is pinned in `docs/40-verification/worker-pool-transcript-slice-v0.md`: `transcript.slice` is a case-indexed bounded window set over ordered `CH-LOG v0` references, stable case ids own the layout, and `fresh-commute` / `install-conflict` carry `primary` + `swapped` order variants.
   - The transcript/evidence slice MUST also bind the presence of exactly one `sponsor` import, the exact set of `worker_seed/<label>` imports, whether `install_target` was present, and the canonical exported names `pool.control` plus `worker[i]`.
   - The harness may use ordinary `CH-LOG v0` entries plus digest references; it does not require a new constructor-specific transcript schema.

7) **Fresh isolated pool creation is the positive commutativity case**
   - The harness MUST test the commuting case where two fresh pool instantiations consume disjoint explicit imports and publish only to previously unused export slots.
   - Success criterion: swap order changes only fresh identifiers/internal epochs, not the normalized caller-visible export structure.

8) **Install-into-existing-slot tests must reuse the target seam’s conflict keys**
   - The harness MUST also test one non-commuting install case where the constructor publishes into an owner-visible slot/name/export table.
   - Success criterion: ordering/serialization evidence comes from the target seam’s existing conflict key(s), ordering witness, and `CH-SPROJ v0`-style post-state observations rather than a constructor-global ordering service.

## Negative tests

9) **Negative tests must probe ambient authority acquisition and export widening**
   - Minimum negative cases:
     - undeclared import removed → deterministic failure,
     - requested export wider than the pinned export contract → deterministic failure,
     - worker attempts ambient file/network/time/entropy/local-IPC acquisition beyond explicit imports → deterministic failure or confinement-test failure,
     - replay with changed template/exec-pack/parameter digest but claimed “same invocation” → mismatch detected/fail closed.
   - At least one negative case should exercise the existing capshell posture suites for “no ambient acquisition” where applicable.

## Required harness outputs

10) **The first evidence bundle is small and closed**
   - The harness output bundle MUST contain:
     - the frozen invocation contract digest set,
     - baseline and post-state `CH-CAPG v0` snapshots,
     - any target-seam projection needed for install cases,
     - the transcript slice (`CH-LOG v0` digests or canonical entries),
     - a machine-checkable pass/fail summary for the delta predicate and replay predicate.
   - The bundle must stay bounded and content-addressable so it can later fit replay bundles / incident bundles without inventing a new evidence lane.
   - `worker-pool-constructor-evidence-pack-v0.md` fixes the canonical member labels for that bundle as `invocation.manifest`, `capgraph.before`, `capgraph.after`, `transcript.slice`, `verdict.summary`, and install-only `target.before` / `target.after`.
   - `worker-pool-capgraph-snapshots-v0.md` fixes the exact `capgraph.before` / `capgraph.after` object pair itself: same-profile caller-scoped `CH-CAPG v0` receipts, compared only on the normalized caller-reachable delta over the canonical export surface.
   - `worker-pool-verdict-summary-v0.md` fixes the exact compact `verdict.summary` object itself: one stable case-id verdict table with explicit `delta_predicate_ok` / `replay_predicate_ok` bits over the canonical worker-pool export shape.

## Wiring

- Decision surface: **D-CONSTR**.
- Primary family contract: `docs/30-architecture/worker-pool-constructor-family-v0.md`.
- Exact invocation boundary: `docs/30-architecture/worker-pool-constructor-invocation-v0.md`.
- Exact family-local parameter schema: `docs/30-architecture/worker-pool-parameter-schema-v0.md`.
- Exact sponsor-import contract: `docs/30-architecture/worker-pool-sponsor-surface-v0.md`.
- Exact install-target contract: `docs/30-architecture/worker-pool-install-target-surface-v0.md`.
- Exact seed-import meaning: `docs/30-architecture/worker-pool-seed-surface-v0.md`.
- Exact invocation-manifest contract: `docs/30-architecture/worker-pool-invocation-manifest-v0.md`.
- Exact control-handle contract: `docs/30-architecture/worker-pool-control-surface-v0.md`.
- Exact worker-entry contract: `docs/30-architecture/worker-pool-worker-surface-v0.md`.
- Canonical handoff pack: `docs/40-verification/worker-pool-constructor-evidence-pack-v0.md`.
- Exact cap-graph snapshot contract: `docs/40-verification/worker-pool-capgraph-snapshots-v0.md`.
- Exact target-projection contract: `docs/40-verification/worker-pool-target-projection-v0.md`.
- Exact transcript-slice contract: `docs/40-verification/worker-pool-transcript-slice-v0.md`.
- Exact verdict-summary contract: `docs/40-verification/worker-pool-verdict-summary-v0.md`.
- Supporting seams: **D-CAPAUD**, **D-COMMUTE**, **D-SEAL**, **D-BUDGET**.
- Assurance hooks: **I-CONSTR-1**, **I-CONSTR-2**, **PO-CONSTR-CONFINE**, **PO-CONSTR-REPLAY**.
- External inspirations: **REF-FUCHSIA-REALMS**, **REF-GENODE-INIT**, **REF-EROS-CONFINEMENT**.

## Evidence hook

- CI drift gate: `tools/check_constructor_worker_pool_harness.py` (**EVID-2026-359**).
