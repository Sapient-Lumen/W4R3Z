# rev0087 focused validation

- `pytest -q tests/test_cli.py`: pass
- `pytest -q tests/test_dev_tools.py`: pass
- `pytest -q tests/test_native_host.py`: pass
- `npm run typecheck`: pass
- `npm run build`: pass
- direct `python -m glassttyd.cli overflow-report`: pass (artifact found, full message omitted by default)
- direct `python -m glassttyd.cli overflow-report --include-message`: pass
- `python scripts/doctor.py --pretty` overflow visibility: pass
- `python scripts/native-host-report.py --pretty` overflow visibility: pass
- `python scripts/verify-package.py /mnt/data/GlassTTY-rev0087-2026.03.17.10.19-nativeoverflowreport-hostsignal-operatorsight-whimbrel.zip --pretty`: pass

Honest gap: no live Chromium/native-host/browser round-trip was proven in this container.
