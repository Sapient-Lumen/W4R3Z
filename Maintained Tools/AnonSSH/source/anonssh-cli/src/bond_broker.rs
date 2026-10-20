use std::collections::{BTreeMap, VecDeque};
use std::fs;
use std::future::Future;
use std::io::{self, IsTerminal};
use std::os::fd::{AsRawFd, FromRawFd, OwnedFd, RawFd};
use std::os::unix::fs::{DirBuilderExt, FileTypeExt, MetadataExt, PermissionsExt};
use std::path::{Path, PathBuf};
use std::pin::Pin;
use std::process::{Command, Stdio};
use std::sync::Arc;
use std::task::{ready, Context as TaskContext, Poll};
use std::time::Duration;

use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use subtle::ConstantTimeEq;
use tokio::io::{
    unix::AsyncFd, AsyncRead, AsyncReadExt, AsyncWrite, AsyncWriteExt, BufReader, ReadBuf,
};
use tokio::net::{TcpStream, UnixListener, UnixStream};
use tokio::sync::{watch, Mutex, OnceCell};
use tokio::task::{JoinHandle, JoinSet};
use tokio::time::{sleep, timeout, Instant};
use tracing::warn;
use zeroize::Zeroizing;

use crate::bond_transport::{ClientBondSession, ResourceGovernorSnapshot, SharedResourceGovernor};
use crate::embedded_runtime::StoragePolicyReport;
use crate::identity::DerivedClientRecoveryIdentity;
use crate::local_transport::{
    AlpDialRequest, AlpErrorCode, AlpResult, AlpTransport, DEFAULT_SETUP_DEADLINE,
};
use crate::product_config::{ProductConfig, ResidentServicePolicy, ResourceProfile, ScalingPolicy};
use crate::router_pool::{
    RouterPool, RouterProgressPhase, RouterProgressSnapshot, RouterProvider, PRODUCTION_I2P_SLOTS,
    PRODUCTION_TOR_SLOTS,
};
use crate::runtime::{resolve_executable, AppConfig};
use crate::sam::SamConnector;
use crate::tor_transport::TorConnector;

const REQUEST_MAGIC: [u8; 4] = *b"ABR3";
const RESPONSE_READY: [u8; 4] = *b"ABO1";
const RESPONSE_FAILED: [u8; 4] = *b"ABE1";
const RESPONSE_POLICY_MISMATCH: [u8; 4] = *b"ABM1";
const RESPONSE_PROGRESS: [u8; 4] = *b"ABG1";
const RESPONSE_AUTO_REPORT: [u8; 4] = *b"ABU1";
const REQUEST_BOND: u8 = 1;
const REQUEST_TOR: u8 = 2;
const REQUEST_I2P: u8 = 3;
const REQUEST_STATUS: u8 = 4;
const REQUEST_STOP: u8 = 5;
const REQUEST_AUTO: u8 = 6;
const REQUEST_AUTHORIZE: u8 = 7;
const RESPONSE_STATUS: [u8; 4] = *b"ABS1";
const MAX_DESTINATION_BYTES: usize = 4_096;
const MAX_RECENT_STREAMS: usize = 64;
const SOCKET_START_DEADLINE: Duration = Duration::from_secs(10);
const SESSION_START_DEADLINE: Duration = Duration::from_secs(900);
const STALE_LEASE_GRACE: Duration = Duration::from_secs(2);
const BROKER_IDLE_TIMEOUT: Duration = Duration::from_secs(30 * 60);
const WARM_ROUTER_HEALTH_INTERVAL: Duration = Duration::from_secs(30);
const WARM_ROUTER_RETRY_INTERVAL: Duration = Duration::from_secs(5);
const WARM_POLICY_INTERVAL: Duration = Duration::from_secs(5);
const WARM_MINIMUM_RETENTION: Duration = Duration::from_secs(5 * 60);
const WARM_MAXIMUM_RETENTION: Duration = Duration::from_secs(60 * 60);
const PROGRESS_INTERVAL: Duration = Duration::from_secs(2);
const MAX_PROGRESS_BYTES: usize = 64 * 1024;
const MAX_AUTHORIZED_TARGETS: usize = 64;
const AUTHORIZATION_IDLE_TIMEOUT: Duration = Duration::from_secs(12 * 60 * 60);
const AUTO_WINNER_SETTLE: Duration = Duration::from_millis(10);
const AUTO_TOR_ONLY_DELAY: Duration = Duration::from_secs(1);
const AUTO_I2P_ONLY_DELAY: Duration = Duration::from_secs(2);
const AUTO_DIRECT_TOR_DELAY: Duration = Duration::from_secs(5);
const AUTO_DIRECT_I2P_DELAY: Duration = Duration::from_secs(10);
const AUTO_BOND_TOR_DEADLINE: Duration = Duration::from_secs(600);
const AUTO_BOND_I2P_DEADLINE: Duration = Duration::from_secs(840);
const AUTO_DIRECT_TOR_DEADLINE: Duration = Duration::from_secs(360);
const AUTO_DIRECT_I2P_DEADLINE: Duration = Duration::from_secs(840);
const VERBOSE_OUTPUT_ENV: &str = "ANONSSH_VERBOSE_OUTPUT";
pub(crate) const QUIET_OUTPUT_ENV: &str = "ANONSSH_QUIET_OUTPUT";

type SessionRegistry = Mutex<BTreeMap<[u8; 32], Arc<SessionEntry>>>;
type AuthorizationRegistry = Mutex<BTreeMap<String, AuthorizedTarget>>;

struct AuthorizedTarget {
    request: BondRequest,
    last_used: Instant,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum DirectProvider {
    Tor,
    I2p,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "kebab-case")]
enum AutoRoute {
    BondMixed,
    BondTor,
    BondI2p,
    Tor,
    I2p,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "kebab-case")]
enum AutoAttemptOutcome {
    Succeeded,
    Failed,
    TimedOut,
    Canceled,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
struct AutoRouteAttempt {
    route: AutoRoute,
    start_delay_millis: u64,
    completed_millis: Option<u64>,
    outcome: AutoAttemptOutcome,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
struct AutoRouteReport {
    schema: String,
    winner: AutoRoute,
    elapsed_millis: u64,
    attempts: Vec<AutoRouteAttempt>,
}

#[derive(Clone, Copy)]
struct AutoCandidateSpec {
    route: AutoRoute,
    start_delay: Duration,
    deadline: Duration,
}

#[derive(Debug)]
struct AutoRaceWinner<T> {
    value: T,
    report: AutoRouteReport,
}

enum AutoCandidateOutcome<T> {
    Succeeded(T),
    Failed(String),
    TimedOut,
}

struct AutoCandidateCompletion<T> {
    spec: AutoCandidateSpec,
    completed_millis: u64,
    outcome: AutoCandidateOutcome<T>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct BrokerStatus {
    pub schema: String,
    pub running: bool,
    #[serde(default)]
    pub resident: bool,
    pub process_id: Option<u32>,
    pub router_pool_instances: usize,
    #[serde(default)]
    pub authorized_targets: usize,
    pub bond_sessions: usize,
    pub bond_session_ids: Vec<u64>,
    #[serde(default)]
    pub bond_session_topologies: Vec<BrokerBondSessionStatus>,
    #[serde(default)]
    pub recent_bond_streams: Vec<BrokerBondStreamStatus>,
    pub recent_bond_stream_ids: Vec<u64>,
    pub tor_routers_running: usize,
    pub i2p_routers_running: usize,
    #[serde(default)]
    pub resource_profile: Option<ResourceProfile>,
    #[serde(default)]
    pub scaling_policy: Option<ScalingPolicy>,
    #[serde(default)]
    pub resource_governor: Option<ResourceGovernorSnapshot>,
    #[serde(default)]
    pub resident_policy: Option<ResidentServicePolicy>,
    #[serde(default)]
    pub warm_pool: Option<ResidentWarmPoolStatus>,
    #[serde(default)]
    pub storage_policy: Option<StoragePolicyReport>,
    #[serde(default)]
    pub router_progress: RouterProgressSnapshot,
}

#[derive(Clone, Copy, Debug, Default, Deserialize, Eq, PartialEq, Serialize)]
pub struct ResidentWarmPoolStatus {
    pub tor_target: usize,
    pub i2p_target: usize,
    pub tor_demanded: usize,
    pub i2p_demanded: usize,
    pub minimum_per_provider: usize,
    pub maximum_per_provider: usize,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, Ord, PartialEq, PartialOrd, Serialize)]
pub struct BrokerBondStreamStatus {
    pub session_id: u64,
    pub stream_id: u64,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct BrokerBondSessionStatus {
    pub session_id: u64,
    pub topology: String,
    pub candidate_lanes: usize,
    pub active_lane_ids: Vec<u64>,
    pub statistics_available: bool,
}

impl BrokerStatus {
    fn stopped() -> Self {
        Self {
            schema: "anonssh.broker-status.v8".to_owned(),
            running: false,
            resident: false,
            process_id: None,
            router_pool_instances: 0,
            authorized_targets: 0,
            bond_sessions: 0,
            bond_session_ids: Vec::new(),
            bond_session_topologies: Vec::new(),
            recent_bond_streams: Vec::new(),
            recent_bond_stream_ids: Vec::new(),
            tor_routers_running: 0,
            i2p_routers_running: 0,
            resource_profile: None,
            scaling_policy: None,
            resource_governor: None,
            resident_policy: None,
            warm_pool: None,
            storage_policy: None,
            router_progress: RouterProgressSnapshot::empty(),
        }
    }
}

pub async fn status() -> Result<BrokerStatus> {
    let paths = BrokerPaths::for_user()?;
    let mut stream = match UnixStream::connect(&paths.socket).await {
        Ok(stream) => stream,
        Err(error) if broker_is_absent(&error) => return Ok(BrokerStatus::stopped()),
        Err(error) => return Err(error).context("failed to connect to the AnonSSH bond broker"),
    };
    BrokerRequest::Status.write_to(&mut stream).await?;
    let mut response = [0_u8; 4];
    stream.read_exact(&mut response).await?;
    if response != RESPONSE_STATUS {
        bail!("bond broker returned an unsupported status response");
    }
    let length = usize::try_from(stream.read_u32().await?)
        .context("bond broker status length overflowed")?;
    if length == 0 || length > 64 * 1024 {
        bail!("bond broker returned an invalid status length");
    }
    let mut encoded = vec![0_u8; length];
    stream.read_exact(&mut encoded).await?;
    serde_json::from_slice(&encoded).context("bond broker returned invalid status JSON")
}

pub async fn stop() -> Result<bool> {
    let paths = BrokerPaths::for_user()?;
    let mut stream = match UnixStream::connect(&paths.socket).await {
        Ok(stream) => stream,
        Err(error) if broker_is_absent(&error) => return Ok(false),
        Err(error) => return Err(error).context("failed to connect to the AnonSSH bond broker"),
    };
    BrokerRequest::Stop.write_to(&mut stream).await?;
    let mut response = [0_u8; 4];
    stream.read_exact(&mut response).await?;
    if response != RESPONSE_READY {
        bail!("bond broker rejected the stop request");
    }
    Ok(true)
}

pub async fn proxy(
    tor_destinations: &[String],
    i2p_destinations: &[String],
    key_file: &Path,
    resource_profile: ResourceProfile,
) -> Result<()> {
    proxy_request(BrokerRequest::Bond(BondRequest::from_key_file(
        tor_destinations,
        i2p_destinations,
        key_file,
        resource_profile,
    )?))
    .await
}

pub async fn auto_proxy(
    tor_destinations: &[String],
    i2p_destinations: &[String],
    direct_tor_destination: &str,
    direct_i2p_destination: &str,
    key_file: &Path,
    resource_profile: ResourceProfile,
) -> Result<()> {
    proxy_request(BrokerRequest::Auto(AutoRequest::from_key_file(
        tor_destinations,
        i2p_destinations,
        direct_tor_destination,
        direct_i2p_destination,
        key_file,
        resource_profile,
    )?))
    .await
}

pub async fn direct_proxy(provider: DirectProvider, destination: &str) -> Result<()> {
    validate_destination(provider.label(), destination)?;
    let request = match provider {
        DirectProvider::Tor => BrokerRequest::Tor(destination.to_owned()),
        DirectProvider::I2p => BrokerRequest::I2p(destination.to_owned()),
    };
    proxy_request(request).await
}

pub async fn authorize_target(
    target: &str,
    identity: &DerivedClientRecoveryIdentity,
    resource_profile: ResourceProfile,
) -> Result<()> {
    crate::local_transport::validate_target(target)?;
    start(true).await?;
    let request = BondRequest::new(
        identity.tor_pool_destinations.clone(),
        identity
            .i2p_pool
            .iter()
            .map(|derived| derived.destination.clone())
            .collect(),
        Zeroizing::new(*identity.bond_session_key),
        resource_profile,
    )?;
    let paths = BrokerPaths::for_user()?;
    let mut stream = UnixStream::connect(&paths.socket)
        .await
        .context("failed to connect to the AnonSSH broker control socket")?;
    BrokerRequest::Authorize {
        target: target.to_owned(),
        request,
    }
    .write_to(&mut stream)
    .await?;
    let mut response = [0_u8; 4];
    stream.read_exact(&mut response).await?;
    if response != RESPONSE_READY {
        bail!("bond broker rejected target authorization");
    }
    Ok(())
}

pub async fn dial_service(request: AlpDialRequest) -> Result<()> {
    request.validate()?;
    let expected_request_id = request.request_id.clone();
    let paths = BrokerPaths::for_user()?;
    let mut stream = UnixStream::connect(&paths.transport_socket)
        .await
        .context("ALP transport is unavailable; run `anonssh authorize user@machine-id`")?;
    crate::local_transport::write_record(&mut stream, &request).await?;
    let result: AlpResult = timeout(
        request.deadline().min(DEFAULT_SETUP_DEADLINE),
        crate::local_transport::read_record(&mut stream),
    )
    .await
    .context("ALP broker response timed out")??;
    if result.request_id != expected_request_id {
        bail!("ALP broker returned a mismatched request ID");
    }
    result.into_ready()?;
    relay_stdio(stream).await
}

impl DirectProvider {
    const fn label(self) -> &'static str {
        match self {
            Self::Tor => "Tor",
            Self::I2p => "I2P",
        }
    }
}

async fn proxy_request(request: BrokerRequest) -> Result<()> {
    let paths = BrokerPaths::for_user()?;
    let mut stream = match UnixStream::connect(&paths.socket).await {
        Ok(stream) => stream,
        Err(error) if broker_is_absent(&error) => {
            spawn_broker(false)?;
            connect_when_ready(&paths.socket).await?
        }
        Err(error) => return Err(error).context("failed to connect to the AnonSSH bond broker"),
    };
    request.write_to(&mut stream).await?;
    let verbose = verbose_output();
    let quiet = quiet_output();
    let mut progress_output = ConnectionProgressOutput::default();
    let mut route_reported = false;
    loop {
        let mut response = [0_u8; 4];
        timeout(SESSION_START_DEADLINE, stream.read_exact(&mut response))
            .await
            .context("bond broker did not establish the destination before its deadline")??;
        match response {
            RESPONSE_READY => {
                if !route_reported && !quiet {
                    print_ui_line("ready", "private route established", true);
                }
                return relay_stdio(stream).await;
            }
            RESPONSE_FAILED => bail!("bond broker could not establish the requested session"),
            RESPONSE_POLICY_MISMATCH => bail!(
                "bond broker uses a different resource profile; stop it before changing profiles"
            ),
            RESPONSE_PROGRESS => {
                let progress = read_progress_payload(&mut stream).await?;
                progress_output.print(&progress, verbose, quiet);
            }
            RESPONSE_AUTO_REPORT => {
                let report = read_auto_report(&mut stream).await?;
                print_auto_route_report(&report, verbose, quiet)?;
                route_reported = true;
            }
            _ => bail!("bond broker returned an unsupported response"),
        }
    }
}

#[derive(Default)]
struct ConnectionProgressOutput {
    last_summary: Option<String>,
}

impl ConnectionProgressOutput {
    fn print(&mut self, progress: &RouterProgressSnapshot, verbose: bool, quiet: bool) {
        if !quiet {
            if let Some(summary) = self.changed_summary(progress) {
                print_ui_line("routes", &summary, false);
            }
        }
        if verbose {
            print_router_progress(progress);
        }
    }

    fn changed_summary(&mut self, progress: &RouterProgressSnapshot) -> Option<String> {
        let summary = router_progress_summary(progress)?;
        if self.last_summary.as_deref() == Some(&summary) {
            return None;
        }
        self.last_summary = Some(summary.clone());
        Some(summary)
    }
}

fn print_auto_route_report(report: &AutoRouteReport, verbose: bool, quiet: bool) -> Result<()> {
    if !quiet {
        print_ui_line(
            "ready",
            &format!(
                "{} in {}",
                auto_route_human_label(report.winner),
                human_duration(report.elapsed_millis)
            ),
            true,
        );
    }
    if verbose {
        eprintln!("anonssh-route: {}", serde_json::to_string(report)?);
    }
    Ok(())
}

fn print_ui_line(label: &str, message: &str, success: bool) {
    if io::stderr().is_terminal() {
        let color = if success { "\x1b[1;32m" } else { "\x1b[1;36m" };
        eprintln!("anonssh  {color}{label:<7}\x1b[0m {message}");
    } else {
        eprintln!("anonssh  {label:<7} {message}");
    }
}

fn verbose_output() -> bool {
    std::env::var_os(VERBOSE_OUTPUT_ENV).is_some()
}

fn quiet_output() -> bool {
    std::env::var_os(QUIET_OUTPUT_ENV).is_some()
}

fn router_progress_summary(progress: &RouterProgressSnapshot) -> Option<String> {
    let tor = provider_progress_summary(progress, RouterProvider::Tor);
    let i2p = provider_progress_summary(progress, RouterProvider::I2p);
    match (tor, i2p) {
        (Some(tor), Some(i2p)) => Some(format!("Tor: {tor} | I2P: {i2p}")),
        (Some(tor), None) => Some(format!("Tor: {tor}")),
        (None, Some(i2p)) => Some(format!("I2P: {i2p}")),
        (None, None) => None,
    }
}

fn provider_progress_summary(
    progress: &RouterProgressSnapshot,
    provider: RouterProvider,
) -> Option<String> {
    let mut connected = 0;
    let mut ready = 0;
    let mut warming = 0;
    let mut retrying = 0;
    let mut failed = 0;
    for slot in progress
        .slots
        .iter()
        .filter(|slot| slot.provider == provider)
    {
        match slot.phase {
            RouterProgressPhase::Active => connected += 1,
            RouterProgressPhase::RouterReady => ready += 1,
            RouterProgressPhase::Starting | RouterProgressPhase::Repairing => warming += 1,
            RouterProgressPhase::Backoff => retrying += 1,
            RouterProgressPhase::Failed => failed += 1,
            RouterProgressPhase::Idle
            | RouterProgressPhase::Draining
            | RouterProgressPhase::Stopped => {}
        }
    }
    let mut parts = Vec::with_capacity(5);
    push_progress_count(&mut parts, connected, "connected");
    push_progress_count(&mut parts, ready, "router ready");
    push_progress_count(&mut parts, warming, "starting");
    push_progress_count(&mut parts, retrying, "retrying");
    push_progress_count(&mut parts, failed, "failed");
    (!parts.is_empty()).then(|| parts.join(", "))
}

fn push_progress_count(parts: &mut Vec<String>, count: usize, label: &str) {
    if count > 0 {
        parts.push(format!("{count} {label}"));
    }
}

const fn auto_route_human_label(route: AutoRoute) -> &'static str {
    match route {
        AutoRoute::BondMixed => "Tor + I2P bond",
        AutoRoute::BondTor => "Tor bond",
        AutoRoute::BondI2p => "I2P bond",
        AutoRoute::Tor => "direct Tor recovery",
        AutoRoute::I2p => "direct I2P recovery",
    }
}

fn human_duration(millis: u64) -> String {
    if millis < 1_000 {
        return format!("{millis} ms");
    }
    if millis < 60_000 {
        return format!("{:.1} s", millis as f64 / 1_000.0);
    }
    let seconds = millis / 1_000;
    format!("{}m {:02}s", seconds / 60, seconds % 60)
}

async fn read_auto_report<R: AsyncRead + Unpin>(reader: &mut R) -> Result<AutoRouteReport> {
    read_bounded_json(reader, "automatic route report").await
}

async fn write_auto_report<W: AsyncWrite + Unpin>(
    writer: &mut W,
    report: &AutoRouteReport,
) -> Result<()> {
    writer.write_all(&RESPONSE_AUTO_REPORT).await?;
    write_bounded_json(writer, report, "automatic route report").await
}

async fn read_progress_payload<R: AsyncRead + Unpin>(
    reader: &mut R,
) -> Result<RouterProgressSnapshot> {
    read_bounded_json(reader, "bond broker progress").await
}

async fn read_bounded_json<T: serde::de::DeserializeOwned, R: AsyncRead + Unpin>(
    reader: &mut R,
    label: &str,
) -> Result<T> {
    let length = usize::try_from(reader.read_u32().await?)
        .with_context(|| format!("{label} length overflowed"))?;
    if length == 0 || length > MAX_PROGRESS_BYTES {
        bail!("bond broker returned an invalid {label} length");
    }
    let mut encoded = vec![0_u8; length];
    reader.read_exact(&mut encoded).await?;
    serde_json::from_slice(&encoded)
        .with_context(|| format!("bond broker returned invalid {label} JSON"))
}

async fn write_progress_payload<W: AsyncWrite + Unpin>(
    writer: &mut W,
    progress: &RouterProgressSnapshot,
) -> Result<()> {
    writer.write_all(&RESPONSE_PROGRESS).await?;
    write_bounded_json(writer, progress, "bond broker progress").await
}

async fn write_bounded_json<T: Serialize, W: AsyncWrite + Unpin>(
    writer: &mut W,
    value: &T,
    label: &str,
) -> Result<()> {
    let encoded = serde_json::to_vec(value)?;
    if encoded.is_empty() || encoded.len() > MAX_PROGRESS_BYTES {
        bail!("{label} exceeds its wire bound");
    }
    writer
        .write_u32(u32::try_from(encoded.len()).with_context(|| format!("{label} is too large"))?)
        .await?;
    writer.write_all(&encoded).await?;
    writer.flush().await?;
    Ok(())
}

fn print_router_progress(progress: &RouterProgressSnapshot) {
    if let Some(line) = router_progress_line(progress) {
        eprintln!("{line}");
    }
}

pub(crate) fn router_progress_line(progress: &RouterProgressSnapshot) -> Option<String> {
    let event = progress
        .recent_events
        .iter()
        .rev()
        .find(|event| event.attempt > 0)?;
    let active_tor = progress
        .slots
        .iter()
        .filter(|slot| {
            slot.provider == RouterProvider::Tor && slot.phase == RouterProgressPhase::Active
        })
        .count();
    let active_i2p = progress
        .slots
        .iter()
        .filter(|slot| {
            slot.provider == RouterProvider::I2p && slot.phase == RouterProgressPhase::Active
        })
        .count();
    let deadline = event
        .operation_deadline_millis
        .map(|millis| format!(", deadline={}s", millis.saturating_add(999) / 1_000))
        .unwrap_or_default();
    let retry = event
        .retry_after_millis
        .map(|millis| format!(", retry={}s", millis.saturating_add(999) / 1_000))
        .unwrap_or_default();
    Some(format!(
        "anonssh: {} slot {} {} (attempt {}{}{}; active tor/i2p={active_tor}/{active_i2p})",
        provider_label(event.provider),
        event.slot,
        progress_phase_label(event.phase),
        event.attempt,
        deadline,
        retry,
    ))
}

fn latest_started_progress_sequence(progress: &RouterProgressSnapshot) -> u64 {
    progress
        .recent_events
        .iter()
        .rev()
        .find(|event| event.attempt > 0)
        .map_or(0, |event| event.sequence)
}

const fn provider_label(provider: RouterProvider) -> &'static str {
    match provider {
        RouterProvider::Tor => "tor",
        RouterProvider::I2p => "i2p",
    }
}

const fn progress_phase_label(phase: RouterProgressPhase) -> &'static str {
    match phase {
        RouterProgressPhase::Idle => "idle",
        RouterProgressPhase::Starting => "starting",
        RouterProgressPhase::Repairing => "repairing",
        RouterProgressPhase::RouterReady => "router-ready",
        RouterProgressPhase::Active => "active",
        RouterProgressPhase::Backoff => "backoff",
        RouterProgressPhase::Draining => "draining",
        RouterProgressPhase::Stopped => "stopped",
        RouterProgressPhase::Failed => "failed",
    }
}

pub async fn start(resident: bool) -> Result<bool> {
    let paths = BrokerPaths::for_user()?;
    let existing = status().await?;
    if existing.running && (!resident || existing.resident) {
        return Ok(false);
    }
    spawn_broker(resident)?;
    if resident {
        wait_for_broker_generation(&paths.socket, existing.process_id, true).await?;
    } else {
        drop(connect_when_ready(&paths.socket).await?);
    }
    Ok(true)
}

pub async fn serve(product_config: ProductConfig, resident: bool) -> Result<()> {
    let paths = BrokerPaths::for_user()?;
    if resident {
        stop_existing_before_claim(&paths.socket).await?;
    }
    let Some(socket) = BrokerSocket::claim(paths).await? else {
        return Ok(());
    };
    eprintln!("anonssh: bond broker acquired the per-user router pool");

    let config = AppConfig::new()?;
    let tor = resolve_executable("ANONSSH_TOR_BIN", "tor").ok();
    let i2pd = resolve_executable("ANONSSH_I2PD_BIN", "i2pd").ok();
    if tor.is_none() && i2pd.is_none() {
        bail!("bond broker requires at least one available Tor or i2pd executable");
    }
    let resident_policy = product_config.resident_service_policy();
    let storage_policy = crate::embedded_runtime::enforce_storage_policy(&config, resident_policy)?;
    let pool = Arc::new(RouterPool::production_client(
        &config,
        tor,
        i2pd,
        product_config.external_tor_services(),
    )?);
    let resource_profile = product_config.resource_profile();
    let resource_governor = Arc::new(SharedResourceGovernor::new(resource_profile.policy()));
    let warm_pool = Arc::new(Mutex::new(ResidentWarmPoolStatus {
        minimum_per_provider: resident_policy.minimum_warm_slots_per_provider,
        maximum_per_provider: resident_policy.maximum_warm_slots_per_provider,
        ..ResidentWarmPoolStatus::default()
    }));
    let i2p_connector = pool
        .i2p_slots()
        .first()
        .map(|slot| SamConnector::new(slot.sam_endpoint.to_string(), None));
    let runtime = Arc::new(BrokerRuntime {
        pool: pool.clone(),
        i2p_connector,
        metrics: BrokerMetrics::default(),
        resource_profile,
        resource_governor: resource_governor.clone(),
        resident_policy,
        app_config: config,
        storage_policy,
        warm_pool: warm_pool.clone(),
        resident,
    });
    let registry = Arc::new(SessionRegistry::new(BTreeMap::new()));
    let authorizations = Arc::new(AuthorizationRegistry::new(BTreeMap::new()));
    let warm_routers = resident.then(|| {
        tokio::spawn(maintain_warm_routers(
            pool.clone(),
            resource_governor,
            registry.clone(),
            resident_policy,
            resource_profile.policy(),
            warm_pool,
        ))
    });
    let operation = run(
        socket.private_listener(),
        socket.transport_listener(),
        runtime,
        registry.clone(),
        authorizations,
        resident,
    )
    .await;
    if let Some(warm_routers) = warm_routers {
        warm_routers.abort();
        let _ = warm_routers.await;
    }
    drop(socket);
    let sessions = shutdown_sessions(registry).await;
    let routers = pool.stop().await;
    merge_cleanup(merge_cleanup(operation, sessions), routers)
}

#[derive(Clone, Copy, Debug)]
struct WarmProviderPolicyState {
    target: usize,
    last_pressure: Duration,
}

#[derive(Clone, Copy, Debug)]
struct WarmPolicyState {
    tor: WarmProviderPolicyState,
    i2p: WarmProviderPolicyState,
}

impl WarmPolicyState {
    fn new(policy: ResidentServicePolicy, tor_available: usize, i2p_available: usize) -> Self {
        let target = policy.minimum_warm_slots_per_provider;
        Self {
            tor: WarmProviderPolicyState {
                target: target.min(tor_available),
                last_pressure: Duration::ZERO,
            },
            i2p: WarmProviderPolicyState {
                target: target.min(i2p_available),
                last_pressure: Duration::ZERO,
            },
        }
    }

    fn update(
        &mut self,
        now: Duration,
        policy: ResidentServicePolicy,
        demand: (usize, usize),
        available: (usize, usize),
        startup: (Option<Duration>, Option<Duration>),
        resource_pressure: bool,
    ) -> (usize, usize) {
        update_warm_provider(
            &mut self.tor,
            now,
            policy,
            demand.0,
            available.0,
            startup.0,
            resource_pressure,
        );
        update_warm_provider(
            &mut self.i2p,
            now,
            policy,
            demand.1,
            available.1,
            startup.1,
            resource_pressure,
        );
        (self.tor.target, self.i2p.target)
    }
}

fn update_warm_provider(
    state: &mut WarmProviderPolicyState,
    now: Duration,
    policy: ResidentServicePolicy,
    demand: usize,
    available: usize,
    startup: Option<Duration>,
    resource_pressure: bool,
) {
    let floor = policy.minimum_warm_slots_per_provider.min(available);
    let ceiling = policy.maximum_warm_slots_per_provider.min(available);
    let demand = demand.clamp(floor, ceiling);
    state.target = state.target.clamp(floor, ceiling);
    if demand >= state.target {
        state.target = demand;
        if demand > floor {
            state.last_pressure = now;
        }
        return;
    }
    if resource_pressure {
        state.target = state.target.saturating_sub(1).max(demand);
        state.last_pressure = now;
        return;
    }
    let retention = startup
        .unwrap_or(WARM_MINIMUM_RETENTION / 2)
        .saturating_mul(2)
        .clamp(WARM_MINIMUM_RETENTION, WARM_MAXIMUM_RETENTION);
    if now.saturating_sub(state.last_pressure) >= retention {
        state.target = state.target.saturating_sub(1).max(demand);
        state.last_pressure = now;
    }
}

async fn maintain_warm_routers(
    pool: Arc<RouterPool>,
    governor: Arc<SharedResourceGovernor>,
    registry: Arc<SessionRegistry>,
    policy: ResidentServicePolicy,
    scaling_policy: ScalingPolicy,
    status: Arc<Mutex<ResidentWarmPoolStatus>>,
) {
    let mut supervisors = JoinSet::new();
    let mut tor_demands = Vec::new();
    let mut i2p_demands = Vec::new();
    let mut policy_state =
        WarmPolicyState::new(policy, pool.tor_slots().len(), pool.i2p_slots().len());
    for router in pool.tor_slots() {
        let pool = pool.clone();
        let governor = governor.clone();
        let slot = router.slot;
        let desired = usize::try_from(slot).is_ok_and(|slot| slot <= policy_state.tor.target);
        let (demand, receiver) = watch::channel(desired);
        tor_demands.push((slot, demand));
        supervisors.spawn(supervise_warm_router(
            pool,
            governor,
            RouterProvider::Tor,
            slot,
            receiver,
        ));
    }
    for router in pool.i2p_slots() {
        let pool = pool.clone();
        let governor = governor.clone();
        let slot = router.slot;
        let desired = usize::try_from(slot).is_ok_and(|slot| slot <= policy_state.i2p.target);
        let (demand, receiver) = watch::channel(desired);
        i2p_demands.push((slot, demand));
        supervisors.spawn(supervise_warm_router(
            pool.clone(),
            governor,
            RouterProvider::I2p,
            slot,
            receiver,
        ));
    }
    supervisors.spawn(async move {
        let started = Instant::now();
        loop {
            let physical_demand = governor.demanded_provider_slots()?;
            let requested = requested_warm_baseline(&registry).await;
            let demand = (
                physical_demand.0.max(requested.0),
                physical_demand.1.max(requested.1),
            );
            let process_samples = pool.process_samples().await?;
            let mut startup = (None, None);
            let mut resident_bytes = 0_u64;
            for sample in process_samples {
                let target = match sample.provider {
                    RouterProvider::Tor => &mut startup.0,
                    RouterProvider::I2p => &mut startup.1,
                };
                if let Some(observed) = sample.startup_latency {
                    *target =
                        Some(target.map_or(observed, |current: Duration| current.max(observed)));
                }
                if let Some(usage) = sample.usage {
                    resident_bytes = resident_bytes.saturating_add(usage.resident_bytes);
                }
            }
            let targets = policy_state.update(
                started.elapsed(),
                policy,
                demand,
                (tor_demands.len(), i2p_demands.len()),
                startup,
                resident_bytes > scaling_policy.maximum_memory_bytes,
            );
            for (slot, sender) in &tor_demands {
                sender.send_replace(usize::try_from(*slot).is_ok_and(|slot| slot <= targets.0));
            }
            for (slot, sender) in &i2p_demands {
                sender.send_replace(usize::try_from(*slot).is_ok_and(|slot| slot <= targets.1));
            }
            *status.lock().await = ResidentWarmPoolStatus {
                tor_target: targets.0,
                i2p_target: targets.1,
                tor_demanded: demand.0,
                i2p_demanded: demand.1,
                minimum_per_provider: policy.minimum_warm_slots_per_provider,
                maximum_per_provider: policy.maximum_warm_slots_per_provider,
            };
            sleep(WARM_POLICY_INTERVAL).await;
        }
        #[allow(unreachable_code)]
        Ok::<(), anyhow::Error>(())
    });
    while supervisors.join_next().await.is_some() {}
}

async fn requested_warm_baseline(registry: &SessionRegistry) -> (usize, usize) {
    registry
        .lock()
        .await
        .values()
        .fold((0, 0), |(tor, i2p), entry| {
            let has_tor = !entry.request.tor_destinations.is_empty();
            let has_i2p = !entry.request.i2p_destinations.is_empty();
            (
                tor.max(if has_tor {
                    if has_i2p {
                        2
                    } else {
                        4
                    }
                } else {
                    0
                }),
                i2p.max(if has_i2p {
                    if has_tor {
                        2
                    } else {
                        4
                    }
                } else {
                    0
                }),
            )
        })
}

async fn supervise_warm_router(
    pool: Arc<RouterPool>,
    governor: Arc<SharedResourceGovernor>,
    provider: RouterProvider,
    slot: u32,
    mut desired: watch::Receiver<bool>,
) -> Result<()> {
    loop {
        if *desired.borrow() {
            let operation = async {
                match provider {
                    RouterProvider::Tor => pool.ensure_tor_slot(slot).await.map(drop),
                    RouterProvider::I2p => pool.ensure_i2p_slot(slot).await,
                }
            };
            let result = tokio::select! {
                result = operation => Some(result),
                changed = desired.changed() => {
                    changed.map_err(|_| anyhow::anyhow!("warm router demand closed"))?;
                    None
                }
            };
            if let Some(result) = result {
                let delay = match result {
                    Ok(()) => WARM_ROUTER_HEALTH_INTERVAL,
                    Err(error) => {
                        warn!(?provider, slot, "warm router unavailable: {error:#}");
                        WARM_ROUTER_RETRY_INTERVAL
                    }
                };
                tokio::select! {
                    _ = sleep(delay) => {}
                    changed = desired.changed() => {
                        changed.map_err(|_| anyhow::anyhow!("warm router demand closed"))?;
                    }
                }
            }
            continue;
        }
        if governor.physical_slot_demanded(provider, slot)? {
            tokio::select! {
                _ = sleep(WARM_POLICY_INTERVAL) => {}
                changed = desired.changed() => {
                    changed.map_err(|_| anyhow::anyhow!("warm router demand closed"))?;
                }
            }
            continue;
        }
        let stopped = match provider {
            RouterProvider::Tor => pool.stop_tor_slot(slot).await,
            RouterProvider::I2p => pool.stop_i2p_slot(slot).await,
        };
        if let Err(error) = stopped {
            warn!(?provider, slot, "warm router stop failed: {error:#}");
        }
        desired
            .changed()
            .await
            .map_err(|_| anyhow::anyhow!("warm router demand closed"))?;
    }
}

async fn run(
    private_listener: &UnixListener,
    transport_listener: &UnixListener,
    runtime: Arc<BrokerRuntime>,
    registry: Arc<SessionRegistry>,
    authorizations: Arc<AuthorizationRegistry>,
    resident: bool,
) -> Result<()> {
    let mut connections = JoinSet::new();
    let idle = sleep(BROKER_IDLE_TIMEOUT);
    tokio::pin!(idle);
    loop {
        tokio::select! {
            accepted = private_listener.accept() => {
                let (stream, _) = accepted.context("bond broker socket failed")?;
                idle.as_mut().reset(Instant::now() + BROKER_IDLE_TIMEOUT);
                if connections.len() >= runtime.resident_policy.maximum_local_connections {
                    reject_connection_at_listener_capacity(stream);
                    continue;
                }
                let runtime = runtime.clone();
                let registry = registry.clone();
                let authorizations = authorizations.clone();
                connections.spawn(async move {
                    handle_connection(stream, runtime, registry, authorizations).await
                });
            }
            accepted = transport_listener.accept() => {
                let (stream, _) = accepted.context("ALP transport socket failed")?;
                idle.as_mut().reset(Instant::now() + BROKER_IDLE_TIMEOUT);
                if connections.len() >= runtime.resident_policy.maximum_local_connections {
                    reject_connection_at_listener_capacity(stream);
                    continue;
                }
                let runtime = runtime.clone();
                let registry = registry.clone();
                let authorizations = authorizations.clone();
                connections.spawn(async move {
                    handle_transport_connection(stream, runtime, registry, authorizations)
                        .await
                        .map(|()| ConnectionOutcome::Complete)
                });
            }
            completed = connections.join_next(), if !connections.is_empty() => {
                match completed {
                    Some(Ok(Ok(ConnectionOutcome::Complete))) => {}
                    Some(Ok(Ok(ConnectionOutcome::Stop))) => break,
                    Some(Ok(Err(error))) => warn!("bond broker connection failed: {error:#}"),
                    Some(Err(error)) => warn!("bond broker connection task failed: {error}"),
                    None => {}
                }
                if connections.is_empty() {
                    idle.as_mut().reset(Instant::now() + BROKER_IDLE_TIMEOUT);
                }
            }
            _ = &mut idle, if !resident && connections.is_empty() => break,
            signal = shutdown_signal() => {
                signal.context("failed to wait for bond broker shutdown signal")?;
                break;
            }
        }
    }
    connections.abort_all();
    while connections.join_next().await.is_some() {}
    Ok(())
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum ConnectionOutcome {
    Complete,
    Stop,
}

fn reject_connection_at_listener_capacity(stream: UnixStream) {
    // Saturation must not allocate more tasks than the configured hard ceiling.
    // A typed response would require reading an attacker-controlled request, so
    // hard saturation is represented by deterministic EOF on both protocols.
    drop(stream);
}

async fn authorize_broker_target(
    authorizations: &AuthorizationRegistry,
    target: String,
    request: BondRequest,
) -> Result<()> {
    crate::local_transport::validate_target(&target)?;
    let mut targets = authorizations.lock().await;
    targets.retain(|_, target| target.last_used.elapsed() < AUTHORIZATION_IDLE_TIMEOUT);
    if !targets.contains_key(&target) && targets.len() >= MAX_AUTHORIZED_TARGETS {
        bail!("bond broker reached its authorized-target limit");
    }
    targets.insert(
        target,
        AuthorizedTarget {
            request,
            last_used: Instant::now(),
        },
    );
    Ok(())
}

async fn handle_transport_connection(
    mut local: UnixStream,
    runtime: Arc<BrokerRuntime>,
    registry: Arc<SessionRegistry>,
    authorizations: Arc<AuthorizationRegistry>,
) -> Result<()> {
    let credentials = local
        .peer_cred()
        .context("failed to authenticate ALP peer credentials")?;
    if !peer_uid_is_authorized(credentials.uid(), unsafe { libc::geteuid() }) {
        local.shutdown().await?;
        bail!("rejected ALP connection from another Unix user");
    }
    let request: AlpDialRequest = timeout(
        SOCKET_START_DEADLINE,
        crate::local_transport::read_record(&mut local),
    )
    .await
    .context("ALP request setup timed out")??;
    request.validate()?;
    let request_id = request.request_id.clone();
    let service = crate::application_service::ServiceName::parse(&request.service)?;
    let bond_request = {
        let mut targets = authorizations.lock().await;
        targets.retain(|_, target| target.last_used.elapsed() < AUTHORIZATION_IDLE_TIMEOUT);
        let Some(target) = targets.get_mut(&request.target) else {
            drop(targets);
            return write_alp_error(
                &mut local,
                request_id,
                AlpErrorCode::AuthorizationRequired,
                "target is not authorized in this broker generation",
            )
            .await;
        };
        target.last_used = Instant::now();
        target.request.for_transport(request.transport)?
    };
    let operation = establish_native_bond_stream(
        &runtime,
        &registry,
        bond_request,
        &service,
        request.class.into(),
    );
    let mut remote = match timeout(request.deadline(), operation).await {
        Ok(Ok(stream)) => stream,
        Ok(Err(error)) => {
            warn!("ALP route failed: {error:#}");
            let (code, message) = classify_alp_route_error(&error);
            return write_alp_error(&mut local, request_id, code, message).await;
        }
        Err(_) => {
            return write_alp_error(
                &mut local,
                request_id,
                AlpErrorCode::Timeout,
                "bond or peer service setup timed out",
            )
            .await;
        }
    };
    crate::local_transport::write_record(&mut local, &AlpResult::ready(request_id)?).await?;
    crate::data_stream::relay_bidirectional(&mut local, &mut remote).await?;
    remote.shutdown().await?;
    Ok(())
}

fn classify_alp_route_error(error: &anyhow::Error) -> (AlpErrorCode, &'static str) {
    use crate::application_service::{ServiceRejection, ServiceSetupError};

    match error.downcast_ref::<ServiceSetupError>() {
        Some(ServiceSetupError::Rejected { rejection, .. }) => match rejection {
            ServiceRejection::UnknownService => (
                AlpErrorCode::UnknownService,
                "peer does not offer the service",
            ),
            ServiceRejection::ClassDenied => (
                AlpErrorCode::ClassDenied,
                "peer rejected the requested traffic class",
            ),
            ServiceRejection::Capacity => (AlpErrorCode::Capacity, "peer service is at capacity"),
            ServiceRejection::Unavailable => (
                AlpErrorCode::ServiceUnavailable,
                "peer service is unavailable",
            ),
        },
        Some(ServiceSetupError::PeerIncompatible) => (
            AlpErrorCode::PeerIncompatible,
            "peer does not support native services",
        ),
        Some(ServiceSetupError::Timeout) => {
            (AlpErrorCode::Timeout, "peer service negotiation timed out")
        }
        None => (
            AlpErrorCode::RouteUnavailable,
            "bond or peer service is unavailable",
        ),
    }
}

fn peer_uid_is_authorized(peer: libc::uid_t, owner: libc::uid_t) -> bool {
    peer == owner
}

async fn write_alp_error(
    local: &mut UnixStream,
    request_id: String,
    code: AlpErrorCode,
    message: &str,
) -> Result<()> {
    crate::local_transport::write_record(local, &AlpResult::error(request_id, code, message)?)
        .await?;
    local.shutdown().await?;
    Ok(())
}

async fn handle_connection(
    mut local: UnixStream,
    runtime: Arc<BrokerRuntime>,
    registry: Arc<SessionRegistry>,
    authorizations: Arc<AuthorizationRegistry>,
) -> Result<ConnectionOutcome> {
    match BrokerRequest::read_from(&mut local).await? {
        BrokerRequest::Bond(request) => {
            handle_bond_connection(local, &runtime, registry, request).await?;
            Ok(ConnectionOutcome::Complete)
        }
        BrokerRequest::Auto(request) => {
            handle_auto_connection(local, runtime, registry, request).await?;
            Ok(ConnectionOutcome::Complete)
        }
        BrokerRequest::Tor(destination) => {
            handle_tor_connection(local, &runtime.pool, &destination).await?;
            Ok(ConnectionOutcome::Complete)
        }
        BrokerRequest::I2p(destination) => {
            handle_i2p_connection(local, &runtime, &destination).await?;
            Ok(ConnectionOutcome::Complete)
        }
        BrokerRequest::Status => {
            write_status(&mut local, &runtime, &registry, &authorizations).await?;
            Ok(ConnectionOutcome::Complete)
        }
        BrokerRequest::Authorize { target, request } => {
            if request.resource_profile != runtime.resource_profile {
                local.write_all(&RESPONSE_POLICY_MISMATCH).await?;
                bail!("bond broker rejected authorization with a mismatched resource profile");
            }
            authorize_broker_target(&authorizations, target, request).await?;
            local.write_all(&RESPONSE_READY).await?;
            local.shutdown().await?;
            Ok(ConnectionOutcome::Complete)
        }
        BrokerRequest::Stop => {
            local.write_all(&RESPONSE_READY).await?;
            local.shutdown().await?;
            Ok(ConnectionOutcome::Stop)
        }
    }
}

async fn handle_bond_connection(
    mut local: UnixStream,
    runtime: &BrokerRuntime,
    registry: Arc<SessionRegistry>,
    request: BondRequest,
) -> Result<()> {
    if request.resource_profile != runtime.resource_profile {
        local.write_all(&RESPONSE_POLICY_MISMATCH).await?;
        bail!("bond broker rejected a mismatched resource profile");
    }
    let operation = async {
        timeout(
            SESSION_START_DEADLINE,
            establish_bond_stream(runtime, &registry, request),
        )
        .await
        .context("bond session startup exceeded its deadline")?
    };
    let mut stream = match await_with_router_progress(&mut local, &runtime.pool, operation).await {
        Ok(stream) => stream,
        Err(error) => {
            let _ = local.write_all(&RESPONSE_FAILED).await;
            return Err(error);
        }
    };
    relay_ready(&mut local, &mut stream).await
}

async fn handle_tor_connection(
    mut local: UnixStream,
    pool: &RouterPool,
    destination: &str,
) -> Result<()> {
    let operation = establish_tor_stream(pool, destination);
    let mut remote = match await_with_router_progress(&mut local, pool, operation).await {
        Ok(remote) => remote,
        Err(error) => {
            let _ = local.write_all(&RESPONSE_FAILED).await;
            return Err(error);
        }
    };
    relay_ready(&mut local, &mut remote).await
}

async fn handle_i2p_connection(
    mut local: UnixStream,
    runtime: &BrokerRuntime,
    destination: &str,
) -> Result<()> {
    let operation = establish_i2p_stream(runtime, destination);
    let mut remote = match await_with_router_progress(&mut local, &runtime.pool, operation).await {
        Ok(remote) => remote,
        Err(error) => {
            let _ = local.write_all(&RESPONSE_FAILED).await;
            return Err(error);
        }
    };
    relay_ready(&mut local, &mut remote).await
}

async fn establish_bond_stream(
    runtime: &BrokerRuntime,
    registry: &SessionRegistry,
    request: BondRequest,
) -> Result<anonssh_bond_tokio::BondedStream> {
    if request.resource_profile != runtime.resource_profile {
        bail!("bond broker rejected a mismatched resource profile");
    }
    let allow_new_session =
        crate::embedded_runtime::state_within_quota(&runtime.app_config, runtime.resident_policy)?;
    let entry = session_entry(
        registry,
        request,
        runtime.resident_policy.maximum_sessions,
        allow_new_session,
    )
    .await?;
    let client = entry
        .client(
            &runtime.pool,
            runtime.resource_profile.policy(),
            runtime.resource_governor.clone(),
        )
        .await?;
    let stream = client
        .open_ssh_stream()
        .await
        .context("failed to open brokered SSH stream")?;
    runtime
        .metrics
        .record_stream(client.session().session_id(), stream.stream_id().get())
        .await;
    Ok(stream)
}

async fn establish_native_bond_stream(
    runtime: &BrokerRuntime,
    registry: &SessionRegistry,
    request: BondRequest,
    service: &crate::application_service::ServiceName,
    class: anonssh_bond::TrafficClass,
) -> Result<anonssh_bond_tokio::BondedStream> {
    if request.resource_profile != runtime.resource_profile {
        bail!("bond broker rejected a mismatched resource profile");
    }
    let allow_new_session =
        crate::embedded_runtime::state_within_quota(&runtime.app_config, runtime.resident_policy)?;
    let entry = session_entry(
        registry,
        request,
        runtime.resident_policy.maximum_sessions,
        allow_new_session,
    )
    .await?;
    let client = entry
        .client(
            &runtime.pool,
            runtime.resource_profile.policy(),
            runtime.resource_governor.clone(),
        )
        .await?;
    let stream = client
        .open_service_stream(service, class)
        .await
        .context("failed to open brokered native service stream")?;
    runtime
        .metrics
        .record_stream(client.session().session_id(), stream.stream_id().get())
        .await;
    Ok(stream)
}

async fn establish_tor_stream(pool: &RouterPool, destination: &str) -> Result<TcpStream> {
    let endpoint = pool
        .ensure_tor_slot(1)
        .await
        .context("failed to start the broker's Tor router")?;
    let remote = TorConnector::new(endpoint)
        .connect(destination, 0)
        .await
        .context("brokered Tor connection failed")?;
    pool.tor_slot(1)?.mark_direct_ready();
    Ok(remote)
}

async fn establish_i2p_stream(runtime: &BrokerRuntime, destination: &str) -> Result<TcpStream> {
    runtime
        .pool
        .ensure_i2p_slot(1)
        .await
        .context("failed to start the broker's I2P router")?;
    let connector = runtime
        .i2p_connector
        .as_ref()
        .context("bond broker has no I2P router")?;
    let remote = connector
        .connect_with_initial_payload(destination, 0, &[])
        .await
        .context("brokered I2P connection failed")?;
    runtime.pool.i2p_slot(1)?.mark_direct_ready();
    Ok(remote)
}

enum AutoEstablishedStream {
    Bond(anonssh_bond_tokio::BondedStream),
    Direct(TcpStream),
}

async fn handle_auto_connection(
    mut local: UnixStream,
    runtime: Arc<BrokerRuntime>,
    registry: Arc<SessionRegistry>,
    request: AutoRequest,
) -> Result<()> {
    if request.resource_profile != runtime.resource_profile {
        local.write_all(&RESPONSE_POLICY_MISMATCH).await?;
        bail!("bond broker rejected a mismatched resource profile");
    }
    let specs = automatic_candidate_specs(&runtime.pool);
    if specs.is_empty() {
        local.write_all(&RESPONSE_FAILED).await?;
        bail!("automatic routing has no available providers");
    }
    let request = Arc::new(request);
    let candidate_runtime = runtime.clone();
    let candidate_registry = registry.clone();
    let candidate_request = request.clone();
    let race = race_auto_candidates(&specs, move |route| {
        let runtime = candidate_runtime.clone();
        let registry = candidate_registry.clone();
        let request = candidate_request.clone();
        async move { establish_auto_route(route, runtime, registry, request).await }
    });
    let result = await_with_router_progress(&mut local, &runtime.pool, race).await;
    prune_empty_sessions(&registry).await;
    let winner = match result {
        Ok(winner) => winner,
        Err(error) => {
            let _ = local.write_all(&RESPONSE_FAILED).await;
            return Err(error);
        }
    };
    write_auto_report(&mut local, &winner.report).await?;
    match winner.value {
        AutoEstablishedStream::Bond(mut stream) => relay_ready(&mut local, &mut stream).await,
        AutoEstablishedStream::Direct(mut stream) => relay_ready(&mut local, &mut stream).await,
    }
}

fn automatic_candidate_specs(pool: &RouterPool) -> Vec<AutoCandidateSpec> {
    let has_tor = !pool.tor_slots().is_empty();
    let has_i2p = !pool.i2p_slots().is_empty();
    let mut candidates = Vec::new();
    if has_tor && has_i2p {
        candidates.push(AutoCandidateSpec {
            route: AutoRoute::BondMixed,
            start_delay: Duration::ZERO,
            deadline: AUTO_BOND_TOR_DEADLINE,
        });
    }
    if has_tor {
        candidates.push(AutoCandidateSpec {
            route: AutoRoute::BondTor,
            start_delay: AUTO_TOR_ONLY_DELAY,
            deadline: AUTO_BOND_TOR_DEADLINE,
        });
    }
    if has_i2p {
        candidates.push(AutoCandidateSpec {
            route: AutoRoute::BondI2p,
            start_delay: AUTO_I2P_ONLY_DELAY,
            deadline: AUTO_BOND_I2P_DEADLINE,
        });
    }
    if has_tor {
        candidates.push(AutoCandidateSpec {
            route: AutoRoute::Tor,
            start_delay: AUTO_DIRECT_TOR_DELAY,
            deadline: AUTO_DIRECT_TOR_DEADLINE,
        });
    }
    if has_i2p {
        candidates.push(AutoCandidateSpec {
            route: AutoRoute::I2p,
            start_delay: AUTO_DIRECT_I2P_DELAY,
            deadline: AUTO_DIRECT_I2P_DEADLINE,
        });
    }
    candidates
}

async fn establish_auto_route(
    route: AutoRoute,
    runtime: Arc<BrokerRuntime>,
    registry: Arc<SessionRegistry>,
    request: Arc<AutoRequest>,
) -> Result<AutoEstablishedStream> {
    match route {
        AutoRoute::BondMixed | AutoRoute::BondTor | AutoRoute::BondI2p => {
            if std::env::var_os("ANONSSH_INTERNAL_TEST_FAIL_BOND").is_some() {
                bail!("bond candidate failure was requested by the internal test harness");
            }
            if let Some(delay) = internal_bond_stall() {
                sleep(delay).await;
            }
            Ok(AutoEstablishedStream::Bond(
                establish_bond_stream(&runtime, &registry, request.bond_request(route)?).await?,
            ))
        }
        AutoRoute::Tor => {
            reject_direct_route_for_internal_test()?;
            Ok(AutoEstablishedStream::Direct(
                establish_tor_stream(&runtime.pool, &request.direct_tor_destination).await?,
            ))
        }
        AutoRoute::I2p => {
            reject_direct_route_for_internal_test()?;
            Ok(AutoEstablishedStream::Direct(
                establish_i2p_stream(&runtime, &request.direct_i2p_destination).await?,
            ))
        }
    }
}

fn reject_direct_route_for_internal_test() -> Result<()> {
    if std::env::var_os("ANONSSH_INTERNAL_TEST_FAIL_DIRECT").is_some() {
        bail!("direct candidate failure was requested by the internal test harness");
    }
    Ok(())
}

fn internal_bond_stall() -> Option<Duration> {
    std::env::var("ANONSSH_INTERNAL_TEST_STALL_BOND_MILLIS")
        .ok()
        .and_then(|value| value.parse::<u64>().ok())
        .map(|millis| Duration::from_millis(millis.clamp(1, 15 * 60 * 1_000)))
}

async fn race_auto_candidates<T, F, Fut>(
    specs: &[AutoCandidateSpec],
    start: F,
) -> Result<AutoRaceWinner<T>>
where
    T: Send + 'static,
    F: Fn(AutoRoute) -> Fut,
    Fut: Future<Output = Result<T>> + Send + 'static,
{
    if specs.is_empty() {
        bail!("automatic route race has no candidates");
    }
    let race_started = Instant::now();
    let mut attempts = BTreeMap::new();
    let mut tasks = JoinSet::new();
    for spec in specs.iter().copied() {
        if attempts
            .insert(
                spec.route,
                AutoRouteAttempt {
                    route: spec.route,
                    start_delay_millis: duration_millis(spec.start_delay),
                    completed_millis: None,
                    outcome: AutoAttemptOutcome::Canceled,
                },
            )
            .is_some()
        {
            bail!("automatic route race declared a duplicate candidate");
        }
        let operation = start(spec.route);
        tasks.spawn(async move {
            sleep(spec.start_delay).await;
            let outcome = match timeout(spec.deadline, operation).await {
                Ok(Ok(value)) => AutoCandidateOutcome::Succeeded(value),
                Ok(Err(error)) => AutoCandidateOutcome::Failed(format!("{error:#}")),
                Err(_) => AutoCandidateOutcome::TimedOut,
            };
            AutoCandidateCompletion {
                spec,
                completed_millis: duration_millis(race_started.elapsed()),
                outcome,
            }
        });
    }

    let mut failures = Vec::new();
    let mut winners = Vec::new();
    while let Some(joined) = tasks.join_next().await {
        let completion = match joined {
            Ok(completion) => completion,
            Err(error) => {
                abort_auto_candidates(&mut tasks).await;
                return Err(anyhow::anyhow!("automatic route task failed: {error}"));
            }
        };
        record_auto_completion(completion, &mut attempts, &mut failures, &mut winners)?;
        if winners.is_empty() {
            continue;
        }

        let settle = sleep(AUTO_WINNER_SETTLE);
        tokio::pin!(settle);
        loop {
            tokio::select! {
                _ = &mut settle => break,
                joined = tasks.join_next(), if !tasks.is_empty() => {
                    let Some(joined) = joined else { break; };
                    let completion = match joined {
                        Ok(completion) => completion,
                        Err(error) => {
                            abort_auto_candidates(&mut tasks).await;
                            return Err(anyhow::anyhow!("automatic route task failed: {error}"));
                        }
                    };
                    record_auto_completion(
                        completion,
                        &mut attempts,
                        &mut failures,
                        &mut winners,
                    )?;
                }
            }
        }
        abort_auto_candidates(&mut tasks).await;
        let winner_index = winners
            .iter()
            .enumerate()
            .min_by_key(|(_, (route, _))| *route)
            .map(|(index, _)| index)
            .context("automatic route race lost its successful candidate")?;
        let (winner, value) = winners.swap_remove(winner_index);
        return Ok(AutoRaceWinner {
            value,
            report: AutoRouteReport {
                schema: "anonssh.auto-route.v1".to_owned(),
                winner,
                elapsed_millis: duration_millis(race_started.elapsed()),
                attempts: attempts.into_values().collect(),
            },
        });
    }

    bail!(
        "all automatic route candidates failed: {}",
        failures.join("; ")
    )
}

fn record_auto_completion<T>(
    completion: AutoCandidateCompletion<T>,
    attempts: &mut BTreeMap<AutoRoute, AutoRouteAttempt>,
    failures: &mut Vec<String>,
    winners: &mut Vec<(AutoRoute, T)>,
) -> Result<()> {
    let attempt = attempts
        .get_mut(&completion.spec.route)
        .context("automatic route completion was not declared")?;
    attempt.completed_millis = Some(completion.completed_millis);
    match completion.outcome {
        AutoCandidateOutcome::Succeeded(value) => {
            attempt.outcome = AutoAttemptOutcome::Succeeded;
            winners.push((completion.spec.route, value));
        }
        AutoCandidateOutcome::Failed(error) => {
            attempt.outcome = AutoAttemptOutcome::Failed;
            failures.push(format!(
                "{}: {error}",
                auto_route_label(completion.spec.route)
            ));
        }
        AutoCandidateOutcome::TimedOut => {
            attempt.outcome = AutoAttemptOutcome::TimedOut;
            failures.push(format!(
                "{}: exceeded {} seconds",
                auto_route_label(completion.spec.route),
                completion.spec.deadline.as_secs()
            ));
        }
    }
    Ok(())
}

async fn abort_auto_candidates<T: 'static>(tasks: &mut JoinSet<AutoCandidateCompletion<T>>) {
    tasks.abort_all();
    while tasks.join_next().await.is_some() {}
}

const fn auto_route_label(route: AutoRoute) -> &'static str {
    match route {
        AutoRoute::BondMixed => "bond-mixed",
        AutoRoute::BondTor => "bond-tor",
        AutoRoute::BondI2p => "bond-i2p",
        AutoRoute::Tor => "tor",
        AutoRoute::I2p => "i2p",
    }
}

fn duration_millis(duration: Duration) -> u64 {
    u64::try_from(duration.as_millis()).unwrap_or(u64::MAX)
}

async fn await_with_router_progress<T>(
    local: &mut UnixStream,
    pool: &RouterPool,
    operation: impl std::future::Future<Output = Result<T>>,
) -> Result<T> {
    tokio::pin!(operation);
    let mut interval = tokio::time::interval(PROGRESS_INTERVAL);
    interval.set_missed_tick_behavior(tokio::time::MissedTickBehavior::Skip);
    let mut last_progress_sequence = 0;
    loop {
        tokio::select! {
            result = &mut operation => return result,
            _ = interval.tick() => {
                let progress = pool.progress_snapshot();
                let sequence = latest_started_progress_sequence(&progress);
                if sequence > last_progress_sequence {
                    write_progress_payload(local, &progress).await?;
                    last_progress_sequence = sequence;
                }
            }
        }
    }
}

async fn relay_ready<S>(local: &mut UnixStream, remote: &mut S) -> Result<()>
where
    S: AsyncRead + AsyncWrite + Unpin,
{
    local.write_all(&RESPONSE_READY).await?;
    local.flush().await?;
    crate::data_stream::relay_bidirectional(local, remote).await?;
    remote.shutdown().await?;
    Ok(())
}

struct BrokerRuntime {
    pool: Arc<RouterPool>,
    i2p_connector: Option<SamConnector>,
    metrics: BrokerMetrics,
    resource_profile: ResourceProfile,
    resource_governor: Arc<SharedResourceGovernor>,
    resident_policy: ResidentServicePolicy,
    app_config: AppConfig,
    storage_policy: StoragePolicyReport,
    warm_pool: Arc<Mutex<ResidentWarmPoolStatus>>,
    resident: bool,
}

#[derive(Default)]
struct BrokerMetrics {
    recent_streams: Mutex<VecDeque<BrokerBondStreamStatus>>,
}

impl BrokerMetrics {
    async fn record_stream(&self, session_id: u64, stream_id: u64) {
        let mut streams = self.recent_streams.lock().await;
        if streams.len() == MAX_RECENT_STREAMS {
            streams.pop_front();
        }
        streams.push_back(BrokerBondStreamStatus {
            session_id,
            stream_id,
        });
    }
}

async fn write_status(
    local: &mut UnixStream,
    runtime: &BrokerRuntime,
    registry: &SessionRegistry,
    authorizations: &AuthorizationRegistry,
) -> Result<()> {
    let sessions = registry.lock().await;
    let entries = sessions.values().cloned().collect::<Vec<_>>();
    let bond_session_ids = entries
        .iter()
        .filter_map(|entry| entry.session_id())
        .collect::<Vec<_>>();
    let recent_bond_streams = runtime
        .metrics
        .recent_streams
        .lock()
        .await
        .iter()
        .copied()
        .collect::<Vec<_>>();
    let recent_bond_stream_ids = recent_bond_streams
        .iter()
        .map(|stream| stream.stream_id)
        .collect();
    drop(sessions);
    let mut bond_session_topologies = Vec::new();
    for entry in entries {
        if let Some(status) = entry.status().await {
            bond_session_topologies.push(status);
        }
    }
    let processes = runtime.pool.process_samples().await?;
    let status = BrokerStatus {
        schema: "anonssh.broker-status.v8".to_owned(),
        running: true,
        resident: runtime.resident,
        process_id: Some(std::process::id()),
        router_pool_instances: 1,
        authorized_targets: authorizations.lock().await.len(),
        bond_sessions: bond_session_ids.len(),
        bond_session_ids,
        bond_session_topologies,
        recent_bond_streams,
        recent_bond_stream_ids,
        tor_routers_running: processes
            .iter()
            .filter(|sample| {
                sample.provider == crate::router_pool::RouterProvider::Tor && sample.usage.is_some()
            })
            .count(),
        i2p_routers_running: processes
            .iter()
            .filter(|sample| {
                sample.provider == crate::router_pool::RouterProvider::I2p && sample.usage.is_some()
            })
            .count(),
        resource_profile: Some(runtime.resource_profile),
        scaling_policy: Some(runtime.resource_profile.policy()),
        resource_governor: Some(runtime.resource_governor.snapshot()?),
        resident_policy: Some(runtime.resident_policy),
        warm_pool: Some(*runtime.warm_pool.lock().await),
        storage_policy: Some(runtime.storage_policy.clone()),
        router_progress: runtime.pool.progress_snapshot(),
    };
    let encoded = serde_json::to_vec(&status)?;
    local.write_all(&RESPONSE_STATUS).await?;
    local
        .write_u32(u32::try_from(encoded.len()).context("broker status is too large")?)
        .await?;
    local.write_all(&encoded).await?;
    local.shutdown().await?;
    Ok(())
}

async fn session_entry(
    registry: &SessionRegistry,
    request: BondRequest,
    maximum_sessions: usize,
    allow_new_session: bool,
) -> Result<Arc<SessionEntry>> {
    let cache_key = request.topology_key();
    loop {
        let existing = {
            let mut sessions = registry.lock().await;
            sessions
                .retain(|_, entry| entry.client.get().is_some() || Arc::strong_count(entry) > 1);
            if let Some(entry) = sessions.get(&cache_key) {
                if !entry.request.same_topology(&request) {
                    bail!("bond broker session topology digest collided");
                }
                if !entry.request.key_matches(&request) {
                    bail!("bond broker rejected a mismatched session key");
                }
                Some(entry.clone())
            } else {
                if sessions.len() >= maximum_sessions {
                    bail!("bond broker reached its destination session limit");
                }
                if !allow_new_session {
                    bail!(
                        "persistent router state exceeds its configured quota; refusing a new session"
                    );
                }
                let entry = Arc::new(SessionEntry::new(request));
                sessions.insert(cache_key, entry.clone());
                return Ok(entry);
            }
        };
        let entry = existing.expect("existing session was checked");
        if !entry.supervision_finished().await {
            return Ok(entry);
        }
        let retired = {
            let mut sessions = registry.lock().await;
            if sessions
                .get(&cache_key)
                .is_some_and(|candidate| Arc::ptr_eq(candidate, &entry))
            {
                sessions.remove(&cache_key)
            } else {
                None
            }
        };
        drop(entry);
        if let Some(retired) = retired {
            retired.stop_supervision().await;
        }
    }
}

async fn prune_empty_sessions(registry: &SessionRegistry) {
    registry
        .lock()
        .await
        .retain(|_, entry| entry.client.get().is_some() || Arc::strong_count(entry) > 1);
}

struct SessionEntry {
    request: BondRequest,
    client: OnceCell<Arc<ClientBondSession>>,
    supervisor: Mutex<Option<JoinHandle<Result<()>>>>,
}

impl SessionEntry {
    fn new(request: BondRequest) -> Self {
        Self {
            request,
            client: OnceCell::new(),
            supervisor: Mutex::new(None),
        }
    }

    fn session_id(&self) -> Option<u64> {
        self.client
            .get()
            .map(|client| client.session().session_id())
    }

    async fn supervision_finished(&self) -> bool {
        self.supervisor
            .lock()
            .await
            .as_ref()
            .is_some_and(JoinHandle::is_finished)
    }

    async fn stop_supervision(&self) {
        if let Some(client) = self.client.get() {
            let _ = client
                .session()
                .control()
                .terminate("retired failed broker bond session".to_owned())
                .await;
        }
        if let Some(supervisor) = self.supervisor.lock().await.take() {
            supervisor.abort();
            let _ = supervisor.await;
        }
    }

    async fn status(&self) -> Option<BrokerBondSessionStatus> {
        let client = self.client.get()?.clone();
        let statistics = timeout(Duration::from_secs(1), client.session().statistics())
            .await
            .ok()
            .and_then(Result::ok);
        let active_lane_ids = statistics
            .as_ref()
            .map(|statistics| {
                statistics
                    .lanes
                    .iter()
                    .filter(|lane| lane.active)
                    .map(|lane| u64::from(lane.id.get()))
                    .collect()
            })
            .unwrap_or_default();
        Some(BrokerBondSessionStatus {
            session_id: client.session().session_id(),
            topology: self.topology_label().to_owned(),
            candidate_lanes: self.request.tor_destinations.len()
                + self.request.i2p_destinations.len(),
            active_lane_ids,
            statistics_available: statistics.is_some(),
        })
    }

    const fn topology_label(&self) -> &'static str {
        match (
            self.request.tor_destinations.is_empty(),
            self.request.i2p_destinations.is_empty(),
        ) {
            (false, false) => "bond-mixed",
            (false, true) => "bond-tor",
            (true, false) => "bond-i2p",
            (true, true) => "invalid",
        }
    }

    async fn client(
        &self,
        pool: &Arc<RouterPool>,
        scaling_policy: ScalingPolicy,
        resource_governor: Arc<SharedResourceGovernor>,
    ) -> Result<Arc<ClientBondSession>> {
        let client = self
            .client
            .get_or_try_init(|| async {
                let session_pool = Arc::new(pool.prefix(
                    usize::from(!self.request.tor_destinations.is_empty()) * PRODUCTION_TOR_SLOTS,
                    usize::from(!self.request.i2p_destinations.is_empty()) * PRODUCTION_I2P_SLOTS,
                )?);
                let client = Arc::new(
                    ClientBondSession::connect_with_resource_governor(
                        &session_pool,
                        &[],
                        &self.request.tor_destinations,
                        &self.request.i2p_destinations,
                        *self.request.key,
                        scaling_policy,
                        resource_governor,
                    )
                    .await?,
                );
                let supervised_client = client.clone();
                *self.supervisor.lock().await = Some(tokio::spawn(async move {
                    supervised_client.maintain_lanes(&session_pool).await
                }));
                Ok::<_, anyhow::Error>(client)
            })
            .await?;
        if self
            .supervisor
            .lock()
            .await
            .as_ref()
            .is_some_and(JoinHandle::is_finished)
        {
            bail!("bond session lane supervision has stopped");
        }
        Ok(client.clone())
    }

    async fn shutdown(self) -> Result<()> {
        if let Some(supervisor) = self.supervisor.into_inner() {
            supervisor.abort();
            let _ = supervisor.await;
        }
        let Some(client) = self.client.into_inner() else {
            return Ok(());
        };
        Arc::try_unwrap(client)
            .map_err(|_| anyhow::anyhow!("bond broker session remained borrowed during shutdown"))?
            .shutdown()
            .await
    }
}

async fn shutdown_sessions(registry: Arc<SessionRegistry>) -> Result<()> {
    let registry = Arc::try_unwrap(registry)
        .map_err(|_| anyhow::anyhow!("bond broker registry remained borrowed during shutdown"))?
        .into_inner();
    let mut failures = Vec::new();
    for (key, entry) in registry {
        let result = match Arc::try_unwrap(entry) {
            Ok(entry) => entry.shutdown().await,
            Err(_) => Err(anyhow::anyhow!(
                "bond broker destination remained borrowed during shutdown"
            )),
        };
        if let Err(error) = result {
            failures.push(format!(
                "{:02x}{:02x}{:02x}{:02x}: {error:#}",
                key[0], key[1], key[2], key[3]
            ));
        }
    }
    if failures.is_empty() {
        Ok(())
    } else {
        bail!(
            "bond broker session cleanup failed: {}",
            failures.join("; ")
        )
    }
}

struct BondRequest {
    tor_destinations: Vec<String>,
    i2p_destinations: Vec<String>,
    key: Zeroizing<[u8; 32]>,
    resource_profile: ResourceProfile,
}

struct AutoRequest {
    tor_destinations: Vec<String>,
    i2p_destinations: Vec<String>,
    direct_tor_destination: String,
    direct_i2p_destination: String,
    key: Zeroizing<[u8; 32]>,
    resource_profile: ResourceProfile,
}

enum BrokerRequest {
    Bond(BondRequest),
    Auto(AutoRequest),
    Tor(String),
    I2p(String),
    Authorize {
        target: String,
        request: BondRequest,
    },
    Status,
    Stop,
}

impl BrokerRequest {
    async fn write_to<W: AsyncWrite + Unpin>(&self, writer: &mut W) -> Result<()> {
        writer.write_all(&REQUEST_MAGIC).await?;
        match self {
            Self::Bond(request) => {
                writer.write_u8(REQUEST_BOND).await?;
                request.write_payload(writer).await?;
            }
            Self::Auto(request) => {
                writer.write_u8(REQUEST_AUTO).await?;
                request.write_payload(writer).await?;
            }
            Self::Tor(destination) => {
                writer.write_u8(REQUEST_TOR).await?;
                write_destination(writer, destination).await?;
            }
            Self::I2p(destination) => {
                writer.write_u8(REQUEST_I2P).await?;
                write_destination(writer, destination).await?;
            }
            Self::Authorize { target, request } => {
                writer.write_u8(REQUEST_AUTHORIZE).await?;
                write_destination(writer, target).await?;
                request.write_payload(writer).await?;
            }
            Self::Status => writer.write_u8(REQUEST_STATUS).await?,
            Self::Stop => writer.write_u8(REQUEST_STOP).await?,
        }
        writer.flush().await?;
        Ok(())
    }

    async fn read_from<R: AsyncRead + Unpin>(reader: &mut R) -> Result<Self> {
        let mut magic = [0_u8; 4];
        reader.read_exact(&mut magic).await?;
        if magic != REQUEST_MAGIC {
            bail!("unsupported bond broker request version");
        }
        match reader.read_u8().await? {
            REQUEST_BOND => Ok(Self::Bond(BondRequest::read_payload(reader).await?)),
            REQUEST_AUTO => Ok(Self::Auto(AutoRequest::read_payload(reader).await?)),
            REQUEST_TOR => Ok(Self::Tor(read_destination(reader).await?)),
            REQUEST_I2P => Ok(Self::I2p(read_destination(reader).await?)),
            REQUEST_AUTHORIZE => {
                let target = read_destination(reader).await?;
                crate::local_transport::validate_target(&target)?;
                Ok(Self::Authorize {
                    target,
                    request: BondRequest::read_payload(reader).await?,
                })
            }
            REQUEST_STATUS => Ok(Self::Status),
            REQUEST_STOP => Ok(Self::Stop),
            _ => bail!("unsupported bond broker request mode"),
        }
    }
}

impl BondRequest {
    fn from_key_file(
        tor_destinations: &[String],
        i2p_destinations: &[String],
        key_file: &Path,
        resource_profile: ResourceProfile,
    ) -> Result<Self> {
        let key = read_bond_key(key_file)?;
        Self::new(
            tor_destinations.to_vec(),
            i2p_destinations.to_vec(),
            key,
            resource_profile,
        )
    }

    fn new(
        tor_destinations: Vec<String>,
        i2p_destinations: Vec<String>,
        key: Zeroizing<[u8; 32]>,
        resource_profile: ResourceProfile,
    ) -> Result<Self> {
        validate_destinations("Tor", &tor_destinations, PRODUCTION_TOR_SLOTS)?;
        validate_destinations("I2P", &i2p_destinations, PRODUCTION_I2P_SLOTS)?;
        if tor_destinations.is_empty() && i2p_destinations.is_empty() {
            bail!("bond broker request has no transport providers");
        }
        Ok(Self {
            tor_destinations,
            i2p_destinations,
            key,
            resource_profile,
        })
    }

    async fn write_payload<W: AsyncWrite + Unpin>(&self, writer: &mut W) -> Result<()> {
        writer.write_u8(self.resource_profile.wire_code()).await?;
        write_destinations(writer, &self.tor_destinations).await?;
        write_destinations(writer, &self.i2p_destinations).await?;
        writer.write_all(self.key.as_ref()).await?;
        Ok(())
    }

    async fn read_payload<R: AsyncRead + Unpin>(reader: &mut R) -> Result<Self> {
        let resource_profile = ResourceProfile::from_wire_code(reader.read_u8().await?)?;
        let tor_destinations = read_destinations(reader, PRODUCTION_TOR_SLOTS).await?;
        let i2p_destinations = read_destinations(reader, PRODUCTION_I2P_SLOTS).await?;
        let mut key = Zeroizing::new([0_u8; 32]);
        reader.read_exact(key.as_mut()).await?;
        Self::new(tor_destinations, i2p_destinations, key, resource_profile)
    }

    fn topology_key(&self) -> [u8; 32] {
        let mut digest = Sha256::new();
        digest.update(b"anonssh-broker-topology-v1\0");
        digest.update([self.resource_profile.wire_code()]);
        hash_destinations(&mut digest, b't', &self.tor_destinations);
        hash_destinations(&mut digest, b'i', &self.i2p_destinations);
        digest.finalize().into()
    }

    fn same_topology(&self, other: &Self) -> bool {
        self.tor_destinations == other.tor_destinations
            && self.i2p_destinations == other.i2p_destinations
            && self.resource_profile == other.resource_profile
    }

    fn key_matches(&self, other: &Self) -> bool {
        bool::from(self.key.as_ref().ct_eq(other.key.as_ref()))
    }

    fn for_transport(&self, transport: AlpTransport) -> Result<Self> {
        let (tor, i2p) = match transport {
            AlpTransport::Auto | AlpTransport::Mixed => {
                if self.tor_destinations.is_empty() || self.i2p_destinations.is_empty() {
                    bail!("requested mixed bond is not authorized for both providers");
                }
                (self.tor_destinations.clone(), self.i2p_destinations.clone())
            }
            AlpTransport::TorOnly => {
                if self.tor_destinations.is_empty() {
                    bail!("requested Tor-only bond is not authorized");
                }
                (self.tor_destinations.clone(), Vec::new())
            }
            AlpTransport::I2pOnly => {
                if self.i2p_destinations.is_empty() {
                    bail!("requested I2P-only bond is not authorized");
                }
                (Vec::new(), self.i2p_destinations.clone())
            }
        };
        Self::new(tor, i2p, Zeroizing::new(*self.key), self.resource_profile)
    }
}

impl AutoRequest {
    fn from_key_file(
        tor_destinations: &[String],
        i2p_destinations: &[String],
        direct_tor_destination: &str,
        direct_i2p_destination: &str,
        key_file: &Path,
        resource_profile: ResourceProfile,
    ) -> Result<Self> {
        Self::new(
            tor_destinations.to_vec(),
            i2p_destinations.to_vec(),
            direct_tor_destination.to_owned(),
            direct_i2p_destination.to_owned(),
            read_bond_key(key_file)?,
            resource_profile,
        )
    }

    fn new(
        tor_destinations: Vec<String>,
        i2p_destinations: Vec<String>,
        direct_tor_destination: String,
        direct_i2p_destination: String,
        key: Zeroizing<[u8; 32]>,
        resource_profile: ResourceProfile,
    ) -> Result<Self> {
        validate_destinations("Tor", &tor_destinations, PRODUCTION_TOR_SLOTS)?;
        validate_destinations("I2P", &i2p_destinations, PRODUCTION_I2P_SLOTS)?;
        if tor_destinations.len() != PRODUCTION_TOR_SLOTS
            || i2p_destinations.len() != PRODUCTION_I2P_SLOTS
        {
            bail!("automatic routing requires complete Tor and I2P destination pools");
        }
        validate_destination("direct Tor", &direct_tor_destination)?;
        validate_destination("direct I2P", &direct_i2p_destination)?;
        Ok(Self {
            tor_destinations,
            i2p_destinations,
            direct_tor_destination,
            direct_i2p_destination,
            key,
            resource_profile,
        })
    }

    fn bond_request(&self, route: AutoRoute) -> Result<BondRequest> {
        let (tor, i2p) = match route {
            AutoRoute::BondMixed => (self.tor_destinations.clone(), self.i2p_destinations.clone()),
            AutoRoute::BondTor => (self.tor_destinations.clone(), Vec::new()),
            AutoRoute::BondI2p => (Vec::new(), self.i2p_destinations.clone()),
            AutoRoute::Tor | AutoRoute::I2p => bail!("direct route has no bond request"),
        };
        BondRequest::new(tor, i2p, Zeroizing::new(*self.key), self.resource_profile)
    }

    async fn write_payload<W: AsyncWrite + Unpin>(&self, writer: &mut W) -> Result<()> {
        writer.write_u8(self.resource_profile.wire_code()).await?;
        write_destinations(writer, &self.tor_destinations).await?;
        write_destinations(writer, &self.i2p_destinations).await?;
        write_destination(writer, &self.direct_tor_destination).await?;
        write_destination(writer, &self.direct_i2p_destination).await?;
        writer.write_all(self.key.as_ref()).await?;
        Ok(())
    }

    async fn read_payload<R: AsyncRead + Unpin>(reader: &mut R) -> Result<Self> {
        let resource_profile = ResourceProfile::from_wire_code(reader.read_u8().await?)?;
        let tor_destinations = read_destinations(reader, PRODUCTION_TOR_SLOTS).await?;
        let i2p_destinations = read_destinations(reader, PRODUCTION_I2P_SLOTS).await?;
        let direct_tor_destination = read_destination(reader).await?;
        let direct_i2p_destination = read_destination(reader).await?;
        let mut key = Zeroizing::new([0_u8; 32]);
        reader.read_exact(key.as_mut()).await?;
        Self::new(
            tor_destinations,
            i2p_destinations,
            direct_tor_destination,
            direct_i2p_destination,
            key,
            resource_profile,
        )
    }
}

fn read_bond_key(key_file: &Path) -> Result<Zeroizing<[u8; 32]>> {
    let encoded =
        Zeroizing::new(fs::read(key_file).context("failed to read the ephemeral bond key")?);
    if encoded.len() != 32 {
        bail!("ephemeral bond key has an invalid length");
    }
    let mut key = Zeroizing::new([0_u8; 32]);
    key.copy_from_slice(&encoded);
    Ok(key)
}

fn validate_destinations(label: &str, destinations: &[String], expected: usize) -> Result<()> {
    if !destinations.is_empty() && destinations.len() != expected {
        bail!("{label} bond topology requires exactly {expected} destinations");
    }
    if destinations
        .iter()
        .any(|destination| destination.is_empty() || destination.len() > MAX_DESTINATION_BYTES)
    {
        bail!("{label} bond destination has an invalid length");
    }
    Ok(())
}

fn validate_destination(label: &str, destination: &str) -> Result<()> {
    if destination.is_empty() || destination.len() > MAX_DESTINATION_BYTES {
        bail!("{label} destination has an invalid length");
    }
    Ok(())
}

async fn write_destination<W: AsyncWrite + Unpin>(writer: &mut W, destination: &str) -> Result<()> {
    validate_destination("direct", destination)?;
    writer
        .write_u16(u16::try_from(destination.len()).context("broker destination is too long")?)
        .await?;
    writer.write_all(destination.as_bytes()).await?;
    Ok(())
}

async fn read_destination<R: AsyncRead + Unpin>(reader: &mut R) -> Result<String> {
    let length = usize::from(reader.read_u16().await?);
    if length == 0 || length > MAX_DESTINATION_BYTES {
        bail!("bond broker request declared an invalid destination length");
    }
    let mut encoded = vec![0_u8; length];
    reader.read_exact(&mut encoded).await?;
    String::from_utf8(encoded).context("bond destination is not UTF-8")
}

async fn write_destinations<W: AsyncWrite + Unpin>(
    writer: &mut W,
    destinations: &[String],
) -> Result<()> {
    writer
        .write_u16(u16::try_from(destinations.len()).context("too many broker destinations")?)
        .await?;
    for destination in destinations {
        writer
            .write_u16(u16::try_from(destination.len()).context("broker destination is too long")?)
            .await?;
        writer.write_all(destination.as_bytes()).await?;
    }
    Ok(())
}

async fn read_destinations<R: AsyncRead + Unpin>(
    reader: &mut R,
    maximum: usize,
) -> Result<Vec<String>> {
    let count = usize::from(reader.read_u16().await?);
    if count > maximum {
        bail!("bond broker request declared too many destinations");
    }
    let mut destinations = Vec::with_capacity(count);
    for _ in 0..count {
        let length = usize::from(reader.read_u16().await?);
        if length == 0 || length > MAX_DESTINATION_BYTES {
            bail!("bond broker request declared an invalid destination length");
        }
        let mut encoded = vec![0_u8; length];
        reader.read_exact(&mut encoded).await?;
        destinations.push(String::from_utf8(encoded).context("bond destination is not UTF-8")?);
    }
    Ok(destinations)
}

fn hash_destinations(digest: &mut Sha256, provider: u8, destinations: &[String]) {
    digest.update([provider]);
    digest.update((destinations.len() as u64).to_be_bytes());
    for destination in destinations {
        digest.update((destination.len() as u64).to_be_bytes());
        digest.update(destination.as_bytes());
    }
}

struct BrokerPaths {
    directory: PathBuf,
    socket: PathBuf,
    transport_socket: PathBuf,
    lease: PathBuf,
}

impl BrokerPaths {
    fn for_user() -> Result<Self> {
        let base = dirs::runtime_dir()
            .or_else(|| dirs::cache_dir().map(|path| path.join("anonssh-runtime")))
            .context("cannot resolve a private runtime directory for the bond broker")?;
        Ok(Self::under(base.join("anonssh")))
    }

    fn under(directory: PathBuf) -> Self {
        Self {
            socket: directory.join("bond-broker.sock"),
            transport_socket: directory.join("transport.sock"),
            lease: directory.join("bond-broker.lease"),
            directory,
        }
    }
}

struct BrokerSocket {
    private_listener: UnixListener,
    transport_listener: UnixListener,
    paths: BrokerPaths,
}

impl BrokerSocket {
    async fn claim(paths: BrokerPaths) -> Result<Option<Self>> {
        ensure_private_runtime_directory(&paths.directory)?;
        let started = Instant::now();
        loop {
            match fs::create_dir(&paths.lease) {
                Ok(()) => break,
                Err(error) if error.kind() == io::ErrorKind::AlreadyExists => {
                    if UnixStream::connect(&paths.socket).await.is_ok() {
                        return Ok(None);
                    }
                    if started.elapsed() < STALE_LEASE_GRACE {
                        sleep(Duration::from_millis(25)).await;
                        continue;
                    }
                    match fs::remove_dir(&paths.lease) {
                        Ok(()) => continue,
                        Err(error) if error.kind() == io::ErrorKind::NotFound => continue,
                        Err(error) => {
                            return Err(error).context("failed to reclaim stale broker lease")
                        }
                    }
                }
                Err(error) => return Err(error).context("failed to acquire bond broker lease"),
            }
        }
        remove_stale_socket(&paths.socket)?;
        remove_stale_socket(&paths.transport_socket)?;
        let private_listener = match UnixListener::bind(&paths.socket) {
            Ok(listener) => listener,
            Err(error) => {
                let _ = fs::remove_dir(&paths.lease);
                return Err(error).context("failed to bind bond broker socket");
            }
        };
        let transport_listener = match UnixListener::bind(&paths.transport_socket) {
            Ok(listener) => listener,
            Err(error) => {
                let _ = fs::remove_file(&paths.socket);
                let _ = fs::remove_dir(&paths.lease);
                return Err(error).context("failed to bind ALP transport socket");
            }
        };
        fs::set_permissions(&paths.socket, fs::Permissions::from_mode(0o600))?;
        fs::set_permissions(&paths.transport_socket, fs::Permissions::from_mode(0o600))?;
        Ok(Some(Self {
            private_listener,
            transport_listener,
            paths,
        }))
    }

    fn private_listener(&self) -> &UnixListener {
        &self.private_listener
    }

    fn transport_listener(&self) -> &UnixListener {
        &self.transport_listener
    }
}

fn ensure_private_runtime_directory(path: &Path) -> Result<()> {
    match fs::symlink_metadata(path) {
        Ok(_) => {}
        Err(error) if error.kind() == io::ErrorKind::NotFound => {
            let mut builder = fs::DirBuilder::new();
            builder.recursive(true).mode(0o700);
            builder
                .create(path)
                .context("failed to create bond broker runtime directory")?;
        }
        Err(error) => return Err(error).context("failed to inspect bond broker runtime directory"),
    }
    let metadata = fs::symlink_metadata(path)
        .context("failed to inspect bond broker runtime directory after creation")?;
    if !metadata.file_type().is_dir() {
        bail!("bond broker runtime path is not a real directory");
    }
    if metadata.uid() != unsafe { libc::geteuid() } {
        bail!("bond broker runtime directory is not owned by the current user");
    }
    if metadata.permissions().mode() & 0o077 != 0 {
        bail!("bond broker runtime directory is accessible by another user");
    }
    Ok(())
}

impl Drop for BrokerSocket {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.paths.socket);
        let _ = fs::remove_file(&self.paths.transport_socket);
        let _ = fs::remove_dir(&self.paths.lease);
        let _ = fs::remove_dir(&self.paths.directory);
    }
}

fn remove_stale_socket(path: &Path) -> Result<()> {
    match fs::symlink_metadata(path) {
        Ok(metadata) if metadata.file_type().is_socket() => {
            fs::remove_file(path)?;
            Ok(())
        }
        Ok(_) => bail!("bond broker socket path is occupied by a non-socket file"),
        Err(error) if error.kind() == io::ErrorKind::NotFound => Ok(()),
        Err(error) => Err(error.into()),
    }
}

fn spawn_broker(resident: bool) -> Result<()> {
    let executable = std::env::current_exe().context("failed to resolve anonssh executable")?;
    let mut command = Command::new(executable);
    command.arg("bond-broker");
    if resident {
        command.arg("--resident");
    }
    command.stdin(Stdio::null()).stdout(Stdio::null());
    if verbose_output() {
        command.stderr(Stdio::inherit());
    } else {
        command.stderr(Stdio::null());
    }
    command
        .spawn()
        .context("failed to launch the AnonSSH bond broker")?;
    Ok(())
}

async fn stop_existing_before_claim(path: &Path) -> Result<()> {
    let mut stream = match UnixStream::connect(path).await {
        Ok(stream) => stream,
        Err(error) if broker_is_absent(&error) => return Ok(()),
        Err(error) => return Err(error).context("failed to inspect the existing bond broker"),
    };
    BrokerRequest::Stop.write_to(&mut stream).await?;
    let mut response = [0_u8; 4];
    stream.read_exact(&mut response).await?;
    if response != RESPONSE_READY {
        bail!("existing bond broker rejected resident takeover");
    }
    drop(stream);
    let deadline = Instant::now() + SOCKET_START_DEADLINE;
    loop {
        match UnixStream::connect(path).await {
            Err(error) if broker_is_absent(&error) => return Ok(()),
            Err(error) if Instant::now() >= deadline => {
                return Err(error).context("existing bond broker did not release its socket");
            }
            Ok(_) | Err(_) => {}
        }
        sleep(Duration::from_millis(25)).await;
    }
}

async fn connect_when_ready(path: &Path) -> Result<UnixStream> {
    let deadline = Instant::now() + SOCKET_START_DEADLINE;
    loop {
        match UnixStream::connect(path).await {
            Ok(stream) => return Ok(stream),
            Err(error) if Instant::now() >= deadline => {
                return Err(error)
                    .context("bond broker did not publish its socket before the startup deadline");
            }
            Err(_) => {}
        }
        sleep(Duration::from_millis(25)).await;
    }
}

async fn wait_for_broker_generation(
    path: &Path,
    previous_process_id: Option<u32>,
    resident: bool,
) -> Result<()> {
    let deadline = Instant::now() + SOCKET_START_DEADLINE;
    loop {
        match status().await {
            Ok(status)
                if status.running
                    && status.resident == resident
                    && status.process_id != previous_process_id =>
            {
                return Ok(())
            }
            Ok(_) | Err(_) if Instant::now() < deadline => {}
            Ok(_) => bail!("bond broker did not enter the requested resident generation"),
            Err(error) => {
                return Err(error)
                    .context("bond broker did not enter the requested resident generation")
            }
        }
        sleep(Duration::from_millis(25)).await;
        if !path.exists() && Instant::now() >= deadline {
            bail!("bond broker did not publish its resident socket")
        }
    }
}

fn broker_is_absent(error: &io::Error) -> bool {
    matches!(
        error.kind(),
        io::ErrorKind::NotFound | io::ErrorKind::ConnectionRefused
    )
}

async fn relay_stdio(stream: UnixStream) -> Result<()> {
    let input = AsyncFileDescriptor::duplicate(libc::STDIN_FILENO)?;
    let output = AsyncFileDescriptor::duplicate(libc::STDOUT_FILENO)?;
    relay_local_stream(stream, input, output).await
}

struct AsyncFileDescriptor {
    inner: AsyncFd<RestoringFileDescriptor>,
}

struct RestoringFileDescriptor {
    inner: OwnedFd,
    clear_nonblocking_on_drop: bool,
}

impl AsRawFd for RestoringFileDescriptor {
    fn as_raw_fd(&self) -> RawFd {
        self.inner.as_raw_fd()
    }
}

impl Drop for RestoringFileDescriptor {
    fn drop(&mut self) {
        if !self.clear_nonblocking_on_drop {
            return;
        }
        let flags = unsafe { libc::fcntl(self.as_raw_fd(), libc::F_GETFL) };
        if flags >= 0 {
            let _ =
                unsafe { libc::fcntl(self.as_raw_fd(), libc::F_SETFL, flags & !libc::O_NONBLOCK) };
        }
    }
}

impl AsyncFileDescriptor {
    fn duplicate(source: RawFd) -> io::Result<Self> {
        // The proxy must not use tokio::io::stdin: its blocking worker cannot be
        // cancelled when the broker closes while OpenSSH keeps stdin open.
        let duplicated = unsafe { libc::fcntl(source, libc::F_DUPFD_CLOEXEC, 0) };
        if duplicated < 0 {
            return Err(io::Error::last_os_error());
        }
        // SAFETY: F_DUPFD_CLOEXEC returned a new descriptor owned by this process.
        let descriptor = unsafe { OwnedFd::from_raw_fd(duplicated) };
        Self::from_owned(descriptor)
    }

    fn from_owned(descriptor: OwnedFd) -> io::Result<Self> {
        let flags = unsafe { libc::fcntl(descriptor.as_raw_fd(), libc::F_GETFL) };
        if flags < 0 {
            return Err(io::Error::last_os_error());
        }
        let clear_nonblocking_on_drop = flags & libc::O_NONBLOCK == 0;
        if clear_nonblocking_on_drop
            && unsafe {
                libc::fcntl(
                    descriptor.as_raw_fd(),
                    libc::F_SETFL,
                    flags | libc::O_NONBLOCK,
                )
            } < 0
        {
            return Err(io::Error::last_os_error());
        }
        Ok(Self {
            inner: AsyncFd::new(RestoringFileDescriptor {
                inner: descriptor,
                clear_nonblocking_on_drop,
            })?,
        })
    }
}

impl AsyncRead for AsyncFileDescriptor {
    fn poll_read(
        self: Pin<&mut Self>,
        context: &mut TaskContext<'_>,
        buffer: &mut ReadBuf<'_>,
    ) -> Poll<io::Result<()>> {
        loop {
            let mut readiness = ready!(self.inner.poll_read_ready(context))?;
            let unfilled = buffer.initialize_unfilled();
            match readiness.try_io(|inner| {
                let read = unsafe {
                    libc::read(
                        inner.get_ref().as_raw_fd(),
                        unfilled.as_mut_ptr().cast(),
                        unfilled.len(),
                    )
                };
                if read < 0 {
                    Err(io::Error::last_os_error())
                } else {
                    Ok(usize::try_from(read).expect("read byte count is non-negative"))
                }
            }) {
                Ok(Ok(read)) => {
                    buffer.advance(read);
                    return Poll::Ready(Ok(()));
                }
                Ok(Err(error)) => return Poll::Ready(Err(error)),
                Err(_) => continue,
            }
        }
    }
}

impl AsyncWrite for AsyncFileDescriptor {
    fn poll_write(
        self: Pin<&mut Self>,
        context: &mut TaskContext<'_>,
        buffer: &[u8],
    ) -> Poll<io::Result<usize>> {
        loop {
            let mut readiness = ready!(self.inner.poll_write_ready(context))?;
            match readiness.try_io(|inner| {
                let written = unsafe {
                    libc::write(
                        inner.get_ref().as_raw_fd(),
                        buffer.as_ptr().cast(),
                        buffer.len(),
                    )
                };
                if written < 0 {
                    Err(io::Error::last_os_error())
                } else {
                    Ok(usize::try_from(written).expect("write byte count is non-negative"))
                }
            }) {
                Ok(result) => return Poll::Ready(result),
                Err(_) => continue,
            }
        }
    }

    fn poll_flush(self: Pin<&mut Self>, _context: &mut TaskContext<'_>) -> Poll<io::Result<()>> {
        Poll::Ready(Ok(()))
    }

    fn poll_shutdown(self: Pin<&mut Self>, _context: &mut TaskContext<'_>) -> Poll<io::Result<()>> {
        Poll::Ready(Ok(()))
    }
}

async fn relay_local_stream<S, I, O>(stream: S, input: I, output: O) -> Result<()>
where
    S: AsyncRead + AsyncWrite + Unpin,
    I: AsyncRead + Unpin,
    O: AsyncWrite + Unpin,
{
    let (remote_read, mut remote_write) = tokio::io::split(stream);
    let mut input = BufReader::with_capacity(crate::data_stream::RELAY_BUFFER_BYTES, input);
    let mut remote_read =
        BufReader::with_capacity(crate::data_stream::RELAY_BUFFER_BYTES, remote_read);
    let mut output = output;
    let upstream = async {
        tokio::io::copy_buf(&mut input, &mut remote_write).await?;
        remote_write.shutdown().await
    };
    let downstream = async {
        tokio::io::copy_buf(&mut remote_read, &mut output).await?;
        output.shutdown().await
    };
    tokio::pin!(upstream);
    tokio::pin!(downstream);
    tokio::select! {
        result = &mut downstream => result?,
        result = &mut upstream => {
            result?;
            downstream.await?;
        }
    }
    Ok(())
}

async fn shutdown_signal() -> io::Result<()> {
    let mut terminate = tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate())?;
    tokio::select! {
        result = tokio::signal::ctrl_c() => result,
        signal = terminate.recv() => signal.map(|_| ()).ok_or_else(|| {
            io::Error::other("termination signal stream closed")
        }),
    }
}

fn merge_cleanup<T>(operation: Result<T>, cleanup: Result<()>) -> Result<T> {
    match (operation, cleanup) {
        (Ok(value), Ok(())) => Ok(value),
        (Err(error), Ok(())) => Err(error),
        (Ok(_), Err(error)) => Err(error),
        (Err(operation), Err(cleanup)) => Err(anyhow::anyhow!(
            "{operation:#}; cleanup also failed: {cleanup:#}"
        )),
    }
}

#[cfg(test)]
mod tests {
    use std::os::fd::{AsRawFd, FromRawFd, OwnedFd};
    use std::os::unix::fs::PermissionsExt;
    use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};
    use std::sync::Arc;
    use std::time::Duration;

    use tokio::io::{AsyncReadExt, AsyncWriteExt};

    use super::{
        authorize_broker_target, auto_route_human_label, classify_alp_route_error,
        ensure_private_runtime_directory, human_duration, latest_started_progress_sequence,
        peer_uid_is_authorized, race_auto_candidates, read_auto_report, read_progress_payload,
        reject_connection_at_listener_capacity, relay_local_stream, requested_warm_baseline,
        router_progress_summary, session_entry, write_auto_report, write_progress_payload,
        AsyncFileDescriptor, AuthorizationRegistry, AutoAttemptOutcome, AutoCandidateSpec,
        AutoRequest, AutoRoute, AutoRouteAttempt, AutoRouteReport, BondRequest, BrokerMetrics,
        BrokerPaths, BrokerRequest, BrokerSocket, ConnectionProgressOutput, SessionRegistry,
        WarmPolicyState, REQUEST_MAGIC, RESPONSE_AUTO_REPORT, RESPONSE_PROGRESS,
    };
    use crate::application_service::{ServiceRejection, ServiceSetupError};
    use crate::local_transport::{AlpErrorCode, AlpTransport};
    use crate::product_config::ResourceProfile;
    use crate::router_pool::{
        RouterProgressDetail, RouterProgressEvent, RouterProgressPhase, RouterProgressSnapshot,
        RouterProvider,
    };

    #[test]
    fn alp_preserves_native_service_failure_categories() {
        let cases = [
            (
                ServiceSetupError::Rejected {
                    rejection: ServiceRejection::UnknownService,
                    reason: "missing".to_owned(),
                },
                AlpErrorCode::UnknownService,
            ),
            (
                ServiceSetupError::Rejected {
                    rejection: ServiceRejection::ClassDenied,
                    reason: "wrong class".to_owned(),
                },
                AlpErrorCode::ClassDenied,
            ),
            (
                ServiceSetupError::Rejected {
                    rejection: ServiceRejection::Capacity,
                    reason: "busy".to_owned(),
                },
                AlpErrorCode::Capacity,
            ),
            (
                ServiceSetupError::Rejected {
                    rejection: ServiceRejection::Unavailable,
                    reason: "down".to_owned(),
                },
                AlpErrorCode::ServiceUnavailable,
            ),
            (
                ServiceSetupError::PeerIncompatible,
                AlpErrorCode::PeerIncompatible,
            ),
            (ServiceSetupError::Timeout, AlpErrorCode::Timeout),
        ];
        for (error, expected) in cases {
            let wrapped = anyhow::Error::new(error).context("outer route context");
            assert_eq!(classify_alp_route_error(&wrapped).0, expected);
        }
        assert_eq!(
            classify_alp_route_error(&anyhow::anyhow!("network failed")).0,
            AlpErrorCode::RouteUnavailable
        );
    }

    static DIRECTORY_SEQUENCE: AtomicU64 = AtomicU64::new(1);

    fn destinations(prefix: &str, count: usize) -> Vec<String> {
        (1..=count).map(|slot| format!("{prefix}-{slot}")).collect()
    }

    fn request(key: u8) -> BondRequest {
        request_with_profile(key, ResourceProfile::Performance)
    }

    fn request_with_profile(key: u8, resource_profile: ResourceProfile) -> BondRequest {
        BondRequest::new(
            destinations("tor", super::PRODUCTION_TOR_SLOTS),
            destinations("i2p", super::PRODUCTION_I2P_SLOTS),
            zeroize::Zeroizing::new([key; 32]),
            resource_profile,
        )
        .unwrap()
    }

    fn progress_event(
        provider: RouterProvider,
        slot: u32,
        phase: RouterProgressPhase,
    ) -> RouterProgressEvent {
        RouterProgressEvent {
            sequence: u64::from(slot),
            elapsed_millis: 2_000,
            provider,
            slot,
            phase,
            detail: RouterProgressDetail::RouterStartup,
            attempt: 1,
            operation_deadline_millis: Some(900_000),
            retry_after_millis: None,
        }
    }

    #[test]
    fn default_progress_is_provider_level_and_deduplicated() {
        let progress = RouterProgressSnapshot {
            schema: "anonssh.router-progress.v1".to_owned(),
            observed_millis: 2_000,
            slots: vec![
                progress_event(RouterProvider::Tor, 1, RouterProgressPhase::Active),
                progress_event(RouterProvider::Tor, 2, RouterProgressPhase::RouterReady),
                progress_event(RouterProvider::I2p, 1, RouterProgressPhase::Starting),
                progress_event(RouterProvider::I2p, 2, RouterProgressPhase::Backoff),
            ],
            recent_events: Vec::new(),
        };
        assert_eq!(
            router_progress_summary(&progress).as_deref(),
            Some("Tor: 1 connected, 1 router ready | I2P: 1 starting, 1 retrying")
        );
        let mut output = ConnectionProgressOutput::default();
        assert!(output.changed_summary(&progress).is_some());
        assert!(output.changed_summary(&progress).is_none());
    }

    #[test]
    fn selected_route_and_elapsed_time_are_human_readable() {
        assert_eq!(
            auto_route_human_label(AutoRoute::BondMixed),
            "Tor + I2P bond"
        );
        assert_eq!(human_duration(731), "731 ms");
        assert_eq!(human_duration(12_345), "12.3 s");
        assert_eq!(human_duration(125_000), "2m 05s");
    }

    fn auto_request(key: u8) -> AutoRequest {
        AutoRequest::new(
            destinations("tor", super::PRODUCTION_TOR_SLOTS),
            destinations("i2p", super::PRODUCTION_I2P_SLOTS),
            "direct.onion".to_owned(),
            "direct.b32.i2p".to_owned(),
            zeroize::Zeroizing::new([key; 32]),
            ResourceProfile::Performance,
        )
        .unwrap()
    }

    struct DropMarker(Arc<AtomicUsize>);

    impl Drop for DropMarker {
        fn drop(&mut self) {
            self.0.fetch_add(1, Ordering::SeqCst);
        }
    }

    #[tokio::test]
    async fn broker_request_round_trips_with_explicit_bounds() {
        let expected = request(7);
        let expected_key = expected.topology_key();
        let (mut writer, mut reader) = tokio::io::duplex(32 * 1024);
        let write =
            tokio::spawn(async move { BrokerRequest::Bond(expected).write_to(&mut writer).await });
        let BrokerRequest::Bond(decoded) = BrokerRequest::read_from(&mut reader).await.unwrap()
        else {
            panic!("bond request decoded as a direct route");
        };
        write.await.unwrap().unwrap();

        assert_eq!(decoded.topology_key(), expected_key);
        assert!(decoded.key_matches(&request(7)));
        assert_eq!(decoded.tor_destinations.len(), super::PRODUCTION_TOR_SLOTS);
        assert_eq!(decoded.i2p_destinations.len(), super::PRODUCTION_I2P_SLOTS);
        assert_eq!(decoded.resource_profile, ResourceProfile::Performance);

        let (mut writer, mut reader) = tokio::io::duplex(16);
        writer.write_all(b"ABR9\0\0\0\0").await.unwrap();
        assert!(BrokerRequest::read_from(&mut reader).await.is_err());
        assert_ne!(REQUEST_MAGIC, *b"ABR9");

        let (mut writer, mut reader) = tokio::io::duplex(16);
        writer.write_all(&REQUEST_MAGIC).await.unwrap();
        writer.write_u8(super::REQUEST_BOND).await.unwrap();
        writer.write_u8(u8::MAX).await.unwrap();
        assert!(BrokerRequest::read_from(&mut reader).await.is_err());
    }

    #[tokio::test]
    async fn authorization_request_round_trips_without_exposing_it_on_alp() {
        let expected = request(8);
        let expected_key = expected.topology_key();
        let (mut writer, mut reader) = tokio::io::duplex(32 * 1024);
        let write = tokio::spawn(async move {
            BrokerRequest::Authorize {
                target: "alice@home-1".to_owned(),
                request: expected,
            }
            .write_to(&mut writer)
            .await
        });
        let BrokerRequest::Authorize {
            target,
            request: decoded,
        } = BrokerRequest::read_from(&mut reader).await.unwrap()
        else {
            panic!("authorization request decoded as another mode");
        };
        write.await.unwrap().unwrap();
        assert_eq!(target, "alice@home-1");
        assert_eq!(decoded.topology_key(), expected_key);
        assert!(decoded.key_matches(&request(8)));
    }

    #[tokio::test(start_paused = true)]
    async fn authorization_registry_is_bounded_to_live_idle_targets() {
        let registry = AuthorizationRegistry::new(std::collections::BTreeMap::new());
        authorize_broker_target(&registry, "alice@first".to_owned(), request(1))
            .await
            .unwrap();
        tokio::time::sleep(super::AUTHORIZATION_IDLE_TIMEOUT + Duration::from_secs(1)).await;
        authorize_broker_target(&registry, "alice@second".to_owned(), request(2))
            .await
            .unwrap();
        let targets = registry.lock().await;
        assert_eq!(targets.len(), 1);
        assert!(targets.contains_key("alice@second"));
    }

    #[test]
    fn authorization_selects_only_declared_provider_topologies() {
        let request = request(4);
        let mixed = request.for_transport(AlpTransport::Mixed).unwrap();
        assert_eq!(mixed.tor_destinations.len(), super::PRODUCTION_TOR_SLOTS);
        assert_eq!(mixed.i2p_destinations.len(), super::PRODUCTION_I2P_SLOTS);
        let tor = request.for_transport(AlpTransport::TorOnly).unwrap();
        assert_eq!(tor.tor_destinations.len(), super::PRODUCTION_TOR_SLOTS);
        assert!(tor.i2p_destinations.is_empty());
        let i2p = request.for_transport(AlpTransport::I2pOnly).unwrap();
        assert!(i2p.tor_destinations.is_empty());
        assert_eq!(i2p.i2p_destinations.len(), super::PRODUCTION_I2P_SLOTS);
        assert!(request.key_matches(&mixed));
        assert!(request.key_matches(&tor));
        assert!(request.key_matches(&i2p));
    }

    #[test]
    fn alp_peer_credentials_require_the_broker_owner_uid() {
        assert!(peer_uid_is_authorized(1_000, 1_000));
        assert!(!peer_uid_is_authorized(1_001, 1_000));
        assert!(!peer_uid_is_authorized(0, 1_000));
    }

    #[tokio::test]
    async fn automatic_request_and_report_round_trip_with_explicit_bounds() {
        let expected = auto_request(9);
        let (mut writer, mut reader) = tokio::io::duplex(32 * 1024);
        let write =
            tokio::spawn(async move { BrokerRequest::Auto(expected).write_to(&mut writer).await });
        let BrokerRequest::Auto(decoded) = BrokerRequest::read_from(&mut reader).await.unwrap()
        else {
            panic!("automatic request decoded as another route");
        };
        write.await.unwrap().unwrap();
        assert_eq!(decoded.tor_destinations.len(), super::PRODUCTION_TOR_SLOTS);
        assert_eq!(decoded.i2p_destinations.len(), super::PRODUCTION_I2P_SLOTS);
        assert_eq!(decoded.direct_tor_destination, "direct.onion");
        assert_eq!(decoded.direct_i2p_destination, "direct.b32.i2p");
        assert_eq!(decoded.key.as_ref(), &[9_u8; 32]);

        let report = AutoRouteReport {
            schema: "anonssh.auto-route.v1".to_owned(),
            winner: AutoRoute::BondTor,
            elapsed_millis: 123,
            attempts: vec![AutoRouteAttempt {
                route: AutoRoute::BondTor,
                start_delay_millis: 10,
                completed_millis: Some(123),
                outcome: AutoAttemptOutcome::Succeeded,
            }],
        };
        let expected = report.clone();
        let (mut writer, mut reader) = tokio::io::duplex(4_096);
        let write = tokio::spawn(async move { write_auto_report(&mut writer, &report).await });
        let mut magic = [0_u8; 4];
        reader.read_exact(&mut magic).await.unwrap();
        assert_eq!(magic, RESPONSE_AUTO_REPORT);
        assert_eq!(read_auto_report(&mut reader).await.unwrap(), expected);
        write.await.unwrap().unwrap();
    }

    #[tokio::test(start_paused = true)]
    async fn automatic_race_prefers_a_fast_bond_before_fallback_start() {
        let specs = [
            AutoCandidateSpec {
                route: AutoRoute::BondMixed,
                start_delay: Duration::ZERO,
                deadline: Duration::from_secs(10),
            },
            AutoCandidateSpec {
                route: AutoRoute::Tor,
                start_delay: Duration::from_secs(2),
                deadline: Duration::from_secs(10),
            },
        ];
        let winner = race_auto_candidates(&specs, |route| async move {
            tokio::time::sleep(Duration::from_secs(1)).await;
            Ok::<_, anyhow::Error>(route)
        })
        .await
        .unwrap();
        assert_eq!(winner.value, AutoRoute::BondMixed);
        assert_eq!(winner.report.winner, AutoRoute::BondMixed);
        assert_eq!(
            winner.report.attempts[1].outcome,
            AutoAttemptOutcome::Canceled
        );
    }

    #[tokio::test(start_paused = true)]
    async fn automatic_race_escapes_a_stalled_bond_and_cancels_it() {
        let specs = [
            AutoCandidateSpec {
                route: AutoRoute::BondMixed,
                start_delay: Duration::ZERO,
                deadline: Duration::from_secs(30),
            },
            AutoCandidateSpec {
                route: AutoRoute::Tor,
                start_delay: Duration::from_secs(2),
                deadline: Duration::from_secs(10),
            },
        ];
        let canceled = Arc::new(AtomicUsize::new(0));
        let marker = canceled.clone();
        let winner = race_auto_candidates(&specs, move |route| {
            let marker = marker.clone();
            async move {
                match route {
                    AutoRoute::BondMixed => {
                        let _drop = DropMarker(marker);
                        std::future::pending::<Result<AutoRoute, anyhow::Error>>().await
                    }
                    AutoRoute::Tor => {
                        tokio::time::sleep(Duration::from_secs(1)).await;
                        Ok(route)
                    }
                    _ => unreachable!(),
                }
            }
        })
        .await
        .unwrap();
        assert_eq!(winner.value, AutoRoute::Tor);
        assert_eq!(canceled.load(Ordering::SeqCst), 1);
        assert_eq!(
            winner.report.attempts[0].outcome,
            AutoAttemptOutcome::Canceled
        );
    }

    #[tokio::test(start_paused = true)]
    async fn automatic_race_escapes_stalled_tor_through_i2p() {
        let specs = [
            AutoCandidateSpec {
                route: AutoRoute::Tor,
                start_delay: Duration::ZERO,
                deadline: Duration::from_secs(30),
            },
            AutoCandidateSpec {
                route: AutoRoute::I2p,
                start_delay: Duration::from_secs(1),
                deadline: Duration::from_secs(10),
            },
        ];
        let winner = race_auto_candidates(&specs, |route| async move {
            match route {
                AutoRoute::Tor => std::future::pending::<Result<AutoRoute, anyhow::Error>>().await,
                AutoRoute::I2p => {
                    tokio::time::sleep(Duration::from_secs(1)).await;
                    Ok(route)
                }
                _ => unreachable!(),
            }
        })
        .await
        .unwrap();
        assert_eq!(winner.value, AutoRoute::I2p);
    }

    #[tokio::test(start_paused = true)]
    async fn automatic_race_breaks_simultaneous_success_by_route_priority() {
        let specs = [
            AutoCandidateSpec {
                route: AutoRoute::Tor,
                start_delay: Duration::ZERO,
                deadline: Duration::from_secs(10),
            },
            AutoCandidateSpec {
                route: AutoRoute::BondMixed,
                start_delay: Duration::ZERO,
                deadline: Duration::from_secs(10),
            },
        ];
        let winner = race_auto_candidates(&specs, |route| async move {
            tokio::time::sleep(Duration::from_secs(1)).await;
            Ok::<_, anyhow::Error>(route)
        })
        .await
        .unwrap();
        assert_eq!(winner.value, AutoRoute::BondMixed);
        assert!(winner
            .report
            .attempts
            .iter()
            .all(|attempt| attempt.outcome == AutoAttemptOutcome::Succeeded));
    }

    #[tokio::test(start_paused = true)]
    async fn automatic_race_reports_independent_failure_and_timeout() {
        let specs = [
            AutoCandidateSpec {
                route: AutoRoute::BondMixed,
                start_delay: Duration::ZERO,
                deadline: Duration::from_secs(10),
            },
            AutoCandidateSpec {
                route: AutoRoute::Tor,
                start_delay: Duration::ZERO,
                deadline: Duration::from_secs(2),
            },
        ];
        let error = race_auto_candidates(&specs, |route| async move {
            match route {
                AutoRoute::BondMixed => Err(anyhow::anyhow!("rejected")),
                AutoRoute::Tor => {
                    tokio::time::sleep(Duration::from_secs(20)).await;
                    Ok(route)
                }
                _ => unreachable!(),
            }
        })
        .await
        .unwrap_err();
        let error = format!("{error:#}");
        assert!(error.contains("bond-mixed: rejected"));
        assert!(error.contains("tor: exceeded 2 seconds"));
    }

    #[tokio::test]
    async fn progress_frames_round_trip_before_stream_readiness() {
        let event = RouterProgressEvent {
            sequence: 7,
            elapsed_millis: 2_000,
            provider: RouterProvider::I2p,
            slot: 3,
            phase: RouterProgressPhase::Repairing,
            detail: RouterProgressDetail::RouterStartup,
            attempt: 2,
            operation_deadline_millis: Some(900_000),
            retry_after_millis: None,
        };
        let progress = RouterProgressSnapshot {
            schema: "anonssh.router-progress.v1".to_owned(),
            observed_millis: 2_000,
            slots: vec![event.clone()],
            recent_events: vec![event],
        };
        let expected = progress.clone();
        let (mut writer, mut reader) = tokio::io::duplex(4_096);
        let write = tokio::spawn(async move {
            write_progress_payload(&mut writer, &progress)
                .await
                .unwrap();
            writer.write_all(b"SSH-").await.unwrap();
        });
        let mut magic = [0_u8; 4];
        reader.read_exact(&mut magic).await.unwrap();
        assert_eq!(magic, RESPONSE_PROGRESS);
        let decoded = read_progress_payload(&mut reader).await.unwrap();
        assert_eq!(decoded, expected);
        assert_eq!(latest_started_progress_sequence(&decoded), 7);
        reader.read_exact(&mut magic).await.unwrap();
        assert_eq!(&magic, b"SSH-");
        write.await.unwrap();
    }

    #[tokio::test]
    async fn direct_requests_round_trip_without_session_keys() {
        for expected in [
            BrokerRequest::Tor("example.onion".to_owned()),
            BrokerRequest::I2p("example.b32.i2p".to_owned()),
        ] {
            let (mut writer, mut reader) = tokio::io::duplex(1_024);
            let write = tokio::spawn(async move { expected.write_to(&mut writer).await });
            match BrokerRequest::read_from(&mut reader).await.unwrap() {
                BrokerRequest::Tor(destination) => assert_eq!(destination, "example.onion"),
                BrokerRequest::I2p(destination) => assert_eq!(destination, "example.b32.i2p"),
                BrokerRequest::Bond(_) | BrokerRequest::Auto(_) => {
                    panic!("direct request decoded as a pooled route")
                }
                BrokerRequest::Authorize { .. } => {
                    panic!("direct request decoded as authorization")
                }
                BrokerRequest::Status | BrokerRequest::Stop => {
                    panic!("direct request decoded as broker control")
                }
            }
            write.await.unwrap().unwrap();
        }
    }

    #[tokio::test]
    async fn broker_control_requests_round_trip() {
        for expected in [BrokerRequest::Status, BrokerRequest::Stop] {
            let (mut writer, mut reader) = tokio::io::duplex(64);
            let write = tokio::spawn(async move { expected.write_to(&mut writer).await });
            let decoded = BrokerRequest::read_from(&mut reader).await.unwrap();
            assert!(matches!(
                decoded,
                BrokerRequest::Status | BrokerRequest::Stop
            ));
            write.await.unwrap().unwrap();
        }
    }

    #[tokio::test]
    async fn broker_metrics_distinguish_session_local_stream_ids() {
        let metrics = BrokerMetrics::default();
        metrics.record_stream(7, 1).await;
        metrics.record_stream(8, 1).await;

        let streams = metrics.recent_streams.lock().await;
        assert_eq!(streams.len(), 2);
        assert_ne!(streams[0], streams[1]);
        assert_eq!(streams[0].stream_id, streams[1].stream_id);
    }

    #[tokio::test]
    async fn broker_shutdown_ends_proxy_with_open_client_input() {
        let (relay_remote, mut broker) = tokio::io::duplex(1_024);
        let mut pipe = [-1; 2];
        assert_eq!(
            unsafe { libc::pipe2(pipe.as_mut_ptr(), libc::O_CLOEXEC) },
            0
        );
        // SAFETY: pipe2 initialized two new descriptors, each transferred once.
        let input =
            AsyncFileDescriptor::from_owned(unsafe { OwnedFd::from_raw_fd(pipe[0]) }).unwrap();
        // Keeping the writer open reproduces OpenSSH holding ProxyCommand stdin.
        let _open_input_peer = unsafe { OwnedFd::from_raw_fd(pipe[1]) };
        let (output, mut output_reader) = tokio::io::duplex(1_024);
        let relay = tokio::spawn(relay_local_stream(relay_remote, input, output));

        broker.write_all(b"server closed").await.unwrap();
        broker.shutdown().await.unwrap();
        let mut received = Vec::new();
        output_reader.read_to_end(&mut received).await.unwrap();

        tokio::time::timeout(std::time::Duration::from_secs(1), relay)
            .await
            .expect("proxy remained blocked on open client input")
            .unwrap()
            .unwrap();
        assert_eq!(received, b"server closed");
    }

    #[tokio::test]
    async fn async_descriptor_restores_shared_nonblocking_status() {
        let mut pipe = [-1; 2];
        assert_eq!(
            unsafe { libc::pipe2(pipe.as_mut_ptr(), libc::O_CLOEXEC) },
            0
        );
        let observer = unsafe { libc::fcntl(pipe[0], libc::F_DUPFD_CLOEXEC, 0) };
        assert!(observer >= 0);
        // SAFETY: pipe2 and fcntl each returned one owned descriptor.
        let source = unsafe { OwnedFd::from_raw_fd(pipe[0]) };
        let observer = unsafe { OwnedFd::from_raw_fd(observer) };
        let _writer = unsafe { OwnedFd::from_raw_fd(pipe[1]) };
        assert_eq!(
            unsafe { libc::fcntl(observer.as_raw_fd(), libc::F_GETFL) } & libc::O_NONBLOCK,
            0
        );

        let descriptor = AsyncFileDescriptor::from_owned(source).unwrap();
        assert_ne!(
            unsafe { libc::fcntl(observer.as_raw_fd(), libc::F_GETFL) } & libc::O_NONBLOCK,
            0
        );
        drop(descriptor);
        assert_eq!(
            unsafe { libc::fcntl(observer.as_raw_fd(), libc::F_GETFL) } & libc::O_NONBLOCK,
            0
        );
    }

    #[tokio::test]
    async fn saturated_listener_rejection_allocates_no_followup_work() {
        let (private, mut private_peer) = tokio::net::UnixStream::pair().unwrap();
        reject_connection_at_listener_capacity(private);
        let mut response = Vec::new();
        private_peer.read_to_end(&mut response).await.unwrap();
        assert!(response.is_empty());

        let (transport, mut transport_peer) = tokio::net::UnixStream::pair().unwrap();
        reject_connection_at_listener_capacity(transport);
        let mut response = Vec::new();
        transport_peer.read_to_end(&mut response).await.unwrap();
        assert!(response.is_empty());
    }

    #[test]
    fn session_identity_separates_topology_and_authentication() {
        let mixed = request(3);
        let wrong_key = request(4);
        let low_resource = request_with_profile(3, ResourceProfile::Low);
        let tor_only = BondRequest::new(
            destinations("tor", super::PRODUCTION_TOR_SLOTS),
            Vec::new(),
            zeroize::Zeroizing::new([3; 32]),
            ResourceProfile::Performance,
        )
        .unwrap();
        assert_eq!(mixed.topology_key(), wrong_key.topology_key());
        assert!(!mixed.key_matches(&wrong_key));
        assert_ne!(mixed.topology_key(), low_resource.topology_key());
        assert!(!mixed.same_topology(&low_resource));
        assert_ne!(mixed.topology_key(), tor_only.topology_key());
    }

    #[test]
    fn warm_policy_ramps_immediately_retains_slow_paths_and_drains_gradually() {
        let policy = ResourceProfile::Performance.resident_policy();
        let mut state = WarmPolicyState::new(policy, 8, 8);
        assert_eq!(
            state.update(Duration::ZERO, policy, (0, 0), (8, 8), (None, None), false,),
            (2, 2)
        );
        assert_eq!(
            state.update(
                Duration::from_secs(1),
                policy,
                (6, 5),
                (8, 8),
                (
                    Some(Duration::from_secs(400)),
                    Some(Duration::from_secs(30))
                ),
                false,
            ),
            (6, 5)
        );
        assert_eq!(
            state.update(
                Duration::from_secs(600),
                policy,
                (2, 2),
                (8, 8),
                (
                    Some(Duration::from_secs(400)),
                    Some(Duration::from_secs(30))
                ),
                false,
            ),
            (6, 4)
        );
        assert_eq!(
            state.update(
                Duration::from_secs(801),
                policy,
                (2, 2),
                (8, 8),
                (
                    Some(Duration::from_secs(400)),
                    Some(Duration::from_secs(30))
                ),
                false,
            ),
            (5, 4)
        );
        assert_eq!(
            state.update(
                Duration::from_secs(1_401),
                policy,
                (2, 2),
                (8, 8),
                (
                    Some(Duration::from_secs(400)),
                    Some(Duration::from_secs(30))
                ),
                false,
            ),
            (5, 3)
        );
    }

    #[test]
    fn warm_policy_obeys_profile_and_available_provider_ceilings() {
        let policy = ResourceProfile::Low.resident_policy();
        let mut state = WarmPolicyState::new(policy, 8, 0);
        assert_eq!(
            state.update(Duration::ZERO, policy, (8, 8), (8, 0), (None, None), false,),
            (2, 0)
        );
    }

    #[test]
    fn warm_policy_sheds_only_surplus_under_memory_pressure() {
        let policy = ResourceProfile::Performance.resident_policy();
        let mut state = WarmPolicyState::new(policy, 8, 8);
        assert_eq!(
            state.update(
                Duration::from_secs(1),
                policy,
                (6, 5),
                (8, 8),
                (None, None),
                false,
            ),
            (6, 5)
        );
        assert_eq!(
            state.update(
                Duration::from_secs(2),
                policy,
                (3, 2),
                (8, 8),
                (None, None),
                true,
            ),
            (5, 4)
        );
    }

    #[tokio::test]
    async fn pending_topologies_request_only_their_minimum_viable_warm_set() {
        let registry = SessionRegistry::new(std::collections::BTreeMap::new());
        let _mixed = session_entry(&registry, request(3), 16, true)
            .await
            .unwrap();
        assert_eq!(requested_warm_baseline(&registry).await, (2, 2));
        let tor_only = BondRequest::new(
            destinations("tor", super::PRODUCTION_TOR_SLOTS),
            Vec::new(),
            zeroize::Zeroizing::new([4; 32]),
            ResourceProfile::Performance,
        )
        .unwrap();
        session_entry(&registry, tor_only, 16, true).await.unwrap();
        assert_eq!(requested_warm_baseline(&registry).await, (4, 2));
    }

    #[tokio::test]
    async fn existing_topology_rejects_a_wrong_key_without_allocating_a_session() {
        let registry = SessionRegistry::new(std::collections::BTreeMap::new());
        let first = session_entry(&registry, request(3), 16, true)
            .await
            .unwrap();
        let error = session_entry(&registry, request(4), 16, true)
            .await
            .err()
            .expect("wrong key was accepted");
        assert!(error.to_string().contains("mismatched session key"));
        assert_eq!(registry.lock().await.len(), 1);

        let reused = session_entry(&registry, request(3), 16, true)
            .await
            .unwrap();
        assert!(std::sync::Arc::ptr_eq(&first, &reused));
    }

    #[tokio::test]
    async fn configured_destination_session_limit_is_enforced() {
        let registry = SessionRegistry::new(std::collections::BTreeMap::new());
        let _first = session_entry(&registry, request(3), 1, true).await.unwrap();
        let tor_only = BondRequest::new(
            destinations("tor", super::PRODUCTION_TOR_SLOTS),
            Vec::new(),
            zeroize::Zeroizing::new([3; 32]),
            ResourceProfile::Performance,
        )
        .unwrap();
        assert!(session_entry(&registry, tor_only, 1, true).await.is_err());
    }

    #[tokio::test]
    async fn state_quota_blocks_only_new_destination_sessions() {
        let registry = SessionRegistry::new(std::collections::BTreeMap::new());
        let first = session_entry(&registry, request(3), 16, true)
            .await
            .unwrap();
        let reused = session_entry(&registry, request(3), 16, false)
            .await
            .unwrap();
        assert!(Arc::ptr_eq(&first, &reused));
        let tor_only = BondRequest::new(
            destinations("tor", super::PRODUCTION_TOR_SLOTS),
            Vec::new(),
            zeroize::Zeroizing::new([3; 32]),
            ResourceProfile::Performance,
        )
        .unwrap();
        let error = session_entry(&registry, tor_only, 16, false)
            .await
            .err()
            .expect("state quota accepted a new destination");
        assert!(error.to_string().contains("state exceeds"));
    }

    #[tokio::test]
    async fn socket_lease_has_one_owner_and_reclaims_cleanly() {
        let root = std::env::temp_dir().join(format!(
            "anonssh-broker-test-{}-{}",
            std::process::id(),
            DIRECTORY_SEQUENCE.fetch_add(1, Ordering::Relaxed)
        ));
        let paths = BrokerPaths::under(root.clone());
        let owner = BrokerSocket::claim(paths).await.unwrap().unwrap();
        let paths = BrokerPaths::under(root.clone());
        assert!(BrokerSocket::claim(paths).await.unwrap().is_none());
        drop(owner);

        let paths = BrokerPaths::under(root.clone());
        let replacement = BrokerSocket::claim(paths).await.unwrap().unwrap();
        assert_eq!(
            std::fs::metadata(root.join("bond-broker.sock"))
                .unwrap()
                .permissions()
                .mode()
                & 0o777,
            0o600
        );
        assert_eq!(
            std::fs::metadata(root.join("transport.sock"))
                .unwrap()
                .permissions()
                .mode()
                & 0o777,
            0o600
        );
        drop(replacement);
        assert!(!root.exists());
    }

    #[test]
    fn broker_runtime_directory_rejects_links_and_shared_access() {
        let root = std::env::temp_dir().join(format!(
            "anonssh-broker-path-test-{}-{}",
            std::process::id(),
            DIRECTORY_SEQUENCE.fetch_add(1, Ordering::Relaxed)
        ));
        let target = root.with_extension("target");
        std::fs::create_dir(&target).unwrap();
        std::fs::set_permissions(&target, std::fs::Permissions::from_mode(0o700)).unwrap();
        std::os::unix::fs::symlink(&target, &root).unwrap();
        assert!(ensure_private_runtime_directory(&root).is_err());
        std::fs::remove_file(&root).unwrap();
        std::fs::remove_dir(&target).unwrap();

        std::fs::create_dir(&root).unwrap();
        std::fs::set_permissions(&root, std::fs::Permissions::from_mode(0o750)).unwrap();
        assert!(ensure_private_runtime_directory(&root).is_err());
        std::fs::remove_dir(root).unwrap();
    }
}
