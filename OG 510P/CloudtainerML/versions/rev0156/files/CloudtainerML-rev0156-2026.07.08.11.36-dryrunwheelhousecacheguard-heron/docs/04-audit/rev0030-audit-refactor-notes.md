# rev0030 audit/refactor notes

- Added `tools/spectral_operator_report.py`.
- Updated `tools/operator_route_report.py` family hints to include expert-choice, copy-head, GBLA, and confidence-adaptive probes.
- Updated `tools/native_probe_audit.py` to map five new C++ probes to stable smoke artifact names.
- Updated `tools/smoke_validate.py` to require the spectral operator report.
- Carried forward rev0029 native smoke artifacts as explicit continuity artifacts and generated five fresh rev0030 native outputs.
