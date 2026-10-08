# Restorative Justice & Conflict-Resolution Rails (Reduce coercion; increase repair)

**Aim:** provide a **non-carceral default lane** for many harms (where safe and appropriate), with **real remedy** and **tight safeguards** against coercion, intimidation, and “justice theater.”

**This memo is not** a full criminal-justice theory. It’s a **governance interface**: receipts, clocks, safety gates, and escalation rules.

## 190.1 Scope & eligibility (what belongs here)

Use restorative / mediated processes when:
- the harmed person has **safe choice** (no intimidation; informed consent)
- the person who caused harm acknowledges enough facts to participate meaningfully (or the process is explicitly *dialogue-only*)
- power imbalances can be mitigated (advocates, separate sessions, safety plan)
- outcomes can be **monitored and enforced** without hidden coercion

Do **not** use as a substitute for due process when:
- violence/coercion risk is high and cannot be mitigated
- the process would function as compelled confession
- the harmed person cannot safely refuse

**Anchor:** UN restorative justice principles emphasize voluntary participation, safety, and respect for rights and due process. citeturn0search0turn0search16

## 190.2 Core invariants

1) **Voluntariness is real** (no penalty for refusal; refusal cannot worsen standing).
2) **Safety dominates** (protective measures are first-class, not optional).
3) **Rights remain intact** (restorative lane cannot waive basic rights by default).
4) **Repair is concrete** (agreements specify actions, deadlines, verification).
5) **Coercion boundary is explicit** (what is confidential; what is reportable; what can be used later).

## 190.3 Minimal artifacts (the receipts)

### A) Offer & consent
- **RJO‑OFR** — Restorative Justice Offer Receipt
  - eligibility basis, lane options (restorative / adjudicative / hybrid)
  - explicit “refusal is safe” clause
  - advocate access + interpreter access

- **RJO‑CON** — Consent Receipt
  - informed consent checklist (rights, risks, confidentiality limits)
  - power-imbalance assessment + mitigations
  - withdrawal path (any time) + safety escalation

### B) Safety & power
- **RJO‑SAP** — Safety & Power Plan
  - contact constraints, logistics, separate-session option
  - retaliation tripwires + interim protections
  - facilitator conflict/recusal record

### C) Process + outcomes
- **RJO‑PRC** — Process Receipt
  - process type (mediation / conferencing / circles / shuttle)
  - facilitator credentials + independence assertions
  - session log (minimal metadata; no sensitive content by default)

- **RJO‑AGR** — Agreement Receipt
  - concrete repair commitments (actions, deadlines)
  - verification method + who can attest
  - contingency rules if partial compliance

- **RJO‑FUP** — Follow‑Through Receipt
  - progress checkpoints + completion assertion
  - breach handling (see 190.5)

## 190.4 Confidentiality & data governance

**Default:** keep content private; publish only minimal metadata needed for oversight.

- **RJO‑COV** — Confidentiality & Use‑of‑Info Voucher
  - what is confidential
  - what is mandatory-reportable
  - what is admissible later (default: narrow; must be explicit)

**Anti‑trap rule:** restorative participation cannot be a covert evidence‑harvesting pipeline.

(Aligns with international guidance emphasizing voluntariness and safeguarding rights.) citeturn0search0turn0search16

## 190.5 Breach, non‑compliance, and escalation

Define a **bounded breach ladder** that avoids both impunity *and* coercive bait‑and‑switch:

1) **Repair renegotiation window** (if safe) → issue amended `RJO‑AGR`.
2) **Binding decider** assigns fallback remedy lane (civil, administrative, criminal) with **continuity defaults** (no ping‑pong).
3) If escalation occurs, **receipt the reason** (why restorative lane failed; which safeguard tripped).

## 190.6 Oversight without “therapy theater”

Publish aggregate, privacy‑preserving oversight artifacts:
- count of offers, consents, withdrawals
- completion rates
- re‑harm signals / safety incidents
- time‑to‑resolution distributions

Require periodic independent audit of:
- voluntariness integrity (no coercion via prosecutors/administrators)
- facilitator independence and training
- disparate impact (who gets offered restorative lanes; who gets denied)

## 190.7 Integration points

- Coercion governance: `116-coercion-use-of-force-and-detention-governance.md`
- Sanctions integrity: `131-compliance-and-sanctions-integrity.md`
- Whistleblowing / retaliation: `121-whistleblowing-and-protected-disclosure.md`
- Legitimacy & selection integrity (panel models): `180-...`, `119-...`

## 190.8 Quick tests

- Can a harmed person refuse restorative process **without penalty**?
- Is there a **written confidentiality boundary** (`RJO‑COV`)?
- Are agreements concrete and enforceable (`RJO‑AGR` + `RJO‑FUP`)?
- Are intimidation risks actively mitigated (`RJO‑SAP`)?

