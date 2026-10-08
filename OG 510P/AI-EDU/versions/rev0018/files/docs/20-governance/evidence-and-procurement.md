# Evidence and procurement

This document states the archive's current bar for adopting AI in educational settings.

## Rule 1. Separate workflow value from learning value

A tool can save teacher time without improving student learning. That may still matter, but institutions should say which claim is being made.

- **Workflow claim:** saves time, reduces friction, improves access to materials.
- **Learning claim:** improves understanding, transfer, persistence, or outcomes.

Do not let workflow value smuggle in stronger learning claims.

## Rule 2. Scale according to stakes

### Low-stakes uses

Examples: first-draft feedback, lesson adaptation, translation, brainstorming, retrieval-practice generation.

Allowed more easily, but still require privacy review and human oversight.

### Medium-stakes uses

Examples: tutoring, formative assessment support, personalized practice, advising support.

Require bounded pilots, teacher visibility, clear escalation paths, and monitoring for bias or developmental harms.

### High-stakes uses

Examples: grading, placement, admissions, discipline, disability accommodation design, legal compliance decisions.

Should not be delegated to opaque AI outputs. Human review, appeal paths, and rights protections are mandatory. See `B07`, `B08`, `B09`.

## Rule 3. Prefer pedagogically explicit tools

The archive currently distinguishes three classes:

1. **general-purpose AI** used in class or study;
2. **education-shaped AI** with visible pedagogical scaffolds;
3. **evidence-backed educational AI** that has been trialed in realistic settings.

The further right a tool sits, the more confidence institutions can reasonably place in it. OECD 2026 is especially useful here: it argues that purpose-built tools grounded in learning science show more promise than unguided use of generic systems. See `B11`.

## Rule 4. Procurement should ask nine questions

1. What learning problem is this tool supposed to solve?
2. What is the theory of change?
3. What is the stake level?
4. What evidence supports the claim?
5. What data does it collect, store, or expose?
6. What human review or opt-out path exists?
7. Does it support clear course-level tagging, light disclosure, and privacy-protective support routing rather than forcing one disclosure regime for everything?
8. Does it meet accessibility and non-discrimination requirements in the actual institutional context?
9. What will make us stop using it?

If these questions cannot be answered, the archive's default posture is **do not scale**.

## Rule 5. Minimum evidence package rises with stakes

### Low-stakes package

At minimum require:

- a one-page use-case memo,
- privacy/data review,
- teacher-facing guidance on appropriate delegation,
- a simple explanation of how the tool fits local mode/disclosure rules,
- a quick accessibility check for the intended user group and devices,
- and a short post-adoption check on workload, errors, and obvious misuse.

This is enough for bounded support tools, but not for stronger learning claims.

### Medium-stakes package

At minimum require:

- a bounded pilot with comparison to current practice or a clear baseline,
- teacher training before student launch,
- family and student notice where relevant,
- subgroup review for equity and accessibility,
- an explicit decision on which uses belong in pedagogical disclosure versus protected support routing,
- and explicit stop conditions for dependency, hallucination, bias, inaccessible design, or loss of teacher visibility.

This is the archive's default package for tutoring, advising, and formative-support tools. Tools that cannot support clear course-level expectations without hidden logging or awkward workarounds should be treated with caution. See [`../30-operations/course-level-ai-use-grammar.md`](../30-operations/course-level-ai-use-grammar.md).

### High-stakes package

The archive's default posture is **non-delegation of final judgment**. If AI is used at all, require:

- documented validation in the local context,
- human accountable sign-off,
- appeal and override paths,
- public explanation of the tool's role,
- and rights review for civil rights, disability, and due-process concerns.

In many cases, the right answer remains: do not use AI to make the determination.

## Rule 6. Back teacher augmentation before teacher replacement

Current evidence is strongest for AI that helps educators or tutors do their work better, not for systems that fully replace them. Tutor CoPilot is notable precisely because it augments tutors and improves their pedagogical moves. See `B13`.

## Rule 7. Keep families and learners legible in the loop

U.S. DOE's toolkit emphasizes transparency and opportunities for students, teachers, and parents to opt out of AI-enabled applications. This matters especially when institutions serve minors or vulnerable populations. See `B07`.

## Rule 8. Procurement must include equity and accessibility review

A tool that works only for already-advantaged students or that increases disability barriers is a failed educational intervention even if average performance looks positive. OECD and UNESCO both reinforce this. OECD's 2026 work on neurodivergent learners adds a practical warning about affordability, teacher-capacity gaps, and the risk that cheating concerns will constrain legitimate assistive use. For many public institutions, accessibility is not merely aspirational but increasingly concrete: public web and app surfaces generally need WCAG-aligned accessibility, including vendor-provided content in the institution's service environment. See `B01`, `B09`, `B10`, `B19`, `B20`, `B27`, `B28`.

## Current purchasing heuristic

The archive's current practical heuristic is:

> buy or deploy AI for education only when the tool is teacher-visible, rights-compatible, accessibility-checked, compatible with light course-level legibility plus protected support routing, pedagogically shaped, and tied to a concrete proof plan for educational value.
