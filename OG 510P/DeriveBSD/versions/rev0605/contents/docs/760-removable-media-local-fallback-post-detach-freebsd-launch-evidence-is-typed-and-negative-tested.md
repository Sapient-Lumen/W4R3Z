# Removable-media local fallback post-detach FreeBSD launch evidence is typed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt, Registry→Diff→Gate, Quarantine→Promote

r504 closed the post-detach contract shape. r505 closes the next seam: the FreeBSD backend evidence that proves a later worker actually launched under that contract.

The earlier contract phrase `receipt-must-bind-freebsd-launch-evidence-to-contract` is no longer just a posture promise. The first host-local removable-media fallback now has a typed evidence artifact, a positive fixture, negative fixtures, canonical stack wiring, and a hygiene checker.

See also:
- ADR: `adrs/ADR-0349-removable-media-local-fallback-post-detach-freebsd-launch-evidence-is-typed-and-negative-tested.md`
- runtime schema: `spec/removable.media.local.post_detach.launch.evidence.schema.json`
- exact fixture schema: `spec/removable.media.local.post_detach.launch.evidence.fixture.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.launch.evidence.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-launch-evidence/`
- previous cut: `docs/759-removable-media-local-fallback-post-detach-contract-closure-is-schema-backed-and-negative-tested.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-freebsd-launch-evidence-positive-and-negative-fixture-guarded`
- `sha256:4949494949494949494949494949494949494949494949494949494949494949`
- `known-bad-freebsd-launch-evidence-shapes-must-fail-validation`

The typed launch evidence object is `removable.media.local.post_detach.launch.evidence`. It is intentionally narrower than a future general sandbox evidence object. It only covers the first host-local removable-media fallback: one selected regular-file subject, media detached before worker launch, preserved capture as the only input, a post-detach worker under FreeBSD jail/Capsicum confinement, no Casper services, no network descriptors, no inherited parent environment, no executable path search, nonpersistent scratch, and one declared derivative output slot.


## Runtime/fixture split

r561 keeps the runtime launch-evidence schema generic and moves exact historical r505 literals into `spec/removable.media.local.post_detach.launch.evidence.fixture.schema.json`. New broker output should validate against `spec/removable.media.local.post_detach.launch.evidence.schema.json`; the canonical historical fixture also validates against the exact fixture schema so `sha256:4949494949494949494949494949494949494949494949494949494949494949` remains regression evidence without freezing future launch-evidence digests, worker IDs, launcher IDs, or contract/recovery joins.

## Evidence object shape

`spec/removable.media.local.post_detach.launch.evidence.schema.json` requires these closed-world sections:

- `contract_binding`: the evidence binds back to the r504 contract digest, the preopen map digest, and the plan digest;
- `worker_identity`: the launcher/tool instance and proof that the worker started after detach;
- `launch_sequence`: detach receipt seen, `closefrom` before exec, descriptor review before exec, and `cap_enter` before tool mainline;
- `confinement`: FreeBSD jail/Capsicum posture, Casper absence, devfs posture, pf posture, and mount visibility;
- `descriptors`: only reviewed fds after close/attenuation, no unexpected fds, rights proof digest, and no path-lookup authority on the input object;
- `executable`: launcher-resolved executable digest, no `PATH` search, no helper discovery, no setuid/setgid, and no plugin discovery;
- `runtime_closure`: pinned runtime closure, no loader env vars, no ambient plugin paths;
- `environment`: no inherited parent environment, no `PATH`, no home-like vars, no loader/proxy vars;
- `credentials`: fixed unprivileged worker user/group and no supplementary groups;
- `network`: no sockets, no Casper services, no DNS/resolver/proxy authority, no remote callbacks;
- `scratch`: memory-backed or key-discarded scratch only, cleanup observed, no worker-visible persistent path;
- `output`: one declared derivative slot, append-only, no readback, no truncate, no rebind, broker-collected and remeasured;
- `resource_envelope`: rctl/limit/observed-usage digests and fail-closed resource semantics.

## Red corpus

The launch-evidence red corpus starts under `spec/examples/invalid/removable-media/post-detach-launch-evidence/` with:

- `capability-mode-not-observed.json`
- `unexpected-fd-present.json`
- `casper-service-present.json`
- `network-descriptor-present.json`
- `parent-env-inherited.json`
- `path-search-allowed.json`
- `persistent-scratch-visible.json`
- `output-rebind-possible.json`

Each fixture is intentionally close to the canonical object and must fail validation. This protects against a future edit that quietly broadens the ordinary lane into a general-purpose local worker.

## What this changes in implementation terms

A launcher prototype should now aim to emit a launch-evidence object before it tries to emit a polished user-facing receipt. The evidence object is the backend-facing proof bundle. The derivative receipt can then reference the evidence digest instead of reciting every raw fact inline.

This is deliberately a two-level design:

1. The r504 contract says which authority is allowed.
2. The r505 launch evidence says what the FreeBSD backend actually observed.

The derivative is not receipt-visible until both levels validate.

## Notes for backend implementers

The schema does not require the first prototype to solve every future desktop problem. It asks for a narrow proof bundle:

- record the fd table after `closefrom`/attenuation;
- record rights for each reviewed fd;
- prove the approved shim entered capability mode before tool mainline;
- show the jail/devfs/pf posture active at launch;
- show no Casper service socket or service name was granted;
- show no network descriptor or resolver/proxy authority reached the worker;
- show parent environment, `PATH`, home-like variables, loader variables, and proxy variables were absent;
- show scratch was memory-backed or key-discarded and cleanup was observed;
- show the derivative came only from the declared append-only output slot.

## Failure semantics

For this first lane, evidence failure is not degraded success. The schema records:

- `schema_mismatch = fail-closed`
- `missing_evidence = withhold-derivative-receipt`
- `unexpected_fd = fail-closed`
- `network_authority = fail-closed`
- `persistent_scratch = not-admitted-in-first-lane`
- `output_rebind = fail-closed`

The receipt result visibility posture is `withheld-until-launch-evidence-validates`. A future compatibility lane can define weaker behavior, but it must use a different posture and fixtures.

## First-run check

Run:

```sh
python3 tools/check_removable_media_local_post_detach_launch_evidence.py
```

Then run:

```sh
python3 tools/check_removable_media_local_post_detach_contract_closure.py
python3 tools/validate_spec_examples.py
python3 tools/check_generated_docs.py
```

`tools/hygiene.py` includes the new guardrail so release hygiene catches drift.


## r506 recovery-evidence handoff

r506 keeps launch evidence focused on backend launch facts and adds `spec/removable.media.local.post_detach.recovery.evidence.schema.json` for post-run and post-crash facts. Launch evidence now points at `typed-post-detach-recovery-evidence-positive-and-negative-fixture-guarded` and `sha256:5050505050505050505050505050505050505050505050505050505050505050` so derivative receipt visibility waits for recovery evidence as well as launch evidence.

Last updated: 2026-06-10r561
