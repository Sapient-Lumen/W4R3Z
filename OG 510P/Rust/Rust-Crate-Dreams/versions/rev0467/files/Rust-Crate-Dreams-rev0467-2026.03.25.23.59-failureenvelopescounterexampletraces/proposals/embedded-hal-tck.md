---
id: P-0020
title: embedded-hal TCK — conformance + semantics test kit for HALs and drivers
status: idea
domains: [embedded, testing, reliability]
last_reviewed: 2026-03-01
evidence:
  - https://blog.rust-embedded.org/embedded-hal-v1/
  - https://github.com/dbrgn/embedded-hal-mock
  - https://crates.io/crates/defmt-test
  - https://github.com/rust-embedded/awesome-embedded-rust
  - https://users.rust-lang.org/t/how-to-implement-unit-tests-for-a-project-with-embedded-rust/99768
needs:
  - HAL authors need confidence that implementations match embedded-hal’s semantics, not just its type signatures.
  - Driver authors want reusable “behavioral” test suites and golden mocks that catch subtle protocol bugs early.
  - Teams want a standard way to run host tests + hardware-in-the-loop tests in CI.
risks:
  - Semantics vary by hardware; tests must be explicit about what is required vs recommended.
  - Must avoid becoming a maintenance burden across many MCUs; needs a modular, trait-focused structure.
---

# Problem

`embedded-hal` 1.0 is stable and explicitly focuses on drivers and interoperability. That stability creates an opportunity: define a **Technology Compatibility Kit (TCK)** that checks not only compilation against traits, but behavioral expectations and common gotchas.

Today:
- `embedded-hal-mock` helps test drivers without hardware.
- `defmt-test` and other harnesses help test on-target.
But there’s no widely adopted, canonical set of *conformance/semantics* tests that HAL authors can run to say “this HAL behaves correctly for common driver assumptions”.

# Users & user stories

- **HAL maintainers**: “Run a standard suite and publish a badge: conforms to embedded-hal 1.0 (SPI/I2C/GPIO/etc.).”
- **Driver authors**: “Use shared test vectors and mocks; catch protocol bugs before HIL.”
- **Product teams**: “Combine host tests + HIL tests with one consistent story.”

# Prior art (and why it’s insufficient)

- `embedded-hal-mock` provides mocks and expectations, but doesn’t define *semantic conformance* criteria or a cross-trait suite.
- `defmt-test` is a harness, not a semantics spec or compatibility kit.
- Tutorials and templates exist, but they’re not a standardized suite.

# Design goals

- Provide a trait-by-trait suite with explicit semantics:
  - Required behaviors (must pass)
  - Recommended behaviors (warn)
  - Hardware-dependent behaviors (documented + opt-in)
- Work for both blocking and async traits (`embedded-hal-async`).
- Allow two execution modes:
  - **Host simulation** (mock/virtual peripheral)
  - **HIL** (on-target with probe tooling)
- Make results publishable (machine-readable report + human summary).

# Non-goals

- Replacing project-specific HIL infrastructure.
- Providing complete MCU simulation/emulation for every chip.

# Architecture & API sketch

**Crates**
- `embedded_hal_tck_core`: trait semantics specs + report model.
- `embedded_hal_tck_host`: host runners (mocks, property tests, fuzz harnesses).
- `embedded_hal_tck_hil`: glue for running suites on hardware (integrate with defmt-test / embedded-test).
- Optional integration crates:
  - `embedded_hal_tck_probe_rs` (if used)
  - `embedded_hal_tck_embassy` (async executor patterns)

**Key APIs**
- `Suite::spi()`, `Suite::i2c()`, `Suite::gpio()`, ...
- `Runner::run(suite, impl_under_test) -> Report`
- `Report` emits JSON + JUnit + Markdown summaries.

**Semantic test examples**
- SPI: CS asserted for entire transaction; no interleaving across devices (where required); error kind mapping.
- I2C: start/stop semantics; repeated start handling; NACK error classification.
- GPIO wait semantics for async wait trait (edge/level behavior).

# Security / safety model

- Designed to be `no_std` friendly where possible for embedded contexts.
- HIL runners must guard against “bricking” behaviors (e.g., avoid destructive tests by default).

# Maintenance & governance plan

- Semantics specs live as doc tests + executable tests.
- Add conformance fixtures for popular HALs (as opt-in integration tests).
- Require new suite items to include: rationale, failure example, and a driver that benefits.

# Milestones

## 0.1
- Core report format + 2 suites (SPI + I2C) host-runner with deterministic mocks.
- Documentation: “How HAL authors use this in CI.”

## 0.2
- Add async trait coverage (selected high value traits).
- Add HIL adapter for defmt-test (minimal).

## 0.3
- Add property-based “fuzz the bus” runner for SPI/I2C transaction sequences.
- Publish badges and summary generator.

## 1.0
- Stable suite semantics + versioning policy; broad trait coverage.

# Open questions

- Where should semantics be sourced/defined: embedded-hal docs, an adjunct “semantics book”, or both?
- How to handle HALs that legitimately cannot satisfy some semantics due to hardware limits?

# Sources

- https://blog.rust-embedded.org/embedded-hal-v1/
- https://github.com/dbrgn/embedded-hal-mock
- https://crates.io/crates/defmt-test
- https://github.com/rust-embedded/awesome-embedded-rust
- https://users.rust-lang.org/t/how-to-implement-unit-tests-for-a-project-with-embedded-rust/99768
