# FT-0181 public outcome kernel

Date: 2026-06-16
Revision: rev0268
Status: pre-evidence public-language and field-decision kernel; not an evidence packet, not a send-now brief, and not a public summary.

## Purpose

This surface answers a narrow operational question before any real owner packet arrives: if the first `AIEDU-SR-003` packet is returned safely, what could count as a small credible outcome, and what still must not be claimed?

The kernel prevents two opposite failures. It blocks overclaiming after a small packet, and it also gives maintainers a positive target so the cube is not only a list of prohibitions.

## Source-truth ladder for the first packet

| Source state | What it can support | What it cannot support |
|---|---|---|
| No owner packet | Only readiness/process statements about the archive's request lane. | Any service, learning, workload, safety, access, compliance, scale, or effectiveness claim. |
| Owner reply blocked | A process statement that the bounded ask prevented unsafe transfer or unclear authority. | A claim that the service worked or that the blocked material was harmful in fact. |
| `RE-ASK-ONCE` | A process statement that one or two minimized meanings need clarification. | A claim that the service is ready for a live window. |
| `PROCEED-STAGED` | A narrow statement that a minimized owner-reviewed packet can enter local staging review. | A public outcome, learning gain, safety finding, access finding, or workload reduction. |
| Accepted workbench plus live-window readout | A bounded process/outcome statement limited to the measured window and claim ceiling. | Generalized effectiveness, scale, compliance, or cross-course claims unless separately evidenced. |

## Small credible outcomes

A first real packet can be useful if it changes a decision in one of these ways:

| Signal | Minimal decision effect | Allowed wording after suitable evidence | Forbidden wording |
|---|---|---|---|
| Safe owner reply | Owner can answer eight rows without raw learner data or protected facts. | The packet supported bounded internal review without requiring raw learner records. | The service is safe, privacy-preserving, or compliant. |
| Authority confirmation | Owner confirms draft-only/no-send/no-write/no-penalty/no-protected-inference. | The reviewed workflow preserved human send authority for this bounded cycle. | AI made or automated the decision safely. |
| Fallback readiness | Owner names fallback route, rollback owner, incident class, and one stop condition. | The reviewed workflow had a named fallback and stop condition. | The service is resilient or incident-safe. |
| Workload signal | Owner supplies method-limited workload signal or says unknown. | Workload evidence was recorded as known/unknown for review. | AI reduced teacher workload. |
| Guidance signal | Owner names guidance owner or says unknown. | Use guidance ownership was recorded for review. | Teachers/students were adequately trained. |
| Claim ceiling | Owner supplies safe language that avoids learning/safety/access/workload/compliance/scale/effectiveness claims. | Public language remained bounded to internal staging/readiness. | The pilot improved learning, safety, access, compliance, or effectiveness. |
| Field trim | One or more requested fields do not affect a decision and are dropped from the next ask. | The next evidence ask was narrowed after review. | The schema is validated by real data. |
| Blocked transfer | Reply is blocked as overbroad/protected/security/authority/evidence. | The bounded process prevented unsafe or unsupported intake. | The block proves the service or owner was unsafe. |

## First public statement templates

Before a real owner packet, even after a send-now brief or sent-clock note exists:

```text
AI-EDU has prepared a bounded owner-review lane for one draft-reminder workflow. No real owner-reviewed packet has been accepted, and no learning, safety, access, workload, compliance, scale, or effectiveness claim is supported.
```

After a safe `PROCEED-STAGED` packet but before acceptance/readout:

```text
A minimized owner-reviewed reply for one draft-reminder workflow has entered local staging review. The reply has not yet been accepted as closure evidence and does not support learning, safety, access, workload, compliance, scale, or effectiveness claims.
```

After an accepted workbench and bounded live-window readout, if it happens:

```text
For the reviewed workflow window only, the evidence supported [specific bounded process finding]. The finding is limited to the named service, owner-reviewed source boundary, date range, and public claim ceiling; it is not a general learning, safety, access, workload, compliance, scale, or effectiveness claim.
```

## Decision rule

When evidence arrives, ask: what did this packet make us stop, narrow, confirm, or refuse?

If the answer is "nothing," do not promote fields or public language. Use the result to trim the next request.

If the answer is "we can continue," preserve the same service boundary, date range class, authority ceiling, owner role, and public claim ceiling until the next reviewed readout.

## Closure boundary

This kernel is not evidence and does not close `FT-0181`. It is a pre-commitment that prevents a small packet from becoming a broad public story.
