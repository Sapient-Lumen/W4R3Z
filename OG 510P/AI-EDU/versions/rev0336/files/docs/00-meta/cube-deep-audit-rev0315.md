# rev0315 cube deep audit: mission, missing center, waste, and repair

## Executive judgment

The heart of AI-EDU is unusually strong and still worth preserving: redesign education for an
AI-normal world so that technology increases understanding, learner agency, access, teacher
capacity, and institutional truth without weakening human responsibility or proof of learning.

The archive's active behavior, however, has drifted. It now acts primarily as an assurance case and
release-control machine for one hypothetical evidence import. That machinery contains valuable
ideas—source truth, human authority, privacy, contestability, claim ceilings, rollback, and no-fake-
evidence boundaries—but the means have become larger and more visible than the educational end.

The most important correction is not to abandon governance. It is to restore hierarchy:

> pedagogy and learning are the mission; evidence operations make that mission trustworthy;
> release controls support the evidence operations; historical controls remain quiet until needed.

## What the mission really is

The charter, design principles, and reference model converge on five outcomes:

1. **Understanding:** students should develop transferable knowledge and judgment, not merely submit
   better-looking products.
2. **Agency:** AI should widen the learner's ability to inquire, practice, reflect, and contest—not
   make the learner dependent on opaque answers.
3. **Teacher capacity:** automate or assist work that drains attention while strengthening teacher
   planning, feedback, diagnosis, care, and escalation.
4. **Access:** make explanation, language support, accommodations, and high-quality guidance more
   available without turning vulnerability into a surveillance record.
5. **Institutional truth:** keep claims proportional to evidence; preserve accountable decisions,
   source lineage, appeal, and the distinction between local signals and public proof.

The reference model's best sentence remains the center: AI should expand explanation, feedback,
access, teacher capacity, institutional learning, and lifelong opportunity without replacing human
responsibility, weakening proof of learning, hiding decisions, or turning support records into
surveillance.

## What is missing

### 1. The external truth the live rail was built to receive

`FT-0181` has one genuine blocker: there is no real owner-reviewed `SRC2+` packet. The cube has
prepared many increasingly precise representations of contact, return, review, decision, change,
activation, readout, and closure, but it has not crossed the human boundary. No owner contact means
no empirical feedback about whether the request is understandable, whether the owner exists, what
records actually exist, or which controls matter in practice.

### 2. A visible pedagogical intervention portfolio

The archive describes a whole educational order, yet current revision energy is concentrated on one
operational import chain. Missing from the live center is a small portfolio of testable education
interventions: for example, tutor coaching, feedback that elicits revision, teacher planning support,
accessible explanation, or AI-resistant proof-of-learning routines. Each needs a theory of change,
learner activity, teacher role, comparison, outcome measure, process measure, access check, workload
measure, and stop rule.

### 3. A data plane paired with the control plane

The cube has an extensive control plane but almost no real observations flowing through it. A useful
system needs both: controls that bound action, and a data plane containing owner returns, decisions,
implementation observations, learner evidence, teacher evidence, adverse events, and revisions. A
control with no real cycle cannot show whether it prevents harm, changes a decision, or merely adds
steps.

### 4. Deletion, consolidation, and burden accounting

Earlier audits explicitly declared control saturation and said no new control should be added until a
real packet exposed a gap. Growth continued. The rev0314 archive contained 720 files: 494 Markdown,
121 Python, 102 JSON, two CSV files, and a Makefile—about 932,000 whitespace-delimited words. Roughly
38% of the words sat in governance; only about 1.2% sat in core and assessment together. The archive
contains 79 cube-deep-audit files, 45 mission kernels, 44 risk-burndown files, and many revision-
specific release examples. That is not proof that the content is useless; it is strong evidence that
deletion and retrieval costs have not been treated as first-class design variables.

The missing metrics are simple: startup links, operator commands, files touched, elapsed minutes,
number of human decisions, number of controls that changed a decision, and controls retired after a
cycle.

## Where something went severely wrong

### Passing lint changed the thing being inspected

The clearest executable failure was not philosophical. `make lint-fast` could pass and leave
synthetic `real-owner-packet.csv` files and review briefs in the live field tree. The field report
then counted escaped review briefs as live state. This violated the archive's own validation-fixture
firebreak and made a successful assurance run produce false operational residue.

Rev0315 repairs the checks and adds a suite-level invariant: after ignored validation fixtures are
cleaned, selected lint lanes must leave non-fixture field state byte-for-byte unchanged. It also
cleans validator-only lanes on normal exit and `SIGTERM`/`SIGINT`/`SIGHUP`; a forced interruption
test preserved an operator-owned sentinel while removing validation residue.

### The no-new-control rule became advisory prose

The saturation record says `SAT4`, `new_control_allowed: false`, and lists no uncovered risk. Yet
successive revisions kept adding surfaces while the sole external blocker remained. Some additions
closed real seams, but the aggregate pattern is control-plane self-expansion. The rule lacked an
enforcement mechanism that matters more than another lint: revision planning did not require an
explicit choice among field evidence, pedagogical evidence, or burden reduction.

Rev0315 puts that choice in the charter and handoff. It does not add a gate for it; the correction is
to stop rewarding surface count.

### Navigation and release history overstated coherence

The supposedly compact re-entry map pointed to rev0302 while the release was rev0314 and exposed a
long downstream chain. The context startup list sat at its maximum of 32 entries. The changelog had
five `# Changelog` headings, began before its title, omitted rev0313 despite naming it as the previous
revision, and duplicated several revision headings. Existing validators checked only the first
matching revision and link-count ceilings, so they certified documents whose semantic role had
drifted.

Rev0315 repairs the documents and strengthens existing checks to verify the current revision,
previous-revision continuity, one title, unique headings, and a genuinely compact startup path.

### Source labels were more confident than source provenance

Bibliography entries B108 and B122 called a privately operated AI Act explainer “official.” The
archive already held the official EUR-Lex text elsewhere. The URLs and wording are corrected. This
is a small defect with large symbolic importance: a source-truth project must not relax provenance
standards in its own bibliography.

## What current external evidence suggests

The research does not support either “deploy broadly” or “freeze until certainty.” It supports
bounded, pedagogically explicit, human-led experiments.

- OECD's 2026 synthesis says generative AI can support learning when guided by clear teaching
  principles, while task outsourcing without pedagogical support can improve apparent performance
  without real learning. That maps directly to the archive's learning-over-output thesis (B11/B107).
- UNESCO's teacher framework defines 15 competencies across human-centred mindset, ethics, AI
  foundations and applications, AI pedagogy, and professional learning. A serious mission therefore
  needs a teacher capability program, not only procurement and evidence controls (B03/B152).
- Tutor CoPilot's randomized trial involved more than 700 tutors and 1,000 students; students were
  four percentage points more likely to master topics, with a nine-point gain among lower-rated
  tutors, at roughly $20 per tutor per year. This is exactly the kind of human-augmentation hypothesis
  AI-EDU should represent and test (B13/B279).
- Stanford SCALE's 2026 K–12 review says the research base is growing but rigorous causal evidence
  remains thin. That justifies evidence humility and targeted trials—not years of pretrial control
  expansion (B133).
- NIST's generative-AI profile supports provenance, monitoring, human review, and risk management
  aligned to organizational goals. Those ideas validate the strongest controls here, but alignment
  means the control burden should be proportional to the actual educational use and decision stakes
  (B275).
- Current EU AI Act guidance treats specified education uses—such as consequential admission,
  assignment, learning-outcome evaluation, level assessment, and test monitoring—as high-risk. This
  supports strict controls in consequential lanes, not universalizing the same burden to every
  bounded teacher-support experiment (B287/B291).
- U.S. Department of Education guidance permits responsible AI uses under existing program and legal
  obligations and frames AI as support for teaching, learning, access, and educators rather than a
  replacement for educators (B101/B283).

## Architectural speculation

These are hypotheses, not findings from a real field cycle.

### The cube has become an assurance case without its paired program

The current archive resembles a high-integrity assurance case: many claims, hazards, controls,
artifacts, and traceability links. What is absent is the educational program whose assurance case it
is. A healthier architecture would have three layers:

1. **Public mission and pedagogy:** a small set of human-readable models, intervention patterns,
   assessment designs, evidence summaries, and open decisions.
2. **Thin live rail:** the current router plus only the controls needed for the actual use case and
   stakes.
3. **Cold assurance history:** schemas, old audits, branch tails, fixtures, and release examples kept
   searchable but removed from ordinary startup and planning.

### Controls need a half-life

After one real cycle, every control should answer: What decision did I change? What harm did I
prevent? What evidence would justify keeping me? A control that did none of those should merge,
move to cold history, or retire. This is not anti-safety. It is how safety systems avoid becoming so
complex that operators route around them or stop doing the underlying work.

### The next flagship should be teacher/tutor augmentation

The most mission-aligned next study is probably a bounded human-augmentation intervention, not an
agentic student replacement. A candidate would provide tutors or teachers with real-time prompts for
probing questions, misconception diagnosis, or feedback moves; compare against ordinary support;
and measure learner transfer, educator practice, access, workload, and inappropriate dependence.
The Tutor CoPilot evidence gives this hypothesis empirical plausibility, while the SCALE review
requires local humility.

### The archive may need a deliberate pause after real contact

Once owner contact occurs, the most valuable revision may be subtractive: measure where the owner
was confused, which artifacts were never used, how many commands were necessary, and which controls
did not change any decision. Then remove or archive them before extending the chain.

## Changes made in rev0315

- Repaired lint live-lane contamination and added a byte-state invariant to the existing runner.
- Moved escaped synthetic packets and review briefs into validation scratch, including a second
  terminal-brief default-path leak, and added normal-exit plus signal cleanup.
- Recentered charter, README, startup, and agent handoff on education rather than FT-0181.
- Reduced re-entry to ten current surfaces and reduced generated startup context.
- Repaired changelog title/continuity/duplicate structure and strengthened the existing receipt check.
- Corrected B108/B122 to official EU sources.
- Added no schema, branch family, or new release-control validator.

## Priority sequence

The next sequence should be deliberately small:

1. Human owner contact or documented route block.
2. One real packet through the existing rail, stopping at each human decision.
3. One bounded pedagogical pilot with explicit learning and teacher-practice measures.
4. A post-cycle deletion and burden audit before any new control family.

No real field evidence was created by this audit. The repair makes the cube more truthful and less
self-contaminating; only a real cycle can show which larger architectural speculation is correct.
