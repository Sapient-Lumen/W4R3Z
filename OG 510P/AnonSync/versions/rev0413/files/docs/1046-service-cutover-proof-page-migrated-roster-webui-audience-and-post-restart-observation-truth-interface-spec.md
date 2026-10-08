# Service cutover proof page — migrated roster, WebUI audience, and post-restart observation truth

## Purpose

Provide the first durable proof after cutover of what really happened.

This page exists to answer:

- `did the reviewed service seat actually start under the expected principal?`
- `did the expected roster carry forward, or did a different world open?`
- `what control audience does the running service actually expose now?`
- `what observation grade does the running seat really have after restart?`
- `what stronger continuity or readiness sentence is still blocked?`

## Required sections

### 1. Runtime witness block

Must show:

- observed runtime class
- observed principal
- observed storage root
- startup witness time
- whether witness came from process proof, control-surface proof, or both

### 2. Roster carry-forward proof

Must show:

- expected subject count / roster class from review
- observed roster class after cutover
- matched carried-forward subjects
- missing subjects
- newly empty world verdict if applicable

Allowed verdicts:

- `reviewed roster carried forward`
- `clean branch confirmed`
- `different storage world confirmed`
- `partial carry-forward; reconnect review required`
- `insufficient proof`

### 3. WebUI audience proof

Must show:

- listener address class
- whether audience is loopback-only, selected-interface, all-interfaces, none, or unknown
- whether restart was required to reach current posture
- whether posture matches reviewed expectation

### 4. Observation truth block

Must show:

- mapped-drive status
- notification grade now in effect
- rescan dependence now in effect
- whether the service seat is expected to discover changes immediately, only on rescan, or only on restart/manual probe for some subject classes

### 5. Blocked stronger sentence

Examples:

- `All prior inventory was preserved automatically.`
- `This service seat observes updates the same way the interactive seat did.`
- `Same-seat continuity is fully proven.`

The page must instead publish the strongest safe sentence that current proof actually supports.

## Required interactions

- `Open reconnect review for missing subjects`
- `Open service lineage receipt`
- `Re-run proof after policy or listener restart`
- `Escalate unexpected world switch`

## Guardrails

- Never let successful service start imply successful migration.
- Never let browser-open imply same audience as reviewed.
- Never let `folders visible` erase observation downgrade.
- Never let partial carry-forward collapse into `migrated`.

## Output

A post-cutover proof surface that turns service start into a witnessed continuity verdict rather than a hopeful assumption.
