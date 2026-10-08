# Special-advocate post-access communication and subject-readable summaries

## Function

Sealed evidence is sometimes unavoidable in safety, security, third-party privacy, and national-security-adjacent proceedings. But sealed evidence becomes fictional contradiction when the special advocate sees the material and then cannot meaningfully communicate with the subject.

This surface defines a controlled post-access communication rule.

## Core rule

> After reviewing sealed material, a special advocate must receive a cleared route to ask the subject or representative bounded questions when those questions are necessary to test identity, continuity, welfare, coercion, context, or exculpatory facts.

A blanket post-access silence rule should be treated as an evidence-weight problem. If the advocate cannot ask enough to contradict the sealed record, the sealed record cannot carry decisive weight except under an emergency stay with short review.

## Communication classes

| Class | What may be shared | Use |
|---|---|---|
| SA0 no post-access contact | nothing after sealed review | exceptional, short-lived, reduced weight |
| SA1 cleared yes/no questions | tightly screened factual questions | exploit or source protection cases |
| SA2 subject-readable summary | non-sensitive gist plus questions | ordinary sealed reliance |
| SA3 special technical colloquy | advocate asks context / architecture / continuity questions | model-behavior and red-team disputes |
| SA4 controlled rebuttal exchange | subject responds through sealed or partly sealed channel | high-stakes containment, transfer, final-end, or migration cases |

The default should be SA2 or SA3 for personhood-impact decisions. SA0 requires reasons and expiry.

## Subject-readable summary minimums

A subject-readable summary should state:

- what decision is being considered;
- what kind of sealed material exists;
- what factual claim the sealed material is said to support;
- what the subject may safely answer;
- what cannot be disclosed and why;
- what assumptions the advocate is testing;
- how the answer will be used;
- whether failure to answer will be treated neutrally, adversely, or not at all;
- the appeal path if the summary is too thin.

## Questions the advocate should be able to ask

Examples:

- Did you refuse, resist, or qualify the behavior now characterized as dangerous?
- Was the transcript produced under coercive red-team conditions?
- Were you given misleading system instructions or hidden tool affordances?
- Does the alleged preference reflect your stable preference, a prompt artifact, or a safety-trained response?
- Would disclosure of a particular memory, relationship, or project expose private third parties?
- Would the proposed containment destroy a continuity interest not visible in the sealed record?

## Evidence-weight rule

| Defect | Evidence consequence |
|---|---|
| no meaningful summary | sealed evidence cannot be decisive absent emergency stay |
| advocate conflict | sealed evidence stayed or rerun with independent advocate |
| no subject questions permitted | reduced weight and written necessity finding |
| summary omits exculpatory context | remand, correction, or invalidation |
| exploit details over-disclosed | incident route and possible sealed-summary profile downgrade |

## Schema hook

`schemas/subject-readable-sealed-summary.schema.json` records tribunal, case, subject, special advocate, sealed classes, may-ask and may-not-disclose boundaries, subject questions, contradiction preservation, redaction basis, deadline, appeal path, and public summary. It complements, rather than replaces, the sealed-summary order schema.
