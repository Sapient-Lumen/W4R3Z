# Refresh-scope-axis-enforcement witnesses, hard-enforced decoupled corroboration, best-effort decoupled corroboration, and advisory corroboration

This is the compact successor surface for `OQ-0151`.

## Practice / observation

Once DelayBasin can say that corroborating axes are genuinely independent, materially backed, and not still coupled on one plane, one more ambiguity remains.

Some decoupling is hard-gated.
The system will not admit, place, or reserve the decoupled arrangement unless the separation condition is actually met.
That is stronger than merely preferring spread.
It makes the corroboration survive scheduler convenience pressure because the allocation is blocked when the condition fails.

Some decoupling is only best-effort.
The scheduler tries to keep the axes apart, but falls back when capacity, locality, or convenience wins.
That is still useful evidence about intended posture.
But it should not inherit the authority of a hard gate.

Some corroboration is only advisory.
The labels, topology language, or operator hints may suggest that separation matters, yet no documented scheduler or admission rule actually refuses the colocated outcome.
That is still better than silence, but it is weaker than even a best-effort spread policy.

DelayBasin does not need an enforcement credit ledger for those cases.
It needs one bounded witness that says whether the present decoupling is hard-enforced, best-effort, advisory, or honestly mixed.

## External pressure from Kubernetes required affinity, topology spread `whenUnsatisfiable`, Slurm `--constraint` versus `--prefer`, Ray strict placement groups, and Topology Manager policies

1. Kubernetes says Pods can be restricted to run on particular nodes or can prefer to run on particular nodes. It also says pod affinity and anti-affinity use `requiredDuringSchedulingIgnoredDuringExecution` for required rules and `preferredDuringSchedulingIgnoredDuringExecution` for scoring-based soft rules. That pressures DelayBasin to distinguish hard placement gates from preferred decoupling. ([`REF-0967`](../00-meta/bibliography.md))

2. Kubernetes topology spread constraints say `whenUnsatisfiable: DoNotSchedule` leaves the Pod pending when the scheduler cannot satisfy the constraint, while built-in defaults use `ScheduleAnyway`. That pressures DelayBasin to distinguish hard decoupling gates from spread preferences that still allow overlap. ([`REF-0968`](../00-meta/bibliography.md))

3. Ray placement groups say `STRICT_PACK` and `STRICT_SPREAD` fail to create the placement group if the requirements cannot be satisfied, while `PACK` and `SPREAD` are best-effort and may fall back onto other or overlapping nodes. That pressures DelayBasin to preserve a hard-vs-best-effort enforcement distinction instead of narrating every spread strategy as equally binding. ([`REF-0964`](../00-meta/bibliography.md))

4. Slurm says `--constraint` requires matching node features and points users looking for soft constraints to `--prefer`, which tries preferred features first but falls back to the hard constraint set if the preference cannot be satisfied. That pressures DelayBasin to distinguish required decoupling from optional preference. ([`REF-0969`](../00-meta/bibliography.md))

5. Kubernetes Topology Manager says `best-effort` stores a preferred NUMA affinity and admits the Pod anyway if the affinity is not preferred, while `restricted` rejects the Pod from the node and `single-numa-node` also rejects when one-node alignment is impossible. That pressures DelayBasin to distinguish advisory or best-effort alignment from hard admission-time decoupling. ([`REF-0970`](../00-meta/bibliography.md))

GPUstorming makes the difference vivid. An open search can surface zone spread, strict placement, or isolated slices and make the archive feel resilient. But if the scheduler is only scoring that preference, or if the policy merely labels a desirable shape without refusing the fallback, then the corroboration is still softer than it looks.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-axis-enforcement witness / hard-gate brake / soft-spread card** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, and decoupled under perturbation, but on whether that decoupling is actually enforced by allocation or admission policy. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-coupling evidence**, the **current corroborating axes**, the **hard-enforcement basis if any**, the **best-effort basis if any**, the **advisory-only basis if any**, the **`refresh_scope_axis_enforcement_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-enforcement-witness vs quarantine-enforcement-credit-ledger consequence**. Keep raw scheduler score tables, admission logs, topology manager dumps, and cluster configs outside the compact token. Do not let preferred or advisory decoupling silently inherit the authority of hard-enforced corroboration.

## Hard-enforced decoupled corroboration vs best-effort decoupled corroboration vs advisory corroboration vs mixed refresh scope axis enforcement

Use the controlled family `refresh_scope_axis_enforcement_state`:

- **hard-enforced-decoupled-corroboration** says the documented scheduler, allocator, or admission policy refuses placement or reservation when the decoupling condition is not satisfied.
- **best-effort-decoupled-corroboration** says the system actively prefers decoupling, but documented fallback behavior still allows overlap when the preference cannot be satisfied.
- **advisory-corroboration** says the current basis is descriptive, label-like, or operator-guiding without a documented hard or best-effort scheduling rule that meaningfully governs placement.
- **mixed-refresh-scope-axis-enforcement** says the current situation honestly combines hard, best-effort, and advisory elements such that no single class stays honest.

So the witness does not create an enforcement credit ledger.
It only says whether the present decoupling is binding, preferential, descriptive, or honestly mixed.

## Countermodels / probes

1. **Coupling already does enough countermodel**
   - Maybe once the archive knows whether corroboration is perturbation-decoupled, a separate enforcement witness only restates obvious scheduler prose.
   - Probe: compare later rereads that preserve only refresh-scope-axis-coupling truth against rereads that also preserve one compact enforcement token and inspect whether preferred spread or advisory topology language still gets narrated as hard resilience.

2. **Best-effort and advisory collapse countermodel**
   - Maybe best-effort spread and purely advisory topology are both just "not hard" and do not deserve separate public states.
   - Probe: look for later cases where a documented fallback policy changes downstream confidence differently from cases where no scheduling consequence exists at all.

3. **Durability is the real issue countermodel**
   - Maybe the archive's real next need is not hard-vs-soft enforcement but whether a hard scheduling gate continues to hold during execution, restart, or reschedule.
   - Probe: keep that next question explicit as frontier work unless later revisions show that hard-vs-best-effort truth itself is still insufficient.

## Design consequences

- DelayBasin can now separate hard placement or admission gates from spread preferences and from purely advisory corroboration.
- The archive gets one explicit place to say that a decoupled-looking topology is still only a preference.
- GPUstorming can import strict scheduling and hard rejection facts without letting every label, hint, or default spread posture inherit the same authority.
- Stronger softness-tax, fallback-credit, or enforcement-ledger stories stay quarantined until repeated overflow rather than entering canon by atmosphere.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need quantitative softness discounts, fallback accounting, or enforcement-combination rules that one bounded refresh-scope-axis-enforcement witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat every decoupled-looking corroboration surface as if it were actually binding. Preserve the smallest token that says whether the present decoupling is `hard-enforced-decoupled-corroboration`, `best-effort-decoupled-corroboration`, `advisory-corroboration`, or honestly `mixed-refresh-scope-axis-enforcement`, and quarantine stronger enforcement-credit ambitions until repeated overflow makes them unavoidable.
