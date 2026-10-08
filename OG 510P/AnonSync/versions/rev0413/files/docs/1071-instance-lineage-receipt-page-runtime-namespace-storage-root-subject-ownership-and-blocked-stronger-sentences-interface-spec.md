# Instance lineage receipt page, runtime namespace, storage root, subject ownership, and blocked stronger sentences interface spec

## Purpose

After any same-host multi-instance decision, the operator should not have to remember Linux launch details, storage defaults, or why a path was blocked.
They should be able to open one receipt and answer:

> what runtime namespace did we create, what durable world did it attach to, what subject claims were explicitly blocked, and what stronger sentence did the product refuse?

## When receipts are required

Emit this receipt whenever the product:

- starts a second runtime on a host
- changes listener or control audience for namespace separation
- chooses an explicit storage root for multi-instance bringup
- blocks a same-path or shared-storage collision
- imports a removable/runtime world as successor instead of allowing direct reuse

## Receipt sections

Every instance-lineage receipt should preserve the same sections in the same order:

1. **Namespace outcome**
2. **Continuity and storage basis**
3. **Subject-ownership verdict**
4. **Blocked stronger sentences**
5. **Follow-up obligations**

### 1) Namespace outcome

Show:

- resulting namespace ref
- start outcome (`started-distinct`, `continued-existing`, `blocked`, `inspect-only`, `successor-imported`)
- launch class
- runtime principal
- listener and control audience actually achieved

### 2) Continuity and storage basis

Show:

- storage root actually attached
- identity root actually attached
- whether continuity basis was `same-world`, `new-world`, `reviewed-successor`, or `ambiguous`
- whether any default-derived path was replaced by an explicit path during review

### 3) Subject-ownership verdict

Show:

- requested subject paths
- accepted claims
- blocked claims
- which path was redirected into branch review, migrate review, or inspect-only
- whether removable media lineage remained unresolved

### 4) Blocked stronger sentences

Always preserve statements such as:

- `safe to run both against the same folder`
- `same user means same world`
- `different process means safe second ownership`
- `external media was empty enough to reuse directly`

### 5) Follow-up obligations

Examples:

- `no subject binds allowed until successor import review completes`
- `audience widened to LAN; credential review remains required`
- `incumbent runtime must be opened for reattach instead of starting a second bind`
- `branch target path must be reviewed before first sync subject is created`

## Public objects

### `instance_lineage_receipt`

Fields:

- `instance_lineage_receipt_id`
- `host_ref`
- `result_namespace_ref` nullable
- `namespace_outcome`
- `runtime_principal_ref`
- `achieved_data_listener`
- `achieved_control_audience`
- `attached_storage_root_ref` nullable
- `attached_identity_root_ref` nullable
- `continuity_basis`
- `requested_subject_paths[]`
- `accepted_subject_paths[]`
- `blocked_subject_paths[]`
- `blocked_stronger_sentences[]`
- `follow_up_obligations[]`
- `issued_at`

## Compact render

Compact receipt rows should read like:

- `distinct namespace started · separate listener/storage roots · no subject claims accepted yet`
- `same-path claim blocked · incumbent world remains owner · migrate review opened`
- `removable world reuse blocked · successor import required`
- `namespace evidence ambiguous · inspect-only opened`

## Design tests

The receipt model is not strong enough if any of these remain true:

- later operators still need launch folklore to know whether the runtime was actually distinct
- blocked same-path claims vanish once the immediate warning is dismissed
- removable-world reuse can no longer be distinguished from a clean new namespace
- the product cannot restate the stronger sentence it refused

## Non-clone reason

Current official Resilio docs still make the operator recover same-host namespace truth from Linux notes, update ritual, service/storage semantics, and repair warnings.
AnonSync should keep one durable lineage receipt instead.
