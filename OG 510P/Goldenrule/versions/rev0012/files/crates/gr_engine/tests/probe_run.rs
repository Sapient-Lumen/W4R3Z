use gr_engine::probe::{run_probe, AssertionSpec, ProbeMatchup, ProbeSpec};
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
fn run_probe_is_deterministic() {
    let probe = ProbeSpec {
        schema_version: 1,
        id: "p".to_string(),
        description: "".to_string(),
        world: world(10),
        matchups: vec![ProbeMatchup {
            id: "m".to_string(),
            strategy_a: builtin("a", BuiltinKind::TitForTat),
            strategy_b: builtin("b", BuiltinKind::WinStayLoseShift),
            replications: 3,
            seed_offset: 0,
            trace_rounds: 0,
            assertions: vec![],
        }],
    };

    let r1 = run_probe(&probe).unwrap();
    let r2 = run_probe(&probe).unwrap();
    assert_eq!(
        serde_json::to_value(r1).unwrap(),
        serde_json::to_value(r2).unwrap()
    );
}

#[test]
fn probe_matchup_reports_rounds_summary_under_geometric_termination() {
    let probe: gr_engine::probe::ProbeSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "id": "p_geo",
          "world": {
            "id": "w",
            "seed": 7,
            "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } },
            "noise": { "kind": "none" },
            "termination": { "kind": "geometric", "delta": 0.5, "max_rounds": 25 }
          },
          "matchups": [
            {
              "id": "c_vs_d",
              "strategy_a": { "family": "builtin", "id": "c", "kind": "always_c" },
              "strategy_b": { "family": "builtin", "id": "d", "kind": "always_d" },
              "replications": 5,
              "assertions": [ { "kind": "avg_payoff_a_at_least", "min": 0.1 } ]
            }
          ]
        }
        "#,
    )
    .unwrap();

    let out = gr_engine::probe::run_probe(&probe).unwrap();
    assert_eq!(out.matchups.len(), 1);
    let m = &out.matchups[0];
    assert_eq!(m.replications, 5);
    let minr = m.rounds_min.expect("rounds_min");
    let maxr = m.rounds_max.expect("rounds_max");
    let meanr = m.rounds_mean.expect("rounds_mean");
    assert!(minr >= 1);
    assert!(maxr >= minr);
    assert!(meanr >= minr as f64);
    assert!(meanr <= maxr as f64);
    assert_eq!(m.rounds_per_replication, maxr);
}

#[test]
fn run_probe_reports_assertion_failures() {
    let probe = ProbeSpec {
        schema_version: 1,
        id: "p".to_string(),
        description: "".to_string(),
        world: world(5),
        matchups: vec![ProbeMatchup {
            id: "c_vs_d".to_string(),
            strategy_a: builtin("always_c", BuiltinKind::AlwaysC),
            strategy_b: builtin("always_d", BuiltinKind::AlwaysD),
            replications: 2,
            seed_offset: 0,
            trace_rounds: 0,
            assertions: vec![
                AssertionSpec::AvgPayoffAAtLeast { min: 0.1 },
                AssertionSpec::AvgPayoffBAtLeast { min: 4.9 },
            ],
        }],
    };

    let result = run_probe(&probe).unwrap();
    assert!(!result.passed);
    assert_eq!(result.matchups.len(), 1);
    let m = &result.matchups[0];
    assert!(!m.passed);
    assert_eq!(m.assertions.len(), 2);
    assert_eq!(m.assertions[0].passed, false);
    assert_eq!(m.assertions[1].passed, true);
}
