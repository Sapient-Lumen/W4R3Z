# Elections and Electoral Administration (Minimum Viable Election Integrity)

**Purpose:** make election administration credible by specifying auditable interfaces that resist fraud narratives and capture.

Elections are a **high-stakes legitimacy generator** (`DEC-1/5`) and a **critical infrastructure operation**. If election administration is not *auditable, contestable, and resilient*, legitimacy collapses even when formal rights exist.

This memo defines a **Minimum Viable Election Integrity System (MVEIS)** that fits the archive’s interface-first approach: treat election operations as a pipeline that emits **joinable public artifacts** (`DRR-*`, `REL-*`, `AL-*`, `RULE-*`, `CON-*`, `STD-*`).

Anchors (administration + standards): see [BIB-VENICE-ELECT], [BIB-IDEA-EMD], [BIB-OSCE-EOH], and (for verification) [BIB-NASEM-SECURINGTHEVOTE-2018].


## Kernel anchors (do not repeat)
- Person-facing invariants: `98-persons-path-and-accessibility-invariants.md` (incl. non‑digital/non‑reading options), service journeys `47-...`, remedy lanes `36-...` / `08-...`.
- Protective legibility + adoption dynamics: `99-protective-legibility-and-adoption-dynamics.md` (transparency ≠ accountability; identify who loses discretion / who gains contestation capacity).
- Publication integrity (no silent edits; “as‑of” access): `53-...` and `31-...` where relevant.
- Coercive edge cases (policing/intimidation, roll purges): treat as contestable determinations with receipts (`05-...`, `43-...`).
- High‑stakes safety/quality claims (machines, audits, cyber posture): use assurance‑case discipline where warranted (`73-...`, `59-...`).

## Named tensions (design must surface these)
- Fast results vs verifiable results (speed vs auditability).
- Transparency/auditability vs voter privacy and coercion risk.
- Access/participation vs manipulation/capture narratives (design procedures that are *checkable*, not merely asserted).
- Emergency flexibility vs incumbent entrenchment (exception powers become the attack surface).
- Cyber disclosure vs attacker advantage (publish what’s necessary for trust without gifting exploit detail).

---

## 1) Failure modes (design against)
- **Partisan administration capture:** rules and discretionary choices (polling sites, ballot design, tabulation procedures) become partisan tools.
- **Opaque tabulation:** results cannot be independently checked; trust depends on authority.
- **No audit trail / no software independence:** systems can fail or be attacked without detection.
- **Voter roll manipulation or error:** disenfranchisement by data changes without remedy.
- **Emergency manipulation:** last-minute changes to timing or procedures entrench incumbents.
- **Litigation as sabotage:** dispute lanes are slow/opaque; no clear deadlines; denial by delay.

---

## 2) Minimum Viable Election Integrity System (MVEIS)

### A) Authority + rule legibility
**MUST**
- Put election rules in a **Public Rules Register** (`RULE-*`), versioned and discoverable (`25`, `39`).
- Treat **election operations decisions** (polling-place changes, eligibility determinations, recount/audit triggers, emergency procedure changes) as **`DRR-*`** receipts with reasons (`RC-*`) and contestation lanes (`AL-*`) (`31`, `36`, `52`).
- Receipts/notices MUST meet the **comprehension test** and be usable without prior system knowledge (language + disability access; clear next step + deadline; no-wrong-door routing). See `98-persons-path-and-accessibility-invariants.md` and `31-records-foi-and-government-memory.md`.
- Identify the election management body as a `Unit ID` in the competence ledger, including its legal basis and scope (`34`).

**SHOULD**
- Publish a short “**election operations doctrine**” (what is discretionary vs. rule-bound) and require departures to emit a `DRR`.

### B) Voter registry governance (accuracy + remedy)
**MUST**
- Maintain a voter registry with **change logging** and a correction path that is fast, accessible, and appealable (use `AL-*`).
- Publish processing-time **tail** metrics for corrections (not just averages) and provide assistance/representation where the registrant cannot self-advocate. (`03-...`, `98-persons-path-and-accessibility-invariants.md`)
- Publish non-sensitive **coverage/quality metrics** (e.g., update rates, error rates, address-change processing times) as `REL-*` releases with methods and revision logs (`51`, `26`, `03`).

**SHOULD**
- Establish a standing red-team / data-quality review cadence; log findings and fixes via the OFRR (`55`).

### C) Balloting + tabulation (auditability first)
**MUST**
- Ensure outcomes are **independently checkable** using an auditable trail (paper ballots or voter-verifiable paper records) and procedures consistent with **software independence** concepts (verification does not rely solely on software).
- Prohibit “silent” changes to tabulation configuration: publish versioned configuration/control artifacts (where lawful) and log changes.
- Treat voting system requirements as governance-grade standards (`STD-*`) and tie procurement/contracts to those standards (`27`, `38`).

**SHOULD**
- Prefer systems and procedures compatible with **risk-limiting audits** (RLAs) ([BIB-NIST-RLA-GENTLE], [BIB-AMSTAT-ELECTIONAUDIT-2018]).

### D) Results publication (official facts with methods)
**MUST**
- Publish results as a `REL-*` release with:
  - clear **status** (`PRELIM` vs `CERTIFIED`),
  - a **methods note** (tabulation pipeline + aggregation rules),
  - a revision log (no silent corrections),
  - and contestation lane(s) (`AL-*`).
- Publish a precinct/ward-level dataset where lawful (or a justified redaction policy) so observers can check aggregation.

**SHOULD**
- Publish a small “**changes ledger**” for corrected reporting errors (what changed, why, and what does *not* change).

### E) Post-election verification (audit + recount discipline)
**MUST**
- Require **post-election verification** for contestable contests (at minimum, a mandatory audit regime; prefer RLAs where feasible).
- Publish the audit plan + results as `REL-*` releases; if anomalies exceed thresholds, open an `OFR-*` case and publish the response/closure path (`55`).

**SHOULD**
- Pre-commit to audit escalation rules (expand sample → full recount) and publish them as a `RULE-*` (avoid ad hoc disputes).

### F) Disputes + remedy (time-bounded contestation)
**MUST**
- Maintain a discoverable election dispute lane (`AL-*`) with deadlines and a no-response rule; publish dispute outcomes as `DRR-KIND: REVIEW` with `AO-*`.
- Publish a **guided intake** option (in-person/phone/offline) so voters do not need to know the lane taxonomy to contest a denial. (No-wrong-door; navigation duty.) (`98-persons-path-and-accessibility-invariants.md`, `08-...`)
- Keep courts/tribunals available during emergencies; emergency procedure changes do **not** suspend review (`23`, `36`).

### G) Integrity (money + influence)
**MUST**
- Disclose political finance and relevant influence channels (pair `ACC-5` with `46-influence-and-interests-register.md`).
- Prevent procurement capture in election equipment/services: open contracting + vendor performance histories (`22`, `38`).

### H) Emergency constraints (anti-entrenchment)
**MUST**
- Election date/procedure changes in emergencies require heightened approval and tight bounds (`23-emergency-governance-and-exceptions.md`).
- Publish an **election-integrity notice** (what changed, why, who approved, how audit/remedy will work) as a `DRR` and/or `REL` release.

---

## 3) Interface summary (what to emit)
- **`RULE-*`**: election rules + audit/recount doctrine.
- **`DRR-*`**: operational decisions (polling changes, eligibility rulings, audit/recount triggers, emergency procedure changes).
- **`REL-*`**: official results + audit results + voter-roll quality metrics (methods + revision logs).
- **`AL-*`**: dispute lanes (administrative + tribunal + court) with deadlines.
- **`STD-*`**: voting system / e-voting standards incorporated by law or procurement (e.g., VVSG; CoE e‑voting guidance) ([BIB-EAC-VVSG], [BIB-COE-EVOTING-2017]).
- **`CON-*`/`OCID`**: election equipment/services contracts (open contracting).
- **`OFR-*`**: credible anomaly/integrity cases with follow-through and closure verification.
