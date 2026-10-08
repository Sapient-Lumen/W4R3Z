# Reusable starter override rows for construct-sensitive supports

This document closes the archive's next implementation gap about **which subject- and age-sensitive override rows are portable enough to inherit as starter defaults** rather than being rebuilt from scratch by every programme, district, or institution.

The archive's current bet is:

> publish a very small starter row set for repeated construct-sensitive cases, mark those rows as provisional by default, and require short local reasons only when a system materially narrows, broadens, splits, or declines to inherit them.

The point is to avoid four predictable failures at once:

- **reinvention drift** — departments keep rediscovering the same language-learning, writing, coding, or live-performance rule without shared identifiers or proof surfaces;
- **overcentralized panic** — central policy answers construct sensitivity with broad bans because it lacks narrow inherited defaults;
- **hidden local inequity** — similarly situated learners meet materially different support rules depending on which teacher or site they happen to get;
- **premature hardening** — one plausible row becomes immortal even though age band, stakes, or assessment design later show that it should be split, softened, or retired.

Current public examples point in a convergent direction. College Board's current AP guidance already differentiates among domains rather than treating all AI use alike: AP Capstone permits limited support for exploration and checking while requiring students' own analysis plus checkpoints; AP Computer Science Principles allows AI-assisted coding and debugging but still requires learners to understand and explain the code; AP world-language projects allow AI to help locate target-language sources while requiring the learner's own target-language performance; and AP Art and Design prohibits AI across the creative process. Contemporary assessment-accessibility guidance from CAST, ETS, Smarter Balanced, and WIDA still presses the same deeper rule: widen access where the support removes barriers, but narrow supports when they would otherwise replace the construct being measured. Medical-education guidance from the AAMC adds a further constraint for professional settings: maintain human-centered judgment, equal access, and local evaluation where patient-facing performance is at stake. See `B88`, `B89`, `B90`, `B91`, `B92`, `B93`, `B94`.

## Relationship to the base grammar

This document does not replace the base legend in [`presumptive-access-support-categories-and-override-triggers.md`](presumptive-access-support-categories-and-override-triggers.md) or the row profile in [`subject-and-age-override-table-profile.md`](subject-and-age-override-table-profile.md).

It adds one thing only:

- a **starter row set** for repeated cases that are portable enough to inherit provisionally.

Each row below still uses the existing row fields, support classes (`A1-A5`), trigger vocabulary (`T1-T4`), and public outcomes (`protected_default`, `first_unaided_then_supported`, `ordinary_course_rule`, `live_or_supervised_surface_required`, `manual_review`).

## Inheritance rule

The archive's default inheritance posture is deliberately light.

- publish the starter rows centrally with stable IDs;
- mark them `provisional` unless a sector has stronger evidence for `active`;
- let schools, programmes, or departments inherit them unchanged;
- require a short public reason note only when a local owner **declines**, **splits**, **tightens**, or **broadens** a starter row;
- and prefer local add-on rows only for truly programme-specific constructs rather than for the recurring cases below.

Omission from a local table should mean one of two things only:

- the institution inherited the starter row unchanged and is relying on the central publication; or
- the domain remains local-only and the institution says so explicitly.

## The starter set

The archive's current starter set is intentionally tiny. These are **starter defaults**, not universal mandates.

| Row ID | Age / family | Narrow construct | Support / trigger basis | Default outcome | Default alternative proof surface | Portability judgment |
|---|---|---|---|---|---|---|
| `SR-READ-FOUND-01` | early primary / foundational literacy | first-pass decoding of unseen alphabetic text | `A1` read-aloud, text-to-speech, or translation when `T1` + `T2` apply | `first_unaided_then_supported` | short first-pass decoding check, then supported comprehension or discussion work | strong starter |
| `SR-LANG-ORAL-01` | lower secondary through postsecondary / world languages | spontaneous target-language interpersonal speaking and listening | `A2-A4` when `T1` + `T4` apply | `live_or_supervised_surface_required` | short live conversation, interview, or oral exchange | strong starter |
| `SR-LANG-PROJ-01` | upper secondary through postsecondary / world-language projects | target-language source use and learner-owned presentation | `A1-A3` search/translation support with `T1` guard | `ordinary_course_rule` for final presented product, but not for source-finding support alone | target-language presentation plus short defense of source choice and meaning | medium-strong starter |
| `SR-WRITE-RHET-01` | secondary through postsecondary / composition and rhetoric | final wording, syntax, and argument control where those features are graded | `A4` rewriting or surrogate drafting when `T1` applies | `ordinary_course_rule` | timed in-class rewrite, oral defense, annotated revision memo, or draft-history checkpoint | strong starter |
| `SR-MATH-PROC-01` | upper primary through first-year college / symbolic mathematics | first-pass symbolic procedure or stepwise manipulation | `A4` solver/executor support when `T1` + `T2` apply | `first_unaided_then_supported` | short unaided procedure check followed by supported application/problem-solving task | medium-strong starter |
| `SR-CODE-EXPL-01` | secondary through postsecondary / introductory coding | code production plus learner explanation, tracing, and debugging ownership | `A4` code generation or heavy completion when `T1` applies | `ordinary_course_rule` with required explanation surface | live trace, oral walkthrough, modification task, or supervised debug step | strong starter |
| `SR-LIVE-PRO-01` | upper secondary through professional education / clinical, counseling, advising, trade, or safeguarding performance | live accountable performance where safety, interpersonal judgment, or spontaneous response matter | `A4-A5` when `T3` + `T4` apply | `live_or_supervised_surface_required` | observed simulation, supervised encounter, or oral walk-through under relevant conditions | strong starter |

## Row notes

### `SR-READ-FOUND-01` — foundational decoding needs one direct surface

The archive continues to treat ordinary presentation supports as presumptively protected. But early decoding is one of the clearest places where oral presentation can replace the exact thing being measured if no direct surface is ever preserved. So the starter rule is not blanket prohibition. It is: preserve one short first-pass decoding surface, then return to supported reading for later comprehension, discussion, and participation. That stance fits the archive's barrier-removal bias while respecting the construct logic that underlies accessibility guidance in current assessment practice. See `B88`, `B89`, `B90`, `B91`.

### `SR-LANG-ORAL-01` — spontaneous oral exchange is usually not a translation problem

World-language oral performance is a recurrent case where translation, scripting, or mediated response can collapse the evidence needed about real-time language use. The current AP world-language project policy is consistent with that intuition: AI may help with inquiry and source-finding, but the learner must still produce the presentation in a way that demonstrates their own language abilities and cultural understanding. For ordinary institutions, the reusable starter move is to require at least one live or supervised interpersonal surface rather than trying to ban support everywhere. See `B86`, `B91`, `B92`.

### `SR-LANG-PROJ-01` — keep source-finding support lighter than final language performance

This starter row exists because institutions often overreact in language learning by treating source-finding help, glossary support, and exploratory translation exactly the same as final presented performance. The archive's starter default is narrower: protected access and bounded support can remain available during inquiry, but once the final construct becomes learner-owned target-language communication, the output belongs on the ordinary course rail with a proof surface that shows the learner can explain what they are presenting. Current AP guidance again points in this direction. See `B86`, `B91`, `B92`.

### `SR-WRITE-RHET-01` — final rhetorical control is a classic construct-sensitive case

This is one of the most portable starter rows in the archive. AI can help with exploration, grammar checking, and feedback, but once wording, syntax, rhetorical control, and evidence use are part of the graded claim, surrogate drafting and rewriting are no longer mere access. AP Capstone's current policy takes a comparable line by permitting limited support while still requiring students' own analysis, synthesis, and checkpoints with teachers. The starter row therefore moves final production into ordinary course policy while insisting on a proof surface stronger than disclosure alone. See `B25`, `B26`, `B92`.

### `SR-MATH-PROC-01` — baseline procedure first, supported application after

The archive still rejects nostalgic blanket no-tool mathematics. But where the institution truly needs direct evidence of symbolic procedure or first-pass manipulation, a starter row should preserve one unaided surface before returning to realistic supported work. Contemporary exam policy already uses part-sensitive tool segmentation rather than all-or-nothing permission structures; College Board's current AP calculator policy is a clean public example. The archive's default AI analogue is therefore not a course-wide ban, but `first_unaided_then_supported`. See `B90`, `B93`.

### `SR-CODE-EXPL-01` — code help is increasingly normal, code ownership still needs proof

Coding is now one of the clearest domains where ordinary AI use belongs in the learning environment, but the construct often includes understanding, tracing, debugging, and explaining what the code does. Current AP Computer Science Principles guidance makes exactly that move: students may use generative AI as a supplementary resource for coding and debugging, but they remain responsible for understanding, acknowledging, and explaining any code co-written with AI. That makes coding a strong starter-row family for `ordinary_course_rule` plus a required explanation surface, not a domain for pretending AI assistance can be kept absent. See `B92`, `B94`.

### `SR-LIVE-PRO-01` — patient-facing or safety-relevant performance still needs a human surface

The archive treats live professional performance as a distinct starter family because some constructs cannot be reduced to polished artifacts or after-the-fact narration. Clinical, counseling, advising, trade, and safeguarding tasks often require real-time judgment, communication, and accountability. The AAMC's current principles reinforce the same operating intuition: maintain human-centered focus, provide equal access, protect privacy, and monitor AI in actual place of use. The reusable starter rule is therefore to preserve at least one observed or directly supervised surface when live accountable performance is part of the claim. See `B89`, `B94`.

## Domains that should usually remain local for now

The archive is **not** ready to publish starter defaults for every construct-sensitive domain. At present, the following families should usually remain local unless a sector develops stronger shared evidence:

- studio- and portfolio-based arts outside clearly bounded exam programmes;
- advanced graduate writing where genre, co-authorship norms, and professional tooling differ sharply by field;
- upper-division statistics, modeling, or engineering work where tool use is inseparable from ordinary practice but the needed proof surface varies widely;
- programme-specific regulatory tasks where external licensure or employer rules already control the evidence surface.

The rule here is disciplined restraint. A starter row should exist only when reuse is more helpful than misleading.

## What counted as a real archive gain

The archive now does more than say “publish override tables.” It now names a compact starter set that institutions can inherit provisionally for repeated construct-sensitive cases in literacy, languages, writing, mathematics, coding, and live professional performance. That is a meaningful operating step because it turns a governance profile into deployable defaults without collapsing back into blanket bans or giant rulebooks.

## Current archive bet

The archive's current best guess is that a tiny starter row set for repeated construct-sensitive cases will produce more fairness, portability, and implementation coherence than either fully local improvisation or overbroad central bans.

That claim is now canon, but still live. The next problem is narrower: which starter rows are stable enough to promote from provisional defaults to stronger sector-level inheritances, and what evidence should force a row to split, soften, or retire instead. See `OQ-0005`.
