use crate::probe::{ProbeError, ProbeSpec};
use crate::sim::{run_match, SimError};
use crate::snapshot::SnapshotSummary;
use crate::spec::{NoiseModelSpec, StrategySpec, TaskSpec, TerminationRuleSpec};
use serde::{Deserialize, Serialize};
use thiserror::Error;

fn default_schema_version() -> u32 {
    1
}

#[derive(Debug, Error)]
pub enum MetamorphicError {
    #[error("metamorphic schema_version {0} is unsupported")]
    UnsupportedSchemaVersion(u32),
    #[error(transparent)]
    Probe(#[from] ProbeError),
    #[error(transparent)]
    Sim(#[from] SimError),
    #[error("metamorphic check requires eligible matchup: {0}")]
    Ineligible(String),
    #[error("duplicate check id {0}")]
    DuplicateCheckId(String),
    #[error("missing check id {0}")]
    MissingCheckId(String),
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MetamorphicKind {
    PlayerSwapSymmetry,
    ScalingPrefixStability,
}

impl Serialize for MetamorphicKind {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let s = match self {
            MetamorphicKind::PlayerSwapSymmetry => "player_swap_symmetry",
            MetamorphicKind::ScalingPrefixStability => "scaling_prefix_stability",
        };
        serializer.serialize_str(s)
    }
}

impl<'de> Deserialize<'de> for MetamorphicKind {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        #[derive(Deserialize)]
        #[serde(untagged)]
        enum Repr {
            Str(String),
            Obj { kind: String },
        }

        let repr = Repr::deserialize(deserializer)?;
        let s = match repr {
            Repr::Str(s) => s,
            Repr::Obj { kind } => kind,
        };

        match s.as_str() {
            "player_swap_symmetry" => Ok(MetamorphicKind::PlayerSwapSymmetry),
            "scaling_prefix_stability" => Ok(MetamorphicKind::ScalingPrefixStability),
            other => Err(serde::de::Error::custom(format!(
                "unknown metamorphic kind {other}"
            ))),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetamorphicCheckSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub kind: MetamorphicKind,
    #[serde(default)]
    pub scaling_prefix: Option<ScalingPrefixConfig>,
    pub probe: ProbeSpec,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScalingPrefixConfig {
    pub base_rounds: u32,
    pub extended_rounds: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetamorphicRegistrySpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub checks: Vec<MetamorphicCheckSpec>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetamorphicSuiteSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub check_ids: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetamorphicResultArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub check_id: String,
    pub kind: MetamorphicKind,
    pub input_hash: String,
    pub passed: bool,
    pub eligible_pairs: u32,
    pub skipped_matchups: u32,
    pub failures: Vec<MetamorphicFailure>,
    pub skipped: Vec<MetamorphicSkip>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetamorphicSuiteResultArtifact {
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
    pub check_results: Vec<MetamorphicResultArtifact>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetamorphicSkip {
    pub reason: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetamorphicFailure {
    pub message: String,
    pub task_ab: TaskSpec,
    pub task_ba: TaskSpec,
    pub artifact_ab: crate::artifact::MatchArtifact,
    pub artifact_ba: crate::artifact::MatchArtifact,
}

fn is_deterministic_strategy(spec: &StrategySpec) -> bool {
    match spec {
        StrategySpec::Builtin { kind, .. } => !matches!(kind, crate::spec::BuiltinKind::Random),
        StrategySpec::MemoryOne { .. } => false,
        StrategySpec::MemoryOneExit { .. } => false,
        StrategySpec::Fsm { states, .. } => states
            .iter()
            .all(|s| s.output_c == 0.0 || s.output_c == 1.0),
    }
}

fn is_deterministic_noise(noise: &NoiseModelSpec) -> bool {
    match *noise {
        NoiseModelSpec::None => true,
        NoiseModelSpec::ImplementationFlip { p } => p == 0.0,
        NoiseModelSpec::ObservationFlip { p } => p == 0.0,
        NoiseModelSpec::Iid {
            p_implementation,
            p_observation,
        } => p_implementation == 0.0 && p_observation == 0.0,
        NoiseModelSpec::AsymmetricIid {
            p_implementation_a,
            p_implementation_b,
            p_observation_a,
            p_observation_b,
        } => {
            p_implementation_a == 0.0
                && p_implementation_b == 0.0
                && p_observation_a == 0.0
                && p_observation_b == 0.0
        }
    }
}

fn approx_eq(a: f64, b: f64) -> bool {
    (a - b).abs() <= 1e-12
}

fn check_swap_stats(
    ab: &crate::artifact::MatchStats,
    ba: &crate::artifact::MatchStats,
) -> Result<(), String> {
    if ab.rounds != ba.rounds {
        return Err(format!("rounds mismatch: {} vs {}", ab.rounds, ba.rounds));
    }
    if !approx_eq(ab.total_payoff_a, ba.total_payoff_b) {
        return Err(format!(
            "total_payoff swap mismatch: ab.a={} vs ba.b={}",
            ab.total_payoff_a, ba.total_payoff_b
        ));
    }
    if !approx_eq(ab.total_payoff_b, ba.total_payoff_a) {
        return Err(format!(
            "total_payoff swap mismatch: ab.b={} vs ba.a={}",
            ab.total_payoff_b, ba.total_payoff_a
        ));
    }
    if !approx_eq(ab.avg_payoff_a, ba.avg_payoff_b) {
        return Err("avg_payoff_a != swapped avg_payoff_b".to_string());
    }
    if !approx_eq(ab.avg_payoff_b, ba.avg_payoff_a) {
        return Err("avg_payoff_b != swapped avg_payoff_a".to_string());
    }
    if !approx_eq(ab.coop_rate_a, ba.coop_rate_b) {
        return Err("coop_rate_a != swapped coop_rate_b".to_string());
    }
    if !approx_eq(ab.coop_rate_b, ba.coop_rate_a) {
        return Err("coop_rate_b != swapped coop_rate_a".to_string());
    }
    if !approx_eq(ab.mutual_coop_rate, ba.mutual_coop_rate) {
        return Err("mutual_coop_rate != mutual_coop_rate".to_string());
    }
    if !approx_eq(ab.mutual_defect_rate, ba.mutual_defect_rate) {
        return Err("mutual_defect_rate != mutual_defect_rate".to_string());
    }
    Ok(())
}

pub fn run_metamorphic_check(
    spec: &MetamorphicCheckSpec,
) -> Result<MetamorphicResultArtifact, MetamorphicError> {
    if spec.schema_version != 1 {
        return Err(MetamorphicError::UnsupportedSchemaVersion(
            spec.schema_version,
        ));
    }

    match spec.kind {
        MetamorphicKind::PlayerSwapSymmetry => run_player_swap_symmetry(spec),
        MetamorphicKind::ScalingPrefixStability => run_scaling_prefix_stability(spec),
    }
}

pub fn validate_metamorphic_registry(
    reg: &MetamorphicRegistrySpec,
) -> Result<(), MetamorphicError> {
    if reg.schema_version != 1 {
        return Err(MetamorphicError::UnsupportedSchemaVersion(
            reg.schema_version,
        ));
    }
    let mut ids = std::collections::BTreeSet::new();
    for c in &reg.checks {
        if !ids.insert(c.id.clone()) {
            return Err(MetamorphicError::DuplicateCheckId(c.id.clone()));
        }
        if c.schema_version != 1 {
            return Err(MetamorphicError::UnsupportedSchemaVersion(c.schema_version));
        }
    }
    Ok(())
}

pub fn validate_metamorphic_suite(suite: &MetamorphicSuiteSpec) -> Result<(), MetamorphicError> {
    if suite.schema_version != 1 {
        return Err(MetamorphicError::UnsupportedSchemaVersion(
            suite.schema_version,
        ));
    }
    if suite.check_ids.is_empty() {
        return Err(MetamorphicError::Ineligible(
            "suite check_ids must be non-empty".to_string(),
        ));
    }
    Ok(())
}

fn find_check<'a>(reg: &'a MetamorphicRegistrySpec, id: &str) -> Option<&'a MetamorphicCheckSpec> {
    reg.checks.iter().find(|c| c.id == id)
}

pub fn run_metamorphic_suite(
    reg: &MetamorphicRegistrySpec,
    suite: &MetamorphicSuiteSpec,
) -> Result<MetamorphicSuiteResultArtifact, MetamorphicError> {
    validate_metamorphic_registry(reg)?;
    validate_metamorphic_suite(suite)?;

    let registry_hash = {
        let canonical =
            serde_json::to_vec(reg).map_err(|e| MetamorphicError::Ineligible(e.to_string()))?;
        crate::util::sha256_hex(&canonical)
    };
    let suite_hash = {
        let canonical =
            serde_json::to_vec(suite).map_err(|e| MetamorphicError::Ineligible(e.to_string()))?;
        crate::util::sha256_hex(&canonical)
    };

    let mut check_results = Vec::with_capacity(suite.check_ids.len());
    for id in &suite.check_ids {
        let check =
            find_check(reg, id).ok_or_else(|| MetamorphicError::MissingCheckId(id.clone()))?;
        let canonical =
            serde_json::to_vec(check).map_err(|e| MetamorphicError::Ineligible(e.to_string()))?;
        let input_hash = crate::util::sha256_hex(&canonical);

        let mut r = run_metamorphic_check(check)?;
        r.input_hash = input_hash;
        check_results.push(r);
    }

    let passed = check_results.iter().all(|r| r.passed);
    Ok(MetamorphicSuiteResultArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        registry_id: reg.id.clone(),
        suite_id: suite.id.clone(),
        input_hash: String::new(), // filled by CLI
        registry_hash,
        suite_hash,
        snapshot: None,
        passed,
        check_results,
    })
}

pub fn run_metamorphic_suite_with_snapshot(
    reg: &MetamorphicRegistrySpec,
    suite: &MetamorphicSuiteSpec,
    snapshot: SnapshotSummary,
) -> Result<MetamorphicSuiteResultArtifact, MetamorphicError> {
    let mut artifact = run_metamorphic_suite(reg, suite)?;
    artifact.snapshot = Some(snapshot);
    Ok(artifact)
}

fn run_player_swap_symmetry(
    spec: &MetamorphicCheckSpec,
) -> Result<MetamorphicResultArtifact, MetamorphicError> {
    let probe = &spec.probe;
    crate::probe::validate_probe(probe)?;

    let mut failures = Vec::new();
    let mut skipped = Vec::new();
    let mut eligible_pairs: u32 = 0;

    for matchup in &probe.matchups {
        let eligible = is_deterministic_noise(&probe.world.noise)
            && is_deterministic_strategy(&matchup.strategy_a)
            && is_deterministic_strategy(&matchup.strategy_b);
        if !eligible {
            skipped.push(MetamorphicSkip {
                reason: format!("ineligible matchup {}", matchup.id),
            });
            continue;
        }

        for rep in 0..matchup.replications {
            eligible_pairs = eligible_pairs.saturating_add(1);
            let match_seed = probe
                .world
                .seed
                .wrapping_add(matchup.seed_offset)
                .wrapping_add(rep as u64);

            let mut task_ab = TaskSpec::new(
                &format!("{}/{}__rep{}", probe.id, matchup.id, rep),
                probe.world.clone(),
                matchup.strategy_a.clone(),
                matchup.strategy_b.clone(),
                match_seed,
            );
            task_ab.trace_rounds = matchup.trace_rounds;

            let mut task_ba = TaskSpec::new(
                &format!("{}/{}_swapped__rep{}", probe.id, matchup.id, rep),
                probe.world.clone(),
                matchup.strategy_b.clone(),
                matchup.strategy_a.clone(),
                match_seed,
            );
            task_ba.trace_rounds = matchup.trace_rounds;

            let artifact_ab = run_match(&task_ab)?;
            let artifact_ba = run_match(&task_ba)?;

            if let Err(msg) = check_swap_stats(&artifact_ab.stats, &artifact_ba.stats) {
                failures.push(MetamorphicFailure {
                    message: format!("{} (matchup {}, rep {})", msg, matchup.id, rep),
                    task_ab,
                    task_ba,
                    artifact_ab,
                    artifact_ba,
                });
            }
        }
    }

    let skipped_matchups = skipped.len() as u32;
    let passed = failures.is_empty() && eligible_pairs > 0;
    Ok(MetamorphicResultArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        check_id: spec.id.clone(),
        kind: spec.kind.clone(),
        input_hash: String::new(), // filled by CLI
        passed,
        eligible_pairs,
        skipped_matchups,
        failures,
        skipped,
    })
}

fn run_scaling_prefix_stability(
    spec: &MetamorphicCheckSpec,
) -> Result<MetamorphicResultArtifact, MetamorphicError> {
    let probe = &spec.probe;
    crate::probe::validate_probe(probe)?;

    let cfg = spec
        .scaling_prefix
        .clone()
        .ok_or_else(|| MetamorphicError::Ineligible("missing scaling_prefix config".to_string()))?;
    if cfg.base_rounds == 0 {
        return Err(MetamorphicError::Ineligible(
            "base_rounds must be > 0".to_string(),
        ));
    }
    if cfg.base_rounds > cfg.extended_rounds {
        return Err(MetamorphicError::Ineligible(
            "base_rounds must be <= extended_rounds".to_string(),
        ));
    }

    let mut failures = Vec::new();
    let mut skipped = Vec::new();
    let mut eligible_pairs: u32 = 0;

    for matchup in &probe.matchups {
        if matchup.replications == 0 {
            skipped.push(MetamorphicSkip {
                reason: format!("ineligible matchup {} (replications=0)", matchup.id),
            });
            continue;
        }

        for rep in 0..matchup.replications {
            eligible_pairs = eligible_pairs.saturating_add(1);
            let match_seed = probe
                .world
                .seed
                .wrapping_add(matchup.seed_offset)
                .wrapping_add(rep as u64);

            let world_base = WorldSpecWithTermination::new(probe.world.clone(), cfg.base_rounds);
            let world_ext = WorldSpecWithTermination::new(probe.world.clone(), cfg.extended_rounds);

            let mut task_base = TaskSpec::new(
                &format!("{}/{}_base__rep{}", probe.id, matchup.id, rep),
                world_base.0,
                matchup.strategy_a.clone(),
                matchup.strategy_b.clone(),
                match_seed,
            );
            task_base.trace_rounds = cfg.base_rounds;

            let mut task_ext = TaskSpec::new(
                &format!("{}/{}_extended__rep{}", probe.id, matchup.id, rep),
                world_ext.0,
                matchup.strategy_a.clone(),
                matchup.strategy_b.clone(),
                match_seed,
            );
            task_ext.trace_rounds = cfg.base_rounds;

            let artifact_base = run_match(&task_base)?;
            let artifact_ext = run_match(&task_ext)?;

            let t_base = artifact_base
                .trace
                .as_ref()
                .map(|t| t.as_slice())
                .unwrap_or(&[]);
            let t_ext = artifact_ext
                .trace
                .as_ref()
                .map(|t| t.as_slice())
                .unwrap_or(&[]);

            if t_base.len() != cfg.base_rounds as usize || t_ext.len() != cfg.base_rounds as usize {
                failures.push(MetamorphicFailure {
                    message: format!(
                        "trace_rounds mismatch (expected {}): base {}, extended {}",
                        cfg.base_rounds,
                        t_base.len(),
                        t_ext.len()
                    ),
                    task_ab: task_base,
                    task_ba: task_ext,
                    artifact_ab: artifact_base,
                    artifact_ba: artifact_ext,
                });
                continue;
            }

            if t_base != t_ext {
                failures.push(MetamorphicFailure {
                    message: format!("trace prefix differs (matchup {}, rep {})", matchup.id, rep),
                    task_ab: task_base,
                    task_ba: task_ext,
                    artifact_ab: artifact_base,
                    artifact_ba: artifact_ext,
                });
            }
        }
    }

    let skipped_matchups = skipped.len() as u32;
    let passed = failures.is_empty() && eligible_pairs > 0;
    Ok(MetamorphicResultArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        check_id: spec.id.clone(),
        kind: spec.kind.clone(),
        input_hash: String::new(), // filled by CLI
        passed,
        eligible_pairs,
        skipped_matchups,
        failures,
        skipped,
    })
}

struct WorldSpecWithTermination(pub crate::spec::WorldSpec);

impl WorldSpecWithTermination {
    fn new(mut world: crate::spec::WorldSpec, rounds: u32) -> Self {
        world.termination = TerminationRuleSpec::Fixed { rounds };
        Self(world)
    }
}
