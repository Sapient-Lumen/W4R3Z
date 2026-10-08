# Controller-map field severability, partial acceptance, and issue-scoped correction ladder

## Question in one sentence

Once the archive already knows **how to rank controllers**, **what a controller map must contain**, **how confidence and imputation work**, **how review and contest operate**, and **when a packet becomes final for a period**, **what is the smallest workable rule for accepting settled controller-map fields while correcting only the disputed issue instead of treating every contradiction as a reason to reopen the whole packet?**[S16][S17][S20][S21][S27][S39][S40][S41][S83][S89][S91][S92]

## Companion routes

Use this memo with:

- [`../10-framework/tax-subjecthood-and-liability-routing.md`](../10-framework/tax-subjecthood-and-liability-routing.md)
- [`../10-framework/collection-and-remittance-routing.md`](../10-framework/collection-and-remittance-routing.md)
- [`../10-framework/administration-explanation-and-appeal-routing.md`](../10-framework/administration-explanation-and-appeal-routing.md)
- [`controller-boundary-and-co-controller-ranking-ladder.md`](controller-boundary-and-co-controller-ranking-ladder.md)
- [`controller-map-minimum-contents-attestation-and-update-cadence-standard.md`](controller-map-minimum-contents-attestation-and-update-cadence-standard.md)
- [`controller-map-confidence-unknowns-and-bounded-imputation-ladder.md`](controller-map-confidence-unknowns-and-bounded-imputation-ladder.md)
- [`controller-map-verification-sampling-and-review-intensity-ladder.md`](controller-map-verification-sampling-and-review-intensity-ladder.md)
- [`controller-map-contest-window-counter-map-and-finality-ladder.md`](controller-map-contest-window-counter-map-and-finality-ladder.md)
- [`controller-map-packet-identity-canonical-fields-and-supersession-ladder.md`](controller-map-packet-identity-canonical-fields-and-supersession-ladder.md)

Route: controller-map review should usually be **issue-scoped and severable**. A real error in one field should correct that field, any tightly coupled consequences, and the packet version going forward — not silently poison every settled field or force a needless full rehearing.[S16][S17][S20][S21][S27][S39][S40][S41][S83][S89][S91][S92]

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — all-or-nothing packet lane | any material dispute reopens the entire controller map.[S16][S17][S20][S21][S27][S39][S41] | Reject: too much closure is lost when one field is wrong. |
| B — silent cherry-pick lane | reviewers may keep whichever fields they like without naming which parts were accepted, rejected, or left provisional.[S20][S21][S27][S39][S41][S89] | Reject: obscures what was actually decided. |
| C — severable issue-scoped lane | accept settled fields, correct the disputed field and any tightly coupled consequences, and issue a delta or superseding packet only where the dependency graph requires it.[S16][S17][S20][S21][S27][S39][S40][S41][S83][S89][S91][S92] | Adopt. |
| D — perpetual global provisionality lane | keep the whole map provisional until no objection remains anywhere.[S16][S17][S20][S27][S39][S40][S41] | Reject: turns narrow dispute into chronic non-finality. |

## Five-rung ladder

1. **field-scoping lane** — objections, counter-maps, and review findings should identify the disputed field, edge, or issue rather than attacking the packet in the abstract.[S16][S17][S20][S21][S27][S39][S41][S89]
2. **severability presumption lane** — when one controller-map element is contested, presume other fields remain operative unless the challenger names a real dependency that makes them unstable too.[S16][S17][S20][S21][S27][S39][S40][S41]
3. **coupling lane** — if the disputed field changes controller ranking, group membership, remittance share, or period finality for another field, reopen only that coupled subset rather than the whole map.[S16][S17][S20][S21][S27][S39][S40][S41][S83]
4. **partial-correction lane** — corrections should travel by delta or scoped supersession when possible; reserve full packet replacement for cases where the canonical identity fields themselves have changed.[S16][S17][S21][S27][S39][S40][S41][S89][S91][S92]
5. **scoped-finality lane** — once the contested issue is resolved, harden finality only for the accepted and corrected fields at issue, while leaving independently open matters open on their own clock.[S16][S17][S20][S21][S27][S39][S40][S41][S83]

## Provisional recommendation

Adopt **Option C — severable issue-scoped lane** as the archive's default correction rule for controller maps.[S16][S17][S20][S21][S27][S39][S40][S41][S83][S89][S91][S92]

Presumption:

- controller-map objections should name a field, edge, period, or dependency rather than merely alleging that the packet is "wrong",
- accepted fields should stay accepted unless a real coupling reason is shown,
- correction should usually move by issue-scoped delta or partial supersession,
- full rehearing belongs to canonical-identity change, broad integrity failure, or dense interdependence rather than to ordinary field error,
- and finality should harden at the smallest issue-set that can honestly be treated as settled.

This is the archive's narrowest workable setting because it preserves closure and reuse where the map is already good while still allowing genuine corrections to propagate where they matter.

## Default handling matrix

| Live posture | Default handling | Why it usually fits | Archive warning |
|---|---|---|---|
| one disputed field, no shown dependence | partial correction only | most controller-map errors are local rather than packet-wide.[S16][S17][S20][S21][S27][S39][S41] | do not reopen settled fields out of habit. |
| one field changes ranking or controller-group share across linked fields | reopen the coupled subset | some map elements really do move together.[S16][S17][S20][S21][S27][S39][S40][S41][S83] | name the dependency; do not invoke coupling as a slogan. |
| canonical packet identity or period anchor changes | superseding packet | the packet family itself has changed.[S16][S17][S21][S27][S39][S40][S41][S89][S91][S92] | use full replacement only when identity or scope truly moved. |
| broad stale / false / sham-redacted map | wider reopening plus harder presumptions | integrity failure can infect more than one field.[S16][S17][S20][S21][S27][S39][S40][S41][S83] | distinguish broad corruption from an honest local mistake. |
| challenger names only vague discomfort with no field-level objection | keep accepted fields operative | contest rights do not require abstract packet destabilization.[S16][S17][S20][S21][S27][S39][S41] | require pointed objection, not mood. |

## Failure-mode capsule

Cube anti-pattern axes: `classification_or_label_arbitrage`.
Use this controlled axis packet instead of a second local anti-pattern taxonomy; add only route-specific exceptions in the ladder or recommendation text.
Source continuity: [S16][S17][S20][S21][S27][S39][S40][S41][S89][S91][S92]

## Recalibration trigger capsule

Cube review-trigger axes: `controller_or_accountability_drift`.
Reopen the route when those triggers materially change controller identity, control evidence, protected burden, contest access, or fallback duty.
Source continuity: [S16][S17][S20][S21][S27][S39][S40][S41][S83][S89][S91][S92]

## Accountability capsule

Profile: `controller_map_field_severability_partial_acceptance_and_issue_scoped_correction` in `docs/00-meta/actor-accountability-profiles.json`. Duty owner: `controller_map_reviewer_and_field_owner_controlling_issue_scoped_correction`. Benefit/rent trace: `actor_benefiting_from_reopening_whole_packet_to_delay_correction_or_from_freezing_false_field_in_place`.
Bottleneck/evidence start: `controller_map_correction_channel`; `field_owner_record_holder`; `review_authority`; `controller_map_field_identity_and_version_record`; `partial_acceptance_or_dispute_scope_record`; `field_owner_source_record_and_correction_proof`. Fallback: `public_body_must_preserve_no_rent_fallback_notice_cure_and_nonforfeiture_for_issue_scoped_controller_map_correction`.
Source continuity: [S16][S17][S20][S21][S27][S39][S40][S41][S83][S89][S91][S92]

## Source IDs only

[S16][S17][S20][S21][S27][S39][S40][S41][S83][S89][S91][S92]

[S16]: ../../SOURCES.md#S16
[S17]: ../../SOURCES.md#S17
[S20]: ../../SOURCES.md#S20
[S21]: ../../SOURCES.md#S21
[S27]: ../../SOURCES.md#S27
[S39]: ../../SOURCES.md#S39
[S40]: ../../SOURCES.md#S40
[S41]: ../../SOURCES.md#S41
[S83]: ../../SOURCES.md#S83
[S89]: ../../SOURCES.md#S89
[S91]: ../../SOURCES.md#S91
[S92]: ../../SOURCES.md#S92
