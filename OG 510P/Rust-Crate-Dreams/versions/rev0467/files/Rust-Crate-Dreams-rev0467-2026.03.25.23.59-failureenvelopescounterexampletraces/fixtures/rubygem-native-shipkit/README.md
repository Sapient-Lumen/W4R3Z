# RubyGems Native Extension ShipKit fixtures

This fixture pack now treats three review objects as first-class:

1. **platform coverage** — which binary gems actually exist and where source-build fallback still applies;
2. **resolver route** — whether Bundler/RubyGems will actually take the route the support story implies;
3. **extension residency** — whether copied `lib/` artifacts, require stubs, shared-library basenames, and runtime load expectations still agree.

Core schemas:
- `platform-coverage.report.schema.json`
- `resolver-route.report.schema.json`
- `extension-residency.report.schema.json`
- `release.receipt.schema.json`
- `runtime-support.schema.json`

Scenario families:
- clean fat-gem matrix with aligned gemspec/platform metadata
- source-build-only native gem with no binary artifacts
- hybrid release where some platforms use binary gems and others fall back to source build
- README/runtime claims that exceed observed MRI/JRuby/TruffleRuby route evidence
- lockfile/platform route drift that hides real multi-platform install behavior
- gemspec platform or packaged extension path/name drift
- publish-identity posture that does not match the release recipe
