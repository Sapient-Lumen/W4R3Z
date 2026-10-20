use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

const LEGACY_MANIFEST_SCHEMA: &str = "anonssh.i2p-bootstrap.v2";
const MANIFEST_SCHEMA: &str = "anonssh.i2p-bootstrap.v3";
const OBSERVATION_SCHEMA: &str = "anonssh.i2p-bootstrap-observations.v1";
const STATUS_SCHEMA: &str = "anonssh.i2p-bootstrap-status.v1";
const SOURCE_STATUS_SCHEMA: &str = "anonssh.i2p-bootstrap-source-status.v1";
const MANIFEST_FILE: &str = "manifest.json";
const MAXIMUM_PROFILE_SIZE: u64 = 16 * 1024;
const MINIMUM_ROUTER_INFO_SIZE: u64 = 512;
const MAXIMUM_ROUTER_INFO_SIZE: u64 = 16 * 1024;
const MAXIMUM_METADATA_SIZE: u64 = 64 * 1024 * 1024;
const MAXIMUM_CURRENT_EVIDENCE_AGE_SECS: u64 = 24 * 60 * 60;
const MAXIMUM_CLOCK_SKEW_SECS: u64 = 5 * 60;
const MINIMUM_SOURCE_OBSERVATIONS: usize = 2;
pub const DEFAULT_MINIMUM_OBSERVATION_DAYS: u64 = 3;
pub const DEFAULT_MINIMUM_OBSERVATION_SPAN_DAYS: u64 = 7;

mod embedded {
    include!(concat!(env!("OUT_DIR"), "/embedded_i2p_bootstrap.rs"));
}

#[derive(Debug, Serialize)]
pub struct ObservationReport {
    pub schema: &'static str,
    pub sources: usize,
    pub currently_corroborated: usize,
    pub first_seen: usize,
    pub observed_again: usize,
    pub total_tracked: usize,
    pub observed_at: u64,
    pub ledger: PathBuf,
}

#[derive(Debug, Eq, PartialEq, Serialize)]
pub struct ObservationDayCount {
    pub days: u64,
    pub identities: usize,
}

#[derive(Debug, Eq, PartialEq, Serialize)]
pub struct ObservationStatusReport {
    pub schema: &'static str,
    pub ledger: PathBuf,
    pub updated_at: u64,
    pub tracked: usize,
    pub minimum_observation_days: u64,
    pub minimum_observation_span_seconds: u64,
    pub observation_day_distribution: Vec<ObservationDayCount>,
    pub maximum_observation_span_seconds: u64,
    pub earliest_possible_span_completion: Option<u64>,
    pub qualifying_identities: usize,
}

#[derive(Debug, Eq, PartialEq, Serialize)]
pub struct SourceRootStatus {
    pub path: PathBuf,
    pub usable_positive_identities: usize,
    pub newest_profile_update: Option<u64>,
    pub newest_profile_age_seconds: Option<u64>,
    pub newest_router_info_modified: Option<u64>,
    pub newest_router_info_age_seconds: Option<u64>,
}

#[derive(Debug, Eq, PartialEq, Serialize)]
pub struct SourceStatusReport {
    pub schema: &'static str,
    pub policy_ready: bool,
    pub observed_at: u64,
    pub minimum_source_observations: usize,
    pub currently_corroborated: usize,
    pub sources: Vec<SourceRootStatus>,
}

#[derive(Debug, Serialize)]
pub struct CurationReport {
    pub schema: &'static str,
    pub ready: bool,
    pub sources: usize,
    pub currently_corroborated: usize,
    pub tracked: usize,
    pub selected: usize,
    pub minimum_observation_days: u64,
    pub minimum_observation_span_seconds: u64,
    pub output: PathBuf,
    pub manifest_sha256: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct ValidationReport {
    pub schema: &'static str,
    pub manifest_schema: String,
    pub entries: usize,
    pub minimum_source_observations: usize,
    pub minimum_entry_source_observations: usize,
    pub longevity_proven: bool,
    pub minimum_observation_days: Option<u64>,
    pub minimum_entry_observation_days: Option<u64>,
    pub minimum_observation_span_seconds: Option<u64>,
    pub shortest_entry_observation_span_seconds: Option<u64>,
    pub oldest_router_info_modified: u64,
    pub newest_router_info_modified: u64,
    pub oldest_router_info_age_seconds: u64,
    pub manifest_sha256: String,
}

#[derive(Debug, Default, Eq, PartialEq)]
pub struct ImportReport {
    pub available: usize,
    pub imported: usize,
    pub retained: usize,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct LegacyBootstrapManifest {
    schema: String,
    minimum_source_observations: usize,
    entries: Vec<LegacyBootstrapEntry>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct LegacyBootstrapEntry {
    identity: String,
    path: String,
    sha256: String,
    source_observations: usize,
    oldest_profile_update: u64,
    router_info_modified: u64,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct BootstrapManifest {
    schema: String,
    minimum_source_observations: usize,
    minimum_observation_days: u64,
    minimum_observation_span_seconds: u64,
    curated_at: u64,
    entries: Vec<BootstrapEntry>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct BootstrapEntry {
    identity: String,
    path: String,
    sha256: String,
    source_observations: usize,
    first_observed: u64,
    last_observed: u64,
    observation_days: u64,
    latest_profile_update: u64,
    router_info_modified: u64,
}

#[derive(Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
struct ObservationLedger {
    schema: String,
    minimum_source_observations: usize,
    updated_at: u64,
    routers: Vec<RouterObservation>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
struct RouterObservation {
    identity: String,
    first_observed: u64,
    last_observed: u64,
    observation_days: u64,
}

#[derive(Debug, Eq, PartialEq)]
struct VerifiedManifest {
    schema: String,
    minimum_source_observations: usize,
    minimum_observation_days: Option<u64>,
    minimum_observation_span_seconds: Option<u64>,
    entries: Vec<VerifiedEntry>,
}

#[derive(Debug, Eq, PartialEq)]
struct VerifiedEntry {
    identity: String,
    path: String,
    sha256: String,
    source_observations: usize,
    first_observed: Option<u64>,
    last_observed: Option<u64>,
    observation_days: Option<u64>,
    profile_update: u64,
    router_info_modified: u64,
}

#[derive(Clone, Debug)]
struct ProfileObservation {
    source_index: usize,
    router_info: PathBuf,
    router_info_modified: u64,
    update: u64,
}

#[derive(Debug)]
struct Candidate {
    identity: String,
    source_observations: usize,
    latest_profile_update: u64,
    router_info: PathBuf,
    router_info_modified: u64,
}

pub fn observe(sources: &[PathBuf], ledger: &Path) -> Result<ObservationReport> {
    observe_at(sources, ledger, unix_time()?)
}

pub fn observation_status(
    ledger: &Path,
    minimum_observation_days: u64,
    minimum_observation_span_days: u64,
) -> Result<ObservationStatusReport> {
    if !ledger.exists() {
        bail!("I2P bootstrap observation ledger does not exist");
    }
    let minimum_observation_span_seconds =
        longevity_policy(minimum_observation_days, minimum_observation_span_days)?;
    let observations = read_observation_ledger(ledger, MINIMUM_SOURCE_OBSERVATIONS)?;
    let mut day_counts = BTreeMap::new();
    let mut maximum_observation_span_seconds = 0;
    let mut earliest_possible_span_completion = None;
    let mut qualifying_identities = 0;

    for entry in &observations.routers {
        *day_counts.entry(entry.observation_days).or_insert(0) += 1;
        let span = entry.last_observed.saturating_sub(entry.first_observed);
        maximum_observation_span_seconds = maximum_observation_span_seconds.max(span);
        let span_completion = entry
            .first_observed
            .checked_add(minimum_observation_span_seconds)
            .context("I2P bootstrap span completion overflows Unix time")?;
        earliest_possible_span_completion = Some(
            earliest_possible_span_completion
                .map_or(span_completion, |current: u64| current.min(span_completion)),
        );
        if entry.observation_days >= minimum_observation_days
            && span >= minimum_observation_span_seconds
        {
            qualifying_identities += 1;
        }
    }

    Ok(ObservationStatusReport {
        schema: STATUS_SCHEMA,
        ledger: ledger.to_path_buf(),
        updated_at: observations.updated_at,
        tracked: observations.routers.len(),
        minimum_observation_days,
        minimum_observation_span_seconds,
        observation_day_distribution: day_counts
            .into_iter()
            .map(|(days, identities)| ObservationDayCount { days, identities })
            .collect(),
        maximum_observation_span_seconds,
        earliest_possible_span_completion,
        qualifying_identities,
    })
}

pub fn source_status(sources: &[PathBuf]) -> Result<SourceStatusReport> {
    source_status_at(sources, unix_time()?)
}

fn source_status_at(sources: &[PathBuf], now: u64) -> Result<SourceStatusReport> {
    let canonical_sources = canonical_sources(sources)?;
    let mut observations: BTreeMap<String, Vec<ProfileObservation>> = BTreeMap::new();
    for (source_index, source) in canonical_sources.iter().enumerate() {
        collect_source(source, source_index, now, &mut observations)?;
    }

    let mut source_identities = (0..canonical_sources.len())
        .map(|_| BTreeSet::new())
        .collect::<Vec<BTreeSet<String>>>();
    let mut newest_profile_updates = vec![None; canonical_sources.len()];
    let mut newest_router_info_modified = vec![None; canonical_sources.len()];
    for (identity, entries) in &observations {
        for entry in entries {
            source_identities[entry.source_index].insert(identity.clone());
            newest_profile_updates[entry.source_index] = Some(
                newest_profile_updates[entry.source_index]
                    .map_or(entry.update, |current: u64| current.max(entry.update)),
            );
            newest_router_info_modified[entry.source_index] = Some(
                newest_router_info_modified[entry.source_index]
                    .map_or(entry.router_info_modified, |current: u64| {
                        current.max(entry.router_info_modified)
                    }),
            );
        }
    }
    let currently_corroborated = observations
        .into_iter()
        .filter_map(|(identity, entries)| candidate(identity, entries, MINIMUM_SOURCE_OBSERVATIONS))
        .count();
    let sources = canonical_sources
        .into_iter()
        .enumerate()
        .map(|(index, path)| SourceRootStatus {
            path,
            usable_positive_identities: source_identities[index].len(),
            newest_profile_update: newest_profile_updates[index],
            newest_profile_age_seconds: newest_profile_updates[index]
                .map(|timestamp| now.saturating_sub(timestamp)),
            newest_router_info_modified: newest_router_info_modified[index],
            newest_router_info_age_seconds: newest_router_info_modified[index]
                .map(|timestamp| now.saturating_sub(timestamp)),
        })
        .collect();

    Ok(SourceStatusReport {
        schema: SOURCE_STATUS_SCHEMA,
        policy_ready: currently_corroborated > 0,
        observed_at: now,
        minimum_source_observations: MINIMUM_SOURCE_OBSERVATIONS,
        currently_corroborated,
        sources,
    })
}

pub fn curate(
    sources: &[PathBuf],
    ledger: &Path,
    output: &Path,
    minimum_observation_days: u64,
    minimum_observation_span_days: u64,
) -> Result<CurationReport> {
    curate_at(
        sources,
        ledger,
        output,
        minimum_observation_days,
        minimum_observation_span_days,
        unix_time()?,
    )
}

fn observe_at(sources: &[PathBuf], ledger: &Path, now: u64) -> Result<ObservationReport> {
    let canonical_sources = canonical_sources(sources)?;
    let candidates = current_candidates(&canonical_sources, now)?;
    let mut observations = read_observation_ledger(ledger, MINIMUM_SOURCE_OBSERVATIONS)?;
    if now < observations.updated_at {
        bail!("I2P bootstrap observation clock moved backwards");
    }
    let today = now / (24 * 60 * 60);
    let mut routers = observations
        .routers
        .drain(..)
        .map(|entry| (entry.identity.clone(), entry))
        .collect::<BTreeMap<_, _>>();
    let mut first_seen = 0;
    let mut observed_again = 0;
    for candidate in &candidates {
        match routers.get_mut(&candidate.identity) {
            Some(entry) => {
                if entry.last_observed / (24 * 60 * 60) != today {
                    entry.observation_days = entry.observation_days.saturating_add(1);
                }
                entry.last_observed = now;
                observed_again += 1;
            }
            None => {
                routers.insert(
                    candidate.identity.clone(),
                    RouterObservation {
                        identity: candidate.identity.clone(),
                        first_observed: now,
                        last_observed: now,
                        observation_days: 1,
                    },
                );
                first_seen += 1;
            }
        }
    }
    observations.updated_at = now;
    observations.routers = routers.into_values().collect();
    write_json_atomic(ledger, &observations)?;
    Ok(ObservationReport {
        schema: "anonssh.i2p-bootstrap-observation-report.v1",
        sources: canonical_sources.len(),
        currently_corroborated: candidates.len(),
        first_seen,
        observed_again,
        total_tracked: observations.routers.len(),
        observed_at: now,
        ledger: ledger.to_path_buf(),
    })
}

fn curate_at(
    sources: &[PathBuf],
    ledger: &Path,
    output: &Path,
    minimum_observation_days: u64,
    minimum_observation_span_days: u64,
    now: u64,
) -> Result<CurationReport> {
    if sources.len() < 2 {
        bail!("I2P bootstrap curation requires at least two router roots");
    }
    let minimum_observation_span_seconds =
        longevity_policy(minimum_observation_days, minimum_observation_span_days)?;
    if output.exists() {
        bail!("bootstrap output already exists: {}", output.display());
    }

    let canonical_sources = canonical_sources(sources)?;
    let current = current_candidates(&canonical_sources, now)?;
    let tracked = read_observation_ledger(ledger, MINIMUM_SOURCE_OBSERVATIONS)?;
    let tracked_count = tracked.routers.len();
    let currently_corroborated = current.len();
    let by_identity = tracked
        .routers
        .into_iter()
        .map(|entry| (entry.identity.clone(), entry))
        .collect::<BTreeMap<_, _>>();
    let candidates = current
        .into_iter()
        .filter(|candidate| {
            by_identity.get(&candidate.identity).is_some_and(|entry| {
                entry.observation_days >= minimum_observation_days
                    && entry.last_observed.saturating_sub(entry.first_observed)
                        >= minimum_observation_span_seconds
                    && entry.last_observed / (24 * 60 * 60) == now / (24 * 60 * 60)
            })
        })
        .collect::<Vec<_>>();
    if candidates.is_empty() {
        return Ok(CurationReport {
            schema: "anonssh.i2p-bootstrap-curation.v3",
            ready: false,
            sources: canonical_sources.len(),
            currently_corroborated,
            tracked: tracked_count,
            selected: 0,
            minimum_observation_days,
            minimum_observation_span_seconds,
            output: output.to_path_buf(),
            manifest_sha256: None,
        });
    }

    write_corpus(
        output,
        MINIMUM_SOURCE_OBSERVATIONS,
        minimum_observation_days,
        minimum_observation_span_seconds,
        now,
        &candidates,
        &by_identity,
    )?;
    let validation = validate_at(output, now)?;
    Ok(CurationReport {
        schema: "anonssh.i2p-bootstrap-curation.v3",
        ready: true,
        sources: canonical_sources.len(),
        currently_corroborated,
        tracked: tracked_count,
        selected: candidates.len(),
        minimum_observation_days,
        minimum_observation_span_seconds,
        output: output.to_path_buf(),
        manifest_sha256: Some(validation.manifest_sha256),
    })
}

fn longevity_policy(
    minimum_observation_days: u64,
    minimum_observation_span_days: u64,
) -> Result<u64> {
    if minimum_observation_days < 2 || minimum_observation_span_days == 0 {
        bail!("I2P bootstrap longevity policy requires multiple days and a non-zero span");
    }
    minimum_observation_span_days
        .checked_mul(24 * 60 * 60)
        .context("I2P bootstrap observation span overflows seconds")
}

pub fn import_configured(data_dir: &Path) -> Result<ImportReport> {
    match std::env::var_os("ANONSSH_I2PD_BOOTSTRAP_DIR") {
        Some(directory) => import(Path::new(&directory), data_dir),
        None => import_embedded(data_dir),
    }
}

pub fn validate(directory: &Path) -> Result<usize> {
    Ok(read_verified_manifest(directory)?.entries.len())
}

pub fn validation(directory: &Path) -> Result<ValidationReport> {
    validate_at(directory, unix_time()?)
}

pub fn validate_embedded() -> Result<usize> {
    Ok(read_embedded_manifest()?.entries.len())
}

fn import(directory: &Path, data_dir: &Path) -> Result<ImportReport> {
    let manifest = read_verified_manifest(directory)?;
    let mut report = ImportReport {
        available: manifest.entries.len(),
        ..ImportReport::default()
    };
    for entry in manifest.entries {
        let source = directory.join(&entry.path);
        let destination = data_dir.join(&entry.path);
        if destination.exists() {
            report.retained += 1;
            continue;
        }
        let parent = destination
            .parent()
            .context("bootstrap destination has no parent")?;
        fs::create_dir_all(parent)
            .with_context(|| format!("failed to create {}", parent.display()))?;
        fs::copy(&source, &destination).with_context(|| {
            format!(
                "failed to import I2P bootstrap {} to {}",
                source.display(),
                destination.display()
            )
        })?;
        report.imported += 1;
    }
    Ok(report)
}

fn import_embedded(data_dir: &Path) -> Result<ImportReport> {
    let manifest = read_embedded_manifest()?;
    let mut report = ImportReport {
        available: manifest.entries.len(),
        ..ImportReport::default()
    };
    for entry in manifest.entries {
        let destination = data_dir.join(&entry.path);
        if fs::symlink_metadata(&destination).is_ok() {
            report.retained += 1;
            continue;
        }
        let parent = destination
            .parent()
            .context("embedded bootstrap destination has no parent")?;
        fs::create_dir_all(parent)
            .with_context(|| format!("failed to create {}", parent.display()))?;
        let bytes = embedded_file(&entry.path)?;
        match OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&destination)
        {
            Ok(mut output) => {
                output.write_all(bytes).with_context(|| {
                    format!(
                        "failed to import embedded I2P bootstrap {}",
                        destination.display()
                    )
                })?;
                report.imported += 1;
            }
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {
                report.retained += 1;
            }
            Err(error) => {
                return Err(error).with_context(|| {
                    format!(
                        "failed to create embedded I2P bootstrap {}",
                        destination.display()
                    )
                });
            }
        }
    }
    Ok(report)
}

fn embedded_file(path: &str) -> Result<&'static [u8]> {
    embedded::FILES
        .iter()
        .find_map(|(candidate, bytes)| (*candidate == path).then_some(*bytes))
        .with_context(|| format!("embedded I2P bootstrap is missing {path}"))
}

fn unix_time() -> Result<u64> {
    Ok(SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .context("system clock precedes the Unix epoch")?
        .as_secs())
}

fn current_candidates(sources: &[PathBuf], now: u64) -> Result<Vec<Candidate>> {
    let mut observations: BTreeMap<String, Vec<ProfileObservation>> = BTreeMap::new();
    for (source_index, source) in sources.iter().enumerate() {
        collect_source(source, source_index, now, &mut observations)?;
    }
    let mut candidates = observations
        .into_iter()
        .filter_map(|(identity, observations)| {
            candidate(identity, observations, MINIMUM_SOURCE_OBSERVATIONS)
        })
        .collect::<Vec<_>>();
    candidates.sort_by(|left, right| left.identity.cmp(&right.identity));
    Ok(candidates)
}

fn read_observation_ledger(
    path: &Path,
    minimum_source_observations: usize,
) -> Result<ObservationLedger> {
    if !path.exists() {
        return Ok(ObservationLedger {
            schema: OBSERVATION_SCHEMA.to_owned(),
            minimum_source_observations,
            updated_at: 0,
            routers: Vec::new(),
        });
    }
    let metadata = fs::symlink_metadata(path)
        .with_context(|| format!("failed to inspect observation ledger {}", path.display()))?;
    if !metadata.file_type().is_file() || metadata.len() > MAXIMUM_METADATA_SIZE {
        bail!("I2P bootstrap observation ledger is not a bounded regular file");
    }
    parse_observation_ledger(&fs::read(path)?, minimum_source_observations)
}

fn parse_observation_ledger(
    bytes: &[u8],
    minimum_source_observations: usize,
) -> Result<ObservationLedger> {
    if bytes.len() as u64 > MAXIMUM_METADATA_SIZE {
        bail!("I2P bootstrap observation ledger exceeds the metadata limit");
    }
    let ledger: ObservationLedger =
        serde_json::from_slice(bytes).context("invalid I2P bootstrap observation ledger")?;
    if ledger.schema != OBSERVATION_SCHEMA {
        bail!("unsupported I2P bootstrap observation schema");
    }
    if ledger.minimum_source_observations != minimum_source_observations
        || minimum_source_observations < 2
    {
        bail!("I2P bootstrap observation source policy changed");
    }
    let mut identities = BTreeSet::new();
    let mut previous = None;
    for entry in &ledger.routers {
        if !valid_identity(&entry.identity) || !identities.insert(entry.identity.clone()) {
            bail!("I2P bootstrap observation ledger has an invalid or duplicate identity");
        }
        if previous
            .as_ref()
            .is_some_and(|value| value >= &entry.identity)
        {
            bail!("I2P bootstrap observation ledger is not identity-sorted");
        }
        if entry.first_observed == 0
            || entry.last_observed < entry.first_observed
            || entry.last_observed > ledger.updated_at
            || entry.observation_days == 0
        {
            bail!("I2P bootstrap observation ledger has invalid monotonic evidence");
        }
        let maximum_days = entry
            .last_observed
            .saturating_div(24 * 60 * 60)
            .saturating_sub(entry.first_observed / (24 * 60 * 60))
            .saturating_add(1);
        if entry.observation_days > maximum_days {
            bail!("I2P bootstrap observation ledger overstates distinct observation days");
        }
        previous = Some(entry.identity.clone());
    }
    Ok(ledger)
}

fn write_json_atomic<T: Serialize>(path: &Path, value: &T) -> Result<()> {
    let parent = path
        .parent()
        .context("I2P bootstrap metadata has no parent")?;
    fs::create_dir_all(parent)?;
    let name = path
        .file_name()
        .and_then(|value| value.to_str())
        .context("I2P bootstrap metadata path is not UTF-8")?;
    let temporary = parent.join(format!(".{name}.tmp-{}", std::process::id()));
    let result = (|| {
        let mut bytes = serde_json::to_vec_pretty(value)?;
        bytes.push(b'\n');
        let mut file = OpenOptions::new()
            .create_new(true)
            .write(true)
            .open(&temporary)?;
        file.write_all(&bytes)?;
        file.sync_all()?;
        fs::rename(&temporary, path)?;
        Ok::<(), anyhow::Error>(())
    })();
    if result.is_err() {
        let _ = fs::remove_file(&temporary);
    }
    result
}

fn canonical_sources(sources: &[PathBuf]) -> Result<Vec<PathBuf>> {
    if sources.len() < MINIMUM_SOURCE_OBSERVATIONS {
        bail!("I2P bootstrap observation requires at least two router roots");
    }
    let mut unique = BTreeSet::new();
    let mut canonical = Vec::with_capacity(sources.len());
    for source in sources {
        let source = fs::canonicalize(source)
            .with_context(|| format!("failed to resolve router root {}", source.display()))?;
        if !source.join("netDb").is_dir() || !source.join("peerProfiles").is_dir() {
            bail!(
                "{} is not an i2pd root with netDb and peerProfiles",
                source.display()
            );
        }
        if !unique.insert(source.clone()) {
            bail!("duplicate I2P router root {}", source.display());
        }
        canonical.push(source);
    }
    Ok(canonical)
}

fn collect_source(
    source: &Path,
    source_index: usize,
    now: u64,
    observations: &mut BTreeMap<String, Vec<ProfileObservation>>,
) -> Result<()> {
    let profiles = source.join("peerProfiles");
    for bucket in read_directories(&profiles)? {
        let bucket_name = file_name(&bucket)?;
        if !valid_bucket(&bucket_name, 'p') {
            continue;
        }
        for path in read_regular_files(&bucket)? {
            let name = file_name(&path)?;
            let Some(identity) = name
                .strip_prefix("profile-")
                .and_then(|value| value.strip_suffix(".txt"))
            else {
                continue;
            };
            if !valid_identity(identity) || bucket_name.as_bytes()[1] != identity.as_bytes()[0] {
                continue;
            }
            let metadata = fs::symlink_metadata(&path)?;
            if metadata.len() > MAXIMUM_PROFILE_SIZE {
                continue;
            }
            let Some(profile) = parse_profile(&fs::read_to_string(&path)?) else {
                continue;
            };
            if profile.update > now.saturating_add(MAXIMUM_CLOCK_SKEW_SECS)
                || now.saturating_sub(profile.update) > MAXIMUM_CURRENT_EVIDENCE_AGE_SECS
                || profile.agreed == 0
                || profile.agreed.saturating_mul(1_000)
                    < profile
                        .declined
                        .saturating_mul(1_000)
                        .saturating_add(profile.nonreplied_milli)
            {
                continue;
            }
            let router_info = source
                .join("netDb")
                .join(format!("r{}", &identity[..1]))
                .join(format!("routerInfo-{identity}.dat"));
            let Ok(router_info_metadata) = fs::symlink_metadata(&router_info) else {
                continue;
            };
            if !router_info_metadata.file_type().is_file()
                || router_info_metadata.len() < MINIMUM_ROUTER_INFO_SIZE
                || router_info_metadata.len() > MAXIMUM_ROUTER_INFO_SIZE
            {
                continue;
            }
            let Ok(router_info_modified) = router_info_metadata
                .modified()?
                .duration_since(UNIX_EPOCH)
                .map(|duration| duration.as_secs())
            else {
                continue;
            };
            if router_info_modified > now.saturating_add(MAXIMUM_CLOCK_SKEW_SECS)
                || now.saturating_sub(router_info_modified) > MAXIMUM_CURRENT_EVIDENCE_AGE_SECS
            {
                continue;
            }
            observations
                .entry(identity.to_owned())
                .or_default()
                .push(ProfileObservation {
                    source_index,
                    router_info,
                    router_info_modified,
                    update: profile.update,
                });
        }
    }
    Ok(())
}

fn candidate(
    identity: String,
    mut observations: Vec<ProfileObservation>,
    minimum_source_observations: usize,
) -> Option<Candidate> {
    observations.sort_by_key(|observation| observation.source_index);
    observations.dedup_by_key(|observation| observation.source_index);
    if observations.len() < minimum_source_observations {
        return None;
    }
    let newest_router = observations
        .iter()
        .max_by_key(|observation| observation.router_info_modified)?;
    let latest_profile_update = observations
        .iter()
        .map(|observation| observation.update)
        .max()?;
    Some(Candidate {
        identity,
        source_observations: observations.len(),
        latest_profile_update,
        router_info: newest_router.router_info.clone(),
        router_info_modified: newest_router.router_info_modified,
    })
}

fn write_corpus(
    output: &Path,
    source_count: usize,
    minimum_observation_days: u64,
    minimum_observation_span_seconds: u64,
    curated_at: u64,
    candidates: &[Candidate],
    observations: &BTreeMap<String, RouterObservation>,
) -> Result<()> {
    fs::create_dir_all(output)
        .with_context(|| format!("failed to create bootstrap output {}", output.display()))?;
    let result = (|| {
        let mut entries = Vec::with_capacity(candidates.len());
        for candidate in candidates {
            let observation = observations
                .get(&candidate.identity)
                .context("qualified router lacks observation evidence")?;
            let bytes = fs::read(&candidate.router_info)
                .with_context(|| format!("failed to read {}", candidate.router_info.display()))?;
            let bucket = format!("r{}", &candidate.identity[..1]);
            let name = format!("routerInfo-{}.dat", candidate.identity);
            let relative = Path::new("netDb").join(bucket).join(name);
            let destination = output.join(&relative);
            fs::create_dir_all(destination.parent().context("missing corpus bucket")?)?;
            fs::write(&destination, &bytes)?;
            entries.push(BootstrapEntry {
                identity: candidate.identity.clone(),
                path: path_string(&relative)?,
                sha256: hex_sha256(&bytes),
                source_observations: candidate.source_observations,
                first_observed: observation.first_observed,
                last_observed: observation.last_observed,
                observation_days: observation.observation_days,
                latest_profile_update: candidate.latest_profile_update,
                router_info_modified: candidate.router_info_modified,
            });
        }
        entries.sort_by(|left, right| left.identity.cmp(&right.identity));
        let manifest = BootstrapManifest {
            schema: MANIFEST_SCHEMA.to_owned(),
            minimum_source_observations: source_count,
            minimum_observation_days,
            minimum_observation_span_seconds,
            curated_at,
            entries,
        };
        let mut bytes = serde_json::to_vec_pretty(&manifest)?;
        bytes.push(b'\n');
        fs::write(output.join(MANIFEST_FILE), bytes)?;
        read_verified_manifest(output)?;
        Ok::<(), anyhow::Error>(())
    })();
    if result.is_err() {
        let _ = fs::remove_dir_all(output);
    }
    result
}

fn read_verified_manifest(directory: &Path) -> Result<VerifiedManifest> {
    let directory_metadata = fs::symlink_metadata(directory)
        .with_context(|| format!("missing bootstrap directory {}", directory.display()))?;
    if !directory_metadata.file_type().is_dir() {
        bail!("bootstrap path is not a directory: {}", directory.display());
    }
    let manifest_path = directory.join(MANIFEST_FILE);
    let metadata = fs::symlink_metadata(&manifest_path)
        .with_context(|| format!("missing bootstrap manifest {}", manifest_path.display()))?;
    if !metadata.file_type().is_file() || metadata.len() > MAXIMUM_METADATA_SIZE {
        bail!("bootstrap manifest is not a bounded regular file");
    }
    let manifest = parse_verified_manifest(&fs::read(&manifest_path)?)?;
    verify_manifest_files(manifest, |entry| {
        let path = directory.join(&entry.path);
        let metadata = fs::symlink_metadata(&path)
            .with_context(|| format!("missing bootstrap RouterInfo {}", path.display()))?;
        if !metadata.file_type().is_file() {
            bail!("bootstrap RouterInfo is not a regular file");
        }
        fs::read(path).context("failed to read bootstrap RouterInfo")
    })
}

fn read_embedded_manifest() -> Result<VerifiedManifest> {
    let manifest = parse_verified_manifest(embedded::MANIFEST)?;
    verify_manifest_files(manifest, |entry| Ok(embedded_file(&entry.path)?.to_vec()))
}

fn parse_verified_manifest(bytes: &[u8]) -> Result<VerifiedManifest> {
    if bytes.len() as u64 > MAXIMUM_METADATA_SIZE {
        bail!("bootstrap manifest exceeds the metadata limit");
    }
    let value: serde_json::Value =
        serde_json::from_slice(bytes).context("invalid I2P bootstrap manifest")?;
    let schema = value
        .get("schema")
        .and_then(serde_json::Value::as_str)
        .context("I2P bootstrap manifest lacks a schema")?;
    let manifest = match schema {
        LEGACY_MANIFEST_SCHEMA => {
            let legacy: LegacyBootstrapManifest =
                serde_json::from_value(value).context("invalid legacy I2P bootstrap manifest")?;
            VerifiedManifest {
                schema: legacy.schema,
                minimum_source_observations: legacy.minimum_source_observations,
                minimum_observation_days: None,
                minimum_observation_span_seconds: None,
                entries: legacy
                    .entries
                    .into_iter()
                    .map(|entry| VerifiedEntry {
                        identity: entry.identity,
                        path: entry.path,
                        sha256: entry.sha256,
                        source_observations: entry.source_observations,
                        first_observed: None,
                        last_observed: None,
                        observation_days: None,
                        profile_update: entry.oldest_profile_update,
                        router_info_modified: entry.router_info_modified,
                    })
                    .collect(),
            }
        }
        MANIFEST_SCHEMA => {
            let current: BootstrapManifest = serde_json::from_value(value)
                .context("invalid I2P bootstrap longevity manifest")?;
            if current.minimum_observation_days < 2
                || current.minimum_observation_span_seconds == 0
                || current.curated_at == 0
            {
                bail!("I2P bootstrap manifest has an invalid longevity policy");
            }
            let minimum_days = current.minimum_observation_days;
            let minimum_span = current.minimum_observation_span_seconds;
            let curated_at = current.curated_at;
            let entries = current
                .entries
                .into_iter()
                .map(|entry| {
                    if entry.first_observed == 0
                        || entry.last_observed < entry.first_observed
                        || entry.last_observed > curated_at
                        || entry.observation_days < minimum_days
                        || entry.last_observed.saturating_sub(entry.first_observed) < minimum_span
                        || entry.last_observed / (24 * 60 * 60) != curated_at / (24 * 60 * 60)
                        || entry.latest_profile_update == 0
                    {
                        bail!("I2P bootstrap entry lacks required longevity evidence");
                    }
                    Ok(VerifiedEntry {
                        identity: entry.identity,
                        path: entry.path,
                        sha256: entry.sha256,
                        source_observations: entry.source_observations,
                        first_observed: Some(entry.first_observed),
                        last_observed: Some(entry.last_observed),
                        observation_days: Some(entry.observation_days),
                        profile_update: entry.latest_profile_update,
                        router_info_modified: entry.router_info_modified,
                    })
                })
                .collect::<Result<Vec<_>>>()?;
            VerifiedManifest {
                schema: current.schema,
                minimum_source_observations: current.minimum_source_observations,
                minimum_observation_days: Some(minimum_days),
                minimum_observation_span_seconds: Some(minimum_span),
                entries,
            }
        }
        _ => bail!("unsupported I2P bootstrap manifest schema"),
    };
    if manifest.minimum_source_observations < 2 {
        bail!("I2P bootstrap manifest lacks independent source evidence");
    }
    if manifest.entries.is_empty() {
        bail!("I2P bootstrap manifest is empty");
    }

    let mut identities = BTreeSet::new();
    for entry in &manifest.entries {
        if !valid_identity(&entry.identity) || !identities.insert(entry.identity.clone()) {
            bail!("I2P bootstrap manifest has an invalid or duplicate identity");
        }
        if entry.source_observations < manifest.minimum_source_observations {
            bail!("I2P bootstrap entry lacks required source evidence");
        }
        if entry.profile_update == 0 || entry.router_info_modified == 0 {
            bail!("I2P bootstrap entry lacks profile or RouterInfo evidence");
        }
        let expected_path = format!(
            "netDb/r{}/routerInfo-{}.dat",
            &entry.identity[..1],
            entry.identity
        );
        if entry.path != expected_path || !valid_hex_sha256(&entry.sha256) {
            bail!("I2P bootstrap entry has an invalid path or digest");
        }
    }
    Ok(manifest)
}

fn verify_manifest_files(
    manifest: VerifiedManifest,
    mut load: impl FnMut(&VerifiedEntry) -> Result<Vec<u8>>,
) -> Result<VerifiedManifest> {
    for entry in &manifest.entries {
        let bytes = load(entry)?;
        if bytes.len() < MINIMUM_ROUTER_INFO_SIZE as usize
            || bytes.len() > MAXIMUM_ROUTER_INFO_SIZE as usize
        {
            bail!("bootstrap RouterInfo is not bounded: {}", entry.path);
        }
        if hex_sha256(&bytes) != entry.sha256 {
            bail!("bootstrap RouterInfo digest mismatch: {}", entry.path);
        }
    }
    Ok(manifest)
}

fn validate_at(directory: &Path, now: u64) -> Result<ValidationReport> {
    let manifest = read_verified_manifest(directory)?;
    let oldest_router_info_modified = manifest
        .entries
        .iter()
        .map(|entry| entry.router_info_modified)
        .min()
        .context("I2P bootstrap manifest has no RouterInfo evidence")?;
    let newest_router_info_modified = manifest
        .entries
        .iter()
        .map(|entry| entry.router_info_modified)
        .max()
        .context("I2P bootstrap manifest has no RouterInfo evidence")?;
    let oldest_router_info_age_seconds =
        evidence_age(now, oldest_router_info_modified, "RouterInfo")?;
    evidence_age(now, newest_router_info_modified, "RouterInfo")?;
    let minimum_entry_source_observations = manifest
        .entries
        .iter()
        .map(|entry| entry.source_observations)
        .min()
        .context("I2P bootstrap manifest has no source evidence")?;
    let manifest_bytes = fs::read(directory.join(MANIFEST_FILE))?;
    let shortest_entry_observation_span_seconds = manifest
        .entries
        .iter()
        .filter_map(|entry| Some(entry.last_observed?.saturating_sub(entry.first_observed?)))
        .min();
    let minimum_entry_observation_days = manifest
        .entries
        .iter()
        .filter_map(|entry| entry.observation_days)
        .min();
    Ok(ValidationReport {
        schema: "anonssh.i2p-bootstrap-validation.v3",
        manifest_schema: manifest.schema,
        entries: manifest.entries.len(),
        minimum_source_observations: manifest.minimum_source_observations,
        minimum_entry_source_observations,
        longevity_proven: manifest.minimum_observation_days.is_some(),
        minimum_observation_days: manifest.minimum_observation_days,
        minimum_entry_observation_days,
        minimum_observation_span_seconds: manifest.minimum_observation_span_seconds,
        shortest_entry_observation_span_seconds,
        oldest_router_info_modified,
        newest_router_info_modified,
        oldest_router_info_age_seconds,
        manifest_sha256: hex_sha256(&manifest_bytes),
    })
}

fn evidence_age(now: u64, timestamp: u64, label: &str) -> Result<u64> {
    if timestamp > now.saturating_add(MAXIMUM_CLOCK_SKEW_SECS) {
        bail!("I2P bootstrap {label} evidence is from the future");
    }
    Ok(now.saturating_sub(timestamp))
}

#[derive(Debug, Default, Eq, PartialEq)]
struct ParsedProfile {
    update: u64,
    agreed: u64,
    declined: u64,
    nonreplied_milli: u64,
}

fn parse_profile(contents: &str) -> Option<ParsedProfile> {
    let mut profile = ParsedProfile::default();
    let mut seen = BTreeSet::new();
    let mut section = "";
    for line in contents.lines() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        if let Some(value) = line
            .strip_prefix('[')
            .and_then(|line| line.strip_suffix(']'))
        {
            section = value;
            continue;
        }
        let (key, value) = line.split_once('=')?;
        let qualified = format!("{section}.{key}");
        if !seen.insert(qualified.clone()) {
            return None;
        }
        match qualified.as_str() {
            ".lastupdatetimestamp" => profile.update = value.parse().ok()?,
            "participation.agreed" => profile.agreed = value.parse().ok()?,
            "participation.declined" => profile.declined = value.parse().ok()?,
            "participation.nonreplied" => {
                let parsed = value.parse::<f64>().ok()?;
                if !parsed.is_finite() || parsed.is_sign_negative() {
                    return None;
                }
                profile.nonreplied_milli = (parsed * 1_000.0).round() as u64;
            }
            "usage.taken" | "usage.rejected" => {
                value.parse::<u64>().ok()?;
            }
            "usage.connected" => {
                value.parse::<bool>().ok()?;
            }
            _ => {}
        }
    }
    (profile.update != 0).then_some(profile)
}

fn read_directories(path: &Path) -> Result<Vec<PathBuf>> {
    let mut paths = Vec::new();
    for entry in fs::read_dir(path).with_context(|| format!("failed to read {}", path.display()))? {
        let path = entry?.path();
        if fs::symlink_metadata(&path)?.file_type().is_dir() {
            paths.push(path);
        }
    }
    paths.sort();
    Ok(paths)
}

fn read_regular_files(path: &Path) -> Result<Vec<PathBuf>> {
    let mut paths = Vec::new();
    for entry in fs::read_dir(path).with_context(|| format!("failed to read {}", path.display()))? {
        let path = entry?.path();
        if fs::symlink_metadata(&path)?.file_type().is_file() {
            paths.push(path);
        }
    }
    paths.sort();
    Ok(paths)
}

fn file_name(path: &Path) -> Result<String> {
    path.file_name()
        .and_then(|value| value.to_str())
        .map(str::to_owned)
        .with_context(|| format!("path has no UTF-8 file name: {}", path.display()))
}

fn valid_bucket(value: &str, prefix: char) -> bool {
    (value.len() == 2 && value.starts_with(prefix) && value.as_bytes()[1].is_ascii_alphanumeric())
        || value == format!("{prefix}-")
        || value == format!("{prefix}~")
}

fn valid_identity(value: &str) -> bool {
    value.len() == 44
        && value.ends_with('=')
        && value[..43]
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || byte == b'-' || byte == b'~')
}

fn path_string(path: &Path) -> Result<String> {
    path.to_str()
        .map(|value| value.replace(std::path::MAIN_SEPARATOR, "/"))
        .context("bootstrap path is not UTF-8")
}

fn hex_sha256(bytes: &[u8]) -> String {
    let digest = Sha256::digest(bytes);
    digest.iter().map(|byte| format!("{byte:02x}")).collect()
}

fn valid_hex_sha256(value: &str) -> bool {
    value.len() == 64
        && value
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
}

pub const BOOTSTRAP_FUZZ_SEED: u64 = 0x414e_4f4e_5353_4803;
pub const DEFAULT_BOOTSTRAP_FUZZ_CASES: u32 = 1_024;
const MAXIMUM_FUZZ_INPUT_SIZE: usize = 8 * 1024;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct BootstrapFuzzCounts {
    pub cases: u32,
    pub accepted: u32,
    pub rejected: u32,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct BootstrapFuzzReport {
    pub seed: u64,
    pub manifest: BootstrapFuzzCounts,
    pub observation_ledger: BootstrapFuzzCounts,
    pub peer_profile: BootstrapFuzzCounts,
}

pub fn embedded_bootstrap_fuzz_test() -> Result<BootstrapFuzzReport> {
    bootstrap_fuzz_test(BOOTSTRAP_FUZZ_SEED, DEFAULT_BOOTSTRAP_FUZZ_CASES)
}

pub fn bootstrap_fuzz_test(seed: u64, cases_per_parser: u32) -> Result<BootstrapFuzzReport> {
    if seed == 0 || cases_per_parser < 16 {
        bail!("invalid I2P bootstrap fuzz configuration");
    }
    let observation_seed = serde_json::to_vec(&ObservationLedger {
        schema: OBSERVATION_SCHEMA.to_owned(),
        minimum_source_observations: 2,
        updated_at: 8 * 24 * 60 * 60,
        routers: vec![RouterObservation {
            identity: format!("A{}=", "a".repeat(42)),
            first_observed: 24 * 60 * 60,
            last_observed: 8 * 24 * 60 * 60,
            observation_days: 3,
        }],
    })?;
    let profile_seed = b"lastupdatetimestamp=100\n[participation]\nagreed=9\ndeclined=1\nnonreplied=0.5\n[usage]\ntaken=2\nrejected=0\nconnected=true\n";
    let mut random = BootstrapFuzzRandom::new(seed);
    let manifest = exercise_bootstrap_parser(
        "manifest",
        embedded::MANIFEST,
        cases_per_parser,
        &mut random,
        fuzz_manifest_case,
    )?;
    let observation_ledger = exercise_bootstrap_parser(
        "observation-ledger",
        &observation_seed,
        cases_per_parser,
        &mut random,
        fuzz_observation_case,
    )?;
    let peer_profile = exercise_bootstrap_parser(
        "peer-profile",
        profile_seed,
        cases_per_parser,
        &mut random,
        fuzz_profile_case,
    )?;
    Ok(BootstrapFuzzReport {
        seed,
        manifest,
        observation_ledger,
        peer_profile,
    })
}

fn exercise_bootstrap_parser(
    family: &str,
    seed: &[u8],
    cases: u32,
    random: &mut BootstrapFuzzRandom,
    parse: fn(&[u8]) -> Result<bool>,
) -> Result<BootstrapFuzzCounts> {
    let mut counts = BootstrapFuzzCounts {
        cases,
        accepted: 0,
        rejected: 0,
    };
    for case in 0..cases {
        let input = mutate_bootstrap_input(seed, case, random);
        if parse(&input)? {
            counts.accepted += 1;
        } else {
            counts.rejected += 1;
        }
    }
    if counts.accepted == 0 || counts.rejected == 0 {
        bail!(
            "I2P bootstrap fuzz family {family} lacks mixed coverage (accepted={}, rejected={})",
            counts.accepted,
            counts.rejected
        );
    }
    Ok(counts)
}

fn fuzz_manifest_case(input: &[u8]) -> Result<bool> {
    let Ok(manifest) = parse_verified_manifest(input) else {
        return Ok(false);
    };
    if manifest.entries.is_empty() || manifest.minimum_source_observations < 2 {
        bail!("accepted fuzz manifest violates verified bounds");
    }
    let value: serde_json::Value = serde_json::from_slice(input)?;
    let canonical = serde_json::to_vec(&value)?;
    let reparsed = parse_verified_manifest(&canonical)
        .context("accepted fuzz manifest did not survive canonical JSON encoding")?;
    if manifest != reparsed {
        bail!("accepted fuzz manifest changed across canonical JSON encoding");
    }
    Ok(true)
}

fn fuzz_observation_case(input: &[u8]) -> Result<bool> {
    let Ok(ledger) = parse_observation_ledger(input, 2) else {
        return Ok(false);
    };
    let canonical = serde_json::to_vec(&ledger)?;
    let reparsed = parse_observation_ledger(&canonical, 2)
        .context("accepted fuzz observation ledger did not survive canonical encoding")?;
    if ledger != reparsed {
        bail!("accepted fuzz observation ledger changed across canonical encoding");
    }
    Ok(true)
}

fn fuzz_profile_case(input: &[u8]) -> Result<bool> {
    let Ok(contents) = std::str::from_utf8(input) else {
        return Ok(false);
    };
    let Some(profile) = parse_profile(contents) else {
        return Ok(false);
    };
    let nonreplied = format!(
        "{}.{:03}",
        profile.nonreplied_milli / 1_000,
        profile.nonreplied_milli % 1_000
    );
    let canonical = format!(
        "lastupdatetimestamp={}\n[participation]\nagreed={}\ndeclined={}\nnonreplied={nonreplied}\n",
        profile.update, profile.agreed, profile.declined
    );
    if parse_profile(&canonical).as_ref() != Some(&profile) {
        bail!("accepted fuzz peer profile changed across canonical encoding");
    }
    Ok(true)
}

fn mutate_bootstrap_input(seed: &[u8], case: u32, random: &mut BootstrapFuzzRandom) -> Vec<u8> {
    match case % 8 {
        0 => seed.to_vec(),
        1 => seed[..random.bounded(seed.len().saturating_add(1))].to_vec(),
        2 => {
            let mut input = seed.to_vec();
            input.extend_from_slice(b" trailing");
            input
        }
        3 => {
            let mut input = seed.to_vec();
            if !input.is_empty() {
                let index = random.bounded(input.len());
                input[index] ^= 1 << random.bounded(8);
            }
            input
        }
        4 => {
            let mut input = seed.to_vec();
            if !input.is_empty() {
                let index = random.bounded(input.len());
                input[index] = 0xff;
            }
            input
        }
        5 => {
            let mut input = vec![0; random.bounded(MAXIMUM_FUZZ_INPUT_SIZE + 1)];
            random.fill(&mut input);
            input
        }
        6 => vec![b' '; random.bounded(seed.len().min(MAXIMUM_FUZZ_INPUT_SIZE) + 1)],
        _ => {
            let mut input = seed.to_vec();
            for _ in 0..4 {
                if input.is_empty() {
                    break;
                }
                let index = random.bounded(input.len());
                input[index] ^= (random.next_u64() as u8) | 1;
            }
            input
        }
    }
}

struct BootstrapFuzzRandom(u64);

impl BootstrapFuzzRandom {
    const fn new(seed: u64) -> Self {
        Self(seed)
    }

    fn next_u64(&mut self) -> u64 {
        let mut value = self.0;
        value ^= value << 13;
        value ^= value >> 7;
        value ^= value << 17;
        self.0 = value;
        value
    }

    fn bounded(&mut self, upper_exclusive: usize) -> usize {
        if upper_exclusive == 0 {
            0
        } else {
            (self.next_u64() as usize) % upper_exclusive
        }
    }

    fn fill(&mut self, output: &mut [u8]) {
        for chunk in output.chunks_mut(8) {
            let bytes = self.next_u64().to_le_bytes();
            chunk.copy_from_slice(&bytes[..chunk.len()]);
        }
    }
}

#[cfg(test)]
mod tests {
    use std::sync::atomic::{AtomicUsize, Ordering};

    use super::{
        curate_at, embedded, hex_sha256, import, import_embedded, observation_status, observe_at,
        parse_profile, read_observation_ledger, source_status_at, validate, validate_at,
        validate_embedded, write_json_atomic, LegacyBootstrapEntry, LegacyBootstrapManifest,
        LEGACY_MANIFEST_SCHEMA, MAXIMUM_CLOCK_SKEW_SECS,
    };

    static NEXT_ROOT: AtomicUsize = AtomicUsize::new(0);

    struct TestRoot(std::path::PathBuf);

    impl TestRoot {
        fn new(label: &str) -> Self {
            let path = std::env::temp_dir().join(format!(
                "anonssh-bootstrap-{label}-{}-{}",
                std::process::id(),
                NEXT_ROOT.fetch_add(1, Ordering::Relaxed)
            ));
            std::fs::create_dir_all(&path).unwrap();
            Self(path)
        }
    }

    impl Drop for TestRoot {
        fn drop(&mut self) {
            let _ = std::fs::remove_dir_all(&self.0);
        }
    }

    #[test]
    fn profile_parser_rejects_duplicates_and_bad_numbers() {
        let valid = "lastupdatetimestamp=100\n[participation]\nagreed=9\ndeclined=1\nnonreplied=0.5\n[usage]\ntaken=2\nrejected=0\nconnected=true\n";
        let profile = parse_profile(valid).unwrap();
        assert_eq!(profile.nonreplied_milli, 500);
        assert!(parse_profile(&format!("{valid}[participation]\nagreed=10\n")).is_none());
        assert!(parse_profile(&valid.replace("0.5", "NaN")).is_none());
    }

    #[test]
    fn deterministic_bootstrap_campaign_has_mixed_coverage() {
        let first = super::bootstrap_fuzz_test(super::BOOTSTRAP_FUZZ_SEED, 128).unwrap();
        let second = super::bootstrap_fuzz_test(super::BOOTSTRAP_FUZZ_SEED, 128).unwrap();
        assert_eq!(first, second);
        for counts in [first.manifest, first.observation_ledger, first.peer_profile] {
            assert_eq!(counts.accepted + counts.rejected, counts.cases);
            assert!(counts.accepted > 0);
            assert!(counts.rejected > 0);
        }
    }

    #[test]
    fn embedded_corpus_validates_imports_and_never_overwrites_state() {
        let state = TestRoot::new("embedded-state");
        let entries = validate_embedded().unwrap();
        assert_eq!(entries, embedded::FILES.len());
        assert!(entries > 0);

        let first = import_embedded(&state.0).unwrap();
        assert_eq!(first.available, entries);
        assert_eq!(first.imported, entries);
        assert_eq!(first.retained, 0);

        let retained_path = state.0.join(embedded::FILES[0].0);
        std::fs::write(&retained_path, b"operator-owned replacement").unwrap();
        let second = import_embedded(&state.0).unwrap();
        assert_eq!(second.imported, 0);
        assert_eq!(second.retained, entries);
        assert_eq!(
            std::fs::read(retained_path).unwrap(),
            b"operator-owned replacement"
        );
    }

    #[test]
    fn longevity_ledger_is_daily_uncapped_and_required_for_curation() {
        let source_a = TestRoot::new("source-a");
        let source_b = TestRoot::new("source-b");
        let source_c = TestRoot::new("source-c");
        let output = TestRoot::new("output-parent");
        let output_path = output.0.join("corpus");
        let ledger_path = output.0.join("observations.json");
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();
        for index in 0..300 {
            let identity = format!("A{index:03}{}=", "a".repeat(39));
            write_candidate(&source_a.0, &identity, now, index);
            write_candidate(&source_b.0, &identity, now, index);
        }
        std::fs::create_dir_all(source_c.0.join("peerProfiles")).unwrap();
        std::fs::create_dir_all(source_c.0.join("netDb")).unwrap();

        let sources = [source_a.0.clone(), source_b.0.clone()];
        let first = observe_at(&sources, &ledger_path, now).unwrap();
        assert_eq!(first.currently_corroborated, 300);
        assert_eq!(first.first_seen, 300);
        let initial_status = observation_status(&ledger_path, 3, 7).unwrap();
        assert_eq!(initial_status.schema, "anonssh.i2p-bootstrap-status.v1");
        assert_eq!(initial_status.tracked, 300);
        assert_eq!(initial_status.observation_day_distribution.len(), 1);
        assert_eq!(initial_status.observation_day_distribution[0].days, 1);
        assert_eq!(
            initial_status.observation_day_distribution[0].identities,
            300
        );
        assert_eq!(initial_status.maximum_observation_span_seconds, 0);
        assert_eq!(
            initial_status.earliest_possible_span_completion,
            Some(now + 7 * 24 * 60 * 60)
        );
        assert_eq!(initial_status.qualifying_identities, 0);
        assert!(observation_status(&ledger_path, 1, 7).is_err());
        assert!(observation_status(&ledger_path, 3, 0).is_err());
        assert!(observation_status(&output.0.join("missing.json"), 3, 7).is_err());
        let source_status = source_status_at(&sources, now).unwrap();
        assert!(source_status.policy_ready);
        assert_eq!(source_status.currently_corroborated, 300);
        assert_eq!(source_status.sources.len(), 2);
        assert!(source_status
            .sources
            .iter()
            .all(|source| source.usable_positive_identities == 300));
        assert!(source_status
            .sources
            .iter()
            .all(|source| source.newest_profile_age_seconds == Some(0)));
        let same_day = observe_at(&sources, &ledger_path, now + 1).unwrap();
        assert_eq!(same_day.first_seen, 0);
        assert_eq!(same_day.observed_again, 300);
        let expanded_sources = [source_a.0.clone(), source_b.0.clone(), source_c.0.clone()];
        let expanded = observe_at(&expanded_sources, &ledger_path, now + 2).unwrap();
        assert_eq!(expanded.sources, 3);
        assert_eq!(expanded.currently_corroborated, 300);
        let degraded_sources = [source_a.0.clone(), source_c.0.clone()];
        let degraded_status = source_status_at(&degraded_sources, now + 2).unwrap();
        assert!(!degraded_status.policy_ready);
        assert_eq!(degraded_status.currently_corroborated, 0);
        assert_eq!(degraded_status.sources[0].usable_positive_identities, 300);
        assert_eq!(degraded_status.sources[1].usable_positive_identities, 0);
        let mut observations = read_observation_ledger(&ledger_path, 2).unwrap();
        assert!(observations
            .routers
            .iter()
            .all(|entry| entry.observation_days == 1));
        let premature = curate_at(&sources, &ledger_path, &output_path, 3, 7, now + 2).unwrap();
        assert!(!premature.ready);
        assert_eq!(premature.selected, 0);
        assert!(!output_path.exists());

        for entry in &mut observations.routers {
            entry.first_observed = now - 7 * 24 * 60 * 60;
            entry.last_observed = now;
            entry.observation_days = 3;
        }
        observations.updated_at = now;
        write_json_atomic(&ledger_path, &observations).unwrap();

        let qualifying_status = observation_status(&ledger_path, 3, 7).unwrap();
        assert_eq!(
            qualifying_status.maximum_observation_span_seconds,
            7 * 24 * 60 * 60
        );
        assert_eq!(qualifying_status.qualifying_identities, 300);

        let report = curate_at(&sources, &ledger_path, &output_path, 3, 7, now).unwrap();
        assert!(report.ready);
        assert_eq!(report.selected, 300);
        assert_eq!(report.schema, "anonssh.i2p-bootstrap-curation.v3");
        assert_eq!(report.manifest_sha256.unwrap().len(), 64);
        assert_eq!(validate(&output_path).unwrap(), 300);

        let current = validate_at(&output_path, now).unwrap();
        assert!(current.longevity_proven);
        assert_eq!(current.entries, 300);
        assert_eq!(current.minimum_source_observations, 2);
        assert_eq!(current.minimum_entry_source_observations, 2);
        assert_eq!(current.minimum_entry_observation_days, Some(3));
        let old = validate_at(&output_path, now + 365 * 24 * 60 * 60).unwrap();
        assert!(old.oldest_router_info_age_seconds >= 365 * 24 * 60 * 60);
        let before_allowed_skew = current
            .newest_router_info_modified
            .checked_sub(MAXIMUM_CLOCK_SKEW_SECS + 1)
            .unwrap();
        assert!(validate_at(&output_path, before_allowed_skew).is_err());

        let state = TestRoot::new("state");
        let first_import = import(&output_path, &state.0).unwrap();
        assert_eq!(first_import.imported, 300);
        let second = import(&output_path, &state.0).unwrap();
        assert_eq!(second.imported, 0);
        assert_eq!(second.retained, 300);

        let router_info = std::fs::read_dir(output_path.join("netDb/rA"))
            .unwrap()
            .next()
            .unwrap()
            .unwrap()
            .path();
        std::fs::write(router_info, vec![7_u8; 700]).unwrap();
        assert!(validate(&output_path).is_err());
    }

    #[test]
    fn legacy_manifest_remains_importable_without_claiming_longevity() {
        let corpus = TestRoot::new("legacy-corpus");
        let state = TestRoot::new("legacy-state");
        let identity = format!("A{}=", "a".repeat(42));
        let relative = format!("netDb/rA/routerInfo-{identity}.dat");
        let bytes = vec![9_u8; 700];
        let path = corpus.0.join(&relative);
        std::fs::create_dir_all(path.parent().unwrap()).unwrap();
        std::fs::write(&path, &bytes).unwrap();
        let manifest = LegacyBootstrapManifest {
            schema: LEGACY_MANIFEST_SCHEMA.to_owned(),
            minimum_source_observations: 2,
            entries: vec![LegacyBootstrapEntry {
                identity,
                path: relative,
                sha256: hex_sha256(&bytes),
                source_observations: 2,
                oldest_profile_update: 100,
                router_info_modified: 100,
            }],
        };
        write_json_atomic(&corpus.0.join("manifest.json"), &manifest).unwrap();

        let report = validate_at(&corpus.0, 10_000).unwrap();
        assert!(!report.longevity_proven);
        assert_eq!(report.minimum_observation_days, None);
        assert_eq!(import(&corpus.0, &state.0).unwrap().imported, 1);
    }

    fn write_candidate(root: &std::path::Path, identity: &str, now: u64, index: usize) {
        let bucket = &identity[..1];
        let profile_dir = root.join("peerProfiles").join(format!("p{bucket}"));
        let router_dir = root.join("netDb").join(format!("r{bucket}"));
        std::fs::create_dir_all(&profile_dir).unwrap();
        std::fs::create_dir_all(&router_dir).unwrap();
        std::fs::write(
            profile_dir.join(format!("profile-{identity}.txt")),
            format!(
                "lastupdatetimestamp={now}\n[participation]\nagreed={}\ndeclined=1\nnonreplied=0.5\n[usage]\ntaken=2\nrejected=0\nconnected=true\n",
                100 + index
            ),
        )
        .unwrap();
        std::fs::write(
            router_dir.join(format!("routerInfo-{identity}.dat")),
            vec![u8::try_from(index % 251).unwrap(); 700],
        )
        .unwrap();
    }
}
