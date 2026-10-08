
## 2026-03-25 (467) — failure-envelope / counterexample-trace pass

Sources rechecked:
- 2025 State of Rust Survey results
- Rust debugging survey 2026
- What is maintenance, anyway?
- What does it take to ship Rust in safety-critical?
- January 2026 crates.io development update
- February 2026 malicious-crate notification policy update
- March 2026 Cargo security advisory
- October 2025 docs.rs default-targets post
- docs.rs metadata / builds / download / rustdoc JSON pages
- sandboxed build scripts / cargo-semver-checks / cargo build analysis / build-dir-layout / StableMIR goal pages
- target tier policy

Main takeaway:
The archive still does **not** need a fresh umbrella frontier reset.
The sharper missing move is to plan the leading lanes around **failure envelopes**: compact counterexample traces, degraded-claim notes, withdrawn guarantees, and repair-hint slices that let another team see how a claim broke without reconstructing the whole basis.

Repository consequence:
- added a frontier failure-envelope note;
- added a falsification/counterexample doctrine note;
- added a compact top-lane falsification note;
- added a failure-envelope template;
- and added `failure-envelopes.json` as a machine-readable planning spine.

- 2026-03-25 (entry 466): combined current official signals on crate-choice friction, debugger variance, maintainer/reviewer labor, safety-critical traceability needs, docs.rs machine-usable surfaces, crates.io trust surfaces, target-tier semantics, semver-checking, build-analysis, relink-don't-rebuild, and StableMIR into one new repo conclusion: the archive now needs explicit **assurance cases** more than stronger review or verdict wording.
- Practical takeaway: a worthy crate should tell downstream teams **what is being claimed, which witnesses support it, what warrant is being used, what remains challenged, and how the new case inherits from or supersedes the old one**.

- 2026-03-25 (entry 465): combined current official signals on maintenance burden, safety-critical upgrade explainability, build-dir and docs.rs basis drift, relink-don't-rebuild, build-analysis, semver-checking, public/private boundary work, StableMIR, and alternate-registry risk into one new repo conclusion: the archive now needs explicit **delta contracts** more than stronger renewal wording.
- Practical takeaway: a worthy crate should tell downstream teams **what changed, what still carries forward, what exact slice must be rerun, and when confidence must reset**.

- 2026-03-25 (entry 464): combined current official signals on maintenance burden, safety-critical operational stability, build-dir churn, malicious-crate notification policy, alternate-registry risk, docs.rs machine-usable surfaces, and Cargo/tooling goals into one new repo conclusion: the archive now needs bounded **renewal contracts** more than another packet family.
- Practical takeaway: a worthy crate should tell downstream teams **what stays fresh, what can be cheaply rerun, what forces deeper review, and how old approvals are retired**.

## 2026-03-25 (463) — review-packet / signoff-rail refresh

Consulted sources:
- 2025 State of Rust Survey results — continued pain around debugging, resource usage, and crate choice context.
- What is maintenance, anyway? — maintenance and reviewer enablement are multiplicative and often invisible.
- crates.io development update — Trusted Publishing only mode, blocked risky triggers, SLOC, and `pubtime`.
- What does it take to ship Rust in safety-critical? — evidence, interop, upgrade explainability, and long-lived review burden matter more at higher assurance.
- Rust debugging survey 2026 — strong matrix and version burden for debugger support.
- What we heard about Rust’s challenges — safety-critical certification tooling immaturity and embedded constraints remain live concerns.
- docs.rs metadata / builds / download / rustdoc JSON — docs/build/target/API surfaces are increasingly machine-usable.
- cargo-semver-checks goal — explicit model where a default check may still allow an override path.
- public/private dependencies and open namespaces goals — clearer ownership and boundary substrate.
- cargo build analysis goal — promising future substrate, but still explicitly unstable.
- sandboxed build scripts goal — stronger pressure for reviewable capability and execution boundaries.
- StableMIR goal — more durable tooling interface for future analyzers.

Main takeaway:
The archive’s strongest current missing crates should now be described not only as evidence or policy crates, but as **review burden reducers**.
They help another human approve, archive, inherit, supersede, and revisit a decision without replaying every raw artifact from scratch.
That interpretation did not require a frontier reset, but it did require stronger doctrine around review packets, signoff ledgers, override visibility, and maintenance summaries.



## 2026-03-25 (460) — conformance-kit / promise-tier pass

Sources rechecked:
- 2025 State of Rust Survey results
- Rust debugging survey 2026
- January 2026 crates.io development update
- February 2026 malicious-crate notification policy update
- March 2026 Cargo security advisory
- March 2026 build-dir-layout testing call
- October 2025 docs.rs default-targets post
- October 2025 Rust 1.91 target-tier release notes
- January 2026 safety-critical note
- docs.rs builds / metadata / rustdoc JSON / download pages
- Cargo build-analysis / libtest JSON / public-private dependencies / open namespaces / cargo-semver-checks / StableMIR goal pages

Main takeaway:
The archive still does **not** need a fresh umbrella frontier reset.
The sharper missing move is to plan the leading lanes around **tiered support claims** with claim envelopes, raw receipts, human summaries, and named rerun loops.

Repository consequence:
- added a frontier conformance note;
- added a conformance/promise-tier doctrine note;
- added a compact top-lane conformance note;
- added a conformance-kit template;
- and added `conformance-kits.json` as a machine-readable planning spine.

## 2026-03-25 (459) — suite-topology / package-boundary pass

Sources rechecked:
- 2025 State of Rust Survey results
- March 2026 Rust challenges post
- January 2026 crates.io development update
- February 2026 malicious-crate notification policy update
- March 2026 Cargo security advisory
- docs.rs builds / metadata / rustdoc JSON / download pages
- Rust Project Goals 2026 overview
- open namespaces / public-private dependencies / Cargo build-analysis / libtest JSON goal pages
- ecosystem hubs: Are We Web Yet, Are We GUI Yet, GeoRust, and Automerge

Main takeaway:
The archive still does **not** need a fresh umbrella frontier reset.
The sharper missing move is to plan the leading lanes as **small package families** with explicit CLI/core/schema/adapter/corpus seams.

Repository consequence:
- added a frontier suite-topology note;
- added a package-topology doctrine note;
- added a compact top-lane suite note;
- added a suite-topology template;
- and added `suite-topologies.json` as a machine-readable planning spine.


## 2026-03-25 (458) — product-blueprint / acceptance-packet / state-file pass

Sources rechecked:
- 2025 State of Rust Survey results
- March 2026 Rust challenges post
- February 2026 debugging survey post
- January 2026 crates.io development update
- October 2025 docs.rs default-target change announcement
- docs.rs build, metadata, and rustdoc JSON pages
- Rust Project Goals 2026 overview/goals pages plus Cargo build-analysis work
- ecosystem hubs: Are We Web Yet, Are We GUI Yet, GeoRust, and Automerge

Main takeaway:
The archive still does **not** need a fresh umbrella frontier reset.
The more useful next move is to convert the current top lanes into **product blueprints** with explicit maturity ladders and acceptance packets.

Repository consequence:
- added a frontier product-blueprint note;
- added a compact top-lane blueprint note;
- added a release-ladder framework;
- added a product-blueprint template;
- and added `archive-state.json` as a machine-readable memory spine.

## 2026-03-25 (456) — operating-surface / scenario-corpus pass

Consulted sources:
- 2025 State of Rust survey — resource usage and debugging remain important productivity problems; online documentation remains the preferred canonical reference.
- Rust challenges (with retraction note) — recurring high-level pain remains broad, but the page itself now also reinforces the archive’s need to keep wording subordinate to evidence.
- Rust debugging survey — debugger, version, OS, async, visualizer, and expression-evaluation variance all remain material.
- crates.io development update — Security tab, Trusted Publishing, SLOC, and `pubtime` all strengthen receiver-facing operating surfaces.
- malicious-crate policy update — advisory-first notification posture strengthens the need for intake/recheck kits rather than blog-driven memory.
- Cargo advisory for CVE-2026-33056 — crates.io and alternate-registry realities remain meaningfully distinct.
- docs.rs builds / metadata / download / rustdoc JSON docs — hosted docs remain machine-usable but recipe-shaped and caveat-heavy.
- docs.rs changed default targets — target assumptions remain moving substrate.
- Cargo build analysis, libtest JSON, public/private dependencies, Rust-for-Linux, build-script sandboxing, and safety-critical reporting — all strengthen the case for explicit runners, deterministic evidence surfaces, and bounded support claims.
- community hubs (web, GUI, game dev, IDE, geospatial, local-first) — still show broad activity, reinforcing that the missing contribution is more often a control-plane seam than a whole new umbrella ecosystem.

Main takeaway:
The sharper missing crate contribution for the current frontier is no longer only a better packet family or a better continuity contract.
It is a receiver-facing **operating model** with a named **scenario corpus** that proves what the packet family and continuity contract really mean in practice.


## 2026-03-25 (455) — continuity-ring / receiver-value / claim-discipline pass

Consulted sources:
- 2025 State of Rust survey results — persistent pain remains around resource usage, debugging, async, and crate choice.
- Rust challenges post — repeats crate choice, async, compile-time, embedded, safety-critical, and GUI pain as major themes.
- Rust debugging survey 2026 — strong detail on what first-class debugging support would actually need.
- crates.io January 2026 development update — security tab, Trusted Publishing changes, SLOC, and `pubtime` make more post-adoption signals visible.
- crates.io malicious-crate policy update — strong signal/noise lesson: advisories and bounded response channels matter more than noisy narrative repetition.
- March 2026 Cargo security advisory — crates.io and alternate registries do not necessarily share the same protection story.
- Build-dir layout v2 call for testing — many tools still rely on internal Cargo details, which strengthens migration/continuity planning.
- docs.rs metadata / download / rustdoc JSON / build docs / changed default targets — strong evidence that hosted docs/build/target substrate is machine-usable but caveated.
- Cargo build-analysis, cargo-semver-checks, libtest JSON, and 2026 goals — stronger evidence for build/report, public-boundary, mirroring, SBOM precursor, cache, and target-support lanes.
- safety-critical Rust post — especially strong evidence for evidence-heavy lifecycle and target-readiness planning.
- Are We Web Yet / Are We GUI Yet / Are We Game Yet / Are We IDE Yet / GeoRust / Automerge — maturity signals showing many sectors are active enough that continuity/evidence seams beat new umbrella rewrites.

Main takeaway:
The archive’s top missing crates should now be described not only as **adoption-contract crates** but as **continuity-contract crates**.
They help another team choose, freeze, import truth, recheck later, explain drift, survive mirror/source differences, and exit cleanly if needed.
That interpretation did not require a frontier reset, but it did require a clearer continuity ring and a stricter claim-upgrade discipline.

## 2026-03-25 (454) — adoption-contract / MVP-stack / source-basis pass

Consulted sources:
- 2025 State of Rust survey results — persistent pain remains around resource usage, debugging, and general productivity limits.
- Rust challenges post — cross-domain challenges such as compilation performance remain broadly felt.
- Rust debugging survey 2026 — strong detail on what first-class debugging support would actually need.
- crates.io development update — security tab, Trusted Publishing enhancements, and more visible trust posture.
- crates.io malicious crate policy update — clearer signal/noise lesson for security incident communication.
- docs.rs builds / rustdoc JSON / download / changed default targets — strong evidence that docs/build/target truth is increasingly machine-usable, but still caveated.
- Cargo build analysis goal — stronger evidence that iteration/build-report substrate is becoming real but remains emerging.
- cargo-semver-checks goal — stronger evidence that public-boundary and compatibility work is becoming more operational and witness-based.
- async parity / Rust for Linux / seamless Rust-C++ / standard-library contracts / libtest JSON goals — strong evidence that harder domains still need explicit support, tooling, and contract surfaces.
- safety-critical Rust post — especially strong evidence for lifecycle, target-readiness, interop, and bounded dependency posture.
- Are We Web Yet / Are We GUI Yet / Are We Game Yet / GeoRust / Automerge — maturity signals showing many sectors are active enough that seam kits beat new umbrellas.

Main takeaway:
The archive’s top missing crates should now be described primarily as **adoption-contract crates**:
they help other teams choose, freeze, explain, support, and revisit crate decisions with less lore.
That interpretation did not require a frontier reset, but it did require stronger MVP planning and stronger source-basis hygiene.

## 2026-03-25 (453) — delivery-card / need-vs-buildability refresh

Consulted sources:
- Rust challenges and 2025 survey results
- crates.io January 2026 development update and February 2026 malicious-crate notification policy update
- Rust debugging survey 2026
- docs.rs build, rustdoc JSON, download, and rebuild-queue docs
- Cargo plumbing, build-analysis, build-dir-layout, and cargo-semver-checks goal pages
- docs.rs default-target change announcement
- sector hubs: Are We Web Yet, Are We GUI Yet, Are We Game Yet, Are We Learning Yet, GeoRust, Automerge, and Embedded “not yet awesome”
- safety-critical Rust article plus C++ interop and Rust-for-Linux goal material

Main takeaway:
The strongest missing crates are still mostly **receiver-facing control planes and evidence kits**.
What changed this pass is that current official substrate now makes some of them more buildable than others.
That supports a clearer split between:
- **front door:** P-0509 + P-0536
- **ground-truth ring:** P-0472 + P-0484 + P-0535
- **next semantic / support ring:** P-0486, P-0537, P-0538

Repository consequence:
- added a need-vs-buildability matrix;
- added delivery cards for the leading lanes;
- added pass-operating rules and templates so future revisions keep emitting buildable planning artifacts.

## 2026-03-25 (452) — wide ecosystem rescan still favors horizontal control-plane and seam-kit proposals

Sources rechecked:
- Rust challenges and 2025 survey
- 2026 flagships / project goals
- Cargo plumbing, Cargo build-analysis, Cargo build cache / build-std surfaces
- docs.rs builds / rustdoc JSON / download / queue
- crates.io development and malicious-crate notification updates
- maturity/community hubs across web, GUI, game, learning, embedded, geospatial, and local-first work
- safety-critical, C++ interop, and Rust-for-Linux goal material

Synthesis:
- the broad scan still points to crate choice, debugging, resource/build friction, supply-chain visibility, target/support truth, and “building block” substrate work as strong missing seams;
- mature sector hubs reduce the case for giant new umbrella crates and strengthen the case for interop/evidence/transition kits instead;
- this promoted **P-0536** as the clearer memory plane beside **P-0509**, nudged **P-0537** and **P-0431** upward, and strengthened the archive’s anti-mega-lane discipline.

Files added from this synthesis:
- `meta/missing-crate-territory-map-2026-03-25.md`
- `meta/epic-crate-worthiness-framework-2026-03-25.md`
- `meta/archive-amnesia-resistance-2026-03-25.md`

## 2026-03-24 (451) — front-door refresh around evidence gaps and bounded closure campaigns

Sources rechecked:
- Rust challenges (crate choice, uneven domain maturity)
- 2025 State of Rust survey (resource/debug pain, docs as canonical reference)
- 2026 flagships (supply chain, SBOM, safety-critical, async, cargo plumbing)
- Cargo plumbing and Cargo build-analysis goals
- docs.rs builds / metadata / rustdoc JSON / download / queue
- crates.io development update (`Security` tab, Trusted Publishing, `pubtime`)
- Cargo Vet commands/config/wildcard audits
- cargo-deny common options

New synthesis:
- the front-door stack is now strong enough that the sharper missing layer is not “another ranking” but a bounded answer to how missing proof gets closed;
- official Rust substrate now exposes enough structured routes that a worthy crate can name campaign items instead of hiding behind generic manual-review language;
- the repo should explicitly separate gap extraction, campaign planning, and closure receipts.

Artifacts added this pass:
- `evidence-gap.report`
- `evidence-campaign.plan`
- `gap-closure.receipt`

## 2026-03-24 (450) — front-door refresh around decision programs and stage progression

Consulted sources:
- Rust challenges — users still struggle with crate choice/trust and some domains remain immature.
- 2025 State of Rust survey results — resource usage and debugging remain live pain points while online docs remain the canonical reference.
- Rust in 2026 / flagships — 2026 priorities still emphasize supply-chain work, safety-critical evidence, SBOM, Wasm Components, async, and cargo plumbing.
- Prototype a new set of Cargo plumbing commands — Cargo explicitly frames build work as staged programmatic phases.
- Prototype Cargo build analysis — Cargo is explicitly moving toward persisted machine-readable build data across invocations.
- docs.rs builds / metadata / rustdoc JSON / download — hosted docs posture, custom build knobs, versioned JSON, and offline caveats can be imported as stage inputs rather than treated as the whole answer.
- crates.io development update — `pubtime`, Security tab, and Trusted Publishing improve visible trust/timing posture without settling stage fitness.
- Cargo Vet configuration / commands / audit criteria — criteria, policies, exemptions, and renewals already act like stage gates and bounded relief.
- cargo-deny config / offline behavior — target-scoped graphs and offline caveats already act like stage constraints.
- safety-critical Rust — explicitly describes staged narrowing, wrapping, and replace-later dependency patterns.

Main takeaway:
The sharper missing crate contribution for the front-door stack is no longer only compare / freeze / profile / adjudicate truth.
It is a receiver-facing support bundle for **decision programs**: stable stages, stage-entry requirements, inherited basis rules, progression reports, and explicit exit statuses such as keep / conditional keep / hold / split-boundary / replace-later.

## 2026-03-24 (449) — front-door refresh around policy profiles and evidence floors

Consulted sources:
- Rust challenges — users still struggle with crate choice/trust and some domains remain immature.
- 2025 State of Rust survey results — resource usage and debugging remain live pain points while online docs remain the canonical reference.
- Rust in 2026 / flagships — 2026 priorities still emphasize supply-chain work, safety-critical evidence, SBOM, Wasm Components, async, and cargo plumbing.
- safety-critical Rust — calls for MSRV conventions, target-readiness checklists, dependency-lifecycle playbooks, and safety-case-friendly runtime requirements.
- cargo metadata — Cargo’s machine-readable surfaces remain versioned and should be explicitly pinned.
- docs.rs rustdoc JSON — docs.rs hosts versioned rustdoc JSON with a `format_version` story.
- crates.io development update — `pubtime` and Trusted Publishing improve visible trust/timing posture without settling task fit.
- Cargo Vet configuration / audit criteria / how it works — multiple criteria sets, subtree policies, imports, and exemptions already act like profile fragments.
- cargo-deny advisory / bans / licenses config — target-scoped policy and exception structure already exist in tool-local form.

Main takeaway:
The sharper missing crate contribution for the front-door stack is no longer only compare / freeze / adjudicate / exception truth.
It is a receiver-facing support bundle for **policy profiles and evidence floors**: stable adopter profile IDs, explicit minimum evidence, profile-specific pass/conditional/manual/fail answers, and non-claims that stop “good enough for prototype” from masquerading as “good enough for every adopter.”

## 2026-03-24 (448) — front-door refresh around exceptions, expiry, and removal paths

Consulted sources:
- Rust challenges — users still struggle with crate choice/trust and some domains still lack mature support.
- Cargo build analysis goal — Cargo is explicitly moving toward persisted machine-readable build data across invocations.
- crates.io development update — Trusted Publishing Only Mode and `pubtime` create visible trust/timing inputs without settling task fit.
- docs.rs builds + metadata — docs.rs has visible sandbox/resource ceilings and configurable metadata knobs that explain partial support stories.
- Cargo Vet commands + performing audits — Cargo Vet uses exemptions, trust entries, renewals, audit backlog reduction, and notes that exemptions should usually shrink.
- cargo-deny init template — ignored advisories can include reasons and license checks support per-crate exceptions.
- cargo-semver-checks goal + API docs — publish-time overrides are part of the intended future story, and witness generation is a first-class concept.
- safety-critical Rust — higher-integrity teams often internalize, replace, or wrap dependencies later and need managed upgrade/dependency evidence.

Main takeaway:
The sharper missing crate contribution for the front-door stack is no longer only compare / freeze / intake / adjudicate truth.
It is a receiver-facing support bundle for **temporary exception discipline**: owner, scope, rationale, witness/evidence refs, expiry, removal path, and renewal/transition tickets.

## 2026-03-24 (447) — adjudication workbench and carry-forward discipline

### Key takeaways
- The archive’s sharper missing layer is now **adjudication**, not more packet families.
- Current Cargo/docs.rs/crates.io substrate is machine-readable enough that worthy crates should export **adjudication sessions** and **carry-forward receipts**.
- Cargo JSON streams, registry-index records, docs.rs route families, and trusted-public surfaces can disagree in ways that must remain visible rather than silently normalized.
- The repo itself benefits from mirroring the same discipline through a disagreement ledger.

### Sources consulted
- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Prototype a new set of Cargo plumbing commands — https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Prototype Cargo build analysis — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- cargo metadata — https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo external tools — https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo registry index — https://doc.rust-lang.org/cargo/reference/registry-index.html
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- docs.rs download archives — https://docs.rs/about/download
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

## 2026-03-24 (446) — packet consumers, intake/materialization, and session receipts

### Key takeaways
- The archive’s sharper missing layer is now **consumer-side packet discipline**, not another broad frontier expansion.
- Cargo / docs.rs / crates.io surfaces are now structured enough that worthy crates should publish **intake receipts** and **materialization plans**, not just producer-side packets.
- `cargo metadata`, registry-index records, docs.rs rustdoc JSON, docs.rs download archives, and `.cargo_vcs_info.json` all come with route/compatibility/provenance caveats that downstream consumers must preserve.
- The repo itself benefits from mirroring the same discipline through a lightweight session-receipt model that records baseline, sources, deltas, and non-actions.

### Sources consulted
- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Prototype a new set of Cargo plumbing commands — https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Prototype Cargo build analysis — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- cargo metadata — https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo external tools — https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo registry index — https://doc.rust-lang.org/cargo/reference/registry-index.html
- cargo package — https://doc.rust-lang.org/cargo/commands/cargo-package.html
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- docs.rs download archives — https://docs.rs/about/download
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Secure quorum-based cryptographic verification and mirroring for crates.io — https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html

## 2026-03-23 (445) — new research takeaways

- Current Rust signals still point to crate choice, trust, debugging, build/docs/support drift, and hard-domain evidence as live ecosystem bottlenecks.
- The sharper missing repo move was **not** another rerank or sector expansion, but a real answer to when frozen decisions are reopened.
- crates.io `pubtime`, Security-tab trust surfaces, and the lower-noise malicious-crate notification policy make local recheck discipline more important than before.
- docs.rs build rules, target/default-target behavior, metadata controls, and rustdoc JSON make hosted support drift concrete enough to drive typed recheck tickets.
- Cargo build-analysis and plumbing work strengthen the case for packet ops: a worthy crate can now stand on local historical and versioned machine surfaces instead of vague “monitoring”.
- New practical distinction locked in: trigger intake vs recheck ticket vs revalidation vs transition posture.

### Sources consulted
- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io malicious crate update — https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Security advisory for Cargo — https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Prototype a new set of Cargo plumbing commands — https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Prototype Cargo build analysis — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Call for Testing: Build Dir Layout v2 — https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- cargo metadata — https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo external tools — https://doc.rust-lang.org/cargo/reference/external-tools.html
- cargo package — https://doc.rust-lang.org/cargo/commands/cargo-package.html
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json

## 2026-03-23 (444) — new research takeaways

- Current Rust signals still point to crate choice, trust, domain maturity, and async/build/debug pain as live ecosystem bottlenecks.
- The most useful additional repo move was **not** another wide frontier expansion, but deeper planning for what happens after a team freezes a crate choice.
- Safety-critical evidence and newer Cargo/crates.io machine surfaces make **P-0535 Dependency Lifecycle Transition Kit** look more implementation-ready than before.
- New practical distinction locked in: comparator packet vs frozen basis vs refresh/revalidation packet vs transition packet.
- Repo hygiene consequence: later passes should append revalidation / transition artifacts rather than silently rewriting frozen answers.

## 2026-03-24 (443) — basis witnesses, first-usable release contracts, and replayable basis locks

### Key takeaways
- The archive now needs a clearer answer to what **evidence-bearing basis** supports the leading packets, not just what packet family they emit.
- Current official Rust substrate is now rich enough to justify a concrete **basis witness stack**: `cargo metadata`, Cargo JSON messages, docs.rs rustdoc JSON and metadata, registry index entries, and `cargo package` / `.cargo_vcs_info.json`.
- A worthy top-lane `0.1` should be judged by a **first usable release contract**: receiver, repeated workflow, packet family, basis/replay story, and refusal boundary.
- This strengthens the practical pairing of **P-0509 + P-0536** and makes basis locks a reusable pattern for later debug, source-parity, and parity-doctor lanes.

### Sources consulted
- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Prototype a new set of Cargo plumbing commands — https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Prototype Cargo build analysis — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Finish the libtest JSON output experiment — https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- Call for Testing: Build Dir Layout v2 — https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- cargo metadata — https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo external tools — https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo registries — https://doc.rust-lang.org/cargo/reference/registries.html
- Cargo registry index — https://doc.rust-lang.org/cargo/reference/registry-index.html
- Cargo registry web API — https://doc.rust-lang.org/cargo/reference/registry-web-api.html
- cargo package — https://doc.rust-lang.org/cargo/commands/cargo-package.html
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- What does it take to ship Rust in safety-critical? — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

## 2026-03-24 (442) — front-door stack, packet-family discipline, and crate-knowledge review bundles

### Key takeaways
- The archive now needs a cleaner answer to how **P-0509 Pathfinder** and **P-0536 Crate Knowledge Pack** work together as one practical front door.
- Current official Rust substrate makes **schema discipline** more important: Cargo plumbing, build-analysis, rustdoc JSON, docs.rs metadata/build rules, and libtest JSON all point toward machine-readable packet families that need explicit evolution plans.
- A worthy knowledge-pack first release should export a compact **review bundle**, not just a generic machine-readable export.
- This reinforces the practical build order of **pathfinder + knowledge-pack first**, then debuggability, then restricted-delivery/docs-build/support-truth lanes.

### Sources consulted
- Rust project goals overview — https://rust-lang.github.io/rust-project-goals/2026/
- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Prototype a new set of Cargo plumbing commands — https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Prototype Cargo build analysis — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Finish the libtest JSON output experiment — https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo source replacement — https://doc.rust-lang.org/cargo/reference/source-replacement.html
- cargo vendor — https://doc.rust-lang.org/cargo/commands/cargo-vendor.html
- Cargo registries — https://doc.rust-lang.org/cargo/reference/registries.html
- Secure quorum-based cryptographic verification and mirroring for crates.io — https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html

## 2026-03-24 (441) — receiver personas, first-adopter programs, and restricted-delivery evidence

### Key takeaways
- The archive now needs a sharper answer to **who** top crates serve, not just what abstractions or packets they expose.
- A worthy crate should survive a **first-adopter program** test: cohort, repeated task, packet family, success/failure, and non-claim.
- Restricted-delivery truth looks more urgent again because mirror verification, trusted publishing, `pubtime`, build-dir churn, and hard-domain adoption all sharpen the need for one honest workspace-local source-parity bundle.
- This makes **P-0496 Cargo Vendor & Source Parity Kit** worth promoting back into the practical core.

### Sources consulted
- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Rust Vision Doc goal — https://rust-lang.github.io/rust-project-goals/2025h1/rust-vision-doc.html
- Rust 2024/vision general notes on picking crates — https://rust-lang.github.io/rust-project-goals/2024h2/notes.html
- Prototype Cargo build analysis — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Call for Testing: Build Dir Layout v2 — https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- What does it take to ship Rust in safety-critical? — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Security advisory for Cargo — https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- Secure quorum-based cryptographic verification and mirroring for crates.io — https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
- Program management update — January 2026 — https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/

## 2026-03-24 (440) — supportive surfaces, first-release bundles, and hard-domain ladders

### Key takeaways
- The archive now needs a stronger answer to what a worthy crate provides **other people**, not just what abstractions it exposes.
- Current Rust signals support a stronger **supportive-surface** framing: orientation, evidence, review, machine, and drift/refusal surfaces.
- Pathfinder and knowledge-pack work now belong closer together in the practical build queue.
- Hard domains should be described with an **adoption ladder**, not a yes/no support badge.
- Sector variety still matters, but the next useful widening move is scenario packs for hard domains rather than a fresh frontier explosion.

### Sources consulted
- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- What do people love about Rust? — https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Prototype Cargo build analysis — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Continue resolving `cargo-semver-checks` blockers for merging into cargo — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- Rework Cargo Build Dir Layout — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- safety-critical Rust write-up — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

## 2026-03-23 (439) — sector atlas, pathfinder scenario packs, and receiver-value bar

### Key takeaways
- A wider sector scan still points back to the same top control-plane crates.
- The current archive needs stronger **pathfinder packaging** more than it needs more top-level proposals.
- The best way to keep variety without repo sprawl is to treat sector themes as a **watchlist** until they export a distinct evidence seam.
- A worthy crate contribution should now be judged by the receiver-facing packets it gives adopters, maintainers, reviewers, operators, or tooling.

### Sources consulted
- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Prototype Cargo build analysis — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Rework Cargo Build Dir Layout — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Call for Testing: Build Dir Layout v2 — https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- build-std — https://rust-lang.github.io/rust-project-goals/2025h1/build-std.html
- Continue resolving `cargo-semver-checks` blockers for merging into cargo — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- docs.rs changed default targets — https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- safety-critical Rust write-up — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

## 2026-03-23 (438) — applied scorecard pass, concurrency scenario-lab planning, and freshness discipline

### Key takeaways
- Applying the epic-crate bar did not overturn the repo: control-plane crates still dominate the frontier.
- Pathfinder and debuggability still lead the practical queue.
- Concurrency support moves back into the top salience cluster because async remains a current official ecosystem pain.
- Build/docs/native seams remain ahead in immediate shipability because Cargo and docs.rs now expose very concrete current substrate.
- The archive now needs an explicit freshness policy so future broad passes do not conflate volatile signals with evergreen docs or flatten salience into shipability.

### Sources consulted
- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Prototype Cargo build analysis — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Call for Testing: Build Dir Layout v2 — https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo build scripts reference — https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo FAQ — https://doc.rust-lang.org/cargo/faq.html
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io malicious crate update — https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Security advisory for Cargo — https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- safety-critical Rust write-up — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

## 2026-03-23 (437) research delta

This pass emphasized the current sources that sharpen the native-build and delivery-card story:
- 2025 State of Rust survey results
- Rust debugging survey 2026
- Rust in 2026 / flagships
- Call for Testing: Build Dir Layout v2
- Cargo build scripts reference
- Cargo FAQ on unexpected rebuilds
- Cargo release notes around `OUT_DIR` build-time behavior
- docs.rs builds / metadata / rustdoc JSON / about
- crates.io development update
- crates.io malicious crate policy update
- safety-critical Rust write-up
- `system-deps` docs and standardization discussion
- `vcpkg` docs

Main effect on the repo: add delivery cards for top-ranked crates and treat buildscript/native-deps support as the next practical adoption-amplifier stack after docs.rs parity and build-dir transition.


## 2026-03-23 (436) research delta

This pass emphasized current official sources that sharpened the product-planning story for horizontal crates:
- 2025 State of Rust survey results
- Rust debugging survey 2026
- crates.io development update
- crates.io malicious crate policy update
- Rust challenges
- Rust in 2026 / flagships
- Prototype Cargo build analysis
- Rework Cargo Build Dir Layout
- Call for Testing: Build Dir Layout v2
- docs.rs builds / metadata / rustdoc JSON / about
- safety-critical Rust write-up

Main effect on the repo: promote docs.rs parity and build-dir transition from “interesting” to “implementation-ready enough to deserve concrete product-plan refinement”.

## 2026-03-23 (435) — demand-matrix and implementation-planning pass for the top control-plane crates

### Key takeaways
- The archive now needs more **implementation-ready product planning** for the top frontier, not just more idea accumulation.
- Current official Rust signals span async, building blocks, safety-critical, Wasm Components, C++ interop, Rust for Linux, and specification upkeep, which means the strongest missing crates must survive a very wide demand map.
- That breadth strengthens shared control-plane lanes more than it strengthens most new niche sector proposals.
- The next sharp repo work is therefore a cross-domain demand matrix plus concrete product plans for **P-0509** and **P-0486**.

### Sources consulted
- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- async parity goal — https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- C++ interop goal — https://rust-lang.github.io/rust-project-goals/2025h1/seamless-rust-cpp.html
- Rust for Linux tooling goal — https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- Cargo build analysis — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo build-dir layout — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Relink-don't-rebuild — https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- build-std — https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
- libtest JSON — https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- reference expansion — https://rust-lang.github.io/rust-project-goals/2025h2/reference-expansion.html
- FLS upkeep capabilities — https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- docs.rs default targets change — https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io malicious crate policy update — https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Rust compiler performance survey 2025 results — https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Faster linking with stable LLD — https://blog.rust-lang.org/2025/09/01/rust-lld-on-1.90.0-stable/
- safety-critical Rust write-up — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Adopting the FLS — https://blog.rust-lang.org/2025/03/26/adopting-the-fls/

## 2026-03-23 (434) — territory-map rerank, debuggability promotion, and archive-operator hygiene

### Key takeaways
- The archive needed explicit bands so it can preserve extreme variety without losing salience discipline.
- Compile/iteration, crate choice, dependency transition, machine-usable knowledge, concurrency semantics, debuggability, target/toolchain truth, and stewardship still form the strongest control-plane frontier.
- Debugging now has enough current official pain signal to be promoted into that frontier.
- docs.rs and crates.io continue to improve, but their surfaces still do not replace receiver-facing support contracts or decision bundles.
- The March 2026 Rust challenges retraction note is a practical reminder that this archive should stay concise, source-grounded, and anti-handwave.

### Sources consulted
- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo build analysis — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo build-dir layout — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Relink-don't-rebuild — https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io malicious crate update — https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- safety-critical Rust write-up — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

## 2026-03-23 (433) — broad frontier rerank against current surveys, goals, docs.rs, and crates.io surfaces

### Key takeaways
- State of Rust and the compiler performance survey both keep compile/iteration pain near the center of the ecosystem problem map.
- Rust project goals now make build analysis, build-dir layout, relink-don't-rebuild, Cranelift-for-dev, build-std, sandboxed build scripts, public/private dependencies, SBOM precursor work, MC/DC, safety-critical lints, and FLS/spec upkeep part of the official near-term landscape.
- Rust challenges still name async complexity as a live pain.
- docs.rs remains constrained and target-sensitive, so knowledge-pack work must stay pinned and context-aware.
- crates.io Security-tab work improves trust surfaces, but does not remove the need for pathfinder and crate-health lanes.

### Sources consulted
- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust compiler performance survey 2025 results — https://blog.rust-lang.org/inside-rust/2026/02/06/2025-Rust-Compiler-Performance-Survey-Results/
- Rust project goals 2025h2 — https://rust-lang.github.io/rust-project-goals/2025h2/
- Rust project goals 2026 flagships — https://rust-lang.github.io/rust-project-goals/2026h1/
- Cargo build analysis — https://rust-lang.github.io/rust-project-goals/2025h2/Cargo-build-analysis.html
- Build-dir layout — https://rust-lang.github.io/rust-project-goals/2025h2/build-dir-layout.html
- Relink-don't-rebuild — https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- Production-ready Cranelift — https://rust-lang.github.io/rust-project-goals/2025h2/Production-ready-cranelift.html
- Sandboxed build scripts — https://rust-lang.github.io/rust-project-goals/2025h2/sandboxed-build-script.html
- Build-std — https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
- Rust for Linux compiler support — https://rust-lang.github.io/rust-project-goals/2025h2/rust-for-linux.html
- FLS / spec capability goal — https://rust-lang.github.io/rust-project-goals/2025h2/FLS.html
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Alpha-Omega crates.io Security tab write-up — https://alpha-omega.dev/blog/rust-security-at-a-glance-crates.io-security-tab/
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs default targets change — https://blog.rust-lang.org/2025/05/23/docsrs-default-targets/

- Chose to deepen **P-0538** with observer-cursor and observer-progress-isolation artifacts because current sources now clearly distinguish independent seen-state cursors, per-receiver lag-rebased cursors, shared work-stealing claim pools, fixed single-consumer posture, and wake-only no-cursor surfaces.
- Re-read **P-0538** and confirmed the next thin seam was not another queue wrapper or subscriber helper, but whether observers advance their own frontier and whether one observer’s slowness changes another observer’s truth.
- Updated **P-0538** so future passes stop flattening audience, claim, order, lag, and multi-observer progress into one fake “channel semantics” story.
## 2026-03-23 (431) — deepen concurrency-contract around late-joiner admission and join-start baseline

- Re-read the March 2026 Rust challenges post to confirm async complexity is still a live pain signal.
- Re-read current Tokio `broadcast`, `watch`, `Notify`, `Notified`, `mpsc`, and `oneshot` docs to isolate a support-contract gap around observer entry and start position rather than generic channel semantics.
- Chose to deepen **P-0538** with late-joiner-admission and join-start artifacts because current sources now clearly distinguish future-only subscribe, current-tail resubscribe, current-snapshot subscribe, stored-permit late waits, current-waiters-only notify, and fixed-cohort no-join surfaces.

## 2026-03-23 (429) — concurrency-contract refresh around delivery order and gap visibility

- Re-read **P-0538** and confirmed the next thin seam was not shutdown or another wrapper, but what sequence a receiver is actually promised and what it can know about missed or collapsed units.
- Refreshed evidence with the March 2026 Rust challenges post plus current Tokio `mpsc` / `broadcast` / `watch` / `Notify` docs and Crossbeam `Select` docs.
- Added `delivery-order.report`, `gap-visibility.report`, and six scenario families showing single-consumer FIFO, per-receiver FIFO with counted lag, latest-snapshot-only visibility, coalesced wake without counts, random ready-operation choice, and portable bundle separation.
- Updated **P-0538** so future passes stop flattening queue order, snapshot visibility, lag counters, and wake coalescing into one fake “ordered channel” story.

## 2026-03-23 (427) — concurrency-contract refresh around delivery audience and consumption claim

- Re-read **P-0538** and confirmed the next thin seam was not another channel implementation or actor helper.
- Refreshed evidence with the March 2026 Rust challenges post plus current Tokio `broadcast` / `watch` / `Notify` / `mpsc` / `oneshot` docs, `async-channel`, and Flume `Receiver` docs.
- Added `delivery-audience.report`, `consumption-claim.report`, and seven scenario families showing current-waiter-only notification, all-active-receiver fanout, independent watch seen-state, single-consumer `mpsc`, MPMC exclusive claim, non-broadcast cloned receivers, and one-shot transfer.
- Updated **P-0538** so future passes stop flattening many receivers, fanout, single claim, latest-state observation, and wake-only notification into one fake “channel behavior” story.

## 2026-03-23 (425) — compile-iteration coverage-scope / claim-ceiling pass

- Chose to deepen **P-0537** with coverage-scope and coverage-ceiling artifacts because current sources now clearly distinguish framework-level hot-reload branding from actual tip-crate / annotated / wrapped / preexisting-route support.
- Main supporting signals: Rust challenges (compile time remains a universal productivity tax), Dioxus (RSX / asset / Rust hotpatch split plus tip-crate limit), Subsecond (tip-crate-only plus `call` / `HotFn` boundaries), Chaud (`#[chaud::hot]` updates and feature-gated no-op macros), hot-lib-reloader (wrapped dylib exports and generic-function limitation), and bevy_simple_subsecond_system (annotated/preexisting-route scope plus unsupported workspace shapes).
- Rejected opening a new lane because the sharper missing value is still inside the already top-ranked compile-iteration bundle, not another adjacent hot-reload engine.

## 2026-03-23 (424) — compile-iteration outcome / degraded-mode pass

- Chose to deepen **P-0537** with live-update-outcome and degraded-iteration-mode artifacts because current sources now clearly distinguish theoretical patchability, actual patch application, degraded running posture, and restart-required danger zones.
- Main supporting signals: Rust challenges (compile time remains a universal productivity tax), compiler-performance survey (hot-patching still limitation-heavy), Subsecond (`PatchError` application failures), Chaud (warn vs error live-reload posture), and hot-lib-reloader (signature/layout/tracing crash hazards).
- Rejected opening a new lane because the sharper missing value is still inside the already top-ranked compile-iteration bundle, not another adjacent live-coding helper.

## 2026-03-23 (423) — compile-iteration retirement/depletion pass

- Chose to deepen **P-0537** with retirement-boundary and old-generation-drain artifacts because current sources now clearly distinguish activation, generation identity, route retirement, and drain completeness.
- Main supporting signals: Rust challenges (compile time remains a universal productivity tax), compiler-performance survey (hot-patching still limitation-heavy), Subsecond (stack rewind + nested hot anchors), Chaud (unbounded old-code survival), and hot-lib-reloader (reload observer lifecycle without drain proof).
- Rejected opening a new lane because the sharper missing value is still inside the already top-ranked compile-iteration bundle, not another adjacent hot-reload helper.


## 2026-03-23 (422) — compile-iteration generation witness pass

- Re-read current Rust challenges and compiler-performance survey material to confirm compile iteration remains top-tier salience.
- Re-read current Dioxus/Subsecond/Chaud/hot-lib-reloader docs to isolate a support-contract gap around code-generation identity rather than generic hot reload enthusiasm.
- Chose to deepen **P-0537** with generation-witness and mixed-generation-risk artifacts because current sources now clearly distinguish activation, route cut points, pointer latestness, and old-code survival.

## 2026-03-23 (421) — compile-iteration activation / stale-code refresh

- Re-read **P-0537** and confirmed the next thin seam was not another dev-server or hotpatch wrapper, but the meaning of *fresh code becoming active* versus *a reload-looking event having happened*.
- Refreshed evidence with the March 2026 Rust challenges post, the active Relink don’t Rebuild goal, current Dioxus hot-reload docs, current `subsecond` docs, current `chaud` docs, and current `hot-lib-reloader` docs/source.
- Added `activation-boundary.report`, `stale-code-risk.report`, and five scenario families showing entrypoint-gated activation, reload-event handoff, stored callback / trait-object stale code, `TypeId` identity drift, and portable bundle separation.
- Updated **P-0537** so future passes stop flattening patch route, continuity, activation, and stale-code residency into one fake “reload worked” story.

## 2026-03-23 (419) — concurrency-contract refresh around locality/affinity and driver-liveness

- Re-read **P-0538** and confirmed the next thin seam was not another primitive, abstraction, or runtime choice helper.
- Refreshed evidence with the March 2026 Rust challenges post, the 2026 community wish-list thread, Tokio runtime / `spawn_local` / `LocalSet` / `Handle::block_on` / `LocalRuntime` docs, `async_executor::LocalExecutor`, glommio docs, and current executor-abstraction crates.
- Added `mobility-affinity.report`, `driver-liveness.report`, and six scenario families showing local-context spawn requirements, non-driving handles on `current_thread`, thread-bound local runtimes, creator-thread-bound `async_executor`, glommio local-executor requirements, and portable bundle separation.
- Updated **P-0538** so future passes stop flattening locality, liveness, execution-context legality, fairness, and cancellation into one fake “works in async” story.

## 2026-03-23 (418) — pathfinder exclusion / re-entry refresh

- Re-read the March 2026 Rust challenges write-up, 2024 survey learning-material notes, the January 2026 crates.io development update, current Cargo `info` / `add` docs, current docs.rs build docs, and the active crates.io search discussion.
- Confirmed that richer public surfaces still do not explain why an excluded candidate lost or what exact fact would let it back in.
- Added planning plus fixture/schema stubs for `candidate-elimination.receipt` and `candidate-reentry.policy`, with scenario families for MSRV exclusion, search/popularity non-authority, visibility/SLOC non-authority, and portable bundle separation.
- Reaffirmed that runner-up status, hard exclusion, re-entry, and replacement must remain distinct stories.

## 2026-03-23 (416) — deepen dependency lifecycle around selection anchors and re-resolution honesty

- Re-read the current **P-0535** lane and confirmed that the sharper missing layer is not another dependency graph UI or upgrade helper, but a **support-contract bundle** for what currently anchors the realized transition route and what happens on a clean re-resolve.
- Refreshed evidence with the January 2026 safety-critical write-up, the January 2026 maintenance post, the March 2026 Rust challenges write-up, the January 2026 crates.io update, current Cargo.toml vs Cargo.lock docs, overriding-dependencies docs, source-replacement docs, cargo update docs, cargo yank docs, and current `rust-version` docs.
- Added a new frontier note, a new re-resolution plan note, two new schemas, and scenario families for local patch plus lock anchors, yanked-but-locked selection drift, `rust-version`-sensitive family shifts, and portable bundles that keep override authority / selection anchor / clean-resolve risk separate.
- Reaffirmed that a green current lockfile, a local patch, a vendor mirror, or one successful CI build must not masquerade as one honest lifecycle-transition durability story.

## 2026-03-23 (415) — pathfinder freeze-time / replay refresh

- Re-read **P-0509** and confirmed the next thin seam was not another ranking surface, but the meaning of freeze-time knowability after teams commit a starter-set lock.
- Refreshed evidence with the March 2026 Rust challenges post, the 2025 State of Rust survey, the January 2026 crates.io update, the active crates.io search discussion, current Cargo `add`/`info` docs, and current docs.rs metadata plus default-target-change material.
- Added `decision-timebox.receipt`, `as-of-replay.report`, and pathfinder-bundle updates plus scenario families for pubtime cooldown, docs-surface drift, and portable bundle separation.
- Updated **P-0509** so future passes stop flattening current registry/docs visibility, current search order, and freeze-time decision authority into one fake “best crate” story.

## 2026-03-23 (410) — broad rerank / concurrency-contract refresh

- Re-read the latest archive and confirmed that the next worthwhile addition was not another dashboard, ranking pass, or mutex implementation, but a receiver-facing concurrency support-contract lane above existing channels/resource/runtime coverage.
- Refreshed evidence with the March 2026 Rust challenges note, the 2025 State of Rust survey, the February 2026 Rust debugging survey, the active Rust forum thread on missing ecosystem pieces, and current primary docs for Tokio `Mutex`, `RwLock`, `Semaphore`, `select!`, `parking_lot`, `std::sync::Mutex`, and the experimental `std::sync::ReentrantLock`.
- Added **P-0538 Concurrency Contract Kit**, a lane-boundaries note, core schemas for `reentrancy-scope`, `progress-fairness`, `wait-cancellation`, `execution-context-boundary`, and a portable bundle manifest, plus scenario families for Tokio fairness-vs-reentrancy, lane-specific cancellation behavior, `parking_lot` eventual fairness, and std blocking/reentrant distinctions.
- Updated archive memory and hygiene so future passes do not collapse reentrancy, progress/fairness, cancellation, and execution-context truth into one fake “concurrency-safe” verdict.

## 2026-03-23 (409) — rustdoc JSON support-contract refresh

- Re-read **P-0051** and confirmed the next thin seam was not another parser API, but the meaning of route provenance, supported format windows, and normalization-loss honesty for machine-facing docs tooling.
- Refreshed evidence with the rustdoc unstable-features page, Cargo unstable `output-format` docs, the docs.rs rustdoc JSON page, the cargo-semver-checks goal, and the 2025 State of Rust survey.
- Added `source-route.receipt`, `format-window.matrix`, `normalization-loss.report`, and `rustdoc-json-support-bundle.manifest` schemas plus five scenario families showing docs.rs import caveats, rustup component imports, multi-version support windows, cross-crate/manfest loss ceilings, and portable bundle composition.
- Updated **P-0051** so future passes stop flattening parse success, format-window support, normalization quality, and downstream query confidence into one fake “rustdoc JSON is handled” claim.

## 2026-03-23 (405) — compile-time containment / ambient ingress refresh

- Re-read **P-0107** and confirmed the next thin seam was not another backend experiment, but the meaning of inherited env/path/toolchain channels and wrapper routes inside supposedly sandboxed compile-time lanes.
- Refreshed evidence with the sandboxed-build-scripts project goal, Cargo env/config docs, permanently-unstable `--compile-time-deps`, the long-running env-sanitization and host-config issues, the old-but-still-relevant `OUT_DIR` build-time release note, and current primary-source README material for `cargo-sandbox` and `cackle`.
- Added `ambient-input.receipt`, `sanitization-mode.receipt`, and `launcher-route.receipt` schemas plus five scenario families showing env/path ingress, host-flag bleed, route mutation risk, project-local opt-out rejection, and portable bundle composition.
- Updated **P-0107** so future passes stop flattening explicit capability grants, ambient ingress, sanitization posture, and launcher-route meaning into one fake “sandboxed build” claim.

## 2026-03-23 refresh — crate off-ramp authority / horizon / witness pass (403)

This pass returned to **P-0515 Crate Off-Ramp Pack Kit** instead of adding another advisory client, registry policy helper, or maintenance-score variant.

The sharper gap is now the receiver-facing difference between:
- successor class,
- successor authority,
- temporary stopgaps,
- and migration paths that were actually witnessed.

Added:
- `entries/2026-03-23-403.md`
- `meta/crate-offramp-frontier-2026-03-23.md`
- `meta/crate-offramp-authority-horizon-plan-2026-03-23.md`
- `meta/crate-offramp-claim-boundaries-2026-03-23.md`
- new schema/example files for `successor-authority.receipt`, `stopgap-horizon.report`, `recipe-witness.report`, and `offramp-support-bundle.manifest`.

Why this matters:
- deprecation substrate is real,
- yanks and advisories can create stopgaps,
- but another team still needs one honest artifact for *who is telling them to leave, for how long a stopgap is acceptable, and how much of the exit path was actually checked*.

## 2026-03-23 (401) — publish receipts need registry-capability and protection-scope honesty

- Re-read `P-0477 Cargo Publish Receipt Join Kit` and confirmed the earlier lane still flattened too much registry-specific behavior into a generic “post-publish receipt” story.
- Checked current Cargo registry docs and recent crates.io/security posts. The key new boundary is that crates.io now exposes TP-only posture, `pubtime`, and specific mitigation/advisory behavior, while alternate registries remain capability- and vendor-dependent rather than uniformly covered.
- Conclusion: deepen **P-0477** around `registry-capability.receipt.json`, `protection-scope.report.json`, and `publish-join-bundle.manifest.json` rather than opening another generic release helper, registry trust score, or moderation idea.

## 2026-03-23 (400) — deepen workspace-boundary doctor around ancestor discovery, config layering, and invocation mode

- Re-read **P-0506 Cargo Workspace Boundary Doctor Kit** and confirmed that the sharper missing layer is no longer just “why did Cargo choose that workspace?”
- Current official Cargo material now makes a reviewable split possible between **ancestor discovery**, **config layering**, and **invocation mode**.
- Added `meta/cargo-workspace-boundary-frontier-2026-03-23.md`, `meta/cargo-workspace-boundary-product-plan-2026-03-23.md`, and `meta/cargo-workspace-boundary-invocation-boundaries-2026-03-23.md`.
- Added new fixture/schema families for `ancestor-discovery.receipt.json`, `config-layering.report.json`, `invocation-mode.report.json`, and `boundary-support-bundle.manifest.json`, plus scenario examples for include/CLI layering, manifest-command route shifts, single-file package posture, and portable bundle shape.
- Updated **P-0506**, the archive entry stream, and repo hygiene docs so future passes do not collapse parent candidates, config precedence, and invocation route into one fake “workspace root” story.

## 2026-03-23 (399) — deepen crate knowledge pack around answerability scope and claim-trace honesty

- Re-read the current P-0536 substrate and confirmed that the sharper missing layer is not another assistant wrapper, but a **support-contract bundle** for machine-facing pack structure, query-support scope, refusal/manual-review honesty, and claim traceability.
- Refreshed evidence with the 2025 State of Rust survey, docs.rs builds/metadata/redirections/download/rustdoc-json pages, Cargo unstable `output-format` docs, and RFC 2963 rustdoc JSON.
- Added a new frontier note, an answerability-plan note, an assistant-boundaries note, three new schemas, and three scenario families for supported-query declarations, question-class matrices, and traceable machine-summary claims.
- Reaffirmed that “we emitted assistant context”, “the crate has rustdoc JSON”, “docs.rs hosts the docs”, and “the slice is compact” must not masquerade as one honest crate-knowledge verdict.


## Added 2026-03-23 (397) — contract-consumption honesty became the sharper missing layer

- Chose to deepen **P-0453 Safety Contract Consumer Kit** instead of adding another verifier or assurance wrapper because the current missing layer is the reviewer-facing contract-consumption handoff above emerging std contracts and multiple proof/checking tools.
- Treat std-contract authority, downstream consumer coverage, and semantic-lane caveats as separate review objects.
- Prefer small mixed-lane fixtures and consumer-coverage matrices for future passes instead of broad “cross-tool support” claims.

## Update 2026-03-23 (396) — async runtime deployment-topology / guarded-capability pass

- Re-read **P-0532 Async Runtime Assurance Profile Kit** and confirmed that the sharper missing layer is no longer only runtime family or even service topology; it is also a receiver-facing contract for **deployment lanes**, **capability availability by lane**, and **explicit surface guards**.
- Refreshed evidence with the March 2026 Rust challenges post, the January 2026 safety-critical Rust post, current Tokio runtime/I-O/signal/AsyncFd docs, the Embassy book plus Embassy executor docs, and current RTIC app/software-task/monotonic docs.
- Added a frontier note, product-plan note, lane-boundary note, three new schemas, and scenario families for Embassy host-vs-target topology, Tokio lane-scoped AsyncFd/signal support, Windows-vs-Unix surface guards, and portable bundles that keep topology, matrix, and guards separate.
- Reaffirmed that runtime family names, one working example host, and one platform-specific demo must not masquerade as one honest async-runtime support story.

## Update 2026-03-23 (395) — async runtime assurance topology / capability-route pass

- Re-read **P-0532 Async Runtime Assurance Profile Kit** and confirmed that the sharper missing layer is no longer only a runtime-choice summary; it is a receiver-facing contract for **service topology**, **capability routes**, and **compatibility-bridge debt**.
- Refreshed evidence with the March 2026 Rust challenges post, the January 2026 safety-critical Rust post, current Tokio runtime/resource-driver/context docs, current Embassy executor + time-driver docs, current RTIC app/software-task docs, and current `async-compat` / `async_executors` / `async-std` docs.
- Added a frontier note, product-plan note, lane-boundary note, three new schemas, and scenario families for Tokio manual runtimes missing time drivers, split Embassy executor/time-driver topology, RTIC dispatcher/timer-queue service lanes, bridge-debt honesty for `async-compat`, and portable bundles that keep runtime profile/topology/bridge debt separate.
- Reaffirmed that dependency name, adapter presence, and one working host configuration must not masquerade as one honest async-runtime support story.

## 2026-03-23 (394) — deepen projection/reborrow work around authority and witness honesty

- Re-read the current **P-0440** lane and confirmed that the sharper missing layer is not another projection macro or ergonomic helper, but a **support-contract bundle** for projection authority, borrow-mode coverage, witness basis, and portable semantics review.
- Refreshed evidence with the 2026 flagships page, the field-projections goal, the reborrow-traits goal, the in-place-initialization goal, current crate pages for `pin-project`, `pin-init`, `reborrow-generic`, and `moveit`, the Miri repository, and the 2025 PinChecker paper.
- Added product-plan updates plus fixture/schema stubs for `projection-authority.receipt`, `borrow-semantics.matrix`, `semantics-witness.report`, and `projection-support-bundle.manifest`, with scenario families for macro-authority overread, generalized-reborrow mode flattening, partial Miri witness coverage, and portable bundle separation.
- Reaffirmed that macro presence, helper traits, green test runs, green Miri runs, and full semantic support must not masquerade as one interchangeable “projection is handled” claim.

## 2026-03-22 (393) — deepen ecosystem navigation around candidate basis and visibility honesty

- Re-read the current **P-0509** lane and confirmed that the sharper missing layer is not another crate-ranking UI or blessed-catalog debate, but a **decision-pack bundle** for candidate-basis honesty, support-visibility truth, and portable starter-set handoff.
- Refreshed evidence with the March 2026 Rust challenges write-up, the December 2025 “What do people love about Rust?” post, the January 2026 crates.io development update, the February 2026 malicious-crate notification update, the October 2025 docs.rs default-target change, current docs.rs metadata docs, and current Cargo `add` / `info` docs.
- Added product-plan updates plus fixture/schema stubs for `candidate-basis.receipt`, `support-visibility.report`, and `pathfinder-bundle.manifest`, with scenario families for Cargo best-effort source selection, public support-surface overread, and portable bundle separation.
- Reaffirmed that Cargo discoverability, registry trust surfaces, docs.rs visibility, and actual task-fit judgment must not masquerade as one interchangeable “best crate choice” claim.

## 2026-03-22 (383) — deepen dependency lifecycle transitions around override authority and freshness honesty

- Re-read the current **P-0535** lane and confirmed that the sharper missing layer is not another dependency tree viewer, local patch helper, or vendoring wrapper, but a **support-contract bundle** for transition authority, imported-signal freshness, exception reevaluation, and release-to-release posture drift.
- Refreshed evidence with the January 2026 safety-critical write-up, the March 2026 Rust challenges post, current Cargo config docs, current Cargo source-replacement docs, current cargo-metadata docs, current Cargo.toml vs Cargo.lock docs, the January 2026 crates.io development update, and the Rust Foundation 2026–2028 strategy.
- Added product-plan updates plus fixture/schema stubs for `override-authority.receipt`, `signal-freshness.report`, and `exception-reevaluation.report`, with scenario families for local config-patch visibility, source-replacement not implying fork progress, stale imported signals, expired exceptions, and portable bundle separation.
- Reaffirmed that a local patch, a vendored source, positive imported signals, and an old waiver must not masquerade as one honest lifecycle-transition verdict.

## 2026-03-22 (382) — deepen trusted-publishing tooling around registry-state imports and authorization drift

- Re-read the current **P-0175** lane and confirmed that the sharper missing layer is not another CI OIDC helper, but a **support-contract bundle** for imported registry trust state, workflow-route identity, claim/trigger/mode coherence, and release-to-release authorization drift.
- Refreshed evidence with RFC 3691, the January 2026 crates.io development update, current GitHub OIDC docs, current GitLab ID-token/docs, and the January 2026 Rust Infrastructure update about trusted publishing as IaC.
- Added product-plan updates plus fixture/schema stubs for `registry-publisher-state.import`, `workflow-identity-route.receipt`, and `publish-authorization-drift.report`, with scenario families for imported TP-only state, reusable workflow route identity, GitLab route drift, and portable bundle separation.
- Reaffirmed that imported crates.io trust state, repo-local policy, observed CI claims, and authorization drift must not masquerade as one interchangeable “trusted publishing configured” claim.

## 2026-03-22 (380) — deepen cargo feature-surface contract around scope honesty and hosted-doc posture

- Re-read the current Cargo/docs.rs feature substrate and confirmed that the sharper missing layer is not another feature enumerator, docs page, or combination runner, but a **support-contract bundle** for public feature surface, activation profiles, exact observation scope, hosted-doc feature posture, and portable review bundles.
- Refreshed evidence with the current Cargo feature reference, resolver reference, Rust 2021 resolver guide, docs.rs metadata docs, release notes on namespaced/weak dependency features, RFC 2957, RFC 3143, the 2025 State of Rust survey, and the March 2026 Rust challenges post.
- Added product-plan updates plus fixture/schema stubs for `resolution-scope.receipt`, `hosted-feature-profile.receipt`, and `feature-support-bundle.manifest`, with scenario families for workspace-wide `--no-default-features` scope drift, docs.rs `all-features` hosted-doc posture, and portable bundle separation.
- Reaffirmed that one observed scope, one docs.rs feature profile, and one green all-features build must not masquerade as one honest feature-support verdict.

## Update 2026-03-22 (376) — toolchain authority / docs-surface / bundle pass

- Re-read the current **P-0484** lane and verified that it remained the strongest frontier but still lacked one crisp separation: imported upstream authority versus local support promise versus public docs surface.
- Refreshed evidence with current official sources on safety-critical target-readiness guidance, March 2026 ecosystem challenges, rustup 1.29.0, rustup override rules, Cargo build-cache/config docs, docs.rs metadata/builds docs, the October 2025 docs.rs default-target change, and RFC 2803 target-tier policy.
- Added `meta/toolchain-target-support-authority-surface-plan-2026-03-22.md`, three new schemas, and concrete scenario artifacts for rustup-supported-host import truth, implicit docs.rs default-surface drift, and portable support-bundle inventory.
- Updated **P-0484** so future passes stop flattening upstream authority, public docs surface, and project-local support class into one fake “supports target X” claim.

## Update 2026-03-22 (375) — debuggability artifact-completeness pass

- Re-read the current **P-0486** lane and confirmed that the sharper missing layer above debugger substrate is not another launcher or symbol helper, but a **debug support contract** for broad posture, exact backend observations, source-material lookup, and portable review bundles.
- Refreshed evidence with the February 2026 Rust debugging survey, the March 2026 Rust challenges write-up, current Cargo profile/build-cache docs, current `rustc` codegen docs, the Rust Reference on `#[debugger_visualizer]`, and the March 2026 Build Dir Layout v2 call-for-testing.
- Added a new frontier-salience note, a new artifact-completeness note, three new schemas, and new scenario families for one observed Visual Studio lane that must not imply cross-backend support, trimmed-path builds that still need internal source materials, and portable bundles that keep sidecars/backend evidence/source materials separate.
- Reaffirmed that symbol-rich artifacts, visualizer presence, source-lookup consequences, exact checked backend capabilities, and portable support-bundle truth must not collapse into one fake “debuggable build” verdict.


## 2026-03-22 (374) — MSRV policy-activation / split-policy / authoring-floor scan

Primary-source refresh used for this pass:
- Cargo `rust-version` docs framing MSRV as a support promise and saying unsupported-toolchain diagnostics affect all package targets;
- Cargo resolver docs spelling out mixed-MSRV workspace heuristics and “too low / too high” selection pressure;
- Rust 2024 Edition Guide and Cargo workspace docs making root-level resolver activation and virtual-workspace explicitness concrete;
- Cargo changelog notes around explicit virtual-workspace resolver warnings and lockfile v4 default authoring behavior;
- Rust 1.93 release notes noting that Cargo now respects `rust-version` when generating lockfiles;
- active Cargo issue traffic showing `cargo run` vs `cargo metadata` divergence and mixed-workspace surprise remains real;
- and current `cargo-msrv` changelog/repo state confirming that find/verify tooling is alive but still not a portable support-contract export.

Archive judgment from the scan:
the missing value is not another one-number MSRV tool.
It is a reviewable MSRV support contract for **effective workspace promises**, **policy activation**, **command-family floors**, **lockfile-authoring honesty**, **member-split drift**, and **portable support bundles**.

## 2026-03-22 (371) — unsafe authority/drift/comparison scan

Primary-source refresh used for this pass:
- the 2026 flagships page explicitly naming normative unsafe documentation in the safety-critical agenda;
- the std-contracts goal describing contract attributes, machine-retrievable safety conditions, and contract-as-code direction;
- the unsafe-fields goal describing why important invariants often live beyond the visible surface of `unsafe` blocks;
- Miri’s public docs stressing both its practical UB coverage and the fact that it does not define the full Rust specification;
- and the January 2026 safety-critical write-up favoring reviewable, transportable evidence over folklore.

Archive judgment from the scan:
the missing value is not another unsafe checker UI.
It is a reviewable unsafe-evidence contract for **authority imports**, **obligation drift**, **witness comparison**, and **partial callback/FFI boundaries**.

## 2026-03-22 — Cargo lock-contention witness refresh

- Re-read current Cargo build-cache docs and build-dir-layout material to confirm that `target-dir` and `build-dir` are now explicitly separate user-facing roots, not just internal folklore.
- Re-read current rust-analyzer configuration docs to confirm that target-dir separation, override commands, invocation strategy, and wrapper posture are now explicit enough to model as artifact fields.
- Re-read current Cargo unstable docs and Cargo 1.93 development-cycle notes to confirm that compile-time-only tool lanes and split lock work are real substrate but still not a finished stable contention story.

## 2026-03-22 — public/private dependency boundary product-plan pass

- Re-read the current official public/private dependency direction and confirmed that the sharper missing layer above Cargo/rustc is not another lint wrapper, but a **reviewable boundary bundle** that separates manifest intent, effective publicness, route, provenance, workspace gaps, and migration posture.
- Refreshed evidence with the 2025H2 public/private dependency goal, the 2026 flagship themes, RFC 3516, Cargo unstable docs, `cargo add` docs, Cargo changelog notes around public-dependency support, `public_api`, and `cargo-check-external-types`.
- Added a new frontier note, product-plan note, lane-boundary note, a fixture/schema family, and concrete scenarios for reexports, workspace inheritance gaps, hidden-shim allowlists, SemVer-sensitive wrapper migrations, and release drift.
- Reaffirmed that manifest declaration, effective exposure, rustc/Cargo authority, rustdoc inference, and migration advice must not collapse into one fake “public dependencies handled” verdict.

## 2026-03-22 — in-place initialization / pinned construction deepening

- Re-read official Rust planning and current crate substrate to decide whether the next worthy contribution should be another pinning helper or a shared review layer for construction semantics.
- Current anchors used for the pass:
  - Rust in 2026 flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - In-place initialization goal — https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
  - Reborrow traits goal — https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
  - `moveit` docs — https://docs.rs/moveit/latest/moveit/
  - `pin-init` docs — https://docs.rs/pin-init/latest/pin_init/
  - Crubit `Ctor` — https://github.com/google/crubit/blob/main/support/ctor.rs
  - “Initialization in Rust with pin-init” handout — https://lpc.events/event/19/contributions/2018/attachments/1769/3837/handout.pdf
- Main conclusion: the missing crate is not another macro or one more abstract proposal summary, but a compact support-contract layer that publishes **placement topology**, **constructor-lane truth**, **address-commit truth**, **failure-cleanup truth**, and **transition drift** above today’s crates and tomorrow’s language support.

## 2026-03-22 — lint-policy evidence scan

- Rust’s 2026 flagship goals now explicitly include **safety-critical lints in Clippy**, which raises the salience of lint-policy evidence as a first-class ecosystem gap.
- Cargo’s manifest and workspace references now provide stable `[lints]` and `workspace.lints` surfaces, while the unstable reference documents `[lints.cargo]` behind `-Zcargo-lints`.
- Cargo’s January 2026 development notes show workspace-level lint semantics and inherited dependency linting are still active design seams.
- Clippy’s configuration reference makes scope-changing knobs concrete: private-item coverage, test-only MSRV checks, and safety-comment interpretation all materially affect what a “clean” run means.
- Conclusion: deepen **P-0459** around policy authority, checked scope, diagnostic channels, waivers, and drift rather than adding another generic lint runner.

## Update 2026-03-22 (346) — unsafe-field invariant contract deepening

- Re-read **P-0460** and **P-0120** and confirmed that the archive had a strong broad unsafe lane but still lacked one crisp receiver-facing lane for **field-carried invariants** specifically.
- Refreshed evidence with the unsafe-fields goal, the std-contracts goal, the 2026 flagships page, the January 2026 safety-critical Rust write-up, and “The Scope of Unsafe”.
- Added a new frontier note, a product-plan note, a lane-boundary note, and new fixtures centered on field authority, mutation lanes, trusted constructors, witness-scope honesty, and drift.
- Reaffirmed that field privacy, safety comments, Miri success, and trusted constructors are different truths that should not be flattened into one fake “the unsafe invariant story is covered” verdict.

## Update 2026-03-22 (345) — documentation-example support-contract deepening

- Re-read **P-0455**, **P-0481**, **P-0472**, and **P-0476** and confirmed that the archive had enough docs-facing proposals but still lacked one clear shared core for documentation-example support truth.
- Refreshed evidence with the March 2026 2025 State of Rust survey results, the Rust-for-Linux tooling goal, rustdoc’s unstable doctest JSON docs, current rustdoc documentation-test docs, current release notes for `--test-runtool` and `ignore-*`, and the merged-doctests goal.
- Added a new frontier note, a product-plan note, a lane-boundary note, and new fixtures centered on manifest extraction, rewrite lineage, execution-mode truth, support-class reporting, and drift.
- Reaffirmed that docs canonicality, docs.rs success, and doctest execution are three different truths that should not be flattened into one fake “our docs are supported” verdict.

## 2026-03-22 — dependency lifecycle / criticality / seam pass

- Added **P-0535 Dependency Lifecycle Transition Kit** after checking the January 2026 safety-critical write-up, the December 2025 Vision Doc post, the 2025 State of Rust survey, the January 2026 crates.io update, and current Cargo graph / resolver / override docs.
- Main conclusion: the missing layer is not another trust score or dependency graph viewer, but a reviewable contract for **where third-party crates may live**, **what seam contains them**, and **how they are expected to leave over time**.
- Added product-plan, lane-boundary, frontier, and fixture docs for P-0535.
- Updated archive memory / prioritization / roadmap / hygiene notes so future passes do not duplicate dependency lifecycle planning inside Trust Lens, MSRV, or crate off-ramp work.


## 2026-03-22 — toolchain/target support follow-up scan

Fresh signals reviewed in this pass:
- Rust challenges (cross-compilation and `no_std` friction remain explicit)
- safety-critical Rust (target-readiness questions remain explicit)
- Cargo build-dir-layout-v2 call for testing (many projects rely on unspecified build-dir details)
- rustup 1.29.0 (host support and environment behavior continue to move)
- docs.rs metadata + 2025 default-target change
- 2025 target demotion announcements for `i686-pc-windows-gnu` and `x86_64-apple-darwin`

Conclusion: the sharpest missing contribution is still not another builder or linker helper, but a support-contract layer that makes artifact discovery and host/target execution topology reviewable.

## 2026-03-22 — cross-language interop / boundary-contract refresh

- Re-read current official Rust framing and interop substrate to decide whether the next worthy contribution should be another generator/shipkit or a stronger shared boundary contract.
- Current anchors used for the pass:
  - 2025 State of Rust survey — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - program-management update (application areas incl. Cross-language interop and Safety-critical & regulated) — https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
  - safety-critical Rust write-up with explicit interop/bindings guidance — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
  - Rust 2024 `unsafe extern` guide — https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html
  - Rust Reference external blocks — https://doc.rust-lang.org/reference/items/external-blocks.html
  - RFC 2945 `C-unwind` — https://rust-lang.github.io/rfcs/2945-c-unwind-abi.html
  - `cxx` shared / opaque / result docs — https://cxx.rs/shared.html ; https://cxx.rs/concepts.html ; https://cxx.rs/binding/result.html
  - UniFFI object refs / async / errors / foreign traits — https://mozilla.github.io/uniffi-rs/latest/internals/object_references.html ; https://mozilla.github.io/uniffi-rs/latest/internals/async-ffi.html ; https://mozilla.github.io/uniffi-rs/latest/udl/errors.html ; https://mozilla.github.io/uniffi-rs/latest/foreign_traits.html
  - Diplomat book (types / opaque) — https://rust-diplomat.github.io/book/types.html ; https://rust-diplomat.github.io/book/opaque.html
  - component model / WIT / resources / Canonical ABI motivation — https://component-model.bytecodealliance.org/design/why-component-model.html ; https://component-model.bytecodealliance.org/design/wit.html ; https://component-model.bytecodealliance.org/using-wit-resources.html ; https://component-model.bytecodealliance.org/design/wit-example.html
  - `cbindgen` docs — https://docs.rs/cbindgen/latest/cbindgen/
- Main conclusion: the missing crate is not another generator, but a compact boundary-contract layer that publishes **ownership**, **unwind**, **callback**, **coverage**, **layout authority**, and **error channel** truth above today’s bridges and generators.

## Update 2026-03-22 (338) — broad territory rerank + target-readiness support-contract refinement

- Re-read the latest archive and chose a **broad rerank** instead of adding another narrow top-level proposal.
- Refreshed evidence with the March 2026 Rust challenges post, the March 2026 2025 State of Rust survey results, the January 2026 safety-critical Rust post, the February 2026 program-management update, and the latest rustup / docs.rs / target-tier / Cargo resolver docs already feeding **P-0484**.
- Added an explicit epic-crate rubric, an archive-refresh checklist for future humans/LLMs, a fresh frontier-salience snapshot, and a lane-boundary note for **P-0484**.
- Deepened **P-0484 Toolchain & Target Support Contract Kit** with a new `target-readiness.report.json` review object plus a scenario that keeps target tier, `no_std` posture, last known tested environment, blockers, prerequisites, and exercise scope separate.
- Reaffirmed that the archive’s strongest near-term frontier is now support-contract infrastructure across toolchain/target support, MSRV, interop, runtime assurance, and debuggability.


## Update 2026-03-21 (335) — service readiness / drain contract addition

- Re-read the current Tower/Hyper/Axum/Tonic/Tokio substrate and confirmed that the sharper missing layer above it is not another framework or signal helper, but a **service-transition support contract** for activation gates, readiness surfaces, health channels, shutdown triggers, drain policy, and in-flight fate.
- Refreshed evidence with the March 2026 Rust challenges post plus current docs for Tower `Service` / `ServiceExt::ready`, hyper graceful shutdown, axum `WithGracefulShutdown`, tonic-health server utilities, Tokio graceful shutdown guidance, `TaskTracker`, and `tokio-graceful-shutdown`.
- Added a new proposal, product-plan note, lane-boundary note, frontier-salience note, schema pack, and scenario artifacts for poll-ready versus external readiness, warmup gates, gRPC health versus HTTP admission, graceful-timeout aftermath, and distinct shutdown triggers.
- Reaffirmed that activation, readiness, health, trigger, drain, and in-flight-fate truths must not collapse into one fake “service is healthy and supports graceful shutdown” verdict.

## Update 2026-03-21 (334) — crash artifact / symbolication product-plan pass

- Re-read the current **P-0101** lane and confirmed that the sharper missing layer above minidump parsing, stackwalking, symbol fetching, and dump writing is a **crash support contract** for capture basis, module identity, symbol route, analysis coverage, report determinism, and share-safety.
- Refreshed evidence with current `rust-minidump` / `minidump-stackwalk` docs and release notes, current `wholesym` docs, current `symbolic` docs, current `minidumper` and `minidump-writer` docs, Mozilla’s rust-minidump deployment/fuzzing notes, Jake Shadle’s crash-reporting notes, and the Breakpad symbol-file specification.
- Added a new product-plan note, lane-boundary note, seven schemas, and five scenario families for external-monitor capture posture, Windows code-id fallback truth, offline-versus-live symbol-route determinism, mixed-route coverage gaps, and safe-share bundle posture.
- Reaffirmed that “symbolicated crash report available” must not collapse capture posture, module identity confidence, symbol-route authority, report completeness, replayability, and share-safety into one fake support story.

## Update 2026-03-21 (333) — task supervision / restart product-plan pass

- Re-read the current **P-0095** lane and confirmed that the sharper missing layer above task groups, shutdown helpers, actor supervisors, and watchdog loops is a **supervision contract** for topology, restart policy, health/readiness basis, state reset, shutdown escalation, and failure bundles.
- Refreshed evidence with the March 2026 Rust challenges post, current Tokio `JoinSet` and task docs, current `tokio-util::task::TaskTracker` docs, and current docs for `task_scope`, `task-supervisor`, `spry`, and `ractor-supervisor`, plus Erlang supervisor background.
- Added a new product-plan note, lane-boundary note, six schemas, and five scenario families for blast-radius truth, meltdown-policy + bundle emission, clone-reset honesty, hung-task restart basis, and shutdown-timeout aftermath.
- Reaffirmed that “supports supervised tasks” must not collapse restart topology, trigger class, readiness/health basis, retained state, and timeout aftermath into one fake operational story.

## Update 2026-03-21 (332) — OpenAPI 3.1 / JSON Schema toolchain product-plan pass

- Re-read the current **P-0224** lane and confirmed that the sharper missing layer above parser/model crates, generic JSON Schema validation, and code-first emitters is a **toolchain contract** for dialect identity, ref-resolution route, projection policy, compatibility profile, and semantic-diff authority.
- Refreshed evidence with the current OpenAPI 3.1 specification, the current OpenAPI 3.1 Schema Object dialect publication, the current JSON Schema Draft 2020-12 overview, and current docs for `openapiv3_1`, `oas3`, `jsonschema`, and `utoipa`.
- Added a new product-plan note, lane-boundary note, six schemas, and five scenario families for dialect labeling, explicit ref-resolution policy, review-bundle versus codegen projection drift, structural-validity versus consumer-profile gaps, and descriptive diff versus policy-backed verdicts.
- Reaffirmed that “supports OpenAPI 3.1” must not collapse dialect posture, resolution policy, projection choice, consumer compatibility, and breaking-change authority into one fake toolchain story.

## Update 2026-03-21 (331) — evidence-bundle core becomes receipt-first again

### Why this pass happened

- **P-0256 Evidence Bundle Core Kit** was already important, but too many later proposals still depended on it with under-specified assumptions.
- Current external substrate now makes bundle layering much more explicit: in-toto layers, Sigstore bundles, OCI subject/referrers, and SCITT-style publication/transparency.
- The archive also picked up a small hygiene risk: future passes could oscillate between bundle substrate, attestation lane, and publication route semantics without naming the difference.

### What changed

- Added a real product plan for **P-0256**.
- Added a fresh lane-boundaries note.
- Upgraded the proposal around five explicit review objects: container basis, entry lineage, attestation lane, publication route, and share-safety posture.
- Expanded `fixtures/evidencebundle-core-kit/` with five new schemas and five new scenario families.
- Added an archive-hygiene note to keep the legacy `evidencebundle-core-kit` fixture root spelling stable until a deliberate bulk rename.

### Why this seems right

- Too many other archive lanes now want portable bundles without wanting to reinvent private grammar.
- Verification, replay, conformance, and assurance imports all become cleaner when bundle-substrate receipts stay reusable.
- Publication and attestation lanes are now concrete enough that they should stop hiding inside generic “bundle verified” prose.

### Next likely follow-ups

- Keep **P-0503** and **P-0264** honest consumers of **P-0256** rather than private format inventors.
- Prefer tiny adapter notes between domain profiles and the new receipt vocabulary before adding more bundle families.
- Revisit whether a deliberate directory rename from `evidencebundle` to `evidence-bundle` is worth the churn in a later hygiene-only pass.

## 2026-03-21 — trusted publishing productization

- Re-read **P-0175 Trusted Publishing Tooling Kit** and confirmed that the sharper missing layer is no longer just “rehearse trusted publishing”, but a **reviewable release-identity contract** for provider scope, claim basis, trigger policy, publish mode, and rehearsal result.
- Refreshed evidence with RFC 3691, the January 2026 crates.io development update, current crates.io trusted publishing docs, current GitHub OIDC/reusable-workflow docs, and current GitLab ID-token / `id_tokens` docs.
- Added `meta/trusted-publishing-tooling-product-plan-2026-03-21.md`, `meta/trusted-publishing-tooling-lane-boundaries-2026-03-21.md`, expanded `fixtures/trusted-publishing-tooling-kit/` with new claim-basis / publish-mode / support-bundle schemas, and added scenario artifacts for GitHub direct workflows, GitHub reusable workflows, blocked GitHub triggers, GitLab.com TP-only releases, self-hosted GitLab manual-review boundaries, and mixed-workspace migration posture.
- Reaffirmed that trusted-publishing rehearsal is distinct from post-publish receipts, provenance/attestation, registry-auth diagnosis, and public incident communication.

## 2026-03-21 — async replay debugger productization

- Chose to deepen **P-0073** instead of opening another adjacent determinism or incident-bundle lane.
- Decided that the next implementation pass should elevate **schedule basis**, **time basis**, **instrumentation coverage**, **effect boundaries**, and **replay fidelity** into first-class artifacts.
- Reaffirmed that async replay contracts are distinct from harness/minimization labs, trace-spec lanes, generic run/test bundle lanes, and runtime assurance lanes.


- Re-read **P-0081 Stable Plugin Host Kit** and confirmed that the sharper missing layer is no longer just “Rust can load plugins”, but a **native plugin support contract** for ABI surface, capability negotiation, lifecycle posture, and compatibility witnesses.
- Refreshed evidence with current docs for `abi_stable`, `abi_stable::library`, prefix types, `RootModule`, and `libloading`, plus adjacent FFI crates `cglue`, `safer_ffi`, and `interoptopus`, and current Cargo ecosystem writing on plugins.
- Chose to deepen the existing native-plugin lane rather than opening another adjacent Wasm-plugin, raw FFI, or marketplace lane.

- Re-read **P-0003 Array API** and confirmed that the sharper missing layer is no longer just “backend-agnostic arrays”, but a **support contract** for semantic profile, layout/view truth, device+dtype truth, namespace coverage, and interop routes.
- Refreshed evidence with the latest Python Array API standard purpose/scope and inspection docs plus current docs for `ndarray`, `nalgebra`, `faer`, `linalg-traits`, `mdarray`, `candle`, `burn`, and `arrow-array`.
- Added `meta/array-api-product-plan-2026-03-21.md`, `meta/array-api-lane-boundaries-2026-03-21.md`, `fixtures/array-api-kit/*.schema.json`, and scenario artifacts for operator-semantic mismatch, layout/order differences, device+dtype defaults, Arrow interop-route honesty, and profile separation between dense arrays and tensor backends.

- Re-read **P-0002 Wasm Plugin Kit** and confirmed that the sharper missing layer is no longer just “safe Wasm plugins”, but a **plugin support contract** for interface authority, capability grants, execution budgets, and instance lifecycle above current Wasmtime / component-model / Extism substrate.
- Refreshed evidence with the Rust 2026 flagships page, current Wasmtime plugin and component docs, current component-model packages/worlds/distribution docs, `cargo component`'s current README, and current Extism manifest/config/runtime docs.
- Added `meta/wasm-plugin-kit-product-plan-2026-03-21.md`, `meta/wasm-plugin-kit-lane-boundaries-2026-03-21.md`, `fixtures/wasm-plugin-kit/plugin-interface.receipt.schema.json`, `fixtures/wasm-plugin-kit/capability-grant.receipt.schema.json`, `fixtures/wasm-plugin-kit/execution-budget.receipt.schema.json`, `fixtures/wasm-plugin-kit/instance-lifecycle.receipt.schema.json`, and scenario artifacts for experimental tooling, allowlisted capabilities, budget-basis drift, and pooled-instance freshness bluffing.

- Re-read **P-0076 Local-first Sync Kit** and confirmed that the sharper missing layer is no longer just repo/transport/membership receipts, but also a **presence contract** and a **history-retention contract** above current local-first substrate.
- Refreshed evidence with current Automerge docs, Automerge Repo DocHandle docs for ephemeral messages, current Yrs sync/awareness docs, and current Loro version-control / shallow-snapshot docs.
- Added `meta/localfirst-sync-kit-product-plan-2026-03-21.md`, `meta/localfirst-sync-kit-lane-boundaries-2026-03-21.md`, `fixtures/localfirst-sync-kit/presence-surface.receipt.schema.json`, `fixtures/localfirst-sync-kit/history-retention.receipt.schema.json`, and scenario artifacts for ephemeral presence overclaim and shallow-snapshot history narrowing.

- Opened **P-0533 Error Surface Contract Kit** after checking current `std::error`, `thiserror`, `anyhow`, `miette`, `ariadne`, `error-stack`, and `snafu` docs plus the 2025 State of Rust survey.
- Chose to treat the missing value as a receiver-facing contract layer instead of another error type or renderer.
- Added `meta/error-surface-contract-product-plan-2026-03-21.md`, `meta/error-surface-contract-lane-boundaries-2026-03-21.md`, and `fixtures/error-surface-contract-kit/` with first artifact vocabulary for identity, audience, remediation, and sensitivity posture.

- Opened **P-0532 Async Runtime Assurance Profile Kit** after re-reading the March 2026 Rust challenges post, the January 2026 safety-critical Rust post, the 2026 flagships page, and current Tokio / Embassy / RTIC runtime docs.
- New judgment: the sharper missing layer above async language progress and existing runtime implementations is a **runtime-choice support contract** for runtime family, allocation posture, shutdown behavior, timing/preemption posture, and qualification basis.
- Added a product plan, lane-boundaries note, two starter schemas, and concrete fixture scenarios showing that Tokio timeout-based shutdown and static embedded executor/scheduler profiles must not be flattened into one fake “async runtime support” story.

- Refreshed **P-0489** with Cargo's March 13, 2026 Build Dir Layout v2 call for testing, Cargo build-cache docs, Cargo build/docs for `CARGO_BIN_EXE_*`, Cargo environment-variable docs for `OUT_DIR`, and the Cargo 1.94 changelog.
- New judgment: the sharper downstream gap is **adapter-viability windows** — maintainers need a compact receipt that says whether a proposed migration path is documented stable now, only above a Cargo floor, nightly-only, heuristic-only, or still blocked on upstream.

## Update 2026-03-21 (315) — crate-health maintenance-coverage / duty-map refinement

- Re-read the current crate-health lane and confirmed that the sharper missing layer above support windows and succession is a **stewardship contract** for what maintenance work is actually covered.
- Refreshed evidence with the 2026 Inside Rust maintenance post, the 2025 State of Rust survey, current crates.io development updates, Cargo manifest docs on badge-era maintenance status, the crates.io maintenance-status UI/API issue, and the existing internals discussion on maintenance metrics.
- Added a new maintenance-coverage note, one new schema, and concrete scenario artifacts for quiet-reactive support with review gaps and feature-active work with invisible maintenance gaps.
- Reaffirmed that broad health profile, support horizon, succession, imported trust signals, and maintenance-duty coverage must not collapse into one fake “maintained crate” story.

## Update 2026-03-21 (313) — resource-surface topology / clone-sharing refinement

- Re-read the current resource-support substrate and confirmed that the sharper missing layer above bounds/saturation is a **support contract** for budget topology, clone sharing, multiplication axes, and aggregate-bound honesty.
- Refreshed evidence with the 2025 State of Rust survey plus current docs for `reqwest::Client`, `reqwest::ClientBuilder::pool_max_idle_per_host`, `sqlx::Pool`, Deadpool `Pool`, Tokio `mpsc::Sender`, Tokio `mpsc`, Moka shared-cache clone behavior, Tower `ServiceBuilder` order, and tonic server per-connection concurrency/load-shed posture.
- Added a new budget-topology note, one new schema, and concrete scenario artifacts for shared reqwest client pools, shared sqlx pool handles, and tonic per-connection concurrency that should not be misread as a process-wide cap.
- Reaffirmed that a local numeric limit, sharing scope, multiplication axis, and aggregate deployment bound must not collapse into one fake “resource boundedness” verdict.

## 2026-03-21 — cargo-build-insights product-plan pass

- Re-read the current Cargo build-analysis substrate and confirmed that the sharper missing layer above it is not another timing viewer or one-run incident explainer, but a **historical imported-session warehouse** with explicit comparison-window, series-split, and export-bundle truth.
- Refreshed evidence with the build-analysis project goal, current unstable Cargo docs for `-Zbuild-analysis` / `cargo report`, the Cargo 1.94 development-cycle update, Cargo external-tools / `cargo metadata` docs, the 2025 compiler performance survey, and the 2025 State of Rust survey.
- Added a new product-plan note, a comparison-window boundaries note, a new schema for `comparison-window.receipt`, and scenario families for PR-vs-last-green review windows and redacted CI trend exports.
- Reaffirmed that session import, comparison-window choice, series compatibility, and per-run rebuild explanation must not collapse into one fake “build performance insight” result.


## Update 2026-03-20 (310) — request-execution policy contract addition

- Re-read the current `reqwest`, `reqwest-retry`, Tower, `governor`, and `tonic` substrate and confirmed that the sharper missing layer above it is not another middleware bundle, but a **support contract** for replay safety, attempt budgets, admission paths, and execution topology.
- Refreshed evidence with the current `reqwest` retry source, Tower retry/timeout/hedge/order docs, `governor` keyed/direct quota docs, and `tonic` load-shed versus buffered admission behavior.
- Added a new product-plan note, lane-boundary note, four schemas, and five scenario families for scoped retry budgets, layer-order drift, hedged parallel attempts, load-shed versus buffer behavior, and keyed quota waiting with jitter.
- Reaffirmed that “supports retries / timeouts / rate limits” must not collapse into one fake execution-policy story.


## Update 2026-03-20 (308) — feature-surface contract addition

- Re-read the current Cargo feature substrate and confirmed that the sharper missing layer above it is not another feature enumerator or combo runner, but a **support contract** for public feature surface, activation profiles, conflict policy, and unification risk.
- Refreshed evidence with the Cargo features reference, resolver reference, feature-unification unstable docs, `cargo tree` docs, the Rust 2021 resolver guide, RFC 2957, RFC 3143, `cargo-feature-combinations`, `cargo hakari`, and `cargo-hack`.
- Added a new product-plan note, lane-boundary note, four schemas, and three scenario families for grouped optional dependencies, explicit exclusivity policy, and resolver-v2 split risk.
- Reaffirmed that raw feature lists, `all-features` CI success, and workspace-hack speedups must not collapse into one fake “feature support” result.


## 2026-03-20 — FFI boundary contract deepening

- Re-read current official Rust FFI guidance and confirmed that `unsafe extern`, unwind ABI distinctions, panic containment, and callback-after-drop hazards are all still live, explicit parts of the substrate.
- Re-checked current bridge/generator substrate (`uniffi`, UniFFI user guide + async internals, Diplomat, `cxx`, `wit-bindgen`, `cbindgen`) and confirmed the ecosystem now has serious generation/runtime support but still lacks one shared receiver-facing contract for ownership, unwind, callback, and verification-strength truth.
- Judgment: the sharper missing crate is not another generator or per-language shipkit; it is a compact boundary-contract layer that can import existing bridge facts and publish four receipts/reports another team can review.

## 2026-03-20 — choose package-review authority truth over another publish/provenance lane

- Chose to deepen **P-0470** instead of opening another publish-orchestration, provenance, or source-parity lane because Cargo’s packaging substrate now exposes a sharper missing layer: maintainers still need one compact answer for **which surface was authoritative**, **which packaged files were copied or generated**, and **what changed only after unpacking for verification**.
- Treat `cargo package` docs, Cargo changelog entries for deterministic/generated-file timestamps and unpack-time mtime updates, Rust 1.93.1 tarball-retention guidance, and the `.cargo-ok` integrity issue as the main proving-ground facts.


## Update 2026-03-20 (294) — open-table surface / capability / coupling implementation pass

- Chose to deepen **P-0028 open-table-format-kit** instead of opening another adjacent lakehouse engine, metadata-only replay tool, or generic query-engine lane.
- Reconfirmed that the missing value is a **reviewable table-surface / capability-profile / coupling bundle** above today’s Iceberg / Delta / Hudi substrate, not another universal format abstraction.
- Promoted **table-surface truth**, **capability-profile truth**, and **integration-coupling truth** to first-class review objects.
- Added schema/fixture stubs so the lane can model live-versus-static Iceberg providers, Delta-versus-Hudi operation asymmetry, and binding/storage gaps honestly.

## Update 2026-03-20 (293) — lifecycle phase / timeout-aftermath implementation pass

- Chose to deepen **P-0520 Crate Lifecycle Surface Pack Kit** instead of opening another adjacent timeout helper, shutdown supervisor, or runtime-local orchestration lane.
- Reconfirmed that the missing value is a **reviewable lifecycle bundle** above today’s async/runtime substrate, not another cancellation primitive.
- Promoted **shutdown-phase truth** and **timeout-aftermath truth** to first-class review objects alongside activation boundaries, stop semantics, shutdown barriers, escape paths, blocking-work caveats, teardown evidence, and drain recipes.
- Added schema/fixture stubs so the lane can model timeout-dropped waits and runtime-budget exhaustion with surviving blocking work honestly.

## Update 2026-03-20 (292) — lifecycle barrier / escape-path implementation pass

- Chose to deepen **P-0520 Crate Lifecycle Surface Pack Kit** instead of opening another adjacent graceful-shutdown helper, structured-concurrency runtime, or framework-local fix lane.
- Reconfirmed that the missing value is a **reviewable lifecycle bundle** above today’s async/task substrate, not another cancellation primitive.
- Promoted **shutdown-barrier truth** and **escape-path truth** to first-class review objects alongside activation boundaries, stop semantics, blocking-work caveats, teardown evidence, and drain recipes.
- Added schema/fixture stubs so the lane can model upgraded-task escape and pending-stream barrier blockage honestly.

## Update 2026-03-20 (291) — text-input web-path / geometry implementation pass

- Chose to deepen **P-0027 text-input-kit** instead of opening another adjacent GUI toolkit, browser-editing, or accessibility lane.
- Reconfirmed that the missing value is a **reviewable text-input bundle** above event substrate, not another vague widget abstraction.
- Promoted **web-edit-path truth** and **selection-geometry truth** to first-class review objects alongside IME transactions, selection contracts, and backend capability receipts.
- Added fixture/schema stubs so the lane can model EditContext-backed custom editors, offscreen accessibility mirrors, and native key-release leak normalization honestly.

## Update 2026-03-20 (290) — trust-lens implementation pass

- Chose to deepen **P-0017 Trust Lens** instead of opening another adjacent advisory client, registry-policy lane, or score dashboard.
- Reconfirmed that the missing value is a **reviewable dependency-trust bundle**, not a universal score.
- Promoted **identity risk**, **signal-basis provenance**, **assumption registers**, **review debt**, and **policy decisions** to first-class review objects.
- Added fixture/schema stubs so the lane can model campaign-adjacent confusable names, imported audit signals, and unresolved dangerous-effect review debt honestly.


## Update 2026-03-21 (317) — trust-lens notification-channel implementation pass

- Chose to deepen **P-0017 Trust Lens** instead of opening another adjacent advisory client, feed mirror, or registry-policy lane.
- Reconfirmed that the missing value is a **reviewable dependency-trust bundle**, not a universal score and not a notification service by itself.
- Promoted **notification-channel coverage**, **change-class coverage**, and **feed-gap honesty** to first-class review objects alongside identity risk, signal provenance, assumptions, review debt, and policy decisions.
- Added schema/fixture stubs so the lane can model blog-only monitoring, advisory-RSS coverage, and crate-page-security plus Trusted-Publishing posture without flattening them into one fake “trust watch configured” verdict.

## 2026-03-21 — trust watch should now be revisited as a coverage lane, not a score lane

Revisit **P-0017** with four distinctions kept explicit:
1. **current signal visibility** versus ongoing watch coverage,
2. **known-vulnerability surfaces** versus routine malware-removal notice routes,
3. **publish-identity posture** versus advisory/watch posture,
4. **configured feed coverage** versus manual-review-only gaps.

Do not flatten trust watch into crate health, pathfinder, or “we looked at the crate page once.”

## 2026-03-20 — crate health should now be revisited as a contract lane, not a badge lane

Revisit **P-0011** with four distinctions kept explicit:
1. **maintenance window** versus raw release cadence,
2. **succession / backup posture** versus generic bus-factor folklore,
3. **support intent** versus trust/security/publishing signals,
4. **health check** versus task-fit ranking.

Do not flatten crate health into pathfinder, off-ramp, or trust scoring just because all of them import some overlapping registry facts.


## Update 2026-03-20 (287) — crate upgrade-pack omission-register refinement

- Re-read the donor set again and found one more load-bearing move worth stealing into **P-0514**: Overseer kept a first-class `Not Included` surface, and Anonymity kept treating no-publication / hold reasons as part of the public contract rather than as silent absence.
- Landed `omission-register.report.json` so the upgrade pack can say which known hazards, receipts, or local-only context were intentionally left off the public entry surface or export bundle, why, and where the nearest safe fallback lives.
- Added two scenario families: one where a candidate-public pack omits local-only workspace context honestly under an explicit omission register, and one where a known blocking hazard is left out of the public entry surface and the consistency surface fails until the omission is disclosed or the summary is corrected.

## Update 2026-03-20 (286) — crate upgrade-pack surface-authorship refinement

- Re-read the donor set again and found one more load-bearing move worth stealing into **P-0514**: SlopOS kept treating **who authored the bytes** as the practical trust-plane discriminator, and the current upgrade-pack lane still let exact citations blur tool-native evidence, maintainer guidance, reviewer decisions, and archive synthesis.
- Landed `surface-authorship.report.json` so the upgrade pack can say which surfaced artifacts are Cargo-native generated, maintainer-authored, reviewer-authored, archive-derived, or mixed-context rather than forcing readers to infer that from filenames or prose.
- Added two scenario families: one where SemVer output, migration guidance, review decisions, and summaries stay in distinct authorship buckets, and one where a summary claim fails consistency because it markets maintainer guidance as a native import.

---
## Update 2026-03-20 (285) — crate upgrade-pack baseline-state refinement

- Landed `baseline-state.receipt.json` so the upgrade pack can say whether the checked subject was a pinned published release, a reconstructible package extract, a git checkout, or a mutable local workspace, and whether downstream claims remain safe as a release-pair contract or only as a comparison/local note.
- Added two scenario families: one where a published extract keeps the release-pair baseline exact, and one where a dirty partially migrated workspace blocks public release-pair claims until the baseline posture is downgraded or rerun from a pristine subject.

---
- Re-read the donor set again and found one more load-bearing move worth stealing into **P-0514**: Rust-Needs-and-Dreams kept treating replay-versus-copy provenance as its own seam instead of letting copied exports inherit native replay authority.
- Landed `replay-bridge.receipt.json` so the upgrade pack can say whether imported evidence is reached by direct rerun, native-storage rerender, copied attachment inspection, manual reconstruction, or not replayable at all.
- Added two scenario families: one where a stable future-incompat import is replayed from native report id instead of copied into the bundle, and one where native-storage replay posture fails consistency because no actual replay bridge was recorded.

- Re-read the donor set again and found one more load-bearing move worth stealing into **P-0514**: Rust-Needs-and-Dreams kept treating native Cargo session identity as its own seam, and DelayBasin kept insisting that nearby witnesses should not be silently fused just because they are directionally aligned.
- Landed `session-honesty.report.json` so the upgrade pack can say whether imported evidence belongs to one native session, one explicit capture family, a cross-session comparison, or a mixed-session synthesis that requires public warning/disclosure.
- Added two scenario families: one where several imports honestly share one session family, and one where mixed-session synthesis stays useful only because the warning surface and summary claim keep that posture visible.

## Update 2026-03-20 (280) — crate upgrade-pack redaction-receipt refinement

- Landed `redaction.receipt.json` so the upgrade pack can say which local paths, internal package aliases, private registry locators, or raw internal notes were dropped, generalized, rewritten, or moved to private context before a pack claims public-shareable posture.
- Added fixture scenarios for a candidate-public pack whose bounded redaction receipt justifies export and for a public-export claim that fails consistency because it says redaction was applied without shipping any exact receipt.
- Updated the proposal, product plan, fixture README, bundle schema, cross-register input vocabulary, README, INDEX, roadmap, prioritization, and LLM hygiene so future passes keep **public cleanliness** separate from **reviewable sanitization basis**.

## Freshness anchors
- Cargo package/publish docs on shipped-file verification and `include` / `exclude`-controlled package contents
- Cargo manifest docs on public-facing package metadata such as `readme` and `documentation`

## Update 2026-03-20 (279) — crate upgrade-pack durable public-cue refinement

- Landed `durable-cue.report.json` so the upgrade pack can say which blocking warnings, supersession notices, freshness states, deviations, or manual-review boundaries remain durably visible on the exported entry surface instead of surviving only as compact labels or machine-readable registers.
- Added fixture scenarios for a blocking public warning that requires a durable summary cue and for a superseded public pack that keeps its replacement cue visible.
- Updated the proposal, product plan, fixture README, bundle schema, publication-surface role vocabulary, cross-register input vocabulary, README, INDEX, roadmap, prioritization, and LLM hygiene so future passes keep public traceability distinct from durable public visibility.

## Update 2026-03-20 (278) — crate upgrade-pack lane-selection origin refinement

- Re-read the donor set again and found one more load-bearing move worth stealing into **P-0514**: Rust-Needs-and-Dreams kept treating **discovery roots + workspace attachment + package-selection causes** as their own explicit seam, and SlopOS kept showing that once a family gets wide enough it needs one compact map for why adjacent members are in or out instead of relying on ambient structure.
- Landed `lane-selection.receipt.json` so the upgrade pack can say whether the reviewed lane came from a workspace root, explicit manifest path, ambient `workspace.default-members`, explicit `-p`, `--workspace`, or target gating rather than asking reviewers to reconstruct that from command lines.
- Added two scenario families: one where workspace-root `default-members` quietly narrows the lane, and one where explicit package selection widens it past ambient defaults.
- Updated the proposal, product plan, fixture README, bundle schema, cross-register input vocabulary, README, INDEX, roadmap, prioritization, and LLM hygiene so future passes keep package scope, sparse matrix coverage, and lane-selection origin separate.

## Freshness anchors
- Cargo workspace docs on `default-members` and workspace-root package selection
- `cargo metadata` docs including versioned output and `workspace_default_members`
- Cargo target docs on `required-features` gating for bins/tests/examples/benches

## Update 2026-03-20 (277) — crate upgrade-pack public-trace-path pass

- Deepened **P-0514 Crate Upgrade Pack Kit** again after another donor sweep.
- Chose to add `public-trace-path.report` because a public summary can still sound evidence-backed while its promised inspection route is private, broken, or fragment-missing on the exported surface.
- Chose to keep trace misses typed because the remaining honesty gap was no longer generic validation; it was whether the **public trace path itself** actually resolved.
- Reaffirmed that this lane should stay above Cargo-native packaging/export substrate and below generic docs-browser/navigation product layers.

## Update 2026-03-20 (276) — crate upgrade-pack capture-context and coverage-matrix pass

- Deepened **P-0514 Crate Upgrade Pack Kit** again after another donor sweep.
- Chose to add `capture-context.receipt` because imported `cargo fix` / `cargo metadata` / SemVer evidence can still be over-read unless the exact package/target/feature/toolchain/lockfile context remains first-class.
- Chose to add `coverage-matrix.report` because lane-fidelity dimension lists still permit fake whole-lane coverage when required-feature targets, alternate target triples, or profile lanes remain unchecked.
- Reaffirmed that this lane should stay above Cargo-native receipts and below broader diagnosis/release automation/product layers.

## Update 2026-03-19 (264) — crate authority-surface lane deepening

- Chose to deepen **P-0519 Crate Authority Surface Pack Kit** because the archive’s support stack still needed a sharper answer for “where does this power come from, what fallback widens it, and what happens when the host denies it?”
- Reframed the lane around three new first-class review objects: **authority origin**, **fallback order**, and **refusal posture**.
- Added `meta/crate-authority-surface-product-plan-2026-03-19.md` as the refreshed implementation-ready sketch for **P-0519**.
- Added three new schemas and four new scenario families so the archive can express explicit capability preference, silent project-dir denial fallback, cache-root priority inversion, and root-crate ownership of `getrandom` backend choice.
- Updated README, INDEX, known-existing, roadmap, prioritization, decision log, epic portfolio, proposal text, and LLM hygiene so this lane is easier to rediscover and harder to collapse back into vague “better sandboxing”.

## 2026-03-19 — crate observability support refresh

- Rust vision doc: crates still need supportive interfaces rather than only elegant abstractions.
- 2025 State of Rust survey: docs and code remain the main learning surfaces; debugging/resource-usage remain visible pains.
- Tokio tracing docs: `tracing` still routes into OpenTelemetry, Tokio Console, logging, and profiling.
- `EnvFilter` docs: filters may be global or per-layer; regex field matching is on by default and should be disabled for potentially untrusted input.
- `console-subscriber` docs: Tokio console route still requires Tokio `tracing` support and `tokio_unstable` on the Tokio path.
- `tracing-opentelemetry` docs: bridge exports traces and metrics but not logs.
- OpenTelemetry Rust docs: traces, metrics, and logs are still beta in Rust.
- OpenTelemetry Rust libraries docs: docs team still does not know of any Rust library with native OTel integrated by default.
- OpenTelemetry schema docs: semantic drift is tied to schema URLs.
- OpenTelemetry sensitive-data docs: implementers remain responsible for reviewing what fields instrumentation emits.

Main synthesis: the sharper gap is now a **crate-authored observability contract** above signal emission, filter posture, console/runtime activation, bridge routes, schema posture, and sensitivity boundaries.

## Update 2026-03-19 (262) — crate performance-envelope deepening pass

Questions asked:
- what is the sharpest remaining gap inside P-0517 now that Criterion, Iai-Callgrind, Divan, CodSpeed compatibility layers, and nextest all make different kinds of performance evidence easier to obtain?
- what should the crate provide other people beyond benchmark outputs and charts?
- what distinction is still easy for maintainers to blur in ways that would mislead downstream users?

Conclusions:
- the missing value is not another benchmark harness but a receiver-facing contract for **which number rules**, **what kind of run produced it**, **what workload it stands for**, and **how much trust it deserves**.
- cargo-nextest’s current Criterion integration makes a crucial boundary explicit: benchmark targets can be exercised in a way that verifies compilation and panic freedom without producing trustworthy performance measurement.
- CodSpeed compatibility layers make another crucial boundary explicit: “the suite ran” is not always the same claim as “a real measurement happened in this environment.”
- Divan’s allocation profiling makes a third boundary explicit: a metric can be exactly the right public promise while simultaneously perturbing supporting timing measurements.

Repository changes:
- Added `entries/2026-03-19-262.md`.
- Added `meta/frontier-salience-2026-03-19-82.md`.
- Added `meta/crate-performance-envelope-product-plan-2026-03-19.md`.
- Added `fixtures/crate-performance-envelope-pack-kit/README.md`.
- Added `execution-intent.report` and `workload-lineage.receipt` schemas plus scenario families for nextest Criterion test mode, custom-profile drift, CodSpeed unknown-environment runs, captured-trace workload authority, and Divan allocation-budget metric authority.
- Updated **P-0517** and the archive’s portfolio/meta docs to treat execution intent and workload lineage as first-class review objects.

## 2026-03-19 — Crate example-surface deepening

Re-checked the current **P-0524** lane against live Rust/docs.rs ecosystem evidence.

Fresh evidence reviewed:
- Rust vision doc (supportive interfaces from crates)
- 2025 State of Rust survey (docs + code remain the main learning surfaces)
- Rust API Guidelines documentation chapter
- Cargo targets docs (`examples/` as first-class targets compiled by `cargo test`)
- rustdoc documentation tests
- rustdoc scraped examples
- Cargo unstable `doc-scrape-examples` docs
- docs.rs metadata and builds pages
- `trycmd`, `term_transcript`, `mdBook`, and `cargo-generate` docs

Main conclusions:

- the archive already had the example lane and schema vocabulary,
- but it still needed a fresher implementation pass that made **official quickstarts**, **prerequisite lineage**, **docs/example linkage**, **scenario coverage**, and **witnessed first success** concrete,
- and the live ecosystem evidence is now strong enough that the missing value is clearly the **contract layer above substrate** rather than another docs or testing backend.

Changes made:

- Added `meta/crate-example-surface-product-plan-2026-03-19.md` as the current implementation-ready sketch for **P-0524**.
- Added a root fixture README plus concrete example artifacts for CLI quickstarts, loopback client starts, hidden prerequisite origins, guide/example linkage drift, dynamic normalization boundaries, proc-macro starter outputs, embedded environment honesty, and scenario gaps where only credentialed paths exist.
- Updated **P-0524**, the frontier ranking, known-existing notes, and archive meta docs so future passes do not drift back into vague “better docs/examples” language.

## Update 2026-03-19 (256) — crate diagnosis-support implementation pass

Researched current Rust diagnosis substrate again before making another archive move.
Main inputs this round:

- Rust vision-doc work on **supportive interfaces from crates**
- 2025 State of Rust survey results
- Rust debugging survey 2026
- Tokio tracing guidance
- `console-subscriber` compatibility/Builder docs
- `tokio-metrics` runtime interval docs
- `miette::Diagnostic` / `JSONReportHandler` docs
- `tracing-error::SpanTrace` docs

Main conclusions:

- the archive already had the diagnosis lane and schema vocabulary,
- but it still needed a fresher implementation pass that made **instrumentation honesty** and **safe capture boundaries** concrete,
- and the live ecosystem evidence is now strong enough that the missing value is clearly the **contract layer above substrate** rather than another diagnostics backend.

Changes made:

- Added `meta/crate-diagnosis-surface-product-plan-2026-03-19.md` as the current implementation-ready sketch for **P-0525**.
- Added example artifacts for retry-storm triage order, queue-growth signal mapping, safe CLI support capture, console-path mismatch detection, and secret-safe bundle evaluation.
- Updated **P-0525**, the frontier ranking, known-existing notes, and archive meta docs so future passes do not drift back into vague “debugging support” language.

## 2026-03-19 — Public API readiness deepening

- Reviewed the current P-0483 state and concluded that the proposal was still too analyzer-shaped.
- Confirmed that the sharper missing layer is the **joined public-release review artifact** above semver/public-API/public-dependency/docs substrate.
- Added `meta/public-api-readiness-product-plan-2026-03-19.md` as the implementation-ready v0.1 sketch for **P-0483**.
- Added `meta/public-api-readiness-lanes-2026-03-19.md` so semver evidence, public-dependency boundary work, item-level availability truth, and joined release readiness stay separate.
- Added schema fixtures and scenario families for quiet public-boundary drift, public-docs regressions, and stale waiver posture.
- Tightened **P-0483** so the crate’s center of gravity is now explicit release-review truth rather than a vague API-quality dashboard.
- Performed a small hygiene fix by correcting recent frontier snapshots that had drifted into the wrong docs.rs parity proposal id.

## 2026-03-19 refresh — crate off-ramp productization (253)

### Fresh evidence checked
- 2025 State of Rust survey: documentation remains the preferred canonical reference and code study follows close behind; maintainers support also ticked upward as an ecosystem concern. https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- crates.io development update: crate pages now have a Security tab with RustSec-backed affected version ranges. https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io malicious-crate policy update: RustSec advisories remain the always-on communication path for removed malware crates. https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- rustc deprecated-lint docs: deprecated surfaces should usually include what to use instead. https://doc.rust-lang.org/rustc/lints/listing/warn-by-default.html#deprecated
- Cargo SemVer guidance + yank/update docs still make deprecation and yanked-version handling explicit without defining a successor plan. https://doc.rust-lang.org/cargo/reference/semver.html ; https://doc.rust-lang.org/cargo/commands/cargo-yank.html ; https://doc.rust-lang.org/cargo/commands/cargo-update.html
- RFC 3416 keeps feature deprecation and documentation structure explicitly in scope. https://rust-lang.github.io/rfcs/3416-feature-metadata.html
- docs.rs now exposes real redirect-crate patterns with explicit migration steps (`sello-crypto` → `txgate-crypto`). https://docs.rs/crate/sello-crypto/latest

### Main synthesis
The gap is no longer “Rust needs better deprecation notes.”
The sharper gap is a **crate-authored off-ramp contract** above warning/advisory/yank substrate:

- what exactly is being sunset,
- what successor class really applies,
- whether a shim or last-safe pin is only temporary,
- and what migration recipe was actually checked.

### Archive actions
- Added `meta/crate-offramp-product-plan-2026-03-19.md`.
- Added a root fixture README plus scenario example artifacts for rename-shim, security stopgap, successor split, and no-successor cases.
- Updated `proposals/crate-offramp-pack-kit.md` with first-class review objects, workspace split, and command surface.
- Added `entries/2026-03-19-253.md` and `meta/frontier-salience-2026-03-19-73.md`.
- Updated README/index/prioritization/portfolio/hygiene files so future passes do not flatten off-ramp work back into vague maintenance metadata.

### Discipline update
Do **not** let future passes say “there is a deprecation note / RustSec advisory / redirect crate, therefore the sunset story is solved.”
The archive now treats **successor intent**, **stopgap horizon**, and **recipe witness** as distinct review objects.

# Added 2026-03-19 (252)

### Desktop shipping / release-contract substrate
- `dist` / `cargo-dist` docs: planning, building, hosting, publishing, announcing, installers, and machine-readable manifests are already real substrate. https://axodotdev.github.io/cargo-dist/book/
- `cargo-packager` docs.rs: packaging as a Rust library / cargo subcommand plus signing-oriented APIs (`package_and_sign`, `sign_outputs`). https://docs.rs/cargo-packager/latest/cargo_packager/
- CrabNebula Packager docs: macOS/Windows/Linux package families and compatible updater flow. https://docs.crabnebula.dev/packager/
- Tauri distribution docs: platform-specific bundling, code signing, notarization, and store/direct-download routes remain distinct. https://v2.tauri.app/distribute/
- Tauri updater docs: updater signatures are mandatory and key continuity matters operationally. https://v2.tauri.app/plugin/updater/
- Rust `rustc` codegen docs: `split-debuginfo` and `strip` behavior is platform-specific and can materially change symbol-sidecar reality. https://doc.rust-lang.org/rustc/codegen-options/index.html
- Cargo profiles docs: Cargo and `rustc` can have different `split-debuginfo` defaults, reinforcing that symbol-handoff truth is not inferable from “release build succeeded.” https://doc.rust-lang.org/cargo/reference/profiles.html

**Conclusion:** the gap is **not** “Rust has no desktop release tooling”, **not** “we just need another packager”, and **not** “an updater alone solves desktop shipping.” The sharper gap is a **desktop release/update/support contract** above existing packagers, updater substrate, and debug-symbol behaviors.

## Added 2026-03-19 (250)

### text-input productization / adjacent prior art
- winit IME controls and platform notes: https://docs.rs/winit/latest/winit/window/struct.Window.html
- winit `WindowEvent::Ime` docs: https://docs.rs/winit/latest/winit/event/enum.WindowEvent.html
- current Windows overlap bug while IME is allowed: https://github.com/rust-windowing/winit/issues/4508
- current Web/WASM IME issue (canvas limitation + hidden-input workaround): https://github.com/rust-windowing/winit/issues/4424
- Parley docs (rich text layout substrate): https://docs.rs/parley/latest/parley/
- cosmic-text docs (layout/editing substrate): https://docs.rs/cosmic-text/latest/cosmic_text/
- AccessKit docs (text position / selection vocabulary): https://docs.rs/accesskit/latest/accesskit/
- 2025 survey of Rust GUI libraries (field signal that text-input/accessibility polish still varies): https://www.boringcactus.com/2025/04/13/2025-survey-of-rust-gui-libraries.html
- Slint issue showing text-input accessibility exposure remains difficult: https://github.com/slint-ui/slint/issues/2895
- 2025 State of Rust survey (current ecosystem/productivity context): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

**Conclusion:** the gap is **not** “Rust lacks text layout/editing substrate”, **not** “`winit` already solved text input everywhere”, and **not** “an accessibility tree alone settles text semantics.” The sharper remaining gap is a **shared IME-transaction / selection-contract / backend-capability layer** above current substrate.

## Added 2026-03-19 (249)

### UI accessibility doctor productization / adjacent prior art
- AccessKit overview and current Rust integrations: https://accesskit.dev/
- accesskit_winit adapter docs (authoring-side tree exposed through native platform APIs): https://docs.rs/crate/accesskit_winit/latest
- egui docs (`accesskit` feature flag): https://docs.rs/egui/latest/egui/
- kittest docs (AccessKit-powered framework-agnostic GUI testing): https://docs.rs/kittest/latest/kittest/
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- ACT Rules Format 1.1: https://www.w3.org/TR/act-rules-format/
- ACT overview and audience/intent: https://www.w3.org/WAI/standards-guidelines/act/
- Rust vision work (“double down on extensibility”, supportive interfaces from crates, and ecosystem navigation): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (debugging/productivity pain and docs/code as main learning surfaces): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- 2025 survey of Rust GUI libraries (field signal that GUI polish/accessibility maturity still varies widely): https://www.boringcactus.com/2025/04/13/2025-survey-of-rust-gui-libraries.html
- current winit Web/WASM IME issue (important adjacent boundary showing why text-input substrate and a11y doctoring should stay distinct): https://github.com/rust-windowing/winit/issues/4424

**Conclusion:** the gap is **not** “Rust lacks accessibility substrate”, **not** “testing alone solves accessibility quality”, and **not** “an emitted tree proves compliance.” The sharper remaining gap is an **AccessKit-first semantic doctor / rule-authority / baseline-drift layer** above current toolkit and testing substrate.

## Update 2026-03-18 (239) — Rust Android Mobile Kit deepening pass

### Sources consulted
- `cargo-ndk` README / command surface
- UniFFI Kotlin bindings overview
- Android NDK native-library packaging guidance
- Android JNI tips / performance guidance
- Android 16 KB page-size guidance
- `cargo-apk` repository/docs
- `cargo-mobile2` repository/docs
- Rust release notes / Android NDK floor note

### Kept together
- the distinction between **target/NDK plumbing** and a **reviewable Android library shipping contract**
- the distinction between **binding generation** and **final packaging/distribution truth**
- the distinction between **built ABI coverage** and **load-readiness inside a final app graph**
- the fact that Android policy changes such as **16 KB page-size support** can make native-library readiness part of release review rather than an invisible ops detail

### Result
- Added `meta/frontier-salience-2026-03-18-59.md` to rank Android library shipping more clearly as a Band B shipping-kit opportunity.
- Added `meta/rust-android-mobile-kit-product-plan-2026-03-18.md` as the implementation-ready `0.1` sketch for **P-0168**.
- Added `abi-coverage.report`, `load-doctor.report`, and `page-size-compat.report` schemas plus three new fixture families for AAR native-library collision risk, 16 KB page-size release gating, and UniFFI-bindings-without-packaging-honesty drift.
- Updated **P-0168** so the crate’s center of gravity is now explicit Android library shipping truth, not a vague “mobile tooling” idea.

### Freshness anchors
- Re-check Android packaging guidance before restating AAR/native-library collision rules.
- Re-check page-size guidance before repeating exact release-policy claims later on.
- Re-check Rust release notes before assuming the same Android NDK floor.
- Re-check `cargo-ndk`, UniFFI, `cargo-apk`, and `cargo-mobile2` before flattening them into one fake Android stack.

### Common false gap patterns from this pass
1. “UniFFI generated Kotlin bindings, therefore Android shipping is solved.”
2. “`cargo-ndk` exists, therefore teams already have a reviewable Android shipping contract.”
3. “We built one `.so`, therefore ABI coverage and load-readiness are both proven.”
4. “The AAR was produced, therefore native-library collision and page-size readiness are someone else’s problem.”

## Update 2026-03-17 (236) — crate persistence-surface deepening pass

### Sources consulted
- Rust vision-doc work on supportive interfaces from crates
- 2025 State of Rust survey results
- `std::fs::File` docs
- `std::fs::rename` docs
- `tempfile::NamedTempFile::persist` docs
- `atomic-write-file` docs
- Tokio `fs` docs
- docs for `serde-reflection`, Postcard, `revision`, and redb

### Kept together
- the distinction between **compatibility windows** and **compatibility authority**
- the distinction between **no-intermediate-state replacement** and **durable local publication**
- the distinction between **declared recovery paths** and **witnessed recovery/repair evidence**
- the fact that async file wrappers are useful substrate but not themselves a receiver-facing persistence contract

### Result
- Added `meta/frontier-salience-2026-03-17-56.md` to raise persistence-support salience after separating authority, atomicity, and witness questions more clearly.
- Added `compatibility-authority.policy`, `atomicity-scope.report`, and `recovery-witness.receipt` schemas to the persistence-surface fixture pack.
- Added fixture families for atomicity-vs-durability drift, stable-wire-authority honesty, and declared-but-unwitnessed recovery paths.
- Updated **P-0522** and its product plan so the crate’s center of gravity is now explicit trusted-compatibility, exact atomicity scope, and witnessed recovery truth.

### Freshness anchors
- Re-check file-write and temp-file docs before restating what “atomic write” really guarantees.
- Re-check Tokio `fs` docs before implying async file APIs create a new persistence model.
- Re-check Postcard, `serde-reflection`, `revision`, and redb docs before flattening their very different compatibility/recovery guarantees into one generic “stable storage” story.

### Common false gap patterns from this pass
1. “We use temp-file replacement, therefore the save is durable after power loss.”
2. “One surface uses Postcard, therefore all persisted bytes are stable.”
3. “The storage engine documents repair, therefore the crate has a current recovery witness.”
4. “Tokio `fs` changes the async story, therefore it changes the persistence contract by itself.”

## Update 2026-03-17 (234) — crate example-surface deepening pass

### Sources consulted
- Rust vision-doc work on supportive interfaces from crates
- 2025 State of Rust survey results
- Rust API Guidelines documentation chapter
- Cargo targets / examples docs
- rustdoc scraped examples book page
- docs.rs metadata docs
- docs.rs builds docs
- docs for `trycmd`, `term-transcript`, `mdBook`, and `cargo-generate`

### Kept together
- the distinction between **official quickstarts** and adjacent tooling for templates, tutorial books, transcript rendering, or docs hosting
- the fact that example-heavy crates can still lack an honest first-success path for a major adoption scenario
- the need for **prerequisite-origin receipts** so hidden feature flags, docs.rs metadata, or guide-only steps do not get rewritten into “the README explained it”
- the need for **success-witness receipts** so scraped examples and green local builds do not masquerade as official witnessed starts
- the need for **scenario-coverage reports** so “there are examples” does not get mistaken for “there is an official quickstart for the way you want to adopt this crate”

### Result
- Added `meta/frontier-salience-2026-03-17-54.md` to rank first-success support more clearly against the surrounding failure-path lanes.
- Added `prerequisite-origin.receipt`, `success-witness.receipt`, and `scenario-coverage.report` schemas to the example-surface fixture pack.
- Added fixture families for hidden feature/prerequisite origins, scraped-example presence without official witnessed success, and credentialed-service-only paths that still need scenario honesty.
- Updated **P-0524** and its product plan so the crate’s center of gravity is now explicit quickstart truth, not just example discovery.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness priorities later on.
- Re-check Cargo / rustdoc / docs.rs example-related docs before restating how much example support is already present upstream.
- Re-check `trycmd`, `term-transcript`, `mdBook`, and `cargo-generate` before flattening them into one fake onboarding stack.

### Common false gap patterns from this pass
1. “A green README snippet is already an official quickstart” when prerequisite origin and witnessed success still matter.
2. “Scraped examples solve this” when linkage and official first-success support are different layers.
3. “A credentialed demo is good enough as the only getting-started path” when scenario coverage still needs an honest local/loopback/manual-review answer.
4. “Templates or books solve onboarding” when scaffolding a new project and validating a chosen crate’s first-success path are different jobs.

- Revisited **P-0525 Crate Diagnosis Surface Pack Kit** after the guidance/runtime-handoff passes to keep the support-surface cluster from collapsing into one fake DX lane.
- Added `meta/crate-support-surface-boundaries-2026-03-17.md` as a dedicated amnesia resistor for guidance vs runtime handoff vs observability vs examples vs diagnosis.
- Added `symptom-class.policy`, `triage-origin.receipt`, and `bundle-safety.report` to make diagnosis support more reviewable.
- Added scenario families for console-without-instrumentation, vague timeout buckets, and secret-leaking support bundles.

- `entries/2026-03-17-232.md` — crate guidance-pack planning sharpened into an implementation-ready v0.1 shape
- `meta/crate-guidance-pack-product-plan-2026-03-17.md` — concrete command/artifact/adoption plan for P-0512
- `fixtures/crate-guidance-pack-kit/guidance-authority.policy.schema.json` + `recovery-origin.receipt.schema.json` + `recipe-fidelity.report.schema.json` — schemas for guidance-authority meaning, recovery provenance, and checked recipe fidelity
- `fixtures/crate-guidance-pack-kit/compile_fail_doctest_catches_failure_but_not_message_drift/` + `do_not_recommend_hides_blanket_impl_but_recipe_missing/` + `proc_macro_diagnostic_url_points_to_stale_syntax/` — new fixture families for docs-vs-message drift, suppressed-bad-hint without replacement path, and proc-macro anchor drift

## 2026-03-17 refinement — crate guidance-pack lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0512 Crate Guidance Pack Kit** into a more buildable shape.

### Main judgment
- Treat `meta/crate-guidance-pack-product-plan-2026-03-17.md` as the working build sketch for **P-0512**.
- The key new planning detail is that a guidance-pack crate should publish explicit **guidance-authority policy**, **recovery-origin receipts**, and **recipe-fidelity reports** rather than leaving compile-time help scattered across attributes, compile-fail tests, docs examples, and issue answers.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s compiler diagnostic hooks, rustdoc examples, and compile-fail harness substrate.

### What to keep separate
- Keep **P-0512** separate from task-first crate choice (**P-0509**).
- Keep **P-0512** separate from generic diagnostic rendering.
- Keep **P-0512** separate from docs portals and tutorial systems.
- Keep **P-0512** separate from runtime failure handoff (**P-0513**).

### Preferred proving grounds
- trait-heavy crates using `on_unimplemented` and `do_not_recommend`
- feature-rich crates whose smallest good path is narrower than the advertised docs surface
- proc-macro crates that need something better than panic text
- crates relying on rustdoc `compile_fail` examples that do not by themselves prove message fidelity


- `entries/2026-03-17-231.md` — crate runtime-handoff planning sharpened into an implementation-ready v0.1 shape
- `meta/crate-runtime-handoff-product-plan-2026-03-17.md` — concrete command/artifact/adoption plan for P-0513
- `fixtures/crate-runtime-handoff-pack-kit/capture-exactness.policy.schema.json` + `share-safety.receipt.schema.json` + `handoff-fidelity.report.schema.json` — schemas for runtime-capture exactness, safe-to-share classification, and post-failure bundle fidelity
- `fixtures/crate-runtime-handoff-pack-kit/error_stack_attachment_secret_needs_hash_redaction/` + `spantrace_declared_but_error_layer_missing/` + `panic_hook_present_but_report_bundle_path_missing/` — new fixture families for attachment redaction, unsupported async-context drift, and panic-hook artifact-path honesty

## 2026-03-17 refinement — crate runtime-handoff lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0513 Crate Runtime Handoff Pack Kit** into a more buildable shape.

### Main judgment
- Treat `meta/crate-runtime-handoff-product-plan-2026-03-17.md` as the working build sketch for **P-0513**.
- The key new planning detail is that a runtime-handoff crate should publish explicit **capture-exactness policy**, **share-safety receipts**, and **handoff-fidelity reports** rather than leaving post-failure truth buried across panic hooks, ad hoc log dumps, report files, and issue-template prose.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s error, panic, attachment, and span-context substrate.

### What to keep separate
- Keep **P-0513** separate from compile-time guidance (**P-0512**).
- Keep **P-0513** separate from generic report rendering.
- Keep **P-0513** separate from tracing / observability platforms.
- Keep **P-0513** separate from hosted crash collectors or domain-specific incident bundles.

### Preferred proving grounds
- CLI tools with custom panic hooks or user-submittable report files
- async services where span traces matter more than raw executor stacks
- library crates using attachment-heavy runtime errors
- privacy-sensitive applications where config/env/user identifiers must not leak into public support bundles
- framework crates whose runtime support story still lives mostly in issue comments


## 2026-03-17 refinement — crate configuration/setup-scenario productization pass (227)

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Cargo features docs
- Cargo targets docs (`required-features`)
- Cargo external tools docs
- Cargo metadata docs
- docs.rs metadata docs
- docs.rs build docs
- RFC 3416 feature metadata
- Cargo 1.93 development-cycle post
- `document-features` docs
- `cargo-feature-combinations` docs
- `cargo-hack` crate page

### Kept together
- the distinction between **named setup scenarios** and raw feature/config substrate
- the need to keep **docs.rs surface drift** separate from ordinary default-scenario truth
- the need to keep **backend-choice policy** separate from “it compiles if you turn everything on” facts
- the need to keep **matrix fidelity** explicit instead of pretending one green CI job proves the whole scenario surface

### Result
- Added `meta/crate-configuration-scenario-product-plan-2026-03-17.md` as the working build sketch for **P-0516**.
- Added schema artifacts for **scenario-class policy**, **config-origin receipts**, and **matrix-fidelity reports**.
- Added three fixture families that force the lane to stay honest about docs.rs/default drift, backend-choice policy, and `no_std`-vs-example coverage.
- Updated repo-memory files so future passes do not rediscover this seam as “better feature docs” or “just run powersets harder”.

### Freshness anchors
- Re-check Cargo target/docs.rs docs before repeating the same `required-features` or hosted-build assumptions later on.
- Re-check feature-metadata progress before assuming RFC 3416 remains equally incomplete later on.
- Re-check the current feature-combination tooling ecosystem before claiming the same support gap later on.

### Common false gap patterns from this pass
1. “`document-features` already solves setup support” when it mostly solves feature documentation rather than scenario policy or recipe truth.
2. “powerset tools already solve setup support” when they mostly solve execution coverage rather than naming the official receiver-facing lanes.
3. “docs.rs shows the API, so the scenario is real” when docs.rs configuration may widen the surface beyond the ordinary recommended path.
4. “one green `no_std` build proves the whole lane” when examples/tests/docs can still skew `std` or host-only.


## 2026-03-17 — memory-observability productization note

The memory-observability lane is worth treating as a real crate candidate, but only if the archive keeps it above current tooling rather than pretending Rust lacks profilers or allocator introspection.

Current substrate check:
- `leaktracer` already demonstrates low-friction allocator interception and per-function allocation accounting.
- `dhat` already demonstrates a scoped profiler lifetime and file-emitting heap profile workflow.
- `tikv-jemalloc-ctl` already demonstrates allocator-side stats / control / dump substrate.
- `jemalloc_pprof` already demonstrates allocator heap profiling that can be exported into pprof-compatible artifacts.

Implication:
- The missing value is now a reviewable artifact layer for **capture scope**, **symbolization fidelity**, **backend capability**, and **regression gating**.
- Do **not** collapse this lane into resource-surface support contracts, performance-envelope honesty, allocator choice/tuning, or full observability platforms.
- Good proving grounds are RSS regressions with stable alloc-count totals, scoped profiling that misses a later phase, and systems where allocator stats exist but callsite attribution does not.

## Added 2026-03-17 (224)

### Crate ecosystem pathfinder / decision-pack productization refinement
- The Rust vision-doc work keeps framing ecosystem supportiveness and crate discoverability as part of the real product experience of Rust, not a side quest. https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The 2025 State of Rust survey says documentation and code remain the main learning surfaces, which means crate choice still often happens by hand across docs/READMEs rather than through a stronger task-oriented tool. https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2024 project-goals notes explicitly call out spotty ecosystem support for older technologies plus the need for companies to assemble learning workflows from many pieces. https://rust-lang.github.io/rust-project-goals/2024h2/notes.html
- `cargo search` still documents textual search plus description output, and `cargo add` still optimizes for adding a known dependency rather than choosing among plausible families. https://doc.rust-lang.org/cargo/commands/cargo-search.html https://doc.rust-lang.org/cargo/commands/cargo-add.html
- Cargo manifest metadata still gives only small keyword/category slots, which are useful but too weak to encode task roles, lock-in, or reviewable starter-set judgments. https://doc.rust-lang.org/cargo/reference/manifest.html
- The crates.io search discussion makes it explicit that better search ordering is non-trivial and that current relevance behavior still does not guarantee newcomer-friendly task discovery. https://github.com/rust-lang/crates.io/discussions/9325
- The historical Rust Platform follow-up remains a useful warning that global blessing / metapackage answers can create real drawbacks even when the discoverability problem is genuine. https://internals.rust-lang.org/t/follow-up-the-rust-platform/3782

**Conclusion:** the gap is **not** “Rust lacks a registry”, **not** “a better popularity score would solve crate choice”, and **not** “the answer is one blessed ecosystem snapshot.” The sharper gap is a **task-oriented decision-pack layer** with explicit task profiles, role coverage, interop/lock-in analysis, evidence-weight policy, starter-set locks, and honest manual-review boundaries.


## Added 2026-03-17 (221)

### Crate lifecycle-surface productization refinement
- Tokio shutdown guide frames graceful shutdown as deciding when to stop, telling tasks to stop, and waiting for them to stop. https://tokio.rs/tokio/topics/shutdown
- `TaskTracker` docs explicitly position it alongside `CancellationToken` for waiting until tasks actually exit. https://docs.rs/tokio-util/latest/tokio_util/task/task_tracker/struct.TaskTracker.html
- `JoinHandle` docs say dropping the handle detaches the task, and `AbortHandle` docs say dropping the abort handle does not abort the task. https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html https://docs.rs/tokio/latest/tokio/task/struct.AbortHandle.html
- `spawn_blocking` docs say running blocking tasks cannot be aborted once started. https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html
- Tokio `select!` docs define cancellation safety as “drop and recreate without losing progress”, while `AsyncWriteExt` docs distinguish cancel-safe writes from `write_all`; `AsyncWrite::shutdown` docs say shutdown is the hook for graceful protocol teardown. https://docs.rs/tokio/latest/tokio/macro.select.html https://docs.rs/tokio/latest/tokio/io/trait.AsyncWriteExt.html https://docs.rs/tokio/latest/tokio/io/trait.AsyncWrite.html
- `async_shutdown`, `tokio-graceful-shutdown`, `task_scope`, and `moro` still look like useful substrate or adjacent experiments rather than a crate-authored downstream lifecycle contract. https://docs.rs/async-shutdown/latest/async_shutdown/ https://docs.rs/tokio-graceful-shutdown/latest/tokio_graceful_shutdown/ https://docs.rs/task_scope/latest/task_scope/ https://docs.rs/crate/moro/0.4.0

**Conclusion:** the gap is still **not** “Rust lacks async lifecycle primitives.” The sharper gap is a **crate-authored lifecycle-surface / activation-boundary / stop-semantics / teardown-evidence / diff layer** above today’s shutdown, cancellation, and structured-concurrency substrate.


## Update 2026-03-17 (217) — crate persistence-surface productization pass

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- `std::fs::File` docs
- `std::fs::rename` docs
- `tempfile::NamedTempFile::persist` docs
- `atomic-write-file` docs
- Serde container attributes
- Serde field attributes
- `serde-reflection` docs
- Postcard docs
- redb database docs

### Kept together
- the distinction between **crate-authored persistence contracts** and adjacent upgrade packs, setup scenarios, lifecycle/resource/authority surfaces, serializers, embedded stores, and migration frameworks
- the fact that file/serde/storage substrate is already real, which means the missing value is now the reviewable contract above it
- the need to keep **contract level**, **write path**, and **failure model** explicit instead of flattening them into one vague “persistence is supported” claim
- the need to deepen **P-0522** before inventing another neighboring durability/storage-support crate lane too early

### Result
- Added `meta/crate-persistence-surface-product-plan-2026-03-17.md` as the implementation-ready v0.1 sketch for **P-0522**.
- Added `surface-contract.policy`, `write-path.receipt`, and `failure-model.profile` schemas plus three new persistence fixture families for atomic-replace durability boundaries, Serde unknown-field narrowing, and recovery-vs-repair honesty.
- Updated **P-0522** with tighter prior-art boundaries, richer artifacts, and a direct link to the new product plan.
- Updated repo-memory files so future passes do not mistake atomic replace helpers, stable wire formats, or crash-recovery substrate for the same missing crate.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness priorities later on.
- Re-check `std::fs::File`, `std::fs::rename`, and `tempfile` docs before restating write/durability semantics later on.
- Re-check Postcard, redb, and relevant serde docs before repeating the same compatibility/recovery substrate assumptions later on.

### Common false gap patterns from this pass
1. “Rust needs another serializer or embedded store” when the sharper gap is a **crate-authored persistence contract**.
2. “Atomic replace is enough” when replacement semantics and durability boundary are different jobs.
3. “Serde-based means compatible” when rename/default/unknown-field policy still needs explicit review.
4. “Crash safe” when the honest result may differ across unclean shutdown, power loss, and external corruption.

## Update 2026-03-17 (216) — docs.rs parity productization pass

### Sources consulted
- docs.rs builds page
- docs.rs metadata page
- docs.rs about page
- docs.rs rustdoc JSON page
- docs.rs default-target change announcement
- docs.rs repository README
- `cargo docs-rs` README
- 2025 State of Rust survey results

### Kept together
- the distinction between **docs.rs parity / issue bundles** and adjacent toolchain support contracts, docs rendering/hosting, item-level cfg availability, and rustdoc-coverage work
- the fact that docs.rs already exposes real metadata, build-limit, and builder-reproduction substrate, which means the missing value is now the explanation layer above it
- the need to keep **fidelity class**, **hosted-build import**, and **drift-cause classification** explicit instead of burying them in one flat “docs failed” result
- the need to deepen **P-0472** before inventing another neighboring docs-support crate lane too early

### Result
- Added `meta/docsrs-build-parity-product-plan-2026-03-17.md` as the implementation-ready v0.1 sketch for **P-0472**.
- Added `preflight-fidelity.report`, `hosted-build-import.receipt`, and `drift-cause.report` schemas plus three new docs.rs parity fixture families for network-policy drift, missing native dependencies, and hosted-log truncation.
- Updated **P-0472** with tighter artifacts, richer boundaries, and a direct link to the new product plan.
- Updated repo-memory files so future passes do not mistake local preflight, builder reproduction, hosted summaries, or rustdoc JSON availability for the same kind of evidence.

### Freshness anchors
- Re-check docs.rs builds and metadata pages before repeating the same nightly, sandbox, and target-default assumptions later on.
- Re-check the docs.rs about/rustdoc JSON pages before restating hosted summary or JSON-availability behavior later on.
- Re-check the docs.rs default-target announcement before assuming the same default-target posture later on.

### Common false gap patterns from this pass
1. “`cargo docs-rs` already solves docs.rs support” when the sharper gap is a **fidelity / drift-cause / issue-bundle layer**.
2. “Hosted docs failed, so the crate needs another docs runner” when the sharper value is a compact explanation artifact above existing runners.
3. “The local run was green, so hosted drift must be a docs.rs bug” when network policy, read-only paths, missing native deps, target count, or log truncation may explain the difference.
4. “rustdoc JSON hosting solves this” when JSON availability and HTML/build parity are different jobs.

## Update 2026-03-17 (215) — debuggability-support productization pass

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Rust debugging survey 2026
- Cargo profiles docs
- `rustc` codegen options docs
- Rust reference docs for `#[debugger_visualizer]`
- Cargo unstable docs for `trim-paths`
- `rustc` command-line docs for `--remap-path-prefix`
- Cargo changelog
- Build Dir Layout v2 call-for-testing post

### Kept together
- the distinction between **broad debuggability support contracts** and adjacent source-lookup diagnosis, visualizer compatibility, runtime troubleshooting, and crash backends
- the fact that Cargo/rustc/debugger-visualizer substrate is already real, which means the missing value is now the reviewable contract above it
- the need to keep **support class**, **artifact handoff**, and **source-lookup impact** explicit instead of treating them as trivia hidden in profiles or release scripts
- the need to deepen **P-0486** before inventing another neighboring debug-support crate lane too early

### Result
- Added `meta/debuggability-support-product-plan-2026-03-17.md` as the implementation-ready v0.1 sketch for **P-0486**.
- Added `support-class.policy`, `artifact-handoff.manifest`, and `source-lookup-impact.report` schemas plus three new debug-support fixture families for implicit strip drift, build-dir relocation, and path-hygiene/source-lookup boundaries.
- Updated **P-0486** with tighter artifacts, richer boundaries, and a direct link to the new product plan.
- Updated repo-memory files so future passes do not mistake debugger substrate, symbol files, or path hygiene for the same missing crate.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness priorities later on.
- Re-check Cargo profile docs and changelog before restating `debug` / `split-debuginfo` / `strip` behavior later on.
- Re-check Build Dir Layout v2 before assuming the same build-dir/target-dir migration posture later on.
- Re-check debugger visualizer and remap/trim-path docs before repeating the same source-lookup consequences later on.

### Common false gap patterns from this pass
1. “Rust needs another debugger” when the sharper gap is a **support-posture / symbol-handoff / drift contract**.
2. “The symbols existed somewhere in CI, so support is fine” when the sharper question is whether the release/support handoff preserved them.
3. “Path trimming broke debugging” when the honest result may be a narrower **source-lookup impact** report rather than a total debugger verdict.
4. “Build-dir paths changed, so the support story changed” when location churn and support truth are different jobs.

## Update 2026-03-17 (214) — toolchain/target support productization pass

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Rustup 1.29 announcement
- rustup overrides / profiles / components / cross-compilation docs
- Cargo `rust-version` docs
- Cargo config docs (`build.target`, target linker/runner, config hierarchy)
- Cargo resolver docs
- docs.rs metadata docs
- docs.rs builds docs
- docs.rs default-target change announcement
- RFC 2803 target-tier policy

### Kept together
- the distinction between **whole-project support contracts** and adjacent docs.rs parity, item-level cfg availability, linker diagnosis, and MSRV-only tools
- the fact that rustup, Cargo, and docs.rs already expose real substrate, which means the missing value is now the reviewable contract above them
- the need to keep **support class**, **evidence provenance**, and **external prerequisites** explicit instead of treating “supported target” like one flat label
- the need to deepen **P-0484** before inventing another neighboring support-truth crate lane too early

### Result
- Added `meta/toolchain-target-support-product-plan-2026-03-17.md` as the implementation-ready v0.1 sketch for **P-0484**.
- Added `support-class.policy`, `support-evidence.report`, and `external-prerequisite.manifest` schemas plus three new toolchain-support fixture families for workspace policy splits, runner requirements, and newly supported rustup hosts that a project does **not** yet claim.
- Updated **P-0484** with tighter evidence, richer artifacts, and a direct link to the new product plan.
- Updated repo-memory files so future passes do not mistake docs.rs posture, target tiers, or one local build for the same kind of support claim.

### Freshness anchors
- Re-check rustup release notes and rustup book behavior before repeating the same host/profile/toolchain assumptions later on.
- Re-check Cargo `rust-version`, resolver, and config docs before restating workspace or target-setting behavior later on.
- Re-check docs.rs metadata/build docs before assuming the same default-target and sandbox behavior later on.

### Common false gap patterns from this pass
1. “The project has a `rust-toolchain.toml`, so its support story is already clear” when the sharper gap is a **reviewable support contract with evidence classes**.
2. “Rust target tier tells us the project supports that target” when the target tier is Rust-the-project’s policy, not the crate’s promise.
3. “docs.rs built it, so it’s supported” when docs visibility, compile-only posture, and real contributor/runtime support are different jobs.
4. “One laptop or CI job proved it” when external prerequisites and support classes still need to be stated explicitly.

## Update 2026-03-17 (213) — crate diagnosis-surface productization pass

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Rust debugging survey 2026
- Tokio tracing topic docs
- Tokio Console announcement + `console-subscriber` docs
- `tokio-metrics` docs
- `miette` docs + `miette::Diagnostic` docs
- `tracing-error` docs + `TracedError` docs

### Kept together
- the distinction between **crate-authored diagnosis contracts** and adjacent tracing / metrics / debugger / error-rendering substrate
- the fact that runtime warnings, metric streams, diagnostic codes, and span traces already exist, which means the missing value is now the contract above them
- the need to keep **symptoms** separate from **root-cause guesses**
- the need for explicit **capture-policy** and **triage-order** artifacts so troubleshooting support does not dissolve back into prose
- the need to deepen **P-0525** before inventing another neighboring crate lane too early

### Result
- Added `meta/crate-diagnosis-surface-product-plan-2026-03-17.md` as the implementation-ready v0.1 sketch for **P-0525**.
- Added `symptom-taxonomy.profile`, `capture-policy.profile`, and `triage-sequence.manifest` schemas plus three new diagnosis-surface fixture families for runtime warnings, auth-vs-endpoint ambiguity, and board-only capture honesty.
- Updated **P-0525** with tighter prior-art boundaries, richer artifacts, and a direct link to the new product plan.
- Updated repo-memory files so future passes do not mistake runtime warning systems, error-reporting crates, or span-trace helpers for the same missing crate.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness priorities later on.
- Re-check Tokio tracing / console / metrics docs before assuming the same runtime-diagnostics substrate later on.
- Re-check `miette` and `tracing-error` before restating their current role in the stack later on.

### Common false gap patterns from this pass
1. “Rust needs another runtime debugger” when the sharper gap is a **crate-authored symptom / triage / capture contract**.
2. “Tokio Console warnings already solve troubleshooting support” when they still do not define per-crate symptom names, self-checks, or safe bundles.
3. “Pretty error reports solve this” when rendering a diagnostic and publishing a reviewable troubleshooting contract are different jobs.
4. “The missing crate is a support portal” when the sharper value is still a small local pack/diff/bundle layer above today’s substrate.

## Update 2026-03-17 (212) — crate example-surface productization pass

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Rust API Guidelines documentation chapter
- Cargo targets / examples docs
- rustdoc scraped examples book page + RFC 3123
- docs.rs metadata docs
- docs.rs builds docs
- docs for `trycmd`, `trybuild`, and `skeptic`
- docs for `cargo-generate`, `mdBook`, and `term-transcript`
- live `s2-sdk` docs showing scraped examples in practice

### Kept together
- the distinction between **official quickstart contracts** and adjacent tools for templates, tutorials, snapshots, or docs hosting
- the fact that Rust already has enough example/doc substrate that the missing value is now the reviewable contract above it
- the need for **normalization profiles** so dynamic output does not quietly make “official quickstarts” unverifiable
- the need to deepen **P-0524** before inventing another adjacent crate lane too early

### Result
- Added `meta/crate-example-surface-product-plan-2026-03-17.md` as the implementation-ready v0.1 sketch for **P-0524**.
- Added `example-normalization.profile` schema and two new example-surface fixture families for dynamic CLI output and guide/book + examples linkage.
- Updated **P-0524** with tighter prior-art boundaries, a normalization artifact, and a direct link to the new product plan.
- Updated repo-memory files so future passes do not mistake project templates, tutorial systems, transcript tools, or live scraped-example usage for the same missing crate.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness priorities later on.
- Re-check docs.rs metadata/build docs before assuming the same docs-hosting constraints later on.
- Re-check `trycmd`, `trybuild`, `skeptic`, `cargo-generate`, `mdBook`, and `term-transcript` before restating their current role in the stack later on.

### Common false gap patterns from this pass
1. “Rust still needs a tutorial system” when the sharper gap is a **crate-authored official quickstart contract**.
2. “A template generator solves onboarding” when scaffolding a *new project* is not the same as validating the *chosen crate’s* first-success path.
3. “Snapshotting already solves example support” when output normalization and support-level honesty are still separate decisions.
4. “Scraped examples already solve it” when live scraped examples still do not classify official starts, prerequisites, or release-to-release drift.

## Update 2026-03-17 (211) — crate diagnosis-surface pass

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Rust debugging survey 2026
- Tokio tracing topic docs
- `tracing` docs
- `console-subscriber` docs
- `metrics` docs
- `tokio-metrics` docs

### Kept together
- the distinction between **diagnosis-surface contracts** and raw telemetry/debugger substrate
- the fact that Rust already has meaningful tracing / metrics / async-debugging pieces, which changes the missing-crate question
- the fact that downstream users still need crate-authored symptom catalogs, self-checks, and remediation guidance above those pieces
- the need to keep crash-handoff bundles, observability contracts, debugger posture, and diagnosis-surface contracts separate

### Result
- Added a new top-level proposal: **P-0525 Crate Diagnosis Surface Pack Kit**.
- Added a crate-diagnosis-surface lane-boundary note.
- Added fixture/schema stubs for **P-0525** so the proposal now has concrete pack/receipt/report/manifest/diff surfaces.
- Updated the crate-frontier map and repo-memory files so future passes do not rediscover this seam under “better tracing”, “better debugging”, or “better support bundles”.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness priorities later on.
- Re-check Tokio/tracing/console docs before claiming the same runtime-diagnostics substrate later on.
- Re-check `metrics` / `tokio-metrics` before assuming the same signal-export posture later on.

### Common false gap patterns from this pass
1. “Rust needs better telemetry” when the sharper gap is a **crate-authored symptom/self-check/remediation contract**.
2. “tokio-console already solves this” when it provides powerful diagnostics substrate but not a crate-specific troubleshooting contract.
3. “runtime-handoff bundles already solve this” when many ecosystem pain points are steady-state diagnosis rather than crashes.
4. “issue templates are enough” when downstream users need reviewable artifacts and diffs, not just prose prompts.

## Update 2026-03-17 (210) — crate example-surface lane

- Promoted **P-0524 Crate Example Surface Pack Kit** because the archive still lacked a receiver-facing artifact for official quickstarts, example support levels, environment assumptions, docs/example linkage, and first-success diffs.
- Added a lane-boundary note so future passes keep example-surface contracts separate from task-first crate choice, failure-path guidance, setup scenarios, downstream testing support, docs.rs parity / hosting, and tutorial publishing.
- Added a small fixture/schema pack so the archive can now express example packs, example catalogs, quickstart manifests, adoption scenarios, environment reports, docs-linkage reports, output reports, support checks, and example-surface diffs.
- Updated the frontier map and ranked frontier snapshot so the repo’s memory no longer treats onboarding / quickstart support as just a side effect of docs or tests.

Common false moves this pass tried to avoid:
1. “Rust just needs better docs” when the sharper gap is a **crate-authored example-support contract**.
2. “Scraped examples already solve this” when scraped examples do not classify support levels, prerequisites, or release-to-release quickstart changes.
3. “The test-surface lane already covers it” when first-success / onboarding paths and downstream-testing contracts are adjacent but different.

## Update 2026-03-17 (208) — crate persistence-surface lane

- Promoted **P-0522 Crate Persistence Surface Pack Kit** because the archive still lacked a receiver-facing artifact for persisted-state compatibility windows, durability boundaries, recovery posture, and migration of durable bytes/state even after adding choice, setup, performance, observability, authority, lifecycle, and resource-support lanes.
- Added a lane-boundary note so future passes keep persistence-surface contracts separate from upgrade packs, configuration scenarios, authority/lifecycle/resource support, serializer or storage-engine substrate, and domain schema workbenches.
- Added a small fixture/schema pack so the archive can now express persistence packs, format-compat reports, durability-boundary reports, recovery-posture reports, migration manifests, compatibility windows, and persistence diffs.
- Updated the frontier map and ranked frontier snapshot so the repo’s memory no longer treats persisted-state trust as a side note under upgrade or storage-engine work.

Common false moves this pass tried to avoid:
1. “Rust just needs another serializer or database” when the sharper gap is a **crate-authored persistence pack with compatibility, durability, recovery, and migration receipts**.
2. “Upgrade packs already cover this” when release-to-release code migration and persisted-state migration are often different problems.
3. “Storage docs are enough” when downstream users need reviewable artifacts and diffs, not just implementation prose.

## Update 2026-03-17 (206) — crate lifecycle-surface lane

- Promoted **P-0520 Crate Lifecycle Surface Pack Kit** because the archive still lacked a receiver-facing artifact for background work, cancel safety, shutdown obligations, and drain recipes even after adding setup, performance, observability, authority, upgrade, and failure-support lanes.
- Added a lane-boundary note so future passes keep lifecycle-surface contracts separate from graceful-shutdown frameworks, structured-concurrency substrate, runtime handoff, observability, and authority posture.
- Added a small fixture/schema pack so the archive can now express lifecycle packs, background-work receipts, cancellation surfaces, shutdown-obligation reports, drain recipes, and lifecycle diffs.
- Updated README, INDEX, frontier map, known-existing, roadmap, and LLM hygiene so this lane is easier to rediscover and harder to collapse back into vague “better async shutdown tooling”.


## 2026-03-17 refresh — crate observability-surface pass (204)

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Tokio tracing topic docs
- `tracing` docs
- `tracing-subscriber` docs
- OpenTelemetry Rust docs
- OpenTelemetry Rust instrumentation-libraries docs
- OpenTelemetry semantic-conventions docs
- OpenTelemetry logs docs

### Kept together
- the distinction between **observability-surface contracts** and generic telemetry plumbing
- the fact that Rust already has real tracing/OTel substrate, which changes the missing-crate question
- the fact that docs/source remain the main learning path, making emitted-signal expectations part of the product rather than an afterthought
- the need to keep schema linting, redaction tooling, and full observability platforms separate from a crate-authored signal contract

### Result
- Added a new top-level proposal: **P-0518 Crate Observability Surface Pack Kit**.
- Added a crate-observability-surface lane-boundary note.
- Added fixture/schema stubs for **P-0518** so the proposal now has concrete pack/receipt/report/recipe/cost/redaction/diff surfaces.
- Updated the crate-frontier map and repo-memory files so future passes do not rediscover this seam under “better tracing setup”, “better OpenTelemetry support”, or “better dashboards”.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness priorities later on.
- Re-check Tokio/tracing/tracing-subscriber docs before claiming the same substrate later on.
- Re-check OpenTelemetry Rust status and instrumentation-library guidance before assuming the same fragmentation story later on.
- Re-check semantic-convention and logs guidance before assuming the same schema-stability posture later on.

### Common false gap patterns from this pass
1. “Rust needs better telemetry plumbing” when the sharper gap is a **crate-authored observability surface with stability, cost, and redaction boundaries**.
2. “`tracing` / OpenTelemetry already solve this” when they mostly solve emission and transport substrate rather than the joined receiver-facing contract.
3. “Schema linting already solves this” when naming conventions are not the same thing as a crate-authored signal catalog.
4. “Dashboards prove operability” when dashboards are downstream views, not a portable support artifact.

## 2026-03-17 refresh — crate performance-envelope pass (203)

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Cargo bench docs
- Cargo profiles docs
- Cargo 1.84 development-cycle post
- docs for Criterion, Iai-Callgrind, Divan, codspeed-criterion-compat, and codspeed-divan-compat

### Kept together
- the distinction between **configuration/setup scenarios** and **performance-envelope contracts**
- the fact that Cargo already has real benchmark/profile substrate, which changes the missing-crate question
- the fact that benchmark tools differ in measurement philosophy, making metric choice itself part of the product surface
- the need to keep generic benchmark/profiling tools and hosted CI services separate from a crate-authored performance contract

### Result
- Added a new top-level proposal: **P-0517 Crate Performance Envelope Pack Kit**.
- Added a crate-performance-envelope lane-boundary note.
- Added fixture/schema stubs for **P-0517** so the proposal now has concrete pack/receipt/report/recipe/budget/diff surfaces.
- Updated the crate-frontier map and repo-memory files so future passes do not rediscover this seam under “better benchmark tooling”, “better perf dashboards”, or “better config scenarios with numbers”.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness priorities later on.
- Re-check Cargo benchmark/profile docs before claiming the same substrate later on.
- Re-check the current stable benchmark-tool ecosystem before assuming the same fragmentation story later on.

### Common false gap patterns from this pass
1. “Rust needs better benchmarking” when the sharper gap is a **crate-authored performance envelope with explicit workload, metric, confidence, and recipe boundaries**.
2. “Criterion / Iai already solve this” when they mostly solve measurement surfaces rather than the joined receiver-facing contract.
3. “Perf CI services already solve this” when CI execution is not the same thing as a crate-authored performance promise.

## 2026-03-16 refresh — crate configuration/setup-scenario pass (202)

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Cargo features docs
- Cargo SemVer guidance
- Cargo environment variables docs
- Cargo build docs (`required-features`)
- Cargo external tools docs (`cargo metadata`)
- Cargo resolver docs
- docs.rs metadata docs
- docs.rs build docs
- Inside Rust `hint-mostly-unused` post
- RFC 3416 feature metadata
- Cargo 1.93 development-cycle post
- docs for `cargo-hack`, `document-features`, and `cargo-feature-combinations`

### Kept together
- the distinction between **task-first crate choice** and **setup/configuration scenarios**
- the fact that Cargo already has real feature/env/docs substrate, which changes the missing-crate question
- the fact that docs/source remain the main learning path, making setup surfaces part of the product rather than an afterthought
- the need to keep config provenance tools, feature-combo test tools, and feature-doc renderers separate from a crate-authored scenario contract

### Result
- Added a new top-level proposal: **P-0516 Crate Configuration Scenario Pack Kit**.
- Added a crate-configuration-scenario lane-boundary note.
- Added fixture/schema stubs for **P-0516** so the proposal now has concrete pack/receipt/report/recipe/check/conflict/diff surfaces.
- Updated the crate-frontier map and repo-memory files so future passes do not rediscover this seam under “better setup docs”, “better feature docs”, or “better Cargo config explanation”.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness priorities later on.
- Re-check Cargo feature/config/docs.rs docs before claiming the same setup substrate later on.
- Re-check feature-metadata progress before assuming today’s feature-doc gap stays unchanged.
- Re-check the existing feature-combo tooling ecosystem before claiming the same scenario lane later on.

### Common false gap patterns from this pass
1. “Rust needs better feature docs” when the sharper gap is a **crate-authored scenario pack with checked recipes and conflict classes**.
2. “`cargo-hack` already solves this” when it mostly checks combinations rather than naming intended receiver-facing scenarios.
3. “Cargo config receipts already solve this” when precedence explanation is not the same thing as setup guidance for one chosen crate.
4. “Feature metadata RFCs will solve this automatically” when metadata vocabulary is only one ingredient of a scenario contract.

## 2026-03-16 refresh — crate off-ramp / successor-support pass (201)

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- rustc warn-by-default lint docs for `deprecated`
- Cargo SemVer guidance
- Cargo yank docs
- Cargo update docs
- crates.io development update (Security tab)
- crates.io malicious crate notification policy update
- docs for `cargo-audit`, `cargo-deny`, and `cargo-outdated`
- RFC 3416 feature metadata
- docs.rs crate rename example (`sello` → `txgate`)

### Kept together
- the distinction between **upgrade support** and **off-ramp support**
- the fact that Cargo/crates.io/RustSec already expose real deprecation, yank, and advisory substrate, which changes the missing-crate question
- the fact that docs/source remain the main learning path, making successor guidance part of the product rather than an afterthought
- the need to keep health metadata, advisory detection, and publish/yank mechanics separate from a crate-authored exit contract

### Result
- Added a new top-level proposal: **P-0515 Crate Off-Ramp Pack Kit**.
- Added a crate-offramp lane-boundary note.
- Added fixture/schema stubs for **P-0515** so the proposal now has concrete pack/map/receipt/recipe/check/diff surfaces.
- Updated the crate-frontier map and repo-memory files so future passes do not rediscover this seam under “better deprecation notes”, “better advisories”, or “better maintenance metadata”.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness priorities later on.
- Re-check Cargo’s yank/update docs before claiming the same sunset substrate later on.
- Re-check crates.io Security tab / malicious-crate policy language before claiming the same advisory communication posture later on.
- Re-check feature-metadata progress before assuming feature-level deprecation remains purely aspirational.

### Common false gap patterns from this pass
1. “Rust needs better deprecation notes” when the sharper gap is a **crate-authored off-ramp pack with successor maps and checked exit recipes**.
2. “`cargo-audit` / `cargo-deny` already solve this” when they mostly detect risk rather than define successor paths.
3. “Yanking a version is enough communication” when yanks do not delete crates and do not hand users a checked replacement plan.
4. “Crate health metadata already covers succession” when broad maintenance posture is not the same as a receiver-facing exit contract.

## 2026-03-16 refresh — crate runtime handoff/support-bundle pass (199)

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- `std::error` module docs
- `std::error::Error` docs
- `std::backtrace` docs
- `std::panic::set_hook` docs
- `std::error::Request` docs
- nightly `std::error::Report` docs
- RFC 3192 / dyno background
- docs for `error-stack`, `miette`, `tracing-error`, and `human-panic`

### Kept together
- the distinction between **compile-time guidance** and **runtime failure handoff**
- the fact that `std` already has real runtime error/panic substrate, which changes the missing-crate question
- the fact that debugging remains a live pain while docs/source remain the main learning path
- the need to keep renderer crates, tracing stacks, and domain-specific incident bundles separate from a crate-authored runtime handoff contract

### Result
- Added a new top-level proposal: **P-0513 Crate Runtime Handoff Pack Kit**.
- Added a crate-runtime-handoff lane-boundary note.
- Added fixture/schema stubs for **P-0513** so the proposal now has concrete pack/receipt/redaction/check/diff surfaces.
- Updated the crate-frontier map and repo-memory files so future passes do not rediscover this seam under “better logs”, “better panic messages”, or “better observability”.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness priorities later on.
- Re-check `std::error`, `std::panic`, and `std::backtrace` docs before claiming the same runtime substrate later on.
- Re-check whether `std::error::Report` or generic-member-access surfaces stabilize before claiming the same gap later on.

### Common false gap patterns from this pass
1. “Rust needs prettier runtime errors” when the sharper gap is a **crate-authored runtime handoff pack with redaction and diffs**.
2. “Tracing exists, therefore crate runtime supportiveness is solved.”
3. “Panic hooks exist, therefore safe user-submittable crash reports are already a boring default.”
4. “Issue templates and logs are enough, so a crate does not need a machine-readable runtime handoff contract.”

## 2026-03-16 refresh — crate guidance/supportiveness pass (198)

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Rust Reference diagnostics attributes page
- Rust Reference built-in attributes index
- Rust release notes for 1.78.0 stabilization of `#[diagnostic]`
- RFC 3368 diagnostic attribute namespace

### Kept together
- the distinction between **crate choice**, **support claims**, **shared interop profiles**, and **receiver-facing guidance**
- the fact that stable compiler hooks for crate-authored diagnostics now exist, which changes the missing-crate question
- the fact that docs and source remain the main learning path, making support surfaces part of the product rather than an afterthought
- the need to keep generic renderer crates separate from authoring/testing/diffing guidance packs

### Result
- Added a new top-level proposal: **P-0512 Crate Guidance Pack Kit**.
- Added a crate-guidance lane-boundary note.
- Added fixture/schema stubs for **P-0512** so the proposal now has concrete pack/receipt/recipe/check/diff surfaces.
- Updated the crate-frontier map and repo-memory files so future passes do not rediscover this seam under “better docs”, “better diagnostics”, or “better metadata”.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness priorities later on.
- Re-check the Reference before claiming the same `#[diagnostic]` surface or semantics later on.
- Re-check compiler release notes before claiming no new crate-facing diagnostic hooks have stabilized.

### Common false gap patterns from this pass
1. “Rust needs prettier diagnostics” when the sharper gap is a **crate-authored guidance pack with fixtures and recipes**.
2. “The compiler has `#[diagnostic]`, therefore crate supportiveness is solved.”
3. “Good docs exist, therefore failure-path guidance is already structured and diffable.”
4. “Crate metadata tells you what to use, so you do not need receiver-facing recovery surfaces.”

## 2026-03-09 refresh — accessibility interop lab pass (166)

### Sources consulted
- AccessKit overview and architecture docs
- docs.rs for `accesskit`, `accesskit_winit`, `accesskit_unix`, `accesskit_windows`, and `accesskit_macos`
- AT-SPI2 overview
- Microsoft UI Automation providers overview
- Apple `NSAccessibilityProtocol` docs
- WAI-ARIA 1.2
- WCAG 2.2

### Kept together
- the distinction between **toolkit authoring/doctor** and **cross-platform capture/interop lab**
- the fact that AccessKit and its adapters are now meaningful substrate, which changes the missing-crate question
- the need for lane-explicit evidence across authoring, exposure, events, and policy rather than another screenshot-only or prose-only accessibility workflow
- the fact that policy packs can be standards-informed without pretending to automate legal compliance

### Result
- Did **not** add another top-level proposal.
- Added an accessibility-stack boundaries note.
- Upgraded **P-0202** with materially stronger “what it provides other people” planning.
- Clarified the relationship between **P-0087** and **P-0202** so the repo stops duplicating the same a11y story under two names.
- Added fixture/schema stubs for **P-0202** so the proposal now has concrete capture/tree/event/result/diff surfaces.

### Freshness anchors
- Re-check AccessKit adapter maturity before claiming the same platform coverage or ergonomics later on.
- Re-check official AT-SPI/UIA/NSAccessibility docs before freezing stronger platform-equivalence assumptions.
- Re-check ARIA/WCAG guidance before expanding policy packs into new automated findings.

### Common false gap patterns from this pass
1. “Rust needs another accessibility abstraction” when the sharper gap is a **portable capture and diff lab above existing abstractions**.
2. “AccessKit exists, therefore accessibility regression triage is solved.”
3. “WCAG exists, therefore an automation-friendly conformance artifact already exists for Rust desktop apps.”
4. “A screenshot changed, therefore the important accessibility facts were captured.”


## 2026-03-09 refresh — evidence-bundle core pass (162)

### Sources consulted
- in-toto Attestation Framework specs
- in-toto envelope spec
- Sigstore bundle format docs
- IETF SCITT architecture draft
- RFC 8785 (JCS)
- RFC 9052 (COSE)
- Rust crate docs for `sigstore`, `coset`, `serde_jcs`, and `zip`

### Kept together
- the distinction between **bundle substrate**, **attestation/signature lanes**, **profile contract**, and **publication lane**
- the fact that current ecosystem pressure points to a coordination artifact above existing crypto and packaging substrate
- the fact that local/shareable support bundles still matter even when transparency or publication layers exist
- the need to let domain crates import Sigstore or DSSE material without re-specifying their semantics

### Result
- Did **not** add another top-level proposal.
- Added an evidence-bundle boundaries note.
- Upgraded **P-0256** with materially stronger “what it provides other people” planning.
- Added fixture/schema stubs for **P-0256** so the proposal now has concrete manifest/profile/redaction/verification/diff surfaces.

### Freshness anchors
- Re-check in-toto layering and bundle guidance before claiming the same boundaries later on.
- Re-check Sigstore bundle docs and Rust `sigstore` support before claiming the same import lane maturity later on.
- Re-check SCITT drafts before freezing publication/transparency assumptions.
- Re-check docs.rs before claiming `zip`, `coset`, `serde_jcs`, and `sigstore` still provide the same substrate surface.

### Common false gap patterns from this pass
1. “Rust needs another attestation format” when the sharper gap is a **portable bundle substrate above multiple attestation lanes**.
2. “Sigstore bundles exist, therefore support/repro bundles are solved.”
3. “Publication exists, therefore local shareable bundles are no longer first-class.”
4. “A bundle is signed, therefore its profile semantics are automatically clear.”


## 2026-03-09 refresh — conformance/assurance stack pass (160)

### Sources consulted
- Cargo Book (`cargo test`)
- Cargo target reference
- nextest custom-harness docs
- nextest JUnit docs
- `libtest-mimic` docs
- `datatest-stable` docs
- Rust project goals 2026 flagships
- Rust blog: safety-critical Rust
- Safety-Critical Rust Consortium
- SACM 2.3

### Kept together
- the distinction between **suite contract**, **bundle substrate**, and **assurance review pack**
- the fact that Rust already has enough harness plumbing that the missing value is now a stable schema/vocabulary layer
- the fact that conformance evidence is an increasingly important assurance input, but not the whole assurance argument
- the need to keep JUnit/export lanes separate from the canonical semantic model

### Result
- Did **not** add another top-level proposal.
- Added a conformance-to-assurance layering note.
- Upgraded **P-0264** with materially stronger “what it provides other people” planning.
- Tightened **P-0503** so conformance bundles are treated as one evidence-import lane rather than as a surrogate assurance case.
- Added fixture/schema stubs for **P-0264** so the proposal now has concrete suite/result/environment/comparison surfaces.

### Freshness anchors
- Re-check nextest docs before claiming custom-harness or JUnit behavior is unchanged.
- Re-check docs.rs before claiming `libtest-mimic` and `datatest-stable` have the same capabilities or maintenance posture later on.
- Re-check Rust project goals and safety-critical program materials before claiming the ecosystem pressure around evidence/certification is unchanged.

### Common false gap patterns from this pass
1. “We need conformance tooling” when the real missing layer is a **stable suite manifest and verdict vocabulary**.
2. “We need certification support” when the real missing layer is still a **portable failing-case bundle**.
3. “JUnit exists, therefore the semantic result model is solved.”
4. “A suite passed, therefore the assurance claim is automatically satisfied.”


## 2026-03-09 refresh — correctness-lab pass (159)

### Sources consulted
- Rust project goals 2026 flagships
- Unicode UAX #14 and UAX #29
- ICU4X 2.0 changelog
- `parley` and `cosmic-text`
- Bevy text-backend migration discussion
- MDN Web Authentication API docs
- WPT `testdriver` virtual-authenticator docs
- geckodriver release notes
- `webauthn-rs` and `passkey-rs`

### Kept together
- the distinction between **mature substrate** and the still-missing **correctness-lab coordination artifact**
- the fact that Unicode algorithms define only part of text-layout behavior, leaving a real higher-level review surface
- the fact that passkey automation has improved enough that a Rust interop lab is now more plausible than it was a year ago
- the need to keep backend or runner churn from being misread as proof that the repo should propose one more backend instead of a comparison layer

### Result
- Did **not** add another top-level proposal.
- Added a correctness-frontier meta note.
- Upgraded **P-0197** and **P-0200** with materially stronger “what it provides other people” planning.
- Added fixture/schema stubs for both proposals so they now have concrete artifact surfaces.

### Freshness anchors
- Re-check ICU4X and text-backend maturity before freezing stronger assumptions about a default text stack.
- Re-check browser and WebDriver virtual-authenticator support before promising wider automation coverage.
- Re-check `webauthn-rs` and `passkey-rs` capability boundaries before claiming the Rust-only lane can replace browser/device evidence.

### Common false gap patterns from this pass
1. “Rust needs another text engine” when the sharper gap is a **layout conformance kit**.
2. “Rust needs another passkey SDK” when the sharper gap is an **interop/device lab**.
3. “The standard exists, so reproducible conformance and triage are solved” when the sharper gap is the **portable scenario/bundle layer**.

## 2026-03-09 refresh — bundle substrate and assurance stack

### Best next frontier move
- **P-0256 Evidence Bundle Core Kit** — now more clearly a shared substrate candidate than an isolated proposal, because too many later ideas want deterministic, signed, redactable, diffable bundle artifacts.

### Immediate follow-ons
- **P-0485 Verification Campaign Workbench Kit** — should consume a stable bundle substrate instead of growing a private packaging grammar.
- **P-0503 Assurance Case Workbench Kit** — should stay above imported evidence and review-pack assembly.
- **P-0264 Rust Conformance Harness Toolkit** — should keep suite/runner semantics distinct from container substrate.

### Working planning rule
For the next few passes, prefer bundle/profile layering notes, import contracts, and small stack fixtures over adding more bundle-first proposal count.

## Research ledger — 2026-03-09 broad portfolio pass (157)

### Sources consulted
- 2025 State of Rust survey results
- Rust compiler performance survey 2025 results
- Rust project goals (2026 flagships; Cargo rebuild/build-dir goals)
- Cargo test / target docs
- nextest custom harness docs
- local-first sources (Ink & Switch, Automerge, Loro)
- Unicode / ICU4X / shaping sources
- WebAuthn Level 3 and FIDO conformance/interoperability sources
- Rust verification tool sources (Kani, Creusot, Prusti, Flux, Miri)
- SACM standard overview
- crates.io home/categories

### Kept together
- the distinction between a **sharp sub-frontier** and a **healthy overall portfolio**
- the rule that worthy crates increasingly hand other people a **coordination artifact**
- the difference between “Rust lacks raw substrate” and “Rust lacks a boring default workflow above substrate”

### Result
- Did **not** add another top-level proposal.
- Added a new broad salience scan.
- Upgraded **P-0076** and **P-0264** with materially stronger “what it provides other people” planning.
- Added a hygiene note so future passes do periodic portfolio rebalancing.

### Freshness anchors
- Re-check the annual survey and compiler-performance survey before repeating pain-priority claims.
- Re-check WebAuthn/FIDO status before freezing stronger passkey-certification assumptions.
- Re-check ICU4X and shaping-engine maintenance reality before claiming one text-layout backend is the long-term default.
- Re-check local-first substrate maturity before narrowing on one CRDT backend as the golden path.

### Common false gap patterns from this pass
1. “Rust needs another parser/SDK” when the sharper gap is a **bundle / suite / contract / evidence layer**.
2. “Rust has a crate for that, so the problem is solved” when the sharper gap is still the **boring operational workflow**.
3. “The current top frontier should own the whole repo” when the healthier move is a **broad salience rebalance**.

## 2026-03-08 refresh — Cargo resolver workspace-inheritance layer

This pass again did **not** add a new proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** by freezing the next missing receiver-facing boundaries:

- manifest origin truth for `[workspace.dependencies]` versus member manifests,
- inherited `default-features` policy (disabled, neutralized, or re-enabled),
- target-specific inherited dependency scope,
- and conservative reporting when current docs and observed behavior do not line up cleanly.

Why this matters now:

- Cargo workspace docs say workspace-dependency features are additive.
- Dependency-spec docs still say inherited dependencies cannot use keys like `default-features`.
- A current documentation issue says the resulting semantics are easy to misread.
- Issue history shows both neutralized `default-features = false` and member-side re-enabling behavior.
- Target-specific inherited dependency behavior still has enough bug history to justify manual-review boundaries.

So the missing value is a **dependency-origin / inherited-policy why-bundle**, not another generic feature matrix.

For the next few passes, prefer:

- stabilizing `dependency-origin.report`,
- tiny workspace-inheritance scenarios,
- and explicit manifest-origin capture for **P-0468**.

Do **not** drift into:

- another generic workspace-deps wrapper,
- a false claim that the member manifest alone authored the effective policy,
- or a host/target/config story that forgets this is still resolver explanation work.

## 2026-03-08 refresh — Cargo resolver feature-intent layer

This pass again did **not** add a new proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** by freezing the next missing receiver-facing boundaries:

- positive feature requests versus negative feature intent,
- explanation subject scope (`--bin`, `-p`, workspace root, or equivalent),
- explicit reporting when another package kept a feature active anyway,
- and conservative reporting when investigative surfaces blur the requested subject.

Why this matters now:

- Cargo features docs explicitly warn that `default-features = false` may still fail to keep defaults off.
- The same docs say `--no-default-features` only disables defaults for the selected packages.
- Resolver docs still say multiple selected workspace packages unify dependency features.
- The feature-unification tracking issue is still open.
- Open issues still show subject-selection-dependent outcomes for `--bin`, `-p`, and workspace builds.

So the missing value is a **feature-intent and suppression why-bundle**, not another generic graph browser.

For the next few passes, prefer:

- stabilizing `feature-intent.report`,
- tiny positive/negative intent scenarios,
- and explicit subject-scope capture for **P-0468**.

Do **not** drift into:

- another generic feature-matrix runner,
- a false claim that raw tree output already preserves who asked for what,
- or a workflow/IDE story that forgets this is still resolver explanation work.

## 2026-03-08 refresh — Cargo resolver unification-scope layer

This pass again did **not** add a new proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** by freezing the next missing receiver-facing boundaries:

- feature-unification policy (`selected`, `workspace`, `package`),
- selected-package scope versus participating-package scope,
- explicit `feature_unification_policy_changed` diffs,
- and conservative reporting when investigative surfaces do not preserve package-mode truth exactly.

Why this matters now:

- unstable Cargo docs now define the three unification modes explicitly,
- the resolver docs still say multiple selected workspace packages unify dependency features,
- the tracking issue still has unresolved representation questions for package mode,
- and the long-running package-set-sensitivity issue is still open.

So the missing value is a **policy-and-participant why-bundle**, not another generic graph export.

For the next few passes, prefer:

- stabilizing `unification-scope.report`,
- tiny selected/workspace/package policy scenarios,
- and explicit participant-set capture for **P-0468**.

Do **not** drift into:

- another generic graph browser,
- a false claim that `cargo tree` already preserves package-mode truth,
- or a compile-time-deps/editor-parity story that forgets this is still resolver explanation work.

## 2026-03-08 refresh — Cargo resolver lane + platform coverage layer

This pass again did **not** add a new proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** by freezing the next missing receiver-facing boundaries:

- dependency-kind lane partition,
- platform-coverage truth for target-specific clauses,
- explicit `--filter-platform` / selected-target capture,
- and stronger manual-review markers when human-facing views merge lanes.

Why this matters now:

- Cargo’s resolver and features docs both make lane splits explicit for target-specific, build/proc-macro, and dev cases.
- `cargo tree` still says its feature view is only close to what Cargo will build.
- `cargo metadata` still includes all targets unless the capture narrows platform scope.
- `--unit-graph` remains the richer internal-graph substrate, but it is still unstable.
- current issue reports still show normal/dev and proc-macro/build cases where exactness must stay conservative.

So the missing value is a **lane-aware why-bundle**, not another generic graph API.

For the next few passes, prefer:

- stabilizing `lane-partition.report` and `platform-coverage.report`,
- tiny lane/target scenarios,
- and stronger exactness markers for **P-0468**.

Do **not** drift into:

- another generic graph query crate,
- a false claim that `cargo tree` or all-target metadata already gives exact build truth,
- or a mega Cargo doctor that absorbs host/target, linker, and editor-parity stories.

## 2026-03-08 refresh — Cargo resolver exactness + MSRV layer

This pass again did **not** add a new proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** by freezing the missing receiver-facing boundaries:

- `resolve-why.lock` as a capture-scope spine,
- mixed-MSRV version-choice receipts,
- selection-sensitive scenario bundles,
- and exact/manual-review vocabulary in the receipt itself.

Why this matters now:

- Cargo’s resolver docs now make mixed-workspace MSRV heuristics explicit.
- The same docs make the two-pass feature story explicit.
- `cargo tree` says its view is only close to what Cargo will build, not exact.
- the Cargo plumbing goal still says `cargo metadata` excludes feature resolution.
- `--unit-graph` remains useful but unstable.

So the missing value is a **why-bundle with boundary metadata**, not another graph API.

For the next few passes, prefer:

- stabilizing `resolve-why.lock`,
- tiny MSRV and selection-sensitive scenarios,
- and stronger exactness markers for **P-0468**.

Do **not** drift into:

- another generic graph query crate,
- another mega Cargo doctor,
- or a tool that silently treats `cargo tree` output as exact build truth.

## Research ledger — 2026-03-08 frontier pass (144)

### Sources consulted
- Cargo configuration docs
- Cargo unstable features docs (`host-config`, `target-applies-to-host`)
- Cargo changelog
- Cargo issue #14046 (`RUSTFLAGS` when `--target` is present)
- docs.rs issue #1580 (rustdoc cfg vs build-script cfg)
- Cargo tracking issues #9452 / #9453
- Cargo internal `extra_args` docs

### Kept together
- the distinction between config policy, observed application, and conservative diagnosis
- the separation between host/target scope, linker-lane choice, and tool-only compile surfaces
- the need to preserve same-triple lane changes instead of flattening them into “nothing changed”

### Result
- Did **not** add another top-level proposal.
- Added a host/target implementation note and a fresh frontier-salience note.
- Upgraded **P-0505** around policy / receipt / diff layering.
- Expanded `fixtures/host-target-scope-contract-kit/` with observation and diff schemas plus four scenario bundles.

### Freshness anchors
- Re-check Cargo config docs before freezing stronger assumptions about stable `rustflags` or `rustdocflags` precedence.
- Re-check #9452 / #9453 before claiming nightly host-config behavior is settled.
- Re-check Cargo internal docs before relying on exact wording about counterintuitive behavior.

### Common false gap patterns from this pass
1. “This is just cross-compilation pain” when the sharper gap is **host/target scope reviewability**.
2. “Same host and target triple means no meaningful change” when the sharper gap is often **command-shape or support-lane drift**.
3. “`[host]` exists, so downstream tooling is solved” when the sharper gap is still the **portable policy/receipt/diff bundle**.

## Research ledger — 2026-03-08 frontier pass (143)

### Sources consulted
- Cargo unstable docs (`-Zbuild-analysis`)
- Cargo changelog
- Cargo issue #15844 (tracking issue for `-Zbuild-analysis`)
- Cargo issue #2904 (why rebuilt diagnostics)
- 2025 State of Rust survey results
- Relink don’t Rebuild goal
- Cargo build-dir layout goal
- This development-cycle in Cargo 1.84 (`RUSTFLAGS` and caching)

### Kept together
- the existing Cargo explainability stack (P-0469 / P-0468 / P-0035 / P-0494 / P-0490)
- the distinction between upstream recording substrate and downstream stable support bundles
- the need for a small cause vocabulary instead of another Cargo-performance umbrella idea

### Result
- Did **not** add another top-level proposal.
- Added a rebuild-explanation upstream-fit note and a fresh frontier-salience note.
- Upgraded **P-0469** around three evidence lanes: imported Cargo reports, live capture, and optional fingerprint overlays.
- Expanded `fixtures/cargo-rebuild-why-kit/` with `fingerprint-delta` and `cache-conflict` schemas plus three scenario bundles.

### Freshness anchors
- Re-check Cargo unstable docs before freezing stronger assumptions about `cargo report` shape or wording.
- Re-check issue #15844 before treating session/report fields as settled downstream contracts.
- Re-check survey / project-goal framing before claiming rebuild pain or lock-contention priorities stayed the same.

### Common false gap patterns from this pass
1. “Cargo now has `cargo report rebuilds`, so downstream tooling is solved” when the sharper gap is still the **stable receipt and support-bundle layer**.
2. “Rebuild explanation should be a dashboard” when the sharper 0.1 value is a **portable artifact for one incident**.
3. “Any cache conflict hint belongs inside P-0469” when the sharper rule is to **import P-0490 context** rather than duplicate it.

## 2026-03-08 refresh — host/target config scope layer

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target in this frontier
- **P-0505 Cargo Host/Target Scope Contract Kit** — now newly justified because Cargo’s official config docs, unstable host-config surfaces, and real issue reports make the missing value clearly the scope contract / observation / doctor layer above them.

### Immediate follow-ons
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — should keep tool-only / editor-oriented build-surface parity separate from host/target scope diagnosis.
- **P-0504 Linker Lane Contract & Diagnosis Kit** — should keep linker-lane choice and switch-risk distinct from config-scope behavior.
- **P-0484 Toolchain & Target Support Contract Kit** — should keep broader target/toolchain posture separate from mixed-build scope facts.

### Working planning rule
For the next few passes, prefer schema stabilization, tiny mixed-build scenario bundles, and adapter planning for **P-0505** instead of adding another generic cross-build or “Cargo doctor” proposal.

### Added implementation rule
Treat `build.rustflags`, `build.rustdocflags`, `target.*`, `[host]`, `target-applies-to-host`, `--target`, and docs-builder/rustdoc quirks as substrate. The crate value begins at the **scope contract / observation receipt / diagnosis / diff bundle** above those surfaces.

## 2026-03-08 refresh — linker lane contract layer

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target in this frontier
- **P-0504 Linker Lane Contract & Diagnosis Kit** — now newly justified because the official Rust/Cargo substrate and the ecosystem’s real lane-specific tools make the missing value clearly the contract/receipt/doctor layer above them.

### Immediate follow-ons
- **P-0484 Toolchain & Target Support Contract Kit** — should keep broader target/toolchain posture separate from linker-lane drift.
- **P-0058 native-deps-kit** — should keep native probing/fallback behavior separate from linker-lane diagnosis.
- **P-0497 CPU Baseline & Runtime Dispatch Contract Kit** — should keep hardware-support promises separate from linker-lane support promises.

### Working planning rule
For the next few passes, prefer schema stabilization, tiny link-lane scenario bundles, and adapter planning for **P-0504** instead of adding another generic cross-compilation or linker-wrapper proposal.

### Added implementation rule
Treat Cargo linker config, `rustc` linker knobs, rustup cross-compilation docs, and existing tools like `cargo-zigbuild`, `cargo-xwin`, `xwin`, and `cross` as substrate. The crate value begins at the **lane contract / diagnosis / diff bundle** above those surfaces.

## 2026-03-08 refresh — safety-critical evidence stack

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target in this frontier
- **P-0503 Assurance Case Workbench Kit** — best new frontier move because the repo already has enough safety-relevant evidence proposals that the missing value has shifted upward into claim/evidence assembly and conservative review-pack export.

### Immediate follow-ons
- **P-0433 MC/DC Coverage Workbench Kit** — should stay the coverage-evidence producer, not grow its own assurance layer.
- **P-0453 Safety Contract Consumer Kit** — should remain the contract extraction/diff substrate feeding assurance packs.
- **P-0459 Clippy Safety Profile & Waiver Kit** — should provide machine-readable policy/waiver evidence that an assurance layer can import.
- **P-0465 BorrowSanitizer Workflow & Evidence Kit** — should stay a provenance-rich evidence producer for aliasing/unsafe reviews.
- **P-0256 Evidence Bundle Core Kit** — should remain the portable bundle substrate below assurance assembly.

### Working planning rule
For the next safety-critical passes, prefer stack notes, import-contract planning, and tiny assurance fixtures for **P-0503** and its feeder crates instead of adding more isolated safety-critical proposal count.

### Added implementation rule
Treat GSN/SACM as interchange surfaces and prior art, not as proof that the missing Rust value is “just an editor”. The crate value begins at the **claim/evidence graph, freshness tracking, and change-impact review pack** above Rust-native receipts.

## 2026-03-08 refresh — Cargo resolver explanation implementation layer

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target in this frontier
- **P-0468 Cargo Resolver Explanation Kit** — now substantially more implementation-ready because Cargo’s official surfaces and ecosystem prior art make the missing value clearly the explanation receipt, not raw graph access.

### Immediate follow-ons
- **P-0469 Cargo Rebuild Explanation Kit** — should keep sharing receipt vocabulary with P-0468 while staying focused on run-delta causes.
- **P-0035 cargo-build-insights** — should remain the historical warehouse / regression layer above imported sessions and explanation bundles, not a replacement for them.
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — should stay focused on tool-workflow parity while reusing the same observed-fact / conservative-inference vocabulary.

### Working planning rule
For the next few passes, prefer schema stabilization, tiny scenario bundles, and proposal-file upgrades for **P-0468** instead of adding another generic Cargo graph or feature-management proposal.

### Added implementation rule
Treat `cargo tree`, `cargo metadata`, `--unit-graph`, and `guppy`/`hakari` as substrate and prior art. The crate value begins at the **portable explanation receipt** above them.

## 2026-03-08 refresh — native build / buildscript stack

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target in this frontier
- **P-0046 buildscript-ux-kit** — best first move because it helps every build-script user immediately and creates shared report vocabulary for the rest of the stack.

### Immediate follow-ons
- **P-0059 buildscript-testkit** — should share normalized directive/report vocabulary with P-0046 and focus on fake-tool fixture scenarios first.
- **P-0058 native-deps-kit** — should reuse report/test vocabulary from P-0046/P-0059 and stay focused on declarative contracts plus a doctor UX.

### Working planning rule
For the next few passes, prefer schemas, fixture corpora, and planning notes for P-0046 / P-0059 / P-0058 instead of adding more native-build-adjacent proposal count.

### Added implementation rule
When touching this frontier again, prefer example bundles and crate-split/API notes over adding more native-build proposal count.


## 2026-03-08 refresh — Cargo explainability stack

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target
- **P-0469 Cargo Rebuild Explanation Kit** — strongest 0.1 candidate because the user story is concrete, the pain is current, and the artifact is easy to explain and review.

### Immediate follow-ons
- **P-0468 Cargo Resolver Explanation Kit** — should share receipt vocabulary and fixture style with P-0469.
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — should be treated as the tool-invocation parity layer above the same stack.

### Working planning rule
For the next few passes, prefer adding schemas, fixture corpora, and incubation notes to these three proposals instead of adding more proposal count.

# Roadmap (incubation picks)

This file is intentionally opinionated. Update it when new evidence changes the landscape.

## Candidate top 3 to incubate
1) **P-0001 Cargo Snapshot** — huge pain + clear MVP; aligns with enterprise needs.
2) **P-0016 Audit Lens** — rides strong research signal; composes with cargo-vet.
3) **P-0015 Cargo Attest** — matches ecosystem direction (Trusted Publishing); hard but high leverage.

## Why these
- Strong external evidence that the pain is real and recurring.
- Clear “library core + cargo plugin” architecture.
- Can ship an MVP without compiler changes.

## Next concrete actions (2-week spikes)
- P-0001: prototype `cargo snapshot create` that emits a tarball + manifest for a single workspace.
- P-0016: implement schema + diff tool with one Cargo Scan fixture.
- P-0015: implement statement + provenance JSON emission for `cargo package` output.


## Watchlist (high leverage, later)
- **P-0019 Cargo Transparency Bundle** — likely best as an integration layer that plugs into cargo-dist.
- **P-0020 embedded-hal TCK** — strong ecosystem multiplier after embedded-hal 1.0 stability.
- **P-0021 mpi-typed** — niche but high impact in HPC communities.

## Watchlist (new: 2026-03-04)
- **Local-first Sync Kit** — big upside if it nails secure-by-default + deterministic repro artifacts; needs tight scope to avoid “platform” creep.
- **Verification Workbench Kit** — can dramatically lower adoption friction for Kani/Creusot/Prusti/Miri by standardizing workflows and artifacts.
- **OTA Update Kit** — security-critical, repetitive work; good candidate for a conformance-first MVP.
- **WASI Conformance Kit** — interop multiplier for the Component Model era; pairs well with plugin kits.

## Watchlist additions (new evidence)
- **P-0023 vet-workbench** — cargo-vet adoption/UX blocker; could be a standalone accelerator for supply-chain hygiene.
- **P-0024 data-contract-kit** — “schema evolution” is universal in distributed systems; Rust still lacks a default, integrated kit.
- **P-0025 chaos-lab** — deterministic chaos testing is emerging; a unified reproducible-harness could make it mainstream.
- **P-0022 privacy-metrics-kit** — recurring “no telemetry” debates point to a missing reusable privacy/consent framework.

Last updated: 2026-03-04

## Next wave candidates
- **P-0026 cargo-tuf-mirror** — aligns with ecosystem direction (TUF adoption) and complements offline/mirror work.
- **P-0027 text-input-kit** — high-leverage for every GUI toolkit; IME and selection bugs are chronic and costly.
- **P-0028 open-table-format-kit** — strategic for Rust-in-data; avoids each engine reimplementing format glue.
- **P-0029 audio-graph-kit** — consolidates fragmented real-time audio plumbing into reusable primitives.


## New candidates (2026-03-01)
- **P-0030 cargo-build-jail** — strong supply-chain leverage; can ship as external tool before upstream changes.
- **P-0033 cargo-capabilities** — makes sandboxing/policy scalable by reducing “ad-hoc allowlist” pain.
- **P-0031 isolate-kit** — reusable substrate; also a dependency for P-0030 and plugin sandboxes.
- **P-0032 inference-kit** — valuable, but should incubate only with a committed adopter (avoid “abstraction-only” trap).

- **P-0038 cargo-repro-pack** — improves verifiability and supply-chain posture by making `.crate` artifacts deterministic (prototype for upstream).
- **P-0039 i18n-icu-kit** — a pragmatic i18n foundation: typed tokens + ICU-backed formatting without framework lock-in.
- **P-0040 proc-macro-sandbox-kit** — accelerates migration to sandboxed proc macros by giving authors a compatibility harness.
- **P-0041 cargo-prebuilt-artifacts** — supply-chain-aware prebuilt dep packs; potentially huge CI speedups if trust model is right.


## New candidates (2026-03-01-08)
- **P-0042 cargo-event-stream** — unblock IDE/CI tooling by making Cargo output machine-readable and robust to proc-macro noise.
- **P-0043 winit-web-ime-kit** — unlock serious WASM GUI text input (global IME) with a shared, tested bridge.
- **P-0044 ebpf-shipkit** — reduce bespoke packaging/testing burden for Rust eBPF apps; likely to accelerate adoption.

## Recent candidates
- **P-0042 cargo-event-stream** — unlocks IDE/CI tooling; pairs with build-analysis reporting.
- **P-0045 cargo-input-manifest** — build signatures for caching/repro; shares primitives with reproducible packaging.
- **P-0046 buildscript-ux-kit** — reduces “build.rs noise” and enables CI policies without upstream changes.

## New candidates (install trust & sandboxing)
- **P-0047 cargo-binary-trust** — verification/policy layer for fast binary installs (composes with cargo-binstall/cargo-dist); responds to rising demand for “fast installs” plus trust concerns.
- **P-0048 install-script-jail** — sandbox runner for third-party installer scripts (curl|sh) with auditable reports; extends build-sandbox ideas to the broader devtool ecosystem.
## New candidates (native deps + codegen + robotics)
- **P-0058 native-deps-kit** — unify system dependency workflows across pkg-config/vcpkg/vendoring with a “doctor” UX; reduces ubiquitous -sys pain.
- **P-0059 buildscript-testkit** — make build.rs testable; raises reliability for FFI and native builds without upstream changes.
- **P-0060 openapi-sdk-kit** — reduce fragmentation by standardizing an OpenAPI IR + conformance fixtures; make codegen outputs trustworthy and upgrade-friendly.
- **P-0061 rclrs-extras-kit** — fill ROS 2 Rust gaps (actions/executors/launch ergonomics) with conformance fixtures; improves “Rust robotics” viability.

Last updated: 2026-03-01

## New candidates (2026-03-01-16)
- **P-0062 Durable Workflow Kit** — high leverage if kept library-first; prioritize replay + local UX over platform ambitions.
- **P-0063 Passkey Stack Kit** — adoption multiplier: wrap existing protocol crates with secure defaults + framework adapters.
- **P-0064 BLE Conformance Kit** — avoid “yet another BLE crate”; focus on capability model + test harness + compatibility matrix.
- **P-0065 HTTP Cassette Kit** — unify fragmented VCR crates with a shared cassette format + redaction + adapters.

## Watchlist additions
- P-0066 Determinism Sim Kit
- P-0067 Kube Integration Testkit
- P-0068 Markdown Safe Kit

## Watchlist (new additions)

- **P-0069 mail-transport-security-kit** — operational “doctor” + evaluation engine for MTA-STS/TLS-RPT/DANE.
- **P-0070 saml-stack-kit** — secure XML signature substrate + SAML SP building blocks + conformance fixtures.
- **P-0071 MCP Guard Kit** — transport exposure, auth boundaries, operation guards, and review bundles for MCP deployments (built atop SDKs).
- **P-0072 pdf-safe-kit** — safe-by-default parsing/extraction limits + fuzz/conformance scaffolding.


## Frontier bets (2026-03-04)
- P-0073 Async Replay Debugger Kit
- P-0074 Capability Sandbox Kit
- P-0075 Cargo Provenance Suite
- P-0076 Local-first Sync Kit


# Roadmap (incubation picks)

This file is intentionally opinionated. Update it when new evidence changes the landscape.

## Candidate top 3 to incubate
1) **P-0001 Cargo Snapshot** — huge pain + clear MVP; aligns with enterprise needs.
2) **P-0016 Audit Lens** — rides strong research signal; composes with cargo-vet.
3) **P-0015 Cargo Attest** — matches ecosystem direction (Trusted Publishing); hard but high leverage.

## Why these
- Strong external evidence that the pain is real and recurring.
- Clear “library core + cargo plugin” architecture.
- Can ship an MVP without compiler changes.

## Next concrete actions (2-week spikes)
- P-0001: prototype `cargo snapshot create` that emits a tarball + manifest for a single workspace.
- P-0016: implement schema + diff tool with one Cargo Scan fixture.
- P-0015: implement statement + provenance JSON emission for `cargo package` output.


## Watchlist (high leverage, later)
- **P-0019 Cargo Transparency Bundle** — likely best as an integration layer that plugs into cargo-dist.
- **P-0020 embedded-hal TCK** — strong ecosystem multiplier after embedded-hal 1.0 stability.
- **P-0021 mpi-typed** — niche but high impact in HPC communities.

## Watchlist (new: 2026-03-04)
- **Local-first Sync Kit** — big upside if it nails secure-by-default + deterministic repro artifacts; needs tight scope to avoid “platform” creep.
- **Verification Workbench Kit** — can dramatically lower adoption friction for Kani/Creusot/Prusti/Miri by standardizing workflows and artifacts.
- **OTA Update Kit** — security-critical, repetitive work; good candidate for a conformance-first MVP.
- **WASI Conformance Kit** — interop multiplier for the Component Model era; pairs well with plugin kits.

## Watchlist additions (new evidence)
- **P-0023 vet-workbench** — cargo-vet adoption/UX blocker; could be a standalone accelerator for supply-chain hygiene.
- **P-0024 data-contract-kit** — “schema evolution” is universal in distributed systems; Rust still lacks a default, integrated kit.
- **P-0025 chaos-lab** — deterministic chaos testing is emerging; a unified reproducible-harness could make it mainstream.
- **P-0022 privacy-metrics-kit** — recurring “no telemetry” debates point to a missing reusable privacy/consent framework.

Last updated: 2026-03-04

## Next wave candidates
- **P-0026 cargo-tuf-mirror** — aligns with ecosystem direction (TUF adoption) and complements offline/mirror work.
- **P-0027 text-input-kit** — high-leverage for every GUI toolkit; IME and selection bugs are chronic and costly.
- **P-0028 open-table-format-kit** — strategic for Rust-in-data; avoids each engine reimplementing format glue.
- **P-0029 audio-graph-kit** — consolidates fragmented real-time audio plumbing into reusable primitives.


## New candidates (2026-03-01)
- **P-0030 cargo-build-jail** — strong supply-chain leverage; can ship as external tool before upstream changes.
- **P-0033 cargo-capabilities** — makes sandboxing/policy scalable by reducing “ad-hoc allowlist” pain.
- **P-0031 isolate-kit** — reusable substrate; also a dependency for P-0030 and plugin sandboxes.
- **P-0032 inference-kit** — valuable, but should incubate only with a committed adopter (avoid “abstraction-only” trap).

- **P-0038 cargo-repro-pack** — improves verifiability and supply-chain posture by making `.crate` artifacts deterministic (prototype for upstream).
- **P-0039 i18n-icu-kit** — a pragmatic i18n foundation: typed tokens + ICU-backed formatting without framework lock-in.
- **P-0040 proc-macro-sandbox-kit** — accelerates migration to sandboxed proc macros by giving authors a compatibility harness.
- **P-0041 cargo-prebuilt-artifacts** — supply-chain-aware prebuilt dep packs; potentially huge CI speedups if trust model is right.


## New candidates (2026-03-01-08)
- **P-0042 cargo-event-stream** — unblock IDE/CI tooling by making Cargo output machine-readable and robust to proc-macro noise.
- **P-0043 winit-web-ime-kit** — unlock serious WASM GUI text input (global IME) with a shared, tested bridge.
- **P-0044 ebpf-shipkit** — reduce bespoke packaging/testing burden for Rust eBPF apps; likely to accelerate adoption.

## Recent candidates
- **P-0042 cargo-event-stream** — unlocks IDE/CI tooling; pairs with build-analysis reporting.
- **P-0045 cargo-input-manifest** — build signatures for caching/repro; shares primitives with reproducible packaging.
- **P-0046 buildscript-ux-kit** — reduces “build.rs noise” and enables CI policies without upstream changes.

## New candidates (install trust & sandboxing)
- **P-0047 cargo-binary-trust** — verification/policy layer for fast binary installs (composes with cargo-binstall/cargo-dist); responds to rising demand for “fast installs” plus trust concerns.
- **P-0048 install-script-jail** — sandbox runner for third-party installer scripts (curl|sh) with auditable reports; extends build-sandbox ideas to the broader devtool ecosystem.
## New candidates (native deps + codegen + robotics)
- **P-0058 native-deps-kit** — unify system dependency workflows across pkg-config/vcpkg/vendoring with a “doctor” UX; reduces ubiquitous -sys pain.
- **P-0059 buildscript-testkit** — make build.rs testable; raises reliability for FFI and native builds without upstream changes.
- **P-0060 openapi-sdk-kit** — reduce fragmentation by standardizing an OpenAPI IR + conformance fixtures; make codegen outputs trustworthy and upgrade-friendly.
- **P-0061 rclrs-extras-kit** — fill ROS 2 Rust gaps (actions/executors/launch ergonomics) with conformance fixtures; improves “Rust robotics” viability.

Last updated: 2026-03-01

## New candidates (2026-03-01-16)
- **P-0062 Durable Workflow Kit** — high leverage if kept library-first; prioritize replay + local UX over platform ambitions.
- **P-0063 Passkey Stack Kit** — adoption multiplier: wrap existing protocol crates with secure defaults + framework adapters.
- **P-0064 BLE Conformance Kit** — avoid “yet another BLE crate”; focus on capability model + test harness + compatibility matrix.
- **P-0065 HTTP Cassette Kit** — unify fragmented VCR crates with a shared cassette format + redaction + adapters.

## Watchlist additions
- P-0066 Determinism Sim Kit
- P-0067 Kube Integration Testkit
- P-0068 Markdown Safe Kit

## Watchlist (new additions)

- **P-0069 mail-transport-security-kit** — operational “doctor” + evaluation engine for MTA-STS/TLS-RPT/DANE.
- **P-0070 saml-stack-kit** — secure XML signature substrate + SAML SP building blocks + conformance fixtures.
- **P-0071 MCP Guard Kit** — transport exposure, auth boundaries, operation guards, and review bundles for MCP deployments (built atop SDKs).
- **P-0072 pdf-safe-kit** — safe-by-default parsing/extraction limits + fuzz/conformance scaffolding.


## Frontier bets (2026-03-04)
- P-0073 Async Replay Debugger Kit
- P-0074 Capability Sandbox Kit
- P-0075 Cargo Provenance Suite
- P-0076 Local-first Sync Kit


## New candidates (2026-03-05)
- P-0283 TLS 1.3 + X.509 Path Validation Interop & Evidence Kit (tlsbundle)
- P-0284 IEC 60870-5-104 Interop & Evidence Kit (iec104bundle)
- P-0285 HL7 v2 + MLLP Interop & Evidence Kit (hl7bundle)

- P-0271 WebGPU CTS triage & evidence kit
- P-0272 Apache Arrow Flight/Flight SQL interop & evidence kit
- P-0273 gNMI interop & evidence kit

- **P-0197 Text Layout & Shaping Conformance Kit** — high leverage for every Rust GUI toolkit; keeps scope to deterministic layout outputs + fixtures.
- **P-0198 Network Cassette & Impairment Kit** — makes network failures reproducible and shareable (redaction-first), with capture→replay→diff workflows.
- **P-0199 MessageFormat 2 Localization Kit** — positions Rust for MF2 adoption; conformance-first implementation that composes with ICU4X.
- **P-0200 WebAuthn & Passkeys Interop + Device Lab Kit** — turns passkeys into a testable integration surface with scenario DSL + portable evidence bundles.
- **P-0201 Secure Email Interop ShipKit** — cohesive MIME/S/MIME/OpenPGP + auth verification with deterministic normalization and shareable diagnostics.

Last updated: 2026-03-05
## New candidates (2026-03-05)

- **P-0286 SNMPv3 Interop & Evidence Kit** — canonical/redactable USM transcripts + capability matrices + replay/diff.
- **P-0287 RADIUS + EAP Interop & Evidence Kit** — registry-pinned decoding + exchange bundles + replay/diff for AAA flows.
- **P-0288 CAN + ISO-TP + UDS Interop & Evidence Kit** — canonical CAN/UDS traces + timing/state checks + reproducible diagnostic bundles.
- **P-0289 DNP3 Secure Authentication Interop & Evidence Kit** — canonical SA transcripts + capability matrices + replay/diff.
- **P-0290 OpenID Federation 1.0 Interop & Evidence Kit** — trust-chain resolution + policy diffs + reproducible federation bundles.
- **P-0291 JPEG XL Conformance & Evidence Kit** — golden tests + fuzz corpus bundles + reproducible divergence triage.

Last updated: 2026-03-05


## New candidates (2026-03-06)
- **P-0292 OpenRTB 2.6 + AdCOM Interop & Evidence Kit** — high-leverage for adtech compatibility; profile-as-code plus redactable trace bundles.
- **P-0293 MAVLink Microservices Interop & Evidence Kit** — strong robotics/drone multiplier; mission/parameter/file/signing scenarios with replay.
- **P-0294 AS2 + MDN Interop & Evidence ShipKit** — gives Rust a credible B2B transport story without promising a full EDI suite.
- **P-0295 ORC Interop & Canonicalization Kit** — lakehouse/data infra helper around `orc-rust`; semantic diffs + bug bundles.
- **P-0296 BPMN 2.0 + DMN Conformance Workbench Kit** — process/rules assets under CI with portable traces and FEEL corpora.

Last updated: 2026-03-06


## Frontier queue — 2026-03-06 (69)

1. **FIX + Orchestra** — strongest case for a profile-as-code + replay + certification workbench around multiple existing Rust engines.
2. **XBRL + iXBRL** — prioritize conformance-runner + canonical-fact diff MVP, ideally side-by-side with Arelle outputs.
3. **SECS/GEM** — prototype transcript IR + GEM state-trace model before broadening into vendor-specific flows.
4. **IPP Everywhere** — keep scope anchored to capability inspection, job replay, and certification-style bundles.
5. **EBICS** — validate whether a neutral simulated-bank suite can cover enough onboarding pain to justify a full workbench.


## Frontier queue — 2026-03-06 (70)

1. **FHIR + SMART** — strongest cross-cutting case for IG lockfiles, validator adapters, and PHI-safe evidence bundles.
2. **OCPP** — certification/test-case momentum plus active field pain makes profile-aware replay unusually actionable.
3. **RDAP + EPP** — compelling because Rust already has credible RDAP substrate and ICANN-adjacent operational context.
4. **OpenADR** — now that Rust VEN/VTN implementations exist, scenario/evidence layers could materially accelerate adoption.
5. **IFC / BIM** — conformance-first workbench looks more promising than trying to outbuild mature authoring tools.


## Frontier queue — 2026-03-06 (71)

1. **EPCIS + CBV** — strongest cross-industry case in this pass; traceability, lineage, and recall evidence have broad adoption surface and clear standards gravity.
2. **SIP + SDP + RTP** — active Rust substrate plus never-ending interop pain make a replay/evidence layer unusually credible.
3. **AS4 + Peppol eDelivery** — strong B2B/e-government leverage if kept discovery/trust/evidence-first rather than platform-ambitious.
4. **ONVIF + RTSP** — practical value for security/video stacks; profile-aware camera bundles could materially reduce field debugging time.
5. **DLMS/COSEM** — high infrastructure relevance, but success depends on keeping scope to utility-profile evidence rather than full smart-meter platforms.


## Frontier queue — 2026-03-06 (72)

1. **DCSA eBL + PINT** — recent production interoperability milestones make portable dispute/onboarding bundles more timely than they looked even a year ago.
2. **OPC UA PubSub + UAFX** — strongest industrial bet if scoped to timing/metadata/profile evidence instead of generic OPC UA breadth.
3. **GTFS + GTFS Realtime** — high public utility and unusually clear leverage from schedule-aware semantic validation.
4. **OGC API Features + CQL2** — GeoRust substrate is finally good enough that conformance/query lockfiles might stick.
5. **STIX 2.1 + TAXII 2.1** — strong security standards case; worth watching for maintainer-energy and policy-scope risk.

Last updated: 2026-03-06



## Frontier queue — 2026-03-06 (74)

1. **UBL + EN16931 + Peppol/PINT** — strongest mix of adoption surface, active release cadence, and missing profile/evidence tooling.
2. **AMWA NMOS** — compelling because official testing already exists but topology/activation evidence is still messy in practice.
3. **SDMX 3.0** — unusually good “machine-readable standards + public API + early Rust substrate” setup for a conformance workbench.
4. **LTI 1.3 + Advantage** — strong certification/replay case now that Rust has credible LTI libraries.
5. **3MF** — conformance-suite momentum and packaging semantics make this more valuable than yet another raw parser.

Last updated: 2026-03-06



## Frontier queue — 2026-03-06 (75)

1. **Crossref 5.4.0 + JATS 1.4** — strongest case in this pass because the transformation/validation seam is active, standards-driven, and now close enough to fresh Rust substrate.
2. **OpenDRIVE + OpenSCENARIO** — official checker infrastructure raises the value of a neutral replay/diff crate above one more parser.
3. **DDEX ERN + MEAD** — compelling because partner onboarding pain is real and Rust is finally getting plausible parser/builder substrate.
4. **OCFL + BagIt Profiles** — preservation workflows would benefit from a boring artifact for transfer/storage bugs, but the maintainer pool is narrower than for publishing or automotive ecosystems.
5. **CCSDS CFDP** — high-value niche where a small, careful replay/evidence layer could materially improve mission integration debugging.

Last updated: 2026-03-06



## Added 2026-03-06 (76)
- **P-0332 (Medium-High)** EPUB 3.3 + EPUBCheck + OPDS 2.0 Interop & Evidence Kit — strong publishing/library value; the sharp idea is validator normalization plus publication/catalog seam debugging.
- **P-0333 (High)** BIDS + NIfTI Conformance & Dataset Evidence Kit — unusually leverageable for research-data QA because the official validator exists but replayable, redactable Rust evidence does not.
- **P-0334 (Medium-High)** STAC 1.1 + STAC API Validation & Replay Kit — real Rust substrate and large ecosystem; replayable query behavior is the differentiator.
- **P-0335 (Medium-High)** LAS 1.4/1.5 + LAZ 1.4 + COPC Interop & Evidence Kit — strong geospatial delivery/QA value if kept on metadata/package semantics rather than analysis.
- **P-0336 (Medium)** MARC 21 + BIBFRAME Conversion Workbench Kit — strategically important migration seam, though probably a narrower maintainer pool than publishing/geospatial data proposals.


## Watchlist additions (2026-03-06-77)
- **P-0337 GA4GH htsget + refget + Crypt4GH Interop & Evidence Kit** — strongest of this pass; unusually good fit for compliance + reference-integrity + redactable evidence.
- **P-0338 xAPI 2.0 + cmi5 Conformance & Replay Kit** — good “profile lockfile + replay” candidate with active Rust substrate.
- **P-0339 NETCONF + YANG + RESTCONF Conformance & Evidence Kit** — promising if kept controller-neutral and capability-lock focused.

## New candidates (2026-03-06, pass 78)
- **P-0342 OpenUSD Core Spec 1.0 + USDZ Conformance & Evidence Kit** — validator-aware scene/package replay and portable bug bundles.
- **P-0343 CityGML 3.0 + CityJSON 2.0 Conformance & Conversion Workbench Kit** — subset-aware validation, conversion-loss reports, and procurement-friendly evidence.
- **P-0344 netCDF + CF Conventions + OPeNDAP Interop & Evidence Kit** — CF-aware validation, subset replay, and semantic dataset diffs.
- **P-0345 CAP 1.2 + IPAWS Interop & Evidence Kit** — profile-pinned emergency-alert validation and redactable exchange bundles.
- **P-0346 MusicXML 4.0 + MEI Interop & Evidence Kit** — notation conversion-loss reporting, semantic diffs, and score bug bundles.


## Frontier queue — 2026-03-06 (79)

1. **WARC + CDXJ + WACZ** — strongest fit for the archive’s missing-middle thesis because the cross-layer preservation/replay seam is clear and Rust substrate now exists.
2. **glTF 2.0 + KTX 2.0** — official validator plus current crate momentum makes a profile/evidence workbench newly plausible.
3. **MCAP + rosbag2** — excellent operational multiplier for robotics teams if kept focused on schema/channel/clock evidence.
4. **miniSEED 3 + StationXML + SeedLink** — very neglected and important, but probably best started with a tight interchange/replay core.
5. **MPEG-DASH + DASH-IF** — useful conformance-wrapper candidate, especially if profile packs stay narrow and validator-first.

Last updated: 2026-03-06


## Frontier queue — 2026-03-06 (80)

1. **ISO 20022 + CBPR+ / HVPS+ / SEPA** — strongest mix of economic surface, current migration pressure, and missing profile/evidence tooling.
2. **LSP + DAP + LSIF** — unusually high Rust-ecosystem leverage because protocol crates exist but portable interop testing is still weak.
3. **OME-Zarr / NGFF** — official validator + fresh Rust metadata/Zarr substrate makes a conformance-first workbench newly realistic.
4. **WMO GRIB2 + BUFR** — table/version pinning and ecCodes normalization could save real operational pain across weather-data stacks.
5. **FITS + WCS + VOTable** — strong archive/science value if scope stays coordinate- and export-seam focused rather than trying to absorb the whole VO ecosystem.

Last updated: 2026-03-06

## Frontier queue — 2026-03-06 (81)

1. **Apache Iceberg REST Catalog + Delta Kernel / UniForm** — strongest near-term multiplier because open lakehouse adoption is high and the missing value is squarely in the metadata/interop seam.
2. **RDF 1.2 + SPARQL 1.2 + SHACL 1.2** — broad standards surface with real Rust substrate and a very crisp canonicalization/evidence gap.
3. **VCF 4.5 + BCF 2.2 + CSI/Tabix** — especially strong because Rust already has excellent low-level format support, making the missing workbench layer newly plausible.
4. **OData 4.01/4.02 + CSDL** — large practical API surface, but best started with a careful metadata/query core before vendor overlays proliferate.
5. **Amazon Ion + PartiQL** — narrower adopter base, but unusually differentiated and a good fit for a semantic replay workbench.

Last updated: 2026-03-06


## Frontier queue — 2026-03-06 (82)

1. **ONNX + ONNX Runtime + Backend Test** — strongest fit for the archive’s current thesis because the missing value is clearly in model/opset/backend replay rather than raw model loading.
2. **HL7 v2.x + MLLP + Message Profiles** — broad operational footprint and clear need for redacted, replayable evidence in hospital integrations.
3. **OSCAL 1.1.x cross-model workbench** — compelling because Rust now has substrate, but package linkage and validation evidence are still underbuilt.
4. **OMA LwM2M 1.2 + OMNA registry** — high-value IoT/fleet seam if kept object-version and registration-focused.
5. **UN/EDIFACT syntax + directories** — neglected but important partner-onboarding/debugging seam; best started with a tight release/profile core.

Last updated: 2026-03-06


## Frontier queue — 2026-03-07 (95)

1. **Promoted on 2026-03-16 to P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — keep future work focused on task-first decision packs above today's generic search substrate, and keep it visibly distinct from crate health, trust scoring, façade crates, and blessing/stdlib debates.
2. **Edition-drift witness kit** — adjacent to P-0427 and potentially strong if it stays focused on edition deltas and migration receipts rather than general linting.
3. **Cargo explanation receipts for cache/build decisions** — adjacent to P-0428; only worthwhile if it sharpens “why did Cargo do this?” rather than duplicating existing build-insight proposals.
4. **Public syntax / macro expansion evidence kits** — promising only if they sit cleanly between current rustc_public work and existing rustdoc/build proposals.
5. **Unsafe-contract witness corpora** — likely high value, but should be checked against existing unsafe/audit proposals before promotion.

Last updated: 2026-03-07


## Frontier queue — 2026-03-07 (96)

1. **Cargo test harness/reporting interop kit** — only worthwhile if it sharpens the handoff between libtest/custom harnesses/Cargo reporting instead of duplicating the archive’s existing run-record and test-artifact proposals.
2. **Public-API/boundary release gate kit** — promising as a follow-on above P-0431 if it stays focused on release-review receipts rather than generic linting.
3. **Toolchain profile lock / hardening profile pack** — adjacent to P-0430 and possibly strong if it remains a policy/receipt layer rather than a new distribution channel.
4. **Cargo resolver explanation receipts** — adjacent to P-0432 and only worth adding if it can explain feature-resolution surprises without collapsing back into generic metadata tooling.
5. **Safety-case evidence glue for Rust toolchains** — adjacent to P-0433, but must avoid overpromising certification and instead stay narrowly evidence-oriented.

Last updated: 2026-03-07


## Frontier queue — 2026-03-07 (97)

1. **Exploit-mitigation profile pack** — adjacent to P-0434/P-0430 and only worth adding if it sharpens hardening-profile receipts instead of duplicating sanitizer/sysroot work.
2. **Single-file package publication handoff kit** — adjacent to P-0435 and promising only if it stays focused on repro/tutorial/archive handoff rather than becoming a new package manager.
3. **Cargo cache contention explainer** — adjacent to P-0436 and worthwhile only if it sharpens “why are these processes blocking?” without scraping too much unstable internals.
4. **Backend bug minimization corpus kit** — adjacent to P-0437 and only strong if it stays repro-oriented rather than trying to benchmark everything.
5. **Reflection/comptime migration receipts** — still promising, but should be revisited only if the language experiment matures enough that a workflow layer is clearer.

Last updated: 2026-03-07


## Frontier queue — 2026-03-07 (98)

1. **Ergonomic ref-counting workflow receipts** — promising if it focuses on migration/explainability for `.use` / share-style ergonomics rather than becoming a broad smart-pointer framework.
2. **In-place initialization evidence/workbench kit** — newly sharper after this pass, but should avoid duplicating P-0440 and instead focus on constructor/pinning/address-stability receipts.
3. **Cargo rebuild-explainer receipts** — adjacent to P-0438 and only worth adding if it can explain actual Cargo rebuild choices without overclaiming knowledge of unstable internals.
4. **Reflection/comptime adapter packs** — follow-on work above P-0439 if specific downstream categories (schema/CLI/editor/config) prove they need richer annotations.
5. **C++ exception/panic boundary policy kit** — adjacent to P-0441 and only worthwhile if it stays narrowly about boundary policy/evidence instead of generic FFI advice.

Last updated: 2026-03-07


## Frontier queue — 2026-03-07 (99)

1. **Polonius / borrowck transition witness kit** — promising if it stays clearly distinct from P-0442 and focuses on borrow-check outcome drift rather than generic compile-fail workflows.
2. **Namespace release-gate receipts** — adjacent to P-0443 and only worthwhile if it sharpens actual rollout/release review instead of duplicating the planner.
3. **Kernel subsystem waiver matrix kit** — adjacent to P-0444 and only strong if it stays narrowly about waiver policy/evidence and not full build orchestration.
4. **Const docs/report adapters** — adjacent to P-0445 and valuable only if downstream docs/release-note workflows prove they need first-class rendering.
5. **Externally-implementable-items migration kit** — promising if it stays focused on transition planning and capability ledgers rather than broad trait-system theory.

Last updated: 2026-03-07



## Frontier queue — 2026-03-07 (100)

1. **Crate slicing soundness/adoption kit** — newly stronger now that official 2026 goal text and a `cargo-slicer` prototype exist; future work should stay focused on receipts, waivers, and fallback-to-full-crate behavior rather than trying to own slicing end-to-end.
2. **Namespace release-gate receipts** — still adjacent to P-0443 and only worth adding if it sharpens rollout review instead of duplicating the planner.
3. **Pinned-drop / pin-ergonomics casebook kit** — adjacent to P-0447 and only strong if it stays tightly on design feedback receipts rather than generic pin helpers.
4. **Share-trait docs/report adapters** — adjacent to P-0448 and worthwhile only if real teams need first-class rendering or release-note artifacts.
5. **Trait-evolution codemod assists** — adjacent to P-0449 and only worth promoting if a clearly conservative, semver-aware subset emerges.

Last updated: 2026-03-07


## Watchlist additions (2026-03-07-101)
- **P-0451 Cfg Availability Ledger Kit** — broad maintainer leverage if kept ledger-first; avoid drifting into “build a better rustdoc”.
- **P-0450 Parallel Front-End Parity Lab Kit** — strong while stabilization work is active; keep scope on parity receipts and reduced repros, not generic benchmarking.
- **P-0452 Externally Implementable Item Adoption Kit** — promising if it stays semver/migration/diagnostics-focused rather than becoming DI or linker abstraction.
- **P-0453 Safety Contract Consumer Kit** — strategically important, but should prove its value with extraction/diff/runtime receipts before ambitious multi-tool translation.



## Watchlist additions (2026-03-07-102)
- **P-0454 ABI Coherence Profile Kit** — strongest if it stays on whole-program flag contracts, exemption ledgers, and sysroot receipts rather than becoming a generic compiler-flags helper.
- **P-0455 Doctest Extraction & Pipeline Kit** — promising while rustdoc extraction and grouping work are moving; keep scope on manifests, rewrites, and runner receipts instead of rebuilding rustdoc.
- **P-0456 Formality Counterexample Bridge Kit** — strategically important, but should prove value with minimized divergence bundles before ambitious multi-engine orchestration.
- **P-0457 External Toolchain Handshake Kit** — worth pursuing if it remains a contract artifact for non-Cargo orchestrators rather than drifting into “replace Cargo” ambition.



## Watchlist additions (2026-03-07-103)
- **P-0458 Async Dyn Transition Kit** — strong while async dyn support is still converging; keep scope on recipe comparison and migration receipts rather than broad async refactoring.
- **P-0459 Clippy Safety Profile & Waiver Kit** — high practical leverage if it stays artifact-first and does not overclaim certification or official policy status.
- **P-0460 Unsafe Field Invariant Ledger Kit** — strategically novel, but should prove value with a tiny vocabulary and conservative mutation witnesses before deeper analysis.
- **P-0461 Edition Drift Witness Kit** — broadly adoptable if it remains a rehearsal/evidence layer above `cargo fix --edition` instead of becoming a generic codemod engine.



## Frontier queue — 2026-03-07 (104)

1. **Invocation-reuse compatibility kit** — newly stronger now that “Incremental Systems Rethought” is a 2026 goal; only worth adding if it sharpens `check`/`build`/`clippy` compatibility receipts instead of duplicating shared-cache and build-analysis proposals.
2. **Edition-scoped API surface planner** — promising after the new standard-library-across-editions goal, but only if it stays on migration/review artifacts rather than generic docs rendering.
3. **Open-enum ABI readiness kit** — potentially strong if it remains narrowly about extension/ABI receipts for separately compiled boundaries rather than becoming another broad enum helper crate.
4. **BorrowSanitizer suppression / expectation pack** — adjacent to P-0465 and only worthwhile if real teams need structured expectation files beyond evidence bundles.
5. **Sized-hierarchy docs/report adapters** — adjacent to P-0464 and worth revisiting only if release-note or rustdoc workflows prove they need first-class rendering.

Last updated: 2026-03-07


## Watchlist additions (2026-03-07-104)
- **P-0462 Crate Slicing Soundness & Adoption Kit** — strongest if it stays on candidate/fallback/benefit receipts rather than turning into a new slicer.
- **P-0463 Libtest JSON Interop Kit** — broad leverage if it remains schema-lock and interop focused instead of becoming a runner replacement.
- **P-0464 Sized Hierarchy & Extern-Type Readiness Kit** — strategically useful if it stays audit-first and does not overclaim final language semantics.
- **P-0465 BorrowSanitizer Workflow & Evidence Kit** — high-value if it remains finding-bundle oriented and does not pretend a clean run proves safety.

## Frontier queue — 2026-03-07 (105)

1. **Python wheel ABI / free-threading shipkit** — newly strong because PyO3/maturin/Python docs now make the compatibility seam explicit; future work should stay on wheel-policy and release receipts rather than becoming a general Python packaging tool.
2. **Apple XCFramework / SwiftPM shipkit** — newly strong because Swift bindings and XCFramework helpers already exist; the sharper missing layer is slice/checksum/privacy/origin receipts above them.
3. **Cargo rebuild/cache explanation receipts** — still promising because the survey keeps pointing at build/storage pain, but only worthwhile if it sharpens reviewable decisions instead of duplicating existing build-insight proposals.
4. **Sanitizer expectation/suppression packs** — adjacent to P-0434/P-0465 and only worth promoting if teams clearly need structured expectation layers beyond evidence bundles.
5. **Python/Apple release-drift diffing** — promising follow-on work only after P-0466/P-0467 stabilize their core receipt vocabularies.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-105)
- **P-0466 Python Wheel ABI & Free-Threading ShipKit** — strongest if it remains policy/matrix/receipt-first and does not drift into a new upload tool.
- **P-0467 Apple XCFramework & SwiftPM ShipKit** — strongest if it remains slice/checksum/privacy/origin-first and does not become a full Xcode generator.


## Frontier queue — 2026-03-07 (106)

1. **Cargo resolver explanation receipts** — promoted to **P-0468** because Cargo's resolver/tree/plumbing surfaces are now strong enough that the sharper missing layer is a feature/version/duplicate-build why-bundle, not another metadata dump.
2. **Cargo rebuild explanation receipts** — promoted to **P-0469** because survey/build-dir/relink evidence now makes a compact per-run rebuild witness sharper than generic performance dashboards.
3. **Cargo cache contention explainer** — still promising, but only if later work stays narrowly on blocking/lease facts instead of duplicating P-0469's broader rebuild story.
4. **Public-API/boundary release gate kit** — still promising as a follow-on above P-0431 and P-0438 if it remains release-review-first.
5. **Python/Apple release-drift diffing** — still promising follow-on work once P-0466 and P-0467 have stable receipt vocabularies.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-106)
- **P-0468 Cargo Resolver Explanation Kit** — strongest if it remains cause-chain / duplicate-build / diff-first and does not collapse back into raw graph export.
- **P-0469 Cargo Rebuild Explanation Kit** — strongest if it remains a per-run why-bundle and does not turn into a full analytics warehouse.


## Frontier queue — 2026-03-07 (107)

1. **Cargo artifact handoff kit** — promoted to **P-0471** because Cargo’s produced-artifact JSON, unstable `artifact-dir`, and output-tracking work now make a downstream handoff manifest sharper than another bespoke release script.
2. **Cargo package review kit** — promoted to **P-0470** because packaging docs still imply manual inspection and `.crate` drift review; the missing layer is a publish-readiness receipt.
3. **Cargo lints adoption receipts** — still promising if it stays on profile inheritance / waiver / workspace receipt workflows rather than becoming a lint runner.
4. **Artifact-sidecar contract kit** — adjacent to P-0471 and only worth adding if SBOM or similar sidecars converge enough to justify a smaller standardized vocabulary.
5. **Publish-surface / provenance join layer** — promising follow-on work only after P-0470 and P-0015 have stable core artifacts.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-107)
- **P-0470 Cargo Package Review Kit** — strongest if it remains review/diff/policy-first and does not become a new publish orchestrator.
- **P-0471 Cargo Artifact Handoff Kit** — strongest if it remains manifest/receipt-first and does not drift into a full release platform.


## Frontier queue — 2026-03-07 (108)

1. **Docs.rs build parity / issue bundles** — promoted to **P-0472** because docs.rs now exposes enough documented environment and metadata surface that the sharper missing layer is a preflight/diff/limit receipt, not another docs runner.
2. **Cargo lints adoption receipts** — promoted to **P-0473** because stable `workspace.lints` and emerging Cargo-lint surfaces now make inheritance / waiver / rollout artifacts sharper than another lint wrapper.
3. **Artifact-sidecar contract kit** — still promising, but only if SBOM or related sidecars converge enough to justify a compact common vocabulary above P-0471.
4. **Publish-surface / provenance join layer** — still promising once P-0470 and P-0015 have stable core receipts.
5. **Docs coverage review bundles** — promising follow-on work only if rustdoc coverage JSON and docs maintenance workflows converge enough to justify a separate receipt layer from P-0472.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-108)
- **P-0472 Docs.rs Build Parity & Evidence Kit** — strongest if it remains receipt/diff/limit-first and does not become a new docs host or full builder emulator.
- **P-0473 Cargo Lints Adoption Receipt Kit** — strongest if it remains inheritance/waiver/rollout-first and does not become a generic lint runner.


## Frontier queue — 2026-03-07 (109)

1. **Cargo config-layer receipts** — promoted to **P-0474** because Cargo now has enough config substrate that the sharper missing layer is an effective-config / origin-trace / redacted support bundle, not another parser.
2. **Rustdoc mergeable-info handoff** — promoted to **P-0475** because `doc.parts` / merge / finalize substrate now exists, but ordinary maintainers still lack a manifest / compatibility / finalize receipt workflow.
3. **Docs coverage review bundles** — still promising, but only if rustdoc coverage and docs maintenance workflows converge enough to justify a layer distinct from P-0472 and P-0475.
4. **Publish-surface / provenance join layer** — still promising once P-0470 and P-0015 have stable core receipts.
5. **Artifact-sidecar contract kit** — still promising only if SBOM or adjacent sidecars converge enough to justify a compact vocabulary above P-0471.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-109)
- **P-0474 Cargo Config Layer Receipt Kit** — strongest if it remains origin/redaction/diff-first and does not become a generic config framework.
- **P-0475 Rustdoc Mergeable Info Handoff Kit** — strongest if it remains manifest/compatibility/finalize-first and does not become a new docs host or UI.


## Frontier queue — 2026-03-07 (110)

1. **Docs coverage review bundles** — promoted to **P-0476** because rustdoc coverage JSON and rustdoc JSON now make a review bundle sharper than another docs scorecard.
2. **Publish-surface / provenance join layer** — promoted to **P-0477** because package review, registry checksums, and trusted-publishing facts now make a post-publish receipt sharper than another CI publisher.
3. **Artifact-sidecar contract kit** — still promising only if SBOM or adjacent sidecars converge enough to justify a compact vocabulary above P-0471.
4. **Cargo cache contention explainer** — still promising if it stays narrowly on blocking/lease facts rather than broad rebuild analytics.
5. **Python/Apple release-drift diffing** — still promising follow-on work once P-0466 and P-0467 have stable receipt vocabularies.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-110)
- **P-0476 Rustdoc Coverage Review Bundle Kit** — strongest if it remains API-aware docs review and does not become a generic dashboard.
- **P-0477 Cargo Publish Receipt Join Kit** — strongest if it remains checksum/identity/join-first and does not become another publish platform.



## Frontier queue — 2026-03-07 (111)

1. **Cargo future-incompat triage** — promoted to **P-0478** because Cargo already has display/report substrate; the sharper missing layer is a durable owner/waiver/remediation bundle.
2. **Artifact-sidecar contract kit** — promoted to **P-0479** because sidecar conventions are now emerging enough that a narrow attachment/schema contract is sharper than another general artifact exporter.
3. **Cargo cache contention explainer** — still promising if it stays narrowly on blocking/lease facts rather than broad rebuild analytics.
4. **Python/Apple release-drift diffing** — still promising follow-on work once P-0466 and P-0467 have stable receipt vocabularies.
5. **Public-API release gate kit** — still promising as a follow-on above P-0431 and P-0438 if it remains release-review-first.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-111)
- **P-0478 Cargo Future-Incompat Triage Kit** — strongest if it remains owner/waiver/remediation-first and does not become another generic diagnostics viewer.
- **P-0479 Cargo Artifact Sidecar Contract Kit** — strongest if it remains attachment/schema/diff-first and does not turn into a second general artifact manifest layer.


## Watchlist additions (2026-03-07-112)
- **P-0480 Cargo Global Cache Policy & GC Receipt Kit** — promising if it stays on Cargo-home inventory, dry-run policy, and cleanup receipts instead of drifting into a general-purpose disk janitor.
- **P-0481 Doctest Runtool Profile Kit** — promising if it stays on runner profiles, target matrices, and ignore audits instead of becoming a broad cross-device test framework.


## Frontier queue — 2026-03-07 (113)

1. **Python/Apple release-promise drifting** — promoted to **P-0482** because foreign-language shipping substrate is now real enough that the sharper missing layer is a consumer-promise diff/impact artifact, not another builder.
2. **Public-API release readiness bundles** — promoted to **P-0483** because semver checks, public-API diffing, public-dependency work, and docs-surface metrics now make a joined release-review artifact sharper than another individual analyzer.
3. **Cargo cache contention explainer** — still promising if it stays narrowly on blocking/lease facts rather than duplicating P-0469 or P-0480.
4. **Debugger support-pack refresh** — still promising only if it becomes a compact compatibility/receipt workflow above P-0083 rather than another general debugger wishlist.
5. **Foreign-SDK consumer doctor** — still promising follow-on work once P-0482 stabilizes its promise vocabulary and receipts.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-113)
- **P-0482 SDK Release Promise Drift Kit** — strongest if it remains consumer-promise/diff/impact-first and does not become a second build-and-upload tool.
- **P-0483 Public API Readiness Bundle Kit** — strongest if it remains joined public-contract review and does not collapse back into a generic compatibility platform.


## Added 2026-03-07 (114)
- **P-0484 Toolchain & Target Support Contract Kit** — strong day-to-day maintainer value because it joins support intent, observed environment, docs posture, and drift into one contributor/reviewer artifact.
- **P-0485 Verification Campaign Workbench Kit** — strategic assurance value because it gives Rust’s growing verification ecosystem one honest obligation/trust/policy/evidence bundle instead of more scattered logs and notes.


## Frontier queue — 2026-03-07 (115)

1. **Debuggability support contracts** — promoted to **P-0486** because Rust already has meaningful debugging substrate, and the sharper missing layer is now a support-posture/symbol-receipt workflow rather than another debugger wishlist.
2. **Foreign-SDK consumer doctor** — promoted to **P-0487** because P-0482 covered producer-side release promises, but downstream adoption diagnosis is still its own unserved seam.
3. **Cargo cache contention explainer** — still promising if it stays narrowly on blocking/lease facts rather than duplicating P-0469 or P-0480.
4. **Debugger formatter/conformance refresh** — still promising only if it becomes a clean follow-on above P-0083 and P-0486 instead of a broad debugger platform.
5. **Other foreign package ecosystems** — still promising only after the Python/Apple consumer-diagnosis vocabulary proves stable.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-115)
- **P-0486 Debuggability Support Contract Kit** — strongest if it remains support-posture/symbol-layout/diff-first and does not become a new debugger UI or crash backend.
- **P-0487 Foreign SDK Consumer Doctor Kit** — strongest if it remains consumer-diagnosis-first and does not collapse back into a second shipkit or release bot.


## Added 2026-03-07 (116)
- **P-0488 Cargo Minimal-Version Witness Kit** — strong day-to-day crate-maintainer value because it turns lower-bound checking into one honest proof/blame/waiver artifact instead of a flaky nightly CI job and scattered notes.
- **P-0489 Cargo Build-Dir Consumer Transition Kit** — strategically useful for Cargo-adjacent tooling because it gives scripts and helpers a migration path away from internal build-dir scraping as Cargo’s layout evolves.


## Frontier queue — 2026-03-07 (116)

1. **Lower-bound dependency witnesses** — promoted to **P-0488** because Cargo’s lower-bound substrate and new minimum-version lint now make a reviewable witness sharper than a generic dependency updater or compatibility platform.
2. **Build-dir consumer transitions** — promoted to **P-0489** because Cargo’s evolving build-dir story now clearly creates a tooling-migration seam distinct from cache policy or final-artifact handoff.
3. **Debugger formatter/conformance refresh** — still promising only if it becomes a clean follow-on above P-0083 and P-0486 instead of a broad debugger platform.
4. **Other foreign package ecosystems** — still promising only after the Python/Apple consumer-diagnosis vocabulary proves stable enough to generalize.
5. **Cargo cache contention explainer** — still promising if it stays narrowly on live blocking facts rather than duplicating P-0436, P-0480, or P-0489.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-116)
- **P-0488 Cargo Minimal-Version Witness Kit** — strongest if it remains lower-bound-proof/blame/waiver-first and does not turn into a generic dependency updater.
- **P-0489 Cargo Build-Dir Consumer Transition Kit** — strongest if it remains audit/path-contract/transition-first and does not collapse into another cache manager or profiler.


## Added 2026-03-07 (117)
- **P-0490 Cargo Lock Contention Witness Kit** — high practical value because it gives teams one honest artifact for IDE/manual/CI lock waits instead of scattered anecdotes and workaround folklore.
- **P-0491 Debugger Visualizer Compatibility Kit** — useful narrower follow-on because embedded visualizer assets are now a real stable surface, but their backend compatibility is still not boring to review.


## Frontier queue — 2026-03-07 (117)

1. **Cargo lock-contention witnesses** — promoted to **P-0490** because Cargo and rust-analyzer now document enough blocking substrate that the sharper missing layer is a live wait/collision/mitigation artifact.
2. **Debugger visualizer compatibility receipts** — promoted to **P-0491** because stable embedded NatVis/GDB support now makes a narrow backend-matrix follow-on sharper than another broad debugger toolkit.
3. **Other foreign package ecosystems** — still promising only after the Python/Apple consumer-diagnosis vocabulary proves stable enough to generalize.
4. **Cargo compile-time-deps workflow receipts** — still promising if it stays narrowly on tool-only build surfaces and does not collapse back into generic editor/Cargo performance tooling.
5. **Build-std adoption receipts** — still promising if the unstable substrate sharpens enough that a new workflow layer would not duplicate P-0116 or related build-std ideas.

## Watchlist additions (2026-03-07-117)
- **P-0490 Cargo Lock Contention Witness Kit** — strongest if it remains live-blocking/wait/mitigation-first and does not become another profiler, scheduler, or cache manager.
- **P-0491 Debugger Visualizer Compatibility Kit** — strongest if it remains asset/back-end matrix first and does not collapse into P-0083’s formatter-pack ambition or P-0486’s broader support contract.


## Added 2026-03-07 (119)
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — high practical leverage because Cargo now has a documented tool-only compile surface, but maintainers still lack one honest artifact for what editor/wrapper workflows actually built and when they must fall back to a real build.
- **P-0495 Cargo Artifact Dependency Adoption Kit** — strong targeted leverage because Cargo artifact dependencies are real enough to justify a contract/env-var/fallback layer, but still too unstable and niche for a simple “just use it” answer.


## Frontier queue — 2026-03-07 (119)

1. **Compile-time-deps workflow receipts** — promoted to **P-0494** because Cargo now explicitly documents a tool-only compile surface intended for tools, while the `cargo check` policy boundary keeps the missing layer firmly in parity/fallback artifacts rather than build correctness claims.
2. **Artifact-dependency adoption receipts** — promoted to **P-0495** because Cargo’s artifact-dependency substrate plus RFC 3028 / RFC 3176 now make a contract/target/env-var/fallback layer sharper than another generic build helper.
3. **Other foreign package ecosystems** — still promising once the Python/Apple and generic foreign-consumer vocabulary proves stable enough to generalize to Node/npm, NuGet, or similar ecosystems.
4. **Invocation-reuse compatibility kit** — still promising if the 2026 incremental-systems work sharpens a clean check/build/clippy reuse receipt distinct from P-0490 and P-0494.
5. **Build-std adoption receipts** — still promising only if a new workflow layer would sharpen support/adoption facts without duplicating P-0430 or related sanitizer/toolchain proposals.

## Watchlist additions (2026-03-07-119)
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — strongest if it remains tool-surface/parity/fallback-first and does not turn into a rust-analyzer fork, a new checker, or a false equivalence layer between `cargo check` and `cargo build`.
- **P-0495 Cargo Artifact Dependency Adoption Kit** — strongest if it remains contract/target/env-var/fallback-first and does not collapse into another final-artifact exporter, package manager, or Cargo syntax proposal.


## Added 2026-03-07 (120)
- **P-0496 Cargo Vendor & Source Parity Kit** — high practical leverage because vendored and source-replaced dependency workflows are common, yet maintainers still lack one honest artifact for where resolution actually came from and whether offline claims are true.
- **P-0497 CPU Baseline & Runtime Dispatch Contract Kit** — valuable cross-domain leverage because Rust already has real CPU-feature substrate, but maintainers still lack one compact release artifact for hardware-support promises and fallback posture.


## Frontier queue — 2026-03-07 (120)

1. **Vendor/source-parity receipts** — promoted to **P-0496** because Cargo now has serious source-management substrate, while the sharper missing layer is a source-origin and offline-honesty artifact rather than another mirror or registry.
2. **CPU baseline/runtime-dispatch contracts** — promoted to **P-0497** because Rust already has codegen knobs and runtime detection, while the sharper missing layer is a downstream hardware-support promise rather than another SIMD abstraction.
3. **Other foreign package ecosystems** — still promising once the Python/Apple and generic foreign-consumer vocabulary proves stable enough to generalize to Node/npm, NuGet, or similar ecosystems.
4. **Invocation-reuse compatibility kit** — still promising if the 2026 incremental-systems work sharpens a clean check/build/clippy reuse receipt distinct from P-0490 and P-0494.
5. **Build-std adoption receipts** — still promising only if a new workflow layer would sharpen support/adoption facts without duplicating P-0430 or related sanitizer/toolchain proposals.

## Watchlist additions (2026-03-07-120)
- **P-0496 Cargo Vendor & Source Parity Kit** — strongest if it remains source-origin/parity/offline-honesty-first and does not collapse into another mirror, registry, or package-review system.
- **P-0497 CPU Baseline & Runtime Dispatch Contract Kit** — strongest if it remains hardware-support/dispatch/fallback-first and does not turn into another SIMD abstraction, benchmark harness, or compiler-wrapper fantasy.


## Added 2026-03-08 (122)
- **P-0500 JAR/JNI Native ShipKit** — promoted because the JVM now looks like the next clean foreign-package sibling: real JNI/Maven substrate exists, but maintainers still lack an honest classifier/load/native-access contract.

## Frontier queue — 2026-03-08 (122)

1. **JAR/JNI ship contracts** — promoted to **P-0500** because the package/runtime contract has become sharper than generic Rust/Java interop framing.
2. **Cross-ecosystem support-contract generalization** — still promising once enough producer-side package-contract vocabularies stabilize.
3. **Invocation-reuse compatibility kit** — still promising if incremental-systems work creates a distinct check/build/clippy reuse receipt.
4. **Build-std adoption receipts** — still promising only when it can stay adoption-first rather than duplicating existing sysroot evidence work.


## Added 2026-03-08 (123)
- Promote **P-0501 RubyGems Native Extension ShipKit** as the next concrete foreign-package ecosystem seam.
- Use `meta/foreign-package-contract-vocabulary.md` before any future attempt to generalize Python/Apple/Node/NuGet/JVM/Ruby shipping contracts.
- Keep future foreign-package work biased toward **review artifacts** (artifact matrices, loader receipts, support-risk bundles) rather than raw binding/framework substrate.

## Frontier queue — 2026-03-08 (123)
1. Cross-ecosystem support-contract vocabulary and schemas
2. RubyGems fat-gem/package-contract fixtures
3. Invocation-reuse compatibility receipts
4. Build-std adoption/support receipts



## Debug support stack refresh — 2026-03-08 (126)

1. **P-0486 Debuggability Support Contract Kit** — promoted as the strongest next non-Cargo incubation target because debugging remains a top ecosystem pain while Rust already has enough substrate that the missing layer is now a support-posture / symbol-layout / drift bundle rather than another debugger wishlist.
2. **P-0493 Source Path Hygiene & Debug Source Kit** — strengthened because path trimming/remapping and `rust-src` / `rustc-dev` lookup now clearly form their own support seam instead of a footnote inside broad debuggability.
3. **P-0491 Debugger Visualizer Compatibility Kit** — remains real but narrower; strongest once it reuses broader support vocabulary instead of acting like a universal debugger platform.

### Watchlist additions (2026-03-08-126)
- **P-0486 Debuggability Support Contract Kit** — strongest if it remains support-posture / symbol-layout / diff-first and does not become a new debugger UI, crash backend, or giant IDE integration.
- **P-0493 Source Path Hygiene & Debug Source Kit** — strongest if it remains remap/trim-path/source-component diagnosis first and does not collapse into P-0486 or a full source-packaging system.
- **P-0491 Debugger Visualizer Compatibility Kit** — strongest if it remains asset/backend-matrix-first and does not silently absorb broader symbol/source support posture.

# Research ledger — 2026-03-08 frontier pass (137)

## Sources consulted
- 2025 State of Rust survey results
- Rust debugging survey 2026
- Cargo profiles reference
- rustc codegen options reference
- debugger_visualizer reference
- Cargo unstable `trim-paths` docs
- Cargo changelog

## Main notes
- The official debug substrate is now explicit enough that the archive should prefer a **support-contract crate** over another vague debugging proposal.
- The most important nuance uncovered in this pass is that support posture can drift even when teams think they are only making “size” or “profile default” changes.
- The right 0.1 artifact family is small: receipt, symbol layout, visualizer manifest, support report, and optional drift diff.

# Research ledger — 2026-03-08 frontier pass (128)

## Sources consulted
- Cargo build scripts reference
- Cargo config reference (`target.<triple>.<links>`)
- Cargo unstable features (`any build script metadata`)
- Cargo changelog (`cargo::error`, warnings handling)
- `system-deps` docs
- `vcpkg` docs
- Cargo issue #15038
- Cargo issue #15010 / build-dir layout tracking
- 2025 State of Rust survey results

## Kept together
- concrete crate-split planning for P-0046 / P-0059 / P-0058
- tiny example bundles showing what another human would receive
- build-script/native-deps artifact vocabulary

## Result
- Did **not** add another top-level proposal.
- Added a new implementation brief for the native-build stack.
- Added three missing schema files and three tiny example scenario bundles.
- Promoted P-0046 in prioritization from medium-high to high inside this frontier.

## Freshness anchors
- Re-check Cargo's `target.<triple>.<links>` override docs before freezing override-handoff language in P-0058.
- Re-check “any build script metadata” before promising too much stability around metadata propagation.
- Re-check build-script error presentation issues before assuming upstream Cargo removed the need for P-0046-style summaries.

## Common false gap patterns from this pass
1. “Need another native-deps proposal” when the archive actually needed **example bundles and crate-split planning**.
2. “Override paths are edge cases” when Cargo's `links` overrides make them part of the real workflow contract.
3. “Text output is enough” when the archive already wants reviewable receipts that tools and humans can both consume.


# Research ledger — 2026-03-08 frontier pass (129)

## Sources consulted
- Cargo external tools / JSON messages
- Cargo config (`target.<triple>.<links>` overrides)
- Cargo unstable features (`metabuild`, `multiple-build-scripts`, `any build script metadata`)
- Cargo issue #14948 (reduce the need for users to write build scripts)
- `system-deps` docs
- `vcpkg` docs

## Kept together
- upstream-fit constraints for P-0046 / P-0059 / P-0058
- new example bundles for hidden warnings, happy-path fake pkg-config, and pkg-config→vendored fallback
- a sharper receiver/artifact matrix for what each crate should hand other people

## Result
- Did **not** add another top-level proposal.
- Added an upstream-fit note and a receipt matrix for the native-build stack.
- Added three new scenario bundles that make the stack more implementation-shaped.

## Freshness anchors
- Re-check Cargo external-tools JSON before making stronger assumptions about build-script-executed fields than Cargo guarantees.
- Refresh P-0046 around three honest constraints: `cargo::warning` visibility is asymmetric, `cargo::error` still has noisy non-zero-exit cases, and build-script JSON may reflect cached rather than live execution.
- Re-check `metabuild` and `multiple-build-scripts` if they stabilize or change shape; P-0059 should not ossify around a nightly snapshot.
- Re-check issue #14948 or successor work before claiming upstream Cargo has truly reduced the need for handwritten build scripts in ordinary crates.

## Common false gap patterns from this pass
1. “Need another native-build crate” when the archive actually needed **upstream-fit planning and example bundles**.
2. “Buildscript tooling must parse raw logs only” when Cargo already exposes machine-readable build-script result substrate.
3. “A vendored fallback success is just success” when the real support truth is often the **ordered backend-attempt receipt**.


# Research ledger — 2026-03-08 frontier pass (130)

## Sources consulted
- Cargo unstable docs (`build-analysis`)
- Cargo changelog (`cargo report timings`, `--compile-time-deps`)
- Cargo tracking issue #15844
- Cargo issues #16472 and #16488
- Cargo external-tools JSON docs
- Cargo timings docs
- 2025 State of Rust survey results

## Kept together
- the current Cargo explainability stack (P-0469 / P-0468 / P-0494)
- the newer upstream `cargo report` / persisted-session substrate
- stable receipt schemas and a tiny example bundle showing what another person would actually receive

## Result
- Did **not** add another top-level proposal.
- Added a build-analysis adoption note and a fresh frontier-salience note.
- Upgraded **P-0469** so it layers more explicitly on Cargo's new report/session substrate.
- Added session-index / timings-pointer schemas and one tiny scenario bundle for imported Cargo sessions.

## Freshness anchors
- Re-check Cargo issue #15844 and the unstable docs before freezing stronger assumptions about session JSON shape or nested-session semantics.
- Re-check #16472 before promising permanent session-selection UX in the imported receipt vocabulary.
- Re-check #16488 or successor docs before assuming the `cargo report` subcommands are fully documented/stable.

## Common false gap patterns from this pass
1. “Need another Cargo performance proposal” when the archive actually needed a **stable adoption layer above new Cargo build-analysis substrate**.
2. “`cargo report` HTML exists, so the machine contract exists” when the durable value is often a smaller redaction-aware receipt.
3. “Upstream solved rebuild explainability” when the tracking issue itself still names schema/programmatic-format questions.

# Research ledger — 2026-03-08 frontier pass (131)

## Sources consulted
- Cargo unstable docs (`build-analysis`, timings note)
- Cargo changelog
- Cargo external-tools JSON docs
- Cargo metadata docs
- Cargo tracking issue #15844
- Cargo issue #16472
- 2025 State of Rust survey results

## Kept together
- the current Cargo explainability stack (P-0469 / P-0035 / P-0468 / P-0494)
- the distinction between per-run support artifacts and multi-session warehousing
- the need for stable downstream contracts above evolving Cargo session/report surfaces

## Result
- Did **not** add another top-level proposal.
- Rewrote **P-0035** around imported-session warehousing, longitudinal diffs, and regression adjudication.
- Added a layering note and a fresh frontier-salience note for the Cargo explainability family.
- Added a new `fixtures/cargo-build-insights/` family with schemas and one tiny scenario bundle.

## Freshness anchors
- Re-check Cargo issue #15844 before freezing stronger assumptions about session shape or stored metrics.
- Re-check #16472 before promising permanent session-selection ergonomics in imported-series workflows.
- Re-check Cargo docs/changelog before assuming current timing-machine-output removals or replacements are still true.

## Common false gap patterns from this pass
1. "Need another Cargo performance crate" when the archive actually needed a **historical warehouse layer** above imported sessions.
2. "P-0469 already covers this" when the real question is about *many sessions over time*, not one support incident.
3. "Cargo now has `cargo report`, so downstream machine contracts are solved" when stable import and regression artifacts are still a separate value layer.


## Update 2026-03-08 (132) — cargo tool-workflow stack

- Refreshed **P-0494** to be a sharper receiver-facing crate contract: one tool-build receipt, one compile-surface manifest, one parity report, and one fallback plan.
- Added a stack note to keep **P-0494 / P-0490 / P-0489** distinct.
- Added scenario bundles proving separate-target-dir success, missing-sysroot-source diagnosis, and target-mismatch fallback.


## Research ledger — 2026-03-08 frontier pass (134)

### Sources consulted
- rust-analyzer FAQ
- rust-analyzer configuration
- Cargo build-cache docs
- Cargo unstable docs (`build-dir-new-layout`)
- Cargo cache-lock internals docs
- Cargo build-dir layout project goal
- 2025 State of Rust survey results

### Kept together
- the existing cargo tool-workflow stack (P-0494 / P-0490 / P-0489)
- the official locking and target-dir workaround substrate
- the need for a tiny receiver-facing bundle rather than a scheduler or profiler

### Result
- Did **not** add another top-level proposal.
- Added a lock-contention upstream-fit note and a fresh frontier-salience note.
- Upgraded **P-0490** around a smaller 0.1 artifact contract.
- Expanded `fixtures/cargo-lock-contention-witness-kit/` with schema files and three scenario bundles.

### Freshness anchors
- Re-check rust-analyzer FAQ/config wording before freezing stronger claims about lock behavior or target-dir mitigation.
- Re-check Cargo build-dir-layout work before assuming root shapes or locking behavior will stay exactly as they are today.
- Re-check Cargo cache-lock internals if the package/index cache coordination surface changes.

### Common false gap patterns from this pass
1. “Cargo IDE friction needs another generic proposal” when the sharper gap is a **live lock/contention witness**.
2. “A separate target directory means the problem is solved” when the real support artifact still needs to explain the trade-off and mitigation posture.
3. “We need PID-perfect attribution” when a conservative root-level witness and mitigation bundle is often the more durable value.


## Research ledger — 2026-03-08 frontier pass (135)

### Sources consulted
- Cargo build-cache docs
- Cargo config docs
- Cargo external-tools docs
- Cargo build-script docs
- Cargo environment variables docs
- Rust release notes
- Cargo unstable docs (`build-dir-new-layout`)
- Cargo build-dir layout project goal
- User-wide build cache goal
- rust-analyzer `build-dir` support issue

### Kept together
- the existing cargo tool-workflow stack (P-0494 / P-0490 / P-0489)
- stable `build.build-dir` and explicit internal-layout warnings
- existing adapter substrate (`OUT_DIR`, `CARGO_BIN_EXE_<name>`, Cargo JSON, dep-info / final-artifact routing)

### Result
- Did **not** add another top-level proposal.
- Added a build-dir transition upstream-fit note and a fresh frontier-salience note.
- Upgraded **P-0489** around a smaller, more reviewable artifact contract.
- Expanded `fixtures/cargo-build-dir-consumer-transition-kit/` with schema files and four scenario bundles.

### Freshness anchors
- Re-check Cargo release-note wording before claiming the warning or migration ask is unchanged.
- Re-check Cargo config/build-cache docs before assuming `build.build-dir` or target/build splits stay described the same way.
- Re-check rust-analyzer `build-dir` support status before freezing stronger claims about downstream adoption.

### Common false gap patterns from this pass
1. “Cargo made `build.build-dir` stable, so migration is solved” when the sharper gap is still the **consumer inventory / path contract / transition receipt**.
2. “Any use of `target/.../build/...` means the only answer is directory scraping forever” when the sharper adapter can be `OUT_DIR` or build-script JSON.
3. “This consumer needs build-dir migration help” when it actually wants a final artifact and should be routed toward artifact handoff instead.



## Research ledger — 2026-03-08 frontier pass (138)

### Sources consulted
- Rust reference: `#[debugger_visualizer]`
- GDB manual: auto-load safe path
- Rust release notes
- Rust debugging survey 2026

### Kept together
- the existing debug-support stack (P-0486 / P-0493 / P-0491)
- the explicit NatVis target restriction and GDB auto-load safe-path behavior
- the need for a tiny receiver-facing compatibility bundle rather than a new debugger platform

### Result
- Did **not** add another top-level proposal.
- Added a visualizer upstream-fit note and a fresh frontier-salience note.
- Upgraded **P-0491** around a smaller 0.1 artifact contract.
- Expanded `fixtures/debugger-visualizer-compatibility-kit/` with schema files and four scenario bundles.

### Freshness anchors
- Re-check the Rust reference before claiming additional backend coverage under `#[debugger_visualizer]`.
- Re-check GDB auto-load/safe-path wording before freezing stronger classification rules for trust-policy failures.
- Re-check the debugging-survey and follow-on compiler-team planning before assuming official debugger priorities stayed the same.

### Common false gap patterns from this pass
1. “Rust visualizers need another syntax feature” when the sharper gap is a **compatibility / render-golden / drift receipt** above the stable feature.
2. “GDB rendering failed, therefore the asset is broken” when the real cause may be **safe-path trust refusal**.
3. “Visualizer support means debugger parity is solved” when some lanes should remain explicit external/manual routes.


# Research ledger — 2026-03-08 frontier pass (139)

## Sources consulted
- Rust reference: debugger visualizers
- GDB manual: auto-load safe path
- LLDB variable formatting
- Rust debugging survey 2026

## Main notes
- The key distinction for P-0491 is now explicit: embedded asset, activation/trust, and compatibility must remain separate fields.
- LLDB should stay an explicit external/manual lane until stronger official Rust-side embedding evidence exists.
- This makes P-0491 more honest without making it larger.



## Research ledger — 2026-03-08 frontier pass (146)

### Sources consulted
- `system-deps` docs
- `system-deps` `Config` docs
- `system-deps` issue #97
- Cargo external-tools docs
- Cargo config docs (`target.<triple>.<links>`)
- Cargo issue #14948
- Rust Internals discussion on external dependencies and cross-platform development
- 2025 State of Rust survey results

### Kept together
- the existing native-build stack (P-0046 / P-0059 / P-0058)
- current `system-deps` substrate for declarative metadata and build-internal env control
- current Cargo substrate for build-script JSON results and override/handoff flows
- the need to stay honest about cross-platform package-management complexity

### Result
- Did **not** add another top-level proposal.
- Added a native vendoring/mode boundaries note and a fresh frontier-salience note.
- Upgraded **P-0058** around a smaller 0.1 artifact contract.
- Expanded `fixtures/native-deps-kit/` with new schema files and two scenario bundles focused on policy and mode truth.

### Freshness anchors
- Re-check `system-deps` docs before claiming the exact env controls or fallback behavior are unchanged.
- Re-check Cargo config docs before freezing stronger claims about `target.<triple>.<links>` override semantics.
- Re-check Cargo’s build-script-reduction work before claiming upstream is or is not replacing a specific native-build use case.

### Common false gap patterns from this pass
1. “Rust needs a universal cross-platform native package manager” when the sharper gap is a **mode/policy artifact** above existing substrate.
2. “vendored feature exists, therefore the outcome is explained” when the real missing artifact is **who forced vendoring and whether policy allowed it**.
3. “system-deps already has env knobs, so the problem is solved” when the sharper gap is still a **portable lock/report** another person can review.

## Research ledger — 2026-03-08 frontier pass (147)

### Sources consulted
- Cargo source replacement docs
- `cargo vendor` docs
- `cargo fetch` docs
- Cargo dependency override docs
- Cargo changelog
- Cargo issue #14821
- Cargo issue #16141
- Cargo issue #10134

### Kept together
- the existing source-management substrate (`cargo vendor`, source replacement, local registries, path/git deps)
- the exact-same-source assumption and offline-resolution warning from Cargo docs
- the need to separate logical source identity from physical vendor roots
- the need to separate coverage truth from raw “vendored build succeeded once” optimism

### Result
- Did **not** add another top-level proposal.
- Added a source-parity boundaries note and a fresh frontier-salience note.
- Upgraded **P-0496** around a smaller 0.1 artifact contract.
- Expanded `fixtures/cargo-vendor-source-parity-kit/` with new schema files and three scenario bundles focused on alias splits, git-history requirements, and path-dependency spillover.

### Freshness anchors
- Re-check Cargo source replacement docs before claiming the exact same-source assumption or private-registry boundary is unchanged.
- Re-check `cargo vendor` docs before freezing stronger claims about `--respect-source-config`, `--sync`, or other workflow flags.
- Re-check open source-replacement and vendoring issues before pretending multi-source aliases, git-history requirements, or path-dependency coverage have become boring.

### Common false gap patterns from this pass
1. “Cargo already has `cargo vendor`, so the problem is solved” when the sharper gap is a **source identity and coverage artifact**.
2. “Everything points at one `vendor/` directory, therefore the identity story is simple” when the real missing artifact is a **logical-source-aware parity lock**.
3. “The workspace built offline once, therefore the vendored boundary is honest” when the real missing artifact is a **coverage report** that names path/git/manual-review blockers.



## Research ledger — 2026-03-08 frontier pass (148)

### Sources consulted
- Rust compiler performance survey 2025
- rust-analyzer FAQ
- rust-analyzer configuration docs
- Cargo build-cache docs
- Cargo environment/config docs
- Cargo cache-lock internals
- Cargo unstable features (`build-dir-new-layout`)
- Cargo build-dir layout goal

### Kept together
- the existing tool-workflow-adjacent stack (P-0494 / P-0490 / P-0489)
- the now-explicit distinction between target-dir, build-dir, and package/index cache roots
- wrapper/hash-separation facts from Cargo and rust-analyzer docs
- the need for a tiny receiver-facing topology + wait + mitigation bundle rather than another generic Cargo IDE-friction tool

### Result
- Did **not** add another top-level proposal.
- Added a contention-topology boundaries note and a fresh frontier-salience note.
- Upgraded **P-0490** around a smaller 0.1 artifact contract.
- Expanded `fixtures/cargo-lock-contention-witness-kit/` with new schema files and two scenario bundles focused on target/build-root separation and wrapper/hash-split context.

### Freshness anchors
- Re-check rust-analyzer docs before claiming the exact target-dir / wrapper defaults or command shapes are unchanged.
- Re-check Cargo build-cache and environment/config docs before freezing stronger claims about target-dir/build-dir separation or wrapper hash semantics.
- Re-check build-dir-layout and fine-grain-locking progress before pretending shared-root contention has become boring upstream.

### Common false gap patterns from this pass
1. “Cargo is blocked, therefore the target dir is the whole story” when the sharper missing artifact is a **root-sharing topology** that can distinguish target-dir, build-dir, and package-cache lanes.
2. “Wrapper behavior is an implementation detail” when the sharper missing artifact is an optional **wrapper-context receipt** explaining cache-mode split.
3. “Separate target dirs solve lock contention” when the real bundle may still need to report build-dir or package-cache serialization honestly.



## Research ledger — 2026-03-08 frontier pass (149)

### Sources consulted
- Cargo unstable docs (`compile-time-deps`)
- RFC 3477 (`cargo check` policy)
- rust-analyzer configuration docs
- Cargo build-dir layout goal
- rust-analyzer issue #10793
- rust-analyzer issue #5962
- esp-idf-sys issue #113

### Kept together
- the existing tool-workflow-adjacent stack (P-0494 / P-0490 / P-0489)
- the now-explicit distinction between tool workflow truth and comparison-baseline truth
- rust-analyzer override-command, placeholder, wrapper, and target-dir facts
- the need for a tiny receiver-facing comparison-lock + override-receipt bundle rather than another generic editor/Cargo support tool

### Result
- Did **not** add another top-level proposal.
- Added a compile-time-deps boundaries note and a fresh frontier-salience note.
- Upgraded **P-0494** around a smaller 0.1 artifact contract.
- Expanded `fixtures/cargo-compile-time-deps-workflow-kit/` with new schema files and three scenario bundles focused on label-scoped selection drift, relative override-command provenance, and paired toolchain-specific build-script overrides.

### Freshness anchors
- Re-check rust-analyzer docs before claiming the exact override-command, wrapper, or targetDir defaults are unchanged.
- Re-check Cargo unstable docs before pretending `--compile-time-deps` semantics or stated intent have become ordinary stable workflow.
- Re-check real issue reports before claiming custom wrapper and override-command workflows have become boring support cases.

### Common false gap patterns from this pass
1. “The editor used Cargo, therefore the result is basically a build” when the sharper missing artifact is a **comparison-baseline lock**.
2. “A custom override command can emit JSON, therefore provenance does not matter” when the sharper missing artifact is an **override-command receipt**.
3. “Selection drift is just config noise” when the real bundle must freeze **package/label/workspace scope truth** explicitly.



## Research ledger — 2026-03-08 frontier pass (150)

### Sources consulted
- rust-analyzer configuration docs
- Cargo build command docs
- Cargo unstable docs (`compile-time-deps`)
- RFC 3477 (`cargo check` policy)
- rust-analyzer issue #18528
- rust-analyzer issue #17126

### Kept together
- the existing tool-workflow-adjacent stack (P-0494 / P-0490 / P-0489)
- the now-explicit distinction between command provenance and coverage truth
- package scope, target-class coverage, proc-macro availability, and linked-project invocation topology
- the need for a tiny receiver-facing selection-coverage + workspace-invocation bundle rather than another generic editor/Cargo support tool

### Result
- Did **not** add another top-level proposal.
- Added a tool-workflow coverage boundaries note and a fresh frontier-salience note.
- Upgraded **P-0494** around a smaller 0.1 artifact contract.
- Expanded `fixtures/cargo-compile-time-deps-workflow-kit/` with new schema files and three scenario bundles focused on target-class coverage holes, startup scope leakage, and linked-project once-mode narrowing.

### Freshness anchors
- Re-check rust-analyzer docs before claiming the exact `allTargets`, `check.workspace`, or invocation-strategy defaults are unchanged.
- Re-check Cargo build docs before freezing stronger claims about target-class expansions or omitted lanes.
- Re-check real issue reports before pretending proc-macro coverage holes or startup-scope leakage have become boring support cases.

### Common false gap patterns from this pass
1. “The editor used Cargo, therefore target coverage is obvious” when the sharper missing artifact is a **selection-coverage report**.
2. “Package-only diagnostics were configured, therefore that is exactly what happened” when the sharper missing artifact is a **workspace-invocation receipt** that can preserve startup leakage.
3. “Multiple linked projects still imply per-workspace coverage” when the real bundle must freeze **once-mode / opened-project-root narrowing** explicitly.


## Research ledger — 2026-03-08 frontier pass (155)

### Sources consulted
- Cargo features docs
- Cargo registry-index docs (`features2`)
- Rust release notes (Rust 1.60 feature stabilization)
- Cargo issue #10543
- Cargo issue #10788
- Cargo issue #12111
- Cargo issue #12336
- Cargo issue #14015
- Cargo changelog (fix #12130)

### Kept together
- the existing resolver-explanation stack inside **P-0468**
- feature causes versus feature authoring origin
- implicit optional-dependency aliases, `dep:` suppression, `pkg/feat` activation, and `pkg?/feat` weak forwarding
- the need for a tiny receiver-facing feature-origin bundle rather than another generic feature visualizer

### Result
- Did **not** add another top-level proposal.
- Added a feature-origin boundaries note and a fresh frontier-salience note.
- Upgraded **P-0468** around a smaller 0.1 artifact contract.
- Expanded `fixtures/cargo-resolve-why-kit/` with one new schema file and two scenario bundles focused on hidden optional aliases and weak forwarding preconditions.

### Freshness anchors
- Re-check Cargo feature docs before claiming `dep:` / `pkg/feat` / `pkg?/feat` semantics are unchanged.
- Re-check Cargo issue history before pretending metadata or emitted feature-like cfg names now preserve author intent cleanly.
- Re-check Cargo changelog / issue follow-through before claiming namespaced-feature edge cases have become boring support cases.

### Common false gap patterns from this pass
1. “A dependency showed up in the graph, therefore the crate already knows whether it was public or intentionally hidden.”
2. “A feature of an optional dependency was forwarded, therefore that clause must have activated the dependency.”
3. “If a tool saw a feature-like name, then that must be a real public manifest feature.”


## Update 2026-03-08 (156) — resolver dependency identity and rename surface

### Why this pass happened
- Cargo dependency-spec docs distinguish local dependency names from package names for renamed optional dependencies and transitive feature references.
- Registry-index docs distinguish renamed-dependency field mappings across publish API / index / `cargo metadata`.
- Cargo issue history still shows missing support for renaming inherited workspace dependencies and continuing registry/private-registry edge cases for renamed + gated dependencies.

### Kept together
- the existing resolver-explanation stack inside **P-0468**
- feature-origin truth versus dependency-identity truth
- local dependency keys, original package names, metadata `rename` fields, and registry/index `name` / `package` surfaces
- the need for a tiny receiver-facing dependency-identity bundle rather than another generic Cargo manifest explainer

### Result
- Did **not** add another top-level proposal.
- Added a dependency-identity boundaries note and a fresh frontier-salience note.
- Upgraded **P-0468** around a smaller 0.1 artifact contract.
- Expanded `fixtures/cargo-resolve-why-kit/` with one new schema file and two scenario bundles focused on renamed optional dependency feature namespaces and ignored inherited renames.

### Freshness anchors
- Re-check dependency-spec docs before claiming renamed dependency feature syntax has changed.
- Re-check registry-index docs before claiming publish / index / metadata field mappings still align the same way.
- Re-check Cargo issue history before pretending inherited rename support or private-registry renamed-dependency workflows have become boring support cases.

### Common false gap patterns from this pass
1. “The package is named `foo`, therefore the relevant feature token must also be `foo`.”
2. “`cargo metadata` and the registry index use the same fields for renamed dependencies, so another tool can compare them directly without context.”
3. “A workspace member wrote `package = ...` on an inherited dependency, therefore the rename definitely took effect.”


## Update 2026-03-09 (161) — reproducibility evidence layering and fixture-first plan

### Why this pass happened
- **P-0242 Reproducible Build Evidence Kit** remained one of the archive’s broad top-tier bets, but it was still too essay-like relative to newer fixture-first proposals.
- Current substrate is now stronger and easier to reuse: Reproducible Builds has explicit Rust guidance, Cargo/rustc expose more path-hygiene knobs, and OSS Rebuild has made cross-ecosystem rebuild verification and publication more concrete.

### Sources consulted
- Rust 2026 project goals
- Reproducible Builds Rust docs
- Reproducible Builds recording/buildinfo guidance
- SOURCE_DATE_EPOCH specification
- diffoscope official site
- Cargo unstable docs for `trim-paths`
- rustc unstable docs for `remap-cwd-prefix`
- OSS Rebuild README and launch post

### Kept together
- the existing broad top-tier status of **P-0242**
- build recipe, rebuild verdict, diff triage, and portable bundle as one small receiver-facing stack
- the boundary between local review artifacts and external/public attestation publication
- the need for small schema surfaces instead of another long “reproducible builds are important” essay

### Result
- Did **not** add another top-level proposal.
- Added a reproducibility-layering note.
- Upgraded **P-0242** around a smaller 0.1 artifact contract.
- Expanded `fixtures/reprobuildbundle/` with three schema files and two scenario bundles.
- Cleaned one concrete UI-citation leak in `meta/known-existing.md` while touching repo hygiene.

### Freshness anchors
- Re-check Reproducible Builds Rust guidance before claiming the usual failure classes are unchanged.
- Re-check Cargo/rustc path-hygiene docs before claiming `trim-paths` / remap behavior is unchanged.
- Re-check OSS Rebuild coverage and behavior before treating it as stable background context rather than an active external signal.
- Re-check diffoscope release behavior before claiming exact output modes or normalizers are unchanged.

### Common false gap patterns from this pass
1. “Reproducible build evidence is just a `diffoscope` wrapper.”
2. “Any byte mismatch is automatically a suspicious mismatch rather than a semantic-reproduction or normalization case.”
3. “Publisher recipe, third-party rebuild result, and public attestation are all the same artifact.”


## Update 2026-03-09 (164) — assurance-case workbench becomes review-contract-first

### Why this pass happened
- **P-0503 Assurance Case Workbench Kit** remained in the archive’s broad top tier, but it was still more persuasive essay than implementable artifact contract.
- Recent archive work already strengthened the lower layers (**P-0256** evidence bundles and **P-0485** verification campaigns), which made the missing upper-layer review/import contract easier to specify honestly.
- Current external signals are strong: Rust’s 2026 goals explicitly mention certified tooling/specifications/evidence for functional safety; the Rust safety-critical writeup says the path exists but ecosystem support thins at higher criticality; GSN/SACM and existing assurance-case tools show that Rust does not need to invent assurance notation from scratch.

### Sources consulted
- Rust 2026 project goals
- Rust safety-critical blog post
- Rust Foundation Safety-Critical Rust Consortium page
- Safety-Critical Rust Coding Guidelines repository
- OMG SACM 2.3
- GSN Community Standard
- WebGSN
- AssurancePlatform
- CertWare

### Kept together
- the existing broad top-tier status of **P-0503**
- the boundary between evidence producers, bundle/profile substrate, assurance-case assembly, and standards-shaped exports
- the need for small receiver-facing artifacts instead of another decorative editor-first story
- the newer verification/conformance bundle substrate as import lanes rather than as substitutes for assurance arguments

### Result
- Did **not** add another top-level proposal.
- Added an assurance-case boundaries note.
- Upgraded **P-0503** around a smaller 0.1 artifact contract.
- Expanded `fixtures/assurance-case-workbench-kit/` with five schema files and two concrete scenario bundles.
- Updated README, frontier salience, roadmap, and LLM hygiene to preserve stack boundaries.

### Freshness anchors
- Re-check Rust project goals and safety-critical Rust posts before claiming the safety-critical direction is unchanged.
- Re-check the Rust Foundation consortium/guidelines surfaces before treating them as stable long-term inputs.
- Re-check SACM / GSN and existing assurance-case tools before claiming export/interchange surfaces have not shifted.

### Common false gap patterns from this pass
1. “Rust needs an assurance-case editor” when the sharper missing crate is a conservative import/status/diff layer.
2. “Verification campaign bundles or conformance bundles are already the assurance case.”
3. “A GSN/SACM export means the crate must own certification workflow end-to-end.”


## 2026-03-09 — local-first sync coordination layer sharpened

- **P-0076 Local-first Sync Kit** now reads much more clearly as a receiver-facing coordination artifact above existing substrate rather than as “another CRDT”.
- Strong current substrate now exists in **Automerge**, **Loro**, **Yrs**, peer-sync tooling, and **MLS/OpenMLS**. That lowers feasibility risk but also raises the bar: the honest missing value is the boring repo / receipt / bundle layer above them.
- The next-best implementation stance is lane-explicit: **engine lane**, **store lane**, **transport lane**, **membership lane**, and **support-bundle lane** should stay separate in both proposal text and fixtures.
- The proposal is stronger when its first shipped profile is **same-user multi-device** with one default engine/store/transport path, followed by a separate **shared-group** profile with key-epoch and revocation receipts.
- The new fixture pack is the right shape: repo manifest, sync-state report, transport-session receipt, membership ledger, and divergence-triage report.


## 2026-03-09 — accessibility doctor/gating separated from capture/interop lab

- The archive’s accessibility frontier is stronger when it is treated as **two layers**, not one fuzzy proposal: **P-0087** for authoring-side semantic doctor/gating and **P-0202** for observer-side capture/diff/bundles.
- Current Rust substrate is now meaningful enough — especially **AccessKit**, its adapters, and real toolkit adoption — that the sharper missing value is the boring workflow layer above that substrate.
- The new fixture packs are the right receiver-facing shapes: **toolkit profile + doctor report + gate result** for P-0087, and **bundle manifest + tree snapshot + event stream + semantic diff** for P-0202.
- Future passes should keep expected-vs-observed comparison as the seam between these proposals instead of collapsing semantic authoring, platform capture, and compliance claims into one story.


## Update 2026-03-09 (167) — local-first fixtures restored and transport/bootstrap boundaries sharpened

### Why this pass happened
- The archive already treated **P-0076 Local-first Sync Kit** as one of the broad top-tier bets, but the actual archive contents had drifted from that memory surface: `entries/2026-03-09-165.md` described a full `fixtures/localfirst-sync-kit/` pack that was missing from the extracted archive.
- Current substrate is now strong enough that the sharper missing planning detail is no longer "which CRDT exists" but **what transport/bootstrap facts the crate should hand to another person**.

### Sources consulted
- Automerge docs and sync module docs
- Automerge Repo 2.0 blog post
- Loro docs and Loro 1.0 announcement
- iroh docs (`what is iroh`, protocols, Automerge example, relays, tickets)
- RFC 9420 and OpenMLS repository

### Kept together
- the broad top-tier status of **P-0076**
- the separation between engine/store/transport/membership/support lanes
- the need for concrete receiver-facing fixture files, not just better prose
- the boundary between bootstrap convenience tokens and durable identity / authorization truth

### Result
- Did **not** add another top-level proposal.
- Restored and expanded the missing `fixtures/localfirst-sync-kit/` pack.
- Added a transport/bootstrap boundaries note.
- Upgraded **P-0076** with more explicit transport, relay, and bootstrap planning.
- Updated README, roadmap, frontier salience, LLM hygiene, and INDEX so the repo’s memory surface matches the archive contents again.

### Freshness anchors
- Re-check Automerge sync assumptions before claiming the ordered/reliable transport contract is unchanged.
- Re-check iroh docs before claiming public relay or ticket guidance is unchanged.
- Re-check Loro docs/roadmap before claiming the adapter boundary with a future repo/store layer is unchanged.
- Re-check RFC 9420 / OpenMLS before treating current epoch/revocation planning as settled application policy rather than protocol substrate.

### Common false gap patterns from this pass
1. "A P2P ticket or invite link is the durable identity of a replica/member."
2. "Direct path versus relay fallback is transport trivia and does not belong in support bundles."
3. "If the CRDT converges, membership, revocation, and privacy semantics are probably fine too."


## Addendum (2026-03-09): async determinism stack
- **P-0104 Deterministic Simulation Kit** now looks more credible as a cross-backend artifact/adaptor layer: simulation profile, backend capability receipt, fault plan, transcript, and replay/minimization bundle.
- Keep it distinct from **P-0114 Distributed Systems Hardship Harness Kit**, which should own curated hardship/profile suites rather than the general bundle/receipt substrate.
- Keep it distinct from **P-0073 Async Replay Debugger Kit** and **P-0066 Determinism Sim Kit**, which target different truth surfaces.

## 2026-03-09 refresh — text layout profile contracts

### Best next frontier move
- Keep strengthening **P-0197** as a profile-pinned correctness lab rather than as a stealth text engine.

### Kept together
- the distinction between the **case** and the **profile** that interprets it
- the distinction between **backend capability** and **decision origin**
- the distinction between **requested fonts** and the **fonts that actually resolved**

### Result
- Did **not** add another top-level proposal.
- Added a text-layout profile-boundaries note.
- Upgraded **P-0197** with stronger profile/discretion/runtime-font planning.
- Added schema/scenario artifacts so the repo can now express profile-driven text diffs without pretending they are backend mysteries.

### Freshness anchors
- Re-check Unicode annex revisions and Unicode-version drift before freezing default-profile assumptions.
- Re-check Parley and COSMIC Text policy/fallback surfaces before claiming a profile axis is universally supported.
- Re-check WPT CSS Text import value before expanding browser-policy corpus coverage.

## 2026-03-09 refresh — passkey lab capability receipts and comparability truth

### Checked
- WebAuthn Level 3 Candidate Recommendation Snapshot status
- WPT `testdriver` virtual-authenticator and SPC automation hooks
- Selenium virtual-authenticator surface
- geckodriver virtual-authenticator warning state
- `webauthn-rs` and `passkey-rs` capability boundaries
- FIDO certification and conformance program surfaces

### Kept together
- the distinction between protocol semantics and runner-lane capability truth
- the distinction between local automation evidence and certification/conformance evidence
- the need to preserve `manual-review-required` and `not-comparable` as honest outputs

### Result
- Did **not** add another top-level proposal.
- Upgraded **P-0200** into a more implementable scenario/capability/comparability lab.
- Added fixture schemas and scenario packs that make browser-lane truth much more explicit.

### Freshness anchors
- Re-check geckodriver virtual-authenticator status before promoting Firefox into a strong automation baseline.
- Re-check WebAuthn Level 3 and SPC maturity before freezing broader overlay claims.
- Re-check `webauthn-rs` and `passkey-rs` scope before overstating Rust-only lane coverage.


## Update 2026-03-16 (172) — async transition and BorrowSanitizer evidence refresh

- Treat **P-0458 Async Dyn Transition Kit** as a stronger cross-ecosystem transition workbench now that the official 2026 async story explicitly includes `async fn in dyn trait`.
- Treat **P-0465 BorrowSanitizer Workflow & Evidence Kit** as a sharper lane inside the broader sanitizer/debugging frontier, not as a generic sanitizer wrapper.
- Prefer tiny receiver-facing bundles in both cases: recipe/allocation/migration receipts for P-0458, and profile/boundary/finding/reduction receipts for P-0465.
- Keep the distinction sharp between **language-transition artifacts**, **general sanitizer workflows**, **debug-support contracts**, and **higher-level verification imports**.

## Update 2026-03-16 (195) — crate ecosystem pathfinder and decision-pack lane

- Promoted **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** because the latest official Rust vision-doc work names crate discoverability and lack of starter-set guidance as a real supportiveness problem.
- Added a lane-boundary note so future passes keep task-first decision packs separate from crate health, trust scoring, façade crates, and governance-level blessing debates.
- Added a small fixture/schema pack so the archive can now express candidate imports, interop-surface reports, ranked decision packs, and starter-set locks.
- Updated README, INDEX, roadmap, and LLM hygiene so this lane is easier to rediscover and harder to collapse back into vague “crate curation”.

## Update 2026-03-16 (196) — crate capability contract and producer-side interop truth lane

- Promoted **P-0510 Crate Capability Contract & Interop Profile Kit** because the new pathfinder lane still lacks a good producer-side fact surface for runtime coupling, `no_std` posture, docs posture, native obligations, and interop exports.
- Added a lane-boundary note so future passes keep producer-side capability contracts separate from task-first decision packs, item-level availability ledgers, whole-project support contracts, and public-API / semver / MSRV slice tools.
- Added a small fixture/schema pack so the archive can now express capability contracts, observed-capabilities receipts, interop export maps, and profile-conformance reports.
- Updated README, INDEX, frontier map, known-existing, roadmap, and LLM hygiene so this lane is easier to rediscover and harder to collapse back into vague “better crate metadata”.


## Update 2026-03-16 (197) — shared ecosystem interop profile lane

- Promoted **P-0511 Crate Interop Profile Pack Kit** because official Rust guidance now names smoother library interop directly, while the archive still lacked a reusable shared-profile layer above building blocks like `http`, `tower-service`, `futures-core`, and Serde.
- Added a lane-boundary note so future passes keep shared ecosystem profiles separate from producer-side capability contracts, task-first decision packs, trait-evolution / EII migration planners, semver slice tools, and domain-specific conformance kits.
- Added a small fixture/schema pack so the archive can now express interop profile packs, static conformance receipts, behavioral probes, pairwise compatibility reports, and migration hazards.
- Updated README, INDEX, frontier map, known-existing, roadmap, and LLM hygiene so this lane is easier to rediscover and harder to collapse back into vague “better library interop”.


## Update 2026-03-16 (200) — crate upgrade-pack lane

- Promoted **P-0514 Crate Upgrade Pack Kit** because the archive had no good receiver-facing artifact for one crate release-to-release transition, even after adding decision packs, capability contracts, interop profiles, compile-time guidance, and runtime handoff lanes.
- Added a lane-boundary note so future passes keep upgrade packs separate from SemVer/public-API evidence, release automation/changelog tooling, compile-time guidance, and runtime handoff.
- Added a small fixture/schema pack so the archive can now express upgrade packs, hazard reports, fixup receipts, migration recipes, and upgrade diffs.
- Updated README, INDEX, frontier map, known-existing, roadmap, and LLM hygiene so this lane is easier to rediscover and harder to collapse back into vague “better release tooling”.


## Update 2026-03-17 (205) — crate authority-surface lane

- Promoted **P-0519 Crate Authority Surface Pack Kit** because the archive still lacked a receiver-facing artifact for ambient powers, determinism posture, injection points, and sandbox-ready profiles even after adding choice, setup, performance, observability, upgrade, and failure-support lanes.
- Added a lane-boundary note so future passes keep authority-surface contracts separate from capability-oriented APIs, compile-time sandbox policy, static authority scanning, configuration scenarios, and observability surfaces.
- Added a small fixture/schema pack so the archive can now express authority packs, authority-surface receipts, determinism reports, capability-injection reports, sandbox recipes, and authority diffs.
- Updated README, INDEX, frontier map, known-existing, roadmap, and LLM hygiene so this lane is easier to rediscover and harder to collapse back into vague “better security tooling”.


## Update 2026-03-17 (207) — crate resource-surface lane

- Promoted **P-0521 Crate Resource Surface Pack Kit** because the archive still lacked a receiver-facing artifact for queue depth, buffer growth, pool size, cache bounds, worker counts, burst posture, and saturation behavior even after adding choice, setup, performance, observability, authority, and lifecycle-support lanes.
- Added a lane-boundary note so future passes keep resource-surface contracts separate from configuration scenarios, performance envelopes, observability surfaces, authority posture, lifecycle truth, and lower-level queue/cache/limiter/runtime substrate.
- Added a small fixture/schema pack so the archive can now express resource packs, surface receipts, capacity profiles, saturation reports, reclaim obligations, budgets, and resource diffs.
- Updated README, INDEX, frontier map, known-existing, roadmap, and LLM hygiene so this lane is easier to rediscover and harder to collapse back into vague “better tuning docs” or “more backpressure tooling”.


## Update 2026-03-17 (209) — crate test-surface lane

- Promoted **P-0523 Crate Test Surface Pack Kit** because the archive still lacked a receiver-facing artifact for official fixtures, fake backends, paused-time seams, scenario corpora, and supported integration topologies even after adding setup, authority, lifecycle, resource, and persistence-support lanes.
- Added a lane-boundary note so future passes keep test-surface contracts separate from generic testing substrate, runtime/setup support surfaces, and domain-specific conformance workbenches.
- Added a small fixture/schema pack so the archive can now express test-surface packs, fixture catalogs, fake-backend reports, scenario corpora, deterministic seams, snapshot normalization, topology manifests, and test-surface diffs.
- Updated README, INDEX, frontier map, known-existing, roadmap, and LLM hygiene so this lane is easier to rediscover and harder to collapse back into vague “better testing docs”.


## Update 2026-03-17 (218) — crate test-surface planning sharpened into an implementation-ready v0.1 shape

- Did **not** add a new lane; instead, made **P-0523 Crate Test Surface Pack Kit** more executable as a near-term build target.
- Added a product-plan note so future passes keep support levels, environment requirements, and scenario witnesses separate from generic fixture discovery or “better mocks”.
- Added three concrete schemas so the archive can now express support-level policy, test-environment requirements, and scenario-witness receipts.
- Added three scenario families so the archive can now model paused-time drift, official-fake-versus-wiremock boundary confusion, and containerized-peer requirements without flattening them into generic testing advice.
- Updated README, INDEX, known-existing, roadmap, and LLM hygiene so this lane is easier to continue without accidentally inventing a new adjacent crate.


## Update 2026-03-17 (219) — crate observability-surface productization pass

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Tokio tracing topic docs
- `tracing` docs
- `tracing-subscriber` docs + `EnvFilter` docs
- `console-subscriber` docs
- `tracing-opentelemetry` docs
- OpenTelemetry Rust docs
- OpenTelemetry instrumentation-libraries docs
- OpenTelemetry semantic conventions docs
- OpenTelemetry schemas docs
- OpenTelemetry logs docs
- OpenTelemetry handling-sensitive-data docs

### Kept together
- the distinction between **crate-authored observability contracts** and adjacent subscriber/exporter/dashboard/plumbing substrate
- the fact that `tracing`, filters, layers, OpenTelemetry bridges, and tokio-console already exist, which means the missing value is now the contract above them
- the need to keep **signal stability** separate from **signal activation**
- the need to keep **schema/convention posture** separate from raw field names or backend-specific dashboards
- the need to deepen **P-0518** before inventing another neighboring telemetry lane too early

### Result
- Added `meta/crate-observability-surface-product-plan-2026-03-17.md` as the implementation-ready `0.1` sketch for **P-0518**.
- Added `signal-stability.policy`, `activation-recipe.receipt`, and `schema-convention.profile` schemas plus three new observability-surface fixture families for filter-gated visibility, runtime-specific console recipes, and semantic-convention/schema drift.
- Updated **P-0518** with tighter prior-art boundaries, richer artifacts, and a direct link to the new product plan.
- Updated repo-memory files so future passes do not mistake filters, subscribers, exporter bridges, or semconv naming rules for the same missing crate.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness priorities later on.
- Re-check Tokio tracing / console docs before assuming the same runtime-introspection substrate later on.
- Re-check `tracing-subscriber`, `tracing-opentelemetry`, and OpenTelemetry semantic-convention/schema docs before restating activation or naming behavior later on.

### Common false gap patterns from this pass
1. “Rust still needs another tracing layer” when the sharper gap is a **crate-authored signal / activation / sensitivity contract**.
2. “The crate emits telemetry, so the support story is clear” when visibility may still depend on filters, features, runtime support, or exporter bridges.
3. “Semantic conventions solve it” when semconv alignment still does not publish one crate’s stability classes, activation recipes, or sensitivity boundaries.
4. “A dashboard or collector config is the product” when the sharper value is still a small local pack/diff/bundle layer above today’s substrate.


## Update 2026-03-17 (220) — cfg availability-ledger productization pass

### Sources consulted
- rustdoc `doc_cfg` stabilization goal
- RFC 3631 rustdoc cfg handling
- rustdoc unstable-features docs for `#[doc(cfg)]` / `#[doc(auto_cfg)]`
- rustdoc advanced-features docs for `#[cfg(doc)]`
- docs.rs builds docs
- docs.rs rustdoc JSON docs
- Cargo features reference
- Cargo build-scripts reference
- Cargo changelog (`--check-cfg` stabilization)

### Kept together
- the distinction between **item-level conditional API truth** and adjacent whole-project support / docs.rs parity / capability-contract lanes
- the fact that rustdoc, docs.rs, rustdoc JSON, and Cargo feature plumbing already exist, which means the missing value is the review artifact above them
- the need to keep **availability class** separate from **origin**
- the need to keep **origin** separate from **matrix fidelity**
- the need to deepen **P-0451** before inventing another neighboring docs/config crate too early

### Result
- Added `meta/cfg-availability-ledger-product-plan-2026-03-17.md` as the implementation-ready `0.1` sketch for **P-0451**.
- Added `availability-class.policy`, `availability-origin.receipt`, and `matrix-fidelity.report` schemas plus three new cfg-availability fixture families for docs-only visibility, docs.rs-only slices, and semver-sensitive feature drift.
- Updated **P-0451** with tighter artifacts, better `0.1` command surface, and a direct link to the new product plan.
- Updated repo-memory files so future passes do not mistake docs markers, hosted docs assumptions, or raw rustdoc JSON imports for the same missing crate.

### Freshness anchors
- Re-check the rustdoc `doc_cfg` / RFC 3631 status before restating stabilization posture later on.
- Re-check docs.rs build and rustdoc-JSON pages before restating hosted-vs-local or format-version behavior later on.
- Re-check Cargo features / build-script / `--check-cfg` docs before repeating feature or custom-cfg behavior later on.

### Common false gap patterns from this pass
1. “Rust still needs better conditional docs” when the sharper gap is a **maintainer-facing matrix / origin / fidelity artifact**.
2. “If the docs show it, it exists” when visibility may still come from `cfg(doc)`, `doc(cfg)`, `auto_cfg`, or docs.rs-only assumptions.
3. “A public-API diff already catches this” when the important drift is conditional rather than universal.
4. “docs.rs parity solves it” when whole-build parity still does not answer per-item availability truth.


## Update 2026-03-17 (222) — crate resource-surface productization pass

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Tokio `mpsc` docs
- Tokio bounded/unbounded channel docs
- Tokio runtime builder docs
- Tokio runtime metrics docs
- Tokio `spawn_blocking` docs
- Reqwest client + client-builder docs
- Tower limit docs
- Moka cache builder + cache docs
- Governor quota docs

### Kept together
- the distinction between **crate-authored resource contracts** and adjacent queue/cache/limiter/runtime substrate
- the fact that observability signals help, but do **not** by themselves publish one crate’s boundedness or saturation promises
- the need to keep **boundedness meaning** separate from **raw numeric defaults**
- the need to keep **pressure-signal guidance** separate from generic “emit metrics” advice
- the need to deepen **P-0521** before inventing another neighboring capacity/perf/observability lane too early

### Result
- Added `meta/crate-resource-surface-product-plan-2026-03-17.md` as the implementation-ready `0.1` sketch for **P-0521**.
- Added `boundedness-class.policy`, `pressure-signal.profile`, and `saturation-evidence.receipt` schemas plus three new resource-surface fixture families for unbounded queue growth, hidden blocking queues after thread-cap saturation, and externally-owned backlog boundaries.
- Updated **P-0521** with tighter artifacts, a sharper `0.1` command surface, and a direct link to the new product plan.
- Updated repo-memory files so future passes do not mistake runtime metrics, concurrency limiters, or pool/capacity knobs for the same missing crate.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness/resource-usage priorities later on.
- Re-check Tokio channel / runtime / `spawn_blocking` docs before restating queueing, worker-cap, or shutdown-adjacent resource behavior later on.
- Re-check reqwest / tower / Moka / governor docs before repeating default-bound or admission-control claims later on.

### Common false gap patterns from this pass
1. “Rust still needs another backpressure crate” when the sharper gap is a **crate-authored boundedness / saturation / pressure-signal contract**.
2. “The crate emits metrics, so the resource story is clear” when metrics still do not publish what is bounded or what happens at saturation.
3. “A concurrency limit solves backlog too” when upstream waiting or buffering may still sit outside the documented bound.
4. “A default numeric knob is the whole story” when the important truth is the class of bound and the observed behavior at the edge.

## Update 2026-03-19 (259) — crate resource-surface contract refresh

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Tokio `Semaphore` + `SemaphorePermit` docs
- Tower buffer + `ServiceBuilder` docs
- SQLx `Pool` + `PoolOptions` docs
- Deadpool managed `Pool` docs

### Kept together
- the distinction between **resource support contracts** and raw queue/pool/cache substrate
- the need to keep **admission order** separate from **numeric limits**
- the need to keep **backlog ownership** separate from **in-flight concurrency**
- the need to keep **capacity shrink** separate from constructor-time capacity
- the need to keep **acquire fate** separate from generic “there is a max size” prose

### Result
- Added `meta/crate-resource-surface-product-plan-2026-03-19.md` as the refreshed implementation-ready sketch for **P-0521**.
- Added `admission-path.report`, `backlog-ownership.receipt`, `capacity-shrink.report`, and `acquire-fate.report` schemas plus four new scenario families for Tower layer order, semaphore permit loss, and pool wait/close semantics.
- Updated **P-0521** with sharper review objects, tighter artifact vocabulary, and a direct link to the new product plan.
- Updated repo-memory files so future passes do not confuse “a visible limit exists” with “the resource support contract is already clear.”

### Freshness anchors
- Re-check Tokio semaphore / queue / runtime docs before restating permit-loss, queueing, or blocking-pool behavior later on.
- Re-check Tower docs before repeating any claim about `buffer` + `concurrency_limit` ordering.
- Re-check SQLx and Deadpool docs before repeating pool wait, fairness, timeout, or close-wakes-waiters claims later on.

### Common false gap patterns from this pass
1. “A pool size explains everything” when acquire timeout, fairness, and close semantics are still missing.
2. “A concurrency limit owns backlog too” when the waiting room may still live upstream.
3. “Capacity is whatever the constructor said” when permits or pool state can shrink effective capacity later.
4. “The docs mention a queue” when the real missing value is a receiver-facing contract about admission, backlog, and caller fate.


## Update 2026-03-17 (223) — crate performance-envelope productization pass

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Cargo `cargo bench` docs
- Cargo profiles reference
- Cargo 1.84 development-cycle post
- Criterion docs
- Iai-Callgrind docs
- Divan docs
- codspeed-criterion-compat docs
- codspeed-divan-compat docs

### Kept together
- the distinction between **crate-authored performance contracts** and adjacent benchmark / profiling / hosted-service substrate
- the fact that one scenario can have multiple measurements while still needing one **authoritative metric**
- the need to keep **environment fidelity** separate from **budget numbers**
- the need to keep **noise/trust class** separate from raw benchmark output
- the need to deepen **P-0517** before inventing another neighboring perf/observability/runtime lane too early

### Result
- Added `meta/crate-performance-envelope-product-plan-2026-03-17.md` as the implementation-ready `0.1` sketch for **P-0517**.
- Added `metric-authority.policy`, `environment-fidelity.receipt`, and `noise-class.report` schemas plus three new performance-envelope fixture families for bench-versus-release drift, CI-stable instruction-count authority, and compatibility-layer semantic gaps.
- Updated **P-0517** with tighter artifacts, a sharper `0.1` command surface, and a direct link to the new product plan.
- Updated repo-memory files so future passes do not mistake benchmark runners, profiler imports, or hosted CI outputs for the same missing crate.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness/perf-usage priorities later on.
- Re-check Cargo bench/profile docs before restating profile defaults or harness behavior later on.
- Re-check Criterion / Iai / Divan / CodSpeed docs before repeating tool-specific support or compatibility-layer limits later on.

### Common false gap patterns from this pass
1. “Rust still needs another benchmark framework” when the sharper gap is a **crate-authored workload / metric / fidelity / confidence contract**.
2. “A CI perf service already solves it” when hosted results still do not say which metric is authoritative or which local semantics were dropped.
3. “One benchmark number is enough” when the real missing truth is the named scenario, its assumptions, and its trust class.
4. “Profiling support and performance support are the same lane” when downstream adopters still need a smaller review artifact above the profiler substrate.


## Update 2026-03-17 (225) — crate authority-surface productization pass

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Safety-critical vision-doc post
- Rust project goal on sandboxed build scripts
- Cargo environment-variable docs
- Cargo build-scripts docs
- `ambient-authority` docs
- `cap-std` docs
- `cap-std::fs::Dir` docs
- `rustix` docs
- `wasi-cap-std-sync` docs
- `getrandom` docs

### Kept together
- the distinction between **crate-authored authority contracts** and adjacent capability / sandbox / lint substrate
- the fact that compile-time sandbox policy and runtime/library authority posture are related but **not the same lane**
- the need to keep **authority budget meaning** separate from raw import sightings
- the need to keep **injection-boundary truth** separate from “a test seam exists somewhere”
- the need to keep **profile witnesses** separate from aspirational README claims
- the need to deepen **P-0519** before inventing another neighboring security/sandbox crate too early

### Result
- Added `meta/crate-authority-surface-product-plan-2026-03-17.md` as the implementation-ready `0.1` sketch for **P-0519**.
- Added `authority-budget.policy`, `injection-boundary.receipt`, and `profile-witness.report` schemas plus three new authority-surface fixture families for env/home fallback drift, clock-leak nondeterminism, and capability-profile absolute-path escapes.
- Updated **P-0519** with tighter artifact and command language plus a direct link to the new product plan.
- Updated repo-memory files so future passes do not mistake capability libraries, static scans, or full sandbox hosts for the same missing crate.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness/learning-surface priorities later on.
- Re-check the safety-critical post before restating how teams treat third-party crates in production-critical settings.
- Re-check the sandboxed-build-script goal before restating Cargo’s authority/determinism framing later on.
- Re-check `ambient-authority`, `cap-std`, `rustix`, `wasi-cap-std-sync`, and `getrandom` docs before repeating substrate details or injection/back-end claims later on.

### Common false gap patterns from this pass
1. “Rust needs another sandbox crate” when the sharper gap is a **crate-authored authority budget / injection / witness contract**.
2. “Capability-based APIs solve it already” when adopters still need to know which public paths remain ambient-only.
3. “A static scan found env/network/fs calls, so the authority story is done” when profile budgets and witness evidence are still missing.
4. “A seeded RNG seam makes the crate deterministic” when time, home-dir, env, or other host dependencies still leak nondeterminism.


## Update 2026-03-17 (228) — crate upgrade-pack productization pass

- Chose to deepen **P-0514 Crate Upgrade Pack Kit** instead of opening a neighboring examples/fix-orchestration lane.
- Decided that the first implementation should elevate **hazard classes**, **fixup capability receipts**, and **checked-lane fidelity** into first-class artifacts.
- Reaffirmed that upgrade-pack support is distinct from SemVer/public-API evidence, release automation, generic lint-fix orchestration, and runtime/compile-time support surfaces.


## Update 2026-03-17 (229) — crate capability-contract planning sharpened into an implementation-ready v0.1 shape

- Did **not** add a new lane; instead, made **P-0510 Crate Capability Contract & Interop Profile Kit** more executable as a near-term build target.
- Added a product-plan note so future passes keep claim classes, support obligations, and profile fidelity separate from generic “better crate metadata”.
- Added three concrete schemas so the archive can now express claim-class meaning, observed adoption obligations, and profile-fidelity posture.
- Added three scenario families so the archive can now model public-runtime neutrality, docs.rs-overlay drift, and hidden build/native/proc-macro obligations without flattening them into generic crate-quality advice.
- Updated README, INDEX, known-existing, roadmap, and LLM hygiene so this lane is easier to continue without accidentally inventing a new adjacent crate.


## Update 2026-03-17 (230) — crate interop-profile planning sharpened into an implementation-ready v0.1 shape

- Did **not** add a new lane; instead, made **P-0511 Crate Interop Profile Pack Kit** more executable as a near-term build target.
- Added a product-plan note so future passes keep profile classes, boundary obligations, and pair fidelity separate from generic “compatibility tooling”.
- Added three concrete schemas so the archive can now express shared-profile meaning, required boundary obligations, and how complete a provider/consumer verdict really is.
- Added three scenario families so the archive can now model public-runtime leakage, `tower-service`/`http` seam-versus-body-shape drift, and format-specific helper lock-in without flattening them into generic semver or metadata advice.
- Updated README, INDEX, known-existing, roadmap, and LLM hygiene so this lane is easier to continue without accidentally inventing a new adjacent crate.


## Update 2026-03-17 (235) — cfg availability-ledger deepening pass

- Chose to deepen **P-0451 Cfg Availability Ledger Kit** instead of opening another neighboring docs/support lane.
- Decided that the next implementation pass should elevate **slice witnesses**, **gate normalization**, and **re-export lineage** into first-class artifacts.
- Reaffirmed that rustdoc markers, docs.rs overlays, hosted imports, and public re-export paths are useful substrate, but they do not by themselves produce a trustworthy item-level availability contract.
- Added a lane-boundary note so future passes keep item-level availability separate from whole-project support, docs.rs parity, and generic public-API diff tooling.


## Update 2026-03-17 (237) — toolchain/target support deepening pass

- Chose to deepen **P-0484 Toolchain & Target Support Contract Kit** instead of opening another neighboring support or CI lane.
- Decided that the next implementation pass should elevate **override lineage**, **component availability**, and **exercise scope** into first-class artifacts.
- Reaffirmed that rustup selectors, requested toolchains, effective toolchains, component availability, and exercised scopes are related facts but not interchangeable.
- Added scenario families for environment override shadowing, nightly fallback due to missing components, and host-helper scope splitting under explicit `--target` builds.


## Update 2026-03-18 (238) — crate ecosystem pathfinder deepening pass

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Rust debugging survey 2026
- crates.io development update (January 2026)
- crates.io malicious-crate policy update (February 2026)
- docs.rs default-target change announcement
- docs.rs metadata docs
- docs.rs builds docs
- Cargo build-analysis goal
- Build-dir-layout v2 call for testing
- rustup 1.29.0 announcement

### Kept together
- the distinction between **task-first crate choice** and adjacent health/trust/docs/toolchain lanes
- the fact that **evidence origin** matters because registry metadata, official policy, crate-authored docs, and local observation are not equally authoritative
- the fact that **fresh signals** are worth importing but not always worth freezing into a starter set immediately
- the fact that **starter-set scope** must stay explicit because teaching, production, and org-policy defaults can diverge
- the need to deepen **P-0509** before inventing another neighboring curation or ranking lane too early

### Result
- Added `meta/frontier-salience-2026-03-18-58.md` and `meta/epic-crate-portfolio-2026-03-18.md`.
- Added `evidence-origin.report`, `freshness-window.policy`, and `starter-set-scope.report` schemas plus three new pathfinder fixture families for pubtime cooldowns, docs.rs target-visibility drift, and trust-signal-vs-task-fit boundaries.
- Updated **P-0509** and its product plan so future passes keep provenance, freshness, and scope explicit instead of drifting back into fake popularity or fake “best crate” language.
- Updated repo-memory files so future passes can rank worthy work without forgetting the current cross-archive priority structure.

### Freshness anchors
- Re-check the survey / debugging-survey / vision-doc language before repeating broad ecosystem pain claims later on.
- Re-check crates.io development updates before restating Security-tab, Trusted-Publishing, `pubtime`, or filtered-download details later on.
- Re-check docs.rs metadata/build docs and target-default changes before restating documentation-surface behavior later on.
- Re-check Cargo/rustup update posts before restating build-dir or toolchain-surface churn later on.

### Common false gap patterns from this pass
1. “A better popularity rank would solve crate choice” when the sharper gap is a **task-first decision artifact with provenance and scope**.
2. “Security tab or Trusted Publishing means this is the right crate” when the sharper gap still includes role coverage and interop fit.
3. “Docs.rs shows it, so support changed” when the sharper gap is still whether visible support drift altered the intended task scope.
4. “A fresh publish should immediately enter the starter set” when the sharper gap is a **reviewable freshness window** rather than novelty worship.


## 2026-03-18 — Python wheel/free-threading shipkit deepening

### Sources checked
- PyO3 building/distribution docs
- PyO3 multiple-version support docs
- PyO3 free-threading guide
- Python free-threaded extension HOWTO
- What’s new in Python 3.14
- maturin changelog
- maturin `abi3.abi3t` issue
- cibuildwheel options docs
- PEP 803 and PEP 825

### Working conclusions
- PyO3 + maturin + cibuildwheel already make Python extension shipping real substrate.
- The sharper gap has moved upward into a **compatibility contract**: what ABI class is claimed, what thread-support is declared, and what future packaging surfaces are still out-of-scope.
- The archive should keep separate “build succeeded”, “loads on free-threaded Python”, “declares free-threaded safety”, and “future `abi3t` support planned”.
- Accepted `abi3t` / wheel-variant work makes it more important, not less, to keep variant-horizon honesty explicit.

### Common false gap patterns from this pass
1. “A better binding generator would solve this” when the sharper gap is a **release-contract artifact above existing generators**.
2. “Free-threaded Python is supported now, so the old Stable ABI story just extends automatically” when Python’s own docs still require separate wheels today.
3. “The PEP was accepted, therefore current release tooling already supports it” when the actual project tooling still has open follow-on work.
4. “A wheel loads, so the extension supports GIL-disabled execution” when PyO3 still distinguishes explicit thread-support declarations and opt-outs.


## 2026-03-18 — Wasm component shipkit deepening

### Sources checked
- Rust component-model language support docs
- Rust project goals 2026 flagships
- component-model composition docs
- Wasmtime running-components docs
- Bytecode Alliance article on `wasmtime run --invoke`
- rustc `wasm32-wasip3` platform-support docs
- Wasmtime February 2026 component-model-async security advisory
- current Wasmtime release notes
- cargo-component repo and release page

### Working conclusions
- Native Rust tooling now matters as much as `cargo-component`, because official docs are already shifting toward direct target builds.
- The sharper gap has moved upward into a **component contract bundle**: how the component was produced, what exact world/package/version contract it carries, whether imports are actually closed, and how another person can exercise it.
- The archive should keep separate “component exists”, “world lock is explicit”, “composition is closed”, and “generic runnable surface is known”.
- `wasm32-wasip3` and recent Wasmtime async/runtime movement make it more important, not less, to keep tooling lineage and exercise posture explicit.

### Common false gap patterns from this pass
1. “A better builder wrapper would solve this” when the sharper gap is a **contract artifact above shifting builder paths**.
2. “The component has a world, therefore composition should obviously work” when version inference and package IDs can still drift.
3. “It built natively, so it is closed and runnable” when host-supplied imports or transitive open edges still remain.
4. “A Wasm runtime change is unrelated to shipping-contract design” when exercise posture and async/runtime assumptions still affect what a bundle truthfully promises.


## 2026-03-18 — Node-API package contract deepening

### Sources checked
- Node-API reference
- Node ABI stability guide
- Node packages docs (`node-addons`, `default`, `--no-addons`)
- Node addons docs (Worker/context-aware support)
- Node CLI / errors docs for non-context-aware loading
- napi-rs homepage, getting-started docs, build docs, and v3 announcement
- npm trusted publishing docs
- npm publish docs for provenance generation context

### Working conclusions
- Node-API + `napi-rs` already make Rust addon authoring and cross compilation real substrate.
- The sharper gap has moved upward into a **package contract**: what tuples are actually prebuilt, what loader route downstream users actually take, and what publish identity the npm release really has.
- The archive should keep separate “published successfully”, “native prebuild shipped for this tuple”, “there is a universal fallback route”, and “runtime claims beyond Node are justified”.
- npm trusted publishing and provenance make publish identity more important, not less, but they still do not settle support claims by themselves.

### Common false gap patterns from this pass
1. “A better binding generator would solve this” when the sharper gap is a **release-contract artifact above existing generators**.
2. “A native addon package published to npm is therefore fully prebuilt” when missing libc/arch tuples may still fall back to local builds.
3. “A `default` route exists, so support is universal” when `default` may only represent a narrower WASM or degraded path.
4. “Trusted publishing with provenance means the runtime claims are strong too” when release identity and compatibility evidence are adjacent but separate truths.

## 2026-03-18 — Apple XCFramework shipkit deepening

### Sources checked
- UniFFI Swift/Xcode integration docs
- UniFFI docs.rs page
- `cargo swift` README / current crate surface
- `xcframework` crate docs
- SwiftPM package-description docs for binary targets
- Apple binary-framework distribution docs for Swift packages
- Apple origin-verification docs for XCFrameworks
- Apple privacy-manifest docs
- Apple third-party SDK requirements page

### Working conclusions
- UniFFI + `cargo swift` + `xcframework` already make Rust-backed Apple SDK shipping real substrate.
- The sharper gap has moved upward into an **Apple release contract**: what slices are actually present, whether the SwiftPM wrapper really matches the bundle, and what trust posture the release really has.
- The archive should keep separate “an XCFramework exists”, “the wrapper/checksum aligns”, “the bundle is signed”, and “privacy-manifest posture is complete enough for downstream review”.
- Apple’s current binary-target, signature/origin, and privacy-policy surfaces make this more important, not less, to keep explicit.

### Common false gap patterns from this pass
1. “A better binding generator would solve this” when the sharper gap is a **release-contract artifact above existing generators**.
2. “The wrapper imports, so the Apple support promise is clear” when the real gap may still be slice coverage or stale wrapper/checksum identity.
3. “The XCFramework is signed, so trust posture is settled” when privacy-manifest and downstream policy obligations may still remain.
4. “A SwiftPM checksum exists, so the wrapper and binary identity obviously still match” when module-name or deployment-claim drift can still survive a rebuild.


## 2026-03-18 — NuGet native interop shipkit deepening

### Sources checked
- NuGet native files in .NET packages
- RID catalog
- unmanaged library loading algorithm
- plugin-host tutorial with `AssemblyDependencyResolver`
- Native AOT interop docs
- .NET 8 RID-asset compatibility note
- .NET 10 single-file native-library search breaking change
- native interop best practices (`LibraryImport`)
- csbindgen repo

### Working conclusions
- Rust already has real Rust→C# binding substrate, so the sharper gap is not another generator.
- The missing value has moved upward into a **NuGet producer-side shipping contract**: what assets actually shipped for which RIDs, how unmanaged loading is expected to work, and what deployment modes are really supported.
- RID inventory, loader route, and deployment posture should stay separate because one local restore or one successful app launch does not imply broad support.
- .NET 8+ and .NET 10 behavior changes make “we used to rely on that probing quirk” a real risk surface rather than an implementation detail.

### Common false gap patterns from this pass
1. “A better binding generator would solve this” when the sharper gap is a **release-contract artifact above existing generators**.
2. “The package restored, so the RID matrix must be fine” when the shipped native assets may still lag the claimed support surface.
3. “The DLL loaded in one app, so loader behavior is boring” when plugin hosts and custom resolvers still change the route materially.
4. “Single-file or Native AOT support is just another publish flag” when deployment-mode rules and native-library search behavior still move underneath the package.

## 2026-03-18 — Hex shipkit deepening

- Promoted **P-0502 Hex Native NIF ShipKit** from a plausible package-support idea into a much tighter shipping-contract proposal.
- The main sharpeners were current first-party and live-project facts: the checksum file is mandatory for `rustler_precompiled` packages, NIF versions are more stable than OTP versions, and live packages still break on checksum inclusion, artifact naming, target coverage, and local-build fallback.
- Added a product-plan note and fixture/schema families for **checksum residency**, **NIF-version window**, and **fallback trigger**.
- Hygiene improvement: corrected a local prioritization drift where one queue had been referring to a phantom “Composer Native Extension ShipKit” instead of the actual Hex lane.

## Added 2026-03-18 (246)

### JAR/JNI shipkit / current ecosystem evidence
- Oracle `System.loadLibrary` docs now explicitly state the method is restricted and requires enabled native access: https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html
- JNI intro explicitly says native library loading and `native` declarations without native access lead to warnings and/or exceptions: https://docs.oracle.com/en/java/javase/25/docs/specs/jni/intro.html
- Current migration guidance now spells out `--enable-native-access` for named modules and `ALL-UNNAMED` for class-path code: https://docs.oracle.com/en/java/javase/26/migrate/migrating-from-jdk-8-later-jdk-releases.html
- Maven deploy-plugin docs keep attached classifiers fully ordinary: https://maven.apache.org/plugins/maven-deploy-plugin/examples/deploying-with-classifiers.html
- Sonatype Central documents Maven-plugin publication through the Publisher Portal: https://central.sonatype.org/publish/publish-portal-maven/
- `os-maven-plugin` / `osdetector` still provide a real de-facto classifier dialect for native JVM artifacts: https://github.com/trustin/os-maven-plugin
- `jni` docs still show that raw JNI authoring substrate already exists: https://docs.rs/jni

### Resulting archive judgment
- Promoted **P-0500 JAR/JNI Native ShipKit** from a plausible foreign-package lane into a much tighter shipping-contract proposal.
- Concluded that the sharper missing layer is not another binding generator or publisher wrapper, but a **reviewable classifier/loader/native-access contract**.
- Chose to elevate **classifier dialect**, **native-access posture**, and **loader residency** into first-class review objects.
- Reaffirmed that attached artifacts, classifier naming, runtime flags, and loader paths should not collapse into one fake “Java support” verdict.


## Added 2026-03-18 (247)

### R / CRAN compiled-package shipping substrate
- `rextendr` package-development article: https://extendr.rs/rextendr/articles/package.html
- `extendr_module!` docs: https://extendr.github.io/extendr/extendr_api/macro.extendr_module.html
- R Extensions manual (`useDynLib`, registration): https://cran.r-project.org/doc/manuals/r-devel/R-exts.html
- R Internals (`useDynLib`, `.onLoad`, `library.dynam`, installed `libs/`): https://cran.r-project.org/doc/manuals/r-devel/R-ints.html
- `R CMD INSTALL` / staged install / sub-architectures: https://cran.r-project.org/doc/manuals/r-patched/packages/utils/refman/utils.html
- R Installation and Administration (binary/source installs, compiled-code toolchains): https://cran.r-project.org/doc/manuals/r-devel/R-admin.html
- Rust-backed packages on CRAN list: https://github.com/nanxstats/r-rust-pkgs

**Conclusion:** the missing value is no longer another authoring layer. The sharper gap is a reviewable release contract for registration posture, DLL load contracts, and install posture.


## Added 2026-03-18 (248)

### RubyGems native-extension shipping substrate
- Bundler `bundle gem` docs (`--ext=rust`): https://bundler.io/man/bundle-gem.1.html
- RubyGems specification reference (`extensions`, `platform`, `require_paths`): https://guides.rubygems.org/specification-reference/
- RubyGems guide: gems with extensions: https://guides.rubygems.org/gems-with-extensions/
- Bundler Gemfile docs (`platforms`, Ruby engines): https://bundler.io/man/gemfile.5.html
- Bundler cache docs (`--all-platforms`, remote fetch behavior): https://bundler.io/man/bundle-cache.1.html
- RubyGems trusted publishing guide: https://guides.rubygems.org/trusted-publishing/
- RubyGems command reference (`gem rebuild`): https://guides.rubygems.org/command-reference/
- official `release-gem` action: https://github.com/rubygems/release-gem
- `rb-sys`: https://github.com/oxidize-rb/rb-sys
- `magnus`: https://docs.rs/magnus
- oxidize.rb deployment guide: https://oxidize-rb.org/docs/deployment/

### Resulting archive judgment
- Promoted **P-0501 RubyGems Native Extension ShipKit** from a plausible foreign-package idea into a much tighter shipping-contract proposal.
- Concluded that the sharper missing layer is not another binding generator, template, or publish bot, but a **reviewable Ruby release contract**.
- Chose to elevate **platform coverage**, **resolver route**, and **extension residency** into first-class review objects.
- Reaffirmed that gemspec platform, Bundler engine/platform gating, binary/source fallback, copied extension files, and publish/rebuild posture should not collapse into one fake “Ruby support” verdict.


## Added 2026-03-19 (251) — embedded filesystem / LittleFS adoption
- **P-0527 LittleFS Native Adoption Kit** — sharpened because the ecosystem now has both a mainstream FFI-backed littlefs path and a fresh pure-Rust port, but still lacks one boring adoption layer for storage-adapter receipts, compatibility witnesses, power-cut evidence, and image/support bundles.


## Update 2026-03-19 (258) — crate lifecycle-surface deepening

- Revisited **P-0520 Crate Lifecycle Surface Pack Kit** against current Rust/Tokio substrate instead of opening another adjacent lane.
- Confirmed that the sharper remaining gap is a receiver-facing lifecycle contract above existing shutdown/task/cancellation helpers, not another framework.
- Refreshed evidence with current Tokio docs for `JoinHandle`, `JoinSet`, `TaskTracker`, `CancellationToken`, `select!`, and `AsyncWriteExt`, plus current `async_shutdown`, `tokio-graceful-shutdown`, `task_scope`, and `moro` docs.
- Promoted activation boundaries, stop verbs, blocking-work caveats, teardown evidence, and drain recipes into the working review objects for `0.1`.
- Added concrete scenario artifacts for detach-on-drop, lazy activation, protocol shutdown, partial-progress writes, subscription stop semantics, blocking-work abort caveats, and JoinSet shutdown-vs-detach behavior.


## 2026-03-19 (persistence deepening refresh)

Reviewed / re-checked:
- Rust blog vision-doc post on supportive interfaces from crates
- 2025 State of Rust survey results
- `std::fs::File` docs (`sync_all`, `sync_data`, close-error-on-drop warning)
- `std::fs::rename` docs (same-mount limit, platform-specific replacement behavior)
- `tempfile::NamedTempFile::persist` docs (atomic replace without content/dir synchronization)
- `atomic-write-file` docs (no-intermediate-state overwrite path, symlink replacement, metadata-retention limits)
- Tokio `fs` docs (`spawn_blocking` for ordinary file IO)
- redb database docs (automatic recovery plus integrity-check / repair boundary)
- Postcard, `serde-reflection`, and `revision` docs (different compatibility-authority classes)

Main conclusions:
- The sharper missing value for **P-0522** is no longer generic durability language.
- The lane now needs explicit review objects for **publication target** and **identity retention** in addition to durability, compatibility authority, and recovery witness.
- Async file ergonomics must stay separate from persistence guarantees.
- Atomic replacement must stay separate from metadata retention and from durable publication.

Archive changes driven by this review:
- Added a fresh 2026-03-19 product-plan refresh for **P-0522**.
- Added a lane-boundaries note so persistence support stays separate from serializers, engines, async wrappers, upgrade packs, and LittleFS adoption.
- Added fixture-root guidance plus new scenarios for symlink replacement, metadata-retention drift, and Tokio async-surface overclaiming.
- Updated the proposal, roadmap, prioritization, epic portfolio, and repo hygiene notes so future passes keep these boundaries explicit.


## Update 2026-03-19 (261) — crate test-surface deepening around witness lineage and topology honesty

- Revisited **P-0523 Crate Test Surface Pack Kit** instead of opening another adjacent testing/tooling lane.
- Refreshed evidence with current Tokio paused-time/runtime docs, current `cargo-nextest` record/replay and portable recordings docs, `assert_cmd` Cargo-binary limitations, `wiremock` per-test isolation guidance, Testcontainers runtime requirements, current `trybuild` compile-fail docs, and current Insta redaction/sorted-redaction docs.
- Concluded that the sharper remaining gap is not test substrate but a receiver-facing contract for **support levels**, **topology honesty**, **witness lineage**, and **normalization boundaries**.
- Added a fresh 2026-03-19 product-plan note plus a fixture root README, a new `witness-lineage` schema, and concrete scenario artifacts for portable recordings, compile-fail witness lineage, `assert_cmd` integration-test context, sorted snapshot normalization, and Tokio paused-time requirements.
- Updated the proposal, prioritization, roadmap, epic portfolio, and repo hygiene notes so future passes keep imported evidence separate from officially supported local recipes.


## Update 2026-03-19 (265) — crate guidance-pack deepening around message stability and channel honesty

- Revisited **P-0512 Crate Guidance Pack Kit** instead of opening another adjacent diagnostic, proc-macro, or testing lane.
- Refreshed evidence with the current Rust vision-doc supportiveness language, 2025 State of Rust survey results, Rust Reference diagnostic attributes, rustdoc `compile_fail` docs, rustdoc unstable doctest error-code caveats, current `trybuild`, `ui_test`, `miette`, and `proc-macro-error2` docs.
- Concluded that the sharper remaining gap is not raw diagnostic substrate but a receiver-facing contract for **message stability**, **guidance channel**, **environment sensitivity**, **recipe witness**, and **release drift**.
- Added a fresh 2026-03-19 product-plan note, two new schemas, and concrete scenario artifacts for `rust-src`-dependent stderr rendering, nightly doctest code-level checks, proc-macro panic escape from structured guidance, and `miette` URL presence without a witnessed fix path.
- Updated the proposal, prioritization, roadmap, epic portfolio, and repo hygiene notes so future passes keep “the misuse still fails”, “the exact message is supported”, and “the recovery recipe was checked” as separate truths.

## Update 2026-03-19 (266) — crate ecosystem pathfinder implementation pass

Questions asked:
- what is the sharpest remaining gap inside **P-0509** now that Cargo, crates.io, and docs.rs expose more selection signals?
- what should a pathfinder crate provide other people beyond ranking and generic curation?
- what distinction is still easy for maintainers to blur in ways that would mislead downstream teams?

Conclusions:
- the missing value is not another global ranking list but a receiver-facing contract for **starter-set readiness**, **lock-in cost**, and **scope split**.
- Cargo’s current command and external-tool surfaces make it realistic to build a decision-pack crate above existing workflows rather than replace them.
- crates.io and docs.rs now improve evidence import, but they still do not tell another maintainer whether a starter set may be frozen or whether one default is being over-claimed for multiple scopes.

Repository changes:
- Added `entries/2026-03-19-266.md`.
- Added `meta/frontier-salience-2026-03-19-86.md`.
- Added `meta/crate-ecosystem-pathfinder-product-plan-2026-03-19.md` and `meta/crate-ecosystem-pathfinder-lane-boundaries-2026-03-19.md`.
- Added `starter-set-readiness.report`, `lockin-cost.report`, and `scope-split.receipt` schemas plus scenario families for hidden companion crates, teaching/production default splits, and lower-lock-in stacks that lose short-term onboarding.
- Updated **P-0509** and the archive’s portfolio/meta docs to treat freeze readiness, exit cost, and scoped defaults as first-class review objects.

## Update 2026-03-19 (267) — crate upgrade-pack authority/scope pass

- Chose to deepen **P-0514 Crate Upgrade Pack Kit** instead of opening another adjacent release-tool or codemod lane.
- Reconfirmed that the missing value is a **downstream upgrade contract**, not another producer-side publish workflow.
- Promoted **hazard authority**, **package-scope truth**, and **follow-through coverage** to first-class review objects.
- Added fresh fixtures so the lane can model semver-green-but-feature-shift hazards, release-bot/workspace partiality, and source-only machine fixes honestly.


## Update 2026-03-20 (268) — crate upgrade-pack cross-archive refinement

- Re-read unrelated archives for transfer rather than topic overlap and found three moves worth stealing into **P-0514**: fail-closed source-lineage discipline for imported human-authored surfaces, conflict-transparent hazard arbitration, and explicit active follow-through state.
- Added fixture/schema stubs for `source-lineage.receipt`, `hazard-arbitration.report`, and `followthrough-state.report`.
- Reaffirmed that upgrade-pack support should not flatten nearby release/changelog/docs sources together, should not force a synthetic winner when authorities disagree, and should not let previous-lane completion silently satisfy the current lane.


## Update 2026-03-20 (270) — crate upgrade-pack source-head and readiness refinement

- Re-read the remaining unrelated donor datacubes and found two more moves worth stealing into **P-0514**: lineage-level head discipline for imported guidance surfaces, and one fused hold/candidate/freeze-ready review surface for pack maturity.
- Added `source-heads.report` and `pack-readiness.report` schemas plus concrete scenario families for operational-head-without-citation-head and hold-not-freeze-ready pack review debt.
- Reaffirmed that upgrade support should not let a floating docs `latest` page masquerade as a citation-ready migration source, and should not force reviewers to infer pack readiness by hand from a pile of otherwise honest receipts.

## Update 2026-03-20 (271) — crate upgrade-pack review-queue and consistency refinement

- Re-read the donor set again and found two final moves worth stealing into **P-0514**: explicit queued maturation work from VHK-style review backlogs, and loud contradiction checks from cross-register consistency surfaces.
- Added `review-queue.report` and `cross-register-consistency.report` schemas plus concrete scenario families for hold-state work queues and freeze-ready claims that must fail under citation/scope/follow-through contradictions.
- Reaffirmed that upgrade support should not hide remaining work in one prose next step, and should not allow a polished freeze-ready claim when the pack’s own receipts still disagree.

## Update 2026-03-20 (273) — crate upgrade-pack deviation-ledger and warning-register refinement

- Re-read the donor set again and found two more moves worth stealing into **P-0514**: expiring override records from Radical-Governance-style waiver/deviation ledgers, and one compact warning register from Goldenrule/Election-Stack-style surfaced warning discipline.
- Added `deviation-ledger.receipt` and `warning-register.report` schemas plus concrete scenario families for a temporary freeze override with public summary and a public warning register that keeps blocker severity plus deviation links visible.
- Reaffirmed that upgrade support should not carry exceptions as meeting memory, and should not let public warning labels float free of provenance, severity, or audience scope.

## Update 2026-03-20 (272) — crate upgrade-pack export-posture and publication-surface refinement

- Re-read the donor set again and found two more moves worth stealing into **P-0514**: exact public-surface manifests from EvidenceVault-style publication boundaries, and audience/redaction posture exactness from DeriveBSD/Radical-Governance-style scope discipline.
- Added `export-posture.report` and `publication-surface.manifest` schemas plus concrete scenario families for private-candidate packs that still need redaction and frozen public packs that export only exact entry points.
- Reaffirmed that upgrade support should not mistake internal maturity for public-shareable posture, and should not imply that the whole working tree is the stable public contract.


## Added 2026-03-20 (281)
- Cross-archive donor pressure from Radical-Governance suggests one more support-contract gap above exact receipts: maker/checker separation, independent challenge, and fallback review posture for consequential public surfaces.


## Update 2026-03-20 (284) — crate upgrade-pack config-basis refinement

- Re-read the donor set again and found one more move worth stealing into **P-0514**: explicit request-context / ambient-baseline disclosure for hidden config and override surfaces that materially shape an otherwise ordinary-looking lane.
- Added `config-basis.receipt` plus scenario families for checked-in `[patch]` / mirror disclosure and user-home source-replacement consistency failure.
- Reaffirmed that upgrade support should not let Cargo config hierarchy, env/config injection, or override surfaces hide behind a clean command line or an opaque `env` digest.


## 2026-03-20 — pathfinder decision-aging notes

- Frozen crate-choice artifacts need a different contract from freshness windows: they need explicit **revisit triggers** and **watch state** once a team has already frozen the answer.
- New crates.io security/publishing/`pubtime` substrate, RustSec-first malicious-crate notifications, and docs.rs visible-target shifts all increase the rate at which a previously good starter-set lock can become review-worthy without a local manifest change.
- A worthy pathfinder should distinguish `review_due` from `invalidated`, and both from automatic replacement.


## 2026-03-20 — SPIFFE / workload identity refresh

Sources checked this pass:
- https://spiffe.io/docs/latest/deploying/libraries/
- https://spiffe.io/docs/latest/spiffe-specs/spiffe/
- https://spiffe.io/docs/latest/spiffe-specs/spiffe_workload_api/
- https://spiffe.io/docs/latest/spiffe-specs/spiffe_federation/
- https://docs.rs/crate/spiffe/latest
- https://docs.rs/spiffe-rustls/latest/spiffe_rustls/
- https://docs.rs/spiffe-rustls-tokio/latest/spiffe_rustls_tokio/
- https://docs.rs/crate/spire-api/latest

Working conclusion:
- Rust now has meaningful SPIFFE/SPIRE substrate, but the archive was still missing a receiver-facing contract for identity-source basis, trust-domain scope, peer-identity handoff, and rotation/failure posture.
- Deepened **P-0134** around reviewable receipts/reports instead of opening another adjacent auth or mesh lane.


## Update 2026-03-20 (296) — cfg availability deepening around usability witnesses

- Revisited **P-0451 Cfg Availability Ledger Kit** instead of opening another neighboring docs or SemVer lane.
- Refreshed evidence with the 2025H2 `doc_cfg` goal, RFC 3631, current rustdoc `cfg(doc)` guidance, current Cargo doctest behavior, current Cargo feature-unification guidance, docs.rs hosted-build limits, docs.rs rustdoc JSON provenance notes, and the October 2025 docs.rs default-target change announcement.
- Concluded that the sharper remaining gap is not just item visibility but a receiver-facing contract for **docs-visible**, **doctest-usable**, **downstream-usable**, and **default-surface drift** truth.
- Added a new usability-boundaries note, two new schemas, and concrete scenario artifacts for docs-visible-only items and docs.rs default-target drift without new support evidence.
- Updated the proposal, roadmap, prioritization, epic portfolio, decision log, and repo hygiene notes so future passes do not flatten visible docs surface into real usability.

## Update 2026-03-20 (297) — msrv policy activation and lockfile-floor refinement

- Re-read the current Cargo/MSRV substrate and confirmed that the sharper missing layer above it is not another one-number finder but a **support contract** for policy activation, command-family floors, and lockfile-authoring compatibility.
- Added fixture/schema stubs for `policy-activation.receipt`, `command-family-floor.report`, and `lockfile-floor.receipt` plus scenario families for virtual-workspace resolver activation and lockfile-v4 authoring drift.
- Reaffirmed that pinned-lockfile buildability must not masquerade as full ongoing MSRV support for update/package/generate flows.


## Update 2026-03-20 (298) — publish-receipt deepening around capture basis and visibility state

- Re-read the current Cargo / crates.io / docs.rs substrate and confirmed that the sharper missing layer above it is not another publishing helper but a **support contract** for capture basis, receipt authority, and publication visibility.
- Added fixture/schema stubs for `capture-basis.receipt`, `receipt-authority.report`, and `publication-visibility.report` plus scenario families for tarball-retention drift and index-visible / docs-pending releases.
- Reaffirmed that local artifact capture, authoritative index truth, publish identity, and lagging docs/public surfaces must not collapse into one fake “publish succeeded” result.


## Update 2026-03-20 (300) — future-incompat visibility / suppression refinement

- Re-read the current Cargo / rustc future-incompat substrate and confirmed that the sharper missing layer above it is not another generic report viewer but a **support contract** for finding visibility, suppression basis, and latent-debt honesty.
- Added fixture/schema stubs for `finding-visibility.report` and `suppression-basis.receipt` plus scenario families for suppressed-but-recorded warnings and package-filtered recall narrowing.
- Reaffirmed that terminal cleanliness, full-report truth, package-filtered recall, and latent-but-recorded future debt must not collapse into one fake “no future incompatibility” result.

## Update 2026-03-20 (301) — test-surface isolation / reset refinement

- Re-read the current Rust testing substrate and confirmed that the sharper missing layer above fixture catalogs, topologies, and witness lineage is a **support contract** for isolation class and reset posture.
- Refreshed evidence with Rust's own test-parallelism guidance, the newly-unsafe `std::env::set_var` guidance, nextest's process-per-test / environment-safety documentation, `wiremock`'s per-test isolation guidance, `testcontainers`' isolation/cleanup docs, and `tempfile`'s OS-cleanup versus destructor-cleanup distinction.
- Added fixture/schema stubs for `isolation-class.receipt` and `reset-capability.receipt` plus scenario families for runner-specific env mutation safety, per-test mock-server freshness, destructor-based temp cleanup, and scope-based container cleanup over an external daemon.
- Reaffirmed that deterministic seams, environment requirements, runner choice, contamination risk, and cleanup mechanism must not collapse into one fake “test support” result.

## Update 2026-03-20 (302) — i18n/runtime contract refinement

- Re-read the current ICU4X / Fluent / Rust localization helper substrate and confirmed that the sharper missing layer above it is not another translation macro or pipeline, but a **support contract** for typed message arguments, locale-data profile, formatter coverage, and fallback witnesses.
- Refreshed evidence with ICU4X README/data-management/runtime-loading docs, locale fallback docs, `fluent` / `fluent-templates` docs, the Fluent high-level Rust API discussion, and neighboring helper crates (`typed-i18n`, `rust-i18n`, `i18n-embed`, `i18n-embed-fl`).
- Added fixture/schema stubs for `message-arg-schema.receipt`, `data-profile.receipt`, `formatter-coverage.report`, and `fallback-witness.report` plus scenario families for typed-arg versus formatter-coverage separation, mixed data-profile posture, and fallback-priority differences.
- Reaffirmed that using ICU4X, using Fluent, compile-time arg checks, and “has fallback” must not collapse into one fake “localization support” result.

## 2026-03-20 — schema compatibility contract pass

- Re-read **P-0124** and promoted it from generic diff-tool thinking into a receiver-facing schema-compatibility contract lane.
- Current anchors used for the pass:
  - Buf breaking change detection overview and categories — https://buf.build/docs/breaking/
  - oasdiff breaking/severity/ignore behavior — https://github.com/oasdiff/oasdiff/blob/main/docs/BREAKING-CHANGES.md
  - `jsonschema` crate validation/draft support — https://docs.rs/jsonschema/latest/jsonschema/
  - Confluent compatibility API and latest-vs-transitive behavior — https://docs.confluent.io/platform/current/schema-registry/develop/api.html and https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html
  - Schemars derive / Serde alignment — https://docs.rs/schemars/latest/schemars/derive.JsonSchema.html
  - Rust native compatibility substrate (`schema-registry-compatibility`) — https://docs.rs/schema-registry-compatibility/latest/schema_registry_compatibility/
- Main conclusion: the missing crate is not another parser or registry, but a compact way to publish **comparison basis**, **compatibility profile**, **finding strength**, and **policy decision**.



## 2026-03-20 — Cargo config invocation-basis / replayability pass

- Re-read **P-0474** and promoted it from generic effective-config/origin-trace thinking into a receiver-facing per-invocation contract lane.
- Current anchors used for the pass:
  - Cargo configuration reference — https://doc.rust-lang.org/cargo/reference/config.html
  - Cargo unstable features (`cargo config`) — https://doc.rust-lang.org/cargo/reference/unstable.html
  - Cargo changelog (1.94 include stabilization; 1.93 `--config` precedence/path fixes) — https://doc.rust-lang.org/cargo/CHANGELOG.html
  - Cargo 1.93 development-cycle notes for config-include design and optional includes — https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Main conclusion: the missing crate is not another parser or viewer, but a compact way to publish **invocation basis** and **replayability** above effective config, origins, paths, and redaction.

## 2026-03-20 — secrets-kit contract refresh

- Confirmed `secrecy` currently documents three explicit goals: explicit secret access, prevention of accidental debug leakage, and secure wiping on drop via `zeroize`, while also explicitly stating it does **not** provide `mlock(2)` / `mprotect(2)` advanced memory protection and warning that `serde` deserialization can introduce intermediate plaintext callers must clean up.
- Confirmed `zeroize` currently documents stable volatile-write-and-fence zeroization guarantees and explicitly limits its scope rather than claiming register clearing or broader protected-memory semantics.
- Confirmed `keyring` currently documents explicit per-platform secure-store features, bring-your-own credential builders, and a mock credential store that provides no persistence.
- Confirmed `secrets` currently documents protected-memory guarantees including `mprotect`, guard pages, `mlock`, zero-on-drop, and borrow-gated access, which makes `zeroize_only` versus `protected_memory` a real support boundary.

## 2026-03-20 — observability delivery/completeness contract pass

- Re-read **P-0518** and promoted it from “signal + route + redaction” thinking into a receiver-facing delivery/completeness contract lane.
- Current anchors used for the pass:
  - Tokio tracing topic — https://tokio.rs/tokio/topics/tracing
  - `tracing-appender` nonblocking docs + `WorkerGuard` + `ErrorCounter` — https://docs.rs/tracing-appender/latest/tracing_appender/non_blocking/ ; https://docs.rs/tracing-appender/latest/tracing_appender/non_blocking/struct.WorkerGuard.html ; https://docs.rs/tracing-appender/latest/tracing_appender/non_blocking/struct.ErrorCounter.html
  - OpenTelemetry sampling docs — https://opentelemetry.io/docs/concepts/sampling/
  - `SdkTracerProvider` + `SdkLoggerProvider` flush/shutdown docs — https://docs.rs/opentelemetry_sdk/latest/opentelemetry_sdk/trace/struct.SdkTracerProvider.html ; https://docs.rs/opentelemetry_sdk/latest/opentelemetry_sdk/logs/struct.SdkLoggerProvider.html
  - `opentelemetry` metrics docs + `tracing-opentelemetry` metrics layer docs — https://docs.rs/opentelemetry/latest/opentelemetry/ ; https://docs.rs/tracing-opentelemetry/latest/tracing_opentelemetry/struct.MetricsLayer.html
  - `opentelemetry-appender-tracing` docs + OpenTelemetry Rust instrumentation-libraries docs — https://docs.rs/opentelemetry-appender-tracing/latest/opentelemetry_appender_tracing/ ; https://opentelemetry.io/docs/languages/rust/libraries/
- Main conclusion: the missing crate is not another exporter, appender, or queue, but a compact way to publish **delivery posture** and **completeness class** above signal, route, schema, and sensitivity artifacts.


## 2026-03-20 — add channel-surface contract lane

- Chose to add **P-0529** instead of deepening another adjacent lifecycle/resource/observability lane because the archive still lacked one receiver-facing artifact for channel semantics.
- Decided that the first implementation pass should elevate **capacity posture**, **overflow policy**, **delivery obligation**, and **shutdown/drain truth** into first-class artifacts.
- Reaffirmed that “bounded”, “broadcast”, “watch”, “queue”, or “clean shutdown” must not collapse into one fake “channel support” verdict.


## 2026-03-21 — CLI surface contract pass

- Re-read the current Rust CLI substrate and promoted the missing layer from vague “better CLI UX” thinking into a receiver-facing CLI contract lane.
- Current anchors used for the pass:
  - `clap` docs and source aspirations — https://docs.rs/clap/latest/clap/ and https://docs.rs/clap/latest/src/clap/lib.rs.html
  - `anstream::AutoStream` docs — https://docs.rs/anstream/latest/anstream/struct.AutoStream.html
  - `std::io::IsTerminal` docs — https://doc.rust-lang.org/std/io/trait.IsTerminal.html
  - `indicatif` docs — https://docs.rs/indicatif/latest/indicatif/
  - `dialoguer` docs — https://docs.rs/dialoguer/latest/dialoguer/
  - `std::process::ExitCode` docs — https://doc.rust-lang.org/std/process/struct.ExitCode.html
  - `trycmd`, `snapbox`, and `assert_cmd` docs — https://docs.rs/trycmd/latest/trycmd/ ; https://docs.rs/snapbox/latest/snapbox/ ; https://docs.rs/assert_cmd/latest/assert_cmd/
  - 2025 State of Rust survey — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Main conclusion: the missing crate is not another parser or snapshot harness, but a compact way to publish **command surface**, **output modes**, **terminal posture**, and **exit semantics** above today’s CLI substrate.
- Added a new product-plan note, lane-boundary note, proposal, and fixture/schema pack so future passes stop collapsing parser ergonomics, human output, machine output, prompt posture, and exit meaning into one fake “nice CLI” story.


## Update 2026-03-21 (314) — debuggability backend-coverage refinement

- Re-read the official Rust debugging survey and confirmed that the sharper missing layer above symbols, sidecars, and visualizers is now a **support contract** for debugger-family coverage and capability ceilings, not another generic debugger wishlist.
- Refreshed evidence with the Rust debugging survey, the 2025 State of Rust survey, Cargo build-cache / profile docs, `rustc` `strip` docs, the stable `debugger_visualizer` reference, Cargo unstable `trim-paths`, and the March 2026 Build Dir Layout v2 call-for-testing.
- Added a schema stub for `debugger-backend-coverage.report` plus scenario families for Windows NatVis/PDB posture that still does not prove uniform backend support, and symbol-rich builds that still require manual review before claiming async-debugging or expression-evaluation support.
- Reaffirmed that artifact posture, visualizer assets, backend-family coverage, advanced debugger capabilities, and source-lookup consequences must not collapse into one fake “debugger support” result.


## 2026-03-21 refinement — Cargo cache policy now needs recovery obligation and cache-surface truth

- Treat `meta/cargo-global-cache-policy-product-plan-2026-03-21.md` and `meta/cargo-global-cache-recovery-boundaries-2026-03-21.md` as the current working sketch for **P-0480**.
- Keep **inventory-basis truth**, **cache-surface truth**, **recovery-obligation truth**, **offline-cost honesty**, and **mixed-toolchain compatibility truth** explicit.
- Prefer tiny receiver-facing artifacts such as `cache-surface.receipt`, `recovery-obligation.report`, and `gc.receipt` rather than another disk cleaner, `target/` janitor, or remote-cache server.

## Update 2026-03-21 (318) — workspace toolchain manifest route / root refinement

- Re-read the current Cargo / rustup / third-party tool-install substrate and confirmed that the sharper missing layer above it is not another binary installer but a **workspace contract** for install-root posture, tool-route authority, and rustup-context honesty.
- Refreshed evidence with the current Cargo install docs, current external-tools docs, current rustup override docs, the still-open Cargo design issue for dev-dependency commands, and current docs for `cargo-run-bin` and `cargo-binstall`.
- Added fixture/schema stubs for `install-root.receipt` and `tool-route.receipt` plus scenario families for cargo-home subcommand shadowing, workspace-local versus ephemeral CI roots, and rustup-override context drift.
- Reaffirmed that declaring a workspace tool, installing a tool somewhere, resolving a requested command, and running under the intended toolchain context must not collapse into one fake “repo-pinned tool” result.


## Update 2026-03-21 (321) — comptime reflection bridge productization pass

- Re-read the current Rust reflection/comptime goal and confirmed that the sharper missing layer above it is not another reflection framework but a **bridge contract** for schema source, coverage scope, execution posture, and loss accounting.
- Refreshed evidence with current `bevy_reflect`, `facet`, `facet-reflect`, and `serde_reflection` docs so runtime registries, static `SHAPE` exports, runtime value views, and format-description tracing stay in their own authority classes.
- Added product-plan/boundary notes plus fixture/schema stubs for `schema-source.receipt`, `coverage-scope.report`, `execution-posture.receipt`, and `loss-accounting.report`, with scenario families for Bevy registered-monomorphization limits, Facet static-shape exports, future compile-time-only adapters, and Serde format-schema boundaries.
- Reaffirmed that "reflection-like metadata exists" must not masquerade as full generic-family coverage, registry-free execution, or runtime-mutation support.


## Update 2026-03-21 (324) — test-run artifact standard productization pass

- Re-read the current Rust test-run substrate and confirmed that the sharper missing layer above it is not another test runner or JUnit exporter but a **portable artifact contract** for run identity, selection basis, attempt topology, and bundle sensitivity.
- Refreshed evidence with Cargo test docs, Cargo's external-tools JSON caveat, the Rust libtest-JSON project goal, `libtest-mimic` docs, nextest recording/replay/portable-recording docs, and nextest retry/stress docs.
- Added product-plan/boundary notes plus fixture/schema stubs for `run-identity.receipt`, `selection-basis.receipt`, `attempt-topology.report`, `bundle-sensitivity.receipt`, and `testrun-bundle.manifest`, with scenario families for sensitive portable recordings, unstable libtest-JSON imports, libtest-mimic harness identity, and retry/stress/fail-fast topology drift.
- Reaffirmed that “has logs”, “has JSON”, “has JUnit”, and “has a nextest recording” must not masquerade as one stable portable test-run contract.


## Update 2026-03-21 (329) — verification campaign productization pass

- Re-read the current Rust verification / safety-critical substrate and confirmed that the sharper missing layer above it is not another verifier but a **cross-tool campaign contract** for obligation inventory, lane semantics, trust surface, policy evaluation, and comparability.
- Refreshed evidence with current Rust 2026 flagship themes, the January 2026 safety-critical Rust post, the Safety-Critical Rust Consortium page, and current Miri / Kani / Creusot / Prusti / Flux / Verus documentation.
- Expanded the fixture pack around `campaign-manifest`, `obligation-record`, `lane-result`, `trust-ledger`, `policy-evaluation.report`, `campaign-diff.report`, and `verify-campaign`, with scenario families for Miri evidence-class limits, Kani contract-stub trust cost, Creusot replay-context drift, Prusti trusted items, and Flux+Verus partial-scope closure.
- Reaffirmed that “we ran verification tools” must not masquerade as a stable cross-tool campaign verdict unless obligations, trust surface, policy, and comparability stay explicit.

- 2026-03-21: revisited **P-0458 Async Dyn Transition Kit** after the archive's product-shaping passes to add `meta/async-dyn-transition-product-plan-2026-03-21.md`, `meta/async-dyn-transition-lane-boundaries-2026-03-21.md`, and new tooling-interop / native-readiness artifacts.

- Chose to deepen **P-0503 Assurance Case Workbench Kit** instead of opening another verifier, evidence-bundle variant, or standards wrapper because the missing layer is now the review/import contract above the existing evidence substrate.


## Update 2026-03-22 (342) — sanitizer workflow contract productization pass

- Re-read the current Rust sanitizer substrate and confirmed that the sharper missing layer above it is not another shell wrapper or target matrix, but a **workflow-and-evidence contract** for instrumentation scope, runtime linkage, symbolization route, and suppression policy.
- Refreshed evidence with the 2026 project-goals slate, the January 2026 goals update, the current sanitizer unstable-book docs, current Cargo `-Z build-std` requirements, the March 2026 Rust challenges write-up, and the January 2026 safety-critical Rust post.
- Added product-plan/boundary notes plus fixture/schema stubs for `instrumentation-scope.receipt`, `runtime-linkage.receipt`, `symbolization-route.receipt`, and `suppression-policy.receipt`, with scenario families for MemorySanitizer full-instrumentation requirements, Cargo `--target` host-helper exclusion, mixed Rust/C++ `external-clangrt` routing, missing `llvm-symbolizer`, and visible suppression debt.
- Reaffirmed that “sanitizer enabled”, “job passed”, “stack trace exists”, and “suppression file present” must not masquerade as one strong sanitizer-evidence verdict.

## Update 2026-03-22 (343) — crate-health routing / continuity productization pass

- Re-read the current Rust/Foundation maintenance and sustainability material and confirmed that the sharper missing layer above health-profile metadata is not another score, but an operational stewardship contract for **work routing**, **response-channel posture**, and **continuity backstops**.
- Refreshed evidence with the January 2026 Inside Rust maintenance post, the 2025 State of Rust survey, the January 2026 crates.io development update, the Rust Foundation 2026–2028 strategic plan, the 2025 stewardship statement, and current GitHub docs for CODEOWNERS and private vulnerability reporting.
- Added product-plan/boundary notes plus fixture/schema stubs for `work-routing.report`, `response-channel.receipt`, and `continuity-backstop.report`, with scenario families for public bug routes vs private security routes, CODEOWNERS limits, and single-primary maintainers with org backstops.
- Reaffirmed that “issues are open”, “CODEOWNERS exists”, “private vulnerability reporting exists”, and “an org owns the repo” must not masquerade as one honest crate stewardship contract.

## 2026-03-22 — unsafe contracts / witness honesty scan

Fresh inputs that materially changed the archive:

- 2026 flagship goals now name safety-critical work including normative unsafe documentation and related building blocks.
- 2025h1 std-contracts work says the standard library already has many safety conditions documented, that experimental contract attributes were accepted for implementation, and that the direction is contract-as-code rather than prose-only guidance.
- Miri remains critical substrate but still documents important limits, which makes witness-boundary artifacts more important than a bare pass/fail bit.
- Rust 2024 `unsafe extern` and unsafe attributes keep making “unsafe obligation classes” broader than memory-model-only review.

## 2026-03-22 — delegated build-script support contract scan

Fresh scan result: current Cargo sources now make delegated build-time support reviewable enough to justify deepening **P-0508** instead of adding another helper crate.
Key anchors used in this pass:

- GSoC 2025 results for multiple-build-scripts, deterministic ordering, and separate output directories;
- Cargo 1.93 development notes for artifact-dir staging, collision checking, and concurrency constraints;
- Cargo build-script docs for `OUT_DIR`, order-sensitive directives, metadata, and `links`-override behavior;
- Cargo external-tools docs for machine-readable build observations;
- Cargo unstable docs for metabuild / multiple-build-scripts / any-build-script-metadata;
- cargo issue #14948 for the broader direction of reducing handwritten build-script dependence.

Decision from the scan: the missing value is a support-contract layer for **unit topology**, **output-lane ownership**, **override authority**, **bridge posture**, and **delegation drift**.


## 2026-03-22 (350) — compile-time sandbox policy refresh

- Re-checked the current upstream compile-time sandbox direction and confirmed that the sharper missing layer above it is not another sandbox runtime but a **reviewable policy contract**.
- Refreshed evidence with the sandboxed-build-scripts project goal, compiler-team MCP #475, Cargo issue #5720, accepted host-runner issue #16591, current Cargo environment/config docs, unstable `--compile-time-deps`, release notes on build-script `OUT_DIR` behavior, and current primary-source docs for `cackle` and `cargo-sandbox`.
- Added `policy-authority.receipt`, `actor-capability.matrix`, `enforcement-mode.receipt`, `exception-ack.record`, `sandbox-policy-drift.diff`, and `sandbox-support-bundle.manifest` schemas plus five new compile-time sandbox fixture families.

### Future caution
1. Do not let “sandboxed build” hide observe-only mode.
2. Do not let proc-macro coarse granularity impersonate per-macro isolation.
3. Do not let workspace or CI overlays broaden power without becoming the visible authority route.


## Update 2026-03-22 (351) — rebuild-causality baseline / reverse-impact productization pass

- Re-read the current Cargo build-analysis and relink-don’t-rebuild substrate and confirmed that the sharper missing layer above Cargo sessions/reports is not another recorder, but a **support contract** for baseline authority and reverse-impact honesty.
- Refreshed evidence with the Cargo unstable build-analysis docs, Cargo 1.94 development-cycle update, Cargo changelog, the 2025h2 build-analysis goal, the 2025h2 relink-don’t-rebuild goal, and the 2025 State of Rust survey.
- Added product-plan/boundary/frontier notes plus fixture/schema stubs for `baseline-authority.receipt` and `reverse-impact.report`, with scenario families for rejecting a nearer but incompatible session, preferring a farther same-profile/target baseline, and keeping reverse fanout separate from proven interface change.
- Reaffirmed that “Cargo had a session id”, “cargo report rebuilds printed a reason”, “the nearest prior run existed”, and “dependents rebuilt” must not masquerade as one honest rebuild explanation.


- Re-read the current next-solver substrate and confirmed that the sharper missing layer is not another compile-fail harness but a **support contract** for solver-lane truth, obligation classes, diagnostic normalization, and minimization lineage above corpus runners and witness-generation workflows.
- Added `meta/trait-solver-drift-frontier-2026-03-22.md` so P-0442 stays separate from P-0446 borrowck transition work, SemVer witness generation, and generic rustc tracing/debugging.

## 2026-03-22 — MC/DC coverage evidence deepening

Primary-source refresh used for this pass:
- Rust 2026 flagship themes now list **implement MC/DC coverage support**.
- The rustc book documents source-based coverage through `-C instrument-coverage` and notes detailed mode selection through unstable `-Z coverage-options`.
- `cargo-llvm-cov` currently exposes unstable `--branch` and `--mcdc` options.
- Rust issue #124118 publishes a concrete list of supported and unsupported branch-coverage constructs.

Archive judgment: the missing value is no longer another coverage runner. It is a support-contract layer for decision authority, construct support, independence evidence, caveat basis, and evidence lineage.


## 2026-03-22 — Cargo script / single-file-package deepening

- Re-read the current Cargo script / single-file-package substrate and confirmed that the sharper missing layer above it is not another runner, but a **support-contract bundle** for frontmatter authority, discovery scope, invocation interpretation, cache residency, and export lineage.
- Refreshed evidence with the cargo-script goal page, Cargo unstable docs for `script`, `single-file packages`, and manifest-commands, plus the Cargo 1.94 development-cycle notes on workspace/config discovery.
- Added product-plan/boundary notes plus fixture/schema stubs for `frontmatter-authority.receipt`, `discovery-scope.receipt`, `invocation-interpretation.receipt`, `cache-residency.receipt`, `export-lineage.plan`, and `script-support-bundle.manifest`, with scenario families for defaulted edition authority, manifest-command semantics, disabled workspace auto-discovery with parent config influence, hashed target-dir/lockfile residency, and export lineage.
- Reaffirmed that “Cargo can run the script”, “the frontmatter parsed”, “no workspace was discovered”, and “we can export later” must not masquerade as one honest single-file-package support verdict.

## 2026-03-22 (368) — broad frontier rerank and crate-knowledge scan

- Re-read the latest archive and refreshed it against the 2025 State of Rust survey, March 2026 challenges post, compiler-performance survey, debugging survey, 2026 goals flagships, safety-critical write-up, crates.io development update, Rust Foundation strategy, and docs.rs rustdoc/build docs.
- Confirmed that the strongest missing value is still support-contract infrastructure, not another round of wrapper crates.
- Added `meta/ecosystem-gap-map-2026-03-22.md` as the current broad territory map.
- Added **P-0536 Crate Knowledge Pack Kit** after confirming the archive already had rustdoc-json, docs.rs parity, doctest, and docs-coverage lanes but still lacked one provenance-aware handoff bundle for support, search, and assistant-grade crate understanding.
- Reaffirmed that broad scans should rerank, synthesize, and eliminate before proliferating new lanes.



## 2026-03-22 (369) — crate knowledge pack productization + cross-sector opportunity mapping

- Re-read the current P-0536 substrate and confirmed that the sharper missing layer is not another docs portal, rustdoc parser, or assistant UX, but a **support-contract bundle** for API authority, docs-source provenance, example lineage, hosted docs.rs presence, visibility truth, and slice policy.
- Refreshed evidence with the 2025 State of Rust survey, March 2026 Rust challenges post, docs.rs about/builds/metadata/rustdoc-json pages, Cargo `cargo rustdoc` docs, rustdoc unstable JSON docs, RFC 2963, the crates.io January 2026 update, the Rust 2026 flagships page, the Rust Foundation 2026–2028 strategy, and the January 2026 safety-critical write-up.
- Added product-plan and lane-boundary notes plus fixture/schema stubs for `api-surface.receipt`, `docs-source.manifest`, `example-lineage.report`, `docsrs-presence.import`, `knowledge-slice.manifest`, `knowledge-diff.report`, and `knowledge-pack.manifest`.
- Added `meta/cross-sector-opportunity-map-2026-03-22.md` to keep future wide scans broad in topic coverage while still preferring synthesis into existing top support-contract lanes.
- Reaffirmed that “rustdoc JSON exists”, “docs.rs built the crate”, “README has snippets”, “doctests passed”, and “an assistant index can be built” must not masquerade as one honest crate-knowledge answer.


## 2026-03-22 (370) — dependency lifecycle seam-proof / source-boundary scan

Primary-source refresh used for this pass:
- the January 2026 safety-critical write-up explicitly describing higher-criticality workflows where teams constrain or replace third-party crates;
- the March 2026 Rust challenges write-up emphasizing domain-specific ecosystem maturity problems rather than one universal beginner-only story;
- the January 2026 crates.io development update adding Security-tab visibility, Trusted Publishing Only Mode, SLOC, and `pubtime`;
- the January 2026 maintenance post stressing that maintenance work is broad, ongoing, and often invisible;
- Cargo docs clarifying the split among `[patch]`, restricted path overrides, exact-source replacement, and read-only vendoring;
- and the Rust Foundation 2026–2028 strategy emphasizing stable infrastructure and sustainable maintenance.

Archive judgment from the scan:
the missing value is not another graph browser, trust score, or offline/vendor tool.
It is a local architectural contract for **lane placement**, **seam proof**, **typed exceptions**, **imported context**, and **lifecycle drift**.


## 2026-03-22 (372) — crate-health imported-signal / routing-drift scan

Primary-source refresh used for this pass:
- the January 2026 maintenance post describing maintenance as broad, ongoing work rather than a narrow release-status story;
- the 2025 State of Rust survey noting online docs remain canonical while concern about developer and maintainer support ticked upward;
- the January 2026 crates.io update adding Security tab, Trusted Publishing Only Mode, SLOC, and `pubtime`;
- GitHub docs clarifying that CODEOWNERS is review-routing substrate, private vulnerability reporting is a distinct secure channel, and repository transfer preserves many objects without making continuity equivalence automatic;
- and the Rust Foundation 2026–2028 strategy elevating Sustainable Maintenance as a core pillar.

Archive judgment from the scan:
the missing value is not another maintenance score, badge, or donor dashboard.
It is a receiver-facing contract for **imported stewardship context**, **routing drift**, **portable support bundles**, and **manual-review honesty**.


## Update 2026-03-22 (373) — async runtime assurance qualification/diff/bundle refinement

- Re-read **P-0532 Async Runtime Assurance Profile Kit** and confirmed that the sharper missing layer is no longer just a runtime-choice summary; it is a receiver-facing contract for **qualification basis**, **runtime drift meaning**, and **portable bundle shape**.
- Refreshed evidence with the March 2026 Rust challenges post, the January 2026 safety-critical Rust post, the 2026 flagships page, current Tokio runtime and `spawn_blocking` docs, current `tokio-metrics` and `RuntimeMetrics` docs, current Embassy executor docs, and the RTIC book’s app/timer-queue sections.
- Added `meta/async-runtime-assurance-artifact-completeness-plan-2026-03-22.md`, three new schemas, and concrete scenario artifacts for Tokio docs-plus-metrics not implying on-target qualification, Embassy board-scope review gaps, Tokio→RTIC runtime-model drift, and mixed host Tokio + target Embassy bundle shape.

## 2026-03-22 (377) — rebuild-causality comparison-scope / route pass

Consulted sources:
- 2025 State of Rust Survey Results — compile-time and storage pain remain prominent.
- What we heard about Rust's challenges — build times remain an active challenge lane.
- Cargo unstable build-analysis docs — persisted sessions plus `cargo report sessions|timings|rebuilds`.
- This Development-cycle in Cargo: 1.94 — report commands and build-analysis substrate gaining shape.
- Relink don't Rebuild — reverse dependencies still rebuild more broadly than users want.
- Rework Cargo Build Dir Layout — finer-grained locking and route/layout work remain active.
- Call for Testing: Build Dir Layout v2 — workflows touching `build-dir` / `target-dir` should be exercised explicitly.
- Cargo build cache docs — final artifacts and intermediate artifacts now have explicit distinct route language.
- rust-analyzer configuration — private `cargo.targetDir` remains a documented route split used to avoid locking.

Main takeaway:
The missing value is no longer another build recorder. It is a receiver-facing rebuild bundle that states comparison scope, route drift, evidence source, exactness, and imported adjacent context honestly.

## 2026-03-22 (378) — deepen lock-contention witness around package-cache lock modes and mitigation outcomes

- Re-read the current Cargo/rust-analyzer substrate and confirmed that the sharper missing layer above it is not another lock workaround, but a **support-contract bundle** for package-cache lock-mode truth, residual contention after mitigation, and honest before/after outcome diffs.
- Refreshed evidence with the rust-analyzer FAQ and configuration docs, Cargo build-cache/config/unstable docs, the March 2026 build-dir-layout-v2 testing call, the Cargo 1.94 development-cycle update, and the current Cargo internal `cache_lock` docs.
- Added product-plan/boundary updates plus fixture/schema stubs for `package-cache-lock-mode.receipt`, `residual-contention.report`, and `mitigation-outcome.diff`, with scenario families for non-interfering download-exclusive package-cache activity, mutate-exclusive cache GC blocking, residual proc-macro/build-script overlap after target-dir mitigation, and artifact-duplication-heavy outcomes that still require manual review.
- Reaffirmed that “same package cache root”, “conflicting lock mode”, “mitigation applied”, and “contention solved” must not masquerade as one honest lock-contention verdict.

## 2026-03-22 (379) — deepen crate knowledge pack around material basis and export-policy honesty

- Re-read the current docs/search/support substrate and confirmed that the sharper missing layer is not another docs UI or assistant wrapper, but a **support-contract bundle** for exact material basis, export policy, and excerpt lineage.
- Refreshed evidence with the 2025 State of Rust survey, the March 2026 Rust challenges post, current docs.rs about/builds/metadata/rustdoc-json/download/redirections pages, current Cargo unstable `output-format` docs, `cargo rustdoc`, and rustdoc’s `--output-format json` docs.
- Added product-plan/boundary updates plus fixture/schema stubs for `material-basis.receipt`, `export-policy.receipt`, and `excerpt-lineage.report`, with scenario families for floating docs.rs redirects, pre-2025 hosted JSON gaps, download-archive caveats, and public support exports that redact internal playbooks but keep exact excerpt lineage.
- Reaffirmed that “docs.rs has a latest URL”, “rustdoc JSON exists somewhere”, “the README was imported”, and “an assistant slice was emitted” must not masquerade as one honest crate-knowledge verdict.

## 2026-03-22 (381) — FFI support still lacks one authority/lifecycle contract above the generators

Fresh sources reviewed for this pass included:
- the February 2026 program-management update naming **Cross-language interop** as an application area;
- the Rust 2024 Edition Guide page on `unsafe extern` blocks making signature correctness an explicit author responsibility;
- RFC 2945 on `"C-unwind"` and unresolved corners around foreign unwind / `catch_unwind` behavior;
- UniFFI object-reference and async FFI docs on foreign-thread reality, `Send+Sync`, `Arc`-backed handles, completion callbacks, cancellation hooks, and free requirements;
- CXX docs on shared vs opaque types and unsafe `ExternType` assertions;
- Diplomat docs on opaque types and backend-specific `Result` lowering;
- and WIT/component-model docs on resource ownership and generated bindings from WIT worlds.

Archive judgment from those sources:
- P-0121 is strongest when it owns **interface authority**, **callback lifecycle**, and **portable review bundles** above the generation/runtime substrate.
- Future passes should avoid rephrasing this as another language SDK helper, packaging suite, or generic FFI safety score.


## 2026-03-22 (384) — FFI projection/parity scan

Fresh sources reviewed for this pass included:
- the February 2026 program-management update keeping cross-language interop explicit as an application area;
- current release notes keeping `unsafe extern` and `extern "C-unwind"` as explicit boundary substrate;
- UniFFI’s current foreign-language binding docs stating that binding generation produces source code but does not build that code;
- UniFFI’s current proc-macro docs documenting mixed UDL/proc-macro surfaces and `#[cfg]` caveats inside `#[uniffi::export]` blocks;
- Diplomat backend-attribute docs documenting rename/namespace and other backend-shaped projections;
- current `cbindgen` docs documenting broad binding-header configuration;
- current `wit-bindgen-rust` options documenting export-macro naming/visibility, custom-section helper generation, and generated-type breadth;
- and current CXX reference docs documenting source-of-truth direction, naming, namespaces, async, and error lanes.

Archive judgment from those sources:
- P-0121 is strongest when it owns **projection basis**, **derivative parity**, and **receiver-visible projection drift** above the existing generation/runtime substrate.
- Future passes should avoid rephrasing this as another generator comparison, language-package shipkit, or generic compatibility score.

## 2026-03-22 (385) — deepen MC/DC evidence around campaign scope, comparison basis, and qualification honesty

Consulted sources:
- Rust 2026 flagship themes — MC/DC remains an explicit safety-critical milestone.
- rustc coverage book — doctest inclusion still needs unstable persistence flags and a known doctest source-line issue remains documented.
- nightly rustc `coverage-options` enum docs — `Block`, `Branch`, and `MCDC` modes are explicit, with `MCDC` adding instrumentation for certain boolean expressions not directly used for branching.
- `cargo-llvm-cov` README/docs — branch/doctest support remain unstable; `--target` and `--remap-path-prefix` materially affect scope/interpretation.
- Clang source-based coverage docs — raw profiles have no backward/forward compatibility guarantees; coverage mappings are not forward-compatible; MC/DC instrumentation has hard limits and exclusion warnings.
- Rust MC/DC tracking and branch-limitation issues — support is still incomplete and construct-sensitive.
- Toward Modified Condition/Decision Coverage of Rust — Rust-specific semantics like `?`, pattern matching, and constants still need language-aware treatment.

Main takeaway:
The missing value is no longer another runner or another overall percentage. It is a receiver-facing MC/DC bundle that states campaign scope, comparability, and qualification class honestly before it ever claims improvement or readiness.



# Research ledger — 2026-03-22 frontier pass (386)

## Sources consulted
- Rust Reference: debugger visualizers
- rustc dev guide: debugger visualizers
- GDB manual: auto-load safe path
- LLDB data formatter docs
- Rust debugging survey 2026

## Main notes
- The key distinction for P-0491 is now four-way: asset inventory, activation route, formatter origin, and backend verdict.
- Toolchain launchers such as `rust-lldb` are real formatter-origin evidence, but they are not the same kind of evidence as crate-embedded assets.
- GDB safe-path refusal should stay a route/trust fact, not silently degrade into generic asset failure.



## 2026-03-22 (387) — deepen doctest support around extraction basis and grouping comparability

Consulted sources:
- 2025 State of Rust survey — docs remain the preferred canonical reference.
- Rust for Linux tooling goal — stable rustdoc features to extract/customize doctests remain an explicit goal.
- rustdoc unstable-features docs — `--output-format doctest` emits JSON with `format_version`, original/re-written code, wrapper details, and computed attributes.
- rustdoc documentation tests docs — preprocessing rules, hidden lines, crate injection, `compile_fail`, `no_run`, edition tags, merged doctests, `standalone_crate`, and target-specific ignores are all concrete substrate.
- Rust 2024 edition guide — merged doctests materially change compilation grouping while preserving separate-process execution.
- Cargo test docs — doctest execution details are not guaranteed and may change in the future.
- Rust release notes — doctest xcompile, `ignore-*`, and `--test-runtool` / `--test-runtool-arg` are current official substrate.

Main takeaway:
The missing value is no longer another “test the examples” layer. It is a receiver-facing bundle that states **what extraction authority produced the manifest, whether two doctest bundles are even comparable, and what exact receipts must travel together in review or support handoff**.

## 2026-03-22 — P-0481 route/basis refresh

- Re-read **P-0481** and confirmed the proposal still had real value, but the strongest missing layer was no longer “runner profiles exist” — it was route provenance and execution-basis honesty.
- Refreshed evidence with rustdoc’s command-line docs for `--test-runtool`, Cargo unstable docs for `doctest-xcompile`, current release notes for target-specific `ignore-*` and stable runtool flags, Cargo config docs for `target.<triple>.runner` and precedence, Cargo test docs for execution-model caveats and compile-vs-run working-directory split, the Rust-for-Linux tooling goal, and rustdoc’s unstable `--persist-doctests` docs.
- Concluded that the worthiest next slice was to add `runner-route.receipt`, `execution-basis.receipt`, and a portable runtool-support bundle instead of adding another emulator helper or another docs wrapper.


## 2026-03-22 — P-0491 probe-surface / comparison-basis refresh

- Re-read **P-0491** and confirmed the proposal still had real value, but the strongest missing layer was no longer only asset activation or formatter origin — it was probe-surface and comparison-basis honesty.
- Confirmed from current primary docs that CDB-powered surfaces can appear through WinDbg, VSCode, and part of Visual Studio; that `lldb-dap` is a distinct observation layer above LLDB; that NatVis delivery has explicit precedence and hot-reload differences; and that GDB printer versioning/objfile registration matter to comparability.
- Promoted `probe-surface.receipt` and `comparison-basis.receipt` as the next implementation-critical artifacts for **P-0491**.


## 2026-03-22 (390) — deepen MC/DC evidence around profile compatibility, campaign policy, and manual-review debt

Signals reviewed:
- Rust 2026 flagship themes — MC/DC remains an explicit safety-critical milestone.
- rustc coverage docs — doctest persistence remains unstable and `-Z coverage-options` remains unstable.
- rustc codegen options docs — coverage profile data format may change and may not work with non-shipped tools.
- cargo-llvm-cov README/docs — `--mcdc` and doctest support remain unstable.
- LLVM source-based coverage + instrumentation-profile docs — raw profiles have no backward/forward compatibility guarantees; indexed profiles are not forward-compatible.
- Rust branch-coverage limitations issue — `match` arms, or-patterns, `?`, `.await`, and macro-generated branches remain unsupported/caveat-heavy.

Conclusion: the missing value is no longer another runner or another trend chart. It is a receiver-facing MC/DC bundle that states profile durability, explicit construct policy, and unresolved review debt before it ever claims retention safety or release readiness.

## 2026-03-22 (391) — broad rerank surfaced compile iteration feedback as a missing cross-domain support lane

Consulted sources:
- 2025 State of Rust survey — compile/resource pain and debugging remain notable productivity limits.
- Rust challenges write-up — compile performance is the universal productivity tax; GUI iteration, async fragmentation, embedded maturity, and ecosystem navigation are explicit pain points.
- Rust compiler-performance survey 2025 results — small-change rebuild workflows remain painful and relink/rebuild work is still experimental.
- Rust 1.90 LLD-by-default announcement — link latency is important enough to change upstream defaults.
- `relink-don't-rebuild` goal — dependency rebuild avoidance remains active but unfinished substrate.
- `subsecond`, Dioxus hot reload docs, Wild README, and cargo-watch README — the ecosystem now has real pieces for watch loops, UI reload, runtime patching, and faster linking, but not one stable review contract above them.

Main takeaway:
The missing value is no longer only “faster builds”. It is a receiver-facing compile-iteration bundle that states patch eligibility, linker route, reload surface, state continuity, restart fallback, and latency-budget truth honestly.


## Added 2026-03-22 (392): cargo-event-stream deepening
- **P-0042 cargo-event-stream** — Cargo's own 2026 structured-logging/build-analysis direction now makes the missing value much sharper: not “more JSON”, but a stable crate-level handoff for native events, foreign output, rendering policy, session provenance, and portable export.
## 2026-03-23 (398) — example support now needs official-start authority, entrypoint viability, and hosted-visibility honesty

Consulted sources:
- 2025 State of Rust survey — online docs remain the preferred canonical learning reference, followed by code.
- What people love about Rust — crates still need more supportive interfaces and guidance.
- Rust API Guidelines — examples are copied verbatim by users.
- Cargo target docs — examples are built by `cargo test` by default, but not run by default; `required-features` can skip example targets.
- rustdoc scraped-examples docs — scraping remains unstable.
- Cargo unstable scrape-examples docs — scraping can be suppressed by dev-dependency conditions unless a target opts in.
- docs.rs metadata/build docs — features/targets/default-target can reshape hosted visibility, while docs.rs still runs in a constrained sandbox with blocked network access and mostly read-only sources.

Main takeaway:
The missing value is no longer only “examples exist and were witnessed once.” It is a receiver-facing bundle that states **what source authorized the start path, which entrypoints are viable in which lanes, and what hosted visibility does or does not prove**.

## 2026-03-22 (402) — debuggability support capability-witness refresh

- Reviewed the Rust debugging survey (2026-02-23) for current upstream framing: support still varies by debugger and OS, with async debugging and Rust expression evaluation explicitly called out as missing ideals.
- Reviewed the rustc debugging-support guide for concrete debugger-lane constraints: GDB’s Rust expression parser supports only a subset of Rust, LLDB implements slightly less than GDB, GDB generally works better on Linux, and WinDbg/CDB depend on PDB-based debug info on Windows.
- Reviewed the Rust Reference for `#[debugger_visualizer]` and GDB pretty-printer autoload behavior: embedded GDB scripts are not auto-loaded by default and require safe-path / user-config help.
- Reviewed rustc-dev-guide test directives to confirm debugger testing remains explicitly lane-scoped by debugger family, version, OS, and compare mode.
- Reviewed LLDB internals to confirm that LLDB’s PDB reader default changed in version 22, strengthening the need for version-sensitive claim ceilings.
- Conclusion: P-0486 should be deepened around `session-scope.receipt`, `capability-witness.report`, and `claim-ceiling.report`, not widened into a debugger launcher or replay product.


## 2026-03-23 (404) — build-dir consumer transition now needs consumer-need truth and adapter-authority truth

Consulted sources:
- Call for Testing: Build Dir Layout v2 — many projects still rely on unspecified build-dir details because features are missing; users are asked to test builds, release processes, and anything else touching build-dir / target-dir under `-Zbuild-dir-new-layout`; and the post names concrete failure modes plus a version-windowed `CARGO_BIN_EXE_*` hint.
- Cargo 1.94 development-cycle notes — build-dir layout remains active work and Cargo itself moved tests toward runtime `CARGO_BIN_EXE_*` availability while continuing layout refinements.
- Cargo build-cache docs — final artifacts live in target-dir while intermediate artifacts are internal to Cargo and rustc and live in build-dir.
- Cargo build docs — `CARGO_BIN_EXE_<name>` is documented for integration-test binary lookup.
- Cargo external-tools docs — `--message-format=json` covers Cargo / rustc output but not arbitrary tool or proc-macro output.
- Cargo unstable docs — new-layout rehearsal and nightly artifact-dir style routes are explicit substrate, not timeless stable guarantees.
- Cargo build-dir-layout goal — the upstream motivation is easier caching / locking, not a public promise that internal paths are stable.

Main takeaway:
The missing value is no longer only “audit who scrapes Cargo internals.” It is a receiver-facing bundle that states **what the consumer really needed**, **what source class authorized the suggested adapter**, **which Cargo/layout windows actually hold**, and **how to hand around a rehearsal bundle without issue archaeology**.


## 2026-03-23 (406) — FFI callback authority / completion refresh

Consulted sources:
- Program management update — cross-language interop is an application area.
- Safety-critical Rust write-up — interop guidance/tooling for C/C++ boundaries is explicitly recommended.
- UniFFI object references — callback handles transfer ownership and use clone/free hooks via foreign-side handle maps.
- UniFFI async FFI docs — `complete_func` must be called exactly once; dropped-future cancellation hooks are optional; dropped callback may run after task completion.
- UniFFI foreign traits — unexpected callback errors can map via `From<UnexpectedUniFFICallbackError>`; otherwise generated code will panic.
- Diplomat intro/types — bindings are unidirectional and callback support in parameters is limited.
- CXX async docs — direct async FFI is not implemented; recommended path is an opaque-context + oneshot callback adapter.
- wit-bindgen docs — world imports/exports and generated traits/functions make directionality explicit.

Main takeaway:
The sharper missing crate contribution is a reviewable callback support-contract layer above bridge/generator substrate: callback authority receipts plus callback completion reports that keep directionality, native-vs-adapter status, exactly-once obligations, cancellation, and unexpected-error posture explicit.

## 2026-03-23 (407) — Cargo SBOM precursor support now needs capture-route truth and artifact-coverage honesty

Consulted sources:
- Rust in 2026 flagships — Cargo SBOM precursor stabilization remains an explicit secure-supply-chain milestone.
- Cargo unstable features docs — precursor files are generated only for executable and linkable outputs uplifted into target or artifact directories; `CARGO_SBOM_PATH` is a direct discovery hook; `--artifact-dir` copies promoted outputs into a predictable directory.
- Cargo external-tools docs — `compiler-artifact` messages expose filenames, executable paths, enabled features, and `fresh` status even when rustc was not run.
- Cargo changelog — `-Z sbom` remains active Cargo substrate rather than a hypothetical future.

Main takeaway:
The missing value is no longer only precursor ingestion and format emission. It is a receiver-facing bundle that states **how precursor evidence was captured, which outputs were actually eligible, and where imported trees or copied outputs stop stronger same-invocation claims**.

## 2026-03-23 (408) — workspace tool support now needs command-authority truth and fallback ceilings

Consulted sources:
- rustup 1.29 release — rustup now considers a `rust-analyzer` binary from `PATH` when the rustup-managed one is not found; empty env vars are treated as unset; `rustup check` now has distinct exit codes for update found vs none found.
- rustup book: overrides — toolchain selection order remains explicit (`+toolchain`, `RUSTUP_TOOLCHAIN`, directory override, toolchain file, default toolchain).
- rustup book: proxies — proxy-backed commands are a defined surface and include `cargo`, `rustc`, `rustdoc`, `rust-analyzer`, `cargo-clippy`, `cargo-miri`, and debugger wrappers.
- rustup book: components — optional components are installed per toolchain and may vary across toolchains/releases.
- Cargo external-tools docs — external `cargo-*` subcommands are resolved from PATH with `$CARGO_HOME/bin` precedence by default.
- cargo install / config docs — install roots and source selection remain explicit posture, not hidden implementation detail.

Main takeaway:
The missing value is no longer only “the workspace can sync tools.” It is a receiver-facing bundle that states **which command family actually answered the request, what component/toolchain surface was really available, and where PATH or cargo-home fallback stops stronger support claims**.


## 2026-03-23 (411) — compile-iteration framework-route refresh

Consulted sources:
- Rust challenges — compile performance remains the universal productivity tax; hot reloading and faster linking are explicitly named as high-leverage mitigations.
- Compiler performance survey 2025 results — incremental rebuilds after small changes remain an important workflow and build experience differs significantly across users and workflows.
- Dioxus hot-reload docs — Dioxus exposes three route families (RSX, assets, Rust hot-reloading); RSX can avoid recompiling the whole app for UI changes; multiple edit classes still require full rebuild or hotpatch.
- Dioxus RSX tutorial page — ordinary Rust edits trigger full rebuild under `dx serve` unless `--hotpatch` is used.
- Tauri CLI docs — `tauri dev` combines Rust-code hot-reloading with `build.devUrl` and `beforeDevCommand`, which usually starts a frontend dev server.
- Leptos styling docs — `trunk` and `cargo-leptos` can update edited CSS files immediately in the browser.

Main takeaway:
The sharper missing crate contribution for **P-0537** is not another framework-local dev loop.
It is a receiver-facing support bundle for **reload-surface class**, **restart ceilings**, and **latency-budget readiness classes** that can compare visual-only, logic-ready, and restarted-app feedback honestly.


## 2026-03-23 (412) — concurrency-contract refresh around cancellation classes and recovery posture

Consulted sources:
- Rust challenges — async complexity, fragmentation, and runtime lock-in remain live pain.
- 2025 State of Rust survey results — resource usage and debugging remain meaningful productivity limits.
- Tokio `Notify` docs — cancellation loses queue place; `notify_one` stores at most one permit.
- Tokio `watch::Receiver::changed` docs — cancellation does not mark a value seen.
- Tokio `mpsc::Receiver::recv` docs — cancellation does not receive a message.
- Tokio `RwLock` docs — `blocking_*` methods panic inside async execution contexts.
- std `Mutex` poisoning source/docs — poisoning is advisory and `PoisonError::into_inner` exists as an escape hatch.
- `parking_lot::Mutex` docs — no poisoning and eventual fairness are explicit claims.
- nightly `std::sync::nonpoison::Mutex` docs — non-poisoning is explicit but experimental.

Main takeaway:
The sharper missing crate contribution for **P-0538** is no longer just a fairness/reentrancy vocabulary.
It is a receiver-facing support bundle for **cancellation class**, **queue/value preservation truth**, **panic/recovery posture**, and **claim ceilings** above primitive-specific docs.


## 2026-03-23 (413) — crate-knowledge refresh around citation locators and citation capability

Consulted sources:
- 2025 State of Rust survey — online documentation remains the preferred canonical reference and LLM-like tooling appears in learning/support behavior.
- docs.rs about/builds — hosted README rules, `docsrs` cfg behavior, target-aware builds, and sandbox/resource limits remain explicit.
- docs.rs metadata — default-target, targets, additional-targets, and build knobs are explicit public substrate.
- docs.rs redirections — `latest`, semver ranges, and page-level redirects are intentional convenience routes.
- docs.rs rustdoc JSON — hosted JSON began on 2025-05-23, format-version matters, and rebuild redirects can point to absent targets until coverage catches up.
- docs.rs download — archive imports are useful but still carry static-root and invocation-specific asset caveats.
- Cargo rustdoc — target/example/bin selection remains explicit.
- Cargo metadata — consumers are still told to pin `--format-version` for compatibility.

Main takeaway:
The sharper missing crate contribution for **P-0536** is no longer only a provenance-aware machine-facing pack.
It is a receiver-facing support bundle for **citation locator resolution**, **target-aware pinning**, **citation-capability ceilings**, and **doctor checks that reject fake citation certainty**.


## 2026-03-23 (414) — crate-knowledge refresh around item witnesses and opaque-ID discipline

Consulted sources:
- Rust challenges — compile-time pain, ecosystem guidance needs, and async fragmentation reinforce the value of receiver-facing support contracts over more wrappers.
- 2025 State of Rust survey results — online documentation remains the preferred canonical reference while some support/learning flow appears to be moving toward LLM tooling.
- RFC 2963 rustdoc JSON — item IDs are opaque and only valid within a single JSON blob; HTML output is explicitly not stabilized for scraping.
- rustdoc unstable features — JSON output and doctest JSON are explicitly machine-facing substrate; merge flags and parts directories exist as unstable plumbing.
- docs.rs shorthand / metadata / builds / rustdoc JSON / download docs — docs.rs gives floating selectors, target-aware builds, rustdoc JSON download routes, README/default-target rules, and archive caveats.
- Cargo rustdoc / Cargo metadata — target and target-kind selection are explicit, and machine-readable output consumers are told to pin format versions.
- RFC 3662 mergeable rustdoc cross-crate info — `doc.parts` is unstable and incompatible across disparate rustdoc versions.

Main takeaway:
The missing value is no longer only “this pack can cite a page.” It is a receiver-facing bundle that states **what conceptual item a claim was tied to**, **what opaque-ID scope was observed**, **what witness basis justifies cross-version/target reuse**, and **where manual review still begins**.

## 2026-03-23 (417) — compile-iteration invalidation / barrier refresh

- Re-read **P-0537** and confirmed that the sharper missing layer is no longer just what reloaded or how fast it felt, but **what the edit actually touched** and **what barrier blocked the strongest fast path**.
- Refreshed evidence with the March 2026 Rust challenges post, the 2025 compiler-performance survey, the `Relink don’t Rebuild` goal, current Dioxus hot-reload docs, current `subsecond` docs, Tauri develop docs, the cargo-leptos README, and the Trunk README.
- Added `edit-scope.receipt` and `fast-path-barrier.report` schemas plus scenario families for dependency edits outside the tip crate, struct-layout changes that require reinstancing or restart, interface-preserving edits that still cascade rebuilds today, and portable bundles that keep invalidation truth separate from readiness truth.
- Reaffirmed that “the page changed instantly,” “the framework supports hot reload,” and “the linker got faster” must not masquerade as one honest compile-iteration verdict.

## 2026-03-23 (420) — crate-knowledge build-surface / conditioned-availability pass

- Re-opened the latest archive after the item-witness / citation-locator work and asked what still remained missing inside **P-0536**.
- Confirmed from current docs.rs docs that hosted documentation is recipe-shaped in several concrete ways: nightly toolchain, sandboxed builds, `cfg(docsrs)` scope limited to the final documented crate, configurable features/targets/default target, and cross-compilation for non-default targets.
- Confirmed from docs.rs rustdoc JSON docs that machine-facing consumers must inspect `format_version`.
- Confirmed from Cargo unstable docs and changelog that scrape-examples remains recipe-bound, target-level, and subject to dev-dependency caveats.
- Rechecked existing rustdoc-JSON-powered tools (`cargo-public-api`, `cargo-semver-checks`) and kept them as substrate/adjacent tooling, not as the missing support-contract crate.
- Conclusion: the sharper missing crate contribution for **P-0536** is a portable answer to **what recipe produced this visible surface** and **under what conditions the visibility claim is valid**.
- Added a new frontier note, a build-surface plan, two schemas, and five scenario bundles.
- Updated README, INDEX, prioritization, roadmap, decision log, LLM hygiene, and memory anchor so future passes do not rediscover this seam under vague labels like “better docs metadata”, “better cfg docs”, or “better feature visibility”.

## 2026-03-23 (426) — concurrency-contract refresh around delivery memory and backlog pressure

Consulted sources:
- Rust challenges — async complexity remains part of the current Rust pain picture.
- Rust forum wish list — community demand still explicitly names better documentation for forward progress guarantees and reentrancy.
- Tokio `Notify` docs — `notify_one` stores at most one permit; `notify_waiters` stores no future permit.
- Tokio `watch` docs — only the latest value is retained; `changed()` marks the new value seen on completion.
- Tokio `broadcast` docs — bounded retained history can lag, skip messages, and report lag counts.
- Tokio bounded `mpsc` docs — buffered FIFO with sender backpressure and single receiver.
- `async-channel` docs — bounded and unbounded MPMC single-delivery channels with remaining messages receivable after close.
- `crossbeam-channel` bounded docs — zero-capacity channels are explicit rendezvous channels.

Main takeaway:
The sharper missing crate contribution for **P-0538** is no longer only cancellation/fairness/context vocabulary.
It is a receiver-facing support bundle for **delivery-memory class**, **backlog-pressure posture**, **lag/loss signal visibility**, and **claim ceilings** above channel-specific docs.


## 2026-03-23 (428) — concurrency-contract refresh around delivery acceptance and observation evidence

Consulted sources:
- Rust challenges — async complexity remains part of the current Rust pain picture.
- Tokio `mpsc::Sender::send` docs — `Ok` does not guarantee the data will be received.
- Tokio `broadcast::Sender::send` and `receiver_count` docs — success requires an active receiver, while receiver counts are not guaranteed delivery receipts.
- Tokio `watch::Sender::send` docs — successful send updates shared latest state; failed send returns the value and seeds no future receivers.
- Tokio `oneshot` module and `Sender::poll_closed` docs — sent value can remain in the channel while sender-visible follow-up is closure-oriented rather than processing proof.
- Tokio `Notify` docs — notify paths carry no data and only change wake eligibility.
- Flume `Sender` docs — success requires live receivers, but still is not proof of downstream handling.

Main takeaway:
The sharper missing crate contribution for **P-0538** is no longer only cancellation / context / memory / audience vocabulary.
It is a receiver-facing support bundle for **what producer-visible success certifies**, **what it definitely does not prove**, **what later signals count only as hints**, and **when application-level acknowledgment is still required**.


## 2026-03-23 (430) — concurrency-contract refresh around closure finality and post-close availability

Consulted sources:
- Rust challenges — async complexity remains part of the current Rust pain picture.
- Tokio `mpsc` docs — clean shutdown is close plus drain; buffered items and outstanding permits may still produce values after close.
- Tokio `broadcast` docs — closure begins when all senders drop, but retained values remain receivable until exhausted.
- Tokio `watch` docs — `changed` error posture depends on closed + seen state, and `Sender::subscribe` can reopen a closed interval.
- Tokio `oneshot` docs — close blocks future sends without proving the slot is empty; `try_recv` may still recover a value sent before close completed.
- `async-channel` docs — closed channels reject future sends while still allowing remaining messages to be received.
- `std::sync::mpsc::Receiver` docs — buffered messages sent before disconnect can still be properly received.

Main takeaway:
The sharper missing crate contribution for **P-0538** is no longer only cancellation / memory / audience / acceptance / order vocabulary.
It is a receiver-facing support bundle for **what closure actually finalizes**, **what remains observable afterward**, **whether closed is terminal or reopenable**, and **when draining or probing is still required after close**.

## 2026-03-25 (457) — promise-bundle / support-envelope refresh across broad domain activity

Consulted sources:
- 2025 State of Rust survey — broad productivity pain remains visible and documentation still matters as canonical support substrate.
- Rust challenges — crate choice remains hard, some industries remain immature, and embedded / safety-critical pains remain materially different from the median.
- Rust debugging survey 2026 — debugger quality varies across debuggers, operating systems, versions, and async situations.
- crates.io development update — stronger Trusted Publishing controls, SLOC, and `pubtime` sharpen trust and lifecycle surfaces.
- docs.rs builds / metadata / rustdoc JSON / download docs — hosted docs have recipe-shaped truth, configurable targets/features, JSON format-version caveats, and archive caveats.
- 2026 goals overview — annual goals and 66-goal slate reinforce the size and motion of current substrate work.
- Cargo build analysis / build-dir rework / semver checks / public-private dependencies / verifiable mirroring / StableMIR / open namespaces / Rust-for-Linux goals — together reinforce tool-building substrate, support-boundary work, and distribution/trust seams.
- AreWeWebYet / AreWeGuiYet / AreWeGameYet / AreWeIDEYet / GeoRust / Automerge — broad domain ecosystems are active enough that the missing value is often cross-cutting and receiver-facing rather than “one more umbrella framework”.

Main takeaway:
The sharper missing crate contribution is not another broad fantasy.
It is a **promise bundle**: a compact support envelope another team can review, rerun, and hand off.
That keeps the control-plane frontier in front while making the archive more explicit about what a worthy crate actually provides other people.

## 2026-03-25 (461) — evidence-interchange / profile-contract refresh

Consulted sources:
- 2025 State of Rust survey — resource usage and debugging remain notable pain points, and official online docs remain the preferred canonical reference.
- Rust debugging survey 2026 — debugger quality varies across debuggers, operating systems, versions, and async situations.
- crates.io development update — Security tab, Trusted Publishing enhancements, and other trust/publication surfaces make more ecosystem truth machine-visible.
- docs.rs rustdoc JSON / builds / metadata / download docs — docs.rs exposes structured rustdoc JSON, configurable build metadata, downloadable archives, and hosted-build caveats that are useful but need explicit compatibility handling.
- rustc target tier policy — official support already comes in bounded tiers rather than one binary status.
- cargo-semver-checks / libtest JSON / verification and mirroring / open namespaces / build-std / Rust-for-Linux / cargo build-analysis / public-private dependencies / StableMIR / 2026 goals overview — together reinforce that Rust is adding more stable or semi-stable tool-facing surfaces, clearer API boundaries, more build/report substrate, and more long-lived tooling expectations.

Main takeaway:
The sharper missing crate contribution is not another report generator.
It is a **portable evidence-interchange contract**:
a reviewed bundle, raw receipts, named profiles, a verifier, and a schema/version policy that other tools can actually reuse.
That keeps the control-plane frontier in front while making “what should the crate provide other people?” more concrete again.


## 2026-03-25 (462) — policy-pack / explainable-verdict refresh

Consulted sources:
- 2025 State of Rust survey — reinforces crate-choice/resource/debugging pain and the continued centrality of official docs.
- crates.io January 2026 update — Security tab, Trusted Publishing Only mode, blocked risky triggers, SLOC, and `pubtime` all strengthen machine-usable decision inputs.
- rustc target tier policy — support already comes in bounded levels rather than one binary claim.
- cargo-semver-checks goal — shows a real official appetite for policy-like gating in `cargo publish`, while still preserving an override path.
- cargo build-analysis goal — useful new substrate, but explicitly prototype-grade and not itself a policy-stable interface.
- StableMIR goal — reinforces that semver-stable tool-facing interfaces are becoming a real design target in Rust.
- public/private dependencies and verification/mirroring goals — reinforce boundary and trust signals that should feed policy reruns.

Main takeaway:
The sharper missing crate contribution is not just more evidence.
It is an **explainable decision packet**: reusable policy packs, rule outcomes, override objects, and recheck triggers that another team can defend later.
