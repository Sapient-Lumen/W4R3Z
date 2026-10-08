---
id: P-0274
title: Wi‑Fi Easy Connect (DPP) Interop & Evidence Kit — canonical onboarding transcripts + dppbundle.zip
status: idea
domains: [networking, iot, wifi, security, interoperability, testing]
last_reviewed: 2026-03-05
evidence:
  - https://source.android.com/docs/core/connect/wifi-easy-connect
  - https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/network/esp_dpp.html
  - https://link.springer.com/article/10.1007/s10207-025-00988-3
---

## What it should provide others

A portable way to **reproduce and compare Wi‑Fi Easy Connect / Device Provisioning Protocol (DPP)** onboarding behavior across device firmware, mobile OSes, and host stacks — without shipping raw packet captures.

The crate should give users:

- **Capture → canonicalize → diff** DPP onboarding sessions into a stable, privacy-aware IR.
- **Scenario runner** to execute common flows (QR bootstrap, NFC bootstrap, configurator ↔ enrollee roles).
- **Shareable evidence bundles** (`*.dppbundle.zip`) with redaction presets for keys/identities.
- **Interop matrices** across:
  - Android versions / OEM variations,
  - embedded SDKs (e.g., ESP-IDF),
  - Wi‑Fi AP models and security modes,
  - configurator/enrollee implementations.

## Why it is missing / worth building

DPP is increasingly used for IoT onboarding; Android documents it as the successor to WPS, and embedded SDKs expose DPP APIs — but debugging failures remains ad-hoc (logs, vendor tools, full pcaps). A Rust “missing middle” is a **canonical transcript + evidence bundle** format that teams can attach to CI failures and field tickets.

There is also active security analysis work on Wi‑Fi Easy Connect, which increases the value of a repeatable harness for regression and variant testing.

## Non-goals

- Not a full Wi‑Fi stack or supplicant.
- Not a replacement for vendor certification tooling.
- Not a packet sniffer; if pcap is used, it should be an optional input adapter.

## Proposed design

### Workspace layout

- `dpp-evidence-core`
  - canonical IR, redaction, bundle I/O (`dppbundle.zip`)
- `dpp-capture`
  - adapters:
    - Android logcat + dumpsys parsers (best-effort)
    - embedded SDK event stream adapters (ESP-IDF-style callbacks)
    - optional pcap → transcript adapter
- `dpp-replay`
  - deterministic “transcript replay” for regression (simulates peer responses, validates state machine)
- `dpp-matrix`
  - scenario DSL + matrix runner

### Canonical IR sketch (high level)

- `Bootstrap { method: QR|NFC|Manual, pubkey_fingerprint, info_hash }`
- `AuthInit/AuthResp { curve, wrapped_data_ref }`
- `ConfigRequest/ConfigResponse { ssid_ref, akm, chan_list, expiry }`
- `Failure { code, phase, peer_hint? }`

### Evidence bundle (`*.dppbundle.zip`)

- `manifest.json` (tool versions, OS/firmware fingerprint, redaction policy id)
- `transcript.jsonl` (canonical IR events)
- `artifacts/` (optional: sanitized logs, minimal pcaps, QR payload samples)
- `verdict.json` (expected vs observed, diffs, “likely causes” heuristics)

## Minimum lovable MVP (4–8 weeks)

1. Canonical IR + bundle spec + redaction presets.
2. ESP-IDF adapter + sample fixtures for two flows.
3. Diff + report generator (“where did the state machine diverge?”).

## De-risk plan

- Build IR from **two real implementations** (Android + one embedded SDK) before expanding features.
- Validate that the IR can represent “weird” failures (timeouts, retries, partial config).
- Keep cryptographic material in `*_ref` placeholders from day one.

## Scorecard (0–5)

- Impact: 4
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 4
