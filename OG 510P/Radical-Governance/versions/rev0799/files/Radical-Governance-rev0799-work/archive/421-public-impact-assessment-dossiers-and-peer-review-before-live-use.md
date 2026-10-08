# 421 — Public impact-assessment dossiers and peer review before live use

## One-line thesis

Before public automated decisions go live, operators should publish a compact **assessment dossier** that combines impact scoring, context-specific rights analysis, independent review, and accountable sign-off.

## Why this matters

A recurring governance failure is assessment fragmentation:

- one team completes a technical risk form,
- another team files privacy paperwork,
- rights impacts remain implicit,
- peer review happens late or not at all,
- the public sees only a finished system and none of the reasoning that justified live use.

Recent official practice points toward a tighter pattern. Canada’s automated-decision regime makes impact assessment mandatory, publishes completed assessments, and requires peer review for higher-impact systems before production. The EU AI Act likewise requires certain public bodies and public-service deployers of high-risk AI to perform a fundamental-rights impact assessment before first use, update it when material elements change, and notify authorities. The archive should therefore prefer one legible deployment dossier over scattered compliance fragments.

## Design rule

Any public automated system that can materially affect a person’s rights, benefits, opportunities, or obligations should have a single **assessment dossier** before live consequential use. That dossier should minimally answer:

- what decision or workflow is being automated or supported,
- what impact level or risk tier the operator assigns,
- which people and groups may be affected,
- what harms are plausible in this context,
- what independent review occurred,
- who signed off and on what date,
- what must be revisited before scope expansion or major change.

## Pattern pack

### 1. Join abstract system risk to contextual rights risk

A model can appear technically acceptable in the abstract while remaining dangerous in its actual public context. The dossier should therefore combine:

- system-level impact scoring,
- workflow-specific rights analysis,
- privacy and data-protection analysis where applicable,
- operational limits and fallback arrangements.

This keeps the archive from mistaking generic assurance for deployment readiness.

### 2. Publish a plain-language dossier before live consequential use

Do not wait for controversy or litigation to reveal the underlying assessment. Publish a public-facing version before the system becomes part of normal operations. It should describe:

- the decision context,
- the role of the system in that process,
- the likely affected populations,
- the main risks identified,
- the mitigations and oversight measures,
- the available review or recourse path.

### 3. Scale independent review with impact level

Peer review should not be optional decoration. Higher-impact systems should face stronger outside scrutiny before production, not only internal reassurance. The review should examine:

- the assessment itself,
- the evidence supporting the claimed mitigations,
- technical and domain assumptions,
- whether the human-oversight story is credible,
- whether the system belongs in production at all.

### 4. Make sign-off nameable and phase-bound

The dossier should record the named responsible authority who approved:

- the initial live use,
- any scope expansion,
- any move from pilot to production,
- any major retraining or redesign that changes the risk profile.

This prevents anonymous institutional assent.

### 5. Treat updates as part of operations, not as embarrassment

Impact and rights assessments should be updated when core elements change, including:

- materially different data,
- materially different population affected,
- materially different use case,
- materially different level of automation,
- materially different legal or operational setting.

A stale dossier is evidence debt.

### 6. Preserve historical versions

The public and future investigators should be able to see what claims were made at the time the system was approved. Keep dated versions instead of silently overwriting them.

### 7. Use the dossier as a promotion gate, not a filing ritual

A dossier should not simply exist. It should block promotion when the evidence is weak, contradictory, or unfinished. “Assessment complete” is not the same as “system justified”.

## Guardrails

- Keep the public version compact and readable, with a fuller internal record behind it.
- Distinguish clearly between system facts, operator claims, and reviewer conclusions.
- Require publication before production or first consequential use, not after.
- Update the dossier when major changes occur.
- Do not hide all meaningful content behind supplier confidentiality claims.

## Failure modes

- **paper fragmentation**: multiple assessments exist, but no one can see the whole justification.
- **peer-review theater**: experts are consulted too late to change the decision.
- **stale approval**: the system changes, but the public record still shows the old rationale.
- **sign-off blur**: responsibility is institutional but no approving role is identifiable.
- **confidentiality overreach**: commercially sensitive details are used to suppress basic public accountability.

## Practical tests

A dossier regime passes when it can answer yes to all of the following:

1. Is there one visible assessment packet for each consequential system?
2. Does it identify the affected populations and likely harms in context?
3. Has independent review occurred before live use when impact is non-trivial?
4. Is the approving authority named and dated?
5. Are historical versions and update triggers preserved?

## Compression rule for the archive

Before a public automated system goes live, ask:

**Where is the single dossier that shows the context, the harms, the reviewers, the signer, and the reason this system was allowed into consequence?**

If no such dossier exists, the governance story is still too fragmented to trust.
