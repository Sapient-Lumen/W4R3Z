# 983 — Cloudtainer mission kernel, reproducible build, schema completeness, route gravity, affected-person proof, and no governance by self-consistent cube

## One-line thesis

The archive’s heart is evidence continuity for public power, but its own integrity cannot rest on internal agreement alone: default builds must reproduce, every canonical JSON surface must be schema-governed, gaps must remain live, active routes must be reducible, and official administrative records must never be mistaken for affected-person outcomes or completed remedies.

## Why this matters

The cloudtainer is not a loose essay folder. Before this revision it held 580 numbered notes, 62 release/meta notes, 48 editable metadata and source files, 47 schemas, 47 Python tools, and more than one hundred generated surfaces. The archive prose was close to one million words. That scale is now an institutional fact: the maintenance system can preserve doctrine, but it can also generate convincing self-consistency around a bad category, a stale assumption, or a timestamp that changes every build.

The deepest mission remains sound. Across benefit delivery, public automation, casework, infrastructure, payments, identity, emergency response, procurement, and cross-boundary institutions, the archive asks one repeated question: what evidence joins lawful authority to actual delivery, person-level consequence, contestability, continuity, repair, and source currentness? Its best negative rules reject administrative theater. An outcome letter is not the decision packet. A portal is not a service home. An account approval is not usable money. A generated route is not a maintained mission.

The audit found that the cube had begun to violate that rule internally. `make lint` passed, yet a default rebuild rewrote 58 generated files without a substantive source change because each generator used the wall clock. Two live JSON surfaces declared schema identifiers for which no schema existed. Foundational note 403 was routed under `biodiversity-governance`, and notes 413 and 415 carried similarly unrelated tags. Every gap in the gap ledger was marked repaired. Every numbered note remained active in some form. These are not cosmetic defects: they show how a coherent derivation pipeline can reproduce the same wrong premise across indexes, manifests, thread maps, and audit summaries.

The governing repair is **no governance by self-consistent cube**.

## Pattern pack

### 1. Preserve the mission kernel: evidence must cross the administrative boundary

The archive’s central distinction is between an administrative surface and the reality the surface claims to represent. A status row can show that a case changed state. It does not by itself show that notice arrived, support remained available, the person understood the effect, the appeal clock was usable, or the remedy restored what was lost. A source-health row can show that a maintainer performed a check. It does not by itself preserve the supporting passage or prove the underlying public service works.

The minimum mission kernel is therefore:

- lawful authority and bounded discretion;
- a typed decision or action object;
- an operational delivery chain;
- affected-person or community outcome evidence;
- explanation, challenge, correction, and appeal;
- completed repair or redress;
- continuity through transition and failure;
- maintained, reconstructable evidence.

This is why the archive’s strongest contribution is not “radicality” as rhetoric. It is an anti-theater discipline that makes proof classes explicit.

### 2. Correct the reproducibility false-green

Before rev0785, all generators ultimately called a helper that used the current UTC wall clock unless a maintainer knew to set `RG_GENERATED_AT_UTC`, `RG_GENERATED_AT`, or `SOURCE_DATE_EPOCH`. The optional override was sound, but the default release path was not. Rebuilding an unchanged revision changed `generated_at_utc` in dozens of files; the manifest then honestly hashed the churn it had just created. A hashed manifest with unstable inputs is not a reproducibility guarantee.

This revision changes the default. When no explicit build-time override is present, generators now derive their timestamp from the current revision timestamp in `README.md`. Explicit environment overrides and `SOURCE_DATE_EPOCH` remain supported. `tools/check_reproducible_build.py` snapshots every generated hash, runs the default build again, and fails if any output changes. `make lint` now includes that guard.

The distinction matters: a release timestamp is source metadata; wall-clock build time is an execution accident. The Reproducible Builds convention treats `SOURCE_DATE_EPOCH` as a standard way to make tools consume source time rather than uncontrolled current time. The archive now follows the same principle by default.

### 3. Turn schema files from decoration into enforced coverage

The archive already had substantial hand-written lint and 47 JSON Schema documents. But `metadata/route_merge_packets.json` declared `route_merge_packets.v1` without a corresponding schema, and `sources/source_catalog.json` declared `radical-governance-source-catalog-v1` without one. The result was a partial schema system that could look complete from file counts.

Rev0785 adds both schemas and a dependency-free schema validator for the exact JSON Schema subset used by this repository: object/array/string/integer/boolean/null types, required properties, property schemas, additional-property rules, array items, constants, and regular-expression patterns. Lint now requires every canonical JSON document under `metadata/` and `sources/` to declare a unique known schema and validate against it. A future schema identifier without a schema is a lint failure, not a quiet exception.

### 4. Treat routing metadata as public evidence, not harmless labels

Note 403 is the archive’s foundational pattern for narrow public standards, interfaces, portability, conformance, procurement, and switching. Its sole metadata tag was `biodiversity-governance`. That tag was propagated into generated indexes and threads even though the prose had nothing to do with biodiversity. Note 413’s trust-list and relying-party route carried the same contaminant; note 415’s automation-lifecycle route carried `ageing-governance`.

This revision repairs those tags. The larger problem remains open: 580 notes carry hundreds of distinct tags, many appearing once, and source-health fields contain many one-off categorical labels. Free text has gradually entered fields that readers and generators treat as controlled vocabulary. The repair should be alias-backed and staged, not a destructive global rename, but category governance is now a live gap rather than an invisible maintenance preference.

### 5. Make the gap ledger admit gaps

Before rev0785 the ledger contained 28 entries and every one was marked repaired. Its prose described a backlog of missing domains and next artifacts, but operationally it was an accomplishments register. This encourages a pathological rhythm: name a gap, add a note or matrix in the same revision, and declare the gap closed before external validation or longitudinal evidence exists.

The ledger now contains live gaps for affected-person validation, route retirement and taxonomy control, source-receipt preservation, license and maintainer governance, and power/material-outcome theory. Lint now fails if every gap is again marked repaired. A live knowledge system should be able to state what it does not know.

### 6. Separate content preservation from active routing

The archive says “no archive by immortal note,” but every numbered note remains active, active-first-citation, active-via-dispatcher, or active-lineage. The retirement machinery has produced careful preservation reviews, which is better than reckless deletion, but it has not yet retired a route. The system currently treats keeping a file and keeping a route active as nearly the same decision.

The next retirement pilot should preserve the Markdown file, source history, hashes, and redirects while changing its live routing status to `superseded` or `historical`, with a `retired_to` pointer and a generated reader notice. This would test whether the archive can reduce present-tense cognitive load without erasing lineage. A maintenance ratio should follow: sustained note growth needs either active-route reduction or an explicit exception.

### 7. Shrink the human front door without destroying the machine registry

The generated front-door object contains well over one hundred named routes. That is useful as a registry, but it is not a front door in the ordinary sense. Note 963 called for fewer than twenty doctrine families; rev0785 adds `MISSION.md` with ten families and a proof ladder. The large machine map remains untouched for compatibility and should later be renamed `route_registry` once downstream readers can migrate.

The design rule is simple: humans need a compact path to the thesis; machines may keep exhaustive lookup surfaces behind it. Validation also exposed a filename-route defect: the release parser accepted any Markdown bullet, so `MISSION.md` briefly became `archive/MISSION.md`, while several generators assumed exactly three note digits. The parser is now restricted to numbered notes and the shared grammar accepts three or more digits, avoiding an imminent note-1000 failure.

### 8. Stop reporting source-health completion as evidentiary completeness

The source-health generator can truthfully say that every source key has a row. That is useful coverage. It is not the same as saying every document was opened, every claim was checked against a passage, every volatile page was preserved, or every official assertion was validated against affected-person experience.

A future source-receipt layer should separate at least:

- source identity resolved;
- document opened;
- relevant passage located;
- claim-to-passage mapping recorded;
- authority/currentness confirmed;
- content hash or lawful archival receipt retained;
- limitation and fallback documented.

The current “100 percent” style of completion metric should be read as ledger coverage only.

### 9. Add affected-person evidence as a first-class proof lane

The archive is source-rich but official-surface heavy. Its own doctrine repeatedly says that official rows are not outcomes, yet many case packets still rely mainly on laws, agency pages, audits, dashboards, registers, and press or oversight reports. Those sources can establish authority, system design, known failure, and public posture. They rarely establish the complete person journey, burden, non-take-up, successful remedy, or exclusion of people who never reached the formal channel.

Current external standards point in the same direction. The OECD’s human-centred services recommendation centers needs, experiences, rights, outcomes beyond the immediate interaction, user participation, measurement, and feedback. Its 2026 Digital Government Outlook says the main challenge is closing the gap between standards and lived delivery; it also reports that user engagement remains narrow and that standardized measurement of burdens is uncommon. The current GOV.UK Service Standard tells teams to solve the whole user problem across organizations and, after its 2026 update, to monitor outcomes and ethical issues rather than leaving assurance entirely to automated tools. The Universal DPI Safeguards Framework similarly treats individual and societal safeguards, inclusion, trust, and equity as implementation concerns rather than properties conferred by infrastructure alone.

The archive should therefore add an affected-person evidence protocol before it adds many more topical case packets. That protocol must address privacy, consent, representativeness, vulnerable non-users, complaint and appeal records, channel switching, administrative burden, remedy completion, and the limits of anecdote.

### 10. Name the conceptual boundary: procedural integrity is not a complete politics

The title “Radical Governance” promises more than the current corpus consistently delivers. The archive is strongest at administrative constitutionalism: interfaces, state transitions, reason-giving, source currentness, continuity, failure, remedy, and bounded institutional form. Those are real foundations. But a system can be interoperable, contestable, well-documented, reproducible, and still allocate resources unjustly, underfund public labor, privatize risk, entrench coercion, or exclude people from agenda-setting.

This is a speculative diagnosis, not a claim that the archive lacks concern for power. The missing step is an explicit doctrine that joins administrative proof to budgets, staffing, ownership, labor conditions, enforcement, democratic authorization, capture, redistribution, and materially unequal outcomes. Without it, the cube may become exceptionally good at proving that an unjust decision was administered cleanly.

## What changed in rev0785

- Added `MISSION.md` as a ten-family human front door and proof ladder.
- Added deterministic default generation from the release timestamp while retaining explicit `SOURCE_DATE_EPOCH` and archive-specific overrides.
- Added `tools/check_reproducible_build.py` and made reproducibility part of `make lint`.
- Added dependency-free repository-wide JSON Schema enforcement.
- Added schemas for `route_merge_packets.v1` and `radical-governance-source-catalog-v1`.
- Corrected the unrelated tags on notes 403, 413, and 415.
- Centralized numbered-note parsing, excluded non-numbered Markdown front doors, and removed the exactly-three-digit note ceiling.
- Reopened the gap ledger with five substantive maintenance and mission gaps, plus a lint guard against an all-repaired ledger.
- Added current primary and official comparison sources for human-centred services, whole-service delivery, service reliability, DPI safeguards, and reproducible builds.

## Anti-theater tests

1. Do two default builds from identical source produce byte-identical generated files?
2. Does every canonical JSON document have a known schema that lint actually applies?
3. Can the gap ledger show a high-severity unknown without pretending a new note repaired it?
4. Can a reader reach the mission through fewer than twenty doctrine families?
5. Can an old route become historical while its file and lineage remain preserved?
6. Does “source health complete” distinguish row coverage from passage-level and claim-level verification?
7. Does a case packet include evidence from affected people, non-users, burdens, and completed remedies rather than only official surfaces?
8. Can the archive explain how procedural integrity connects to power, labor, budgets, coercion, ownership, and distribution?

## Priority sequence

The next high-value work is not another broad topical expansion. First, pilot an affected-person evidence protocol in two existing case families. Second, retire or supersede one active route without deleting its file. Third, normalize the highest-churn tags and source-health categories through aliases and controlled vocabularies. Fourth, pilot source receipts and passage-level claim mapping. Fifth, obtain owner decisions on license, contribution, maintainer, and succession governance. Sixth, write and test the power-and-material-outcomes doctrine.

## Source posture

The external sources in this note are comparison and design standards. They support the distinction between standards and implementation, the need for whole-service and outcome evidence, DPI safeguards, and reproducible build time. They do not prove that any jurisdiction, service, infrastructure deployment, or archive route satisfies those standards. The internal counts and defects are derived from the rev0784 package and the before/after rev0785 build tests.
