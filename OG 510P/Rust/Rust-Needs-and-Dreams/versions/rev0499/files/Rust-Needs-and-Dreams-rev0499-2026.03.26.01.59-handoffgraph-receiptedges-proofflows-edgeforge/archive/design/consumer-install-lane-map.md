# Design: Consumer Install Lane Map (source builds, prebuilt binaries, mirror fallback, CI wrappers, delegated managers, install receipts)

## Goal
Make the archive more precise about **what kind of first-install claim is actually being made**.

Rust already has many ways to get software onto a machine, but the phrase “installation support” still hides too much.
A `cargo install` source build, a `cargo binstall` prebuilt fetch, a cargo-dist installer choosing between primary and mirror hosts, a CI wrapper like `install-action` using manifests and fallback, and a delegated package-manager or hand-import lane are **different but connected** lanes.

The worthy contribution here is therefore not another installer, release website, or package-manager shim.
It is a **portable lane map and evidence boundary** that lets tools say which install lane they occupy, what assumptions attach to it, where adapters are lossy, and which downstream consumers may reuse the claim honestly.

Read this together with:
- [`design/consumer-install-kit.md`](./consumer-install-kit.md)
- [`design/consumer-install-pilot-program.md`](./consumer-install-pilot-program.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)
- [`design/update-continuity-kit.md`](./update-continuity-kit.md)
- [`design/release-truth-stack.md`](./release-truth-stack.md)
- [`design/signed-binaries-kit.md`](./signed-binaries-kit.md)
- [`proposals/epic-consumer-install-kit.md`](../proposals/epic-consumer-install-kit.md)

## Why this note is needed now
The current Cargo/ecosystem signals line up around one conclusion: Rust needs a better **consumer-install contract**, not just more installer variants.

- `cargo install` keeps the source-build lane sharp: packaged `Cargo.lock` is ignored by default unless `--locked` is used, the install root carries tracking metadata by default, and `--no-track` disables that file plus Cargo’s concurrent-install protection. That means first install already has lock/ownership/state semantics that other lanes do not share.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- Cargo packaging docs now say `Cargo.lock` is always included unless `--exclude-lockfile` is used and warn that the flag is not for general use because some tools expect the lock file, including `cargo install --locked`. That is a strong producer→consumer coupling signal.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- `cargo-binstall` is explicit that it searches linked repository releases for matching artifacts, falls back to quickinstall, tries alternate targets, and only finally falls back to `cargo install`. It also documents signature support separately. That means prebuilt install is a distinct candidate-selection lane, not “Cargo install but faster.”
  https://github.com/cargo-bins/cargo-binstall
  https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md
- cargo-dist 0.31.0 added mirror-aware hosting fallback and says mirror priority follows config order. That means visible candidate order and actual selected source are first-class install facts rather than release-page trivia.
  https://github.com/axodotdev/cargo-dist/blob/main/CHANGELOG.md
- `taiki-e/install-action` now openly exposes manifest-managed installs, `cargo-binstall` fallback, `cargo install` fallback, checksum verification, optional signature verification, and distro package-manager setup for prerequisites. That is direct evidence that CI install lanes are plural and partially delegated.
  https://github.com/taiki-e/install-action
- `axoupdater` uses install receipts produced by cargo-dist and says those receipts contain metadata about the currently-installed version and the cargo-dist version that produced it. That is strong evidence that install receipts are real, but still too tool-local to be the missing shared Rust boundary.
  https://github.com/axodotdev/axoupdater
- crates.io’s recent work on Trusted Publishing and `pubtime` improves producer-side truth, but it still does not answer what any given user machine or CI runner actually installed. That is exactly why the consumer-install boundary must stay separate from publish truth.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

## The lane map

### Lane 1 — Source-build install lane (`cargo install`)
**What it is**
- First install by building a crate from source via Cargo.
- Usually rooted in crates.io, git, or local-path package identity plus Cargo’s install-root conventions.

**Why it matters**
- This is the baseline consumer-install lane for Rust tools.
- It preserves packaged-lock posture, registry/index choice, build environment assumptions, and Cargo-owned install metadata that other lanes do not inherit.

**What the archive should preserve**
- requested package/binary/version/target/root,
- source kind (`crates-io`, `git`, `local-path`, alternate registry),
- whether packaged lock truth was ignored or forced with `--locked`,
- whether tracking metadata existed or `--no-track` was used,
- and what Cargo claims to manage afterward.

**What it should not pretend**
- that a source-build install is interchangeable with prebuilt acquisition,
- that crates.io release truth equals installed-state truth,
- or that one “install succeeded” message proves ownership or reproducibility posture.

### Lane 2 — Prebuilt binary lane (`cargo-binstall`, direct binary archive fetch)
**What it is**
- First install by selecting a released binary artifact instead of compiling locally.
- Candidate search may involve repository releases, quickinstall-like mirrors, alternate targets, checksums, signatures, and final fallback to source build.

**Why it matters**
- Candidate visibility, target matching, and verification posture differ materially from source-build installs.
- The final applied result can still drift if fallback changes the chosen lane.

**What the archive should preserve**
- candidate artifact family and host,
- target/arch matching and alternate-target logic,
- checksum/signature/attestation posture,
- fallback order and final chosen lane,
- and lossy-import notes when only partial shell/CI evidence survives.

**What it should not pretend**
- that prebuilt and source-built installs are interchangeable,
- that signature support automatically means every install was verified,
- or that the first visible candidate was the one actually applied.

### Lane 3 — Mirror / installer-host lane (cargo-dist-style host ordering)
**What it is**
- A first install flow where the installer or shell/bootstrapper can choose among multiple hosts or mirrors for the same release payload.

**Why it matters**
- Host order, outage fallback, and selected source become part of the install event.
- This lane is especially important for airgapped, mirrored, or high-availability deployment stories.

**What the archive should preserve**
- ordered host/mirror candidates,
- selected host and fallback reason,
- installer identity and version,
- partial/interrupted-install notes,
- and imported producer-side release evidence.

**What it should not pretend**
- that all mirrors are equivalent trust anchors,
- that release truth alone proves the selected download path,
- or that selected-host facts can be reconstructed later from version number alone.

### Lane 4 — CI wrapper / delegated bootstrap lane (`install-action`, scripted fallback)
**What it is**
- A first install flow mediated by an automation wrapper, manifest, or bootstrap action that may choose among release downloads, `cargo-binstall`, `cargo install`, and prerequisite package-manager setup.

**Why it matters**
- The wrapper’s own manifest/fallback/security policy becomes part of the install contract.
- CI installs often create the only surviving evidence for developer-tool acquisition in real projects.

**What the archive should preserve**
- wrapper identity/version,
- manifest-managed vs fallback install path,
- checksum/signature policy,
- prerequisite-manager behavior,
- and what was implementation detail versus durable installed subject.

**What it should not pretend**
- that CI wrapper behavior is the same as a direct user install,
- that wrapper success proves a clean one-lane install story,
- or that setup dependencies installed transiently are part of the managed app/tool forever.

### Lane 5 — Delegated manager / imported install lane (Homebrew, Snap, distro package, app store, enterprise agent)
**What it is**
- A first install flow whose authority and mutation are owned by an external package manager, store, enterprise agent, or imported forensic record.

**Why it matters**
- Many Rust tools and apps end up here, and the correct first-install output is often an explicit delegated or lossy receipt rather than a direct mutation claim.
- This lane is where Rust-side tools must stay honest about ownership boundaries.

**What the archive should preserve**
- delegate identity,
- imported evidence and lossiness,
- what current tool can and cannot verify,
- and which later update/uninstall facts remain external.

**What it should not pretend**
- that external ownership is merely a weaker version of direct install,
- that a Rust-side wrapper knows what every external manager actually did,
- or that imported provenance can be silently upgraded into direct receipts.

### Lane 6 — Receipt / managed-content lane
**What it is**
- The lane where the install event becomes durable enough for later lifecycle continuity, support, incident review, or policy import.

**Why it matters**
- `axoupdater` and cargo-dist already prove install receipts are real.
- Without a portable receipt lane, every downstream consumer keeps rescraping terminals, CI logs, or platform-specific state.

**What the archive should preserve**
- receipt identity/version,
- selected lane and evidence inputs,
- what files/roots were mutated when known,
- manager identity and managed-content scope,
- and explicit unknowns.

**What it should not pretend**
- that receipt capture is universal today,
- that receipt success proves later update continuity,
- or that downstream consumers may silently infer stronger ownership than the receipt actually states.

## Lane transitions the archive must keep explicit
1. **requested subject ↔ visible candidates**
   - what the user asked for is not the same truth as what candidate set was visible.
2. **candidate visibility ↔ chosen plan**
   - ranking/refusal reasons are not the same as applied result.
3. **direct install ↔ delegated/imported install**
   - authority and completeness change what the Rust-side tool may claim.
4. **install event ↔ managed-content receipt**
   - successful apply is not the same as durable ownership/receipt capture.
5. **first install ↔ later update continuity**
   - update/rollback/uninstall logic must import the install receipt rather than redefining the original event.

## What should change elsewhere in the archive
- **Consumer Install Kit** should remain the base artifact family, but it should now cite this lane map as the rule for what must stay separate.
- **Distribution Contract Stack** should keep composing producer-side release/signature truth with leaf install truth, not re-owning the leaf install event.
- **Update Continuity Kit** should import `install-receipt/v0` and managed-content posture instead of silently narrating first install.
- **Signed Binaries Kit** should keep owning artifact issuer/verification evidence rather than becoming the install authority.
- **Airgap Kit** should keep owning mirror topology and restricted-network validation posture.
- **Support / policy / inventory consumers** should import bounded install facts instead of retroactively inventing one cleaner install story than the evidence supports.
