# Completion dispute timeline page: challenge, escalation, verdict, and reopen events interface spec

## Purpose

A challenged completion claim can change shape over time.
The operator needs one ordered place that preserves when the challenge opened, what evidence arrived, when acceptance narrowed, what rework spawned, and whether the same claim was later appealed or reopened.

## Core decision

AnonSync must expose one first-class **Completion dispute timeline** whenever a fulfillment claim enters challenge, adjudication, appeal, or post-verdict reopen.

## Fixed timeline event classes

Supported `event_class` values:

- `challenge-opened`
- `counterevidence-attached`
- `assignee-response-attached`
- `witness-priority-changed`
- `prior-acceptance-frozen`
- `narrowing-proposed`
- `verdict-issued`
- `rework-issued`
- `downstream-recall-sent`
- `appeal-opened`
- `appeal-denied`
- `appeal-upheld`
- `claim-reopened`
- `dispute-closed`

## Required timeline columns

- event time
- actor
- affected scope
- witness family referenced
- sentence strengthened or weakened
- downstream object touched
- next required action

## Hard rules

### Challenge-freeze rule

Once a material challenge opens, the timeline must show whether the prior acceptance remained active, narrowed, or frozen.

### Sentence-delta rule

Every event must record whether it strengthened, weakened, split, or preserved the current safe sentence.

### Spawned-object rule

If the dispute creates rework, recall, a downgraded certificate, or a reopened case, the timeline must link the spawned object directly.

## Required interactions

- **Filter to sentence-changing events**
- **Filter to witness attachments only**
- **Filter to appeal / reopen only**
- **Jump to spawned rework**
- **Jump to recalled reliance packet**

## Empty and failure states

If only the opening challenge exists, show:

- `Challenge is open; no adjudication events have occurred yet.`
