## v162 (contact-surface IDs in schema + worked-example excerpt polish)

- Synthesis~12: added \texttt{contact\_surface\_id} to the minimal tuple table and clarified how to carry extra fields via \texttt{module\_ext}; rebuilt PDF.
- Synthesis~17: expanded the receipt excerpt to show \texttt{fallback\_contact\_surface} with \texttt{contact\_surface\_id} + semantic interface fields; added an explicit digest-binding step (RFC~8785/JCS) to the client skeleton; rebuilt PDF.
- Synthesis~30: added a crisp rule-of-thumb separating long-lived deployment state (\texttt{state\_decl\_id}) from per-contact semantic interfaces (\texttt{contact\_surface\_id}); rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated \texttt{MANIFEST.json}.


## v161 (JCS digest binding + worked-example hygiene)
- Synthesis~17: fixed a stray `\noindent` typo, removed a lingering undocumented Rainbow protocol-filter knob mention, recommended RFC 8785 (JCS) for digest-bound canonical JSON, and labeled the shipped drift-case table; rebuilt PDF.
- Synthesis~12: standardized `contact_surface_id` as `sha256(JCS(contact_surface))` with an RFC 8785 anchor; rebuilt PDF.
- Synthesis~30: minor citation/title cleanup so the Rainbow changelog anchor no longer implies a protocol-filter knob; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.


## v160 (protocol-filter hygiene + worked-example drift cases + retrieval pinning)
- Synthesis~30: corrected protocol-filter discussion (removed undocumented Rainbow knob), clarified that protocol-filter defaults must be pinned by deployed client version, and refreshed retrieval/timing knob citations; rebuilt PDF.
- Synthesis~12: expanded service contact surfaces to include method and time budgets, and added a recommended `contact_surface_id` digest for atomic micro-diffs; rebuilt PDF.
- Synthesis~17: added canonicalization notes, a 3-case drift taxonomy table from the shipped bundle, and a compare-report `user_fast_diff` excerpt; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v159 (routing budgets + retrieval surfaces + user micro-diff)
- Synthesis~30: added Rainbow's application-level routing time budget (`RAINBOW_ROUTING_TIMEOUT`) alongside network-level router timeouts, and documented Rainbow HTTP retrieval knobs (enable/allow/deny/timeouts) as a derived destination surface; updated the pinning checklist; rebuilt PDF.
- Synthesis~12: tightened the definition of service contact surfaces as semantic interfaces (method + shaping defaults) and expanded the state-surface field description to include refresh/timeout budgets and fallback rules; rebuilt PDF.
- Synthesis~17: added a deterministic receipt-level micro-diff algorithm and generalized request-shaping drift to include routing/retrieval budgets; rebuilt PDF.
- Synthesis~24: refreshed archive stamp to v159; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v158 (Rainbow autoconf refresh + line-item glance + attenuation intuition)
- Synthesis~30: made the ``delegated router is a caching proxy'' coupling explicit (IPNI docs), and added Rainbow control-plane knobs (`RAINBOW_AUTOCONF_REFRESH`, `RAINBOW_HTTP_ROUTERS_TIMEOUT`) to the deployed-surface checklist; rebuilt PDF.
- Synthesis~17: added an at-a-glance line-item table and three tiny attenuation intuition rows (keeps shipped bundle label `worked-example-draft-59`); rebuilt PDF.
- Anonymity~B: refreshed archive stamp to v158; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.



## v157 (protocol-filter surfaces + micro-diff hygiene)
- Synthesis~30: made delegated-routing \emph{protocol filters} a first-class request-shaping surface across implementations by adding Rainbow's `--http-routers-filter-protocols` knob alongside Kubo's `IPFS_HTTP_ROUTERS_FILTER_PROTOCOLS`; updated the pinning checklist; rebuilt PDF.
- Synthesis~17: tightened the micro-diff discussion (single state-surface-drift rule, less redundancy) and fixed a stray tab/typo that caused an `exttt{...}` rendering glitch; rebuilt PDF.
- Synthesis~12: synchronized archive stamp to v157; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v156 (Receipt-schema de-bloat + protocol-filter pinning)
- Synthesis~12: removed module-by-module prose (keeps only the stable tuple schema + drift semantics), and tightened contact-surface semantics (path scope + request-shaping defaults); rebuilt PDF.
- Synthesis~30: pinned delegated-routing protocol filtering as a control-plane state surface by adding `IPFS_HTTP_ROUTERS_FILTER_PROTOCOLS` and explicit IPIP-0484 anchor; rebuilt PDF.
- Synthesis~17: added a short client-side algorithmic skeleton and a concrete micro-diff on request-shaping drift (filters); kept shipped bundle label `worked-example-draft-59`; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.


## v155 (Worked-example tightening + projection/state coupling + override precedence)
- Synthesis~17: compressed the receipt section to be schema-nonredundant (explicitly defers tuple mechanics to Synthesis~12 and control-plane pinning to Synthesis~30), added a tiny receipt excerpt, merged drift examples into the micro-diff section, and replaced the long numerical table with the single attenuation shape + validator pointer; rebuilt PDF.
- Synthesis~30: added an explicit ``how to cite'' ownership paragraph (defers pinning mechanics to Synthesis~12/18) and added a compact override-precedence crosswalk for router set resolution (env > config > AutoConf) tied to state-decl change control; rebuilt PDF.
- Anonymity~B: added a short remark explicitly coupling equalization targets to declared projections and pinned state/control-plane surfaces; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.


## v154 (HTTP retrieval surfaces + env override pinning)
- Synthesis~30: tightened AutoConf + override story: pinned `IPFS_HTTP_ROUTERS` and `IPFS_HTTP_ROUTERS_FILTER_PROTOCOLS` (IPIP-484), added Rainbow `RAINBOW_HTTP_ROUTERS` anchor, and added a new short section on `HTTPRetrieval.Enabled` / trustless-HTTP block retrieval as a derived routing surface; rebuilt PDF.
- Synthesis~12: added a short note that delegated-router sets and retrieval-mode switches are legitimate state line items owned by Synthesis~30; rebuilt PDF.
- Synthesis~17: reduced redundancy by pointing schema ownership to Synthesis~12 and control-plane drift ownership to Synthesis~30; kept shipped bundle label `worked-example-draft-59`; rebuilt PDF.
- Synthesis~7: upgraded Pisces citation to NDSS 2013 + canonical PDF link; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v153 (Path-scoped routing + router-selection knobs + social-overlay citation)
- Synthesis~30: added path-scoped Routing V1 endpoints and explicit router-selection knobs (`Routing.Routers`, `Routing.AcceleratedDHTClient`, `IPFS_HTTP_ROUTERS`) to the deployed-surfaces pinning checklist; rebuilt PDF.
- Synthesis~12: clarified that contact surfaces are full URLs including path scope; treated as semantic drift; rebuilt PDF.
- Synthesis~17: added a short note that routing path scope is semantic, plus a drift micro-example; kept shipped bundle label `worked-example-draft-59`; rebuilt PDF.
- Synthesis~7: added Pisces (social-graph random-walk peer discovery) to the restricted-route taxonomy branch; rebuilt PDF.
- Anonymity~B: added a short note on active Sybil/eclipse regimes invalidating benign equalization contracts, with concrete IPFS-DHT references; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v152 (Control-plane anchors + crosswalk keys + drift micro-examples)
- Synthesis~30: updated delegated-routing / AutoConf control-plane anchors to current primary sources (Kubo v0.40.0 feature note + v0.40.1 patch line), and made cache layering explicit by adding the Helia client-side caching surface; replaced the chunked-OHTTP placeholder citations with the IETF draft tracker; rebuilt PDF.
- Synthesis~12: removed a duplicated remark, and added an explicit primary+fallback architecture paragraph (including `fallback_contact_surface`) to align the schema note with the worked example and deployed-surface pinning; rebuilt PDF.
- Synthesis~17: added a short micro-diff section explaining what should change (and what must not) when knobs/state/projection drift across releases; kept the shipped bundle label `worked-example-draft-59`; rebuilt PDF.
- Synthesis~24: added a small table of recommended stable bibkeys (`wiki:*`) for the five published math backbone notes to reduce cross-paper redundancy; rebuilt PDF.
- Synthesis~7: pointed the related-work map to Synthesis~24 as the canonical math-backbone pointer and added a citation stub; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v151 (Worked-example line-item repair + deployed-surface tightening)
- Synthesis~17: repaired a coherence gap in the worked example: the representative line-item table now includes `fallback_contact_surface` (matching the shipped receipt and the numerical slice).
- Synthesis~30: tightened the deployed-surface note by removing a duplicated gateway-drift paragraph, fixing a quotation glitch, explicitly tying the self-hosted-gateway surface to `Gateway.ExposeRoutingAPI`, and adding a short `cid.contact` shared-reader sentence anchored to IPFS Docs.
- Anonymity~B: refreshed archive stamp to v151 (content unchanged; pointer chain unchanged).

## v150 (Citation closure)
- Synthesis~30: fixed an undefined citation by adding a primary-source bibliographic anchor for Kubo v0.40.0 (`/routing/v1` exposure by default) and the associated config knob `Gateway.ExposeRoutingAPI`.
- Synthesis~8 and Synthesis~25: closed two dangling internal citations (`series:selectiondiscipline`, `series:bucketdesign`) so the archive compiles citation-clean.

## v149 (Deployed-surface drift: Kubo v0.40.0 default Routing V1 endpoint)
- Synthesis~30: added a concrete drift surface: Kubo v0.40.0 exposes Routing V1 at `/routing/v1` on the gateway port by default; added citation and clarified why this changes the reader-set and window semantics.
- Synthesis~4: added a one-sentence pointer that delegated-routing/AutoConf/gateway defaults must be treated as declared state; points to Synthesis~30.
- Synthesis~7: refreshed archive stamp to v149 and clarified the deployed-mitigations taxonomy row to include self-hosted gateway exposure.

## v148 (Worked-example schema alignment + deployed drift incidents)
- Synthesis~17: fixed a real coherence bug in the numerical slice: the receipt stores the selection-tax cap as `path_selection_indicator.budget_value` and the mixture term is replay-derived (not stored as its own line item). Updated the field table accordingly (wrapping-friendly) and refreshed archive stamp to v148 with no change to the shipped bundle label (`worked-example-draft-59`); rebuilt PDF.
- Synthesis~30: fixed a missing bib entry for IPFS Docs “Public IPFS Utilities”, added two concrete drift examples (Sep 2025 `cid.contact` temporary routers; Rainbow defaults moving to `auto` expansion), and anchored the “caching proxy” claim to IPFS Docs (IPNI page); bumped note to v0.05 and archive stamp to v148; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v147 (Referee-grade citation tightening + selection discipline bridge)
- Synthesis~30: anchored the public delegated-routing endpoint to IPFS Docs “Public IPFS Utilities” and replaced the weaker CLI anchor for `["auto"]` placeholder resolution with the Kubo RPC reference (`expand-auto`); bumped note to v0.04 and archive stamp to v147; rebuilt PDF.
- Synthesis~7: replaced a personal-hosted “open PDF” link for the SAC’25 Kademlia query-obfuscation paper with the TU Dresden research-portal record; bumped note to v0.44 and archive stamp to v147; rebuilt PDF.
- Synthesis~29: updated archive stamp and added one external anchor to post-selection inference (Lee et al., Ann. Stat. 2016) to justify the pilot/frozen “data splitting” warning; rebuilt PDF.
- Anonymity~B: updated archive stamp and aligned the query-obfuscation bibliographic anchor with Synthesis~7; rebuilt PDF.
- Synthesis~17: minor numerical-slice clarity (explicit tier contributions) without changing the shipped worked-example bundle label (`worked-example-draft-59`); archive stamp bumped to v147; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.


## v146 (Deployed-surface citation closure + worked-example stamp)
- Synthesis~30: added an authoritative pointer to the canonical IPFS Mainnet AutoConf manifest (conf.ipfs-mainnet.org/autoconf.json), added a docs-based anchor for 'auto' placeholder resolution in Kubo, and replaced the chunked-OHTTP IESG approval placeholder with the IETF-Announce mailarchive record (27 Feb 2026); bumped note to v0.03 and archive stamp to v146; rebuilt PDF.
- Synthesis~17: refreshed the archive stamp to v146 while keeping the shipped worked-example artifact bundle fixed at worked-example-draft-59; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v145 (Deployed-surface accuracy hardening + pointer-chain coherence)
- Synthesis~30: tightened and corrected deployed-surface citations using authoritative IPFS Docs and raw Kubo documentation; clarified AutoConf defaults (conf.ipfs-mainnet.org/autoconf.json), added explicit pinning guidance for env-var overrides (IPFS_HTTP_ROUTERS), and clarified that the delegated-routing reader-privacy upgrade track (IPIP-0421) is currently a draft; bumped note to v0.02 and archive stamp to v145; rebuilt PDF.
- Synthesis~7: further de-bloated the deployed-mitigations taxonomy branch to cite Synthesis~30 as the canonical deployed-surface map (keeping only measurement comparators inline); bumped note to v0.43 and archive stamp to v145; rebuilt PDF.
- Synthesis~17: added an explicit pointer to Synthesis~30 for primary-path control-plane surfaces, repaired a missing series:notation bibliography anchor, and refreshed the archive stamp to v145 (worked-example bundle remains worked-example-draft-59); rebuilt PDF.
- AnonDHT~State~1: refreshed the archive stamp to v145 and added a one-line pointer to Synthesis~30 so state-dependent anonymity claims treat deployed control-plane drift as part of the declared state surface; rebuilt PDF.
- regenerated `MANIFEST.json`.

## v144 (Deployed-surface companion note + related-work de-bloat)
- Synthesis~30: new deployed-surface companion note isolating IPFS/libp2p control-plane + service concentration surfaces (delegated routing, AutoConf, OHTTP/chunking) with a minimal "what-to-pin" checklist; built PDF.
- Synthesis~7: moved detailed deployed-surface discussion into Synthesis~30 to keep the related-work map compact; bumped note to v0.42 and archive stamp to v144; rebuilt PDF.
- Anonymity~B: now cites Synthesis~30 at first mention of deployed control-plane surfaces; archive stamp bumped to v144; rebuilt PDF.
- SERIES_INDEX: added a v144 section, added Synthesis~30 to reading order and inventory, and fixed minor inventory hygiene; rebuilt PDF.
- regenerated `MANIFEST.json`.

## v143 (Deployed-surface citation hardening + selection-discipline pointers)
- Synthesis~7: kept the control-plane/autoconf and caching-endpoint surfaces, but added authoritative IPFS Docs + Kubo-config references for the public delegated-routing endpoint and AutoConf configuration knobs; bumped note to v0.41 and archive stamp to v143; rebuilt PDF.
- Anonymity~B: repaired an archive-stamp drift, replaced a placeholder wiki-style Prefix Capacities entry with the series' standard published-note pointer, and added an explicit selection-discipline reminder in the log-audit workflow for data-selected bucket/coarsening maps; rebuilt PDF.
- Synthesis~17: coarsening-variant paragraph now explicitly imports selection discipline (Synthesis~29) for any data-selected partition maps; archive stamp bumped to v143; rebuilt PDF.
- updated SERIES_INDEX and regenerated `MANIFEST.json`.

## v142 (Worked-example coherence + deployed autoconf surface)
- Synthesis~17: corrected an internal drift so the narrative stamp matches the shipped worked-example artifacts (`note_version=0.59`, `worked-example-draft-59`); clarified that primary-path protocol/endpoint specifics live in the manifest's evidence hooks rather than bloating the public guard object; rebuilt PDF.
- Synthesis~7: added dynamic endpoint discovery / autoconf as an explicit control-plane observation surface (IPFS Mainnet AutoConf pointer); bumped note to v0.40 and archive stamp to v142; rebuilt PDF.
- Anonymity~B: added DOI anchors for Peer2PIR (IEEE S&P'25) and Backes et al. (ASIACCS'12) to reduce “preprint-only” ambiguity; rebuilt PDF.
- AnonDHT~State~1: stamp aligned to archive v142; rebuilt PDF.
- updated SERIES_INDEX and regenerated `MANIFEST.json`.

## v141 (Citation closure + deployed-surface pointers)
- citation closure: repaired dangling `series:selection` citations by standardizing on `series:selectiondiscipline` (Anonymity~B and Synthesis~28); rebuilt PDFs.
- Synthesis~28: stamp bumped to archive v141 and the selection-discipline note (Synthesis~29) is now a first-class bibliography anchor; rebuilt PDF.
- Synthesis~7: added explicit pointers to delegated-routing caching and Someguy-backed public endpoints as real deployed observation surfaces; stamp bumped to archive v141; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v140 (Coherence + citation hardening)
- Synthesis~7: fixed a DOI typo for the 2025 Kademlia query-obfuscation paper; refreshed archive stamp; rebuilt PDF.
- Synthesis~8: explicitly points claims with data-dependent bucket maps to the selection-discipline note (Synthesis~29); refreshed stamp; rebuilt PDF.
- Synthesis~17: tightened again and explicitly imports the series-wide notation (Synthesis~8); rebuilt PDF.
- AnonDHT~State~1: replaced the Nym reputation pointer with the ePrint report (2026/101) as a stable anchor; refreshed stamp; rebuilt PDF.
- Anonymity~B: tied log-based equalization audits to selection discipline when projections use learned/coarsened buckets; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v138 (Selection discipline for data-dependent maps + de-duplication)
- Synthesis~29: new short note centralizing conservative receipt-grade handling of data-dependent bucket/coarsening map selection (witness-indexed families + pilot/frozen phases under change control); built PDF.
- Synthesis~27: de-duplicated the quantile-bucket caveat by pointing to Synthesis~29; stamp bumped to archive v138; rebuilt PDF.
- Synthesis~28: de-duplicated the data-dependent top-$m$ caveat by pointing to Synthesis~29; stamp bumped to archive v138; rebuilt PDF.
- Anonymity~B: imports Synthesis~29 (one-line pointer) alongside Synthesis~28 so map-selection guidance is not rederived in the contract paper; stamp bumped to archive v138; rebuilt PDF.
- SERIES_INDEX: added a v138 section, fixed a broken arrow in the synthesis reading-order chain, added Synthesis~29 to inventory; rebuilt PDF.
- regenerated `MANIFEST.json`.

## v137 (Worked example: coarsening variant + pointer-chain hygiene)
- Synthesis~17: bumped to worked-example-draft-59 / v0.59 and added a fully wired coarsening variant receipt and evidence path (large-alphabet contact-set hash made audit-feasible via a digest-bound deterministic coarsening map), including new replay plan and support-bundle resolver entry; rebuilt PDF.
- Synthesis~28: now points to the Synthesis~17 coarsening variant as a concrete receipt/evidence instantiation of the partition-map design step; rebuilt PDF.
- Anonymity~B: adds an explicit pointer to the coarsening variant receipt (Synthesis~17) and design rule (Synthesis~28); bumped stamp to archive v137; rebuilt PDF.
- Anonymity~D: stamp aligned to archive v137; makes the MaxL-to-odds-inflation bridge explicit via Synthesis~5; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v136 (Coarsening rules for large-alphabet audits + bucket-budget lemma tightened)
- Synthesis~28: new short note centralizing receipt-facing coarsening/partition rules for high-cardinality discrete projections, including post-processing (TV / max-divergence contraction) and an explicit alphabet constraint that makes sample-feasibility transparent.
- Synthesis~27: replaced the linear-only bucket ``rule of thumb'' with the exact Weissman-derived alphabet constraint (and retained the approximation as a secondary line); bumped stamp to archive v136; rebuilt PDF.
- Synthesis~26: stamp aligned to archive v136 (no semantic changes); rebuilt PDF.
- Anonymity~B: imports Synthesis~28 for large-alphabet/coarsening guidance and cites it in the coarsening research agenda; bumped stamp to archive v136; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v133 (Menu-level log-audit note + de-duplication)
- Synthesis~25: new short note centralizing conservative finite-sample TV certificates for discrete interface projections audited from logs, including a receipt-facing publication checklist and explicit menu-level correction via a single $\delta_{\mathrm{stat}}$ parameter.
- Synthesis~0: added an explicit pointer to Synthesis~25 so mechanism papers can cite the centralized statistics note instead of reprinting audit lemmas.
- Anonymity~B: removed the inlined discrete log-audit lemma (now referenced via Synthesis~25) to keep the paper contract-focused; added a clean pointer chain to worked-example receipts (Synthesis~17).
- Anonymity~C: ABOM definition now explicitly defers to the shared contract-object vocabulary (Synthesis~0); minimal schema sketch updated to avoid stale path references; stamp aligned to archive v133.
- Rebuilt touched PDFs; updated SERIES_INDEX and regenerated MANIFEST.json.

## v132 (State-conditioned prefix-fetch variant + conditional equalization interface)
- Synthesis~17: bumped to worked-example-draft-58 (v0.58) and added a fully wired second optional profiling variant that conditions prefix-fetch equalization on a published state witness (bucket-staleness class), including a companion variant receipt (`example_receipt_prefixfetch_statecond_variant.json`) and evidence object (`example_profiling_evidence_prefixfetch_statecond.json`) with its own replay plan and support-bundle pointer.
- Anonymity~B: added a compact subsection defining state-conditioned equalization given a published witness and pointing to the plan/state conditioning lemma; fixed minor prefix-fetch wording and bumped stamp to archive v132.
- Synthesis~18: bumped stamp/version to v0.05 (archive v132) so plan/state equivalence and conditioning lemma can be cited without stamp drift; rebuilt PDF.
- rebuilt touched PDFs, rebuilt SERIES_INDEX, and regenerated `MANIFEST.json`.

## v131 (Worked-example alignment + prefix-fetch variant wiring)
- Synthesis~17: aligned the worked-example draft/version stamp with the maintained tooling; validator now exits nonzero on failure and `rebuild_example.sh` is a single clean pass; line-item summary table now matches the published receipt (includes the path-selection indicator); added an optional prefix-fetch profiling micro-slice plus a fully wired variant receipt (`example_receipt_prefixfetch_variant.json`) and companion evidence object (`example_profiling_evidence_prefixfetch.json`).
- Anonymity~B: added a one-sentence pointer to the worked-example prefix-fetch variant artifacts.

## v130 (Profiling prefix-fetch witness + citation closure hygiene)
- Anonymity~B: added a prefix-fetch witness family to the ``what can be equalized?'' example list, explicitly tying prefix-level obfuscation to shared-kernel feasibility/lower bounds (Prefix Capacities, 2026-01-25) and stop-time normal forms; bumped archive stamp to v130; rebuilt PDF.
- Anonymity~D: fixed the related-work map key and added an explicit canonical wiki-link pointer to the published spectral anonymity backbone note; bumped archive stamp to v130; rebuilt PDF.
- citation closure: repaired missing bibliography items where citations previously resolved as ``?'' (Synthesis~8: backbone crosswalk; AnonDHT~State~1: conditional certificates; Synthesis~23: receipt-accounting rulebook); bumped stamps and rebuilt PDFs.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v129 (State-surface micro-slice + non-redundancy tightening)
- Synthesis~17: added a short, digest-bound state-surface micro-slice explaining how \texttt{state\_decl\_id} pins a 24h public-bucket cache/refresh scope (and where deeper state-dependent leakage lives in the state series); bumped stamp to archive v129; rebuilt PDF.
- Synthesis~18: added a small conditioning lemma bounding joint leakage when a proof conditions on a published state witness; bumped stamp to archive v129; rebuilt PDF.
- Synthesis~13: tightened the abstract to explicitly import ABOM/OINL + line items + transparency primitives; added a one-line pointer to RFC~9540 for OHTTP transport discovery as an optional complement; bumped stamp to archive v129; rebuilt PDF.
- Synthesis~8 + Synthesis~24: made the canonical wiki-link list line-breakable and added explicit ownership division (envelope vs line items vs plan/state digests); crosswalk now includes a canonical wiki-link block and updated archive stamp; rebuilt PDFs.
- Synthesis~12: clarified envelope ownership in the abstract and bumped archive stamp; rebuilt PDF.
- Synthesis~7: fixed a truncated DOI and corrected the chunked-OHTTP protocol-action URL; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.


## v128 (Worked-example TeX hygiene + chunked-OHTTP status pin)
- Synthesis~17: fixed an accidental TeX escaping that rendered a table as literal text (\texttt{\\begin\{table\}}); tightened the note by pruning unused bibliography entries, adding an explicit Synthesis~13 user-interface import, and adding a one-line validator pointer for the numerical slice; bumped stamp to archive v128; rebuilt PDF.
- Synthesis~7: pinned the chunked-OHTTP transport line to its current IETF status (IESG protocol action approving draft-ietf-ohai-chunked-ohttp-08 as Proposed Standard on 27 Feb 2026) and bumped stamp to archive v128; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.


## v127 (Units consistency + horizon composition hygiene)
- Synthesis~19: made units explicit (\(\varepsilon\) in bits) and replaced mixed $e^{\varepsilon}$/\texttt{exp()} expressions with $2^{\varepsilon}$ throughout, aligning the horizon rulebook with the archive's odds-inflation/MaxL convention; rebuilt PDF.
- Anonymity~B: corrected the horizon slack formula to use $2^{\sum_{j<\ell}\eta_j}$ (bits) and bumped the archive stamp; rebuilt PDF.
- Synthesis~0 + Synthesis~8: corrected ``hockey-stick'' / approximate max-divergence displays to use $2^{\varepsilon}$ (bits) and fixed the implied one-sided TV bound to $1-2^{-\varepsilon}$; rebuilt PDFs.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.


## v126 (Restricted-route related-work branch + worked example evidence drift + profiling drift pointer)
- Synthesis~7: added a restricted-route / social-overlay DHT routing branch (X-Vine, R$^{5}$N) to disambiguate anonymous lookup vs directory scaling; added citations to the academic papers and the R$^{5}$N technical specification; rebuilt PDF.
- Synthesis~17: upgraded to worked-example-draft-55 (v0.55) and replaced the third drift vignette with an evidence-drift example centered on \texttt{evidence\_id} + \texttt{replay\_hook}; regenerated artifacts via the materializer/validator and rebuilt PDF.
- Anonymity~B: clarified that adaptive stopping/drift monitoring should use state-series anytime-valid (e-value) audits rather than the i.i.d. log-certificate lemma; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.


## v125 (Receipt completeness + stopping-safe drift audits + rebuilds)
- packaging correctness: rebuilt missing PDFs (Operational~A and Synthesis~12) and recompiled touched notes.
- AnonDHT~State~1: added stopping-safe drift-audit subsection (time-uniform e-values / Ville inequality) and removed stale inlining markers.
- Synthesis~12: clarified the separation between \texttt{evidence\_id} (supporting object) and \texttt{replay\_hook} (recomputation plan) via a dedicated remark.
- TeX hygiene: removed legacy ``inlined section'' comment scaffolding across multiple papers.
- updated SERIES_INDEX and regenerated `MANIFEST.json`.

## v124 (Non-redundancy tightening + receipt-ID hygiene)
- tightened Operational~A (schedule-only retries): replaced long-form security-game definitions with a compact imported contract (Anonymity~A / Synthesis~21) and updated the lifting theorem statement to cite the conditional-certificate interface; rebuilt PDF.
- aligned Synthesis~8 (notation/minimal model) with receipt schema: clarified \texttt{state\_decl\_id} is optional (monitored/stateful settings only); rebuilt PDF.
- stamp alignment: bumped archive stamps for Anonymity~B (profiling/equalization) and Anonymity~D (spectral delegation budgets); rebuilt PDFs.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v123 (Hygiene + drift safety: conditional certificates fixed; worked example de-bloated; OHTTP draft refreshed)
- fixed Synthesis~21 (conditional per-step certificates): repaired a real TeX corruption (broken \texttt{\textbackslash begin} and \texttt{\textbackslash bibitem} tokens) so the note compiles cleanly; rebuilt PDF.
- tightened Synthesis~17 (worked example): upgraded to worked-example-draft-54 (v0.54) and replaced the long object inventory table with a grouped pointer to the shipped artifact inventory + support manifest; regenerated artifacts via the materializer/validator and rebuilt PDF.
- refreshed Synthesis~7 (related work map): updated the chunked OHTTP anchor to \texttt{draft-ietf-ohai-chunked-ohttp-08} (18 Feb 2026) and rebuilt PDF.
- tightened Synthesis~12 (receipt line items): clarified \texttt{state\_decl\_id} is optional (stateful/monitored settings) and \texttt{witness\_tier} is non-binding; rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v122 (Log-audit equalization is now CP+union-bound; worked example reconciled and computed)
- strengthened Anonymity~B (profiling/equalization): made the log-audit certificate referee-grade by separating the statistical confidence parameter \(\delta_{\mathrm{stat}}\) from the published slack \(\delta\), and by using exact binomial (Clopper--Pearson) intervals with a union bound to derive a deterministic receipt-grade \((\eta,\delta)\) summary from a published count table; rebuilt PDF.
- strengthened Synthesis~17 (worked example): fixed an inconsistency between the narrative numerical slice and the receipt's profiling values, upgraded to worked-example-draft-53 (v0.53), and updated the generator to compute the profiling \((\eta,\delta)\) from toy counts using CP+union-bound (evidence schema v2); rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v121 (Evidence IDs as a receipt primitive; worked-example generator sync; chunked-OHTTP correction)
- tightened Synthesis~12 (receipt line items): added an explicit optional \texttt{evidence\_id} field, and clarified the split between \texttt{evidence\_id} (what supports the bound) and \texttt{replay\_hook} (how to reproduce/validate it); rebuilt PDF.
- strengthened Synthesis~17 (worked example): upgraded to worked-example-draft-52 (v0.52) and made profiling evidence coherent end-to-end: added a dedicated ENF surface for retry-bucket profiling, a receipt line item that carries \texttt{evidence\_id}, a replay plan + bundle for the audit, and updated the materialize/validate tooling so all shipped JSONs are generator-consistent; rebuilt PDF.
- tightened Synthesis~0 (contract objects): removed the redundant full object-catalog table and pointed readers to SERIES_INDEX and Synthesis~24 for the authoritative map; rebuilt PDF.
- corrected Synthesis~7 (related work map): fixed the chunked OHTTP reference to \texttt{draft-ietf-ohai-chunked-ohttp-06} (13 Sep 2025) and rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.


## v120 (Notation IDs + evidence IDs unified; worked example exercises profiling certificates)
- tightened Synthesis~8 (notation/model): clarified line-item interface IDs (\texttt{exposure\_nf\_id}, \texttt{cond\_iface\_id}) and introduced an explicit \texttt{evidence\_id} convention for log-audits and conditional certificates; updated stamp and rebuilt PDF.
- strengthened Synthesis~17 (worked example): added a fourth representative line item for profiling/equalization ($(\eta,\delta)$) plus the minimal supporting registry/replay artifacts so the example receipt exercises log-audit evidence objects; updated stamp and rebuilt PDF.
- refreshed Synthesis~7 (related work map): bumped archive stamp to v120 and rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.


## v119 (Profiling audit now yields $(\eta,\delta)$ + horizon/certificate interlock)
- strengthened Anonymity~B (profiling/equalization): replaced the finite-sample audit lemma with an explicit $(\eta,\delta)$ equalization certificate for discrete projections; the slack $\delta$ now accounts for rare bins directly (no ad-hoc probability floor), and the paper states the coarsening rule needed to make $\delta$ negligible; updated stamp and rebuilt PDF.
- tightened Synthesis~19 (receipt accounting rulebook): added an explicit mapping from horizon claims to the receipt tuple hooks (\texttt{tw\_id}, \texttt{usage}, \texttt{replay\_hook}) and pointed Regime~II authors to conditional per-step certificates; updated stamp and rebuilt PDF.
- tightened Synthesis~21 (conditional certificates): added a minimal per-step certificate record format for plan-spec tooling output, and linked it to profiling/equalization audit evidence objects; updated stamp and rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.


## v118 (Worked-example de-bloat + profiling audit lemma + OHTTP discovery pin)
- tightened Synthesis~17 (worked example receipt interlock): removed schema restatements and redundant interlock tables; the note now exercises only three representative line items and points to owning papers for schemas/theory; updated stamps to archive v118 and rebuilt PDF.
- strengthened Anonymity~B (profiling/equalization): added a conservative finite-sample max-divergence audit lemma for discrete transcript projections, suitable for log-based certification with an explicit confidence level and policy floor; updated stamp and rebuilt PDF.
- updated Synthesis~7 (related-work map): added RFC 9540 (OHTTP service discovery via SVCB/HTTPS records) as an explicit metadata surface to pin alongside RFC 9458 and chunked OHTTP; updated stamp and rebuilt PDF.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.


## v117 (Related-work map expansion + PDF build fix)
- expanded Synthesis~7 (related-work map): added an explicit DHT-backed relay-selection/directory branch (AP3, NISAN, Torsk) to separate ``DHT privacy'' from ``DHT-scaled directory services''; added a Bitswap random-walk plausible-deniability anchor; and added a chunked-OHTTP draft anchor (metadata corrected in v121).
- fixed archive packaging correctness: regenerated previously-empty PDFs (Synthesis~7 and three addendum/optional papers) by recompiling from the shipped TeX sources.
- rebuilt SERIES_INDEX and regenerated `MANIFEST.json`.

## v116 (Worked example: guarded endpoint form + TW/ENF interlocks)
- upgraded Synthesis~17 (worked example receipt interlock): added an explicit guarded endpoint form that carries the separation-failure bound $\rho$ alongside the scalar MaxL summary, plus a short math-backbone pointer paragraph so the example stays non-redundant.
- tightened Synthesis~3 (trace interfaces) and Synthesis~4 (threat windows): clarified how ENF/TW declarations are referenced by receipt line items (	exttt{exposure\_nf\_id}, 	exttt{tw\_id}) and added a concrete TW-template instance reused by the worked example.
- updated archive stamps to `archive v116` in the touched papers and SERIES_INDEX, rebuilt touched PDFs, and regenerated `MANIFEST.json`.

## v115 (Separation $\rho$: model-to-bound crosswalk + evolving OHTTP transports)
- tightened Synthesis~22 (separation manifests): the minimal manifest now commits the assignment/rotation policy (how role instances are selected/rotated), which is the missing hook needed to make separation assumptions replayable and to justify any published separation-failure bound.
- strengthened Synthesis~23 (probabilistic separation budgets): added a compact ``toy bounds'' subsection translating common committed clauses (independent compromise, finite adversary counts, per-epoch rotation/union-bounds) into a threat-window $\rho$; still treats $\rho$ as an upper bound, not a universal estimator.
- refreshed Synthesis~7 (related-work map): added the OHAI chunked-OHTTP draft and a short warning that chunking introduces new metadata features (chunk boundaries/pacing) that must be pinned under the declared projection; also added the missing internal change-control bibitem (Synthesis~18) to keep citations clean.
- updated the archive stamp to `archive v115` in the touched papers and SERIES_INDEX, rebuilt touched PDFs, and regenerated `MANIFEST.json`.

## v114 (Hygiene + correctness: units + control-char repair + related-work verification)
- repaired a real text corruption in Synthesis~17: removed stray control characters so the primary-path separation paragraph renders correctly (\texttt{rho_upper}, $(0,\rho)$) and matches the shipped bundle semantics.
- corrected a lingering units bug in Anonymity~A: the interpretation remark now states odds inflation is measured in bits under \log_2 (with the standard nats$\rightarrow$bits conversion reminder).
- corrected Synthesis~7 bibliography metadata: Proof-of-Validator EthResearch post date is Aug.\ 23, 2023; also verified the reconnaissance-pressure anchor arXiv:2411.14623 metadata.
- cleaned SERIES_INDEX: updated the v114 ``what's new'' bullets to match this revision, removed a stray backslash in the reading-order list, and repaired a broken \texttt{} token.
- bumped TeX archive stamps to `archive v114`, rebuilt PDFs, and regenerated `MANIFEST.json`.

## v113 (Worked-example version coherence + rho adjunct integration + separation composition note)
- fixed a real worked-example coherence bug: Synthesis~17’s paper header version is again aligned to the worked-example draft label (v0.46), matching the shipped bundle’s `note_version` and validator expectations.
- extended the worked example to actually exercise probabilistic separation: the primary-path line item and primary-surface manifest now publish `rho_upper` (policy upper bound) and thread it through the change-control guard and compare-profile auditor fast-diff fields (interpreted as the guarded checkpoint $(0,\rho)$ per Synthesis~23).
- tightened Synthesis~19 (receipt accounting rulebook): adds a short remark stating that separation-failure adjuncts compose as a $\delta$ term and records the resulting horizon mapping (cites Synthesis~22--23).
- normalized Synthesis~24 internal citation keys for the Regime~II certificate interface and the spectral-to-budget packaging to reduce cross-paper drift.
- bumped TeX archive stamps to `archive v113`, rebuilt PDFs, and regenerated `MANIFEST.json`.

## v112 (Math-backbone crosswalk + notation pointer + archive stamp bump)
- added Synthesis~24 (Mathematics Backbone Crosswalk): a compact ``what-to-cite-where'' map from the five published wiki math notes to receipt-facing interfaces (no new primitives).
- tightened Synthesis~8 (notation/model): now points to Synthesis~24 for the backbone crosswalk (reduces redundancy in downstream papers).
- bumped TeX archive stamps to `archive v112`, rebuilt PDFs, and regenerated `MANIFEST.json`.

## v111 (Archive-stamp normalization + odds-inflation units fix + minor typography)
- normalized TeX headers across all papers: all \`paper.tex\` files now carry a consistent \`archive v111\` stamp so PDFs and citations agree.
- fixed a units/wording bug in Anonymity~A: odds inflation \$\ell(o)\$ is measured in bits under \`\log_2\`; nats-to-bits conversion is via division by \$\ln 2\$.
- fixed minor typography in Synthesis~23 (title line-break); no semantic changes.
- expanded Synthesis~23 (research warranted): added a compact menu of evidence-bundle shapes for estimating/publishing $\rho$ in a replayable way (no schema changes).
- rebuilt all PDFs and regenerated \`MANIFEST.json\`.


## v110 (Separation $\rho$ drift rule + schema alignment + related-work wording + patch-notes hygiene)
- clarified Synthesis~23 (probabilistic separation budgets): interpret a published separation-failure upper bound $\rho$ as the guarded additive checkpoint $(0,\rho)$, and make the monotone drift rule explicit (tightening requires replay/evidence; relaxation can be published as \`lineage=coarsening\`).
- aligned Synthesis~12 (receipt line-item schema): the separation-primary remark now matches the same $\rho$ drift rule.
- tightened Synthesis~7 (related-work map): removed the stale “optional coarsenings” wording (the series’ canonical semantics is $(0,\rho)$).
- cleaned the v109 patch-notes block to remove accidental control-character artifacts.
- rebuilt touched PDFs and regenerated \`MANIFEST.json\`.

## v109 (Worked-example quick verification + compilation hygiene + full PDF coverage)
- tightened Synthesis~17 (worked example): adds a short quick verification recipe (validate + compare) and trims maintenance/disclosure prose to reduce redundancy; maintenance details remain in the folder README.
- bumped Synthesis~7 (related work map) to archive v109 and corrected the Proof-of-Validator EthResearch post date (Aug.\ 7, 2023).
- fixed real compile defects in “owner” notes:
  - AnonDHT State~1: repaired an escape-sequence corruption in the inlined bibliography and added missing internal bibitems so citations resolve.
  - Synthesis~16 (deployment blueprint): removed a stray control sequence that broke compilation; bumped its archive stamp.
  - Synthesis~0 and Synthesis~12: filled missing internal bibitems so citations resolve.
- compiled and shipped all paper PDFs (every \`paper.tex\` now has a sibling \`paper.pdf\`); no schema changes implied.

## v108 (Probabilistic separation: canonical $(0,\rho)$ only + index cleanup)
- tightened Synthesis~23 (probabilistic separation budgets): treat a published separation-failure bound $\rho$ purely as the guarded additive checkpoint $(0,\rho)$ and remove the prior non-canonical $\varepsilon_\rho$ display mapping
- updated Synthesis~22/12/4/17 and SERIES_INDEX to remove the $\varepsilon_\rho$ references and keep \texttt{rho\_upper} interpretation uniform; rebuilt touched PDFs and regenerated MANIFEST.json

## v107 (Probabilistic separation: tight $(0,\rho)$ checkpoint + downstream alignment)
- refined Synthesis~23 (probabilistic separation budgets): a published separation-failure bound $\rho$ yields the tight guarded checkpoint $(0,\rho)$ (TV/additive form), with a conservative multiplicative display coarsening $(\varepsilon_\rho,\rho)$ where $\varepsilon_\rho=\log_2\!\frac{1}{1-\rho}$
- updated Synthesis~22/12/4/7/17 to cite $(0,\rho)$ as the default separation-failure adjunct (optionally coarsened for display); rebuilt touched PDFs and regenerated MANIFEST.json

## v106 (Probabilistic separation semantics fix + downstream alignment)
- corrected Synthesis~23 (probabilistic separation budgets): a published separation-failure bound $\rho$ yields a guarded checkpoint $(\varepsilon_\rho,\rho)$ with $\varepsilon_\rho=\log_2\!\frac{1}{1-\rho}$ (and records an explicit pure-$\delta$ coarsening for deployments that insist on $\varepsilon=0$)
- tightened Synthesis~22/12/4/7/17 to match the corrected semantics (no papers in the series now claim an invalid ``$(0,\rho)$'' separation rule); rebuilt touched PDFs and regenerated MANIFEST.json

## v105 (Delegation priors + separation-in-TW + notation/wiki links + related-work anchors)
- tightened Anonymity~D (spectral delegation certificates): added a compact $\chi^2\Rightarrow$MaxL lemma so non-uniform priors / class budgets can be packaged as receipt-grade evidence objects without changing the public receipt surface
- tightened Synthesis~4 (threat windows): explicit reminder that primary-path non-collusion assumptions belong in the TW declaration; points to Synthesis~22 (manifest guard objects) and Synthesis~23 (probabilistic adjunct) for receipt-facing publication
- tightened Synthesis~8 (notation/model): embeds the canonical wiki links for the five backbone mathematics posts and centralizes the source-only artifact-policy boilerplate for non-redundancy
- refreshed Synthesis~7 (related-work map): adds a credentialed-membership anchor (Proof-of-Validator) to the blockchain/Web3 branch and adds a modern reconnaissance-pressure anchor (arXiv:2411.14623) in the attacks section
- refreshed SERIES_INDEX highlights accordingly; rebuilt touched PDFs and regenerated MANIFEST.json

## v104 (Probabilistic separation adjunct + separation-citation unification)
- added Synthesis~23 (probabilistic separation budgets): a short receipt-facing adjunct that maps a published upper bound on separation failure/collusion risk $\rho$ to a guarded checkpoint $(\varepsilon_\rho,\rho)$ compatible with the series' existing $(\varepsilon,\delta)$ endpoint semantics and checkpoint composition (v106 corrects and clarifies the exact mapping)
- tightened Synthesis~22 (separation manifests): now explicitly cites OHTTP and points to Synthesis~23 for deployments that want a quantitative collusion-risk adjunct without changing the receipt schema
- tightened Synthesis~12 (receipt schema): added an editorial remark that separation-class primary paths should commit a manifest digest and (optionally) carry \texttt{rho\_upper} per Synthesis~23
- tightened Synthesis~7 (related-work map): standardized the separation-manifest citation key to \texttt{series:primarysepmanifest} and updated the internal map row to include Synthesis~23
- tightened Synthesis~17 (worked example): expanded the bundle object-map table to explicitly list the primary-surface manifest, user watch policy, and maintenance-side reports as first-class shipped objects
- updated SERIES_INDEX highlights accordingly; rebuilt touched PDFs and regenerated MANIFEST.json

## v103 (Non-redundant profiling + related-work taxonomy refresh)
- tightened Anonymity~B (profiling/equalization): removed a duplicated horizon-composition theorem/proof and instead imports the sequential checkpoint composition theorem from Anonymity~A, keeping only the resulting label formula and OINL-facing identification cap
- refreshed Synthesis~7 (related work map): split ``deployed mitigations'' vs ``role separation/gateway splits'' vs ``blockchain/web3 overlays'' as distinct branches; added an explicit pointer to separation manifests (Synthesis~22) and a concrete blockchain-overlay exemplar (NC-DHT)
- updated SERIES_INDEX highlights accordingly; rebuilt touched PDFs and regenerated MANIFEST.json

## v102 (Separation-manifest guard note + worked-example draft-46 coherence)
- added Synthesis~22 (primary-path separation manifests): a compact, digest-bound guard object for non-collusion/separation assumptions (e.g., `sep.nr1`), intended to be referenced from primary-path receipt line items without changing the public schema
- bumped the worked example support bundle to `worked-example-draft-46` (Synthesis~17 v0.46) and regenerated artifacts, compare report, validation report, and support manifest/inventory so the paper cut and bundle cut are coherent
- tightened Synthesis~17: shortened maintenance prose, added an optional numeric primary-path delegation slice showing how to use the spectral witness pathway (Anonymity~D) through the Regime~II conditional-certificate interface (Synthesis~21)
- tightened Synthesis~12: added a short remark standardizing how assumption-qualified primary surfaces should carry separation-manifest digests (citing Synthesis~22)
- tightened Synthesis~13: removed a redundant preliminary definition so the UVI interface is a single minimal definition (same semantics, less redundancy)
- fixed SERIES_INDEX inventory omissions (Anonymity~D and Synthesis~21 were referenced but not listed) and refreshed highlights; regenerated MANIFEST and rebuilt touched PDFs

## v101 (Worked-example primary-path delegation pointer + replay-citation hygiene)
- tightened Synthesis~17 (worked example): primary-path section now explicitly points quantitative delegation budgeting to Anonymity~D (spectral witness => per-step MaxL) and Synthesis~21 (Regime~II conditional certificate shape), while keeping the separation-surface worked instantiation unchanged
- citation-key hygiene: standardized the auditor replay checklist key as `series:auditorreplay` in the receipt schema, UVI interface, worked example, and Anonymity~D
- fixed a lingering citation-key drift (`series:planstate` -> `series:planstateequiv`) and removed a duplicated bibliography entry in the worked example so touched papers compile cleanly as single files
- recompiled touched PDFs and refreshed SERIES_INDEX / MANIFEST

## v100 (Spectral delegation paper + Regime II interface tightening)
- added Anonymity~D (spectral delegation): a compact, referee-friendly translation from spectral contraction witnesses (as in the published spectral anonymity note) to receipt-grade per-step MaxL caps in bits, designed to be directly usable as Regime~II evidence objects
- tightened Synthesis~21 (conditional per-step certificates): removed the spectral derivation and replaced it with a pointer to Anonymity~D; Synthesis~21 remains the interface definition and certificate object-shape owner
- tightened Anonymity~B (profiling/equalization): dependence-aware equalization now explicitly points to Anonymity~D as the delegation-specific pathway to small conditional certificates
- unified TeX headers to archive v100 and regenerated MANIFEST.json / rebuilt shipped PDFs for touched papers

## v99 (Spectral-to-certificate sketch + index PDF fix)
- strengthened Synthesis~21 (conditional per-step certificates): added a compact proposition sketch translating a spectral contraction witness (via the published spectral delegation note) into a high-probability per-step MaxL cap in bits; kept it explicitly as ``research warranted'' so mechanism papers can cite without re-deriving
- tightened Anonymity~B (profiling/equalization): the dependence-aware equalization bullet now directly points to Synthesis~21 as the intended interface for adaptive/stateful horizon claims
- fixed packaging defect: compiled a real SERIES_INDEX.pdf (v98 shipped a zero-byte placeholder) and regenerated MANIFEST.json accordingly

## v98 (Worked-example de-dup + recent deployed IPFS/DHT privacy anchors)
- tightened Synthesis~17 (worked example): added an explicit receipt-field mapping (envelope + replay hooks) and removed duplicated replay mechanics in favor of the dedicated auditor checklist (Synthesis~20) and Regime~II certificate interface (Synthesis~21)
- refreshed Synthesis~7 (related work map): added recent IPFS/Bitswap privacy engineering anchors (privacy-enhanced Bitswap discovery; Peer2PIR) and a modern Kademlia query-obfuscation reference (SAC 2025)
- normalized archive stamps: all TeX note headers now say ``archive v98''; shipped PDFs were recompiled and MANIFEST regenerated (excluding TeX build byproducts and excluding the manifest itself)

## v97 (Bits-by-default units pass + log-base clarity across applied notes)
- standardized endpoint units: added an explicit ``bits by default'' convention (and nats conversion rule) in Synthesis~8; applied notes now either use \log_2/2^{\epsilon} explicitly or cite the convention
- tightened Synthesis~0 (contract objects): rewrote odds-inflation clauses in bits (\log_2 and 2^{\epsilon}) and pointed repeats/resets to the receipt-accounting and Regime~II certificate notes (Synthesis~19--21)
- clarified destination-privacy MC-EQ bound units: made the D_\infty-to-budget conversion explicitly base-2 to align with MaxL budgets elsewhere

## v96 (Regime II conditional-certificate interface + replay alignment)
- added Synthesis~21 (conditional per-step budget certificates): defines the conditioning interface and digest-bound evidence hooks sufficient for Regime~II horizon claims under adaptive interaction (no independence assumption); records the research hooks (spectral contraction + optional-stopping drift) in one place
- tightened Synthesis~19 (receipt accounting rulebook): bumped archive stamp to v96 and cites Synthesis~21 for the certificate shape instead of re-explaining ``replayable per-step conditional bounds''
- tightened Synthesis~20 (auditor replay recipe): bumped archive stamp to v96; imports Synthesis~21 and adds a concrete replay obligation for Regime~II horizon-$Q$ receipts (record checked per-step bounds and their sum)
- minor non-redundant cross-citation: Anonymity~B now points at Synthesis~21 when referring to horizon semantics under adaptive retries/state
- recompiled the affected PDFs and regenerated \texttt{MANIFEST.json}

## v95 (log-base consistency + projection/summary non-double-counting)
- fixed Synthesis~14 (path-selection tax): rewrote the statement in \\(\log_2\\) bits (using a \(2^{b}\) stability form) so it matches MaxL receipt units and the worked example's \texttt{selection\_tax\_bits}
- strengthened Synthesis~12 (receipt schema): added a compact remark on ``derived vs.\ binding'' line items to prevent double-counting when both projections and summaries are published on the same surface
- tightened Synthesis~17 (worked example): added an explicit ``projection vs.\ summary'' warning stating that the CSET projection is auxiliary and the tiered summary is the binding fallback budget surface
- updated SERIES_INDEX highlights and refreshed unified archive stamps for the touched notes; recompiled the affected PDFs and regenerated \texttt{MANIFEST.json}

## v94 (adaptive horizon composition condition + related-work hygiene + archive cleanup)
- strengthened Synthesis~19 (receipt accounting rulebook): added an explicit adaptive sequential-composition proposition (receipt-facing condition for horizon-$n$ claims without independence) and updated the editorial rule to require an explicit regime (independence, conditional per-step replayable bounds, or digest-bound state scope)
- refreshed Synthesis~7 (related-work map): fixed title formatting, removed a duplicated DOI line, and bumped the unified archive stamp
- tightened Anonymity~B dependence remark to point the ``no-independence required'' case to Synthesis~19 (avoids re-deriving adaptive composition conditions in the profiling paper)
- archive packaging hygiene: removed TeX build byproducts (\texttt{.aux/.log/.out}) from the shipped tree and regenerated \texttt{MANIFEST.json} without the old self-reference trap

## v93 (auditor replay checklist + horizon/receipt pointer tightening)
- added Synthesis~20: a compact, citable auditor replay checklist (anchoring → envelope → bundle digests → plan-spec replay) so mechanism papers can remain referee-grade without re-stating verification workflows
- updated Synthesis~17 (worked example) to cite Synthesis~20 for the replay algorithm and removed a stray internal citation-key drift (\texttt{series:planstate} → \texttt{series:planstateequiv})
- updated Synthesis~12 and Synthesis~13 to point mechanical validation/replay steps to Synthesis~20 (non-redundant interface hygiene)
- updated Anonymity~B/C to treat horizon-$n$ statements as structured claims governed by the receipt-accounting rulebook (Synthesis~19), not as an implicit consequence of TW declarations alone

## v92 (horizon-accounting rulebook + non-redundancy tightening)
- added Synthesis~19: a compact receipt-facing rulebook for horizon-$n$ accounting under retries and state; includes a clear editorial rule (no "$Q\times$" composition without an explicit independence declaration or a digest-bound StateDecl)
- updated Synthesis~8 (notation/model) to treat horizon composition as owned by Synthesis~19 (reducing redundancy and making the "unit+reset+accountant+replay plan" requirement explicit)
- updated Synthesis~17 (worked example) to cite Synthesis~19 where it warns against naive horizon composition under state
- refreshed remaining `archive vXX` header stamps to the unified v92 cut (cosmetic; no interface drift)

## v91 (non-redundancy tightening in Anonymity~B + archive-stamp refresh)
- tightened Anonymity~B (profiling/equalization): removed redundant in-paper composition theorems and identification derivations; composition and sizing are now explicitly imported from Anonymity~A (odds inflation) and the endpoint bridge, leaving only the equalization contract plus the minimal horizon-$n$ ``profiling label'' formulas required for OINL publication
- refreshed synthesis-note archive stamps that still referenced older internal archive numbers (v73/v79) so headers match the unified v91 cut (no semantic changes)
- compile hygiene: removed a stray cross-reference macro usage in Anonymity~B so it remains standalone without adding new packages

## v90 (identifier conventions centralized + receipt/UVI envelope alignment + related-work adds)
- centralized series-wide identifier/digest conventions in Synthesis~8 (and pointed Synthesis~18 to it), so papers can cite one place for \texttt{claim_id}/\texttt{tw_id}/\texttt{state_decl_id} and replay-hook IDs \texttt{plan_id}/\texttt{plan_spec_id}
- strengthened Synthesis~12 (receipt schema): added an explicit ``receipt envelope'' definition (three IDs) and a short drift rationale; aligned schema language with the worked example's actual fields and cited Synthesis~8 and Synthesis~18 for non-redundant semantics
- tightened Synthesis~13 (user-verifiability): made the UVI carry the same envelope IDs as the receipt plus \texttt{receipt_digest} and log proofs; added explicit cross-references to Synthesis~12 and the worked example bundle (Synthesis~17)
- refreshed Synthesis~17 (worked example): added an explicit receipt-envelope table and a minimal replay-hook explanation, citing Synthesis~8/12/18 and Operational~B
- updated Synthesis~7 (related work map): added an information-leak analysis reference for DHTs and a lightweight deployed-mitigation reference (IPFS triple hashing), and recorded Peer2PIR's S\&P DOI


## v89 (replay-plan identifier unification + blueprint replay hooks)
- unified replay-plan identifiers in Operational~B: replaced the standalone \textsf{PlanId} with the series-wide \texttt{plan_id} + digest-bound \texttt{plan_spec_id} pair (per Synthesis~18), so schedule-only audit plans obey the same drift/equivalence rules as receipt replay hooks
- tightened Synthesis~16 (deployment blueprint): receipts now explicitly require \texttt{plan_id}/\texttt{plan_spec_id} in line items and recommend PTL-backed plan certificates when schedule-only trace auditing is used (citing Operational~B); added a non-redundancy bullet pointing to Synthesis~18 for plan/state drift semantics

## v88 (worked-example clarity + related-work refresh)
- tightened Synthesis~17 (worked example): added a short ``how to use this bundle'' recipe, made field\rightarrow variable bindings explicit, and connected the published per-lookup MaxL bound to odds-inflation and identification sizing (importing the endpoint bridge instead of re-deriving it)
- refreshed Synthesis~7 (related work map): bumped header to the unified v88 cut and tightened the ``what-to-cite-where'' table so other papers can cite Synthesis~7 rather than repeating external-context paragraphs
- drift semantics alignment: Synthesis~18 and Synthesis~12/17 now share the same one-paragraph statement of why \texttt{plan\_spec\_id} and \texttt{state\_decl\_id} are digest-bound and what changes trigger replay vs recertification

## v87 (tightening + worked-example-draft-44)
- bumped the worked example to `worked-example-draft-44` (Synthesis~17 v0.44): updated the generator release id and regenerated artifacts / compare report / support manifest / validation report as one coherent cut; the change-control prose now cites the centralized drift taxonomy (Synthesis~18)
- fixed a claim-field typo and tightened stateful-claim identity in AnonDHT State~1: `state_decl_id` is now stated as a third claim field for stateful deployments, with explicit receipt/ABOM pointers and citations to Synthesis~12 and Synthesis~18
- tightened Anonymity~B (profiling/equalization) by removing redundant end-of-paper navigation sections, replacing them with a single positioning paragraph; added an explicit note that stateful profiling claims may additionally depend on `state_decl_id` (via Synthesis~18)

## worked-example-draft-44
- updated the worked-example generator release id to `worked-example-draft-44` and rebuilt the maintained bundle so all public objects (receipt, ABOM, UVI, watch policy, compare report, validation report, support manifest) name the same release id and re-validate cleanly

## v86 (change-control synthesis)
- added Synthesis~18: a tight change-control note that defines minimal semantic cores and digest-binding rules for replay plans (`plan_spec_id`) and state declarations (`state_decl_id`), and centralizes an operational drift taxonomy (P0/P1/P2 and S0/S1/S2)
- tightened Synthesis~12 (receipt line items) to import replay/state drift semantics from Synthesis~18 (keeping the receipt note focused on the tuple surface)
- updated Anonymity~C (ABOM/OINL) to explicitly state the republish-on-id-change rule for `plan_spec_id` and `state_decl_id` and to cite Synthesis~18 as the canonical taxonomy
- updated Certified~C to treat claim identity as receipt-level (ENF-ID + TW-ID + optional StateDecl) and to note how `plan_spec_id` drift is handled under the Synthesis~18 taxonomy
- fixed a latent LaTeX table row termination bug in Synthesis~0's contract-object map (CPPC row) and bumped its archive stamp

## worked-example-draft-43
- bumped Synthesis 17 to v0.43 and refreshed the maintained support-bundle label to `worked-example-draft-43`; updated the worked-example tooling constants and rebuilt artifacts, compare report, support manifest, and validation report as a coherent cut
- tightened Anonymity~C (ABOM/OINL) so ABOM and OINL explicitly cover digest-bound replay semantics (`plan_spec_id`) and, when applicable, digest-bound state surfaces (`state_decl_id`), matching the receipt line-item tuple (Synthesis~12) and the worked example

## worked-example-draft-42
- bumped Synthesis 17 to v0.42 and refreshed the maintained support-bundle label to `worked-example-draft-42`
- added digest-bound state surfaces: the worked bundle introduces `state_decl_id = sha256(canon(state_decl_core))`, publishes a small label→digest registry (`example_state_decl_registry.json`), and threads `state_decl_id` through the receipt, change-control guard, compare profile, drift cases, and validator so “same state_contract_id, different state surface” drift cannot hide off-surface
- extended the receipt schema for stateful claims: Synthesis~12 is now v0.05 and adds optional `state_decl_id`

## worked-example-draft-41
- bumped Synthesis 17 to v0.41 and refreshed the maintained support-bundle label to `worked-example-draft-41`
- digest-bound replay semantics: introduced `plan_spec_id = sha256(canon(plan_spec))`, threaded it through the replay-plan catalog and each receipt line item's `replay_hook`, and tightened the worked-example validator to check the plan-spec digest binding
- updated the contract-object map (Synthesis~0) and receipt schema (Synthesis~12) to treat `plan_spec_id` as the replay-facing companion of `plan_id`

## v82 housekeeping
- updated SERIES_INDEX revision stamp to v82 (no content changes to papers or worked-example artifacts relative to v81)

## v81 housekeeping
- fixed SERIES_INDEX v80 bullet wording so it matches the actual worked-example bump (draft 40 / Synthesis 17 v0.40)

## worked-example-draft-40
- bumped Synthesis 17 to v0.40 and refreshed the maintained support-bundle label to `worked-example-draft-40`
- fixed a worked-example interface mismatch: the fallback contact surface is now explicitly a Tier 2 ordered contact/failure trace (`enf.fallback.cct.v1`), so the exposure normal form matches the receipt's Tier-2 witness designation (and ENF-ID changes accordingly)
- normalized worked-example plan naming in prose: removed the stray `plan:` prefix so plan ids match the JSON `replay_hook` schema; updated the replay-plan catalog, drift cases, compare surfaces, and validator accordingly
- bumped the related-work map header stamp to v0.19 (archive v80)
- regenerated worked-example artifacts, compare report, validation report, and refreshed MANIFEST.json

## worked-example-draft-39
- bumped Synthesis 17 to v0.39 and refreshed the worked-example release label to `worked-example-draft-39`
- aligned worked-example claim fields with ABOM/OINL conventions: `exposure_nf_id` (ENF-ID) and `tw_id` (TW-ID) are now digest-bound claim fields encoded as `sha256:<hex>`
- added two tiny binding adjuncts for digest ids: `example_exposure_nf_registry.json` (label→ENF-ID) and `example_tw_decl.json` (TW label→TW-ID), and updated the worked-example ABOM/receipt/UVI/watch/compare objects to use the digest ids
- unified the user-verifiability interface naming: Synthesis 13 is now v0.03 and the UVI record uses `exposure_nf_id` (matching receipts and ABOMs)
- tightened interface notes: Synthesis 12 is now v0.03 and uses `tw_id` consistently; Synthesis 3/4 are bumped and now recommend explicit `sha256:<hex>` encoding for ENF-ID/TW-ID
- fixed Anonymity~B compilation errors from missing citation keys by removing a redundant long related-work list in favor of the related-work map, and added the intended series bib entries for evaluation/stealth-audit references
- updated SERIES_INDEX v79 highlights and regenerated MANIFEST.json

## worked-example-draft-38
- bumped Synthesis 17 to v0.38 and refreshed the worked-example release label to `worked-example-draft-38`; updated `materialize_example.py` / `validate_example.py`, ran the rebuild script to regenerate artifacts (including `example_compare_report.json`) and refresh `support_manifest.json` until the validator reaches a fixed point
- bumped Synthesis 3 to v0.04 (archive v78): added an explicit pointer that query-privacy mechanisms are orthogonal to transcript-interface declaration; added a modern ``anonymous DHT'' context citation
- bumped Synthesis 4 to v0.10 (archive v78): added a one-paragraph TW declaration template; kept `tw_id` field naming guidance unchanged
- made claim-field usage explicit in AnonDHT State 1/2/3: these papers now import ENF-ID / TW-ID and state that `exposure_nf_id` and `tw_id` are non-negotiable claim fields carried by contracts, receipts, and ABOM entries; State 2 adds an explicit CCT→committee-contact projection paragraph
- tightened Anonymity A by replacing the toy numeric TV→odds example with a pointer to the receipt-style worked example (Synthesis 17)

## worked-example-draft-37
- bumped Synthesis 17 to v0.37 and refreshed the worked-example release label to `worked-example-draft-37`; updated `materialize_example.py`, `validate_example.py`, rebuilt artifacts, compare report, support manifest, and validation report
- bumped Synthesis 0 to v0.11 (archive v77) and fixed a latent LaTeX table-row linebreak bug in the contract-object map (compile-cleaner)
- tightened Anonymity~B (profiling/equalization) by removing duplicated frontmatter and making the claim-field contract explicit: every profiling bound is parameterized by `exposure_nf_id` and `tw_id`
- updated SERIES_INDEX metadata + v77 highlights
- regenerated `MANIFEST.json`

## worked-example-draft-36
- bumped Synthesis 17 to v0.36 and refreshed the worked-example release label to `worked-example-draft-36`
- normalized the threat/window field name to `tw_id` (lowercase) in receipt line items; updated `materialize_example.py`, `validate_example.py`, and regenerated the worked-example artifacts / maintenance reports
- bumped Synthesis 3 to v0.03 (archive v76) and standardized the ENF-ID claim-field name as `exposure_nf_id` to match receipts/ABOMs
- bumped Synthesis 4 to v0.09 (archive v76) with an explicit warning against `TW_id`/`tw_id` case drift
- bumped Synthesis 0 to v0.10 (archive v76) and updated the contract-object map so ABOM/OINL and TW declarations call out `exposure_nf_id` and `tw_id` as first-class claim fields
- tightened Anonymity~C (ABOM/OINL) so the minimal schema and nutrition-label table treat ENF-ID (`exposure_nf_id`) and TW-ID (`tw_id`) as mandatory claim fields
- tightened Operational~B (auditable trace privacy) by removing date-sensitive transparency ecosystem commentary and by recommending hashing `exposure_nf_id` and `tw_id` into the plan id to prevent audit drift
- updated Anonymity~A (odds inflation) to import ENF-ID/TW-ID as claim fields rather than re-describing interface/window assumptions in prose
- updated SERIES_INDEX metadata + v76 highlights

## worked-example-draft-35
- bumped Synthesis 17 to v0.35: clarified label→digest binding (ENF-ID) and added TW-ID tags to the receipt line items to make horizons explicit
- bumped Synthesis 3 to v0.02: defined ENF-ID (canonical hash) and tightened export language for interface binding
- bumped Synthesis 4 to v0.08: defined TW-ID (canonical hash) and explained why window ids must be explicit
- updated Evaluation 1 manifest schema table to include TW-ID and added the missing threat-window synthesis import/bib entry
- expanded Anonymity series Paper B with a compact related-work/positioning section plus a series-consumption map; cleaned bibliography escapes
- updated SERIES_INDEX metadata + v75 highlights

## worked-example-draft-34
- bumped Synthesis 17 to v0.34: added an at-a-glance public-object bundle map, tightened the drift-case presentation, and compressed the ambiguity log while keeping explicit "where-more-work-is-warranted" flags
- tightened Anonymity series Paper B (profiling/equalization) by making the trace-interface and threat-window imports explicit and adding the missing synthesis bib entries for those imports

## worked-example-draft-32
- bumped Synthesis 17 to v0.32
- fixed a maintenance-report identity gap: `example_compare_report.json` now records the current `release_id` directly instead of only a `base_release_id`, so the compare report identifies the same bundle cut from the same fields as the validation report
- extended `tools/validate_example.py` with an explicit compare-report `release_id` check and refreshed the Synthesis 17 / README maintenance wording accordingly

## worked-example-draft-29
- bumped Synthesis 17 to v0.29
- fixed a real maintenance-bundle coherence bug: the compare-report digest is now bound into `support_manifest.json` by `tools/emit_compare_report.py` instead of being silently healed in memory by the validator
- tightened `tools/validate_example.py` so it checks the compare-report digest actually written on disk, then appends the refreshed validation-report digest without rebinding the compare report for it
- updated `tools/rebuild_example.sh` to rerun validation after writing the refreshed validation report, so a clean rebuild now verifies the persisted maintained bundle cut instead of only a pre-write snapshot
- refreshed the Synthesis 17 / README maintenance wording and regenerated `MANIFEST.json`

## worked-example-draft-27
- bumped Synthesis 17 to v0.27
- added reciprocal ids between `example_artifact_inventory.json` and `support_manifest.json` so the maintenance layer names one maintained bundle cut from both sides instead of only from the compare/validation reports
- extended `tools/validate_example.py` with a manifest-inventory cross-reference check and refreshed the paper / README wording accordingly
- corrected the `SERIES_INDEX.tex` invariant note so it points to `PATCH_NOTES.md` for narrative deltas and `MANIFEST.json` for file digests
- regenerated the root `MANIFEST.json` as a source-file digest list that excludes `MANIFEST.json` itself, avoiding the old self-reference trap

## worked-example-draft-26
- bumped Synthesis 17 to v0.26
- fixed a maintenance-bundle coherence gap: the validator now rebinds and checks the support-manifest digest entry for `example_compare_report.json` instead of tolerating a stale compare-report digest
- tightened the maintenance note in Synthesis 17 and the worked-example README so the bundle now says explicitly that the compare report is digest-bound into the current support-manifest cut on a clean rebuild


## worked-example-draft-24
- bumped Synthesis 17 to v0.24
- made the maintenance reports more self-describing by adding the current support-manifest id and artifact-inventory id to the machine-readable compare report and validation report
- extended the validator with a maintenance-report identity check so the compare report must point back to the current manifest/inventory cut
- fixed a real release-label drift in the generated successor examples by deriving the draft-suffix labels from the current base release id instead of leaving stale hard-coded values in the drift-case catalog and compare walk-through

## worked-example-draft-20
- cleaned the packaged archive handoff so transient root-level preview/build outputs are no longer shipped alongside the maintained source bundle
- bumped Synthesis 17 to v0.20
- clarified in the paper and worked-example README that the maintained support bundle intentionally excludes transient local render outputs such as PDFs, TeX auxiliary files, and PNG page checks
- updated the validator to enforce that the artifact inventory and support manifest stay focused on the bounded source-side support bundle rather than build byproducts
- updated the one-shot rebuild helper to clean TeX aux/log/out files after rebuilding the worked example

## worked-example-draft-19
- bumped Synthesis 17 to v0.19
- expanded the maintenance inventory/support-bundle story so it now covers the worked-note source (`paper.tex`) in addition to the JSON adjuncts, README, and tiny rebuild helpers
- updated the validator and support manifest so handoff coverage now checks the note source alongside the helper scripts and generated support objects
- tightened the paper and worked-example README wording so the machine-readable inventory is described as a support-bundle map rather than a claim to index the entire folder

## worked-example-draft-18
- bumped Synthesis 17 to v0.18
- expanded the worked-example support manifest so it now digest-binds the tiny rebuild helpers (README plus the materialize / compare / validate / rebuild scripts), not just the JSON adjuncts
- updated the paper and README so the maintenance layer is described more honestly as a bundle of adjuncts plus helper files
- extended the validator so support-manifest coverage now checks the helper-file digests as well

# Patch notes for synthesis-layer cleanup

This patched archive applies low-risk synthesis-layer cleanups:

- standardized the `series:traceifaces` bibkey across the archive (`series:traceinterfaces` removed)
- updated synthesis archive stamps to `archive v73` where applicable
- standardized date formatting in Synthesis 3, 5, 6, and 8
- relabeled Synthesis 6 as a micro-note rather than a full technical paper
- de-duplicated Synthesis 16 by pointing its architecture discussion back to Synthesis 10 and retaining its checklist/receipt-chain role
- added a forward pointer from Synthesis 12 to Synthesis 13
- added synthesis paper-type cues and a better Synthesis 12 -> 13 ordering in `SERIES_INDEX.tex`

Not changed:

- Synthesis 0 is **not** truncated in source; Proposition 2 lacks a proof, but the file itself is complete.
- Synthesis 11 and 15 were kept separate; they are adjacent but still own distinct interfaces.
- No new candidate construction note was added.


Additional working-draft changes in this archive copy:

- added `synthesis/paper17_worked_example_receipt_interlock/paper.tex` as a worked-example micro-note focused on receipt instantiation and evaluation interlocks
- added worked-example support artifacts (`example_receipt.json`, `example_abom.json`, `example_uvi.json`, `example_release_receipt.json`, `example_verifier_report.json`)
- added a small generator script at `synthesis/paper17_worked_example_receipt_interlock/tools/materialize_example.py`
- updated `SERIES_INDEX.tex` to include Synthesis 17 in reading order and inventory

Additional working-draft changes in this revision:

- strengthened `synthesis/paper17_worked_example_receipt_interlock/paper.tex` by making the MUCC impossibility result an explicit motivation for using a tiered worked slice rather than a universal raw-DHT equalization story
- added worked-example caveats on auditor-role governance, state-dependent correlation, and transparency-log operational assumptions
- refined `SERIES_INDEX.tex` so the MUCC paper is called out earlier in the suggested reading path and Synthesis 17 is included explicitly in both reading order and inventory
- added a short first-pass reading note for the long scheduling/compiler backbone paper

- tightened Synthesis 17 around receipt semantics: the worked example now uses an explicit public-value convention (effective published bounds in `budget_value`, replay inputs in `obs_model`/`knobs`)
- sharpened the primary-path line item in Synthesis 17 into an assumption-qualified linkability surface (`enf.primary.linkability.v1`, separation class `sep.nr1`) instead of a loose prose-only declaration
- added `example_state_decl.json` as a support artifact so the worked example names cache coarsening, routing refresh, and rate-limit assumptions without pretending they are already solved by the receipt schema
- updated the worked-example generator script and support manifests to encode policy-bound vs empirical-estimate status directly in the JSON artifacts
- fixed `SERIES_INDEX.tex` inventory so it explicitly lists Synthesis 17

- added `example_replay_plans.json` as a support artifact resolving each `replay_hook.plan_id` to a workflow owner, required inputs, and expected replay output
- clarified in Synthesis 17 that the replay-plan catalog is operational glue rather than a new receipt primitive
- refreshed `MANIFEST.json` and the worked-example release label for this draft iteration

- tightened Synthesis 17's primary-path story by adding a primary-surface manifest artifact and threading its digest through the worked receipt / replay materials
- added `example_primary_surface_manifest.json` and `example_user_watch_policy.json` as operational adjuncts in the worked-example folder
- made the user-facing side of Synthesis 17 more concrete by pairing the minimal UVI record with an explicit watch-policy adjunct for drift alarms
- updated the worked-example generator, support manifests, and release-binding objects for draft 4

- added `example_change_control.json` as a release-side change-control adjunct so the worked example can distinguish refresh-only updates from replay-required and full-recertification updates
- revised Synthesis 17 to connect the release receipt to Certified~C style disagreement-gated recertification without expanding the core receipt schema
- updated the worked-example generator, support manifest, and verifier report for draft 5

- added `example_drift_cases.json` and revised Synthesis 17 with three concrete successor-release sketches so the change-control categories are shown on actual field diffs rather than only described abstractly
- tightened the worked-example narrative around drift handling, user alarms, and replay-vs-recertification decisions for draft 6

- sharpened the worked-example state declaration so it now names included vs excluded state surfaces and makes its 24h accounting scope explicit
- added `example_support_bundle_map.json` so each `artifact_bundle` id resolves to the concrete in-archive artifacts and support pointers its replay plan depends on
- revised Synthesis 17 to explain the support-bundle map and to make the state declaration’s scope / exclusions more explicit for draft 7

- added `example_compare_profile.json` so the worked example now names a compact OINL-style fast-diff surface for users and auditors instead of leaving cross-release comparison implicit in the ABOM and release receipt
- revised Synthesis 17 to explain the compare-profile adjunct and to add it to the evaluation interlock map for draft 8
- refreshed the worked-example generator, support manifest, release-binding object, and verifier report so the new compare-profile digest is carried through the archive materials

- added `example_compare_walkthrough.json` so the worked example now shows one concrete prior-vs-current comparison using the compare-profile fields rather than leaving cross-release diffs purely schematic
- revised Synthesis 17 to add a tiny compare walk-through subsection and to make the primary/fallback comparison split more explicit for draft 9

- stabilized Synthesis 17 for draft 10 by tightening the primary-vs-fallback comparison story, adding an explicit ``what to compare first rule of thumb, and pruning some export/summary wording so the note reads more like a stable worked note than an expanding sandbox
- refreshed the worked-example release label to `worked-example-draft-10` and regenerated the support artifacts / manifests from the deterministic materialization script

- stabilized Synthesis 17 further for draft 11 by making its adjunct-object stance explicit, then propagated that stance lightly into Synthesis 13, Synthesis 16, and the series index so the worked example is easier to discover without changing the core receipt or UVI interfaces
- refreshed the worked-example release label to `worked-example-draft-11` and regenerated the support artifacts / manifests from the deterministic materialization script

- froze the worked-example support chain a bit further for draft 12 by adding `tools/validate_example.py` and a generated `example_validation_report.json`, so the archive now carries a lightweight consistency check over digests, replay-hook references, and worked-example arithmetic
- bumped Synthesis 17 to `v0.12`, updated its artifact-policy note to mention the validation script, and refreshed the worked-example release label to `worked-example-draft-12`
- tightened the support-manifest coverage in the worked-example folder so the compare walk-through is now carried explicitly alongside the other support artifacts


- stabilized the worked-example note for draft 13 by adding a compact adjunct-inventory table near the receipt discussion, trimming repeated “not a new primitive” prose, and regrouping the README so the support objects are easier to navigate
- strengthened `tools/validate_example.py` for draft 13 with extra coherence checks across the compare profile, user-facing surfaces, change-control guard fields, and replay-bundle coverage
- refreshed the worked-example release label to `worked-example-draft-13` and regenerated the support artifacts / manifests / validation report

## 2026-02-26 - Worked example draft 14
- bumped Synthesis 17 to v0.14 and added a short freeze-oriented maintenance note
- added `example_artifact_inventory.json` as a machine-readable role inventory for the worked-example support files
- extended `validate_example.py` to check inventory coverage alongside digest/reference and arithmetic consistency
- refreshed README language so the worked-example folder is easier to maintain as a bounded support bundle


## worked-example-draft-15
- Added `tools/emit_compare_report.py` and a generated `example_compare_report.json` so the compare-profile/compare-walkthrough story can be materialized as a machine-readable diff summary.
- Added `tools/rebuild_example.sh` as a one-shot maintenance helper for regenerating artifacts, emitting the compare report, rerunning validation, and rebuilding the paper.
- Updated Synthesis 17 and the worked-example README to describe the compare report and the rebuild flow as maintenance tooling rather than new publication primitives.
- Extended the validator to check compare-report coherence and support-manifest coverage for the new maintenance artifact.

## worked-example-draft-16
- Bumped Synthesis 17 to v0.16 and added a short subsection explaining the support-manifest / artifact-inventory / compare-report / validation-report layer as a maintenance-side integrity layer rather than a claim-side schema extension.
- Added a matching row to the evaluation interlock map so the maintenance artifacts are explicitly tied to local consistency checks and handoff integrity, without promoting them to new certification primitives.
- Rebases the worked-example release label to `worked-example-draft-16`, regenerates the JSON artifacts / compare report / validation report, and refreshes the root MANIFEST for the new archive revision.

## worked-example-draft-17
- Bumped Synthesis 17 to v0.17 and clarified in the paper that the support-layer inventory covers the tiny rebuild helpers as well as the JSON adjuncts.
- Expanded `example_artifact_inventory.json` so it now lists `README.md` and the small rebuild / compare / validation helpers alongside the maintenance reports.
- Extended `validate_example.py` so inventory coverage now checks the helper scripts and README in addition to the JSON artifacts, making the maintenance bundle more handoff-friendly.


## worked-example-draft-22
- Bumped Synthesis 17 to v0.22 and refreshed the worked-example release label to `worked-example-draft-22` so the paper cut and release-bound JSON no longer drift apart.
- Extended `validate_example.py` with a paper-version/draft-label alignment check, which catches the specific handoff bug where a newer note revision could ship stale release ids in the support bundle.
- Tightened the maintenance note and worked-example README to say this alignment is part of the bounded handoff discipline, then rebuilt the support artifacts, compare report, and validation report.

- draft23: made `support_manifest.json` self-describing and release-bound; aligned drift-case / compare-walkthrough successor labels with the current base release; added validator checks for manifest identity and successor release-id coherence.

## worked-example-draft-28
- Bumped Synthesis 17 to v0.28 and refreshed the worked-example release label to `worked-example-draft-28`.
- Added `note_version` to the maintenance-side manifest, artifact inventory, compare report, and validation report so the bundle identifies the exact paper cut as well as the release id it summarizes.
- Extended `validate_example.py` with a note-version alignment check across `paper.tex`, `support_manifest.json`, `example_artifact_inventory.json`, and the generated maintenance reports, then rebuilt and revalidated the bundle.

## worked-example-draft-30
- Bumped Synthesis 17 to v0.30 and refreshed the worked-example release label to `worked-example-draft-30`.
- Tightened `validate_example.py` so it now checks the persisted validation-report digest already bound in `support_manifest.json`, rather than only refreshing that binding during the run.
- Made that persisted validation-report check stable across repeated runs, so the validator no longer changes its own report digest merely by recording the prior digest value in detail text.
- Updated the worked-example paper and README to describe that stricter rebuild discipline, then rebuilt and revalidated the maintained bundle.
- worked-example-draft-31 / Synthesis 17 v0.31: exclude Python bytecode caches from the maintained support-bundle story and cleanup flow; rebuild helper now removes `tools/__pycache__/` and `*.pyc`, validator treats them as transient byproducts, and the paper/README describe them as excluded from the packaged handoff.

## worked-example-draft-33
- Bumped Synthesis 17 to v0.33 and refreshed the worked-example release label to `worked-example-draft-33`.
- Fixed a worked-example mismatch: the paper describes each receipt line item as carrying a `TW_id`, but the JSON line items previously omitted it. Line items now include `TW_id` explicitly.
- Extended `validate_example.py` with a `TW_id per line item` check and rebuilt the support bundle, compare report, and validation report.

## worked-example-draft-41
- Bumped Synthesis 17 to v0.41 and refreshed the maintained bundle label to `worked-example-draft-41`.
- Digest-bound replay semantics: added `plan_spec_id = sha256(canon(plan_spec))` to the replay-plan catalog and included `plan_spec_id` in every receipt line item's `replay_hook`, so "same plan_id, different replay" drift cannot hide outside the receipt surface.
- Extended the worked-example validator to check plan-spec canonicalization and replay-hook/catalog coherence for `plan_spec_id`.
- Updated Synthesis 12 (receipt schema) and Synthesis 0 (contract objects) to treat `plan_spec_id` as a recommended claim field, aligning the series around a single replay-workflow binding rule.
- Regenerated the worked-example support artifacts, compare report, and validation report; refreshed `MANIFEST.json`.

## worked-example-draft-42
- Bumped Synthesis 17 to v0.42 and refreshed the maintained bundle label to `worked-example-draft-42`.
- Digest-bound state surfaces: added `state_decl_id = sha256(canon(state_decl_core))` to the worked-example state declaration and threaded `state_decl_id` through the receipt, change-control guard, compare profile, drift cases, and validator so state-surface drift cannot hide under a reused `state_contract_id` label.
- Added `example_state_decl_registry.json` as a small label→digest registry for state declarations (human `state_contract_id` → digest-bound `state_decl_id`), paralleling the exposure registry and TW declaration binding.
- Updated Synthesis 12 (receipt schema) to include an optional `state_decl_id` field and updated Synthesis 0 (contract objects) to add a StateDecl contract row and state-declaration digest-binding guidance.
- Regenerated the worked-example JSON artifacts, compare report, validation report, and paper PDF; refreshed `MANIFEST.json`.

## 2026-02-28 - v134 Anytime spending for expanding log audits
- Added Synthesis~26 (Anytime Statistical Spending for Menu Audits): a compact, conservative publication rule for repeated/expanding log-audit certificates using a named spending schedule (geometric or $1/t^2$) so a single published $\delta_{\mathrm{stat}}$ remains meaningful over time.
- Tightened Synthesis~25 to defer adaptive-menu bookkeeping to Synthesis~26 (non-redundancy).
- Updated Anonymity~B to cite Synthesis~25--26 (log-audit certificates + anytime spending) instead of pointing to Certified~A for within-projection menu guarantees.
- Tightened Certified~C by removing an inlined confidence-sequence aside and deferring the receipt-facing monitoring-confidence story to Synthesis~26.
- Updated SERIES_INDEX inventory to explicitly list Synthesis~25 and Synthesis~26; rebuilt touched PDFs and regenerated MANIFEST.

## v135 (Bucket design for continuous timing projections)
- Synthesis~27: new short note defining a receipt-facing bucket-map declaration for timing signals and a simple alphabet-size design inequality tied to Synthesis~25--26 audit surfaces.
- Synthesis~25: now points to Synthesis~27 for timing discretization/bucket design (non-redundancy).
- Anonymity~B: cites Synthesis~27 at first mention of timing buckets; archive stamp aligned to v135.
- Rebuilt touched PDFs, updated SERIES_INDEX, and regenerated MANIFEST.

## v139 (Worked-example tightening + threat/trace stamp sync)
- Synthesis~17: rewrote the worked example to be tighter and more referee-facing (minimal public identifiers + four representative line items + explicit interlock walkthrough); bumped to worked-example-draft-60; rebuilt PDF.
- Synthesis~3 and Synthesis~4: synchronized archive stamp to v139; rebuilt PDFs.
- State~1: synchronized archive stamp to v139; rebuilt PDF.
- Anonymity~B: added a concrete IPFS passive-monitoring citation (Balduf et al., ICDCS'22) in the profiling motivation and added the bib entry; synchronized archive stamp to v139; rebuilt PDF.

## v140 (Coherence + citation hardening)
- Synthesis~7: fixed DOI typo for Daniel/Michel/Tschorsch (SAC 2025) and updated archive stamp to v140; rebuilt PDF.
- Synthesis~8: updated archive stamp to v140 and added an explicit pointer to the selection-discipline note (Synthesis~29) for data-dependent bucket/coarsening maps; rebuilt PDF.
- Synthesis~17: added explicit import of the series-wide notation (Synthesis~8) in the takeaways; the paper text briefly carried a worked-example-draft-61 stamp, but the shipped worked-example artifacts remained at worked-example-draft-59; this drift is repaired in v142.
- Anonymity~B: in the log-based equalization audit workflow, added an explicit selection-discipline guardrail when the audited projection uses learned/coarsened buckets; updated archive stamp to v140; rebuilt PDF.
- State~1: replaced the Nym-reputation citation anchor with the stable ePrint report (2026/101) and updated archive stamp to v140; rebuilt PDF.
- Updated SERIES_INDEX and regenerated MANIFEST.

## v141 (Citation closure + deployed-surface pointers)
- Anonymity~B: fixed a dangling selection-discipline citation key (standardized on `series:selectiondiscipline`) and bumped stamp to archive v141; rebuilt PDF.
- Synthesis~28: fixed a dangling selection-discipline citation key, added the selection-discipline bibliography anchor (Synthesis~29), and bumped stamp to archive v141; rebuilt PDF.
- Synthesis~7: added explicit pointers to delegated-routing caching and Someguy-backed public endpoints as real deployed observation surfaces; bumped stamp to archive v141 and note version to v0.39; rebuilt PDF.
- Rebuilt SERIES_INDEX and regenerated MANIFEST.

## v142 (Worked-example coherence + delegated-routing autoconf surface)
- Synthesis~17 (worked example): repaired internal drift by aligning the paper's version/release stamp with the shipped worked-example artifacts (note\_version=0.59 / worked-example-draft-59); added a short paragraph clarifying how primary-path protocol/endpoint specifics are carried by evidence hooks rather than bloating the public guard; updated archive stamp to v142; rebuilt PDF.
- Synthesis~7 (related work map): added dynamic endpoint discovery / autoconf (IPFS Mainnet AutoConf) as an explicit deployed control-plane observation surface; bumped note to v0.40 and archive stamp to v142; rebuilt PDF.
- Anonymity~B (profiling): added DOI anchors for Peer2PIR (IEEE S\&P'25) and Backes et al. (ASIACCS'12); rebuilt PDF.
- AnonDHT~State~1: updated archive stamp to v142; rebuilt PDF.
- Rebuilt SERIES_INDEX and regenerated MANIFEST.
## v157 (Protocol-filter surfaces + micro-diff hygiene)
- Synthesis~30 (deployed surfaces): added an explicit note that delegated-routing protocol filters (IPIP-0484) are a request-shaping surface and that Rainbow exposes a corresponding knob (--http-routers-filter-protocols). The what-to-pin checklist now names Rainbow's filter control alongside Kubo's IPFS_HTTP_ROUTERS_FILTER_PROTOCOLS.
- Synthesis~17 (worked example): tightened the micro-diff discussion by collapsing redundant prose into a single state-surface-drift rule; fixed a stray tab/typo in the rendered state_decl_id reference; kept the request-shaping drift paragraph but made it one sentence.
- Synthesis~12 (receipt schema): synchronized archive stamp to v157.
- Rebuilt touched PDFs and regenerated MANIFEST.
