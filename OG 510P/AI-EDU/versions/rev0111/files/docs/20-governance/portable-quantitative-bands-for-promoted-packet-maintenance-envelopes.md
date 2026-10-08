# Portable quantitative bands for promoted packet maintenance envelopes

This document closes the archive's next packet-governance gap: **once a pre-declared packet maintenance envelope already travels as a branch- or authority-family default, do its numeric limits travel too, or should the basket name travel while the cap/window numbers stay local?**

The archive's answer is deliberately narrower than its already narrow portability rule:

> only the maintenance classes whose *editing density* remains truthful across the reuse scope should carry shared numeric bands. In the starter canon, `PME-LABEL` may usually carry one shared cap/window pair, `PME-CALENDAR` for `AF-RECORD` may usually carry only a shared cap while keeping the window local to the review calendar, and route or safety calendars still keep both numbers local.

The point is to avoid three opposite errors at once:

- **quantitative laundering** — a service uses one small portable basket name to smuggle in a longer or denser change programme than the inherited shell truth can honestly support;
- **false precision** — the archive publishes one universal window for calendar upkeep even when checkpoint density, callback cadence, or live review timing vary too much across the reuse scope;
- **permanent under-specification** — a basket whose editing density really is stable enough to travel never gets a shared band and therefore keeps re-litigating the same tiny limit locally.

Current public signals support this thinner move. OECD's 2026 outlook keeps pressing educational AI toward pedagogically purposeful design rather than convenience-first task completion; RAND's March 2026 survey shows student AI use rising alongside concern about harm to critical thinking; OpenAI's current learning-outcomes work emphasizes longitudinal measurement rather than one-off performance snapshots; and ICO guidance keeps simple challenge routes, privacy-by-default, and child-facing design limits in view. See `B11`, `B143`, `B146`, `B149`, `B150`, `B151`.

## Relationship to the existing packet-governance canon

This document does not replace [`portable-defaults-for-predeclared-packet-maintenance-envelopes.md`](portable-defaults-for-predeclared-packet-maintenance-envelopes.md) or [`publication-of-local-departures-from-owner-facing-recovery-packet-defaults.md`](publication-of-local-departures-from-owner-facing-recovery-packet-defaults.md).

Those surfaces already answer:

- when recurring same-basket upkeep may use a pre-declared maintenance envelope at all;
- which baskets may travel as `PMT-BRANCH`, `PMT-FAMILY`, or `PMT-LOCAL`;
- the shell invariants, breach triggers, and named checkpoint discipline that keep batching honest.

This document answers one narrower question:

- **which promoted portable envelope defaults, if any, can also carry one shared numeric edit-cap and maintenance-window band across their reuse scope?**

## Three quantitative portability tiers

The archive now distinguishes three quantitative portability tiers.

| Tier | Meaning | What travels | What stays local |
|---|---|---|---|
| `PQT-BOTH` | the promoted envelope carries one shared edit-cap band and one shared maintenance-window band | the basket name, the max covered edits, and the max window length | any stricter local floor, cadence notes, and branch-specific explanatory language |
| `PQT-CAP` | the promoted envelope carries only one shared edit-cap band | the basket name and the max covered edits | the window length, because real checkpoint density still varies too much |
| `PQT-LOCAL` | the promoted envelope carries no shared numeric band | only the basket name / portability tier from the prior document | both the edit cap and the window length |

The archive is intentionally asymmetric here:

> numeric portability is harder to earn than basket portability. The same topic can travel while the truthful density of edits still does not.

## Five tests for whether numeric limits truly travel

A promoted portable maintenance envelope may harden above `PQT-LOCAL` only when all five tests hold.

1. **same-density test** — comparable sites or owners usually make the same number of truthful covered edits before the named post-window checkpoint.
2. **same-cadence test** — the real review/checkpoint rhythm is similar enough that one shared maximum window does not hide later first meaningful review in some reuse cases.
3. **no-latency-loss test** — the shared band does not make learner visibility, challengeability, or expiry clarity arrive later in practice on any ordinary reuse case.
4. **no-hidden-redesign test** — the proposed shared cap/window pair does not create enough room for ordering, wording, route, or anchor edits to become rolling redesign under a portable label.
5. **cross-regime truth test** — the same cap/window pair remains truthful across the proposed scope without leaning on one office's local term calendar, callback cadence, safeguarding stage, or dispatch practice.

Failing the first, third, or fifth test keeps the envelope at `PQT-LOCAL`. Failing only the second usually points to `PQT-CAP`: the basket and cap may travel while the window still stays local.

## The starter quantitative bands

The archive now names only two starter numeric bands.

| Code | Meaning |
|---|---|
| `QC-3` | no more than **3 covered edits** before the named post-window checkpoint |
| `QW-14D` | no more than **14 calendar days** between envelope publication and the named post-window checkpoint |

The archive does **not** yet create a richer ladder. The starter canon is deliberately small:

- no promoted portable envelope may currently carry a shared cap above `QC-3`;
- no promoted portable envelope may currently carry a shared window above `QW-14D`;
- where the archive refuses one shared band, services must still publish a local number rather than hiding behind a portable basket name alone.

## The archive's starter quantitative answers

### `PME-LABEL` usually hardens as `PQT-BOTH` with `QC-3 + QW-14D`

`PME-LABEL` may usually carry **both** a shared edit-cap band and a shared maintenance-window band across its branch scope.

Why the archive allows this:

- label/plain-language harmonisation usually changes wording, ordering, glosses, or display labels rather than changing packet power;
- those edits tend to cluster tightly in one clean-up burst rather than unfolding across long checkpoint calendars;
- the same branch-level shell invariants usually keep the same challenge route, same review anchor, and same expiry truth visible across the reuse set.

The starter default is therefore:

> when `PME-LABEL` has already earned `PMT-BRANCH`, it may usually also inherit `PQT-BOTH` with `QC-3 + QW-14D`.

What still collapses the shared band immediately:

- any edit that changes field-inclusion logic, family-conditioned scope, review anchor, expiry truth, or challenge-route prominence;
- any fourth covered edit before the named checkpoint;
- any attempt to roll the same shared band across a second window without republication.

### `PME-CALENDAR` for `AF-RECORD` usually hardens only as `PQT-CAP`

Record-owner calendar housekeeping may usually carry one shared **cap**, but not one shared **window**.

Why the archive stops there:

- record-owner checkpoint density often varies by term structure, exam-board calendar, progression cycle, or transcript-refresh rhythm even when the same family owns the path;
- the number of truthful covered edits before the next checkpoint is often stable enough to travel, but the length of the pre-checkpoint housekeeping window is not;
- one shared cross-site window would too easily conceal a later first meaningful review in quarter, trimester, modular, or rolling-completion settings.

The starter default is therefore:

> when `PME-CALENDAR` for `AF-RECORD` has already earned `PMT-FAMILY`, it may usually inherit `PQT-CAP` with a shared **`QC-2`** cap, while the maintenance window must still be published locally against the real record-review cadence.

Why `QC-2` rather than `QC-3`:

- calendar edits change timing semantics more directly than label cleanup does;
- a lower cap leaves less room for silent drift in carry-forward, expiry wording, or checkpoint ordering;
- the archive wants the record-owner calendar family to remain honest about how quickly calendar housekeeping can become substantive path redesign.

### `PME-CALENDAR` for `AF-ROUTE` stays `PQT-LOCAL`

Route-owner calendar housekeeping keeps **both** numbers local in the starter canon.

Why it does not yet carry a shared band:

- queue and callback cadence vary too much across dispatch, intake, referral, and partner-inventory systems;
- the same nominal calendar basket can conceal materially different waiting, recontact, or partner-availability realities;
- even a truthful portable basket name does not yet imply one shared density pattern for edits or one safe cross-site maximum window.

### `PME-CALENDAR` for `AF-SAFETY` stays `PQT-LOCAL`

Safety-owner calendar handling remains fully local for the same reason it remained non-portable at the basket level: protective review timing is too tightly coupled to duty stage, incident shape, or safeguarding regime to claim one shared numeric band yet.

## What portable numeric bands still may not do

Even when a promoted envelope carries a shared numeric band, it may not:

1. weaken a shell invariant or challenge path;
2. change the first meaningful review point;
3. lengthen truthful expiry or imply hidden carry-forward;
4. hide a republished second window inside the same supposedly shared band;
5. convert calendar or label upkeep into route redesign, merits preparation, queue shaping, or owner-boundary drift.

Numeric portability is therefore subordinate to shell truth. The number travels only while the packet meaning still does.

## What services must still publish locally

Even under `PQT-BOTH` or `PQT-CAP`, a service must still publish:

- the exact promoted basket and portability tier already in force;
- any stricter local cap or shorter local window;
- the real post-window checkpoint that will test whether inherited trust still deserves to survive;
- the local breach signals that collapse the envelope back into ordinary packet-governance rules;
- any residue that remains owner-, site-, or regime-specific.

This document therefore does **not** create a right to reuse old maintenance notices. It only says when the archive is willing to let one small number travel with an already portable basket.

## Starter quantitative matrix

| Promoted basket | Prior portability | Quantitative portability | Shared band | Why this is the archive's current limit |
|---|---|---|---|---|
| `PME-LABEL` | `PMT-BRANCH` | `PQT-BOTH` | `QC-3 + QW-14D` | wording cleanup usually clusters tightly without changing packet power |
| `PME-CALENDAR` for `AF-RECORD` | `PMT-FAMILY` | `PQT-CAP` | `QC-2`; window local | edit density often travels better than checkpoint cadence |
| `PME-CALENDAR` for `AF-ROUTE` | `PMT-FAMILY` | `PQT-LOCAL` | none | callback and queue cadence vary too much across regimes |
| `PME-CALENDAR` for `AF-SAFETY` | `PMT-LOCAL` | `PQT-LOCAL` | none | protective review timing is too regime-bound |
| `PME-ROUTE` | `PMT-LOCAL` | `PQT-LOCAL` | none | first-contact and challenge-route truth still do not travel |

## Why this belongs in the archive now

This is a small but useful hardening step. The archive already had a basket rule and a portability rule; without this quantitative pass, a service could still over-interpret those wins and quietly stretch a promoted envelope into a denser or longer-running maintenance programme than the inherited trust could honestly support.

The archive can now close `FT-0065` directly:

> basket portability does not automatically imply numeric portability. In the starter canon, `PME-LABEL` usually carries `QC-3 + QW-14D`, `PME-CALENDAR` for `AF-RECORD` usually carries only `QC-2`, and route / safety calendars keep both numbers local.

That claim is now canon, but still live. The archive now has a starter checkpoint / breach answer too: see [`portable-checkpoint-and-breach-defaults-for-promoted-packet-maintenance-envelopes.md`](portable-checkpoint-and-breach-defaults-for-promoted-packet-maintenance-envelopes.md). The archive now has a starter republication / recurrence answer too: see [`portable-republication-and-recurrence-defaults-for-promoted-packet-maintenance-envelopes.md`](portable-republication-and-recurrence-defaults-for-promoted-packet-maintenance-envelopes.md). The next narrower question is which promoted portable maintenance envelopes, if any, can safely carry one shared **cumulative-cycle ceiling or fatigue rule** across repeated cycles, and which should keep long-run accumulation and de-promotion handling local even when republication or recurrence duties now travel. See `OQ-0038`.
