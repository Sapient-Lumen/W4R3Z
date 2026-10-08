# Design note: Firmware Productization Stack (Device Lab + Toolchain Productization + Footprint + Observability + Support Envelope + Release Truth)

## Goal
Define the **division of labor and consumer flow** between Rust device-lab truth, target/toolchain/sysroot truth, memory/footprint truth, runtime logging/fault truth, support/docs truth, and release/update truth so the ecosystem can make **real firmware products** reviewable without anointing one HAL, one async framework, one board template, or one flasher/debugger stack as the answer.

This is **not** a new top-level kit.
It is a stack note explaining how existing archive pieces should compose, with `design/device-lab-pilot-program.md` now acting as the explicit first execution path for the physical-target layer:
- [`design/device-lab-kit.md`](./device-lab-kit.md)
- [`design/cross-toolchain-kit.md`](./cross-toolchain-kit.md)
- [`design/sysroot-pack-kit.md`](./sysroot-pack-kit.md)
- [`design/footprint-kit.md`](./footprint-kit.md)
- [`design/observability-kit.md`](./observability-kit.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md)
- [`design/docproof-kit.md`](./docproof-kit.md)

## Why this note is needed now
Rust’s current embedded signals are no longer saying only “microcontroller work in Rust is possible.” They are saying the ecosystem now has enough serious ingredients that the next missing contribution is the **productization layer above them**:
- The 2025 Rust debugging survey launch says debugging remains one of the biggest challenges annoying Rust developers and that support quality varies substantially across debuggers and operating systems. For firmware, that raises the value of portable runtime-evidence artifacts above debugger-specific setup lore.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- `embedded-hal` 1.0 explicitly scopes itself as a foundation for platform-agnostic drivers and now has companion crates for async and nb execution models. That is a strong signal that the missing standardization pressure is **above** the trait layer, not inside it.
  https://docs.rs/embedded-hal/
  https://blog.rust-embedded.org/embedded-hal-v1/
- `probe-rs` now gives Rust a serious host↔device lane for flashing, attach, RTT, and `defmt` output, and its `run` docs say it should be the preferred embedded-development path where applicable. At the same time, the probe-rs VS Code debugger is still documented as pre-production/Alpha, which is a reminder that runtime-evidence portability matters above any one debugger UX.
  https://probe.rs/docs/tools/probe-rs/
  https://probe.rs/docs/tools/debugger/
- Embassy now presents itself as the next-generation framework for embedded applications and explicitly ties async to safe, correct, and energy-efficient embedded code. RTIC still presents a hardware-accelerated real-time concurrency model, and Hubris presents a memory-isolated microcontroller operating environment with restartable tasks and offline dumps. That makes firmware execution-model diversity a reality the stack must preserve rather than erase.
  https://embassy.dev/book/
  https://github.com/rtic-rs/rtic
  https://hubris.oxide.computer/
- Espressif’s `esp-hal` reached a 1.0 release in October 2025 as the **first vendor-backed Rust SDK** for embedded devices, with both async and blocking modes, a project generator, and a curated book. The ESP book’s logging docs explicitly recommend pairing `defmt` with `probe-rs` for best results, which is exactly the kind of cross-tooling operational truth a product layer should preserve.
  https://developer.espressif.com/blog/2025/10/esp-hal-1/
  https://docs.espressif.com/projects/rust/book/application-development/logging.html
- The Embedonomicon’s SoC-support guide is unusually explicit that vendor-ready Rust support requires documentation, SVD/register descriptions, flash algorithms, and community support posture. Those are productization facts, not just crate internals.
  https://docs.rust-embedded.org/embedonomicon/soc-support.html
- The build-std project goal remains active in 2025H2, which is a reminder that std/sysroot identity for unusual or constrained targets is still moving ecosystem terrain rather than settled plumbing.
  https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
- Tool churn is also instructive: `probe-run` was deprecated in favor of `probe-rs`, and the migration note explicitly says there is no replacement for the older `--json` structured-log output. That is exactly the kind of gap a portable firmware evidence layer should close.
  https://ferrous-systems.com/blog/probe-run-deprecation/
- The best current research picture is not “embedded Rust is done.” The 2024 CCS study on Rust for embedded systems found inadequate software support, poorly organized documentation, tool failures on embedded crates, and build/diversity/interoperability challenges. A thin productization stack is a better response than another monolithic framework pitch.
  https://arxiv.org/html/2311.05063v2

Together these signals justify treating firmware/embedded productization as a **frontier-worthy ecosystem seam** rather than leaving Rust firmware work as a pile of HAL traits, board templates, linker scripts, probe commands, CI YAML, and README folklore.

## Stack layers

### 1) Device Lab: board / probe / flash / reset / run truth
Device Lab owns the **real device execution boundary**:
- board / SoC / revision identity
- probe / transport / boot path assumptions
- flash / attach / reset / recovery posture
- test/bench/bring-up run plans and reports
- lab capability and fixture truth
- attached logs, traces, and operator notes from real runs

Device Lab answers questions like:
- “Which exact board and probe path was exercised?”
- “Was this a flash-only lane, a smoke lane, a per-test-reset lane, or a bring-up lane?”
- “What actually happened on real hardware, and under which reset/logging conditions?”

Design rule: **do not flatten physical-target truth into host-side CI success or one cargo runner line**.

### 2) Toolchain Productization: target / linker / sysroot / stdlib truth
Toolchain Productization owns the **build activation boundary**:
- built-in versus custom targets
- linker and C toolchain posture
- sysroot/SDK identity
- `build-std` / custom-stdlib assumptions
- nightly versus stable requirements
- generated Cargo config and environment activation

This layer answers questions like:
- “Which target/sysroot/linker path actually built this firmware?”
- “Did this target need nightly or custom stdlib construction?”
- “Was success tied to one host image or to a portable toolchain description?”

Design rule: **firmware support should not depend on hidden linker folklore and shell state alone**.

### 3) Footprint: memory / flash / stack / profile truth
Footprint owns the **resource and layout boundary**:
- binary and section sizes
- RAM/FLASH budgets
- stack and allocation evidence
- optimization-profile tradeoffs
- special layout assumptions (vector table, boot configuration windows, section placement)
- drift diffs across commits, targets, and build profiles

This layer answers questions like:
- “Did the image fit, and under which profile?”
- “Which sections or symbols consumed the budget?”
- “What changed in RAM/FLASH/stack posture between revisions?”

Design rule: **resource truth must not live only in linker scripts, size screenshots, or one successful lab run**.

### 4) Observability: log / fault / trace / runtime evidence truth
Observability owns the **runtime evidence boundary**:
- RTT / `defmt` / serial / semihosting / debugger output posture
- panic/fault capture assumptions
- structured versus unstructured logs
- probe/host decoding expectations
- timings, counters, and attached traces when available
- explicit unknown/inconclusive states when channels are missing

This layer answers questions like:
- “How are runtime facts observed on this device?”
- “Which logs were emitted on-target versus synthesized on-host?”
- “Which failures were genuine firmware behavior versus probe/lab issues?”

Design rule: **do not flatten `defmt`, RTT, serial, semihosting, and debugger evidence into one fake logging story**.

### 5) Support Envelope + DocProof: supported reality
Support Envelope and DocProof own the **promise boundary**:
- supported boards/chips/targets/probes/host lanes
- runtime floors and prerequisite tooling
- docs/setup/recovery truth
- source-build versus shipped-artifact posture
- checked examples and bring-up guides
- support tiers and explicit exclusions

This layer answers questions like:
- “What hardware/host/probe combinations are actually supported?”
- “What can users rely on during bring-up, debugging, and updates?”
- “Do the docs match the real board/toolchain/lab story?”

Design rule: **one vendor demo board, one README, or one passing HIL lane is not the support contract**.

### 6) Release Truth: artifact / update / archaeology truth
Release Truth owns the **shipped-firmware boundary**:
- firmware image identities and build provenance
- package/bundle/update artifact posture
- release-time attachments to device-lab, toolchain, footprint, and observability evidence
- change notes for boot path or support changes
- archaeology/diff lanes for “what firmware really shipped?”

This layer answers questions like:
- “Which image actually shipped to devices?”
- “What board/support/toolchain/resource evidence accompanied the release?”
- “What changed in support or boot/update posture across releases?”

Design rule: **release truth should import device/toolchain/resource/runtime evidence rather than restating it from scratch**.

### 7) Downstream consumers
The stack becomes ecosystem-shaping when real consumers can import it without flattening it:
- **release/recovery/update** consumers can attach real board/toolchain/resource evidence to firmware artifacts;
- **support/docs** consumers can answer bring-up and probe questions from artifacts instead of team memory;
- **incident/debug** consumers can distinguish firmware faults from lab/probe/toolchain faults;
- **vendor / BSP / atlas** consumers can compare enablement quality across targets without pretending all embedded lanes are the same.

Design rule: **consumers import selected firmware-productization facts; they do not redefine the stack**.

## What an epic contribution should look like in practice
A worthy contribution here is not “one embedded framework to rule them all”, “another HAL unification push”, or “a prettier flashing CLI”.
It is a portable, reviewable stack with clear boundaries:

1. **device profile / run plan / report truth first**
   - prove stable `device-profile`, `device-run-plan`, and `device-run-report` artifacts on one real board family;
2. **toolchain / target / sysroot activation second**
   - attach real target/linker/sysroot/build-std posture so successful firmware builds become portable evidence instead of host folklore;
3. **footprint / layout evidence third**
   - prove RAM/FLASH/stack/section-budget reports that can travel with firmware releases and target reviews;
4. **observability / fault evidence fourth**
   - attach the actual logging/fault/trace channels that make firmware runs debuggable and supportable;
5. **support / docs / release consumers fifth**
   - prove board support claims, setup/recovery docs, and release/update artifacts can import the lower layers honestly.

An aggregate bundle may eventually exist, but it should remain a **thin pack of linked artifacts**, not a mega-schema that erases board identity, toolchain posture, resource budgets, and runtime evidence into one fake “firmware readiness” number.

## Ranked first execution lanes
1. **Board / probe / run lane**
   - best first exporter because real firmware teams already need board/probe/reset/log truth even when the rest of the stack is immature.
2. **Target / sysroot / linker lane**
   - proves firmware success can survive host-image churn and custom-target reality.
3. **Resource / layout lane**
   - proves Flash/RAM/stack/section budgets are first-class review artifacts rather than archaeology.
4. **Logging / fault / runtime-evidence lane**
   - proves firmware support can reason from captured evidence instead of screenshots and operator memory.
5. **Support / release / incident lane**
   - proves the stack matters once firmware is shipped and supported, not only while it is being developed.

## Non-goals
- one universal embedded framework;
- reopening the `embedded-hal` scope fight;
- pretending async, blocking, RTIC, and bare-loop firmware all want the same control plane;
- flattening board/probe/run truth, target/sysroot truth, memory/footprint truth, and log/fault truth into one fake “embedded support” badge;
- requiring one probe, one boot path, or one logging transport.

## Archive implications
- The archive should now treat **Device Lab + Toolchain Productization + Footprint + Observability + Support Envelope + Release Truth** as a coupled **Firmware Productization Stack** in frontier discussions.
- Future revisions should prefer **board/probe/run truth, target/sysroot activation, footprint/layout evidence, logging/fault evidence, and support/release imports** over another board template, runner wrapper, lab daemon, or framework bake-off.
- When support, release, incident, or atlas work cites embedded readiness, it should import **device-lab**, **toolchain**, **footprint**, **observability**, and **support** facts separately.

## References (signals)
- 2024 State of Rust survey results:
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- `embedded-hal` repository / scope:
  https://github.com/rust-embedded/embedded-hal
- `probe-rs`:
  https://probe.rs/
- `embedded-test`:
  https://github.com/probe-rs/embedded-test
- Embassy:
  https://embassy.dev/
- `esp-hal` beta + 1.0 release:
  https://developer.espressif.com/blog/2025/02/rust-esp-hal-beta/
  https://developer.espressif.com/blog/2025/10/esp-hal-1/
- Embedonomicon SoC-support guide:
  https://docs.rust-embedded.org/embedonomicon/soc-support.html
- build-std project goal:
  https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
- probe-run deprecation note:
  https://ferrous-systems.com/blog/probe-run-deprecation/
- Rust for Embedded Systems study:
  https://arxiv.org/html/2311.05063v2
- Embedded Rust book speed-vs-size discussion:
  https://docs.rust-embedded.org/book/unsorted/speed-vs-size.html
- `cortex-m-rt` runtime / memory-layout expectations:
  https://docs.rs/cortex-m-rt/latest/cortex_m_rt/
  https://docs.rust-embedded.org/embedonomicon/compiler-support.html
