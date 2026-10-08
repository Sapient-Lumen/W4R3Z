# LLMPoetry — rev0070

**Current head:** `P0005-D001` — “All Three Bits Said Yes”  
**Artifact:** `LLMPoetry-rev0070-2026.06.18.17.17-allthreebitssaidyes-bloomfalsepresence-releasescaffoldprune-hardwater.zip`  
**State:** same-turn unjudged; artifact-verified; not admitted, not evidence-ready, and not an anthology candidate.

## What materially changed

`P0005-D001` commits a deterministic 32-bit Bloom-filter false positive. `CASE-1001` is absent from the exact ledger, yet bits 17, 28, and 26 are all set—each by a different inserted record—so the probabilistic filter says `POSSIBLY PRESENT` while the exact set says `NOT PRESENT`.

The release audit also removed 22 parent-dependent revision constructors totaling 1,382,114 bytes and centralized manifest, package, and ZIP member safety in `tools/release_tree.py`. `ARCHIVE_INVARIANTS.json`, stale since rev0024, is now current and validator-gated.

## Read first

- `poems/P0005/draft_001.md`
- `poems/P0005/material/source_material_packet_001.json`
- `poems/P0005/artifact/d001/BLOOM_POEM_SPEC.json`
- `poems/P0005/artifact/d001/BLOOM_RECEIPT.json`
- `poems/P0005/artifact/d001/filter_surface.txt`
- `docs/40-audits/P0005_D001_BLOOM_FALSE_PRESENCE_RELEASE_SCAFFOLD_AUDIT_rev0070.md`
- `anthology/candidates/P0004-D002_candidate_packet.json`
- `anthology/candidates/P0003-D004_candidate_packet.json`
- `anthology/candidates/P0002-D010_field_kit/README.md`

## Boundary and next action

P0005-D001 proves one synthetic deterministic Bloom-filter false positive only. It remains same-turn unjudged, not admitted, not evidence-ready, not an anthology candidate, not a real case system, and not a reader response. The release refactor is a local packaging-safety and waste reduction claim, not external security certification. P0002-D010 still has no real response; P0003-D004 and P0004-D002 remain frozen internal candidates.

Cold-review P0005-D001 in a later turn against its exact draft, filter, ledger, query, spec, receipt, and rebuild hashes; keep PILOT-0048 open for one real non-identifying disclosed-reader response to P0002-D010; do not create P0005-D002, P0004-D003, P0003-D005, or P0002-D029 by inertia.

Current research pulse: `RP-0062`.

Every LLMPoetry turn begins with a web research pulse.
