# rust-android-mobile-kit

Fixture pack for **P-0168 Rust Android Mobile Kit**.

The first implementation should revolve around a compact `androidbundle.zip` and a few reviewable reports rather than a giant generated Android project.

## Core review objects

- **ABI coverage** — which Android ABIs/API levels were declared versus actually built.
- **Load doctor** — whether packaging/layout/runtime-library facts create likely integration or collision risk.
- **Page-size compatibility** — whether native outputs are plausibly ready for modern Android 16 KB page-size requirements.

## Core schemas in this fixture pack

- `artifact-schema.json` — top-level bundle metadata stub
- `abi-coverage.report.schema.json`
- `load-doctor.report.schema.json`
- `page-size-compat.report.schema.json`

## Scenario families

- `scenarios/aar_native_library_collision_requires_policy/`
- `scenarios/page_size_16kb_release_gate/`
- `scenarios/uniffi_kotlin_bindings_need_packaging_honesty/`

Future passes should keep this fixture pack scoped to **library shipping / packaging / readiness evidence** and avoid turning it into a full Android build system or UI framework.
