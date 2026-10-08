# GlassTTY rev0067 focused validation

- timestamp: 2026-03-16T17:56:30Z
- overall_ok: True
- complete: True
- mode: focused-manual-validation
- interrupted_wrapper_proof: validation/rev0067-interrupted/

| step | ok | returncode | artifact |
|---|---:|---:|---|
| extension_typecheck | yes | 0 | validation/rev0067-focused/extension_typecheck.stdout.txt |
| extension_build | yes | 0 | validation/rev0067-focused/extension_build.stdout.txt |
| pytest_validate_release | yes | 0 | validation/rev0067-focused/pytest_validate_release.stdout.txt |
| pytest_cli | yes | 0 | validation/rev0067-focused/pytest_cli.stdout.txt |
| manual_package_checks | yes | 0 | validation/rev0067-focused/package_release_manual_checks.stdout.txt |
| package_release | yes | 0 | validation/rev0067-focused/package_release.stdout.txt |
| verify_package | yes | 0 | validation/rev0067-focused/verify_package.json |
