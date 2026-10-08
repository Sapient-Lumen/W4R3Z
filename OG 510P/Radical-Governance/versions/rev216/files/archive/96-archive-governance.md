# Archive Governance (How the Research Program Stays Coherent)

**Purpose:** keep the research program coherent and small by enforcing density, cross-linking, and safety constraints.

This archive is designed to grow *slowly* while remaining decision-useful.


**Legitimacy note:** this archive is an expert-authored design *proposal*, not a democratic constitution. It should be treated as a starting point for public contestation and co-design—adopt/adapt/reject based on what governed communities choose, and record deviations explicitly (with reasons) rather than pretending one universal implementation exists.

## Kernel anchors (do not repeat)
- Complexity/manageability budget is a first-class constraint: `96` is the enforcement point.
- Interop is the default join surface (don’t add new interfaces casually): `70-...`.
- Person-facing floors and safety: `98-persons-path-and-accessibility-invariants.md`, `77-...`.

## Named tensions (design must surface these)
- Comprehensiveness vs cognitive manageability (archive bloat is a failure mode).
- Specificity for implementability vs generality for transfer across contexts.
- Openness of the archive vs safety (don’t publish playbooks for coercion).
- Tight coherence vs pluralism/functional equivalents.


## B. Archive self-threat-model (failure modes of *this* spec)
- **Control apparatus risk:** joinable registers can be weaponized for surveillance/targeting. Mitigate by minimizing join surfaces (`70`), keeping the affected person as integrator where possible, and enforcing secrecy/retaliation constraints (`77`, `98`).
- **Paperwork theatre:** artifacts can be emitted but unusable to the governed (formal compliance without lived contestability). Mitigate with comprehension/non‑reading floors and navigation duty (`31`, `98`).
- **Register sprawl / maintenance collapse:** the cost of keeping many registries current can exceed the governance benefit. Mitigate via the complexity budget + refactor‑instead‑of‑add rule (this memo) and one‑screen schemas.
- **Capture and legitimacy laundering:** captured oversight or “audit dashboards” can create a veneer of accountability. Mitigate by publication integrity + mirroring (`53`), plural contestation channels (`08`, `36`), and explicit adoption‑dynamics analysis (`99`). This includes **legibility theater** (formal compliance with toothless follow‑through; see [TM-24] and [TM-33]) and **capture‑by‑complexity** (adding detail to obscure safeguards or exhaust implementers).

---


## A. What belongs here
A memo belongs here only if it:
- introduces a **new reusable primitive** (toolkit module, interface, metric loop), or
- clarifies a **scope boundary** (who owns what), or
- adds a **new failure mode** with a concrete mitigation.

Everything else SHOULD be a refactor of existing text.


**Traceability test:** every structure added to the archive MUST be traceable to a concrete harm it prevents or a concrete form of agency it enables for a governed person (the `98` lens). If you can’t name that sentence, refactor/delete rather than add.
**Purpose sentence rule:** each memo MUST include (early, preferably in the opening paragraph) one plain-language sentence naming the governed person/community it serves or the concrete harm it prevents. This keeps “nouns” (artifacts) tied to “verbs” (lived experience) without adding new machinery.

**Map discipline:** any new memo that stays in the archive MUST add (or update) a one-line entry in `75-archive-map-and-entry-points.md` **and** be referenced from at least **two** other memos (otherwise merge/refactor instead of adding).

## B. Size and structure constraints
- **ID naming discipline:** when referring to joinable objects, prefer the archive’s ID families (`PROG-*`, `EVAL-*`, `STD-*`, etc.) over generic phrases (“Program IDs”) to prevent drift.

- **Size budget:** significant additions should come with deletions/refactors elsewhere (replace rather than append). If a new memo is added, remove or consolidate overlapping prose in other memos so the archive stays dense.

- **New ID families:** add only when a real interface gap exists; when added, include a minimal schema, add it to the one-screen join-key map in `70-interoperability.md`, and reference it in **2+ memos**.

- **Join-key homes:** if a join-key (`REL-*`, `RC-*`, etc.) is referenced across memos, it MUST have an explicit “home” spec (a dedicated registry memo or a clearly named section in an existing memo). Avoid “floating interfaces.”

- **Threat→control hygiene:** if you add/modify a `TM-*` mitigation pattern, update `72-threat-response-bundles.md` (or refactor an existing bundle) rather than duplicating controls across many memos.

- **Complexity budget:** each memo SHOULD keep its “new concepts per page” low. Prefer (a) referencing existing primitives, (b) adding one compact table, or (c) tightening cross-links, rather than introducing new taxonomies. If a memo adds a new interface, it MUST say what it replaces or why an existing one cannot be extended.

- **Concrete complexity budget (enforceable):**
  - The **join-key map** in `70-interoperability.md` MUST remain **one screen** (keep it tight; consolidate or demote anything that isn’t doing real cross-scope work).
  - Any memo’s **Interfaces** section SHOULD name **≤10 join-key families**; if you need more, refactor by (a) referencing `70` and (b) naming a primary set + an “only-if-applicable” set.
  - **Reader burden test:** a competent generalist SHOULD be able to read the **kernel** (`01`, `02`, `14`, `54`, `70`, `71`, `75`) in **≤3 hours** and understand the architecture. If not, tighten prose before adding more.


- **Adversarial review norm:** periodically run an explicit “red-team” pass on a subset of memos (threat models, secrecy, coercion, remedy). Treat the review itself as an input to refactoring (add tensions, name tradeoffs, tighten safeguards) rather than as commentary.

- **Independent review requirement (for major structural edits):** any change that (a) introduces a new ID family, (b) changes a core invariant (receipts/rules/remedy/records), or (c) weakens a safeguard MUST be reviewed by **two independent readers**, at least one of whom is explicitly asked to argue **against** the change.

- **No “feedback doctrine”:** external review notes are inputs to refactoring, not archive artifacts. Integrate or explicitly reject (with reasons) and then discard; do not add a permanent “feedback corpus” to the archive.

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
- **Mechanism justification test:** every new register/join-key/interface MUST be traceable to a concrete person-facing failure it prevents or an agency it enables ("without this, the person cannot see / challenge / correct X"). If you cannot complete that sentence, refactor or delete instead of adding.

- If a concept appears in **3+** places, refactor it into one canonical home:
  - the toolkit (`02-...`) for reusable primitives,
  - metrics (`03-...`) for decision loops and packs,
  - threats (`04-...`) and bundles (`72-...`) for failure modes and countermeasures,
  - interoperability (`70-...`) and register specs for join-keys and schemas.

- **Assurance cases** belong in `73-assurance-case-and-governance-safety-case.md`. Domain and scope memos SHOULD reference `AC-*` rather than duplicating the structure.

- Any join-key ID family listed in `70-interoperability.md` MUST have a single canonical memo that defines its minimum schema (table or YAML skeleton); `70` SHOULD point to that section.
- **Enumeration discipline:** shared enumerated fields (e.g., `DRR-KIND`, `DRR-TYPE`, `OFR-KIND`, lane `STATUS` states) MUST be defined in one canonical place; don’t introduce new values elsewhere—extend the canonical spec and update references.
- **Portable code discipline:** the portable code tables for `RC-*` (reasons), `AL-*` (appeal lanes), and `AO-*` (appeal outcomes) live in `52-reason-codes-registry.md`; other memos SHOULD reference them rather than inventing alternate codes.
- **Field-name hygiene:** avoid using join-key prefixes as field names (e.g., avoid `AL-ID`); use neutral names like `LANE-ID` / `LANES` and store the join-key values (`AL-*`) in the values.
- When adding a new primitive, update at least **two** memos to reference it (or don’t add it).

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
grep -ho "^[-*] \*\*\[BIB-[A-Z0-9-]*\]" 90-bibliography.md 91-bibliography-extended.md | grep -o "\[BIB-[A-Z0-9-]*\]" | sort -u > /tmp/bib_defined.txt
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


4) **No raw URLs in memos** (keep URLs in `90-bibliography.md` / `91-bibliography-extended.md` only)
```bash
grep -RE "https?://" *.md | grep -Ev "90-bibliography\.md|91-bibliography-extended\.md" && echo "FOUND RAW URL(S) — move to bibliography" || echo "OK"
```

If anything fails: fix the join-key/name now (renaming later is expensive).

## I. Revision notes (rev120+)

Unresolved (keep ≤10; each item MUST name target doc(s) and a deprecation plan):

- **none:** keep this list empty by default; add an item only when it has a target doc + a deprecation plan.

Recent resolved (keep last ~6; older milestones summarized in `00-README.md`):
- **rev156:** propagated person-facing invariants into resilience/critical infrastructure/energy/capital spend (`63`, `59`, `65`, `48`, `97`).
- **rev155:** tightened market/contract governance coherence: require machine-readable open contracting and strengthen contractual legibility clauses so vendor systems can’t defeat comprehension/no-wrong-door; propagated safe contestation posture into regulation and competition; added deterministic escalation expectations for ignored oversight findings (`22`, `38`, `13`, `94`, `32`, `55`).
- **rev154:** extended the contestation stack to include relational legitimacy signals: add dignity/comprehension hooks to delivery metrics (`03`) and clarify “the governed” category (AI tool today; participant framing noted in `01`, `06`, `42`).
- **rev153:** propagated person-facing invariants into legitimacy, legal legibility, epistemic infrastructure, standards governance, program evaluation, permissioning, and constitutional change; added a traceability-to-harm rule in archive governance.
- **rev147:** added canonical version semantics invariant + “no person join‑key” note (`70`); added residual category/no‑fit handling requirements (`44`, `47`); clarified remedy boundary (`08`); strengthened wait‑time tail + retaliation signal metrics (`82`, `03`); added archive self‑threat model (`96`) and updated person entry point to include ADS/human review (`75`).
- **rev146:** tightened complexity budget + independent review norms (`96`); elevated person-facing usability as a universal interface obligation (`71`) and toolkit invariant (`02` `IOP-34`); clarified entity-identifier limitations + DRR taxonomy maintenance (`70`).

## J. Debt register (≤10 items)

1. Standardize **Interfaces** sections across remaining scope and domain memos (ensure every memo names required join-keys and escalation paths).
2. Tighten cross-links between `19-compacts...`, `35-transfer...`, and `18-intergovernmental-finance...` (conditionality and remedy should be one mental model).

---

## K. Consistency checks (anti-drift; keep join-keys coherent)

Because this archive uses ID families (`RULE-*`, `DRR-*`, `ENG-*`, etc.) as “join keys”, **naming drift** breaks interoperability.

Minimal checks (run occasionally; keep lightweight):
- **No orphan prefixes:** if a new `XYZ-*` prefix appears, it MUST be defined in a register memo or the design toolkit, and referenced in `70-interoperability.md` if it is a join key.
- **No dead links:** internal `(\`NN-name.md\`)` links should resolve; fix as part of any edit that touches them.
- **No alias drift:** do not rename an existing prefix (`ENG-*` vs `PPR-*`) without a migration note and a mechanical sweep.
- **Map discipline:** `75-archive-map-and-entry-points.md` remains the single compact navigation surface—update it for any new memo.

(Implementation note: simple `ripgrep`/`grep`-based checks are enough; avoid adding heavy tooling unless the archive becomes large enough to justify it.)

