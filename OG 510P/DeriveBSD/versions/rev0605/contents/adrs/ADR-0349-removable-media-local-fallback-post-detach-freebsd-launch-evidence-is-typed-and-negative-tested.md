# ADR-0349: Removable-media local fallback post-detach FreeBSD launch evidence is typed and negative-tested

- Status: accepted
- Date: 2026-05-21
- Deciders: archive maintainers
- Consulted: `adrs/ADR-0348-removable-media-local-fallback-post-detach-contract-closure-is-schema-backed-and-negative-tested.md`, `docs/759-removable-media-local-fallback-post-detach-contract-closure-is-schema-backed-and-negative-tested.md`, `spec/removable.media.local.post_detach.launch.evidence.schema.json` / `spec/removable.media.local.post_detach.launch.evidence.fixture.schema.json`

## Context

ADR-0348 made the first removable-media post-detach worker contract schema-backed and red-fixture guarded, but it still used `receipt-must-bind-freebsd-launch-evidence-to-contract` as a posture promise. That is the right promise, but it leaves the next implementation seam open: a receipt could name backend evidence without proving which FreeBSD facts were observed, which descriptors survived `closefrom`, whether capability mode was entered before tool mainline, whether Casper services were absent, whether the worker inherited parent environment, or whether the derivative slot was non-rebindable.

The first host-local fallback needs a concrete evidence target before runtime code exists, not after. The evidence object should be narrow enough to emit from an early launcher and strict enough to reject common false proofs.

## Decision

Add `spec/removable.media.local.post_detach.launch.evidence.schema.json` with kind `removable.media.local.post_detach.launch.evidence`, the canonical example `spec/examples/removable.media.local.post_detach.launch.evidence.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-launch-evidence/`.

The ordinary B/C removable-media local fallback now records `typed-freebsd-launch-evidence-positive-and-negative-fixture-guarded`, `sha256:4949494949494949494949494949494949494949494949494949494949494949`, and `known-bad-freebsd-launch-evidence-shapes-must-fail-validation` in the contract, plan, receipt, preopen map, attach grant, and detach receipt examples.

The launch-evidence object is explicitly FreeBSD-shaped: jail/Capsicum confinement, Casper absence, devfs and pf posture, fd table after `closefrom`, fd rights proof, launcher-resolved executable identity, pinned runtime closure, reviewed environment, fixed unprivileged credentials, no network descriptors, nonpersistent scratch, broker-collected output, resource evidence, and failure semantics.


### r561 runtime/fixture split

r561 keeps ADR-0349's narrow FreeBSD launch evidence semantics but separates the generic runtime schema from the exact historical fixture schema. Runtime broker output validates against `spec/removable.media.local.post_detach.launch.evidence.schema.json`; the canonical r505 sample also validates against `spec/removable.media.local.post_detach.launch.evidence.fixture.schema.json` so the historical `sha256:4949494949494949494949494949494949494949494949494949494949494949` digest remains pinned as fixture evidence, not as a runtime contract literal.

## Consequences

- The backend evidence promise from ADR-0348 is now an artifact target rather than a comment.
- A derivative receipt is not visible for this lane until launch evidence validates against the typed object.
- Runtime implementers have a first evidence shape to emit: they do not need to guess which FreeBSD facts count.
- Negative fixtures make false launch evidence explicit. Capability mode not observed, unexpected fds, Casper services, network descriptors, inherited parent env, path search, persistent scratch, and output rebind all fail the ordinary-lane schema.

## Alternatives considered

- **Keep backend evidence as a posture field.** Rejected because the implementation would still have to invent the evidence grammar later.
- **Use one generic sandbox evidence object.** Rejected for the first lane because removable-media post-detach evidence has deliberately narrow B/C assumptions that should not be hidden behind a broad launcher abstraction.
- **Accept textual launcher logs as evidence.** Rejected for the ordinary lane because logs are useful diagnostics but not a closed-world contract.

## Follow-up

- Teach the first launcher prototype to emit this evidence object or a mechanically translatable superset.
- Add backend-specific extraction notes for fd rights, jail profile digests, devfs rulesets, pf anchors, and scratch teardown.
- Consider promoting common fields into a future generic `sandbox.launch.evidence` schema only after this narrow lane proves stable.

## Links

- boundary doc: `docs/760-removable-media-local-fallback-post-detach-freebsd-launch-evidence-is-typed-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.launch.evidence.schema.json`
- exact fixture schema: `spec/removable.media.local.post_detach.launch.evidence.fixture.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.launch.evidence.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-launch-evidence/`
- previous cut: `adrs/ADR-0348-removable-media-local-fallback-post-detach-contract-closure-is-schema-backed-and-negative-tested.md`
