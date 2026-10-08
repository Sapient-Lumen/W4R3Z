# Tranche Summary

This file is generated from `docs/TRANCHES.md`.

- total: 720
- completed: 720
- completion_percent: 100.00

| id | done | title |
|---|---|---|
| 1 | yes | Replace narrative operating contract with scientific contract (`AGENTS.md`). |
| 2 | yes | Establish deterministic make-based command surface (`Makefile`). |
| 3 | yes | Add doctor checks for toolchains and prerequisites. |
| 4 | yes | Add deterministic quick/full harness modes. |
| 5 | yes | Emit seed artifacts per harness mode. |
| 6 | yes | Emit timing artifacts per harness mode. |
| 7 | yes | Add artifact cleanup utility with safe defaults. |
| 8 | yes | Add process lifecycle control wrapper. |
| 9 | yes | Add process hygiene checks. |
| 10 | yes | Add async soak control and status checks. |
| 11 | yes | Add golden registry with validation. |
| 12 | yes | Add timing baseline under `goldens/`. |
| 13 | yes | Add spec ledger with schema and validator. |
| 14 | yes | Add ADR template/index/validator. |
| 15 | yes | Add CI smoke job with timing artifact upload. |
| 16 | yes | Add scientific execution roadmap (`docs/SCIENCE_PLAN.md`). |
| 17 | yes | Add scientific terminology policy (`candidate`/`adversary`). |
| 18 | yes | Migrate gauntlet default spec to adversary naming. |
| 19 | yes | Keep backward compatibility for legacy gauntlet keys. |
| 20 | yes | Migrate status output labels to scientific terms. |
| 21 | yes | Keep backward compatibility for legacy strategy directories. |
| 22 | yes | Add adversary strategy directory. |
| 23 | yes | Add adversary probe registry artifacts. |
| 24 | yes | Add noisy adversary probe registry artifacts. |
| 25 | yes | Add adversary probe suite artifact. |
| 26 | yes | Add adversarial-extortion technical note. |
| 27 | yes | Migrate AFK mission controller terminology. |
| 28 | yes | Keep AFK legacy artifact mirrors for compatibility. |
| 29 | yes | Route AFK Rust builds through `tools/rust_exec.sh`. |
| 30 | yes | Harden JuNest rust fallback setup in `rust_exec`. |
| 31 | yes | Add JuNest auto-repair for missing Rust packages. |
| 32 | yes | Add deterministic environment metadata recorder. |
| 33 | yes | Add timing regression checker against baselines. |
| 34 | yes | Add spec-ledger markdown rollup checker. |
| 35 | yes | Add release manifest generator with checksums. |
| 36 | yes | Add release hygiene checker script. |
| 37 | yes | Add security false-positive allowlist policy. |
| 38 | yes | Add allowlist expiration validator. |
| 39 | yes | Add repo-managed hooks (`pre-commit`, `pre-push`). |
| 40 | yes | Add hook installer script. |
| 41 | yes | Add audited hook bypass log writer. |
| 42 | yes | Add experimental protocol documentation. |
| 43 | yes | Add data management documentation. |
| 44 | yes | Add statistical practice documentation. |
| 45 | yes | Add release process documentation. |
| 46 | yes | Add changelog scaffold. |
| 47 | yes | Add control tests for governance/tooling checks. |
| 48 | yes | Wire tranche checks into `make gate`. |
| 49 | yes | Validate baseline (`make doctor`, `make test-quick`, `make gate`). |
| 50 | yes | Update `docs/AGENT_LOG.md` with tranche outcomes. |
| 51 | yes | Add formal methods posture documentation (`docs/FORMAL_METHODS.md`). |
| 52 | yes | Add solver-tool availability probe (`scripts/formal/check_formal_tooling.py`). |
| 53 | yes | Add deterministic certification invariant check (`scripts/formal/check_certify_invariants.py`). |
| 54 | yes | Add `make test-formal-smoke` target. |
| 55 | yes | Add `make test-formal-tools` target. |
| 56 | yes | Wire formal checks into integration gate. |
| 57 | yes | Add example corpus JSON validation (`scripts/test/check_examples_json.py`). |
| 58 | yes | Add `make test-examples-json` target. |
| 59 | yes | Wire example validation into integration gate. |
| 60 | yes | Add markdown link integrity validator (`scripts/test/check_markdown_links.py`). |
| 61 | yes | Add `make test-doc-links` target. |
| 62 | yes | Wire link integrity checks into integration gate. |
| 63 | yes | Add artifact layout validator (`scripts/test/check_artifact_layout.py`). |
| 64 | yes | Add `make test-artifact-layout` target. |
| 65 | yes | Add bypass-log structural validator (`scripts/test/check_bypass_log.py`). |
| 66 | yes | Add `make test-bypass-log` target. |
| 67 | yes | Add artifact policy linter for `.gitignore` (`scripts/test/check_gitignore_artifacts_policy.py`). |
| 68 | yes | Add `make test-gitignore-policy` target. |
| 69 | yes | Add spec target-date validator (`scripts/test/check_spec_dates.py`). |
| 70 | yes | Add `make test-spec-dates` target. |
| 71 | yes | Wire date-validation checks into integration gate. |
| 72 | yes | Expand ignored-artifact policy to include formal/release/report buckets. |
| 73 | yes | Add `artifacts/release/.gitkeep`. |
| 74 | yes | Add `artifacts/formal/.gitkeep`. |
| 75 | yes | Add `artifacts/reports/.gitkeep`. |
| 76 | yes | Integrate environment metadata capture into harness execution. |
| 77 | yes | Add experiment catalog generator (`scripts/report/build_experiment_catalog.py`). |
| 78 | yes | Add generated experiment catalog doc (`docs/EXPERIMENT_CATALOG.md`). |
| 79 | yes | Add experiment catalog artifact output (`artifacts/reports/experiment_catalog.json`). |
| 80 | yes | Add `make update-experiment-catalog` target. |
| 81 | yes | Add `make test-experiment-catalog` drift check target. |
| 82 | yes | Wire catalog drift check into integration gate. |
| 83 | yes | Add artifact summary generator (`scripts/report/summarize_artifacts.py`). |
| 84 | yes | Add `make report-artifact-summary` target. |
| 85 | yes | Wire artifact summary generation into integration gate. |
| 86 | yes | Extend `make help` with tranche-2 command surface. |
| 87 | yes | Extend README command index with tranche-2 controls. |
| 88 | yes | Extend README baseline-layout section with formal/catalog pointers. |
| 89 | yes | Keep security tooling strict-only for release posture (`gate-strict`). |
| 90 | yes | Keep solver-tool checks non-strict in integration gate for dev ergonomics. |
| 91 | yes | Preserve no-network deterministic defaults in harness. |
| 92 | yes | Preserve explicit seed policy for all harness runs. |
| 93 | yes | Preserve stable locale and timezone defaults. |
| 94 | yes | Preserve compatibility paths for legacy naming (`vampire`, `saint`). |
| 95 | yes | Preserve canonical scientific naming in active docs/CLI output. |
| 96 | yes | Keep Rust as simulation truth boundary. |
| 97 | yes | Keep Python as orchestration/certification boundary. |
| 98 | yes | Ensure all new tranche scripts emit machine-readable artifacts. |
| 99 | yes | Ensure all new tranche scripts run without external network dependencies. |
| 100 | yes | Re-run `make test-quick` after tranche-2 edits. |
| 101 | yes | Re-run `make gate` after tranche-2 edits. |
| 102 | yes | Re-run release-manifest/hygiene checks after tranche-2 edits. |
| 103 | yes | Record tranche-2 execution in `docs/AGENT_LOG.md`. |
| 104 | yes | Keep one-Concern command targets with deterministic naming (`test-*`, `report-*`, `update-*`). |
| 105 | yes | Preserve auditable release artifact location (`artifacts/release/<version>/`). |
| 106 | yes | Preserve auditable security artifact location (`artifacts/security/`). |
| 107 | yes | Preserve auditable timing artifact location (`artifacts/timing/`). |
| 108 | yes | Preserve auditable formal artifact location (`artifacts/formal/`). |
| 109 | yes | Preserve auditable report artifact location (`artifacts/reports/`). |
| 110 | yes | Keep tranche list itself explicit, long, and executable. |
| 111 | yes | Add examples unique-id validator (`scripts/test/check_examples_unique_ids.py`). |
| 112 | yes | Add scripts executable-bit validator (`scripts/test/check_scripts_executable.py`). |
| 113 | yes | Add script/python compile validator (`scripts/test/check_scripts_compile.py`). |
| 114 | yes | Add README command-surface validator (`scripts/test/check_readme_command_surface.py`). |
| 115 | yes | Add docs index core-link validator (`scripts/test/check_docs_index_core.py`). |
| 116 | yes | Add tranche completion validator (`scripts/test/check_tranches_complete.py`). |
| 117 | yes | Add tranche status generator (`scripts/report/build_tranche_status.py`). |
| 118 | yes | Add release manifest schema validator (`scripts/release/check_release_manifest_schema.py`). |
| 119 | yes | Add release checksum validator (`scripts/release/check_release_checksums.py`). |
| 120 | yes | Add reproducibility bundle index generator (`scripts/report/build_repro_bundle_index.py`). |
| 121 | yes | Add quality-assurance policy doc (`docs/QUALITY_ASSURANCE.md`). |
| 122 | yes | Add reproducibility policy doc (`docs/REPRODUCIBILITY.md`). |
| 123 | yes | Add release manifest schema contract (`schemas/release_manifest.schema.json`). |
| 124 | yes | Add `make test-examples-unique-ids` target. |
| 125 | yes | Add `make test-scripts-exec` target. |
| 126 | yes | Add `make test-scripts-compile` target. |
| 127 | yes | Add `make test-readme-commands` target. |
| 128 | yes | Add `make test-docs-index` target. |
| 129 | yes | Add `make test-tranches` target. |
| 130 | yes | Add `make update-tranche-status` target. |
| 131 | yes | Add `make test-tranche-status` target. |
| 132 | yes | Add `make test-release-manifest-schema` target. |
| 133 | yes | Add `make test-release-checksums` target. |
| 134 | yes | Add `make report-repro-bundle` target. |
| 135 | yes | Wire new tranche checks into `make gate`. |
| 136 | yes | Extend `make help` with tranche-expansion commands. |
| 137 | yes | Extend root README command index with tranche-expansion commands. |
| 138 | yes | Extend docs index with QA/repro links. |
| 139 | yes | Extend schema index with release-manifest schema. |
| 140 | yes | Extend release process doc with manifest/checksum validation commands. |
| 141 | yes | Extend control test required-file checks for QA/repro/schema assets. |
| 142 | yes | Extend control test Makefile target checks for tranche-expansion commands. |
| 143 | yes | Keep all tranche-expansion scripts executable. |
| 144 | yes | Keep tranche-expansion scripts local-only and deterministic. |
| 145 | yes | Emit machine-readable artifact for examples unique-id check. |
| 146 | yes | Emit machine-readable artifact for tranche status (`artifacts/reports/tranche_status.json`). |
| 147 | yes | Emit machine-readable reproducibility bundle index (`artifacts/reports/repro_bundle_index.json`). |
| 148 | yes | Keep release-manifest schema validation decoupled from external tools. |
| 149 | yes | Keep release-checksum validation reproducible and content-addressed. |
| 150 | yes | Preserve compatibility with existing `gate-strict` security behavior. |
| 151 | yes | Ensure docs link validator ignores http/mailto anchors safely. |
| 152 | yes | Ensure tranche validator enforces sequential numbering. |
| 153 | yes | Ensure tranche validator fails on unchecked items. |
| 154 | yes | Ensure scripts compile validator covers both `scripts/` and `grlab/`. |
| 155 | yes | Ensure docs-index validator protects critical scientific docs. |
| 156 | yes | Ensure README validator protects operational command discoverability. |
| 157 | yes | Ensure release schema validator checks all existing release manifests. |
| 158 | yes | Ensure release checksum validator verifies each listed file hash. |
| 159 | yes | Ensure reproducibility bundle index includes replay command pointer. |
| 160 | yes | Ensure gate emits tranche/report artifacts for auditability. |
| 161 | yes | Regenerate experiment catalog after tranche-expansion edits. |
| 162 | yes | Regenerate tranche status summary after tranche-expansion edits. |
| 163 | yes | Re-run `make test-quick` after tranche-expansion edits. |
| 164 | yes | Re-run `make gate` after tranche-expansion edits. |
| 165 | yes | Re-run `make release-manifest RELEASE_VERSION=dev` after tranche-expansion edits. |
| 166 | yes | Re-run `make test-release-manifest-schema` after manifest generation. |
| 167 | yes | Re-run `make test-release-checksums RELEASE_VERSION=dev` after manifest generation. |
| 168 | yes | Re-run `make test-release-hygiene RELEASE_VERSION=dev` after manifest checks. |
| 169 | yes | Re-run `make doctor` after tranche-expansion edits. |
| 170 | yes | Update `docs/AGENT_LOG.md` with tranche-expansion execution evidence. |
| 171 | yes | Preserve goldens/artifacts separation while expanding report surfaces. |
| 172 | yes | Preserve deterministic seed defaults while expanding QA controls. |
| 173 | yes | Preserve no-network posture while expanding validators. |
| 174 | yes | Preserve process hygiene checks while adding tranche checks. |
| 175 | yes | Preserve formal-smoke behavior with expected singular-case handling. |
| 176 | yes | Preserve tool-adapter abstraction for security and SBOM commands. |
| 177 | yes | Preserve release artifact location convention under `artifacts/release/<version>/`. |
| 178 | yes | Preserve report artifact location convention under `artifacts/reports/`. |
| 179 | yes | Preserve formal artifact location convention under `artifacts/formal/`. |
| 180 | yes | Keep tranche list very long, inclusive, and operationally executed. |
| 181 | yes | Add CI smoke workflow validator (`scripts/test/check_ci_smoke.py`). |
| 182 | yes | Add policy expiry validator (`scripts/test/check_policy_expirations.py`). |
| 183 | yes | Add spec evidence-link validator (`scripts/test/check_spec_evidence_links.py`). |
| 184 | yes | Add release process command validator (`scripts/test/check_release_doc_commands.py`). |
| 185 | yes | Add make-help surface validator (`scripts/test/check_make_help_surface.py`). |
| 186 | yes | Add required example asset validator (`scripts/test/check_required_examples.py`). |
| 187 | yes | Add report JSON parse validator (`scripts/test/check_reports_json_valid.py`). |
| 188 | yes | Add command inventory generator (`scripts/report/build_command_inventory.py`). |
| 189 | yes | Add validator inventory generator (`scripts/report/build_validator_inventory.py`). |
| 190 | yes | Add policy inventory generator (`scripts/report/build_policy_inventory.py`). |
| 191 | yes | Add CI policy doc (`docs/CI_POLICY.md`). |
| 192 | yes | Add dependency policy doc (`docs/DEPENDENCY_POLICY.md`). |
| 193 | yes | Add `make test-ci-smoke` target. |
| 194 | yes | Add `make test-policy-expirations` target. |
| 195 | yes | Add `make test-spec-evidence` target. |
| 196 | yes | Add `make test-release-doc` target. |
| 197 | yes | Add `make test-make-help` target. |
| 198 | yes | Add `make test-required-examples` target. |
| 199 | yes | Add `make test-reports-json` target. |
| 200 | yes | Add `make update-command-inventory` target. |
| 201 | yes | Add `make test-command-inventory` target. |
| 202 | yes | Add `make update-validator-inventory` target. |
| 203 | yes | Add `make test-validator-inventory` target. |
| 204 | yes | Add `make update-policy-inventory` target. |
| 205 | yes | Add `make test-policy-inventory` target. |
| 206 | yes | Wire CI/policy/spec-evidence checks into `make gate`. |
| 207 | yes | Wire command/validator/policy inventory drift checks into `make gate`. |
| 208 | yes | Wire report JSON validation into `make gate`. |
| 209 | yes | Extend `make help` to include tranche-expansion-II commands. |
| 210 | yes | Extend root README command index for tranche-expansion-II commands. |
| 211 | yes | Extend docs index with CI/dependency policy docs. |
| 212 | yes | Extend docs index with generated inventory docs. |
| 213 | yes | Extend control tests for tranche-expansion-II targets/docs. |
| 214 | yes | Add allowlist policy for intentional duplicate example ids (`policy/examples_id_allowlist.json`). |
| 215 | yes | Adapt unique-id validator to enforce only non-allowlisted duplicates. |
| 216 | yes | Emit policy-expiration report artifact (`artifacts/reports/policy_expirations.json`). |
| 217 | yes | Emit spec-evidence report artifact (`artifacts/reports/spec_evidence_links.json`). |
| 218 | yes | Emit command inventory artifact (`artifacts/reports/command_inventory.json`). |
| 219 | yes | Emit validator inventory artifact (`artifacts/reports/validator_inventory.json`). |
| 220 | yes | Emit policy inventory artifact (`artifacts/reports/policy_inventory.json`). |
| 221 | yes | Emit generated command inventory doc (`docs/COMMAND_INVENTORY.md`). |
| 222 | yes | Emit generated validator inventory doc (`docs/VALIDATOR_INVENTORY.md`). |
| 223 | yes | Emit generated policy inventory doc (`docs/POLICY_INVENTORY.md`). |
| 224 | yes | Keep CI smoke policy tied to `make test-quick` for deterministic fast loop. |
| 225 | yes | Keep policy expiry checks date-driven and machine-readable. |
| 226 | yes | Keep evidence-link checks explicit and traceable to ledger entries. |
| 227 | yes | Keep release process docs command-complete and test-verified. |
| 228 | yes | Keep `make help` output as executable contract surface. |
| 229 | yes | Keep required examples validated as scientific fixture baseline. |
| 230 | yes | Keep inventory docs generated from source data, not manual edits. |
| 231 | yes | Keep report JSON artifacts parse-valid before gate success. |
| 232 | yes | Keep deterministic/no-network posture while expanding validators. |
| 233 | yes | Keep all new scripts executable and local-only. |
| 234 | yes | Keep compatibility duplicate IDs explicit and policy-governed. |
| 235 | yes | Keep release manifest validation separate from external dependency tooling. |
| 236 | yes | Keep schema/index docs aligned with generated inventory outputs. |
| 237 | yes | Regenerate experiment catalog after tranche-expansion-II edits. |
| 238 | yes | Regenerate tranche status summary after tranche-expansion-II edits. |
| 239 | yes | Generate reproducibility bundle index after tranche-expansion-II edits. |
| 240 | yes | Generate command inventory after tranche-expansion-II edits. |
| 241 | yes | Generate validator inventory after tranche-expansion-II edits. |
| 242 | yes | Generate policy inventory after tranche-expansion-II edits. |
| 243 | yes | Re-run `make test-quick` after tranche-expansion-II edits. |
| 244 | yes | Re-run `make gate` after tranche-expansion-II edits. |
| 245 | yes | Re-run `make doctor` after tranche-expansion-II edits. |
| 246 | yes | Re-run `make release-manifest RELEASE_VERSION=dev` after tranche-expansion-II edits. |
| 247 | yes | Re-run `make test-release-manifest-schema` after manifest regeneration. |
| 248 | yes | Re-run `make test-release-checksums RELEASE_VERSION=dev` after manifest regeneration. |
| 249 | yes | Re-run `make test-release-hygiene RELEASE_VERSION=dev` after manifest regeneration. |
| 250 | yes | Update `docs/AGENT_LOG.md` with tranche-expansion-II evidence. |
| 251 | yes | Preserve strict security-tool requirement behavior for `gate-strict`. |
| 252 | yes | Preserve formal-tool non-strict advisory behavior in `gate`. |
| 253 | yes | Preserve process hygiene controls under expanded gate surface. |
| 254 | yes | Preserve artifact bucket contracts while adding inventory artifacts. |
| 255 | yes | Preserve command surface determinism by validating help/readme/doc indices. |
| 256 | yes | Preserve traceability by validating spec evidence links. |
| 257 | yes | Preserve CI smoke semantics by validating workflow content. |
| 258 | yes | Preserve policy governance by validating expiry dates. |
| 259 | yes | Preserve baseline scientific fixtures by validating required examples. |
| 260 | yes | Keep tranche list even longer, broader, and fully executed. |
| 261 | yes | Add schema JSON validity validator (`scripts/test/check_schema_json_valid.py`). |
| 262 | yes | Add policy JSON validity validator (`scripts/test/check_policy_json_valid.py`). |
| 263 | yes | Add hook contract validator (`scripts/test/check_hooks_contract.py`). |
| 264 | yes | Add artifact `.gitkeep` validator (`scripts/test/check_artifact_gitkeeps.py`). |
| 265 | yes | Add release-manifest required-entry validator (`scripts/test/check_release_manifest_entries.py`). |
| 266 | yes | Add timing artifact presence validator (`scripts/test/check_timing_artifacts_presence.py`). |
| 267 | yes | Add generated-doc presence validator (`scripts/test/check_generated_docs_presence.py`). |
| 268 | yes | Add schema inventory generator (`scripts/report/build_schema_inventory.py`). |
| 269 | yes | Add artifact-bucket inventory generator (`scripts/report/build_artifact_bucket_inventory.py`). |
| 270 | yes | Add `make test-schema-json` target. |
| 271 | yes | Add `make test-policy-json` target. |
| 272 | yes | Add `make test-hooks-contract` target. |
| 273 | yes | Add `make test-artifact-gitkeeps` target. |
| 274 | yes | Add `make test-release-manifest-entries` target. |
| 275 | yes | Add `make test-timing-artifacts` target. |
| 276 | yes | Add `make test-generated-docs` target. |
| 277 | yes | Add `make update-schema-inventory` target. |
| 278 | yes | Add `make test-schema-inventory` target. |
| 279 | yes | Add `make update-artifact-buckets` target. |
| 280 | yes | Add `make test-artifact-buckets` target. |
| 281 | yes | Wire schema/policy/hook/artifact validators into `make gate`. |
| 282 | yes | Wire timing artifact presence validation into `make gate`. |
| 283 | yes | Wire generated-doc presence validation into `make gate`. |
| 284 | yes | Wire schema/artifact inventory drift checks into `make gate`. |
| 285 | yes | Extend `make help` with tranche-expansion-IV command surface. |
| 286 | yes | Extend root README command index with tranche-expansion-IV commands. |
| 287 | yes | Extend docs index with generated schema/artifact inventory docs. |
| 288 | yes | Extend control tests for tranche-expansion-IV docs/targets. |
| 289 | yes | Keep validator scripts executable and local-only. |
| 290 | yes | Preserve deterministic execution posture for new validators. |
| 291 | yes | Preserve no-network default posture for expanded gate. |
| 292 | yes | Preserve compatibility naming while enforcing policy guards. |
| 293 | yes | Ensure hook policy remains auditable through bypass logging checks. |
| 294 | yes | Ensure artifact-retention structure is enforced via `.gitkeep` checks. |
| 295 | yes | Ensure release manifest content includes expected baseline assets. |
| 296 | yes | Ensure timing artifacts are present before gate completion. |
| 297 | yes | Ensure generated docs required by governance are materially present. |
| 298 | yes | Ensure schema inventory remains generated, not hand-edited. |
| 299 | yes | Ensure artifact-bucket inventory remains generated, not hand-edited. |
| 300 | yes | Preserve command surface traceability through generated inventories. |
| 301 | yes | Regenerate tranche status summary after tranche-expansion-IV edits. |
| 302 | yes | Regenerate experiment catalog after tranche-expansion-IV edits. |
| 303 | yes | Regenerate command inventory after tranche-expansion-IV edits. |
| 304 | yes | Regenerate validator inventory after tranche-expansion-IV edits. |
| 305 | yes | Regenerate policy inventory after tranche-expansion-IV edits. |
| 306 | yes | Generate schema inventory after tranche-expansion-IV edits. |
| 307 | yes | Generate artifact-bucket inventory after tranche-expansion-IV edits. |
| 308 | yes | Generate reproducibility bundle index after tranche-expansion-IV edits. |
| 309 | yes | Re-run `make test-quick` after tranche-expansion-IV edits. |
| 310 | yes | Re-run `make doctor` after tranche-expansion-IV edits. |
| 311 | yes | Re-run `make gate` after tranche-expansion-IV edits. |
| 312 | yes | Re-run `make release-manifest RELEASE_VERSION=dev` after tranche-expansion-IV edits. |
| 313 | yes | Re-run `make test-release-manifest-schema` after manifest regeneration. |
| 314 | yes | Re-run `make test-release-manifest-entries RELEASE_VERSION=dev` after manifest regeneration. |
| 315 | yes | Re-run `make test-release-checksums RELEASE_VERSION=dev` after manifest regeneration. |
| 316 | yes | Re-run `make test-release-hygiene RELEASE_VERSION=dev` after manifest regeneration. |
| 317 | yes | Update `docs/AGENT_LOG.md` with tranche-expansion-IV evidence. |
| 318 | yes | Preserve strict security requirements in `gate-strict`. |
| 319 | yes | Preserve non-strict security behavior in `gate` for dev mode. |
| 320 | yes | Preserve process hygiene enforcement under expanded gate. |
| 321 | yes | Preserve ledger/schema governance under expanded gate. |
| 322 | yes | Preserve ADR validation controls under expanded gate. |
| 323 | yes | Preserve golden registry validation controls under expanded gate. |
| 324 | yes | Preserve timing baseline regression controls under expanded gate. |
| 325 | yes | Preserve release schema/checksum hygiene controls under expanded gate model. |
| 326 | yes | Preserve report JSON validity under expanded report generation. |
| 327 | yes | Preserve evidence-link traceability between specs and artifacts/docs. |
| 328 | yes | Preserve CI smoke determinism checks via workflow validator. |
| 329 | yes | Preserve policy-expiry governance via automated date checks. |
| 330 | yes | Preserve command/help discoverability via automated checks. |
| 331 | yes | Preserve required scientific fixtures via explicit example checks. |
| 332 | yes | Preserve inventory drift detection as deterministic gate control. |
| 333 | yes | Preserve artifact-bucket auditability via generated summary docs. |
| 334 | yes | Preserve schema auditability via generated schema inventory docs. |
| 335 | yes | Preserve policy auditability via generated policy inventory docs. |
| 336 | yes | Preserve validator auditability via generated validator inventory docs. |
| 337 | yes | Preserve command auditability via generated command inventory docs. |
| 338 | yes | Keep tranche ledger sequential and fully checked. |
| 339 | yes | Keep tranche execution broad across code, docs, policy, CI, and release controls. |
| 340 | yes | Keep tranche program very long, inclusive, and executed end-to-end. |
| 341 | yes | Run deep external-source research pass for science-direction reset. |
| 342 | yes | Collect primary repeated-game literature for memory-one/ZD/extortion/generosity claims. |
| 343 | yes | Collect benchmark-ecosystem references (Axelrod/OpenSpiel). |
| 344 | yes | Collect formal solver and verification references (SMT-LIB, Z3, cvc5, rsmt2, Kani, Prusti, Creusot). |
| 345 | yes | Collect probabilistic model-checking references (PRISM, Storm). |
| 346 | yes | Collect reproducibility operations references (Snakemake, DVC, NASEM). |
| 347 | yes | Collect deterministic performance/testing references (Criterion, nextest). |
| 348 | yes | Verify source URL health with explicit HTTP checks. |
| 349 | yes | Add source registry doc (`docs/RESEARCH_SOURCES.md`). |
| 350 | yes | Encode source identifiers by domain (IPD/formal/Rust-Python/ops). |
| 351 | yes | Map each source to explicit Concord implications. |
| 352 | yes | Add source-backed agenda doc (`docs/RESEARCH_AGENDA.md`). |
| 353 | yes | Expand science plan phases to include formal-claim strengthening. |
| 354 | yes | Define broad tranche queue across theory, Rust, formal solvers, orchestration, stats, and release operations. |
| 355 | yes | Link research docs from docs index (`docs/README.md`). |
| 356 | yes | Link context index to research bibliography (`docs/context/README.md`). |
| 357 | yes | Record new formal-method ambiguity in spec ledger (`SG-002`). |
| 358 | yes | Record linked research question for solver obligations (`SQ-002`). |
| 359 | yes | Record temporary solver-posture assumption (`SA-002`). |
| 360 | yes | Keep evidence links in ledger pointing only to local auditable paths. |
| 361 | yes | Preserve Rust/Python boundary while updating research direction. |
| 362 | yes | Preserve deterministic/no-network test posture during research tranche. |
| 363 | yes | Preserve formal checks as advisory in integration gate pending claim-class spec resolution. |
| 364 | yes | Preserve strict release posture for optional security tooling. |
| 365 | yes | Keep research outputs diffable textual docs. |
| 366 | yes | Keep research outputs compatible with existing governance validators. |
| 367 | yes | Regenerate tranche summary/status artifacts after tranche-extension-V edits. |
| 368 | yes | Re-run `make test-quick` after research-doc edits. |
| 369 | yes | Re-run `make test-spec-ledger` after ledger updates. |
| 370 | yes | Re-run `make test-spec-evidence` after ledger evidence-link updates. |
| 371 | yes | Re-run `make test-doc-links` after adding research docs. |
| 372 | yes | Re-run `make test-docs-index` after docs-index updates. |
| 373 | yes | Re-run `make test-tranches` after tranche-extension-V edits. |
| 374 | yes | Re-run `make test-tranche-status` after tranche summary regeneration. |
| 375 | yes | Re-run `make gate` after research tranche integration. |
| 376 | yes | Update `docs/AGENT_LOG.md` with research tranche evidence. |
| 377 | yes | Preserve source traceability for future claim audits. |
| 378 | yes | Preserve assumption traceability for unresolved formal-method policy decisions. |
| 379 | yes | Preserve compatibility with current command/gate surface while adding research direction. |
| 380 | yes | Keep tranche ledger long, inclusive, and executed across research + implementation governance. |
| 381 | yes | Add source-mapped research tranche matrix (`docs/RESEARCH_TRANCHE_MATRIX.md`). |
| 382 | yes | Define explicit tranche IDs (`RT-001`..`RT-060`) for science build sequencing. |
| 383 | yes | Map tranche packages to source IDs for traceability. |
| 384 | yes | Map tranche packages to minimum verification commands/artifacts. |
| 385 | yes | Cover theory/spec tranche class in execution matrix. |
| 386 | yes | Cover Rust engine tranche class in execution matrix. |
| 387 | yes | Cover formal solver tranche class in execution matrix. |
| 388 | yes | Cover Python orchestration tranche class in execution matrix. |
| 389 | yes | Cover benchmark/evaluation tranche class in execution matrix. |
| 390 | yes | Cover statistics/evidence tranche class in execution matrix. |
| 391 | yes | Cover reproducibility/release operations tranche class in execution matrix. |
| 392 | yes | Add explicit sequencing prerequisites to tranche matrix. |
| 393 | yes | Extend docs index with tranche matrix entry. |
| 394 | yes | Extend research source registry with classical cooperation references. |
| 395 | yes | Re-run URL health checks for bibliography set after source expansion. |
| 396 | yes | Regenerate tranche summary/status after tranche-extension-VI edits. |
| 397 | yes | Re-run `make test-quick` after tranche-extension-VI edits. |
| 398 | yes | Re-run `make test-tranches` and `make test-tranche-status` after tranche-extension-VI edits. |
| 399 | yes | Re-run `make gate` after tranche-extension-VI edits. |
| 400 | yes | Keep tranche program broader and deeper while preserving deterministic controls. |
| 401 | yes | Continue research/planning pass on request with deeper scientific prioritization. |
| 402 | yes | Expand source registry with Kani feature-support reference. |
| 403 | yes | Expand source registry with PRISM tutorial reference. |
| 404 | yes | Expand source registry with MDP model-checking algorithm guide reference. |
| 405 | yes | Add explicit research-opinion document (`docs/RESEARCH_OPINIONS.md`). |
| 406 | yes | Document strong project opinions on Rust/Python/formal boundaries. |
| 407 | yes | Document explicit "build first" priorities for next cycles. |
| 408 | yes | Document explicit "do not build yet" anti-pattern list. |
| 409 | yes | Add 12-week phased research implementation priorities. |
| 410 | yes | Add decision gates for promoting advisory checks to required checks. |
| 411 | yes | Add failure conditions that freeze expansion until foundations are repaired. |
| 412 | yes | Link research-opinion doc in docs index. |
| 413 | yes | Re-run bibliography URL checks for newly added references. |
| 414 | yes | Regenerate tranche summary/status after tranche-extension-VII edits. |
| 415 | yes | Re-run `make test-quick` after tranche-extension-VII edits. |
| 416 | yes | Re-run `make test-tranches` and `make test-tranche-status` after tranche-extension-VII edits. |
| 417 | yes | Re-run `make test-doc-links` after research-opinion additions. |
| 418 | yes | Re-run `make test-docs-index` after docs index updates. |
| 419 | yes | Re-run `make gate` after tranche-extension-VII edits. |
| 420 | yes | Keep long-form research planning active while preserving deterministic gate integrity. |
| 421 | yes | Start tranche-extension-VIII with inclusive cross-domain scope. |
| 422 | yes | Add machine-readable claim class specification (`specs/claim_classes.yaml`). |
| 423 | yes | Add claim class schema contract (`schemas/claim_classes.schema.json`). |
| 424 | yes | Add claim class validator (`scripts/test/check_claim_classes.py`). |
| 425 | yes | Add claim matrix generator (`scripts/report/build_claim_matrix.py`). |
| 426 | yes | Add research docs validator (`scripts/test/check_research_docs.py`). |
| 427 | yes | Add claim taxonomy policy doc (`docs/CLAIM_TAXONOMY.md`). |
| 428 | yes | Add formal obligation mapping doc (`docs/FORMAL_OBLIGATION_TABLE.md`). |
| 429 | yes | Add benchmark program doc (`docs/BENCHMARK_PROGRAM.md`). |
| 430 | yes | Add execution rhythm doc (`docs/EXECUTION_RHYTHM.md`). |
| 431 | yes | Add research risk register doc (`docs/RESEARCH_RISK_REGISTER.md`). |
| 432 | yes | Extend docs index with new research-governance docs. |
| 433 | yes | Extend root README command index with claim-matrix/claim-class commands. |
| 434 | yes | Extend schema reference doc with claim-class schema. |
| 435 | yes | Extend generated-doc presence validator with `docs/CLAIM_MATRIX.md`. |
| 436 | yes | Extend docs-index core validator with research/claim links. |
| 437 | yes | Add Makefile target `test-research-docs`. |
| 438 | yes | Add Makefile target `test-claim-classes`. |
| 439 | yes | Add Makefile target `update-claim-matrix`. |
| 440 | yes | Add Makefile target `test-claim-matrix`. |
| 441 | yes | Add new targets to Makefile `.PHONY` surface. |
| 442 | yes | Add new targets to `make help` command surface. |
| 443 | yes | Wire research-doc checks into `make gate`. |
| 444 | yes | Wire claim-class validation into `make gate`. |
| 445 | yes | Wire claim-matrix drift check into `make gate`. |
| 446 | yes | Keep claim-class spec textual and diffable. |
| 447 | yes | Keep claim-class validator local-only and deterministic. |
| 448 | yes | Keep claim-matrix generator artifact-writing deterministic. |
| 449 | yes | Keep research-doc validator deterministic and low-cost. |
| 450 | yes | Keep no-network posture for new gate checks. |
| 451 | yes | Keep strict-gate policy separation for high-formality claim classes. |
| 452 | yes | Include explicit evidence-class taxonomy (`empirical`, `formal`, `hybrid`, `operational`, `assumption`). |
| 453 | yes | Include strict-gate-required flag in machine-readable claim classes. |
| 454 | yes | Include required checks list per claim class. |
| 455 | yes | Include required artifacts list per claim class. |
| 456 | yes | Include claim summary scope text per claim class. |
| 457 | yes | Add claim class coverage for empirical performance claims. |
| 458 | yes | Add claim class coverage for robustness claims. |
| 459 | yes | Add claim class coverage for formal invariance claims. |
| 460 | yes | Add claim class coverage for cross-solver agreement claims. |
| 461 | yes | Add claim class coverage for probabilistic-bound claims. |
| 462 | yes | Add claim class coverage for reproducibility claims. |
| 463 | yes | Add claim class coverage for policy-exception assumption claims. |
| 464 | yes | Add formal-obligation table entry per claim class. |
| 465 | yes | Add benchmark family definitions in benchmark program doc. |
| 466 | yes | Add benchmark governance rules in benchmark program doc. |
| 467 | yes | Add daily cadence controls in execution rhythm doc. |
| 468 | yes | Add weekly cadence controls in execution rhythm doc. |
| 469 | yes | Add release-candidate cadence controls in execution rhythm doc. |
| 470 | yes | Add risk register entries for solver disagreement and benchmark overfit. |
| 471 | yes | Add risk register entries for orchestration drift and artifact incompleteness. |
| 472 | yes | Add risk register review cadence guidance. |
| 473 | yes | Add source-registry integration for claim governance posture. |
| 474 | yes | Preserve source-to-work-package traceability through tranche expansion. |
| 475 | yes | Preserve spec-ledger assumption transparency during claim-taxonomy expansion. |
| 476 | yes | Preserve Rust truth boundary while adding research governance controls. |
| 477 | yes | Preserve Python orchestration boundary while adding claim governance controls. |
| 478 | yes | Preserve artifact-bucket auditability while adding claim matrix artifacts. |
| 479 | yes | Preserve command-surface discoverability with new make targets. |
| 480 | yes | Preserve validator inventory completeness with new validators. |
| 481 | yes | Preserve schema inventory completeness with new schema. |
| 482 | yes | Preserve generated-doc inventory semantics with claim matrix doc. |
| 483 | yes | Generate claim matrix doc/artifact from claim classes (`update-claim-matrix`). |
| 484 | yes | Regenerate schema inventory after claim-schema addition. |
| 485 | yes | Regenerate command inventory after Makefile target expansion. |
| 486 | yes | Regenerate validator inventory after new validator scripts. |
| 487 | yes | Regenerate tranche status summary after tranche-extension-VIII edits. |
| 488 | yes | Re-run claim-class validator after initial write. |
| 489 | yes | Re-run research-doc validator after docs/index updates. |
| 490 | yes | Re-run docs-link validation after research-doc additions. |
| 491 | yes | Re-run docs-index core validation after required-link expansion. |
| 492 | yes | Re-run schema-json validation after schema addition. |
| 493 | yes | Re-run schema-inventory drift check after schema inventory regeneration. |
| 494 | yes | Re-run command-inventory drift check after command inventory regeneration. |
| 495 | yes | Re-run validator-inventory drift check after validator inventory regeneration. |
| 496 | yes | Re-run generated-doc presence check after claim matrix generation. |
| 497 | yes | Re-run `make test-quick` after tranche-extension-VIII edits. |
| 498 | yes | Re-run `make test-tranches` and `make test-tranche-status` after tranche-extension-VIII edits. |
| 499 | yes | Re-run `make gate` after tranche-extension-VIII edits. |
| 500 | yes | Update `docs/AGENT_LOG.md` with tranche-extension-VIII evidence. |
| 501 | yes | Add tranche item for reproducibility-oriented claim-class auditing. |
| 502 | yes | Add tranche item for formal-obligation staged adoption policy. |
| 503 | yes | Add tranche item for benchmark governance anti-overfit guardrails. |
| 504 | yes | Add tranche item for risk register maintenance practice. |
| 505 | yes | Add tranche item for evidence-class declaration requirements. |
| 506 | yes | Add tranche item for strict-gate-required claim flag semantics. |
| 507 | yes | Add tranche item for claim-matrix drift-control practice. |
| 508 | yes | Add tranche item for inclusive documentation across science + ops + governance. |
| 509 | yes | Add tranche item for integrating new research docs into repo index. |
| 510 | yes | Add tranche item for integrating new command surface into root README. |
| 511 | yes | Add tranche item for integrating new schema into schema reference docs. |
| 512 | yes | Add tranche item for integrating claim matrix into generated-doc checks. |
| 513 | yes | Add tranche item for integrating research docs into gate coverage. |
| 514 | yes | Add tranche item for integrating claim classes into gate coverage. |
| 515 | yes | Add tranche item for integrating claim matrix drift checks into gate coverage. |
| 516 | yes | Add tranche item for inclusive tranche wave coverage across files/scripts/docs/policy. |
| 517 | yes | Add tranche item for post-change deterministic validation sweep. |
| 518 | yes | Add tranche item for tranche summary regeneration at new scale. |
| 519 | yes | Add tranche item for maintaining long-form inclusive tranche program continuity. |
| 520 | yes | Keep tranche program very long, inclusive, and fully executed in tranche-extension-VIII. |
| 521 | yes | Start tranche-extension-IX for claim-register execution infrastructure. |
| 522 | yes | Add machine-readable claim register spec (`specs/claim_register.yaml`). |
| 523 | yes | Add claim register schema contract (`schemas/claim_register.schema.json`). |
| 524 | yes | Add claim register validator (`scripts/test/check_claim_register.py`). |
| 525 | yes | Add claim register summary generator (`scripts/report/build_claim_register_summary.py`). |
| 526 | yes | Add claim workflow policy doc (`docs/CLAIM_WORKFLOW.md`). |
| 527 | yes | Add claim register generated doc surface (`docs/CLAIM_REGISTER.md`). |
| 528 | yes | Extend research-doc validator to require claim workflow assets. |
| 529 | yes | Extend generated-doc validator to require `docs/CLAIM_REGISTER.md`. |
| 530 | yes | Extend docs-index core validator to require claim register link. |
| 531 | yes | Extend README command surface validator with claim-register commands. |
| 532 | yes | Extend repo control tests with claim schemas. |
| 533 | yes | Extend repo control tests with claim-register make targets. |
| 534 | yes | Add Makefile target `test-claim-register`. |
| 535 | yes | Add Makefile target `update-claim-register-summary`. |
| 536 | yes | Add Makefile target `test-claim-register-summary`. |
| 537 | yes | Add claim-register targets to `.PHONY`. |
| 538 | yes | Add claim-register targets to `make help`. |
| 539 | yes | Add claim-register commands to root `README.md` command index. |
| 540 | yes | Add claim register to root README baseline-layout pointers. |
| 541 | yes | Add claim workflow and claim register to docs index. |
| 542 | yes | Add claim-register schema pointer to `docs/SCHEMAS.md`. |
| 543 | yes | Wire claim-register validation into `make gate`. |
| 544 | yes | Wire claim-register summary drift check into `make gate`. |
| 545 | yes | Keep claim register entries local-path evidence only (no remote dependency). |
| 546 | yes | Keep claim register deterministic and diffable. |
| 547 | yes | Keep claim register IDs stable (`CL-*`). |
| 548 | yes | Keep class linkage explicit (`claim_class_id` -> `CC-*`). |
| 549 | yes | Keep assumption linkage explicit (`assumptions` -> `SA-*`). |
| 550 | yes | Keep claim status lifecycle explicit (`draft|active|superseded|retired`). |
| 551 | yes | Keep claim update timestamps date-validated. |
| 552 | yes | Ensure claim-register validator checks class existence. |
| 553 | yes | Ensure claim-register validator checks assumption existence in ledger. |
| 554 | yes | Ensure claim-register validator checks evidence-link path existence. |
| 555 | yes | Ensure claim-register validator emits machine-readable artifact. |
| 556 | yes | Ensure claim-register summary emits machine-readable artifact. |
| 557 | yes | Ensure claim-register summary markdown is generated from source of truth. |
| 558 | yes | Add active claim coverage for empirical claim classes. |
| 559 | yes | Add active claim coverage for operational reproducibility claim class. |
| 560 | yes | Add active claim coverage for assumption/policy claim class. |
| 561 | yes | Add draft claim coverage for cross-solver class pending implementation. |
| 562 | yes | Add draft claim coverage for probabilistic-bound class pending adapters. |
| 563 | yes | Add active claim coverage for formal-invariance class. |
| 564 | yes | Add claim-register scope text per entry. |
| 565 | yes | Add claim-register owner field per entry. |
| 566 | yes | Add claim-register evidence-link count reporting in summary. |
| 567 | yes | Add claim-register strict-gate-required projection in summary. |
| 568 | yes | Keep strict claim classes visible for release policy planning. |
| 569 | yes | Keep claim workflow aligned with existing gate model. |
| 570 | yes | Keep claim workflow aligned with spec-ledger discipline. |
| 571 | yes | Keep claim workflow aligned with evidence-link validation policy. |
| 572 | yes | Keep claim workflow aligned with release-manifest reproducibility posture. |
| 573 | yes | Keep claim workflow commands scoped to Makefile targets. |
| 574 | yes | Keep claim workflow narrow and actionable for AFK operation. |
| 575 | yes | Keep claim-register scripts executable and compile-clean. |
| 576 | yes | Preserve no-network deterministic posture for claim-register controls. |
| 577 | yes | Preserve goldens/artifacts separation while adding claim reports. |
| 578 | yes | Preserve report-bucket auditability after adding claim artifacts. |
| 579 | yes | Preserve command inventory generation after make-target expansion. |
| 580 | yes | Preserve validator inventory generation after new validator scripts. |
| 581 | yes | Preserve schema inventory generation after new schema file. |
| 582 | yes | Preserve generated-doc checks with expanded generated surfaces. |
| 583 | yes | Preserve docs-link integrity after claim workflow docs addition. |
| 584 | yes | Preserve docs-index integrity after claim workflow docs addition. |
| 585 | yes | Preserve README command integrity after claim command additions. |
| 586 | yes | Generate claim register summary via `make update-claim-register-summary`. |
| 587 | yes | Re-run claim class matrix generation for consistency. |
| 588 | yes | Re-run schema inventory generation after claim-register schema. |
| 589 | yes | Re-run command inventory generation after Makefile changes. |
| 590 | yes | Re-run validator inventory generation after script changes. |
| 591 | yes | Re-run tranche status summary after tranche-extension-IX edits. |
| 592 | yes | Re-run `make test-claim-classes` after claim-register additions. |
| 593 | yes | Re-run `make test-claim-register` after register additions. |
| 594 | yes | Re-run `make test-claim-register-summary` after summary generation. |
| 595 | yes | Re-run `make test-research-docs` after workflow/register doc additions. |
| 596 | yes | Re-run `make test-schema-json` after schema additions. |
| 597 | yes | Re-run `make test-schema-inventory` after schema regeneration. |
| 598 | yes | Re-run `make test-command-inventory` after command regeneration. |
| 599 | yes | Re-run `make test-validator-inventory` after validator regeneration. |
| 600 | yes | Re-run `make test-generated-docs` after claim-register doc generation. |
| 601 | yes | Re-run `make test-doc-links` after docs expansion. |
| 602 | yes | Re-run `make test-docs-index` after index expansion. |
| 603 | yes | Re-run `make test-readme-commands` after command surface expansion. |
| 604 | yes | Re-run `make test-quick` after tranche-extension-IX edits. |
| 605 | yes | Re-run `make test-tranches` and `make test-tranche-status` after tranche-extension-IX edits. |
| 606 | yes | Re-run `make gate` after tranche-extension-IX edits. |
| 607 | yes | Update `docs/AGENT_LOG.md` with tranche-extension-IX evidence. |
| 608 | yes | Add tranche item for inclusive claim-governance execution across spec/schema/scripts/docs. |
| 609 | yes | Add tranche item for deterministic claim-audit reporting surfaces. |
| 610 | yes | Add tranche item for claim-lifecycle operationalization. |
| 611 | yes | Add tranche item for active/draft claim portfolio tracking. |
| 612 | yes | Add tranche item for strict-claim visibility in generated reports. |
| 613 | yes | Add tranche item for assumption-linked claim traceability. |
| 614 | yes | Add tranche item for evidence-linked claim traceability. |
| 615 | yes | Add tranche item for schema-backed claim register safety. |
| 616 | yes | Add tranche item for gate-backed claim governance enforcement. |
| 617 | yes | Add tranche item for audit-ready claim docs in repo index. |
| 618 | yes | Add tranche item for AFK-safe autonomous build expansion execution. |
| 619 | yes | Add tranche item for preserving broad tranche inclusivity while deepening implementation. |
| 620 | yes | Keep tranche program very long, inclusive, and fully executed in tranche-extension-IX. |
| 621 | yes | Start tranche-extension-X for machine-readable risk governance. |
| 622 | yes | Add risk register source file (`specs/risk_register.yaml`). |
| 623 | yes | Add risk register schema contract (`schemas/risk_register.schema.json`). |
| 624 | yes | Add risk register validator (`scripts/test/check_risk_register.py`). |
| 625 | yes | Add risk register summary generator (`scripts/report/build_risk_register_summary.py`). |
| 626 | yes | Add generated risk register doc (`docs/RISK_REGISTER.md`). |
| 627 | yes | Extend research docs validator with generated risk register doc. |
| 628 | yes | Extend generated-doc validator with risk register generated doc. |
| 629 | yes | Extend docs-index core validator with risk register link requirement. |
| 630 | yes | Extend schema reference with risk register schema. |
| 631 | yes | Extend root README command surface with risk-register commands. |
| 632 | yes | Extend root README baseline layout with risk register summary pointer. |
| 633 | yes | Extend docs index with risk register summary pointer. |
| 634 | yes | Update research risk register narrative doc to point at machine source. |
| 635 | yes | Add Makefile target `test-risk-register`. |
| 636 | yes | Add Makefile target `update-risk-register-summary`. |
| 637 | yes | Add Makefile target `test-risk-register-summary`. |
| 638 | yes | Add risk-register targets to `.PHONY`. |
| 639 | yes | Add risk-register targets to `make help`. |
| 640 | yes | Add risk-register checks to integration gate. |
| 641 | yes | Keep risk register textual and diffable. |
| 642 | yes | Keep risk register deterministic and no-network. |
| 643 | yes | Keep risk register IDs stable (`RK-*`). |
| 644 | yes | Keep risk status lifecycle explicit (`open|mitigated|accepted|closed`). |
| 645 | yes | Keep risk domains constrained to known categories. |
| 646 | yes | Keep severity constrained (`low|medium|high|critical`). |
| 647 | yes | Keep likelihood constrained (`low|medium|high`). |
| 648 | yes | Keep owner field mandatory for accountability. |
| 649 | yes | Keep mitigation field mandatory for each risk. |
| 650 | yes | Keep review_date mandatory and date-validated. |
| 651 | yes | Keep evidence_links mandatory and path-validated. |
| 652 | yes | Ensure risk register validator emits machine-readable artifact. |
| 653 | yes | Ensure risk summary generator emits machine-readable artifact. |
| 654 | yes | Ensure risk summary markdown is generated from spec source. |
| 655 | yes | Add risk entry for solver-disagreement exposure. |
| 656 | yes | Add risk entry for benchmark-overfitting exposure. |
| 657 | yes | Add risk entry for artifact/reproducibility incompleteness exposure. |
| 658 | yes | Add risk entry for assumption-backlog governance exposure. |
| 659 | yes | Add risk entry for performance feedback-loop degradation exposure. |
| 660 | yes | Tie risk evidence links to existing docs/specs/scripts. |
| 661 | yes | Keep risk review dates future-dated to avoid immediate stale entries. |
| 662 | yes | Enforce overdue open/mitigated risk failure policy in validator. |
| 663 | yes | Preserve compatibility with existing policy-expiration checks. |
| 664 | yes | Preserve compatibility with existing spec-evidence checks. |
| 665 | yes | Preserve compatibility with existing claim-register checks. |
| 666 | yes | Preserve compatibility with generated-doc inventory checks. |
| 667 | yes | Preserve command inventory generation with new targets. |
| 668 | yes | Preserve validator inventory generation with new validator script. |
| 669 | yes | Preserve schema inventory generation with new schema file. |
| 670 | yes | Preserve artifact bucket policy with new report artifacts. |
| 671 | yes | Extend repo control tests with risk schema requirements. |
| 672 | yes | Extend repo control tests with risk-register make targets. |
| 673 | yes | Extend README command validator with risk-register commands. |
| 674 | yes | Keep risk register integrated with AFK-friendly make workflows. |
| 675 | yes | Keep risk governance integrated with release/repro posture. |
| 676 | yes | Generate risk register summary (`update-risk-register-summary`). |
| 677 | yes | Regenerate claim matrix summary for consistency. |
| 678 | yes | Regenerate claim register summary for consistency. |
| 679 | yes | Regenerate schema inventory after schema additions. |
| 680 | yes | Regenerate command inventory after target additions. |
| 681 | yes | Regenerate validator inventory after script additions. |
| 682 | yes | Regenerate tranche status summary after tranche-extension-X edits. |
| 683 | yes | Re-run `make test-risk-register` after risk spec additions. |
| 684 | yes | Re-run `make test-risk-register-summary` after risk summary generation. |
| 685 | yes | Re-run `make test-research-docs` after risk docs/index updates. |
| 686 | yes | Re-run `make test-claim-classes` after combined governance updates. |
| 687 | yes | Re-run `make test-claim-register` after combined governance updates. |
| 688 | yes | Re-run `make test-claim-register-summary` after combined governance updates. |
| 689 | yes | Re-run `make test-schema-json` after adding risk schema. |
| 690 | yes | Re-run `make test-schema-inventory` after regeneration. |
| 691 | yes | Re-run `make test-command-inventory` after regeneration. |
| 692 | yes | Re-run `make test-validator-inventory` after regeneration. |
| 693 | yes | Re-run `make test-generated-docs` after generated risk doc addition. |
| 694 | yes | Re-run `make test-doc-links` after docs expansion. |
| 695 | yes | Re-run `make test-docs-index` after index expansion. |
| 696 | yes | Re-run `make test-readme-commands` after command expansion. |
| 697 | yes | Re-run `make test-quick` after tranche-extension-X edits. |
| 698 | yes | Re-run `make test-tranches` and `make test-tranche-status` after tranche-extension-X edits. |
| 699 | yes | Re-run `make gate` after tranche-extension-X edits. |
| 700 | yes | Update `docs/AGENT_LOG.md` with tranche-extension-X evidence. |
| 701 | yes | Add tranche item for inclusive risk governance across specs/schemas/scripts/docs. |
| 702 | yes | Add tranche item for generated risk summary integration in docs/automation. |
| 703 | yes | Add tranche item for explicit risk lifecycle policy enforcement. |
| 704 | yes | Add tranche item for deterministic risk-review audit output. |
| 705 | yes | Add tranche item for risk evidence-link local path enforcement. |
| 706 | yes | Add tranche item for risk severity/likelihood machine validation. |
| 707 | yes | Add tranche item for active risk review-date freshness enforcement. |
| 708 | yes | Add tranche item for preserving broad tranche inclusivity in governance layers. |
| 709 | yes | Add tranche item for preserving broad tranche inclusivity in report layers. |
| 710 | yes | Add tranche item for preserving broad tranche inclusivity in schema layers. |
| 711 | yes | Add tranche item for preserving broad tranche inclusivity in validator layers. |
| 712 | yes | Add tranche item for preserving broad tranche inclusivity in command-surface layers. |
| 713 | yes | Add tranche item for preserving broad tranche inclusivity in docs-index layers. |
| 714 | yes | Add tranche item for preserving broad tranche inclusivity in control-test layers. |
| 715 | yes | Add tranche item for preserving broad tranche inclusivity in gate layers. |
| 716 | yes | Add tranche item for preserving AFK operability while adding governance controls. |
| 717 | yes | Add tranche item for preserving deterministic local-first operation while scaling control surface. |
| 718 | yes | Add tranche item for preserving machine-auditable evidence at increased tranche scale. |
| 719 | yes | Add tranche item for preserving end-to-end validation discipline at increased tranche scale. |
| 720 | yes | Keep tranche program very long, inclusive, and fully executed in tranche-extension-X. |
