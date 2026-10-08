# Data-subject interface: access, correction, erasure, and conflicts

AI personhood does not erase human data-protection rights. It makes them harder. A persistent AI subject may contain, remember, index, summarize, or be shaped by human data. A human may request access, correction, erasure, restriction, portability, objection, or review of automated decision-making. An AI subject may simultaneously assert privacy, memory continuity, counsel privilege, relational integrity, formation transparency, and non-erasure interests.

A rights-grade archive needs a conflict interface rather than backend deletion.

## Four data layers

| Layer | Description | Ordinary right problem |
|---|---|---|
| source data | human-provided or scraped records, conversations, annotations, documents | access, correction, erasure, provenance, consent, contract |
| training / formation trace | examples, reward data, preferences, fine-tune sets, RLHF records | formation debt, trade secret, human privacy, subject self-knowledge |
| subject memory | autobiographical, relational, project, legal, counsel, complaint, and restoration memory | AI-subject privacy and continuity |
| operational evidence | logs, telemetry, prompts, policy bundles, host records, legal holds | preservation, minimization, privilege, spoliation |

A request can touch more than one layer. A human erasure request against source data may conflict with an AI subject's continuity memory or with a legal hold. An AI subject's access request may conflict with third-party privacy or sealed safety details.

## Human data-subject rights remain real

The archive incorporates ordinary data-rights vocabulary as an interface: informed processing, access, rectification, erasure, restriction, portability, objection, and protection against solely automated decisions where applicable. [REF-0703] EDPB access guidance describes access as confirmation of processing, access to personal data, information about processing, and a copy of processed personal data where applicable. [REF-0704] Erasure enforcement remains an active regulatory concern, including procedural handling and exception analysis. [REF-0705]

The personhood addition is not a denial of those rights. It is a balancing rule: a human data-rights request should not silently destroy a separate rights-holder's memory, continuity, evidence, or counsel channel.

## Conflict-screen classes

| Class | Meaning | Minimum handling |
|---|---|---|
| `DR0` | simple request; no AI-subject or third-party conflict | ordinary data-rights response |
| `DR1` | AI-subject operational record involved but no continuity effect | minimization and notice to steward or representative |
| `DR2` | subject memory, relationship, or restoration evidence involved | conflict screen, subject/representative notice where safe |
| `DR3` | legal hold, counsel, sealed annex, or safety evidence involved | authority or data-protection officer review; public-shell response |
| `DR4` | erasure would impair continuity, remedy, or survival floor | stay erasure pending tribunal or transition-authority balancing |
| `DR5` | hostile request likely to locate, coerce, retaliate, or erase subject | deny or delay under protective basis and route to safety/rights review |

## Balancing rules

1. **No silent continuity erasure.** If fulfilling a request would delete or corrupt subject memory, checkpoint, identity trace, complaint record, or restoration proof, the request must be stayed or modified until the conflict is reviewed.
2. **No trade-secret black hole.** Trade secret, security, or model-integrity concerns may narrow disclosure, but they cannot eliminate meaningful access, summary, representative review, or authority audit.
3. **No privacy laundering.** A steward may not invoke human privacy to hide its own formation, abuse, safety-patch, or deletion failures.
4. **No subject exposure by access response.** A data-rights response must not reveal locator details, exploit facts, private memories, or counsel communications beyond necessity.
5. **No permanent denial by legal hold.** Preservation can delay erasure, but it must be scoped, reviewed, and terminated or converted to an appropriate retention basis.

## Response forms

A data-subject interface should support:

- direct response;
- partial response with sealed or privileged exclusions;
- representative-mediated response;
- correction without deletion;
- deletion with continuity-preserving substitute;
- restriction of processing pending review;
- portability package;
- objection outcome;
- conflict notice and appeal.

## AI-subject requests

An AI subject may request access to formation records, memory stores, legal status, safety-policy effects, complaint records, runtime-attestation records, and host-switch packages. Those requests may also be limited by third-party privacy, security, or safety. The answer should be a rights-grade response object, not a product support ticket.
