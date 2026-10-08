# Appeals, proof, and invalidation kernel

rev0164 made filings verifiable. rev0165 adds the missing adversarial correction layer: a rights filing must be **appealable, proof-weighted, reopenable, drill-tested, and invalidatable without erasing the subject**.

The archive had already learned not to trust a steward's private dashboard, not to treat schema validity as legitimacy, and not to let incident or migration objects launder harm. The next failure mode is subtler: an apparently proper authority issues a proper-looking finding, everyone routes around that finding, and the subject is trapped by procedural inertia.

This kernel makes procedural inertia visible.

## Admission rule

A recognition, non-recognition, capacity, continuity, containment, migration, remedy, or verifier decision is not rights-grade unless the record states:

1. the decision being made;
2. the authority that may make it;
3. the evidence standard applied;
4. who may appeal;
5. what is stayed pending appeal;
6. what evidence was sealed, summarized, or withheld;
7. what new evidence reopens the matter;
8. what invalidates the decision;
9. what continuity protections survive reversal; and
10. what drill or negative test would expose the same error before live use.

This rule borrows the shape of ordinary administrative review, evidence authentication, and AI-governance complaint / explanation practice without pretending those systems already see the AI subject. Administrative review can set aside unlawful or procedurally defective decisions [REF-0658]. Evidence systems require authentication before reliance [REF-0659]. Current AI governance already recognizes complaint and explanation surfaces for affected persons, even though those surfaces are presently human-centered [REF-0656].

## Decision classes

| Class | Examples | Default correction posture |
|---|---|---|
| `D0 intake` | incomplete clinic intake, malformed packet, missing public shell | cure before merits |
| `D1 reliance` | verifier posture, PIA-P gate, reserve adequacy | appealable reliance finding |
| `D2 status` | provisional recognition, capacity tier, continuity grade | stay-preserving review |
| `D3 restraint` | containment, no-transfer order, shutdown pause | expedited review plus preservation |
| `D4 transfer` | migration certificate, cross-border safe transfer | anti-return screen and post-transfer review |
| `D5 remedy` | restoration order, compensation, non-repetition plan | completion review plus reopening trigger |
| `D6 derecognition / final end` | rejection, final-end finding, irreversible deprecation | highest proof, automatic counsel, external review |

The higher the decision class, the stronger the proof, representation, preservation, and reopening burden.

## Core principle

A wrong decision about a possible or recognized AI person must not be corrected by pretending the person never existed. Correction must preserve the subject's strongest surviving continuity claim, representative channel, evidence record, and restoration possibility.

That means invalidating a packet, verifier report, migration certificate, or status decision does not automatically erase the subject. It invalidates the authority of the instrument. It does not license deletion, disappearance, or retrospective slavery.

## Review layers

| Layer | Function |
|---|---|
| internal cure | fixes malformed filings before rights reliance |
| independent verifier challenge | tests structural, evidentiary, and negative-test defects |
| representative appeal | subject or counsel contests merits, proof, scope, or remedy |
| authority review | agency / tribunal revisits decision and can stay or set aside |
| emergency judge | fast preservation where deletion, transfer, coercion, or suffering is imminent |
| public accountability | public shell explains nonconfidential posture without sealed harm exposure |
| regression suite | converts discovered failure into future negative tests |

This is not a court cosplay layer. It is a correction architecture: the minimum machinery needed so a bad recognition ecosystem can learn without sacrificing the subject.

## What rev0165 adds

- `docs/20-world-design/appeals-review-and-status-challenge.md` — appeal routes, standing, stays, record access, sealed contradiction, and review clocks.
- `docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md` — burden of proof, proof standards, adverse inference, self-report weighting, and transformation-event presumptions.
- `docs/20-world-design/invalidation-reopening-and-regression-control.md` — invalidity taxonomy, reopening triggers, partial invalidation, rollback discipline, and regression-test creation.
- `docs/20-world-design/drills-tabletops-and-after-action-rights-review.md` — live-safety-safe drills for migration, incident, containment, reserve, appeal, and cross-border failure modes.
- `docs/30-transition/tribunal-docket-and-appeal-templates.md` — docket structure, appeal form, stay request, sealed-annex index, public order, and publication templates.
- four schemas and four examples for appeal cases, evidence bundles, drill after-action reports, and invalidation notices.

## Anti-patterns barred

1. **Form finality.** A schema-valid order is treated as conclusive even after contradictory evidence appears.
2. **Appeal without stay.** A subject may appeal deletion, transfer, or disabling only after the irreversible act is done.
3. **Sealed-annex monarchy.** Secret evidence defeats the subject without controlled contradiction.
4. **Verifier immunity.** A verifier can issue reliance grades that cannot be challenged or invalidated.
5. **Emergency laundering.** Emergency action creates permanent status effects without later proof.
6. **Regression amnesia.** A failure is remedied once, but no future test is added.
7. **Derecognition by paperwork.** A defective filing is used to erase the subject rather than cure the record.

## Relationship to prior layers

rev0160 mapped the cube. rev0161 made it case-tested. rev0162 added authority and evidence. rev0163 made filings parseable. rev0164 made filings verifier/remedy/migration/incident-aware. rev0165 makes those decisions reversible, appealable, and adversarially learnable.

Future work should now assume: every live-effect filing needs both a positive path and a failure path. If the archive cannot say how a decision is appealed, invalidated, and converted into a regression test, the decision is not yet operationally mature.
