use crate::probe::{run_probe, ProbeResultArtifact, ProbeRunError, ProbeSpec};
use crate::spec::TerminationRuleSpec;
use serde::{Deserialize, Serialize};
use thiserror::Error;

fn default_schema_version() -> u32 {
    1
}

#[derive(Debug, Error)]
pub enum ShrinkError {
    #[error("shrink schema_version {0} is unsupported")]
    UnsupportedSchemaVersion(u32),
    #[error(transparent)]
    ProbeRun(#[from] ProbeRunError),
    #[error("probe does not fail at the original rounds; nothing to shrink")]
    ProbeDoesNotFail,
    #[error("unsupported termination for shrinker: {0}")]
    UnsupportedTermination(String),
    #[error("max_scan_rounds {max_scan_rounds} is less than original rounds {original_rounds}")]
    ScanLimitTooSmall {
        max_scan_rounds: u32,
        original_rounds: u32,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShrinkProbeRoundsSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub probe: ProbeSpec,
    #[serde(default = "default_max_scan_rounds")]
    pub max_scan_rounds: u32,
}

fn default_max_scan_rounds() -> u32 {
    250
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShrinkProbeRoundsArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub shrink_id: String,
    pub input_hash: String,
    pub original_rounds: u32,
    pub shrunk_rounds: u32,
    pub original_result: ProbeResultArtifact,
    pub shrunk_result: ProbeResultArtifact,
    pub shrunk_probe: ProbeSpec,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShrinkProbeMatchupsSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub probe: ProbeSpec,
    #[serde(default)]
    pub try_remove_failing_matchups: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShrinkProbeMatchupsArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub shrink_id: String,
    pub input_hash: String,
    pub original_result: ProbeResultArtifact,
    pub shrunk_result: ProbeResultArtifact,
    pub shrunk_probe: ProbeSpec,
    pub kept_matchup_ids: Vec<String>,
    pub removed_matchup_ids: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShrinkProbeReplicationsSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub probe: ProbeSpec,
    #[serde(default)]
    pub matchup_id: Option<String>,
    #[serde(default = "default_max_scan_replications")]
    pub max_scan_replications: u32,
}

fn default_max_scan_replications() -> u32 {
    50
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShrinkProbeReplicationsArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub shrink_id: String,
    pub input_hash: String,
    pub target_matchup_id: String,
    pub original_replications: u32,
    pub shrunk_replications: u32,
    pub original_result: ProbeResultArtifact,
    pub shrunk_result: ProbeResultArtifact,
    pub shrunk_probe: ProbeSpec,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShrinkProbePipelineSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub probe: ProbeSpec,
    #[serde(default)]
    pub try_remove_failing_matchups: bool,
    #[serde(default = "default_max_scan_rounds")]
    pub max_scan_rounds: u32,
    #[serde(default)]
    pub matchup_id: Option<String>,
    #[serde(default = "default_max_scan_replications")]
    pub max_scan_replications: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShrinkProbePipelineArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub shrink_id: String,
    pub input_hash: String,
    pub original_result: ProbeResultArtifact,
    pub matchups: ShrinkProbeMatchupsArtifact,
    pub rounds: ShrinkProbeRoundsArtifact,
    pub replications: ShrinkProbeReplicationsArtifact,
    pub final_result: ProbeResultArtifact,
    pub final_probe: ProbeSpec,
}

fn get_rounds(probe: &ProbeSpec) -> Result<u32, ShrinkError> {
    match probe.world.termination {
        TerminationRuleSpec::Fixed { rounds } => Ok(rounds),
        TerminationRuleSpec::Geometric { max_rounds, .. } => Ok(max_rounds),
    }
}

fn with_rounds(mut probe: ProbeSpec, template: &TerminationRuleSpec, rounds: u32) -> ProbeSpec {
    probe.world.termination = match template {
        TerminationRuleSpec::Fixed { .. } => TerminationRuleSpec::Fixed { rounds },
        TerminationRuleSpec::Geometric { delta, .. } => TerminationRuleSpec::Geometric {
            delta: *delta,
            max_rounds: rounds,
        },
    };
    probe
}

pub fn shrink_probe_rounds(
    spec: &ShrinkProbeRoundsSpec,
) -> Result<ShrinkProbeRoundsArtifact, ShrinkError> {
    if spec.schema_version != 1 {
        return Err(ShrinkError::UnsupportedSchemaVersion(spec.schema_version));
    }
    let original_rounds = get_rounds(&spec.probe)?;
    if original_rounds == 0 {
        return Err(ShrinkError::ProbeDoesNotFail);
    }
    if original_rounds > spec.max_scan_rounds {
        return Err(ShrinkError::ScanLimitTooSmall {
            max_scan_rounds: spec.max_scan_rounds,
            original_rounds,
        });
    }

    let original_result = run_probe(&spec.probe)?;
    if original_result.passed {
        return Err(ShrinkError::ProbeDoesNotFail);
    }

    let mut best_rounds = original_rounds;
    let mut best_probe = spec.probe.clone();
    let mut best_result = original_result.clone();

    for r in 1..=original_rounds {
        let candidate_probe = with_rounds(spec.probe.clone(), &spec.probe.world.termination, r);
        let candidate_result = run_probe(&candidate_probe)?;
        if !candidate_result.passed {
            best_rounds = r;
            best_probe = candidate_probe;
            best_result = candidate_result;
            break;
        }
    }

    Ok(ShrinkProbeRoundsArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        shrink_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        original_rounds,
        shrunk_rounds: best_rounds,
        original_result,
        shrunk_result: best_result,
        shrunk_probe: best_probe,
    })
}

pub fn shrink_probe_matchups(
    spec: &ShrinkProbeMatchupsSpec,
) -> Result<ShrinkProbeMatchupsArtifact, ShrinkError> {
    if spec.schema_version != 1 {
        return Err(ShrinkError::UnsupportedSchemaVersion(spec.schema_version));
    }

    let original_result = run_probe(&spec.probe)?;
    if original_result.passed {
        return Err(ShrinkError::ProbeDoesNotFail);
    }

    let mut shrunk_probe = spec.probe.clone();
    let mut shrunk_result = original_result.clone();

    let mut removed = Vec::new();

    // Greedy minimization: attempt to remove matchups one-by-one in a deterministic order.
    // By default we remove passing matchups only; optionally we also try removing failing ones.
    loop {
        if shrunk_probe.matchups.len() <= 1 {
            break;
        }

        let mut candidate_ids = shrunk_result
            .matchups
            .iter()
            .filter(|m| spec.try_remove_failing_matchups || m.passed)
            .map(|m| m.id.clone())
            .collect::<Vec<_>>();
        candidate_ids.sort();

        let mut removed_any = false;
        for id in candidate_ids {
            if shrunk_probe.matchups.len() <= 1 {
                break;
            }
            let mut candidate_probe = shrunk_probe.clone();
            candidate_probe.matchups = candidate_probe
                .matchups
                .into_iter()
                .filter(|m| m.id != id)
                .collect();

            let candidate_result = run_probe(&candidate_probe)?;
            if !candidate_result.passed {
                shrunk_probe = candidate_probe;
                shrunk_result = candidate_result;
                removed.push(id);
                removed_any = true;
                break;
            }
        }

        if !removed_any {
            break;
        }
    }

    let mut kept_matchup_ids = shrunk_probe
        .matchups
        .iter()
        .map(|m| m.id.clone())
        .collect::<Vec<_>>();
    kept_matchup_ids.sort();
    removed.sort();

    Ok(ShrinkProbeMatchupsArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        shrink_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        original_result,
        shrunk_result,
        shrunk_probe,
        kept_matchup_ids,
        removed_matchup_ids: removed,
    })
}

pub fn shrink_probe_replications(
    spec: &ShrinkProbeReplicationsSpec,
) -> Result<ShrinkProbeReplicationsArtifact, ShrinkError> {
    if spec.schema_version != 1 {
        return Err(ShrinkError::UnsupportedSchemaVersion(spec.schema_version));
    }

    let original_result = run_probe(&spec.probe)?;
    if original_result.passed {
        return Err(ShrinkError::ProbeDoesNotFail);
    }

    let target_matchup_id = match &spec.matchup_id {
        Some(id) => id.clone(),
        None => original_result
            .matchups
            .iter()
            .find(|m| !m.passed)
            .map(|m| m.id.clone())
            .ok_or(ShrinkError::ProbeDoesNotFail)?,
    };

    let original_matchup = spec
        .probe
        .matchups
        .iter()
        .find(|m| m.id == target_matchup_id)
        .ok_or(ShrinkError::ProbeDoesNotFail)?;

    let original_replications = original_matchup.replications;
    if original_replications == 0 {
        return Err(ShrinkError::ProbeDoesNotFail);
    }
    let scan_limit = spec.max_scan_replications.min(original_replications).max(1);

    let mut best_replications = original_replications;
    let mut best_probe = spec.probe.clone();
    let mut best_result = original_result.clone();

    for r in 1..=scan_limit {
        let mut candidate_probe = spec.probe.clone();
        for m in &mut candidate_probe.matchups {
            if m.id == target_matchup_id {
                m.replications = r;
            }
        }

        let candidate_result = run_probe(&candidate_probe)?;
        if !candidate_result.passed {
            best_replications = r;
            best_probe = candidate_probe;
            best_result = candidate_result;
            break;
        }
    }

    Ok(ShrinkProbeReplicationsArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        shrink_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        target_matchup_id,
        original_replications,
        shrunk_replications: best_replications,
        original_result,
        shrunk_result: best_result,
        shrunk_probe: best_probe,
    })
}

pub fn shrink_probe_pipeline(
    spec: &ShrinkProbePipelineSpec,
) -> Result<ShrinkProbePipelineArtifact, ShrinkError> {
    if spec.schema_version != 1 {
        return Err(ShrinkError::UnsupportedSchemaVersion(spec.schema_version));
    }

    let original_result = run_probe(&spec.probe)?;
    if original_result.passed {
        return Err(ShrinkError::ProbeDoesNotFail);
    }

    let matchups_spec = ShrinkProbeMatchupsSpec {
        schema_version: 1,
        id: format!("{}__matchups", spec.id),
        description: String::new(),
        probe: spec.probe.clone(),
        try_remove_failing_matchups: spec.try_remove_failing_matchups,
    };
    let matchups = shrink_probe_matchups(&matchups_spec)?;

    let rounds_spec = ShrinkProbeRoundsSpec {
        schema_version: 1,
        id: format!("{}__rounds", spec.id),
        description: String::new(),
        probe: matchups.shrunk_probe.clone(),
        max_scan_rounds: spec.max_scan_rounds,
    };
    let rounds = shrink_probe_rounds(&rounds_spec)?;

    let replications_spec = ShrinkProbeReplicationsSpec {
        schema_version: 1,
        id: format!("{}__replications", spec.id),
        description: String::new(),
        probe: rounds.shrunk_probe.clone(),
        matchup_id: spec.matchup_id.clone(),
        max_scan_replications: spec.max_scan_replications,
    };
    let replications = shrink_probe_replications(&replications_spec)?;

    Ok(ShrinkProbePipelineArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        shrink_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        original_result,
        matchups: matchups.clone(),
        rounds: rounds.clone(),
        replications: replications.clone(),
        final_result: replications.shrunk_result.clone(),
        final_probe: replications.shrunk_probe.clone(),
    })
}
