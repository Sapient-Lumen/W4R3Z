# Legitimacy Protocols (DEC primitives that scale)

**Purpose:** make legitimacy **operational** (not vibes): who can decide what, on what basis, with what standing, and with what contestability—across scopes.

**Design stance:** legitimacy is a *protocol* with receipts. If a person can’t understand **why** they’re bound, and can’t **contest** the binding, the system is illegitimate *for them* in practice.

---

## DEC‑0: Minimal legitimacy contract (MUST)

Every governance interface that binds a person **MUST** provide:

1) **Authority receipt** — *who* has jurisdiction and *why* (charter, mandate, delegation chain).  
2) **Reason receipt** — the decision basis: rule/standard + facts used + uncertainties.  
3) **Standing map** — who could have influenced the outcome (participation routes) and who can contest it (appeal routes).  
4) **Contest window** — time limits + interim protection where delay would irreversibly harm rights/livelihood.  
5) **Reversibility note** — what can be undone, what cannot, and what compensation exists if wrong.

(Interface hooks: pair with `71-interface-obligations-by-scope.md`, `08-remedy-and-grievance.md`, and the loop spec in `104-governance-control-loops.md`.)

---

## DEC‑1: Consent/voice/exit by scope (SHOULD)

**Rule of thumb:** as scope grows, *exit* becomes less realistic; therefore **voice and contestability must strengthen**.

- **Micro‑local (house/building/block):** exit is plausible ⇒ decisions can lean on *opt‑in* and lightweight rules, but MUST include rapid grievance + anti‑harassment protections.
- **Municipal/metro:** partial exit ⇒ require *layered voice* (neighborhood + citywide), accessible agenda‑setting, and strong due‑process on services.
- **Regional/national:** exit mostly implausible ⇒ require **constitutionalized rights**, independent remedy, and strict limits on discretionary coercion.
- **Global / transnational regimes:** exit often impossible (externalities) ⇒ legitimacy MUST include *representation plus transparency* and enforceable contest for affected parties, not just members.

---

## DEC‑2: Deliberation minimums (MUST for high‑stakes)

For decisions that materially affect rights, safety, livelihood, or status, procedures MUST meet:

- **Effective participation**: real opportunity to submit reasons/evidence.  
- **Voting equality / equal weight where votes apply**.  
- **Enlightened understanding**: accessible information about alternatives and consequences.  
- **Control of agenda**: routes for affected parties to put issues on the agenda.  
- **Inclusion**: affected adults aren’t arbitrarily excluded.

(Operationalizes classic democratic process criteria associated with Dahl; see references.)

Where deliberation is used (citizens’ assemblies, councils, juries), treat “equal ability to speak” and “ability to challenge claims” as *test conditions*, not decor.

---

## DEC‑3: Commons legitimacy (SHOULD when shared resources)

When governing shared resources (land, fisheries, digital commons), legitimacy SHOULD follow: clearly defined boundaries, congruence with local conditions, collective choice, monitoring, graduated sanctions, low‑cost conflict resolution, recognition of local autonomy, and nested enterprises (for large systems). (See Ostrom references.)

---

## Failure modes to pre‑wire (fast checklist)

- **Shadow authority** (who decided is unclear) → publish delegation chain and decision owner.  
- **Fake participation** (comment box with no influence) → publish how inputs moved the outcome (or why not).  
- **Delay‑as‑control** → interim relief + deadlines + default escalation (see `105`).  
- **Epistemic capture** (only insiders can argue) → plain‑language reasons + assistance + representative advocacy.  

---

## References (cite, don’t quote)

- Robert A. Dahl, *On Democracy* (criteria for democratic process).  
  Link: https://newuniversityinexileconsortium.org/wp-content/uploads/2022/08/Robert-A.-Dahl-On-Democracy-1998-1.pdf  
- Jürgen Habermas (overview of discourse ethics / communicative action).  
  Links: https://plato.stanford.edu/archives/win2024/entries/habermas/ ; https://iep.utm.edu/habermas/  
- Elinor Ostrom design principles for governing commons (overview + generalizations).  
  Links: https://patternsofcommoning.org/uncategorized/eight-design-principles-for-successful-commons/ ; https://www.sciencedirect.com/science/article/abs/pii/S0167268112002697

