# Overseer Archive

## Purpose

Define the rebuilt Overseer archive as a reproducible, curated export of the
live house for outside study, critique, and planning.

This is not a raw dump. It is a bounded derivative for:

- WebUI-assisted planning and metalooper study
- sharing the current shape of the house without leaking secrets
- helping others understand and reproduce the system design
- reconstructing a fresh archive repeatedly from the live repo
- giving outside reasoners a stronger packet for conductor/metalooper critique

## Builder

- `scripts/build_overseer_archive.py`
- `make archive-overseer`

Event-boundary doctrine:

- `docs/archive-event-boundaries.md`

The builder emits into:

- `/home/overseer/archive/release-candidates/`

Artifacts include:

- a staged archive tree
- a compressed `.zip` suitable for WebUI upload
- a stable symlink: `Overseer-latest-webui.zip`
- a build receipt JSON that marks the artifact as a stable handoff build, not an automatically declared milestone datacube

The human-wing publisher is intentionally stricter than the stable symlink
alone. If asked to publish `Overseer-latest-webui.zip` and the symlink is stale
or missing while newer `Overseer-rev*.zip` candidates exist, the publisher now
self-corrects to the newest release candidate rather than exporting an older
handoff build by accident.

## Inclusion policy

Included:

- root placards and opening surfaces
- bounded current-operator packet:
  - `WEEK.md`
  - `docs/operator-week.md`
  - `state/operator-week/latest.md`
  - `state/operator-week/latest.json`
- synthetic research-packet docs:
  - `NORTH-STAR.md`
  - `TRAJECTORY-MAP.md`
  - `HOW-TO-HELP.md`
  - `LIVE-HOUSE-PACKET.json`
    - includes critique-assimilation posture, compact critique-reading guardrails, critique guardrail provenance, bounded operator-auth-intervention memory, bounded operator-reported profile deactivation posture, compact auth-death guardrails plus their provenance, auth spend-proven vs proven-available supply split, provider-mail witness memory, compact provider-reading guardrails, provider guardrail provenance, and load-balancer guardian posture including its auth-pressure evidence-class mix
  - `WEBUI-METALOOPER-HANDOFF.md`
  - `QUESTIONS-FOR-OUTSIDE-REASONERS.md`
  - `REFERENCE-ARCHIVES.md`
  - `RECENT-COMMITS.md`
  - `WORKED-EXAMPLE.md`
  - `BOOTSTRAP-HISTORY.md`
  - `WORKED-EXAMPLE-ARTIFACTS.md`
  - `REPLAY-AND-VALIDATION.md`
  - `PACKET-DIALECT.md`
  - `METALOOPER-SEED.md`
  - `OUTSIDE-REASONER-RUNBOOK.md`
  - `REPORT-BACK.md`
  - `REPORT-BACK-SCHEMA.json`
  - `OUTSIDE-REASONER-PACKET.json`
  - `OUTSIDE-REASONER-PROMPT.xml`
  - `PACKET-INDEX.json`
  - `WORKED-EXAMPLE-ARTIFACT-INVENTORY.json`
- full `docs/`
- full `scripts/`
- full `tests/`
- full `specs/`
- full `nix/`
- small supporting trees:
  - `goldens/`
  - `browser/userscripts/`
  - `artifacts/timing/`
- safe `.human/` launcher/runtime scripts
- tracked `/etc/nixos` source files
- selected redacted/latest `state/` snapshots

Excluded or redacted:

- `authcreds/`
- `.codex/`
- browser profiles and browser caches
- private keys and `authorized_keys`
- full timer-churn histories
- raw journals and coredumps
- sensitive auth identifiers

## Why this shape

The archive should maximize:

- explanatory power
- reproducibility
- safe sharing
- low compression risk
- explicit opening paths
- outside-reasoner usefulness
- bounded operator-week usefulness
- metalooper/conductor planning value
- dedicated WebUI metalooper handoff value
- worked-example value
- bootstrap-history value
- worked-example artifact inventory value
- replay and validation value
- structured outside-reasoner reuse value
- packet-dialect value
- metalooper seed value
- truthful live-house current-posture reuse value
- machine-readable report-back value

It should not pretend to be:

- a live restore bundle
- a secret-bearing operational backup
- a full forensic image

## Outside-reasoner rule

The archive now expects a sharper standard than generic structured judgment.

When an outside reasoner makes current-posture claims, the report-back should
say whether `LIVE-HOUSE-PACKET.json` was actually used and whether its
anti-counterfeit distinctions were preserved, and if it was used should name
the anti-counterfeit seam ids actually relied on, especially:

- raw status vs effective status
- live interactive occupancy
- historical interactive continuity
- active interactive recovery
- critique receipt memory vs house judgment
- critique guardrail provenance from live lifted posture vs bounded fallback
- bounded operator-auth intervention memory vs downstream auth viability
- bounded operator-reported profile deactivation vs generic auth pressure or broader provider-family collapse
- auth-death guardrail provenance from live lifted posture vs bounded fallback
- bounded provider-mail witness memory vs compact provider guardrails vs provider guardrail provenance
- bounded provider-mail witness memory vs downstream auth viability
- provider guardrail provenance from live lifted posture vs bounded fallback
- identity-bearing provider walls vs `browser_session_residue` provider walls
- guardian observed/stale auth debt vs operationally weighty guardian auth proof

## Current rule

If the live repo and the archive disagree:

- the live repo wins
- the archive is a bounded explanatory derivative

If a rebuild does not cross an event boundary:

- preserve lineage
- keep the stable handoff current if needed
- do not automatically treat the rebuild as a milestone datacube worth special circulation

Bounded reopen may preserve that same rule as a compact attic ceiling when live
force is still narrow: `publication_posture_ceiling = stable_handoff_build`,
`milestone_status_ceiling = not_declared_by_builder`, and the bounded next move
remains preserving lineage while keeping the stable handoff current.

## Future value

This archive is part of the metalooper/conductor problem.
It is a low-cost external cognitive artifact that can be rebuilt on loop,
handed to outside reasoning surfaces, and used to study how the house is
changing over time.

## Subordination rule

Archive sophistication should remain subordinate to live force.

That means:

- handoff quality may improve the house
- archive doctrine may reduce reread cost
- outside critique may sharpen the constitutional picture

But none of those should be allowed to masquerade as operational strength.

If the live fleet is narrow, auth/browser/quota force is fragile, or the house
 is still depending on one or two especially expensive seams, then further
 archive refinement should be judged against that backdrop rather than treated
 as neutral progress.

The attic is valuable because it helps the organism remember and hand off its
 truth. It is not permission for the organism to become weaker while its export
 packet becomes prettier.

`LIVE-HOUSE-PACKET.json` should therefore carry the current strategic agenda
 only as bounded current-posture memory:

- enough to remember the four live cross-room pressures
- enough to preserve one compact live anchor for why each pressure is current
- enough to preserve one bounded residual gap when a pressure is partly
  grounded but not yet fully adopted, such as one remaining transition-law
  target surface
- enough to preserve one compact current posture for how hot each pressure is
- enough to preserve `current_posture.strategic_agenda.status_summary` and
  `current_posture.strategic_agenda.rightness_standard.status_summary`, so
  outside readers can hear the overall packeted house mood without
  reconstructing it from posture counts
- enough to preserve the agenda's non-claims
- enough to preserve the anchor reading rule that keeps those anchors from
  masquerading as closure proof
- enough to preserve posture counts and highest pressure level without letting
  that bounded geometry masquerade as a scheduler or room-local conclusion
- enough to preserve the top-level
  `current_posture.strategic_agenda.bounded_reentry_walk_order`, including the
  fact that it may be empty when all current strategic pressures are already
  `ok`, so outside readers can hear that the map still spans the agenda
  without inventing live strategic heat
- not enough to masquerade as a scheduler or as live proof that those pressures
  are already satisfied

The live packet may also preserve bounded weekly-room fleet coverage:

- which surviving live-force profiles the weekly room is measuring
- which of them already carry visible reset deadlines
- the compact posture for whether that live-force weekly coverage is full or
  still partial

The same archive restraint applies to quota-sweep cadence too:

- preserve whether the room is carrying simple cadence observation, partial
  bounded sweep evidence, or fresh bounded cache-refresh proof
- do not flatten those three classes into one generic "quota freshness" claim

That coverage memory exists to lower reread cost. It does not authorize further
token spend by itself.

The packet may also preserve the weekly room's live-fleet-specific
recommendation separately from the batch-wide recommendation, so outside
reasoners do not flatten "other profiles still have auth debt" into "the
surviving live fleet still needs more weekly-clock maintenance."

The same general anti-counterfeit rule now applies to weekly-clock posture too:
the live packet may carry visible weekly proof, bounded spend-only admissible
evidence, and ordinary maintenance observation, but outside readers should not
flatten those into one class of quota-time truth.
