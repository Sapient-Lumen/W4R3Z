# ADR 0186: Authorize remote update staging through durable commands

Status: accepted construction protocol over direct UDP and forced TCP, 2026-08-26.

## Context

ADRs 0184 and 0185 separated release intent from synchronization delivery and qualified the local
inactive-slot lifecycle. They intentionally left feature bit 20 dark because no peer-facing request
could prove all of these facts together:

- the peer currently owns `install.firmware` authority under the active ownership epoch;
- both peers negotiated the update construction and its durable/sync dependencies;
- the request names the receiver's exact current accepted synchronization HEAD;
- replay, restart, quotas, cancellation, and audit retain the existing durable-command truth;
- remote staging cannot imply apply, restart, health confirmation, or execution.

Creating a second OTA queue would duplicate identities and recovery semantics already frozen in the
signed command store. Treating sync publication or a valid release signature as install authority
would collapse independent gates.

## Decision

Register durable operation 4, `update.stage`, requiring `install.firmware` and idempotent
desired-state recovery. Preserve `ICQ1` byte-for-byte and use fixed 40-byte `ICQ2` containing only
one exact nonzero 32-byte accepted HEAD. A successful result carries fixed 80-byte `IUS1` evidence:
the verified release sequence, exact accepted HEAD, exact signed-update manifest record, and whether
that inactive state already existed.

Advertise `signed-ota-v1` only after the local update construction opens successfully. Reject a
HELLO that advertises it without `durable-commands-v1`, `state-sync-v1`, and
`state-sync-ranges-v1`. Dispatch `update.stage` only when the feature is in the confirmed bilateral
selection. The ordinary exact-head authority proof must then grant `install.firmware` to the stable
principal currently bound to the peer and ownership epoch.

Serialize local and remote update mutation through one lock. At execution, reopen the update
policy's range-v1 namespace, require the request HEAD to equal its exact current accepted HEAD,
reverify the complete immutable artifact and signed bundle, and invoke the same inactive-slot
staging primitive used by the local control. A stale or different HEAD returns `conflict` without an
effect. Infrastructure failure returns `internal-error` and commits no invented success evidence.

Use the existing signed command journal without exceptions:

- commit outgoing intent before the first transport attempt and incoming intent before receipt or
  effect;
- key replay by peer Tox key, sender epoch, and message ID;
- bind admission to stable principal, authority head, and ownership epoch;
- enforce global, per-peer/direction, canonical-byte, and absolute store ceilings;
- permit outgoing cancellation only before the first committed send attempt;
- replay exact terminal bytes for an exact duplicate and return conflict for identity reuse with
  different canonical bytes;
- after interrupted `STARTED`, reexecute only the same HEAD, adopt the exact already-staged state,
  and commit canonical evidence.

Keep `update-apply` and `update-confirm` same-user local controls. No remote record selects a local
path, changes the update policy, restarts the Agent, obtains a health token, confirms health, or
executes slot bytes.

## Consequences

- Feature bit 20 and advertised operation bit 3 now mean a real, authority-gated remote staging
  path exists; they are absent when the update construction is disabled or cannot open.
- Sync writers, release signers, Tox friends, and `install.firmware` principals remain independent
  roles. A peer may need more than one explicit grant, but no role substitutes for another.
- A durable sender may request staging while the peer is offline. It cannot revoke that request
  after the first attempt because remote observation is then unknowable.
- Repeated staging is safe only for the exact immutable HEAD and verified candidate. It does not
  make a future deployment adapter idempotent.
- Remote apply, fleet rollout, release-key operations, destructive slot retention, boot integration,
  power-cut behavior, and representative-hardware qualification remain open M7 gates.

## Qualification

Canonical codec, executor, store, session, CLI, fuzzer, and real-Agent tests cover malformed
`ICQ2`/`IUS1`, feature dependencies, exact request/result binding, authority, expiry refusal, store
reopen, exact duplicate replay, conflict, interrupted reexecution, and the full local
apply/restart/confirm/rollback lifecycle after remote stage.

The same source-linked IoTox 0.41.0 rev0041 binary
`bd950320270ac7c40e9cdf197f33cd8ec20181fecfa83e7697bb5f4c7c49380d` passes two simultaneous
Sandwurm guests over direct UDP (`pair.6ebmw2t_`) and forced TCP (`pair.m_1e_fio`). Both roles in
each cell prove feature selection, exact remote durable staging, matching sender epoch/message ID,
sequence 1, one later Agent incarnation, health confirmation, and identical selected inert bytes.
The compact evidence and exact nonclaims are recorded in
`evidence/2026-08-26-sandwurm-remote-update-stage.md`.

