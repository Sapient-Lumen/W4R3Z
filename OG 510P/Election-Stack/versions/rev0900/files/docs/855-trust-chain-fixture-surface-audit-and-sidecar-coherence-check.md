# 855. Trust-chain fixture surface audit and sidecar coherence check

**Track:** Shared / verifier-maintainer audit  
**Revision:** v848

## What this refactors

The strongest synthetic verifier command now depends on eight packet-external fixture files: trust keyset, keyset receipt, governance bundle, governance-bundle receipt, status snapshot, status-snapshot receipt, signer-authorization roster, and verification-policy lockfile. The wasteful failure mode would be to keep adding prose about these files while no compact machine-readable report says whether their sidecars still match.

rev0848 keeps `scripts/report_trust_chain_fixture_surface.py`, now pointing at the scoped rev0848 policy lockfile, and emits:

- `artifacts/reports/trust-chain-fixture-surface-rev0848.csv`
- `artifacts/reports/trust-chain-fixture-surface-rev0848.json`

Current result:

```text
fixture_count: 8
failure_count: 0
all_sidecars_match: true
all_fixtures_packet_external: true
```

## Maintainer rule

Do not move any trust root, governance bundle, publication receipt, status snapshot, signer-authorization roster, or verification-policy lockfile into the packet being verified. Keep these fixtures packet-external, byte-pinned, and explicitly supplied by the caller. Prefer the policy lockfile for the strongest synthetic path so humans do not hand-copy a long list of trust-chain flags.

## Boundary

This audit proves only local fixture-surface coherence. It does not prove production signer authority, real independent publication governance, live online revocation freshness, certification, legal reliance, current voter instruction, or live-pilot readiness.
