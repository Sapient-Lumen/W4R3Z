# Design: Epic contribution launch wedges and proof paths (2026 Q1)

## Goal
The archive can already rank worthy Rust contributions, describe their operating surfaces, place them in honest homes, keep hot truth separate from canon, and maintain explicit present-tense claims.

What it still lacked was one explicit answer to a narrower, more practical question:

> once a contribution looks worthy in theory, what is the **first adoption wedge** that proves it deserves real energy instead of becoming another admired but unentered design folder?

This note is a **launch-wedge / first-proof / first-adopter** pass.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It exists so future revisions can say **who the first user is, what painful decision gets answered, what artifact gets carried into that moment, and what proof would show the wedge is real**.

Read with:
- `design/epic-contribution-worthy-repo-buildout-2026Q1.md`
- `design/epic-contribution-operating-surface-2026Q1.md`
- `design/epic-contribution-stewardship-and-graduation-map-2026Q1.md`
- `design/epic-contribution-portfolio-control-loop-2026Q1.md`
- `design/portfolio-hypothesis-ledger-2026Q1.md`
- `meta/LAUNCH_WEDGE_PROTOCOL.md`
- `ledgers/portfolio-launch-wedges-v0/wedges.json`

## Why this pass is needed now
The latest official Rust signals still point toward **painful repeated decisions** and **substrate imports**, not toward one giant framework that wins by announcement.

Signals that matter here:
- The 2025 State of Rust survey still says resource usage remains one of the most common productivity limits, debugging remains a live pain point, and online docs remain canonical even as editor- and LLM-mediated learning rises. That is a strong sign that a worthy contribution must prove itself inside real workflows quickly rather than relying on ambient enthusiasm.  
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The March 2026 challenges post still concentrates pain around async confusion, crate choice and trust, embedded constraints, safety-critical tooling maturity, and GUI compile-loop tax. That is a “what is the first decision we can actually improve?” signal, not a “name one mega-platform” signal.  
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- Cargo build analysis is still explicitly a prototype around recorded build metadata and unstable `cargo report` subcommands. That supports a narrow first wedge around build triage and review receipts rather than a broad build-control plane.  
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The March 2026 build-dir-layout-v2 testing call says many projects still rely on unspecified internals because Cargo features are missing. That argues that a first wedge must work by **importing bounded facts and preserving unknowns**, not by leaning on unstable archaeology as if it were a contract.  
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo’s external-tools guidance still recommends driving Cargo via the CLI and `cargo metadata` rather than treating Cargo-as-a-library as stable. The `cargo clippy` model still shows that optional toolchain-distributed external commands can be real without pretending everything belongs in Cargo core.  
  https://doc.rust-lang.org/cargo/reference/external-tools.html  
  https://doc.rust-lang.org/cargo/commands/cargo-clippy.html
- crates.io now has a Security tab, GitLab support for Trusted Publishing, Trusted-Publishing-only mode, and blocked risky GitHub triggers. That makes package-intake work more concrete, but it still looks like a companion review wedge over service truth rather than a universal trust oracle.  
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- docs.rs still hosts rustdoc JSON with `format_version` caveats and historical-availability caveats. That reinforces a repeated lesson across the repo: machine-readable imports matter, but their caveats must travel with them into the wedge.  
  https://docs.rs/about/rustdoc-json
- The January/February 2026 Project Director update says `cargo-capslock` exists for static and runtime capability analysis, the vulnerability surfacing tab is live, and interop mapping work is continuing. That is exactly the kind of upstream/service movement a wedge should import rather than trying to subsume.  
  https://blog.rust-lang.org/inside-rust/2026/03/25/project-director-update/
- The Rust Foundation strategy and Rust Innovation Lab make the hosting picture clearer for stewardship-heavy work: some worthy contributions become real only when they have funded, governed, and maintained homes without losing technical direction.  
  https://rustfoundation.org/strategic-plan/  
  https://blog.rust-lang.org/2025/09/03/welcoming-the-rust-innovation-lab/
- The 2026 goals overview continues to frame goals as contributor-proposed, team-accepted work with identified champions and support. That is a good reminder that “worthy” does not just mean strategically attractive; it must also have a believable first entry path.  
  https://rust-lang.github.io/rust-project-goals/2026/

Taken together, the missing layer is:
**what is the first believable wedge for each strong contribution, and what proof would show that wedge is worth widening?**

## Headline answer
A worthy Rust contribution should now be described not just as a seam, kernel, or program, but also as a **launch wedge**.

A launch wedge is a compact answer to five questions:
1. **who** is the first real user;
2. **when** do they feel the pain strongly enough to try the thing;
3. **what artifact** do they carry into that moment;
4. **what proof** would show the wedge answered a real decision; and
5. **what tempting broader shape must still be refused** even if the wedge works.

The archive should now prefer **wedge-first deepening** over broadening a contribution’s ambition prematurely.

## What the wedge layer is for
Use the wedge layer when the repo needs to answer:
- what the first ten serious users would actually do with a contribution;
- what review, diagnosis, or readiness question would justify trying it;
- what minimum proving ground should count as “real enough to keep going”;
- what credible home the wedge should begin in; and
- what bigger product story should still stay out of scope even after early success.

Do **not** use the wedge layer to pretend that:
- first-adopter interest alone settles the strategic ranking;
- one successful wedge automatically justifies centralization into Cargo core or a hosted platform;
- the wedge must already satisfy every downstream use case; or
- the repo should replace design theory with growth hacking.

## The launch-wedge model
Every serious wedge card should name:
- the seam it belongs to;
- the first operator or maintainer it serves;
- the trigger moment where the pain is sharpest;
- the initial surface or artifact family it presents;
- the imports it relies on;
- the proving grounds that make the wedge honest;
- the success signals that say it helped for real;
- the anti-goals that keep it from sprawling too early; and
- the next wider move that becomes credible only **if** the wedge proves itself.

## Cross-wedge rules

### 1) A wedge must answer one painful decision within a working day
If a contribution’s v0 cannot help a real user answer one consequential question in hours rather than weeks, it is still mostly theory.

### 2) The first wedge should usually ride imports, not replace them
Use Cargo, crates.io, docs.rs, debugger tuples, and institutional program truth as bounded inputs. Do not pretend the wedge becomes the source of truth for everything it touches.

### 3) Proof beats coverage theater
A wedge should prove one repeated decision strongly rather than claim universal coverage weakly.

### 4) Adoption proof is not the same as prestige proof
“Could become official” is not an early success signal. A better early signal is that a maintainer, operator, or review lead changed what they did because the artifact was materially helpful.

### 5) Every wedge needs an anti-goal
A wedge is incomplete if it never says what larger product temptation must still be refused.

## Wedge cards for the strongest seams

### 1) Build-State Evidence
**First real user:** workspace maintainer, build engineer, or performance-minded team lead.

**Trigger moment:** “why did this rebuild, why is CI slower today, or what changed between the last good warm build and this one?”

**Best first artifact:** a local or CI-produced `build-state-pack` plus `report/diff/doctor` receipts.

**Why this wedge is strong now:** Cargo is moving toward recorded build facts and `cargo report`, but the user-facing review layer is still incomplete. The wedge can therefore be honest, useful, and companion-first.

**Minimal proving grounds:**
- one large workspace incremental rebuild diff;
- one CI cold-vs-warm comparison;
- one build-dir-layout caveat case with explicit unknowns.

**Success signal:** a team stops arguing from anecdote and starts carrying receipts into triage, perf review, or migration work.

**Refuse first:** universal build daemon, hidden cache empire, or target-dir archaeology sold as contract truth.

### 2) Package Intake + Release Boundary Review
**First real user:** crate maintainer, release owner, or dependency-admission reviewer.

**Trigger moment:** “should we publish this, should we take this dependency, and what route risks or release-boundary caveats need to be visible right now?”

**Best first artifact:** a `review/admit/quarantine/waive/recheck` kit over local package facts plus crates.io service truth.

**Why this wedge is strong now:** crates.io is adding security and trusted-publishing truth, but the maintainer-facing review layer is still fragmented. That leaves room for a real operator wedge without inventing a fake trust score.

**Minimal proving grounds:**
- one publish dry-run / package listing review path;
- one dependency-admission path with Security-tab imports;
- one Trusted-Publishing route profile with blocked-trigger posture;
- one capability-analysis import case.

**Success signal:** maintainers begin attaching explicit review receipts or waivers to publish and intake decisions.

**Refuse first:** universal crate ranking, universal safety score, or policy engine that erases waivers and context.

### 3) Feedback / Debug Acceptance Commons
**First real user:** debugger maintainer, Rust team member handling an issue, or app engineer filing a reproducible debugging complaint.

**Trigger moment:** “does this debugger tuple actually work for my scenario, and what should I export when it doesn’t?”

**Best first artifact:** tuple cards plus session export packs and unsupported-state receipts.

**Why this wedge is strong now:** official signals still describe the gap as capability coverage across debugger/version/OS/runtime tuples, not as a missing front-end brand.

**Minimal proving grounds:**
- one LLDB or GDB tuple matrix;
- one async-debug scenario;
- one roundtrip from session export into issue/support context.

**Success signal:** debugging issues become easier to reproduce, compare, and route because tuple identity and unsupported states travel with the report.

**Refuse first:** debugger fork, IDE-only magic, or green-demo marketing that ignores degraded tuples.

### 4) Safety-Critical + Institutional Readiness Commons
**First real user:** team evaluating whether Rust is acceptable for a regulated or qualification-sensitive subsystem.

**Trigger moment:** “what readiness gaps, lifecycle requirements, ownership expectations, and evidence burdens stand between us and a credible internal yes?”

**Best first artifact:** freshness-bearing readiness cards plus gap, waiver, and renewal receipts.

**Why this wedge is strong now:** the safety-critical work still looks like coordinated checklists, lifecycle playbooks, interop discipline, and durable stewardship more than one crate or tool.

**Minimal proving grounds:**
- one target/domain card family;
- one dependency lifecycle case;
- one institutional ownership / renewal handoff example.

**Success signal:** organizations begin using the cards to frame adoption, procurement, or qualification-prep conversations more honestly.

**Refuse first:** certification product theater or a fake “Rust is safety-ready” badge.

### 5) Compatibility Claims
**First real user:** release engineer, library maintainer, or reviewer deciding whether a release is compatible enough to ship.

**Trigger moment:** “what changed at the public boundary, what evidence supports the claim, and what remains unknown or waived?”

**Best first artifact:** a release-boundary claim pack with diff, witness, and waiver posture.

**Why this wedge is still secondary but real:** it is highly useful, but it compounds best after build-state and package-boundary evidence are already honest.

**Minimal proving grounds:**
- one pre-release diff path;
- one rustdoc-JSON-backed claim with explicit format caveat;
- one waiver / unsupported-state receipt.

**Success signal:** releases carry more reviewable compatibility posture and fewer hand-waved “probably semver-safe” claims.

**Refuse first:** one universal API truth source that erases lossy imports and witness-specific caveats.

### 6) Adoption Navigation + Ecosystem Atlas
**First real user:** domain newcomer or internal guide trying to choose a sane starting stack without falling into portal sprawl.

**Trigger moment:** “what conservative default should we start with for this kind of project, and what evidence backs that suggestion?”

**Best first artifact:** one conservative domain default with renewal receipts and bounded evidence links.

**Why this wedge stays constrained:** the seam is strategically important but still renewal-burden heavy. So the wedge must be extremely narrow and evidence-bearing.

**Minimal proving grounds:**
- one domain default card;
- one renewal receipt;
- one explicit stale or unsupported path.

**Success signal:** people reuse the default because it is conservative, honest, and updated, not because it looks comprehensive.

**Refuse first:** giant portal, best-of-Rust leaderboard, or generic atlas with no renewal owner.

### 7) Tooling Contract / Semantic Context
**First real user:** tool author or assistant workflow that needs structured context without compiler-internal lock-in.

**Trigger moment:** “what machine-usable context can I import safely, and where are the format/freshness boundaries?”

**Best first artifact:** a thin import kit over Cargo metadata, rustdoc JSON, and adjacent machine-readable surfaces with explicit provenance and caveats.

**Why this wedge matters:** it is an enabling substrate, not the main user-facing empire. Its success is measured by how well other wedges can import it honestly.

**Minimal proving grounds:**
- one bounded importer;
- one provenance-bearing export;
- one failure or stale-state example.

**Success signal:** other wedges become easier to build and less tempted to scrape unstable internals.

**Refuse first:** universal workspace index or magical assistant context plane that claims authority it does not have.

## What changed in the broad reading
The broad ladder is unchanged.
The new layer is **launch wedge / first proof path discipline**, not a new worthy-contribution seam.

Current interpretation:
- **Build-State Evidence** remains the strongest single-project bet and now also has the clearest first wedge.
- **Package Intake + Release Boundary Review** remains the clearest urgent operator-facing wedge.
- **Feedback / Debug Acceptance Commons** and **Safety-Critical + Institutional Readiness Commons** remain the strongest deepen lanes, but now with clearer first-adopter proofs.
- **Compatibility Claims** remains a high-value second-wave wedge that compounds over stronger evidence layers.
- **Adoption Navigation + Ecosystem Atlas** remains strategically huge but wedge-constrained by renewal burden.
- **Tooling Contract / Semantic Context** remains an enabling import substrate whose wedge is mostly judged by what it makes possible elsewhere.

## Default interpretation for future revisions
Until stronger evidence arrives:
- use the wedge layer when the question is “how does this contribution enter the world credibly?”;
- keep ranking, packet posture, stewardship home, hot substrate drift, claim-state, and launch wedge visibly separate;
- require a proving ground and an anti-goal for every serious wedge card; and
- prefer first-ten-users proof over premature universalization.
