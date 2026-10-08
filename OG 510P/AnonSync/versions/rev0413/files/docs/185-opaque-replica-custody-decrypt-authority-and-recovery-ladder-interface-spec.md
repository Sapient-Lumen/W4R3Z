# Opaque replica custody, decrypt authority, and recovery ladder interface spec

## Purpose

The archive already had restore, retained-replica truth, and snapshot-transfer language.
What it still lacked was one interface contract for a very different class of member:

> when a device is allowed to hold and seed bytes but is not trusted to open them, what page proves that this is an **opaque replica** with sharply limited authority instead of just another read-only peer?

Current official Resilio docs make this seam much sharper than an abstract encryption discussion would.
They still describe encrypted folders as a way to keep a peer on an untrusted device, say files are encrypted before transfer and are not decrypted on the destination, warn that encrypted folders add CPU and memory cost, require an empty target directory for initial setup, and note that reusing a directory that already contains files encrypted with the same F-key causes the files to be re-synced and moved to Archive, taking extra space.
They also still say the encrypted node is always read-only, always has `Overwrite any changed files` activated, does not support Selective Sync, can share onward only in encrypted form, and cannot restore a deleted file back to peers from its Archive in the ordinary way.
Recovery from the encrypted node still depends on saved RW/RO keys, keeping the original database, or dropping to a CLI decrypt command with a database path learned from logs.

That is useful capability.
It is not a clean public operator contract.

## Core decision

AnonSync should make **opaque replica** a first-class role with first-class review, not a side effect of a special key family.

An opaque replica is a member or bind with this public contract:

- may receive and retain ciphertext
- may seed ciphertext onward where policy allows
- may not render plaintext
- may not act as the authoritative restorer of record for share-visible delete/undelete
- may require separate recovery authority to turn retained ciphertext back into readable bytes
- must declare local target hygiene and replay/space side effects before setup

If a user still has to learn those truths from a mix of key prefixes, manual-connection ritual, archive side effects, and CLI recovery examples, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal seven truths AnonSync should not clone:

- an untrusted backup peer is a distinct custody class, not just a normal read-only recipient
- setup safety depends on target emptiness and on whether prior ciphertext already lives in that directory
- steady-state behavior still includes forced overwrite posture and no Selective Sync
- ciphertext holders can still seed while lacking plaintext-open authority
- restore-from-encrypted-backup is not the same as normal restore and still depends on preserved key material and preserved database lineage
- share-visible undelete still has a different ceiling from local recovery out of retained ciphertext
- the practical recovery story still falls back to debug-log/database-path ritual

AnonSync therefore needs one stricter rule:

> ciphertext custody, decrypt authority, restore ceiling, and target hygiene must be visible on one page before an opaque replica is created or trusted for recovery.

## Fixed review order

Every non-trivial opaque-replica action should render the same sections in the same order:

1. **Custody class and plaintext boundary**
2. **Target hygiene and steady-state limits**
3. **Recovery ladder**
4. **Receipt and post-create promises**

### 1) Custody class and plaintext boundary

This section should show:

- whether the new member is `plaintext`, `opaque replica`, or `mixed recovery seat`
- what the member may read, write, seed, or re-share
- whether local plaintext rendering is impossible by design or merely disabled by policy
- whether onward sharing preserves ciphertext-only posture or can widen authority

The operator must be able to answer: **is this device trusted with data, with ciphertext only, or with both?**

### 2) Target hygiene and steady-state limits

This section should show:

- whether the chosen target path is empty
- whether prior ciphertext with matching lineage already exists there
- whether attaching will cause re-ingest, archive moves, or extra local space use
- whether Selective Sync, local edit preservation, or ordinary restore are unavailable
- any extra CPU or memory cost expected from the role

The operator must be able to answer: **what does this target need to look like, and what steady-state limits come with the role?**

### 3) Recovery ladder

This section should show the honest recovery choices in strict order:

- `ordinary restore is not available from this opaque replica`
- `recover by connecting an authorized decrypt-capable seat`
- `recover locally with separate decrypt authority`
- `wait for a plaintext-capable witness`
- `blocked because required recovery material is absent`

It must also show which proof objects are missing if recovery is not presently possible.

The operator must be able to answer: **how exactly would readable data come back out of this node if the primary peers fail?**

### 4) Receipt and post-create promises

This section should show:

- the opaque-replica receipt that will be emitted
- the exact custody promises being made
- what future recovery prerequisites are being recorded now
- what this member will and will not count as in restore and witness views

The operator must be able to answer: **what evidence will later prove that this node was only ever meant to hold ciphertext?**

## Public objects

### Opaque replica plan

Fields:

- `opaque_replica_plan_id`
- `subject_ref`
- `member_ref`
- `target_path`
- `custody_class` (`ciphertext-only`, `mixed-recovery-seat`)
- `plaintext_rendering` (`forbidden`, `separate-authority-required`)
- `seed_capability` (`none`, `ciphertext-only`, `policy-limited`)
- `target_hygiene_verdict` (`empty-ok`, `ciphertext-lineage-present`, `mixed-material-blocked`, `non-empty-blocked`)
- `steady_state_limits[]`
- `expected_local_costs[]`
- `generated_at`
- `expires_at` nullable

### Opaque replica recovery ladder

Fields:

- `opaque_replica_recovery_ladder_id`
- `plan_ref`
- `required_material[]`
- `available_material[]`
- `recovery_steps[]`
- `restore_ceiling` (`local-decrypt-only`, `plaintext-seat-required`, `blocked`)
- `generated_at`

### Opaque replica receipt

Fields:

- `opaque_replica_receipt_id`
- `plan_ref`
- `member_ref`
- `created_path`
- `recorded_custody_class`
- `recorded_restore_ceiling`
- `target_hygiene_result`
- `recovery_prerequisite_refs[]`
- `completed_at`
- `provenance_ref` nullable

## Compact row contract

A truthful compact row should keep these facts in stable order:

1. member or seat
2. custody class
3. can render plaintext?
4. restore ceiling
5. next honest action

Example:

```text
vault-seed-eu-1     ciphertext-only     no     local decrypt authority required     Record recovery materials
```

The product should not make a user infer all of that from a padlock icon or a special invite flavor.

## CLI implications

A minimum public surface should include:

```text
anonsync opaque-replica plan create --subject <subject> --member <member> --path <path>
anonsync opaque-replica plan show <opaque_replica_plan_id>
anonsync opaque-replica recovery show <opaque_replica_recovery_ladder_id>
anonsync opaque-replica apply <opaque_replica_plan_id>
anonsync opaque-replica receipt show <opaque_replica_receipt_id>
```

The CLI should let an operator prove the custody boundary and recovery ceiling without consulting debug logs or remembering key-letter folklore.
