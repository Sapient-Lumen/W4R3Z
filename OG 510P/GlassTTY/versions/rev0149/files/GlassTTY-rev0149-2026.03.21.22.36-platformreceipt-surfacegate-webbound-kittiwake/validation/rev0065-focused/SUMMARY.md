# GlassTTY validation summary

- overall_ok: True
- note: direct focused validation bundle; the full validate-release wrapper again terminated early in this container before writing its own summary

| step | ok | detail |
|---|---:|---|
| extension_typecheck | yes | npm --prefix extension run typecheck |
| extension_build | yes | npm --prefix extension run build |
| pytest_focus | yes | PYTHONPATH=daemon/src python -m pytest -q tests/test_package_release.py tests/test_validate_release.py tests/test_cli.py |
| package_release | yes | bash scripts/package-release.sh "$PWD" validation/rev0065-focused/package-check.zip |
| verify_package | yes | python scripts/verify-package.py validation/rev0065-focused/package-check.zip --pretty |
