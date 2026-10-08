# Portable checkpoint and breach defaults for promoted packet maintenance envelopes

This document closes the archive's next packet-governance gap: **once a pre-declared packet maintenance envelope already travels as a promoted basket and may even carry a shared numeric band, do the post-window checkpoint and breach triggers travel too, or should that proof bundle stay local?**

The archive's answer is narrower again:

> only maintenance classes whose **verification object** and **collapse semantics** remain truthful across the reuse scope should carry one shared post-window checkpoint / breach package. In the starter canon, `PME-LABEL` may usually carry both, `PME-CALENDAR` for `AF-RECORD` may usually carry only a shared breach family while keeping the checkpoint anchor local, and route or safety calendars still keep both local.

The point is to avoid three opposite errors at once:

- **proof laundering** — a service uses one promoted basket and one small numeric band to imply that its post-window verification duties travel too when the real checkpoint object or collapse rule still varies materially by owner or regime;
- **cadence concealment** — a service publishes one supposedly portable checkpoint even though the first meaningful review point still depends on local record calendars, callback practice, or protective staging;
- **permanent under-hardening** — a promoted envelope whose checkpoint object and collapse semantics really are stable enough to travel never gets one reusable proof bundle and therefore keeps relitigating the same small post-window discipline locally.

Current public signals support this thinner move. OECD's 2026 outlook keeps pressing educational AI toward pedagogically purposeful design rather than convenience-first task completion; OpenAI's current learning-outcomes work emphasizes longitudinal measurement instead of one-off performance snapshots; UNESCO's 2026 competency frameworks keep human agency and AI pedagogy central; and ICO guidance keeps challengeable design, privacy by default, and child-focused limits in view. See `B11`, `B23`, `B143`, `B146`, `B149`, `B150`, `B151`.

## Relationship to the existing packet-governance canon

This document does not replace [`portable-defaults-for-predeclared-packet-maintenance-envelopes.md`](portable-defaults-for-predeclared-packet-maintenance-envelopes.md), [`portable-quantitative-bands-for-promoted-packet-maintenance-envelopes.md`](portable-quantitative-bands-for-promoted-packet-maintenance-envelopes.md), or [`publication-of-local-departures-from-owner-facing-recovery-packet-defaults.md`](publication-of-local-departures-from-owner-facing-recovery-packet-defaults.md).

Those surfaces already answer:

- when recurring same-basket upkeep may use a pre-declared maintenance envelope at all;
- which baskets may travel as `PMT-BRANCH`, `PMT-FAMILY`, or `PMT-LOCAL`;
- which promoted baskets, if any, may also carry a shared numeric cap/window band;
- the shell invariants, publication floor, and collapse triggers that keep batching honest.

This document answers one narrower question:

- **which promoted portable envelopes, if any, can also carry one shared post-window checkpoint / breach package across their reuse scope?**

## Three checkpoint-portability tiers

The archive now distinguishes three checkpoint-portability tiers.

| Tier | Meaning | What travels | What stays local |
|---|---|---|---|
| `PCP-BOTH` | the promoted envelope carries one shared checkpoint family and one shared breach package | the checkpoint object, the minimum verification questions, and the collapse triggers | any stricter local proof note, additional local reviewers, and local explanatory language |
| `PCP-BREACH` | the promoted envelope carries only one shared breach package | the reasons that collapse inherited trust | the actual checkpoint anchor and the local verification object |
| `PCP-LOCAL` | the promoted envelope carries no shared checkpoint package | only the basket and any previously earned portability / quantitative tier | both the checkpoint anchor and the breach package |

The archive is deliberately asymmetric again:

> checkpoint portability is harder to earn than numeric portability. A basket can travel, and even a low cap can travel, while the truthful post-window proof bundle still does not.

## Five tests for whether checkpoint / breach duties really travel

A promoted portable maintenance envelope may harden above `PCP-LOCAL` only when all five tests hold.

1. **same-verification-object test** — comparable sites or owners are genuinely checking the same thing after the window closes, rather than one site checking render fidelity while another is effectively checking a different record or queue event.
2. **same-anchor-truth test** — the named checkpoint can be described in one reusable way without concealing a later first meaningful review in some ordinary reuse cases.
3. **same-collapse-semantics test** — the events that should collapse inherited trust are materially the same across the proposed reuse scope.
4. **no-latency-loss test** — the shared package does not delay learner visibility, challengeability, or truthful expiry handling anywhere inside the proposed reuse scope.
5. **no-rolling-renewal-disguise test** — the shared package does not make it easier to treat repeated renewal, republication failure, or slow redesign as though it were still one bounded maintenance episode.

Failing the first, second, or fourth test keeps the envelope at `PCP-LOCAL`. Failing only the second while the collapse semantics still travel usually points to `PCP-BREACH`: the reasons for collapse may travel while the actual checkpoint anchor still stays local.

## The starter checkpoint and breach packages

The archive now names one shared checkpoint family and one shared breach family.

| Code | Meaning |
|---|---|
| `CK-LABEL-SHELL` | a post-window checkpoint that verifies the same packet still shows the same field map, same challenge route, same review anchor, and same expiry truth after label/plain-language cleanup |
| `BR-PME-CORE` | a breach family triggered by shell drift, cap/window overrun, missed published checkpoint, or silent rollover into a second maintenance episode |

The archive does **not** yet create a larger library. The starter canon is deliberately small:

- no promoted portable maintenance envelope currently carries more than one shared checkpoint family;
- no promoted portable maintenance envelope currently carries a portable breach family that omits missed-checkpoint or silent-rollover triggers;
- where the archive refuses a shared checkpoint or breach package, services must still publish a **local** checkpoint anchor and collapse rule rather than hiding behind a portable basket or numeric band alone.

## The archive's starter checkpoint answers

### `PME-LABEL` usually hardens as `PCP-BOTH`

`PME-LABEL` may usually carry **both** a shared checkpoint family and a shared breach package across its promoted branch scope.

Why the archive allows this:

- label/plain-language upkeep usually preserves the same verification object: the service is checking that wording cleanup did not silently alter field inclusion, challengeability, review-anchor meaning, or expiry truth;
- the real post-window checkpoint can usually be described the same way across the branch scope: after the bounded clean-up burst closes, verify the rendered packet shell against the inherited field map and rights shell;
- the same small collapse triggers usually remain truthful across the reuse set.

The starter default is therefore:

> when `PME-LABEL` has already earned `PMT-BRANCH` and `PQT-BOTH`, it may usually also inherit `PCP-BOTH` with `CK-LABEL-SHELL + BR-PME-CORE`.

What `CK-LABEL-SHELL` must minimally verify:

1. the same fields still appear, disappear, and group the same way as before the maintenance window;
2. the challenge / review route is still equally visible and truthful;
3. the named review anchor still refers to the same real post-window checkpoint;
4. expiry, carry-forward, and republication truth have not weakened.

What `BR-PME-CORE` means in this branch-starter use:

- **shell-drift breach** — field inclusion logic, family-conditioned scope, challenge-route prominence, review-anchor meaning, or expiry truth changes;
- **density breach** — the shared cap or shared window is exceeded;
- **checkpoint-miss breach** — the promised post-window checkpoint is not actually performed or published as promised;
- **rollover breach** — the service tries to keep using the same envelope after the checkpoint without republication.

### `PME-CALENDAR` for `AF-RECORD` usually hardens only as `PCP-BREACH`

Record-owner calendar housekeeping may usually carry one shared **breach family**, but not one shared checkpoint family.

Why the archive stops there:

- the same events usually do collapse inherited trust across the family — anchor drift, expiry/carry-forward weakening, cap overrun, checkpoint miss, or silent rollover all still mean the packet no longer deserves the promoted maintenance story;
- but the actual checkpoint anchor is still too dependent on local term structure, record refresh cadence, progression calendar, or exam-cycle practice to claim one shared post-window checkpoint family honestly.

The starter default is therefore:

> when `PME-CALENDAR` for `AF-RECORD` has already earned `PMT-FAMILY` and `PQT-CAP`, it may usually inherit `PCP-BREACH` with `BR-PME-CORE`, while the actual checkpoint anchor and local verification object must still be published against the real record-review cadence.

What stays local even here:

- the exact post-window checkpoint name or date;
- the office-specific record object being rechecked;
- any stronger local proof question tied to transcript refresh, exam-board carry-forward, or award-cycle timing.

### `PME-CALENDAR` for `AF-ROUTE` stays `PCP-LOCAL`

Route-owner calendar housekeeping keeps **both** the checkpoint and the breach package local in the starter canon.

Why it does not yet carry a shared package:

- route systems often combine callback cadence, intake order, partner inventory, and challenge-route visibility in ways that make both the verification object and the collapse rule more owner-specific than the basket name suggests;
- the same nominal delay or checkpoint miss can mean materially different learner effects across referral, dispatch, and partner-capacity environments.

### `PME-CALENDAR` for `AF-SAFETY` stays `PCP-LOCAL`

Safety-owner calendar handling remains fully local for the same reason it remained non-portable at the basket and numeric layers: protective review timing and collapse semantics are too tightly coupled to incident shape, duty stage, and safeguarding regime to claim one shared checkpoint or breach package yet.

## What portable checkpoint packages still may not do

Even under `PCP-BOTH` or `PCP-BREACH`, a promoted envelope may not:

1. weaken a shell invariant, challenge path, or truthful expiry statement;
2. make a later first meaningful review look equivalent to an earlier one;
3. replace republication when a second maintenance episode begins;
4. hide route redesign, merits preparation, or owner-boundary drift inside a supposedly shared checkpoint package;
5. treat a missed checkpoint as harmless simply because the basket and cap were portable.

Checkpoint portability is therefore subordinate to shell truth. The proof bundle travels only while the post-window meaning still does.

## What services must still publish locally

Even under `PCP-BOTH` or `PCP-BREACH`, a service must still publish:

- the promoted basket and portability tier (`PMT-*`);
- any shared numeric tier (`PQT-*`) and the actual local cap/window when the numbers do not fully travel;
- the exact local checkpoint anchor when the shared package does not supply it;
- any stricter local breach trigger, stronger review owner, or additional local republication rule.

## Starter matrix

| Envelope | Portability tier | Quantitative tier | Checkpoint tier | Starter package | Why |
|---|---|---|---|---|---|
| `PME-LABEL` | `PMT-BRANCH` | `PQT-BOTH` | `PCP-BOTH` | `CK-LABEL-SHELL + BR-PME-CORE` | verification object and collapse semantics usually travel with the branch scope |
| `PME-CALENDAR` for `AF-RECORD` | `PMT-FAMILY` | `PQT-CAP` | `PCP-BREACH` | `BR-PME-CORE`; checkpoint anchor local | collapse semantics often travel better than checkpoint cadence |
| `PME-CALENDAR` for `AF-ROUTE` | `PMT-FAMILY` | `PQT-LOCAL` | `PCP-LOCAL` | local checkpoint + local breach package | callback / partner / queue semantics still vary too much |
| `PME-CALENDAR` for `AF-SAFETY` | `PMT-LOCAL` | `PQT-LOCAL` | `PCP-LOCAL` | local checkpoint + local breach package | protective timing and collapse semantics remain regime-bound |

## Why this move belongs in an education-with-AI archive

This may look like a tiny packet-governance refinement. It matters because the archive's core claim is not merely that educational AI should be safe in principle, but that **support, recovery, and rights shells should remain truthful under ordinary operational upkeep**. Once institutions run official study companions, access-routing services, or owner-facing recovery paths at scale, small shell edits become inevitable. The archive therefore needs an honest answer not only about when maintenance can be batched, but about which parts of the *proof that batching stayed harmless* can really travel.

That answer is now narrower and clearer: branch-level label cleanup may usually share the checkpoint and the breach package; record-owner calendar upkeep may usually share only the breach package; route and safety calendar handling must still prove themselves locally.

## Status

This document is **adopted canon** for the archive's packet-maintenance line.

It closes `FT-0066` and sharpens `OQ-0036`.

The archive now has a starter republication / recurrence answer too: see [`portable-republication-and-recurrence-defaults-for-promoted-packet-maintenance-envelopes.md`](portable-republication-and-recurrence-defaults-for-promoted-packet-maintenance-envelopes.md). The next narrower question is which promoted portable maintenance envelopes, if any, can safely carry one shared **cumulative-cycle ceiling or fatigue rule** across repeated cycles, and which should keep long-run accumulation and de-promotion handling local even when republication or recurrence duties now travel. See `OQ-0038`.
