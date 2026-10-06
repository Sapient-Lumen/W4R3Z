# Closure proofs (prove what will run)

DeriveBSD’s **closure** is the complete, transitive set of runtime objects that must exist for a host generation or workload instance to run.

The goal is not just to *compute* closures, but to **prove** them:
- every runtime bit is accounted for
- every object is content-addressed and verified
- the result is explainable and reversible

## Closure manifest

A **closure manifest** is a small, hashable JSON object that lists:
- the root artifact(s) (host generation or microVM bundle)
- the runtime manifest digest (for microVMs)
- all referenced store objects (path + digest)
- required attestations/policies (as digests)

The manifest is JCS-canonicalized (RFC 8785) before hashing.

Schema + example:
- `spec/closure.manifest.schema.json`
- `spec/examples/closure.manifest.json`

## Closure proof

A **closure proof** is a signature over:
- `closure_manifest_digest`
- a target kind (`host` | `microvm` | …)
- a namespace/channel identifier
- an expiry or epoch window (anti-freeze)

Proofs are checked *before* activation/launch.

Schema + example:
- `spec/closure.proof.schema.json`
- `spec/examples/closure.proof.json`

## Verification rules (v1)

At consume time:
1. Verify **closure manifest digest**.
2. Verify **closure proof signature** against policy-selected keys.
3. Verify each referenced store object’s **digest**.
4. If policy requires attestations, verify they exist and bind to the artifact digest.

Additionally, consumers should verify the **policy decision record** referenced by the closure manifest bindings (`docs/93-policy-decision-records.md`).

Additionally, runtime closure verification should bind the root artifact's `host_platform` (not `build_platform`) so cross-built objects remain explainable without accidentally treating build-host tools as runtime authority. That boundary now follows `docs/701-cross-compilation-platform-identity-stays-build-host-target-shaped-and-not-store-path-encoded.md` and the helper schemas `spec/platform.identity.schema.json` / `spec/platform.roles.schema.json`.

This is the minimal mechanism behind:
- “prove closure”
- “deny network” (no runtime fetches)
- “explain dependencies”
- build-only tools do not become runtime closure authority by accident

Pointers:
- store/closure basics: `docs/56-store-layout-and-digests.md`
- artifact verification rules: `adrs/ADR-0009-artifact-verification.md`
- channel metadata / anti-freeze: `docs/61-channel-metadata-tuf-inspired.md`, `docs/62-replay-rollback-freeze.md`

Last updated: 2026-03-23r432
