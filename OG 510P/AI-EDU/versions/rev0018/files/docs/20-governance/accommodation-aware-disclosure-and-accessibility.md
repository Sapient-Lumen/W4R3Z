# Accommodation-aware disclosure and accessibility defaults

This document resolves the archive's first serious inclusion boundary.

Once institutions publish course-level AI rules, a new problem appears immediately: **the same policy can clarify ordinary use while quietly penalizing learners who rely on access supports, translation, dictation, read-aloud, executive-function scaffolds, or formal accommodations**.

The archive's current rule is:

> use **two channels**, not one.

- Use a **pedagogical disclosure channel** when AI use changes the learning claim, the workflow being assessed, or the amount of substantive content generation.
- Use a **protected support channel** when the main function is access, communication, or accommodation and public artifact-level disclosure would reveal more private information than the course actually needs.

This is a small design move, but it matters. OECD's 2026 neurodivergent-VET work makes clear that AI can improve accessibility, support executive function, and build independence, while also warning that cheating fears can constrain legitimate assistive use and that privacy, bias, and exclusion remain real risks. UNESCO's right-to-education framing sharpens the norm further: education must remain accessible and adapted, not merely formally available. The European Commission's 2026 ethical-use guidance adds the institutional point that AI use is rising fast enough to require context-based ethical decisions, AI Act/GDPR awareness, and stronger AI literacy. See `B19`, `B20`, `B24`.

## The two-channel rule

### Channel A — pedagogical disclosure

Use the ordinary course grammar when AI use is pedagogically relevant to the claim being made.

Examples:

- AI helped draft, paraphrase, or reorganize substantive prose in a writing task.
- AI generated code, debugging moves, or mathematical steps that are part of the assessed performance.
- AI translated or simplified material in a task where language handling itself is part of the construct being assessed.
- AI proposed sources, interpretations, or arguments in a task where source judgment is central.

In these cases, the course should use the archive's normal mode/disclosure/proof syntax. See [`../30-operations/course-level-ai-use-grammar.md`](../30-operations/course-level-ai-use-grammar.md).

### Channel B — protected support routing

Use privacy-protective accommodation, accessibility, or learner-support channels when the main function is access rather than hidden substitution for the assessed cognitive work.

Examples often include:

- text-to-speech and read-aloud;
- speech-to-text or dictation;
- captioning and transcription;
- interface simplification;
- executive-function supports such as planning prompts or task chunking;
- translation or language support when language production is **not** the main thing being assessed;
- and other support tools approved through disability, multilingual, or learner-support processes.

The key point is that the institution may need to authorize, configure, or document these supports **without demanding that learners publicly append private support information to ordinary coursework**.

## Four tests for deciding the route

When institutions are unsure which channel applies, the archive recommends four tests.

### 1. Function test

Is the tool mainly helping the learner **perceive, express, navigate, or organize** the task, or is it generating substantive content or reasoning for them?

### 2. Construct test

Is the supported faculty part of what the task is supposed to measure?

If the task is measuring oral fluency, translation support is not neutral. If the task is measuring historical interpretation, text-to-speech may be.

### 3. Privacy test

Would artifact-level disclosure reveal disability status, support status, or another sensitive condition that the course does not actually need to know?

If yes, the default should be to keep the support detail in a protected channel.

### 4. Equivalence test

Would the institution demand the same disclosure for the non-AI analogue of the support?

If a school would not require a learner to write “I used a human reader” or “I used a conventional dictation tool” on the face of the assignment, it should be cautious about demanding a more revealing disclosure merely because the support now contains AI components.

## Presumptive defaults

The archive's current defaults are intentionally narrow.

### Presumptively allowed without artifact-level disclosure, unless the task says otherwise

- text-to-speech;
- speech-to-text/dictation;
- captioning/transcription;
- visual, auditory, or interface accessibility features;
- and comparable access supports whose main function is perception, expression, or navigation.

These may still require institutional approval or local configuration. The point is that they should not be treated as presumptive misconduct.

### Usually private-route first, then course-rule check if the support changes the construct

- translation;
- simplification or summarization of source material;
- executive-function scaffolds;
- grammar or style assistance;
- and planning/rewrite support.

These can be legitimate access supports in one context and substantive intervention in another. The course should therefore state when the supported faculty is itself being assessed, and institutions should offer alternative proof paths rather than surprise enforcement.

### Always in the pedagogical channel

- substantive drafting or rewriting;
- solving or step generation;
- code generation that replaces key reasoning or implementation work;
- source selection or interpretation that the learner cannot later defend;
- and any use that materially changes the evidentiary claim of the submitted work.

The answer here is not “ban everything.” It is to use the ordinary course grammar and stronger proof surfaces.

## What institutions should publish

A minimal institutional packet should now add four sentences to the course grammar legend.

1. **Access-support principle:** some AI-enabled supports are treated as accessibility or accommodation tools rather than ordinary authorship tools.
2. **Privacy principle:** learners are not required to disclose disability-related or similarly sensitive support details on the face of ordinary coursework unless pedagogically necessary.
3. **Assessment principle:** when a task measures a faculty that a support would directly substitute for, the course must say so in advance and provide an alternative or bounded proof path.
4. **Review principle:** questions about supports route through existing accessibility, disability, multilingual, or learner-support processes rather than improvised accusation.

That is enough to prevent most confusion.

## Procurement and infrastructure floor

Institutions should not solve this only in syllabus language. They should also buy and configure tools accordingly.

The archive's current minimum floor is:

- require accessibility review before procurement, not after complaint;
- require relevant technical accessibility standards for institutional web and app surfaces;
- require compatibility with assistive technologies and ordinary classroom devices;
- require data minimization, role-based access, and human override;
- prohibit hidden risk scoring or integrity flagging tied to disability- or support-related use patterns;
- and require non-discrimination review under the institution's existing civil-rights obligations.

For public U.S. state and local institutions, the current accessibility floor is now more concrete: ADA guidance explains that state and local government web content and mobile apps generally must meet WCAG 2.1 Level AA, including content and apps provided through contractors or vendors, while obligations of effective communication and reasonable modifications still remain. OCR's AI resource adds that schools and postsecondary institutions remain responsible for discrimination that results from AI use under federal civil-rights law. See `B27`, `B28`.

## Failure modes this document is trying to prevent

- **access chilled by integrity policy** — learners stop using legitimate supports for fear of accusation;
- **private status exposed unnecessarily** — coursework becomes an accidental disability or support disclosure surface;
- **translation treated as cheating by default** — even when language performance is not the construct at issue;
- **inaccessible AI procurement** — institutions buy “smart” systems that fail basic accessibility or interoperability;
- **support details substituted for proof** — institutions ask for more confession instead of better task design.

## Current archive bet

The archive's current best guess is that a **two-channel rule** will outperform a single disclosure regime.

A single regime looks tidy on paper, but in practice it confuses access with authorship, creates unnecessary privacy harms, and pushes institutions toward detector theatre. A two-channel regime is not fully frictionless, but it better matches the real structure of the problem: some AI use changes the learning claim and needs pedagogical legibility; some AI use is part of making education accessible and adapted, and needs privacy-protective support routing instead.

This claim is now canon, but not finished. The next live question is narrower: which access-support categories can institutions safely presume allowed across most courses, and which still require local program-level override because the construct being assessed differs too much by discipline or age band. See `OQ-0001` and `OQ-0005`.
