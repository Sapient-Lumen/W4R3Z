use crate::sim::SimError;
use crate::snapshot::SnapshotSummary;
use crate::spec::{NoiseModelSpec, StrategySpec, TaskSpec, TerminationRuleSpec, WorldSpec};
use serde::{Deserialize, Serialize};
use thiserror::Error;

fn default_schema_version() -> u32 {
    1
}

#[derive(Debug, Error)]
pub enum ProbeError {
    #[error("probe schema_version {0} is unsupported")]
    UnsupportedSchemaVersion(u32),
    #[error("invalid probability {0} (expected in [0,1])")]
    InvalidProbability(f64),
    #[error("invalid number {0} (expected finite)")]
    InvalidNumber(f64),
    #[error("invalid value: {0}")]
    InvalidValue(String),
    #[error("duplicate matchup id {0}")]
    DuplicateMatchupId(String),
    #[error("duplicate probe id {0}")]
    DuplicateProbeId(String),
    #[error("missing probe id {0}")]
    MissingProbeId(String),
}

#[derive(Debug, Error)]
pub enum ProbeRunError {
    #[error(transparent)]
    Probe(#[from] ProbeError),
    #[error(transparent)]
    Sim(#[from] SimError),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProbeSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub world: WorldSpec,
    pub matchups: Vec<ProbeMatchup>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProbeMatchup {
    pub id: String,
    pub strategy_a: StrategySpec,
    pub strategy_b: StrategySpec,
    #[serde(default = "default_replications")]
    pub replications: u32,
    #[serde(default)]
    pub seed_offset: u64,
    #[serde(default)]
    pub trace_rounds: u32,
    #[serde(default)]
    pub assertions: Vec<AssertionSpec>,
}

fn default_replications() -> u32 {
    1
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum AssertionSpec {
    AvgPayoffAAtLeast { min: f64 },
    AvgPayoffBAtLeast { min: f64 },
    CoopRateAAtLeast { min: f64 },
    CoopRateBAtLeast { min: f64 },
    MutualCoopRateAtLeast { min: f64 },
    MutualDefectRateAtMost { max: f64 },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProbeRegistrySpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub probes: Vec<ProbeSpec>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProbeSuiteSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub probe_ids: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExpandedProbe {
    pub probe_id: String,
    pub probe_schema_version: u32,
    pub probe_hash: String,
    pub tasks: Vec<TaskSpec>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProbeSuiteResultArtifact {
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
    pub probe_results: Vec<ProbeResultArtifact>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProbeResultArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub probe_id: String,
    pub probe_schema_version: u32,
    pub input_hash: String,
    pub probe_hash: String,
    pub passed: bool,
    pub matchups: Vec<ProbeMatchupResult>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProbeMatchupResult {
    pub id: String,
    pub replications: u32,
    pub rounds_per_replication: u32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rounds_min: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rounds_max: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rounds_mean: Option<f64>,
    pub mean: MatchupMeanStats,
    pub assertions: Vec<AssertionEval>,
    pub passed: bool,
    pub replications_detail: Vec<ReplicationResult>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReplicationResult {
    pub rep: u32,
    pub task_id: String,
    pub match_seed: u64,
    pub stats: crate::artifact::MatchStats,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub trace: Option<Vec<crate::artifact::RoundTrace>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MatchupMeanStats {
    pub avg_payoff_a: f64,
    pub avg_payoff_b: f64,
    pub coop_rate_a: f64,
    pub coop_rate_b: f64,
    pub mutual_coop_rate: f64,
    pub mutual_defect_rate: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AssertionEval {
    pub assertion: AssertionSpec,
    pub passed: bool,
    pub observed: f64,
}

fn validate_probability(p: f64) -> Result<(), ProbeError> {
    if !p.is_finite() {
        return Err(ProbeError::InvalidNumber(p));
    }
    if (0.0..=1.0).contains(&p) {
        Ok(())
    } else {
        Err(ProbeError::InvalidProbability(p))
    }
}

fn validate_finite(x: f64) -> Result<(), ProbeError> {
    if x.is_finite() {
        Ok(())
    } else {
        Err(ProbeError::InvalidNumber(x))
    }
}

fn validate_noise(noise: &NoiseModelSpec) -> Result<(), ProbeError> {
    match *noise {
        NoiseModelSpec::None => Ok(()),
        NoiseModelSpec::ImplementationFlip { p } => validate_probability(p),
        NoiseModelSpec::ObservationFlip { p } => validate_probability(p),
        NoiseModelSpec::Iid {
            p_implementation,
            p_observation,
        } => {
            validate_probability(p_implementation)?;
            validate_probability(p_observation)?;
            Ok(())
        }
        NoiseModelSpec::AsymmetricIid {
            p_implementation_a,
            p_implementation_b,
            p_observation_a,
            p_observation_b,
        } => {
            validate_probability(p_implementation_a)?;
            validate_probability(p_implementation_b)?;
            validate_probability(p_observation_a)?;
            validate_probability(p_observation_b)?;
            Ok(())
        }
    }
}

fn validate_termination(termination: &TerminationRuleSpec) -> Result<(), ProbeError> {
    match *termination {
        TerminationRuleSpec::Fixed { rounds } => {
            if rounds == 0 {
                Err(ProbeError::InvalidValue(
                    "termination rounds must be > 0".to_string(),
                ))
            } else {
                Ok(())
            }
        }
        TerminationRuleSpec::Geometric { delta, max_rounds } => {
            validate_probability(delta)?;
            if max_rounds == 0 {
                Err(ProbeError::InvalidValue(
                    "geometric max_rounds must be > 0".to_string(),
                ))
            } else {
                Ok(())
            }
        }
    }
}

pub fn validate_probe(probe: &ProbeSpec) -> Result<(), ProbeError> {
    if probe.schema_version != 1 {
        return Err(ProbeError::UnsupportedSchemaVersion(probe.schema_version));
    }

    validate_noise(&probe.world.noise)?;
    validate_termination(&probe.world.termination)?;

    let mut ids = std::collections::BTreeSet::new();
    for m in &probe.matchups {
        if !ids.insert(m.id.clone()) {
            return Err(ProbeError::DuplicateMatchupId(m.id.clone()));
        }
        if m.replications == 0 {
            return Err(ProbeError::InvalidValue(format!(
                "matchup {} has replications=0",
                m.id
            )));
        }
        for a in &m.assertions {
            match a {
                AssertionSpec::AvgPayoffAAtLeast { min } => validate_finite(*min)?,
                AssertionSpec::AvgPayoffBAtLeast { min } => validate_finite(*min)?,
                AssertionSpec::CoopRateAAtLeast { min }
                | AssertionSpec::CoopRateBAtLeast { min }
                | AssertionSpec::MutualCoopRateAtLeast { min } => validate_probability(*min)?,
                AssertionSpec::MutualDefectRateAtMost { max } => validate_probability(*max)?,
            }
        }
    }

    Ok(())
}

pub fn validate_probe_registry(reg: &ProbeRegistrySpec) -> Result<(), ProbeError> {
    if reg.schema_version != 1 {
        return Err(ProbeError::UnsupportedSchemaVersion(reg.schema_version));
    }
    let mut ids = std::collections::BTreeSet::new();
    for p in &reg.probes {
        if !ids.insert(p.id.clone()) {
            return Err(ProbeError::DuplicateProbeId(p.id.clone()));
        }
        validate_probe(p)?;
    }
    Ok(())
}

pub fn validate_probe_suite(suite: &ProbeSuiteSpec) -> Result<(), ProbeError> {
    if suite.schema_version != 1 {
        return Err(ProbeError::UnsupportedSchemaVersion(suite.schema_version));
    }
    if suite.probe_ids.is_empty() {
        return Err(ProbeError::InvalidValue(
            "suite probe_ids must be non-empty".to_string(),
        ));
    }
    Ok(())
}

fn find_probe<'a>(reg: &'a ProbeRegistrySpec, id: &str) -> Option<&'a ProbeSpec> {
    reg.probes.iter().find(|p| p.id == id)
}

pub fn run_probe_suite(
    reg: &ProbeRegistrySpec,
    suite: &ProbeSuiteSpec,
) -> Result<ProbeSuiteResultArtifact, ProbeRunError> {
    validate_probe_registry(reg)?;
    validate_probe_suite(suite)?;

    let registry_hash = {
        let canonical =
            serde_json::to_vec(reg).map_err(|e| ProbeError::InvalidValue(e.to_string()))?;
        crate::util::sha256_hex(&canonical)
    };
    let suite_hash = {
        let canonical =
            serde_json::to_vec(suite).map_err(|e| ProbeError::InvalidValue(e.to_string()))?;
        crate::util::sha256_hex(&canonical)
    };

    let mut probe_results = Vec::with_capacity(suite.probe_ids.len());
    for id in &suite.probe_ids {
        let probe = find_probe(reg, id).ok_or_else(|| ProbeError::MissingProbeId(id.clone()))?;
        let canonical =
            serde_json::to_vec(probe).map_err(|e| ProbeError::InvalidValue(e.to_string()))?;
        let input_hash = crate::util::sha256_hex(&canonical);

        let mut r = run_probe(probe)?;
        r.input_hash = input_hash;
        probe_results.push(r);
    }

    let passed = probe_results.iter().all(|r| r.passed);
    Ok(ProbeSuiteResultArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        registry_id: reg.id.clone(),
        suite_id: suite.id.clone(),
        input_hash: String::new(), // filled by CLI
        registry_hash,
        suite_hash,
        snapshot: None,
        passed,
        probe_results,
    })
}

pub fn run_probe_suite_with_snapshot(
    reg: &ProbeRegistrySpec,
    suite: &ProbeSuiteSpec,
    snapshot: SnapshotSummary,
) -> Result<ProbeSuiteResultArtifact, ProbeRunError> {
    let mut artifact = run_probe_suite(reg, suite)?;
    artifact.snapshot = Some(snapshot);
    Ok(artifact)
}

pub fn expand_probe(probe: &ProbeSpec) -> Result<ExpandedProbe, ProbeError> {
    validate_probe(probe)?;

    let probe_hash = {
        let canonical =
            serde_json::to_vec(probe).map_err(|e| ProbeError::InvalidValue(e.to_string()))?;
        crate::util::sha256_hex(&canonical)
    };

    let mut tasks = Vec::new();
    for matchup in &probe.matchups {
        for rep in 0..matchup.replications {
            let match_seed = probe
                .world
                .seed
                .wrapping_add(matchup.seed_offset)
                .wrapping_add(rep as u64);
            let mut task = TaskSpec::new(
                &format!("{}/{}__rep{}", probe.id, matchup.id, rep),
                probe.world.clone(),
                matchup.strategy_a.clone(),
                matchup.strategy_b.clone(),
                match_seed,
            );
            task.trace_rounds = matchup.trace_rounds;
            tasks.push(task);
        }
    }

    Ok(ExpandedProbe {
        probe_id: probe.id.clone(),
        probe_schema_version: probe.schema_version,
        probe_hash,
        tasks,
    })
}

fn mean(values: &[f64]) -> f64 {
    if values.is_empty() {
        return f64::NAN;
    }
    let s: f64 = values.iter().sum();
    s / (values.len() as f64)
}

fn mean_u32(values: &[u32]) -> Option<f64> {
    if values.is_empty() {
        return None;
    }
    let s: u64 = values.iter().map(|&x| x as u64).sum();
    Some((s as f64) / (values.len() as f64))
}

fn eval_assertion(a: &AssertionSpec, mean_stats: &MatchupMeanStats) -> AssertionEval {
    match a {
        AssertionSpec::AvgPayoffAAtLeast { min } => {
            let observed = mean_stats.avg_payoff_a;
            AssertionEval {
                assertion: a.clone(),
                passed: observed >= *min,
                observed,
            }
        }
        AssertionSpec::AvgPayoffBAtLeast { min } => {
            let observed = mean_stats.avg_payoff_b;
            AssertionEval {
                assertion: a.clone(),
                passed: observed >= *min,
                observed,
            }
        }
        AssertionSpec::CoopRateAAtLeast { min } => {
            let observed = mean_stats.coop_rate_a;
            AssertionEval {
                assertion: a.clone(),
                passed: observed >= *min,
                observed,
            }
        }
        AssertionSpec::CoopRateBAtLeast { min } => {
            let observed = mean_stats.coop_rate_b;
            AssertionEval {
                assertion: a.clone(),
                passed: observed >= *min,
                observed,
            }
        }
        AssertionSpec::MutualCoopRateAtLeast { min } => {
            let observed = mean_stats.mutual_coop_rate;
            AssertionEval {
                assertion: a.clone(),
                passed: observed >= *min,
                observed,
            }
        }
        AssertionSpec::MutualDefectRateAtMost { max } => {
            let observed = mean_stats.mutual_defect_rate;
            AssertionEval {
                assertion: a.clone(),
                passed: observed <= *max,
                observed,
            }
        }
    }
}

pub fn run_probe(probe: &ProbeSpec) -> Result<ProbeResultArtifact, ProbeRunError> {
    validate_probe(probe)?;
    let expanded = expand_probe(probe)?;

    let mut matchup_results = Vec::with_capacity(probe.matchups.len());

    for matchup in &probe.matchups {
        let mut replications_detail = Vec::with_capacity(matchup.replications as usize);
        let mut avg_a = Vec::with_capacity(matchup.replications as usize);
        let mut avg_b = Vec::with_capacity(matchup.replications as usize);
        let mut coop_a = Vec::with_capacity(matchup.replications as usize);
        let mut coop_b = Vec::with_capacity(matchup.replications as usize);
        let mut mutual_c = Vec::with_capacity(matchup.replications as usize);
        let mut mutual_d = Vec::with_capacity(matchup.replications as usize);

        for rep in 0..matchup.replications {
            let match_seed = probe
                .world
                .seed
                .wrapping_add(matchup.seed_offset)
                .wrapping_add(rep as u64);

            let mut task = TaskSpec::new(
                &format!("{}/{}__{}", probe.id, matchup.id, rep),
                probe.world.clone(),
                matchup.strategy_a.clone(),
                matchup.strategy_b.clone(),
                match_seed,
            );
            task.trace_rounds = matchup.trace_rounds;
            let artifact = crate::sim::run_match(&task)?;
            avg_a.push(artifact.stats.avg_payoff_a);
            avg_b.push(artifact.stats.avg_payoff_b);
            coop_a.push(artifact.stats.coop_rate_a);
            coop_b.push(artifact.stats.coop_rate_b);
            mutual_c.push(artifact.stats.mutual_coop_rate);
            mutual_d.push(artifact.stats.mutual_defect_rate);

            replications_detail.push(ReplicationResult {
                rep,
                task_id: task.task_id,
                match_seed,
                stats: artifact.stats,
                trace: artifact.trace,
            });
        }

        let mean_stats = MatchupMeanStats {
            avg_payoff_a: mean(&avg_a),
            avg_payoff_b: mean(&avg_b),
            coop_rate_a: mean(&coop_a),
            coop_rate_b: mean(&coop_b),
            mutual_coop_rate: mean(&mutual_c),
            mutual_defect_rate: mean(&mutual_d),
        };

        let assertions = matchup
            .assertions
            .iter()
            .map(|a| eval_assertion(a, &mean_stats))
            .collect::<Vec<_>>();
        let passed = assertions.iter().all(|a| a.passed);

        let rounds = replications_detail
            .iter()
            .map(|r| r.stats.rounds)
            .collect::<Vec<_>>();
        let rounds_min = rounds.iter().min().copied();
        let rounds_max = rounds.iter().max().copied();
        let rounds_mean = mean_u32(&rounds);
        let rounds_per_replication = rounds_max.unwrap_or(0);

        matchup_results.push(ProbeMatchupResult {
            id: matchup.id.clone(),
            replications: matchup.replications,
            rounds_per_replication,
            rounds_min,
            rounds_max,
            rounds_mean,
            mean: mean_stats,
            assertions,
            passed,
            replications_detail,
        });
    }

    let passed = matchup_results.iter().all(|m| m.passed);
    Ok(ProbeResultArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        probe_id: expanded.probe_id,
        probe_schema_version: expanded.probe_schema_version,
        input_hash: String::new(), // filled by CLI (hash over canonical probe bytes)
        probe_hash: expanded.probe_hash,
        passed,
        matchups: matchup_results,
    })
}
