# Epic proposal: Device Lab Kit

## Thesis
Embedded Rust has enough successful pieces that the next high-leverage contribution is not another board template, another runner, or another hosted lab service.
It is a **shared device-lab contract** that describes what hardware a project targets, which lane of hardware execution actually ran, which native captures came back, and which normalized evidence was derived from them.

That would be a worthy ecosystem contribution because it helps:
- HAL/BSP maintainers,
- board vendors enabling Rust support,
- teams running self-hosted hardware CI,
- libraries validating support claims on real devices,
- and incident/debug/perf/release workflows that currently depend on ad hoc repo lore.

## Why now
The timing is unusually good:
- `probe-rs` has become a serious host↔device lane for flashing, attach, RTT/`defmt`, debugging, and HITL setups.
- `embedded-test` now gives Rust a practical libtest-compatible on-device path across ARM, RISC-V, and Xtensa, including per-test reset semantics.
- the `defmt` book explicitly routes users away from the old `probe-run`-centric test path and toward `embedded-test` with `probe-rs`.
- `probe-rs-tools` is now the installation unit for the main CLI surface, which is another sign that the workflow surface is still moving and deserves a durable metadata layer above one install layout.
- embedded ecosystems like `esp-hal` explicitly treat hardware-in-the-loop testing as release-blocking quality infrastructure.
- the Embedonomicon still treats flash algorithms, examples, templates, and debug/test guidance as target-enablement work rather than incidental notes.

Sources:
- https://probe.rs/
- https://probe.rs/docs/getting-started/installation/
- https://docs.rs/embedded-test/latest/embedded_test/
- https://defmt.ferrous-systems.com/
- https://developer.espressif.com/blog/2025/02/rust-esp-hal-beta/
- https://docs.espressif.com/projects/rust/esp-hal/1.0.0-beta.0/esp32/esp_hal/index.html
- https://docs.rust-embedded.org/embedonomicon/soc-support.html
- https://github.com/probe-rs/probe-rs/releases

## Proposed shape
Ship a narrowly scoped reference stack:
1. schemas for `device-profile/v0`, `device-lab-manifest/v0`, `device-run-plan/v0`, `device-capture-import/v0`, `device-run-report/v0`, and `lab-pack/v0`
2. one explicit lane map so attach/smoke, testcase harnesses, native captures, target-enablement posture, shared-lab operations, and firmware-consumer imports stop getting blurred together
3. validators + diff tooling
4. adapters for `probe-rs`, `embedded-test`, `defmt`, simple serial capture, and one vendor flasher or bootloader lane
5. example profiles for a few representative board families (Cortex-M, RP2040, ESP32-class Xtensa/RISC-V)
6. CI examples for local deskside runs and self-hosted/shared-lab runs

The winning version is boring, honest, and adapter-heavy.
It should make today’s tools more legible rather than marketing itself as a replacement stack.

## Initial pilots
- a single-board `probe-rs` attach/smoke lane
- a `probe-rs` + `embedded-test` + optional `defmt` board-test lane with per-test reset
- a mixed transport example with one RTT/`defmt` board and one serial/bootloader-only board
- one shared-lab / flaky-board / maintenance-state scenario to prove quarantine semantics are not an afterthought
- one target-enablement example carrying flash algorithm / linker / boot attachments for a board family
- one firmware-productization import example showing support/release consumers attaching device-lab evidence instead of retelling it

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - include honest support for transport differences, native capture imports, and flaky-lab states
2. **v0.2 adapters**
   - generate plans from common board/project conventions
   - ingest run results from `probe-rs`, `embedded-test`, simple serial capture, and one vendor/custom lane
3. **v0.3 CI + evidence integration**
   - show attachment into Coverage / Benchmark / Incident / Release / Support review flows
   - diff run conditions and outcomes across revisions
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one monorepo or one vendor

## Success metrics
- Teams can move board/run knowledge out of README prose and workflow YAML into portable artifacts.
- A failing hardware CI run yields a structured report with board/probe/reset/log context plus pointers to native capture imports.
- Vendor/HAL bring-up guides can publish reusable device profiles and target-enablement attachments instead of only narrative setup docs.
- Support/release claims can point to concrete device-lab evidence rather than “tested on hardware” prose.
- Embedded evidence becomes attachable to broader Rust testing, release, policy, and assurance workflows.

## Archive fit
This proposal fills a genuine hole in the current concise archive.
The repo is already strong on Cargo/build/supply-chain/testing substrates.
Device Lab Kit adds a missing **physical-target workflow substrate** without duplicating Cross Toolchain, Observability, Test Execution, or Release Pipeline work.
