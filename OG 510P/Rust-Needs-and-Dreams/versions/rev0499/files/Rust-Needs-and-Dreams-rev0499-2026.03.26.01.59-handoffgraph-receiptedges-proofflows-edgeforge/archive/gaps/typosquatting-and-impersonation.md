# Gap: Typosquatting / Impersonation Defense (Supply-Chain Hygiene)

## Summary
Typosquatting and near-name impersonation remain a high-leverage supply-chain attack vector:
- Users install the wrong crate due to a small name difference.
- Attackers can publish lookalike crates and wait for accidental adoption.
- Tooling offers little **pre-flight warning** and registries struggle with the signal/noise tradeoff.

This gap is about **prevention + detection + explainable warnings**, not only after-the-fact advisories.

## Ecosystem signals
- crates.io changed its malicious crate notification policy (Feb 13, 2026), explicitly aiming to reduce noise from frequent individual incident posts.  
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Research has proposed automated detection of malicious typosquatting candidates for popular crates on crates.io (ACM poster, Aug 2025).  
  https://dl.acm.org/doi/10.1145/3708821.3735340
- Community discussion continues to ask for edit-distance-style prevention mechanisms on crates.io (e.g., blocking too-close names).  
  https://www.reddit.com/r/rust/comments/1r3wa64/cratesio_an_update_to_the_malicious_crate/

## What “good” looks like
- A consistent *warning surface* in tools (Cargo) and registries (crates.io) that is:
  - explainable (why this looks suspicious),
  - configurable (org policies),
  - low-noise (focus on popular/targeted namespaces).
- A shared schema for “name similarity risk” and “impersonation evidence” that can feed:
  - Trust Signals Kit,
  - Resolve Doctor,
  - Security triage workflows.
