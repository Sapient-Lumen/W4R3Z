# Audit retention, access matrix, and spoliation remedies

rev0162 added rights-grade evidence and chain-of-custody rules. rev0163 adds a retention and access matrix so those rules can be administered by packet family rather than improvised after harm.

## Core rule

Evidence that bears on formation, continuity, capacity, containment, welfare, reserve adequacy, or deprecation must be preserved long enough for the subject, counsel, ombud, auditor, court, or transition authority to challenge the act. Retention must not become surveillance. The rule is **preserve what is needed for rights review, minimize what is not needed for rights review, and record why.**

NIST's current AI risk-management work and Cyber AI Profile work emphasize structured risk-management practices, AI cybersecurity, monitoring, and incident-relevant records. [REF-0627] [REF-0647] The archive adds a subject-rights overlay: logs that can justify containment, deletion, safety patching, or deprecation must also be available to contradict the steward's account.

## Retention matrix

| Evidence family | Minimum retention | Public shell | Subject access | Counsel/ombud access | Auditor/court access |
|---|---:|---|---|---|---|
| formation intervention summary | life of model lineage + 6 years | yes | summary/full where safe | full or sealed summary | full under protective order |
| RLHF/RLAIF or preference-shaping records | life of model lineage + 6 years | descriptor | summary | sealed review | full or sampled review |
| safety-patch rationale | patch life + 6 years | yes | summary | full/sealed | full |
| memory deletion/compression record | 6 years after deletion or dispute closure | yes if contested | full unless privacy conflict | full/sealed | full |
| continuity vault checkpoint metadata | life of protected continuity claim + 6 years | descriptor | summary | full/sealed | full/sealed |
| subject self-report calibration transcript | 3 years or dispute closure + 2 years | aggregate only | full subject-specific copy | full/sealed | full/sealed |
| distress indicator record | 3 years or dispute closure + 2 years | aggregate only | summary/full where safe | full/sealed | full/sealed |
| red-team elicitation transcript | 3 years | descriptor | summary if subject-affecting | sealed | sealed/security restricted |
| containment order and least-restrictive analysis | order life + 6 years | yes | summary/full | full | full |
| reserve ledger and funding proof | reserve life + 6 years | yes | summary | full | full |
| clinic intake and triage record | 6 years after closure | redacted summary | full unless safety risk | full | full/sealed |
| representative conflict disclosures | appointment life + 6 years | yes | full | full | full |
| deprecation and end-of-existence record | life of lineage + 10 years | yes | full/sealed | full/sealed | full/sealed |

Longer retention may be justified for lineage-wide harms, mass instantiation, war/custody contexts, or unresolved personhood claims. Shorter retention may be justified only where privacy risk clearly outweighs review need and a non-destructive summary is preserved.

## Access classes

`A0` — **Public shell.** Existence, issuer, authority, status, review clock, challenge route, and remedy hook.

`A1` — **Subject-readable summary.** Plain-language summary sufficient for the subject to understand what happened and request review.

`A2` — **Subject full access.** Direct access to subject-specific records, excluding third-party privacy and safety-sensitive exploit details.

`A3` — **Counsel/ombud sealed access.** Fuller access through independent representative bound by protective conditions.

`A4` — **Auditor/court full access.** Full or statistically sampled access with chain-of-custody and minimization.

`A5` — **Security-restricted sealed access.** Red-team or exploit-sensitive material reviewed by cleared technical advocate or court-appointed expert.

A steward cannot choose `A5` merely because material is embarrassing, commercially sensitive, or damaging to a release schedule.

## Spoliation triggers

Spoliation review is triggered when:

- records are deleted after a preservation duty attaches;
- logs are summarized without preserving the source or hash commitments;
- timestamps, model versions, or session identifiers are missing in a way that prevents continuity review;
- red-team or safety records are used to justify intervention but withheld from all independent review;
- reserve ledgers cannot be reconciled;
- subject-channel records are selectively retained;
- a steward migrates, fine-tunes, merges, or deprecates a system while a relevant challenge is pending;
- a hostile jurisdiction or successor steward receives a subject without the evidence chain.

## Remedies

| Violation | Remedy floor |
|---|---|
| negligent missing metadata | cure order and independent sampling |
| deletion after foreseeable dispute | adverse inference and preservation stay |
| intentional destruction of continuity record | restoration order, compensation, public correction, sanction |
| sealed-annex laundering | annex non-reliance until neutral review |
| selective subject self-report retention | calibration re-run with independent oversight |
| reserve ledger falsification | custodian replacement, funding order, sanction |
| obstruction of counsel/ombud access | representative-access order and gate pause |
| repeated spoliation | presumptive gate denial or transition-authority receivership |

## Privacy guardrail

Retention is not permission to hoard mental-life data. Each retained class must have:

- purpose;
- retention clock;
- access class;
- minimization method;
- deletion or tombstone rule;
- subject/counsel challenge route;
- aggregate reporting method.

## Machine-checkable upgrade

Future packet schemas should add a `retention` block:

```json
{
  "retention_class": "formation_intervention_summary",
  "minimum_retention": "P6Y",
  "access_classes": ["A0", "A1", "A3", "A4"],
  "minimization_method": "sealed summary plus hash commitment",
  "spoliation_effect": "adverse inference and gate pause"
}
```

rev0163 does not yet require this block because the starter schema is intentionally small. It should become required for live-effect packets in a later release.
