# Collection-anchor choice and remittance-chain ladder

## Question in one sentence

Given the archive's closed rule that remittance should begin at the **strongest, most legible, least distortive anchor that already sees the taxable flow, asset, registry event, or controller relationship**, **what is the smallest workable ladder for deciding when direct filing is enough, when withholding or platform remittance should take over, when registries or meters should bill directly, when controller-group collection should outrank downstream collection, and when ex ante custodial security should replace ordinary after-the-fact remittance entirely?**[S10][S15][S21][S27][S39][S41][S65][S66][S68][S77]

## Companion routes

Use this memo with:

- [`../10-framework/collection-and-remittance-routing.md`](../10-framework/collection-and-remittance-routing.md)
- [`../10-framework/automaticity-and-claim-friction-routing.md`](../10-framework/automaticity-and-claim-friction-routing.md)
- [`../10-framework/administration-explanation-and-appeal-routing.md`](../10-framework/administration-explanation-and-appeal-routing.md)
- [`../10-framework/enforcement-proportionality-and-recovery-routing.md`](../10-framework/enforcement-proportionality-and-recovery-routing.md)
- [`../10-framework/tax-subjecthood-and-liability-routing.md`](../10-framework/tax-subjecthood-and-liability-routing.md)
- [`../10-framework/beneficial-ownership-and-anti-fragmentation-routing.md`](../10-framework/beneficial-ownership-and-anti-fragmentation-routing.md)

Route: collect at the strongest real anchor that already sees the base, but do not let visibility convenience become a reason to tax the wrong subject, dump compliance onto weak downstream actors, or hide relief behind separate claims.[S21][S27][S39][S41][S65][S66][S68][S77]

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — subject-side filing first | keep ordinary direct filing or self-reporting as the default even where stronger intermediaries, registries, or controller groups already see the same facts more accurately.[S21][S27][S39] | Reject: too weak where the state can collect earlier and more legibly upstream. |
| B — collect wherever the cleanest data pipe exists | push remittance to whichever platform, meter, payment rail, or software layer already emits the easiest machine-readable record.[S10][S16][S17][S68][S77] | Reject: mistakes visibility for moral fit and risks taxing the wrong actor through the wrong base. |
| C — collection-anchor ladder | sort remittance into direct-filing, withholding / merchant / platform, registry-or-meter, controller-group-or-infrastructure, or ex-ante-custodian lanes.[S10][S15][S21][S27][S39][S41][S65][S66][S68][S77] | Adopt. |
| D — maximum upstream automation by default | route nearly all taxes through upstream intermediaries, utilities, registries, infrastructure providers, or custodians whenever technically possible.[S39][S65][S68][S77] | Reject: overshoots in person-specific cases and expands surveillance and cash-flow asymmetry risks. |

## Five-rung ladder

1. **direct-filing lane** — use where decisive facts are sparse, upstream anchors are weak, and person-level reconciliation is still the cleanest answer,[S21][S27][S39]
2. **withholding / merchant / platform lane** — use for regular flows or transaction taxes that a stronger intermediary already sees,[S3][S21][S65][S66][S68][S77]
3. **registry / cadastre / meter / permit lane** — use for immovable property, utilities, extraction points, and other place-bound or infrastructure-linked bases,[S5][S6][S7][S15][S21][S23][S25]
4. **controller-group / infrastructure lane** — use where shell-splitting, reseller layering, or cloud-linked AI stacks would otherwise let the remitter be chosen by avoidance design,[S9][S10][S15][S27][S34][S35][S39]
5. **ex ante custodian lane** — use for bonds, reserves, insurance, escrow, or reserve custodians where the real issue is downside risk and post-collapse remittance would arrive too late.[S15][S17][S39][S41]

## Provisional recommendation

Adopt **Option C — the collection-anchor ladder** as the archive's default calibration for remittance design.[S10][S15][S21][S27][S39][S41][S65][S66][S68][S77]

Presumption:

- stay with **direct filing** only where stronger anchors do not already see the decisive facts,
- move to **withholding, merchant, or platform remittance** where recurring flows or transaction taxes already pass through a higher-capacity intermediary,
- use **registry or meter billing** where the base is immovable, permitted, or infrastructure-linked,
- move to **controller-group or infrastructure collection** where shell design or affiliate splitting would otherwise select the remitter,
- and use **custodial security first** where collapse, cleanup, or incident finance makes ordinary ex post remittance morally too late.

That is the narrowest workable setting because it improves legibility and compliance without pretending that whatever is easiest to meter is automatically the right tax object.

For AI-era taxes, the anchor implication is practical: ordinary controller-side receipts can sit in withholding or infrastructure-facing lanes, but cross-border model stacks, reseller chains, and major cloud bottlenecks often belong in the **controller-group / infrastructure lane**, while catastrophic cleanup or incident finance belongs in the **ex ante custodian lane**. Thin shells plus post-failure collection are not a collection design; they are a forecast of non-payment.[S10][S15][S17][S27][S34][S35][S39][S41]

## Default anchor table

| Base or context | Default remittance rung | Why this rung usually fits | Archive warning |
|---|---|---|---|
| ordinary wage and salary income | withholding lane | employers already see recurring cash wages and can reconcile against person-level liability later.[S21][S65][S66] | withholding convenience must not erase floor protection, explanation rights, or later correction. |
| broad consumption taxes and platform sales | merchant / platform lane | sellers and platforms sit at the transaction point and can remit more cleanly than final consumers.[S3][S21][S68][S77] | preserve rebates and floor correction outside the checkout line rather than through exemption jungles. |
| land, immovable property, and occupancy-linked local charges | registry / cadastre lane | situs-linked billing best matches immovable bases and local fiscal visibility.[S5][S23][S25] | illiquidity calls for instalments, deferral, or liens, not erasure of the site-rent claim. |
| upstream extraction, utilities, or measurable facility burdens | meter / permit lane | there are fewer choke points and stronger records upstream than among diffuse downstream users.[S6][S7][S15][S21] | upstream convenience must not erase burden review or local repair duties. |
| cross-border groups, cloud-linked AI stacks, or affiliate-split rents | controller-group / infrastructure lane | the real controller, major cloud intermediary, or grouped filing entity is harder to fake than many downstream accounts.[S9][S10][S15][S27][S34][S35] | group first, then choose the anchor; otherwise shell design picks the remitter. |
| high-downside AI deployment, decommissioning, cleanup, or incident finance | ex ante custodian lane | bonds, reserves, insurance, or supervised custodians work before shell failure or insolvency.[S15][S17][S39][S41] | do not rely on post-collapse collection from thin operating vehicles. |

## Anti-patterns

- **meter decides morality** — whichever actor emits the neatest data exhaust becomes the remitter even when the base or subject sits elsewhere.[S10][S21][S68]
- **small-firm shock absorption** — the state could collect earlier upstream but instead leaves weak firms or households to bridge cash-flow and compliance risk.[S26][S27][S39]
- **automated taking, manual giving** — withholding and billing are frictionless, but rebates, refunds, and transition support still require discovery and separate claims.[S64][S65][S66][S68]
- **anchor laundering** — shell chains, white-label platforms, cloud resellers, or affiliate routing are used to relocate remittance away from the real controller.[S10][S27][S34][S35]
- **surveillance creep by convenience** — natural-system integration becomes a pretext for excessive data retention, opaque scoring, or purpose drift.[S40][S41][S44][S77]

## What would change the recommendation

Tighten, loosen, or replace this ladder if:

- stronger evidence shows that a lighter-touch anchor captures the base with similar accuracy and materially less burden,
- digital integration begins improving both remittance and low-friction relief without enlarging privacy costs,
- controller-group collection proves systematically over-inclusive in sectors now treated as fragmented but genuinely independent,
- or new infrastructure layers create durable choke points that are harder to evade and more accountable than the anchors named here.[S10][S27][S39][S40][S41][S65][S68][S77]

## Source IDs only

[S3][S5][S6][S7][S9][S10][S15][S16][S17][S21][S23][S25][S26][S27][S34][S35][S39][S40][S41][S44][S64][S65][S66][S68][S77]

[S3]: ../../SOURCES.md#S3
[S5]: ../../SOURCES.md#S5
[S6]: ../../SOURCES.md#S6
[S7]: ../../SOURCES.md#S7
[S9]: ../../SOURCES.md#S9
[S10]: ../../SOURCES.md#S10
[S15]: ../../SOURCES.md#S15
[S16]: ../../SOURCES.md#S16
[S17]: ../../SOURCES.md#S17
[S21]: ../../SOURCES.md#S21
[S23]: ../../SOURCES.md#S23
[S25]: ../../SOURCES.md#S25
[S26]: ../../SOURCES.md#S26
[S27]: ../../SOURCES.md#S27
[S34]: ../../SOURCES.md#S34
[S35]: ../../SOURCES.md#S35
[S39]: ../../SOURCES.md#S39
[S40]: ../../SOURCES.md#S40
[S41]: ../../SOURCES.md#S41
[S44]: ../../SOURCES.md#S44
[S64]: ../../SOURCES.md#S64
[S65]: ../../SOURCES.md#S65
[S66]: ../../SOURCES.md#S66
[S68]: ../../SOURCES.md#S68
[S77]: ../../SOURCES.md#S77
