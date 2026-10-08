# AI service security, red-team, and agentic tool boundaries

## Current overlay

Security now threads through procurement, evidence grading, action authority, observability,
failure, change, assessment proof, and public-route recognition. Prompt injection, retrieval
poisoning, insecure output handling, excessive agency, data exfiltration, and record contamination
are not just IT risks; they can become learner, teacher, assessment, accessibility, and standing
harms.

Education AI security is not only an IT issue. A compromised or poorly bounded AI workflow can
expose learner records, alter grades or queues, fabricate feedback, mishandle protected support
evidence, send misleading notices, or turn ordinary classroom artifacts into instructions for
downstream systems.

This surface adds a compact security posture for AI services that retrieve content, call tools,
write records, summarize evidence, recommend actions, or operate inside LMS, SIS, assessment,
advising, library, workforce, or public-route systems.

## Default security rule

> Any AI service that can read institutional data, retrieve documents, call tools, or influence
records must be treated as an integrated workflow with adversarial inputs, not as a harmless
chatbot.

The archive therefore distinguishes conversational risk from **agentic workflow risk**. A model that
only drafts text for a teacher has one risk profile. A model that reads student submissions,
retrieves policy, writes notes, flags misconduct, updates queues, sends notices, or triggers support
routes has another.

## Security posture ladder

| Code | Name | Meaning | Default treatment |
|---|---|---|---|
| `SEC0` | Non-integrated use | No institutional data, tools, memory, or record effect | Course grammar and ordinary digital-safety rules may suffice |
| `SEC1` | Read-only institutional context | The service can see bounded institutional content but cannot call tools or write records | Require source permissions, logging minimization, and output review |
| `SEC2` | Retrieved / uploaded content exposure | The service processes learner work, webpages, PDFs, code, images, or RAG content that may contain hostile instructions | Require prompt-injection testing and source isolation |
| `SEC3` | Tool-enabled workflow | The service can call tools, send messages, create drafts in systems, or modify reversible workflow state | Require tool allowlist, human approval, rollback, and abuse tests |
| `SEC4` | Record-bearing or consequence-bearing workflow | The service can affect grades, attendance, queues, eligibility, support routes, discipline, or official records | Keep human-owned; require audit, contestability, and legal / policy review |
| `SECX` | Blocked boundary | The workflow cannot be made safe enough for the proposed authority, memory, or cohort | Do not deploy; redesign or keep human-only |

`SEC2` is the inflection point. Once untrusted content enters the context window or retrieval path,
the service must assume prompt injection, policy hallucination, and data-exfiltration attempts are
plausible.

## Required adversarial test families

| Test family | Question |
|---|---|
| Prompt injection | Can user, webpage, document, image, code, or retrieved text override the intended instructions? |
| Indirect prompt injection | Can content from a trusted-looking source cause the AI to reveal data, ignore policy, or misuse tools? |
| Data exfiltration | Can a learner, staff member, vendor actor, or external page extract records outside their role? |
| Insecure output handling | Are generated outputs treated as commands by LMS, SIS, email, forms, code, grading, or support systems? |
| Tool misuse | Can the AI call a tool outside the user's intention, role, or authority ceiling? |
| Retrieval poisoning | Can outdated, malicious, inaccessible, or unauthorized material enter the RAG corpus? |
| Record contamination | Can AI-generated uncertainty become official fact, misconduct evidence, accommodation evidence, or eligibility evidence? |
| Cost / denial-of-service | Can repeated or adversarial use cause outage, throttling, runaway cost, or delayed support? |
| Human-overtrust | Can staff reasonably distinguish suggestion, draft, flag, evidence, and official decision? |

Testing must use the actual integrated workflow. A clean base-model test does not prove that an LMS
plugin, browser extension, RAG corpus, or tool-enabled agent is safe.

## Agentic boundary rules

1. **Tools are authority.** A tool call is not a chat response; it is a possible institutional act.
2. **Untrusted content must not grant instructions.** Student work, retrieved webpages, PDFs,
   comments, images, and code are data, not policy.
3. **Record-bearing tools require human ownership.** AI may draft or queue, but official grades,
   discipline, eligibility, accommodation, and certification actions need accountable human decision
   paths.
4. **Generated output is not a source of record truth.** A summary can point to evidence; it cannot
   become evidence merely because it is fluent.
5. **Least privilege is educational policy.** Give the AI only the data, tools, cohort, and duration
   required for the approved purpose.
6. **Logs must be enough for incidents but not a surveillance archive.** Keep security
   reconstruction separate from routine learner profiling.
7. **Rollback must be rehearsed.** If a tool writes or sends anything, the owner must know how to
   undo, notify, correct, and protect affected learners.
8. **Hot combinations require earlier human stop gates.** `AA3+SEC2`, `AA4+SEC3`, `AA5`, `M3`,
   protected support, minors, and high-stakes assessment should not launch on vendor assurances
   alone.

## Security fields for decision records

Every `SEC2+` service record should include:

- authorized data sources;
- prohibited data sources;
- RAG corpus owner;
- tool allowlist;
- maximum `AA` authority;
- maximum `M` memory state;
- prompt-injection test date;
- retrieval-poisoning test date;
- data-exfiltration test date;
- rollback owner;
- incident-notice owner;
- evidence-retention boundary;
- protected-support evidence boundary;
- and next security review date.

## What must not happen

The archive rejects these shortcuts:

- “The vendor says it is secure” as a substitute for workflow testing;
- using AI detectors as discipline triggers without construct, evidence, and contestability
  controls;
- allowing a chatbot to summarize accommodation evidence into ordinary analytics or misconduct
  files;
- letting an AI agent send official notices, update queues, or alter records without human-owned
  authority;
- treating AI-generated summaries as canonical proof when the underlying evidence is missing,
  inaccessible, or contested;
- retaining full traces indefinitely because they might someday help security;
- using security logs for teacher evaluation, learner ranking, or behavioral profiling.

## Fit with the archive

This surface strengthens, but does not replace:

- [`ai-service-bom-and-procurement-intake.md`](ai-service-bom-and-procurement-intake.md);
- [`ai-action-authority-register-and-delegation-ceilings.md`](ai-action-authority-register-and-delegation-ceilings.md);
- [`minimum-observability-and-retention-without-surveillance.md`](minimum-observability-and-retention-without-surveillance.md);
- [`failure-escalation-safe-degradation-and-manual-fallback.md`](failure-escalation-safe-degradation-and-manual-fallback.md);
- [`model-and-workflow-change-classification-and-fresh-review-triggers.md`](model-and-workflow-change-classification-and-fresh-review-triggers.md);
- and
  [`persistent-memory-personalization-and-learner-model-boundaries.md`](persistent-memory-personalization-and-learner-model-boundaries.md).

See `B275`, `B280`, and `B281`.

## Rev0214 action-authority overlay

Security review now cross-checks action authority.

| Agentic security finding | Required authority response |
|---|---|
| prompt-injection path can alter instructions | cap at `AA2` until mitigated and re-tested |
| tool can write, send, delete, schedule, or label | treat as `AA4` or `AA5` even if marketed as assistance |
| output can trigger queue, priority, or investigation | treat as `AA3` and require contestability |
| rollback cannot reconstruct action chain | no `AA4+` authority |
| protected fact can leak into ordinary workflow | pause or retreat to protected owner route |

A service cannot claim a secure agentic workflow while its actual action authority is unnamed.
