# Epic Proposal: Replay Kit (cargo replay)

## One-sentence pitch
Make async/concurrency bugs reproducible and shareable by standardizing task-level record/replay + schedule minimization into a portable “bug cassette” artifact.

## Deliverables
- `cargo-replay` reference implementation
- Schemas:
  - `replay-pack/v0`
  - `replay-report/v0`
- Instrumentation adapters:
  - `tracing` layer
  - Tokio runtime hooks (initial)
  - generic futures executor hooks (roadmap)
- Minimizer:
  - delta debugging of schedules + event subsets
- Corpus:
  - sample flaky tests and known concurrency bugs
- Docs:
  - privacy and redaction guide
  - how to use with Tokio Console and (optional) rr

## Why now (signals)
- Rust already has strong concurrency testing tools (Loom, Shuttle) but sharing a minimal repro across machines/CI is still painful.  
  https://crates.io/crates/loom  
  https://docs.rs/shuttle/latest/shuttle/
- Tokio Console provides task-level diagnostics; it’s a natural substrate for recording the right signals.  
  https://crates.io/crates/tokio-console
- rr demonstrates the power of deterministic record/replay and reverse debugging at the OS level; Replay Kit brings a task-level version to Rust async.  
  https://rr-project.org/
- Real-world experimentation exists (e.g., lildb), suggesting the next step is standardization + tooling UX.  
  https://cliffle.com/blog/lildb/

## Non-goals
- “Perfect” replay for all programs without instrumentation
- Capturing sensitive data by default (privacy-first)
- Replacing rr or Tokio Console (we integrate)

## Milestones
1) v0: record/replay packs for a Tokio-instrumented test suite + `replay-report/v0`
2) v0.2: minimizer + CI diff integration
3) v0.3: adapters for other runtimes + loom/shuttle import/export
4) v1: stable schemas + production incident capture mode (opt-in, redacted)
