# Design: Airgap Pilot Program (`cargo airgap pilot`, `airgap-pilot-pack/v0`)

## Goal
Make the **Airgap Kit** executable through a ranked pilot program that starts with the highest-value restricted-network lanes instead of pretending “offline Rust” is one thing.

The archive already had the right thesis:
- restricted-network Rust has at least three distinct planes,
- mirror topology matters,
- warm-cache success is not the same as validated offline correctness,
- and Cargo, `cargo install`, and rustup do not share one configuration or lock story.

What was still missing is the execution layer:
- which lanes should go first,
- which artifacts must be reviewed per lane,
- which existing Cargo/rustup primitives should be imported rather than reimplemented,
- and how secure mirroring / verification should widen only after the basic planes are modeled honestly.

A worthy contribution here is **not** another mirror daemon, another `cargo --offline` wrapper, or a giant enterprise bootstrap script.
It is a disciplined rollout that proves Rust teams can publish **portable restricted-network truth** for a few concrete lanes before widening to full mirror and policy ecosystems.

## References (signals)
- The Rust project’s accepted crates.io mirroring goal explicitly targets cryptographic verification of releases and crates, secure local mirrors, and mirror use in restrictive firewalls, unreliable internet, and CI infrastructure.
  https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
- Cargo’s source-replacement docs say replacement sources are for mirrors or exact local copies and rely on the core assumption that the source code is **exactly the same** in both sources; replacement sources may not add extra crates.
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
- Cargo’s offline FAQ says `--offline` / `--frozen` should error rather than touch the network, and recommends `cargo fetch` plus vendoring/source replacement to prepare for offline use.
  https://doc.rust-lang.org/cargo/faq.html
- `cargo install` is materially different from ordinary workspace builds: by default it ignores the packaged `Cargo.lock` unless `--locked` is passed, and its configuration discovery starts at `$CARGO_HOME/config.toml` unless using `--path`.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
  https://doc.rust-lang.org/cargo/faq.html
- rustup already supports mirror roots through `RUSTUP_DIST_SERVER` and `RUSTUP_UPDATE_ROOT`, which means toolchain mirroring is a supported lane, not a hack.
  https://rust-lang.github.io/rustup/environment-variables.html
- crates.io’s January 2026 update added Trusted Publishing Only Mode and other publish-side hardening, which is useful but does not solve consumer-side install, mirror, or offline-validation truth.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- The 2026 flagships still put supply-chain work in the active milestone set through SBOM and public/private dependency work, reinforcing that distribution and verification surfaces remain strategic.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## Why this needs its own design layer
The archive already had [`design/airgap-kit.md`](./airgap-kit.md), but it still read mostly as a strong concept.
That was no longer enough because current Rust/Cargo signals now make the operational seams explicit:

- **workspace dependency/build lane**
  - `cargo fetch`, vendoring, local registries, and source replacement
- **developer-tool installation lane**
  - `cargo install`, install roots, binary metadata tracking, `--locked` posture
- **toolchain distribution lane**
  - rustup mirrors, targets, components, self-update roots
- **secure mirror verification lane**
  - signed / verified mirrors and threat-model-aware trust
- **combined restricted-network lane**
  - CI/bootstrap workflows that need all of the above without quietly mixing them up

Without a ranked pilot layer, this seam risks two bad outcomes:
1. **cache theater** — teams think “it built offline once on one machine” means the environment is reviewably airgapped;
2. **mirror folklore** — publish/mirror/install/toolchain concerns get glued together differently in every organization with no reusable artifact boundary.

## Design principles
1. **Pilot planes first, then integrated environments.** The archive should prove dependency/build, tool-install, and rustup lanes separately before claiming one complete story.
2. **Mirror topology is part of the contract.** Vendored directories, local registries, sparse mirrors, and full service mirrors are not interchangeable.
3. **Warm cache is not evidence.** A pilot should distinguish cached success from validated no-egress or mirror-only success.
4. **Consumer-side truth matters.** Publish-side hardening is useful, but it does not prove what installers, mirrors, and restricted clients actually consumed.
5. **Reuse official knobs.** Import Cargo and rustup configuration semantics instead of inventing rival environment models.
6. **Treat verification as a widening lane, not a prerequisite for every v0 pilot.** Exact-copy and no-egress truth should land before the archive pretends cryptographic mirror verification is already ubiquitous.
7. **Keep secrets and enterprise auth out of canonical packs.** Record modes, locations, and expectations, not credentials.

## Pilot artifact family
### 1. `airgap-pilot-brief/v0`
Why this lane is being piloted.

Should record:
- pilot id and summary
- primary lane (`workspace-build`, `tool-install`, `toolchain-mirror`, `mirror-verification`, `integrated-ci`)
- why the lane matters now
- why it is tractable now
- intended consumers and decision points

### 2. `airgap-plane-map/v0`
How the pilot slices the environment.

Should record:
- which of the three main planes are in scope
- which plane is primary
- how planes are linked
- what is explicitly deferred
- where ambiguity or future widening remains

Design rule: **do not let one pilot silently claim all planes.**

### 3. `airgap-mirror-topology-profile/v0`
How sources are provided.

Should record:
- topology kind (`vendor`, `local-registry`, `sparse-mirror`, `git-index-mirror`, `mixed`)
- source replacement / registry mapping posture
- exact-copy assumptions
- whether the topology is curated subset, mirror cache, or checked-in tree
- optional verification posture
- raw config attachments

### 4. `airgap-install-profile/v0`
How developer tools and binary crates are handled.

Should record:
- `cargo install` vs prebuilt binary vs internal package path
- install root and metadata tracking posture
- `--locked` / lockfile expectations
- config-discovery starting point
- whether compilation or download is expected
- how conflicts/reinstalls are reasoned about

### 5. `airgap-bootstrap-scorecard/v0`
Decides whether the pilot worked.

Should ask:
- did the pilot keep plane identity explicit?
- did it distinguish warm-cache from validated no-egress?
- did it make mirror topology reviewable?
- did it keep `cargo install` distinct from workspace builds?
- did it keep rustup/toolchain behavior explicit?
- did a real consumer use the result?
- did it surface where verification remained absent or partial?

### 6. `airgap-pilot-pack/v0`
Bundle for review and reuse:
- pilot brief
- plane map
- mirror topology profile
- install profile
- `airgap-profile`
- `airgap-lock`
- `airgap-check-report`
- scorecard
- rendered summaries and references

## Ranked first pilots

### 1) Workspace dependency/build lane
**Why first**
- Cargo already has the most official substrate here: `cargo fetch`, `--offline`, `--frozen`, `cargo vendor`, local registries, and source replacement.
- This is the cleanest place to prove exact-copy and no-egress truth without yet solving binary installs or toolchains.
- It is also where many regulated or firewalled teams hit pain first.

**Core artifacts**
- `airgap-profile`
- `airgap-lock`
- `airgap-check-report`
- `airgap-mirror-topology-profile`
- `airgap-bootstrap-scorecard`

**Primary consumers**
- workspace maintainers
- CI/bootstrap teams
- internal mirror operators
- policy/release tooling that wants “mirror-only build” evidence

### 2) Developer-tool installation lane
**Why second**
- `cargo install` is a recurring source of restricted-network pain precisely because it is *not* just another workspace build.
- Its config-discovery and lockfile behavior are concrete enough upstream that the archive can stop hand-waving here.
- This lane is crucial for bootstrapping developer environments and CI helpers.

**Core artifacts**
- `airgap-install-profile`
- `airgap-check-report`
- `airgap-bootstrap-scorecard`
- raw install-root / metadata attachments
- optional signed-binary / internal-package attachments

**Primary consumers**
- platform teams
- developer-experience owners
- security/compliance reviewers
- airgapped workstation bootstrap flows

### 3) Toolchain mirror lane
**Why third**
- rustup already exposes supported mirror roots, but teams still need a portable way to say which toolchains, targets, and components must exist in the restricted environment.
- This proves the archive can keep Cargo source truth and rustup distribution truth separate while still relating them.

**Core artifacts**
- `airgap-profile`
- `airgap-lock`
- `airgap-plane-map`
- rustup mirror / toolchain attachments
- `airgap-bootstrap-scorecard`

**Primary consumers**
- infra/platform teams
- cross-target / embedded / custom-target workflows
- offline workstation and CI bootstrap

### 4) Secure mirror verification lane
**Why fourth**
- The Rust project has explicit accepted work around cryptographic verification and mirroring, but the broader ecosystem is still in transition.
- This lane should only widen after the archive can already represent plain mirror topology and plane boundaries honestly.
- It is where “same bits from a mirror” becomes stronger than “same URLs and cached files”.

**Core artifacts**
- `airgap-mirror-topology-profile`
- verification / trust attachments
- `airgap-check-report`
- `airgap-bootstrap-scorecard`

**Primary consumers**
- security/compliance teams
- mirror operators
- regulated organizations
- downstream trust/policy tooling

### 5) Integrated restricted-network CI/bootstrap lane
**Why fifth**
- This is the real-world end state: workspace builds, tool installs, and toolchain provisioning all need to cooperate.
- It should come last so the archive does not fake simplicity before the individual planes are reviewable.

**Core artifacts**
- `airgap-pilot-pack`
- linked release / policy / signed-binary attachments
- bootstrap scripts/templates
- scorecard with explicit deferred areas

**Primary consumers**
- larger organizations
- release engineering
- policy and audit consumers
- long-lived internal platform stacks

## Success criteria
The pilot program succeeds when:
- at least one lane makes airgap truth **more reviewable than shell docs**;
- consumers can tell which plane failed without reverse-engineering the bootstrap scripts;
- the archive can represent both unverified mirror-only lanes and stronger verified-mirror lanes without flattening them;
- and future release/policy/toolchain consumers can import `airgap-pack/v0` instead of rediscovering restricted-network assumptions from scratch.

## Failure modes to avoid
- Treating `cargo install` success as equivalent to workspace-build success.
- Treating warmed caches as proof of policy-compliant offline operation.
- Pretending vendoring, local registries, and sparse mirrors are interchangeable.
- Smuggling rustup behavior into Cargo-only artifacts.
- Waiting for the full cryptographic mirroring story before shipping any useful restricted-network contract.

## Relationship to neighboring kits
- [`design/airgap-kit.md`](./airgap-kit.md) remains the primary design for schema and boundary shape.
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md) may attach airgap packs to release artifacts, but does not define restricted-network bootstrap truth.
- [`design/policy-kit.md`](./policy-kit.md) consumes airgap evidence for decision-making, but should not redefine its lane semantics.
- [`design/signed-binaries-kit.md`](./signed-binaries-kit.md) can attach signed-install evidence, but does not replace mirror topology or tool-install posture.
- [`design/cross-toolchain-kit.md`](./cross-toolchain-kit.md) and [`design/sysroot-pack-kit.md`](./sysroot-pack-kit.md) remain about provisioning/productized toolchains, not restricted-network transport and validation posture.
