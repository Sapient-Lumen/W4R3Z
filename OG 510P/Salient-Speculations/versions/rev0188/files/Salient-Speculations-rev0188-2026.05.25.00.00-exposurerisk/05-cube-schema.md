# Cube Schema

This revision separates the archive's **controlled cube** from its large and generative **primitive inventory**.

The old cube grew by accretion. That was useful while the archive was discovering its center of gravity, but it also made the substrate axis absorb substrates, actors, artifact names, lifecycle states, status labels, and examples. The result was expressive but hard to query. This file is the working schema for future revisions.

## Design rule

A speculation should now be recorded as a state-changing mechanism:

> **In domain D, bottleneck B hardens through enforcement surface E, creating artifact A at lifecycle stage L; actor X operates or arbitrates it; failure mode F makes the artifact valuable; adversarial pressure P and distributional burden Q determine whether it becomes legitimate.**

That sentence is the minimum useful shape.

## Required dossier fields

Future dossiers should be classifiable by these fields. They do not need to appear as literal YAML in every old file yet, but the archive should migrate toward this structure.

```yaml
id: ss-0180-example-title
title: Example title becomes an institutional bottleneck
revision_promoted: rev0180
constellation:
  - managed-legibility
  - administrative-repair
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near

domain:
  - diligence-packets
  - procurement
  - cyber-risk

bottleneck_type:
  - interim-reliance-authority
  - correction-propagation

enforcement_surface:
  - procurement
  - underwriting
  - covenant
  - platform-eligibility

artifact_type:
  - state-label
  - notice
  - registry-entry
  - replay-bundle

lifecycle_stage:
  - publish
  - rely
  - dispute
  - stay
  - correct
  - retire

primary_actors:
  - broker
  - buyer
  - insurer
  - lender
  - source-vendor

failure_modes:
  - stale-state
  - false-join
  - strategic-delay
  - nonpropagation
  - spoofed-proof

adversarial_pressure:
  - forged-artifact
  - graph-poisoning
  - silence-as-leverage
  - overbroad-disclosure

distributional_effect:
  - small-supplier-burden
  - incumbent-compliance-advantage
  - buyer-side-information-leverage

graph_edges:
  precondition_of: []
  sequel_to: []
  imports_pattern_from: []
  weakens: []
  same_failure_mode_as: []
```

## Controlled values

These are intentionally finite. New values should be added slowly and only when several dossiers need them.

### Domain / substrate

- energy / grid / flexible load
- water / basin / allocation
- land / parcel / place-proof
- climate / retreat / habitability
- compute / AI / data centers
- cyber / software supply chain / vulnerability governance
- product identity / passports / traceability
- identity / credentials / delegated authority
- organizational identity / entity resolution
- standards / interoperability / conformance
- procurement / purchasing / offtake
- insurance / risk transfer / underwriting
- finance / payments / settlement
- waste / remediation / decommissioning
- healthcare / biological observability / diagnostics
- care / ageing / household capacity
- education / capability formation
- civic services / casework / appeals
- communication / emergency reachability
- logistics / cold chain / physical continuity
- simulation / forecasting / counterfactual capacity
- urban systems / municipal reliability

### Bottleneck type

- clearance latency
- admissible evidence
- source-of-truth precedence
- state freshness
- correction throughput
- appealability / redress
- interim reliance authority
- recipient-scope precision
- provenance / custody
- replayability / reconstructability
- conformance capacity
- interoperability translation
- version / support-window compatibility
- registry coverage
- identity matching
- allocation priority
- queue position
- underwritability
- liability-tail custody
- maintenance capacity
- fallback / graceful degradation
- selective disclosure / minimization
- fraud resistance
- small-actor evidence capacity

### Enforcement surface

- statute / regulation
- permit / license
- procurement / framework contract
- underwriting / insurance renewal
- lending covenant / credit agreement
- court / tribunal / administrative appeal
- certification / conformity assessment
- platform eligibility / ranking
- customs / market access
- subsidy / tax credit / public funding
- audit / attestation / assurance
- incident reporting
- consumer disclosure
- professional duty / malpractice exposure
- operational-resilience supervision
- title / conveyancing / property transfer
- payment / settlement access

### Artifact type

- packet
- registry entry
- state label
- notice
- appeal record
- correction record
- non-reliance marker
- certificate / attestation
- scorecard
- materiality schedule
- source snapshot
- transform recipe
- replay bundle
- recipient graph
- privacy proof
- selective-disclosure credential
- resolver / pointer
- successor map
- waiver / override
- holdback / reserve label
- due-diligence statement
- model / baseline / scenario
- audit log
- reason code

### Lifecycle stage

- source
- capture
- normalize / transform
- validate
- publish
- route
- rely
- transfer
- dispute
- stay
- investigate
- correct
- restate
- supersede
- restrict
- withdraw
- non-rely
- retire
- archive

### Actor

- state / regulator
- standards body / schema steward
- certifier / notified body / lab
- broker / platform / clearinghouse
- insurer / reinsurer
- lender / servicer
- buyer / procurement office
- seller / supplier
- source vendor / native-system owner
- auditor / assurance provider
- court / review agency / ombuds
- utility / grid operator
- customs / market-surveillance authority
- identity issuer / verifier / wallet provider
- small-supplier intermediary / cooperative
- civil-society monitor
- household / delegated representative
- field operator / maintainer

### Failure mode

- false positive
- false negative
- false join
- false split
- stale state
- missing recipient
- overbroad recipient disclosure
- nonpropagation
- spoofed notice
- forged compliance object
- replay failure
- unverifiable source
- strategic nonresponse
- strategic appeal abuse
- overbroad stay
- silent reliance revival
- stale non-reliance marker
- capture by incumbent
- small-actor exclusion
- privacy leakage
- unofficial workaround capture
- fail-closed exclusion
- fail-open liability
- version drift
- clock mismatch
- retention gap
- ambiguous source precedence

### Maturity scale

- **S0 — evocative seed.** The phrase is interesting, but the archive has not yet found a strong institutional mechanism.
- **S1 — signal cluster.** Multiple signals point in the same direction, but the artifact is not stable.
- **S2 — artifact emerging.** Named objects, schemas, reports, labels, or service roles are visible.
- **S3 — enforcement surface.** The artifact begins gating money, permission, ranking, access, liability, or compliance.
- **S4 — infrastructure.** Multiple institutions depend on it; failure becomes an incident, market disruption, or supervisory concern.
- **S5 — constitutional layer.** Conflict rules, appeal rights, fallback authority, and legitimacy fights become central.

## Required reasoning sections for new dossiers

Every promoted dossier should include, explicitly or implicitly:

1. **Core claim.** What state changes, not merely what noun appears.
2. **Why this belongs.** Why the bottleneck is broad and asymmetric.
3. **Speculative consequences.** What institutions or markets would do differently.
4. **Artifact shape.** What the object looks like when mature.
5. **Who pays / who saves / who captures.** Incentive model.
6. **How this gets abused.** Fraud, delay, capture, privacy leakage, exclusion, or overreach.
7. **Near misses.** What looks similar but is not the thesis.
8. **Falsifiers.** How the archive would know the thesis is overextended.
9. **Research queue.** What to track next.

## Near-miss rules

- A dashboard is not governance unless someone is required to act on it.
- A schema is not infrastructure unless refusal or failure changes access.
- A certificate is not a bottleneck unless it gates money, permission, liability, or ranking.
- A right is not operational unless there is a funded route to exercise it.
- A registry is not a source of truth unless conflict rules say it wins.
- A privacy proof is not useful unless a verifier accepts less disclosure as sufficient.
- A warning is not a notice unless delivery, timing, authenticity, and recipient scope matter.
- A correction is not material unless it changes reliance, price, eligibility, liability, or duty to route.

## Migration plan

1. Add YAML front matter to new dossiers first.
2. Backfill old dossiers only when they are touched for substantive reasons.
3. Maintain a graph file rather than trying to force every edge into prose.
4. Keep the old cube lists as a primitive bank, but stop treating them as controlled axes.
5. Add no new primitive unless it names a state transition, artifact, enforcement surface, or failure mode not already expressible by the schema above.


## rev0182 additional fields

rev0182 adds optional stress fields for future front matter.

```yaml
attack_surface:
  - forgery
  - laundering
  - stale-proof-reuse
  - subject-mismatch
  - issuer-compromise
  - resolver-capture
  - graph-poisoning
  - nonresponse-leverage
  - redaction-abuse
  - trust-anchor-failure
burden_surface:
  - small-supplier-evidence-capacity
  - over-disclosure-pressure
  - appeal-cost
  - credential-exclusion
  - low-connectivity-access
  - proprietary-tooling-dependency
minimum_sufficient_proof:
  profile: <name or TBD>
  forbidden_overcollection:
    - <attribute/category>
falsifier:
  - <observable condition that would weaken the thesis>
```

These fields are not required for every older dossier. They should be required for newly promoted proof-object, passport, credential, model-assurance, incident-routing, and reliance-packet dossiers.


## rev0183 schema additions

### New optional fields

```yaml
evidence_grade: E3-artifact-live
decision_grade: DG-B
review_bucket: source-refresh-needed
decision_surfaces:
  - procurement language
  - audit checklist
  - product architecture
overconfidence_risk: Treating pilot artifacts as enforced infrastructure.
next_verification_move: Search for buyer templates, regulator guidance, public registry fields, or incident cases.
consolidation_risk: Could be merged into evidence-freshness model.
```

### New controlled values added by rev0183

Domains:

- cryptography / trust infrastructure
- medical devices / conformity capacity
- data spaces / data sharing
- media / content provenance / attention markets
- consumer services / transactions / redress

Bottleneck types:

- delegated authority
- market-access timing
- algorithm transition
- assessor capacity
- verifier sufficiency

Enforcement surfaces:

- data-space participation
- content provenance / platform moderation
- notified-body assessment

Artifact types:

- authority log
- consent receipt
- tool-call record
- participation profile
- access policy
- data-use receipt
- trust framework
- transition plan
- exception record
- provenance label
- nonparticipation marker
- manifest
- queue-state record

Failure modes:

- algorithm-obsolescence
- hidden-dependency
- false-migration-claim
- assessor-bottleneck
- incomplete-file
- scope-mismatch
- authority-spoofing
- consent-drift
- policy-translation-loss
- intermediary-capture
- provenance-strip
- false-nonparticipation
- legacy-content-misclassification
## rev0184 optional schema extension: freshness fields

For dossiers in the evidence-freshness family, front matter may include:

```yaml
refactor_cluster:
  - evidence-freshness
freshness_role: cache-age and validation-age disclosure
consolidation_status: standalone-mechanism | bridge-dossier | model-substate
state_family:
  - freshness
state_terms:
  - valid-cached
  - stale-if-error
  - revalidation-due
freshness_clock:
  - source_observed_at
  - validated_at
  - relied_at
```

These fields are intentionally optional outside proof/state-object dossiers. They should not become universal metadata bloat.


## rev0186 schema extension: authority-lifecycle fields

Dossiers in the authority/delegation/proxy family may use:

```yaml
refactor_cluster:
  - authority-lifecycle
authority_role: scope-translator and verifier-relying-party
authority_stage:
  - grant
  - scope
  - verify
state_family:
  - authority
state_terms:
  - scope-limited
  - revocation-pending
```

Recommended `authority_stage` values:

`define`, `grant`, `bind`, `scope`, `publish`, `present`, `verify`, `act`, `log`, `revoke`, `propagate`, `fallback`, `dispute`, `audit`.

Recommended `state_terms` values are defined in `27-authority-state-vocabulary.md`.


## rev0187 schema addition: lineage fields

New optional dossier fields:

```yaml
refactor_cluster:
  - provenance-lineage
lineage_role: transformer-broker and verifier-relying-party
lineage_stage:
  - capture
  - transform
  - replay
state_family:
  - provenance
state_terms:
  - snapshot-captured
  - transform-replayable
  - replay-sufficient
```

Use `lineage_stage` when the dossier turns on origin, custody, transformation, package, signature, resolver, disclosure, redaction, transfer, diff, replay, verification, correction, supersession, or archive state. Use `lineage_role` to clarify whether the main actor is a source issuer, transformer broker, resolver operator, registry steward, signer, redactor, auditor, relying party, rights holder, or evidence broker.

## rev0188 schema extension: exposure

New optional dossier fields:

```yaml
exposure_role: carrier-broker and risk-manager
exposure_stage:
  - trigger
  - classify
  - notify
  - reserve
state_family:
  - exposure
state_terms:
  - coverage-position-reserved
  - reserve-held
  - subrogation-preserved
```

Use these fields when the dossier changes loss allocation, coverage response, indemnity, reserve, limit, renewal, or recovery rights.
