# PROOFCORE threat model — rev0855 addition

rev0855 addresses the risk that the selected streamfold sumcheck frontier remains a named target forever without executable closure.

The adversary may try to relabel absent payloads as recovered, tamper with expected hashes or byte counts, substitute a bad sumcheck transcript, silently sever the rev0854 parent checkpoint, or treat a synthetic toy transcript as a canonical streamfold proof. The rev0855 verifier checks the rev0854 parent replay, exact 17-path payload gate, current overlay absence, optional candidate-root hashes, toy sumcheck accept/reject behavior, and the rights block.

Non-goal retained: no zero-knowledge property, no succinctness, no recursive SNARK composition claim, no publication permission, no recovery of missing canonical bytes, and no mathematical correctness statement for the absent canonical streamfold payloads.

---

# PROOFCORE threat model — rev0854 addition

rev0854 adds parent replay and frontier recomputation threats.

The adversary may try to make a later overlay silently invalidate a prior PCD checkpoint, alter the frontier target selection, mark absent canonical payloads as present, change the recommended next lane away from the narrow `streamfold_sumcheck_toy_v2_family`, or smuggle a publication permission into a proof envelope. The rev0854 verifier addresses those cases by reconstructing rev0853 in a temporary tree, restoring cyclic parent surfaces from hashed snapshots, recomputing the frontier from the path-role map, checking required role coverage, checking payload absence, and rechecking the rights block.

Non-goal retained: No zero-knowledge property, no succinctness, no recursive SNARK composition claim, no publication permission, and no mathematical correctness statement for missing `streamfold` or `zkrtp` payloads.

---

## Previous rev0853 threat model

# PROOFCORE threat model — rev0853

## Assets protected

- The identity of a claim and the exact public inputs used to check it.
- The verifier code identity used for a claim.
- The distinction between local overlay integrity, proof-system validity, and publication rights.
- The recovery map from canonical proof-adjacent paths to proof roles.

## Adversary model for the first lane

The adversary may tamper with extracted files, alter a fixture, alter the expected patch-chain endpoint, change a required file path, add a root `LICENSE` or `NOTICE` sentinel without rights review, or relabel transparent local checks as SNARK/ZK claims.

The first verifier detects those local integrity and labeling failures. It does not defend against a malicious Python interpreter, compromised host filesystem, or forged cryptographic proof because no cryptographic proof system is implemented in this lane.

## Non-goals

- No zero-knowledge property.
- No succinctness claim.
- No recursive proof composition claim.
- No license grant or publication permission.
- No statement about mathematical correctness of `zkrtp` or `streamfold` payloads that are indexed but absent from this overlay.

## Completion trigger for the next lane

The next useful lane should bind one recovered `zkrtp` or `streamfold` claim to an actual verifier or receipt. It should reuse this directory shape and replace `transparent_deterministic_verifier` with the recovered proof system, receipt format, public inputs, and reject vectors.
