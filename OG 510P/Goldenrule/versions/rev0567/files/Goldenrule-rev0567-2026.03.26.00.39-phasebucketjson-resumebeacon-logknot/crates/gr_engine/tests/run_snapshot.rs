use gr_engine::run_snapshot::run_snapshot;
use gr_engine::snapshot::SnapshotSpec;

#[test]
fn run_snapshot_is_deterministic() {
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

    let r1 = run_snapshot(&spec).unwrap();
    let r2 = run_snapshot(&spec).unwrap();
    assert_eq!(
        serde_json::to_value(r1).unwrap(),
        serde_json::to_value(r2).unwrap()
    );
}

#[test]
fn run_snapshot_requires_registry_and_suite_pairing() {
    let spec: SnapshotSpec =
        serde_json::from_str(r#"{ "schema_version": 1, "id": "s", "probe_suite": { "schema_version":1, "id":"suite", "probe_ids":["p1"] } }"#).unwrap();
    let err = run_snapshot(&spec).unwrap_err().to_string();
    assert!(err.contains("probe_suite requires probe_registry"));
}

#[test]
fn run_snapshot_can_run_scorecard_suite_when_embedded() {
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

    let r = run_snapshot(&spec).unwrap();
    assert!(r.scorecard_suite.is_some());
    assert!(r.scorecard_suite.unwrap().passed);
}
