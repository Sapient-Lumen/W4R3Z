use gr_engine::run_snapshot::run_snapshot;
use gr_engine::snapshot::SnapshotSpec;
use gr_engine::snapshotrun_diff::{diff_snapshot_run_artifacts, SnapshotRunArtifactDiffSpec};

#[test]
fn snapshot_run_diff_is_unchanged_when_equal() {
    let spec: SnapshotSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "id": "s",
          "probe_registry": {
            "schema_version": 1,
            "id": "reg",
            "probes": [
              {
                "schema_version": 1,
                "id": "p1",
                "world": {
                  "id": "w",
                  "seed": 7,
                  "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } },
                  "noise": { "kind": "none" },
                  "termination": { "kind": "fixed", "rounds": 5 }
                },
                "matchups": [
                  {
                    "id": "m",
                    "strategy_a": { "family": "builtin", "id": "c", "kind": "always_c" },
                    "strategy_b": { "family": "builtin", "id": "d", "kind": "always_d" },
                    "replications": 1,
                    "assertions": []
                  }
                ]
              }
            ]
          },
          "probe_suite": { "schema_version": 1, "id": "suite", "probe_ids": ["p1"] }
        }
        "#,
    )
    .unwrap();

    let a = run_snapshot(&spec).unwrap();
    let b = run_snapshot(&spec).unwrap();

    let diff_spec = SnapshotRunArtifactDiffSpec {
        schema_version: 1,
        id: "d".to_string(),
        description: String::new(),
        a,
        b,
    };

    let d = diff_snapshot_run_artifacts(&diff_spec).unwrap();
    assert!(!d.changed);
    assert!(!d.passed_changed);
    assert!(!d.snapshot_changed);
    assert!(!d.probe_suite_changed);
    assert!(!d.metamorphic_suite_changed);
    assert!(!d.scorecard_changed);
    assert!(!d.scorecard_suite_changed);
    assert!(d.snapshot_diff.is_some());
    assert!(!d.snapshot_diff.unwrap().changed);
    assert!(d.probe_suite_diff.is_some());
}

#[test]
fn snapshot_run_diff_detects_scorecard_suite_drift() {
    let spec: SnapshotSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "id": "s",
          "probe_registry": {
            "schema_version": 1,
            "id": "reg",
            "probes": [
              {
                "schema_version": 1,
                "id": "p1",
                "world": {
                  "id": "w",
                  "seed": 7,
                  "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } },
                  "noise": { "kind": "none" },
                  "termination": { "kind": "fixed", "rounds": 5 }
                },
                "matchups": [
                  {
                    "id": "m",
                    "strategy_a": { "family": "builtin", "id": "tft", "kind": "tit_for_tat" },
                    "strategy_b": { "family": "builtin", "id": "tft2", "kind": "tit_for_tat" },
                    "replications": 1,
                    "assertions": [ { "kind": "mutual_coop_rate_at_least", "min": 1.0 } ]
                  }
                ]
              }
            ]
          },
          "probe_suite": { "schema_version": 1, "id": "suite", "probe_ids": ["p1"] },
          "scorecard_registry": {
            "schema_version": 1,
            "id": "sreg",
            "scorecards": [
              {
                "schema_version": 1,
                "id": "sc",
                "card": { "id": "card", "version": "v1", "intent": "smoke" },
                "gates": { "require_probe_suite": true, "require_metamorphic_suite": false, "fail_on_hash_mismatch": true }
              }
            ]
          },
          "scorecard_suite": { "schema_version": 1, "id": "ssuite", "scorecard_ids": ["sc"] }
        }
        "#,
    )
    .unwrap();

    let a = run_snapshot(&spec).unwrap();
    let mut b = a.clone();

    let new_suite_passed = !b.scorecard_suite.as_ref().unwrap().passed;
    b.scorecard_suite.as_mut().unwrap().passed = new_suite_passed;
    b.passed = new_suite_passed;

    let diff_spec = SnapshotRunArtifactDiffSpec {
        schema_version: 1,
        id: "d".to_string(),
        description: String::new(),
        a,
        b,
    };

    let d = diff_snapshot_run_artifacts(&diff_spec).unwrap();
    assert!(d.changed);
    assert!(d.passed_changed);
    assert!(!d.snapshot_changed);
    assert!(!d.probe_suite_changed);
    assert!(d.scorecard_suite_changed);
    assert!(d.scorecard_suite_diff.is_some());
    assert!(d.scorecard_suite_diff.unwrap().changed);
}
