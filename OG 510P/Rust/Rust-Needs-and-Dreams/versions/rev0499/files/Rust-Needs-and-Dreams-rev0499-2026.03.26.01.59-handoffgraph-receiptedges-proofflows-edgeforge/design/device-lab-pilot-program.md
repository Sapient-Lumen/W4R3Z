# Design: Device Lab Pilot Program (attach/smoke → per-test-reset harnesses → transport/capture imports → shared-lab operations → firmware-consumer handoffs)

## Goal
Turn **Device Lab Kit** into a ranked execution program so the archive can answer a practical question: what is the first boring, portable, ecosystem-shaping contribution that would materially improve how Rust teams run, debug, and review firmware on real hardware?

This file now sits under two adjacent constraints:
- [`proposals/epic-device-lab-kit.md`](../proposals/epic-device-lab-kit.md) owns the product thesis.
- [`design/device-lab-lane-map.md`](./device-lab-lane-map.md) keeps the lanes honest so this rollout does not blur smoke tests, testcase harnesses, transport capture, target enablement, shared-lab operations, and downstream imports.

## Why a pilot program is necessary now
Rust embedded work no longer lacks tools in the abstract.
It lacks a stable way to describe and exchange the concrete hardware reality those tools depend on.

The current ecosystem signals all point the same way:
- `probe-rs` is strong enough to run, flash, debug, decode RTT/`defmt`, support many probes/targets, and power HITL setups.
- `embedded-test` proves that libtest-compatible on-device testing across ARM, RISC-V, and Xtensa is practical, including per-test reset semantics.
- `probe-rs` installation now routes through `probe-rs-tools`, which is a reminder that CLI packaging can move while board/lab truths remain the same.
- the `defmt` book explicitly routes users away from the older `probe-run` testing path and toward `embedded-test` + `probe-rs`.
- Espressif’s `esp-hal` beta says HIL testing was crucial for stabilization, while the crate docs show build/run/test automation as part of the repository contract.
- the Embedonomicon still treats flash algorithms, target tooling, examples, templates, and debug/test guidance as part of real SoC enablement.

## Principles
1. **Start with physical truth, not framework elegance**
   - a board/probe/reset/log report is worth more than another embedded platform pitch.
2. **Keep native captures distinct from normalized reports**
   - raw `probe-rs`, serial, or custom bridge output is not the same thing as a portable run summary.
3. **Respect transport plurality**
   - RTT, `defmt`, serial, semihosting, vendor boot ROMs, and custom bridges are all real lanes.
4. **Make flakiness and maintenance state first-class**
   - board farms and shared labs are valuable precisely because hardware is not frictionless.
5. **Let downstream consumers import evidence**
   - support docs, coverage, performance, release, and incident consumers should import device-lab artifacts rather than restating them from memory.
6. **Prefer boring adapters over lab empires**
   - the credible first contribution is schemas + importers + reports, not a hosted scheduler or universal IDE.

## Common artifacts this program should drive
- `device-profile/v0` — board / SoC / transport / reset / logging capability truth.
- `device-lab-manifest/v0` — what one host/lab can actually provide, including maintenance or quarantine state.
- `device-run-plan/v0` — selected firmware subject + board/lab + lane + expectations.
- `device-capture-import/v0` — native output imported from one concrete tool or transport path.
- `device-run-report/v0` — normalized outcome with explicit failure class and imported-capture references.
- `lab-pack/v0` — attachable bundle for CI, bring-up, support, release review, or incident exchange.
- `device-lab-readiness-scorecard/v0` — a bounded checklist showing which lanes a subject actually supports, not a fake maturity score.

## Ranked pilot lanes

### 1) Single-board attach / flash / smoke lane
**Why first:** it gives the archive a real board/probe/reset/log identity without depending on custom harnesses or advanced scheduling.

**Concrete scope**
- one representative board profile
- one selected probe/transport path
- flash-only and smoke lanes
- reset / attach posture
- one concrete logging/capture lane
- structured failure classes

**Graduation bar**
- another engineer can tell which board was used, how it was reached, what binary ran, and why it passed or failed.

### 2) `embedded-test` per-test-reset harness lane
**Why second:** it proves that modern on-device testing is a real reusable consumer, not a one-off runner trick.

**Concrete scope**
- `probe-rs` + `embedded-test` path
- per-test reset semantics
- optional async/init support
- testcase-level timeouts and ignored/should-panic posture
- imported `defmt` or `log` capture when present

**Graduation bar**
- one run pack can explain both the selected test lane and the per-test/device-reset behavior that produced the result.

### 3) Mixed transport / native-capture lane
**Why third:** once the archive can describe one good execution path, it needs to prove that the contract sits above one transport or one host output format.

**Concrete scope**
- one RTT/`defmt` lane
- one serial or semihosting lane
- optional vendor flasher or bootloader lane
- imported-capture lossiness notes
- same normalized report shape across unlike native outputs

**Graduation bar**
- the archive can compare unlike device runs without pretending their captures were produced by the same tool or channel.

### 4) Shared lab / quarantine / maintenance lane
**Why fourth:** real hardware CI is not just one desk setup; it is also contention, power cycling, flaky boards, and repair windows.

**Concrete scope**
- lab manifest with capability and exclusivity hints
- maintenance/quarantine states
- power-cycle-required or fixture-required lanes
- operator versus automated runner identity
- infra-failed versus device-failed versus inconclusive outcomes

**Graduation bar**
- a failed run can explain whether the problem belonged to firmware, probe/device conditions, or lab infrastructure.

### 5) Target-enablement / bring-up attachments lane
**Why fifth:** once execution lanes exist, the archive needs to show that target descriptions, flash algorithms, linker/boot facts, and example/template references are first-class evidence rather than stray notes.

**Concrete scope**
- target/SoC family attachments
- flash algorithm references
- linker/memory/bootloader notes
- board-template or BSP references when relevant
- “reachable vs flashable vs debuggable vs harness-ready” posture

**Graduation bar**
- one board family can be described without pretending a single smoke run proves complete target enablement.

### 6) Firmware-productization import lane
**Why sixth:** this is where Device Lab proves it matters beyond development-time debugging.

**Concrete scope**
- attach lab packs to support/release review
- connect to footprint or runtime-observability evidence when present
- import selected device-run evidence into coverage, benchmark, or incident consumers without flattening it
- publish a bounded readiness scorecard for one board family

**Graduation bar**
- support/release consumers can answer what hardware evidence exists for a firmware claim without reading CI folklore.

## What to defer
- a universal embedded IDE
- a hosted board-farm scheduler
- automatic probe reservation/orchestration policy for everyone
- universal HAL or framework coordination
- one mega-schema covering build, run, support, and release all at once
- “AI firmware copilots” that claim hardware understanding without stable device-lab artifacts

## Immediate archive consequences
- Re-elevate **Device Lab Kit** as a frontier-worthy execution seam, not only a Tier 1/2 note.
- Add `design/device-lab-lane-map.md` and use it to keep attach/smoke, testcase, transport/capture, shared-lab, bring-up, and firmware-consumer claims distinct.
- Keep **Test Execution Evidence Stack** responsible for generic run truth while letting Device Lab import and specialize that truth for physical targets.
- Keep **Firmware Productization Stack** anchored on Device Lab rather than letting board/probe/reset reality disappear into toolchain or release prose.
- Add an amnesia resistor so future revisions cannot collapse device profile, lab capability, run lane, native captures, normalized run reports, target-enablement posture, and downstream support/release claims into one vague “hardware tested” statement.

## Read this together with
- `design/device-lab-kit.md`
- `design/device-lab-lane-map.md`
- `proposals/epic-device-lab-kit.md`
- `gaps/embedded-device-labs-and-hardware-in-the-loop.md`
- `design/firmware-productization-stack.md`
- `design/firmware-productization-pilot-program.md`
- `design/test-execution-evidence-stack.md`
