# Epic crate evidence-interchange doctrine — 2026-03-25

This note answers a practical question the archive had still not made explicit enough:

**If a worthy crate emits packets, how do those packets become a stable contract that other tools and teams can actually exchange?**

## Main judgment

A worthy crate should usually **not** stop at “export JSON”.
It should ship a **versioned evidence-interchange contract**.

That means:
- a stable reviewed bundle,
- a separate raw receipt stream,
- named receiver profiles,
- a verifier,
- and a compatibility story.

## Default receiver profiles

Use a bounded profile vocabulary unless a lane has a better domain-specific version:

1. **explore** — lightweight basis, fast iteration, high unknown tolerance
2. **ci-minimal** — reproducible enough for normal CI reuse and review
3. **enterprise-offline** — portable bundles with explicit mirror/offline basis
4. **safety-qualified** — profile with extra qualification artifacts and lower tolerance for unverifiable gaps

Profiles should be explicit inputs to claim generation and explicit outputs in the reviewed bundle.

## Default interchange artifact family

A strong first evidence-interchange kit usually includes:

### A. `profile-manifest.json`
This says:
- which receiver posture is in scope,
- required dimensions,
- minimum claim tiers,
- accepted import routes,
- and downgrade / expiry behavior.

### B. `exchange-bundle.json`
This is the compact reviewed artifact.
It should summarize:
- profile,
- dimensions,
- claim tiers,
- basis pointers,
- schema version,
- compatibility requirements,
- and refusal / unknown / degraded states.

### C. `receipt-stream.jsonl`
This is the append-only raw evidence stream.
It should contain:
- local probe receipts,
- hosted import events,
- mirror/registry observations,
- and failures or degraded attempts.

### D. `support-summary.md`
This is the short human-facing sheet.
It should explain:
- what the bundle claims,
- what was imported versus replayed,
- what profile is in force,
- and what stays outside scope.

### E. `bundle-diff.json`
This is the machine-readable change surface.
It should say:
- what profile changed,
- what dimensions changed,
- whether basis moved,
- and whether human review is required.

### F. `bundle-verify.json`
This is the verifier result.
It should say:
- schema validity,
- profile compatibility,
- basis freshness and compatibility checks,
- imported-surface parse success,
- and downgrade/refusal reasons when verification fails.

## Interchange doctrine

### 1. Separate reviewed bundles from raw receipts
Do not ask downstream tools to infer a stable claim from a loose pile of logs.

### 2. Version the contract, not just the code
Schema compatibility must be explicit enough that an old bundle can be parsed, rejected, or downgraded intentionally.

### 3. Keep profile semantics stable
If “enterprise-offline” or “safety-qualified” changes meaning every quarter, the bundle is not a contract.

### 4. Point back to imported substrate
The bundle should carry basis pointers and imported-surface identifiers rather than pretending to be the substrate itself.

### 5. Expose refusal and downgrade paths
A verifier should be allowed to say:
- unsupported profile,
- stale basis,
- incompatible schema,
- missing imported surface,
- or refused domain qualification.

### 6. Keep policy overlays above universal core meaning
The core bundle should be reusable across teams.
Organization-specific policy logic should sit in overlays, not in the universal schema.

## Release doctrine

### Honest `0.1`
Ship:
- one stable bundle schema,
- one profile vocabulary with at most a few profiles,
- one verifier command/library,
- one reviewed bundle,
- one raw receipt stream,
- and explicit downgrade/refusal states.

Do **not** ship at `0.1`:
- giant profile taxonomies,
- bespoke adapters for every ecosystem surface,
- fake backward-compatibility promises,
- or qualification rhetoric without extra artifacts.

### Strong `0.3`
Add:
- bundle diffing,
- stronger import adapters,
- schema evolution notes,
- compatibility testing across versions,
- and reusable policy overlays.

### Real `1.0`
Usually means:
- schema evolution policy is explicit,
- profile meanings are stable,
- verifier behavior is stable,
- and human handoff semantics actually match machine interchange semantics.

## Anti-patterns

### Anti-pattern 1 — local JSON with no contract
Symptoms:
- one CLI dumps JSON,
- no version field,
- no verifier,
- no compatibility note.

### Anti-pattern 2 — reviewed and raw collapsed together
Symptoms:
- probe failures mixed directly into support claims,
- no stable place for human review,
- no downgrade rules.

### Anti-pattern 3 — profile theater
Symptoms:
- “enterprise”, “offline”, or “safety” badges,
- but no manifest, no extra artifacts, no verifier behavior.

### Anti-pattern 4 — every lane invents its own packet universe
Symptoms:
- similar bundles with different field names,
- duplicate profile semantics,
- incompatible verifier logic,
- needless translation work across tools.

## Practical archive rule after this pass

When planning a top-lane crate, the archive should now answer:
1. what profile vocabulary it uses,
2. what reviewed bundle it exports,
3. what raw receipt stream sits beneath it,
4. what verifier checks it provides,
5. how schema/version compatibility works,
6. and what downgrade/refusal paths are explicit.

If the pass cannot answer those questions, the lane is still underplanned.
