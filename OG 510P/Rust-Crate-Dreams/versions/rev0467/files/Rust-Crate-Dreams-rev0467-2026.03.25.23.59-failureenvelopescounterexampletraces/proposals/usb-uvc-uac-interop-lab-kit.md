---
id: P-0210
title: USB UVC/UAC Host + Interop Lab Kit — cross-platform enumeration, control, capture, and reproducible device bundles
status: idea
domains: [usb, device, multimedia, drivers, interop, testing]
last_reviewed: 2026-03-05
evidence:
  - https://www.usb.org/document-library/video-class-v15-document-set
  - https://www.usb.org/documents
  - https://en.wikipedia.org/wiki/USB_video_device_class
needs:
  - A Rust-native, cross-platform *host-side* toolkit for UVC (cameras) and UAC (audio) that makes devices testable and debuggable.
  - Deterministic, shareable “device evidence bundles” that capture descriptors, control transactions, and (optionally) media samples with redaction.
  - A compatibility matrix + conformance harness that helps vendors and app teams identify what actually works.
risks:
  - USB class specs are large; keep scope to the “missing middle”: descriptor parsing, control plane, capture plumbing, evidence bundles.
  - Platform-specific backends (Windows/macOS/Linux) can dominate; design an adapter layer and ship one backend first.
  - Privacy risk: device serials, frames, audio; must ship redaction tools and opt-in capture.
---

## Problem

Rust has USB primitives and multimedia stacks, but a *cohesive, test-harness-shaped* UVC/UAC host toolkit is hard to find: teams end up writing bespoke descriptor parsers, control transaction loggers, and capture glue.

UVC v1.5 is a widely referenced baseline for modern devices, with a published document set from USB-IF.
Source: https://www.usb.org/document-library/video-class-v15-document-set

## What this crate should provide

A workspace (one repo) that yields:

### 1) `uvc_uac` library: class-aware host API
- Parse and validate:
  - Device/config/interface/endpoint descriptors
  - UVC class-specific descriptors (terminals, processing units, extension units)
  - UAC descriptors (feature units, terminals)
- High-level control plane:
  - Enumerate controls with typed schemas
  - Read/write controls with safe defaults (bounds checking, rollback helpers)
  - Transaction logging with stable normalization

### 2) Backends (adapter architecture)
- `backend-libusb` (Linux/macOS first), optional `backend-winusb` / `backend-iokit` later.
- Clear boundary:
  - transport (control/bulk/isochronous)
  - clocking/timestamps
  - OS-specific permission/setup doctor

### 3) Capture + replay utilities
- Optional pipelines (feature-gated):
  - MJPEG / uncompressed frame sampling
  - isochronous capture transcript
  - audio sample capture (short windows)
- “Replay” is primarily for control-plane transaction sequences; media replay is optional and can be synthetic.

### 4) Evidence bundles: `*.uvcbundle.zip`
A portable artifact to attach to issues/CI failures:
- `device.json` (descriptor inventory + hashes)
- `controls.json` (enumerated controls + ranges)
- `transactions.ndjson` (normalized control transfers)
- `env.json` (OS/driver/kernel, bus speed, timestamps)
- Optional `samples/` with redacted frame/audio snippets

### 5) Conformance + compatibility matrix
- Scenario harness:
  - “set exposure / verify state / capture 5 frames”
  - “toggle mic gain / verify readback”
- Output a matrix: device models × OS × backend × scenario.

## Prior art (and why it’s insufficient)

- The USB-IF UVC 1.5 document set defines the target behaviors but does not provide a turnkey host toolkit.
  Source: https://www.usb.org/document-library/video-class-v15-document-set
- UVC is a broad class (webcams, capture devices), but host-side debugging remains fragmented across OS tooling.
  Source: https://en.wikipedia.org/wiki/USB_video_device_class

## MVP plan (4–8 weeks)

1. Implement `device inventory`:
   - parse descriptors, output stable JSON
2. Implement `control transfer logger`:
   - normalize requests/responses, write `transactions.ndjson`
3. Implement `*.uvcbundle.zip` bundler:
   - redaction presets (serial numbers, frames off by default)
4. Implement a small scenario set:
   - list controls, set/get a few safe controls, report.

## v1 plan (8–14 weeks)

- One solid backend (libusb) + “doctor” for permissions.
- Typed control schemas for common units.
- Basic frame sampling for MJPEG/uncompressed with redaction.
- Compatibility matrix runner + GitHub Actions template.

## Design constraints (keep it epic but survivable)

- **Don’t become a full multimedia framework.** Focus on class control plane + evidence.
- **Bundle-first.** Every failure should be reproducible from a `uvcbundle`.
- **Adapter-first.** Make OS backends pluggable; ship one excellent path.
