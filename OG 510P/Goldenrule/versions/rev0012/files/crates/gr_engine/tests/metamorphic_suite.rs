use gr_engine::metamorphic::{
    run_metamorphic_suite, run_metamorphic_suite_with_snapshot, MetamorphicCheckSpec,
    MetamorphicKind, MetamorphicRegistrySpec, MetamorphicSuiteSpec, ScalingPrefixConfig,
};
use gr_engine::probe::{ProbeMatchup, ProbeSpec};
use gr_engine::snapshot::{build_snapshot, summarize_snapshot, SnapshotSpec};
use gr_engine::spec::{
    BuiltinKind, BuiltinParams, GameSpec, NoiseModelSpec, Payoffs, ReputationModelSpec,
    StrategySpec, TerminationRuleSpec, WorldSpec,
};

fn world(rounds: u32) -> WorldSpec {
    WorldSpec {
        id: "w".to_string(),
        game: GameSpec::Ipd {
            payoffs: Payoffs::default(),
        },
        noise: NoiseModelSpec::None,
        termination: TerminationRuleSpec::Fixed { rounds },
        reputation: ReputationModelSpec::None,
        seed: 123,
    }
}

#[test]
fn run_metamorphic_suite_smoke_and_determinism() {
    let probe_swap = ProbeSpec {
        schema_version: 1,
        id: "p_swap".to_string(),
        description: "".to_string(),
        world: world(20),
        matchups: vec![ProbeMatchup {
            id: "tft_vs_wsls".to_string(),
            strategy_a: StrategySpec::Builtin {
                id: "tft".to_string(),
                kind: BuiltinKind::TitForTat,
                params: BuiltinParams::default(),
            },
            strategy_b: StrategySpec::Builtin {
                id: "wsls".to_string(),
                kind: BuiltinKind::WinStayLoseShift,
                params: BuiltinParams::default(),
            },
            replications: 2,
            seed_offset: 0,
            trace_rounds: 0,
            assertions: vec![],
        }],
    };

    let probe_scale = ProbeSpec {
        schema_version: 1,
        id: "p_scale".to_string(),
        description: "".to_string(),
        world: WorldSpec {
            noise: NoiseModelSpec::Iid {
                p_implementation: 0.2,
                p_observation: 0.1,
            },
            ..world(10)
        },
        matchups: vec![ProbeMatchup {
            id: "rand_vs_mem1".to_string(),
            strategy_a: StrategySpec::Builtin {
                id: "rand".to_string(),
                kind: BuiltinKind::Random,
                params: BuiltinParams { p_cooperate: 0.42 },
            },
            strategy_b: StrategySpec::MemoryOne {
                id: "m1".to_string(),
                p0: 0.9,
                p_cc: 0.9,
                p_cd: 0.1,
                p_dc: 0.8,
                p_dd: 0.2,
            },
            replications: 2,
            seed_offset: 0,
            trace_rounds: 0,
            assertions: vec![],
        }],
    };

    let reg = MetamorphicRegistrySpec {
        schema_version: 1,
        id: "reg".to_string(),
        description: "".to_string(),
        checks: vec![
            MetamorphicCheckSpec {
                schema_version: 1,
                id: "swap".to_string(),
                description: "".to_string(),
                kind: MetamorphicKind::PlayerSwapSymmetry,
                scaling_prefix: None,
                probe: probe_swap,
            },
            MetamorphicCheckSpec {
                schema_version: 1,
                id: "scale".to_string(),
                description: "".to_string(),
                kind: MetamorphicKind::ScalingPrefixStability,
                scaling_prefix: Some(ScalingPrefixConfig {
                    base_rounds: 10,
                    extended_rounds: 30,
                }),
                probe: probe_scale,
            },
        ],
    };

    let suite = MetamorphicSuiteSpec {
        schema_version: 1,
        id: "suite".to_string(),
        description: "".to_string(),
        check_ids: vec!["swap".to_string(), "scale".to_string()],
    };

    let r1 = run_metamorphic_suite(&reg, &suite).unwrap();
    let r2 = run_metamorphic_suite(&reg, &suite).unwrap();
    assert_eq!(
        serde_json::to_value(r1).unwrap(),
        serde_json::to_value(&r2).unwrap()
    );

    assert!(r2.passed);
    assert_eq!(r2.check_results.len(), 2);
}

#[test]
fn metamorphic_suite_can_embed_snapshot_summary() {
    let probe = ProbeSpec {
        schema_version: 1,
        id: "p".to_string(),
        description: "".to_string(),
        world: world(10),
        matchups: vec![ProbeMatchup {
            id: "tft_vs_wsls".to_string(),
            strategy_a: StrategySpec::Builtin {
                id: "tft".to_string(),
                kind: BuiltinKind::TitForTat,
                params: BuiltinParams::default(),
            },
            strategy_b: StrategySpec::Builtin {
                id: "wsls".to_string(),
                kind: BuiltinKind::WinStayLoseShift,
                params: BuiltinParams::default(),
            },
            replications: 1,
            seed_offset: 0,
            trace_rounds: 0,
            assertions: vec![],
        }],
    };

    let reg = MetamorphicRegistrySpec {
        schema_version: 1,
        id: "reg".to_string(),
        description: "".to_string(),
        checks: vec![MetamorphicCheckSpec {
            schema_version: 1,
            id: "swap".to_string(),
            description: "".to_string(),
            kind: MetamorphicKind::PlayerSwapSymmetry,
            scaling_prefix: None,
            probe,
        }],
    };

    let suite = MetamorphicSuiteSpec {
        schema_version: 1,
        id: "suite".to_string(),
        description: "".to_string(),
        check_ids: vec!["swap".to_string()],
    };

    let snap: SnapshotSpec = serde_json::from_str(r#"{ "schema_version":1, "id":"s" }"#).unwrap();
    let snap_art = build_snapshot(&snap).unwrap();
    let snap_sum = summarize_snapshot(&snap_art);

    let out = run_metamorphic_suite_with_snapshot(&reg, &suite, snap_sum).unwrap();
    assert!(out.snapshot.is_some());
    assert_eq!(out.snapshot.unwrap().snapshot_id, "s");
}
