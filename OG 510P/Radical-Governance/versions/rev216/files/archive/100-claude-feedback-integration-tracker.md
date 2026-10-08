# Claude Feedback Integration Tracker (rev216)

**Purpose:** keep Claude rev142 feedback integration systematic without duplicating it or inflating the archive.

This memo keeps a **compact pointer map** from Claude’s rev142 feedback bundle to concrete archive locations.
It is **not** a restatement of the feedback; it exists to keep ongoing integration work systematic without inflating the archive.

**Legend:** DONE / PARTIAL / PENDING.

---

## Kernel anchors (do not repeat)
- Claude feedback bundle (rev142) and current archive revision log: `00-README.md`.
- Density/complexity constraints for integration work: `96-archive-governance.md`.

## Named tensions (design must surface these)
- Fidelity to feedback vs archive size constraints (integrate by wiring, not duplication).
- Systemwide coherence vs local edits (avoid “one memo fixed, others drifting”).


## Part 1 — Structural observations (Claude rev142 Part 1)
- **Legibility trap (transparency ≠ accountability)** — DONE: `99-protective-legibility-and-adoption-dynamics.md`, `04-threat-models.md`, `00-README.md`; rev215 tightens the regime‑change hazard by adding an explicit **forced‑retreat** protocol (no silent unpublish; preserve record under protected access; publish safe substitutes) in `77-sensitive-information-and-secrecy-governance.md`.
- **Political economy of adoption (why would power accept constraints?)** — DONE: `99-protective-legibility-and-adoption-dynamics.md`, `80-implementation-roadmap.md` (adoption requirement), principles adoption note (`01-principles.md`). rev183 adds an explicit **compliance ratchet** and “compel records” minimal package alignment (`99`, `80`). rev204 adds a compact coalition prompt list in `80` (champions, external pressure points, demonstration wins, hostile environments) to reduce “handwave politics” failure.
- **The governed person’s experience** — DONE: `98-persons-path-and-accessibility-invariants.md` + propagated hooks (see `00-README.md` change log).
- **Core artifact registries must stay person-consumable (reasons/releases/follow-through)** — IMPROVED (rev191): wired `98-persons-path-and-accessibility-invariants.md` into `51` (REL), `52` (RC), `55` (OFR follow‑through), and `72` bundles so implementers don’t treat these as analyst-only artifacts.
- **Power, not just information** — PARTIAL→IMPROVED (rev162): strengthened “power map” + tension framing in `21-...`, `05-...`, `32-...`; continue coherence checks across remaining domain playbooks; rev165–166 adds kernel/tension blocks in `06`, `07`, `11`, `13`, `18`, `23`, `56`, `59`, `60`, `61`, `62`, `63`, `65`, `66`, `67`. rev168 extends the same kernel/tension wiring into the “governance mechanics” layer (`02`, `09`, `14`, `15`, `16`, `17`, `19`, `20`, `30`, `40`, `27`, `28`, `29`, `35`). rev188 adds explicit threat model **[TM-33]** for power asymmetry beyond information (`04-...`). rev208 propagates explicit [TM-29]/[TM-33] citations into the highest-stakes person-facing interfaces so “remedy people won’t use” and “legibility without follow-through” remain visible (coercion logs `05`/`43`, justice `66`, migration `67`, whistleblowing `83`).
- **Transition states / degraded modes** — DONE: Phase −1 bootstraps in `80-implementation-roadmap.md` and `99-protective-legibility-and-adoption-dynamics.md`.
- **Uneven adoption / missing registers (some comply, some don’t)** — IMPROVED (rev180): `70-interoperability.md` now requires degraded interop + publishes interface coverage/health snapshots.
- **Resist adding / keep archive tight** — ONGOING constraint: `96-archive-governance.md`.

---

## Part 2 — Cultural assumptions, capacity, and AI (Claude rev142 Part 2)
- **Cultural pluralism / functional equivalents** — DONE (rev161): `01-principles.md` (pluralism), `08-remedy-and-grievance.md` (form‑agnostic recourse), `34-competence-ledger-and-mandate-registry.md` (map reality; no legitimacy stamp); rev168 extends kernel/tension wiring into the “governance mechanics” layer (toolkit/scope/levels/standards/programs/permissioning/conditionality/state capacity: `02`, `09`, `14`, `15`, `16`, `17`, `19`, `20`, `30`, `40`, `27`, `28`, `29`, `35`). rev205 reasserts the “plural pathways” paragraph in `01-principles.md` (prevents drift).
- **Competing authorities: map as‑is, don’t launder reality** — DONE: `34-...` + Phase −1 guidance in `80-...`.
- **Low-infrastructure operations (no electricity / low bandwidth)** — DONE: `80-...` Phase −1 (receipt-first publishing modes).
- **AI as governance medium (chatbots, drafting, synthesis)** — DONE: `06-digital-and-algorithmic-governance.md` (“AI as the medium”), `42-automated-decision-systems-and-model-registry.md`.
- **AI systems as potential governed entities (uncertain standing; representation duty)** — IMPROVED (rev207): `06-digital-and-algorithmic-governance.md` scope note now acknowledges corporate/institutional governance over AI systems and routes contestation via the representation duty (`98`).
- **AI as a citizen-side contestation tool (machine-readable public artifacts)** — DONE: `06-...`, `51-release-registry.md`.
- **Inequality risk (AI-equipped vs non-equipped publics)** — PARTIAL→IMPROVED (rev162–164): explicit “no AI-only front door” + staffed/non-digital path requirements in `98-persons-path-and-accessibility-invariants.md` and `82-...`, plus no‑AI‑only identity gating (`12-...`) and no digital‑only gate for rights‑salient participation (`41-...`); continue propagation where digital gates appear; rev164 also tightened ALR/SRV channel requirements (`36-...`, `47-...`). rev204 hardens this as a universal scope obligation in `71-interface-obligations-by-scope.md`.

---

## Part 3 — Internal tensions, architecture notes, cross-reference gaps (Claude rev142 Part 3)
rev176 extends explicit **Named tensions** coverage into core “primitive” memos (remedy/records/interop/oversight/lifecycle disciplines) and standardizes the heading so scans are consistent.

- **Failure to act / omission framing (nonfeasance as policy)** — DONE (rev190): `04-threat-models.md` anchors this as **[TM-30]** (with **[TM-34]** kept as a deprecated alias) and the bundles/metrics wire it into enforceable artifacts (`72` B16; `03` CAD-2 zero‑throughput flags).
- **Clarified power-asymmetry threat split (retaliation/fear vs toothless enforcement)** — IMPROVED (rev198): [TM-29] now focuses on retaliation/fear (“remedy people won’t use”); dashboard-theater cases point to [TM-33] (e.g., `26`, `64`).
- **Name core tensions explicitly (legibility vs privacy; transparency vs retaliation; joinability vs justice)** — PARTIAL→IMPROVED (rev162–165): propagated tension statements into `21-...`, `05-...`, `32-...` in addition to `01/77/83/98` and the digital/fiscal/commons/emergency layer (`06`, `07`, `11`, `23`, `13`, `18`), plus epistemic/legal/metrics (`26`, `25`, `03`); rev166 extends named tensions into `56`, `59`, `60`, `61`, `62`, `63`, `65`, `66`, `67`; rev167 adds explicit kernel/tension blocks to `33`, `77`, `58`, and the `64/68/69` triad. rev168 adds explicit named tensions (and kernel anchors where missing) to the governance mechanics layer (`02`, `09`, `14`, `15`, `16`, `17`, `19`, `20`, `30`, `40`, `27`, `28`, `29`, `35`). rev211 makes the legibility↔safety (registry weaponization) tension explicit in `04-threat-models.md` so implementers see it at the threat layer.
- **Cross-reference gaps / ensure each domain memo points to the same kernel artifacts — PARTIAL→IMPROVED (rev162–165): added compact kernel-anchor blocks in `21-...`, `32-...`, `05-...`, `24-...`, plus domain propagation in `06`, `07`, `11`, `13`, `18`, `23`, and epistemic/legal/metrics (`26`, `25`, `03`); continue systematic pass across remaining domain memos (rev166 extends coverage to elections, cyber/CI, global, comms, housing, DRR, energy, justice, migration; rev167 adds the data/secrecy/constitutional integrity junction (`33`, `77`, `58`) and the benefits/education/labor triad (`64/68/69`)). rev168 extends the same “kernel anchors” approach into core mechanics memos (scope + levels-of-government + standards + permissioning/conditionality/program evaluation: `02`, `09`, `14`, `15`, `16`, `17`, `19`, `20`, `30`, `40`, `27`, `28`, `29`, `35`). rev170 extends the same kernel/tension wiring into key **register-layer** memos (`37`–`39`, `41`–`46`, `48`–`50`, and `71`) so implementers encounter the same constraints everywhere.
- **Universal `98`/`99` kernel anchors** — IMPROVED (rev195) + CLOSED (rev210): every non-bibliography memo now explicitly anchors both person‑path (`98`) and protective legibility/adoption (`99`) to reduce drift (including register/navigation/safety-case/verification memos that previously lagged).


- **Commons↔fiscal/revenue junction** — IMPROVED (rev184): `11-commons...` now explicitly anchors fiscal substrate (`07`, `93`, `18`) and `07`/`93` now carry a compact commons/eco junction note so ecological limits and the revenue/budget story remain joinable.
- **DRR taxonomy maintenance trigger (avoid `DRR` as a god-object)** — IMPROVED (rev185/212): `70-interoperability.md` now includes an explicit threshold to prompt refactor/splitting when `DRR-TYPE` proliferates. rev212 adds the matching maintenance rule at the DRR schema (`31-records-foi-and-government-memory.md`).
- **EID gap note (entity identity is a bundle; invest in entity resolution)** — DONE (rev213): `70-interoperability.md` now includes a canonical EID note (no trusted global entity registry; invest proportional to corruption/capture risk; avoid false merges).
- **Version semantics invariant (monotonic revisions; change metadata; point-in-time retrieval)** — IMPROVED (rev216): `70-interoperability.md` now makes issuer/authorizing decision metadata explicit and requires point‑in‑time retrieval for any versioned object.
- **Person-as-integrator / no person join-key (privacy-preserving):** IMPROVED (rev206): `98-persons-path-and-accessibility-invariants.md` now states this explicitly (portable copies; no account/device gate; safe duplication).
---
- **Remaining navigation/checklist docs now carry the same wiring cues** — IMPROVED (rev177): added compact `Kernel anchors` + `Named tensions` blocks to `10-micro-local.md` and `92-boundary-change-checklist.md`, and upgraded `95-template-design-memo.md` to require a person-served sentence plus explicit kernel/tension sections.

- **Mechanism justification test (every structure traces to person harm prevented / agency enabled)** — DONE (rev207): added as an explicit rule in `96-archive-governance.md` and required in `95-template-design-memo.md`.

- **Comprehensiveness vs cognitive manageability (complexity budget)** — IMPROVED (rev171): `96-archive-governance.md` enforces a concrete complexity budget; `70-interoperability.md` refactored to a true one‑screen join-key map with domain add‑ons.
- **Archive self-threat-model (spec as a hazard)** — IMPROVED (rev180): `96-...` now includes a brief self-threat-model covering control-apparatus risk, paperwork theatre, register sprawl, and capture/legitimacy laundering.
- **Foundational wiring normalization** — IMPROVED (rev181): standardized `Kernel anchors` + `Named tensions` sections in the remaining foundational memos (`01-principles.md`, `04-threat-models.md`, `72-threat-response-bundles.md`).


## Parts 4–10 — Purpose, person’s path, resistance/hope, material floor, and closing notes
These parts are largely *orientation* and *ethical constraints* rather than new registers.
Key integration anchors in the archive:
- **Those who cannot contest (children/incapacity/future persons/the dead)** — IMPROVED (rev196): representation duty is now explicit and wired into the *interfaces* people actually touch: `98-persons-path-and-accessibility-invariants.md` clarifies **AUTO‑ADVOCATE triggers** + conflict‑of‑interest routing; `47-...` requires `SRV-*` entries to disclose representative filing + safe non‑guardian routes; `36-...` adds an explicit `REPRESENTATION` field for appeal lanes. Domain hooks: advocate/ombuds CC requirement in `64-...` and `68-...`; durable record framing in `31-...`/`53-...`; future-persons parallel in `89-...`.


- **What this project is about (legitimacy as lived contestability)** — PARTIAL→IMPROVED (rev177): `96-archive-governance.md` adds a purpose-sentence rule and `95-template-design-memo.md` now requires naming the concrete person/community served (keeps the “why” visible without expanding every memo). `00-README.md`, `21-...`, `98-persons-path-and-accessibility-invariants.md` (continue tightening “why” language across sector memos).
- **Humility about authorship / test against lived experience** — IMPROVED (rev216): `00-README.md` now includes an explicit process note (AI assistance; treat as a proposal to be contested and field-tested, not doctrine).
- **Plain speech + precision (one-sentence purpose in each memo)** — DONE (rev195): applied a one‑sentence **Purpose** line across the entire archive (not just the oversight/register layer), keeping from‑below intent visible everywhere.
- **What this adds relative to existing frameworks (positioning)** — IMPROVED (rev189): `00-README.md` states the archive’s distinct contribution (integration, protocol‑level specificity, adversarial design, and scale‑free composability).

- **Theory of political agency (who contests; who uses the joins)** — IMPROVED (rev182): `99-protective-legibility-and-adoption-dynamics.md` now includes a minimal actor-map and the “capacity is unequal” implication (friction minimization + advocate hooks).
- **Material floor (revenue + time/subsistence constraints)** — IMPROVED (rev204–205): `21-legitimacy-architecture.md` names the material floor tension; rev205 adds a “funded public good” note in `07-fiscal-and-budgetary-governance.md` and a time/subsistence barrier bullet to `36-appeal-lanes-and-redress-registry.md`.
- **Resistance / hope / community** — PARTIAL→IMPROVED (rev162–178): added explicit “hope (not optimism)” and community-capacity notes in `10-...` and `24-...`; rev175 wires community continuity explicitly into emergency governance (`23-...`) and public health (`57-...`) via kernel anchors; rev178 adds an explicit **resistance boundary** note so remedy structures are framed as the alternative to resistance, not its refutation (`01-...`, `08-...`, `04` [TM-31]).

- **The eight experiences of being governed (from below) as a design checklist** — IMPROVED (rev180): `98-persons-path-and-accessibility-invariants.md` now assigns `EXP-*` codes and points to counter‑artifacts; `95-...` template asks designers to name which experiences are primary; `75-...` person entry point aligned.
- **Receipts must be comprehensible (not just joinable)** — IMPROVED (rev172): strengthened DRR comprehension test + missing-doc denial requirements in `31-...`; tightened proof burden inventory + once-only defect framing in `47-...`. rev205 adds an explicit language/format accessibility invariant in `31-records-foi-and-government-memory.md`. rev210 adds an explicit **non‑reading modality** requirement (oral + audio/pictogram equivalents) and makes FOI intake explicitly support assisted/oral filing (also in `31`).
- **Retaliation / chilling monitoring** — IMPROVED (rev172): added a cross-lane post‑filing adverse‑action uplift monitor to `03-...` and refined `83-...` minimal metrics.
- **Collective filing as first-class remedy input** — IMPROVED (rev173): ALR minimum fields now include `COLLECTIVE-FILING` (`36-...`), and systemic redress explicitly accepts/acknowledges collective filings + requires disclosure in lane records (`76-...`).
- **Lawful-but-harmful rules boundary (individual remedy can’t fix politics)** — IMPROVED (rev187): `76-systemic-redress-and-pattern-remediation.md` now names the boundary and routes such patterns to rule/policy change interfaces (`41`, `88`, `28`).
- **Individual harms → political response (pattern legibility as a civic input)** — IMPROVED (rev211): `08-remedy-and-grievance.md` now explicitly names that the purpose of making harms legible is also to surface patterns that demand systemic redress and, when rules work as written but harm persists, rule/policy change routing (`76` ↔ `41/88/28`).
- **Correction propagation made person-auditable** — IMPROVED (rev173): Decision Receipt guidance now calls for downstream notification/ack status for corrections to joinable records (`31-...` ↔ `70-...`).
- **Material floor (governance requires a substrate)** — IMPROVED (rev164–166): rev164 adds an explicit material-floor note in `00-README.md` and strengthens low‑literacy/oral access requirements in `98`, `36`, `47`, and `82`; rev166 adds explicit degraded‑mode channel examples in `47-...` and `61-...` (continue to audit any memo that assumes capacity). rev182 makes the same constraint explicit inside adoption dynamics (`99-protective-legibility-and-adoption-dynamics.md`) so implementers see it when thinking about legibility → contestation. rev204 names the same tension inside legitimacy architecture (`21-legitimacy-architecture.md`) so it is visible where legitimacy stacks are composed.
- **Micro-local as a start point (visible wins)** — IMPROVED (rev181): Phase 0 sequencing in `80-implementation-roadmap.md` and the “severe constraint” entry point in `75-archive-map-and-entry-points.md` now explicitly recommend starting with `10-micro-local.md` where the person’s path is shortest.
- **Bibliography as evidence docket (traceability without bloat)** — IMPROVED (rev181): `91-bibliography-extended.md` now names its role as the archive’s evidence docket and reinforces density policy.
- **Collapse boundary: preserve the record** — IMPROVED (rev181): `53-publication-integrity-and-tamper-evident-logs.md` adds a collapse-boundary section; `05-public-safety-and-coercion.md` notes record preservation during drift toward violence.
- **Records as voice for the dead** — IMPROVED (rev197): `53-...` now names the moral reason record integrity matters (the dead cannot contest; the record speaks for them).
- **Precision as moral force (one-sentence stake)** — IMPROVED (rev181): `95-template-design-memo.md` now requires a “Moral stake” sentence so mechanisms stay tied to what is owed by power.
- **Guided navigation / assisted intake (no prior legal knowledge required)** — IMPROVED (rev187): ALR now explicitly requires a guided navigation/assisted intake path (`36-...`), reinforcing the navigation duty framing in `08-...` and `98-persons-path-and-accessibility-invariants.md`.
- **Person’s Path entry point in the archive map** — DONE (rev180): `75-archive-map-and-entry-points.md` now includes a person/community entry path (receipt → reasons → contest lane).
  - rev186: cleaned and unified the person/community entry block in `75` (removed duplication; repaired formatting).
- **Accessibility invariant explicitly stated in `08`** — DONE (rev180): remedy memo now carries the concrete persona test and points to `98-persons-path-and-accessibility-invariants.md`.
- **Severe-constraint operational detail (carbon-copy receipts)** — DONE (rev180): Phase −1 now names pre-numbered carbon-copy receipt pads as the minimal implementation substrate.
- **Receipt language access (in the person’s language)** — IMPROVED (rev180): comprehension test now requires the one-screen block be available in the person’s language (or via interpretation/translation).

