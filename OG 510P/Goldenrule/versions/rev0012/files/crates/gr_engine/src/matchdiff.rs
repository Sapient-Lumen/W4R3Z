use crate::artifact::{MatchArtifact, MatchStats, RoundTrace, SeedStreams};
use serde::{Deserialize, Serialize};
use thiserror::Error;

fn default_schema_version() -> u32 {
    1
}

#[derive(Debug, Error)]
pub enum MatchDiffError {
    #[error("match diff schema_version {0} is unsupported")]
    UnsupportedSchemaVersion(u32),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MatchArtifactDiffSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub a: MatchArtifact,
    pub b: MatchArtifact,
}

fn stats_changed(a: &MatchStats, b: &MatchStats) -> bool {
    a.rounds != b.rounds
        || a.total_payoff_a != b.total_payoff_a
        || a.total_payoff_b != b.total_payoff_b
        || a.avg_payoff_a != b.avg_payoff_a
        || a.avg_payoff_b != b.avg_payoff_b
        || a.coop_rate_a != b.coop_rate_a
        || a.coop_rate_b != b.coop_rate_b
        || a.mutual_coop_rate != b.mutual_coop_rate
        || a.mutual_defect_rate != b.mutual_defect_rate
}

fn seed_streams_changed(a: &SeedStreams, b: &SeedStreams) -> bool {
    a.match_seed != b.match_seed
        || a.decision_a != b.decision_a
        || a.decision_b != b.decision_b
        || a.impl_a != b.impl_a
        || a.impl_b != b.impl_b
        || a.obs_a != b.obs_a
        || a.obs_b != b.obs_b
        || a.termination != b.termination
}

fn trace_changed_and_first_diff_round(
    a: &Option<Vec<RoundTrace>>,
    b: &Option<Vec<RoundTrace>>,
) -> (bool, Option<u32>) {
    match (a, b) {
        (None, None) => (false, None),
        (Some(_), None) | (None, Some(_)) => (true, None),
        (Some(at), Some(bt)) => {
            if at.len() != bt.len() {
                return (true, None);
            }
            for (ra, rb) in at.iter().zip(bt.iter()) {
                if ra != rb {
                    return (true, Some(ra.round));
                }
            }
            (false, None)
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MatchDiffArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub diff_id: String,
    pub input_hash: String,
    pub a: MatchArtifact,
    pub b: MatchArtifact,
    pub task_id_changed: bool,
    pub input_hash_changed: bool,
    pub world_id_changed: bool,
    pub world_seed_changed: bool,
    pub strategy_a_id_changed: bool,
    pub strategy_b_id_changed: bool,
    pub match_seed_changed: bool,
    pub seed_streams_changed: bool,
    pub stats_changed: bool,
    pub trace_changed: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub first_diff_round: Option<u32>,
    pub changed: bool,
}

pub fn diff_match_artifacts(
    spec: &MatchArtifactDiffSpec,
) -> Result<MatchDiffArtifact, MatchDiffError> {
    if spec.schema_version != 1 {
        return Err(MatchDiffError::UnsupportedSchemaVersion(
            spec.schema_version,
        ));
    }

    let task_id_changed = spec.a.task_id != spec.b.task_id;
    let input_hash_changed = spec.a.input_hash != spec.b.input_hash;
    let world_id_changed = spec.a.world_id != spec.b.world_id;
    let world_seed_changed = spec.a.world_seed != spec.b.world_seed;
    let strategy_a_id_changed = spec.a.strategy_a_id != spec.b.strategy_a_id;
    let strategy_b_id_changed = spec.a.strategy_b_id != spec.b.strategy_b_id;
    let match_seed_changed = spec.a.match_seed != spec.b.match_seed;
    let seed_streams_changed = seed_streams_changed(&spec.a.seed_streams, &spec.b.seed_streams);
    let stats_changed = stats_changed(&spec.a.stats, &spec.b.stats);
    let (trace_changed, first_diff_round) =
        trace_changed_and_first_diff_round(&spec.a.trace, &spec.b.trace);

    let changed = task_id_changed
        || input_hash_changed
        || world_id_changed
        || world_seed_changed
        || strategy_a_id_changed
        || strategy_b_id_changed
        || match_seed_changed
        || seed_streams_changed
        || stats_changed
        || trace_changed;

    Ok(MatchDiffArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        diff_id: spec.id.clone(),
        input_hash: String::new(), // filled by CLI
        a: spec.a.clone(),
        b: spec.b.clone(),
        task_id_changed,
        input_hash_changed,
        world_id_changed,
        world_seed_changed,
        strategy_a_id_changed,
        strategy_b_id_changed,
        match_seed_changed,
        seed_streams_changed,
        stats_changed,
        trace_changed,
        first_diff_round,
        changed,
    })
}
