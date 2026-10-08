# SNARK-origin proofcore recovery audit — rev0852

Created: 2026-06-16T12:46:00-04:00 / 2026-06-16T16:46:00Z

## Why this changes the mission read

The user-supplied origin note says the project began as a **SNARKs-adjacent proof exploration** and that this was the core for most of its life. That explains the shape of the archive: EvidenceVault looks less like an ordinary research bundle and more like a proof-carrying evidence object that gradually built publication, provenance, rights, and integrity scaffolding around a buried proofcore.

The revised heart of the mission is therefore not just "preserve a trustworthy research object." It is: **preserve a proof-carrying research object where claims, evidence, verifier commitments, public inputs, witness policy, provenance, and rights decisions remain distinguishable and checkable.**

## Evidence visible in the overlay

The overlay does not carry the canonical proof payloads themselves, but its carried canonical indexes and ledgers expose the old core:

- `INDEX/files.csv` carries 4586 canonical file rows.
- A broad proof/SNARK/protocol keyword scan finds 1067 proof-signal paths totaling 25,915,114 bytes.
- Of those proof-signal paths, 0 are present as payload files in this overlay ZIP and 1067 are absent. This confirms that this ZIP is a map/overlay, not the full proof tree.
- `zkrtp` appears as 193 files / 18,902,244 bytes and is recorded as "zk-RTP represented without retained sources/ root".
- `streamfold` appears as 83 files / 2,778,263 bytes and is recorded as "StreamFold represented without retained sources/ root".
- The index names `sumcheck`, `FRI`, `PCS`, `Halo2`, `lookup`, `folding`, `sigma`, proof receipts, witness sets, verifiers, DSSE attestations, SCITT receipts, and proof-carrying-policy papers.

Representative indexed paths include:

| Path | Bytes | Present in overlay? |
|---|---:|---:|
| `papers/ev_zkrtp.tex` | 4,081 | `false` |
| `papers/ev_streamfold.tex` | 4,869 | `false` |
| `artifacts/curated/streamfold/abi_ir/sumcheck_toy_v2.json` | 2,015 | `false` |
| `artifacts/curated/streamfold/abi_ir/fri_open_toy_v3_mined.json` | 2,585 | `false` |
| `artifacts/curated/streamfold/abi_ir/halo2_multiopen_toy_v1.json` | 2,086 | `false` |
| `certs/curated/zkrtp_v2/attestations/policy_proof_accept.dsse.json` | 3,842 | `false` |
| `renders/legacy_pdfs/zkrtp_portfolio/paper_proof_carrying_policies.pdf` | 166,704 | `false` |
| `schemas/policy_circuit_cost_model.schema.json` | 2,901 | `false` |
| `sources/ocf_llm/tools/verifiers/toy_sic_zk_verifier_v1.py` | 1,357 | `false` |


## What is missing

The missing thing is a first-class proofcore contract. The archive has many signs of proof work, but the overlay does not expose a simple path from claim to machine check:

1. Claim schema: what is being proven, and what is merely being recorded?
2. Public inputs: what bytes are public commitments, roots, keys, statements, or verifier parameters?
3. Witness policy: what is private, redacted, unavailable, synthetic, or unnecessary?
4. Verifier code: what command checks the claim, and what exact output means accept/reject?
5. Circuit/constraint/IR mapping: where do `sumcheck`, `FRI`, `PCS`, `Halo2`, lookup, folding, and other indexed protocol artifacts fit?
6. Parameter registry: hash functions, curves, transcript labels, setup status, verifier-key identity, and versioning.
7. Rights closure: `zkrtp` and `streamfold` remain blocked pending owner/upstream license decisions.

## What should change

Create a canonical `PROOFCORE/` lane in the full tree, not just another audit file:

```text
PROOFCORE/
  THREAT_MODEL.md
  GLOSSARY.md
  proofcore_manifest.json
  claims/*.json
  commitments/*.json
  public_inputs/*.json
  witness_policy/*.md
  verifiers/*
  parameters/*.json
  fixtures/accept/*
  fixtures/reject/*
  maps/canonical_path_to_role.csv
```

The first green path should be deliberately small: one claim, one commitment/public-input object, one verifier, one accept vector, one reject vector, and one rights decision. After that, expand to `zkrtp` and `streamfold` as component families.

## What went wrong or became wasteful

The project appears to have spent many revisions hardening the archive shell: publication queue safety, symlink boundaries, overlay patch application, rights scans, SPDX/RO-Crate surfaces, and command ergonomics. That work is not wasted; it is exactly the kind of infrastructure a proof-carrying artifact needs before publication. The waste is that the infrastructure became more visible than the proof question it was supposed to protect.

The correction is not to delete the shell. The correction is to make every new shell change answer a named invariant:

- Does this protect proofcore integrity?
- Does this protect publication rights?
- Does this protect reproducibility/provenance?
- Does this reduce full-tree/cloudtainer waste?

If none apply, stop and work on proofcore recovery instead.

## Speculative read

The original SNARK-adjacent exploration may have broadened into proof-carrying policies, receipts, attestations, and governance because those were easier to preserve, explain, and audit than a complete cryptographic proof stack. That can be a valid evolution. But it should be named: either EvidenceVault is pursuing actual zero-knowledge/succinct proof verification, or it is pursuing a broader proof-carrying evidence system with some SNARK-inspired structure. Both are valuable; conflating them is risky.

## Research notes

- zk-SNARKs are normally framed as zero-knowledge, succinct, non-interactive arguments of knowledge; this means the project should avoid using the label unless the proof system, witness privacy boundary, and verifier semantics are explicit.
- Proof-carrying data is a close conceptual neighbor: data/messages carry proofs that prescribed properties hold. EvidenceVault's receipts, attestations, policies, and verifier inventory look closer to this family than to a single monolithic SNARK implementation.
- in-toto/SLSA/SCITT-style attestations and provenance are useful for supply-chain integrity, but they do not by themselves establish mathematical/protocol correctness.
- SPDX `NOASSERTION` still means no license conclusion has been made. It is not a publication grant.

## Rights status

Publication remains blocked. rev0852 does not add or infer any root or component license. It records that the proof-origin context makes source/root and rights closure more important, not less.
