//! Core domain model for the AnonSync workspace.
//!
//! This crate intentionally stays transport-agnostic.

/// Canonical project name.
pub const PROJECT_NAME: &str = "AnonSync";

/// Supported transport families.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TransportKind {
    I2pSam,
    TorArti,
    TorExternal,
    Mixed,
}

/// Product stage in repository planning.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ProjectStage {
    ArchiveSkeleton,
    Design,
    Prototype,
    Alpha,
    Beta,
    Stable,
}

/// A compact statement of current project posture.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProjectPosture {
    pub stage: ProjectStage,
    pub one_binary_goal: bool,
    pub transport_agnostic_core: bool,
}

impl Default for ProjectPosture {
    fn default() -> Self {
        Self {
            stage: ProjectStage::ArchiveSkeleton,
            one_binary_goal: true,
            transport_agnostic_core: true,
        }
    }
}

/// Return the current posture used by the workspace skeleton.
pub fn current_posture() -> ProjectPosture {
    ProjectPosture::default()
}

/// Ordered bootstrap sequence for early development mode.
pub fn recommended_boot_sequence() -> &'static [&'static str] {
    &[
        "Load local config",
        "Validate runtime prerequisites",
        "Start or connect transport providers",
        "Open repository state",
        "Start sync orchestration",
    ]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn project_name_is_stable() {
        assert_eq!(PROJECT_NAME, "AnonSync");
    }

    #[test]
    fn posture_defaults_to_skeleton_mode() {
        assert_eq!(current_posture().stage, ProjectStage::ArchiveSkeleton);
    }

    #[test]
    fn bootstrap_sequence_is_non_empty() {
        assert!(!recommended_boot_sequence().is_empty());
    }
}
