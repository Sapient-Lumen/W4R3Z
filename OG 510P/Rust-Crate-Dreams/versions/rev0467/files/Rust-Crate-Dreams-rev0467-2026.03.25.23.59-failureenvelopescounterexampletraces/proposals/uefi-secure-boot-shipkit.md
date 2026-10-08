---
id: P-0129
title: UEFI Secure Boot ShipKit — build/sign/test/upgrade Rust UEFI apps with confidence
status: idea
domains: [firmware, security, devtools, embedded]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/uefi/latest/uefi/
  - https://crates.io/crates/uefi
  - https://doc.rust-lang.org/beta/rustc/platform-support/unknown-uefi.html
  - https://blog.malware.re/2023/08/20/rust-os-part1/index.html
---

# Problem

Rust has solid UEFI foundations, but end-to-end *Secure Boot* workflows remain fragmented: signing EFI binaries, managing keys, building bootable images, running in QEMU/OVMF, and safely rolling updates (including rollback strategies) are repetitive and error-prone.

# What it provides

A “golden path” crate + cargo tooling for UEFI apps:

- `uefi_shipkit` library:
  - helpers for metadata embedding (build IDs), structured logging, and test harness hooks
  - a small “boot protocol” for reporting status back to a host harness
- `cargo uefi` subcommands:
  - `cargo uefi build` (target config helpers, OVMF-friendly outputs)
  - `cargo uefi sign` (pluggable signers; local keys for dev; interface for HSM/KMS)
  - `cargo uefi image` (assemble FAT image / ESP layout; include config + artifacts)
  - `cargo uefi test` (QEMU/OVMF runner; captures console + exit/status protocol)
  - `cargo uefi capsule` (optional: build UEFI capsule update artifacts + test rollout flows)
- Standard artifact: `*.uefibundle.zip`:
  - EFI binary + signature metadata, test logs, QEMU/OVMF version info, and reproducible image manifest.

# Users & user stories

- **OSDev hobbyist**: “I want a repeatable QEMU harness and signing flow without bespoke scripts.”
- **OEM / embedded**: “I need a controlled signing pipeline and test evidence bundles for releases.”
- **Security**: “I want auditable signing inputs/outputs and replayable test logs.”

# Prior art (and why it’s insufficient)

- `uefi` crate provides safe abstractions for UEFI functionality but does not define a cohesive secure-boot/signing/test/update toolchain.
- The `*-unknown-uefi` platform notes document the landscape but not a developer “shipkit”.
- Community tutorials exist, but each reinvents build/sign/test steps.

# Design goals

- **Reproducible firmware artifacts**: deterministic bundle manifests.
- **Friendly local dev**: easy self-signed dev mode, while keeping production signing pluggable.
- **Test evidence**: QEMU/OVMF harness outputs that can be attached to issues/PRs.
- **Small + composable**: do not swallow the entire OSDev ecosystem.

# Non-goals

- Implementing a full bootloader framework.
- Mandating a single signing solution; ShipKit provides interfaces and defaults.

# Architecture & API sketch

- `Signer` trait: `sign_efi(path) -> SignatureMeta`.
- `EspBuilder`: creates an ESP layout from a declarative manifest.
- `Harness`: runs QEMU/OVMF, captures serial, parses “boot protocol” status, emits bundle.

# Security / safety model

- Strict separation: dev keys vs production keys; never “helpfully” use prod key material.
- Bundle redaction: allow stripping serial logs if needed; default keeps logs since they’re often vital.

# Maintenance & governance plan

- Keep the stable core as: artifact schema + harness protocol + cargo subcommands.
- Provide adapters rather than forcing dependencies (QEMU runner, signing backend, capsule builder).

# Milestones

- **MVP**: `cargo uefi test` with QEMU/OVMF + `uefibundle` schema + `cargo uefi image`.
- **v0.2**: pluggable `sign` + CI templates.
- **v1.0**: capsule update tooling (optional), conformance vectors (known-good OVMF matrix).

# Open questions

- How to best package OVMF dependencies (download vs system) while staying reproducible?
- Opinionated defaults for ESP layout and config management.

# Sources

- `uefi` crate docs and registry page.
- Rust platform support notes for UEFI targets.
- Community OSDev walkthrough showing typical steps and pitfalls.
