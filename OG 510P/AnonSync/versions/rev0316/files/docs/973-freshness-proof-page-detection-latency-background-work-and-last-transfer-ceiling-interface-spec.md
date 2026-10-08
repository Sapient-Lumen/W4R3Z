# Freshness proof page — detection latency, background work, and last-transfer ceiling

## Purpose

Separate real freshness proof from the weaker proxies operators often over-read:

- green state
- empty transfer queues
- no recent warnings
- a recent `last transferred` timestamp

## Top-level sentence

The page begins with one typed freshness sentence, such as:

- `Fresh as of 11:50 for connected peers; next rescan may still reveal local changes.`
- `Transfer quiet observed; freshness unproven because indexing is still active.`
- `Freshness stale because filesystem notifications are degraded and the rescan window has not elapsed.`

## Evidence sections

### 1. Detection evidence

Shows:

- filesystem notification health
- time since last full rescan
- configured rescan cadence
- whether manual rescan is available / pending
- substrate caveats if detection is known to be weak

### 2. Internal work evidence

Shows active or recently completed hidden operations:

- scanning files
- hashing
- merging folder tree
- reading file blocks
- copying local blocks / deduplication
- writing file to disk

Each item shows state: `none`, `active`, `recently active`, `stale proof`, `unknown`.

### 3. Transfer evidence

Shows:

- last transferred time
- queue empty / not empty
- pending upload/download counts
- last transfer horizon (connected peers only? all proved peers?)

### 4. Ceiling explainer

Explicitly states what the evidence does **not** prove.
Examples:

- `Recent transfer does not prove all intended peers are current.`
- `Quiet queue does not prove there is no local indexing debt.`
- `Green state does not prove freshness for excluded or offline peers.`

## Visual rules

- Never show a single monolithic freshness badge.
- The freshness sentence and its evidence blocks stay on one page.
- If freshness is weakened by detection lag, the weakening appears above any success color.

## Export rules

Any exported proof must include:

- proof timestamp
- detection basis
- hidden-work basis
- transfer basis
- proof ceiling
- invalidators
