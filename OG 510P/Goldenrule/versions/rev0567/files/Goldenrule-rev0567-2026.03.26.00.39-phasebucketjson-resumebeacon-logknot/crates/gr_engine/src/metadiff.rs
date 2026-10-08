use crate::metamorphic::{
    MetamorphicKind, MetamorphicResultArtifact, MetamorphicSuiteResultArtifact,
};
use serde::{Deserialize, Serialize};
use thiserror::Error;

fn default_schema_version() -> u32 {
    1
}

#[derive(Debug, Error)]
pub enum MetamorphicDiffError {
    #[error("metamorphic diff schema_version {0} is unsupported")]
    UnsupportedSchemaVersion(u32),
    #[error("invalid value: {0}")]
    InvalidValue(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetamorphicResultArtifactDiffSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub a: MetamorphicResultArtifact,
    pub b: MetamorphicResultArtifact,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetamorphicSuiteResultArtifactDiffSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub a: MetamorphicSuiteResultArtifact,
    pub b: MetamorphicSuiteResultArtifact,
}

fn hash_json<T: Serialize>(obj: &T) -> Result<String, MetamorphicDiffError> {
    let canonical =
        serde_json::to_vec(obj).map_err(|e| MetamorphicDiffError::InvalidValue(e.to_string()))?;
    Ok(crate::util::sha256_hex(&canonical))
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetamorphicCountsDelta {
    pub eligible_pairs: i64,
    pub skipped_matchups: i64,
    pub failures: i64,
    pub skipped: i64,
}

fn counts_delta(
    a: &MetamorphicResultArtifact,
    b: &MetamorphicResultArtifact,
) -> MetamorphicCountsDelta {
    MetamorphicCountsDelta {
        eligible_pairs: b.eligible_pairs as i64 - a.eligible_pairs as i64,
        skipped_matchups: b.skipped_matchups as i64 - a.skipped_matchups as i64,
        failures: b.failures.len() as i64 - a.failures.len() as i64,
        skipped: b.skipped.len() as i64 - a.skipped.len() as i64,
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetamorphicResultDiffArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub diff_id: String,
    pub input_hash: String,
    pub a: MetamorphicResultArtifact,
    pub b: MetamorphicResultArtifact,
    pub check_id_changed: bool,
    pub kind_changed: bool,
    pub passed_changed: bool,
    pub counts_deltas: MetamorphicCountsDelta,
    pub failures_changed: bool,
    pub skipped_changed: bool,
    pub changed: bool,
}

pub fn diff_metamorphic_artifacts(
    spec: &MetamorphicResultArtifactDiffSpec,
) -> Result<MetamorphicResultDiffArtifact, MetamorphicDiffError> {
    if spec.schema_version != 1 {
        return Err(MetamorphicDiffError::UnsupportedSchemaVersion(
            spec.schema_version,
        ));
    }

    let check_id_changed = spec.a.check_id != spec.b.check_id;
    let kind_changed = spec.a.kind != spec.b.kind;
    let passed_changed = spec.a.passed != spec.b.passed;
    let failures_changed = hash_json(&spec.a.failures)? != hash_json(&spec.b.failures)?;
    let skipped_changed = hash_json(&spec.a.skipped)? != hash_json(&spec.b.skipped)?;
    let counts_deltas = counts_delta(&spec.a, &spec.b);
    let changed = check_id_changed
        || kind_changed
        || passed_changed
        || failures_changed
        || skipped_changed
        || counts_deltas.eligible_pairs != 0
        || counts_deltas.skipped_matchups != 0
        || counts_deltas.failures != 0
        || counts_deltas.skipped != 0;

    Ok(MetamorphicResultDiffArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        diff_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        a: spec.a.clone(),
        b: spec.b.clone(),
        check_id_changed,
        kind_changed,
        passed_changed,
        counts_deltas,
        failures_changed,
        skipped_changed,
        changed,
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetamorphicSuiteCheckDiff {
    pub check_id: String,
    pub kind: String, // added|removed|changed|unchanged
    pub changed: bool,
    pub a_passed: Option<bool>,
    pub b_passed: Option<bool>,
    pub passed_changed: bool,
    pub a_kind: Option<MetamorphicKind>,
    pub b_kind: Option<MetamorphicKind>,
    pub kind_changed: bool,
    pub counts_deltas: MetamorphicCountsDelta,
}

fn diff_suite_checks(
    a: &MetamorphicSuiteResultArtifact,
    b: &MetamorphicSuiteResultArtifact,
) -> Result<Vec<MetamorphicSuiteCheckDiff>, MetamorphicDiffError> {
    let mut a_map = std::collections::BTreeMap::new();
    for r in &a.check_results {
        a_map.insert(r.check_id.clone(), r);
    }
    let mut b_map = std::collections::BTreeMap::new();
    for r in &b.check_results {
        b_map.insert(r.check_id.clone(), r);
    }

    let ids = a_map
        .keys()
        .chain(b_map.keys())
        .cloned()
        .collect::<std::collections::BTreeSet<_>>();

    let mut out = Vec::with_capacity(ids.len());
    for id in ids {
        match (a_map.get(&id), b_map.get(&id)) {
            (Some(ar), Some(br)) => {
                let passed_changed = ar.passed != br.passed;
                let kind_changed = ar.kind != br.kind;
                let counts_deltas = counts_delta(ar, br);
                let changed = passed_changed
                    || kind_changed
                    || counts_deltas.eligible_pairs != 0
                    || counts_deltas.skipped_matchups != 0
                    || counts_deltas.failures != 0
                    || counts_deltas.skipped != 0;
                out.push(MetamorphicSuiteCheckDiff {
                    check_id: id,
                    kind: if changed { "changed" } else { "unchanged" }.to_string(),
                    changed,
                    a_passed: Some(ar.passed),
                    b_passed: Some(br.passed),
                    passed_changed,
                    a_kind: Some(ar.kind),
                    b_kind: Some(br.kind),
                    kind_changed,
                    counts_deltas,
                });
            }
            (Some(ar), None) => out.push(MetamorphicSuiteCheckDiff {
                check_id: id,
                kind: "removed".to_string(),
                changed: true,
                a_passed: Some(ar.passed),
                b_passed: None,
                passed_changed: true,
                a_kind: Some(ar.kind),
                b_kind: None,
                kind_changed: true,
                counts_deltas: MetamorphicCountsDelta {
                    eligible_pairs: 0,
                    skipped_matchups: 0,
                    failures: 0,
                    skipped: 0,
                },
            }),
            (None, Some(br)) => out.push(MetamorphicSuiteCheckDiff {
                check_id: id,
                kind: "added".to_string(),
                changed: true,
                a_passed: None,
                b_passed: Some(br.passed),
                passed_changed: true,
                a_kind: None,
                b_kind: Some(br.kind),
                kind_changed: true,
                counts_deltas: MetamorphicCountsDelta {
                    eligible_pairs: 0,
                    skipped_matchups: 0,
                    failures: 0,
                    skipped: 0,
                },
            }),
            (None, None) => {}
        }
    }

    Ok(out)
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetamorphicSuiteDiffArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub diff_id: String,
    pub input_hash: String,
    pub a: MetamorphicSuiteResultArtifact,
    pub b: MetamorphicSuiteResultArtifact,
    pub passed_changed: bool,
    pub registry_hash_changed: bool,
    pub suite_hash_changed: bool,
    pub snapshot_changed: bool,
    pub check_diffs: Vec<MetamorphicSuiteCheckDiff>,
    pub changed: bool,
}

pub fn diff_metamorphic_suite_artifacts(
    spec: &MetamorphicSuiteResultArtifactDiffSpec,
) -> Result<MetamorphicSuiteDiffArtifact, MetamorphicDiffError> {
    if spec.schema_version != 1 {
        return Err(MetamorphicDiffError::UnsupportedSchemaVersion(
            spec.schema_version,
        ));
    }

    let passed_changed = spec.a.passed != spec.b.passed;
    let registry_hash_changed = spec.a.registry_hash != spec.b.registry_hash;
    let suite_hash_changed = spec.a.suite_hash != spec.b.suite_hash;
    let snapshot_changed = hash_json(&spec.a.snapshot)? != hash_json(&spec.b.snapshot)?;
    let check_diffs = diff_suite_checks(&spec.a, &spec.b)?;
    let changed = passed_changed
        || registry_hash_changed
        || suite_hash_changed
        || snapshot_changed
        || check_diffs.iter().any(|d| d.changed);

    Ok(MetamorphicSuiteDiffArtifact {
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
        check_diffs,
        changed,
    })
}
