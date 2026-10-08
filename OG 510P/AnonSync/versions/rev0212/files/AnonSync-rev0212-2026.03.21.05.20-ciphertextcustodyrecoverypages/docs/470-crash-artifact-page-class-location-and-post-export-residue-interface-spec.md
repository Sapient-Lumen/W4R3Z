# Crash artifact page: class, location, and post-export residue interface spec

## Purpose

This page answers:

> what crash artifact classes exist for this seat, where do they currently live, how are they exported, and what still remains local after export?

The page exists because `crash report`, `mini dump`, `dump`, `core dump`, and `diagnostic report` are not the same artifact.

## Core rule

Every crash or hard-failure workflow must expose one first-class **Crash artifact** page before export or cleanup.
That page owns:

- artifact class
- local path / owner scope
- collection route
- export status
- post-export residue

## Primary layout

The page always renders the same regions:

1. artifact verdict
2. class and locality card
3. collection route card
4. export and sensitivity card
5. post-export residue and cleanup card

### 1) Artifact verdict

Show:

- artifact label
- artifact verdict: `crash-report-present`, `minidump-present`, `core-dump-present`, `path-known-but-empty`, `awaiting-crash`, `mixed`, `unknown`
- strongest honest summary
- one next honest action

### 2) Class and locality card

Show:

- artifact classes currently present
- current local path for each class
- whether the path belongs to interactive user, service account, config-owned storage, NAS runtime, or unknown owner
- whether the artifact is hidden from ordinary file browsing

The operator must be able to answer: **what kind of crash evidence do I have, and where does it really live?**

### 3) Collection route card

Show:

- how each artifact is collected (`ordinary file pickup`, `task-manager dump`, `terminal script`, `SSH/ulimit workflow`, `automatic after crash`, `unknown`)
- whether out-of-product tools or elevated access are required
- whether collection can change the runtime or restart state
- whether the workflow is platform-specific and why

### 4) Export and sensitivity card

Show:

- whether the artifact has already been exported
- to which route / target class it went
- strongest sensitivity posture (`high`, `very-high`, `unknown`) and why
- whether redaction is possible, impossible, or not yet reviewed

### 5) Post-export residue and cleanup card

Show:

- what exact artifacts still remain local after export
- whether cleanup is manual, automatic, blocked, or unreviewed
- whether local residue is still needed for later retry / analysis
- the receipt or audit object that proves cleanup if performed

## Honest outputs

This page may conclude:

- `Windows minidump present in service-owned storage`
- `NAS core dump requires SSH collection and manual move`
- `crash artifact exported; local residue still present`
- `artifact path known but no current dump found`

It may not collapse these into one vague `crash logs available` verdict.

## Rules

### Rule 1 — class names must stay distinct

A crash report, minidump, and core dump may coexist and must not be flattened into one row.

### Rule 2 — runtime owner must remain visible

Interactive-user, LocalService, LocalSystem, config-owned, and NAS-hosted paths can imply different custody and cleanup consequences.

### Rule 3 — export must not imply cleanup

Sending or copying a dump elsewhere does not prove local removal unless cleanup is separately witnessed.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- what crash artifact classes exist here
- where each one lives and under which runtime owner
- how each one is collected and exported
- what sensitivity class the artifact implies
- what still remains local after export
