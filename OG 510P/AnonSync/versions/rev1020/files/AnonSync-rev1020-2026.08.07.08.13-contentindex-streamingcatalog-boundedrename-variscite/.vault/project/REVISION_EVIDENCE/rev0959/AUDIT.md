# Rev0959 implementation and adjacent audit

## Mission checkpoint

AnonSync remains one C++ product spine whose purpose is to replace Resilio Sync
for a named real folder workflow. Direct TCP, Tor, and I2P remain routes into the
same authenticated peer and convergence semantics. Rev0959 changes the retained
payload-store owner; it does not introduce another daemon, scanner, catalog, or
policy engine.

## Severe mixed-reader defect

Rev0958 made canonical `Prepared` and `Progress` scrub intent revoke restart
acceleration until current bytes are re-proved. Older readers do not understand
`Prepared = 4`. They could ignore an unknown scrub record while continuing to
open the same identity basename and trust a metadata-exact verification-index
entry. A downgrade could therefore restore authority to bytes that the newer
reader had already placed behind a restart fence.

The scrub sidecar cannot enforce its own reader generation: by definition, an
old reader does not know that the sidecar is mandatory. The fence has to be in an
object every cooperative reader already opens for identity and locking.

## Implemented reader fence

- Standalone v2 and product-bound v3 identity bytes remain unchanged, but current
  readers use reader-fenced basenames.
- A legacy-only writable root migrates only while an exclusive `flock` is held
  on the exact legacy identity inode.
- Before rename, the owner performs a complete descriptor-rooted payload scan
  with process and durable verification reuse disabled.
- Migration uses Linux `RENAME_NOREPLACE`, retains the open lock inode, accepts
  only the expected ctime transition, synchronizes the inode and parent
  directory, and re-proves old-name absence plus exact new-name binding.
- The successful cold proof is rebound to the post-rename identity observation
  and moved into the ordinary snapshot path, avoiding a second payload-byte
  pass.
- Current-plus-legacy coexistence, unsupported v1 names, conflicting bytes or
  types, lock contention, corruption, and post-cutpoint drift all fail closed
  without deleting forensic evidence.
- `ReadOnlyInspect` never migrates.

## Restart-fence repair and zero-read settlement

A present but checksum-invalid scrub record is no longer equivalent to absence.
Because its active digest cannot be recovered safely, it disables process and
durable verification reuse for the complete digest namespace until current
bytes are re-proved. A good complete scan can then rebuild canonical state under
the exact exclusive cutpoint, even when bounded scrub byte work is configured
as zero.

Likewise, when a complete scan has already hashed and proved the payload named by
an older `Prepared` or `Progress` record, the optional scrub transition no longer
resumes stale partial SHA-256 state. It re-proves the frozen state/root/payload
observation, advances the fair cursor, and publishes `Idle` with zero duplicate
payload reads. This removes both an immediate I/O tax and a false-corruption path
after metadata-hidden in-place repair.

## Adjacent authority and liveness audit

The sanitizer lane exposed a test-authority defect. The real-process corruption
regression wrote directly to a digest-named payload while the service was free
to begin a shared complete scan. Under instrumentation, the product correctly
reported that the namespace entry changed during validation, but the test had
intended to exercise a stable digest mismatch and degraded recovery.

The fault injector now opens the exact reader-fenced product identity with
`O_NOFOLLOW`, proves the named and opened regular-file inode and link count,
acquires `LOCK_EX|LOCK_NB` with bounded retry, re-proves the pathname, performs
the deliberate overwrite, and proves the lock inode remained exact before
unlock. Corruption, changed-corruption, and repair all use that helper. The test
therefore obeys the same cooperative ownership boundary as production writes.

The same audit separated product behavior from test supervision. The ordinary
folder-owner CTest timeout remains 60 seconds; ASan/UBSan builds receive a
bounded 120-second horizon. The focused instrumented executable completes in
about 49.5 seconds, so the new limit covers measured instrumentation cost without
weakening production deadlines.

A nearby production refactor classifies one exact complete-observation drift as
restartable. The scanner may discard one stale attempt, re-prove the live lock
inode, and restart with a fresh directory cursor. No verification generation,
checkpoint, scrub report, or snapshot authority is published from the discarded
attempt. A second drift remains terminal, keeping churn bounded.

## Audit result

The final lexical authority audit passes 161/161 checks. It binds the reserved
identity-name set, directed same-family migration pairs, cold pre-rename scan,
exact inode-preserving rename, post-rename reproof, damaged-intent namespace
fence, zero-read active settlement, stale-observation retry bound, lease-correct
fault injection, sanitizer-only test timeout, status schema v6, release verifier,
source patch, whitespace-stable prose checks, and documentation. This is defense in depth, not a semantic proof
of filesystem or crash behavior.

## Nonclaims

Rev0959 does not claim seamless mixed-version rolling upgrade, downgrade to an
old binary, hostile same-UID protection, universal power-loss behavior,
network-filesystem lock equivalence, quarantine, restore, bounded retention,
reachability pinning, garbage collection, rename identity, directory semantics,
selective synchronization, many-share supervision, cross-platform qualification,
live public Tor/I2P privacy qualification, or completion of the first measured
Resilio uninstall workload.
