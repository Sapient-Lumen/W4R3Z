# Gap: embedded device labs and hardware-in-the-loop contracts

## What is missing
Rust’s embedded ecosystem now has strong point tools and stronger common traits, but it still lacks a **shared host↔device workflow contract** and an explicit **lane map** for what different kinds of hardware evidence mean.

Today there is no standard way to describe, exchange, and diff:
- which board / SoC / probe / boot path a project targets,
- which lane actually ran (`attach`, `smoke`, `test`, `bringup`, `bench`, `recovery`),
- which flash / reset / log / debug / test paths are expected to work,
- which physical lab capabilities are required,
- which native captures came back from the real tool path,
- which normalized on-device run report was derived from those captures,
- which target-enablement attachments exist for a board family,
- and which support or release claim is actually backed by hardware evidence.

That missing layer matters because embedded Rust is no longer only about library traits.
It is also about repeatable bring-up, board farms, CI on real hardware, vendor enablement, manufacturing tests, and supportable debug/logging flows.

Sources:
- https://probe.rs/
- https://probe.rs/docs/getting-started/installation/
- https://docs.rs/embedded-test/latest/embedded_test/
- https://docs.rust-embedded.org/embedonomicon/soc-support.html
- https://developer.espressif.com/blog/2025/02/rust-esp-hal-beta/
- https://docs.espressif.com/projects/rust/esp-hal/1.0.0-beta.0/esp32/esp_hal/index.html
- https://defmt.ferrous-systems.com/
- https://github.com/probe-rs/probe-rs/releases

## The current seam is awkward
The ecosystem has real building blocks:
- `embedded-hal` / `embedded-hal-async` for driver interoperability,
- `probe-rs` for flashing, debugging, RTT, and `defmt` output,
- `defmt` for efficient host-decoded logs,
- `embedded-test` for libtest-compatible on-device tests,
- Embassy / BSP templates / project templates for app setup.

But each real project still ends up hand-assembling a lab contract out of:
- `.cargo/config.toml`,
- linker scripts and board-specific memory files,
- target / chip / probe command-line flags,
- self-hosted runner YAML,
- ad hoc serial/RTT/`defmt` capture conventions,
- repo-local notes about boot pins or under-reset attach,
- and README prose explaining how to reset the board when automation fails.

The churn between adjacent tools is a signal here, not a criticism.
The installation unit for the main `probe-rs` CLI surface is now `probe-rs-tools`; `defmt-test` is now explicitly the deprecated `probe-run` lane rather than the recommended path; and the Embedonomicon still frames target enablement as a bundle of flash/debug/examples/templates/testing work rather than one magic crate. That is a healthy ecosystem evolving, but it also shows the absence of one durable workflow description layer above the tools.

## Why this matters
This gap is bigger than nicer flashing UX.
It affects:
1. **stability work** — Espressif’s `esp-hal` beta explicitly says HIL testing was crucial for stabilization;
2. **target onboarding** — the Embedonomicon’s SoC support flow requires flash algorithms, probe support, templates, examples, BSPs, and debug/test guidance, but today those requirements are mostly prose and per-repo convention;
3. **CI realism** — on-device tests are now practical across ARM, RISC-V, and Xtensa via `embedded-test`, with per-test reset, but reusable run descriptions and reports are still mostly absent;
4. **tool composability** — the `probe-rs` surface is growing and reorganizing, yet hardware truth still leaks through command layouts, local config, and runner-specific output;
5. **adoption quality** — without a lane map, teams flatten target enablement, smoke tests, testcase harnesses, shared-lab failures, and support statements into one fake “tested on hardware” sentence.

## What “good” looks like
A worthy contribution here is **not** “one embedded framework to rule them all” and not “standardize all HAL APIs after `embedded-hal` intentionally stopped trying to do that.”

It is a shared device-lab boundary:
- one `device-profile/v0` describing board / SoC / probe / flash / reset / logging / test capabilities,
- one `device-lab-manifest/v0` describing what a real lab or runner can provide,
- one `device-run-plan/v0` describing an intended flash/smoke/test/benchmark/bring-up lane,
- one `device-capture-import/v0` preserving the native output from `probe-rs`, serial logging, `defmt`, or vendor tooling,
- one `device-run-report/v0` recording firmware identity, lab conditions, transports, results, and attached captures,
- one `lab-pack/v0` bundle for CI, release review, board bring-up, vendor enablement, and incident/debug exchange,
- and one explicit lane map so **attach/smoke**, **per-test-reset harness**, **native capture transport**, **target-enablement**, **shared-lab operations**, and **support/release imports** stay distinct.

That would let Test Execution Evidence, Toolchain Productization, Observability, Coverage Evidence, Benchmark Evidence, Incident, Support, and Release Truth share the same subject instead of burying the operational truth in template repos and CI YAML.
