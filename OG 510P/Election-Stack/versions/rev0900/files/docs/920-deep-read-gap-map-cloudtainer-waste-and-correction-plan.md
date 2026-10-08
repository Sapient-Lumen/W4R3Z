# 920 — Deep-read gap map, cloudtainer waste, and correction plan

**Track:** Shared / session audit / release governance

## Purpose

This `v882` note records a deep read of the `v881` datacube and the corrections that should be made without weakening the archive boundary. It is a session-audit and maintenance map, not a live release claim.

Boundary: this document is synthetic-release governance only. It is not current voter instruction, legal advice, certification, production signer authority, source-byte cache completeness, independent validation, or live-pilot authorization.

## What is missing

1. **Source-byte cache completion.** The receipt lane is well shaped but incomplete. The current status report shows `118` pinned sources, `13` valid/present receipts, `105` missing receipts, `6` source-byte handoff batches, and batch `01` as the first incomplete operator batch. This revision must not invent receipts; it should keep the no-network external-cache path and accept only exact SHA-256 matches.
2. **Adopter authority capture for quarantined state/local source examples.** The public-surface firewall correctly keeps quarantined state/local xrefs out of current-voter-instruction posture, but the remaining work is human/organizational: capture authority records before promotion.
3. **Live-pilot evidence lanes.** Local-pilot intake, redaction/publication review, accessibility/language review, evidence custody/provenance, independent review/conflict checks, production publication governance, and certification evidence remain no-go lanes.
4. **Standards/current-source drift candidates.** New or moving references should be locked before they become evidence-facing claims: EAC VVSG migration/current certification lifecycle notes, EAC NOC 26-01 end-of-life certification review policy, NIST VTS 200-1, current SCITT drafts/RFC queue state, SLSA v1.2 provenance/source-track references, and OONI data/risk guidance.
5. **Numbered-doc range explanation.** The numbered docs currently jump across a broad `713-838` range. That may be intentional compaction, but the archive should add a range-level tombstone or compaction map so reviewers do not infer silent deletion.

## What should change

- Treat `artifacts/reports/source-byte-cache-batch-status-rev0882.json` as the source-byte operator dashboard, and keep batch files stale-proofed so a source with a receipt cannot remain in a receipt-missing batch.
- Add lockfile rows for new online-research candidates before citing them in public or evidence-facing docs.
- Keep the release posture blunt: `GO_SYNTHETIC_RELEASE_ONLY` is the right topline until live evidence lanes are filled.
- Add a doc-range compaction explanation before adding many more numbered docs.
- Prefer one session-level findings report over another cluster of small reports when the finding is cross-cutting.
- Keep generated navigation zero-padding revision numbers; `v882` must point at `rev0882` artifacts, not an impossible `rev882` family.

## What has gone wrong or wasteful

- The canonical ZIP size looks wasteful because members are stored rather than deflated. That is not accidental: the release builder and verifier intentionally use `ZIP_STORED` to avoid compressor-runtime drift and to support byte-for-byte canonical rebuild checks. Do not silently switch the canonical release ZIP to DEFLATE.
- A noncanonical deflate estimate was much smaller than the stored carrier, so a compressed sidecar distribution artifact may be worthwhile. It needs an explicit policy and verifier before it replaces any canonical artifact.
- Exact duplicate files exist, but estimated exact-duplicate savings are small compared with the doc/report surface. This revision compacted stale non-current source-byte and trust-policy history into digest-preserving summaries; the better long-term cleanup remains router/index consolidation for sprawling docs and governed compaction for stale report families.
- The source-byte DNS blocker is environmental. It should steer the workflow toward external cache handoff, not toward fake receipts, bundled third-party bytes, or network retry churn inside this cloudtainer.

## Correction order

1. Run the first source-byte cache batch externally and import only exact `operator_cache_file` matches.
2. Lock new EAC/NIST/SCITT/SLSA/OONI candidate sources before evidence-facing references depend on them.
3. Add a `713-838` range tombstone/compaction map or equivalent explanation.
4. Design a deterministic compressed sidecar carrier while preserving the canonical stored ZIP release verifier.
5. Continue stale generated-report compaction only when original digests and current no-go evidence remain intact.

## Machine-readable companion

- `artifacts/reports/deep-review-gap-map-rev0882.json`
- `artifacts/reports/rev0882-deep-read-history-compaction.json`

## Related gates and reports

- `artifacts/reports/source-byte-cache-batch-status-rev0882.json`
- `artifacts/reports/source-byte-cache-batch-manifests-rev0882.json`
- `artifacts/reports/source-byte-cache-intake-manifest-rev0882.json`
- `artifacts/reports/current-revision-fixture-sweep-rev0882.json`
- `artifacts/reports/release-go-no-go-decision.json`
- `artifacts/reports/release-maintainer-handoff.json`
