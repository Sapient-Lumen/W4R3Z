# rev0115 focused validation

## Passed here

- `PYTHONPATH=daemon/src pytest -q tests/test_e2e_fixturelab.py::test_playwright_extension_launch_plan_falls_back_to_bundled_executable_when_cache_name_drifts tests/test_e2e_fixturelab.py::test_playwright_extension_launch_plan_prefers_repair_then_sync_command_when_cache_repair_exists`
  - result: `2 passed`
- `PYTHONPATH=daemon/src pytest -vv tests/test_playwright_browsers.py::test_playwright_browsers_script_import_archive_and_inspect`
  - result: `1 passed`
- `PYTHONPATH=daemon/src pytest -vv tests/test_dev_tools.py::test_doctor_hints_playwright_channel_alignment_when_cache_name_drifts`
  - result: `1 passed`
- `npm run typecheck`
  - result: passed
- `npm run build`
  - result: passed
- `python scripts/doctor.py --pretty`
  - result: passed

## What changed

- GlassTTY now exposes whether the Playwright persistent extension lane is actually `channel_ready`.
- Drifted-cache fallback reports now include a reason plus explicit recovery commands, including a channel-ready command chain when cache repair should precede sync.
- `playwright-browsers.py inspect` now embeds the same launch-plan guidance that `doctor.py` uses, so cache archaeology and operator hints agree.

## Extra artifacts

- `playwright-inspect-drifted.json` shows a synthetic drifted cache where the launch plan reports `cache_alignment_status: "cache-install-name-drift"` and a concrete `recommended_channel_ready_command`.
- `doctor-drifted-cache.json` shows the matching doctor hints for that same synthetic cache.

## Honest limits

- No fresh live browser/native-messaging round-trip is claimed here.
- The drifted-cache JSON artifacts use a temporary cache root, so the captured repair command is intentionally environment-specific.
- No broad full-suite claim is made for this revision.
