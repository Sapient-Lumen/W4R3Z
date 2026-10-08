# Gap: Downstream / Reverse-Dependency Testing for Libraries

## Summary
Rust has world-class compiler ecosystem testing via Crater, but ordinary library authors and
application teams lack an adoption-friendly way to do **reverse-dependency (rdeps) testing**:
- “Will this change break my dependents?” is hard to answer without bespoke CI.
- There’s no standard way to express “downstream test suites” and expected failures.
- There’s no portable artifact/report format to compare results across revisions.

This gap is about bringing a *Crater-like* capability down to everyday projects: small-scale,
repeatable, explainable downstream testing that runs in CI.

## Ecosystem signals
- Crater exists to run experiments over many crates and detect regressions.  
  Source: crater repository. https://github.com/rust-lang/crater
- The rustc dev guide describes “ecosystem testing” and positions Crater as separate infrastructure.  
  https://rustc-dev-guide.rust-lang.org/tests/ecosystem.html
- A recent writeup compares Debian’s autopkgtest + Britney migration gating (reverse-dependency testing)
  to Rust’s ecosystem testing, underscoring the value of rdeps as a release/quality gate.  
  https://nesbitt.io/2026/03/01/downstream-testing.html

## What “good” looks like
- A CLI that can:
  - pick an rdeps set (top-N, curated list, reverse-deps from crates.io)
  - build/test them with consistent toolchain + features
  - explain failures and diff results between PR/main
- Clear “cost controls” (budgets, shard strategy, caching)
- Portable reports that can be attached to releases or PR checks
