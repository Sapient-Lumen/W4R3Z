use gr_engine::matchdiff::{diff_match_artifacts, MatchArtifactDiffSpec};
use gr_engine::sim::run_match;
use gr_engine::spec::TaskSpec;

#[test]
fn diff_match_artifacts_is_unchanged_for_identical_results() {
    let task: TaskSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "task_id": "t",
          "world": {
            "id": "w",
            "seed": 7,
            "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } },
            "noise": { "kind": "none" },
            "termination": { "kind": "fixed", "rounds": 10 }
          },
          "strategy_a": { "family": "builtin", "id": "tft", "kind": "tit_for_tat" },
          "strategy_b": { "family": "builtin", "id": "tft2", "kind": "tit_for_tat" },
          "match_seed": 123,
          "trace_rounds": 10
        }
        "#,
    )
    .unwrap();

    let a = run_match(&task).unwrap();
    let b = run_match(&task).unwrap();

    let spec = MatchArtifactDiffSpec {
        schema_version: 1,
        id: "d".to_string(),
        description: String::new(),
        a,
        b,
    };

    let d = diff_match_artifacts(&spec).unwrap();
    assert!(!d.changed);
    assert!(!d.stats_changed);
    assert!(!d.trace_changed);
}

#[test]
fn diff_match_artifacts_detects_first_trace_difference() {
    let task: TaskSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "task_id": "t",
          "world": {
            "id": "w",
            "seed": 7,
            "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } },
            "noise": { "kind": "none" },
            "termination": { "kind": "fixed", "rounds": 10 }
          },
          "strategy_a": { "family": "builtin", "id": "tft", "kind": "tit_for_tat" },
          "strategy_b": { "family": "builtin", "id": "tft2", "kind": "tit_for_tat" },
          "match_seed": 123,
          "trace_rounds": 10
        }
        "#,
    )
    .unwrap();

    let a = run_match(&task).unwrap();
    let mut b = a.clone();
    b.trace.as_mut().unwrap()[3].a_executed = gr_engine::spec::Action::D;

    let spec = MatchArtifactDiffSpec {
        schema_version: 1,
        id: "d".to_string(),
        description: String::new(),
        a,
        b,
    };

    let d = diff_match_artifacts(&spec).unwrap();
    assert!(d.changed);
    assert!(d.trace_changed);
    assert_eq!(d.first_diff_round, Some(3));
}
