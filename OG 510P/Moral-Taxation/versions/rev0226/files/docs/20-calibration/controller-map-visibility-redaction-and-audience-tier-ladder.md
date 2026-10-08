# Controller-map visibility, redaction, and audience-tier ladder

## Question in one sentence

Once the archive already knows **who owes a controller map**, **what that packet must contain**, and **how interim filing proceeds while disputes remain open**, **what is the smallest workable ladder for deciding which parts of the controller map must be public, which may stay regulator-private or court-sealed, when redaction is justified, and when secrecy claims should fail because they hide the very governance facts needed to assign controller-side duties?**[S16][S17][S20][S21][S27][S39][S40][S41][S83]

## Companion routes

Use this memo with:

- [`../10-framework/tax-subjecthood-and-liability-routing.md`](../10-framework/tax-subjecthood-and-liability-routing.md)
- [`../10-framework/collection-and-remittance-routing.md`](../10-framework/collection-and-remittance-routing.md)
- [`../10-framework/administration-explanation-and-appeal-routing.md`](../10-framework/administration-explanation-and-appeal-routing.md)
- [`../10-framework/enforcement-proportionality-and-recovery-routing.md`](../10-framework/enforcement-proportionality-and-recovery-routing.md)
- [`controller-map-evidence-presumption-and-burden-shifting-ladder.md`](controller-map-evidence-presumption-and-burden-shifting-ladder.md)
- [`controller-map-minimum-contents-attestation-and-update-cadence-standard.md`](controller-map-minimum-contents-attestation-and-update-cadence-standard.md)
- [`provisional-controller-filing-escrow-and-true-up-ladder.md`](provisional-controller-filing-escrow-and-true-up-ladder.md)
- [`data-minimization-credential-reuse-and-sensitive-attribute-firewall-ladder.md`](data-minimization-credential-reuse-and-sensitive-attribute-firewall-ladder.md)

Route: controller maps should be **disclosure-bounded and reviewable**. The archive should expose enough to assign real controller duties and let affected parties contest them, but should not turn controller proof into a universal publication mandate for exploit-ready security detail, personal data, or unrelated commercial paperwork.[S16][S17][S21][S27][S39][S40][S41]

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — full public data-room lane | publish the whole controller packet, contracts, and operational details to anyone by default.[S16][S17][S39][S40][S41] | Reject: too privacy-costly, too security-costly, and too easy to repurpose into broad surveillance or exploit assistance. |
| B — secrecy-by-assertion lane | let filers hide most of the packet whenever they invoke confidentiality, trade secrecy, or security.[S21][S27][S39][S41] | Reject: invites controller laundering by redaction and leaves outsiders unable to contest the real governance story. |
| C — audience-tier disclosure with bounded redaction | require a short public or affected-party-facing summary, a regulator-private full packet, and sealed escalation only for truly sensitive detail, with reviewable redaction claims.[S16][S17][S20][S21][S27][S39][S40][S41][S83] | Adopt. |
| D — regulator-only black box lane | allow filing to the state alone, with no short summary or contestable disclosure for affected parties.[S21][S27][S39][S41] | Reject: too much hidden assignment power and too little contestability. |

## Five audience tiers

1. **public gist lane** — disclose the layer being mapped, the filing entity, the asserted primary controller or controller group, any claimed co-controller lanes, the signer, and the relevant period in short form.[S20][S21][S27][S41]
2. **affected-party summary lane** — where liability, escrow, or remedial claims turn on the map, disclose enough additional role detail for affected parties to contest the controller story without needing the full private packet.[S16][S17][S21][S27][S39][S41][S83]
3. **regulator-private packet lane** — give the competent authority the full minimum controller packet, including governance levers, residual upside / downside, and key interfaces, subject to ordinary confidentiality and misuse limits.[S16][S17][S20][S21][S27][S39][S40][S41]
4. **sealed-review lane** — hold genuinely exploit-sensitive or unrelated third-party-confidential details under sealed judicial or equivalent supervised review rather than ordinary circulation.[S16][S17][S27][S39][S40][S41]
5. **fail-open-on-governance-facts lane** — if secrecy claims hide the very facts needed to test governance, continuation power, residual upside, or controller-group membership, the archive should deny the redaction, require a cleaner summary, or draw an adverse inference rather than accept opacity.[S20][S21][S27][S39][S41][S83]

## Provisional recommendation

Adopt **Option C — audience-tier disclosure with bounded redaction** as the archive's default controller-map visibility rule.[S16][S17][S20][S21][S27][S39][S40][S41][S83]

Default posture:

- the world does **not** get a universal controller data-room,
- affected parties should still get a **contestable summary** when liability, escrow, or remedial position depends on the map,
- the competent authority gets the **full bounded packet**,
- sealed review is for genuinely sensitive operational or third-party detail,
- and no filer may use confidentiality language to hide the facts that actually settle controller status.

This is the archive's narrowest workable compromise because it preserves both **proof discipline** and **data minimization**. It also blocks a familiar failure mode: controller actors claiming that the packet exists, but that almost all of it is too sensitive for anyone else to see or challenge.

## Default disclosure table

| Information type | Default audience | Why | Archive warning |
|---|---|---|---|
| layer, filer, asserted controller, signer, period | public gist | basic contestability and filing legibility.[S20][S21][S27][S41] | do not let the gist shrink into a meaningless entity name and date stamp. |
| role summary for key interfaces and claimed co-controllers | affected-party summary | lets real challengers contest the map without bulk document disclosure.[S16][S17][S21][S27][S39][S41] | avoid vague labels like “platform” or “affiliate” where controller roles are disputed. |
| detailed governance levers, residual upside / downside, update triggers | regulator-private packet | enough detail for real ranking, proof, and interim filing decisions.[S16][S17][S20][S21][S27][S39][S40][S41] | keep the packet purpose-bounded; do not let it become a general surveillance file. |
| exploit-sensitive commands, credentials, or unrelated third-party secrets | sealed review | preserves safety and confidentiality without surrendering adjudicative access.[S16][S17][S27][S39][S40][S41] | sealed treatment must stay exceptional and reviewable, not the ordinary lane. |
| facts central to controller assignment | fail-open against secrecy | governance facts cannot be redacted away without defeating the whole controller map regime.[S20][S21][S27][S39][S41][S83] | do not honor secrecy claims that erase who can start, stop, approve, or continue the activity. |

## Anti-patterns

- **confidentiality theater** — asserting secrecy in order to avoid naming who really governs the layer.[S21][S27][S39][S41]
- **public-summary emptiness** — releasing a gist so thin that no one can tell whether the map is contestable.[S20][S21][S27][S41]
- **regulator-only invisibility** — giving the state the whole story while affected parties must litigate blind.[S16][S17][S21][S39][S41][S83]
- **security pretext overreach** — treating ordinary commercial embarrassment or bargaining sensitivity as if it were exploit-sensitive operational detail.[S16][S17][S27][S39][S40][S41]
- **sealed-everything drift** — normalizing sealed review until the audience-tier system collapses into secrecy-by-default.[S21][S27][S39][S41]

## What would change the recommendation

Tighten, loosen, or replace this ladder if:

- privacy-preserving credentials or verifiable attestations can expose controller facts without revealing much of the underlying packet,
- affected-party summaries prove either too thin for meaningful contest or too thick for justified confidentiality,
- real systems show that regulator-private packets are routinely being repurposed beyond controller assignment,
- or adversaries can reliably exploit the disclosure lanes in ways the archive now underestimates.[S16][S17][S21][S27][S39][S40][S41][S83]

## Source IDs only

[S16][S17][S20][S21][S27][S39][S40][S41][S83]

[S16]: ../../SOURCES.md#S16
[S17]: ../../SOURCES.md#S17
[S20]: ../../SOURCES.md#S20
[S21]: ../../SOURCES.md#S21
[S27]: ../../SOURCES.md#S27
[S39]: ../../SOURCES.md#S39
[S40]: ../../SOURCES.md#S40
[S41]: ../../SOURCES.md#S41
[S83]: ../../SOURCES.md#S83
