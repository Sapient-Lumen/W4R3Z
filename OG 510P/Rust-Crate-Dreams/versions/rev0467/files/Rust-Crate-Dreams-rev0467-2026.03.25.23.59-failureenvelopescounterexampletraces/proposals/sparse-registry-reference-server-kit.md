---
id: P-0135
title: Sparse Registry Reference Server Kit — open, compatible, self-hostable Cargo sparse registries + mirrors
status: idea
domains: [cargo, enterprise, supply-chain, infra]
last_reviewed: 2026-03-05
evidence:
  - https://doc.rust-lang.org/cargo/reference/registries.html
  - https://rust-lang.github.io/rfcs/2789-sparse-index.html
  - https://doc.rust-lang.org/cargo/reference/registry-index.html
  - https://jfrog.com/help/r/jfrog-artifactory-documentation/index-cargo-repositories-using-sparse-indexing
needs:
  - A clean, open-source “reference implementation” for the **sparse registry protocol** that teams can self-host, mirror, cache, and audit.
  - A compatibility test suite that ensures the server behaves like Cargo expects (HTTP caching, partial fetches, correct `config.json`, and edge cases).
  - A practical offline story for CI and air-gapped builds that doesn’t require bespoke enterprise tooling.
non_goals:
  - Replacing crates.io.
  - Being a full artifact manager (Artifactory/Nexus competitor).
what_it_provides:
  - A production-quality sparse registry server:
    - Serves a sparse index (with correct caching headers, compression, and HTTP/2 friendliness).
    - Supports auth (token, mTLS) and scoped authorization by crate namespace.
  - A mirroring mode:
    - Pull-through cache for crates.io (or any upstream) with integrity verification.
    - Periodic snapshotting (“freeze a point in time”) with signed snapshot manifests.
  - An operator-grade UX:
    - `registry doctor` checks index integrity, missing blobs, hash mismatches, and cache hit ratios.
    - Metrics + tracing for request patterns (index hot spots, parallelism).
  - A compatibility suite:
    - Black-box tests that run `cargo` against the server and assert expected requests and correctness.
    - Golden fixtures for index path layout and `config.json` behavior.
  - Artifact format:
    - `*.registrycapsule.zip`: a snapshot manifest + selected index shards + crate tarballs sufficient to reproduce a build offline.
mvp_plan:
  - MVP (4–6 weeks):
    - Read-only sparse index server + download endpoint proxy + minimal auth.
    - Compatibility runner that executes scripted Cargo interactions and verifies responses.
  - v1 (2–4 months):
    - Mirroring + snapshotting; signed manifests; admin UI/CLI; hardening and rate limits.
design_notes:
  - Make protocol compliance testable:
    - Treat Cargo as the “client oracle”; capture request traces and diff them between versions.
  - Optimize for **operational safety**:
    - Safe defaults for cache eviction, integrity checks, and atomic snapshot publish.
  - Keep format-neutral:
    - Works for both git-based and sparse upstreams, but prioritizes sparse for performance.
testing_conformance:
  - CI matrix across Cargo versions (stable/beta/nightly).
  - Deterministic fixture repos + offline build verification.
  - Negative tests: corrupted crate tarball, bad index entry, stale cache headers.
adoption_path:
  - Start with “local mirror for CI” usage; expand to org-wide internal registry.
  - Publish a “how to migrate from git index to sparse” playbook.
---

(Proposal details are encoded in the YAML front matter for machine-checkable indexing.)
