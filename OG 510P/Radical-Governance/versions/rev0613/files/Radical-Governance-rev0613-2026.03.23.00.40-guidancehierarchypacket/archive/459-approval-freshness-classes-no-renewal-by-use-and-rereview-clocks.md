# 459 — Approval freshness classes, no renewal by use, and rereview clocks

## One-line thesis

Consequential public-AI approvals, waivers, elevated grants, and standing adoption decisions should carry explicit freshness classes and rereview clocks, and continued use or silence should not silently renew them.

## Why this matters

Public-AI governance already produces many approval-shaped objects: launch approvals, use-case approvals, determination records, waiver renewals, temporary access grants, supplier-adoption approvals, exception decisions, review signoffs, and emergency accommodations. Those artifacts often begin life with clear owners and dates. They become dangerous later.

The danger is not only that they expire. It is that they appear active long after the surrounding facts have cooled. Staff change roles. Operating context drifts. the system is used in new ways. A waiver that made sense during remediation becomes quiet background. A temporary grant stops being challenged because the work still feels familiar. A use-case approval keeps getting exercised and therefore *feels* current even though nobody explicitly re-reviewed it.

The archive already includes periodic reapproval, expiring deviations, and temporary authority leases. What it still lacked was one explicit freshness grammar: a way to say not only that an approval exists, but whether it is fresh, cooling, stale, frozen, revoked, or awaiting rereview — and what those states permit. The archive should therefore refuse silent renewal by ordinary use.

## Pattern pack

### 1. Apply freshness classes to approval-shaped governance objects

Relevant objects include:

- launch or release approvals,
- use-case approvals,
- determination or waiver records,
- elevated access grants,
- supplier or model adoption approvals,
- fallback accommodations,
- and standing review decisions that can influence later conduct.

The archive should treat them as living governance objects, not one-time paperwork.

### 2. Preserve last explicit review separately from last exercise

A freshness record should distinguish at least:

- when the object was last explicitly reviewed,
- when it was last exercised or relied on,
- what basis was in force at the last review,
- and whether later use occurred without a fresh review.

This prevents the common collapse where repeated operational use is mistaken for renewed governance attention.

### 3. Define freshness classes and what each one permits

A compact class system may vary by institution, but it should usually distinguish states such as:

- `fresh`,
- `cooling`,
- `stale`,
- `frozen`,
- `revoked`,
- or `review-pending`.

Each class should define what is still allowed, what requires supervisor review, what must pause, and what cannot resume without a new decision.

### 4. Make cooling and stale triggers explicit

Freshness should cool or freeze when relevant facts change, such as:

- material system change,
- role or owner change,
- dormancy,
- incident involvement,
- boundary widening,
- repeated reliance outside the originally approved scope,
- or unresolved dependencies in the approval basis.

A quiet record is not necessarily a current one.

### 5. Require explicit rereview for renewal

The archive should treat renewal as an affirmative event with:

- reviewer identity,
- scope,
- date,
- basis checked,
- and resulting freshness class.

Continued use, mere access, ongoing uptime, or the absence of complaints should not count as renewal.

### 6. Route stale objects toward the next honest action

A stale or cooling approval should not leave operators guessing. The system should say whether the next honest action is to:

- rereview,
- narrow scope,
- pause use,
- issue a temporary hold,
- retire the object,
- or obtain fresh authorization.

### 7. Technically constrain objects that have passed their live basis

Where practical, stale or expired approval-shaped objects should drive real system behavior, such as:

- disabling or narrowing access,
- blocking widening of scope,
- requiring second-person signoff,
- surfacing a visible warning,
- or preventing silent resume after interruption.

The archive should prefer freshness that bites over freshness that merely decorates.

## Guardrails

- Do not treat last use as if it were last review.
- Do not let silence or operational familiarity silently renew consequential authority.
- Do not allow stale approvals to widen scope by habit.
- Do not keep temporary or emergency accommodations active at administrator convenience.
- Do not hide cooling, stale, or frozen status inside back-office records only.

## Failure modes

- **immortal approval**: an old approval keeps governing because nobody reopened it.
- **touch-as-renewal**: routine use is mistaken for fresh review.
- **dormant authority return**: an old approval or grant springs back after a long quiet period.
- **cooling invisibility**: the basis has aged, but the surface still looks current.
- **stale-by-default operations**: the institution continues under inherited approvals because rereview never got operationalized.

## Practical tests

An approval-freshness discipline passes when it can answer yes to all of the following:

1. Do approval-shaped objects record last explicit review separately from last exercise?
2. Do they carry explicit freshness classes with allowed and forbidden actions?
3. Are cooling, stale, and frozen triggers named in advance?
4. Does renewal require an affirmative rereview event rather than mere continued use?
5. Can stale or expired objects technically constrain conduct instead of remaining decorative metadata?

## Compression rule for the archive

If an institution cannot answer **when this approval was last truly reviewed, how fresh it still is, and what use it still permits**, then the archive is still letting **habit** impersonate **authorization**.
