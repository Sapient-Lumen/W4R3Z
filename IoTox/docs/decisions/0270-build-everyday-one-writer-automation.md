# ADR 0270: Build everyday one-writer synchronization automation

Status: accepted local construction, 2026-08-31; two-guest qualification accepted by ADR 0276,
2026-09-01

## Context

M5B can publish, pull, verify, accept, and activate immutable revisions, but every transition
requires an explicit local command. That is a truthful transfer tool, not yet an ordinary unattended
folder mirror. Replacing that friction must not turn friendship into authority, persist process-local
friend numbers, activate merely because bytes arrived, or imply a multiwriter merge model.

## Decision

Add one owner-local automation policy per namespace:

```text
iotox sync-auto-publish NAMESPACE PATH [INTERVAL_SECONDS]
iotox sync-follow FRIEND NAMESPACE pull|verified [INTERVAL_SECONDS]
iotox sync-automation
iotox sync-automation-remove NAMESPACE
```

Each fixed-size `IOTXSAU1` record is signed by the stable device identity and binds a monotonically
increasing local generation, namespace, mode, activation intent, interval/retry bounds, and exactly
one source. A publisher stores a canonical absolute local path. A follower resolves the selected
live friend through the current transcript-confirmed v3 authority session and stores only the proven
stable publisher principal. A disabled higher-generation record is the revocation truth; deleting a
file is not.

Loading permits exactly one new private `automation/` directory beside `namespaces/`. Both the
namespace loader and the automation loader require an owner-owned mode-0700 directory. Automation
then rejects unexpected names, symlinks, links, wrong ownership/mode/size, noncanonical padding,
foreign signers, invalid timing/path/principal combinations, and signature changes. An active policy
must still reference a live namespace. Local publication requires the device in its writer set;
following requires the persisted principal in that set; verified activation additionally requires
the namespace's existing manual-activation permission. Namespace update/removal requires automation
to be disabled first.

Run a deterministic bounded scheduler above the existing controls. One periodic action and one
activation action may be in flight per namespace. New generations reconcile immediately; success
waits the configured interval; failure uses bounded exponential backoff; exact reload preserves
runtime state; and a completion from a replaced generation cannot mutate the new schedule. Counters
are content-free. Publisher scans, peer selection, network work, hashing, accepted-state inspection,
and activation execute on the existing bounded synchronization worker, never the Agent service
thread.

Do not add peer messages or feature bits. Automatic publication invokes the existing HEAD-last
publication transaction. Automatic pull selects a currently ready session for the stored principal
and invokes the existing authority-gated pull entrance. `verified` activation loads the current
device-authenticated accepted HEAD and passes its exact record digest to the existing optimistic
activation transaction. A newer HEAD cannot be selected accidentally; failure preserves the prior
projection and retries. `pull` never activates.

## Evidence

The owned registry now contains 674 passing checks. New deterministic coverage proves:

- signed generation creation, exact duplicate, replacement, and disabled tombstone behavior;
- tamper, foreign-signer, unsafe-root-path, zero-principal, and malformed-record refusal;
- immediate scheduling, one-in-flight admission, bounded exponential retry, success cadence,
  activation retry, and stale-generation fencing;
- local-control v1.44 operation/name stability and malformed CLI refusal; and
- a live mock-provider Agent periodically publishing a namespace, advancing after a source change,
  stopping, strictly reloading the signed policy, and advancing again after restart without another
  publish or automation command; and
- a live transcript-confirmed v3 publisher being captured by stable principal, followed
  automatically, converging one paged content-v2 CAS revision, accepting HEAD last, and activating
  only that exact accepted record under `verified`, with no manual pull or activation command.

This evidence qualifies the complete local deterministic scheduler path. ADR 0276 adds the separate
two-isolated-guest lifecycle, including independent publisher and replica Agent interruption over
direct UDP and forced TCP.

## Consequences

IoTox now has a real one-writer automation layer suitable for controlled evaluation. ADR 0276 closes
the two-guest mutation/restart gate: policy is installed once, each daemon role is interrupted, and
three source-only generations converge and activate without manual publication, pull, or activation.
This is still not a sole-copy Resilio Sync replacement claim. An hours-long noncritical shadow mirror
must follow before sole-copy use.

Treepack-v1 still republishes one whole deterministic archive and therefore is not an efficient
large-tree or one-file-delta design. Remote deletion, archive/restore, filesystem watches,
selective-sync placeholders, independent automation-policy rollback resistance, and bidirectional
editing remain absent. The future efficient path is a signed per-file CAS tree with explicit deletion
tombstones; multiwriter work, if ever selected, requires branch HEADs and explicit merges rather than
wall-clock last-writer-wins.
