## rev0499 — add a handoff-graph ledger so the archive can name exact receipt edges between strong seams instead of waving at “integration”
This revision is a **continue-research + worthy-repo-construction + handoff-graph / receipt-edge canon** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to another recurrent follow-on question:
**once the strongest seams already have wedges, journeys, and first shipsets, what exact artifacts should move between them, what boundaries are allowed to carry those artifacts, and what larger platform collapse is still refused?**

The refreshed canon is:
- `design/epic-contribution-handoff-graph-2026Q1.md`
- `meta/HANDOFF_GRAPH_PROTOCOL.md`
- `ledgers/top-band-handoff-graph-v0/README.md`
- `ledgers/top-band-handoff-graph-v0/handoffs.json`
- `tools/check_handoff_graph.py`

Why this refresh was merited:
- official Cargo guidance still centers stable machine-facing integration lanes rather than Cargo-as-a-library fantasies;
- Cargo build analysis, build-dir-layout churn, crates.io security/service truth, rustdoc JSON caveats, and libtest JSON all sharpen the need for explicit receipt edges;
- the repo already had kernels and journeys, but it still lacked one compact machine-checked place to say **what artifact should actually move from one to another**; and
- future assistants needed one more anti-amnesia rail so “these ideas compose” does not quietly replace the actual edge canon.

Archive decision:
- add the design note and protocol for the handoff-graph layer
- add and validate `ledgers/top-band-handoff-graph-v0/handoffs.json`
- add `tools/check_handoff_graph.py` and wire it into hygiene and archive-doctor
- refresh front-door routing and continuity rails: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `meta/ARCHIVE_DOCTOR_PROTOCOL.md`
- refresh `ledgers/README.md`, `kernels/README.md`, `RESEARCH_LOG.md`, and `atlases/portfolio-source-atlas-v0/sources.json`
- mirror refreshed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the new missing layer is **handoff graph / receipt-edge canon**, not a fresh worthy-contribution seam;
- **Build-State Evidence** remains the clearest first build and now also anchors the first required receipt edge;
- **Package Intake + Release Boundary Review** remains the clearest urgent operator seam and now also anchors the strongest service-truth handoff;
- and future continue-research passes should now say **what artifact moves between seams and what that edge is allowed to mean** instead of only saying that the seams fit together.

## rev0498 — add a kernel-shipset ledger so the archive can name exact first repo shapes without re-inventing them from packets and mood
This revision is a **continue-research + worthy-repo-construction + kernel-shipset / first-repo-shape canon** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to another recurrent follow-on question:
**once a seam has already earned kernelization, what exact first shipset should a small team build, what modules belong in that repo, what proof artifacts must it emit, and what bigger product shape is still refused?**

The refreshed canon is:
- `design/epic-contribution-kernel-shipset-ledger-2026Q1.md`
- `meta/KERNEL_SHIPSET_LEDGER_PROTOCOL.md`
- `ledgers/top-band-kernel-shipsets-v0/README.md`
- `ledgers/top-band-kernel-shipsets-v0/shipsets.json`
- `tools/check_kernel_shipsets.py`

Why this refresh was merited:
- current Rust signals still reward bounded companion-first shipsets over framework theater;
- the repo already had prose kernel briefs, but it still lacked one compact, validated place to keep their endorsed repo/module shapes current;
- build analysis, build-dir-layout, registry security work, rustdoc JSON caveats, and libtest JSON all strengthen the case for explicit import surfaces and proof artifacts in first shipsets; and
- future assistants needed one more anti-amnesia rail so “we roughly know what v0 looks like” does not quietly replace the actual first-build canon.

Archive decision:
- add the design note and protocol for the kernel-shipset ledger layer
- add and validate `ledgers/top-band-kernel-shipsets-v0/shipsets.json`
- add `tools/check_kernel_shipsets.py` and wire it into hygiene and archive-doctor
- refresh front-door routing and continuity rails: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `meta/ARCHIVE_DOCTOR_PROTOCOL.md`
- refresh `ledgers/README.md`, `kernels/README.md`, `RESEARCH_LOG.md`, and `atlases/portfolio-source-atlas-v0/sources.json`
- mirror refreshed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the new missing layer is **kernel shipset / first-repo-shape canon**, not a fresh worthy-contribution seam;
- **Build-State Evidence** remains the clearest first build and now also has the clearest machine-validated first shipset card;
- **Package Intake + Release Boundary Review** remains the clearest urgent local review kit;
- and future continue-research passes should now say **which exact first shipset the repo endorses** instead of only gesturing toward one.

## rev0497 — add a decision-journey layer so the strongest seams compose inside real operator moments instead of only reading as adjacent good ideas
This revision is a **continue-research + worthy-repo-construction + decision-journey / repeated-operator-moment composition** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to another recurrent follow-on question:
**once the strongest seams are ranked, specified, placed, watched, and given believable wedges, what repeated real-world decision moments should they actually compose inside?**

The refreshed canon is:
- `design/epic-contribution-decision-journeys-2026Q1.md`
- `meta/DECISION_JOURNEY_PROTOCOL.md`
- `ledgers/portfolio-decision-journeys-v0/README.md`
- `ledgers/portfolio-decision-journeys-v0/journeys.json`
- `tools/check_decision_journeys.py`

Why this refresh was merited:
- current Rust signals still point to repeated operator moments around rebuild triage, publish/intake review, debug issue handoff, release-boundary review, safety-readiness evaluation, and conservative default selection rather than one missing mega-framework;
- the repo already knew how to rank seams, give them wedges, and state falsifiers, but it still lacked one explicit place to say **how several seams should work together during one real decision**;
- official Cargo and crates.io work is increasingly workflow-shaped, not just substrate-shaped; and
- future assistants needed one more anti-smoothing rail so “these ideas are compatible” does not quietly become “there is already a practical workflow story here.”

Archive decision:
- add the design note and protocol for the decision-journey layer
- add and validate `ledgers/portfolio-decision-journeys-v0/journeys.json`
- add `tools/check_decision_journeys.py` and wire it into hygiene and archive-doctor
- refresh front-door routing and continuity rails: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `meta/ARCHIVE_DOCTOR_PROTOCOL.md`
- refresh `ledgers/README.md`, `RESEARCH_LOG.md`, and `atlases/portfolio-source-atlas-v0/sources.json`
- mirror refreshed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the new missing layer is **decision journeys**, not a fresh worthy-contribution seam;
- **Build-State Evidence** remains the clearest first build and now also anchors the clearest cross-seam journey;
- **Package Intake + Release Boundary Review** remains the clearest urgent operator review journey;
- and future continue-research passes should now say **what repeated decision moment a proposed contribution changes** instead of only why it sounds worthy.


## rev0496 — add a launch-wedge layer so worthy contributions have believable first users, first proofs, and anti-goals instead of only elegant design names
This revision is a **continue-research + worthy-repo-construction + launch-wedge / first-proof-path** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to another recurrent follow-on question:
**once a contribution looks worthy in theory, what is the first believable adoption wedge, what artifact enters that moment, what would count as honest first proof, and what broader product temptation should still be refused?**

The refreshed canon is:
- `design/epic-contribution-launch-wedges-2026Q1.md`
- `meta/LAUNCH_WEDGE_PROTOCOL.md`
- `ledgers/portfolio-launch-wedges-v0/README.md`
- `ledgers/portfolio-launch-wedges-v0/wedges.json`
- `tools/check_launch_wedges.py`

Why this refresh was merited:
- current Rust signals still point to repeated practical decisions around compile/rebuild pain, crate trust, debugger capability, and safety-readiness burden rather than one missing framework;
- the repo already knew how to rank, build out, place, watch, and falsify seams, but it still lacked one explicit place to say **who the first user is and what proof would show the seam deserves widening**;
- Cargo and crates.io continue to expose bounded facts and extension paths rather than full finished products, which makes wedge discipline especially useful now; and
- future assistants needed one more anti-smoothing rail so “this looks strategically important” does not quietly become “this has a believable path into practice.”

Archive decision:
- add the design note and protocol for the launch-wedge layer
- add and validate `ledgers/portfolio-launch-wedges-v0/wedges.json`
- add `tools/check_launch_wedges.py` and wire it into hygiene and archive-doctor
- refresh front-door routing and continuity rails: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `meta/ARCHIVE_DOCTOR_PROTOCOL.md`
- refresh `RESEARCH_LOG.md` and `atlases/portfolio-source-atlas-v0/sources.json`
- mirror refreshed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the new missing layer is **launch wedge / first-proof-path discipline**, not a fresh worthy-contribution seam;
- **Build-State Evidence** remains the strongest single-project claim and now also the clearest first wedge;
- **Package Intake + Release Boundary Review** remains the clearest urgent operator-facing wedge;
- and future continue-research passes should now say **how a seam enters the world credibly** instead of only why it sounds worthy.

## rev0495 — add a hypothesis-ledger layer so the archive's strongest current claims can be narrowed or broken visibly instead of living forever as tone
This revision is a **continue-research + worthy-repo-construction + hypothesis-ledger / falsifier-gate** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to another recurrent follow-on question:
**once the strongest contributions are ranked, built out, placed, packetized, and watched, where does the repo keep the strongest present-tense claims as explicit claims with downgrade triggers and falsifiers instead of house style?**

The refreshed canon is:
- `design/portfolio-hypothesis-ledger-2026Q1.md`
- `meta/HYPOTHESIS_LEDGER_PROTOCOL.md`
- `ledgers/portfolio-hypothesis-ledger-v0/hypotheses.json`
- `tools/check_hypothesis_ledger.py`

Why this refresh was merited:
- current Rust signals still make the top claims plausible, but in caveat-heavy ways: build analysis is still prototype-stage, build-dir behavior is still moving, service truths keep getting richer, and safety/institutional readiness is still program-shaped rather than magically productized;
- the repo already knew how to rank and refresh, but it still lacked one explicit place to say which broad claims are live, what would narrow them, and what would falsify them;
- and future assistants needed one more anti-smoothing rail so that “the archive keeps saying this” does not quietly become “this is still true”.

Archive decision:
- refresh the design note and meta protocol for the hypothesis-ledger layer
- refresh `ledgers/portfolio-hypothesis-ledger-v0/hypotheses.json`
- refresh `tools/check_hypothesis_ledger.py`
- refresh front-door routing and continuity rails: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- refresh `RESEARCH_LOG.md` and `atlases/portfolio-source-atlas-v0/sources.json`
- mirror refreshed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the new missing layer is **hypothesis-ledger / falsifier-gate discipline**, not a fresh worthy-contribution seam;
- **Build-State Evidence** remains the strongest single-project claim;
- a thin family of evidence, review, and readiness layers still beats one new platform empire;
- fast substrate drift should still land in watchcards before frontier promotion; and
- future continue-research passes should now say which strong claims were confirmed, narrowed, degraded, superseded, or retired instead of only rephrasing the canon.

## rev0494 — add a hot-substrate watchcard layer so fast-moving Rust truths land somewhere concrete before they impersonate packets or canon
This revision is a **continue-research + worthy-repo-construction + hot-substrate-watchcard** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has an explicit artifact family for the fastest loop:
- `design/epic-contribution-hot-substrate-watchcards-2026Q1.md`
- `meta/HOT_SUBSTRATE_WATCH_PROTOCOL.md`
- the four current `evidence/hot-substrate-*.md` watchcards

Interpretation:
- the broad ladder is unchanged;
- the new missing layer is **hot-substrate watchcards**, not a fresh worthy-contribution seam;
- future continue-research passes should now land fast-moving source truth in watchcards before touching packets, charters, or canon.

## rev0493 — add a portfolio control-loop note so worthy contributions keep living on the right cadence instead of being frozen or reranked on every new signal
This revision is a **continue-research + worthy-repo-construction + control-loop/cadence** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to another recurrent follow-on question:
**once the strongest contributions are known, built out, given a shared operator grammar, and mapped to honest homes, what recurring loop should keep them current without confusing hot substrate drift, current packet posture, stewardship decisions, broad canon refresh, and repo hygiene?**

The new notes are:
- `design/epic-contribution-portfolio-control-loop-2026Q1.md`
- `meta/PORTFOLIO_CONTROL_LOOP_PROTOCOL.md`

Why this refresh was merited:
- current Rust process signals are strongly cadence-shaped: goals now run on a full-year cycle with explicit phases and owner/champion expectations;
- maintenance, foundation strategy, and new hosting modes like the Rust Innovation Lab all reinforce that worthy work survives on the cadence its steward burden requires;
- Cargo/build-analysis, service surfaces, and operator/security boundaries keep moving faster than the broad ladder should;
- and future assistants needed one more way to distinguish **hot substrate watch**, **decision-packet refresh**, **charter/stewardship review**, **canon refresh**, and **archive hygiene**.

Archive decision:
- new design note: `design/epic-contribution-portfolio-control-loop-2026Q1.md`
- new meta protocol: `meta/PORTFOLIO_CONTROL_LOOP_PROTOCOL.md`
- design-front-door refresh: `design/ideal-rust-worthy-contributions-2026Q1.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/territory-priority-refresh-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the new missing layer is **portfolio control-loop / renewal-cadence discipline**, not a fresh worthy-contribution seam;
- **Build-State Evidence** and **Package Intake + Release Boundary Review** still lead, but they now clearly live on faster hot-watch and packet loops than the broad canon does;
- **Feedback / Debug Acceptance Commons** and **Safety-Critical + Institutional Readiness Commons** still deepen rather than widen, but now with visibly different packet vs stewardship rhythms;
- **Adoption Navigation + Ecosystem Atlas** remains strategically huge and should still move on the slowest renewal loop; and
- future “continue the repo” answers should now route through the new control-loop note and protocol before treating every fresh signal as either a ladder rewrite or a reason to do nothing.


## rev0492 — add a stewardship-and-graduation note so worthy contributions get honest homes instead of prestige-driven merges
This revision is a **continue-research + repo-construction + stewardship/graduation** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to another recurrent follow-on question:
**once the strongest contributions are known, what should stay companion-first, what raw facts belong upstream or service-side, what might deserve optional toolchain distribution, and what only becomes real through project or consortium stewardship?**

The new notes are:
- `design/epic-contribution-stewardship-and-graduation-map-2026Q1.md`
- `meta/STEWARDSHIP_AND_GRADUATION_PROTOCOL.md`

Why this refresh was merited:
- current Rust signals now show multiple honest homes rather than one universal answer: Cargo prototypes some raw evidence inside core, external tools remain the default extension path, Clippy remains the clearest optional-component model, crates.io and docs.rs expose real service truth, and specification/safety-critical work now has visible long-horizon stewardship patterns;
- future assistants needed a way to distinguish **rank**, **vehicle**, **decision rights**, **shared operator grammar**, and **maturity / graduation path**;
- and the repo needed a cleaner way to say “upstream the facts, not the whole product” or “this only becomes real as a commons/program”, instead of flattening everything into core-vs-external.

Archive decision:
- new design note: `design/epic-contribution-stewardship-and-graduation-map-2026Q1.md`
- new meta protocol: `meta/STEWARDSHIP_AND_GRADUATION_PROTOCOL.md`
- design-front-door refresh: `design/ideal-rust-worthy-contributions-2026Q1.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/territory-priority-refresh-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the new missing layer is **stewardship and graduation discipline**, not a fresh worthy-contribution seam;
- **Build-State Evidence** remains the clearest first deep product surface and now also the clearest split-home build: companion-first product over narrow Cargo-owned raw facts;
- **Package Intake + Release Boundary Review** remains the clearest operator-boundary seam and now also the clearest companion + service-truth split-home build;
- **Feedback / Debug Acceptance** and **Safety-Critical + Institutional Readiness** remain the strongest deepen lanes and now also the clearest cases for consortium/program stewardship rather than one-repo fantasy;
- **Compatibility Claims** remains the clearest renewable companion-first claims layer with selective future distribution or upstream-fact asks; and
- future “continue building the worthy repo” answers should now route through the new stewardship/graduation note and protocol before inventing prestige-driven merger plans.

## rev0491 — add an operating-surface note so the strongest seams can mature as one family instead of seven dialects
This revision is a **continue-research + repo-construction + operating-surface** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to another recurrent follow-on question:
**once the worthy contributions and buildout order are already known, what common operator grammar should they share in theory and in practice so the repo compounds as a family rather than fragmenting into local frameworks?**

The new notes are:
- `design/epic-contribution-operating-surface-2026Q1.md`
- `meta/OPERATING_SURFACE_PROTOCOL.md`

Why this refresh was merited:
- current official Rust signals increasingly point to machine-usable evidence and review surfaces, not one more flagship framework;
- Cargo build-analysis/report work, Cargo external-tools guidance, libtest JSON, rustdoc JSON, crates.io service truth, and toolchain-distributed optional components now give the archive a better practical vocabulary for shared operator verbs;
- package-intake, debug-acceptance, safety-readiness, compatibility, and tooling-contract work all benefit from a common family of report/diff/review/replay/renew/doctor/export moves; and
- future assistants needed a way to distinguish **ranking**, **packet posture**, **repo buildout order**, and **shared operating grammar**.

Archive decision:
- new design note: `design/epic-contribution-operating-surface-2026Q1.md`
- new meta protocol: `meta/OPERATING_SURFACE_PROTOCOL.md`
- design-front-door refresh: `design/ideal-rust-worthy-contributions-2026Q1.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/territory-priority-refresh-2026Q1.md`, `design/epic-contribution-worthy-repo-buildout-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the new missing layer is **shared operating surface**, not a new worthy-contribution seam;
- the most important shared family gap is now **report/diff/explain + negative-state receipts + review/recheck verbs**;
- **Build-State Evidence** remains the clearest first deep product surface, but it now also acts as the clearest model for the family grammar;
- **Package Intake + Release Boundary Review** remains the clearest operator-boundary seam and benefits most from shared review/admit/quarantine/waive/recheck verbs;
- **Feedback / Debug Acceptance** and **Safety-Critical + Institutional Readiness** remain the strongest deepen lanes and gain the most from session/replay/renew/doctor discipline; and
- future “continue building the worthy repo” answers should now route through the new operating-surface note and protocol before inventing fresh local command families.

## rev0490 — add a worthy-repo buildout note so continuing research deepens the strongest seams instead of fragmenting the map
This revision is a **continue-research + repo-buildout-order + theory/practice deepening** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to a recurrent follow-on question:
**once the latest archive and latest official Rust signals have been refreshed, how should the repo keep growing, what should the strongest contributions look like in theory and practice, and which fresh side-bets should be folded instead of promoted?**

The new notes are:
- `design/epic-contribution-worthy-repo-buildout-2026Q1.md`
- `meta/WORTHY_REPO_BUILDOUT_PROTOCOL.md`

Why this refresh was merited:
- the live-refresh pass clarified current ecosystem pressure, but it still left one recurring construction question open: how to keep extending the archive without multiplying seams;
- current official signals now offer stronger practical hooks for several existing leaders, especially build evidence, package-intake/release-boundary review, debugger acceptance, and safety-critical readiness;
- the Project Director update made capability analysis, vulnerability surfacing, and interop mapping concrete enough to matter for repo shape; and
- future assistants needed a way to distinguish **broad ranking**, **current packet posture**, **repo buildout order**, and **fold-under-parent discipline**.

Archive decision:
- new design note: `design/epic-contribution-worthy-repo-buildout-2026Q1.md`
- new meta protocol: `meta/WORTHY_REPO_BUILDOUT_PROTOCOL.md`
- design-front-door refresh: `design/ideal-rust-worthy-contributions-2026Q1.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/territory-priority-refresh-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the new missing layer is **worthy repo buildout discipline**, not another broad ranking rewrite;
- **Build-State Evidence** remains the clearest deep first-class product surface;
- **Package Intake + Release Boundary Review** remains the clearest operator-shaped boundary surface and now absorbs capability-analysis hooks more explicitly;
- **Feedback / Debug Acceptance Commons** remains the clearest tuple-acceptance deepening lane;
- **Safety-Critical + Institutional Readiness Commons** remains the clearest program-shaped deepening lane;
- **Compatibility Claims** and **Tooling Contract / Semantic Context** remain critical supporting layers; and
- future “continue the repo” answers should now route through the new worthy-repo buildout note and protocol before inventing fresh seams.

## rev0489 — add a live ecosystem refresh note and source-candor protocol without changing the broad ladder
This revision is a **latest-archive + latest-official-signals refresh**.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to a recurrent maintainer question:
**if we re-open the latest canon, re-check the freshest official Rust signals, and ask what ideal Rust still needs now, how do we keep strategic ranking, current packet posture, and LLM/source-candor hygiene separate?**

The new notes are:
- `design/epic-contribution-live-ecosystem-refresh-2026Q1.md`
- `meta/LIVE_ECOSYSTEM_REFRESH_PROTOCOL.md`

Why this refresh was merited:
- the latest official Rust signals still reinforce build/resource pain, debugger friction, package-intake/supply-chain reality, safety-critical maturity gaps, and recommendation/tacit-knowledge burden;
- the archive already had broad ranking, live packets, kernel briefs, slices, contracts, witnesses, fixtures, and schemas, but lacked one explicit **live-refresh synthesis note** that kept strategic importance separate from current delivery posture;
- the March 2026 challenges post also created a new meta-hygiene lesson: a source can be current and still require unusually careful source-candor handling; and
- future assistants needed a way to answer “latest” without reconstructing present-tense truth from memory or from one fresh post.

Archive decision:
- new design note: `design/epic-contribution-live-ecosystem-refresh-2026Q1.md`
- new meta protocol: `meta/LIVE_ECOSYSTEM_REFRESH_PROTOCOL.md`
- design-front-door refresh: `design/ideal-rust-worthy-contributions-2026Q1.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/territory-priority-refresh-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the new missing layer is **live ecosystem refresh + source-candor discipline**, not another ranking rewrite;
- **Build-State Evidence** remains the clearest broad first build and the clearest current `advance`;
- **Package Intake + Release Boundary Review** remains the clearest urgent operator-shaped `advance`;
- **Feedback / Debug Acceptance Commons** and **Safety-Critical Readiness Commons** remain the clearest current `deepen` lanes;
- **Adoption Navigation + Ecosystem Atlas** remains strategically huge but current-kernel `hold` until renewal burden is more honestly solved; and
- future “what does the latest archive plus latest Rust signals imply?” answers should now route through the new live-refresh note and protocol before re-summarizing the territory.

## rev0488 — add kernel artifact schemas so top-band kernels become machine-validatable, not just well-described and replayable
This revision is an **artifact-schema-pack + conformance-validator** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to the next practical question after fixture packs:
**once the repo knows what surface a first implementation should honor, what outputs that surface should emit, and what replayable scenarios should drive them, what machine-readable JSON families should validate so two implementations stay compatible without telepathy?**

The new notes are:
- `design/epic-contribution-kernel-artifact-schemas-2026Q1.md`
- `meta/KERNEL_ARTIFACT_SCHEMA_PROTOCOL.md`

The new schema corpus is:
- `schemas/top-band-v0/*.schema.json`
- `schemas/top-band-v0/schema-pack-hygiene-checks.json`
- `schemas/README.md`
- `schemas/top-band-v0/README.md`

This pass also adds a new validator and expands the witness/specimen corpus with missing shared-receipt and route/lint examples.

Why this refresh was merited:
- the repo already had ranking, packets, dossiers, kernels, slices, contracts, witnesses, and fixtures, but still lacked a **machine-validatable schema layer**;
- fresh Rust signals still reward explicit format-versioning, programmatic output, and schema-bearing external-tool surfaces over scraping or dashboard theater;
- example payloads alone still left too much room for structural drift to pass unnoticed; and
- future assistants needed a way to stop treating JSON examples as frozen by vibe rather than by a versioned schema family.

Archive decision:
- new design note: `design/epic-contribution-kernel-artifact-schemas-2026Q1.md`
- new meta protocol: `meta/KERNEL_ARTIFACT_SCHEMA_PROTOCOL.md`
- new schema corpus: `schemas/top-band-v0/*`
- schema-corpus refresh: `schemas/README.md`, `schemas/top-band-v0/README.md`, `schemas/top-band-v0/schema-pack-hygiene-checks.json`
- new checker: `tools/check_kernel_artifact_schemas.py`
- specimen refresh: `specimens/README.md`, `specimens/kernel-contract-witnesses-v0/README.md`, the four witness notes, and new example JSON receipts/reports
- doctor/hygiene refresh: `meta/ARCHIVE_DOCTOR_PROTOCOL.md`, `tools/archive_doctor.py`, `tools/hygiene.py`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the missing new layer is **kernel artifact schemas**, not another ranking rewrite;
- **Build-State Evidence** remains the clearest first serious build and now also has explicit schema families for session packs, diffs, and unsupported-state receipts;
- **Feedback / Debug Acceptance Commons** remains the clearest second serious build and now also has explicit schema families for tuple/session/replay artifacts;
- **Package Intake + Release Boundary Review** remains the sharpest operator bridge and now also has route-profile, intake, waiver, quarantine, drill, and unsupported-state schemas;
- **Safety-Critical + Institutional Readiness Commons** remains the clearest stewarded long-horizon seam and now also has readiness card/pack/lint/diff/stale-receipt schemas; and
- **Navigation / Defaults / Claims Commons** remains intentionally unschematized because the blocker is still renewal burden rather than payload-shape imagination.

## rev0487 — add kernel fixture packs so top-band kernels become replayable, not just well-described
This revision is a **kernel-fixture-pack + replay-input** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to the next practical question after witness packs:
**once the repo knows what surface a first implementation should honor and what outputs that surface should emit, what scenario inputs and expected checks should drive those outputs honestly?**

The new notes are:
- `design/epic-contribution-kernel-fixture-packs-2026Q1.md`
- `meta/KERNEL_FIXTURE_PACK_PROTOCOL.md`

The new fixture corpus is:
- `fixtures/top-band-v0/build-state-pack.inner-loop-stable.fixture.json`
- `fixtures/top-band-v0/build-state-pack.build-dir-layout-caveat.fixture.json`
- `fixtures/top-band-v0/debug-acceptance-matrix.async-tuple.fixture.json`
- `fixtures/top-band-v0/package-intake-review-kit.alternate-registry.fixture.json`
- `fixtures/top-band-v0/safety-critical-readiness-cards.stale-card.fixture.json`
- plus corpus-overview and hygiene files in the same folder

Why this refresh was merited:
- the repo already had ranking, packets, dossiers, kernels, slices, contracts, and witnesses, but still lacked a **replayable input-and-check layer**;
- fresh Rust signals still reward machine-readable command recipes, real-workflow testing, and programmatic harness surfaces over platform theater;
- witness artifacts alone still left too much room for future editors to forget what proving-ground case or negative-state posture should generate them; and
- future assistants needed a way to stop treating output examples as free-floating illustrations.

Archive decision:
- new design note: `design/epic-contribution-kernel-fixture-packs-2026Q1.md`
- new meta protocol: `meta/KERNEL_FIXTURE_PACK_PROTOCOL.md`
- new fixture corpus: `fixtures/top-band-v0/*`
- fixture-hygiene refresh: `fixtures/README.md`, `fixtures/top-band-v0/README.md`, `fixtures/top-band-v0/fixture-pack-hygiene-checks.json`
- new checker: `tools/check_kernel_fixture_packs.py`
- doctor/hygiene refresh: `meta/ARCHIVE_DOCTOR_PROTOCOL.md`, `tools/archive_doctor.py`, `tools/hygiene.py`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the missing new layer is **kernel fixture packs**, not another ranking rewrite;
- **Build-State Evidence** remains the clearest first serious build and now also has stable-only and experimental-caveated replay fixtures;
- **Feedback / Debug Acceptance Commons** remains the clearest second serious build and now also has an async-heavy tuple replay fixture;
- **Package Intake + Release Boundary Review** remains the sharpest operator bridge and now also has a route-specific uncertainty fixture;
- **Safety-Critical + Institutional Readiness Commons** remains the clearest stewarded long-horizon seam and now also has a stale-evidence fixture; and
- **Navigation / Defaults / Claims Commons** remains intentionally un-fixtured because the blocker is still renewal burden rather than replay-shape imagination.


## rev0486 — add contract witness packs so top-band kernels have concrete example outputs, not just contract prose
This revision is a **contract-witness-pack + example-artifact** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to the next practical question after contract0:
**once the repo knows what command/file/schema surface a first implementation should honor, what should that surface actually look like when exercised honestly?**

The new notes are:
- `design/epic-contribution-contract-witness-packs-2026Q1.md`
- `meta/KERNEL_CONTRACT_WITNESS_PROTOCOL.md`

The new witness corpus is:
- `specimens/kernel-contract-witnesses-v0/build-state-pack.witness.md`
- `specimens/kernel-contract-witnesses-v0/debug-acceptance-matrix.witness.md`
- `specimens/kernel-contract-witnesses-v0/package-intake-review-kit.witness.md`
- `specimens/kernel-contract-witnesses-v0/safety-critical-readiness-cards.witness.md`
- plus their paired example artifacts in the same folder

Why this refresh was merited:
- the repo already had ranking, packets, dossiers, kernels, slices, and contracts, but still lacked a **concrete exercised-output layer**;
- fresh Rust signals still reward documented machine-facing seams, explicit compatibility posture, and local-first receipts over platform ambition;
- contract prose alone still left too much room for future editors to normalize away negative states or stable/experimental separation; and
- future assistants needed a way to stop re-inventing example outputs from prose when the archive already had enough structure to show them.

Archive decision:
- new design note: `design/epic-contribution-contract-witness-packs-2026Q1.md`
- new meta protocol: `meta/KERNEL_CONTRACT_WITNESS_PROTOCOL.md`
- new witness corpus: `specimens/kernel-contract-witnesses-v0/*`
- specimen-hygiene refresh: `specimens/README.md`, `meta/SPECIMEN_CORPUS_PROTOCOL.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the missing new layer is **contract witness packs**, not another ranking rewrite;
- **Build-State Evidence** remains the clearest first serious build and now also has the clearest example capture/diff/doctor witness bundle;
- **Feedback / Debug Acceptance Commons** remains the clearest second serious build and now also has the clearest tuple-card / replay witness bundle;
- **Package Intake + Release Boundary Review** remains the sharpest operator bridge and now also has the clearest local review/waiver/drill witness bundle;
- **Safety-Critical + Institutional Readiness Commons** remains the clearest stewarded long-horizon seam and now also has the clearest card/pack/diff witness bundle; and
- **Navigation / Defaults / Claims Commons** remains intentionally unwitnessed because the blocker is still renewal burden rather than missing product shape.

## rev0485 — add kernel interface contracts so top-band kernels have explicit command/file/schema surfaces
This revision is a **kernel-interface-contract + machine-surface** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to the next practical question after kernel slices:
**once the repo knows what a bounded v0 contains and what lands first inside it, what exact surface should an implementation expose so the kernel is buildable without telepathy?**

The new notes are:
- `design/epic-contribution-kernel-interface-contracts-2026Q1.md`
- `meta/KERNEL_INTERFACE_CONTRACT_PROTOCOL.md`

The new contract corpus is:
- `contracts/top-band-v0/build-state-pack.contract0.md`
- `contracts/top-band-v0/debug-acceptance-matrix.contract0.md`
- `contracts/top-band-v0/package-intake-review-kit.contract0.md`
- `contracts/top-band-v0/safety-critical-readiness-cards.contract0.md`

Why this refresh was merited:
- the repo already had ranking, packets, dossiers, live packets, kernel briefs, and slice plans, but still lacked an **explicit first contract surface**;
- fresh Rust signals still reward documented machine-facing seams and careful separation of stable versus experimental imports;
- current Cargo, debugging, package-security, and safety-critical signals all point toward contract-bearing local tools and commons rather than speculative platform layers; and
- future assistants needed a way to stop re-inventing command verbs, schema families, and receipt posture from memory.

Archive decision:
- new design note: `design/epic-contribution-kernel-interface-contracts-2026Q1.md`
- new meta protocol: `meta/KERNEL_INTERFACE_CONTRACT_PROTOCOL.md`
- new contract corpus: `contracts/top-band-v0/*`
- contract-corpus hygiene refresh: `contracts/README.md`, `contracts/top-band-v0/README.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the missing new layer is **kernel interface contracts**, not another ranking rewrite;
- **Build-State Evidence** remains the clearest first serious build and now also has the clearest contract0 for capture/diff/doctor surfaces;
- **Feedback / Debug Acceptance Commons** remains the clearest second serious build and now also has the clearest tuple/session/replay contract0;
- **Package Intake + Release Boundary Review** remains the urgent bridge and now also has the clearest local review/waive/quarantine/drill contract0;
- **Safety-Critical + Institutional Readiness Commons** remains the clearest stewarded long-horizon seam and now also has the clearest lint/pack/diff readiness-card contract0; and
- **Navigation / Defaults / Claims Commons** remains intentionally un-contractized because the blocker is still renewal burden rather than interface imagination.

## rev0484 — add kernel slices so top-band kernels have real first milestones, not just repo shapes
This revision is a **kernel-slice + thin-implementation-milestone** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to the next practical question after kernel briefs:
**once the repo knows what a bounded v0 should contain, what lands first inside that v0 so the kernel proves something real before it expands?**

The new notes are:
- `design/epic-contribution-kernel-slices-2026Q1.md`
- `meta/KERNEL_SLICE_PROTOCOL.md`

The new slice corpus is:
- `slices/top-band-v0/build-state-pack.slice0.md`
- `slices/top-band-v0/debug-acceptance-matrix.slice0.md`
- `slices/top-band-v0/package-intake-review-kit.slice0.md`
- `slices/top-band-v0/safety-critical-readiness-cards.slice0.md`

Why this refresh was merited:
- the repo already had ranking, reference architectures, charters, stage gates, packets, dossiers, live packets, and kernel briefs, but still lacked a **first milestone inside the v0**;
- fresh Rust signals still reward thin local proof over platform ambition;
- current Cargo, debugging, package-security, and safety-critical signals all point toward bounded slices with replayable artifacts rather than big-launch products; and
- future assistants needed a way to stop re-inventing “phase one” from memory for the same kernels.

Archive decision:
- new design note: `design/epic-contribution-kernel-slices-2026Q1.md`
- new meta protocol: `meta/KERNEL_SLICE_PROTOCOL.md`
- new slice corpus: `slices/top-band-v0/*`
- slice-corpus hygiene refresh: `slices/README.md`, `slices/top-band-v0/README.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the missing new layer is **first bounded milestones inside top-band kernels**, not another ranking rewrite;
- **Build-State Evidence** remains the clearest first serious build and now also has the clearest thin first milestone;
- **Feedback / Debug Acceptance Commons** remains the clearest second serious build and now also has the clearest fixture/replay-first slice;
- **Package Intake + Release Boundary Review** remains the urgent bridge and now also has the clearest route-profile / receipt / drill first slice;
- **Safety-Critical + Institutional Readiness Commons** remains the clearest stewarded long-horizon seam and now also has the clearest schema + lint + exemplar first slice; and
- **Navigation / Defaults / Claims Commons** remains intentionally unsliced because the blocker is still renewal burden rather than milestone imagination.

## rev0483 — add v0 kernel briefs so the top band has first honest shipsets, not just packets and dossiers
This revision is a **v0-kernel-brief + first-build-shape** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to the next practical question after live decision packets:
**once the repo knows what it would decide today, what should a real bounded v0 repo actually contain for the candidates that have earned a first build?**

The new notes are:
- `design/epic-contribution-v0-kernel-briefs-2026Q1.md`
- `meta/V0_KERNEL_BRIEF_PROTOCOL.md`

The new kernel corpus is:
- `kernels/top-band-v0/build-state-pack.v0.md`
- `kernels/top-band-v0/debug-acceptance-matrix.v0.md`
- `kernels/top-band-v0/package-intake-review-kit.v0.md`
- `kernels/top-band-v0/safety-critical-readiness-cards.v0.md`

Why this refresh was merited:
- the repo already had ranking, macro-programs, reference architectures, charters, stage gates, packets, specimens, dossiers, and live decision packets, but still lacked a **first-build / first-shipset layer**;
- fresh Rust signals still reward bounded companion tools, corpora, and commons over new framework empires;
- the archive needed to distinguish candidates that have earned kernelization from candidates that are still rightly blocked by renewal burden; and
- future assistants needed a way to stop re-inventing repo trees, command surfaces, and proof assets for the same top candidates.

Archive decision:
- new design note: `design/epic-contribution-v0-kernel-briefs-2026Q1.md`
- new meta protocol: `meta/V0_KERNEL_BRIEF_PROTOCOL.md`
- new kernel corpus: `kernels/top-band-v0/*`
- kernel-corpus hygiene refresh: `kernels/README.md`, `kernels/top-band-v0/README.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the missing new layer is **v0 kernel briefs / first-build discipline**, not another ranking rewrite;
- **Build-State Evidence** remains the clearest first serious build and now also has the clearest first repo shape;
- **Feedback / Debug Acceptance Commons** remains the clearest second serious build and now also has the clearest fixture/replay/matrix kernel;
- **Package Intake + Release Boundary Review** remains the urgent bridge and now also has the clearest operator-local review-kit kernel;
- **Safety-Critical + Institutional Readiness Commons** remains the clearest stewarded long-horizon seam and now also has the clearest validated-card commons kernel; and
- **Navigation / Defaults / Claims Commons** remains intentionally un-kernelized because its blocking factor is still renewal burden rather than missing product imagination.

## rev0482 — add live decision packets so the top band has current verdict artifacts, not just dossiers and specimens
This revision is a **live-decision-packet + current-verdict-corpus** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to the next practical question after dossiers:
**once the repo knows the leaders and keeps current working cards for them, where should it keep the actual packet a maintainer should read to decide `advance`, `deepen`, or `hold` today?**

The new notes are:
- `design/epic-contribution-live-decision-packets-2026Q1.md`
- `meta/LIVE_DECISION_PACKET_PROTOCOL.md`

The new live decision-packet corpus is:
- `packets/top-band-v0/build-state-evidence.advance.current.md`
- `packets/top-band-v0/debug-acceptance.deepen.current.md`
- `packets/top-band-v0/navigation-defaults.hold.current.md`
- `packets/top-band-v0/package-intake.advance.current.md`
- `packets/top-band-v0/safety-critical-readiness.deepen.current.md`

Why this refresh was merited:
- the repo already had ranking, macro-programs, reference architectures, charters, stage gates, packet rules, specimen packets, and live dossiers, but still lacked a **current explicit verdict artifact** for the top band;
- fresh Rust signals still support a small number of serious seams rather than a new magical framework;
- Cargo build analysis, report work, build-dir-layout changes, crates.io provenance/security work, registry-route advisories, and safety-critical readiness all reward packet-shaped judgment more than fresh broad prose; and
- future assistants needed a way to say what the repo would actually decide now without reconstructing verdict posture from several notes.

Archive decision:
- new design note: `design/epic-contribution-live-decision-packets-2026Q1.md`
- new meta protocol: `meta/LIVE_DECISION_PACKET_PROTOCOL.md`
- new packet corpus: `packets/top-band-v0/*`
- packet-corpus hygiene refresh: `packets/README.md`, `packets/top-band-v0/README.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the missing new layer is **live current decision packets**, not another ranking rewrite;
- **Build-State Evidence** remains the clearest first serious build and now also has the clearest current `advance` packet;
- **Feedback / Debug Acceptance Commons** remains the clearest second serious build and now also has the clearest current `deepen` packet;
- **Navigation / Defaults / Claims Commons** remains the clearest widener and now also has the clearest current `hold` packet;
- **Package Intake + Release Boundary Review** remains the urgent bridge and now also has the clearest operator-shaped current `advance` packet;
- **Safety-Critical + Institutional Readiness Commons** remains the clearest stewarded long-horizon seam and now also has the clearest current `deepen` packet; and
- future packet-heavy revisions should now refresh the nearest live packet before inventing another broad memo.

## rev0481 — add live candidate dossiers so the top band has current working cards, not just theory and specimens
This revision is a **candidate-dossier + live-posture** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit answer to the next practical question after packet specimens:
**once the repo knows what a good packet looks like, where should it keep the current working posture of the real top-band candidates so future revisions stop reconstructing them from scattered notes?**

The new notes are:
- `design/epic-contribution-candidate-dossiers-2026Q1.md`
- `meta/CANDIDATE_DOSSIER_PROTOCOL.md`

The new dossier corpus is:
- `dossiers/top-band-v0/build-state-evidence.current.md`
- `dossiers/top-band-v0/debug-acceptance.current.md`
- `dossiers/top-band-v0/navigation-defaults.current.md`
- `dossiers/top-band-v0/package-intake.current.md`
- `dossiers/top-band-v0/safety-critical-readiness.current.md`

Why this refresh was merited:
- the repo already had ranking, macro-programs, reference architectures, charters, stage gates, packet rules, and specimen packets, but still lacked a **live working dossier layer** for the actual leaders;
- fresh Rust signals still reward owner-shaped, packet-shaped, proving-ground-aware work rather than new grand synthesis: the 2026 goals process emphasizes owners, champions, and accepting teams; build-analysis and build-dir-layout work are still active and incomplete; Cargo still emphasizes narrow machine-usable seams while listing key plumbing/supply-chain work without progress; and safety-critical plus Foundation strategy sources keep reinforcing maintenance realism and institution-shaped stewardship;
- the archive's next failure mode was clear: future revisions could keep sounding correct while silently rebuilding the top band's live posture from memory each time; and
- dossiers are the smallest new layer that fixes that failure without turning into another shortlist or portal.

Archive decision:
- new design note: `design/epic-contribution-candidate-dossiers-2026Q1.md`
- new meta protocol: `meta/CANDIDATE_DOSSIER_PROTOCOL.md`
- new dossier corpus: `dossiers/top-band-v0/*`
- dossier-hygiene refresh: `dossiers/README.md`
- routing refresh: `AGENTS.md`, `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the missing new layer is **live top-band candidate dossiers**, not another ranking rewrite;
- **Build-State Evidence** remains the clearest first serious build and now also has the clearest live `advance` dossier;
- **Feedback / Debug Acceptance Commons** remains the clearest second serious build and now also has the clearest live `deepen` dossier;
- **Navigation / Defaults / Claims Commons** remains the clearest widener and now also has the clearest live `hold` dossier;
- **Package Intake + Release Boundary Review** remains the urgent bridge and now also has the clearest operator-shaped live `advance` dossier;
- **Safety-Critical + Institutional Readiness Commons** remains the clearest stewarded long-horizon seam and now has a stricter live `deepen` dossier; and
- future packet-heavy revisions should start from the nearest dossier before writing new packet prose.


## rev0480 — add review-packet specimens plus provenance guards so the repo can show what a real packet looks like
This revision is a **packet-specimen + provenance-guard** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for the next practical question after packet theory:
**once the repo knows what a good packet should contain, what tiny set of filled-out specimen packets should it keep so future revisions stop re-inventing packet shape, verdict burden, and evidence candor from scratch?**

The new notes are:
- `design/epic-contribution-review-packet-specimens-2026Q1.md`
- `meta/REVIEW_PACKET_SPECIMEN_PROTOCOL.md`

The new specimen corpus is:
- `specimens/review-packets-v0/build-state-evidence.advance.example.md`
- `specimens/review-packets-v0/debug-acceptance.deepen.example.md`
- `specimens/review-packets-v0/navigation-defaults.hold.example.md`
- `specimens/review-packets-v0/package-intake.advance.example.md`

Why this refresh was merited:
- the repo already had packet theory, stage gates, charters, and reference architectures, but still lacked a **real filled-out packet corpus**;
- current Rust signals still support different verdict postures across the top band: build evidence looks ready for bounded advancement, debugging still wants deeper tuple truth, recommendation/default layers need hold discipline, and package-intake work has route-real operator momentum;
- the March 2026 Rust challenges post now also gives the archive a direct provenance lesson because its original LLM-assisted draft was retracted, which raises the value of source-candor notes and anti-summary-theater rules;
- and future LLM-assisted revisions needed a concrete way to preserve caveats, unstable-surface warnings, and missing-proof honesty instead of just sounding coherent.

Archive decision:
- new design note: `design/epic-contribution-review-packet-specimens-2026Q1.md`
- new meta protocol: `meta/REVIEW_PACKET_SPECIMEN_PROTOCOL.md`
- new specimen corpus: `specimens/review-packets-v0/*`
- specimen-hygiene refresh: `specimens/README.md`, `meta/SPECIMEN_CORPUS_PROTOCOL.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the missing new layer is **filled-out packet specimens with source-provenance discipline**, not another ranking rewrite;
- **Build-State Evidence** remains the clearest first serious build and now also the clearest `advance` specimen;
- **Feedback / Debug Acceptance Commons** remains the clearest second serious build and now also the clearest `deepen` specimen;
- **Navigation / Defaults / Claims Commons** remains the clearest widener and now also the clearest `hold` specimen;
- **Package Intake + Release Boundary Review** remains the urgent bridge and now also the clearest operator-shaped second `advance` specimen; and
- future packet-heavy revisions should now deepen or refresh the nearest specimen before inventing new local packet grammar.


## rev0479 — add a standard review-packet layer so the repo can compare, advance, merge, or kill top programs without drift
This revision is a **review-packet + verdict-discipline** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a practical editorial question that remained too scattered across scorecards, reference architectures, charters, pilots, and stage gates:
**when a worthy Rust ecosystem program comes up for comparison or action, what packet should reviewers actually read, what verdicts are allowed, and what must remain visible before the repo advances, merges, folds, holds, or kills it?**

The new notes are:
- `design/epic-contribution-review-packets-2026Q1.md`
- `meta/PROGRAM_REVIEW_PACKET_PROTOCOL.md`

Why this refresh was merited:
- the latest public Rust signals still point to a handful of serious programs rather than one missing universal framework;
- the repo already had ranking, practical build-shape, macro-program, reference-architecture, charter, and stage-gate notes, but still lacked one direct **what should reviewers read before changing their minds?** answer;
- current Cargo and Rust governance signals keep rewarding machine-readable packs, bounded companion tools, milestones, and owner-visible proof rather than summary-driven portfolio churn; and
- after the stage-gate pass, the next archive failure mode was clearly **top programs being compared or widened with different hidden criteria each revision**.

Archive decision:
- new design note: `design/epic-contribution-review-packets-2026Q1.md`
- new meta protocol: `meta/PROGRAM_REVIEW_PACKET_PROTOCOL.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the missing new layer is **review-packet / verdict discipline**, not another ranking rewrite;
- **Evidence Spine / Build-State Evidence** remains the clearest first program and now also the clearest first candidate that should be carried by one strong packet rather than repeated summaries;
- **Feedback / Debug Acceptance Commons** remains the clearest second program and now also the clearest candidate whose packet must show tuple posture, unsupported states, and exportable support bundles;
- **Navigation / Defaults / Claims Commons** remains the clearest widener and now also the clearest candidate that must carry freshness, renewal, and anti-winner-table clauses in every packet;
- **Package Intake + Release Boundary Review** remains the urgent bridge and now also the clearest candidate that should never move without route-real, local-first operator packets; and
- **Safety-Critical + Institutional Readiness Commons** remains the clearest stewarded long-horizon seam and now also the clearest candidate whose packet must foreground shared ownership, evidence recipes, and contract limits.


## rev0478 — add a stage-gate layer so the repo can answer “when is a worthy program actually allowed to get bigger?”
This revision is a **stage-gate + proof-budget** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a practical question that remained too scattered across sequencing, charter, reference-architecture, and pilot-evaluation notes:
**once a worthy Rust ecosystem program is real enough to exist, what stages should it pass through, what proof budget has it earned, what next gate justifies widening it, and what larger promises are still premature?**

The new notes are:
- `design/epic-contribution-stage-gates-and-proof-budgets-2026Q1.md`
- `meta/PROGRAM_STAGE_GATE_PROTOCOL.md`

Why this refresh was merited:
- the latest public Rust signals keep pointing to a small number of serious programs rather than one missing framework;
- the repo already had ranking, practical build-shape, macro-program, reference-architecture, and program-charter notes, but still lacked one direct **when may this program widen?** answer;
- current official substrate work keeps modeling bounded staged progress: prototyping, unstable surfaces, testing calls, milestones, and owner updates rather than one-shot universal launches; and
- after the charter pass, the next archive failure mode was clearly **good programs widening faster than their proof**.

Archive decision:
- new design note: `design/epic-contribution-stage-gates-and-proof-budgets-2026Q1.md`
- new meta protocol: `meta/PROGRAM_STAGE_GATE_PROTOCOL.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the missing new layer is **stage-gate / proof-budget discipline**, not another ranking rewrite;
- **Evidence Spine / Build-State Evidence** remains the clearest first program and now also the clearest example of a program that should earn widening one gate at a time;
- **Feedback / Debug Acceptance Commons** remains the clearest second program and now also the clearest example of stage-2 tuple widening;
- **Navigation / Defaults / Claims Commons** remains the clearest widener and now also the clearest example of why recommendation layers must widen slower than they are described;
- **Package Intake + Release Boundary Review** remains the urgent bridge and now also the clearest example of why incident-real route truth must precede broader policy asks; and
- **Safety-Critical + Institutional Readiness Commons** remains the clearest stewarded long-horizon seam and now also the clearest example of why some worthy programs should face the strictest stage discipline.

## rev0477 — add a charter layer so the repo can answer “how does this worthy program become real?”
This revision is a **program-charter + operating-rail** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a practical question that remained too scattered across sequencing, decision-rights, support-bundle, and reference-architecture notes:
**once a top Rust ecosystem program is clearly worthy and technically specified, what launch charter makes it real enough to start, survive, and widen honestly?**

The new notes are:
- `design/epic-contribution-program-charters-2026Q1.md`
- `meta/PROGRAM_CHARTER_PROTOCOL.md`

Why this refresh was merited:
- the latest public Rust signals still point to a small number of serious programs rather than one missing framework;
- the repo had strong rank, practical-shape, macro-program, and reference-architecture notes, but still lacked a direct **owner-shape / residency / pilot-partner / maintenance-envelope** answer;
- the Rust goals process, task-owner rules, maintenance writeup, and Foundation strategy all reinforce that worthwhile work becomes real only when owners, support, and upkeep are explicit; and
- after the program-spec pass, the next archive failure mode was clearly **good technical designs with vague launch charters**.

Archive decision:
- new design note: `design/epic-contribution-program-charters-2026Q1.md`
- new meta protocol: `meta/PROGRAM_CHARTER_PROTOCOL.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- source-atlas refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the missing new layer is **program charter / execution realism**, not another ranking rewrite;
- **Evidence Spine** remains the clearest first program and now also the clearest **companion-first + pilot-partnered + narrowly-upstreamed** program;
- **Feedback / Debug Acceptance Commons** remains the clearest second program and now also the clearest **cross-tool steward-group** program;
- **Navigation / Defaults / Claims Commons** remains the clearest widener and now also the clearest **editorial-with-renewal** program;
- **Package Intake + Release Boundary Review** remains the urgent bridge and now also the clearest **operator-owned local-first** program; and
- **Safety-Critical + Institutional Readiness Commons** remains the clearest **consortium / shared-owner** program.

## rev0476 — add a reference-architecture layer so the repo can answer “what must each top program actually contain?”
This revision is a **reference-architecture + program-spec** pass.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a construction question that remained too scattered across macro-program and execution-blueprint notes:
**once the strongest worthy Rust contributions are grouped into macro-programs, what are their minimum viable kernels, import surfaces, proof assets, proving grounds, v0 scopes, exit criteria, and refusal clauses?**

The new notes are:
- `design/epic-contribution-reference-architectures-2026Q1.md`
- `meta/PROGRAM_SPEC_DEEPENING_PROTOCOL.md`

Why this refresh was merited:
- the latest public Rust signals still point to evidence flows, debugger acceptance, package-boundary review, and safety/institutional readiness rather than one missing framework;
- the repo had strong rank, practical-shape, and macro-program notes, but still lacked a direct **spec-first answer** for what each serious program actually contains;
- Cargo build-analysis, build-dir-layout, crates.io/security, and 2026 flagship work all make interfaces, proof assets, and proving grounds more important than another broad top-ten note; and
- after the dedup pass, the next archive failure mode was clearly **program names without kernels or exit criteria**.

Archive decision:
- new design note: `design/epic-contribution-reference-architectures-2026Q1.md`
- new meta protocol: `meta/PROGRAM_SPEC_DEEPENING_PROTOCOL.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the missing new layer is **reference architecture / program-spec discipline**, not another ranking rewrite;
- **Evidence Spine** remains the clearest first macro-program and now also the clearest first program whose kernel, imports, proof assets, and exit criteria should guide later work;
- **Feedback / Debug Acceptance Commons** remains the clearest second macro-program and should be specified around tuple records, async acceptance, and exportable session packs rather than one debugger surface;
- **Navigation / Defaults / Claims Commons** remains the clearest widener and should be specified around renewable lane cards and claim packs rather than winner tables;
- **Package Intake + Release Boundary Review** remains the urgent bridge and should be specified around extraction, quarantine, waiver, replay, and release-boundary receipts;
- **Safety-Critical + Institutional Readiness Commons** remains the clearest stewarded program seam and should be specified around readiness profiles and evidence recipes; and
- future deepening should usually route through `design/epic-contribution-reference-architectures-2026Q1.md` and `meta/PROGRAM_SPEC_DEEPENING_PROTOCOL.md` before inventing another broad synthesis layer.

## rev0475 — collapse the top band into macro-programs and add a dedup rail so the repo becomes worthier instead of merely larger
This revision is a **program-stack + pruning + continuity-rail pass**.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a practical repo-construction question that the prior synthesis notes still left too scattered:
**which strongest-worthy contributions should be treated as macro-programs, which ideas should be folded under them, and how should the archive avoid duplicating broad synthesis every time it learns something new?**

The new notes are:
- `design/epic-contribution-program-stack-2026Q1.md`
- `meta/BROAD_SYNTHESIS_DEDUP_PROTOCOL.md`

Why this refresh was merited:
- the latest public Rust signals still point to a smaller number of real program-shaped gaps than the raw proposal count suggests;
- the repo had strong rank, scorecard, and practical-shape notes, but no clear **macro-program / fold / eliminate / worthy-repo construction** note;
- package-boundary and provenance caveats keep showing that boundary-review work must stay explicit rather than dissolve into recommendation or release prose;
- docs remain canonical while LLM/editor mediation rises, which makes broad-synthesis dedup and routing discipline more important, not less; and
- the archive needed a sharper rule for when a fresh broad note is actually merited versus when an existing note or blueprint should simply be deepened.

Archive decision:
- new design note: `design/epic-contribution-program-stack-2026Q1.md`
- new meta protocol: `meta/BROAD_SYNTHESIS_DEDUP_PROTOCOL.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- continuity/meta-hygiene refresh: `meta/LATEST_REVISION_FILESET.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research refresh: `RESEARCH_LOG.md`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- the missing new layer is **macro-program / fold / worthy-repo construction discipline**, not another rank rewrite;
- **Evidence Spine** is now the clearest first macro-program and folds Build-State Evidence plus the thin machine-facing multipliers beneath it;
- **Feedback / Debug Acceptance Commons** is now the clearest second macro-program and folds most session/debug/defect-acceptance work beneath it;
- **Navigation / Defaults / Claims Commons** is now the clearest widener macro-program;
- **Package Intake + Release Boundary Review** remains the clearest urgent bridge macro-program; and
- **Safety-Critical + Institutional Readiness Commons** remains the clearest program/consortium macro-program.

## rev0474 — add a practical build menu so the archive can answer “what should we actually build?” without drifting into framework or dashboard theater
This revision is a **practical-build-menu + continuity-fileset pass**.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a broad question that remained too scattered across scorecards and execution blueprints:
**once the strongest worthy Rust contributions are already known, what concrete library, tool, pack, commons, or program shapes should a serious team actually build next — and which popular instincts should be killed instead of widened?**

The new synthesis note is:
- `design/practical-epic-contribution-briefs-2026Q1.md`

Why this refresh was merited:
- the March 2026 challenges writeup keeps the pain on async difficulty, tacit-knowledge/choice-paralysis, and immature domain support rather than on one missing framework;
- the 2025 State of Rust survey keeps resource usage and debugging high while docs remain canonical even as editor/LLM mediation rises;
- Cargo build-analysis and build-dir-layout work make report/pack and shared-cache truth more concrete than another generic build-product fantasy;
- the debugging survey makes the debugger seam look like an acceptance commons, not a one-plugin gap;
- the safety-critical writeup reinforces that some of the most valuable seams are really stewarded programs and readiness commons rather than crates; and
- the archive itself needed a faster continuity answer for “what files moved in the latest broad synthesis pass?” so future assistants do not pay a full diff tax.

Archive decision:
- new design note: `design/practical-epic-contribution-briefs-2026Q1.md`
- new continuity ledger: `meta/LATEST_REVISION_FILESET.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- meta-hygiene refresh: `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research/source refresh: `RESEARCH_LOG.md`, `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun archive doctor

Interpretation:
- the broad ladder is unchanged;
- **Build-State Evidence** remains the strongest one-team first build and should default to **report/pack** shape;
- **Feedback Loop / Debuggability Acceptance** remains the clearest second serious build and should default to **acceptance-commons + session-pack** shape;
- **Adoption Navigation + Ecosystem Atlas + renewal receipts** remains the clearest reviewable recommendation widener;
- **Tooling Contract**, **Semantic Context**, and **Shared Spine** remain the key multipliers;
- **Package Intake Gateway** remains the clearest urgent bridge; and
- **Safety-Critical Readiness Commons** remains the clearest program seam.

## rev0473 — add a learning-clock map so worthy contributions stop pretending every strong idea learns at the same speed
This revision is a **comparative-learning-clock + meta-hygiene pass**.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a question that stayed under-answered even after ranking, scorecards, delivery, incubation fit, proof burden, bet sizing, compounding, support bundles, renewal burden, distortion risk, boundary fit, decision rights, and reversibility:
**once a Rust ecosystem contribution is clearly worthy, how long does it take to get a trustworthy signal after a change — same day, per commit, per release train, per tuple matrix, per incident route, or per institutional review cycle?**

The new synthesis note is:
- `design/epic-contribution-learning-clock-map-2026Q1.md`

Why this refresh was merited:
- the compiler-performance survey and 2025 State of Rust results keep pointing at inner-loop pain, rebuild understanding, and practical time-to-truth problems rather than just abstract “performance matters” complaints;
- Cargo build-analysis work is explicitly about recording build metadata across invocations so developers can explain rebuilds and past timing;
- rustc-perf improvements are explicitly about compare-within-configuration discipline, collector health, and broader measurement coverage rather than one-off benchmarks;
- the build-dir layout testing call shows that some seams only learn honestly when downstream tools and users actually replay them;
- the debugging survey makes clear that debugger progress is a slower tuple-matrix acceptance problem, not a same-day one-machine truth seam;
- the crates.io policy update and March 2026 Cargo advisory show that package-ingress work often learns on an incident/operator clock unless it builds synthetic replays first; and
- the repo needed a sharper way to distinguish **importance**, **proof burden**, **renewal burden**, and **reversibility** from **time-to-truth / feedback tempo**.

Archive decision:
- new design note: `design/epic-contribution-learning-clock-map-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- meta-hygiene refresh: `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research/source refresh: `RESEARCH_LOG.md`, `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene/doctor

Interpretation:
- the broad ladder is unchanged;
- **Build-State Evidence** remains the strongest broad first build and now also the clearest **fast-learning first build**;
- **Semantic Context / Tooling Contract / Shared Spine** remain strongest when they **shorten later learning clocks** rather than becoming abstract schema empires;
- **Feedback Loop / Debuggability Acceptance** remains the clearest **slow tuple-matrix acceptance seam**;
- **Adoption Navigation + Ecosystem Atlas** remains strategically real but should widen only as fast as its evidence imports renew;
- **Compatibility Claims** remains a **rerun-and-release-train seam** rather than a one-shot proof seam;
- **Package Intake Gateway** remains the clearest **incident/route-owner seam** and therefore needs synthetic proving grounds;
- **Safety-Critical Readiness Commons** remains the clearest **institutional / slow-clock** seam; and
- future portfolio revisions should now state explicitly **the fastest truthful loop, the slower graduation loop, the synthetic proving ground, and the expiry boundary for current evidence**.

## rev0472 — add a reversibility map so worthy contributions stop pretending every good idea should launch as policy
This revision is a **comparative-reversibility + meta-hygiene pass**.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a question that stayed under-answered even after ranking, scorecards, delivery, incubation fit, proof burden, bet sizing, compounding, support bundles, renewal burden, distortion risk, boundary fit, and decision rights:
**once a Rust ecosystem contribution is clearly worthy, how safely should it begin, how much blast radius does it carry, and what kind of rollback or escape hatch must exist before it widens?**

The new synthesis note is:
- `design/epic-contribution-reversibility-map-2026Q1.md`

Why this refresh was merited:
- Cargo's external-tools and metadata posture keeps showing that bounded machine-facing surfaces enable reversible companion experimentation before Cargo-core ratchets appear;
- the Cargo 1.94 cycle reiterates that compatibility guarantees make core-tool defaults more expensive to change than companion layers;
- the Build Dir Layout v2 testing call shows that seemingly local toolchain changes can still create downstream blast radius and therefore need staged testing;
- the docs.rs default-target change is a concrete model of **default with explicit escape hatch**;
- `cargo fix` is a concrete model of high-value advisory automation that remains reviewable and reversible;
- the `cargo-semver-checks` goal is a concrete model of **default-on with override** rather than irreversible publish policy; and
- the repo needed a sharper way to distinguish **importance**, **decision rights**, and **boundary fit** from **how safely a contribution can be introduced and undone**.

Archive decision:
- new design note: `design/epic-contribution-reversibility-map-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- meta-hygiene refresh: `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research/source refresh: `RESEARCH_LOG.md`, `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene/doctor

Interpretation:
- the broad ladder is unchanged;
- **Build-State Evidence** remains the strongest broad first build and now also the clearest **advisory replayable probe**;
- **Semantic Context / Tooling Contract / Shared Spine** remain the clearest **reversible hidden multipliers**;
- **Adoption Navigation + Ecosystem Atlas** remains strongest as an **advisory/defaults commons** and should resist premature canonization;
- **Compatibility Claims** is now more clearly a **default-with-override** seam rather than an instant Cargo-law seam;
- **Package Intake Gateway** remains the clearest **staged operator-boundary** seam;
- **Feedback Loop / Debuggability Acceptance** remains a **fixture-first seam whose broad acceptance claims are expensive to ratchet**;
- **Safety-Critical Readiness Commons** remains the clearest **governance-grade ratchet** seam; and
- future portfolio revisions should now state explicitly **what survives rollback, what escape hatch exists, and what wrong ratchet the contribution must refuse**.

## rev0471 — add a decision-rights map so worthy contributions stop blurring local wins with coalition programs
This revision is a **comparative-decision-rights + meta-hygiene pass**.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a question that stayed under-answered even after ranking, scorecards, delivery, incubation fit, proof burden, bet sizing, compounding, support bundles, renewal burden, distortion risk, and boundary fit:
**once a Rust ecosystem contribution is clearly worthy, who actually has to agree before users feel value — one team, an upstream team, a service/operator owner, several tool owners, or a consortium?**

The new synthesis note is:
- `design/epic-contribution-decision-rights-map-2026Q1.md`

Why this refresh was merited:
- the 2026 goals overview and owners guidance make explicit that accepted work depends on champions, review support, and already-known resources;
- Cargo's external-tools posture, the Cargo plumbing goal, and the 1.93/1.94 cycle posts all show that some high-value work can create immediate local value as companion tooling without waiting for wholesale upstream agreement;
- `cargo clippy` provides a concrete middle case: an external command shipped with the toolchain as an optional component rather than Cargo core;
- the March 2026 challenges post and 2025 State of Rust survey reinforce that practical pain is broad but not blocked on the same people in every seam;
- the debugging survey makes clear that debugger progress is a cross-tool tuple problem rather than a unilateral plugin problem;
- the crates.io malicious-notification update and March 2026 Cargo advisory show that intake/security seams are operator- and route-shaped rather than just “one checker exists” shaped; and
- the repo needed a sharper way to separate **importance** from **who must agree before first value appears** so future passes stop budgeting coalition seams like local companion builds.

Archive decision:
- new design note: `design/epic-contribution-decision-rights-map-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- meta-hygiene refresh: `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research/source refresh: `RESEARCH_LOG.md`, `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene/doctor

Interpretation:
- the broad ladder is unchanged;
- **Build-State Evidence** remains the strongest broad first build and now also the clearest **low-consensus local-first** build;
- **Semantic Context / Tooling Contract / Shared Spine** remain the strongest **low-consensus hidden multipliers**;
- **Adoption Navigation + Ecosystem Atlas** remains a **medium-consensus editorial/defaults commons**;
- **Package Intake Gateway** remains the clearest **operator / route-owner** seam;
- **Feedback Loop / Debuggability Acceptance** remains the clearest **cross-tool tuple-consensus** seam;
- **Safety-Critical Readiness Commons** remains the clearest **consortium / standards-grade** seam; and
- future portfolio revisions should now state explicitly **who can benefit unilaterally, what extra value needs narrow upstream permission, and which seams are blocked on coalition agreement no matter how good one team's prototype is**.

## rev0470 — add a boundary-fit map so worthy contributions stop collapsing into “merge it into Cargo”
This revision is a **comparative-boundary-fit + meta-hygiene pass**.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a question that stayed under-answered even after ranking, scorecards, delivery, incubation fit, proof burden, bet sizing, compounding, support bundles, renewal burden, and distortion risk:
**once a Rust ecosystem contribution is clearly worthy, where should its value actually live — as a companion tool, a companion with narrow upstream asks, a consortium/editorial commons, an operator bridge, or an upstream substrate/stabilization program?**

The new synthesis note is:
- `design/epic-contribution-boundary-map-2026Q1.md`

Why this refresh was merited:
- Cargo's external-tools chapter and metadata docs still channel integration through bounded machine-facing surfaces rather than through Cargo becoming every workflow;
- the Cargo 1.93 and 1.94 development-cycle notes explicitly say Cargo can't be everything to everyone because of the compatibility guarantees it must uphold while simultaneously showing active work on report/plumbing/build-dir/artifact surfaces;
- the Cargo plumbing goal explicitly says to prototype a third-party subcommand to experiment with what Cargo should integrate;
- build-analysis and build-dir work make the value of narrow upstream hooks clearer while leaving richer evidence products better suited to companion layers;
- StableMIR / `rustc_public`, `build-std`, and Rust-for-Linux tooling are the opposite kind of signal: they are truly upstream substrate/stabilization work;
- and the repo needed a sharper way to separate **importance** from **residency** so future passes stop treating “important” as shorthand for “merge it upstream”.

Archive decision:
- new design note: `design/epic-contribution-boundary-map-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- meta-hygiene refresh: `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research/source refresh: `RESEARCH_LOG.md`, `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene/doctor

Interpretation:
- the broad ladder is unchanged;
- **Build-State Evidence** remains the strongest broad first build and now also the clearest **companion-first** build with narrower upstream asks;
- **Feedback Loop / Debuggability Acceptance** remains the clearest **consortium acceptance commons** rather than a one-plugin fantasy;
- **Adoption Navigation + Ecosystem Atlas** remains the clearest **editorial/default commons** and should not be collapsed into official stack ranking;
- **Tooling Contract**, **Shared Spine**, and **Semantic Context** remain major companion/reference multipliers rather than arguments for Cargo or rustc to absorb whole products;
- **Package Intake Gateway** remains the clearest **operator/security bridge**;
- **Safety-Critical Readiness Commons** remains the clearest **consortium/institutional commons**; and
- **StableMIR / `rustc_public`, `build-std`, and Rust-for-Linux tooling** remain the clearest cases where the right answer really is upstream substrate/stabilization work.

## rev0469 — add a distortion-risk map so worthy contributions cannot win by overclaiming
This revision is a **comparative-distortion-risk + meta-hygiene pass**.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a question that was still under-answered even after ranking, scorecards, delivery, incubation fit, proof burden, bet sizing, compounding, support bundles, and renewal burden:
**once a Rust ecosystem contribution is clearly worthy, how is it most likely to go wrong while still looking successful — by over-reading unstable surfaces, letting one tuple pose as coverage, letting projections outrun canon, turning best-effort provenance into fake certainty, or rewarding the wrong metric?**

The new synthesis note is:
- `design/epic-contribution-distortion-risk-map-2026Q1.md`

Why this refresh was merited:
- the March 2026 challenges post itself became evidence that generated summary layers can feel weaker than canon even when their underlying points are real;
- the 2025 State of Rust survey keeps docs canonical while editor/LLM mediation rises, which makes projection-versus-canon discipline a first-order ecosystem concern;
- Cargo's own docs distinguish stable/versioned JSON, human-readable output without compatibility guarantees, and best-effort VCS hints without verified provenance, which means several plausible ecosystem tools become dishonest exactly when they forget the strength of their imports;
- the build-dir goal, build-analysis goal, debugging survey, cargo-semver-checks work, rustc-perf guidance, and March 2026 Cargo advisory each expose a different false-success pattern the archive should now name explicitly;
- and the repo needed a sharper way to say that a contribution can be worth funding yet still be the wrong shape if its easiest success mode is a distortion machine.

Archive decision:
- new design note: `design/epic-contribution-distortion-risk-map-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- meta-hygiene refresh: `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research/source refresh: `RESEARCH_LOG.md`, `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene/doctor

Interpretation:
- the broad ladder is unchanged;
- **Build-State Evidence** remains the strongest broad first build and now also the clearest anti-distortion first build because its false-success modes can be constrained with lineage, configuration boundaries, and rerun receipts;
- **Feedback Loop / Debuggability Acceptance** remains the clearest second serious build and now also the clearest place to refuse one-tuple theater;
- **Adoption Navigation + Ecosystem Atlas** remains the clearest high-value widener and now also the clearest place to refuse projection-becomes-canon drift;
- **Tooling Contract**, **Shared Spine**, **Semantic Context**, and **Compatibility Claims** remain major multipliers and now also the clearest places to preserve surface strength and imported-versus-inferred separation;
- **Package Intake Gateway** remains the strongest boundary bridge and now also the clearest place to refuse trust-score theater;
- **Safety-Critical Readiness Commons** remains the clearest stewardship-heavy program seam and now also the clearest place to refuse readiness halo theater; and
- future portfolio revisions should now state explicitly **what false success looks like, what weak surface is being imported, and what artifact makes the contribution honest anyway**.

## rev0468 — add a renewal-burden map so worthy contributions carry an honest upkeep story
This revision is a **comparative-renewal-burden + meta-hygiene pass**.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a question that was still under-answered even after ranking, scorecards, delivery, incubation fit, proof burden, bet sizing, compounding, shared-spine execution, proving-world work, and support-bundle discipline:
**once a Rust ecosystem contribution is worthy, what recurring renewal burden does it create, at what cadence, what part can be automated, and what part needs durable human stewardship?**

The new synthesis note is:
- `design/epic-contribution-renewal-burden-map-2026Q1.md`

Why this refresh was merited:
- the 2026 goals overview and design axioms make accepted work a contract with champions, review, and support rather than an unbounded idea list;
- the January 2026 program-management update keeps pushing portfolio thinking toward real capacity and industry-backed roadmaps;
- the Maintainer Fund design post makes explicit that Rust maintenance is about keeping things working across daily nightly releases and six-week stable releases;
- the Foundation strategy now names sustainable maintenance as a first-class pillar;
- the March 2026 challenges post and 2025 survey results keep showing that build truth, debugging, docs, and ecosystem guidance are recurring practical taxes, not one-shot blog-post problems;
- the build-dir-layout testing call, debugging survey, crates.io policy change, Cargo advisory, and FLS-upkeep goal all show different **cadences of renewal** across tooling, tuple acceptance, security response, and consortium documents;
- and the repo needed a sharper way to say “cheap to launch” is not the same thing as “cheap to keep honest”.

Archive decision:
- new design note: `design/epic-contribution-renewal-burden-map-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- meta-hygiene refresh: `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research/source refresh: `RESEARCH_LOG.md`, `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene/doctor

Interpretation:
- the broad ladder is unchanged;
- **Build-State Evidence** remains the strongest broad first build and now also the strongest **renewal-aligned** first build because much of its recurring upkeep can be tied to exemplar replays and versioned receipts;
- **Feedback Loop / Debuggability Acceptance** remains the clearest **heavy tuple-renewal** build;
- **Adoption Navigation + Ecosystem Atlas** remains the clearest **heavy editorial-renewal** build;
- **Tooling Contract**, **Shared Spine**, **Compatibility Claims**, and narrow **Semantic Context** remain mostly **release-cadence + substrate-watch** renewal layers;
- **Package Intake Gateway** remains the clearest **operational / incident-renewal** bridge;
- **Safety-Critical Readiness Commons** remains the clearest **consortium-renewal** program seam; and
- future portfolio revisions should now state explicitly **what expires, what must be rerun, what part is automated, what part is human, and what false upkeep story is being refused**.

## rev0467 — add a support-bundle map so worthy contributions ask the ecosystem for the right things
This revision is a **comparative-support-bundle + meta-hygiene pass**.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a question that was still under-answered even after ranking, scorecards, delivery, incubation fit, proof burden, bet sizing, compounding, shared-spine execution, and proving-world work:
**once a Rust ecosystem contribution is worthy, what should it actually ask for from upstream teams, maintainers, vendors, operators, the Foundation, or a consortium — and what kinds of asks are category errors that would distort it?**

The new synthesis note is:
- `design/epic-contribution-support-bundle-map-2026Q1.md`

Why this refresh was merited:
- the 2026 goals overview and the owners guidance make owners, champions, and already-known resources part of honest acceptance rather than optional polish;
- the January 2026 program-management update says roadmaps and application areas are meant to focus industry funding and explicitly routes review through team capacity and champions;
- the Foundation strategy, annual-report/strategy post, Maintainers Fund, Community Grants support page, and Innovation Lab now make several distinct support vehicles real enough that the archive should stop saying only “fund this somehow”;
- the March 2026 challenges post, 2025 survey results, build-analysis work, debugging survey, safety-critical writeup, and March 2026 Cargo advisory keep proving that different seams need radically different support bundles to become honest;
- exemplar access, upstream review windows, operator/security participation, and consortium tuples are now often as important as money itself;
- and the repo needed a sharper way to say “who must say yes first, to what exact ask, and what not to ask for yet” without collapsing that into rank or bet size.

Archive decision:
- new design note: `design/epic-contribution-support-bundle-map-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- meta-hygiene refresh: `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- research/source refresh: `RESEARCH_LOG.md`, `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene/doctor

Interpretation:
- the broad ladder is unchanged;
- **Build-State Evidence** remains the strongest broad first build and now also the ripest **first support bundle**: companion-team budget + upstream liaison + exemplar donors;
- **Feedback Loop / Debuggability Acceptance** remains the clearest **consortium / interoperability ask bundle**;
- **Adoption Navigation + Ecosystem Atlas** remains an **editorial/defaults + renewal + exemplar** ask bundle, not a heavy institutional one;
- **Tooling Contract**, **Shared Spine**, **Compatibility Claims**, and narrow **Semantic Context** work remain mostly **companion-team + upstream-review + exemplar-consumer** asks;
- **Package Intake Gateway** remains an **operator/security boundary** ask bundle;
- **Safety-Critical Readiness Commons** remains the clearest **consortium/institution** ask bundle; and
- future portfolio revisions should now state explicitly **who must say yes first, what support is being requested, what is intentionally not being requested yet, and what artifact or proof lane justifies the ask**.

## rev0465 — turn “shared spine first” into a concrete worthy contribution
This revision is a **stage-0 execution + meta-hygiene pass**.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a question that was still under-answered even after ranking, scorecards, delivery, incubation fit, proof burden, bet sizing, compounding, sequencing, and portfolio artifact conventions:
**if the archive says “shared spine first”, what should that actually become before later evidence, boundary-bridge, and widener layers depend on it?**

The new synthesis note is:
- `design/shared-spine-execution-blueprint-2026Q1.md`

Why this refresh was merited:
- the March 2026 challenges post keeps clustering pain around recurring practical taxes, and its author's note about retracting an LLM-written first draft is unusually direct evidence that generated summaries should stay weaker than canonical artifacts;
- the 2025 State of Rust survey still says resource usage hurts while docs remain canonical and editor/LLM mediation rises;
- Cargo plumbing, build-analysis, build-dir-layout, and the 1.93/1.94 Cargo cycles keep saying machine-usable substrate is growing but still versioned, partial, and compatibility-sensitive;
- docs.rs rustdoc JSON, libtest JSON, and StableMIR / `rustc_public` progress keep reinforcing the need for compatibility gates and lineage receipts rather than one opaque cache;
- package-ingress security posture keeps proving that route/extraction review layers need to share the same honesty grammar as broader ecosystem evidence work; and
- the Foundation strategy and Innovation Lab make infrastructure stewardship shapes real, but still too selective to justify turning a stage-0 shared spine into a giant institution-shaped platform by default.

Archive decision:
- new design note: `design/shared-spine-execution-blueprint-2026Q1.md`
- execution-routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- stage-0 clarity refresh: `design/portfolio-artifact-conventions-2026Q1.md`, `design/portfolio-execution-sequencing-2026Q1.md`
- meta-hygiene refresh: `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`
- source refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene/doctor

Interpretation:
- the broad ladder is unchanged;
- **Build-State Evidence** remains the strongest broad first build;
- the new note makes **Shared Spine Contract Kit** the archive's concrete answer for stage-0 portfolio glue: a thin envelope, lineage receipt, compatibility gate, validator/linter, fixture corpus, and bounded brief/assistant-slice family;
- the archive should now keep **canonical pack**, **brief/handoff**, **verify receipt**, **lineage receipt**, and **assistant slice** visibly separate;
- the shared spine should begin as a bootstrap companion protocol + validator + fixtures project, not a hosted registry or Cargo replacement;
- and future revisions should now answer explicitly what is shared, what is seam-specific, which compatibility gates apply, and how assistant-facing slices remain weaker than canon.

## rev0464 — add a compounding map so worthy contributions are judged by what they unlock
This revision is a **comparative-compounding + meta-hygiene pass**.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a question that was still under-answered even after ranking, scorecards, delivery, incubation fit, proof burden, bet sizing, and generic sequencing:
**which worthy Rust ecosystem contributions are actually unlock bets for later ones, which ones are contract multipliers, which ones are consumer wideners, which ones are late program seams, and which upstream efforts should be treated as substrate unlocks rather than public-platform epics?**

The new synthesis note is:
- `design/epic-contribution-compounding-map-2026Q1.md`

Why this refresh was merited:
- the March 2026 challenges writeup keeps clustering pain around recurring practical taxes, which favors reusable unlocks over premature front-door products;
- the 2025 State of Rust survey keeps saying docs remain canonical while editor/LLM mediation rises, which favors stronger reusable artifacts beneath later guidance layers;
- the compiler-performance survey plus Cargo build-analysis, build-dir testing, and the 1.94 Cargo cycle keep making Build-State Evidence look like the strongest first unlock rather than merely a standalone tool idea;
- `relink-don't-rebuild`, docs.rs rustdoc JSON, `cargo-semver-checks`, and StableMIR / `rustc_public` progress keep proving that semantic and change-impact substrates now matter more as compounding inputs;
- the debugging survey keeps proving that debugging work is an acceptance-corpus unlock rather than a one-IDE feature race;
- and the 2026 flagships page plus the safety-critical writeup keep showing that later program seams should consume earlier compatibility, intake, and acceptance receipts instead of pretending to replace them.

Archive decision:
- new design note: `design/epic-contribution-compounding-map-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- meta-hygiene refresh: `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`
- source refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene/doctor

Interpretation:
- **Build-State Evidence** remains the strongest broad first build and is now also the clearest **first unlock**;
- **Semantic Context** remains the strongest hidden **substrate multiplier**;
- **Feedback Loop / Debuggability Acceptance** remains the clearest **acceptance unlock**;
- **Tooling Contract** remains a critical routing layer, but should usually import earlier exemplar packs rather than lead with pure abstraction;
- **Compatibility Claims** remains the strongest claims router once semantic and acceptance lanes exist;
- **Package Intake Gateway** remains the strongest operational bridge and should consume earlier artifact discipline;
- **Adoption Navigation** remains the first honest widener rather than the first unlock;
- **Safety-Critical Readiness Commons** remains a later compound program seam; and
- upstream efforts like Cargo build-analysis, build-dir work, relink, libtest JSON, StableMIR / `rustc_public`, and Rust-for-Linux stable tooling should now be treated more explicitly as **substrate unlocks** rather than fake standalone epics.

## rev0463 — add a bet-sizing map so worthy contributions are matched to honest capital bands
This revision is a **comparative-bet-sizing + meta-hygiene pass**.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a question that was still under-answered even after ranking, scorecards, delivery, incubation fit, and proof burden:
**what size and kind of bet is each worthy Rust ecosystem contribution actually asking for? Which ones fit direct maintainer sponsorship, which ones fit a bootstrap companion build, which need a staffed bridge, which require a consortium, and which should be funded upstream instead of productized sideways?**

The new synthesis note is:
- `design/epic-contribution-bet-sizing-map-2026Q1.md`

Why this refresh was merited:
- the January 2026 program-management update says goals are being reviewed against champions and capacity and that roadmaps/application areas are meant to focus industry funding;
- the project-goals owner guidance says goals without owners can only be provisional;
- the Rust Foundation's 2026–2028 strategy, Maintainers Fund, and 2026 project-priorities funding all make maintenance and mid-sized ecosystem support vehicles real rather than hypothetical;
- the Rust Innovation Lab proves there is now a keystone support vehicle for some funded projects, but not for every worthy seam;
- Cargo's plugin posture keeps validating bounded companion tools rather than “Cargo must be everything” dreams;
- build-analysis plus the compiler-performance survey keep making Build-State Evidence look like the strongest bootstrapable first bet;
- and the debugging and safety-critical writeups keep proving that some of the worthiest gaps are coalition- or institution-shaped rather than one-team product bets.

Archive decision:
- new design note: `design/epic-contribution-bet-sizing-map-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- meta-hygiene refresh: `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`
- source refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene/doctor

Interpretation:
- **Build-State Evidence** remains the strongest broad first build and now also the clearest **bootstrap companion bet**;
- **Feedback Loop / Debuggability Acceptance** remains the clearest **consortium / interoperability bet**;
- **Adoption Navigation + Ecosystem Atlas** remains the strongest **focused funded commons** once earlier evidence exists;
- **Package Intake Gateway** remains the strongest **operator-shaped funded bridge**;
- **Safety-Critical Readiness Commons** remains the clearest **keystone / consortium readiness program**;
- **Tooling Contract**, **Compatibility Claims**, and narrow **Semantic Context** work often fit **bootstrap companion** or **focused funded bridge** bands rather than giant platform bets;
- and substrate bets like **StableMIR / rustc_public**, **build-std**, **relink-don't-rebuild**, and **Rust-for-Linux stable tooling** should usually be treated as **upstream sponsorship or stabilization-program bets**, not as standalone product epics.

## rev0462 — add a proof-burden map so worthy contributions are judged by the right evidence
This revision is a **comparative-proof-discipline + meta-hygiene pass**.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a question that was still under-answered even after ranking, scorecards, delivery, and incubation fit:
**what does each worthy Rust ecosystem contribution actually have to prove, on what proving grounds, before it deserves widening, funding, or canon status as a serious ecosystem answer?**

The new synthesis note is:
- `design/epic-contribution-proof-burden-map-2026Q1.md`

Why this refresh was merited:
- the March 2026 challenges writeup keeps pointing to recurring ecosystem taxes rather than one-off novelty problems;
- the 2025 State of Rust survey says resource usage remains a major productivity issue, the debugging story still hurts enough to trigger a dedicated survey, docs remain canonical, and LLM/editor mediation is rising;
- Cargo build-analysis, build-dir-layout, and the March 2026 build-dir testing call make Build-State Evidence and adjacent tooling seams unusually measurable right now;
- docs.rs rustdoc JSON and cargo-semver-checks keep proving that several strong contributions have import-fidelity burdens rather than dashboard burdens;
- the March 2026 Cargo advisory plus the malicious-crate notification update keep proving that package-intake work lives at an operational boundary;
- the safety-critical writeup keeps proving that some strategically worthy contributions fail on owner and maintenance proof, not only on technical design;
- and the goals-owner guidance makes owner-backed proof part of the ecosystem's current execution reality.

Archive decision:
- new design note: `design/epic-contribution-proof-burden-map-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- meta-hygiene refresh: `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`
- source refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene/doctor

Interpretation:
- **Build-State Evidence** remains the strongest broad first build overall and now also has the ripest proof burden;
- **Feedback Loop / Debuggability Acceptance** remains the clearest second serious build, but must now be read through cross-tuple acceptance proof rather than generic tooling frustration;
- **Adoption Navigation + Ecosystem Atlas + renewal receipts** remains the strongest consumer-facing widening once earlier evidence exists, but must be judged by renewal honesty rather than curation volume;
- **Tooling Contract**, **Semantic Context**, and **Compatibility Claims** remain critical machine-facing layers whose burden is import fidelity and explicit lossiness posture;
- **Package Intake Gateway** remains the urgent operational bridge and now has a clearer fail-closed proof burden;
- **Safety-Critical Readiness Commons** remains the clearest institution-shaped program seam and now has a clearer consortium-readiness burden; and
- future comparative passes should keep **importance**, **delivery shape**, **incubation vehicle**, **proof family**, **proving ground**, and **graduation line** visibly separate.


## rev0461 — add an incubation map so worthy contributions start in the right vehicle
This revision is an **incubation-fit + meta-hygiene pass**.
It does **not** rerank the broad ladder and it does **not** promote a new frontier.
What changed is that the archive now has one explicit note for a question that was still under-answered even after the scorecards and delivery matrix:
**what kind of incubation vehicle should a worthy Rust ecosystem contribution actually begin in so it can land without being deformed by the wrong funding, governance, or ownership model?**

The new synthesis note is:
- `design/epic-contribution-incubation-map-2026Q1.md`

Why this refresh was merited:
- the January 2026 program-management update says roadmaps and application areas exist partly to focus outside funding;
- the Rust Foundation's 2026–2028 strategy explicitly prioritizes stable infrastructure and sustainable maintenance;
- the Rust Innovation Lab now provides a real maintainer-led keystone incubation vehicle;
- Cargo plumbing, build analysis, build-dir, and relink work keep validating companion-first substrate experiments rather than giant replacement platforms;
- Cranelift, build-std, and Rust-for-Linux stable-tooling work keep proving that some of Rust's most valuable contributions are roadmap substrates or stabilization programs rather than ordinary crates;
- and current package-security realities keep validating operational bridges rather than recommendation theater.

Archive decision:
- new design note: `design/epic-contribution-incubation-map-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- meta-hygiene refresh: `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`
- source refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene/doctor

Interpretation:
- **Build-State Evidence** remains the strongest first serious **companion-project** build;
- **Feedback Loop / Debuggability Acceptance** remains the clearest **consortium / interop** second build;
- **Adoption Navigation** remains an **editorial/defaults commons**;
- **Package Intake Gateway** remains an **operator-shaped operational bridge**;
- **Safety-Critical Readiness Commons** remains a **consortium-grade readiness program**;
- **Semantic Context / StableMIR**, **Cranelift local-dev acceleration**, **relink-don't-rebuild**, **build-std**, and **Rust-for-Linux stable-tooling** should now be read more explicitly as **roadmap substrates or stabilization programs**;
- and future comparative passes should keep **seam**, **artifact family**, **incubation vehicle**, **staffing/funding posture**, **exit path**, and **wrong starting vehicle** visibly separate.

## rev0460 — add a delivery matrix for top worthy contributions without changing the broad ladder
This revision is a **comparative-delivery + meta-hygiene pass**.
It does **not** promote a new frontier and it does **not** rewrite the broad ladder.
What changed is that the archive now has one explicit note for comparing the strongest candidates by the thing builders and funders actually need next: **what should ship first, who should own it, what proving grounds should it survive, and what wrong shape should be refused early**.

The new synthesis note is:
- `design/epic-contribution-delivery-matrix-2026Q1.md`

Why this refresh was merited:
- the March 2026 challenges writeup and the 2025 State of Rust survey keep pointing to broad recurring workflow taxes rather than one narrow gap;
- Cargo build-analysis/report work, build-dir-layout work, docs.rs rustdoc JSON, and cargo-semver-checks progress keep validating import-first evidence/reference layers rather than hosted dashboards or universal platform stories;
- the program-management update, the Rust Foundation's 2026–2028 strategy, the Rust Innovation Lab, and the maintenance writeup all make owner shape and maintenance shape too important to leave implicit;
- the safety-critical synthesis keeps showing that some of the worthiest contributions are only honest as shared-readiness programs rather than one crate;
- and the repo itself benefits from stronger anti-drift rules when a ranking answer is mistaken for a delivery plan.

Archive decision:
- new design note: `design/epic-contribution-delivery-matrix-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- meta-hygiene refresh: `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`
- source refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene/doctor

Priority interpretation:
- **Build-State Evidence** remains the strongest broad first build overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest second serious build;
- **Adoption Navigation + Ecosystem Atlas + renewal receipts** remains the strongest consumer-facing widening once earlier evidence exists;
- **Tooling Contract**, **Semantic Context**, and **Compatibility Claims** remain critical machine-facing multipliers or routing layers;
- **Package Intake Gateway** remains the urgent operational bridge;
- **Safety-Critical Readiness Commons** remains the clearest institution-shaped program seam; and
- future comparative passes should keep **delivery shape**, **owner shape**, **first shipped artifact family**, **proving grounds**, and **refused wrong shape** visibly separate.


## rev0459 — add comparative scorecards without rewriting the broad ladder
This revision is a **comparative-prioritization + meta-hygiene pass**.
It does **not** promote a new frontier and it does **not** rewrite the broad ladder again.
What changed is that the archive now has one explicit note for comparing the strongest candidates side-by-side without collapsing broad first-build value, second-build value, multiplier value, urgency, or consortium shape into one fake total score.

The new synthesis note is:
- `design/epic-contribution-scorecards-2026Q1.md`

Why this refresh was merited:
- the March 2026 challenges writeup keeps pointing to broad recurring taxes rather than one niche pain;
- the 2025 State of Rust survey keeps build/resource pain, debugging friction, canonical docs, and rising editor/LLM mediation in one frame;
- the compiler-performance survey and Cargo report/build-dir work keep validating build-state and machine-facing evidence seams;
- the debugging survey sharpens why feedback-loop acceptance is more than “better IDE support”;
- the safety-critical synthesis sharpens why some worthy contributions are really program seams;
- crates.io improvements plus the March 2026 Cargo advisory sharpen why package-intake work is urgent without automatically making it the broad #1;
- and the repo itself benefits from stronger anti-collapse rules when comparing strong candidates.

Archive decision:
- new design note: `design/epic-contribution-scorecards-2026Q1.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- meta-hygiene refresh: `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`
- source refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene/doctor

Priority interpretation:
- **Build-State Evidence** remains the strongest broad first build overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest second serious build;
- **Adoption Navigation + Ecosystem Atlas + renewal receipts** remains the strongest consumer-facing widening once earlier evidence exists;
- **Tooling Contract** and **Semantic Context** remain critical hidden multipliers, but for different layers;
- **Compatibility Claims** remains the key claim-routing seam;
- **Package Intake Gateway** is sharper as an urgent operational bridge;
- **Safety-Critical Readiness Commons** remains the clearest rising consortium/program seam; and
- future comparisons should keep **breadth**, **urgency**, **multiplier value**, **specialist weight**, and **steward shape** visibly separate.

## rev0458 — refresh the top portfolio order and add continuity rails without promoting a new frontier
This revision is a **ranking refresh + meta-hygiene pass**.
It does **not** promote a new frontier.
What changed is that the archive now says more directly which contributions deserve the next serious build/funding slots after re-reading the latest archive and current public Rust signals.

The new synthesis note is:
- `design/territory-priority-refresh-2026Q1.md`

The new meta-hygiene note is:
- `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`

Why this refresh was merited:
- the March 2026 challenges writeup keeps naming compile/resource pain, async difficulty, choice paralysis, and maturity gaps instead of one narrow language complaint;
- the 2025 State of Rust survey keeps build/resource pressure, debugging friction, canonical docs, and rising editor/LLM mediation in the same frame;
- the compiler-performance survey keeps validating Build-State Evidence and the broader feedback-loop story;
- the debugging survey makes it explicit that Rust still lacks a real multi-lane debug acceptance story;
- safety-critical work keeps proving that support, evidence, dependency lifecycle, async qualification, and interop boundaries are still underbuilt; and
- the archive itself now benefits from stronger continuity rails so future assistants do not silently rewrite canon from one synthesis pass.

Archive decision:
- new design note: `design/territory-priority-refresh-2026Q1.md`
- new meta note: `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`
- routing refresh: `AGENTS.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`
- memory-rail refresh: `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`
- source refresh: `atlases/portfolio-source-atlas-v0/sources.json`
- maintenance: mirror changed files under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, rerun hygiene/doctor

Priority interpretation:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** should now be treated as the clearest second-band build priority rather than only a missing-middle footnote;
- **Adoption Navigation + Ecosystem Atlas + renewal receipts** remains the strongest anti-tacit-knowledge answer;
- **Tooling Contract** remains the key machine-facing substrate;
- **Compatibility Claims** and **Safety-Critical Readiness Commons** rise as strategic program seams;
- and the archive should refuse generic crate-ranking portals, Cargo daemon dreams, release-bot empires, framework winner-hunting, and assistant-memory canonization faster than before.


## rev0457 — turn Tooling Contract into a real execution blueprint without inventing a new frontier
Instead of widening the archive again, this revision deepens one repeatedly promoted machine-facing seam that still lacked a direct “what should this actually ship?” answer: **Tooling Contract**.

The broad frontier map is unchanged, but the repo now has an explicit **Tooling Contract execution blueprint** for “what should ideal Rust actually build around discovery and package-selection truth, graph/plan truth, execution/build-state evidence, stability posture, adapter lossiness, and bounded consumer handoffs?” questions.

Why this deepening was merited:
- Rust’s 2026 flagships still keep **integrate Cargo into larger build systems** in the active Building Blocks agenda;
- Cargo’s plumbing goal still says current machine-facing surfaces are too porcelain-oriented, that `cargo metadata` excludes feature resolution, and that builds decompose into explicit phases from project discovery through final-artifact staging;
- Cargo’s stable external-tools story still centers on `cargo metadata`, `--message-format=json`, and custom subcommands rather than one coherent discovery → scope → plan → execute contract;
- Cargo now publicly separates final artifacts in `target-dir` from intermediate artifacts in `build-dir` while still calling build-dir layout internal and subject to change;
- the March 2026 build-dir-layout-v2 testing call explicitly says many projects rely on unspecified build-dir details because Cargo still lacks the right features;
- Cargo 1.94 kept structured logging, `cargo report rebuild`, `cargo report sessions`, and workspace/config discovery active while reiterating that plugins matter; and
- rust-analyzer still needs `cargo.targetDir` and non-Cargo override/`{label}` hooks, which is direct evidence that adapter lossiness and tool-specific workarounds remain real.

Archive decision:
- New design note: `design/tooling-contract-execution-blueprint-2026Q1.md`
- Design/contract refresh: `design/tooling-contract-stack.md`, `design/tooling-contract-pilot-program.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `proposals/epic-tooling-contract-stack.md`
- Canon/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Maintenance: mirror changed canon under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, and rerun the archive doctor

Strategy:
- keep the broad ranking intact;
- keep **Build-State Evidence** as the strongest one-project answer overall;
- keep **Feedback Loop / Debuggability Acceptance** as the clearest under-ranked missing middle;
- make **Tooling Contract** the clearest current **machine-facing Cargo composition / scope-plan-evidence / adapter-lossiness execution blueprint**;
- keep **Repo Composition**, **Build Interop**, and **Build-State Evidence** as imported owners beneath it rather than collapsing them; and
- refuse the tempting wrong shapes first: a Cargo daemon, a BSP-only standard, a target-dir scraper, or a giant monorepo control plane.

## rev0456 — turn Compatibility Claims into a real execution blueprint without inventing a new frontier
Instead of widening the archive again, this revision deepens one repeatedly promoted seam that still lacked a direct “what should this actually ship?” answer: **Compatibility Claims**.

The broad frontier map is unchanged, but the repo now has an explicit **Compatibility Claims execution blueprint** for “what should ideal Rust actually build around imported support-envelope truth, MSRV/toolchain compatibility, debugger/acceptance drift, public-boundary compatibility, and bounded docs/release/support/policy/safety handoffs?” questions.

Why this deepening was merited:
- rustc’s target-tier policy still makes support lanes formally distinct instead of flattening them into one verdict;
- docs.rs metadata, docs.rs builds, and the October 2025 target-default change make docs-target posture part of the public compatibility story;
- Cargo’s `rust-version` field and resolver behavior make MSRV/toolchain compatibility a real machine-visible claim surface;
- the safety-critical adoption writeup explicitly asks for target-focused readiness checklists and ecosystem-wide MSRV conventions;
- next-solver stabilization work and 2026’s supply-chain flagships mean releases can change compatibility without changing the target matrix at all;
- docs remain canonical while editor/LLM mediation rises, which increases the value of attachable claim truth; and
- Cargo’s plumbing/report direction keeps making reviewable pack-oriented handoffs more plausible than hosted matrix empires.

Archive decision:
- New design note: `design/compatibility-claims-execution-blueprint-2026Q1.md`
- Design/contract refresh: `design/compatibility-claims-2026Q1.md`, `design/compatibility-claims-stack.md`, `design/compatibility-claims-pilot-program.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `proposals/epic-compatibility-claims-stack.md`
- Canon/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Maintenance: mirror changed canon under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, and rerun the archive doctor

Strategy:
- keep the broad ranking intact;
- keep **Build-State Evidence** as the strongest one-project answer overall;
- keep **Feedback Loop / Debuggability Acceptance** as the clearest under-ranked missing middle;
- make **Compatibility Claims** the clearest current **claim-routing / import-boundary / handoff execution blueprint**;
- keep **Support Envelope** as the platform/runtime/docs layer beneath it rather than replacing it;
- and refuse the tempting wrong shapes first: one compatibility badge, one hosted matrix, one MSRV field, one docs target list, or one semver check pretending to be the whole story.

## rev0455 — turn Release Truth into a real execution blueprint without inventing a new frontier
Instead of widening the archive again, this revision deepens one repeatedly promoted seam that still lacked a direct “what should this actually ship?” answer: **Release Truth**.

The broad frontier map is unchanged, but the repo now has an explicit **Release Truth execution blueprint** for “what should ideal Rust actually build around producer-side package publication, artifact publication, signatures/attestations, rebuild evidence, inventory attachments, and bounded downstream handoffs?” questions.

Why this deepening was merited:
- Cargo’s `cargo package` and `cargo publish` commands already define a concrete package-publication boundary, but not a full release-native evidence boundary;
- crates.io’s January 2026 update hardened Trusted Publishing with GitLab CI/CD support, Trusted-Publishing-only mode, and blocked risky GitHub triggers;
- Cargo’s unstable SBOM support now emits precursor JSON for executable and linkable outputs uplifted into target or artifact directories;
- Rust’s 2026 flagships still keep SBOM support and public/private dependency work in the active supply-chain band;
- cargo-dist now exposes a machine-readable `DistManifest` spanning releases, artifacts, assets, upload files, linkage, and GitHub artifact-attestation posture;
- release-plz continues to automate changelog generation, GitHub/Gitea/GitLab releases, cargo-registry publishing, and version bumps; and
- cargo-binstall keeps signed-download verification as a real but bounded attachment lane rather than the whole release verdict.

Archive decision:
- New design note: `design/release-truth-execution-blueprint-2026Q1.md`
- Design/contract refresh: `design/release-truth-stack.md`, `design/release-truth-pilot-program.md`, `proposals/epic-release-truth-stack.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`, `design/worthy-contribution-shortlist-2026Q1.md`
- Canon/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Maintenance: mirror changed canon under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, and rerun the archive doctor

Strategy:
- keep the broad ranking intact;
- keep **Build-State Evidence** as the strongest one-project answer overall;
- keep **Feedback Loop / Debuggability Acceptance** as the clearest under-ranked missing middle;
- make **Release Truth** the clearest current **producer-side package/artifact/signature/rebuild/inventory continuity execution blueprint**;
- and refuse the tempting wrong shapes first: another release bot, a host-page portal, one provenance badge, or a control-plane dream that erases producer-side boundaries.

## rev0454 — turn Observability Contract into a real execution blueprint without inventing a new frontier
Instead of widening the archive again, this revision deepens one repeatedly promoted seam that still lacked a direct “what should this actually ship?” answer: **Observability Contract**.

The broad frontier map is unchanged, but the repo now has an explicit **Observability execution blueprint** for “what should ideal Rust actually build around diagnostic identity, signal/profile declarations, activation routes, runtime-diagnostic capabilities, support posture, and bounded consumer handoffs?” questions.

Why this deepening was merited:
- the 2025 State of Rust survey still says resource usage and debugging remain live productivity issues while docs stay canonical and editor/LLM mediation rises;
- `tracing-subscriber` and `metrics` still make layering and pluggability explicit rather than giving Rust one hidden telemetry runtime;
- OpenTelemetry Rust still marks traces, metrics, and logs as **Beta**, while opentelemetry-rust recommends `tracing` for fresh setups and OTLP for production scenarios;
- OpenTelemetry's own stability work says complexity and lack of stability impede production deployments, and Weaver argues for observability-by-design with schema validation;
- Tokio Console still proves runtime diagnostics are a separate capability lane with explicit activation requirements;
- Cargo still says plugins matter because Cargo cannot be everything to everyone; and
- exporter routes themselves can decay, as the `opentelemetry-jaeger` advisory now makes explicit.

Archive decision:
- New design note: `design/observability-execution-blueprint-2026Q1.md`
- Design/contract refresh: `design/observability-contract-2026Q1.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`, `design/observability-productization-stack.md`, `design/observability-productization-pilot-program.md`
- Canon/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Maintenance: mirror changed canon under `archive/`, regenerate `meta/ARCHIVE_MANIFEST.md`, and rerun the archive doctor

Strategy:
- keep the broad ranking intact;
- keep **Build-State Evidence** as the strongest one-project answer overall;
- keep **Feedback Loop / Debuggability Acceptance** as the clearest under-ranked missing middle;
- make **Observability Contract** the clearest current **runtime telemetry / activation / support / consumer-handoff execution blueprint**;
- and refuse the tempting wrong shapes first: one exporter route, one dashboard, one runtime probe, or one fake maturity score.

## Latest addition (rev0453)
The archive now has an explicit **Defect Escalation execution blueprint**:
**if ideal Rust needs a real answer for observed failures, minimized repro lineage, routing and duplicate posture, regression-test candidacy, evidence imports, and bounded issue/PR/assistant handoffs, what should that worthy contribution actually ship in theory and practice beyond issue templates, one-file repros, bisection transcripts, or auto-filing bots?**

Read first if you want the repo's current answer to “what should the repro-to-routing-to-regression seam actually become before it turns into another issue form or portal?”
- `design/defect-escalation-execution-blueprint-2026Q1.md`
- `design/defect-escalation-contract-2026Q1.md`
- `design/defect-escalation-stack.md`
- `design/cargo-report-kit.md`
- `design/prototype-elevation-stack.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest still-unbuilt **repro-to-routing-to-regression** answer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Defect Escalation** now has a direct execution blueprint rather than only a contract/stack cluster;
- the sharper answer is now **reference layer + report/pack command + adapter/import corpus** rather than another issue template, portal, or auto-filing workflow;
- the escalation story is now framed around **observed-failure truth + minimization-lineage truth + routing/dedup truth + regression-candidate truth + evidence-import truth + consumer-handoff truth**;
- the first serious proving lanes are now single-file repros, workspace-slice lineage, bisection imports, uncertain-routing cases, and regression-test handoff packs;
- and future debug/report/runner/assistant work should import this escalation substrate rather than rediscovering it privately.

- New design note: `design/defect-escalation-execution-blueprint-2026Q1.md`
- Design refresh: `design/defect-escalation-contract-2026Q1.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`, `meta/ARCHIVE_MANIFEST.md`
- Hygiene: future defect-escalation revisions should keep **observation**, **minimization lineage**, **routing/dedup posture**, **regression candidacy**, **evidence imports**, and **consumer handoff** separate instead of collapsing them into one fake “bug report” story.

## Latest addition (rev0452)
The archive now has an explicit **Benchmark Evidence execution blueprint**:
**if ideal Rust needs a real answer for benchmark subject identity, measurement-lane truth, collector/configuration posture, baseline posture, comparability verdicts, and bounded CI/release/perf-review handoffs, what should that worthy contribution actually ship in theory and practice beyond one harness, one dashboard, or one hosted service?**

Read first if you want the repo's current answer to “what should Rust actually build around performance-claim comparability before the story collapses into screenshots, one score, or tool-specific folklore?”
- `design/benchmark-evidence-execution-blueprint-2026Q1.md`
- `design/benchmark-evidence-contract-2026Q1.md`
- `design/benchmark-evidence-kit.md`
- `design/benchmark-evidence-lane-map.md`
- `design/benchmark-evidence-pilot-program.md`
- `proposals/epic-benchmark-evidence-kit.md`
- `design/perf-labs.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest still-unbuilt **performance-claim / compare-shaping** answer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Benchmark Evidence** now has a direct execution blueprint rather than only contract/kit/lane-map/pilot/proposal notes;
- the sharper answer is now **reference layer + report/pack command + adapter/import corpus** rather than another benchmark harness, dashboard, CI bot, or hosted benchmark product;
- the benchmark story is now framed around **subject truth + measurement-lane truth + collector/configuration truth + baseline truth + verdict/comparability truth + consumer-handoff truth**;
- the first serious proving lanes are now Criterion + Divan, nextest runner import, Iai-Callgrind deterministic-profiler imports, hosted adapter imports, and bounded Perf Labs handoffs;
- and future benchmark, hosted-perf, CI-regression, and release/perf-review work should import this evidence substrate rather than rediscover comparability truth privately.

- New design note: `design/benchmark-evidence-execution-blueprint-2026Q1.md`
- Design refresh: `design/benchmark-evidence-contract-2026Q1.md`, `design/benchmark-evidence-kit.md`, `design/benchmark-evidence-pilot-program.md`, `proposals/epic-benchmark-evidence-kit.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`, `meta/ARCHIVE_MANIFEST.md`
- Hygiene: future benchmark-evidence revisions should keep subject, lane, collector/configuration, baseline, verdict/comparability, and consumer handoffs separate instead of collapsing them into one fake “benchmark result”.

## Latest addition (rev0451)
The archive now has an explicit **Public API execution blueprint**:
**if ideal Rust needs a trustworthy release-boundary and semver-evidence layer, what should that worthy contribution actually ship in theory and practice beyond API diff tools, semver badges, or one-off CI checks?**

Read first if you want the repo's current answer to “what should the public-API seam actually become before it turns into semver theater or tool-specific folklore?”
- `design/public-api-execution-blueprint-2026Q1.md`
- `design/public-api-contract-2026Q1.md`
- `design/public-api-kit.md`
- `design/public-api-pilot-program.md`
- `design/migration-public-api-execution-blueprint-2026Q1.md`
- `design/ideal-rust-worthy-contributions-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest still-unbuilt **release-boundary / exposure / semver-evidence** answer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Migration/Public API** remains the broader release / upgrade composition answer;
- **Public API** now has a direct execution blueprint rather than only a contract/kit/pilot/proposal role;
- the sharper answer is now **reference layer + report/pack command + witness/import corpus** rather than another diff viewer, publish gate, or semver score;
- the public-boundary story is now framed around **subject truth + exposure truth + structural-diff truth + witness/proof truth + bounded-verification truth + consumer-handoff truth**;
- the first serious proving lanes are now single-crate release review, cross-crate / foreign-item exposure, workspace-family API review, migration/publish/downstream imports, and bounded assistant/archive consumers;
- and future release, publish, migration, distro-intake, docs, policy, and archive-summary work should import this API substrate rather than rediscovering it privately.

- New design note: `design/public-api-execution-blueprint-2026Q1.md`
- Design refresh: `design/public-api-contract-2026Q1.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`, `design/worthy-contribution-shortlist-2026Q1.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`, `meta/ARCHIVE_MANIFEST.md`
- Hygiene: future public-API revisions should keep **subject**, **exposure**, **structural diff**, **witness/proof**, **bounded verification**, and **consumer handoff** separate instead of collapsing them into one fake “semver result” story.

## Latest addition (rev0450)
The archive now has an explicit **Canonical Learning execution blueprint**:
**if ideal Rust needs a trustworthy maintainer-authored learning layer, what should that worthy contribution actually ship in theory and practice beyond docs portals, docs scores, or assistant-memory blobs?**

Read first if you want the repo's current answer to “what should the canonical-learning seam actually become before it turns into pseudo-canon, scraped summaries, or smart-docs theater?”
- `design/canonical-learning-execution-blueprint-2026Q1.md`
- `design/canonical-learning-stack.md`
- `design/canonical-learning-lane-map.md`
- `design/canonical-learning-pilot-program.md`
- `design/canonical-learning-consumer-pilot-program.md`
- `design/docproof-kit.md`
- `design/compile-guidance-kit.md`
- `design/ideal-rust-worthy-contributions-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest still-unbuilt **teaching-truth / consumer-import / authority-boundary** answer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Canonical Learning** now has a direct execution blueprint rather than only a stack/lane-map/pilot/proposal role;
- the sharper answer is now **reference layer + report/pack command + consumer/import corpus** rather than another docs portal, search surface, or AI context blob;
- the learning story is now framed around **subject truth + canonical-lane truth + evidence truth + consumer-import truth + derived-overlay truth + consumer-handoff truth**;
- the first serious proving lanes are now API-doc/reference + docs-host posture, guide/tutorial books, compile-guidance / negative-teaching, consumer-import overlays, and bounded support/release/atlas/archive handoffs;
- and future docs-host, editor, assistant, support, release, atlas, and archive-summary work should import this learning substrate rather than rediscovering it privately.

- New design note: `design/canonical-learning-execution-blueprint-2026Q1.md`
- Design refresh: `design/canonical-learning-stack.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`, `design/worthy-contribution-shortlist-2026Q1.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`, `meta/ARCHIVE_MANIFEST.md`
- Hygiene: future canonical-learning revisions should keep **subject**, **canonical lane**, **evidence**, **consumer import**, **derived overlay**, and **consumer handoff** separate instead of collapsing them into one fake “knowledge” story.

## Latest addition (rev0449)
The archive now has an explicit **Support Envelope execution blueprint**:
**if ideal Rust needs a trustworthy platform/runtime/docs support layer, what should that worthy contribution actually ship in theory and practice beyond target matrices, support badges, or cross-build wrappers?**

Read first if you want the repo's current answer to “what should the support-envelope seam actually become before it turns into compatibility theater?”
- `design/support-envelope-execution-blueprint-2026Q1.md`
- `design/support-envelope-kit.md`
- `design/support-envelope-pilot-program.md`
- `design/compatibility-claims-stack.md`
- `design/compatibility-claims-pilot-program.md`
- `design/ideal-rust-worthy-contributions-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest still-unbuilt **platform/runtime/docs support** answer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Compatibility Claims** remains the broader support/claim-shaping band;
- **Support Envelope** now has a direct execution blueprint rather than only a kit/pilot/stack role;
- the sharper answer is now **reference layer + report/pack command + observation/diff corpus** rather than another matrix page, badge system, or wrapper crate;
- the support story is now framed around **subject truth + lane truth + provisioning/runtime-floor truth + evidence truth + drift truth + consumer-handoff truth**;
- the first serious proving lanes are now released artifacts, source-build/custom-target support, docs-surface posture, runtime-floor derivation, and long-lived support handoffs;
- and future release/support/adoption/policy/safety/package-intake layers are now more clearly downstream consumers rather than the canonical source of support truth.

- New design note: `design/support-envelope-execution-blueprint-2026Q1.md`
- Design refresh: `design/support-envelope-kit.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`, `meta/ARCHIVE_MANIFEST.md`
- Hygiene: future support-envelope revisions should keep **subject**, **lane**, **provisioning/runtime-floor**, **evidence**, **drift**, and **consumer handoff** separate instead of collapsing them into one fake “supported platforms” story.


## Latest addition (rev0448)
The archive now has an explicit **Toolchain Productization execution blueprint**:
**if ideal Rust needs a real answer for provisioned toolchain identity, stdlib/sysroot profile identity, activation/reuse posture, runtime-analysis or hardening lane truth, and bounded release/support/safety/assistant handoffs, what should that worthy contribution actually ship in theory and practice beyond another wrapper around rustup, `build-std`, or sanitizer flags?**

Read first if you want the repo's current answer to “what should the toolchain-variant / sysroot / hardening seam actually become before it turns into another environment manager or cache-first product?”
- `design/toolchain-productization-execution-blueprint-2026Q1.md`
- `design/toolchain-productization-contract-2026Q1.md`
- `design/toolchain-productization-stack.md`
- `design/toolchain-productization-lane-map.md`
- `design/toolchain-productization-pilot-program.md`
- `proposals/epic-toolchain-productization-stack.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest still-unbuilt **toolchain-variant / sysroot / hardening / activation** answer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Toolchain Productization** now has a direct execution blueprint rather than only contract/stack/lane-map/pilot/proposal notes;
- the sharper answer is now **reference layer + report/pack command + profile/acceptance corpus** rather than an environment-manager empire, a universal `build-std` wrapper, or a cache product that hides stdlib identity;
- the story is now framed around **provisioning truth + sysroot truth + activation truth + runtime-lane truth + support-envelope truth + consumer-handoff truth**;
- the first serious proving lanes are now stock rustup/override truth, rebuilt-stdlib profile truth, compiler-pinned custom-target truth, instrumented/hardened runtime truth, and bounded release/support/safety/assistant handoffs;
- and future build-std, sanitizer, custom-target, firmware, low-level-platform, and large-adopter work should import this toolchain substrate rather than rediscovering it privately.

- New design note: `design/toolchain-productization-execution-blueprint-2026Q1.md`
- Design refresh: `design/toolchain-productization-contract-2026Q1.md`, `design/toolchain-productization-stack.md`, `proposals/epic-toolchain-productization-stack.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`, `meta/ARCHIVE_MANIFEST.md`
- Hygiene: future toolchain-productization revisions should keep provisioning, sysroot, activation, runtime-lane, support-envelope, and consumer handoff separate instead of collapsing them into one fake “custom toolchain” story.


## Latest addition (rev0447)
The archive now has an explicit **Reviewable Edit execution blueprint**:
**if ideal Rust needs a real answer for machine-produced code mutation, candidate provenance, ordered selection, application receipts, verification receipts, and bounded review/CI/editor/assistant handoffs, what should that worthy contribution actually ship in theory and practice beyond another refactor engine, one editor integration, or direct agent mutation?**

Read first if you want the repo's current answer to “what should the mutation / review / handoff seam actually become before it turns into a universal rewrite platform or a bot-controlled working tree?”
- `design/reviewable-edit-execution-blueprint-2026Q1.md`
- `design/reviewable-edit-contract-2026Q1.md`
- `design/edit-workflow-kit.md`
- `proposals/epic-edit-workflow-kit.md`
- `design/semantic-context-kit.md`
- `design/migration-kit.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest still-unbuilt **mutation / review / handoff** answer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Reviewable Edit** now has a direct execution blueprint rather than only contract/kit/proposal notes;
- the sharper answer is now **reference layer + report/pack command + adapter/acceptance corpus** rather than a refactor empire, assistant autopilot, or IDE-only workflow;
- the edit story is now framed around **subject truth + candidate-provenance truth + selection truth + application truth + verification truth + consumer-handoff truth**;
- the first serious proving lanes are now rustc/Cargo-fix suggestion imports, edition-migration waves, rust-analyzer assist/rename/SSR exports, weaker-authority assistant candidate packs, and bounded PR/CI handoffs;
- and future migration, lint, editor, CI, and assistant layers should import this edit substrate rather than rediscover it privately.

- New design note: `design/reviewable-edit-execution-blueprint-2026Q1.md`
- Design refresh: `design/reviewable-edit-contract-2026Q1.md`, `design/edit-workflow-kit.md`, `proposals/epic-edit-workflow-kit.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`, `meta/ARCHIVE_MANIFEST.md`
- Hygiene: future reviewable-edit revisions should keep subject, provenance, selection, application, verification, and consumer handoffs separate instead of collapsing them into one fake “patch applied” story.

## Latest addition (rev0446)
The archive now has an explicit **Publisher & Source Identity execution blueprint**:
**if ideal Rust needs a real answer for package publication identity, publish authority, family/namespace claims, source-route posture, source-hint boundaries, and downstream handoffs, what should that worthy contribution actually ship in theory and practice beyond badges, registry UI, or provenance theater?**

Read first if you want the repo's current answer to “what should the publication / authority / route seam actually become before it turns into a trust-score service or an all-purpose supply-chain platform?”
- `design/publisher-source-identity-execution-blueprint-2026Q1.md`
- `design/publisher-source-identity-contract-2026Q1.md`
- `design/publisher-source-identity-stack.md`
- `design/publisher-source-identity-pilot-program.md`
- `proposals/epic-publisher-source-identity-stack.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/distribution-contract-execution-blueprint-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest still-unbuilt **publication / authority / route-shaping** answer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Publisher & Source Identity** now has a direct execution blueprint rather than only a contract/stack/pilot/proposal cluster;
- the sharper answer is now **reference layer + report/pack command + adapter/acceptance corpus** rather than a badge program, registry-UI rewrite, or universal provenance platform;
- the identity story is now framed around **subject truth + claim truth + publisher-authority truth + source-route truth + source-hint/provenance-boundary truth + consumer truth**;
- the first serious proving lanes are now crates.io owner/team-owner truth, trusted-publisher and trusted-publishing-only posture, authenticated alternate registries, exact-copy replacement/vendoring routes, namespace-controlled vs inferred family claims, and bounded intake/trust/distribution/support/incident handoffs;
- and future trust, intake, distribution, support, and incident layers should import this identity substrate rather than re-deriving it privately.

- New design note: `design/publisher-source-identity-execution-blueprint-2026Q1.md`
- Design refresh: `design/publisher-source-identity-contract-2026Q1.md`, `design/publisher-source-identity-stack.md`, `design/publisher-source-identity-pilot-program.md`, `proposals/epic-publisher-source-identity-stack.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`, `meta/ARCHIVE_MANIFEST.md`
- Hygiene: future publisher/source-identity revisions should keep claim posture, publisher authority, source route, source-hint boundaries, and consumer handoffs separate instead of collapsing them into one fake “package identity” story.

## Latest addition (rev0445)
The archive now has an explicit **Workspace Environment execution blueprint**:
**if ideal Rust needs a real answer for workspace discovery, declared environment intent, realization across substrates, observed drift, and bounded human/editor/CI/agent handoffs, what should that worthy contribution actually ship in theory and practice beyond another setup guide, dev shell, or remote-dev platform?**

Read first if you want the repo's current answer to “what should the workspace environment seam actually become before it turns into another environment manager or one-true-substrate fight?”
- `design/workspace-environment-execution-blueprint-2026Q1.md`
- `design/workspace-environment-contract-2026Q1.md`
- `design/workspace-environment-stack.md`
- `design/workspace-environment-bundle.md`
- `design/tooling-contract-stack.md`
- `design/toolchain-productization-stack.md`
- `proposals/epic-workspace-environment-stack.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest still-unbuilt **environment / realization / observation / handoff** answer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Workspace Environment** now has a direct execution blueprint rather than only contract/stack/bundle/proposal notes;
- the sharper answer is now **reference layer + report/pack command + realization/acceptance corpus** rather than another setup wizard, secret vault, or remote-dev empire;
- the environment story is now framed around **subject/discovery truth + declared-intent truth + realization truth + secret-posture truth + observation truth + consumer truth**;
- the first serious proving lanes are now parent-discovery/config-precedence reports, rustup override/toolchain posture, host-vs-devcontainer-or-Nix comparisons, rust-analyzer/CI handoffs, and redacted support/agent exports;
- and future onboarding, editor, CI, institutional-overlay, and bootstrap work now read more clearly as downstream consumers rather than the canonical environment source.

- New design note: `design/workspace-environment-execution-blueprint-2026Q1.md`
- Design refresh: `design/workspace-environment-contract-2026Q1.md`, `design/workspace-environment-stack.md`, `design/workspace-environment-bundle.md`, `proposals/epic-workspace-environment-stack.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`, `meta/ARCHIVE_MANIFEST.md`
- Hygiene: future workspace-environment revisions should keep **subject/discovery**, **declared intent**, **realization**, **secret posture**, **observation**, and **consumer handoff** separate instead of collapsing them into one fake “dev setup”.

## Latest addition (rev0444)
The archive now has an explicit **Distribution Contract execution blueprint**:
**if ideal Rust needs a real answer for delivery, acquisition, fallback, verification, and installed ownership, what should that worthy contribution actually ship in theory and practice beyond one installer, one binary host, or one app-store fantasy?**

Read first if you want the repo's current answer to “what should the delivery / acquisition / ownership seam actually become before it turns into another installer wrapper or updater empire?”
- `design/distribution-contract-execution-blueprint-2026Q1.md`
- `design/distribution-contract-2026Q1.md`
- `design/distribution-contract-stack.md`
- `design/distribution-contract-pilot-program.md`
- `design/consumer-install-kit.md`
- `design/cargo-artifact-contract-execution-blueprint-2026Q1.md`
- `proposals/epic-distribution-contract-stack.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest still-unbuilt **delivery / acquisition / ownership** answer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Distribution Contract** now has a direct execution blueprint rather than only a contract/stack/pilot cluster;
- the sharper answer is now **reference layer + report/pack command + adapter/acceptance corpus** rather than another installer, updater monopoly, or hosted software portal;
- the delivery story is now framed around **release-import truth + route/catalog truth + selection/fallback truth + verification truth + installed-ownership truth + consumer-handoff truth**;
- the first serious proving lanes are now `cargo install` source-build truth, cargo-binstall prebuilt/fallback truth, cargo-dist mirror/installer imports, rustup/Cargo shared-path ownership, and bounded update/support/uninstall handoffs;
- and **Cargo Artifact Contract** now reads more clearly as the upstream final-output substrate beneath the distribution answer.

- New design note: `design/distribution-contract-execution-blueprint-2026Q1.md`
- Design refresh: `design/distribution-contract-2026Q1.md`, `design/distribution-contract-stack.md`, `proposals/epic-distribution-contract-stack.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`, `meta/ARCHIVE_MANIFEST.md`
- Hygiene: future distribution revisions should keep **release imports**, **route visibility**, **selection/fallback**, **verification**, **installed ownership**, and **consumer handoff** separate instead of collapsing them into one fake “install succeeded” story.

## Latest addition (rev0443)
The archive now has an explicit **Cargo Artifact Contract execution blueprint**:
**if ideal Rust needs a trustworthy final-output and handoff layer for Cargo, what should that worthy contribution actually ship in theory and practice beyond JSON scraping, `target/` archaeology, or one more release manifest?**

Read first if you want the repo's current answer to “what should the artifact/final-output seam actually become before it turns into a path-convention accident or a downstream release-tool monopoly?”
- `design/cargo-artifact-contract-execution-blueprint-2026Q1.md`
- `design/cargo-artifact-contract-2026Q1.md`
- `design/artifact-surface-kit.md`
- `proposals/epic-artifact-surface-kit.md`
- `design/ideal-rust-worthy-contributions-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest still-unbuilt final-output answer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Cargo Artifact Contract** now has a direct execution blueprint rather than only a frontier note and kit/proposal cluster;
- the sharper answer is now **reference layer + report/pack command + acceptance corpus** rather than a target-dir scraper, release orchestrator, or hosted artifact portal;
- the artifact story is now framed around **selected-subject truth + evidence-path truth + final-artifact identity truth + origin/staging truth + sidecar truth + consumer truth**;
- the first serious proving lanes are now Cargo-native bin/lib/example outputs, doc/package outputs, build-script uplift, SBOM sidecars, and bounded release/inventory/repro/install/support handoffs;
- and future release, install, inventory, or reproducibility layers are now more clearly downstream consumers rather than the canonical artifact source.

- New design note: `design/cargo-artifact-contract-execution-blueprint-2026Q1.md`
- Design refresh: `design/worthy-contribution-shortlist-2026Q1.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`, `design/artifact-surface-kit.md`, `proposals/epic-artifact-surface-kit.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`, `meta/ARCHIVE_MANIFEST.md`
- Hygiene: future artifact-contract revisions should keep **selected subject**, **evidence path**, **final artifact identity**, **origin/staging**, **sidecar attachment**, and **consumer handoff** separate instead of collapsing them into one fake “artifact list”.

## Latest addition (rev0442)
The archive now has an explicit **Safety-Critical Readiness Commons execution blueprint**:
**if ideal Rust needs a real answer for safety-critical adoption, what should that worthy contribution actually ship in theory and practice beyond one assurance pack, one qualified distro, or one more lint/evidence pile?**

Read first if you want the repo's current answer to “what should the safety-critical commons layer actually become before it turns into qualification theater?”
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `design/safety-critical-assurance-contract-2026Q1.md`
- `design/safety-critical-evidence-stack.md`
- `design/safety-critical-pilot-program.md`
- `design/ideal-rust-worthy-contributions-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `proposals/epic-safety-critical-readiness-commons.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest still-unbuilt safety program answer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Safety-Critical Readiness Commons** now has a direct execution blueprint rather than only evidence/assurance/kit notes;
- the sharper answer is now **stewarded program + readiness commons + profile/acceptance corpus + report/pack command** rather than a badge system, one vendor toolchain, or one evidence stack;
- the safety-critical story is now framed around **critical-slice truth + authority truth + qualified-scope truth + target/runtime truth + dependency-lifecycle truth + interface truth + evidence/consumer truth**;
- the first serious proving lanes are now target-readiness profiles, dependency-lifecycle patterns, mixed-language boundary packs, async/runtime caveat imports, and assurance-import handoffs;
- and the existing **Safety-Critical Assurance Contract** is now more clearly a vital substrate import rather than the whole commons.

- New design note: `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- New proposal note: `proposals/epic-safety-critical-readiness-commons.md`
- Design refresh: `design/worthy-contribution-shortlist-2026Q1.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`
- Hygiene: future safety-critical-readiness revisions should keep **qualified scope**, **target/runtime posture**, **dependency posture**, **interface posture**, and **assurance/evidence posture** separate instead of collapsing them into “certified/not certified”.

## Latest addition (rev0441)
The archive now has an explicit **Async Capability Commons execution blueprint**:
**if ideal Rust needs a real answer to runtime lock-in, partial portability, and async capability truth, what should that worthy contribution actually ship in theory and practice instead of collapsing into “better async ergonomics” or “another runtime” vibes?**

Read first if you want the repo's current answer to “what should the async commons layer actually become before it turns into one more runtime abstraction story?”
- `design/async-capability-commons-execution-blueprint-2026Q1.md`
- `design/async-commons-kit.md`
- `design/async-commons-lane-map.md`
- `design/async-commons-pilot-program.md`
- `design/async-lifecycle-kit.md`
- `design/async-reliability-stack.md`
- `design/ideal-rust-worthy-contributions-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest async program-shaped answer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Async Capability Commons** now has a direct execution blueprint rather than only kit/lane-map/pilot/proposal notes;
- the sharper answer is now **reference layer + capability commons + adapter/acceptance corpus + report/pack command** rather than another runtime, abstraction facade, or portability badge;
- the async story is now framed around **lane truth + capability truth + common-surface truth + adapter truth + environment truth + consumer truth**;
- the first serious proving lanes are now I/O adapters, spawn/local capability, time/deadline posture, stream/async-sequence `watch` reports, environment contrast, and lifecycle/reliability imports;
- and future async recommendation, debugging, or service layers are now more clearly downstream consumers rather than the canonical source of async truth.

- New design note: `design/async-capability-commons-execution-blueprint-2026Q1.md`
- Design refresh: `design/worthy-contribution-shortlist-2026Q1.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`, `proposals/epic-async-commons-kit.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`
- Hygiene: future async-commons revisions should keep **lane truth, capability truth, common-surface truth, adapter truth, environment truth, and consumer truth** separate instead of collapsing them into a generic “runtime compatibility” story.

## Latest addition (rev0440)
The archive now has an explicit **Maintainer Reality / Keystone Stewardship execution blueprint**:
**if ideal Rust needs better continuity, maintainer support, and keystone-project truth, what should that worthy contribution actually ship in theory and practice instead of dissolving into dashboards, badges, or funding vibes?**

Read first if you want the repo's current answer to “what should the stewardship/continuity layer actually become before it turns into another ecosystem scorecard?”
- `design/maintainer-reality-keystone-stewardship-execution-blueprint-2026Q1.md`
- `design/maintenance-reality-stack.md`
- `design/maintenance-reality-lane-map.md`
- `design/keystone-stewardship-stack.md`
- `design/stewardship-pilot-program.md`
- `design/ideal-rust-worthy-contributions-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest program-shaped stewardship answer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Maintainer Reality / Keystone Stewardship** now has a direct execution blueprint rather than only stack/pilot/contract notes;
- the sharper answer is now **reference layer + corpus/atlas + report/pack command** rather than another dashboard, health score, or funder spreadsheet;
- the maintenance/stewardship story is now framed around **lifecycle truth + operations truth + keystone truth + institutional-support truth + continuity-risk truth + consumer truth**;
- and the first serious proving lanes are now triage / stale review, help routing, keystone library review, release/backport continuity, and bounded atlas/fund/policy exports.

- New design note: `design/maintainer-reality-keystone-stewardship-execution-blueprint-2026Q1.md`
- Design refresh: `design/worthy-contribution-shortlist-2026Q1.md`, `design/ideal-rust-worthy-contributions-2026Q1.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`
- Hygiene: future maintainer/stewardship revisions should keep declared lifecycle, observed operations, keystone criticality, institutional backing, continuity risk, and consumer claims separate instead of collapsing them into “maintainer health”.

## Latest addition (rev0439)
The archive now has an explicit **Feedback Loop / Debuggability Acceptance execution blueprint**:
**if rev0438 elevated this as the clearest under-ranked missing middle, what should the contribution actually ship in theory and practice instead of dissolving into “better debugging” vibes?**

Read first if you want the repo's current answer to “what should the missing middle around build/debug/inspection/acceptance actually become before it turns into another tool soup?”
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/feedback-loop-stack.md`
- `design/debuggability-stack.md`
- `design/feedback-loop-pilot-program.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/ideal-rust-worthy-contributions-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/portfolio-contribution-shapes-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest “missing middle” answer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** now has a direct execution blueprint rather than only a stack/pilot/proposal cluster;
- the sharper answer is now **capability commons + acceptance corpus + report/pack layer** rather than another debugger, IDE backend, or dashboard;
- the build/debug loop is now framed around **session truth + build-state truth + inspection truth + acceptance truth + consumer truth**;
- the first serious proving lanes are now session/build→debug handoff, debugger tuple + visualizer acceptance, async inspection, native/split-debug-info posture, and bounded issue/support/docs exports;
- and future assistant/editor/service layers are now more clearly downstream consumers rather than the canonical source of loop truth.

- New design note: `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`
- Hygiene: future feedback-loop/debuggability revisions should keep **session truth, build-state truth, inspection truth, acceptance truth, and consumer truth** separate instead of collapsing them into a generic “debugging support” story.

## Latest addition (rev0438)
The archive now has an explicit **Ideal Rust Worthy Contributions** synthesis note:
**if we step back from individual seams and ask what the Rust ecosystem is still truly missing, which contributions are really worthy or epic now, what shape should they take, and which seductive directions should be eliminated rather than widened?**

Read first if you want the repo's current answer to “what should ideal-Rust portfolio work rank highest, what should count as a serious contribution, and what should be folded, downgraded, or killed?”
- `design/ideal-rust-worthy-contributions-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/portfolio-selection-rubric-2026Q1.md`
- `design/portfolio-contribution-shapes-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/migration-public-api-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/native-edge-execution-blueprint-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens and reorganizes the archive's top-level portfolio map:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** is now treated as the clearest under-ranked missing middle;
- **Semantic Context**, **Package Intake Gateway**, and **Migration/Public API** remain core build-now answers;
- **Adoption Navigation** is retained but reclassified as a routed decision layer that should usually import stronger substrate from the build, package, migration, maintenance, and semantic seams;
- **Native Edge Contract** remains the active specialist frontier;
- the archive now names **Async Capability Commons** and **Maintainer Reality / Keystone Stewardship** more explicitly as worthy program-shaped opportunities;
- and the repo now has a clearer elimination list for ideas that should usually be folded instead of promoted: mega frameworks, assistant-only recommendation oracles, hosted dashboards before local truth, universal FFI platforms, and “new runtime solves async” answers.

- New design note: `design/ideal-rust-worthy-contributions-2026Q1.md`
- Design refresh: `design/worthy-contribution-shortlist-2026Q1.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Tooling refresh: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`
- Hygiene: future “ideal Rust” revisions should now say explicitly which candidates are **build-now epics**, which are **substrate multipliers**, which are **program-shaped**, and which should be **eliminated or folded** rather than merely sounding exciting.

## Latest addition (rev0437)
The archive now has an explicit **Portfolio Contribution Shapes** note, a paired **Contribution Shape Protocol**, a first `morphologies/portfolio-contribution-shapes-v0/` corpus, and a real `tools/check_contribution_shapes.py` checker:
**if the repo already knows which Rust seams are worthy, what shared atlas should tell future revisions what kind of thing a given contribution should actually become — protocol, collector, reference layer, report command, service, corpus, checker, bridge, pilot program, or stewarded program — instead of relying on instinct?**

Read first if you want the repo's current answer to “what shape should this worthy contribution take in theory and practice before it overbuilds itself?”
- `design/portfolio-contribution-shapes-2026Q1.md`
- `meta/CONTRIBUTION_SHAPE_PROTOCOL.md`
- `morphologies/README.md`
- `morphologies/portfolio-contribution-shapes-v0/README.md`
- `morphologies/portfolio-contribution-shapes-v0/shapes.json`
- `tools/check_contribution_shapes.py`
- `design/portfolio-selection-rubric-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's execution-design discipline:
- **Build-State Evidence** remains the strongest one-project answer overall;
- the strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- the repo now has a canonical answer for **what form a worthy contribution should take before launch claims outrun artifact reality**;
- and future revisions can now say not only “this seam matters” but “this should begin as a collector, reference layer, report surface, corpus/checker pair, bridge, or stewarded program — and here is the category mistake to avoid.”

- New design note: `design/portfolio-contribution-shapes-2026Q1.md`
- New meta note: `meta/CONTRIBUTION_SHAPE_PROTOCOL.md`
- New morphology corpus: `morphologies/README.md`, `morphologies/portfolio-contribution-shapes-v0/README.md`, and `morphologies/portfolio-contribution-shapes-v0/shapes.json`
- New tool: `tools/check_contribution_shapes.py`
- Tooling refresh: `tools/hygiene.py`, `tools/archive_doctor.py`, `meta/ARCHIVE_DOCTOR_PROTOCOL.md`, `meta/ARCHIVE_DOCTOR_LAST_RUN.json`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep the core portfolio intact; and add one concrete answer for **what kind of deliverable the archive should choose before building the wrong class of thing for the right seam**.
- Hygiene: future revisions that materially change the shared shape atlas should now update the design note, the protocol, the morphology corpus, and the checker in the same revision, or explicitly say why not.

## Latest addition (rev0436)
The archive now has an explicit **Portfolio Source Atlas** note, a paired **Source Atlas Protocol**, a first `atlases/portfolio-source-atlas-v0/` corpus, and a real `tools/check_source_atlas.py` checker:
**if the repo already has rankings, claims, renewal rules, and repeated citations, what small shared atlas should tell future revisions which Rust source families support which kinds of claims, with what caveats, instead of relying on maintainer memory?**

Read first if you want the repo's current answer to “which upstream source lane should carry this canon claim, and what caveat should travel with it?”
- `design/portfolio-source-atlas-2026Q1.md`
- `meta/SOURCE_ATLAS_PROTOCOL.md`
- `atlases/README.md`
- `atlases/portfolio-source-atlas-v0/README.md`
- `atlases/portfolio-source-atlas-v0/sources.json`
- `tools/check_source_atlas.py`
- `design/portfolio-evidence-renewal-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's citation and renewal discipline:
- **Build-State Evidence** remains the strongest one-project answer overall;
- the strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- the repo now has a canonical answer for **which recurring source families support which kinds of archive claims, with what caveats**;
- and future revisions can now register authority lanes explicitly instead of stretching one blog post, one goals page, or one service doc across the whole canon.

- New design note: `design/portfolio-source-atlas-2026Q1.md`
- New meta note: `meta/SOURCE_ATLAS_PROTOCOL.md`
- New atlas corpus: `atlases/README.md`, `atlases/portfolio-source-atlas-v0/README.md`, and `atlases/portfolio-source-atlas-v0/sources.json`
- New tool: `tools/check_source_atlas.py`
- Tooling refresh: `tools/hygiene.py`, `tools/archive_doctor.py`, `meta/ARCHIVE_DOCTOR_PROTOCOL.md`, `meta/ARCHIVE_DOCTOR_LAST_RUN.json`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `design/portfolio-archive-doctor-2026Q1.md`
- Strategy: keep the broad ladder intact; keep the core portfolio intact; and add one concrete answer for **how the archive should remember which source families are fit for which claims before it widens or renews them**.
- Hygiene: future revisions that materially change the shared source atlas should now update the design note, the protocol, the atlas corpus, and the checker in the same revision, or explicitly say why not.

## Latest addition (rev0435)
The archive now has an explicit **Portfolio Hypothesis Ledger** note, a paired **Hypothesis Ledger Protocol**, a first `ledgers/portfolio-hypothesis-ledger-v0/` corpus, and a real `tools/check_hypothesis_ledger.py` checker:
**if the repo already knows what seams matter, what should ship, how pilots should prove themselves, and how freshness should be renewed, which repeated strategic claims should now be named explicitly with downgrade triggers and falsifiers instead of floating forever as stylistic canon?**

Read first if you want the repo's current answer to “which present-tense portfolio claims are live enough to lean on, and what would narrow or break them?”
- `design/portfolio-hypothesis-ledger-2026Q1.md`
- `meta/HYPOTHESIS_LEDGER_PROTOCOL.md`
- `ledgers/README.md`
- `ledgers/portfolio-hypothesis-ledger-v0/README.md`
- `ledgers/portfolio-hypothesis-ledger-v0/hypotheses.json`
- `tools/check_hypothesis_ledger.py`
- `design/portfolio-evidence-renewal-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's comparison-to-reality layer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- the strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- the repo now has a canonical answer for **which repeated strategic claims deserve explicit cards, statuses, downgrade triggers, and falsifiers**;
- and future ranking or sequencing revisions can now say “this claim was confirmed, narrowed, degraded, superseded, or retired” without hiding the claim itself inside prose.

- New design note: `design/portfolio-hypothesis-ledger-2026Q1.md`
- New meta note: `meta/HYPOTHESIS_LEDGER_PROTOCOL.md`
- New ledger corpus: `ledgers/README.md`, `ledgers/portfolio-hypothesis-ledger-v0/README.md`, and `ledgers/portfolio-hypothesis-ledger-v0/hypotheses.json`
- New tool: `tools/check_hypothesis_ledger.py`
- Design/meta/tool refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `meta/ARCHIVE_DOCTOR_PROTOCOL.md`, `tools/hygiene.py`, `tools/archive_doctor.py`
- Strategy: keep the broad ladder intact; keep the core portfolio intact; and add one concrete answer for **how the archive names, reviews, and potentially retracts its strongest repeated claims**.
- Hygiene: future revisions that materially change a top-band portfolio claim should now either update the hypothesis ledger or explicitly say why the claim ledger did not need to change.

## Latest addition (rev0434)
The archive now has an explicit **Portfolio Anchor Corpus** note, a paired **Anchor Corpus Protocol**, a first `proofgrounds/portfolio-anchor-corpus-v0/` corpus, and a real `tools/check_anchor_corpus.py` checker:
**if the repo already has a shared scenario matrix, what concrete representative case profiles should serious pilots bind to so they stop winning by carefully chosen private demos?**

Read first if you want the repo's current answer to “what thin anchor corpus should future pilots, funders, and maintainers use so scenario coverage turns into comparable representative cases?”
- `design/portfolio-anchor-corpus-2026Q1.md`
- `meta/ANCHOR_CORPUS_PROTOCOL.md`
- `proofgrounds/README.md`
- `proofgrounds/portfolio-anchor-corpus-v0/README.md`
- `proofgrounds/portfolio-anchor-corpus-v0/anchors.json`
- `tools/check_anchor_corpus.py`
- `design/portfolio-proving-grounds-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's proving/evaluation layer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- the strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- the repo now has a canonical answer for **what concrete representative case profiles serious pilots should bind to beneath the shared scenario matrix**;
- and future pilots now have to say not just which scenario IDs they exercised but which anchor IDs they satisfied, what they held constant, and what those choices still fail to prove.

- New design note: `design/portfolio-anchor-corpus-2026Q1.md`
- New meta note: `meta/ANCHOR_CORPUS_PROTOCOL.md`
- New corpus: `proofgrounds/portfolio-anchor-corpus-v0/README.md`, `proofgrounds/portfolio-anchor-corpus-v0/anchors.json`
- New tool: `tools/check_anchor_corpus.py`
- Tooling refresh: `tools/archive_doctor.py`, `tools/hygiene.py`, `meta/ARCHIVE_DOCTOR_LAST_RUN.json`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `proofgrounds/README.md`
- Strategy: keep the broad ladder intact; keep the core portfolio intact; and add one concrete answer for **what representative case profiles should sit beneath scenario cards before the archive widens its claims**.
- Hygiene: future revisions that materially change the shared anchor corpus should now update the design note, the protocol, the corpus, and the checker in the same revision, or explicitly say why not.

## Latest addition (rev0433)
The archive now has an explicit **Portfolio Proving Grounds** note, a paired **Proving Grounds Protocol**, a first `proofgrounds/portfolio-scenario-matrix-v0/` corpus, and a real `tools/check_proving_ground_matrix.py` checker:
**if the repo already knows how to rank, stage, and score worthy seams, what shared Rust realities should serious pilots bind themselves to so they stop winning by incomparable demos?**

Read first if you want the repo's current answer to “what thin scenario matrix should future pilots, funders, and maintainers use before they generalize from one happy path?”
- `design/portfolio-proving-grounds-2026Q1.md`
- `meta/PROVING_GROUNDS_PROTOCOL.md`
- `proofgrounds/README.md`
- `proofgrounds/portfolio-scenario-matrix-v0/README.md`
- `proofgrounds/portfolio-scenario-matrix-v0/scenarios.json`
- `tools/check_proving_ground_matrix.py`
- `design/portfolio-pilot-evaluation-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's execution/evaluation layer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- the strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- the repo now has a canonical answer for **what shared proving grounds serious pilots should name before claiming broad relevance**;
- and future pilots now have to state which scenario cards they exercised, which they skipped, and what those skips prohibit them from claiming.

- New design note: `design/portfolio-proving-grounds-2026Q1.md`
- New meta note: `meta/PROVING_GROUNDS_PROTOCOL.md`
- New corpus: `proofgrounds/README.md`, `proofgrounds/portfolio-scenario-matrix-v0/README.md`, `proofgrounds/portfolio-scenario-matrix-v0/scenarios.json`
- New tool: `tools/check_proving_ground_matrix.py`
- Tooling refresh: `tools/archive_doctor.py`, `tools/hygiene.py`, `meta/ARCHIVE_DOCTOR_PROTOCOL.md`, `meta/ARCHIVE_DOCTOR_LAST_RUN.json`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep the core portfolio intact; and add one concrete answer for **what representative Rust realities should make a pilot more comparable and more falsifiable before the archive widens its claims**.
- Hygiene: future revisions that materially change the shared scenario matrix should now update the design note, the protocol, the scenario corpus, and the checker in the same revision, or explicitly say why not.

## Latest addition (rev0432)
The archive now has an explicit **Portfolio Archive Doctor** note, a paired **Archive Doctor Protocol**, a real `tools/archive_doctor.py` entrypoint, and a machine-readable last-run receipt:
**if the repo already has queues, protocols, specimens, and validators, what one maintainer-facing workflow should run them, distinguish hard failures from human follow-up, and leave a receipt instead of a vague “looks good” claim?**

Read first if you want the repo's current answer to “what should a real archive-health pass actually do before a revision claims it is complete enough to hand off?”
- `design/portfolio-archive-doctor-2026Q1.md`
- `meta/ARCHIVE_DOCTOR_PROTOCOL.md`
- `tools/archive_doctor.py`
- `meta/ARCHIVE_DOCTOR_LAST_RUN.json`
- `design/portfolio-conformance-validation-2026Q1.md`
- `design/portfolio-evidence-renewal-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's maintainer/operations layer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- the strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- the repo now has a canonical answer for **what one real maintainer doctor pass should check, what it may fail mechanically, and what it must still hand back to human review**;
- and future revisions can now leave behind a machine-readable doctor receipt instead of only claiming hygiene by prose.

- New design note: `design/portfolio-archive-doctor-2026Q1.md`
- New meta note: `meta/ARCHIVE_DOCTOR_PROTOCOL.md`
- New tool: `tools/archive_doctor.py`
- New receipt: `meta/ARCHIVE_DOCTOR_LAST_RUN.json`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep the core portfolio intact; and add one concrete answer for **how a steward or LLM should run a real repo-health pass without pretending that passing checks automatically refreshes ecosystem truth**.
- Hygiene: future revisions that materially change required doctor checks or doctor receipts should now update the design note, the protocol, the tool, and `meta/ARCHIVE_DOCTOR_LAST_RUN.json` in the same revision, or explicitly say why not.

## Latest addition (rev0431)
The archive now has an explicit **Portfolio Conformance Validation** note, a paired **Portfolio Conformance Protocol**, a first `fixtures/portfolio-envelope-v0/` negative-fixture lane, and a real `tools/check_portfolio_envelope_contract.py` checker:
**if the repo already knows what shared artifact grammar should mean and already has specimen examples, what hard honesty rules should a validator actually enforce now, and what should remain seam-local rather than being swallowed by one fake mega-schema?**

Read first if you want the repo's current answer to “what may a shared-grammar validator legitimately check before future tools, CI glue, or LLM edits claim an artifact is well-formed?”
- `design/portfolio-conformance-validation-2026Q1.md`
- `meta/PORTFOLIO_CONFORMANCE_PROTOCOL.md`
- `fixtures/portfolio-envelope-v0/README.md`
- `fixtures/portfolio-envelope-v0/portfolio-envelope-hygiene-checks.json`
- `tools/check_portfolio_envelope_contract.py`
- `design/portfolio-reference-specimens-2026Q1.md`
- `design/portfolio-artifact-conventions-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's execution/hygiene layer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- the strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- the repo now has a canonical answer for **what shared-grammar rules may be enforced mechanically right now**;
- and future shared-envelope edits now have to pass both positive specimens and negative fixtures rather than only sounding plausible in prose.

- New design note: `design/portfolio-conformance-validation-2026Q1.md`
- New meta note: `meta/PORTFOLIO_CONFORMANCE_PROTOCOL.md`
- New fixtures: `fixtures/portfolio-envelope-v0/README.md`, `fixtures/portfolio-envelope-v0/portfolio-envelope-hygiene-checks.json`, and `fixtures/portfolio-envelope-v0/invalid/*.json`
- New tool: `tools/check_portfolio_envelope_contract.py`
- Design/meta/specimen refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `specimens/README.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`, `tools/hygiene.py`
- Strategy: keep the broad ladder intact; keep the core portfolio intact; and add one concrete answer for **what a validator may actually reject before the archive treats shared packs, briefs, diffs, verify receipts, and lineage receipts as fit for reuse**.
- Hygiene: future revisions that materially change shared grammar, role minimums, or routing posture should now update the checker and at least one positive or negative fixture in the same revision, or explicitly say why not.

## Latest addition (rev0430)
The archive now has an explicit **Portfolio Reference Specimens** note, a paired **Specimen Corpus Protocol**, and a first `specimens/` corpus:
**if the repo already knows what honest packs, briefs, diffs, verify receipts, and lineage receipts should mean, what tiny concrete corpus should future validators, glue tooling, and LLM edits actually look at so they stop inventing incompatible examples?**

Read first if you want the repo's current answer to “what shared examples should exist before we trust tools or assistants to ‘just know’ the archive's artifact grammar?”
- `design/portfolio-reference-specimens-2026Q1.md`
- `meta/SPECIMEN_CORPUS_PROTOCOL.md`
- `specimens/README.md`
- `specimens/portfolio-envelope-v0/README.md`
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/portfolio-consumer-routing-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's execution/hygiene layer:
- **Build-State Evidence** remains the strongest one-project answer overall;
- the strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- the repo now has a canonical answer for **what minimal cross-seam example corpus should exist**;
- and future shared-grammar, routing, or validator work can now diff a small concrete corpus instead of only diffing prose.

- New design note: `design/portfolio-reference-specimens-2026Q1.md`
- New meta note: `meta/SPECIMEN_CORPUS_PROTOCOL.md`
- New specimen corpus: `specimens/README.md`, `specimens/portfolio-envelope-v0/README.md`, and first `*.example.json` files
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep the core portfolio intact; and add one concrete answer for **what shared examples future tools and LLM edits should follow when they need honest pack/brief/diff/verify/lineage shapes**.
- Hygiene: future revisions that materially change shared grammar, routed-brief rules, or verify/lineage posture should now either refresh the affected specimen or explicitly say why no specimen changed.

## Latest addition (rev0429)
The archive now has an explicit **Portfolio Consumer Routing** note and a paired **Consumer Routing Protocol**:
**if the repo already knows what worthy seams should ship and what honest artifacts they should emit, which downstream consumers should get which slice, with what authority floor, and when must they escalate back to the canonical pack instead of pretending a brief is enough?**

Read first if you want the repo's current answer to “how should CI, reviewers, editors, release/security operators, and assistants consume the canon without laundering weaker views into truth?”
- `design/portfolio-consumer-routing-2026Q1.md`
- `meta/CONSUMER_ROUTING_PROTOCOL.md`
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `design/portfolio-evidence-renewal-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's consumer/handoff discipline:
- **Build-State Evidence** remains the strongest one-project answer overall;
- the strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- the repo now has a canonical answer for **consumer class, decision class, authority floor, lossiness budget, and escalation target**;
- and every serious routed view can now be judged by whether it is honest enough for its consumer instead of by whether it is pleasantly compact.

- New design note: `design/portfolio-consumer-routing-2026Q1.md`
- New meta note: `meta/CONSUMER_ROUTING_PROTOCOL.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep the core portfolio intact; and add a repo-level answer for **which weaker views are allowed for which consumers, and when those consumers must escalate back to the source artifact**.
- Hygiene: future consumer-facing revisions must declare the **primary consumer class, allowed decisions, preserved authority floor, lossiness budget, prohibited conclusions, and escalation path**; do not let CI summaries, editor hints, release dashboards, or assistant briefs silently impersonate the canonical pack.


## Latest addition (rev0428)
The archive now has an explicit **Portfolio Evidence Renewal** note and a paired **Evidence Renewal Protocol**:
**if the repo already knows what seams are worthy and how to stage and judge them, how should it keep its strongest claims fresh as Rust's goals, services, security assumptions, and machine-usable inputs continue to move?**

Read first if you want the repo's current answer to “how should the canon detect drift, refresh supporting claims, and avoid stale confidence?”
- `design/portfolio-evidence-renewal-2026Q1.md`
- `meta/EVIDENCE_RENEWAL_PROTOCOL.md`
- `meta/CANONICAL_RENEWAL_QUEUE.md`
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `design/portfolio-selection-rubric-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's maintenance and comparison system:
- **Build-State Evidence** remains the strongest one-project answer overall;
- the strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- the repo now has a canonical answer for **claim class, authority lane, drift horizon, renewal trigger, and renewal outcome**;
- and every serious freshness pass can now end in **confirmed / narrowed / degraded / superseded / retired** instead of silent evergreen prose.

- New design note: `design/portfolio-evidence-renewal-2026Q1.md`
- New meta notes: `meta/EVIDENCE_RENEWAL_PROTOCOL.md`, `meta/CANONICAL_RENEWAL_QUEUE.md`
- Design/meta refresh: `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep the core portfolio intact; and add a repo-level answer for **how strong claims should stay current without overreacting to one new source**.
- Hygiene: future freshness revisions must say **what was re-checked, what class of claim it was, what drift horizon it had, what triggered review, and whether the result was confirmed, narrowed, degraded, superseded, or retired**; do not let dated citations or assistant summaries silently keep impersonating live truth.


## Latest addition (rev0427)
The archive now has an explicit **Portfolio Pilot Evaluation** note and a paired **Pilot Scorecard Protocol**:
**if the repo already knows what seams are worthy and in what order they should be built, how should it judge whether a real pilot actually proved itself well enough to graduate, deepen, fold, delay, or die?**

Read first if you want the repo's current answer to “what evidence should a serious pilot leave behind?”
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `meta/PILOT_SCORECARD_PROTOCOL.md`
- `design/portfolio-selection-rubric-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's execution system:
- **Build-State Evidence** remains the strongest one-project answer overall;
- the strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- the repo now has a canonical answer for **lane proof, artifact proof, decision proof, and steward proof**;
- and every serious pilot can now be judged with an explicit scorecard that ends in **graduate / deepen / fold / delay / kill** instead of vibes.

- New design note: `design/portfolio-pilot-evaluation-2026Q1.md`
- New meta note: `meta/PILOT_SCORECARD_PROTOCOL.md`
- Design/meta refresh: `design/portfolio-selection-rubric-2026Q1.md`, `design/portfolio-execution-sequencing-2026Q1.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep the core portfolio intact; and add a repo-level answer for **what proof should let a serious pilot advance**.
- Hygiene: future pilot-heavy revisions must declare the **lane exercised, artifacts emitted, decisions improved, residue left over, steward cost, and explicit verdict**; do not let one clever prototype, benchmark anecdote, dashboard, or assistant demo silently count as success.


## Latest addition (rev0426)
The archive now has an explicit **Portfolio Selection Rubric** note and a paired **Candidate Triage Protocol**:
**if the repo already has strong seams and execution blueprints, how should it judge new proposals repeatably instead of promoting, delaying, or keeping them by vibe?**

Read first if you want the repo's current answer to “what makes a proposed Rust contribution worthy enough to promote, deep enough to keep, or weak enough to fold or kill?”
- `design/portfolio-selection-rubric-2026Q1.md`
- `meta/CANDIDATE_TRIAGE_PROTOCOL.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's decision system:
- **Build-State Evidence** remains the strongest one-project answer overall;
- the strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- the repo now has a canonical rubric for **recurring pain, substrate readiness, seam clarity, artifact honesty, thin-shippable v0, reuse/multiplier value, and stewardship realism**;
- and the archive now has a small candidate-card protocol so new proposals have to earn promotion instead of drifting into the canon by recency or rhetoric.

- New design note: `design/portfolio-selection-rubric-2026Q1.md`
- New meta note: `meta/CANDIDATE_TRIAGE_PROTOCOL.md`
- Design/frontier/meta refresh: `design/worthy-contribution-shortlist-2026Q1.md`, `design/portfolio-execution-sequencing-2026Q1.md`, `design/strategic-territory-map-2026Q1.md`, `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep the core portfolio intact; and use **Portfolio Selection Rubric** when the question is no longer “which seams exist?” but “what deserves promotion, what deserves deepening, and what should be folded or killed?”
- Hygiene: future proposal revisions must carry ranking class, seam sentence, artifact family, pilot lane, imports, steward story, anti-goals, and fold/kill triggers; do not let a fresh source, security scare, assistant use case, or neat demo silently create another top-band empire.

## Latest addition (rev0425)
The archive now has an explicit **Portfolio Execution Sequencing** note that turns the shortlist + shared-grammar portfolio into a practical staging answer:
**if a serious team, lab, or funder wants to build the archive's best contributions in theory and practice, what should come first, what comes later, and what gates must each stage pass?**

Read first if you want the repo's current answer to “what order should the strongest seams actually be built, staffed, or funded?”
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`
- `design/migration-public-api-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/native-edge-execution-blueprint-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's strongest portfolio answer by making its **staging logic** explicit:
- **Build-State Evidence** remains the strongest one-project answer overall;
- the strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- **Adoption Navigation** and **Native Edge** remain important later consumer/frontier widenings rather than the first generic build steps;
- and the repo now has a canonical answer for **shared spine first, then evidence, then boundary bridges, then recommendation/specialist widenings**.

- New design note: `design/portfolio-execution-sequencing-2026Q1.md`
- Design/frontier/meta refresh: `design/worthy-contribution-shortlist-2026Q1.md`, `design/strategic-territory-map-2026Q1.md`, `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep the four-seam core portfolio intact; and use **Portfolio Execution Sequencing** when the question is no longer “which seams matter?” but “what order should a serious program actually build them?”
- Hygiene: future portfolio revisions must say which **stage**, **gate**, and **stewardship model** they are changing; do not let launch energy outrun maintenance capacity or let later consumer surfaces start pretending they generate their own substrate truth.

## Latest addition (rev0424)
The archive now has an explicit **Portfolio Artifact Conventions** note that turns the shortlist's old “shared artifact conventions” sentence into a concrete repo-level grammar:
**if the archive's best answer is a portfolio of reference layers rather than one mega-tool, what exactly should those layers share without collapsing into one schema empire?**

Read first if you want the repo's current answer to “how should the strongest multi-project contributions line up in theory and practice?”
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`
- `design/migration-public-api-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's strongest **multi-project** answer and adds repo hygiene:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Native Edge Contract** remains the active specialist frontier;
- **Adoption Navigation Contract** remains the strongest anti-tacit-knowledge answer;
- **Package Intake Gateway** remains the most underappreciated operational seam;
- **Semantic Context Contract** remains the hidden multiplier;
- and the strongest portfolio answer now has a concrete **shared reference-layer grammar** for envelope fields, verb families, lineage receipts, and handoff lossiness.

- New design note: `design/portfolio-artifact-conventions-2026Q1.md`
- Design/frontier/meta refresh: `design/worthy-contribution-shortlist-2026Q1.md`, `design/strategic-territory-map-2026Q1.md`, `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep the four-seam portfolio answer intact; and use **Portfolio Artifact Conventions** when the question is no longer “which seams matter?” but “how should the serious seams actually resemble one another?”
- Hygiene: future cross-portfolio revisions must keep **shared envelope grammar**, **seam-specific payload truth**, **lineage/execution receipts**, **consumer-slice lossiness**, and **assistant-derived artifacts** visibly separate; do not let a nice common header silently become a fake universal schema or let seam-specific semantics drift into six incompatible mini-languages.

## Latest addition (rev0423)
The archive now has an explicit **Native Edge execution blueprint** note that turns the current active specialist frontier into a concrete build program:
**if a serious team builds the archive's cross-language / native-adoption answer, what exact artifact families, commands, pilot lanes, and anti-goals should it have?**

Read first if you want the repo's current answer to “what should the archive's specialist frontier actually ship in theory and practice?”
- `design/native-edge-execution-blueprint-2026Q1.md`
- `design/native-edge-contract-2026Q1.md`
- `design/native-edge-stack.md`
- `design/ffi-boundary-kit.md`
- `design/native-dependency-kit.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `PRIORITIES.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's active specialist frontier:
- **Build-State Evidence** remains the strongest single-project contribution overall;
- **Native Edge Contract** remains the active specialist frontier;
- the frontier is now described more concretely as a **portable native-edge reference layer** with explicit subject, boundary, provider/link, host-vs-target/toolchain context, foreign-build handoff, and bounded downstream conclusions;
- **Adoption Navigation Contract** remains the strongest anti-tacit-knowledge answer;
- **Package Intake Gateway** remains the most underappreciated operational seam;
- **Semantic Context Contract** remains the hidden multiplier.

- New design note: `design/native-edge-execution-blueprint-2026Q1.md`
- Design/frontier/meta refresh: `design/native-edge-contract-2026Q1.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/strategic-territory-map-2026Q1.md`, `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep **Native Edge Contract** as the active specialist frontier; and use **Native Edge execution blueprint** when the question is what that frontier should actually build
- Hygiene: future native-edge revisions must preserve **subject truth**, **boundary truth**, **provider/link truth**, **host-vs-target/toolchain context**, **foreign-build handoff**, and **brief/consumer truth** as separate layers; do not let one binding generator, one provider crate, one Corrosion/CMake lane, or one assistant summary silently become the whole story

## Latest addition (rev0422)
The archive now has an explicit **Adoption Navigation execution blueprint** note that turns the current anti-tacit-knowledge winner into a concrete build program:
**if a serious team builds the archive's recommendation / starter-set answer, what exact artifact families, commands, pilot lanes, and anti-goals should it have?**

Read first if you want the repo's current answer to “what should the archive's project-scoped recommendation frontier actually ship in theory and practice?”
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-contract-2026Q1.md`
- `design/reviewable-lane-defaults.md`
- `design/lane-default-renewal-receipts.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `PRIORITIES.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's strongest anti-tacit-knowledge answer:
- **Build-State Evidence** remains the strongest single-project contribution overall;
- **Adoption Navigation Contract** remains the archive's strongest anti-tacit-knowledge answer;
- the answer is now described more concretely as a **portable recommendation-review layer** with explicit question, lane, canon, evidence, local-fit, and handoff truth;
- **Native Edge Contract** remains the active specialist frontier;
- **Package Intake Gateway** remains the most underappreciated operational seam;
- **Semantic Context Contract** remains the hidden multiplier.

- New design note: `design/adoption-navigation-execution-blueprint-2026Q1.md`
- Design/frontier/meta refresh: `design/adoption-navigation-contract-2026Q1.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/strategic-territory-map-2026Q1.md`, `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep **Native Edge Contract** as the active specialist frontier; and use **Adoption Navigation execution blueprint** when the question is what the archive's recommendation frontier should actually build
- Hygiene: future recommendation revisions must preserve **question truth**, **candidate-lane truth**, **canonical-reference truth**, **imported-evidence truth**, **local-fit truth**, and **brief/handoff truth** as separate layers; do not let one curated list, one docs page, one local prototype, or one assistant summary silently become the whole story

## Latest addition (rev0421)
The archive now has an explicit **Migration/Public API execution blueprint** note that turns the portfolio's remaining release / upgrade quadrant into a concrete build program:
**if a serious team builds the archive's Migration/Public API contribution, what exact artifact families, commands, pilot lanes, and anti-goals should it have?**

Read first if you want the repo's current answer to “what should the release-boundary + upgrade-program contribution actually ship in theory and practice?”
- `design/migration-public-api-execution-blueprint-2026Q1.md`
- `design/public-api-contract-2026Q1.md`
- `design/migration-truth-contract-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `PRIORITIES.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's clearest remaining portfolio seam:
- **Build-State Evidence** remains the strongest single-project contribution overall;
- **Migration/Public API** is now described more concretely as a **portable release-boundary + upgrade-program bridge** above imported Public API and Migration Truth evidence;
- **Package Intake Gateway** remains the archive's most underappreciated operationally urgent seam;
- **Native Edge Contract** remains the active specialist frontier;
- **Semantic Context Contract** remains the key hidden multiplier.

- New design note: `design/migration-public-api-execution-blueprint-2026Q1.md`
- Design/frontier/meta refresh: `design/worthy-contribution-shortlist-2026Q1.md`, `design/strategic-territory-map-2026Q1.md`, `design/public-api-contract-2026Q1.md`, `design/migration-truth-contract-2026Q1.md`, `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep **Native Edge Contract** as the active specialist frontier; and use **Migration/Public API execution blueprint** when the question is what the archive's release / upgrade quadrant should actually build
- Hygiene: future release / upgrade revisions must preserve **subject truth**, **exposure/proof truth**, **migration-intent truth**, **change-application truth**, **bounded verification/outcome truth**, and **consumer-handoff truth** as separate layers; do not let one semver diff, one `cargo fix` run, one dependency bump, or one assistant summary silently become the whole story

## Latest addition (rev0420)
The archive now has an explicit **Package Intake Gateway execution blueprint** note that turns the current operational seam into a concrete build program:
**if a serious team builds the archive's most underappreciated urgent seam, what exact artifact families, commands, pilot lanes, and anti-goals should it have?**

Read first if you want the repo's current answer to “what should the package-ingress / extraction / staging boundary actually ship in theory and practice?”
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `design/package-admission-stack.md`
- `design/dependency-review-stack.md`
- `design/consumer-install-kit.md`
- `proposals/epic-package-intake-gateway.md`
- `PRIORITIES.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's strongest operational seam:
- **Build-State Evidence** remains the strongest single-project contribution overall;
- **Package Intake Gateway** remains the archive's most underappreciated operationally urgent seam;
- the seam is now described more concretely as a **portable package-ingress review layer** with explicit route, payload, staging, resolution, and handoff truth;
- **Native Edge Contract** remains the active specialist frontier;
- **Semantic Context Contract** remains the key hidden multiplier.

- New design note: `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- Design/frontier/meta refresh: `design/package-intake-gateway-2026Q1.md`, `design/worthy-contribution-shortlist-2026Q1.md`, `design/strategic-territory-map-2026Q1.md`, `proposals/epic-package-intake-gateway.md`, `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep **Native Edge Contract** as the active specialist frontier; and use **Package Intake Gateway execution blueprint** when the question is what the archive's current operational seam should actually build
- Hygiene: future intake revisions must preserve **subject truth**, **route truth**, **payload truth**, **staging / extraction truth**, **resolution truth**, and **consumer-handoff truth** as separate layers; do not let one scary advisory, one SBOM export, one installer path, or one malware note silently become the whole intake story

## Latest addition (rev0419)
The archive now has an explicit **Semantic Context execution blueprint** note that turns the current hidden multiplier into a concrete build program:
**if a serious team builds Semantic Context, what exact artifact families, commands, pilot lanes, and anti-goals should it have?**

Read first if you want the repo's current answer to “what should the archive's key enabling substrate actually ship in theory and practice?”
- `design/semantic-context-execution-blueprint-2026Q1.md`
- `design/semantic-context-contract-2026Q1.md`
- `design/semantic-context-pilot-program.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `proposals/epic-semantic-context-kit.md`
- `PRIORITIES.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's strongest hidden multiplier:
- **Build-State Evidence** remains the strongest single-project contribution overall;
- **Semantic Context Contract** remains the archive's key hidden multiplier;
- the multiplier is now described more concretely as a **thin semantic-context reference layer** with exact subject capture, ranked lane imports, bounded query budgets, and explicit consumer handoffs;
- **Native Edge Contract** remains the active specialist frontier;
- **Package Intake Gateway** remains the most underappreciated operationally urgent seam.

- New design note: `design/semantic-context-execution-blueprint-2026Q1.md`
- Design/frontier/meta refresh: `design/worthy-contribution-shortlist-2026Q1.md`, `design/strategic-territory-map-2026Q1.md`, `proposals/epic-semantic-context-kit.md`, `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep **Native Edge Contract** as the active specialist frontier; and use **Semantic Context execution blueprint** when the question is what the current hidden multiplier should actually build
- Hygiene: future hidden-multiplier revisions must preserve **subject truth**, **resolution/build-context truth**, **input-lane truth**, **merge/completeness truth**, **query truth**, and **consumer-handoff truth** as separate layers; do not let a stronger blueprint silently become a universal index, a verdict engine, or an assistant blob


## Latest addition (rev0418)
The archive now has an explicit **Build-State Evidence execution blueprint** note that turns the current one-project winner into a concrete build program:
**if a serious team only builds one Rust ecosystem contribution, what should Build-State Evidence actually ship?**

Read first if you want the repo's current answer to “what exact artifact families, commands, pilot lanes, and anti-goals should the strongest one-project answer have?”
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `design/build-state-evidence-stack.md`
- `design/build-state-evidence-pilot-program.md`
- `proposals/epic-build-state-evidence-stack.md`
- `PRIORITIES.md`

This revision deliberately does **not** promote a new frontier.
Instead, it deepens the archive's strongest one-project answer:
- **Build-State Evidence** remains the strongest single-project contribution overall;
- the winner is now described more concretely as a **portable build-review layer above Cargo-native evidence**;
- **Package Intake Gateway** remains the most underappreciated operationally urgent seam and is kept separate from build-state truth;
- **Native Edge Contract** remains the active specialist frontier;
- **Semantic Context Contract** remains the hidden multiplier.

- New design note: `design/build-state-evidence-execution-blueprint-2026Q1.md`
- Design/frontier/meta refresh: `design/worthy-contribution-shortlist-2026Q1.md`, `design/strategic-territory-map-2026Q1.md`, `proposals/epic-build-state-evidence-stack.md`, `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep **Native Edge Contract** as the active specialist frontier; and use **Build-State Evidence execution blueprint** when the question is what the current broad winner should actually build
- Hygiene: future one-project-winner revisions must preserve **observed facts**, **imported facts**, **derived judgments**, and **hypothetical opportunities** as separate truths; do not let a sharper execution plan turn into another build-system empire

## Latest addition (rev0417)
The archive now has an explicit **Worthy Contribution Shortlist** note that turns the broader territory map into an execution-oriented answer:
**if a serious team or funder can only build one or a few Rust ecosystem contributions, what should they actually build, and what should those contributions look like in practice?**

Read first if you want the repo's current answer to “what is the best one-project bet, what is the best multi-project portfolio bet, what specialist frontier is strategically real, and what operational seam is more urgent than its rank might suggest?”
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `design/epic-contribution-ladder-2026.md`
- `design/ecosystem-priority-ladder-2026.md`
- `meta/ACTIVE_FRONTIER.md`
- `PRIORITIES.md`

This revision deliberately does **not** promote a new frontier.
Instead, it makes one execution-oriented synthesis explicit:
- **Build-State Evidence** remains the strongest single-project answer overall;
- **Adoption Navigation Contract** remains the strongest anti-tacit-knowledge answer;
- **Native Edge Contract** remains the active specialist frontier;
- **Package Intake Gateway** is now called out more explicitly as the archive's most underappreciated operationally urgent seam;
- **Semantic Context Contract** remains the key hidden multiplier;
- and the strongest multi-project portfolio answer is now stated more plainly: **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**, with shared artifact conventions and bounded consumer layers.

- New design note: `design/worthy-contribution-shortlist-2026Q1.md`
- Design/frontier/meta refresh: `design/strategic-territory-map-2026Q1.md`, `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep **Native Edge Contract** as the active specialist frontier; and use **Worthy Contribution Shortlist** when the question is execution order, funding order, or one-project-vs-portfolio choice rather than raw frontier promotion
- Hygiene: future execution-oriented revisions must explicitly separate **one-project winner**, **portfolio answer**, **specialist frontier**, **operational urgency seam**, and **hidden multiplier**; do not let one exciting frontier, one scary incident, or one assistant-friendly substrate impersonate all of them

## Latest addition (rev0416)
The archive now has an explicit **Strategic Territory Map** note that answers the broader portfolio question:
**what would actually count as a worthy or even epic Rust contribution right now, after reading the latest archive and fresh official signals?**

Read first if you want the repo’s current answer to “what is Rust really missing beyond individual crates, and which proposals should be built, folded together, or eliminated?”
- `design/strategic-territory-map-2026Q1.md`
- `design/epic-contribution-ladder-2026.md`
- `design/ecosystem-priority-ladder-2026.md`
- `meta/ACTIVE_FRONTIER.md`
- `PRIORITIES.md`

This revision deliberately does **not** promote a new frontier.
Instead, it makes one archive-wide synthesis explicit:
- **Build-State Evidence** still looks like the strongest broad/buildable epic contribution overall;
- **Adoption Navigation Contract** still looks like the strongest anti-tacit-knowledge / recommendation answer;
- **Rust inner-loop contract** still looks like the clearest build/debug bundle-shaping move;
- **Native Edge Contract** remains the latest specialist frontier with especially real industry pressure;
- **Semantic Context Contract** is now called out more clearly as the archive’s most important hidden multiplier for semver/docs/edit/CI/assistant consumers;
- and several tempting “new” ideas should be folded into those seams instead of being promoted as separate empires.

- New design note: `design/strategic-territory-map-2026Q1.md`
- Ladder/frontier/meta refresh: `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`, `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ladder intact; keep **Native Edge Contract** as the active specialist frontier; and use **Strategic Territory Map** when the question is archive-wide ranking, portfolio pruning, or “what worthy contribution should win next?”
- Hygiene: future portfolio revisions must explicitly say whether they are **promotion**, **deepening**, **synthesis with no new promotion**, or **hygiene**; do not let one vivid source, one active frontier, one crate-score idea, or one assistant summary silently rewrite the whole portfolio.

## Latest addition (rev0415)
The archive now has an explicit **Native Edge Contract** note that promotes the existing **Native Edge Stack** into the clearest next **cross-language / native-adoption / external-build-handoff** frontier.

Read first if you want the repo’s current answer to “what worthy Rust contribution should let Rust teams carry reviewed FFI boundaries, native-provider/link decisions, host-vs-target context, and external-build handoffs through one reviewable subject instead of scattering that truth across generated headers, `build.rs`, Cargo logs, and CMake folklore?”
- `design/native-edge-contract-2026Q1.md`
- `design/native-edge-stack.md`
- `design/native-edge-pilot-program.md`
- `design/native-edge-cpp-lane-map.md`
- `design/ffi-boundary-kit.md`
- `design/native-dependency-kit.md`
- `gaps/native-edge-adoption-boundaries-provider-locks-and-build-handoffs.md`
- `proposals/epic-native-edge-stack.md`
- `meta/ACTIVE_FRONTIER.md`

This revision deliberately does **not** rewrite the broad ladder.
Instead, it sharpens a Tier-A seam the archive already knew about: **FFI Boundary** still answers Rust↔native boundary truth; **Native Dependency** still answers provider/link truth; **Toolchain Productization** still answers provisioned toolchains and sysroot/runtime-analysis lanes; **Polyglot Productization** still answers shipped mixed-language product surfaces; but **Native Edge Contract** now answers the missing boundary for **reviewed native-edge subject truth, imported boundary/provider facts, host-vs-target/toolchain context, external-build handoff, and bounded downstream conclusions**.

- New design note: `design/native-edge-contract-2026Q1.md`
- Design/proposal/gap refresh: `design/native-edge-stack.md`, `proposals/epic-native-edge-stack.md`, `gaps/native-edge-adoption-boundaries-provider-locks-and-build-handoffs.md`, `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `INDEX.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact; keep **Public API Contract** as the release-boundary seam; and promote **Native Edge Contract** as the clearest next **cross-language / native-adoption / external-build-handoff** move
- Hygiene: future native-edge revisions must keep **boundary truth**, **provider/link truth**, **host-vs-target/toolchain context**, **external-build handoff**, and **consumer conclusions** visibly separate instead of letting one binding generator, one provider lock, one CMake bridge, or one support summary rewrite the whole story


## Latest addition (rev0414)
The archive now has an explicit **Public API Contract** note that promotes the existing **Public API Kit** into the clearest next **release-boundary / semver-evidence-shaping** frontier.

Read first if you want the repo’s current answer to “what worthy Rust contribution should let Rust library teams carry public-boundary identity, declared-vs-inferred exposure drift, structural diffs, witness-backed type compatibility evidence, MSRV bounds, waivers, and later publish/policy/migration/downstream claims through one reviewable handoff instead of scattering that truth across rustdoc JSON, CI logs, and release prose?”
- `design/public-api-contract-2026Q1.md`
- `design/public-api-kit.md`
- `design/public-api-pilot-program.md`
- `gaps/public-api-boundaries-exposure-diffs-semver-and-msrv-handoffs.md`
- `proposals/epic-public-api-kit.md`
- `meta/ACTIVE_FRONTIER.md`

This revision deliberately does **not** rewrite the broad ladder.
Instead, it sharpens a Tier-A seam the archive already knew about: **Semantic Context** still answers broad analysis authority; **Compatibility Claims** still answers support-envelope truth; **Migration Truth** still answers source→destination change programs; **Publisher & Source Identity** still answers who published and by what route; but **Public API Contract** now answers the missing boundary for **public-boundary subject truth, exposure truth, structural-diff truth, witness/type-proof truth, bounded verification truth, and consumer handoff**.

- New design note: `design/public-api-contract-2026Q1.md`
- New gap note: `gaps/public-api-boundaries-exposure-diffs-semver-and-msrv-handoffs.md`
- Design/proposal refresh: `design/public-api-kit.md`, `design/public-api-pilot-program.md`, `proposals/epic-public-api-kit.md`, `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `INDEX.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact, keep **Migration Truth Contract** as the change-program seam, and promote **Public API Contract** as the clearest next **release-boundary / semver-evidence-shaping** move
- Hygiene: future public-API revisions must keep **public-boundary subject**, **exposure**, **structural diff**, **witness/type proof**, **bounded verification**, and **consumer handoff** visibly separate instead of letting one diff tool, one semver lint run, one nightly rustdoc export, or one green publish check rewrite the whole story


## Latest addition (rev0413)
The archive now has an explicit **Migration Truth Contract** note that promotes the existing **Migration Truth Stack** into the clearest next **change-program / upgrade-shaping** frontier.

Read first if you want the repo’s current answer to “what worthy Rust contribution should let Rust teams carry edition upgrades, `rust-version` ratchets, dependency/API migrations, docs/support checks, waivers, and final release/support claims through one reviewable handoff instead of scattering the truth across `cargo fix`, CI, and maintainer memory?”
- `design/migration-truth-contract-2026Q1.md`
- `design/migration-truth-stack.md`
- `design/migration-pilot-program.md`
- `gaps/upgrade-choreography-and-reviewable-migrations.md`
- `proposals/epic-migration-truth-stack.md`
- `meta/ACTIVE_FRONTIER.md`

This revision deliberately does **not** rewrite the broad ladder.
Instead, it sharpens a Tier-A seam the archive already knew about: **Reviewable Edit Contract** still answers candidate→selection→application→verification; **Compatibility Claims** still answers support-envelope truth; **Semantic Context** still answers analysis authority; **Distribution** and **Update Continuity** still answer delivered artifacts over time; but **Migration Truth Contract** now answers the missing boundary for **source state, destination intent, suggested-vs-applied edits, imported compatibility/support/docs/downstream evidence, waivers, and bounded downstream claims**. The current official signals make that distinction more important than it used to be: the Edition Guide still treats migration as a staged workflow; Cargo’s docs still require multiple `cargo fix --edition` runs across features/targets; Rust 1.85 says automatic fixes are conservative and not recommendations; Cargo’s 1.90 work says the current fix architecture is slow and awkward for selective/interactive flows; Cargo’s `rust-version` docs say mixed workspace policies complicate verification; public/private dependencies plus cargo-semver-checks are still on the path toward Cargo integration; docs.rs now hosts rustdoc JSON; and the 2025 survey still says docs are canonical while machine-mediated use rises.

- New design note: `design/migration-truth-contract-2026Q1.md`
- Design/proposal/gap refresh: `design/migration-truth-stack.md`, `gaps/upgrade-choreography-and-reviewable-migrations.md`, `proposals/epic-migration-truth-stack.md`, `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `INDEX.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact, keep **Toolchain Productization Contract** as the toolchain seam, and promote **Migration Truth Stack / Migration Truth Contract** as the clearest next **change-program / upgrade-shaping** move
- Hygiene: future migration revisions must keep **source state**, **destination intent**, **mechanical edit truth**, **compatibility/support/docs/downstream import truth**, **run/outcome truth**, and **consumer handoff** visibly separate instead of letting one `cargo fix` run, one green CI pass, or one upgrade PR rewrite the whole story

## Latest addition (rev0412)
The archive now has an explicit **Toolchain Productization Contract** note that promotes the existing **Toolchain Productization Stack** into the clearest next **toolchain-variant / sysroot / runtime-analysis-shaping** frontier.

Read first if you want the repo’s current answer to “what worthy Rust contribution should give Rust teams one reviewable handoff for provisioned toolchains, rebuilt stdlib profiles, activation/reuse posture, instrumented-runtime lanes, and later firmware/release/safety/support imports without becoming another toolchain manager?”
- `design/toolchain-productization-contract-2026Q1.md`
- `design/toolchain-productization-stack.md`
- `design/toolchain-productization-lane-map.md`
- `gaps/toolchain-variants-sysroots-cross-builds-and-sanitizer-support-contracts.md`
- `proposals/epic-toolchain-productization-stack.md`
- `meta/ACTIVE_FRONTIER.md`

This revision deliberately does **not** rewrite the broad ladder.
Instead, it sharpens a Tier-A seam the archive already knew about: **Workspace Environment** still answers setup/realization/observation/handoff; **Toolchain Productization Contract** answers provisioned toolchain identity, stdlib/sysroot profile identity, activation/reuse posture, runtime-analysis truth, and bounded consumer claims. The current official signals make that distinction more important than it used to be: 2026 flagships still put rebuild-std and larger-build-system integration in the top band; the build-std goal is explicitly aiming at a stabilizable MVP; current Cargo docs still keep `-Z build-std` nightly/`rust-src`/all-invocations constrained; rustup still separates targets, profiles, and overrides; custom targets still require compiler pinning; sanitizer work still points at precompiled instrumented standard libraries; and Rust for Linux plus CPython show the pressure is broader than one embedded niche.

- New design note: `design/toolchain-productization-contract-2026Q1.md`
- Design/proposal/gap refresh: `design/toolchain-productization-stack.md`, `gaps/toolchain-variants-sysroots-cross-builds-and-sanitizer-support-contracts.md`, `proposals/epic-toolchain-productization-stack.md`, `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `AGENTS.md`, `INDEX.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact, keep **Workspace Environment Contract** as the environment seam, and promote **Toolchain Productization Stack / Toolchain Productization Contract** as the clearest next **toolchain-variant / sysroot / runtime-analysis** move
- Hygiene: future toolchain / sysroot / sanitizer revisions must keep **provisioning**, **stdlib/sysroot-profile**, **activation/reuse**, **runtime-analysis**, **support/compatibility**, and **consumer handoff** visibly separate instead of letting one override, one cache, or one CI lane rewrite the whole story


## Latest addition (rev0411)
The archive now has an explicit **Benchmark Evidence Contract** note that promotes the existing benchmark/performance substrate into the clearest next **performance-claim / compare-shaping** frontier.

Read first if you want the repo's current answer to “what worthy Rust contribution should connect `cargo bench`, Criterion baselines, Divan counters, nextest runner imports, Iai-Callgrind profiler lanes, CodSpeed hosted adapters, and later Perf Labs/release/CI consumers without flattening them into one dashboard or one score?”
- `design/benchmark-evidence-contract-2026Q1.md`
- `design/benchmark-evidence-kit.md`
- `design/benchmark-evidence-lane-map.md`
- `design/benchmark-evidence-pilot-program.md`
- `gaps/benchmark-evidence-subjects-lanes-baselines-and-imports.md`
- `proposals/epic-benchmark-evidence-kit.md`

This revision deliberately does **not** re-rank the whole archive and does **not** demote the existing adoption, maintenance, defect-escalation, or build/debug seams.
Instead, it sharpens one already-present resource/performance frontier that current official and primary tool signals now make much more concrete: Cargo's benchmark surface is still plural and `#[bench]` remains unstable; Rust 1.94 widened workspace benchmark selection; nextest now has an experimental benchmark lane with benchmark-specific configuration; Criterion still has a native baseline story while `cargo-criterion` still lacks baseline support; Divan makes counter semantics explicit; Iai-Callgrind keeps deterministic profiler-backed metrics and raw attachments first-class; CodSpeed keeps hosted adapter plurality explicit; rustc-perf continues to emphasize comparison within declared configurations; and Cargo report/build-analysis work keeps normalizing machine-readable evidence elsewhere in the toolchain.

- New design note: `design/benchmark-evidence-contract-2026Q1.md`
- Design/proposal/gap refresh: `design/benchmark-evidence-kit.md`, `design/benchmark-evidence-lane-map.md`, `design/benchmark-evidence-pilot-program.md`, `proposals/epic-benchmark-evidence-kit.md`, `gaps/benchmark-evidence-subjects-lanes-baselines-and-imports.md`, `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `INDEX.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact; keep **Harness Protocol**, **Test Run Evidence**, **Cargo Report**, and **Perf Labs** as neighboring layers; and promote **Benchmark Evidence Contract** as the clearest next **performance-claim / compare-shaping** move rather than another benchmark engine, scorecard, or screenshot-first dashboard
- Hygiene: future benchmark-evidence revisions should keep **subject**, **measurement lane**, **collector/configuration**, **baseline**, **verdict**, and **consumer handoff** visibly separate; do not let one Criterion baseline, one nextest import, one callgrind trace, one CodSpeed report, or one assistant benchmark summary silently become the whole performance story

## Latest addition (rev0410)
The archive now has an explicit **Defect Escalation Contract** note for the missing boundary between **what a Rust user actually observed locally**, **what minimized subject still reproduces**, **what target and duplicate posture are honest**, and **what downstream issue / regression-test / fix consumers may legitimately import**.

Read first if you want the repo's current answer to “what worthy Rust contribution should connect cargo-script reproducers, Cargo report evidence, rustc issue triage, duplicate search, and regression-test handoff without flattening them into one issue template or one auto-file bot?”
- `design/defect-escalation-contract-2026Q1.md`
- `design/defect-escalation-stack.md`
- `design/prototype-elevation-stack.md`
- `design/cargo-report-kit.md`
- `design/debuggability-stack.md`
- `gaps/defect-escalation-minimal-repros-routing-and-regression-handoffs.md`
- `proposals/epic-defect-escalation-stack.md`

This revision deliberately does **not** re-rank the whole archive and does **not** demote the current adoption, maintenance, distribution, or build/debug seams.
Instead, it sharpens one already-present frontier that current Rust signals now make much more concrete: the 2025H2 goals explicitly say `cargo script` should make reproducible bug reports easier; the February 2026 program update says single-file Rust makes minimal reproducers and quick prototypes materially easier to share; Forge triage already treats reproductions, MCVEs, and bisections as first-class routing state; the rustc-dev-guide says bug fixes should land with succinct regression tests; libtest JSON work is explicitly about moving reporting responsibility upward to runners/Cargo; and Cargo's build-analysis/report work keeps making local evidence more machine-usable.

- New design note: `design/defect-escalation-contract-2026Q1.md`
- Design/proposal/gap refresh: `design/defect-escalation-stack.md`, `proposals/epic-defect-escalation-stack.md`, `gaps/defect-escalation-minimal-repros-routing-and-regression-handoffs.md`, `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `INDEX.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact; keep **cargo-script / ScriptKit** as the tiny-subject lane, **Cargo Report** and **Debuggability** as evidence imports, and promote **Defect Escalation Contract** as the clearest next **upstream-routing / repro-to-regression-handoff** move rather than another issue template, crash uploader, or auto-filing assistant
- Hygiene: future defect-escalation revisions should keep **observation**, **minimization lineage**, **routing/dedup posture**, **regression-test candidacy**, and **consumer handoff** visibly separate; do not let one Markdown snippet, one MCVE, one duplicate guess, one triage label set, or one assistant-generated issue body silently become the whole escalation story

## Latest addition (rev0409)
The archive now has an explicit **Adoption Navigation Contract** note for the missing boundary between **what Rust stack question is being asked**, **which lanes are serious candidates**, **which canonical references and imported evidence shaped the answer**, **what local-fit checks were actually run**, and **what the final brief may honestly claim downstream**.

Read first if you want the repo's current answer to “what worthy Rust contribution should connect Atlas lane maps, reviewable lane defaults, maintainer-authored canon, trust/maintenance/support evidence, local-fit grounding, and bounded human/platform/assistant briefs without flattening them into one blessed-crates page?”
- `design/adoption-navigation-contract-2026Q1.md`
- `design/adoption-navigation-bundle.md`
- `design/adoption-decision-stack.md`
- `design/reviewable-lane-defaults.md`
- `design/lane-default-renewal-receipts.md`
- `proposals/epic-adoption-navigation-bundle.md`
- `gaps/ecosystem-navigation-and-reference-stacks.md`

This revision deliberately does **not** re-rank the whole archive and does **not** fold navigation into trust, maintenance, or canonical learning.
Instead, it sharpens an already-present seam that recent official and primary-project signals make newly concrete: Rust now names **choice paralysis** and **tacit knowledge** directly; docs remain canonical while LLM/editor mediation rises; users still lack a clear place to get advice on a good starter set of crates; docs.rs and crates.io both expose more drift-sensitive decision inputs; and the Foundation now treats adoption growth, maintenance, and infrastructure as one strategic system.

- New design note: `design/adoption-navigation-contract-2026Q1.md`
- Design/proposal/gap refresh: `design/adoption-navigation-bundle.md`, `proposals/epic-adoption-navigation-bundle.md`, `gaps/ecosystem-navigation-and-reference-stacks.md`, `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `INDEX.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep **Build-State Evidence** as the strongest broad/buildable epic contribution; treat **Adoption Navigation Contract** as the strongest explicit anti-tacit-knowledge frontier; and keep **Reviewable Lane Defaults + renewal receipts** as the execution seam beneath it


## Latest addition (rev0408)
The archive now has an explicit **Maintenance Reality Contract** note for the missing boundary between **what a Rust project declares about support and succession**, **what its stewardship machinery actually looks like in operation**, and **what downstream Atlas/trust/release/fund/assistant consumers may honestly conclude from those facts**.

Read first if you want the repo's current answer to “what worthy Rust contribution should connect lifecycle declarations, queue policy, queue snapshots, review pressure, explicit help requests, mentoring capacity, and restricted/public maintenance views without flattening them into one health badge?”
- `design/maintenance-reality-contract-2026Q1.md`
- `design/maintenance-reality-stack.md`
- `design/maintenance-reality-lane-map.md`
- `design/lifecycle-ledger-kit.md`
- `design/stewardship-ops-kit.md`
- `proposals/epic-maintenance-reality-stack.md`
- `gaps/maintenance-operations-and-stewardship-queues.md`

This revision deliberately does **not** re-rank the whole archive and does **not** fold maintenance into trust, release, or funding.
Instead, it sharpens an already-present seam that recent official and primary-project signals make newly concrete: the Rust Foundation now treats **Sustainable Maintenance** as a strategic pillar; the Maintainers Fund centers consistent, transparent, long-term support; the ecosystem is actively defining what maintenance labor counts; compiler operations and Forge triage already expose queue/routing semantics; and docs remain canonical while machine-mediated use rises, which increases the value of bounded maintenance handoffs.

- New design note: `design/maintenance-reality-contract-2026Q1.md`
- Design/proposal/gap refresh: `design/maintenance-reality-stack.md`, `gaps/maintenance-operations-and-stewardship-queues.md`, `proposals/epic-maintenance-reality-stack.md`, `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `INDEX.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact; keep **Lifecycle Ledger** and **Stewardship Ops** as the lower leaves; and promote **Maintenance Reality Contract** as the clearest next **stewardship / continuity / support-routing** move


## Latest addition (rev0407)
The archive now has an explicit **Distribution Contract** note for the missing boundary between **what release and route facts were imported into consumer delivery** and **what install/update/support/policy consumers may honestly conclude from the selected acquisition path and resulting ownership state**.

Read first if you want the repo's current answer to “what worthy Rust contribution should connect `cargo install`, cargo-dist, `cargo-binstall`, release-plz, mirrors, package-manager imports, and ownership/uninstall truth without flattening them into one installer or one release manifest?”
- `design/distribution-contract-2026Q1.md`
- `design/distribution-contract-stack.md`
- `design/distribution-contract-pilot-program.md`
- `design/consumer-install-kit.md`
- `design/update-continuity-kit.md`
- `design/consumer-lifecycle-continuity-bundle.md`
- `proposals/epic-distribution-contract-stack.md`

This revision deliberately does **not** re-rank the whole archive and does **not** fold delivery into publication identity or lifecycle continuity.
Instead, it sharpens an already-present seam that recent official and primary project signals make newly concrete: `cargo install` still defines its own route/root/lock behavior; Cargo still treats installed-binary updates as plugin territory; rustup is clarifying managed-content ownership in shared paths; cargo-dist now exposes explicit build/distribute phases, machine-readable manifests, mirror fallback, and installer-hardening work; cargo-binstall explicitly models artifact search plus fallback; and release-plz keeps producer-side release automation increasingly standardized.

- New design note: `design/distribution-contract-2026Q1.md`
- Design/proposal refresh: `design/distribution-contract-stack.md`, `proposals/epic-distribution-contract-stack.md`, `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `INDEX.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact; keep **Consumer Lifecycle Continuity Bundle** as the broader consumer-side composition point; keep **Publisher & Source Identity Contract** upstream and **Update Continuity Kit** downstream; and promote **Distribution Contract** as the clearest next **delivery / acquisition / ownership-shaping** move


## Latest addition (rev0406)
The archive now has an explicit **Publisher & Source Identity Contract** note for the missing boundary between **who may publish and what is being claimed** and **what later trust, package-admission, install, support, and incident consumers may honestly conclude from those identity facts**.

Read first if you want the repo's current answer to “what worthy Rust contribution should connect owners, team owners, Trusted Publishing, optional namespaces, alternate registries, exact-copy replacement sources, and packaging-time source hints without flattening them into one registry badge or one provenance claim?”
- `design/publisher-source-identity-contract-2026Q1.md`
- `design/publisher-source-identity-stack.md`
- `design/org-identity-registry-ux-kit.md`
- `design/trust-decision-stack.md`
- `proposals/epic-publisher-source-identity-stack.md`
- `gaps/publisher-source-identity-authority-claims-and-source-posture-continuity.md`

This revision deliberately does **not** re-rank the whole archive and does **not** fold publication identity into intake or trust.
Instead, it sharpens an already-present seam that recent official and primary project signals make newly concrete: crates.io now supports multi-provider Trusted Publishing and Trusted-Publishing-only mode; Cargo explicitly distinguishes named owners, team owners, alternate registries, and replacement sources; RFC 3243 keeps namespace control live; RFC 3052 makes current owners rather than manifest authors the durable UI-facing identity plane; `cargo package` says VCS hints are not verified provenance; and verification/mirroring work increases the value of keeping route/source posture separate from claim posture.

- New design note: `design/publisher-source-identity-contract-2026Q1.md`
- Design/proposal/gap refresh: `design/publisher-source-identity-stack.md`, `gaps/publisher-source-identity-authority-claims-and-source-posture-continuity.md`, `proposals/epic-publisher-source-identity-stack.md`, `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `INDEX.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact; keep **Package Intake Gateway** as the local-ingress seam and **Trust Decision Stack** as the downstream trust/policy seam; and promote **Publisher & Source Identity Contract** as the clearest next **publication / authority / route-shaping** move


## Latest addition (rev0405)
The archive now has an explicit **Observability Contract** note for the missing boundary between **what a Rust subject emits and activates at runtime** and **what operators, support, release, incident, and assistant consumers may honestly conclude from that telemetry posture**.

Read first if you want the repo's current answer to “what worthy Rust contribution should connect `tracing`, `tracing-subscriber`, `tracing-log`, `metrics`, OpenTelemetry, Tokio Console, runtime/export activation, and support/docs truth without flattening them into one backend or one dashboard?”
- `design/observability-contract-2026Q1.md`
- `design/observability-productization-stack.md`
- `design/observability-kit.md`
- `design/diagnostic-surface-kit.md`
- `design/runtime-settings-kit.md`
- `proposals/epic-observability-productization-stack.md`
- `gaps/observability-products-telemetry-runtime-diagnostics-and-support-contracts.md`

This revision deliberately does **not** re-rank the whole archive and does **not** demote the current build/debug/tooling contracts.
Instead, it sharpens an already-present seam that recent official and primary project signals make newly concrete: the 2025 State of Rust survey still says resource usage is high, debugging remains a notable pain, docs remain the canonical reference, and agentic editors are rising; `tracing` and `tracing-subscriber` keep composition explicit; `metrics` still presents a facade rather than one universal metrics runtime; OpenTelemetry's Rust docs still mark traces, metrics, and logs as **Beta**; OpenTelemetry's own governance work says complexity and lack of stability impede production deployments; OpenTelemetry Weaver argues for observability-by-design with schema validation; Tokio Console already uses a distinct protocol and subscriber layer for async diagnostics; Cargo 1.94 and `cargo report` make machine-readable reporting more normal; OTLP remains the default SDK exporter and opentelemetry-rust recommends it for production, while `opentelemetry-jaeger` is now explicitly unmaintained.

- New design note: `design/observability-contract-2026Q1.md`
- Design/proposal/gap refresh: `design/observability-productization-stack.md`, `gaps/observability-products-telemetry-runtime-diagnostics-and-support-contracts.md`, `proposals/epic-observability-productization-stack.md`, `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `INDEX.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact; keep **Safety-Critical Assurance Contract** as the clearest current high-assurance seam; and promote **Observability Contract** as the clearest next **runtime telemetry / support / handoff-shaping** move rather than another backend wrapper, exporter preference memo, or dashboard-first tool

## Latest addition (rev0404)
The archive now has an explicit **Safety-Critical Assurance Contract** note for the missing boundary between **what high-assurance Rust evidence exists** and **what a release, audit, or qualification-prep consumer may honestly conclude from it**.

Read first if you want the repo's current answer to “what worthy Rust contribution should connect normative `unsafe` docs, FLS/spec cadence, safety-critical lint profiles, criterion-aware coverage, sanitizer/proof imports, and waiver-aware handoffs without flattening them into one certification badge?”
- `design/safety-critical-assurance-contract-2026Q1.md`
- `design/safety-critical-evidence-stack.md`
- `design/safety-evidence-kit.md`
- `design/coverage-evidence-kit.md`
- `design/conformance-traceability-stack.md`
- `proposals/epic-safety-critical-evidence-stack.md`
- `gaps/unsafe-and-verification-evidence.md`

This revision deliberately does **not** promote the whole archive around safety-critical work. Instead, it sharpens an already-present seam that recent official signals make newly concrete: Rust's 2026 roadmap now names **Safety-Critical Rust** as a flagship theme with explicit milestones for MC/DC coverage, normative unsafe docs, Clippy linting, and FLS release cadence; the January 2026 safety-critical writeup says evidence and verification pressure rises sharply with criticality; the standard-library contracts effort and experimental `core::contracts` module make machine-readable contracts more real; and rustc coverage docs already show that criterion-aware evidence has to stay honest about engine, flags, doctests, and comparability.

- New design note: `design/safety-critical-assurance-contract-2026Q1.md`
- Proposal/gap refresh: `proposals/epic-safety-critical-evidence-stack.md`, `gaps/unsafe-and-verification-evidence.md`
- Stack refresh: `design/safety-critical-evidence-stack.md`
- Ladder refresh: `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact; keep **Harness Protocol Contract** as the clearest current testing seam; and promote **Safety-Critical Assurance Contract** as the clearest next **high-assurance / evidence-shaping** move

## Latest addition (rev0403)
The archive now has an explicit **Harness Protocol Contract** note for the missing boundary between **what a Rust harness declares before execution** and **what runners, IDEs, CI, and downstream evidence layers do with that truth**.

Read first if you want the repo's current answer to “what worthy Rust contribution should connect libtest, custom harnesses, benches, doctests, Cargo UX, alternate runners, and IDE tooling without flattening them into one universal runner?”
- `design/harness-protocol-contract-2026Q1.md`
- `design/harness-protocol-kit.md`
- `design/harness-protocol-pilot-program.md`
- `proposals/epic-harness-protocol-kit.md`
- `gaps/testing-harness-protocols-and-benchmark-interop.md`
- `design/test-execution-evidence-stack.md`

This revision deliberately does **not** promote the whole test-execution stack at once.
Instead, it sharpens the upstream testing seam that recent official signals make newly concrete: Rust's 2026 roadmap now names **better test tooling** under **Building blocks**; RFC 3455 already framed testing as a cross-component concern; the libtest-JSON goal explicitly wants reporting to shift upward toward Cargo while lowering the barrier for custom harnesses and custom runners; Cargo 1.94 still lists that work as unfinished; and Cargo's bench/doctest/custom-harness surface remains plural and partly unstable.

- New design note: `design/harness-protocol-contract-2026Q1.md`
- Proposal/gap refresh: `proposals/epic-harness-protocol-kit.md`, `gaps/testing-harness-protocols-and-benchmark-interop.md`
- Ladder refresh: `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact; keep **Semantic Context Contract** as the clearest current context/authority seam; and promote **Harness Protocol Contract** as the clearest next **testing / runner / adapter-shaping** move

## Latest addition (rev0402)
The archive now has an explicit **semantic context contract** note that promotes the existing **Semantic Context Kit** into the clearest next **context / authority / consumer-shaping** frontier.

Read first if you want the repo’s current answer to “what worthy Rust contribution should let semver tooling, docs fronts, compiler-attached tools, fix workflows, IDEs, CI, and assistant consumers share one reviewable semantic subject/context boundary without becoming another universal Rust index?”
- `design/semantic-context-contract-2026Q1.md`
- `design/semantic-context-kit.md`
- `design/semantic-context-lane-map.md`
- `design/semantic-context-pilot-program.md`
- `gaps/cross-crate-semantic-context-and-analysis-inputs.md`
- `proposals/epic-semantic-context-kit.md`
- `design/epic-contribution-ladder-2026.md`

This revision deliberately does **not** rewrite the broad ladder and does **not** replace the rev0394 inner-loop bet, the rev0395 package-intake seam, the rev0396 compatibility-claims move, the rev0397 proc-macro-transition move, the rev0398 artifact-contract promotion, the rev0399 build-interop promotion, the rev0400 workspace-environment promotion, or the rev0401 reviewable-edit promotion.
Instead, it promotes an already-present frontier candidate because the current official signals are unusually aligned: Cargo's accepted plumbing goal says the current machine-facing surface is too porcelain-oriented and that `cargo metadata` excludes feature resolution; the `cargo-semver-checks` goal keeps cross-crate items and type information on the critical path for eventual Cargo integration; the July 2025 goals update says docs.rs-hosted rustdoc JSON helps as a cache but recursive active dependency features are still missing from Cargo interfaces and `rmeta`-based combination is still needed; docs.rs now hosts rustdoc JSON directly and warns consumers that `format_version` matters; the StableMIR publication goal plus the `rustc_public` GSoC work make versioned compiler-facing tooling inputs more real; Cargo 1.93 says plugins matter and schema work around structured outputs is active; and the 2025 State of Rust survey says docs remain canonical while editor/LLM-mediated learning rises.

- New design note: `design/semantic-context-contract-2026Q1.md`
- Design/proposal/gap refresh: `design/semantic-context-kit.md`, `gaps/cross-crate-semantic-context-and-analysis-inputs.md`, `proposals/epic-semantic-context-kit.md`, `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact, keep the current Cargo-facing and edit-facing seams intact, and promote **Semantic Context Kit / Semantic Context Contract** as the clearest next **context / authority / consumer-shaping** move beneath **Semantic Context + Compiler Extensibility + Reviewable Edit + Canonical Learning + Adoption Decision**
- Hygiene: future semantic-context revisions should keep **subject identity**, **authority lane**, **merge/completeness**, **query/result**, **consumer slice**, and **comparison/handoff** visibly separate; do not let one docs.rs cache, one local rustdoc JSON build, one Cargo fallback, one compiler export, or one assistant context slice silently become the whole story


## Latest addition (rev0401)
The archive now has an explicit **reviewable edit contract** note that promotes the existing **Edit Workflow Kit** into the clearest next **mutation / review / handoff-shaping** frontier.

Read first if you want the repo’s current answer to “what worthy Rust contribution should let compiler suggestions, edition migrations, IDE refactors, CI bots, and assistant proposals enter normal Rust review as explicit candidate → selection → application → verification chains without becoming another one-true refactoring platform?”
- `design/reviewable-edit-contract-2026Q1.md`
- `design/edit-workflow-kit.md`
- `design/edit-governance-pilot-program.md`
- `gaps/reviewable-edits-code-actions-and-refactors.md`
- `proposals/epic-edit-workflow-kit.md`
- `design/epic-contribution-ladder-2026.md`

This revision deliberately does **not** rewrite the broad ladder and does **not** replace the rev0394 inner-loop bet, the rev0395 package-intake seam, the rev0396 compatibility-claims move, the rev0397 proc-macro-transition move, the rev0398 artifact-contract promotion, the rev0399 build-interop promotion, or the rev0400 workspace-environment promotion.
Instead, it promotes an already-present frontier candidate because the current official signals are unusually aligned: `cargo fix` is mainstream but configuration-bounded; the Edition Guide says migration can require multiple passes, `--broken-code`, and manual cleanup; Cargo 1.90 says the current `cargo fix` architecture is slow and hard to make selective or interactive; the GSoC 2025 `cargo-fixit` prototype shows a top-level controlled alternative is viable; Cargo 1.93 says schema work could unlock a faster and more flexible future; the StableMIR publication goal says Rust wants semver-governed public compiler-facing crates for analyzers, linters, and development environments; and the 2025 State of Rust survey says online docs remain canonical while editors with agentic support are rising.

- New design note: `design/reviewable-edit-contract-2026Q1.md`
- Design/proposal/gap refresh: `design/edit-workflow-kit.md`, `design/edit-governance-pilot-program.md`, `gaps/reviewable-edits-code-actions-and-refactors.md`, `proposals/epic-edit-workflow-kit.md`, `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact, keep the current Cargo-facing seams intact, and promote **Edit Workflow Kit / Reviewable Edit Contract** as the clearest next **mutation / review / handoff-shaping** move beneath **Edit Workflow + Lint Governance + Migration + Compiler Extensibility**
- Hygiene: future edit/mutation revisions should keep **subject/context**, **candidate provenance**, **selection/ordering**, **application**, **verification**, and **consumer handoff** visibly separate; do not let one `cargo fix` run, one editor assist, one migration pass, or one assistant patch silently become the whole story

## Latest addition (rev0400)
The archive now has an explicit **workspace environment contract** note that promotes the existing **Workspace Environment Stack** into the clearest next **environment / realization / observation / handoff-shaping** frontier.

Read first if you want the repo’s current answer to “what worthy Rust contribution should connect workspace discovery, Cargo/rustup precedence, toolchain/native/service requirements, host/container/Nix/CI realizations, secret posture, and bounded human/editor/CI/agent handoffs without becoming another one-true dev environment platform?”
- `design/workspace-environment-contract-2026Q1.md`
- `design/workspace-environment-stack.md`
- `design/workspace-environment-bundle.md`
- `gaps/workspace-environments-onboarding-and-agent-safe-dev-contracts.md`
- `proposals/epic-workspace-environment-stack.md`
- `design/epic-contribution-ladder-2026.md`

This revision deliberately does **not** rewrite the broad ladder and does **not** replace the rev0394 inner-loop bet, the rev0395 package-intake seam, the rev0396 compatibility-claims move, the rev0397 proc-macro-transition move, the rev0398 artifact-contract promotion, or the rev0399 build-interop promotion.
Instead, it promotes an already-present frontier candidate because the current official signals are unusually aligned: the 2025 State of Rust survey says resource usage remains painful while online docs remain canonical and editors with agentic support are rising; Cargo config and workspace discovery both walk parent directories and change behavior based on discovery root; rustup override selection also walks the directory tree; Cargo 1.94 explicitly says broken parent manifests or `.cargo/config.toml` files can fail unrelated builds; rust-analyzer already exposes override commands, invocation strategies, extra args/env, linked-workspace behavior, and target-dir tradeoffs; and Dev Containers plus Nix are real reproducible realization substrates without being a Rust-specific review layer.

- New design note: `design/workspace-environment-contract-2026Q1.md`
- Design/proposal/gap refresh: `design/workspace-environment-stack.md`, `design/workspace-environment-bundle.md`, `gaps/workspace-environments-onboarding-and-agent-safe-dev-contracts.md`, `proposals/epic-workspace-environment-stack.md`, `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact, keep **Rust inner-loop contract** as the clearest build/debug bundle-shaping move, keep **Cargo artifact contract** as the explicit final-output / handoff seam, keep **Cargo build interop contract** as the explicit workspace-graph / plan / event seam, and promote **Workspace Environment Stack / Workspace Environment Contract** as the clearest next **environment / realization / observation / handoff-shaping** move beneath Tooling Contract + Toolchain Productization + Native Dependency + Runtime Settings + Credentials
- Hygiene: future environment/setup revisions should keep **subject/discovery truth**, **declared-intent truth**, **realization truth**, **secret posture truth**, **observation/drift truth**, and **consumer-handoff truth** visibly separate; do not let one `rust-toolchain.toml`, one `.cargo/config.toml`, one devcontainer, one flake, one editor override, or one successful local run silently become the whole story

## Latest addition (rev0399)
The archive now has an explicit **Cargo build interop contract** note that promotes the existing **Build Interop Kit** into the clearest next **workspace-graph / plan / event / adapter-shaping** frontier for Cargo in larger build systems.

Read first if you want the repo's current answer to “what worthy Rust contribution should connect workspace discovery, Cargo/native and non-Cargo graph identity, build intent, execution events, and adapter handoffs for IDEs / CI / wrappers / monorepos without becoming another one-true build system?”
- `design/cargo-build-interop-contract-2026Q1.md`
- `design/build-interop-kit.md`
- `gaps/build-system-interop-and-cargo-plumbing.md`
- `proposals/epic-build-interop-kit.md`
- `design/cargo-artifact-contract-2026Q1.md`
- `design/epic-contribution-ladder-2026.md`

This revision deliberately does **not** rewrite the broad ladder and does **not** replace the rev0394 inner-loop bet, the rev0395 package-intake seam, the rev0396 compatibility-claims move, the rev0397 proc-macro-transition move, or the rev0398 artifact-contract promotion.
Instead, it promotes an already-present frontier candidate because the current official signals are unusually aligned: Rust's 2026 flagships now explicitly include **integrating Cargo into larger build systems**; the accepted Cargo plumbing goal already decomposes the build into discover/read/lock/resolve/plan/execute/stage phases; Cargo's stable external-tools story is still mainly `cargo metadata`, JSON messages, and subcommands; the old unstable `build-plan` was removed in favor of plumbing commands, `--unit-graph`, and structured logging; rust-analyzer documents provisional discovery/event contracts plus `{label}`-aware overrides; and Fuchsia remains a live proof that generated Rust workspace graphs are valuable but too format-fragile to keep reinventing forever.

- New design note: `design/cargo-build-interop-contract-2026Q1.md`
- Design/proposal/gap refresh: `design/build-interop-kit.md`, `gaps/build-system-interop-and-cargo-plumbing.md`, `proposals/epic-build-interop-kit.md`, `design/epic-contribution-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact, keep **Rust inner-loop contract** as the clearest build/debug bundle-shaping move, keep **Cargo artifact contract** as the explicit final-output / handoff seam, and promote **Build Interop Kit / Cargo Build Interop Contract** as the clearest next **workspace-graph / plan / event / adapter-shaping** move beneath Cargo plumbing, rust-analyzer discovery, and larger-build-system integration pressure
- Hygiene: future build-system/plumbing revisions should keep **workspace discovery**, **workspace/unit graph**, **build intent**, **execution events**, **adapter projections**, and **final artifacts** visibly separate; do not let one `cargo metadata` view, one provisional `rust-project.json`, one BSP adapter, or one target-dir walk silently become the whole story

## Latest addition (rev0398)
The archive now has an explicit **Cargo artifact contract** note that promotes the existing **Artifact Surface Kit** into the clearest next **build-system / plumbing-shaping** frontier.

Read first if you want the repo's current answer to “what worthy Rust contribution should connect Cargo plumbing phases, final-output identity, origin/staging semantics, artifact-sidecars, and downstream release/inventory/repro/support handoffs without becoming another build-system empire?”
- `design/cargo-artifact-contract-2026Q1.md`
- `design/artifact-surface-kit.md`
- `gaps/final-artifact-surface-identity-selection-outputs-and-handoffs.md`
- `proposals/epic-artifact-surface-kit.md`
- `design/build-interop-kit.md`
- `design/epic-contribution-ladder-2026.md`

This revision deliberately does **not** rewrite the broad ladder and does **not** replace the rev0394 inner-loop bet, the rev0395 package-intake seam, the rev0396 compatibility-claims move, or the rev0397 proc-macro-transition move.
Instead, it promotes an already-present frontier candidate because the current official signals are unusually aligned: Rust's 2026 flagships now include cargo plumbing commands under the Building blocks roadmap; the accepted plumbing goal explicitly breaks Cargo into phases ending with **stage final artifacts**; the GSoC 2025 prototype implemented seven plumbing subcommands through `plan-build` but not that final-artifact boundary; Cargo's external-tools docs still leave downstream tools stitching together metadata, JSON messages, and custom commands; Cargo 1.93's custom-final-artifacts discussion makes artifact staging/collision/uplift semantics explicit; and the March 2026 build-dir-layout-v2 testing call shows many tools still rely on unspecified layout details because the missing Cargo-facing boundary has not fully arrived yet.

- New design note: `design/cargo-artifact-contract-2026Q1.md`
- Design/proposal/gap refresh: `design/artifact-surface-kit.md`, `gaps/final-artifact-surface-identity-selection-outputs-and-handoffs.md`, `proposals/epic-artifact-surface-kit.md`, `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact, keep **Rust inner-loop contract** as the clearest build/debug bundle-shaping move, keep **Package Intake Gateway** as the clearest supply-chain/intake seam, keep **Compatibility Claims** as the clearest support/claim-shaping move, keep **Proc-Macro Exit Stack** as the clearest compile-time/transition move, and promote **Artifact Surface Kit / Cargo Artifact Contract** as the clearest next **build-system/plumbing-shaping** move beneath Cargo's current output and handoff surfaces
- Hygiene: future artifact/plumbing revisions should keep **build subject truth**, **phase/evidence-path truth**, **final artifact identity truth**, **origin/staging/copy truth**, **sidecar truth**, and **downstream handoff truth** visibly separate; do not let one JSON stream, one `--artifact-dir` copy, one package listing, one SBOM precursor, or one release manifest silently become the whole story

## Latest addition (rev0397)
The archive now has an explicit **proc-macro exit stack** note that promotes the existing macro-workflow and reflection-transition material into the clearest next **compile-time/transition-shaping** frontier.

Read first if you want the repo’s current answer to “what worthy Rust contribution should reduce unnecessary proc-macro burden, preserve honest inventory/cost/debug/review truth, and make declarative-macro or reflection transitions reviewable without becoming another macro empire?”
- `design/proc-macro-exit-stack-2026Q1.md`
- `design/macro-workflow-kit.md`
- `gaps/macro-workflows-and-proc-macro-migration.md`
- `gaps/reflection-transition-lane-comparison-macro-burden-and-core-reflection-migration.md`
- `proposals/epic-proc-macro-exit-stack.md`
- `design/epic-contribution-ladder-2026.md`

This revision deliberately does **not** rewrite the broad ladder and does **not** replace the rev0394 inner-loop bet, the rev0395 package-intake seam, or the rev0396 compatibility-claims move.
Instead, it promotes an already-present frontier candidate because the current official signals are unusually aligned: macro-improvements work explicitly aims to replace many proc-macro use cases with declarative macros for faster builds and smaller dependency supply chains; reflection/comptime explicitly says proc-macro derives have historically been hard to debug and bootstrap; the 2026 flagships now include prototype reflection; the compiler-performance survey says some language features could remove proc macros and that derive-proc-macro expansion is still not an ideal incremental-build story; and the Rust Reference still treats proc macros as compile-time code with build-script-like security concerns.

- New design note: `design/proc-macro-exit-stack-2026Q1.md`
- New proposal: `proposals/epic-proc-macro-exit-stack.md`
- Design refresh: `design/epic-contribution-ladder-2026.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact, keep **Rust inner-loop contract** as the clearest next build/debug bundle-shaping move, keep **Package Intake Gateway** as the clearest newly sharpened supply-chain seam, keep **Compatibility Claims** as the clearest next support/claim-shaping move, and promote **Proc-Macro Exit Stack** as the clearest next **compile-time/transition-shaping** move beneath **Macro Workflow + Compile-Time Capabilities + Reflection Transition**
- Hygiene: future macro/reflection revisions should keep **macro inventory/cost/debug truth**, **compile-time execution authority**, **transition-target truth**, **migration-confidence truth**, and **consumer-handoff truth** visibly separate; do not let one `cargo expand` rendering, one `cargo tree` marker, one reflection prototype, or one derive anecdote silently become the whole story

## Latest addition (rev0396)
The archive now has an explicit **compatibility claims contract** note that promotes the existing compatibility-claims material into the clearest next **support/claim-shaping** frontier.

Read first if you want the repo’s current answer to “what worthy Rust contribution should connect platform/runtime support, docs-target posture, debugger tuple reality, and advanced compiler-lane acceptance into one reviewable contract without becoming another hosted compatibility empire?”
- `design/compatibility-claims-2026Q1.md`
- `design/compatibility-claims-stack.md`
- `design/compatibility-claims-pilot-program.md`
- `proposals/epic-compatibility-claims-stack.md`
- `gaps/compatibility-claims-platform-debugger-and-acceptance-contracts.md`
- `design/epic-contribution-ladder-2026.md`

This revision deliberately does **not** rewrite the broad ladder and does **not** replace the rev0394 inner-loop bet or the rev0395 package-intake seam.
Instead, it promotes an already-present frontier candidate because the current official signals are unusually aligned: target-tier and platform-support docs now carry more real support structure; `x86_64-apple-darwin` and `aarch64-pc-windows-msvc` show public support drift in both directions; docs.rs changed its default targets; the debugging survey makes debugger tuples a public compatibility concern; the next-solver work keeps compiler-lane acceptance moving; and the safety-critical writeup explicitly asks for target-readiness and long-lived support discipline.

- New design note: `design/compatibility-claims-2026Q1.md`
- Design refresh: `design/epic-contribution-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: keep the broad ranking intact, keep **Rust inner-loop contract** as the clearest next build/debug bundle-shaping move, keep **Package Intake Gateway** as the clearest newly sharpened supply-chain seam, and promote **Compatibility Claims** as the clearest next **support/claim-shaping** move beneath **Support Envelope + Debuggability + Acceptance Surface**
- Hygiene: future compatibility/support revisions should keep **support-envelope truth**, **debugger-tuple truth**, **acceptance-surface truth**, **declared-vs-observed evidence**, and **consumer-summary truth** visibly separate; do not let one target table, one docs.rs default, one debugger anecdote, or one green CI run silently become the whole compatibility story

## Latest addition (rev0395)
The archive now has an explicit **package intake gateway** note for the under-modeled seam between **package publication / route truth** and **local extraction / staging / build / install truth**.

Read first if you want the repo’s current answer to “what worthy Rust contribution should connect registry route identity, `.crate` payload truth, local extraction/staging semantics, lock/resolution posture, and bounded handoffs into dependency review / build / install / incident response?”
- `design/package-intake-gateway-2026Q1.md`
- `proposals/epic-package-intake-gateway.md`
- `gaps/package-intake-extraction-route-quarantine-and-handoff-truth.md`
- `design/package-admission-stack.md`
- `design/dependency-review-stack.md`
- `design/consumer-install-kit.md`
- `design/epic-contribution-ladder-2026.md`

This revision deliberately does **not** rewrite the broad ladder again.
Instead, it deepens an under-modeled Tier A supply-chain seam that recent official signals made harder to ignore: Cargo’s March 21, 2026 extraction vulnerability shows package ingress itself is part of the attack and review surface; Cargo’s route semantics for alternate registries, mirrors, and source replacement are explicit but fragmented; `cargo package` and `cargo install` already have materially different local staging / lock / config behavior; and crates.io’s newer trust/freshness signals still do not tell later consumers what happened when a package crossed into local machine state.

- New design note: `design/package-intake-gateway-2026Q1.md`
- New proposal: `proposals/epic-package-intake-gateway.md`
- New gap note: `gaps/package-intake-extraction-route-quarantine-and-handoff-truth.md`
- Ladder refresh: `design/epic-contribution-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/AMNESIA_RESISTORS.md`, `meta/REVISION_OPERATING_PROTOCOL.md`
- Strategy: keep the broad ranking and the rev0394 inner-loop bet intact, but promote **Package Intake Gateway** as the clearest new **supply-chain/intake-shaping** seam beneath **Package Admission + Dependency Review + Consumer Install**
- Hygiene: future supply-chain revisions should keep **publication admission**, **package intake**, **dependency review**, **compile-time execution authority**, and **consumer install** visibly separate; do not let one advisory, one registry feature, or one install workflow silently flatten all five layers

## Latest addition (rev0394)
The archive now has an explicit **Rust inner-loop contract** synthesis note that promotes the existing **Feedback Loop Stack** from “promising composition seam” to the clearest next **bundle-shaping** move under the build/debug band.

Read first if you want the repo’s current answer to “what worthy contribution should connect Cargo build facts, rust-analyzer/editor tradeoffs, debugger/runtime-side inspection truth, and honest downstream handoffs without becoming another local platform empire?”
- `design/rust-inner-loop-contract-2026Q1.md`
- `design/feedback-loop-stack.md`
- `design/feedback-loop-pilot-program.md`
- `proposals/epic-feedback-loop-stack.md`
- `gaps/developer-feedback-loops-build-debug-iteration-and-honest-session-handoffs.md`
- `design/epic-contribution-ladder-2026.md`

This revision deliberately does **not** widen the maintained default-card corpus again.
Instead, it promotes an already-present frontier candidate because the current official signals are unusually aligned: Cargo is surfacing session/rebuild/timing evidence, build-dir/layout work is making Cargo ↔ editor coexistence explicit, the performance survey sharpens debug-info and IDE/Cargo tradeoffs, and the debugging survey makes debugger-tuple/async/evaluation gaps explicit.

- New design note: `design/rust-inner-loop-contract-2026Q1.md`
- Design refresh: `proposals/epic-feedback-loop-stack.md`, `gaps/developer-feedback-loops-build-debug-iteration-and-honest-session-handoffs.md`, `design/epic-contribution-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: after the ladder refresh in rev0393, the strongest next move was to **promote an existing near-frontier synthesis candidate** rather than mint another adjacent seam or default lane
- Hygiene: when the archive promotes a composition seam, say explicitly whether it outranks neighboring stacks **overall** or only becomes the next **bundle-shaping** move; do not let “this is the next thing to shape” silently become “this is now the most important thing Rust is missing”

## Latest addition (rev0393)
The archive now has an explicit **epic territory map** plus a concrete next-lane note for the long-telegraphed **browser + Node dual-target Wasm package overlay**.

Read first if you want the repo’s current answer to “what is most missing in Rust right now, what would count as a worthy epic contribution, and which next public lane deserves promotion if we widen the defaults corpus again?”
- `design/rust-ecosystem-epic-map-2026Q1.md`
- `design/browser-node-dual-target-wasm-package-overlay.md`
- `proposals/epic-browser-node-dual-target-wasm-package-overlay.md`
- `design/ecosystem-priority-ladder-2026.md`
- `design/epic-contribution-ladder-2026.md`

This revision deliberately does **not** add another maintained default card.
Instead, it corrects a different kind of archive weakness: the repo had enough material that “what matters most”, “what is most buildable”, and “what next lane should be promoted” were at risk of collapsing into one vague frontier mood.
The new map now keeps those questions separate, keeps **Build-State Evidence**, **Adoption Navigation + reviewable defaults**, and **Debuggability** in the top band, and names **browser + Node dual-target Wasm package overlay** as the clearest next public-lane candidate ahead of **raw custom Wasmtime embedder** or **durable internal library**.

- New design note: `design/rust-ecosystem-epic-map-2026Q1.md`
- New design note: `design/browser-node-dual-target-wasm-package-overlay.md`
- New proposal: `proposals/epic-browser-node-dual-target-wasm-package-overlay.md`
- New gap note: `gaps/browser-node-dual-target-wasm-packages-target-contract-and-maintenance-truth.md`
- Ladder refresh: `design/ecosystem-priority-ladder-2026.md`, `design/epic-contribution-ladder-2026.md`
- Frontier/meta refresh: `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, `meta/AMNESIA_RESISTORS.md`
- Strategy: after filling the native-shell mobile hole, the strongest next move was a **ladder refresh plus one concrete next-lane note** rather than widening the maintained defaults corpus on autopilot
- Hygiene: future ladder refreshes should keep **broad ecosystem need**, **near-term buildability**, **next public-lane candidacy**, and **repo-hygiene/meta work** visibly separate; do not let one fashionable crate, one runtime, or one blog post rewrite all four at once

## Latest addition (rev0392)
The archive now has a first **native-shell mobile product** default card plus its first receipt.

Read first if you want the repo’s current answer to “what should we actually start with for a serious Android+iOS product when Swift/Kotlin should own the app shell and Rust should be the shared engine?”
- `design/native-shell-mobile-product-default-lane.md`
- `defaults/conservative-native-shell-mobile-product-2026Q1.md`
- `evidence/conservative-native-shell-mobile-product-2026Q1-renewal-2026-03-22.md`
- `design/mobile-app-product-default-lane.md`
- `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`

This completes the next missing client/mobile split the archive had already been naming: the repo no longer treats **cross-platform mobile shell** and **native-shell mobile productization** as one blurry “Rust mobile” story. It now publishes a bounded native-shell answer instead of smearing UniFFI, Xcode build phases, Gradle integration, cargo-ndk, and Flutter-first product guidance across generic mobile folklore.

- New design note: `design/native-shell-mobile-product-default-lane.md`
- New proposal: `proposals/epic-native-shell-mobile-product-default-lane.md`
- New gap note: `gaps/native-shell-mobile-products-os-framework-ownership-and-rust-core-boundaries.md`
- New default card: `defaults/conservative-native-shell-mobile-product-2026Q1.md`
- New renewal receipt: `evidence/conservative-native-shell-mobile-product-2026Q1-renewal-2026-03-22.md`
- Design refresh: `design/reviewable-lane-defaults-corpus.md`, `evidence/README.md`, `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`
- Frontier/priority refresh: corrected the corpus so it now covers a **native-shell mobile product lane** distinct from the existing **cross-platform mobile shell** lane
- Strategy: after the self-hosted Wasm-host correction, the strongest next correction was the missing **native-shell mobile** answer rather than another runtime or package split
- Hygiene: for native-shell mobile guidance, keep **native app-shell truth**, **Rust-core truth**, **binding-generation truth**, **Android-build truth**, **iOS-build truth**, **resource/lifetime truth**, and **support/docs truth** visibly separate; do not let one bridge tool, one Xcode script, or one Gradle snippet silently become the whole lane


## Latest addition (rev0391)
The archive now has a first **portable self-hosted Wasm edge host** default card plus its first receipt.

Read first if you want the repo’s current answer to “what should we actually start with for a serious self-hosted Rust/Wasm web product when provider independence matters more than one managed edge runtime?”
- `design/portable-self-hosted-wasm-edge-host-default-lane.md`
- `defaults/conservative-portable-self-hosted-wasm-edge-host-2026Q1.md`
- `evidence/conservative-portable-self-hosted-wasm-edge-host-2026Q1-renewal-2026-03-22.md`
- `design/worker-first-edge-web-product-default-lane.md`
- `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`

This completes the next missing public-web/runtime split the archive had already been naming: the repo no longer treats **managed worker edge runtime** and **portable self-hosted Wasm hosting** as one blurry “Rust on the edge” story. It now publishes a bounded self-hosted answer instead of smearing Spin, SpinKube, raw Wasmtime, and wasmCloud across generic web/serverless/component folklore.

- New design note: `design/portable-self-hosted-wasm-edge-host-default-lane.md`
- New proposal: `proposals/epic-portable-self-hosted-wasm-edge-host-default-lane.md`
- New gap note: `gaps/portable-self-hosted-wasm-edge-hosts-app-packaging-runtime-and-cluster-truth.md`
- New default card: `defaults/conservative-portable-self-hosted-wasm-edge-host-2026Q1.md`
- New renewal receipt: `evidence/conservative-portable-self-hosted-wasm-edge-host-2026Q1-renewal-2026-03-22.md`
- Design refresh: `design/reviewable-lane-defaults-corpus.md`, `evidence/README.md`, `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`
- Frontier/priority refresh: corrected the corpus so it now covers a **portable self-hosted Wasm edge-host lane** distinct from the existing **worker-first managed edge-runtime** lane
- Strategy: after the public SDK-family correction, the strongest next correction was the long-promised **portable/self-hosted Wasm-host** answer rather than another library/client/package note
- Hygiene: for self-hosted Wasm-host guidance, keep **application/manifest truth**, **component/runtime truth**, **OCI/distribution truth**, **local-dev/testing truth**, **cluster/operator/runtime-class truth**, **portability/runtime-boundary truth**, and **support/docs truth** visibly separate; do not let one host demo, one runtime, or one Kubernetes walkthrough silently become the whole lane

## Latest addition (rev0390)
The archive now has a first **public SDK family** default card plus its first receipt.

Read first if you want the repo’s current answer to “what should we actually start with for a serious public Rust SDK family when the real source of truth is an OpenAPI-described API and the support story has to survive regeneration?”
- `design/public-sdk-family-default-lane.md`
- `defaults/conservative-public-sdk-family-2026Q1.md`
- `evidence/conservative-public-sdk-family-2026Q1-renewal-2026-03-22.md`
- `design/sdk-productization-stack.md`
- `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`

This instantiates a long-standing archive seam: the repo no longer has only an abstract **SDK Productization Stack**. It now publishes a bounded maintained answer for the central **public generated-client / SDK-family** lane instead of leaving SDK guidance smeared across generic publishable-library advice, OpenAPI-generator folklore, and large-scale Smithy/AWS examples.

- New design note: `design/public-sdk-family-default-lane.md`
- New proposal: `proposals/epic-public-sdk-family-default-lane.md`
- New gap note: `gaps/public-sdk-families-contract-runtime-and-release-truth.md`
- New default card: `defaults/conservative-public-sdk-family-2026Q1.md`
- New renewal receipt: `evidence/conservative-public-sdk-family-2026Q1-renewal-2026-03-22.md`
- Design refresh: `design/reviewable-lane-defaults-corpus.md`, `evidence/README.md`, `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`
- Frontier/priority refresh: corrected the corpus so it now covers a **public SDK family lane** distinct from both the general **publishable-library** lane and the **polyglot workspace component** lane
- Strategy: after the runtime/product splits, the strongest next correction was not another host lane but to instantiate the older **SDK Productization** frontier as a maintained default card
- Hygiene: for public SDK-family guidance, keep **source-contract truth**, **generated-code truth**, **hand-written overlay truth**, **runtime/auth/config truth**, **docs/example/mock/CLI family truth**, **release/versioning/package truth**, and **support/docs truth** visibly separate; do not let one generator homepage or one sample repo silently become the whole lane

## Latest addition (rev0389)
The archive now has a first **worker-first edge web product** default card plus its first receipt.

Read first if you want the repo’s current answer to “what should we actually start with for a serious Rust worker/edge product whose real substrate is a managed edge runtime rather than a self-managed origin server?”
- `design/worker-first-edge-web-product-default-lane.md`
- `defaults/conservative-worker-first-edge-web-product-2026Q1.md`
- `evidence/conservative-worker-first-edge-web-product-2026Q1-renewal-2026-03-22.md`
- `design/web-productization-stack.md`
- `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`

This corrects the remaining hole in the archive’s public-web map: the repo now publishes a bounded **worker-first edge-runtime** answer instead of leaving edge-hosted Rust smeared across full-stack web hosting, browser-package notes, and generic serverless/provider folklore.

- New design note: `design/worker-first-edge-web-product-default-lane.md`
- New proposal: `proposals/epic-worker-first-edge-web-product-default-lane.md`
- New gap note: `gaps/worker-first-edge-products-provider-state-and-route-truth.md`
- New default card: `defaults/conservative-worker-first-edge-web-product-2026Q1.md`
- New renewal receipt: `evidence/conservative-worker-first-edge-web-product-2026Q1-renewal-2026-03-22.md`
- Design refresh: `design/reviewable-lane-defaults-corpus.md`, `evidence/README.md`, `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`
- Frontier/priority refresh: corrected the corpus so it now covers a **worker-first managed edge-runtime lane** distinct from the existing **browser-first public web-app**, **full-stack Rust web-product**, and **browser-consumed Wasm-package** lanes
- Strategy: after completing the public-web split and the mobile-product correction, the strongest next correction was the missing **edge-runtime worker-product** answer rather than a generic SDK or generated-client note
- Hygiene: for edge-worker guidance, keep **provider/runtime envelope truth**, **binding/storage/service truth**, **route/assets/deploy truth**, **local-dev/testing truth**, **portability/provider-lock truth**, and **support/docs truth** visibly separate; do not let one provider homepage or one demo silently become the whole lane


## Latest addition (rev0388)
The archive now has a first **mobile app product** default card plus its first receipt.

Read first if you want the repo’s current answer to “what should we actually start with for a serious mobile-first product that wants real Rust in the core without forcing a universal all-Rust UI bet?”
- `design/mobile-app-product-default-lane.md`
- `defaults/conservative-mobile-app-product-2026Q1.md`
- `evidence/conservative-mobile-app-product-2026Q1-renewal-2026-03-22.md`
- `design/client-productization-stack.md`
- `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`

This is the concrete split that the client-productization frontier had been signaling for a while: the repo now publishes a bounded **mobile-first app-product** answer instead of leaving mobile guidance smeared across desktop guidance, Tauri/Dioxus/Slint examples, and generic polyglot-component notes.

- New design note: `design/mobile-app-product-default-lane.md`
- New proposal: `proposals/epic-mobile-app-product-default-lane.md`
- New gap note: `gaps/mobile-app-products-shell-core-store-and-permission-truth.md`
- New default card: `defaults/conservative-mobile-app-product-2026Q1.md`
- New renewal receipt: `evidence/conservative-mobile-app-product-2026Q1-renewal-2026-03-22.md`
- Design refresh: `design/reviewable-lane-defaults-corpus.md`, `evidence/README.md`, `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`
- Frontier/priority refresh: corrected the corpus so it now covers a **mobile-first public app-product lane** distinct from both the **desktop-first app-product lane** and the **polyglot workspace component** lane
- Strategy: after completing the public-web split, the strongest next correction was the missing **mobile-first app-product** answer rather than another web note or a premature edge/runtime card
- Hygiene: for mobile-product guidance, keep **mobile shell/runtime truth**, **Rust-core/bridge truth**, **native escape truth**, **permission/device-capability truth**, **store/package/signing truth**, and **support/docs truth** visibly separate; do not let one framework homepage or one cross-platform demo silently become the whole lane

## Latest addition (rev0387)
The archive now has a first **browser Wasm package** default card plus its first receipt.

Read first if you want the repo’s current answer to “what should we actually start with for a serious browser-consumed Rust package published through an npm-shaped interface?”
- `design/browser-wasm-package-default-lane.md`
- `defaults/conservative-browser-wasm-package-2026Q1.md`
- `evidence/conservative-browser-wasm-package-2026Q1-renewal-2026-03-22.md`
- `design/browser-web-app-default-lane.md`
- `design/full-stack-rust-web-product-default-lane.md`
- `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`

This completes the maintained three-way public-web split the repo had been circling around: the archive now distinguishes **browser-first app deployment**, **Rust-owned full-stack web product**, and **browser-consumed Wasm package publication** instead of leaving all three inside one vague “Rust web” bucket.

- New design note: `design/browser-wasm-package-default-lane.md`
- New proposal: `proposals/epic-browser-wasm-package-default-lane.md`
- New gap note: `gaps/browser-wasm-package-defaults-js-glue-types-and-publication-truth.md`
- New default card: `defaults/conservative-browser-wasm-package-2026Q1.md`
- New renewal receipt: `evidence/conservative-browser-wasm-package-2026Q1-renewal-2026-03-22.md`
- Design refresh: `design/reviewable-lane-defaults-corpus.md`, `evidence/README.md`, `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`
- Frontier/priority refresh: corrected the corpus so it now covers a **browser-consumed public Wasm-package lane** distinct from both the **browser-first public web-app lane** and the **full-stack Rust web-product lane**
- Strategy: after adding the two app-oriented web cards, the strongest next split was the missing **package-publication lane** rather than another abstract web note or a premature edge-runtime card
- Hygiene: for browser-package guidance, keep **crate identity**, **npm package identity**, **generated JS glue**, **TypeScript declarations**, **bundler-vs-web target truth**, **browser-test truth**, and **tool-maintenance truth** visibly separate; do not let one tool homepage silently become the whole lane

## Latest addition (rev0386)
The archive now has a first **full-stack Rust web product** default card plus its first receipt.

Read first if you want the repo’s current answer to “what should we actually start with for a serious Rust web product when Rust should own both the browser and server halves?”
- `design/full-stack-rust-web-product-default-lane.md`
- `defaults/conservative-full-stack-rust-web-product-2026Q1.md`
- `evidence/conservative-full-stack-rust-web-product-2026Q1-renewal-2026-03-22.md`
- `design/browser-web-app-default-lane.md`
- `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`

This is the concrete split that the browser-web card was designed to make possible: the repo now publishes a bounded **full-stack SSR/hydration** answer instead of leaving “Rust web” to blur together browser-only apps, full-stack products, and future npm-published Wasm/package lanes.

- New design note: `design/full-stack-rust-web-product-default-lane.md`
- New proposal: `proposals/epic-full-stack-rust-web-product-default-lane.md`
- New gap note: `gaps/full-stack-rust-web-products-ssr-serverfunctions-and-dual-target-truth.md`
- New default card: `defaults/conservative-full-stack-rust-web-product-2026Q1.md`
- New renewal receipt: `evidence/conservative-full-stack-rust-web-product-2026Q1-renewal-2026-03-22.md`
- Design refresh: `design/reviewable-lane-defaults-corpus.md`, `evidence/README.md`, `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`
- Frontier/priority refresh: corrected the corpus so it now covers a **full-stack public web-product lane** distinct from both the **browser-first public web-app lane** and any future **browser package / npm-published Wasm** lane
- Strategy: after adding the browser-only web card, the strongest next split was the missing **Rust-owned full-stack web product** card rather than another abstract web note or a premature npm-package lane
- Hygiene: for full-stack web guidance, keep **dual-target build truth**, **SSR/hydration truth**, **server-function/API truth**, **auth/session/deploy truth**, and **support/docs truth** visibly separate; do not let one framework homepage or one dev CLI silently become the whole lane


## Latest addition (rev0385)
The archive now has a first **browser web app** default card plus its first receipt.

Read first if you want the repo’s current answer to “what should we actually start with for a serious browser-first Rust web app?”
- `design/browser-web-app-default-lane.md`
- `defaults/conservative-browser-web-app-2026Q1.md`
- `evidence/conservative-browser-web-app-2026Q1-renewal-2026-03-22.md`
- `design/web-productization-stack.md`
- `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`

This is the concrete bridge between the older web-productization stack and the newer defaults/receipts discipline: the repo now publishes a bounded browser-first answer instead of leaving Rust web guidance as a framework or render-mode shootout.

- New design note: `design/browser-web-app-default-lane.md`
- New proposal: `proposals/epic-browser-web-app-default-lane.md`
- New gap note: `gaps/browser-web-app-defaults-render-mode-bundle-and-browser-boundaries.md`
- New default card: `defaults/conservative-browser-web-app-2026Q1.md`
- New renewal receipt: `evidence/conservative-browser-web-app-2026Q1-renewal-2026-03-22.md`
- Design refresh: `design/reviewable-lane-defaults-corpus.md`, `evidence/README.md`, `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`
- Frontier/priority refresh: corrected the corpus so it now covers a **browser-first public web-app lane** distinct from both the broader abstract **web productization stack** and any future **full-stack Rust web product** card
- Strategy: after completing first-receipt coverage for the maintained cards, widen again only with a lane this central or better
- Hygiene: for browser-web guidance, keep **render-mode truth**, **bundle/base-path/deploy truth**, **browser capability / JS-interop truth**, **service/API boundary truth**, and **support/docs truth** visibly separate; do not let one framework homepage or one bundler setup silently become the whole lane

## Latest addition (rev0384)
The archive now has the missing first **polyglot workspace / monorepo component** renewal receipt, plus a sharpened card that keeps **workspace truth, config truth, Rust-core truth, host-package truth, and boundary-framework truth** visibly separate.

Read first if you want the repo’s current answer to “how should we add one Rust component to a bigger non-Rust or mixed-language system without prematurely betting on CXX, PyO3, UniFFI, or napi-rs?”
- `defaults/polyglot-workspace-component-2026Q1.md`
- `evidence/polyglot-workspace-component-2026Q1-renewal-2026-03-22.md`
- `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`
- `meta/LANE_RENEWAL_RECEIPTS_WORKING_SET.md`
- `meta/ACTIVE_FRONTIER.md`

This closes the last first-receipt gap in the maintained defaults corpus.
The current corpus can now show a readable receipt for every maintained card instead of leaving the polyglot lane as the lone prose-only holdout.

- New renewal receipt: `evidence/polyglot-workspace-component-2026Q1-renewal-2026-03-22.md`
- Card refresh: `defaults/polyglot-workspace-component-2026Q1.md`
- Corpus/frontier refresh: `design/reviewable-lane-defaults-corpus.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`, `meta/LANE_RENEWAL_RECEIPTS_WORKING_SET.md`
- Strategy: after receipt-complete coverage for the current maintained cards, prefer **renewing the oldest central card whose lane-level answer has actually moved** before widening the corpus again
- Hygiene: for polyglot-component guidance, keep **workspace membership**, **config overlays**, **Rust core**, **boundary adapter**, **host-package/distribution contract**, **exact package identity**, and **final lane judgment** visibly separate; do not let one binding demo or one package-manager workflow silently become the whole lane

## Latest addition (rev0383)
The archive now has a first **desktop-app product** default card plus its first receipt.

Read first if you want the repo’s current answer to “what should we actually start with for a real Rust desktop app?”
- `design/desktop-app-default-lane.md`
- `defaults/conservative-desktop-app-product-2026Q1.md`
- `evidence/conservative-desktop-app-product-2026Q1-renewal-2026-03-22.md`
- `design/client-productization-stack.md`
- `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`

This is a concrete bridge between the older client-productization stack and the newer defaults/receipts discipline: the repo now publishes a bounded desktop-first answer instead of leaving GUI guidance as a framework shootout.

- New design note: `design/desktop-app-default-lane.md`
- New proposal: `proposals/epic-desktop-app-default-lane.md`
- New gap note: `gaps/desktop-app-defaults-webview-native-shells-a11y-and-distribution.md`
- New default card: `defaults/conservative-desktop-app-product-2026Q1.md`
- New renewal receipt: `evidence/conservative-desktop-app-product-2026Q1-renewal-2026-03-22.md`
- Design refresh: `design/reviewable-lane-defaults-corpus.md`, `evidence/README.md`, `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`
- Frontier/priority refresh: corrected the corpus so it now covers a **desktop-first public GUI product lane** distinct from both **installable CLI products** and the broader abstract **client-productization stack**
- Strategy: after adding this card, prefer finishing **polyglot receipt coverage** and renewing central cards before widening the corpus again
- Hygiene: for desktop-product guidance, keep **app shell/runtime truth**, **frontend/runtime contract**, **capability/permission truth**, **accessibility posture**, and **packaging/distribution posture** visibly separate; do not let one toolkit homepage or one showcase app silently become the whole lane

## Latest addition (rev0382)
The archive now has a first **installable CLI product** default card and receipt, which fills the public-binary gap between the internal CLI lane and the library/publication lane.

Read first if you want the repo’s current answer to “what should a boring Rust CLI product normalize around once real release/distribution/support routes matter?”
- `design/installable-cli-product-default-lane.md`
- `defaults/conservative-installable-cli-product-2026Q1.md`
- `evidence/conservative-installable-cli-product-2026Q1-renewal-2026-03-22.md`
- `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`
- `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`

This is the concrete next step after the publishable-library correction: the repo now covers not only **internal tooling, services, scripts, components, and publishable crates**, but also the central **installable CLI product** lane where release/build truth, install-route truth, source-fallback truth, supply-chain truth, and ownership/update truth have to stay visible together.

- New design note: `design/installable-cli-product-default-lane.md`
- New proposal: `proposals/epic-installable-cli-product-default-lane.md`
- New gap note: `gaps/installable-cli-products-release-routes-ownership-and-update-posture.md`
- New default card: `defaults/conservative-installable-cli-product-2026Q1.md`
- New renewal receipt: `evidence/conservative-installable-cli-product-2026Q1-renewal-2026-03-22.md`
- Design refresh: `design/reviewable-lane-defaults-corpus.md`
- Frontier/priority refresh: corrected the corpus so it now distinguishes **internal CLI** from **installable CLI product** instead of letting release/distribution concerns hide inside one broad command-line story
- Strategy: after adding this public-binary card, prefer **receipt completion and renewal of existing central cards** before widening the corpus again
- Hygiene: for installable-binary guidance, keep **release/build truth**, **supported install routes**, **source-fallback truth**, **optional Cargo-native prebuilt route truth**, **supply-chain evidence**, and **ownership/update posture** visibly separate; do not let one release tool silently become the whole lane

## Latest addition (rev0381)
The archive now has a first **publishable library** default card and receipt, which fills the corpus’s missing center between app-facing lanes and more specialized component lanes.

Read first if you want the repo’s current answer to “what should a boring reusable Rust library normalize around before release?”
- `design/publishable-library-default-lane.md`
- `defaults/conservative-publishable-library-2026Q1.md`
- `evidence/conservative-publishable-library-2026Q1-renewal-2026-03-22.md`
- `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`
- `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`

This is the concrete next step after the receipt corpus: the repo now covers not only **apps and scripts**, but also the central **publishable library** lane where manifest truth, docs.rs truth, semver truth, public API boundary, and exact package identity have to stay visible together.

- New design note: `design/publishable-library-default-lane.md`
- New proposal: `proposals/epic-publishable-library-default-lane.md`
- New gap note: `gaps/publishable-library-defaults-docsrs-semver-and-public-api-discipline.md`
- New default card: `defaults/conservative-publishable-library-2026Q1.md`
- New renewal receipt: `evidence/conservative-publishable-library-2026Q1-renewal-2026-03-22.md`
- Meta-engineering: added `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`
- Design refresh: `design/reviewable-lane-defaults-corpus.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/priority refresh: promoted the corpus correction that the archive now needs a **central library-authoring card** before it deserves more edge-lane expansion
- Strategy: prefer completing receipt coverage for the current high-centrality cards, especially `polyglot-workspace-component`, before adding novelty lanes
- Hygiene: keep **manifest contract**, **docs.rs behavior**, **semver gate**, **public dependency exposure**, and **exact package identity** visibly separate when a card concerns publishable crates

## Latest addition (rev0380)
The archive now has a first **lane-default renewal receipts corpus** under `evidence/` plus `design/lane-default-renewal-receipts.md`.

Read first if you want the repo’s current answer to “show me the receipts behind this default”:
- `design/lane-default-renewal-receipts.md`
- `evidence/README.md`
- `evidence/conservative-internal-cli-2026Q1-renewal-2026-03-22.md`
- `evidence/conservative-http-service-2026Q1-renewal-2026-03-22.md`
- `evidence/script-repro-tiny-utility-2026Q1-renewal-2026-03-22.md`
- `meta/LANE_RENEWAL_RECEIPTS_WORKING_SET.md`

This is the concrete next step beneath the existing evidence bundle: the repo now publishes **real renewal receipts** for current cards instead of only describing what a receipt should look like.

- New design note: `design/lane-default-renewal-receipts.md`
- New proposal: `proposals/epic-lane-default-renewal-receipts.md`
- New gap note: `gaps/concrete-renewal-receipts-and-exact-identity-hygiene.md`
- New evidence corpus: `evidence/README.md`, `evidence/conservative-internal-cli-2026Q1-renewal-2026-03-22.md`, `evidence/conservative-http-service-2026Q1-renewal-2026-03-22.md`, `evidence/script-repro-tiny-utility-2026Q1-renewal-2026-03-22.md`
- Meta-engineering: added `meta/LANE_RENEWAL_RECEIPTS_WORKING_SET.md`
- Design refresh: `design/lane-default-evidence-bundle.md`, `design/lane-default-evidence-pilot-program.md`, `design/reviewable-lane-defaults-corpus.md`, `design/ecosystem-priority-ladder-2026.md`
- Default-card refresh: linked the current cards to their latest receipts
- Frontier/priority refresh: promoted explicit **Lane Default Renewal Receipts** as the next practical seam beneath **Lane Default Evidence Bundle**, so the archive now treats **exact package identity + renewal verdict + replay notes** as part of the carried answer rather than cleanup
- Strategy: prefer renewing and narrowing current cards with visible receipts before widening the corpus
- Hygiene: current RustSec lookalike-crate removals make exact-identity discipline part of the archive’s LLM hygiene, not an optional stylistic nicety

## Latest addition (rev0379)
The archive now has a **Lane Default Evidence Bundle** under `design/lane-default-evidence-bundle.md` plus a compact `meta/DEFAULT_EVIDENCE_WORKING_SET.md`.

Read first if you want the repo’s current answer to “how do we keep default cards renewable instead of prose-only?”
- `design/lane-default-evidence-bundle.md`
- `design/lane-default-evidence-pilot-program.md`
- `meta/DEFAULT_EVIDENCE_WORKING_SET.md`
- `defaults/script-repro-tiny-utility-2026Q1.md`
- `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`

This is the concrete next step beneath the existing defaults corpus: the repo now treats **default card → evidence imports → renewal judgment → diffable receipt** as the practical maintenance loop instead of leaving renewal as manual lore.

- New design notes: `design/lane-default-evidence-bundle.md`, `design/lane-default-evidence-pilot-program.md`
- New proposal: `proposals/epic-lane-default-evidence-bundle.md`
- New gap note: `gaps/reviewable-default-evidence-and-renewal-receipts.md`
- New default card: `defaults/script-repro-tiny-utility-2026Q1.md`
- Meta-engineering: added `meta/DEFAULT_EVIDENCE_WORKING_SET.md`
- Design refresh: `design/lane-default-evaluation-framework.md`, `design/reviewable-lane-defaults-corpus.md`, `design/reviewable-lane-defaults.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/priority refresh: promoted explicit **Lane Default Evidence Bundle** as the immediate practical seam beneath the **Reviewable Lane Defaults Corpus**, so the archive now treats **canon import + registry/supply-chain import + API/compatibility import + support/maintenance import + freshness/replay import + renewal judgment** as distinct control-plane pieces instead of one recommendation paragraph
- Strategy: after proving that a maintained defaults corpus is viable, the next worthy move is not rapid corpus expansion but **renewable evidence packs**; the first new bounded card added under that discipline is **script / repro / tiny utility**, because cargo-script has unusually clear official momentum and a naturally narrow scope
- Hygiene: future corpus revisions should update `meta/DEFAULT_EVIDENCE_WORKING_SET.md` together with `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, and `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`; do not let evidence inputs collapse into prose-only defaults


## Latest addition (rev0378)
The archive now has a **reviewable defaults corpus** under `defaults/` backed by `design/lane-default-evaluation-framework.md` and `design/reviewable-lane-defaults-corpus.md`.

Read first if you want the repo’s current practical answer to “what should we actually recommend right now?”
- `design/lane-default-evaluation-framework.md`
- `design/reviewable-lane-defaults-corpus.md`
- `defaults/conservative-internal-cli-2026Q1.md`
- `defaults/conservative-http-service-2026Q1.md`
- `defaults/polyglot-workspace-component-2026Q1.md`
- `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`

This is the concrete next step beneath `design/reviewable-lane-defaults.md`: the repo now publishes and maintains a small set of default cards instead of only describing the layer abstractly.

- New design note: `design/reviewable-lane-defaults-pilot-program.md`
- New proposal: `proposals/epic-reviewable-lane-defaults.md`
- New gap note: `gaps/scoped-recommendation-defaults-project-classes-freshness-and-overlays.md`
- Meta-engineering: added `meta/CANONICAL_WORKING_SET.md`
- Design refresh: `design/reviewable-lane-defaults.md`, `design/adoption-navigation-bundle.md`, `design/ecosystem-priority-ladder-2026.md`
- Frontier/priority refresh: promoted explicit **Reviewable Lane Defaults** as the immediate execution seam beneath **Adoption Navigation Bundle** so the archive now treats **candidate space + reusable scoped defaults + project-specific adoption briefs + profiled onramp/bootstrap handoffs + local overlays** as separate control-plane layers instead of oscillating between non-answer neutrality and accidental blessing
- Strategy: after shaping Adoption Navigation into a concrete bundle, the next worthy move is to prove **scoped reusable defaults** rather than widen more adjacent navigation leaves or drift into a universal starter-set story
- Hygiene: added `meta/CANONICAL_WORKING_SET.md` and refreshed protocol/frontier/amnesia guidance so future frontier changes update the compact working set and active frontier note together, plus mirror/manifest obligations

## 2026-03-22 — Reviewable lane defaults (turn recommendation philosophy into reusable scoped defaults)
- Re-read the latest archive and looked for the strongest follow-on to rev0376’s Adoption Navigation Bundle. The missing piece was no longer another atlas or another project-specific recommendation note. It was the reusable middle layer between them. The archive already had the pieces — Ecosystem Atlas, Recommendation Posture Ladder, Adoption Navigation, Adoption Decision, Profiled Onramp, Project Bootstrap, and Institutional Overlay — but it still lacked the concrete epic and pilot program for **scoped reusable defaults**.
- Fresh official signals all point at that seam. Rust’s March 20, 2026 challenges post says ecosystem navigation still depends too much on tacit knowledge and choice paralysis. Rust’s December 2025 vision work says users need help getting oriented in crates.io and finding a good “starter set” of crates, while also warning that blessing crates too broadly is politically risky. The 2025 State of Rust survey says online docs remain canonical while editor and LLM-mediated workflows keep rising. crates.io’s January 2026 update added stronger refresh and review inputs like `pubtime`, SLOC, and source links to docs.rs. Cargo’s February 2026 development-cycle note reiterates that Cargo cannot be everything to everyone and that plugins matter. The Rust Foundation’s 2026–2028 strategy still couples stable infrastructure, sustainable maintenance, and adoption growth. Together those signals say the worthy contribution is a thin **`cargo lane` / `lane-default-pack/v0`** layer for recurring project classes, not a global crate leaderboard or a hidden recommendation engine.
- Archive decision: add `design/reviewable-lane-defaults-pilot-program.md`, `proposals/epic-reviewable-lane-defaults.md`, `gaps/scoped-recommendation-defaults-project-classes-freshness-and-overlays.md`, and `meta/CANONICAL_WORKING_SET.md`; refresh `design/reviewable-lane-defaults.md`, `design/adoption-navigation-bundle.md`, `design/ecosystem-priority-ladder-2026.md`, `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, `meta/AMNESIA_RESISTORS.md`, and `meta/REVISION_OPERATING_PROTOCOL.md`; mirror changed canonical files under `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future navigation/default revisions honest by separating **candidate space, reusable scoped default, project-specific override, profiled starter handoff, neutral shared common ground, and local institutional overlay**.
- Sources: https://blog.rust-lang.org/2026/03/20/rust-challenges/ ; https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/ ; https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/ ; https://blog.rust-lang.org/2026/01/21/crates-io-development-update/ ; https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/ ; https://rustfoundation.org/strategic-plan/


- New design note: `design/adoption-navigation-bundle.md`
- New proposal: `proposals/epic-adoption-navigation-bundle.md`
- Design refresh: `design/adoption-decision-stack.md`, `design/ecosystem-priority-ladder-2026.md`, `design/epic-contribution-ladder-2026.md`
- Frontier/priority refresh: promoted an explicit **Adoption Navigation Bundle** so the archive now treats **question → candidate lanes → canonical references → imported evidence → local fit → bounded brief** as a concrete top-band answer-shaping program above Atlas + Canonical Learning + Trust / Maintenance / Semantic Context imports
- Strategy: keep **Build-State Evidence** as the strongest pure build-first candidate, but let **Adoption Navigation** become the clearest research-side bundle when the repo needs a shape-changing move instead of one more adjacent leaf
- Hygiene: added `meta/REVISION_OPERATING_PROTOCOL.md` and refreshed frontier/amnesia guidance so future revisions declare update class, promoted candidate, eliminated alternatives, and required mirror/manifest work

## 2026-03-22 — Adoption navigation bundle (turn ecosystem choice paralysis into a concrete decision bundle)
- Re-read the latest archive and deliberately looked for the next move that would reshape the repo rather than merely add another leaf. After turning Consumer Lifecycle Continuity and Workspace Environment into concrete bundles, the strongest remaining repo-shaping gap was not another stack note but a bundle for the ecosystem-navigation side itself. The archive already had strong substrate in Ecosystem Atlas, Adoption Decision, Canonical Learning, Trust Decision, Maintenance Reality, and Semantic Context, but it still lacked one document that said what the actual portable decision bundle should be.
- Fresh official signals all pushed the same way. Rust’s March 20, 2026 challenges post explicitly names ecosystem choice paralysis and tacit knowledge, saying the problem is less a lack of libraries than the expertise required to choose among them. The 2025 State of Rust survey says online docs remain canonical while editor- and machine-mediated learning keep rising. Rust’s December 2025 vision work says users still need help getting oriented in crates.io and finding a good starter set of crates. docs.rs changed default targets in October 2025 to better reflect current platform reality, crates.io’s January 2026 update added stronger recommendation inputs like Trusted-Publishing-only mode, SLOC, and `pubtime`, and the Rust Foundation’s 2026–2028 strategy keeps adoption, stable infrastructure, and sustainable maintenance coupled. Together those signals say ideal Rust needs a thin recommendation bundle, not another search result page, crate score, or AI chooser.
- Archive decision: add `design/adoption-navigation-bundle.md` and `proposals/epic-adoption-navigation-bundle.md`; refresh `design/adoption-decision-stack.md`, `design/ecosystem-priority-ladder-2026.md`, and `design/epic-contribution-ladder-2026.md`; prepend matching frontier notes in `INDEX.md`, `PRIORITIES.md`, and `STRATEGIC_FRONTIER.md`; update `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; add `meta/REVISION_OPERATING_PROTOCOL.md`; mirror the changed canonical files under `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future revisions honest by separating **question, candidate lanes, canonical references, imported evidence, local-fit checks, and bounded briefs**.
- Sources: https://blog.rust-lang.org/2026/03/20/rust-challenges/ ; https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/ ; https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/ ; https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/ ; https://blog.rust-lang.org/2026/01/21/crates-io-development-update/ ; https://rustfoundation.org/strategic-plan/ ; https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/

- New design note: `design/workspace-environment-bundle.md`
- New proposal: `proposals/epic-workspace-environment-bundle.md`
- Design refresh: `design/workspace-environment-stack.md`, `design/epic-contribution-ladder-2026.md`
- Frontier/priority refresh: promoted an explicit **Workspace Environment Bundle** so the archive now treats **Tooling Contract + Toolchain Productization + Native Dependency + Runtime Settings + Credentials** as one concrete top-band workenv program with explicit **subject → intent → realization → observation → handoff** boundaries
- Strategy: after turning Consumer Lifecycle into a concrete epic, the next strong move was to sharpen a second Tier A candidate instead of minting another seam; this revision turns Workspace Environment into a real bundle MVP with clearer artifacts, substrate boundaries, and non-goals
- Hygiene: refreshed frontier and amnesia guidance so future setup/onboarding/editor/CI/agent revisions keep **workspace subject, declared intent, substrate realization, observed state, secret posture, and bounded handoff** distinct

## 2026-03-22 — Workspace environment bundle (turn a second Tier A candidate into a real workenv epic)
- Re-read the latest archive and deliberately looked for the next move that would change the repo’s shape instead of adding another isolated stack note. After rev0374 turned Consumer Lifecycle Continuity into a concrete receipt-chain epic, the strongest next step was to sharpen a second Tier A candidate into a buildable program. Workspace Environment was the best fit because the archive already had strong leaves for tooling contract, toolchain productization, native dependency posture, runtime settings, credentials, bootstrap, and prototype elevation, but it still lacked one document that said what the workenv bundle itself should be.
- Fresh official signals kept pointing toward the same gap. The 2025 State of Rust survey says online docs remain canonical, editors with agentic support are rising, and resource usage/debugging remain notable productivity pains. Cargo config is hierarchical from the current directory through parent directories, and Cargo workspace discovery also walks parent directories for `[workspace]`, which means environment behavior already depends on discovery boundaries rather than only local files. rustup toolchain files can pin channel/date/components/targets/profile while `path` toolchains have different semantics, so toolchain choice is project-facing but still only one slice of environment truth. Cargo 1.94 says broken parent manifests or `.cargo/config.toml` files can poison unrelated builds. rust-analyzer already runs per-workspace commands by default and supports override commands, extra args/env, and linked-workspace behavior. Dev Containers and Nix both provide real repeatable substrates, but they are substrate-level mechanisms rather than the Rust-specific review layer above them. Together those signals say the missing contribution is a thin **subject → intent → realization → observation → handoff** bundle, not another environment manager.
- Archive decision: add `design/workspace-environment-bundle.md` and `proposals/epic-workspace-environment-bundle.md`; refresh `design/workspace-environment-stack.md` and `design/epic-contribution-ladder-2026.md`; prepend matching frontier notes in `INDEX.md`, `PRIORITIES.md`, and `STRATEGIC_FRONTIER.md`; update `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror the changed canonical files under `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future revisions honest by separating **workspace subject, declared intent, substrate realization, observed state, secret posture, and bounded downstream handoff**.
- Sources: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/ ; https://doc.rust-lang.org/cargo/reference/config.html ; https://doc.rust-lang.org/cargo/reference/workspaces.html ; https://rust-lang.github.io/rustup/overrides.html ; https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/ ; https://rust-analyzer.github.io/book/configuration.html ; https://containers.dev/implementors/spec/ ; https://nix.dev/concepts/flakes.html ; https://rustfoundation.org/strategic-plan/

- New design note: `design/consumer-lifecycle-continuity-bundle.md`
- New proposal: `proposals/epic-consumer-lifecycle-continuity-bundle.md`
- Frontier/priority refresh: promoted an explicit **Consumer Lifecycle Continuity Bundle** so the archive now treats **current managed state + typed lifecycle events + ownership scope + route/home changes + bounded downstream handoffs** as a concrete top-band build target instead of a loose bundle of adjacent install/update/distribution notes
- Strategy: after adding the Epic Contribution Ladder, the stronger move was to sharpen one Tier A candidate rather than mint another seam; this revision turns the lifecycle bundle into a real receipt-chain MVP with clearer artifact boundaries and non-goals
- Hygiene: refreshed frontier and amnesia guidance so future install/update/distribution/incident/sunset revisions keep **first install, current owned state, typed mutations, route changes, and support/incident handoff** distinct

## 2026-03-22 — Consumer lifecycle continuity bundle (turn a top-band candidate into a real receipt-chain epic)
- Re-read the latest archive and deliberately looked for the next move that would change the repo’s shape instead of adding another isolated stack note. After rev0373 introduced the Epic Contribution Ladder 2026, the strongest next step was to sharpen one Tier A candidate into a buildable program. Consumer Lifecycle Continuity was the best fit because the archive already had strong leaf notes for install, update continuity, distribution contract, route mobility, and release truth, but it still lacked a single document that said what the bundle itself should be.
- Fresh official Cargo/Rust signals kept pointing toward the same gap. Cargo install already defines install-root precedence, source classes, reinstall triggers, packaged-lock behavior, and config-discovery boundaries, including the fact that packaged `Cargo.lock` is ignored unless `--locked` is passed and that non-`--path` installs begin config discovery at `$CARGO_HOME/config.toml`. Cargo uninstall uses the same root-precedence model and only removes packages installed with `cargo install`, which makes ownership scope a first-class lifecycle fact. Cargo package says `--exclude-lockfile` is not for general use because some consumers expect the lockfile, including `cargo install --locked`. Cargo’s source-replacement docs say exact-copy mirrors are not patching or private registries, while cargo vendor says vendored sources are read-only and real modifications should use `[patch]` or `path`. Finally, Cargo’s 1.86 development update explicitly highlighted `cargo install-update` as a plugin and said built-in installed-binary update support is still being tracked. Together those signals say the missing contribution is a thin receipt chain for **install → update → rollback/uninstall → route change**, not a universal updater or another package-manager wrapper.
- Archive decision: add `design/consumer-lifecycle-continuity-bundle.md` and `proposals/epic-consumer-lifecycle-continuity-bundle.md`; tighten `design/epic-contribution-ladder-2026.md`; add cross-links from the install/distribution side; prepend matching frontier notes in `INDEX.md`, `PRIORITIES.md`, and `STRATEGIC_FRONTIER.md`; update `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror the changed canonical files under `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future revisions honest by separating **managed subject, current owned state, typed lifecycle mutation, route/home change, and bounded downstream handoff**.
- Sources: https://doc.rust-lang.org/cargo/commands/cargo-install.html ; https://doc.rust-lang.org/cargo/commands/cargo-uninstall.html ; https://doc.rust-lang.org/cargo/commands/cargo-package.html ; https://doc.rust-lang.org/cargo/reference/source-replacement.html ; https://doc.rust-lang.org/cargo/commands/cargo-vendor.html ; https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/

- New design note: `design/epic-contribution-ladder-2026.md`
- Frontier/priority refresh: promoted an explicit **Epic Contribution Ladder 2026** so the archive now distinguishes **research priority** from **build priority** and treats **Build-State Evidence + Workspace Environment + Package Admission + Consumer Lifecycle Continuity + Toolchain Productization** as the most buildable near-term companion-tool band
- Strategy: clarified that the worthy next move for the repo is no longer automatically “one more seam”, but often a thinner MVP and non-goal specification for the most buildable cross-cutting candidates, especially where Cargo/crates.io already expose real machine-usable facts
- Hygiene: refreshed frontier and amnesia guidance so future revisions prefer **build-ladder consolidation, MVP sharpening, and anti-sprawl synthesis** before minting another top-band control-plane note

## 2026-03-22 — Epic contribution ladder 2026 (separate buildable companion tools from merely interesting seams)
- Re-read the latest archive and deliberately looked for the next move that would change the repo’s shape instead of adding one more adjacent stack note. The archive is now rich enough that another isolated seam risks becoming decorative. The stronger move was to add a second ladder: not which frontier seams matter most in theory, but which **thin Rust ecosystem contributions are most buildable now**.
- Fresh official signals kept pointing toward the same need. Rust’s March 20, 2026 challenges post says ecosystem navigation still depends too much on tacit knowledge and choice paralysis. The 2025 State of Rust survey says online docs remain canonical while editor/LLM-mediated learning rises. Rust’s December 2025 vision work says Rust should expand crate-level supportive interfaces and build-workflow extensibility. The 2026 flagships keep pushing cargo-script, public/private dependencies, SBOM support, and build-std / better build-system integration. Cargo 1.94 says workspace/config discovery still causes cross-project breakage, while the March 2026 build-dir-layout testing call shows tools still rely on Cargo internals because the contract surface is incomplete. Cargo 1.86 explicitly called out `cargo install-update` as a plugin and said built-in support is still being tracked. The Rust Foundation’s 2026–2028 strategy then ties stable infrastructure, sustainable maintenance, and adoption together. Together those signals say the repo needs a sharper buildability ladder.
- Archive decision: add `design/epic-contribution-ladder-2026.md`; prepend matching frontier notes in `INDEX.md`, `PRIORITIES.md`, and `STRATEGIC_FRONTIER.md`; update `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror the changed files under `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future revisions honest by separating **research importance, build readiness, MVP shape, non-goals, and anti-sprawl archive hygiene**.
- Sources: https://blog.rust-lang.org/2026/03/20/rust-challenges/ ; https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/ ; https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/ ; https://rust-lang.github.io/rust-project-goals/2026/flagships.html ; https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/ ; https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/ ; https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/ ; https://rustfoundation.org/strategic-plan/

- New design note: `design/distribution-route-mobility-stack.md`
- Frontier/priority refresh: promoted explicit **Distribution-Route Mobility Stack** so the archive now treats **route subject + current route class + exact-copy-or-divergent posture + publish/consumer constraints + route-change intent + bounded downstream handoff** as separate truths instead of letting one registry switch, one mirror config, one vendored tree, or one `[patch]` carry narrate the whole home-change story
- Strategy: clarified that the worthy contribution here is not another registry implementation, mirror manager, vendoring helper, or migration dashboard, but a thin `cargo route` / `route-pack/v0` layer for reviewable home changes across crates.io publication, alternate registries, exact-copy mirrors, vendored/local registries, local development bridges, and continuity-driven route moves
- Hygiene: refreshed frontier and amnesia guidance so future source/distribution/continuity revisions keep **route class, equivalence-vs-divergence, publish constraints, visibility scope, and install/incident/sunset handoff** distinct

## 2026-03-22 — Distribution-route mobility stack (reviewable home changes across registries, mirrors, vendored lanes, and local bridges)
- Re-read the latest archive and deliberately looked for the next frontier move that would change the repo’s shape instead of adding another adjacent continuity or maintenance note. After strengthening support routing, succession continuity, fork continuity, and sunset transition, the strongest missing seam turned out to be the boundary between **knowing where a Rust subject currently lives** and **knowing how a change in that home should be represented when Cargo route classes have materially different semantics**.
- Fresh research kept pointing toward the same gap. Cargo’s registries docs make alternate registries a first-class route, let `package.publish` restrict allowed publish homes, and recent release notes say `cargo publish` will use an alternate registry by default when it is the only allowed target. Cargo’s source-replacement docs then sharpen the equivalence boundary: replacement sources must be exact copies, may not add new crates, and are not patching or private-registry divergence. Cargo’s dependency docs say crates.io packages cannot depend on code published outside crates.io, while **multiple locations** let local `git`/`path` work bridge to a registry version later. `cargo vendor` says vendored sources are read-only and directs actual modifications toward `[patch]` or local `path`, so offline/local copies and divergent local carries already have different official meanings. The January 2026 crates.io update expanded Trusted Publishing and Trusted-Publishing-only mode, making publish-home and publish-authority shifts more explicit. The Rust Foundation’s 2026–2028 strategy explicitly names **signed crates** and **official mirrors**, and the March 2026 challenges post says ecosystem navigation still depends too much on tacit knowledge and choice paralysis. Together those signals say ideal Rust still lacks a compact control layer for route motion.
- Archive decision: add `design/distribution-route-mobility-stack.md`; prepend matching frontier notes in `INDEX.md`, `PRIORITIES.md`, and `STRATEGIC_FRONTIER.md`; update `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror the changed files under `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future source/distribution/continuity revisions honest by separating **route subject, current route class, exact-copy-or-divergent posture, publish/consumer constraints, route-change intent, and bounded downstream handoff**.
- Sources: https://doc.rust-lang.org/cargo/reference/registries.html ; https://doc.rust-lang.org/beta/releases.html ; https://doc.rust-lang.org/cargo/reference/source-replacement.html ; https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html ; https://doc.rust-lang.org/cargo/commands/cargo-vendor.html ; https://blog.rust-lang.org/2026/01/21/crates-io-development-update/ ; https://rustfoundation.org/strategic-plan/ ; https://blog.rust-lang.org/2026/03/20/rust-challenges/

- New design note: `design/sunset-transition-stack.md`
- Frontier/priority refresh: promoted explicit **Sunset Transition Stack** so the archive now treats **sunset subject + narrowing/retirement intent + last-supported/support-window truth + replacement-or-no-successor posture + registry/archive action + consumer off-ramp + closure witness/end-state** as separate truths instead of letting one deprecated badge, one yank, one archived repo, or one successor README narrate the whole end-of-support story
- Strategy: clarified that the worthy contribution here is not another badge scheme, graveyard site, or stealth deprecation score, but a thin `cargo sunset` / `sunset-pack/v0` layer for reviewable support narrowing and end-of-life across deprecated-with-successor, security-fix-only tails, repo-archived-but-still-installable crates, and honest no-successor exits
- Hygiene: refreshed frontier and amnesia guidance so future lifecycle/succession/fork/trust revisions keep **support narrowing, last-supported lines, replacement posture, registry/archive action, consumer guidance, and terminal/reversible end-state** distinct

## 2026-03-22 — Sunset transition stack (honest support narrowing and retirement when code remains discoverable)
- Re-read the latest archive and deliberately looked for the next frontier move that would change the repo’s shape instead of adding another adjacent governance note. After strengthening lifecycle metadata, succession continuity, fork continuity, and support routing, the strongest missing seam turned out to be the boundary between **knowing a Rust project should no longer be a normal default choice** and **knowing how that narrowing or retirement is actually represented when the registry remains a durable archive**.
- Fresh research kept pointing toward the same gap. Cargo’s manifest docs still define maintenance states like `passively-maintained`, `as-is`, `looking-for-maintainer`, and `deprecated`, but they also say crates.io no longer displays badges directly, so the ecosystem has vocabulary without a strong shared review surface. Cargo’s publishing docs say yanks do not delete code and existing lockfiles keep working because crates.io aims to remain a permanent archive. RFC 3660 keeps deletions tightly constrained, which means many real Rust artifacts will remain discoverable even when maintainers want users to stop selecting them by default. RFC 3646 then sharpens the neighboring boundary: unreachable-owner cases should expect a different name rather than registry-mediated transfer, so sunset often borders but should not be confused with succession or continuation. The Rust Foundation’s 2026–2028 strategy and the maintenance writeup both frame maintenance as ongoing, invisible, and burnout-sensitive work, which makes support narrowing or retirement a legitimate stewardship move rather than automatic evidence of neglect. Finally, the March 2026 challenges post says ecosystem navigation still depends too much on tacit knowledge and choice paralysis. Together those signals say ideal Rust still lacks a compact control layer for honest off-ramps.
- Archive decision: add `design/sunset-transition-stack.md`; prepend matching frontier notes in `INDEX.md`, `PRIORITIES.md`, and `STRATEGIC_FRONTIER.md`; update `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror the changed files under `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future lifecycle/succession/fork/trust revisions honest by separating **sunset subject, support narrowing, last-supported lines, replacement posture, registry/archive action, consumer off-ramp, and closure witness/end-state**.
- Sources: https://doc.rust-lang.org/cargo/reference/manifest.html ; https://doc.rust-lang.org/cargo/reference/publishing.html ; https://rust-lang.github.io/rfcs/3660-crates-io-crate-deletions.html ; https://rust-lang.github.io/rfcs/3646-remove-crate-transfer-mediation-policy.html ; https://rustfoundation.org/strategic-plan/ ; https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/ ; https://blog.rust-lang.org/2026/03/20/rust-challenges/

- New design note: `design/fork-continuity-stack.md`
- Frontier/priority refresh: promoted explicit **Fork Continuity Stack** so the archive now treats **origin subject + continuation intent + authority/identity relationship + distribution route + compatibility/migration posture + continuity witness/exit** as separate truths instead of letting one successor pointer, one renamed crate, one `[patch]`, or one alternate registry narrate the whole continuation story
- Strategy: clarified that the worthy contribution here is not a forced-transfer service, fork marketplace, or universal successor badge, but a thin `cargo continuation` / `continuation-pack/v0` layer for reviewable continuity without ownership transfer across owner-unreachable continuations, renamed successors, local carries, alternate homes, and reconvergence
- Hygiene: refreshed frontier and amnesia guidance so future lifecycle/succession/identity/migration/trust revisions keep **origin relationship, approval state, publication route, compatibility claim, local-vs-public continuation, and exit/rejoin posture** distinct

## 2026-03-22 — Fork continuity stack (reviewable continuation when ownership cannot or does not move)
- Re-read the latest archive and deliberately looked for the next frontier move that would change the repo’s shape instead of adding another adjacent governance note. After strengthening lifecycle metadata, support routing, succession continuity, identity, and institutional hosting, the strongest missing seam turned out to be the boundary between **knowing a Rust project should continue** and **knowing how that continuation is actually represented when authority does not cleanly transfer**.
- Fresh research kept pointing toward the same gap. RFC 3646 says the crates.io team wants to stop mediating crate ownership transfers and that unreachable-owner cases must pick a different name. crates.io policy still requires explicit current-owner approval for transfer. Cargo’s override docs say `[patch]` is a real lane for immediate unpublished fixes, while source-replacement docs insist mirrors must be exact copies and are not a patching or private-registry story. Cargo’s registries docs say alternate registries are real homes, but crates.io packages cannot depend on those registries; its dependency docs also say multiple locations let local git/path development bridge to a published registry version later. The Rust Project’s own crate-ownership policy names an **Expatriated** category, which proves continuity outside the original official owner is already a real concept. The Rust Innovation Lab then adds a neutral nonprofit relocation lane, and the March 2026 challenges post reminds us that ecosystem navigation still depends too much on tacit knowledge. Together those signals say ideal Rust still lacks a compact control layer for continuation without transfer.
- Archive decision: add `design/fork-continuity-stack.md`; prepend matching frontier notes in `INDEX.md`, `PRIORITIES.md`, and `STRATEGIC_FRONTIER.md`; update `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror the changed files under `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future lifecycle/succession/identity/migration/trust revisions honest by separating **origin subject, continuation intent, authority/identity relationship, distribution route, compatibility/migration posture, and continuity witness/exit**.
- Sources: https://rust-lang.github.io/rfcs/3646-remove-crate-transfer-mediation-policy.html ; https://crates.io/policies ; https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html ; https://doc.rust-lang.org/cargo/reference/source-replacement.html ; https://doc.rust-lang.org/cargo/reference/registries.html ; https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html ; https://forge.rust-lang.org/policies/crate-ownership.html ; https://blog.rust-lang.org/2025/09/03/welcoming-the-rust-innovation-lab/ ; https://rustfoundation.org/rust-innovation-lab/ ; https://blog.rust-lang.org/2026/03/20/rust-challenges/

- New design note: `design/succession-continuity-stack.md`
- Frontier/priority refresh: promoted explicit **Succession Continuity Stack** so the archive now treats **continuity subject + transition intent + authority surfaces + overlap/transfer plan + institutional anchor + continuity witness** as separate truths instead of letting one “seeking maintainer” note, one owner change, or one funding route narrate the whole continuity story
- Strategy: clarified that the worthy contribution here is not an automatic ownership-transfer engine, public pressure mechanism, or vague sustainability essay, but a thin `cargo succession` / `continuity-pack/v0` layer for reviewable maintainer transitions across co-maintainership, publish-authority changes, release/incident overlap, and neutral-home institutionalization
- Hygiene: refreshed frontier and amnesia guidance so future lifecycle/support/identity/keystone revisions keep **declared intent, authority movement, overlap, institutional anchor, and proof of working continuity** distinct

## 2026-03-22 — Succession continuity stack (turn maintainer-change intent into reviewable continuity transitions)
- Re-read the latest archive and deliberately looked for the next frontier move that would change the repo’s shape instead of adding another adjacent governance note. After strengthening maintenance reality, keystone stewardship, support routing, institutional overlays, and incident posture, the strongest missing seam turned out to be the boundary between **saying a Rust project needs continuity** and **showing how continuity will actually survive a maintainer transition**.
- Fresh research kept pointing toward the same gap. The Rust Foundation’s 2026–2028 strategy explicitly calls for funding models for ongoing maintenance, transparent support criteria, contributor→maintainer pathways, and help for under-resourced core crate owners. The Maintainers Fund announcement says support should be reliable, aligned with project priorities, and accountable. The maintenance writeup says maintenance is broad and ongoing, which means the most important transition knowledge is often invisible unless it is exported deliberately. The October 2025 program-management update says some teams rely on one or two people just to stay afloat. crates.io policy then sharpens the authority boundary: ownership transfer requires explicit current-owner approval, so succession cannot be inferred from inactivity or desire. Meanwhile crates.io’s 2026 development update says publish authority is increasingly mediated through Trusted Publishing and Trusted-Publishing-only mode, while Cargo’s publishing docs remind us that token and release authority are concrete secrets and surfaces, not abstractions. And the Rust Innovation Lab proves there is a real continuity lane above simple co-maintainership: neutral governance, legal/admin support, fiscal sponsorship, and a stable home for keystone infrastructure. Together those signals say ideal Rust still lacks a compact control layer for continuity transition itself.
- Archive decision: add `design/succession-continuity-stack.md`; refresh `design/stewardship-support-routing-stack.md`; prepend matching frontier notes in `INDEX.md`, `PRIORITIES.md`, and `STRATEGIC_FRONTIER.md`; update `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror the changed files under `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future lifecycle/support/identity/keystone revisions honest by separating **continuity subject, transition intent, authority surfaces, overlap/transfer plan, institutional anchor, and continuity witness**.
- Sources: https://rustfoundation.org/strategic-plan/ ; https://rustfoundation.org/media/announcing-the-rust-foundation-maintainers-fund/ ; https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/ ; https://blog.rust-lang.org/inside-rust/2025/11/19/program-management-update--october-2025/ ; https://crates.io/policies ; https://blog.rust-lang.org/2026/01/21/crates-io-development-update/ ; https://doc.rust-lang.org/cargo/reference/publishing.html ; https://rustfoundation.org/rust-innovation-lab/ ; https://rustfoundation.org/media/rust-foundation-launches-rust-innovation-lab-with-rustls-as-inaugural-project/ ; https://rustfoundation.org/media/rust-foundation-signs-joint-statement-on-open-source-infrastructure-stewardship/

- New design note: `design/stewardship-support-routing-stack.md`
- Frontier/priority refresh: promoted explicit **Stewardship Support Routing Stack** so the archive now treats **support need + evidence slice + intervention class + routing/privacy/eligibility + accepted backing + review/exit** as separate truths instead of letting one help request, one funding mention, or one “critical project” label narrate the whole support story
- Strategy: clarified that the worthy contribution here is not another public health dashboard, generic grant portal, or hidden allocator, but a thin `cargo supportroute` / `support-route-pack/v0` layer for reviewable routing across volunteer help, co-maintainership, release/triage relief, maintainer funding, fiscal sponsorship, and neutral governance/hosting
- Hygiene: refreshed frontier and amnesia guidance so future maintenance/keystone/funding/overlay revisions keep **need evidence, intervention class, privacy/eligibility, accepted support posture, and expiry/review** distinct

## 2026-03-22 — Stewardship support routing stack (turn maintenance pressure and criticality into honest support routes)
- Re-read the latest archive and deliberately looked for the next frontier move that would change the repo’s shape instead of adding another adjacent mechanism note. After multiple revisions on maintenance reality, keystone stewardship, institutional overlays, incidents, deviations, and canaries, the strongest missing seam turned out to be the boundary between **knowing a Rust project matters or is strained** and **knowing what kind of help should actually be routed**.
- Fresh research kept pointing toward the same gap. The Rust Foundation’s 2026–2028 strategy explicitly centers stable infrastructure, sustainable maintenance, adoption, and community support. The Maintainers Fund announcement says the goal is long-term maintainer roles and continuity, with transparent alignment to Rust Project priorities. The maintenance writeup says maintenance is broad, often invisible, and burnout-sensitive, so “needs support” cannot just mean “has open issues”. The October 2025 program-management update says maintenance work often loses out to feature funding and some teams effectively rely on one or two people. The Rust Innovation Lab then proves that not all support is money: some projects need fiscal sponsorship, governance, legal, networking, marketing, and administrative support in a neutral nonprofit environment. And the 2025 State of Rust survey still shows concern about developer and maintainer support and explicitly asks companies to support Rust contributors and crate authors they rely on. Together those signals say Rust now has multiple real support lanes, but still lacks a compact control layer for matching evidence to the right intervention.
- Archive decision: add `design/stewardship-support-routing-stack.md`; refresh `design/stewardship-pilot-program.md`; prepend matching frontier notes in `INDEX.md`, `PRIORITIES.md`, and `STRATEGIC_FRONTIER.md`; update `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror the changed files under `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future maintenance/keystone/funding/overlay revisions honest by separating **support subject, need/evidence slice, intervention class, routing/privacy/eligibility, accepted backing, and review/exit posture**.
- Sources: https://rustfoundation.org/strategic-plan/ ; https://rustfoundation.org/media/announcing-the-rust-foundation-maintainers-fund/ ; https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/ ; https://blog.rust-lang.org/inside-rust/2025/11/19/program-management-update--october-2025/ ; https://rustfoundation.org/media/rust-foundation-launches-rust-innovation-lab-with-rustls-as-inaugural-project/ ; https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

- New design note: `design/deviation-governance-stack.md`
- Frontier/priority refresh: promoted explicit **Deviation Governance Stack** so the archive now treats **normative basis + deviation subject + mechanism + scope + owner/justification + expiry/watch + exit** as separate truths instead of letting one waiver comment, one `[patch]`, one nightly pin, or one allow-fail CI lane narrate the whole exception story
- Strategy: clarified that the worthy contribution here is not another policy wiki, giant waiver spreadsheet, or hidden compliance engine, but a thin `cargo deviate` / `deviation-pack/v0` layer for reviewable bounded deviations across lints, migrations, preview adoption, dependency overrides, watch-lane downgrades, and emergency carries
- Hygiene: refreshed frontier and amnesia guidance so future preview/baseline/canary/incident/trust/lint revisions keep **normative basis, mechanism, scope, owner, review trigger, and exit posture** distinct

## 2026-03-22 — Deviation governance stack (turn scattered exceptions into reviewable bounded deviations)
- Re-read the latest archive and deliberately looked for the next frontier move that would change the repo’s shape instead of adding another adjacent mechanism note. After a run of overlays, preview adoption, canary validation, baseline ratchets, incident response, and multiple waiver-carrying kits, the strongest missing seam turned out to be the boundary between **having a real exception in a Rust project** and **being able to review that exception honestly over time**.
- Fresh research kept pointing toward the same gap. The rustc lint docs say `expect` exists so a suppression can fail loudly once it is no longer needed. The Edition Guide’s advanced migration docs say `cargo fix --edition` may need repeated runs, partial migration lints, or `--broken-code` carries across configurations. The nightly and unstable-features docs say preview capabilities require explicit activation and often a per-project override or pin. Cargo’s override docs show `[patch]` as a real lane for bugfix carries and unpublished upstream work, while Cargo’s config docs warn that config-local patches are usually not checked into source control and are shaped by hierarchical config merging. Source replacement then makes an even sharper distinction: mirrors/vendors must be exact copies and are not the same as patching. Cargo’s publishing docs say yanks do not fix existing lockfiles. The CI guide says latest-deps jobs may intentionally continue on error or rely on schedules/notifications that may not reach an owner. And `rust-version` docs say drift from a stated support policy creates user confusion and that multiple policies can exist in one workspace. Together those signals say Rust already has many legitimate deviation mechanisms, but still lacks a compact cross-cutting review layer for owner, scope, expiry, and exit.
- Archive decision: add `design/deviation-governance-stack.md`; prepend matching frontier notes in `INDEX.md`, `PRIORITIES.md`, and `STRATEGIC_FRONTIER.md`; update `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror changed files under `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future preview/baseline/canary/incident/trust/lint revisions honest by separating **normative basis, deviation subject, mechanism, scope, owner/justification, expiry/watch, and exit posture**.
- Sources: https://doc.rust-lang.org/rustc/lints/levels.html ; https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html ; https://doc.rust-lang.org/cargo/reference/unstable.html ; https://doc.rust-lang.org/book/appendix-07-nightly-rust.html ; https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html ; https://doc.rust-lang.org/cargo/reference/config.html ; https://doc.rust-lang.org/cargo/reference/source-replacement.html ; https://doc.rust-lang.org/cargo/reference/publishing.html ; https://doc.rust-lang.org/cargo/guide/continuous-integration.html ; https://doc.rust-lang.org/cargo/reference/rust-version.html ; https://blog.rust-lang.org/2026/03/20/rust-challenges/ ; https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

- New design note: `design/ecosystem-incident-response-stack.md`
- Design refresh: clarified that `design/incident-kit.md` now sits below the new stack as the concrete CLI/artifact surface rather than the whole response story
- Frontier/priority refresh: promoted explicit **Ecosystem Incident Response Stack** so the archive now treats **incident subject + exposure slice + containment actions + rebuild/reissue truth + communication handoff + post-incident policy/drill import** as separate truths instead of letting one RustSec advisory, one yank, or one security scanner result narrate the whole response
- Strategy: clarified that the worthy contribution here is not another scanner wrapper, security score, dashboard, or generic supply-chain essay, but a thin `cargo incident` / `incident-pack/v0` layer for reviewable containment and reissue programs across malicious crates, compromised publish paths, local overrides, release replacement, and downstream communication
- Hygiene: refreshed frontier and amnesia guidance so future trust/admission/canary/release/support revisions keep **incident subject, exposure, containment, rebuild/reissue, communication, and post-incident policy change** distinct

## 2026-03-22 — Ecosystem incident response stack (turn advisories and removals into reviewable containment + reissue programs)
- Re-read the latest archive and deliberately looked for the next frontier move that would change the repo’s shape instead of adding another adjacent note. After a run of recommendation, bootstrap, preview, canary, baseline, prototype, defect, and iteration layers, the next missing seam turned out to be the boundary between **knowing there is a Rust ecosystem incident** and **proving what local containment, rebuild, reissue, and downstream communication actually happened**.
- Fresh research kept pointing toward the same gap. The January 2026 crates.io development update says crate pages now expose a Security tab backed by RustSec advisories, expands Trusted Publishing to GitLab CI/CD, allows Trusted-Publishing-only mode, and blocks risky GitHub triggers like `pull_request_target` and `workflow_run`. The February 2026 malicious-crate notification-policy update says routine malicious-crate removals will always get a RustSec advisory, while broad public blog posts become the exception. The Rust Foundation’s 2026–2028 strategy centers secure infrastructure, signed crates, official mirrors, and sustainable crates.io/release operations. The Foundation’s May 2025 security update says provenance tracking is live, Typomania and Painter have matured, real-time scanning pilots are underway, a Rust-focused Capslock-style Cargo subcommand is being built, and TUF-based signed-metadata work remains on the roadmap. Rust’s 2026 flagships keep secure-supply-chain work active via public/private dependencies and SBOM support. Cargo’s publishing docs then sharpen the operational point: yanking does not delete code or fix existing lockfiles, while Cargo’s override docs show `[patch]` as a real local remediation lane.
- Archive decision: add `design/ecosystem-incident-response-stack.md`; refresh `design/incident-kit.md`; prepend matching frontier notes in `INDEX.md`, `PRIORITIES.md`, and `STRATEGIC_FRONTIER.md`; update `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror the changed files under `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future trust/admission/canary/release/support revisions honest by separating **incident subject, exposure, containment, rebuild/reissue, communication, and post-incident policy change**.
- Sources: https://blog.rust-lang.org/2026/01/21/crates-io-development-update/ ; https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/ ; https://rustfoundation.org/strategic-plan/ ; https://rustfoundation.org/media/strengthening-rust-security-with-alpha-omega-a-progress-update/ ; https://rust-lang.github.io/rust-project-goals/2026/flagships.html ; https://doc.rust-lang.org/cargo/reference/publishing.html ; https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html

- New design note: `design/canary-validation-stack.md`
- Frontier/priority refresh: promoted explicit **Canary Validation Stack** so the archive now treats **baseline/support policy + selected watch lanes + gating/cadence rules + observed canary outcomes + escalation handoff** as separate truths instead of letting one CI matrix, one scheduled dependency job, or one future-incompat notice narrate the whole advance-warning story
- Strategy: clarified that the worthy contribution here is not another CI template repo, dashboard, dependency bot, or generic “test stable/beta/nightly” essay, but a thin `cargo canary` / `canary-pack/v0` layer for reviewable early-warning programs across stable, beta, nightly, MSRV, latest-deps, and future-incompat lanes
- Hygiene: refreshed frontier and amnesia guidance so future preview/baseline/migration/report/compatibility revisions keep **watch lanes, gating policy, cadence, coverage slices, observed outcomes, and escalation destinations** distinct

- New design note: `design/preview-adoption-stack.md`
- Frontier/priority refresh: promoted explicit **Preview Adoption Stack** so the archive now treats **preview subject + activation/pin + adoption scope + guardrails + watch/landing posture + exit handoff** as separate truths instead of letting one nightly toolchain pin, `#![feature]` list, or CI lane narrate the whole unstable story
- Strategy: clarified that the worthy contribution here is not another feature-tracker portal, nightly distro, or generic “use stable unless you must” essay, but a thin `cargo previewadopt` / `preview-pack/v0` layer for reviewable preview usage across nightly language features, Cargo `-Z` flags, unstable edition previews, beta validation, and eventual stable landing or removal
- Hygiene: refreshed frontier and amnesia guidance so future baseline/migration/workenv/docs revisions keep **preview subject, activation mechanism, adoption scope, guardrails, watchpoints, and exit posture** distinct

- New design note: `design/baseline-ratchet-stack.md`
- Frontier/priority refresh: promoted explicit **Baseline Ratchet Stack** so the archive now treats **current baseline vector + proposed ratchet delta + workspace/member variance + verification matrix + release-line policy + downstream handoff** as separate truths instead of letting one `cargo fix` run, `rust-version` bump, or release note narrate the whole floor change
- Strategy: clarified that the worthy contribution here is not another upgrader, CI snippet, or “always latest” policy page, but a thin `cargo ratchet` / `baseline-pack/v0` layer for reviewable edition / `rust-version` / resolver / toolchain / release-line changes
- Hygiene: refreshed frontier and amnesia guidance so future migration/compatibility/lifecycle/release revisions keep **baseline vector, ratchet intent, workspace variance, verification scope, branch policy, and downstream claims** distinct
- New design note: `design/iteration-profile-stack.md`
- Frontier/priority refresh: promoted explicit **Iteration Profile Stack** so the archive now treats **workflow intent + evidence basis + chosen config/editor realization + debug/fidelity/concurrency tradeoffs + observed before/after consequences + bounded downstream import** as separate truths instead of letting one build-speed tip or editor preset define the whole local loop story
- Strategy: clarified that the worthy contribution here is not another build-speed blog post, one universal dev profile, hidden IDE preset, or local daemon, but a thin `cargo iterprofile` / `iter-profile-pack/v0` layer for publishing reviewable iteration tradeoffs across Cargo profiles, linkers, debuginfo, target-dir posture, and debugger reality
- Hygiene: refreshed frontier and amnesia guidance so future build/debug/workenv/bootstrap revisions keep **workflow goal, diagnosis/evidence, chosen profile delta, preserved debug posture, contention/duplication costs, and observed outcome** distinct

## 2026-03-22 — Iteration profile stack (turn local-loop tradeoffs into reviewable artifacts)
- Re-read the latest archive and deliberately looked for the next frontier move that would change the repo’s shape instead of adding another adjacent tool idea. After several revisions on bootstrap, overlays, async transition, prototype elevation, and defect escalation, the next missing layer turned out to be the boundary between **diagnosing a slow or awkward Rust loop** and **choosing a reusable local iteration profile**.
- Fresh research kept pointing toward the same gap. Rust’s March 20, 2026 challenges post says compile times are a universal productivity tax and explicitly says that faster linking or hot reloading would have outsized leverage on development velocity. The 2025 compiler-performance survey says the default `dev` profile’s full debuginfo slows compilation and linking, says many users still have not tried easy build-speed mechanisms, and says Cargo is considering a lower-debuginfo default plus a built-in debugging profile. Cargo’s own profiles docs show that built-in/custom profiles, `debug = "line-tables-only"|"limited"|"full"`, config overrides, and `split-debuginfo` are already real supported levers rather than unofficial folklore. Cargo’s build-analysis goal says rebuild reasons, CLI flags, profiles, and run IDs should become machine-usable. The build-dir-layout goal plus the March 13, 2026 testing call say editor/CLI coexistence, lock contention, user-wide cache, and tool reliance on unspecified build-dir details are still live seams. rust-analyzer explicitly documents `cargo.targetDir` as a lock-avoidance tradeoff that duplicates artifacts. And the 2026 debugging survey says debugger support still varies across debugger families and operating systems and that async debugging is not yet first-class.
- Archive decision: add `design/iteration-profile-stack.md`; prepend matching frontier notes in `PRIORITIES.md` and `STRATEGIC_FRONTIER.md`; update `INDEX.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror the changed files under `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future build/debug/workenv/bootstrap revisions honest by separating **workflow intent, evidence basis, chosen profile/config/editor realization, debug/fidelity/concurrency tradeoffs, and observed outcomes**.
- Sources: https://blog.rust-lang.org/2026/03/20/rust-challenges/ ; https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/ ; https://doc.rust-lang.org/cargo/reference/profiles.html ; https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html ; https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html ; https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/ ; https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/ ; https://rust-analyzer.github.io/book/configuration.html ; https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

- New design note: `design/defect-escalation-stack.md`
- Frontier/priority refresh: promoted explicit **Defect Escalation Stack** so the archive now treats **local observation/session evidence + minimized-subject lineage + routing/dedup posture + issue/regression-test handoff** as separate truths instead of letting a useful repro or issue template silently define the whole escalation story
- Strategy: clarified that the worthy contribution here is not another issue template, crash uploader, hosted triage portal, or hidden minimizer bot, but a thin `cargo escalate` / `defect-escalation-pack/v0` layer for turning local Rust failures into reviewable upstream artifacts with visible minimization, routing, and testability
- Hygiene: refreshed frontier and amnesia guidance so future script/debug/build/support revisions keep **observed subject, reduced subject, duplicate-search posture, selected target, and regression-test suitability** distinct

## 2026-03-22 — Defect escalation stack (turn local Rust failures into actionable upstream issues or regression-test candidates)
- Re-read the latest archive and deliberately looked for the next frontier move that would change the repo’s shape instead of adding another adjacent idea. After several revisions on recommendation, bootstrap, async transition, prototype elevation, and local overlays, the next missing layer turned out to be the boundary between **local failure evidence** and **actionable upstream escalation**.
- Fresh research kept pointing toward the same gap. The cargo-script goal explicitly says single-file packages should reduce friction for bug reports and warns that people currently under-specify repro cases. The January 2026 program-management update says cargo script is especially good for minimal bug reproducers and quick prototypes. Cargo’s build-analysis goal and the Cargo 1.94 cycle show `cargo report rebuild`, `cargo report sessions`, and timing history maturing into machine-usable local evidence. Rust release notes still explicitly ask users to test nightly and report bugs early. The rustc-dev-guide’s fuzzing guide gives a concrete reporting contract: verify on latest nightly, include a reasonably minimal standalone example, include template data, search for existing reports, and format the case. The rustc-dev-guide’s test-writing docs then say minimized bug reports should become succinct regression tests, while compiler-team triage actively tracks regressions and high-priority bugs.
- Archive decision: add `design/defect-escalation-stack.md`; prepend matching frontier notes in `PRIORITIES.md` and `STRATEGIC_FRONTIER.md`; update `INDEX.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror changed files into `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future script/debug/build/support/triage revisions honest by separating **observed subject/session evidence, minimized-subject lineage, routing/dedup posture, and issue/regression-test handoff**.
- Sources: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-script.html ; https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/ ; https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html ; https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/ ; https://doc.rust-lang.org/beta/releases.html ; https://rustc-dev-guide.rust-lang.org/fuzzing.html ; https://rustc-dev-guide.rust-lang.org/tests/adding.html ; https://rustc-dev-guide.rust-lang.org/compiler-team.html

- New design note: `design/prototype-elevation-stack.md`
- Frontier/priority refresh: promoted explicit **Prototype Elevation Stack** so the archive now treats **single-file subject truth + lift decision + introduced project/workspace/environment structure + equivalence/drift checks + downstream handoff** as separate truths instead of letting a useful script silently turn into a fake finished project
- Strategy: clarified that the worthy contribution here is not another template generator, repo wizard, or hidden “promote this script” button, but a thin `cargo elevate` / `elevate-pack/v0` layer for publishing reviewable lifts from repros/prototypes to real Rust projects with visible drift and bounded handoffs
- Hygiene: refreshed frontier and amnesia guidance so future script/bootstrap/workenv/tooling revisions keep **standalone script truth, promotion decision, lifted structure, equivalence claims, and consumer handoff** distinct

## 2026-03-22 — Prototype elevation stack (bridge single-file repros and real projects without losing the subject)
- Re-read the latest archive and deliberately looked for a frontier move that would change the repo’s shape instead of adding another adjacent note. After pushing on guidance, defaults, overlays, bootstrap, and async transition, the next missing layer turned out to be the boundary between **single-file scripts/prototypes/repros** and **reviewable long-lived Rust projects**.
- Fresh research kept pointing toward the same gap. The active cargo-script work says single-file packages matter for bug reports, educational material, prototyping, and small utilities. The January 2026 program-management update says those one-file subjects are especially valuable for minimal reproducers and quick prototypes. Cargo’s unstable docs make scripts intentionally distinct from full projects: they are not auto-discovered like `Cargo.toml`, disallow workspace and target tables, and use a hashed `$CARGO_HOME/target/<hash>` plus a lockfile in `CARGO_TARGET_DIR`. Meanwhile the 2025 State of Rust survey says docs remain canonical while editor/LLM-mediated workflows rise, Rust’s 2025 vision work says users still need better starter-set and ecosystem-navigation help, and the March 20, 2026 challenges post says learning paths and iteration friction are still central.
- Archive decision: add `design/prototype-elevation-stack.md`; prepend matching frontier notes in `PRIORITIES.md` and `STRATEGIC_FRONTIER.md`; update `INDEX.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror changed files into `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future script/bootstrap/workenv/tooling revisions honest by separating **original one-file subject truth, promotion decision, introduced manifest/workspace/environment structure, equivalence or repro-drift checks, and bounded downstream handoffs**.
- Sources: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-script.html ; https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/ ; https://doc.rust-lang.org/cargo/reference/unstable.html ; https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/ ; https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/ ; https://blog.rust-lang.org/2026/03/20/rust-challenges/

- New design note: `design/async-transition-stack.md`
- Frontier/priority refresh: promoted explicit **Async Transition Stack** so the archive now treats **sync baseline + async trigger + runtime-family commitment + lifecycle/reliability/debugging consequences + learning/bootstrap handoff** as separate truths instead of letting one runtime choice or tutorial silently define the whole async story
- Strategy: clarified that the worthy contribution here is not another runtime, framework, or async tutorial empire, but a thin `cargo asyncroute` / `async-route-pack/v0` layer for publishing reviewable sync→async route decisions with visible alternatives, freshness, and downstream handoffs
- Hygiene: refreshed frontier and amnesia guidance so future async/onramp/service/debug revisions keep **sync baseline, async boundary reason, runtime-family posture, lifecycle/reliability, debug/iteration posture, and canonical-learning/bootstrap consequences** distinct

## 2026-03-21 — Async transition stack (close the sync→async chasm without pretending async is one lane)
- Re-read the latest archive and deliberately looked for a frontier move that would change the repo’s shape rather than merely add another adjacent note. After several revisions on crate guidance, defaults, overlays, and bootstrap, the next missing execution layer turned out not to be another recommendation artifact but the **sync→async boundary** itself.
- Fresh research kept pointing toward the same gap. Rust’s March 20, 2026 challenges post says async is still a major pain point, that many developers avoid it, and that runtime choice creates hard-to-reverse lock-in. The 2026 Rust Project Goals page keeps **Just Add Async** active, while the earlier async flagship says the long-term aim is parity with sync Rust but still names runtime-choice stress and interop trouble. The 2026 debugging survey explicitly says first-class async debugging is still unfinished. And the 2025 compiler-performance survey says workflows differ materially, editor/Cargo contention is a real blocker, and default debuginfo often trades iteration speed against debug posture.
- Archive decision: add `design/async-transition-stack.md`; prepend matching frontier notes in `PRIORITIES.md` and `STRATEGIC_FRONTIER.md`; update `INDEX.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror changed files into `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future async/onramp/service/debug revisions honest by separating **sync baseline, async trigger, runtime-family commitment, lifecycle/reliability, debug/iteration posture, and learning/bootstrap handoff**.
- Sources: https://blog.rust-lang.org/2026/03/20/rust-challenges/ ; https://rust-lang.github.io/rust-project-goals/2026/flagships.html ; https://rust-lang.github.io/rust-project-goals/2025h1/async.html ; https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/ ; https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/ ; https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

- New design note: `design/institutional-overlay-stack.md`
- Frontier/priority refresh: promoted explicit **Institutional Overlay Stack** so the archive now treats **public lane defaults + local institutional overlays + project-specific adoption/bootstrap/workenv/admission consequences** as separate control-plane layers instead of laundering org policy into public Rust guidance
- Strategy: clarified that the worthy contribution here is not another internal portal, starter-fork empire, or hidden policy bot, but a thin `cargo overlay` / `overlay-pack/v0` layer for publishing reviewable local deltas atop shared defaults with visible freshness, ownership, and bounded handoffs
- Hygiene: refreshed frontier and amnesia guidance so future revisions keep **public defaults, neutral common ground, local overlays, starter realization, workspace environment, and package policy** distinct

## 2026-03-21 — Institutional overlay stack (make local defaults explicit instead of smuggling them into public guidance)
- Re-read the latest archive and deliberately looked for the next seam that would reduce repeated future drift rather than merely add another adjacent note. The archive already distinguished public candidate space, reusable scoped defaults, project-specific adoption briefs, profiled onramps, bootstrap, and local overlays in principle; what it still lacked was a concrete execution layer for those **local overlays** themselves.
- Fresh research kept pointing toward the same gap. Rust’s December 2025 vision work says users need starter-set guidance but simple blessing is risky; Rust’s March 20, 2026 challenges post says ecosystem navigation still depends too much on tacit knowledge and directly names choice paralysis; the 2025 State of Rust survey says docs remain canonical while editor/LLM-mediated workflows rise; Cargo config and rustup overrides already make local configuration/toolchain posture real and hierarchical; Cargo 1.94 shows broken parent config/workspace discovery can poison unrelated builds; crates.io now exposes Security-tab, Trusted Publishing, SLOC, and `pubtime`; and the Rust Foundation’s 2026–2028 strategy keeps stable infrastructure, sustainable maintenance, and adoption coupled.
- Archive decision: add `design/institutional-overlay-stack.md`; prepend matching frontier notes in `PRIORITIES.md` and `STRATEGIC_FRONTIER.md`; update `INDEX.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror changed files into `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future guidance/bootstrap/workenv/policy revisions honest by separating **public defaults, neutral common ground, local institutional overlays, project-specific adoption, starter/environment realization, and package-admission consequences**.
- Sources: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/ ; https://blog.rust-lang.org/2026/03/20/rust-challenges/ ; https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/ ; https://doc.rust-lang.org/cargo/reference/config.html ; https://rust-lang.github.io/rustup/overrides.html ; https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/ ; https://blog.rust-lang.org/2026/01/21/crates-io-development-update/ ; https://rustfoundation.org/strategic-plan/

- New design note: `design/reviewable-lane-defaults.md`
- Frontier/priority refresh: promoted explicit **Reviewable Lane Defaults** so the archive now treats **atlas candidate space + reusable scoped defaults + project-specific adoption briefs + profiled onramp/bootstrap handoffs** as separate control-plane layers instead of oscillating between generic non-answers and accidental blessing
- Strategy: clarified that the worthy contribution here is not another blessed-crates page, hidden scorer, or template bundle, but a thin `cargo lane` / `lane-default-pack/v0` layer for publishing scoped reusable defaults with visible alternatives, freshness, and downstream handoffs
- Hygiene: refreshed frontier and amnesia guidance so future revisions keep **candidate-space truth, scoped defaults, project-specific adoption briefs, profiled starter defaults, neutral shared common ground, and local institutional overlays** distinct

## 2026-03-21 — Reviewable lane defaults (publish reusable scoped defaults without pretending they are universal)
- Re-read the latest archive and deliberately looked for the next control-plane seam that would reduce repeated future drift rather than merely add another adjacent idea. The archive already had strong notes for Atlas, Adoption Decision, Recommendation Posture, Profiled Onramp, and Project Bootstrap, but it still lacked a reusable layer for saying “for this recurring project class, here is the default Rust lane we are prepared to recommend right now.”
- Fresh research kept pointing toward the same gap. Rust’s December 2025 vision work says users need help navigating crates.io and do not have a clear place to get advice on a good starter set, but also says simple blessing is risky. Rust’s March 20, 2026 challenges post says ecosystem navigation still depends too much on tacit knowledge and directly names choice paralysis. The 2025 State of Rust survey says docs remain canonical while editor/LLM-mediated workflows rise, which makes fuzzy default authority more dangerous. crates.io now exposes richer refresh inputs like Security-tab advisories, Trusted Publishing posture, SLOC, and `pubtime`. And Cargo continues to say plugins matter because Cargo itself cannot be everything to everyone.
- Archive decision: add `design/reviewable-lane-defaults.md`; prepend matching frontier notes in `PRIORITIES.md` and `STRATEGIC_FRONTIER.md`; update `INDEX.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror changed files into `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future crate-guidance revisions honest by separating **atlas candidate space, reusable scoped defaults, project-specific adoption briefs, profiled starter defaults, neutral shared common ground, and local institutional overlays**.
- Sources: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/ ; https://blog.rust-lang.org/2026/03/20/rust-challenges/ ; https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/ ; https://blog.rust-lang.org/2026/01/21/crates-io-development-update/ ; https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

- New design note: `design/recommendation-posture-ladder.md`
- Strategy: clarified that the worthy contribution here is not another blessed-crates page, opaque recommender, or assistant with one undifferentiated confidence level, but a thin recommendation-control layer that distinguishes **candidate sets, lane defaults, profiled starter defaults, neutral common ground, and local overlays**
- Re-read the latest archive and deliberately looked for the next seam that would reduce future drift rather than add another adjacent idea. Fresh official Rust signals pointed toward the same missing layer: the December 2025 vision work says Rust needs starter-set guidance but simple blessing is politically risky; the March 20, 2026 challenges post says ecosystem navigation still depends too much on tacit knowledge and choice paralysis; the 2025 State of Rust survey says docs remain canonical while editor/LLM mediation rises; crates.io now exposes materially richer recommendation inputs; and Cargo continues to frame plugins as companion infrastructure because Cargo cannot be everything to everyone.
- Archive decision: add `design/recommendation-posture-ladder.md`; update `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror changed files into `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep the next worthy move framed as an **explicit recommendation-posture ladder** rather than another global default list.

## 2026-03-21 — Recommendation posture ladder (say more than nothing without accidentally blessing everything)
- Re-read the latest archive and deliberately looked for the next control-plane seam that the repo still treated too loosely. The archive already had serious notes for adoption decisions, atlas curation, profile-aware onramps, project bootstrap, and interop commons, but it still lacked a compact rule for **what kind of recommendation claim** each layer is actually allowed to make.
- Fresh research kept pushing toward the same missing governance seam. Rust’s December 2025 vision work says users need help navigating crates.io and do not have a clear place to get advice on a good “starter set” of crates, but also says blessing crates carries political risk. Rust’s March 20, 2026 challenges post says ecosystem navigation still depends too much on tacit knowledge, directly names choice paralysis, and says the recommendation tradeoff may need a more creative answer. The 2025 State of Rust survey says docs remain canonical while editor/LLM-mediated learning rises, which makes recommendation authority fuzzier and more consequential. crates.io now exposes Security-tab, Trusted Publishing, SLOC, and `pubtime`, which means the evidence feeding recommendation layers is materially richer than before. And Cargo’s 1.93 cycle repeats that Cargo cannot be everything to everyone, so a companion control-plane layer remains the right execution posture.
- Archive decision: add `design/recommendation-posture-ladder.md`; prepend matching frontier notes in `PRIORITIES.md` and `STRATEGIC_FRONTIER.md`; update `AGENTS.md`, `RESEARCH_LOG.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror changed files into `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep future curation/onramp/bootstrap/common-ground revisions honest by separating **raw evidence import, curated candidate sets, reviewable lane defaults, profiled starter defaults, neutral shared common ground, and local institutional overlays**.
- Sources: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/ ; https://blog.rust-lang.org/2026/03/20/rust-challenges/ ; https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/ ; https://blog.rust-lang.org/2026/01/21/crates-io-development-update/ ; https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/

- New design note: `design/profiled-onramp-stack.md`
- Strategy: clarified that the worthy contribution here is not another tutorial portal, universal curriculum, or hidden assistant-tutor layer, but a thin `cargo onramp` / `onramp-pack/v0` composition surface that keeps background profile, concept translation, canonical learning imports, lane choice, bootstrap handoff, and environment realization distinct
- Re-read the latest archive and deliberately looked for the next control-plane seam that the repo still treated too loosely. Fresh official Rust signals pointed toward the same gap: the March 20, 2026 challenges post says learning Rust is strongly background- and domain-dependent and recommends tailored learning paths; the 2025 State of Rust survey says docs remain canonical while editor/LLM mediation rises; the 2025 vision work still says users need better starter-set and guidance support; and `cargo script` continues to lower friction for tiny proofs, examples, and bug reports.
- Archive decision: add `design/profiled-onramp-stack.md`; update `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror changed files into `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep the next worthy move framed as a **profile-aware onramp composition layer** rather than another pile of tutorials or starter templates.

- New design note: `design/project-bootstrap-stack.md`
- Frontier/priority refresh: promoted an explicit **Project Bootstrap Stack** so the archive now treats **Adoption Decision + Starter Pack + Workspace Environment** as a distinct execution bridge just below the top control-plane band
- Strategy: clarified that the worthy contribution here is not another template engine, quickstart wrapper, or hidden “best starter” catalog, but a thin `cargo bootstrap` / `bootstrap-pack/v0` layer that preserves lane choice, starter realization, environment realization, and downstream imports as separate truths
- Hygiene: refreshed the active frontier and amnesia guidance so future revisions do not collapse recommendation, generated working tree, local environment, and later support/policy conclusions into one fake starter verdict

## 2026-03-21 — Project Bootstrap Stack (turn recommendation into a reviewable repo + realized environment)
- Re-read the latest archive and deliberately looked for the next seam that was both strategically live and still underdesigned. The archive already had strong notes for adoption decisions, starter repos, and workspace environments, but it still lacked the explicit bridge that turns a lane recommendation into a first reviewable Rust project without flattening all of those layers together.
- Fresh research kept pointing toward the same gap. Rust’s 2025 vision work says the ecosystem still needs better crate navigation and clearer advice on a good starter set; the 2025 State of Rust survey says docs remain canonical while more learning/navigation is mediated by editors and LLM-like workflows; Cargo’s 1.94 development cycle keeps plugin seams and workspace/config discovery live; and Rust’s 2026 goals continue to push higher-level workflows like `cargo script`, public/private dependency control, and SBOM-adjacent work.
- Archive decision: add `design/project-bootstrap-stack.md`; update `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, `RESEARCH_LOG.md`, `AGENTS.md`, `meta/ACTIVE_FRONTIER.md`, and `meta/AMNESIA_RESISTORS.md`; mirror changed files into `archive/`; regenerate `meta/ARCHIVE_MANIFEST.md`; and keep the next worthy move framed as a **thin bootstrap composition layer** rather than a new universal generator.
- Sources: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/ ; https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/ ; https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/ ; https://rust-lang.github.io/rust-project-goals/2026/flagships.html ; https://doc.rust-lang.org/cargo/commands/cargo-new.html ; https://docs.rs/crate/cargo-generate/latest

- New design note: `design/ecosystem-priority-ladder-2026.md`
- New meta note: `meta/ACTIVE_FRONTIER.md`
- Frontier/priority refresh: promoted an explicit **2026 ecosystem priority ladder** so the archive now ranks **Build-State Evidence + Adoption Decision + Canonical Learning + Package Admission + Workspace Environment** as the default cross-cutting frontier band ahead of most narrower domain kits unless official motion or multi-stack leverage justifies an exception
- Strategy: clarified that the deepest missing contribution in “ideal Rust” is increasingly not another one-off crate family but thin, reviewable control-plane layers that preserve evidence, freshness, and bounded handoffs across build/debug, ecosystem choice, learning, package review, and workspace/agent reality
- Hygiene: added `meta/ACTIVE_FRONTIER.md` so future revisions start from the ranked working set, keep control-plane epics distinct from substrate/domain kits, and avoid archive sprawl or accidental re-prioritization by drift

## 2026-03-21 — Ecosystem priority ladder (rank the control-plane epics before adding more narrow kits)
- Re-read the latest archive and deliberately checked whether the next honest move was yet another domain seam or a sharper synthesis above the existing stacks. The archive already had strong individual frontier notes, but it still lacked a compact, current, explicit ranking for **which worthy contributions actually deserve to be built first**.
- Fresh research pushed the answer toward a cross-cutting ladder rather than another narrow kit. The 2025 State of Rust survey says resource usage remains a major productivity problem, debugging remains high, and online docs remain canonical while learning behavior shifts toward LLM/editor mediation; the 2025 compiler-performance survey says rebuild latency, `cargo check`/`cargo build` duplication, editor latency, and lack of build explanations remain real blockers; Cargo’s current work keeps build analysis, build-dir layout, target-dir locking, workspace/config discovery, and cargo-script live; crates.io now exposes Security-tab, Trusted Publishing, SLOC, and `pubtime`; and Rust’s vision/Foundation/2026-goal work all point toward higher-level workflows, supply-chain clarity, and responsible adoption rather than “just add more crates”.
- Archive decision: add `design/ecosystem-priority-ladder-2026.md` and `meta/ACTIVE_FRONTIER.md`; prepend matching frontier notes in `INDEX.md`, `PRIORITIES.md`, `RESEARCH_LOG.md`, `STRATEGIC_FRONTIER.md`, and `AGENTS.md`; and strengthen `meta/AMNESIA_RESISTORS.md` so future revisions keep **control-plane epics, evidence substrates, and domain kits** distinct instead of letting fresh domain work silently outrank ecosystem-wide leverage.
- Sources: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/ ; https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/ ; https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html ; https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html ; https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/ ; https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/ ; https://blog.rust-lang.org/2026/01/21/crates-io-development-update/ ; https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/ ; https://rust-lang.github.io/rust-project-goals/2026/flagships.html ; https://rustfoundation.org/strategic-plan/ ; https://rustfoundation.org/media/annual-report-strategy-2025/

- New design notes: `design/vector-surface-lane-map.md`, `design/vector-surface-pilot-program.md`
- Design/gap/epic refresh: `design/vector-surface-kit.md`, `gaps/vector-surfaces-simd-target-features-and-dispatch-contracts.md`, `proposals/epic-vector-surface-kit.md`
- Frontier/priority refresh: sharpened **Vector Surface Kit** so the archive now treats **portable-fixed-width + target-specific/compile-time + runtime-multiversioned + fallback-backed + scalable-vector/experimental + adapter/consumer-import + target/layout/semantic evidence** as distinct but connected review lanes instead of one fake “SIMD support” verdict
- Strategy: clarified that the worthy contribution here is not another intrinsic wrapper, benchmark badge, or universal SIMD facade, but a thin `cargo vectorsurf` / `vector-pack/v0` layer whose lane catalog, target-feature and dispatch/fallback profiles, alignment/semantic reports, and bounded downstream handoffs let Rust teams compare vector claims honestly
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future vector/scientific/media/crypto/offload revisions keep portable SIMD, target-specific compile-time lanes, runtime multiversioning, fallback-backed lanes, scalable-vector experiments, adapter/import posture, and target/layout/semantic evidence distinct instead of flattening them into one vector story

## 2026-03-21 — Vector Surface lane map and ranked pilot (portable SIMD, target features, dispatch, fallbacks, and scalable vectors)
- Re-read the latest archive and deliberately looked for a frontier seam that was already strategically important but still too flat to resist future revisions. **Vector Surface Kit** was the clearest fit: the archive already had the gap note, design note, and epic, but it still lacked the explicit lane map and ranked pilot that would stop portable fixed-width SIMD, target-specific compile-time intrinsics, runtime multiversioning, fallback-backed abstractions, scalable-vector experiments, and downstream consumer imports from collapsing into one fake “SIMD support” verdict.
- Fresh research confirmed the lane split is real rather than theoretical. Rust’s 2026 flagships keep **Sized Hierarchy and Scalable Vectors** active, including `const Sized`, scalable-vector RFC work, SVE types/intrinsics in `stdarch`, and early SME design; the 2025H1 SVE/SME goal still says SVE is unsupported today and explicitly warns against overfitting to one architecture; `std::simd` is portable across targets but still nightly-only and still documents subnormal-`f32` caveats on some older architectures; the Reference keeps `#[target_feature]` hazards explicit; `safe_arch`, `multiversion`, and `wide` each publish materially different current-tense lanes.
- Archive decision: add `design/vector-surface-lane-map.md` and `design/vector-surface-pilot-program.md`; refresh `design/vector-surface-kit.md`, `gaps/vector-surfaces-simd-target-features-and-dispatch-contracts.md`, and `proposals/epic-vector-surface-kit.md`; update `INDEX.md`, `PRIORITIES.md`, `RESEARCH_LOG.md`, `STRATEGIC_FRONTIER.md`, and `AGENTS.md`; and add a new amnesia resistor so future vector/scientific/media/crypto/offload revisions keep lane identity, target-feature posture, dispatch/fallback posture, alignment/layout truth, operation semantics, and evidence separate.
- Sources: https://rust-lang.github.io/rust-project-goals/2026/flagships.html ; https://rust-lang.github.io/rust-project-goals/2025h1/arm-sve-sme.html ; https://doc.rust-lang.org/std/simd/index.html ; https://doc.rust-lang.org/reference/attributes/codegen.html#the-target_feature-attribute ; https://docs.rs/safe_arch ; https://docs.rs/multiversion/latest/multiversion/ ; https://docs.rs/wide

- New design note: `design/tensor-surface-lane-map.md`
- Design/gap/epic refresh: `design/tensor-surface-kit.md`, `design/tensor-surface-pilot-program.md`, `design/scientific-productization-stack.md`, `design/scientific-productization-pilot-program.md`, `gaps/numerical-array-tensor-surfaces-and-interop-contracts.md`, `proposals/epic-tensor-surface-kit.md`
- Frontier/priority refresh: sharpened **Tensor Surface Kit** so the archive now treats **dense-array + matrix/linalg + runtime-tensor/device + persisted-array + interchange/attachment + adapter/consumer-import** as distinct but connected review lanes instead of one fake “tensor support” verdict
- Strategy: clarified that the worthy contribution here is not another ndarray competitor, universal array trait, or numerical mega-runtime, but a thin `cargo tensorcheck` / `tensor-pack/v0` layer whose lane catalog, shape/layout/ownership/device/storage profiles, exact-vs-copy-vs-lossy adapter reports, and bounded downstream handoffs let Rust teams compare numerical-surface claims honestly
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future tensor/scientific/model/offload/dataset revisions keep array lanes, matrix lanes, runtime-tensor lanes, persisted-array lanes, interchange lanes, and consumer-import conclusions distinct instead of flattening them into one numerical story

## 2026-03-21 — Tensor Surface lane map (dense arrays, matrices, runtime tensors, persisted arrays, interchange, and adapters)
- Re-read the latest archive and deliberately looked for a frontier seam that was already strategically important but still too flat to resist future revisions. **Tensor Surface Kit** was the clearest fit: the archive already had the gap note, design note, pilot, epic, and the wider Scientific Productization stack, but it still lacked the explicit lane map that would stop dense arrays, matrix vocabularies, runtime tensors, persisted multidimensional arrays, interchange structures, and adapter/import consumers from collapsing into one fake “tensor support” verdict.
- Fresh research confirmed the lane split is real rather than theoretical. `ndarray` still centers `ArrayBase`, owned arrays, views, and raw-storage vocabulary; `nalgebra` and `faer` still represent distinct matrix/linalg families; Candle and Burn keep runtime/device/autodiff posture concrete; `zarrs` keeps stored-array metadata/conformance concrete; DLPack and the Array API interchange discussion keep conversion/device/layout requirements concrete; and `argmin-math` still bridges `Vec`, `ndarray`, `nalgebra`, and `faer` rather than assuming one numerical winner.
- Archive decision: add `design/tensor-surface-lane-map.md`; refresh `design/tensor-surface-kit.md`, `design/tensor-surface-pilot-program.md`, `design/scientific-productization-stack.md`, `design/scientific-productization-pilot-program.md`, `gaps/numerical-array-tensor-surfaces-and-interop-contracts.md`, and `proposals/epic-tensor-surface-kit.md`; update `INDEX.md`, `PRIORITIES.md`, `STRATEGIC_FRONTIER.md`, and `AGENTS.md`; and add a new amnesia resistor so future tensor/scientific revisions keep lane identity separate from cross-cutting shape/layout/ownership/device/storage evidence.
- Sources: https://docs.rs/ndarray/latest/ndarray/struct.ArrayBase.html ; https://docs.rs/ndarray/latest/ndarray/trait.RawData.html ; https://www.nalgebra.rs/docs/user_guide/vectors_and_matrices/ ; https://docs.rs/faer/latest/faer/ ; https://docs.rs/candle-core/latest/candle_core/enum.Device.html ; https://docs.rs/burn-tensor ; https://docs.rs/burn-store ; https://docs.rs/zarrs/latest/zarrs/ ; https://docs.rs/zarrs/latest/zarrs/array/struct.Array.html ; https://docs.rs/argmin-math/ ; https://docs.rs/dlpark/latest/dlpark/traits/index.html ; https://data-apis.org/array-api/2024.12/design_topics/data_interchange.html ; https://data-apis.org/blog/array_api_v2024_release/

## New (rev0350)
- New design note: `design/dataflow-surface-lane-map.md`
- Design/gap/epic refresh: `design/dataflow-surface-kit.md`, `design/dataflow-surface-pilot-program.md`, `gaps/streaming-dataflows-sources-time-state-materialization-and-progress-contracts.md`, `proposals/epic-dataflow-surface-kit.md`
- Frontier/priority refresh: sharpened **Dataflow Surface Kit** so the archive now treats **SQL-planned/relational-stream + connector-programmable/inline-transform + custom graph/progress-replay + streaming-database/materialized-serving + source-boundary + temporal-semantics + state/checkpoint/recovery + materialization/progress + consumer-import** as distinct but connected review lanes instead of one fake “streaming support” or “real-time readiness” verdict
- Strategy: clarified that the worthy contribution here is not another engine, connector marketplace, control plane, or maturity score, but a thin `cargo dataflowcheck` / `dataflow-pack/v0` layer whose lane catalog, source/time/state/materialization profiles, progress evidence attachments, diffs, and bounded consumer summaries let Rust teams compare dataflow claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future dataflow/event/dataset/runtime/observability revisions keep engine-family lanes, source/sink posture, temporal semantics, state/backfill/recovery posture, materialization/progress evidence, and downstream consumer imports distinct instead of flattening them into one streaming story

## New (rev0349)
- New design notes: `design/trait-surface-lane-map.md`, `design/trait-surface-pilot-program.md`
- Design/gap/epic refresh: `design/trait-surface-kit.md`, `gaps/trait-surfaces-dyn-posture-return-shapes-and-impl-truth.md`, `proposals/epic-trait-surface-kit.md`
- Frontier/priority refresh: sharpened **Trait Surface Kit** so the archive now treats **ordinary static/named-return + native dyn-compatible/object-safe + opaque-return/RTN-bound + native async/RPITIT non-dyn + dyn-via-adapter/boxed-erased + split/local-send/evolving-family + blanket/extension coverage + solver-sensitive acceptance/watch** as distinct but connected review lanes instead of one fake “trait support” or “dyn support” verdict
- Strategy: clarified that the worthy contribution here is not another trait-helper macro, dyn-safety badge, or universal metadata blob, but a thin `cargo traitsurf` / `trait-pack/v0` layer whose lane catalog, return-shape profiles, dyn/adaptation reports, family-migration notes, impl-coverage records, and solver-watch vectors let Rust teams compare trait claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future trait/async/pointer/lending/borrowing revisions keep native dyn posture, opaque-return obligations, adapter dyn posture, family splits, blanket coverage, and solver-sensitive acceptance distinct instead of flattening them into one trait story

## New (rev0348)
- New design notes: `design/initialization-surface-lane-map.md`, `design/initialization-surface-pilot-program.md`
- Design/gap/epic refresh: `design/initialization-surface-kit.md`, `gaps/initialization-surfaces-in-place-construction-and-destruction-contracts.md`, `proposals/epic-initialization-surface-kit.md`
- Frontier/priority refresh: sharpened **Initialization Surface Kit** so the archive now treats **ordinary constructor/builder + caller-allocated out-pointer/uninit + construct-then-pin + pinned-in-place/fallible assembly + cyclic/weak-self bootstrap + unique-to-shared publication + self-referential/borrow-carrying + foreign-emplace/destructor-coupled** as distinct but connected review lanes instead of one fake “constructor support” or “in-place init” verdict
- Strategy: clarified that the worthy contribution here is not another constructor macro, universal builder trait, or placement-new slogan crate, but a thin `cargo initsurf` / `init-pack/v0` layer whose lane catalog, phase maps, exposure-timing reports, rollback vectors, adapter-lossiness records, and teardown/guaranteed-destructor posture let Rust teams compare initialization claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future initialization/borrowing/interop revisions keep storage origin, address-stability timing, staged assembly, publication transitions, internal-borrow exposure, and teardown guarantees distinct instead of flattening them into one init story

## New (rev0347)
- New design note: `design/canonical-learning-lane-map.md`
- Design/gap/stack/epic refresh: `design/canonical-learning-stack.md`, `design/canonical-learning-pilot-program.md`, `design/canonical-learning-consumer-pilot-program.md`, `gaps/canonical-learning-maintainer-authored-teaching-and-derived-consumer-boundaries.md`, `proposals/epic-canonical-learning-stack.md`
- Frontier/priority refresh: sharpened **Canonical Learning Stack** so the archive now treats **api-doc/reference + guide/tutorial + executable-example proof + compile-guidance/negative-teaching + docs-host/build posture + structured machine-import + derived consumer overlays + review/handoff imports** as distinct but connected review lanes instead of one fake “docs quality” or “smart docs” verdict
- Strategy: clarified that the worthy contribution here is not another docs portal, AI-context blob, or documentation score, but a thin `cargo learncanon` / `canonical-learning-pack/v0` layer whose lane catalog, canonical source index, check reports, import reports, authority boundaries, and bounded consumer handoffs let Rust teams compare learning claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future docs/guidance/semantic-context/editor/assistant revisions keep authored canon, executable proof, docs-host posture, structured imports, derived overlays, and release/support handoffs distinct instead of flattening them into one learning verdict

## New (rev0346)
- New design note: `design/async-commons-lane-map.md`
- New gap note: `gaps/async-runtime-neutrality-and-capability-profiles.md`
- Design/gap/stack/epic refresh: `design/async-commons-kit.md`, `design/async-commons-pilot-program.md`, `design/async-lifecycle-kit.md`, `design/async-reliability-stack.md`, `proposals/epic-async-commons-kit.md`
- Frontier/priority refresh: sharpened **Async Commons Kit** so the archive now treats **core-future/poll substrate + spawn/executor capability + local-`!Send` placement + I/O trait/adapter truth + time/deadline capability + stream/watch posture + environment family + bounded consumer imports** as distinct but connected review lanes instead of one fake “runtime agnostic” verdict
- Strategy: clarified that the worthy contribution here is not another runtime wrapper, portability badge, or universal async facade, but a thin `cargo async-commons` / `async-commons-pack/v0` layer whose lane profiles, capability declarations, adapter-lossiness reports, readiness classes, and bounded consumer views let Rust teams compare async claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future async/lifecycle/reliability/adoption revisions keep shared substrate, runtime-shaped APIs, local-vs-`Send` posture, adapter lossiness, environment families, and downstream lifecycle claims distinct instead of flattening them into one portability score

## New (rev0345)
- New design note: `design/maintenance-reality-lane-map.md`
- Design/gap/stack/epic refresh: `design/maintenance-reality-stack.md`, `design/stewardship-pilot-program.md`, `gaps/maintenance-operations-and-stewardship-queues.md`, `proposals/epic-maintenance-reality-stack.md`
- Frontier/priority refresh: sharpened **Maintenance Reality Stack** so the archive now treats **lifecycle intent + workflow policy + observed state + derived pressure findings + help-routing + mentoring capacity + visibility posture + bounded consumer handoffs** as distinct but connected review lanes instead of one fake “maintainer health” verdict
- Strategy: clarified that the worthy contribution here is not another dashboard, score, or hidden funding oracle, but a thin `cargo maintenance-reality` / `maintenance-reality-pack/v0` layer whose lane-aware imports, briefs, routing profiles, and bounded consumer views let Rust teams compare stewardship claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future maintenance/lifecycle/keystone/support revisions keep lifecycle declarations, workflow policy, observed operations, derived findings, support routing, mentoring promises, visibility posture, and consumer handoffs distinct instead of flattening them into one health score

## New (rev0344)
- New design note: `design/compatibility-claims-lane-map.md`
- Design/gap/stack/epic refresh: `design/support-envelope-kit.md`, `design/compatibility-claims-stack.md`, `design/compatibility-claims-pilot-program.md`, `gaps/compatibility-claims-platform-debugger-and-acceptance-contracts.md`, `proposals/epic-compatibility-claims-stack.md`
- Frontier/priority refresh: sharpened **Compatibility Claims Stack** so the archive now treats **dev-host + source-build + release-artifact + docs-surface + runtime-floor + debugger-tuple + acceptance-profile + bounded consumer views** as distinct but connected review lanes instead of one fake “supported” verdict
- Strategy: clarified that the worthy contribution here is not another matrix page, badge, or UI-test wrapper, but a thin `cargo compat` / `compat-pack/v0` layer whose lane catalogs, imported claim registers, diffs, and bounded summaries let Rust teams compare compatibility claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future compatibility/support/debugger/acceptance revisions keep host/build/release/docs/runtime/debugger/acceptance lanes distinct instead of flattening them into one compatibility score

## New (rev0343)
- New design note: `design/trust-decision-lane-map.md`
- Design/gap/stack/epic refresh: `design/trust-signals-kit.md`, `design/trust-signals-pilot-program.md`, `design/trust-decision-stack.md`, `design/trust-decision-pilot-program.md`, `gaps/crate-trust-signals.md`, `gaps/trust-decisions-evidence-policy-handoff-and-thin-views.md`, `proposals/epic-trust-signals-kit.md`, `proposals/epic-trust-decision-stack.md`
- Frontier/priority refresh: sharpened **Trust Signals Kit / Trust Decision Stack** so the archive now treats **registry discovery + advisory feeds + audit attestations + graph-policy lint + artifact recovery + local decisions/waivers + thin consumer views** as distinct but connected review lanes instead of one fake crate-trust bucket
- Strategy: clarified that the worthy contribution here is not another score, scanner wrapper, or registry badge, but a thin `cargo trust` / `cargo trust-decision` layer whose lane profiles, evidence imports, decision packs, and bounded consumer views let Rust teams compare dependency-trust claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future trust/policy/admission/dependency-review revisions keep registry facts, RustSec advisories, cargo-vet attestations, cargo-deny graph-policy lints, artifact recovery, and local decisions distinct instead of flattening them into one trust verdict


## New (rev0342)
- New design notes: `design/repro-build-lane-map.md`, `design/repro-build-pilot-program.md`
- Design/gap/stack/epic refresh: `design/repro-build-kit.md`, `design/release-truth-stack.md`, `gaps/reproducible-build-verification-and-diffable-attestations.md`, `proposals/epic-repro-build-kit.md`
- Frontier/priority refresh: sharpened **Repro Build Kit / Release Truth Stack** so the archive now treats **source-package reproducibility + final-artifact compare modes + provenance attestation + SBOM-attestation attachment + offline-verification bundles + lifecycle posture** as distinct but connected review lanes instead of one fake reproducible-release bucket
- Strategy: clarified that the worthy contribution here is not another provenance badge, release wrapper, or generic hermetic-build recipe, but a thin `cargo repro` / `repro-pack/v0` layer whose lane profiles, compare reports, attestation refs, offline bundles, and bounded handoffs let Rust teams compare rebuild claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future release/repro/inventory/distribution revisions keep package reproducibility, artifact equivalence, provenance, inventory attestation, offline verification, and lifecycle posture distinct instead of flattening them into one trust verdict


- New design note: `design/sbom-evidence-lane-map.md`
- Design/gap/stack/epic refresh: `design/sbom-evidence-kit.md`, `design/inventory-evidence-stack.md`, `design/inventory-evidence-pilot-program.md`, `gaps/sbom-evidence-and-artifact-linked-dependency-inventory.md`, `proposals/epic-sbom-evidence-kit.md`, `proposals/epic-inventory-evidence-stack.md`
- Frontier/priority refresh: sharpened **SBOM Evidence Kit / Inventory Evidence Stack** so the archive now treats **Cargo-native precursors + source-project exports + embedded binary recovery + release-attached standards documents + scanner/import views + downstream consumer handoffs** as distinct but connected review lanes instead of one fake SBOM-support bucket
- Strategy: clarified that the worthy contribution here is not another exporter wrapper, registry badge, or one-file compliance story, but a thin `cargo inventory` / `inventory-pack/v0` layer whose lane reports, artifact-link reports, projection-lossiness records, recovery imports, and bounded downstream handoffs let Rust teams compare inventory claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future SBOM/release/scanner/policy revisions keep Cargo-native precursor truth, source-project export truth, embedded binary recovery, release attachments, scanner/import results, and downstream verdicts distinct instead of flattening them into one inventory verdict

## New (rev0340)
- New design notes: `design/build-cache-lane-map.md`, `design/build-cache-pilot-program.md`
- Design/gap/epic refresh: `design/build-cache-kit.md`, `gaps/userwide-build-cache.md`, `proposals/epic-build-cache-kit.md`
- Frontier/priority refresh: sharpened **Build Cache Kit** so the archive now treats **Cargo-native workspace-local state + editor-private duplication + Cargo-native user-wide intermediates + compiler-wrapper caches + container recipe/layer caching + CI/plugin exchange** as distinct but connected review lanes instead of one fake build-cache bucket
- Strategy: clarified that the worthy contribution here is not another cache daemon, wrapper score, Dockerfile generator, or one-number hit dashboard, but a thin `cargo cache` / `build-state-pack/v0` layer whose lane reports, lock explanations, reuse verdicts, and bounded imports let Rust teams compare build-cache claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future build-cache/build-state/tooling revisions keep Cargo-native state, wrapper caches, editor duplication, container layers, and CI/plugin exchange distinct instead of flattening them into one cache verdict


## New (rev0339)
- New design note: `design/manifest-surface-lane-map.md`
- Design/gap/stack/epic refresh: `design/manifest-surface-kit.md`, `design/manifest-truth-stack.md`, `design/manifest-truth-pilot-program.md`, `gaps/manifest-truth-authored-published-and-consumed.md`, `proposals/epic-manifest-truth-stack.md`
- Frontier/priority refresh: sharpened **Manifest Truth Stack** so the archive now treats **authored package manifests + inherited/defaulted/discovered interpretation + packaged publish-normalized manifests + script/frontmatter subjects + machine-consumer imports + human projections + evolving schema/watch lanes** as distinct but connected review lanes instead of one fake “the manifest” story
- Strategy: clarified that the worthy contribution here is not another formatter, editor shell, registry page, or `cargo metadata` wrapper, but a thin `cargo manifest` / `manifest-pack/v0` layer whose lane reports, publish diffs, consumer-lossiness records, and bounded downstream handoffs let Rust teams compare manifest claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future manifest/repo-composition/script/publish revisions keep authored text, inherited meaning, packaged truth, script subjects, and consumer projections distinct instead of flattening them into one manifest verdict


## New (rev0338)
- New design notes: `design/filesystem-surface-lane-map.md`, `design/filesystem-surface-pilot-program.md`
- Design/gap/epic refresh: `design/filesystem-surface-kit.md`, `gaps/filesystem-surfaces-paths-traversal-and-durable-mutation-contracts.md`, `proposals/epic-filesystem-surface-kit.md`
- Frontier/priority refresh: sharpened **Filesystem Surface Kit** so the archive now treats **bare-path std I/O + UTF-8 paths + rooted/capability resolution + canonical/display bridges + traversal + watch + staged mutation + durable replace + trust/privacy checks** as distinct but connected review lanes instead of one fake filesystem-support bucket
- Strategy: clarified that the worthy contribution here is not another path helper, watcher wrapper, virtual filesystem, or “safe save” facade, but a thin `cargo fscheck` / `fs-pack/v0` layer whose lane profiles, vector reports, fixture attachments, and bounded downstream handoffs let Rust teams compare filesystem claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future filesystem/runtime-settings/command/security revisions keep path kind, rooted authority, canonical-vs-display form, traversal policy, watch backend, temp staging, durability guarantees, and trust/privacy checks distinct instead of flattening them into one filesystem verdict

## New (rev0337)
- New design note: `design/benchmark-evidence-lane-map.md`
- Design/gap/epic refresh: `design/benchmark-evidence-kit.md`, `design/benchmark-evidence-pilot-program.md`, `gaps/benchmark-evidence-subjects-lanes-baselines-and-imports.md`, `proposals/epic-benchmark-evidence-kit.md`
- Frontier/priority refresh: sharpened **Benchmark Evidence Kit** so the archive now treats **cargo-bench foundations + Criterion-native statistical baselines + Divan-style counter lanes + nextest runner imports + Iai-Callgrind deterministic profiler lanes + hosted adapter modes** as distinct but connected review lanes instead of one fake benchmark-support bucket
- Strategy: clarified that the worthy contribution here is not another benchmark harness, hosted dashboard wrapper, or one-number performance badge, but a thin `cargo benchpack` / `benchmark-pack/v0` layer whose lane profiles, baseline imports, runner imports, raw attachments, and bounded Perf Labs handoffs let Rust teams compare benchmark claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future benchmark/perf revisions keep Cargo launch truth, engine semantics, baseline provenance, runner lossiness, metric-family identity, and hosted-adapter posture distinct instead of flattening them into one benchmark verdict

## New (rev0336)
- New design note: `design/device-lab-lane-map.md`
- Design/gap/epic refresh: `design/device-lab-kit.md`, `design/device-lab-pilot-program.md`, `gaps/embedded-device-labs-and-hardware-in-the-loop.md`, `proposals/epic-device-lab-kit.md`
- Frontier/priority refresh: sharpened **Device Lab Kit** so the archive now treats **attach/smoke + per-test-reset harnesses + native capture transports + target-enablement posture + shared-lab quarantine/operations + firmware-consumer imports** as distinct but connected review lanes instead of one fake hardware-tested bucket
- Strategy: clarified that the worthy contribution here is not another board template, runner wrapper, or hosted board-farm control plane, but a thin `cargo devicelab` / `lab-pack/v0` layer whose lane profiles, board/lab manifests, native capture imports, and bounded downstream handoffs let Rust teams compare physical-target evidence honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future device-lab/testing/firmware revisions keep board identity, run lane, target-enablement posture, native capture, shared-lab state, normalized reports, and support/release conclusions distinct instead of flattening them into one hardware-success verdict
## New (rev0335)
- New design note: `design/sanitizer-battery-lane-map.md`
- Design/gap/epic refresh: `design/sanitizer-battery-kit.md`, `design/sanitizer-battery-pilot-program.md`, `gaps/sanitizers-and-dynamic-analysis.md`, `proposals/epic-sanitizer-battery-kit.md`
- Frontier/priority refresh: sharpened **Sanitizer Battery Kit** so the archive now treats **Miri isolated interpreter + Miri runner-import + `cargo-careful` native checking + LLVM sanitizer finding + mitigation/hardening + Borrow/aliasing watch-import** as distinct but connected review lanes instead of one fake runtime-checking bucket
- Strategy: clarified that the worthy contribution here is not another “run all checks” wrapper, badge, or dashboard, but a thin `cargo sanitize` / `sanitize-pack/v0` layer whose lane profiles, execution imports, runtime/sysroot provenance, finding-or-mitigation posture, and bounded downstream handoffs let Rust teams compare dynamic-analysis claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future sanitizer/safety/toolchain revisions keep interpreter/native/runner/mitigation/aliasing differences distinct instead of flattening them into one battery-success score
## New (rev0334)
- New design note: `design/coverage-evidence-lane-map.md`
- Design/gap/epic refresh: `design/coverage-evidence-kit.md`, `design/coverage-evidence-pilot-program.md`, `gaps/coverage-evidence-and-ci-review.md`, `proposals/epic-coverage-evidence-kit.md`
- Frontier/priority refresh: sharpened **Coverage Evidence Kit** so the archive now treats **official LLVM baseline coverage + Cargo-native LLVM orchestration + nextest/doctest merge + external/FFI imports + Tarpaulin contrast + future decision/MC/DC watch/import posture** as distinct but connected review lanes instead of one fake coverage-support bucket
- Strategy: clarified that the worthy contribution here is not another coverage engine, hosted percentage service, or badge normalizer, but a thin `cargo cov` / `coverage-pack/v0` layer whose lane profiles, criterion profiles, execution imports, merge reports, and bounded downstream handoffs let Rust teams compare coverage claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future coverage/safety/testing revisions keep criterion, engine, execution import, merge comparability, FFI/native inclusion, and decision/MC/DC watch posture distinct instead of flattening them into one coverage-success score
## New (rev0333)
- New design note: `design/observability-lane-map.md`
- Design/stack/gap/epic refresh: `design/observability-kit.md`, `design/observability-productization-stack.md`, `design/observability-productization-pilot-program.md`, `gaps/observability-interop-and-telemetry-contracts.md`, `proposals/epic-observability-kit.md`
- Frontier/priority refresh: sharpened **Observability Kit** so the archive now treats **structured tracing composition + local formatted diagnostics + `log`-bridge posture + metrics-facade posture + OpenTelemetry export/profile posture + runtime-diagnostic posture + imported machine-report posture** as distinct but connected review lanes instead of one fake observability-support bucket
- Strategy: clarified that the worthy contribution here is not another exporter helper, backend bootstrap crate, or one-true telemetry wrapper, but a thin `cargo obs` / `obs-pack/v0` layer whose lane profiles, activation reports, vector reports, and bounded consumer handoffs let downstream tools compare Rust observability claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future observability/debuggability/service/support revisions keep local output, tracing composition, legacy-log import, metrics, OTLP/exporter profile, runtime diagnostics, and imported Cargo/build reports distinct instead of flattening them into one observability-success score
## New (rev0332)
- New design notes: `design/consumer-install-lane-map.md`, `design/consumer-install-pilot-program.md`
- Design/gap/epic refresh: `design/consumer-install-kit.md`, `gaps/consumer-install-selection-channels-mirrors-and-receipts.md`, `proposals/epic-consumer-install-kit.md`
- Frontier/priority refresh: sharpened **Consumer Install Kit** so the archive now treats **source-build installs + prebuilt installs + mirror/host fallback + CI-wrapper installs + delegated/imported installs + durable receipt/managed-content claims** as distinct but connected review lanes instead of one fake install-support bucket
- Strategy: clarified that the worthy contribution here is not another installer script, package-manager shim, or speed-focused bootstrapper, but a thin `cargo installproof` / `install-pack/v0` layer whose lane profiles, candidate catalogs, plan/receipt reports, and bounded handoffs let downstream tools compare Rust first-install behavior honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future install/distribution/update/support revisions keep requested subject, visible candidates, chosen plan, selected source, verification posture, receipt/mutation, and managed-content claims distinct instead of flattening them into one install-success score

## New (rev0331)
- New design notes: `design/database-contract-lane-map.md`, `design/database-contract-pilot-program.md`
- Design/stack/gap/epic refresh: `design/database-contract-kit.md`, `design/data-productization-stack.md`, `gaps/database-schema-query-and-migration-contracts.md`, `proposals/epic-database-contract-kit.md`
- Frontier/priority refresh: sharpened **Database Contract Kit** so the archive now treats **backend-authority posture, checked-query evidence, dynamic-query evidence, schema-as-code/entity lanes, migration-source lanes, embedded-shipping lanes, and validation-environment receipts** as distinct but connected review lanes instead of one fake database-support bucket
- Strategy: clarified that the worthy contribution here is not another ORM, migration generator, query-builder bake-off, or hosted schema control plane, but a thin `cargo dbcheck` / `db-pack/v0` layer whose lane profiles, adapter reports, environment receipts, and bounded consumer handoffs let downstream tools compare Rust relational-database claims honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future database/data-product revisions keep backend authority, checked-query evidence, dynamic-query evidence, schema source, migration execution, embedded shipping, and validation-environment receipts distinct instead of flattening them into one database-readiness score

## New (rev0330)
- New design note: `design/toolchain-productization-lane-map.md`
- Design/gap/epic refresh: `design/toolchain-productization-stack.md`, `design/toolchain-productization-pilot-program.md`, `design/sysroot-pack-kit.md`, `gaps/toolchain-variants-sysroots-cross-builds-and-sanitizer-support-contracts.md`, `proposals/epic-toolchain-productization-stack.md`
- Frontier/priority refresh: sharpened **Toolchain Productization Stack** so the archive now treats **stock rustup toolchains + local build-std rebuilds + reusable sysroot packs + compiler-pinned custom-target lanes + activation/host-target split rules + instrumented/hardened runtime families + external-build handoff** as distinct but connected review lanes instead of one fake custom-toolchain bucket
- Strategy: clarified that the worthy contribution here is not another cross-build wrapper, org-local cache, or `build-std` convenience layer, but a thin `cargo toolchaincheck` / `toolchain-product-pack/v0` layer whose lane profiles, activation reports, reuse policies, and bounded consumer handoffs let downstream tools compare Rust toolchain variants honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future toolchain/sysroot/sanitizer/support revisions keep provisioning, rebuilt-stdlib identity, activation, custom-target coupling, runtime-family claims, and external handoff conclusions distinct instead of flattening them into one toolchain-success score

## New (rev0329)
- New design notes: `design/update-continuity-lane-map.md`, `design/update-continuity-pilot-program.md`
- Design/gap/epic refresh: `design/update-continuity-kit.md`, `gaps/update-continuity-detection-selection-apply-rollback-and-uninstall.md`, `proposals/epic-update-continuity-kit.md`
- Frontier/priority refresh: sharpened **Update Continuity Kit** so the archive now treats **source-installed tool updates + prebuilt reinstall flows + receipt-driven updater lanes + bundle/app updater lanes + delegated-manager posture + ownership/rollback/uninstall truth + forensic/imported handoff** as distinct but connected review lanes instead of one fake update-support bucket
- Strategy: clarified that the worthy contribution here is not another self-update crate, release-feed service, or updater dashboard, but a thin `cargo update-continuity` / `update-pack/v0` layer whose lane profiles, plan/apply/ownership reports, and bounded handoffs let downstream tools compare Rust update behavior honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future update/install/support revisions keep installed subject, candidate visibility, check/plan, apply result, delegation, and ownership/uninstall conclusions distinct instead of flattening them into one update-success score

## New (rev0328)
- New design notes: `design/publish-set-lane-map.md`, `design/publish-set-pilot-program.md`
- Design/gap/epic refresh: `design/publish-set-kit.md`, `gaps/publish-sets-package-selection-contents-verification-and-registry-receipts.md`, `proposals/epic-publish-set-kit.md`
- Frontier/priority refresh: sharpened **Publish Set Kit** so the archive now treats **single-package direct publish + workspace publish sets + alternative-registry/credential-provider posture + trusted-publishing/OIDC posture + check/waiver lanes + upload/index/`pubtime` receipts + forensic/imported handoff** as distinct but connected review lanes instead of one fake publish-support bucket
- Strategy: clarified that the worthy contribution here is not another release bot, trusted-publishing badge, or registry dashboard, but a thin `cargo publish-set` / `publish-pack/v0` layer whose lane profiles, payload/check/receipt reports, and bounded handoffs let downstream tools compare Rust source-package publication honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future publish/release/package-admission revisions keep subject, payload, authority path, checks, receipts, and downstream verdicts distinct instead of flattening them into one publish-success score

## New (rev0327)
- New design notes: `design/time-surface-lane-map.md`, `design/time-surface-pilot-program.md`
- Design/gap/epic refresh: `design/time-surface-kit.md`, `gaps/time-surfaces-clocks-time-zones-and-calendrical-contracts.md`, `proposals/epic-time-surface-kit.md`
- Frontier/priority refresh: sharpened **Time Surface Kit** so the archive now treats **monotonic elapsed/timeout clocks, wall-clock/external timestamps, civil/offset forms, zoned DST-aware values, localized calendar/locale rendering, storage/migration adapters, and deterministic fake-clock lanes** as distinct but connected review lanes instead of one fake datetime-support bucket
- Strategy: clarified that the worthy contribution here is not another datetime crate, formatting DSL, or migration bake-off, but a thin `cargo timesurf` / `time-pack/v0` layer whose lane profiles, adapter reports, vector reports, and consumer handoffs let downstream tools compare temporal behavior honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future time/background-work/localization revisions keep clock, zone, locale, storage, and fake-clock claims distinct instead of flattening them into one temporal score

## New (rev0326)
- New design notes: `design/terminal-surface-lane-map.md`, `design/terminal-surface-pilot-program.md`
- Design/gap/epic refresh: `design/terminal-surface-kit.md`, `gaps/terminal-surfaces-capabilities-input-and-render-contracts.md`, `proposals/epic-terminal-surface-kit.md`
- Frontier/priority refresh: sharpened **Terminal Surface Kit** so the archive now treats **styled output/color policy, full-screen TUI, interactive line editing, capability/probing stacks, parser/test backends, and graphics protocols** as distinct but connected review lanes instead of one fake terminal-support bucket
- Strategy: clarified that the worthy contribution here is not another backend facade, style crate, or screenshot-heavy TUI showcase, but a thin `cargo termsurf` / `terminal-pack/v0` layer whose lane profiles, adapter reports, vector reports, and consumer handoffs let downstream tools compare terminal behavior honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future terminal/CLI/process revisions keep render/input/layout/probe/test/graphics claims distinct instead of flattening them into one terminal score

## New (rev0325)
- New design notes: `design/process-surface-lane-map.md`, `design/process-surface-pilot-program.md`
- Design/gap/epic refresh: `gaps/process-surfaces-subprocesses-pipelines-and-supervision-contracts.md`, `design/process-surface-kit.md`, `proposals/epic-process-surface-kit.md`
- Frontier/priority refresh: sharpened **Process Surface Kit** so the archive now treats **direct exec, shell-shaped composition, pipe topology, async child lifecycle/reaping, tree-control/concurrent-control wrappers, and PTY interaction** as distinct but connected review lanes instead of one fake “Command support” bucket
- Strategy: clarified that the worthy contribution here is not another shell helper, task runner, or universal supervisor, but a thin `cargo procsurf` / `process-pack/v0` layer whose lane profiles, adapter reports, vector reports, and consumer handoffs let downstream tools compare subprocess semantics honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future process/tooling revisions keep actual shell execution, shell-like DSLs, pipe topology, async lifecycle, tree control, and PTY interaction distinct instead of flattening them into one subprocess score

## New (rev0324)
- New design note: `design/semantic-context-lane-map.md`
- Design/epic refresh: `gaps/cross-crate-semantic-context-and-analysis-inputs.md`, `design/semantic-context-kit.md`, `design/semantic-context-pilot-program.md`, `proposals/epic-semantic-context-kit.md`
- Frontier/priority refresh: sharpened **Semantic Context Kit** so the archive now treats **local authoritative workspace capture, public docs.rs/release cache, local-versus-remote comparison, fix/lint semantic handoff, derived editor/assistant slices, and compiler-backed augmentation watch work** as distinct but connected review lanes instead of one fake universal semantic index
- Strategy: clarified that the worthy contribution here is not another hidden workspace graph, docs.rs mirror, or AI-context blob, but a thin `cargo semctx` / `semctx-pack/v0` layer whose lane profiles, merge reports, diff reports, and consumer handoffs let downstream tools compare semantic authority/freshness honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future semantic-context/edit/tooling revisions keep canonical capture, public cache, comparison posture, consumer power, and compiler-backed watch claims distinct instead of flattening them into one semantic-context score

## New (rev0323)
- New design note: `design/pointer-shared-ownership-lane-map.md`
- Frontier/priority refresh: sharpened the existing **Pointer Surface / Borrowing Frontier** band so the archive now treats **ordinary `Rc`, ordinary `Arc`, unique-to-shared construction, weakless borrowed-arc families, read-mostly publication layers, and language-watch ergonomic-ref-counting work** as distinct but connected review lanes instead of one fake “Arc ergonomics” bucket
- Strategy: clarified that the worthy contribution here is not another Arc clone, closure-capture helper, or universal shared-ownership trait, but a thin `cargo pointer` / `pointer-pack/v0` layer whose shared-ownership branch can export lane-family truth, weak/unique/post-publication semantics, transition lossiness, and bounded async/native/initialization handoffs honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future pointer/async revisions keep syntax ergonomics, pointer semantics, unique-to-shared construction, borrowed/layout-specialized arc forms, and publication/storage layers distinct instead of flattening them into one ref-counting score

## New (rev0322)
- New design note: `design/python-host-lane-map.md`
- Frontier/priority refresh: sharpened the existing **Host Package / Polyglot** band so the archive now treats **full-API CPython extensions, `abi3` limited-API extensions, free-threaded Python, `asyncio` bridge posture, packaging/link/test handoff, and embedding/CPython-upstream adjacency** as distinct but connected review lanes instead of one fake “PyO3 support” bucket
- Strategy: clarified that the worthy contribution here is not another PyO3 wrapper, Python mega-framework, or hidden package abstraction, but a thin `cargo hostpkg` / `hostpkg-pack/v0` layer whose Python branch can export lane-family truth, wheel/build posture, async/runtime posture, and bounded support handoffs honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future Python/polyglot revisions keep full-API, `abi3`, free-threaded ABI, async bridge, packaging/link/test, and embedding/CPython-upstream work distinct instead of flattening them into one Python-support score

## New (rev0321)
- New design note: `design/native-edge-cpp-lane-map.md`
- Frontier/priority refresh: sharpened the existing **Native Edge Stack** so the archive now treats **C ABI export/import, safe-common C++ bridge lanes, automated large-existing-codebase lanes, provider/link-plan truth, external-build handoff, and watch-worthy upstream interop motion** as distinct but connected review lanes instead of one fake “Rust/C++ support” bucket
- Strategy: clarified that the worthy contribution here is not another bridge bake-off, provider helper, or build-system wrapper, but a thin `cargo native-edge` / `native-edge-pack/v0` layer whose `lane-profile`, boundary/provenance packs, provider/link packs, handoff reports, and readiness reports let downstream consumers compare native-adoption lanes honestly
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future native-edge revisions keep C ABI, CXX-style safe-common bridges, autocxx-style automation, provider resolution, build-script reduction pressure, and foreign-build/package handoff distinct instead of flattening them into one interop score

## New (rev0320)
- New gap/design/proposal layer: `gaps/async-commons-runtime-capabilities-traits-and-portability-contracts.md`, `design/async-commons-kit.md`, `design/async-commons-pilot-program.md`, `proposals/epic-async-commons-kit.md`
- Frontier/priority refresh: promoted an explicit **Async Commons Kit** so the archive now treats **neutral async capability truth + shared trait/type seams + adapter lossiness + readiness/watch reports** as a missing lower-level boundary beneath Async Lifecycle / Async Reliability and beside Navigation + Commons instead of letting runtime lock-in get re-described separately by every service, library, and adoption note
- Strategy: clarified that the worthy contribution here is not another runtime, universal async facade, or “works on every runtime” badge, but a thin `cargo async-commons` / `async-commons-pack/v0` layer whose capability profiles, seam reports, and adapter vectors can tell downstream stacks what is genuinely portable, what is partial, and what is still blocked on language/compiler work
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future revisions do not flatten `std`/language async progress, neutral futures/stream/I/O vocabulary, runtime-shaped APIs, adapter costs, and downstream lifecycle/productization conclusions into one fake portability story

## New (rev0319)
- Cargo-report review-separation refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`, `fixtures/cargo-report-pack-kit/cargo-report-review-request.schema.json`, `fixtures/cargo-report-pack-kit/cargo-report-decision-witness.schema.json`, `fixtures/cargo-report-pack-kit/cargo-report-review-separation-receipt.schema.json`, `fixtures/cargo-report-pack-kit/cargo-report-taxonomy.json`, `fixtures/cargo-report-pack-kit/cargo-report-scenario-index.json`, `fixtures/cargo-report-pack-kit/cargo-report-review-gates.json`, `fixtures/cargo-report-pack-kit/cargo-report-hygiene-checks.json`, `fixtures/cargo-report-pack-kit/README.md`, `tools/check_cargo_report_pack_contract.py`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **manual-review carry as role-separated review truth** instead of letting requester-authored or same-actor review silently impersonate an independent checker for public/current/frozen/contradiction-carry claims
- Strategy: clarified that the worthy contribution here is still not another dashboard, raw-log mirror, or approval workflow app, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer whose stronger carries name proposer/reviewer/executor identity, review-separation class, compensating controls, and fallback-review expiry when independence is weak
- Hygiene: strengthened `AGENTS.md`, `meta/AMNESIA_RESISTORS.md`, the Cargo-report fixture taxonomy/scenario/gate spine, and `tools/check_cargo_report_pack_contract.py` so future revisions cannot claim stronger review-cleared carry without moving the review-separation receipt, the updated request/witness refs, and scenario coverage for both independent and self-review hold paths

## New (rev0318)
- Cargo-report review-head/rereview refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`, `fixtures/cargo-report-pack-kit/cargo-report-review-request.schema.json`, `fixtures/cargo-report-pack-kit/cargo-report-decision-witness.schema.json`, `fixtures/cargo-report-pack-kit/cargo-report-taxonomy.json`, `fixtures/cargo-report-pack-kit/cargo-report-scenario-index.json`, `fixtures/cargo-report-pack-kit/cargo-report-review-gates.json`, `fixtures/cargo-report-pack-kit/cargo-report-hygiene-checks.json`, `fixtures/cargo-report-pack-kit/README.md`, `tools/check_cargo_report_pack_contract.py`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **manual-review carries as head-scoped requests and head-scoped decisions** instead of letting approval on one retained pack/head silently slide onto a newer operational head
- Strategy: clarified that the worthy contribution here is still not another dashboard, raw-log mirror, or premature schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer whose stronger current/public/frozen/head carries stay bound to the exact reviewed head and reissue explicitly when the lineage tip moves
- Hygiene: strengthened `AGENTS.md`, `meta/AMNESIA_RESISTORS.md`, the Cargo-report fixture taxonomy/scenario/gate spine, and `tools/check_cargo_report_pack_contract.py` so future revisions cannot claim a manual review cleared the latest head unless the request named the expected head, the witness named the reviewed head, and stale-head/rereview coverage still passes the contract checks

## New (rev0317)
- Cargo-report review-request/decision-witness refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`, `fixtures/cargo-report-pack-kit/cargo-report-review-request.schema.json`, `fixtures/cargo-report-pack-kit/cargo-report-decision-witness.schema.json`, `fixtures/cargo-report-pack-kit/cargo-report-taxonomy.json`, `fixtures/cargo-report-pack-kit/cargo-report-scenario-index.json`, `fixtures/cargo-report-pack-kit/cargo-report-review-gates.json`, `fixtures/cargo-report-pack-kit/README.md`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **review requests + decision witnesses + safe-without-approval sentences + manual-carry basis refs** as part of the same raw-evidence seam instead of collapsing queued review and cleared approval into one status label
- Strategy: clarified that the worthy contribution here is still not another dashboard, raw-log mirror, or premature schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer whose manual-review carries remain explicit requests and explicit witnesses before stronger public/current/frozen reuse is allowed
- Hygiene: strengthened `AGENTS.md`, `meta/AMNESIA_RESISTORS.md`, and the Cargo-report fixtures so future revisions cannot claim manual review cleared a contradiction/promotion/currentness/compatibility carry without moving the request, the consulted basis refs, the resulting decision witness, and the matching scenario/gate coverage in the same revision

## New (rev0317)
- Cargo-report contract-hygiene refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`, `fixtures/cargo-report-pack-kit/cargo-report-hygiene-checks.json`, `fixtures/cargo-report-pack-kit/cargo-report-review-gates.json`, `fixtures/cargo-report-pack-kit/README.md`, `tools/check_cargo_report_pack_contract.py`, `tools/hygiene.py`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **machine-checked contract hygiene + schema/example validation + taxonomy/scenario/gate coherence checks** as part of the same raw-evidence seam instead of freezing portable meanings in files that can still drift apart silently
- Strategy: clarified that the worthy contribution here is still not another dashboard, raw-log mirror, or premature schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer whose portable meanings are not only explicit and fixture-backed but also mechanically checked before a revision is treated as complete
- Hygiene: strengthened `AGENTS.md`, `meta/AMNESIA_RESISTORS.md`, the Cargo-report fixture control surfaces, and added `tools/check_cargo_report_pack_contract.py` plus `tools/hygiene.py` so future revisions cannot change taxonomy values, review gates, scenario coverage, or example artifacts without failing a concrete contract check

## New (rev0315)
- Cargo-report contradiction/arbitration refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`, `fixtures/cargo-report-pack-kit/cargo-report-contradiction-packet.schema.json`, `fixtures/cargo-report-pack-kit/cargo-report-taxonomy.json`, `fixtures/cargo-report-pack-kit/cargo-report-scenario-index.json`, `fixtures/cargo-report-pack-kit/cargo-report-review-gates.json`, `fixtures/cargo-report-pack-kit/README.md`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **contradiction packets + arbitration witnesses + competing-head warnings + review-queue hold posture** as part of the same raw-evidence seam instead of forcing one same-scope report story to win silently by recency, vividness, or weaker derived convenience
- Strategy: clarified that the worthy contribution here is still not another dashboard, raw-log mirror, or premature schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer whose same-scope competing artifacts can remain explicitly unresolved, held, or branch-marked until native-basis precedence or manual review actually settles them
- Hygiene: strengthened `AGENTS.md`, `meta/AMNESIA_RESISTORS.md`, the Cargo-report fixture schemas, and named scenarios so future revisions cannot add competing operational heads, source-versus-summary contradictions, or lane-conflict carries without moving contradiction packets, arbitration rules, review-queue posture, and blocked stronger-use rules in the same revision

## New (rev0314)
- Cargo-report execution/lineage refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`, `fixtures/cargo-report-pack-kit/cargo-report-execution-receipt.schema.json`, `fixtures/cargo-report-pack-kit/cargo-report-lineage-register.schema.json`, `fixtures/cargo-report-pack-kit/cargo-report-taxonomy.json`, `fixtures/cargo-report-pack-kit/cargo-report-scenario-index.json`, `fixtures/cargo-report-pack-kit/cargo-report-review-gates.json`, `fixtures/cargo-report-pack-kit/README.md`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **execution receipts + derivation lineage registers + parent/output artifact links + no-semantic-backwrite provenance** as part of the same raw-evidence seam instead of letting packs, projected bundles, and derived summaries appear without a durable production story
- Strategy: clarified that the worthy contribution here is still not another dashboard, raw-log mirror, or premature schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer whose derived or promoted artifacts carry explicit production receipts and lineage links before broader build/perf/debug consumers or frozen shared heads rely on them
- Hygiene: strengthened `AGENTS.md`, `meta/AMNESIA_RESISTORS.md`, the Cargo-report fixture schemas, and named scenarios so future revisions cannot add derived summaries, projected exports, or promoted heads without moving execution receipts, lineage links, parent refs, and blocked stronger-use rules in the same revision

## New (rev0313)
- Cargo-report waiver-ledger refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`, `fixtures/cargo-report-pack-kit/cargo-report-waiver-ledger.schema.json`, `fixtures/cargo-report-pack-kit/cargo-report-taxonomy.json`, `fixtures/cargo-report-pack-kit/cargo-report-scenario-index.json`, `fixtures/cargo-report-pack-kit/cargo-report-review-gates.json`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **expiring waiver ledgers + named stronger-use exceptions + promotion/current/compat carry refs + stale-waiver demotion** as part of the same raw-evidence seam instead of leaving temporary reviewer overrides as prose footnotes
- Strategy: clarified that the worthy contribution here is still not another dashboard, raw-log mirror, or premature schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer whose stronger exceptions are durable, named, scoped, expiring artifacts rather than permanent hidden privileges
- Hygiene: strengthened `AGENTS.md`, `meta/AMNESIA_RESISTORS.md`, the Cargo-report fixture schemas, and named scenarios so future revisions cannot rely on waivers for stronger share/current/frozen reuse without owner/reviewer identity, expiry, status, and demotion behavior moving in the same revision

## New (rev0312)
- Cargo-report taxonomy/gates refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`, `fixtures/cargo-report-pack-kit/cargo-report-taxonomy.json`, `fixtures/cargo-report-pack-kit/cargo-report-scenario-index.json`, `fixtures/cargo-report-pack-kit/cargo-report-review-gates.json`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **taxonomy-backed class registers + scenario coverage index + machine-readable review gates** as part of the same raw-evidence seam instead of leaving claim/currentness/projection/quarantine/promotion meanings as open string fields
- Strategy: clarified that the worthy contribution here is still not another dashboard, raw-log mirror, or premature external schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer whose portable meanings are frozen through fixture-backed taxonomies and fail-closed gates before broader build/perf/debug consumers depend on them
- Hygiene: strengthened `AGENTS.md`, `meta/AMNESIA_RESISTORS.md`, and the Cargo-report fixture schemas so future revisions cannot add new class values, warning classes, or stronger promotion claims without moving the taxonomy, schema enums, examples, and scenario coverage in the same revision


## New (rev0311)
- Cargo-report fixture-corpus refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`, `fixtures/cargo-report-pack-kit/README.md`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **fixture-backed artifact vocabulary + schema/example freeze + named scenario corpus + review-completion gates** as part of the same raw-evidence seam instead of leaving authority/projection/quarantine/currentness/compatibility meaning to drift in prose alone
- Strategy: clarified that the worthy contribution here is still not another dashboard, raw-log mirror, or premature external schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer whose receipts and warning classes are frozen through a small fixtures corpus before stronger build/perf/debug consumers rely on them
- Hygiene: strengthened `AGENTS.md`, `meta/AMNESIA_RESISTORS.md`, and the Cargo-report pilot/deliverable surfaces so future revisions update schemas/examples/scenarios whenever claim classes, authority paths, projection rules, quarantine classes, currentness classes, compatibility gates, or frozen-head promotion rules change


## New (rev0310)
- Cargo-report quarantine-first refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **quarantine-first retained capture + omitted-field non-inference + derived-artifact separation + projection/currentness/compatibility discipline** as part of the same raw-evidence seam instead of forcing unstable/native-private imports into a false delete-or-share binary
- Strategy: clarified that the worthy contribution here is still not another dashboard, raw-log mirror, or schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer that can preserve risky/unknown/native-private bytes in a `capture-only` / `quarantined-retained` posture while keeping later summaries or normalized explanations on distinct derived artifacts rather than semantic back-writing onto the source
- Hygiene: strengthened `AGENTS.md`, `meta/AMNESIA_RESISTORS.md`, and the Cargo-report pilot/head/explain surfaces so future revisions keep quarantined-retained capture, projection receipts, omitted-field non-inference, derived summaries, frozen-head warnings, and downstream consumer conclusions distinct


## New (rev0309)
- Cargo-report projection-receipt refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **share-safe projection receipts + redaction/omission discipline + retained-basis-loss warnings + authority-path/currentness/compatibility discipline** as part of the same raw-evidence seam instead of letting one portable pack silently hide which local-private fields were filtered, coarsened, hashed, omitted, or later lost from the native basis
- Strategy: clarified that the worthy contribution here is still not another dashboard, raw-log mirror, or schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer that records how CLI args / environment / paths / raw payloads moved from local-native capture into portable packs, which omissions or redactions were intentional, and when stronger frozen/current/citation-like reuse must demote because only a projected or basis-lost artifact remains
- Hygiene: strengthened `AGENTS.md`, `meta/AMNESIA_RESISTORS.md`, and the Cargo-report pilot/diff/promote surfaces so future revisions keep local-private capture, projection receipts, omission notes, retained-basis loss, frozen-head warnings, and downstream consumer conclusions distinct


## New (rev0308)
- Cargo-report authority-path refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **authority-origin/import-path truth + fallback-order posture + refusal-posture gates + authoritative native basis + currentness/compatibility discipline** as part of the same raw-evidence seam instead of letting one pack silently inherit the authority of a stronger replay path than it actually used
- Strategy: clarified that the worthy contribution here is still not another dashboard, log scraper, or premature schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer that records whether a reviewable artifact came from Cargo-native replay, direct native session bytes, copied native bytes, or derived renderings, and when stronger reuse must fail closed rather than silently falling back
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md`, tightened nearby frontier wording, and cleaned the Cargo-report pilot ordering so future revisions keep authority path, fallback order, refusal posture, frozen-head authority, and downstream consumer conclusions distinct


## New (rev0307)
- Cargo-report drift-discipline refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **import-compatibility receipts + decoder/toolchain/schema-drift posture + material-change reimport/re-review gates + currentness/head-warning discipline** as part of the same raw-evidence seam instead of letting one unstable-derived pack silently keep the authority of a newer Cargo/toolchain/importer context
- Strategy: clarified that the worthy contribution here is still not another dashboard, log scraper, or premature schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer that records which native lane, decoder, and toolchain family interpreted the evidence and when stronger reuse must fail closed until drift is reviewed
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md`, and tightened nearby frontier wording so future cargo-report revisions keep retained native observations, compatibility receipts, reimport triggers, frozen-head authority, and downstream consumer conclusions distinct



## New (rev0306)
- Cargo-report currentness refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **observation-epoch truth + currentness class + recheck-gate discipline + superseded/stale-head warnings + authoritative native basis + exact coverage/claim boundaries** as part of the same raw-evidence seam instead of letting one retained session, one replayable report id, or one copied timing HTML artifact silently pose as the current workspace build state
- Strategy: clarified that the worthy contribution here is still not another dashboard, log scraper, or premature schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer that records when an artifact is only historical, when it is current only as-of a named observation epoch, when it has actually been rechecked against a newer native basis, and when later heads supersede earlier ones
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md`, and tightened nearby frontier wording so future cargo-report revisions keep historical native observations, current active claims, stale/superseded heads, frozen shared examples, and downstream consumer conclusions distinct



## New (rev0305)
- Cargo-report claim-scope refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **observed native scope + coverage-slice exactness + lane-wide claim-class honesty + authoritative native basis + promotion/head-warning discipline** as part of the same raw-evidence seam instead of letting one session, one target/profile slice, or one copied HTML replay silently pose as workspace-wide build truth
- Strategy: clarified that the worthy contribution here is still not another dashboard, log scraper, or premature schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer that records what Cargo actually observed, what a later shared artifact is allowed to claim, and when workspace/target/feature/toolchain-wide sentences must fail closed
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md`, and tightened nearby frontier wording so future cargo-report revisions keep observed scope, claim scope, partial-coverage warnings, promotion receipts, and downstream consumer conclusions distinct


## New (rev0304)
- Cargo-report promotion-boundary refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **authoritative native basis + stable-vs-unstable report posture + exact session/report scope + field authorship + local-private-capture-versus-portable-pack-versus-shared-surface-versus-frozen-head truth + promotion/head-warning discipline + replay/copy provenance + bounded build/perf/debug handoffs** as a first-order raw-evidence seam instead of leaving Cargo-native report reality split across `future-incompat`, build-analysis session logs, copied HTML, CI artifacts, issue attachments, and downstream adapter folklore
- Strategy: clarified that the worthy contribution here is still not another dashboard, log scraper, or premature schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer that imports stable `future-incompat` first, then honest unstable build-analysis sessions, while keeping authoritative basis, portable packs, frozen shared heads, and downstream diagnoses explicitly distinct
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md`, and tightened nearby frontier wording so future cargo-report revisions keep basis truth, scope exactness, field authorship, capture/share posture, promotion warnings, normalized pack truth, and consumer conclusions distinct

## New (rev0303)
- Cargo-report hardening refresh: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`
- Frontier/priority refresh: sharpened **Cargo Report Kit** so the archive now treats **stable-vs-unstable native report posture + exact session/report scope + field authorship + local-private-capture-versus-portable-pack-versus-shared-surface truth + replay/copy provenance + bounded build/perf/debug handoffs** as a first-order raw-evidence seam instead of leaving Cargo-native report reality split across `future-incompat`, build-analysis session logs, HTML replay, CI artifacts, issue attachments, and downstream adapter folklore
- Strategy: clarified that the worthy contribution here is still not another dashboard, log scraper, or premature schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer that imports stable `future-incompat` first, then honest unstable build-analysis sessions, while keeping Cargo-home capture, portable packs, shared surfaces, and downstream diagnoses explicitly distinct
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md`, and tightened nearby frontier wording so future cargo-report revisions keep scope exactness, field authorship, capture/share posture, normalized pack truth, and consumer conclusions distinct

## New (rev0302)
- Cargo-report refresh + new pilot layer: `gaps/standardized-cargo-reports.md`, `design/cargo-report-kit.md`, `design/cargo-report-pilot-program.md`, `proposals/epic-cargo-report-kit.md`
- Frontier/priority refresh: re-elevated **Cargo Report Kit** so the archive now treats **stable-vs-unstable native report posture + session/report identity + replay/copy provenance + normalized import truth + bounded build/perf/debug handoffs** as a first-order raw-evidence seam instead of leaving Cargo-native report reality split across `future-incompat`, build-analysis session logs, HTML replay, CI artifacts, and downstream adapter folklore
- Strategy: clarified that the worthy contribution here is not another dashboard, log scraper, or premature schema freeze, but a thin `cargo reportpack` / `cargo-report-pack/v0` layer that proves stable `future-incompat` import first and then honest unstable build-analysis session imports above Cargo-native storage and below Build-State Evidence / Perf Labs / Feedback Loop
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md`, and tightened nearby build-state/perf/frontier wording so future cargo-report revisions keep native report families, session ids, copied attachments, normalized packs, and downstream diagnoses distinct

## New (rev0301)
- Gap/design/proposal refresh + new pilot layer: `gaps/embedded-device-labs-and-hardware-in-the-loop.md`, `design/device-lab-kit.md`, `design/device-lab-lane-map.md`, `design/device-lab-pilot-program.md`, `proposals/epic-device-lab-kit.md`
- Frontier/priority refresh: re-elevated **Device Lab Kit** so the archive now treats **board/probe/fixture truth + lab capability/quarantine truth + run-plan truth + native capture-import truth + normalized on-device report truth + bounded firmware/testing/release handoffs** as a first-order execution seam instead of leaving embedded hardware evidence split across `probe-rs`, `embedded-test`, `defmt`, archived templates/runners, CI YAML, and bring-up folklore
- Strategy: clarified that the worthy contribution here is not another board template, runner wrapper, or hosted lab scheduler, but a thin `cargo devicelab` / `lab-pack/v0` layer with an explicit `device-capture-import/v0` boundary plus a ranked `design/device-lab-pilot-program.md` execution path
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md`, and tightened nearby firmware/testing ownership so future device-lab revisions keep board identity, run lane, target-enablement posture, native captures, normalized run reports, shared-lab state, and downstream support/release claims distinct

## New (rev0300)
- New gap/design/pilot/proposal layer: `gaps/benchmark-evidence-subjects-lanes-baselines-and-imports.md`, `design/benchmark-evidence-kit.md`, `design/benchmark-evidence-pilot-program.md`, `proposals/epic-benchmark-evidence-kit.md`
- Frontier/priority refresh: promoted an explicit **Benchmark Evidence Kit** lower-level anchor so the archive now treats **benchmark subject truth + measurement-lane/counter truth + runner/import posture + baseline-import truth + native result/attachment lineage + bounded Perf Labs handoffs** as its own reusable boundary instead of leaving Rust benchmarks smeared across `cargo bench`, Criterion/cargo-criterion JSON, Divan counters, nextest bench imports, Iai-Callgrind outputs, and hosted-service adapters
- Strategy: clarified that the worthy contribution here is not another benchmark harness, dashboard, or fake universal score, but a thin `cargo benchpack` / `benchmark-pack/v0` layer between **Harness Protocol + Test Run Evidence** and **Perf Labs**
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md`, and narrowed nearby ownership boundaries so future benchmark revisions keep harness discovery, benchmark-native results, runner imports, baseline imports, compare policy, and downstream conclusions distinct

## New (rev0299)
- Coverage-evidence refresh + new pilot layer: `gaps/coverage-evidence-and-ci-review.md`, `design/coverage-evidence-kit.md`, `design/coverage-evidence-pilot-program.md`, `proposals/epic-coverage-evidence-kit.md`
- Frontier/priority refresh: re-elevated **Coverage Evidence Kit** so the archive now treats **criterion truth + imported execution truth + merge/comparability honesty + diffable gates + bounded safety-critical handoffs** as a first-order execution seam instead of leaving Rust coverage split across compiler flags, `cargo-llvm-cov`, nextest/doctest merges, Tarpaulin backend differences, and hosted-service percentages
- Strategy: clarified that the worthy contribution here is not another badge, dashboard, or one-number service, but a thin `cargo cov` / `coverage-pack/v0` layer with explicit `coverage-criterion-profile/v0` and `coverage-execution-import/v0` boundaries above engines and below testing/safety consumers
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future coverage revisions keep criterion class, execution imports, merge provenance, gate outcomes, and downstream assurance conclusions distinct

## New (rev0298)
- Dynamic-analysis refresh + new pilot layer: `gaps/sanitizers-and-dynamic-analysis.md`, `design/sanitizer-battery-kit.md`, `design/sanitizer-battery-pilot-program.md`, `proposals/epic-sanitizer-battery-kit.md`
- Frontier/priority refresh: re-elevated **Sanitizer Battery Kit** so the archive now treats **lane identity + instrumented-runtime provenance + imported execution truth + capability/blind-spot honesty + finding/waiver/diff continuity + bounded toolchain/safety handoffs** as a first-order execution seam instead of leaving Rust dynamic analysis split across engine flags, runner differences, instrumented-stdlib lore, and CI scripts
- Strategy: clarified that the worthy contribution here is not another checker, wrapper, or fake universal battery command, but a thin `cargo sanitize` / `sanitize-pack/v0` layer with an explicit `sanitize-execution-import/v0` boundary above engines and below testing/toolchain/safety consumers
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future dynamic-analysis revisions keep engine family, runtime/sysroot provenance, runner/import semantics, visibility limits, finding reports, and downstream assurance conclusions distinct

## New (rev0297)
- Testing-stack refresh: `design/test-execution-evidence-stack.md`, `design/test-run-evidence-kit.md`, `design/test-execution-pilot-program.md`, `proposals/epic-test-execution-evidence-stack.md`
- Frontier/priority refresh: re-elevated **Test Execution Evidence Stack** so the archive now treats **harness truth + concrete run truth + imported runner-native recordings + config-bound execution identity + specialized attachment continuity + bounded consumer handoffs** as a first-order “better test tooling” seam instead of leaving Rust testing split across unstable libtest JSON, nextest-native stores, JUnit exports, CI job names, and raw logs
- Strategy: clarified that the worthy contribution here is not another test runner, XML bridge, or one-runner recording store, but a thin `cargo test-execution` / `test-exec-pack/v0` layer with an explicit `runner-recording-import/v0` boundary above Harness Protocol and below coverage/fuzz/replay/downstream/device consumers
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future testing revisions keep harness discovery, portable run reports, runner-native recordings, config ids, specialized attachments, and downstream verdicts distinct

## New (rev0296)
- Formal-verification design refresh + new pilot layer: `design/formal-verification-kit.md`, `design/formal-verification-pilot-program.md`, `proposals/epic-formal-verification-kit.md`
- Frontier/priority refresh: re-elevated **Formal Verification Kit** so the archive now treats **proof subject truth + backend-family identity + imported native outputs + assumption/trusted-code budget + proof/counterexample/diff artifacts + bounded safety-critical imports** as a first-order execution seam instead of leaving verification as an important-but-abstract Tier 1 note
- Strategy: clarified that the worthy contribution here is not another verifier wrapper, proof badge, or premature certification bundle, but a ranked `cargo verify pilot` / `verify-pilot-pack/v0` execution path that hardens proof/report interoperability before wider safety-critical consumers import it
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future passes keep proof subject, backend-family identity, imported native outputs, assumption budget, counterexample/failure artifacts, and certified-or-derived proof attachments distinct

## New (rev0295)
- Gap refresh + new design/proposal layer: `gaps/consumer-install-selection-channels-mirrors-and-receipts.md`, `design/consumer-install-kit.md`, `proposals/epic-consumer-install-kit.md`
- Frontier/priority refresh: promoted an explicit **Consumer Install Kit** lower-level anchor so the archive now treats **install subject truth + visible candidate truth + install policy/plan truth + receipt/mutation truth + managed-content claim + bounded downstream handoffs** as its own reusable boundary instead of leaving first-install reality smeared across Distribution Contract, `cargo install`, `cargo-binstall`, cargo-dist mirrors, CI fallback glue, and tool-local receipts
- Strategy: clarified that the worthy contribution here is not another installer wrapper, package-manager shim, or self-update helper, but a thin `cargo installproof` / `install-pack/v0` layer above current install lanes and below Distribution Contract / Update Continuity consumers
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md`, and narrowed nearby ownership boundaries so future passes keep install subject, visible candidates, policy/plan, receipt/mutation, managed-content claims, and downstream lifecycle/support conclusions distinct

## New (rev0294)
- New gap/design/proposal layer: `gaps/update-continuity-detection-selection-apply-rollback-and-uninstall.md`, `design/update-continuity-kit.md`, `proposals/epic-update-continuity-kit.md`
- Frontier/priority refresh: promoted an explicit **Update Continuity Kit** lower-level anchor so the archive now treats **current installed-subject truth + candidate/comparator truth + chosen plan truth + apply/rollback result truth + ownership/uninstall truth + bounded downstream handoffs** as its own reusable boundary instead of letting update and uninstall reality stay smeared across Distribution Contract, release feeds, self-update helpers, app-updater docs, and support folklore
- Strategy: clarified that the worthy contribution here is not another self-update crate, installer rerun helper, release-feed format, or package-manager wrapper, but a thin `cargo update-continuity` / `update-pack/v0` layer above install receipts and below broader CLI/client/extension/operator/support consumers
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md`, and narrowed nearby ownership boundaries so future passes keep current install truth, candidate/comparator truth, plan/apply truth, rollback/uninstall ownership, and downstream support/policy/product conclusions distinct

## New (rev0293)
- Refreshed and re-elevated the existing **Reflection Transition Stack** seam instead of inventing another adjacent reflection crate wish
- Gap/design/pilot/proposal refresh: `gaps/reflection-transition-lane-comparison-macro-burden-and-core-reflection-migration.md`, `design/reflection-transition-stack.md`, `design/reflection-transition-pilot-program.md`, `proposals/epic-reflection-transition-stack.md`
- Frontier/priority refresh: elevated **Reflection Transition Stack** into the current frontier-correction band, so the archive now treats **proc-macro burden + runtime reflection semantics + visit-only/schema lanes + foreign-type/orphan-rule pressure + future compile-time reflection posture** as one explicit migration boundary instead of leaving reflection transition split across Bevy-style runtime registries, inspect-only observability, schema tracing, and language-roadmap notes
- Strategy: clarified that the worthy contribution here is not another runtime reflection crate, derive helper, registry macro, or premature universal reflect trait, but a thin `cargo reflect-transition` / `reflection-transition-pack/v0` layer above **Macro Workflow + Reflection Surface + Const Surface**
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future passes keep macro burden, runtime reflection, visit-only inspection, schema extraction, future compile-time reflection, and downstream consumer conclusions distinct

## New (rev0292)
- Refreshed and re-elevated the existing **Runtime Capability Kit** seam around **declared authority + inferred authority + generated policy + enacted policy + checked behavior** instead of inventing another security wrapper
- Gap/design/pilot/proposal refresh: `gaps/runtime-capabilities-and-least-privilege-contracts.md`, `design/runtime-capability-kit.md`, `design/runtime-capability-pilot-program.md`, `proposals/epic-runtime-capability-kit.md`
- Frontier/priority refresh: sharpened **Runtime Capability Kit** as a concrete blast-radius-reduction boundary beneath Trust / Policy / Dependency Review, so the archive now treats **authority classes + scopes + delegation + analyzer plurality + candidate enforcement + enacted enforcement continuity + drift/evidence handoff** as one reusable contract instead of leaving Rust capability truth split across APIs, framework configs, analyzer output, seccomp drafts, and deployment folklore
- Strategy: clarified that the worthy contribution here is not another seccomp generator, permissions DSL, or one-true sandbox, but a thin `cargo capability` / `cap-pack/v0` layer with an explicit `cap-enactment-report/v0` to keep generated and deployed truth separate
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future passes keep declaration, inference, generation, enactment, and downstream policy/support conclusions distinct
## New (rev0291)
- Refreshed and deepened the existing **FuzzPack Kit** seam instead of adding another Cargo-adjacent wrapper idea
- Stack/design refresh: `gaps/fuzzing-orchestration.md`, `design/fuzzpack-kit.md`, `proposals/epic-fuzzpack-kit.md`
- Frontier/priority refresh: elevated **FuzzPack Kit** as the most under-modeled execution-evidence lane inside the broader Testing Contract Stack, so the archive now treats **target profile truth + corpus/crasher/regression truth + shrink/minimization truth + execution-envelope truth + replay/diff handoff** as one reusable boundary instead of leaving Rust fuzzing split across engine directories, property-test files, CI artifacts, and shell history
- Strategy: clarified that the worthy contribution here is not another engine wrapper or fuzzing dashboard, but a thin `cargo fuzzpack` / `fuzz-pack/v0` layer above `cargo-fuzz`, `honggfuzz`, `test-fuzz`, `proptest`, and optional LibAFL imports
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future passes keep target profile truth, corpus/crash truth, persisted regression seeds, shrink/minimization traces, execution-envelope assumptions, and later policy/support conclusions distinct

## New (rev0290)
- New gap: `gaps/package-admission-publish-review-evidence-waivers-and-handoffs.md`
- Stack refresh: `design/package-admission-stack.md`, `design/package-admission-pilot-program.md`, `proposals/epic-package-admission-stack.md`
- Frontier/priority refresh: elevated **Package Admission Stack** as a sharper publish-review synthesis above **Publish Set + Dependency Control + Public API + SBOM Evidence + Trust Signals + Policy**, so the archive now treats **selected package/payload/receipt truth + graph/exposure/inventory/trust evidence + explicit admit/hold/warn/inconclusive decisions + package-to-release handoff** as one review boundary instead of leaving publish review smeared across Cargo packaging, registry UI, API checks, trust signals, and CI policy glue
- Strategy: clarified that the worthy contribution here is not another secure-publish wrapper, registry score, or release umbrella, but a thin `cargo package-admission` / `package-admission-pack/v0` layer importing `publish-pack/v0` and other existing evidence packs
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future passes keep publish-set truth, graph truth, exposure truth, inventory truth, trust inputs, policy decisions, and later release/install conclusions distinct

## New (rev0289)
- New gap/design/proposal layer: `gaps/publish-sets-package-selection-contents-verification-and-registry-receipts.md`, `design/publish-set-kit.md`, `proposals/epic-publish-set-kit.md`
- Frontier/priority refresh: promoted an explicit **Publish Set Kit** lower-level anchor so the archive now treats **selected publish subject truth + packaged payload truth + check/waiver truth + authority/registry-path truth + upload/index receipt truth + bounded downstream handoffs** as its own reusable boundary instead of letting source-package publication stay smeared across Manifest Truth, Publisher & Source Identity, Release Pipeline, Package Admission, and CI workflow glue
- Strategy: clarified that the worthy contribution here is not another release bot, version-bump wrapper, registry dashboard, or trusted-publishing badge, but a thin `cargo publish-set` / `publish-pack/v0` layer above Cargo packaging and registry upload and below broader release/install consumers
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md`, and narrowed nearby ownership boundaries so future passes keep publish subject, package payload, check/waiver posture, authority path, upload/index receipts, and downstream release/library/admission conclusions distinct

## New (rev0288)
- New gap/design/proposal layer: `gaps/discovery-boundaries-manifest-workspace-config-and-explicit-attachment.md`, `design/discovery-boundary-kit.md`, `proposals/epic-discovery-boundary-kit.md`
- Frontier/priority refresh: promoted an explicit **Discovery Boundary Kit** lower-level anchor so the archive now treats **invocation subject truth + manifest walk truth + workspace attachment/opt-out truth + config-discovery provenance + consumer-import lossiness** as its own reusable boundary instead of letting discovery stay smeared across Repo Composition, Workspace Governance, ScriptKit, Build Interop, and Workspace Environment
- Strategy: clarified that the worthy contribution here is not another workspace manager, repo daemon, config wrapper, or editor-only discover hook, but a thin `cargo discoverbound` / `discovery-pack/v0` layer above Cargo’s discovery facts and below later governance/build/environment layers
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md`, and narrowed nearby ownership boundaries so future passes keep invocation subject, manifest walk, workspace attachment, config discovery, consumer-import views, and downstream governance/build conclusions distinct

## New (rev0287)
- Gap/design/pilot/proposal refresh: `gaps/starter-repos-template-provenance-and-freshness.md`, `design/starter-pack-kit.md`, `design/starter-pack-pilot-program.md`, `proposals/epic-starter-pack-kit.md`
- Frontier/priority refresh: elevated **Starter Pack Kit** as an explicit execution bridge above Atlas / Adoption Decision and below real repo bootstrapping, so the archive now treats **starter subject + imported recommendation/workenv/policy truth + render-plan/adapter truth + working-tree ownership + overlays + freshness/refresh** as a missing ecosystem contract rather than leaving bootstrapping split across `cargo new`, `cargo-generate`, framework/domain-specific generators, copied starter repos, and assistant-produced skeletons
- Strategy: clarified that the worthy contribution here is not another template engine, framework quickstart wrapper, or giant repo generator, but a thin `cargo starter` / `starter-pack/v0` layer with explicit `starter-render-plan/v0` and `starter-render-report/v0` artifacts above both direct and delegated renderers
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future passes keep imported recommendation truth, render-plan/adapter truth, rendered-file ownership, overlays, freshness, and derived guide/assistant outputs distinct instead of collapsing them into one fake “official starter repo”

## New (rev0286)
- New gap: `gaps/final-artifact-surface-identity-selection-outputs-and-handoffs.md`
- New design: `design/artifact-surface-kit.md`
- New proposal: `proposals/epic-artifact-surface-kit.md`
- Frontier/priority refresh: promoted an explicit **Artifact Surface Kit** seam so the archive now treats **selected build subject truth + final output identity + origin/location truth + artifact-linked sidecars + bounded downstream handoffs** as a reusable lower-level anchor instead of leaving Rust final-artifact reality split across JSON streams, target-dir folklore, release manifests, and CI glue
- Strategy: clarified that the worthy contribution here is not another target-dir scraper, JSON helper, release wrapper, or installer manifest, but a thin `cargo artifacts` / `artifact-pack/v0` layer above **Cargo final outputs + bounded uplift imports + explicit handoff summaries**
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future passes keep selected-subject truth, final-artifact truth, sidecar truth, release truth, and installed-state truth distinct instead of collapsing them into one fake “artifact shipped” story

## New (rev0285)
- Gap/design refresh: `gaps/polyglot-host-packages-runtime-and-support-contracts.md`, `design/host-package-kit.md`
- New proposal: `proposals/epic-host-package-kit.md`
- Frontier/priority refresh: promoted an explicit **Host Package Kit** proposal layer so the archive now treats **crate-vs-foreign-package identity + imported boundary truth + generated-binding provenance + runtime/interpreter/ABI/support truth + shipped/install receipts + bounded downstream conclusions** as a reusable cross-stack anchor instead of leaving host-facing Rust packages as a footnote inside Polyglot, Extension, and Web productization notes
- Strategy: clarified that the worthy contribution here is not another wheel helper, prebuild matrix wrapper, binding generator, or host-language package manager, but a thin `cargo hostpkg` / `hostpkg-pack/v0` layer above **foreign package truth + imported FFI/component/schema attachments + runtime/install/support evidence**
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future passes prefer promoting reusable lower-level anchors inside already-explicit stacks and keep foreign-package truth, imported boundary truth, runtime constraints, shipped/install receipts, and downstream conclusions distinct instead of collapsing them into one fake “bindings shipped” story

## New (rev0284)
- New gap: `gaps/native-edge-adoption-boundaries-provider-locks-and-build-handoffs.md`
- New design: `design/native-edge-stack.md`
- Pilot refresh: `design/native-edge-pilot-program.md`
- New proposal: `proposals/epic-native-edge-stack.md`
- Frontier/priority refresh: promoted an explicit **Native Edge Stack** proposal layer so the archive now treats **FFI boundary truth + native-provider/link truth + host/target/build-handoff context + bounded release/support/audit conclusions** as a ranked seam with a concrete build direction instead of a frontier note split across two adjacent kits
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future native-edge revisions keep boundary truth, provider/link truth, host/target/toolchain context, external-build handoff, and downstream conclusions distinct instead of collapsing them into one fake “interop readiness” story

## New (rev0283)
- New gap: `gaps/streaming-dataflows-sources-time-state-materialization-and-progress-contracts.md`
- New design: `design/dataflow-surface-kit.md`
- New pilot: `design/dataflow-surface-pilot-program.md`
- New proposal: `proposals/epic-dataflow-surface-kit.md`
- Frontier/priority refresh: promoted an explicit **Dataflow Surface Kit** seam so the archive now treats **source/sink truth + event-time/watermark/window/lateness truth + state/checkpoint/backfill/recovery posture + materialization/freshness/progress evidence** as a real frontier band instead of leaving Rust streaming/dataflow split across SQL files, connector config, checkpoint metadata, catalogs, dashboards, and README folklore
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future dataflow-surface revisions keep source/connector truth, temporal semantics, state/checkpoint/backfill truth, materialization/progress evidence, and downstream conclusions separate instead of collapsing them into one fake “real-time readiness” story

## New (rev0282)
- New gap: `gaps/workflow-products-jobs-schedules-journals-and-support-contracts.md`
- New design: `design/workflow-productization-stack.md`
- New pilot: `design/workflow-productization-pilot-program.md`
- New proposal: `proposals/epic-workflow-productization-stack.md`
- Frontier/priority refresh: promoted an explicit **Workflow Productization Stack** seam so the archive now treats **declared jobs/workflows/schedules truth + runtime/engine/storage activation + journal/history/retry/recovery evidence + long-lived release lineage + shipped/support truth** as a real frontier band instead of leaving Rust durable work split across queue tables, engine dashboards, worker code, runtime config, and README folklore
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future workflow-productization revisions keep declared work truth, runtime activation, history/evidence, release lineage, and downstream conclusions distinct instead of collapsing them into one fake “workflow reliability” story

## New (rev0281)
- New gap: `gaps/operator-products-crds-rbac-webhooks-status-and-support-contracts.md`
- New design: `design/operator-productization-stack.md`
- New pilot: `design/operator-productization-pilot-program.md`
- New proposal: `proposals/epic-operator-productization-stack.md`
- Frontier/priority refresh: promoted an explicit **Operator Productization Stack** seam so the archive now treats **CRD/status truth + RBAC/capability posture + webhook/health/admin truth + runtime evidence + install/upgrade/Kubernetes-version truth + shipped/support claims** as a real frontier band instead of leaving Rust operators split across CRD YAML, controller code, RBAC files, charts, dashboards, and README folklore
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future operator-productization revisions keep CRD/schema truth, capability posture, runtime evidence, webhook surfaces, install/support truth, and downstream conclusions distinct instead of collapsing them into one fake “operator readiness” story

## New (rev0280)
- New gap: `gaps/geospatial-products-datasets-catalogs-tiles-and-support-contracts.md`
- New design: `design/geospatial-productization-stack.md`
- New pilot: `design/geospatial-productization-pilot-program.md`
- New proposal: `proposals/epic-geospatial-productization-stack.md`
- Frontier/priority refresh: promoted an explicit **Geospatial Productization Stack** seam so the archive now treats **spatial semantics truth + dataset/catalog/archive publication truth + runtime/native/backend activation + client/render/query attachments + shipped/support truth** as a real frontier band instead of leaving Rust geospatial products split across `geo-pack` declarations, STAC/GeoParquet/PMTiles metadata, renderer configs, and README folklore
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future geospatial-productization revisions keep spatial semantics, publication/freshness truth, runtime activation, importing client/search/service lanes, and downstream conclusions distinct instead of collapsing them into one fake “geospatial support” story

## New (rev0279)
- New gap: `gaps/search-products-corpora-indexes-ranking-freshness-and-support-contracts.md`
- New design: `design/search-productization-stack.md`
- New pilot: `design/search-productization-pilot-program.md`
- New proposal: `proposals/epic-search-productization-stack.md`
- Frontier/priority refresh: promoted an explicit **Search Productization Stack** seam so the archive now treats **query/ranking truth + corpus freshness/import truth + hybrid/model attachments + runtime/evidence truth + shipped/support truth** as a real frontier band instead of leaving Rust search products split across index configs, embedder setup, dashboards, and README folklore
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future search-productization revisions keep query/ranking truth, corpus freshness truth, hybrid/model attachments, runtime activation, and downstream conclusions distinct instead of collapsing them into one fake “search support” story

## New (rev0278)
- New gap: `gaps/robot-description-topology-frames-calibration-and-runtime-handoffs.md`
- New design: `design/robot-description-surface-kit.md`
- New pilot: `design/robot-description-pilot-program.md`
- New proposal: `proposals/epic-robot-description-surface-kit.md`
- Frontier/priority refresh: promoted a new robotics-domain seam centered on portable robot-description truth rather than another framework/runtime bake-off
- Hygiene: added a robotics-specific amnesia resistor so future revisions keep authored model truth, frame topology, geometry/assets, limits/calibration posture, and imported runtime/replay evidence separate

## New (rev0277)
- Epic: `proposals/epic-firmware-productization-stack.md`
- Design refresh: `design/firmware-productization-stack.md`, `design/firmware-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Firmware Productization Stack** proposal layer so the archive now treats **board/probe/run truth + target/linker/sysroot/build-std activation + footprint/layout evidence + runtime logging/fault truth + shipped/support truth** as a ranked seam with a concrete build direction instead of a strong-but-still-implicit frontier band
- Strategy: clarified that the worthy contribution here is not another HAL unification push, board template, probe wrapper, or framework bake-off, but a thin `cargo firmware-product` / `firmware-product-pack/v0` layer above **Device Lab + Toolchain Productization + Footprint + Observability + Support Envelope + Release Truth**
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future firmware-productization revisions keep board/probe/run truth, target activation, footprint/layout evidence, runtime-evidence channels, and shipped/support conclusions distinct instead of collapsing them into one fake embedded-readiness story

## New (rev0276)
- Epic: `proposals/epic-data-productization-stack.md`
- Design refresh: `design/data-productization-stack.md`, `design/data-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Data Productization Stack** proposal layer so the archive now treats **live database truth + checked-query/offline truth + public schema truth + migration-program truth + runtime activation + support/docs truth** as a ranked seam with a concrete build direction instead of a strong-but-still-implicit frontier band
- Strategy: clarified that the worthy contribution here is not another ORM, query DSL, migration generator, or hosted control plane, but a thin `cargo data-product` / `data-product-pack/v0` layer above **Database Contract + Schema Contract + Migration Truth + Runtime Settings + Support Envelope**
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future data-productization revisions keep checked queries, live DB truth, public schema truth, migration choreography, runtime activation, and downstream conclusions distinct instead of collapsing them into one fake “data platform readiness” story

## New (rev0275)
- Epic: `proposals/epic-interactive-productization-stack.md`
- Design refresh: `design/interactive-productization-stack.md`, `design/interactive-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Interactive Productization Stack** proposal layer so the archive now treats **asset/content truth + shader/backend/device truth + window/input/frame-loop truth + runtime/perf activation + shipped/support truth** as a ranked seam with a concrete build direction instead of a strong-but-still-implicit frontier band
- Strategy: clarified that the worthy contribution here is not another engine, renderer wrapper, asset helper, profiling HUD, or starter template, but a thin `cargo interactive-product` / `interactive-product-pack/v0` layer above **Media Surface + Offload Surface + Client App Surface + Runtime Settings + Observability + Distribution Contract + Support Envelope**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future interactive-productization revisions keep tooling/editor-runtime posture distinct from shipped interactive support instead of collapsing them into one fake "interactive readiness" story

## New (rev0274)
- Epic: `proposals/epic-local-first-productization-stack.md`
- Design refresh: `design/local-first-productization-stack.md`, `design/local-first-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Local-First Productization Stack** proposal layer so the archive now treats **replica/document/history/storage truth + client-vs-relay/runtime-role truth + runtime/identity activation + recovery/export/migration truth + support/docs truth** as a ranked seam with a concrete build direction instead of a strong-but-still-implicit frontier band
- Strategy: clarified that the worthy contribution here is not another CRDT engine, relay backend, full-stack sync framework, or Tauri-plus-sync starter, but a thin `cargo local-product` / `local-first-product-pack/v0` layer above **Replica Surface + Client App Surface + Event/Service Surface + Runtime Settings + Identity Surface + Support Envelope**
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future passes keep durable replica truth, ephemeral awareness/presence truth, client/relay/runtime-role truth, recovery/export posture, and downstream conclusions distinct instead of collapsing them into one fake “collaboration readiness” story

## New (rev0273)
- Epic: `proposals/epic-scientific-productization-stack.md`
- Design refresh: `design/scientific-productization-stack.md`, `design/scientific-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Scientific Productization Stack** proposal layer so the archive now treats **array/tensor truth + dataset/storage truth + backend/device truth + model/runtime attachments + activation truth + support/docs truth** as a ranked seam with a concrete build direction instead of a strong-but-still-implicit frontier band
- Strategy: clarified that the worthy contribution here is not a Rust NumPy clone, one giant GPU stack, a model-runtime winner pitch, or a benchmark theater dashboard, but a thin `cargo science-product` / `scientific-product-pack/v0` layer above **Tensor Surface + Dataset Surface + Offload Surface + Model Surface + Runtime Settings + Support Envelope**
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future passes prefer promoting already-designed stacks before inventing adjacent kits and future scientific-productization revisions keep imported interchange prior art, activation truth, and downstream conclusions distinct instead of collapsing them into one fake “scientific readiness” story

## New (rev0272)
- Epic: `proposals/epic-identity-productization-stack.md`
- Design refresh: `design/identity-productization-stack.md`, `design/identity-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Identity Productization Stack** proposal layer so the archive now treats **supported-auth/principal truth + protected-surface requirements + provider/session/cookie/key activation + authorization-policy attachments + support/docs truth + migration evidence** as a ranked seam with a concrete build direction instead of a strong-but-still-implicit frontier band
- Strategy: clarified that the worthy contribution here is not another auth framework, JWT/session abstraction, route-guard pile, or policy-engine winner pitch, but a thin `cargo identity-product` / `identity-product-pack/v0` layer above **Identity Surface + Runtime Settings + Credentials + Support Envelope**, with Service/Command/Schema/Client lanes importing it
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future identity-productization revisions keep supported auth methods, protected-surface coverage, provider/session/key activation, authorization-engine attachments, support/docs/platform truth, and migration conclusions distinct instead of collapsing them into one fake “auth support” story

## New (rev0271)
- Epic: `proposals/epic-borrowing-frontier-stack.md`
- Design refresh: `design/borrowing-frontier-stack.md`, `design/borrowing-frontier-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Borrowing Frontier Stack** proposal layer so the archive now treats **trait-family truth + pointer/reference truth + lending/sequence truth + initialization/destruction truth + migration-horizon evidence** as a ranked seam with a concrete build direction instead of a strong-but-still-implicit frontier band
- Strategy: clarified that the worthy contribution here is not a universal smart-pointer trait, one true lending facade, or constructor empire, but a thin `cargo borrowfront` / `borrowing-frontier-pack/v0` layer above **Trait Surface + Pointer Surface + Lending Surface + Initialization Surface**
- Hygiene: strengthened `AGENTS.md` and `meta/AMNESIA_RESISTORS.md` so future borrowing-frontier revisions keep roadmap motion, workaround-crate posture, stable-vs-nightly/native-vs-adapter truth, migration horizon, and downstream conclusions distinct instead of collapsing them into one fake “borrowing ergonomics solved” story

## New (rev0270)
- Epic: `proposals/epic-agent-productization-stack.md`
- Design refresh: `design/agent-productization-stack.md`, `design/agent-productization-pilot-program.md`, `gaps/agentic-application-surfaces-and-tooling-contracts.md`
- Meta-engineering: added `AGENTS.md` as a repo-operational guardrail so future LLM passes re-read the canon, preserve root/archive parity, prefer one high-leverage move, and keep repo instructions separate from research truth
- Frontier/priority refresh: promoted an explicit **Agent Productization Stack** proposal layer so the archive now treats **workflow/prompt/tool/resource truth + model/retrieval attachments + runtime/identity activation + eval/trace evidence + migration/support truth** as a ranked seam with a concrete build direction instead of a strong-but-still-implicit stack note
- Strategy: clarified that the worthy contribution here is not another agent framework, MCP helper, or provider wrapper, but a thin `cargo agent-product` / `agent-product-pack/v0` layer above **Agent Surface + Model Surface + Retrieval Surface + Runtime Settings + Identity Surface + Observability + Support Envelope**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future archive-maintenance passes keep repo-operational instructions distinct from research canon and future agent-productization revisions keep workflow truth, imported capability/runtime facts, migration evidence, and downstream conclusions distinct instead of collapsing them into one fake “agent readiness” story

## New (rev0269)
- Epic: `proposals/epic-extension-productization-stack.md`
- Design refresh: `design/extension-productization-stack.md`, `design/extension-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Extension Productization Stack** proposal layer so the archive now treats **host/plugin surface truth + runtime-kind/capability truth + extension package/install/update truth + compatibility/migration truth + shipped/support truth** as a ranked seam with a concrete build direction instead of a strong-but-still-implicit stack note
- Strategy: clarified that the worthy contribution here is not another plugin SDK, extension gallery, marketplace scraper, or Wasm-only convenience layer, but a thin `cargo extensioncheck` / `extension-product-pack/v0` layer above **Plugin Surface + Runtime Capability + Wasm Component + Host Package + Distribution Contract + Support Envelope**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future extension-productization revisions keep host version, plugin package version, protocol/WIT/runtime compatibility, capability activation, install/update truth, and downstream conclusions distinct instead of collapsing them into one fake “extension readiness” story

## New (rev0268)
- Gap: `gaps/mixed-language-product-boundaries-crate-package-binding-runtime-and-support-truth.md`
- Epic: `proposals/epic-polyglot-productization-stack.md`
- Design refresh: `design/polyglot-productization-stack.md`, `design/polyglot-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Polyglot Productization Stack** proposal layer so the archive now treats **crate-vs-foreign-package identity + generated-binding provenance + runtime/init/threading/lifetime truth + shipped/install truth + support/docs truth** as a ranked seam instead of leaving Rust mixed-language products split across wheel/prebuild/package metadata, generated bindings, C++ bridge handoffs, component manifests, and README folklore
- Strategy: clarified that the worthy contribution here is not another binding generator, upload wrapper, universal IDL, or “best interop framework” chooser, but a thin `cargo poly-product` / `polyglot-product-pack/v0` layer above **Host Package + FFI Boundary + Wasm Component + Release Truth + Support Envelope**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future polyglot-productization revisions keep Cargo package identity, foreign package identity, generated-binding provenance, runtime/threading/lifetime truth, shipped/install receipts, and downstream support/release conclusions distinct instead of collapsing them into one fake “interop supported” story

## New (rev0267)
- Gap: `gaps/reflection-transition-lane-comparison-macro-burden-and-core-reflection-migration.md`
- Epic: `proposals/epic-reflection-transition-stack.md`
- Design refresh: `design/reflection-transition-stack.md`, `design/reflection-transition-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Reflection Transition Stack** proposal layer so the archive now treats **macro-burden-aware reflection lane comparison and migration** as a ranked seam instead of leaving it split across proc-macro folklore, runtime reflection crates, inspect-only observability lanes, schema/shape exports, and future core-reflection anticipation
- Strategy: clarified that the worthy contribution here is not another runtime reflection crate, derive helper, registry macro, or universal reflect trait, but a thin `cargo reflect-transition` / `reflection-transition-pack/v0` layer above **Macro Workflow + Reflection Surface + Const Surface**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future reflection-transition-epic revisions keep compared lane identity, current burden, target-lane posture, adapter dependencies, watch/wait outcomes, and downstream summaries distinct instead of collapsing them into one fake reflection-maturity story

## New (rev0266)
- Gap: `gaps/dependency-review-effect-capability-and-intake-truth.md`
- Added synthesis design: `design/dependency-review-stack.md`
- Added execution design: `design/dependency-review-pilot-program.md`
- Epic: `proposals/epic-dependency-review-stack.md`
- Frontier/priority refresh: promoted an explicit **Dependency Review Stack** (**Trust Decision Stack + effect-audit imports + Runtime Capability Kit + artifact-linked inventory**) so the archive now treats **dependency intake and upgrade review** as a ranked seam instead of leaving it split across crates.io advisory tabs, `cargo vet` audits, Cargo Scan research artifacts, Capslock-style capability analysis, and binary-linkage tools
- Strategy: clarified that the worthy contribution here is not another crate score, malware dashboard, or `cargo vet` replacement, but a thin `cargo dep-review` / `dependency-review-pack/v0` layer above trust/effect/capability/artifact evidence
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future dependency-review revisions keep reviewed subject identity, imported trust/effect/capability/artifact evidence, and bounded consumer verdicts in an explicit import relationship instead of collapsing them into one fake dependency-safety story

## New (rev0265)
- Gap: `gaps/developer-feedback-loops-build-debug-iteration-and-honest-session-handoffs.md`
- Added synthesis design: `design/feedback-loop-stack.md`
- Added execution design: `design/feedback-loop-pilot-program.md`
- Epic: `proposals/epic-feedback-loop-stack.md`
- Frontier/priority refresh: promoted an explicit **Feedback Loop Stack** (**Build-State Evidence Stack + Debuggability Stack**, with bounded Edit Workflow / Semantic Context imports) so the archive now treats **session-shaped build/debug iteration truth** as a ranked seam instead of leaving Rust inner-loop pain split across `cargo report` sessions, rust-analyzer target-dir workarounds, debug-info tradeoffs, debugger tuple folklore, and issue archaeology
- Strategy: clarified that the worthy contribution here is not another IDE backend, daemon, dashboard, or assistant wrapper, but a thin `cargo innerloop` / `feedback-loop-pack/v0` layer above Build-State Evidence + Debuggability
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future feedback-loop revisions keep session identity, build-state evidence, debug evidence, and consumer summaries in an explicit import relationship instead of collapsing them into one fake developer-experience story

## New (rev0264)
- Gap: `gaps/async-reliability-lifecycle-replay-simulation-and-consumer-handoffs.md`
- Epic: `proposals/epic-async-reliability-stack.md`
- Deepened `design/async-reliability-stack.md` so the seam now more explicitly treats **runtime-shaped lifecycle policy + replay posture + exploration semantics + bounded consumer handoffs** as one ranked execution band rather than only a strong stack note
- Design refresh: `design/async-reliability-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Async Reliability Stack** proposal layer so the archive now treats **shutdown truth + replay truth + deterministic exploration truth** as a ranked seam instead of leaving Rust async reliability split across runtime helpers, simulator-specific seeds, flaky issue repros, and debugger folklore
- Strategy: clarified that the worthy contribution here is not another runtime wrapper, deterministic scheduler, or async dashboard, but a thin `cargo asyncdoctor` / `async-reliability-pack/v0` layer above **Async Lifecycle + Replay + DST**
- Hygiene: repaired `STRATEGIC_FRONTIER.md`’s stale revision label and strengthened `meta/AMNESIA_RESISTORS.md` so future async-reliability revisions keep runtime/lifecycle truth, replay truth, exploration truth, and consumer imports in an explicit import relationship instead of collapsing them into one fake async health story

## New (rev0263)
- Gap: `gaps/canonical-learning-maintainer-authored-teaching-and-derived-consumer-boundaries.md`
- Added execution design: `design/canonical-learning-pilot-program.md`
- Epic: `proposals/epic-canonical-learning-stack.md`
- Design refresh: `design/canonical-learning-stack.md`, `design/canonical-learning-consumer-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Canonical Learning Stack** proposal layer so the archive now treats **maintainer-authored teaching truth + validation evidence + bounded derived consumers** as a ranked seam instead of leaving Rust learning split across rustdoc pages, mdBook tests, docs.rs metadata, compile-fail fixtures, and assistant/editor overlays
- Strategy: clarified that the worthy contribution here is not another docs portal, UI layer, or assistant-shaped index, but a thin `cargo learncanon` / `canonical-learning-pack/v0` layer above **DocProof + Compile Guidance + bounded consumer handoffs**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future canonical-learning-epic revisions keep canonical authoring, validation evidence, docs-host posture, derived overlays, and downstream authority in an explicit import relationship instead of collapsing them into one fake smart-docs surface

## New (rev0262)
- Epic: `proposals/epic-migration-truth-stack.md`
- Deepened `design/migration-truth-stack.md` so the seam now more explicitly treats **source state + destination intent + edit/application handoff + compatibility/support/docs/downstream evidence + archaeology consumers** as one ranked execution band rather than only a strong stack note
- Design refresh: `design/migration-pilot-program.md`, `gaps/upgrade-choreography-and-reviewable-migrations.md`
- Frontier/priority refresh: promoted an explicit **Migration Truth Stack** proposal layer so the archive now treats **change-program continuity** as a ranked seam instead of leaving Rust migrations split across `cargo fix` suggestions, `rust-version` ratchets, semver checks, docs/support follow-through, and maintainer memory
- Strategy: clarified that the worthy contribution here is not another upgrade bot, dependency-bump daemon, or friendly `cargo fix` wrapper, but a thin `cargo migrate` / `migration-pack/v0` layer above **Migration Kit + imported edit/API/support/docs/downstream evidence**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future migration-truth-stack revisions keep source/destination state, executed scope, imported evidence, and archaeology handoffs in an explicit import relationship instead of collapsing them into one fake upgrade result

## New (rev0261)
- Epic: `proposals/epic-lint-governance-stack.md`
- Deepened `design/lint-governance-stack.md` so the seam now more explicitly treats **authored guidance + selected policy locks + observed findings/debt + fix/application handoff + bounded consumer verdicts** as one ranked execution band rather than only a strong stack note
- Design refresh: `design/lint-governance-pilot-program.md`, `gaps/lint-profiles-baselines-and-fixpacks.md`
- Frontier/priority refresh: promoted an explicit **Lint Governance Stack** proposal layer so the archive now treats **policy/baseline/fix continuity** as a ranked seam instead of leaving lint meaning split across manifest tables, console logs, Clippy config files, autofix suggestions, and CI glue
- Strategy: clarified that the worthy contribution here is not another Clippy preset, lint dashboard, or autofix wrapper, but a thin `cargo lint-governance` / `lint-governance-pack/v0` layer above **Compile Guidance + Lint Baseline + Edit Workflow + Policy**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future lint-governance revisions keep authored guidance, selected policy, observed findings, fix/application receipts, and downstream conclusions in an explicit import relationship instead of collapsing them into one fake lint status

## New (rev0260)
- Epic: `proposals/epic-resolution-strategy-stack.md`
- Deepened `design/resolution-strategy-stack.md` so the seam now more explicitly treats **objective profiles + chosen-graph/feature imports + historical/publish-time uncertainty + accepted tradeoffs + bounded downstream handoffs** as one ranked execution band rather than only a strong stack note
- Design refresh: `design/resolution-strategy-pilot-program.md`, `gaps/resolution-strategy-objectives-and-reviewable-lockfile-decisions.md`
- Frontier/priority refresh: promoted an explicit **Resolution Strategy Stack** proposal layer so the archive now treats **reviewable dependency objective/tradeoff truth** as a ranked seam instead of leaving it split across lockfiles, CI flags, MSRV heuristics, publish-time experiments, and maintainer memory
- Strategy: clarified that the worthy contribution here is not another dependency dashboard, solver fork, or policy engine, but a thin `cargo resolve-plan` / `resolution-strategy-pack/v0` layer above **Resolution Strategy Kit + Dependency Control + downstream consumer handoffs**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future resolution-strategy revisions keep objective profiles, chosen-graph imports, candidate comparisons, accepted tradeoffs, historical assumptions, and downstream verdicts in an explicit import relationship instead of collapsing them into one fake dependency decision

## New (rev0259)
- Gap: `gaps/repo-composition-discovery-package-selection-and-scope-continuity.md`
- Epic: `proposals/epic-repo-composition-stack.md`
- Deepened `design/repo-composition-stack.md` so the seam now more explicitly treats **discovery roots + config/include layers + workspace governance + package-selection scope + bounded downstream handoffs** as one ranked execution band rather than only a strong stack note
- Design refresh: `design/repo-composition-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Repo Composition Stack** proposal layer so the archive now treats **discovery + selection + scope handoff continuity** as a ranked seam instead of leaving Rust repo meaning split across parent-file discovery, `default-members`, `cwd`, `cargo metadata`, CI shell glue, and editor guesses
- Strategy: clarified that the worthy contribution here is not another monorepo manager, repo manifest, or CI generator, but a thin `cargo repo-compose` / `repo-compose-pack/v0` layer above **Workspace Governance + Config Set + Build Interop**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future repo-composition revisions keep discovery roots, config/include layers, workspace governance, scope-selection causes, and consumer imports in an explicit import relationship instead of collapsing them into one fake repo state

## New (rev0258)
- Epic: `proposals/epic-dependency-control-stack.md`
- Deepened `design/dependency-control-stack.md` so the seam now more explicitly treats **chosen-graph facts + activation/why-chain facts + selection-policy posture + public/private-boundary handoffs + bounded downstream imports** as one ranked execution band rather than only a strong stack note
- Design refresh: `design/dependency-control-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Dependency Control Stack** proposal layer so the archive now treats **selection truth + activation truth + policy truth + boundary handoff** as a ranked seam instead of leaving Rust dependency meaning split across `cargo tree`, feature flags, workspace-selection folklore, MSRV notes, and downstream API/policy guesses
- Strategy: clarified that the worthy contribution here is not another graph viewer, feature dashboard, or solver fork, but a thin `cargo dependency-control` / `dependency-control-pack/v0` layer above **Resolution Doctor + Feature Kit + public/private-boundary imports**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future dependency-control revisions keep chosen graph, activation traces, selection policy, and boundary/API conclusions in an explicit import relationship instead of collapsing them into one fake dependency verdict

## New (rev0257)
- Epic: `proposals/epic-manifest-truth-stack.md`
- Deepened `design/manifest-truth-stack.md` so the seam now more explicitly treats **authored fields + inherited/discovered context + packaged-manifest rewrites + frontmatter defaults + consumer-import lossiness + bounded downstream handoffs** as one ranked execution band rather than only a strong stack note
- Design refresh: `design/manifest-truth-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Manifest Truth Stack** proposal layer so the archive now treats **authored-vs-packaged-vs-consumer manifest continuity** as a ranked seam instead of leaving Rust manifest meaning split across raw `Cargo.toml` diffs, `cargo metadata`, `cargo info`, package tarballs, workspace inheritance, and single-file-script folklore
- Strategy: clarified that the worthy contribution here is not another formatter, manifest editor, registry page, or metadata wrapper, but a thin `cargo manifest-truth` / `manifest-pack/v0` layer above **Manifest Surface + Repo Composition + ScriptKit + Dependency Control + Publisher & Source Identity**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future manifest revisions keep authored, inherited/discovered, packaged, and consumer-imported truth in an explicit import relationship instead of collapsing them into one fake canonical manifest

## New (rev0256)
- Gap: `gaps/publisher-source-identity-authority-claims-and-source-posture-continuity.md`
- Epic: `proposals/epic-publisher-source-identity-stack.md`
- Deepened `design/publisher-source-identity-stack.md` so the seam now more explicitly treats **claim posture + publish-authority posture + source/auth posture + best-effort package/VCS hints + bounded downstream handoffs** as one ranked execution band rather than only a strong stack note
- Design refresh: `design/publisher-source-identity-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Publisher & Source Identity Stack** proposal layer so the archive now treats **owner/team/issuer authority + registry/replacement identity + namespace/family claims + package/install handoffs** as a ranked seam instead of leaving Rust identity truth split across crates.io settings, Cargo config, namespace debates, repository links, and downstream badge systems
- Strategy: clarified that the worthy contribution here is not an org-verification badge, one-true namespace scheme, or stealth trust-score surface, but a thin `cargo source` / `cargo publisher` / `publisher-source-pack/v0` layer above **Org Identity & Registry UX + Trust Signals + Package Admission + Distribution Contract**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future identity revisions keep owners, authors, trusted-publisher subjects, source posture, family claims, and downstream trust/install conclusions in an explicit import relationship instead of collapsing them into one fake package identity

## New (rev0255)
- Epic: `proposals/epic-test-execution-evidence-stack.md`
- Deepened `design/test-execution-evidence-stack.md` so the seam now more explicitly treats **harness capability/discovery imports + runner-semantic run truth + config-bound execution identity + specialized attachment continuity + bounded consumer handoffs** as one ranked execution band rather than only a strong stack note
- Frontier/priority refresh: promoted an explicit **Test Execution Evidence Stack** proposal layer so the archive now treats **harness/run/config/attachment composition** as a ranked seam instead of leaving Rust testing truth split across libtest JSON experiments, nextest-native recordings, JUnit bridges, CI job names, and tool-specific artifact stores
- Strategy: clarified that the worthy contribution here is not another runner wrapper, XML/JUnit normalizer, or giant test dashboard, but a thin `cargo test-execution` / `test-exec-pack/v0` layer above **Harness Protocol + Test Run Evidence + Config Set + specialized attachment imports**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future testing-stack revisions keep harness truth, runner-native recordings, raw outputs, config ids, and downstream verdicts in an explicit import relationship instead of collapsing them into one fake universal test report

## New (rev0254)
- Epic: `proposals/epic-safety-critical-evidence-stack.md`
- Deepened `design/safety-critical-evidence-stack.md` so the seam now more explicitly treats **unsafe-contract authority + criterion-aware coverage + sanitizer/runtime-lane truth + proof assumptions + bounded qualification handoffs** as one ranked execution band rather than only a strong stack note
- Design refresh: `design/safety-critical-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Safety-Critical Evidence Stack** proposal layer so the archive now treats **high-assurance evidence composition + pilot-slice discipline + bounded audit/qualification handoffs** as a ranked seam instead of leaving it split across contracts prose, coverage percentages, sanitizer jobs, and proof-tool islands
- Strategy: clarified that the worthy contribution here is not another checklist, verifier wrapper, or fake certification platform, but a thin `cargo safety-critical` / `safety-critical-pack/v0` layer above **Safety Evidence + Coverage Evidence + Sanitizer Battery + Formal Verification**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future safety-critical-stack revisions keep safety-case authority, coverage criteria, dynamic-analysis lanes, proof assumptions, and certification-facing packaging distinct instead of collapsing them into one fake assurance verdict

## New (rev0253)
- Epic: `proposals/epic-inventory-evidence-stack.md`
- Deepened `design/inventory-evidence-stack.md` so the seam now more explicitly treats **Cargo-native precursor capture + package admission imports + producer-side release attachments + consumer-side install receipts + bounded downstream handoffs** as one ranked execution band rather than only a strong synthesis note
- Design refresh: `design/inventory-evidence-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Inventory Evidence Stack** proposal layer so the archive now treats **package→release→install inventory continuity + projection/recovery lossiness + incident/policy/distro/support imports** as a ranked seam instead of leaving Rust inventory truth split across precursor files, exported SBOMs, binary scans, release attachments, and install history
- Strategy: clarified that the worthy contribution here is not another exporter wrapper, registry inventory page, or fake supply-chain dashboard, but a thin `cargo inventory-evidence` / `inventory-evidence-pack/v0` layer above **SBOM Evidence + Package Admission + Release Truth + Distribution Contract**
- Hygiene: repaired a `RESEARCH_LOG.md` top-entry revision-label typo (`rev0252` had been mislabeled as `rev0250`) and strengthened `meta/AMNESIA_RESISTORS.md` so future inventory revisions keep Cargo-native precursors and projected standards documents in an explicit source-vs-adapter relationship

## New (rev0252)
- Epic: `proposals/epic-distribution-contract-stack.md`
- Deepened `design/distribution-contract-stack.md` so the seam now explicitly treats **producer/import truth + visible catalog/selection truth + verification/fallback truth + installed-state ownership truth + downstream handoffs** as one ranked execution band rather than only a strong synthesis note
- Design refresh: `design/distribution-contract-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Distribution Contract Stack** proposal layer so the archive now treats **consumer-side candidate visibility + source-vs-prebuilt continuity + mirror/fallback behavior + ownership-aware install receipts + bounded support/policy imports** as a ranked seam instead of leaving Rust acquisition truth split across `cargo install`, prebuilt-install helpers, package-manager wrappers, mirror policy, and shell history
- Strategy: clarified that the worthy contribution here is not another installer wrapper, binary-only fast-path, or “safe install” badge, but a thin `cargo distribution-contract` / `distribution-contract-pack/v0` layer above **Release Pipeline + Signed Binaries + Airgap + acquisition receipts**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future distribution-contract revisions keep acquisition receipts separate from managed-content ownership and uninstall/update scope instead of flattening them into one vague “installed here” claim

## New (rev0251)
- Added execution design: `design/conformance-traceability-pilot-program.md`
- Epic: `proposals/epic-conformance-traceability-stack.md`
- Deepened `design/conformance-traceability-stack.md` so the seam now explicitly treats **stable text + experimental text + vector/capability truth + acceptance-diff imports + assurance/release handoffs** as one ranked execution band rather than only a synthesis note
- Frontier/priority refresh: promoted an explicit **Conformance Traceability Stack** proposal layer so the archive now treats **paragraph-linked source truth + lane-aware execution reality + safety/qualification imports + bounded archaeology handoffs** as a ranked seam instead of leaving it split across spec prose, compiletest-style suites, acceptance caveats, and bespoke assurance binders
- Strategy: clarified that the worthy contribution here is not a compiletest clone, certification badge, or one mega qualification schema, but a thin `cargo traceability` / `traceability-pack/v0` layer above **Spec Conformance + Acceptance Surface + Safety-Critical Evidence**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future conformance-stack revisions do not flatten stable text, experimental text, executable vectors, acceptance diffs, and assurance conclusions into one fake “Rust conforms” story

## New (rev0250)
- Gap: `gaps/build-state-topology-impact-and-diagnosis-continuity.md`
- Epic: `proposals/epic-build-state-evidence-stack.md`
- Frontier/priority refresh: promoted an explicit **Build-State Evidence Stack** proposal layer so the archive now treats **build-state topology/reuse truth + change-impact/rebuild-scope truth + workflow-aware diagnosis truth + bounded consumer handoffs** as one ranked seam instead of leaving it split across timing HTML, unstable raw reports, CI cache folklore, and support guesswork
- Strategy: clarified that the worthy contribution here is not another cache wrapper, timings dashboard, remote-cache product, or one-score build oracle, but a thin `cargo build-state` / `build-state-evidence-pack/v0` layer above **Build Cache + Change Impact + Build Doctor** with `cargo report` and raw traces as explicit imports
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future high-ranked stack seams with both a synthesis design and pilot program do not linger without a proposal-layer file while adjacent leaves keep proliferating

## New (rev0249)
- Gap: `gaps/trust-decisions-evidence-policy-handoff-and-thin-views.md`
- Added execution design: `design/trust-decision-pilot-program.md`
- Epic: `proposals/epic-trust-decision-stack.md`
- Deepened `design/trust-decision-stack.md` so the seam now explicitly treats **evidence import + policy decision + waiver/inconclusive posture + bounded thin-view consumers** as one execution band rather than only a stack note
- Frontier/priority refresh: clarified that the **Policy / Trust / SBOM / Lifecycle** band now has an explicit **Trust Decision Stack** rollout above Trust Signals + Policy, centered on **lockfile evidence-to-policy continuity, scope-sensitive trust review, freshness/cooldown posture, package/release attachment, and thin consumer views**
- Strategy: clarified that the worthy contribution here is not another crate-score dashboard, registry verdict engine, or cargo-vet replacement, but a thin `cargo trust-decision` / `trust-decision-pack/v0` composition layer above **Trust Signals + Policy** with lifecycle/name-risk/inventory/signing as explicit imports
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future frontier-promoted stack notes either carry an explicit pilot/epic pair or say they remain note-only, preventing silent drift between named seams and executable archive layers

## New (rev0248)
- Added synthesis design: `design/release-truth-stack.md`
- Added execution design: `design/release-truth-pilot-program.md`
- Epic: `proposals/epic-release-truth-stack.md`
- Frontier/priority refresh: promoted an explicit **Release Truth Stack** so the archive now treats **package publish identity + artifact publication truth + attached signature/rebuild/inventory evidence + bounded downstream handoffs** as a ranked seam instead of leaving Rust release truth split across crates.io pages, CI logs, dist manifests, signature sidecars, and host-specific release metadata
- Strategy: clarified that the worthy contribution here is not another release wrapper, installer tool, provenance badge, or GitHub-action bundle, but a thin `cargo release-truth` / `release-truth-pack/v0` layer above **Release Pipeline + Signed Binaries + Repro Build**, with Inventory and Distribution as explicit imports rather than hidden sublayers
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future release-truth revisions do not flatten package publish truth, producer-side artifact truth, attached verification evidence, and consumer-side install conclusions into one fake “trusted release” story

## New (rev0247)
- Gap: `gaps/starter-repos-template-provenance-and-freshness.md`
- Added design: `design/starter-pack-kit.md`
- Added execution design: `design/starter-pack-pilot-program.md`
- Epic: `proposals/epic-starter-pack-kit.md`
- Frontier/priority refresh: promoted an explicit **Starter Pack Kit** so the archive now treats **starter subject + imported lane/workenv/policy truth + rendered-layout ownership + overlay posture + freshness/refresh evidence** as a ranked seam instead of leaving Rust starter repos split across `cargo new`, `cargo-generate`, framework quickstarts, copied CI files, and README boilerplate
- Strategy: clarified that the worthy contribution here is not another template engine, framework bootstrapper, or hidden starter catalog, but a thin `cargo starter` / `starter-pack/v0` layer above **Atlas + Adoption Decision + Workspace Environment + Productization/Policy/Support imports**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future starter-pack revisions do not flatten recommendation imports, generated working-tree ownership, local overlays, freshness state, and derived docs/assistant contexts into one fake “official starter repo” story

## New (rev0246)
- Gap: `gaps/adoption-decisions-reviewable-stack-selection-and-freshness.md`
- Restored root copies: `design/adoption-decision-stack.md`, `design/adoption-decision-pilot-program.md`, `proposals/epic-adoption-decision-stack.md`
- Deepened the Adoption Decision seam so it now more explicitly treats **project question + candidate lanes + trust/maintenance/docs/local-fit imports + alternatives + freshness/recheck state + bounded assistant rendering** as the missing artifact family
- Frontier/priority refresh: clarified that the **Adoption Decision Stack** remains one of the strongest ecosystem-shaping seams because Rust now explicitly says users need help getting oriented in crates.io while docs remain canonical and LLM/editor tooling rises
- Strategy: clarified that the worthy contribution here is not another blessed-crates page, hidden recommender, or AI chooser, but a thin `cargo adopt` / `adoption-pack/v0` layer above **Atlas + Commons + Trust + Maintenance + Canonical Learning + Semantic Context**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future archive revisions keep root/archive parity and do not leave frontier-linked files present only in the mirrored archive copy

## New (rev0245)
- Gap: `gaps/sdk-products-generated-clients-clis-mocks-and-support-contracts.md`
- Added design: `design/sdk-surface-kit.md`
- Added synthesis design: `design/sdk-productization-stack.md`
- Added execution design: `design/sdk-productization-pilot-program.md`
- Epic: `proposals/epic-sdk-productization-stack.md`
- Frontier/priority refresh: promoted an explicit **SDK Productization Stack** so the archive now treats **SDK family identity + upstream contract provenance + auth/config/runtime truth + release/support truth + bounded consumer handoffs** as a ranked seam instead of leaving Rust SDKs split across generator templates, builder code, checked-in generated output, CLI companions, and README prose
- Strategy: clarified that the worthy contribution here is not another OpenAPI/Smithy/protobuf generator fork, transport wrapper, or auth helper, but a thin `cargo sdkcheck` / `sdk-pack/v0` layer above **SDK Surface + Schema Contract + Identity Productization + Runtime Settings + Library/Release/Support imports**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future SDK-productization revisions do not flatten source-contract truth, SDK family truth, auth/config activation, shipped artifact truth, and support conclusions into one fake “SDK support” story

## New (rev0244)
- Gap: `gaps/workspace-environments-onboarding-and-agent-safe-dev-contracts.md`
- Added synthesis design: `design/workspace-environment-stack.md`
- Epic: `proposals/epic-workspace-environment-stack.md`
- Frontier/priority refresh: promoted an explicit **Workspace Environment Stack** so the archive now treats **workspace/discovery truth + declared environment intent + realization-substrate truth + credential posture + bounded human/editor/CI/agent handoffs** as a ranked seam instead of leaving Rust setup split across `rust-toolchain.toml`, `.cargo/config.toml`, rust-analyzer overrides, devcontainer/Nix files, CI bootstrap scripts, and README prose
- Strategy: clarified that the worthy contribution here is not a universal environment manager, secret vault, or one-true-substrate migration, but a thin `cargo workenv` / `workenv-pack/v0` layer above **Tooling Contract + Toolchain Productization + Native Dependency + Runtime Settings + Credentials**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future workspace-environment revisions do not flatten discovery/scope, declared intent, realization substrate, secret posture, observed state, and downstream handoff authority into one fake “setup works” story

## New (rev0243)
- Epic: `proposals/epic-maintenance-reality-stack.md`
- Deepened `design/maintenance-reality-stack.md` and `design/stewardship-pilot-program.md` so the maintenance seam now has an explicit proposal layer and a small artifact family around **subject + lifecycle/stewardship imports + visibility posture + transition diff + consumer handoff** rather than only a synthesis note and pilot track
- Frontier/priority refresh: clarified that the **Maintenance Reality Stack** now has a concrete candidate epic centered on **declared lifecycle truth + observed stewardship truth + visibility/routing posture + explicit help requests + bounded consumer handoffs**
- Strategy: clarified that the worthy contribution here is not a public maintainer dashboard, health score, abandonment oracle, or hidden fund-allocation engine, but a thin `cargo maintenance-reality` / `maintenance-reality-pack/v0` layer above **Lifecycle Ledger + Stewardship Ops**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future maintenance-reality epic revisions do not flatten lifecycle/stewardship imports, visibility posture, help-routing, keystone/adoption/fund conclusions, and consumer authority into one fake “project health” story

## New (rev0242)
- Epic: `proposals/epic-package-admission-stack.md`
- Deepened `design/package-admission-stack.md` and `design/package-admission-pilot-program.md` so the publish-review seam now has an explicit proposal layer and a small artifact family around **package subject + chosen graph + public exposure + decision brief + release handoff** rather than only a synthesis note and pilot track
- Frontier/priority refresh: clarified that the **Package Admission Stack** now has a concrete candidate epic centered on **graph truth + exposure truth + inventory/trust imports + policy decisions + bounded package-to-release handoff**
- Strategy: clarified that the worthy contribution here is not a secure-publish wrapper, registry risk score, moderation surrogate, or binary-release umbrella, but a thin `cargo package-admission` / `package-admission-pack/v0` layer above **Dependency Control + Public API + SBOM Evidence + Trust Signals + Policy**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future package-admission epic revisions do not flatten package graph/exposure truth, inventory/trust imports, policy decisions, release handoff, and downstream consumer authority into one fake “safe to publish” story

## New (rev0241)
- Epic: `proposals/epic-tooling-contract-stack.md`
- Deepened `design/tooling-contract-stack.md` and `design/tooling-contract-pilot-program.md` so the tooling seam now has an explicit proposal layer and a small artifact family around **subject + scope + plan + evidence + consumer handoff** rather than only a synthesis note and pilot track
- Frontier/priority refresh: clarified that the **Tooling Contract Stack** now has a concrete candidate epic centered on **discovery-boundary truth + selected-scope truth + graph/plan truth + imported-evidence posture + bounded adapter/handoff summaries**
- Strategy: clarified that the worthy contribution here is not a Cargo daemon, BSP-only bridge, target-dir scraper, or universal monorepo platform, but a thin `cargo tooling-contract` / `tooling-contract-pack/v0` layer above **Repo Composition + Build Interop + Build-State Evidence**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future tooling-contract epic revisions do not flatten stable contract surfaces, experimental report imports, adapter lossiness, and downstream consumer authority into one fake “tooling truth” story

## New (rev0240)
- Epic: `proposals/epic-debuggability-stack.md`
- Deepened `design/debuggability-stack.md` and `design/debuggability-pilot-program.md` so the debuggability seam now has an explicit proposal layer framing it as a worthy ecosystem contribution rather than only a frontier note and pilot track
- Frontier/priority refresh: clarified that the **Debuggability Stack** now has a concrete candidate epic centered on **failure-identity truth + runtime-correlation truth + debugger tuple truth + replay/handoff truth + bounded consumer summaries**
- Strategy: clarified that the worthy contribution here is not another IDE plugin, debugger wrapper, tracing bootstrap, or hosted debugging portal, but a thin `cargo debuggability` / `debuggability-pack/v0` layer above **Diagnostic Surface + Observability + Debugger Experience**, with Replay/Incident as imports rather than hidden defaults
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future debuggability-epic revisions do not flatten native debugger support, runtime-side async inspection, diagnostic/telemetry evidence, and downstream support renderings into one fake “debugging parity” story

## New (rev0239)
- Epic: `proposals/epic-service-productization-stack.md`
- Deepened `design/service-productization-stack.md` and `design/service-productization-pilot-program.md` so the service seam now has an explicit proposal layer framing it as a worthy ecosystem contribution rather than only a frontier note and pilot track
- Frontier/priority refresh: clarified that the **Service Productization Stack** now has a concrete candidate epic centered on **service boundary truth + config truth + telemetry/runtime evidence + shutdown/background-work truth + support/docs truth + bounded consumer handoffs**
- Strategy: clarified that the worthy contribution here is not another web framework, service template, control plane, or Rust Spring Boot fantasy, but a thin `cargo service product` / `service-product-pack/v0` layer above **Service Surface + Runtime Settings + Observability + Async Reliability + Background Work + Support Envelope**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future service-productization epic revisions do not flatten service-surface truth, settings truth, telemetry/runtime evidence, shutdown/background-work truth, support/docs posture, and downstream consumer authority into one fake “service readiness” story

## New (rev0238)
- Epic: `proposals/epic-client-productization-stack.md`
- Deepened `design/client-productization-stack.md` and `design/client-productization-pilot-program.md` so the client-app seam now has an explicit proposal layer framing it as a worthy ecosystem contribution rather than only a frontier note and pilot track
- Frontier/priority refresh: clarified that the **Client Productization Stack** now has a concrete candidate epic centered on **app/package/capability truth + support/docs truth + accessibility truth + locale/runtime-data truth + distribution/install truth + bounded consumer handoffs**
- Strategy: clarified that the worthy contribution here is not another GUI toolkit, shell, bridge generator, or store/deploy wrapper, but a thin `cargo app product` / `client-product-pack/v0` layer above **Client App Surface + A11yKit + Localization Surface + Distribution Contract + Support Envelope**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future client-productization epic revisions do not flatten app/package/capability truth, support/docs truth, accessibility evidence, locale/runtime-data posture, install reality, and downstream consumer authority into one fake “app readiness” story

## New (rev0237)
- Gap: `gaps/compatibility-claims-platform-debugger-and-acceptance-contracts.md`
- Added synthesis design: `design/compatibility-claims-stack.md`
- Epic: `proposals/epic-compatibility-claims-stack.md`
- Design refresh: clarified in `design/compatibility-claims-pilot-program.md` that Support Envelope and Acceptance Surface are the core owners while debugger tuple truth remains an imported input from the Debuggability Stack
- Frontier/priority refresh: promoted an explicit **Compatibility Claims Stack** so the archive now treats **platform/runtime support truth + debugger tuple truth + advanced-pattern acceptance truth + diff/consumer truth** as a ranked seam instead of leaving compatibility scattered across target-tier docs, docs.rs defaults, debugger setup lore, `trybuild` fixtures, and release-note caveats
- Strategy: clarified that the worthy contribution here is not another matrix page, UI-test harness, or compatibility badge, but a thin `cargo compat` / `compat-pack/v0` layer that imports Support Envelope, Debuggability, and Acceptance Surface artifacts without flattening them
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future compatibility-claims revisions do not flatten platform support, debugger tuple support, acceptance-lane truth, declared-vs-observed evidence, and downstream consumer conclusions into one fake “supported” verdict

## New (rev0236)
- Epic: `proposals/epic-compiler-extensibility-stack.md`
- Deepened `design/compiler-extensibility-stack.md` and `design/compiler-extensibility-pilot-program.md` so the seam now has an explicit proposal layer framing it as a worthy ecosystem contribution rather than only a frontier note and pilot track
- Frontier/priority refresh: clarified that the **Compiler Extensibility Stack** now has a concrete candidate epic centered on **compiler attachment truth + subject/configuration truth + capability/stability truth + result-family truth + bounded consumer handoffs**
- Strategy: clarified that the worthy contribution here is not a universal plugin ABI, a Cargo-merger fantasy, or another nightly-only analyzer, but a thin `cargo toolcontract` / `tool-pack` layer above **MIR Analysis + Lint Governance + Compile Guidance + Conformance Traceability**
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future compiler-extensibility epic revisions do not flatten companion-tool scope, possible upstream integration, lane-specific stability, and consumer authority into one fake “official tool” story

## New (rev0235)
- Gap: `gaps/compiler-extensibility-analysis-lints-and-reviewable-tool-contracts.md`
- Added synthesis design: `design/compiler-extensibility-stack.md`
- Added execution design: `design/compiler-extensibility-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Compiler Extensibility Stack** so the archive now treats **compiler attachment truth + subject/configuration truth + capability/stability truth + result/handoff truth + consumer-proof imports** as a ranked seam instead of leaving Rust compiler-aware tooling split across nightly flags, rustdoc/MIR exporter lore, Clippy config, bespoke plugin CLIs, and issue-thread folklore
- Strategy: clarified that the worthy contribution here is not one universal compiler-plugin ABI, another nightly-only analyzer, or a Cargo-merger fantasy, but a portable contract layer above **MIR Analysis + Lint Governance + Compile Guidance + Conformance Traceability** that lets compiler-attached tools become reviewable ecosystem products
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future compiler-extensibility revisions do not flatten attachment lane, analysis subject/configuration, capability/stability posture, emitted findings/guidance/assurance artifacts, and downstream CI/editor/release/safety conclusions into one fake “tool support” story

## New (rev0234)
- Gap: `gaps/keystone-projects-critical-infrastructure-and-institutional-stewardship-contracts.md`
- Added synthesis design: `design/keystone-stewardship-stack.md`
- Added execution design: `design/keystone-stewardship-pilot-program.md`
- Epic: `proposals/epic-keystone-stewardship-stack.md`
- Frontier/priority refresh: promoted an explicit **Keystone Stewardship Stack** so the archive now treats **criticality truth + institutional-support truth + continuity/obligation truth + transition truth + consumer-import truth** as a ranked seam instead of leaving ecosystem-keystone decisions split across blog posts, issue-thread folklore, funding announcements, and private spreadsheets
- Strategy: clarified that the worthy contribution here is not a popularity leaderboard, blessed-crates canon, or private governance database, but a portable keystone-stewardship substrate that keeps **criticality + stewardship + institutional backing + continuity + consumer imports** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future keystone-stewardship revisions do not flatten keystone status, trust/product/maintenance imports, institutional support, continuity risks, and downstream funding/adoption conclusions into one fake “critical crate” story

## New (rev0233)
- Added execution design: `design/runtime-capability-pilot-program.md`
- Deepened `design/runtime-capability-kit.md` and `proposals/epic-runtime-capability-kit.md` so runtime-authority work now treats **declared capability truth + analyzer-backed inference + generated-enforcement candidates + enacted sandbox truth + checked runtime evidence** as separate layers instead of one permissions blob
- Frontier/priority refresh: clarified that **Runtime Capability Kit** is now concrete enough to advance through a ranked pilot program centered on service inference, declaration reconciliation, generated seccomp/policy candidates, framework attachment, and policy/release consumers
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future runtime-capability revisions do not flatten maintainer declarations, `cargo-capslock` findings, generated seccomp/Tauri/WASI/container artifacts, deployed enforcement, and observed deny/allow behavior into one fake least-privilege story

## New (rev0232)
- Added epic: `proposals/epic-adoption-decision-stack.md`
- Frontier/priority refresh: clarified that the **Adoption Decision Stack** is now concrete enough to pitch as a worthy contribution in its own right, not just as a seam adjacent to Atlas, Trust, Maintenance, Canonical Learning, and Semantic Context
- Strategy: clarified that the worthy contribution here is not another blessed-crates page, hidden chooser, or AI wrapper, but a thin adoption-brief/check/diff pack that imports **lane truth + trust/maintenance truth + docs/support truth + local-fit truth** without collapsing them into one fake verdict
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future adoption-decision revisions do not flatten the project question, imported evidence, recommendation, alternatives, freshness/check state, and assistant rendering into one fake “best stack” artifact

## New (rev0231)
- Added synthesis design: `design/adoption-decision-stack.md`
- Added execution design: `design/adoption-decision-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Adoption Decision Stack** so the archive now treats **project-scoped selection questions + lane/interop truth + trust/maintenance truth + canonical docs/guidance + local semantic-fit truth** as a ranked seam instead of leaving Rust stack choices split across blessed-crates pages, README prestige, issue-thread folklore, and ungrounded assistant answers
- Strategy: clarified that the worthy contribution here is not another blessed-crates page, crate score, hidden recommender, or AI wrapper, but a thin reviewable adoption-brief layer above Atlas, Trust Decision, Maintenance Reality, Canonical Learning, and Semantic Context
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future adoption-decision revisions do not flatten curator guidance, trust/policy inputs, maintenance reality, docs authority, and local semantic-fit evidence into one fake “best stack” verdict

## New (rev0230)
- Gap: `gaps/toolchain-variants-sysroots-cross-builds-and-sanitizer-support-contracts.md`
- Added synthesis design: `design/toolchain-productization-stack.md`
- Added epic: `proposals/epic-toolchain-productization-stack.md`
- Frontier/priority refresh: promoted an explicit **Toolchain Productization Stack** so the archive now treats **provisioning truth + stdlib/sysroot truth + activation/reuse truth + runtime-analysis truth** as a ranked seam instead of leaving Rust toolchain variants split across rustup state, `build-std` flags, target JSON files, linker setup, sanitizer jobs, and CI-cache folklore
- Strategy: clarified that the worthy contribution here is not another `build-std` wrapper, cross-build helper, or org-local cache, but a portable boring-toolchain substrate that keeps **provisioning truth + stdlib truth + activation truth + runtime-analysis truth** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future toolchain-productization revisions do not flatten rustup provisioning, stdlib profile identity, activation/reuse policy, and sanitizer/hardening evidence into one fake “custom toolchain works” story

## New (rev0229)
- Gap: `gaps/event-products-brokers-delivery-replay-and-support-contracts.md`
- Added synthesis design: `design/event-productization-stack.md`
- Added execution design: `design/event-productization-pilot-program.md`
- Epic: `proposals/epic-event-productization-stack.md`
- Frontier/priority refresh: promoted an explicit **Event Productization Stack** so the archive now treats **channel/event/delivery truth + schema/evolution truth + runtime/topology activation + replay/observability evidence + support/docs truth** as a ranked seam instead of leaving Rust event products split across broker clients, schema lore, replay runbooks, and dashboard folklore
- Strategy: clarified that the worthy contribution here is not another broker client, schema registry, or queue abstraction, but a portable boring-event substrate that keeps **event truth + schema truth + activation truth + replay truth + support truth** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future event-productization revisions do not flatten channel/event/delivery truth, schema/evolution truth, runtime/topology/credential activation, replay/recovery evidence, and support/release conclusions into one fake “messaging readiness” story

## New (rev0228)
- Gap: `gaps/observability-products-telemetry-runtime-diagnostics-and-support-contracts.md`
- Added synthesis design: `design/observability-productization-stack.md`
- Added execution design: `design/observability-productization-pilot-program.md`
- Epic: `proposals/epic-observability-productization-stack.md`
- Frontier/priority refresh: promoted an explicit **Observability Productization Stack** so the archive now treats **diagnostic identity truth + signal/profile truth + activation/export truth + support/docs truth + release/incident consumer imports** as a ranked seam instead of leaving Rust observability split across subscriber layers, env vars, runtime probes, collector defaults, and README folklore
- Strategy: clarified that the worthy contribution here is not another exporter wrapper, dashboard integration, vendor bootstrap crate, or runtime probe, but a portable boring-observability substrate that keeps **diagnostic truth + telemetry truth + activation truth + support truth** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future observability-productization revisions do not flatten failure identity, signal/schema promises, exporter/sampling/redaction activation, runtime-diagnostic posture, and support/release conclusions into one fake “observability readiness” story

## New (rev0227)
- Gap: `gaps/library-crates-public-contract-release-and-support-contracts.md`
- Added synthesis design: `design/library-productization-stack.md`
- Added execution design: `design/library-productization-pilot-program.md`
- Epic: `proposals/epic-library-productization-stack.md`
- Frontier/priority refresh: promoted an explicit **Library Productization Stack** so the archive now treats **public-contract truth + feature/package truth + release/provenance truth + docs/support truth** as a ranked seam instead of leaving Rust libraries split across API diffs, manifest flags, docs.rs settings, release jobs, and README folklore
- Strategy: clarified that the worthy contribution here is not another semver wrapper, manifest linter, registry dashboard, or release bot, but a portable boring-library substrate that keeps **API truth + package truth + release truth + support truth** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future library-productization revisions do not flatten public API/semver/MSRV truth, feature/default/public-dependency posture, release/provenance identity, docs/support posture, and downstream policy/trust conclusions into one fake “crate quality” story

## New (rev0226)
- Gap: `gaps/crypto-products-keys-providers-compliance-and-support-contracts.md`
- Added synthesis design: `design/cryptography-productization-stack.md`
- Added execution design: `design/cryptography-productization-pilot-program.md`
- Epic: `proposals/epic-cryptography-productization-stack.md`
- Frontier/priority refresh: promoted an explicit **Cryptography Productization Stack** so the archive now treats **algorithm/provider/key-material/compliance truth + randomness posture + runtime/provider/key-source activation + support/docs truth** as a ranked seam instead of leaving Rust cryptography products split across provider defaults, feature flags, init code, secret wrappers, and README folklore
- Strategy: clarified that the worthy contribution here is not another primitive crate, provider wrapper, or fake universal crypto facade, but a portable boring-crypto substrate that keeps **algorithm truth + provider truth + secret/randomness truth + activation truth + support truth** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future cryptography-productization revisions do not flatten algorithm/provider truth, key-material and randomness posture, runtime/key-source activation, compliance/audit posture, and support conclusions into one fake “crypto support” story

## New (rev0225)
- Gap: `gaps/media-products-transcoding-streaming-playback-and-support-contracts.md`
- Added synthesis design: `design/media-productization-stack.md`
- Added execution design: `design/media-productization-pilot-program.md`
- Epic: `proposals/epic-media-productization-stack.md`
- Frontier/priority refresh: promoted an explicit **Media Productization Stack** so the archive now treats **operation/format/processing truth + native/plugin/backend activation + service/client attachment truth + observability/fidelity evidence + shipped/support truth** as a ranked seam instead of leaving Rust media products split across crate docs, plugin setup, pipeline strings, and README folklore
- Strategy: clarified that the worthy contribution here is not another codec matrix, transcoder wrapper, pipeline DSL, or FFmpeg-replacement fantasy, but a portable boring-media substrate that keeps **media truth + runtime truth + attachment truth + evidence/support truth** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future media-productization revisions do not flatten media semantics, runtime/plugin/native/backend activation, service/client attachments, observability/fidelity evidence, and support conclusions into one fake “media support” story

## New (rev0224)
- Gap: `gaps/model-products-artifacts-tokenizers-runtimes-and-support-contracts.md`
- Added synthesis design: `design/model-productization-stack.md`
- Added execution design: `design/model-productization-pilot-program.md`
- Epic: `proposals/epic-model-productization-stack.md`
- Frontier/priority refresh: promoted an explicit **Model Productization Stack** so the archive now treats **model/artifact/tokenizer truth + backend/offload truth + acquisition/cache/auth activation + support/docs truth** as a ranked seam instead of leaving Rust model work split across runtimes, hub caches, format variants, env flags, and README folklore
- Strategy: clarified that the worthy contribution here is not another inference runtime, weight-format winner, hub wrapper, or serving control plane, but a portable boring-model substrate that keeps **model truth + backend truth + activation truth + support truth** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future model-productization revisions do not flatten model identity, tokenizer behavior, artifact variants, backend/device/precision posture, acquisition/cache/auth activation, and support conclusions into one fake “model support” story

## New (rev0223)
- Gap: `gaps/protocol-products-transport-bridges-and-interop-support-contracts.md`
- Added synthesis design: `design/protocol-productization-stack.md`
- Added execution design: `design/protocol-productization-pilot-program.md`
- Epic: `proposals/epic-protocol-productization-stack.md`
- Frontier/priority refresh: promoted an explicit **Protocol Productization Stack** so the archive now treats **wire/bridge truth + service/schema attachment truth + runtime/security activation + conformance evidence + support/docs truth** as a ranked seam instead of leaving Rust protocol work split across transport crates, TLS builder code, interop fixtures, proxy bridges, and README folklore
- Strategy: clarified that the worthy contribution here is not another transport crate, proxy helper, or RPC framework bake-off, but a portable boring-protocol substrate that keeps **wire truth + bridge/security truth + service/schema truth + conformance truth + support truth** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future protocol-productization revisions do not flatten wire/transport truth, bridge/security posture, service/schema attachments, conformance evidence, and support conclusions into one fake “protocol readiness” story

## New (rev0222)
- Gap: `gaps/web-apps-browser-wasm-and-fullstack-productization-contracts.md`
- Added synthesis design: `design/web-productization-stack.md`
- Added execution design: `design/web-productization-pilot-program.md`
- Epic: `proposals/epic-web-productization-stack.md`
- Frontier/priority refresh: promoted an explicit **Web Productization Stack** so the archive now treats **render-mode truth + browser capability/interop truth + bundle/base-path/deploy truth + server/client split truth + support/docs truth** as a ranked seam instead of leaving Rust web work split across framework templates, bundler defaults, generated JS glue, deploy snippets, and README folklore
- Strategy: clarified that the worthy contribution here is not another frontend framework, bundler wrapper, or “Rust React” comparison page, but a portable boring-web substrate that keeps **page/render truth + browser/runtime truth + package/deploy truth + support truth** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future web-productization revisions do not flatten render mode, browser capability/interop, bundle/base-path/deploy truth, server/client split truth, and support conclusions into one fake “web readiness” story

## New (rev0221)
- Gap: `gaps/extension-hosts-galleries-capabilities-and-support-contracts.md`
- Added synthesis design: `design/extension-productization-stack.md`
- Added execution design: `design/extension-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Extension Productization Stack** so the archive now treats **host/plugin surface truth + runtime-kind/capability truth + extension package/install/update truth + compatibility/migration truth + shipped/support truth** as a ranked seam instead of leaving Rust extension work split across plugin SDK docs, permission files, gallery/install UX, and README folklore
- Strategy: clarified that the worthy contribution here is not another plugin SDK, gallery wrapper, marketplace scraper, or Wasm-only convenience layer, but a portable boring-extension substrate that keeps **host truth + capability truth + runtime truth + package/install truth + support truth** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future extension-productization revisions do not flatten host/plugin surface truth, capability/permission truth, runtime-kind truth, install/update/downgrade truth, and support/release conclusions into one fake “extension readiness” story

## New (rev0220)
- Gap: `gaps/interactive-apps-games-and-real-time-rendering-productization-contracts.md`
- Added synthesis design: `design/interactive-productization-stack.md`
- Added execution design: `design/interactive-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Interactive Productization Stack** so the archive now treats **asset/media truth + shader/backend/device truth + window/input/frame-loop truth + runtime/perf activation + shipped/support truth** as a ranked seam instead of leaving Rust interactive work split across engine docs, shader build glue, asset conventions, runtime toggles, and README folklore
- Strategy: clarified that the worthy contribution here is not another engine bake-off, renderer wrapper, asset manager, shader convenience layer, or benchmark-only graphics story, but a portable boring-interactive substrate that keeps **content truth + render truth + runtime truth + shipping/support truth** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future interactive-productization revisions do not flatten asset/media truth, shader/backend/device truth, frame/input/update truth, runtime/perf activation, and support/release conclusions into one fake “interactive readiness” story

## New (rev0219)
- Added synthesis design: `design/local-first-productization-stack.md`
- Added execution design: `design/local-first-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Local-First Productization Stack** so the archive now treats **document/sync/history/storage truth + client-vs-relay boundary truth + runtime/identity activation + recovery/export/migration truth + support/docs truth** as a ranked seam instead of leaving Rust offline/collaboration work split across CRDT engines, repo adapters, relay glue, and README folklore
- Strategy: clarified that the worthy contribution here is not another CRDT bake-off, relay wrapper, sync demo, or full-stack local-first framework, but a portable boring-local-first substrate that keeps replica truth, client/relay truth, runtime/identity truth, recovery truth, and support truth distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future local-first-productization revisions do not flatten document/sync/history/storage truth, client/relay/runtime-role truth, runtime/identity activation, recovery/migration posture, and support/release conclusions into one fake “collaboration readiness” story

## New (rev0218)
- Gap: `gaps/cli-tools-terminal-apps-and-cargo-subcommand-productization-contracts.md`
- Added synthesis design: `design/cli-productization-stack.md`
- Added execution design: `design/cli-productization-pilot-program.md`
- Epic: `proposals/epic-cli-productization-stack.md`
- Frontier/priority refresh: promoted an explicit **CLI Productization Stack** so the archive now treats **parser/help/completion/manpage truth + terminal/raw-mode/color/layout truth + runtime-setting activation + install/update receipts + support/docs truth** as a ranked seam instead of leaving Rust tools split across parser crates, terminal backends, release jobs, and README folklore
- Strategy: clarified that the worthy contribution here is not another parser framework, TUI shell, installer wrapper, self-update helper, or shell-completion-only convenience layer, but a portable boring-tool substrate that keeps **command truth + terminal truth + runtime truth + install truth + support truth** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future CLI-productization revisions do not flatten declared command surfaces, live terminal semantics, machine-vs-human output posture, runtime-setting activation, install/update truths, and support conclusions into one fake “tool readiness” story

## New (rev0217)
- Gap: `gaps/polyglot-host-packages-runtime-and-support-contracts.md`
- Design: `design/host-package-kit.md`
- Added synthesis design: `design/polyglot-productization-stack.md`
- Added execution design: `design/polyglot-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Polyglot Productization Stack** so the archive now treats **crate-vs-foreign-package identity + generated-binding provenance + runtime/init/threading truth + shipped-artifact truth + support/docs truth** as an emerging ranked seam instead of leaving Rust mixed-language products split across FFI notes, wheel/prebuild/package metadata, component manifests, and README folklore
- Strategy: clarified that the worthy contribution here is not another host-language binding framework, packaging wrapper, or universal IDL pitch, but a portable boring-polyglot substrate that keeps boundary truth, package truth, runtime truth, artifact truth, and support truth distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future polyglot-productization revisions do not flatten native ABI boundaries, host-package metadata, generated-binding provenance, runtime/lifetime/threading assumptions, shipped artifacts, and support conclusions into one fake “bindings support” story

## New (rev0216)
- Added synthesis design: `design/firmware-productization-stack.md`
- Added execution design: `design/firmware-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Firmware Productization Stack** so the archive now treats **board/probe/run truth + target/sysroot activation + footprint/layout evidence + logging/fault evidence + support/release truth** as a ranked seam instead of leaving Rust firmware work split across HAL traits, board templates, linker scripts, probe commands, and README folklore
- Strategy: clarified that the worthy contribution here is not another HAL unification push, board template, runner wrapper, or framework bake-off, but a portable boring-firmware substrate that keeps **device lab + toolchain + footprint + runtime evidence + support/release truth** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future firmware-productization revisions do not flatten device/run truth, toolchain activation, footprint/layout evidence, runtime/fault evidence, and support/release conclusions into one fake embedded-readiness story

## New (rev0215)
- Added synthesis design: `design/scientific-productization-stack.md`
- Added execution design: `design/scientific-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Scientific Productization Stack** so the archive now treats **tensor truth + dataset/storage truth + backend/offload truth + model/runtime truth + activation truth + support/docs truth** as a ranked seam instead of leaving Rust scientific work split across runtime APIs, storage formats, GPU backends, model runners, and README folklore
- Strategy: clarified that the worthy contribution here is not another NumPy/JAX/PyTorch clone, giant numerical runtime, or fake universal array trait, but a portable boring-science substrate that keeps array/tensor, storage, backend, model, runtime, and support truths distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future scientific-productization revisions do not flatten storage surfaces, array/tensor semantics, backend/device activation, model/runtime attachments, and support conclusions into one fake scientific-readiness story

## New (rev0214)
- Gap: `gaps/numerical-array-tensor-surfaces-and-interop-contracts.md`
- Design: `design/tensor-surface-kit.md`
- Added execution design: `design/tensor-surface-pilot-program.md`
- Epic: `proposals/epic-tensor-surface-kit.md`
- Priority refresh: added **Tensor Surface Kit** as a Tier 1/2 candidate so the archive now treats **shape/dtype truth + layout/view/ownership posture + device/autodiff assumptions + interchange/storage adapter evidence** as a real numerical/scientific seam instead of leaving Rust tensor work split across library docs, runtime APIs, and ad hoc conversion code
- Strategy: clarified that the worthy contribution here is not another NumPy clone, tensor runtime, or universal array trait, but a portable numerical-surface substrate that keeps **shape/layout/view/device/interchange truth** distinct while still letting downstream data/model/offload work compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future tensor-surface revisions do not flatten arrays, matrices, runtime tensors, storage-backed arrays, and adapter outcomes into one fake canonical object

## New (rev0213)
- Added synthesis design: `design/agent-productization-stack.md`
- Added execution design: `design/agent-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Agent Productization Stack** so the archive now treats **workflow/prompt/tool/resource truth + model/retrieval attachments + runtime/identity activation + eval/trace evidence + support/docs truth** as an emerging ranked seam instead of leaving Rust agentic work split across MCP manifests, provider dashboards, prompt files, and framework-local glue
- Strategy: clarified that the worthy contribution here is not another model wrapper, MCP helper, or orchestration framework, but a portable boring-agent substrate for real Rust products
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future agent-productization revisions keep workflow truth, lower-layer attachments, runtime/identity activation, eval/trace evidence, support/docs truth, and transition evidence distinct instead of flattening them into one fake “agent readiness” story

## New (rev0212)
- Added synthesis design: `design/identity-productization-stack.md`
- Added execution design: `design/identity-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Identity Productization Stack** so the archive now treats **supported auth/principal truth + protected-surface attachments + runtime provider/secret activation + support/docs truth + transition evidence** as a ranked seam instead of leaving Rust identity work scattered across middleware, provider configs, cookie settings, and prose
- Strategy: clarified that the worthy contribution here is not another auth framework, JWT helper, or policy engine, but a portable boring-auth substrate that keeps **identity surface + protected surfaces + runtime activation + support truth + migrations** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future identity-productization revisions keep supported auth methods, principal/claim truth, protected-surface requirements, runtime settings/credentials posture, support/docs truth, and downstream consumer conclusions distinct instead of flattening them into one vague “auth support” story

## New (rev0211)
- Added synthesis design: `design/data-productization-stack.md`
- Added execution design: `design/data-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Data Productization Stack** so the archive now treats **live database truth + public schema truth + migration-program truth + runtime settings/secret activation + support/docs truth** as a ranked seam instead of leaving Rust stateful-data work split across ORM notes, migration tools, and README folklore
- Strategy: clarified that the worthy contribution here is not another ORM, query DSL, migration generator, or hosted control plane, but a portable boring-data substrate that keeps **query/offline evidence + schema snapshots + migration reports + runtime activation + consumer imports** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future data-productization revisions keep live DB truth, public schema truth, broader migration truth, runtime settings/secret truth, support/docs truth, and downstream consumer conclusions distinct instead of flattening them into one vague “data platform” story


## New (rev0210)
- Added synthesis design: `design/client-productization-stack.md`
- Added execution design: `design/client-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Client Productization Stack** so the archive now treats **app-surface/package truth + a11y semantics + locale/fallback/runtime-data truth + distribution/install receipts + support/docs truth** as a ranked seam instead of leaving Rust client apps as scattered framework docs and platform manifests
- Strategy: clarified that the worthy contribution here is not another GUI toolkit, shell, bridge generator, or deployment wrapper, but a portable boring-app substrate that keeps **client app surface + accessibility + localization + distribution/install truth + support claims** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future client-productization revisions keep app/package/capability/lifecycle truth, a11y snapshots and reports, locale/catalog/fallback/runtime-data truth, distribution/install receipts, support/docs truth, and downstream consumer conclusions distinct instead of flattening them into one vague “app readiness” story


## New (rev0209)
- Added synthesis design: `design/tooling-contract-stack.md`
- Added execution design: `design/tooling-contract-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Tooling Contract Stack** so the archive now treats **discovery roots/config layers + package-selection truth + graph/plan exports + execution/build-state evidence + consumer handoffs** as a ranked Cargo-adjacent seam instead of scattered workspace/build/cache notes
- Strategy: clarified that the worthy contribution here is not a Cargo daemon, target-dir scraper, or universal monorepo manager, but a portable machine-facing contract stack that keeps **discovery + selection + plan + execution + rebuild evidence + consumer imports** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future tooling-contract revisions keep discovery roots, package scope, planned graph, live execution, imported report evidence, and downstream consumer conclusions distinct instead of flattening them into one vague “build tooling” story

## New (rev0208)
- Added synthesis design: `design/service-productization-stack.md`
- Added execution design: `design/service-productization-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Service Productization Stack** so the archive now treats **request/route truth + runtime settings truth + runtime evidence + async lifecycle/replay posture + background-work contracts + support/docs truth** as a ranked seam adjacent to, but distinct from, Debuggability, Compatibility Claims, and Release Truth
- Strategy: clarified that the worthy contribution here is not another web framework, app template, or “Rust Spring Boot”, but a portable boring-service substrate that keeps **HTTP/service behavior + settings + telemetry + async shutdown + jobs/workflows + support claims** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future service-productization revisions keep service surface, settings, observability, async lifecycle, background work, support truth, and downstream release/policy/incident conclusions distinct instead of flattening them into one vague “production readiness” story

## New (rev0207)
- Added synthesis design: `design/lint-governance-stack.md`
- Added execution design: `design/lint-governance-pilot-program.md`
- Design/epic refresh: `gaps/lint-profiles-baselines-and-fixpacks.md`, `design/lint-baseline-kit.md`, `proposals/epic-lint-baseline-kit.md`
- Frontier/priority refresh: promoted an explicit **Lint Governance Stack** so the archive now treats **selected policy/workspace inheritance truth + baseline debt + fixpack/apply handoff + Cargo-side warning imports + policy/release/safety consumers** as a ranked seam adjacent to, but distinct from, Compile Guidance, Edit Workflow, and Policy
- Strategy: clarified that the worthy contribution here is not another Clippy preset, autofix wrapper, or cleanliness score, but a portable lint-governance substrate that keeps **authored guidance + selected policy + observed findings + applied edits + downstream verdicts** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future lint-governance revisions keep profile locks, baseline debt, observed findings, fix suggestions, applied edits, and consumer conclusions distinct instead of flattening them into one vague lint or code-health story

## New (rev0206)
- Added synthesis design: `design/reflection-transition-stack.md`
- Added execution design: `design/reflection-transition-pilot-program.md`
- Design/epic refresh: `design/reflection-surface-kit.md`, `design/macro-workflow-kit.md`, `design/const-surface-kit.md`, `proposals/epic-reflection-surface-kit.md`
- Frontier/priority refresh: promoted an explicit **Reflection Transition Stack** so the archive now treats **current proc-macro burden + runtime/object-safe/schema reflection lanes + future compile-time reflection posture** as a ranked seam adjacent to, but distinct from, the broader Compile-Time Surface Stack
- Strategy: clarified that the worthy contribution here is not another reflection runtime, derive helper, or universal reflect trait, but a portable transition substrate that keeps **what macros cost today + what reflection metadata exists + what adapters rely on it + what const/comptime lanes really buy** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future reflection-transition revisions keep proc-macro burden, runtime reflection, compile-time reflection, registry semantics, and downstream adapter claims separate instead of flattening them into one vague “reflection support” story

## New (rev0205)
- Added synthesis design: `design/inventory-evidence-stack.md`
- Added execution design: `design/inventory-evidence-pilot-program.md`
- Design/epic refresh: `design/sbom-evidence-kit.md`, `proposals/epic-sbom-evidence-kit.md`
- Frontier/priority refresh: promoted an explicit **Inventory Evidence Stack** so the archive now treats **Cargo-native inventory truth + package-admission handoff + release attachment + distribution/install receipt truth + export-lossiness notes** as a ranked seam adjacent to, but distinct from, Package Admission, Release Truth, and Distribution Contract
- Strategy: clarified that the worthy contribution here is not another exporter, registry inventory page, or supply-chain dashboard, but a portable inventory-continuity substrate that keeps **what Cargo observed + what got projected + what binaries revealed + what releases attached + what installations selected** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future inventory-evidence revisions keep package subject, release subject, install subject, capture/projection/recovery lanes, and downstream trust/policy/incident conclusions separate instead of flattening them into one vague “SBOM state” story

## New (rev0204)
- Gap: `gaps/resolution-strategy-objectives-and-reviewable-lockfile-decisions.md`
- Design: `design/resolution-strategy-kit.md`
- Added synthesis design: `design/resolution-strategy-stack.md`
- Added execution design: `design/resolution-strategy-pilot-program.md`
- Epic: `proposals/epic-resolution-strategy-kit.md`
- Design refresh: `design/resolution-doctor-kit.md`, `design/dependency-control-stack.md`
- Frontier/priority refresh: promoted an explicit **Resolution Strategy Stack** so the archive now treats **objective-profile truth + accepted-tradeoff truth + bounded candidate comparison + dependency-control imports + downstream handoff posture** as a ranked seam adjacent to, but distinct from, Dependency Control, Migration, Public API, and Policy
- Strategy: clarified that the worthy contribution here is not another dependency dashboard, solver fork, or lockfile diff, but a portable strategy-review substrate that keeps **what objective was pursued + what Cargo selected + what alternatives mattered + what tradeoffs were accepted + what consumers may conclude** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future resolution-strategy revisions keep chosen-graph truth, activation truth, objective/tradeoff truth, candidate-comparison truth, and downstream policy/migration/support conclusions separate instead of flattening them into one vague “dependency decision” story

## New (rev0203)
- Gap: `gaps/manifest-truth-authored-published-and-consumed.md`
- Design: `design/manifest-surface-kit.md`
- Added synthesis design: `design/manifest-truth-stack.md`
- Added execution design: `design/manifest-truth-pilot-program.md`
- Epic: `proposals/epic-manifest-surface-kit.md`
- Frontier/priority refresh: promoted an explicit **Manifest Truth Stack** so the archive now treats **authored-manifest truth + packaged-manifest truth + discovery/frontmatter truth + feature-surface truth + consumer-import truth** as a ranked seam adjacent to, but distinct from, Repo Composition, ScriptKit, Dependency Control, and Publisher/Source Identity
- Strategy: clarified that the worthy contribution here is not another formatter, manifest editor, registry page, or metadata wrapper, but a portable manifest-review substrate that keeps **what was written + what Cargo inferred + what got packaged + what consumers imported + what downstream tools concluded** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future manifest-truth revisions keep authored, packaged, discovered, script/frontmatter, consumer-import, and downstream policy/install conclusions separate instead of flattening them into one vague “Cargo.toml state” story

## New (rev0202)
- Added synthesis design: `design/publisher-source-identity-stack.md`
- Added execution design: `design/publisher-source-identity-pilot-program.md`
- Design/epic refresh: `gaps/org-ownership-and-registry-ux.md`, `design/org-identity-registry-ux-kit.md`, `proposals/epic-org-identity-registry-ux-kit.md`
- Frontier/priority refresh: promoted an explicit **Publisher & Source Identity Stack** so the archive now treats **project-family claims + publish-authority truth + source/mirror identity + downstream trust/admission/install handoffs** as a ranked seam adjacent to, but distinct from, Trust, Package Admission, and Distribution
- Strategy: clarified that the worthy contribution here is not “finally pick namespaces”, another registry wrapper, or a stealth trust score, but a portable identity substrate that keeps **claim truth + publisher authority + source identity + downstream policy/install conclusions** distinct while still letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future publisher/source-identity revisions keep org/project labels, publish authority, namespace/claim semantics, source/replacement identity, and downstream trust/policy/install conclusions distinct instead of flattening them into one vague verification story

## New (rev0201)
- Gap: `gaps/consumer-install-selection-channels-mirrors-and-receipts.md`
- Design: `design/consumer-install-kit.md`
- Epic: `proposals/epic-consumer-install-kit.md`
- Added synthesis design: `design/distribution-contract-stack.md`
- Added execution design: `design/distribution-contract-pilot-program.md`
- Epic: `proposals/epic-distribution-contract-kit.md`
- Design refresh: `design/release-pipeline-kit.md`, `design/signed-binaries-kit.md`, `gaps/release-engineering-and-distribution-contract.md`
- Frontier/priority refresh: promoted an explicit **Distribution Contract Stack** so the archive now treats **consumer-side channel/catalog truth + selection/fallback truth + verification truth + installed-state receipts** as a ranked seam adjacent to, but distinct from, producer-side **Release Truth**
- Strategy: clarified that the worthy contribution here is not another installer wrapper, host-page autodetector, or binary-only trust badge, but a portable acquisition boundary that keeps **release truth + visible candidates + selection/fallback + verification + installed state + downstream support/incident imports** distinct while letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future distribution-contract revisions keep producer release truth, visible catalog/channel truth, selection/fallback truth, verification posture, installed-state truth, and downstream support/incident conclusions distinct instead of flattening them into one vague “installed successfully” story

## New (rev0200)
- Added synthesis design: `design/package-admission-stack.md`
- Added execution design: `design/package-admission-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Package Admission Stack** (**Dependency Control + Public API + SBOM Evidence + Trust Signals + Policy**) so the archive now treats registry-facing package publication as a ranked execution seam distinct from the broader binary/install/rebuild story
- Strategy: clarified that the worthy contribution here is not another secure-publish wrapper, registry score, or release umbrella, but a portable package-admission boundary that keeps **graph truth + exposure truth + inventory truth + trust-signal truth + policy truth + package-to-release handoff** distinct while letting them compose
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future package-admission revisions keep chosen graph, public contract, inventory, trust inputs, decision reports, and package-vs-release handoff distinct instead of flattening them into one vague supply-chain or release-safety claim

## New (rev0199)
- Added synthesis design: `design/borrowing-frontier-stack.md`
- Added execution design: `design/borrowing-frontier-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Borrowing Frontier Stack** (**Trait Surface Kit + Pointer Surface Kit + Lending Surface Kit + Initialization Surface Kit**) so the archive now treats pointer/reference semantics, borrowing-sequence semantics, trait-family evolution, and in-place/pinned construction as one ranked language-adjacent execution band instead of a mix of isolated frontier edges and “important later” notes
- Proposal follow-through: the stack now has a concrete proposal-layer candidate in `proposals/epic-borrowing-frontier-stack.md`
- Strategy: clarified that the worthy contribution here is not a universal smart-pointer trait, stream replacement, trait-system manifesto, or constructor empire, but a portable review/migration substrate that keeps **trait truth + pointer truth + lending truth + initialization truth** distinct while the language frontier continues to move
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future borrowing-frontier revisions keep trait-family semantics, pointer/reference semantics, lending/sequence semantics, and initialization/destruction semantics distinct instead of flattening them into one vague “borrowing support” story

## New (rev0198)
- Gap: `gaps/testing-harness-protocols-and-benchmark-interop.md`
- Design: `design/harness-protocol-kit.md`
- Added execution design: `design/harness-protocol-pilot-program.md`
- Epic: `proposals/epic-harness-protocol-kit.md`
- Design/stack refresh: `design/test-run-evidence-kit.md`, `design/test-execution-evidence-stack.md`, `design/test-execution-pilot-program.md`
- Frontier/priority refresh: added **Harness Protocol Kit** as a first-class testing seam and tightened the broader testing map so the archive now treats **capability/discovery truth + runner-adapter truth + execution/result truth + specialized attachments** as a real **Testing Contract Stack** instead of letting test-run evidence quietly absorb bench/doctest/custom-framework questions it was never meant to own
- Strategy: clarified that the worthy contribution here is not another test runner, benchmark framework replacement, or hidden libtest schema, but a portable harness contract that Cargo, nextest, IDEs, CI, docs, and ecosystem harnesses can all build on honestly
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future testing revisions keep harness capability/discovery, runner semantics, execution/result truth, benchmark metrics, doctest posture, and downstream conclusions distinct instead of flattening them into one vague “testing support” story

## New (rev0197)
- Added synthesis design: `design/trust-decision-stack.md`
- Added execution design: `design/trust-signals-pilot-program.md`
- Design/epic refresh: `design/trust-signals-kit.md`, `proposals/epic-trust-signals-kit.md`
- Frontier/priority refresh: clarified an explicit **Trust Decision Stack** (**Trust Signals + Policy + Typosquat Guard + Lifecycle + Signed/Inventory imports**) in `STRATEGIC_FRONTIER.md` and tightened `PRIORITIES.md` so **Trust Signals Kit** now advances through a ranked evidence-first pilot program instead of overlapping with Policy Kit or drifting toward crate-score theater
- Strategy: clarified that the worthy contribution here is not another cargo-vet replacement, registry-only warning UI, or fake trust number, but a ranked rollout connecting issuer-aware trust reports, build/proc-macro scope truth, publisher/freshness truth, policy handoff, and thin explainable registry/review views
- Hygiene: refactored **Trust Signals Kit** so it no longer claims a separate `trust-policy/v0` verdict layer, and strengthened `meta/AMNESIA_RESISTORS.md` so future trust revisions keep trust-import profiles, downstream policy, and rendered views distinct instead of flattening them into one vague trust/compliance story

## New (rev0196)
- Added synthesis design: `design/conformance-traceability-stack.md`
- Added execution design: `design/spec-conformance-pilot-program.md`
- Design/epic refresh: `design/spec-conformance-kit.md`, `proposals/epic-spec-conformance-kit.md`
- Frontier/priority refresh: promoted **Spec Conformance Kit** from Tier 1 to Tier 0/1 in `PRIORITIES.md` and added an explicit **Conformance Traceability Stack** (**Spec Conformance + Acceptance Surface + Safety-Critical Evidence**) seam to `STRATEGIC_FRONTIER.md`
- Strategy: clarified that the worthy contribution here is not a compiletest clone or a fake certification badge, but a ranked traceability stack connecting paragraph-linked text, executable vectors, implementation-capability reports, acceptance diffs, and safety-critical consumer imports
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future conformance-traceability revisions keep stable text, experimental text, conformance vectors, acceptance reality, and assurance conclusions distinct instead of flattening them into one vague “spec compliance” claim

## New (rev0195)
- Added synthesis design: `design/debuggability-stack.md`
- Added execution design: `design/debuggability-pilot-program.md`
- Frontier/priority refresh: promoted an explicit **Debuggability Stack** (**Diagnostic Surface + Observability + Debugger Experience**) so the archive now treats failure identity, runtime correlation, debugger tuple truth, and repro/support handoffs as one ranked ecosystem seam instead of scattered adjacent notes
- Strategy: tightened the archive around **diagnostic identity + runtime/telemetry correlation + debugger tuple capability + downstream repro/support truth**, with an explicit refusal to collapse diagnostics, tracing, debugger claims, and replay escalation into one fake “debugging works” story
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future debugging revisions keep declared failure surfaces, runtime evidence, debugger tuple results, and replay/incident handoffs distinct instead of flattening them into one vague debug status claim

## New (rev0194)
- Added synthesis design: `design/migration-truth-stack.md`
- Added execution design: `design/migration-pilot-program.md`
- Design/epic refresh: `design/migration-kit.md`, `proposals/epic-migration-kit.md`
- Frontier/priority refresh: promoted **Migration Truth Stack** (**Migration Kit + Edit Workflow + Public API + Support Envelope + DocProof + Downstream Testing**) into the current frontier discussion so the archive now treats upgrade choreography as a ranked orchestration seam instead of a worthy-but-floating side note; the stack-level proposal direction is now explicit in `proposals/epic-migration-truth-stack.md`
- Strategy: tightened the archive around **source-state truth + destination-intent truth + mechanical-edit truth + compatibility/support/docs/downstream imports + outcome/release truth**, with an explicit refusal to let `cargo fix`, dependency bumps, or green CI silently stand in for the migration program
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future migration revisions keep source state, destination intent, imported analysis, plan/run receipts, outcome claims, and downstream consumer conclusions distinct instead of collapsing them into one vague “upgrade succeeded” story

## New (rev0193)
- Added execution design: `design/airgap-pilot-program.md`
- Design/epic refresh: `design/airgap-kit.md`, `proposals/epic-airgap-kit.md`
- Frontier/priority refresh: promoted **Airgap Kit** in `PRIORITIES.md` and added a first-class restricted-network seam in `STRATEGIC_FRONTIER.md` so the archive now treats workspace-build, developer-tool-install, rustup-mirror, secure-mirror-verification, and integrated bootstrap lanes as a ranked program instead of one vague “offline Rust” story
- Strategy: tightened the archive around **exact-copy mirror topology + three-plane separation + install/root/lock truth + warm-cache-vs-validated-offline distinction**, with an explicit refusal to let publish-side hardening, warmed caches, or one mirror topology silently stand in for the whole restricted-network contract
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future airgap revisions keep dependency/build, developer-tool-install, rustup/toolchain, verification posture, and warm-cache-vs-validated-offline truths distinct instead of collapsing them into one fake offline-success claim

## New (rev0192)
- Added synthesis design: `design/dependency-control-stack.md`
- Added execution design: `design/dependency-control-pilot-program.md`
- Design/epic refresh: `design/resolution-doctor-kit.md`, `design/feature-kit.md`, `proposals/epic-resolution-doctor-kit.md`, `proposals/epic-feature-kit.md`
- Frontier/priority refresh: added **Dependency Control Stack** (**Resolution Doctor Kit + Feature Kit**) to `STRATEGIC_FRONTIER.md` and tightened `PRIORITIES.md` so chosen-graph truth, feature/unification truth, and public/private-boundary handoffs are now treated as one ranked execution band instead of adjacent dependency notes
- Strategy: tightened the archive around **selection truth + activation truth + control-policy truth + downstream handoff truth**, with an explicit refusal to flatten resolver choices, feature posture, and API/policy conclusions into one dependency-health score
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future dependency-control revisions keep chosen graph, activated capabilities, selection policy, and downstream consumer conclusions distinct instead of collapsing them into one vague supply-chain/dependency story

## New (rev0191)
- Added synthesis design: `design/async-reliability-stack.md`
- Added execution design: `design/async-reliability-pilot-program.md`
- Design/epic refresh: `design/async-lifecycle-kit.md`, `design/replay-kit.md`, `design/dst-kit.md`, `proposals/epic-async-lifecycle-kit.md`
- Frontier/priority refresh: replaced the standalone frontier-edge framing for **Async Lifecycle Kit** with a broader **Async Reliability Stack** (**Async Lifecycle + Replay + DST**) in `STRATEGIC_FRONTIER.md`, and added an explicit async stack note in `PRIORITIES.md` so shutdown truth, replay truth, and deterministic-simulation truth are now treated as one ranked execution band instead of adjacent concepts
- Strategy: tightened the archive around **ownership/shutdown truth + replay truth + exploration truth**, with an explicit refusal to flatten graceful shutdown, captured failures, and deterministic simulation into one fake async-health layer
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future async-reliability revisions keep runtime identity, lifecycle artifacts, replay exactness, DST capability, and consumer imports distinct instead of collapsing them into one vague async-debugging story

## New (rev0190)
- Added execution design: `design/pointer-surface-pilot-program.md`
- Design/epic/gap refresh: `design/pointer-surface-kit.md`, `proposals/epic-pointer-surface-kit.md`, `gaps/reference-surfaces-smart-pointers-and-custom-borrow-contracts.md`
- Frontier/priority refresh: promoted **Pointer Surface Kit** into the frontier-edge band in `STRATEGIC_FRONTIER.md` and tightened `PRIORITIES.md` so the archive now treats custom pointer/reference semantics as a ranked pilot program rather than a static “important later” language note
- Strategy: tightened the archive around **identity + alias/uniqueness + projection family + receiver/dyn posture + transition truth**, with explicit refusal to let one derive macro, one unsafe abstraction crate, or one fake universal smart-pointer trait silently become the ecosystem standard
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future pointer-surface revisions keep shared-ownership, pin/projection, foreign-reference, receiver/dyn, and transition/migration truths distinct instead of collapsing them into one vague “smart pointer support” story

## New (rev0189)
- Gap: `gaps/test-run-machine-readable-and-reviewable-results.md`
- Design: `design/test-run-evidence-kit.md`
- Added synthesis design: `design/test-execution-evidence-stack.md`
- Added execution design: `design/test-execution-pilot-program.md`
- Epic: `proposals/epic-test-run-evidence-kit.md`
- Frontier/priority refresh: promoted **Test Run Evidence Kit** in `PRIORITIES.md` and added **Test Execution Evidence Stack** to `STRATEGIC_FRONTIER.md` so the archive now treats machine-readable test execution as a real substrate rather than a side effect of individual runners or CI XML
- Strategy: tightened the archive around **subject identity + runner semantics + config-bound execution + attachment truth + flake posture**, with an explicit refusal to let coverage, replay, mutation, downstream, or device-lab lanes silently redefine the canonical test subject
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future testing revisions keep inventory, run profile, specialized evidence, flake observations, and downstream conclusions distinct instead of collapsing them into one fake “test status” story

## New (rev0188)
- Added synthesis design: `design/safety-critical-evidence-stack.md`
- Added execution design: `design/safety-critical-pilot-program.md`
- Design/epic refresh: `design/safety-evidence-kit.md`, `design/coverage-evidence-kit.md`, `design/sanitizer-battery-kit.md`, `design/formal-verification-kit.md`, `proposals/epic-safety-evidence-kit.md`
- Frontier/priority refresh: clarified in `STRATEGIC_FRONTIER.md` and `PRIORITIES.md` that the archive should now treat **Safety Evidence + Coverage Evidence + Sanitizer Battery + Formal Verification** as one ranked **Safety-Critical Evidence Stack** rather than a loose cluster of adjacent safety ideas
- Strategy: tightened the archive around **authority truth + criterion truth + runtime-checking truth + proof truth**, with an explicit refusal to collapse them into one fake certification score or universal qualification bundle
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future safety-critical revisions keep critical-slice scope, authority class, coverage criterion, runtime/proof lane, waiver budgets, and consumer claims distinct instead of flattening them into one vague assurance story

## New (rev0187)
- Added execution design: `design/wasm-component-pilot-program.md`
- Design/epic/gap refresh: `design/wasm-component-kit.md`, `proposals/epic-wasm-component-kit.md`, `gaps/wasm-component-workflows-and-wit-packaging.md`
- Frontier/priority refresh: clarified in `STRATEGIC_FRONTIER.md` and `PRIORITIES.md` that **Wasm Component Kit** should now advance through a ranked transition-aware pilot program rather than remain a strong-but-underspecified frontier note
- Strategy: tightened the archive around **native-Cargo-first component truth + `cargo-component` bridge truth + composition/host requirement evidence + registry/package identity + late consumer imports**, with explicit refusal to collapse Cargo package identity, WIT/package identity, artifact identity, and published identity
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future Wasm-component revisions keep native-vs-bridge lanes, WIT resolution, composition, host requirements, and publication identity distinct instead of collapsing them into one vague “Rust Wasm component support” story

## New (rev0186)
- Added execution design: `design/scriptkit-pilot-program.md`
- Design/epic/gap refresh: `design/scriptkit.md`, `proposals/epic-scriptkit.md`, `gaps/single-file-scripts-first-class.md`
- Frontier/priority refresh: promoted **ScriptKit** in `PRIORITIES.md` and added a frontier note in `STRATEGIC_FRONTIER.md` that Cargo single-file packages now deserve explicit **script-truth** treatment rather than remaining a side note under compile-time ergonomics
- Strategy: tightened the archive around **subject identity + frontmatter/default truth + lock/cache/discovery posture + consumer-import reports**, with a ranked rollout of minimal bug repro → shebang utility → in-repo automation → editor/CI import → workspace opt-in/policy
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future ScriptKit revisions keep explicit-vs-inferred manifest truth, standalone-vs-workspace posture, cache/lock lane identity, consumer import lossiness, and policy attachments distinct instead of collapsing them into one vague “Rust scripting” story

## New (rev0185)
- Added synthesis design: `design/build-state-evidence-stack.md`
- Added execution design: `design/build-state-evidence-pilot-program.md`
- Design/epic refresh: `design/build-cache-kit.md`, `design/change-impact-kit.md`, `design/build-doctor-kit.md`, `proposals/epic-build-cache-kit.md`, `proposals/epic-change-impact-kit.md`, `proposals/epic-build-doctor-kit.md`
- Frontier/priority refresh: clarified in `STRATEGIC_FRONTIER.md` and `PRIORITIES.md` that the **Build-State Evidence Stack** now needs an explicit ranked pilot program — editor/CLI coexistence first, private-change/relink opportunity second, workspace/CI exchange third, workflow-aware diagnosis fourth, then federated consumers
- Strategy: tightened the archive around **layout truth + impact truth + diagnosis truth** so cache reports, relink-sensitive reasoning, and build suggestions can compose without collapsing into one fake build-health score
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future build-state-evidence revisions keep lane profile, imported evidence, reuse/block/impact distinctions, diagnosis scope, and scorecards distinct instead of flattening them into one vague slow-build story

## New (rev0184)
- Added execution design: `design/canonical-learning-consumer-pilot-program.md`
- Design refresh: `design/canonical-learning-stack.md`, `design/docproof-kit.md`, `design/compile-guidance-kit.md`
- Frontier/priority refresh: clarified in `STRATEGIC_FRONTIER.md` and `PRIORITIES.md` that the **Canonical Learning Stack** now needs an explicit shared consumer-import layer — docs host/rendered-doc import first, then CI/release-review import, then editor overlays, then assistant slices, and only then atlas/support/release consumers
- Strategy: tightened the archive around **canonical-first authority boundaries** so docs hosts, CI, editors, assistants, and review tools can import `doc-pack` / `guidance-pack` artifacts without silently becoming the new canon
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future canonical-learning-consumer revisions keep canonical artifacts, import profiles, derived overlays, mutation authority, and downstream review/curation views distinct instead of collapsing them into one vague AI/docs layer

## New (rev0183)
- Added execution design: `design/docproof-pilot-program.md`
- Added synthesis design: `design/canonical-learning-stack.md`
- Design/epic/gap refresh: `design/docproof-kit.md`, `proposals/epic-docproof-kit.md`, `gaps/executable-docs-and-guide-verification.md`
- Frontier/priority refresh: replaced the standalone compile-guidance frontier-edge framing with a broader **Canonical Learning Stack** (**DocProof Kit + Compile Guidance Kit**) in `STRATEGIC_FRONTIER.md`, promoted **DocProof Kit** in `PRIORITIES.md`, and added an explicit stack note that semantic/editor/assistant consumers must import canonical learning artifacts rather than overwrite them
- Strategy: clarified that the next credible move is a paired ranked rollout — DocProof should start with API docs + docs.rs, then CLI transcripts, then guide books, then compile-fail teaching, then release/support consumers; Compile Guidance should keep its ranked pilot track for trait diagnostics, proc-macro UI/examples, lint catalogs, hook profiles, and CI/editor consumers
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future canonical-learning revisions keep docs/guides/transcripts, compile-time guidance, hosted-doc/support imports, and semantic/editor/assistant-derived context distinct instead of collapsing them into one assistant-shaped knowledge blob

## New (rev0182)
- Gap: `gaps/repo-composition-discovery-package-selection-and-scope-continuity.md`
- Design: `design/repo-composition-stack.md`
- Design: `design/repo-composition-pilot-program.md`
- Epic: `proposals/epic-repo-composition-stack.md`
- Design refresh: `design/workspace-governance-kit.md`
- Priority: promoted the emerging Repo Composition Stack (**Workspace Governance Kit + Config Set Kit + Build Interop Kit**) as a Tier 0/1 synthesis priority; framed around discovery-boundary truth, package-selection/default-members evidence, `workspace-report` ↔ `config-set` handoff, and honest tool-lossiness notes rather than another universal monorepo manager

## New (rev0181)
- Added synthesis note: `design/maintenance-reality-stack.md`
- Design/epic refresh: `design/stewardship-ops-kit.md`, `proposals/epic-stewardship-ops-kit.md`
- Frontier refresh: promoted **Maintenance Reality Stack** (**Lifecycle Ledger Kit + Stewardship Ops Kit**) into the frontier band in `STRATEGIC_FRONTIER.md` and cleaned duplicate tail sections in that file
- Priority refresh: clarified in `PRIORITIES.md` that maintenance-reality work should now prefer ranked stewardship pilots, explicit declared-vs-observed boundaries, support-routing profiles, public-vs-restricted visibility rules, and real consumer proofs rather than another maintainer-health dashboard
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future maintenance-reality revisions keep lifecycle intent, observed operations, routing posture, visibility policy, and downstream funding/policy conclusions distinct instead of collapsing them into one fake project-health score

## New (rev0180)
- Added execution design: `design/support-envelope-pilot-program.md`
- Design/epic refresh: `design/support-envelope-kit.md`, `proposals/epic-support-envelope-kit.md`
- Frontier/priority refresh: clarified in `STRATEGIC_FRONTIER.md` and `PRIORITIES.md` that the **Support Envelope** half of the broader Compatibility Claims stack should now advance through its own ranked pilot program (released binaries → source-build/custom-target → docs surface → runtime-floor derivation → long-lived support) rather than another platform matrix, cross-build wrapper, or support badge
- Strategy: tightened the support story around explicit evidence policies, docs-surface truth, runtime-floor profiles, `cargo build` vs `cargo check` discipline, and keeping provisioning backend truth separate from support status
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future support-envelope-pilot revisions keep pilot lane, evidence policy, docs posture, runtime-floor posture, consumer class, and scorecard distinct instead of flattening them into one vague “platform support” claim

## New (rev0179)
- Added execution design: `design/compile-guidance-pilot-program.md`
- Design/epic refresh: `design/compile-guidance-kit.md`, `proposals/epic-compile-guidance-kit.md`
- Frontier/priority refresh: clarified in `STRATEGIC_FRONTIER.md` and `PRIORITIES.md` that **Compile Guidance Kit** should advance through a ranked pilot program (trait diagnostics → proc-macro UI/examples → lint catalogs → hook profiles → CI/editor consumers) rather than another lint pack, macro helper, or universal extension manifest
- Strategy: promoted **Compile Guidance Kit** out of the generic non-demotion bucket and reframed it around explicit stability profiles, example catalogs, consumer profiles, and imported hook-authority truth instead of one vague “better errors” story
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future compile-guidance-pilot revisions keep guidance family, stability posture, example evidence, hook-authority imports, consumer class, and scorecard distinct instead of flattening everything into one fake supportive-tooling claim

## New (rev0178)
- Added execution design: `design/policy-pilot-program.md`
- Design/epic refresh: `design/policy-kit.md`, `proposals/epic-policy-kit.md`
- Frontier/priority refresh: clarified in `STRATEGIC_FRONTIER.md` and `PRIORITIES.md` that **Policy Kit** should advance through a ranked pilot program (package release gate → workspace split-scope → proc-macro/build-lane cooldown → artifact-linked release candidate → migration diff lane) rather than more bespoke CI glue, registry-health dashboards, or fake compliance scores
- Strategy: sharpened the policy story around explicit subject slices, evidence-import profiles, honest `INCONCLUSIVE` states, visible waiver budgets, and consumer-specific decision packs instead of pretending one org-wide policy verdict is the natural first move
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future policy-pilot revisions keep pilot subject, evidence mix, waiver budget, consumer handoff, and scorecard distinct instead of collapsing them into one vague governance rollout

## New (rev0177)
- Added execution design: `design/semantic-context-pilot-program.md`
- Design/epic refresh: `design/semantic-context-kit.md`, `proposals/epic-semantic-context-kit.md`
- Frontier/priority refresh: clarified in `STRATEGIC_FRONTIER.md` and `PRIORITIES.md` that **Semantic Context Kit** should advance through a ranked pilot program (local semver lane → docs.rs lookup lane → fix/lint handoff lane → editor/assistant slice lane → compiler-backed augmentation lane) rather than another universal workspace index, hidden tool cache, or “AI context” blob
- Strategy: sharpened the semantic-context story around exact subject identity, lane-specific provenance, explicit cache/freshness posture, bounded query budgets, consumer handoffs, and weaker derived assistant/editor slices rather than pretending all machine consumers share one level of authority
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future semantic-context pilot revisions keep pilot subject, input-lane mix, cache/freshness posture, consumer class, query budget, and graduation status distinct instead of collapsing them into one vague rollout

## New (rev0176)
- Added execution design: `design/debugger-pilot-program.md`
- Frontier/priority refresh: clarified in `STRATEGIC_FRONTIER.md` and `PRIORITIES.md` that **Debugger Experience Kit** should advance through a ranked pilot program (std/container tuple truth → crate visualizer release lane → async inspection lane → expression posture → compatibility-consumer lane) rather than more anecdotal debugger support claims, IDE-only integrations, or a premature cross-runtime debug standard
- Strategy: sharpened the debugger story around tuple truth, release-grade visualizer artifacts, explicit native-vs-side-channel async inspection, honest expression-evaluation posture, and downstream consumption by compatibility/support tooling only after evidence exists
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future debugger revisions keep tuple identity, native debugger capabilities, visualizer coverage, async inspection posture, expression-evaluation posture, and regression evidence distinct instead of flattening everything into “debugging works”

## New (rev0175)
- Added execution design: `design/interop-commons-pilot-program.md`
- Design/epic refresh: `design/interop-commons-kit.md`, `proposals/epic-interop-commons-kit.md`
- Frontier/priority refresh: promoted **Navigation + Commons Stack** (**Ecosystem Atlas Kit + Interop Commons Kit**) higher in `STRATEGIC_FRONTIER.md` and clarified in `PRIORITIES.md` that the next credible move is a paired atlas+commons pilot posture rather than another ranking site, giant blessed-crates page, or premature universal abstraction crate
- Strategy: clarified that Interop Commons should launch through ranked pilots (HTTP request/response/body → service/layer middleware → one explicit watch/wait async borrowing/sequence seam), while Atlas remains the curator/freshness layer that consumes proven seams rather than silently minting them
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future commons-pilot revisions keep seam selection, neutral-core scope, adapter evidence, conformance budgets, readiness verdicts, and stewardship posture distinct instead of collapsing everything into one vague “better interop” story

## New (rev0174)
- Added execution design: `design/lending-surface-pilot-program.md`
- Design/epic refresh: `gaps/lending-surfaces-borrowing-streams-and-sequence-interop.md`, `design/lending-surface-kit.md`, `proposals/epic-lending-surface-kit.md`
- Frontier/priority refresh: promoted **Lending Surface Kit** from the “important non-demotion” bucket to the frontier edge in `STRATEGIC_FRONTIER.md` and clarified in `PRIORITIES.md` that the next credible move is a ranked pilot program rather than another attempt to crown one universal sequence facade
- Strategy: clarified that the lending rollout should be sync lending → async bridge → borrowing callback / async closure → pin/runtime-sensitive adapters → domain pilots, so borrow modes, adapter lossiness, runtime posture, and language-readiness stay explicit instead of being flattened into one vague “better stream” story
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future lending-surface pilot revisions keep borrow mode, adapter lossiness, pin/runtime posture, and language-readiness distinct instead of collapsing sync lending, async bridges, borrowing callbacks, and future language-enabled lanes into one fake universal sequence API

## New (rev0173)
- Added execution design: `design/edit-governance-pilot-program.md`
- Design/epic refresh: `design/semantic-context-kit.md`, `design/edit-workflow-kit.md`, `gaps/reviewable-edits-code-actions-and-refactors.md`, `proposals/epic-edit-workflow-kit.md`
- Frontier/priority refresh: kept the **Semantic Context + Edit Workflow Stack** in the top frontier band in `STRATEGIC_FRONTIER.md` and clarified in `PRIORITIES.md` that the next credible move is a ranked edit-governance pilot program rather than direct assistant patching or another opaque autofix tool
- Strategy: clarified that semantic context should remain canonical-first and shared, while edit producers must travel through explicit candidate → selection → apply → verify lanes; ranked the rollout as compiler suggestions → Cargo fix / edition waves → rust-analyzer assist export → assistant proposals under manual review → CI consumers
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future edit-governance revisions keep canonical context capture, candidate generation, selection authority, apply receipts, and verification rights distinct instead of flattening them into one vague “autofix” event

## New (rev0172)
- Added execution design: `design/release-pipeline-pilot-program.md`
- Design/epic refresh: `design/release-pipeline-kit.md`, `design/signed-binaries-kit.md`, `design/repro-build-kit.md`, `proposals/epic-release-pipeline-kit.md`
- Frontier/priority refresh: added the **Release Truth Stack** (**Release Pipeline Kit + Signed Binaries Kit + Repro Build Kit**) to `STRATEGIC_FRONTIER.md` and promoted **Release Pipeline Kit** from **Tier 1** to **Tier 0/1** in `PRIORITIES.md`
- Strategy: clarified that the next credible release move is a ranked pilot program (crate-only publish → CLI binary → signed-install → independent rebuild → multi-channel/mirror) rather than another all-in-one release wrapper, host-page scraper, or fake “secure release” badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future release-truth revisions keep source publish, built-artifact inventory, signature verification, provenance, and rebuild evidence distinct instead of collapsing them into one vague release score

## New (rev0171)
- Added execution design: `design/async-lifecycle-pilot-program.md`
- Design/epic refresh: `gaps/async-lifecycle-and-structured-concurrency.md`, `design/async-lifecycle-kit.md`, `proposals/epic-async-lifecycle-kit.md`
- Frontier/priority refresh: moved **Async Lifecycle Kit** onto the frontier edge in `STRATEGIC_FRONTIER.md` and promoted it from **Tier 1** to **Tier 0/1** in `PRIORITIES.md`
- Strategy: clarified that the next credible async move is a ranked pilot program (Tokio service shutdown → runtime-portable library → supervised worker lanes → repro/debug consumers → constrained async) rather than another convenience runtime facade, shutdown helper, or fake cross-runtime compatibility badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future async-lifecycle revisions keep runtime capability, shutdown policy, task ownership, cancellation-path evidence, and repro/debug consumer lanes distinct instead of flattening them into one vague “async reliability” score

## New (rev0170)
- Added execution design: `design/public-api-pilot-program.md`
- Design/epic refresh: `design/public-api-kit.md`, `proposals/epic-public-api-kit.md`, `gaps/public-api-semver-msrv.md`
- Frontier/priority refresh: kept **Public API Kit** as the top frontier and clarified in `STRATEGIC_FRONTIER.md` and `PRIORITIES.md` that the next credible move is a ranked pilot program (single-crate release gate → workspace release group → downstream intake → policy correlation → change-impact consumer) rather than more isolated API diff outputs
- Strategy: clarified that `api-pack/v0` should first win publisher CI and release-attachment reality, then survive workspace aggregation and downstream review before becoming a serious policy/build consumer input
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future public-API pilot revisions keep release subject, comparison baseline, consumer lane, override posture, and attachment policy distinct instead of flattening them into one fake publish score

## New (rev0169)
- Added execution design: `design/toolchain-productization-pilot-program.md`
- Design/epic refresh: `design/sysroot-pack-kit.md`, `proposals/epic-sysroot-pack-kit.md`
- Frontier/priority refresh: moved the **Toolchain Productization Stack** (**Sysroot Pack Kit + Cross Toolchain Kit + Sanitizer Battery Kit**) into `STRATEGIC_FRONTIER.md` and promoted **Sysroot Pack Kit** from **Tier 1** to **Tier 0/1** in `PRIORITIES.md`
- Strategy: clarified that the next credible move is a ranked pilot program (instrumented stdlib → hardened/ABI-modifying → custom target/tier-3 → shared cache/CI → external build handoff) rather than another `build-std` wrapper, org-local cache, or fake universal toolchain manager
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future toolchain-productization revisions keep provisioning, stdlib identity, activation, and runtime-analysis lanes distinct instead of flattening them into one vague “custom toolchain” story

## New (rev0168)
- Added execution design: `design/resource-evidence-pilot-program.md`
- Design/epic refresh: `design/perf-labs.md`, `design/footprint-kit.md`, `proposals/epic-footprint-kit.md`
- Frontier/priority refresh: reframed **Perf Labs + Footprint Kit** as a shared **Resource Evidence Stack** in `STRATEGIC_FRONTIER.md`, and promoted **Footprint Kit** from **Tier 1/2** to **Tier 0/1** in `PRIORITIES.md`
- Strategy: clarified that the next credible move is a ranked resource-evidence pilot program (compile-workflow + build-storage → native release artifacts → constrained embedded/Wasm → runtime allocation → federated review) rather than another benchmark dashboard, one-off size script, or fake universal resource score
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future resource-evidence revisions keep compile/workflow cost, build-storage cost, artifact footprint, runtime allocation evidence, and verdicts distinct instead of flattening them into one fake health number

## New (rev0166)
- Added execution design: `design/compile-time-profile-ladder.md`
- Design/epic refresh: strengthened `design/compile-time-capabilities-kit.md`, `design/compile-time-surface-pilot-program.md`, `design/build-extension-kit.md`, `design/macro-workflow-kit.md`, `design/scriptkit.md`, and `proposals/epic-compile-time-capabilities-kit.md`
- Frontier/priority refresh: sharpened the **Compile-Time Surface Stack** so it now centers named governance profiles (`ambient-observed` → `declared-native` → `narrow-native` → `portable-sandbox` / `declared-no-run` / `language-first`) instead of vague all-or-nothing sandbox talk
- Strategy: clarified that the next credible compile-time move is a profile ladder plus profile-fit reports, so real workspaces can graduate by narrowing authority, replacing imperative steps, or migrating to language-first lanes rather than merely collecting more compile-time tooling
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future compile-time-profile revisions keep target profile, current fit, blockers, waiver posture, and graduation intent distinct instead of flattening them into one fake maturity score

## New (rev0165)
- Added execution design: `design/compile-time-surface-pilot-program.md`
- Design/epic refresh: `design/compile-time-capabilities-kit.md`, `design/build-extension-kit.md`, `design/macro-workflow-kit.md`, `design/scriptkit.md`, `proposals/epic-compile-time-capabilities-kit.md`, `proposals/epic-build-extension-kit.md`, `proposals/epic-macro-workflow-kit.md`, `proposals/epic-scriptkit.md`
- Frontier/priority refresh: strengthened `STRATEGIC_FRONTIER.md` so **Compile-Time Surface Stack** (**Compile-Time Capabilities + Build Extension + Macro Workflow**) is now treated as a top-band frontier, and updated `PRIORITIES.md` so **Build Extension Kit** is promoted to **Tier 0/1** and **Macro Workflow Kit** to **Tier 1**
- Strategy: clarified that the next credible move is a ranked compile-time pilot program (strict build-script authority → proc-macro-heavy workflow → structured replacement → shareable single-file repro → future-facing transition lane) rather than yet another isolated sandbox, macro debugger, or build-script helper
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future compile-time-surface revisions keep authority, replacement, workflow, share/repro, and transition layers distinct instead of collapsing them into one compile-time mega-tool or one fake “safe build” badge

## New (rev0164)
- Added execution design: `design/compatibility-claims-pilot-program.md`
- Design/epic refresh: `design/support-envelope-kit.md`, `design/acceptance-surface-kit.md`, `proposals/epic-support-envelope-kit.md`, `proposals/epic-acceptance-surface-kit.md`
- Frontier/priority refresh: reframed **Support Envelope Kit + Acceptance Surface Kit** as a shared **Compatibility Claims Stack** in `STRATEGIC_FRONTIER.md`; strengthened `PRIORITIES.md` so both kits now explicitly point at that shared stack and a ranked pilot program
- Strategy: clarified that the next credible move is not another cross-build wrapper or another UI-test harness, but a compatibility-claims pilot program spanning released binaries, debugger capability lanes, advanced-pattern acceptance lanes, mixed workspaces, and long-lived support lanes
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future compatibility-claim revisions keep platform support, debugger support, runtime floors, compiler-lane acceptance, workaround truth, and waivers separate instead of flattening them into one fake compatibility badge

## New (rev0163)
- Added execution design: `design/native-edge-pilot-program.md`
- Design/epic refresh: `design/ffi-boundary-kit.md`, `design/native-dependency-kit.md`, `proposals/epic-ffi-boundary-kit.md`, `proposals/epic-native-dependency-kit.md`
- Frontier/priority refresh: moved the **Native Edge Stack** (FFI Boundary + Native Dependency) into the top frontier band in `STRATEGIC_FRONTIER.md` and promoted **Native Dependency Kit** from **Tier 1** to **Tier 0/1** in `PRIORITIES.md`
- Strategy: clarified that the next credible interop/adoption move is a ranked pilot program (C ABI export → system-library consumers → C++ bridges → external build handoff → audited/safety-oriented compositions) rather than another generator, provider shim, or fake universal native package manager
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future native-edge revisions keep ABI boundaries, provider choices, build-system handoff, toolchain/support claims, and policy/safety overlays distinct instead of collapsing them into one vague “interop support” story

## New (rev0162)
- Added execution design: `design/stewardship-pilot-program.md`
- Design/epic refresh: `design/stewardship-ops-kit.md`, `proposals/epic-stewardship-ops-kit.md`
- Priority: promoted **Stewardship Ops Kit** from **Tier 1** to **Tier 0/1** in `PRIORITIES.md`; clarified that the strongest next move is a ranked pilot program with support-routing semantics rather than a generic maintainer-health dashboard
- Frontier: strengthened `STRATEGIC_FRONTIER.md` so the stewardship seam now points explicitly at PR-triage / issue-intake / release-readiness / maintainer-help / mentoring pilots and at support-program consumers
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future stewardship-pilot revisions keep workflow choice, service-level budgets, support-routing, and scorecards distinct instead of collapsing them into one fake health number

## New (rev0161)
- Gap: `gaps/maintenance-operations-and-stewardship-queues.md`
- Design: `design/stewardship-ops-kit.md`
- Epic: `proposals/epic-stewardship-ops-kit.md`
- Priority: added **Stewardship Ops Kit** as a Tier 1 candidate; framed it as the shared `steward-scope` / `queue-profile` / `queue-snapshot` / `review-pressure-report` / `help-request` / `mentoring-lane` / `steward-action-report` / `steward-diff-report` / `steward-pack` boundary across GitHub labels, triagebot flows, mentoring intake, release/backport queues, and support-program consumers rather than another maintainer dashboard or fake ecosystem-health score
- Frontier: strengthened `STRATEGIC_FRONTIER.md` to distinguish lifecycle **state** from maintenance **operations**, and to treat Stewardship Ops as an emerging seam just below the top frontier band
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future stewardship-operations revisions keep queue policy, observed state, derived pressure, help requests, mentoring capacity, and action logs distinct instead of flattening them into one fake health number

## New (rev0160)
- Added execution design: `design/atlas-pilot-program.md`
- Design/epic refresh: `design/ecosystem-atlas-kit.md`, `proposals/epic-ecosystem-atlas-kit.md`
- Frontier/priority refresh: strengthened the Navigation + Commons band in `STRATEGIC_FRONTIER.md` and clarified in `PRIORITIES.md` that the next credible Atlas move is a ranked pilot program rather than universal curation
- Strategy: ranked the first serious Atlas pilots as CLI → HTTP/services → client apps → safety-oriented lanes → Wasm/plugin lanes, with explicit pilot evidence budgets, governance profiles, freshness rules, and graduation scorecards
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future Atlas revisions preserve why a domain was chosen, what evidence it required, who curates it, and whether it is exploratory, promoted, stale, split, or retired

## New (rev0159)
- Frontier refresh: strengthened `STRATEGIC_FRONTIER.md`
- Design/epic refresh: `design/ecosystem-atlas-kit.md`, `design/interop-commons-kit.md`, `proposals/epic-ecosystem-atlas-kit.md`, `proposals/epic-interop-commons-kit.md`
- Priority: moved the **Navigation + Commons Stack** (Ecosystem Atlas + Interop Commons) into the top frontier band and promoted **Interop Commons Kit** from **Tier 1** to **Tier 0/1** in `PRIORITIES.md`
- Strategy: clarified the division of labor so Atlas owns curator-aware lanes, freshness, overlays, and derived guide / assistant outputs while Interop Commons owns neutral seams, adapter truth, conformance vectors, seam-readiness, and stewardship
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future revisions do not let recommendation pressure silently mint pseudo-standards or let neutral common-seam work smuggle in hidden stack preferences

## New (rev0158)
- Frontier refresh: strengthened `STRATEGIC_FRONTIER.md`
- Design/epic refresh: `design/semantic-context-kit.md`, `proposals/epic-semantic-context-kit.md`, `design/edit-workflow-kit.md`, `proposals/epic-edit-workflow-kit.md`
- Priority: elevated **Semantic Context + Edit Workflow** as a top tool-facing substrate band in the frontier, arguing that docs remaining canonical while machine consumers rise makes portable semantic context plus governed edit execution one of the strongest outside-the-box Rust ecosystem contribution seams now
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future tool-facing-knowledge proposals keep canonical sources, captured semantic context, and derived assistant/editor outputs distinct, and so edit-governance proposals rank review boundaries above producer hype

## New (rev0157)
- Added frontier map: `STRATEGIC_FRONTIER.md`
- Priority: added an evidence-weighted near-term ranking for where an epic Rust ecosystem contribution is most leveraged **now**, separating the broader conceptual map from the current action frontier instead of flattening everything into one undifferentiated shortlist
- Priority: promoted Build Doctor Kit and Debugger Experience Kit from **Tier 1** to **Tier 0/1** in `PRIORITIES.md`, reflecting the combination of persistent survey pain and live Cargo/debugging ecosystem motion
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future frontier updates separate user pain, upstream traction, complement-vs-duplicate posture, archive leverage, and broad conceptual importance instead of ranking by coolness or novelty alone

## New (rev0155)
- Gap rewrite: `gaps/unified-dependency-policy.md`
- Design rewrite: `design/policy-kit.md`
- Epic rewrite: `proposals/epic-policy-kit.md`
- Priority: strengthened Policy Kit at the top of the steering shortlist and in the Tier 0/1 supply-chain map; reframed it as the shared `policy-subject` / `policy-input-catalog` / `policy-rule-catalog` / `policy-waiver` / `policy-decision-report` / `policy-diff-report` / `policy-pack` boundary across cargo-deny, cargo-audit/rustsec, cargo-vet, Trust Signals, Lifecycle Ledger, SBOM Evidence, Signed Binaries, Support Envelope, and name-risk inputs rather than another opaque compliance score, bespoke CI shell wrapper, or one-off security dashboard
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future policy proposals keep subject scope, imported evidence, explicit rule catalogs, decision outcomes, waivers, and presentation layers distinct instead of flattening them into one fake compliance number

## New (rev0154)
- Gap rewrite: `gaps/upgrade-choreography-and-reviewable-migrations.md`
- Design rewrite: `design/migration-kit.md`
- Epic rewrite: `proposals/epic-migration-kit.md`
- Priority: promoted Migration Kit from **Tier 1/2** to **Tier 0/1**; reframed it as the shared `migration-subject` / `migration-intent` / `migration-analysis-report` / `migration-plan` / `migration-run-report` / `migration-outcome-report` / `migration-waiver` / `migration-pack` boundary across edition upgrades, Cargo fix / cargo-fixit-era edit flows, toolchain/MSRV ratchets, dependency changes, and support/API-sensitive transitions rather than another one-shot upgrader or blind autofix wrapper
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future migration proposals keep destination intent, configuration scope, candidate edits, approved execution, waivers, and final support claims distinct instead of flattening everything into one fake “upgrade result”

## New (rev0153)
- Gap rewrite: `gaps/sanitizers-and-dynamic-analysis.md`
- Design rewrite: `design/sanitizer-battery-kit.md`
- Epic rewrite: `proposals/epic-sanitizer-battery-kit.md`
- Priority: promoted Sanitizer Battery Kit from **Tier 1** to **Tier 0/1**; reframed it as the shared `sanitize-subject` / `sanitize-lane-profile` / `sanitize-runtime-profile` / `sanitize-capability-profile` / `sanitize-observation-report` / `sanitize-finding-report` / `sanitize-waiver` / `sanitize-diff-report` / `sanitize-pack` boundary across Miri, `cargo-careful`, LLVM sanitizers, exploit-mitigation lanes, and future BorrowSanitizer-style tools rather than another wrapper script, one-off CI matrix, or fake universal sanitizer badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future sanitizer-battery proposals keep engine family, runtime/sysroot provenance, execution semantics, finding capability, and waiver/comparability truth distinct instead of flattening Miri, careful, ASan/MSan/TSan/CFI, and future aliasing tools into one fake runtime-checking story

## New (rev0152)
- Gap: `gaps/reflection-surfaces-type-shapes-and-registration-contracts.md`
- Design: `design/reflection-surface-kit.md`
- Epic: `proposals/epic-reflection-surface-kit.md`
- Priority: added Reflection Surface Kit as a **Tier 1** reflection-and-meta-programming candidate; framed it as the shared `reflection-subject` / `reflection-acquisition-profile` / `reflection-shape-profile` / `reflection-value-access-profile` / `reflection-registry-profile` / `reflection-adapter-profile` / `reflection-check-report` / `reflection-diff-report` / `reflect-pack` boundary across future compile-time reflection, `bevy_reflect`, `facet`, `valuable`, `serde_reflection`, and inventory-backed registration rather than another reflection runtime, registry macro, or derive-only portability story
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future reflection-surface proposals keep acquisition mode, exposed shape metadata, value-access semantics, registry/discovery behavior, and downstream adapter claims distinct instead of flattening them into one fake “reflectable” badge

## New (rev0151)
- Gap: `gaps/change-impact-rebuild-scope-and-relinkability.md`
- Design: `design/change-impact-kit.md`
- Epic: `proposals/epic-change-impact-kit.md`
- Priority: added Change Impact Kit as a **Tier 0/1** build-and-compilation-efficiency candidate; framed it as the shared `impact-subject` / `change-slice` / `impact-lane-profile` / `impact-classification-report` / `rebuild-scope-report` / `relink-opportunity-report` / `impact-diff-report` / `impact-pack` boundary across Cargo fingerprinting, `cargo report rebuilds`, public-API evidence, compile-time invalidation facts, and future relink-don’t-rebuild work rather than another cache wrapper, perf dashboard, or vague “incremental build score”
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future change-impact proposals keep concrete change slices, semantic classifications, rebuild scope, relink opportunities, and observed-vs-required work distinct instead of flattening them into one fake rebuild story

## New (rev0150)
- Gap: `gaps/solver-sensitive-acceptance-and-borrow-check-portability.md`
- Design: `design/acceptance-surface-kit.md`
- Epic: `proposals/epic-acceptance-surface-kit.md`
- Priority: added Acceptance Surface Kit as a **Tier 0/1** language-and-toolchain-assurance candidate; framed it as the shared `acceptance-subject` / `pattern-catalog` / `compiler-lane-profile` / `acceptance-expectation-set` / `workaround-profile` / `acceptance-check-report` / `acceptance-diff-report` / `acceptance-pack` boundary across stable/beta/nightly, `-Znext-solver=globally`, Polonius, compiler UI-test practices, and library-side `trybuild` / `ui_test` harnesses rather than another snapshot runner, one-off regression matrix, or folklore-heavy “works on nightly” claim
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future acceptance-surface proposals keep subject identity, compiler lane, pattern catalog, workaround truth, reason-coded outcomes, and downstream conclusions distinct instead of flattening them into one fake compiler-compatibility badge

## New (rev0149)
- Gap rewrite: `gaps/mir-analysis-and-stable-export.md`
- Design rewrite: `design/mir-analysis-kit.md`
- Epic rewrite: `proposals/epic-mir-analysis-kit.md`
- Priority: promoted MIR Analysis Kit from **Tier 1** to **Tier 0/1**; reframed it as the shared `mir-subject` / `mir-capture-profile` / `mir-capability-profile` / `mir-observation-report` / `mir-derived-graph` / `mir-query-report` / `mir-diff-report` / `mir-pack` boundary across `rustc_public`, `rustc_public_bridge`, `stable-mir-json`-style exporters, and downstream semver/safety/verification tooling rather than another custom driver format or a fake stable “MIR JSON” promise
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future MIR-analysis proposals keep subject identity, capture lane, semantic epoch, capability/completeness, derived graphs/queries, and downstream conclusions distinct instead of flattening every compiler-aware export into one fake universal MIR snapshot

## New (rev0148)
- Gap rewrite: `gaps/target-support-envelopes-and-runtime-baselines.md`
- Design rewrite: `design/support-envelope-kit.md`
- Epic rewrite: `proposals/epic-support-envelope-kit.md`
- Priority: promoted Support Envelope Kit from **Tier 1/2** to **Tier 0/1**; reframed it as the shared `support-envelope` / `runtime-floor-report` / `support-observation-report` / `support-diff-report` / `support-waiver` / `support-pack` boundary across rustc target tiers, docs.rs target metadata, Cargo `supported-targets`, `build-std` / custom-target lanes, cross/zigbuild/xwin provisioning, release artifacts, and runtime-floor evidence rather than another cross-build wrapper or compatibility badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future platform-support proposals keep dev-host, source-build, release-artifact, docs, provisioning, runtime-floor, and validation-strength truths distinct instead of flattening them into one fake platform-support story

## New (rev0147)
- Gap rewrite: `gaps/reference-surfaces-smart-pointers-and-custom-borrow-contracts.md`
- Design rewrite: `design/pointer-surface-kit.md`
- Epic rewrite: `proposals/epic-pointer-surface-kit.md`
- Priority: moved Pointer Surface Kit higher in the steering shortlist and reframed it as the shared `pointer-surface` / `alias-uniqueness-profile` / `projection-family-profile` / `receiver-coercion-profile` / `pointer-transition-profile` / `pointer-vector-set` / `pointer-check-report` / `pointer-pack` boundary across ref-counted, pinned, foreign, intrusive, and custom pointer-like types rather than another smart-pointer crate, universal trait hierarchy, or unsafe abstraction empire
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future pointer-surface proposals keep identity/equality posture, aliasing/uniqueness semantics, projection families, receiver/coercion posture, and lifecycle guarantees distinct instead of flattening them into one fake universal smart-pointer story

## New (rev0146)
- Gap rewrite: `gaps/userwide-build-cache.md`
- Design rewrite: `design/build-cache-kit.md`
- Epic rewrite: `proposals/epic-build-cache-kit.md`
- Priority: promoted Build Cache Kit from **Tier 1** to **Tier 0/1**; reframed it as the shared `build-state-subject` / `build-layout-report` / `build-lock-report` / `cache-entry-report` / `reuse-verdict-report` / `cache-retention-policy` / `cache-exchange-profile` / `build-state-pack` boundary across Cargo’s build-dir relayout, finer-grained locking, user-wide cache work, rust-analyzer coexistence, and CI/remote cache lanes rather than another sccache wrapper, blob cache, or fake universal cache-hit score
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future build-cache proposals keep layout, lock scope, cache-entry identity, reuse verdicts, and retention/exchange policy distinct instead of flattening them into one vague “target dir state” story

## New (rev0145)
- Gap: `gaps/reviewable-edits-code-actions-and-refactors.md`
- Design: `design/edit-workflow-kit.md`
- Epic: `proposals/epic-edit-workflow-kit.md`
- Priority: added Edit Workflow Kit as a **Tier 0/1** tooling-and-IDE-cohesion candidate; framed it as the shared `edit-subject` / `edit-candidate-report` / `edit-selection-plan` / `edit-apply-report` / `edit-verify-report` / `edit-diff-report` / `edit-pack` boundary across `rustc` suggestions, `cargo fix`, edition migrations, rust-analyzer assists / SSR, and future assistant-generated edit batches rather than another editor plugin, one-shot autofix command, or giant blind patch
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future edit-workflow proposals keep subject identity, candidate provenance, selection policy, application outcome, and verification evidence distinct instead of flattening all suggested or applied edits into one fake “auto-fix result”

## New (rev0144)
- Gap: `gaps/cross-crate-semantic-context-and-analysis-inputs.md`
- Design: `design/semantic-context-kit.md`
- Epic: `proposals/epic-semantic-context-kit.md`
- Priority: added Semantic Context Kit as a Tier 0/1 tooling-substrate candidate; framed it as the shared `semctx-subject` / `resolution-context` / `semantic-input-catalog` / `semantic-merge-report` / `semantic-query-report` / `semctx-diff-report` / `semctx-pack` boundary across Cargo plumbing, docs.rs rustdoc JSON, `rmeta` / `rustc_public` compiler-backed lanes, semver/public-API tooling, docs/search frontends, and fix/lint/IDE/assistant consumers rather than another hidden workspace index or one-off code-intelligence cache
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future semantic-context proposals keep subject identity, resolution/build context, input provenance, merge/completeness truth, derived query results, and consumer decisions distinct instead of flattening Cargo, rustdoc, compiler, and cache lanes into one fake universal semantic story

## New (rev0143)
- Gap rewrite: `gaps/unsafe-and-verification-evidence.md`
- Design rewrite: `design/safety-evidence-kit.md`
- Epic rewrite: `proposals/epic-safety-evidence-kit.md`
- Priority: promoted Safety Evidence Kit from Tier 1 to Tier 0/1; reframed it as the shared `safety-subject` / `unsafe-surface-report` / `safety-contract-report` / `safety-lint-report` / `coverage-criterion-report` / `verification-claim-report` / `safety-case-report` / `safety-pack` boundary across unsafe documentation, contracts, Clippy/rustc lint posture, criterion-aware coverage, sanitizers, and formal-verification lanes rather than another spreadsheet binder, badge, or fake universal safety score
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future safety-case proposals keep unsafe surface, cited contracts, lint posture, coverage criteria, verification claims, and waivers distinct instead of flattening them into one fake assurance blob

## New (rev0142)
- Gap: `gaps/sbom-evidence-and-artifact-linked-dependency-inventory.md`
- Design: `design/sbom-evidence-kit.md`
- Epic: `proposals/epic-sbom-evidence-kit.md`
- Priority: added SBOM Evidence Kit as a Tier 0/1 candidate; framed it as the shared `inventory-subject` / `inventory-capture-report` / `inventory-graph` / `artifact-inventory-report` / `inventory-projection-report` / `inventory-diff-report` / `inventory-pack` boundary across Cargo SBOM precursors, `cargo-auditable`, CycloneDX/SPDX export lanes, and binary/container recovery rather than another one-shot exporter or fake universal BOM truth
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future SBOM/inventory proposals keep subject identity, capture lane, dependency-scope truth, artifact linkage, format projection, and downstream policy use distinct instead of flattening them into one fake inventory story

## New (rev0141)
- Gap rewrite: `gaps/procmacro-buildscript-transparency.md`
- Design rewrite: `design/compile-time-capabilities-kit.md`
- Epic rewrite: `proposals/epic-compile-time-capabilities-kit.md`
- Priority: strengthened Compile-Time Capabilities Kit in the steering shortlist and Tier 0/1 map; reframed it as the shared `ct-unit-manifest` / `ct-execution-lane` / `ct-capability-profile` / `ct-input-surface` / `ct-observation-report` / `ct-determinism-report` / `ct-policy` / `ct-waiver` / `ct-pack` boundary across build scripts, native/wasm proc-macros, and `links` override lanes rather than another sandbox wrapper or fake universal “safe build” badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future compile-time-capabilities proposals keep unit kind, execution lane, declared capabilities, observed accesses, input/invalidation surface, and override/waiver truth distinct instead of flattening all compile-time code execution into one monolithic security story

## New (rev0140)
- Gap rewrite: `gaps/reproducible-benchmarking-and-perf-regressions.md`
- Design rewrite: `design/perf-labs.md`
- Epic rewrite: `proposals/epic-perf-labs.md`
- Priority: promoted Perf Labs from Tier 1 to Tier 0/1; reframed it as the shared `perf-subject` / `perf-workload` / `perf-measurement-profile` / `perf-collector-profile` / `perf-baseline-record` / `perf-compare-report` / `perf-policy` / `perf-pack` boundary across Criterion/cargo-criterion, Iai-Callgrind/Valgrind-backed lanes, rustc-perf-style compile scenarios, and Cargo report imports rather than another benchmark engine, screenshot dashboard, or fake universal performance score
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future performance-evidence proposals keep workload identity, measurement lane, collector configuration, baseline provenance, raw evidence, and policy outcomes distinct instead of flattening them into one fake perf number

## New (rev0139)
- Gap rewrite: `gaps/public-api-semver-msrv.md`
- Design rewrite: `design/public-api-kit.md`
- Epic rewrite: `proposals/epic-public-api-kit.md`
- Priority: promoted Public API Kit from the broader Tier 0/1 map into the steering shortlist; reframed it as the shared `api-surface` / `api-exposure-report` / `api-diff-report` / `semver-report` / `api-witness-report` / `msrv-report` / `api-pack` boundary across Cargo public/private dependencies, `cargo-public-api`, `cargo-semver-checks`, witness-based type compatibility checking, and future `cargo publish` gating rather than another semver badge or changelog helper
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future public-API proposals keep surface export, dependency exposure, diff reason codes, witness evidence, MSRV verification, and publish/waiver posture distinct instead of collapsing them into one fake compatibility score

## New (rev0138)
- Gap rewrite: `gaps/ecosystem-navigation-and-reference-stacks.md`
- Design rewrite: `design/ecosystem-atlas-kit.md`
- Epic rewrite: `proposals/epic-ecosystem-atlas-kit.md`
- Priority: promoted Ecosystem Atlas Kit from Tier 1 to Tier 0/1; reframed it as the shared `atlas-domain` / `stack-lane` / `stack-slot-map` / `interop-seam-map` / `selection-evidence` / `curator-record` / `freshness-budget` / `atlas-check-report` / `atlas-pack` boundary across crates.io signals, docs.rs, trust/lifecycle/support inputs, and community curation rather than another ranking site or a single blessed-crates page
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future ecosystem-navigation proposals keep curator provenance, lane philosophy, slot choices, evidence, freshness budgets, interop posture, and derived guide/assistant outputs distinct instead of collapsing them into one fake leaderboard or one drifting prose guide

## New (rev0137)
- Gap rewrite: `gaps/crate-trust-signals.md`
- Design rewrite: `design/trust-signals-kit.md`
- Epic rewrite: `proposals/epic-trust-signals-kit.md`
- Priority: promoted Trust Signals Kit from Tier 1 to Tier 0/1; reframed it as the shared `trust-signal` / `trust-report` / `trust-policy` / `trust-diff-report` / `trust-pack` boundary across crates.io publisher controls and `pubtime`, RustSec advisories, cargo-vet audits, lifecycle inputs, and attached release evidence rather than another ranking site or one fake canonical score
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future trust proposals keep signal kinds, issuer classes, dependency scopes, freshness, policy evaluation, and optional ranking/views distinct instead of flattening them into one fake trust number

## New (rev0136)
- Gap rewrite: `gaps/lifecycle-ledger-and-succession.md`
- Design rewrite: `design/lifecycle-ledger-kit.md`
- Epic rewrite: `proposals/epic-lifecycle-ledger-kit.md`
- Priority: promoted Lifecycle Ledger Kit from Tier 1 to Tier 0/1; reframed it as the shared `lifecycle-intent` / `support-window-map` / `successor-map` / `handoff-consent` / `maintenance-report` / `lifecycle-report` / `lifecycle-diff-report` / `lifecycle-pack` boundary across crates.io lifecycle UI, RustSec unmaintained signals, Cargo’s dormant maintenance metadata, and `cargo-unmaintained`-style heuristics rather than another health-score site, automatic crate-transfer policy, or security-advisory overload
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future lifecycle proposals keep declared maintainer intent, version-line support truth, successor/handoff claims, maintenance evidence, and derived heuristics distinct instead of flattening them into one fake crate-health story

## New (rev0135)
- Gap rewrite: `gaps/debugger-interop-and-visualizers.md`
- Design rewrite: `design/debugger-experience-kit.md`
- Epic rewrite: `proposals/epic-debugger-experience-kit.md`
- Priority: promoted Debugger Experience Kit from Tier 1/2 to Tier 1; reframed it as the shared `debug-profile` / `debug-capability-report` / `viz-pack` / `async-debug-profile` / `expr-eval-profile` / `debug-battery-report` / `debug-pack` boundary across `rust-gdb` / `rust-lldb` / `rust-windbg` wrappers, `#![debugger_visualizer]`, IDE adapters, and Tokio-Console-style async instrumentation rather than another debugger or IDE plugin
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future debugging proposals keep debugger-family/OS/toolchain capability truth, visualizer coverage, async-runtime instrumentation, expression-evaluation posture, and repro artifacts distinct instead of flattening them into one fake universal debugging story

## New (rev0134)
- Gap: `gaps/build-performance-diagnosis-and-actionable-guidance.md`
- Design: `design/build-doctor-kit.md`
- Epic: `proposals/epic-build-doctor-kit.md`
- Priority: added Build Doctor Kit as a Tier 1 candidate; framed it as the shared `build-workflow-profile` / `build-observation-pack` / `build-bottleneck-profile` / `build-suggestion-catalog` / `build-diagnosis-report` / `build-doctor-pack` layer above Cargo report/build-analysis data and the official build-performance guide rather than another benchmark engine, timing HTML viewer, or generic compile-faster tips list
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future build-performance proposals keep workflow selection, raw observations, diagnoses, and tradeoff-aware suggestions distinct instead of collapsing them into one fake compile-time score or vague build-doctor mega-manifest

## New (rev0133)
- Gap: `gaps/cryptography-surfaces-algorithm-providers-and-secret-handling-contracts.md`
- Design: `design/cryptography-surface-kit.md`
- Epic: `proposals/epic-cryptography-surface-kit.md`
- Priority: added Cryptography Surface Kit as a Tier 1 candidate; framed it as the shared `crypto-surface` / `algorithm-family-profile` / `provider-backend-profile` / `key-material-profile` / `sidechannel-audit-profile` / `compliance-certification-profile` / `crypto-adapter-profile` / `crypto-vector-set` / `crypto-check-report` boundary across RustCrypto trait crates, `ring`, `aws-lc-rs`, `rustls` provider selection, password-hash PHC lanes, and secret-handling helpers rather than another algorithm crate, blanket security badge, or fake universal crypto facade
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future cryptography-surface proposals keep algorithm-family scope, provider/backend posture, key-material handling, side-channel and audit posture, compliance claims, and evidence distinct instead of flattening them into one fake cryptography story

## New (rev0132)
- Gap: `gaps/randomness-surfaces-entropy-seeding-and-reproducibility-contracts.md`
- Design: `design/randomness-surface-kit.md`
- Epic: `proposals/epic-randomness-surface-kit.md`
- Priority: added Randomness Surface Kit as a Tier 1 candidate; framed it as the shared `randomness-surface` / `entropy-source-profile` / `rng-semantics-profile` / `seed-repro-profile` / `crypto-strength-profile` / `target-backend-profile` / `randomness-adapter-profile` / `randomness-vector-set` / `randomness-check-report` boundary across `getrandom`, `rand`, portable named generators, lightweight alternatives, and crypto-facing RNG consumers rather than another universal RNG crate or fake “secure random” badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future randomness-surface proposals keep entropy source, PRNG semantics, seeding/reproducibility, crypto-strength claims, target/backend posture, and evidence distinct instead of flattening them into one fake randomness story

## New (rev0131)
- Gap: `gaps/encoding-surfaces-serialization-binary-text-and-zero-copy-contracts.md`
- Design: `design/encoding-surface-kit.md`
- Epic: `proposals/epic-encoding-surface-kit.md`
- Priority: added Encoding Surface Kit as a shortlist / Tier 0-1 candidate; framed it as the shared `encoding-surface` / `type-model-profile` / `wire-format-profile` / `borrow-zero-copy-profile` / `canonicality-compat-profile` / `stream-buffer-profile` / `encoding-adapter-profile` / `encoding-vector-set` / `encoding-check-report` boundary across Serde-backed text/binary formats, protobuf/codegen lanes, archive/zero-copy stacks, and lighter specialized alternatives rather than another derive crate, universal codec, or fake one-size-fits-all serialization badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future encoding-surface proposals keep type-model posture, wire-format semantics, borrow/zero-copy rules, canonicality/compatibility claims, streaming/buffer assumptions, and evidence distinct instead of flattening them into one fake serialization story

## New (rev0130)
- Gap: `gaps/terminal-surfaces-capabilities-input-and-render-contracts.md`
- Design: `design/terminal-surface-kit.md`
- Epic: `proposals/epic-terminal-surface-kit.md`
- Priority: added Terminal Surface Kit as a Tier 1/2 candidate; framed it as the shared `terminal-surface` / `terminal-capability-profile` / `terminal-render-profile` / `terminal-input-profile` / `terminal-unicode-layout-profile` / `terminal-graphics-profile` / `terminal-adapter-profile` / `terminal-vector-set` / `terminal-check-report` boundary across `crossterm`, Ratatui backends, `termwiz`, `anstream`, `reedline`, `vt100`, and richer terminal-protocol adapters rather than another backend facade, style crate, or screenshot-only TUI story
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future terminal-surface proposals keep terminal capabilities, rendering/input posture, Unicode layout, graphics protocol assumptions, cleanup/restore guarantees, and evidence distinct instead of flattening them into one fake terminal story

## New (rev0129)
- Gap: `gaps/process-surfaces-subprocesses-pipelines-and-supervision-contracts.md`
- Design: `design/process-surface-kit.md`
- Epic: `proposals/epic-process-surface-kit.md`
- Priority: added Process Surface Kit as a Tier 1 candidate; framed it as the shared `process-surface` / `spawn-model-profile` / `argv-env-cwd-profile` / `stdio-topology-profile` / `supervision-termination-profile` / `tty-pty-profile` / `process-adapter-profile` / `process-vector-set` / `process-check-report` boundary across `std::process`, `std::io::pipe`, Tokio, `async-process`, `duct`, `xshell`, `portable-pty`, `command-group`, `process-wrap`, `shared_child`, and signal-handling adapters rather than another shell helper, task runner, or fake universal process badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future process-surface proposals keep spawn model, argv/env/cwd posture, stdio topology, supervision/termination semantics, PTY behavior, and evidence distinct instead of flattening them into one fake subprocess story

## New (rev0128)
- Gap: `gaps/filesystem-surfaces-paths-traversal-and-durable-mutation-contracts.md`
- Design: `design/filesystem-surface-kit.md`
- Epic: `proposals/epic-filesystem-surface-kit.md`
- Priority: added Filesystem Surface Kit as a Tier 1 candidate; framed it as the shared `fs-surface` / `path-kind-profile` / `resolution-traversal-profile` / `mutation-durability-profile` / `temp-staging-profile` / `walk-watch-profile` / `fs-adapter-profile` / `fs-vector-set` / `fs-check-report` boundary across `std::fs`, nightly `std::fs::Dir`, `cap-std`, `cap-std-ext`, `camino`, `tempfile`, atomic-write helpers, `notify`, `walkdir`, and `ignore` rather than another helper facade, virtual filesystem, or fake universal path badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future filesystem-surface proposals keep authority, path identity, resolution/traversal policy, mutation/durability semantics, temp/staging behavior, and watch/walk evidence distinct instead of flattening them into one fake filesystem story

## New (rev0127)
- Gap: `gaps/time-surfaces-clocks-time-zones-and-calendrical-contracts.md`
- Design: `design/time-surface-kit.md`
- Epic: `proposals/epic-time-surface-kit.md`
- Priority: added Time Surface Kit as a shortlist / Tier 0-1 candidate; framed it as the shared `time-surface` / `clock-kind-profile` / `civil-zone-profile` / `calendar-locale-profile` / `time-storage-profile` / `time-adapter-profile` / `time-vector-set` / `time-check-report` boundary across `std::time`, Chrono, `time`, Jiff, ICU4X, SQL adapters, and deterministic-test lanes rather than another datetime crate, formatting DSL, or fake universal time badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future time-surface proposals keep clock kind, civil/offset/zoned semantics, locale/calendar rendering, storage/wire mappings, and deterministic-test evidence distinct instead of flattening them into one fake datetime story

## New (rev0126)
- Gap: `gaps/allocation-surfaces-allocators-arenas-and-memory-resource-contracts.md`
- Design: `design/allocation-surface-kit.md`
- Epic: `proposals/epic-allocation-surface-kit.md`
- Priority: added Allocation Surface Kit as a Tier 1 candidate; framed it as the shared `allocation-surface` / `memory-resource-profile` / `container-allocation-profile` / `region-lifetime-profile` / `oom-failure-profile` / `allocation-adapter-profile` / `allocation-vector-set` / `allocation-check-report` boundary across process-global allocators, allocator-generic collections, `allocator-api2`, bump/arena crates, id-arena families, and future memory-resource surfaces rather than another magical universal allocator, arena crate, or benchmark-only badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future allocation-surface proposals keep resource identity, failure posture, reclamation/reset semantics, destructor behavior, stable/nightly interop, and evidence distinct instead of flattening them into one fake memory-management story

## New (rev0125)
- Gap: `gaps/offload-surfaces-kernels-device-memory-and-accelerator-contracts.md`
- Design: `design/offload-surface-kit.md`
- Epic: `proposals/epic-offload-surface-kit.md`
- Priority: added Offload Surface Kit as a Tier 1 candidate; framed it as the shared `offload-surface` / `kernel-map` / `backend-device-profile` / `buffer-transfer-profile` / `launch-sync-profile` / `dispatch-fallback-profile` / `offload-adapter-profile` / `offload-vector-set` / `offload-check-report` boundary across `std::offload`, `wgpu` compute, `rust-gpu`, CubeCL/Burn backends, CUDA-focused wrappers, and future accelerator lanes rather than another magical unified GPU crate, backend wrapper, or benchmark-only badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future offload-surface proposals keep kernel identity, backend/device/runtime posture, memory-transfer truth, launch/synchronization semantics, dispatch/fallback lanes, and evidence distinct instead of flattening them into one fake accelerator story

## New (rev0124)
- Gap: `gaps/atomic-surfaces-orderings-progress-and-reclamation-contracts.md`
- Design: `design/atomic-surface-kit.md`
- Epic: `proposals/epic-atomic-surface-kit.md`
- Priority: added Atomic Surface Kit as a shortlist / Tier 0-1 candidate; framed it as the shared `atomic-surface` / `ordering-profile` / `target-atomic-profile` / `progress-reclamation-profile` / `shared-state-profile` / `atomic-adapter-profile` / `atomic-vector-set` / `atomic-check-report` boundary across std atomics, `portable-atomic`, `arc-swap`, `crossbeam-epoch`, Loom-tested lock-free lanes, and future kernel- or alternative-memory-model surfaces rather than another atomic wrapper, lock-free vanity crate, or fake universal concurrency badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future atomic-surface proposals keep ordering semantics, target capability, progress/reclamation, shared-state shape, and evidence distinct instead of flattening them into one fake atomic story

## New (rev0123)
- Gap: `gaps/vector-surfaces-simd-target-features-and-dispatch-contracts.md`
- Design: `design/vector-surface-kit.md`
- Epic: `proposals/epic-vector-surface-kit.md`
- Priority: added Vector Surface Kit as a shortlist / Tier 0-1 candidate; framed it as the shared `vector-surface` / `lane-shape-profile` / `target-feature-profile` / `dispatch-fallback-profile` / `alignment-layout-profile` / `operation-semantics-profile` / `vector-adapter-profile` / `vector-vector-set` / `vector-check-report` boundary across nightly `std::simd`, `safe_arch`, `multiversion`, `wide`, and coming scalable-vector/SVE lanes rather than another intrinsic wrapper, benchmark league table, or fake universal SIMD facade
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future vector-surface proposals keep lane shape, target features, dispatch/fallback posture, alignment/layout truth, operation semantics, and evidence distinct instead of flattening them into one fake vector story

## New (rev0122)
- Gap: `gaps/initialization-surfaces-in-place-construction-and-destruction-contracts.md`
- Design notes: `design/initialization-surface-kit.md`, `design/initialization-surface-lane-map.md`, `design/initialization-surface-pilot-program.md`
- Epic: `proposals/epic-initialization-surface-kit.md`
- Priority: added Initialization Surface Kit as a shortlist / Tier 0-1 candidate; framed it as the shared `init-surface` / `placement-init-profile` / `init-sequence-profile` / `pin-destruction-profile` / `init-adapter-profile` / `init-vector-set` / `init-check-report` boundary across `MaybeUninit`, `Box::pin`, `Rc::new_cyclic`, nightly `UniqueArc`, `pin-init`, `moveit`, and self-referential helpers rather than another builder macro, placement-new clone, or fake universal constructor manifest
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future initialization-surface proposals keep placement/storage, assembly phases, pinning/immobility, failure rollback, and teardown guarantees distinct instead of flattening them into one fake init story

## New (rev0121)
- Gap: `gaps/override-surfaces-global-providers-and-distributed-registration-contracts.md`
- Design: `design/override-surface-kit.md`
- Epic: `proposals/epic-override-surface-kit.md`
- Priority: added Override Surface Kit as a Tier 1 candidate; framed it as the shared `override-surface` / `provider-slot-profile` / `install-lifecycle-profile` / `scope-multiplicity-profile` / `registry-discovery-profile` / `override-adapter-profile` / `override-vector-set` / `override-check-report` boundary across `#[panic_handler]`, `#[global_allocator]`, panic and alloc-error hooks, `log`/`tracing` globals and scoped defaults, and `inventory`/`linkme` distributed registration rather than another service locator, singleton helper, or fake universal global-init manifest
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future override-surface proposals keep provider slots, install lifecycle, scope/multiplicity, distributed discovery, and fallback/composition truth distinct instead of flattening them into one fake global-config manifest

## New (rev0120)
- Gap: `gaps/synchronization-surfaces-locks-channels-and-coordination-contracts.md`
- Design: `design/synchronization-surface-kit.md`
- Epic: `proposals/epic-synchronization-surface-kit.md`
- Priority: added Synchronization Surface Kit as a shortlist / Tier 0-1 candidate; framed it as the shared `sync-surface` / `lock-profile` / `channel-profile` / `signal-permit-profile` / `shutdown-cancel-profile` / `sync-adapter-profile` / `sync-vector-set` / `sync-check-report` boundary across std, Tokio, `parking_lot`, `crossbeam-channel`, `flume`, and mixed-mode adapters rather than another lock/channel crate or fake universal concurrency primitive
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future synchronization-surface proposals keep lock semantics, queue topology, signal/permit coordination, shutdown/cancellation behavior, and verification posture distinct instead of flattening them into one fake concurrency manifest

## New (rev0119)
- Gap: `gaps/const-surfaces-compile-time-evaluable-apis-and-transition-bridges.md`
- Design: `design/const-surface-kit.md`
- Epic: `proposals/epic-const-surface-kit.md`
- Priority: added Const Surface Kit as a shortlist / Tier 0-1 candidate; framed it as the shared `const-surface` / `const-capability-profile` / `const-parameter-profile` / `const-eval-cost-profile` / `const-fallback-profile` / `const-vector-set` / `const-check-report` boundary across typenum bridges, const-generics-first APIs, fixed-capacity `no_std` structures, compile-time utility crates, and future reflection/comptime lanes rather than another numerics crate, proc-macro workaround pile, or fake universal const-ready badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future const-surface proposals keep value-level const evaluation, type-level numerics, evaluator-cost posture, fallback/migration lanes, and channel/MSRV truth distinct instead of flattening them into one fake compile-time support manifest

## New (rev0118)
- Gap: `gaps/validity-surfaces-invalid-values-and-boundary-checks.md`
- Design: `design/validity-surface-kit.md`
- Epic: `proposals/epic-validity-surface-kit.md`
- Priority: added Validity Surface Kit as a shortlist / Tier 0-1 candidate; framed it as the shared `validity-surface` / `niche-profile` / `layout-validity-profile` / `boundary-ingress-profile` / `unsafe-invariant-profile` / `validity-adapter-profile` / `validity-vector-set` / `validity-check-report` boundary across zero-copy, FFI, plugin/load-time, and unsafe abstraction lanes rather than another safe-transmute crate or fake universal safety badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future validity-surface proposals keep type initialization invariants, invalid values / niches, layout assumptions, boundary-ingress checks, library safety invariants, and evidence posture distinct instead of flattening them into one fake universal soundness manifest

## New (rev0117)
- Gap: `gaps/trait-surfaces-dyn-posture-return-shapes-and-impl-truth.md`
- Design: `design/trait-surface-kit.md`
- Epic: `proposals/epic-trait-surface-kit.md`
- Priority: added Trait Surface Kit as a shortlist / Tier 0-1 candidate; framed it as the shared `trait-surface` / `trait-semantics-profile` / `dyn-dispatch-profile` / `return-shape-profile` / `impl-coverage-profile` / `trait-adapter-profile` / `trait-vector-set` / `trait-check-report` boundary across async traits, dyn adapters, split trait families, and future evolving-trait lanes rather than another macro, trait-helper crate, or fake universal object-safety badge
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future trait-surface proposals keep semantic obligations, dyn posture, return-shape guarantees, impl coverage / blanket-impl assumptions, and adapter / migration truth distinct instead of flattening them into one fake universal trait manifest

## New (rev0116)
- Gap: `gaps/reference-surfaces-smart-pointers-and-custom-borrow-contracts.md`
- Design: `design/pointer-surface-kit.md`
- Epic: `proposals/epic-pointer-surface-kit.md`
- Priority: added Pointer Surface Kit as a shortlist / Tier 0-1 candidate; framed it as a shared `pointer-surface` / `pointer-semantics-profile` / `projection-reborrow-profile` / `receiver-dispatch-profile` / `pointer-adapter-profile` / `pointer-vector-set` / `pointer-check-report` boundary across ref-counted, pinned, foreign, and custom pointer-like types rather than another smart-pointer crate, universal trait hierarchy, or unsafe abstraction empire
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future pointer-surface proposals keep ownership/aliasing semantics, projection/reborrow behavior, receiver/dyn posture, and pin/drop guarantees distinct instead of flattening them into one fake universal smart pointer


## New (rev0115)
- Gap: `gaps/lending-surfaces-borrowing-streams-and-sequence-interop.md`
- Design: `design/lending-surface-kit.md`
- Epic: `proposals/epic-lending-surface-kit.md`
- Priority: added Lending Surface Kit as a shortlist / Tier 0-1 candidate; framed it as a shared `lending-surface` / `borrow-mode-profile` / `sequence-adapter-profile` / `yield-vector-set` / `executor-runtime-profile` / `sequence-check-report` boundary across `Iterator`, streaming/lending iterators, `Stream`, nightly `AsyncIterator`, and future reborrow/generator lanes rather than another runtime-owned facade, iterator empire, or premature universal stream crate
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future lending-surface proposals keep giving vs streaming vs lending vs async modes, invalidation rules, adapter costs, and runtime lifecycle assumptions distinct instead of flattening them into one fake universal sequence trait

## New (rev0114)
- Gap: `gaps/compile-time-guidance-and-developer-facing-tooling-extensions.md`
- Design: `design/compile-guidance-kit.md`
- Epic: `proposals/epic-compile-guidance-kit.md`
- Priority: added Compile Guidance Kit as a shortlist / Tier 0-1 candidate; framed it as a shared `guidance-surface` / `diagnostic-catalog` / `lint-catalog` / `pipeline-hook-profile` / `guidance-example-catalog` / `guidance-check-report` boundary across trait diagnostics, proc-macros, lint packs, build integrations, and future compiler-extensibility lanes rather than another lint engine, compiler plugin platform, or snapshot-only macro UX stack
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future compile-guidance proposals keep compile-time diagnostics, lint governance, runtime failures, and extension-hook authority/determinism distinct instead of flattening them into one fake universal diagnostics manifest

## New (rev0113)
- Gap: `gaps/interop-commons-and-shared-building-blocks.md`
- Design: `design/interop-commons-kit.md`
- Epic: `proposals/epic-interop-commons-kit.md`
- Priority: added Interop Commons Kit as a shortlist / Tier 0-1 candidate; framed it as a shared `interop-seam` / `shared-building-block` / `adapter-profile` / `conformance-vector-set` / `interop-check-report` boundary across proven ecosystem seams like `http`, `tower-service`, `tower-http`, and future async/shared-trait lanes rather than another mega-abstraction, facade, or silently blessed framework
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future interop proposals keep seam scope, neutral common layers, crate adapters, conformance vectors, and stewardship/adoption policy distinct instead of flattening interop into one fake universal crate

## New (rev0112)
- Gap: `gaps/ecosystem-navigation-and-reference-stacks.md`
- Design: `design/ecosystem-atlas-kit.md`
- Epic: `proposals/epic-ecosystem-atlas-kit.md`
- Priority: added Ecosystem Atlas Kit as a shortlist / Tier 1 candidate; framed it as a shared `atlas-domain` / `stack-lane` / `starter-stack` / `interop-profile` / `selection-evidence` / `atlas-check-report` boundary across official signals and community curation rather than another search engine, ranking site, or single blessed-crates page
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future ecosystem-navigation proposals keep domains, curation lanes, evidence, alternatives, and interop notes distinct instead of collapsing everything into one fake leaderboard

## New (rev0111)
- Gap: `gaps/runtime-capabilities-and-least-privilege-contracts.md`
- Design: `design/runtime-capability-kit.md`
- Epic: `proposals/epic-runtime-capability-kit.md`
- Priority: added Runtime Capability Kit as a Tier 0/1 candidate and added a steering shortlist to the top of `PRIORITIES.md` so future revisions bias toward the highest-leverage cross-cutting epics rather than adding breadth without convergence
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` so future runtime-capability proposals keep authority classes, scopes, delegation, and sandbox/enforcement layers distinct instead of flattening them into one fake universal permissions file

## New (rev0110)
- Gap: `gaps/network-protocol-transports-and-rpc-contracts.md`
- Design: `design/protocol-surface-kit.md`
- Epic: `proposals/epic-protocol-surface-kit.md`
- Priority: added Protocol Surface Kit as a Tier 1/2 candidate; framed it as a shared `protocol-surface` / `transport-profile` / `interaction-profile` / `security-profile` / `interop-check-report` boundary across `tonic`, `tonic-web`, `h2`, Quinn, `h3`, WebSocket/WebTransport crates, `rustls`, and transport-agnostic RPC crates rather than another transport, proxy, or RPC framework

## New (rev0109)
- Gap: `gaps/geospatial-data-crs-and-format-contracts.md`
- Design: `design/geospatial-surface-kit.md`
- Epic: `proposals/epic-geospatial-surface-kit.md`
- Priority: added Geospatial Surface Kit as a Tier 1/2 candidate; framed it as a shared `geo-surface` / `geometry-catalog` / `crs-profile` / `geo-check-report` boundary across GeoRust, `geo`, `geo-types`, `geozero`, `geoarrow`, `proj`, `gdal`, FlatGeobuf, and adjacent crates rather than another GIS engine, format wrapper, or map framework

## New (rev0108)
- Gap: `gaps/media-pipelines-codec-support-and-reviewable-content-contracts.md`
- Design: `design/media-surface-kit.md`
- Epic: `proposals/epic-media-surface-kit.md`
- Priority: added Media Surface Kit as a Tier 1/2 candidate; framed it as a shared `media-surface` / `media-format-catalog` / `media-processing-profile` / `media-check-report` boundary across `image`, Symphonia, `ffmpeg-next`, GStreamer Rust, `mp4parse`, `rav1e`, and adjacent crates rather than another transcoder, wrapper, or pipeline framework

## New (rev0107)
- Gap: `gaps/local-first-and-replicated-state-contracts.md`
- Design: `design/replica-surface-kit.md`
- Epic: `proposals/epic-replica-surface-kit.md`
- Priority: added Replica Surface Kit as a Tier 1/2 candidate; framed it as a shared `replica-surface` / `replica-doc-catalog` / `sync-capability-profile` / `merge-history-profile` / `replica-check-report` boundary across Automerge, Yrs/Yjs-style stacks, Loro, and persistence/adapter layers rather than another CRDT engine, sync backend, or local-first framework

## New (rev0106)
- Gap: `gaps/client-app-surfaces-and-platform-behavior-contracts.md`
- Design: `design/client-app-surface-kit.md`
- Epic: `proposals/epic-client-app-surface-kit.md`
- Priority: added Client App Surface Kit as a Tier 1/2 candidate; framed it as a shared `app-surface` / `bridge-catalog` / `app-capability-profile` / `app-lifecycle-profile` / `app-check-report` boundary across Tauri mobile, Dioxus, Slint, UniFFI, `flutter_rust_bridge`, and `cargo-mobile2` rather than another UI framework, shell, or bridge generator

## New (rev0105)
- Gap: `gaps/agentic-application-surfaces-and-tooling-contracts.md`
- Design: `design/agent-surface-kit.md`
- Epic: `proposals/epic-agent-surface-kit.md`
- Priority: added Agent Surface Kit as a Tier 1/2 candidate; framed it as a shared `agent-surface` / `prompt-catalog` / `tool-catalog` / `provider-capability-profile` / `agent-check-report` boundary across MCP, Rust agent frameworks, and provider tool/eval surfaces rather than another model wrapper, MCP helper, or agent runtime

## New (rev0104)
- Gap: `gaps/feature-rollouts-experiments-and-flag-contracts.md`
- Design: `design/rollout-surface-kit.md`
- Epic: `proposals/epic-rollout-surface-kit.md`
- Priority: added Rollout Surface Kit as a Tier 1/2 candidate; framed it as a shared `rollout-surface` / `flag-catalog` / `targeting-profile` / `exposure-profile` / `rollout-check-report` boundary across OpenFeature, Unleash, GrowthBook, Flipt, and provider-specific SDKs rather than another flag service, dashboard, or SDK wrapper

## New (rev0103)
- Gap: `gaps/search-and-retrieval-surfaces-and-ranking-contracts.md`
- Design: `design/retrieval-surface-kit.md`
- Epic: `proposals/epic-retrieval-surface-kit.md`
- Priority: added Retrieval Surface Kit as a Tier 1/2 candidate; framed it as a shared `retrieval-surface` / `corpus-profile` / `query-surface` / `ranking-profile` / `retrieval-check-report` boundary across Tantivy, Quickwit, LanceDB, Qdrant, Meilisearch, and lower-level ANN libraries rather than another search engine, vector DB, or RAG wrapper

## New (rev0102)
- Gap: `gaps/background-jobs-schedules-and-durable-work-contracts.md`
- Design: `design/background-work-kit.md`
- Epic: `proposals/epic-background-work-kit.md`
- Priority: added Background Work Kit as a Tier 1/2 candidate; framed it as a shared `work-surface` / `job-catalog` / `execution-profile` / `retry-idempotency-profile` / `work-check-report` boundary across `apalis`, `fang`, `sqlxmq`, schedulers, and durable workflow systems rather than another queue, cron crate, or workflow engine

## New (rev0101)
- Gap: `gaps/analytic-dataset-surfaces-and-table-layout-contracts.md`
- Design: `design/dataset-surface-kit.md`
- Epic: `proposals/epic-dataset-surface-kit.md`
- Priority: added Dataset Surface Kit as a Tier 1/2 candidate; framed it as a shared `dataset-surface` / `dataset-layout-profile` / `engine-capability-profile` / `dataset-check-report` boundary across Arrow, Polars, DataFusion, Parquet, `object_store`, Delta Lake, and Iceberg rather than another dataframe engine, query engine, or lakehouse format

## New (rev0100)
- Gap: `gaps/model-packaging-tokenizers-and-inference-contracts.md`
- Design: `design/model-surface-kit.md`
- Epic: `proposals/epic-model-surface-kit.md`
- Priority: added Model Surface Kit as a Tier 1/2 candidate; framed it as a shared `model-surface` / `tokenizer-profile` / `runtime-capability-profile` / `model-check-report` boundary across Candle, Burn, `ort`, `tract`, `tokenizers`, `hf-hub`, safetensors, model cards, and GGUF rather than another model runtime, inference framework, or serving stack

## New (rev0099)
- Gap: `gaps/plugin-surfaces-and-extension-contracts.md`
- Design: `design/plugin-surface-kit.md`
- Epic: `proposals/epic-plugin-surface-kit.md`
- Priority: added Plugin Surface Kit as a Tier 1/2 candidate; framed it as a shared `plugin-surface` / `extension-point-map` / `host-capability-profile` / `plugin-check-report` boundary across native loading, stable-ABI crates, Extism, Wasm components, and framework plugin ecosystems rather than another plugin runtime or loader

## New (rev0098)
- Gap: `gaps/event-driven-surfaces-and-delivery-contracts.md`
- Design: `design/event-surface-kit.md`
- Epic: `proposals/epic-event-surface-kit.md`
- Priority: added Event Surface Kit as a Tier 1/2 candidate; framed it as a shared `event-surface` / `channel-map` / `delivery-profile` / `event-check-report` boundary across AsyncAPI, CloudEvents, Kafka/NATS/AMQP clients, schema-registry helpers, and broker-backed test tooling rather than another broker client, schema registry, or queue abstraction

## New (rev0097)
- Gap: `gaps/http-service-surfaces-and-route-behavior-contracts.md`
- Design: `design/service-surface-kit.md`
- Epic: `proposals/epic-service-surface-kit.md`
- Priority: added Service Surface Kit as a Tier 1/2 candidate; framed it as a shared `service-surface` / `route-map` / `service-middleware-profile` / `service-check-report` boundary across Rust web frameworks, `tower-http`, OpenAPI generators, and HTTP contract-test tooling rather than another web framework or codegen layer

## New (rev0096)
- Gap: `gaps/authentication-authorization-and-session-contracts.md`
- Design: `design/identity-surface-kit.md`
- Epic: `proposals/epic-identity-surface-kit.md`
- Priority: added Identity Surface Kit as a Tier 1/2 candidate; framed it as a shared `identity-surface` / `principal-claims-schema` / `access-requirements-map` / `auth-check-report` boundary across password auth, sessions, OIDC/OAuth2, WebAuthn/passkeys, and authorization-policy engines rather than another batteries-included auth framework or policy engine

## New (rev0095)
- Gap: `gaps/internationalization-and-localization-contracts.md`
- Design: `design/localization-surface-kit.md`
- Epic: `proposals/epic-localization-surface-kit.md`
- Priority: added Localization Surface Kit as a Tier 1/2 candidate; framed as a shared `locale-surface` / `message-catalog` / `locale-negotiation-plan` / `locale-check-report` boundary across Fluent, ICU4X, gettext-style flows, `i18n-embed`/`cargo-i18n`, lighter key/value approaches, and framework-specific helpers rather than another localization engine or translation platform

## New (rev0094)
- Gap: `gaps/error-diagnostics-and-reviewable-failure-surfaces.md`
- Design: `design/diagnostic-surface-kit.md`
- Epic: `proposals/epic-diagnostic-surface-kit.md`
- Priority: added Diagnostic Surface Kit as a Tier 1/2 candidate; framed it as a shared `diagnostic-catalog` / `diagnostic-mapping-plan` / `diagnostic-check-report` boundary across `thiserror`, `anyhow`, `miette`, `error-stack`, `tracing-error`, path-aware deserialization diagnostics, and HTTP Problem Details crates rather than another error wrapper or pretty-printer

## New (rev0093)
- Gap: `gaps/runtime-settings-and-configuration-contracts.md`
- Design: `design/runtime-settings-kit.md`
- Epic: `proposals/epic-runtime-settings-kit.md`
- Priority: added Runtime Settings Kit as a Tier 1/2 candidate; framed as a shared `settings-schema` / `settings-source-plan` / `settings-check-report` boundary across `config`, `figment`, `confique`, `envy`, `clap`, schema generators/validators, and file-secret adapters rather than another config loader

## New (rev0092)
- Gap: `gaps/command-surface-and-cli-contracts.md`
- Design: `design/command-surface-kit.md`
- Epic: `proposals/epic-command-surface-kit.md`
- Priority: added Command Surface Kit as a Tier 1/2 candidate; framed as a shared `command-surface` / `command-example-catalog` / `command-check-report` boundary across `clap`, `clap_complete`, `clap_mangen`, `assert_cmd`, `trycmd`, `snapbox`, and Cargo subcommands rather than another parser or snapshot runner

## New (rev0091)
- Gap: `gaps/target-support-envelopes-and-runtime-baselines.md`
- Design: `design/support-envelope-kit.md`
- Epic: `proposals/epic-support-envelope-kit.md`
- Priority: added Support Envelope Kit as a Tier 1/2 candidate; framed as a shared `support-envelope` / `support-check-report` / `support-diff-report` boundary across rustc target tiers, Cargo `supported-targets`, docs.rs target metadata, CI target matrices, and runtime baselines like glibc/min-OS assumptions rather than another cross-build wrapper

## New (rev0090)
- Gap: `gaps/database-schema-query-and-migration-contracts.md`
- Design: `design/database-contract-kit.md`
- Design note: `design/database-contract-lane-map.md`
- Pilot: `design/database-contract-pilot-program.md`
- Epic: `proposals/epic-database-contract-kit.md`
- Priority: added Database Contract Kit as a Tier 1/2 candidate; framed as a shared `db-intent` / `db-schema-snapshot` / `db-query-catalog` / `db-migration-report` / `db-test-env` boundary across SQLx, Diesel, SeaORM, refinery, and Testcontainers rather than another ORM or migration runner

## New (rev0089)
- Gap: `gaps/resource-footprint-and-budget-contracts.md`
- Design: `design/footprint-kit.md`
- Epic: `proposals/epic-footprint-kit.md`
- Priority: added Footprint Kit as a Tier 1/2 candidate; framed as a shared footprint-budget / measurement-report / diff-report boundary across native size tools, Wasm retained-size analysis, stack analysis, linker layouts, and runtime allocation evidence rather than another one-off shrinker

## New (rev0088)
- Gap: `gaps/upgrade-choreography-and-reviewable-migrations.md`
- Design: `design/migration-kit.md`
- Epic: `proposals/epic-migration-kit.md`
- Priority: added Migration Kit as a Tier 1/2 candidate; framed as a shared change-intent / analysis / plan / run-report boundary across editions, dependency upgrades, toolchain/MSRV ratchets, API checks, and downstream/doc/release evidence rather than another one-shot upgrader

## New (rev0087)
- Gap: `gaps/executable-docs-and-guide-verification.md`
- Design: `design/docproof-kit.md`
- Epic: `proposals/epic-docproof-kit.md`
- Priority: added DocProof Kit as a Tier 1/2 candidate; framed as a shared guide-profile / example-catalog / doc-check-report boundary across rustdoc doctests, mdBook, docs.rs builds, CLI transcript tests, and compile-fail teaching examples rather than another docs host or style guide

## New (rev0086)
- Gap: `gaps/embedded-device-labs-and-hardware-in-the-loop.md`
- Design: `design/device-lab-kit.md`
- Epic: `proposals/epic-device-lab-kit.md`
- Priority: added Device Lab Kit as a Tier 1/2 candidate; framed as a shared device-profile / run-plan / run-report boundary across `probe-rs`, `embedded-test`, `defmt`, Embassy-era templates, and vendor bring-up flows rather than another embedded framework or flasher

## New (rev0085)
- Gap: `gaps/configuration-space-prioritization-and-reviewable-matrices.md`
- Design: `design/config-set-kit.md`
- Epic: `proposals/epic-config-set-kit.md`
- Priority: promoted and tightened the buried configuration-space-prioritization thread into Config Set Kit as a Tier 1 candidate; framed as a shared config-set / analysis / run-report boundary across `cargo-hack`, `check-cfg`, target selection, nextest, coverage, and future compiler-guided prioritizers rather than another CI generator

## New (rev0084)
- Gap: `gaps/macro-workflows-and-proc-macro-migration.md`
- Design: `design/macro-workflow-kit.md`
- Epic: `proposals/epic-macro-workflow-kit.md`
- Priority: added Macro Workflow Kit as a Tier 1/2 candidate; framed as a shared inventory / expansion / cost / debug / migration boundary for proc macros and future declarative/reflection alternatives rather than another macro helper crate

## New (rev0083)
- Gap: `gaps/custom-sysroots-and-build-std-packs.md`
- Design: `design/sysroot-pack-kit.md`
- Epic: `proposals/epic-sysroot-pack-kit.md`
- Priority: promoted and tightened the buried sysroot-packs / build-std thread into Sysroot Pack Kit as a Tier 1 candidate; framed as a shared sysroot-intent / pack / activation / report substrate for reusable custom standard-library builds rather than another org-specific cache or wrapper

## New (rev0082)
- Gap: `gaps/formal-verification-workflows-and-proof-artifacts.md`
- Design: `design/formal-verification-kit.md`
- Epic: `proposals/epic-formal-verification-kit.md`
- Priority: promoted and tightened the buried formal-verification-workflow thread into Formal Verification Kit as a Tier 1 candidate; framed as a shared verification-intent / backend-capabilities / proof-report / counterexample-pack substrate across Kani, Creusot, Prusti, Verus, ESBMC, and future proof tools rather than another verifier

## New (rev0081)
- Gap: `gaps/native-dependency-resolution-and-provider-locks.md`
- Design: `design/native-dependency-kit.md`
- Epic: `proposals/epic-native-dependency-kit.md`
- Priority: promoted and tightened the buried native-deps manager thread into Native Dependency Kit as a Tier 1 candidate; framed as a shared native-intent / provider-lock / link-plan / report substrate across `system-deps`, `pkg-config`, `vcpkg`, `cmake`, vendoring, Cargo artifacts, and external build systems rather than another provider-specific helper crate

## New (rev0080)
- Gap: `gaps/lifecycle-ledger-and-succession.md`
- Design: `design/lifecycle-ledger-kit.md`
- Epic: `proposals/epic-lifecycle-ledger-kit.md`
- Priority: promoted and merged the buried maintenance-evidence / crate-lifecycle-succession thread into Lifecycle Ledger Kit as a Tier 1 candidate; framed as a shared maintenance-intent / support-window / successor / handoff / report substrate that feeds crates.io, Cargo, and trust-policy tooling instead of overloading RustSec advisories, yanks, or README prose

## New (rev0079)
- Gap: `gaps/reproducible-build-verification-and-diffable-attestations.md`
- Design: `design/repro-build-kit.md`
- Epic: `proposals/epic-repro-build-kit.md`
- Priority: promoted and tightened the buried reproducible-build-verification thread into Repro Build Kit as a Tier 1 candidate; framed as an independent rebuild-verdict / diff-reasons / attachable-pack substrate that composes with release manifests, SBOMs, and provenance rather than equating provenance with reproducibility

## New (rev0078)
- Gap: `gaps/declarative-build-extensions-and-artifact-uplift.md`
- Design: `design/build-extension-kit.md`
- Epic: `proposals/epic-build-extension-kit.md`
- Priority: promoted and merged the buried declarative-build-extensions / build-script-final-artifacts thread into Build Extension Kit as a Tier 1 candidate; framed as a shared manifest / report / artifact-uplift substrate across metabuild, parameter passing, delegated build steps, and Cargo-managed final-artifact export rather than another build-helper crate

## New (rev0077)
- Gap: `gaps/build-system-interop-and-cargo-plumbing.md`
- Design: `design/build-interop-kit.md`
- Epic: `proposals/epic-build-interop-kit.md`
- Priority: promoted and merged the buried workspace-discovery / build-plan / event-stream thread into Build Interop Kit as a Tier 1 candidate; framed as a shared discovery / graph / plan / event substrate across Cargo plumbing, rust-analyzer discovery, and non-Cargo build systems rather than another wrapper crate

## New (rev0076)
- Gap: `gaps/sanitizers-and-dynamic-analysis.md`
- Design: `design/sanitizer-battery-kit.md`
- Epic: `proposals/epic-sanitizer-battery-kit.md`
- Priority: promoted and tightened the buried sanitizer / aliasing dynamic-analysis thread into Sanitizer Battery Kit as a Tier 1 candidate; framed as a shared profile / capability / report / suppression / pack boundary across Miri, `cargo-careful`, LLVM sanitizers, nextest-based CI, and future BorrowSanitizer-style engines rather than another checker

## New (rev0075)
- Gap: `gaps/lint-profiles-baselines-and-fixpacks.md`
- Design: `design/lint-baseline-kit.md`
- Epic: `proposals/epic-lint-baseline-kit.md`
- Priority: promoted and tightened the buried lint bundles/baselines idea into Lint Baseline Kit as a Tier 1 candidate; framed as a shared lint profile / debt baseline / report / fix-pack boundary across rustc, Clippy, rustdoc, and adjacent tools rather than another lint engine

## New (rev0074)
- Gap: `gaps/specification-traceability-and-conformance.md`
- Design: `design/spec-conformance-kit.md`
- Stack follow-on: `design/conformance-traceability-stack.md`
- Pilot follow-on: `design/spec-conformance-pilot-program.md`
- Epic: `proposals/epic-spec-conformance-kit.md`
- Priority: promoted and tightened the buried spec/conformance thread into Spec Conformance Kit as a Tier 1 candidate; later promoted it again into the emerging **Conformance Traceability Stack** so the archive now treats specification text, executable vectors, acceptance reality, and safety-critical evidence as one ranked traceability seam rather than isolated adjacent ideas

## New (rev0073)
- Gap: `gaps/mir-analysis-and-stable-export.md`
- Design: `design/mir-analysis-kit.md`
- Epic: `proposals/epic-mir-analysis-kit.md`
- Priority: promoted and tightened the buried StableMIR snapshot idea into MIR Analysis Kit as a Tier 1 candidate; framed as a shared `rustc_public` export/report/pack boundary for analyzers and verification tools rather than another one-off compiler driver

## New (rev0072)
- Gap: `gaps/airgapped-bootstrapping-and-offline-profiles.md`
- Design: `design/airgap-kit.md`
- Epic: `proposals/epic-airgap-kit.md`
- Priority: promoted and tightened the buried airgapped bootstrapping thread into Airgap Kit as a Tier 1 candidate; framed as a shared profile/lock/check/pack boundary across Cargo offline/source replacement/vendor/local registries, rustup mirrors, and existing mirror tools rather than another mirror daemon

## New (rev0071)
- Gap: `gaps/wasm-component-workflows-and-wit-packaging.md`
- Design: `design/wasm-component-kit.md`
- Epic: `proposals/epic-wasm-component-kit.md`
- Priority: promoted and merged the buried Wasm component plugin/devex lines into Wasm Component Kit as a Tier 1 candidate; framed as a shared WIT/package/composition/report boundary across plain `wasm32-wasip2` Cargo, `cargo-component`, `wit-bindgen`, `wkg`, and `wasm-tools` rather than another one-off wrapper

## New (rev0070)
- Gap: `gaps/schema-contracts-and-evolution.md`
- Design: `design/schema-contract-kit.md`
- Epic: `proposals/epic-schema-contract-kit.md`
- Priority: promoted and merged the buried schema-registry / contract-testing thread into Schema Contract Kit as a Tier 1 candidate; framed as a shared contract / diff / migration layer across Serde, JSON Schema, OpenAPI, and Protobuf rather than a hosted registry product

## New (rev0069)
- Gap: `gaps/observability-interop-and-telemetry-contracts.md`
- Design: `design/observability-kit.md`
- Epic: `proposals/epic-observability-kit.md`
- Priority: promoted Observability Kit into the concise archive as a Tier 1 candidate; positioned as a shared telemetry contract and validation layer across `tracing`, OpenTelemetry, Tokio Console, and metrics-style ecosystems rather than another logging crate

## New (rev0068)
- Gap: `gaps/deterministic-simulation-testing.md`
- Design: `design/dst-kit.md`
- Epic: `proposals/epic-dst-kit.md`
- Priority: promoted DST Kit into the concise archive as a Tier 1 candidate; positioned as the shared seed/fault/history/report substrate across Loom, Shuttle, Tokio paused-time tests, Turmoil, MadSim, and Moonpool rather than yet another simulator

## New (rev0067)
- Gap: `gaps/release-engineering-and-distribution-contract.md`
- Design: `design/release-pipeline-kit.md`
- Epic: `proposals/epic-release-pipeline-kit.md`
- Priority: promoted Release Pipeline Kit into the concise archive as a Tier 1 candidate; positioned as the release-boundary contract that composes `release-plz`, `cargo-release`, `cargo-dist`, `cargo-packager`, `cargo-binstall`, attestations, and attached evidence packs rather than replacing them

## New (rev0066)
- Gap: `gaps/coverage-evidence-and-ci-review.md`
- Design: `design/coverage-evidence-kit.md`
- Epic: `proposals/epic-coverage-evidence-kit.md`
- Priority: added Coverage Evidence Kit as a Tier 1 candidate; positioned as a convergence layer for `cargo-llvm-cov`, Tarpaulin, and CI review semantics rather than a new coverage engine

## New (rev0065)
- Gap: `gaps/reproducible-benchmarking-and-perf-regressions.md`
- Design: `design/perf-labs.md`
- Epic: `proposals/epic-perf-labs.md`
- Priority: promoted Perf Labs into the concise archive as a Tier 1 candidate; positioned as a performance evidence/review layer that converges Criterion, Iai-Callgrind, and Cargo report seams rather than replacing them

## New (rev0064)
- Gap: `gaps/async-lifecycle-and-structured-concurrency.md`
- Design: `design/async-lifecycle-kit.md`
- Epic: `proposals/epic-async-lifecycle-kit.md`
- Priority: promoted Async Lifecycle Kit into the concise archive as a Tier 1 candidate; distinct from Replay Kit because it targets default task ownership/shutdown correctness rather than post-failure reproduction

## New (rev0063)
- Gap: `gaps/resolution-explainability-and-feature-trace.md`
- Design: `design/resolution-doctor-kit.md`
- Epic: `proposals/epic-resolution-doctor-kit.md`
- Priority: promoted Resolution Doctor Kit to Tier 0/1 as a shared substrate for Feature Kit, Public API Kit, Policy Kit, and future Cargo plumbing/report work

## New (rev0062)
- Gap: `gaps/public-api-semver-msrv.md`
- Design: `design/public-api-kit.md`
- Epic: `proposals/epic-public-api-kit.md`
- Hygiene: strengthened `meta/AMNESIA_RESISTORS.md` to prefer promoting buried Tier-1 ideas into the concise archive before inventing net-new ones

## New (rev0061)
- Gap: `gaps/ffi-boundary-contracts.md`
- Design: `design/ffi-boundary-kit.md`
- Epic: `proposals/epic-ffi-boundary-kit.md`
- Hygiene: `meta/AMNESIA_RESISTORS.md`
- Repair: restored missing top-level debugger files referenced by rev0060 (`gaps/debugger-interop-and-visualizers.md`, `design/debugger-experience-kit.md`, `proposals/epic-debugger-experience-kit.md`)

## New (rev0060)
- Gap: `gaps/debugger-interop-and-visualizers.md`
- Design: `design/debugger-experience-kit.md`
- Epic: `proposals/epic-debugger-experience-kit.md`

## New (rev0040)
- Gap: `gaps/userwide-build-cache.md`
- Design: `design/build-cache-kit.md`
- Epic: `proposals/epic-build-cache-kit.md`

## New (rev0041)
- Gap: `gaps/crate-trust-signals.md`
- Design: `design/trust-signals-kit.md`
- Epic: `proposals/epic-trust-signals-kit.md`

## New (rev0042)
- Gap: `gaps/secrets-and-credentials-ux.md`
- Design: `design/credentials-kit.md`
- Epic: `proposals/epic-credentials-kit.md`

## New (rev0043)
- Gap: `gaps/downstream-testing.md`
- Design: `design/downstream-testing-kit.md`
- Epic: `proposals/epic-downstream-testing-kit.md`

## New (rev0044)
- Gap: `gaps/signed-prebuilt-binaries.md`
- Design: `design/signed-binaries-kit.md`
- Epic: `proposals/epic-signed-binaries-kit.md`

## New (rev0045)
- Gap: `gaps/typosquatting-and-impersonation.md`
- Design: `design/typosquat-guard-kit.md`
- Epic: `proposals/epic-typosquat-guard-kit.md`

## New (rev0046)
- Gap: `gaps/unified-dependency-policy.md`
- Design: `design/policy-kit.md`
- Epic: `proposals/epic-policy-kit.md`

## New (rev0047)
- Gap: `gaps/ecosystem-incident-response.md`
- Design: `design/incident-kit.md`
- Epic: `proposals/epic-incident-kit.md`

## New (rev0048)
- Gap: `gaps/standardized-cargo-reports.md`
- Design: `design/cargo-report-kit.md`
- Epic: `proposals/epic-cargo-report-kit.md`

## New (rev0049)
- Gap: `gaps/procmacro-buildscript-transparency.md`
- Design: `design/compile-time-capabilities-kit.md`
- Epic: `proposals/epic-compile-time-capabilities-kit.md`

## New (rev0050)
- Gap: `gaps/workspace-composition-governance.md`
- Design: `design/workspace-governance-kit.md`
- Epic: `proposals/epic-workspace-governance-kit.md`

## New (rev0051)
- Gap: `gaps/org-ownership-and-registry-ux.md`
- Design: `design/org-identity-registry-ux-kit.md`
- Epic: `proposals/epic-org-identity-registry-ux-kit.md`

## New (rev0052)
- Gap: `gaps/cross-compilation-just-works.md`
- Design: `design/cross-toolchain-kit.md`
- Epic: `proposals/epic-cross-toolchain-kit.md`

## New (rev0053)
- Gap: `gaps/deterministic-async-debugging.md`
- Design: `design/replay-kit.md`
- Epic: `proposals/epic-replay-kit.md`

## New (rev0054)
- Gap: `gaps/feature-graph-control.md`
- Design: `design/feature-kit.md`
- Epic: `proposals/epic-feature-kit.md`

## New (rev0055)
- Gap: `gaps/a11y-and-ui-testing-substrate.md`
- Design: `design/a11ykit-ui-testing.md`
- Epic: `proposals/epic-a11ykit.md`

## New (rev0056)
- Gap: `gaps/unsafe-and-verification-evidence.md`
- Design: `design/safety-evidence-kit.md`
- Epic: `proposals/epic-safety-evidence-kit.md`

## New (rev0057)
- Gap: `gaps/single-file-scripts-first-class.md`
- Design: `design/scriptkit.md`
- Design: `design/scriptkit-pilot-program.md`
- Epic: `proposals/epic-scriptkit.md`

## New (rev0058)
- Gap: `gaps/crosslang-compiledb-ide.md`
- Design: `design/compiledb-kit.md`
- Epic: `proposals/epic-compiledb-kit.md`

## New (rev0059)
- Gap: `gaps/fuzzing-orchestration.md`
- Design: `design/fuzzpack-kit.md`
- Epic: `proposals/epic-fuzzpack-kit.md`

- Priority: rewrote **Wasm Component Kit** around `component-subject` / `wit-resolution-lock` / `component-surface-report` / `component-host-requirement-profile` / `composition-plan` / `composition-run-report` / `component-compat-report` / `component-publish-report`, and promoted it from Tier 1 to Tier 0/1 so the archive treats WIT/package identity, composition evidence, host requirements, and publication truth as separate first-class artifacts rather than one vague “component build” story.
