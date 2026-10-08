---
id: P-0406
title: Web Push + VAPID + HTTP ECE Interop & Evidence Kit — subscription locks, endpoint receipts, and browser-safe delivery evidence
status: idea
domains: [web, messaging, security, interoperability, validation, operations]
last_reviewed: 2026-03-06
evidence:
  - https://www.rfc-editor.org/rfc/rfc8030.html
  - https://www.rfc-editor.org/rfc/rfc8291.html
  - https://www.rfc-editor.org/rfc/rfc8292.html
  - https://docs.rs/web-push/
  - https://docs.rs/web-push-native
  - https://crates.io/crates/ece
---

# Problem

Web Push is well specified at the protocol layer: RFC 8030 for push delivery, RFC 8291 for payload encryption, RFC 8292 for VAPID identification. Browser-facing APIs are also well documented, and Rust already has useful building blocks in `web-push`, `web-push-native`, and `ece`.

But the painful failures still happen at the seam between:

- **a browser subscription object and the exact server-side assumptions made about it**,
- **encrypted payload rules and the VAPID keys or audience values actually used in delivery**,
- **browser/runtime push behavior and server-side delivery/debug logs**,
- **endpoint rotation, expiration, and status handling that rarely leave portable evidence behind**,
- and **operations teams that still debug delivery with ad hoc HTTP traces, copied subscription JSON, and guesswork about encryption inputs.**

The missing Rust contribution is not another push sender library. It is an **interop and evidence kit** for subscription locks, endpoint receipts, encryption-policy checks, and browser-safe delivery bundles.

# What it provides

- `push.lock` — pins protocol expectations, VAPID key identifiers, audience/origin assumptions, payload visibility policy, and browser capability overlays.
- `subscription-receipt` — normalized artifact for endpoint, keys, expiration, content-encoding, and client capability assumptions.
- `delivery-receipt` — compact record of request metadata, encryption inputs, response outcome, and retry/disposition findings.
- `policy-findings` — explains mismatched audience, missing user-visible policy, expired endpoints, and encryption/input drift.
- `cargo webpush-evidence` — emits `*.webpushbundle.zip` with locks, receipts, redacted inputs, and notes.

# What the crate should provide other people

1. **A boring receipt for Web Push delivery bugs**.
2. **Pinned subscription/server assumptions** that survive handoff.
3. **Encryption and VAPID diagnostics** without dumping raw sensitive material.
4. **A browser-safe artifact** for support and regression workflows.
5. **A coordination layer above existing Rust Web Push senders.**

# Persona / who it’s for

- Rust backend teams sending web push notifications
- PWA teams validating subscription and delivery flows
- Release/support engineers debugging delivery failures
- Security reviewers checking VAPID and payload-handling policy

# Users & user stories

- **Backend engineer**: “Tell me whether this failure is endpoint expiry, VAPID audience mismatch, or encryption input drift.”
- **PWA engineer**: “Pin exactly what the browser subscribed with and what the server assumed.”
- **Support engineer**: “Share a redacted bundle that explains the failure without exposing raw secrets.”
- **Security reviewer**: “See that visible-notification and key-handling policy were applied consistently.”

# Prior art (and why it’s insufficient)

- The RFC stack and browser docs define the formal and operational surfaces.
- Rust already has push sender crates and ECE encryption substrate.
- Existing workflows tend to stop at “send request, inspect status code, retry maybe.”

What Rust still lacks is an **evidence-grade coordination artifact** for pinned subscription assumptions, encrypted-delivery receipts, and explainable policy findings.

# Design goals

1. **Subscription-explicit** — the browser-provided inputs must be pinned and reviewable.
2. **Redaction-first** — retain reasoning value without leaking sensitive material.
3. **Protocol-honest** — delivery, encryption, and VAPID layers remain distinguishable.
4. **Browser-overlay aware** — operational differences belong in overlays, not hand-waving.
5. **Ops-friendly** — artifacts should help real debugging, not just conformance demos.

# MVP surface

- Minimal types: `PushLock`, `SubscriptionReceipt`, `DeliveryReceipt`, `PushFinding`, `WebPushBundle`
- Minimal functions:
  - `capture_subscription()`
  - `prepare_delivery()`
  - `evaluate_delivery()`
  - `write_bundle()`
- Feature flags:
  - `vapid`
  - `ece`
  - `web-push`
  - `browser-overlays`

# Compatibility story

- Works above existing Rust sender crates rather than replacing them.
- Supports offline analysis of captured subscription/delivery metadata.
- Keeps browser-specific behavior in overlays and findings.
- Can later integrate with test harnesses or replay tools without changing the core lockfile.

# Conformance & fixtures

- Goldens for VAPID audience mismatch, content-encoding drift, expired endpoints, and missing user-visible policy assumptions.
- Tiny corpora for successful and failed delivery receipts across different push-service behaviors.
- Fixtures showing the same logical notification under different browser/subscription assumptions.
- Public mini-corpus of redacted subscription JSON and delivery outcomes.

# Path to boring stability

- Stabilize the lockfile and receipt schemas before broader runtime integrations.
- Start with server-side artifact capture and evaluation.
- Keep browser overlays explicit and versioned.
- Resist drift into becoming a notification platform or FCM/APNs abstraction layer.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A Rust library and CLI that pin subscription/server assumptions, capture redacted Web Push delivery receipts, evaluate policy and protocol findings, and emit compact `*.webpushbundle.zip` artifacts.

# De-risk plan

1. Start with subscription receipts and offline delivery evaluation.
2. Add direct adapters for `web-push` / `web-push-native` next.
3. Keep browser-specific overlays small and explicit.
4. Pilot in PWA support and regression workflows before broader operations claims.

# Non-goals

- Not a notification service.
- Not a browser automation framework.
- Not a replacement for push-service providers.
- Not a general mobile push abstraction spanning unrelated ecosystems.

# Architecture & API sketch

```rust
pub struct PushLock {
    pub vapid_key_id: Option<String>,
    pub expected_audiences: Vec<String>,
    pub require_user_visible: bool,
    pub browser_overlays: Vec<String>,
}

pub fn capture_subscription(json: &serde_json::Value) -> Result<SubscriptionReceipt>;
pub fn prepare_delivery(lock: &PushLock, receipt: &SubscriptionReceipt) -> Result<DeliveryInput>;
pub fn evaluate_delivery(lock: &PushLock, outcome: &DeliveryReceipt) -> Vec<PushFinding>;
```

Bundle draft: `push.lock`, `subscription-receipt.json`, `delivery-receipt.json`, `findings.json`, `notes.md`.

# Security / safety model

- Redact or hash endpoint and key material by default.
- Preserve enough metadata for reproducible findings.
- Separate browser-supplied inputs from server-generated assumptions.
- Treat receipts as potentially privacy-sensitive and keep them compact.

# Maintenance & governance plan

- Keep the core about locks, receipts, and findings.
- Version browser overlays and push-service quirks explicitly.
- Publish a tiny redacted corpus of subscription/delivery cases.
- Resist drift into a full push platform.

# Milestones

## 0.1
- `push.lock`
- subscription receipts
- offline policy evaluation

## 0.2
- sender adapters
- delivery receipts
- public redacted corpus

## 1.0
- stable `*.webpushbundle.zip`
- documented compatibility policy for browser and push-service overlays
- CI-friendly regression artifacts

# Open questions

- What is the best stable redaction policy for endpoint and key material?
- Which push-service differences deserve first-class overlays versus simple findings?
- How much client/browser capability data is needed before receipts become materially more useful?

# Sources

- RFC 8030 Web Push: https://www.rfc-editor.org/rfc/rfc8030.html
- RFC 8291 Web Push encryption: https://www.rfc-editor.org/rfc/rfc8291.html
- RFC 8292 VAPID: https://www.rfc-editor.org/rfc/rfc8292.html
- `web-push`: https://docs.rs/web-push/
- `web-push-native`: https://docs.rs/web-push-native
- `ece`: https://crates.io/crates/ece
