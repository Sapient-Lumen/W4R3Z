# 438 — Citation-gated public chatbots, approved source hierarchies, and abstention

## One-line thesis

Public AI assistants should answer only when they can stay inside an **approved source hierarchy** and return an authoritative citation; when they cannot, they should abstain, hand off, or route the user to the right wizard, form, or human channel instead of improvising.

## Why this matters

Public-service chatbots fail in a specific and predictable way: they sound helpful precisely when they are least grounded. This is especially dangerous when the user assumes the system is speaking with state authority.

Current official guidance is moving toward a much tighter design pattern. Canada’s 2026 content guidance for AI help applications says AI help applications must produce accurate responses and always include a citation link, that all in-scope answers must include at least one authoritative citation link to source material, and that responses should wherever possible cite Government of Canada webpages so users can review the source for themselves. The same guidance says responses should be generated only from trusted sources such as Canada.ca, that existing online wizards should be preferred to the AI improvising its own branching interview, and that shorter answers help prevent hallucination. NIST’s Generative AI Profile similarly recommends reviewing and verifying sources and citations in outputs during pre-deployment measurement and ongoing monitoring, and verifying that retrieval-augmented-generation data is grounded. CRA’s public chatbot describes its purpose as helping Canadians quickly find trusted information on CRA programs and services, not as inventing an open-ended answer space.

The archive should therefore sharpen a rule that is only implicit in many public deployments: **no citation, no answer** for in-scope consequential guidance. The assistant’s job is not to sound generally informed. It is to safely route people to authoritative content, the right next step, or a reachable human path.

## Pattern pack

### 1. Maintain an approved source hierarchy

Each public AI assistant should declare a ranked source hierarchy such as:

1. canonical service pages,
2. official wizard or eligibility tools,
3. official forms and transactional pages,
4. official policy or legal references,
5. and only then any approved secondary explanatory materials.

If a requested answer cannot be grounded inside that hierarchy, the assistant should not fabricate one.

### 2. Require at least one authoritative citation for every in-scope answer

For any answer that gives guidance, requirements, eligibility information, steps, or deadlines, the system should return at least one visible authoritative citation close to the answer. Citation gating should happen before release, not as a post-hoc nicety.

### 3. Prefer routing over imitation when a wizard already exists

If an official wizard or step-by-step decision tool exists, the assistant should route the user there instead of trying to reproduce branching eligibility logic from memory. This is especially important when rules are updated frequently or contain nested conditions.

### 4. Separate answerable questions from handoff questions

The service should explicitly classify requests into:

- answerable with grounded citation,
- needs clarification before a grounded answer is possible,
- route-to-wizard or route-to-form,
- out of scope,
- or requires human assistance.

That classification itself is a governance function.

### 5. Use abstention text that is helpful, not evasive

A good abstention should tell the user:

- why the system cannot answer reliably,
- what official source it can point to,
- what question would make a grounded answer possible,
- or which human/service channel can help next.

Abstention is a service action, not a failure to serve.

### 6. Monitor citation quality, not only answer fluency

Teams should measure:

- citation presence,
- citation correctness,
- citation relevance to the specific claim,
- dead-link and outdated-link rates,
- and the rate at which users must ignore the cited page because it does not actually support the answer.

A polished answer with a weak citation is still a governance defect.

### 7. Keep prompt policy aligned with source policy

If the assistant is instructed to be conversational, empathetic, or concise, those style goals must remain subordinate to the source hierarchy. Tone must not pressure the system into answering when the source basis is weak.

## Guardrails

- No authoritative citation, no authoritative-sounding answer.
- Keep official sources canonical and versioned.
- Route to existing wizards instead of reverse-engineering their logic in free text.
- Measure citation correctness continuously.
- Treat abstention and handoff as part of the product, not as edge-case behavior.

## Failure modes

- **fluent fabrication**: the assistant answers from general model priors rather than approved sources.
- **ornamental citation**: a link is shown, but it does not support the actual claim made.
- **wizard bypass**: the assistant recreates complex eligibility logic badly instead of routing to the maintained official flow.
- **scope bleed**: the assistant answers out-of-scope questions because it has no explicit abstention path.
- **tone override**: a friendliness instruction causes the model to guess rather than pause.

## Practical tests

A source-governed assistant passes when it can answer yes to all of the following:

1. Is there a written approved source hierarchy for the assistant?
2. Does every in-scope answer include at least one authoritative citation that actually supports the claim?
3. Does the system route to official wizards or forms when they exist instead of improvising them?
4. Can the assistant abstain or hand off cleanly when no grounded answer is available?
5. Are citation quality and drift monitored as operational metrics?

## Compression rule for the archive

When a public AI assistant cannot show its source, it should usually **show the user the route instead of the guess**.
