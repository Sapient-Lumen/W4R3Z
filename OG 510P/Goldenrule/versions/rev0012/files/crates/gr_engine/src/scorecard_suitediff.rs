use crate::scorecard::ScorecardResultArtifact;
use crate::scorecard_suite::ScorecardSuiteResultArtifact;
use crate::scorecarddiff::{diff_scorecard_artifacts, ScorecardResultArtifactDiffSpec};
use serde::{Deserialize, Serialize};
use thiserror::Error;

fn default_schema_version() -> u32 {
    1
}

#[derive(Debug, Error)]
pub enum ScorecardSuiteDiffError {
    #[error("scorecard suite diff schema_version {0} is unsupported")]
    UnsupportedSchemaVersion(u32),
    #[error("invalid value: {0}")]
    InvalidValue(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScorecardSuiteResultArtifactDiffSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub a: ScorecardSuiteResultArtifact,
    pub b: ScorecardSuiteResultArtifact,
}

fn hash_json<T: Serialize>(obj: &T) -> Result<String, ScorecardSuiteDiffError> {
    let canonical = serde_json::to_vec(obj)
        .map_err(|e| ScorecardSuiteDiffError::InvalidValue(e.to_string()))?;
    Ok(crate::util::sha256_hex(&canonical))
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScorecardSuiteScorecardDiff {
    pub scorecard_id: String,
    pub kind: String, // added|removed|changed|unchanged
    pub changed: bool,
    pub a_passed: Option<bool>,
    pub b_passed: Option<bool>,
    pub passed_changed: bool,
    pub banner_changed: bool,
    pub warnings_changed: bool,
}

fn get_scorecard<'a>(
    suite: &'a ScorecardSuiteResultArtifact,
) -> std::collections::BTreeMap<String, &'a ScorecardResultArtifact> {
    let mut m = std::collections::BTreeMap::new();
    for r in &suite.scorecard_results {
        m.insert(r.scorecard_id.clone(), r);
    }
    m
}

fn diff_scorecards(
    a: &ScorecardSuiteResultArtifact,
    b: &ScorecardSuiteResultArtifact,
) -> Result<Vec<ScorecardSuiteScorecardDiff>, ScorecardSuiteDiffError> {
    let a_map = get_scorecard(a);
    let b_map = get_scorecard(b);
    let ids = a_map
        .keys()
        .chain(b_map.keys())
        .cloned()
        .collect::<std::collections::BTreeSet<_>>();

    let mut out = Vec::with_capacity(ids.len());
    for id in ids {
        match (a_map.get(&id), b_map.get(&id)) {
            (Some(ar), Some(br)) => {
                let spec = ScorecardResultArtifactDiffSpec {
                    schema_version: 1,
                    id: "inner".to_string(),
                    description: String::new(),
                    a: (*ar).clone(),
                    b: (*br).clone(),
                };
                let d = diff_scorecard_artifacts(&spec)
                    .map_err(|e| ScorecardSuiteDiffError::InvalidValue(e.to_string()))?;
                out.push(ScorecardSuiteScorecardDiff {
                    scorecard_id: id,
                    kind: if d.changed { "changed" } else { "unchanged" }.to_string(),
                    changed: d.changed,
                    a_passed: Some(ar.passed),
                    b_passed: Some(br.passed),
                    passed_changed: d.passed_changed,
                    banner_changed: d.banner_changed,
                    warnings_changed: d.warnings_changed,
                });
            }
            (Some(ar), None) => out.push(ScorecardSuiteScorecardDiff {
                scorecard_id: id,
                kind: "removed".to_string(),
                changed: true,
                a_passed: Some(ar.passed),
                b_passed: None,
                passed_changed: true,
                banner_changed: true,
                warnings_changed: true,
            }),
            (None, Some(br)) => out.push(ScorecardSuiteScorecardDiff {
                scorecard_id: id,
                kind: "added".to_string(),
                changed: true,
                a_passed: None,
                b_passed: Some(br.passed),
                passed_changed: true,
                banner_changed: true,
                warnings_changed: true,
            }),
            (None, None) => {}
        }
    }
    Ok(out)
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScorecardSuiteDiffArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub diff_id: String,
    pub input_hash: String,
    pub a: ScorecardSuiteResultArtifact,
    pub b: ScorecardSuiteResultArtifact,
    pub passed_changed: bool,
    pub registry_hash_changed: bool,
    pub suite_hash_changed: bool,
    pub snapshot_changed: bool,
    pub scorecard_diffs: Vec<ScorecardSuiteScorecardDiff>,
    pub changed: bool,
}

pub fn diff_scorecard_suite_artifacts(
    spec: &ScorecardSuiteResultArtifactDiffSpec,
) -> Result<ScorecardSuiteDiffArtifact, ScorecardSuiteDiffError> {
    if spec.schema_version != 1 {
        return Err(ScorecardSuiteDiffError::UnsupportedSchemaVersion(
            spec.schema_version,
        ));
    }

    let passed_changed = spec.a.passed != spec.b.passed;
    let registry_hash_changed = spec.a.registry_hash != spec.b.registry_hash;
    let suite_hash_changed = spec.a.suite_hash != spec.b.suite_hash;
    let snapshot_changed = hash_json(&spec.a.snapshot)? != hash_json(&spec.b.snapshot)?;
    let scorecard_diffs = diff_scorecards(&spec.a, &spec.b)?;
    let changed = passed_changed
        || registry_hash_changed
        || suite_hash_changed
        || snapshot_changed
        || scorecard_diffs.iter().any(|d| d.changed);

    Ok(ScorecardSuiteDiffArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        diff_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        a: spec.a.clone(),
        b: spec.b.clone(),
        passed_changed,
        registry_hash_changed,
        suite_hash_changed,
        snapshot_changed,
        scorecard_diffs,
        changed,
    })
}
