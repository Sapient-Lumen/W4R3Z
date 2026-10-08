---
id: P-0053
title: schedule-kit — DST-safe recurrence, business calendars, and a conformance suite
status: idea
domains: [time, scheduling, correctness, apps]
last_reviewed: 2026-03-01
evidence:
  - https://docs.rs/jiff
  - https://github.com/jkbrzt/rrule/issues/550
  - https://docs.rs/jiff-tzdb
---

# Problem
Scheduling in “civil time” is full of footguns: DST transitions, time-zone database updates, and recurrence rules that shift the wall-clock time unexpectedly. Even mature libraries in other ecosystems have DST recurrence bugs, and Rust developers often end up writing bespoke logic.

# Users & user stories
- SaaS backend: “Run a job every day at 09:00 in America/Denver — even across DST.”
- Personal productivity app: “Expand RRULE schedules reliably; show users why an occurrence moved/skipped.”
- Infrastructure: “We need a conformance suite so two implementations agree.”

# Prior art (and why it’s insufficient)
- Date/time crates (e.g., Jiff) provide TZDB-aware primitives, but do not define “recurrence semantics + conformance.”
- Recurrence libraries in other ecosystems show recurring DST-shift failure modes.

# Design goals
- A DST-safe recurrence engine with explicit semantics (preserve wall-clock time by default).
- Pluggable holiday/business-calendar constraints.
- A conformance suite with pinned TZDB snapshots and DST boundary fixtures.

# Non-goals
- Replacing core datetime libraries; schedule-kit should build on one (preferably Jiff).

# Architecture & API sketch
- Core types:
  - `Schedule { tz: TimeZone, rule: RRuleLike, constraints: [...] }`
  - `Schedule::next_after(InstantOrZonedDateTime) -> ZonedDateTime`
  - iterator `occurrences(start..end)`
- Recurrence semantics:
  - “local time first” calculations; explicit handling for “missing” times (spring forward) and ambiguous times (fall back)
  - policy knobs: `MissingTimePolicy`, `AmbiguousTimePolicy`
- Conformance suite:
  - fixtures: (tz, DTSTART, RRULE, expected occurrences)
  - run against multiple backends if desired

# Security / safety model
- Deterministic, pure computation; no network.
- TZDB source is explicit (system vs bundled), and schedule results are tied to a TZDB version.

# Maintenance & governance plan
- Aggressive test coverage around DST edges.
- Document semantics clearly; treat semantics as the “product.”

# Milestones
- 0.1: RRULE subset + DST boundary fixtures for a few zones.
- 0.2: full RRULE coverage + explain mode (“why this time”).
- 0.3: business calendars + holiday providers.

# Open questions
- How to handle TZDB updates and “what did this schedule mean historically?” (pinning & migration).
- Best public representation (iCalendar RRULE vs custom).

# Sources
See front matter links.
