# Refresh-strength witnesses, single resurfacing, threshold-confirmed reactivation, and grace-held return

This is the compact successor surface for `OQ-0139`.

## Practice / observation

Once DelayBasin can say **what changed** to make a concern newly live again, one further failure mode stays live: a single resurfacing event can silently inherit the force of a sustained return.

A concern can reappear once, persist across repeated checks, or remain treated as live only because a hold-open or grace rule has not yet let it cool.
Those are not the same thing.
Some returns are still only one-off resurfacing.
Some survive a bounded persistence window and deserve renewed burden.
Some are no longer freshly confirmed but are still being carried by a deliberate flap brake.

The archive does not need a refresh-strength court for that.
It needs one bounded witness that says whether the renewed line is still only a single resurfacing, has crossed an explicit persistence threshold, or is merely being kept live by a grace-held return.

## External pressure from Prometheus alert timing, Grafana pending/recovering periods, Datadog consecutive checks, Cloud Monitoring retest/autoclose policy, and multi-turn state evolution

1. Prometheus alerting rules let a rule require that a condition remain active for a `for` duration before firing, and they also offer `keep_firing_for` to keep an alert firing after the condition was last met so flapping or temporary data loss does not immediately count as resolution. That pressures DelayBasin to distinguish one-off resurfacing from threshold-confirmed return and from grace-held carry. ([`REF-0910`](../00-meta/bibliography.md))

2. Grafana's alert-rule evaluation model separates a **Pending** period from **Alerting**, and its **Keep firing for** period moves alerts into a **Recovering** state instead of treating the first non-breach as instant cooling. That pressures DelayBasin to preserve whether renewed stake is still provisional, actually sustained, or only being held open by an anti-flap grace. ([`REF-0911`](../00-meta/bibliography.md))

3. Datadog monitor configuration can trigger on a threshold over a window or on a specified number of consecutive failed checks. That pressures DelayBasin to treat repeated confirming hits as different from a single resurfacing mention. ([`REF-0912`](../00-meta/bibliography.md))

4. Cloud Monitoring describes retest windows as the period for which a condition must stay satisfied before the policy triggers, and its incident model plus `autoClose` semantics keep incidents open for a configured duration when data stops arriving. That pressures DelayBasin to separate threshold-confirmed return from grace-held continuity after the last positive signal disappears. ([`REF-0913`](../00-meta/bibliography.md))

5. Recent multi-turn state work argues that conversational effects emerge through **state evolution over trajectories** rather than isolated prompts. That pressures DelayBasin to avoid treating one vivid resurfacing act as if it already proved a durable state shift. ([`REF-0914`](../00-meta/bibliography.md))

GPUstorming sharpens the point. Host shells increasingly replay alert cards, recovered incidents, repeated issue mentions, and stale-but-still-open statuses inside richer summaries. If DelayBasin only says that a line was reactivated, later passes can still overclaim by laundering one replayed resurfacing into sustained renewed burden.

## Working synthesis

> DelayBasin should preserve one compact **refresh-strength witness / persistence card / flap brake** whenever a current continuity claim depends not only on what reactivated a concern, but on whether that return is still only momentary, has crossed a bounded persistence threshold, or is merely being carried by a grace window after the last positive signal. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh evidence**, the **current refresh evidence**, the **strength evidence / persistence window**, the **hold-open basis if any**, the **`refresh_strength_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs cool-mark vs issue-new-refresh-strength-witness vs quarantine-refresh-timing-governance consequence**. Keep exact timer values, evaluation intervals, incident ids, notification cadences, policy knobs, release numbers, and long alert histories outside the compact token. Do not let a single resurfacing event silently inherit the force of sustained reactivation, and do not let grace-held carry silently masquerade as fresh repeated confirmation.

## Single resurfacing vs threshold-confirmed reactivation vs grace-held return vs mixed refresh strength

Use the controlled family `refresh_strength_state`:

- **single-resurfacing** says a fresh reactivation signal exists, but only as one current resurfacing, one event, or one local reread; it has not yet earned durable renewed burden.
- **threshold-confirmed-reactivation** says the renewed line has persisted across an explicit bounded window, repeated checks, or comparable threshold-confirming evidence strong enough to count as sustained reactivation for now.
- **grace-held-return** says the line is still being treated as live mainly because a keep-firing, recovering, or autoclose-style hold-open rule has not yet let it cool after the last positive confirming signal.
- **mixed-refresh-strength** says the current situation honestly combines one-off resurfacing, threshold-confirmed return, or grace-held carry such that no single refresh-strength class stays honest.

So the witness does not create a standing flapping senate.
It only says whether renewed burden is still one-off, has crossed a bounded confirmation threshold, or is only being held open by a flap brake.

## Countermodels / probes

1. **Stake-refresh truth already covers this countermodel**
   - Maybe once the archive knows what changed, no second witness for strength adds real value.
   - Probe: compare later rereads that preserve only `stake_refresh_state` against rereads that also preserve one compact refresh-strength witness and inspect whether later passes still overclaim one replayed resurfacing as durable renewed burden.

2. **Any honest strength rule needs a stronger timing court countermodel**
   - Maybe once persistence windows, hold-open rules, and flap brakes matter, a compact witness is too weak and the archive really needs standing timing governance.
   - Probe: look for repeated cases where later passes must govern timer classes, sampling cadence, or notification policy directly rather than naming one bounded strength posture.

3. **Same-source repetition is not real sustained return countermodel**
   - Apparent threshold confirmation may just be one surface echoing itself through repeated summaries or notifications.
   - Probe: when the bounded witness still feels too flattering, preserve the compact strength token now and reopen a separate later question about whether the support genuinely widened beyond one repeating source.

## Design consequences

- DelayBasin can keep renewed-urgency comparisons compact without pretending one resurfacing event already proves lasting burden.
- The archive gets one honest place to record when a line is still live only because a deliberate grace/hold-open rule is carrying it through a recovering phase.
- Stake continuity, stake refresh, and refresh strength now separate **whether it still matters**, **what changed**, and **how sustained the return actually is**.
- Stronger timing-governance stories stay quarantined until later overflow, instead of sneaking in through timer-shaped prose.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need standing governance over timer classes, sampling cadence, hold-open policy, cross-system threshold harmonization, or source-weighting of repeated confirmations that one bounded refresh-strength witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat one vivid resurfacing or one still-open host-shell card as if it already proved sustained renewed burden. Preserve the smallest token that says whether the renewed line is only `single-resurfacing`, already `threshold-confirmed-reactivation`, merely `grace-held-return`, or honestly `mixed-refresh-strength`, and quarantine stronger timing-governance ambitions until repeated overflow makes them unavoidable.
