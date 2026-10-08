---
id: ss-migrated-translation-loss-proofs-become-an-audit-surface
revision_promoted: pre-rev0182
migration_status: inferred-rev0182
title: Translation-loss proofs become an audit surface
constellation:
- managed-legibility
- queue-governance
- standards-and-conformance
- model-governance
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- standards / interoperability / conformance
- procurement / purchasing / offtake
bottleneck_type:
- admissible evidence
- provenance / custody
- interoperability translation
- conformance capacity
enforcement_surface:
- procurement / framework contract
- platform eligibility
- audit / assurance engagement
artifact_type:
- transform recipe
lifecycle_stage:
- normalize / transform
- validate
- publish
- rely
failure_modes:
- semantic-loss
- forged-proof
---
# Translation-loss proofs become an audit surface

**Thesis:** once trust and verification intent is translated across Trivy VEX-method priority, ordered VEX repositories, Sigstore `ClusterImagePolicy` matching and `no-match-policy` behavior, Kyverno `verifyImages` / `ImageValidatingPolicy` defaults and audit reports, and Ratify config-vs-rego policy providers with different verification-response versions, the scarce capability is no longer only moving a policy bundle from one engine to another. It is producing an inspectable artifact showing what semantics were preserved, tightened, weakened, reordered, or left unresolved. When buyers, auditors, and migration teams start relying on that artifact, translation-loss proofs become an audit surface.

## Core claim

The archive has already argued that **trust-bundle translators become interoperability intermediaries**, **signer-trust profiles become portable policy bundles**, **public replay-result matrices become a buyer shortcut**, **conformance-regression alerts become contract triggers**, and **regression-disclosure windows become a governance surface**. Those dossiers explain why policy intent moves, why tools differ, and why visible regressions matter. But they still leave one practical question under-described: *what proves that a translated policy still means what its operator thinks it means?*

The current documentation shows that this is no longer a hypothetical concern. Trivy says users can enable multiple VEX methods simultaneously and that the order of specification determines priority [S993]. Its repository documentation says repository priority is determined by configuration order and that matching proceeds through repositories until a match is found [S994]. That means one policy surface already encodes meaning as ordered source precedence rather than as a flat allowlist.

Sigstore policy-controller expresses related trust intent differently. Its overview says admission is evaluated against multiple `ClusterImagePolicy` resources, that each matched policy must pass, that at least one authority inside a matched policy must pass, and that the system also exposes a separate `no-match-policy` with `warn|allow|deny` behavior [S995]. In other words, another engine expresses policy meaning through matched-policy conjunction, per-policy authority disjunction, and an explicit unmatched-image default.

Kyverno expresses the same neighborhood of meaning in still another shape. Its `verifyImages` overview says rules include `required`, `mutateDigest`, `verifyDigest`, `repository`, and `attestors.count`, and it explicitly constrains certain fields to static values so evaluation remains deterministic [S996]. Its policy-report documentation says `verifyImages` results can surface in Kubernetes policy reports when resources match relevant rules [S997]. That means Kyverno policy meaning includes enforcement defaults, digest mutation behavior, determinism constraints, and a reportable audit surface, not just signer lists.

Ratify makes the mismatch even more explicit. Its provider documentation says config and rego policy providers can return different verification-result formats, and that config policy supports per-artifact `any` / `all` success semantics [S998]. Its verification-response reference says the response is versioned, that config and rego policies historically generate different response versions, and that the project is tracking unification of the format [S999]. Its Gatekeeper authoring guide then says downstream Rego policies using Ratify external data need to know the response structure to use it correctly [S1000]. So even the machine-readable report that downstream policy consumes is part of the meaning that may drift during migration.

Taken together, these sources point to the next bottleneck: **semantic drift needs evidence, not reassurance**. Once trust-policy migration, policy-bundle translation, and cross-engine interoperability become normal, the important artifact is no longer the translated policy alone. It is the **translation-loss proof**: a compact record that states which source semantics were preserved exactly, which were approximated, which became stricter, which became looser, which defaults changed, which report shapes changed, and which behaviors require named replay cases instead of textual assurance.

A translation-loss proof is therefore not just a migration log. It is closer to an audit object. It gives another party enough structured information to decide whether a translated policy is equivalent enough for use, equivalent only in one environment, or materially different in ways that require approval, compensating controls, or rejection.

## Why this belongs in the archive

This thesis belongs here because it identifies the bottleneck **above** translation itself. The archive has already moved from portable policy objects to translation intermediaries. The next scarce layer is the evidence that makes those intermediaries governable.

That is a broad shift, not a narrow product detail. Many institutional systems follow the same path: first a rule becomes explicit, then it becomes portable, then it becomes translatable, and then the real struggle becomes proving whether translation preserved the operative meaning. At that point the valuable service is no longer conversion alone. It is declared semantic residue.

## Speculative consequences worth tracking

### 1. “Import succeeded” stops being a credible completion signal

Operators may increasingly treat a successful policy import as incomplete unless it is accompanied by a machine-readable statement of preserved, tightened, weakened, and unresolved semantics.

### 2. Auditors begin asking for semantic-drift manifests

Security review and compliance workflows may increasingly request artifacts showing where precedence order, fallback defaults, digest requirements, attestation scope, or response-schema expectations changed during translation.

### 3. Translators start publishing equivalence grades

Intermediaries may increasingly compress complex loss proofs into labels such as exact, tighter, weaker, partial, or advisory-only, while still linking back to the underlying structured proof.

### 4. Migration approvals become case-backed rather than prose-backed

Instead of approving a translated policy from narrative description alone, organizations may increasingly require named replay cases or external-policy tests that demonstrate the important preserved and changed behaviors.

### 5. Report-shape stability becomes part of portability

Once downstream controllers, dashboards, or Gatekeeper policies consume verification results directly, a change in report structure may become just as important as a change in allow/deny logic.

### 6. Silent semantic drift becomes a support and liability problem

More disputes may center on whether a translation quietly widened admission, narrowed signer trust, changed unmatched-resource handling, or dropped an audit-visible outcome without clearly declaring that fact.

### 7. Engines redesign themselves for proofability

If translation-loss proofs become expected, vendors may increasingly redesign policy surfaces so defaults, precedence, and unsupported semantics are easier to enumerate and export.

## What could falsify or weaken the thesis

- One policy model becomes dominant enough that translation remains a marginal migration task.
- Most operators tolerate per-engine divergence and do not demand inspectable proofs of equivalence.
- Translation can usually be exact and obvious, so separate loss proofs add little value.
- Downstream enforcement and reporting systems stop depending on precise response shapes or policy defaults.
- Buyers and auditors remain satisfied with informal migration notes rather than structured semantic-drift evidence.

## Research queue

- Which semantic differences most often force a loss proof: precedence order, unmatched-resource defaults, `any` / `all` success thresholds, digest mutation, attestor counts, or report-schema dependencies?
- Do translation-loss proofs stay internal migration artifacts, or do suppliers begin publishing them as buyer-facing evidence packs?
- Which format emerges first for proof exchange: diff manifests, replay-case bundles, signed attestations, or policy-pair scorecards?
- Do ecosystems begin defining named equivalence classes for policy translation, such as exact, stricter, weaker, or non-comparable?
- Which downstream systems first break because report shape drift was treated as cosmetic when it was actually operational?
