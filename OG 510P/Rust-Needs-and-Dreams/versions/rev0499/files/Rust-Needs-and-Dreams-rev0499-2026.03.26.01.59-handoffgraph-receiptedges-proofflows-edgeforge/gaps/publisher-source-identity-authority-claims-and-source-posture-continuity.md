# Gap: publisher/source identity, authority/claim boundaries, and source-posture continuity

## Current interpretation after rev0406
This gap is now the execution-side deficit statement beneath the promoted **Publisher & Source Identity Contract**.
Read it as the concrete explanation for why the archive elevated publisher/source identity into a first-class frontier instead of leaving it scattered across trust, namespace, package-intake, and install notes.

# Gap: publisher/source identity, authority/claim boundaries, and source-posture continuity

## What is missing
Rust now has materially stronger identity-relevant signals around crates, but it still lacks a **portable identity handoff layer** that keeps the following questions distinct:
- who may publish;
- which source or registry path is in play;
- which project-family or namespace claim is being made;
- which of those are hard facts versus suggestive labels;
- and what later package-admission, trust, and install consumers may honestly conclude.

Today the ecosystem can separately observe:
- crate owners and team owners;
- issuer-backed Trusted Publishing posture;
- authenticated alternate registries;
- exact-copy source replacement and vendored sources;
- optional-namespace control as an active implementation seam;
- and UI/API shifts that increasingly treat **owners**, not manifest authors, as the user-facing identity surface.

What is still missing is the shared layer that answers:
- whether a publish path was token-backed or issuer-backed;
- whether a package came from crates.io, an alternate registry, or an exact-copy replacement path;
- whether `projectname-*` or `parent::child` reflects actual control or only a loose family claim;
- where best-effort VCS/source hints stop and verified provenance does not begin;
- and how those facts should be exported for policy, package-admission, or install receipts without collapsing them into one fake trust verdict.

## Why it matters
Rust’s current identity story is now strong enough that confusion becomes expensive.

A team reviewing a crate may need to know all of these at once:
- whether the package is controlled by the people they think it is;
- whether publication is restricted to a trusted CI issuer or still token-capable;
- whether a registry entry is coming from an alternate registry or a mirror/replacement path;
- whether the user-facing crate-family label is namespace-enforced, maintainer-declared, or merely implied by a prefix;
- and whether package-time source hints are actually verified.

Without a shared publisher/source identity substrate, downstream tools keep reinventing partial answers:
- registry UI badges that overclaim;
- policy rules that confuse “published by a trusted issuer” with “safe to use”;
- install receipts that forget where software actually came from;
- namespace debates that quietly swallow source/auth questions;
- and support or incident tooling that cannot reconstruct whether the observed artifact followed the expected identity path.

A worthy contribution here would make identity facts easier to **report, compare, import, and constrain** without forcing Rust to settle every registry-governance or namespace argument first.

## Existing building blocks worth composing
- crates.io now supports GitLab Trusted Publishing, Trusted-Publishing-only mode, and blocks risky GitHub Actions triggers. That makes publish authority more explicit and more issuer-shaped than it used to be.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo’s publishing docs and `cargo owner` docs draw a hard distinction between named owners and team owners, including different authority and mutability semantics.
  https://doc.rust-lang.org/cargo/reference/publishing.html
  https://doc.rust-lang.org/cargo/commands/cargo-owner.html
- Cargo’s registry-authentication docs require credential-provider posture for authenticated alternate registries, while the registries and source-replacement docs keep alternate registries and replacement sources as distinct concepts.
  https://doc.rust-lang.org/cargo/reference/registry-authentication.html
  https://doc.rust-lang.org/cargo/reference/registries.html
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
- `cargo package` includes `.cargo_vcs_info.json`, but the docs explicitly say the provenance is not verified and the tarball is not guaranteed to match that VCS information. That is a useful fact, but not verified source identity.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- RFC 3243 and the active open-namespaces project goal make namespace control an active implementation seam rather than a permanently hypothetical debate.
  https://rust-lang.github.io/rfcs/3243-packages-as-optional-namespaces.html
  https://rust-lang.github.io/rust-project-goals/2025h2/open-namespaces.html
- RFC 3052 made `package.authors` optional and moved crates.io/docs.rs UI toward current owners, which is strong evidence that manifest authorship, current ownership, and user-facing identity are already separate planes.
  https://rust-lang.github.io/rfcs/3052-optional-authors-field.html

## Why existing tools are not yet the whole answer
The ecosystem now has **owners, registry config, credential providers, Trusted Publishing, namespaces, and packaging hints**, but not the **shared identity brief layer**:
- crates.io and Cargo can tell you who owns a crate;
- Trusted Publishing can tell you whether an issuer-backed lane exists;
- registries/source-replacement docs can tell you what kinds of source configuration exist;
- RFC 3243 can tell you what namespace control is supposed to mean;
- `cargo package` can emit best-effort VCS metadata;
- package-admission, trust, and distribution layers can import some of this.

But teams still have to invent their own answers for:
- normalized authority-vs-claim-vs-source reporting;
- explicit uncertainty and non-claim posture;
- explainable import boundaries for trust/policy consumers;
- package→release→install identity continuity;
- and renewable identity diffs when owner/source/publisher posture changes.

That is the same pattern seen elsewhere in this archive: strong point facts, weak shared artifacts.

## Target outcome
A project should be able to say:
- “this is the package, family, or namespace claim under discussion,”
- “this is the publish-authority posture and its evidence,”
- “this is the registry/source/replacement path and auth posture,”
- “this is where VCS/package hints stop and verified provenance does not begin,”
- “these are the exact fields later trust/admission/install consumers may import,”
- and “this is the portable pack humans and tools may consume.”

That is bigger than a registry settings page and smaller than a universal crate-governance system.
