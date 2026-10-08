use gr_engine::probe::{run_probe, run_probe_suite, ProbeRegistrySpec, ProbeSpec, ProbeSuiteSpec};
use gr_engine::probediff::{
    diff_probe_artifacts, diff_probe_suite_artifacts, ProbeResultArtifactDiffSpec,
    ProbeSuiteResultArtifactDiffSpec,
};

#[test]
fn diff_probe_artifacts_is_unchanged_for_identical_results() {
    let probe: ProbeSpec = serde_json::from_str(
        r#"
        {
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
              "id": "tft_vs_tft",
              "strategy_a": { "family": "builtin", "id": "tft", "kind": "tit_for_tat" },
              "strategy_b": { "family": "builtin", "id": "tft2", "kind": "tit_for_tat" },
              "replications": 2,
              "assertions": [ { "kind": "mutual_coop_rate_at_least", "min": 1.0 } ]
            }
          ]
        }
        "#,
    )
    .unwrap();

    let a = run_probe(&probe).unwrap();
    let b = run_probe(&probe).unwrap();

    let spec = ProbeResultArtifactDiffSpec {
        schema_version: 1,
        id: "diff".to_string(),
        description: String::new(),
        a,
        b,
    };

    let out = diff_probe_artifacts(&spec).unwrap();
    assert!(!out.changed);
    assert!(!out.probe_id_changed);
    assert!(!out.probe_hash_changed);
    assert!(!out.passed_changed);
    assert!(out.matchup_diffs.iter().all(|m| !m.changed));
}

#[test]
fn diff_probe_suite_artifacts_detects_changed_probe_hash() {
    let probe_a: ProbeSpec = serde_json::from_str(
        r#"
        {
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
              "id": "m",
              "strategy_a": { "family": "builtin", "id": "tft", "kind": "tit_for_tat" },
              "strategy_b": { "family": "builtin", "id": "tft2", "kind": "tit_for_tat" },
              "replications": 1,
              "assertions": [ { "kind": "mutual_coop_rate_at_least", "min": 1.0 } ]
            }
          ]
        }
        "#,
    )
    .unwrap();

    let probe_b: ProbeSpec = serde_json::from_str(
        r#"
        {
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
              "id": "m",
              "strategy_a": { "family": "builtin", "id": "c", "kind": "always_c" },
              "strategy_b": { "family": "builtin", "id": "c2", "kind": "always_c" },
              "replications": 1,
              "assertions": [ { "kind": "mutual_coop_rate_at_least", "min": 1.0 } ]
            }
          ]
        }
        "#,
    )
    .unwrap();

    let reg_a = ProbeRegistrySpec {
        schema_version: 1,
        id: "reg".to_string(),
        description: String::new(),
        probes: vec![probe_a],
    };
    let reg_b = ProbeRegistrySpec {
        schema_version: 1,
        id: "reg".to_string(),
        description: String::new(),
        probes: vec![probe_b],
    };
    let suite = ProbeSuiteSpec {
        schema_version: 1,
        id: "suite".to_string(),
        description: String::new(),
        probe_ids: vec!["p".to_string()],
    };

    let a = run_probe_suite(&reg_a, &suite).unwrap();
    let b = run_probe_suite(&reg_b, &suite).unwrap();

    let spec = ProbeSuiteResultArtifactDiffSpec {
        schema_version: 1,
        id: "diff_suite".to_string(),
        description: String::new(),
        a,
        b,
    };

    let out = diff_probe_suite_artifacts(&spec).unwrap();
    assert!(out.changed);
    assert!(out.registry_hash_changed);
    assert!(out.probe_diffs.iter().any(|d| d.probe_hash_changed));
}
