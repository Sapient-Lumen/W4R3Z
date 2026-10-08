# Precinct closeout evidence capture checklist

**Track:** Shared (cross-cutting)


**Use:** Track A deployments (poll tape + seals + closeout note micro-packets)

See: `docs/197-precinct-closeout-evidence-capture-and-publication.md` (canonical pattern) + `docs/198-precinct-closeout-index-and-omission-detection.md` (index)

## Before polls close (prep)
- [ ] Reporting unit identifiers are fixed and published (precinct / tabulation center IDs).
- [ ] Capture devices are configured (time sync best-effort; storage available).
- [ ] Upload path(s) and mirror targets are tested (including during degraded network).
- [ ] Staff know the “fail loudly” rule: missing artifacts trigger a PublicNotice gap note.

## At closeout (capture)
- [ ] Poll / results tape photo(s) captured (readable; multiple angles if needed).
- [ ] Seal/container photo(s) captured (if applicable; include seal numbers).
- [ ] Short closeout note written (unit id, time window, anomalies).

## Package
- [ ] Media bytes stored as content-addressed objects (`sha256-<hex>.*`).
- [ ] Envelopes emitted binding each artifact (payload_digest + pointers).
- [ ] `manifest.json` created (`EvidenceBundleManifest`) and signed per local policy.

## Publish
- [ ] Packet published at primary public URL.
- [ ] Packet mirrored to at least one independent host.
- [ ] PublicNotice issued referencing the packet manifest digest (`sha256:<hex>`) + mirror URLs.
- [ ] PublicNotice digest mirrored across official channels (site, status board, social, press list).
- [ ] Parity monitoring enabled for the digest across channels (see `docs/195`).
- [ ] (Recommended) Closeout index updated/published so omissions are measurable (see `docs/198`).

## After publish (spot checks)
- [ ] Confirm mirrors serve identical manifest/object bytes.
- [ ] Confirm PublicNotice digest resolves to the expected payload.
- [ ] If any late correction occurs, publish a new PublicNotice (no silent edits).
