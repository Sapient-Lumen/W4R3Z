# wasm-component-artifact-conformance-kit

Fixture pack for **P-0206 Wasm Component Contract & Conformance ShipKit**.

The first implementation should revolve around a compact `componentbundle.zip` and a few reviewable reports rather than a giant new Wasm platform.

## Core review objects

- **Tooling lineage** — which build/composition path actually produced the component.
- **World lock** — what exact package/world/interface/version contract the component carries.
- **Composition closure** — whether the component is actually closed and runnable or still depends on host/composition context.

## Core schemas in this fixture pack

- `tooling-lineage.report.schema.json`
- `world-lock.report.schema.json`
- `composition-closure.report.schema.json`

## Scenario families

- `scenarios/cargo_component_transitional_build_repacked_with_wac/`
- `scenarios/package_version_inference_breaks_interface_match/`
- `scenarios/native_wasip2_component_still_requires_host_supplied_imports/`

Future passes should keep this fixture pack scoped to **contract truth above native tooling, WIT versioning, and composition closure** and avoid turning it into a full Wasm runtime or registry platform.
