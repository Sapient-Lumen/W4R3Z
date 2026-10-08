use gr_engine::run_snapshot::run_snapshot;
use gr_engine::scorecard::{ScorecardCard, ScorecardDef, ScorecardGateSpec};
use gr_engine::scorecard_suite::{run_scorecard_suite, ScorecardRegistrySpec, ScorecardSuiteSpec};
use gr_engine::snapshot::SnapshotSpec;

#[test]
fn scorecard_suite_smoke_and_determinism() {
    let snap: SnapshotSpec = serde_json::from_str(
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
          "probe_suite": { "schema_version": 1, "id": "suite", "probe_ids": ["p1"] }
        }
        "#,
    )
    .unwrap();
    let run = run_snapshot(&snap).unwrap();

    let def = ScorecardDef {
        schema_version: 1,
        id: "sc".to_string(),
        description: "".to_string(),
        card: ScorecardCard {
            id: "card".to_string(),
            version: "v1".to_string(),
            intent: "smoke".to_string(),
            non_goals: vec![],
            lenses: vec![],
            known_risks: vec![],
            required_holdouts: vec![],
            required_metamorphic: vec![],
            appropriate_contexts: vec![],
            inappropriate_contexts: vec![],
            changelog: vec![],
        },
        gates: ScorecardGateSpec {
            require_probe_suite: true,
            require_metamorphic_suite: false,
            fail_on_hash_mismatch: true,
        },
    };

    let reg = ScorecardRegistrySpec {
        schema_version: 1,
        id: "reg".to_string(),
        description: "".to_string(),
        scorecards: vec![def],
    };
    let suite = ScorecardSuiteSpec {
        schema_version: 1,
        id: "suite".to_string(),
        description: "".to_string(),
        scorecard_ids: vec!["sc".to_string()],
    };

    let a = run_scorecard_suite(&reg, &suite, &run).unwrap();
    let b = run_scorecard_suite(&reg, &suite, &run).unwrap();
    assert_eq!(
        serde_json::to_value(a).unwrap(),
        serde_json::to_value(b).unwrap()
    );
}
