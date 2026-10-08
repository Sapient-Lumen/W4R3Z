# Person’s Path & Accessibility Invariants (Governance from Below)

**Purpose:** define the person/community path and accessibility floors that make every other artifact actually usable.

**Person served:** The person standing at the counter (or on the phone) trying to understand a decision and what they can do next.

**From-below:** This is the promise sheet you can use to demand access, safety, and a real remedy no matter how complex the system is.

**Why this exists:** the archive must remain navigable from the person at the counter (and their advocate), not just coherent for institutions.
(See `101-claude-rev142-normative-requirements.md` (NR-01, NR-04).)

**Canonical anchors:** this memo is the primary enforcement point for `101` requirements NR-01, NR-04, NR-05, NR-06, NR-08, NR-10, NR-12, NR-13, and NR-16.

This memo defines a **design test**: can a specific person—under stress, with limited resources—*understand what happened*, *prove what is true*, and *get timely relief*?

**Material floor (one sentence):** these invariants MUST have a lowest‑infrastructure, assisted variant (oral/phone/in‑person/paper) and MUST name the staffing/time/budget assumptions rather than shifting burden to the person. (See `101-claude-rev142-normative-requirements.md` (NR-13, NR-17).)

**Assistance & representation are first-class access floors:** every high-stakes interface MUST support assisted/oral paths (navigator, interpreter, disability support) and MUST disclose who can file/act on behalf of someone who cannot safely/self‑advocate (authorized representative/advocate), with conflict controls and an independent advocate option in high‑stakes domains. (See `101-claude-rev142-normative-requirements.md` (NR-12, NR-17); canonical interfaces: `36-...`, `47-...`, `82-...`.)

The archive is written in systems language (MUST/SHOULD/MAY; registers; join‑keys). This memo does **not** replace that. It provides the *person‑facing invariants* that make the theory of change real: **legibility → contestation → accountability**.

**Use:** attach these invariants to any high‑stakes service (`SRV-*`), decision receipt (`DRR-*`), enforcement flow, or automated system (`ADS-*`).

**No person-level join key (by design):** the archive does not define a universal person identifier. The governed person (or their advocate) is the integrator of their own governance experience using the receipts and artifacts they accumulate. Therefore systems MUST issue portable copies (paper + digital where available), MUST NOT require accounts/devices to retrieve past receipts, and SHOULD provide safe duplication/backup paths. (See `70-interoperability.md` and `31-records-foi-and-government-memory.md`.)

**Applies to collective subjects too:** when the governed subject is a community/collective person, interpret these invariants at the level of the community interface (authorized representatives, community advocates, or collective filings) rather than assuming an individual can self‑advocate (see `12-...`, `41-...`, `36-...`). (See `101-claude-rev142-normative-requirements.md` (NR-12).)

**See:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md` (ALR), `31-records-foi-and-government-memory.md` (DRR/receipts), `47-service-catalog-and-access-journeys-register.md` (SRV), `82-service-standards-and-minimum-service-guarantees.md` (service floors), `83-whistleblowing-and-protected-disclosures.md` (retaliation discipline).

## Concrete stakes (keep the person real)

These are representative failure modes this archive is meant to make **survivable and correctable**. Keep them concrete but *one sentence*; do not expand into narrative.

- **Voter registration rejected near an election** because a name/record mismatch can’t be corrected fast enough to meet the deadline → requires a receipt, a correction path that propagates once, and a deadline-triggered escalation.
- **Benefits cut by an automated classification** with no intelligible reason and no interim relief while an appeal queues → requires an explainable decision receipt, a usable appeal lane, and a non‑digital/non‑reading path to file and track.
- **A foster child’s record fails to follow them across jurisdictions** so accommodations and risks are invisible to the next caseworker → requires portable copies, interoperability that tolerates partial IDs, and a representation duty when the person cannot self‑advocate.

(See `101-claude-rev142-normative-requirements.md` (NR-01, NR-04, NR-20).)

## Kernel anchors (do not repeat)
- Remedy and appeals: `08-...`, `36-...`, `76-...`.
- Service catalog/journeys and service standards: `47-...`, `82-...`.
- Records/receipts and publication integrity: `31-...`, `53-...`.
- Protective legibility / adoption dynamics (so person-facing floors survive politics): `99-protective-legibility-and-adoption-dynamics.md`.

## Named tensions (design must surface these)
- Frictionless service vs safeguards against coercion/capture (don’t trade rights for convenience).
- Universal channels vs cost/capacity (but exclusions are not “efficiency”).
- Privacy/safety vs legibility for contestation (publish enough to challenge).
- Assistance/navigators vs dependence and gatekeeping power.
- Rights on paper vs ability to use them (literacy, safety, time, subsistence).

---
## A) The eight experiences (what being governed feels like)

Treat these as **failure modes** of the citizen–state interface. Good governance reduces their frequency and their harm.

1) **EXP-01 Opacity** — “I don’t know what is happening to me.”
2) **EXP-02 Waiting** — “My life is on hold and nobody can tell me when it will end.”
3) **EXP-03 Proof burden** — “I must prove I exist / qualify / deserve help.”
4) **EXP-04 Error** — “The system says something false about me and I can’t fix it.”
5) **EXP-05 Fear** — “If I complain, things will get worse.”
6) **EXP-06 Complexity** — “I can’t see the path forward.”
7) **EXP-07 Indifference** — “The rules were followed and I am still harmed.” (See `101-claude-rev142-normative-requirements.md` (NR-11).)
8) **EXP-08 Invisibility** — “I don’t fit the categories; the system can’t see me.” (See `101-claude-rev142-normative-requirements.md` (NR-10).)

(See `101-claude-rev142-normative-requirements.md` (NR-04).)

**Design rule:** every rights‑affecting system MUST be able to point to the specific artifacts that counter each experience (receipt, rules, deadlines, escalation, correction, representation).
**Memo convention:** include a single `**EXP pointer:**` line near the top of each interface memo naming the relevant `EXP-*` (see `96-archive-governance.md`).
**Counter-artifacts (typical pointers):**
- **EXP-01 Opacity →** `DRR-*` + `RULE-*` *as-of* (`31`, `39`, `25`) + explained reasons (`52`) + the service path (`47`).
- **EXP-02 Waiting →** time floors + escalation (`82`, `36`) + status updates in receipts (`31`) + oversight follow-through (`55`).
- **EXP-03 Proof burden →** proof-inventory + once-only + alternatives (`47`, `82`) + missing-doc denials that name substitutes (`31`).
- **EXP-04 Error →** correction lane + interim protection + propagation (`31`, `36`, `70`).
- **EXP-05 Fear →** safe filing + anti‑retaliation discipline (`83`, `77`) + separation from deciding authority (`36`).
- **EXP-06 Complexity →** explicit journeys + navigator/assistance channels (`47`, `98`) + “what to say / what to submit” (`31`, `36`).
- **EXP-07 Indifference →** hardship / equitable relief + exception discipline with receipts (`66`, `85`) + pattern remediation (`76`).
- **EXP-08 Invisibility →** recognition/category repair (`12`) + participation duty-to-respond (`41`) + systemic redress (`76`).

---

## B) Accessibility invariant (persona test)

For any remedy system (`AL-*`), service journey (`SRV-*`), or receipt (`DRR-*`) that affects rights/benefits/custody/housing/food/health:

**It MUST work for the following persona without special pleading:**
- functionally illiterate **or** low‑literacy in the dominant language,
- no reliable internet/smartphone,
- does not speak the dominant language well,
- has prior experience of retaliation or exclusion for complaining,
- has a time‑critical need (eviction, detention, essential service cutoff, benefits interruption).

If the design fails for this persona, it MUST be treated as a **governance defect**, not a “user education” problem.

**Minimum accommodations (non‑exhaustive):**
- offline filing + paper receipts (with tracking number),
- **no AI‑only or app‑only front door:** if chatbots/portals exist, there MUST be an equivalent staffed/non‑digital path; contestation must not require private tooling,
- translation/interpretation pathways,
- assisted navigation (navigator / ombuds intake),
- non‑reading modalities: allow **oral filing** and provide **audio / pictogram** summaries for the one‑screen “What happened / Why / What next” block when literacy is a barrier,
- time/subsistence realism: minimize steps and repeat visits; offer after‑hours/low‑travel options where feasible; do not gate urgent relief on time‑consuming documentation when safer substitutes exist (`82`, `09`),
- clear interim‑protection triggers for time‑critical harms,
- safe reporting options: confidential/anonymous intake where feasible, protected contact channels, and explicit anti‑retaliation pathways (see `83-...`, `08-...`, `36-...`). Remedy owners MUST also publish aggregate retaliation/chilling metrics (see `03-metrics-and-evidence.md` [LRR-14]). (See `101-claude-rev142-normative-requirements.md` (NR-08).)

---

## C) Comprehension test for Decision Receipts (DRR)

A `DRR` can be correct and still be unusable. Therefore:

- Person‑facing Decision Receipts MUST include a **plain‑language “What happened / Why / What next”** block (one screen), available in the person’s language (or via interpretation/translation).
- Receipts SHOULD be tested with representative users for **basic comprehension**: the person can correctly answer:
 1) what happened,
 2) the rule basis (as‑of),
 3) the deadline,
 4) where/how to contest,
 5) what interim protection exists (if any).
- If comprehension fails in testing, the receipt format MUST be revised (not merely appended to).

(Receipt minimum fields live in `31-records-foi-and-government-memory.md`.)

---

## D) Navigation duty (no wrong door)

When people are harmed, they rarely know which institution “owns” the problem.

- Any intake channel receiving a rights‑affecting complaint MUST either (a) accept the filing, or (b) route it to the correct lane/unit without losing deadlines (**no wrong door**).
- The decision‑making institution MUST not only *emit* a receipt but help the person *use* it: provide a plain‑language explanation and a navigator/ombuds route for high‑stakes harms.

- The system MUST provide a single tracking number that follows the complaint across rerouting.
- The `SRV-*` entry for a service MUST list the **front‑door** channels and the fallback escalation path (see `47-...` and ALR `36-...`).

---

## E) Waiting is harm (delay as first‑class failure)

- Service standards and remedy lanes MUST treat **missed response deadlines** as a defined outcome (e.g., “deemed denial” or “auto‑escalate”) rather than silence.
- Waiting time SHOULD be tracked as a harm proxy (especially where waiting creates eviction, job loss, hunger, or loss of custody). See `82-...` and `03-metrics-and-evidence.md`.

---

## F) Proof burden inventory and the once‑only principle

For each `SRV-*`, publish a **proof burden inventory**: what documents/claims are required, where they come from, and what alternatives are acceptable.

- Services SHOULD follow a **once‑only** principle: when the state already holds a fact, it should not repeatedly demand the person re‑prove it (subject to privacy and security constraints).
- When repeated proof is required (fraud controls, time lapse, changed circumstances), the `SRV-*` entry MUST state why and how to minimize burden. (See `101-claude-rev142-normative-requirements.md` (NR-06, NR-05).)

See: administrative burden framing [BIB-RSF-ADMINBURDEN-2018].

---

## G) Error correction duty (stop error propagation)

- Systems that store person‑referent facts (identity, eligibility, enforcement) MUST provide a **correction pathway** with deadlines and a receipt.
- Corrections MUST propagate to downstream systems that relied on the error (or publish a clear non‑propagation rule and the person’s recourse).
See `33-data-protection-and-personal-data-governance.md` and `44-identity-credential-and-eligibility-systems-register.md`.

---

## H) Remedy people fear is not remedy (retaliation discipline)

If filing a complaint plausibly increases harm, contestation collapses.

- Remedy channels MUST provide safe reporting options and explicit anti‑retaliation pathways.
- Programs SHOULD track a **retaliation signal** metric: allegations of retaliation after filings, substantiation rates, and protective actions taken (see `83-...`, `03-...`).

---

## I) Collective harms need collective filings

Many harms are too small to contest individually but large in aggregate.

- Remedy systems MUST support **collective filing** as a first‑class mode (opt‑in/opt‑out as appropriate), and MUST publish support/constraints in the ALR schema (`COLLECTIVE-FILING` in `36-...`). (See `101-claude-rev142-normative-requirements.md` (NR-12).)
- Where collective filing is not supported, the system MUST publish the substitute mechanism (class action, representative complaints, watchdog standing, pattern‑based redress; see `76-systemic-redress-and-pattern-remediation.md`).

---

## J) Those who cannot contest (representation duty)

Some affected parties cannot speak for themselves (children, future persons, the dead; and, in practice, many people under custody/control, severe disability, or incapacitation).

- Governance designs MUST support **representative filing** as a default (and disclose standing rules), rather than assuming the affected person can initiate.
- For **high‑stakes decisions** affecting a non‑self‑advocate (removal/placement, serious discipline, guardianship/custody, essential‑service cutoff under guardianship), the system MUST provide a discoverable **independent advocate / ombuds intake path** and SHOULD (where feasible) implement **AUTO‑ADVOCATE triggers** that do not depend on the potentially adverse guardian.
- Designs MUST include **conflict‑of‑interest handling** (e.g., when the guardian/household decision‑maker may be the source of harm) and safe routing to an independent channel.

See `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md`, `47-service-catalog-and-access-journeys-register.md`, `89-intergenerational-governance-and-future-obligations.md`, and `66-justice-and-administrative-justice-governance.md`.

(See `101-claude-rev142-normative-requirements.md` (NR-13).)

---

## K) Dignity and voice are load-bearing (relational legitimacy)

Contestable artifacts (receipts, reasons, remedy) are necessary but not sufficient if the lived interaction is degrading or dehumanizing. (See `101-claude-rev142-normative-requirements.md` (NR-17, NR-16).)

Minimum floor for high-stakes governance interfaces:
- **Voice:** the person MUST have a credible way to be heard by an accountable human (or a representative/advocate) where stakes are high; “form-only” or “bot-only” is insufficient for contested, consequential outcomes.
- **Dignity:** service interactions MUST not require humiliation by default (public disclosure of sensitive facts, repeated proof rituals, adversarial posture for basic entitlements). Provide privacy-preserving alternatives where feasible. (See `101-claude-rev142-normative-requirements.md` (NR-06, NR-05).)
- **Actionability:** dignity/voice failures MUST be receiptable and grievable (wired into `SRV-*` service standards `82-...` and remedy lanes `08-...`), so “the rules were followed” does not become a shield for harm.

(See `101-claude-rev142-normative-requirements.md` (NR-17).)
