# Design: Device Lab Kit (`cargo devicelab`, `lab-pack/v0`)

## Goal
Define a portable contract for describing Rust device targets, lab capabilities, planned on-device runs, imported native captures, and the normalized evidence produced by those runs.

This should **not** replace `probe-rs`, `embedded-test`, `defmt`, Embassy, BSP templates, or vendor tooling.
It should make them compose better and make physical-target workflows reviewable.

This file now sits beside an explicit lane map:
- `design/device-lab-lane-map.md` keeps **attach/smoke**, **per-test-reset harnesses**, **native capture transports**, **target-enablement**, **shared-lab operations**, and **firmware-consumer imports** distinct.
- this file keeps the artifact model and reference UX above those lanes.

## Why elevate it again now
The embedded Rust ecosystem now has enough serious pieces that the next missing contribution is not another framework, board template, or runner wrapper.
It is the thin execution/evidence boundary above them.

Signals:
- `probe-rs` now presents itself as a flexible embedded toolkit that can run programs, decode RTT/`defmt`, support many targets and probes, and even power “awesome HITL setups”.
  https://probe.rs/
- `embedded-test` documents a libtest-compatible host/target runner for ARM, RISC-V, and Xtensa, with per-test reset and structured testcase execution.
  https://docs.rs/embedded-test/latest/embedded_test/
- `probe-rs` installation now routes through `probe-rs-tools`, while still installing `probe-rs`, `cargo-flash`, and `cargo-embed`. That is another sign that durable metadata should live above one command layout.
  https://probe.rs/docs/getting-started/installation/
- The `defmt` book says `defmt-test` is for the deprecated `probe-run` path and points users to `embedded-test`.
  https://defmt.ferrous-systems.com/
- Espressif’s `esp-hal` beta announcement says hardware-in-the-loop testing was crucial for stabilization, and the crate docs say the repo uses an `xtask` to automate building, running, and testing examples.
  https://developer.espressif.com/blog/2025/02/rust-esp-hal-beta/
  https://docs.espressif.com/projects/rust/esp-hal/1.0.0-beta.0/esp32/esp_hal/index.html
- The Embedonomicon’s SoC-support guide explicitly lists flash algorithms, debugging tools like `probe-rs`, examples, templates, and debugging/testing guidance as target-enablement work.
  https://docs.rust-embedded.org/embedonomicon/soc-support.html
- `probe-rs` release notes continue to add target families, flash-algorithm controls, and attach/runtime capabilities, which makes a stable metadata/evidence layer more valuable.
  https://github.com/probe-rs/probe-rs/releases

## Core components

### 1) `device-profile/v0`
Describes a target device or board and the workflows it supports.

Required ideas:
- identity: board, SoC/MCU family, revision, optional serial or inventory id
- Rust target triple / custom target reference
- flash transport(s): SWD, JTAG, USB DFU/ROM loader, serial bootloader, network agent
- supported host tools and versions (for example `probe-rs`, vendor flasher, custom bridge)
- reset and attach strategies (`normal`, `under-reset`, boot pin requirements, boot ROM path)
- memory / linker / bootloader expectations (`memory.x`, second-stage boot, slot layout)
- log/debug channels (RTT, `defmt`, ITM, serial, semihosting)
- capability flags (`debug`, `flash`, `rtt`, `async-test`, `benchmark`, `power-cycle-required`, `exclusive-lab-access`)
- optional fixture requirements (power switch, USB hub control, GPIO jig, network reachability)
- human notes + raw attachments (SVD references, flash algorithm refs, BSP docs)

Design rule: **describe the operational truth, not just the ideal target story**.
If a board only works under-reset with a specific probe speed, the profile must be able to say so.

### 2) `device-lab-manifest/v0`
Describes what a lab or CI environment can actually provide.

Should support:
- available device/profile ids
- available probes / transport bridges
- host OS + toolchain/tool versions
- concurrency / exclusivity hints
- power-cycle / reset-control capabilities
- quarantine / flaky / maintenance state
- secrets or credentials references without embedding them
- local paths or service endpoints for runners/capture agents

This is intentionally lighter than a full lab scheduler.
It answers “what can this environment run and under which assumptions?”

### 3) `device-run-plan/v0`
Declares an intended physical-target run.

Should record:
- subject firmware identity (commit, binary, package, build profile, feature set)
- selected `device-profile/v0`
- selected lab identity or explicit “operator local” posture
- run lane (`flash-only`, `smoke`, `test`, `bench`, `bringup`, `manufacturing`, `soak`, `recovery`)
- required environment / fixtures
- timeout, retry, and reset policy
- log capture policy and artifact retention policy
- optional expected assertions (panic-free boot, RTT channel present, benchmark threshold, known serial banner)

A good v0 can be generated from templates, but the plan artifact must stand on its own.

### 4) `device-capture-import/v0`
Preserves the native outputs of one concrete host/device tool path before any normalized summary is produced.

Should support:
- originating tool/lane identity (`probe-rs run`, `embedded-test`, serial logger, vendor flasher, custom bridge)
- transport/channel identity (`RTT`, `defmt`, serial, semihosting, debugger stream)
- host-side decode assumptions and versions
- exact attachment locations or embedded snippets
- explicit lossiness notes if only summarized output survived
- correlation pointers into the selected plan/profile/lab

Design rule: **do not pretend raw/native captures and normalized run reports are the same thing**.

### 5) `device-run-report/v0`
Records what actually happened on hardware.

Should support:
- plan id + device/lab ids
- exact firmware artifact hash
- flashed/not flashed + attach mode used
- observed channels (RTT, serial, semihosting, debugger)
- structured status (`passed`, `failed`, `flaky`, `infra-failed`, `not-provisioned`, `timed-out`, `inconclusive`)
- durations
- failure class (flash, attach, reset, protocol, assertion, timeout, lab infra)
- imported capture references (`device-capture-import/v0`)
- operator or runner identity
- optional follow-up hints (quarantine suggestion, known workaround, reproduce command)

This report is the missing unit for CI diffs, bring-up handoff, and board-farm debugging.

### 6) `lab-pack/v0`
Bundle containing:
- `device-profile/v0`
- optional `device-lab-manifest/v0`
- `device-run-plan/v0`
- optional `device-capture-import/v0`
- optional `device-run-report/v0`
- optional raw attachments

This is the unit that should travel through CI, release review, vendor bring-up, or incident exchange.

### 7) `cargo devicelab`
Reference UX:
- `cargo devicelab doctor`
- `cargo devicelab plan`
- `cargo devicelab run`
- `cargo devicelab import`
- `cargo devicelab pack`
- `cargo devicelab diff`

`cargo devicelab` should begin as an explainer / adapter / report packer.
It should not try to become a universal embedded IDE, RTOS, or lab scheduler.

## What the kit should provide to others
- **Test Execution Evidence Stack:** on-device runs can import normalized run truth without flattening device/probe/reset specifics into generic test results.
- **Coverage Evidence / Benchmark Evidence / FuzzPack:** hardware-attached evidence can reference stable device/run ids instead of free-text CI logs.
- **Toolchain Productization Stack:** device plans can declare which targets/sysroots a real lab lane depends on.
- **Observability Kit:** telemetry/logging attachments can reference explicit channel types and decode assumptions.
- **Replay Kit / DST Kit:** physical-target failures can point back to real device/lab conditions that simulations try to model.
- **Release Truth / Support Envelope:** embedded releases and support claims can attach lab evidence for supported boards rather than relying on README claims alone.
- **Firmware Productization Stack:** Device Lab remains the physical-target anchor beneath footprint/runtime/support/release consumers.

## Non-goals
- Do **not** standardize HAL APIs here.
- Do **not** replace `probe-rs`, `embedded-test`, `defmt`, Embassy, vendor flashers, or board templates.
- Do **not** require one transport. RTT, serial, ITM, semihosting, and vendor-specific channels should stay distinct.
- Do **not** turn v0 into a full remote-lab scheduler or reservation system.
- Do **not** pretend all device labs are equally deterministic; flakiness and quarantine need first-class representation.
- Do **not** collapse target-enablement, smoke, testcase, capture, and release-consumer lanes into one “hardware tested” verdict.

## Overlap boundaries
- **Harness Protocol Kit** handles runner capability/discovery and host-side harness facts; Device Lab handles physical-target identity, lab capability, native capture imports, and concrete hardware execution assumptions.
- **Cross Toolchain Kit / Sysroot Pack Kit** handle provisioning host/target toolchains and stdlib identity; Device Lab references those artifacts only when relevant.
- **Observability Kit** defines telemetry contracts; Device Lab records how a concrete board/run exposed telemetry.
- **Replay Kit / DST Kit** model and reproduce failures; Device Lab captures the real physical run context that motivated those reproductions.
- **Build Interop Kit** describes build graphs/plans; Device Lab starts after a firmware artifact exists and must meet real hardware.
- **Firmware Productization Stack** imports device-lab packs; it does not redefine board/probe/reset/capture truth from prose.

## Why this could matter
A good Device Lab Kit would make embedded Rust feel less like a collection of excellent but loosely coupled rituals.
It would give the ecosystem:
- a durable board/lab metadata layer despite template churn,
- reproducible and reviewable HIL runs,
- better bring-up handoff between vendors, HAL authors, and downstream teams,
- fewer “works on my probe/board” mysteries,
- and a way for embedded evidence to plug into the same archive-wide pattern as testing, coverage, benchmarking, incidents, and release review.
