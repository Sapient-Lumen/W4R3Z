use gr_engine::defdiff::{
    diff_snapshot_artifacts, diff_snapshots, SnapshotArtifactDiffSpec, SnapshotDiffSpec,
};
use gr_engine::snapshot::{build_snapshot, SnapshotSpec};

#[test]
fn snapshot_diff_detects_change_in_probe_suite() {
    let a: SnapshotSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "id": "a",
          "probe_registry": { "schema_version": 1, "id": "r", "probes": [] },
          "probe_suite": { "schema_version": 1, "id": "s1", "probe_ids": ["p1"] }
        }
        "#,
    )
    .unwrap();

    let b: SnapshotSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "id": "b",
          "probe_registry": { "schema_version": 1, "id": "r", "probes": [] },
          "probe_suite": { "schema_version": 1, "id": "s2", "probe_ids": ["p2"] }
        }
        "#,
    )
    .unwrap();

    let spec = SnapshotDiffSpec {
        schema_version: 1,
        id: "d".to_string(),
        description: "".to_string(),
        a,
        b,
    };

    let diff = diff_snapshots(&spec).unwrap();
    assert!(diff.changed);
    let probe_suite_change = diff
        .changes
        .iter()
        .find(|c| c.kind == "probe_suite")
        .unwrap();
    assert!(probe_suite_change.changed);
}

#[test]
fn snapshot_artifact_diff_matches_snapshot_diff() {
    let a: SnapshotSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "id": "a",
          "probe_registry": { "schema_version": 1, "id": "r", "probes": [] },
          "probe_suite": { "schema_version": 1, "id": "s1", "probe_ids": ["p1"] }
        }
        "#,
    )
    .unwrap();

    let b: SnapshotSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "id": "b",
          "probe_registry": { "schema_version": 1, "id": "r", "probes": [] },
          "probe_suite": { "schema_version": 1, "id": "s2", "probe_ids": ["p2"] }
        }
        "#,
    )
    .unwrap();

    let diff_spec = SnapshotDiffSpec {
        schema_version: 1,
        id: "d".to_string(),
        description: "".to_string(),
        a: a.clone(),
        b: b.clone(),
    };
    let diff_from_specs = diff_snapshots(&diff_spec).unwrap();

    let a_art = build_snapshot(&a).unwrap();
    let b_art = build_snapshot(&b).unwrap();
    let art_spec = SnapshotArtifactDiffSpec {
        schema_version: 1,
        id: "d2".to_string(),
        description: "".to_string(),
        a: a_art,
        b: b_art,
    };
    let diff_from_artifacts = diff_snapshot_artifacts(&art_spec).unwrap();

    assert_eq!(diff_from_specs.changed, diff_from_artifacts.changed);
    let kinds_specs = diff_from_specs
        .changes
        .iter()
        .map(|c| (c.kind.clone(), c.changed))
        .collect::<std::collections::BTreeMap<_, _>>();
    let kinds_art = diff_from_artifacts
        .changes
        .iter()
        .map(|c| (c.kind.clone(), c.changed))
        .collect::<std::collections::BTreeMap<_, _>>();
    assert_eq!(kinds_specs, kinds_art);
}
