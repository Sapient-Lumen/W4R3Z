# Association & Collective Power (Exit is not enough)

**Goal:** make “voice” workable at scale by protecting **association, collective bargaining, and collective filing**—without requiring heroic personal risk.

This memo adds a portable interface layer: **Association Integrity** (you can organize), **Negotiation Integrity** (the other side must respond), and **Collective Remedy** (systemic harms can be fixed as a class).

## Why this matters (scope-agnostic)

Individual contestation fails when:
- harms are **systemic** (patterned denials, discriminatory enforcement, repeated safety violations),
- people face **retaliation risk** (jobs/housing/immigration status),
- bargaining power is **asymmetric** (monopsony/employer dominance; platform lock-in),
- costs to file are **too high** (time, counsel, documentation).

**Design requirement:** government must provide *safe collective channels* that produce receipts, clocks, and binding responses—otherwise “participation” is theater.

## AIP — Association Integrity Protocol

### AIP-1 Protected association lane (AAL-*)
- MUST: provide at least one **Association Access Lane** (staffed + non-digital option) that allows people to:
  - register an association/collective (or an intent-to-organize),
  - request protected communication channels,
  - request interim protections.
- MUST: issue an **Association Access Receipt (`AAL-*`)** with:
  - covered people/org, scope, start date, and renewal cycle,
  - confidentiality settings (public / pseudonymous / sealed),
  - anti-retaliation triggers and escalation contacts.

### AIP-2 Anti-retaliation defaults (circuit breakers)
- MUST: treat **credible retaliation risk** as an **interim protection** trigger (see `105-institutional-circuit-breakers.md`, `121-whistleblowing-and-protected-disclosure.md`).
- SHOULD: require **Reason Receipts** for adverse actions against covered persons during protected windows, with accelerated review.

### AIP-3 Collective representation (REP-*)
- MUST: publish rules for who can represent whom (union, worker council, tenant association, consumer group, disability org).
- SHOULD: allow **co-representation** (advocate + counsel + community org), and allow opt-in/opt-out.

## NIP — Negotiation Integrity Protocol (bargaining that binds)

### NIP-1 Duty-to-respond and time budgets (NTR-*)
- MUST: when a covered collective submits a proposal, the counterparty must produce a **Negotiation Response Receipt (`NTR-*`)** within a published time budget (see `108-service-standards-and-time-budgets.md`):
  - accept / reject / counter with reasons,
  - disclose what evidence would change the decision,
  - specify next meeting/timebox if continuing.

### NIP-2 Regulatory footprint for bargaining (influence legibility)
- SHOULD: attach a **footprint**: who negotiated, who advised, conflicts/recusals, and any outside influence (see `120-conflicts-of-interest-and-influence-integrity.md`).

### NIP-3 Impasse handling (bounded decider)
- MUST: define an impasse pathway: mediation → arbitration/board → bounded binding decision, with an explicit scope of authority and appeal lane (see `114-interjurisdictional-dispute-and-coordination.md`, `08-remedy-and-grievance.md`).

## CRM — Collective Remedy Mechanisms (systemic fixes)

### CRM-1 Collective filing lane (CFL-*)
- MUST: provide a **Collective Filing Lane** that accepts:
  - grouped individual complaints (“bundle”),
  - pattern claims (statistical + narrative),
  - representative complaints.
- MUST: issue a **Collective Filing Receipt (`CFL-*`)** linking to:
  - affected population definition,
  - evidence bundle pointers (stable record ids),
  - requested remedies (policy fix, restitution, injunction, audit).

### CRM-2 Pattern remediation
- SHOULD: require agencies to maintain a **Pattern Remediation Register** for repeated harms:
  - publish recurring issue clusters,
  - publish corrective actions + deadlines,
  - publish outcome metrics and rollback if ineffective.

### CRM-3 Safe publicity
- MUST: allow **anonymized aggregation** publication when publicity increases retaliation risk.
- SHOULD: provide protected “named to oversight only” pathways.

## Minimal metrics (publishable)

- % of collective proposals answered within time budget (NTR compliance).
- Retaliation allegation rate + time-to-protection.
- Share of systemic harms that reach pattern remediation vs. repeated individual appeals.
- Remedy effectiveness: recurrence rate after remediation.

## Anchors
- Control loops + circuit breakers: `104-governance-control-loops.md`, `105-institutional-circuit-breakers.md`
- Time budgets: `108-service-standards-and-time-budgets.md`
- Influence footprint: `120-conflicts-of-interest-and-influence-integrity.md`
- Protected disclosure lane (anti-retaliation patterns): `121-whistleblowing-and-protected-disclosure.md`
- Dispute coordination (impasse / bounded binding): `114-interjurisdictional-dispute-and-coordination.md`

## References (keys)
- [BIB-ILO-C87], [BIB-ILO-C98], [BIB-ICESCR-ART8], [BIB-UNGP] (see `91-bibliography-extended.md`)
