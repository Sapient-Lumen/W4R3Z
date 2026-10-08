
## Addendum (rev0459)
For questions about how already-worthy candidates compare **after** they pass the selection rubric, read `design/epic-contribution-scorecards-2026Q1.md` next.

Interpretation rule:
- this note still answers whether a candidate deserves serious consideration at all;
- the new note answers how the strongest current candidates differ by priority type once they are all already “in”.

## Addendum (rev0427)
For questions about **how to judge a candidate after it has passed initial selection and is now being proven in the world**, read `design/portfolio-pilot-evaluation-2026Q1.md` and `meta/PILOT_SCORECARD_PROTOCOL.md` after this note.

Interpretation rule:
- this note still owns **proposal selection**;
- the new note owns **pilot proof and exit criteria**;
- and a candidate should not be considered truly strengthened just because builders produced a good-looking prototype without scorecard evidence for lane value, artifact honesty, downstream decision value, and stewardability.


## Addendum (rev0426)
For questions about **how to judge, rank, deepen, fold, delay, or kill candidate contributions** before they mutate the canon, read this note right after `design/worthy-contribution-shortlist-2026Q1.md` and `design/portfolio-execution-sequencing-2026Q1.md`.

Interpretation rule:
- this note does **not** change the broad ladder;
- it does **not** promote a new frontier;
- it exists to answer the missing governance question: **what makes a proposal worthy enough to promote, deep enough to keep, or weak enough to fold or kill?**
- keep **Build-State Evidence** as the strongest one-project answer overall;
- keep the strongest multi-project answer as **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- keep **Adoption Navigation** and **Native Edge** as later consumer/frontier widenings rather than the default generic first build steps;
- and require every new proposal to declare its ranking class, substrate imports, steward story, artifact family, and explicit fold/kill triggers.

# Design: Portfolio selection rubric (2026 Q1)

## Goal
The archive now has rankings, execution blueprints, shared grammar, and a default build sequence.
What it still lacked was a canonical answer to another practical question:

> when a new Rust-ecosystem idea appears, how should the archive decide whether to promote it, deepen it, fold it into an existing seam, delay it, or kill it outright?

This note exists to make the repo more **decision-capable**.
It is the archive's answer to **proposal triage, promotion discipline, and anti-empire hygiene**.

Read with:
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `meta/CANDIDATE_TRIAGE_PROTOCOL.md`

## Why this note is needed now
The repo has become good at naming strong seams.
That creates a new risk: once a canon gets sharper, it can start admitting attractive-but-thin ideas simply because they sound adjacent.
The current official Rust signals make that risk more important, not less:

- Rust's March 2026 challenges writeup says the recurring problems are not random; they cluster around **compile/resource pain**, **choice paralysis / tacit knowledge**, async complexity, and domain-specific maturity gaps. That argues for judging proposals by whether they hit recurring pain rather than novelty alone.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says the broad challenge picture is fairly stable, docs remain canonical, and editor/LLM-mediated learning is rising. That argues for preferring proposals that can emit reviewable artifacts and import canonical truth, not ideas that rely on vibes or screenshot-level curation.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The Rust goals process says goals work best when a contributor is ready to do the work and a Rust team can champion it. That argues for judging proposals partly by **champion / steward realism**, not just by conceptual appeal.
  https://rust-lang.github.io/rust-project-goals/2026/
- The 2026 flagships explicitly bundle **Building blocks**, **Secure your supply chain**, and roadmap/application-area work like **cross-language interop**. That argues for preferring seams that compose with current upstream motion and can start as bounded companion layers.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo's accepted plumbing and build-analysis work keeps moving toward machine-usable phases, structured evidence, and schema-bearing companion tooling rather than one universal porcelain. That argues for preferring proposals with a thin contract boundary and artifact family over “one more mega-tool”.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- docs.rs rustdoc JSON, `cargo-semver-checks` blocker work, `public/private dependencies`, and `rustc_public` / StableMIR all reinforce that the ecosystem is getting stronger when tools can import **bounded machine-usable truth**.
  https://docs.rs/about/rustdoc-json
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
  https://rust-lang.github.io/rust-project-goals/2025h2/pub-priv.html
  https://doc.rust-lang.org/nightly/nightly-rustc/rustc_public/index.html
- crates.io's trusted-publishing/security improvements and the March 2026 Cargo extraction advisory show that operational urgency is real, but they also show why urgency alone is not a complete ranking method: some seams are urgent, others are broader, and the archive should say which is which.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- The January 2026 maintenance writeup says maintenance has a multiplicative effect, and the Rust Foundation strategy pairs stable infrastructure, sustainable maintenance, and adoption growth. That argues for making **stewardship fit** a first-class gate in proposal selection.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
  https://rustfoundation.org/strategic-plan/

Taken together, those signals say the archive needed a note for **selection discipline**.

## Headline answer
A worthy Rust ecosystem contribution is not merely:
- technically interesting,
- emotionally urgent,
- or plausible as a startup/product pitch.

A worthy contribution should score well on **recurring pain**, **substrate readiness**, **contract clarity**, **artifact honesty**, **thin-ship ability**, **reuse / multiplier value**, and **steward realism**.

In archive terms, the strongest candidates are those that:
1. solve a recurring pain that official Rust signals already recognize;
2. have a narrow enough seam that adjacent layers stay explicit;
3. can emit reviewable machine-usable artifacts;
4. can ship as a thin companion layer before upstream perfection;
5. improve multiple consumers or a strategically real frontier;
6. have a believable steward / refresh / fixture story;
7. and come with explicit anti-goals and fold/kill triggers.

That is why **Build-State Evidence** still wins broadly, why **Semantic Context** still wins as multiplier, why **Package Intake** is urgent without becoming the broad #1, and why **Native Edge** remains specialist instead of generic first build.

## The seven-axis rubric
Do **not** reduce this to fake precision.
Use the axes to compare candidates honestly and to force explicit tradeoffs.

### 1) Recurring pain / breadth
Questions:
- Does the proposal reduce a pain that keeps appearing in official Rust signals?
- Is the pain broad across many users, or narrow and sponsor-specific?
- Does the idea attack a real tax rather than a nice-to-have convenience?

Good signs:
- repeated survey or official-goals mention;
- broad user classes benefit;
- failure is expensive in real time, money, or trust.

Typical winners:
- build-state, release-boundary, package-ingress, navigation/tacit-knowledge work.

### 2) Substrate readiness / official pull
Questions:
- Is upstream Rust/Cargo/docs.rs/crates.io already exposing surfaces that make this buildable now?
- Does the proposal align with accepted goals, current flagships, or clearly moving machine-facing APIs?
- Can it start outside the compiler/Cargo core without waiting for a grand merge?

Good signs:
- accepted goal or active official experiment;
- importable official output rather than reverse-engineered logs;
- bounded upstream dependencies.

Typical winners:
- build-state, semantic context, migration/public API, package intake.

### 3) Seam clarity / anti-flattening
Questions:
- Can the contribution name its exact boundary and its adjacent imported layers?
- Does it preserve seam-specific truth instead of swallowing five neighboring problems?
- Would two different teams describe the same seam similarly after reading the note?

Good signs:
- exact layer names;
- imported truths and downstream conclusions stay separate;
- obvious anti-goals.

Typical losers:
- “Rust platform” empires;
- dashboard/score ideas that hide missing lower-layer evidence;
- assistant wrappers that silently impersonate canonical truth.

### 4) Artifact honesty / reviewability
Questions:
- Can the idea emit a portable artifact family, not just prose, screenshots, or hosted UI state?
- Can a human or tool inspect freshness, partiality, and authority?
- Can the artifact survive handoff into CI, docs, support, review, or assistant consumers?

Good signs:
- canonical pack + brief/receipt split;
- explicit imported-versus-derived truth;
- diffable and lintable outputs.

Typical winners:
- evidence layers and bounded review layers.

### 5) Thin-shippable v0
Questions:
- Could a serious team ship a useful v0 as a companion layer without owning all of Cargo or the compiler?
- Is there a viable narrow first lane or pilot?
- Does the v0 still help even if upstream never fully absorbs it?

Good signs:
- one artifact family;
- one or two strong pilot lanes;
- useful locally before hosted/network effects.

Typical losers:
- proposals that require total ecosystem blessing before producing value.

### 6) Reuse / multiplier value
Questions:
- Does the proposal improve several later consumers or adjacent seams?
- If it is specialist, does it at least unlock an adoption frontier with real industrial weight?
- Could later surfaces import it rather than re-inventing their own facts?

Good signs:
- multiple downstream consumers;
- clear import relationship from higher layers;
- narrow seam but high composability.

Typical winners:
- Build-State Evidence, Semantic Context, Migration/Public API.

### 7) Stewardship / refresh realism
Questions:
- Is there a believable maintainer or champion story?
- Can fixtures, validators, and canonical examples be refreshed without heroic archaeology?
- Is the upkeep proportional to the leverage?

Good signs:
- bounded compatibility promise;
- refresh sources are official or maintainer-authored;
- steward model is named.

Typical losers:
- curation empires with no clear refresh path;
- broad blessed-list ambitions with permanent review burden.

## Decision outcomes
After scoring a candidate qualitatively across the seven axes, the archive should choose one of five outcomes.

### Promote
Use when:
- the candidate is both strategically strong and seam-clear;
- it improves the broad ladder or the active specialist frontier;
- and it clearly beats its adjacent alternatives.

Promotion requires:
- explicit ranking-class statement;
- explicit read-first set;
- anti-goals;
- and synced updates to canon + meta routing.

### Deepen
Use when:
- the seam is already right,
- but the repo still lacks execution detail, artifact families, pilot lanes, or practical gates.

Deepening is now the default move for mature strong seams.
That is why recent revisions mostly added blueprints and portfolio notes instead of re-promoting the ladder every time.

### Fold
Use when:
- the attractive idea is real, but it is better understood as a consumer or lower layer of an existing seam.

Examples:
- another crate-score or starter-site idea should usually fold into **Adoption Navigation**;
- another semver/docs helper should often fold into **Semantic Context** or **Migration/Public API**;
- another install/security wrapper may belong under **Package Intake** or **consumer install**, not as a fresh frontier.

### Delay
Use when:
- the pain is real,
- but substrate or steward reality is not ready enough to justify promotion.

Delay is not dismissal.
It means the archive should keep a watch note, imports, or adjacent lane map without pretending the seam is ready for a top-band push.

### Kill
Use when:
- the proposal has no clear artifact family,
- no steward story,
- no separable seam,
- or it mostly rebrands an existing layer with more rhetoric and less honesty.

“Kill” here means: do not promote, do not build a new top-level canon note, and do not let the idea quietly metastasize through summary language.

## Must-pass gates before a new proposal enters the top band
Before promoting a new worthy-contribution candidate, require all of these:

1. **Ranking-class declaration**
   Say whether the candidate is trying to become:
   - one-project winner,
   - multi-project portfolio component,
   - active specialist frontier,
   - operational seam,
   - or hidden multiplier.

2. **Seam sentence**
   One sentence that names the boundary and the adjacent imported layers.

3. **Artifact-family sentence**
   One sentence that says what canonical pack/report/receipt family the v0 would emit.

4. **Pilot lane**
   At least one concrete v0 lane or workflow where the contribution proves itself.

5. **Steward story**
   Name the compatible steward shape: maintainer team, funder-backed lab, working group, or clearly bounded external tool owner.

6. **Fold/kill triggers**
   State what evidence would cause the candidate to be folded into another seam, delayed, or killed.

If those six gates are not met, do **not** promote the idea no matter how fashionable it sounds.

## Penalties and disqualifiers
Apply heavy penalties when a candidate:
- depends on hidden curation or a permanent blessing committee;
- needs Cargo/compiler absorption before it is useful at all;
- cannot say what is imported versus derived;
- smears multiple seams into a fake platform answer;
- only emits screenshots, scores, or prose summaries;
- or tries to become an assistant-only truth layer.

Immediate kill indicators:
- “another dashboard” with no new canonical evidence;
- “another universal index” with no bounded seam ownership;
- “another better recommendations site” without renewal receipts;
- “another build speed platform” that cannot explain observed facts;
- “another release assistant” that cannot name what proofs it imports.

## How the current leading candidates score
### Build-State Evidence
Why it still wins broadly:
- strongest recurring pain coverage;
- strong upstream substrate via Cargo build analysis and build-dir work;
- very clear artifactability;
- thin-shippable companion-layer v0;
- and broad downstream reuse.

Main weakness:
- stewardship/compatibility discipline must stay strong or it can drift into cache/dashboard empire behavior.

### Semantic Context
Why it remains the key multiplier:
- high reuse across semver, docs, CI, edit, and assistant consumers;
- rising upstream substrate via docs.rs rustdoc JSON, semver-checks work, and compiler-facing publication work;
- clear payoff once evidence lanes stay honest.

Main weakness:
- easier than Build-State to over-expand into a universal index or assistant platform if not bounded.

### Migration/Public API
Why it remains a strong bridge rather than the broad winner:
- strong leverage on release/upgrade correctness;
- now has meaningful official pull from public/private dependencies and semver-checks work;
- improves one important quadrant sharply.

Main weakness:
- narrower breadth than Build-State and depends heavily on prior semantic evidence.

### Package Intake Gateway
Why it remains the operational seam:
- urgency is now very real;
- route/payload/staging/resolution/handoff are clear and artifactable;
- security and trust surfaces are moving upstream.

Main weakness:
- high urgency does not automatically make it the broadest first build.

### Adoption Navigation
Why it remains the anti-tacit-knowledge answer:
- solves a highly visible and growing pain;
- benefits from better registry/docs signals;
- can sharply improve first-route decisions.

Main weakness:
- recommendation layers are maintenance-expensive and should not outrun the evidence spine.

### Native Edge
Why it remains specialist rather than generic first place:
- strategically real frontier with industrial weight;
- official roadmap support via cross-language interop;
- clear missing seam around boundary/provider/context/handoff truth.

Main weakness:
- narrower broad-user leverage than Build-State, and often sponsor-specific.

## The archive consequence
The repo should now default to this meta-answer:

> The next revision should usually **deepen** or **fold** before it **promotes**.

That is not timidity.
It is how the archive avoids inventing a new empire every time Rust gets a new tool, advisory, or excitement spike.

## Proposal-card minimum for future revisions
Any future candidate worthy-contribution note should carry, at minimum:
- ranking class;
- seam sentence;
- artifact-family sentence;
- pilot lane;
- imports / authority sources;
- steward story;
- anti-goals;
- fold trigger;
- kill trigger.

That minimum is intentionally small enough for LLMs and humans to follow, but strong enough to stop the archive from admitting vague “big ideas” with no theory of practice.

## Practical recommendation for this archive
Use this note whenever the repo is tempted to:
- invent another frontier because a source is fresh;
- flatten a hidden multiplier into a new top-band answer;
- let a recommendation or assistant surface outrun its evidence spine;
- or keep weak candidates alive merely because they sound strategic.

When in doubt:
- prefer **deepen** over **promote**,
- prefer **fold** over proliferate,
- and prefer **kill** over keeping a vague zombie note alive.
