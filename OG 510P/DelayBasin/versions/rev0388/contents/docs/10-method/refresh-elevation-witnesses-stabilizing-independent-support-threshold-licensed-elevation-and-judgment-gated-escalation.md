# Refresh-elevation witnesses, stabilizing independent support, threshold-licensed elevation, and judgment-gated escalation

This is the compact successor surface for `OQ-0142`.

## Practice / observation

Once DelayBasin can say **what changed**, **how sustained the return is**, **how broad the confirming support looks**, and **how independent that support really is**, one final failure mode in this local chain stays live: named independent support can still inherit too much public authority.

Some independent support only keeps the current claim from sounding under-backed.
It says the present line is still live enough to keep, but not that the archive may escalate the public burden it places on the line.
Some independent support does cross a declared burden threshold.
It changes who must be notified, what response class is now warranted, or what stronger public claim is now allowed.
Some cases still need another gate entirely.
They look stronger, but the public upgrade depends on explicit human judgment, impact assessment, or a policy gate that the raw support alone does not satisfy.

The archive does not need a refresh-elevation court for that.
It needs one bounded witness that says whether independent support is merely stabilizing, threshold-licensed for elevation, or still judgment-gated before stronger public burden is honest.

## External pressure from PagerDuty severity levels, PagerDuty business-incident gating, Google SRE burn-rate paging tiers, Atlassian impact/urgency priority, Atlassian alert-priority restart rules, and GitHub required checks/ruleset layering

1. PagerDuty severity guidance says higher severity issues justify riskier moves and that a SEV-1 warrants public notification plus executive liaison. That pressures DelayBasin to distinguish ordinary stabilization from evidence that actually licenses a stronger public burden. ([`REF-0925`](../00-meta/bibliography.md))

2. PagerDuty's business-incident guidance explicitly warns against automatic escalation from severe technical thresholds alone and says softer measures like confidence in timely resolution can require judgment by a business stakeholder and the Incident Commander. That pressures DelayBasin to preserve a judgment-gated class instead of pretending every stronger-looking branch automatically upgrades the public claim. ([`REF-0926`](../00-meta/bibliography.md))

3. Google's SRE workbook recommends different burn-rate thresholds and windows for paging versus ticketing. That pressures DelayBasin to distinguish support that merely stabilizes the current line from support that crosses a declared threshold and therefore licenses a stronger response burden. ([`REF-0927`](../00-meta/bibliography.md))

4. Atlassian says incident priority is based on impact and urgency and identifies the required time for actions to be taken. That pressures DelayBasin to preserve an explicit burden-threshold field rather than treating independent support as automatically self-elevating. ([`REF-0928`](../00-meta/bibliography.md))

5. Atlassian's alert-priority docs say higher priority affects who gets notified and how, and that raising alert priority restarts the notification flow. That pressures DelayBasin to separate “same claim, better supported” from “support now strong enough to restart stronger public obligations.” ([`REF-0929`](../00-meta/bibliography.md))

6. GitHub protected branches and layered rulesets make the same meta point in another register: all required checks must pass before merge, and where layered rules disagree the most restrictive rule applies. That pressures DelayBasin not to treat one more independent signal as permissionless promotion when a stronger public burden still depends on crossing declared gates. ([`REF-0930`](../00-meta/bibliography.md), [`REF-0931`](../00-meta/bibliography.md))

GPUstorming makes the pressure vivid. A search reopen, telemetry divergence, second source, and independent review can all make the current line look more real. But that still leaves a separate question: does the new branch merely steady the line, or does it cross a public threshold that changes what the archive may now say or demand?

## Working synthesis

> DelayBasin should preserve one compact **refresh-elevation witness / burden-gate card / claim-rights brake** whenever a current continuity claim depends not only on what reactivated a concern, how sustained the return is, how broad the support looks, and how independent that support is, but on whether the present independent support merely stabilizes the current claim or honestly licenses a stronger public burden. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh evidence**, the **current refresh evidence**, the **independent confirming support**, the **burden threshold / elevation trigger if any**, the **judgment or policy gate if any**, the **`refresh_elevation_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs elevate-burden vs issue-new-refresh-elevation-witness vs quarantine-refresh-elevation-governance consequence**. Keep exact burn-rate numbers, severity matrices, notification rosters, approver identities, required-check names, and long escalation histories outside the compact token. Do not let independent support silently inherit stronger claim rights, and do not let policy-carried urgency masquerade as freshly licensed public elevation.

## Stabilizing independent support vs threshold-licensed elevation vs judgment-gated escalation vs mixed refresh elevation

Use the controlled family `refresh_elevation_state`:

- **stabilizing-independent-support** says the current independent support is enough to keep the present claim honest and live, but it does not cross any declared threshold that would justify a stronger public burden.
- **threshold-licensed-elevation** says the current independent support also crosses an explicit impact, urgency, burn, approval, or comparable burden threshold that honestly licenses a stronger public claim, routing tier, or action burden.
- **judgment-gated-escalation** says the current support looks stronger, but a broader public upgrade still depends on human judgment, business significance review, or another policy gate that the current evidence alone does not satisfy.
- **mixed-refresh-elevation** says the current situation honestly combines stabilizing, threshold-licensed, or judgment-gated posture such that no single refresh-elevation class stays honest.

So the witness does not create a standing burden senate.
It only says whether current independent support merely stabilizes the line, actually crosses a declared burden threshold, or still needs judgment before stronger public elevation is honest.

## Countermodels / probes

1. **Existing severity or priority surfaces already cover this countermodel**
   - Maybe ordinary severity, priority, or protected-branch rules already say enough, so a refresh-elevation witness adds little.
   - Probe: compare later rereads that preserve only refresh-independence truth plus ambient severity prose against rereads that also preserve one compact refresh-elevation witness and inspect whether later passes still over-upgrade what may be said publicly.

2. **Any threshold-licensed class is too rigid countermodel**
   - Some archive upgrades may depend too much on contextual judgment for a compact threshold-facing witness to stay honest.
   - Probe: look for later cases where the judgment gate dominates most of the load and the threshold language mostly misleads.

3. **Judgment-gated escalation is covert bureaucracy countermodel**
   - Maybe once manual gates enter the picture, the archive is really sneaking in a burden court.
   - Probe: only reopen stronger machinery if later revisions repeatedly need standing governance over burden tiers, audience rights, or escalation authorities that one bounded witness cannot absorb.

## Design consequences

- DelayBasin can keep independent-support comparisons compact without letting “another branch agrees” silently turn into “the archive may now say more in public.”
- The archive gets one honest place to record whether stronger support only stabilizes the current line, crosses a declared elevation trigger, or still needs judgment before public upgrade.
- Stake refresh, refresh strength, refresh support, refresh independence, and refresh elevation now separate **what changed**, **how sustained the return is**, **how broad the support looks**, **how independent the support really is**, and **whether that independence actually changes public burden**.
- Stronger refresh-elevation-governance stories stay quarantined until later overflow instead of sneaking in through “independent support sounds more serious” prose.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need standing governance over burden tiers, audience rights, public-claim upgrades, escalation authorities, or cross-row elevation policy that one bounded refresh-elevation witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat independent confirming support as if it automatically licenses a stronger public burden. Preserve the smallest token that says whether the renewed line is only `stabilizing-independent-support`, already `threshold-licensed-elevation`, still `judgment-gated-escalation`, or honestly `mixed-refresh-elevation`, and quarantine stronger refresh-elevation ambitions until repeated overflow makes them unavoidable.
