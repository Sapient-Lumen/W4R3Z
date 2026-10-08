---
id: P-0431
title: Public Dependency Boundary Kit — manifest-intent receipts, effective-boundary verdicts, and migration bundles
status: idea
domains: [cargo, semver, api-design, dependency-management, release, devtools]
last_reviewed: 2026-03-22
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/pub-priv.html
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://rust-lang.github.io/rfcs/3516-public-private-dependencies.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html#public-dependency
  - https://doc.rust-lang.org/cargo/commands/cargo-add.html
  - https://doc.rust-lang.org/cargo/CHANGELOG.html
  - https://docs.rs/public-api/latest/public_api/
  - https://docs.rs/crate/cargo-check-external-types/latest
---

# Problem

The sharper missing value here is no longer “mark dependencies as `public = true`”.
Rust and Cargo are finally explicit enough that the ecosystem needs a **boring review layer** above the unstable feature, the compiler lint, and rustdoc-based analyzers.

Other maintainers need to know all of these separately:

1. what the manifest *declared*,
2. what the crate is *effectively* exposing today,
3. which route caused that exposure,
4. which conclusions came from Cargo/rustc versus rustdoc-based inference,
5. where current workspace / target / feature limitations still block a clean declaration,
6. and what migration would shrink accidental publicness without lying about SemVer cost.

The missing crate is therefore a **Public Dependency Boundary Kit**.
It should not be another lint wrapper, and it should not be another generic public-API diff tool.
It should be the handoff bundle that lets someone else review dependency boundary truth.

# Why this lane is hot now

Current upstream and substrate signals align unusually well:

- the 2025H2 project goal is explicitly about finding an MVP for stabilizing public/private dependencies;
- the 2026 flagships list public/private dependency stabilization as ongoing flagship work;
- Cargo’s unstable docs already support `public = true` / private-by-default and note that `workspace.dependencies` does **not** support `public`;
- `cargo add` already exposes `--public` / `--no-public` on nightly;
- recent Cargo changelogs now mention `cargo metadata` support, `cargo tree --edges public`, better manifest errors, and publish support for the `public` field;
- RFC 3516 makes clear that false negatives are preferred to false positives, that accidental exposure often comes from convenience traits and reexports, and that some `#[allow(exported_private_dependencies)]` cases remain real;
- `public_api` / `cargo-public-api` and `cargo-check-external-types` already provide real rustdoc-driven substrate for seeing what external types escape.

That means the missing contribution is not compiler internals.
It is the **reviewable support contract** above them.

# Main judgment

A worthy crate in this lane should answer all of these cleanly:

1. **Which dependencies are public in effect, not just in intent?**
2. **What exact route exposed each dependency?**
3. **Which verdicts came from manifest declarations, which from rustc/Cargo signals, and which from rustdoc-based inference?**
4. **Where do workspace inheritance, target/feature scope, or nightly-only limits block a stronger claim?**
5. **What migration path would make intent and effect line up?**

If a candidate crate cannot answer those questions, it is still mostly boundary folklore.

# Product shape

Deliver **P-0431** as:

1. a library for capture / classify / explain / diff / pack;
2. a cargo subcommand for CI, release review, and edition migration prep;
3. a compact schema family that other tools can import.

## Receiver-facing promise

Given a crate or workspace, another engineer should be able to tell:

- what the manifest intended,
- what dependencies are effectively public now,
- how they escaped,
- what evidence backs that judgment,
- where unresolved workspace/nightly/scope gaps remain,
- and what migration plan is safest.

# What it provides

- `manifest-intent.receipt.json` — direct dependency declarations, `public` settings, private-by-default facts, and any unsupported workspace inheritance situations.
- `boundary-verdict.report.json` — per-dependency verdicts such as `public_declared_and_effective`, `private_declared_but_effective_public`, `public_declared_but_not_witnessed`, `workspace_gap`, `ambiguous_scope`, and `manual_review_required`.
- `exposure-route.report.json` — why the dependency crossed the public boundary: reexport, visible signature, associated type, trait implementation, macro/proc-macro helper route, or hidden shim.
- `evidence-provenance.receipt.json` — which parts came from Cargo/rustc/lints/metadata, which from rustdoc JSON analysis, which from imported tools, and what exactness class applies.
- `workspace-gap.receipt.json` — unsupported or awkward cases around `workspace.dependencies`, feature/target scoping, or edition-migration limitations.
- `boundary-migration.plan.json` — conservative steps such as declare `public = true`, wrap the external type, split facades, reduce visibility, add allowlisted exception receipts, or defer to manual review.
- `public-dependency-drift.diff.json` — classify `effective_publicness_added`, `effective_publicness_removed`, `route_changed`, `workspace_gap_resolved`, `public_declaration_added`, `false_positive_risk_reduced`, and `manual_review_now_required`.
- `public-dependency-support-bundle.manifest.json` — compact handoff bundle joining the receipts and reports.
- `cargo pub-boundary inspect`
- `cargo pub-boundary explain <dep>`
- `cargo pub-boundary migrate`
- `cargo pub-boundary diff <old> <new>`
- `cargo pub-boundary pack`

# What the crate should provide other people

1. **Boundary truth they can review** instead of grepping manifests and error text.
2. **Effective-publicness explanations** that say *why* a dependency escaped.
3. **Evidence provenance** so rustc/Cargo facts do not get mixed with rustdoc-driven conservative inference.
4. **Workspace-gap honesty** instead of pretending unstable Cargo limitations do not exist.
5. **Migration plans** that help teams align declaration and effect without hand-waving SemVer consequences.
6. **Boundary drift artifacts** for release review and edition migration.
7. **A reusable import surface** for SemVer, public-API, and documentation tools.

# Persona / who it’s for

- maintainers of public libraries and SDKs
- release and SemVer reviewers
- workspace owners preparing for public/private dependency stabilization
- API stewards trying to reduce accidental dependency exposure
- tooling authors who need one structured boundary bundle

# Users & user stories

- **Library maintainer**: “Which dependencies are really part of my API today, and why?”
- **Reviewer**: “Is this new dependency intentionally public, accidentally public, or only public in one feature/target lane?”
- **Workspace owner**: “Which packages are blocked by `workspace.dependencies` not carrying `public`, and how should we migrate?”
- **Release engineer**: “What changed in the public dependency boundary between the last release and this branch?”
- **Edition-migration owner**: “Which `exported_private_dependencies` warnings are best solved by manifest edits versus API wrappers?”

# Prior art (and why it’s insufficient)

- **RFC 3516 / Cargo / rustc lint** define the language and compiler direction, but not a portable review bundle.
- **`public_api` / `cargo-public-api`** list and diff public items via rustdoc JSON, but do not own dependency-boundary verdicts or migration receipts.
- **`cargo-check-external-types`** is strong for allowlisting exposed external types, but it is not the same as explaining manifest intent, unstable Cargo gaps, or migration posture.
- **SemVer/public-API tools** help review public surface changes, but they do not make dependency-boundary truth itself first-class.

What remains missing is the **dependency-boundary-specific coordination artifact**.

# Design goals

1. **Boundary-first** — focus on public/private dependency truth, not all API governance.
2. **Explainability-first** — every verdict should say what evidence supports it.
3. **Migration-first** — emit plans, not just warnings.
4. **Workspace-honest** — keep unsupported inheritance and scope gaps visible.
5. **Conservative** — prefer false negatives to noisy false positives when evidence is mixed.
6. **Import-friendly** — other tools should be able to consume the receipts.

# Non-goals

- not a replacement for rustc’s `exported_private_dependencies` lint;
- not a full SemVer checker;
- not a dependency resolver overhaul;
- not a generic rustdoc JSON explorer;
- not an automatic code-rewriter for every migration.

# v0.1 implementation stance

- manifest parsing + `cargo metadata` import + rustdoc-JSON/public-API import;
- optional import of `cargo-check-external-types` style findings;
- explicit exactness classes whenever feature/target/workspace scope is partial;
- no silent autofix for boundary-changing source edits.

# Stage 1

Freeze verdict taxonomy, route taxonomy, and evidence-provenance receipts.
Do not chase resolver-side future possibilities yet.

# Stage 2

Add migration planning and drift comparison.

# Stage 3

Add richer workspace aggregation and optional edition-migration helpers.

# Adoption targets

1. public Rust libraries with broad downstream ecosystems,
2. workspace-based SDK families,
3. SemVer/release review automation,
4. edition-migration preparation for public/private dependency stabilization.

# Why this could be epic

This crate sits at a leverage point.
If public/private dependencies stabilize, many teams will need help answering “what is public *really*?” and “what do we change now?”
The winner here is likely not the deepest compiler integration.
It is the tool that makes the transition **legible, reviewable, and boring**.
