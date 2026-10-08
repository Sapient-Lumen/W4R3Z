# Archive Governance (How the Research Program Stays Coherent)

**Purpose:** keep the research program coherent and small by enforcing density, cross-linking, and safety constraints.

**Person served:** Maintainers and implementers who need a small, coherent archive that stays accountable to governed people as it grows.

**From-below:** This sets the rules that keep the archive honest—versioned, contestable, and aligned with the people it claims to serve.

This archive is designed to grow *slowly* while remaining decision-useful.

**Legitimacy note:** this archive is an expert-authored design *proposal*, not a democratic constitution. It should be treated as a starting point for public contestation and co-design—adopt/adapt/reject based on what governed communities choose, and record deviations explicitly (with reasons) rather than pretending one universal implementation exists. (See `101-claude-rev142-normative-requirements.md` (NR-03, NR-18).)

**Archive self-application note:** treat changes to this archive as governance acts: avoid silent edits; record reasons and review paths (revision log + tracker + issues) so the archive remains contestable and auditable.
(See `101-claude-rev142-normative-requirements.md` (NR-18).)

**Language note:** the archive’s MUST/SHOULD/MAY language is intentionally “spec-like” so obligations are testable and don’t dissolve into polite recommendation. Treat MUSTs as *owed* person-facing floors, and keep each memo’s Purpose line from‑below (what harm prevented / agency enabled).

**Citation migration rule:** when a memo is justified by Claude rev142 constraints, cite `101-claude-rev142-normative-requirements.md` (NR-xx) (or the canonical internal anchor listed there) rather than citing `sources/claude-feedback/rev142` directly. Existing direct citations are acceptable during migration but SHOULD be removed as touched.

**Dual-audience rule:** every memo MUST include (near the top) a single plain‑language sentence that says what the artifact lets a person do (or what harm it prevents), written as if to the person at the counter; keep it ≤40 words. This keeps *purpose visible inside mechanism* without bloating the archive.
(See `101-claude-rev142-normative-requirements.md` (NR-01, NR-04, NR-17).)

**EXP pointer rule:** any memo that proposes an interface, registry, lane, checklist, or obligation MUST include a single `**EXP pointer:**` line naming the governed-experience failure modes it must counter (see `98-persons-path-and-accessibility-invariants.md`; `101-claude-rev142-normative-requirements.md` (NR-04)).

**Assistance & representation rule:** any memo that defines a person-facing filing path (service intake/journey `SRV-*`, remedy/complaints `AL-*`, record access/FOI, inspection/enforcement findings, or public participation `ENG-*`) MUST include a one-line `**Assistance & representation:**` field near the top that discloses (a) staffed/assisted/oral + offline paths, and (b) who can file/act on behalf of someone (advocate/authorized representative, collective filing) and how conflicts/consent are handled. Default to the canonical anchors (`98`, `36`, `47`). (See `101-claude-rev142-normative-requirements.md` (NR-12, NR-17).)

**Proof burdens rule:** any memo that defines eligibility/permissioning/verification gates MUST include a one-line `**Proof burdens:**` field (or cite where defined) naming required evidence classes, least-burdensome alternatives, and “once-only” retrieval of state-held facts; adverse outcomes MUST cite `RC-*` reason codes + a contestation lane (`47`, `44`, `52`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-06).)

**Join constraints rule:** any memo that introduces or depends on cross-scope joins, identifiers, entity resolution, or data sharing MUST include a one-line `**Join constraints:**` field near the top naming the empowered use‑path + corrective action (per `70`), minimization/purpose limits, and a narrow alternative when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `101-claude-rev142-normative-requirements.md` (NR-14).)

**Authority + retaliation rule:** any memo defining a lane, enforcement path, oversight channel, or compliance interface MUST include one-line `**Authority:**` and `**Retaliation safety:**` fields near the top (binding vs advisory; escalation; protected filing); the retaliation line MUST include at least one degraded/offline safe channel and a privacy‑safe chilling indicator (`03` IPM‑4) or cite `83` as the controlling floor (`83`, `77`, `98`, `03`). (See `101-claude-rev142-normative-requirements.md` (NR-08, NR-09).)

**Mercy / interim protection rule:** any memo that defines a hard edge (sanction, shutoff, custody/control, deprivation) MUST include a one-line `**Mercy / interim protection:**` field describing the waiver/exception path and interim protection/stay triggers (missed deadlines, pending review, hardship), or explicitly cite the canonical anchors (`85`, `82`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)

**As-of & corrections rule:** any memo specifying a register/registry/inventory/log that people rely on to contest decisions MUST include a one-line `**As-of & corrections:**` field stating point-in-time semantics and how corrections propagate (see `31`, `53`, `70`, `73`). (See `101-claude-rev142-normative-requirements.md` (NR-07, NR-15).)

**Notices & receipts rule:** any memo defining a binding decision or rights‑affecting outcome MUST include a one-line `**Notices & receipts:**` field near the top committing to a comprehension-tested Decision Receipt that meets the `31` minimum fields (incl. consequence triggers, interim protection/mercy where available, the binding follow‑through lane, and a safe/offline contestation channel — no personal device required — per `83-...`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-08, NR-15).)

**Receipt “as-of” + windows rule:** any memo that relies on person-facing notices/receipts (`DRR-*` or equivalent) MUST ensure the receipt cites controlling `RULE-*`/`STD-*`/`SRV-*` **as-of** and discloses deadlines/time limits and whether lanes can bind; default to the minimum receipt fields in `31-records-foi-and-government-memory.md`. (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-09, NR-15).)

**Mercy note:** this archive can specify accountability infrastructure, but not the human practice of mercy. Designs MUST keep bounded discretion spaces structurally possible—and govern them so mercy isn’t favoritism and cruelty isn’t hidden procedure (route hard edges through `85-waivers-variances-and-exceptions-discipline.md`, with reasons + review). (See `101-claude-rev142-normative-requirements.md` (NR-16).)

## Kernel anchors (do not repeat)
- Complexity/manageability budget is a first-class constraint: `96` is the enforcement point.
- Interop is the default join surface (don’t add new interfaces casually): `70-...`.
- Person-facing floors and safety: `98-persons-path-and-accessibility-invariants.md`, `77-...`.
- Protective legibility + adoption dynamics: `99-protective-legibility-and-adoption-dynamics.md`.

- Claude rev142 normative requirements anchor: `101-claude-rev142-normative-requirements.md` (use for new citations; retire raw feedback sources when feasible).

**Time bounds & escalation rule:** any memo defining a lane, enforcement path, oversight channel, or compliance interface MUST include a one-line `**Time bounds & escalation:**` field naming (a) ack/decision deadlines, (b) the no-response rule (auto-escalation or interim protection), and (c) tail-wait publication for high-harm classes; default to `82-service-standards-and-minimum-service-guarantees.md` and the receipt minimums in `31-records-foi-and-government-memory.md`. (See `101-claude-rev142-normative-requirements.md` (NR-05).)
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
**Purpose sentence rule:** each memo MUST include (early, preferably in the opening paragraph) a **one‑sentence, from‑below** `**Person served:** ...` line naming the governed person/community it serves (or the concrete harm it prevents) and what they need. Where feasible, also add a one‑sentence `**Moral stake:** ...` obligation line. Keep both short—this is a navigation/grounding duty, not a new essay. (See `101-claude-rev142-normative-requirements.md` (NR-01).)

**Concrete case test:** if a memo introduces a new interface/register/join-key, it MUST name (in ≤1 sentence) a concrete failure mode it prevents for a real person/community—or cite `98` “Concrete stakes” instead of inventing a new vignette. (See `101-claude-rev142-normative-requirements.md` (NR-04, NR-20).)

**Person’s Path test:** if a memo adds/changes a structure (receipt/register/lane/join‑key/metric), it MUST state (≤3 bullets, or by citing `98`) how the governed person finds it, uses it, and what the fail‑safe is if they can’t (navigator/ombuds + offline channel). (See `101-claude-rev142-normative-requirements.md` (NR-04, NR-01).)

**Map discipline:** any new memo that stays in the archive MUST add (or update) a one-line entry in `75-archive-map-and-entry-points.md` **and** be referenced from at least **two** other memos (otherwise merge/refactor instead of adding).

## B. Size and structure constraints
- **ID naming discipline:** when referring to joinable objects, prefer the archive’s ID families (`PROG-*`, `EVAL-*`, `STD-*`, etc.) over generic phrases (“Program IDs”) to prevent drift.

- **Density budget (default):** significant additions SHOULD be offset by deletions/refactors elsewhere (replace rather than append). If a new memo is added or a memo grows materially, name what gets removed/merged; if you can’t yet, record a one-line pruning plan in the Debt register. (See `101-claude-rev142-normative-requirements.md` (NR-20, NR-14).)

- **Material floor disclosure (default):** if you introduce a new MUST that creates ongoing operational load (staffing/adjudication/translation/publication), you MUST name the minimal resourcing mode in one sentence (or cite where it is funded/operated, e.g., `07` MVF / `80` Phase −1). For person-facing flows, you MUST also state the non-reading/offline path (or cite `98`/`82`). Prefer the header field `**Material floor (one sentence):**` in the from‑below header. (See `101-claude-rev142-normative-requirements.md` (NR-13).)

- **New ID families:** add only when a real interface gap exists; when added, include a minimal schema, add it to the one-screen join-key map in `70-interoperability.md`, and reference it in **2+ memos**.

- **Join-key homes:** if a join-key (`REL-*`, `RC-*`, etc.) is referenced across memos, it MUST have an explicit “home” spec (a dedicated registry memo or a clearly named section in an existing memo). Avoid “floating interfaces.”

- **Threat→control hygiene:** if you add/modify a `TM-*` mitigation pattern, update `72-threat-response-bundles.md` (or refactor an existing bundle) rather than duplicating controls across many memos.

- **Complexity budget:** each memo SHOULD keep its “new concepts per page” low. Prefer (a) referencing existing primitives, (b) adding one compact table, or (c) tightening cross-links, rather than introducing new taxonomies. If a memo adds a new interface, it MUST say what it replaces or why an existing one cannot be extended.

- **Resist adding (default):** avoid (a) country‑specific implementation guides, (b) technology prescriptions (platform/blockchain/etc.), (c) extensive private/corporate governance redesign, (d) new registers/ID families unless a real interface gap exists, and (e) philosophical foundations that don’t change operational obligations. Put such material in derivative documents. (See `101-claude-rev142-normative-requirements.md` (NR-20).)

- **Legibility-with-bite rule (enforceable):** if a memo proposes new transparency/receipt/registry surfaces, it MUST also name the follow‑through mechanism: (a) who can compel/act, (b) what consequence triggers when ignored, and (c) how an affected person (or advocate) can invoke it — or cite `21-...` (A1) / `04` [TM-33] / `32`/`08`/`82` instead of handwaving.

- **Concrete complexity budget (enforceable):**
 - The **join-key map** in `70-interoperability.md` MUST remain **one screen** (keep it tight; consolidate or demote anything that isn’t doing real cross-scope work).
 - Any memo’s **Interfaces** section SHOULD name **≤10 join-key families**; if you need more, refactor by (a) referencing `70` and (b) naming a primary set + an “only-if-applicable” set.
 - **Reader burden test:** a competent generalist SHOULD be able to read the **kernel** (`01`, `02`, `14`, `54`, `70`, `71`, `75`) in **≤3 hours** and understand the architecture. If not, tighten prose before adding more.

 (See `101-claude-rev142-normative-requirements.md` (NR-03).)

- **Adversarial review norm:** periodically run an explicit “red-team” pass on a subset of memos (threat models, secrecy, coercion, remedy). Treat the review itself as an input to refactoring (add tensions, name tradeoffs, tighten safeguards) rather than as commentary.

 (See `101-claude-rev142-normative-requirements.md` (NR-14).)

- **Independent review requirement (for major structural edits):** any change that (a) introduces a new ID family, (b) changes a core invariant (receipts/rules/remedy/records), or (c) weakens a safeguard MUST be reviewed by **two independent readers**, at least one of whom is explicitly asked to argue **against** the change.

- **No “feedback doctrine”:** external review notes are inputs to refactoring, not archive artifacts. Integrate or explicitly reject (with reasons) and then discard; do not add a permanent “feedback corpus” to the archive. Temporary vendoring under `sources/` for citation **during active integration** is allowed only if it includes an explicit removal target (date or revision threshold). See `../sources/claude-feedback/rev142/README.md` for the removal target. Prefer citing `101` (or canonical internal anchors) rather than the raw feedback files.
 (See `101-claude-rev142-normative-requirements.md` (NR-09).)

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
- **Mechanism justification test:** every new register/join-key/interface MUST be traceable to a concrete person-facing failure it prevents or an agency it enables ("without this, the person cannot see / challenge / correct X"). If you cannot complete that sentence, refactor or delete instead of adding. (See `101-claude-rev142-normative-requirements.md` (NR-01, NR-04).)
- **Join use‑path requirement:** don’t add join‑keys or interop interfaces solely to make the system “more joinable.” Each join MUST name (a) who uses it, (b) what corrective action follows, and (c) how the person can trigger/benefit (via `98`). If you cannot name a use path, treat the join as design debt and prefer narrower/receipt-based bridging. (See `101-claude-rev142-normative-requirements.md` (NR-20, NR-14).)

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
- Prefer **verbs over nouns**: if a memo proposes a new person-facing artifact (receipt, register, lane), it MUST include a minimal **process sketch** (≤5 bullets: what happens in the room) or cite an existing canonical process memo (`08`, `36`, `82`). (See `101-claude-rev142-normative-requirements.md` (NR-20, NR-14).)
- Prefer **field‑tested person claims** over armchair narratives: when a memo describes a governed person’s experience, treat it as a hypothesis to be validated (or explicitly marked as an assumption), and invite correction from those with lived experience. (See `101-claude-rev142-normative-requirements.md` (NR-04).)

## G. Debt register (keep refactors visible)
- Maintain a short list (≤10 bullets) of the most important refactors or missing primitives.
- Each item MUST include: owner (or “unassigned”), target doc(s), and a deprecation plan for redundant text.
- Delete or resolve items aggressively; do not let this become a second backlog.

## H. 60-second lint protocol (manual; no code committed)
**Operator note:** when using LLMs to edit this archive, follow `126-llm-archive-operator-protocol.md`.

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

See `102-revision-log.md` for the running change history (kept out of the main README to keep entry points small).

Unresolved (keep ≤10; each item MUST name target doc(s) and a deprecation plan):

- **none:** keep this list empty by default; add an item only when it has a target doc + a deprecation plan.

Recent resolved (keep last ~6; older milestones summarized in `00-README.md`):
- **rev282:** clarified the boundary between individual remedy and political change: when rules work *as written* and still harm, governance must make the pattern legible and route it into systemic redress + rule‑change participation (`08`, `41`, `76`).
 (See `101-claude-rev142-normative-requirements.md` (NR-11).)
- **rev281:** implemented Claude’s “invisibility / no category fit” requirement by adding residual handling + category-edge review duties to `SRV-*` and service standards (`47`, `82`) and anchoring identity residual handling provenance (`12`).
 (See `101-claude-rev142-normative-requirements.md` (NR-10).)
- **rev280:** made proof burdens first‑class and measurable by requiring `SRV-*` to publish a proof burden inventory (interaction count + time/cost estimate + state‑held vs applicant‑supplied) and wiring it into service standards (`47`, `82`, `95`).
 (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-06).)
- **rev279:** propagated Claude’s “waiting is harm / deny‑by‑delay” constraint into migration (`67`) and administrative justice (`66`) so delay becomes a first‑class, auditable governance harm in rights‑salient processes (deadlines + duty‑to‑account + interim protection where delay moots rights).
 (See `101-claude-rev142-normative-requirements.md` (NR-05).)
- **rev278:** extended the ADS/MOD registry and contracting interface so foundation‑model AI and shared AI services are treated as governance infrastructure (not just “decision tools”), ensuring upstream AI mediation is registered/versioned and contract‑linked (`42`, `38`).
- **rev277:** anchored the epistemic/evidence/publication layer (`26`, `37`, `51`) to Claude’s legibility-trap + power-beyond-information constraints (publication is not power) with minimal wiring to `TM-33`/`TM-35` and the oversight/remedy loop.