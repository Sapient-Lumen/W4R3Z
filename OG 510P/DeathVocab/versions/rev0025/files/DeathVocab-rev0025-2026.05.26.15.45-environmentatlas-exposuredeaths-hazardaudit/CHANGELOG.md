# Changelog

## rev0022 — 2026.05.26.02.53 — workergrief-deathwork workforceaudit

Added the worker-carried-death / professional-grief / deathwork-burden layer and a targeted workforce-axis audit/refactor.

Added:

- 24 quarantined records, `DV-REC-000327` through `DV-REC-000350`.
- `WORKER-CARRIED-DEATH-ATLAS.json`.
- `PROFESSIONAL-GRIEF-AND-BURDEN-MATRIX.json`.
- `DEATHWORK-ROLE-BURDEN-MATRIX.json`.
- `WORKER-TESTIMONY-AND-CONFESSION-GATE.json`.
- `DEBRIEFING-RITUAL-AND-ORGANIZATIONAL-CARE-MATRIX.json`.
- `WORKFORCE-SURFACE-SAFETY-STANDARD.json`.
- `WORKFORCE-AXIS-AUDIT.json`.
- `tools/workforce_axis_audit.py`.
- 13 worker/deathwork source cards, `DV-SRC-WEB-0258` through `DV-SRC-WEB-0270`.
- 7 review packets, `DV-RP-0097` through `DV-RP-0103`.

Refactored/audited:

- Backfilled 18 prior role and postvention records into `worker_distress_axis`.
- Added `worker_testimony_and_confession` to high-gate coverage.
- Recomputed source-card dependencies, source-card index, review packet index, class taxonomy, factor graph, evidence audit, axis audit, high-gate audit, official-trace audit, postvention audit, reference integrity, and re-entry surfaces.
- Added a worker-carried-death record template for future sessions.

Posture remains: no public records, no private testimony, no active recruitment, no worker confession extraction, no therapy/staffing/employment/legal/forensic/funeral/emergency advice.

## rev0017 — 2026.05.25.16.36 — insideview-nonproof auditspine

Added the first inside-view/nonproof layer and a targeted evidence/source audit refactor.

Added:

- 20 quarantined records, `DV-REC-000211` through `DV-REC-000230`.
- `INSIDE-VIEW-ATLAS.json`.
- `INTERIORITY-EVIDENCE-LADDER.json`.
- `NONPROOF-AND-NONUNIVERSALITY-GUARD.json`.
- `EXPERIENCE-TRANSLATION-MATRIX.json`.
- `EVIDENCE-CLASS-MATRIX.json` and `EVIDENCE-CLASS-AUDIT.json`.
- `SOURCE-URL-BACKFILL-LEDGER.json`.
- `tools/evidence_class_audit.py`.
- 7 inside-view source cards, `DV-SRC-WEB-0191` through `DV-SRC-WEB-0197`.
- 7 review packets, `DV-RP-0062` through `DV-RP-0068`.

Refactored/audited:

- Added `provenance.evidence_class` to all quarantined records.
- Recomputed source-card dependency lists.
- Backfilled URLs for `DV-SRC-WEB-0017` and `DV-SRC-WEB-0039`.
- Added `evidence-audit` to `make check`.

Posture remains: no public records, no private testimony, no active recruitment, no proof/advice/prediction surface.

# Changelog

## rev0016 — 2026.05.25.16.44 — sensoryroom-smellsoundtouch materialwitness

Returned to corpus substance after the fieldwork bridge by adding a sensory/material-room layer.

Added:

- 24 quarantined records, `DV-REC-000187` through `DV-REC-000210`.
- `SENSORY-ROOM-ATLAS.json`.
- `MATERIAL-WITNESS-MATRIX.json`.
- `SOUND-SMELL-TOUCH-SAFETY-LEDGER.json`.
- `ROOM-OBJECT-REGISTRY.json`.
- `SENSORY-SOURCE-DEBT-LEDGER.json`.
- `SENSORY-RENDERING-STANDARD.json`.
- `docs/00-meta/rev0016-sensory-room-layer.md`.
- `docs/10-method/material-witness-and-sensory-evidence.md`.
- `surfaces/prototypes/lay-witness/internal-sensory-room-index.prototype.md`.
- 8 sensory/material source cards, `DV-SRC-WEB-0183` through `DV-SRC-WEB-0190`.
- 6 review packets, `DV-RP-0056` through `DV-RP-0061`.

Updated:

- `AXIS-REGISTRY.json`, `FACTOR-REGISTRY.json`, `EARNED-RIGHTS-LEDGER.json`, `CLAIM-SURFACE.json`, `SOURCE-LEDGER.json`, `SOURCE-CARD-INDEX.json`, `REVIEW-PACKET-INDEX.json`, `SEARCH-ALIAS-MAP.json`, `READER-QUERY-ROUTER.json`, `GLOSSARY-CROSSWALK.json`, `PUBLIC-SOURCE-PILOT-LEDGER.json`, `REVIEW-DEBT-LEDGER.json`, `COVERAGE-GAP-REGISTER.json`, `FOLLOWTHROUGH-QUEUE.json`, `OPEN-QUESTIONS.json`, and office re-entry surfaces.

Non-claims:

- No public records.
- No private testimony.
- No sensory publication surface.
- No medical, legal, ritual, funeral, facility, emergency, therapy, benefits, prognosis, or fieldwork recruitment advice.
- No child sensory material published.
- No good-death aesthetic.

Integrity:

- `make lint` passes.
- `make fieldwork-check` passes.
- `make audit` passes.
- `make check` passes.


# Changelog

## rev0015 — 2026.05.25.15.22 — fieldoffice-consentdryrun testimonybridge

Built the fieldwork/testimony bridge after the deep audit.

Added:

- `FIELDWORK-CHARTER.json`
- `CONTRIBUTOR-CONSENT-STATE-MACHINE.json`
- `TESTIMONY-INTAKE-SCHEMA.json`
- `INTERVIEW-PROTOCOL-ATLAS.json`
- `QUOTE-AND-PARAPHRASE-GATE.json`
- `DEIDENTIFICATION-AND-RECONTEXTUALIZATION-STANDARD.json`
- `PARTICIPANT-DISTRESS-AND-STOP-PROTOCOL.json`
- `CONTRIBUTOR-COMPENSATION-AND-CREDIT-LEDGER.json`
- `DATA-CUSTODY-AND-ACCESS-CONTROL-LEDGER.json`
- `FIELDWORK-REVIEW-BOARD-CHARTER.json`
- `SOURCE-ACQUISITION-TRIAGE-MATRIX.json`
- `FIELDWORK-SAMPLE-QUEUE.json`
- `PILOT-INTERVIEW-DRYRUN-PACKET.json`
- Draft contributor forms under `forms/contributor/`
- Fieldwork method docs under `docs/15-intake/`
- Five fieldwork review packets, `DV-RP-0051` through `DV-RP-0055`
- Six process source cards, `DV-SRC-WEB-0177` through `DV-SRC-WEB-0182`
- `tools/fieldwork_dryrun_check.py` and `make fieldwork-check`

Updated:

- `FACTOR-REGISTRY.json` with `DV-FAC-09 fieldwork_consent_and_testimony_bridge`.
- `EARNED-RIGHTS-LEDGER.json` to mark dry-run permission as earned and real testimony collection as still unearned.
- `STRUCTURAL-INVARIANTS.json`, `OPEN-QUESTIONS.json`, `FOLLOWTHROUGH-QUEUE.json`, `SOURCE-LEDGER.json`, `SOURCE-CARD-INDEX.json`, `REVIEW-PACKET-INDEX.json`, and re-entry surfaces.

Non-claims:

- No new corpus records.
- No real testimony collection.
- No public quotes or public paraphrases.
- No public corpus pages.
- No legal/IRB approval claim.
- No protected storage implementation yet.
- No high-gate recruitment.


## rev0014 — 2026.05.25.15.00 — deepaudit-factorgraph-integrityguard

Audit/factoring revision; no new records. Final packaging pass reconciled SEARCH-ALIAS-MAP and READER-QUERY-ROUTER alias namespaces, added `publication_review_state: blocked` to all 186 quarantined records, strengthened lint, and added `make audit` / `make check`.


# Changelog

## rev0014 — 2026.05.25.14.56 — audit-factor-integrityspine

Performed a structural audit and factoring pass without adding record volume.

Added:

- `AUDIT-REPORT.json`.
- `REFERENCE-INTEGRITY-REPORT.json`.
- `STRUCTURAL-INVARIANTS.json`.
- `FACTOR-REGISTRY.json`.
- `CLASS-TAXONOMY.json`.
- `SOURCE-CANONICALIZATION-LEDGER.json`.
- `FILE-INVENTORY-MANIFEST.json`.
- `docs/00-meta/rev0014-audit-and-factor-report.md`.
- `docs/10-method/schema-audit-and-normalization.md`.
- 14 source cards for record-referenced sources that had no card file.

Repaired:

- Added missing review blocks to perspective records.
- Added missing links blocks to setting and perspective records.
- Deduplicated record class tags and axis arrays.
- Normalized `ICU`/`ED` setting tags and removed setting leakage from timeline axes.
- Recomputed all source-card dependency lists from record source packets.
- Renamed lower-case `DV-RP-0011` through `DV-RP-0015` packet paths.
- Updated `RECORD-SCHEMA.json` and `tools/lint_archive.py` to match actual cube structure without freezing the ontology.

Non-claims:

- No record is public-facing.
- No private testimony has been collected or simulated.
- No external expert review has occurred.
- No medical, legal, emergency, funeral, ritual, financial, benefits, prognosis, or therapy advice is enabled.

## rev0013 — 2026.05.25.14.21 — milehigh-telos-dreamoffice

- Added a mile-high foundation checkpoint rather than expanding record volume.
- Added `TELOS-CHARTER.json` to name the archive’s earned-authority telos.
- Added `DREAM-REGISTER.json` to keep long-run dreams legible without converting them into release promises.
- Added `EARNED-RIGHTS-LEDGER.json` to distinguish what the archive has earned from what remains gated.
- Added `ANTI-OVERCONSTRAINT-LEDGER.json` to separate ethical hard law from provisional scaffolding.
- Added `FOUNDATION-MAP.json`, `OFFICE-STATE.json`, and `OFFICE-REENTRY-MEMO.md` for future-session continuity.
- Added four meta docs under `docs/00-meta/` on telos, earned rights, future-session thinking, and constraint hygiene.
- Updated re-entry surfaces, operating thesis, claim surface, open questions, followthrough queue, and lint expectations.
- Added no records; retained 186 quarantined records, 0 public records, and 0 private testimony.

Non-claims:

- Rev0013 does not make any quarantined record public.
- Rev0013 does not claim the current axes or schemas are final.
- Rev0013 does not collect, publish, or simulate private testimony.
- Rev0013 does not provide medical, legal, emergency, funeral, ritual, financial, benefits, or therapy advice.


## rev0012 — 2026.05.25.06.12 — perspective axis witness roles authority boundaries

Opened the perspective axis as an account-authority and witness-role layer.

Added:

- 30 quarantined perspective-axis records, `DV-REC-000157` through `DV-REC-000186`.
- `PERSPECTIVE-AXIS-ATLAS.json`.
- `ACCOUNT-AUTHORITY-MATRIX.json`.
- `ROLE-BIAS-AND-BLINDSPOT-LEDGER.json`.
- `FIRST-PERSON-TESTIMONY-GATE.json`.
- `CONTRIBUTOR-CREDIT-AND-SAFETY-PROTOCOL.json`.
- `PERSPECTIVE-ROUTING-GUIDE.json`.
- `records/templates/perspective-record-template.json`.
- Source cards `DV-SRC-WEB-0148` through `DV-SRC-WEB-0176`.
- Review packets `DV-RP-0043` through `DV-RP-0050`.

Updated:

- `WITNESS-ROLE-ACCESS-MATRIX.json` expanded from broad setting access to a full witness-role matrix.
- `AXIS-REGISTRY.json`, `PRACTICE-ATLAS.json`, `THRESHOLD-ATLAS.json`, `SEARCH-ALIAS-MAP.json`, `READER-QUERY-ROUTER.json`, `GLOSSARY-CROSSWALK.json`, `HIGH-GATE-POLICY.json`, `REVIEW-DEBT-LEDGER.json`, `COVERAGE-GAP-REGISTER.json`, `FOLLOWTHROUGH-QUEUE.json`, and re-entry surfaces.

Non-claims:

- No role is treated as the final or complete truth.
- No first-person, child, worker, official, call, bystander, or no-witness testimony has been collected.
- No clinical, legal, emergency, funeral, ritual, therapy, or benefit advice is enabled.
- No perspective-axis record is public-facing.

# Changelog

## rev0011 — 2026.05.25.05.36 — setting-axis-roomauthority-unprettyplacegates

- Added twenty-eight quarantined setting-axis records: `DV-REC-000129` through `DV-REC-000156`.
- Added setting governance surfaces: `SETTING-AXIS-ATLAS.json`, `ROOM-AUTHORITY-MATRIX.json`, `BODY-ACCESS-AND-CONTROL-LEDGER.json`, `WITNESS-ROLE-ACCESS-MATRIX.json`, `SETTING-ROUTING-GUIDE.json`, `GOOD-DEATH-AESTHETIC-RISK-LEDGER.json`, `NONHOSPICE-EDGE-REGISTER.json`, `POLITICAL-AND-OPAQUE-DEATH-GATE.json`, `MORTALITY-DATA-BOUNDARY-MATRIX.json`, and `SETTING-LANGUAGE-SAFETY-STANDARD.json`.
- Added source cards for home/hospice/care settings, ICU, ED, EMS, nursing home, homelessness, custody, disaster/humanitarian death, pediatric/perinatal/maternal high-gate settings, coroner/medical examiner roles, suicide/overdose safe language, family conflict, and pet presence.
- Added review packets `DV-RP-0035` through `DV-RP-0042`.
- Expanded search aliases, glossary crosswalk, practice atlas, threshold atlas, high-gate policy, review debt, coverage gaps, followthrough queue, and surface status.
- Kept all records quarantined; no public surfaces enabled; no place-of-death ranking, legal advice, emergency instructions, investigation, disaster operations, or trauma spectacle.

# Changelog

## rev0010 — 2026.05.25.04.18 — trajectory-axis-courseforms-prognosisguard

- Added twenty-four quarantined trajectory-axis records: `DV-REC-000105` through `DV-REC-000128`.
- Added `TRAJECTORY-AXIS-ATLAS.json`, `COURSE-FORM-MATRIX.json`, `PROGNOSIS-GUARDRAIL-LEDGER.json`, and `TRAJECTORY-ROUTING-GUIDE.json`.
- Added source cards for illness-trajectory, cancer, dementia, heart failure, COPD/advanced lung disease, kidney failure, liver disease, MND/ALS, Parkinson’s, stroke, and frailty sources.
- Added review packets `DV-RP-0029` through `DV-RP-0034`.
- Expanded search aliases, glossary crosswalk, threshold atlas, practice atlas, review debts, coverage gaps, and followthrough queue.
- Kept all records quarantined; no public surfaces enabled; no trajectory record may be rendered as prognosis, hospice eligibility, or treatment advice.

# Changelog

## rev0009 — 2026.05.25.03.21 — tradition-axis-ritualgates-sovereignty

- Added twenty quarantined cultural/tradition-axis records: `DV-REC-000085` through `DV-REC-000104`.
- Added `TRADITION-AXIS-ATLAS.json`, `CULTURAL-SOVEREIGNTY-PROTOCOL.json`, `TRADITION-HOLDER-REVIEW-CHARTER.json`, `RITUAL-AUTHORITY-GATE-MATRIX.json`, `APPROPRIATION-RISK-LEDGER.json`, `TRADITION-SOURCE-BIAS-MATRIX.json`, and `TRANSLATION-AND-DIACRITIC-STANDARD.json`.
- Added source cards for cultural humility, Catholic, Jewish, Muslim, Hindu, Buddhist, Tibetan Buddhist/tukdam, Quaker, green burial, home funeral, Día de los Muertos, African American secondary burial, humanist, Orthodox, and Sikh public sources.
- Added review packets `DV-RP-0022` through `DV-RP-0028`.
- Expanded search aliases, glossary crosswalk, threshold atlas, practice atlas, high-gate policy, language safety, review debts, coverage gaps, and followthrough queue.
- Kept all records quarantined; no public surfaces enabled; no ritual instructions admitted.

# Changelog

## rev0008 — 2026.05.25.02.47 — afterward-atlas-firstdays-griefgrammar

- Added twenty-two quarantined aftermath/bereavement/funeral records: `DV-REC-000063` through `DV-REC-000084`.
- Added `AFTERWARD-ATLAS.json`, `GRIEF-LANGUAGE-BOUNDARY-MATRIX.json`, `BODY-RELEASE-AND-DISPOSITION-MATRIX.json`, and `ADMINISTRATIVE-BURDEN-LEDGER.json`.
- Added source cards for after-death checklists, registration, funeral arrangement, FTC Funeral Rule, care of the body after death, public grief resources, prolonged grief disorder, child bereavement/funerals, anniversary reactions, continuing bonds, Citizens Advice, Age UK, HFA other losses, and Good Funeral Guide.
- Added review packets `DV-RP-0016` through `DV-RP-0021`.
- Expanded search aliases, glossary crosswalk, threshold atlas, practice atlas, high-gate policy, language safety, review debts, coverage gaps, and followthrough queue.
- Kept all records quarantined; no public surfaces enabled.

# Changelog

## rev0007 — 2026.05.25.01.34 — decisionlanguage-codestatus-institutiongates

- Added eighteen quarantined decision-language/institution-gate records: `DV-REC-000045` through `DV-REC-000062`.
- Added `DECISION-LANGUAGE-ATLAS.json`, `INSTITUTIONAL-GATE-MATRIX.json`, and `SURROGATE-PRESSURE-LEDGER.json`.
- Added source cards for advance care planning, POLST, DNACPR, withholding/withdrawing, ICU end-of-life care, ventilator withdrawal, palliative sedation, VSED, MAID, brain death, DCD/OPO, and honor-walk sources.
- Added review packets `DV-RP-0011` through `DV-RP-0015`.
- Expanded search aliases, glossary crosswalk, threshold atlas, practice atlas, high-gate policy, language safety, clinical review checklist, review debts, and followthrough queue.
- Kept all records quarantined; no public surfaces enabled.

# Changelog

## rev0006 — 2026.05.25.00.55 — utterance-atlas-lastwords-nonprophecy

- Added sixteen quarantined utterance/listening records: `DV-REC-000029` through `DV-REC-000044`.
- Added `UTTERANCE-SCHEMA.json`, `UTTERANCE-ATLAS.json`, `INTERPRETATION-BOUNDARY-MATRIX.json`, `LAST-WORDS-MYTH-LEDGER.json`, and `RESPONSE-BRAID-REGISTRY.json`.
- Added source cards for communication, last-words, relationship-completion, and euphemism/plain-language sources.
- Added review packets `DV-RP-0007` through `DV-RP-0010`.
- Expanded search aliases, glossary crosswalk, threshold atlas, practice atlas, language safety standard, review debts, and followthrough queue.
- Kept all records quarantined; no public surfaces enabled.


## rev0005 — 2026.05.24.20.09 — practice-atlas-reviewpack-sourcecards

- Added twelve quarantined practice-layer records: `DV-REC-000017` through `DV-REC-000028`.
- Added `CARE-MOVE-SCHEMA.json`, `PRACTICE-ATLAS.json`, `BEDSIDE-PHRASEBOOK.json`, and `LANGUAGE-SAFETY-STANDARD.json`.
- Added `SOURCE-CARD-INDEX.json` plus source cards for practice-layer sources.
- Added `REVIEW-PACKET-INDEX.json` plus six review packet stubs.
- Expanded search aliases and glossary crosswalk for care moves and after-death terms.
- Kept all records quarantined; no public surfaces enabled.


# Changelog

## rev0004 — 2026.05.24.19.39 — threshold-atlas-reviewgates-recordspread

- Expanded quarantined public-source pilot records from 5 to 16.
- Added threshold atlas clusters across breathing, mouth/intake/elimination, skin/eyes/smell, presence/visions/rally, and after-death room.
- Added reader query router and search alias map v2.
- Added glossary crosswalk v2.
- Added clinical review checklist.
- Added high-gate policy for pediatric, suicide, custody, restricted tradition, violent, and mass-death domains.
- Added held-source triage, coverage gap register, review debt ledger, and source snapshot ledger.
- Kept public record count at zero.
- Kept private testimony count at zero.
- Kept all seed cues quarantined.

## rev0003 — witnessed-schema-sourcegates-firstrecords — 2026.05.24.19.10

Began the corpus in quarantine. Added witnessed-moment schema v2, source ladder, contributor consent workflow, publication gates, intake pipeline, search aliases, glossary crosswalk, rendering rules, and five public-source pilot records. No public corpus pages were enabled.

# Changelog

## rev0003 — 2026.05.24.19.10 — witnessed schema sourcegates firstrecords

Started the corpus machinery without pretending the pilot records are public pages.

Added:

- `RECORD-SCHEMA.json` v2 for witnessed-moment records.
- `SOURCE-LADDER.json` and `docs/20-taxonomy/source-ladder.md`.
- `CONSENT-WORKFLOW.json` and `docs/10-method/contributor-consent-workflow.md`.
- `PUBLICATION-GATE-MATRIX.json` and `docs/10-method/publication-gate-matrix.md`.
- `RECORD-INTAKE-PIPELINE.json`.
- `SURFACE-RENDERING-RULES.json` and prototype lay/practitioner/provenance renderings for `DV-REC-000001`.
- `SEARCH-ALIAS-MAP.json`.
- `GLOSSARY-CROSSWALK.json` and glossary-crosswalk method note.
- `PUBLIC-SOURCE-PILOT-LEDGER.json`.
- `docs/15-intake/` templates for public sources, professional witnesses, family witnesses, and withdrawal/amendment requests.
- Five quarantined public-source pilot records under `records/quarantine/`.

Updated:

- `SOURCE-LEDGER.json` with seven public source entries.
- `CLAIM-SURFACE.json`, `SURFACE-STATUS.json`, `REVISION-RECEIPT.json`, `FOLLOWTHROUGH-QUEUE.json`, `OPEN-QUESTIONS.json`, `ETHICS-LEDGER.json`, `DEFEATER-LEDGER.json`, `ROLLBACK-LEDGER.json`, and re-entry surfaces.
- Lint now permits quarantined records and checks source references.

Non-claims:

- No pilot record is public-facing.
- No clinical validation is claimed.
- No private contributor testimony has entered.
- No seed cue has been promoted to fact.
- No search alias is a diagnosis, instruction, or prediction.

# Changelog

## rev0002 — 2026.05.24.18.45 — witnessed moments atlas northstar

Added the first direction-setting layer after the scaffold foundation.

Added:

- `OPERATING-THESIS.json` with the directional thesis that DeathVocab should become a bedside atlas of witnessed moments.
- `docs/00-meta/what-this-could-become.md` as a long-form project-shape memo.
- `docs/10-method/witnessed-moment-as-primary-unit.md` to prevent a term-first glossary from flattening scenes.
- `docs/10-method/three-public-surfaces.md` to distinguish lay witness, practitioner apprenticeship, and provenance/scholarship views.

Updated:

- Re-entry surfaces to point at the operating thesis.
- Open questions and followthrough queue to include witnessed-moment schema work.
- Claim surface to mark the new thesis as directional, not evidentiary.

Non-claims:

- No public corpus records exist yet.
- No source-acquisition or consent workflow has been field-tested yet.
- No medical, cultural, or public-interface validation is claimed.


## rev0001 — 2026.05.24.17.35 — bedside record ethics firebreak

Founded the DeathVocab baby datacube.

Added:

- Seed source preservation under `sources/seed/`.
- `SOURCE-LEDGER.json` with seed and prior-art source roles.
- `AXIS-REGISTRY.json` for the first orthogonal location axes.
- `RECORD-SCHEMA.json` for future record intake.
- `ETHICS-LEDGER.json` for hard publication gates.
- `CLAIM-SURFACE.json` to separate current claims, non-claims, and evidence debts.
- `CUE-REGISTRY.json` for seed motifs, all marked `seed_prompt_unverified`.
- `DEFEATER-LEDGER.json` and `ROLLBACK-LEDGER.json` for withdrawal, correction, cultural restriction, clinical-harm, and source-chain failures.
- Re-entry surfaces: `README.md`, `START_HERE.md`, `AGENTS.md`, `context-pack.json`, `frontier-ticket.json`, `replay-capsule.json`, `compact-surface-bundle.json`.
- `OPEN-QUESTIONS.json` and `FOLLOWTHROUGH-QUEUE.json` for next work.

Non-claims:

- No corpus records exist yet.
- No medical validation is claimed.
- No contributor consent system is implemented yet.
- No public database or search surface exists yet.


## rev0016 — 2026.05.25.16.44 — sensoryroom-smellsoundtouch-materialwitness

- Added 24 quarantined sensory/material-room records, DV-REC-000187 through DV-REC-000210.
- Added sensory room, material witness, sound/smell/touch safety, room object, source-debt, and rendering-standard surfaces.
- Added six new review packets, DV-RP-0056 through DV-RP-0061.
- Added eight new source cards, DV-SRC-WEB-0183 through DV-SRC-WEB-0190.
- Recomputed source-card dependencies and class counts.
- Preserved posture: 0 public records, 0 private testimony, no advice surfaces.


## rev0018 — 2026-05-25T17:24:00-04:00

Added 24 quarantined social-room / kinship-conflict records (DV-REC-000231..DV-REC-000254), 12 source cards, 6 review packets, social-room atlases/gates, and an axis coverage / record-factor graph refactor. No public records, no private testimony, no advice surfaces.


## rev0019 — 2026-05-25T18:12:00-04:00

Added 24 quarantined pediatric/perinatal high-gate records (DV-REC-000255..DV-REC-000278), 19 source cards, 8 review packets, child-material publication block, perinatal memory-making matrix, sibling/school/community gate, parental-grief nonpathology standard, and high-gate coverage audit/refactor. No public records, no private testimony, no child words or perinatal photographs.

## rev0020 — 2026-05-26T00:04:00+00:00

Added 24 quarantined absence/official-trace records (DV-REC-000279..DV-REC-000302), 13 source cards, 7 review packets, `ABSENCE-AND-TRACE-ATLAS.json`, `NO-WITNESS-EVIDENCE-MATRIX.json`, `OFFICIAL-TRACE-BOUNDARY-MATRIX.json`, `OFFICIAL-TRACE-LEXICON.json`, `ABSENCE-RENDERING-STANDARD.json`, `OFFICIAL-TRACE-AUDIT.json`, and `tools/official_trace_audit.py`. Backfilled seven prior absence-adjacent records into the official-trace audit spine. No public records, no private testimony, no forensic/legal/search/disaster-response/funeral advice, no public identification surface, and no closure-promise surface.
## rev0021 — 2026-05-26T01:06:00+00:00

Added 24 quarantined suicide/overdose postvention high-gate records (DV-REC-000303..DV-REC-000326), 16 source cards, 7 review packets, `POSTVENTION-ATLAS.json`, `SUICIDE-OVERDOSE-SAFETY-GATE.json`, `METHOD-SILENCE-AND-SAFE-SEARCH-STANDARD.json`, `STIGMA-AND-BLAME-LEXICON.json`, `POSTVENTION-RENDERING-STANDARD.json`, `SURVIVOR-RISK-AND-RESOURCE-BOUNDARY.json`, `POSTVENTION-SAFE-SURFACE-AUDIT.json`, and `tools/postvention_safe_surface_audit.py`. Backfilled four prior suicide/overdose-adjacent records into the postvention audit spine and extended official-trace audit coverage for cause/manner/toxicology/pending-language overlap. No public records, no private testimony, no method/scene/note detail, no overdose-response instruction, no survivor diagnosis, and no safe-search surface enabled.

## rev0023 — 2026.05.26.04.21 — closedroom-custodycare-accountabilityaudit

- Added 24 institutional-opacity / custody / congregate-care closed-room records (`DV-REC-000351..DV-REC-000374`).
- Added institutional opacity atlas, closed-room gate, family/body access matrix, congregate-care witness matrix, opaque-death rendering standard, and institutional-opacity audit.
- Added 20 source cards and 7 review packets.
- Backfilled 8 prior setting/official-trace records into the institutional-opacity audit spine.
- Integrated `make institutional-opacity-audit` into `make check`.
- Preserved quarantine: 0 public records and 0 private testimony.


## rev0025 — environmentatlas-exposuredeaths-hazardaudit

- Added 24 quarantined environment/exposure records (`DV-REC-000399`..`DV-REC-000422`).
- Backfilled 10 prior records into `environment_exposure_axis`.
- Added environment/exposure audit and scale/hazard factor surfaces.
- Added 17 source cards and 7 review packets.
- No public records, no private testimony, no hazard advice.
