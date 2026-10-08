# Graph Backbone

This file records typed relationships among dossiers. It is intentionally partial. Its purpose is to keep the archive from becoming a warehouse of adjacent nouns.

## Edge types

- **precondition-of** — dossier A must exist before dossier B becomes operationally plausible.
- **sequel-to** — dossier B is a later lifecycle stage of dossier A.
- **imports-pattern-from** — dossier B borrows a governance pattern from another domain.
- **same-artifact-family-as** — dossiers share reusable object shapes.
- **same-failure-mode-as** — dossiers fail for structurally similar reasons.
- **weakens** — dossier B limits, complicates, or de-romanticizes dossier A.
- **anti-abuse-layer-for** — dossier B exists because dossier A creates incentives to game the system.
- **privacy-layer-for** — dossier B preserves usefulness while limiting disclosure.
- **small-actor-layer-for** — dossier B exists because dossier A would otherwise burden smaller participants.

## Reliance-object lifecycle chain

```text
authoritative source hierarchies
  -> source-snapshot escrow
  -> reliance-grade source attestations
  -> reliance-scope matrices
  -> re-review trigger grammars
  -> effective-date synchronization services
  -> state-transition notice services
  -> delivery attestations
  -> propagation-lag budgets
  -> convergence-proof gates
  -> proceed-before-convergence waivers
  -> compensating-control bundles
  -> post-waiver validation certificates
  -> conditional-acceptance residue inventories
  -> residue burn-down covenants
  -> extension-lineage disclosures
  -> renewal-history normalization services
  -> normalization-loss warranties
  -> non-comparable-state carve-outs
  -> source-object identity warranties
  -> transformation-code escrow
  -> split/merge correction notices
  -> amendment-recipient registries
  -> identity-match appeals
  -> appeal-stay labels
  -> correction-materiality thresholds
  -> non-reliance packet states
```

## New rev0180 edges

### source-witness nonresponse defaults become broker policy

- **sequel-to:** identity-match appeals become broker support queues
- **sequel-to:** appeal-stay labels become reliance controls
- **precondition-of:** reasoned unresolved / unverifiable / silence-based stay outcomes
- **anti-abuse-layer-for:** strategic source-vendor silence, buyer delay, seller obstruction
- **same-failure-mode-as:** authority-check outages; record repair; source-of-truth precedence disputes

### recipient-graph privacy proofs become broker trust products

- **sequel-to:** amendment-recipient registries become reliance-graph infrastructure
- **privacy-layer-for:** state-transition notice services; delivery attestations; appeal-stay propagation
- **weakens:** naive managed legibility, because not every correct graph should be visible to every counterparty
- **same-artifact-family-as:** selective-disclosure credentials; trust-bundle translators; proof-of-origin objects

### non-reliance packet states become version lifecycle controls

- **sequel-to:** correction-materiality thresholds become packet boilerplate
- **sequel-to:** appeal-stay labels become reliance controls
- **same-artifact-family-as:** regression-retirement markers; machine-readable retirement notices; historical-state views
- **precondition-of:** reopening thresholds for holdbacks, covenants, eligibility, and audit reliance

### compliance-object forgery becomes organized fraud infrastructure

- **anti-abuse-layer-for:** product passports; due-diligence statements; validation reports; appeal-stay labels; source attestations
- **weakens:** any thesis that assumes machine-readable proof objects remain trusted merely because they are structured
- **same-failure-mode-as:** spoofed notices; false-positive exception workflows; forged credentials; trust-anchor compromise

### data-minimization proofs become procurement requirements

- **privacy-layer-for:** recipient-graph privacy proofs; delegated authority; product passports; EUDR place-proof; identity wallets
- **weakens:** broad disclosure as the default path to trust
- **precondition-of:** privacy-preserving eligibility, role, origin, and authority proofs in high-volume workflows

## Cross-constellation bridges to watch

### Product passports and packet governance

Digital product passports validate the archive's “objects acquire governed biographies” lane. But their next problems are packet-governance problems: issuer identity, update rights, repair history, selective disclosure, forged passports, non-reliance states, successor pointers, and resolver continuity.

### EUDR place-proof and small-supplier burden

Deforestation-free market access turns plot geometry and due-diligence statements into admissibility objects. The likely bottleneck is not only satellite detection; it is the small supplier's ability to generate, maintain, correct, and defend place-proof without surrendering excessive commercial information.

### NVD / vulnerability enrichment and status afterlife

NVD's risk-based enrichment shift is a live case of database authority becoming status-aware: not every listed record receives the same enrichment, and downstream users must distinguish raw listing, prioritized enrichment, known exploitation, deferral, and local vendor assertion.

### AI / data-center energy and queue governance

Data-center electricity demand turns grid-connection position, curtailment terms, protected-load status, storage commitments, and power-quality obligations into strategic assets. The relevant cube lane is not simply compute or energy; it is queue position becoming industrial policy.

## rev0186 authority-lifecycle graph spine

The authority refactor adds a lifecycle spine:

`delegated-representation` → `authority-scope-crosswalks` → `authority-check-middleware` → `representative-of-record-ledgers` → `standing-and-representation-proofs`.

Two side spines matter:

- organizational authority: `organizational-identity` → `legal-person-wallets` → `data-space-access-rules`;
- agentic authority: `capability-token-provenance` → `delegated-ai-agent-authority-logs`.

The abuse layer is explicit: `safeguarded-delegation` → `proxy-abuse-telemetry` ↔ `representation-risk-telemetry`.

Future graph edits should avoid adding every portal-specific authorization case. Add edges only when a dossier changes the lifecycle state, evidence object, verifier, or failure mode.
