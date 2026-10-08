# Public Communication & Information Integrity (Cross-scope)

**Purpose:** support truthful public communication without turning ‘information integrity’ into censorship or propaganda.

**Person served:** A resident trying to make decisions with accurate public information—especially in crises—who needs provenance, corrections, and protection from manipulative or coercive messaging.

**From-below:** This keeps official communication honest and corrigible so misinformation and spin don’t become policy tools without consequence.

**EXP pointer:** `EXP-01` (Opacity), `EXP-02` (Waiting), `EXP-05` (Fear) — see `98-persons-path-and-accessibility-invariants.md`.

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)
**Assistance & representation:** publish staffed/oral/offline paths (incl. interpretation) and who can act on behalf of someone (advocate/authorized representative); allow third‑party/collective filing where harms are collective or the person can’t safely file; disclose conflict/consent rules (see `98`, `36`, `47`, `41`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).
**Authority:** communications MUST clearly label what is *binding* (`RULE-*`) vs *advisory* (`REL-*` only), and route any coercive effect through a receipted `DRR-*` with `AL-*` remedy. (See `101-claude-rev142-normative-requirements.md` (NR-09, NR-02).)
**Retaliation safety:** when publishing guidance, avoid doxxing targets/witnesses; offer protected contact and reporting routes (`77-...`, `83-...`); include at least one degraded/offline safe channel (no personal device required) and publish a privacy‑safe chilling indicator (`03` IPM‑4). (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed, a timely challenge is pending, or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**Proof burdens:** interventions that restrict reach/visibility or label content MUST disclose evidentiary standards + who must prove harm/falsehood; prefer least-restrictive remedies and “once-only” access to state-held facts; adverse outcomes cite `RC-*` + `AL-*` (`44`, `03`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-06).)
**Join constraints:** cross‑scope joins/IDs/data sharing MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and provide a narrow fallback when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-14).)


**Problem class:** legitimacy depends on shared public facts, especially in emergencies. Real systems fail through **silent edits**, inconsistent guidance, propaganda/capture, and “decision by press release” with no remedy.

**Design goal:** treat official communication as **auditable infrastructure**: publish canonical statements as joinable artifacts (`REL-*` + `RULE-*` + `DRR-*`), issue corrections with stable IDs, and preserve free expression while making state claims **verifiable, revisable, and contestable**.

This memo complements:
- `26-epistemic-infrastructure-and-public-knowledge.md` (releases + methods + correction discipline),
- `33-data-protection-and-personal-data-governance.md` (privacy constraints on comms + analytics),
- `56/57/59` (domain spines that depend on reliable comms).

## Kernel anchors (do not repeat)
- Person-facing invariants: `98-persons-path-and-accessibility-invariants.md` (incl. non‑digital/non‑reading options), service journeys `47-...`, remedy lanes `36-...` / `08-...`.
- Protective legibility + adoption dynamics: `99-protective-legibility-and-adoption-dynamics.md` (transparency ≠ accountability; identify who loses discretion / who gains contestation capacity).
- Publication integrity (no silent edits; “as‑of” access): `53-...` and `31-...` where relevant.
- Secrecy/retaliation constraints (whistleblowers, safety, security): `77-...`.
- Where comms mediates determinations (chatbots, scripted advisories): treat as part of ADS governance (`06-...`).

## Named tensions (design must surface these)
- Speed vs accuracy and uncertainty (fast guidance vs wrong guidance).
- Central consistency vs plural trusted messengers (avoid single‑channel fragility).
- Counter‑misinformation posture vs free expression and political abuse.
- Transparency vs retaliation/security (some disclosures increase danger).
- Audience analytics/personalization vs privacy and manipulation risk.

---

## A. Minimum Viable Public Communication Integrity System (MVPCIS)

### 1) Canonical channel + “as-of” access
- MUST: maintain a canonical, timestamped public channel where authoritative guidance lives (web page + API optional).
- MUST: maintain a low‑tech broadcast/posting fallback (e.g., community radio, SMS, print, public noticeboards) for outages/low‑bandwidth/low‑literacy contexts; publish where to find it. (`98-persons-path-and-accessibility-invariants.md`)
- MUST: every material advisory/claim is a `REL-*` release (or part of a versioned `REL-*` series) with:
  - scope (who/where it applies),
  - method note (how it was derived),
  - change log (what changed and why),
  - and links to any enabling `RULE-*` and affected-service `SRV-*` objects.
- MUST: preserve “as-of” access (people can retrieve what was published when). See `53-publication-integrity-and-tamper-evident-logs.md`.

- SHOULD: if AI systems draft or mediate official responses, label the channel and preserve a human-authored pathway for rights-affecting interactions; treat AI-mediated determinations as requiring receipts. (`06-...`, `42-...`, `31-...`)

### 2) Corrections, retractions, and uncertainty are first-class
- MUST: **no silent edits** of public guidance that affects rights/resources; corrections publish as new `REL-*` entries that link the prior version.
- MUST: publish an “uncertainty rubric” for high-stakes guidance (what is known, what is plausible, what is unknown, and when the next update is expected).
- SHOULD: publish a compact correction taxonomy (e.g., *clarification*, *material change*, *error*), with stable reason codes (`RC-COMM-*`).

### 3) “Decision by announcement” is illegal in the archive’s model
- MUST: if a communication has coercive effects (restrictions, eligibility, enforcement posture, platform orders), it MUST be grounded in `RULE-*` and emit a `DRR-*` receipt citing:
  - and the person-facing text MUST pass the comprehension test (what changed, why, what to do next, by when) under the `98-persons-path-and-accessibility-invariants.md` persona constraints; publish an offline/phone path where needed.
  - legal basis (`RULE-*` as-of),
  - reasons (`RC-*` + plain language),
  - evidence releases (`REL-*`),
  - and remedy (`AL-*`).
- SHOULD: for emergency guidance that is *not* binding, label it explicitly as non-binding and link the binding rules separately (if any).

### 4) Listening and duty-to-respond (two-way integrity)
- MUST: maintain a public intake channel for questions/claims of harm, with triage rules and response targets.
- SHOULD: publish a “rumor response” workflow for emergencies:
  - how claims are evaluated,
  - when a public response is issued,
  - and how reversals are explained.
- Serious failures (harmful guidance, systematic deception, or repeated silent edits) SHOULD open an `OFR-*` case for independent follow‑through. See `55-oversight-findings-and-response-register.md`.

### 5) Independence where communication must hold power to account
- SHOULD: where public service media exists, governance MUST protect editorial independence and stable funding, with transparent appointments and remedy for interference. See [BIB-COE-PSM-GOV-2012].

---

## B. Emergency risk communication (when speed and trust both matter)

Use evidence-based risk communication patterns:
- be fast, factual, and consistent across institutions; correct quickly and visibly;
- communicate actions people can take; reduce ambiguity and administrative burden;
- tailor language and channels to vulnerable groups (translation, disability access, low-bandwidth).
Anchors: WHO emergency risk communication guidance [BIB-WHO-RCCE], WHO *Communicating risk in public health emergencies* [BIB-WHO-CRPHE-2017], and CDC CERC manual [BIB-CDC-CERC-2024].

---

## C. Platform ecosystems (state comms in hostile attention markets)

When the state uses private platforms:
- MUST: treat official announcements as pointers to canonical `REL-*` artifacts (avoid “platform-only” rules).
- SHOULD: publish a minimal transparency report for paid amplification and influencer partnerships (what was paid for, by whom, and with what targeting constraints), with privacy constraints from `33-...`.
- SHOULD: align platform governance demands with human-rights compatible transparency and due process rather than opaque “trust us” moderation. Anchors: UNESCO platform governance guidance [BIB-UNESCO-PLATFORM-GUIDELINES], UN policy brief on information integrity [BIB-UN-SG-INFOINTEGRITY-2023].

---

## D. Minimal artifact checklist (drop-in)

For a major advisory or claim:
- `REL-*` (canonical text + method note + change log + links)
- `RULE-*` (if binding)
- `DRR-*` (if rights/resources change)
- `AL-*` (remedy lane pointer)
- `OFR-*` (if there is material controversy, harm, or repeated noncompliance)
