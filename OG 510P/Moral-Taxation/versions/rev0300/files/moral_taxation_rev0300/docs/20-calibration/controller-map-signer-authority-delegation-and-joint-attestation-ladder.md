# Controller-map signer authority, delegation, and joint-attestation ladder

## Question in one sentence

Once the archive already knows **who owes a controller map**, **what the minimum packet contains**, and **how packet identity and portability work**, **what is the smallest workable rule for deciding who may honestly sign the map, when an authorized representative is enough, and when shared control requires co-attestation instead of one convenience signer standing in for everyone?**[S16][S17][S20][S21][S27][S34][S35][S39][S40][S41][S83][S89][S91][S92]

## Companion routes

Use this memo with:

- [`../10-framework/tax-subjecthood-and-liability-routing.md`](../10-framework/tax-subjecthood-and-liability-routing.md)
- [`../10-framework/collection-and-remittance-routing.md`](../10-framework/collection-and-remittance-routing.md)
- [`../10-framework/administration-explanation-and-appeal-routing.md`](../10-framework/administration-explanation-and-appeal-routing.md)
- [`controller-boundary-and-co-controller-ranking-ladder.md`](controller-boundary-and-co-controller-ranking-ladder.md)
- [`controller-map-minimum-contents-attestation-and-update-cadence-standard.md`](controller-map-minimum-contents-attestation-and-update-cadence-standard.md)
- [`controller-map-visibility-redaction-and-audience-tier-ladder.md`](controller-map-visibility-redaction-and-audience-tier-ladder.md)
- [`controller-map-verification-sampling-and-review-intensity-ladder.md`](controller-map-verification-sampling-and-review-intensity-ladder.md)
- [`controller-map-packet-identity-canonical-fields-and-supersession-ladder.md`](controller-map-packet-identity-canonical-fields-and-supersession-ladder.md)
- [`provisional-controller-filing-escrow-and-true-up-ladder.md`](provisional-controller-filing-escrow-and-true-up-ladder.md)

Route: a controller map should be signed by the **smallest accountable set of actors who can honestly attest to the decisive governance facts** for the layer at issue. Do not force universal co-signing, but do not let a thin filer, preparer, or interface signer replace principals who actually hold the relevant levers.[S20][S21][S27][S34][S35][S39][S41][S83][S89][S91][S92]

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — convenience-signer lane | let any visible filer, reseller, vendor, or preparer sign as long as someone signs.[S21][S27][S39][S41] | Reject: makes paper custody too close to moral attestation. |
| B — universal co-sign lane | require every materially involved actor to sign every controller map.[S20][S21][S27][S34][S35][S41][S83] | Reject: overstates jointness and turns routine filing into coalition theater. |
| C — decisive-lever signer lane with bounded delegation and co-sign triggers | prefer one accountable signer who can attest to the decisive governance facts; allow authorized representatives when authority basis is named; require co-attestation only when no single signer honestly spans the decisive levers or controller shares in dispute.[S16][S17][S20][S21][S27][S34][S35][S39][S40][S41][S83][S89][S91][S92] | Adopt. |
| D — sealed-registry proxy lane | let a central registry sign or bless controller maps in place of the actors who actually know the facts.[S27][S39][S40][S41][S89][S91][S92] | Reject: portability and identity do not let official paperwork replace situated responsibility. |

## Five-rung ladder

1. **single accountable signer lane** — default to one signer when one person or office can honestly attest to the decisive governance levers, residual upside / downside, and update triggers for the mapped layer.[S20][S21][S27][S39][S41][S83]
2. **authority-basis lane** — every signer should state why they may sign: direct executive authority, designated controller-group office, delegated filing authority, fiduciary mandate, or comparable basis tied to the named packet family and period.[S21][S27][S34][S35][S39][S41][S89]
3. **bounded representative lane** — allow an authorized representative, managed-service filer, or counsel to sign only if the packet also names the principal or principals for whom the signer speaks and preserves a reachable authority chain; representative signature is filing machinery, not moral substitution.[S21][S27][S34][S35][S39][S41][S83][S89][S91][S92]
4. **co-attestation trigger lane** — require co-signing when decisive governance facts are genuinely split across actors or offices so that no one signer can honestly attest to mission control, continuation power, or controller shares without another actor's confirmation.[S16][S17][S20][S21][S27][S34][S35][S41][S83]
5. **anti-fronting lane** — reject packets signed only by preparers, nominees, thin resellers, outside interfaces, or other actors chosen mainly because they are visible, solvent, or convenient rather than because they can truly attest to the mapped control facts.[S20][S21][S27][S34][S35][S39][S41][S83]

## Provisional recommendation

Adopt **Option C — decisive-lever signer lane with bounded delegation and co-sign triggers** as the archive's default attestation rule for controller maps.[S16][S17][S20][S21][S27][S34][S35][S39][S40][S41][S83][S89][S91][S92]

Presumption:

- if one actor or office can honestly attest to the decisive control facts, use **one accountable signer**,
- every packet should name the signer's **authority basis**,
- an authorized representative may sign as filing machinery only when the represented principal remains named and reachable,
- require **co-attestation** only when real shared control or split knowledge makes one honest signer impossible,
- and treat convenience signers chosen for visibility, asset location, or collection ease as a warning sign for fronting rather than a cure for uncertainty.

This is the archive's narrowest workable setting because it keeps controller maps reviewable and attributable without collapsing into either false singularity or mandatory everyone-signs ritual.

## Default signer matrix

| Live posture | Default signer rule | Why it usually fits | Archive warning |
|---|---|---|---|
| one controller or one controller-group office clearly spans the decisive levers | one accountable signer | one real attestor is better than a coalition of decorative signatures.[S20][S21][S27][S39][S41] | do not confuse filing convenience with attestation authority. |
| principal uses counsel, preparer, or managed-service filer | representative may sign only with named principal and authority basis | representation can reduce friction without hiding who actually knows and governs.[S21][S27][S39][S41][S89][S91][S92] | representative signature alone should not sever the authority chain. |
| controller group, consortium, or split governance stack where mission control and continuation power sit in different hands | co-attestation | no single signer can honestly cover the decisive facts alone.[S16][S17][S20][S21][S27][S34][S35][S41][S83] | do not demand every peripheral actor join the packet. |
| emergency step-in, successor handoff, or temporary receiver governance | transitional signer plus predecessor / successor link where reachable | continuity matters more than paper reset.[S16][S17][S20][S21][S27][S39][S41][S83] | do not let a temporary signer erase the longer control chain. |
| packet signed only by reseller, channel intermediary, preparer, or nominal operator | reject as fronting unless real authority is shown | visible interfaces often know too little about decisive governance.[S20][S21][S27][S34][S35][S39][S41][S83] | convenience should not become moral substitution. |

## Anti-patterns

- **signature theater** — collecting many signatures that do not add real attestive knowledge.[S20][S21][S27][S41]
- **representative laundering** — using counsel, preparers, or managed-service filers to hide the principal who actually governs the layer.[S21][S27][S34][S35][S39][S41][S83]
- **single-signer fiction** — forcing one actor to attest to control facts that are genuinely split across a controller group or across successor / step-in periods.[S16][S17][S20][S21][S27][S41][S83]
- **outside-interface substitution** — choosing the signer because the actor is easy to find, wealthy, or already remits, even though it does not actually hold the decisive levers.[S20][S21][S27][S34][S35][S39][S41][S83]
- **orphan attestation** — the packet is signed, but no authority basis, represented principal, or reachable office is named for correction or contest.[S21][S27][S39][S41][S89][S91][S92]

## What would change the recommendation

Tighten, loosen, or replace this ladder if:

- privacy-preserving delegated credentials make representative signing safer and more reviewable than the archive now assumes,
- controller groups routinely need a more formal lead-signer / co-signer grammar than a simple authority-basis rule,
- repeated disputes show that one accountable signer is usually too narrow for real split-governance stacks,
- or interoperable attestation systems can bind signer authority to packet families and revocation status without adding surveillance or exclusion risk.[S16][S17][S21][S27][S34][S35][S39][S40][S41][S83][S89][S91][S92]

## Source IDs only

[S16][S17][S20][S21][S27][S34][S35][S39][S40][S41][S83][S89][S91][S92]

[S16]: ../../SOURCES.md#S16
[S17]: ../../SOURCES.md#S17
[S20]: ../../SOURCES.md#S20
[S21]: ../../SOURCES.md#S21
[S27]: ../../SOURCES.md#S27
[S34]: ../../SOURCES.md#S34
[S35]: ../../SOURCES.md#S35
[S39]: ../../SOURCES.md#S39
[S40]: ../../SOURCES.md#S40
[S41]: ../../SOURCES.md#S41
[S83]: ../../SOURCES.md#S83
[S89]: ../../SOURCES.md#S89
[S91]: ../../SOURCES.md#S91
[S92]: ../../SOURCES.md#S92
