# Portable republication and recurrence defaults for promoted packet maintenance envelopes

This document closes the archive's next packet-governance gap: **once a pre-declared packet
maintenance envelope already travels as a promoted basket, may even carry a shared numeric band, and
may even carry a shared checkpoint / breach package, do the rules for starting a fresh cycle travel
too, or should renewal handling stay local?**

The archive's answer is narrower again:

> only maintenance classes whose **fresh-cycle notice** and **re-entry conditions** remain truthful
across the reuse scope should carry one shared republication / recurrence package. In the starter
canon, `PME-LABEL` may usually carry both, `PME-CALENDAR` for `AF-RECORD` may usually carry only the
shared republication floor while keeping recurrence admission local, and route or safety calendars
still keep both local.

The point is to avoid three opposite errors at once:

- **cycle laundering** — a service uses one promoted basket, one small numeric band, and one
  checkpoint package to imply that repeated cycles are already governed too, even though the real
  conditions for beginning another cycle still vary materially by owner or regime;
- **silent rollover** — a service lets a maintenance episode blur into a second one without a new
  public notice, making old trust evidence do work it no longer deserves;
- **permanent under-hardening** — a promoted envelope whose fresh-cycle notice and re-entry
  conditions really are stable enough to travel never earns one reusable renewal package and
  therefore keeps relitigating the same tiny recurrence rule locally.

Current public signals support this thinner move. OECD's 2026 outlook keeps pressing educational AI
toward pedagogically purposeful design rather than convenience-first task completion; OpenAI's
current learning-outcomes work emphasizes longitudinal measurement instead of one-off performance
snapshots; UNESCO's 2026 competency frameworks keep human agency and AI pedagogy central; and ICO
guidance keeps challengeable design, privacy by default, and child-focused limits in view. See
`B11`, `B23`, `B143`, `B146`, `B149`, `B150`, `B151`.

## Relationship to the existing packet-governance canon

This document does not replace
[`portable-defaults-for-predeclared-packet-maintenance-envelopes.md`](portable-defaults-for-predeclared-packet-maintenance-envelopes.md),
[`portable-quantitative-bands-for-promoted-packet-maintenance-envelopes.md`](portable-quantitative-bands-for-promoted-packet-maintenance-envelopes.md),
[`portable-checkpoint-and-breach-defaults-for-promoted-packet-maintenance-envelopes.md`](portable-checkpoint-and-breach-defaults-for-promoted-packet-maintenance-envelopes.md),
or
[`publication-of-local-departures-from-owner-facing-recovery-packet-defaults.md`](publication-of-local-departures-from-owner-facing-recovery-packet-defaults.md).

Those surfaces already answer:

- when recurring same-basket upkeep may use a pre-declared maintenance envelope at all;
- which baskets may travel as `PMT-BRANCH`, `PMT-FAMILY`, or `PMT-LOCAL`;
- which promoted baskets, if any, may also carry a shared numeric cap/window band;
- which promoted baskets, if any, may also carry a shared checkpoint / breach package.

This document answers one narrower question:

- **which promoted portable maintenance envelopes, if any, can also carry one shared republication /
  recurrence package across repeated cycles?**

## Three republication / recurrence portability tiers

The archive now distinguishes three republication / recurrence portability tiers.

| Tier | Meaning | What travels | What stays local |
|---|---|---|---|
| `RRP-BOTH` | the promoted envelope carries one shared fresh-cycle republication floor and one shared recurrence-admission rule | the minimum fields for the next-cycle notice and the minimum conditions for beginning another cycle | any stricter local cycle ceiling, extra local reviewer, and local explanatory language |
| `RRP-REPUB` | the promoted envelope carries only one shared republication floor | the fact that each fresh cycle needs a new notice with a prior-cycle closure marker | the actual local rule for when another cycle may begin |
| `RRP-LOCAL` | the promoted envelope carries no shared renewal package | only the basket and any previously earned portability / numeric / checkpoint tiers | both the fresh-cycle notice structure and the local recurrence-admission rule |

The archive is deliberately asymmetric again:

> recurrence portability is harder to earn than checkpoint portability. A basket can travel, a cap
can travel, and even a checkpoint or breach package can partly travel while the truthful conditions
for beginning another cycle still do not.

## Five tests for whether republication / recurrence duties really travel

A promoted portable maintenance envelope may harden above `RRP-LOCAL` only when all five tests hold.

1. **same-cycle-object test** — comparable sites or owners are genuinely beginning the same kind of
   fresh maintenance cycle, rather than one site starting a bounded wording cleanup while another is
   effectively reopening a different review or record path.
2. **same-fresh-notice test** — the new-cycle notice can be described in one reusable way without
   concealing owner-, office-, or regime-specific truths about what is restarting and what prior
   trust has already expired.
3. **same-reentry-conditions test** — the minimum facts that must be true before another cycle
   begins are materially the same across the proposed reuse scope.
4. **no-expiry-blur test** — the shared package does not make an ended cycle look still current,
   still trusted, or still challenge-complete once its checkpoint window has closed.
5. **no-cycle-chaining-disguise test** — the shared package does not make it easier to treat rolling
   redesign, repeated extension, or slow unresolved drift as though it were still one bounded
   maintenance episode.

Failing the second test keeps the envelope at `RRP-LOCAL` unless the archive can still honestly say
that every new cycle requires the same small republication floor. Failing only the third while the
fresh-cycle notice still travels usually points to `RRP-REPUB`: the new notice floor may travel
while the real conditions for another cycle stay local.

## The starter republication / recurrence packages

The archive now names one shared republication floor and one shared recurrence-admission rule.

| Code | Meaning |
|---|---|
| `RN-FRESH-CYCLE` | a fresh-cycle notice that republishes the promoted basket, applicable portability / numeric / checkpoint tiers, the prior-cycle closure marker, the new cycle start and end window, and any remaining local residue before edits restart |
| `RG-PASS-THEN-REOPEN` | a recurrence gate that allows another cycle only after the prior cycle has closed, the required checkpoint has been performed or truthfully localized, and no unresolved breach remains open |

The archive does **not** yet create a larger renewal library. The starter canon is deliberately
small:

- no promoted portable maintenance envelope currently carries more than one shared republication
  floor;
- no promoted portable maintenance envelope currently carries a shared recurrence gate that permits
  silent rollover, auto-extension, or indefinite chaining;
- where the archive refuses a shared republication or recurrence package, services must still
  publish a **local** fresh-cycle notice and local recurrence-admission rule rather than hiding
  behind a portable basket or checkpoint package alone.

## The archive's starter republication / recurrence answers

### `PME-LABEL` usually hardens as `RRP-BOTH`

`PME-LABEL` may usually carry **both** a shared fresh-cycle republication floor and a shared
recurrence-admission rule across its promoted branch scope.

Why the archive allows this:

- label/plain-language upkeep usually preserves the same cycle object: the service is beginning
  another bounded wording-cleanup burst rather than reopening a different owner path;
- the fresh-cycle notice can usually be described the same way across the branch scope without
  concealing who owns the packet or what trust has already expired;
- the same small re-entry conditions are usually truthful too: close the prior cycle, perform the
  promised checkpoint, resolve or publish any breach, then reopen only with a new notice.

The starter default is therefore:

> when `PME-LABEL` has already earned `PMT-BRANCH`, `PQT-BOTH`, and `PCP-BOTH`, it may usually also
inherit `RRP-BOTH` with `RN-FRESH-CYCLE + RG-PASS-THEN-REOPEN`.

What `RN-FRESH-CYCLE` must minimally republish:

1. the promoted basket and branch scope still in force;
2. the prior-cycle closure marker or reference;
3. the new `QC-3 + QW-14D` band or any stricter local band;
4. the checkpoint / breach package still governing the new cycle;
5. any residue that still remains local.

What `RG-PASS-THEN-REOPEN` means in this branch-starter use:

- **no silent carry-forward** — a second wording-cleanup burst may not begin under the prior notice
  after the first cycle has closed;
- **checkpoint-first reopening** — the prior `CK-LABEL-SHELL` check must have been completed and any
  `BR-PME-CORE` breach must have been cleared or locally re-published;
- **fresh timestamp truth** — the new cycle must state a new start / close window rather than
  implying continuing live coverage from the earlier cycle.

### `PME-CALENDAR` for `AF-RECORD` usually hardens only as `RRP-REPUB`

Record-owner calendar housekeeping may usually carry one shared **fresh-cycle republication floor**,
but not one shared recurrence-admission rule.

Why the archive stops there:

- the same minimum truth usually does travel: once another calendar-cleanup burst begins, the
  service should republish a new notice rather than implying the prior cycle is still live;
- but the actual conditions for beginning another cycle are still too dependent on local term
  boundaries, transcript refresh cadence, award-cycle practice, or exam-board staging to claim one
  shared recurrence gate honestly.

The starter default is therefore:

> when `PME-CALENDAR` for `AF-RECORD` has already earned `PMT-FAMILY`, `PQT-CAP`, and `PCP-BREACH`,
it may usually inherit `RRP-REPUB` with `RN-FRESH-CYCLE`, while the real recurrence-admission rule
must still be published against the local record calendar.

What stays local even here:

- the condition that makes another calendar cycle appropriate at all;
- the exact office or board event that authorizes reopening;
- any stronger local rule that blocks repetition near freeze windows, award cutoffs, or transcript
  issue points.

### `PME-CALENDAR` for `AF-ROUTE` stays `RRP-LOCAL`

Route-owner calendar housekeeping keeps **both** the fresh-cycle notice structure and the
recurrence-admission rule local in the starter canon.

Why it does not yet carry a shared package:

- route systems often combine callback cadence, intake order, partner inventory, and queue truth in
  ways that make even the “fresh cycle” story more owner-specific than the basket name suggests;
- the same nominal reopening can materially change when the learner gets a real response, who
  answers first, or whether the challenge path is still functionally visible.

### `PME-CALENDAR` for `AF-SAFETY` stays `RRP-LOCAL`

Safety-owner calendar handling remains fully local for the same reason it remained non-portable at
the basket, numeric, and checkpoint layers: protective review timing and recurrence truth are too
tightly coupled to incident shape, duty stage, and safeguarding regime to claim one shared
fresh-cycle or recurrence rule yet.

## What portable republication / recurrence packages still may not do

Even under `RRP-BOTH` or `RRP-REPUB`, a promoted envelope may not:

1. weaken a shell invariant, challenge path, or truthful expiry statement;
2. make an ended cycle look still current after the earlier window has closed;
3. treat a failed or unresolved checkpoint as compatible with ordinary reopening;
4. hide rolling redesign, route reshaping, or owner-boundary drift inside a supposedly shared
   renewal package;
5. imply one cross-site cycle ceiling, fatigue rule, or long-run trust story that the archive has
   not yet actually hardened.

Republication / recurrence portability is therefore subordinate to shell truth. The cycle package
travels only while the service can still tell the truth about when one episode ended and why another
may begin.

## What services must still publish locally

Even under `RRP-BOTH` or `RRP-REPUB`, a service must still publish:

- the promoted basket and portability tier (`PMT-*`);
- any shared numeric tier (`PQT-*`) and the actual local cap/window when the numbers do not fully
  travel;
- any shared checkpoint tier (`PCP-*`) and the exact local checkpoint anchor when the package does
  not supply it;
- any stricter local recurrence ceiling, freeze window, or re-entry reviewer.

## Starter matrix

| Envelope | Portability tier | Quantitative tier | Checkpoint tier | Renewal tier | Starter package | Why |
|---|---|---|---|---|---|---|
| `PME-LABEL` | `PMT-BRANCH` | `PQT-BOTH` | `PCP-BOTH` | `RRP-BOTH` | `RN-FRESH-CYCLE + RG-PASS-THEN-REOPEN` | fresh-cycle notice and re-entry conditions usually travel with the branch scope |
| `PME-CALENDAR` for `AF-RECORD` | `PMT-FAMILY` | `PQT-CAP` | `PCP-BREACH` | `RRP-REPUB` | `RN-FRESH-CYCLE`; recurrence gate local | fresh notice truth often travels better than renewal admission |
| `PME-CALENDAR` for `AF-ROUTE` | `PMT-FAMILY` | `PQT-LOCAL` | `PCP-LOCAL` | `RRP-LOCAL` | local cycle notice + local recurrence rule | callback / queue semantics still vary too much |
| `PME-CALENDAR` for `AF-SAFETY` | `PMT-LOCAL` | `PQT-LOCAL` | `PCP-LOCAL` | `RRP-LOCAL` | local cycle notice + local recurrence rule | protective timing remains regime-bound |

## Why this move belongs in an education-with-AI archive

This is a tiny packet-governance refinement, but it matters because the archive's core claim is not
merely that educational AI should be safe in principle. It is that **rights shells, recovery paths,
and bounded upkeep stories should stay truthful under ordinary operational recurrence**. Once
institutions run official study companions, access-routing services, or owner-facing recovery paths
at scale, some shell upkeep will recur. The archive therefore needs an honest answer not only about
when maintenance can be batched and how it is checked, but about whether the story for **starting
the next cycle** itself really travels.

That answer is now narrower and clearer: branch-level label cleanup may usually share both the
fresh-cycle notice and the pass-then-reopen gate; record-owner calendar upkeep may usually share
only the fresh-cycle notice; route and safety calendar handling must still govern cycle truth
locally.

## Status

This document is **adopted canon** for the archive's packet-maintenance line.

It closes `FT-0067` and sharpens `OQ-0037`.

The next narrower question is which promoted portable maintenance envelopes, if any, can safely
carry one shared **cumulative-cycle ceiling or fatigue rule** across repeated cycles, and which
should keep long-run accumulation and de-promotion handling local even when republication or
recurrence duties now travel. See `OQ-0038`.
