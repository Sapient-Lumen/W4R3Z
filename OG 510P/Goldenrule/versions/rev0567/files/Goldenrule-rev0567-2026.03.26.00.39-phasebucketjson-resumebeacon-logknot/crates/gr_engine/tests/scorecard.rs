use gr_engine::run_snapshot::run_snapshot;
use gr_engine::scorecard::{run_scorecard, ScorecardCard, ScorecardGateSpec, ScorecardSpec};
use gr_engine::snapshot::SnapshotSpec;

#[test]
fn scorecard_smoke_from_snapshot_run() {
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
          "probe_suite": { "schema_version": 1, "id": "suite", "probe_ids": ["p1"] },
          "metamorphic_registry": {
            "schema_version": 1,
            "id": "mreg",
            "checks": [
              {
                "schema_version": 1,
                "id": "swap",
                "kind": "player_swap_symmetry",
                "probe": {
                  "schema_version": 1,
                  "id": "mp",
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
              }
            ]
          },
          "metamorphic_suite": { "schema_version": 1, "id": "msuite", "check_ids": ["swap"] }
        }
        "#,
    )
    .unwrap();

    let run = run_snapshot(&snap).unwrap();

    let spec = ScorecardSpec {
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
            require_metamorphic_suite: true,
            fail_on_hash_mismatch: true,
        },
        snapshot: None,
        snapshot_run: Some(run),
        probe_suite: None,
        metamorphic_suite: None,
    };

    let out = run_scorecard(&spec).unwrap();
    assert!(out.passed);
    assert!(out.banner.passed);
    assert_eq!(out.banner.probes_failed, 0);
    assert_eq!(out.banner.checks_failed, 0);
    assert!(out.warnings.is_empty());
    assert!(out.snapshot.is_some());
}
