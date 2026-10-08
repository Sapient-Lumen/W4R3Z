# 879 — Staff-facing AI copilots, casework triage, draft records, and no public action by invisible autocomplete

## One-line thesis

A staff-facing AI copilot is not safe merely because the public never sees it; when it drafts, summarizes, classifies, routes, prepopulates, flags, or records public-service work, it needs an internal action docket that proves use-case boundaries, source lineage, output capture, review quality, queue effects, sensitive-data controls, model-change records, and error feedback before invisible autocomplete becomes public action.

## Why this matters

`876` handled public-facing generative guidance: the state speaking to the public through a chatbot, RAG assistant, or service bot. Staff-facing tools are quieter and often more dangerous to accountability. They may never produce an official answer themselves. Instead, they draft the answer an official sends, summarize the record an official reads, classify the incoming letter, flag vulnerability, write the first version of an inspection report, extract fields into a case file, or route work to a queue. The citizen sees a normal official act. The model disappears behind the staff member.

That invisibility can be appropriate. A tool that shortens a draft, helps a civil servant summarize a long document, or prepopulates routine fields may save time without changing the legal boundary. But invisibility also creates **shadow action**: practical public power is shaped before the public receives notice, reasons, or a chance to correct the record. The staff member may still be formally responsible, while the real friction, framing, and first draft have already narrowed the case.

This note creates the missing docket between ordinary office software, public chatbots, and automated decisions. It says that staff-facing AI must be judged by what it does to the public workflow, not by whether the public can see the interface.

## Pattern pack

### 1. Form boundary

| Label | Finding |
| --- | --- |
| ordinary office software | too thin when the system selects, classifies, drafts, summarizes, or inserts substantive content |
| public chatbot | wrong interface if the tool only speaks to officials |
| model-mediated decision | too thick unless output directly determines benefit, debt, enforcement, sanction, inspection judgment, licence, priority, or legal effect |
| staff copilot | honest default when the tool supports officials but may shape casework, records, correspondence, reports, queues, or triage |
| shadow decision system | escalation label when human review is nominal, outputs are hard to reconstruct, or queue / draft effects predictably decide outcomes |

The public-law boundary is not the screen boundary. A staff-only interface can become a public-action waist if it supplies the draft, field, flag, or route that officials normally accept.

### 2. Internal action docket

A staff-facing AI system must carry at least these records:

| Field | Required record |
| --- | --- |
| public owner | department, service owner, senior responsible officer, product owner, complaint / review route |
| use-case register | tasks allowed, tasks forbidden, harm classes, pilot scope, expansion approval, and per-use-case risk rating |
| input lineage | documents, emails, case files, policies, transcripts, scanned images, knowledge-base pages, and upload classification |
| output lineage | draft text, summaries, extracted fields, labels, risk flags, report sections, queue movements, and model / prompt version |
| human review | who reviews, what they must check, how disagreement is recorded, and whether acceptance rates are monitored |
| queue effect | whether output changes priority, allocation, deadline, support channel, inspection scope, or response speed |
| release gate | how a draft becomes an external letter, report, notice, enforcement file, or internal recommendation |
| sensitive data | security classification, personal-data treatment, privilege, official-sensitive handling, retention, deletion, and admin access |
| supplier / model | model name, host, support access, model-switch process, prompt / retrieval change, and audit log |
| feedback loop | false positives, false negatives, staff corrections, citizen corrections, complaints, bias signals, and retraining / tuning decisions |

A staff member can be accountable only if the record lets the staff member, reviewer, citizen, auditor, and court reconstruct what the tool contributed.

### 3. Reliance ladder

| Grade | Public meaning | Control floor |
| --- | --- | --- |
| personal productivity | summarize or redraft staff-owned material | staff-use rules, retention limits, no automatic record capture |
| correspondence drafting | proposes public-facing reply | source pack, sent-output log, staff QA, public correction route |
| intake / field extraction | creates case record fields | source-image link, field provenance, correction log, mismatch audit |
| triage / queue support | changes priority, route, urgency, or support offer | queue-effect ledger, false-negative audit, vulnerable-user channel |
| report drafting | proposes findings, inspection wording, or risk assessment | evidence map, inspector / assessor edits, QA, challenge route |
| decision support | recommends outcome or legal effect | activate `874` model-decision tests |
| decision | creates legal effect | staff-copilot form is insufficient; require statutory decision, notice, reasons, review, and audit |

The crucial transition is not “AI used” versus “AI not used.” It is **draft-to-record**, **flag-to-route**, **summary-to-understanding**, and **recommendation-to-effect**.

### 4. Human review as weak control

“Human in the loop” fails when:

- the human lacks time, training, source links, or authority to reject the output;
- acceptance rates are high but not audited;
- the draft is polished enough to suppress skepticism;
- the source record is harder to inspect than the model output;
- output becomes the case note before review;
- the review checklist asks only whether the text reads well;
- queue or priority effects occur before review;
- staff corrections are not fed into model / process repair;
- managers use productivity claims to pressure acceptance.

Meaningful review requires source access, edit freedom, disagreement logging, quality sampling, and a public-law route when the output reaches the person.

### 5. Shadow-action channels

- **draft capture**: the first AI draft becomes the official answer by inertia.
- **summary capture**: officials read the summary instead of the record.
- **field capture**: extracted fields become the case truth.
- **queue capture**: a model-created flag changes urgency or allocation before anyone sees the whole file.
- **vulnerability capture**: support depends on model recognition of distress, and non-recognition becomes silence.
- **record capture**: the generated text is kept, but the prompt, sources, and edits are lost.
- **security confidence laundering**: approval for official-sensitive use becomes treated as approval for substantive reliability.
- **productivity laundering**: time saved is treated as evidence of public-law adequacy.
- **staff-responsibility laundering**: the department says the human owns the action while the workflow makes rejection unlikely.

### 6. Relationship to existing notes

Use this note with:

- `876` when the same system, or a connected system, also speaks to the public;
- `874` when staff-facing output creates or materially shapes legal effect;
- `859` and `867` when the provider, cloud, retrieval stack, or admin-support route becomes the control surface;
- `856` when the copilot becomes the practical waist through which cases, drafts, or records must pass;
- `857` when a case needs claim-level evidence and review clocks;
- `861` when a lower form, pause, human-only process, or no-new-system finding is possible;
- `870` when a public body is blamed or praised for outcomes while the operative lever is an internal platform.

### 7. Staff-copilot defeat rule

A staff-facing AI system should be narrowed, paused, or downshifted if the owner cannot show:

1. a public owner and approved use-case register;
2. task-specific prohibited-use boundaries;
3. input and output lineage;
4. meaningful human review evidence;
5. queue / priority / service-speed effect records;
6. release gates before public communication or report publication;
7. sensitive-data and privilege controls;
8. model and supplier change logs;
9. error, bias, and false-negative review;
10. a user correction or complaint route once AI-shaped output reaches the public.

### 8. Open research questions

- When should staff-copilot use be disclosed in individual reasons, letters, reports, or case files?
- What acceptance-rate threshold should trigger independent review?
- How should agencies measure false negatives in vulnerability or safeguarding flags?
- When does a general-purpose internal LLM become many unapproved use cases rather than one tool?
- Should staff-facing AI outputs be discoverable in appeals, freedom-of-information processes, or complaints?
- How should model-change records be preserved when a tool lets users choose among models?
- Can productivity trials validly measure public-law quality, or only time saved?

### 9. Holding

The archive should treat staff-facing AI as a first-class public-governance surface. The core rule is: **no public action by invisible autocomplete**. A tool may help an official think or draft, but once it shapes a public record, route, reply, report, priority, support offer, or legal file, the archive needs an internal action docket.

## Anti-theater tests

This note fails if agencies use “assistive,” “internal,” “pilot,” “human reviewed,” or “no automated decision” as blanket safety labels. Those labels are useful only after the public owner, use case, source lineage, output record, human-review quality, queue effect, release gate, sensitive-data treatment, model-change record, and feedback loop are visible.
