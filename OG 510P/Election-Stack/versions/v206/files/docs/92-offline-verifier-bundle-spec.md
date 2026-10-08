# 92 — Offline Verifier Bundle Spec

**Track:** A (Deployable core)


## Purpose
Define a portable, content-addressed bundle format that an independent party can download once and verify offline.

## Directory layout (recommended)
observer-kit/
  README.md
  manifest.json
  public_keys.json
  bundle/
    epb.json
    ballot_definition/
      ...
    checkpoints/
      checkpoint_*.json
    election_record/
      index.json
      ...
    results/
      rrp_*.json
    enr/
      enr_update_*.json
    logs/
      event_log_export_*.json
    proofs/
      ...
  tools/
    offline_verifier.py

## Manifest requirements
The manifest MUST:
- list every file with SHA-256 and byte length
- bind to a specific election context (election_id, epb_hash)
- bind to a specific checkpoint (checkpoint_id, checkpoint_hash)
- include ≥N signatures from *independent* signing keys (policy-defined)

### Canonicalization
Signatures are computed over a canonical JSON serialization of the manifest **excluding** the `signatures` field.
Use RFC 8785 JSON Canonicalization Scheme (JCS) where feasible; if not, use a deterministic subset (sorted keys, stable separators) and declare it.

## Public keys
`public_keys.json` MUST contain:
- key_id
- algorithm
- public key material (e.g., Ed25519 raw or PEM)
- role binding (witness, election authority, observer org)

## Verification outputs
An offline verifier MUST output:
- PASS/FAIL
- bundle_id, election_id, epb_hash
- checkpoint_id and a summary of checkpoint signatures
- list of missing/modified files (if any)

## Security notes
- The bundle is not assumed to be secret; do not include voter PII.
- Do not include per-voter network metadata.
- Publish a redaction policy for logs (what is included/excluded and why).
- Use `artifacts/checklists/public-artifact-redaction-checklist.md` as a pre-publication gate.