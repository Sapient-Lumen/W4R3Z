# Wake from amnesia — rev0019

Open the cube here:

1. `START_HERE.md`
2. `docs/170-rev0019-leaseroute-storemesh-budgetreceipt.md`
3. `docs/171-lease-route-gossip-pressure.md`
4. `docs/172-store-mesh-tombstone-repair.md`
5. `docs/173-garden-budget-receipts.md`
6. `docs/174-repeated-round-ledger.md`
7. `docs/175-surface-ledger-refactor-rev0019.md`
8. `docs/163-rev0019-storeflight-leasequorum-surfaceclean.md`

## What rev0019 means

The cube now treats generosity channels as pressure surfaces. Garden nodes, route gossip, contact leases, sibling storage, budget refusals, provider proofs, and witnesses all help the DHT. They also all create plausible-looking false confidence when checked alone.

The local acceptance posture is now:

```text
lease evidence gates route repair
store acknowledgements gate storage claims
tombstone evidence gates resurrection pressure
budget receipts make garden throttling visible
repeated rounds gate liveness/proof/witness convergence
```

## Active Python surfaces

- `storeflight.py`
- `leasequorum.py`
- `storagelease.py`
- `readrepair.py`
- `leaseroute.py`
- `storemesh.py`
- `budgetreceipt.py`
- `roundledger.py`
- `surfaceledger.py`

Run:

```bash
scripts/ci/run_python_cloudtainer_lane.sh
```
