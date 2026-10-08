---
status: active_bridge
claim_kind: program_rule
route_role: case_work_core
canonical_anchor: false
route_refs:
- case_work_core
supersedes: null
depends_on: []
source_refresh_due: '2026-12-31'
case_pressure: rev0304_portfolio_calibration
---

# Comparison-set selection and non-comparability

## What this note is for

The archive now has a compact rule for comparing several live or exemplar case memos on the same operator spine.
What it still lacked was the thinner upstream bridge:
**which cases belong in the same comparison set at all, and when should the archive refuse a neat comparison because the cases are not commensurable enough yet?**

That gap matters because a tight archive can go wrong in two opposite ways:
- it can compare cases that do not yet share enough memo freshness, claim level, or evidentiary footing to support a useful pattern call,
- or it can refuse all comparison so aggressively that obviously recurring failures never get named as recurring failures.[S04][S05][S06][S15][S20][S23][S31][S32][S33]

This note gives the archive a small rule for choosing a comparison set and for saying **not comparable enough yet** without embarrassment.
It is not a new dashboard note and not a new doctrine note.
It is a **comparison-entry discipline**.

Use this note with:
- [`case-work-decision-path.md`](case-work-decision-path.md)
- [`case-application-protocol.md`](case-application-protocol.md)
- [`case-staleness-and-recertification.md`](case-staleness-and-recertification.md)
- [`confidence-labels-and-action-under-proof-debt.md`](confidence-labels-and-action-under-proof-debt.md)
- [`cross-case-comparison-and-pattern-extraction.md`](cross-case-comparison-and-pattern-extraction.md)
- [`case-portfolio-triage-and-memo-selection.md`](case-portfolio-triage-and-memo-selection.md)

## Minimum rule

A cross-case pass should start only after the archive can name a **shared comparison question**.
Usually that question should be one of these:

1. **Are these cases failing in the same dominant way?**
2. **Are nominal gains being erased by the same washout channel?**
3. **Do these cases split into different governing modes?**
4. **Does the same package family keep failing or succeeding for the same reason?**
5. **Is one live doctrine note under repeated pressure from several cases?**

If the archive cannot phrase the comparison question that tightly, it usually does not need a retained comparison set yet.
It usually needs:
- a better single-case memo,
- a narrower portfolio choice,
- or a doctrine question routed elsewhere.

## What should usually count as the same comparison set

Cases belong in the same working set when they are similar enough on the archive's upstream burdens that one comparison can still say something real.
Ordinarily that means enough overlap on five things.

### 1. Freshness burden

The cases should be comparably live.
A fresh memo can sometimes be compared to a slightly older but still live memo.
It should rarely be compared to a stale memo that survives only as verdict residue or partial salvage.
Use [`case-staleness-and-recertification.md`](case-staleness-and-recertification.md) first.

### 2. Claim level

The cases should be compared at the same level of claim.
Examples of valid like-with-like comparison:
- verdict to verdict,
- washout to washout,
- package to package,
- watch posture to watch posture.

Examples that usually fail:
- one case's verdict against another case's package,
- one case's confidence posture against another case's package design,
- one case's rail fit against another case's moral target.

### 3. Evidence burden

The cases should not differ so radically in proof quality that the comparison mostly tracks who has the cleaner dataset.
A case with strong verdict confidence and thin package confidence can still belong in a set, but only if the comparison question stays at the verdict or mechanism level.
It should not be forced into a package league table it has not earned.

### 4. Operator spine compatibility

The cases should be expressible on the same small operator spine:
- verdict,
- dominant breach,
- fastest washout,
- mode,
- opening package,
- confidence posture,
- watch posture,
- next scoreboard / main evidence debt.

If one candidate case can only be compared through a large bespoke metric universe, it probably does not belong in the same retained set yet.

### 5. Comparison job

The set should be assembled for one job at a time:
- **portfolio choice**,
- **pattern extraction**,
- or **doctrine pressure**.

If the group of cases is trying to do all three at once, the archive should usually split the set or route the outputs separately.[S15][S18][S19][S20][S21][S22][S23][S31][S32][S33]

## When cases are comparable enough

Treat a set as comparable enough when all of the following are true:
- the shared question fits in one sentence,
- the cases are live enough for the same level of claim,
- the comparison can stay on the archive's operator spine,
- the intended output is one of the archive's allowed comparison jobs,
- and the cases are not being included mainly because they are vivid, famous, or politically resonant.

That is usually enough.
The archive does **not** need perfect symmetry before it can compare two or three cases usefully.
It needs a comparison that is honest about what the cases can and cannot bear.

## When a case should stay out of the comparison set

Exclude or postpone a candidate case when one of these conditions dominates.

### 1. The memo is too stale for the intended claim

Do not compare a partly salvageable memo to a fresh memo at the package or watch-posture level.
Either recertify the older memo or narrow the comparison question.

### 2. The case is only there because it is vivid

A famous or rhetorically convenient case is not automatically part of the best comparison set.
If it does not help answer the shared comparison question, leave it out.

### 3. The comparison would mostly track data architecture

If the cases differ so much in legibility, capture, or undercount that the result would mainly be a comparison of measurement systems, the archive should say so directly.
That may still matter, but it is a source-order or evidence-gap question first.

### 4. The comparison would collapse distinct governing modes

If one case is fundamentally about weak floors and another is mainly about wealth-to-rule conversion under already-thick private holdings, the archive should not force them into one flat ranking just because both involve inequality.
They may still belong in the same portfolio, but not necessarily the same comparison set.

### 5. The set would quietly redefine doctrine by breadth alone

Do not put cases together merely to create an aura of generality.
If the real job is doctrine pressure or doctrine revision, name that job and route it accordingly rather than letting breadth do the argumentative work.[S18][S19][S20][S21][S22][S23][S31][S32][S33]

## The archive's safe comparison-set sizes

A tight archive should usually prefer very small sets.
Ordinarily:
- **2 cases** is enough to test whether a supposed common mechanism is even plausible,
- **3 cases** is enough to see whether a pattern survives first contrast,
- **4 or more cases** should be rare and usually justified only when the output stays extremely thin.

If a comparison wants to keep expanding beyond that, the archive usually does not need a bigger retained set.
It usually needs either:
- one portfolio note,
- one doctrine-repair question,
- or a temporary scratch comparison that is not kept as a live archive note.

## What to output before the real comparison starts

Before writing a retained cross-case pass, a future revision should normally state only these four lines:

1. **comparison question**
2. **cases included**
3. **cases excluded or postponed and why**
4. **comparison level** — verdict / mechanism / package / watch posture / doctrine pressure

If those lines cannot be written cleanly, the archive should usually stop there.
That is not a failure.
That is the archive avoiding fake commensurability.

## The three false moves this note is meant to stop

### 1. Fake like-with-like comparison

Two cases can both matter morally and still be wrong to compare directly at the same level.
This note is meant to make that sentence easy to say.

### 2. Comparison-set inflation

Once several candidate cases are on the table, it is tempting to keep adding more cases for rhetorical safety.
Usually that lowers the archive's signal instead of raising it.

### 3. Treating non-comparability as defeat

Sometimes the correct archive move is:
**same broad problem, not the same retained comparison set yet.**
That is a useful conclusion because it prevents a shadow dashboard built from mismatched burdens.

## Fast use rule

When several cases are on the table:

1. **State the shared comparison question in one sentence.**
2. **Exclude stale or claim-level-mismatched cases before comparing.**
3. **Keep the set small enough to stay on the same operator spine.**
4. **Say plainly when a case is excluded because it is not comparable enough yet.**
5. **Only then route the surviving set into** [`cross-case-comparison-and-pattern-extraction.md`](cross-case-comparison-and-pattern-extraction.md).

## Bottom line

The archive now has a compact answer to a question that comes **before** multi-case comparison:
**which cases should actually be compared together, and when should the archive refuse a neat comparison because the burden is not shared enough yet?**
Choose a small set around one shared question, exclude cases that cannot honestly bear the same level of claim, and treat **not comparable enough yet** as a disciplined archive output rather than a weakness.
