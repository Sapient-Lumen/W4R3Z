## 2026Q1 frontier note
This bundle is now explicitly promoted as the archive's **Adoption Navigation Contract** frontier.

New default rule:
- use this file to define the bundle members, artifact family, and MVP boundary;
- use `design/adoption-navigation-contract-2026Q1.md` to define the sharper frontier claim and what layers must stay separate;
- keep **question**, **candidate lanes**, **canonical references**, **imported evidence**, **local fit**, and **brief/handoff** visibly distinct;
- keep **Reviewable Lane Defaults + renewal receipts** as the execution seam beneath this bundle rather than widening recommendation prose by volume.

# Design: Adoption Navigation Bundle

## Thesis
Rust ecosystem guidance is now too important to stay smeared across crates.io searches, docs.rs pages, README prose, unofficial curated lists, internal platform docs, conference talks, and assistant prompts.

The missing contribution is not one globally blessed crate list.
It is a thin portable bundle that keeps six truths separate:
- **question** — what project is being decided, with which constraints, risk posture, time horizon, and non-goals;
- **candidate lanes** — which respectable stack lanes are actually under consideration;
- **canonical references** — which maintainer-authored docs, guides, examples, and support surfaces count as the first reading set;
- **imported evidence** — which trust, maintenance, interop, compatibility, and freshness inputs shaped the recommendation;
- **local fit** — what happened when the candidate lane met one real workspace, proof-of-concept, or semantic-context check;
- **brief / handoff** — what a human reviewer, internal platform team, CI gate, or assistant may safely conclude next.

## Why this bundle now matters
Fresh official signals are unusually aligned:
- Rust’s March 20, 2026 challenges post explicitly names **choice paralysis** and **tacit knowledge** in ecosystem navigation, says maturity varies a lot by domain, and says the problem is not a lack of libraries so much as the expertise needed to choose among them.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says online documentation remains the preferred canonical reference, while learning and editor behavior are increasingly shaped by machine-mediated workflows.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust’s December 2025 vision work explicitly says users need help getting oriented in crates.io, says there is no clear place to get advice on a good starter set of crates, and recommends better supportive interfaces and guidance from crates.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- docs.rs changed its default targets in October 2025 to better reflect current platform reality, which is a reminder that support expectations drift and should be imported with freshness instead of copied into static recommendation prose.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- crates.io’s January 2026 development update added stronger Trusted Publishing controls, SLOC display, and `pubtime` in the index, which means the ecosystem now exposes materially better recommendation inputs than it used to.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- the Rust Foundation’s 2026–2028 strategy explicitly pairs stable infrastructure, sustainable maintenance, and adoption growth; recommendation infrastructure now sits inside core Rust ecosystem strategy rather than outside it.
  https://rustfoundation.org/strategic-plan/
- Rust’s 2026 maintenance writeup says maintenance is ongoing, invisible, and not reducible to one release event, which means any serious recommendation layer must import maintenance reality instead of treating popularity as a proxy.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/

Together these signals say the next worthy move is not another general essay about crate choice.
It is an **adoption navigation bundle** that can travel between humans and tools without pretending there is one universal Rust starter stack.

## Bundle members
Treat this as a deliberate bundle composed from existing lower layers:
- **Ecosystem Atlas Kit** owns domains, lanes, slot maps, curator provenance, and freshness budgets.
- **Reviewable Lane Defaults** owns reusable scoped defaults for recurring project classes.
- **Adoption Decision Stack** owns project-scoped recommendation composition.
- **Canonical Learning Stack** owns maintainer-authored canonical references and derived consumer overlays.
- **Trust Decision Stack** owns imported trust and policy evidence.
- **Maintenance Reality Stack** owns stewardship, succession, and operational strain posture.
- **Semantic Context Kit** owns real workspace-local fit checks.
- **Interop Commons Kit** owns shared seams that should be referenced rather than silently assumed.
- **Adoption Navigation Bundle** owns the composition boundary above them.

## Core artifact family

### 1. `adoption-question/v0`
A compact statement of the decision surface:
- project/workspace identity
- operating context
- required constraints and explicit non-goals
- risk posture and time horizon
- team maturity and support expectations

### 2. `candidate-lane-set/v0`
The respectable answer space:
- imported atlas domain and lane refs
- shortlist of serious candidate lanes
- conservative default versus more opinionated alternatives
- slot maps / commons seams that materially matter here
- invalidated lanes and why

### 3. `canonical-reference-set/v0`
The maintainer-authored reading surface:
- canonical docs / guides / examples for each candidate lane
- support-level and docs-host posture
- warnings about partial, target-specific, or stale references
- derived-versus-canonical markers

### 4. `adoption-evidence-report/v0`
Imported decision inputs:
- trust / admission / lifecycle inputs
- maintenance / stewardship posture
- docs / guide / compile-guidance posture
- compatibility / support-envelope / platform notes when relevant
- freshness timestamp and unresolved evidence gaps

### 5. `local-fit-check/v0`
What happened when a candidate met real code:
- workspace or prototype subject
- semantic-context observations
- obvious migration burden or slot mismatch
- unsupported assumptions or hidden glue revealed locally
- checks run and checks skipped

### 6. `adoption-brief/v0`
The bounded recommendation surface:
- recommended lane
- why it is the default here
- visible caveats and unanswered questions
- freshness status
- review owner / next renewal point

### 7. `adoption-alternative-set/v0`
Respectable alternatives stay first-class:
- alternatives worth serious consideration
- what they improve
- why they are not default here
- switch cost / migration cost

### 8. `adoption-handoff/v0`
A bounded consumer-facing summary for:
- `human-review`
- `platform-team`
- `ci-policy`
- `assistant`

The `assistant` lane must stay freshness-aware and explicitly derived.

### 9. `adoption-diff-report/v0`
Difference between two recommendation moments:
- question drift
- lane-set drift
- evidence drift
- canonical-reference drift
- recommendation drift
- consequence summary

### 10. `adoption-navigation-pack/v0`
Attachable bundle linking:
- `adoption-question/v0`
- `candidate-lane-set/v0`
- `canonical-reference-set/v0`
- `adoption-evidence-report/v0`
- optional `local-fit-check/v0`
- `adoption-brief/v0`
- `adoption-alternative-set/v0`
- optional handoffs and diff reports

## Reference UX
A reference implementation could expose:
- `cargo adopt question` — emit `adoption-question/v0`
- `cargo adopt lanes` — emit `candidate-lane-set/v0`
- `cargo adopt canon` — emit `canonical-reference-set/v0`
- `cargo adopt evidence` — emit `adoption-evidence-report/v0`
- `cargo adopt local-fit` — emit `local-fit-check/v0`
- `cargo adopt brief` — emit `adoption-brief/v0`
- `cargo adopt diff` — emit `adoption-diff-report/v0`
- `cargo adopt pack` — bundle `adoption-navigation-pack/v0`

## Theory of change
The critical design move is to keep these truths separate:
- **what this project is asking**,
- **which lanes are actually respectable options**,
- **which maintainer-authored references should be read first**,
- **which imported evidence shaped the call**,
- **what local-fit checks revealed**,
- and **what the final brief is allowed to claim**.

That separation matters because current Rust practice often collapses them into one fake story:
- a crates.io search result or popularity signal becomes “the recommendation”;
- one blog post or template repo becomes “the canonical docs”;
- one internal approved-stack page becomes “the evidence” even after the underlying ecosystem moved;
- one successful prototype becomes “proof the lane fits”;
- or one assistant summary becomes “the actual decision record”.

If those truths stay flattened together, the ecosystem will keep producing prestige-driven private curation instead of one boring portable recommendation vocabulary.

## Shared stack role
This bundle should be treated as the archive’s **ecosystem navigation composition point**.
It is:
- above **Ecosystem Atlas**, **Adoption Decision**, **Canonical Learning**, **Trust Decision**, **Maintenance Reality**, and **Semantic Context**;
- beside **Package Admission** and **Compatibility Claims**;
- upstream of onboarding, starter-template, internal-platform, and assistant consumers.

## Adjacent boundaries
- **Ecosystem Atlas Kit** still owns domain/lane/slot/curator/freshness structure.
- **Reviewable Lane Defaults** still owns reusable project-class defaults.
- **Adoption Decision Stack** still owns the recommendation-composition logic.
- **Canonical Learning Stack** still owns maintainer-authored canon and derived consumer overlays.
- **Trust Decision Stack** still owns imported trust and policy evidence.
- **Maintenance Reality Stack** still owns stewardship and succession posture.
- **Semantic Context Kit** still owns repository-local grounding.
- **Interop Commons Kit** still owns shared seams, not recommendation prose.

## MVP boundary
A worthy first implementation should prove exactly six things:
1. export one explicit project question with constraints and non-goals;
2. import one atlas-backed candidate lane set from one domain;
3. import one canonical reference set instead of writing freehand starter prose;
4. attach one evidence report with freshness-visible trust, maintenance, and docs inputs;
5. record one local-fit check against a real workspace or bounded prototype;
6. emit one bounded recommendation brief with serious alternatives still visible.

Optional extension: import one reusable scoped default when the project question matches a maintained project class.

That is enough to validate the bundle without becoming a global ranking engine.

## Non-goals
Do **not** turn this into:
- one globally blessed crate list,
- one assistant-first recommender pretending to be canon,
- one hidden score for crate quality,
- a crates.io replacement,
- a giant documentation portal,
- or a policy engine that silently replaces trust / maintenance / support evidence.

Also avoid flattening:
- candidate lanes into a single winner,
- canonical references into generic commentary,
- maintenance reality into popularity,
- local-fit checks into universal truths,
- assistant output into the source of record.

## Success criteria
- humans can reconstruct why a Rust stack recommendation was made from one portable bundle;
- candidate lanes, canonical references, evidence, local fit, and final brief remain visibly distinct;
- freshness drift becomes auditable instead of anecdotal;
- internal platform teams and assistants can import the same bundle without becoming hidden authorities;
- the ecosystem gets one explainable recommendation seam instead of more private spreadsheets, lore, and prompt cargo cults.
