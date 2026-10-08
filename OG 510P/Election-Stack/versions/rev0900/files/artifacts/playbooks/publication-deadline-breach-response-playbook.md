# Publication deadline breach response playbook

**Track:** Shared (cross-cutting)


**Trigger:** A `PublicationContract` deadline is missed, or audiences disagree on whether required evidence exists.

## Goals
1. Make the breach **provable and portable**
2. Prevent selective disclosure (some audiences see “all good”, others see “missing”)
3. Produce court-usable artifacts without inflaming confusion

## Steps (watcher/monitor)
1. **Re-run offline packet verification** on any received packet:
   - `python tools/observer_verify_packet.py <packet_dir>`
2. **Check the contract rule** for the missing kind:
   - Identify `kind`, `trigger`, and `max_delay_seconds`.
3. **Collect probe records** (keep them minimal but reproducible):
   - timestamps, mirror endpoints, log query parameters, response hashes.
4. **Issue a PublicationSuppressionReport** envelope:
   - kind: `hfv.publication.suppression_report`
   - include probe summary + references
5. **Publish the suppression report** with required attachments:
   - transparency receipt (submit/ inclusion proof)
   - gossip summary (digests for cross-audience comparison)
6. **Gossip the digest set** across transports (see `docs/100–102`).
7. **Escalate** using the incident communication policy (see `docs/08`, `docs/171`):
   - keep language precise: “missing evidence by contract deadline” not “fraud”
8. **Recovery**:
   - if evidence later appears, issue an updated envelope that references both the late evidence and the suppression report.

## Steps (election authority / publisher)
1. Confirm whether the evidence was never generated, generated but not published, or published to a subset.
2. If generated but delayed: publish immediately + attach receipts and a corrective note.
3. If never generated: publish a signed explanation envelope + create an AAR.

## Pitfalls
- Do not claim cryptographic “non-existence proofs” unless your log supports them.
- Avoid ambiguous clock language; always use RFC3339 timestamps.

## Required references
- `docs/181-publication-contract-and-deadline-breach-proofs.md`
- `docs/145-mmd-style-deadlines-for-evidence-publication.md`
- `docs/180-receipts-and-gossip-attachments.md`
