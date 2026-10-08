# Gap: Ecosystem Incident Response (Malicious Crates, Coordinated Disclosure, Rebuild Guidance)

## Summary
The Rust ecosystem's security posture is improving, but **incident response remains ad-hoc** for most orgs and maintainers:
- When a malicious crate is found, users need a fast *operational* playbook: identify exposure, quarantine builds, rotate credentials, and rebuild safely.
- Advisories exist, but actionable remediation steps vary wildly and are hard to automate.
- Registry-side decisions (blog posts, advisories, removals) influence what downstream users learn and how quickly.

This gap is about packaging incident response into **repeatable workflows + portable reports**, so orgs can run drills and react quickly when supply-chain events occur.

## Ecosystem signals
- crates.io updated its malicious crate notification policy (Feb 13, 2026), reducing per-incident blog posts in favor of RustSec advisories except for cases with real-world usage/exploitation.  
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- The Rust Project’s 2026 flagships explicitly include “Secure your supply chain” (dependency control + SBOM), indicating a push toward evidence and operational controls.  
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo has an unstable `sbom` build configuration for emitting SBOM precursor files, a key input for exposure analysis.  
  https://github.com/rust-lang/cargo/issues/16565

## What “good” looks like
- A standard “incident packet” that captures:
  - dependency graph snapshot
  - exposure analysis (what builds/hosts/users were affected)
  - remediation actions taken (key rotation, rebuild, pinning)
- Drillable playbooks and checklists (like fire drills):
  - tabletop scenarios
  - automated CI exercises (safe mode)
- Tight integration with policy/evidence tools:
  - `cargo policy`, `cargo trust`, `cargo attest`, `cargo cache`, `cargo safe`
