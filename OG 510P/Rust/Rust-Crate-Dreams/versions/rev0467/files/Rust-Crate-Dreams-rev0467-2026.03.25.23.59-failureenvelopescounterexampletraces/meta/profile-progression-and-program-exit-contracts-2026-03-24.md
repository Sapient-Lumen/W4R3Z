# Profile progression and program-exit contracts — 2026-03-24

## The problem this note solves

The archive already had:
- task profiles,
- basis locks,
- adjudication sessions,
- exception receipts,
- carry-forward receipts,
- recheck tickets,
- policy-profile packs,
- and profile-satisfaction reports.

What it did **not** yet preserve cleanly was the difference between:

1. **the adopter profile** asking,
2. **the current stage** in a decision program,
3. **the evidence gates** needed to progress,
4. **the progression report** saying what changed,
5. and **the program exit** that follows if progression succeeds, stalls, or splits.

Without that separation, future passes will drift into fake continuity.

## Contract vocabulary

### Policy profile pack
A statement of:
- adopter class,
- required evidence floors,
- allowed exception budget,
- escalation requirements,
- and explicit non-claims.

Question answered:
> “What standard should this adopter hold the packet to?”

### Decision-program stage
A statement of:
- program stage identity,
- required input artifacts,
- approval roles,
- progression gates,
- and reopen triggers.

Question answered:
> “Where in the adoption program are we right now?”

### Progression rule
A statement of:
- what must be inherited,
- what must be newly added,
- what unresolved gaps may remain,
- and which exit statuses are allowed.

Question answered:
> “What has to happen before we can move forward honestly?”

### Profile progression report
A report that says:
- which earlier artifacts were inherited,
- which new evidence was required,
- which gaps remain,
- which exceptions still spend the budget,
- and what the current stage exit status is.

Question answered:
> “What exactly changed between the old stage and the new one?”

### Program exit
A compact posture such as:
- `keep`,
- `conditional_keep`,
- `hold`,
- `split_boundary`,
- `replace_later`,
- `stop_and_reopen_compare`.

Question answered:
> “What operational posture follows from the current stage review?”

## Design rules

1. **Do not let profile and stage collapse together.**
   The same profile can appear in more than one stage, and the same stage shape may apply to multiple profiles.

2. **Do not let progression rewrite history.**
   A later stage may inherit an earlier basis, exceptions, or adjudications; it should not silently replace them.

3. **Do not let stage exit imply certification.**
   A `keep` or `conditional_keep` result is still an operational posture, not a regulatory or legal conclusion.

4. **Do not let unresolved gaps disappear just because progression happened.**
   A stage can advance with visible conditional gaps or bounded exceptions.

5. **Do not let hosted/public surfaces masquerade as stage-complete evidence.**
   docs.rs, Security tab, Trusted Publishing, and popularity signals may help satisfy some gates without satisfying all hard-domain or offline gates.

## Suggested stage families for the front-door stack

### `explore`
For:
- newcomers,
- experiments,
- internal comparisons,
- early proof-of-concept work.

Typical gate:
- task profile,
- candidate basis,
- profile pack,
- profile-satisfaction report,
- explicit runner-ups.

### `team_default`
For:
- shared internal defaults,
- onboarding docs,
- standard starter stacks.

Typical gate:
- basis lock,
- knowledge pack,
- recheck trigger policy,
- explicit exclusions,
- exception budget within limit.

### `enterprise_offline_gate`
For:
- mirror/vendoring users,
- restricted CI,
- air-gapped or approval-heavy delivery paths.

Typical gate:
- source-parity evidence,
- materialization plan,
- offline caveats,
- trusted-public posture imported but not overclaimed.

### `safety_onramp_gate`
For:
- safety-adjacent teams,
- higher-assurance adoption planning,
- boundary-splitting or replace-later programs.

Typical gate:
- target/support truth,
- MSRV/toolchain floor,
- dependency-lifecycle posture,
- explicit manual-review ceiling,
- bounded exceptions only where policy allows.

## Exit-status guidance

### `keep`
Use when:
- stage gate is satisfied,
- evidence floors are satisfied,
- and no unresolved issue exceeds policy.

### `conditional_keep`
Use when:
- stage gate is mostly satisfied,
- unresolved items remain visible,
- and exceptions or manual follow-up are still bounded.

### `hold`
Use when:
- current posture is frozen,
- progression is blocked,
- but replacement is not yet justified.

### `split_boundary`
Use when:
- one part of the system can proceed with the selected crate,
- but another boundary needs stricter isolation, wrapping, or replacement.

### `replace_later`
Use when:
- the current stage can proceed temporarily,
- but lifecycle posture already assumes later substitution.

### `stop_and_reopen_compare`
Use when:
- new facts are strong enough that the original front-door comparison should be reopened.

## Archive-level implication

Future passes that touch the front-door stack should ask:
- which profile is being served,
- which stage is active,
- which artifacts are inherited versus newly required,
- which exit statuses are allowed,
- and whether the crate’s non-claims stayed visible.

If the answer is “no,” then the pass should deepen program discipline before inventing more crate ideas.
