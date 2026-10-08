# Same-host multi-instance port, storage, and state-world review interface spec

## Purpose

The archive already has execution-seat switching, host-custody claims, and same-host collision language.
What it still lacked was one explicit contract for a different same-host case:

> when one operator wants two live runtimes on the same host at the same time, what page proves that ports, storage, identity, and subject ownership are actually isolated instead of hoping manual flags are enough?

Current official Resilio docs make this seam vivid.
They still say Linux can run multiple instances, but that the second and later instances require manual transmission/reception port assignment.
The same Linux guide still says that if `--storage` is not defined, a default `.sync` storage folder is created in the current directory.
A current error page still says two instances of Sync on the same computer, or one external drive used as storage for two instances, can corrupt the former instance's internal `.sync` files if the same folder is added twice.

That is not just an advanced-user footnote.
It means multi-instance operation still depends on manually keeping namespaces apart.

AnonSync should therefore treat same-host multi-instance bringup as one reviewed namespace allocation and custody problem.

## Core decision

Every live runtime on the same host must belong to an explicit **instance namespace** that proves four separations together:

1. transport/listener ports
2. control endpoint identifiers
3. storage and identity roots
4. subject ownership claims for local paths

The product must never normalize a second live runtime into `just start another process`.

## Fixed review order

Every same-host multi-instance review should render the same sections in the same order:

1. **Existing runtimes on this host**
2. **Requested new instance namespace**
3. **Collision and corruption risks**
4. **Receipt and branch proof**

### 1) Existing runtimes on this host

This section should show:

- each currently running instance
- its control endpoint(s)
- transport/listener ports it owns
- storage/identity root it owns
- whether it already claims any overlapping local subject paths

The operator must be able to answer: **what already lives on this host, and which namespaces are already occupied?**

### 2) Requested new instance namespace

This section should show:

- proposed instance name
- proposed control endpoint(s)
- proposed transport/listener ports
- proposed storage root and identity root
- whether the new runtime is a sibling, branch, scratch lab, or reviewed migration target

The operator must be able to answer: **what exact namespace will this new runtime own?**

### 3) Collision and corruption risks

This section should show:

- port collisions
- storage-root overlap
- same-subject local-path overlap
- external-disk/shared-root reuse risk
- whether the new instance would read or write another instance's service state

The operator must be able to answer: **is this truly a separate runtime, or am I about to split one state world across two processes?**

### 4) Receipt and branch proof

This section should show:

- resulting instance namespace handle
- namespace reservations created
- blocked overlaps if any
- branch/migration relation to older runtimes
- teardown rule for later retirement

The operator must be able to answer: **what later proves that these runtimes were intentionally separated rather than accidentally colliding?**

## Public objects

### `instance_namespace_review`

Fields:

- `instance_namespace_review_id`
- `host_ref`
- `existing_instance_refs[]`
- `requested_instance_name`
- `requested_port_set[]`
- `requested_control_endpoint_set[]`
- `requested_storage_root`
- `requested_identity_root`
- `requested_branch_class`
- `collision_findings[]`
- `generated_at`

### `instance_namespace_receipt`

Fields:

- `instance_namespace_receipt_id`
- `review_ref`
- `host_ref`
- `instance_ref`
- `reserved_port_set[]`
- `reserved_control_endpoint_set[]`
- `storage_root`
- `identity_root`
- `branch_summary`
- `created_at`

## Main surface

A compact row should read like one of these:

- `second runtime admitted · isolated ports and storage`
- `blocked · storage root overlaps active runtime`
- `blocked · same subject path already claimed by sibling runtime`
- `lab branch admitted · no subject custody overlap`

## CLI shape

```text
anonsync instance list --host this
anonsync instance review --host this --name lab-b --storage /srv/anonsync-lab-b --port-set 41000-41002
anonsync instance apply <review>
anonsync instance receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- multiple live runtimes still depend on manual port memory alone
- a second instance can silently reuse another instance's storage or service state
- same-path subject ownership is discovered only after corruption or suspension
- the operator cannot prove later whether a second process was a reviewed branch, migration helper, or accidental duplicate

## Non-clone reason

Current Resilio docs still make same-host multi-instance operation depend on manual port assignment, implicit storage-root discipline, and later corruption warnings when two instances touch the same subject path.
AnonSync should instead require one explicit namespace review before a second live runtime starts.
