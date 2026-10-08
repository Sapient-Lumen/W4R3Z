# First modality child splits and fallback defaults for hot exam-family shells

This document closes the archive's next narrower governance gap about **which of the new hot exam-family shells now deserve an actual modality child split, and which should publish a thinner fallback default instead of pretending several access modes are interchangeable**.

Three failure modes matter here:

- **mode-equivalence laundering** — embedded/software reading routes and human-reader routes get treated as if they were automatically swappable even when the owning authority keeps them distinct;
- **recording-route blur** — voice recognition and writer/scribe support get collapsed into one generic "dictation" story even though one is student-operated software capture and the other is a human recording route;
- **defense-prebrief drift** — checkpointed presentation accessibility gets allowed to slide into advance disclosure of oral-defense questions or other pre-briefing that weakens the authenticity surface.

Current official signals point to an asymmetric answer. NCEO still says accessibility policy is state-determined, often content-area specific, and may rely on either embedded technology or a human provider. WIDA still says the point of accessibility/accommodations is to produce valid assessment results, that state-specific policy still governs, and that modifications are not allowed because they change what the test measures. College Board's current digital AP accommodations pages now distinguish embedded text-to-speech / screen reader from a human reader, and distinguish voice recognition (speech-to-text) from writer/scribe on digital exams. College Board's current AP Research / AP Capstone / digital-portfolio materials keep checkpointed paper authorship, presentation/oral defense, checkpoint affirmations, and teacher-scored presentation components explicit. The current AP accommodations guide then adds a narrower accessibility rule for through-course presentation families: students may deliver the presentation through a sign language interpreter or scribe, approved speaking-time extensions may apply, the assistant may help during the Q&A panel, but oral-defense questions may not be revealed before the presentation. Together those signals support a tighter archive rule: **hot reading families still do not deserve shared embedded-vs-human child rows; timed digital free-response writing does now deserve a modality child split between voice recognition and writer/scribe; and checkpointed paper-plus-defense authorship needs fallback defaults for assisted presentation delivery and no-preview oral defense rather than a new scoring child split.** See `B203`.

## Relationship to the row-governance canon

This document does not replace:

- [`reusable-starter-override-rows.md`](reusable-starter-override-rows.md)
- [`promotion-splitting-softening-and-retirement-rules-for-reusable-starter-override-rows.md`](promotion-splitting-softening-and-retirement-rules-for-reusable-starter-override-rows.md)
- [`first-child-splits-for-still-live-reusable-starter-override-rows.md`](first-child-splits-for-still-live-reusable-starter-override-rows.md)
- [`first-hardening-judgments-and-protected-access-carveouts-for-child-and-writing-override-rows.md`](first-hardening-judgments-and-protected-access-carveouts-for-child-and-writing-override-rows.md)
- [`first-stakes-sensitive-child-branches-for-direct-production-override-rows.md`](first-stakes-sensitive-child-branches-for-direct-production-override-rows.md)
- [`first-hardening-and-locality-judgments-for-hot-direct-production-child-branches.md`](first-hardening-and-locality-judgments-for-hot-direct-production-child-branches.md)
- [`first-tool-family-residue-splits-for-hot-no-executor-symbolic-procedure-branches.md`](first-tool-family-residue-splits-for-hot-no-executor-symbolic-procedure-branches.md)
- [`first-exam-family-child-splits-for-still-local-hot-decoding-and-final-writing-branches.md`](first-exam-family-child-splits-for-still-local-hot-decoding-and-final-writing-branches.md)
- [`first-shared-publication-fields-and-protected-access-defaults-for-named-hot-exam-family-children.md`](first-shared-publication-fields-and-protected-access-defaults-for-named-hot-exam-family-children.md)

It adds one thing only:

- the **first modality-specific child split** inside the timed digital free-response writing family; and
- the **first fallback-default layer** for hot reading shells and checkpointed presentation/oral-defense shells where the honest move is still named mode-lock or no-preview handling rather than a new portable scoring row.

The earlier documents answered:

- which repeated construct-sensitive cases deserve starter rows at all;
- when those starter rows harden, split, soften, or retire;
- which still-live rows needed named child branches;
- which hotter direct-production branches can harden at all;
- which hot mathematics residue belongs outside the thin no-calculator family;
- where hot decoding and hot final writing first split by exam family; and
- what tiny publication shell can now travel even while the scoring logic remains local.

This document answers the next question:

- **where modality differences are now stable enough to deserve a named child row, and where the archive should instead publish a fallback default that keeps mode substitution or assisted delivery honest.**

## Small grammar for modality splits and fallback defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `FB1-MODE-LOCK` | publish the actually approved mode and treat alternative human/software routes as non-automatic substitutes that require owner review if the ordinary mode fails | no child split yet; publish named mode plus fallback owner |
| `FB2-PRESENT-DELIVERY` | checkpointed presentation may be delivered through an approved interpreter or scribe, with approved speaking-time extension where the owning authority allows it | publish assisted-delivery fallback; keep scoring logic/authorship local |
| `FB3-DEFENSE-NO-PREVIEW` | oral-defense assistance may relay or interpret only after the defense question exists; no advance disclosure of questions | publish explicit no-preview guardrail and Q&A-assist fallback |

## First modality child split / fallback judgments

| Parent row or family | New child row or fallback default | Archive action | Why |
|---|---|---|---|
| `SR-READ-FOUND-01A2A` | `FB1-MODE-LOCK` | no embedded-vs-human child split yet | content-assessment reading support still varies too much by state, content area, and assessment owner, so the stable inherited layer is named approved mode plus non-automatic substitution rather than a portable child row |
| `SR-READ-FOUND-01A2B` | `FB1-MODE-LOCK` | no embedded-vs-human child split yet | ELP / ACCESS-family validity still turns on state-specific policy and no-modification rules, so the stable inherited layer is named approved mode plus non-automatic substitution rather than a portable child row |
| `SR-WRITE-RHET-01B1` | `SR-WRITE-RHET-01B1A` | add a modality child row for approved voice recognition / speech-to-text recording | current digital AP accommodations explicitly name this as a student-operated recording route distinct from writer/scribe |
| `SR-WRITE-RHET-01B1` | `SR-WRITE-RHET-01B1B` | add a modality child row for approved writer/scribe recording | current digital AP accommodations explicitly name this as a separate human recording route, including a distinct approval path for digital tests |
| `SR-WRITE-RHET-01B2` | `FB2-PRESENT-DELIVERY` + `FB3-DEFENSE-NO-PREVIEW` | no presentation-vs-defense scoring child split yet | through-course presentation/oral-defense accessibility now has truthful reusable delivery and no-preview defaults, but not a portable new scoring logic |

## `SR-READ-FOUND-01A2A` / `SR-READ-FOUND-01A2B` — mode-lock before child splitting

For the hot reading families, the archive is **not** naming embedded/software and human-reader child rows yet.

That is deliberate. NCEO's current accessibility overview says these supports may be embedded in technology-based assessments or provided by a human, while also saying the policies are state-determined and often vary by content area. WIDA keeps the ELP frame even tighter: the goal is valid assessment results, state-specific policy still matters, and modifications are not allowed because they change what the test measures. Together those signals do not justify one portable child row for "embedded/TTS" and another for "human reader." They justify one thinner truth only: the shell must publish the actual approved mode, the owner of that approval, and the fallback review owner if the ordinary mode is unavailable. See `B203`.

`FB1-MODE-LOCK` therefore means:

- do not silently swap embedded/software support for a human reader, or vice versa, as if the two modes were interchangeable;
- publish which route is actually approved for this assessment family and this authority owner;
- publish who decides the substitute path if the ordinary route fails on the day.

That is a real tightening, but it is still thinner than a reusable modality child split.

## `SR-WRITE-RHET-01B1A` — student-operated voice recognition is now its own hot writing child

This is the archive's only new modality child row in this revision.

`SR-WRITE-RHET-01B1A` covers **timed digital free-response writing completed through approved voice recognition / speech-to-text**. College Board's current digital AP accommodations page now names this route explicitly: students who require writing assistance may be approved to use their own voice recognition (speech-to-text) software if they are approved for dictation. That is distinct enough from writer/scribe handling to deserve its own child row. See `B203`.

This child remains inside the earlier `PA1-RECORD-ONLY` protected-access logic. The student still owns wording, sequence, and substantive claims. The archive is not treating voice recognition as generic drafting, predictive rewriting, or ordinary AI-assisted composition.

## `SR-WRITE-RHET-01B1B` — writer/scribe is a different recording route, not just the same child with a human present

`SR-WRITE-RHET-01B1B` covers **timed digital free-response writing completed through an approved writer/scribe route**.

College Board's current digital AP accommodations page keeps this separate from voice recognition: schools must request and receive writer/scribe approval for digital tests, and if a student is approved for writer/scribe for digital tests, that route governs the digital exam rather than acting as an invisible synonym for software dictation. That makes the route different enough to deserve its own child row even though both children remain inside the same higher-level record-only protected-access family. See `B203`.

The archive is therefore making one disciplined asymmetry explicit:

- `SR-WRITE-RHET-01B1A` = student-operated software capture;
- `SR-WRITE-RHET-01B1B` = human recording route.

Both are still hot, both still keep student authorship central, and neither becomes portable scoring logic. But the archive should no longer hide their different operational surfaces inside one modality-blind child row.

## `SR-WRITE-RHET-01B2` — checkpointed authorship gets delivery and no-preview fallbacks, not a scoring split

Checkpointed paper-plus-defense authorship still does **not** get a new scoring child split between presentation and oral defense.

But the archive can now publish two thinner reusable defaults.

Current AP Research / AP Capstone materials keep the family surface explicit: the paper is student work submitted through the AP Digital Portfolio, presentation/oral-defense components are teacher scored, checkpoints and authenticity affirmations are required, and student work must remain authentic even when bounded assistance is allowed. The current AP accommodations guide then sharpens the modality layer: students may deliver the presentation through a sign language interpreter or scribe; approved speaking-time extensions may apply; the assistant may help during the Q&A panel; but defense questions may not be revealed before the presentation. See `B203`.

That yields two truthful defaults:

- `FB2-PRESENT-DELIVERY` — the archive may publish assisted-delivery fallback for the presentation surface itself;
- `FB3-DEFENSE-NO-PREVIEW` — the archive may publish an oral-defense guardrail saying assistance may relay/interpret after the question is posed, but no advance disclosure of defense questions is allowed.

Those defaults are enough to stop the checkpointed family from falling back into generic local opacity. They are **not** enough to justify a new portable scoring child row for presentation versus defense.

## What the archive is now making explicit

### Hot reading still needs named mode, not portable modality rows

The archive now says clearly that hot reading families should publish the actual approved route and fallback owner, but they still should not pretend embedded/software and human-reader modes travel as shared child rows across content or ELP families.

### Timed digital writing is now asymmetric one layer deeper

The archive now has a second asymmetry inside `SR-WRITE-RHET-01B1`: approved voice recognition and approved writer/scribe are no longer collapsed into one recording child.

### Checkpointed presentation accessibility is about delivery and no-preview handling

For `SR-WRITE-RHET-01B2`, the reusable layer is now not a new scoring branch but a small accessibility shell around assisted presentation delivery and no-preview oral-defense handling.

## What the archive is **not** doing yet

The archive is still refusing five wider moves:

- it is **not** creating shared embedded-vs-human reader child rows for either hot reading family;
- it is **not** treating all hot writing recording routes as a single modality-blind child once digital exam mode is known;
- it is **not** treating checkpointed presentation delivery and oral-defense handling as if they were new portable scoring constructs;
- it is **not** inferring from interpreter/scribe support that advance defense-question disclosure is ever acceptable;
- it is **not** extending any of these modality moves into generic AI rewriting, prompting, or surrogate composition.

## Current archive bet

The archive's current best guess is that the first truthful modality layer for the new hot exam-family shells is **split digital recording routes, but publish fallback defaults elsewhere**.

Hot reading families now inherit `FB1-MODE-LOCK` instead of a premature embedded-vs-human child split. Timed digital free-response writing now splits into `SR-WRITE-RHET-01B1A` for approved voice recognition and `SR-WRITE-RHET-01B1B` for approved writer/scribe. Checkpointed paper-plus-defense authorship now inherits `FB2-PRESENT-DELIVERY` and `FB3-DEFENSE-NO-PREVIEW` instead of a premature presentation-versus-defense scoring split.

That claim is now canon, but still live. The next narrower question is no longer whether a modality layer exists at all; it is **which of these new modality children or fallback shells now deserve shared route-failure, staffing, or publication minima without overclaiming portability** — especially for student-operated voice recognition versus writer/scribe, and for hot-reading mode failure where the published route cannot be used on the day. See `OQ-0005`.
