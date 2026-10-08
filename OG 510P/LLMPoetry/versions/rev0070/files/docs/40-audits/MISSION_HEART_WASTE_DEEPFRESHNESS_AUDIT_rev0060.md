# Mission Heart / Drift-Waste / Deep-Freshness Audit — rev0060

Current head: `P0002-D028`  
Current draft: `poems/P0002/draft_028.md`  
Current packet: `poems/P0002/material/source_material_packet_028.json`  
Artifact target: `LLMPoetry-rev0060-2026.06.17.23.59-missionheart-driftwaste-deepfreshness-hardwater.zip`  
Research pulse: `RP-0052`

## Heart of the mission

LLMPoetry is not mainly a poem folder. It is an adversarial, disclosure-honest poetry office: a datacube where machine participation, source pressure, branching, judgment latency, and release state are not hidden around the poem but made part of what the poem must survive.

The target is not “write like a human.” The target is: **make poems whose value survives disclosure that they were machine-drafted, whose procedures are replayable, and whose pressure cannot be replaced by a generic workshop prompt without losing the work.**

The strongest internal formulation remains the rev0023 mission-heart question: what can a poem become when branching, receipts, selectors, source traces, state transitions, and disclosure are necessary to reading rather than excuses around weak lines?

## What is missing

1. **External disclosed-reader evidence.** P0002-D010 has candidate-reader machinery, but it remains preserved rather than run. P0002-D028 is same-turn unjudged. Internal cold review is useful, but it is not C1/C2 reader evidence.
2. **A single canonical current-state source.** Many mirrors are useful for resumability, but current-facing files drift. The reader/operator needs one generated source of truth and generated mirrors, not hand-maintained quasi-identical surfaces.
3. **Deep freshness validation.** The existing validator and doctor passed while root and descriptor surfaces still pointed to D022/D023/D027/rev0023/rev0058 in current-facing fields. Rev0060 adds `tools/check_deep_surface_consistency.py` to block that class.
4. **A pruning economy.** The office has accumulated powerful receipts, but every new gate should state the failure it prevents, the old surface it supersedes, and the future deletion/deprecation target.
5. **Publication-grade metadata or honest “lite” metadata.** RO-Crate/Croissant/DataPackage/CITATION surfaces are valuable only if they are fresh enough to preserve trust. Otherwise they should be marked as lite/nonconformant navigation aids.

## What went severely wrong

The severe fault is not byte bloat. It is **truth bloat**: enough surfaces existed that the validators could pass while current-facing instructions lied or lagged.

Concrete rev0059 faults found before this repair:

| Surface | Fault |
|---|---|
| `HUMAN_QUESTIONS.md` | Root mirror froze at rev0054 / P0002-D023 while the cube head was P0002-D028. |
| `FRONTIER_TICKET.json` | `frontier` still ordered cold review of P0002-D023; `web_pulse` and descriptor fields lagged. |
| `REENTRY_CONTRACT.json` | `contract` still resumed at P0002-D022. |
| `DATA_CARD.json` | descriptor date/version/prose lagged at rev0058/D027. |
| `docs/10-method/DATACUBE_DATA_CARD.md` | still said “As of rev0023” and described only P0001/D001-D010. |
| `pyproject.toml` / `sbom-lite.json` | still advertised rev0023 and P0001 as current scaffolding. |
| `poems/P0002/metadata.json` / `poems/P0002/INDEX.json` | top current metrics/summary/draft list lagged D027 or turn 50 while current head was D028. |
| `ro-crate-metadata.json` / `codemeta.json` / `datapackage.json` | metadata mostly pointed current, but names/descriptions/resources still contained stale current prose. |

## Waste that can be corrected over time in this cloudtainer

- Exact duplicate boot cards are small in bytes but costly in cognition. They should become generated mirrors from one canonical YAML/JSON current-state object.
- Release descriptors should be either validated as real publication surfaces or explicitly demoted to “lite navigation surfaces.”
- Preserved D010 reader machinery should be used or demoted. Carrying reader-proof infrastructure without readers is a recurring credibility cost.
- P0002 reanchors from D011-D028 may be a productive failure-search, but they need a stop rule: after D028 cold review, either promote a disclosed-reader packet, prune the line, or start a new wager.
- New validators should be admitted only with a named prior failure and should include a deletion/merge candidate.

## Rev0060 changes

- Adds this audit: `docs/40-audits/MISSION_HEART_WASTE_DEEPFRESHNESS_AUDIT_rev0060.md`.
- Adds machine-readable report: `reports/mission_heart_waste_deepfreshness_audit_rev0060.json`.
- Adds `tools/check_deep_surface_consistency.py` and wires it into the main validator, doctor, Makefile, and validation manifest.
- Refreshes current-facing compact surfaces to `rev0060` / `P0002-D028` / `RP-0052`.
- Repairs stale root human question and method data card surfaces.
- Repairs descriptor and P0002 metadata/index current fields without creating D029 and without judging/promoting D028.

## Required next action

Later-turn cold review of P0002-D028 using rev0060 deep-surface gate; no D029 before review unless explicitly justified and logged.

## Non-claim

Rev0060 is an audit/repair revision, not a D028 cold review or quality promotion. P0002-D028 remains same-turn unjudged; no admission, evidence-ready status, anthology candidacy, reader response, or live NOAA value is claimed.
