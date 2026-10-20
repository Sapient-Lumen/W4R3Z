# ADR 0133: administer synchronization namespaces only while quiescent

Status: accepted

Date: 2026-08-21

## Decision

The live owner-local synchronization surface now admits two explicit policy effects in addition to
creation:

```text
iotox sync-namespace-update PATH
iotox sync-namespace-remove NAMESPACE
```

`sync-namespace-update` consumes one complete canonical `iotox-sync-namespace-v1` record. In this
first replacement slice, only activation mode and the sorted writer/subscriber principal sets may
change. Namespace ID, local data root, engine, and every quota remain immutable. Changing those
fields can change storage identity, interpretation, or resource accounting and therefore requires a
future migration rather than an update disguised as ordinary policy administration.

`sync-namespace-remove` deletes only the owner-local policy record. It never removes the namespace
data root, immutable objects, signed published/accepted/activated state, retention pins, rollback
guard, attempts, or evidence. A later reinstall can therefore recover the same locally retained
state. Removal is not garbage collection, deactivation, rollback, remote revocation, or proof that
content is unreachable.

Both effects cross same-user local control protocol v1.29 and require synchronization to be enabled.
They serialize with installation inside the Agent and on the namespace-directory inode. Before a
replacement or removal begins, the Agent requires the conservative service-wide publisher replay
cache to be empty and the target namespace to have no live subscriber job or unresolved failed or
cancelled cleanup. This deliberately prefers a bounded retryable refusal over changing membership
while a previously authorized transfer effect can still complete.

Replacement encodes the validated record into an unnamed mode-0600 `O_TMPFILE`, writes and fsyncs it,
links it under the one exact private temporary name `.<id>.namespace.update`, atomically renames it
over `<id>.namespace`, and fsyncs the namespace directory. Startup and every policy mutation remove
only strictly named, owner-private, singly linked, canonical update temporaries whose record ID
matches the filename. An unknown hidden entry, malformed record, alias, link, ownership mismatch, or
permission mismatch fails closed instead of becoming a general cleanup authority.

Removal unlinks the exact policy filename and fsyncs the directory. After every possibly mutating
store call—including an error that could have occurred after rename or unlink—the Agent reloads disk
truth when it differs from the live registry. Reload or registry replacement failure empties the live
registry. Thus a post-commit directory-fsync error cannot leave an older, more-permissive in-memory
policy active.

Exact update retry is `duplicate`; exact removal retry is `absent`. Neither advances the live registry
generation when disk and memory already agree. A committed update or removal reloads the complete
strict store and advances the generation once.

## Consequences

- Operators can rotate namespace membership or disable activation without stopping the Agent.
- Removing policy immediately closes future namespace resolution but intentionally preserves all
  content and signed state. Destructive GC remains absent.
- Writer/subscriber policy membership still does not grant authority by itself. Every remote effect
  must also pass the current authority-ledger v3 capability proof in the current authenticated epoch.
- Revoking an authority-ledger principal and removing it from namespace policy remain separate
  operations. The stricter of the two gates wins at each effect entrance.
- Root, engine, and quota changes require an explicit migration design with state and accounting
  consequences; delete-and-reinstall is not specified as that migration.
- This is manual policy administration, not a persistent `sync-subscribe` scheduler or an automatic
  watch relationship.

## Evidence

The direct namespace check covers atomic replacement, strict durable reload, exact duplicate,
immutable root/quota refusal, canonical stale-temporary cleanup, policy-only removal, absent retry,
and preserved store shape. Subscriber checks prove a live job blocks mutation while settled terminal
tombstones do not. The live Agent check crosses operations 74 and 75 through the real local socket and
proves install, update, duplicate, immutable-field refusal, remove, absent retry, and reinstall with
the exact registry generations.

The owned registry contains 509 checks. GCC warnings-as-errors and the complete compiler/sanitizer
matrices are the acceptance gates for this local-administration slice. Genuine two-guest transfer
qualification remains attached to data-plane milestones; this policy-only effect does not manufacture
a network claim.
