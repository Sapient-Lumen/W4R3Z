use gr_engine::metadiff::{
    diff_metamorphic_artifacts, diff_metamorphic_suite_artifacts,
    MetamorphicResultArtifactDiffSpec, MetamorphicSuiteResultArtifactDiffSpec,
};
use gr_engine::metamorphic::{
    run_metamorphic_check, run_metamorphic_suite, MetamorphicCheckSpec, MetamorphicKind,
    MetamorphicRegistrySpec, MetamorphicSuiteSpec,
};
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
fn diff_metamorphic_artifacts_is_unchanged_for_identical_results() {
    let probe = ProbeSpec {
        schema_version: 1,
        id: "p".to_string(),
        description: "".to_string(),
        world: world(10),
        matchups: vec![ProbeMatchup {
            id: "tft_vs_wsls".to_string(),
            strategy_a: builtin("tft", BuiltinKind::TitForTat),
            strategy_b: builtin("wsls", BuiltinKind::WinStayLoseShift),
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

    let a = run_metamorphic_check(&spec).unwrap();
    let b = run_metamorphic_check(&spec).unwrap();
    let diff_spec = MetamorphicResultArtifactDiffSpec {
        schema_version: 1,
        id: "d".to_string(),
        description: "".to_string(),
        a,
        b,
    };
    let out = diff_metamorphic_artifacts(&diff_spec).unwrap();
    assert!(!out.changed);
}

#[test]
fn diff_metamorphic_suite_artifacts_detects_registry_hash_change() {
    let probe = ProbeSpec {
        schema_version: 1,
        id: "p".to_string(),
        description: "".to_string(),
        world: world(5),
        matchups: vec![ProbeMatchup {
            id: "c_vs_d".to_string(),
            strategy_a: builtin("c", BuiltinKind::AlwaysC),
            strategy_b: builtin("d", BuiltinKind::AlwaysD),
            replications: 1,
            seed_offset: 0,
            trace_rounds: 0,
            assertions: vec![],
        }],
    };

    let reg_a = MetamorphicRegistrySpec {
        schema_version: 1,
        id: "reg".to_string(),
        description: "".to_string(),
        checks: vec![MetamorphicCheckSpec {
            schema_version: 1,
            id: "swap".to_string(),
            description: "".to_string(),
            kind: MetamorphicKind::PlayerSwapSymmetry,
            scaling_prefix: None,
            probe: probe.clone(),
        }],
    };
    let reg_b = MetamorphicRegistrySpec {
        schema_version: 1,
        id: "reg".to_string(),
        description: "".to_string(),
        checks: vec![MetamorphicCheckSpec {
            schema_version: 1,
            id: "swap".to_string(),
            description: "changed".to_string(),
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

    let a = run_metamorphic_suite(&reg_a, &suite).unwrap();
    let b = run_metamorphic_suite(&reg_b, &suite).unwrap();

    let diff_spec = MetamorphicSuiteResultArtifactDiffSpec {
        schema_version: 1,
        id: "d".to_string(),
        description: "".to_string(),
        a,
        b,
    };
    let out = diff_metamorphic_suite_artifacts(&diff_spec).unwrap();
    assert!(out.changed);
    assert!(out.registry_hash_changed);
}
