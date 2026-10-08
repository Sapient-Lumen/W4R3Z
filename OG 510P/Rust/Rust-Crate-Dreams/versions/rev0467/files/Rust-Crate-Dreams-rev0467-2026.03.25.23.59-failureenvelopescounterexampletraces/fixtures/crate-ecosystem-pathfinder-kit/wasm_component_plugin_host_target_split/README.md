# Scenario stub — Wasm component/plugin host-target split

Decision question:
> Which crates should a team choose for a Wasm component or plugin stack without confusing build target, runtime host, and docs visibility?

This scenario exists because Wasm Components are a current Rust flagship area, but support claims here are highly sensitive to target choice, binding generation, and host runtime assumptions.

## Roles to fill
- component / binding generation
- host integration
- packaging / transport
- target support / docs surface
- testing / preview support

## Expected artifacts
- `host-target-route.report.json`
- `support-visibility.report.json`
- `decision-brief.md`
- `starter-set.bundle.json`
- `manual-review.note.md`

## Guardrail
Do not treat docs.rs visibility or compile success as proof of full runtime compatibility.
