# LLMPoetry Datacube Data Card — rev0070

## Current state

The global head is `P0005-D001`, a same-turn unjudged deterministic Bloom-filter poem. It is artifact-verified but not admitted, evidence-ready, or a candidate. `P0003-D004` and `P0004-D002` remain frozen internal candidates. `P0002-D010` remains the first disclosed-reader target and has zero responses.

## Substantive result

The exact inserted ledger contains `CASE-0017`, `CASE-0021`, and `CASE-0028`, but not `CASE-1001`. The absent query maps to three set bits; each bit was contributed by a different true record. The filter therefore returns possible presence without any record answering yes. The artifact is only four bytes, but its contradiction is fully reconstructable from the committed spec and receipt.

## Audit and refactor

The distributable cube no longer ships parent-dependent root revision constructors: 22 files totaling 1,382,114 bytes were removed. Manifest construction, package construction, package inspection, and consolidated manifest coverage now share `tools/release_tree.py`. A stale archive-identity file that still claimed rev0024/P0002-D010 is now current and checked against `STATE.json`.

## Known limits

The Bloom result is one synthetic construction, not a claim about a live case system. Its literary pressure remains unjudged until a later turn. Internal correctness also cannot replace the missing real disclosed-reader response.

## Next action

Cold-review P0005-D001 in a later turn against its exact draft, filter, ledger, query, spec, receipt, and rebuild hashes; keep PILOT-0048 open for one real non-identifying disclosed-reader response to P0002-D010; do not create P0005-D002, P0004-D003, P0003-D005, or P0002-D029 by inertia.
