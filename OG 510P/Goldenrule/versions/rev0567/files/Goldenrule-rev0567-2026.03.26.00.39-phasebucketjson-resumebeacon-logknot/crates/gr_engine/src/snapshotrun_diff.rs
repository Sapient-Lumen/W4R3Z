use crate::defdiff::{diff_snapshot_artifacts, SnapshotArtifactDiffSpec};
use crate::metadiff::{diff_metamorphic_suite_artifacts, MetamorphicSuiteResultArtifactDiffSpec};
use crate::probediff::{diff_probe_suite_artifacts, ProbeSuiteResultArtifactDiffSpec};
use crate::run_snapshot::SnapshotRunArtifact;
use crate::scorecard_suitediff::{
    diff_scorecard_suite_artifacts, ScorecardSuiteResultArtifactDiffSpec,
};
use crate::scorecarddiff::{diff_scorecard_artifacts, ScorecardResultArtifactDiffSpec};
use serde::{Deserialize, Serialize};
use thiserror::Error;

fn default_schema_version() -> u32 {
    1
}

#[derive(Debug, Error)]
pub enum SnapshotRunDiffError {
    #[error("snapshot run diff schema_version {0} is unsupported")]
    UnsupportedSchemaVersion(u32),
    #[error("invalid value: {0}")]
    InvalidValue(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnapshotRunArtifactDiffSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub a: SnapshotRunArtifact,
    pub b: SnapshotRunArtifact,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnapshotRunDiffArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub diff_id: String,
    pub input_hash: String,
    pub a: SnapshotRunArtifact,
    pub b: SnapshotRunArtifact,
    pub passed_changed: bool,
    pub snapshot_changed: bool,
    pub probe_suite_changed: bool,
    pub metamorphic_suite_changed: bool,
    pub scorecard_changed: bool,
    pub scorecard_suite_changed: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub snapshot_diff: Option<crate::defdiff::SnapshotDiffArtifact>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub probe_suite_diff: Option<crate::probediff::ProbeSuiteDiffArtifact>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metamorphic_suite_diff: Option<crate::metadiff::MetamorphicSuiteDiffArtifact>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scorecard_diff: Option<crate::scorecarddiff::ScorecardResultDiffArtifact>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scorecard_suite_diff: Option<crate::scorecard_suitediff::ScorecardSuiteDiffArtifact>,
    pub changed: bool,
}

pub fn diff_snapshot_run_artifacts(
    spec: &SnapshotRunArtifactDiffSpec,
) -> Result<SnapshotRunDiffArtifact, SnapshotRunDiffError> {
    if spec.schema_version != 1 {
        return Err(SnapshotRunDiffError::UnsupportedSchemaVersion(
            spec.schema_version,
        ));
    }

    let passed_changed = spec.a.passed != spec.b.passed;
    let snapshot_diff_spec = SnapshotArtifactDiffSpec {
        schema_version: 1,
        id: format!("{}__snapshot", spec.id),
        description: String::new(),
        a: spec.a.snapshot.clone(),
        b: spec.b.snapshot.clone(),
    };
    let mut snapshot_diff = diff_snapshot_artifacts(&snapshot_diff_spec)
        .map_err(|e| SnapshotRunDiffError::InvalidValue(e.to_string()))?;
    snapshot_diff.input_hash = crate::util::sha256_hex(
        &serde_json::to_vec(&snapshot_diff_spec)
            .map_err(|e| SnapshotRunDiffError::InvalidValue(e.to_string()))?,
    );
    let snapshot_changed = snapshot_diff.changed;

    let snapshot_diff = Some(snapshot_diff);

    let mut probe_suite_diff = None;
    let mut probe_suite_changed = false;
    match (&spec.a.probe_suite, &spec.b.probe_suite) {
        (Some(a), Some(b)) => {
            let diff_spec = ProbeSuiteResultArtifactDiffSpec {
                schema_version: 1,
                id: format!("{}__probe_suite", spec.id),
                description: String::new(),
                a: a.clone(),
                b: b.clone(),
            };
            let mut d = diff_probe_suite_artifacts(&diff_spec)
                .map_err(|e| SnapshotRunDiffError::InvalidValue(e.to_string()))?;
            d.input_hash = crate::util::sha256_hex(
                &serde_json::to_vec(&diff_spec)
                    .map_err(|e| SnapshotRunDiffError::InvalidValue(e.to_string()))?,
            );
            probe_suite_changed = d.changed;
            probe_suite_diff = Some(d);
        }
        (None, None) => {}
        _ => probe_suite_changed = true,
    }

    let mut metamorphic_suite_diff = None;
    let mut metamorphic_suite_changed = false;
    match (&spec.a.metamorphic_suite, &spec.b.metamorphic_suite) {
        (Some(a), Some(b)) => {
            let diff_spec = MetamorphicSuiteResultArtifactDiffSpec {
                schema_version: 1,
                id: format!("{}__metamorphic_suite", spec.id),
                description: String::new(),
                a: a.clone(),
                b: b.clone(),
            };
            let mut d = diff_metamorphic_suite_artifacts(&diff_spec)
                .map_err(|e| SnapshotRunDiffError::InvalidValue(e.to_string()))?;
            d.input_hash = crate::util::sha256_hex(
                &serde_json::to_vec(&diff_spec)
                    .map_err(|e| SnapshotRunDiffError::InvalidValue(e.to_string()))?,
            );
            metamorphic_suite_changed = d.changed;
            metamorphic_suite_diff = Some(d);
        }
        (None, None) => {}
        _ => metamorphic_suite_changed = true,
    }

    let mut scorecard_diff = None;
    let mut scorecard_changed = false;
    match (&spec.a.scorecard, &spec.b.scorecard) {
        (Some(a), Some(b)) => {
            let diff_spec = ScorecardResultArtifactDiffSpec {
                schema_version: 1,
                id: format!("{}__scorecard", spec.id),
                description: String::new(),
                a: a.clone(),
                b: b.clone(),
            };
            let mut d = diff_scorecard_artifacts(&diff_spec)
                .map_err(|e| SnapshotRunDiffError::InvalidValue(e.to_string()))?;
            d.input_hash = crate::util::sha256_hex(
                &serde_json::to_vec(&diff_spec)
                    .map_err(|e| SnapshotRunDiffError::InvalidValue(e.to_string()))?,
            );
            scorecard_changed = d.changed;
            scorecard_diff = Some(d);
        }
        (None, None) => {}
        _ => scorecard_changed = true,
    }

    let mut scorecard_suite_diff = None;
    let mut scorecard_suite_changed = false;
    match (&spec.a.scorecard_suite, &spec.b.scorecard_suite) {
        (Some(a), Some(b)) => {
            let diff_spec = ScorecardSuiteResultArtifactDiffSpec {
                schema_version: 1,
                id: format!("{}__scorecard_suite", spec.id),
                description: String::new(),
                a: a.clone(),
                b: b.clone(),
            };
            let mut d = diff_scorecard_suite_artifacts(&diff_spec)
                .map_err(|e| SnapshotRunDiffError::InvalidValue(e.to_string()))?;
            d.input_hash = crate::util::sha256_hex(
                &serde_json::to_vec(&diff_spec)
                    .map_err(|e| SnapshotRunDiffError::InvalidValue(e.to_string()))?,
            );
            scorecard_suite_changed = d.changed;
            scorecard_suite_diff = Some(d);
        }
        (None, None) => {}
        _ => scorecard_suite_changed = true,
    }

    let changed = passed_changed
        || snapshot_changed
        || probe_suite_changed
        || metamorphic_suite_changed
        || scorecard_changed
        || scorecard_suite_changed;

    Ok(SnapshotRunDiffArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        diff_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        a: spec.a.clone(),
        b: spec.b.clone(),
        passed_changed,
        snapshot_changed,
        probe_suite_changed,
        metamorphic_suite_changed,
        scorecard_changed,
        scorecard_suite_changed,
        snapshot_diff,
        probe_suite_diff,
        metamorphic_suite_diff,
        scorecard_diff,
        scorecard_suite_diff,
        changed,
    })
}
