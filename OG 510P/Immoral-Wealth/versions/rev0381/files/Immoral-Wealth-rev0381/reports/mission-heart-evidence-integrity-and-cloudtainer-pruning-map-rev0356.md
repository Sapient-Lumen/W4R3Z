---
project: Immoral Wealth
status: current_audit_and_refactor_map
claim_kind: archive_integrity_and_mission_audit
route_role: archive_governance_core
canonical_anchor: true
revision_current: rev0356
base_revision: rev0355
codename: mission-heart-evidence-integrity-and-cloudtainer-pruning-map
generated_at: 2026-06-18T08:30:59Z
---

# Mission heart, evidence integrity, and cloudtainer pruning map — rev0356

## Executive judgment

The archive's heart is morally and analytically strong:

> **Wealth should give people durable ordinary independence, but should not give anyone durable governing power over other people, public institutions, or the future.**

The project is therefore not fundamentally a ranking of wealth shares. It is an inquiry into whether people possess claimable security and exit options; whether ownership becomes command; whether advantage is inherited and closed; whether private gain transfers risk to the public; and whether public/common wealth gives ordinary people a durable counterweight.

The best existing programmatic expression is the **bounded-top, thick-middle, real-floor, open-circulation order** in `docs/20-program/ideal-distribution-and-policy-portfolio.md`. The archive's distinctive contribution is that it connects household wealth, labor dependence, inheritance, housing and debt extraction, democratic capture, public balance sheets, and remedy access in one frame.

But the cloudtainer is now better at **proving that its bookkeeping is internally present** than at proving that its claims are true. The current machine layer can certify a source-to-field association without showing the exact passage, claim, direction, scope, or contradiction. The all-green validator therefore overstates epistemic assurance. This is the central failure to repair.

## A clearer operating constitution

The project should be organized as three explicit layers rather than one accumulating cube:

1. **Normative constitution** — the moral tests, target family, disqualifying domination conditions, and public/common wealth principles. This layer changes rarely and records disagreements and sensitivity ranges.
2. **Empirical observatory** — versioned measurements of wealth, power, public assets/liabilities, ecological assets, lived experience, and institutional performance. Every measure carries concept, unit, population, valuation date, revision, and uncertainty.
3. **Instrument laboratories** — bounded case dossiers that test mechanisms and remedies. River Bend belongs here as a large-load public-incidence laboratory; it should not be the archive's front door or stand in for the whole mission.

A case should move through the chain:

`harm / dependence -> causal mechanism -> operative instrument -> expected incidence -> observed outcome -> contrary evidence -> verdict -> recertification trigger`

The present archive often has the first, second, and seventh elements, but not a disciplined bridge through the others.

## What is missing

### 1. Claim-level evidence, not source presence

The next evidence model needs atomic claims and auditable annotations. A minimally sufficient edge should contain:

- `claim_id` and the exact bounded claim text;
- `source_id`, source version, and retrieval date;
- page, section, table, paragraph, docket item, or data-series locator;
- a short quotation or faithful extraction;
- relationship: `supports`, `qualifies`, `contradicts`, `context_only`, or `method_only`;
- directness and authority for this claim, not for the source in general;
- extraction method and reviewer;
- uncertainty, applicability limits, and disconfirming evidence;
- a stable hash or annotation target so the edge can be reproduced.

The current `source_ids` arrays can remain as routing hints, but they should no longer count as verified evidence edges. Until migration, the archive should call the present **6,793 rows mechanical evidence associations**, not independently verified claims.

### 2. Falsifiers and strongest contrary cases

Every verdict needs a compact reversal rule: what new evidence would change it, what competing explanation is strongest, and which comparator would embarrass the preferred remedy. A project about capture must be unusually resistant to its own confirmation bias.

### 3. Maturity and certification tiers

All 95 cases are labeled `active`; all 95 carry `high` proof-debt severity; 87 have medium confidence; and the case ledger uses `see_case` for all 95 jurisdictions and units of analysis. That is a catalog, not a calibrated portfolio. Add separate fields for:

- `seed` — question and route only;
- `working` — material evidence but unresolved proof obligations;
- `certified_current` — claim-level lineage, contrary evidence, operative instruments, and completed review;
- `historical_comparator` — preserved but not current;
- `quarantined` — lineage or identity failure;
- `retired` — superseded with an explicit successor.

“Active” should describe workflow state, not evidentiary maturity.

### 4. A power-and-control dashboard

Wealth shares are necessary but insufficient. The cube needs separate measures of control: voting and ownership rights, political finance, media and platform agenda power, workplace authority, landlord/creditor discretion, procurement leverage, and exit threats. The moral problem is often not how much an asset is worth but what decisions its owner can impose or veto.

### 5. Target provenance and sensitivity

The default 20/50/20/10 private-wealth attractor is useful as a screen, but its status is unclear. The archive should distinguish:

- a **normative target** (what justice requires),
- an **empirical benchmark** (what observed systems achieve),
- a **measurement convention** (household/person, pensions, housing, offshore adjustment), and
- a **policy scenario** (what a feasible instrument portfolio is expected to produce).

Publish a target-provenance memo with sensitivity ranges and examples where acceptable shares still coexist with domination, or where unusual public wealth changes the private-share interpretation.

### 6. Public wealth as rights, governance, and resilience

Positive public net worth is not enough. The cube should ask who controls public assets, who receives services or dividends, whether assets can be raided or patronage-captured, how intergenerational claims are protected, and whether contingent liabilities and public corporations are included. Ecological solvency must be a co-condition: measured private and public financial wealth can rise while natural assets are depleted.

### 7. Implementation and transition incidence

Every proposed instrument needs legal authority, administrator, budget or financing path, enforcement capacity, time to impact, transition losers, appeals/remedies, and capture points. “Tax it” or “create a fund” is not an implementation theory.

### 8. Affected-person and experiential evidence

The source inventory is institution-heavy. Add a distinct evidence track for structured interviews, administrative-friction diaries, claimant journey tests, worker/tenant/borrower testimony, and participatory review. These should not replace causal evidence; they reveal mechanisms and harms that aggregate series miss.

### 9. Cross-border and exported-harm accounting

A jurisdiction can improve domestic distribution by exporting labor exploitation, resource depletion, tax-base erosion, pollution, or financial risk. Add an externalized-incidence gate to the target family and public balance-sheet work.

## Places where something has gone severely wrong

### A. Evidence-edge inflation — severe

The ledger contains **6,793 rows but only 670 unique case-source pairs**, an average of **10.139 rows per pair**. Of the rows, **4,144** are labeled `scoreboard_source_ids`; every one of the 95 cases repeats an identical source set across at least ten paths. The AI/data-center case alone has **1,464 rows (21.55%)**, 51 unique sources, and 56 unique claim paths. Each of S533-S537 generated exactly 28 rows when added.

This does not prove that the underlying claims are wrong. It proves that the count is not a defensible proxy for independent evidentiary support. A narrow source can be copied across many generic paths and inflate apparent coverage. The validator recomputes this multiplication and certifies the loop.

**Correction over time:** freeze edge-count growth as a success metric; introduce atomic claim annotations; migrate highest-consequence verdicts first; publish two counts during transition—`mechanical_association_count` and `verified_claim_edge_count`.

### B. Broken front door and stale “current” doctrine — severe

`README.md` and `START_HERE.md` pointed to a report filename that did not exist. Three current doctrine surfaces still reported 532 sources and 6,653 edges while the ledgers held 537 and 6,793. The validator passed because it checked normal Markdown links but not backtick paths, and because release-specific checks required selected fragments rather than exact cross-surface consistency.

**Correction applied in rev0356:** mission-first entrypoints, exact existing paths, generated current-count checks, and backtick-path validation.

### C. Historical provenance was overwritten — severe and not safely auto-repairable

All 81 report JSON files share the same `generated_at` value (`2026-06-13T19:37:00Z`); 60 JSON filenames disagree with their declared revision; 61 Markdown report filenames disagree with `revision_current`. Old audits can therefore present old metrics under a new revision identity. This destroys the ability to know what an audit actually observed.

**Correction over time:** do not mass-rewrite history again. Add immutable fields—`report_revision`, `observed_archive_revision`, `generated_at_original`, `input_manifest_sha256`, and `superseded_by`. Quarantine ambiguous historical reports in an index, preserve bytes and hashes, and regenerate only explicitly labeled reconstructions.

### D. The validator has become an append-only release diary — severe operational debt

`tools/validate_archive.py` is about **175,470 bytes / 2,995 lines**, defines 74 checks, includes 45 revision-specific check functions, references 49 revision tokens, and declared `CURRENT_REVISION` twice. Historical release assertions execute forever. This makes change risky, hides generic invariants, and rewards adding another bespoke function each turn.

**Correction over time:** split into `validate_core.py`, `build_ledgers.py`, and immutable release fixtures. Core validation should test schemas, identities, counts, paths, manifests, provenance, and semantic minimums. Historical receipts should be data, not executable code.

### E. Derived artifacts have no reproducible build path — severe integrity debt

The archive includes only one Python tool, the validator. Its largest ledgers are highly compressible and evidently generated, but no checked-in build script shows how to reproduce them. For example, `EVIDENCE_LEDGER.json` is about 3.0 MB and compresses to roughly 64 KB. Storage is not the primary problem; unverifiable generation and review burden are.

**Correction over time:** check in a deterministic build pipeline; make generated files carry generator version, input hashes, row-count tests, and `do_not_edit` metadata; compare regenerated output byte-for-byte in validation.

### F. Portfolio maturity is overstated — high

Every case is active and every case has high proof debt. Equal workflow labels flatten major differences between well-supported live cases, provisional mechanism maps, and inherited shells. The portfolio count therefore reads as more mature than it is.

**Correction over time:** introduce maturity tiers and publish counts by tier on every front door. No “certified current” case without claim-level locators, strongest contrary evidence, operational instrument text, and recertification date.

### G. Schema sprawl — high and wasteful

The field registry has 367 keys; 50 are `registered_unused`; 208 are used once; and 316 (86.1%) are used in at most two cases. The median use count is one. This weakens comparability and forces the validator to defend a long tail of bespoke vocabulary.

**Correction over time:** freeze new core fields temporarily; namespace case-specific observations; promote a field to the shared schema only after use in at least three cases or an explicit doctrinal necessity review; add alias, deprecation, successor, and retirement metadata.

### H. Report and changelog accretion — high and wasteful

There are 164 report files for 95 cases, including 48 validation reports and five exact duplicate report pairs. The changelog is itself a large, partially repetitive release surface. Keeping history is valuable; forcing every historical receipt into the main working set is not.

**Correction over time:** keep one current validation report in the live root, move immutable historical receipts to a content-addressed archive with an index, and generate a concise changelog from structured receipts. Never delete without a hash-preserving migration record.

### I. River Bend concentration and mission capture — medium/high

Recent work has concentrated heavily on one AI/data-center/large-load dossier. That topic is substantively important: data-center demand is large enough to raise current reliability, affordability, water, infrastructure, and cost-allocation questions. But one vivid project can capture the archive's attention and front door.

**Correction applied in rev0356:** River Bend is explicitly described as a **working large-load public-incidence instrument laboratory**, not the project's mission. Future work should require a portfolio allocation budget—mission core, measurement, cross-case comparison, and instrument labs—so topical urgency cannot consume all maintenance capacity.

## Online research synthesis

The external literature largely supports the archive's moral center while sharpening its missing machinery:

- Contemporary egalitarian work treats wealth inequality as a power asymmetry, not only a consumption gap. Republican work on labor-market domination emphasizes dependence and the absence of independent alternatives. This supports the cube's focus on claimability, exit, and non-domination.
- The Federal Reserve's Distributional Financial Accounts integrate aggregate financial accounts with Survey of Consumer Finances microdata and are revised as models change; the Fed has noted that model updates can materially change estimates for lower-wealth groups. A cube that stores only a share and source ID is therefore under-specified: measurement concept and vintage are part of the claim.
- IMF public-sector balance-sheet practice integrates assets, debt, non-debt liabilities, public corporations, infrastructure, natural resources, and pension liabilities, with stress testing. This supports a broader public-wealth layer than a single net-worth number.
- World Bank comprehensive-wealth work warns that rising measured output or wealth can coexist with depletion of natural assets. Ecological solvency should therefore constrain the ideal distribution rather than sit outside it.
- W3C Web Annotation, PROV-family practice, and Data on the Web Best Practices show how exact targets, provenance, versions, and quality metadata can be represented. RO-Crate demonstrates a practical package pattern for files, metadata, provenance, and workflows. The archive does not need to adopt every standard literally, but its next evidence contract should be interoperable with these ideas.
- DOE reported that data centers used about 4.4% of U.S. electricity in 2023 and projected 6.7%-12% by 2028. FERC's large-load proceeding explicitly includes reliability, affordability, state regulators, and affected communities; NARUC's 2026 review describes tariffs and project-specific filings aimed at allocating large-load costs. This validates River Bend as an instrument lab while reinforcing the need to inspect operative tariffs and contracts rather than company announcements alone.

### External audit references (not added to the canonical source registry)

These references informed this archive audit only. They are intentionally not registered as case evidence in rev0356, because adding sources before repairing claim-level lineage would reproduce the problem diagnosed here.

1. Christian Schemmel, “Wealth, Power, and Equality,” *Philosophy*: https://www.cambridge.org/core/journals/philosophy/article/wealth-power-and-equality/188FE4CB0DD6B828A99EFE05CB7BBE68
2. “Structural Domination and Freedom in the Labor Market,” *American Political Science Review*: https://www.cambridge.org/core/journals/american-political-science-review/article/structural-domination-and-freedom-in-the-labor-market-from-voluntariness-to-independence/15DE09962D69039C60D94AE163381C72
3. Federal Reserve, Distributional Financial Accounts overview and announcements: https://www.federalreserve.gov/releases/z1/dataviz/dfa/index.html and https://www.federalreserve.gov/releases/z1/dataviz/dfa/announcements/
4. IMF, Public Sector Balance Sheet toolkit: https://www.imf.org/en/topics/fiscal-policies/fiscal-risks/fiscal-risks-toolkit/fiscal-risks-toolkit-psbs
5. World Bank, comprehensive wealth and natural capital: https://www.worldbank.org/en/news/feature/2021/10/27/taking-a-comprehensive-view-of-wealth-to-meet-today-s-development-challenges
6. W3C, Web Annotation Data Model and Data on the Web Best Practices: https://www.w3.org/TR/annotation-model/ and https://www.w3.org/TR/dwbp/
7. Research Object, RO-Crate specifications: https://www.researchobject.org/specs/
8. U.S. Department of Energy, data-center electricity demand report announcement: https://www.energy.gov/articles/doe-releases-new-report-evaluating-increase-electricity-demand-data-centers
9. FERC Docket RM26-4 large-load interconnection page: https://www.ferc.gov/rm26-4
10. NARUC, state approaches to data-center and large-load tariffs (April 2026): https://pubs.naruc.org/pub/EAB18192-E245-0C03-2D98-33139B86E8B7

## Speculation: the strongest future form of this project

The cube could become a **public-interest institutional compiler** rather than an encyclopedia. Given a place or policy, it would produce:

1. the dominant dependence or domination mechanism;
2. the affected population and distributional baseline;
3. the private and public balance-sheet incidence;
4. the operative legal/contractual instruments;
5. a small portfolio of corrective instruments;
6. expected first-, second-, and third-order effects;
7. transition protections and administrative requirements;
8. falsifiers, uncertainty, and a recertification clock.

The output would not be “this country is at 12/48/24/16.” It would be a testable institutional diagnosis such as: ordinary households lack liquid exit security; rent and debt extract gains; public infrastructure subsidizes concentrated upside; governance rights are weak; and the nearest durable move is a linked package of claimable assets, cost-allocation rules, public upside, anti-capture governance, and remedy access.

A concise north-star dashboard could use five co-equal dimensions:

- **real floor:** liquidity, housing security, debt resilience, and service access;
- **broad ownership:** middle/bottom asset shares and portable person-level claims;
- **non-domination:** exit options, workplace/creditor/landlord limits, democratic power;
- **open circulation:** inheritance persistence, market entry, monopoly and gatekeeping;
- **public/ecological solvency:** full public balance sheet, common-asset rights, natural capital, and contingent risk.

No aggregate score should permit strength in one dimension to cancel a disqualifying failure in another.

## Staged correction plan

### Phase 0 — truth surface (applied in rev0356)

- restore mission-first `README.md` and `START_HERE.md`;
- fix the broken report route and stale live counts;
- label 6,793 rows as mechanical associations where presented to operators;
- add generic validation for entrypoint code paths, exact current-count surfaces, archive-index completeness, manifest completeness, and checksum consistency;
- remove the duplicate current-revision declaration;
- preserve historical reports rather than silently rewriting them;
- add no sources, cases, or schema fields.

### Phase 1 — evidence pilot

Choose five consequential cases across different gates. Create atomic claim records with locators, stance, quotations/extractions, contrary evidence, and review status. Stop expanding the existing edge ledger for those cases. Measure reviewer time and disagreement.

### Phase 2 — maturity and schema governance

Classify all 95 cases; populate jurisdiction and unit fields; quarantine identity/provenance failures; freeze core-field growth; produce a field retirement and alias map.

### Phase 3 — deterministic build and validator decomposition

Generate ledgers, indexes, front-door counts, and changelog from source records. Replace executable historical checks with fixture receipts. Add reproducibility and semantic-minimum tests.

### Phase 4 — substantive missing modules

Add target sensitivity, power/control dashboard, affected-person evidence, implementation/transition incidence, public-wealth governance, ecological solvency, and cross-border externalization.

### Phase 5 — portfolio discipline

Adopt a work-allocation rule. One possible starting point is 30% mission/framework and measurement, 30% cross-case comparison and certification, 30% instrument laboratories, and 10% maintenance/debt retirement. Review the allocation quarterly rather than allowing the newest case to determine it implicitly.

## Changes actually made in rev0356

- Added this human report and a paired machine-readable audit.
- Rewrote the two entrypoints around the mission and corrected all referenced paths.
- Corrected stale current-count notes in the coverage map, scoreboard specification, and open-questions surface.
- Updated current live ledgers and governance surfaces to rev0356 without changing their substantive source/case/field contents.
- Added generic validator checks for exact front-door counts, code-formatted entrypoint paths, archive-index synchronization, a non-circular manifest policy, manifest completeness, and manifest checksum verification.
- Added a rev0356 receipt check and removed the duplicate `CURRENT_REVISION` declaration.
- Regenerated the archive index and manifest under explicit completeness rules.

## Deliberately not changed

- No evidence edges were deleted or reclassified; doing so safely requires claim-level migration.
- No historical report content was rewritten; its ambiguity is documented rather than compounded.
- No case was promoted, demoted, or quarantined without a maturity rubric.
- No field was retired without an alias/successor plan.
- No external audit reference was inserted into `SOURCES.json`.
- No new cases, schema fields, or canonical sources were added.

## Current audit measurements

- 95 case memos / 95 scoreboards
- 537 canonical source rows
- 367 registered fields, 50 `registered_unused`
- 6,793 mechanical evidence associations
- 670 unique case-source pairs
- 3,425 `source_ids` arrays; 1,668 empty; 772 distinct source sets
- 164 report files, including 48 validation reports
- 95 active cases; 95 with high proof-debt severity
- 208 fields used once; 316 fields used in at most two cases

## Bottom line

Do not abandon the cube. Its moral architecture is unusually coherent and its cross-domain ambition is valuable. But stop treating accumulation, row counts, and all-green structural validation as proof of knowledge. The next era should be **smaller at the claim boundary, stricter about provenance, clearer about maturity, and more explicit about institutional causality**.
