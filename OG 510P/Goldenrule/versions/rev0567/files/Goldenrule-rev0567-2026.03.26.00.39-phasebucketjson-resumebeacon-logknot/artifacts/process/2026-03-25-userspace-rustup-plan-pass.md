# 2026-03-25 — userspace rustup comeback plan pass

## Why this pass existed

The archive already knew that a repo-local `rustup` detour was plausible on a later egress-capable machine, but it still left the actual command sequence split across prose and memory. That is fragile in exactly the kind of handoff this program expects.

## What changed

- added `scripts/tools/plan_userspace_rustup_comeback.py`
- added `scripts/report/build_cloudtainer_userspace_rustup_plan.py`
- added `scripts/test/check_cloudtainer_userspace_rustup_plan.py`
- generated `docs/CLOUDTAINER_USERSPACE_RUSTUP_PLAN.md`
- generated `artifacts/reports/cloudtainer_userspace_rustup_plan.json`
- added `.local/` to `.gitignore`
- extended `docs/CLOUDTAINER_USERSPACE_RUSTUP_DETOUR.md`
- extended `docs/RESEARCH_SOURCES.md` with `RS-GR-560` and `RS-GR-561`
- threaded the new lane through `Makefile`, `README.md`, `docs/README.md`, `docs/ENVIRONMENT_SANDWORM.md`, `scripts/test/check_generated_docs_presence.py`, and refreshed the command / validator inventories

## Practical result

Future inheritors now have one exact later-machine lane:
1. export repo-local `CARGO_HOME`, `RUSTUP_HOME`, and `CARGO_TARGET_DIR`
2. bootstrap `rustup` without selecting a default toolchain yet
3. install the repo-pinned `stable` toolchain under `minimal` plus additive `rustfmt`
4. run `cargo fetch --locked` while HTTPS egress still exists
5. take the standing smallest Rust witness (`probe_run` quick foothold)
6. prune `.local/cargo`, `.local/rustup`, and `.local/target` before the next retained archive cut

## Local validation

- `make show-cloudtainer-userspace-rustup-plan`
- `make test-cloudtainer-userspace-rustup-plan`
- `make test-generated-docs`
- `make test-command-inventory`
- `make test-validator-inventory`
- `python3 -m py_compile scripts/tools/plan_userspace_rustup_comeback.py scripts/report/build_cloudtainer_userspace_rustup_plan.py scripts/test/check_cloudtainer_userspace_rustup_plan.py`
- `python3 scripts/test/check_markdown_links.py README.md docs/README.md docs/ENVIRONMENT_SANDWORM.md docs/CLOUDTAINER_USERSPACE_RUSTUP_DETOUR.md docs/CLOUDTAINER_USERSPACE_RUSTUP_PLAN.md`
