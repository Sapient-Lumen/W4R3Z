# AnonSync rev0873 revision notes

## Exact retry-release provenance, honest v3 migration, and separated time fence

Rev0873 fixes a durable authority gap in the sender outbox. Rev0872 retained the
retry deadline but discarded the accepted time observation that minted it. The
live release path enforced the 24-hour delay ceiling, but restart could no longer
revalidate that policy from durable state.

New releases now persist both:

- `retry_not_before_epoch`, the exact next-claim boundary; and
- `retry_released_at_epoch`, the exact accepted observation from which the
  relative delay was derived.

A durable enum records whether the pair is exact, absent, or inherited from an
older schema that did not retain release time. Exact history is not reconstructed
from a plausible lower bound.

## C++ state-machine changes

`SyncReplicaOutboxLeaseState` adds:

- `retry_released_at_epoch`; and
- `SyncReplicaOutboxRetryReleaseProvenance` with fixed protocol values
  `None=0`, `Exact=1`, and `LegacyUnproven=2`.

Validation now rejects:

- retry state with no provenance;
- an exact row with zero/reversed/over-budget release time;
- a legacy marker that fabricates a nonzero exact release observation;
- provenance on untouched or active-claim rows; and
- unsupported enum values.

The release API now accepts a bounded relative delay, performs overflow-checked
addition in the policy owner, and atomically mints exact deadline/provenance.
Claim token domain v2 binds the prior deadline, release observation, and
provenance tag before clearing retry state.

## SQLite schema v4

Schema v4 adds exact release-observation bytes and the provenance tag to every
outbox row. The current outbox digest advances to domain v3; the current
cutpoint advances to domain v4. Exact historical v1, v2, and rev0872-v3 schema
and digest readers remain available only for migration attestation.

All insert, exact update, exact delete, current restore, staged precommit
attestation, and snapshot paths include the new fields.

## Honest v1/v2/v3 migration

V1, v2, and v3 are migrated transactionally after exact schema and cutpoint
restoration. A released v2/v3 row preserves its exact deadline but receives:

```
retry_released_at_epoch = 0
retry_release_provenance = LegacyUnproven
```

That marker says precisely what is known. The migration clock floor uses the
strongest conservative lower bound old rows prove; it never invents the missing
observation. Exact v3 clock state is preserved. The next claim clears inherited
retry provenance, and a subsequent release mints exact v4 provenance.

## Audit/refactor corrections

The anti-rollback time-fence primitive is moved out of the lease implementation
into its own header, production translation unit, and runtime test. This makes
clock-fence policy independently auditable and leaves the lease owner focused on
attempt authority.

A build audit found the new test registered with CTest but missing from sanitizer
compile/link target lists. The library and executable are now included in the
instrumented graph.

The lease and SQLite structural audits advance to the rev0873 protocol surface.
They require the new state fields, enum values, claim domain, relative-delay
arithmetic, schema v4, historical v3 reader, digest domains, exact SQL compares,
migration semantics, tamper tests, CMake coverage, and release-verifier scope.
Stale malformed-migration test and audit identifiers were also renamed from
`into_v3` to `into_v4`, so diagnostic vocabulary matches the schema actually
published by this revision.

## Focused proof surface

The focused debug slice reports:

- time-fence test: 5 checks;
- pure lease test: 37 checks;
- SQLite owner test: 161 checks;
- lease structural audit: 24 checks; and
- SQLite owner structural audit: 44 checks.

The SQLite suite includes exact v3-to-v4 migration, restart, direct release-time
tamper, exact-to-legacy provenance downgrade, TEMP-trigger post-update mutation,
and rollback of the failed staged publication.

Final broader build, registered-test, warning, sanitizer, analyzer, stress,
lineage, patch-replay, manifest, directory, and ZIP evidence is recorded under
`REVISION_EVIDENCE/rev0873/` and summarized by `RELEASE_GATE.json`.

## Heart of the mission

AnonSync remains an evidence-authorized, crash-consistent, bounded convergence
engine under construction:

> Exact history is authority; summaries are acceleration.

A durable deadline is a consequence. The observation and policy that authorized
it are history. Rev0873 makes the current owner retain that history and makes
migration disclose where older implementations did not.

## Remaining gaps

The epoch remains caller-supplied; rollback is fenced but a bad far-future value
can still deny service. There is no boot/session-bound trusted clock owner,
forward-step bound, anomaly quarantine, or recovery protocol.

The retry owner lacks failure classification, exponential backoff, deterministic
jitter, maximum attempt age/count, poison state, dead-letter policy, and indexed
wake scheduling.

There is no authenticated receiver request, receiver-side idempotency/effect
owner, payload materializer, atomic visible-file publication, or authenticated
terminal receipt. Sender-side settlement is not an exactly-once end-to-end
protocol.

Digests remain unkeyed. Membership, actor key lifecycle, rotation, revocation,
recovery, forward secrecy, post-compromise behavior, causal stability,
compaction, production-scale incremental projection, complete physical resource
governance, and a privacy threat model remain future work.

See `RETRY_RELEASE_PROVENANCE_AUDIT_rev0873.md` for the full authority model,
migration reasoning, waste analysis, primary-source research, speculation,
roadmap, and deliberate nonclaims.
