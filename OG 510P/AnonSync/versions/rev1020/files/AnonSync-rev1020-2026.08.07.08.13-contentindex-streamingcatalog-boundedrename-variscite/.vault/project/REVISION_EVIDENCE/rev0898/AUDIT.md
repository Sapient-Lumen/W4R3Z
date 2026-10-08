# AnonSync rev0898 audit

## Heart of the mission

AnonSync is a durable, bounded causal-convergence system in which authority is
explicit, evidence-bound, recoverable, and never fabricated by observation.
Exact authorized history and live owned capabilities decide what may exist,
move, retry, settle, or become visible. Paths, clocks, handles, summaries,
indexes, process exits, and configuration documents remain subordinate evidence.

## Corrected authority inversion

Rev0897 removed implicit SQLite creation from ordinary commands, but payload
identity and store-set composition still leaked bootstrap authority. A status or
send path aimed at an empty payload directory could publish a durable folder
marker, and operational commands could independently mix database paths, roots,
folder identity, actor identity, and payload limits.

Rev0898 makes `anonsync_replica init` the sole product bootstrap frontier. It
prepares a canonical deployment manifest, validates that the exact bytes fit the
reader's 16 KiB/strict-UTF-8/strict-JSON contract before mutating any store,
initializes each selected owner explicitly, and publishes the manifest last.
Every operational command accepts the manifest as its sole store-set authority,
requires existing-only SQLite and payload opens, binds the embedded manifest
path to the file actually opened, rechecks the self-digest and canonical bytes,
and rejects copied, tampered, path-mixed, profile-incompatible, detached, or
lexically overlapping configurations before the protected mutation frontier.

The durable payload store now requires a non-defaulted open disposition.
`ExistingOnly` verifies the exact identity marker and cannot mint it;
`CreateIfMissing` is used only by init. The strict JSON parser was extracted
from the broad runtime aggregation into one dependency-light shared owner so
manifest admission and existing crypto documents cannot silently diverge.

## Audit/refactor result

The process proof exercises missing manifests, absent and detached stores,
manifest collision, copied and same-path-tampered manifests, raw-path mixing,
empty replacement payload roots, profile capability failures, wrong-role
SQLite targets, membership preflight ordering, clock quarantine/recovery,
mutual TLS transfer, filesystem publication, receipt, and terminal settlement.

The full registry initially stopped at 216/217 because the bounded-file source
audit's exact consumer inventory did not yet include the new manifest reader.
That was a policy-tripwire failure, not a runtime failure. The inventory was
updated without weakening its exactness, the release verifier was taught to pin
the new surface, and the final registry passed 217/217.

## Remaining highest-risk gaps

1. Store composition is still manifest-bound rather than cryptographically
   persisted into every SQLite role and payload marker. A shared deployment ID
   should be stamped into every selected authority resource and attested on open.
2. Init is publish-last but not yet a resumable/quarantinable crash-recovery
   state machine. Partial stores may remain after interruption even though no
   committed manifest exists.
3. Path authority is lexically normalized and final-link rejecting, not yet
   fully descriptor-rooted against ancestor replacement. Linux `openat2`-style
   resolution or a portable descriptor-walk owner is a likely next boundary.
4. SQLite WAL transactions across separate databases are not atomic as a set.
   Cross-store operations need an explicit coordinator/protocol rather than
   inferred atomicity.
5. The executable is still a bounded command spine, not a supervised production
   daemon with operator policy, backoff, resource ceilings, observability, and
   lifecycle integration.
6. The current build graph remains expensive for narrow product-spine changes;
   cache launchers, carefully scoped unity builds, and job pools should be
   measured rather than applied globally.

## Validation

- GCC 14 / Debug / bundled SQLite 3.53.3 configuration completed.
- Final dependency closure reported `ninja: no work to do.`
- Focused product/authority lane: 8/8 passed.
- Full registered suite: 217/217 passed.
- Database-open policy audit: 16/16 passed.
- Bootstrap-authority audit: 18/18 passed.
- Bounded-regular-file audit: 23/23 passed.
- Release path-policy selftest: 14/14 passed.
- Direct and registered executable process proofs passed.
- `git diff --check` and Python bytecode compilation passed.
- `clang-format` was unavailable in the cloudtainer and is not claimed.

The source audits are lexical tripwires and are not formal proofs of runtime
race freedom, crash safety, filesystem semantics, or cross-store atomicity.
