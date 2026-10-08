# Managed hidden bytes page — archive, inflight, stubs, and safe browse interface spec

## Purpose

The archive already had service residue and cleanup language.
What it still lacked was one ordinary page for the simpler question:

> right now, while this subject is alive, which hidden managed bytes exist under it, what do they mean, and which of them are safe to browse, safe to export, or unsafe to edit by hand?

Current official Resilio docs make this seam concrete.
They still say Archive may need to be opened through the hidden filesystem path, that `.!sync` names represent in-flight data, that stream stubs may appear when xattrs cannot be stored natively, and that deleting the wrong hidden material can suspend sync entirely.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Managed hidden bytes** page for every subject with hidden managed families.

The page exists to answer five things in one place:

1. which hidden managed byte families are present now
2. whether each family represents live work, history, metadata fallback, policy sidecars, or continuity spine
3. which families are browse-safe, export-safe, compact-safe, or mutation-forbidden
4. which families are currently overdue / stuck / expected / empty
5. what reviewed action is the least-widening way to inspect, export, compact, or repair them

## Fixed page order

1. **Current hidden-bytes verdict**
2. **Managed family inventory**
3. **Live meaning now**
4. **Safe browse / edit / delete contract**
5. **Reviewed actions**

### 1) Current hidden-bytes verdict

Show:

- `managed_hidden_bytes_page_id`
- subject scope
- current `hidden_bytes_verdict` (`none-present`, `expected-families-present`, `history-heavy`, `inflight-active`, `fallback-stubs-present`, `stuck-or-overdue`, `unknown`)
- strongest honest summary
- last materially hidden-bytes-shaping event time

The operator must be able to answer:

> what hidden managed bytes are under this subject right now?

### 2) Managed family inventory

Show rows such as:

- continuity spine
- history / archive bytes
- in-flight temp bytes
- metadata fallback stubs
- sidecar policy files
- diagnostic spill attached to the subject

Each row must show:

- item count
- byte count
- current state (`empty`, `active`, `retained`, `stuck`, `degraded`, `unknown`)
- default visibility class

### 3) Live meaning now

For each family show:

- what it means while the subject is healthy
- what it means when overdue or stuck
- strongest next proof that it will clear or settle
- whether another page owns the next decision

This section must make `archive retained`, `in-flight active`, and `fallback stubs present` visibly different.

### 4) Safe browse / edit / delete contract

Show one contract row per family:

- browse-safe?
- export-safe?
- compact-safe?
- direct manual delete safe?
- managed-action-only?

The page must make `safe to inspect` visibly different from `safe to mutate`.

### 5) Reviewed actions

Actions may include:

- `Open archive review`
- `Inspect inflight residue`
- `Inspect metadata fallback stubs`
- `Export hidden-bytes receipt`
- `Compact retained history`
- `Open spine integrity page`
- `Do not delete by hand`

Each action must preview state delta and non-effects.

## Public object

### Managed hidden bytes page

Fields:

- `managed_hidden_bytes_page_id`
- `subject_ref`
- `hidden_bytes_verdict`
- `managed_family_rows[]`
- `safe_contract_rows[]`
- `next_proof_rows[]`
- `reviewed_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. subject
2. hidden-bytes verdict
3. dominant managed family
4. dominant safety rule
5. next least-widening action

Example:

```text
Project Alpha     inflight-active     .!sync + archive present     browse safe, manual delete blocked     Open managed hidden bytes
```

## Non-goals

This page does **not** replace subject-spine continuity review or sidecar mutation review.
It proves only the current **managed hidden bytes** and their safe-handling contract.
