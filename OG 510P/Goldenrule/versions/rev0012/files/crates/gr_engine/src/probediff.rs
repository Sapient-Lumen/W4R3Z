use crate::probe::{
    MatchupMeanStats, ProbeMatchupResult, ProbeResultArtifact, ProbeSuiteResultArtifact,
};
use serde::{Deserialize, Serialize};
use thiserror::Error;

fn default_schema_version() -> u32 {
    1
}

#[derive(Debug, Error)]
pub enum ProbeDiffError {
    #[error("probe diff schema_version {0} is unsupported")]
    UnsupportedSchemaVersion(u32),
    #[error("invalid value: {0}")]
    InvalidValue(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProbeResultArtifactDiffSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub a: ProbeResultArtifact,
    pub b: ProbeResultArtifact,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProbeSuiteResultArtifactDiffSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub a: ProbeSuiteResultArtifact,
    pub b: ProbeSuiteResultArtifact,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProbeMeanDelta {
    pub avg_payoff_a: f64,
    pub avg_payoff_b: f64,
    pub coop_rate_a: f64,
    pub coop_rate_b: f64,
    pub mutual_coop_rate: f64,
    pub mutual_defect_rate: f64,
}

fn mean_delta(a: &MatchupMeanStats, b: &MatchupMeanStats) -> ProbeMeanDelta {
    ProbeMeanDelta {
        avg_payoff_a: b.avg_payoff_a - a.avg_payoff_a,
        avg_payoff_b: b.avg_payoff_b - a.avg_payoff_b,
        coop_rate_a: b.coop_rate_a - a.coop_rate_a,
        coop_rate_b: b.coop_rate_b - a.coop_rate_b,
        mutual_coop_rate: b.mutual_coop_rate - a.mutual_coop_rate,
        mutual_defect_rate: b.mutual_defect_rate - a.mutual_defect_rate,
    }
}

fn mean_changed(a: &MatchupMeanStats, b: &MatchupMeanStats) -> bool {
    a.avg_payoff_a != b.avg_payoff_a
        || a.avg_payoff_b != b.avg_payoff_b
        || a.coop_rate_a != b.coop_rate_a
        || a.coop_rate_b != b.coop_rate_b
        || a.mutual_coop_rate != b.mutual_coop_rate
        || a.mutual_defect_rate != b.mutual_defect_rate
}

fn assertions_hash(matchup: &ProbeMatchupResult) -> Result<String, ProbeDiffError> {
    let canonical = serde_json::to_vec(&matchup.assertions)
        .map_err(|e| ProbeDiffError::InvalidValue(e.to_string()))?;
    Ok(crate::util::sha256_hex(&canonical))
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProbeMatchupDiff {
    pub id: String,
    pub kind: String, // added|removed|changed|unchanged
    pub changed: bool,
    pub a_passed: Option<bool>,
    pub b_passed: Option<bool>,
    pub passed_changed: bool,
    pub a_replications: Option<u32>,
    pub b_replications: Option<u32>,
    pub replications_changed: bool,
    pub a_rounds_per_replication: Option<u32>,
    pub b_rounds_per_replication: Option<u32>,
    pub rounds_per_replication_changed: bool,
    pub a_rounds_min: Option<u32>,
    pub b_rounds_min: Option<u32>,
    pub rounds_min_changed: bool,
    pub a_rounds_max: Option<u32>,
    pub b_rounds_max: Option<u32>,
    pub rounds_max_changed: bool,
    pub a_rounds_mean: Option<f64>,
    pub b_rounds_mean: Option<f64>,
    pub rounds_mean_changed: bool,
    pub mean_changed: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mean_deltas: Option<ProbeMeanDelta>,
    pub assertions_changed: bool,
}

fn diff_matchups(
    a: &ProbeResultArtifact,
    b: &ProbeResultArtifact,
) -> Result<Vec<ProbeMatchupDiff>, ProbeDiffError> {
    let mut a_map = std::collections::BTreeMap::new();
    for m in &a.matchups {
        a_map.insert(m.id.clone(), m);
    }
    let mut b_map = std::collections::BTreeMap::new();
    for m in &b.matchups {
        b_map.insert(m.id.clone(), m);
    }

    let ids = a_map
        .keys()
        .chain(b_map.keys())
        .cloned()
        .collect::<std::collections::BTreeSet<_>>();

    let mut out = Vec::with_capacity(ids.len());
    for id in ids.iter() {
        match (a_map.get(id), b_map.get(id)) {
            (Some(am), Some(bm)) => {
                let passed_changed = am.passed != bm.passed;
                let replications_changed = am.replications != bm.replications;
                let rounds_per_replication_changed =
                    am.rounds_per_replication != bm.rounds_per_replication;
                let rounds_min_changed = am.rounds_min != bm.rounds_min;
                let rounds_max_changed = am.rounds_max != bm.rounds_max;
                let rounds_mean_changed = am.rounds_mean != bm.rounds_mean;
                let mean_changed = mean_changed(&am.mean, &bm.mean);
                let mean_deltas = if mean_changed {
                    Some(mean_delta(&am.mean, &bm.mean))
                } else {
                    None
                };
                let assertions_changed = assertions_hash(am)? != assertions_hash(bm)?;
                let changed = passed_changed
                    || replications_changed
                    || rounds_per_replication_changed
                    || rounds_min_changed
                    || rounds_max_changed
                    || rounds_mean_changed
                    || mean_changed
                    || assertions_changed;
                out.push(ProbeMatchupDiff {
                    id: id.clone(),
                    kind: if changed { "changed" } else { "unchanged" }.to_string(),
                    changed,
                    a_passed: Some(am.passed),
                    b_passed: Some(bm.passed),
                    passed_changed,
                    a_replications: Some(am.replications),
                    b_replications: Some(bm.replications),
                    replications_changed,
                    a_rounds_per_replication: Some(am.rounds_per_replication),
                    b_rounds_per_replication: Some(bm.rounds_per_replication),
                    rounds_per_replication_changed,
                    a_rounds_min: am.rounds_min,
                    b_rounds_min: bm.rounds_min,
                    rounds_min_changed,
                    a_rounds_max: am.rounds_max,
                    b_rounds_max: bm.rounds_max,
                    rounds_max_changed,
                    a_rounds_mean: am.rounds_mean,
                    b_rounds_mean: bm.rounds_mean,
                    rounds_mean_changed,
                    mean_changed,
                    mean_deltas,
                    assertions_changed,
                });
            }
            (Some(am), None) => out.push(ProbeMatchupDiff {
                id: id.clone(),
                kind: "removed".to_string(),
                changed: true,
                a_passed: Some(am.passed),
                b_passed: None,
                passed_changed: true,
                a_replications: Some(am.replications),
                b_replications: None,
                replications_changed: true,
                a_rounds_per_replication: Some(am.rounds_per_replication),
                b_rounds_per_replication: None,
                rounds_per_replication_changed: true,
                a_rounds_min: am.rounds_min,
                b_rounds_min: None,
                rounds_min_changed: true,
                a_rounds_max: am.rounds_max,
                b_rounds_max: None,
                rounds_max_changed: true,
                a_rounds_mean: am.rounds_mean,
                b_rounds_mean: None,
                rounds_mean_changed: true,
                mean_changed: true,
                mean_deltas: None,
                assertions_changed: true,
            }),
            (None, Some(bm)) => out.push(ProbeMatchupDiff {
                id: id.clone(),
                kind: "added".to_string(),
                changed: true,
                a_passed: None,
                b_passed: Some(bm.passed),
                passed_changed: true,
                a_replications: None,
                b_replications: Some(bm.replications),
                replications_changed: true,
                a_rounds_per_replication: None,
                b_rounds_per_replication: Some(bm.rounds_per_replication),
                rounds_per_replication_changed: true,
                a_rounds_min: None,
                b_rounds_min: bm.rounds_min,
                rounds_min_changed: true,
                a_rounds_max: None,
                b_rounds_max: bm.rounds_max,
                rounds_max_changed: true,
                a_rounds_mean: None,
                b_rounds_mean: bm.rounds_mean,
                rounds_mean_changed: true,
                mean_changed: true,
                mean_deltas: None,
                assertions_changed: true,
            }),
            (None, None) => {}
        }
    }

    Ok(out)
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProbeResultDiffArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub diff_id: String,
    pub input_hash: String,
    pub a: ProbeResultArtifact,
    pub b: ProbeResultArtifact,
    pub probe_id_changed: bool,
    pub probe_hash_changed: bool,
    pub passed_changed: bool,
    pub matchup_diffs: Vec<ProbeMatchupDiff>,
    pub changed: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProbeSuiteProbeDiff {
    pub probe_id: String,
    pub kind: String, // added|removed|changed|unchanged
    pub changed: bool,
    pub a_passed: Option<bool>,
    pub b_passed: Option<bool>,
    pub passed_changed: bool,
    pub a_probe_hash: Option<String>,
    pub b_probe_hash: Option<String>,
    pub probe_hash_changed: bool,
}

fn diff_suite_probes(
    a: &ProbeSuiteResultArtifact,
    b: &ProbeSuiteResultArtifact,
) -> Vec<ProbeSuiteProbeDiff> {
    let mut a_map = std::collections::BTreeMap::new();
    for r in &a.probe_results {
        a_map.insert(r.probe_id.clone(), r);
    }
    let mut b_map = std::collections::BTreeMap::new();
    for r in &b.probe_results {
        b_map.insert(r.probe_id.clone(), r);
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
                let probe_hash_changed = ar.probe_hash != br.probe_hash;
                let changed = passed_changed || probe_hash_changed;
                out.push(ProbeSuiteProbeDiff {
                    probe_id: id,
                    kind: if changed { "changed" } else { "unchanged" }.to_string(),
                    changed,
                    a_passed: Some(ar.passed),
                    b_passed: Some(br.passed),
                    passed_changed,
                    a_probe_hash: Some(ar.probe_hash.clone()),
                    b_probe_hash: Some(br.probe_hash.clone()),
                    probe_hash_changed,
                });
            }
            (Some(ar), None) => out.push(ProbeSuiteProbeDiff {
                probe_id: id,
                kind: "removed".to_string(),
                changed: true,
                a_passed: Some(ar.passed),
                b_passed: None,
                passed_changed: true,
                a_probe_hash: Some(ar.probe_hash.clone()),
                b_probe_hash: None,
                probe_hash_changed: true,
            }),
            (None, Some(br)) => out.push(ProbeSuiteProbeDiff {
                probe_id: id,
                kind: "added".to_string(),
                changed: true,
                a_passed: None,
                b_passed: Some(br.passed),
                passed_changed: true,
                a_probe_hash: None,
                b_probe_hash: Some(br.probe_hash.clone()),
                probe_hash_changed: true,
            }),
            (None, None) => {}
        }
    }

    out
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProbeSuiteDiffArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub diff_id: String,
    pub input_hash: String,
    pub a: ProbeSuiteResultArtifact,
    pub b: ProbeSuiteResultArtifact,
    pub passed_changed: bool,
    pub registry_hash_changed: bool,
    pub suite_hash_changed: bool,
    pub probe_diffs: Vec<ProbeSuiteProbeDiff>,
    pub changed: bool,
}

pub fn diff_probe_artifacts(
    spec: &ProbeResultArtifactDiffSpec,
) -> Result<ProbeResultDiffArtifact, ProbeDiffError> {
    if spec.schema_version != 1 {
        return Err(ProbeDiffError::UnsupportedSchemaVersion(
            spec.schema_version,
        ));
    }

    let probe_id_changed = spec.a.probe_id != spec.b.probe_id;
    let probe_hash_changed = spec.a.probe_hash != spec.b.probe_hash;
    let passed_changed = spec.a.passed != spec.b.passed;
    let matchup_diffs = diff_matchups(&spec.a, &spec.b)?;
    let changed = probe_id_changed
        || probe_hash_changed
        || passed_changed
        || matchup_diffs.iter().any(|m| m.changed);

    Ok(ProbeResultDiffArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        diff_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        a: spec.a.clone(),
        b: spec.b.clone(),
        probe_id_changed,
        probe_hash_changed,
        passed_changed,
        matchup_diffs,
        changed,
    })
}

pub fn diff_probe_suite_artifacts(
    spec: &ProbeSuiteResultArtifactDiffSpec,
) -> Result<ProbeSuiteDiffArtifact, ProbeDiffError> {
    if spec.schema_version != 1 {
        return Err(ProbeDiffError::UnsupportedSchemaVersion(
            spec.schema_version,
        ));
    }

    let passed_changed = spec.a.passed != spec.b.passed;
    let registry_hash_changed = spec.a.registry_hash != spec.b.registry_hash;
    let suite_hash_changed = spec.a.suite_hash != spec.b.suite_hash;
    let probe_diffs = diff_suite_probes(&spec.a, &spec.b);
    let changed = passed_changed
        || registry_hash_changed
        || suite_hash_changed
        || probe_diffs.iter().any(|p| p.changed);

    Ok(ProbeSuiteDiffArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        diff_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        a: spec.a.clone(),
        b: spec.b.clone(),
        passed_changed,
        registry_hash_changed,
        suite_hash_changed,
        probe_diffs,
        changed,
    })
}
