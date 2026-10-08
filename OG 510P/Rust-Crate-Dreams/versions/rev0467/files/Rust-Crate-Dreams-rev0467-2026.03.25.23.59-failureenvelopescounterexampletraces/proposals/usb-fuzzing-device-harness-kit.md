---
id: P-0177
title: USB Fuzzing & Device Emulation Harness Kit — reproducible external USB fuzzing workflows and portable crash bundles
status: idea
domains: [security, fuzzing, embedded, kernel, virtualization, testing]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/google/syzkaller/blob/master/docs/linux/external_fuzzing_usb.md
  - https://lifeasageek.github.io/papers/kyungtae-fuzzusb.pdf
---

## What it should provide others

A Rust kit that makes **USB protocol fuzzing** and “virtual device” testing accessible, reproducible, and shareable:

- A portable `*.usbfuzzbundle.zip` format:
  - device descriptor set + control transfer scripts,
  - fuzzer seed + minimized reproducer,
  - crash logs + coverage hints (when available),
  - environment fingerprint (kernel, modules, gadget backend).
- A harness API:
  - define a virtual USB device (descriptors + endpoints + state machine),
  - plug into backends like Linux Raw Gadget / dummy HCD,
  - integrate with `cargo fuzz` / libFuzzer / AFL-style loops.
- A conformance scenario library:
  - common stacks (HID, mass storage, CDC ACM, vendor control endpoints),
  - “nasty but legal” edge-case descriptors and timing.
- A “doctor” CLI:
  - validates kernel/module prerequisites, permissions, and backend health,
  - emits a stable report for CI and bug reports.

## Why this is still missing

USB fuzzing exists, but it is **hard to reproduce** and often bound to bespoke scripts and kernel-specific setup.
Syzkaller demonstrates powerful external USB fuzzing approaches, and research systems explore stateful fuzzing,
but there is no Rust-native “batteries included” workflow that produces portable artifacts and encourages sharing.

## MVP scope

- Linux-only harness for Raw Gadget / dummy HCD workflows.
- `usbfuzzbundle` pack/unpack + reproducible runner.
- Minimal scenario library for descriptor fuzzing and control transfers.

## v1 scope

- Stateful device model helpers (explicit state machines, timing constraints).
- Corpus minimization + delta-debugging helpers that output stable reproducers.
- Optional “host stack” testing mode (run a user-space host stack against a virtual device).

## Design notes

- Separate concerns: device model ↔ backend ↔ fuzz loop ↔ artifact recording.
- Make “share the bundle” the default bug report path (especially for kernel/driver issues).
