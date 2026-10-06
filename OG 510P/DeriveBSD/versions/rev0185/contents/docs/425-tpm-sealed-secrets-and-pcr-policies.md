# TPM-sealed secrets and PCR policies (optional lane)

**Tier:** C (Optional lane)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, isolation, supply-chain, operability
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

Some deployments want “secrets only unlock when *this* host booted the *expected* generation”.
TPM2 sealed objects (and PCR-bound policies) are strong prior art for this, but they are notoriously easy to integrate badly:
implicit policy, fragile upgrades, no receipts.

This doc defines a small, DeriveBSD-shaped lane:

- secrets remain **policy-governed** (`secret-policy`)
- PCR constraints are a **typed artifact** you can diff (`tpm.pcr.policy`)
- unseal acts emit **receipts** (`secret-receipt` + structured events)

No platform is forced into TPM: this lane is **optional** and must be killable by policy.
Platforms without TPM (or with hostile TPM assumptions) can use `sealed-blob` or external providers.

## Pattern mapping

- **Spec → Lock → Plan → Artifact → Activate:** the PCR policy is a digest-pinned artifact; activation selects which policy digest applies.
- **Registry → Diff → Gate:** PCR policies are reviewed as diffs and can be gated (e.g. “only allow PCR policies anchored to boot.manifest”).
- **Broker → Lease:** secrets are materialized through the secrets broker and delivered as leased capabilities (memfd/fd), not ambient files.
- **Plan → Receipt:** every unseal/materialize emits a `secret-receipt` with evidence pointers.

## What is a PCR policy in DeriveBSD

A **`tpm.pcr.policy`** is a small typed object that describes the intended PCR binding.
It is deliberately an *operator review surface*, not a full TPM policy language.

Key design goal: upgrades must be survivable.
The policy therefore supports **OR clauses** (multiple acceptable clauses during a rollout window).

Schema: `spec/tpm.pcr.policy.schema.json`
Example: `spec/examples/tpm.pcr.policy.json`

### Recommended discipline

1) **Anchor clauses to DeriveBSD boot evidence**
   - use `anchor.boot_manifest_digest` and/or `anchor.deployment_ref_digest`
   - optionally record `anchor.eventlog_digest` for measured boot canonicalization

2) Prefer **evolvable policies**
   - use TPM2 *PolicyAuthorize* (or equivalent) so you can rotate “allowed boot measurements” without resealing every secret
   - record `tpm.authorizing_key_id` as a stable policy authority identifier

3) Keep the lane killable
   - if `secret-policy` selects `source.mode=tpm2-sealed`, there must be a policy knob to refuse TPM usage entirely (fallback to `sealed-blob` or provider).

## Wiring into secret-policy

`secret-policy` already supports TPM2 sealing:

- `secrets[].source.mode = "tpm2-sealed"`
- `secrets[].source.tpm2.pcr_policy = <digest or id>`

Recommended: treat `pcr_policy` as a **digest pointer** to a stored `tpm.pcr.policy` object.

Example sketch:

```json
{
  "kind": "secret-policy",
  "policy_version": "0.1",
  "created_at": "2026-02-27T00:00:00Z",
  "secrets": [
    {
      "secret_id": "zfs.rootkey",
      "class": "opaque",
      "source": {
        "mode": "tpm2-sealed",
        "tpm2": {
          "pcr_policy": "sha256:<digest-of-tpm.pcr.policy>"
        }
      },
      "access": {
        "selectors": [{"service_id": "derive-activation"}],
        "delivery": ["memfd"],
        "require_attestation": true,
        "attestation_ref": "sha256:<digest-of-attestation requirement/policy>"
      }
    }
  ]
}
```

## Evidence / receipts

A successful unseal/materialize must produce:

- `secret-receipt` (`action: "unseal"` or `"materialize"`)
  - include `policy_digest` (the secret-policy digest)
  - include `provider` fields indicating TPM usage (e.g. `provider.name=tpm2`)
  - include `lease` (lease id + expiry) when delivering secrets as handles
  - include `events[]` pointers to structured journal records

Optionally include pointers to boot evidence:

- `boot-attestation` digest (if measured boot is enabled)
- `boot.manifest` digest (if available)

(Keep this as *pointers*; the receipt should remain small.)

## Upgrade choreography (avoid bricking)

PCR-bound secrets can brick a machine if you change what gets measured.
DeriveBSD’s discipline is:

1) **Add the next clause first** (OR list): extend `tpm.pcr.policy` with a clause anchored to the next generation’s boot evidence.
2) Roll out the new generation.
3) After the rollout window closes, **retire the old clause**.

This keeps the diff surface small and makes “what boot measurements are accepted?” reviewable.

## Prior art / references

- systemd-cryptenroll (TPM2 enrollment into LUKS2): https://www.freedesktop.org/software/systemd/man/systemd-cryptenroll.html
- systemd-pcrphase.service (boot-phase measurements into PCRs): https://www.freedesktop.org/software/systemd/man/systemd-pcrphase.service.html
- systemd TPM2 PCR measurements overview: https://systemd.io/TPM2_PCR_MEASUREMENTS/
- tpm2-tools man pages:
  - tpm2_unseal(1): https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_unseal.1/
  - tpm2_policypcr(1): https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_policypcr.1/
  - tpm2_policyauthorize(1): https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_policyauthorize.1/
- TCG TPM2 Library Part 1 (policy/PCR primitives): https://trustedcomputinggroup.org/wp-content/uploads/Trusted-Platform-Module-2.0-Library-Part-1-Architecture-Version-184-rc2_20Dec24.pdf

## Files

- PCR policy schema: `spec/tpm.pcr.policy.schema.json`
- PCR policy example: `spec/examples/tpm.pcr.policy.json`
- Secrets policy schema: `spec/secret.policy.schema.json`
- Secret receipt schema: `spec/secret.receipt.schema.json`
- Optional measured boot evidence: `spec/boot.attestation.schema.json`

