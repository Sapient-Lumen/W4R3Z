# RubyGems Native Extension ShipKit — product plan (2026-03-18)

This note sharpens **P-0501 RubyGems Native Extension ShipKit** into an implementation-ready `0.1` shape.

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps maintainers publish one reviewable answer to:

- which gem platforms actually ship as binary gems,
- which users still fall back to source builds,
- what Bundler / Ruby-engine / lockfile route users will actually take,
- where the extension actually resides and is required from,
- and whether the release identity / rebuild story is boring enough for package reviewers and downstream users.

It should **not** try to become a replacement for RubyGems, Bundler, `rb-sys`, `magnus`, or CI publishing tools.
Those are substrate and workflow partners, not the missing product.

## What the crate should provide other people

For maintainers, release engineers, support reviewers, and downstream Ruby users, the crate should provide:

1. **One compact support contract** instead of release truth spread across gemspecs, lockfiles, CI, require stubs, and install folklore.
2. **A platform-coverage report** that states which binary gems exist and where source-build fallback still applies.
3. **A resolver-route report** that says how Bundler / RubyGems are likely to resolve the gem for MRI / JRuby / TruffleRuby and for different lockfile target sets.
4. **An extension-residency report** that says where the compiled extension actually lands and how Ruby is expected to require/load it.
5. **A diffable release bundle** that makes platform, route, and load drift visible across releases.

## Three first-class review objects

### 1. Platform coverage

This should stay separate from “the gem built once in CI”.

Named classes for `0.1`:
- `platform_contract_ok`
- `fat_gem_gap`
- `source_build_only`
- `manual_review_required`

This object should answer:
- which `.gem` artifacts actually exist,
- which platforms are covered by binary gems,
- where the release still depends on install-time compilation,
- and whether README / support text exceeds the observed artifact matrix.

### 2. Resolver route

This should answer questions like:
- whether Gemfile `platforms:` and Ruby-engine expectations align with the package’s support claims,
- whether the lockfile/platform additions needed for multi-platform installs are actually present,
- whether `bundle cache --all-platforms` or equivalent workflow assumptions are satisfied,
- whether `force_ruby_platform` or source-build fallback materially changes what users will install,
- and whether JRuby / TruffleRuby / alternate routes are honest or merely aspirational.

### 3. Extension residency

This should stop the product from treating “a shared library exists somewhere” as enough.
It should say explicitly:
- whether the extension build hooks and packaged artifact layout agree,
- whether copied files under `lib/` and `require` stubs still point at the right basename/location,
- whether gemspec platform and runtime load expectations align,
- and whether there is obvious drift after gem/lib/module renames.

## Recommended `0.1` command surface

### `cargo rubygem-ship inspect`
Read project facts from the gemspec, `Gemfile.lock`, Bundler config, built gem artifacts if present, require stubs, Ruby extension layout, Cargo metadata, and CI metadata.
Emit early observations without pretending the release is valid yet.

### `cargo rubygem-ship check`
Run policy checks for:
- missing or ambiguous binary-gem coverage,
- README / platform coverage drift,
- missing lockfile platform targets for claimed support routes,
- JRuby / TruffleRuby support claims that exceed actual resolution evidence,
- missing or unclear copied-extension/load paths,
- and publish/rebuild/manual-review boundaries.

### `cargo rubygem-ship diff <old> <new>`
Compare release bundles and classify:
- `platform_coverage_changed`
- `resolver_route_changed`
- `extension_residency_changed`
- `publish_identity_changed`
- `rebuild_parity_changed`
- `manual_review_boundary_changed`

### `cargo rubygem-ship bundle`
Produce one compact `.rubygembundle.zip` containing normalized receipts plus a short summary.

## Recommended crate/workspace split

- `rubygem_ship_model`
  - shared types for policies, receipts, reports, and diffs
- `rubygem_ship_import`
  - gemspec parsing, built-gem inventory import, lockfile/Bundler import, require-stub/import logic
- `rubygem_ship_check`
  - policy checking and conservative classification
- `rubygem_ship_render`
  - markdown summaries and zip bundle export
- `cargo-rubygem-ship`
  - user-facing cargo subcommand

Optional later adapters:
- `rubygem_ship_rubygems_api`
- `rubygem_ship_rb_sys_import`
- `rubygem_ship_release_gem_import`

## `0.1` artifact set

Core artifacts should be:
- `rubygem-shipkit.toml`
- `platform-coverage.report.json`
- `resolver-route.report.json`
- `extension-residency.report.json`
- `build-toolchain.receipt.json`
- `publish-identity.receipt.json`
- `rebuild-parity.report.json`
- `support-risk.report.json`
- `notes.md`

This pass says `0.1` also needs one sharper support artifact:
- `lockfile-platform.receipt.json`

That matters because the shipkit gets vague again if it only records built gems and gemspec metadata without showing whether downstream multi-platform intake was actually represented in the lockfile / Bundler story.

## Discovery order

1. **Package metadata inspection**
   - gemspec platform / extension hooks / require paths
   - supported Ruby version family
   - artifact naming expectations
2. **Artifact inspection**
   - produced `.gem` files
   - packaged shared libraries / copied `lib/` files
   - checksums / publish intent
3. **Platform-coverage receipt**
   - binary-gem inventory
   - source-build fallback
   - hybrid/manual-review boundaries
4. **Resolver-route receipt**
   - Gemfile `platforms:` / Ruby engine intent
   - `Gemfile.lock` platform targets
   - bundle-cache / multi-platform route assumptions
   - fallback/manual-review boundaries
5. **Extension-residency receipt**
   - built shared object names
   - copied files under `lib/`
   - require stub alignment
   - runtime load expectations
6. **Bundle + diff**
   - reviewable summary
   - previous-release comparison

## Ranking discipline

The first implementation should not treat “the gem installed locally” as the verdict.
A good `0.1` should keep separate:
- `platform_contract_known`
- `resolver_route_known`
- `extension_residency_known`
- `publish_identity_known`
- `rebuild_parity_known`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- Bundler `bundle gem --ext=rust`
- RubyGems platform / extensions / require-path rules
- Bundler Gemfile engine/platform rules
- Bundler multi-platform cache/lockfile behavior
- trusted publishing and release-gem substrate
- `gem rebuild` / reproducibility substrate
- `rb-sys`, `magnus`, and fat-gem deployment guidance

### Do not flatten into one fake verdict
- “Bundler generated a Rust extension skeleton”
- “the gem built once in CI”
- “a `.gem` file exists for one platform”
- “the shared library exists somewhere in the package”
- “trusted publishing was configured”
- “the maintainer says JRuby is supported”

## Preferred proving grounds

- a clean MRI binary-gem matrix with copied extension files and require stubs aligned
- a gem that claims “fat gem support” but omits one common target from the actual artifact set
- a gem that claims JRuby / alternate-engine support while the lockfile and cache route still only reflect MRI/native paths
- a gem whose extension basename or copied `lib/` file path drifts after a rename

## Non-goals

- not another Rust↔Ruby binding generator
- not a generic gem publishing bot
- not a replacement for RubyGems or Bundler
- not a promise that one successful local install implies boring support for all users

## MVP API sketch

```rust
pub enum PlatformCoverageClass {
    PlatformContractOk,
    FatGemGap,
    SourceBuildOnly,
    ManualReviewRequired,
}

pub fn inspect_release(root: &Path) -> Result<ReleaseInspection>;
pub fn evaluate_platform_coverage(release: &ReleaseInspection) -> Result<PlatformCoverageReport>;
pub fn evaluate_resolver_route(release: &ReleaseInspection) -> Result<ResolverRouteReport>;
pub fn evaluate_extension_residency(release: &ReleaseInspection) -> Result<ExtensionResidencyReport>;
pub fn write_bundle(bundle: &RubygemBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Follow RubyGems / Bundler official docs closely.
- Follow `rb-sys` / `magnus` / oxidize.rb as substrate, not as the entire product.
- Preserve `manual review required` whenever the crate cannot safely infer platform, route, or residency truth.
