use gr_engine::probe::{
    expand_probe, validate_probe_registry, validate_probe_suite, ProbeRegistrySpec, ProbeSpec,
    ProbeSuiteSpec,
};

#[test]
fn probe_hash_ignores_json_field_order_and_whitespace() {
    let a = r#"
    {
      "id": "p1",
      "schema_version": 1,
      "description": "test",
      "world": { "id": "w", "seed": 7, "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } }, "noise": { "kind": "none" }, "termination": { "kind": "fixed", "rounds": 5 } },
      "matchups": [
        { "id": "m1", "strategy_a": { "family": "builtin", "id": "a", "kind": "always_c", "params": { "p_cooperate": 1.0 } }, "strategy_b": { "family": "builtin", "id": "b", "kind": "always_d", "params": { "p_cooperate": 0.0 } }, "replications": 2 }
      ]
    }
    "#;

    let b = r#"{ "matchups":[{"replications":2,"strategy_b":{"id":"b","family":"builtin","kind":"always_d","params":{"p_cooperate":0}},"id":"m1","strategy_a":{"params":{"p_cooperate":1},"kind":"always_c","family":"builtin","id":"a"}}], "world":{"termination":{"rounds":5,"kind":"fixed"},"noise":{"kind":"none"},"game":{"payoffs":{"p":1,"t":5,"s":0,"r":3},"kind":"ipd"},"seed":7,"id":"w"}, "description":"test", "id":"p1", "schema_version":1 }"#;

    let probe_a: ProbeSpec = serde_json::from_str(a).unwrap();
    let probe_b: ProbeSpec = serde_json::from_str(b).unwrap();

    let ea = expand_probe(&probe_a).unwrap();
    let eb = expand_probe(&probe_b).unwrap();
    assert_eq!(ea.probe_hash, eb.probe_hash);
    assert_eq!(ea.tasks.len(), eb.tasks.len());
}

#[test]
fn registry_and_suite_validation_smoke() {
    let probe: ProbeSpec = serde_json::from_str(
        r#"
        {
          "id": "p1",
          "world": { "id": "w", "seed": 7, "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } }, "noise": { "kind": "none" }, "termination": { "kind": "fixed", "rounds": 5 } },
          "matchups": [
            { "id": "m1", "strategy_a": { "family": "builtin", "id": "a", "kind": "always_c" }, "strategy_b": { "family": "builtin", "id": "b", "kind": "always_d" } }
          ]
        }
        "#,
    )
    .unwrap();

    let reg = ProbeRegistrySpec {
        schema_version: 1,
        id: "reg1".to_string(),
        description: "".to_string(),
        probes: vec![probe],
    };
    validate_probe_registry(&reg).unwrap();

    let suite = ProbeSuiteSpec {
        schema_version: 1,
        id: "suite1".to_string(),
        description: "".to_string(),
        probe_ids: vec!["p1".to_string()],
    };
    validate_probe_suite(&suite).unwrap();
}

#[test]
fn expand_probe_supports_geometric_and_asymmetric_iid() {
    let probe: ProbeSpec = serde_json::from_str(
        r#"
        {
          "id": "p2",
          "world": {
            "id": "w2",
            "seed": 7,
            "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } },
            "noise": {
              "kind": "asymmetric_iid",
              "p_implementation_a": 0.0,
              "p_implementation_b": 0.1,
              "p_observation_a": 0.2,
              "p_observation_b": 0.0
            },
            "termination": { "kind": "geometric", "delta": 0.9, "max_rounds": 5 }
          },
          "matchups": [
            {
              "id": "m1",
              "strategy_a": { "family": "builtin", "id": "a", "kind": "always_c" },
              "strategy_b": { "family": "builtin", "id": "b", "kind": "always_d" },
              "replications": 2
            }
          ]
        }
        "#,
    )
    .unwrap();

    let expanded = expand_probe(&probe).unwrap();
    assert_eq!(expanded.tasks.len(), 2);
    match expanded.tasks[0].world.noise {
        gr_engine::spec::NoiseModelSpec::AsymmetricIid { .. } => {}
        _ => panic!("expected AsymmetricIid noise in expanded tasks"),
    }
    match expanded.tasks[0].world.termination {
        gr_engine::spec::TerminationRuleSpec::Geometric { .. } => {}
        _ => panic!("expected Geometric termination in expanded tasks"),
    }
}
