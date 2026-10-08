# Exit, Voice, Fork, Federation (Anti‑Monopoly Legitimacy)

**Problem:** when governance is a **monopoly** (or acts like one), “voice” becomes the only option—and voice can be ignored. A system that cannot be **exited** or **forked** tends to drift toward capture, coercion, and stagnation.

**Goal:** make *exit* and *fork* **safe, bounded, and legible** across scopes—so competition and experimentation are possible **without** turning into fragmentation, secession violence, or race‑to‑the‑bottom.

This memo defines a minimal **protocol layer** that can attach to communities, institutions, and jurisdictions.

---

## Core primitives

### 1) EXIT — individual / organizational exit lanes (low drama)
An “exit lane” is a defined pathway to leave a governance provider (or regime) while preserving continuity.

**MUST**
- **Portability default:** leaving MUST NOT reset identity, eligibility, evidence, or time served unless a published rule explicitly requires it (see continuity: `109-portability-and-cross-jurisdiction-continuity.md`).
- **Continuity receipt:** any exit action emits `EXIT-*` with:
 - What is being transferred (entitlements, files, liabilities, obligations).
 - Effective date and interim coverage.
 - Dispute lane + deadlines (`114-interjurisdictional-dispute-and-coordination.md`).
- **Non‑retaliation:** governments MUST NOT impose punitive exit costs beyond published, contestable fees/taxes and legitimate liability settlement.

**SHOULD**
- **Graduated exit:** allow partial exit (service‑by‑service) when full exit is dangerous or infeasible.
- **Exit insurance:** pooled funds to prevent “only the rich can exit.”

**Metrics (minimal)**
- Median time to complete an exit transfer.
- % exits with continuity break (should approach 0).
- Differential exit cost by income decile (proxy for coercive lock‑in).

---

### 2) VOICE — standing, contest, and response (high signal, not theater)
Exit is not a substitute for voice; voice is the core of legitimacy. But voice needs **teeth**.

**MUST**
- Decisions affecting rights/benefits emit decision receipts (`DRR-*`) with reasons and lanes (see `106-legitimacy-protocols.md`, `111-deliberation-to-decision-binding.md`).
- Participation claims MUST bind to duty‑to‑respond (`DEC-0`).

**SHOULD**
- “Voice budget” for institutions: publish time and backlog integrity for contest/appeals (`108-service-standards-and-time-budgets.md`).

---

### 3) FORK — bounded community/jurisdictional split (high drama, controlled)
A fork is a reversible (or at least rule‑governed) split of a governance unit into two (or more) successor units.

**MUST**
- **Fork charter:** a fork proposal MUST publish `FORK-*`:
 - Proposed boundaries + population and asset/liability inventory.
 - Delegated powers requested/retained.
 - Fiscal settlement proposal and cross‑subsidy continuity plan.
 - Transitional service coverage plan (no cliff).
 - Dispute lane + deadlines (`114`).
- **Rights floor:** a fork MUST preserve a published **minimum rights/standards floor** for persons, regardless of successor unit.
- **Cooling + contest:** cooling period, public evidence pack, and a contest window (see legitimacy protocol: `106`).
- **Anti‑coercion safeguards:** special protections for minorities at risk of expulsion/violence; credible monitoring plan (see coercion governance: `116`).

**SHOULD**
- **Fork escrow:** escrow transitional funds so service continuity is not hostage to politics.

**Metrics (minimal)**
- Continuity break rate during forks.
- % of fork disputes resolved within deadline.
- Post‑fork rights-floor compliance.

---

### 4) FEDERATION — compacts as a programmable layer (polycentric stability)
Federation is the *default alternative* to secession: modular delegation under explicit compacts.

**MUST**
- **Compact register:** compacts are published as `COMP-*` with:
 - Delegated powers list (what is delegated; what is reserved).
 - Funding flows, settlement rules, and audit hooks (`110-budget-procurement-integrity.md`).
 - Exit / amendment clause + timelines (reversibility lock).
 - Interop obligations (`70`, `71`) and continuity rules (`109`).
 - Conflict‑of‑laws and dispute lane (`114`).
- **Sunsets for delegations:** any extraordinary delegation MUST sunset unless renewed under contestable process (`112-exception-control-and-emergency-powers.md`).

**SHOULD**
- **Mutual recognition floor:** define what must be recognized across members (identity, credentials, judgments) and how exceptions are logged.

---

## Failure modes and guardrails

- **Fragmentation / governance arbitrage:** mitigate with a **rights floor**, minimum service standards, and transparent fiscal settlement.
- **Race to the bottom:** mitigate with baseline labor/environment/human rights floors + publishable enforcement stats.
- **Coercive secession / ethnic cleansing risk:** require credible coercion safeguards, monitoring, and circuit breakers (`116`, `105`).
- **Exit as abandonment:** use “exit insurance” and portability to prevent stratified lock‑in.

---

## Where this plugs into the stack
- Continuity and transfers: `109`, `114`
- Legitimacy + duty-to-respond: `106`, `111`
- Time budgets / deadlines: `108`
- Coercion safeguards: `116`, `112`
- Fiscal settlement + audit: `110`

---

## References (anchors)
- [BIB-HIRSCHMAN-EVL] (exit/voice framing)
- [BIB-OSTROM-POLYCENTRIC] (polycentric governance / federation logic)
