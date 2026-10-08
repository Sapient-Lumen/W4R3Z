use crate::snapshot::{build_snapshot, SnapshotArtifact, SnapshotSpec};
use serde::{Deserialize, Serialize};
use thiserror::Error;

fn default_schema_version() -> u32 {
    1
}

#[derive(Debug, Error)]
pub enum DiffError {
    #[error("diff schema_version {0} is unsupported")]
    UnsupportedSchemaVersion(u32),
    #[error("invalid value: {0}")]
    InvalidValue(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnapshotDiffSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub a: SnapshotSpec,
    pub b: SnapshotSpec,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnapshotArtifactDiffSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub a: SnapshotArtifact,
    pub b: SnapshotArtifact,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnapshotDiffArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub diff_id: String,
    pub input_hash: String,
    pub a: SnapshotArtifact,
    pub b: SnapshotArtifact,
    pub changes: Vec<DefChange>,
    pub changed: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DefChange {
    pub kind: String,
    pub a: Option<crate::snapshot::HashedDef>,
    pub b: Option<crate::snapshot::HashedDef>,
    pub changed: bool,
}

fn push_change(
    changes: &mut Vec<DefChange>,
    kind: &str,
    a: &Option<crate::snapshot::HashedDef>,
    b: &Option<crate::snapshot::HashedDef>,
) {
    let changed = match (a, b) {
        (None, None) => false,
        (Some(_), None) | (None, Some(_)) => true,
        (Some(x), Some(y)) => x.hash != y.hash,
    };
    changes.push(DefChange {
        kind: kind.to_string(),
        a: a.clone(),
        b: b.clone(),
        changed,
    });
}

fn diff_snapshot_artifacts_inner(a: &SnapshotArtifact, b: &SnapshotArtifact) -> Vec<DefChange> {
    let mut changes = Vec::new();
    push_change(
        &mut changes,
        "world_registry",
        &a.world_registry,
        &b.world_registry,
    );
    push_change(&mut changes, "world_suite", &a.world_suite, &b.world_suite);
    push_change(
        &mut changes,
        "probe_registry",
        &a.probe_registry,
        &b.probe_registry,
    );
    push_change(&mut changes, "probe_suite", &a.probe_suite, &b.probe_suite);
    push_change(
        &mut changes,
        "metamorphic_registry",
        &a.metamorphic_registry,
        &b.metamorphic_registry,
    );
    push_change(
        &mut changes,
        "metamorphic_suite",
        &a.metamorphic_suite,
        &b.metamorphic_suite,
    );
    push_change(&mut changes, "scorecard", &a.scorecard, &b.scorecard);
    push_change(
        &mut changes,
        "scorecard_registry",
        &a.scorecard_registry,
        &b.scorecard_registry,
    );
    push_change(
        &mut changes,
        "scorecard_suite",
        &a.scorecard_suite,
        &b.scorecard_suite,
    );
    changes
}

pub fn diff_snapshots(spec: &SnapshotDiffSpec) -> Result<SnapshotDiffArtifact, DiffError> {
    if spec.schema_version != 1 {
        return Err(DiffError::UnsupportedSchemaVersion(spec.schema_version));
    }

    let a = build_snapshot(&spec.a).map_err(|e| DiffError::InvalidValue(e.to_string()))?;
    let b = build_snapshot(&spec.b).map_err(|e| DiffError::InvalidValue(e.to_string()))?;

    let changes = diff_snapshot_artifacts_inner(&a, &b);

    let changed = changes.iter().any(|c| c.changed);
    Ok(SnapshotDiffArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        diff_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        a,
        b,
        changes,
        changed,
    })
}

pub fn diff_snapshot_artifacts(
    spec: &SnapshotArtifactDiffSpec,
) -> Result<SnapshotDiffArtifact, DiffError> {
    if spec.schema_version != 1 {
        return Err(DiffError::UnsupportedSchemaVersion(spec.schema_version));
    }

    let changes = diff_snapshot_artifacts_inner(&spec.a, &spec.b);
    let changed = changes.iter().any(|c| c.changed);
    Ok(SnapshotDiffArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        diff_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        a: spec.a.clone(),
        b: spec.b.clone(),
        changes,
        changed,
    })
}
