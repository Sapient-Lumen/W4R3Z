# Intervention contract sheet page: candidate action, risk, and success-claim interface spec

## Purpose

The archive already has pages for rollout health and promotion confidence.
What it still lacked was one ordinary page for the next action question:

> what intervention is actually on the table right now, how destructive is it, what evidence justifies it, and what sentence would count as success afterward?

Current official Resilio docs make this seam concrete because they suggest very different actions — restart, rescan, reconnect, re-add, unlink identity, change service user, raise watcher limits, delete stuck temp files, collect logs — but do not normalize them in one operator-facing intervention workspace.

## Core decision

AnonSync must expose one first-class **Intervention contract sheet** whenever any material operator action is under consideration.
This includes observation-only and artifact-capture actions.

The sheet exists to answer ten things in one place:

1. what problem sentence currently holds
2. what stronger sentence is blocked
3. what candidate interventions are in scope
4. which one is currently preferred
5. what evidence threshold justifies each candidate
6. what blast radius each candidate carries
7. what reversibility class each candidate carries
8. what prerequisites or coordination each candidate requires
9. what post-action proof is expected
10. what abort / escalation path applies if the chosen action fails

## Fixed page order

1. **Intervention header**
2. **Current-problem card**
3. **Candidate-intervention matrix**
4. **Risk and reversibility card**
5. **Post-action-proof card**
6. **Blocked stronger sentence**

### 1) Intervention header

Show at minimum:

- `intervention_id`
- linked incident / rollout-health id
- subject scope
- current strongest safe sentence
- blocked stronger sentence
- preferred candidate action
- current intervention status
- last reviewed time

Supported headline statuses must include:

- `observe-only`
- `ready-to-execute`
- `blocked-by-prerequisite`
- `executing`
- `awaiting-post-action-proof`
- `succeeded-partial`
- `succeeded-strong`
- `failed`
- `rolled-back`
- `escalated`

### 2) Current-problem card

Show explicit rows for at least:

- symptom or blocked sentence
- affected subjects
- current evidence basis
- urgency
- harm if no action is taken
- evidence freshness
- coordination scope

Supported urgency values must include:

- `low`
- `medium`
- `high`
- `contain-now`

### 3) Candidate-intervention matrix

Each row is one typed intervention candidate.
Required columns:

- `action_class`
- human label
- evidence threshold
- scope touched
- blast radius
- reversibility class
- coordination needed
- expected time to signal
- success-claim ceiling
- current recommendation

Supported `action_class` values must include at least:

- `wait-and-observe`
- `manual-rescan`
- `restart-client`
- `restart-service`
- `repair-connectivity-path`
- `reconnect-folder`
- `re-add-folder`
- `rebuild-local-metadata`
- `relink-identity`
- `switch-default-arrival-posture`
- `change-runtime-or-service-world`
- `raise-system-prerequisite`
- `clean-temp-or-service-files`
- `collect-artifacts`
- `escalate-human`

Rules:

- `wait-and-observe` is a real intervention class, not absence of action
- `collect-artifacts` is an intervention class with cost and prerequisites
- actions that fork or replace a settings/storage world must be visually stronger than local repairs
- more than one candidate may be `allowed`, but only one may be `preferred`

### 4) Risk and reversibility card

This card must separate these dimensions explicitly:

- destructive risk
- world-fork risk
- multi-subject coordination risk
- data-loss risk
- operator-time cost
- restart cost
- reversibility class

Supported reversibility classes:

- `instant-undo`
- `easy-local-revert`
- `restart-bound-revert`
- `requires-reconnect`
- `requires-readd`
- `world-fork-no-clean-merge`
- `unknown`

Hard rule:

Visible-value recovery must not overclaim reversibility.
An action can appear reversible while still abandoning prior metadata or service world history.

### 5) Post-action-proof card

This card must publish the strongest sentence that would count as success for the chosen action.
Show at minimum:

- expected observation window
- expected success predicate
- stronger sentence still blocked even after success
- evidence required to declare success
- evidence required to declare failure
- retry / cooldown rule

Supported success predicates must include:

- `symptom-cleared`
- `path-restored`
- `metadata-rebuilt`
- `identity-restored`
- `service-world-shifted`
- `artifact-captured`
- `cause-still-unknown`

### 6) Blocked stronger sentence

Always show at least one sentence that remains blocked even if the preferred action succeeds.
Examples:

- `Peer connectivity restored` may still be weaker than `root cause permanently removed`.
- `Folder sync resumed after restart` may still be weaker than `file watcher delivery is now reliable`.
- `Service can now write to target folder` may still be weaker than `old service world preserved without re-share cost`.

## Hard rules

- no destructive action may be marked `preferred` unless every weaker candidate shows an explicit rejection reason
- no candidate may hide whether it affects one subject, one cohort, or the whole runtime world
- success proof must distinguish `symptom disappeared` from `root cause removed`
- escalation cannot remain a vague fallback; it must have a typed trigger and required artifact bundle
