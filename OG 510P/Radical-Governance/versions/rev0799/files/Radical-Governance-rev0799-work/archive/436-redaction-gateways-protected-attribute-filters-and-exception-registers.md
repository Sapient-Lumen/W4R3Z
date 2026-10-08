# 436 — Redaction gateways, protected-attribute filters, and exception registers

## One-line thesis

Public AI systems should default to **redaction before inference**: block or strip unnecessary personal data, prohibit protected-attribute and emotion inference by default, and require a named, reviewable exception register for the rare cases law explicitly permits.

## Why this matters

A great deal of public AI risk begins before the model generates anything. It begins at the input field, the upload box, the camera feed, the prompt template, or the quiet reuse of a dataset that contains more personal detail than the service actually needs. Once that information crosses the boundary into the system, the institution is already exposed to privacy, discrimination, procedural-fairness, and security risk.

Current official materials increasingly support a stricter posture than “be careful with sensitive data.” Canada’s current design guidance for AI help applications says teams should gather only the personal information necessary for the AI to function, should not retain conversational personal information for secondary purposes, and should remove and redact as much personal information in the user input field as possible rather than sending it to the AI service or storing it. NARA’s 2025 AI compliance plan describes internal safeguards for its approved generative AI assistant that prohibit classified or sensitive data, including PII and CUI, and forbid high-impact AI uses without CAIO approval. The EU AI Act goes further for specific inference classes: it prohibits biometric categorisation used to infer political opinions, trade union membership, religious or philosophical beliefs, race, sex life, or sexual orientation, and prohibits emotion-recognition uses in workplace and education contexts, subject only to narrow legal carve-outs and safeguards.

The archive should therefore treat **input governance** as a first-class public-control layer. Many institutions spend more time debating how to explain outputs than how to stop the wrong inputs, wrong inferences, and wrong sensing modes from entering the system in the first place.

## Pattern pack

### 1. Put a redaction gateway in front of every public-facing AI input

Before user text, uploaded files, or retrieved records are sent to a model or AI pipeline, the service should pass them through a gateway that can:

- strip obvious personal information that is not necessary for the task,
- block sensitive identifiers where the service has no need for them,
- detect when the prompt no longer makes sense after redaction,
- and return the user to a safer, reformulated request path instead of sending garbage or sensitive residue onward.

A redaction gateway is not only a privacy aid. It is also a way to shrink the problem space to the minimum data actually needed.

### 2. Maintain a banned-inference list, not just a banned-tool list

Institutions should document classes of inference the service must not attempt, even if a vendor claims the model can do them. This list may include:

- inferring protected attributes from biometric or behavioural data,
- inferring emotional state in contexts where power imbalances make misuse likely,
- inferring intent, credibility, or dangerousness from thin behavioural traces,
- or converting free-text queries into hidden risk scores without legal authority and clear review.

A banned-inference list governs what the system is forbidden to *conclude*, not only which model the institution happens to buy.

### 3. Separate lawful exceptions from everyday operation

If law allows a narrow exception for a sensitive inference or sensing mode, that use should not disappear into ordinary operations. It should have:

- a specific legal basis,
- a named owner,
- a written necessity and proportionality case,
- explicit time, geography, data, and user-scope limits,
- stronger logging and audit review,
- and a visible expiry or reauthorisation date.

Exceptional authority should look exceptional in the governance record.

### 4. Distinguish structured service inputs from exploratory staff prompts

Public services often conflate two very different things:

- a governed operational workflow with defined required fields, and
- open-ended prompt experimentation by staff.

The former should be tightly fielded, validated, and minimised. The latter should stay out of live consequential workflows unless and until it is converted into a governed service path. “Flexible prompting” is often another name for undeclared scope drift.

### 5. Keep unsafe content out of the model, not only out of the user interface

Threats, profanity, jailbreak attempts, and disallowed requests should be intercepted before the model call where practical. If blocked content still reaches the model and is merely hidden from the end user, the institution still bears the upstream risk.

### 6. Make redaction failures visible as incidents and design debt

Redaction misses, accidental sensitive-data transmission, or repeated attempts to use banned inference paths should feed:

- incident logs,
- model and workflow adjustments,
- refreshed notices and runbooks,
- and possible narrowing of the approved use case.

A redaction layer that quietly fails is worse than one that visibly stops the service.

### 7. Publish the existence of exception classes without disclosing sensitive operations

The public record should at least reveal that an exception framework exists, what kinds of special handling are possible in principle, who authorises them, how they expire, and what oversight bodies review them. Detailed operational facts can still be lawfully withheld where needed.

## Guardrails

- Default to collection minimisation before model improvement.
- Treat protected-attribute inference as a special governance event, not a feature request.
- Do not rely on vendor claims that sensitive attributes are not *really* being inferred because they are not named explicitly.
- Keep exception pathways narrow, expiring, and reviewable.
- Redact before storage and before transmission, not just before display.

## Failure modes

- **input sprawl**: the system receives far more personal data than it needs because free text is easier than service design.
- **hidden trait extraction**: a system claims to classify behaviour or risk while effectively inferring protected attributes through proxies.
- **normalised exception**: extraordinary sensing or inference authorities become routine because the exception path is invisible.
- **cosmetic filtering**: the interface hides bad content while the backend still receives and stores it.
- **prompt drift into casework**: exploratory prompt use turns into live decision support without ever passing through a governed input design.

## Practical tests

An input-governance regime passes when it can answer yes to all of the following:

1. Does every public AI entry point apply data-minimisation and redaction before model processing where appropriate?
2. Is there a written banned-inference list covering protected attributes, emotion recognition, and similar sensitive conclusions?
3. Are lawful exceptions separately authorised, time-limited, logged, and reviewable?
4. Can the institution show what happens when a redacted query no longer makes sense, instead of sending it anyway?
5. Are redaction misses and blocked-inference attempts treated as incident and design signals?

## Compression rule for the archive

If the safest place to stop a harmful inference is before the model call, then governance that begins only at the output is already **too late**.
