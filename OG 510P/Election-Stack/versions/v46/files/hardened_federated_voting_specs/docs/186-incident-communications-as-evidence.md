# 186 — Incident communications as evidence (rumor control without hand-waving)

**Track:** A (Deployable core)

This project treats public communication as an **engineering surface**.

If evidence can be delayed or selectively disclosed, the attacker can win by controlling the
verification ecosystem and the public narrative—even if the tally is correct.

This doc defines a minimal, spec-first approach for publishing public notices as **content-addressed evidence**.

## Grounding (why this is not optional)

Election operators are expected to communicate during incidents and coordinate reporting.
Two practical reference points:

- CISA voluntary incident reporting guidance for the 2024 election cycle:
  https://www.cisa.gov/resources-tools/resources/2024-general-election-cycle-voluntary-incident-reporting-guidance-election-infrastructure
- Election Infrastructure Incident Response Communications Guide (EAC/CISA, Oct 2024):
  https://www.eac.gov/sites/default/files/2024-10/Election_Infrastructure_Incident_Response_Comms_Guide_508.pdf

We do not bundle these PDFs; we cite them and extract only minimal snippets where needed.

## The core idea: a PublicNotice is an EvidenceEnvelope

We introduce a new envelope kind:

- `hfv.public.notice` with payload schema `schemas/PublicNotice.json`

A PublicNotice is:
- signed/bound via `EvidenceEnvelope` digest rules,
- published under the `PublicationContract` (time-bounded), and
- receipted + gossiped (anti selective disclosure), per registry.

### What a PublicNotice is *for*

- status updates that can be mirrored without distortion
- incident advisories that link to evidence packets
- corrections / retractions (with explicit `correction_of` linkage)
- “what we know / what we don't know” statements that survive later disputes

### What a PublicNotice is *not*

- propaganda
- claims without references when references exist
- vague reassurances without measurable commitments

## Publication requirements (A2 posture)

A Track A deployment SHOULD:
1. publish notices as content-addressed envelopes,
2. include (at minimum) receipt + gossip attachments,
3. reference any relevant evidence packet objects by digest (or packet path),
4. avoid overclaiming when facts are uncertain.

## Failure mode we explicitly harden

**Split-view comms:** some audiences see “all good”, others see “something's wrong”.

By requiring receipt + gossip attachments for public notices, we make *absence* and *selective omission*
detectable by third parties.

See also:
- `docs/180` receipts + gossip attachments
- `docs/181` publication contract + breach proofs
- `docs/174` coverage accounting (measuring representativeness, not vibes)

## Minimal payload fields

See `schemas/PublicNotice.json`. The schema is intentionally small:
- stable IDs
- time
- type
- short message
- references/pointers to evidence packets when applicable

Over time, Track C can incorporate stronger attestation of “who authored what, from what workstation”,
but Track A must work without assuming perfect endpoints.


## Deadlines and coverage for public notice (v46)

To make 'they never told us' measurable, Track A now supports a contract rule for `hfv.public.notice` triggered by `incident_declared` (registry: docs/184). Use `hfv.publication.trigger_event` as the portable anchor and compute compliance via docs/187.

PublicNotice payload schema now includes optional linkage fields (`correction_of_notice_id`, `supersedes_notice_id`, `related_trigger_event_id`) and additional notice types (`incident_declaration`, `rumor_control`) so corrections and rumor-control statements can be mirrored without ambiguity.
