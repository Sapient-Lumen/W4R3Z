# Gap: package admission still lacks one honest publish-review boundary

Rust increasingly has the ingredients for serious package publication review, but it still lacks a **portable admission boundary** that joins them without collapsing them.

Today, a maintainer can recover pieces of the story from official tooling and registry surfaces:
- `cargo publish` and `cargo package` define **which package(s)** are selected, what verification ran, which registry was targeted, and whether Cargo saw the package appear in the index;
- `cargo package --list --message-format json` is starting to expose **packaged payload truth** in machine-readable form;
- public/private dependencies and `cargo-semver-checks` are pushing publish-time review closer to the **public contract** itself;
- Cargo SBOM precursor work is pushing package/build inventory toward a durable machine-readable lane;
- crates.io now exposes stronger package-side trust signals such as a Security tab, Trusted Publishing controls, and `pubtime`.

But those facts still do not add up to one explicit answer to the question the ecosystem increasingly needs:

**what package set and packaged payload were actually admitted for publication, under what evidence, under what waivers, and with what bounded handoff to later release/install/support consumers?**

## Why this matters more now
The pressure is no longer hypothetical:
- Rust’s 2026 flagships explicitly keep **Cargo SBOM support** active, which makes package-side inventory continuity an upstream concern.
- Cargo’s unstable features already expose `public-dependency` and `sbom`, meaning package-admission-relevant facts are becoming explicit machine-facing seams rather than folklore.
- The 2025H2 `cargo-semver-checks` goal explicitly aims at integrating SemVer review into the `cargo publish` workflow, with an override when the maintainer intentionally proceeds.
- `cargo package` now has an unstable machine-readable listing surface and explicitly says `.cargo_vcs_info.json` is only a best-effort snapshot rather than verified provenance.
- crates.io’s January 2026 update added GitLab Trusted Publishing, Trusted-Publishing-only mode, blocked risky GitHub triggers, and `pubtime`, which makes authority-path and publish-time visibility richer than before.
- Cargo publishing is durable enough that later reviewers need to understand what was actually admitted without replaying a transient CI job.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://doc.rust-lang.org/cargo/reference/unstable.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
- https://doc.rust-lang.org/cargo/commands/cargo-publish.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

## What is missing
The missing layer is not another release bot, registry score, or upload wrapper.
It is the review boundary that keeps these truths distinct while composing them:

1. **publish-set truth**
   - which package(s) were selected;
   - what files and normalized manifest actually went into the package(s);
   - what checks ran or were waived;
   - what authority path and registry path were used;
   - what upload/index receipt existed.

2. **graph-control truth**
   - which versions, sources, features, and public/private dependency choices actually shaped the published package review.

3. **public-contract truth**
   - what API/exposure/semver/MSRV evidence mattered for admission.

4. **inventory truth**
   - what component or SBOM evidence existed, with what scope and lossiness.

5. **trust-signal truth**
   - what publisher/freshness/name-risk/advisory/audit signals were visible at decision time.

6. **decision truth**
   - what policy profile, waivers, and `admit` / `hold` / `warn` / `INCONCLUSIVE` result were actually recorded.

7. **handoff truth**
   - what later still belongs to release bundles, binary signatures, rebuild evidence, distribution/install receipts, support promises, or incident consumers.

## What this should not become
This should **not** become:
- a prettier crates.io moderation page;
- a universal crate-risk score;
- another `cargo publish` wrapper that hides Cargo’s own semantics;
- a binary-release umbrella that swallows package upload truth;
- a trust engine that silently rewrites evidence into one verdict;
- a package dashboard that erases waivers, unsupported lanes, or package-vs-release boundaries.

## What a worthy contribution would look like
A real contribution here would define a thin **Package Admission Stack** that imports:
- `publish-pack/v0` from **Publish Set Kit**;
- graph/activation evidence from **Dependency Control Stack**;
- `api-pack/v0` from **Public API Kit**;
- inventory attachments from **SBOM Evidence / Inventory Evidence**;
- trust inputs from **Trust Signals Kit**;
- explicit decisions from **Policy Kit**.

It would then export a small family such as:
- `package-subject/v0`
- `package-admission-brief/v0`
- `package-release-handoff/v0`
- `package-admission-pack/v0`

The point is not one more check.
The point is that a maintainer, CI system, registry, downstream packager, or assistant should be able to answer:
- what package set was under review;
- what payload and publish path were actually admitted;
- what API / inventory / trust evidence mattered;
- what waivers were used;
- and what later consumers still need to prove.

## Strongest path forward in this archive
The strongest current path is to treat **Package Admission Stack** as the thin publish-review layer above:
- **Publish Set Kit** for selected package/payload/check/receipt truth;
- **Dependency Control Stack** for chosen graph and activation truth;
- **Public API Kit** for exposure/semver/MSRV truth;
- **SBOM Evidence / Inventory Evidence** for component capture and lossiness;
- **Trust Signals Kit** for publisher/freshness/audit/advisory inputs;
- **Policy Kit** for explicit decisions and waivers.

That keeps the stack honest: it can review what was admitted for package publication without pretending it already proved broader release, binary, install, or support truth.

See also:
- `design/package-admission-stack.md`
- `design/package-admission-pilot-program.md`
- `proposals/epic-package-admission-stack.md`
