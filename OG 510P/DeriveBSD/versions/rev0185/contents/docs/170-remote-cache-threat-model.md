# Remote cache threat model (poisoning, replay, and verification)

DeriveBSD’s baseline cache posture is “untrusted mirrors, trusted verification.”
But remote caching adds a subtle extra attack surface: the cache can claim “this action output is X” even if it is lying.

Bazel distinguishes remote caching from remote execution and documents the operational model.
Recent deep dives also highlight the security pitfalls of adopting remote caches without carefully defining trust boundaries.

## Threats

### 1) Action-cache poisoning

An attacker controlling the cache (or MITM) returns a wrong output for a given action key.
If clients accept it without verification, the cache becomes a build oracle.

### 2) Replay / freeze

Even signed artifacts can be replayed if clients don’t enforce freshness/expiry and anti-rollback rules.
(Handled elsewhere via TUF/Uptane-inspired metadata, but the cache must not bypass those checks.)

### 3) Cross-tenant leakage

If cache keys are not derived strictly from declared inputs, a tenant can influence or observe another tenant’s builds.

## DeriveBSD constraints (what makes this fixable)

1) **Plan digest is the action key**
- Remote cache lookups are keyed by `plan_digest` + target kind + builder ABI.

2) **CAS + closure proof**
- Outputs are content-addressed; the client verifies blob/tree digests.
- Closure proof prevents “missing dependency” tricks.

3) **Publish-domain re-signing**
- Builders and caches are not trusted as authorities.
- Only the publish domain may mint *trusted* signatures for a namespace/channel.

4) **Policy-bound acceptance**
- Even a correct artifact can be rejected if required evidence (tests, SBOM, provenance) is missing.

## Operational recommendation

- Treat remote caches as performance optimizers, never as authorities.
- Verify outputs before importing into a trusted store dataset.
- Record cache provenance in evidence:
  - “fetched from cache C at time T” as a signed receipt (optional transparency input).

Optional high-assurance add-on:

- require **cache witness quorums** for specific channels/targets so substitution requires corroboration by independent rebuilders (`docs/190-cache-witness-quorums-trustix.md`).

## Where this plugs in

- baseline cache trust model: `docs/46-cache-trust-model.md`
- transparency lanes: `docs/131-sigsum-lightweight-transparency.md`, `docs/132-scitt-ledger-receipts.md`

## References

- Bazel remote caching: https://bazel.build/remote/caching
- Bazel remote execution overview: https://bazel.build/remote/rbe
- Remote caching security deep dive: https://blogsystem5.substack.com/p/bazel-remote-caching

Last updated: 2026-02-24

