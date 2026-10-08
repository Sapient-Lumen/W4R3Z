# General-purpose versus purpose-built deployment ladder

This document closes the next procurement gap after stake scaling and evidence thresholds.

Institutions now need a rule that avoids two bad extremes:

- **consumer-chat absolutism** — one general-purpose chatbot quietly becomes the answer to tutoring, advising, accessibility, and assessment;
- **premature bespoke panic** — institutions assume no meaningful AI use can begin until every use case has a fully custom platform.

The archive's current bet is:

> allow general-purpose AI for bounded low-stakes open use; require institutional wrappers or purpose-built educational tools as dependence, data sensitivity, pedagogical specificity, or rights stakes rise; never delegate final educational judgment.

Current public signals point this way. OECD's 2026 education work argues both that general-purpose GenAI tools are not designed to help students learn and that specialized tools grounded in learning science show more promise when evaluated seriously. UNESCO's 2026 Charter for Public Digital Learning Platforms says digital learning environments should support the public mission of education and serve teachers, learners, and families as governed digital commons. The European Commission's updated 2026 educator guidance treats AI use as a context-based ethical and legal decision, not free classroom improvisation. U.S. DOE's 2025 guidance explicitly names AI-enabled instructional materials, tutoring, advising, and navigation as allowable public uses under current programs, while IES's U-GAIN portfolio keeps concentrating public R&D on designed agents for tutoring and teacher support rather than unmanaged consumer chat alone. Tutor CoPilot remains a useful concrete example: the gain came from a human-AI tutoring system that improved tutoring moves, not from giving students a raw answer engine. See `B08`, `B11`, `B12`, `B13`, `B24`, `B99`, `B100`.

## The five deployment levels

The archive now names five levels.

### `D0` — optional open use

Examples:

- a teacher using a general-purpose model for private brainstorming;
- an adult learner using a public chatbot for optional study help;
- a student using an allowed `OPEN-AI` tool for low-stakes exploration outside any required institutional workflow.

**Default rule:** tolerated only where the institution is **not** making the tool part of its official support infrastructure.

Why this level exists:

- general-purpose tools are already common;
- some exploratory or adult self-directed use should not require a procurement process;
- but optional use is not the same as institutional dependence.

### `D1` — bounded instructional allowance

Examples:

- teachers allowing a general-purpose tool for brainstorming, translation of administrative text, retrieval-practice generation, or low-stakes feedback;
- students using a general-purpose tool inside a clearly tagged `OPEN-AI` assignment;
- staff piloting light workflow support without routing protected support cases or persistent learner histories through the tool.

**Default rule:** acceptable for low-stakes, reversible, clearly bounded use when the course grammar and privacy floor already exist.

Minimum conditions:

- the task rule is explicit (`NO-AI`, `GUIDED-AI`, `OPEN-AI` plus disclosure/proof);
- no hidden institutional claim that the tool is official tutoring or official advising;
- no dependence on opaque detector or surveillance backfill when the tool is used;
- and no requirement that minors or vulnerable learners create unmanaged personal accounts as the only path to participation.

### `D2` — institutionally wrapped general-purpose use

Examples:

- a school- or university-provided workspace built on a general-purpose model;
- a governed institutional assistant for study help, drafting support, or teacher productivity;
- a library or workforce-navigation front door that uses a general model inside a public institutional shell with published limits and fallback.

**Default rule:** minimum required when the institution recommends, provisions, or normalizes repeated student-facing use at scale.

Minimum conditions:

- published privacy, retention, and visibility rules;
- accessibility review and a non-AI fallback;
- age-appropriate settings and family legibility where relevant;
- clear boundary between pedagogical use and protected accessibility/accommodation routing;
- and human override paths when the assistant fails, confuses, or overreaches.

This level is often enough for governed access to generic capabilities. It is **not** enough by itself to justify stronger claims about learning improvement.

### `D3` — pedagogically explicit or purpose-built educational AI

Examples:

- tutoring systems;
- adaptive practice tools;
- formative-feedback systems making improvement claims;
- advising and navigation tools that shape pathway choice;
- teacher copilots that claim to improve instruction rather than merely compress workflow.

**Default rule:** preferred and often required whenever the institution is making a recurring pedagogical or developmental claim.

Minimum conditions:

- explicit theory of change;
- visible pedagogical structure rather than answer delivery alone;
- teacher or advisor escalation path;
- local evaluation against current practice;
- and compatibility with the archive's course grammar, proof layer, and accessibility/protected-support rules.

A purpose-built tool may still sit on top of a general-purpose model. What matters is that the **service shape** is educationally explicit and governable.

### `D4` — human-accountable determination

Examples:

- grading and final credential awards;
- placement, progression, or exclusion decisions;
- admissions, discipline, or high-stakes advising triage;
- disability/accommodation determinations;
- safety-relevant readiness judgments.

**Default rule:** AI may assist humans here, but final judgment, explanation, appeal, and accountability stay human.

This is the archive's non-delegation floor. A tool can summarize, suggest, surface options, or help a professional review evidence. It cannot quietly become the decision-maker.

## Triggers that move a use case rightward

Move a use case toward a higher deployment level when one or more of the following are true:

- the tool is required or strongly normalized rather than merely tolerated;
- minors, novice learners, or otherwise vulnerable populations are the main users;
- the system stores persistent learner histories, profiles, or nudges;
- the tool mediates accessibility, accommodation, or multilingual access for official participation;
- the institution is making a tutoring, advising, or learning-improvement claim;
- the output influences progression, opportunity, resources, or risk;
- teacher/advisor visibility, family notice, or human fallback would matter if the tool failed;
- or the institution would struggle to explain why the tool is the right fit if challenged publicly.

The compact heuristic is simple:

> the more a tool behaves like educational infrastructure, the less a bare consumer chatbot is enough.

## What schools and providers should publish

For each recurring institutional AI use case, publish only four things:

1. which deployment level (`D0-D4`) it occupies;
2. whether the system is tolerated, wrapped, purpose-built, or human-accountability-only;
3. what interaction data, if any, are visible to staff and how long they are retained;
4. what the human fallback and appeal path are.

That is usually enough to stop the common confusion where a course rule describes task-level AI use, but nobody can tell whether the institution is also endorsing the underlying tool as infrastructure.

The archive now adds six narrower companion surfaces: [`student-facing-function-deployment-defaults-and-handoff-triggers.md`](student-facing-function-deployment-defaults-and-handoff-triggers.md), which publishes starter defaults for recurring functions such as FAQ, study help, tutoring, advising, accessibility routing, and well-being support; [`sector-and-age-profile-splits-for-student-facing-defaults.md`](sector-and-age-profile-splits-for-student-facing-defaults.md), which names the places where those learner-facing defaults should already split by sector and age band before local evidence accumulates; [`teacher-facing-function-delegation-defaults-and-sign-off-triggers.md`](teacher-facing-function-delegation-defaults-and-sign-off-triggers.md), which publishes starter defaults for recurring teacher-side functions such as planning, materials drafting, feedback assistance, marking support, analytics, and outward communication; [`sector-and-age-profile-splits-for-teacher-facing-defaults.md`](sector-and-age-profile-splits-for-teacher-facing-defaults.md), which names the places where those teacher-facing defaults should already split by sector and age band before local evidence accumulates; [`institution-facing-decision-support-defaults-and-contestability-triggers.md`](institution-facing-decision-support-defaults-and-contestability-triggers.md), which publishes starter defaults for recurring institution-side functions such as clerical compression, queueing, risk flags, allocation, and formal decision support; and [`sector-and-office-profile-splits-for-institution-facing-defaults.md`](sector-and-office-profile-splits-for-institution-facing-defaults.md), which names the places where those institution-side defaults should already split by sector and office type before local evidence accumulates.

## Current archive bet

The archive's current best guess is that a **deployment ladder** will outperform both extremes:

- treating all general-purpose AI as categorically unusable in education;
- and treating one unmanaged consumer chatbot as sufficient institutional infrastructure.

That claim is now canon, but still live. The next problem is narrower: which of the starter function defaults and sector/office profile splits are stable enough to harden across age bands and sectors, where they need further branching, and where real implementation evidence should force retreat back toward human-only handling. See `OQ-0004`, `OQ-0007`, and `OQ-0009`.
