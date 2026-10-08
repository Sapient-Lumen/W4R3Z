# Emergency Measures Register (EMR) (Emergency Powers as an Interface)

**Purpose:** keep emergency powers bounded, contestable, and sunsettable—so exceptions don’t become permanent governance by bypass.
**Person served:** a person living under emergency restrictions who needs exceptional powers bounded, time‑limited, and contestable.

**From-below:** This keeps emergency powers accountable by listing measures, legal basis, end dates, and review paths you can invoke.

**EXP pointer:** counters `EXP-02` (Waiting), `EXP-05` (Fear), and `EXP-01` (Opacity) by requiring receipted exceptional powers with reachable review even under degraded conditions (see `98-persons-path-and-accessibility-invariants.md`).
**Join constraints:** identifiers/joins using this artifact MUST follow `70-interoperability.md` (empowered use‑path + corrective action), stay purpose‑limited/minimized, and have a narrow alternative when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `101-claude-rev142-normative-requirements.md` (NR-14).)
**As-of & corrections:** This artifact is versioned and queryable “as-of”; corrections emit a citable update (`REL-*`) and must propagate to dependent records/systems (see `31`, `53`, `70`, `73`). (`101` NR-07, NR-15)
**Material floor (one sentence):** during crises, measures and changes MUST be publishable and retrievable in lowest‑infrastructure modes (radio/posters/print) with receipted updates and sunset dates. (See `101-claude-rev142-normative-requirements.md` (NR-13, NR-05).)

Emergency powers are *where governance most often breaks*: decisions happen fast, normal constraints get bypassed, and “temporary” exceptions quietly become permanent. The goal here is not “more transparency,” but a **joinable audit spine** that makes exceptional powers:

- **legible** (who declared what, for where, under what law),
- **bounded** (time limits, renewal discipline, scope),
- **contestable** (clear appeal lanes),
- **reviewable** (after-action review and closure), and
- **interoperable** (exceptions in procurement/data/coercion/fiscal systems must reference the same emergency episode).

This memo defines a minimal **Emergency Measures Register (EMR)** keyed by stable `EMR` IDs.

**Anchors:** [BIB-ICCPR] (derogations discipline); [BIB-HRC-GC29] (procedural/material safeguards); [BIB-SIRACUSA] (interpretive constraints); [BIB-VENICE-SOE-COMPILATION-2020] (benchmarks); [BIB-VENICE-COVID-EMERGENCY-2020] (COVID-era guardrails); [BIB-ECHR-A15-GUIDE-2025] (derogation notice + strict necessity); [BIB-COE-A15-NOTIF-PROC] (notification procedure); [BIB-WHO-IHR-TEXT-2025] (cross-border health obligations); [BIB-FEMA-CGC-2024] (continuity planning); [BIB-ISO-22301-2019] (business continuity management system baseline).

---

## Kernel anchors (do not repeat)
- **From-below usability:** these artifacts MUST remain comprehensible and actionable via the person’s path (assisted/offline options; no insider knowledge). (`98-persons-path-and-accessibility-invariants.md`)
- **Exception discipline:** `23-emergency-governance-and-exceptions.md` (sunsets; oversight; receipts).
- **Records + publication integrity:** `31-...`, `53-...` (no “silent emergency”).
- **Remedy lanes:** `08-remedy-and-grievance.md`, ALR `36-...` (contestability during emergencies).
- **Secrecy discipline:** `77-...` (typed withholding receipts where needed).
- **Protective legibility:** `99-protective-legibility-and-adoption-dynamics.md` (emergency powers are a capture surface).

## Named tensions (design must surface these)
- **Speed vs contestation:** urgent action still needs logged reasons and review.
- **Secrecy vs trust:** confidentiality may be necessary; dark zones destroy legitimacy.
- **Uniformity vs locality:** emergency rules can misfit; publish variance and rationale.
- **Expiry vs entrenchment:** temporary powers tend to stick; enforce sunsets and renewal receipts.

## A. What an EMR entry is (episode vs. measures)
An **EMR entry** represents an **emergency episode** (a declared state of emergency, public health emergency, disaster declaration, security crisis, etc.) and the **exceptional measures** authorized under it.

- **Episode:** the declaration + renewals + termination.
- **Measures:** the concrete deviations from baseline constraints (e.g., procurement exceptions, special data access, accelerated permitting, movement restrictions).

**Rule:** measures MUST not float as informal “policy guidance.” If a power is exceptional, it MUST be logged as a measure under an `EMR` episode.

---

## B. Join rules (the point of EMR)
EMR is only useful if other systems can *point to it*.

### Required joins
If an emergency episode is active and an action relies on emergency authority, the action MUST cite `EMR-*`:

- **Decisions:** `DRR` for declaration/renewal/termination MUST cite `EMR-*` and the governing `RULE` version/as-of.
- **Procurement:** any emergency procurement exception MUST cite `EMR-*` and still appear in the CPR (`CON-*`). (See `38-...`.)
- **Data access:** emergency data processing/access MUST cite `EMR-*` and appear in the DPR (`DPR-*`). (See `33-...`.)
- **Coercion:** emergency enforcement/custody events MUST still be logged in `ENF-*`; when emergency authority is invoked, `ENF-*` SHOULD reference `EMR-*`. (See `43-...`.)
- **Transfers:** emergency grants/withholding/conditionality MUST cite `EMR-*` in `TRF-*` when justified by emergency authority. (See `35-...`.)
- **Services:** if emergency authority changes, suspends, or reroutes a public service workflow, the measure SHOULD cite impacted `SRV-*` entries; if any are `ESS-1`, the EMR measure MUST record the continuity-floor check and any backstop/fallback plan. (See `47-...`.)
- **Participation:** if emergency measures use consultation/assemblies, log as `ENG-*` and link (even if expedited). (See `41-...`.)

### Contestability
Every emergency episode MUST publish an **appeal lane crosswalk**:
- `EMR-*` MUST list the relevant `AL-*` lanes for:
 - challenging the declaration/renewal,
 - challenging measures (esp. restrictions/denials),
 - urgent protection (injunction/urgent review) for high-stakes harms.

(See `36-...`, `08-...`.)

---

## B1. Person-facing obligations in emergencies (don’t let speed erase agency)

Emergency governance touches people through **orders** (evacuations, closures, curfews, quarantines), **allocations** (shelter, aid), and **enforcement**. Legitimacy fails when affected people cannot understand what applies to them or cannot safely seek relief.

**Minimum requirements (wire to `98`):**
- **Comprehension-tested public notices:** any emergency order with legal effect SHOULD have a plain-language “rules card” view (translations + low-bandwidth formats) keyed to the `EMR-*` episode and the underlying `RULE-*` basis (`39`, `61`, `98`).
- **Orders and denials emit receipts:** where an emergency measure creates a specific obligation or denies access to relief, it MUST emit a portable `DRR-*` receipt citing `RULE-*` (as-of) and the applicable remedy lane (`AL-*`). (`31`, `08`, `36`)
- **No-wrong-door intake:** relief and complaint channels MUST accept and route filings even when jurisdiction is unclear (multiple agencies, vendors, NGOs).
- **Delay is harm:** emergency relief programs SHOULD publish time promises (ack / first contact / decision) and apply interim protections where delay can cause displacement, hunger, or preventable death (`82`, `03`).
- **Safety vs legibility:** public reporting can endanger people (e.g., shelter locations, identities). Use the two-layer model in §D and secrecy governance (`77`, `99`) rather than defaulting to either full disclosure or full opacity.## C. EMR minimum schema (keep it small)
Implementations can add fields, but SHOULD NOT remove these.

### Episode fields
| Field | Meaning |
|---|---|
| `EMR ID` | stable identifier for the emergency episode |
| Declaring unit | the authority/body (must exist in the competence ledger) |
| Declaration `DRR` | the decision receipt for the declaration |
| Hazard type | standardized category (local taxonomy allowed; prefer re-usable standard) |
| Legal basis (`RULE`) | statute/charter/compact authority (version/as-of) |
| Coverage | territory/service area reference (unit(s) / boundary) |
| Critical services impacted | list of impacted `SRV-*` (flag `ESS-1` where applicable) |
| Powers invoked | enumerated list of activated powers (link to `RULE` instruments) |
| Rights affected | brief classification + rationale; MUST state **rights mode** (limitation vs derogation) and non-derogable constraints; if derogation, list provisions derogated and link depositary notice(s) |
| Start / sunset | start time + fixed end (or renewal cadence) |
| Renewals | list of renewal `DRR` IDs + dates + deltas |
| Oversight | renewal/approval body + required audits/inspections |
| Appeal lanes | `AL-*` crosswalk for declaration and measures |
| Cross-border notifications | any required notifications (IHR/treaty/etc.), including derogation notices to depositaries where applicable |
| Status | active / terminated / under review |
| Closure artifacts | after-action review (`OFR-*`/`EVAL-*`) + completion date |

### Measure fields (inside the episode)
Each measure under an episode SHOULD be addressable as `EMR-*:M1`, `EMR-*:M2`, etc.

| Field | Meaning |
|---|---|
| Measure ID | local-in-episode identifier |
| Power invoked (`RULE`) | the activated authority + version/as-of |
| Measure type | procurement / data / fiscal / coercion / movement / health / permitting / other |
| Rights mode | limitation / derogation (if derogation: provisions derogated + depositary notice link) |
| Scope | who/where affected + any eligibility gates (`IDN-*` if relevant) |
| Start / end | time bounds (must be explicit) |
| Authorizing `DRR` | receipt for this measure (or the declaration if bundled) |
| Evidence link | cite `CLM-*` / data releases used to justify (if applicable) |
| Linked objects | `CON-*`, `DPR-*`, `ENF-*`, `TRF-*`, `PAR-*`, `PROG-*` as relevant |
| Impacted services | `SRV-*` list (and whether any are `ESS-1`) |
| Continuity-floor check | if any impacted `SRV` is `ESS-1`, record whether the measure risks dropping below the published floor and the backstop/fallback plan (or a temporary floor modification with sunset) |
| Remedy | `AL-*` lanes + urgent-protection availability |
| Update log | amendments/deltas (do not silently revise) |

---

## D. Publication & sensitive information (two-layer model)
EMR MUST be public, but operational details can be protected **without** destroying accountability.

- **Public EMR:** episode + measures + joins + deltas + oversight + closure.
- **Protected annex (optional):** sensitive details (tactical plans, victim identifiers, etc.) with:
 - a **reason code** and **expiry** (default: time-bounded),
 - a **typed FOI exemption** policy,
 - an `OFR-*` oversight hook to prevent “permanent secrecy.”

(See `31-...`, `32-...`.)

---

## E. Renewal and termination discipline (anti-normalization)
**Renewal is a decision, not autopilot.**
- MUST: renewals require an affirmative vote/approval on a fixed cadence.
- MUST: each renewal publishes a delta: what ended, what remains, what changed.
- SHOULD: renewal thresholds increase after N renewals (anti-entrenchment).
- MUST: termination publishes a closure `DRR` with the end-state and next steps.

---

## F. Metrics and tests
- **[IPM-19] Emergency exception density & closure:** days under EMR; renewal counts; share of spend tied to `EMR-*` (from budget + `CON-*`); % measures with explicit sunset; % episodes with completed after-action review within target window.

(See `03-metrics-and-evidence.md`.)

---

## G. Failure modes (see [TM-18])
- “Temporary” becomes permanent → *fixed sunsets + rising renewal thresholds + mandatory deltas.*
- Hidden emergency procurement → *all emergency awards still in CPR (`CON-*`) and linked to `EMR-*`.*
- Rights restrictions without remedy → *mandatory `AL-*` crosswalk + urgent protection lane.*
- Silent revisions → *versioning and update logs; no overwrites.*

(See `04-threat-models.md` and `23-emergency-governance-and-exceptions.md`.)
