# P0004 D002 Candidate Freeze / OCI Path Containment Audit — rev0069

## Priority decision

The riskiest unfinished internal task was the delayed decision on D002. Creating D003 before that decision would have rewarded motion instead of resolving whether the current artifact had earned a stop. The later-turn review promotes D002 to an **internal anthology candidate, not evidence**, ranks it behind P0003-D004, and freezes P0004 at D002.

The work’s strongest pressure survives disclosure. In the merged filesystem, only `NO APPEAL ON FILE` remains. In the image graph, the manifest still requires the lower content-addressed layer containing `THIS IS AN APPEAL`, `THE RECORD IS WRONG`, and `I WAS HERE`. The current view denies what its own retained history still contains.

The residual weakness is equally explicit: the lower statements are generic and the title/status phrase may make the piece feel like a solved OCI riddle. That is now a reader question, not a reason to manufacture D003 without evidence.

## Severe audit finding: validation and generation could cross the cube boundary

The incoming release package itself contained no symlinks and its D002 descriptors were valid. The defect was latent in the tooling:

- the generator joined `artifact_dir` and `layout_dir` from a spec without first proving they remained beneath the cube and artifact roots;
- the validator split a descriptor digest into path components and looked up the corresponding blob before enforcing the project’s exact SHA-256 grammar;
- non-canonical tar names such as repeated separators or dot segments were not rejected by one shared rule;
- the layer simulator could retain an impossible file-ancestor/child pair during replacement edge cases.

A malicious or accidentally corrupted spec could therefore direct generator writes outside the cube. A malformed descriptor could cause the checker to inspect a path outside the image layout before eventually reporting failure. That behavior is unacceptable in a cloudtainer whose archive claims contained, replayable verification.

## Refactor

`tools/oci_path_safety.py` now provides one fail-closed path contract used by both generator and checker:

1. paths must be canonical POSIX relatives with no absolute prefix, traversal, dot segments, repeated separators, backslashes, controls, or trailing slash;
2. every existing path component is checked for symlinks before resolution;
3. spec paths must remain beneath their declared roots;
4. project descriptors must be exactly `sha256:` plus 64 lowercase hexadecimal characters before a blob path is constructed;
5. declared size and a 64 MiB project-local bound are checked before blob bytes are read and hashed.

The OCI checker now also verifies path-tree consistency and correct file-to-directory replacement. Its self-tests rebuild D002 in a temporary cube byte-for-byte, reject escaping `artifact_dir` and `layout_dir` values, reject a symlinked layout, and verify that outside sentinels remain unchanged. The real frozen D002 artifact is never rebuilt or mutated by those tests.

## Specification boundary

OCI v1.1.1 requires descriptor size and digest verification, defines SHA-256 encodings as 64 lowercase hexadecimal characters, places content-addressed blobs beneath `blobs/<algorithm>/<encoded>`, and permits unreferenced blobs in a general image layout. LLMPoetry’s closed-world blob rule remains deliberately stricter and project-local. The whiteout review remains grounded in OCI’s lower-layer-only and order-independent opaque-whiteout semantics.

At the June 18, 2026 access check, the official image-spec release page still marked v1.1.1 as latest.

## Secondary truth-drift finding: nested proof status contradicted the current cube

`registries/proof_status.json` had a correct P0004 top-level head but still described P0002-D023 as current inside its P0002 entry, left P0003-D004 in a same-turn-unjudged state after its later candidate freeze, omitted P0004 from the poem map, and retained a `current_context` routed to P0003. The main validator did not inspect those nested aliases. Rev0069 normalizes P0002, P0003, and P0004 into structured family entries and extends `tools/check_deep_surface_consistency.py` so global proof aliases, nested family heads, candidate/freeze state, paths, and the P0002-D010 zero-response target must agree with `registries/poem_index.json`.

Clean-room validation exposed a related lifecycle bug in `tools/check_surface_freshness.py`: it recognized only WAL-style candidate artifact fields, then demanded that frozen OCI index/surface files repeat the later routing revision and head. That would force false provenance or byte mutation. The checker now consumes the candidate artifact inventory generically and lets the current wrapper bind hash-frozen low-level components to the current head. Mutable wrappers must still name rev0069.

## Frozen-byte boundary

The revision does not rewrite D002’s draft, source packet, metrics, spec, receipt, surfaces, image index, layout marker, config, manifest, or layer blobs. The candidate packet records every artifact file’s size and SHA-256. The exact rev0068 disclosure remains historical creation-time state; current candidate status is supplied only by the rev0069 review and wrapper.

## External bottleneck

P0002-D010 remains the first disclosed-reader target and its response log remains empty. P0003-D004 remains frozen at rank two. D002 is rank three. No synthetic response, admission, evidence status, or publication clearance is created.

## Next

Keep P0004-D002 and P0003-D004 frozen, run no new candidate apparatus, and obtain one real non-identifying disclosed-reader response for P0002-D010; create P0004-D003 only if later external pressure identifies a concrete failure, and do not create P0003-D005 or P0002-D029 by inertia.
