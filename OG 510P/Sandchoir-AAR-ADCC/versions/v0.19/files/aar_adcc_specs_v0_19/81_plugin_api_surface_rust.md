# 81 — Plugin API Surface (Rust) (v0.19)

Kernel stays stable/small. Evolution happens via plugins and config (CFG#).

## 1) Plugin categories
### AAR policy plugin
- scores candidates for HOT/ROLE/DISCOVERY
- may suggest ordering, but cannot violate invariants

### JSON repair plugin
- `repair_ctrljson(bytes)->bytes|error`
- kernel validates with schema after repair

### Verifier registry/execution plugin
- lists verifiers
- runs verifiers under budgets
- returns E# summaries + ledger pointers + cache keys

### Telemetry exporter plugin
- emits JSONL and/or OpenTelemetry (optional)
- no state mutation

## 2) Trait sketches (conceptual)
- `AarPolicy::score_item(item, ctx)->i64`
- `AarPolicy::choose_exploration(cands, ctx)->Option<ID>`
- `JsonRepair::repair(input)->Result<String, RepairError>`
- `Verifier::run(name, params, timeout)->EvidenceResult`
- `TelemetrySink::emit(event)`

## 3) Capability gating
Plugins declare flags; kernel checks before enabling:
- `supports_token_estimation`
- `supports_schema_constrained_decoding`
- `supports_exec_lane`

## 4) Configuration
CFG# proposals apply to plugin configs and kernel knobs.
Kernel records before/after hashes and cursor.

## 5) Testing
Plugins must be golden-testable (61_):
- same input → same output
- no hidden nondeterminism in scoring/repair
