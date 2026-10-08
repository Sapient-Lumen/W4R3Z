# Cooperation Benchmark Card Scope Surface

Generated canonical boundary manifest for the compact cooperation-benchmark-card subsystem. This surface answers which files constitute the compact-card stack, which of those files are generated, and which paths are intentionally self-elided to avoid recursive hashing.

- subsystem_id: `compact-cooperation-benchmark-card-stack`
- scope_manifest_sha256: `aab567dd654ea003a86ed735c181cd0d76bbe23c18873f7e09797e7a6b4f89ea`
- category_count: 7
- path_count: 137
- source_path_count: 113
- generated_path_count: 24
- hashed_path_count: 113
- path_only_path_count: 22
- self_elided_path_count: 2

## Boundary rules

- `compact-card-boundary-is-explicit` — Treat only the paths named here as the compact-card subsystem boundary; do not infer extra scope from nearby repo layout or agent prose.
- `generated-vs-source-stays-typed` — Keep source contracts (schemas, builders, validators, doctrine, examples, tooling) distinct from generated reports/docs so inheritors know what to edit versus what to rebuild.
- `self-entries-are-path-only` — The scope surface includes its own generated report/doc paths, but marks them self-elided so the manifest stays exact without recursive hash dependency.

## Category summary

| category_id | path_count | summary |
|---|---:|---|
| `example-lineage-artifacts` | 7 | Worked example cards, rendered markdown, and retained receipts that exercise the compact-card lineage machinery. |
| `tooling-and-schemas` | 17 | Compact-card wrapper/tool entrypoints plus the schema contracts for cards, receipts, and inheritor surfaces. |
| `report-builders` | 12 | Builders that regenerate the compact-card reports and generated docs. |
| `validators` | 18 | Compact-card validators that keep the subsystem contracts and durable command doctrine machine-checkable. |
| `generated-docs` | 12 | Generated human-readable surfaces that mirror the compact-card report layer. |
| `generated-reports` | 12 | Generated machine-readable surfaces that constitute the compact-card control plane. |
| `program-doctrine` | 59 | Program doctrine and topic notes that explain why the compact-card surfaces exist and how inheritors should interpret them. |

## Verification commands

- `./grpy ./scripts/test/check_cooperation_benchmark_card_scope_surface.py`
- `./grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py`
- `./grpy ./scripts/test/check_cooperation_benchmark_card_handoff_pack.py`

## Refresh commands

- `./grpy ./scripts/report/build_cooperation_benchmark_card_scope_surface.py --write`
- `./grpy ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write`
- `./grpy ./scripts/report/build_cooperation_benchmark_card_handoff_pack.py --write`

## Category details

### `example-lineage-artifacts`

Worked example cards, rendered markdown, and retained receipts that exercise the compact-card lineage machinery.

| path | role | stage | integrity_mode | bytes | sha256 |
|---|---|---|---|---:|---|
| `examples/snapshots/cooperation_benchmark_card_example.json` | `example-card` | `source` | `hashed` | 6891 | `e033c1d6dd6970f7ed1ffd9a178e92e094cb14c0bdd02f03751e04bae131e8ee` |
| `examples/snapshots/cooperation_benchmark_card_example.md` | `example-rendered-markdown` | `source` | `hashed` | 6647 | `26a4710caee71ea2d65798f7f377ebd174a7c44e12820f49593757881e7e5b60` |
| `examples/snapshots/cooperation_benchmark_card_example.freeze_receipt.json` | `example-freeze-receipt` | `source` | `hashed` | 963 | `6760bc495711b3eb61ba6486da0a989c5d6dba786efb293082edda1ed7f7b2bd` |
| `examples/snapshots/cooperation_benchmark_card_example.delta_receipt.json` | `example-delta-receipt` | `source` | `hashed` | 1323 | `c98e0e9b9336579afcd617ae733c199b6a44f44df3726578756892c37192cc72` |
| `examples/snapshots/cooperation_benchmark_card_example_v2.json` | `example-card` | `source` | `hashed` | 6924 | `a2f5c4aa0ee8263d3d24d24ad1fe6ef69b421ddaff6718c4a7cfea57862db6db` |
| `examples/snapshots/cooperation_benchmark_card_example_v2.md` | `example-rendered-markdown` | `source` | `hashed` | 6680 | `ef9d265d3059aed17cc2607c6cb9d74f7f31e1be952e37463903e3d3a7d3d1c9` |
| `examples/snapshots/cooperation_benchmark_card_example_v2.freeze_receipt.json` | `example-freeze-receipt` | `source` | `hashed` | 1375 | `faecd1ec68b9793884670d29d49bbb5b519ac1d8f44326d4d06825d61f38e4b4` |

### `tooling-and-schemas`

Compact-card wrapper/tool entrypoints plus the schema contracts for cards, receipts, and inheritor surfaces.

| path | role | stage | integrity_mode | bytes | sha256 |
|---|---|---|---|---:|---|
| `grpy` | `python-wrapper` | `source` | `hashed` | 89 | `a9dc5b34831b0293085fbceaca888fc5cb82fe252709740ec6aded4cf7a77fcc` |
| `scripts/tools/cooperation_benchmark_card.py` | `card-tool` | `source` | `hashed` | 20182 | `85740c85f6e31e176a716d58a1f3ce51508d3511fa3caccabd66465d85dfc7b0` |
| `schemas/cooperation_benchmark_card.schema.json` | `schema` | `source` | `hashed` | 9615 | `4c73b5ad7c0a76c079864c8ec9035c1bf7595e553bbb3f8cb4517ab296e05b25` |
| `schemas/cooperation_benchmark_card_delta_receipt.schema.json` | `schema` | `source` | `hashed` | 1918 | `230165dfd3d73553faf9868f44238f8ae646f84aed0c2cda1f4356916ec6a5c5` |
| `schemas/cooperation_benchmark_card_freeze_receipt.schema.json` | `schema` | `source` | `hashed` | 2553 | `d5507138230c506d84cd85af34a6ed1d3b9da6f9fb30a38f5b064cdf3b92aefd` |
| `schemas/cooperation_benchmark_card_heads_register.schema.json` | `schema` | `source` | `hashed` | 5050 | `9642921d00b2dffda63d2dea330d786b20838ff189b3b13f6305f4861b3d8a09` |
| `schemas/cooperation_benchmark_card_review_queue.schema.json` | `schema` | `source` | `hashed` | 2927 | `8ffdfc36357d66d379c95b6d4a126cb0e3685281d8a95c746f86760da8bbfbe5` |
| `schemas/cooperation_benchmark_card_inventory.schema.json` | `schema` | `source` | `hashed` | 7796 | `ee26e3a90a568e7b49fa40538a7ec11f767603fda51d8ac5826201d81507d791` |
| `schemas/cooperation_benchmark_card_citation_surface.schema.json` | `schema` | `source` | `hashed` | 3772 | `483668b40ee934bf66bc92dd5086f610d5c37ddd96f83bd4bb7166482b386353` |
| `schemas/cooperation_benchmark_card_handoff_pack.schema.json` | `schema` | `source` | `hashed` | 14183 | `ddcb5ca36de4211df5efe40f47713c9a9e041156db3afd2f6ca697953f27444b` |
| `schemas/cooperation_benchmark_card_macro_review_queue.schema.json` | `schema` | `source` | `hashed` | 4385 | `93d9ef7a0b9b89003f9d062139f19cbb8a63e4dda788128c1f150a92a0e7d4df` |
| `schemas/cooperation_benchmark_card_control_plane.schema.json` | `schema` | `source` | `hashed` | 15899 | `3230cf123fc43ea074757768a1564af731919dd709486dc782132840a54e8792` |
| `schemas/cooperation_benchmark_card_next_action_witness.schema.json` | `schema` | `source` | `hashed` | 30043 | `8e98b7f00025a4aecb3800ea7b1185aade47753d433e420834898c8b46f1df01` |
| `schemas/cooperation_benchmark_card_next_action.schema.json` | `schema` | `source` | `hashed` | 31496 | `6eab3fbfa0203e090f06c2fcd76b0f51f22f2f664834e2982e9874563c9c0b14` |
| `schemas/cooperation_benchmark_card_execution_lanes.schema.json` | `schema` | `source` | `hashed` | 4871 | `3c52c4d524aec1aa2fd70eaddbea24c2143aa686c08d9326a076f57f86bd88ab` |
| `schemas/cooperation_benchmark_card_taxonomy.schema.json` | `schema` | `source` | `hashed` | 2998 | `d3b39c7752abb7da9846721aec485e45f54279bdb4c4ec93108bb1054d0b2b13` |
| `schemas/cooperation_benchmark_card_scope_surface.schema.json` | `schema` | `source` | `hashed` | 6257 | `e53d24056c2774cb64651f3f793bd7eb2af7e6d2b70424902cb11df8bee5eefa` |

### `report-builders`

Builders that regenerate the compact-card reports and generated docs.

| path | role | stage | integrity_mode | bytes | sha256 |
|---|---|---|---|---:|---|
| `scripts/report/build_cooperation_benchmark_card_inventory.py` | `report-builder` | `source` | `hashed` | 15797 | `f27bd68883c6c58af3ccbae8b5df61ac2eaf8d02846fae594ebfd6cbbb450503` |
| `scripts/report/build_cooperation_benchmark_card_heads.py` | `report-builder` | `source` | `hashed` | 11358 | `8f44440dd371c127739246e9215ce7c1ce057244a0fd82dfc20a30681c372ba5` |
| `scripts/report/build_cooperation_benchmark_card_review_queue.py` | `report-builder` | `source` | `hashed` | 13872 | `51fe7a5be25a1272b75e3239ad0e76da6c8847c05e98f58cfa5558012d96ce95` |
| `scripts/report/build_cooperation_benchmark_card_citation_surface.py` | `report-builder` | `source` | `hashed` | 10716 | `7317943b0a7e1c1c6b979b6ddb81d95e9742cd6b268263904be26a5d89c0551e` |
| `scripts/report/build_cooperation_benchmark_card_handoff_pack.py` | `report-builder` | `source` | `hashed` | 32314 | `510b2a6297cf72d3486bfdc49e3d8d02032b7e3b836b7a47cd1930a7cccdb6e3` |
| `scripts/report/build_cooperation_benchmark_card_macro_review_queue.py` | `report-builder` | `source` | `hashed` | 8379 | `35df791901e1734afb10cc868b0022eb59694c0b1e50e138cdb232af1d89e05f` |
| `scripts/report/build_cooperation_benchmark_card_control_plane.py` | `report-builder` | `source` | `hashed` | 34115 | `13ce298bed043672eae07930a78a80c5f113ecc8cec28f1d3a3ab073ecea8cc5` |
| `scripts/report/build_cooperation_benchmark_card_next_action_witness.py` | `report-builder` | `source` | `hashed` | 54083 | `06fd7361205c7f03b7f929db209e119e4ee165d86bf3d07fda1cbe8b7217baaa` |
| `scripts/report/build_cooperation_benchmark_card_next_action.py` | `report-builder` | `source` | `hashed` | 32215 | `931768edd7414657d9d4868e2e6a19ed77e24c402fc05fcede99d050700c5da5` |
| `scripts/report/build_cooperation_benchmark_card_execution_lanes.py` | `report-builder` | `source` | `hashed` | 13773 | `b090a4afe394aae0f503580c84e061f99faa648e043543b18f498e60e079c03c` |
| `scripts/report/build_cooperation_benchmark_card_taxonomy.py` | `report-builder` | `source` | `hashed` | 27281 | `caaad9afb8ed5d7986fb7130115dc8402e15c3a713ee18868c44dec0a6a698c8` |
| `scripts/report/build_cooperation_benchmark_card_scope_surface.py` | `report-builder` | `source` | `hashed` | 30418 | `49d627901f1c7a286de7b259c3c101eae93141d537c432d599ce3f5b921384db` |

### `validators`

Compact-card validators that keep the subsystem contracts and durable command doctrine machine-checkable.

| path | role | stage | integrity_mode | bytes | sha256 |
|---|---|---|---|---:|---|
| `scripts/test/check_cooperation_benchmark_card_schema.py` | `validator` | `source` | `hashed` | 1510 | `cf841c4b6a386bcbe98eb69e79a79d5d2f573a51124b27705682aa61c6ba68ab` |
| `scripts/test/check_cooperation_benchmark_card_tooling.py` | `validator` | `source` | `hashed` | 2716 | `4cf1221d3e186eebedd194530c3fc326443a69cf6810bd529bf24c35afc37b62` |
| `scripts/test/check_cooperation_benchmark_card_readiness_lint.py` | `validator` | `source` | `hashed` | 1965 | `d9136ece37fe2ab2fd43b7a56efb416dfcc3a7eda8e0419e31d5cee12cde186a` |
| `scripts/test/check_cooperation_benchmark_card_freeze_receipt.py` | `validator` | `source` | `hashed` | 5079 | `7f04a80f13a7efdb46de1799ff112e5113a1a495960ac61ed8bed57587b30c6c` |
| `scripts/test/check_cooperation_benchmark_card_delta_receipt.py` | `validator` | `source` | `hashed` | 3857 | `cede85bbda20e527037781f052e44b36fe130714af174090b3947637554d455e` |
| `scripts/test/check_cooperation_benchmark_card_inventory.py` | `validator` | `source` | `hashed` | 2829 | `8963d2cc46f3463e2588c30f3d5cc69dcf2c40cdd836fe05c53206a170a77560` |
| `scripts/test/check_cooperation_benchmark_card_heads.py` | `validator` | `source` | `hashed` | 2666 | `da7dac1cc6480550dc9ae6af0b8e1175b23606ea149fa44e962215365c19a333` |
| `scripts/test/check_cooperation_benchmark_card_review_queue.py` | `validator` | `source` | `hashed` | 2074 | `1f1f665e4b0854b6bc8c480878b32e6619b1c25d56d792065ef027523c0c11ea` |
| `scripts/test/check_cooperation_benchmark_card_citation_surface.py` | `validator` | `source` | `hashed` | 2682 | `20d40ba61460a8a82fbef09078ac4f43674f4c12461c71545abadde6a7c8d64a` |
| `scripts/test/check_cooperation_benchmark_card_handoff_pack.py` | `validator` | `source` | `hashed` | 14699 | `e2082544296e6a6121c7acda1f9375370a7c470f0dcac3f1c2020c04ca8df8b3` |
| `scripts/test/check_cooperation_benchmark_card_macro_review_queue.py` | `validator` | `source` | `hashed` | 3263 | `ef9971694d26c964a3fb53f336c85a900f6ddc9015dbc7d8f20ec5db8f011cd9` |
| `scripts/test/check_cooperation_benchmark_card_control_plane.py` | `validator` | `source` | `hashed` | 24728 | `a4a410f473fb66511082b44b672a0fcb0f10509b623a651b6b07305d30b99dea` |
| `scripts/test/check_cooperation_benchmark_card_next_action_witness.py` | `validator` | `source` | `hashed` | 45733 | `782ea43176b4420bd5e9bd66b5703c4811ae7f87345936c444eea8fd63b87c36` |
| `scripts/test/check_cooperation_benchmark_card_next_action.py` | `validator` | `source` | `hashed` | 18200 | `4c5ef5836c38016c9b2f1867bff619225c198124e0b6db9538ee5bd859779ee1` |
| `scripts/test/check_cooperation_benchmark_card_execution_lanes.py` | `validator` | `source` | `hashed` | 3312 | `f28fa0ae7142c1277e86b8b3f9974e4184a722ce817d8dc8d410e865cd23dfe7` |
| `scripts/test/check_cooperation_benchmark_card_taxonomy.py` | `validator` | `source` | `hashed` | 9347 | `87affa4432ceb90a4fd8dc15d9191ec42ab27675d491a4143d5e561ee2466bf0` |
| `scripts/test/check_cooperation_benchmark_program_compact_card_command_surface.py` | `validator` | `source` | `hashed` | 2192 | `2cf741cf845ef2fc7a8e935570308c9297b2228fe56867ba52d189d4f7208ffc` |
| `scripts/test/check_cooperation_benchmark_card_scope_surface.py` | `validator` | `source` | `hashed` | 4030 | `164c563181efb219b9ff8167245ad9aa79753234d10f986605520c1305da4dce` |

### `generated-docs`

Generated human-readable surfaces that mirror the compact-card report layer.

| path | role | stage | integrity_mode | bytes | sha256 |
|---|---|---|---|---:|---|
| `docs/COOPERATION_BENCHMARK_CARD_INVENTORY.md` | `generated-doc` | `generated` | `path-only` | — | — |
| `docs/COOPERATION_BENCHMARK_CARD_HEADS.md` | `generated-doc` | `generated` | `path-only` | — | — |
| `docs/COOPERATION_BENCHMARK_CARD_REVIEW_QUEUE.md` | `generated-doc` | `generated` | `path-only` | — | — |
| `docs/COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md` | `generated-doc` | `generated` | `path-only` | — | — |
| `docs/COOPERATION_BENCHMARK_CARD_HANDOFF_PACK.md` | `generated-doc` | `generated` | `path-only` | — | — |
| `docs/COOPERATION_BENCHMARK_CARD_MACRO_REVIEW_QUEUE.md` | `generated-doc` | `generated` | `path-only` | — | — |
| `docs/COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md` | `generated-doc` | `generated` | `path-only` | — | — |
| `docs/COOPERATION_BENCHMARK_CARD_NEXT_ACTION_WITNESS.md` | `generated-doc` | `generated` | `path-only` | — | — |
| `docs/COOPERATION_BENCHMARK_CARD_NEXT_ACTION.md` | `generated-doc` | `generated` | `path-only` | — | — |
| `docs/COOPERATION_BENCHMARK_CARD_EXECUTION_LANES.md` | `generated-doc` | `generated` | `path-only` | — | — |
| `docs/COOPERATION_BENCHMARK_CARD_TAXONOMY.md` | `generated-doc` | `generated` | `path-only` | — | — |
| `docs/COOPERATION_BENCHMARK_CARD_SCOPE_SURFACE.md` | `generated-doc` | `generated` | `self-elided` | — | — |

### `generated-reports`

Generated machine-readable surfaces that constitute the compact-card control plane.

| path | role | stage | integrity_mode | bytes | sha256 |
|---|---|---|---|---:|---|
| `artifacts/reports/cooperation_benchmark_card_inventory.json` | `generated-report` | `generated` | `path-only` | — | — |
| `artifacts/reports/cooperation_benchmark_card_heads.json` | `generated-report` | `generated` | `path-only` | — | — |
| `artifacts/reports/cooperation_benchmark_card_review_queue.json` | `generated-report` | `generated` | `path-only` | — | — |
| `artifacts/reports/cooperation_benchmark_card_citation_surface.json` | `generated-report` | `generated` | `path-only` | — | — |
| `artifacts/reports/cooperation_benchmark_card_handoff_pack.json` | `generated-report` | `generated` | `path-only` | — | — |
| `artifacts/reports/cooperation_benchmark_card_macro_review_queue.json` | `generated-report` | `generated` | `path-only` | — | — |
| `artifacts/reports/cooperation_benchmark_card_control_plane.json` | `generated-report` | `generated` | `path-only` | — | — |
| `artifacts/reports/cooperation_benchmark_card_next_action_witness.json` | `generated-report` | `generated` | `path-only` | — | — |
| `artifacts/reports/cooperation_benchmark_card_next_action.json` | `generated-report` | `generated` | `path-only` | — | — |
| `artifacts/reports/cooperation_benchmark_card_execution_lanes.json` | `generated-report` | `generated` | `path-only` | — | — |
| `artifacts/reports/cooperation_benchmark_card_taxonomy.json` | `generated-report` | `generated` | `path-only` | — | — |
| `artifacts/reports/cooperation_benchmark_card_scope_surface.json` | `generated-report` | `generated` | `self-elided` | — | — |

### `program-doctrine`

Program doctrine and topic notes that explain why the compact-card surfaces exist and how inheritors should interpret them.

| path | role | stage | integrity_mode | bytes | sha256 |
|---|---|---|---|---:|---|
| `docs/BENCHMARK_PROGRAM.md` | `program-doctrine` | `source` | `hashed` | 64104 | `f90a7844ea3d3d0c8894e4eef717d3cb2953c3b67465d9fdef7ca1b0db6083a7` |
| `docs/LIBRARY/README.md` | `library-index` | `source` | `hashed` | 10341 | `8387165fa313b1b64c42a0b0b5359718e270ced0c3b55bdeec53e4c623b92d72` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_machine_checkable_compact_card_schema_and_worked_example.md` | `topic-note` | `source` | `hashed` | 1832 | `5a103f35f71c054074ea3ba676c65deb9c404efc5dcbc04791c1a85c6d72217c` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_scaffold_and_canonical_renderer_for_compact_cards.md` | `topic-note` | `source` | `hashed` | 2014 | `06c3f10a3bfd4ce4e271b849d2d7b30bf5abc365a7e5c149a443742100520dc2` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_distinguish_draft_valid_cards_from_claim_ready_cards_via_readiness_lint.md` | `topic-note` | `source` | `hashed` | 2338 | `26e1b9f888c2b1dd14880eee498f540e6e2ae0b72cb6aea2b30cfa280ac70c49` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_freeze_receipt_for_claim_ready_compact_cards.md` | `topic-note` | `source` | `hashed` | 2543 | `cfd3b5ad27ebc3e965b4c4f322f824d00f96c95db6462a23e372db116821dc93` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_canonical_delta_receipt_for_compact_cards.md` | `topic-note` | `source` | `hashed` | 2790 | `e80e905ff9d3deda20c3ddf61a31a64238313ed4988286ac70d82faf41d232e7` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_compact_inventory_and_lineage_register_for_cards_and_receipts.md` | `topic-note` | `source` | `hashed` | 1695 | `6c96cba613d56de5df8f089248cbe27d1bd54a3d92ec72e095617d5ead7235ee` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_lineage_head_register_for_compact_cards.md` | `topic-note` | `source` | `hashed` | 1725 | `9f4caa74cf4cd09b03a21a4b53b5a05848d6be2db44b39a7c0c6ced4eacbe936` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_fail_closed_when_freezing_compact_cards_against_stale_operational_heads.md` | `topic-note` | `source` | `hashed` | 1335 | `4080e143696d863ce4cdf9b34d94b7c368e76a92c4ad4f8d1379daf259b61648` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_an_actionable_review_queue_for_compact_cards.md` | `topic-note` | `source` | `hashed` | 1362 | `9a89810c20c802f94f16fe365756956710cfe8c039873784dd9213450a36f07e` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_fail_closed_citation_surface_for_compact_cards.md` | `topic-note` | `source` | `hashed` | 910 | `60661475b49047e095d5846fd23a1d2aa631d723e6e9ee444eff80029e38d6d2` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_fail_closed_when_retained_delta_receipts_no_longer_match_current_card_bytes.md` | `topic-note` | `source` | `hashed` | 1323 | `fd2915f6b129a9c9c3aa20a59f5cc29ee91a91e3e149466ececf3c7f7be5dde3` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_fused_control_plane_surface_for_compact_cards.md` | `topic-note` | `source` | `hashed` | 1199 | `0beaffbfacd9948421c52e1c82dd8565f3231311bf7bb807df0b30b01caf0cbe` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_a_deterministic_focus_lineage_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 1092 | `516544d33977447af8ea5547455f177753f3a816ee46bda448812687a932d500` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_a_primary_focus_open_path_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 1080 | `a61eef4b8647a1148cd2bb38d341e6425e71a93be7ac8d4a0941ff0aa980c64b` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_ordered_focus_open_paths_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 1105 | `38230072da06704c036fa4d5fc266b6c9473492e5e995ff22a2a445c18605470` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_role_annotated_focus_open_targets_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 1140 | `943933eb724c7ecc8d8115a78ea6b865ecc7d6f0a1bd2bada844b9eecefde09e` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_head_card_paths_and_a_primary_open_path_in_handoff_packs.md` | `topic-note` | `source` | `hashed` | 1479 | `ff27fdb1ce210c2691db3d49e0e779f4185f909d8f7cfb1930836f3d4bda88b8` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_role_annotated_entry_targets_in_handoff_packs.md` | `topic-note` | `source` | `hashed` | 1360 | `f2c647bce5ee0de966804b9ba76d16a3d540b8d4ec08fd3e7932077ee260e94d` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_role_annotated_primary_open_targets_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 787 | `d1d07e106ef3c9589fca9b51ce8b22ecb639dd8f035d02ef81f29b33a75b8846` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_role_annotated_focus_primary_verify_and_refresh_targets_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 972 | `43bb20debb124f166b4fe84a617e2f966a2c6d80f3685bcb81b801fd36df8069` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_commands_in_handoff_packs.md` | `topic-note` | `source` | `hashed` | 784 | `ca7cacaa5e7346bfd2392c981bad86f2d2e12153f060871a97fcbce9fa19d358` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_role_annotated_primary_verify_and_refresh_targets_in_handoff_packs.md` | `topic-note` | `source` | `hashed` | 1050 | `dc3332037fd66d9075342a5f4a0ca29865d0064aa6cf56bcd642be7de7df2c01` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_subject_role_codes_in_handoff_packs.md` | `topic-note` | `source` | `hashed` | 847 | `dc591ca30197d8be280d23a1934f12fb15382bebb6df9ad251401027bcd3ad7b` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_intent_summaries_in_handoff_packs.md` | `topic-note` | `source` | `hashed` | 851 | `ef13f0511a7d7171fe664b174f0638798a4cda7e35cfe3f20f203e6b793ca202` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_outcome_summaries_in_handoff_packs.md` | `topic-note` | `source` | `hashed` | 678 | `ca0181fb724a86c1f77eb90697807dde993fe79cd4fc2e10f4e19b1210be2453` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_effect_codes_in_handoff_packs.md` | `topic-note` | `source` | `hashed` | 886 | `22e1937cd55edcf769c7e2ffe3662181d42d0264541ae8bdaa3c0a482c26901d` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_target_bytes_in_handoff_packs.md` | `topic-note` | `source` | `hashed` | 855 | `0fdbf0f70ab311ee28173910ec53b3d4888aeb2e0cf63b88717930eaf2d01afe` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_target_sha256s_in_handoff_packs.md` | `topic-note` | `source` | `hashed` | 928 | `950337c515ce01cec7c16de331c3d7190e82aec7b79e55a6602a661d9ef83023` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_target_citation_entry_counts_and_primary_refresh_target_card_counts_in_handoff_packs.md` | `topic-note` | `source` | `hashed` | 1095 | `682d82f7216f0a00190f82572738eb3696fd1aa8d946b13b5b727285f7ea598a` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_remaining_primary_verify_and_refresh_target_semantic_counts_in_handoff_packs.md` | `topic-note` | `source` | `hashed` | 934 | `7fa3aa9fdb9b1e0d894f5a5d23c93294d50d62960300868667dbeb8f5c4f6a17` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_target_scale_summaries_in_handoff_packs.md` | `topic-note` | `source` | `hashed` | 1006 | `35f57898829c362b7c917a567b726736b9127a1ecf79599a3f0529d55c633c76` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_commands_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 869 | `4b3244a66be54c2a6fa85c92ae81b9da9678ec9d80b212cadb1ecd00778878a0` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_subject_role_codes_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 851 | `40f6c05db03b9842bf10d25fb691c9acdb7da6e8490a8c527fe5b1a2031540f0` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_intent_summaries_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 863 | `eaa539e1be776b0e4a712e4aa2891272b79da9f26175ba8b043df9c4cfc50ba8` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_outcome_summaries_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 673 | `8e95c8ad1c10fece6e9ebd27e611d59a87ebdc71af4f0a66a296104093810c95` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_effect_codes_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 850 | `a9d1976b8d8523d94ade9f0b84652e9d6ea1351624fdd18e681d5dc6b3d82ffd` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_target_bytes_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 839 | `2a7e736c0d50efbc133eb028d7d792ae4145c18c4e07acaa552f9826466e48b0` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_target_sha256s_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 919 | `863b8601740714f2b9657b43686246f19340864afd35be5be89da42cc495a18d` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_target_citation_entry_counts_and_focus_primary_refresh_target_card_counts_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 1004 | `7fec40d2c4bc0ec98360808b31931c1f618f15c4c3a7b15307586b093e6d6a5c` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_remaining_focus_primary_verify_and_refresh_target_semantic_counts_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 1037 | `b931160b9000cda412344739e5a3f19d9a36d52b4f18e03eb679fb351b79b405` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_target_scale_summaries_for_compact_card_reentry.md` | `topic-note` | `source` | `hashed` | 858 | `f5e0f226beb8332244be381566e7320cbb64e0b40754bed84575dc6727d2c3cb` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_next_command_targets_and_semantics_for_compact_card_next_action_surfaces.md` | `topic-note` | `source` | `hashed` | 905 | `63d08820f31b6377e5caa2ef43748eaba0f6a648aadceda2930c30c965aef06b` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_next_command_target_audit_fields_for_compact_card_next_action_surfaces.md` | `topic-note` | `source` | `hashed` | 1209 | `6953fe11aa13be44eb241f2a7497dc470d8d30e5e8b52be44b23d2098be98b8b` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_next_command_target_semantic_counts_for_compact_card_next_action_surfaces.md` | `topic-note` | `source` | `hashed` | 561 | `a169e448e7b481f52fd6bc510434b7bb7c2a59676934bb51cb18ea8a3d25e3fd` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_fallback_command_targets_and_semantics_for_compact_card_next_action_surfaces.md` | `topic-note` | `source` | `hashed` | 988 | `9f0fb38691cbe04c92aebfc02e3b3ae66b47a7b5b42b3583d2c66d254fff402c` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_fallback_command_target_audit_fields_for_compact_card_next_action_surfaces.md` | `topic-note` | `source` | `hashed` | 1244 | `86f4ade322c326b65e89863f459353ea38afacaaeb6302cdefd2569025605e30` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_fallback_command_target_semantic_counts_for_compact_card_next_action_surfaces.md` | `topic-note` | `source` | `hashed` | 1056 | `0a146cb7f656fe9cc6175d0665678080010e4421bbd2b94b53e45c429cb61d44` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_command_open_paths_for_compact_card_next_action_surfaces.md` | `topic-note` | `source` | `hashed` | 1118 | `aa02a73d12bda1bf184517fca22eaaeb22ff25f264712ebb8a9241504f4325c5` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_role_annotated_selected_command_open_targets_for_compact_card_next_action_surfaces.md` | `topic-note` | `source` | `hashed` | 1201 | `15ad07b81ba8ee837a73f9980b17ae3ecea128ffe51e2628f1222e14dbf2216c` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_wrapper_normalized_compact_card_commands_in_durable_program_docs.md` | `topic-note` | `source` | `hashed` | 1050 | `bcc454ac9f10146432c91388e5aa2c27337a529d92ca3b0b8f407917ed4d8d85` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_preserve_interpreter_continuity_when_compact_card_validators_spawn_builders.md` | `topic-note` | `source` | `hashed` | 1088 | `ccd6230c5d380b337034f9b5b7218d892ad93460144dc478e60d3cd373665c02` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_lineage_grouped_macro_review_queue_for_compact_cards.md` | `topic-note` | `source` | `hashed` | 1100 | `e195bf0b4efe37131c919253cc280ded5754347b6e8f833de911cac8e8446c5e` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_typed_next_action_surface_for_compact_cards.md` | `topic-note` | `source` | `hashed` | 825 | `444e75d72cee91def9f47a5bb48aa59a306b1c83fedc132d85a3f12d979fc942` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_an_arbitration_witness_for_compact_card_next_action_selection.md` | `topic-note` | `source` | `hashed` | 700 | `3f0f40e5afc9e769a60c40ea6abeba6514978b604034f626eb962969f3e42bb3` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_an_execution_lane_surface_for_compact_card_handoffs.md` | `topic-note` | `source` | `hashed` | 1311 | `2b0f1d9527dc1110ea2b6667945049fc362d2cdc45f4ab1d09c406f3df792730` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_taxonomy_registry_for_compact_card_reason_codes_action_kinds_and_execution_lanes.md` | `topic-note` | `source` | `hashed` | 1195 | `c02f1ec01d038905933b41a3a778ace976cb2c8fe46691d83d8c6ab7deb3791d` |
| `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_scope_surface_for_compact_card_subsystem_boundaries.md` | `topic-note` | `source` | `hashed` | 1104 | `a0bbad190a38151e9545720df1c902d5550e56b7691e49fadc55f5e81e62ff14` |

