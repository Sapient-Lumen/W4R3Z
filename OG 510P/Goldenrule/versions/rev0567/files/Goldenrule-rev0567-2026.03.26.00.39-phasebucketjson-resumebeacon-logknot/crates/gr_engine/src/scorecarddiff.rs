use crate::scorecard::{ScorecardBanner, ScorecardResultArtifact};
use serde::{Deserialize, Serialize};
use thiserror::Error;

fn default_schema_version() -> u32 {
    1
}

#[derive(Debug, Error)]
pub enum ScorecardDiffError {
    #[error("scorecard diff schema_version {0} is unsupported")]
    UnsupportedSchemaVersion(u32),
    #[error("invalid value: {0}")]
    InvalidValue(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScorecardResultArtifactDiffSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub a: ScorecardResultArtifact,
    pub b: ScorecardResultArtifact,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScorecardBannerDelta {
    pub probes_failed: i64,
    pub probes_total: i64,
    pub checks_failed: i64,
    pub checks_total: i64,
    pub checks_skipped_matchups: i64,
}

fn banner_delta(a: &ScorecardBanner, b: &ScorecardBanner) -> ScorecardBannerDelta {
    ScorecardBannerDelta {
        probes_failed: b.probes_failed as i64 - a.probes_failed as i64,
        probes_total: b.probes_total as i64 - a.probes_total as i64,
        checks_failed: b.checks_failed as i64 - a.checks_failed as i64,
        checks_total: b.checks_total as i64 - a.checks_total as i64,
        checks_skipped_matchups: b.checks_skipped_matchups as i64
            - a.checks_skipped_matchups as i64,
    }
}

fn warnings_hash(warnings: &[String]) -> Result<String, ScorecardDiffError> {
    let canonical = serde_json::to_vec(warnings)
        .map_err(|e| ScorecardDiffError::InvalidValue(e.to_string()))?;
    Ok(crate::util::sha256_hex(&canonical))
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScorecardResultDiffArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub diff_id: String,
    pub input_hash: String,
    pub a: ScorecardResultArtifact,
    pub b: ScorecardResultArtifact,
    pub passed_changed: bool,
    pub card_changed: bool,
    pub banner_changed: bool,
    pub banner_deltas: ScorecardBannerDelta,
    pub warnings_changed: bool,
    pub changed: bool,
}

pub fn diff_scorecard_artifacts(
    spec: &ScorecardResultArtifactDiffSpec,
) -> Result<ScorecardResultDiffArtifact, ScorecardDiffError> {
    if spec.schema_version != 1 {
        return Err(ScorecardDiffError::UnsupportedSchemaVersion(
            spec.schema_version,
        ));
    }

    let passed_changed = spec.a.passed != spec.b.passed;
    let card_changed = serde_json::to_value(&spec.a.card)
        .map_err(|e| ScorecardDiffError::InvalidValue(e.to_string()))?
        != serde_json::to_value(&spec.b.card)
            .map_err(|e| ScorecardDiffError::InvalidValue(e.to_string()))?;
    let banner_changed = serde_json::to_value(&spec.a.banner)
        .map_err(|e| ScorecardDiffError::InvalidValue(e.to_string()))?
        != serde_json::to_value(&spec.b.banner)
            .map_err(|e| ScorecardDiffError::InvalidValue(e.to_string()))?;
    let warnings_changed = warnings_hash(&spec.a.warnings)? != warnings_hash(&spec.b.warnings)?;
    let changed = passed_changed || card_changed || banner_changed || warnings_changed;

    Ok(ScorecardResultDiffArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        diff_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        a: spec.a.clone(),
        b: spec.b.clone(),
        passed_changed,
        card_changed,
        banner_changed,
        banner_deltas: banner_delta(&spec.a.banner, &spec.b.banner),
        warnings_changed,
        changed,
    })
}
