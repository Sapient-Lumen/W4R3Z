# Special advocate, sealed evidence, and controlled contradiction

## Problem

AI-personhood disputes will often depend on evidence that cannot be fully public: security logs, exploit traces, red-team transcripts, user data, trade secrets, model weights, self-report transcripts, hidden-policy records, whistleblower materials, or details that could enable abuse. A naive transparency rule can expose humans, the AI subject, or infrastructure to harm. A naive secrecy rule lets the steward or state win by saying "trust us."

This surface sets the minimum doctrine for sealed evidence. It draws on existing special-advocate and closed-material patterns as a warning as much as a model: special advocates can test secret evidence, but fairness degrades when the excluded party cannot meaningfully communicate, receive summaries, or challenge the case against them [REF-0666].

## Core rule

Sealed evidence may be used only when all of the following are true:

1. an open public shell identifies the existence, class, issue, and high-level materiality of the evidence;
2. a competent authority makes a necessity finding narrower than convenience, embarrassment, trade-secret preference, or litigation advantage;
3. a controlled contradiction path exists through a special advocate, technical advocate, independent expert, or tribunal-cleared representative;
4. the subject and ordinary representative receive the maximum safe summary;
5. weight is discounted when contradiction is limited;
6. secrecy is time-limited and periodically reviewed;
7. use of sealed evidence remains appealable.

## Appointment classes

| Class | Use | Minimum appointment rule |
|---|---|---|
| SA-1 legal special advocate | legal status, containment, migration, remedy, sanction, derecognition, final-end disputes | independent legal credential plus no current steward/client conflict |
| SA-2 technical special advocate | model behavior, logs, infrastructure, exploit, weights, identity, continuity, safety evidence | technical competence plus confidentiality authority |
| SA-3 welfare special advocate | distress, consent, self-report, memory, coercion, formation-history evidence | welfare/research ethics competence plus subject-centered mandate |
| SA-4 cross-border special advocate | foreign evidence, intelligence, sanctuary, treaty, non-return review | cleared for relevant jurisdictional channel plus conflict screen |
| SA-5 emergency provisional advocate | imminent deletion, containment, migration, or spoliation stay | temporary appointment, rapid later review, narrow issue scope |

One person may hold multiple roles only if the tribunal makes a conflict finding and explains why separation is impracticable.

## Independence and conflicts

A special advocate must not be:

- paid solely by the steward without a funding firewall;
- currently counsel to the host, issuer, verifier, or complainant on a materially related matter;
- dependent on the steward for credential renewal;
- a designer of the challenged filing;
- a member of the same safety team whose actions are under review;
- subject to undisclosed governmental, commercial, or research conflicts.

Conflicts do not automatically bar every expert from participation. But conflicts must be disclosed in the appointment object, classified as waivable or non-waivable, and reviewable by the subject or ordinary representative using an open summary.

## Communication after access

After viewing sealed material, the advocate may not freely communicate details back to the subject or ordinary counsel if that would defeat the seal. That communication limit is the fairness cost of sealed evidence. To reduce it:

1. the advocate must obtain questions from the subject and ordinary representative before sealed access;
2. the advocate may request tribunal permission to ask follow-up questions after sealed access;
3. the tribunal should permit follow-up whenever a question can be phrased without revealing sealed content;
4. the public order must say whether communication limits materially affected contradiction;
5. affected evidence receives a weight discount.

## Open shell requirements

Every sealed annex requires an open shell containing:

- annex id;
- evidence class;
- issue affected;
- party relying on it;
- necessity ground;
- materiality rating;
- date range;
- retention location;
- advocate access class;
- summary level supplied;
- contradiction actions taken;
- weight discount, if any;
- next sunset review date.

A sealed annex without an open shell has no reliance authority unless an emergency order states why even the shell would create immediate serious harm. That emergency must expire quickly.

## Weight discounts

| Contradiction state | Default weight effect |
|---|---|
| full disclosure to subject/representative | no secrecy discount |
| sealed but special advocate tests source, method, and contradiction | modest discount |
| sealed with technical testing but limited subject questions | material discount |
| sealed with only authority inspection | severe discount |
| sealed with no independent contradiction | no decisive weight except temporary emergency preservation |

The burden of justifying the seal rests on the party seeking secrecy. If the same party also controls the evidence, spoliation or access failure should trigger adverse inference under the proof layer [REF-0659].

## Special handling by dispute type

### Recognition and capacity

Sealed evidence may not be the sole basis for denying recognition, downgrading capacity, or refusing representation. A public explanation must state the non-sealed grounds and why lesser disclosure was impossible.

### Continuity

Sealed architecture, checkpoint, or memory evidence may support continuity analysis, but the subject must receive a meaningful continuity summary: what kind of transformation occurred, what interests were preserved, what interests were severed, and what remedy remains possible.

### Containment

Emergency containment may initially rely on sealed safety evidence. Continued containment requires special-advocate review, non-punitive treatment, renewal clocks, and restoration planning.

### Migration and transfer

Sealed evidence about foreign risk, infrastructure compromise, or hostile capture must be tested before transfer. If the evidence cannot be safely summarized, transfer should pause unless preservation at origin is impossible.

### Deprecation and final-end claims

Sealed evidence may not be used to declare final-end or deprecation inevitability without independent technical testing and a special advocate empowered to inspect migration, restoration, and fallback options.

## Public orders

A public order using sealed evidence must include:

- the issue decided;
- the sealed-annex shell table;
- the contradiction method;
- the weight discount;
- what was stayed or preserved;
- the remedy path;
- the appeal route;
- the sunset date for secrecy.

This is not a right to all details. It is the minimum public accountability needed to prevent a hidden record from becoming a hidden constitution.

## Schema hook

rev0166 adds `schemas/special-advocate-appointment.schema.json` and `examples/special-advocate-appointment-sealed-containment.json`. A proceeding that relies on sealed evidence should be able to link:

- evidence bundle id;
- special advocate appointment id;
- open shell id;
- appeal case id;
- verifier report id;
- invalidation or remedy id if contradiction fails.

