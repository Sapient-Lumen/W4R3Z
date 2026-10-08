# 439 — Legal-authority maps, scope gates, and jurisdiction labels

## One-line thesis

A public AI system should not reach consequential use until the operating team can name the **decision it affects, the authority that permits it, the scope test that brings it under governance, and the review route that governs challenges to it**.

## Why this matters

Public-sector AI often fails before any model error appears. The deeper failure is that nobody can cleanly answer a basic administrative-law question: what decision is this system helping make, under what authority, and under which governing regime? When those answers are vague, teams misclassify systems as harmless experimentation, miss mandatory controls, and leave affected people unsure which appeal or review path applies.

Current official guidance points toward a tighter pattern. Canada’s Guideline on Service and Digital says automated decision systems must be compatible with transparency, accountability, legality, and procedural fairness, and that decisions produced using these systems should be made pursuant to Canadian law. The related scope guidance says departments should test whether a system is used by a department, developed or significantly modified after the trigger date, used within an administrative decision-making process, replaces or assists judgment, and is used in production. The AIA also explicitly asks whether new policy or legal authority is required and directs teams to consult legal services and ATIP early. The UK’s ATRS guidance similarly expects teams to explain how a tool fits into the broader operational process, who owns it, and whether its outputs or the surrounding process can be appealed or reviewed.

The archive should therefore add a simple but hard rule: **no live consequential deployment without an authority map and a scope label**. A system that cannot state its legal footing is not yet ready to act with public force.

## Pattern pack

### 1. Write an authority map before production

For each AI-assisted function, create a compact authority map that states:

- the exact decision, assessment, prioritisation, recommendation, or routing action involved;
- the statute, regulation, policy instrument, program authority, or delegated power that permits that action;
- whether the system merely informs human judgment or helps determine a legally significant outcome;
- and the accountable public office that owns the authority, not only the technical service.

### 2. Run a scope gate that asks whether the system is truly in production

Before launch, classify the use case against a written scope gate such as:

- does it affect a real client, case, application, entitlement, investigation, or enforcement step?
- does it replace or assist human judgment or discretion?
- is it being used in a production environment, even if only on a bounded beta or pilot population?
- has a significant modification changed scope, capability, or the affected population?

Research, testing, and proof-of-concept work should be labelled as such. Once outputs affect real clients, the production obligations should attach.

### 3. Publish a jurisdiction label with the public record

Every public record for the system should include a compact jurisdiction label, for example:

- administrative decision support / in scope,
- client-help assistant / public information only,
- operational triage / no direct client effect,
- research-only / not used in live decisions,
- or mixed use / split controls apply.

This reduces the common ambiguity where a system is treated as “just informational” even though it materially channels or constrains later decisions.

### 4. Tie the authority map to a named review route

For each function, record which review route applies when a person wants to challenge the outcome:

- internal reconsideration,
- formal appeal,
- complaint pathway,
- ombuds or inspector channel,
- privacy challenge,
- judicial review,
- or no direct review because the function is not outcome-determinative.

If there is no meaningful review route, that is itself a governance finding that should block certain uses.

### 5. Separate system authority from supplier authority

A supplier contract, model licence, or platform approval is not the legal authority for public action. The authority map should distinguish:

- what the government is legally empowered to do,
- what the supplier is technically allowed to provide,
- and what the deployer is actually authorising the system to influence.

### 6. Re-open the authority map after material change

Any material change to:

- the decision type,
- the affected population,
- the deployment context,
- the model capability,
- or the degree of human reliance

should trigger a fresh scope test and a refreshed authority map.

### 7. Use authority labels at the operator interface too

Operators should see the use case’s authority and scope label inside the workflow, not only in compliance files. This helps prevent staff from expanding the tool into adjacent tasks that were never approved.

## Guardrails

- No consequential deployment without a written authority map.
- Production pilots that affect real clients should be governed as production.
- The governing regime should be named, not implied.
- Every consequential function should have a review-route label.
- Vendor approval does not substitute for public legal authority.

## Failure modes

- **authority blur**: the team can describe the model but not the public power it is exercising or informing.
- **prototype laundering**: a live pilot is treated as research to avoid stricter obligations.
- **review mismatch**: affected people are sent to the wrong complaint or appeal path.
- **scope creep**: staff extend the system into adjacent decisions because the approved authority boundary is invisible.
- **contract confusion**: a vendor permission or procurement approval is mistaken for legal authority to act.

## Practical tests

A use case passes this pattern when it can answer yes to all of the following:

1. Is the exact public action or decision the system affects clearly named?
2. Is there a written authority map tying that action to law, policy, or delegated program authority?
3. Has the team explicitly tested whether the use case is in scope because it assists or replaces judgment in production?
4. Is there a named review, recourse, or appeal route appropriate to the function?
5. Would a new use context or material change automatically trigger a fresh scope and authority review?

## Compression rule for the archive

When a public AI system cannot state **what power it touches and under whose authority**, it is still too early to let it touch the public.
