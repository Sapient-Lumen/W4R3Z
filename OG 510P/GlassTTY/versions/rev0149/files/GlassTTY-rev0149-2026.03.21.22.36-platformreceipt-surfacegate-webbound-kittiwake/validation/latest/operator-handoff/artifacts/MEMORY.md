## rev0119 memory

- rev0118 made setup failures legible, but future sessions still had to infer the *environment* behind those failures and manually translate that into a next command.
- rev0119 closes that gap by recording a compact setup environment fingerprint (browser family, Playwright cache alignment, profile/playwright roots, required native-host targets) and a derived `recommended_next_action` in the smoke ledger/summary.
- `scripts/e2e_fixturelab_capture.py` now surfaces those fields in the summarized latest-smoke view, and `scripts/doctor.py` threads the recommended command straight into latest-smoke hints for setup-stage failures.
- Focused proof for this revision lives under `validation/rev0119-focused/`, especially `pytest-e2e-setup-guidance.txt`, `pytest-capture.txt`, `doctor-pretty.txt`, `typecheck.txt`, `build.txt`, and `setup-artifact-sample/`.
- Future sessions should start with `STATUS.md`, `docs/handoff-rev0119-2026-03-19.md`, `docs/research-notes-2026-03-18.md`, and `validation/rev0119-focused/`.
