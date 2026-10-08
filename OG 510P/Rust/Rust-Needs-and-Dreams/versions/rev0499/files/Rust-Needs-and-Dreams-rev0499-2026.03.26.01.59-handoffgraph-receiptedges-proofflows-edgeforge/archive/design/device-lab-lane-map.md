# Design: Device Lab lane map (attach/smoke, per-test-reset harnesses, native capture transports, target-enablement, shared-lab operations, and firmware-consumer imports)

## Goal
Sharpen **Device Lab Kit** so the archive stops treating “hardware tested” as one bucket.
Rust embedded work already spans materially different lanes, and they differ in **what is being proven**, **which host↔device path is authoritative**, **how much lab state matters**, **which native captures exist**, and **what later consumers may honestly conclude**.

The archive should therefore keep device-lab review grounded in a lane map instead of one flattened “board support” or “HIL passed” story.

## Signals from the current ecosystem
- `probe-rs` explicitly positions itself as a flexible embedded toolkit that can run programs, decode RTT/`defmt`, support many targets and probes, power VS Code / DAP debugging, and enable “awesome HITL setups”.
  https://probe.rs/
- The `probe-rs` installation docs now make `probe-rs-tools` the install unit while still installing `probe-rs`, `cargo-flash`, and `cargo-embed`. That is a strong sign that command layout can move while the underlying board/lab facts stay the same.
  https://probe.rs/docs/getting-started/installation/
- `embedded-test` documents a libtest-compatible host/target runner for ARM, RISC-V, and Xtensa that reads tests from the ELF, flashes once, resets per testcase, signals which test to run, and reports results.
  https://docs.rs/embedded-test/latest/embedded_test/
- The `defmt` book now says `defmt-test` belongs to the deprecated `probe-run` lane and points users to `embedded-test` for better `probe-rs` integration. That is exactly the kind of lane distinction the archive should preserve.
  https://defmt.ferrous-systems.com/
- Espressif’s `esp-hal` beta announcement says hardware-in-the-loop testing was crucial for stabilization, while the crate docs say the repository uses an `xtask` to automate building, running, and testing examples.
  https://developer.espressif.com/blog/2025/02/rust-esp-hal-beta/
  https://docs.espressif.com/projects/rust/esp-hal/1.0.0-beta.0/esp32/esp_hal/index.html
- The Embedonomicon’s SoC-support guide keeps flash algorithms, debugging tools like `probe-rs`, examples, templates, and debugging/testing guidance explicit. That means target enablement is a real adjacent lane, not just a footnote to smoke tests.
  https://docs.rust-embedded.org/embedonomicon/soc-support.html
- `probe-rs` 0.31.0 release notes continue to add target families, flash-algorithm controls, and attach/runtime capabilities. That reinforces the need for durable metadata above one fast-moving tool surface.
  https://github.com/probe-rs/probe-rs/releases

## The lanes

### 1) Desk-side attach / flash / smoke lane
This is the lowest-friction physical-target lane.

What defines it:
- one identified board or device profile
- one selected transport/probe path
- flash and attach posture
- minimal run success criteria (boots, banner, RTT channel present, returns control, no panic)
- enough native capture to explain pass/fail

Why it deserves its own lane:
- it is the first honest proof that a firmware artifact can meet a real target
- it does **not** require full test-harness semantics
- it is where reset mode, probe speed, boot pins, and “works only under reset” truths first become visible

Design rule:
- keep attach/smoke truth separate from later testcase, benchmark, or support claims

### 2) Per-test-reset harness lane
This is the structured on-device test lane.

What defines it:
- runner/harness semantics from `embedded-test` or an equivalent host↔device test protocol
- testcase discovery from the produced artifact
- per-test reset or equivalent isolation posture
- testcase-level timeout / ignore / should-panic semantics
- testcase result aggregation distinct from raw transport output

Why it deserves its own lane:
- `embedded-test` explicitly defines a test protocol rather than only “run firmware once”
- per-test reset semantics materially change what success and failure mean
- async-test and libtest-compatibility posture belong here, not in generic smoke-test claims

Design rule:
- keep harness semantics separate from board identity and separate from transport/capture choices

### 3) Native capture / transport lane
This is the lane that preserves what the board and host actually exchanged.

What defines it:
- RTT / `defmt`, serial, semihosting, debugger streams, or vendor-specific channels
- host-side decode assumptions and versions
- raw versus summarized capture preservation
- explicit lossiness when only a decoded or filtered view survives

Why it deserves its own lane:
- `probe-rs` already makes RTT/`defmt` a first-class path, while `defmt` keeps semihosting, RTT, and other transports distinct
- a passing board run through RTT/`defmt` is not the same native-capture posture as serial logs or semihosting
- downstream observability, test, coverage, and incident consumers need the native-capture boundary preserved

Design rule:
- keep capture/transport truth separate from execution/harness truth and from later normalized reports

### 4) Target-enablement / bring-up lane
This is the lane where a board family becomes supportable at all.

What defines it:
- target description availability
- flash-algorithm posture
- linker/memory/bootloader expectations
- template / example / BSP / bring-up guidance attachments
- whether a target family is in “barely reachable”, “flashable”, “debuggable”, or “runner-ready” posture

Why it deserves its own lane:
- the Embedonomicon treats flash algorithms, examples, templates, and debugging/testing guidance as target-enablement work
- `probe-rs` itself highlights target descriptions and flash-algorithm templates with automatic tests
- this lane answers *can the ecosystem even talk to this target honestly?*, which is prior to ordinary smoke or test execution

Design rule:
- keep target-enablement posture separate from the claim that one downstream firmware project already passed tests on one board

### 5) Shared-lab operations / quarantine lane
This is the operational lane for hardware CI and shared labs.

What defines it:
- lab manifest, capacity, exclusivity, and fixture control
- maintenance/quarantine/flaky states
- power-cycle requirements and infra ownership
- operator versus automated runner identity
- infra-failed versus target-failed versus inconclusive distinctions

Why it deserves its own lane:
- real labs are not just “the same board, but in CI”
- hardware failures and infrastructure failures are materially different downstream facts
- if this lane is not explicit, “board support” claims get polluted by shared-lab folklore and invisible repairs

Design rule:
- keep shared-lab state separate from board capability and separate from firmware-result interpretation

### 6) Firmware-consumer import lane
This is the lane where device-lab evidence becomes useful outside embedded bring-up.

What defines it:
- imports into support/readiness/release review
- bounded imports into coverage, benchmark, observability, incident, and firmware-productization consumers
- explicit “what this hardware evidence does and does not prove” posture
- stable references from support statements back to lab packs and run reports

Why it deserves its own lane:
- “tested on hardware” is not the same as “device-lab evidence exists and can be inspected”
- firmware productization depends on support/release consumers importing device truth honestly
- the archive should not let later consumers silently rewrite hardware evidence in prose

Design rule:
- keep consumer-import posture separate from raw device/lab/run facts and from target-enablement posture

## Review rules that follow from the lane map
1. Keep **board identity** separate from **runner/harness semantics**.
2. Keep **execution lanes** separate from **native capture/transport lanes**.
3. Keep **target-enablement posture** separate from **downstream firmware-success claims**.
4. Keep **shared-lab operational state** separate from **firmware result meaning**.
5. Keep **desk-side smoke** separate from **per-test-reset harness truth**.
6. Keep **normalized run reports** separate from **native captures**.
7. Keep **consumer-import conclusions** separate from **source device-lab evidence**.
8. Keep **tool layout/install churn** separate from **durable board/lab metadata**.

## What a worthy contribution should look like
The worthy contribution here is **not**:
- another embedded framework,
- another board-template empire,
- another runner wrapper,
- another hosted board-farm scheduler,
- or another README badge that says “tested on hardware”.

It is a thin `cargo devicelab` / `lab-pack/v0` layer that can preserve:
- lane identity,
- board/probe/fixture truth,
- runner/harness posture,
- native capture imports,
- target-enablement attachments,
- lab capability/quarantine state,
- normalized run reports,
- and bounded firmware/support/release handoffs.

That means downstream reviewers can answer:
- *was this only an attach/smoke lane, or a per-test-reset lane?*
- *which board/probe/reset path actually ran?*
- *what native capture channel existed, and what decode assumptions were used?*
- *is this target merely reachable, or broadly enablement-ready?*
- *did failure belong to firmware, the lab, or target bring-up posture?*
- *what may a support/release consumer conclude, and what must remain only a device-lab fact?*

## Immediate archive consequences
Read this together with:
- `design/device-lab-kit.md`
- `design/device-lab-pilot-program.md`
- `gaps/embedded-device-labs-and-hardware-in-the-loop.md`
- `proposals/epic-device-lab-kit.md`
- `design/test-execution-evidence-stack.md`
- `design/firmware-productization-stack.md`

The archive should now prefer **lane-aware device-lab packs before one fake “hardware tested” status**, and it should keep device-lab, test-execution, observability, toolchain, and firmware-productization consumers on bounded import paths.
