use crate::metamorphic::{run_metamorphic_suite_with_snapshot, MetamorphicError};
use crate::probe::{run_probe_suite_with_snapshot, ProbeRunError};
use crate::scorecard::{run_scorecard, ScorecardError, ScorecardSpec};
use crate::scorecard_suite::{run_scorecard_suite, ScorecardSuiteError};
use crate::snapshot::{
    build_snapshot, summarize_snapshot, SnapshotArtifact, SnapshotError, SnapshotSpec,
};
use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum RunSnapshotError {
    #[error(transparent)]
    Snapshot(#[from] SnapshotError),
    #[error(transparent)]
    Probe(#[from] ProbeRunError),
    #[error(transparent)]
    Metamorphic(#[from] MetamorphicError),
    #[error(transparent)]
    Scorecard(#[from] ScorecardError),
    #[error(transparent)]
    ScorecardSuite(#[from] ScorecardSuiteError),
    #[error("invalid snapshot: {0}")]
    Invalid(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnapshotRunArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub run_id: String,
    pub input_hash: String,
    pub snapshot: SnapshotArtifact,
    pub passed: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub probe_suite: Option<crate::probe::ProbeSuiteResultArtifact>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metamorphic_suite: Option<crate::metamorphic::MetamorphicSuiteResultArtifact>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scorecard: Option<crate::scorecard::ScorecardResultArtifact>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scorecard_suite: Option<crate::scorecard_suite::ScorecardSuiteResultArtifact>,
}

pub fn run_snapshot(spec: &SnapshotSpec) -> Result<SnapshotRunArtifact, RunSnapshotError> {
    let snapshot = build_snapshot(spec)?;
    let summary = summarize_snapshot(&snapshot);

    let mut probe_suite = None;
    if spec.probe_suite.is_some() || spec.probe_registry.is_some() {
        let Some(reg) = &spec.probe_registry else {
            return Err(RunSnapshotError::Invalid(
                "probe_suite requires probe_registry".to_string(),
            ));
        };
        let Some(suite) = &spec.probe_suite else {
            return Err(RunSnapshotError::Invalid(
                "probe_registry requires probe_suite for run_snapshot".to_string(),
            ));
        };
        let mut r = run_probe_suite_with_snapshot(reg, suite, summary.clone())?;
        let canonical = serde_json::to_vec(&(reg, suite, &summary))
            .map_err(|e| RunSnapshotError::Invalid(e.to_string()))?;
        r.input_hash = crate::util::sha256_hex(&canonical);
        probe_suite = Some(r);
    }

    let mut metamorphic_suite = None;
    if spec.metamorphic_suite.is_some() || spec.metamorphic_registry.is_some() {
        let Some(reg) = &spec.metamorphic_registry else {
            return Err(RunSnapshotError::Invalid(
                "metamorphic_suite requires metamorphic_registry".to_string(),
            ));
        };
        let Some(suite) = &spec.metamorphic_suite else {
            return Err(RunSnapshotError::Invalid(
                "metamorphic_registry requires metamorphic_suite for run_snapshot".to_string(),
            ));
        };
        let mut r = run_metamorphic_suite_with_snapshot(reg, suite, summary.clone())?;
        let canonical = serde_json::to_vec(&(reg, suite, &summary))
            .map_err(|e| RunSnapshotError::Invalid(e.to_string()))?;
        r.input_hash = crate::util::sha256_hex(&canonical);
        metamorphic_suite = Some(r);
    }

    let base_run = SnapshotRunArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        run_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        snapshot: snapshot.clone(),
        passed: false, // filled later
        probe_suite: probe_suite.clone(),
        metamorphic_suite: metamorphic_suite.clone(),
        scorecard: None,
        scorecard_suite: None,
    };

    let mut scorecard = None;
    if let Some(def) = &spec.scorecard {
        let scorecard_spec = ScorecardSpec {
            schema_version: 1,
            id: def.id.clone(),
            description: def.description.clone(),
            card: def.card.clone(),
            gates: def.gates.clone(),
            snapshot: Some(summary.clone()),
            snapshot_run: None,
            probe_suite: probe_suite.clone(),
            metamorphic_suite: metamorphic_suite.clone(),
        };
        let canonical = serde_json::to_vec(&scorecard_spec)
            .map_err(|e| RunSnapshotError::Invalid(e.to_string()))?;
        let input_hash = crate::util::sha256_hex(&canonical);
        let mut r = run_scorecard(&scorecard_spec)?;
        r.input_hash = input_hash;
        scorecard = Some(r);
    }

    let mut scorecard_suite = None;
    if spec.scorecard_suite.is_some() || spec.scorecard_registry.is_some() {
        let Some(reg) = &spec.scorecard_registry else {
            return Err(RunSnapshotError::Invalid(
                "scorecard_suite requires scorecard_registry".to_string(),
            ));
        };
        let Some(suite) = &spec.scorecard_suite else {
            return Err(RunSnapshotError::Invalid(
                "scorecard_registry requires scorecard_suite for run_snapshot".to_string(),
            ));
        };
        let mut r = run_scorecard_suite(reg, suite, &base_run)?;
        let canonical = serde_json::to_vec(&(reg, suite, &summary, &base_run))
            .map_err(|e| RunSnapshotError::Invalid(e.to_string()))?;
        r.input_hash = crate::util::sha256_hex(&canonical);
        scorecard_suite = Some(r);
    }

    let passed = probe_suite.as_ref().map(|r| r.passed).unwrap_or(true)
        && metamorphic_suite.as_ref().map(|r| r.passed).unwrap_or(true)
        && scorecard.as_ref().map(|r| r.passed).unwrap_or(true)
        && scorecard_suite.as_ref().map(|r| r.passed).unwrap_or(true);

    Ok(SnapshotRunArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        run_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        snapshot,
        passed,
        probe_suite,
        metamorphic_suite,
        scorecard,
        scorecard_suite,
    })
}
