# 280 — Governance Systems Index and Memo Attachment Guide

**Purpose:** make the archive’s ten-system architecture concrete enough that future merge work can attach memos to the right home instead of generating near-duplicates.

**How to use this memo:** when a file feels “similar” to another file, first ask whether the similarity comes from:
1. shared values,
2. a shared failure mode,
3. a shared implementation surface,
4. or a truly duplicate conceptual role.

Most of the archive’s apparent duplication is really **cross-system adjacency**, not exact duplication. This index names the primary home for each major cluster so future revisions stay tighter.

---

## 1. Legitimacy System

**Canonical question:** why should people accept this institution or decision as rightful rather than merely imposed?

**Primary anchors**
- `21-legitimacy-architecture.md`
- `56-elections-and-electoral-administration.md`
- `147-representation-and-electoral-system-choice.md`
- `180-legitimacy-engines-elections-sortition-deliberation-recall.md`
- `284-deliberation-stack-binding-and-legitimacy-guide.md`

**Key supporting modules**
- `88-deliberative-institutions-and-sortition.md`
- `111-deliberation-to-decision-binding.md`
- `119-selection-and-sortition-integrity.md`
- `123-association-and-collective-power.md`
- `141-delegation-and-representation-integrity.md`
- `143-deliberative-systems-and-citizens-assemblies.md`
- `159-civic-lottery-and-deliberation-infrastructure.md`
- `224-deliberative-processes-and-citizens-assemblies-rails.md`

**Usual confusion boundary**
- If the memo is about **who gets to decide and why that is accepted**, it belongs here.
- If it is about **how the decision is executed**, it probably belongs in the Decision or Implementation System.

---

## 2. Decision System

**Canonical question:** how are public choices formed, authorized, versioned, and bounded?

**Primary anchors**
- `118-rulemaking-and-change-control.md`
- `215-legislative-process-and-drafting-rails.md`
- `216-regulatory-impact-assessment-and-ex-post-review-rails.md`
- `206-constitutional-change-and-amendment-rails.md`

**Key supporting modules**
- `23-emergency-governance-and-exceptions.md`
- `112-exception-control-and-emergency-powers.md`
- `165-emergency-powers-derogation-sunsets-rails.md`
- `171-constitutional-maintenance-and-amendment-ops.md`
- `205-constitutional-review-observability-and-precedent-ledgers.md`
- `207-sunset-review-and-rollback-rails.md`

**Usual confusion boundary**
- Decision memos govern **choice architecture, authority thresholds, and change control**.
- Crisis memos are adjacent, but if the core issue is **how extraordinary decisions are authorized**, start here.

---

## 3. Implementation System

**Canonical question:** how do public decisions become actual service delivery, enforcement, infrastructure, and operating reality?

**Primary anchors**
- `09-public-service-and-state-capacity.md`
- `22-public-integrity-and-procurement.md`
- `82-service-standards-and-minimum-service-guarantees.md`
- `108-service-standards-and-time-budgets.md`
- `219-shared-services-and-federated-administration-rails.md`

**Key supporting modules**
- `29-permissioning-and-approvals.md`
- `38-contracting-and-procurement-register.md`
- `93-tax-and-revenue-administration.md`
- `97-public-investment-and-capital-project-governance.md`
- `110-budget-procurement-integrity.md`
- `138-public-investment-and-capital-projects-integrity.md`
- `225-public-assets-maintenance-and-capital-planning-rails.md`

**Usual confusion boundary**
- If the memo is about **queues, deadlines, continuity, operators, handoffs, or procurement seams**, it belongs here.
- If it is primarily about **anti-capture or oversight**, route to Oversight.

---

## 4. Oversight System

**Canonical question:** how do we discover abuse, follow up, and force correction?

**Primary anchors**
- `32-oversight-institutions-and-follow-through.md`
- `55-oversight-findings-and-response-register.md`
- `130-audit-and-inspection-integrity.md`
- `226-public-integrity-system-architecture.md`
- `231-supreme-audit-institutions-and-public-accounts-rails.md`

**Key supporting modules**
- `79-conflict-of-interest-and-revolving-door-discipline.md`
- `120-conflicts-of-interest-and-influence-integrity.md`
- `121-whistleblowing-and-protected-disclosure.md`
- `181-influence-lobbying-transparency-and-integrity-rails.md`
- `183-governance-observability-and-public-audits.md`
- `187-public-integrity-system-blueprint.md`
- `227-prosecutorial-and-disciplinary-integrity-rails.md`

**Usual confusion boundary**
- If the memo is about **finding, disclosing, or escalating wrongdoing**, it belongs here.
- If it is about **remedying a harmed person’s case**, route to Justice & Redress.

---

## 5. Justice & Redress System

**Canonical question:** what can a person do when government gets it wrong, and how does correction actually propagate?

**Primary anchors**
- `08-remedy-and-grievance.md`
- `36-appeal-lanes-and-redress-registry.md`
- `76-systemic-redress-and-pattern-remediation.md`
- `195-dispute-resolution-escalation-and-odr-rails.md`
- `283-justice-and-redress-stack-routing-guide.md`

**Key supporting modules**
- `115-information-integrity-and-record-interfaces.md`
- `82-service-standards-and-minimum-service-guarantees.md`
- `98-persons-path-and-accessibility-invariants.md`
- `121-whistleblowing-and-protected-disclosure.md`
- `193-restorative-justice-and-conflict-resolution-rails.md`
- `200-freedom-of-information-and-access-to-official-documents-rails.md`

**Usual confusion boundary**
- If the center of gravity is a **person-path, appeal lane, or correction duty**, it belongs here.
- If it is about **general compliance or inspections**, route to Oversight.

---

## 6. Crisis Governance System

**Canonical question:** how do institutions handle severe time pressure without blowing through legitimacy, rights, or recoverability?

**Primary anchors**
- `23-emergency-governance-and-exceptions.md`
- `24-mutual-aid-and-serious-incident-protocol.md`
- `57-public-health-and-biosecurity-governance.md`
- `165-emergency-powers-derogation-sunsets-rails.md`
- `234-public-health-preparedness-and-response-rails.md`

**Key supporting modules**
- `05-public-safety-and-coercion.md`
- `63-climate-adaptation-and-disaster-risk-governance.md`
- `192-dualuse-research-and-biosecurity-oversight.md`
- `232-corrections-and-incarceration-governance.md`
- `233-policing-and-use-of-force-governance-rails.md`

**Usual confusion boundary**
- If the issue is **time-compressed state power under danger**, it belongs here.
- If the issue is mainly **ordinary constitutional change control**, route back to Decision.

---

## 7. Inter-Jurisdiction Coordination System

**Canonical question:** how do people and institutions survive borders, handoffs, and overlapping authority without losing rights or legibility?

**Primary anchors**
- `17-jurisdiction-formation-and-boundaries.md`
- `19-compacts-and-cooperative-governance.md`
- `109-portability-and-cross-jurisdiction-continuity.md`
- `114-interjurisdictional-dispute-and-coordination.md`
- `230-conflict-of-laws-and-cross-border-dispute-rails.md`

**Key supporting modules**
- `40-national.md`
- `197-polycentric-federalism-and-overlapping-sovereignty.md`
- `182-polycentric-governance-and-compacts.md`
- `194-fiscal-federalism-open-budgets-and-participation-rails.md`
- `197-polycentric-federalism-and-overlapping-sovereignty.md`
- `217-intergovernmental-fiscal-transfers-and-equalization-rails.md`
- `170-watershed-and-water-governance-compacts.md`

**Usual confusion boundary**
- If the memo is about **seams between authorities**, it belongs here.
- If it is about a **local service implementation seam**, it may belong in Implementation instead.

---

## 8. Evidence & Metrics System

**Canonical question:** what must be measured, published, tested, and made legible so governance is verifiable rather than theatrical?

**Primary anchors**
- `03-metrics-and-evidence.md`
- `28-program-register-and-evaluation-commitments.md`
- `142-metrics-and-indicators-integrity.md`
- `184-official-statistics-and-census-integrity.md`
- `214-evaluation-learning-agendas-and-evidence-governance-rails.md`

**Key supporting modules**
- `37-claims-evidence-and-update-discipline.md`
- `42-automated-decision-systems-and-model-registry.md`
- `51-release-registry.md`
- `53-publication-integrity-and-tamper-evident-logs.md`
- `190-policy-experimentation-and-evidence-rails.md`
- `191-algorithmic-systems-registry-and-audit-rails.md`
- `202-open-knowledge-evidence-commons-and-scientific-integrity-rails.md`

**Usual confusion boundary**
- If the memo’s point is **measurement, publication, evaluation, or evidence discipline**, it belongs here.
- If it is about **how a person corrects an error using those records**, route to Justice & Redress.

---

## 9. Institutional Learning System

**Canonical question:** how does a governance system remember, train, compare, and improve instead of repeating avoidable harm?

**Primary anchors**
- `133-evaluation-and-learning-integrity.md`
- `177-governance-failure-taxonomy-and-recovery-ops.md`
- `220-civic-learning-and-democratic-maintenance-infrastructure.md`
- `276-worked-example-system-consolidated.md`

**Key supporting modules**
- `235-worked-examples-and-trace-walkthroughs.md`
- `237-worked-example-quick-reference-and-training-drills.md`
- `238-worked-example-failure-signatures-and-cross-case-patterns.md`
- `239-worked-example-counterfactuals-and-minimum-viable-fixes.md`
- `240-worked-example-evidence-packets-and-review-views.md`
- `241-worked-example-tabletop-exercises-and-audit-scripts.md`
- `242-worked-example-comparison-cuts-and-starter-packets.md`
- `243-worked-example-quality-bar-and-red-team-lints.md`
- `244-worked-example-atlas-and-retrieval-index.md`
- `245-worked-example-sequence-builder-and-themed-reading-packs.md`
- `246-worked-example-role-based-field-manual-packs.md`
- `247-worked-example-implementation-bridge-and-retrofit-sequences.md`
- `274-worked-example-to-domain-crosswalk.md`
- `278-worked-example-system-architecture.md`

**Usual confusion boundary**
- If the memo is about **training, examples, retrospectives, or portable lessons**, it belongs here.
- If it actually defines new institutional structure, it may belong in Reform / Retrofit.

---

## 10. Institutional Reform / Retrofit System

**Canonical question:** how do we change institutions without losing continuity, legitimacy, or implementation reality?

**Primary anchors**
- `80-implementation-roadmap.md`
- `171-constitutional-maintenance-and-amendment-ops.md`
- `178-institutional-lifecycle-sunsets-and-scrutiny.md`
- `208-change-management-and-release-engineering-for-government.md`

**Key supporting modules**
- `74-sunsetting-and-deprecation-discipline.md`
- `99-protective-legibility-and-adoption-dynamics.md`
- `166-managed-retreat-and-planned-relocation.md`
- `201-futures-and-intergenerational-governance-institutions.md`
- `206-constitutional-change-and-amendment-rails.md`
- `207-sunset-review-and-rollback-rails.md`
- `247-worked-example-implementation-bridge-and-retrofit-sequences.md`

**Usual confusion boundary**
- If the memo is about **migration, sequencing, rollback, or deprecation**, it belongs here.
- If it is about the steady-state design of an institution, route to the relevant system instead.

---

## Merge discipline rules for future revisions

### A. Before creating a new memo
Ask:
1. Does the concept already have a **system home** here?
2. Is the missing value a **new implementation layer** or only a better explanation of an existing memo?
3. Should the change be a **cross-reference, addendum, or canonicalization note** instead of a new file?

### B. Before deleting an overlapping memo
Do **not** delete until you can state the relationship explicitly:
- architecture vs rails,
- person-path vs institution-path,
- steady-state vs crisis mode,
- evidence vs remedy,
- design theory vs worked example.

### C. Canonicalization preference
Prefer:
1. **one canonical anchor**,
2. **one bridge / crosswalk** if needed,
3. **many modules**, only when they play distinct roles.

That pattern preserves salience while reducing merge regret.


---

**Navigation hygiene note:** after renumbering or canonicalization work, run the reference-integrity pass in `282-reference-integrity-and-canonical-link-remediation.md` before treating a memo as duplicate or obsolete.
