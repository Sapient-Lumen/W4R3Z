# 430 — Public system cards, operating bounds, and warning labels

## One-line thesis

Consequential public AI should ship with a public system card that states intended purpose, operating bounds, known limitations, language and accessibility coverage, and explicit no-use conditions at the point people actually encounter it.

## Why this matters

Public institutions often disclose that they “use AI” without telling people what the system is actually for, where it is likely to fail, or what should never be delegated to it.

That gap matters. A public-facing chatbot, triage assistant, fraud flagger, or eligibility support tool can look authoritative even when the institution itself knows the tool is probabilistic, incomplete, or reliable only inside a narrow operating envelope. If those limits remain buried in procurement files or internal assurance packs, the public receives the performance aura without the decision boundary.

Current official guidance points to a stronger norm. The UK AI Playbook makes “you know what AI is and what its limitations are” its first principle and requires public bodies in scope to use the Algorithmic Transparency Recording Standard and make that information clearly accessible to the public. The EU AI Act says instructions for use should help deployers make informed decisions, include meaningful and understandable information, and use illustrative examples for limitations and intended and precluded uses where appropriate. Canada’s current AI help-application guidance adds two operationally important details: regularly test for accuracy, and tell users in plain language that AI can make mistakes and they should verify the answer. It also says departments should test generative systems to ensure output quality meets official-language requirements.

The archive should therefore treat the **public system card** as a live governance artifact. It is the compact public-facing equivalent of the internal assurance pack: not every technical detail, but enough to make the system’s actual envelope legible before trust outruns evidence.

## Pattern pack

### 1. Publish one compact public card per consequential system

Every consequential public AI system should have a public card that can be reached from:

- the service page,
- the transparency register entry,
- the notice shown to users,
- and any appeal or complaint route connected to the system.

This card should not require the public to decode a procurement record or read a full impact assessment before learning the basics.

### 2. Name the job the system is for — and the job it is not for

A good card should say plainly:

- what the system does,
- who uses it,
- what human role remains decisive,
- what kinds of outputs it produces,
- what decisions it can inform,
- and what decisions it must not make alone.

This reduces the common failure mode where a tool drifts from “decision support” into practical substitution because nobody kept repeating the boundary.

### 3. State operating bounds and no-use conditions explicitly

The card should include explicit boundaries such as:

- only for draft assistance, not final determination,
- only for low-risk triage, not refusal or sanction,
- not reliable for novel or out-of-domain cases,
- not to be used without a trained operator,
- not to be used where evidence is missing or disputed,
- not to be treated as sole source of truth.

If the team already knows the tool degrades under certain workloads, languages, data conditions, or subject matters, those limits belong on the card.

### 4. Surface known limitations in usable language

Known limitations should be written for ordinary users and practitioners, not only for lawyers or engineers. That includes:

- likely error types,
- uncertainty conditions,
- quality differences across groups or languages,
- gaps in citations or evidence linkage,
- conditions under which human verification is mandatory,
- signs that the system is outside its operating envelope.

This is where “AI can make mistakes” becomes more than a slogan. The warning should point to the specific kinds of mistakes the institution actually expects.

### 5. Declare language and accessibility coverage as part of the performance envelope

A public system is not genuinely “working” if it performs acceptably only in one language or only for users who can navigate a particular interface. Public cards should therefore state:

- which languages are supported and tested,
- whether outputs vary materially by language,
- what accessibility checks have been performed,
- which alternative channels exist if the AI path is not workable,
- and whether citations, notices, and explanations are available in the same language and format as the interaction.

Treating language and accessibility as aftercare hides real performance boundaries from affected people.

### 6. Put the short warning label at the point of interaction, not only in a registry

A long-form system card is useful, but users also need a short warning label where they meet the tool. For example:

- this response was generated by AI,
- it may be incomplete or mistaken,
- check the cited source or ask for human help,
- do not rely on this tool alone for urgent or high-stakes action.

The point is not theatrical disclaimers. The point is to interrupt false certainty at the moment the output is most persuasive.

### 7. Refresh the card whenever the real envelope changes

A system card is stale if the model, provider, prompt structure, retrieval source, supported language set, or degree of automation changes while the public description does not. Material changes should trigger:

- refreshed limitations,
- refreshed no-use conditions,
- updated examples,
- updated language and accessibility coverage,
- and a dated public version note.

## Guardrails

- Do not let public cards collapse into vendor marketing or generic assurance boilerplate.
- Do not describe intended use without also naming precluded use.
- Keep warning labels short, but anchor them in the real limitations documented elsewhere.
- Do not imply support for languages, formats, or use contexts that have not been meaningfully tested.
- Make the card reachable from the actual service interface, not only from oversight pages.

## Failure modes

- **glossy card**: the card describes benefits but not boundaries.
- **limitation laundering**: known limits exist internally but are translated into vague public phrasing like “results may vary”.
- **single-language illusion**: the institution claims a public AI tool is generally ready while only one language path has been checked seriously.
- **registry-only transparency**: the information exists somewhere in a register but not where users encounter the system.
- **stale boundary**: the model or operating context changes but the public card still describes the old system.

## Practical tests

A public-card regime passes when it can answer yes to all of the following:

1. Can a user learn the system’s intended purpose and no-use conditions in under two minutes?
2. Does the card describe concrete known limitations instead of generic disclaimer language?
3. Are language and accessibility coverage treated as part of the operating envelope?
4. Is a short warning label shown at the point of interaction?
5. Do material changes trigger a visibly updated version of the card?

## Compression rule for the archive

If a public AI tool can be encountered faster than its operating bounds can be understood, the institution is still shipping **confidence before context**.

