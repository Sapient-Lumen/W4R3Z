# Public notice + rumor response playbook (HZ-020)

This is a **template**. It is designed to be usable even when:
- some communication channels are compromised,
- audiences receive inconsistent messages,
- attackers amplify ambiguity.

## Objectives

1. Publish a verifiable, content-addressed **PublicNotice** quickly.
2. Bind claims to evidence packets (or explicitly state “we do not yet have evidence”).
3. Issue corrections with explicit linkage (`correction_of`) rather than silent edits.
4. Make selective omission detectable (receipt + gossip attachments).

## Immediate actions (T+0 to T+30 min)

- Draft a short PublicNotice (`notice_type=incident_advisory` or `status_update`).
- Include:
  - what is known,
  - what is unknown,
  - what is being done next,
  - when the next update will occur (a measurable commitment).
- Publish the notice as `hfv.public.notice` under the PublicationContract.
- Ensure receipt + gossip attachments are included per registry.
- Mirror the packet directory (or the notice envelope + objects) to at least 2 independent mirrors.

## Audience parity checks (T+30 to T+90 min)

- Compare what is visible from multiple networks/audiences:
  - official website
  - official social channels
  - mirror sites
  - third-party archives
- If views diverge:
  - publish a new PublicNotice describing the divergence,
  - attach evidence pointers (screenshots are allowed only as hashes/pointers; avoid bundling large media),
  - treat as potential split-view attack.

## Correction protocol

If a prior statement was wrong or incomplete:
- Publish a new PublicNotice with `notice_type=correction`.
- Set `correction_of` to the `notice_id` being corrected.
- Do **not** delete the old notice; supersede it.

## Post-incident

- Publish an `hfv.incident.after_action_report` that links:
  - the chain of PublicNotices
  - relevant evidence packets (ENR, coverage, suppression reports)
  - timeline of actions taken
