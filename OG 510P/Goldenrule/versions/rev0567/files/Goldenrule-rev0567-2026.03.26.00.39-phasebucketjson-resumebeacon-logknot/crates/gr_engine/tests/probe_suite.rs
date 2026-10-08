use gr_engine::probe::{
    run_probe_suite, run_probe_suite_with_snapshot, AssertionSpec, ProbeMatchup, ProbeRegistrySpec,
    ProbeSpec, ProbeSuiteSpec,
};
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
        seed: 7,
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
fn run_probe_suite_smoke_and_determinism() {
    let pass_probe = ProbeSpec {
        schema_version: 1,
        id: "pass".to_string(),
        description: "".to_string(),
        world: world(10),
        matchups: vec![ProbeMatchup {
            id: "tft_vs_wsls".to_string(),
            strategy_a: builtin("tft", BuiltinKind::TitForTat),
            strategy_b: builtin("wsls", BuiltinKind::WinStayLoseShift),
            replications: 2,
            seed_offset: 0,
            trace_rounds: 0,
            assertions: vec![],
        }],
    };

    let fail_probe = ProbeSpec {
        schema_version: 1,
        id: "fail".to_string(),
        description: "".to_string(),
        world: world(10),
        matchups: vec![ProbeMatchup {
            id: "always_c_vs_always_d".to_string(),
            strategy_a: builtin("c", BuiltinKind::AlwaysC),
            strategy_b: builtin("d", BuiltinKind::AlwaysD),
            replications: 2,
            seed_offset: 0,
            trace_rounds: 0,
            assertions: vec![AssertionSpec::AvgPayoffAAtLeast { min: 0.1 }],
        }],
    };

    let reg = ProbeRegistrySpec {
        schema_version: 1,
        id: "reg".to_string(),
        description: "".to_string(),
        probes: vec![pass_probe, fail_probe],
    };

    let suite = ProbeSuiteSpec {
        schema_version: 1,
        id: "suite".to_string(),
        description: "".to_string(),
        probe_ids: vec!["pass".to_string(), "fail".to_string()],
    };

    let r1 = run_probe_suite(&reg, &suite).unwrap();
    let r2 = run_probe_suite(&reg, &suite).unwrap();
    assert_eq!(
        serde_json::to_value(r1).unwrap(),
        serde_json::to_value(&r2).unwrap()
    );

    assert_eq!(r2.probe_results.len(), 2);
    assert_eq!(r2.passed, false);
}

#[test]
fn probe_suite_can_embed_snapshot_summary() {
    let probe = ProbeSpec {
        schema_version: 1,
        id: "p1".to_string(),
        description: "".to_string(),
        world: world(5),
        matchups: vec![ProbeMatchup {
            id: "m".to_string(),
            strategy_a: builtin("a", BuiltinKind::AlwaysC),
            strategy_b: builtin("b", BuiltinKind::AlwaysD),
            replications: 1,
            seed_offset: 0,
            trace_rounds: 0,
            assertions: vec![],
        }],
    };

    let reg = ProbeRegistrySpec {
        schema_version: 1,
        id: "reg".to_string(),
        description: "".to_string(),
        probes: vec![probe],
    };

    let suite = ProbeSuiteSpec {
        schema_version: 1,
        id: "suite".to_string(),
        description: "".to_string(),
        probe_ids: vec!["p1".to_string()],
    };
    let snap: SnapshotSpec = serde_json::from_str(r#"{ "schema_version":1, "id":"s" }"#).unwrap();
    let snap_art = build_snapshot(&snap).unwrap();
    let snap_sum = summarize_snapshot(&snap_art);

    let a = run_probe_suite_with_snapshot(&reg, &suite, snap_sum).unwrap();
    assert!(a.snapshot.is_some());
    assert_eq!(a.snapshot.unwrap().snapshot_id, "s");
}
