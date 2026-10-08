use gr_engine::snapshot::{build_snapshot, SnapshotSpec};

#[test]
fn snapshot_input_hash_is_stable_across_json_formatting() {
    let a = r#"
    {
      "id": "snap",
      "schema_version": 1,
      "probe_registry": { "schema_version": 1, "id": "r", "probes": [] },
      "probe_suite": { "schema_version": 1, "id": "s", "probe_ids": ["p1"] }
    }
    "#;

    let b = r#"{ "probe_suite":{"probe_ids":["p1"],"id":"s","schema_version":1}, "probe_registry":{"id":"r","probes":[],"schema_version":1}, "id":"snap", "schema_version":1 }"#;

    let sa: SnapshotSpec = serde_json::from_str(a).unwrap();
    let sb: SnapshotSpec = serde_json::from_str(b).unwrap();

    let aa = build_snapshot(&sa).unwrap();
    let ab = build_snapshot(&sb).unwrap();
    assert_eq!(aa.input_hash, ab.input_hash);
    assert_eq!(
        aa.probe_registry.unwrap().hash,
        ab.probe_registry.unwrap().hash
    );
    assert_eq!(aa.probe_suite.unwrap().hash, ab.probe_suite.unwrap().hash);
}
