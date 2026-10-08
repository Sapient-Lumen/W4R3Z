# rev0088 focused validation

- `pytest -q tests/test_cli.py`: passed
- `pytest -q tests/test_native_host.py`: passed
- `pytest -q tests/test_dev_tools.py::test_doctor_and_native_host_report_surface_latest_overflow_summary -vv`: passed
- `pytest -q tests/test_dev_tools.py::test_doctor_script_reports_manifest_and_wrapper -vv`: passed
- `python -m py_compile daemon/src/glassttyd/*.py scripts/*.py`: passed
- `npm run typecheck`: passed
- `npm run build`: passed
- direct temp-home proof: `overflow-report` showed 4 artifacts before prune
- direct temp-home proof: `overflow-prune --keep 1 --max-disk-bytes 2000` planned 3 deletions
- direct temp-home proof: `overflow-prune --keep 1 --max-disk-bytes 2000 --apply` deleted 3 artifacts and preserved the latest linked spill artifact
- direct temp-home proof: `doctor.py` showed an `overflow-prune` hint before cleanup and no prune hint after cleanup
- direct temp-home proof: `native-host-report.py` surfaced the same before/after overflow inventory counts
- `python scripts/verify-package.py /mnt/data/GlassTTY-rev0088-2026.03.17.11.00-overflowprune-retention-inventory-spurwing.zip`: passed

Honest gap: no live Chromium/native-host/browser round-trip was proven in this container.
