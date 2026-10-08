# Overlap admission review page — local subject reopen, sibling branch, and collision risk interface spec

## Purpose

Review any same-host action that could attach a local subject to a runtime namespace.
This page answers:

- is this action reopening the same subject in the same namespace
- creating a deliberate sibling branch with distinct hidden state
- blocked because the same device already hosts the subject elsewhere
- dangerous because two runtimes may touch one continuity-bearing hidden spine

## Inputs

- requested action (`add-folder`, `connect-link`, `rebind`, `service-switch`, `config-launch`, `portable-launch`, `update-reopen`)
- local path / subject identifier
- detected hidden-state evidence (`.sync/ID`, archives, databases, receipts, unknown)
- active namespace chosen
- sibling runtime roster
- candidate lineage verdict (`safe-reopen`, `safe-sibling-branch`, `duplicate-id-block`, `spine-collision-risk`, `fresh-epoch-reset`, `uncertain`)
- strongest safe sentence
- stronger forbidden sentence

## Primary questions this page must answer

1. What kind of host-local branch will exist if I commit?
2. Is this the same subject, a clean sibling branch, or a collision?
3. What evidence justifies that verdict?
4. Which alternative branch was rejected and why?
5. What stronger continuity sentence remains unsafe?

## Layout

### A. Admission verdict strip

Fields:

- requested action
- branch verdict
- collision-risk level
- strongest safe sentence
- stronger forbidden sentence
- next safest action

Example verdicts:

- `Safe reopen of known subject in same namespace`
- `Safe sibling branch; new namespace, distinct subject identity required`
- `Blocked: same subject already hosted elsewhere on this device`
- `Blocked: hidden-spine collision risk between runtimes`
- `Fresh epoch only; preserve witness before reset`

### B. Evidence card

Show concrete evidence rows such as:

- `.sync/ID` present and matches known subject
- `.sync/ID` present but belongs to another active namespace
- no hidden spine present
- archive/history residue present
- storage root mismatch with presumed lineage
- selected folder already added elsewhere
- runtime roster shows competing namespace ownership

### C. Branch consequence compare

Compare at least these branches:

- reopen same subject
- create sibling namespace branch
- block and inspect existing runtime
- reset / remove and re-add as new epoch

For each branch show:

- continuity preserved?
- hidden spine reused?
- collision risk?
- share roster impact?
- witness preservation required?

### D. Rejected alternatives card

Fields:

- rejected branch
- why it was rejected
- what evidence would be needed to reconsider it

### E. Commit language block

Four lines:

- requested phrase
- approved phrase
- forbidden stronger phrase
- reason stronger phrase is blocked

Example:

- `Attach this folder here`
- `Reopen this subject in the known namespace`
- `Use this folder interchangeably from both runtimes`
- `The continuity-bearing hidden spine would become collision-prone`

## Required interactions

- `Inspect active namespace`
- `Open sibling runtime roster`
- `Preserve witness before reset`
- `Commit attach / block / reset`

## Guardrails

- Never let a folder picker silently become an overlap action.
- Never offer `safe reopen` without evidence of namespace continuity.
- Never offer `fresh reset` without surfacing witness-preservation consequences.
- Never allow a stronger sentence than the branch evidence earns.

## Output

A reviewed branch verdict that turns same-host attach into an explicit continuity decision instead of a support-case surprise.
