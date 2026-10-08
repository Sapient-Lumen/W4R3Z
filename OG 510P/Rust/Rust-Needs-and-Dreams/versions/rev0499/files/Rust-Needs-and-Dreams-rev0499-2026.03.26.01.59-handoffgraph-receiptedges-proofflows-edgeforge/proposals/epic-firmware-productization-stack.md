# Epic proposal: Firmware Productization Stack (`cargo firmware-product`, `firmware-product-pack/v0`)

## One-line thesis
Build a thin Rust companion layer for **real firmware products** that links **board/probe/run truth**, **target/linker/sysroot/build-std truth**, **footprint/layout truth**, **runtime logging/fault truth**, and **release/support truth** into one portable review boundary without pretending one HAL, one async framework, one RTOS, one board template, or one probe stack has already won.

## Why this is now worth doing
Rust’s firmware story is now strong enough that the missing contribution looks like a **product boundary above the ingredients** rather than another ingredient:
- `embedded-hal` 1.0 is explicit that it provides platform-agnostic driver traits, includes companion crates for async and nb execution models, and does not try to be the whole target platform. That is a strong signal that the next standardization pressure is **above** the trait layer, not inside it.
  https://docs.rs/embedded-hal/
  https://blog.rust-embedded.org/embedded-hal-v1/
- Embassy now presents itself as the next-generation framework for embedded applications, focused on safe, correct, and energy-efficient code, while RTIC still presents a hardware-accelerated real-time concurrency model and Hubris presents a memory-isolated task-based operating environment. The ecosystem already has materially different runtime families; the missing contribution should preserve that plurality instead of erasing it.
  https://embassy.dev/book/
  https://github.com/rtic-rs/rtic
  https://hubris.oxide.computer/
- The host↔device tooling lane is real but still uneven. `probe-rs run` is explicit that it should be the preferred path where applicable and that it can flash, start, and print RTT/defmt logs from `cargo run`; the probe-rs VS Code debugger docs are equally explicit that the debugger extension is still pre-production/Alpha; and the old `probe-run` deprecation note says there is no replacement for the older `--json` structured-log output. That is exactly the pattern where a reviewable evidence layer above tooling becomes valuable.
  https://probe.rs/docs/tools/probe-rs/
  https://probe.rs/docs/tools/debugger/
  https://ferrous-systems.com/blog/probe-run-deprecation/
- Vendor-backed enablement is now real enough to justify boring product contracts. Espressif’s October 2025 `esp-hal` 1.0 announcement calls it the first vendor-backed Rust SDK, exposes both async and blocking modes, and ships a project generator plus a curated book; the ESP book’s logging docs explicitly recommend pairing `defmt` with `probe-rs` for best results. That is a strong maturity signal, but it still lives across setup docs, generator defaults, logging choices, and support assumptions rather than one portable product boundary.
  https://developer.espressif.com/blog/2025/10/esp-hal-1/
  https://docs.espressif.com/projects/rust/book/application-development/logging.html
- Toolchain activation still matters materially for embedded users. The active `build-std` goal says embedded developers often care more about size and often target systems without a precompiled std, while the Embedonomicon’s SoC-support guide is explicit that real target support depends on documentation, SVD/register descriptions, flash algorithms, and community support posture.
  https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
  https://docs.rust-embedded.org/embedonomicon/soc-support.html

What is still missing is the **stack-level boundary that says one firmware product subject was reviewed with these boards/probes/run lanes, these toolchain and target assumptions, these RAM/FLASH/layout constraints, these runtime evidence channels, these shipped images and update paths, and these bounded support conclusions**.

## Working name
- CLI: `cargo firmware-product`
- primary artifact: `firmware-product-pack/v0`

## Scope
### This epic should own
- firmware-product subject identity
- imported device-lab / toolchain-productization / footprint / observability / support / release attachments
- diffable review points across board/probe/run posture, target/sysroot/linker activation, memory/layout budgets, runtime-evidence channels, and shipped/support claims
- bounded release / support / incident / atlas / assistant handoffs
- verification of pack integrity and import references

### This epic should not own
- a universal embedded framework
- a universal board template or starter generator
- a universal flasher/debugger stack
- a vendor-SDK replacement
- flattening async, RTIC, Hubris, bare-loop, and vendor-runtime families into one runtime model
- a fake one-number “embedded readiness” badge

## Candidate artifact family
### `firmware-product-brief/v0`
Why the product exists, intended consumer set, boards/targets in scope, supported host/lab environments, freshness budget, and review status.

### `firmware-product-subject/v0`
The exact workspace/app/release/deployment subject, imported device/toolchain/footprint/observability/support/release surfaces, comparison base, and support/environment scope.

### `firmware-product-pack/v0`
The portable review bundle linking:
- imported `device-profile` / `device-run-report` / lab-capability attachments
- imported target/linker/sysroot/build-std/toolchain attachments
- imported memory/section/layout/budget attachments
- imported logging/fault/trace/runtime-evidence attachments
- imported release/support/docs and optional incident/update handoffs
- local notes, waivers, caveats, and integrity metadata

### `firmware-product-diff/v0`
What changed between two review points, with separate sections for:
- board / probe / transport / reset posture
- target / linker / sysroot / stable-vs-nightly / custom-stdlib posture
- RAM / FLASH / section / stack / layout posture
- runtime evidence channel and decoder posture
- shipped image / update / recovery posture
- support / docs / host-lane claims

### `firmware-product-handoff/v0`
Bounded consumer summaries for:
- release review
- support / incident review
- lab / bring-up review
- atlas / adoption review
- assistant / editor rendering

## Recommended rollout
1. device profile / run-report lane
2. target / linker / sysroot / build-std lane
3. footprint / layout lane
4. runtime evidence / fault lane
5. release / support / incident handoff lane

This should be driven by [`design/firmware-productization-pilot-program.md`](../design/firmware-productization-pilot-program.md).

## What makes this epic “epic” rather than incremental
A merely incremental tool would improve one lane:
- a nicer board template,
- a nicer `probe-rs` wrapper,
- a nicer linker-script helper,
- a nicer size-report tool,
- or a nicer RTT/defmt console.

An epic contribution here instead gives Rust one **portable firmware product contract** above those lanes.
That is strategically different because it can:
- make release/support/incident/atlas reviews share the same subject and evidence boundary;
- let HALs, runtimes, vendor SDKs, probe tools, and board-specific setup remain specialized without pretending any one defines the whole product;
- keep board/run truth, target activation, footprint/layout truth, runtime evidence, and shipped/support truth distinct but linked;
- and give downstream tooling a bounded artifact to import instead of re-scraping linker scripts, `.cargo/config.toml`, host env vars, debug launch configs, CI logs, board README prose, and issue-thread archaeology.

## Design principles
- **Board/probe/run truth is not build truth.**
- **Build truth is not footprint truth.**
- **Footprint/layout truth is not runtime-evidence truth.**
- **Runtime evidence channels are part of the support surface.**
- **Vendor SDK defaults are not the whole product contract.**
- **Shipped firmware and support claims must import lower-layer evidence instead of restating it.**
- **Consumer summaries are lossy on purpose and say so.**
- **The stack remains thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact firmware product subject,”
- “these are the boards, probes, transports, and reset/run lanes that were actually exercised,”
- “these are the target/linker/sysroot/build-std assumptions that materially affected the build,”
- “these are the RAM/FLASH/section/stack/layout facts that materially affected fit or bootability,”
- “these are the logging/fault/trace channels that actually observed runtime behavior,”
- “these are the shipped images, update/recovery assumptions, and support/docs caveats,”
- “this is what changed from the prior review,”
- and “this is what release/support/incident/atlas consumers may safely conclude,”

without inventing a bespoke readiness schema for every board support package, vendor SDK, RTIC app, Embassy app, or probe script.

## Read this with
- `gaps/embedded-device-labs-and-hardware-in-the-loop.md`
- `gaps/toolchain-variants-sysroots-cross-builds-and-sanitizer-support-contracts.md`
- `gaps/target-support-envelopes-and-runtime-baselines.md`
- `design/firmware-productization-stack.md`
- `design/firmware-productization-pilot-program.md`
- `design/device-lab-kit.md`
- `design/cross-toolchain-kit.md`
- `design/sysroot-pack-kit.md`
- `design/footprint-kit.md`
- `design/observability-kit.md`
- `design/support-envelope-kit.md`
- `design/release-pipeline-kit.md`
