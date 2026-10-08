# 186 — Incident communications as evidence (rumor control without hand-waving)

**Track:** A (Deployable core)

This project treats public communication as an **engineering surface**.

If evidence can be delayed or selectively disclosed, the attacker can win by controlling the
verification ecosystem and the public narrative—even if the tally is correct.

This doc defines a minimal, spec-first approach for publishing public notices as **content-addressed evidence**.

See also: `219-uncertainty-safe-public-updates.md` (epistemic tagging + update commitments for public notices/statement text); `220-publicnotice-graph-resolution-and-effective-state.md` (how boards/monitors resolve supersedes/corrections into “current state”); `218-epistemic-status-tags-and-confidence-rubric.md` (tags + confidence); `195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md` (how to turn notices into a verifiable rumor-control + status-board surface); `200-publicnotice-feeds-and-mirror-index.md` (bounded discovery + rollback detection); `197-precinct-closeout-evidence-capture-and-publication.md` (binding closeout artifacts to PublicNotice digests).

## Grounding (why this is not optional)

Election operators are expected to communicate during incidents and coordinate reporting.
Two practical reference points:

- CISA voluntary incident reporting guidance for the 2024 election cycle (`xref: cisa_voluntary_incident_reporting_guidance_2024_pdf`).
- CISA Election Security "Rumor vs. Reality" landing page (`xref: cisa_rumorcontrol_page`).
- Election Infrastructure Incident Response Communications Guide (EAC/CISA, Oct 2024) (`source: eac_incident_response_comms_guide_pdf`).
- CISA landing page for incident response communications guidance (`xref: cisa_election_ir_comms_guide_page`).
- Public communications guide (EAC/CISA, 2024): `source: eac_enhancing_election_security_public_comms_2024_pdf`.
- Public comms toolkit for pre/post election processes (EAC, 2026): `xref: eac_communicating_election_post_election_toolkit_2026_page`.
- AI-generated content comms tips (EAC, 2023): `source: eac_ai_toolkit_2023_pdf`.

- CISA Binding Operational Directive (BOD) 18-01: Enhance Email and Web Security (`xref: cisa_bod_18_01_page`).
- CISA: Best Practices for Securing Election Systems (`xref: cisa_best_practices_securing_election_systems_page`).
- NIST SP 800-61r3 (incident response recommendations; CSF 2.0 community profile): `source: nist_sp800_61r3_pdf`.

We do not bundle these PDFs; we cite them and extract only minimal snippets where needed.

## The core idea: a PublicNotice is an EvidenceEnvelope

We introduce a new envelope kind:

- `hfv.public.notice` with payload schema `schemas/PublicNotice.json`

Example packet:
- `artifacts/examples/evidence_packet_public_notice/` (minimal, offline-verifier-friendly)

A PublicNotice is:
- signed/bound via `EvidenceEnvelope` digest rules,
- published under the `PublicationContract` (time-bounded), and
- receipted + gossiped (anti selective disclosure), per registry.

### What a PublicNotice is *for*

- status updates that can be mirrored without distortion
- incident advisories that link to evidence packets
- corrections / retractions (with explicit `correction_of_notice_id` linkage)
  - Template: `artifacts/templates/public-notice-correction-payload.json` (draft a correction as a new notice; do not silently edit).

- “what we know / what we don't know” statements that survive later disputes

### AI-era note (synthetic media / forged statements)

Assume adversaries can mass-produce convincing fake screenshots and “official” statements.
Make authenticity **cheap to check**:
- every public channel (web, press release, social) should include the PublicNotice digest (short form) and a pointer to mirrors (and optionally the latest PublicNotice feed digest; docs/200),
- verifiers should accept a notice only if its digest matches the published envelope and its receipts/gossip attachments.

Operational note: treat comms channel security as part of the verification surface; use the hardening checklist:
- `artifacts/checklists/official-communications-channels-hardening-checklist.md`

See also: `194-synthetic-media-and-comms-authenticity-minimum-controls.md` (minimum deployable controls for AI-era forgeries).

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

Starter payload templates (valid JSON; replace fields):
- `artifacts/templates/public-notice-payload.json`
- `artifacts/templates/public-notice-status-update-payload.json` (follow-up updates; uses `supersedes_notice_id`)

Channel IDs: `channels` SHOULD use `channel_id` values from `artifacts/registries/official-channels.csv` so monitors and observers have a canonical list of comms surfaces for parity checks.

**Channel identity (keys):** jurisdictions SHOULD publish a pre-committed allow-list of keys authorized to sign PublicNotices:
- `hfv.public.notice_signing_keyset` (docs/208)

This turns “which key is official?” into a verifiable surface that can be mirrored and checked under attack.

If a parity failure is detected (different audiences receiving different statements), publish a bounded `hfv.public.surface_parity_snapshot` (docs/201) and cite its digest in a follow-up PublicNotice so the split-view evidence is portable.

Measurable commitments: when possible, set `next_update_at` (RFC3339) so monitors can automatically check update promises.

Optional helper (prints a human-friendly digest card for comms surfaces):
- `python tools/public_notice_card.py --packet <packet_dir>`
- `python tools/public_notice_card.py --envelope <path/to/envelope.json>`

Note: older notices MAY use `correction_of` as a legacy alias; prefer `correction_of_notice_id` for new notices.

Over time, Track C can incorporate stronger attestation of “who authored what, from what workstation”,
but Track A must work without assuming perfect endpoints.


## Deadlines and coverage for public notice

To make 'they never told us' measurable, Track A now supports a contract rule for `hfv.public.notice` triggered by `incident_declared` (registry: docs/184). Use `hfv.publication.trigger_event` as the portable anchor and compute compliance via docs/187.

PublicNotice payload schema now includes optional linkage fields (`correction_of_notice_id`, `supersedes_notice_id`, `related_trigger_event_id`) and additional notice types (`incident_declaration`, `rumor_control`) so corrections and rumor-control statements can be mirrored without ambiguity.

## 186.6 Minimal rumor-control packet (template)

Goal: enable **independent reproduction** of the key checks *quickly*, without overclaiming.

Publish (as a bundle, and as one or more `PublicNotice` envelopes that point into it):

Drafting helper:
- Rumor-control notice template: `artifacts/templates/public-notice-rumor-control-payload.json` (use `notice_type=rumor_control`; bind claims to packet digests).

1. **Statement of scope** (facts only): what this notice is about and what it is *not* about.
2. **Anchors** (stable, copyable identifiers):
   - `election_id`
   - EPB digest (or EPB pointer)
   - latest quorum checkpoint ID + digest
   - bundle manifest digest (if publishing a packet)
3. **Reproducibility hooks**:
   - the exact verifier command line / tool version (or `VerifierProvenance` pointer)
   - expected output digests (content-addressed), not screenshots
4. **Disclosure boundaries**:
   - what voter-specific data is intentionally not disclosed
   - the next planned update time

Non-goals:
- “Winning the narrative” in a single post.
- Proving more than the available evidence can support.

Cross-links:
- Disinformation resilience requirements: `37-public-evidence-and-disinformation-resilience.md`
- Adversary playbooks: `27-adversary-playbooks-and-detection-signals.md`
- Offline bundle contract: `92-offline-verifier-bundle-spec.md`