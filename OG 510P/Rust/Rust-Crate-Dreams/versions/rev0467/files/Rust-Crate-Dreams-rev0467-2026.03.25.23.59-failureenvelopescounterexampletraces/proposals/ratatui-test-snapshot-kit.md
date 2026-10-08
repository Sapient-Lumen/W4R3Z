---
id: P-0178
title: Ratatui Test & Snapshot Kit — interaction replay + deterministic snapshots + CI diffs for terminal UIs
status: idea
domains: [tui, developer-tools, testing, accessibility, cli]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/ratatui/ratatui
  - https://ratatui.rs/
  - https://github.com/ratatui/crates-tui
---

## What it should provide others

A standard testing substrate for terminal UIs (Ratatui-first, extensible to others) that makes UI regressions boring:

- Deterministic **render snapshots**:
  - stable “screen model” snapshots (cells, styles, scroll state),
  - golden-file diffs with semantic grouping (layout vs text vs color/style).
- Interaction **replay harness**:
  - record/replay key chords, mouse events, window resizes, tick timers,
  - deterministic “time” (drive the app with a mocked clock).
- Portable `*.tuitestbundle.zip` failure artifacts:
  - snapshot diffs, event stream, app logs, environment (terminal size, features),
  - optional redaction rules for sensitive screen content.
- A `cargo tui-test` runner:
  - supports CI sharding, retry, and stable reporting,
  - emits `tui-report.json` with pass/fail + snapshot drift summary.

## Why this is still missing

Ratatui is popular and there are many real TUIs, but testing is fragmented:
teams either do ad-hoc snapshotting, or rely on manual QA. A shared kit would:

- reduce churn from layout changes across terminals,
- make refactors safer by turning UI behavior into artifacts,
- enable ecosystem-wide “widget conformance” tests.

## MVP scope

- Snapshot model + golden diff tool.
- Event stream format + replay runner for one async runtime (Tokio).
- Basic bundle format: `tuitestbundle`.

## v1 scope

- Widget conformance suite (tables, lists, input, scrolling) with fixture apps.
- Accessibility affordances for terminal UIs:
  - semantic labels for focus, “role” hints, readable summaries for screen readers (where feasible).
- Cross-terminal normalization (handle minor ANSI quirks predictably).

## Design notes

- Prefer stable, color-agnostic diffs by default; allow strict mode.
- Keep the snapshot model independent of Ratatui internals to avoid version lock-in.
- Make reproduction trivial: `cargo tui-test replay path/to/bundle.zip`.
