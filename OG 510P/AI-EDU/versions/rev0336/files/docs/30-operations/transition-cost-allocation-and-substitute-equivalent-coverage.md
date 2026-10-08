# Transition-cost allocation and substitute-equivalent coverage

The archive already distinguishes documented reliance and burden bands. It also
has no-fault fee-waiver rules. This surface makes the payer and coverage rule
operational across public, higher-education, workforce, and community-learning
routes.

The core rule is:

> when a system-caused change creates a protected continuity duty, the learner
> should not carry the front-end cost of preserving a route-equivalent chance.

That does not mean every preferred alternative is free. It means the cost of
repairing institutional churn should sit first with the system that caused or
published the route, and only later with a learner's elective upgrade.

## Payer ladder

| Code | Payer posture | Use when |
|---|---|---|
| `TC0` | ordinary learner cost | no documented reliance, no system-caused change, or purely elective upgrade |
| `TC1` | change-owner absorbs | the publishing, advising, or rule-owning body caused the change and can provide substitute-equivalent repair |
| `TC2` | receiving / public node fronts | the learner needs a route-equivalent step now, and backend responsibility can be reconciled later |
| `TC3` | shared public / partner pool | multiple owners jointly created reliance or jointly benefit from the route continuity |
| `TC4` | hardship / access protection | direct charge, travel, device, accessibility, or schedule burden would defeat access despite formal equivalence |
| `TC5` | learner elective delta | learner chooses a materially richer, faster, or unrelated path after a no-loss substitute was available |

`TC1-TC4` are no-front-end-invoice postures. They can still differ backstage in
who reimburses whom.

## Evidence and burden crosswalk

| Reliance / burden pattern | Default coverage |
|---|---|
| `E0` plus `B0-B1` | updated guidance; ordinary learner cost may remain |
| `E1` plus `B1-B2` | queue preservation and fee waiver for system-required bridge |
| `E2` plus `B1-B2` | change-owner or receiving/public node covers substitute-equivalent review or bridge |
| `E2-E3` plus `B3` | funded substitute-equivalent route, teach-out, or challenge path is presumptive |
| `E4` near-finish reliance | preserve completion route if lawful; do not charge for system-caused restart |
| protected-route or accessibility burden | apply `TC4` even where ordinary burden might look only `B1-B2` |

## What counts as substitute-equivalent cost

Substitute-equivalent coverage may include:

- bridge module or reassessment fee;
- transcript, portfolio, or prior-learning review fee;
- required proctoring, interview, or defense cost;
- accessible-format conversion or assistive channel needed for the substitute;
- travel or scheduling burden that the original route did not require;
- second-review or appeal administration when nonacceptance follows a system
  change;
- temporary seat hold, cohort transfer, or queue-preserving intake work.

It does not automatically include:

- a learner's unrelated preferred programme;
- premium speed beyond the protected no-loss route;
- optional enrichment;
- costs caused by fraud, misrepresentation, or independent learner choice;
- a credential upgrade that goes beyond the original route-equivalent claim.

## Coverage owner rule

Every transition packet should name one visible coverage owner even where the
back-end payer is disputed.

```text
Learner-facing coverage owner:
Back-end payer posture: TC0 / TC1 / TC2 / TC3 / TC4 / TC5
Reliance band:
Burden band:
Substitute-equivalent step:
Front-end charge: none / waived / ordinary / elective delta
Accessibility or protected-route adjustment:
Deadline / queue protection:
Backend reimbursement owner:
Appeal route:
Expiry or renewal trigger:
```

The learner should not have to solve an inter-office reimbursement dispute in
order to preserve a time-sensitive route.

## Decision defaults

| Situation | Default |
|---|---|
| rule owner withdraws or changes a published standing route after `E2` reliance | `TC1` if the owner can repair; otherwise `TC2` with backend reconciliation |
| receiving node requires a new short bridge because standing evidence changed | waive or front the bridge when reliance is `E2-E4` and burden is `B1-B3` |
| public route changes while funding or mandated participation window is live | `TC2-TC4` plus no-deadline-loss rule |
| accessibility need makes the substitute route materially harder | `TC4`; equivalence is not real if access burden defeats participation |
| learner declines a no-loss substitute and chooses a better / unrelated route | `TC5` only for the elective delta |

## Closeout

This surface resolves `FT-0017` by combining reliance evidence, burden bands,
fee-waiver logic, and a simple payer ladder. Future work should test whether
`TC1-TC4` are enough for real multi-agency cases or whether public-route
funding needs a more detailed reimbursement grammar.

See
[`documented-reliance-and-burden-thresholds.md`](documented-reliance-and-burden-thresholds.md),
[`no-fault-transition-cost-absorption-and-fee-waiver-rules.md`](no-fault-transition-cost-absorption-and-fee-waiver-rules.md),
[`in-flight-teach-out-and-substitute-equivalent-rules.md`](in-flight-teach-out-and-substitute-equivalent-rules.md),
[`minimum-public-entitlement-and-handoff-standard.md`](minimum-public-entitlement-and-handoff-standard.md),
and `B74`, `B76`, `B77`, `B79`, `B80`, `B81`, `B82`, `B83`.
