# REV0338 — latest-run health + fused stack-state verdict

This revision adds `vhk latest-run-health-json`, wires `bin/latest_run_health_json.sh` into the generated i3/X11 warm-runtime stack, and folds the newest-run health verdict into `bin/stack_state_json.sh` / `bin/stack_state.sh` so the control plane can answer whether the latest run looks safe to keep iterating on.

Highlights:
- added `vhk latest-run-health-json PROJECT_DIR`
- added generated `bin/latest_run_health_json.sh`
- extended generated `control-plane.json` with a `latest_run_health_json` observability helper
- extended generated `stack_state_json.sh` / `stack_state.sh` with latest-run health
- added `tests/test_latest_run_health_json_cli.py`
