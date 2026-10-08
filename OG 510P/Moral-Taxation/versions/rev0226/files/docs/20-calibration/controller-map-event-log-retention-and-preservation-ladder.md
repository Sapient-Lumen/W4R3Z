# Controller-map event-log, retention, and preservation ladder

## Question in one sentence

Once the archive already knows **who must map control, what that packet must contain, who may see it, how integrity failures harden presumptions, and how interim filing proceeds**, **what is the smallest workable ladder for deciding which controller-relevant records must be kept, for how long, when deletion must pause, and when missing records become spoliation rather than ordinary administrative drift?**[S16][S17][S20][S21][S27][S39][S40][S41][S44][S83]

## Companion routes

Use this memo with:

- [`../10-framework/collection-and-remittance-routing.md`](../10-framework/collection-and-remittance-routing.md)
- [`../10-framework/administration-explanation-and-appeal-routing.md`](../10-framework/administration-explanation-and-appeal-routing.md)
- [`../10-framework/enforcement-proportionality-and-recovery-routing.md`](../10-framework/enforcement-proportionality-and-recovery-routing.md)
- [`controller-map-evidence-presumption-and-burden-shifting-ladder.md`](controller-map-evidence-presumption-and-burden-shifting-ladder.md)
- [`controller-map-minimum-contents-attestation-and-update-cadence-standard.md`](controller-map-minimum-contents-attestation-and-update-cadence-standard.md)
- [`controller-map-visibility-redaction-and-audience-tier-ladder.md`](controller-map-visibility-redaction-and-audience-tier-ladder.md)
- [`controller-map-integrity-correction-safe-harbor-and-sanction-ladder.md`](controller-map-integrity-correction-safe-harbor-and-sanction-ladder.md)
- [`provisional-controller-filing-escrow-and-true-up-ladder.md`](provisional-controller-filing-escrow-and-true-up-ladder.md)

Route: keep enough structured evidence to replay controller ranking, map updates, and true-up, but do not let controller-proof administration turn into indefinite raw-trace hoarding.[S16][S17][S20][S21][S27][S39][S40][S41][S44][S83]

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — packet-only lane | keep the signed controller map but no dated event trail, source pointers, or preservation trigger.[S20][S21][S27][S41] | Reject: too easy to rewrite history once disputes appear. |
| B — full raw-trace hoard lane | keep prompts, telemetry, approvals, and operational exhaust indefinitely just in case future ranking fights arise.[S16][S17][S27][S39][S40][S41][S44] | Reject: disproportional, privacy-heavy, and an invitation to surveillance drift. |
| C — bounded event-log plus preservation-on-notice lane | keep a thin controller-relevant event log and packet pointers in ordinary time, then freeze deletion narrowly once dispute, audit, incident, or appeal makes the records material.[S16][S17][S20][S21][S27][S39][S40][S41][S44][S83] | Adopt. |
| D — regulator-mirror lane | require routine delivery of full controller-side logs into a state mirror so preservation is never a live issue.[S16][S17][S27][S39][S40][S41][S44] | Reject: too centralizing and too broad for the archive's bounded-proof discipline. |

## Five-rung ladder

1. **packet-and-pointer lane** — in ordinary undisputed periods, keep the attested controller map, signer, effective dates, system identifiers, and hashed or otherwise stable pointers to the source materials that support the map.[S16][S17][S21][S27][S39][S41]
2. **material-change event-log lane** — when successor shifts, step-in command, release-gate control, tool-permission control, mission commissioning, or other controller-relevant changes occur, append a short dated event record that ties the change to the affected layer, period, and map version.[S16][S17][S20][S21][S27][S39][S41][S83]
3. **preservation-on-notice lane** — once a ranking dispute, provisional filing fight, audit, incident review, or appeal is opened, suspend ordinary deletion for the records in scope and preserve enough evidence to replay the contested controller story.[S16][S17][S21][S27][S39][S40][S41][S44]
4. **handoff and chain-of-custody lane** — where control moves between predecessor and successor, principal and managed operator, or ordinary controller and step-in manager, require a bounded handoff packet so the archive can reconstruct who governed which layer and period without storing every raw trace forever.[S16][S17][S20][S21][S27][S39][S41][S83]
5. **anti-spoliation lane** — deletion, log tampering, or selective non-preservation after notice justifies adverse inference, hardened presumptions, escrow hardening, and sanctions through the integrity ladder.[S20][S21][S27][S34][S35][S39][S41][S83]

## Provisional recommendation

Adopt **Option C — bounded event-log plus preservation-on-notice lane** as the archive's default record rule for controller maps.[S16][S17][S20][S21][S27][S39][S40][S41][S44][S83]

Presumption:

- keep a **thin packet plus controller-relevant event log** in ordinary time,
- keep **ordinary retention bounded** rather than indefinite,
- trigger **narrow preservation** when dispute, audit, incident, or appeal makes particular records material,
- require **handoff packets** when controller-relevant authority moves across entities or layers,
- and treat **post-notice deletion or tampering** as a stronger integrity failure than ordinary stale administration.

This is the archive's narrowest workable setting because it preserves replayability for ranking, true-up, and appeal without turning controller-boundary administration into a permanent telemetry lake.

## Default response table

| Live situation | Default response | Why it usually fits | Archive warning |
|---|---|---|---|
| stable undisputed deployment | keep the signed packet plus thin event pointers | enough to test the map later without full raw-trace capture.[S16][S17][S21][S27][S39] | do not confuse general observability with moral permission to store everything. |
| ordinary controller-relevant change | append a dated event record | preserves continuity across versions, successors, and governed layers.[S16][S17][S20][S21][S27][S39][S41][S83] | the event log should name the change, period, and affected layer, not become a narrative diary. |
| ranking dispute, audit, appeal, or incident opens | freeze deletion for records in scope | replay becomes more important than ordinary minimization once the facts are live.[S16][S17][S21][S27][S39][S40][S41][S44] | keep holds narrow and contestable; do not convert one dispute into universal retention. |
| controller handoff or step-in episode | require a handoff packet and chain-of-custody note | prevents transition periods from becoming liability fog.[S16][S17][S20][S21][S27][S39][S41][S83] | no-handoff transitions should harden successor or step-in presumptions. |
| deletion or log tampering after notice | apply adverse inference and integrity escalation | once notice exists, missing records are evidence problems, not just filing defects.[S20][S21][S27][S34][S35][S39][S41][S83] | sanctions still track materiality and culpability, not mere storage mistakes. |

## Anti-patterns

- **packet fiction without replay** — the archive receives a polished controller map with no stable pointers or dated event trail.[S20][S21][S27][S41]
- **privacy collapse by preservation panic** — every controller inquiry triggers indefinite retention of raw prompts, telemetry, or unrelated logs.[S16][S17][S39][S40][S41][S44]
- **no-handoff amnesia** — control changes hands but no bounded transfer packet preserves who governed which layer and period.[S20][S21][S27][S39][S41][S83]
- **sealed-forever retention** — records are preserved but never reviewable enough to test the map or contest the ranking.[S16][S17][S21][S39][S40][S41]
- **delete-before-disclose racing** — actors strip logs or source pointers once challenge becomes likely but before formal notice lands.[S20][S21][S27][S34][S35][S39][S41]

## What would change the recommendation

Tighten, loosen, or replace this ladder if:

- privacy-preserving proofs become strong enough that thinner packets can still replay controller ranking,
- experience shows that most controller disputes turn on short handoff windows rather than long historical trails,
- preservation notices are arriving too late to stop strategic deletion,
- or bounded event logs themselves begin drifting toward generic surveillance rather than controller-specific replay.[S16][S17][S20][S21][S27][S39][S40][S41][S44][S83]

## Source IDs only

[S16][S17][S20][S21][S27][S34][S35][S39][S40][S41][S44][S83]

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
[S44]: ../../SOURCES.md#S44
[S83]: ../../SOURCES.md#S83
