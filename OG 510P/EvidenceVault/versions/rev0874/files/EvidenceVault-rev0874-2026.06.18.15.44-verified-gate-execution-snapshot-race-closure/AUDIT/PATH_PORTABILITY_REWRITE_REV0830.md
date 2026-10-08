# Path portability rewrite rev0830

This surface records concrete content rewrites from build-host absolute paths to shipped archive-relative paths. It is deliberately limited to references whose trailing path components resolve to exactly one file in the archive.

- Mode: `applied_safe_unique_suffix_rewrites`
- Files rewritten: **160**
- Absolute references rewritten: **1332**
- Unique old→new pairs: **578**
- Unresolved/external references left unchanged: **20** in **14** files
- Ambiguous references left unchanged: **2** in **2** files

## Why this is safe enough for a patch

The old references were host coordinates such as `/mnt/data/...`. The new references name payload files shipped inside this archive. The rewrite does not alter referenced artifact digests; it only replaces non-portable coordinates when a unique shipped target exists.

## Rewritten files

| Path | Refs rewritten | Unique pairs | New SHA-256 |
| --- | ---: | ---: | --- |
| `certs/curated/ocf_llm/examples/resolver_trace_cpc_profile_receipt_pbc_policy_mismatch_v1.yaml` | 7 | 4 | `3d1eb1c7fc6419091b8776fdd9dde43cdc371a69080191524cbf7e4e14e02806` |
| `certs/curated/ocf_llm/examples/resolver_trace_cpc_profile_receipt_pbc_stale_policy_v1.yaml` | 3 | 2 | `97870f87ca12a29a83723aca9167741d8a7083e71b5a9dd6c9d64ea44a5d31c0` |
| `sources/docf/test_vectors/_emit_demo_log.txt` | 4 | 2 | `25d9163c382f066aadae88e61240878071f3016d2c06fc9afef90227eb423ebf` |
| `sources/docf/test_vectors/pct_witness_diversity_real_results.json` | 1 | 1 | `197917d3b61f58a97e899b01bd11e90665e74f0d541db3ad4aea672d7ebc7dab` |
| `sources/docf/test_vectors/tpv_gate_satisfaction_witnessed_demo.json` | 1 | 1 | `cf2ffde0711c2f46a7eb082b90b4be3d1e0c3dbeb08c6b9225b08ad4d3257d4c` |
| `sources/docf/test_vectors/tpv_gate_satisfaction_witnessed_scitt_statement_demo.json` | 1 | 1 | `88a498e1127d6e8678c2ed690de37ca837d5c91d988bb41d3cd726402c9a1d00` |
| `sources/ocf_llm/archive/v263_snapshot/assurance_adc_churn_run_v263.json` | 3 | 3 | `022ec7caef5b606422016a8a221863ce99d47d12e0c4d8e6b888ab9bf8e8041c` |
| `sources/ocf_llm/archive/v264_snapshot/assurance_adc_hotspot_run_v264.json` | 3 | 3 | `ae75f112d6e0036fbed26b9d00bfd3b76146a5ec5b5fa5ccf4020c0a60d16a35` |
| `sources/ocf_llm/examples/_trace_abirc.yaml` | 8 | 2 | `df6ff4a8a5c3315d0c2aca07405a7dfc7b26c0aec9ff0599a2a7a8a0dbd4d442` |
| `sources/ocf_llm/examples/_trace_check_v153.yaml` | 16 | 3 | `c805e8288ea4377b3d16c20394ddb623309605ad5ea759165b5aef335984924b` |
| `sources/ocf_llm/examples/_trace_rtm.yaml` | 24 | 10 | `775bfcd5518d691535c2ee07794f696bb6823009c4687ff60b1b46863726df59` |
| `sources/ocf_llm/examples/_trace_sabom_scitt_v2.yaml` | 3 | 1 | `765c3b7925a50876baf9e4b5d3ab562bb991d37616c09f2d08b94dc3664ac42f` |
| `sources/ocf_llm/examples/article53_profile_demo_v135/trace_fail.yaml` | 4 | 3 | `3cee41c0bb6a7a635b897f15b0a6902c6ea6aed8e2372196a444efef8097b535` |
| `sources/ocf_llm/examples/article53_profile_demo_v135/trace_pass.yaml` | 4 | 3 | `c03641195a578aa51537e1009b466ead2884c75d704db216ff9af14ea0a2bede` |
| `sources/ocf_llm/examples/article53_profile_demo_v136/trace_fail.yaml` | 4 | 3 | `392587482969fc3244e9fd4b3829afcf7cdc5e5a3632d24f1cdf597dc7c1b168` |
| `sources/ocf_llm/examples/article53_profile_demo_v136/trace_pass.yaml` | 5 | 4 | `f68e4ddabbfa400b7580697f5c5cdebcc86a5677bf1e9e09d501e8291c39e025` |
| `sources/ocf_llm/examples/assurance_adc_churn_run_v263.json` | 3 | 3 | `022ec7caef5b606422016a8a221863ce99d47d12e0c4d8e6b888ab9bf8e8041c` |
| `sources/ocf_llm/examples/assurance_adc_hotspot_run_v264.json` | 3 | 3 | `ae75f112d6e0036fbed26b9d00bfd3b76146a5ec5b5fa5ccf4020c0a60d16a35` |
| `sources/ocf_llm/examples/avr_transparency_demo_v225/equivocation_report.json` | 1 | 1 | `d9fd5537dfd17020628fd29f2eb2e7b787c80184a608f6c914bf5b889536015d` |
| `sources/ocf_llm/examples/drc_toy_trace.yaml` | 2 | 1 | `b54f18d2ad7678a5739cf12121a701c5d3893bad45ae2165de88df83ec323d43` |
| `sources/ocf_llm/examples/drc_toy_trace_beacon_evidence.yaml` | 4 | 2 | `be17950daf75b260359e168a372e64bc46ce58830311123f07f1040725d6d0b0` |
| `sources/ocf_llm/examples/drift_budget_demo_v203/drift_budget_report.json` | 3 | 2 | `07830b0ffbb540296c76951c0e75d98be17bb2c85781ce4965073fc6fa557bbb` |
| `sources/ocf_llm/examples/eic_qic_jrc_policy_trace.yaml` | 11 | 2 | `b56d26c1d48a3baafac41ec3dbd85ccfdf087d46b7c9a848bc323215daa622ff` |
| `sources/ocf_llm/examples/eic_qic_latency_trace_v46.yaml` | 4 | 3 | `d386d8e302198715b97a832fe3da81caf58ce5dc008e3f5d0a74fafda8a3b890` |
| `sources/ocf_llm/examples/idc_demo_altpaths_v255/report.json` | 2 | 2 | `9db76b94db7d70840bacd192d051b060935fa8f4364e3f59a53ddb3a01843d6a` |
| `sources/ocf_llm/examples/idc_demo_altpaths_v255/traces/altpaths_full.yaml` | 5 | 4 | `f68e4ddabbfa400b7580697f5c5cdebcc86a5677bf1e9e09d501e8291c39e025` |
| `sources/ocf_llm/examples/idc_demo_altpaths_v255/traces/altpaths_missing_both.yaml` | 3 | 2 | `1780ac3320ed3e116f385a6a19be6be9eb0fa7619782897757ffddab211fe9c3` |
| `sources/ocf_llm/examples/idc_demo_article53_v251/traces/article53_fail_v1.yaml` | 4 | 3 | `fedd76dd6c6270f6c6307215cbeb6adc2995b294cdb5c1ce1b135743ea741b35` |
| `sources/ocf_llm/examples/idc_demo_article53_v251/traces/article53_fail_v2.yaml` | 4 | 3 | `392587482969fc3244e9fd4b3829afcf7cdc5e5a3632d24f1cdf597dc7c1b168` |
| `sources/ocf_llm/examples/idc_demo_article53_v251/traces/article53_pass_v1.yaml` | 4 | 3 | `a95fc91dd9e729974c87cc85fae10647eed4983014112e5c162c788efbe345cd` |
| `sources/ocf_llm/examples/idc_demo_article53_v251/traces/article53_pass_v2.yaml` | 5 | 4 | `f68e4ddabbfa400b7580697f5c5cdebcc86a5677bf1e9e09d501e8291c39e025` |
| `sources/ocf_llm/examples/idc_demo_article53_v252/traces/article53_fail_v1.yaml` | 4 | 3 | `fedd76dd6c6270f6c6307215cbeb6adc2995b294cdb5c1ce1b135743ea741b35` |
| `sources/ocf_llm/examples/idc_demo_article53_v252/traces/article53_fail_v2.yaml` | 4 | 3 | `392587482969fc3244e9fd4b3829afcf7cdc5e5a3632d24f1cdf597dc7c1b168` |
| `sources/ocf_llm/examples/idc_demo_article53_v252/traces/article53_pass_v1.yaml` | 4 | 3 | `a95fc91dd9e729974c87cc85fae10647eed4983014112e5c162c788efbe345cd` |
| `sources/ocf_llm/examples/idc_demo_article53_v252/traces/article53_pass_v2.yaml` | 5 | 4 | `f68e4ddabbfa400b7580697f5c5cdebcc86a5677bf1e9e09d501e8291c39e025` |
| `sources/ocf_llm/examples/idc_demo_article53_v253/traces/article53_fail_v1.yaml` | 4 | 3 | `fedd76dd6c6270f6c6307215cbeb6adc2995b294cdb5c1ce1b135743ea741b35` |
| `sources/ocf_llm/examples/idc_demo_article53_v253/traces/article53_fail_v2.yaml` | 4 | 3 | `392587482969fc3244e9fd4b3829afcf7cdc5e5a3632d24f1cdf597dc7c1b168` |
| `sources/ocf_llm/examples/idc_demo_article53_v253/traces/article53_pass_v1.yaml` | 4 | 3 | `a95fc91dd9e729974c87cc85fae10647eed4983014112e5c162c788efbe345cd` |
| `sources/ocf_llm/examples/idc_demo_article53_v253/traces/article53_pass_v2.yaml` | 5 | 4 | `f68e4ddabbfa400b7580697f5c5cdebcc86a5677bf1e9e09d501e8291c39e025` |
| `sources/ocf_llm/examples/idc_demo_article53_v254/traces/article53_fail_v1.yaml` | 4 | 3 | `fedd76dd6c6270f6c6307215cbeb6adc2995b294cdb5c1ce1b135743ea741b35` |
| `sources/ocf_llm/examples/idc_demo_article53_v254/traces/article53_fail_v2.yaml` | 4 | 3 | `392587482969fc3244e9fd4b3829afcf7cdc5e5a3632d24f1cdf597dc7c1b168` |
| `sources/ocf_llm/examples/idc_demo_article53_v254/traces/article53_pass_v1.yaml` | 4 | 3 | `a95fc91dd9e729974c87cc85fae10647eed4983014112e5c162c788efbe345cd` |
| `sources/ocf_llm/examples/idc_demo_article53_v254/traces/article53_pass_v2.yaml` | 5 | 4 | `f68e4ddabbfa400b7580697f5c5cdebcc86a5677bf1e9e09d501e8291c39e025` |
| `sources/ocf_llm/examples/idc_demo_article53_v255/traces/article53_anyof_hardfail_v2.yaml` | 5 | 4 | `06b56cd75cf07ee42d584558e0a071f2009780570cb0a66d4f2d578c9d8a1b2f` |
| `sources/ocf_llm/examples/idc_demo_article53_v255/traces/article53_fail_v1.yaml` | 4 | 3 | `fedd76dd6c6270f6c6307215cbeb6adc2995b294cdb5c1ce1b135743ea741b35` |
| `sources/ocf_llm/examples/idc_demo_article53_v255/traces/article53_fail_v2.yaml` | 4 | 3 | `392587482969fc3244e9fd4b3829afcf7cdc5e5a3632d24f1cdf597dc7c1b168` |
| `sources/ocf_llm/examples/idc_demo_article53_v255/traces/article53_pass_v1.yaml` | 4 | 3 | `a95fc91dd9e729974c87cc85fae10647eed4983014112e5c162c788efbe345cd` |
| `sources/ocf_llm/examples/idc_demo_article53_v255/traces/article53_pass_v2.yaml` | 5 | 4 | `f68e4ddabbfa400b7580697f5c5cdebcc86a5677bf1e9e09d501e8291c39e025` |
| `sources/ocf_llm/examples/impact_demo_v176/impact_report_v176.json` | 2 | 2 | `49531ead4872ab537f1ead79a750b6a867b465cbb234beecb2f61dc43b7185d6` |
| `sources/ocf_llm/examples/jbc_demo_v235/jbc_demo_v1.json` | 4 | 4 | `fb7610c88311f071df470ad7ae7d461e4de246e2226139dbd7eb1ce2242ee795` |
| `sources/ocf_llm/examples/lean_autoformalization_specbind_abom.yaml` | 5 | 3 | `b59eb54c28585dc60a1fc8162e44de4bb8e60bd0924976742f554b4b762a8959` |
| `sources/ocf_llm/examples/lean_autoformalization_specbind_trace.yaml` | 5 | 3 | `60f13fbd466fb019d1ff21a81ed7531078646ce49ddc154dfc539826be981c65` |
| `sources/ocf_llm/examples/lean_passk_abom.yaml` | 2 | 1 | `02d91f51bb775c109236e61327d73b4b8b269582b1c78c86754bda84717ab56a` |
| `sources/ocf_llm/examples/lean_passk_abom_v2.yaml` | 2 | 1 | `d0c426986117365469d8f54771f8c37cbf46261076bd2d378e99f5d813aec0e0` |
| `sources/ocf_llm/examples/mbc_drc_toy_trace_fail_dup_service_v1.yaml` | 6 | 2 | `294c10a12a1df71b53d61d9ec8a434242d3356f9ade3fbdfbd3800004392ae18` |
| `sources/ocf_llm/examples/mbc_drc_toy_trace_v1.yaml` | 8 | 3 | `ec9dc2289da83c126e6576432df1a0e679a3a61166b0e0f74eca7448579c30ca` |
| `sources/ocf_llm/examples/ndc_noop_update_v175/resolver_trace_noop.yaml` | 10 | 4 | `ddd30819da229fb7c7bb29bdb28283b4bd223a988bd1b805c8924eb2d45a9cfb` |
| `sources/ocf_llm/examples/ndc_noop_update_v175/resolver_trace_real.yaml` | 10 | 4 | `f89146180fdf943393bd3a0bb1973e2104764e8ddc7f745321e0cb425a2b88b4` |
| `sources/ocf_llm/examples/output_credential_demo_v242/demo_report.json` | 2 | 2 | `1ad74a4b87dcb89853be9749fc966436adb9f990971eb3a127dd1b67115eac65` |
| `sources/ocf_llm/examples/pcb_equivocation_demo_v238/equivocation_report.json` | 1 | 1 | `6ae991e07625b8512a5d9fd63c4d1ba9454477eb1f7cf553828e35c9f5020d69` |
| `sources/ocf_llm/examples/pip_gate_decision_annexiv_tampered_v1.json` | 1 | 1 | `99e684763c77de0630ca9259624d138486e75a1acfdf0ae1c3e8e6fbeb6f111b` |
| `sources/ocf_llm/examples/pip_gate_decision_annexiv_v1.json` | 1 | 1 | `a67cb244c8446226ffe1c93b3a95c1aa6cb906e03937d826f6431aadcc4ec10c` |
| `sources/ocf_llm/examples/publication_or_refusal_demo_v123/trace_pub_rec.yaml` | 1 | 1 | `08116bee4388588fdb0f8c50ae4fcc3dbb84c5e4c8a364de8c286370ef8004b5` |
| `sources/ocf_llm/examples/publication_or_refusal_demo_v123/trace_pub_scitt.yaml` | 1 | 1 | `84fd617fe14a7b5178f3217a539437fb8fdb4d769955e20d9f56f1f0ebf7328b` |
| `sources/ocf_llm/examples/publication_or_refusal_demo_v123/trace_published.yaml` | 6 | 3 | `5e8ba1abf29f0535c0152ac0459644911e88f5a5e2d7511bb527e80a8726cc32` |
| `sources/ocf_llm/examples/publication_or_refusal_demo_v123/trace_refusal.yaml` | 8 | 4 | `a24d1e328564f7cd6df6736abfe7acf13ccf4f120b632d38ccff4148224cbf0a` |
| `sources/ocf_llm/examples/resolver_bench_v2.json` | 16 | 9 | `940c7bf6639be05939f83c164071def5055bb44d25eeb77dc2462e2a7c668161` |
| `sources/ocf_llm/examples/resolver_bench_v3.json` | 14 | 8 | `2d49907d771ca43af17d672ed761f560da6849cf00ccaab3bb63bc4e18acf840` |
| `sources/ocf_llm/examples/resolver_trace_bfc_gap_demo_gapfail_v173.yaml` | 27 | 5 | `535db3d71b5865f8acce081ed8dc3de50426e78c92514c900f25462ef60204a7` |
| `sources/ocf_llm/examples/resolver_trace_bfc_gap_demo_pass_v173.yaml` | 39 | 7 | `834a0c5d42ce5acadee6f9b7e0b6dd60acdc9fa7f023e77a02a4ee05684cb4d9` |
| `sources/ocf_llm/examples/resolver_trace_bfc_gate_cadence_fail_v172.yaml` | 17 | 5 | `9ab15d32ecd9f5747a4d0453b05807635eacb0d080a4d084c5f53f3d9a336b17` |
| `sources/ocf_llm/examples/resolver_trace_bfc_gate_pass_v172.yaml` | 29 | 7 | `78cbf6c3c6ef4f634c6efdff3e392dc846febaf26049854352aa975d48c084af` |
| `sources/ocf_llm/examples/resolver_trace_bfc_gate_stale_v172.yaml` | 7 | 3 | `ff07f88c67bd638b710cbdcfffc4f7af4910655a25df37e942b7236e348c1d8e` |
| `sources/ocf_llm/examples/resolver_trace_cfic_ceb_toy.yaml` | 1 | 1 | `b6c89ae31c55f5f46c2c0706c209899c1a8b027c8298e011f69c7426e9365dcf` |
| `sources/ocf_llm/examples/resolver_trace_cpc_profile_receipt_pbc_policy_mismatch_v1.yaml` | 7 | 4 | `3d1eb1c7fc6419091b8776fdd9dde43cdc371a69080191524cbf7e4e14e02806` |
| `sources/ocf_llm/examples/resolver_trace_cpc_profile_receipt_pbc_stale_policy_v1.yaml` | 3 | 2 | `97870f87ca12a29a83723aca9167741d8a7083e71b5a9dd6c9d64ea44a5d31c0` |
| `sources/ocf_llm/examples/resolver_trace_cpc_profile_receipt_pbc_v1.yaml` | 31 | 7 | `f36bc10e7f932d5795a24701fddd3b51775c59942eca2955af327be959469e0d` |
| `sources/ocf_llm/examples/resolver_trace_eic_qic_dsc_buc_toy.yaml` | 15 | 5 | `65ef4542c18826f0168227f0fec2d06f9abfc2f1e1e7f4447c907381cf85c48a` |
| `sources/ocf_llm/examples/resolver_trace_eic_qic_dsc_cbb_toy.yaml` | 14 | 6 | `bfa8746ec02a99c9d5886a54dd36a430f516ea35642f7212d0838e8c60289839` |
| `sources/ocf_llm/examples/resolver_trace_eic_qic_dsc_toy.yaml` | 12 | 5 | `782504a174686c5fe74c3a3cbf7d769a39979f374b259ad630ca2ac24e5ef381` |
| `sources/ocf_llm/examples/resolver_trace_eic_qic_latency.yaml` | 3 | 3 | `7b3b1e5d8f7130912cf390fde2ad149e7777b2050fb3eadda3815bd58d569aeb` |
| `sources/ocf_llm/examples/resolver_trace_eic_qic_latency_annexiv_v1.yaml` | 4 | 3 | `3f9b016408e7f3af50edf67dfdc8e821b9c31f0d345efb40436ab8a9d5704f34` |
| `sources/ocf_llm/examples/resolver_trace_eic_qic_spc_toy.yaml` | 12 | 5 | `241bcb734bbadea3f4c86a54276e8b292030c0d9f45f0cd2c1cdbd9035161835` |
| `sources/ocf_llm/examples/resolver_trace_emic_toy.yaml` | 6 | 2 | `033881032b6ab14686053fb8ee7a30b06d3c3c95cff7ed1af9cae816e3b33913` |
| `sources/ocf_llm/examples/resolver_trace_ibc_unified_budget_v1.yaml` | 6 | 2 | `70a8983ef6f626ee69d1fa212e42bb8a0e9690d717cc891219c6f6357ce12fe8` |
| `sources/ocf_llm/examples/resolver_trace_ibc_unified_budget_v154.yaml` | 6 | 2 | `7a6d96115c6f631241827c18b2d08940eb1b02c25e7e0ed612f103f72ded69cf` |
| `sources/ocf_llm/examples/resolver_trace_ibc_unified_budget_v155.yaml` | 6 | 2 | `abda5e45eac2892f5474620c5a8c5474e7bff305990385dacd7111bf3388cc0c` |
| `sources/ocf_llm/examples/resolver_trace_lean_autoformalization_specbind.yaml` | 5 | 3 | `b9380c73e3fa8ed71ee2292f8d914269995baa624b0a4e3464c7cf6d80dff76d` |
| `sources/ocf_llm/examples/resolver_trace_lean_passk.yaml` | 2 | 1 | `d123db4851f4d08ec8a0877928cb15dac0dd9533d4420e3f83bfb1b661862701` |
| `sources/ocf_llm/examples/resolver_trace_lean_passk_v2.yaml` | 2 | 1 | `b12bdd915dd77919aef795480ee5782a05cd027f62dda24734bb349f99551407` |
| `sources/ocf_llm/examples/resolver_trace_lnf_eqc_dedup.yaml` | 6 | 3 | `39fdaeacb43a96c112daad94a8f8cfbb75c29a7715b33fbce1cd051d9f4ccd7b` |
| `sources/ocf_llm/examples/resolver_trace_monitoring_csic.yaml` | 2 | 1 | `22afe394a25c8e75ebfeb56bad1a8650fab88075aa5a772a5ec855a2119eb579` |
| `sources/ocf_llm/examples/resolver_trace_monitoring_elond_dcc_adapter_v153.json` | 16 | 3 | `8d7c4ca378ecc7b5345f00d271f951fcd5dbd56b5c385006eff5e381c2889e91` |
| `sources/ocf_llm/examples/resolver_trace_monitoring_elond_rbc_v149.yaml` | 6 | 3 | `88f71049d9f0a18002b19ef8479d824bb593e1c66da190e01d683826d8bb9b8a` |
| `sources/ocf_llm/examples/resolver_trace_monitoring_elond_tsp_v150.yaml` | 4 | 2 | `6b1a8f422facaa6bad6fb18c7bc84293530831fa1ad19334ce1bbddf5e33ca12` |
| `sources/ocf_llm/examples/resolver_trace_monitoring_elond_v148.yaml` | 2 | 1 | `1be4daafd432a2d51a5df663c303f6a815b263a9052f34b1195755b3cac2b30e` |
| `sources/ocf_llm/examples/resolver_trace_oci_gate_annexiv_v1.yaml` | 4 | 3 | `3f9b016408e7f3af50edf67dfdc8e821b9c31f0d345efb40436ab8a9d5704f34` |
| `sources/ocf_llm/examples/resolver_trace_pip_gate_annexiv_v1.yaml` | 4 | 3 | `3f9b016408e7f3af50edf67dfdc8e821b9c31f0d345efb40436ab8a9d5704f34` |
| `sources/ocf_llm/examples/resolver_trace_rbc_compiler_demo_clean_v1.yaml` | 15 | 4 | `5143aae44722f665f79552d7d20c1960028f5ff0469a1d154d7de6b68df7fee3` |
| `sources/ocf_llm/examples/resolver_trace_rbc_compiler_demo_v3.yaml` | 11 | 2 | `5b58c6b0d4d8c70e4ef1eea786c256d6b7c4aa128308ffd0194d9a6bd86ba405` |
| `sources/ocf_llm/examples/resolver_trace_rbc_compiler_demo_v4.yaml` | 17 | 5 | `f4e6e6d201ed099619cfd55873704b696c2e2e4cfac06dd64a09a9f52ab53566` |
| `sources/ocf_llm/examples/resolver_trace_sabom_mcp_episode.yaml` | 3 | 1 | `3fbba4d31b4a242e124c9d48a18944e468ac8eb51dbbc055f838398059d0f858` |
| `sources/ocf_llm/examples/resolver_trace_sabom_mcp_episode_multilog_fail_v1.yaml` | 9 | 4 | `7392f74603640e77109b513a0952a44d9b624cdd0155fd1affc5c1d0c145b9ab` |
| `sources/ocf_llm/examples/resolver_trace_sabom_mcp_episode_multilog_v1.yaml` | 12 | 5 | `fa84b8a9676779e798cfa4ce61dbd750972e6c7dc9197b1abbdb648c6e2de072` |
| `sources/ocf_llm/examples/resolver_trace_sabom_mcp_episode_projection.yaml` | 6 | 2 | `06ddfea6268e84586e5ef16a9fed14d8806222343211f2d9bd41b89c38a3e47d` |
| `sources/ocf_llm/examples/resolver_trace_sabom_mcp_episode_projection_v2_noise.yaml` | 8 | 2 | `63d8ae080133293f0e6174b76a2c150aefdbf6dbc1829775337749e637d2d391` |
| `sources/ocf_llm/examples/resolver_trace_sabom_mcp_episode_published.yaml` | 6 | 3 | `30bcf2a711a78d7d376df09862a413343dc95be23bca8d5d1fb965e680dfac34` |
| `sources/ocf_llm/examples/resolver_trace_sabom_mcp_episode_scitt_published.yaml` | 6 | 3 | `5dba58d5edac4aa811696eed58949e980e70afe2849a2efcb3450a09fe64c584` |
| `sources/ocf_llm/examples/resolver_trace_sic_zk_toy_privacy.yaml` | 3 | 3 | `8837221f429c9b34e813440eaffa3aca121a1a9fe334940ab599f0e194c92030` |
| `sources/ocf_llm/examples/resolver_trace_sic_zk_toy_privacy_vco.yaml` | 10 | 4 | `f2520c218dd27fda2901acc0e3c0c7c23013f4a3a8164fc0ad73815708a600f0` |
| `sources/ocf_llm/examples/resolver_trace_sic_zk_toy_privacy_vco_vte.yaml` | 13 | 6 | `28e27161833419a8310345fbb14c6495973064df78563226df2d6b35f600f81e` |
| `sources/ocf_llm/examples/resolver_trace_sic_zk_toy_privacy_vco_vte_vtp.yaml` | 15 | 7 | `90b5888e3e147f1a3c2f72a8d37c43929ead9025fa161f4e7c4a251cfd40326c` |
| `sources/ocf_llm/examples/resolver_trace_sic_zk_toy_privacy_vco_vte_vtpw.yaml` | 18 | 9 | `e20f5b253830feb527968980ce87800e3254ed909c14c2e7f760d6d94ee60d9f` |
| `sources/ocf_llm/examples/resolver_trace_sic_zk_toy_privacy_vco_vte_vtpw2.yaml` | 21 | 10 | `9f263fd58b3b03827b81cbb8188a4905877b11c8499174b64f952ad02c5f7ca5` |
| `sources/ocf_llm/examples/resolver_trace_sic_zk_toy_privacy_vco_vte_vtpw2_fresh.yaml` | 21 | 10 | `51dfad4b5a023de3cc84f35d2407712e21623c9398e138a091b29d5e91c2eccb` |
| `sources/ocf_llm/examples/resolver_trace_sic_zk_toy_privacy_vco_vte_vtpw2_fresh_rtm.yaml` | 21 | 10 | `b0fd334962ac224ddb96b99b922a3800b4742662598a7c6a353dd06e109d821c` |
| `sources/ocf_llm/examples/resolver_trace_sic_zk_toy_privacy_vco_vte_vtpw2_fresh_rtm_profile_v1.yaml` | 38 | 15 | `28e091664e66de550f013a4dfa3253dcac2abe8a99dae81683b02ac069373daa` |
| `sources/ocf_llm/examples/resolver_trace_sic_zk_toy_privacy_vco_vte_vtpw2_q1_fail.yaml` | 21 | 10 | `94d2bbd31631f2fc9459f06ee02180108f080634733373f458663ed99955e827` |
| `sources/ocf_llm/examples/resolver_trace_sic_zk_toy_privacy_vco_vte_vtpw2_stale_fail.yaml` | 21 | 10 | `b542bd3760a1bf519fa5809619986c2a569b8b28f1c18868b274a42c18656678` |
| `sources/ocf_llm/examples/resolver_trace_unified_gate_v156.yaml` | 33 | 5 | `86d5dfc8b5be8354d55d21177299c7945e448f48c362802ead2b536897fce511` |
| `sources/ocf_llm/examples/resolver_trace_unified_gate_v157.yaml` | 33 | 5 | `200b07b40cfcd6f935531d4977945e89f533eca5f4be0944a3e04ff5d0f852f2` |
| `sources/ocf_llm/examples/resolver_trace_unified_gate_v158.yaml` | 41 | 7 | `f5d2f39338242bee8a04e96eced01a1e92d44e51ab91b53eccca6d8ab9baf060` |
| `sources/ocf_llm/examples/scitt_binding_attack_v122/naive_verify_good.json` | 1 | 1 | `8c2a9fea22bb9b302dc521601d7b8ee6b0cab66323a508288465e12cf0ca647d` |
| `sources/ocf_llm/examples/scitt_binding_attack_v122/naive_verify_tampered.json` | 1 | 1 | `f6022664aa7004eacdcfd51833ac7337990032ddca9e6e554fe86910d426dcc9` |
| `sources/ocf_llm/examples/scitt_binding_attack_v122/resolver_trace_good.yaml` | 3 | 2 | `c05971825d00939874c8bde3963ed6dc4423a4890ea5a66eccda13453a225179` |
| `sources/ocf_llm/examples/scitt_binding_attack_v122/resolver_trace_tampered.yaml` | 2 | 1 | `0c969ea0b3875cf5dd0238f4e7bd9cce56a80f146d43313a0d6fa95ba96574b4` |
| `sources/ocf_llm/examples/scitt_binding_attack_v123/naive_verify_good.json` | 1 | 1 | `ab6fa5046a9c1b5b8e2e0a9ea5eb09c81d1767dafa2bfa18a6f0cca756028b3f` |
| `sources/ocf_llm/examples/scitt_binding_attack_v123/naive_verify_tampered_inclusion.json` | 1 | 1 | `ecf39f718f37726c38a2e4d0c9497598b080860f1d722b61316cd912b8934ba8` |
| `sources/ocf_llm/examples/scitt_binding_attack_v123/naive_verify_tampered_statement.json` | 1 | 1 | `6fce428f47486540e5e383a11bbc0e4e8f7e15594f924cb4d798e047f34c201a` |
| `sources/ocf_llm/examples/scitt_binding_attack_v123/resolver_trace_good.yaml` | 3 | 2 | `18f5c9c4353ba3f4f7ce755d3c676f980af755c763491d050fb139f675eee692` |
| `sources/ocf_llm/examples/scitt_binding_attack_v123/resolver_trace_tampered_inclusion.yaml` | 2 | 1 | `dbb20c5ca7b843648c765930a9fe2e8b32ea45f6df145cb4ca75148101244b8d` |
| `sources/ocf_llm/examples/scitt_log_substitution_v124/naive_verify_adversary.json` | 1 | 1 | `d99b617d2d2d9386ed46b23dee1e23d798b6191ab5406f84da35adfba3cc6181` |
| `sources/ocf_llm/examples/scitt_log_substitution_v124/naive_verify_adversary_pinned.json` | 1 | 1 | `17fccfd87b6b5935ab6fd26f2fe401419b0e02552b956b3a9775565f28b2d6e2` |
| `sources/ocf_llm/examples/scitt_log_substitution_v124/naive_verify_honest.json` | 1 | 1 | `ca0a254c4c861ca2493fc0aea86210eb9cee33cb53963a1c0749d1b36d10e874` |
| `sources/ocf_llm/examples/scitt_log_substitution_v124/resolver_trace_pinned_adversary.yaml` | 2 | 1 | `716102dddc59ad81367b5dd317fdcaf1188e8da195fc1a02d8df8ed8b7ed17ba` |
| `sources/ocf_llm/examples/scitt_log_substitution_v124/resolver_trace_pinned_honest.yaml` | 3 | 2 | `fda7233fdf9de2fd32f1ccccbd7ba08bfb4dadd6134ea54b0d66622fb809f0a9` |
| `sources/ocf_llm/examples/scitt_log_substitution_v124/resolver_trace_unpinned_adversary.yaml` | 3 | 2 | `854a8e41dc7f8c275cb3472e35f0a775b70ff0c5df8cbdafd04b0e878bbefedf` |
| `sources/ocf_llm/examples/scitt_log_substitution_v124/resolver_trace_unpinned_honest.yaml` | 3 | 2 | `95ee0be86812c6310ffef44750ee70020f657322d76ee423077b9f0789189363` |
| `sources/ocf_llm/examples/scitt_profile_drift_v161/trace_freshreceipt_v161.yaml` | 3 | 2 | `5a17bb659e9a2606c3dd4694ef2f7742b78a38d7ae97e1a93da09aa533965df0` |
| `sources/ocf_llm/examples/scitt_profile_drift_v161/trace_oldreceipt_v161.yaml` | 3 | 2 | `8376ac19d2e92d4248da027b346ac3494c26a0ddc13ab9893c52928726aa9f7f` |
| `sources/ocf_llm/examples/sic_zk_toy_privacy_abom.yaml` | 3 | 3 | `94ed1b376af2a6028a187b16678f883ebed9a02657a1f81813573f5bc0dd38ae` |
| `sources/ocf_llm/examples/tmp_hotspot.json` | 3 | 3 | `c4b3d9b9b770adf1c3c053d89ad2240e14958771ef9378551463e444bd535605` |
| `sources/ocf_llm/examples/tmp_hotspot_180.json` | 3 | 3 | `323122dbfec28f09f6a8f3a63e14adeb143b51e0a5d119d72582ac2196c60fca` |
| `sources/ocf_llm/examples/tmp_hotspot_30.json` | 3 | 3 | `33e93331a216bb0bbcac50b9b27d83f7bdfbce3f4a7559ee4c7c632ad530981f` |
| `sources/ocf_llm/examples/tmp_hotspot_90.json` | 3 | 3 | `bc0da1f9f2d6c80e6aafae1a011796d0996d20ea02fbfa5fbadaa624d68bd0a0` |
| `sources/ocf_llm/examples/trace_aic_rollup_v1.yaml` | 3 | 2 | `bff87f6460870d8f6de57615481dcd7083b03ea1c9d8a56c31caf667a22e36bc` |
| `sources/ocf_llm/examples/trace_fresh_rtm_profile_stale_policy_v84.yaml` | 27 | 12 | `3d95000d642742fd5d05bcc0113435f8e5986b529e947bae145d2bb5477a1f26` |
| `sources/ocf_llm/examples/trace_fresh_rtm_profile_v84.yaml` | 38 | 15 | `bce4ec5c9232a3a7767c0b8a65557cbf8fd2df54f8d886109a8cdc58dfd78296` |
| `sources/ocf_llm/examples/trace_refusal.yaml` | 8 | 4 | `50236b1712f06b7c39f30c3e09010408db0ce073b423281bcaca25a389fb52dc` |
| `sources/ocf_llm/examples/trace_test.yaml` | 3 | 3 | `7b3b1e5d8f7130912cf390fde2ad149e7777b2050fb3eadda3815bd58d569aeb` |
| `sources/ocf_llm/examples/transparency_gate_demo_v1/resolver_trace_wco_ok_v120.yaml` | 12 | 5 | `8257ccabae5a0065c28523d98945af768f9579c4b03add529cf17b31e41f4ca9` |
| `sources/ocf_llm/examples/verify_dof_attack_v222/trace_good.yaml` | 32 | 10 | `9673b718d5d54de7290793537d879a369896c69774712edcf04924c73fba7a75` |
| `sources/ocf_llm/examples/verify_dof_attack_v222/trace_good_legacy_failclosed.yaml` | 32 | 10 | `4a1f18388257c6cc65f910501546658fe84a0e0d534d4113b21fdd24289f5659` |
| `sources/ocf_llm/examples/verify_dof_attack_v222/trace_tampered_no_drc.yaml` | 30 | 9 | `d585c531bb877e7879ce1e4679b6351162f39be4b5f6b8e34522f141c3c02a31` |
| `sources/ocf_llm/examples/wco_demo_transparency_gate_v121/resolver_trace_wco_gate_allow.yaml` | 12 | 5 | `cf63292803d52044ff0859229ba8e3e62301efcf3a6c27c90e263842bb0d51d0` |
| `sources/ocf_llm/examples/wco_demo_transparency_gate_v121/resolver_trace_wco_gate_stale.yaml` | 12 | 5 | `15025aa321d11ecfe1d3513736e4b24084e42bd0455a654cc76ab45fdce04406` |
| `sources/ocf_llm/examples/wco_demo_v1/resolver_trace_wco_fail_split.yaml` | 11 | 4 | `9cb056ad3b5e6fccf0f70f04e78500280eb7cd21b12486f5ba6cdc8ac9611427` |
| `sources/ocf_llm/examples/wco_demo_v1/resolver_trace_wco_ok.yaml` | 12 | 5 | `6df0523b1f28ec79c993b9bd1f34722b4228e523febdd22db7aed9ce22f10bbb` |
| `sources/ocf_llm/examples/wco_demo_v120_fresh/resolver_trace_wco_fail_split.yaml` | 11 | 4 | `ec43c926cea9fc7dc1ccfdb6b544dbb07687b858a9e9423225e2b3288642f1b2` |
| `sources/ocf_llm/examples/wco_demo_v120_fresh/resolver_trace_wco_ok.yaml` | 12 | 5 | `80400018f7bd37724d7e6cf76ec143d18a2f2987e169c8f14cf250561dd8c4c7` |

## Remaining unresolved/external references

| Path | References | Sample |
| --- | ---: | --- |
| `artifacts/curated/zkrtp_v2/policy_report.json` | 1 | `/mnt/data/zk_rtp_paper_v0.27` × 1 |
| `sources/ocf_llm/examples/mer_demo/receipt_cache_index.json` | 1 | `/mnt/data/ocf_llm_paper_v196_work/ocf_llm_paper_evolving_v196/examples/mer_demo/receipt_cache` × 1 |
| `sources/ocf_llm/examples/nuc_demo/receipt_cache_ok_index.json` | 1 | `/mnt/data/ocf_llm_paper_v197_work/ocf_llm_paper_evolving_v197/examples/nuc_demo/receipt_cache_ok` × 1 |
| `sources/ocf_llm/examples/pip_gate_decision_annexiv_tampered_v1.json` | 1 | `/mnt/data/ocf_llm_paper_v97/` × 1 |
| `sources/ocf_llm/examples/pip_gate_decision_annexiv_v1.json` | 1 | `/mnt/data/ocf_llm_paper_v97/` × 1 |
| `sources/ocf_llm/examples/prc_put_demo_v203/prc.json` | 1 | `/mnt/data/ocf_llm_paper_evolving_current_v203/examples/prc_put_demo_v203` × 1 |
| `sources/ocf_llm/examples/release_train_overlap_demo_v211/summary.json` | 1 | `/mnt/data/ocf_llm_paper_evolving_current_v211/examples/release_train_overlap_demo_v211` × 1 |
| `sources/ocf_llm/examples/resolver_bench_v1.json` | 1 | `/mnt/data/ocf_llm_paper_v87` × 1 |
| `sources/ocf_llm/examples/resolver_bench_v2.json` | 1 | `/mnt/data/ocf_llm_paper_workspace_v91/ocf_llm_paper_v90` × 1 |
| `sources/ocf_llm/examples/resolver_bench_v3.json` | 1 | `/mnt/data/ocf_llm_paper_workspace_v91/ocf_llm_paper_v90` × 1 |
| `sources/ocf_llm/examples/resolver_trace_sic_zk_toy_privacy_vco_vte_vtpw2_fresh_rtm.yaml` | 3 | `/mnt/data/ocf_llm_v81_work/ocf_llm_paper/examples/{` × 3 |
| `sources/ocf_llm/examples/runtime_gate_bench_v1.json` | 5 | `/mnt/data/ocf_llm_paper_v96` × 1<br>`/mnt/data/ocf_llm_paper_v96/examples/eic_qic_latency_eval_log_v1.jsonl\` × 1<br>`/mnt/data/ocf_llm_paper_v96/examples/eic_qic_latency_suite_v1.jsonl\` × 1<br>`/mnt/data/ocf_llm_paper_v96/examples/eic_qic_latency_summary_v1.json\` × 2 |
| `sources/ocf_llm/examples/scitt_log_substitution_v124/resolver_trace_base_pinned.yaml` | 1 | `/mnt/data/ocf_llm_paper_evolving_current_v125/ocf_llm_paper_evolving/examples/scitt_log_substitution_v124/scitt_receipt_placeholder.json` × 1 |
| `sources/ocf_llm/examples/scitt_log_substitution_v124/resolver_trace_base_unpinned.yaml` | 1 | `/mnt/data/ocf_llm_paper_evolving_current_v125/ocf_llm_paper_evolving/examples/scitt_log_substitution_v124/scitt_receipt_placeholder.json` × 1 |

## Remaining ambiguous references

| Path | References | Sample |
| --- | ---: | --- |
| `sources/ocf_llm/examples/publication_or_refusal_demo_v123/trace_pub_rec.yaml` | 1 | `/mnt/data/ocf_llm_paper_evolving_current_v123/ocf_llm_paper_evolving/examples/publication_or_refusal_demo_v123/mcp_episode_attempt_log_v1.jsonl` × 1 |
| `sources/ocf_llm/examples/publication_or_refusal_demo_v123/trace_pub_scitt.yaml` | 1 | `/mnt/data/ocf_llm_paper_evolving_current_v123/ocf_llm_paper_evolving/examples/publication_or_refusal_demo_v123/mcp_episode_attempt_log_v1.jsonl` × 1 |
