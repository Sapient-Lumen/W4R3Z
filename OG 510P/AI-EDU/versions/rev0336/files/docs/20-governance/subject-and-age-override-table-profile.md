# Subject- and age-sensitive override-table profile

This document closes the archive's earlier ambiguity about **how institutions should publish and
maintain local override tables for construct-sensitive AI-enabled supports** without sliding back
into teacher-by-teacher rule drift.

The archive's current bet is simple:

> keep access defaults broad, but make construct-sensitive exceptions public, inherited, reviewable,
and small.

The point is to avoid five familiar failures at once:

- **hidden local drift** — every teacher improvises different restrictions for the same support;
- **single-regime overreach** — accessibility questions are forced back into artifact-level
  disclosure or blanket prohibition;
- **construct panic** — institutions know some domains need narrower rules, but answer by banning
  broadly rather than naming the exact conditions;
- **stale exception tables** — old restrictions survive after curricula, tools, or legal guidance
  change;
- **support-status exposure** — course policy ends up revealing disability, language-support, or
  accommodation status when the real question is construct fit.

UNESCO's rights framing, CAST's UDL work, and assessment-accessibility practice all point in the
same direction: design for access first, publish exceptions when the construct really requires them,
and keep those exceptions tied to what is being measured rather than to who the learner is. See
`B20`, `B27`, `B28`, `B84`, `B87`, `B88`, `B89`, `B90`, `B91`.

## What an override table is

An override table is a **small published rule set** that sits on top of the archive's base support
map:

- `A1-A3` remain presumptively protected supports;
- `A4-A5` remain construct-sensitive by default;
- `T1-T4` still identify when even `A1-A3` supports may need a narrower rule.

The table is for **repeated construct-sensitive cases** that recur across a subject, programme, age
band, or assessment family.

It is **not** a learner dossier, an accommodation register, or a permission slip for individual
students.

## Authority and scope

The archive's preferred authority stack is:

1. **institution-wide base legend** — the public meaning of `A1-A5`, `T1-T4`, and the
   protected-access rail;
2. **subject- or programme-level override table** — public rows for repeated construct-sensitive
   cases;
3. **course/task-level application** — instructors inherit the published rule and name the relevant
   row when it actually applies.

The important discipline is this:

> instructors may apply a published row, but they should not invent hidden construct-sensitive
restrictions from scratch for ordinary repeated cases.

If a course encounters a genuinely unusual case not covered by the published table, it should route
to local review rather than silently becoming a new private rule.

## Where tables should exist

Institutions should publish override tables only where the archive already expects repeated
construct-sensitive variation, especially:

- target-language reading, listening, speaking, and writing;
- foundational decoding and early literacy;
- writing-intensive courses where wording, syntax, fluency, or rhetorical control are part of the
  construct;
- mathematics and technical courses where symbolic procedure or stepwise manipulation is itself
  being measured;
- coding courses where syntax production, tracing, debugging, or architecture explanation is part of
  the claim;
- clinical, trade, advising, counseling, or safeguarding performance where live accountability
  matters.

Everywhere else, the institution should prefer the presumptive defaults rather than manufacturing a
table just because AI exists.

## Minimal row profile

The archive's profile is intentionally small. Every published row should include:

- `row_id` — stable identifier;
- `status` — `active`, `provisional`, `expiring`, `retired`;
- `age_band` — the developmental band or stage the row applies to;
- `subject_or_program_family` — e.g. world languages, first-year composition, algebra, nursing
  simulation;
- `task_or_construct` — the narrow thing being measured;
- `support_classes` — relevant `A1-A5` class or classes;
- `trigger_basis` — which `T1-T4` trigger justifies the override;
- `outcome` — the named rule outcome from the small outcome set below;
- `alternative_proof_surface` — the substitute evidence route, if any;
- `reason_note` — one short construct-fit explanation;
- `authority_owner` — the department, programme, or central office responsible;
- `effective_from` and `review_by` — dates that keep the row from becoming immortal;
- `supersedes` — optional prior row ID if this entry replaces an older one.

Rows may optionally include a short `implementation_note`, but the archive strongly prefers notes
that stay short enough to fit inside ordinary course documents without dragging in whole policy
manuals.

## The five rule outcomes

The archive now names five public outcomes for override rows.

### `protected_default`

The support stays on the protected rail even in this subject or age band.

Use this when a local table mainly exists to reassure staff that the base presumption still holds.

### `first_unaided_then_supported`

The institution requires one named first-pass or baseline evidence surface before the support
returns for later practice or later performance.

Use this when `T2` applies but a total ban would overreach.

### `ordinary_course_rule`

The support is no longer handled on the protected rail for this construct. It follows the ordinary
course AI grammar (`NO-AI`, `GUIDED-AI`, `OPEN-AI`) and the local proof surface.

Use this when `T1` applies because the support would otherwise perform the thing being measured.

### `live_or_supervised_surface_required`

The learner may still use supports elsewhere, but at least one named live, supervised, or directly
observed performance surface is required.

Use this when `T3` or `T4` applies because accountability, safety, or spontaneous interaction is
part of the construct.

### `manual_review`

The base map is not enough and the case is too rare or mixed to encode as a standing row.

Use this sparingly. Overuse means the table is failing to do its job.

## Starter rows live elsewhere

The archive now treats starter rows as their own surface rather than embedding them here as
examples. See [`reusable-starter-override-rows.md`](reusable-starter-override-rows.md) for the
current small inherited starter set covering foundational literacy, world languages, writing,
mathematics, coding, and live professional performance.

## Publication posture

Every override-table publisher should expose two synchronized surfaces:

1. a short human-readable table that faculty, students, families, and support staff can actually
   read;
2. a machine-readable file (`CSV`, `JSON`, or equivalent) using the same row IDs and dates.

The archive's preference is again **boring legibility over bespoke platform dependence**.

Every public table should also state four base rules:

- omission from the table means the presumptive institutional default still governs;
- rows are keyed to constructs and task families, not to disability categories or learner
  identities;
- every restrictive row should name an alternative proof surface where feasible;
- teachers may inherit and apply rows, but may not create hidden recurring restrictions that bypass
  publication and review.

## Review cadence and early-review triggers

The archive's default review rule is:

- review every active row at least every 12 months;
- review every row tied to a named vendor, model family, or product surface every 6 months;
- trigger early review whenever the curriculum, assessment design, legal accessibility floor, or
  repeated appeal pattern changes enough to threaten construct fit or fair access.

Useful early-review triggers include:

- a repeated pattern of appeals, reversals, or confusion around the same row;
- a substantive shift in the task or rubric being assessed;
- a tool change that materially alters what a support can now do;
- updated accessibility or civil-rights guidance;
- or evidence that a row is broad enough to chill legitimate support use.

## What should never be in the table

An override table must not publish:

- learner names or identifiers;
- accommodation records or support-status labels;
- raw submissions, chat logs, or support traces;
- disability diagnoses;
- or free-form narratives that effectively smuggle in a local case file.

The table is a public construct-governance artifact, not a support dossier.

## Failure modes this document is trying to prevent

- **teacher-by-teacher rule sprawl** — the same support is treated differently in adjacent sections
  of the same course;
- **blanket anti-AI fallback** — institutions ban broadly because they lack a small way to publish
  exceptions;
- **private support disclosure** — learners are pushed to confess protected support use when the
  real issue is construct fit;
- **stale construct rules** — restrictions persist after tasks or tool capabilities change;
- **manual-review inflation** — ordinary repeated cases never become legible standing rules.

## Current archive bet

The archive's current best guess is that a **tiny published override-table profile** will outperform
both extremes:

- one universal rule for every support in every subject,
- and fully local hidden discretion at the level of individual teachers or sections.

The right shape is narrower: base access defaults, a short inherited exception table for repeated
construct-sensitive cases, annual review, faster review for tool-specific rows, and alternative
proof surfaces instead of naked prohibition.

That claim is now canon. The archive now also has a separate starter-row surface for repeated
construct-sensitive domains. The next live problem is narrower still: which starter rows are stable
enough to promote beyond provisional defaults, and what evidence should force a row to split,
soften, or retire. See [`reusable-starter-override-rows.md`](reusable-starter-override-rows.md) and
`OQ-0005`.
