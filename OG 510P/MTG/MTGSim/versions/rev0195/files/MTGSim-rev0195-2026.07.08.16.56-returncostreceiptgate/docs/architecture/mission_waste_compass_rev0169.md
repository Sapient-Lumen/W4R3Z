# MTGSim rev0169 — Mission Waste Compass

## Status

This is a deep-read / package-hygiene revision. It does not claim a new Magic rules semantic feature. It records the mission spine, the gaps that matter most, the waste that should stop compounding, and one small corrective tool: `tools/package_revision.py`, a filename-disciplined packager for linked revision artifacts.

## Heart of the mission

MTGSim is not merely trying to be another way to play Magic. The heart is a **trusted transition kernel**:

```text
canonical state + explicit legal choice -> deterministic next state + typed evidence
```

The real product is the evidence spine. Every state transition should be replayable, challengeable, fuzzable, searchable, and safe for future agents to inspect without relying on vague logs, hidden side effects, or English-only explanations. The recent paid-action journal work is consistent with this: it keeps moving inward from "the action succeeded" toward exact declarations, choice locks, cost plans, rollback receipts, row hashes, and sequence bounds.

That mission is distinct from broad community engines such as Forge or XMage. Those projects optimize for playable rules enforcement across many cards and formats. MTGSim should stay focused on audit-grade transitions first, then grow card coverage through typed data and fixtures only where the proof surface stays honest.

## What is missing

1. **Rules source refresh as a first-class diff gate.** The local ledger remains pinned to an older metadata source while the online official Comprehensive Rules TXT observed during this session is effective 2026-06-19. The project has correctly avoided bundling official rules text, but it still needs a deliberate private-fetch -> metadata-index -> diff -> ledger-update flow.
2. **A reusable paid-action cost-plan kernel.** Casts, activated abilities, loyalty abilities, and later special actions still need a single shared transaction body that locks total costs, mode/target/X choices, nonmana payment order, mana plans, rollback reason, and final receipt emission.
3. **Replay-bundle attachment for paid-action journals.** A journal can now be internally sequence-safe, but it is still not attached to the replay bundle manifest as a required companion artifact.
4. **A real card-data ingestion boundary.** The sample catalog proves the schema path, not card-scale coverage. The next safe ingestion layer should treat Scryfall/MTGJSON-style data as card-data input, not as semantic authority.
5. **Replacement/trigger/APNAP transaction surfaces.** The existing evidence model has many good records, but simultaneous choice/replacement ordering remains a long-term source of trust risk unless choices become first-class declared transactions.
6. **A minimization and search harness.** The fuzz harness finds risk seams, but the project still wants automatic counterexample shrinking and replay-bundle emission for each new invariant failure.
7. **Monolith decomposition.** `src/engine.cpp`, `tests/cpp/test_engine.cpp`, `src/validation.cpp`, and `tools/audit_datacube.py` are doing too much. Splitting them by proven subsystem would reduce compile cost and review risk.

## What has gone wrong or wasteful

The severe problem is not a failing test today. The severe problem is **artifact drift around a trust project**.

- `reports/package/zip_integrity_latest.txt` in the incoming datacube pointed at rev0167 even though rev0168 had a dedicated package-integrity report. A mutable `latest` alias that lies is worse than no alias in a project whose thesis is evidence integrity.
- The package carries a large report payload. In the working tree inspected during this session, reports were roughly 70 MB uncompressed, dominated by harness, audit, and rules report history. This is useful as lineage, but wasteful every turn unless there is a retention rule.
- Coverage messaging can mislead. The rules progress report says the ledger is about 94.9% weighted by local ledger units, while the same report's conservative full-rules percentage is about 7.25%. Both can be true; only one sounds like broad rules coverage. Future reports should display both together and label the ledger-weighted figure as local-scope coverage.
- The README and changelog have become release-ledger storage. They are useful, but too much high-frequency lineage in the front door makes the mission harder to see.
- Packaging was still too manual. The project had audits that detect build/cache payloads, but no single committed helper that makes the filename convention and exclusions repeatable.

## Corrective change in this revision

`tools/package_revision.py` now packages a linked revision with a stable root name, excludes build outputs and cache payloads, writes `reports/package/zip_integrity_<rev>.txt`, refreshes `reports/package/zip_integrity_latest.txt`, verifies the zip, and emits a SHA-256 sidecar.

This is intentionally small. It does not replace the audit harness. It makes the recurring packaging step harder to get subtly wrong.

## Recommended next slices

1. **rev0170 candidate: Rules Source Refresh Diff Gate.** Use private local fetches of the current official TXT/PDF, extract metadata-only rule IDs and paragraph hashes, diff against the 2026-04-17 ledger basis, and update the ledger without redistributing official rules text.
2. **rev0171 candidate: Replay Manifest Journal Attachment.** Make paid-action journal verification a replay-bundle manifest requirement, not an optional CLI side artifact.
3. **rev0172 candidate: Report Retention Contract.** Keep current reports plus compact JSONL history; move bulky per-revision harness/audit/rules dumps to opt-in evidence bundles.
4. **rev0173 candidate: Cost-Plan Kernel Extraction.** Promote declaration/cost/payment/rollback/receipt machinery into a shared kernel used by casts and abilities.

## Speculation

My read is that MTGSim is converging on something closer to a proof-carrying game reducer than a conventional rules engine. That is the right weird shape. Magic is too large and exception-heavy to make "we support many cards" an honest early milestone. A narrower kernel that can prove every mutation is more valuable: once the proof surface is stable, card-scale importing and agent search have something solid to stand on.

The project should resist vanity coverage and resist storing every bulky artifact in every linked revision. The durable asset is not the pile of reports; it is the invariant that a linked revision can tell a future reader exactly what changed, why it matters, what evidence backs it, and what risk remains.
