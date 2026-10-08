use crate::metamorphic::{
    validate_metamorphic_registry, validate_metamorphic_suite, MetamorphicRegistrySpec,
    MetamorphicSuiteSpec,
};
use crate::probe::{
    validate_probe_registry, validate_probe_suite, ProbeRegistrySpec, ProbeSuiteSpec,
};
use crate::scorecard::{validate_scorecard_def, ScorecardDef};
use crate::scorecard_suite::{
    validate_scorecard_registry, validate_scorecard_suite, ScorecardRegistrySpec,
    ScorecardSuiteSpec,
};
use crate::worldsheet::{
    validate_world_registry, validate_world_suite, WorldRegistrySpec, WorldSuiteSpec,
};
use serde::{Deserialize, Serialize};
use thiserror::Error;

fn default_schema_version() -> u32 {
    1
}

#[derive(Debug, Error)]
pub enum SnapshotError {
    #[error("snapshot schema_version {0} is unsupported")]
    UnsupportedSchemaVersion(u32),
    #[error("invalid value: {0}")]
    InvalidValue(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnapshotSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub id: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub world_registry: Option<WorldRegistrySpec>,
    #[serde(default)]
    pub world_suite: Option<WorldSuiteSpec>,
    #[serde(default)]
    pub probe_registry: Option<ProbeRegistrySpec>,
    #[serde(default)]
    pub probe_suite: Option<ProbeSuiteSpec>,
    #[serde(default)]
    pub metamorphic_registry: Option<MetamorphicRegistrySpec>,
    #[serde(default)]
    pub metamorphic_suite: Option<MetamorphicSuiteSpec>,
    #[serde(default)]
    pub scorecard: Option<ScorecardDef>,
    #[serde(default)]
    pub scorecard_registry: Option<ScorecardRegistrySpec>,
    #[serde(default)]
    pub scorecard_suite: Option<ScorecardSuiteSpec>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnapshotArtifact {
    pub schema_version: u32,
    pub engine_version: String,
    pub snapshot_id: String,
    pub input_hash: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub world_registry: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub world_suite: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub probe_registry: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub probe_suite: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metamorphic_registry: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metamorphic_suite: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scorecard: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scorecard_registry: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scorecard_suite: Option<HashedDef>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnapshotSummary {
    pub snapshot_id: String,
    pub input_hash: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub world_registry: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub world_suite: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub probe_registry: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub probe_suite: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metamorphic_registry: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metamorphic_suite: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scorecard: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scorecard_registry: Option<HashedDef>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scorecard_suite: Option<HashedDef>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HashedDef {
    pub id: String,
    pub hash: String,
}

fn hash_json<T: Serialize>(obj: &T) -> Result<String, SnapshotError> {
    let canonical =
        serde_json::to_vec(obj).map_err(|e| SnapshotError::InvalidValue(e.to_string()))?;
    Ok(crate::util::sha256_hex(&canonical))
}

pub fn build_snapshot(spec: &SnapshotSpec) -> Result<SnapshotArtifact, SnapshotError> {
    if spec.schema_version != 1 {
        return Err(SnapshotError::UnsupportedSchemaVersion(spec.schema_version));
    }

    if let Some(reg) = &spec.world_registry {
        validate_world_registry(reg).map_err(|e| SnapshotError::InvalidValue(e.to_string()))?;
    }
    if let Some(suite) = &spec.world_suite {
        let Some(reg) = &spec.world_registry else {
            return Err(SnapshotError::InvalidValue(
                "world_suite requires world_registry".to_string(),
            ));
        };
        validate_world_suite(reg, suite).map_err(|e| SnapshotError::InvalidValue(e.to_string()))?;
    }

    if let Some(r) = &spec.probe_registry {
        validate_probe_registry(r).map_err(|e| SnapshotError::InvalidValue(e.to_string()))?;
    }
    if let Some(s) = &spec.probe_suite {
        validate_probe_suite(s).map_err(|e| SnapshotError::InvalidValue(e.to_string()))?;
    }
    if let Some(r) = &spec.metamorphic_registry {
        validate_metamorphic_registry(r).map_err(|e| SnapshotError::InvalidValue(e.to_string()))?;
    }
    if let Some(s) = &spec.metamorphic_suite {
        validate_metamorphic_suite(s).map_err(|e| SnapshotError::InvalidValue(e.to_string()))?;
    }
    if let Some(s) = &spec.scorecard {
        validate_scorecard_def(s).map_err(|e| SnapshotError::InvalidValue(e.to_string()))?;
    }
    if let Some(r) = &spec.scorecard_registry {
        validate_scorecard_registry(r).map_err(|e| SnapshotError::InvalidValue(e.to_string()))?;
    }
    if let Some(s) = &spec.scorecard_suite {
        validate_scorecard_suite(s).map_err(|e| SnapshotError::InvalidValue(e.to_string()))?;
        let Some(reg) = &spec.scorecard_registry else {
            return Err(SnapshotError::InvalidValue(
                "scorecard_suite requires scorecard_registry".to_string(),
            ));
        };
        validate_scorecard_registry(reg).map_err(|e| SnapshotError::InvalidValue(e.to_string()))?;
    }

    let input_hash = hash_json(spec)?;
    Ok(SnapshotArtifact {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        snapshot_id: spec.id.clone(),
        input_hash,
        world_registry: spec
            .world_registry
            .as_ref()
            .map(|r| {
                Ok(HashedDef {
                    id: r.id.clone(),
                    hash: hash_json(r)?,
                })
            })
            .transpose()?,
        world_suite: spec
            .world_suite
            .as_ref()
            .map(|s| {
                Ok(HashedDef {
                    id: s.id.clone(),
                    hash: hash_json(s)?,
                })
            })
            .transpose()?,
        probe_registry: spec
            .probe_registry
            .as_ref()
            .map(|r| {
                Ok(HashedDef {
                    id: r.id.clone(),
                    hash: hash_json(r)?,
                })
            })
            .transpose()?,
        probe_suite: spec
            .probe_suite
            .as_ref()
            .map(|s| {
                Ok(HashedDef {
                    id: s.id.clone(),
                    hash: hash_json(s)?,
                })
            })
            .transpose()?,
        metamorphic_registry: spec
            .metamorphic_registry
            .as_ref()
            .map(|r| {
                Ok(HashedDef {
                    id: r.id.clone(),
                    hash: hash_json(r)?,
                })
            })
            .transpose()?,
        metamorphic_suite: spec
            .metamorphic_suite
            .as_ref()
            .map(|s| {
                Ok(HashedDef {
                    id: s.id.clone(),
                    hash: hash_json(s)?,
                })
            })
            .transpose()?,
        scorecard: spec
            .scorecard
            .as_ref()
            .map(|s| {
                Ok(HashedDef {
                    id: s.id.clone(),
                    hash: hash_json(s)?,
                })
            })
            .transpose()?,
        scorecard_registry: spec
            .scorecard_registry
            .as_ref()
            .map(|s| {
                Ok(HashedDef {
                    id: s.id.clone(),
                    hash: hash_json(s)?,
                })
            })
            .transpose()?,
        scorecard_suite: spec
            .scorecard_suite
            .as_ref()
            .map(|s| {
                Ok(HashedDef {
                    id: s.id.clone(),
                    hash: hash_json(s)?,
                })
            })
            .transpose()?,
    })
}

pub fn summarize_snapshot(artifact: &SnapshotArtifact) -> SnapshotSummary {
    SnapshotSummary {
        snapshot_id: artifact.snapshot_id.clone(),
        input_hash: artifact.input_hash.clone(),
        world_registry: artifact.world_registry.clone(),
        world_suite: artifact.world_suite.clone(),
        probe_registry: artifact.probe_registry.clone(),
        probe_suite: artifact.probe_suite.clone(),
        metamorphic_registry: artifact.metamorphic_registry.clone(),
        metamorphic_suite: artifact.metamorphic_suite.clone(),
        scorecard: artifact.scorecard.clone(),
        scorecard_registry: artifact.scorecard_registry.clone(),
        scorecard_suite: artifact.scorecard_suite.clone(),
    }
}
