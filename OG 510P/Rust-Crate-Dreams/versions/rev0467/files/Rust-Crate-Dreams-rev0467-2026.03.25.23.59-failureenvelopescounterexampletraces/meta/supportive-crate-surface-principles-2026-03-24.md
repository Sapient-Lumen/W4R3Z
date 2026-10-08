# Supportive crate surface principles — 2026-03-24

This note answers a repo-level planning question that the archive now has to answer explicitly:

> What should a worthy crate provide other people besides a good API?

The December 2025 Rust Vision Doc write-up gives the sharpest current prompt:
Rust already gives crates strong tools for building safe, efficient abstractions, but it still lacks enough tools that make crates **supportive** for users.

This archive should therefore judge serious missing crates not only by what they compute, but by what **supportive surfaces** they export.

## Main judgment

A worthy crate should usually provide five distinct surfaces.
If it cannot describe these, it is probably still too vague to promote.

## 1. Orientation surface

Question:
- Who is this crate for, under what task profile, and with what obvious non-goals?

Typical artifacts:
- `decision-brief.md`
- `task-profile.json`
- `scope-split.receipt.json`
- `starter-set-scope.report.json`

What it should provide other people:
- a fast answer to “is this for my situation or not?”

Failure mode if missing:
- users inherit a hidden default culture and mistake it for ecosystem consensus.

## 2. Evidence surface

Question:
- What receipts, reports, witnesses, manifests, or doctors explain what was actually checked?

Typical artifacts:
- `*.receipt.json`
- `*.report.json`
- `*.manifest.json`
- `doctor.txt`

What it should provide other people:
- a portable answer they can attach to issues, reviews, ADRs, and support tickets.

Failure mode if missing:
- the crate degrades into opinion and screenshots.

## 3. Review surface

Question:
- What compact human-facing output should a reviewer or approver read first?

Typical artifacts:
- `manual-review.note.md`
- `decision-brief.md`
- `adoption-checklist.md`
- `claim-ceiling.note.md`

What it should provide other people:
- one short path to “why this, why now, what should still worry me?”

Failure mode if missing:
- all value hides in machine output or verbose docs, which means the crate never reaches the real decision maker.

## 4. Machine surface

Question:
- What should tooling, CI, or assistants be able to ingest without scraping prose?

Typical artifacts:
- JSON schemas
- rustdoc JSON locators
- structured bundle manifests
- stability / freshness policies

What it should provide other people:
- importable, replayable data that can be checked or reused later.

Failure mode if missing:
- every integration becomes one more bespoke parser or one-off prompt.

## 5. Drift and refusal surface

Question:
- What can change later, what should trigger reconsideration, and what must the crate refuse to claim?

Typical artifacts:
- `revisit-trigger.policy.json`
- `freshness-window.policy.json`
- `claim-ceiling.report.json`
- `candidate-reentry.policy.json`

What it should provide other people:
- one honest answer about how the current result can decay.

Failure mode if missing:
- temporary observations get reinterpreted as durable support guarantees.

## Why this matters to the current frontier

### P-0509 Pathfinder
Needs all five surfaces.
Without them it becomes a ranking shell.

### P-0536 Crate Knowledge Pack
Needs all five surfaces.
Without them it becomes a cache of unattributed snippets.

### P-0486 Debuggability Support
Needs evidence, review, machine, and refusal surfaces in particular.
Without them it collapses into one fake “debuggable” label.

### P-0472 Docs.rs Build Parity
Needs orientation and refusal surfaces so local success is not mistaken for hosted parity.

### P-0535 / P-0484 / P-0058
Need drift and refusal surfaces because dependency support, target support, and native prerequisites decay quickly and differ by environment.

## Anti-patterns

A crate is not yet worthy just because it offers:
- a prettier API,
- a ranking page,
- a chat shell,
- a benchmark screenshot,
- or a claim that “we support X.”

Those may still be useful.
They just do not yet satisfy the supportive-surface bar.

## Practical planning rule

Before promoting a proposal, answer these five questions:
1. what is the first **orientation surface**?
2. what is the first **evidence surface**?
3. what is the first **review surface**?
4. what is the first **machine surface**?
5. what is the first **drift/refusal surface**?

If three of those are blank, the proposal should probably stay below the frontier.
