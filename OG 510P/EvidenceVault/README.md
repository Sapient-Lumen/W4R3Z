# EvidenceVault

## Make a research claim travel with what would check it

EvidenceVault explores a practical ambition: a research object should carry not only conclusions, but the material needed to inspect them. A recipient should be able to identify the claim, public inputs, commitments, verifier, examples that should pass and fail, provenance and unresolved dependencies. An argument that cannot be machine-checked should be identified as such, not hidden behind a successful archive checksum. The [proofcore recovery plan][plan] names this a proof-carrying research vault.

The supplied rev0874 is a partial recovery overlay of that larger project. It is useful in three connected ways: as an exact-byte recovery toolkit, as an executable collection of small claim-and-verifier experiments, and as a study of the boundary between checking some bytes and actually using those same bytes. Its incompleteness changes which questions it can answer; it does not reduce the whole work to an inventory of failures.

## A claim, its evidence and its envelope are different objects

The [PROOFCORE entrance][proofcore] develops a repeatable structure: a named claim points to public inputs, a witness policy, verifier code, accept/reject fixtures and a certificate envelope. Earlier checkpoints retain their hash-bound historical inputs, while later replay paths can repair how those inputs are checked. This lets a later revision change its working verifier without quietly rewriting the bytes an earlier claim named.

For example, one implemented lane checks local overlay consistency and the declared state of its proof-related materials. Another checks that a selected family of seventeen StreamFold payload paths agrees with the canonical index, while distinguishing actual bytes from their absence. The [framed-transcript claim][claim] links this admission/absence work to a small mathematical transcript experiment. These are narrower and more inspectable statements than “the research is verified.”

The envelope is transparent and deterministic. It is not itself a signature by an independent witness, a succinct cryptographic proof, or evidence that missing StreamFold code implements a correct protocol. Its value is organizational and executable: it specifies what a checker must read and what would make the local claim fail. The [threat model][threat] keeps local integrity, mathematical validity and permission to reuse material separate.

## The mathematical experiment: bind the challenge to the conversation

The toy sumcheck work makes the distinction between a plausible transcript and a checked transcript concrete. A claim gives a polynomial over a small prime field and its asserted sum over Boolean inputs. The verifier checks each round's degree bound and that the round polynomial's values at zero and one add to the running claim; the next claim is its value at the round challenge. The last value must agree with evaluation of the public polynomial at the collected challenges.

The early harness checked arithmetic. Subsequent revisions address who determines the challenges and what they depend on. The [prefix-bound verifier][prefix] recomputes challenges from the public context, claim, current round polynomial, running claim, prior message hashes and named contract/verifier identities. A supplied challenge is not accepted merely because the rest of the transcript can be made to fit it.

The [framed verifier][framed] then makes the transcript an ordered log of labeled message absorptions and challenge derivations. Each step incorporates the previous state; the required labels and order are checked against the contract. This prevents the reader from treating a bag of individually hashed messages as though it necessarily records the same protocol conversation. Full and minimum payload receipts are themselves named inputs to that conversation.

This is an inspectable learning and regression harness, not a production proof system. The code even directly computes the Boolean-hypercube sum from the public polynomial, making the non-succinct character tangible. It hides no witness and does not establish zero knowledge or soundness for the absent canonical StreamFold implementation. Its concrete contribution is to make transcript binding and tampered-input rejection executable subjects of study.

## Recover exact work without replacing it with plausible work

Suppose a workspace has vanished but an index, patch history and some exported objects survive. A file named in the index is not necessarily present; a newer file at the same path may be valuable but not be the indexed historical version. EvidenceVault therefore separates three inventories:

- The overlay manifest describes the files actually shipped in this partial object.
- The canonical index describes the much larger historical target.
- Content-addressed recovery objects preserve exact historical bytes that need not occupy their old paths.

The [coverage implementation][coverage] computes those relationships from current files rather than trusting a remembered recovery count. Exact-at-path, divergent-at-path, recoverable elsewhere and unavailable are different results. The carried [RO-Crate bridge][crate] provides research-object metadata for the historical canonical release; it is not a declaration that all of those referenced entities are contained in this overlay.

A particularly useful recovery path is [complete new-side reconstruction from patches][patches]. Most diffs omit unchanged context and are not backups. This tool only considers contiguous new-side streams beginning at line one, then requires both the indexed byte count and full SHA-256 to match. Missing context is not guessed. A candidate that reconstructs an older version does not authorize overwriting a later version at the same path. The [rev0866 recovery account][recovery] records eighty-one previously missing files recovered by this route, including twelve source payloads, while leaving legitimate later-overlay files intact.

Other lanes locate exact payloads in loose directories or ZIP exports and stage qualifying sets outside the overlay. A negative search receipt is useful because it records where the expected bytes were not found; it is not proof that they do not exist anywhere. The [latest recovery account][snapshot] reports 109 exact files at canonical paths out of 4,586, and 125 rehydratable files when recovery objects are included. These are different coverage measures over the same canonical inventory, not interchangeable measures of completeness. All seventeen selected StreamFold payloads and the canonical root README remain unresolved in that record.

## A check must be bound to the object that is used

The latest correction is not merely “hash files more often.” The [rev0874 execution-snapshot audit][snapshot] describes a synthetic regression using the reconstructed old gate: it checked legitimate validator bytes, ran a replacement installed between checks, then checked the restored original. Both boundary hashes could pass while the wrong program had run. That demonstrates a local verify/use race, not an allegation that an outside party attacked a historical release.

The replacement [gate implementation][gate] captures the complete inventoried overlay into a private execution tree after verifying its paths, lengths and hashes. Coverage and configured validators execute from that captured tree under isolated Python, not from mutable source-tree script paths. Before declaring success, it checks both the retained source and execution snapshot again. The regression can still swap and restore the original path: what matters is that the legitimate captured validator executes, not that every transient mutation has been detected.

This distinction is useful for reproducible research and recovered tools. A report about a validator's bytes should not silently become a report about another program found later at the same filename. The snapshot closes that source-path substitution route in an ordinary run. Read-only permissions do not make it a sandbox against a hostile process with the same operating-system identity, and the gate cannot authenticate its own bootstrap merely by checking files it was told to trust. External identity verification remains a separate boundary.

An adjacent historical correction makes the same point about ZIPs: structure checks and the reported digest must concern the same captured archive, not one file validated before a pathname is reopened to hash its replacement. The [supplied development history][history] is valuable for these concrete counterexamples and repairs, not just for successful gate totals.

## Where to enter, and what remains open

For recovery, begin with the coverage and patch-reconstruction sources. For proof experiments, begin with the claim, transcript code and fixtures under PROOFCORE. For validation mechanics, read the execution-snapshot audit before the gate. The overlay's own command guide is the relevant entrance: its carried canonical Makefile refers to material absent from the partial object, so the canonical and overlay command surfaces must not be conflated.

The [archived rights overview][rights] and [unresolved license decision][license] remain part of the supplied work; mechanical consistency is not a new rights grant. This introduction does not convert the overlay into a complete canonical release or replace its third-party notices. That is a material reuse boundary, not the organizing purpose of every page.

Read beside [DelayBasin](../DelayBasin/README.md) for continuing a project through disrupted workspaces, [BrowserRT](../BrowserRT/README.md) for the difference between verified bytes and a completed application operation, and [AnonSync](../AnonSync/README.md) for exact state tied to ordinary file use. Their mechanisms differ. The common question is how to carry enough inspectable evidence for someone else to continue responsibly without pretending that a checksum resolves every substantive claim.


[plan]: versions/rev0874/files/EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure/PROOFCORE_RECOVERY_PLAN_REV0852.md
[proofcore]: versions/rev0874/files/EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure/PROOFCORE/README.md
[claim]: versions/rev0874/files/EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure/PROOFCORE/claims/ev-streamfold-framed-receipt.rev0858.claim.json
[threat]: versions/rev0874/files/EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure/PROOFCORE/THREAT_MODEL.md
[prefix]: versions/rev0874/files/EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure/PROOFCORE/verifiers/verify_sumcheck_fs_prefix_transcript_rev0857.py
[framed]: versions/rev0874/files/EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure/PROOFCORE/verifiers/verify_sumcheck_fs_framed_transcript_rev0858.py
[coverage]: versions/rev0874/files/EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure/scripts/canonical_coverage.py
[crate]: versions/rev0874/files/EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure/RO_CRATE_PROFILE.md
[patches]: versions/rev0874/files/EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure/scripts/recover_indexed_files_from_patches.py
[recovery]: versions/rev0874/files/EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure/AUDIT/PATCH_CORPUS_EXACT_RECOVERY_REV0866.md
[snapshot]: versions/rev0874/files/EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure/AUDIT/VERIFIED_GATE_EXECUTION_SNAPSHOT_REV0874.md
[gate]: versions/rev0874/files/EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure/scripts/overlay_gate.py
[history]: versions/rev0874/files/EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure/README.md
[rights]: versions/rev0874/files/EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure/RIGHTS/README.md
[license]: versions/rev0874/files/EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure/RIGHTS/LICENSE_DECISION_BLOCKER.md

## Snapshots and preservation

### Selected snapshots

#### [rev0874](versions/rev0874/README.md)

Adds a verified execution-snapshot boundary to the overlay’s validation design. The supplied README reports limited canonical recovery coverage, absent selected StreamFold payloads and an unresolved canonical README mismatch. The overlay inventory can be checked without pretending the missing canonical archive has been recovered.

### How to read this preservation

These are selected historical snapshots. Original filenames, ZIP bytes and extracted contents are unchanged; new guides, inventories and integrity notes are separate. “Latest” in a supplied filename is a historical label. Nested archives remain nested. Research source claims and reported validation runs were not independently reproduced for this archival delivery. Read the retained limitations, open gates and rights notices before reuse. See the [current owner declaration](../../LEGAL-NOTICE.txt); third-party terms remain distinct.

[Original identities and hashes](PROVENANCE.json) · [Back to OG 510P](../README.md)
