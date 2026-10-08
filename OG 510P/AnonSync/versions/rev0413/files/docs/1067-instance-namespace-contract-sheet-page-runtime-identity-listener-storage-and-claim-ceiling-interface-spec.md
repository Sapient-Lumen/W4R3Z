# Instance namespace contract sheet page, runtime identity, listener, storage, and claim ceiling interface spec

## Purpose

The archive already had launch-class and storage-world pages.
What it still lacked was one explicit contract for the narrower same-host question:

> if this machine runs more than one AnonSync runtime, what exactly defines each runtime namespace and what local claims are forbidden to overlap?

Current official Resilio docs make the missing contract unusually obvious.
They still admit multiple same-host instances on Linux, but require later ones to take manual port ownership, and they still document destructive collision when two local runtimes claim the same synced folder.
That is not mere launch trivia.
It is host-level namespace truth.

AnonSync should therefore render one first-class **instance namespace contract sheet** before the operator is allowed to treat a second runtime as harmless.

## Core decision

Every seat capable of starting, attaching, or reviewing another local runtime must expose one explicit **instance namespace contract**.
It must say:

- which runtime namespace is being reviewed
- which listener and control audience it owns
- which storage and identity roots it would use
- which local subject-path claims are already reserved by another runtime
- what stronger sentence the product must refuse

The product must never let `run another instance`, `start with another config`, or `launch from here` stand in for this truth.

## Fixed review order

Every instance namespace contract sheet should render the same sections in the same order:

1. **Runtime namespace identity**
2. **Listener and control audience**
3. **Storage and identity roots**
4. **Local claim ceiling**
5. **Strongest safe sentence**

### 1) Runtime namespace identity

This section should show:

- namespace class (`interactive-user`, `service-user`, `named-daemon`, `portable-cli`, `ephemeral-review`, `unknown`)
- runtime principal
- continuity basis (`same-user-same-root`, `same-root-new-principal`, `new-root-same-principal`, `fully-distinct`, `unknown`)
- whether the namespace is already lived or only proposed

The operator must be able to answer: **what runtime world is this, and on what basis is it considered distinct or continuous?**

### 2) Listener and control audience

This section should show:

- data listener port posture (`fixed`, `random`, `inherited`, `unknown`)
- control listener / Web audience posture (`loopback`, `specific-interface`, `lan-wide`, `disabled`, `unknown`)
- whether any currently lived runtime already owns the requested port or audience
- whether later instances must separate the listener namespace explicitly

The operator must be able to answer: **what network namespace would this runtime own, and where could it collide?**

### 3) Storage and identity roots

This section should show:

- settings/storage root
- identity store location
- license/material location if separate
- whether these are explicit or default-derived from launch path
- whether they are already attached by another runtime namespace

The operator must be able to answer: **what durable world would this runtime open?**

### 4) Local claim ceiling

This section should show:

- claim posture (`no-subjects-yet`, `distinct-namespace-safe`, `path-collision-risk`, `storage-collision-risk`, `identity-collision-risk`, `unknown`)
- already-claimed local subject roots
- whether same-path bind is blocked, branch-reviewed, migrate-reviewed, or temporarily ambiguous
- whether removable/external media are currently attached to another runtime lineage

The operator must be able to answer: **what local claims are already taken, and what may not be double-claimed?**

### 5) Strongest safe sentence

The page must end with one sentence such as:

- `second runtime is distinct and may start with separate listener and storage roots`
- `runtime is distinct but no subject paths are yet safe to double-claim`
- `requested storage root is already continuity-bearing for another runtime`
- `same-path bind blocked; migrate or branch review required`
- `namespace evidence incomplete; destructive overlap sentence withheld`

And it must also show the stronger blocked sentence it refuses, such as:

- `it is safe to run both against the same folder`
- `different process means different world`
- `launching from another directory is harmless`

## Public objects

### `instance_namespace_contract`

Fields:

- `instance_namespace_contract_id`
- `host_ref`
- `namespace_ref`
- `runtime_principal_ref`
- `namespace_class`
- `continuity_basis`
- `data_listener_posture`
- `control_audience_posture`
- `storage_root_ref`
- `identity_root_ref`
- `license_root_ref` nullable
- `claim_posture`
- `claimed_subject_roots[]`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `generated_at`

## Main surface

A compact row should read like one of these, not just `instance configured`:

- `distinct runtime namespace · listener separated · no subject claims yet`
- `same principal · new storage world · path claims still blocked`
- `storage root already attached elsewhere · start blocked`
- `same-path claim collision risk · migrate or branch review`
- `namespace evidence incomplete · destructive overlap sentence withheld`

## Event language

Use phrases such as:

- `instance namespace prepared`
- `listener namespace separated`
- `storage world would collide with existing runtime`
- `same-path claim blocked pending migration review`

Avoid phrases such as:

- `extra instance enabled`
- `advanced launch ready`
- `multi-instance mode on`

Those lines are too weak and too flattening.

## CLI shape

```text
anonsync runtime namespace show --host self
anonsync runtime namespace explain --namespace ns_01J...
anonsync runtime claims show --host self
```

## Design tests

The model is not explicit enough if any of these remain true:

- the operator can start another runtime without seeing which storage root it would attach
- listener collision and subject-path collision still look like the same problem
- default-derived storage location can still hide behind launch-path convenience
- the product can still say `second instance supported` without owning the blocked same-path sentence

## Non-clone reason

Current official Resilio docs still make same-host multi-instance truth feel like Linux command knowledge plus a later corruption article rather than one ordinary product contract.
AnonSync should instead render runtime namespace, storage, listener ownership, and claim ceiling as one stable reviewed object.
