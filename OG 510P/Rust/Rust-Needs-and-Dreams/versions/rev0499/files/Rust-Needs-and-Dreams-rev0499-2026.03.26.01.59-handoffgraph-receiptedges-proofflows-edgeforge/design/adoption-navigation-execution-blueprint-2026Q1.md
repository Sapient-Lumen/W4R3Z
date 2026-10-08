# Design: Adoption Navigation execution blueprint (2026 Q1)

## Goal
Turn the archive's strongest **anti-tacit-knowledge** answer into a sharper **buildable program**.

The missing contribution is not another “best crates” site, another search-ranking experiment, another assistant-only oracle, or another ecosystem score empire.
It is a disciplined recommendation layer that lets Rust teams carry **portable adoption-decision truth** across stack choice, starter-set guidance, local-fit checks, renewal, and bounded downstream handoffs.

Read this note when the question is narrower than the broad ladder:

> if a serious Rust team wants to build the archive's current answer to Rust's choice-paralysis and tacit-knowledge problem, what should that contribution actually ship in theory and practice?

Read with:
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `design/adoption-navigation-contract-2026Q1.md`
- `design/reviewable-lane-defaults.md`
- `design/lane-default-renewal-receipts.md`
- `design/ecosystem-atlas-kit.md`

## Why this note is needed now
The archive already knew that **Adoption Navigation Contract** was strategically strong.
What it still lacked was a crisper answer to **what the contribution should actually look like**.

Fresh official signals sharpen that answer:
- Rust's March 2026 challenges writeup says the ecosystem problem is often **choice paralysis** and **tacit knowledge**, not simple absence of crates, and explicitly recommends investing in ecosystem guidance and compatibility.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says online docs remain the preferred canonical reference while editor / LLM-mediated learning is rising.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust's December 2025 vision work says people need help navigating crates.io, says there is no clear place to get advice on a good “starter set” of crates, and says the obvious “just bless crates” answer is politically risky.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- Cargo's FAQ still frames one of the core benefits of a central registry as **discoverability** and ecosystem-wide information, which means the substrate for guidance exists even if the review layer is still weak.
  https://doc.rust-lang.org/cargo/faq.html
- crates.io's January 2026 update added a Security tab, Trusted Publishing-only mode, SLOC, and `pubtime`, which means recommendation inputs are materially better than they were a year ago.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- docs.rs changed its default targets in October 2025 to better reflect platform reality, which is a reminder that recommendation inputs drift and must stay freshness-visible.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- The January 2026 maintenance writeup says maintenance includes issue triage, bugs, CI failures, security incidents, performance regressions, dependency updates, and documentation upkeep, and calls that work multiplicative. Recommendation systems that ignore maintenance reality are therefore structurally wrong.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- The Rust Foundation's 2026–2028 strategy explicitly couples **stable infrastructure**, **sustainable maintenance**, and **adoption & innovation**, which makes recommendation infrastructure strategically central rather than decorative.
  https://rustfoundation.org/strategic-plan/

Taken together, those signals say the archive should stop describing the winner only as a theme.
It should describe a real contribution shape.

## Headline answer
If one serious team wants to build the archive's strongest answer to Rust's recommendation and starter-set problem, the answer should now be:

> Build an **Adoption Navigation reference layer** that imports lane maps, canonical references, maintenance/trust evidence, and local-fit checks; preserves decision, evidence, and handoff truth as separate layers; and emits renewable briefs and packs for humans, CI, platform teams, and assistants.

That answer is deliberately narrower than “solve discoverability”.
It is also deliberately stronger than “show recommended crates”.

## What this contribution should be in theory

### Core thesis
An adoption-navigation system becomes ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what exact question and project class are under review;**
2. **what respectable lanes were considered and why they were in scope;**
3. **what canonical maintainer-authored references count as first reading;**
4. **what imported evidence shaped the recommendation;**
5. **what local-fit grounding was actually run;**
6. **what downstream consumers may honestly conclude, and until when.**

If a project cannot answer those questions without chat history, private memory, issue searches, and vibes, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable project-scoped recommendation review**.

It should include:
- explicit question capture;
- candidate-lane and alternative truth;
- canonical-reference capture;
- imported trust / maintenance / support / freshness evidence;
- bounded local-fit grounding;
- consumer-specific briefs and handoffs.

It should not become:
- crates.io itself;
- a universal search engine;
- a hidden numeric quality-score service;
- or the new official Rust canon.

### Separation rule
The contribution must preserve at least six distinct truth classes:
- **question truth** — what is being decided, for whom, under what constraints, risk posture, and time horizon;
- **candidate-lane truth** — which respectable answer space was in scope and which lanes were rejected or demoted;
- **canonical-reference truth** — what maintainer-authored docs, guides, examples, and support notes count as first reading;
- **imported-evidence truth** — what trust, maintenance, compatibility, security, support, and freshness signals were actually imported;
- **local-fit truth** — what prototype, repository-local, or semantic-context checks were run and what mismatches they exposed;
- **brief / handoff truth** — what recommendation, alternatives, caveats, expiration point, and downstream slices are justified.

This is the biggest theory/practice guardrail in the whole design.
Without it, every recommendation becomes a confidence soup.

### Composition rule
A worthy v0 should **compose imported artifacts** instead of replacing them.

It should import, not erase:
- `atlas-lane-map/v0`
- `candidate-lane-set/v0`
- `canonical-reference-set/v0`
- `lane-default-card/v0`
- `lane-default-freshness/v0`
- `maintenance-reality-brief/v0`
- optional trust / intake / compatibility / support evidence packs
- optional `semctx-pack/v0` or other local-fit artifacts

And then it should emit one thinner **adoption-navigation family** above those imports.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo adopt question`
- `cargo adopt lanes`
- `cargo adopt canon`
- `cargo adopt evidence`
- `cargo adopt local-fit`
- `cargo adopt brief`
- `cargo adopt diff`
- `cargo adopt handoff --to <human|pr|platform|ci|assistant>`
- `cargo adopt pack`

The tool should **import** registry/docs/companion-tool surfaces when available rather than replacing them.

### Public artifact spine

#### Imported families
- `candidate-lane-set/v0`
- `canonical-reference-set/v0`
- `lane-default-card/v0`
- `lane-default-freshness/v0`
- `maintenance-reality-brief/v0`
- optional trust / compatibility / package-intake / semantic-context imports

#### Public recommendation families
- `adoption-question/v0`
- `adoption-evidence-report/v0`
- `adoption-local-fit-report/v0`
- `adoption-brief/v0`
- `adoption-alternative-set/v0`
- `adoption-handoff/v0`
- `adoption-diff-report/v0`
- `adoption-navigation-pack/v0`

### Minimum schema disciplines
Every public artifact should keep these fields first-class:
- **subject identity** — project/workspace, project class, domain, runtime family, support horizon, maturity, environment posture;
- **authority posture** — imported from canonical docs, imported from companion evidence, observed locally, or inferred;
- **scope / lane posture** — conservative default, serious alternative, experimental alternative, rejected lane, or unresolved;
- **freshness anchors** — doc versions, publish dates, renewal windows, invalidation triggers, and comparison points;
- **evidence refs** — docs, security/support/maintenance notes, trust signals, examples, and local-fit artifacts;
- **consumer limits** — what PR review, platform teams, CI, procurement, or assistants may and may not claim;
- **raw attachments** — docs URLs, manifest snippets, prototype links, comparison notes, or captured output when present;
- **reason-coded ambiguity** — why a recommendation remains partial, mixed, or unresolved.

### Commands and what they should emit

#### `cargo adopt question`
Purpose:
- capture what is being decided;
- record project class, support/risk posture, team maturity, environment, and non-goals;
- emit `adoption-question/v0`.

Important rule:
- if the question is under-specified, preserve that under-specification explicitly instead of silently importing a generic default.

#### `cargo adopt lanes`
Purpose:
- import the respectable lane space from atlas/default layers;
- emit the candidate-lane set and the initial alternative ordering.

Important rule:
- the output should explain why lanes are in or out of scope, not just list names.

#### `cargo adopt canon`
Purpose:
- collect the maintainer-authored docs, examples, and support notes that count as first reading for each serious lane;
- emit `canonical-reference-set/v0`.

Important rule:
- derived summaries must stay visibly derived; maintainer-authored canon remains stronger.

#### `cargo adopt evidence`
Purpose:
- import maintenance, trust, security, compatibility, support, and freshness signals;
- emit `adoption-evidence-report/v0`.

Important rule:
- weak or missing evidence should remain visible instead of being smoothed over with popularity.

#### `cargo adopt local-fit`
Purpose:
- record bounded project-local grounding such as prototype notes, semantic-context checks, slot mismatches, unsupported assumptions, or hidden glue;
- emit `adoption-local-fit-report/v0`.

Important rule:
- one prototype should never silently become universal truth.

#### `cargo adopt brief`
Purpose:
- tell a human what is recommended, what alternatives remain serious, what evidence shaped the call, what local-fit checks happened, and when the recommendation expires;
- render the same pack at different depths without inventing new facts.

#### `cargo adopt diff`
Purpose:
- compare two adoption packs while preserving the distinction between:
  - changed question/scope,
  - changed lane ranking,
  - changed canonical references,
  - changed imported evidence,
  - changed local-fit findings,
  - and changed downstream claims.

#### `cargo adopt handoff`
Purpose:
- emit smaller downstream exports for PR review, platform approval, CI policy, or assistants without making those slices canonical by themselves.

#### `cargo adopt pack`
Purpose:
- assemble question, lane, canon, evidence, local-fit, and handoff layers into one reviewable `adoption-navigation-pack/v0`.

## Ranked feature set

### P0 — required for a worthy v0
- explicit question capture with scope axes;
- importable candidate-lane sets rather than one flat list;
- canonical-reference capture with derived-vs-canonical markers;
- maintenance / trust / security / freshness imports kept distinct;
- bounded local-fit reporting;
- one portable brief plus one portable pack;
- diffable renewal / expiration markers;
- honest `inconclusive` / `partial` states.

### P1 — strong near-term extensions
- reusable scope-specific default cards and renewal receipts;
- policy-oriented handoffs for internal platform or procurement review;
- better support for migration-sensitive existing workspaces;
- bounded assistant exports that quote the underlying evidence pack rather than freelancing.

### P2 — do later or fold elsewhere
- hosted public ranking portals;
- social proof / popularity scoring empires;
- generalized package search;
- automatic code transformation or bootstrap generation beyond bounded handoff.

## Pilot lanes that best prove the idea

### 1) Conservative internal CLI / installable tool lane
Prove:
- the system can answer a common question without pretending it found one eternal best stack;
- default cards, canon, maintenance reality, and local-fit notes can travel together.

This lane matters because the archive already treats it as a high-legibility project class where recommendation structure should be easiest to prove.

### 2) HTTP / service lane
Prove:
- candidate-lane truth and serious alternatives survive a more crowded answer space;
- imported support/maintenance signals matter more than “everybody uses X”.

This lane matters because the challenges post explicitly notes that Rust is strong in web backends, which makes it a good place to prove disciplined recommendation rather than desperation-driven advice.

### 3) Safety-oriented internal-platform lane
Prove:
- recommendation layers can stay conservative, evidence-heavy, and renewal-aware when support horizon matters more than novelty.

This lane matters because Rust's challenges and Foundation strategy both highlight domain-specific maturity gaps and long-horizon adoption needs.

### 4) Migration-sensitive existing workspace lane
Prove:
- local-fit truth remains real when a team already has code, constraints, and migration residue;
- recommendation does not stay a greenfield fantasy.

This lane matters because one of the archive's key claims is that recommendation without semantic/local grounding is too weak.

### 5) Bounded assistant-consumer lane
Prove:
- assistant exports can exist as thinner consumer slices without becoming the canonical recommendation record.

This lane matters because the survey explicitly points to rising LLM/editor-mediated learning while docs remain canonical.

## What this contribution should prove first
A worthy v0 should prove five things in order:
1. **question honesty** — the system can capture what is actually being decided instead of smuggling in defaults;
2. **lane honesty** — the system can preserve serious alternatives and explain why they differ;
3. **canon honesty** — the system can point to maintainer-authored references instead of replacing them;
4. **evidence honesty** — maintenance, trust, security, support, and freshness signals remain separate;
5. **handoff honesty** — the same pack can drive humans, policy, CI, and assistants without changing the underlying truth.

## Anti-goals
Do not turn this contribution into:
- a universal Rust starter-pack canon;
- a public crate leaderboard;
- a popularity- or download-score empire;
- an assistant-specific recommendation blob;
- or a hidden policy engine that overrules local constraints.

## Relationship to the portfolio
This note does **not** change the broad ranking.
It sharpens the archive's current answer to a narrower question.

Interpret it this way:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Adoption Navigation Contract** remains the strongest anti-tacit-knowledge answer;
- **Native Edge Contract** remains the active specialist frontier;
- **Package Intake Gateway** remains the most underappreciated operational seam;
- **Semantic Context Contract** remains the hidden multiplier;
- and **Adoption Navigation execution blueprint** is now the canonical answer to “what should the recommendation frontier actually ship?”

## References
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://doc.rust-lang.org/cargo/faq.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://rustfoundation.org/strategic-plan/
