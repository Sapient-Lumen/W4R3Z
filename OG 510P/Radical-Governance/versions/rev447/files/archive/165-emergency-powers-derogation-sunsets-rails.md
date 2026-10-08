# Emergency Powers: Derogation, Sunsets, and Receipted Exceptions (Rails)

**Merge relation:** canonical emergency-powers memo for this cluster. Pair with `186-emergency-powers-derogations-and-sunset-discipline.md` for the narrower ledger/renewal discipline layer, and with `112-exception-control-and-emergency-powers.md` / `23-emergency-governance-and-exceptions.md` for the wider exception-control frame.


**Purpose:** make emergency authority **fast** without becoming **sticky** (normalized exception) by routing crisis actions through **time-bounded rails**: proclamation → receipts → review → unwind.

**Person served:** anyone living under emergency measures who needs: (1) **scope + time limits**, (2) **reachable review**, and (3) **reversal/repair** while harm is still preventable.

**From-below thesis:** emergencies are when discretion expands and ordinary accountability fails; therefore emergency powers must be *more* rule‑bound than normal, not less.

**Links:** baseline emergency memo `23-emergency-governance-and-exceptions.md`; circuit breakers `105-institutional-circuit-breakers.md`; threat models `04-threat-models.md`; remedy `08-remedy-and-grievance.md`; coercion `05-public-safety-and-coercion.md`; service time budgets `108-service-standards-and-time-budgets.md`; procurement integrity `110-budget-procurement-integrity.md`; accessibility invariants `98-persons-path-and-accessibility-invariants.md`.

---

## 1) The minimum legal/legitimacy floor (non-negotiable)

A valid emergency regime MUST satisfy:

1. **Declared + justified:** proclamation in writing with a **public statement of necessity** and measurable triggers for continuation/termination (necessity + proportionality). [BIB-VENICE-SOE-COMPILATION-2020]
2. **Time-bounded:** short initial duration; renewal only with **affirmative** legislative approval; *no “evergreen” renewal by default*. (Transience principle.) [BIB-VENICE-SOE-COMPILATION-2020]
3. **Non-derogable core protected:** clearly list rights that remain non‑derogable (e.g., torture ban) and *treat other rights as derogable only when strictly required*; record the article-by-article rationale. [BIB-UNHRC-GC29-2001] [BIB-SIRACUSA]
4. **Independent review stays reachable:** courts/tribunals (or emergency panels) remain **operational**, with *degraded-mode* access (phone/SMS/low-bandwidth, physical kiosks). [BIB-UNHRC-GC29-2001]
5. **Receipt + record continuity:** every coercive act and rights-limiting order produces a **receipt**: who authorized, legal basis, time window, appeal path, and data-retention rule. (See “receipted coercion” pattern in `23` and `98`.)
6. **Sunset + unwind plan:** a “return-to-normal” playbook is published at the start: which measures auto-expire; how data is deleted; how compensation/remedy runs. (Normalization is a known failure mode.) [BIB-SUNSET-CLAUSES-2016]

---

## 2) The emergency “rails” (small set of standardized flows)

### Rail A — Proclamation packet (Day 0)
A single public packet (machine + human readable) containing:
- **Threat statement** + evidence snapshot (what is known/unknown).
- **Scope map:** geography, populations, sectors.
- **Measures list:** each measure with purpose, rights impact, legal basis, start/end time.
- **Oversight wiring:** which body reviews what, on what schedule, and how the public can contest.
- **Termination triggers** and planned demobilization steps.

Use a canonical format to prevent “silent swaps” (measure changes without notice). (See integrity joins `388`.)

### Rail B — Renewal hearing (e.g., Day 7 / Day 30)
Renewal is a **decision**, not a default:
- Publish an **impact + rights audit** (what worked, harm caused, alternatives).
- Require **less-restrictive alternatives** analysis (why each restriction remains necessary). [BIB-UNHRC-GC29-2001]
- Force **scope narrowing** where the exigency has changed (proportionality drift). [BIB-VENICE-SOE-COMPILATION-2020]
- Renewal vote requires **reasoned findings** and a **new sunset** (no rolling “forever” periods).

### Rail C — Emergency procurement (Day 0+)
Emergency spending is where capture spikes. Route through:
- **Exceptional procurement ledger:** contract, vendor, unit price, justification, delivery proof, conflict disclosures.
- **Fast but auditable** vendor selection (prequalified pools + random audits).
- **Anti-price-gouging comparators** + clawback clauses.
See `110-budget-procurement-integrity.md` and `162-procurement-as-governance-lever-and-guardrails.md`.

### Rail D — Rights-impact & discrimination guardrails (continuous)
- Publish a **rights-impact register**; log restrictions + affected groups.
- Require **anti-discrimination checks** and accessible exemptions.
- Provide **appeal channels** that work under degraded infrastructure (`98`).

### Rail E — Exit + repair (automatic)
On termination:
- Automatic expiry of emergency rules unless explicitly re-enacted in ordinary law.
- Data deletion and retention review for emergency collections.
- **After-action inquiry** with subpoena power + public report.
- A **repair channel**: compensation, apology, record correction, expungement where appropriate (`08`).

---

## 3) Design patterns to prevent “emergency drift”

### Pattern: Two-key authorization for rights-limiting measures
For severe restrictions (movement bans, detention expansions), require *two* independent sign-offs (executive + judicial/legislative delegate) with documented rationale.

### Pattern: “Least restrictive by default”
If evidence worsens, restrictions may tighten temporarily; otherwise the default is **automatic loosening** unless renewed with proof. This flips incentives against permanent exception. [BIB-SIRACUSA]

### Pattern: Degraded-mode justice
Assume infrastructure breaks: keep a minimal “justice hotline” + paper receipt stations; publish emergency orders on radio/SMS where needed (`98`).

### Pattern: Compulsory public log of executive orders
Every emergency order is numbered, versioned, and archived; changes require a public diff. (Anti–silent-swap.)

---

## 4) Scope fit notes (micro → global)

- **Micro/local:** focus on mutual aid activation, localized health/safety orders, and *rapid grievance handling*; avoid militarized “blanket” rules.
- **Regional/national:** concentrate on legal rails + procurement integrity + review capacity; publish interoperable formats so localities can comply without confusion.
- **Global:** prefer **coordination compacts** and shared data standards over coercive uniformity; legitimacy comes from transparency, reciprocity, and exit options (polycentric governance). [BIB-OSTROM-POLYCENTRIC-2010]

---

## 5) Implementation checklist (copy/paste)

- [ ] Proclamation packet published (scope, measures, sunset, oversight, termination triggers).
- [ ] Renewal schedule set with mandatory rights/impact report.
- [ ] Non-derogable and strictly-required analysis documented (article-by-article).
- [ ] Courts/tribunals reachable in degraded mode; fast appeal path defined.
- [ ] Receipted coercion + record continuity working end-to-end.
- [ ] Emergency procurement ledger live; random audits scheduled.
- [ ] Exit + repair plan published on Day 0; after-action inquiry pre-authorized.
