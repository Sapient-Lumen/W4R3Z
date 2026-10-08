# Portable public learning packet and recognition profile

## Current overlay

Portable public-learning packets now inherit the evidence-grade and security posture. AI-generated
summaries, recognition suggestions, or transfer narratives cannot become portable proof unless the
claim family, source trail, human owner, security boundary, and protected-record separation are
explicit.

This document closes the schema-and-recognition gap left open by the archive's public handoff
standard.

`minimum-public-entitlement-and-handoff-standard.md` already says adults and other residents should
not have to restart intake at every node. But that rule still needed a sharper answer to three
questions:

1. **what should actually travel** between nodes;
2. **what should stay local or protected**;
3. and **what receiving institutions should do** when a learner arrives with prior AI-learning
   completions from elsewhere.

The archive's current rule is:

> treat portability as a **small claim-and-recognition rail**, not as a giant learner dossier.

That means public AI-learning routes need enough structure for recognition, but not so much
structure that every workshop, advising exchange, or support interaction becomes a permanent
surveillance artifact.

This move is grounded in a converging set of signals. DOL's 2026 workforce guidance explicitly
encourages systems to capture, verify, communicate, own, and make portable learners' skills and
learning assertions. Credential Engine's 2025 prior-learning-recognition proposal argues that the
missing layer is transparent, machine-readable description of recognition policies, accepted
evidence, evaluation methods, and outcomes. 1EdTech's CLR work and W3C's Verifiable Credentials 2.0
both reinforce a learner-controlled issuer-holder-verifier model for portable, machine-verifiable
claims, while Europass's digital-credential stack shows a public-sector route for sharing verifiable
learning credentials in recognition procedures and further training. ACE's National Guide keeps the
higher-stakes edge in view: some external learning can count toward formal credit, but only through
recognized institutional evaluation rather than automatic import. See `B32`, `B40`, `B41`, `B42`,
`B43`, `B44`, `B45`.

## The archive's three-rail rule

A portable packet now has **three rails**.

### Rail 1. Machine-readable core claims

This is the portable public core. It should be structured, minimal, and verifiable.

The default claim set is:

- issuing node or organisation;
- issue date and, if relevant, expiry/review date;
- learner identifier only as needed for the use case;
- claim type;
- short title and description;
- public framework or competency alignment, if one exists;
- stake level or assurance level;
- verification method or URL;
- and an evidence pointer or evidence summary, not the raw evidence bundle itself.

The archive's default posture is that the machine-readable rail should say **what is being
claimed**, **who claims it**, **how it can be checked**, and **how strong the claim is**. It should
not silently drag along the whole instructional or support history.

### Rail 2. Human-readable handoff note

This is the compact narrative layer that helps the next human make sense of the route.

It may include:

- learner goal or intended next step;
- what has already been completed;
- why this next referral is recommended;
- time or access constraints relevant to routing;
- and a short note from the sending node, if the learner wants one.

This rail is useful because public systems are not always technically integrated, and because many
good handoffs still depend on human judgment rather than only machine parsing.

### Rail 3. Protected local support record

This rail does **not** travel by default.

It includes items such as:

- accommodation case details;
- internal advising notes not needed for the next step;
- raw chat logs;
- behavioral telemetry;
- risk scores or vendor-generated profiles;
- identity documents gathered for local compliance;
- and detailed evidence artifacts whose transfer would create needless privacy or governance risk.

The archive's current rule is that portability should move **claims and routing context**, not whole
case files.

## Four portable assertion types

The archive now treats public AI-learning assertions as belonging to four default types.

### A0 — Participation / orientation assertion

This is the lightest portable claim.

Examples:

- attended a library orientation;
- completed a public first-contact workshop;
- received guided navigation into a deeper route.

What it is for:

- routing,
- avoiding duplicate orientation,
- and preserving continuity.

What it is **not** for:

- formal exemption,
- placement,
- or academic credit.

### A1 — Foundational completion assertion

This means the learner completed a bounded foundational offer with named outcomes.

Examples:

- completed a short AI-literacy module on verification, disclosure, privacy, and ordinary study/work
  use;
- completed a public foundational sequence aligned to a local or national framework.

What it is for:

- skipping duplicate basics,
- entering the next stage faster,
- and supporting waiver of repeated introductory non-credit content where policy permits.

What it is not automatically for:

- college credit,
- high-stakes placement,
- or occupational clearance.

### A2 — Demonstrated task assertion

This means the learner did more than merely attend: they produced evidence of performance against
named criteria.

Examples:

- demonstrated AI-assisted verification and source-checking;
- completed a supervised practical task using an approved toolset;
- produced a short proof-of-learning bundle tied to a public module.

What it is for:

- challenge opportunity,
- placement conversation,
- prior-learning review,
- or selective waiver of duplicate practice.

The machine-readable rail should identify the criteria and evidence pointer, while the richer
evidence bundle can remain local until a receiving node actually needs it.

### A3 — Quality-assured credential or assessment assertion

This is the strongest portable type.

Examples:

- a credit-bearing course outcome;
- a formally quality-assured micro-credential;
- a recognised external assessment or evaluated training with published equivalency logic.

What it is for:

- serious recognition conversations,
- formal exemption,
- prior-learning credit review,
- or direct credit where an institution has an explicit policy or agreement.

The archive still rejects the idea that every A3 should auto-convert into academic credit
everywhere. The point is stronger portability and comparability, not forced equivalence.
Sector-by-sector defaults now live in
[`sector-defaults-for-public-ai-learning-recognition.md`](sector-defaults-for-public-ai-learning-recognition.md).
Narrow standing-rule exceptions and local-override logic now live in
[`standing-recognition-exception-profile-and-local-overrides.md`](standing-recognition-exception-profile-and-local-overrides.md).

## Recognition profile: what receiving nodes should do

The archive now pairs assertion types with a **recognition profile**.

### R0 — Route only

The receiving node acknowledges the prior activity but grants no formal recognition beyond
continuity of service.

Typical fit:

- A0 assertions,
- thin or non-verifiable outside claims,
- or cases where the next step is simply better routing.

### R1 — Recognition before re-intake

The receiving node skips duplicate orientation, repeated intake questions, or basic onboarding
already covered elsewhere.

Typical fit:

- A0 and A1 assertions with clear provenance.

### R2 — Waiver of duplicate basics

The receiving node waives repeated foundational non-credit content or equivalent low-stakes baseline
requirements.

Typical fit:

- stronger A1 assertions,
- some A2 assertions,
- and local bridge programmes where basic AI-literacy content is genuinely duplicative.

### R3 — Placement / challenge / prior-learning review

The receiving node treats the packet as enough to trigger a higher-value evaluation path.

Typical fit:

- A2 assertions,
- A3 assertions without standing transfer equivalency,
- or cross-sector transitions where the learning matters but local stakes remain higher.

This is often the archive's preferred middle route because it respects prior learning without
pretending that every context shares the same construct or standard.

### R4 — Direct exemption or credit under published policy

The receiving node grants formal exemption, standing credit, or equivalent recognition because a
policy, evaluation, or agreement already exists.

Typical fit:

- A3 assertions from trusted evaluated providers,
- explicit transfer or equivalency agreements,
- or prior-learning systems that publish accepted evidence and outcomes in advance.

The archive's current rule is simple: **direct credit should be policy-backed, not improvised in the
handoff itself**.

## Default cross-node mapping

The archive's default mapping is intentionally conservative.

### Library or civic first-contact to workforce/provider node

Usual default:

- A0 → R1
- A1 → R1 or R2

The main value here is continuity and non-duplication, not high-stakes academic recognition.

### Workforce system to bridge provider (community college / VET / adult education)

Usual default:

- A1 → R1 or R2
- A2 → R3
- A3 → R3 or R4 when published equivalency exists

### Bridge provider to formal institution

Usual default:

- A1 → R1 or R2
- A2 → R3
- A3 → R3 by default, R4 only where policy or agreement is already published

### Public node to employer or labour-market intermediary

Usual default:

- A1 or A2 may support routing, interviews, or shortlisting;
- A3 may support stronger recognition if the receiving party trusts the issuer and verification
  path.

The archive does not currently centre employer-side recognition, but the same rule applies: trust
should rest on verifiable claims and known policies, not on opaque vendor badges alone.

## What should never be required for routine transfer

The archive now rejects the following as routine portability requirements:

- full conversation transcripts with tutoring or chatbot systems;
- always-on provenance capture;
- behavioral dashboards or keystroke trails;
- disability or accommodation documentation unless the learner explicitly wants that routed through
  a protected channel;
- proprietary platform lock-in that prevents download, export, or third-party verification;
- and all-or-nothing demands that every recognition decision collapse into binary “credit / no
  credit.”

These practices turn public portability into either coercive disclosure or fake precision.

## Technical posture

The archive's preferred technical stack remains intentionally plain:

- use open, structured, interoperable formats where possible;
- support learner-controlled storage and presentation;
- permit signed machine-readable credentials and bundles;
- keep evidence references separable from evidence bodies;
- and allow a human-readable fallback when infrastructure is weak.

This is why the archive now prefers:

- machine-readable claims,
- human-readable notes,
- protected local evidence/support records,
- and published recognition policies.

That combination does more practical work than a giant universal record.

## Failure modes this is meant to prevent

- **binary recognition** — either everything counts as credit or nothing counts at all;
- **evidence over-transfer** — raw support or learning traces move when only a verified claim is
  needed;
- **false comparability** — weak attendance tokens are treated like strong assessed demonstrations;
- **policy opacity** — learners cannot tell in advance whether outside learning can count;
- **wallet theater** — technically portable credentials with no actual recognition consequence;
- **surveillance portability** — systems solve continuity by exporting too much private data.

## Current archive bet

The archive's current best guess is that a **small typed packet plus a recognition profile** will
outperform both loose local referral and universal credit fantasies.

The packet should therefore stay small:

- portable core claims,
- a short human handoff note,
- and protected local support/evidence records.

The recognition rule should also stay small:

- route,
- skip duplicate intake,
- waive duplicate basics,
- trigger a stronger review,
- or grant direct credit only when an explicit policy already exists.

That is now canon. The archive has since sharpened this layer with standing-list governance, a
publication profile, and a bounded exception grammar. The archive now answers that maintenance
problem with a separate privacy-light rule for appeal feedback, aggregate entry signals, and bounded
revision triggers, plus a thin public history/profile for publishing state, date, scope, reason
family, and action hint without raw counts. The next live question is narrower still: which
continuity-reserve or public-entitlement triggers, proof minima, claiming windows, and publication
fields truly travel across sectors, and when repeated `K2` / `K3` burdens should stay as predeclared
reserves rather than harden into learner-facing entitlement floors. See
[`standing-equivalency-lists-and-review-governance.md`](standing-equivalency-lists-and-review-governance.md),
[`standing-list-publication-profile-and-recency-windows.md`](standing-list-publication-profile-and-recency-windows.md),
[`standing-recognition-exception-profile-and-local-overrides.md`](standing-recognition-exception-profile-and-local-overrides.md),
[`appeal-feedback-and-standing-list-maintenance.md`](appeal-feedback-and-standing-list-maintenance.md),
[`public-maintenance-history-and-trust-signals.md`](public-maintenance-history-and-trust-signals.md),
[`no-fault-transition-cost-absorption-and-fee-waiver-rules.md`](no-fault-transition-cost-absorption-and-fee-waiver-rules.md),
`OQ-0008`, and `FT-0034`.


## Separation from standing-list publication

The packet profile should not be overloaded with institutional equivalency rules. Those belong in a
separate public publication layer with entry IDs, dates, recency windows, and manual-review routes.
Learner packets carry claims and context; standing-list feeds carry recognition defaults. See
[`standing-list-publication-profile-and-recency-windows.md`](standing-list-publication-profile-and-recency-windows.md).

## Rev0214 action-authority overlay

Public-route recognition now carries explicit action ceilings.

| Recognition use | Default AA ceiling | Harder trigger |
|---|---|---|
| explain recognition rules or next steps | `AA1` | personalized route priority or deadline effect |
| draft recognition packet or questions | `AA2` | submission to external owner without human review |
| route queue or standing-list recommendation | `AA3` | scarcity priority, fee waiver, or entitlement effect |
| credit, waiver, benefit, standing, or public-recognition decision | `AA5` only under human record owner | no unattended official effect |
| recognition denial without appeal | `AA6` | prohibited |

Learners should not bear transition cost or deadline loss caused by pilot service error.
