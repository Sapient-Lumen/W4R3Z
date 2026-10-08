use clap::Parser;
use gr_engine::defdiff::{
    diff_snapshot_artifacts, diff_snapshots, SnapshotArtifactDiffSpec, SnapshotDiffSpec,
};
use gr_engine::matchdiff::{diff_match_artifacts, MatchArtifactDiffSpec};
use gr_engine::metadiff::{
    diff_metamorphic_artifacts, diff_metamorphic_suite_artifacts,
    MetamorphicResultArtifactDiffSpec, MetamorphicSuiteResultArtifactDiffSpec,
};
use gr_engine::metamorphic::{
    run_metamorphic_check, run_metamorphic_suite, run_metamorphic_suite_with_snapshot,
    MetamorphicCheckSpec, MetamorphicRegistrySpec, MetamorphicSuiteSpec,
};
use gr_engine::probe::{
    run_probe, run_probe_suite, run_probe_suite_with_snapshot, ProbeRegistrySpec, ProbeSpec,
    ProbeSuiteSpec,
};
use gr_engine::probediff::{
    diff_probe_artifacts, diff_probe_suite_artifacts, ProbeResultArtifactDiffSpec,
    ProbeSuiteResultArtifactDiffSpec,
};
use gr_engine::run_snapshot::run_snapshot;
use gr_engine::scorecard::{run_scorecard, ScorecardSpec};
use gr_engine::scorecard_suite::{run_scorecard_suite, ScorecardRegistrySpec, ScorecardSuiteSpec};
use gr_engine::scorecard_suitediff::{
    diff_scorecard_suite_artifacts, ScorecardSuiteResultArtifactDiffSpec,
};
use gr_engine::scorecarddiff::{diff_scorecard_artifacts, ScorecardResultArtifactDiffSpec};
use gr_engine::shrink::{
    shrink_probe_matchups, shrink_probe_pipeline, shrink_probe_replications, shrink_probe_rounds,
    ShrinkProbeMatchupsSpec, ShrinkProbePipelineSpec, ShrinkProbeReplicationsSpec,
    ShrinkProbeRoundsSpec,
};
use gr_engine::sim::run_match;
use gr_engine::snapshot::{build_snapshot, summarize_snapshot, SnapshotArtifact, SnapshotSpec};
use gr_engine::snapshotrun_diff::{diff_snapshot_run_artifacts, SnapshotRunArtifactDiffSpec};
use gr_engine::spec::TaskSpec;
use gr_engine::util::{atomic_write, sha256_hex};
use std::fs;
use std::path::PathBuf;

#[derive(Debug, Parser)]
#[command(name = "gr-engine")]
#[command(about = "Concord simulation core (Stage 1)")]
enum Cli {
    RunTask {
        #[arg(long)]
        task: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    RunProbe {
        #[arg(long)]
        probe: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    RunMetamorphic {
        #[arg(long)]
        spec: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    RunProbeSuite {
        #[arg(long)]
        registry: PathBuf,
        #[arg(long)]
        suite: PathBuf,
        #[arg(long)]
        snapshot: Option<PathBuf>,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    RunMetamorphicSuite {
        #[arg(long)]
        registry: PathBuf,
        #[arg(long)]
        suite: PathBuf,
        #[arg(long)]
        snapshot: Option<PathBuf>,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    Snapshot {
        #[arg(long)]
        spec: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    RunSnapshot {
        #[arg(long)]
        spec: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    RunScorecard {
        #[arg(long)]
        spec: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    RunScorecardSuite {
        #[arg(long)]
        registry: PathBuf,
        #[arg(long)]
        suite: PathBuf,
        #[arg(long)]
        snapshot_run: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    ShrinkProbeRounds {
        #[arg(long)]
        spec: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    ShrinkProbeMatchups {
        #[arg(long)]
        spec: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    ShrinkProbeReplications {
        #[arg(long)]
        spec: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    ShrinkProbePipeline {
        #[arg(long)]
        spec: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    DiffSnapshots {
        #[arg(long)]
        spec: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    DiffSnapshotArtifacts {
        #[arg(long)]
        a: PathBuf,
        #[arg(long)]
        b: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value = "diff_artifacts")]
        id: String,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    DiffProbeArtifacts {
        #[arg(long)]
        a: PathBuf,
        #[arg(long)]
        b: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value = "diff_probe_artifacts")]
        id: String,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    DiffMatchArtifacts {
        #[arg(long)]
        a: PathBuf,
        #[arg(long)]
        b: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value = "diff_match_artifacts")]
        id: String,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    DiffProbeSuiteArtifacts {
        #[arg(long)]
        a: PathBuf,
        #[arg(long)]
        b: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value = "diff_probe_suite_artifacts")]
        id: String,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    DiffMetamorphicArtifacts {
        #[arg(long)]
        a: PathBuf,
        #[arg(long)]
        b: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value = "diff_metamorphic_artifacts")]
        id: String,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    DiffMetamorphicSuiteArtifacts {
        #[arg(long)]
        a: PathBuf,
        #[arg(long)]
        b: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value = "diff_metamorphic_suite_artifacts")]
        id: String,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    DiffScorecardArtifacts {
        #[arg(long)]
        a: PathBuf,
        #[arg(long)]
        b: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value = "diff_scorecard_artifacts")]
        id: String,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    DiffScorecardSuiteArtifacts {
        #[arg(long)]
        a: PathBuf,
        #[arg(long)]
        b: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value = "diff_scorecard_suite_artifacts")]
        id: String,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
    DiffSnapshotRunArtifacts {
        #[arg(long)]
        a: PathBuf,
        #[arg(long)]
        b: PathBuf,
        #[arg(long)]
        out: PathBuf,
        #[arg(long, default_value = "diff_snapshot_run_artifacts")]
        id: String,
        #[arg(long, default_value_t = false)]
        pretty: bool,
    },
}

fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();

    match cli {
        Cli::RunTask { task, out, pretty } => {
            let task_bytes = fs::read(&task)?;
            let task_spec: TaskSpec = serde_json::from_slice(&task_bytes)?;

            let canonical = serde_json::to_vec(&task_spec)?;
            let input_hash = sha256_hex(&canonical);
            let mut artifact = run_match(&task_spec)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };

            atomic_write(&out, &bytes)?;
        }
        Cli::RunProbe { probe, out, pretty } => {
            let probe_bytes = fs::read(&probe)?;
            let probe_spec: ProbeSpec = serde_json::from_slice(&probe_bytes)?;

            let canonical = serde_json::to_vec(&probe_spec)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = run_probe(&probe_spec)?;
            artifact.input_hash = input_hash.clone();

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };

            atomic_write(&out, &bytes)?;
        }
        Cli::RunMetamorphic { spec, out, pretty } => {
            let spec_bytes = fs::read(&spec)?;
            let spec_obj: MetamorphicCheckSpec = serde_json::from_slice(&spec_bytes)?;

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = run_metamorphic_check(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };

            atomic_write(&out, &bytes)?;
        }
        Cli::RunProbeSuite {
            registry,
            suite,
            snapshot,
            out,
            pretty,
        } => {
            let reg_bytes = fs::read(&registry)?;
            let suite_bytes = fs::read(&suite)?;
            let reg_obj: ProbeRegistrySpec = serde_json::from_slice(&reg_bytes)?;
            let suite_obj: ProbeSuiteSpec = serde_json::from_slice(&suite_bytes)?;

            let snapshot_obj = match snapshot {
                None => None,
                Some(path) => {
                    let b = fs::read(path)?;
                    let a: SnapshotArtifact = serde_json::from_slice(&b)?;
                    Some(a)
                }
            };
            let canonical =
                serde_json::to_vec(&(reg_obj.clone(), suite_obj.clone(), snapshot_obj.clone()))?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = match snapshot_obj {
                None => run_probe_suite(&reg_obj, &suite_obj)?,
                Some(a) => {
                    run_probe_suite_with_snapshot(&reg_obj, &suite_obj, summarize_snapshot(&a))?
                }
            };
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };

            atomic_write(&out, &bytes)?;
        }
        Cli::RunMetamorphicSuite {
            registry,
            suite,
            snapshot,
            out,
            pretty,
        } => {
            let reg_bytes = fs::read(&registry)?;
            let suite_bytes = fs::read(&suite)?;
            let reg_obj: MetamorphicRegistrySpec = serde_json::from_slice(&reg_bytes)?;
            let suite_obj: MetamorphicSuiteSpec = serde_json::from_slice(&suite_bytes)?;

            let snapshot_obj = match snapshot {
                None => None,
                Some(path) => {
                    let b = fs::read(path)?;
                    let a: SnapshotArtifact = serde_json::from_slice(&b)?;
                    Some(a)
                }
            };
            let canonical =
                serde_json::to_vec(&(reg_obj.clone(), suite_obj.clone(), snapshot_obj.clone()))?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = match snapshot_obj {
                None => run_metamorphic_suite(&reg_obj, &suite_obj)?,
                Some(a) => run_metamorphic_suite_with_snapshot(
                    &reg_obj,
                    &suite_obj,
                    summarize_snapshot(&a),
                )?,
            };
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };

            atomic_write(&out, &bytes)?;
        }
        Cli::Snapshot { spec, out, pretty } => {
            let spec_bytes = fs::read(&spec)?;
            let spec_obj: SnapshotSpec = serde_json::from_slice(&spec_bytes)?;

            let artifact = build_snapshot(&spec_obj)?;
            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::RunSnapshot { spec, out, pretty } => {
            let spec_bytes = fs::read(&spec)?;
            let spec_obj: SnapshotSpec = serde_json::from_slice(&spec_bytes)?;

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = run_snapshot(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::RunScorecard { spec, out, pretty } => {
            let spec_bytes = fs::read(&spec)?;
            let spec_obj: ScorecardSpec = serde_json::from_slice(&spec_bytes)?;

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = run_scorecard(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::RunScorecardSuite {
            registry,
            suite,
            snapshot_run,
            out,
            pretty,
        } => {
            let reg_bytes = fs::read(&registry)?;
            let suite_bytes = fs::read(&suite)?;
            let snap_bytes = fs::read(&snapshot_run)?;
            let reg_obj: ScorecardRegistrySpec = serde_json::from_slice(&reg_bytes)?;
            let suite_obj: ScorecardSuiteSpec = serde_json::from_slice(&suite_bytes)?;
            let snap_obj: gr_engine::run_snapshot::SnapshotRunArtifact =
                serde_json::from_slice(&snap_bytes)?;

            let canonical =
                serde_json::to_vec(&(reg_obj.clone(), suite_obj.clone(), snap_obj.clone()))?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = run_scorecard_suite(&reg_obj, &suite_obj, &snap_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::ShrinkProbeRounds { spec, out, pretty } => {
            let spec_bytes = fs::read(&spec)?;
            let spec_obj: ShrinkProbeRoundsSpec = serde_json::from_slice(&spec_bytes)?;

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = shrink_probe_rounds(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::ShrinkProbeMatchups { spec, out, pretty } => {
            let spec_bytes = fs::read(&spec)?;
            let spec_obj: ShrinkProbeMatchupsSpec = serde_json::from_slice(&spec_bytes)?;

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = shrink_probe_matchups(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::ShrinkProbeReplications { spec, out, pretty } => {
            let spec_bytes = fs::read(&spec)?;
            let spec_obj: ShrinkProbeReplicationsSpec = serde_json::from_slice(&spec_bytes)?;

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = shrink_probe_replications(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::ShrinkProbePipeline { spec, out, pretty } => {
            let spec_bytes = fs::read(&spec)?;
            let spec_obj: ShrinkProbePipelineSpec = serde_json::from_slice(&spec_bytes)?;

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = shrink_probe_pipeline(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::DiffSnapshots { spec, out, pretty } => {
            let spec_bytes = fs::read(&spec)?;
            let spec_obj: SnapshotDiffSpec = serde_json::from_slice(&spec_bytes)?;

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = diff_snapshots(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::DiffSnapshotArtifacts {
            a,
            b,
            out,
            id,
            pretty,
        } => {
            let a_bytes = fs::read(&a)?;
            let b_bytes = fs::read(&b)?;
            let a_obj: SnapshotArtifact = serde_json::from_slice(&a_bytes)?;
            let b_obj: SnapshotArtifact = serde_json::from_slice(&b_bytes)?;

            let spec_obj = SnapshotArtifactDiffSpec {
                schema_version: 1,
                id,
                description: String::new(),
                a: a_obj,
                b: b_obj,
            };

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = diff_snapshot_artifacts(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::DiffProbeArtifacts {
            a,
            b,
            out,
            id,
            pretty,
        } => {
            let a_bytes = fs::read(&a)?;
            let b_bytes = fs::read(&b)?;
            let a_obj: gr_engine::probe::ProbeResultArtifact = serde_json::from_slice(&a_bytes)?;
            let b_obj: gr_engine::probe::ProbeResultArtifact = serde_json::from_slice(&b_bytes)?;

            let spec_obj = ProbeResultArtifactDiffSpec {
                schema_version: 1,
                id,
                description: String::new(),
                a: a_obj,
                b: b_obj,
            };

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = diff_probe_artifacts(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::DiffMatchArtifacts {
            a,
            b,
            out,
            id,
            pretty,
        } => {
            let a_bytes = fs::read(&a)?;
            let b_bytes = fs::read(&b)?;
            let a_obj: gr_engine::artifact::MatchArtifact = serde_json::from_slice(&a_bytes)?;
            let b_obj: gr_engine::artifact::MatchArtifact = serde_json::from_slice(&b_bytes)?;

            let spec_obj = MatchArtifactDiffSpec {
                schema_version: 1,
                id,
                description: String::new(),
                a: a_obj,
                b: b_obj,
            };

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = diff_match_artifacts(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::DiffProbeSuiteArtifacts {
            a,
            b,
            out,
            id,
            pretty,
        } => {
            let a_bytes = fs::read(&a)?;
            let b_bytes = fs::read(&b)?;
            let a_obj: gr_engine::probe::ProbeSuiteResultArtifact =
                serde_json::from_slice(&a_bytes)?;
            let b_obj: gr_engine::probe::ProbeSuiteResultArtifact =
                serde_json::from_slice(&b_bytes)?;

            let spec_obj = ProbeSuiteResultArtifactDiffSpec {
                schema_version: 1,
                id,
                description: String::new(),
                a: a_obj,
                b: b_obj,
            };

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = diff_probe_suite_artifacts(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::DiffMetamorphicArtifacts {
            a,
            b,
            out,
            id,
            pretty,
        } => {
            let a_bytes = fs::read(&a)?;
            let b_bytes = fs::read(&b)?;
            let a_obj: gr_engine::metamorphic::MetamorphicResultArtifact =
                serde_json::from_slice(&a_bytes)?;
            let b_obj: gr_engine::metamorphic::MetamorphicResultArtifact =
                serde_json::from_slice(&b_bytes)?;

            let spec_obj = MetamorphicResultArtifactDiffSpec {
                schema_version: 1,
                id,
                description: String::new(),
                a: a_obj,
                b: b_obj,
            };

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = diff_metamorphic_artifacts(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::DiffMetamorphicSuiteArtifacts {
            a,
            b,
            out,
            id,
            pretty,
        } => {
            let a_bytes = fs::read(&a)?;
            let b_bytes = fs::read(&b)?;
            let a_obj: gr_engine::metamorphic::MetamorphicSuiteResultArtifact =
                serde_json::from_slice(&a_bytes)?;
            let b_obj: gr_engine::metamorphic::MetamorphicSuiteResultArtifact =
                serde_json::from_slice(&b_bytes)?;

            let spec_obj = MetamorphicSuiteResultArtifactDiffSpec {
                schema_version: 1,
                id,
                description: String::new(),
                a: a_obj,
                b: b_obj,
            };

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = diff_metamorphic_suite_artifacts(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::DiffScorecardArtifacts {
            a,
            b,
            out,
            id,
            pretty,
        } => {
            let a_bytes = fs::read(&a)?;
            let b_bytes = fs::read(&b)?;
            let a_obj: gr_engine::scorecard::ScorecardResultArtifact =
                serde_json::from_slice(&a_bytes)?;
            let b_obj: gr_engine::scorecard::ScorecardResultArtifact =
                serde_json::from_slice(&b_bytes)?;

            let spec_obj = ScorecardResultArtifactDiffSpec {
                schema_version: 1,
                id,
                description: String::new(),
                a: a_obj,
                b: b_obj,
            };

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = diff_scorecard_artifacts(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::DiffScorecardSuiteArtifacts {
            a,
            b,
            out,
            id,
            pretty,
        } => {
            let a_bytes = fs::read(&a)?;
            let b_bytes = fs::read(&b)?;
            let a_obj: gr_engine::scorecard_suite::ScorecardSuiteResultArtifact =
                serde_json::from_slice(&a_bytes)?;
            let b_obj: gr_engine::scorecard_suite::ScorecardSuiteResultArtifact =
                serde_json::from_slice(&b_bytes)?;

            let spec_obj = ScorecardSuiteResultArtifactDiffSpec {
                schema_version: 1,
                id,
                description: String::new(),
                a: a_obj,
                b: b_obj,
            };

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = diff_scorecard_suite_artifacts(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
        Cli::DiffSnapshotRunArtifacts {
            a,
            b,
            out,
            id,
            pretty,
        } => {
            let a_bytes = fs::read(&a)?;
            let b_bytes = fs::read(&b)?;
            let a_obj: gr_engine::run_snapshot::SnapshotRunArtifact =
                serde_json::from_slice(&a_bytes)?;
            let b_obj: gr_engine::run_snapshot::SnapshotRunArtifact =
                serde_json::from_slice(&b_bytes)?;

            let spec_obj = SnapshotRunArtifactDiffSpec {
                schema_version: 1,
                id,
                description: String::new(),
                a: a_obj,
                b: b_obj,
            };

            let canonical = serde_json::to_vec(&spec_obj)?;
            let input_hash = sha256_hex(&canonical);

            let mut artifact = diff_snapshot_run_artifacts(&spec_obj)?;
            artifact.input_hash = input_hash;

            let bytes = if pretty {
                serde_json::to_vec_pretty(&artifact)?
            } else {
                serde_json::to_vec(&artifact)?
            };
            atomic_write(&out, &bytes)?;
        }
    }

    Ok(())
}
