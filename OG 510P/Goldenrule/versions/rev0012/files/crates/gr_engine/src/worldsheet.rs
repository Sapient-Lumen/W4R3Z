use crate::spec::{NoiseModelSpec, TerminationRuleSpec, WorldSpec};
use serde::{Deserialize, Serialize};
use thiserror::Error;

fn default_schema_version() -> u32 {
    1
}

#[derive(Debug, Error)]
pub enum WorldSheetError {
    #[error("worldsheet schema_version {0} is unsupported")]
    UnsupportedSchemaVersion(u32),
    #[error("invalid probability {0} (expected in [0,1])")]
    InvalidProbability(f64),
    #[error("invalid number {0} (expected finite)")]
    InvalidNumber(f64),
    #[error("invalid value: {0}")]
    InvalidValue(String),
    #[error("duplicate world id {0}")]
    DuplicateWorldId(String),
    #[error("missing world id {0}")]
    MissingWorldId(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorldDatasheet {
    pub composition: String,
    pub rationale: String,
    #[serde(default)]
    pub gaps_and_limitations: Vec<String>,
    #[serde(default)]
    pub brittleness_tendencies: Vec<String>,
    pub update_policy: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorldRegistrySpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub worlds: Vec<WorldSpec>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorldSuiteSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    pub datasheet: WorldDatasheet,
    pub world_ids: Vec<String>,
}

fn validate_probability(p: f64) -> Result<(), WorldSheetError> {
    if !p.is_finite() {
        return Err(WorldSheetError::InvalidNumber(p));
    }
    if (0.0..=1.0).contains(&p) {
        Ok(())
    } else {
        Err(WorldSheetError::InvalidProbability(p))
    }
}

fn validate_noise(noise: &NoiseModelSpec) -> Result<(), WorldSheetError> {
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

fn validate_termination(termination: &TerminationRuleSpec) -> Result<(), WorldSheetError> {
    match *termination {
        TerminationRuleSpec::Fixed { rounds } => {
            if rounds == 0 {
                Err(WorldSheetError::InvalidValue(
                    "termination rounds must be > 0".to_string(),
                ))
            } else {
                Ok(())
            }
        }
        TerminationRuleSpec::Geometric { delta, max_rounds } => {
            validate_probability(delta)?;
            if max_rounds == 0 {
                Err(WorldSheetError::InvalidValue(
                    "geometric max_rounds must be > 0".to_string(),
                ))
            } else {
                Ok(())
            }
        }
    }
}

fn validate_world(world: &WorldSpec) -> Result<(), WorldSheetError> {
    if world.id.trim().is_empty() {
        return Err(WorldSheetError::InvalidValue(
            "world id must be non-empty".to_string(),
        ));
    }
    validate_noise(&world.noise)?;
    validate_termination(&world.termination)?;
    Ok(())
}

pub fn validate_world_registry(reg: &WorldRegistrySpec) -> Result<(), WorldSheetError> {
    if reg.schema_version != 1 {
        return Err(WorldSheetError::UnsupportedSchemaVersion(
            reg.schema_version,
        ));
    }
    let mut ids = std::collections::BTreeSet::new();
    for w in &reg.worlds {
        if !ids.insert(w.id.clone()) {
            return Err(WorldSheetError::DuplicateWorldId(w.id.clone()));
        }
        validate_world(w)?;
    }
    Ok(())
}

pub fn validate_world_suite(
    reg: &WorldRegistrySpec,
    suite: &WorldSuiteSpec,
) -> Result<(), WorldSheetError> {
    if suite.schema_version != 1 {
        return Err(WorldSheetError::UnsupportedSchemaVersion(
            suite.schema_version,
        ));
    }
    if suite.world_ids.is_empty() {
        return Err(WorldSheetError::InvalidValue(
            "suite world_ids must be non-empty".to_string(),
        ));
    }
    if suite.datasheet.composition.trim().is_empty()
        || suite.datasheet.rationale.trim().is_empty()
        || suite.datasheet.update_policy.trim().is_empty()
    {
        return Err(WorldSheetError::InvalidValue(
            "datasheet composition/rationale/update_policy must be non-empty".to_string(),
        ));
    }

    validate_world_registry(reg)?;
    let world_ids = reg
        .worlds
        .iter()
        .map(|w| w.id.clone())
        .collect::<std::collections::BTreeSet<_>>();
    for id in &suite.world_ids {
        if !world_ids.contains(id) {
            return Err(WorldSheetError::MissingWorldId(id.clone()));
        }
    }
    Ok(())
}
