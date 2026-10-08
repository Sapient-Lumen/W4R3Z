---
id: ss-0183-semantic-equivalence-grades-become-migration-shorthand
revision_promoted: pre-rev0180
title: Semantic-equivalence grades become migration shorthand
constellation:
- standards-and-conformance
- model-governance
- managed-legibility
- maintenance-and-repair
status: dossier
maturity: S3-enforcement-surface
confidence: medium-low
time_horizon: mixed
domain:
- standards / interoperability / conformance
- compute / AI / data centers
- simulation / forecasting / counterfactual capacity
- identity / credentials / delegated authority
- procurement / purchasing / offtake
- waste / remediation / decommissioning
bottleneck_type:
- conformance capacity
- interoperability translation
- version / support-window compatibility
- model credibility
- admissible evidence
- state freshness
- source-of-truth precedence
- appealability / redress
- liability-tail custody
- maintenance capacity
- replayability / reconstructability
enforcement_surface:
- certification / conformity assessment
- procurement / framework contract
- audit / attestation / assurance
- platform eligibility / ranking
- permit / license
- underwriting / insurance renewal
artifact_type:
- registry entry
- notice
- state label
- certificate / attestation
- replay bundle
lifecycle_stage:
- publish
- rely
- dispute
- correct
- archive
- retire
primary_actors:
- standards-body
- certifier
- buyer
- model-provider
- auditor
- broker
- source-vendor
- operator
- insurer
failure_modes:
- stale-state
- nonpropagation
- false-match
adversarial_pressure:
- strategic-delay
- overbroad-disclosure
distributional_effect:
- incumbent-compliance-advantage
migration_status: inferred-rev0183-minimal
migration_note: Metadata was inferred from title, source references, and local keyword context; review before treating as authoritative.
---
# Semantic-equivalence grades become migration shorthand

**Thesis:** once trust and exception policy is translated across Trivy VEX-method priority, ordered VEX repositories, Sigstore matched-policy conjunction plus `no-match-policy`, Kyverno `verifyImages` defaults and current-state policy reports, and Ratify policy-provider-dependent result formats and `any`/`all` success logic, another party stops wanting to re-read a full drift proof every time. It starts wanting a compact answer to a narrower question: *how close is this translated policy to the source policy in the ways that matter?* When ecosystems begin compressing that answer into labels such as **exact**, **stricter**, **weaker**, **partial**, **advisory-only**, or **non-comparable**, semantic-equivalence grades become migration shorthand.

## Core claim

The archive has already argued that **trust-bundle translators become interoperability intermediaries**, **translation-loss proofs become an audit surface**, **public replay-result matrices become a buyer shortcut**, **conformance-regression alerts become contract triggers**, and **regression-disclosure windows become a governance surface**. Those dossiers explain why policy intent moves, why proof objects matter, and why visible regressions become commercially relevant. But they still leave one practical gap: *how is a complex proof object compressed into something a buyer, migration reviewer, or downstream operator can actually govern by?*

The current documentation shows that this compression problem is no longer hypothetical. Trivy says VEX usage methods can be enabled simultaneously and that their order determines priority [S1015]. Its repository documentation then says repository order also determines which VEX document wins and that search stops at the first match [S1016]. So one ecosystem already encodes decisive meaning in ordered method and repository precedence.

Sigstore policy-controller expresses adjacent meaning in a different shape. Its overview says all matched `ClusterImagePolicy` resources must pass, at least one authority inside a matched policy must pass, and unmatched images are governed separately through configurable `no-match-policy` behavior with `warn|allow|deny`; if `no-match-policy` is absent, unmatched images are rejected by default [S1017]. That is not merely a different file format. It is a different default-and-matching model.

Kyverno gives the same neighborhood of intent yet another shape. Its `verifyImages` overview says policy meaning includes `required`, `mutateDigest`, `verifyDigest`, alternate signature repositories, and attestor counts [S1018]. Its policy-report documentation says `verifyImages` results are emitted as policy reports for currently matching resources and that reports always represent current cluster state rather than retained history [S1019]. So translation into or out of Kyverno can change not only admission behavior but also what sort of audit-visible surface exists afterward.

Ratify makes the compression problem even clearer. Its provider documentation says verification results differ between Rego policy and config policy, that Rego policy uses verification-response `1.0.0`, and that config policy supports per-artifact `any` / `all` success logic with a configurable default policy [S1020]. In other words, another engine expresses meaning through provider choice, response shape, and success thresholds, not just signer selection.

Taken together, these sources point to the next bottleneck: **translation-loss proofs need a governable summary layer**. Once full proofs exist, institutions will not want to inspect every field-level difference during every migration, exception review, supplier comparison, or procurement cycle. They will want a compact label that says whether the translated policy is effectively the same, tighter, weaker, only partially comparable, or too semantically different to treat as equivalent at all.

That is what a semantic-equivalence grade does. It does **not** replace the full proof object. It compresses it into a reusable governance signal. A grade makes it possible to sort, filter, approve, escalate, or reject translated policies without pretending that every migration deserves a full bespoke reading.

## Why this belongs in the archive

This thesis belongs here because it identifies the layer **above** translation-loss proofs. Once translation itself becomes common and loss becomes inspectable, the scarce capability is no longer only proving what changed. It is making that proof legible enough to route decisions.

That pattern is broad. Many systems pass through the same sequence:

1. a rule becomes explicit;
2. the rule becomes portable;
3. portability forces translation;
4. translation forces proof of drift; and then
5. institutions need compressed grades so that ordinary governance can keep up.

At that point the valuable object is not just the full diff. It is the **gradeable equivalence claim** attached to the diff.

## Speculative consequences worth tracking

### 1. Migration approvals start with grades, not proofs

Teams may increasingly triage translated policies by an initial grade such as exact, stricter, weaker, partial, or non-comparable, opening the full drift proof only for borderline or contested cases.

### 2. Procurement starts setting minimum acceptable grades

Buyers may increasingly ask not only whether a policy can be imported, but whether the supplier can demonstrate a minimum grade such as exact-or-stricter for named control families.

### 3. Regression alerts begin carrying grade deltas

A downgrade may increasingly be described not only as pass-to-fail, but as a shift from exact to partial, or from stricter to weaker, which is a much more legible signal for contract and risk review.

### 4. “Non-comparable” becomes an escalation class

Some migrations may increasingly be blocked not because a tool cannot import a file, but because its semantics are different enough that no honest equivalence grade above non-comparable can be assigned.

### 5. Public matrices become richer than pass/fail

Replay-result registries and buyer-facing scoreboards may increasingly add grade columns so ecosystems can compare not just whether an implementation passed a fixture, but how faithfully it preserved the source policy’s meaning.

### 6. Vendors redesign for gradability

If equivalence grades become operationally important, policy engines may increasingly redesign defaults, precedence rules, and report shapes so their semantics are easier to map into common grade classes.

### 7. Translation intermediaries compete on explainable grades

The trusted intermediary may increasingly be the one that can produce a compact, reproducible grade with clear downgrade reasons, not just the one that can emit a syntactically valid translated policy file.

## What could falsify or weaken the thesis

- Operators remain willing to inspect full proof objects without relying on compressed grades.
- One dominant policy model emerges, making translation and comparability marginal concerns.
- Most migrations are obviously exact or obviously impossible, leaving little need for intermediate grade classes.
- Buyers continue governing by prose assurances or local replay only, without treating equivalence grades as reusable signals.
- Engines converge enough on defaults, precedence, and reporting that a separate grading layer adds little value.

## Research queue

- Which semantic differences most often decide the grade: precedence order, unmatched-resource defaults, digest mutation, report shape, attestor thresholds, or success logic?
- Who gets to publish the grade: the translator, the destination engine, an independent signer, or the buyer?
- Does a durable grade taxonomy settle around exact / stricter / weaker / partial / non-comparable, or do sectors invent their own classes?
- Which decisions first encode grade floors formally: migration approvals, procurement terms, exception portability, or public conformance listings?
- Do replay fixtures eventually become the evidence substrate from which equivalence grades are computed automatically?
