use gr_engine::shrink::{
    shrink_probe_pipeline, shrink_probe_rounds, ShrinkProbePipelineSpec, ShrinkProbeRoundsSpec,
};

#[test]
fn shrink_probe_rounds_finds_smaller_counterexample() {
    let spec: ShrinkProbeRoundsSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "id": "shrink",
          "max_scan_rounds": 30,
          "probe": {
            "schema_version": 1,
            "id": "p",
            "world": {
              "id": "w",
              "seed": 7,
              "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } },
              "noise": { "kind": "none" },
              "termination": { "kind": "fixed", "rounds": 20 }
            },
            "matchups": [
              {
                "id": "c_vs_d",
                "strategy_a": { "family": "builtin", "id": "c", "kind": "always_c" },
                "strategy_b": { "family": "builtin", "id": "d", "kind": "always_d" },
                "replications": 2,
                "assertions": [ { "kind": "avg_payoff_a_at_least", "min": 0.1 } ]
              }
            ]
          }
        }
        "#,
    )
    .unwrap();

    let out = shrink_probe_rounds(&spec).unwrap();
    assert!(!out.original_result.passed);
    assert!(!out.shrunk_result.passed);
    assert!(out.shrunk_rounds <= out.original_rounds);
    assert!(out.shrunk_rounds >= 1);
}

#[test]
fn shrink_probe_rounds_supports_geometric_delta_1_by_shrinking_max_rounds() {
    let spec: ShrinkProbeRoundsSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "id": "shrink_geo",
          "max_scan_rounds": 30,
          "probe": {
            "schema_version": 1,
            "id": "p",
            "world": {
              "id": "w",
              "seed": 7,
              "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } },
              "noise": { "kind": "none" },
              "termination": { "kind": "geometric", "delta": 1.0, "max_rounds": 20 }
            },
            "matchups": [
              {
                "id": "c_vs_d",
                "strategy_a": { "family": "builtin", "id": "c", "kind": "always_c" },
                "strategy_b": { "family": "builtin", "id": "d", "kind": "always_d" },
                "replications": 2,
                "assertions": [ { "kind": "avg_payoff_a_at_least", "min": 0.1 } ]
              }
            ]
          }
        }
        "#,
    )
    .unwrap();

    let out = shrink_probe_rounds(&spec).unwrap();
    assert!(!out.original_result.passed);
    assert!(!out.shrunk_result.passed);
    assert!(out.shrunk_rounds <= out.original_rounds);
    assert!(out.shrunk_rounds >= 1);
    match out.shrunk_probe.world.termination {
        gr_engine::spec::TerminationRuleSpec::Geometric { delta, max_rounds } => {
            assert_eq!(delta, 1.0);
            assert_eq!(max_rounds, out.shrunk_rounds);
        }
        gr_engine::spec::TerminationRuleSpec::Fixed { .. } => {
            panic!("expected shrinker to preserve geometric termination")
        }
    }
}

#[test]
fn shrink_probe_rounds_supports_geometric_delta_non_1_by_shrinking_max_rounds() {
    let spec: ShrinkProbeRoundsSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "id": "shrink_geo_non1",
          "max_scan_rounds": 30,
          "probe": {
            "schema_version": 1,
            "id": "p",
            "world": {
              "id": "w",
              "seed": 7,
              "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } },
              "noise": { "kind": "none" },
              "termination": { "kind": "geometric", "delta": 0.5, "max_rounds": 20 }
            },
            "matchups": [
              {
                "id": "c_vs_d",
                "strategy_a": { "family": "builtin", "id": "c", "kind": "always_c" },
                "strategy_b": { "family": "builtin", "id": "d", "kind": "always_d" },
                "replications": 2,
                "assertions": [ { "kind": "avg_payoff_a_at_least", "min": 0.1 } ]
              }
            ]
          }
        }
        "#,
    )
    .unwrap();

    let out = shrink_probe_rounds(&spec).unwrap();
    assert!(!out.original_result.passed);
    assert!(!out.shrunk_result.passed);
    assert!(out.shrunk_rounds <= out.original_rounds);
    assert!(out.shrunk_rounds >= 1);
    match out.shrunk_probe.world.termination {
        gr_engine::spec::TerminationRuleSpec::Geometric { delta, max_rounds } => {
            assert_eq!(delta, 0.5);
            assert_eq!(max_rounds, out.shrunk_rounds);
        }
        gr_engine::spec::TerminationRuleSpec::Fixed { .. } => {
            panic!("expected shrinker to preserve geometric termination")
        }
    }
}

#[test]
fn shrink_probe_matchups_keeps_only_failing_matchup() {
    let spec: gr_engine::shrink::ShrinkProbeMatchupsSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "id": "shrink_matchups",
          "probe": {
            "schema_version": 1,
            "id": "p",
            "world": {
              "id": "w",
              "seed": 7,
              "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } },
              "noise": { "kind": "none" },
              "termination": { "kind": "fixed", "rounds": 10 }
            },
            "matchups": [
              {
                "id": "pass",
                "strategy_a": { "family": "builtin", "id": "tft", "kind": "tit_for_tat" },
                "strategy_b": { "family": "builtin", "id": "tft2", "kind": "tit_for_tat" },
                "replications": 1,
                "assertions": [ { "kind": "mutual_coop_rate_at_least", "min": 1.0 } ]
              },
              {
                "id": "fail",
                "strategy_a": { "family": "builtin", "id": "c", "kind": "always_c" },
                "strategy_b": { "family": "builtin", "id": "d", "kind": "always_d" },
                "replications": 1,
                "assertions": [ { "kind": "avg_payoff_a_at_least", "min": 0.1 } ]
              }
            ]
          }
        }
        "#,
    )
    .unwrap();

    let out = gr_engine::shrink::shrink_probe_matchups(&spec).unwrap();
    assert!(!out.original_result.passed);
    assert!(!out.shrunk_result.passed);
    assert_eq!(out.shrunk_probe.matchups.len(), 1);
    assert_eq!(out.kept_matchup_ids, vec!["fail".to_string()]);
    assert_eq!(out.removed_matchup_ids, vec!["pass".to_string()]);
}

#[test]
fn shrink_probe_replications_finds_smaller_counterexample() {
    let spec: gr_engine::shrink::ShrinkProbeReplicationsSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "id": "shrink_reps",
          "max_scan_replications": 10,
          "probe": {
            "schema_version": 1,
            "id": "p",
            "world": {
              "id": "w",
              "seed": 7,
              "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } },
              "noise": { "kind": "none" },
              "termination": { "kind": "fixed", "rounds": 10 }
            },
            "matchups": [
              {
                "id": "fail",
                "strategy_a": { "family": "builtin", "id": "c", "kind": "always_c" },
                "strategy_b": { "family": "builtin", "id": "d", "kind": "always_d" },
                "replications": 5,
                "assertions": [ { "kind": "avg_payoff_a_at_least", "min": 0.1 } ]
              }
            ]
          }
        }
        "#,
    )
    .unwrap();

    let out = gr_engine::shrink::shrink_probe_replications(&spec).unwrap();
    assert!(!out.original_result.passed);
    assert!(!out.shrunk_result.passed);
    assert_eq!(out.original_replications, 5);
    assert_eq!(out.shrunk_replications, 1);
}

#[test]
fn shrink_probe_pipeline_composes_matchups_rounds_and_replications() {
    let spec: ShrinkProbePipelineSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "id": "shrink_pipeline",
          "max_scan_rounds": 30,
          "max_scan_replications": 10,
          "probe": {
            "schema_version": 1,
            "id": "p",
            "world": {
              "id": "w",
              "seed": 7,
              "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } },
              "noise": { "kind": "none" },
              "termination": { "kind": "fixed", "rounds": 20 }
            },
            "matchups": [
              {
                "id": "pass",
                "strategy_a": { "family": "builtin", "id": "tft", "kind": "tit_for_tat" },
                "strategy_b": { "family": "builtin", "id": "tft2", "kind": "tit_for_tat" },
                "replications": 3,
                "assertions": [ { "kind": "mutual_coop_rate_at_least", "min": 1.0 } ]
              },
              {
                "id": "fail",
                "strategy_a": { "family": "builtin", "id": "c", "kind": "always_c" },
                "strategy_b": { "family": "builtin", "id": "d", "kind": "always_d" },
                "replications": 5,
                "assertions": [ { "kind": "avg_payoff_a_at_least", "min": 0.1 } ]
              }
            ]
          }
        }
        "#,
    )
    .unwrap();

    let out = shrink_probe_pipeline(&spec).unwrap();
    assert!(!out.original_result.passed);
    assert!(!out.final_result.passed);
    assert_eq!(out.final_probe.matchups.len(), 1);
    assert_eq!(out.final_probe.matchups[0].id, "fail");
    assert_eq!(out.final_probe.matchups[0].replications, 1);
    match out.final_probe.world.termination {
        gr_engine::spec::TerminationRuleSpec::Fixed { rounds } => assert_eq!(rounds, 1),
        gr_engine::spec::TerminationRuleSpec::Geometric { .. } => {
            panic!("shrink pipeline should not produce geometric termination")
        }
    }
}
