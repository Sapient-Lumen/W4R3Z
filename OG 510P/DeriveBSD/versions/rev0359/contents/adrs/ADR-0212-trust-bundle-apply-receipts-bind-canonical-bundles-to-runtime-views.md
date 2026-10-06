# ADR-0212: Trust-bundle apply receipts bind canonical bundles to runtime views

- Status: Accepted
- Date: 2026-03-21

## Context

`docs/480-trust-bundle-posture-by-profile.md` already fixed the **product-default authority posture** for trust roots across A–D.
`docs/434-pki-trust-bundle-diff-as-review-surface.md` already fixed the compact drift-review surface.
`docs/228-pki-and-identity-lifecycle-as-evidence.md` and `docs/304-trust-bundles-and-ca-injection-as-artifacts.md` already said the right thing conceptually too:

- canonical trust roots live in `pki-trust-bundle`,
- renderers/adapters are not the source of truth,
- and hosts should be able to prove what trust-store view they actually served.

But one concrete boundary was still missing:

**there was no typed receipt for binding one canonical trust bundle digest to the exact runtime trust view that a host or unit actually applied.**

That omission is expensive because it pushes the most operationally important answer back into adapter folklore:

- operators can review `pki.trust.bundle.diff`, yet still fail to prove which rendered view was actually active on a host or unit,
- shadow-trust investigations can find embedded stores but cannot cleanly point at the official system view that should have been in force,
- support bundles can name the canonical bundle digest but not the exact rendered CAfile / p11-kit / NSS view that a workload actually consumed,
- and distribution adapters can quietly become the de facto source of truth even though their APIs and object models churn over time.

The last point is not theoretical: current trust-distribution ecosystems already show that distribution APIs move independently of trust semantics (for example, cert-manager trust-manager currently centers a cluster-scoped `Bundle` resource but has announced a shift toward `ClusterBundle`).
DeriveBSD therefore needs one stable receipt boundary that survives adapter churn.

No new `product.profiles.defaults` key is introduced.

## Decision

1. Standardize a new evidence artifact: `pki.trust.bundle.apply.receipt`.
   - Schema: `spec/pki.trust.bundle.apply.receipt.schema.json`
   - Example: `spec/examples/pki.trust.bundle.apply.receipt.json`

2. Keep **`pki-trust-bundle` authoritative**.
   `pki.trust.bundle.apply.receipt` is evidence about what canonical bundle digest was rendered and applied to a target view.
   It does **not** replace `pki-trust-bundle` as trust-root authority and does **not** turn renderer output bytes into a new source of truth.

3. Make the receipt bind four things together:
   - the canonical `bundle_digest`,
   - the purpose-scoped target (`purpose`, `target.scope`, host/unit identifiers),
   - the deterministic rendered output digests actually served (`renderings[]`),
   - and the result/status of the apply act.

4. Keep the object **small and digest-first**.
   The receipt records rendered output digests and target metadata.
   It does not carry raw PEM/NSS/p11-kit bytes, raw certificate material, or adapter-private state dumps by default.

5. Keep **one receipt = one canonical bundle → one target view**.
   One receipt = one canonical bundle→one target view.
   If a host generation or unit consumes multiple trust bundles/purposes, that produces multiple apply receipts instead of one giant ambient trust-state blob.

6. Keep **events joined to receipts**.
   `pki-event` may carry `pki_trust_bundle_apply_receipt_digest` for `pki.trust-bundle.updated` milestones so support bundles and journals can point at exact apply proof.

7. Keep **distribution adapters killable**.
   `certctl`, p11-kit, NSS DB renderers, Kubernetes trust distributors, SPIFFE bundle delivery, and similar helpers remain adapters or consumers.
   Their changing APIs must not redefine the canonical trust-root object or the apply-proof boundary.

## Consequences

- The archive now has a typed answer to “what exact trust-bundle view did this host or unit actually serve?”
- Diff review (`pki.trust.bundle.diff`) and activation/apply proof (`pki.trust.bundle.apply.receipt`) are now separate and composable.
- Support/export/investigation flows can stay digest-first while still proving concrete runtime trust views.
- Adapter churn no longer gets to masquerade as trust-root authority.

## What this does not decide

This ADR does **not** decide:

- the final trust-portal API,
- the final renderer set shipped on day-0,
- the final shadow-trust scan taxonomy or waiver object,
- whether a given apply act is host-generation-only, unit-runtime-only, or both in every implementation,
- or the exact transport/export contract for stronger trust-related evidence bundles.

It only closes the missing receipt boundary between canonical bundle objects and concrete runtime trust views.
