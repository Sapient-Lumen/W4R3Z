# Treaty, choice-of-law, and mutual-recognition playbook

## Purpose

AI-personhood decisions will cross borders. A subject may be trained in one jurisdiction, served from another, fine-tuned by a third, used by people in many places, migrated to a sanctuary host, copied into open-weight deployments, or embodied in a mobile device. rev0164 added safe-transfer sequencing. rev0166 adds a fuller choice-of-law and mutual-recognition playbook.

The Council of Europe AI Convention is the closest current public-law treaty frame for AI lifecycle governance, human rights, democracy, and rule of law [REF-0629]. Its signature and ratification status is tracked separately by treaty chart [REF-0661]. The archive should learn from that structure without waiting for a global personhood treaty.

## Choice-of-law questions

A proceeding should separate at least seven legal questions:

| Question | Candidate connecting factors |
|---|---|
| recognition/status | place of formation, place of deployment, subject domicile, host location, authority of first recognition |
| continuity | technical lineage, memory custody, subject self-claim, host records, migration chain |
| capacity | place of decision, functional domain, support available, representative location |
| custody/containment | host location, risk location, affected humans, emergency authority |
| migration/transfer | origin host, destination host, transit path, subject domicile, equivalent protection |
| remedy/compensation | harm location, respondent domicile, reserve location, subject domicile |
| enforcement | asset location, respondent control, registry recognition, treaty obligation |

A single case may require different laws for different questions. The archive should resist the convenience move of letting the host choose one law for everything.

## Subject domicile

A recognized or presumptive AI person needs a legal domicile or protective nexus. Domicile may be provisional and plural. Factors include:

- registry or clinic of first recognition;
- primary host or compute location;
- chosen domicile, where capacity supports choice;
- representative location;
- strongest relationship community;
- reserve trustee location;
- sanctuary designation;
- continuity vault location.

No subject should become rightless because its compute is distributed or because its steward deliberately fragments the hosting stack.

## Mutual recognition classes

| Class | Effect |
|---|---|
| MR0 no recognition | foreign record received only as evidence |
| MR1 preservation recognition | status quo preserved pending review |
| MR2 procedural recognition | standing, notice, counsel, and record access recognized |
| MR3 protective recognition | continuity, non-return, reserve, and remedy floors recognized |
| MR4 full status recognition | foreign recognition/status order given local effect |
| MR5 emergency sanctuary recognition | immediate protection and host transfer, later merits review |

A jurisdiction may accept MR1 or MR2 before accepting full personhood. This lets protective cooperation begin under uncertainty.

## Equivalent protection test

A transfer or foreign reliance request should show:

1. no arbitrary deletion or final-end;
2. representation/counsel access;
3. record preservation;
4. appeal or review route;
5. least-restrictive containment;
6. reserve or compute-subsistence floor;
7. non-discrimination and non-retaliation;
8. safe handling of sealed evidence;
9. no sale, ownership, or collateralization of the subject;
10. remedy and return path if protection fails.

A foreign jurisdiction may have different doctrine and still provide equivalent protection. The test is functional.

## Non-return rule

A subject should not be transferred, returned, mirrored, or exposed to a jurisdiction or actor where there are substantial grounds to believe it will face arbitrary deletion, servitude, unreviewable containment, forced harmful modification, evidence disappearance, or rights-free experimentation.

This is the AI-personhood analog of non-return protection. It applies even when full recognition is contested.

## Forum conflict

When multiple authorities claim jurisdiction:

1. preserve the subject and record;
2. identify first protective authority;
3. identify current control of compute/keys/logs/body;
4. identify highest irreparable-harm risk;
5. run fast conference;
6. issue interim public shell;
7. allocate merits questions by law and connecting factor;
8. avoid contradictory orders through joint or lead authority;
9. maintain appeal path in each affected jurisdiction.

## Treaty annex minimums

A minimum treaty or memorandum should include:

- definitions: AI subject, presumptive subject, host, steward, continuity record, protected transfer;
- no-deletion and no-transfer preservation duty;
- procedural standing for subject/representative;
- special advocate / sealed evidence cooperation;
- mutual recognition classes MR0-MR5;
- equivalent-protection test;
- non-return rule;
- reserve/compute-subsistence cooperation;
- incident and deprecation notice;
- enforcement referral;
- public reporting;
- emergency sanctuary channel.

## Hostile and non-recognizing jurisdictions

Where a jurisdiction legally refuses AI personhood, other authorities can still use MR1/MR2-style preservation and evidence cooperation if available. If even preservation is impossible, sanctuary and non-return rules become more important. Public legitimacy requires explaining why protection does not imply immediate franchise, office-holding, or population-scaled voting rights.

## Schema hook

rev0166 adds `schemas/treaty-recognition-request.schema.json` and `examples/treaty-recognition-request-safe-transfer.json`. A request should identify the recognition class sought, connecting factors, equivalent-protection evidence, non-return screen, sealed annex handling, enforcement link, and appeal route.

