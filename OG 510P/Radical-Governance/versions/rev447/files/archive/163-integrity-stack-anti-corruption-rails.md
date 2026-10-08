# Integrity Stack (Anti‑Corruption Rails)

**Goal:** treat integrity as *infrastructure* (rails + auditing + enforcement), not “ethics training”.
This memo describes a compact “integrity stack” that can be implemented from micro‑local to global scopes.

**Core idea:** corruption is often a *systems* failure (opaque flows, unpriced influence, weak detection, weak sanctions). Build an **end‑to‑end trace** of who decided what, under what interests, using what money, with what counterparties—plus a credible enforcement path.

---

## 1) The integrity stack (minimum viable)

### A. Interest + influence transparency (inputs)
- **Conflict‑of‑interest policy** with required disclosure, recusals, and supervisory review (not self‑policing). See [BIB-OECD-COI-REC-2003].
- **Lobbying/contact transparency**: who met whom, on what, when; a public log for senior officials; clear definitions that include paid + non‑paid influence. See [BIB-GRECO-LOBBY-PRINCIPLES] and [BIB-GRECO-EXEC-2024].
- **Revolving‑door rules** (cooling‑off, role restrictions, waivers logged publicly) for high‑risk positions and procurement roles.

### B. Money + contracting traceability (flows)
- **Open contracting** end‑to‑end (planning → tender → award → contract → implementation), published in a machine‑readable standard, with linkable identifiers. See [BIB-OCDS] and [BIB-OCP-REDFLAGS-2024].
- **Beneficial ownership transparency** for counterparties, with a path to public or “legitimate interest” access depending on privacy/safety constraints. See [BIB-OGP-BO-2024].

### C. Detection (signals)
- **Red‑flag analytics** on procurement and grants (single‑bid awards, split contracts, repeated winners, abnormal change orders, related‑party indicators, etc.) with independent review triggers. See [BIB-OCP-REDFLAGS-2024].
- **Integrity anomaly hotline** + case tracking: complaints become docketed, auditable objects (not “HR vibes”).

### D. Protection + incentives (inputs from below)
- **Whistleblower protection** and anti‑retaliation remedies (fast interim relief, burden shifting, penalties).
- **Citizen/worker monitoring** routes that can feed the docket without requiring heroics (structured submission + status visibility).

### E. Enforcement (teeth)
- **Independent integrity unit** (or inspector general) with: subpoena powers where appropriate; audit authority; referral authority; and required public reporting.
- **Sanctions ladder**: administrative penalties, debarment, civil recovery, and (where necessary) criminal prosecution—mapped to the violation taxonomy.

---

## 2) Interfaces and invariants (make it hard to “silently swap” reality)

**Key invariants** (should be testable in `107-governance-test-suite.md` style):
1. **Decision trace exists**: for any significant decision, a public record of *authority, process, and rationale* exists.
2. **Interest trace exists**: relevant interests (financial + relational) are disclosed and linked to decisions, with recusals logged.
3. **Counterparty trace exists**: vendor/grantee identity links to beneficial ownership and past performance.
4. **Spend trace exists**: planned → committed → disbursed → delivered is measurable, with change‑orders explained.
5. **Remedy path exists**: complaints and investigations are tracked with deadlines and escalation.

---

## 3) Scope‑fit (micro‑local → global)

- **Micro‑local (teams, councils, co‑ops):** focus on contact logs, conflict‑of‑interest, procurement transparency, and “small‑n capture” defenses (rotation, independent review).
- **Municipal/regional:** add open contracting + vendor IDs + debarment lists; publish meeting/contact logs for senior roles.
- **National:** add beneficial ownership regime, stronger lobbying disclosure, central debarment + audit, and cross‑agency data joins.
- **Transnational/global:** converge on shared identifiers + interoperable open contracting; mutual legal assistance for enforcement; shared debarment signals.

---

## 4) Failure modes (and counter‑moves)

- **Paper compliance:** disclosures exist but are unusable → require *machine‑readable* formats + public summaries + random audits.
- **“Ethics theater”:** training replaces enforcement → enforce sanctions ladder and publish integrity metrics (not vanity counts).
- **Capture of integrity unit:** rotate leadership, multi‑party appointment, transparent case dockets, and external audit.
- **Privacy weaponization:** use tiered access (public / legitimate interest / protected) while keeping the enforcement trace intact.

---

## 5) Hooks into existing archive

- Procurement rails: see `110-budget-procurement-integrity.md` and `162-procurement-as-governance-lever-and-guardrails.md`.
- Appointments/tenure integrity: see `113-appointments-and-tenure-integrity.md`.
- Illicit finance joins: see `155-illicit-finance-and-kleptocracy-defense.md`.
- Information/records: see `115-information-integrity-and-record-interfaces.md`.

