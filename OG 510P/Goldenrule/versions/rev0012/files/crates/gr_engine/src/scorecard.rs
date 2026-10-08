use crate::metamorphic::MetamorphicSuiteResultArtifact;
use crate::probe::ProbeSuiteResultArtifact;
use crate::run_snapshot::SnapshotRunArtifact;
use crate::snapshot::SnapshotSummary;
use serde::{Deserialize, Serialize};
use thiserror::Error;

fn default_schema_version() -> u32 {
    1
}

fn default_require_probe_suite() -> bool {
    true
}

fn default_require_metamorphic_suite() -> bool {
    true
}

#[derive(Debug, Error)]
pub enum ScorecardError {
    #[error("scorecard schema_version {0} is unsupported")]
    UnsupportedSchemaVersion(u32),
    #[error("invalid value: {0}")]
    InvalidValue(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScorecardCard {
    pub id: String,
    pub version: String,
    pub intent: String,
    #[serde(default)]
    pub non_goals: Vec<String>,
    #[serde(default)]
    pub lenses: Vec<String>,
    #[serde(default)]
    pub known_risks: Vec<String>,
    #[serde(default)]
    pub required_holdouts: Vec<String>,
    #[serde(default)]
    pub required_metamorphic: Vec<String>,
    #[serde(default)]
    pub appropriate_contexts: Vec<String>,
    #[serde(default)]
    pub inappropriate_contexts: Vec<String>,
    #[serde(default)]
    pub changelog: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScorecardDef {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub card: ScorecardCard,
    #[serde(default)]
    pub gates: ScorecardGateSpec,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScorecardGateSpec {
    #[serde(default = "default_require_probe_suite")]
    pub require_probe_suite: bool,
    #[serde(default = "default_require_metamorphic_suite")]
    pub require_metamorphic_suite: bool,
    #[serde(default)]
    pub fail_on_hash_mismatch: bool,
}

impl Default for ScorecardGateSpec {
    fn default() -> Self {
        Self {
            require_probe_suite: default_require_probe_suite(),
            require_metamorphic_suite: default_require_metamorphic_suite(),
            fail_on_hash_mismatch: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScorecardSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub card: ScorecardCard,
    #[serde(default)]
    pub gates: ScorecardGateSpec,
    #[serde(default)]
    pub snapshot: Option<SnapshotSummary>,
    #[serde(default)]
    pub snapshot_run: Option<SnapshotRunArtifact>,
    #[serde(default)]
    pub probe_suite: Option<ProbeSuiteResultArtifact>,
    #[serde(default)]
    pub metamorphic_suite: Option<MetamorphicSuiteResultArtifact>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScorecardBanner {
    pub headline: String,
    pub passed: bool,
    pub probe_suite_passed: Option<bool>,
    pub probes_total: u32,
    pub probes_failed: u32,
    pub metamorphic_suite_passed: Option<bool>,
    pub checks_total: u32,
    pub checks_failed: u32,
    pub checks_skipped_matchups: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScorecardResultArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub scorecard_id: String,
    pub input_hash: String,
    pub card: ScorecardCard,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub snapshot: Option<SnapshotSummary>,
    pub passed: bool,
    pub banner: ScorecardBanner,
    #[serde(default)]
    pub warnings: Vec<String>,
}

fn summarize_snapshot_run(run: &SnapshotRunArtifact) -> SnapshotSummary {
    crate::snapshot::summarize_snapshot(&run.snapshot)
}

fn validate_card(card: &ScorecardCard) -> Result<(), ScorecardError> {
    if card.id.trim().is_empty() {
        return Err(ScorecardError::InvalidValue(
            "card.id must be non-empty".to_string(),
        ));
    }
    if card.version.trim().is_empty() {
        return Err(ScorecardError::InvalidValue(
            "card.version must be non-empty".to_string(),
        ));
    }
    if card.intent.trim().is_empty() {
        return Err(ScorecardError::InvalidValue(
            "card.intent must be non-empty".to_string(),
        ));
    }
    Ok(())
}

pub fn validate_scorecard_def(def: &ScorecardDef) -> Result<(), ScorecardError> {
    if def.schema_version != 1 {
        return Err(ScorecardError::UnsupportedSchemaVersion(def.schema_version));
    }
    if def.id.trim().is_empty() {
        return Err(ScorecardError::InvalidValue(
            "scorecard id must be non-empty".to_string(),
        ));
    }
    validate_card(&def.card)?;
    Ok(())
}

pub fn scorecard_spec_from_def_and_snapshot_run(
    def: &ScorecardDef,
    snapshot_run: &SnapshotRunArtifact,
) -> ScorecardSpec {
    let snapshot = summarize_snapshot_run(snapshot_run);
    ScorecardSpec {
        schema_version: 1,
        id: def.id.clone(),
        description: def.description.clone(),
        card: def.card.clone(),
        gates: def.gates.clone(),
        snapshot: Some(snapshot),
        snapshot_run: None,
        probe_suite: snapshot_run.probe_suite.clone(),
        metamorphic_suite: snapshot_run.metamorphic_suite.clone(),
    }
}

pub fn run_scorecard_def_on_snapshot_run(
    def: &ScorecardDef,
    snapshot_run: &SnapshotRunArtifact,
) -> Result<ScorecardResultArtifact, ScorecardError> {
    let spec = scorecard_spec_from_def_and_snapshot_run(def, snapshot_run);
    run_scorecard(&spec)
}

fn extract_inputs(
    spec: &ScorecardSpec,
) -> (
    Option<SnapshotSummary>,
    Option<ProbeSuiteResultArtifact>,
    Option<MetamorphicSuiteResultArtifact>,
) {
    if let Some(run) = &spec.snapshot_run {
        let snapshot = Some(crate::snapshot::summarize_snapshot(&run.snapshot));
        let probe_suite = run.probe_suite.clone();
        let metamorphic_suite = run.metamorphic_suite.clone();
        return (snapshot, probe_suite, metamorphic_suite);
    }
    (
        spec.snapshot.clone(),
        spec.probe_suite.clone(),
        spec.metamorphic_suite.clone(),
    )
}

fn maybe_check_hash_mismatch_probe_suite(
    snapshot: &Option<SnapshotSummary>,
    suite: &ProbeSuiteResultArtifact,
    warnings: &mut Vec<String>,
) -> bool {
    let Some(snap) = snapshot else {
        return false;
    };
    let mut mismatch = false;
    if let Some(r) = &snap.probe_registry {
        if r.hash != suite.registry_hash {
            warnings.push(format!(
                "probe_registry hash mismatch: snapshot {} vs suite {}",
                r.hash, suite.registry_hash
            ));
            mismatch = true;
        }
    }
    if let Some(s) = &snap.probe_suite {
        if s.hash != suite.suite_hash {
            warnings.push(format!(
                "probe_suite hash mismatch: snapshot {} vs suite {}",
                s.hash, suite.suite_hash
            ));
            mismatch = true;
        }
    }
    mismatch
}

fn maybe_check_hash_mismatch_metamorphic_suite(
    snapshot: &Option<SnapshotSummary>,
    suite: &MetamorphicSuiteResultArtifact,
    warnings: &mut Vec<String>,
) -> bool {
    let Some(snap) = snapshot else {
        return false;
    };
    let mut mismatch = false;
    if let Some(r) = &snap.metamorphic_registry {
        if r.hash != suite.registry_hash {
            warnings.push(format!(
                "metamorphic_registry hash mismatch: snapshot {} vs suite {}",
                r.hash, suite.registry_hash
            ));
            mismatch = true;
        }
    }
    if let Some(s) = &snap.metamorphic_suite {
        if s.hash != suite.suite_hash {
            warnings.push(format!(
                "metamorphic_suite hash mismatch: snapshot {} vs suite {}",
                s.hash, suite.suite_hash
            ));
            mismatch = true;
        }
    }
    mismatch
}

pub fn run_scorecard(spec: &ScorecardSpec) -> Result<ScorecardResultArtifact, ScorecardError> {
    if spec.schema_version != 1 {
        return Err(ScorecardError::UnsupportedSchemaVersion(
            spec.schema_version,
        ));
    }
    validate_card(&spec.card)?;

    let (snapshot, probe_suite, metamorphic_suite) = extract_inputs(spec);

    let mut warnings = Vec::new();
    let mut mismatch = false;

    let (probe_suite_passed, probes_total, probes_failed) = match &probe_suite {
        None => {
            if spec.gates.require_probe_suite {
                warnings.push("missing required probe_suite".to_string());
            }
            (None, 0, 0)
        }
        Some(r) => {
            mismatch |= maybe_check_hash_mismatch_probe_suite(&snapshot, r, &mut warnings);
            let probes_total = r.probe_results.len() as u32;
            let probes_failed = r.probe_results.iter().filter(|p| !p.passed).count() as u32;
            (Some(r.passed), probes_total, probes_failed)
        }
    };

    let (metamorphic_suite_passed, checks_total, checks_failed, checks_skipped_matchups) =
        match &metamorphic_suite {
            None => {
                if spec.gates.require_metamorphic_suite {
                    warnings.push("missing required metamorphic_suite".to_string());
                }
                (None, 0, 0, 0)
            }
            Some(r) => {
                mismatch |=
                    maybe_check_hash_mismatch_metamorphic_suite(&snapshot, r, &mut warnings);
                let checks_total = r.check_results.len() as u32;
                let checks_failed = r.check_results.iter().filter(|c| !c.passed).count() as u32;
                let checks_skipped_matchups = r
                    .check_results
                    .iter()
                    .map(|c| c.skipped_matchups)
                    .sum::<u32>();
                (
                    Some(r.passed),
                    checks_total,
                    checks_failed,
                    checks_skipped_matchups,
                )
            }
        };

    if mismatch && spec.gates.fail_on_hash_mismatch {
        warnings.push("hash mismatch marked scorecard as failed".to_string());
    }

    let passed = (!spec.gates.require_probe_suite || probe_suite_passed == Some(true))
        && (!spec.gates.require_metamorphic_suite || metamorphic_suite_passed == Some(true))
        && (!spec.gates.fail_on_hash_mismatch || !mismatch);

    let headline = format!(
        "{} (probes: {}/{}, metamorphic: {}/{})",
        if passed { "PASS" } else { "FAIL" },
        probes_total.saturating_sub(probes_failed),
        probes_total,
        checks_total.saturating_sub(checks_failed),
        checks_total
    );

    Ok(ScorecardResultArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        scorecard_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        card: spec.card.clone(),
        snapshot,
        passed,
        banner: ScorecardBanner {
            headline,
            passed,
            probe_suite_passed,
            probes_total,
            probes_failed,
            metamorphic_suite_passed,
            checks_total,
            checks_failed,
            checks_skipped_matchups,
        },
        warnings,
    })
}
