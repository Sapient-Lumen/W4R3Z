# Design: Release Truth execution blueprint 2026Q1

## Why this note exists now
The archive already had the right ingredients for **Release Truth**:
- `design/release-truth-stack.md`
- `design/release-truth-pilot-program.md`
- `design/release-pipeline-kit.md`
- `design/release-pipeline-pilot-program.md`
- `design/signed-binaries-kit.md`
- `design/repro-build-kit.md`
- `design/inventory-evidence-stack.md`
- `proposals/epic-release-truth-stack.md`

What it still lacked was the same thing Build-State Evidence, Feedback Loop, Async Capability Commons, Safety-Critical Readiness Commons, Cargo Artifact Contract, Distribution Contract, Workspace Environment, Publisher & Source Identity, Reviewable Edit, Toolchain Productization, Support Envelope, Canonical Learning, Public API, Benchmark Evidence, Defect Escalation, and Observability now have:

> one direct answer to **what the worthy contribution should actually ship in theory and practice**.

That absence matters because the current ecosystem pressure is no longer only “release tooling exists” or “automate publishing better”.
It is that serious Rust teams increasingly need to answer **what exact source package was published, which binary artifacts belong to that same release subject, what signature or attestation facts exist, what rebuild and inventory evidence attaches, what producer-side uncertainty remains, and what downstream distribution/policy/incident consumers may honestly conclude**.

The archive should therefore stop treating Release Truth as only a stack note and pilot ladder.
It should describe a real contribution shape.

## Fresh signals that force the seam into focus
Primary sources now line up around the same missing middle:
- Cargo’s `cargo package` command makes package publication a concrete curated boundary: it rewrites the manifest, removes `[patch]`, `[replace]`, and `[workspace]`, includes `Cargo.lock` by default, and verifies the packaged crate can be built. That is a strong source-publication substrate, but not yet a full release story.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- Cargo’s publishing model remains permanent and package-oriented. Once uploaded to crates.io, a version cannot be overwritten, which raises the value of precise release-subject and evidence attachment discipline.
  https://doc.rust-lang.org/cargo/reference/publishing.html
  https://doc.rust-lang.org/cargo/commands/cargo-publish.html
- crates.io’s January 2026 update added GitLab CI/CD Trusted Publishing, a Trusted-Publishing-only mode, and blocked the risky `pull_request_target` and `workflow_run` GitHub Actions triggers. That is concrete progress on publish authority and source-route hardening, but it still does not unify broader release evidence.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo’s unstable SBOM support generates precursor JSON files for compiled artifacts and says those files are produced for executable and linkable outputs uplifted into target or artifact directories. That is exactly the kind of attached evidence a release-native boundary should carry without flattening.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Rust’s 2026 flagship slate still keeps **SBOM support** and **public/private dependencies** in the active supply-chain band. That means “what exactly shipped?” remains an officially live ecosystem concern rather than a niche release-engineering hobby.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- `cargo-dist` now exposes a machine-readable `DistManifest` with releases, artifacts, assets, upload files, linkage information, and GitHub artifact-attestation posture. That proves the artifact side is real enough to import rather than reinvent.
  https://docs.rs/cargo-dist-schema/latest/cargo_dist_schema/struct.DistManifest.html
- `release-plz` keeps automating changelog generation, GitHub/Gitea/GitLab releases, publishing to cargo registries, and version bumps in `Cargo.toml`. That proves release orchestration is well-populated; the missing piece is the portable producer-side evidence layer above it.
  https://github.com/release-plz/release-plz/blob/main/README.md
- `cargo-binstall` documents limited signature support, `--only-signed`, and explicit signature-skipping switches. That proves signed-install truth exists as an attachable lane, but not yet as the whole release verdict.
  https://github.com/cargo-bins/cargo-binstall

Taken together, those signals say the missing contribution is not another release bot and not a one-number provenance badge.
It is a **reviewable producer-side release layer**.

## Headline answer
If one serious team wants to build the archive’s clearest remaining producer-side release contribution, the answer should now be:

> Build a **Release Truth reference layer** that captures release-subject identity across source publication, artifact publication, signatures/attestations, rebuild evidence, inventory attachments, and bounded downstream handoffs; emit reusable reports and packs; and prove the shape across crate-only releases, source+binary releases, signed/downloadable releases, rebuild-attached releases, and downstream policy/distribution imports.

That answer is deliberately narrower than “solve supply chain security for Rust”.
It is also deliberately stronger than “make release-plz or cargo-dist nicer”.

## What this contribution should be in theory

### Core thesis
A release-truth system becomes real ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what exact release subject is under discussion** — package or package set, version, tag, commit, registry path, and intended release identity;
2. **what source-publication facts exist** — packaged payload, checks, waivers, and upload/index receipts;
3. **what artifact facts exist** — downloadable archives/installers/assets, target and linkage posture, and attachment provenance;
4. **what stronger evidence exists** — signatures, attestations, rebuild comparisons, inventory attachments, and where each stops;
5. **what bounded the claim** — generator versions, toolchains, registry routes, waiver posture, dry-run versus final-release status, and unsupported residue;
6. **what downstream consumers may honestly conclude** — distribution, policy, incident, support, assistant, and archive consumers should be able to import selected facts without silently promoting them into installed-state or runtime claims.

If a project cannot answer those questions without combining crates.io pages, Git tags, CI logs, GitHub Releases, checksum files, signature docs, SBOM precursors, and maintainer memory by hand, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable producer-side release truth and handoff**.

It should include:
- release-subject identity;
- source-publication truth;
- artifact attachment truth;
- signature/attestation truth;
- rebuild and inventory imports;
- consumer exports and redactions.

It should not become:
- the new universal installer or updater;
- a hosted release portal mistaken for the authoritative record;
- a single provenance score;
- or a policy engine that silently turns evidence into compliance verdicts.

### Separation rule
A worthy contribution here must preserve at least six distinct truth classes:
- **release-subject truth** — which release and comparison the record describes;
- **source-publication truth** — what package payload was published and under what authority/receipt posture;
- **artifact truth** — what downloadable or attachable artifacts belong to the release;
- **signature/attestation truth** — what was signed or attested, by whom, and with what verification outcome;
- **rebuild/inventory truth** — what independent rebuild or inventory evidence attaches and how bounded it is;
- **consumer-handoff truth** — what later consumers may import and what they must not over-claim.

Without that separation, one crates.io upload, one dist manifest, one signature file, one SBOM precursor, or one rebuild report silently becomes the whole release story.

### Shape rule
The primary contribution shape should now be:
- **reference layer + report/pack command + attachment/import corpus**.

Why this shape fits:
- **reference layer** because the seam is really about release identity, evidence vocabulary, and non-collapse rules;
- **report/pack command** because the missing piece is a portable output that teams can diff, publish, attach to releases, and import elsewhere;
- **attachment/import corpus** because the hard cases are exactly the ones where package, artifact, signature, rebuild, and inventory lanes diverge and need reviewable comparison.

Wrong shapes to refuse first:
- one more GitHub Action without portable handoff;
- one “verified release” badge;
- a publish-time gate that hides which evidence was or was not imported;
- or an assistant-facing release summary that cannot point back to source evidence.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo releasetruth collect`
- `cargo releasetruth verify`
- `cargo releasetruth diff`
- `cargo releasetruth handoff --to <distribution|policy|incident|support|assistant|archive>`
- `cargo releasetruth pack`
- `cargo releasetruth doctor`

The tool should **import** Cargo packaging/publishing facts, dist manifests, signature verification facts, rebuild packs, and inventory packs where possible rather than replacing them.

### Public artifact spine
A credible public artifact family would keep the current stack ideas but make the review spine explicit:
- `release-truth-subject/v0`
- `release-truth-register/v0`
- `release-truth-diff/v0`
- `release-truth-verification-report/v0`
- `release-truth-handoff/v0`
- `release-truth-pack/v0`

The pack should import, not replace:
- `publish-pack/v0` or equivalent package-publication outputs;
- `release-pack/v0` where broader release-pipeline truth already exists;
- `binpack/v0` / `binverify-report/v0` for signed-binary truth;
- `repro-pack/v0` for independent rebuild truth;
- SBOM or inventory evidence packs;
- artifact-manifest inputs such as cargo-dist’s `DistManifest`.

### First proving lanes
A credible rollout should rank proving lanes instead of attempting a universal release platform on day one.

#### 1) Crate-only publish continuity lane
Prove that one pack can bind package subject, packaged payload, publish receipts, and bounded evidence attachments without any binary complexity.

Why first:
- it is the smallest durable producer-side boundary;
- it works for ordinary libraries;
- it forces source-publication truth to stay explicit.

#### 2) Source + binary coherence lane
Prove that one release subject can bind `.crate` publication and downloadable binary artifacts without pretending they are the same thing.

Why second:
- this is the most common release split in real Rust projects;
- it tests tag/version/artifact attachment discipline early;
- it proves release truth is more than registry truth.

#### 3) Signed/attested artifact lane
Prove that issuer, verification, and attestation posture can attach cleanly without becoming the whole release status.

Why third:
- it matches real consumer expectations for installable binaries;
- it forces the design to preserve verification reasons instead of flattening them;
- it keeps signature truth separate from rebuild truth.

#### 4) Rebuild + inventory attachment lane
Prove that rebuild verdicts and inventory/SBOM attachments can travel with the release without silently redefining it.

Why fourth:
- it is strategically valuable but easy to overclaim;
- it forces the stack to model incompleteness honestly;
- it proves the release boundary can carry serious evidence without becoming a fake universal supply-chain platform.

#### 5) Distribution/policy/incident handoff lane
Prove that downstream consumers can import the producer boundary without re-scraping CI or silently treating publication as installation.

Why fifth:
- this is where the stack becomes ecosystem infrastructure;
- it validates the handoff boundary with adjacent seams;
- it keeps release truth below install/update/runtime claims.

## Strategic boundaries with adjacent seams
This blueprint is intentionally close to other strong archive seams, but it is not them.

### Not Distribution Contract
Distribution Contract owns acquisition, route ordering, fallback, verification-at-install, and installed ownership.
Release Truth stops before channel choice, fallback logic, and installed-state claims.

### Not Cargo Artifact Contract
Cargo Artifact Contract owns final-output subject/origin/sidecar truth at build time.
Release Truth imports that substrate and re-binds selected artifacts to a producer-side release subject.

### Not Publisher & Source Identity
Publisher & Source Identity owns publish authority, route, family claims, and provenance boundaries.
Release Truth imports that authority plane and attaches broader release evidence above it.

### Not Repro Build
Repro Build owns rebuild-subject identity, compare posture, and reproducibility verdicts.
Release Truth imports rebuild evidence without flattening it into signatures or publication receipts.

### Not Inventory Evidence
Inventory Evidence owns component graph / SBOM / projection continuity.
Release Truth imports those attachments without pretending they are the release itself.

## Why this counts as a worthy contribution
This would count as worthy because it would give Rust something it still does not have:
**a reviewable way to move from “we published a crate and some binaries” to “here is one bounded pack with source-publication, artifact, signature, rebuild, inventory, and handoff truth intact.”**

That is strategically large enough to matter because:
- it reduces release folklore;
- it improves producer-side review without demanding one orchestration tool winner;
- it composes with present tooling instead of replacing it;
- and it creates a clean substrate for distribution, policy, incident, and assistant consumers without letting them invent claims the publisher never made.

## Ranking impact
This does **not** reorder the top of the archive.
It sharpens one remaining high-value seam.

Interpretation:
- **Build-State Evidence** stays the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** stays the clearest under-ranked day-to-day missing middle;
- **Release Truth** now becomes the clearest execution answer for **producer-side package/artifact/signature/rebuild/inventory continuity and handoff** work;
- **Publisher & Source Identity**, **Cargo Artifact Contract**, **Distribution Contract**, **Repro Build**, and **Inventory Evidence** remain major adjacent import and consumer layers;
- and future release proposals should now prove subject, publication, artifact, signature, rebuild, inventory, and handoff truth before widening into portals, control planes, or scoreboards.
