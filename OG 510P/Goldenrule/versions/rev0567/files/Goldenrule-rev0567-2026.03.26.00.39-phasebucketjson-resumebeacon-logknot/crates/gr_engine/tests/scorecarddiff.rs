use gr_engine::scorecard::{
    run_scorecard, ScorecardBanner, ScorecardCard, ScorecardGateSpec, ScorecardResultArtifact,
    ScorecardSpec,
};
use gr_engine::scorecarddiff::{diff_scorecard_artifacts, ScorecardResultArtifactDiffSpec};

fn minimal_card() -> ScorecardCard {
    ScorecardCard {
        id: "card".to_string(),
        version: "v1".to_string(),
        intent: "test".to_string(),
        non_goals: vec![],
        lenses: vec![],
        known_risks: vec![],
        required_holdouts: vec![],
        required_metamorphic: vec![],
        appropriate_contexts: vec![],
        inappropriate_contexts: vec![],
        changelog: vec![],
    }
}

#[test]
fn diff_scorecard_artifacts_is_unchanged_for_identical_results() {
    let spec = ScorecardSpec {
        schema_version: 1,
        id: "sc".to_string(),
        description: "".to_string(),
        card: minimal_card(),
        gates: ScorecardGateSpec {
            require_probe_suite: false,
            require_metamorphic_suite: false,
            fail_on_hash_mismatch: false,
        },
        snapshot: None,
        snapshot_run: None,
        probe_suite: None,
        metamorphic_suite: None,
    };

    let a = run_scorecard(&spec).unwrap();
    let b = run_scorecard(&spec).unwrap();

    let diff_spec = ScorecardResultArtifactDiffSpec {
        schema_version: 1,
        id: "d".to_string(),
        description: "".to_string(),
        a,
        b,
    };

    let out = diff_scorecard_artifacts(&diff_spec).unwrap();
    assert!(!out.changed);
    assert!(!out.passed_changed);
    assert!(!out.card_changed);
    assert!(!out.banner_changed);
    assert!(!out.warnings_changed);
}

#[test]
fn diff_scorecard_artifacts_detects_warning_change() {
    let mut a = ScorecardResultArtifact {
        schema_version: 1,
        engine_version: "0.1.0".to_string(),
        scorecard_id: "sc".to_string(),
        input_hash: "".to_string(),
        card: minimal_card(),
        snapshot: None,
        passed: true,
        banner: ScorecardBanner {
            headline: "PASS".to_string(),
            passed: true,
            probe_suite_passed: None,
            probes_total: 0,
            probes_failed: 0,
            metamorphic_suite_passed: None,
            checks_total: 0,
            checks_failed: 0,
            checks_skipped_matchups: 0,
        },
        warnings: vec![],
    };
    let mut b = a.clone();
    b.warnings.push("note".to_string());
    a.engine_version = env!("CARGO_PKG_VERSION").to_string();
    b.engine_version = env!("CARGO_PKG_VERSION").to_string();

    let diff_spec = ScorecardResultArtifactDiffSpec {
        schema_version: 1,
        id: "d".to_string(),
        description: "".to_string(),
        a,
        b,
    };

    let out = diff_scorecard_artifacts(&diff_spec).unwrap();
    assert!(out.changed);
    assert!(out.warnings_changed);
}
