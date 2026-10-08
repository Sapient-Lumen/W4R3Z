# Rebuild-indexes subprocess refresh audit — rev0839

This audit records a concrete cloudtainer reliability refactor: content-derived material surfaces are refreshed through isolated child Python processes instead of being imported into one long-lived `rebuild_indexes.py` interpreter.

- Status: `material_surface_refresh_uses_subprocess_isolation`
- Script: `scripts/rebuild_indexes.py`
- Script SHA-256: `c1d8c6e57fc3386e2a3a8a98c35d1b104d6144cca872916f8930662380f0132d`

## Required subprocess-refresh snippets

- `import subprocess` — present
- `def run_material_builder_subprocess` — present
- `env = os.environ.copy()` — present
- `env["PYTHONDONTWRITEBYTECODE"] = "1"` — present
- `env["PYTHONUNBUFFERED"] = "1"` — present
- `subprocess.run([sys.executable, "-u", str(script)]` — present
- `cwd=ROOT` — present
- `check=False` — present
- `returned non-zero status` — present

## Required material-surface builders

- `build_asset_indexes.py` — present
- `build_release_refresh_asset_index_audit_rev0834.py` — present
- `build_upstream_retention_coverage.py` — present
- `build_absolute_path_reference_audit.py` — present
- `build_path_reference_shape_audit.py` — present
- `build_external_license_evidence_candidates_rev0834.py` — present
- `build_rights_evidence_scan.py` — present
- `build_license_reference_integrity_audit.py` — present
- `build_rights_readiness.py` — present
- `build_publication_rights_gate_audit_rev0837.py` — present
- `build_publication_entrypoint_rights_gate_audit_rev0838.py` — present
- `build_publication_state_transition_rights_gate_audit_rev0839.py` — present
- `build_publication_preflight_dry_run_safety_audit_rev0840.py` — present

## Forbidden stale in-process refresh patterns

- none present in `refresh_cycle_safe_material_surfaces()`

## Rationale

The prior in-process refresh path made a long refresh harder to diagnose and could hang at interpreter shutdown after many builder imports. Subprocess isolation mirrors the existing command-runner policy: each builder gets a clean interpreter, unbuffered progress output, and bytecode suppression.
