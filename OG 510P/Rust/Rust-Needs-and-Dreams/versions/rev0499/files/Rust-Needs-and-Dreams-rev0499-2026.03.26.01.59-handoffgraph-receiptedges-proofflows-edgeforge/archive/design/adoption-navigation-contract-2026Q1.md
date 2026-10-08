## Execution addendum (rev0422)
For questions about what the archive's **anti-tacit-knowledge / project-scoped recommendation frontier** should actually ship, read `design/adoption-navigation-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- the broad ladder is unchanged;
- **Adoption Navigation Contract** remains the strongest anti-tacit-knowledge answer rather than a new overall #1;
- this revision is **deepening**, not promotion;
- the sharper answer is now a **portable recommendation-review layer** with explicit question, lane, canon, evidence, local-fit, and handoff truth;
- and **Reviewable Lane Defaults + renewal receipts** remain the execution seam beneath it rather than disappearing into prose.

# Design: Adoption Navigation Contract 2026Q1

## Goal
Promote **Adoption Navigation Bundle** into an explicit **Adoption Navigation Contract** frontier: a thin, reviewable boundary for **what decision is being made, which respectable lanes are under consideration, which maintainer-authored references count, what imported evidence shaped the call, what local-fit checks were actually run, and what the final brief may honestly claim**.

The missing contribution is **not** one globally blessed crate list, one crate score, one improved search box, or one assistant that free-associates about the ecosystem.
It is a portable decision record that keeps recommendation layers separate enough to be reviewed, refreshed, diffed, and handed off between humans and tools.

## Why this is the right frontier now
Fresh official signals are unusually aligned around one problem family:
- Rust's March 20, 2026 challenges post names **choice paralysis** and **tacit knowledge** in ecosystem navigation, says domain maturity varies widely, and says the problem is not the absence of libraries so much as the expertise needed to choose among them.
- The 2025 State of Rust survey says online docs remain the preferred canonical reference, while people increasingly learn through LLM tooling and editors with agentic support are rising.
- Rust's December 2025 vision work says users need help getting oriented in crates.io, says there is no clear place to get advice on a good starter set of crates, and recommends better supportive guidance from crates.
- docs.rs changed its default targets in October 2025 to better reflect current platform reality, which is a reminder that recommendation inputs drift and must stay freshness-visible.
- crates.io's January 2026 update added a Security tab, stronger Trusted Publishing controls, SLOC, and `pubtime`, which means recommendation inputs are materially better than they were a year ago.
- The Rust Foundation's 2026–2028 strategy explicitly couples adoption growth, sustainable maintenance, and stable infrastructure, which makes recommendation infrastructure strategically central rather than decorative.
- The January 2026 maintenance writeup says maintenance is continuous, socially real work, which means recommendation layers need to import maintenance reality instead of using popularity as a proxy.

Together these signals say the next worthy move is no longer another essay about “good crates”.
It is a **project-scoped recommendation contract**.

## Boundary: what must stay separate
The contract only works if six truths stay visibly distinct:

### 1) Question truth
What is being decided:
- project/workspace identity
- operating context
- required constraints
- explicit non-goals
- risk posture and time horizon
- team maturity and support expectations

### 2) Candidate-lane truth
What the respectable answer space actually is:
- imported atlas domain/lane refs
- conservative default versus more opinionated alternatives
- relevant slot maps and commons seams
- invalidated lanes and why

### 3) Canonical-reference truth
What should count as first reading:
- maintainer-authored docs, guides, and examples
- support-level and docs-host posture
- warnings about partial, stale, or target-specific canon
- derived-versus-canonical markers

### 4) Imported-evidence truth
What shaped the recommendation:
- trust / policy / publisher / intake imports when relevant
- maintenance / stewardship posture
- compatibility / support-envelope / platform notes
- freshness timestamps and unresolved evidence gaps

### 5) Local-fit truth
What happened when a lane met real code or a bounded prototype:
- workspace or prototype subject
- semantic-context observations
- obvious migration burden or slot mismatch
- hidden glue or unsupported assumptions revealed locally
- checks run and checks skipped

### 6) Brief and handoff truth
What a downstream consumer may honestly conclude:
- recommended lane
- serious alternatives
- visible caveats and unanswered questions
- freshness and renewal point
- bounded renderings for human review, platform teams, CI policy, and assistants

The contract should treat these as adjacent but different truths.
A good bundle links them; it does not collapse them.

## Adjacent boundaries
- **Ecosystem Atlas Kit** still owns domains, lanes, slot maps, curator provenance, and freshness budgets.
- **Reviewable Lane Defaults** still owns reusable project-class defaults and renewal receipts.
- **Adoption Decision Stack** still owns recommendation-composition logic.
- **Canonical Learning Stack** still owns maintainer-authored canonical references and derived overlays.
- **Trust Decision Stack** still owns imported trust and policy evidence.
- **Maintenance Reality Stack** still owns stewardship, succession, and queue-pressure posture.
- **Semantic Context Contract** still owns repository-local grounding.
- **Interop Commons Kit** still owns shared seams that should be referenced rather than smuggled into prose.
- **Adoption Navigation Contract** owns the composition boundary above them.

## Artifact family
A worthy implementation should standardize a thin, boring artifact family:
- `adoption-question/v0`
- `candidate-lane-set/v0`
- `canonical-reference-set/v0`
- `adoption-evidence-report/v0`
- `local-fit-check/v0`
- `adoption-brief/v0`
- `adoption-alternative-set/v0`
- `adoption-handoff/v0`
- `adoption-diff-report/v0`
- `adoption-navigation-pack/v0`

The important design choice is not the exact filenames.
It is the rule that the final brief and assistant handoff remain **derived artifacts** rather than the source of truth.

## What a worthy contribution should look like in practice
A serious contribution here is **not** another curated website alone.
It is a portable recommendation layer that can answer a question like:

> “We are building an internal CLI with conservative support expectations and limited appetite for stack churn; what should we adopt, what are the serious alternatives, and what evidence shaped that answer?”

…and then produce a bundle that:
- imports atlas lanes instead of inventing them;
- imports canonical references instead of rewriting maintainer docs from memory;
- imports trust, maintenance, compatibility, and support evidence separately;
- records whether a real local-fit check happened;
- keeps freshness visible;
- and exposes alternatives without pretending there is one eternal best stack.

The reference UX can stay thin:
- `cargo adopt question`
- `cargo adopt lanes`
- `cargo adopt canon`
- `cargo adopt evidence`
- `cargo adopt local-fit`
- `cargo adopt brief`
- `cargo adopt diff`
- `cargo adopt pack`

## Ranked first execution lanes
1. **Greenfield internal CLI / installable tool**
   - smallest lane where stack choice still matters and docs/trust/maintenance signals are legible.
2. **HTTP/service lane**
   - high-demand lane with real runtime, interop, and support tradeoffs.
3. **Safety-oriented internal-platform lane**
   - forces support, maintenance, and evidence to matter more than popularity.
4. **Migration-sensitive existing workspace lane**
   - proves semantic-context and local-fit imports stay real.
5. **Bounded assistant-consumer lane**
   - the same bundle should yield a derived assistant handoff without changing the underlying recommendation truth.

## Non-goals
- one universal Rust “best stack” answer;
- replacing crates.io, docs.rs, Blessed.rs, lib.rs, or maintainer-authored docs;
- inventing a hidden numeric quality score;
- treating popularity as maintenance truth;
- treating one local prototype as universal evidence;
- treating an assistant rendering as canonical.

## Archive implications
- The archive should now treat **Adoption Navigation Bundle**, read as an **Adoption Navigation Contract**, as the clearest explicit **anti-tacit-knowledge / project-scoped recommendation** frontier.
- Keep **Build-State Evidence** as the strongest broad/buildable epic contribution overall.
- Keep **Reviewable Lane Defaults + renewal receipts** as the immediate execution seam beneath the new contract rather than widening the corpus blindly.
- Keep **Maintenance Reality**, **Trust Decision**, **Canonical Learning**, and **Semantic Context** as imported lanes rather than collapsing them into recommendation prose.
- Future revisions in this band should prefer **question records, candidate-lane sets, canonical-reference sets, evidence reports, local-fit checks, bounded briefs, and diff reports** over another atlas-only note, crate-score concept, or hand-written recommendation essay.

## References (signals)
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://rustfoundation.org/strategic-plan/
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://blessed.rs/crates
