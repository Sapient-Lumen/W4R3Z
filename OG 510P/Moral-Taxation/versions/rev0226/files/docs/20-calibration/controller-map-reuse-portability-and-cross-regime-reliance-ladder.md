# Controller-map reuse, portability, and cross-regime reliance ladder

## Question in one sentence

Once the archive already knows **who the controller is for a period**, **what packet must be filed**, **who may see it**, **how it is verified**, and **when the result becomes operative**, **what is the smallest workable ladder for deciding when that controller map may be reused across related levies, periods, and authorities instead of being rebuilt from scratch every time?**[S16][S17][S27][S39][S40][S41][S44][S68][S77][S89][S91][S92]

## Companion routes

Use this memo with:

- [`../10-framework/tax-subjecthood-and-liability-routing.md`](../10-framework/tax-subjecthood-and-liability-routing.md)
- [`../10-framework/collection-and-remittance-routing.md`](../10-framework/collection-and-remittance-routing.md)
- [`../10-framework/administration-explanation-and-appeal-routing.md`](../10-framework/administration-explanation-and-appeal-routing.md)
- [`../10-framework/jurisdiction-and-scale-routing.md`](../10-framework/jurisdiction-and-scale-routing.md)
- [`controller-boundary-and-co-controller-ranking-ladder.md`](controller-boundary-and-co-controller-ranking-ladder.md)
- [`controller-map-evidence-presumption-and-burden-shifting-ladder.md`](controller-map-evidence-presumption-and-burden-shifting-ladder.md)
- [`controller-map-minimum-contents-attestation-and-update-cadence-standard.md`](controller-map-minimum-contents-attestation-and-update-cadence-standard.md)
- [`controller-map-visibility-redaction-and-audience-tier-ladder.md`](controller-map-visibility-redaction-and-audience-tier-ladder.md)
- [`controller-map-integrity-correction-safe-harbor-and-sanction-ladder.md`](controller-map-integrity-correction-safe-harbor-and-sanction-ladder.md)
- [`controller-map-verification-sampling-and-review-intensity-ladder.md`](controller-map-verification-sampling-and-review-intensity-ladder.md)
- [`controller-map-contest-window-counter-map-and-finality-ladder.md`](controller-map-contest-window-counter-map-and-finality-ladder.md)
- [`provisional-controller-filing-escrow-and-true-up-ladder.md`](provisional-controller-filing-escrow-and-true-up-ladder.md)
- [`data-minimization-credential-reuse-and-sensitive-attribute-firewall-ladder.md`](data-minimization-credential-reuse-and-sensitive-attribute-firewall-ladder.md)

Route: once a controller map is good enough to govern filing for one period, the default should be **versioned reuse plus delta updates**, not repeated full refiling for every nearby obligation or audience.[S27][S39][S40][S41][S44][S68][S77][S89][S91][S92]

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — fresh full packet everywhere | require a new controller map for each tax, period, and authority even when the governance facts have not materially changed.[S27][S39][S41][S68] | Reject: wastes compliance capacity and rewards paper churn over truth. |
| B — universal passport map | let one controller map bind every levy, period, and authority until someone proves fraud or gross error.[S27][S39][S40][S41][S89] | Reject: treats portability as immunity and ignores changed legal tests or changed facts. |
| C — versioned reuse with same-facts reliance, delta updates, and local overrides | reuse a settled map where the governance facts, period logic, and audience tier stay materially aligned; require a short delta or local addendum when they do not.[S16][S17][S27][S39][S40][S41][S44][S68][S77][S89][S91][S92] | Adopt. |
| D — sealed registry only | centralize all controller maps in one inaccessible vault and force every user to trust the registry output without seeing the operative basis.[S40][S41][S89][S91][S92] | Reject: portability cannot erase contestability or audience-tier rights. |

## Five-rung ladder

1. **versioned-packet lane** — every operative controller map should carry a stable period-bounded identifier, signer, issue date, and revision marker so nearby regimes can tell whether they are looking at the same packet or a later delta.[S27][S39][S41][S68][S89]
2. **same-facts reliance lane** — allow reuse across related taxes, filings, or authorities when the live controller question, the governed stack, the relevant period, and the needed audience tier are materially the same.[S16][S17][S27][S39][S40][S41][S44][S77][S89]
3. **delta-update lane** — when only a narrow fact changes, require a short addendum naming the changed controller event, affected layer, period effect, and whether interim filing or allocation moves, rather than rebuilding the whole packet.[S27][S39][S41][S68][S77][S89]
4. **local-override lane** — when a levy or authority has a genuinely different legal test, secrecy posture, or period cut, allow a compact local override or supplement instead of treating prior portability as dispositive.[S20][S27][S39][S40][S41][S44][S83]
5. **anti-lock-in lane** — portability never outranks integrity, preservation, verification, contestability, or material-change reopening; stale, false, strategically partial, or improperly redacted packets lose reuse privileges first.[S16][S17][S20][S27][S39][S40][S41][S44][S89][S91][S92]

## Provisional recommendation

Adopt **Option C — versioned reuse with same-facts reliance, delta updates, and local overrides** as the archive's default portability rule for controller maps.[S16][S17][S27][S39][S40][S41][S44][S68][S77][S89][S91][S92]

Presumption:

- once a controller map is operative for a period, nearby obligations should usually **reuse** it rather than demand a clean-sheet refiling,
- reuse should depend on **same facts, same governed stack, same relevant period logic, and compatible audience tier**, not on mere administrative convenience,
- material factual change should trigger a **delta packet** first,
- materially different legal tests or secrecy needs should trigger a **local addendum or override** rather than a universal passport effect,
- and any packet that fails the archive's integrity, preservation, verification, or reopening rules should lose easy portability before it can contaminate multiple regimes.

This is the archive's narrowest workable setting because it captures the administrative gain from standard packets and credential reuse without turning the first controller map into a cross-regime shield against correction, contest, or better fit.

## Default portability matrix

| Live posture | Default action | Why it usually fits | Archive warning |
|---|---|---|---|
| same deployment, same period, related tax or filing channel | reuse the operative packet id | duplicate packeting adds cost but little truth.[S27][S39][S41][S68][S89] | do not treat channel reuse as audience-tier clearance. |
| same controller story, later nearby period, no material governance change | reuse plus short no-change attestation | most periods differ less than they resemble each other.[S27][S39][S41][S68][S77] | do not let rote attestations hide obvious drift. |
| same stack but named governance event, successor step, or controller-share shift | delta update | the archive needs the changed fact, not a whole rebuilt history.[S16][S17][S20][S27][S39][S41] | if the change is actually foundational, escalate beyond delta form. |
| different authority or levy with a narrower or different test | local supplement or override | portability should reduce duplication, not flatten legal difference.[S20][S27][S39][S40][S41][S44][S83] | do not export one regime's closure point as automatic closure everywhere else. |
| stale, false, or strategically partial packet | deny reliance and reopen | bad portability spreads bad controller answers.[S16][S17][S27][S39][S40][S41][S89][S91][S92] | portability privileges should be among the first things lost. |

## Anti-patterns

- **passport absolutism** — one controller map is treated as binding everywhere even though the later levy or period asks a different question.[S20][S27][S39][S41]
- **refile theater** — authorities demand new full packets simply because they can, not because any material fact or legal test changed.[S27][S39][S41][S68][S77]
- **delta laundering** — foundational controller changes are mislabeled as tiny supplements to avoid new review.[S16][S17][S20][S27][S39][S41]
- **hidden portability** — a packet is silently reused against affected parties who never received the audience-tier access needed to contest it.[S40][S41][S44][S91][S92]
- **contamination by bad packet** — a stale or false controller map is allowed to propagate across regimes before integrity checks run.[S16][S17][S27][S39][S40][S41][S89]

## What would change the recommendation

Tighten, loosen, or replace this ladder if:

- controller-map identifiers, attestations, or reusable credentials become much more interoperable across authorities than the archive now assumes,
- privacy-preserving federation makes same-facts reliance safer and easier than current packet exchange,
- cross-border co-ordination creates a narrower common controller-map standard across several regimes,
- or repeated experience shows that local overrides are either too generous and fragment the map or too stingy and export one regime's answer too broadly.[S27][S39][S40][S41][S44][S68][S77][S89][S91][S92]

## Source IDs only

[S16][S17][S20][S27][S39][S40][S41][S44][S68][S77][S83][S89][S91][S92]

[S16]: ../../SOURCES.md#S16
[S17]: ../../SOURCES.md#S17
[S20]: ../../SOURCES.md#S20
[S27]: ../../SOURCES.md#S27
[S39]: ../../SOURCES.md#S39
[S40]: ../../SOURCES.md#S40
[S41]: ../../SOURCES.md#S41
[S44]: ../../SOURCES.md#S44
[S68]: ../../SOURCES.md#S68
[S77]: ../../SOURCES.md#S77
[S83]: ../../SOURCES.md#S83
[S89]: ../../SOURCES.md#S89
[S91]: ../../SOURCES.md#S91
[S92]: ../../SOURCES.md#S92
