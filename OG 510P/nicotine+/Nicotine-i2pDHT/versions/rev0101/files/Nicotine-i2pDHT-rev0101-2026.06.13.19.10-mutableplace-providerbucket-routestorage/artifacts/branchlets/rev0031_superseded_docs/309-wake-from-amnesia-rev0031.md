# Wake from amnesia — rev0031

Start here after context loss:

1. Read `START_HERE.md`.
2. Read `docs/304-rev0031-leaseprobe-repairdebt-auditmesh.md`.
3. Inspect `src/i2p_dht_lab/leaseprobe.py` and `src/i2p_dht_lab/repairdebt.py`.
4. Run `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests/test_rev0031_leaseprobe_repairdebt_auditmesh.py`.
5. Run `scripts/ci/run_python_cloudtainer_lane.sh` for the whole cube lane.

Working memory:

```text
Lease probes prevent sticky entrances from being promoted by one valid contact surface.
Repair debt prevents repair triggers from becoming unbounded outbound/garden work.
Auditmesh prevents current revision surfaces from becoming hidden branch debris.
```
