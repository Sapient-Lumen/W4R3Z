# Controller-map minimum contents, attestation, and update-cadence standard

## Question in one sentence

Once the archive already knows that the best-informed actor owes a **short controller map**, **what is the smallest workable disclosure standard for what that map must contain, who should attest to it, and when it must be updated so controller disputes can be resolved without either blind trust or surveillance-heavy discovery?**[S16][S17][S20][S21][S27][S34][S35][S39][S40][S41][S83]

## Companion routes

Use this memo with:

- [`../10-framework/tax-subjecthood-and-liability-routing.md`](../10-framework/tax-subjecthood-and-liability-routing.md)
- [`../10-framework/collection-and-remittance-routing.md`](../10-framework/collection-and-remittance-routing.md)
- [`../10-framework/administration-explanation-and-appeal-routing.md`](../10-framework/administration-explanation-and-appeal-routing.md)
- [`../10-framework/enforcement-proportionality-and-recovery-routing.md`](../10-framework/enforcement-proportionality-and-recovery-routing.md)
- [`controller-boundary-and-co-controller-ranking-ladder.md`](controller-boundary-and-co-controller-ranking-ladder.md)
- [`controller-map-evidence-presumption-and-burden-shifting-ladder.md`](controller-map-evidence-presumption-and-burden-shifting-ladder.md)
- [`data-minimization-credential-reuse-and-sensitive-attribute-firewall-ladder.md`](data-minimization-credential-reuse-and-sensitive-attribute-firewall-ladder.md)

Route: first rank the likely controller, then use the proof ladder to decide who owes the map; this memo only sets the **minimum packet** that makes that map usable, reviewable, and privacy-bounded.[S16][S17][S21][S27][S39][S40][S41][S83]

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — no common map standard | let each actor describe governance however it wants, if at all.[S21][S27][S39][S41] | Reject: turns opacity and incomparable paperwork into a recurring advantage. |
| B — full telemetry and contract dump | demand broad logs, full org charts, complete contracts, and message retention by default.[S16][S17][S39][S40][S41] | Reject: too privacy-costly and too easy to repurpose into general surveillance. |
| C — short controller packet with attestation and event-trigger updates | require a compact layer-specific map naming governance levers, economic claims, key interfaces, and update triggers, signed by a responsible actor.[S16][S17][S20][S21][S27][S34][S35][S39][S40][S41][S83] | Adopt. |
| D — annual certification only | accept a once-a-year statement even when command, ownership, or deployment changed mid-cycle.[S21][S27][S39][S41] | Reject: too stale for live controller disputes and too easy to game between filings. |

## Five-part minimum packet

1. **scope and layer lane** — identify the system or deployment layer at issue, the filing entity or entities, the relevant jurisdiction or market, and the immediate affiliate or consortium context.[S21][S27][S34][S35][S41]
2. **governance-lever lane** — name who can start, stop, pause, deploy, update, approve release, allocate scarce capacity, set mission scope, govern retrieval or tool permissions, or change safety posture for the layer in question.[S16][S17][S20][S21][S41]
3. **residual-upside and downside lane** — name who captures the residual upside, who bears ordinary losses, who posts reserves or bonds, and who can authorize exceptional expenditure or continuation after failure.[S20][S21][S39][S41][S83]
4. **interface and dependency lane** — list the main remitters, vendors, hosts, hubs, channels, buyers, and other visible interfaces, while marking whether each is merely an outside interface, a bounded co-controller candidate, or part of the controller group for this layer.[S10][S21][S27][S34][S35][S39][S41][S83]
5. **attestation and update lane** — the map should be signed or attested by a responsible officer or authorized representative, refreshed at bounded intervals, and updated promptly after material events such as mission-specific commissioning, successor transfer, major governance redesign, step-in command, release-gate change, or affiliate-chain restructuring.[S16][S17][S21][S27][S34][S35][S39][S41]

## Provisional recommendation

Adopt **Option C — short controller packet with attestation and event-trigger updates** as the archive's default controller-map standard.[S16][S17][S20][S21][S27][S34][S35][S39][S40][S41][S83]

The archive should require the **smallest workable packet**, not a universal data-room. A controller map is enough when it lets a reviewer answer four questions without broad speculative discovery:

- what layer is being mapped,
- who holds the real governance levers for that layer,
- who captures the residual upside and can continue the activity,
- and which visible actors are only remitters, service providers, outside overseers, or other interfaces.

That packet should usually exist in both **short human-readable form** and **compact machine-readable form**, but the machine form should stay lean and derivative of the same underlying facts rather than expanding into surveillance-by-schema.[S16][S17][S27][S39][S40][S41]

## Minimum-field table

| Field family | Minimum content | What the archive is trying to prevent |
|---|---|---|
| layer identity | model / service / deployment layer, relevant entity, and relevant period.[S21][S27][S41] | vague maps that hide which part of the stack is actually in dispute |
| command rights | who can approve, halt, update, deploy, or materially re-scope the activity.[S16][S17][S20][S21][S41] | paper ownership without operational control |
| economic rights | who receives residual upside, who bears ordinary downside, who can commit capital or reserves.[S20][S21][S39][S41][S83] | remitter / controller confusion and contractor laundering |
| key interfaces | major hosts, channels, tool providers, buyers, auditors, or committees, marked by role rather than left as an undifferentiated list.[S21][S27][S34][S35][S39][S41][S83] | everyone-did-something maximalism |
| update / signer data | date, signer, authority basis, and material-change trigger status.[S16][S17][S21][S27][S39][S41] | stale maps and nobody-owned attestations |

## Failure-mode capsule

Cube anti-pattern axes: `classification_or_label_arbitrage`.
Use this controlled axis packet instead of a second local anti-pattern taxonomy; add only route-specific exceptions in the ladder or recommendation text.
Source continuity: [S16][S17][S20][S21][S27][S34][S35][S39][S40][S41]

## Recalibration trigger capsule

Cube review-trigger axes: `controller_or_accountability_drift`.
Reopen the route when those triggers materially change controller identity, control evidence, protected burden, contest access, or fallback duty.
Source continuity: [S16][S17][S27][S39][S40][S41]

## Accountability capsule

Profile: `controller_map_minimum_contents_attestation_and_update_cadence` in `docs/00-meta/actor-accountability-profiles.json`. Duty owner: `controller_map_filing_entity_and_authorized_attesting_signer`. Benefit/rent trace: `controller_or_affiliate_benefiting_from_opaque_incomplete_or_unsigned_governance_packet`.
Bottleneck/evidence start: `controller_map_packet_channel`; `attestation_signing_authority`; `registry_or_filing_portal`; `controller_map_layer_identity_record`; `governance_lever_and_release_gate_record`; `residual_upside_downside_and_reserve_record`. Fallback: `public_body_must_preserve_no_rent_fallback_notice_cure_and_nonforfeiture_when_map_packet_controls_tax_access_or_contest`.
Source continuity: [S16][S17][S20][S21][S27][S34][S35][S39][S40][S41][S83]

## Source IDs only

[S10][S16][S17][S20][S21][S27][S34][S35][S39][S40][S41][S83]

[S10]: ../../SOURCES.md#S10
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
