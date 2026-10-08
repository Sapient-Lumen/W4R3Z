# Design: Incident Kit (`cargo incident`, incident-pack/v0)

## Position in the archive
This kit now sits below [`design/ecosystem-incident-response-stack.md`](./ecosystem-incident-response-stack.md). The kit owns the concrete CLI/artifact surface; the stack owns the higher-level response boundary between advisories, local containment, rebuild/reissue, and downstream communication.

## Goal
Turn security incidents (especially malicious crates) into a **standard operational workflow** with:
- a reference CLI (`cargo incident`),
- portable artifacts (`incident-report/v0`, `incident-pack/v0`),
- drill scenarios and automation hooks.

This kit bridges registry advisories → org action.

## References (signals)
- crates.io notification policy update (Feb 2026): https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- 2026 supply chain flagship context: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo SBOM precursor tracking: https://github.com/rust-lang/cargo/issues/16565

## Core UX: `cargo incident`
- `cargo incident ingest <advisory-id|url|snapshot>`  
  Pull incident metadata (e.g., RustSec advisory / crates.io removal notice).
- `cargo incident exposure`  
  Determine whether the incident affects the current workspace:
  - lockfile membership
  - scope (build deps / proc-macros / runtime)
  - build matrix (targets/profiles)
  - (optional) CI logs + build provenance integration
- `cargo incident quarantine`  
  Apply mitigations:
  - pin/yank-avoid strategies
  - disable specific features
  - blocklist in `cargo policy` or `cargo deny`
- `cargo incident rebuild`  
  Produce a “safe rebuild plan”:
  - clean builds
  - key rotation checklist (ties into Credentials Kit)
  - cache invalidation guidance (ties into Build Cache Kit)
  - hermetic/sandbox modes (ties into Hermetic + Safe kits)
- `cargo incident pack`  
  Emit an `incident-pack/v0` bundle for audits and postmortems.

## Artifacts
### `incident-report/v0`
- incident metadata:
  - advisory identifiers
  - affected crate(s) + versions + reason (malware, compromise, etc.)
- workspace snapshot:
  - lockfile hash
  - SBOM precursor pointers (if available)
- exposure assessment:
  - affected nodes and scopes
  - “reachable” analysis (direct vs transitive)
  - confidence signals (e.g., missing provenance)
- mitigations applied:
  - pins, bans, patches, replacements
  - credentials rotated? (references `cred-report/v0`)
- rebuild plan and completion status

### `incident-pack/v0`
A bundle containing:
- `incident-report/v0`
- referenced policy reports and trust packs (content addressed)
- optional redacted logs

## Drill scenarios
Provide a small “scenario library”:
- typosquat introduced via transitive dep
- malicious build-dep that exfiltrates env vars
- compromised maintainer key leading to signed but malicious release
Each scenario:
- has expected detection signals (policy fail, trust fail, name-risk warn)
- has expected remediation steps and report fields.

## Evaluation plan
- Pilot with a few real-world incident retrospectives (where public data exists)
- Measure time-to-action: “from advisory to pinned rebuild plan”
- Usability bar: generate a concise checklist for humans + machine-readable evidence for CI.
