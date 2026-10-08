# Tranche Program

This file tracks an inclusive, mixed-domain tranche execution plan for Concord.

## Tranches

1. [x] Replace narrative operating contract with scientific contract (`AGENTS.md`).
2. [x] Establish deterministic make-based command surface (`Makefile`).
3. [x] Add doctor checks for toolchains and prerequisites.
4. [x] Add deterministic quick/full harness modes.
5. [x] Emit seed artifacts per harness mode.
6. [x] Emit timing artifacts per harness mode.
7. [x] Add artifact cleanup utility with safe defaults.
8. [x] Add process lifecycle control wrapper.
9. [x] Add process hygiene checks.
10. [x] Add async soak control and status checks.
11. [x] Add golden registry with validation.
12. [x] Add timing baseline under `goldens/`.
13. [x] Add spec ledger with schema and validator.
14. [x] Add ADR template/index/validator.
15. [x] Add CI smoke job with timing artifact upload.
16. [x] Add scientific execution roadmap (`docs/SCIENCE_PLAN.md`).
17. [x] Add scientific terminology policy (`candidate`/`adversary`).
18. [x] Migrate gauntlet default spec to adversary naming.
19. [x] Keep backward compatibility for legacy gauntlet keys.
20. [x] Migrate status output labels to scientific terms.
21. [x] Keep backward compatibility for legacy strategy directories.
22. [x] Add adversary strategy directory.
23. [x] Add adversary probe registry artifacts.
24. [x] Add noisy adversary probe registry artifacts.
25. [x] Add adversary probe suite artifact.
26. [x] Add adversarial-extortion technical note.
27. [x] Migrate AFK mission controller terminology.
28. [x] Keep AFK legacy artifact mirrors for compatibility.
29. [x] Route AFK Rust builds through `tools/rust_exec.sh`.
30. [x] Harden JuNest rust fallback setup in `rust_exec`.
31. [x] Add JuNest auto-repair for missing Rust packages.
32. [x] Add deterministic environment metadata recorder.
33. [x] Add timing regression checker against baselines.
34. [x] Add spec-ledger markdown rollup checker.
35. [x] Add release manifest generator with checksums.
36. [x] Add release hygiene checker script.
37. [x] Add security false-positive allowlist policy.
38. [x] Add allowlist expiration validator.
39. [x] Add repo-managed hooks (`pre-commit`, `pre-push`).
40. [x] Add hook installer script.
41. [x] Add audited hook bypass log writer.
42. [x] Add experimental protocol documentation.
43. [x] Add data management documentation.
44. [x] Add statistical practice documentation.
45. [x] Add release process documentation.
46. [x] Add changelog scaffold.
47. [x] Add control tests for governance/tooling checks.
48. [x] Wire tranche checks into `make gate`.
49. [x] Validate baseline (`make doctor`, `make test-quick`, `make gate`).
50. [x] Update `docs/AGENT_LOG.md` with tranche outcomes.
51. [x] Add formal methods posture documentation (`docs/FORMAL_METHODS.md`).
52. [x] Add solver-tool availability probe (`scripts/formal/check_formal_tooling.py`).
53. [x] Add deterministic certification invariant check (`scripts/formal/check_certify_invariants.py`).
54. [x] Add `make test-formal-smoke` target.
55. [x] Add `make test-formal-tools` target.
56. [x] Wire formal checks into integration gate.
57. [x] Add example corpus JSON validation (`scripts/test/check_examples_json.py`).
58. [x] Add `make test-examples-json` target.
59. [x] Wire example validation into integration gate.
60. [x] Add markdown link integrity validator (`scripts/test/check_markdown_links.py`).
61. [x] Add `make test-doc-links` target.
62. [x] Wire link integrity checks into integration gate.
63. [x] Add artifact layout validator (`scripts/test/check_artifact_layout.py`).
64. [x] Add `make test-artifact-layout` target.
65. [x] Add bypass-log structural validator (`scripts/test/check_bypass_log.py`).
66. [x] Add `make test-bypass-log` target.
67. [x] Add artifact policy linter for `.gitignore` (`scripts/test/check_gitignore_artifacts_policy.py`).
68. [x] Add `make test-gitignore-policy` target.
69. [x] Add spec target-date validator (`scripts/test/check_spec_dates.py`).
70. [x] Add `make test-spec-dates` target.
71. [x] Wire date-validation checks into integration gate.
72. [x] Expand ignored-artifact policy to include formal/release/report buckets.
73. [x] Add `artifacts/release/.gitkeep`.
74. [x] Add `artifacts/formal/.gitkeep`.
75. [x] Add `artifacts/reports/.gitkeep`.
76. [x] Integrate environment metadata capture into harness execution.
77. [x] Add experiment catalog generator (`scripts/report/build_experiment_catalog.py`).
78. [x] Add generated experiment catalog doc (`docs/EXPERIMENT_CATALOG.md`).
79. [x] Add experiment catalog artifact output (`artifacts/reports/experiment_catalog.json`).
80. [x] Add `make update-experiment-catalog` target.
81. [x] Add `make test-experiment-catalog` drift check target.
82. [x] Wire catalog drift check into integration gate.
83. [x] Add artifact summary generator (`scripts/report/summarize_artifacts.py`).
84. [x] Add `make report-artifact-summary` target.
85. [x] Wire artifact summary generation into integration gate.
86. [x] Extend `make help` with tranche-2 command surface.
87. [x] Extend README command index with tranche-2 controls.
88. [x] Extend README baseline-layout section with formal/catalog pointers.
89. [x] Keep security tooling strict-only for release posture (`gate-strict`).
90. [x] Keep solver-tool checks non-strict in integration gate for dev ergonomics.
91. [x] Preserve no-network deterministic defaults in harness.
92. [x] Preserve explicit seed policy for all harness runs.
93. [x] Preserve stable locale and timezone defaults.
94. [x] Preserve compatibility paths for legacy naming (`vampire`, `saint`).
95. [x] Preserve canonical scientific naming in active docs/CLI output.
96. [x] Keep Rust as simulation truth boundary.
97. [x] Keep Python as orchestration/certification boundary.
98. [x] Ensure all new tranche scripts emit machine-readable artifacts.
99. [x] Ensure all new tranche scripts run without external network dependencies.
100. [x] Re-run `make test-quick` after tranche-2 edits.
101. [x] Re-run `make gate` after tranche-2 edits.
102. [x] Re-run release-manifest/hygiene checks after tranche-2 edits.
103. [x] Record tranche-2 execution in `docs/AGENT_LOG.md`.
104. [x] Keep one-Concern command targets with deterministic naming (`test-*`, `report-*`, `update-*`).
105. [x] Preserve auditable release artifact location (`artifacts/release/<version>/`).
106. [x] Preserve auditable security artifact location (`artifacts/security/`).
107. [x] Preserve auditable timing artifact location (`artifacts/timing/`).
108. [x] Preserve auditable formal artifact location (`artifacts/formal/`).
109. [x] Preserve auditable report artifact location (`artifacts/reports/`).
110. [x] Keep tranche list itself explicit, long, and executable.
111. [x] Add examples unique-id validator (`scripts/test/check_examples_unique_ids.py`).
112. [x] Add scripts executable-bit validator (`scripts/test/check_scripts_executable.py`).
113. [x] Add script/python compile validator (`scripts/test/check_scripts_compile.py`).
114. [x] Add README command-surface validator (`scripts/test/check_readme_command_surface.py`).
115. [x] Add docs index core-link validator (`scripts/test/check_docs_index_core.py`).
116. [x] Add tranche completion validator (`scripts/test/check_tranches_complete.py`).
117. [x] Add tranche status generator (`scripts/report/build_tranche_status.py`).
118. [x] Add release manifest schema validator (`scripts/release/check_release_manifest_schema.py`).
119. [x] Add release checksum validator (`scripts/release/check_release_checksums.py`).
120. [x] Add reproducibility bundle index generator (`scripts/report/build_repro_bundle_index.py`).
121. [x] Add quality-assurance policy doc (`docs/QUALITY_ASSURANCE.md`).
122. [x] Add reproducibility policy doc (`docs/REPRODUCIBILITY.md`).
123. [x] Add release manifest schema contract (`schemas/release_manifest.schema.json`).
124. [x] Add `make test-examples-unique-ids` target.
125. [x] Add `make test-scripts-exec` target.
126. [x] Add `make test-scripts-compile` target.
127. [x] Add `make test-readme-commands` target.
128. [x] Add `make test-docs-index` target.
129. [x] Add `make test-tranches` target.
130. [x] Add `make update-tranche-status` target.
131. [x] Add `make test-tranche-status` target.
132. [x] Add `make test-release-manifest-schema` target.
133. [x] Add `make test-release-checksums` target.
134. [x] Add `make report-repro-bundle` target.
135. [x] Wire new tranche checks into `make gate`.
136. [x] Extend `make help` with tranche-expansion commands.
137. [x] Extend root README command index with tranche-expansion commands.
138. [x] Extend docs index with QA/repro links.
139. [x] Extend schema index with release-manifest schema.
140. [x] Extend release process doc with manifest/checksum validation commands.
141. [x] Extend control test required-file checks for QA/repro/schema assets.
142. [x] Extend control test Makefile target checks for tranche-expansion commands.
143. [x] Keep all tranche-expansion scripts executable.
144. [x] Keep tranche-expansion scripts local-only and deterministic.
145. [x] Emit machine-readable artifact for examples unique-id check.
146. [x] Emit machine-readable artifact for tranche status (`artifacts/reports/tranche_status.json`).
147. [x] Emit machine-readable reproducibility bundle index (`artifacts/reports/repro_bundle_index.json`).
148. [x] Keep release-manifest schema validation decoupled from external tools.
149. [x] Keep release-checksum validation reproducible and content-addressed.
150. [x] Preserve compatibility with existing `gate-strict` security behavior.
151. [x] Ensure docs link validator ignores http/mailto anchors safely.
152. [x] Ensure tranche validator enforces sequential numbering.
153. [x] Ensure tranche validator fails on unchecked items.
154. [x] Ensure scripts compile validator covers both `scripts/` and `grlab/`.
155. [x] Ensure docs-index validator protects critical scientific docs.
156. [x] Ensure README validator protects operational command discoverability.
157. [x] Ensure release schema validator checks all existing release manifests.
158. [x] Ensure release checksum validator verifies each listed file hash.
159. [x] Ensure reproducibility bundle index includes replay command pointer.
160. [x] Ensure gate emits tranche/report artifacts for auditability.
161. [x] Regenerate experiment catalog after tranche-expansion edits.
162. [x] Regenerate tranche status summary after tranche-expansion edits.
163. [x] Re-run `make test-quick` after tranche-expansion edits.
164. [x] Re-run `make gate` after tranche-expansion edits.
165. [x] Re-run `make release-manifest RELEASE_VERSION=dev` after tranche-expansion edits.
166. [x] Re-run `make test-release-manifest-schema` after manifest generation.
167. [x] Re-run `make test-release-checksums RELEASE_VERSION=dev` after manifest generation.
168. [x] Re-run `make test-release-hygiene RELEASE_VERSION=dev` after manifest checks.
169. [x] Re-run `make doctor` after tranche-expansion edits.
170. [x] Update `docs/AGENT_LOG.md` with tranche-expansion execution evidence.
171. [x] Preserve goldens/artifacts separation while expanding report surfaces.
172. [x] Preserve deterministic seed defaults while expanding QA controls.
173. [x] Preserve no-network posture while expanding validators.
174. [x] Preserve process hygiene checks while adding tranche checks.
175. [x] Preserve formal-smoke behavior with expected singular-case handling.
176. [x] Preserve tool-adapter abstraction for security and SBOM commands.
177. [x] Preserve release artifact location convention under `artifacts/release/<version>/`.
178. [x] Preserve report artifact location convention under `artifacts/reports/`.
179. [x] Preserve formal artifact location convention under `artifacts/formal/`.
180. [x] Keep tranche list very long, inclusive, and operationally executed.
181. [x] Add CI smoke workflow validator (`scripts/test/check_ci_smoke.py`).
182. [x] Add policy expiry validator (`scripts/test/check_policy_expirations.py`).
183. [x] Add spec evidence-link validator (`scripts/test/check_spec_evidence_links.py`).
184. [x] Add release process command validator (`scripts/test/check_release_doc_commands.py`).
185. [x] Add make-help surface validator (`scripts/test/check_make_help_surface.py`).
186. [x] Add required example asset validator (`scripts/test/check_required_examples.py`).
187. [x] Add report JSON parse validator (`scripts/test/check_reports_json_valid.py`).
188. [x] Add command inventory generator (`scripts/report/build_command_inventory.py`).
189. [x] Add validator inventory generator (`scripts/report/build_validator_inventory.py`).
190. [x] Add policy inventory generator (`scripts/report/build_policy_inventory.py`).
191. [x] Add CI policy doc (`docs/CI_POLICY.md`).
192. [x] Add dependency policy doc (`docs/DEPENDENCY_POLICY.md`).
193. [x] Add `make test-ci-smoke` target.
194. [x] Add `make test-policy-expirations` target.
195. [x] Add `make test-spec-evidence` target.
196. [x] Add `make test-release-doc` target.
197. [x] Add `make test-make-help` target.
198. [x] Add `make test-required-examples` target.
199. [x] Add `make test-reports-json` target.
200. [x] Add `make update-command-inventory` target.
201. [x] Add `make test-command-inventory` target.
202. [x] Add `make update-validator-inventory` target.
203. [x] Add `make test-validator-inventory` target.
204. [x] Add `make update-policy-inventory` target.
205. [x] Add `make test-policy-inventory` target.
206. [x] Wire CI/policy/spec-evidence checks into `make gate`.
207. [x] Wire command/validator/policy inventory drift checks into `make gate`.
208. [x] Wire report JSON validation into `make gate`.
209. [x] Extend `make help` to include tranche-expansion-II commands.
210. [x] Extend root README command index for tranche-expansion-II commands.
211. [x] Extend docs index with CI/dependency policy docs.
212. [x] Extend docs index with generated inventory docs.
213. [x] Extend control tests for tranche-expansion-II targets/docs.
214. [x] Add allowlist policy for intentional duplicate example ids (`policy/examples_id_allowlist.json`).
215. [x] Adapt unique-id validator to enforce only non-allowlisted duplicates.
216. [x] Emit policy-expiration report artifact (`artifacts/reports/policy_expirations.json`).
217. [x] Emit spec-evidence report artifact (`artifacts/reports/spec_evidence_links.json`).
218. [x] Emit command inventory artifact (`artifacts/reports/command_inventory.json`).
219. [x] Emit validator inventory artifact (`artifacts/reports/validator_inventory.json`).
220. [x] Emit policy inventory artifact (`artifacts/reports/policy_inventory.json`).
221. [x] Emit generated command inventory doc (`docs/COMMAND_INVENTORY.md`).
222. [x] Emit generated validator inventory doc (`docs/VALIDATOR_INVENTORY.md`).
223. [x] Emit generated policy inventory doc (`docs/POLICY_INVENTORY.md`).
224. [x] Keep CI smoke policy tied to `make test-quick` for deterministic fast loop.
225. [x] Keep policy expiry checks date-driven and machine-readable.
226. [x] Keep evidence-link checks explicit and traceable to ledger entries.
227. [x] Keep release process docs command-complete and test-verified.
228. [x] Keep `make help` output as executable contract surface.
229. [x] Keep required examples validated as scientific fixture baseline.
230. [x] Keep inventory docs generated from source data, not manual edits.
231. [x] Keep report JSON artifacts parse-valid before gate success.
232. [x] Keep deterministic/no-network posture while expanding validators.
233. [x] Keep all new scripts executable and local-only.
234. [x] Keep compatibility duplicate IDs explicit and policy-governed.
235. [x] Keep release manifest validation separate from external dependency tooling.
236. [x] Keep schema/index docs aligned with generated inventory outputs.
237. [x] Regenerate experiment catalog after tranche-expansion-II edits.
238. [x] Regenerate tranche status summary after tranche-expansion-II edits.
239. [x] Generate reproducibility bundle index after tranche-expansion-II edits.
240. [x] Generate command inventory after tranche-expansion-II edits.
241. [x] Generate validator inventory after tranche-expansion-II edits.
242. [x] Generate policy inventory after tranche-expansion-II edits.
243. [x] Re-run `make test-quick` after tranche-expansion-II edits.
244. [x] Re-run `make gate` after tranche-expansion-II edits.
245. [x] Re-run `make doctor` after tranche-expansion-II edits.
246. [x] Re-run `make release-manifest RELEASE_VERSION=dev` after tranche-expansion-II edits.
247. [x] Re-run `make test-release-manifest-schema` after manifest regeneration.
248. [x] Re-run `make test-release-checksums RELEASE_VERSION=dev` after manifest regeneration.
249. [x] Re-run `make test-release-hygiene RELEASE_VERSION=dev` after manifest regeneration.
250. [x] Update `docs/AGENT_LOG.md` with tranche-expansion-II evidence.
251. [x] Preserve strict security-tool requirement behavior for `gate-strict`.
252. [x] Preserve formal-tool non-strict advisory behavior in `gate`.
253. [x] Preserve process hygiene controls under expanded gate surface.
254. [x] Preserve artifact bucket contracts while adding inventory artifacts.
255. [x] Preserve command surface determinism by validating help/readme/doc indices.
256. [x] Preserve traceability by validating spec evidence links.
257. [x] Preserve CI smoke semantics by validating workflow content.
258. [x] Preserve policy governance by validating expiry dates.
259. [x] Preserve baseline scientific fixtures by validating required examples.
260. [x] Keep tranche list even longer, broader, and fully executed.
261. [x] Add schema JSON validity validator (`scripts/test/check_schema_json_valid.py`).
262. [x] Add policy JSON validity validator (`scripts/test/check_policy_json_valid.py`).
263. [x] Add hook contract validator (`scripts/test/check_hooks_contract.py`).
264. [x] Add artifact `.gitkeep` validator (`scripts/test/check_artifact_gitkeeps.py`).
265. [x] Add release-manifest required-entry validator (`scripts/test/check_release_manifest_entries.py`).
266. [x] Add timing artifact presence validator (`scripts/test/check_timing_artifacts_presence.py`).
267. [x] Add generated-doc presence validator (`scripts/test/check_generated_docs_presence.py`).
268. [x] Add schema inventory generator (`scripts/report/build_schema_inventory.py`).
269. [x] Add artifact-bucket inventory generator (`scripts/report/build_artifact_bucket_inventory.py`).
270. [x] Add `make test-schema-json` target.
271. [x] Add `make test-policy-json` target.
272. [x] Add `make test-hooks-contract` target.
273. [x] Add `make test-artifact-gitkeeps` target.
274. [x] Add `make test-release-manifest-entries` target.
275. [x] Add `make test-timing-artifacts` target.
276. [x] Add `make test-generated-docs` target.
277. [x] Add `make update-schema-inventory` target.
278. [x] Add `make test-schema-inventory` target.
279. [x] Add `make update-artifact-buckets` target.
280. [x] Add `make test-artifact-buckets` target.
281. [x] Wire schema/policy/hook/artifact validators into `make gate`.
282. [x] Wire timing artifact presence validation into `make gate`.
283. [x] Wire generated-doc presence validation into `make gate`.
284. [x] Wire schema/artifact inventory drift checks into `make gate`.
285. [x] Extend `make help` with tranche-expansion-IV command surface.
286. [x] Extend root README command index with tranche-expansion-IV commands.
287. [x] Extend docs index with generated schema/artifact inventory docs.
288. [x] Extend control tests for tranche-expansion-IV docs/targets.
289. [x] Keep validator scripts executable and local-only.
290. [x] Preserve deterministic execution posture for new validators.
291. [x] Preserve no-network default posture for expanded gate.
292. [x] Preserve compatibility naming while enforcing policy guards.
293. [x] Ensure hook policy remains auditable through bypass logging checks.
294. [x] Ensure artifact-retention structure is enforced via `.gitkeep` checks.
295. [x] Ensure release manifest content includes expected baseline assets.
296. [x] Ensure timing artifacts are present before gate completion.
297. [x] Ensure generated docs required by governance are materially present.
298. [x] Ensure schema inventory remains generated, not hand-edited.
299. [x] Ensure artifact-bucket inventory remains generated, not hand-edited.
300. [x] Preserve command surface traceability through generated inventories.
301. [x] Regenerate tranche status summary after tranche-expansion-IV edits.
302. [x] Regenerate experiment catalog after tranche-expansion-IV edits.
303. [x] Regenerate command inventory after tranche-expansion-IV edits.
304. [x] Regenerate validator inventory after tranche-expansion-IV edits.
305. [x] Regenerate policy inventory after tranche-expansion-IV edits.
306. [x] Generate schema inventory after tranche-expansion-IV edits.
307. [x] Generate artifact-bucket inventory after tranche-expansion-IV edits.
308. [x] Generate reproducibility bundle index after tranche-expansion-IV edits.
309. [x] Re-run `make test-quick` after tranche-expansion-IV edits.
310. [x] Re-run `make doctor` after tranche-expansion-IV edits.
311. [x] Re-run `make gate` after tranche-expansion-IV edits.
312. [x] Re-run `make release-manifest RELEASE_VERSION=dev` after tranche-expansion-IV edits.
313. [x] Re-run `make test-release-manifest-schema` after manifest regeneration.
314. [x] Re-run `make test-release-manifest-entries RELEASE_VERSION=dev` after manifest regeneration.
315. [x] Re-run `make test-release-checksums RELEASE_VERSION=dev` after manifest regeneration.
316. [x] Re-run `make test-release-hygiene RELEASE_VERSION=dev` after manifest regeneration.
317. [x] Update `docs/AGENT_LOG.md` with tranche-expansion-IV evidence.
318. [x] Preserve strict security requirements in `gate-strict`.
319. [x] Preserve non-strict security behavior in `gate` for dev mode.
320. [x] Preserve process hygiene enforcement under expanded gate.
321. [x] Preserve ledger/schema governance under expanded gate.
322. [x] Preserve ADR validation controls under expanded gate.
323. [x] Preserve golden registry validation controls under expanded gate.
324. [x] Preserve timing baseline regression controls under expanded gate.
325. [x] Preserve release schema/checksum hygiene controls under expanded gate model.
326. [x] Preserve report JSON validity under expanded report generation.
327. [x] Preserve evidence-link traceability between specs and artifacts/docs.
328. [x] Preserve CI smoke determinism checks via workflow validator.
329. [x] Preserve policy-expiry governance via automated date checks.
330. [x] Preserve command/help discoverability via automated checks.
331. [x] Preserve required scientific fixtures via explicit example checks.
332. [x] Preserve inventory drift detection as deterministic gate control.
333. [x] Preserve artifact-bucket auditability via generated summary docs.
334. [x] Preserve schema auditability via generated schema inventory docs.
335. [x] Preserve policy auditability via generated policy inventory docs.
336. [x] Preserve validator auditability via generated validator inventory docs.
337. [x] Preserve command auditability via generated command inventory docs.
338. [x] Keep tranche ledger sequential and fully checked.
339. [x] Keep tranche execution broad across code, docs, policy, CI, and release controls.
340. [x] Keep tranche program very long, inclusive, and executed end-to-end.
341. [x] Run deep external-source research pass for science-direction reset.
342. [x] Collect primary repeated-game literature for memory-one/ZD/extortion/generosity claims.
343. [x] Collect benchmark-ecosystem references (Axelrod/OpenSpiel).
344. [x] Collect formal solver and verification references (SMT-LIB, Z3, cvc5, rsmt2, Kani, Prusti, Creusot).
345. [x] Collect probabilistic model-checking references (PRISM, Storm).
346. [x] Collect reproducibility operations references (Snakemake, DVC, NASEM).
347. [x] Collect deterministic performance/testing references (Criterion, nextest).
348. [x] Verify source URL health with explicit HTTP checks.
349. [x] Add source registry doc (`docs/RESEARCH_SOURCES.md`).
350. [x] Encode source identifiers by domain (IPD/formal/Rust-Python/ops).
351. [x] Map each source to explicit Concord implications.
352. [x] Add source-backed agenda doc (`docs/RESEARCH_AGENDA.md`).
353. [x] Expand science plan phases to include formal-claim strengthening.
354. [x] Define broad tranche queue across theory, Rust, formal solvers, orchestration, stats, and release operations.
355. [x] Link research docs from docs index (`docs/README.md`).
356. [x] Link context index to research bibliography (`docs/context/README.md`).
357. [x] Record new formal-method ambiguity in spec ledger (`SG-002`).
358. [x] Record linked research question for solver obligations (`SQ-002`).
359. [x] Record temporary solver-posture assumption (`SA-002`).
360. [x] Keep evidence links in ledger pointing only to local auditable paths.
361. [x] Preserve Rust/Python boundary while updating research direction.
362. [x] Preserve deterministic/no-network test posture during research tranche.
363. [x] Preserve formal checks as advisory in integration gate pending claim-class spec resolution.
364. [x] Preserve strict release posture for optional security tooling.
365. [x] Keep research outputs diffable textual docs.
366. [x] Keep research outputs compatible with existing governance validators.
367. [x] Regenerate tranche summary/status artifacts after tranche-extension-V edits.
368. [x] Re-run `make test-quick` after research-doc edits.
369. [x] Re-run `make test-spec-ledger` after ledger updates.
370. [x] Re-run `make test-spec-evidence` after ledger evidence-link updates.
371. [x] Re-run `make test-doc-links` after adding research docs.
372. [x] Re-run `make test-docs-index` after docs-index updates.
373. [x] Re-run `make test-tranches` after tranche-extension-V edits.
374. [x] Re-run `make test-tranche-status` after tranche summary regeneration.
375. [x] Re-run `make gate` after research tranche integration.
376. [x] Update `docs/AGENT_LOG.md` with research tranche evidence.
377. [x] Preserve source traceability for future claim audits.
378. [x] Preserve assumption traceability for unresolved formal-method policy decisions.
379. [x] Preserve compatibility with current command/gate surface while adding research direction.
380. [x] Keep tranche ledger long, inclusive, and executed across research + implementation governance.
381. [x] Add source-mapped research tranche matrix (`docs/RESEARCH_TRANCHE_MATRIX.md`).
382. [x] Define explicit tranche IDs (`RT-001`..`RT-060`) for science build sequencing.
383. [x] Map tranche packages to source IDs for traceability.
384. [x] Map tranche packages to minimum verification commands/artifacts.
385. [x] Cover theory/spec tranche class in execution matrix.
386. [x] Cover Rust engine tranche class in execution matrix.
387. [x] Cover formal solver tranche class in execution matrix.
388. [x] Cover Python orchestration tranche class in execution matrix.
389. [x] Cover benchmark/evaluation tranche class in execution matrix.
390. [x] Cover statistics/evidence tranche class in execution matrix.
391. [x] Cover reproducibility/release operations tranche class in execution matrix.
392. [x] Add explicit sequencing prerequisites to tranche matrix.
393. [x] Extend docs index with tranche matrix entry.
394. [x] Extend research source registry with classical cooperation references.
395. [x] Re-run URL health checks for bibliography set after source expansion.
396. [x] Regenerate tranche summary/status after tranche-extension-VI edits.
397. [x] Re-run `make test-quick` after tranche-extension-VI edits.
398. [x] Re-run `make test-tranches` and `make test-tranche-status` after tranche-extension-VI edits.
399. [x] Re-run `make gate` after tranche-extension-VI edits.
400. [x] Keep tranche program broader and deeper while preserving deterministic controls.
401. [x] Continue research/planning pass on request with deeper scientific prioritization.
402. [x] Expand source registry with Kani feature-support reference.
403. [x] Expand source registry with PRISM tutorial reference.
404. [x] Expand source registry with MDP model-checking algorithm guide reference.
405. [x] Add explicit research-opinion document (`docs/RESEARCH_OPINIONS.md`).
406. [x] Document strong project opinions on Rust/Python/formal boundaries.
407. [x] Document explicit "build first" priorities for next cycles.
408. [x] Document explicit "do not build yet" anti-pattern list.
409. [x] Add 12-week phased research implementation priorities.
410. [x] Add decision gates for promoting advisory checks to required checks.
411. [x] Add failure conditions that freeze expansion until foundations are repaired.
412. [x] Link research-opinion doc in docs index.
413. [x] Re-run bibliography URL checks for newly added references.
414. [x] Regenerate tranche summary/status after tranche-extension-VII edits.
415. [x] Re-run `make test-quick` after tranche-extension-VII edits.
416. [x] Re-run `make test-tranches` and `make test-tranche-status` after tranche-extension-VII edits.
417. [x] Re-run `make test-doc-links` after research-opinion additions.
418. [x] Re-run `make test-docs-index` after docs index updates.
419. [x] Re-run `make gate` after tranche-extension-VII edits.
420. [x] Keep long-form research planning active while preserving deterministic gate integrity.
421. [x] Start tranche-extension-VIII with inclusive cross-domain scope.
422. [x] Add machine-readable claim class specification (`specs/claim_classes.yaml`).
423. [x] Add claim class schema contract (`schemas/claim_classes.schema.json`).
424. [x] Add claim class validator (`scripts/test/check_claim_classes.py`).
425. [x] Add claim matrix generator (`scripts/report/build_claim_matrix.py`).
426. [x] Add research docs validator (`scripts/test/check_research_docs.py`).
427. [x] Add claim taxonomy policy doc (`docs/CLAIM_TAXONOMY.md`).
428. [x] Add formal obligation mapping doc (`docs/FORMAL_OBLIGATION_TABLE.md`).
429. [x] Add benchmark program doc (`docs/BENCHMARK_PROGRAM.md`).
430. [x] Add execution rhythm doc (`docs/EXECUTION_RHYTHM.md`).
431. [x] Add research risk register doc (`docs/RESEARCH_RISK_REGISTER.md`).
432. [x] Extend docs index with new research-governance docs.
433. [x] Extend root README command index with claim-matrix/claim-class commands.
434. [x] Extend schema reference doc with claim-class schema.
435. [x] Extend generated-doc presence validator with `docs/CLAIM_MATRIX.md`.
436. [x] Extend docs-index core validator with research/claim links.
437. [x] Add Makefile target `test-research-docs`.
438. [x] Add Makefile target `test-claim-classes`.
439. [x] Add Makefile target `update-claim-matrix`.
440. [x] Add Makefile target `test-claim-matrix`.
441. [x] Add new targets to Makefile `.PHONY` surface.
442. [x] Add new targets to `make help` command surface.
443. [x] Wire research-doc checks into `make gate`.
444. [x] Wire claim-class validation into `make gate`.
445. [x] Wire claim-matrix drift check into `make gate`.
446. [x] Keep claim-class spec textual and diffable.
447. [x] Keep claim-class validator local-only and deterministic.
448. [x] Keep claim-matrix generator artifact-writing deterministic.
449. [x] Keep research-doc validator deterministic and low-cost.
450. [x] Keep no-network posture for new gate checks.
451. [x] Keep strict-gate policy separation for high-formality claim classes.
452. [x] Include explicit evidence-class taxonomy (`empirical`, `formal`, `hybrid`, `operational`, `assumption`).
453. [x] Include strict-gate-required flag in machine-readable claim classes.
454. [x] Include required checks list per claim class.
455. [x] Include required artifacts list per claim class.
456. [x] Include claim summary scope text per claim class.
457. [x] Add claim class coverage for empirical performance claims.
458. [x] Add claim class coverage for robustness claims.
459. [x] Add claim class coverage for formal invariance claims.
460. [x] Add claim class coverage for cross-solver agreement claims.
461. [x] Add claim class coverage for probabilistic-bound claims.
462. [x] Add claim class coverage for reproducibility claims.
463. [x] Add claim class coverage for policy-exception assumption claims.
464. [x] Add formal-obligation table entry per claim class.
465. [x] Add benchmark family definitions in benchmark program doc.
466. [x] Add benchmark governance rules in benchmark program doc.
467. [x] Add daily cadence controls in execution rhythm doc.
468. [x] Add weekly cadence controls in execution rhythm doc.
469. [x] Add release-candidate cadence controls in execution rhythm doc.
470. [x] Add risk register entries for solver disagreement and benchmark overfit.
471. [x] Add risk register entries for orchestration drift and artifact incompleteness.
472. [x] Add risk register review cadence guidance.
473. [x] Add source-registry integration for claim governance posture.
474. [x] Preserve source-to-work-package traceability through tranche expansion.
475. [x] Preserve spec-ledger assumption transparency during claim-taxonomy expansion.
476. [x] Preserve Rust truth boundary while adding research governance controls.
477. [x] Preserve Python orchestration boundary while adding claim governance controls.
478. [x] Preserve artifact-bucket auditability while adding claim matrix artifacts.
479. [x] Preserve command-surface discoverability with new make targets.
480. [x] Preserve validator inventory completeness with new validators.
481. [x] Preserve schema inventory completeness with new schema.
482. [x] Preserve generated-doc inventory semantics with claim matrix doc.
483. [x] Generate claim matrix doc/artifact from claim classes (`update-claim-matrix`).
484. [x] Regenerate schema inventory after claim-schema addition.
485. [x] Regenerate command inventory after Makefile target expansion.
486. [x] Regenerate validator inventory after new validator scripts.
487. [x] Regenerate tranche status summary after tranche-extension-VIII edits.
488. [x] Re-run claim-class validator after initial write.
489. [x] Re-run research-doc validator after docs/index updates.
490. [x] Re-run docs-link validation after research-doc additions.
491. [x] Re-run docs-index core validation after required-link expansion.
492. [x] Re-run schema-json validation after schema addition.
493. [x] Re-run schema-inventory drift check after schema inventory regeneration.
494. [x] Re-run command-inventory drift check after command inventory regeneration.
495. [x] Re-run validator-inventory drift check after validator inventory regeneration.
496. [x] Re-run generated-doc presence check after claim matrix generation.
497. [x] Re-run `make test-quick` after tranche-extension-VIII edits.
498. [x] Re-run `make test-tranches` and `make test-tranche-status` after tranche-extension-VIII edits.
499. [x] Re-run `make gate` after tranche-extension-VIII edits.
500. [x] Update `docs/AGENT_LOG.md` with tranche-extension-VIII evidence.
501. [x] Add tranche item for reproducibility-oriented claim-class auditing.
502. [x] Add tranche item for formal-obligation staged adoption policy.
503. [x] Add tranche item for benchmark governance anti-overfit guardrails.
504. [x] Add tranche item for risk register maintenance practice.
505. [x] Add tranche item for evidence-class declaration requirements.
506. [x] Add tranche item for strict-gate-required claim flag semantics.
507. [x] Add tranche item for claim-matrix drift-control practice.
508. [x] Add tranche item for inclusive documentation across science + ops + governance.
509. [x] Add tranche item for integrating new research docs into repo index.
510. [x] Add tranche item for integrating new command surface into root README.
511. [x] Add tranche item for integrating new schema into schema reference docs.
512. [x] Add tranche item for integrating claim matrix into generated-doc checks.
513. [x] Add tranche item for integrating research docs into gate coverage.
514. [x] Add tranche item for integrating claim classes into gate coverage.
515. [x] Add tranche item for integrating claim matrix drift checks into gate coverage.
516. [x] Add tranche item for inclusive tranche wave coverage across files/scripts/docs/policy.
517. [x] Add tranche item for post-change deterministic validation sweep.
518. [x] Add tranche item for tranche summary regeneration at new scale.
519. [x] Add tranche item for maintaining long-form inclusive tranche program continuity.
520. [x] Keep tranche program very long, inclusive, and fully executed in tranche-extension-VIII.
521. [x] Start tranche-extension-IX for claim-register execution infrastructure.
522. [x] Add machine-readable claim register spec (`specs/claim_register.yaml`).
523. [x] Add claim register schema contract (`schemas/claim_register.schema.json`).
524. [x] Add claim register validator (`scripts/test/check_claim_register.py`).
525. [x] Add claim register summary generator (`scripts/report/build_claim_register_summary.py`).
526. [x] Add claim workflow policy doc (`docs/CLAIM_WORKFLOW.md`).
527. [x] Add claim register generated doc surface (`docs/CLAIM_REGISTER.md`).
528. [x] Extend research-doc validator to require claim workflow assets.
529. [x] Extend generated-doc validator to require `docs/CLAIM_REGISTER.md`.
530. [x] Extend docs-index core validator to require claim register link.
531. [x] Extend README command surface validator with claim-register commands.
532. [x] Extend repo control tests with claim schemas.
533. [x] Extend repo control tests with claim-register make targets.
534. [x] Add Makefile target `test-claim-register`.
535. [x] Add Makefile target `update-claim-register-summary`.
536. [x] Add Makefile target `test-claim-register-summary`.
537. [x] Add claim-register targets to `.PHONY`.
538. [x] Add claim-register targets to `make help`.
539. [x] Add claim-register commands to root `README.md` command index.
540. [x] Add claim register to root README baseline-layout pointers.
541. [x] Add claim workflow and claim register to docs index.
542. [x] Add claim-register schema pointer to `docs/SCHEMAS.md`.
543. [x] Wire claim-register validation into `make gate`.
544. [x] Wire claim-register summary drift check into `make gate`.
545. [x] Keep claim register entries local-path evidence only (no remote dependency).
546. [x] Keep claim register deterministic and diffable.
547. [x] Keep claim register IDs stable (`CL-*`).
548. [x] Keep class linkage explicit (`claim_class_id` -> `CC-*`).
549. [x] Keep assumption linkage explicit (`assumptions` -> `SA-*`).
550. [x] Keep claim status lifecycle explicit (`draft|active|superseded|retired`).
551. [x] Keep claim update timestamps date-validated.
552. [x] Ensure claim-register validator checks class existence.
553. [x] Ensure claim-register validator checks assumption existence in ledger.
554. [x] Ensure claim-register validator checks evidence-link path existence.
555. [x] Ensure claim-register validator emits machine-readable artifact.
556. [x] Ensure claim-register summary emits machine-readable artifact.
557. [x] Ensure claim-register summary markdown is generated from source of truth.
558. [x] Add active claim coverage for empirical claim classes.
559. [x] Add active claim coverage for operational reproducibility claim class.
560. [x] Add active claim coverage for assumption/policy claim class.
561. [x] Add draft claim coverage for cross-solver class pending implementation.
562. [x] Add draft claim coverage for probabilistic-bound class pending adapters.
563. [x] Add active claim coverage for formal-invariance class.
564. [x] Add claim-register scope text per entry.
565. [x] Add claim-register owner field per entry.
566. [x] Add claim-register evidence-link count reporting in summary.
567. [x] Add claim-register strict-gate-required projection in summary.
568. [x] Keep strict claim classes visible for release policy planning.
569. [x] Keep claim workflow aligned with existing gate model.
570. [x] Keep claim workflow aligned with spec-ledger discipline.
571. [x] Keep claim workflow aligned with evidence-link validation policy.
572. [x] Keep claim workflow aligned with release-manifest reproducibility posture.
573. [x] Keep claim workflow commands scoped to Makefile targets.
574. [x] Keep claim workflow narrow and actionable for AFK operation.
575. [x] Keep claim-register scripts executable and compile-clean.
576. [x] Preserve no-network deterministic posture for claim-register controls.
577. [x] Preserve goldens/artifacts separation while adding claim reports.
578. [x] Preserve report-bucket auditability after adding claim artifacts.
579. [x] Preserve command inventory generation after make-target expansion.
580. [x] Preserve validator inventory generation after new validator scripts.
581. [x] Preserve schema inventory generation after new schema file.
582. [x] Preserve generated-doc checks with expanded generated surfaces.
583. [x] Preserve docs-link integrity after claim workflow docs addition.
584. [x] Preserve docs-index integrity after claim workflow docs addition.
585. [x] Preserve README command integrity after claim command additions.
586. [x] Generate claim register summary via `make update-claim-register-summary`.
587. [x] Re-run claim class matrix generation for consistency.
588. [x] Re-run schema inventory generation after claim-register schema.
589. [x] Re-run command inventory generation after Makefile changes.
590. [x] Re-run validator inventory generation after script changes.
591. [x] Re-run tranche status summary after tranche-extension-IX edits.
592. [x] Re-run `make test-claim-classes` after claim-register additions.
593. [x] Re-run `make test-claim-register` after register additions.
594. [x] Re-run `make test-claim-register-summary` after summary generation.
595. [x] Re-run `make test-research-docs` after workflow/register doc additions.
596. [x] Re-run `make test-schema-json` after schema additions.
597. [x] Re-run `make test-schema-inventory` after schema regeneration.
598. [x] Re-run `make test-command-inventory` after command regeneration.
599. [x] Re-run `make test-validator-inventory` after validator regeneration.
600. [x] Re-run `make test-generated-docs` after claim-register doc generation.
601. [x] Re-run `make test-doc-links` after docs expansion.
602. [x] Re-run `make test-docs-index` after index expansion.
603. [x] Re-run `make test-readme-commands` after command surface expansion.
604. [x] Re-run `make test-quick` after tranche-extension-IX edits.
605. [x] Re-run `make test-tranches` and `make test-tranche-status` after tranche-extension-IX edits.
606. [x] Re-run `make gate` after tranche-extension-IX edits.
607. [x] Update `docs/AGENT_LOG.md` with tranche-extension-IX evidence.
608. [x] Add tranche item for inclusive claim-governance execution across spec/schema/scripts/docs.
609. [x] Add tranche item for deterministic claim-audit reporting surfaces.
610. [x] Add tranche item for claim-lifecycle operationalization.
611. [x] Add tranche item for active/draft claim portfolio tracking.
612. [x] Add tranche item for strict-claim visibility in generated reports.
613. [x] Add tranche item for assumption-linked claim traceability.
614. [x] Add tranche item for evidence-linked claim traceability.
615. [x] Add tranche item for schema-backed claim register safety.
616. [x] Add tranche item for gate-backed claim governance enforcement.
617. [x] Add tranche item for audit-ready claim docs in repo index.
618. [x] Add tranche item for AFK-safe autonomous build expansion execution.
619. [x] Add tranche item for preserving broad tranche inclusivity while deepening implementation.
620. [x] Keep tranche program very long, inclusive, and fully executed in tranche-extension-IX.
621. [x] Start tranche-extension-X for machine-readable risk governance.
622. [x] Add risk register source file (`specs/risk_register.yaml`).
623. [x] Add risk register schema contract (`schemas/risk_register.schema.json`).
624. [x] Add risk register validator (`scripts/test/check_risk_register.py`).
625. [x] Add risk register summary generator (`scripts/report/build_risk_register_summary.py`).
626. [x] Add generated risk register doc (`docs/RISK_REGISTER.md`).
627. [x] Extend research docs validator with generated risk register doc.
628. [x] Extend generated-doc validator with risk register generated doc.
629. [x] Extend docs-index core validator with risk register link requirement.
630. [x] Extend schema reference with risk register schema.
631. [x] Extend root README command surface with risk-register commands.
632. [x] Extend root README baseline layout with risk register summary pointer.
633. [x] Extend docs index with risk register summary pointer.
634. [x] Update research risk register narrative doc to point at machine source.
635. [x] Add Makefile target `test-risk-register`.
636. [x] Add Makefile target `update-risk-register-summary`.
637. [x] Add Makefile target `test-risk-register-summary`.
638. [x] Add risk-register targets to `.PHONY`.
639. [x] Add risk-register targets to `make help`.
640. [x] Add risk-register checks to integration gate.
641. [x] Keep risk register textual and diffable.
642. [x] Keep risk register deterministic and no-network.
643. [x] Keep risk register IDs stable (`RK-*`).
644. [x] Keep risk status lifecycle explicit (`open|mitigated|accepted|closed`).
645. [x] Keep risk domains constrained to known categories.
646. [x] Keep severity constrained (`low|medium|high|critical`).
647. [x] Keep likelihood constrained (`low|medium|high`).
648. [x] Keep owner field mandatory for accountability.
649. [x] Keep mitigation field mandatory for each risk.
650. [x] Keep review_date mandatory and date-validated.
651. [x] Keep evidence_links mandatory and path-validated.
652. [x] Ensure risk register validator emits machine-readable artifact.
653. [x] Ensure risk summary generator emits machine-readable artifact.
654. [x] Ensure risk summary markdown is generated from spec source.
655. [x] Add risk entry for solver-disagreement exposure.
656. [x] Add risk entry for benchmark-overfitting exposure.
657. [x] Add risk entry for artifact/reproducibility incompleteness exposure.
658. [x] Add risk entry for assumption-backlog governance exposure.
659. [x] Add risk entry for performance feedback-loop degradation exposure.
660. [x] Tie risk evidence links to existing docs/specs/scripts.
661. [x] Keep risk review dates future-dated to avoid immediate stale entries.
662. [x] Enforce overdue open/mitigated risk failure policy in validator.
663. [x] Preserve compatibility with existing policy-expiration checks.
664. [x] Preserve compatibility with existing spec-evidence checks.
665. [x] Preserve compatibility with existing claim-register checks.
666. [x] Preserve compatibility with generated-doc inventory checks.
667. [x] Preserve command inventory generation with new targets.
668. [x] Preserve validator inventory generation with new validator script.
669. [x] Preserve schema inventory generation with new schema file.
670. [x] Preserve artifact bucket policy with new report artifacts.
671. [x] Extend repo control tests with risk schema requirements.
672. [x] Extend repo control tests with risk-register make targets.
673. [x] Extend README command validator with risk-register commands.
674. [x] Keep risk register integrated with AFK-friendly make workflows.
675. [x] Keep risk governance integrated with release/repro posture.
676. [x] Generate risk register summary (`update-risk-register-summary`).
677. [x] Regenerate claim matrix summary for consistency.
678. [x] Regenerate claim register summary for consistency.
679. [x] Regenerate schema inventory after schema additions.
680. [x] Regenerate command inventory after target additions.
681. [x] Regenerate validator inventory after script additions.
682. [x] Regenerate tranche status summary after tranche-extension-X edits.
683. [x] Re-run `make test-risk-register` after risk spec additions.
684. [x] Re-run `make test-risk-register-summary` after risk summary generation.
685. [x] Re-run `make test-research-docs` after risk docs/index updates.
686. [x] Re-run `make test-claim-classes` after combined governance updates.
687. [x] Re-run `make test-claim-register` after combined governance updates.
688. [x] Re-run `make test-claim-register-summary` after combined governance updates.
689. [x] Re-run `make test-schema-json` after adding risk schema.
690. [x] Re-run `make test-schema-inventory` after regeneration.
691. [x] Re-run `make test-command-inventory` after regeneration.
692. [x] Re-run `make test-validator-inventory` after regeneration.
693. [x] Re-run `make test-generated-docs` after generated risk doc addition.
694. [x] Re-run `make test-doc-links` after docs expansion.
695. [x] Re-run `make test-docs-index` after index expansion.
696. [x] Re-run `make test-readme-commands` after command expansion.
697. [x] Re-run `make test-quick` after tranche-extension-X edits.
698. [x] Re-run `make test-tranches` and `make test-tranche-status` after tranche-extension-X edits.
699. [x] Re-run `make gate` after tranche-extension-X edits.
700. [x] Update `docs/AGENT_LOG.md` with tranche-extension-X evidence.
701. [x] Add tranche item for inclusive risk governance across specs/schemas/scripts/docs.
702. [x] Add tranche item for generated risk summary integration in docs/automation.
703. [x] Add tranche item for explicit risk lifecycle policy enforcement.
704. [x] Add tranche item for deterministic risk-review audit output.
705. [x] Add tranche item for risk evidence-link local path enforcement.
706. [x] Add tranche item for risk severity/likelihood machine validation.
707. [x] Add tranche item for active risk review-date freshness enforcement.
708. [x] Add tranche item for preserving broad tranche inclusivity in governance layers.
709. [x] Add tranche item for preserving broad tranche inclusivity in report layers.
710. [x] Add tranche item for preserving broad tranche inclusivity in schema layers.
711. [x] Add tranche item for preserving broad tranche inclusivity in validator layers.
712. [x] Add tranche item for preserving broad tranche inclusivity in command-surface layers.
713. [x] Add tranche item for preserving broad tranche inclusivity in docs-index layers.
714. [x] Add tranche item for preserving broad tranche inclusivity in control-test layers.
715. [x] Add tranche item for preserving broad tranche inclusivity in gate layers.
716. [x] Add tranche item for preserving AFK operability while adding governance controls.
717. [x] Add tranche item for preserving deterministic local-first operation while scaling control surface.
718. [x] Add tranche item for preserving machine-auditable evidence at increased tranche scale.
719. [x] Add tranche item for preserving end-to-end validation discipline at increased tranche scale.
720. [x] Keep tranche program very long, inclusive, and fully executed in tranche-extension-X.

## Notes

- Legacy names (`saint`, `vampire`) remain in compatibility paths only.
- Strict release/security gates still require optional tools in environment.
- Formal solver tooling is currently advisory in `gate` and can be promoted later.
