use gr_engine::sim::run_match;
use gr_engine::spec::{
    BuiltinKind, BuiltinParams, GameSpec, NoiseModelSpec, Payoffs, ReputationModelSpec,
    StrategySpec, TaskSpec, TerminationRuleSpec, WorldSpec,
};
use proptest::prelude::*;

fn deterministic_builtin_kind() -> impl Strategy<Value = BuiltinKind> {
    prop_oneof![
        Just(BuiltinKind::AlwaysC),
        Just(BuiltinKind::AlwaysD),
        Just(BuiltinKind::TitForTat),
        Just(BuiltinKind::WinStayLoseShift),
    ]
}

fn world_no_noise(rounds: u32) -> WorldSpec {
    WorldSpec {
        id: "ipd".to_string(),
        game: GameSpec::Ipd {
            payoffs: Payoffs::default(),
        },
        noise: NoiseModelSpec::None,
        termination: TerminationRuleSpec::Fixed { rounds },
        reputation: ReputationModelSpec::None,
        seed: 123,
    }
}

proptest! {
    #[test]
    fn determinism_same_task_same_output(
        match_seed in any::<u64>(),
        rounds in 1u32..200u32,
        kind_a in deterministic_builtin_kind(),
        kind_b in deterministic_builtin_kind(),
    ) {
        let task = TaskSpec::new(
            "pbt",
            world_no_noise(rounds),
            StrategySpec::Builtin {
                id: "a".to_string(),
                kind: kind_a,
                params: BuiltinParams::default(),
            },
            StrategySpec::Builtin {
                id: "b".to_string(),
                kind: kind_b,
                params: BuiltinParams::default(),
            },
            match_seed,
        );

        let a1 = run_match(&task).unwrap();
        let a2 = run_match(&task).unwrap();
        prop_assert_eq!(serde_json::to_value(a1).unwrap(), serde_json::to_value(a2).unwrap());
    }

    #[test]
    fn swapping_players_swaps_totals_for_deterministic_strategies_no_noise(
        match_seed in any::<u64>(),
        rounds in 1u32..200u32,
        kind_a in deterministic_builtin_kind(),
        kind_b in deterministic_builtin_kind(),
    ) {
        let world = world_no_noise(rounds);
        let a = StrategySpec::Builtin {
            id: "a".to_string(),
            kind: kind_a,
            params: BuiltinParams::default(),
        };
        let b = StrategySpec::Builtin {
            id: "b".to_string(),
            kind: kind_b,
            params: BuiltinParams::default(),
        };

        let task_ab = TaskSpec::new("ab", world.clone(), a.clone(), b.clone(), match_seed);
        let task_ba = TaskSpec::new("ba", world, b, a, match_seed);

        let ab = run_match(&task_ab).unwrap();
        let ba = run_match(&task_ba).unwrap();

        prop_assert!((ab.stats.total_payoff_a - ba.stats.total_payoff_b).abs() < 1e-9);
        prop_assert!((ab.stats.total_payoff_b - ba.stats.total_payoff_a).abs() < 1e-9);
        prop_assert!(ab.stats.total_payoff_a.is_finite());
        prop_assert!(ab.stats.total_payoff_b.is_finite());
    }
}
