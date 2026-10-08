# Controller-map packet identity, canonical fields, and supersession ladder

## Question in one sentence

Once the archive already knows **who owes a controller map**, **what it must contain**, **how it is verified**, and **when a settled map may be reused**, **what is the smallest workable rule for deciding when two filings are really the same packet family, when a short delta is enough, and when a fresh superseding packet must issue so portability does not collapse into filename theater or orphaned update chains?**[S16][S17][S21][S27][S39][S40][S41][S44][S68][S89][S91][S92]

## Companion routes

Use this memo with:

- [`../10-framework/tax-subjecthood-and-liability-routing.md`](../10-framework/tax-subjecthood-and-liability-routing.md)
- [`../10-framework/collection-and-remittance-routing.md`](../10-framework/collection-and-remittance-routing.md)
- [`../10-framework/administration-explanation-and-appeal-routing.md`](../10-framework/administration-explanation-and-appeal-routing.md)
- [`controller-boundary-and-co-controller-ranking-ladder.md`](controller-boundary-and-co-controller-ranking-ladder.md)
- [`controller-map-minimum-contents-attestation-and-update-cadence-standard.md`](controller-map-minimum-contents-attestation-and-update-cadence-standard.md)
- [`controller-map-integrity-correction-safe-harbor-and-sanction-ladder.md`](controller-map-integrity-correction-safe-harbor-and-sanction-ladder.md)
- [`controller-map-verification-sampling-and-review-intensity-ladder.md`](controller-map-verification-sampling-and-review-intensity-ladder.md)
- [`controller-map-contest-window-counter-map-and-finality-ladder.md`](controller-map-contest-window-counter-map-and-finality-ladder.md)
- [`controller-map-reuse-portability-and-cross-regime-reliance-ladder.md`](controller-map-reuse-portability-and-cross-regime-reliance-ladder.md)

Route: portability only works if the archive can tell whether a later filing is the **same controller-map family**, a **bounded delta**, or a **new superseding packet**. This memo sets that identity and lineage rule without turning controller maps into a general-purpose tracking registry.[S16][S17][S21][S27][S39][S40][S41][S44][S68][S89][S91][S92]

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — filename and date convention only | treat packet identity as whatever the filer calls the file or whichever statement was uploaded last.[S21][S27][S39][S41] | Reject: invites silent drift, duplicate packets, and fake portability. |
| B — append-only full-refile chain | require every small correction or period update to ship as a complete new packet with no reusable parent or delta logic.[S21][S27][S39][S41][S68][S89] | Reject: too bulky, too repetitive, and too easy to make unreadable. |
| C — stable packet family id plus canonical core, bounded deltas, and explicit supersession | keep a stable family id for the same governed layer and legal test, require a small canonical field set, allow short deltas for bounded changes, and require a clearly linked superseding packet for material changes.[S16][S17][S21][S27][S39][S40][S41][S44][S68][S89][S91][S92] | Adopt. |
| D — delta-only portability | let later users rely on chains of tiny updates without any clear parent snapshot or superseding reset point.[S21][S27][S39][S41][S68][S89] | Reject: creates orphaned update braids and defeats review. |

## Five-rung ladder

1. **packet-family lane** — assign one stable controller-map family id only when the governed layer, governing legal test, responsible filer set, and audience tier family are materially the same across periods.[S21][S27][S39][S41][S68][S89]
2. **canonical-core lane** — every packet in that family should carry a small canonical core: family id, packet id, schema version, effective period, audience tier, signer, parent pointer if any, and an explicit status of original, delta, superseding, or withdrawn.[S16][S17][S21][S27][S39][S40][S41][S44][S68][S89][S91][S92]
3. **bounded-delta lane** — use a short delta only for no-change attestations, changed dates, corrected redactions, narrow actor-role edits, or other bounded updates that do not materially alter the controller ranking story or the governing legal test.[S16][S17][S21][S27][S39][S40][S41][S68][S89]
4. **supersession lane** — require a fresh superseding packet when mission scope, governed layer, controller group composition, audience tier logic, material redaction posture, or governing legal test changes enough that the old packet is no longer a stable review object.[S16][S17][S21][S27][S39][S40][S41][S44][S68][S89][S91][S92]
5. **lineage lane** — keep a compact lineage pointer from every live packet to its operative predecessor and to the latest operative packet in the family so reuse, verification, contest, and preservation never depend on guessing which file is current.[S21][S27][S39][S40][S41][S68][S89]

## Provisional recommendation

Adopt **Option C — stable packet family id plus canonical core, bounded deltas, and explicit supersession** as the archive's default packet-identity rule for controller maps.[S16][S17][S21][S27][S39][S40][S41][S44][S68][S89][S91][S92]

Presumption:

- the archive should reuse a controller map only when it can say **same governed object, same test, same packet family**, 
- every packet should expose a **small canonical identity core** before any detailed content is considered,
- minor period or correction changes should travel as **bounded deltas** rather than repeated full refiles,
- material governance, audience, or legal-test changes should trigger a **fresh superseding packet**,
- and lineage should stay **compact and explicit** so packet portability never depends on a long guesswork chain.

This is the narrowest workable rule because it lets settled maps travel without turning portability into a free-form paperwork game, while also preventing a technically valid but unreadable history from substituting for an operative current answer.

## Default identity matrix

| Live posture | Default packet answer | Why it usually fits | Archive warning |
|---|---|---|---|
| same layer, same legal test, same audience family, no governance change | reuse family id with no-change or tiny delta packet.[S21][S27][S39][S41][S68][S89] | most nearby periods should not require full refiling. | do not issue a new family just to hide continuity. |
| corrected date, signer, redaction note, or narrow role label | bounded delta packet.[S16][S17][S21][S27][S39][S40][S41] | the packet family is stable even though a field changed. | do not let deltas quietly rewrite the whole controller story. |
| added or removed material controller, successor, or step-in actor | superseding packet in same family or a new family if the governed layer changed.[S16][S17][S21][S27][S39][S40][S41][S44] | the review object changed materially. | say clearly whether this supersedes, withdraws, or forks the prior answer. |
| new legal regime, materially different audience tier logic, or changed governed layer | fresh family id and superseding packet.[S21][S27][S39][S40][S41][S68][S89][S91][S92] | portability across unlike tests needs an explicit reset. | do not pretend cross-regime reuse is the same as same-regime continuity. |
| long delta braid with no clear operative current packet | force compaction into a fresh superseding packet.[S21][S27][S39][S41][S68][S89] | review and reliance need a readable current object. | delta chains should not become a substitute for clarity. |

## Failure-mode capsule

Cube anti-pattern axes: `classification_or_label_arbitrage`.
Use this controlled axis packet instead of a second local anti-pattern taxonomy; add only route-specific exceptions in the ladder or recommendation text.
Source continuity: [S16][S17][S21][S27][S39][S40][S41][S68][S89][S91][S92]

## Recalibration trigger capsule

Cube review-trigger axes: `controller_or_accountability_drift`.
Reopen the route when those triggers materially change controller identity, control evidence, protected burden, contest access, or fallback duty.
Source continuity: [S16][S17][S21][S27][S39][S40][S41][S68][S89][S91][S92]

## Accountability capsule

Profile: `controller_map_packet_identity_canonical_fields_and_supersession` in `docs/00-meta/actor-accountability-profiles.json`. Duty owner: `controller_map_packet_issuer_and_registry_maintaining_canonical_identity_and_supersession`. Benefit/rent trace: `actor_benefiting_from_duplicate_packets_version_confusion_or_unmarked_supersession`.
Bottleneck/evidence start: `controller_map_registry`; `packet_identifier_channel`; `supersession_notice_channel`; `controller_map_packet_identifier_period_and_layer_record`; `canonical_field_set_and_hash_or_version_record`; `supersession_delta_and_successor_notice_record`. Fallback: `public_body_must_preserve_no_rent_fallback_notice_cure_and_nonforfeiture_when_packet_identity_confusion_affects_tax_rights`.
Source continuity: [S16][S17][S21][S27][S39][S40][S41][S44][S68][S89][S91][S92]

## Source IDs only

[S16][S17][S21][S27][S39][S40][S41][S44][S68][S89][S91][S92]

[S16]: ../../SOURCES.md#S16
[S17]: ../../SOURCES.md#S17
[S21]: ../../SOURCES.md#S21
[S27]: ../../SOURCES.md#S27
[S39]: ../../SOURCES.md#S39
[S40]: ../../SOURCES.md#S40
[S41]: ../../SOURCES.md#S41
[S44]: ../../SOURCES.md#S44
[S68]: ../../SOURCES.md#S68
[S89]: ../../SOURCES.md#S89
[S91]: ../../SOURCES.md#S91
[S92]: ../../SOURCES.md#S92
