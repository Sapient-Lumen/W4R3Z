# 868 — Trust-chain fixture-surface audit and policy-receipt scope refactor

**Track:** Shared  
**Release:** v852  
**Status:** Maintainer audit/refactor

## What changed

The strongest verifier path now depends on ten packet-external byte-pinned fixtures rather than a hand-built pile of CLI flags. v852 refreshes the fixture-surface audit so those fixtures stay compact, external to the packet under test, and checked by sidecar SHA-256 files.

Current required fixture roles:

1. trust keyset
2. trust-keyset publication receipt
3. trust-governance bundle
4. trust-governance-bundle publication receipt
5. trust-status snapshot
6. trust-status-snapshot publication receipt
7. signer-authorization roster
8. signer-authorization-roster publication receipt
9. verification-policy lockfile
10. verification-policy-lockfile publication receipt

`artifacts/reports/trust-chain-fixture-surface-rev0852.json` reports:

```text
fixture_count: 10
failure_count: 0
all_sidecars_match: true
all_fixtures_packet_external: true
```

The verification-policy scope audit now also checks that the policy receipt binds the policy digest, matches the policy id, and matches the policy packet selector.

## Maintenance rule

Do not add more trust-chain fixtures unless the new fixture is:

- packet-external;
- byte-pinned by sidecar;
- referenced by the strict policy lockfile;
- covered by a positive verifier path;
- covered by at least one fail-closed negative control;
- summarized in `scripts/report_trust_chain_fixture_surface.py`.

## Source-pressure note

v852 keeps the current-authority source-review cliff at zero while avoiding a wasteful linear platform-tail review. The source reports show:

```text
expired review windows: 0
current-authority rows due within 30 days: 0
platform/UI/vendor rows due within 30 days: 719
bounded platform sample size: 57
linear platform reviews avoided: 662
```

The next source-maintenance move should stay bounded: sample and consolidate the platform/vendor tail rather than spending a full session clicking mutable support pages one by one.
