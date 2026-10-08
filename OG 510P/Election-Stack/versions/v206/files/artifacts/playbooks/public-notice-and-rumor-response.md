# Public notice + rumor response playbook (HZ-020)

This is a **template**. It is designed to be usable even when:
- some communication channels are compromised,
- audiences receive inconsistent messages,
- attackers amplify ambiguity.

## Objectives

1. Publish a verifiable, content-addressed **PublicNotice** quickly.
2. Bind claims to evidence packets (or explicitly state “we do not yet have evidence”).
3. Issue corrections with explicit linkage (`correction_of_notice_id`) rather than silent edits.
4. Make selective omission detectable (receipt + gossip attachments).

## Immediate actions (T+0 to T+30 min)

- Draft a short PublicNotice (`notice_type=incident_advisory` or `status_update`).
- Start from `artifacts/templates/public-notice-payload.json`.
- For follow-up updates, start from `artifacts/templates/public-notice-status-update-payload.json` (sets `notice_type=status_update` and uses `supersedes_notice_id`).
- For rumor-control statements, start from `artifacts/templates/public-notice-rumor-control-payload.json` (sets `notice_type=rumor_control`).
- Set `payload.channels` to canonical channel IDs from `artifacts/registries/official-channels.csv` (or add placeholders there during a drill).
- When applicable, set `next_update_at` as a measurable commitment for the next public update (monitors can check this field automatically).
- Include:
  - what is known,
  - what is unknown,
  - what is being done next,
  - when the next update will occur (a measurable commitment).
- Publish the notice as `hfv.public.notice` under the PublicationContract.
- If keys are in question (impersonation/compromise), publish or update the PublicNotice signing keyset (`hfv.public.notice_signing_keyset`, docs/208) and include its digest on the status board.
- Ensure receipt + gossip attachments are included per registry.
- Mirror the packet directory (or the notice envelope + objects) to at least 2 independent mirrors.
- For comms surfaces (status page, social), publish the notice digest short form:
  - `python tools/public_notice_card.py --packet <packet_dir>`

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
- Set `correction_of_notice_id` to the `notice_id` being corrected.
- (Legacy alias: `correction_of` MAY appear in older notices; treat as equivalent.)
- Do **not** delete the old notice; supersede it.

## Post-incident

- Publish an `hfv.incident.after_action_report` that links:
  - the chain of PublicNotices
  - relevant evidence packets (ENR, coverage, suppression reports)
  - timeline of actions taken

## Stale pointer / cache split-views (freshness disputes)

If audiences report “the official pointers changed” but some networks still see old discovery/feeds:

- Execute `artifacts/checklists/public-surface-cache-and-freshness-test-plan.md` (headers + conditional revalidation).
- Have ≥2 independent watchers publish receipted+gossiped `hfv.coverage.liveness_beacon` entries (`docs/210`) that record:
  - reachability results for `/.well-known/…`, directory, feed, keyset
  - observed `payload_sha256` and cache headers (`ETag`, `Cache-Control`, `Age`, `Last-Modified`)
- If you need a bounded, publishable summary for comms, render a beacon digest card with `tools/liveness_beacon_card.py` (do not paste raw bodies).
- If official channels diverge, publish a `hfv.public.surface_parity_snapshot` (`docs/201`) for the affected `surface_kind`.
- Publish a PublicNotice that cites the relevant beacon + parity snapshot digests and states the recovery plan (purge/rotation + next update time).
