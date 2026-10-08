# Portability & Cross‑Jurisdiction Continuity (Don’t Make People Restart)

**Cross-stack note:** use `296-status-identity-portability-and-mobility-routing-guide.md` for the canonical route across the status / identity / portability / mobility cluster. This memo is the portability / continuity specialization; `12` is the person-recognition front door; `125` is the civil-status / membership specialization; `67` is the migration / border-status specialization; `203` is the mutual-recognition specialization; `158` is the family-unity neighbor; `287` is the digital-implementation family neighbor.

**Purpose:** make *movement across boundaries* (jurisdictions, agencies, programs, providers) **non-destructive**: benefits, credentials, cases, and obligations should carry forward without forcing people to re‑prove their lives.

**Person served:** a person who moved, fled, aged into a new program, changed household status, crossed a municipal/regional/state line, or was transferred between offices—and whose survival shouldn’t depend on mastering bureaucratic seams.

**From-below:** boundaries are where people get dropped. This memo defines a **small, enforceable portability kit** so the system absorbs transfers instead of making the person do the joins.

**EXP pointer:** counters `EXP-02` (Waiting), `EXP-04` (Error), `EXP-06` (Complexity) — see `98-persons-path-and-accessibility-invariants.md`.

---

## A. Portability primitives (minimum viable kit)

### 1) **Continuity Receipt** (CR‑*)
When *any* authority-bearing unit changes (new office, new jurisdiction, new provider, new program lane), the person MUST receive a **Continuity Receipt** that:
- names **what is supposed to continue** (eligibility, coverage, license, case status, deadlines, payments, sanctions, accommodations),
- states a **provisional continuity rule** (see below) and the **date until which continuity is guaranteed** unless an adverse action is lawfully taken,
- provides a **single reference number** that works across units (`70-interoperability.md`), and
- names the **transfer owner** (role + contact path) and the **appeal lane** if continuity is denied (`08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md`).

**Rule:** CR-* is issued **before** the boundary takes effect (move date, reassignment, handoff, release, discharge), or at the moment of first contact in an emergency transfer.

### 2) **Provisional continuity default** (the “no-cliff” rule)
If a person plausibly qualifies and the system cannot confirm status *because of the boundary*, default to **provisional continuity**:
- keep the person in-pay / in-service,
- freeze penalties and enforcement,
- and allow “good-faith compliance” while verification proceeds.

This is the portability form of **mercy / interim protection** (NR-16) and the degraded‑mode rule (NR‑13/17). See `106-legitimacy-protocols.md` (contest windows + receipts), `108-service-standards-and-time-budgets.md` (deadline triggers).

### 3) **Non‑reset evidence rule** (“don’t re-prove the basics”)
Across a transfer, units MUST accept prior evidence *by default* unless they can articulate a **specific, receipt-backed reason** to re‑verify (fraud risk signal, material change, legal incompatibility). Require:
- a **Decision Receipt** if re‑verification is demanded (`31-records-foi-and-government-memory.md` + Decision Receipt minimum fields),
- a narrow list of “re‑verification triggers,” and
- an option to submit **equivalent evidence** (not format fetishism).

### 4) **Mutual recognition with minimum standards**
Where programs/licenses/credentials overlap, adopt **mutual recognition** with a small minimum standard:
- recognize the *status* even if implementation differs,
- use supplements only where genuinely necessary (health/safety, rights constraints),
- and publish the “delta” in plain language.

(Anchor in `02-design-toolkit.md` **IOP‑2**; join discipline in `19-compacts-and-cooperative-governance.md`.)

### 5) **Transfer-of-file protocol** (TOF‑*)
Transfers MUST move the file without making the person courier:
- file transfer occurs **unit-to-unit** with audit logs (`53-publication-integrity-and-tamper-evident-logs.md`),
- the person can see *what moved* and *what didn’t* (withholding receipts if needed: `77-sensitive-information-and-secrecy-governance.md`),
- and the person has a **correction hook** if the file is wrong (`37-claims-evidence-and-update-discipline.md`, NR‑07/15).

### 6) **Jurisdiction for appeal during transfer**
Define where a person appeals **while in transit**:
- default: the unit taking adverse action owns the appeal lane,
- the origin unit remains responsible for continuity until handoff completes,
- conflict is resolved via a named escalation lane + time budget (`108`).

Publish this in `AL-*` / lane registries and on the CR-* receipt.

---

## B. Circuit breakers (portable anti-failure triggers)

If any of the following occurs, trigger **automatic protection** (see `105-institutional-circuit-breakers.md`):
- **missed transfer deadline** → automatic provisional continuity extension + mandatory escalation,
- **lost file / missing join-key** → manual bridge via receipt/reference number; service may not be denied solely due to missing joins (`70` degraded interop rule),
- **duplicate evidence request** → require a Decision Receipt explaining why re‑verification is necessary,
- **handoff dispute** (“not my problem”) → automatic assignment of a temporary case owner with authority to act,
- **housing/health/safety risk** → immediate interim protection pending review (NR‑16).

---

## C. Minimal metrics (to make continuity real)

Track as a small dashboard (avoid metric sprawl; see `03-metrics-and-evidence.md`):
- **CT‑1 Transfer time:** median + P90 time from CR-* issuance to confirmed continuity.
- **CT‑2 Cliff rate:** % of transfers with any payment/service interruption.
- **CT‑3 Duplicate burden:** mean number of “basic facts” re‑requested after transfer.
- **CT‑4 Provisional usage:** % of transfers granted provisional continuity; % later reversed (with reasons).
- **CT‑5 Dispute rate:** % of transfers with “handoff dispute” escalation; time-to-owner assignment.

---

## D. Where this plugs into the stack

- **Interop & join-keys:** `70-interoperability.md`
- **Scope obligations:** `71-interface-obligations-by-scope.md`
- **Compacts & mutual recognition:** `19-compacts-and-cooperative-governance.md`
- **Legitimacy receipts + contest windows:** `106-legitimacy-protocols.md`
- **Accountability loops + circuit breakers:** `104` / `105`
- **Time budgets (enforceable deadlines):** `108`
- **Identity/status systems:** `44-identity-credential-and-eligibility-systems-register.md`, `12-identity-and-recognition.md`

---

## References (citation keys)
- Mutual recognition in the EU’s internal market practice (overview): see [BIB-EU-MUTUAL-RECOGNITION].
- EU single digital gateway / cross-border procedures framing: see [BIB-EU-SDG].
- Identity and cross-border trust services (eIDAS): see [BIB-EU-EIDAS].

## See also

- `160-digital-identity-credentials-privacy-utility.md` (portable claims + relying party governance)

