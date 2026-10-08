# 409 — Interoperability assessments before binding digital rules

## One-line thesis

Before governments freeze new digital requirements into law, policy, procurement, or platform mandates, they should run a formal **interoperability assessment** that tests cross-border, cross-agency, and multi-vendor consequences early enough to change course.

## Why this matters

A large share of digital-state failure begins upstream, when a seemingly local requirement hardens into a binding rule that breaks data exchange, duplicates identifiers, traps agencies in bespoke formats, or silently exports administrative burden to everyone else.

By the time the service launches, the architecture is already political fact.

Interoperability therefore should not be treated as a late technical clean-up task. It should be a pre-commitment discipline that asks, before a rule hardens:

- who must exchange data or status under this requirement,
- what legal and semantic conflicts it creates,
- what existing shared solutions already exist,
- how the change affects portability, contestability, and continuity.

## Design rule

No materially binding digital requirement should ship without a short, published interoperability assessment that covers:

- legal fit,
- organisational fit,
- semantic fit,
- technical fit,
- reuse of existing common components,
- migration and deprecation effects,
- burden shifted onto other institutions or users.

## Pattern pack

### 1. Run the assessment before the rule is frozen

Do it before:

- statutory language is final,
- procurement assumptions are locked,
- APIs are treated as settled,
- migration budgets disappear,
- implementers start coding around avoidable defects.

Late interoperability review usually becomes ceremonial.

### 2. Treat interoperability as four-dimensional

The assessment should examine at least:

- **legal** compatibility,
- **organisational** responsibilities and incentives,
- **semantic** consistency of terms, codes, and statuses,
- **technical** compatibility of identifiers, formats, interfaces, and security models.

A project that only checks data transport usually misses the real failure.

### 3. Map affected actors explicitly

Every assessment should name:

- the bodies that must implement the rule,
- the third parties who must integrate with it,
- the users who will bear extra steps or ambiguity,
- the offices that inherit the exception queues and reconciliation work.

This prevents “local optimisation, system-wide burden.”

### 4. Reuse before rebuild

The team should identify:

- existing standards,
- reusable registries,
- common API components,
- shared identifiers,
- open-source reference implementations,
- adjacent policy or treaty constraints.

If a new requirement ignores reusable infrastructure, the assessment should say why.

### 5. Publish the burden transfer

A good assessment records where the new rule shifts cost:

- onto municipalities,
- onto frontline workers,
- onto residents who now need extra proofs,
- onto successor vendors,
- onto cross-border partners.

Interoperability failure is often just hidden cost transfer with a nicer name.

### 6. Include a migration and deprecation plan

If the requirement changes a live system, the assessment should specify:

- backward-compatibility window,
- dual-running period,
- cutover trigger,
- rollback path,
- data conversion rules,
- archival treatment of old statuses and codes.

### 7. Tie the assessment to decision rights

The assessment must be able to do more than advise. It should be able to:

- trigger redesign,
- require exception handling,
- narrow scope,
- demand reuse of existing solutions,
- delay launch until minimum interoperability conditions are met.

## Guardrails

- Assessments should be short enough to be used, but strong enough to block obvious design debt.
- They should not become a consultant artifact detached from the real policy and build decisions.
- Exemptions should be rare, time-limited, and logged publicly.
- “Urgency” should shorten the format, not erase the discipline.
- The process should include implementers and service operators, not only policy authors.

## Failure modes

- **late discovery**: incompatibilities surface only after procurement or launch.
- **transport-only thinking**: teams check APIs but ignore legal and semantic conflicts.
- **local exceptionalism**: every agency claims its case is too special for reuse.
- **burden dumping**: complexity is exported to smaller bodies or end users.
- **advisory theater**: the assessment exists but cannot alter the decision.

## Practical tests

A binding-rule workflow passes when it can answer yes to all of the following:

1. Was the assessment completed before the binding requirement became hard to change?
2. Did it cover legal, organisational, semantic, and technical dimensions?
3. Did it identify reusable solutions instead of defaulting to bespoke build?
4. Did it show who absorbs the migration and reconciliation burden?
5. Can the assessment still stop or narrow a launch?

## Compression rule for the archive

Before a public digital rule hardens, ask:

**What other institutions, systems, and people now have to bend around this decision?**

If no one can answer concretely, interoperability has not been governed yet.
