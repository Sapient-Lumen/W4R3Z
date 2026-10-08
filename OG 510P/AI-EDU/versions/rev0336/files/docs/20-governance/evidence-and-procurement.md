# Evidence and procurement

## Current overlay

Use [`evidence-grade-and-claim-strength-ladder.md`](evidence-grade-and-claim-strength-ladder.md)
before procurement language describes a service as effective, safe, scalable, compliant, accessible,
or learning-enhancing. Procurement may collect all those claims in one packet, but the claims do not
share one evidence grade.

This document states the archive's current bar for adopting AI in educational settings. Read it
together with
[`pilot-to-scale-evidence-and-rollout-gates.md`](pilot-to-scale-evidence-and-rollout-gates.md),
which answers the narrower question of what should happen *after* a pilot appears to go well, and
[`sector-and-function-profile-splits-for-rollout-gates.md`](sector-and-function-profile-splits-for-rollout-gates.md),
which says where the generic rollout ladder already needs a hotter burden or lower ceiling.

## Rule 1. Separate workflow value from learning value

A tool can save teacher time without improving student learning. That may still matter, but
institutions should say which claim is being made.

- **Workflow claim:** saves time, reduces friction, improves access to materials.
- **Learning claim:** improves understanding, transfer, persistence, or outcomes.

Do not let workflow value smuggle in stronger learning claims.

## Rule 2. Scale according to stakes

### Low-stakes uses

Examples: first-draft feedback, lesson adaptation, translation, brainstorming, retrieval-practice
generation.

Allowed more easily, but still require privacy review and human oversight.

### Medium-stakes uses

Examples: tutoring, formative assessment support, personalized practice, advising support.

Require bounded pilots, teacher visibility, clear escalation paths, and monitoring for bias or
developmental harms.

### High-stakes uses

Examples: grading, placement, admissions, discipline, disability accommodation design, legal
compliance decisions.

Should not be delegated to opaque AI outputs. Human review, appeal paths, and rights protections are
mandatory. See `B07`, `B08`, `B09`.

## Rule 3. Prefer pedagogically explicit tools

The archive currently distinguishes three classes:

1. **general-purpose AI** used in class or study;
2. **education-shaped AI** with visible pedagogical scaffolds;
3. **evidence-backed educational AI** that has been trialed in realistic settings.

The further right a tool sits, the more confidence institutions can reasonably place in it. OECD
2026 is especially useful here: it argues that purpose-built tools grounded in learning science show
more promise than unguided use of generic systems. The archive now pairs that class distinction with
a separate deployment ladder plus starter default tables for recurring student-facing,
teacher-facing, and institution-facing functions: bounded open use may tolerate general-purpose
tools, repeated institutionally recommended student-facing use should usually move into a governed
wrapper, ordinary study help and bounded feedback may sometimes remain at `D2`, recurring
tutoring/advising roles should prefer pedagogically explicit tools, student-facing defaults should
right-shift earlier in minors, credit-bearing higher-ed, professional-practice, or public
adult-route contexts, low-friction teacher planning may remain closer to `D1`, teacher-facing
defaults should also right-shift earlier in those contexts, institution-side clerical compression
may remain closer to `D1-D2`, queueing or risk flags need named owners plus contestability, and
final determinations, grades, official records, and well-being/safeguarding ownership remain
human-accountable. Recurring services should also publish how they cool, narrow, suspend, or roll
back when live use changes, which memory class (`M0-M4`) they use, whether the system remembers
learner-declared preferences or inferred states, which hotter contexts inherit stricter brakes,
change freezes, or reopen floors by default, and which hotter contexts presume some release events
are already `C3-C4` rather than ordinary maintenance. See `B11`, `B94`, `B99`, `B100`, `B101`,
`B102`, `B103`, `B104`, `B105`, `B106`, `B107`, `B108`, `B123`, `B124`, `B125`, `B126`, `B127` and
[`general-purpose-vs-purpose-built-deployment-ladder.md`](general-purpose-vs-purpose-built-deployment-ladder.md),
[`student-facing-function-deployment-defaults-and-handoff-triggers.md`](student-facing-function-deployment-defaults-and-handoff-triggers.md),
[`sector-and-age-profile-splits-for-student-facing-defaults.md`](sector-and-age-profile-splits-for-student-facing-defaults.md),
[`teacher-facing-function-delegation-defaults-and-sign-off-triggers.md`](teacher-facing-function-delegation-defaults-and-sign-off-triggers.md),
[`sector-and-age-profile-splits-for-teacher-facing-defaults.md`](sector-and-age-profile-splits-for-teacher-facing-defaults.md),
[`institution-facing-decision-support-defaults-and-contestability-triggers.md`](institution-facing-decision-support-defaults-and-contestability-triggers.md),
[`failure-escalation-safe-degradation-and-manual-fallback.md`](failure-escalation-safe-degradation-and-manual-fallback.md),
[`sector-and-function-profile-splits-for-failure-defaults.md`](sector-and-function-profile-splits-for-failure-defaults.md),
[`model-and-workflow-change-classification-and-fresh-review-triggers.md`](model-and-workflow-change-classification-and-fresh-review-triggers.md),
and
[`sector-and-function-profile-splits-for-change-defaults.md`](sector-and-function-profile-splits-for-change-defaults.md).

## Rule 4. Procurement should ask nine questions

1. What learning problem is this tool supposed to solve?
2. What is the theory of change?
3. What is the stake level?
4. What evidence supports the claim?
5. What data does it collect, store, remember, infer, or expose, at which memory / observability
   level, and for how long?
6. What human review, challenge, reset, or opt-out path exists?
7. Does it support clear course-level tagging, light disclosure, and privacy-protective support
   routing rather than forcing one disclosure regime for everything?
8. Does it meet accessibility and non-discrimination requirements in the actual institutional
   context?
9. What will make us cool it, stop using it, or roll it back — and how will teaching, support, or
   progression continue in the meantime?

If these questions cannot be answered, the archive's default posture is **do not scale**. Even when
they can be answered, the archive now expects institutions to name the service's current rollout
gate (`RG0-RG4`) rather than jumping directly from a successful pilot to ordinary default use. See
[`pilot-to-scale-evidence-and-rollout-gates.md`](pilot-to-scale-evidence-and-rollout-gates.md) and
[`sector-and-function-profile-splits-for-rollout-gates.md`](sector-and-function-profile-splits-for-rollout-gates.md).
Where a team wants to reuse a rollout profile from another context, it should also ask whether the
same educational claim, ordinary operating model, human alternative, and infrastructure ceiling
still fit; and in the archive's hotter parent profiles it should now also ask whether the service
still belongs in the lower-consequence support branch or has crossed into a consequence-bearing
child branch with a hotter burden and lower default ceiling. A parallel memory question applies too:
whether the service still belongs in a support-continuity branch or has crossed into a
consequence-bearing child branch that should move earlier onto named `M3` rails or remain capped
below `M4`. The archive now also asks whether the claimed reuse is even portable: some branches may
harden only while memory remains function-bounded, while support-routing, candidate-control,
readiness-signalling, and queue-shaping branches should usually harden only as named `M3` rails or
human-only handling. If a branch does move to `M3`, institutions should publish whether it uses the
archive's shared support/access/route rail schema or a function-locked local-only map. For the
function-locked rails, procurement should now separate three things instead of treating the whole
map as one local blob: the portable rights floor, any rail-family presumptions, and the permanently
local residue. The archive now asks one narrower question too: does the service rely on a
presumption that has actually hardened across the family, one of the archive's named readiness /
queue child branches, a presumption that still needs a further office- or stakes-level branch, or a
local rebuttal packet with named reason, scope, substitute protection, and expiry? If it relies on
one of the named readiness / queue child branches, procurement should also ask which inherited
review-window band, substitute-path default, and publication trigger apply, rather than letting the
vendor gesture at a branch name while keeping the actual timing or anti-penalty posture hidden in
local implementation notes. And if the service now sits inside one of the new authority-sensitive
branches — `RS-EPA-LS-EXTERNAL-BAR`, `QS-SS-RS-CROSS-OWNER`, or `QS-UD-CHILD-SAFETY` — procurement
should now also require the archive's tiny shared packet: the branch and authority shape, the
present constraint family, the non-override statement, the earliest meaningful review point, the
strongest guaranteed interim path, and the challenge / explanation route. Procurement should now ask
one narrower question too: whether the service is using one of the archive's authority-family
variants — regulator-bar versus host-bar, public-dispatch versus partner-inventory, or provider-led
safeguarding review versus formal multi-agency child-protection stage — because authority shape,
non-override, review point, and challenge route may now travel that one step further even though
full reason taxonomies and concrete interim protections still mostly remain local residue.
Procurement should now also require any matching mini-codes to be named when the archive has them —
for example `EA-REG-RECONSIDER` versus `EA-PARTNER-RELEASE`, or `IP-PACKET-PRESERVATION` versus
`IP-SAFETY-COMPATIBLE-CONTINUITY` — while refusing fake universal deadlines, queue rank promises, or
protective-plan details. Vendors should not market local merits rules or queue formulas as portable
best practice, and institutions should not accept a generic complaints process where the archive
expects named pause posture, review-before-irreversible-step, interim protections, and visible
departures from family defaults. If one of the archive's hardened authority-family pairings or
limited anti-penalty floors is omitted, weakened, or replaced, procurement should now require the
seven-field departure packet rather than treating the gap as harmless local phrasing. Procurement
should also ask one narrower monitoring question: is the same packet now repeating across sites,
partners, or cycles strongly enough to trigger the archive's repeat-cluster rule, in which case the
supplier or institution should not keep selling the gap as a mere local exception but should instead
branch, cool, or reclassify the inherited default. And if a supplier later claims that a previously
cooled, branched, or office-bound default has recovered, procurement should now require a causal-fix
note, a clean run through the same event family, independent confirmation at the level of travel
being claimed, and active monitoring evidence that the quieter picture is not just suppressed use,
rerouting, or a closed pathway. Procurement should now ask one narrower post-recovery question too:
if a later packet appears, is it only `LOCAL-LOGISTICS` while the same anchor, truthful interim
shape, limited floor, and challenge route all still hold, or has the same structural reason
returned, the rights-compatible shell been lost, monitoring evidence gone dark, a serious incident
attached to the path, or a material path change made the recovery evidence stale? In the latter
cases the recovered default should reopen immediately instead of continuing to enjoy recovered
status. If none of those reopen signals appear, procurement should still ask one narrower watch
question: has the recovered path now survived enough comparable monitored reuse for the special
relapse sensitivity to expire, or has a later substantial modification, intended-purpose shift,
authority-owner change, governance-regime change, rights-shell redesign, or monitoring-basis change
reset the watch even before a new packet appears? The archive now treats staff turnover, copy edits,
bug fixes, and other path-preserving maintenance as non-resetting by default, but it does not let
inherited trust survive a path-changing event just because no one has yet filed a fresh departure
packet. If not, the archive prefers branch-or-cap decisions over silent inheritance. See
[`pilot-to-scale-evidence-and-rollout-gates.md`](pilot-to-scale-evidence-and-rollout-gates.md),
[`sector-and-function-profile-splits-for-rollout-gates.md`](sector-and-function-profile-splits-for-rollout-gates.md),
[`sector-and-function-profile-splits-for-memory-defaults.md`](sector-and-function-profile-splits-for-memory-defaults.md),
and
[`persistent-memory-personalization-and-learner-model-boundaries.md`](persistent-memory-personalization-and-learner-model-boundaries.md).

## Rule 4A. Recurring services need an AI service bill of materials

The nine procurement questions are no longer enough once a service becomes recurring, integrated,
learner-facing, record-adjacent, or action-taking. The archive now requires a current AI service
bill of materials and intake record before a service moves beyond exploration.

At minimum, the record must name the service owner, model / system components, data flows, memory
posture, action authority, construct and cognitive-effort budget, proof burden, accessibility path,
security boundary, human fallback, evidence claim, change gate, and exit plan. See
[`ai-service-bom-and-procurement-intake.md`](ai-service-bom-and-procurement-intake.md) and
[`../30-operations/ai-service-intake-and-decision-record-template.md`](../30-operations/ai-service-intake-and-decision-record-template.md).

For tool-enabled, RAG-backed, LMS/SIS-integrated, or record-adjacent services, procurement must also
include adversarial workflow testing. Prompt injection, insecure output handling, retrieval
poisoning, tool misuse, data exfiltration, and record contamination are educational risks because
they can become grading errors, support-route exposure, misconduct false positives, accessibility
harms, or official-record faults. See
[`ai-service-security-red-team-and-agentic-tool-boundaries.md`](ai-service-security-red-team-and-agentic-tool-boundaries.md).

## Rule 5. Minimum evidence package rises with stakes

### Low-stakes package

At minimum require:

- a one-page use-case memo,
- privacy/data review,
- student-facing guidance for any recurring learner-service use, including the local default table
  or named equivalent for those functions and any inherited sector-and-age profile layer,
- teacher-facing guidance on appropriate delegation, including the local default table or named
  equivalent for recurring teacher-side functions and any inherited sector-and-age profile layer,
- institution-facing guidance for any recurring clerical, queueing, flagging, or decision-support
  use, including the local default table or named equivalent for those functions,
- a simple explanation of how the tool fits local mode/disclosure rules,
- a named memory / personalisation profile or equivalent statement for any recurring learner-,
  teacher-, or institution-facing use that persists across sessions, plus any sector-and-function
  memory overlay where the generic ladder is already too blunt, plus the `M3` rail addendum where
  any consequence-bearing memory sits on a human-owned rail, plus any inherited readiness / queue
  child-branch overlay naming the review-window band, substitute-path default, and publication
  trigger in use, plus a named observability/retention profile and any sector-and-function overlay
  where the generic logging floor is already too blunt,
- a quick accessibility check for the intended user group and devices,
- and a short post-adoption check on workload, errors, and obvious misuse.

This is enough for bounded support tools, but not for stronger learning claims, and it is not yet a
scale claim. In the archive's current grammar this package usually earns at most `RG1`, not broad
default deployment.

### Medium-stakes package

At minimum require:

- a bounded pilot with comparison to current practice or a clear baseline,
- teacher training before student launch,
- family and student notice where relevant,
- subgroup review for equity and accessibility,
- an explicit decision on which uses belong in pedagogical disclosure versus protected support
  routing,
- and explicit stop conditions for dependency, hallucination, bias, inaccessible design, loss of
  teacher visibility, over-capture of learner traces, hidden learner-model drift, or
  institution-side queue/flag drift that cannot be explained or contested.

This is the archive's default package for tutoring, advising, and formative-support tools. Tools
that cannot support clear course-level expectations without hidden logging or awkward workarounds
should be treated with caution. Even then, a successful medium-stakes pilot should usually pass
through a monitored `RG2` stage before broad scale. See
[`../30-operations/course-level-ai-use-grammar.md`](../30-operations/course-level-ai-use-grammar.md),
[`pilot-to-scale-evidence-and-rollout-gates.md`](pilot-to-scale-evidence-and-rollout-gates.md), and
[`sector-and-function-profile-splits-for-rollout-gates.md`](sector-and-function-profile-splits-for-rollout-gates.md).

### High-stakes package

The archive's default posture is **non-delegation of final judgment**. If AI is used at all,
require:

- documented validation in the local context,
- human accountable sign-off,
- appeal and override paths,
- public explanation of the tool's role,
- and rights review for civil rights, disability, and due-process concerns.

In many cases, the right answer remains: do not use AI to make the determination. Where institutions
do use teacher-facing or institution-facing AI for drafting, analytics, triage, or communication
around a high-stakes function, the accountable sign-off or contestability line should be published
in advance rather than improvised after a failure.

## Rule 6. Back teacher augmentation before teacher replacement

Current evidence is strongest for AI that helps educators or tutors do their work better, not for
systems that fully replace them. Tutor CoPilot is notable precisely because it augments tutors and
improves their pedagogical moves. See `B13`.

## Rule 7. Keep families and learners legible in the loop

U.S. DOE's toolkit emphasizes transparency and opportunities for students, teachers, and parents to
opt out of AI-enabled applications. This matters especially when institutions serve minors or
vulnerable populations. See `B07`.

## Rule 8. Procurement must include equity and accessibility review

A tool that works only for already-advantaged students or that increases disability barriers is a
failed educational intervention even if average performance looks positive. OECD and UNESCO both
reinforce this. OECD's 2026 work on neurodivergent learners adds a practical warning about
affordability, teacher-capacity gaps, and the risk that cheating concerns will constrain legitimate
assistive use. For many public institutions, accessibility is not merely aspirational but
increasingly concrete: public web and app surfaces generally need WCAG-aligned accessibility,
including vendor-provided content in the institution's service environment. See `B01`, `B09`, `B10`,
`B19`, `B20`, `B27`, `B28`.

## Current purchasing heuristic

The archive's current practical heuristic is:

> buy or deploy AI for education only when the tool is teacher-visible, rights-compatible,
accessibility-checked, placed on the right rung of the deployment ladder, matched to an explicit
rollout gate rather than scaled on pilot glow, plus any sector-and-function rollout overlay where
minors, formal assessment, professional gatekeeping, or public-route services already need a hotter
scale burden or lower default ceiling, plus any child-branch rollout overlay where tutoring, marking
support, readiness signalling, or queue-shaping route systems no longer share one parent path to
scale, compatible with light course-level legibility plus protected support routing, paired with
explicit student-facing, teacher-facing, or institution-facing default tables where the function
recurs, plus sector/age profile overlays where those defaults already need a stricter or cooler
floor, matched to a published memory / personalisation rule so institutions can say what the system
remembers and whether that memory is learner-declared or inferred, plus any starter memory profile
where minors, formal assessment, professional gatekeeping, or public-route services already need
cooler defaults, earlier human-owned rails, or lower ceilings than the generic `M0-M4` ladder
suggests, plus any child-branch memory overlay where tutoring, accommodation continuity,
professional coaching, or informational route help no longer share one memory ceiling with
support-routing, candidate-control, readiness-signalling, or queue-shaping systems, plus the rule
that cooler child branches harden only while memory stays function-bounded and non-portable and
hotter child branches usually harden only as named `M3` rails or human-only handling, plus a
published indication of whether any `M3` rail uses the archive's shared schema or a function-locked
local-only map, and for the function-locked rails a published inheritance split between portable
floor, rail-family presumption, and permanently local residue rather than one undifferentiated local
code, plus any rebuttal packet where a local system departs from a strengthened or branched family
presumption or from one of the new branch-specific review-window / substitute-path overlays, plus a
published indication of whether `RS-INTERNAL-PROGRESSION` is using the archive's portable unchanged
overlay, whether `RS-EXTERNAL-PRACTICE-ACCESS` is using `RS-EPA-PARTNER-CAPACITY`,
`RS-EPA-LS-PROVIDER-CLEARANCE`, or `RS-EPA-LS-EXTERNAL-BAR`, whether `QS-SCARCE-SEAT` is using
`QS-SS-BATCH-OFFER`, `QS-SS-RS-SAME-OWNER`, or `QS-SS-RS-CROSS-OWNER`, and whether any
`QS-URGENT-DUTY` service has entered the named `QS-UD-CHILD-SAFETY` branch or is still publishing
only the first-stable review point plus regime-local substitute protection rather than pretending a
more portable anti-penalty default exists, plus a published indication of whether any of those
authority-sensitive branches is using the archive's narrower authority-family variant for
regulator-bar versus host-bar, public-dispatch versus partner-inventory, or provider-led
safeguarding review versus formal multi-agency child-protection stage, rather than leaving the
authority family implicit, plus the archive's default event-anchor / interim-protection pairing for
that family where one now hardens, plus the limited anti-forfeiture or anti-punishment floor that
travels with it, plus the seven-field departure packet whenever any of those hardened elements is
omitted, weakened, or replaced in a consequence-bearing way, while keeping rank effects,
challenge-pause posture, concrete substitute packages, and legal calendars local unless a rebuttal
packet or later revision says otherwise, matched to a published observability/retention rule so
safety logging, proof review, and appeal handling do not silently become ambient surveillance, plus
any sector-and-function observability overlay where minors, formal test monitoring, professional
gatekeeping, or public-route coordination already require different default rails or stronger
modality limits, plus any sector-and-function change overlay where minors, formal assessment,
professional gatekeeping, or public-route services already require hotter inherited release
defaults, pedagogically shaped where stronger claims are being made, and tied to a concrete proof
plan for educational value, including any inherited proof-profile overlay where minors, ordinary
higher education, professional-practice, or public adult-route contexts should not share one burden
default.
