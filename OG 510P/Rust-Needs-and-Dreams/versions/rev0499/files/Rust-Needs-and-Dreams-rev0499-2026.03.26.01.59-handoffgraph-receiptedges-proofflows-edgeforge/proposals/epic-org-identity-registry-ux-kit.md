# Epic Proposal: Org Identity & Registry UX Kit

## One-sentence pitch
Give Rust a portable **publisher/source identity substrate** so registry/source configuration, publish authority, project-family claims, and downstream trust/policy/install consumers stop inferring different stories from the same incomplete hints.

## Deliverables
- reference implementations for:
  - `cargo source`
  - `cargo publisher` (with `cargo org` as an optional compatibility alias)
- schemas:
  - `source-report/v0`
  - `publisher-report/v0`
  - `claim-report/v0`
  - `publisher-source-pack/v0`
- integration examples for:
  - Trust Signals imports
  - Package Admission handoff
  - Distribution/install receipt imports
- migration notes for namespace-aware and non-namespace org/family models

## Why now
- crates.io now supports stronger issuer-backed publish control: GitLab CI/CD Trusted Publishing support, Trusted-Publishing-only mode, and improved publish-side security posture;
- Cargo’s authenticated alternative-registry flow now explicitly depends on credential providers, which raises the value of source/auth visibility;
- Cargo still treats alternate registries and source replacement as distinct features, so tools need to preserve that semantic difference;
- RFC 3243 and the open-namespaces goal show namespace control is active work, not dead theory;
- the Feb 2026 ownership/namespace survey threads show the ecosystem wants a way to reduce circular debate and compare designs more cleanly.

Sources:
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://doc.rust-lang.org/cargo/reference/registry-authentication.html
- https://doc.rust-lang.org/cargo/reference/registries.html
- https://doc.rust-lang.org/cargo/reference/source-replacement.html
- https://rust-lang.github.io/rfcs/3243-packages-as-optional-namespaces.html
- https://rust-lang.github.io/rust-project-goals/2025h2/open-namespaces.html
- https://internals.rust-lang.org/t/survey-of-organizational-ownership-and-registry-namespace-designs-for-cargo-and-crates-io/24027

## What makes this worthy instead of merely nice
This is not just a convenience wrapper over `.cargo/config.toml`.
A real identity substrate here would improve several other frontier seams at once:
- **Trust** gets cleaner publisher/source facts;
- **Policy** gets importable authority/source constraints instead of bespoke CI glue;
- **Package Admission** can explain publish authority at review time;
- **Distribution** can state where an install actually came from;
- **Typosquat / impersonation defense** gets higher-quality project-family and namespace context.

## Non-goals
- forcing one namespace/ownership scheme on all of Rust;
- replacing crates.io moderation or governance policy;
- becoming a stealth trust-score engine;
- exposing registry credentials or private tokens;
- pretending exact-copy source replacement is equivalent to alternate-registry identity.

## Ranked milestones
1. **v0: source truth first**
   - `cargo source add/list/verify/doctor`
   - `source-report/v0`
2. **v0.2: publisher authority posture**
   - `cargo publisher report`
   - `publisher-report/v0`
3. **v0.3: claim / namespace posture**
   - `claim-report/v0`
   - namespace-aware and non-namespace examples
4. **v0.4: stack handoff**
   - package-admission / trust imports
   - `publisher-source-pack/v0`
5. **v1: consumer receipts and upstream proposal**
   - distribution/install imports
   - upstream integration proposal once the reports and pilot lanes prove stable value
