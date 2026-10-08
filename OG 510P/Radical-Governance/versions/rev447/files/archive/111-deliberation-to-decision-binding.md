# Deliberation-to-Decision Binding (Making Participation Bite)

**Stack relation:** use `284-deliberation-stack-binding-and-legitimacy-guide.md` for the canonical route across the deliberation cluster. This memo is the binding and anti-theater kernel; `143` is the systems front door; `159` covers infrastructure; `224` covers process rails; `180` covers comparative legitimacy design.

**Material floor (one sentence):** If a deliberation process can shape outcomes, then its inputs, standing, and outputs MUST bind decision-makers via a time-bounded duty-to-respond with reasons (or the process becomes legitimizing theater).

See also: `143-deliberative-systems-and-citizens-assemblies.md`.
**Person served:** People who participate (or are affected) need participation to be **actionable**, not symbolic.

**From-below:** Participation without binding response is often used to launder pre-decided outcomes; binding is an anti-humiliation safeguard.

---

## The binding contract (minimum)

A deliberation process that claims influence MUST publish, up front:

1) **Scope of influence (SOC):** what can change, what cannot, and why.
2) **Decision owner(s):** the accountable authority who must respond (names/roles).
3) **Response deadline:** a date; with a **deadline-miss trigger** (see `108-service-standards-and-time-budgets.md`).
4) **Response taxonomy:** the allowed response types (below) and required fields.
5) **Evidence pack rules:** what counts as evidence, how to contest it, and how late evidence is handled.
6) **Standing rules:** who can submit, who can speak, how representation/assistance works (see `98-persons-path-and-accessibility-invariants.md`).
7) **Safety & non-retaliation:** a degraded/offline channel for protected submissions (see NR-08 in `101-claude-rev142-normative-requirements.md`).

If any item is missing, the process MUST be labeled **consultation-only** and MUST NOT be used as a legitimacy claim for downstream coercive action.

---

## Response taxonomy (so “we listened” is falsifiable)

Decision-makers MUST respond using one of:

- **ADOPT:** accept recommendation(s) as-is.
- **ADOPT-WITH-MODS:** accept with changes. MUST include: what changed, why, and what evidence drove the changes.
- **REJECT:** decline. MUST include: the decisive constraints (legal, fiscal, feasibility), the counter-evidence, and what would need to become true to revisit.
- **DEFER:** postpone with an explicit condition + a next decision date.
- **PARTITION:** adopt parts. MUST map each recommendation to a response type.

Each response MUST be published as a **Decision Receipt** with a stable identifier, and MUST cross-link the deliberation record (`ENG-*` in `41-public-participation-and-deliberation-register.md`) to the decision artifact surface (`DRR-*` / reason codes in `115-information-integrity-and-record-interfaces.md` and `52-reason-codes-registry.md`).

---

## Evidence pack integrity (anti-manipulation)

Deliberation fails when information is curated to force an outcome. Minimum safeguards:

- **Evidence docket:** a public index of submissions, expert testimony, and datasets with “as-of” timestamps (NR-07/15).
- **Adversarial review slot:** a funded, time-bounded opportunity to challenge the evidence pack (red-team the premises).
- **Claim–counterclaim pairing:** contested claims must be paired with the strongest counter-claim that meets evidence rules.
- **Late evidence rule:** late-breaking facts can reopen deliberation or trigger an interim protection / pause (see `105-institutional-circuit-breakers.md`).

---

## Representation, inclusion, and safety (so the process is not selective)

- **Compensation and care:** pay participants; provide childcare, transport, translation, accessibility.
- **Assistance & representation:** allow collective submissions and representatives (NR-12/17).
- **Safety:** publish how retaliation risk is mitigated; provide a protected channel that does not require personal devices (NR-08).

---

## Minority reports and “dissensus” handling

Where consensus is not reached:
- Publish **minority reports** with equal visibility.
- Require the response receipt to address minority concerns explicitly (not just the majority recommendation).

This prevents “forced consensus” and improves legitimacy under plural values.

---

## Failure modes and fixes (one-screen)

- **Theater risk:** no binding response → label consultation-only.
- **Capture risk:** organizer curates evidence → adversarial review + paired claims.
- **Agenda sabotage:** only trivial items allowed → SOC must name exclusions + why.
- **Delay laundering:** indefinite “consideration” → deadline + miss-trigger.
- **Participation tax:** high burden to join → assistance + offline modes.

Use the unit checks in `107-governance-test-suite.md` (contestability, anti-capture, stress performance) to audit.

---

## References (minimal, reusable)
- OECD work on deliberative democracy and institutional design: see extended bibliography keys in `91-bibliography-extended.md` (e.g., [BIB-OECD-DEL] plus case-oriented companions).
- For deliberative polling / structured deliberation methods: add one reusable key for a canonical Fishkin reference if this memo becomes heavily reused.
