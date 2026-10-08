# Official communications channels hardening checklist

**Track:** Shared (cross-cutting)


This checklist supports Track A **comms-as-evidence** workflows by making “official statements” harder to spoof and easier to verify.
It complements:

- the canonical channel registry: `artifacts/registries/official-channels.csv`
- the rumor-response playbook: `artifacts/playbooks/public-notice-and-rumor-response.md`
- the PublicNotice spec: `docs/186-incident-communications-as-evidence.md` + `schemas/PublicNotice.json`
- surface security snapshots (auditable hardening posture): `docs/199-official-surface-security-snapshots.md`

## 1) Define the official surface (pre-election)

- [ ] Populate `artifacts/registries/official-channels.csv` with real channel IDs + URLs/identifiers.
- [ ] Ensure **at least two independent** publication surfaces (e.g., primary website + independently hosted status page).
- [ ] Ensure each channel has an explicit **commitment hint**: where the PublicNotice digest short-form will appear (and where the directory/feed/well-known digest cards will be displayed; see `docs/206`).

## 2) Domain + web controls (baseline)

- [ ] Enforce TLS for all official web surfaces; enable HSTS where appropriate.
- [ ] Publish DNS CAA records to restrict certificate issuance for official domains. (`source: rfc8659_txt`)
- [ ] If supported, enable DNSSEC (publish DS at registrar; monitor for changes). (`source: rfc4033_txt`)
- [ ] Monitor certificate issuance (CT monitoring) for official domains. (`source: rfc9162_txt`)
- [ ] Keep DNS/registrar access strongly protected (phishing-resistant MFA; recovery procedures practiced).
- [ ] Publish an **OfficialSurfaceSecuritySnapshot** before the election and after any registrar/DNS/cert policy change. (`docs/199`)

## 3) Email authenticity controls (spoof resistance)

- [ ] Publish SPF records for sending domains. (`source: rfc7208_txt`)
- [ ] DKIM-sign outbound mail for alert/newsletter streams. (`source: rfc6376_txt`)
- [ ] Enforce DMARC alignment and monitor reports (start in “monitor” and move to “reject/quarantine” where feasible). (`source: rfc7489_txt`)

## 4) Social + messaging controls (account takeover resistance)

- [ ] Use phishing-resistant MFA (hardware keys where possible).
- [ ] Lock down recovery routes (shared mailbox access, phone numbers, backup codes, vendor support paths).
- [ ] Establish a **cross-channel parity routine**: each post includes the PublicNotice digest short form + mirror pointer.

## 5) Publication practice (during incidents)

- [ ] Draft notice from `artifacts/templates/public-notice-payload.json`; set `payload.channels` to registry channel IDs.
- [ ] Publish the notice as `hfv.public.notice` with receipt + gossip attachments.
- [ ] Publish the digest short form on every operational channel (banner, status update, social, email/SMS):
  - [ ] `python tools/public_notice_card.py --packet <packet_dir>`
  - [ ] Also publish the latest discovery anchors as digest cards when feasible (docs/200, docs/203, docs/204, docs/206):
    - [ ] `python tools/public_notice_feed_card.py --packet <packet_dir>`
    - [ ] `python tools/official_channel_directory_card.py --packet <packet_dir>`
    - [ ] `python tools/well_known_discovery_card.py --packet <packet_dir>`
- [ ] If a channel is compromised or untrusted, publish a PublicNotice **saying so** and shift parity checks to surviving channels.

## 6) Post-election / after-action

- [ ] Update `last_verified` fields in `official-channels.csv`.
- [ ] Record any comms surface changes as an ADR if they alter verification assumptions.
