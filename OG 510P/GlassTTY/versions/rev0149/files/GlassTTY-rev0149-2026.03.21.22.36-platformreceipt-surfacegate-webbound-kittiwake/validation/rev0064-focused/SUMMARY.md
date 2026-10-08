# rev0064 focused validation summary

- extension typecheck: passed (`extension-typecheck.txt`)
- extension build: passed (`extension-build.txt`)
- deterministic receiver inventory / priming / content-script experiment checks: passed
- focused pytest bundle: passed (`pytest-focus.txt`)
- direct comparator checks: passed, including the new count-only mismatch fixture (`compare-coverage-experiments.txt`)
- doctor and native-message-budget direct runs: passed
- packaged rev0064 zip verified successfully with the stricter manifest/HTML reference checks (`package-release.txt`, `verify-package.txt`)

Still unproven here: no live Chromium/native-messaging/browser acceptance pass was captured in this container.
