use gr_engine::metamorphic::{run_metamorphic_check, MetamorphicCheckSpec, MetamorphicKind};
use gr_engine::probe::{ProbeMatchup, ProbeSpec};
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

fn builtin(id: &str, kind: BuiltinKind) -> StrategySpec {
    StrategySpec::Builtin {
        id: id.to_string(),
        kind,
        params: BuiltinParams::default(),
    }
}

#[test]
fn metamorphic_player_swap_symmetry_passes_for_deterministic_matchups() {
    let probe = ProbeSpec {
        schema_version: 1,
        id: "p".to_string(),
        description: "".to_string(),
        world: world(20),
        matchups: vec![ProbeMatchup {
            id: "tft_vs_wsls".to_string(),
            strategy_a: builtin("tft", BuiltinKind::TitForTat),
            strategy_b: builtin("wsls", BuiltinKind::WinStayLoseShift),
            replications: 3,
            seed_offset: 0,
            trace_rounds: 0,
            assertions: vec![],
        }],
    };

    let spec = MetamorphicCheckSpec {
        schema_version: 1,
        id: "m".to_string(),
        description: "".to_string(),
        kind: MetamorphicKind::PlayerSwapSymmetry,
        scaling_prefix: None,
        probe,
    };

    let r1 = run_metamorphic_check(&spec).unwrap();
    assert!(r1.failures.is_empty());
    assert!(r1.skipped.is_empty());
    assert!(r1.passed);

    let r2 = run_metamorphic_check(&spec).unwrap();
    assert_eq!(
        serde_json::to_value(r1).unwrap(),
        serde_json::to_value(r2).unwrap()
    );
}

#[test]
fn metamorphic_player_swap_symmetry_marks_ineligible_matchups_as_skipped() {
    let probe = ProbeSpec {
        schema_version: 1,
        id: "p".to_string(),
        description: "".to_string(),
        world: WorldSpec {
            noise: NoiseModelSpec::ImplementationFlip { p: 0.1 },
            ..world(10)
        },
        matchups: vec![ProbeMatchup {
            id: "always_c_vs_always_d".to_string(),
            strategy_a: builtin("c", BuiltinKind::AlwaysC),
            strategy_b: builtin("d", BuiltinKind::AlwaysD),
            replications: 1,
            seed_offset: 0,
            trace_rounds: 0,
            assertions: vec![],
        }],
    };

    let spec = MetamorphicCheckSpec {
        schema_version: 1,
        id: "m".to_string(),
        description: "".to_string(),
        kind: MetamorphicKind::PlayerSwapSymmetry,
        scaling_prefix: None,
        probe,
    };

    let r = run_metamorphic_check(&spec).unwrap();
    assert!(r.failures.is_empty());
    assert!(!r.skipped.is_empty());
    assert!(!r.passed);
}

#[test]
fn metamorphic_scaling_prefix_stability_passes_for_same_seed_prefix() {
    let probe = ProbeSpec {
        schema_version: 1,
        id: "p".to_string(),
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
            replications: 3,
            seed_offset: 0,
            trace_rounds: 0,
            assertions: vec![],
        }],
    };

    let spec = MetamorphicCheckSpec {
        schema_version: 1,
        id: "scale".to_string(),
        description: "".to_string(),
        kind: MetamorphicKind::ScalingPrefixStability,
        scaling_prefix: Some(gr_engine::metamorphic::ScalingPrefixConfig {
            base_rounds: 10,
            extended_rounds: 25,
        }),
        probe,
    };

    let r = run_metamorphic_check(&spec).unwrap();
    assert!(r.passed);
    assert!(r.failures.is_empty());
    assert_eq!(r.skipped_matchups, 0);
    assert_eq!(r.eligible_pairs, 3);
}
