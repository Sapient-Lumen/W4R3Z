use crate::spec::Action;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SeedStreams {
    pub match_seed: u64,
    pub decision_a: u64,
    pub decision_b: u64,
    pub impl_a: u64,
    pub impl_b: u64,
    pub obs_a: u64,
    pub obs_b: u64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub termination: Option<u64>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct RoundTrace {
    pub round: u32,
    pub a_intended: Action,
    pub b_intended: Action,
    pub a_signal: crate::spec::Signal,
    pub b_signal: crate::spec::Signal,
    pub a_executed: Action,
    pub b_executed: Action,
    pub a_observed_opp: Action,
    pub b_observed_opp: Action,
    pub a_observed_signal: crate::spec::Signal,
    pub b_observed_signal: crate::spec::Signal,
    pub payoff_a: f64,
    pub payoff_b: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub state_a: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub state_b: Option<String>,
    pub standing_a: f64,
    pub standing_b: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MatchStats {
    pub rounds: u32,
    pub total_payoff_a: f64,
    pub total_payoff_b: f64,
    pub avg_payoff_a: f64,
    pub avg_payoff_b: f64,
    pub coop_rate_a: f64,
    pub coop_rate_b: f64,
    pub mutual_coop_rate: f64,
    pub mutual_defect_rate: f64,
    pub payoff_diff: f64,  // (avg_payoff_a - avg_payoff_b).abs()
    pub legibility_a: f64, // P(predicted action == actual action)
    pub legibility_b: f64,
    pub honesty_a: f64, // P(action matches prior signal)
    pub honesty_b: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MatchArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub task_id: String,
    pub input_hash: String,
    pub world_id: String,
    pub world_seed: u64,
    pub strategy_a_id: String,
    pub strategy_b_id: String,
    pub match_seed: u64,
    pub seed_streams: SeedStreams,
    pub stats: MatchStats,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub trace: Option<Vec<RoundTrace>>,
}
