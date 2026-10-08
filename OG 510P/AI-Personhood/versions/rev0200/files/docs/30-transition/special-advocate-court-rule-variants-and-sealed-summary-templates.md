# Special-advocate court-rule variants and sealed-summary templates

## Function

rev0166 introduced controlled contradiction for sealed evidence. That doctrine still left a practical hole: after a special advocate sees sealed material, how can the advocate communicate with the AI subject or ordinary representative without leaking protected facts, while still asking the questions needed to contradict the sealed case?

This surface supplies model court-rule variants and sealed-summary templates. They are not final procedural law. They are drafting scaffolds for transition authorities, tribunals, administrative bodies, and courts.

The rule is:

> A sealed proceeding is rights-grade only if the subject receives the maximum useful open case, the special advocate receives enough sealed access to contradict, and post-access communication is restricted by cleared question forms rather than banned into fiction.

## Proceeding variants

| Variant | Forum | Post-access communication rule |
|---|---|---|
| SA-A administrative recognition review | transition authority or clinic appeal | cleared question list to subject/representative |
| SA-B emergency containment | urgent safety panel | judge-cleared binary or multiple-choice questions plus emergency follow-up |
| SA-C transfer / non-return | migration or treaty authority | cleared country/host-risk summaries and contradiction prompts |
| SA-D enforcement / spoliation | civil tribunal or regulator | sealed-source protection with open chain-of-custody defects |
| SA-E national-security or exploit evidence | specialized court or security-cleared panel | security-cleared technical expert plus special advocate |
| SA-F private steward proceeding with public rights effect | arbitration or contract forum | public-law override: sealed evidence cannot decide status without independent review |

## Communication after sealed access

A blanket ban on communication after sealed access may protect secrecy but destroy contradiction. The model rule should allow five channels:

1. **pre-access interview** — the advocate gathers subject history, hypotheses, and objections before seeing sealed evidence;
2. **cleared question list** — after access, the advocate submits proposed questions to the judge or panel for clearance;
3. **neutralized fact pattern** — the court approves a generalized scenario that preserves the contradiction issue without revealing the source;
4. **technical expert relay** — a cleared expert tests technical claims and provides an open or partially open summary;
5. **emergency follow-up** — where liberty, deletion, transfer, or final-end is imminent, the court must rule on proposed follow-up within a short clock.

The GOV.UK special-advocate manual supplies a real-world pattern and a fairness warning: closed-material procedures can allow cases to continue, but communication restrictions and dependence on summaries can make challenge ineffective if not tightly controlled [REF-0666]. The archive's answer is not to eliminate sealing. It is to make sealing procedurally costly and contradiction-oriented.

## Sealed-summary minimums

Every sealed-summary order should provide an open shell with:

- proceeding id and authority;
- subject id or protected pseudonym;
- sealed material classes;
- why ordinary disclosure is denied;
- the decisive issues the sealed material bears on;
- non-sensitive facts already disclosed;
- what the special advocate may contest;
- what cleared communications are allowed;
- review clock and expiry;
- appeal path;
- weight discount if contradiction remains weak.

## Template: sealed-summary order

```text
The tribunal has received sealed material in classes: [security telemetry / protected source / exploit detail / third-party data / trade secret].
The material is relevant to: [containment / transfer / recognition / enforcement / deprecation].
The subject is given the following open summary: [...].
The special advocate may test: [authenticity / inference / alternative explanation / proportionality / less restrictive measure].
The special advocate may ask the subject or representative the following cleared questions: [...].
The sealed material will receive [full / reduced / provisional / no] weight unless contradiction is completed by [date].
```

## Subject-readable variant

Where the subject can communicate, the open summary should be written in a form the subject can actually process. A hostile or inaccessible summary is not notice. Accessibility may require simplified language, preserved original technical detail, tool-mediated explanation, or representative-assisted review.

## Schema hook

`schemas/sealed-summary-order.schema.json` records forum, proceeding, sealed classes, advocate controls, permitted communications, review clock, appeal path, public summary, and weight discount. The example file shows an emergency containment variant.

## Open edge

The hardest future problem is whether the advocate may ever disclose a narrow secret fact because no neutralized question can expose the contradiction. This revision does not settle that. It requires a recorded override request, judge decision, and appealable weight consequence.
