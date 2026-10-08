# MTGSim rev0189 — Mission Freshness Waste Cut

## Heart of the mission

MTGSim should not be judged first by how many printed cards it can name. Its useful center is stricter: given one canonical state and one explicit legal choice, produce a deterministic next state plus typed evidence that can be validated, replayed, branched, fuzzed, searched, explained, and audited after transient game objects disappear.

That means the durable product is the transition receipt. Cards, rules rows, search policies, and AI adapters are consumers of that receipt, not replacements for it. The cube is strongest when every risky Magic seam leaves a small, typed witness: target set hashes, APNAP queue seals, payment spans, stack-resolution backlinks, state checkpoints, and canonical action/choice schemas.

## What is missing

1. **Rules-source freshness as a hard invariant.** The package observed the public 2026-06-19 Comprehensive Rules, but the packaged manifest and ledger still pointed their source dates at 2026-04-17. rev0189 reconciles the metadata, but a private diff workflow is still missing; no semantic behavior should be inferred from a date refresh alone.
2. **Card-data ingestion boundaries.** The current catalog is intentionally tiny. The next importer should distinguish `parsed`, `known card text`, `semantically implemented`, `tested`, and `fuzz-covered`; imported text must not count as implemented behavior.
3. **Interactive transaction kernels.** Replacement/prevention choices, APNAP ordering, target/mode choice, and cost/payment witnesses are present in seams, but they still need modular transaction engines that can serve both gameplay and search.
4. **Agent/search API.** The project already has action traces and page/queue evidence. It still needs a stable observation/action-mask interface, chance/hidden-information boundaries, and value/reward hooks so external search or RL systems do not scrape internals.
5. **Monolith split.** `src/engine.cpp`, `src/validation.cpp`, `tests/cpp/test_engine.cpp`, and `tools/audit_datacube.py` have become useful but heavy seams. Split by transaction family and validator family over time without weakening the audit probes.

## What should change

- Treat official rules-source freshness as a release-check input. A package may keep official text unbundled, but its manifest and ledger date should not lag the latest observed source.
- Keep the public claim humble: the ledger can be about 95% complete while the conservative full-rules proxy remains much lower. User-facing status should show both signals.
- Move from breadth-first card scripting to evidence-first rule kernels: replacement/APNAP/payment/targeting before hundreds of additional card names.
- Add importer completeness gates before large card-data expansion.
- Make linked zips carry current curated evidence, not every historical generated report from the cloud container.

## What went severely wrong or wasteful

The largest correctable waste is report accretion. In the incoming rev0188 zip, `reports/` accounted for roughly 110 MB raw and 11.5 MB compressed, more than 90% of the compressed artifact. Much of that was historical per-revision JSON, stdout mirrors, XML, JSONL histories, and SQLite metrics that are useful locally but create stale-truth surfaces when copied forward.

A second problem was contradictory freshness evidence: `latest_online_observation` knew the public Comprehensive Rules were effective 2026-06-19, while the source manifest and rule ledger still declared 2026-04-17. That is small technically but dangerous culturally: the cube should never let an old source date look authoritative just because tests pass.

A third problem was audit wording: the package was clean, but rev-specific audit artifacts still remembered build/cache warnings from the working cloud container. That should be framed as local preflight evidence, not package truth.

## rev0189 correction

- Refreshes `data/rules/official/manifest.json` and `data/rules/coverage/rules_ledger.json` to the observed 2026-06-19 Comprehensive Rules source date.
- Adds this mission/freshness/waste note as an explicit architectural handoff.
- Updates package curation so linked revisions exclude build/cache payloads, private official-rules caches, stale per-revision report dumps, stdout/JUnit mirrors, JSONL histories, and SQLite metric stores.
- Preserves current/curated reports and source evidence needed for auditability.

## Validation snapshot

Release build and full harness were rerun for the source tree during the rev0189 session: C++ release tests 352/352, scenarios 93/93, broad fuzz 12/12, risk-seam fuzz 8/8, rule coverage 0 errors / 0 warnings, and package/audit hygiene checked after stale report curation.
