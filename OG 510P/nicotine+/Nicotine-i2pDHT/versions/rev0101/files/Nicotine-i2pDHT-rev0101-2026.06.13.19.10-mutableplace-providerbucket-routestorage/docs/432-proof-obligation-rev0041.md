# Proof obligation — rev0041

The current proof obligation is local and narrow:

- router-stop shadows reject unsafe stop/bridge/notransit/persistence cases;
- session resume rejects missing components, withdrawn announcements, hard negatives, replay, drift, forks, and family monoculture;
- exit journal rejects signature/replay/rollback/fork/link/gap/drift/hard-negative-drop cases;
- controlfold sees the live rev0041 path and the rev0040 predecessor path.

Required proof path:

```sh
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_rev0041_routerstop_sessionresume_exitjournal.py
scripts/ci/run_python_cloudtainer_lane.sh
```
