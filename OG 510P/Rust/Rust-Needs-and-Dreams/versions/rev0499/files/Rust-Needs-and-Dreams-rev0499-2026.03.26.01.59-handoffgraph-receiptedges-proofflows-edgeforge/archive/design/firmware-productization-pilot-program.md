# Design: Firmware Productization Pilot Program (Device Truth → Target/Toolchain Truth → Footprint Truth → Runtime Evidence → Support/Release Consumers)

## Goal
Turn the **Firmware Productization Stack** into a ranked execution program so the archive can answer a practical question: what is the first boring, portable, ecosystem-shaping contribution that would materially improve how Rust firmware is built, exercised, supported, and shipped?

This pilot now sits under an explicit proposal layer: [`proposals/epic-firmware-productization-stack.md`](../proposals/epic-firmware-productization-stack.md) should own the stack-level contract, while this file keeps the rollout order honest.

The pilot program should not chase a universal embedded platform.
It should sequence the contribution so each lane proves something concrete before the next lane expands scope.

## Why a pilot program is necessary
Embedded ideas are unusually easy to overgeneralize.
Rust already has real ingredients — HAL traits, async frameworks, vendor SDKs, probe/debug stacks, on-device tests, linker/runtime crates, and board templates — but those ingredients live at different authority layers and fail in different ways.
A credible plan therefore needs to decide:
- when real board/probe/run evidence is already enough,
- when target/sysroot/linker truth must be attached,
- when RAM/FLASH/stack posture becomes part of the contract,
- when logs/fault reports must travel with the run,
- and which support/release consumers justify graduation.

## Principles
1. **Start from physical truth, not abstraction elegance**
   - a board/probe/reset/log report is worth more than a universal framework pitch.
2. **Respect multiple execution families**
   - blocking, async/Embassy, RTIC, vendor SDK, and custom-runtime lanes are all real.
3. **Keep build truth and run truth separate**
   - target/linker/sysroot success is not the same thing as successful flashing or on-device execution.
4. **Resource truth is part of firmware truth**
   - RAM/FLASH/stack/layout posture should be reviewable before release, not discovered after bring-up pain.
5. **Support claims must import evidence**
   - docs, release notes, and board support pages should consume real artifacts instead of retelling them loosely.
6. **Partial truth is still useful**
   - a pack that only knows board identity plus toolchain activation can still help bring-up, CI, and archaeology.

## Common artifacts this program should drive
- `firmware-lane-brief/v0` — declare which pilot lane is being exercised, scope, targets, and non-goals.
- `firmware-escalation-policy/v0` — rules for when a subject must move from device-only evidence to toolchain/footprint/observability/support evidence.
- `firmware-correlation-budget/v0` — bounded rules for correlating board/run/toolchain/resource/log facts without pretending perfect universal inference.
- `firmware-readiness-scorecard/v0` — not a fake maturity score; a lane-by-lane checklist showing which truths exist and which remain absent.
- `firmware-pilot-pack/v0` — attachable summary pack importing the lane artifacts used in a specific pilot.

## Ranked pilot lanes

### 1) Device profile + run-report lane
**Why first:** it hits the most universal embedded pain with the least ecosystem coercion.

**Concrete scope**
- board / SoC / revision identity,
- probe and transport choices,
- flash / attach / reset posture,
- run lane (`flash-only`, `smoke`, `test`, `bringup`),
- log channel expectations,
- structured result and failure classes.

**Graduation bar**
- the pack can explain which hardware was used, how it was reached, what actually ran, and why it passed or failed.

**What success looks like**
- a `probe-rs` / `embedded-test` first proof is acceptable, provided the artifact family stays honest enough that vendor flashers, serial bootloaders, or non-libtest lanes do not feel bolted on later.

### 2) Target / linker / sysroot lane
**Why second:** once a hardware run exists, the next hidden source of pain is build activation truth.

**Concrete scope**
- target triple or custom target,
- stable/nightly posture,
- linker/C toolchain selection,
- sysroot/SDK identity,
- `build-std` or custom-stdlib assumptions,
- generated Cargo/config/environment evidence.

**Graduation bar**
- another engineer or CI lane can explain how the image was produced without reverse-engineering shell history.

### 3) Footprint / layout lane
**Why third:** firmware that runs once but has no durable budget truth is not yet supportable.

**Concrete scope**
- FLASH/RAM/stack budgets,
- binary and section sizes,
- vector-table / boot-window / layout assumptions,
- optimization-profile tradeoffs,
- drift diffs across commits/targets/profiles.

**Graduation bar**
- the pack can explain whether the firmware fit, what consumed the budget, and which layout assumptions matter to keep it bootable.

### 4) Runtime evidence / fault lane
**Why fourth:** once builds and runs are honest, make runtime evidence durable.

**Concrete scope**
- `defmt`/RTT/serial/semihosting/debugger output posture,
- panic/fault capture assumptions,
- structured versus unstructured host decoding,
- log/fault attachments,
- explicit `infra-failed`, `inconclusive`, and `missing-channel` states.

**Graduation bar**
- support and incident consumers can distinguish firmware faults from probe/lab/infrastructure faults without reading raw CI prose.

### 5) Support / docs / release-consumer lane
**Why fifth:** this is where the stack proves it matters beyond development-time experimentation.

**Concrete scope**
- supported boards/chips/probes/host lanes,
- setup and recovery docs,
- checked examples,
- release attachments importing device/toolchain/footprint/runtime evidence,
- archaeology diffs for “what firmware/support story changed?”

**Graduation bar**
- a release or support consumer can answer what is actually supported and what evidence accompanied the shipped firmware.

## What to defer
- a universal embedded IDE,
- a hosted lab scheduler,
- a one-true board template,
- one mega-schema for all firmware workflows,
- policy-first hard gates before the evidence lanes exist,
- “AI firmware copilots” that claim universal understanding without stable artifacts.

## Immediate archive consequences
- Treat **Device Lab Kit** as the anchor of a broader firmware-productization seam rather than an isolated HIL/report idea, and use `design/device-lab-pilot-program.md` as the ranked entry path before widening into the rest of the firmware stack.
- Treat **Cross Toolchain Kit + Sysroot Pack Kit** as the build-activation half of the story rather than a generic cross-compilation convenience lane.
- Treat **Footprint Kit** as a firmware product concern, not just a benchmarking side quest.
- Treat **Support Envelope + Release Truth** as downstream import lanes that should consume lower-layer firmware evidence instead of reconstructing it.
- Add a specific amnesia resistor so later revisions cannot collapse device/run truth, target/toolchain truth, footprint/layout truth, observability/fault truth, and support/release truth into one note.

## Read this together with
- `design/firmware-productization-stack.md`
- `design/device-lab-kit.md`
- `design/cross-toolchain-kit.md`
- `design/sysroot-pack-kit.md`
- `design/footprint-kit.md`
- `design/observability-kit.md`
- `design/support-envelope-kit.md`
- `design/release-pipeline-kit.md`
