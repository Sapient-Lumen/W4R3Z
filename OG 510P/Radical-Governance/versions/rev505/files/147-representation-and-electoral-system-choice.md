# Representation & electoral-system choice (fit-for-scope, fit-for-task)

**Purpose:** provide a *scope-aware* checklist for choosing (or reforming) electoral systems so representation is legitimate, governable, and resistant to manipulation.

**Person served:** a voter who wants their voice to matter **without** elections becoming a permanent crisis.

**From-below:** electoral systems are incentive engines. If the incentives reward polarization, gerrymandering, or factional capture, the public pays forever.

**Scope note:** this memo is **about electoral system choice**, not election operations, party-system design, or executive-form choice (see `56-elections-and-electoral-administration.md` for Minimum Viable Election Integrity and auditable pipelines, `312-party-systems-candidate-selection-caucus-governance-and-anti-defection-rails.md` for party recognition / nomination / caucus / anti-defection design, and `311-executive-system-choice-parliamentary-presidential-semipresidential-and-collegial-rails.md` for parliamentary vs presidential vs semi-presidential / collegial design).
**Family relation:** use `307-legitimacy-representation-elections-and-selection-guide.md` for the canonical route across legitimacy architecture, electoral-system choice, party-system design, election administration, legitimacy-engine comparison, selection integrity, and mandate / delegation integrity. Use `309-representative-chambers-committees-opposition-rights-and-confidence-architecture.md` when the question shifts from seat-allocation design to chamber structure, committee systems, opposition protections, or confidence architecture. Use `312-party-systems-candidate-selection-caucus-governance-and-anti-defection-rails.md` when the question shifts from how votes become seats to how parties, nominations, caucuses, and anti-defection rules shape the political field around those seats. Use `311-executive-system-choice-parliamentary-presidential-semipresidential-and-collegial-rails.md` when the question shifts from how votes become seats to what kind of executive those results are meant to support.

Anchors: International IDEA’s electoral-system design handbook [BIB-IDEA-ESD]; ACE electoral system design topic notes (mixed systems, MMP, etc.) [BIB-ACE-ESD-MIXED], [BIB-ACE-ESD-MMP]; Venice Commission *Code of Good Practice in Electoral Matters* [BIB-VENICE-ELECT].

---

## 0) The non-negotiables (whatever system you pick)

1) **Equal vote weight** (or explicit, justified deviations) and anti-gerrymandering constraints.
2) **Contestability:** clear disputes lanes + deadlines (`AL-*`), and no silent procedural changes (`118-...`, `53-...`).
3) **Access:** language/disability access, assistance paths, and no-wrong-door support (`98-...`, `56-...`).
4) **Coercion ceilings:** protect voters/workers from intimidation; publish safe incident reporting (`05-...`, `56-...`, `83-...`).
5) **Representation honesty:** do not pretend a system produces “proportional representation” unless it actually does at the seat-outcome level.

---

## 1) Choose the *task* first: what is the election for?

Electoral systems are not one thing. The correct choice depends on which legitimacy generator you are running (`21-legitimacy-architecture.md`).

- **Task A — Choose a single executive / mayor / governor:** you want a *majority-backed* winner without rewarding strategic extremism.
- **Task B — Allocate seats in a council/legislature:** you want *representative composition* and coalition incentives.
- **Task C — Select local stewards / boards:** you want competence + accountability in a small body.

**Rule of thumb:**
- For **Task B**, prioritize **multi-winner proportionality**.
- For **Task A**, prioritize **majority legitimacy** with incentives that reduce negative partisanship.

---

## 2) Fit-for-scope heuristics (micro-local → global)

### Micro-local (building/block/co-op/community)
**Goal:** legitimacy + participation + low admin burden.

**Prefer**
- Small councils/boards: **multi-winner ranked (STV)** or **approval/score for multi-seat** where ballot simplicity matters.
- Hybrid governance: add **sortition seats** for anti-clique resilience (`119-...`, `10-micro-local.md`).

**Avoid**
- Winner-take-all single seats for everything (breeds factional lock-in).

**Hard requirement:** clear recall/rotation rules and conflicts disclosure (`120-...`, `123-...`).

### Municipal / regional
**Goal:** stable governing coalitions + representation across neighborhoods/communities.

**Prefer**
- **Multi-member districts with proportional methods** (ranked STV or list PR with credible district magnitudes).
- If you need geographic accountability, prefer **multi-member** districts over many single-member districts (reduces gerrymander surface area).

**If using single-member districts:**
- impose **independent districting** + compactness/communities-of-interest constraints + publish districting artifacts as `REL-*`.

### National
**Goal:** represent pluralism while preventing minority rule and constitutional hard-lock.

**Prefer**
- **PR** (district or national) when pluralism is real and coalition bargaining is acceptable.
- **MMP** when you want both local representatives **and** proportional outcomes (the compensatory tier is the core property).

**Watch-outs**
- Thresholds can reduce fragmentation *or* disenfranchise persistent minorities; treat threshold choice as a rights-affecting rule with explicit rationale + review triggers.
- If executive elections coexist with PR legislatures, publish the *coalition formation norms* and cabinet accountability rules (avoid backroom ambiguity).

### Supranational / global bodies
**Goal:** legitimate representation across units with radically different sizes + preserve functional decision capacity.

**Prefer**
- **Two-chamber / dual-weight** designs: one chamber proportional by population, another by member units (federal logic), with clear competence split (`136-polycentric-...`).
- When direct elections are infeasible, require transparent appointment pipelines and mandate/recusal rules (`132-mandates-...`, `120-...`).

**Hard requirement:** prevent domination by financing: publish contributions and influence channels; enforce conflicts/recusal and contribution caps (`46-...`, `22-...`).

---

## 3) The “system family” chooser (quick map)

This is a *design filter*, not a complete taxonomy.

### Plurality / majoritarian single-winner (FPTP, two-round, etc.)
- **Pros:** simple story; geographic accountability.
- **Cons:** can produce durable minority rule; gerrymander/capture surface is large; encourages negative partisanship.
- **Use when:** very small executive races where the majority legitimacy story is paramount.

### Ranked-choice single-winner (IRV/RCV)
- **Pros:** reduces spoiler dynamics; can broaden appeal incentives.
- **Cons:** tabulation complexity narratives; not proportional for multi-winner bodies.
- **Use when:** you need a single winner and want to reduce spoiler/extremism incentives.

### List PR / open list PR
- **Pros:** proportional outcomes; coalition incentives.
- **Cons:** party control risks; open-list design can create intra-party spending arms races.
- **Use when:** representative legislatures.

### STV (multi-winner ranked)
- **Pros:** proportional-ish outcomes with voter-level ranking; reduces party gatekeeping.
- **Cons:** more complex ballots; count process must be well-explained and auditable.
- **Use when:** municipal/regional councils with multi-member districts.

### Mixed systems (parallel vs compensatory)
- **Parallel:** two systems run side-by-side; outcomes need not be proportional.
- **MMP:** compensatory tier corrects disproportionality (this is the defining feature).
- **Use when:** you need both local representation and overall proportional outcomes.

---

## 4) Manipulation attack surface (treat as threat model)

**Design choices that become attack surfaces:**
- District boundaries (gerrymandering).
- Ballot access rules (who can compete).
- Thresholds and seat-allocation formulas.
- Administrative discretion (polling places, curing rules, emergency changes).

**Mitigations:**
- Publish all controlling rules as `RULE-*` with versioning (`25`, `39`).
- Publish districting, tabulation, and seat-allocation artifacts as `REL-*` with methods notes (`51`, `53`, `56`).
- Pre-commit audit/recount triggers and dispute timelines (`56`, `36`, `08`).

---

## 5) Reform method (how to change systems without civil war)

**Minimum viable reform pipeline:**
1) **Problem statement** as claims + measures (`CLM-*` + `IPM-*`), including what harms the current system produces.
2) **Representative deliberation** on options (jury/assembly) with a binding pathway (`111`, `143`, `119`).
3) **Option set** with “who wins/loses” analysis (capture resistance: `99-protective-legibility...`).
4) **Staged roll-out** with sunset + evaluation triggers (avoid irreversible mistakes) (`118`, `03`).

---

## 6) Tiny checklist (what to write down)

- What *task* does this election serve (A/B/C)?
- What scope is it (micro/local/municipal/regional/national/supranational)?
- What representation promise are we making (majority mandate / proportional composition / geographic accountability)?
- What are the main manipulation surfaces, and what artifacts make them checkable?
- What are the failure modes (polarization, minority rule, fragmentation, capture, legitimacy crisis), and what metrics detect them?

