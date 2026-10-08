# Shared external-storage review page, removable world reuse, and safe ownership handoff interface spec

## Purpose

External or removable storage is where same-host multi-instance mistakes become easiest to rationalize.
The operator tells themselves they are only reusing a disk, test binary, or portable setup.
But continuity-bearing runtime state may already live there.

Current official Resilio docs still say using an external disk drive as storage for two instances can trigger the same corruption class as running two instances on one computer against the same folder.
AnonSync should therefore treat **external-storage reuse** as an ownership-handoff review, not a casual browse action.

## Review order

Every shared external-storage review should render the same sections in the same order:

1. **Detected removable world**
2. **Current ownership evidence**
3. **Requested next owner**
4. **Handoff options**
5. **Safe sentence and receipt preview**

### 1) Detected removable world

Show:

- device or volume identity
- whether continuity-bearing runtime state was detected
- whether the volume carries subject binds, storage roots, or portable branch state
- whether the media is currently attached to another live runtime

### 2) Current ownership evidence

Show:

- current or last-known owning namespace
- principal and storage-world evidence
- whether ownership is proven by receipt, marker, or only path heuristics
- whether the incumbent runtime is still live, dormant, or detached

### 3) Requested next owner

Show:

- requested runtime namespace
- whether the operator wants `resume`, `import as successor`, `inspect`, or `branch`
- whether requested action preserves continuity or intentionally forks it
- whether the plan would reuse existing hidden state or create new state beside it

### 4) Handoff options

Offer only typed options such as:

- `resume incumbent world on this host`
- `import reviewed successor from removable world`
- `branch into new target path on same media`
- `inspect media without binding`
- `detach and archive incumbent state before reuse`

Block silent outcomes such as `just add folder here`.

### 5) Safe sentence and receipt preview

Examples:

- `removable world may be resumed by the incumbent namespace only`
- `reviewed successor import required before this namespace may reuse the media`
- `same-path reuse blocked; create a separate branch path or inspect only`
- `ownership evidence incomplete; destructive reuse sentence withheld`

## Public objects

### `shared_external_storage_review`

Fields:

- `shared_external_storage_review_id`
- `volume_ref`
- `detected_runtime_state_class`
- `incumbent_namespace_ref` nullable
- `ownership_proof_strength`
- `requested_namespace_ref`
- `requested_outcome`
- `allowed_handoff_options[]`
- `blocked_stronger_sentence`
- `reviewed_at`

## Design tests

The page fails if any of these remain true:

- removable media with existing runtime state can still be treated as an ordinary empty target
- reuse across runtimes can still happen without saying whether continuity is resumed, succeeded, branched, or abandoned
- `external disk used by two instances` still appears only as a later corruption anecdote

## Non-clone reason

Current official Resilio docs openly admit that external-storage reuse across instances can corrupt continuity-bearing hidden state, but they still surface the clearest sentence in a repair article.
AnonSync should turn that into a review page that owns media lineage and handoff choices before reuse.
