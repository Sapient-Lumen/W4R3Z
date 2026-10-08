use crate::run_snapshot::SnapshotRunArtifact;
use crate::scorecard::{
    run_scorecard_def_on_snapshot_run, validate_scorecard_def, ScorecardDef, ScorecardError,
    ScorecardResultArtifact,
};
use crate::snapshot::SnapshotSummary;
use serde::{Deserialize, Serialize};
use thiserror::Error;

fn default_schema_version() -> u32 {
    1
}

#[derive(Debug, Error)]
pub enum ScorecardSuiteError {
    #[error("scorecard suite schema_version {0} is unsupported")]
    UnsupportedSchemaVersion(u32),
    #[error(transparent)]
    Scorecard(#[from] ScorecardError),
    #[error("invalid value: {0}")]
    InvalidValue(String),
    #[error("duplicate scorecard id {0}")]
    DuplicateScorecardId(String),
    #[error("missing scorecard id {0}")]
    MissingScorecardId(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScorecardRegistrySpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub scorecards: Vec<ScorecardDef>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScorecardSuiteSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub scorecard_ids: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScorecardSuiteResultArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub registry_id: String,
    pub suite_id: String,
    pub input_hash: String,
    pub registry_hash: String,
    pub suite_hash: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub snapshot: Option<SnapshotSummary>,
    pub passed: bool,
    pub scorecard_results: Vec<ScorecardResultArtifact>,
}

pub fn validate_scorecard_registry(reg: &ScorecardRegistrySpec) -> Result<(), ScorecardSuiteError> {
    if reg.schema_version != 1 {
        return Err(ScorecardSuiteError::UnsupportedSchemaVersion(
            reg.schema_version,
        ));
    }
    let mut ids = std::collections::BTreeSet::new();
    for s in &reg.scorecards {
        if !ids.insert(s.id.clone()) {
            return Err(ScorecardSuiteError::DuplicateScorecardId(s.id.clone()));
        }
        validate_scorecard_def(s)?;
    }
    Ok(())
}

pub fn validate_scorecard_suite(suite: &ScorecardSuiteSpec) -> Result<(), ScorecardSuiteError> {
    if suite.schema_version != 1 {
        return Err(ScorecardSuiteError::UnsupportedSchemaVersion(
            suite.schema_version,
        ));
    }
    if suite.scorecard_ids.is_empty() {
        return Err(ScorecardSuiteError::InvalidValue(
            "suite scorecard_ids must be non-empty".to_string(),
        ));
    }
    Ok(())
}

fn find_scorecard<'a>(reg: &'a ScorecardRegistrySpec, id: &str) -> Option<&'a ScorecardDef> {
    reg.scorecards.iter().find(|s| s.id == id)
}

pub fn run_scorecard_suite(
    reg: &ScorecardRegistrySpec,
    suite: &ScorecardSuiteSpec,
    snapshot_run: &SnapshotRunArtifact,
) -> Result<ScorecardSuiteResultArtifact, ScorecardSuiteError> {
    validate_scorecard_registry(reg)?;
    validate_scorecard_suite(suite)?;

    let registry_hash = {
        let canonical = serde_json::to_vec(reg)
            .map_err(|e| ScorecardSuiteError::InvalidValue(e.to_string()))?;
        crate::util::sha256_hex(&canonical)
    };
    let suite_hash = {
        let canonical = serde_json::to_vec(suite)
            .map_err(|e| ScorecardSuiteError::InvalidValue(e.to_string()))?;
        crate::util::sha256_hex(&canonical)
    };

    let snapshot = Some(crate::snapshot::summarize_snapshot(&snapshot_run.snapshot));

    let mut scorecard_results = Vec::with_capacity(suite.scorecard_ids.len());
    for id in &suite.scorecard_ids {
        let def = find_scorecard(reg, id)
            .ok_or_else(|| ScorecardSuiteError::MissingScorecardId(id.clone()))?;

        let canonical = serde_json::to_vec(&(def, snapshot_run))
            .map_err(|e| ScorecardSuiteError::InvalidValue(e.to_string()))?;
        let input_hash = crate::util::sha256_hex(&canonical);

        let mut r = run_scorecard_def_on_snapshot_run(def, snapshot_run)?;
        r.input_hash = input_hash;
        scorecard_results.push(r);
    }

    let passed = scorecard_results.iter().all(|r| r.passed);
    Ok(ScorecardSuiteResultArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        registry_id: reg.id.clone(),
        suite_id: suite.id.clone(),
        input_hash: String::new(), // filled by CLI
        registry_hash,
        suite_hash,
        snapshot,
        passed,
        scorecard_results,
    })
}
