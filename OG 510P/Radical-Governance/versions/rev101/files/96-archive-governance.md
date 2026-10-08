# Archive Governance (How the Research Program Stays Coherent)

This archive is designed to grow *slowly* while remaining decision-useful.

## A. What belongs here
A memo belongs here only if it:
- introduces a **new reusable primitive** (toolkit module, interface, metric loop), or
- clarifies a **scope boundary** (who owns what), or
- adds a **new failure mode** with a concrete mitigation.

Everything else SHOULD be a refactor of existing text.

## B. Size and structure constraints
- **ID naming discipline:** when referring to joinable objects, prefer the archive’s ID families (`PROG-*`, `EVAL-*`, `STD-*`, etc.) over generic phrases (“Program IDs”) to prevent drift.

- **New ID families:** add only when a real interface gap exists; when added, include a minimal schema, add it to the one-screen join-key map in `70-interoperability.md`, and reference it in **2+ memos**.

- A memo SHOULD fit on ~1–3 pages (roughly 1,000–2,000 words).
- Prefer **bullet specs** over essays.
- Prefer refactors (consolidate, standardize headings, remove duplication) before adding new memos.
- Cite primary sources and summarize implications; avoid long quotations.

## C. Evidence discipline
- For major proposals, record a testable claim ID (`CLM-*`) and link it to program/evaluation registers (see `37-...`, `28-...`).
- Every strong claim SHOULD have either:
  - a citation to a credible anchor, or
  - an explicit “assumption” tag.
- Measurement proposals MUST specify the decision loop they serve (see `03-metrics-and-evidence.md`).

## D. Refactoring rules (anti-archive-bloat)
- If a concept appears in 3+ places, extract it into:
  - the toolkit (`02-...`), metrics (`03-...`), threats (`04-...`), or interoperability (`70-...`).
- Any join-key ID family listed in `70-interoperability.md` MUST have a single canonical memo that defines its minimum schema (table or YAML skeleton); `70` SHOULD point to that section.
- **Enumeration discipline:** shared enumerated fields (e.g., `DRR-KIND`, `DRR-TYPE`, `OFR-KIND`, lane `STATUS` states) MUST be defined in one canonical place; don’t introduce new values in other memos—extend the canonical spec and update references.
- **Portable code discipline:** the portable code tables for `RC-*` (reasons), `AL-*` (appeal lanes), and `AO-*` (appeal outcomes) live in `70-interoperability.md`; other memos SHOULD reference them rather than inventing alternate codes.
- **Field-name hygiene:** avoid using join-key prefixes as field names (e.g., avoid `AL-ID`); use neutral names like `LANE-ID` / `LANES` and store the join-key values (`AL-*`) in the values. This prevents drift detectors and readers from confusing fields with codes.
- When adding a new primitive, update at least **two** scope memos to reference it (or don’t add it).

## E. Change control (lightweight)
- Treat each edit as an “RFC” in miniature:
  - what changed
  - why it matters
  - what it replaces
  - how we’ll know it worked (metric / falsification)
- Keep the bibliography compact and high-trust (`90-bibliography.md`).

## F. Default stance
- Prefer **polycentric** systems with clear interfaces over “one ring” solutions.
- Prefer **reversible** changes (sunsets, pilots, evaluation) over irreversible leaps.

## G. Debt register (keep refactors visible)
- Maintain a short list (≤10 bullets) of the most important refactors or missing primitives.
- Each item MUST include: owner (or “unassigned”), target doc(s), and a deprecation plan for redundant text.
- Delete or resolve items aggressively; do not let this become a second backlog.

## H. 60-second lint protocol (manual; no code committed)
This is a lightweight “don’t ship broken joins” check. Run from the archive root.

1) **Undefined or unused bibliography keys**
```bash
# list used keys
grep -Rho "\[BIB-[A-Z0-9-]*\]" *.md | sort -u > /tmp/bib_used.txt
# list defined keys
grep -ho "^[-*] \*\*\[BIB-[A-Z0-9-]*\]" 90-bibliography.md | grep -o "\[BIB-[A-Z0-9-]*\]" | sort -u > /tmp/bib_defined.txt
# show used-but-undefined
comm -23 /tmp/bib_used.txt /tmp/bib_defined.txt
```

2) **Broken internal file links** (quick scan)
```bash
# list referenced .md files and check they exist
grep -Rho "\`[0-9][0-9]-[a-z0-9-]*\.md\`" *.md | tr -d '\`' | sort -u | while read f; do test -f "$f" || echo "MISSING: $f"; done
```

3) **Accidental identifier collisions** (human-in-the-loop)
```bash
# scan for ID-type declarations and visually confirm uniqueness
grep -R "^\| \`[A-Z][A-Z0-9-]*\`" -n 70-interoperability.md 02-design-toolkit.md 80-implementation-roadmap.md
```


4) **No raw URLs in memos** (keep URLs in `90-bibliography.md` only)
```bash
grep -RE "https?://" *.md | grep -v "90-bibliography.md" && echo "FOUND RAW URL(S) — move to bibliography" || echo "OK"
```

If anything fails: fix the join-key/name now (renaming later is expensive).

## I. Debt register (rev101)

Unresolved (keep ≤10; each item MUST name target doc(s) and a deprecation plan):

- **none:** keep this list empty by default; add an item only when it has a target doc + a deprecation plan.

Recent resolved (keep last ~6 revisions; older milestones summarized):

- **rev101:** tightened private-actor joinability without adding a new ID family: introduced the `EID` bundle (authoritative external entity identifiers) and a beneficial-ownership join pattern (publish BO statements as `REL-*` releases using BODS), added [TM-28] and [IPM-22], and propagated the guidance across procurement, grants/subsidies, and influence registers; added compact verification + LEI anchors ([BIB-OPENOWNERSHIP-VERIFY-2020], [BIB-GLEIF-ISO17442]).
- **rev100:** hardened transparency against *secrecy/classification laundering* by expanding FOI/records classification discipline (joinable refusal `DRR`s with existence metadata + review dates), adding [TM-27], and wiring remedy to require reviewable secrecy exceptions; promoted new anchors ([BIB-TSHWANE-2013], [BIB-JOHANNESBURG-1995]) and corrected the NIST SP 800-63-4 final date (now Jul 2025).
- **rev99:** closed the “spend without contracts” gap by adding a Grants/Subsidies/Tax Expenditures Register (`49-...`) and promoting `GRT-*`/`TEX-*` into the join-key map (`70-...`), plus [TM-26].

- **rev98:** hardened participation against **astroturf/bot manipulation** by requiring joinable input-provenance summaries (`REL-*`) in the `ENG` register (`41-...`), adding an oversight case pattern (`CASE-TYPE: PARTICIPATION-INTEGRITY`) (`32-...`), and adding [TM-25] + [LRR-11] as the cross-scope threat/metric hooks (`04-...`, `03-...`).
- **rev96:** added **ACC-8 self-report safe harbor + self-correction** and linked it into oversight detection and procurement clauses (`02-...`, `32-...`, `38-...`, `04-...`).
- **rev95:**** strengthened “absence-as-signal” by adding possession-based **receipt verification** for `DRR`/`ENF` receipts and tracking it in [IPM-17] (`43-...`, `31-...`, `08-...`, `03-...`); hardened evaluation anti-capture with lightweight independence options (`28-...`); tightened contractor confidentiality claims against audit/oversight access (`38-...`); added a compact “oversight ecosystem” support layer (`32-...`).

- **rev94:** added an incentive-compatible anti-corruption primitive (ACC-7) and anchored randomized-audit evidence in the oversight loop; added/normalized the supporting bibliography anchors.

- **rev93:** hardened “governance by contract” so outsourcing can’t defeat notice/remedy/audit: added a minimal CLC clause pack to `38-...` and propagated the requirement to service delivery (`47-...`), records/FOI (`31-...`), ADS procurement constraints (`06-...`), competence ledger cross-links (`34-...`), and the Phase 0 roadmap (`80-...`); added a high-trust anchor for the government-by-contract framing in `90-...`.

- **rev86:** tightened the “ideal government by scope” articulation without increasing archive surface area: added a non-negotiable public-artifact baseline (authority/money/rules/remedy legibility) and clarified the county/prefecture pattern for “everything in between” inside `14-scope-ladder.md`.

- **rev85:** tightened the “money join” interface without adding new ID families: clarified that budget + execution should be published as joinable `REL-*` releases (budget ledger + execution/payment ledger) with `CON-*`/`TRF-*`/`PROG-*` references where feasible (`07-...`); added an optional OCDS↔budget linkage anchor in the procurement register (`38-...`); and updated the core join-key map (`70-...`) so program/contract objects explicitly point to execution releases.

- **rev84:** tightened joinability and reduced enum/field-name confusion by (a) adding a minimal FOI log entry skeleton to `31-...`, (b) adding `FOI-*` and `AST-*` to the one-screen join-key map in `70-...`, and (c) renaming `AL-ID`/`AL-LANES` fields to neutral names (`LANE-ID`/`LANES`); also expanded the portable `DRR-TYPE` categories in `70-...` to include `INTEGRITY`.
- **rev83:** resolved appeal-lane code drift by aligning `36-...` to the portable `AL-*` taxonomy in `70-...`, and added an explicit portable-code discipline note to prevent future enum drift.
- **rev82:** completed the `AUTH-DRR` field-name refactor for object↔decision joins by updating the minimal schemas in `35-...` (transfers), `38-...` (procurement), and the `PAR` minimum fields in `29-...` (permissioning) to use `AUTH-DRR` consistently (per `70-...`).
- **rev81:** standardized join-key language for learning + standards: replaced generic “Program/Evaluation IDs” with canonical `PROG-*`/`EVAL-*` (and `STD-*`), updated `28-...` schemas accordingly, and promoted `STD-*` and `PROG-*`/`EVAL-*`/`CLM-*` into the top join-key map in `70-...` so core interfaces are visible early.
- **rev80:** made interoperability maintenance cheaper by adding canonical schema pointers to the join-key map (so every ID family has an obvious “source of truth” section); standardized the object↔decision join pattern with a suggested `AUTH-DRR` field name (and added it to the `CMP` skeleton in `19-...`); added continuity anchor (ISO 22301) and trimmed unused bibliography keys.
- **rev79:** made **Unit IDs** less hand-wavy by adding minting rules + a minimum Unit ID entry schema (including optional external coverage-code hooks via [BIB-OCD-DIVISION-IDS] and [BIB-ISO-3166-2]); updated `70-...` to point to the canonical Unit ID section.
- **rev78:** normalized `DRR` semantics (aligned `DRR-KIND` usage, clarified portable `DRR-TYPE` categories including `AID`, and removed a stray `DRR-KIND` value from the integrity register); added an enumeration-discipline rule to prevent future drift.
- **rev77:** made `REL-*` a real join-key by adding a canonical publishable schema + revision linkage and wiring `70` to point to it; promoted metadata anchors (DCAT 3, PROV-O, SDMX 3.0).
Older milestones (rev76 and earlier): extracted the major cross-scope primitives (rule inventory/PRR, DRR receipts, ALR redress lanes, EMR emergency logging, ENF coercion logging, SRV service catalog, integrity/procurement joins, epistemic infrastructure/PDRR, compacts/transfers) and wired them through the scope memos. See prior archive revisions for the per-rev detail.
