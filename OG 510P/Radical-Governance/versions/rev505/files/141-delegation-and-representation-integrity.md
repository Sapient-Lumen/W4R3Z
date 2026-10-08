# Delegation & Representation Integrity

**Problem:** a huge share of power is exercised *by proxies* (representatives, agents, administrators, appointees, advocates, guardians, party whips, procurement officers, algorithm owners). Without explicit delegation interfaces, delegation becomes a capture surface: invisible mandates, “acting on your behalf” without standing, and unreviewable discretion.

**Goal:** make delegation *legible, bounded, revocable, and contestable* with receipts and clocks—so the governed person can prove: who acted, under what authority, for how long, with what conflicts, and how to challenge it.

**Family relation:** use `307-legitimacy-representation-elections-and-selection-guide.md` for the canonical route across legitimacy architecture, electoral-system choice, election administration, legitimacy-engine comparison, selection integrity, and mandate / delegation integrity.

## Minimal primitives

**DLR-* — Delegation Letter Receipt (grant)**
- Names: principal(s), delegate(s); domain + scope; allowed actions; expiry; renewal rules.
- Standing: who can contest; harm thresholds; emergency carve‑outs.
- Controls: conflict disclosure link (`120`), record pointer (`115`), and audit trail (`130`).

**DVR-* — Delegation Verification Receipt (use)**
- Issued when a delegate attempts an action: validates active DLR scope, time, and identity.
- MUST be returned to the principal (and the counterparty) as a checkable token.

**DRR-* — Delegation Revocation Receipt (stop)**
- Immediate revocation for non‑essential domains; bounded delay only for critical safety continuity (joins `109/112/137`).
- Anti‑retaliation: revocation cannot trigger adverse action unless a separate, receipted safety/abuse finding exists.

**RMR-* — Representative Mandate Receipt (collective/office)**
- For elected/selected bodies, clearly bind: constituency, term, decision rights, abstention/recusal rules, and decision trace join (`111/118`).
- Requires a public “mandate card” (joins `132`) and conflict controls (`120`).

**AOR-* — Authority‑of‑Record Pointer**
- Stable pointer to the authoritative DLR/RMR version and change history (joins `115/118`).

## Safety & abuse handling (tight)
- **Capacity / guardianship:** if capacity is disputed, the system MUST create a *reviewable* interim rule with time bounds and a contest lane (joins `08/125/112`).
- **Coercion risk:** if delegation is coerced, issue a protection receipt and freeze non‑essential delegated actions pending review (joins `116/121`).

## Minimum publishable metrics
- % of delegated actions with DVR receipts issued and returned to principals.
- revocation time (median) and % blocked by unjustified “continuity” claims.
- conflict disclosure completeness for delegates in high‑stakes domains.
- reversal/complaint rate for delegate‑executed decisions vs direct decisions.

## Joins (do not duplicate)
- Records/disclosure: `115` \
- Change control: `118` \
- Conflicts/influence: `120` \
- Audit follow‑through: `130` \
- Portability/continuity: `109/114` \
- Coercion safety: `112/116` \
- Deliberation binding: `111` \
- Selection integrity (if delegates are selected by lot): `119`
