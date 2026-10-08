# Epic Proposal: Maintenance Reality Stack (`cargo maintenance-reality` + `maintenance-reality-pack/v0`)

This proposal should now be read together with [`design/maintenance-reality-contract-2026Q1.md`](../design/maintenance-reality-contract-2026Q1.md), which promotes the stack into an explicit contract boundary.

## Why this is worthy
Rust increasingly needs **maintenance to be exportable as reviewable ecosystem reality instead of reconstructed from README hints, repo activity, issue queues, and private memory**.

The official signals are unusually aligned:
- The Rust Foundation’s 2026–2028 strategy puts **Sustainable Maintenance** in the core strategic pillars. That means maintenance is now explicitly treated as Rust infrastructure, not just community background radiation.
  https://rustfoundation.org/strategic-plan/
- The Rust Foundation’s Maintainers Fund announcement says the fund is meant to provide **consistent, transparent, and long-term support** for the developers who make Rust possible, with funding decisions shaped in collaboration with Rust Project leadership and with visibility into how funding is used.
  https://rustfoundation.org/media/announcing-the-rust-foundation-maintainers-fund/
- The Inside Rust post **What is maintenance, anyway?** exists because the project is still actively defining what maintenance work should count for funding and support. That is a strong sign that the ecosystem needs clearer artifact boundaries for maintenance work rather than one catch-all bucket.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- The compiler-team operations writeup says that ops work is needed, improves things for everyone, and helps the Rust Project grow sustainably. That is a concrete example of maintenance labor as operational infrastructure rather than invisible glue.
  https://blog.rust-lang.org/inside-rust/2025/06/05/a-glance-at-the-team-compiler-operations/
- Rust Forge’s triage procedures already encode explicit workflow semantics: status labels, 15-day thresholds, occasional blocked checks, required triage reports, issue-actionability checks, `S-needs-info`, and prioritization routing. That means there is enough shared semantics to export narrow truthful artifacts now.
  https://forge.rust-lang.org/release/triage-procedure.html
  https://forge.rust-lang.org/release/issue-triaging.html
  https://forge.rust-lang.org/compiler/prioritization.html
- The 2025 State of Rust survey reports a slight uptick in concern around **developer and maintainers support**, says funding efforts should focus on retaining people who would otherwise leave after unpaid labor, and directly asks companies using Rust to support Rust contributors and authors of crates they rely on.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

But the ecosystem still has no single honest handoff for **maintenance reality**.
The new constraint this archive should enforce is that maintenance reality is lane-shaped: lifecycle intent, workflow policy, observed operational state, derived pressure findings, help-routing, mentoring capacity, visibility posture, and consumer handoffs are different facts.

That means Atlas/adoption tools, release reviewers, trust/policy systems, support programs, fund committees, keystone reviews, and assistants still have to reconstruct the story from:
- declared support windows or deprecation prose,
- queue states and ad hoc labels,
- backport/regression notes,
- help requests scattered across issues, Zulip, and blogs,
- mentoring promises and newcomer labels with unclear staffing,
- and private project memory about who is overloaded, who is leaving, and what continuity risks actually matter.

The missing contribution is a thin composition layer above lifecycle and stewardship artifacts, **not** another public maintainer dashboard, popularity ranking, or secret funding oracle. The concrete separation rule now lives in [`design/maintenance-reality-lane-map.md`](../design/maintenance-reality-lane-map.md).

## Proposal
Define a **Maintenance Reality Stack** with:
- a reference companion CLI, `cargo maintenance-reality`;
- a thin linked bundle, `maintenance-reality-pack/v0`;
- imported evidence from:
  - `lifecycle-pack/v0`,
  - `steward-pack/v0`,
  - `steward-pilot-pack/v0`,
  - optional `trust-pack/v0`, `support-pack/v0`, `release-pack/v0`, `keystone-pack/v0`, and `adoption-brief/v0` pointers;
- stable stack-facing artifacts:
  - `maintenance-subject/v0`
  - `maintenance-reality-brief/v0`
  - `maintenance-transition-report/v0`
  - `maintenance-consumer-handoff/v0`
  - `maintenance-reality-pack/v0`

The brief layer should keep these sub-lanes explicit:
- lifecycle intent imports
- workflow-policy imports
- observed-state imports
- derived pressure findings
- help/succession routing
- mentoring-capacity notes
- visibility/redaction posture
- consumer-specific bounded views

## Reference CLI shape
- `cargo maintenance-reality export-subject`
  - emit `maintenance-subject/v0` for one crate, workspace, org, or project lane
- `cargo maintenance-reality review`
  - emit `maintenance-reality-brief/v0` from imported lifecycle + stewardship evidence, with explicit visibility posture and inconclusive sections
- `cargo maintenance-reality diff --against <prior-pack-or-brief>`
  - emit `maintenance-transition-report/v0`
- `cargo maintenance-reality handoff --for <atlas|adoption|release|policy|fund|keystone|assistant>`
  - emit `maintenance-consumer-handoff/v0`
- `cargo maintenance-reality pack`
  - produce `maintenance-reality-pack/v0`
- `cargo maintenance-reality verify-pack <path>`
  - verify schema versions, checksums, import integrity, redaction posture, and freshness declarations

This should stay a **thin composition layer**.
It should not replace lifecycle declarations, stewardship exporters, Rust Foundation support processes, fund decision committees, release governance, or keystone reviews.

## What `maintenance-reality-pack/v0` should contain
- `manifest.json`
- `maintenance-subject.json`
- `maintenance-reality-brief.json`
- optional `maintenance-transition-report.json`
- one or more `maintenance-consumer-handoff.json` attachments
- imported lifecycle / stewardship / pilot artifacts or checksummed pointers
- explicit visibility posture, redaction notes, and freshness budgets
- generator identity, checksums, and import-lossiness markers

## Design principles
- **Declared lifecycle stays distinct from observed operations.** “Supported” is not the same thing as “staffed” and neither one should silently rewrite the other.
- **Workflow policy stays distinct from queue snapshots.** Aging thresholds, blocked-state semantics, and routing rules are not the same fact as today’s queue contents.
- **Derived pressure findings stay distinct from raw observations.** Concentration, burnout-adjacent, or continuity-risk findings should cite their inputs rather than masquerading as direct state.
- **Visibility policy is first-class.** Some operational truth should be public, some should be restricted, and the stack must show which is which rather than pretending all evidence can be published safely.
- **Help requests are evidence-bearing artifacts, not social afterthoughts.** A maintainer asking for review help, release help, or continuity support should be exportable with context and urgency.
- **Continuity risk is not the same as trust or popularity.** Maintenance reality may import trust or release facts, but it should not collapse them into one score.
- **Companion-tool success is real success.** Becoming a reusable evidence and handoff layer for Atlas, release, keystone, and support programs is already a worthy outcome.
- **Consumers get bounded handoffs.** Atlas/adoption, release/policy, funding/support, and keystone consumers should each receive explicit summaries instead of freelancing from raw queue data.

## Early implementation order
1. single-project lifecycle + PR-triage lane
2. issue-intake / repro / prioritization lane
3. release / regression / backport lane
4. explicit help-routing / support-program lane
5. keystone / adoption / assistant consumer lane

That order follows the real pressure gradient: first make declared support and operational queues legible together, then widen into issue actionability, then connect maintenance to shipping risk, then make support routing reviewable, and only after that widen into thinner cross-project consumers.

## Non-goals
- a universal maintainer-health score;
- a public wall-of-shame dashboard;
- automatic transfer or abandonment decisions from queue pressure;
- a funding engine that hides human judgment behind artifact math;
- a registry badge that pretends maintenance is settled forever;
- flattening public evidence and restricted support requests into one public feed.

## Success bar
This becomes worthy when a maintainer, curator, release reviewer, support/funding body, or downstream consumer can answer:
- what the project says about support, deprecation, succession, and handoff;
- what operations actually look like right now;
- what work is public, what is restricted, and why;
- where help is explicitly needed;
- what changed since the last review;
- which consumers may safely act on the result;
- and what remains inconclusive,

without reconstructing the story from GitHub labels, blog posts, meeting notes, and institutional memory.

## Read this with
- `design/maintenance-reality-stack.md`
- `design/stewardship-pilot-program.md`
- `design/lifecycle-ledger-kit.md`
- `design/stewardship-ops-kit.md`
- `design/trust-decision-stack.md`
- `design/keystone-stewardship-stack.md`
- `design/adoption-decision-stack.md`
