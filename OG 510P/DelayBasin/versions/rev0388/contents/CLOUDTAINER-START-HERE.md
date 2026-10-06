# Cloudtainer working overlay

Current working overlay: `rev0388` (target filename recorded in `cloudtainer/CLOUDTAINER-REVISION-NOTE.json`).

Start with:

- `cloudtainer/oq0266-self-contained-evidence-capsule-audit-2026-06-18.md`
- `cloudtainer/CLOUDTAINER-REVISION-NOTE.json`
- `cloudtainer/observations/oq0266-self-contained-evidence-capsule-findings-2026-06-18.json`
- `cloudtainer/oq0266-isolated-semantic-pilot/PREFREEZE-README.md`
- `cloudtainer/oq0266-isolated-semantic-pilot/POSTFREEZE-README.md`

## What changed

Rev0387 froze all dynamic result artifacts, but its final scorer still loaded the assignment plan, policy, dispatch, packets, templates, scorer intakes, and validator surfaces from the mutable ambient pilot tree. Deleting that tree made an otherwise valid “portable” run bundle unscoreable.

Rev0388 replaces that dynamic-only handoff with one self-contained evidence capsule. It contains the exact prefreeze dispatch kit, exact postfreeze batch kit, response-set lock, policy-verification receipt, and all four response/custody/score triplets. Its manifest binds both source kits and every result artifact.

Final scoring now requires the exact capsule and a separately preserved expected SHA-256. The digest is checked against the raw capsule bytes before any ZIP or JSON member is interpreted. An internally valid but result-changing replacement capsule is therefore rejected against the original expected digest.

The verifier reconstructs a temporary read-only replay root solely from captured source-kit bytes. It does not consult mutable pilot data outside the capsule and does not execute code carried inside the capsule. Nested ZIPs are inspected with explicit path, topology, integrity, and resource bounds before any file is materialized.

The conventional response/custody/score validation path was refactored to accept an explicit source root, allowing the isolated verifier to reuse it against the capsule-derived tree rather than maintaining a second scoring interpretation.

## Tested diagnostics

```bash
python -B -S tools/check_priority_zero_preanswer_material_clamp_contract.py
python -B -S tools/check_oq0266_isolated_batch_barrier_contract.py
python -B -S cloudtainer/tools/check_oq0266_isolated_semantic_pilot.py --json
python -B -S cloudtainer/tools/check_cloudtainer_mission_preflight.py --json
make lint
```

## Real execution boundary

Do not distribute the full cube. Before the first real response, preserve the exact SHA-256 of:

`cloudtainer/oq0266-isolated-semantic-pilot/prefreeze-dispatch-kit.zip`

outside the cube with a separate person or append-only service. A collector opens only that kit and distributes exactly one nested responder ZIP to each of four genuinely separate responders. After all four responses return, follow `PREFREEZE-README.md` to create the exact all-response lock.

Only after that lock exists may the collector open:

`cloudtainer/oq0266-isolated-semantic-pilot/postfreeze-batch-kit.zip`

Run the policy verifier, preserve its receipt, and pass both prerequisite receipts to every arm’s custody helper. After all four score sheets freeze, run the capsule assembler with the original prefreeze and postfreeze kit ZIPs. Immediately preserve the emitted outer capsule SHA-256 outside the assembly directory. Final aggregation requires both that expected digest and the exact capsule; it needs no ambient pilot data directory.

The package still does not prove real-world identity separation, trusted time, non-collusion, signed provenance, or causal operator burden. It still lacks a genuine isolated batch and the conventional OQ-0266 triplet.

The current canonical DelayBasin surfaces inside the archive remain `rev0374`; `rev0388` is the requested cloudtainer working overlay, not a canonical promotion.

Prior working surfaces remain under `cloudtainer/`, including `CLOUDTAINER-REVISION-NOTE-rev0387-preserved.json`, `oq0266-final-triplet-freeze-and-portable-bundle-audit-2026-06-18.md`, and earlier audits.
