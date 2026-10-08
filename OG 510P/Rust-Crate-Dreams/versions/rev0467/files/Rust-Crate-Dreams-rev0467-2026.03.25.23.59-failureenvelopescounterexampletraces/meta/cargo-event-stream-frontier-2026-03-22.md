# Cargo event-stream frontier — 2026-03-22

## Main judgment

**P-0042 cargo-event-stream** now deserves the archive’s newer artifact-rich treatment.

The upstream direction is finally explicit enough that the missing crate is not another ad-hoc Cargo wrapper.
It is a reviewable support bundle for:

1. **event-envelope authority**,
2. **foreign-output containment**,
3. **rendering-policy truth**,
4. **session identity**,
5. **portable redaction-aware export**.

## Why this frontier sharpened

- Cargo 1.93 development notes explicitly call out **structured logging** as active work.
- The Cargo build-analysis goal says Cargo wants to record build metadata across invocations and expose `cargo report` commands for timing and rebuild reasons.
- Cargo’s external-tools docs still document a hard boundary: `--message-format=json` does not control arbitrary output from procedural macros or other tools.
- Cargo command docs now make output-policy choices like `json-render-diagnostics` explicit, which means capture tools need to preserve not only messages but **how they were rendered**.
- The build-dir-layout-v2 testing call is a reminder that many tools still live on unspecified Cargo details because first-class features are missing.

Taken together, that means the receiver-facing value is now a crate that can say **what kind of event this is**, **what part of the stream was native versus foreign**, **what rendering mode was active**, **which session the event belongs to**, and **what redacted export is safe to hand off**.

## Best next implementation stance

The next implementation pass should freeze a small vocabulary before adding orchestration or analytics:

- event-envelope classes,
- foreign-output classes,
- rendering-policy classes,
- session-manifest classes,
- redaction-receipt classes.

The crate should stay provenance-first and export-first.
It should resist becoming either a dashboard or a trend warehouse.

## Sources

- https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/commands/cargo-doc.html
- https://doc.rust-lang.org/beta/rustc/json.html
