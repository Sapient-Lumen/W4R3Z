# Gap: Rust still lacks one portable consumer-install boundary

## Summary
Rust is getting better at **publishing crates**, **cutting releases**, **shipping signed binaries**, **emitting release manifests**, and **updating already-installed tools**.
What it still lacks is a thin, reviewable boundary for the **first acquisition/install event itself**:

> what exactly was requested, what install candidates were visible, what policy selected one of them, what verification actually ran, what landed on disk, and what did the installing tool claim to manage afterward?

Today that truth is still fragmented across:
- `cargo install` source builds,
- `cargo-binstall` prebuilt downloads,
- cargo-dist manifests/installers,
- GitHub Action wrappers and fallback logic,
- package-manager or install-script lanes,
- and a growing set of tool-local receipts or partial logs.

Those paths are **not semantically equivalent**.
A source build, a prebuilt archive, a package-manager formula, and a mirror fallback may all end with “the tool is installed”, but they differ in:
- what candidate set was actually visible,
- whether the packaged lockfile mattered,
- what verification was available versus required versus skipped,
- what host/mirror/package-manager lane actually served the bits,
- and what local files or paths the installer claims to manage afterward.

## Why now
- Cargo’s install docs still say the packaged `Cargo.lock` is ignored by default unless `--locked` is passed, and they explicitly document install-root metadata tracking plus `--no-track`, which disables that file and Cargo’s concurrent-install protection.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- Cargo packaging docs now explicitly say `--exclude-lockfile` is not for general use because some tools expect the lockfile to be present, including `cargo install --locked`.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- `cargo-binstall` is now a serious prebuilt lane, but its docs still describe signatures as initial/limited and expose explicit policy knobs like `--only-signed` and `--skip-signatures`.
  https://github.com/cargo-bins/cargo-binstall
- cargo-dist’s February 2026 release added mirror-aware fallback ordering for installers/hosts, which makes visible candidate ordering and actual selected source materially more important.
  https://github.com/axodotdev/cargo-dist/blob/main/CHANGELOG.md
- `taiki-e/install-action` now openly exposes fallback choices between `cargo-binstall` and `cargo install`, which is strong evidence that CI acquisition already has plural lanes rather than one canonical path.
  https://github.com/taiki-e/install-action
- `axoupdater` already has an install-receipt concept in its library surface, but that receipt is updater-specific rather than the missing shared Rust consumer-install boundary.
  https://docs.rs/axoupdater/latest/axoupdater/
- crates.io’s current momentum is still mostly publish-side: Trusted Publishing controls and `pubtime` improve producer truth without telling support, incident, or policy consumers what any given machine actually installed.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

## Concrete missing pieces
1. **An install subject boundary**
   - requested package/tool/app identity
   - requested version or range
   - requested binaries / target / install root / mutation scope
   - caller intent like `source-only`, `prebuilt-first`, `mirror-only`, `package-manager-only`

2. **A visible candidate catalog**
   - source-build candidate
   - prebuilt archive candidate
   - installer candidate
   - package-manager candidate
   - mirror variants and host order
   - target/support/verification posture per candidate

3. **A reviewable install policy + plan**
   - why one candidate was ranked above another
   - why a fallback was allowed or refused
   - which checks were required versus opportunistic
   - which install root or manager scope was allowed

4. **A durable install receipt**
   - what was actually fetched/built
   - what verification passed, warned, failed, or was skipped
   - whether source installs used packaged lock truth or recomputed dependencies
   - what files/paths were mutated
   - what the installing tool claims it manages afterward

5. **A strict boundary between install and later lifecycle continuity**
   - first-install truth should stop at one acquisition/mutation event
   - update/rollback/uninstall continuity should import that receipt later instead of redefining it

## Desired properties
- Reuse producer-side release/signature evidence instead of competing with it.
- Keep source-build installs first-class rather than pretending only prebuilt binaries count.
- Preserve host/mirror/package-manager fallback order explicitly.
- Preserve honest incompleteness (`WARN`, `INCONCLUSIVE`, skipped checks).
- Make manager identity and managed-content scope explicit.
- Stay useful in CI and restricted-network environments.
- Give support/incident/policy/update tooling a durable receipt instead of terminal archaeology.

## Distinction from nearby archive entries
- **Release Truth Stack** owns what the producer published.
- **Signed Binaries Kit** owns prebuilt-artifact issuer and verification evidence.
- **Airgap Kit** owns restricted-network mirror topology and validation posture.
- **Update Continuity Kit** owns post-install compare/plan/apply/rollback/uninstall continuity.
- **Distribution Contract Stack** should compose the leaf-level install boundary with producer/imported evidence and downstream handoffs.

This missing piece sits **between** them:
- it imports producer-side release/signature truth,
- performs one consumer-side acquisition/install event,
- emits a durable install receipt,
- and hands later lifecycle continuity to Update Continuity rather than absorbing it.

## What an epic contribution would look like
A worthy contribution here would **not** be another installer script, another package-manager shim, another self-update helper, or another release website.
It would be a thin **Consumer Install Kit** that can:
- describe the requested install subject,
- catalog visible candidates honestly,
- preserve policy and refusal reasons,
- emit a durable install receipt,
- and hand later lifecycle work to update/support/policy consumers without pretending the first install event was the whole story.

The prize is not merely “faster installs”.
The prize is **portable consumer-install truth**.


## What the archive should do next
The archive should now sharpen this gap with an explicit lane map and ranked pilot plan:
- add `design/consumer-install-lane-map.md` so source-build, prebuilt, mirror/host, CI-wrapper, delegated/imported, and receipt/managed-content lanes stop blurring together;
- add `design/consumer-install-pilot-program.md` so the archive proves `cargo install` first, then prebuilt, mirror/fallback, CI-wrapper, delegated-manager, and downstream-handoff lanes in that order;
- keep first install separate from Update Continuity so later update/rollback/uninstall work imports the install receipt rather than redefining the first acquisition event.
