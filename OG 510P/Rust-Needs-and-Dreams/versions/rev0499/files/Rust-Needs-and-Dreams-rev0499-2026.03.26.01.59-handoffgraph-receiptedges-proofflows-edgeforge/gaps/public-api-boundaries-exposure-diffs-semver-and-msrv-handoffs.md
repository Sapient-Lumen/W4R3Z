# Gap: public API boundaries, exposure drift, semver evidence, and MSRV-bounded handoffs

## The gap
Rust has real pieces for API-boundary work—rustdoc JSON, `cargo-public-api`, `cargo-semver-checks`, the SemVer guide, docs.rs rustdoc JSON hosting, and the public/private-dependency effort—but it still lacks one boring shared answer to:
- what exact public boundary was compared?
- which dependencies are deliberately or accidentally part of that boundary?
- which structural changes were observed?
- which ambiguous changes were escalated to compiler-backed witness checks?
- which MSRV / feature / cfg / target posture bounded the claim?
- what later consumers are allowed to conclude from the result?

## Why this is still missing
The relevant truth is spread across:
- rustdoc JSON files and their format-version caveats,
- `cargo-public-api` snapshots and diffs,
- `cargo-semver-checks` lint and witness work,
- Cargo's unstable `public-dependency` and `sbom` features,
- SemVer guide prose,
- and maintainer-specific release workflows.

That fragmentation is survivable for experts and poor for the broader ecosystem.

## What a worthy contribution looks like
A worthy contribution is a **thin reviewable public-API contract** that keeps these distinct:
- public-boundary subject truth,
- exposure truth,
- structural-diff truth,
- witness/type-proof truth,
- bounded verification truth,
- and consumer-handoff truth.

## What would not count
- another CLI that prints API diffs but exports no portable handoff;
- a single “upgrade-safe” badge;
- a publish bot that hides waivers and unsupported lanes;
- or an assistant answer that cannot tell structural suspicion from compiler-backed proof.
