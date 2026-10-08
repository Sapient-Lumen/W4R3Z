# 281 — Semantic Dedupe Backlog and Canonicalization Targets

**Purpose:** record the highest-value remaining overlap clusters so future merge work is deliberate instead of impulsive.

**Standard:** do not collapse a cluster just because cosine similarity is high. Collapse it only when the archive can clearly preserve:
- the best retrieval hook,
- the best implementation hook,
- and the best person-facing explanation.

---

## Tier 1 — ready for controlled canonicalization

### 1. Worked-example architecture duplicates
**Files**
- `276-worked-example-system-consolidated.md`
- `278-worked-example-system-architecture.md`

**Diagnosis**
These had become near-duplicates. In rev445, `276` remains the canonical subsystem architecture, while `278` is narrowed into a map-attachment memo.

**Status**
- resolved enough for now
- do not re-expand `278` into a second architecture memo

---

### 2. Bibliography split
**Files**
- `90-bibliography.md`
- `91-bibliography-extended.md`
- `277-bibliography-canonicalization.md`

**Diagnosis**
This is not a conceptual problem anymore, only a maintenance problem. `91` is the canonical bibliography; `90` should remain a trimmed core set, not regrow into a competing reference corpus.

**Recommended next move**
- keep `90` short and stable
- put new keys in `91` by default

---

## Tier 2 — high overlap, but still distinct enough to preserve

### 3. Justice / grievance / redress cluster
**Files**
- `08-remedy-and-grievance.md`
- `36-appeal-lanes-and-redress-registry.md`
- `76-systemic-redress-and-pattern-remediation.md`
- `195-dispute-resolution-escalation-and-odr-rails.md`

**Why it feels duplicative**
All four live on the same person-path.

**Why it is not yet safe to collapse**
- `08` is the normative and architectural front door
- `36` is the lane/register implementation layer
- `76` handles pattern-level remediation
- `195` handles escalation and ODR routing

**Recommended next move**
Create a short crosswalk or shared glossary, not a destructive merge.

**rev447 action**
- added `283-justice-and-redress-stack-routing-guide.md` as the canonical bridge memo for this cluster
- added stack-relation notes to `08`, `36`, `76`, and `195`

---

### 4. Deliberation / assembly / legitimacy cluster
**Files**
- `88-deliberative-institutions-and-sortition.md`
- `111-deliberation-to-decision-binding.md`
- `143-deliberative-systems-and-citizens-assemblies.md`
- `159-civic-lottery-and-deliberation-infrastructure.md`
- `180-legitimacy-engines-elections-sortition-deliberation-recall.md`
- `224-deliberative-processes-and-citizens-assemblies-rails.md`

**Why it feels duplicative**
All six can surface on the same search query.

**Why it is not yet safe to collapse**
They cover different layers:
- theory of deliberative systems,
- selection infrastructure,
- anti-theater binding rules,
- legitimacy stack,
- and concrete process rails.

**Recommended next move**
One compact “deliberation stack” memo that names the roles of each file without deleting them.

**rev447 action**
- added `284-deliberation-stack-binding-and-legitimacy-guide.md` as the canonical bridge memo for this cluster
- added stack-relation notes to `88`, `111`, `143`, `159`, `180`, and `224`

---

### 5. Emergency / exception cluster
**Files**
- `23-emergency-governance-and-exceptions.md`
- `112-exception-control-and-emergency-powers.md`
- `165-emergency-powers-derogation-sunsets-rails.md`
- `186-emergency-powers-derogations-and-sunset-discipline.md`
- `234-public-health-preparedness-and-response-rails.md`

**Why it feels duplicative**
These all govern exceptional state action.

**Why it is not yet safe to collapse**
- `23` is the broad system frame
- `112` is the generic exception-control kernel
- `165` is the stronger modern emergency-powers rail
- `186` is the narrower discipline companion
- `234` is public-health-specific operating practice

**Recommended next move**
Merge only if a future editor can preserve the general-purpose kernel plus the public-health specialization.

**rev449 action**
- added `286-emergency-powers-stack-and-exit-governance-guide.md` as the canonical bridge memo for this cluster
- added stack-relation notes to `23`, `112`, `165`, `186`, and `234`

### 5b. Public health / preparedness / biosecurity cluster
**Files**
- `57-public-health-and-biosecurity-governance.md`
- `234-public-health-preparedness-and-response-rails.md`
- `192-dualuse-research-and-biosecurity-oversight.md`
- `165-emergency-powers-derogation-sunsets-rails.md`
- `61-public-communication-and-information-integrity.md`

**Why it feels duplicative**
All five can surface on the same “pandemic governance” or “biosecurity” query.

**Why it is not yet safe to collapse**
- `57` is the cross-scope governance front door
- `234` is the preparedness/response operating pack
- `192` is the research/lab biosecurity extension
- `165` is the general emergency-powers neighbor
- `61` is the public-communication and correction-integrity neighbor

**Recommended next move**
Handled in rev453 by adding a compact bridge memo and routing notes; keep the cluster distinct unless a future editor can preserve cross-scope governance, response operations, research/lab oversight, emergency-law discipline, and communication integrity as separate retrieval hooks.

**rev453 action**
- added `291-public-health-preparedness-and-biosecurity-routing-guide.md` as the canonical bridge memo for this cluster
- added routing notes to `57`, `192`, `234`, and `61`

---

### 6. DPI / identity / trust framework cluster
**Files**
- `160-digital-identity-credentials-privacy-utility.md`
- `164-digital-public-infrastructure-governance.md`
- `188-digital-public-infrastructure-governance.md`
- `210-digital-identity-and-credentialing-rails.md`
- `211-privacy-preserving-federation-and-consent-ledgers.md`
- `212-dpi-trust-framework-and-interop-governance.md`
- `213-digital-public-goods-intake-and-certification-rails.md`

**Why it feels duplicative**
Shared language: trust, identity, public infrastructure, interoperability.

**Why it is not yet safe to collapse**
This cluster spans at least four distinct roles:
- public-utility governance,
- identity and personhood utility,
- trust / certification,
- and procurement / intake rules.

**Recommended next move**
A shared glossary and a single “DPI family map” memo would help more than deletion.

**rev449 action**
- added `287-dpi-identity-and-trust-family-map.md` as the canonical bridge memo for this family
- added stack-relation notes to `160`, `164`, `188`, `210`, `211`, `212`, and `213`

---

## Tier 3 — likely cross-system adjacency rather than duplication

### 7. Integrity cluster
**Files**
- `22-public-integrity-and-procurement.md`
- `120-conflicts-of-interest-and-influence-integrity.md`
- `130-audit-and-inspection-integrity.md`
- `163-integrity-stack-anti-corruption-rails.md`
- `181-influence-lobbying-transparency-and-integrity-rails.md`
- `187-public-integrity-system-blueprint.md`
- `226-public-integrity-system-architecture.md`
- `227-prosecutorial-and-disciplinary-integrity-rails.md`

**Judgment**
This cluster is now easier to preserve as a healthy stack: procurement/capture, conflict and disclosure controls, oversight/inspection, compact anti-corruption rails, influence transparency, architecture, and enforcement integrity.

**Recommended next move**
Handled in rev451 by adding a compact bridge memo and routing notes. Keep the cluster distinct unless a future editor can preserve architecture, procurement/capture, influence transparency, compact rails, and enforcement integrity as separate retrieval hooks.

**rev451 action**
- added `289-public-integrity-stack-and-enforcement-routing-guide.md` as the canonical bridge memo for this cluster
- added routing notes to `22`, `120`, `130`, `163`, `181`, `187`, `226`, and `227`

---

### 8. Constitutional change cluster
**Files**
- `124-constitutional-amendment-and-entrenchment.md`
- `171-constitutional-maintenance-and-amendment-ops.md`
- `205-constitutional-review-observability-and-precedent-ledgers.md`
- `206-constitutional-change-and-amendment-rails.md`

**Judgment**
High adjacency, but distinct roles: entrenchment theory, maintenance cadence, review observability, and change-event rails.

**Recommended next move**
Handled in rev450 by adding a compact bridge memo and stack-relation notes; keep the cluster distinct unless a future editor can preserve amendment-event rails, standing maintenance, entrenchment theory, and review observability as separate retrieval hooks.

**rev450 action**
- added `288-constitutional-change-maintenance-and-review-stack-guide.md` as the canonical bridge memo for this cluster
- added routing notes to `124`, `171`, `205`, and `206`

---

## Tier 3 — likely cross-system adjacency rather than duplication

### 9. Evidence / statistics / publication-integrity cluster
**Files**
- `03-metrics-and-evidence.md`
- `28-program-register-and-evaluation-commitments.md`
- `37-claims-evidence-and-update-discipline.md`
- `51-release-registry.md`
- `53-publication-integrity-and-tamper-evident-logs.md`
- `142-metrics-and-indicators-integrity.md`
- `184-official-statistics-and-census-integrity.md`
- `190-policy-experimentation-and-evidence-rails.md`
- `202-open-knowledge-evidence-commons-and-scientific-integrity-rails.md`
- `214-evaluation-learning-agendas-and-evidence-governance-rails.md`

**Judgment**
High adjacency, but distinct roles: minimal measurement loops, institutional evidence governance, program-level commitments, experimentation, official statistics, open-science/evidence commons, metric governance, and publication integrity.

**Recommended next move**
Handled in rev452 by adding a compact bridge memo and stack-relation notes; keep the cluster distinct unless a future editor can preserve measurement-from-below, institutional evidence governance, official-statistics independence, experimentation, evidence-commons design, and publication integrity as separate retrieval hooks.

**rev452 action**
- added `290-evidence-statistics-and-publication-integrity-routing-guide.md` as the canonical bridge memo for this cluster
- added routing notes to `03`, `28`, `37`, `51`, `53`, `142`, `184`, `190`, `202`, and `214`

### 10. Coercion / policing / custody / non-carceral cluster
**Files**
- `05-public-safety-and-coercion.md`
- `116-coercion-use-of-force-and-detention-governance.md`
- `233-policing-and-use-of-force-governance-rails.md`
- `232-corrections-and-incarceration-governance.md`
- `193-restorative-justice-and-conflict-resolution-rails.md`

**Judgment**
High adjacency, but distinct roles: minimum-violence public-safety frame, portable coercion protocol, policing specialization, custody/corrections specialization, and the non-carceral / restorative neighbor.

**Recommended next move**
Handled in rev454 by adding a compact bridge memo and routing notes. Keep the cluster distinct unless a future editor can preserve coercion-front-door framing, force/detention protocol, policing operations, custody governance, and restorative/non-carceral alternatives as separate retrieval hooks.

**rev454 action**
- added `292-coercion-custody-and-public-safety-routing-guide.md` as the canonical bridge memo for this cluster
- added routing notes to `05`, `116`, `233`, `232`, and `193`


### 11. Secrecy / intelligence / war powers cluster
**Files**
- `77-sensitive-information-and-secrecy-governance.md`
- `168-intelligence-and-secrecy-governance.md`
- `222-war-powers-and-external-use-of-force-governance.md`

**Judgment**
High adjacency, but distinct roles: general secrecy and withholding discipline, intelligence / surveillance oversight, and external-force / war-powers governance.

**Recommended next move**
Handled in rev455 by adding a compact bridge memo and routing notes. Keep the cluster distinct unless a future editor can preserve general secrecy discipline, intelligence oversight, war-authority design, requester-side access-to-documents routing, and emergency-law adjacency as separate retrieval hooks.

**rev455 action**
- added `293-secrecy-intelligence-and-war-powers-routing-guide.md` as the canonical bridge memo for this cluster
- added routing notes to `77`, `168`, and `222`

### 12. Climate resilience / infrastructure / retreat / risk-finance cluster
**Files**
- `63-climate-adaptation-and-disaster-risk-governance.md`
- `154-critical-infrastructure-resilience-compacts.md`
- `166-managed-retreat-and-planned-relocation.md`
- `169-resilience-finance-risk-pooling-and-catastrophe-rails.md`
- `170-watershed-and-water-governance-compacts.md`
- `11-commons-and-ecological-governance.md`

**Judgment**
High adjacency, but distinct roles: cross-scope adaptation / DRR governance, infrastructure continuity and operator compacts, managed retreat / relocation, disaster-risk finance, watershed governance, and ecological ceilings / standing.

**Recommended next move**
Handled in rev456 by adding a compact bridge memo and routing notes. Keep the cluster distinct unless a future editor can preserve adaptation / DRR front-door framing, infrastructure continuity, retreat / relocation design, catastrophe-finance design, and water / ecological neighbors as separate retrieval hooks.

**rev456 action**
- added `294-climate-resilience-infrastructure-retreat-and-risk-finance-routing-guide.md` as the canonical bridge memo for this cluster
- added routing notes to `63`, `154`, `166`, and `169`

### 13. Public information / media / access cluster
**Files**
- `129-public-sphere-and-epistemic-infrastructure.md`
- `161-information-commons-and-public-media-governance.md`
- `61-public-communication-and-information-integrity.md`
- `200-freedom-of-information-and-access-to-official-documents-rails.md`
- `77-sensitive-information-and-secrecy-governance.md`
- `115-information-integrity-and-record-interfaces.md`
- `31-records-foi-and-government-memory.md`
- `53-publication-integrity-and-tamper-evident-logs.md`

**Judgment**
High adjacency, but distinct roles: public-sphere integrity, media/pluralism and platform structure, official communication discipline, requester-side ATI / FOI access, secrecy-boundary design, and the records/provenance substrate.

**Recommended next move**
Handled in rev457 by adding a compact bridge memo and routing notes. Keep the cluster distinct unless a future editor can preserve public-sphere integrity, media/pluralism governance, official communication discipline, requester-side access, secrecy-boundary design, and records/provenance guarantees as separate retrieval hooks.

**rev457 action**
- added `295-public-information-media-and-access-routing-guide.md` as the canonical bridge memo for this cluster
- added routing notes to `61`, `129`, `161`, and `200`


### 14. Status / identity / portability / mobility cluster
**Files**
- `12-identity-and-recognition.md`
- `125-identity-membership-and-civil-status.md`
- `109-portability-and-cross-jurisdiction-continuity.md`
- `67-migration-and-mobility-governance.md`
- `203-mutual-recognition-of-credentials-licenses-and-status.md`
- `158-child-family-separation-and-alternative-care-governance.md`
- `287-dpi-identity-and-trust-family-map.md`

**Judgment**
High adjacency, but distinct roles: person recognition, civil-status / membership power, continuity across seams, migration-status procedure, mutual recognition, family-unity constraints, and the digital implementation family.

**Recommended next move**
Handled in rev458 by adding a compact bridge memo and routing notes. Keep the cluster distinct unless a future editor can preserve person-recognition design, status receipts, anti-cliff continuity, migration-status procedure, mutual-recognition logic, family-unity protections, and digital-identity implementation as separate retrieval hooks.

**rev458 action**
- added `296-status-identity-portability-and-mobility-routing-guide.md` as the canonical bridge memo for this cluster
- added routing notes to `12`, `125`, `109`, `67`, `203`, and `158`

### 15. State capacity / appointments / agency independence cluster
**Files**
- `09-public-service-and-state-capacity.md`
- `113-appointments-and-tenure-integrity.md`
- `199-civil-service-merit-and-capacity-rails.md`
- `228-public-appointments-and-board-governance-rails.md`
- `229-independent-regulators-and-agency-independence-rails.md`

**Judgment**
High adjacency, but distinct roles: broad state-capacity framing, personnel-power integrity, merit/workforce rails, board and public-appointments specialization, and agency/regulator-independence specialization.

**Recommended next move**
Handled in rev459 by adding a compact bridge memo and routing notes. Keep the cluster distinct unless a future editor can preserve broad execution-capacity framing, merit-system design, appointment/tenure integrity, board-governance packets, and post-appointment agency insulation as separate retrieval hooks.

**rev459 action**
- added `297-state-capacity-appointments-and-agency-independence-routing-guide.md` as the canonical bridge memo for this cluster
- added routing notes to `09`, `113`, `199`, `228`, and `229`

### 16. Land / housing / commons / value-capture cluster
**Files**
- `62-land-and-housing-governance.md`
- `136-land-housing-and-commons-integrity.md`
- `150-land-commons-stewardship-anti-speculation.md`
- `198-commons-externalities-and-value-capture-rails.md`
- `11-commons-and-ecological-governance.md`
- `294-climate-resilience-infrastructure-retreat-and-risk-finance-routing-guide.md`

**Judgment**
High adjacency, but distinct roles: auditable planning / housing front door, parcel and commons integrity rails, anti-speculation stewardship carriers, land-uplift / externalities recapture, and the ecological / climate neighbors.

**Recommended next move**
Handled in rev460 by adding a compact bridge memo and routing notes. Keep the cluster distinct unless a future editor can preserve planning / permitting front-door retrieval, parcel-and-housing integrity, non-market stewardship carriers, value-capture fiscal design, and ecological / climate neighbor roles as separate retrieval hooks.

**rev460 action**
- added `298-land-housing-commons-and-value-capture-routing-guide.md` as the canonical bridge memo for this cluster
- added routing notes to `62`, `136`, `150`, and `198`

### 17. Social protection / skills / work / worker-voice cluster
**Files**
- `64-social-protection-and-benefits-governance.md`
- `68-education-and-skills-governance.md`
- `69-labor-and-work-governance.md`
- `175-worker-voice-sectoral-bargaining-codetermination.md`
- `123-association-and-collective-power.md`
- `203-mutual-recognition-of-credentials-licenses-and-status.md`
- `82-service-standards-and-minimum-service-guarantees.md`
- `140-queues-and-prioritization-integrity.md`

**Judgment**
This family has a real retrieval problem even though the memos are not near-duplicates. Readers looking for “economic security”, “skills for work”, “decent work”, or “worker power” routinely need to move across at least four layers: material floor, capability formation, labor-market discipline, and countervailing worker voice. That is adjacency dense enough to deserve an explicit bridge memo.

**Recommended next move**
Handled in rev461 by adding a compact bridge memo and routing notes. Keep the family distinct unless a future editor can preserve income-security delivery, education / lifelong-learning governance, labor standards / enforcement, worker-voice institutions, collective-power adjacency, portability of credentials, and shared service-operation substrate as separate retrieval hooks.

**rev461 action**
- added `299-social-protection-skills-work-and-worker-voice-routing-guide.md` as the canonical bridge memo for this family
- added routing notes to `64`, `68`, `69`, and `175`

### 18. Lawmaking / rulemaking / regulatory-change cluster
**Files**
- `25-legal-legibility-and-rule-inventory.md`
- `39-rulebook-and-instruments-registry.md`
- `118-rulemaking-and-change-control.md`
- `215-legislative-process-and-drafting-rails.md`
- `317-delegated-legislation-empowering-provisions-henry-viii-powers-and-parliamentary-scrutiny-rails.md`
- `320-incorporation-by-reference-external-standards-dynamic-updates-and-public-access-rails.md`
- `316-bill-finalization-assent-promulgation-publication-commencement-and-constitutional-referral-rails.md`
- `319-statute-book-maintenance-consolidation-codification-repeal-and-revision-bill-rails.md`
- `318-statutory-guidance-codes-of-practice-directions-manuals-and-shadow-law-rails.md`
- `216-regulatory-impact-assessment-and-ex-post-review-rails.md`
- `208-change-management-and-release-engineering-for-government.md`
- `206-constitutional-change-and-amendment-rails.md`
- `207-sunset-review-and-rollback-rails.md`

**Judgment**
This family has a real retrieval problem even though the memos are not near-duplicates. Readers looking for “how rules change”, “better regulation”, “how lawmaking should work”, “what belongs in delegated legislation”, “when may law import external standards or codes”, “when does guidance become shadow law”, or “how to ship policy safely” routinely need to move across at least ten layers: legal legibility, versioned rule substrate, generic change control, legislative process, primary-to-secondary-legislation design, incorporation-by-reference / external-material design, finalization / promulgation, statute-book maintenance, quasi-law guidance / code design, evidence/review discipline, and implementation / release engineering. That is adjacency dense enough to deserve an explicit bridge memo.

**Recommended next move**
Handled in rev462 by adding a compact bridge memo and routing notes. Keep the family distinct unless a future editor can preserve legal-legibility front-door retrieval, PRR / rulebook substrate, generic rule-change control, legislative drafting / amendment tracing, delegated-legislation design, incorporation-by-reference / external-material design, finalization / promulgation, statute-book maintenance, impact-assessment / ex-post-review discipline, and operational release engineering as separate hooks.

**rev462 action**
- added `300-lawmaking-rulemaking-and-regulatory-change-routing-guide.md` as the canonical bridge memo for this family
- added routing notes to `25`, `39`, `118`, `208`, `215`, and `216`
- later extended in rev478, rev479, rev480, rev481, and rev482 with the narrower `316` lawmaking-finalization seam, `317` delegated-legislation seam, `320` incorporation-by-reference / external-material seam, `318` quasi-law / shadow-law seam, and `319` statute-book-maintenance seam
- rev482 also refreshed routing notes in `25`, `27`, `39`, `300`, `317`, and `318` so standards-governance, rulebook, delegation, incorporation-by-reference, and shadow-law questions stop collapsing into one another

### 19. Digital governance / data / interoperability / algorithmic-assurance cluster
**Files**
- `06-digital-and-algorithmic-governance.md`
- `127-data-governance-and-privacy-interfaces.md`
- `128-interoperability-interfaces-and-standards.md`
- `42-automated-decision-systems-and-model-registry.md`
- `152-algorithmic-impact-assessment-and-public-ai-governance.md`
- `146-ai-assurance-and-public-sector-ai-ops.md`
- `191-algorithmic-systems-registry-and-audit-rails.md`
- `173-ai-standards-and-regulatory-mapping.md`
- `33-data-protection-and-personal-data-governance.md`
- `144-data-stewardship-and-data-trusts.md`
- `287-dpi-identity-and-trust-family-map.md`

**Judgment**
This family has a real retrieval problem even though the memos are not near-duplicates. Readers looking for “digital government guardrails”, “responsible public AI”, “algorithmic accountability”, “data governance”, or “interoperability” routinely need to move across at least seven layers: broad digital-governance framing, personal-data-power interfaces, interoperability seams, ex ante impact assessment, inventory substrate, runtime assurance, and public registry / audit rails.

**Recommended next move**
Handled in rev463 by adding a compact bridge memo and routing notes. Keep the family distinct unless a future editor can preserve broad digital-public-systems framing, data-rights and sharing interfaces, interoperability governance, ex ante public-AI assessment, ADS/model inventory, runtime assurance, public registry / audit rails, and the privacy / standards / DPI neighbors as separate retrieval hooks.

**rev463 action**
- added `301-digital-governance-data-interoperability-and-algorithmic-assurance-routing-guide.md` as the canonical bridge memo for this family
- added routing notes to `06`, `127`, `128`, `42`, `146`, `152`, `173`, and `191`

### 20. Fiscal-state / budget / revenue / transfers cluster
**Files**
- `07-fiscal-and-budgetary-governance.md`
- `110-budget-procurement-integrity.md`
- `135-taxation-and-revenue-integrity.md`
- `93-tax-and-revenue-administration.md`
- `18-intergovernmental-finance.md`
- `194-fiscal-federalism-open-budgets-and-participation-rails.md`
- `217-intergovernmental-fiscal-transfers-and-equalization-rails.md`
- `97-public-investment-and-capital-project-governance.md`
- `138-public-investment-and-capital-projects-integrity.md`
- `157-monetary-and-financial-stability-governance.md`

**Judgment**
This family has a real retrieval problem even though the memos are not near-duplicates. Readers looking for “budget accountability”, “tax fairness”, “how transfers should work”, “open budgets”, or “how the fiscal state should be governed” routinely need to move across at least six layers: broad fiscal constitution, budget/procurement allocation, revenue-rule integrity, operational revenue administration, intergovernmental-finance structure, and transfer/equalization design. That is adjacency dense enough to deserve an explicit bridge memo.

**Recommended next move**
Handled in rev464 by adding a compact bridge memo and routing notes. Keep the family distinct unless a future editor can preserve broad fiscal-governance framing, budget/procurement allocation, revenue-rule integrity, operational administration/collection, cross-scope finance, open-budget participation, equalization design, and capital-allocation / financial-stability neighbors as separate retrieval hooks.

**rev464 action**
- added `302-fiscal-state-budget-revenue-and-transfers-routing-guide.md` as the canonical bridge memo for this family
- added routing notes to `07`, `110`, `135`, `93`, `18`, `194`, `217`, `97`, and `138`

## 21. Productive-state / utilities / market structure / industrial resilience family
**Files**
- `13-regulation-utilities-and-soes.md`
- `65-energy-and-decarbonization-governance.md`
- `94-competition-and-market-power-governance.md`
- `167-antimonopoly-and-market-structure-governance.md`
- `153-industrial-policy-and-supply-chain-resilience.md`
- `137-critical-infrastructure-and-utilities-integrity.md`
- `59-critical-infrastructure-and-cyber-resilience-governance.md`
- `302-fiscal-state-budget-revenue-and-transfers-routing-guide.md`
- `157-monetary-and-financial-stability-governance.md`

**Judgment**
This family has a real retrieval problem even though the memos are not near-duplicates. Readers looking for “industrial policy”, “economic security”, “utility governance”, “SOE reform”, “energy transition”, “competition policy”, or “how to govern strategic sectors without capture” routinely need to move across at least five layers: public-interest regulation and state ownership, sector-specific energy-transition governance, general competition enforcement, structural antimonopoly / contestability engineering, and industrial-policy / supply-chain-resilience design. That is adjacency dense enough to deserve an explicit bridge memo.

**Recommended next move**
Handled in rev465 by adding a compact bridge memo and routing notes. Keep the family distinct unless a future editor can preserve broad public-interest regulation / utilities / SOE framing, energy-transition specialization, competition-enforcement process, structural contestability tools, industrial-policy / supply-chain-resilience design, and the infrastructure / cyber / fiscal / monetary neighbors as separate retrieval hooks.

**rev465 action**
- added `303-productive-state-utilities-market-structure-and-industrial-resilience-routing-guide.md` as the canonical bridge memo for this family
- added routing notes to `13`, `65`, `94`, `153`, and `167`

## 22. Public-capital / assets / infrastructure resilience family
**Files**
- `97-public-investment-and-capital-project-governance.md`
- `138-public-investment-and-capital-projects-integrity.md`
- `225-public-assets-maintenance-and-capital-planning-rails.md`
- `48-asset-and-infrastructure-register.md`
- `154-critical-infrastructure-resilience-compacts.md`
- `59-critical-infrastructure-and-cyber-resilience-governance.md`
- `302-fiscal-state-budget-revenue-and-transfers-routing-guide.md`
- `294-climate-resilience-infrastructure-retreat-and-risk-finance-routing-guide.md`
- `303-productive-state-utilities-market-structure-and-industrial-resilience-routing-guide.md`

**Judgment**
This family has a real retrieval problem even though the memos are not near-duplicates. Readers looking for “public investment governance”, “maintenance backlogs”, “asset management”, “how infrastructure resilience should work”, or “how cyber continuity fits with physical infrastructure governance” routinely need to move across at least six layers: capital-allocation and stage-gate choice, megaproject integrity and change-order discipline, maintenance and lifecycle liability, asset-register substrate, cross-scope resilience compacts, and cyber / outage continuity. That is adjacency dense enough to deserve an explicit bridge memo.

**Recommended next move**
Handled in rev466 by adding a compact bridge memo and routing notes. Keep the family distinct unless a future editor can preserve broad capital-governance framing, project-integrity specialization, maintenance / lifecycle liability, asset-register substrate, resilience-compacts design, cyber / outage continuity, and the fiscal / climate / productive-state neighbors as separate retrieval hooks.

**rev466 action**
- added `304-public-capital-assets-and-infrastructure-resilience-routing-guide.md` as the canonical bridge memo for this family
- added routing notes to `48`, `59`, `97`, `138`, `154`, and `225`

### 23. Inter-jurisdiction / compacts / authority-routing / cross-border-dispute family
**Files**
- `17-jurisdiction-formation-and-boundaries.md`
- `19-compacts-and-cooperative-governance.md`
- `182-polycentric-governance-and-compacts.md`
- `197-polycentric-federalism-and-overlapping-sovereignty.md`
- `219-shared-services-and-federated-administration-rails.md`
- `221-jurisdiction-graph-and-authority-routing.md`
- `114-interjurisdictional-dispute-and-coordination.md`
- `230-conflict-of-laws-and-cross-border-dispute-rails.md`
- `296-status-identity-portability-and-mobility-routing-guide.md`

**Judgment**
This family has a real retrieval problem even though the memos are not near-duplicates. Readers looking for “who is responsible across borders”, “shared services across jurisdictions”, “how federal overlap should work”, “how to stop ping-pong between agencies”, or “how cross-border disputes should be routed” routinely need to move across at least seven layers: boundary / responsibility-map change, compact design, general polycentric coordination language, overlapping-sovereignty design, shared-service operations, authority-router substrate, and domestic / cross-border dispute handling. That is adjacency dense enough to deserve an explicit bridge memo.

**Recommended next move**
Handled in rev467 by adding a compact bridge memo and routing notes. Keep the family distinct unless a future editor can preserve map-change decisions, compact design, polycentric / federal design language, shared-service operations, authority-router substrate, domestic dispute handling, cross-border recognition / conflict-of-laws, and the person-status / continuity neighbor as separate retrieval hooks.

**rev467 action**
- added `305-interjurisdiction-compacts-authority-routing-and-cross-border-dispute-guide.md` as the canonical bridge memo for this family
- added routing notes to `17`, `19`, `114`, `182`, `197`, `219`, `221`, and `230`

### 24. Scope design / ideal-government / reference-bundle cluster
**Files**
- `14-scope-ladder.md`
- `54-subsidiarity-and-scope-assignment-test.md`
- `103-scope-cards.md`
- `176-ideal-governance-by-scope-synthesis.md`
- `285-scope-reference-governments-and-minimum-bundles.md`
- `71-interface-obligations-by-scope.md`
- `10-micro-local.md`, `20-municipal.md`, `87-intermediate-local-administration.md`, `16-metropolitan-governance.md`, `30-regional.md`, `40-national.md`, `50-supranational.md`, `60-global.md`

**Judgment**
This family has a real retrieval problem even though the memos are not near-duplicates. Readers asking “what would ideal government look like at each scope?”, “which level should own this function?”, or “what should a municipal / regional / national government actually be composed of?” routinely need to move across at least six layers: ladder/orientation, auditable assignment, quick-card retrieval, deeper synthesis, bundle composition, interface obligations, and the detailed scope-specific operating memos. That is adjacency dense enough to deserve an explicit bridge memo.

**Recommended next move**
Handled in rev468 by adding a compact bridge memo and routing notes. Keep the family distinct unless a future editor can preserve ladder/orientation, auditable assignment, quick retrieval, deep synthesis, bundle composition, interface obligations, and per-scope specialization as separate retrieval hooks.

**rev468 action**
- added `306-scope-design-ideal-government-and-reference-bundles-guide.md` as the canonical bridge memo for this family
- added routing notes to `14`, `54`, `71`, `103`, `176`, `285`, and the main scope memos

### 24a. Scope-form / office-defaults / anti-theater seam
**Files**
- `285-scope-reference-governments-and-minimum-bundles.md`
- `306-scope-design-ideal-government-and-reference-bundles-guide.md`
- `311-executive-system-choice-parliamentary-presidential-semipresidential-and-collegial-rails.md`
- `309-representative-chambers-committees-opposition-rights-and-confidence-architecture.md`
- `10-micro-local.md`, `20-municipal.md`, `16-metropolitan-governance.md`, `30-regional.md`, `40-national.md`, `50-supranational.md`, `60-global.md`

**Why it feels duplicative**
Readers asking “what should the government at this scale actually look like?” were forced to bounce between bundle composition, executive-form choice, chamber design, and the scope-specialization memos. That made the family feel more repetitive than it really was.

**Why it is not yet safe to collapse**
- `285` is still the bundle-composition memo
- `306` is still the family router
- `311` is still the narrower executive-form seam
- `309` is still the representative-chamber / confidence seam
- the scope memos remain the best front doors for per-scale operating detail

**Recommended next move**
Do not merge this cluster destructively. Keep one compact seam memo that answers the missing question of institutional **shape by scale** and routes outward.

**rev489 action**
- added `327-scope-form-defaults-councils-cabinets-secretariats-and-anti-theater-rails.md` as the canonical seam memo for scope-form / office-defaults / anti-theater questions
- refreshed routing notes in `14`, `75`, `103`, `176`, `273`, `280`, `285`, `306`, and the main scope memos

### 24b. Scope-legitimacy / dominant-channel defaults seam
**Files**
- `285-scope-reference-governments-and-minimum-bundles.md`
- `306-scope-design-ideal-government-and-reference-bundles-guide.md`
- `327-scope-form-defaults-councils-cabinets-secretariats-and-anti-theater-rails.md`
- `21-legitimacy-architecture.md`
- `180-legitimacy-engines-elections-sortition-deliberation-recall.md`
- `10-micro-local.md`, `20-municipal.md`, `16-metropolitan-governance.md`, `30-regional.md`, `40-national.md`, `50-supranational.md`, `60-global.md`

**Why it feels duplicative**
Readers asking “what kind of legitimacy fits this scale?” or “should this level rely mainly on assemblies, elections, delegation, dual legitimacy, or verification?” were forced to bounce between bundle composition, office-shape design, abstract legitimacy architecture, legitimacy-engine comparison, and the scope-specialization memos. That made the family feel blurrier than it really was.

**Why it is not yet safe to collapse**
- `285` is still the bundle-composition memo
- `306` is still the family router
- `327` is still the office-shape seam
- `21` is still the broad legitimacy-architecture memo
- `180` is still the comparative legitimacy-engine memo
- the scope memos remain the best front doors for per-scale operating detail

**Recommended next move**
Do not merge this cluster destructively. Keep one compact seam memo that answers the missing question of legitimacy **channel by scale** and routes outward.

**rev490 action**
- added `328-scope-legitimacy-defaults-voice-elections-delegation-dual-legitimacy-and-verification.md` as the canonical seam memo for scope-legitimacy / dominant-channel questions
- refreshed routing notes in `14`, `75`, `103`, `176`, `273`, `280`, `285`, `306`, `327`, `21`, `180`, and the main scope memos

### 24c. Scope-tempo / time-horizon / review-clock seam
**Files**
- `285-scope-reference-governments-and-minimum-bundles.md`
- `306-scope-design-ideal-government-and-reference-bundles-guide.md`
- `327-scope-form-defaults-councils-cabinets-secretariats-and-anti-theater-rails.md`
- `328-scope-legitimacy-defaults-voice-elections-delegation-dual-legitimacy-and-verification.md`
- `104-governance-control-loops.md`
- `108-service-standards-and-time-budgets.md`
- `74-sunsetting-and-deprecation-discipline.md`
- `122-intergenerational-and-future-protection.md`
- `10-micro-local.md`, `20-municipal.md`, `16-metropolitan-governance.md`, `30-regional.md`, `40-national.md`, `50-supranational.md`, `60-global.md`

**Why it feels duplicative**
Readers asking “what tempo fits this scale?” or “which things should move fast here and which should be slowed down?” were forced to bounce between bundle composition, office-shape design, legitimacy-channel design, control loops, service deadlines, sunset rules, future-obligation memos, and the scope-specialization memos. That made the family feel blurrier than it really was.

**Why it is not yet safe to collapse**
- `285` is still the bundle-composition memo
- `306` is still the family router
- `327` and `328` are still the office-shape and legitimacy-channel seams
- `104` is still the broad control-loop memo
- `108` is still the service-time / deadline memo
- `74` and `122` remain the sunset / future-obligation neighbors
- the scope memos remain the best front doors for per-scale operating detail

**Recommended next move**
Do not merge this cluster destructively. Keep one compact seam memo that answers the missing question of decision **tempo by scale** and routes outward.

**rev491 action**
- added `329-scope-tempo-defaults-fast-loops-slow-commitments-and-review-clocks.md` as the canonical seam memo for scope-tempo / time-horizon / review-clock questions
- refreshed routing notes in `10`, `14`, `16`, `20`, `30`, `40`, `50`, `60`, `87`, `75`, `103`, `176`, `273`, `280`, `281`, `285`, `306`, `327`, and `328`

### 24d. Scope-epistemics / evidence-defaults / anti-blindness seam
**Files**
- `285-scope-reference-governments-and-minimum-bundles.md`
- `306-scope-design-ideal-government-and-reference-bundles-guide.md`
- `327-scope-form-defaults-councils-cabinets-secretariats-and-anti-theater-rails.md`
- `328-scope-legitimacy-defaults-voice-elections-delegation-dual-legitimacy-and-verification.md`
- `329-scope-tempo-defaults-fast-loops-slow-commitments-and-review-clocks.md`
- `03-metrics-and-evidence.md`
- `26-epistemic-infrastructure-and-public-knowledge.md`
- `184-official-statistics-and-census-integrity.md`
- `202-open-knowledge-evidence-commons-and-scientific-integrity-rails.md`
- `10-micro-local.md`, `20-municipal.md`, `16-metropolitan-governance.md`, `30-regional.md`, `40-national.md`, `50-supranational.md`, `60-global.md`

**Why it feels duplicative**
Readers asking “what kind of evidence fits this scale?” or “should this level govern mainly through local observation, service data, territorial indicators, official statistics, or MRV?” were forced to bounce between bundle composition, office-shape design, legitimacy-channel design, tempo design, broad metrics/evidence memos, public-knowledge infrastructure, official-statistics integrity, and the scope-specialization memos. That made the family feel blurrier than it really was.

**Why it is not yet safe to collapse**
- `285` is still the bundle-composition memo
- `306` is still the family router
- `327`, `328`, and `329` are still the office-shape / legitimacy-channel / tempo seams
- `03` is still the general metrics-and-evidence memo
- `26` / `184` / `202` remain the public-knowledge / official-statistics / evidence-commons neighbors
- the scope memos remain the best front doors for per-scale operating detail

**Recommended next move**
Do not merge this cluster destructively. Keep one compact seam memo that answers the missing question of epistemic **mode by scale** and routes outward.

**rev492 action**
- added `330-scope-epistemic-defaults-local-observation-service-data-territorial-indicators-official-statistics-and-mrv.md` as the canonical seam memo for scope-epistemics / evidence-defaults / anti-blindness questions
- refreshed routing notes in `10`, `14`, `16`, `20`, `30`, `40`, `50`, `60`, `87`, `75`, `103`, `176`, `273`, `280`, `281`, `285`, `306`, `327`, `328`, and `329`

### 24e. Scope-accountability / review-mode / anti-shadow seam
**Files**
- `285-scope-reference-governments-and-minimum-bundles.md`
- `306-scope-design-ideal-government-and-reference-bundles-guide.md`
- `327-scope-form-defaults-councils-cabinets-secretariats-and-anti-theater-rails.md`
- `328-scope-legitimacy-defaults-voice-elections-delegation-dual-legitimacy-and-verification.md`
- `329-scope-tempo-defaults-fast-loops-slow-commitments-and-review-clocks.md`
- `330-scope-epistemic-defaults-local-observation-service-data-territorial-indicators-official-statistics-and-mrv.md`
- `08-remedy-and-grievance.md`
- `172-administrative-justice-complaints-ombuds-mesh.md`
- `130-audit-and-inspection-integrity.md`
- `231-supreme-audit-institutions-and-public-accounts-rails.md`
- `156-judicial-systems-and-constitutional-review.md`
- `323-international-reporting-peer-review-and-domestic-follow-through-rails.md`
- `325-international-adjudication-individual-communications-jurisdiction-interim-measures-and-compliance-rails.md`
- `10-micro-local.md`, `20-municipal.md`, `16-metropolitan-governance.md`, `30-regional.md`, `40-national.md`, `50-supranational.md`, `60-global.md`

**Why it feels duplicative**
Readers asking “how should this scale mainly be checked?” or “should this level rely mainly on visible challenge, ombuds, audit, courts, peer review, or compliance tracking?” were forced to bounce between bundle composition, office-shape design, legitimacy-channel design, tempo design, evidence-mode design, complaint / ombuds memos, audit / public-accounts memos, judicial design, and international review / adjudication memos. That made the family feel blurrier than it really was.

**Why it is not yet safe to collapse**
- `285` is still the bundle-composition memo
- `306` is still the family router
- `327`, `328`, `329`, and `330` are still the office-shape / legitimacy-channel / tempo / evidence seams
- `08` / `172` remain the complaint / ombuds / administrative-justice neighbors
- `130` / `231` remain the audit / public-accounts neighbors
- `156` remains the courts / constitutional-review neighbor
- `323` / `325` remain the international peer-review / adjudication neighbors
- the scope memos remain the best front doors for per-scale operating detail

**Recommended next move**
Do not merge this cluster destructively. Keep one compact seam memo that answers the missing question of accountability **mode by scale** and routes outward.

**rev493 action**
- added `331-scope-accountability-defaults-recall-ombuds-audit-courts-peer-review-and-compliance.md` as the canonical seam memo for scope-accountability / review-mode / anti-shadow questions
- refreshed routing notes in `10`, `14`, `16`, `20`, `30`, `40`, `50`, `60`, `87`, `75`, `103`, `176`, `273`, `280`, `281`, `285`, `306`, `327`, `328`, `329`, and `330`


### 24f. Scope-coercion / direct-force-holding / anti-militia seam
**Files**
- `285-scope-reference-governments-and-minimum-bundles.md`
- `306-scope-design-ideal-government-and-reference-bundles-guide.md`
- `327-scope-form-defaults-councils-cabinets-secretariats-and-anti-theater-rails.md`
- `328-scope-legitimacy-defaults-voice-elections-delegation-dual-legitimacy-and-verification.md`
- `329-scope-tempo-defaults-fast-loops-slow-commitments-and-review-clocks.md`
- `330-scope-epistemic-defaults-local-observation-service-data-territorial-indicators-official-statistics-and-mrv.md`
- `331-scope-accountability-defaults-recall-ombuds-audit-courts-peer-review-and-compliance.md`
- `05-public-safety-and-coercion.md`
- `112-exception-control-and-emergency-powers.md`
- `116-coercion-use-of-force-and-detention-governance.md`
- `233-policing-and-use-of-force-governance-rails.md`
- `232-corrections-and-incarceration-governance.md`
- `222-war-powers-and-external-use-of-force-governance.md`
- `10-micro-local.md`, `20-municipal.md`, `16-metropolitan-governance.md`, `30-regional.md`, `40-national.md`, `50-supranational.md`, `60-global.md`

**Why it feels duplicative**
Readers asking “which level should directly hold police power?”, “should metro bodies have armed authority?”, “where should detention live?”, or “when is force a national rather than local function?” were forced to bounce between bundle composition, office-shape design, legitimacy-channel design, tempo design, evidence-mode design, accountability design, generic coercion memos, emergency powers, policing/custody specializations, and the scope-specific memos. That made the family feel blurrier than it really was.

**Why it is not yet safe to collapse**
- `285` is still the bundle-composition memo
- `306` is still the family router
- `327`, `328`, `329`, `330`, and `331` are still the office-shape / legitimacy-channel / tempo / evidence / accountability seams
- `05` / `112` / `116` remain the generic coercion / emergency / portable-protocol neighbors
- `233` / `232` / `222` remain the policing / custody / war-powers specializations
- the scope memos remain the best front doors for per-scale operating detail

**Recommended next move**
Do not merge this cluster destructively. Keep one compact seam memo that answers the missing question of coercive **power-holding by scale** and routes outward.

**rev494 action**
- added `332-scope-coercion-defaults-policing-detention-emergency-force-and-no-shadow-militias.md` as the canonical seam memo for scope-coercion / direct-force-holding / anti-militia questions
- refreshed routing notes in `10`, `14`, `16`, `20`, `30`, `40`, `50`, `60`, `87`, `75`, `103`, `176`, `273`, `280`, `281`, `285`, `306`, `327`, `328`, `329`, `330`, `331`, `05`, `112`, `116`, and `292`

### 25. Legitimacy / representation / elections / selection family
**Files**
- `21-legitimacy-architecture.md`
- `147-representation-and-electoral-system-choice.md`
- `56-elections-and-electoral-administration.md`
- `180-legitimacy-engines-elections-sortition-deliberation-recall.md`
- `119-selection-and-sortition-integrity.md`
- `141-delegation-and-representation-integrity.md`
- `284-deliberation-stack-binding-and-legitimacy-guide.md`

**Judgment**
This family has a real retrieval problem even though the memos are not near-duplicates. Readers asking “how should legitimate representation work”, “what electoral system fits this scope”, “how do election rules differ from election operations”, “when should deliberation or sortition supplement elections”, or “how do we keep proxy authority legible between elections” routinely need to move across at least six layers: broad legitimacy architecture, electoral-system design, election administration, comparative legitimacy-engine composition, draw integrity, and mandate / delegation integrity. That is adjacency dense enough to deserve an explicit bridge memo.

**Recommended next move**
Handled in rev469 by adding a compact bridge memo and routing notes. Keep the family distinct unless a future editor can preserve broad legitimacy architecture, representation / electoral-system choice, election-administration operations, comparative legitimacy-engine design, draw-integrity verification, and proxy-authority / mandate integrity as separate retrieval hooks.

**rev469 action**
- added `307-legitimacy-representation-elections-and-selection-guide.md` as the canonical bridge memo for this family
- added family / routing notes to `21`, `56`, `147`, `180`, `119`, `141`, and `284`

### 26. Transfer-of-power / caretaker / continuity-of-office seam
**Files**
- `56-elections-and-electoral-administration.md`
- `113-appointments-and-tenure-integrity.md`
- `171-constitutional-maintenance-and-amendment-ops.md`
- `228-public-appointments-and-board-governance-rails.md`
- `297-state-capacity-appointments-and-agency-independence-routing-guide.md`
- `186-emergency-powers-derogations-and-sunset-discipline.md`

**Judgment**
This is less a duplication family than a missing seam memo, but it had become a recurrent retrieval problem. Readers asking “how should peaceful transfer of power work”, “what may a caretaker government do”, “how do acting appointments stay bounded during a transition”, or “how do services continue while authority changes hands” had to stitch together election administration, appointment integrity, constitutional maintenance, state-capacity routing, and emergency-exit rails on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev470 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve election operations, appointment / acting integrity, constitutional-maintenance logic, board-governance specialization, state-capacity routing, and emergency-neighbor logic as separate retrieval hooks.

**rev470 action**
- added `308-peaceful-transfer-of-power-caretaker-government-and-continuity-of-office-rails.md` as the canonical seam memo for transfer-of-power / caretaker / continuity questions
- added routing notes to `21`, `56`, `171`, `228`, `297`, `307`, and `288`

### 27. Representative chambers / committee systems / opposition rights / confidence-architecture seam
**Files**
- `147-representation-and-electoral-system-choice.md`
- `215-legislative-process-and-drafting-rails.md`
- `231-supreme-audit-institutions-and-public-accounts-rails.md`
- `308-peaceful-transfer-of-power-caretaker-government-and-continuity-of-office-rails.md`
- `30-regional.md`
- `40-national.md`
- `50-supranational.md`
- `197-polycentric-federalism-and-overlapping-sovereignty.md`

**Judgment**
This is another missing seam rather than a duplicate cluster, but it had become a real retrieval problem. Readers asking “should this polity be unicameral or bicameral”, “what is the upper chamber for”, “how should committee scrutiny and opposition rights work”, or “how do investiture, no-confidence, and dissolution rules fit together” had to stitch together electoral-system design, legislative process, public-accounts oversight, transfer-of-power design, and scope / federal memos on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev471 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve seat-allocation design, legislative process, audit / public-accounts specialization, transfer-of-power practice, and scope / federal chamber logic as separate retrieval hooks.

**rev471 action**
- added `309-representative-chambers-committees-opposition-rights-and-confidence-architecture.md` as the canonical seam memo for representative-chamber / committee / opposition-rights / confidence questions
- added routing notes to `21`, `147`, `215`, `231`, `307`, `308`, `30`, `40`, `50`, and `285`

### 28. Cabinet-government / coalition / portfolio / centre-of-government seam
**Files**
- `309-representative-chambers-committees-opposition-rights-and-confidence-architecture.md`
- `308-peaceful-transfer-of-power-caretaker-government-and-continuity-of-office-rails.md`
- `297-state-capacity-appointments-and-agency-independence-routing-guide.md`
- `09-public-service-and-state-capacity.md`
- `215-legislative-process-and-drafting-rails.md`
- `40-national.md`
- `302-fiscal-state-budget-revenue-and-transfers-routing-guide.md`

**Judgment**
This is another missing seam rather than a duplicate family, but it had become a real retrieval problem. Readers asking “how should a cabinet be formed once confidence exists”, “what should a coalition agreement disclose”, “how should ministerial portfolios map to departments and legislation”, “what is the centre of government actually for”, or “how do cabinet committees keep cross-government issues from turning into leader’s-office improvisation” had to stitch together chamber design, transfer-of-power practice, state-capacity routing, legislative process, fiscal coordination, and national-scope design on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev472 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve chamber / confidence design, transfer practice, state-capacity / merit / appointments routing, legislative sequencing, fiscal coordination, and national executive design as separate retrieval hooks.

**rev472 action**
- added `310-cabinet-government-coalition-agreements-portfolio-architecture-and-centre-of-government-rails.md` as the canonical seam memo for cabinet / coalition / portfolio / CoG questions
- added routing notes to `09`, `40`, `215`, `297`, `307`, `308`, and `309`

### 28b. Executive-form / chamber / cabinet / transfer seam
**Files**
- `21-legitimacy-architecture.md`
- `147-representation-and-electoral-system-choice.md`
- `309-representative-chambers-committees-opposition-rights-and-confidence-architecture.md`
- `310-cabinet-government-coalition-agreements-portfolio-architecture-and-centre-of-government-rails.md`
- `308-peaceful-transfer-of-power-caretaker-government-and-continuity-of-office-rails.md`
- `311-executive-system-choice-parliamentary-presidential-semipresidential-and-collegial-rails.md`
- `40-national.md`
- `50-supranational.md`

**Judgment**
This family can feel duplicative because it is where readers ask the broadest “how should a government actually be built?” questions. But the overlap is mostly healthy adjacency rather than duplication: `21` governs legitimacy architecture, `147` governs electoral-system choice, `309` governs chamber / confidence design, `310` governs cabinet / portfolio / CoG operating design, `308` governs transfer-of-power and caretaker practice, `311` governs executive-form choice, and `40` / `50` keep scope defaults explicit.

**Recommended next move**
Handled in rev473 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve legitimacy generation, electoral-system fit, chamber / confidence design, executive-form choice, cabinet operating design, transfer practice, and scope-sensitive defaults as separate retrieval hooks.

**rev473 action**
- added `311-executive-system-choice-parliamentary-presidential-semipresidential-and-collegial-rails.md` as the canonical seam memo for executive-form / head-of-state / head-of-government questions
- added routing notes to `21`, `147`, `285`, `307`, `309`, `310`, `40`, `50`, `75`, `273`, and `280`

### 28c. Party-system / nomination / caucus-governance seam
**Files**
- `147-representation-and-electoral-system-choice.md`
- `309-representative-chambers-committees-opposition-rights-and-confidence-architecture.md`
- `310-cabinet-government-coalition-agreements-portfolio-architecture-and-centre-of-government-rails.md`
- `311-executive-system-choice-parliamentary-presidential-semipresidential-and-collegial-rails.md`
- `120-conflicts-of-interest-and-influence-integrity.md`
- `181-influence-lobbying-transparency-and-integrity-rails.md`
- `40-national.md`
- `50-supranational.md`

**Judgment**
This is another missing seam rather than a duplicate family, but it had become a real retrieval problem. Readers asking “how should parties be recognized and regulated”, “how should candidate nomination work”, “how do caucuses and whips fit between chamber design and cabinet bargaining”, or “when do anti-defection rules stabilize government versus destroying parliamentary independence” had to stitch together electoral-system design, chamber / confidence design, cabinet formation, executive-form design, influence-integrity rules, and scope memos on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev474 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve electoral-system design, chamber / confidence design, cabinet operating design, executive-form choice, anti-capture integrity, and national / supranational scope defaults as separate retrieval hooks.

**rev474 action**
- added `312-party-systems-candidate-selection-caucus-governance-and-anti-defection-rails.md` as the canonical seam memo for party-system / nomination / caucus-governance questions
- added routing notes to `147`, `307`, `309`, `310`, `311`, `40`, `50`, `75`, `273`, and `280`

### 28d. Head-of-state / reserve-powers / succession seam
**Files**
- `311-executive-system-choice-parliamentary-presidential-semipresidential-and-collegial-rails.md`
- `309-representative-chambers-committees-opposition-rights-and-confidence-architecture.md`
- `308-peaceful-transfer-of-power-caretaker-government-and-continuity-of-office-rails.md`
- `310-cabinet-government-coalition-agreements-portfolio-architecture-and-centre-of-government-rails.md`
- `40-national.md`
- `50-supranational.md`

**Judgment**
This is another missing seam rather than a duplicate family, but it had become a real retrieval problem. Readers asking “should a polity have a separate head of state at all”, “when should a ceremonial president be indirectly rather than directly elected”, “how should countersignature and assent work”, “what reserve powers should exist”, or “how should regency, incapacity, or succession be handled” had to stitch together executive-form choice, chamber / dissolution design, transfer practice, cabinet formation, and scope defaults on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev475 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve executive-form choice, chamber / confidence design, transfer practice, cabinet operating design, and scope-sensitive defaults as separate retrieval hooks while still giving readers one canonical route for the head-of-state layer itself.

**rev475 action**
- added `313-head-of-state-design-non-executive-presidents-constitutional-monarchs-reserve-powers-and-succession-rails.md` as the canonical seam memo for head-of-state / reserve-powers / succession questions
- added routing notes to `21`, `40`, `50`, `285`, `307`, `308`, `309`, and `311`

### 28e. Government-formation / investiture / deadlock seam
**Files**
- `309-representative-chambers-committees-opposition-rights-and-confidence-architecture.md`
- `308-peaceful-transfer-of-power-caretaker-government-and-continuity-of-office-rails.md`
- `310-cabinet-government-coalition-agreements-portfolio-architecture-and-centre-of-government-rails.md`
- `311-executive-system-choice-parliamentary-presidential-semipresidential-and-collegial-rails.md`
- `312-party-systems-candidate-selection-caucus-governance-and-anti-defection-rails.md`
- `313-head-of-state-design-non-executive-presidents-constitutional-monarchs-reserve-powers-and-succession-rails.md`
- `40-national.md`
- `50-supranational.md`

**Judgment**
This was the next real missing seam rather than a duplicate family. Readers asking “who should get the first chance to form a government after a hung parliament”, “what counts as proof of confidence”, “when is minority government acceptable”, “how long may negotiations last”, or “what happens before dissolution is allowed” had to stitch together chamber / confidence design, transfer practice, cabinet design, executive-form choice, party-system incentives, head-of-state powers, and scope defaults on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev476 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve chamber / confidence design, caretaker / continuity practice, cabinet operating design, executive-form choice, party-system incentives, head-of-state powers, and scope defaults as separate retrieval hooks while still giving readers one canonical route for the formation window itself.

**rev476 action**
- added `314-government-formation-investiture-windows-minority-governments-and-deadlock-breaking-rails.md` as the canonical seam memo for government-formation / investiture / minority-government / deadlock questions
- added routing notes to `285`, `40`, `50`, `307`, `308`, `309`, `310`, `311`, `312`, `313`, `75`, `273`, and `280`

### 28f. Constitutional conventions / cabinet manuals / codified-restraint seam
**Files**
- `308-peaceful-transfer-of-power-caretaker-government-and-continuity-of-office-rails.md`
- `310-cabinet-government-coalition-agreements-portfolio-architecture-and-centre-of-government-rails.md`
- `311-executive-system-choice-parliamentary-presidential-semipresidential-and-collegial-rails.md`
- `313-head-of-state-design-non-executive-presidents-constitutional-monarchs-reserve-powers-and-succession-rails.md`
- `314-government-formation-investiture-windows-minority-governments-and-deadlock-breaking-rails.md`
- `171-constitutional-maintenance-and-amendment-ops.md`
- `40-national.md`
- `50-supranational.md`

**Judgment**
This was the next real missing seam rather than a duplicate family. Readers asking “which constitutional rules can safely live as conventions”, “how should cabinet manuals be used”, “how do we stop caretaker or reserve-power practice from becoming insider folklore”, or “how should coalition carve-outs and operating restraint be published without pretending they are supreme law” had to stitch together transfer practice, cabinet design, executive-form choice, head-of-state powers, formation design, constitutional maintenance, and scope defaults on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev477 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve transfer / caretaker practice, cabinet and coalition operations, executive-form choice, head-of-state power design, formation / investiture design, constitutional-maintenance logic, and scope-sensitive defaults as separate retrieval hooks while still giving readers one canonical route for the conventions / cabinet-manual layer itself.

**rev477 action**
- added `315-constitutional-conventions-cabinet-manuals-and-codified-restraint-rails.md` as the canonical seam memo for constitutional conventions / cabinet manuals / codified-restraint questions
- added routing notes to `307`, `308`, `310`, `311`, `313`, `314`, `40`, and `50`

### 28g. Lawmaking-finalization / promulgation / publication / commencement seam
**Files**
- `215-legislative-process-and-drafting-rails.md`
- `313-head-of-state-design-non-executive-presidents-constitutional-monarchs-reserve-powers-and-succession-rails.md`
- `156-judicial-systems-and-constitutional-review.md`
- `31-records-foi-and-government-memory.md`
- `58-constitutional-change-and-amendment-discipline.md`
- `300-lawmaking-rulemaking-and-regulatory-change-routing-guide.md`

**Judgment**
This was another real missing seam rather than a duplicate family. Readers asking “what is the final authoritative text after parliament votes”, “how should assent or return powers be bounded”, “when can a constitutional court or council review a bill before promulgation”, “what makes an official version authoritative”, or “when does a law actually take effect” had to stitch together drafting, head-of-state design, constitutional review, records/publication integrity, and constitutional-change publication logic on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev478 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve drafting / amendment traceability, head-of-state power design, constitutional-review architecture, publication-memory integrity, and constitutional-change publication logic as separate retrieval hooks while still giving readers one canonical route for the final lawmaking stage itself.

**rev478 action**
- added `316-bill-finalization-assent-promulgation-publication-commencement-and-constitutional-referral-rails.md` as the canonical seam memo for lawmaking-finalization / promulgation / publication / commencement questions
- added routing notes to `156`, `215`, `300`, and `313`, and refreshed `75`, `273`, `279`, and `280`

### 28h. Delegated-legislation / empowering-provisions / parliamentary-scrutiny seam
**Files**
- `118-rulemaking-and-change-control.md`
- `215-legislative-process-and-drafting-rails.md`
- `316-bill-finalization-assent-promulgation-publication-commencement-and-constitutional-referral-rails.md`
- `25-legal-legibility-and-rule-inventory.md`
- `39-rulebook-and-instruments-registry.md`
- `300-lawmaking-rulemaking-and-regulatory-change-routing-guide.md`

**Judgment**
This was another real missing seam rather than a duplicate family. Readers asking “what should stay in primary legislation”, “when is a framework bill too skeletal”, “how should delegated powers be justified”, “when should draft regulations be published with a bill”, or “how should Henry VIII powers and delegated exemptions be bounded” had to stitch together generic rulemaking, bill drafting, promulgation, publication infrastructure, and lawmaking-family routing on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev479 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve generic rule-change control, drafting / amendment tracing, post-passage finalization, publication / rulebook infrastructure, and broader lawmaking-family routing as separate retrieval hooks while still giving readers one canonical route for the primary-to-secondary-legislation boundary itself.

**rev479 action**
- added `317-delegated-legislation-empowering-provisions-henry-viii-powers-and-parliamentary-scrutiny-rails.md` as the canonical seam memo for delegated-legislation / empowering-provisions / parliamentary-scrutiny questions
- added routing notes to `118`, `215`, `300`, and `316`, and refreshed `75`, `273`, `279`, and `280`

### 28i. Guidance / codes / directions / manuals / shadow-law seam
**Files**
- `25-legal-legibility-and-rule-inventory.md`
- `39-rulebook-and-instruments-registry.md`
- `118-rulemaking-and-change-control.md`
- `317-delegated-legislation-empowering-provisions-henry-viii-powers-and-parliamentary-scrutiny-rails.md`
- `208-change-management-and-release-engineering-for-government.md`
- `300-lawmaking-rulemaking-and-regulatory-change-routing-guide.md`

**Judgment**
This was another real missing seam rather than a duplicate family. Readers asking “when is guidance actually binding”, “what should a code of practice legally do”, “when does a manual or FAQ become shadow law”, “how should ‘must have regard to’ guidance be reviewed”, or “when do internal scripts and configuration tables need daylight” had to stitch together rule discoverability, rulebook substrate, generic change control, delegated-legislation design, and implementation / operations notes on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev480 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve public legal-legibility, PRR / rulebook substrate, generic rule-change control, statutory-delegation design, and operational deployment as separate retrieval hooks while still giving readers one canonical route for quasi-law / shadow-law instruments themselves.

**rev480 action**
- added `318-statutory-guidance-codes-of-practice-directions-manuals-and-shadow-law-rails.md` as the canonical seam memo for guidance / codes / directions / manuals / shadow-law questions
- added routing notes to `39`, `118`, `208`, `300`, and `317`, and refreshed `75`, `273`, `279`, and `280`

### 28j. Statute-book-maintenance / consolidation / repeal / revision seam
**Files**
- `25-legal-legibility-and-rule-inventory.md`
- `39-rulebook-and-instruments-registry.md`
- `215-legislative-process-and-drafting-rails.md`
- `316-bill-finalization-assent-promulgation-publication-commencement-and-constitutional-referral-rails.md`
- `171-constitutional-maintenance-and-amendment-ops.md`
- `300-lawmaking-rulemaking-and-regulatory-change-routing-guide.md`

**Judgment**
This was another real missing seam rather than a duplicate family. Readers asking “when should we consolidate a body of law”, “how should obsolete provisions be repealed”, “what distinguishes revision bills from substantive reform”, “how should official current texts relate to as-enacted texts”, or “how do we improve statute-book accessibility without hiding policy change inside a tidy-up bill” had to stitch together public legal legibility, rulebook versioning, bill drafting, promulgation/publication, constitutional-maintenance logic, and the broader lawmaking-family router on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev481 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve public legal-legibility, PRR / rulebook substrate, drafting / amendment traceability, post-passage finalization, and constitutional-maintenance distinctions as separate retrieval hooks while still giving readers one canonical route for statute-book maintenance itself.

**rev481 action**
- added `319-statute-book-maintenance-consolidation-codification-repeal-and-revision-bill-rails.md` as the canonical seam memo for statute-book-maintenance / consolidation / repeal / revision-bill questions
- added routing notes to `25`, `39`, `300`, and `316`, and refreshed `75`, `273`, `279`, and `280`


### 28k. Treaty domestication / domestic-effect / reservations / implementation seam
**Files**
- `19-compacts-and-cooperative-governance.md`
- `50-supranational.md`
- `60-global.md`
- `58-constitutional-change-and-amendment-discipline.md`
- `316-bill-finalization-assent-promulgation-publication-commencement-and-constitutional-referral-rails.md`
- `305-interjurisdiction-compacts-authority-routing-and-cross-border-dispute-guide.md`

**Judgment**
This was another real missing seam rather than a duplicate family. Readers asking “when does an international agreement actually bind us domestically”, “should this treaty have direct effect or need transposition”, “where do reservations and declarations live”, “how should treaty obligations map into domestic rules and agencies”, or “how do withdrawal and amendment status stay visible over time” had to stitch together compact design, supranational/global scope logic, constitutional-change discipline, domestic promulgation/finalization, and broader inter-jurisdiction routing on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev483 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve compact design, scope ownership, constitutional-change discipline, domestic implementing-law finalization, and broader cross-border routing as separate retrieval hooks while still giving readers one canonical route for treaty domestication itself.

**rev483 action**
- added `321-treaty-ratification-domestic-effect-reservations-and-implementation-rails.md` as the canonical seam memo for treaty-domestication / domestic-effect / reservations / implementation questions
- added `322-executive-agreements-mous-political-commitments-and-international-instrument-typing-rails.md` as the canonical seam memo for treaty-vs-MOU / binding-status / political-commitment / international-instrument-classification questions
- added routing notes to `19`, `50`, `60`, `58`, `305`, and `316`, and refreshed `75`, `273`, `279`, and `280`


### 28l. International reporting / peer review / domestic follow-through seam
**Files**
- `50-supranational.md`
- `60-global.md`
- `305-interjurisdiction-compacts-authority-routing-and-cross-border-dispute-guide.md`
- `321-treaty-ratification-domestic-effect-reservations-and-implementation-rails.md`
- `322-executive-agreements-mous-political-commitments-and-international-instrument-typing-rails.md`
- `81-verification-inspection-and-compliance-ladders.md`
- `231-supreme-audit-institutions-and-public-accounts-rails.md`

**Judgment**
This was another real missing seam rather than a duplicate family. Readers asking “what happens after a treaty body, peer-review group, or implementation-review mechanism issues recommendations”, “who should own each follow-up action domestically”, “how should unresolved items carry into the next cycle”, “what should a public recommendation tracker show”, or “how do stakeholder submissions and official responses stay joined over time” had to stitch together scope design, cross-border architecture, treaty domestication, instrument typing, generic verification ladders, and domestic audit/follow-through loops on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev485 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve scope ownership, compact/treaty distinctions, domestic-effect typing, generic compliance design, and public audit/follow-through as separate retrieval hooks while still giving readers one canonical route for international review follow-through itself.

**rev485 action**
- added `323-international-reporting-peer-review-and-domestic-follow-through-rails.md` as the canonical seam memo for international reporting / peer review / recommendation-tracking / domestic follow-through questions
- added routing notes to `50`, `60`, `305`, `321`, and `322`, and refreshed `75`, `273`, `279`, and `280`

### 28m. Treaty lifecycle change / provisional application / amendment / suspension / withdrawal seam
**Files**
- `19-compacts-and-cooperative-governance.md`
- `50-supranational.md`
- `60-global.md`
- `305-interjurisdiction-compacts-authority-routing-and-cross-border-dispute-guide.md`
- `321-treaty-ratification-domestic-effect-reservations-and-implementation-rails.md`
- `322-executive-agreements-mous-political-commitments-and-international-instrument-typing-rails.md`
- `323-international-reporting-peer-review-and-domestic-follow-through-rails.md`
- `58-constitutional-change-and-amendment-discipline.md`

**Judgment**
This was another real missing seam rather than a duplicate family. Readers asking “how should provisional application be used without bypassing scrutiny”, “what happens when later protocols or amendments change the baseline”, “how should suspension or withdrawal be published and consequence-mapped”, “what survives exit”, or “where should public treaty-status updates live over time” had to stitch together compact design, scope ownership, treaty domestication, instrument typing, review follow-through, and constitutional exit discipline on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev486 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve compact design, scope ownership, treaty-domestication, instrument-typing, review-follow-through, and constitutional-change distinctions as separate retrieval hooks while still giving readers one canonical route for treaty lifecycle change itself.

**rev486 action**
- added `324-treaty-lifecycle-change-provisional-application-amendment-suspension-and-withdrawal-rails.md` as the canonical seam memo for treaty lifecycle change / provisional application / amendment / suspension / withdrawal questions
- added routing notes to `19`, `50`, `60`, `305`, `321`, `322`, `323`, and `58`, and refreshed `75`, `273`, `279`, and `280`

### 28n. International adjudication / individual communications / jurisdiction / interim-measures / compliance seam
**Files**
- `305-interjurisdiction-compacts-authority-routing-and-cross-border-dispute-guide.md`
- `230-conflict-of-laws-and-cross-border-dispute-rails.md`
- `321-treaty-ratification-domestic-effect-reservations-and-implementation-rails.md`
- `323-international-reporting-peer-review-and-domestic-follow-through-rails.md`
- `326-international-sanctions-listings-countermeasures-humanitarian-exemptions-and-delisting-rails.md`
- `08-remedy-and-grievance.md`
- `156-judicial-systems-and-constitutional-review.md`
- `50-supranational.md`
- `60-global.md`

**Judgment**
This was another real missing seam rather than a duplicate family. Readers asking “which international forum can actually hear this dispute or complaint”, “what declaration, optional protocol, or compromissory clause makes jurisdiction possible”, “what standing or exhaustion rules apply”, “how do interim measures work when irreparable harm is imminent”, or “who owns compliance once a judgment, order, or views are issued” had to stitch together broad inter-jurisdiction routing, private cross-border dispute handling, treaty domestication, international follow-through, generic remedy design, domestic judicial backstops, and scope-level global/supranational architecture on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev487 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve broad authority-routing, treaty-domestication, peer-review follow-through, generic remedy design, domestic-court architecture, and scope ownership as separate retrieval hooks while still giving readers one canonical route for international adjudication and complaint pathways themselves.

**rev487 action**
- added `325-international-adjudication-individual-communications-jurisdiction-interim-measures-and-compliance-rails.md` as the canonical seam memo for international adjudication / individual communications / jurisdiction / interim-measures / compliance questions
- added routing notes to `50`, `60`, `305`, `321`, `322`, `323`, `08`, and `156`, and refreshed `75`, `273`, `279`, and `280`
- added `326-international-sanctions-listings-countermeasures-humanitarian-exemptions-and-delisting-rails.md` as the canonical seam memo for international sanctions / listings / countermeasures / humanitarian-exemptions / delisting questions
- added routing notes to `50`, `60`, `08`, `131`, and `325`, and refreshed `75`, `273`, `279`, and `280`


### 28o. Scope finance / revenue-model / equalisation-fit seam
**Files**
- `14-scope-ladder.md`
- `176-ideal-governance-by-scope-synthesis.md`
- `285-scope-reference-governments-and-minimum-bundles.md`
- `18-intergovernmental-finance.md`
- `07-fiscal-and-budgetary-governance.md`
- `135-taxation-and-revenue-integrity.md`
- `194-fiscal-federalism-open-budgets-and-participation-rails.md`
- `217-intergovernmental-fiscal-transfers-and-equalization-rails.md`
- `302-fiscal-state-budget-revenue-and-transfers-routing-guide.md`

**Judgment**
This was another real missing seam rather than a duplicate family. Readers asking “how should each scale actually be financed”, “when should local government rely on property tax and equalisation rather than grants”, “which functions need pooled national taxation or social insurance”, “when are shared taxes or formula contributions the right answer for metro and regional bodies”, or “how should treaty or global layers be funded without donor whim” had to stitch together scope design, bundle composition, intergovernmental finance, public budgeting, taxation, fiscal federalism, and equalisation design on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev495 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve ladder logic, bundle composition, intergovernmental-finance mechanics, budget participation, tax-administration integrity, and equalisation design as separate retrieval hooks while still giving readers one canonical route for scale-fit finance itself.

**rev495 action**
- added `333-scope-finance-defaults-dues-fees-equalisation-shared-taxes-and-burden-sharing.md` as the canonical seam memo for scope-finance / revenue-model / equalisation-fit questions
- added routing notes to `14`, `176`, `285`, `306`, `10`, `20`, `87`, `16`, `30`, `40`, `50`, and `60`, and refreshed `75`, `273`, and `280`

### 28p. Scope artifact / public-surface / no-dark-governance seam
**Files**
- `14-scope-ladder.md`
- `176-ideal-governance-by-scope-synthesis.md`
- `285-scope-reference-governments-and-minimum-bundles.md`
- `71-interface-obligations-by-scope.md`
- `31-records-foi-and-government-memory.md`
- `115-information-integrity-and-record-interfaces.md`
- `200-freedom-of-information-and-access-to-official-documents-rails.md`
- `183-governance-observability-and-public-audits.md`
- `184-official-statistics-and-census-integrity.md`
- `218-global-commons-governance-clubs-treaties-and-mrv-rails.md`

**Judgment**
This was another real missing seam rather than a duplicate family. Readers asking “what should local government visibly publish besides generic transparency promises”, “what kind of artifacts should metro or regional bodies leave behind so their authority is real”, “when does a scale need a gazette or public-accounts spine rather than a dashboard”, “what should supranational governance expose as an official-journal and implementation surface”, or “what makes global commitments real beyond declarations” had to stitch together scope design, bundle composition, generic interface duties, records / ATI, observability, official statistics, and treaty / MRV infrastructure on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev497 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve ladder logic, bundle composition, baseline interface duties, records / ATI substrate, observability, official-statistics release discipline, and global MRV architecture as separate retrieval hooks while still giving readers one canonical route for scale-fit publication surfaces themselves.

**rev497 action**
- added `335-scope-artifact-defaults-charters-receipts-gazettes-registries-and-no-dark-governance.md` as the canonical seam memo for scope-artifact / public-surface / no-dark-governance questions
- added routing notes to `14`, `176`, `285`, and `306`, and refreshed `75`, `273`, and `280`

### 28v. Scope geometry / boundary-fit / no-cartographic-theater seam
**Files / neighbors**
- `342-scope-geometry-defaults-membership-maps-walksheds-service-areas-functional-urban-areas-and-no-cartographic-theater.md`
- `343-scope-participation-defaults-open-meetings-public-comment-participatory-budgeting-deliberative-panels-and-no-spectator-governance.md`
- `14-scope-ladder.md`
- `176-ideal-governance-by-scope-synthesis.md`
- `54-subsidiarity-and-scope-assignment-test.md`
- `17-jurisdiction-formation-and-boundaries.md`
- `15-functional-authorities.md`
- `16-metropolitan-governance.md`
- `336-scope-constituency-defaults-members-residents-users-commuters-citizens-member-states-and-affected-publics.md`
- `71-interface-obligations-by-scope.md`
- `128-interoperability-interfaces-and-standards.md`
- `164-digital-public-infrastructure-governance.md`
- `197-polycentric-federalism-and-overlapping-sovereignty.md`

**Why it feels duplicative**
All of these can surface when a user asks some version of “what line should this government actually use?”, “should metro mean city limits or commuting zone?”, “when is a compact overlay better than a new tier?”, or “what map fits global governance if it is not a world state?”.

**Why it is not safe to collapse**
- `342` is the scope-sensitive geometry / boundary-fit seam.
- `14` and `176` remain the ladder and synthesis front doors.
- `54` remains the auditable assignment / transfer test.
- `17` remains the deeper boundary-change and reorganisation procedure memo.
- `15` / `16` / `19` remain the functional-authority, metro, and compact implementation neighbors.
- `336` remains the who-counts seam; it answers the relevant public, not the governing map.
- `71` / `128` / `164` remain the interface / geospatial / DPI substrate once a geometry has been chosen.
- `197` remains the overlap / polycentric neighbor when the right answer is intentionally plural rather than neatly nested.

**Judgment**
This is another real missing seam rather than a duplicate family. Readers asking “what map should this scale use”, “when should local government stay contiguous but metro go functional”, “how should regions differ from metropolitan footprints”, “when should member territories remain the base map for a union”, or “what does global geometry even mean if not a world district” had to stitch together scope design, boundary procedure, metro governance, compacts, constituency, and geospatial substrate on their own. That is enough adjacency to justify one compact seam memo.

**Recommended next move**
Handled in rev504 by adding a compact seam memo and routing notes. Keep the family distributed unless a future editor can preserve ladder logic, boundary-change procedure, constituency design, functional-overlay logic, publication interfaces, geospatial joinability, and polycentric overlap as separate retrieval hooks while still giving readers one canonical route for scale-fit geometry itself.

**rev504 action**
- added `342-scope-geometry-defaults-membership-maps-walksheds-service-areas-functional-urban-areas-and-no-cartographic-theater.md` as the canonical seam memo for scope geometry / boundary-fit / no-cartographic-theater questions
- added `343-scope-participation-defaults-open-meetings-public-comment-participatory-budgeting-deliberative-panels-and-no-spectator-governance.md` as the canonical seam memo for scope participation / between-elections voice / no-spectator-governance questions
- added routing notes to `14`, `75`, `103`, `176`, `285`, and `306`, and refreshed `00`, `273`, and `280`

## Tier 4 — operator hygiene

### 29. README / map / revision-log drift
**Diagnosis**
Several revisions improved the archive substantively without fully refreshing the navigation surface.

**rev445 action**
- fixed README last-updated drift
- surfaced the systems map and attachment guide
- recorded the canonicalization move for `276` / `278`

**Rule going forward**
No deep merge revision is complete until:
1. `00-README.md`,
2. `75-archive-map-and-entry-points.md`,
3. `102-revision-log.md`
all reflect the same reality.

---

## Anti-regret rule

When in doubt:
- narrow a duplicate into a **bridge memo**,
- keep one **canonical anchor**,
- and preserve distinct retrieval hooks until the archive can absorb them cleanly.

That is slower than hard deletion, but it is how this repo avoids semantic amnesia.


### 28q. Scope constituency / who-counts / no-fake-demos seam
**Files / neighbors**
- `336-scope-constituency-defaults-members-residents-users-commuters-citizens-member-states-and-affected-publics.md`
- `328-scope-legitimacy-defaults-voice-elections-delegation-dual-legitimacy-and-verification.md`
- `125-identity-membership-and-civil-status.md`
- `296-status-identity-portability-and-mobility-routing-guide.md`
- `196-future-guardianship-and-standing.md`

**Why it feels duplicative**
All of these can surface when a user asks some version of “who counts?” or “who is the real public here?”.

**Why it is not safe to collapse**
- `336` is the scope-sensitive constituency / who-counts seam
- `328` is the legitimacy-channel seam
- `125` and `296` handle the deeper status / residence / portability family
- `196` handles future standing and guardianship

**Recommended next move**
Preserve `336` as the canonical bridge memo so these questions stop bouncing between legitimacy, citizenship, residence, and future-generations files.

### 28r. Scope selection / office-filling / no-prestige-elections seam
**Files / neighbors**
- `338-scope-selection-defaults-rotation-elections-delegates-appointments-and-no-prestige-elections.md`
- `328-scope-legitimacy-defaults-voice-elections-delegation-dual-legitimacy-and-verification.md`
- `337-scope-decision-rule-defaults-consensus-majorities-supermajorities-double-majorities-and-no-false-consensus.md`
- `307-legitimacy-representation-elections-and-selection-guide.md`
- `147-representation-and-electoral-system-choice.md`
- `56-elections-and-electoral-administration.md`
- `119-selection-and-sortition-integrity.md`
- `141-delegation-and-representation-integrity.md`
- `228-public-appointments-and-board-governance-rails.md`
- `297-state-capacity-appointments-and-agency-independence-routing-guide.md`
- `309-representative-chambers-committees-opposition-rights-and-confidence-architecture.md`
- `311-executive-system-choice-parliamentary-presidential-semipresidential-and-collegial-rails.md`
- `314-government-formation-investiture-windows-minority-governments-and-deadlock-breaking-rails.md`

**Why it feels duplicative**
All of these surface when a reader asks some version of “who should fill offices here?” or “what should be elected versus appointed?”.

**Why it is not safe to collapse**
- `338` is the scope-sensitive office-filling seam
- `328` is the legitimacy-channel seam
- `337` is the decision-rule seam
- `307` is the broader legitimacy / elections / selection router
- `147`, `56`, `119`, and `141` handle electoral-system, election-operations, sortition-integrity, and delegated-mandate design
- `228` and `297` handle appointments, boards, merit systems, and agency independence
- `309`, `311`, and `314` handle chamber, executive-form, and formation-specific consequences once election is already the chosen path

**Recommended next move**
Preserve `338` as the canonical bridge memo so scale-fit selection questions stop bouncing between elections, appointments, delegated representation, and regime-design files.

### 28s. Scope tenure / term-design / no-open-ended-office seam

- `339-scope-tenure-defaults-short-terms-medium-cycles-staggering-and-no-openended-office.md`
- `113-appointments-and-tenure-integrity.md`
- `78-delegation-and-acting-authority-discipline.md`
- `228-public-appointments-and-board-governance-rails.md`
- `229-independent-regulators-and-agency-independence-rails.md`
- `308-peaceful-transfer-of-power-caretaker-government-and-continuity-of-office-rails.md`
- `314-government-formation-investiture-windows-minority-governments-and-deadlock-breaking-rails.md`

Keep `339` as the scope-sensitive tenure seam. Keep `113` as the general appointment / acting / removal integrity memo, `78` as the acting-authority discipline memo, `228` and `229` as board / regulator specializations, and `308` / `314` as continuity and formation neighbors.

Preserve `339` as the canonical bridge memo so scale-fit tenure questions stop bouncing between appointments, acting authority, board staggering, executive continuity, and anti-entrenchment design.

### 28t. Scope office status / pay-status / no-unpaid-government seam

- `340-scope-office-status-defaults-volunteer-stipends-salaries-full-time-and-no-unpaid-government.md`
- `113-appointments-and-tenure-integrity.md`
- `120-conflicts-of-interest-and-influence-integrity.md`
- `228-public-appointments-and-board-governance-rails.md`
- `297-state-capacity-appointments-and-agency-independence-routing-guide.md`

Keep `340` as the scope-sensitive office-status seam. Keep `113` as the general appointment / acting / removal integrity memo, `120` as the conflict / outside-income memo, `228` as the board-compensation / public-body neighbor, and `297` as the merit-professional-capability / salaried-public-service specialization.

Preserve `340` as the canonical bridge memo so scale-fit office-status questions stop bouncing between selection, tenure, conflicts, board compensation, accessibility of office, and professional public-service design.

### 28u. Scope remedy / person-facing-review / no-dead-end-review seam

- `341-scope-remedy-defaults-complaints-ombuds-tribunals-courts-and-no-dead-end-review.md`
- `331-scope-accountability-defaults-recall-ombuds-audit-courts-peer-review-and-compliance.md`
- `08-remedy-and-grievance.md`
- `36-appeal-lanes-and-redress-registry.md`
- `172-administrative-justice-complaints-ombuds-mesh.md`
- `195-dispute-resolution-escalation-and-odr-rails.md`
- `323-international-reporting-peer-review-and-domestic-follow-through-rails.md`
- `325-international-adjudication-individual-communications-jurisdiction-interim-measures-and-compliance-rails.md`

Keep `341` as the scope-sensitive remedy seam. Keep `331` as the broader accountability / review-mode seam, `08` and `36` as the general grievance and appeal-lane substrate, `172` and `195` as the administrative-justice and escalation neighbors, and `323` / `325` as the international review and adjudication specializations.

Preserve `341` as the canonical bridge memo so scale-fit remedy questions stop bouncing between accountability, complaints, ombuds, administrative justice, courts, and international complaint / compliance design.
