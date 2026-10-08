# Key transparency for election parameters (EPB-KT)

**Track:** A (Deployable core)


A classic “cheap win” is **parameter substitution**:
- serve some voters a different ballot definition,
- serve some voters a different election public key,
- serve some verifiers a different disclosure policy,
while keeping local crypto checks superficially “valid.”

Key Transparency (KT) is a family of protocols designed to distribute sensitive cryptographic information (e.g., public keys) such that interference is prevented or detectably attempted.

## Threats addressed
- **EPB equivocation**: different audiences see different ElectionParameterBundles.
- **Rollback**: serving older (but still signed) parameter bundles.
- **Targeted discrimination**: ballot-style manipulation against specific groups.

## Requirements (normative)
1. **EPB-KT log**
   - All EPBs MUST be published as leaves in a dedicated KT structure (or as a distinct leaf type in the PBB), producing:
     - inclusion proofs,
     - consistency proofs,
     - and witness-quorum checkpoints.

2. **Pinning rule**
   - A CAST operation MUST be rejected unless:
     - the EPB hash is included in the KT structure,
     - the inclusion proof chains to a witness-quorum checkpoint, and
     - the checkpoint satisfies the witness policy.

3. **Anti-rollback**
   - Clients MUST maintain a “highest-seen” checkpoint and reject rollbacks unless a formal recovery procedure is invoked (documented in incident response).

4. **Canary retrieval**
   - Public canaries MUST continuously retrieve EPBs across geographies/locales/devices and publish parity reports anchored into ATL.

## Outputs
- Extends existing EPB mechanisms (see v10+) with explicit KT language.
- Adds `schemas/EPBTransparencyEntry.json` (optional in this pack; EPB can reuse generic log entry types if desired).