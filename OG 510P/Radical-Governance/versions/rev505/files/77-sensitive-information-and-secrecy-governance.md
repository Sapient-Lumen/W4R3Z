# Sensitive Information & Secrecy Governance (Make Exceptions Auditable)

**Cross-stack note:** use `293-secrecy-intelligence-and-war-powers-routing-guide.md` for the canonical route across the secrecy / intelligence / war-powers cluster. This memo is the general secrecy and withholding front door; `168` is the intelligence and security-service specialization; `222` is the external use-of-force and security-assistance specialization; `200` is the requester-side access-to-documents neighbor; `23` / `286` are the adjacent emergency-powers neighbors.

**Purpose:** bound secrecy so safety and privacy are protected without destroying the possibility of contestation.

**Person served:** People harmed when information is withheld or secrecy is abused who need lawful withholding receipts, review, and protection against concealment-as-power.

**From-below:** This makes secrecy exceptions contestable so “classified” isn’t a magic word that blocks accountability.

**EXP pointer:** counters `EXP-01` (Opacity) and `EXP-05` (Fear) by requiring receipted withholding with binding review lanes and protective procedures (see `98-persons-path-and-accessibility-invariants.md`).

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)

**Assistance & representation:** publish staffed/oral/offline paths (incl. interpretation) and who can act on behalf of someone (advocate/authorized representative); allow third‑party/collective filing where harms are collective or the person can’t safely file; disclose conflict/consent rules (see `98`, `36`, `47`, `41`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).
**Authority:** withholding/classification decisions must disclose whether review can bind (and where), and independent oversight must access the unredacted record under protective procedure (`36`, `66`, `55`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** provide safe contestation channels for requesters and insiders; avoid exposing complainants through metadata; monitor reprisal/chilling (`83`, `98`, `03`); include at least one degraded/offline safe channel (no personal device required) and publish `03` IPM‑4. (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed, a timely challenge is pending, or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**Proof burdens:** the state bears the burden to justify secrecy (scope, duration, and harm model) and to publish a contestable index; adverse secrecy outcomes cite `RC-*` + `AL-*` with least-burdensome proof for requesters (`44`, `31`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-06).)
**Join constraints:** cross‑scope joins/IDs/data sharing MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and provide a narrow fallback when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-14).)


Secrecy is a **governance exception**: it may be necessary, but it is also a high-leverage abuse surface ([TM-27]). This memo specifies a **minimal secrecy discipline** that preserves safety while keeping power **legible, reviewable, and reversible**.

**Design rule:** *if you can’t publish the payload, publish the receipt.*

**Legibility vs safety (first‑order tension):** secrecy can protect the governed (by not publishing targeting information), and it can also shield abuse. Treat both *over‑secrecy* and *over‑disclosure* as harms. In hostile environments or regime‑change scenarios, publish minimal existence metadata, minimize joinability of sensitive person/location data, and route break‑glass changes through time‑bound, reviewable `DRR-*` decisions with independent oversight (`99-protective-legibility-and-adoption-dynamics.md`, `33-...`).

Anchors: access-to-documents norms and proportionality ([BIB-COE-TROMSO], [BIB-JOHANNESBURG-1995]); national-security exceptions as narrow, reviewable, time-bound ([BIB-TSHWANE-2013]).

## Kernel anchors (do not repeat)
- Person-facing remedy invariants (even when payloads are withheld): `98-persons-path-and-accessibility-invariants.md`, `08-...`, `36-...`.
- Publication integrity and records continuity (receipts + “as-of” access): `53-...`, `31-...`.
- Purpose limitation and personal data governance: `33-...`.
- Protective legibility + adoption dynamics (transparency is a tool, not a value): `99-protective-legibility-and-adoption-dynamics.md`.
- Oversight follow-through and closure proofs: `32-...`, `55-...`.

## Named tensions (design must surface these)
- Legibility/transparency vs safety (registry weaponization and targeting risk).
- Oversight access vs leak risk (protective procedures must not become de facto non-access).
- Redaction for privacy vs usability for contestation (publish enough metadata to route remedy).
- Emergency speed vs time-bounded review (avoid permanent secrecy-by-default).

---

## 1) Non‑negotiables (what “good secrecy” must still do)

- **No secret law:** binding rules that affect the public MUST have a public form. Sensitive operational details can be withheld, but the **existence, scope, and constraints** of the authority cannot be secret. (If the rule cannot be public, it is not a lawful basis for public coercion in this design.)
- **Narrow + proportionate:** secrecy must be the **minimum** needed to prevent specific harms; default to redaction over withholding ([BIB-JOHANNESBURG-1995], [BIB-TSHWANE-2013]).
- **Time‑bound:** every secrecy decision has a **review date** (and a renewal standard), not “indefinite.”
- **Independent review exists:** there is a real lane to contest withholding (court/tribunal/ombuds or equivalent), with access to the unredacted record under protective procedures.
- **Oversight sees the unredacted:** external oversight must be able to inspect the full record; the public at least gets a receipt and an audit trail.

---

## 2) Minimal Viable Secrecy Governance Stack (MVSGS)

### A) Withholding / classification decision receipts (`DRR-*`)
Any denial, redaction, or classification decision MUST emit a `DRR-TYPE: WITHHOLD` (or equivalent `DRR-*`) that includes:

- **Object reference:** what is being withheld (document/dataset/event), with a stable ID or pointer (may be abstracted).
- **Authority:** cited `RULE-*` “as‑of” + responsible Unit ID (`34-...`, `39-...`).
- **Reason code(s):** at least one portable code (`RC-SECU`, `RC-PRIV`, `RC-COMM`, `RC-INV`) plus the local exemption code if relevant (`52-...`, `70-...`).
- **Public summary:** what can be said safely (1–3 sentences), including what decision was made and what it affects.
- **Scope + duration:** who/what is covered; **review/declassification date**; renewal standard if extended.
- **Remedy lanes:** `AL-*` for appeal/review, including deadlines and “how to file” (`36-...`).
- **Oversight access path:** which oversight body can see unredacted (and under what protective procedure).

### B) Public withholding log (existence metadata)
Maintain a public log (as a `REL-*` release or registry view) that lists, at minimum:
- `DRR-*` ID, date, Unit ID, reason category (`RC-*`), and next review date.
- A **countable footprint** (so overuse and backlog are measurable), even if payloads are not visible.

**If even confirming existence is harmful:** publish a **redacted entry** and record the exception (reason-coded), but still ensure an independent body has the full entry (see `53-...`).

### C) Declassification / review calendar (make time-bounds real)
- Publish a rolling schedule: upcoming review loads, renewal/expiry outcomes, and backlog size.
- Treat missed review dates as governance incidents (auditable and appealable).

### D) Protective procedures (oversight can see the truth safely)
- Define a small set of protective access modes (secure room, controlled disclosure, attorney/advocate access, vetted expert access).
- Bind every protective mode to: logging, prohibited secondary use, and penalties for misuse.
- Ensure protective access does not become **de facto non-access** (unavailable facilities, impossible clearance standards, or endless delay).

### E) “Disclosure is possible” discipline
When payloads cannot be public:
- publish a **sanitized summary** plus enough metadata to route contestation,
- publish **methods and version notes** for any released aggregates (`REL-*` discipline),
- and ensure later declassification can be matched to earlier receipts (no orphaned secrets).

### F) Regime-change / forced-retreat protocol (when publication becomes targeting)

Sometimes the **safest** posture is to *reduce public joinability* of sensitive person/location data (e.g., sudden targeting, coup/regime change, organized violence). This must not become silent erasure.

- **No silent unpublish:** any withdrawal, downgrade, or redaction of a previously public artifact MUST be authorized by a time‑bound `DRR-TYPE: WITHHOLD` receipt that cites basis, reason (`RC-*`), scope, and a review/restore date.
- **Preserve the record:** keep the prior public version in a tamper‑evident archive under protected access; publish minimal **existence metadata** (or a redacted placeholder when even existence is harmful) so later accountability can verify what changed and when (`53-...`).
- **Publish the safe substitute:** where full disclosure is unsafe, publish the least‑harmful replacement (aggregates, delayed release, coarse geography, or blinded identifiers) and document the degradation explicitly so analysts don’t mistake “missing data” for “no events.”
- **Independent signoff:** forced-retreat decisions SHOULD require independent review (two‑reader / adversarial review norm) and MUST remain appealable via `AL-*` with protective procedures.

---

## 3) Failure modes (and small mitigations)

- **Over-classification as policy cover:** spike in `RC-SECU` use → require independent sampling audit + publish declassification/backlog metrics.
- **Classification laundering:** moving decisions into “sensitive channels” to avoid FOI → require withholding receipts + log coverage across systems (no shadow repositories).
- **Secret exceptions become permanent:** indefinite secrecy → enforce review dates; add automatic expiry unless renewed with reasons + oversight signoff.
- **“Hash confirms existence” paradox:** publishing raw hashes can confirm a sensitive record exists → use the exception path in `53-...` (redacted manifests / guarded commitments).
- **Remedy starvation:** appeal lanes exist but can’t access evidence → require protective procedures and time limits; escalate to systemic `OFR-*` if patterns appear (`76-...`).

---

## 4) Minimal metrics (signals)

- share of withheld items with a **future review date** (target: ~100% unless explicitly justified)
- backlog of overdue reviews (count; median days overdue)
- appeal rate and success rate for withholding decisions (by reason category)
- declassification/release rate over time (and renewal rate)
- “shadow repository” incidents (withholding decisions missing from the log)

See also: [LRR-13] in `03-metrics-and-evidence.md`.

---

## 5) Interfaces to other memos (keep the system joinable)

- Records + FOI: `31-records-foi-and-government-memory.md`
- Reason codes: `52-reason-codes-registry.md` (portable withholding reasons)
- Publication integrity: `53-publication-integrity-and-tamper-evident-logs.md`
- Emergency measures: `23-emergency-governance-and-exceptions.md` (avoid “classified-by-default” emergencies)
- Threat bundle: `72-threat-response-bundles.md` (B10)
