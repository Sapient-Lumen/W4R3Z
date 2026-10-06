# OQ-0266 final-triplet freeze and portable-bundle audit — 2026-06-18

## Executive finding

Rev0386 correctly froze all four responses before postfreeze disclosure and correctly bound each custody record to the exact response-set lock and policy-verification receipt. Its final handoff, however, was not actually frozen.

`prepare_oq0266_isolated_run_manifest.py` emitted a read-only JSON document that contained absolute paths to the four response, custody, and score-sheet files. It did not record the hashes of the custody or score-sheet files, and the final scorer reopened those paths later. The manifest therefore froze *where to look*, not *what bytes had been assembled*.

I reproduced the consequence against the untouched rev0386 workflow. After a positive four-arm synthetic run had been assembled, I replaced only the compact arm's score sheet at the recorded path and left the completed run manifest unchanged. The same manifest still passed. The accepted decision changed from `support-isolated-semantic-recovery-pilot` to `reverse-isolated-semantic-support`; the compact score changed from 17 to 0 while the other scores remained baseline 2, sham 4, and trace 16.

This is a time-of-check/time-of-use defect at the final evidence boundary. It could turn an honestly assembled batch into a different accepted result without changing the artifact described as the frozen run manifest.

## Repair

Rev0387 replaces the path-only final handoff with one deterministic, content-addressed run bundle:

- `run-manifest.json` is the first ZIP member and records the exact SHA-256 of the response-set lock, policy-verification receipt, and all twelve per-arm response/custody/score-sheet members.
- Member names, order, file type, permissions, timestamps, and compression mode are fixed by contract.
- The assembler validates every triplet and prerequisite binding before publishing the bundle.
- Publication is same-directory, fsynced, atomic, no-clobber, and read-only.
- The final scorer reads the bundle bytes once, verifies exact topology and every member digest, parses every JSON member strictly, and validates only temporary read-only copies created from those captured bytes.
- The final summary reports both the outer bundle SHA-256 and the internal manifest SHA-256.

The scorer CLI now takes one dynamic input, `--run-bundle`, instead of separately reopening a lock, policy receipt, and path manifest. The run remains reproducible and portable without preserving the assembler machine's absolute paths.

## Permanent canaries

The normal lint path now proves both sides of the final freeze boundary:

1. **Source mutation isolation.** After bundle publication, the checker changes the compact score at its original source path to zero and reruns aggregation. The accepted decision and reported bundle identity remain unchanged.
2. **Member replacement rejection.** The checker changes the compact score member inside a copied bundle while leaving the internal manifest unchanged. Aggregation fails before score interpretation with a member-hash disagreement.

The existing attacks against incomplete response collection, missing or substituted prerequisite receipts, response-lock substitution, plan/commitment replacement, outcome-adaptive scorer policy, responder-stimulus substitution, duplicate responders, and non-finite JSON remain active.

## Audit and refactor

The old implementation duplicated the meaning of a "completed run" across a template, an assembler, and a scorer. Rev0387 centralizes that meaning in `cloudtainer/tools/oq0266_isolated_run_bundle_lib.py`, including:

- contract and record identifiers;
- exact manifest schemas;
- canonical per-arm member names;
- exact member order;
- bundle topology validation;
- member digest validation; and
- one-shot bundle loading.

`tools/priority_zero_external_run_artifact_lib.py` now exposes one generic atomic byte publisher and one deterministic ZIP publisher. JSON finalization and run-bundle publication therefore share the same no-clobber primitive rather than carrying separate check-then-write implementations.

The postfreeze operator instructions now say what the tool actually does: assemble one portable exact-byte bundle, preserve its SHA-256 outside the working directory, and give only that bundle to final aggregation. Manual hash transcription remains forbidden.

## External design pressure

The repair uses a narrow, established packaging principle rather than inventing another governance layer. RFC 8493 describes BagIt as a reliable storage/transfer layout in which manifests map file paths to checksums and a package is valid only when the listed checksums verify. It also explicitly warns that checksum packaging is confidence against corruption, not protection against an active attacker.

The in-toto specification similarly treats a final product as target files plus metadata whose materials and products are checked across steps. DelayBasin borrows only that artifact-identity idea. This run bundle has no signatures, authorized functionary keys, independent layout owner, trusted timestamp, or transparency log and must not be described as in-toto provenance or BagIt conformance.

References:

- RFC 8493, *The BagIt File Packaging Format (V1.0)*: https://www.rfc-editor.org/rfc/rfc8493.html
- in-toto specification: https://github.com/in-toto/docs/blob/master/in-toto-spec.md

## Remaining risk and next move

The internal runnable path is no longer the main bottleneck. The next mission-bearing action remains external execution:

- one genuinely clean conventional OQ-0266 response/custody/score-sheet triplet; or
- one genuinely isolated four-responder batch using the prefreeze dispatch kit and the postfreeze bundle workflow.

The final bundle itself can still be replaced wholesale unless its outer SHA-256 is preserved by a separate person or append-only service immediately after assembly. Local hashes are unsigned. String identifiers do not prove distinct people or non-collusion. One responder per arm cannot identify causal burden. The trace arm is still a bounded excerpt rather than a measured full archive.

No additional registry or gate was added beyond the executable contract needed to close the reproduced defect.
