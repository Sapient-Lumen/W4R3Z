# Epic Proposal: Typosquat Guard Kit

## One-sentence pitch
Prevent accidental installs of lookalike crates by giving Cargo and CI an explainable, policy-driven “name-risk” gate with portable reports.

## Deliverables
- `cargo-guard` subcommand (focus: `name-risk`, `diff`, `policy`)
- Schemas:
  - `name-risk-report/v0`
  - `name-risk-policy/v0`
- Corpora:
  - synthetic typosquat generator + regression tests
  - curated incident list (publicly documented ones)
- Optional crates.io integration proposal:
  - soft warnings for new crates close to high-value targets
  - reviewer queue for flagged names (human-in-the-loop)

## Why now
- crates.io is adjusting how it communicates malicious crate incidents to reduce noise, making proactive defenses more valuable.  
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Research suggests automated detection of typosquatting candidates is feasible at scale.  
  https://dl.acm.org/doi/10.1145/3708821.3735340
- Community concern continues around near-name crates and accidental adoption.  
  https://www.reddit.com/r/rust/comments/1r3wa64/cratesio_an_update_to_the_malicious_crate/

## Non-goals
- Blanket bans on similar names without appeal
- A single global “trust score”
- Replacing RustSec advisories (this is *prevention* and *early warning*)

## Milestones
1) v0: local lockfile scanning + report + basic policy
2) v0.2: PR diff mode + scope weighting (build-deps/proc-macros)
3) v0.3: corpora + tuning + docs
4) v1: stable schemas + integration proposal for crates.io warnings
