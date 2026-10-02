# ADR 0256: Qualify fail-closed selected content-source loss on native UDP

Status: accepted, 2026-08-30.

## Context

ADR 0255 qualified one content-v2 pull from two complementary authenticated publishers over native
UDP, but it did not remove either publisher while that publisher owned a selected object request.
The existing `sync-source-add JOB_ID FRIEND` sequence also had an ordering hazard on an explicit
retry: a retained verified root manifest could let the primary HEAD result schedule object work
before the owner-local source-add request reached the daemon. If the primary did not hold that
object, an honest `object_absent` result could strand the job before the complementary source was
eligible.

The destructive gate also found an important persistence boundary. The construction fixture gives
both publishers an identical stable-device-signed HEAD, but a HEAD copied into the secondary's
local `published-heads` tree still has a foreign writer. Startup correctly rejects that state. A
replica is not entitled to impersonate a local publisher merely because it possesses immutable
objects and a valid signed root.

## Decision

Add owner-local `sync-pull-multi PRIMARY NAMESPACE SOURCE [SOURCE...]` using local-control v1.41
operation 88. Its payload contains an auxiliary count from 1 through 15, the primary friend number,
the distinct auxiliary friend numbers, and the namespace ID. The Agent resolves and authenticates
every source first, creates one content-v2 job, registers all auxiliaries while the initial HEAD
frame is still withheld, and only then dispatches that HEAD to the primary. Failure anywhere in
registration or dispatch terminally cancels and cleans the new job. This changes no peer frame and
does not grant an auxiliary HEAD or activation authority.

Accept the native-UDP `sync-content-multi-source-loss` gate. The subscriber starts an atomic
two-source pull, waits until the secondary owns positive object work, and stops that exact secondary
Agent. The first job must fail as a whole, remove transient staging and signed attempt state, and
retain neither accepted HEAD nor activation. Verified immutable prerequisites already committed to
CAS remain reusable. Recovery requires the same secondary Tox/signing identity to return at a
strictly higher authenticated epoch, followed by an explicit new atomic pull with a distinct job ID.
Both sources must again answer availability, contribute objects, reconstruct the artifact, accept
the original HEAD last, and activate only by the exact owner-local token.

Keep the locally published writer guard unchanged. For this construction-only complementary store,
the harness holds the foreign HEAD outside the secondary's local published-root tree during cold
start and reinjects the already verified replica HEAD only after the Agent is live. Evidence must
state that fact. A durable authenticated replica/accepted-HEAD store, distinct from locally
published HEAD state, is a separate design and qualification gate.

## Consequences

- Initial multi-source admission and explicit recovery no longer have a local-control ordering race.
  `sync-source-add` remains useful for dynamic source membership, but is not the recommended initial
  entrance when the complete source set is already known.
- Selected-source disappearance has one qualified behavior: fail the whole pull, fence its effects,
  then allow an explicit fresh retry after a higher authenticated epoch. There is no transparent
  continuation claim.
- Failed work may preserve only fully verified immutable CAS objects. It cannot preserve an accepted
  HEAD, activation, live staging, or an ambiguous CTA1 assignment.
- Possession of a valid signed HEAD does not confer local-publisher identity. The rollback/writer
  defense remains fail-closed.
- Forced TCP, Tor/I2P multi-source loss, multiple content lanes, automatic source replacement,
  daemon/guest restart of the subscriber, physical-host diversity, and durable replica cold start
  remain unqualified.

## Evidence

The retained secret-free compact proof is `.sandwurm/exports/pairs/pair.xujufman`. Raw and compact
forms independently passed strict replay. The exact experiment, metrics, construction caveat, and
reproduction commands are recorded in
`docs/evidence/2026-08-30-sandwurm-sync-content-source-loss.md`.
