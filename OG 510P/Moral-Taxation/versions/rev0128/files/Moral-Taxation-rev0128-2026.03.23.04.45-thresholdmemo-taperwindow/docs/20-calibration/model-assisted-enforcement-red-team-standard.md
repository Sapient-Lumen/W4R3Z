# Model-assisted enforcement red-team minimum standard

## Question in one sentence

Given the archive's closed rule that tax enforcement must remain proportionate, privacy-bounded, reviewable, and non-carceral, **what is the smallest workable adversarial-testing and retention standard for models used in audit triage, refund freezes, enforcement referrals, or collection escalation?**[S16][S17][S27][S39][S40][S41][S44]

## Closed rules invoked

This memo does **not** reopen the archive's constitutional waist. It relies on:

- [`../10-framework/enforcement-proportionality-and-recovery-routing.md`](../10-framework/enforcement-proportionality-and-recovery-routing.md)
- [`../10-framework/administration-explanation-and-appeal-routing.md`](../10-framework/administration-explanation-and-appeal-routing.md)
- [`../10-framework/anti-discrimination-and-status-proxy-routing.md`](../10-framework/anti-discrimination-and-status-proxy-routing.md)
- [`../10-framework/review-triggers-and-policy-reversibility.md`](../10-framework/review-triggers-and-policy-reversibility.md)
- [`../10-framework/standing-representation-and-remedy-routing.md`](../10-framework/standing-representation-and-remedy-routing.md)

The constitutional question is already settled: **models may assist enforcement triage, but coercive recovery, serious escalation, and adverse burden routing should not rest on untested black-box systems that cannot be challenged, rolled back, or bounded in retention and scope.**[S16][S17][S27][S39][S40][S41][S44]

## Why calibration is still needed

The archive already rejects opaque coercion, but it still needs a smallest workable operating standard for live enforcement systems. A usable standard has to avoid two opposite failures:

1. **unchecked enforcement scoring**, where models route people into audits, frozen refunds, or harder collection lanes without adversarial testing against bias, fabrication, or privacy creep, and  
2. **blanket anti-automation**, where every model-assisted signal is treated as forbidden even when bounded testing could safely support earlier correction, lighter-touch routing, or faster human review.[S16][S17][S27][S39][S40][S41]

## Small option set

### Option A — generic IT assurance only

Treat enforcement models like ordinary software. Test uptime and basic accuracy, but do not require dedicated red-team exercises for proxy discrimination, fabricated evidence chains, retention creep, gaming, or coercive escalation failures.[S17][S39][S40]

This is too weak for the archive. It treats enforcement risk as a technical-performance issue rather than a justice problem.

### Option B — paper policy review plus complaints

Require a written policy, a legal sign-off, and complaint handling after deployment, but do not require structured adversarial testing before or during live use.[S16][S17][S27]

This is better than pure generic assurance, but still too reactive where enforcement tools can freeze cashflow, intensify surveillance, or steer attention toward protected-burden proxies.

### Option C — minimum enforcement red-team lane

Require any model used for **material enforcement triage or escalation** to pass a compact recurring red-team lane that includes at least:

1. **scope declaration** — the action types the model may influence, and the actions it may not finalize on its own,  
2. **dataset and proxy review** — explicit testing for protected-status proxies, locality distortions, documentation filters, and known low-income or minority proxy bundles,  
3. **fabrication / contamination tests** — adversarial cases for stale data, duplicate records, synthetic identity collisions, and mistaken liability linkage,  
4. **gaming and threshold tests** — whether simple behavioral adaptation or clerical quirks can flip a case into a harsher lane,  
5. **retention-bound check** — a defined logging and deletion window tied to supervisory need rather than indefinite trace hoarding,  
6. **human-gated coercion rule** — no model-only path to liens, seizures, prosecution referral, or similarly coercive escalation,  
7. **rollback trigger** — predeclared failure rates or bias findings that suspend or narrow the tool, and  
8. **review packet retention** — enough documentation for later supervisory replay without requiring the subject to reverse engineer the system.[S16][S17][S27][S39][S40][S41][S44]

This option still allows enforcement triage, but it blocks silent drift from assistance into unreviewable coercion.

### Option D — full external certification for every update

Require every model revision, threshold tweak, or feature change to undergo full external certification and publication before any use in enforcement.[S17][S39][S40]

This is stronger than the archive needs as a general minimum. It risks freezing iterative correction, delaying safer replacements, and converting routine operating changes into a bottleneck that weaker administrations cannot sustain.

## Provisional recommendation

Adopt **Option C — the minimum enforcement red-team lane** as the archive's default operating standard for model-assisted enforcement.[S16][S17][S27][S39][S40][S41][S44]

Use a **tiered application** of that standard:

- **low-stakes case selection** may use lighter testing and shorter logs,  
- **audit triage, frozen refunds, and collection-lane assignment** should always use the full lane,  
- and **coercive escalation** should require both the full lane and real human sign-off before the action can proceed.[S16][S17][S27][S39][S40][S41]

That is the narrowest workable setting because it preserves three things at once:

- useful analytic assistance for early detection and prioritization,  
- adversarial testing against the failure modes most likely to make enforcement unjust, and  
- an explicit boundary between triage assistance and coercive state action.

## Default red-team matrix

| Enforcement use | Minimum red-team requirement | Human gate | Archive stance |
|---|---|---|---|
| low-stakes selection for reminder letters or clerical discrepancy review | proxy and contamination checks, short log window | on request | allowed if no adverse status hardens yet.[S16][S17][S27] |
| audit triage or refund-freeze recommendation | full minimum lane | available before finalization | default standard.[S16][S17][S39][S40] |
| collection-lane assignment or repeated high-risk flagging | full lane plus gaming tests and rollback triggers | proactive or immediate on request | should not operate as silent ratcheting toward harsher treatment.[S17][S27][S39][S41] |
| lien, seizure, prosecution referral, or similarly coercive escalation | full lane plus retained review packet | required before action | model assistance may inform, not autonomously coerce.[S17][S27][S41][S44] |

## Anti-patterns

- **accuracy-only theater** — aggregate accuracy is reported while proxy discrimination, contamination, and gaming are left untested.[S39][S40]
- **triage-to-coercion drift** — a tool approved for routing quietly becomes a de facto determiner of severe enforcement outcomes.[S17][S27][S41]
- **retention creep** — logs, traces, or feature stores are kept indefinitely because enforcement teams might want them later.[S17][S27]
- **threshold opacity** — internal escalation cutoffs shift without declared review or rollback conditions.[S39][S40][S41]
- **appeal without challenge packet** — the subject may contest the outcome but cannot learn enough to dispute the model-assisted path into enforcement.[S16][S17][S27][S44]

## What would change the recommendation

This minimum standard should be tightened, loosened, or replaced if any of the following become clearer:

- evidence shows that low-stakes routing still produces serious protected-burden skew,  
- external audit markets or public supervisory tooling become cheap enough to support broader third-party review,  
- retention burdens from challenge packets prove heavier than expected,  
- or enforcement systems begin combining multiple models in ways that collapse the line between recommendation and determination.[S16][S17][S27][S39][S40][S41][S44]

## Source IDs only

[S16][S17][S27][S39][S40][S41][S44]

[S16]: ../../SOURCES.md#S16
[S17]: ../../SOURCES.md#S17
[S27]: ../../SOURCES.md#S27
[S39]: ../../SOURCES.md#S39
[S40]: ../../SOURCES.md#S40
[S41]: ../../SOURCES.md#S41
[S44]: ../../SOURCES.md#S44
