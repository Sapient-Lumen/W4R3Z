use gr_engine::snapshot::{build_snapshot, SnapshotSpec};
use gr_engine::worldsheet::{
    validate_world_registry, validate_world_suite, WorldDatasheet, WorldRegistrySpec,
    WorldSuiteSpec,
};

#[test]
fn worldsheet_validation_smoke() {
    let reg = WorldRegistrySpec {
        schema_version: 1,
        id: "reg".to_string(),
        description: "".to_string(),
        worlds: vec![gr_engine::spec::WorldSpec {
            id: "w1".to_string(),
            game: gr_engine::spec::GameSpec::default(),
            noise: gr_engine::spec::NoiseModelSpec::None,
            termination: gr_engine::spec::TerminationRuleSpec::Fixed { rounds: 10 },
            reputation: gr_engine::spec::ReputationModelSpec::None,
            seed: 123,
        }],
    };
    let suite = WorldSuiteSpec {
        schema_version: 1,
        id: "suite".to_string(),
        description: "".to_string(),
        datasheet: WorldDatasheet {
            composition: "one world".to_string(),
            rationale: "smoke".to_string(),
            gaps_and_limitations: vec![],
            brittleness_tendencies: vec![],
            update_policy: "append-only".to_string(),
        },
        world_ids: vec!["w1".to_string()],
    };

    validate_world_registry(&reg).unwrap();
    validate_world_suite(&reg, &suite).unwrap();
}

#[test]
fn snapshot_can_hash_world_registry_and_suite() {
    let spec: SnapshotSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "id": "snap",
          "world_registry": {
            "schema_version": 1,
            "id": "wr",
            "worlds": [
              {
                "id": "w1",
                "seed": 1,
                "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } },
                "noise": { "kind": "none" },
                "termination": { "kind": "fixed", "rounds": 10 }
              }
            ]
          },
          "world_suite": {
            "schema_version": 1,
            "id": "ws",
            "datasheet": {
              "composition": "one world",
              "rationale": "smoke",
              "update_policy": "append-only"
            },
            "world_ids": ["w1"]
          }
        }
        "#,
    )
    .unwrap();

    let art = build_snapshot(&spec).unwrap();
    assert!(art.world_registry.is_some());
    assert!(art.world_suite.is_some());
}

#[test]
fn worldsheet_validation_accepts_geometric_and_asymmetric_iid() {
    let reg = WorldRegistrySpec {
        schema_version: 1,
        id: "reg2".to_string(),
        description: "".to_string(),
        worlds: vec![
            gr_engine::spec::WorldSpec {
                id: "geo".to_string(),
                game: gr_engine::spec::GameSpec::default(),
                noise: gr_engine::spec::NoiseModelSpec::None,
                termination: gr_engine::spec::TerminationRuleSpec::Geometric {
                    delta: 0.9,
                    max_rounds: 10,
                },
                reputation: gr_engine::spec::ReputationModelSpec::None,
                seed: 123,
            },
            gr_engine::spec::WorldSpec {
                id: "asym".to_string(),
                game: gr_engine::spec::GameSpec::default(),
                noise: gr_engine::spec::NoiseModelSpec::AsymmetricIid {
                    p_implementation_a: 0.0,
                    p_implementation_b: 0.1,
                    p_observation_a: 0.2,
                    p_observation_b: 0.0,
                },
                termination: gr_engine::spec::TerminationRuleSpec::Fixed { rounds: 10 },
                reputation: gr_engine::spec::ReputationModelSpec::None,
                seed: 456,
            },
        ],
    };
    validate_world_registry(&reg).unwrap();
}

#[test]
fn snapshot_can_hash_geometric_and_asymmetric_iid_worlds() {
    let spec: SnapshotSpec = serde_json::from_str(
        r#"
        {
          "schema_version": 1,
          "id": "snap2",
          "world_registry": {
            "schema_version": 1,
            "id": "wr2",
            "worlds": [
              {
                "id": "geo",
                "seed": 1,
                "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } },
                "noise": { "kind": "none" },
                "termination": { "kind": "geometric", "delta": 0.9, "max_rounds": 10 }
              },
              {
                "id": "asym",
                "seed": 2,
                "game": { "kind": "ipd", "payoffs": { "r": 3, "s": 0, "t": 5, "p": 1 } },
                "noise": {
                  "kind": "asymmetric_iid",
                  "p_implementation_a": 0.0,
                  "p_implementation_b": 0.1,
                  "p_observation_a": 0.2,
                  "p_observation_b": 0.0
                },
                "termination": { "kind": "fixed", "rounds": 10 }
              }
            ]
          },
          "world_suite": {
            "schema_version": 1,
            "id": "ws2",
            "datasheet": {
              "composition": "two worlds",
              "rationale": "schema coverage",
              "update_policy": "append-only"
            },
            "world_ids": ["geo", "asym"]
          }
        }
        "#,
    )
    .unwrap();

    let art = build_snapshot(&spec).unwrap();
    assert!(art.world_registry.is_some());
    assert!(art.world_suite.is_some());
}
