# Student-facing function deployment defaults and handoff triggers

This document closes the archive's next implementation gap about **which recurring student-facing functions can safely remain at the institutionally wrapped general-purpose layer and which should escalate to pedagogically explicit tools or back to human-accountable handling**.

The archive's current bet is:

> publish a very small function-family default table, keep the leftmost safe posture visible, and force explicit human handoff when the function starts carrying developmental, rights, or consequence-bearing weight.

The point is to avoid four predictable failures at once:

- **wrapper complacency** — once an institution has a governed chatbot shell, it quietly gets used for tutoring, advising, and support functions it was never designed to carry;
- **service-shape confusion** — task-level course permissions (`OPEN-AI`) are mistaken for permission to make the same tool official institutional infrastructure;
- **hidden rights drift** — accessibility, advising, or student-support questions slide into opaque automation without clear human owners;
- **panic by exception** — institutions answer these risks with broad bans because they lack a compact default table for ordinary cases.

Current public signals point in a convergent direction. OECD's 2026 work says general-purpose GenAI can sometimes help pedagogically, but specialised tools designed around learning show more promise and should be scrutinised seriously. U.S. DOE's 2025 guidance explicitly names AI-enabled instructional materials, tutoring, pathway exploration, advising, and navigation as allowable public uses, but it also says AI should support educators rather than replace them. UNESCO's 2026 Charter for Public Digital Learning Platforms treats digital learning environments as governed public infrastructure serving teachers, learners, and families. The European Commission's updated 2026 educator guidance frames AI use as a context-based ethical and legal decision rather than a free-form classroom improvisation. The UK Department for Education's current product-safety standards now explicitly include cognitive development, emotional and social development, mental health, and manipulation. Medical-education guidance from the AAMC adds a sharper professional constraint: maintain human-centered focus, equal access, privacy, and frequent evaluation in place of use. See `B11`, `B24`, `B94`, `B99`, `B100`, `B101`, `B102`.

## Relationship to the deployment ladder

This document does not replace [`general-purpose-vs-purpose-built-deployment-ladder.md`](general-purpose-vs-purpose-built-deployment-ladder.md).

It adds one thing only:

- a **starter default table** for recurring student-facing functions.

Its new companion surface, [`sector-and-age-profile-splits-for-student-facing-defaults.md`](sector-and-age-profile-splits-for-student-facing-defaults.md), names the places where those generic learner-service defaults should already split by sector and age band before local evidence accumulates. The archive now also pairs this table with [`persistent-memory-personalization-and-learner-model-boundaries.md`](persistent-memory-personalization-and-learner-model-boundaries.md) so “study help with memory” does not quietly turn into predictive learner modeling or cross-function nudging.

The ladder still supplies the levels (`D0-D4`). This document supplies default placements for common institutional service shapes plus the handoff triggers that should stop a wrapped chatbot from quietly becoming a tutor, advisor, counselor, or decision-maker.

It also does **not** replace the archive's protected support rail. Accessibility, accommodation, and multilingual-access functions still follow [`accommodation-aware-disclosure-and-accessibility.md`](accommodation-aware-disclosure-and-accessibility.md) plus the `A1-A5` / override-row grammar. This document only says how those functions should sit on the deployment ladder when they are provided as official student-facing services.

It now also has a narrow companion surface, [`learning-first-interaction-defaults-and-answer-release-triggers.md`](learning-first-interaction-defaults-and-answer-release-triggers.md), because deployment level alone does not tell institutions whether a governed study tool behaves like diagnosis and scaffolded support, like an answer engine in a school wrapper, or like endless refusal theater — nor whether the same answer-release posture really travels across age bands, constructs, access conditions, and task modes, nor when repeated dependence should leave AI-owned interaction and move onto a teacher-owned recovery path.

## The starter default table

The archive's starter set is intentionally tiny. These are **minimum default placements**, not universal mandates.

| Function family | Ordinary examples | Default minimum | Leftmost safe posture | Move right or hand off when... |
|---|---|---|---|---|
| `SF-ADMIN` | course FAQ, calendar reminders, deadline lookup, room/location help, generic policy wayfinding | `D2` | wrapped assistant with current source material, visible limits, and easy human fallback | the answer depends on a case-specific exception, contested record, or consequence-bearing interpretation |
| `SF-STUDY` | study Q&A, concept explanation, retrieval-practice generation, low-stakes worked examples, optional study companion | `D2` | bounded study help in a governed wrapper, especially for older learners and low stakes | the institution starts claiming tutoring gains, using persistent learner profiles, or making the tool required rather than optional |
| `SF-FEEDBACK` | drafting support, code-debug suggestions, revision prompts, bounded formative critique | `D2` | generic bounded feedback where the learner still owns the work and a teacher still owns the instructional judgment | feedback becomes recurring official instructional guidance tied to learner history, grades, or next-step pathway decisions |
| `SF-TUTOR` | adaptive practice, guided misconceptions work, sequenced tutoring dialogue, high-impact tutoring augmentation | `D3` | pedagogically explicit tutoring or practice tool with teacher/tutor visibility and local evaluation | the system begins shaping progression, access to opportunities, or unattended remediation intensity without accountable human review |
| `SF-ADVISE` | pathway exploration, course planning support, financial-aid or transfer navigation, college/career exploration | `D3` | pedagogically or procedurally explicit advising tool with published limits and named human owner | the output affects placement, admissions, aid, discipline, exclusion, or other consequence-bearing determinations; those remain `D4` |
| `SF-ACCESS` | multilingual access, executive-function support, accessible navigation, accommodation-intake assistance, protected support routing | `D2` for delivery/intake, `D4` for determinations | governed access-support shell with privacy, accessibility, and non-AI fallback, routed on the protected support rail | the question becomes a formal accommodation decision, a construct-sensitive override, or a rights dispute requiring accountable human review |
| `SF-WELL` | well-being check-ins, emotional support prompts, crisis routing, safeguarding concern intake | `D4` | human-accountable service; AI may at most assist with bounded routing, off-hours holding responses, or resource surfacing | distress, manipulation risk, self-harm/safety concern, abuse/coercion signal, or any situation where trust and duty of care require a trained human owner |

## Reading the table correctly

The table gives **default floors**, not product categories.

A general-purpose model can sit underneath several rows. What changes is the **service shape**:

- a governed FAQ shell may be acceptable at `SF-ADMIN`;
- the same underlying model is not automatically acceptable as `SF-TUTOR` or `SF-ADVISE` without movement to `D3`;
- and it is not acceptable as the final actor in `SF-WELL`, accommodation determination, placement, or other `D4` decisions.

The archive is therefore classifying **institutional roles**, not brand names.

## The handoff triggers

The archive now names six generic handoff triggers. They are meant to be easy to publish and easy to remember.

### `H1` — case-specific exception or record conflict

The question turns on an individual record, deadline exception, waiver, appeal, or contradictory source.

### `H2` — rights, accommodation, or protected-support judgment

The question becomes about disability accommodation, language-access duty, privacy, formal support status, or a construct-sensitive override.

### `H3` — progression, opportunity, or sanction consequence

The output could materially affect course access, placement, progression, aid, credentialing, discipline, or comparable opportunities.

### `H4` — persistent confusion, repeated failure, or dependence signal

The system is no longer helping the learner progress, or the learner is repeatedly seeking fuller answers without later reconstruction. The next move is a named recovery path — bounded reset, temporary cool-down, or teacher/tutor inspection — rather than one more unguided AI turn. See [`learning-first-interaction-defaults-and-answer-release-triggers.md`](learning-first-interaction-defaults-and-answer-release-triggers.md).

### `H5` — distress, safeguarding, manipulation, or acute-risk signal

The interaction raises mental-health, coercion, abuse, exploitation, or safety concerns, or the service shape itself could become manipulative. This is the clearest reason to keep well-being and crisis handling on a human-accountable footing.

### `H6` — official determination or accountable sign-off

A human now needs to make, explain, or sign off on the decision because the institution is acting rather than merely helping the learner explore.

## Age-band and stakes modifiers

The archive's default modifiers are deliberately simple.

- **Move one step right for minors** when the function is repeated, required, or profile-building rather than occasional and optional.
- **Move one step right for persistent learner modeling** when the system stores histories, nudges, or inferred risk/progress states over time.
- **Move one step right for requirement** when participation in the tool becomes the ordinary path rather than one available path among others.
- **Never move left of the protected-support rule** for accessibility, accommodation, or multilingual access functions.
- **Never move left of `D4`** for final determinations, safeguarding ownership, or consequence-bearing judgments.

These are intentionally rough defaults. The archive prefers a short visible modifier rule over false precision.

## What institutions should publish

For recurring student-facing services, publish one compact table with only six fields:

1. function family (`SF-ADMIN` through `SF-WELL` or local equivalent);
2. default deployment level (`D2-D4`);
3. age/stakes modifiers if different from the archive default;
4. what interaction data are visible to staff, at what observability level, and for how long;
5. which handoff triggers apply;
6. the named human owner or team.

This is usually enough to stop the common failure where a school publishes task-level AI rules but never states whether official tutoring, advising, accessibility routing, or student-support functions are also being mediated by the same tool. The archive now pairs that publication rule with a separate cross-cutting observability/retention grammar in [`minimum-observability-and-retention-without-surveillance.md`](minimum-observability-and-retention-without-surveillance.md).

## What counted as a real archive gain

The archive now does more than say “use a deployment ladder.” It now publishes compact starter defaults for the most common student-facing function families plus explicit handoff triggers, and it now has a companion profile layer for the learner-serving contexts that are already different enough to need stricter inherited floors before local evidence accumulates. That is a meaningful operating step because it blocks both lazy moves at once: one wrapped chatbot quietly expanding from FAQ to tutor to advisor to counselor, and one generic learner-service table being treated as equally safe for minors, adults, professional trainees, and public-route users.

## Current archive bet

The archive's current best guess is that a tiny function-family default table plus explicit handoff triggers, paired with a tiny sector-and-age profile layer, will outperform both extremes:

- one general rule for all student-facing AI services;
- and case-by-case procurement improvisation with no published default levels.

That claim is now canon, but still live. The next problem is narrower: which of these starter profiles are stable enough to harden, where they should branch further by stakes or programme type, and where real implementation evidence should force retreat back toward human-only handling. See `OQ-0004`.
