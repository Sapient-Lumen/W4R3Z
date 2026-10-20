use std::collections::{BTreeSet, VecDeque};
use std::fs;
use std::future::Future;
use std::net::SocketAddr;
use std::path::{Path, PathBuf};
use std::pin::Pin;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use anonssh_bond::{
    FailureDomain, LaneConfig, LaneId, ProviderId, SchedulerConfig, SenderConfig, TrafficClass,
};
use anonssh_bond_tokio::{
    authenticate_client_lane, authenticate_server_lane, fresh_session_id, BondRuntimeConfig,
    BondRuntimeStats, BondSession, BondSessionControl, BondSessionKey, BondedStream, LaneJoin,
    LaneJoinRegistry, RuntimeLane, SessionRole,
};
use anyhow::{anyhow, bail, Context, Result};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use tokio::io::{AsyncRead, AsyncReadExt, AsyncWrite, AsyncWriteExt};
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::{mpsc, watch};
use zeroize::Zeroizing;

use crate::bond_transport::{i2p_lane_id, BondIngress, ClientBondSession};
use crate::identity::IdentityManager;
use crate::product_config::ScalingPolicy;
use crate::router_pool::{
    RouterPool, RouterProgressSnapshot, PRODUCTION_I2P_SLOTS, PRODUCTION_TOR_CANDIDATES,
    PRODUCTION_TOR_SLOTS,
};
use crate::runtime::{
    chmod, resolve_executable, I2pdManager, ReservedLoopbackEndpoint, TorManager,
};
use crate::sam::{SamConnector, SamListener};
use crate::tor_transport::{TorConnector, TorListener};

const PASSWORD: &str = "anonssh deterministic live bond test";
const MACHINE_ID: &str = "anonssh-live-bond";
const SERVICE_PORT: u16 = 22_424;
const TOR_HANDSHAKE_TIMEOUT: Duration = Duration::from_secs(30);
const I2P_HANDSHAKE_TIMEOUT: Duration = Duration::from_secs(180);
const I2P_LANE_ATTEMPTS: usize = 3;
const ROUTER_START_ATTEMPTS: usize = 2;
const TRANSFER_TIMEOUT: Duration = Duration::from_secs(900);
const SCALE_FORMATION_OPERATION_TIMEOUT: Duration = Duration::from_secs(930);
const POOL_CONVERGENCE_STABILITY: Duration = Duration::from_secs(3);
const PAYLOAD_BYTES: usize = 2 * 1024 * 1024;
const LIVE_REALTIME_SAMPLES: usize = 32;
const LIVE_REALTIME_INTERVAL: Duration = Duration::from_millis(100);
const SCALE_DEFAULT_TARGET_SLOTS_PER_PROVIDER: usize = 8;
const SCALE_MAX_TARGET_SLOTS_PER_PROVIDER: usize = 16;
const SCALE_CARDINALITIES: [usize; 5] = [1, 2, 4, 8, 16];
const SCALE_SMALL_PAYLOAD_BYTES: usize = 2 * 1024 * 1024;
const SCALE_LARGE_PAYLOAD_BYTES: usize = 8 * 1024 * 1024;
const SCALE_SUSTAINED_PAYLOAD_BYTES: usize = 8 * 1024 * 1024;
const SCALE_SCENARIOS_PER_CARDINALITY: usize = 3;
const SCALE_DEFAULT_ROUNDS_PER_TRIAL: usize = 2;
const SCALE_MAX_ROUNDS_PER_TRIAL: usize = 8;
const SCALE_EVIDENCE_MAX_CPU_MILLICORES: u32 = 32_000;
const SCALE_EVIDENCE_MAX_MEMORY_BYTES: u64 = 8 * 1024 * 1024 * 1024;
const SCALE_WARMUP_BYTES: usize = 1024 * 1024;
const SCALE_REALTIME_SAMPLES: usize = 8;
const SCALE_REALTIME_INTERVAL: Duration = Duration::from_millis(100);
const SCALE_PRESSURE_YIELD_BYTES: usize = 64 * 1024;
const SCALE_PRESSURE_INTERVAL: Duration = Duration::from_millis(500);
const SCALE_SCHEMA: &str = "anonssh.live-bond-scale.v7";
const SCALE_CHECKPOINT_ENV: &str = "ANONSSH_INTERNAL_SCALE_CHECKPOINT";
const SCALE_TARGET_ENV: &str = "ANONSSH_INTERNAL_SCALE_MAX_SLOTS_PER_PROVIDER";
const SCALE_ROUNDS_ENV: &str = "ANONSSH_INTERNAL_SCALE_ROUNDS_PER_TRIAL";
const SCALE_METHODOLOGY: &str = "ascending power-of-two mixed topologies from 1+1 through an explicit campaign ceiling (8+8 normally and 16+16 only in extended soak mode) over one campaign-local persistent router corpus; each cardinality receives a configured number of exact rounds of 2 MiB client-to-server, 8 MiB server-to-client, and simultaneous 8 MiB-per-direction bulk while fixed-cadence realtime requests begin under load independently of prior echo completion; router processes stop between trials while private state remains, and every observation labels fresh, partially retained, or retained state from the exact count of previously started slots; measured traffic begins after one idle production reprobe interval, so provider contribution is current traffic rather than formation residue; formation traffic is paced and goodput excludes separately reported router startup; short rounds require one typing request to begin during bulk while long and bidirectional rounds require four, and each retained latency includes the complete echo even when a slow response outlives the bulk transfer; eligibility is derived from each sender's runtime reservations rather than topology arithmetic; protected-pool contribution follows every reserved lane observed before, during, and after each round; retransmission, liveness, and control-replay totals cover formation, warmup, measurement, and repair while formation and measured-round subsets remain explicit; adjacent-cardinality ratios are descriptive, not universal capacity thresholds; extended mode does not alter production topology or resource defaults";
const ENDURANCE_SCHEMA: &str = "anonssh.live-bond-endurance.v3";
const ENDURANCE_STATE_SCHEMA: &str = "anonssh.live-bond-endurance-state.v1";
const ENDURANCE_HISTORY_SCHEMA: &str = "anonssh.live-bond-endurance-history.v3";
const ENDURANCE_V2_HISTORY_SCHEMA: &str = "anonssh.live-bond-endurance-history.v2";
const ENDURANCE_LEGACY_HISTORY_SCHEMA: &str = "anonssh.live-bond-endurance-history.v1";
const ENDURANCE_HISTORY_FILE: &str = "evidence-history.json";
const ENDURANCE_ROOT_ENV: &str = "ANONSSH_INTERNAL_ENDURANCE_ROOT";
const ENDURANCE_CHECKPOINT_ENV: &str = "ANONSSH_INTERNAL_ENDURANCE_CHECKPOINT";
const ENDURANCE_DURATION_ENV: &str = "ANONSSH_INTERNAL_ENDURANCE_DURATION_SECONDS";
const ENDURANCE_SLOTS_ENV: &str = "ANONSSH_INTERNAL_ENDURANCE_SLOTS_PER_PROVIDER";
const ENDURANCE_PAYLOAD_MIB_ENV: &str = "ANONSSH_INTERNAL_ENDURANCE_PAYLOAD_MIB";
const ENDURANCE_QUIET_ENV: &str = "ANONSSH_INTERNAL_ENDURANCE_QUIET_SECONDS";
const ENDURANCE_DISK_GIB_ENV: &str = "ANONSSH_INTERNAL_ENDURANCE_MAX_DISK_GIB";
const ENDURANCE_DEFAULT_DURATION_SECONDS: u64 = 24 * 60 * 60;
const ENDURANCE_MAX_DURATION_SECONDS: u64 = 31 * 24 * 60 * 60;
const ENDURANCE_DEFAULT_SLOTS_PER_PROVIDER: usize = 16;
const ENDURANCE_DEFAULT_PAYLOAD_MIB: u64 = 32;
const ENDURANCE_DEFAULT_QUIET_SECONDS: u64 = 120;
const ENDURANCE_DEFAULT_MAX_DISK_GIB: u64 = 2;
const ENDURANCE_MIN_PAYLOAD_MIB: u64 = 8;
const ENDURANCE_MAX_PAYLOAD_MIB: u64 = 128;
const ENDURANCE_MIN_QUIET_SECONDS: u64 = 60;
const ENDURANCE_MAX_QUIET_SECONDS: u64 = 600;
const ENDURANCE_MAX_DISK_GIB: u64 = 16;
const ENDURANCE_INITIAL_OBSERVATIONS: usize = 12;
const ENDURANCE_RECENT_OBSERVATIONS: usize = 128;
const ENDURANCE_BULK_REALTIME_INTERVAL: Duration = Duration::from_secs(5);
const ENDURANCE_QUIET_REALTIME_SAMPLES: usize = 8;
const ENDURANCE_METHODOLOGY: &str = "one stable campaign-owned mixed router corpus is retained across invocations while every invocation owns and cleans its processes, sockets, session, and lease; the real adaptive controller cycles sustained exact client-to-server, simultaneous bidirectional, and server-to-client bulk followed by a quiet realtime phase whose eight fixed-cadence samples are complete request/echo round trips over one persistent Realtime stream; legacy quiet one-way/lifecycle aggregates remain separate and are never relabeled as echo evidence; the cycle allows measured admission, periodic active-lane reprobe, marginal drain, and later retained-state restart; every phase records endpoint-local protocol deltas plus per-lane and per-provider acknowledged-byte contribution so bounded history remains independently interpretable after older observations are evicted; each completed phase atomically replaces one bounded checkpoint and persistent history containing cumulative aggregates, the first twelve observations, and the latest 128 observations across corpus generations; duration zero means signal-terminated operation while every phase, shutdown, and router operation remains bounded; crossing the configured persistent-state ceiling fails closed; public-overlay ratios remain descriptive";

#[derive(Clone, Copy, Debug, Deserialize, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "lowercase")]
enum Provider {
    Tor,
    I2p,
}

#[derive(Clone, Copy, Debug)]
struct PlannedLane {
    config: LaneConfig,
    provider: Provider,
    purpose: &'static str,
}

#[derive(Serialize)]
struct LiveBondReport {
    schema: &'static str,
    status: &'static str,
    pool: &'static str,
    payload_bytes: usize,
    payload_sha256: String,
    elapsed_millis: u128,
    authenticated_lanes: usize,
    bulk_providers_used: usize,
    bulk_failure_domains_used: usize,
    realtime: LiveRealtimeReport,
    unacknowledged_bytes: usize,
    lanes: Vec<LaneReport>,
}

#[derive(Serialize)]
struct LiveRealtimeReport {
    redundancy_enabled: bool,
    samples: usize,
    sample_interval_millis: u64,
    round_trip_micros_p50: u64,
    round_trip_micros_p95: u64,
    round_trip_micros_max: u64,
    client_protected_lanes: Vec<u32>,
    server_protected_lanes: Vec<u32>,
    protected_providers: usize,
    natural_winner_providers: usize,
    natural_tor_acknowledged_bytes: u64,
    natural_i2p_acknowledged_bytes: u64,
    forced_outage_provider: Option<Provider>,
    outage_probe_samples: usize,
    winner_providers: usize,
    tor_acknowledged_bytes: u64,
    i2p_acknowledged_bytes: u64,
    new_data_frames: u64,
    redundant_frames: u64,
    dropped_redundant_frames: u64,
    shadow_coverage_basis_points: u64,
}

#[derive(Serialize)]
struct LaneReport {
    id: u32,
    provider: Provider,
    router_failure_domain: u64,
    purpose: &'static str,
    reserved_for_low_latency: bool,
    bytes_scheduled: u64,
    bytes_acknowledged: u64,
}

struct TransferSummary {
    pool: &'static str,
    payload_bytes: usize,
    payload_sha256: String,
    elapsed: Duration,
    bulk_providers_used: usize,
    bulk_failure_domains_used: usize,
    realtime: LiveRealtimeReport,
}

struct Endpoints {
    sam: ReservedLoopbackEndpoint,
    server_tor_socks: ReservedLoopbackEndpoint,
    server_tor_control: ReservedLoopbackEndpoint,
    client_tor_socks: ReservedLoopbackEndpoint,
    client_tor_control: ReservedLoopbackEndpoint,
}

struct ProductPoolEndpoints {
    server_sam: [SocketAddr; PRODUCTION_I2P_SLOTS],
    server_tor_socks: [SocketAddr; PRODUCTION_TOR_CANDIDATES],
    server_tor_control: [SocketAddr; PRODUCTION_TOR_CANDIDATES],
    client_sam: [SocketAddr; PRODUCTION_I2P_SLOTS],
    client_tor_socks: [SocketAddr; PRODUCTION_TOR_CANDIDATES],
    client_tor_control: [SocketAddr; PRODUCTION_TOR_CANDIDATES],
    server_reservations: Vec<ReservedLoopbackEndpoint>,
    client_reservations: Vec<ReservedLoopbackEndpoint>,
}

struct ScaleEndpointSet {
    sam: Vec<SocketAddr>,
    tor_socks: Vec<SocketAddr>,
    tor_control: Vec<SocketAddr>,
    reservations: Vec<ReservedLoopbackEndpoint>,
}

struct ScalePoolEndpoints {
    server: ScaleEndpointSet,
    client: ScaleEndpointSet,
}

#[derive(Serialize)]
struct PoolRecoveryReport {
    schema: &'static str,
    status: &'static str,
    zero_lane_outage_observed: bool,
    zero_lane_transfer_bytes: usize,
    zero_lane_retransmitted_frames: u64,
    zero_lane_replayed_control_frames: u64,
    initial_lanes: usize,
    router_processes: usize,
    router_candidates_started: usize,
    lanes_used: usize,
    failed_i2p_slot: u32,
    i2p_degraded_transfer_bytes: usize,
    i2p_replacement_transfer_bytes: usize,
    i2p_state_roots_reused: bool,
    i2p_replacement_lane_bytes: u64,
    tor_degraded_transfer_bytes: usize,
    failed_tor_slot: u32,
    tor_replacement_lane_bytes: u64,
    tor_state_roots_reused: bool,
    all_lanes_active: bool,
    unacknowledged_bytes: usize,
    server_router_progress: RouterProgressSnapshot,
    client_router_progress: RouterProgressSnapshot,
}

#[derive(Serialize)]
struct ScaleCampaignReport {
    schema: &'static str,
    status: &'static str,
    methodology: &'static str,
    maximum_slots_per_provider: usize,
    rounds_per_trial: usize,
    observations: Vec<ScaleTrialReport>,
    comparisons: Vec<ScaleComparison>,
}

#[derive(Serialize)]
struct ScaleCampaignCheckpoint<'a> {
    schema: &'static str,
    status: &'static str,
    methodology: &'static str,
    completed_trials: usize,
    total_trials: usize,
    maximum_slots_per_provider: usize,
    rounds_per_trial: usize,
    current_trial: Option<ScaleCheckpointTrial>,
    observations: &'a [ScaleTrialReport],
    comparisons: Vec<ScaleComparison>,
    error: Option<&'a str>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct ScaleCampaignConfig {
    cardinalities: Vec<usize>,
    rounds_per_trial: usize,
}

impl ScaleCampaignConfig {
    fn from_environment() -> Result<Self> {
        Self::new(
            scale_environment_usize(SCALE_TARGET_ENV, SCALE_DEFAULT_TARGET_SLOTS_PER_PROVIDER)?,
            scale_environment_usize(SCALE_ROUNDS_ENV, SCALE_DEFAULT_ROUNDS_PER_TRIAL)?,
        )
    }

    fn new(maximum_slots_per_provider: usize, rounds_per_trial: usize) -> Result<Self> {
        if !SCALE_CARDINALITIES.contains(&maximum_slots_per_provider) {
            bail!(
                "scale target must be one of {:?}, received {maximum_slots_per_provider}",
                SCALE_CARDINALITIES
            );
        }
        if maximum_slots_per_provider > SCALE_MAX_TARGET_SLOTS_PER_PROVIDER {
            bail!("scale target exceeds the experimental ceiling");
        }
        if rounds_per_trial == 0 || rounds_per_trial > SCALE_MAX_ROUNDS_PER_TRIAL {
            bail!("scale rounds per trial must be between 1 and {SCALE_MAX_ROUNDS_PER_TRIAL}");
        }
        Ok(Self {
            cardinalities: SCALE_CARDINALITIES
                .into_iter()
                .take_while(|cardinality| *cardinality <= maximum_slots_per_provider)
                .collect(),
            rounds_per_trial,
        })
    }

    fn maximum_slots_per_provider(&self) -> usize {
        self.cardinalities
            .last()
            .copied()
            .expect("validated scale cardinalities are non-empty")
    }

    fn matrix(&self) -> Vec<ScaleScenario> {
        self.cardinalities
            .iter()
            .flat_map(|slots| {
                SCALE_WORKLOADS
                    .into_iter()
                    .map(|(payload, direction)| scale_scenario(*slots, payload, direction))
            })
            .collect()
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct EnduranceConfig {
    state_root: PathBuf,
    checkpoint_path: PathBuf,
    duration_seconds: u64,
    slots_per_provider: usize,
    payload_bytes: usize,
    quiet_seconds: u64,
    maximum_disk_bytes: u64,
}

#[derive(Clone, Serialize)]
struct EnduranceConfigReport {
    state_root: String,
    duration_seconds: u64,
    slots_per_provider: usize,
    maximum_active_lanes: usize,
    payload_bytes_per_direction: usize,
    quiet_seconds: u64,
    maximum_disk_bytes: u64,
    initial_observations_retained: usize,
    recent_observations_retained: usize,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
struct EnduranceStateMetadata {
    schema: String,
    created_unix_seconds: u64,
    generation: u64,
    slots_per_provider: usize,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "kebab-case")]
enum EndurancePhase {
    ClientToServer,
    Bidirectional,
    ServerToClient,
    QuietRealtime,
}

#[derive(Clone, Copy, Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
enum EnduranceEndpoint {
    Client,
    Server,
}

impl EndurancePhase {
    const CYCLE: [Self; 4] = [
        Self::ClientToServer,
        Self::Bidirectional,
        Self::ServerToClient,
        Self::QuietRealtime,
    ];

    const fn scale_direction(self) -> Option<ScaleDirection> {
        match self {
            Self::ClientToServer => Some(ScaleDirection::ClientToServer),
            Self::Bidirectional => Some(ScaleDirection::Bidirectional),
            Self::ServerToClient => Some(ScaleDirection::ServerToClient),
            Self::QuietRealtime => None,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "kebab-case")]
enum EnduranceStopReason {
    DurationElapsed,
    Signal,
}

#[derive(Clone, Serialize)]
struct EnduranceCurrentPhase {
    sequence: u64,
    phase: EndurancePhase,
    started_elapsed_millis: u64,
}

#[derive(Clone, Deserialize, Serialize)]
struct EnduranceLaneObservation {
    endpoint: EnduranceEndpoint,
    id: u32,
    provider: Provider,
    active: bool,
    delivery_measured: bool,
    reserved_for_low_latency: bool,
    smoothed_round_trip_micros: u64,
    delivery_rate_bps: u64,
    bytes_scheduled: u64,
    bytes_acknowledged: u64,
    #[serde(default)]
    phase_bytes_scheduled: u64,
    #[serde(default)]
    phase_bytes_acknowledged: u64,
}

#[derive(Clone, Default, Deserialize, Serialize)]
#[serde(default)]
struct EnduranceRuntimeDelta {
    new_data_frames: u64,
    redundant_realtime_frames: u64,
    dropped_redundant_realtime_frames: u64,
    retransmitted_frames: u64,
    ping_frames: u64,
    pong_frames: u64,
    liveness_failures: u64,
    acknowledgement_frames: u64,
    window_update_frames: u64,
    replayed_control_frames: u64,
    delivered_bytes: u64,
    stream_backpressure_events: u64,
    final_reorder_high_water: usize,
    final_unacknowledged_bytes: usize,
    final_active_streams: usize,
    final_retired_stream_tombstones: usize,
    final_maximum_lane_queue_delay_micros: u64,
}

#[derive(Clone, Default, Deserialize, Serialize)]
struct EnduranceRuntimeObservation {
    client: EnduranceRuntimeDelta,
    server: EnduranceRuntimeDelta,
}

#[derive(Clone, Default, Deserialize, Serialize)]
struct EnduranceContributionObservation {
    tor_acknowledged_bytes: u64,
    i2p_acknowledged_bytes: u64,
    contributing_tor_lanes: usize,
    contributing_i2p_lanes: usize,
    maximum_lane_acknowledged_bytes: u64,
    maximum_lane_share_basis_points: u64,
}

#[derive(Clone, Default, Deserialize, Serialize)]
struct EnduranceResourceObservation {
    running_router_processes: usize,
    router_cpu_time_micros: u64,
    router_resident_bytes: u64,
    maximum_router_startup_millis: u64,
    persistent_state_bytes: u64,
}

#[derive(Clone, Deserialize, Serialize)]
struct EnduranceObservation {
    sequence: u64,
    state_generation: u64,
    phase: EndurancePhase,
    run_elapsed_millis: u64,
    phase_elapsed_millis: u64,
    state_age_seconds: u64,
    client_active_lanes: usize,
    server_active_lanes: usize,
    desired_lane_ids: Vec<u32>,
    pending_pressure_lane_ids: Vec<u32>,
    adaptive_generation: u64,
    adaptive_events_retained: usize,
    bulk: Option<ScaleRoundReport>,
    quiet_realtime_round_trip_micros: Vec<u64>,
    quiet_realtime_round_trip_micros_p50: Option<u64>,
    quiet_realtime_round_trip_micros_p95: Option<u64>,
    quiet_realtime_round_trip_micros_max: Option<u64>,
    #[serde(default)]
    quiet_realtime_is_echo: bool,
    #[serde(default)]
    realtime_redundancy: bool,
    #[serde(default)]
    runtime: EnduranceRuntimeObservation,
    #[serde(default)]
    contribution: EnduranceContributionObservation,
    resources: EnduranceResourceObservation,
    lanes: Vec<EnduranceLaneObservation>,
}

#[derive(Clone, Default, Deserialize, Serialize)]
#[serde(default)]
struct EnduranceAggregate {
    observations: u64,
    payload_bytes: u64,
    elapsed_millis: u64,
    goodput_bps_sum: u64,
    goodput_bps_min: Option<u64>,
    goodput_bps_max: Option<u64>,
    realtime_p50_micros_sum: u64,
    realtime_p95_micros_sum: u64,
    realtime_p95_micros_max: Option<u64>,
    active_lanes_min: Option<usize>,
    active_lanes_max: Option<usize>,
    desired_lanes_min: Option<usize>,
    desired_lanes_max: Option<usize>,
    maximum_router_resident_bytes: u64,
    maximum_persistent_state_bytes: u64,
    redundant_realtime_frames: u64,
    dropped_redundant_realtime_frames: u64,
    retransmitted_frames: u64,
    liveness_failures: u64,
    stream_backpressure_events: u64,
    tor_acknowledged_bytes: u64,
    i2p_acknowledged_bytes: u64,
    contributing_lanes_min: Option<usize>,
    contributing_lanes_max: Option<usize>,
    maximum_lane_share_basis_points: u64,
}

#[derive(Clone, Default, Deserialize, Serialize)]
struct EnduranceAggregates {
    client_to_server: EnduranceAggregate,
    bidirectional: EnduranceAggregate,
    server_to_client: EnduranceAggregate,
    quiet_realtime: EnduranceAggregate,
    #[serde(default)]
    legacy_quiet_lifecycle: EnduranceAggregate,
}

#[derive(Clone, Default, Deserialize, Serialize)]
struct EnduranceHistory {
    completed_observations: u64,
    initial_observations: Vec<EnduranceObservation>,
    recent_observations: VecDeque<EnduranceObservation>,
    aggregates: EnduranceAggregates,
}

#[derive(Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct EnduranceHistoryFile {
    schema: String,
    slots_per_provider: usize,
    history: EnduranceHistory,
}

#[derive(Serialize)]
struct EnduranceCheckpoint<'a> {
    schema: &'static str,
    status: &'static str,
    methodology: &'static str,
    config: &'a EnduranceConfigReport,
    state: &'a EnduranceStateMetadata,
    started_unix_seconds: u64,
    elapsed_millis: u64,
    completed_observations: u64,
    current_phase: Option<&'a EnduranceCurrentPhase>,
    stop_reason: Option<EnduranceStopReason>,
    cleanup_complete: bool,
    initial_observations: &'a [EnduranceObservation],
    recent_observations: &'a VecDeque<EnduranceObservation>,
    aggregates: &'a EnduranceAggregates,
    error: Option<&'a str>,
}

#[derive(Serialize)]
struct EnduranceReport {
    schema: &'static str,
    status: &'static str,
    methodology: &'static str,
    config: EnduranceConfigReport,
    state: EnduranceStateMetadata,
    started_unix_seconds: u64,
    elapsed_millis: u64,
    completed_observations: u64,
    interrupted_phase: Option<EnduranceCurrentPhase>,
    stop_reason: EnduranceStopReason,
    cleanup_complete: bool,
    initial_observations: Vec<EnduranceObservation>,
    recent_observations: VecDeque<EnduranceObservation>,
    aggregates: EnduranceAggregates,
}

struct EnduranceLease {
    path: PathBuf,
    held: bool,
}

#[derive(Clone, Copy, Serialize)]
struct ScaleCheckpointTrial {
    sequence: usize,
    topology_slots_per_provider: usize,
    payload_bytes: usize,
    direction: ScaleDirection,
    router_state: ScaleRouterState,
}

#[derive(Serialize)]
struct ScaleTrialReport {
    sequence: usize,
    topology: String,
    direction: ScaleDirection,
    tor_routers_per_endpoint: usize,
    i2p_routers_per_endpoint: usize,
    warm_router_slots_per_provider: usize,
    router_state: ScaleRouterState,
    router_processes: usize,
    initial_activation_lanes: usize,
    formation_load_bytes: u64,
    authenticated_lanes: usize,
    eligible_bulk_lanes_per_sender: usize,
    eligible_bulk_paths: usize,
    bulk_isolated_from_protected_pool: bool,
    payload_bytes: usize,
    payload_bytes_per_round: usize,
    bulk_senders: usize,
    rounds: Vec<ScaleRoundReport>,
    median_goodput_bps: u64,
    goodput_per_eligible_path_bps: u64,
    realtime_round_trip_micros_p50: u64,
    realtime_round_trip_micros_p95: u64,
    realtime_round_trip_micros_max: u64,
    active_lanes: usize,
    repair_cycles: usize,
    inactive_endpoint_lane_observations: usize,
    lanes_with_acknowledged_bytes: usize,
    tor_acknowledged_bytes: u64,
    i2p_acknowledged_bytes: u64,
    final_reserved_lanes: Vec<u32>,
    protected_lanes_observed: Vec<u32>,
    protected_lane_acknowledged_bytes: u64,
    startup_elapsed_millis: u128,
    topology_formation_millis: u128,
    max_router_startup_millis: u64,
    router_cpu_time_micros: u64,
    router_resident_bytes: u64,
    disk_bytes: u64,
    max_queue_delay_micros: u64,
    formation_retransmitted_frames: u64,
    formation_liveness_failures: u64,
    formation_replayed_control_frames: u64,
    measured_retransmitted_frames: u64,
    measured_liveness_failures: u64,
    measured_replayed_control_frames: u64,
    retransmitted_frames: u64,
    liveness_failures: u64,
    replayed_control_frames: u64,
    unacknowledged_bytes: usize,
}

#[derive(Clone, Deserialize, Serialize)]
struct ScaleRoundReport {
    round: usize,
    direction: ScaleDirection,
    payload_bytes: usize,
    payload_bytes_per_direction: usize,
    client_to_server_sha256: Option<String>,
    server_to_client_sha256: Option<String>,
    elapsed_millis: u128,
    goodput_bps: u64,
    realtime_round_trip_micros: Vec<u64>,
    realtime_round_trip_micros_p50: u64,
    realtime_round_trip_micros_p95: u64,
    realtime_round_trip_micros_max: u64,
    bulk_start_overlap_samples: usize,
    protected_lanes_observed: Vec<u32>,
    protected_lane_acknowledged_bytes: u64,
    max_queue_delay_micros: u64,
    retransmitted_frames: u64,
    liveness_failures: u64,
    replayed_control_frames: u64,
}

#[derive(Default)]
struct ScaleRoundProgress {
    expected_bulk_streams: usize,
    bulk_payloads_written: AtomicUsize,
    bulk_writes_closed: AtomicUsize,
    bulk_eofs_received: AtomicUsize,
    bulk_reverse_closes: AtomicUsize,
    realtime_requests_started: AtomicUsize,
    realtime_echoes: AtomicUsize,
    realtime_request_closed: AtomicBool,
    realtime_request_eof: AtomicBool,
    realtime_response_closed: AtomicBool,
    realtime_response_eof: AtomicBool,
    telemetry_complete: AtomicBool,
    acknowledgement_drain_complete: AtomicBool,
}

impl ScaleRoundProgress {
    fn new(expected_bulk_streams: usize) -> Self {
        Self {
            expected_bulk_streams,
            bulk_payloads_written: AtomicUsize::new(0),
            bulk_writes_closed: AtomicUsize::new(0),
            bulk_eofs_received: AtomicUsize::new(0),
            bulk_reverse_closes: AtomicUsize::new(0),
            realtime_requests_started: AtomicUsize::new(0),
            realtime_echoes: AtomicUsize::new(0),
            realtime_request_closed: AtomicBool::new(false),
            realtime_request_eof: AtomicBool::new(false),
            realtime_response_closed: AtomicBool::new(false),
            realtime_response_eof: AtomicBool::new(false),
            telemetry_complete: AtomicBool::new(false),
            acknowledgement_drain_complete: AtomicBool::new(false),
        }
    }

    fn summary(&self) -> String {
        format!(
            "bulk_payloads_written={}/{}, bulk_writes_closed={}/{}, bulk_eofs_received={}/{}, bulk_reverse_closes={}/{}, realtime_requests_started={}/{}, realtime_echoes={}/{}, realtime_request_closed={}, realtime_request_eof={}, realtime_response_closed={}, realtime_response_eof={}, telemetry_complete={}, acknowledgement_drain_complete={}",
            self.bulk_payloads_written.load(Ordering::Acquire),
            self.expected_bulk_streams,
            self.bulk_writes_closed.load(Ordering::Acquire),
            self.expected_bulk_streams,
            self.bulk_eofs_received.load(Ordering::Acquire),
            self.expected_bulk_streams,
            self.bulk_reverse_closes.load(Ordering::Acquire),
            self.expected_bulk_streams,
            self.realtime_requests_started.load(Ordering::Acquire),
            SCALE_REALTIME_SAMPLES,
            self.realtime_echoes.load(Ordering::Acquire),
            SCALE_REALTIME_SAMPLES,
            self.realtime_request_closed.load(Ordering::Acquire),
            self.realtime_request_eof.load(Ordering::Acquire),
            self.realtime_response_closed.load(Ordering::Acquire),
            self.realtime_response_eof.load(Ordering::Acquire),
            self.telemetry_complete.load(Ordering::Acquire),
            self.acknowledgement_drain_complete.load(Ordering::Acquire),
        )
    }
}

#[derive(Serialize)]
struct ScaleComparison {
    scenario: String,
    direction: ScaleDirection,
    payload_bytes: usize,
    baseline_slots_per_provider: usize,
    scaled_slots_per_provider: usize,
    lane_ratio_basis_points: u64,
    eligible_bulk_path_ratio_basis_points: u64,
    goodput_ratio_basis_points: u64,
    ideal_linear_scaling_efficiency_basis_points: u64,
    realtime_p50_ratio_basis_points: u64,
    realtime_p95_ratio_basis_points: u64,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "kebab-case")]
enum ScaleDirection {
    ClientToServer,
    ServerToClient,
    Bidirectional,
}

impl ScaleDirection {
    const fn label(self) -> &'static str {
        match self {
            Self::ClientToServer => "client-to-server",
            Self::ServerToClient => "server-to-client",
            Self::Bidirectional => "bidirectional",
        }
    }

    const fn bulk_senders(self) -> usize {
        match self {
            Self::ClientToServer | Self::ServerToClient => 1,
            Self::Bidirectional => 2,
        }
    }

    const fn includes_client_to_server(self) -> bool {
        matches!(self, Self::ClientToServer | Self::Bidirectional)
    }

    const fn includes_server_to_client(self) -> bool {
        matches!(self, Self::ServerToClient | Self::Bidirectional)
    }
}

impl ScaleCheckpointTrial {
    const fn new(sequence: usize, scenario: ScaleScenario, router_state: ScaleRouterState) -> Self {
        Self {
            sequence,
            topology_slots_per_provider: scenario.slots_per_provider,
            payload_bytes: scenario.payload_bytes,
            direction: scenario.direction,
            router_state,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "kebab-case")]
enum ScaleRouterState {
    Fresh,
    PartiallyRetained,
    Retained,
}

impl ScaleRouterState {
    const fn classify(warm_slots_per_provider: usize, slots_per_provider: usize) -> Self {
        if warm_slots_per_provider == 0 {
            Self::Fresh
        } else if warm_slots_per_provider < slots_per_provider {
            Self::PartiallyRetained
        } else {
            Self::Retained
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize)]
struct ScaleScenario {
    slots_per_provider: usize,
    payload_bytes: usize,
    direction: ScaleDirection,
}

const fn scale_scenario(
    slots_per_provider: usize,
    payload_bytes: usize,
    direction: ScaleDirection,
) -> ScaleScenario {
    ScaleScenario {
        slots_per_provider,
        payload_bytes,
        direction,
    }
}

const SCALE_WORKLOADS: [(usize, ScaleDirection); SCALE_SCENARIOS_PER_CARDINALITY] = [
    (SCALE_SMALL_PAYLOAD_BYTES, ScaleDirection::ClientToServer),
    (SCALE_LARGE_PAYLOAD_BYTES, ScaleDirection::ServerToClient),
    (SCALE_SUSTAINED_PAYLOAD_BYTES, ScaleDirection::Bidirectional),
];

fn scale_environment_usize(name: &str, default: usize) -> Result<usize> {
    match std::env::var(name) {
        Ok(value) => value
            .parse::<usize>()
            .with_context(|| format!("{name} must be a positive integer")),
        Err(std::env::VarError::NotPresent) => Ok(default),
        Err(std::env::VarError::NotUnicode(_)) => bail!("{name} is not UTF-8"),
    }
}

fn expected_scale_lanes(slots_per_provider: usize) -> Result<usize> {
    slots_per_provider
        .checked_mul(2)
        .context("scale topology lane count overflow")
}

fn fixed_scale_policy(maximum_active_lanes: usize) -> ScalingPolicy {
    ScalingPolicy {
        maximum_active_lanes,
        maximum_admissions_per_interval: maximum_active_lanes,
        maximum_drains_per_interval: maximum_active_lanes,
        maximum_cpu_millicores: SCALE_EVIDENCE_MAX_CPU_MILLICORES,
        maximum_memory_bytes: SCALE_EVIDENCE_MAX_MEMORY_BYTES,
        ..ScalingPolicy::performance()
    }
}

impl EnduranceConfig {
    fn from_environment() -> Result<Self> {
        let state_root = std::env::var_os(ENDURANCE_ROOT_ENV)
            .map(PathBuf::from)
            .context("continuous endurance requires ANONSSH_INTERNAL_ENDURANCE_ROOT")?;
        let checkpoint_path = std::env::var_os(ENDURANCE_CHECKPOINT_ENV)
            .map(PathBuf::from)
            .context("continuous endurance requires ANONSSH_INTERNAL_ENDURANCE_CHECKPOINT")?;
        let duration_seconds =
            environment_u64(ENDURANCE_DURATION_ENV, ENDURANCE_DEFAULT_DURATION_SECONDS)?;
        let slots_per_provider = usize::try_from(environment_u64(
            ENDURANCE_SLOTS_ENV,
            ENDURANCE_DEFAULT_SLOTS_PER_PROVIDER as u64,
        )?)
        .context("endurance slot count does not fit usize")?;
        let payload_mib =
            environment_u64(ENDURANCE_PAYLOAD_MIB_ENV, ENDURANCE_DEFAULT_PAYLOAD_MIB)?;
        let quiet_seconds = environment_u64(ENDURANCE_QUIET_ENV, ENDURANCE_DEFAULT_QUIET_SECONDS)?;
        let maximum_disk_gib =
            environment_u64(ENDURANCE_DISK_GIB_ENV, ENDURANCE_DEFAULT_MAX_DISK_GIB)?;
        Self::new(
            state_root,
            checkpoint_path,
            duration_seconds,
            slots_per_provider,
            payload_mib,
            quiet_seconds,
            maximum_disk_gib,
        )
    }

    fn new(
        state_root: PathBuf,
        checkpoint_path: PathBuf,
        duration_seconds: u64,
        slots_per_provider: usize,
        payload_mib: u64,
        quiet_seconds: u64,
        maximum_disk_gib: u64,
    ) -> Result<Self> {
        if state_root.as_os_str().is_empty() || checkpoint_path.as_os_str().is_empty() {
            bail!("endurance state and checkpoint paths must be nonempty");
        }
        if state_root == checkpoint_path {
            bail!("endurance state root and checkpoint path must differ");
        }
        if duration_seconds > ENDURANCE_MAX_DURATION_SECONDS {
            bail!(
                "endurance duration must be zero or at most {ENDURANCE_MAX_DURATION_SECONDS} seconds"
            );
        }
        if !matches!(slots_per_provider, 8 | 16) {
            bail!("endurance topology must use 8 or 16 slots per provider");
        }
        if !(ENDURANCE_MIN_PAYLOAD_MIB..=ENDURANCE_MAX_PAYLOAD_MIB).contains(&payload_mib) {
            bail!(
                "endurance payload must be between {ENDURANCE_MIN_PAYLOAD_MIB} and {ENDURANCE_MAX_PAYLOAD_MIB} MiB"
            );
        }
        if !(ENDURANCE_MIN_QUIET_SECONDS..=ENDURANCE_MAX_QUIET_SECONDS).contains(&quiet_seconds) {
            bail!(
                "endurance quiet phase must be between {ENDURANCE_MIN_QUIET_SECONDS} and {ENDURANCE_MAX_QUIET_SECONDS} seconds"
            );
        }
        if maximum_disk_gib == 0 || maximum_disk_gib > ENDURANCE_MAX_DISK_GIB {
            bail!("endurance disk ceiling must be between 1 and {ENDURANCE_MAX_DISK_GIB} GiB");
        }
        let payload_bytes = usize::try_from(
            payload_mib
                .checked_mul(1024 * 1024)
                .context("endurance payload size overflow")?,
        )
        .context("endurance payload size does not fit usize")?;
        let maximum_disk_bytes = maximum_disk_gib
            .checked_mul(1024 * 1024 * 1024)
            .context("endurance disk ceiling overflow")?;
        Ok(Self {
            state_root,
            checkpoint_path,
            duration_seconds,
            slots_per_provider,
            payload_bytes,
            quiet_seconds,
            maximum_disk_bytes,
        })
    }

    fn report(&self) -> Result<EnduranceConfigReport> {
        Ok(EnduranceConfigReport {
            state_root: self.state_root.display().to_string(),
            duration_seconds: self.duration_seconds,
            slots_per_provider: self.slots_per_provider,
            maximum_active_lanes: expected_scale_lanes(self.slots_per_provider)?,
            payload_bytes_per_direction: self.payload_bytes,
            quiet_seconds: self.quiet_seconds,
            maximum_disk_bytes: self.maximum_disk_bytes,
            initial_observations_retained: ENDURANCE_INITIAL_OBSERVATIONS,
            recent_observations_retained: ENDURANCE_RECENT_OBSERVATIONS,
        })
    }
}

fn environment_u64(name: &str, default: u64) -> Result<u64> {
    match std::env::var(name) {
        Ok(value) => value
            .parse::<u64>()
            .with_context(|| format!("{name} must be a non-negative integer")),
        Err(std::env::VarError::NotPresent) => Ok(default),
        Err(std::env::VarError::NotUnicode(_)) => bail!("{name} is not UTF-8"),
    }
}

fn endurance_scaling_policy(maximum_active_lanes: usize) -> ScalingPolicy {
    ScalingPolicy {
        maximum_active_lanes,
        maximum_admissions_per_interval: 4.min(maximum_active_lanes),
        maximum_drains_per_interval: 4.min(maximum_active_lanes),
        maximum_cpu_millicores: SCALE_EVIDENCE_MAX_CPU_MILLICORES,
        maximum_memory_bytes: SCALE_EVIDENCE_MAX_MEMORY_BYTES,
        ..ScalingPolicy::performance()
    }
}

impl EnduranceAggregate {
    fn observe(&mut self, observation: &EnduranceObservation) {
        self.observations = self.observations.saturating_add(1);
        let (payload_bytes, elapsed_millis, goodput_bps, realtime_p50, realtime_p95) =
            match &observation.bulk {
                Some(bulk) => (
                    u64::try_from(bulk.payload_bytes).unwrap_or(u64::MAX),
                    u64::try_from(bulk.elapsed_millis).unwrap_or(u64::MAX),
                    bulk.goodput_bps,
                    bulk.realtime_round_trip_micros_p50,
                    bulk.realtime_round_trip_micros_p95,
                ),
                None => (
                    0,
                    observation.phase_elapsed_millis,
                    0,
                    observation
                        .quiet_realtime_round_trip_micros_p50
                        .unwrap_or(0),
                    observation
                        .quiet_realtime_round_trip_micros_p95
                        .unwrap_or(0),
                ),
            };
        self.payload_bytes = self.payload_bytes.saturating_add(payload_bytes);
        self.elapsed_millis = self.elapsed_millis.saturating_add(elapsed_millis);
        self.goodput_bps_sum = self.goodput_bps_sum.saturating_add(goodput_bps);
        if goodput_bps > 0 {
            update_min(&mut self.goodput_bps_min, goodput_bps);
            update_max(&mut self.goodput_bps_max, goodput_bps);
        }
        self.realtime_p50_micros_sum = self.realtime_p50_micros_sum.saturating_add(realtime_p50);
        self.realtime_p95_micros_sum = self.realtime_p95_micros_sum.saturating_add(realtime_p95);
        update_max(&mut self.realtime_p95_micros_max, realtime_p95);
        let active_lanes = observation
            .client_active_lanes
            .min(observation.server_active_lanes);
        update_min(&mut self.active_lanes_min, active_lanes);
        update_max(&mut self.active_lanes_max, active_lanes);
        update_min(
            &mut self.desired_lanes_min,
            observation.desired_lane_ids.len(),
        );
        update_max(
            &mut self.desired_lanes_max,
            observation.desired_lane_ids.len(),
        );
        self.maximum_router_resident_bytes = self
            .maximum_router_resident_bytes
            .max(observation.resources.router_resident_bytes);
        self.maximum_persistent_state_bytes = self
            .maximum_persistent_state_bytes
            .max(observation.resources.persistent_state_bytes);
        for runtime in [&observation.runtime.client, &observation.runtime.server] {
            self.redundant_realtime_frames = self
                .redundant_realtime_frames
                .saturating_add(runtime.redundant_realtime_frames);
            self.dropped_redundant_realtime_frames = self
                .dropped_redundant_realtime_frames
                .saturating_add(runtime.dropped_redundant_realtime_frames);
            self.retransmitted_frames = self
                .retransmitted_frames
                .saturating_add(runtime.retransmitted_frames);
            self.liveness_failures = self
                .liveness_failures
                .saturating_add(runtime.liveness_failures);
            self.stream_backpressure_events = self
                .stream_backpressure_events
                .saturating_add(runtime.stream_backpressure_events);
        }
        self.tor_acknowledged_bytes = self
            .tor_acknowledged_bytes
            .saturating_add(observation.contribution.tor_acknowledged_bytes);
        self.i2p_acknowledged_bytes = self
            .i2p_acknowledged_bytes
            .saturating_add(observation.contribution.i2p_acknowledged_bytes);
        let contributing_lanes = observation
            .contribution
            .contributing_tor_lanes
            .saturating_add(observation.contribution.contributing_i2p_lanes);
        update_min(&mut self.contributing_lanes_min, contributing_lanes);
        update_max(&mut self.contributing_lanes_max, contributing_lanes);
        self.maximum_lane_share_basis_points = self
            .maximum_lane_share_basis_points
            .max(observation.contribution.maximum_lane_share_basis_points);
    }
}

impl EnduranceHistory {
    fn observe(&mut self, observation: EnduranceObservation) {
        self.completed_observations = self.completed_observations.saturating_add(1);
        if self.initial_observations.len() < ENDURANCE_INITIAL_OBSERVATIONS {
            self.initial_observations.push(observation.clone());
        }
        if self.recent_observations.len() == ENDURANCE_RECENT_OBSERVATIONS {
            self.recent_observations.pop_front();
        }
        match observation.phase {
            EndurancePhase::ClientToServer => {
                self.aggregates.client_to_server.observe(&observation)
            }
            EndurancePhase::Bidirectional => self.aggregates.bidirectional.observe(&observation),
            EndurancePhase::ServerToClient => {
                self.aggregates.server_to_client.observe(&observation)
            }
            EndurancePhase::QuietRealtime => self.aggregates.quiet_realtime.observe(&observation),
        }
        self.recent_observations.push_back(observation);
    }

    fn validate(&self, state_generation: u64) -> Result<()> {
        if self.initial_observations.len() > ENDURANCE_INITIAL_OBSERVATIONS
            || self.recent_observations.len() > ENDURANCE_RECENT_OBSERVATIONS
        {
            bail!("endurance evidence history exceeds its retention bound");
        }
        if self.completed_observations
            < u64::try_from(
                self.initial_observations
                    .len()
                    .max(self.recent_observations.len()),
            )
            .unwrap_or(u64::MAX)
        {
            bail!("endurance evidence history has an invalid completed count");
        }
        let aggregate_observations = self
            .aggregates
            .client_to_server
            .observations
            .saturating_add(self.aggregates.bidirectional.observations)
            .saturating_add(self.aggregates.server_to_client.observations)
            .saturating_add(self.aggregates.quiet_realtime.observations)
            .saturating_add(self.aggregates.legacy_quiet_lifecycle.observations);
        if aggregate_observations != self.completed_observations {
            bail!("endurance evidence aggregates do not match the completed count");
        }
        if self.completed_observations == 0 {
            if !self.initial_observations.is_empty() || !self.recent_observations.is_empty() {
                bail!("empty endurance evidence history retains observations");
            }
            return Ok(());
        }
        if self.initial_observations.first().map(|item| item.sequence) != Some(1)
            || self.recent_observations.back().map(|item| item.sequence)
                != Some(self.completed_observations)
        {
            bail!("endurance evidence history has an invalid sequence boundary");
        }
        if self
            .initial_observations
            .iter()
            .enumerate()
            .any(|(index, item)| item.sequence != index as u64 + 1)
        {
            bail!("endurance evidence history has an invalid initial sequence");
        }
        let recent_start = self
            .completed_observations
            .saturating_sub(self.recent_observations.len() as u64)
            .saturating_add(1);
        if self
            .recent_observations
            .iter()
            .enumerate()
            .any(|(index, item)| item.sequence != recent_start.saturating_add(index as u64))
        {
            bail!("endurance evidence history has an invalid recent sequence");
        }
        if self
            .initial_observations
            .iter()
            .chain(&self.recent_observations)
            .any(|item| item.state_generation == 0 || item.state_generation > state_generation)
        {
            bail!("endurance evidence history has invalid state generation");
        }
        Ok(())
    }
}

fn load_endurance_history(
    config: &EnduranceConfig,
    state: &EnduranceStateMetadata,
) -> Result<EnduranceHistory> {
    let path = config.state_root.join(ENDURANCE_HISTORY_FILE);
    let bytes = match fs::read(&path) {
        Ok(bytes) => bytes,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            return Ok(EnduranceHistory::default())
        }
        Err(error) => return Err(error).context("failed to read endurance evidence history"),
    };
    if bytes.len() > 16 * 1024 * 1024 {
        bail!("endurance evidence history exceeds 16 MiB");
    }
    let mut history_file: EnduranceHistoryFile =
        serde_json::from_slice(&bytes).context("endurance evidence history is malformed")?;
    if history_file.schema != ENDURANCE_HISTORY_SCHEMA
        && history_file.schema != ENDURANCE_V2_HISTORY_SCHEMA
        && history_file.schema != ENDURANCE_LEGACY_HISTORY_SCHEMA
    {
        bail!("unsupported endurance evidence history schema");
    }
    if history_file.slots_per_provider != config.slots_per_provider {
        bail!("endurance evidence history topology does not match its router corpus");
    }
    if history_file.schema != ENDURANCE_HISTORY_SCHEMA {
        if history_file
            .history
            .aggregates
            .legacy_quiet_lifecycle
            .observations
            != 0
        {
            bail!("legacy endurance history already contains migrated quiet evidence");
        }
        history_file.history.aggregates.legacy_quiet_lifecycle =
            std::mem::take(&mut history_file.history.aggregates.quiet_realtime);
    }
    history_file.history.validate(state.generation)?;
    Ok(history_file.history)
}

fn write_endurance_history(
    config: &EnduranceConfig,
    state_generation: u64,
    history: &EnduranceHistory,
) -> Result<()> {
    history.validate(state_generation)?;
    write_json_atomically(
        &config.state_root.join(ENDURANCE_HISTORY_FILE),
        &EnduranceHistoryFile {
            schema: ENDURANCE_HISTORY_SCHEMA.to_owned(),
            slots_per_provider: config.slots_per_provider,
            history: history.clone(),
        },
    )
}

fn update_min<T: Copy + Ord>(current: &mut Option<T>, value: T) {
    *current = Some(current.map_or(value, |existing| existing.min(value)));
}

fn update_max<T: Copy + Ord>(current: &mut Option<T>, value: T) {
    *current = Some(current.map_or(value, |existing| existing.max(value)));
}

fn current_unix_seconds() -> Result<u64> {
    Ok(SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .context("system clock precedes the Unix epoch")?
        .as_secs())
}

fn duration_millis(duration: Duration) -> u64 {
    u64::try_from(duration.as_millis()).unwrap_or(u64::MAX)
}

fn prepare_endurance_state(config: &EnduranceConfig) -> Result<EnduranceStateMetadata> {
    fs::create_dir_all(&config.state_root).with_context(|| {
        format!(
            "failed to create endurance state root {}",
            config.state_root.display()
        )
    })?;
    let metadata = fs::symlink_metadata(&config.state_root)?;
    if !metadata.file_type().is_dir() || metadata.file_type().is_symlink() {
        bail!("endurance state root must be a real directory");
    }
    chmod(&config.state_root, 0o700)?;
    let path = config.state_root.join("state-metadata.json");
    let mut state = match fs::read(&path) {
        Ok(bytes) => {
            if bytes.len() > 64 * 1024 {
                bail!("endurance state metadata exceeds 64 KiB");
            }
            serde_json::from_slice::<EnduranceStateMetadata>(&bytes)
                .context("endurance state metadata is malformed")?
        }
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => EnduranceStateMetadata {
            schema: ENDURANCE_STATE_SCHEMA.to_owned(),
            created_unix_seconds: current_unix_seconds()?,
            generation: 0,
            slots_per_provider: config.slots_per_provider,
        },
        Err(error) => return Err(error).context("failed to read endurance state metadata"),
    };
    if state.schema != ENDURANCE_STATE_SCHEMA {
        bail!("unsupported endurance state metadata schema");
    }
    if state.slots_per_provider != config.slots_per_provider {
        bail!(
            "endurance state was created for {}+{} but this run requested {}+{}",
            state.slots_per_provider,
            state.slots_per_provider,
            config.slots_per_provider,
            config.slots_per_provider,
        );
    }
    state.generation = state
        .generation
        .checked_add(1)
        .context("endurance state generation overflow")?;
    write_json_atomically(&path, &state)?;
    Ok(state)
}

impl EnduranceLease {
    fn acquire(state_root: &Path) -> Result<Self> {
        let path = state_root.join("campaign.lease");
        for _ in 0..2 {
            match fs::create_dir(&path) {
                Ok(()) => {
                    chmod(&path, 0o700)?;
                    fs::write(path.join("pid"), format!("{}\n", std::process::id()))?;
                    return Ok(Self { path, held: true });
                }
                Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {
                    let metadata = fs::symlink_metadata(&path)
                        .context("failed to inspect existing endurance campaign lease")?;
                    if !metadata.file_type().is_dir() || metadata.file_type().is_symlink() {
                        bail!("endurance campaign lease is not a real directory");
                    }
                    let process_id = fs::read_to_string(path.join("pid"))
                        .ok()
                        .and_then(|value| value.trim().parse::<u32>().ok());
                    if process_id.is_some_and(process_is_alive) {
                        bail!("another endurance campaign owns the persistent state");
                    }
                    fs::remove_dir_all(&path)
                        .context("failed to reclaim stale endurance campaign lease")?;
                }
                Err(error) => {
                    return Err(error).context("failed to acquire endurance campaign lease")
                }
            }
        }
        bail!("failed to acquire endurance campaign lease after stale-state recovery")
    }

    fn release(mut self) -> Result<()> {
        fs::remove_dir_all(&self.path).context("failed to release endurance campaign lease")?;
        self.held = false;
        Ok(())
    }
}

impl Drop for EnduranceLease {
    fn drop(&mut self) {
        if self.held {
            let _ = fs::remove_dir_all(&self.path);
        }
    }
}

fn process_is_alive(process_id: u32) -> bool {
    let Ok(process_id) = i32::try_from(process_id) else {
        return false;
    };
    let result = unsafe { libc::kill(process_id, 0) };
    result == 0 || std::io::Error::last_os_error().raw_os_error() == Some(libc::EPERM)
}

fn write_json_atomically(path: &Path, value: &impl Serialize) -> Result<()> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)
            .with_context(|| format!("failed to create {}", parent.display()))?;
    }
    let temporary = path.with_extension("tmp");
    let bytes = serde_json::to_vec_pretty(value)?;
    fs::write(&temporary, bytes)
        .with_context(|| format!("failed to write {}", temporary.display()))?;
    fs::rename(&temporary, path)
        .with_context(|| format!("failed to atomically replace {}", path.display()))
}

#[derive(Clone, Copy)]
enum RequiredDiversity {
    Providers,
    FailureDomains,
}

pub async fn run() -> Result<()> {
    let root = live_root("mixed");
    remove_if_present(&root)?;
    let endpoints = allocate_endpoints()?;
    let i2pd_binary = resolve_executable("ANONSSH_I2PD_BIN", "i2pd")?;
    let tor_binary = resolve_executable("ANONSSH_TOR_BIN", "tor")?;
    let sam_addr = endpoints.sam.address()?;
    let i2pd = I2pdManager::new_reserved(root.join("i2pd"), i2pd_binary, endpoints.sam)?;
    let server_tor = TorManager::new_reserved(
        root.join("server-tor"),
        tor_binary.clone(),
        endpoints.server_tor_socks,
        endpoints.server_tor_control,
    )?;
    let client_tor = TorManager::new_reserved(
        root.join("client-tor"),
        tor_binary,
        endpoints.client_tor_socks,
        endpoints.client_tor_control,
    )?;

    let operation = run_with_routers(&i2pd, &server_tor, &client_tor, sam_addr).await;
    let cleanup = stop_routers(&i2pd, &server_tor, &client_tor)
        .await
        .and_then(|()| remove_if_present(&root));
    let report = merge_result(operation, cleanup)?;
    println!("{}", serde_json::to_string_pretty(&report)?);
    Ok(())
}

pub async fn run_i2p_pool() -> Result<()> {
    let root = live_root("i2p-pool");
    remove_if_present(&root)?;
    let [first_endpoint, second_endpoint] = allocate_loopback_endpoints(2)?
        .try_into()
        .map_err(|_| anyhow!("I2P pool endpoint allocation returned the wrong count"))?;
    let first_addr = first_endpoint.address()?;
    let second_addr = second_endpoint.address()?;
    let i2pd_binary = resolve_executable("ANONSSH_I2PD_BIN", "i2pd")?;
    let first =
        I2pdManager::new_reserved(root.join("router-1"), i2pd_binary.clone(), first_endpoint)?;
    let second = I2pdManager::new_reserved(root.join("router-2"), i2pd_binary, second_endpoint)?;

    let operation = run_with_i2p_pool(&first, &second, first_addr, second_addr).await;
    let (first_cleanup, second_cleanup) = tokio::join!(first.stop(), second.stop());
    let cleanup =
        merge_result(first_cleanup, second_cleanup).and_then(|()| remove_if_present(&root));
    let report = merge_result(operation, cleanup)?;
    println!("{}", serde_json::to_string_pretty(&report)?);
    Ok(())
}

pub async fn run_pool_recovery() -> Result<()> {
    let root = live_root("pool-recovery");
    remove_if_present(&root)?;
    let endpoints = allocate_product_pool_endpoints()?;
    let i2pd_binary = resolve_executable("ANONSSH_I2PD_BIN", "i2pd")?;
    let tor_binary = resolve_executable("ANONSSH_TOR_BIN", "tor")?;
    let server_pool = product_router_pool(
        &root.join("server"),
        tor_binary.clone(),
        i2pd_binary.clone(),
        endpoints.server_tor_socks,
        endpoints.server_tor_control,
        endpoints.server_sam,
        endpoints.server_reservations,
    )?;
    let client_pool = product_router_pool(
        &root.join("client"),
        tor_binary,
        i2pd_binary,
        endpoints.client_tor_socks,
        endpoints.client_tor_control,
        endpoints.client_sam,
        endpoints.client_reservations,
    )?;

    let operation = run_with_pool_recovery(&server_pool, &client_pool).await;
    let server_failure_progress = server_pool.progress_snapshot();
    let client_failure_progress = client_pool.progress_snapshot();
    let (server_cleanup, client_cleanup) = tokio::join!(server_pool.stop(), client_pool.stop());
    let cleanup =
        merge_result(server_cleanup, client_cleanup).and_then(|()| remove_if_present(&root));
    match merge_result(operation, cleanup) {
        Ok(report) => {
            println!("{}", serde_json::to_string_pretty(&report)?);
            Ok(())
        }
        Err(error) => {
            println!(
                "{}",
                serde_json::to_string_pretty(&serde_json::json!({
                    "schema": "anonssh.live-pool-recovery.v6",
                    "status": "error",
                    "error": format!("{error:#}"),
                    "server_router_progress": server_failure_progress,
                    "client_router_progress": client_failure_progress,
                }))?
            );
            Err(error)
        }
    }
}

pub async fn run_scale() -> Result<()> {
    match run_scale_campaign().await {
        Ok(report) => {
            println!("{}", serde_json::to_string_pretty(&report)?);
            Ok(())
        }
        Err(error) => {
            println!(
                "{}",
                serde_json::to_string_pretty(&live_error_report(SCALE_SCHEMA, &error))?
            );
            Err(error)
        }
    }
}

pub async fn run_endurance() -> Result<()> {
    match run_endurance_campaign().await {
        Ok(report) => {
            println!("{}", serde_json::to_string_pretty(&report)?);
            Ok(())
        }
        Err(error) => {
            println!(
                "{}",
                serde_json::to_string_pretty(&live_error_report(ENDURANCE_SCHEMA, &error))?
            );
            Err(error)
        }
    }
}

async fn run_endurance_campaign() -> Result<EnduranceReport> {
    let config = EnduranceConfig::from_environment()?;
    fs::create_dir_all(&config.state_root)?;
    chmod(&config.state_root, 0o700)?;
    let lease = EnduranceLease::acquire(&config.state_root)?;
    let state = prepare_endurance_state(&config)?;
    let config_report = config.report()?;
    let started_unix_seconds = current_unix_seconds()?;
    let started = Instant::now();
    let mut history = load_endurance_history(&config, &state)?;
    write_endurance_history(&config, state.generation, &history)?;
    let mut current_phase = None;
    write_endurance_checkpoint(
        &config.checkpoint_path,
        "starting",
        &config_report,
        &state,
        started_unix_seconds,
        started.elapsed(),
        &history,
        current_phase.as_ref(),
        None,
        false,
        None,
    )?;
    let initial_disk_bytes = directory_size(&config.state_root)?;
    if initial_disk_bytes > config.maximum_disk_bytes {
        bail!(
            "endurance state already uses {initial_disk_bytes} bytes, above its {} byte ceiling",
            config.maximum_disk_bytes
        );
    }

    let i2pd_binary = resolve_executable("ANONSSH_I2PD_BIN", "i2pd")?;
    let tor_binary = resolve_executable("ANONSSH_TOR_BIN", "tor")?;
    let endpoints = allocate_scale_pool_endpoints(config.slots_per_provider)?;
    let server_pool = scale_router_pool(
        &config.state_root.join("server"),
        tor_binary.clone(),
        i2pd_binary.clone(),
        endpoints.server,
    )?;
    let client_pool = scale_router_pool(
        &config.state_root.join("client"),
        tor_binary,
        i2pd_binary,
        endpoints.client,
    )?;

    let (observations, interrupted, operation) = run_endurance_with_pools(
        &server_pool,
        &client_pool,
        &config,
        &config_report,
        &state,
        started_unix_seconds,
        started,
        history,
        current_phase,
    )
    .await;
    history = observations;
    current_phase = interrupted;

    let (server_stop, client_stop) = tokio::join!(server_pool.stop(), client_pool.stop());
    let cleanup = merge_result(server_stop, client_stop);
    let remaining_processes = count_running_router_processes(&server_pool, &client_pool).await?;
    let final_disk_bytes = directory_size(&config.state_root)?;
    let cleanup = cleanup.and_then(|()| {
        if remaining_processes != 0 {
            bail!("endurance cleanup left {remaining_processes} owned router processes");
        }
        if final_disk_bytes > config.maximum_disk_bytes {
            bail!(
                "endurance state grew to {final_disk_bytes} bytes, above its {} byte ceiling",
                config.maximum_disk_bytes
            );
        }
        Ok(())
    });
    drop(server_pool);
    drop(client_pool);
    let cleanup = cleanup.and_then(|()| lease.release());
    let cleanup_complete = cleanup.is_ok();
    let operation = merge_result(operation, cleanup);
    match operation {
        Ok(stop_reason) => {
            let report = EnduranceReport {
                schema: ENDURANCE_SCHEMA,
                status: "ok",
                methodology: ENDURANCE_METHODOLOGY,
                config: config_report.clone(),
                state: state.clone(),
                started_unix_seconds,
                elapsed_millis: duration_millis(started.elapsed()),
                completed_observations: history.completed_observations,
                interrupted_phase: current_phase.clone(),
                stop_reason,
                cleanup_complete: true,
                initial_observations: history.initial_observations.clone(),
                recent_observations: history.recent_observations.clone(),
                aggregates: history.aggregates.clone(),
            };
            write_endurance_checkpoint(
                &config.checkpoint_path,
                "ok",
                &config_report,
                &state,
                started_unix_seconds,
                started.elapsed(),
                &history,
                current_phase.as_ref(),
                Some(stop_reason),
                true,
                None,
            )?;
            Ok(report)
        }
        Err(error) => {
            let message = format!("{error:#}");
            write_endurance_checkpoint(
                &config.checkpoint_path,
                "error",
                &config_report,
                &state,
                started_unix_seconds,
                started.elapsed(),
                &history,
                current_phase.as_ref(),
                None,
                cleanup_complete,
                Some(&message),
            )?;
            Err(error)
        }
    }
}

#[allow(clippy::too_many_arguments)]
async fn run_endurance_with_pools(
    server_pool: &RouterPool,
    client_pool: &RouterPool,
    config: &EnduranceConfig,
    config_report: &EnduranceConfigReport,
    state: &EnduranceStateMetadata,
    started_unix_seconds: u64,
    started: Instant,
    mut history: EnduranceHistory,
    mut current_phase: Option<EnduranceCurrentPhase>,
) -> (
    EnduranceHistory,
    Option<EnduranceCurrentPhase>,
    Result<EnduranceStopReason>,
) {
    let operation = async {
        let client_socks = vec![client_pool
            .ensure_tor_slot(1)
            .await
            .context("failed to start endurance client discovery router")?];
        let slot_count =
            u32::try_from(config.slots_per_provider).context("endurance slot count overflow")?;
        let machine_id = format!("{MACHINE_ID}-endurance-{}", config.slots_per_provider);
        let password = Zeroizing::new(PASSWORD.to_owned());
        let server_identity = IdentityManager::derive_server_recovery_identity_with_pool_slots(
            &password,
            &machine_id,
            slot_count,
            slot_count,
        )?;
        let client_identity = IdentityManager::derive_client_recovery_identity_with_pool_slots(
            &password,
            &machine_id,
            slot_count,
            slot_count,
        )?;
        drop(password);
        let policy = endurance_scaling_policy(expected_scale_lanes(config.slots_per_provider)?);
        let ingress =
            BondIngress::publish_with_scaling_policy(server_pool, &server_identity, policy).await?;
        let tor_destinations = server_identity
            .tor_pool
            .iter()
            .map(|identity| identity.destination.clone())
            .collect::<Vec<_>>();
        let i2p_destinations = server_identity
            .i2p_pool
            .iter()
            .map(|identity| identity.destination.clone())
            .collect::<Vec<_>>();
        let accept = ingress.accept_session();
        let connect = ClientBondSession::connect_with_scaling_policy(
            client_pool,
            &client_socks,
            &tor_destinations,
            &i2p_destinations,
            *client_identity.bond_session_key,
            policy,
        );
        let (server, client) = tokio::try_join!(accept, connect)?;
        let session_id = server.session_id();
        let payload = deterministic_scale_payload(config.payload_bytes);
        let supervised = with_pool_supervision(
            &ingress,
            &server,
            client_pool,
            &client,
            PoolSupervisionMode::Adaptive,
            run_endurance_loop(
                server_pool,
                client_pool,
                &server,
                &client,
                config,
                config_report,
                state,
                started_unix_seconds,
                started,
                &payload,
                &mut history,
                &mut current_phase,
            ),
        )
        .await;
        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), async {
            server.shutdown().await.map_err(anyhow::Error::from)
        },);
        let shutdown = merge_result(client_shutdown, server_shutdown);
        let release = ingress.release_session(session_id).await;
        merge_result(merge_result(supervised, shutdown), release)
    }
    .await;
    (history, current_phase, operation)
}

#[allow(clippy::too_many_arguments)]
async fn run_endurance_loop(
    server_pool: &RouterPool,
    client_pool: &RouterPool,
    server: &BondSession,
    client: &ClientBondSession,
    config: &EnduranceConfig,
    config_report: &EnduranceConfigReport,
    state: &EnduranceStateMetadata,
    started_unix_seconds: u64,
    started: Instant,
    payload: &[u8],
    history: &mut EnduranceHistory,
    current_phase: &mut Option<EnduranceCurrentPhase>,
) -> Result<EnduranceStopReason> {
    let stop = wait_for_endurance_stop(config.duration_seconds);
    tokio::pin!(stop);
    let mut sequence = history
        .completed_observations
        .checked_add(1)
        .context("endurance sequence overflow")?;
    loop {
        let phase_index = usize::try_from((sequence - 1) % EndurancePhase::CYCLE.len() as u64)
            .context("endurance phase index overflow")?;
        let phase = EndurancePhase::CYCLE[phase_index];
        *current_phase = Some(EnduranceCurrentPhase {
            sequence,
            phase,
            started_elapsed_millis: duration_millis(started.elapsed()),
        });
        write_endurance_checkpoint(
            &config.checkpoint_path,
            "running",
            config_report,
            state,
            started_unix_seconds,
            started.elapsed(),
            history,
            current_phase.as_ref(),
            None,
            false,
            None,
        )?;
        eprintln!(
            "anonssh-test: endurance phase {sequence} {:?} started with {} completed observations",
            phase, history.completed_observations,
        );
        let observation = run_endurance_observation(
            server_pool,
            client_pool,
            server,
            client,
            config,
            state,
            started,
            sequence,
            phase,
            payload,
        );
        let (observation, stop_after_phase) =
            complete_endurance_phase(observation, stop.as_mut()).await?;
        eprintln!(
            "anonssh-test: endurance phase {sequence} {:?} completed with {} active client lanes and {} bytes of persistent state",
            phase,
            observation.client_active_lanes,
            observation.resources.persistent_state_bytes,
        );
        history.observe(observation);
        write_endurance_history(config, state.generation, history)?;
        *current_phase = None;
        write_endurance_checkpoint(
            &config.checkpoint_path,
            "running",
            config_report,
            state,
            started_unix_seconds,
            started.elapsed(),
            history,
            None,
            stop_after_phase,
            false,
            None,
        )?;
        if let Some(stop_reason) = stop_after_phase {
            return Ok(stop_reason);
        }
        sequence = sequence
            .checked_add(1)
            .context("endurance sequence overflow")?;
    }
}

async fn complete_endurance_phase<T, O, S>(
    observation: O,
    mut stop: Pin<&mut S>,
) -> Result<(T, Option<EnduranceStopReason>)>
where
    O: Future<Output = Result<T>>,
    S: Future<Output = Result<EnduranceStopReason>>,
{
    tokio::pin!(observation);
    let mut stop_after_phase = None;
    let result = tokio::select! {
        biased;
        stop_reason = &mut stop => {
            stop_after_phase = Some(stop_reason?);
            observation.await
        }
        result = &mut observation => result,
    };
    Ok((result?, stop_after_phase))
}

#[allow(clippy::too_many_arguments)]
async fn run_endurance_observation(
    server_pool: &RouterPool,
    client_pool: &RouterPool,
    server: &BondSession,
    client: &ClientBondSession,
    config: &EnduranceConfig,
    state: &EnduranceStateMetadata,
    run_started: Instant,
    sequence: u64,
    phase: EndurancePhase,
    payload: &[u8],
) -> Result<EnduranceObservation> {
    let phase_started = Instant::now();
    let (before_client, before_server) =
        tokio::try_join!(client.session().statistics(), server.statistics())?;
    let (bulk, mut quiet_realtime_round_trip_micros) = match phase.scale_direction() {
        Some(direction) => (
            Some(
                run_scale_round_with_interval(
                    client.session(),
                    server,
                    payload,
                    usize::try_from(sequence).context("endurance sequence does not fit usize")?,
                    direction,
                    ENDURANCE_BULK_REALTIME_INTERVAL,
                    Some(1),
                )
                .await?,
            ),
            Vec::new(),
        ),
        None => (
            None,
            run_endurance_quiet_phase(
                client.session(),
                server,
                sequence,
                Duration::from_secs(config.quiet_seconds),
            )
            .await?,
        ),
    };
    let (client_stats, server_stats) =
        wait_until_pair_acknowledged(client.session(), server).await?;
    let scaling = client.scaling_progress()?;
    let resources = endurance_resource_observation(server_pool, client_pool, config).await?;
    if resources.persistent_state_bytes > config.maximum_disk_bytes {
        bail!(
            "endurance state reached {} bytes, above its {} byte ceiling",
            resources.persistent_state_bytes,
            config.maximum_disk_bytes
        );
    }
    let mut lanes = endurance_lane_observations(
        EnduranceEndpoint::Client,
        &before_client,
        &client_stats,
        config.slots_per_provider,
    )?;
    lanes.extend(endurance_lane_observations(
        EnduranceEndpoint::Server,
        &before_server,
        &server_stats,
        config.slots_per_provider,
    )?);
    let runtime = EnduranceRuntimeObservation {
        client: endurance_runtime_delta(&before_client, &client_stats)?,
        server: endurance_runtime_delta(&before_server, &server_stats)?,
    };
    let contribution = endurance_contribution_observation(&lanes);
    quiet_realtime_round_trip_micros.sort_unstable();
    let quiet_realtime_round_trip_micros_p50 = (!quiet_realtime_round_trip_micros.is_empty())
        .then(|| scale_percentile(&quiet_realtime_round_trip_micros, 50))
        .transpose()?;
    let quiet_realtime_round_trip_micros_p95 = (!quiet_realtime_round_trip_micros.is_empty())
        .then(|| scale_percentile(&quiet_realtime_round_trip_micros, 95))
        .transpose()?;
    let quiet_realtime_round_trip_micros_max = quiet_realtime_round_trip_micros.last().copied();
    Ok(EnduranceObservation {
        sequence,
        state_generation: state.generation,
        phase,
        run_elapsed_millis: duration_millis(run_started.elapsed()),
        phase_elapsed_millis: duration_millis(phase_started.elapsed()),
        state_age_seconds: current_unix_seconds()?.saturating_sub(state.created_unix_seconds),
        client_active_lanes: client_stats.lanes.iter().filter(|lane| lane.active).count(),
        server_active_lanes: server_stats.lanes.iter().filter(|lane| lane.active).count(),
        desired_lane_ids: scaling.desired_lane_ids,
        pending_pressure_lane_ids: scaling.pending_pressure_lane_ids,
        adaptive_generation: scaling
            .events
            .last()
            .map(|event| event.generation)
            .unwrap_or(0),
        adaptive_events_retained: scaling.events.len(),
        bulk,
        quiet_realtime_round_trip_micros,
        quiet_realtime_round_trip_micros_p50,
        quiet_realtime_round_trip_micros_p95,
        quiet_realtime_round_trip_micros_max,
        quiet_realtime_is_echo: true,
        realtime_redundancy: true,
        runtime,
        contribution,
        resources,
        lanes,
    })
}

async fn run_endurance_quiet_phase(
    client: &BondSession,
    server: &BondSession,
    sequence: u64,
    duration: Duration,
) -> Result<Vec<u64>> {
    tokio::time::timeout(TRANSFER_TIMEOUT, async {
        if ENDURANCE_QUIET_REALTIME_SAMPLES != SCALE_REALTIME_SAMPLES {
            bail!("endurance and scale real-time sample counts diverged");
        }
        let outbound = client.open_stream(TrafficClass::Realtime).await?;
        let inbound = server.accept_stream().await?;
        if outbound.stream_id() != inbound.stream_id()
            || inbound.traffic_class() != TrafficClass::Realtime
        {
            bail!("endurance quiet phase accepted the wrong logical stream");
        }
        let round = usize::try_from(sequence).context("endurance sequence does not fit usize")?;
        let spacing = duration / u32::try_from(ENDURANCE_QUIET_REALTIME_SAMPLES - 1).unwrap_or(1);
        let active = AtomicBool::new(true);
        let progress = ScaleRoundProgress::new(0);
        let latencies = run_scale_realtime_samples(
            outbound,
            inbound,
            RealtimeSampleConfig {
                round,
                sample_count: SCALE_REALTIME_SAMPLES,
                sample_interval: spacing,
                initial_echo_delay: Duration::ZERO,
            },
            &active,
            &progress,
        )
        .await?;
        if latencies.len() != ENDURANCE_QUIET_REALTIME_SAMPLES {
            bail!("endurance quiet phase omitted an echoed real-time sample");
        }
        Ok(latencies)
    })
    .await
    .context("endurance quiet echo phase exceeded its 15-minute deadline")?
}

async fn endurance_resource_observation(
    server_pool: &RouterPool,
    client_pool: &RouterPool,
    config: &EnduranceConfig,
) -> Result<EnduranceResourceObservation> {
    let mut observation = EnduranceResourceObservation::default();
    for pool in [server_pool, client_pool] {
        for sample in pool.process_samples().await? {
            observation.maximum_router_startup_millis =
                observation.maximum_router_startup_millis.max(
                    sample
                        .startup_latency
                        .map(|latency| u64::try_from(latency.as_millis()).unwrap_or(u64::MAX))
                        .unwrap_or(0),
                );
            if let Some(usage) = sample.usage {
                observation.running_router_processes =
                    observation.running_router_processes.saturating_add(1);
                observation.router_cpu_time_micros = observation
                    .router_cpu_time_micros
                    .saturating_add(u64::try_from(usage.cpu_time.as_micros()).unwrap_or(u64::MAX));
                observation.router_resident_bytes = observation
                    .router_resident_bytes
                    .saturating_add(usage.resident_bytes);
            }
        }
    }
    observation.persistent_state_bytes = directory_size_while_running(&config.state_root)?;
    Ok(observation)
}

fn endurance_lane_observations(
    endpoint: EnduranceEndpoint,
    before: &BondRuntimeStats,
    after: &BondRuntimeStats,
    slots_per_provider: usize,
) -> Result<Vec<EnduranceLaneObservation>> {
    let maximum_lane = expected_scale_lanes(slots_per_provider)?;
    after
        .lanes
        .iter()
        .map(|lane| {
            let id = usize::try_from(lane.id.get()).context("lane ID does not fit usize")?;
            let provider = if id <= slots_per_provider {
                Provider::Tor
            } else if id <= maximum_lane {
                Provider::I2p
            } else {
                bail!("endurance runtime reported out-of-topology lane {id}");
            };
            let previous = before
                .lanes
                .iter()
                .find(|candidate| candidate.id == lane.id);
            let previous_scheduled = previous.map_or(0, |candidate| candidate.bytes_scheduled);
            let previous_acknowledged =
                previous.map_or(0, |candidate| candidate.bytes_acknowledged);
            Ok(EnduranceLaneObservation {
                endpoint,
                id: lane.id.get(),
                provider,
                active: lane.active,
                delivery_measured: lane.delivery_measured,
                reserved_for_low_latency: lane.reserved_for_low_latency,
                smoothed_round_trip_micros: u64::try_from(
                    lane.smoothed_round_trip_time.as_micros(),
                )
                .unwrap_or(u64::MAX),
                delivery_rate_bps: lane.delivery_rate_bps,
                bytes_scheduled: lane.bytes_scheduled,
                bytes_acknowledged: lane.bytes_acknowledged,
                phase_bytes_scheduled: endurance_counter_delta(
                    lane.bytes_scheduled,
                    previous_scheduled,
                    "lane scheduled bytes",
                )?,
                phase_bytes_acknowledged: endurance_counter_delta(
                    lane.bytes_acknowledged,
                    previous_acknowledged,
                    "lane acknowledged bytes",
                )?,
            })
        })
        .collect()
}

fn endurance_runtime_delta(
    before: &BondRuntimeStats,
    after: &BondRuntimeStats,
) -> Result<EnduranceRuntimeDelta> {
    Ok(EnduranceRuntimeDelta {
        new_data_frames: endurance_counter_delta(
            after.new_data_frames,
            before.new_data_frames,
            "new data frames",
        )?,
        redundant_realtime_frames: endurance_counter_delta(
            after.redundant_realtime_frames,
            before.redundant_realtime_frames,
            "redundant real-time frames",
        )?,
        dropped_redundant_realtime_frames: endurance_counter_delta(
            after.dropped_redundant_realtime_frames,
            before.dropped_redundant_realtime_frames,
            "dropped redundant real-time frames",
        )?,
        retransmitted_frames: endurance_counter_delta(
            after.retransmitted_frames,
            before.retransmitted_frames,
            "retransmitted frames",
        )?,
        ping_frames: endurance_counter_delta(after.ping_frames, before.ping_frames, "ping frames")?,
        pong_frames: endurance_counter_delta(after.pong_frames, before.pong_frames, "pong frames")?,
        liveness_failures: endurance_counter_delta(
            after.liveness_failures,
            before.liveness_failures,
            "liveness failures",
        )?,
        acknowledgement_frames: endurance_counter_delta(
            after.acknowledgement_frames,
            before.acknowledgement_frames,
            "acknowledgement frames",
        )?,
        window_update_frames: endurance_counter_delta(
            after.window_update_frames,
            before.window_update_frames,
            "window update frames",
        )?,
        replayed_control_frames: endurance_counter_delta(
            after.replayed_control_frames,
            before.replayed_control_frames,
            "replayed control frames",
        )?,
        delivered_bytes: endurance_counter_delta(
            after.delivered_bytes,
            before.delivered_bytes,
            "delivered bytes",
        )?,
        stream_backpressure_events: endurance_counter_delta(
            after.stream_backpressure_events,
            before.stream_backpressure_events,
            "stream backpressure events",
        )?,
        final_reorder_high_water: after.reorder_high_water,
        final_unacknowledged_bytes: after.unacknowledged_bytes,
        final_active_streams: after.active_streams,
        final_retired_stream_tombstones: after.retired_stream_tombstones,
        final_maximum_lane_queue_delay_micros: max_lane_queue_delay(after),
    })
}

fn endurance_counter_delta(after: u64, before: u64, label: &str) -> Result<u64> {
    after
        .checked_sub(before)
        .with_context(|| format!("endurance {label} counter moved backwards"))
}

fn endurance_contribution_observation(
    lanes: &[EnduranceLaneObservation],
) -> EnduranceContributionObservation {
    let mut observation = EnduranceContributionObservation::default();
    for lane in lanes
        .iter()
        .filter(|lane| lane.phase_bytes_acknowledged > 0)
    {
        match lane.provider {
            Provider::Tor => {
                observation.tor_acknowledged_bytes = observation
                    .tor_acknowledged_bytes
                    .saturating_add(lane.phase_bytes_acknowledged);
                observation.contributing_tor_lanes =
                    observation.contributing_tor_lanes.saturating_add(1);
            }
            Provider::I2p => {
                observation.i2p_acknowledged_bytes = observation
                    .i2p_acknowledged_bytes
                    .saturating_add(lane.phase_bytes_acknowledged);
                observation.contributing_i2p_lanes =
                    observation.contributing_i2p_lanes.saturating_add(1);
            }
        }
        observation.maximum_lane_acknowledged_bytes = observation
            .maximum_lane_acknowledged_bytes
            .max(lane.phase_bytes_acknowledged);
    }
    let total = observation
        .tor_acknowledged_bytes
        .saturating_add(observation.i2p_acknowledged_bytes);
    if total > 0 {
        observation.maximum_lane_share_basis_points = u64::try_from(
            (observation.maximum_lane_acknowledged_bytes as u128).saturating_mul(10_000)
                / total as u128,
        )
        .unwrap_or(u64::MAX);
    }
    observation
}

async fn count_running_router_processes(
    server_pool: &RouterPool,
    client_pool: &RouterPool,
) -> Result<usize> {
    let mut running = 0_usize;
    for pool in [server_pool, client_pool] {
        running = running.saturating_add(
            pool.process_samples()
                .await?
                .iter()
                .filter(|sample| sample.usage.is_some())
                .count(),
        );
    }
    Ok(running)
}

async fn wait_for_endurance_stop(duration_seconds: u64) -> Result<EnduranceStopReason> {
    if duration_seconds == 0 {
        wait_for_endurance_signal().await?;
        return Ok(EnduranceStopReason::Signal);
    }
    tokio::select! {
        () = tokio::time::sleep(Duration::from_secs(duration_seconds)) => {
            Ok(EnduranceStopReason::DurationElapsed)
        }
        result = wait_for_endurance_signal() => {
            result?;
            Ok(EnduranceStopReason::Signal)
        }
    }
}

#[cfg(unix)]
async fn wait_for_endurance_signal() -> Result<()> {
    let mut terminate = tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate())
        .context("failed to install endurance SIGTERM handler")?;
    tokio::select! {
        result = tokio::signal::ctrl_c() => {
            result.context("failed to install endurance SIGINT handler")?;
        }
        signal = terminate.recv() => {
            signal.context("endurance SIGTERM handler stopped")?;
        }
    }
    Ok(())
}

#[cfg(not(unix))]
async fn wait_for_endurance_signal() -> Result<()> {
    tokio::signal::ctrl_c()
        .await
        .context("failed to install endurance interrupt handler")
}

#[allow(clippy::too_many_arguments)]
fn write_endurance_checkpoint(
    path: &Path,
    status: &'static str,
    config: &EnduranceConfigReport,
    state: &EnduranceStateMetadata,
    started_unix_seconds: u64,
    elapsed: Duration,
    history: &EnduranceHistory,
    current_phase: Option<&EnduranceCurrentPhase>,
    stop_reason: Option<EnduranceStopReason>,
    cleanup_complete: bool,
    error: Option<&str>,
) -> Result<()> {
    write_json_atomically(
        path,
        &EnduranceCheckpoint {
            schema: ENDURANCE_SCHEMA,
            status,
            methodology: ENDURANCE_METHODOLOGY,
            config,
            state,
            started_unix_seconds,
            elapsed_millis: duration_millis(elapsed),
            completed_observations: history.completed_observations,
            current_phase,
            stop_reason,
            cleanup_complete,
            initial_observations: &history.initial_observations,
            recent_observations: &history.recent_observations,
            aggregates: &history.aggregates,
            error,
        },
    )
}

fn live_error_report(schema: &str, error: &anyhow::Error) -> serde_json::Value {
    serde_json::json!({
        "schema": schema,
        "status": "error",
        "error": format!("{error:#}"),
    })
}

async fn run_scale_campaign() -> Result<ScaleCampaignReport> {
    let i2pd_binary = resolve_executable("ANONSSH_I2PD_BIN", "i2pd")?;
    let tor_binary = resolve_executable("ANONSSH_TOR_BIN", "tor")?;
    let config = ScaleCampaignConfig::from_environment()?;
    let matrix = config.matrix();
    if matrix.len() != config.cardinalities.len() * SCALE_SCENARIOS_PER_CARDINALITY {
        bail!("scale matrix does not cover every cardinality and workload");
    }
    let root = live_root("bond-scale-campaign");
    remove_if_present(&root)?;
    let endpoints = allocate_scale_pool_endpoints(config.maximum_slots_per_provider())?;
    let server_pool = scale_router_pool(
        &root.join("server"),
        tor_binary.clone(),
        i2pd_binary.clone(),
        endpoints.server,
    )?;
    let client_pool = scale_router_pool(
        &root.join("client"),
        tor_binary,
        i2pd_binary,
        endpoints.client,
    )?;

    let operation =
        run_scale_campaign_with_pools(&root, &server_pool, &client_pool, &config, &matrix).await;
    let (server_cleanup, client_cleanup) = tokio::join!(server_pool.stop(), client_pool.stop());
    let cleanup =
        merge_result(server_cleanup, client_cleanup).and_then(|()| remove_if_present(&root));
    merge_result(operation, cleanup)
}

async fn run_scale_campaign_with_pools(
    root: &Path,
    server_pool: &RouterPool,
    client_pool: &RouterPool,
    config: &ScaleCampaignConfig,
    matrix: &[ScaleScenario],
) -> Result<ScaleCampaignReport> {
    let mut observations = Vec::with_capacity(matrix.len());
    let mut warmed_slots_per_provider = 0_usize;
    let checkpoint_path = std::env::var_os(SCALE_CHECKPOINT_ENV).map(PathBuf::from);
    for (index, scenario) in matrix.iter().copied().enumerate() {
        let warm_slots = warmed_slots_per_provider.min(scenario.slots_per_provider);
        let router_state = ScaleRouterState::classify(warm_slots, scenario.slots_per_provider);
        let current_trial = ScaleCheckpointTrial::new(index + 1, scenario, router_state);
        if let Some(path) = &checkpoint_path {
            write_scale_checkpoint(
                path,
                "running",
                config,
                matrix.len(),
                &observations,
                Some(current_trial),
                None,
            )?;
        }
        eprintln!(
            "anonssh-test: scale trial {} of {}: {}+{}, {}, {} bytes per direction, {:?} state",
            index + 1,
            matrix.len(),
            scenario.slots_per_provider,
            scenario.slots_per_provider,
            scenario.direction.label(),
            scenario.payload_bytes,
            router_state,
        );
        let server_view =
            server_pool.prefix(scenario.slots_per_provider, scenario.slots_per_provider)?;
        let client_view =
            client_pool.prefix(scenario.slots_per_provider, scenario.slots_per_provider)?;
        let observation = run_scale_trial(
            root,
            &server_view,
            &client_view,
            index + 1,
            scenario,
            warm_slots,
            config.rounds_per_trial,
        )
        .await;
        warmed_slots_per_provider = warmed_slots_per_provider.max(scenario.slots_per_provider);
        let (server_stop, client_stop) = tokio::join!(server_pool.stop(), client_pool.stop());
        let stopped = merge_result(server_stop, client_stop);
        match merge_result(observation, stopped) {
            Ok(observation) => observations.push(observation),
            Err(error) => {
                if let Some(path) = &checkpoint_path {
                    let message = format!("{error:#}");
                    if let Err(checkpoint_error) = write_scale_checkpoint(
                        path,
                        "error",
                        config,
                        matrix.len(),
                        &observations,
                        Some(current_trial),
                        Some(&message),
                    ) {
                        return Err(error).context(format!(
                            "scale checkpoint also failed: {checkpoint_error:#}"
                        ));
                    }
                }
                return Err(error);
            }
        }
        if let Some(path) = &checkpoint_path {
            write_scale_checkpoint(
                path,
                "running",
                config,
                matrix.len(),
                &observations,
                None,
                None,
            )?;
        }
    }
    let comparisons = build_scale_comparisons(&observations, &config.cardinalities)?;
    let report = ScaleCampaignReport {
        schema: SCALE_SCHEMA,
        status: "ok",
        methodology: SCALE_METHODOLOGY,
        maximum_slots_per_provider: config.maximum_slots_per_provider(),
        rounds_per_trial: config.rounds_per_trial,
        observations,
        comparisons,
    };
    if let Some(path) = &checkpoint_path {
        write_scale_checkpoint(
            path,
            "ok",
            config,
            matrix.len(),
            &report.observations,
            None,
            None,
        )?;
    }
    Ok(report)
}

fn write_scale_checkpoint(
    path: &Path,
    status: &'static str,
    config: &ScaleCampaignConfig,
    total_trials: usize,
    observations: &[ScaleTrialReport],
    current_trial: Option<ScaleCheckpointTrial>,
    error: Option<&str>,
) -> Result<()> {
    let comparisons = build_scale_comparisons(observations, &config.cardinalities)?;
    let checkpoint = ScaleCampaignCheckpoint {
        schema: SCALE_SCHEMA,
        status,
        methodology: SCALE_METHODOLOGY,
        completed_trials: observations.len(),
        total_trials,
        maximum_slots_per_provider: config.maximum_slots_per_provider(),
        rounds_per_trial: config.rounds_per_trial,
        current_trial,
        observations,
        comparisons,
        error,
    };
    write_json_atomically(path, &checkpoint)
}

fn build_scale_comparisons(
    observations: &[ScaleTrialReport],
    cardinalities: &[usize],
) -> Result<Vec<ScaleComparison>> {
    let mut comparisons = Vec::new();
    for (payload_bytes, direction) in SCALE_WORKLOADS {
        for pair in cardinalities.windows(2) {
            let baseline_slots = pair[0];
            let scaled_slots = pair[1];
            let baseline = observations.iter().find(|observation| {
                observation.direction == direction
                    && observation.payload_bytes == payload_bytes
                    && observation.tor_routers_per_endpoint == baseline_slots
                    && observation.i2p_routers_per_endpoint == baseline_slots
            });
            let scaled = observations.iter().find(|observation| {
                observation.direction == direction
                    && observation.payload_bytes == payload_bytes
                    && observation.tor_routers_per_endpoint == scaled_slots
                    && observation.i2p_routers_per_endpoint == scaled_slots
            });
            match (baseline, scaled) {
                (Some(baseline), Some(scaled)) => {
                    comparisons.push(compare_scale_trials(baseline, scaled)?)
                }
                (None, None) | (Some(_), None) => break,
                (None, Some(_)) => {
                    bail!(
                        "scale observations contain {scaled_slots}+{scaled_slots} {direction:?} without its {baseline_slots}+{baseline_slots} baseline"
                    )
                }
            }
        }
    }
    Ok(comparisons)
}

fn compare_scale_trials(
    baseline: &ScaleTrialReport,
    scaled: &ScaleTrialReport,
) -> Result<ScaleComparison> {
    if baseline.direction != scaled.direction
        || baseline.payload_bytes != scaled.payload_bytes
        || baseline.tor_routers_per_endpoint != baseline.i2p_routers_per_endpoint
        || scaled.tor_routers_per_endpoint != scaled.i2p_routers_per_endpoint
        || scaled.tor_routers_per_endpoint != baseline.tor_routers_per_endpoint * 2
    {
        bail!("scale comparison observations are not adjacent instances of one workload");
    }
    let lane_ratio_basis_points = ratio_basis_points(
        scaled.authenticated_lanes as u64,
        baseline.authenticated_lanes as u64,
    )?;
    let eligible_bulk_path_ratio_basis_points = ratio_basis_points(
        scaled.eligible_bulk_paths as u64,
        baseline.eligible_bulk_paths as u64,
    )?;
    let goodput_ratio_basis_points =
        ratio_basis_points(scaled.median_goodput_bps, baseline.median_goodput_bps)?;
    Ok(ScaleComparison {
        scenario: format!(
            "{}-{}-bytes-{}-to-{}-slots-per-provider",
            baseline.direction.label(),
            baseline.payload_bytes,
            baseline.tor_routers_per_endpoint,
            scaled.tor_routers_per_endpoint,
        ),
        direction: baseline.direction,
        payload_bytes: baseline.payload_bytes,
        baseline_slots_per_provider: baseline.tor_routers_per_endpoint,
        scaled_slots_per_provider: scaled.tor_routers_per_endpoint,
        lane_ratio_basis_points,
        eligible_bulk_path_ratio_basis_points,
        goodput_ratio_basis_points,
        ideal_linear_scaling_efficiency_basis_points: ratio_basis_points(
            goodput_ratio_basis_points,
            eligible_bulk_path_ratio_basis_points,
        )?,
        realtime_p50_ratio_basis_points: ratio_basis_points(
            scaled.realtime_round_trip_micros_p50,
            baseline.realtime_round_trip_micros_p50,
        )?,
        realtime_p95_ratio_basis_points: ratio_basis_points(
            scaled.realtime_round_trip_micros_p95,
            baseline.realtime_round_trip_micros_p95,
        )?,
    })
}

async fn run_scale_trial(
    root: &Path,
    server_pool: &RouterPool,
    client_pool: &RouterPool,
    sequence: usize,
    scenario: ScaleScenario,
    warm_router_slots_per_provider: usize,
    rounds_per_trial: usize,
) -> Result<ScaleTrialReport> {
    let mut report = run_with_scale_pool(
        server_pool,
        client_pool,
        sequence,
        scenario,
        warm_router_slots_per_provider,
        rounds_per_trial,
    )
    .await?;
    report.disk_bytes = scale_topology_directory_size(root, scenario.slots_per_provider)?;
    Ok(report)
}

async fn run_with_scale_pool(
    server_pool: &RouterPool,
    client_pool: &RouterPool,
    sequence: usize,
    scenario: ScaleScenario,
    warm_router_slots_per_provider: usize,
    rounds_per_trial: usize,
) -> Result<ScaleTrialReport> {
    let ScaleScenario {
        slots_per_provider,
        payload_bytes,
        direction,
    } = scenario;
    let router_state =
        ScaleRouterState::classify(warm_router_slots_per_provider, slots_per_provider);
    let startup_started = Instant::now();
    let client_socks = if client_pool.tor_slots().is_empty() {
        client_pool
            .ensure_i2p_slot(1)
            .await
            .context("failed to start scale client discovery router")?;
        Vec::new()
    } else {
        vec![client_pool
            .ensure_tor_slot(1)
            .await
            .context("failed to start scale client discovery router")?]
    };
    let slot_count = u32::try_from(slots_per_provider).context("scale slot count overflow")?;
    let machine_id = format!("{MACHINE_ID}-scale-{sequence}-{slots_per_provider}");
    let password = Zeroizing::new(PASSWORD.to_owned());
    let server_identity = IdentityManager::derive_server_recovery_identity_with_pool_slots(
        &password,
        &machine_id,
        slot_count,
        slot_count,
    )?;
    let client_identity = IdentityManager::derive_client_recovery_identity_with_pool_slots(
        &password,
        &machine_id,
        slot_count,
        slot_count,
    )?;
    drop(password);

    let scaling_policy = fixed_scale_policy(expected_scale_lanes(slots_per_provider)?);
    let ingress =
        BondIngress::publish_with_scaling_policy(server_pool, &server_identity, scaling_policy)
            .await?;
    let startup_elapsed = startup_started.elapsed();
    let tor_destinations = server_identity
        .tor_pool
        .iter()
        .map(|identity| identity.destination.clone())
        .collect::<Vec<_>>();
    let i2p_destinations = server_identity
        .i2p_pool
        .iter()
        .map(|identity| identity.destination.clone())
        .collect::<Vec<_>>();
    let formation_started = Instant::now();
    let accept = ingress.accept_session();
    let connect = ClientBondSession::connect_with_scaling_policy(
        client_pool,
        &client_socks,
        &tor_destinations,
        &i2p_destinations,
        *client_identity.bond_session_key,
        scaling_policy,
    );
    let (server, client) = tokio::try_join!(accept, connect)?;
    let report = with_pool_supervision(
        &ingress,
        &server,
        client_pool,
        &client,
        PoolSupervisionMode::FixedAll,
        async {
    let expected_lanes = expected_scale_lanes(slots_per_provider)?;
    let (activation_stats, activation_server_stats) =
        tokio::try_join!(client.session().statistics(), server.statistics())?;
    let initial_activation_lanes = activation_stats
        .lanes
        .iter()
        .filter(|lane| lane.active)
        .count();
    eprintln!(
        "anonssh-test: scale trial {sequence} activated with {initial_activation_lanes} lane(s); driving fixed formation to {expected_lanes}"
    );
    if initial_activation_lanes == 0 || initial_activation_lanes > expected_lanes {
        bail!("scale topology activated with invalid lane cardinality {initial_activation_lanes}");
    }
    let formation_load_bytes = drive_scale_formation(&client, &server, expected_lanes).await?;
    wait_for_pool_repair(&server, &client, expected_lanes)
        .await
        .context("scale topology did not remain stable after formation pressure")?;
    let topology_formation = formation_started.elapsed();
    eprintln!(
        "anonssh-test: scale trial {sequence} formed {expected_lanes} lanes after {} ms and {} pressure bytes",
        topology_formation.as_millis(),
        formation_load_bytes
    );
    let (initial_stats, initial_server_stats) =
        tokio::try_join!(client.session().statistics(), server.statistics())?;
    let formation_retransmitted_frames = pair_counter_delta(
        &activation_stats,
        &activation_server_stats,
        &initial_stats,
        &initial_server_stats,
        |stats| stats.retransmitted_frames,
    );
    let formation_liveness_failures = pair_counter_delta(
        &activation_stats,
        &activation_server_stats,
        &initial_stats,
        &initial_server_stats,
        |stats| stats.liveness_failures,
    );
    let formation_replayed_control_frames = pair_counter_delta(
        &activation_stats,
        &activation_server_stats,
        &initial_stats,
        &initial_server_stats,
        |stats| stats.replayed_control_frames,
    );
    if initial_stats.lanes.len() != expected_lanes
        || initial_stats.lanes.iter().any(|lane| !lane.active)
        || initial_server_stats.lanes.len() != expected_lanes
        || initial_server_stats.lanes.iter().any(|lane| !lane.active)
    {
        bail!(
            "scale topology did not settle at {expected_lanes} active lanes: client={:?}; server={:?}",
            initial_stats.lanes,
            initial_server_stats.lanes
        );
    }
    let mut repair_cycles = 0;
    let mut inactive_endpoint_lane_observations = 0;

    let warmup = deterministic_scale_payload(SCALE_WARMUP_BYTES);
    let received = transfer_stream(client.session(), &server, TrafficClass::Bulk, &warmup).await?;
    if received != warmup {
        bail!("scale warm-up payload mismatch");
    }
    let realtime_warmup = b"anonssh scale realtime warmup";
    let received = transfer_stream(
        client.session(),
        &server,
        TrafficClass::Realtime,
        realtime_warmup,
    )
    .await?;
    if received != realtime_warmup {
        bail!("scale real-time warm-up payload mismatch");
    }
    let warmup_client_stats = wait_until_acknowledged(client.session()).await?;
    let warmup_server_stats = server.statistics().await?;
    let warmup_inactive = warmup_client_stats
        .lanes
        .iter()
        .chain(&warmup_server_stats.lanes)
        .filter(|lane| !lane.active)
        .count();
    if warmup_inactive > 0 {
        repair_cycles += 1;
        inactive_endpoint_lane_observations += warmup_inactive;
        wait_for_pool_repair(&server, &client, expected_lanes).await?;
    }
    let reprobe_interval = SchedulerConfig::default().bulk_reprobe_interval;
    eprintln!(
        "anonssh-test: scale trial {sequence} awaiting {} ms periodic reprobe window",
        reprobe_interval.as_millis()
    );
    tokio::time::sleep(reprobe_interval).await;
    let (before_client, before_server) =
        wait_until_pair_acknowledged(client.session(), &server).await?;

    let payload = deterministic_scale_payload(payload_bytes);
    let mut rounds = Vec::with_capacity(rounds_per_trial);
    for round in 1..=rounds_per_trial {
        let report =
            run_scale_round(client.session(), &server, &payload, round, direction).await?;
        eprintln!(
            "anonssh-test: scale trial {sequence} round {round} completed at {} bps with {} us p95 realtime RTT",
            report.goodput_bps,
            report.realtime_round_trip_micros_p95
        );
        rounds.push(report);
    }
    let (client_stats, server_stats) =
        wait_until_pair_acknowledged(client.session(), &server).await?;
    if client_stats.lanes.len() != expected_lanes || server_stats.lanes.len() != expected_lanes {
        bail!("scale topology changed lane cardinality after its measured round");
    }
    let inactive = client_stats
        .lanes
        .iter()
        .chain(&server_stats.lanes)
        .filter(|lane| !lane.active)
        .count();
    if inactive > 0 {
        repair_cycles += 1;
        inactive_endpoint_lane_observations += inactive;
        wait_for_pool_repair(&server, &client, expected_lanes).await?;
    }
    let (after, server_after) = wait_until_pair_acknowledged(client.session(), &server).await?;
    let active_lanes = after.lanes.iter().filter(|lane| lane.active).count();
    let mut lanes_with_acknowledged_bytes = 0;
    let mut tor_acknowledged_bytes = 0_u64;
    let mut i2p_acknowledged_bytes = 0_u64;
    for lane in &after.lanes {
        let mut acknowledged = 0_u64;
        if direction.includes_client_to_server() {
            acknowledged = acknowledged.saturating_add(acknowledged_bytes_for_lane(
                &before_client,
                &after,
                lane.id.get(),
            )?);
        }
        if direction.includes_server_to_client() {
            acknowledged = acknowledged.saturating_add(acknowledged_bytes_for_lane(
                &before_server,
                &server_after,
                lane.id.get(),
            )?);
        }
        if acknowledged > 0 {
            lanes_with_acknowledged_bytes += 1;
        }
        if lane.id.get() as usize <= slots_per_provider {
            tor_acknowledged_bytes = tor_acknowledged_bytes.saturating_add(acknowledged);
        } else {
            i2p_acknowledged_bytes = i2p_acknowledged_bytes.saturating_add(acknowledged);
        }
    }
    let mut final_reserved_lanes = BTreeSet::new();
    if direction.includes_client_to_server() {
        observe_protected_lanes(&after, &mut final_reserved_lanes);
    }
    if direction.includes_server_to_client() {
        observe_protected_lanes(&server_after, &mut final_reserved_lanes);
    }
    if final_reserved_lanes.is_empty() {
        bail!("scale topology has no protected low-latency lane");
    }
    let protected_lanes_observed = rounds
        .iter()
        .flat_map(|round| round.protected_lanes_observed.iter().copied())
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect::<Vec<_>>();
    let protected_lane_acknowledged_bytes = rounds
        .iter()
        .map(|round| round.protected_lane_acknowledged_bytes)
        .fold(0_u64, u64::saturating_add);
    if active_lanes != expected_lanes {
        bail!("scale topology finished with inactive lanes");
    }
    if tor_acknowledged_bytes == 0 || i2p_acknowledged_bytes == 0 {
        bail!(
            "scale topology did not acknowledge measured bytes on both providers: Tor={tor_acknowledged_bytes}, I2P={i2p_acknowledged_bytes}"
        );
    }
    if protected_lane_acknowledged_bytes == 0 {
        bail!("scale topology did not acknowledge measured bytes on its protected pool");
    }
    if after.unacknowledged_bytes != 0 || server_after.unacknowledged_bytes != 0 {
        bail!("scale topology retained unacknowledged bytes");
    }

    let process_samples = [server_pool, client_pool];
    let mut router_cpu_time_micros = 0_u64;
    let mut router_resident_bytes = 0_u64;
    let mut max_router_startup_millis = 0_u64;
    for pool in process_samples {
        for sample in pool.process_samples().await? {
            let usage = sample.usage.with_context(|| {
                format!("scale router slot {} omitted process usage", sample.slot)
            })?;
            router_cpu_time_micros = router_cpu_time_micros
                .saturating_add(u64::try_from(usage.cpu_time.as_micros()).unwrap_or(u64::MAX));
            router_resident_bytes = router_resident_bytes.saturating_add(usage.resident_bytes);
            max_router_startup_millis = max_router_startup_millis.max(
                sample
                    .startup_latency
                    .map(|latency| u64::try_from(latency.as_millis()).unwrap_or(u64::MAX))
                    .unwrap_or(0),
            );
        }
    }

    let mut goodputs = rounds
        .iter()
        .map(|round| round.goodput_bps)
        .collect::<Vec<_>>();
    goodputs.sort_unstable();
    let median_goodput_bps = median(&goodputs)?;
    let mut realtime = rounds
        .iter()
        .flat_map(|round| round.realtime_round_trip_micros.iter().copied())
        .collect::<Vec<_>>();
    realtime.sort_unstable();
    let mut eligible_counts = Vec::with_capacity(direction.bulk_senders());
    if direction.includes_client_to_server() {
        eligible_counts.push(effective_bulk_lane_count(&after));
    }
    if direction.includes_server_to_client() {
        eligible_counts.push(effective_bulk_lane_count(&server_after));
    }
    let eligible_bulk_lanes_per_sender = *eligible_counts
        .first()
        .context("scale workload has no bulk sender")?;
    if eligible_bulk_lanes_per_sender == 0
        || eligible_counts
            .iter()
            .any(|count| *count != eligible_bulk_lanes_per_sender)
    {
        bail!("scale workload has inconsistent sender-side bulk eligibility: {eligible_counts:?}");
    }
    let eligible_bulk_paths = eligible_bulk_lanes_per_sender
        .checked_mul(direction.bulk_senders())
        .context("eligible bulk path count overflow")?;
    let bulk_isolated_from_protected_pool = (!direction.includes_client_to_server()
        || has_unprotected_active_lane(&after))
        && (!direction.includes_server_to_client()
            || has_unprotected_active_lane(&server_after));
    let max_queue_delay_micros = rounds
        .iter()
        .map(|round| round.max_queue_delay_micros)
        .max()
        .unwrap_or(0);
    let measured_retransmitted_frames = rounds.iter().map(|round| round.retransmitted_frames).sum();
    let measured_liveness_failures = rounds.iter().map(|round| round.liveness_failures).sum();
    let measured_replayed_control_frames = rounds
        .iter()
        .map(|round| round.replayed_control_frames)
        .sum();
    let retransmitted_frames = pair_counter_delta(
        &activation_stats,
        &activation_server_stats,
        &after,
        &server_after,
        |stats| stats.retransmitted_frames,
    );
    let liveness_failures = pair_counter_delta(
        &activation_stats,
        &activation_server_stats,
        &after,
        &server_after,
        |stats| stats.liveness_failures,
    );
    let replayed_control_frames = pair_counter_delta(
        &activation_stats,
        &activation_server_stats,
        &after,
        &server_after,
        |stats| stats.replayed_control_frames,
    );
    Ok::<_, anyhow::Error>(ScaleTrialReport {
        sequence,
        topology: format!("{slots_per_provider}+{slots_per_provider}"),
        direction,
        tor_routers_per_endpoint: slots_per_provider,
        i2p_routers_per_endpoint: slots_per_provider,
        warm_router_slots_per_provider,
        router_state,
        router_processes: expected_lanes * 2,
        initial_activation_lanes,
        formation_load_bytes,
        authenticated_lanes: expected_lanes,
        eligible_bulk_lanes_per_sender,
        eligible_bulk_paths,
        bulk_isolated_from_protected_pool,
        payload_bytes: payload.len(),
        payload_bytes_per_round: payload
            .len()
            .checked_mul(direction.bulk_senders())
            .context("scale round payload count overflow")?,
        bulk_senders: direction.bulk_senders(),
        rounds,
        median_goodput_bps,
        goodput_per_eligible_path_bps: median_goodput_bps
            / u64::try_from(eligible_bulk_paths).context("eligible path count overflow")?,
        realtime_round_trip_micros_p50: scale_percentile(&realtime, 50)?,
        realtime_round_trip_micros_p95: scale_percentile(&realtime, 95)?,
        realtime_round_trip_micros_max: *realtime
            .last()
            .context("scale campaign produced no overlapping real-time samples")?,
        active_lanes,
        repair_cycles,
        inactive_endpoint_lane_observations,
        lanes_with_acknowledged_bytes,
        tor_acknowledged_bytes,
        i2p_acknowledged_bytes,
        final_reserved_lanes: final_reserved_lanes.into_iter().collect(),
        protected_lanes_observed,
        protected_lane_acknowledged_bytes,
        startup_elapsed_millis: startup_elapsed.as_millis(),
        topology_formation_millis: topology_formation.as_millis(),
        max_router_startup_millis,
        router_cpu_time_micros,
        router_resident_bytes,
        disk_bytes: 0,
        max_queue_delay_micros,
        formation_retransmitted_frames,
        formation_liveness_failures,
        formation_replayed_control_frames,
        measured_retransmitted_frames,
        measured_liveness_failures,
        measured_replayed_control_frames,
        retransmitted_frames,
        liveness_failures,
        replayed_control_frames,
        unacknowledged_bytes: after
            .unacknowledged_bytes
            .saturating_add(server_after.unacknowledged_bytes),
    })
    })
    .await?;
    let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
    client_shutdown?;
    server_shutdown?;
    Ok(report)
}

async fn run_with_pool_recovery(
    server_pool: &RouterPool,
    client_pool: &RouterPool,
) -> Result<PoolRecoveryReport> {
    let client_socks = if client_pool.tor_slots().is_empty() {
        client_pool
            .ensure_i2p_slot(1)
            .await
            .context("failed to start recovery client discovery router")?;
        Vec::new()
    } else {
        vec![client_pool
            .ensure_tor_slot(1)
            .await
            .context("failed to start recovery client discovery router")?]
    };
    let router_candidates_started = server_pool.tor_candidate_count()
        + client_pool.tor_candidate_count()
        + server_pool.i2p_slots().len()
        + client_pool.i2p_slots().len();

    let password = Zeroizing::new(PASSWORD.to_owned());
    let server_identity = IdentityManager::derive_server_recovery_identity(&password, MACHINE_ID)?;
    let client_identity = IdentityManager::derive_client_recovery_identity(&password, MACHINE_ID)?;
    drop(password);
    let ingress = BondIngress::publish(server_pool, &server_identity).await?;
    let i2p_destinations = server_identity
        .i2p_pool
        .iter()
        .map(|identity| identity.destination.clone())
        .collect::<Vec<_>>();
    let tor_destinations = server_identity
        .tor_pool
        .iter()
        .map(|identity| identity.destination.clone())
        .collect::<Vec<_>>();
    let accept = ingress.accept_session();
    let connect = ClientBondSession::connect(
        client_pool,
        &client_socks,
        &tor_destinations,
        &i2p_destinations,
        *client_identity.bond_session_key,
    );
    let (server, client) = tokio::try_join!(accept, connect)?;
    let report = with_pool_supervision(
        &ingress,
        &server,
        client_pool,
        &client,
        PoolSupervisionMode::Adaptive,
        async {
            let zero_lane = prove_zero_lane_formation_repair(&server, &client).await?;
            let expected_lanes = PRODUCTION_TOR_SLOTS + PRODUCTION_I2P_SLOTS;
            drive_scale_formation(&client, &server, expected_lanes)
            .await
            .context("product recovery pool did not form its full adaptive topology")?;

            let initial = vec![0x51; 8 * 1024 * 1024];
            let received =
                transfer_stream(client.session(), &server, TrafficClass::Bulk, &initial).await?;
            if received != initial {
                bail!("initial product-pool transfer mismatch");
            }
            let initial_realtime = b"protected low-latency pool".repeat(1_024);
            let received = transfer_stream(
                client.session(),
                &server,
                TrafficClass::Realtime,
                &initial_realtime,
            )
            .await?;
            if received != initial_realtime {
                bail!("initial product-pool real-time transfer mismatch");
            }
            let (initial_stats, server_initial_stats) =
                drive_complete_pool_contribution(&server, &client, expected_lanes).await?;
            let initial_lanes_scheduled = initial_stats
                .lanes
                .iter()
                .filter(|lane| lane.bytes_scheduled > 0)
                .count();
            let initial_lanes_received = server_initial_stats
                .received_by_lane
                .iter()
                .filter(|lane| lane.unique_data_bytes > 0)
                .count();
            if initial_stats.lanes.len() != expected_lanes
                || initial_lanes_scheduled != expected_lanes
                || initial_lanes_received != expected_lanes
            {
                bail!(
                    "product pool expected {expected_lanes} lanes but authenticated {}, scheduled {initial_lanes_scheduled}, and received unique payload on {initial_lanes_received}",
                    initial_stats.lanes.len(),
                );
            }
            let replacement_lane = i2p_lane_id(client_pool, 2)?;
            let replacement_before = initial_stats
                .lanes
                .iter()
                .find(|lane| lane.id == replacement_lane)
                .context("product pool omitted replacement lane")?
                .bytes_scheduled;

            let server_root = server_pool.i2p_slot(2)?.manager.state_root().to_owned();
            let client_root = client_pool.i2p_slot(2)?.manager.state_root().to_owned();
            fs::write(
                server_root.join("anonssh-retention-marker"),
                b"server-slot-2",
            )?;
            fs::write(
                client_root.join("anonssh-retention-marker"),
                b"client-slot-2",
            )?;
            let (server_failed, client_failed) = tokio::join!(
                server.fail_lane(replacement_lane),
                client.session().fail_lane(replacement_lane),
            );
            server_failed?;
            client_failed?;
            let (server_stopped, client_stopped) =
                tokio::join!(server_pool.stop_i2p_slot(2), client_pool.stop_i2p_slot(2));
            server_stopped?;
            client_stopped?;

            let unaffected = b"healthy paths survive one failed slot".repeat(8_192);
            let received =
                transfer_stream(client.session(), &server, TrafficClass::Bulk, &unaffected).await?;
            if received != unaffected {
                bail!("degraded product-pool transfer mismatch");
            }

            let (server_restarted, client_restarted) = tokio::join!(
                server_pool.ensure_i2p_slot(2),
                client_pool.ensure_i2p_slot(2)
            );
            server_restarted?;
            client_restarted?;
            let state_roots_reused = server_root.join("anonssh-retention-marker").is_file()
                && client_root.join("anonssh-retention-marker").is_file()
                && server_pool.i2p_slot(2)?.manager.state_root() == server_root
                && client_pool.i2p_slot(2)?.manager.state_root() == client_root;
            if !state_roots_reused {
                bail!("I2P slot restart did not retain its state roots");
            }

            drive_scale_formation(&client, &server, initial_stats.lanes.len())
                .await
                .context("I2P pool repair did not converge under adaptive load")?;

            let replacement = vec![0x6d; PAYLOAD_BYTES];
            let received =
                transfer_stream(client.session(), &server, TrafficClass::Bulk, &replacement)
                    .await?;
            if received != replacement {
                bail!("repaired product-pool transfer mismatch");
            }
            let i2p_repaired_stats = wait_until_acknowledged(client.session()).await?;
            let replacement_snapshot = i2p_repaired_stats
                .lanes
                .iter()
                .find(|lane| lane.id == replacement_lane)
                .context("repaired product pool omitted replacement lane")?;
            if !replacement_snapshot.active
                || replacement_snapshot.bytes_scheduled <= replacement_before
            {
                bail!("repaired I2P lane did not return to active data service");
            }
            let i2p_replacement_lane_bytes =
                replacement_snapshot.bytes_scheduled - replacement_before;

            let failed_tor_slot = 2;
            let tor_lane = LaneId::new(failed_tor_slot)?;
            let tor_before = i2p_repaired_stats
                .lanes
                .iter()
                .find(|lane| lane.id == tor_lane)
                .context("product pool omitted the Tor replacement lane")?
                .bytes_scheduled;
            let server_tor_root = server_pool.tor_slot(failed_tor_slot)?.state_root().await?;
            let client_tor_root = client_pool.tor_slot(failed_tor_slot)?.state_root().await?;
            fs::write(
                server_tor_root.join("anonssh-retention-marker"),
                b"server-tor-slot-2",
            )?;
            fs::write(
                client_tor_root.join("anonssh-retention-marker"),
                b"client-tor-slot-2",
            )?;
            let (server_tor_failed, client_tor_failed) = tokio::join!(
                server.fail_lane(tor_lane),
                client.session().fail_lane(tor_lane),
            );
            server_tor_failed?;
            client_tor_failed?;
            let (server_tor_stopped, client_tor_stopped) = tokio::join!(
                server_pool.stop_tor_slot(failed_tor_slot),
                client_pool.stop_tor_slot(failed_tor_slot)
            );
            server_tor_stopped?;
            client_tor_stopped?;

            let tor_degraded = b"seven paths survive a failed Tor router".repeat(8_192);
            let received =
                transfer_stream(client.session(), &server, TrafficClass::Bulk, &tor_degraded)
                    .await?;
            if received != tor_degraded {
                bail!("Tor-degraded product-pool transfer mismatch");
            }

            drive_scale_formation(&client, &server, initial_stats.lanes.len())
                .await
                .context("Tor pool repair did not converge under adaptive load")?;
            let tor_state_roots_reused = server_tor_root.join("anonssh-retention-marker").is_file()
                && client_tor_root.join("anonssh-retention-marker").is_file()
                && server_pool.tor_slot(failed_tor_slot)?.state_root().await? == server_tor_root
                && client_pool.tor_slot(failed_tor_slot)?.state_root().await? == client_tor_root;
            if !tor_state_roots_reused {
                bail!("Tor restart did not retain its state roots");
            }

            let tor_bulk_payload = vec![0x74; 4 * PAYLOAD_BYTES];
            let received = transfer_stream(
                client.session(),
                &server,
                TrafficClass::Bulk,
                &tor_bulk_payload,
            )
            .await?;
            if received != tor_bulk_payload {
                bail!("repaired Tor bulk transfer mismatch");
            }
            let final_stats = wait_until_acknowledged(client.session()).await?;
            let server_final_stats = server.statistics().await?;
            let tor_after = final_stats
                .lanes
                .iter()
                .find(|lane| lane.id == tor_lane)
                .context("repaired pool omitted the Tor replacement lane")?
                .bytes_scheduled;
            let all_lanes_active = final_stats.lanes.iter().all(|lane| lane.active);
            let lanes_used = server_final_stats
                .received_by_lane
                .iter()
                .filter(|lane| lane.unique_data_bytes > 0)
                .count();
            if !all_lanes_active || tor_after <= tor_before || lanes_used != expected_lanes {
                bail!(
                    "repaired pool did not return all {expected_lanes} lanes to active data service"
                );
            }
            if final_stats.unacknowledged_bytes != 0 {
                bail!("repaired pool retained unacknowledged payload");
            }

            Ok::<_, anyhow::Error>(PoolRecoveryReport {
                schema: "anonssh.live-pool-recovery.v6",
                status: "ok",
                zero_lane_outage_observed: true,
                zero_lane_transfer_bytes: zero_lane.transfer_bytes,
                zero_lane_retransmitted_frames: zero_lane.retransmitted_frames,
                zero_lane_replayed_control_frames: zero_lane.replayed_control_frames,
                initial_lanes: initial_stats.lanes.len(),
                router_processes: 2 * (PRODUCTION_TOR_SLOTS + PRODUCTION_I2P_SLOTS),
                router_candidates_started,
                lanes_used,
                failed_i2p_slot: 2,
                i2p_degraded_transfer_bytes: unaffected.len(),
                i2p_replacement_transfer_bytes: replacement.len(),
                i2p_state_roots_reused: state_roots_reused,
                i2p_replacement_lane_bytes,
                tor_degraded_transfer_bytes: tor_degraded.len(),
                failed_tor_slot,
                tor_replacement_lane_bytes: tor_after - tor_before,
                tor_state_roots_reused,
                all_lanes_active,
                unacknowledged_bytes: final_stats.unacknowledged_bytes,
                server_router_progress: server_pool.progress_snapshot(),
                client_router_progress: client_pool.progress_snapshot(),
            })
        },
    )
    .await?;
    let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
    client_shutdown?;
    server_shutdown?;
    Ok(report)
}

struct ZeroLaneRecoveryEvidence {
    transfer_bytes: usize,
    retransmitted_frames: u64,
    replayed_control_frames: u64,
}

async fn prove_zero_lane_formation_repair(
    server: &BondSession,
    client: &ClientBondSession,
) -> Result<ZeroLaneRecoveryEvidence> {
    let client_control = client.session().control();
    let server_control = server.control();
    let (client_initial, server_initial) =
        tokio::try_join!(client_control.statistics(), server_control.statistics())?;
    let discovery = LaneId::new(1)?;
    let client_active = client_initial
        .lanes
        .iter()
        .filter(|lane| lane.active)
        .map(|lane| lane.id)
        .collect::<Vec<_>>();
    let server_active = server_initial
        .lanes
        .iter()
        .filter(|lane| lane.active)
        .map(|lane| lane.id)
        .collect::<Vec<_>>();
    if client_active != [discovery] || server_active != [discovery] {
        bail!(
            "zero-lane proof did not begin on only discovery lane 1: client={client_active:?}, server={server_active:?}"
        );
    }

    let payload = deterministic_scale_payload(8 * PAYLOAD_BYTES);
    let interrupt = async {
        let (client_before, server_before) = tokio::time::timeout(TRANSFER_TIMEOUT, async {
            loop {
                let (client_stats, server_stats) =
                    tokio::try_join!(client_control.statistics(), server_control.statistics())?;
                if client_stats.unacknowledged_bytes > 0 {
                    return Ok::<_, anyhow::Error>((client_stats, server_stats));
                }
                tokio::time::sleep(Duration::from_millis(10)).await;
            }
        })
        .await
        .context("zero-lane proof never observed unacknowledged payload")??;
        let (client_failed, server_failed) = tokio::join!(
            client_control.fail_lane(discovery),
            server_control.fail_lane(discovery)
        );
        client_failed?;
        server_failed?;
        let (client_zero, server_zero) =
            tokio::try_join!(client_control.statistics(), server_control.statistics())?;
        let client_zero_count = client_zero.lanes.iter().filter(|lane| lane.active).count();
        let server_zero_count = server_zero.lanes.iter().filter(|lane| lane.active).count();
        if client_zero_count != 0 || server_zero_count != 0 {
            bail!(
                "zero-lane proof retained active lanes after discovery failure: client={client_zero_count}, server={server_zero_count}"
            );
        }
        Ok::<_, anyhow::Error>((client_before, server_before))
    };
    let transfer = transfer_stream(client.session(), server, TrafficClass::Bulk, &payload);
    let (received, (client_before, server_before)) = tokio::try_join!(transfer, interrupt)?;
    if received != payload {
        bail!("zero-lane recovery transfer mismatch");
    }
    let client_after = wait_until_acknowledged(client.session()).await?;
    let server_after = server.statistics().await?;
    if client_after.unacknowledged_bytes != 0 {
        bail!("zero-lane recovery retained unacknowledged payload");
    }
    let retransmitted_frames = pair_counter_delta(
        &client_before,
        &server_before,
        &client_after,
        &server_after,
        |stats| stats.retransmitted_frames,
    );
    let replayed_control_frames = pair_counter_delta(
        &client_before,
        &server_before,
        &client_after,
        &server_after,
        |stats| stats.replayed_control_frames,
    );
    if retransmitted_frames == 0 || replayed_control_frames == 0 {
        bail!(
            "zero-lane recovery lacked retained-state evidence: retransmitted={retransmitted_frames}, replayed_controls={replayed_control_frames}"
        );
    }
    Ok(ZeroLaneRecoveryEvidence {
        transfer_bytes: payload.len(),
        retransmitted_frames,
        replayed_control_frames,
    })
}

async fn drive_complete_pool_contribution(
    server: &BondSession,
    client: &ClientBondSession,
    expected_lanes: usize,
) -> Result<(BondRuntimeStats, BondRuntimeStats)> {
    const MAX_ATTEMPTS: usize = 4;
    for attempt in 0..=MAX_ATTEMPTS {
        let (client_stats, server_stats) =
            wait_until_pair_acknowledged(client.session(), server).await?;
        let missing_scheduled = (1..=expected_lanes)
            .filter(|id| {
                client_stats
                    .lanes
                    .iter()
                    .find(|lane| lane.id.get() as usize == *id)
                    .is_none_or(|lane| lane.bytes_scheduled == 0)
            })
            .collect::<Vec<_>>();
        let missing_received = (1..=expected_lanes)
            .filter(|id| {
                server_stats
                    .received_by_lane
                    .iter()
                    .find(|lane| lane.id.get() as usize == *id)
                    .is_none_or(|lane| lane.unique_data_bytes == 0)
            })
            .collect::<Vec<_>>();
        let inactive = client_stats
            .lanes
            .iter()
            .chain(&server_stats.lanes)
            .filter(|lane| !lane.active)
            .map(|lane| lane.id.get())
            .collect::<BTreeSet<_>>();
        if client_stats.lanes.len() == expected_lanes
            && server_stats.lanes.len() == expected_lanes
            && missing_scheduled.is_empty()
            && missing_received.is_empty()
            && inactive.is_empty()
        {
            return Ok((client_stats, server_stats));
        }
        if attempt == MAX_ATTEMPTS {
            bail!(
                "product pool contribution did not converge after {MAX_ATTEMPTS} reprobes: missing_scheduled={missing_scheduled:?}, missing_received={missing_received:?}, inactive={inactive:?}"
            );
        }
        eprintln!(
            "anonssh-test: product pool contribution reprobe {}: missing_scheduled={missing_scheduled:?}, missing_received={missing_received:?}, inactive={inactive:?}",
            attempt + 1
        );
        wait_for_pool_repair(server, client, expected_lanes).await?;
        tokio::time::sleep(SchedulerConfig::default().bulk_reprobe_interval).await;
        let bulk = deterministic_scale_payload(PAYLOAD_BYTES);
        let received = transfer_stream(client.session(), server, TrafficClass::Bulk, &bulk).await?;
        if received != bulk {
            bail!("product pool contribution reprobe bulk mismatch");
        }
        let realtime = b"product pool contribution reprobe".repeat(2_048);
        let received =
            transfer_stream(client.session(), server, TrafficClass::Realtime, &realtime).await?;
        if received != realtime {
            bail!("product pool contribution reprobe real-time mismatch");
        }
    }
    unreachable!("bounded contribution loop returns or fails on its final attempt")
}

async fn wait_for_pool_repair(
    server: &BondSession,
    client: &ClientBondSession,
    expected_lanes: usize,
) -> Result<()> {
    let server_control = server.control();
    let client_control = client.session().control();
    let mut last_observation = String::from("no runtime observation completed");
    let mut last_reported = String::new();
    let convergence = tokio::time::timeout(TRANSFER_TIMEOUT, async {
        let mut ready_since = None;
        loop {
            let (server_stats, client_stats) =
                tokio::try_join!(server_control.statistics(), client_control.statistics())?;
            let transition = format!(
                "client={}; server={}",
                pool_health_transition(&client_stats),
                pool_health_transition(&server_stats)
            );
            if transition != last_reported {
                eprintln!("anonssh-test: pool convergence {transition}");
                last_reported = transition;
            }
            last_observation = format!(
                "client={}; server={}",
                pool_health_summary(&client_stats),
                pool_health_summary(&server_stats)
            );
            let server_ready = server_stats.lanes.len() == expected_lanes
                && server_stats.lanes.iter().all(|lane| lane.active);
            let client_ready = client_stats.lanes.len() == expected_lanes
                && client_stats.lanes.iter().all(|lane| lane.active);
            if server_ready && client_ready {
                let since = ready_since.get_or_insert_with(Instant::now);
                if since.elapsed() >= POOL_CONVERGENCE_STABILITY {
                    return Ok::<(), anyhow::Error>(());
                }
            } else {
                ready_since = None;
            }
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
    })
    .await;
    match convergence {
        Ok(result) => result?,
        Err(_) => bail!(
            "pool repair did not converge within fifteen minutes; last observation: {last_observation}"
        ),
    }
    Ok(())
}

fn pool_health_summary(stats: &BondRuntimeStats) -> String {
    let active = stats
        .lanes
        .iter()
        .filter(|lane| lane.active)
        .map(|lane| lane.id.get())
        .collect::<Vec<_>>();
    format!(
        "active={active:?}/{} unacknowledged={} liveness_failures={}",
        stats.lanes.len(),
        stats.unacknowledged_bytes,
        stats.liveness_failures
    )
}

fn pool_health_transition(stats: &BondRuntimeStats) -> String {
    let active = stats
        .lanes
        .iter()
        .filter(|lane| lane.active)
        .map(|lane| lane.id.get())
        .collect::<Vec<_>>();
    format!(
        "active={active:?}/{} liveness_failures={}",
        stats.lanes.len(),
        stats.liveness_failures
    )
}

fn pair_counter_delta(
    before_first: &BondRuntimeStats,
    before_second: &BondRuntimeStats,
    after_first: &BondRuntimeStats,
    after_second: &BondRuntimeStats,
    counter: impl Fn(&BondRuntimeStats) -> u64,
) -> u64 {
    counter(after_first)
        .saturating_add(counter(after_second))
        .saturating_sub(counter(before_first).saturating_add(counter(before_second)))
}

async fn with_pool_supervision<T>(
    ingress: &BondIngress,
    server: &BondSession,
    client_pool: &RouterPool,
    client: &ClientBondSession,
    mode: PoolSupervisionMode,
    operation: impl Future<Output = Result<T>>,
) -> Result<T> {
    let server_control = server.control();
    let client_maintenance = async {
        match mode {
            PoolSupervisionMode::Adaptive => client.maintain_lanes(client_pool).await,
            PoolSupervisionMode::FixedAll => client.maintain_all_lanes(client_pool).await,
        }
    };
    let topology_supervision = supervise_topology_requests(ingress, server, &server_control);
    tokio::select! {
        result = operation => result,
        result = client_maintenance => {
            result?;
            bail!("client pool supervision stopped before the operation completed")
        }
        result = topology_supervision => {
            result?;
            bail!("server topology supervision stopped before the operation completed")
        }
    }
}

#[derive(Clone, Copy)]
enum PoolSupervisionMode {
    Adaptive,
    FixedAll,
}

async fn supervise_topology_requests(
    ingress: &BondIngress,
    server: &BondSession,
    control: &BondSessionControl,
) -> Result<()> {
    loop {
        if server.protocol_version() >= anonssh_bond_tokio::BondProtocolVersion::V4 {
            tokio::select! {
                advertisement = server.accept_capabilities() => {
                    ingress
                        .apply_capability_request(control, advertisement?)
                        .await?;
                }
                advertisement = server.accept_topology() => {
                    ingress
                        .apply_topology_request(control, advertisement?)
                        .await?;
                }
            }
        } else {
            let advertisement = server
                .accept_topology()
                .await
                .context("bond topology request channel closed")?;
            ingress
                .apply_topology_request(control, advertisement)
                .await?;
        }
    }
}

async fn run_with_i2p_pool(
    first: &I2pdManager,
    second: &I2pdManager,
    first_sam: SocketAddr,
    second_sam: SocketAddr,
) -> Result<LiveBondReport> {
    let (first_ready, second_ready) = tokio::join!(first.ensure_running(), second.ensure_running());
    first_ready.context("failed to start I2P pool router 1")?;
    second_ready.context("failed to start I2P pool router 2")?;

    let password = Zeroizing::new(PASSWORD.to_owned());
    let client_identity = IdentityManager::derive_client_recovery_identity(&password, MACHINE_ID)?;
    let server_identity = IdentityManager::derive_server_recovery_identity(&password, MACHINE_ID)?;
    let first_identity = IdentityManager::derive_i2p_pool_identity(&password, MACHINE_ID, 1)?;
    let second_identity = IdentityManager::derive_i2p_pool_identity(&password, MACHINE_ID, 2)?;
    drop(password);
    if *client_identity.bond_session_key != *server_identity.bond_session_key {
        bail!("fresh client and server derived different bond keys");
    }
    if first_identity.destination == second_identity.destination {
        bail!("I2P pool slots derived the same destination");
    }

    let first_listener = SamListener::bind_zeroizing(
        first_sam.to_string(),
        format!("anonssh-pool-1-{}", std::process::id()),
        first_identity.private_key.clone(),
    )
    .await
    .context("failed to publish I2P pool slot 1")?;
    let second_listener = SamListener::bind_zeroizing(
        second_sam.to_string(),
        format!("anonssh-pool-2-{}", std::process::id()),
        second_identity.private_key.clone(),
    )
    .await
    .context("failed to publish I2P pool slot 2")?;
    let first_connector = SamConnector::new(first_sam.to_string(), None);
    let second_connector = SamConnector::new(second_sam.to_string(), None);

    let session_id = fresh_session_id()?;
    let bond_key = BondSessionKey::new(*client_identity.bond_session_key);
    let plan = i2p_pool_plan()?;
    let mut registry = LaneJoinRegistry::new(
        session_id,
        plan.iter()
            .map(|lane| (lane.config.id, lane.config.failure_domain)),
    )?;
    let mut client_lanes = Vec::with_capacity(plan.len());
    let mut server_lanes = Vec::with_capacity(plan.len());
    for lane in &plan {
        let pair = if lane.config.failure_domain.get() == 11 {
            establish_i2p_lane(
                *lane,
                session_id,
                &bond_key,
                &first_connector,
                &second_identity.destination,
                &second_listener,
            )
            .await
            .with_context(|| format!("failed I2P pool lane {}", lane.config.id.get()))?
        } else {
            establish_i2p_lane(
                *lane,
                session_id,
                &bond_key,
                &second_connector,
                &first_identity.destination,
                &first_listener,
            )
            .await
            .with_context(|| format!("failed I2P pool lane {}", lane.config.id.get()))?
        };
        registry.register(&pair.1)?;
        client_lanes.push(RuntimeLane::from_authenticated(lane.config, pair.0));
        server_lanes.push(RuntimeLane::from_authenticated(lane.config, pair.1));
    }
    if !registry.is_complete() {
        bail!("two-router I2P pool did not authenticate its complete lane plan");
    }
    run_transfer(
        session_id,
        &plan,
        client_lanes,
        server_lanes,
        "i2p-pool",
        RequiredDiversity::FailureDomains,
    )
    .await
}

async fn run_with_routers(
    i2pd: &I2pdManager,
    server_tor: &TorManager,
    client_tor: &TorManager,
    sam_addr: SocketAddr,
) -> Result<LiveBondReport> {
    let (i2p_ready, server_tor_ready, client_tor_ready) = tokio::join!(
        i2pd.ensure_running(),
        ensure_tor_running(server_tor, "server"),
        ensure_tor_running(client_tor, "client"),
    );
    i2p_ready.context("failed to start the bond I2P router")?;
    let server_socks = server_tor_ready.context("failed to start the server Tor router")?;
    let client_socks = client_tor_ready.context("failed to start the client Tor router")?;
    if server_socks == client_socks {
        bail!("live bond Tor routers unexpectedly share one SOCKS endpoint");
    }

    let password = Zeroizing::new(PASSWORD.to_owned());
    let client_identity = IdentityManager::derive_client_recovery_identity(&password, MACHINE_ID)?;
    let server_identity = IdentityManager::derive_server_recovery_identity(&password, MACHINE_ID)?;
    drop(password);
    if *client_identity.bond_session_key != *server_identity.bond_session_key {
        bail!("fresh client and server derived different bond keys");
    }
    let bond_key = BondSessionKey::new(*client_identity.bond_session_key);
    let session_id = fresh_session_id()?;
    let plan = mixed_plan()?;
    let mut registry = LaneJoinRegistry::new(
        session_id,
        plan.iter()
            .map(|lane| (lane.config.id, lane.config.failure_domain)),
    )?;

    let tor_ingress = TcpListener::bind("127.0.0.1:0").await?;
    let tor_target = tor_ingress.local_addr()?;
    let _tor_service = TorListener::new(server_tor.control_endpoint().await?)
        .listen_with_key(
            SERVICE_PORT,
            &tor_target.to_string(),
            &server_identity.tor.destination,
            &server_identity.tor.control_private_key,
        )
        .await
        .context("failed to publish the live bond Tor service")?;
    let i2p_listener = SamListener::bind_zeroizing(
        sam_addr.to_string(),
        format!("anonssh-bond-{}", std::process::id()),
        server_identity.i2p.private_key.clone(),
    )
    .await
    .context("failed to publish the live bond I2P service")?;

    let tor_connector = TorConnector::new(client_socks);
    let sam_connector = SamConnector::new(sam_addr.to_string(), None);
    let mut client_lanes = Vec::with_capacity(plan.len());
    let mut server_lanes = Vec::with_capacity(plan.len());
    for lane in &plan {
        let pair = match lane.provider {
            Provider::Tor => {
                establish_tor_lane(
                    *lane,
                    session_id,
                    &bond_key,
                    &tor_connector,
                    &server_identity.tor.destination,
                    &tor_ingress,
                )
                .await?
            }
            Provider::I2p => {
                establish_i2p_lane(
                    *lane,
                    session_id,
                    &bond_key,
                    &sam_connector,
                    &client_identity.i2p.destination,
                    &i2p_listener,
                )
                .await?
            }
        };
        registry.register(&pair.1)?;
        client_lanes.push(RuntimeLane::from_authenticated(lane.config, pair.0));
        server_lanes.push(RuntimeLane::from_authenticated(lane.config, pair.1));
    }
    if !registry.is_complete() {
        bail!("live bond did not authenticate its complete lane plan");
    }

    run_transfer(
        session_id,
        &plan,
        client_lanes,
        server_lanes,
        "tor-i2p",
        RequiredDiversity::Providers,
    )
    .await
}

async fn ensure_tor_running(manager: &TorManager, role: &str) -> Result<String> {
    let mut failures = Vec::new();
    for attempt in 1..=ROUTER_START_ATTEMPTS {
        match manager.ensure_running().await {
            Ok(endpoint) => return Ok(endpoint),
            Err(error) => failures.push(format!("attempt {attempt}: {error:#}")),
        }
    }
    bail!(
        "{role} Tor failed after {ROUTER_START_ATTEMPTS} attempts: {}",
        failures.join("; ")
    )
}

async fn establish_tor_lane(
    lane: PlannedLane,
    session_id: u64,
    key: &BondSessionKey,
    connector: &TorConnector,
    destination: &str,
    ingress: &TcpListener,
) -> Result<(
    anonssh_bond_tokio::AuthenticatedLane<TcpStream>,
    anonssh_bond_tokio::AuthenticatedLane<TcpStream>,
)> {
    let join = LaneJoin::new(session_id, lane.config.id, lane.config.failure_domain)?;
    let isolation = format!("anonssh-bond-lane-{}", lane.config.id.get());
    let client = async {
        let stream = connector
            .connect_isolated(destination, SERVICE_PORT, Some(&isolation))
            .await?;
        authenticate_client_lane(stream, key, join, TOR_HANDSHAKE_TIMEOUT)
            .await
            .map_err(anyhow::Error::from)
            .context("Tor client lane authentication failed")
    };
    let server = async {
        let (stream, _) = ingress.accept().await?;
        authenticate_server_lane(stream, key, join, TOR_HANDSHAKE_TIMEOUT)
            .await
            .map_err(anyhow::Error::from)
            .context("Tor server lane authentication failed")
    };
    let (client, server) = tokio::try_join!(client, server)?;
    Ok((client, server))
}

async fn establish_i2p_lane(
    lane: PlannedLane,
    session_id: u64,
    key: &BondSessionKey,
    connector: &SamConnector,
    destination: &str,
    listener: &SamListener,
) -> Result<(
    anonssh_bond_tokio::AuthenticatedLane<TcpStream>,
    anonssh_bond_tokio::AuthenticatedLane<TcpStream>,
)> {
    let mut failures = Vec::new();
    for attempt in 1..=I2P_LANE_ATTEMPTS {
        match establish_i2p_lane_once(lane, session_id, key, connector, destination, listener).await
        {
            Ok(pair) => return Ok(pair),
            Err(error) => failures.push(format!("attempt {attempt}: {error:#}")),
        }
    }
    bail!(
        "I2P lane {} failed after {} attempts: {}",
        lane.config.id.get(),
        I2P_LANE_ATTEMPTS,
        failures.join("; ")
    )
}

async fn establish_i2p_lane_once(
    lane: PlannedLane,
    session_id: u64,
    key: &BondSessionKey,
    connector: &SamConnector,
    destination: &str,
    listener: &SamListener,
) -> Result<(
    anonssh_bond_tokio::AuthenticatedLane<TcpStream>,
    anonssh_bond_tokio::AuthenticatedLane<TcpStream>,
)> {
    let join = LaneJoin::new(session_id, lane.config.id, lane.config.failure_domain)?;
    let client = async {
        let stream = connector
            .connect_with_initial_payload(destination, SERVICE_PORT, &[])
            .await?;
        authenticate_client_lane(stream, key, join, I2P_HANDSHAKE_TIMEOUT)
            .await
            .map_err(anyhow::Error::from)
            .context("I2P client lane authentication failed")
    };
    let server = async {
        let stream = listener.accept().await?;
        authenticate_server_lane(stream, key, join, I2P_HANDSHAKE_TIMEOUT)
            .await
            .map_err(anyhow::Error::from)
            .context("I2P server lane authentication failed")
    };
    let (client, server) = tokio::try_join!(client, server)?;
    Ok((client, server))
}

async fn run_transfer(
    session_id: u64,
    plan: &[PlannedLane],
    client_lanes: Vec<RuntimeLane>,
    server_lanes: Vec<RuntimeLane>,
    pool: &'static str,
    required_diversity: RequiredDiversity,
) -> Result<LiveBondReport> {
    let realtime_redundancy = matches!(required_diversity, RequiredDiversity::Providers);
    let config = BondRuntimeConfig {
        session_id,
        scheduler: SchedulerConfig {
            low_latency_lane_count: if realtime_redundancy { 2 } else { 1 },
            ..SchedulerConfig::default()
        },
        sender: SenderConfig {
            max_chunk_payload: 16 * 1024,
            bulk_chunk: anonssh_bond::BulkChunkConfig::default(),
            max_unacknowledged_bytes: 4 * 1024 * 1024,
            max_unacknowledged_chunks: 1_024,
            redundant_realtime: realtime_redundancy,
        },
        max_reorder_bytes_per_stream: 4 * 1024 * 1024,
        max_receive_streams: 8,
        stream_receive_window: 4 * 1024 * 1024,
        max_ack_ranges: 16,
        require_stream_open: true,
        retransmit_after: Duration::from_secs(30),
        retransmit_scan_interval: Duration::from_secs(1),
    };
    let client = BondSession::spawn(config, client_lanes, SessionRole::Dialer)?;
    let server = BondSession::spawn(config, server_lanes, SessionRole::Listener)?;
    let payload: Vec<u8> = (0..PAYLOAD_BYTES)
        .map(|index| ((index * 131 + 17) % 251) as u8)
        .collect();
    let payload_hash = format!("{:x}", Sha256::digest(&payload));
    let started = Instant::now();
    let received = transfer_stream(&client, &server, TrafficClass::Bulk, &payload).await?;
    if Sha256::digest(&received) != Sha256::digest(&payload) {
        bail!("live mixed-provider bond payload hash mismatch");
    }
    let bulk_stats = wait_until_acknowledged(&client).await?;
    let (providers_used, failure_domains_used) = bulk_diversity(plan, &bulk_stats);
    match required_diversity {
        RequiredDiversity::Providers if providers_used.len() < 2 => {
            bail!("live bulk transfer did not schedule payload on both Tor and I2P");
        }
        RequiredDiversity::FailureDomains if failure_domains_used.len() < 2 => {
            bail!("live bulk transfer did not use both I2P router failure domains");
        }
        _ => {}
    }

    let (realtime, final_stats, final_server_stats) =
        run_live_realtime_probe(&client, &server, plan, realtime_redundancy).await?;
    if final_stats.unacknowledged_bytes != 0 {
        bail!("live bond retained unacknowledged payload after transfer");
    }
    if final_server_stats.unacknowledged_bytes != 0 {
        bail!("live bond server retained unacknowledged payload after transfer");
    }

    let report = build_report(
        plan,
        final_stats,
        TransferSummary {
            pool,
            payload_bytes: payload.len(),
            payload_sha256: payload_hash,
            elapsed: started.elapsed(),
            bulk_providers_used: providers_used.len(),
            bulk_failure_domains_used: failure_domains_used.len(),
            realtime,
        },
    )?;
    let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
    client_shutdown?;
    server_shutdown?;
    Ok(report)
}

async fn run_live_realtime_probe(
    client: &BondSession,
    server: &BondSession,
    plan: &[PlannedLane],
    redundancy_enabled: bool,
) -> Result<(LiveRealtimeReport, BondRuntimeStats, BondRuntimeStats)> {
    let sample_count = if redundancy_enabled {
        LIVE_REALTIME_SAMPLES
    } else {
        SCALE_REALTIME_SAMPLES
    };
    let sample_interval = if redundancy_enabled {
        LIVE_REALTIME_INTERVAL
    } else {
        SCALE_REALTIME_INTERVAL
    };
    let (before_client, before_server) =
        tokio::try_join!(client.statistics(), server.statistics())?;
    let mut round_trip_micros =
        run_live_realtime_samples(client, server, 0, sample_count, sample_interval).await?;

    let (after_natural_client, after_natural_server) =
        wait_until_pair_acknowledged(client, server).await?;
    let client_protected = protected_lane_ids(&after_natural_client);
    let server_protected = protected_lane_ids(&after_natural_server);
    let expected_protected = if redundancy_enabled { 2 } else { 1 };
    if client_protected.len() != expected_protected || server_protected.len() != expected_protected
    {
        bail!(
            "live bond expected {expected_protected} protected lanes per endpoint, observed client={} server={}",
            client_protected.len(),
            server_protected.len()
        );
    }
    let client_providers = providers_for_lanes(plan, &client_protected)?;
    let server_providers = providers_for_lanes(plan, &server_protected)?;
    let expected_providers = if redundancy_enabled { 2 } else { 1 };
    if client_providers.len() != expected_providers || server_providers.len() != expected_providers
    {
        bail!(
            "live bond expected {expected_providers} protected providers per endpoint, observed client={} server={}",
            client_providers.len(),
            server_providers.len()
        );
    }
    if redundancy_enabled {
        for provider in [Provider::Tor, Provider::I2p] {
            let planned = plan.iter().filter(|lane| lane.provider == provider).count();
            let protected = client_protected
                .iter()
                .filter(|lane_id| {
                    plan.iter()
                        .any(|lane| lane.config.id.get() == **lane_id && lane.provider == provider)
                })
                .count();
            if planned <= protected {
                bail!("live mixed bond left no bulk-capable {provider:?} lane");
            }
        }
    }

    let natural_tor_acknowledged_bytes = acknowledged_bytes_for_provider(
        plan,
        &before_client,
        &after_natural_client,
        Provider::Tor,
    )?
    .saturating_add(acknowledged_bytes_for_provider(
        plan,
        &before_server,
        &after_natural_server,
        Provider::Tor,
    )?);
    let natural_i2p_acknowledged_bytes = acknowledged_bytes_for_provider(
        plan,
        &before_client,
        &after_natural_client,
        Provider::I2p,
    )?
    .saturating_add(acknowledged_bytes_for_provider(
        plan,
        &before_server,
        &after_natural_server,
        Provider::I2p,
    )?);
    let natural_winner_providers = usize::from(natural_tor_acknowledged_bytes > 0)
        + usize::from(natural_i2p_acknowledged_bytes > 0);
    if natural_winner_providers == 0 {
        bail!("live bond did not attribute a natural real-time winner");
    }
    let expected_acknowledged_bytes = u64::try_from(sample_count)
        .unwrap_or(u64::MAX)
        .saturating_mul(64)
        .saturating_mul(2);
    if natural_tor_acknowledged_bytes.saturating_add(natural_i2p_acknowledged_bytes)
        != expected_acknowledged_bytes
    {
        bail!(
            "live bond acknowledged {} of {expected_acknowledged_bytes} real-time bytes",
            natural_tor_acknowledged_bytes.saturating_add(natural_i2p_acknowledged_bytes)
        );
    }

    let (
        forced_outage_provider,
        outage_probe_samples,
        outage_tor_acknowledged_bytes,
        outage_i2p_acknowledged_bytes,
        after_client,
        after_server,
    ) = if redundancy_enabled {
        let outage_provider = if natural_tor_acknowledged_bytes >= natural_i2p_acknowledged_bytes {
            Provider::Tor
        } else {
            Provider::I2p
        };
        fail_provider_lanes(client, server, plan, outage_provider).await?;
        let (before_outage_client, before_outage_server) =
            tokio::try_join!(client.statistics(), server.statistics())?;
        run_live_realtime_samples(
            client,
            server,
            1,
            SCALE_REALTIME_SAMPLES,
            SCALE_REALTIME_INTERVAL,
        )
        .await?;
        let (after_outage_client, after_outage_server) =
            wait_until_pair_acknowledged(client, server).await?;
        let outage_tor = acknowledged_bytes_for_provider(
            plan,
            &before_outage_client,
            &after_outage_client,
            Provider::Tor,
        )?
        .saturating_add(acknowledged_bytes_for_provider(
            plan,
            &before_outage_server,
            &after_outage_server,
            Provider::Tor,
        )?);
        let outage_i2p = acknowledged_bytes_for_provider(
            plan,
            &before_outage_client,
            &after_outage_client,
            Provider::I2p,
        )?
        .saturating_add(acknowledged_bytes_for_provider(
            plan,
            &before_outage_server,
            &after_outage_server,
            Provider::I2p,
        )?);
        let expected_outage_bytes = u64::try_from(SCALE_REALTIME_SAMPLES)
            .unwrap_or(u64::MAX)
            .saturating_mul(64)
            .saturating_mul(2);
        let (failed_bytes, surviving_bytes) = match outage_provider {
            Provider::Tor => (outage_tor, outage_i2p),
            Provider::I2p => (outage_i2p, outage_tor),
        };
        if failed_bytes != 0 || surviving_bytes != expected_outage_bytes {
            bail!(
                "live bond {outage_provider:?} outage probe attributed failed={failed_bytes} surviving={surviving_bytes} expected={expected_outage_bytes} bytes"
            );
        }
        (
            Some(outage_provider),
            SCALE_REALTIME_SAMPLES,
            outage_tor,
            outage_i2p,
            after_outage_client,
            after_outage_server,
        )
    } else {
        (None, 0, 0, 0, after_natural_client, after_natural_server)
    };
    let tor_acknowledged_bytes =
        natural_tor_acknowledged_bytes.saturating_add(outage_tor_acknowledged_bytes);
    let i2p_acknowledged_bytes =
        natural_i2p_acknowledged_bytes.saturating_add(outage_i2p_acknowledged_bytes);
    let winner_providers =
        usize::from(tor_acknowledged_bytes > 0) + usize::from(i2p_acknowledged_bytes > 0);
    if winner_providers != expected_providers {
        bail!(
            "live bond expected {expected_providers} total real-time winner providers, observed Tor={tor_acknowledged_bytes} bytes I2P={i2p_acknowledged_bytes} bytes"
        );
    }

    let redundant_frames = after_client
        .redundant_realtime_frames
        .saturating_sub(before_client.redundant_realtime_frames)
        .saturating_add(
            after_server
                .redundant_realtime_frames
                .saturating_sub(before_server.redundant_realtime_frames),
        );
    let dropped_redundant_frames = after_client
        .dropped_redundant_realtime_frames
        .saturating_sub(before_client.dropped_redundant_realtime_frames)
        .saturating_add(
            after_server
                .dropped_redundant_realtime_frames
                .saturating_sub(before_server.dropped_redundant_realtime_frames),
        );
    let new_data_frames = after_client
        .new_data_frames
        .saturating_sub(before_client.new_data_frames)
        .saturating_add(
            after_server
                .new_data_frames
                .saturating_sub(before_server.new_data_frames),
        );
    let shadow_attempts = redundant_frames.saturating_add(dropped_redundant_frames);
    if redundancy_enabled && (shadow_attempts == 0 || shadow_attempts > new_data_frames) {
        bail!(
            "live bond accounted for {shadow_attempts} shadow attempts across {new_data_frames} real-time data frames"
        );
    }
    if !redundancy_enabled && shadow_attempts != 0 {
        bail!("live bond emitted {shadow_attempts} shadows while redundancy was disabled");
    }
    let shadow_coverage_basis_points = if new_data_frames == 0 {
        0
    } else {
        u64::try_from(
            u128::from(shadow_attempts).saturating_mul(10_000) / u128::from(new_data_frames),
        )
        .unwrap_or(u64::MAX)
    };

    round_trip_micros.sort_unstable();
    let report = LiveRealtimeReport {
        redundancy_enabled,
        samples: sample_count,
        sample_interval_millis: u64::try_from(sample_interval.as_millis()).unwrap_or(u64::MAX),
        round_trip_micros_p50: scale_percentile(&round_trip_micros, 50)?,
        round_trip_micros_p95: scale_percentile(&round_trip_micros, 95)?,
        round_trip_micros_max: *round_trip_micros
            .last()
            .context("live bond produced no real-time latency samples")?,
        client_protected_lanes: client_protected.into_iter().collect(),
        server_protected_lanes: server_protected.into_iter().collect(),
        protected_providers: expected_providers,
        natural_winner_providers,
        natural_tor_acknowledged_bytes,
        natural_i2p_acknowledged_bytes,
        forced_outage_provider,
        outage_probe_samples,
        winner_providers,
        tor_acknowledged_bytes,
        i2p_acknowledged_bytes,
        new_data_frames,
        redundant_frames,
        dropped_redundant_frames,
        shadow_coverage_basis_points,
    };
    Ok((report, after_client, after_server))
}

async fn run_live_realtime_samples(
    client: &BondSession,
    server: &BondSession,
    round: usize,
    sample_count: usize,
    sample_interval: Duration,
) -> Result<Vec<u64>> {
    let outbound = client.open_stream(TrafficClass::Realtime).await?;
    let inbound = server.accept_stream().await?;
    if outbound.stream_id() != inbound.stream_id()
        || inbound.traffic_class() != TrafficClass::Realtime
    {
        bail!("live bond accepted the wrong real-time stream");
    }
    let active = AtomicBool::new(true);
    let progress = ScaleRoundProgress::new(0);
    let latencies = tokio::time::timeout(
        TRANSFER_TIMEOUT,
        run_scale_realtime_samples(
            outbound,
            inbound,
            RealtimeSampleConfig {
                round,
                sample_count,
                sample_interval,
                initial_echo_delay: Duration::ZERO,
            },
            &active,
            &progress,
        ),
    )
    .await
    .with_context(|| {
        format!(
            "live bond real-time echo probe exceeded its deadline: {}",
            progress.summary()
        )
    })??;
    if latencies.len() != sample_count {
        bail!(
            "live bond completed {} of {sample_count} real-time echoes",
            latencies.len()
        );
    }
    Ok(latencies)
}

async fn fail_provider_lanes(
    client: &BondSession,
    server: &BondSession,
    plan: &[PlannedLane],
    provider: Provider,
) -> Result<()> {
    let lane_ids = plan
        .iter()
        .filter(|lane| lane.provider == provider)
        .map(|lane| lane.config.id)
        .collect::<Vec<_>>();
    if lane_ids.is_empty() {
        bail!("live bond cannot fail absent provider {provider:?}");
    }
    for lane_id in lane_ids {
        let (client_result, server_result) =
            tokio::join!(client.fail_lane(lane_id), server.fail_lane(lane_id));
        client_result.with_context(|| {
            format!(
                "failed to remove client {provider:?} lane {}",
                lane_id.get()
            )
        })?;
        server_result.with_context(|| {
            format!(
                "failed to remove server {provider:?} lane {}",
                lane_id.get()
            )
        })?;
    }
    Ok(())
}

fn protected_lane_ids(stats: &BondRuntimeStats) -> BTreeSet<u32> {
    stats
        .lanes
        .iter()
        .filter(|lane| lane.reserved_for_low_latency)
        .map(|lane| lane.id.get())
        .collect()
}

fn providers_for_lanes(
    plan: &[PlannedLane],
    lane_ids: &BTreeSet<u32>,
) -> Result<BTreeSet<Provider>> {
    lane_ids
        .iter()
        .map(|lane_id| {
            plan.iter()
                .find(|lane| lane.config.id.get() == *lane_id)
                .map(|lane| lane.provider)
                .with_context(|| format!("live bond plan omitted protected lane {lane_id}"))
        })
        .collect()
}

fn acknowledged_bytes_for_provider(
    plan: &[PlannedLane],
    before: &BondRuntimeStats,
    after: &BondRuntimeStats,
    provider: Provider,
) -> Result<u64> {
    plan.iter()
        .filter(|lane| lane.provider == provider)
        .try_fold(0_u64, |total, lane| {
            Ok(total.saturating_add(acknowledged_bytes_for_lane(
                before,
                after,
                lane.config.id.get(),
            )?))
        })
}

async fn transfer_stream(
    client: &BondSession,
    server: &BondSession,
    class: TrafficClass,
    payload: &[u8],
) -> Result<Vec<u8>> {
    tokio::time::timeout(TRANSFER_TIMEOUT, async {
        let mut outbound = client.open_stream(class).await?;
        let mut inbound = server.accept_stream().await?;
        if outbound.stream_id() != inbound.stream_id() || inbound.traffic_class() != class {
            bail!("bond session accepted the wrong logical stream");
        }
        let send = async {
            outbound.write_all(payload).await?;
            outbound.shutdown().await
        };
        let receive = async {
            let mut received = Vec::with_capacity(payload.len());
            inbound.read_to_end(&mut received).await?;
            inbound.shutdown().await?;
            Ok::<_, std::io::Error>(received)
        };
        let ((), received) = tokio::try_join!(send, receive)?;
        if received.len() != payload.len() {
            bail!("bond stream delivered an unexpected payload length");
        }
        Ok(received)
    })
    .await
    .context("live bond payload exceeded its 15-minute deadline")?
}

async fn drive_scale_formation(
    client: &ClientBondSession,
    server: &BondSession,
    expected_lanes: usize,
) -> Result<u64> {
    tokio::time::timeout(SCALE_FORMATION_OPERATION_TIMEOUT, async {
        let mut outbound = client
            .session()
            .open_stream(TrafficClass::Bulk)
            .await
            .context("failed to open scale formation pressure stream")?;
        let mut inbound = server
            .accept_stream()
            .await
            .context("failed to accept scale formation pressure stream")?;
        if outbound.stream_id() != inbound.stream_id()
            || inbound.traffic_class() != TrafficClass::Bulk
        {
            bail!("scale formation accepted the wrong pressure stream");
        }

        let (pressure_stop, pressure_stop_rx) = watch::channel(false);
        let pressure = async {
            let chunk = deterministic_scale_payload(64 * 1024);
            let send = async {
                let sent =
                    write_scale_formation_pressure(&mut outbound, pressure_stop_rx, &chunk).await?;
                outbound
                    .shutdown()
                    .await
                    .context("scale formation pressure sender shutdown failed")?;
                Ok::<_, anyhow::Error>(sent)
            };
            let receive = async {
                let mut received = 0_u64;
                let mut buffer = [0_u8; 64 * 1024];
                loop {
                    let read = inbound
                        .read(&mut buffer)
                        .await
                        .context("scale formation pressure read failed")?;
                    if read == 0 {
                        break;
                    }
                    received = received.saturating_add(read as u64);
                }
                inbound
                    .shutdown()
                    .await
                    .context("scale formation pressure receiver shutdown failed")?;
                Ok::<_, anyhow::Error>(received)
            };
            let (sent, received) = tokio::try_join!(send, receive)?;
            if sent != received {
                bail!("scale formation delivered {received} of {sent} pressure bytes");
            }
            Ok::<_, anyhow::Error>(sent)
        };
        let convergence = async {
            let result = wait_for_pool_repair(server, client, expected_lanes)
            .await
            .context("adaptive scale topology did not converge under pressure");
            pressure_stop
                .send(true)
                .context("scale formation pressure stop receiver disappeared")?;
            result
        };
        match tokio::try_join!(pressure, convergence) {
            Ok((formation_load_bytes, ())) => Ok(formation_load_bytes),
            Err(error) => {
                let client_status = client
                    .session()
                    .statistics()
                    .await
                    .map(|stats| {
                        (
                            stats.lanes.iter().filter(|lane| lane.active).count(),
                            stats.unacknowledged_bytes,
                            stats.liveness_failures,
                        )
                    })
                    .map_err(|status| status.to_string());
                let server_status = server
                    .statistics()
                    .await
                    .map(|stats| {
                        (
                            stats.lanes.iter().filter(|lane| lane.active).count(),
                            stats.unacknowledged_bytes,
                            stats.liveness_failures,
                        )
                    })
                    .map_err(|status| status.to_string());
                bail!(
                    "scale formation failed: {error:#}; client(active, unacknowledged, liveness)={client_status:?}; server(active, unacknowledged, liveness)={server_status:?}"
                )
            }
        }
    })
    .await
    .context(
        "adaptive scale formation exceeded its 15-minute convergence plus cleanup deadline",
    )?
}

async fn write_scale_formation_pressure<W>(
    outbound: &mut W,
    mut stop: watch::Receiver<bool>,
    chunk: &[u8],
) -> Result<u64>
where
    W: AsyncWrite + Unpin,
{
    if chunk.is_empty() {
        bail!("scale formation pressure chunk is empty");
    }
    let mut sent = 0_u64;
    let mut bytes_since_yield = 0_usize;
    let mut chunk_offset = 0_usize;
    loop {
        if *stop.borrow() {
            return Ok(sent);
        }
        tokio::select! {
            biased;
            changed = stop.changed() => {
                changed.context("scale formation pressure stop sender disappeared")?;
                continue;
            }
            result = outbound.write(&chunk[chunk_offset..]) => {
                let written = result.context("scale formation pressure write failed")?;
                if written == 0 {
                    bail!("scale formation pressure writer stopped accepting bytes");
                }
                sent = sent.saturating_add(written as u64);
                bytes_since_yield = bytes_since_yield.saturating_add(written);
                chunk_offset += written;
                if chunk_offset == chunk.len() {
                    chunk_offset = 0;
                }
            }
        }
        if bytes_since_yield >= SCALE_PRESSURE_YIELD_BYTES {
            bytes_since_yield %= SCALE_PRESSURE_YIELD_BYTES;
            tokio::task::yield_now().await;
        }
        if chunk_offset == 0 {
            tokio::select! {
                biased;
                changed = stop.changed() => {
                    changed.context("scale formation pressure stop sender disappeared")?;
                }
                () = tokio::time::sleep(SCALE_PRESSURE_INTERVAL) => {}
            }
        }
    }
}

#[derive(Clone, Copy)]
struct ScaleRealtimeTiming {
    sample: usize,
    started: Instant,
    active_before: bool,
}

#[derive(Clone, Copy)]
struct RealtimeSampleConfig {
    round: usize,
    sample_count: usize,
    sample_interval: Duration,
    initial_echo_delay: Duration,
}

async fn run_scale_realtime_samples<Client, Server>(
    client_stream: Client,
    server_stream: Server,
    config: RealtimeSampleConfig,
    bulk_active: &AtomicBool,
    progress: &ScaleRoundProgress,
) -> Result<Vec<u64>>
where
    Client: AsyncRead + AsyncWrite + Unpin,
    Server: AsyncRead + AsyncWrite + Unpin,
{
    if config.sample_count == 0 {
        bail!("real-time sample count must be nonzero");
    }
    let (mut client_reader, mut client_writer) = tokio::io::split(client_stream);
    let (mut server_reader, mut server_writer) = tokio::io::split(server_stream);
    let (timing_sender, mut timing_receiver) = mpsc::channel(config.sample_count);

    let requests = async move {
        let mut cadence = tokio::time::interval(config.sample_interval);
        cadence.set_missed_tick_behavior(tokio::time::MissedTickBehavior::Burst);
        for sample in 0..config.sample_count {
            cadence.tick().await;
            let token = scale_realtime_token(config.round, sample);
            let timing = ScaleRealtimeTiming {
                sample,
                started: Instant::now(),
                active_before: bulk_active.load(Ordering::Acquire),
            };
            client_writer.write_all(&token).await?;
            client_writer.flush().await?;
            progress
                .realtime_requests_started
                .store(sample + 1, Ordering::Release);
            timing_sender
                .send(timing)
                .await
                .context("scale real-time response observer stopped")?;
        }
        client_writer.shutdown().await?;
        progress
            .realtime_request_closed
            .store(true, Ordering::Release);
        Ok::<_, anyhow::Error>(())
    };

    let echoes = async {
        for sample in 0..config.sample_count {
            let expected = scale_realtime_token(config.round, sample);
            let mut received = [0_u8; 64];
            server_reader.read_exact(&mut received).await?;
            if received != expected {
                bail!("scale round {} real-time request mismatch", config.round);
            }
            if sample == 0 && !config.initial_echo_delay.is_zero() {
                tokio::time::sleep(config.initial_echo_delay).await;
            }
            server_writer.write_all(&received).await?;
            server_writer.flush().await?;
        }
        let mut trailing = Vec::new();
        server_reader.read_to_end(&mut trailing).await?;
        progress.realtime_request_eof.store(true, Ordering::Release);
        if !trailing.is_empty() {
            bail!(
                "scale round {} real-time stream had trailing request bytes",
                config.round
            );
        }
        server_writer.shutdown().await?;
        progress
            .realtime_response_closed
            .store(true, Ordering::Release);
        Ok::<_, anyhow::Error>(())
    };

    let responses = async {
        let mut overlapping_latencies = Vec::with_capacity(config.sample_count);
        for sample in 0..config.sample_count {
            let timing = timing_receiver
                .recv()
                .await
                .context("scale real-time request observer stopped")?;
            if timing.sample != sample {
                bail!(
                    "scale round {} real-time timing order changed",
                    config.round
                );
            }
            let expected = scale_realtime_token(config.round, sample);
            let mut echoed = [0_u8; 64];
            client_reader.read_exact(&mut echoed).await?;
            if echoed != expected {
                bail!("scale round {} real-time echo mismatch", config.round);
            }
            progress
                .realtime_echoes
                .store(sample + 1, Ordering::Release);
            if timing.active_before {
                overlapping_latencies
                    .push(u64::try_from(timing.started.elapsed().as_micros()).unwrap_or(u64::MAX));
            }
        }
        if timing_receiver.recv().await.is_some() {
            bail!(
                "scale round {} produced excess real-time timing metadata",
                config.round
            );
        }
        let mut trailing = Vec::new();
        client_reader.read_to_end(&mut trailing).await?;
        progress
            .realtime_response_eof
            .store(true, Ordering::Release);
        if !trailing.is_empty() {
            bail!(
                "scale round {} real-time stream had trailing response bytes",
                config.round
            );
        }
        Ok::<_, anyhow::Error>(overlapping_latencies)
    };

    let ((), (), latencies) = tokio::try_join!(requests, echoes, responses)?;
    Ok(latencies)
}

async fn run_scale_round(
    client: &BondSession,
    server: &BondSession,
    payload: &[u8],
    round: usize,
    direction: ScaleDirection,
) -> Result<ScaleRoundReport> {
    run_scale_round_with_interval(
        client,
        server,
        payload,
        round,
        direction,
        SCALE_REALTIME_INTERVAL,
        None,
    )
    .await
}

async fn run_scale_round_with_interval(
    client: &BondSession,
    server: &BondSession,
    payload: &[u8],
    round: usize,
    direction: ScaleDirection,
    realtime_interval: Duration,
    required_overlap_samples: Option<usize>,
) -> Result<ScaleRoundReport> {
    if realtime_interval.is_zero() {
        bail!("scale real-time interval must be nonzero");
    }
    let progress = ScaleRoundProgress::new(direction.bulk_senders());
    let result = tokio::time::timeout(TRANSFER_TIMEOUT, async {
        let before_client = client.statistics().await?;
        let before_server = server.statistics().await?;
        let mut client_protected_lanes = BTreeSet::new();
        let mut server_protected_lanes = BTreeSet::new();
        observe_protected_lanes(&before_client, &mut client_protected_lanes);
        observe_protected_lanes(&before_server, &mut server_protected_lanes);
        let client_control = client.control();
        let server_control = server.control();
        let client_to_server = if direction.includes_client_to_server() {
            Some(open_scale_bulk_stream(client, server, "client-to-server").await?)
        } else {
            None
        };
        let server_to_client = if direction.includes_server_to_client() {
            Some(open_scale_bulk_stream(server, client, "server-to-client").await?)
        } else {
            None
        };
        let reverse_payload = deterministic_scale_payload_with_salt(payload.len(), 0xa7);
        let realtime_outbound = client.open_stream(TrafficClass::Realtime).await?;
        let realtime_inbound = server.accept_stream().await?;
        if realtime_outbound.stream_id() != realtime_inbound.stream_id()
            || realtime_inbound.traffic_class() != TrafficClass::Realtime
        {
            bail!("scale campaign accepted the wrong real-time stream");
        }

        let bulk_active = AtomicBool::new(true);
        let bulk = async {
            let started = Instant::now();
            match (client_to_server, server_to_client) {
                (Some((outbound, inbound)), None) => {
                    transfer_scale_bulk_stream(
                        outbound,
                        inbound,
                        payload,
                        &progress,
                        "client-to-server",
                    )
                    .await?;
                }
                (None, Some((outbound, inbound))) => {
                    transfer_scale_bulk_stream(
                        outbound,
                        inbound,
                        &reverse_payload,
                        &progress,
                        "server-to-client",
                    )
                    .await?;
                }
                (
                    Some((client_outbound, server_inbound)),
                    Some((server_outbound, client_inbound)),
                ) => {
                    tokio::try_join!(
                        transfer_scale_bulk_stream(
                            client_outbound,
                            server_inbound,
                            payload,
                            &progress,
                            "client-to-server",
                        ),
                        transfer_scale_bulk_stream(
                            server_outbound,
                            client_inbound,
                            &reverse_payload,
                            &progress,
                            "server-to-client",
                        ),
                    )?;
                }
                (None, None) => bail!("scale round has no bulk sender"),
            }
            let elapsed = started.elapsed();
            bulk_active.store(false, Ordering::Release);
            Ok::<_, anyhow::Error>(elapsed)
        };
        let telemetry = async {
            let mut max_queue_delay_micros = 0_u64;
            loop {
                let (client_stats, server_stats) =
                    tokio::try_join!(client_control.statistics(), server_control.statistics())?;
                observe_protected_lanes(&client_stats, &mut client_protected_lanes);
                observe_protected_lanes(&server_stats, &mut server_protected_lanes);
                max_queue_delay_micros = max_queue_delay_micros
                    .max(max_lane_queue_delay(&client_stats))
                    .max(max_lane_queue_delay(&server_stats));
                if !bulk_active.load(Ordering::Acquire) {
                    progress.telemetry_complete.store(true, Ordering::Release);
                    return Ok::<_, anyhow::Error>((
                        max_queue_delay_micros,
                        client_protected_lanes,
                        server_protected_lanes,
                    ));
                }
                tokio::time::sleep(Duration::from_millis(100)).await;
            }
        };
        let realtime = run_scale_realtime_samples(
            realtime_outbound,
            realtime_inbound,
            RealtimeSampleConfig {
                round,
                sample_count: SCALE_REALTIME_SAMPLES,
                sample_interval: realtime_interval,
                initial_echo_delay: Duration::ZERO,
            },
            &bulk_active,
            &progress,
        );
        let (
            elapsed,
            mut realtime_round_trip_micros,
            (mut max_queue_delay_micros, mut client_protected_lanes, mut server_protected_lanes),
        ) = tokio::try_join!(bulk, realtime, telemetry)?;
        let minimum_overlap_samples = required_overlap_samples
            .unwrap_or_else(|| minimum_scale_overlap_samples(direction, payload.len()));
        if minimum_overlap_samples == 0 || minimum_overlap_samples > SCALE_REALTIME_SAMPLES {
            bail!("scale round has an invalid real-time overlap requirement");
        }
        if realtime_round_trip_micros.len() < minimum_overlap_samples {
            bail!(
                "scale round {round} began only {} of the required {minimum_overlap_samples} real-time samples under bulk",
                realtime_round_trip_micros.len(),
            );
        }
        let (after_client, after_server) = wait_until_pair_acknowledged(client, server).await?;
        progress
            .acknowledgement_drain_complete
            .store(true, Ordering::Release);
        observe_protected_lanes(&after_client, &mut client_protected_lanes);
        observe_protected_lanes(&after_server, &mut server_protected_lanes);
        let mut protected_lanes = BTreeSet::new();
        let mut protected_lane_acknowledged_bytes = 0_u64;
        if direction.includes_client_to_server() {
            protected_lanes.extend(client_protected_lanes.iter().copied());
            protected_lane_acknowledged_bytes =
                protected_lane_acknowledged_bytes.saturating_add(acknowledged_bytes_for_lanes(
                    &before_client,
                    &after_client,
                    &client_protected_lanes,
                )?);
        }
        if direction.includes_server_to_client() {
            protected_lanes.extend(server_protected_lanes.iter().copied());
            protected_lane_acknowledged_bytes =
                protected_lane_acknowledged_bytes.saturating_add(acknowledged_bytes_for_lanes(
                    &before_server,
                    &after_server,
                    &server_protected_lanes,
                )?);
        }
        if protected_lane_acknowledged_bytes == 0 {
            bail!("scale round {round} did not use its observed protected pool");
        }
        max_queue_delay_micros = max_queue_delay_micros
            .max(max_lane_queue_delay(&after_client))
            .max(max_lane_queue_delay(&after_server));
        let retransmitted_frames = after_client
            .retransmitted_frames
            .saturating_add(after_server.retransmitted_frames)
            .saturating_sub(
                before_client
                    .retransmitted_frames
                    .saturating_add(before_server.retransmitted_frames),
            );
        let liveness_failures = after_client
            .liveness_failures
            .saturating_add(after_server.liveness_failures)
            .saturating_sub(
                before_client
                    .liveness_failures
                    .saturating_add(before_server.liveness_failures),
            );
        let replayed_control_frames = after_client
            .replayed_control_frames
            .saturating_add(after_server.replayed_control_frames)
            .saturating_sub(
                before_client
                    .replayed_control_frames
                    .saturating_add(before_server.replayed_control_frames),
            );
        realtime_round_trip_micros.sort_unstable();
        let client_to_server_sha256 = direction
            .includes_client_to_server()
            .then(|| format!("{:x}", Sha256::digest(payload)));
        let server_to_client_sha256 = direction
            .includes_server_to_client()
            .then(|| format!("{:x}", Sha256::digest(&reverse_payload)));
        let transferred_payload_bytes = payload
            .len()
            .checked_mul(direction.bulk_senders())
            .context("scale round payload byte count overflow")?;
        let elapsed_nanos = elapsed.as_nanos().max(1);
        let goodput_bps = u64::try_from(
            (transferred_payload_bytes as u128)
                .saturating_mul(8)
                .saturating_mul(1_000_000_000)
                / elapsed_nanos,
        )
        .unwrap_or(u64::MAX);
        Ok(ScaleRoundReport {
            round,
            direction,
            payload_bytes: transferred_payload_bytes,
            payload_bytes_per_direction: payload.len(),
            client_to_server_sha256,
            server_to_client_sha256,
            elapsed_millis: elapsed.as_millis(),
            goodput_bps,
            realtime_round_trip_micros_p50: scale_percentile(&realtime_round_trip_micros, 50)?,
            realtime_round_trip_micros_p95: scale_percentile(&realtime_round_trip_micros, 95)?,
            realtime_round_trip_micros_max: *realtime_round_trip_micros
                .last()
                .context("scale round produced no overlapping real-time samples")?,
            bulk_start_overlap_samples: realtime_round_trip_micros.len(),
            protected_lanes_observed: protected_lanes.iter().copied().collect(),
            protected_lane_acknowledged_bytes,
            realtime_round_trip_micros,
            max_queue_delay_micros,
            retransmitted_frames,
            liveness_failures,
            replayed_control_frames,
        })
    })
    .await;
    match result {
        Ok(result) => result,
        Err(_) => bail!(
            "live bond scale round exceeded its 15-minute deadline: {}",
            progress.summary()
        ),
    }
}

async fn open_scale_bulk_stream(
    sender: &BondSession,
    receiver: &BondSession,
    label: &str,
) -> Result<(BondedStream, BondedStream)> {
    let outbound = sender.open_stream(TrafficClass::Bulk).await?;
    let inbound = receiver.accept_stream().await?;
    if outbound.stream_id() != inbound.stream_id() || inbound.traffic_class() != TrafficClass::Bulk
    {
        bail!("scale campaign accepted the wrong {label} bulk stream");
    }
    Ok((outbound, inbound))
}

async fn transfer_scale_bulk_stream(
    mut outbound: BondedStream,
    mut inbound: BondedStream,
    payload: &[u8],
    progress: &ScaleRoundProgress,
    label: &str,
) -> Result<()> {
    let send = async {
        outbound.write_all(payload).await?;
        progress
            .bulk_payloads_written
            .fetch_add(1, Ordering::AcqRel);
        outbound.shutdown().await?;
        progress.bulk_writes_closed.fetch_add(1, Ordering::AcqRel);
        Ok::<_, std::io::Error>(())
    };
    let receive = async {
        let mut received = Vec::with_capacity(payload.len());
        inbound.read_to_end(&mut received).await?;
        progress.bulk_eofs_received.fetch_add(1, Ordering::AcqRel);
        inbound.shutdown().await?;
        progress.bulk_reverse_closes.fetch_add(1, Ordering::AcqRel);
        Ok::<_, std::io::Error>(received)
    };
    let ((), received) = tokio::try_join!(send, receive)
        .with_context(|| format!("scale round {label} bulk stream failed"))?;
    if received != payload {
        bail!("scale round {label} bulk payload mismatch");
    }
    Ok(())
}

fn observe_protected_lanes(stats: &BondRuntimeStats, observed: &mut BTreeSet<u32>) {
    observed.extend(
        stats
            .lanes
            .iter()
            .filter(|lane| lane.reserved_for_low_latency)
            .map(|lane| lane.id.get()),
    );
}

fn acknowledged_bytes_for_lanes(
    before: &BondRuntimeStats,
    after: &BondRuntimeStats,
    lane_ids: &BTreeSet<u32>,
) -> Result<u64> {
    lane_ids.iter().try_fold(0_u64, |total, lane_id| {
        Ok(total.saturating_add(acknowledged_bytes_for_lane(before, after, *lane_id)?))
    })
}

fn acknowledged_bytes_for_lane(
    before: &BondRuntimeStats,
    after: &BondRuntimeStats,
    lane_id: u32,
) -> Result<u64> {
    let previous = before
        .lanes
        .iter()
        .find(|lane| lane.id.get() == lane_id)
        .with_context(|| format!("scale baseline omitted lane {lane_id}"))?;
    let current = after
        .lanes
        .iter()
        .find(|lane| lane.id.get() == lane_id)
        .with_context(|| format!("scale result omitted lane {lane_id}"))?;
    Ok(current
        .bytes_acknowledged
        .saturating_sub(previous.bytes_acknowledged))
}

fn effective_bulk_lane_count(stats: &BondRuntimeStats) -> usize {
    let active = stats.lanes.iter().filter(|lane| lane.active).count();
    let unprotected = stats
        .lanes
        .iter()
        .filter(|lane| lane.active && !lane.reserved_for_low_latency)
        .count();
    if unprotected == 0 {
        active
    } else {
        unprotected
    }
}

fn has_unprotected_active_lane(stats: &BondRuntimeStats) -> bool {
    stats
        .lanes
        .iter()
        .any(|lane| lane.active && !lane.reserved_for_low_latency)
}

fn deterministic_scale_payload(length: usize) -> Vec<u8> {
    deterministic_scale_payload_with_salt(length, 0)
}

fn deterministic_scale_payload_with_salt(length: usize, salt: u8) -> Vec<u8> {
    (0..length)
        .map(|index| {
            (index as u8)
                .wrapping_mul(31)
                .wrapping_add((index / 251) as u8)
                .wrapping_add(salt)
        })
        .collect()
}

fn scale_realtime_token(round: usize, sample: usize) -> [u8; 64] {
    let mut token = [0_u8; 64];
    token[..8].copy_from_slice(&(round as u64).to_be_bytes());
    token[8..16].copy_from_slice(&(sample as u64).to_be_bytes());
    for (offset, byte) in token[16..].iter_mut().enumerate() {
        *byte = (offset as u8)
            .wrapping_mul(31)
            .wrapping_add(round as u8)
            .wrapping_add(sample as u8);
    }
    token
}

const fn minimum_scale_overlap_samples(direction: ScaleDirection, payload_bytes: usize) -> usize {
    if matches!(direction, ScaleDirection::ClientToServer)
        && payload_bytes == SCALE_SMALL_PAYLOAD_BYTES
    {
        1
    } else {
        SCALE_REALTIME_SAMPLES / 2
    }
}

fn median(sorted: &[u64]) -> Result<u64> {
    let middle = sorted.len() / 2;
    match sorted.len() {
        0 => bail!("cannot compute a median without observations"),
        length if length % 2 == 0 => Ok(u64::try_from(
            (u128::from(sorted[middle - 1]) + u128::from(sorted[middle])) / 2,
        )
        .unwrap_or(u64::MAX)),
        _ => Ok(sorted[middle]),
    }
}

fn scale_percentile(sorted: &[u64], percentile: usize) -> Result<u64> {
    if sorted.is_empty() {
        bail!("cannot compute a percentile without observations");
    }
    let rank = sorted.len().saturating_mul(percentile).div_ceil(100);
    Ok(sorted[rank.saturating_sub(1).min(sorted.len() - 1)])
}

fn ratio_basis_points(numerator: u64, denominator: u64) -> Result<u64> {
    if denominator == 0 {
        bail!("cannot compute a ratio with a zero denominator");
    }
    Ok(
        u64::try_from(u128::from(numerator).saturating_mul(10_000) / u128::from(denominator))
            .unwrap_or(u64::MAX),
    )
}

async fn wait_until_acknowledged(runtime: &BondSession) -> Result<BondRuntimeStats> {
    tokio::time::timeout(TRANSFER_TIMEOUT, async {
        loop {
            let stats = runtime.statistics().await?;
            if stats.unacknowledged_bytes == 0 {
                return Ok(stats);
            }
            tokio::time::sleep(Duration::from_millis(10)).await;
        }
    })
    .await
    .context("live bond acknowledgements exceeded their 15-minute deadline")?
}

async fn wait_until_pair_acknowledged(
    first: &BondSession,
    second: &BondSession,
) -> Result<(BondRuntimeStats, BondRuntimeStats)> {
    tokio::time::timeout(TRANSFER_TIMEOUT, async {
        loop {
            let (first_stats, second_stats) =
                tokio::try_join!(first.statistics(), second.statistics())?;
            if first_stats.unacknowledged_bytes == 0 && second_stats.unacknowledged_bytes == 0 {
                return Ok::<_, anonssh_bond_tokio::BondRuntimeError>((first_stats, second_stats));
            }
            tokio::time::sleep(Duration::from_millis(10)).await;
        }
    })
    .await
    .context("live bond bidirectional acknowledgements exceeded their 15-minute deadline")?
    .map_err(anyhow::Error::from)
}

fn max_lane_queue_delay(stats: &BondRuntimeStats) -> u64 {
    stats
        .lanes
        .iter()
        .map(|lane| {
            u64::try_from(
                lane.queued_through
                    .duration_since(stats.observed_at)
                    .unwrap_or_default()
                    .as_micros(),
            )
            .unwrap_or(u64::MAX)
        })
        .max()
        .unwrap_or(0)
}

fn bulk_diversity(
    plan: &[PlannedLane],
    stats: &BondRuntimeStats,
) -> (BTreeSet<Provider>, BTreeSet<u64>) {
    let used = plan.iter().filter_map(|planned| {
        let snapshot = stats
            .lanes
            .iter()
            .find(|snapshot| snapshot.id == planned.config.id)?;
        (snapshot.bytes_scheduled > 0 && !snapshot.reserved_for_low_latency)
            .then_some((planned.provider, snapshot.failure_domain.get()))
    });
    let providers = used.clone().map(|(provider, _)| provider).collect();
    let failure_domains = used.map(|(_, domain)| domain).collect();
    (providers, failure_domains)
}

fn build_report(
    plan: &[PlannedLane],
    stats: BondRuntimeStats,
    summary: TransferSummary,
) -> Result<LiveBondReport> {
    let lanes = plan
        .iter()
        .map(|planned| {
            let snapshot = stats
                .lanes
                .iter()
                .find(|snapshot| snapshot.id == planned.config.id)
                .context("runtime statistics omitted a planned lane")?;
            Ok(LaneReport {
                id: snapshot.id.get(),
                provider: planned.provider,
                router_failure_domain: snapshot.failure_domain.get(),
                purpose: planned.purpose,
                reserved_for_low_latency: snapshot.reserved_for_low_latency,
                bytes_scheduled: snapshot.bytes_scheduled,
                bytes_acknowledged: snapshot.bytes_acknowledged,
            })
        })
        .collect::<Result<Vec<_>>>()?;
    Ok(LiveBondReport {
        schema: "anonssh.live-bond.v2",
        status: "ok",
        pool: summary.pool,
        payload_bytes: summary.payload_bytes,
        payload_sha256: summary.payload_sha256,
        elapsed_millis: summary.elapsed.as_millis(),
        authenticated_lanes: plan.len(),
        bulk_providers_used: summary.bulk_providers_used,
        bulk_failure_domains_used: summary.bulk_failure_domains_used,
        realtime: summary.realtime,
        unacknowledged_bytes: stats.unacknowledged_bytes,
        lanes,
    })
}

fn mixed_plan() -> Result<Vec<PlannedLane>> {
    const TOR_DOMAIN: u64 = 1;
    const I2P_DOMAIN: u64 = 2;
    Ok(vec![
        planned_lane(1, TOR_DOMAIN, 50, 8, Provider::Tor, "realtime")?,
        planned_lane(2, TOR_DOMAIN, 250, 4, Provider::Tor, "bulk")?,
        planned_lane(3, I2P_DOMAIN, 150, 8, Provider::I2p, "realtime")?,
        planned_lane(4, I2P_DOMAIN, 500, 4, Provider::I2p, "bulk")?,
    ])
}

fn i2p_pool_plan() -> Result<Vec<PlannedLane>> {
    Ok(vec![
        planned_lane(1, 11, 150, 8, Provider::I2p, "realtime")?,
        planned_lane(2, 11, 500, 4, Provider::I2p, "bulk")?,
        planned_lane(3, 12, 500, 4, Provider::I2p, "bulk")?,
    ])
}

fn planned_lane(
    id: u32,
    domain: u64,
    rtt_ms: u64,
    rate_mbps: u64,
    provider: Provider,
    purpose: &'static str,
) -> Result<PlannedLane> {
    Ok(PlannedLane {
        config: LaneConfig::new(
            LaneId::new(id)?,
            FailureDomain::new(domain)?,
            Duration::from_millis(rtt_ms),
            rate_mbps * 1_000_000,
        )?
        .with_provider_group(ProviderId::new(match provider {
            Provider::Tor => 1,
            Provider::I2p => 2,
        })?),
        provider,
        purpose,
    })
}

async fn stop_routers(
    i2pd: &I2pdManager,
    server_tor: &TorManager,
    client_tor: &TorManager,
) -> Result<()> {
    let (i2p, server, client) = tokio::join!(i2pd.stop(), server_tor.stop(), client_tor.stop());
    merge_result(i2p, merge_result(server, client))
}

fn allocate_endpoints() -> Result<Endpoints> {
    let [sam, server_tor_socks, server_tor_control, client_tor_socks, client_tor_control] =
        allocate_loopback_endpoints(5)?
            .try_into()
            .map_err(|_| anyhow!("bond endpoint allocation returned the wrong count"))?;
    Ok(Endpoints {
        sam,
        server_tor_socks,
        server_tor_control,
        client_tor_socks,
        client_tor_control,
    })
}

fn allocate_product_pool_endpoints() -> Result<ProductPoolEndpoints> {
    let per_endpoint = PRODUCTION_I2P_SLOTS + 2 * PRODUCTION_TOR_CANDIDATES;
    let mut reservations = allocate_loopback_endpoints(2 * per_endpoint)?;
    let addresses = reserved_addresses(&reservations)?;
    let client_reservations = reservations.split_off(per_endpoint);
    let server_tor_socks_start = PRODUCTION_I2P_SLOTS;
    let server_tor_control_start = server_tor_socks_start + PRODUCTION_TOR_CANDIDATES;
    let client_sam_start = per_endpoint;
    let client_tor_socks_start = client_sam_start + PRODUCTION_I2P_SLOTS;
    let client_tor_control_start = client_tor_socks_start + PRODUCTION_TOR_CANDIDATES;
    Ok(ProductPoolEndpoints {
        server_sam: addresses[..server_tor_socks_start].try_into()?,
        server_tor_socks: addresses[server_tor_socks_start..server_tor_control_start].try_into()?,
        server_tor_control: addresses[server_tor_control_start..client_sam_start].try_into()?,
        client_sam: addresses[client_sam_start..client_tor_socks_start].try_into()?,
        client_tor_socks: addresses[client_tor_socks_start..client_tor_control_start].try_into()?,
        client_tor_control: addresses[client_tor_control_start..].try_into()?,
        server_reservations: reservations,
        client_reservations,
    })
}

fn allocate_scale_pool_endpoints(slots_per_provider: usize) -> Result<ScalePoolEndpoints> {
    let mut reservations = allocate_loopback_endpoints(slots_per_provider * 6)?;
    let addresses = reserved_addresses(&reservations)?;
    let s = slots_per_provider;
    let client_reservations = reservations.split_off(3 * s);
    Ok(ScalePoolEndpoints {
        server: ScaleEndpointSet {
            sam: addresses[0..s].to_vec(),
            tor_socks: addresses[s..2 * s].to_vec(),
            tor_control: addresses[2 * s..3 * s].to_vec(),
            reservations,
        },
        client: ScaleEndpointSet {
            sam: addresses[3 * s..4 * s].to_vec(),
            tor_socks: addresses[4 * s..5 * s].to_vec(),
            tor_control: addresses[5 * s..6 * s].to_vec(),
            reservations: client_reservations,
        },
    })
}

fn scale_router_pool(
    root: &Path,
    tor_binary: PathBuf,
    i2pd_binary: PathBuf,
    endpoints: ScaleEndpointSet,
) -> Result<RouterPool> {
    let ScaleEndpointSet {
        sam,
        tor_socks,
        tor_control,
        reservations,
    } = endpoints;
    if tor_socks.len() != tor_control.len() || tor_socks.len() != sam.len() {
        bail!("scale router endpoint vectors have inconsistent lengths");
    }
    let tor = tor_socks
        .into_iter()
        .zip(tor_control)
        .enumerate()
        .map(|(index, (socks, control))| {
            let slot = u32::try_from(index + 1).context("Tor scale slot overflow")?;
            Ok((
                slot,
                vec![(root.join(format!("tor-slot-{slot}")), socks, control)],
                u64::from(slot),
            ))
        })
        .collect::<Result<Vec<_>>>()?;
    let i2p = sam
        .into_iter()
        .enumerate()
        .map(|(index, endpoint)| {
            let slot = u32::try_from(index + 1).context("I2P scale slot overflow")?;
            Ok((
                slot,
                root.join(format!("i2pd-slot-{slot}")),
                endpoint,
                100 + u64::from(slot),
            ))
        })
        .collect::<Result<Vec<_>>>()?;
    RouterPool::new_reserved(tor_binary, tor, i2pd_binary, i2p, reservations)
}

fn product_router_pool(
    root: &Path,
    tor_binary: PathBuf,
    i2pd_binary: PathBuf,
    tor_socks: [SocketAddr; PRODUCTION_TOR_CANDIDATES],
    tor_control: [SocketAddr; PRODUCTION_TOR_CANDIDATES],
    sam: [SocketAddr; PRODUCTION_I2P_SLOTS],
    reservations: Vec<ReservedLoopbackEndpoint>,
) -> Result<RouterPool> {
    let tor = (0..PRODUCTION_TOR_SLOTS)
        .map(|index| {
            let slot = u32::try_from(index + 1).context("Tor test slot overflow")?;
            Ok((
                slot,
                vec![
                    (
                        root.join(format!("tor-slot-{slot}")),
                        tor_socks[index],
                        tor_control[index],
                    ),
                    (
                        root.join(format!("tor-slot-{slot}-reserve")),
                        tor_socks[index + PRODUCTION_TOR_SLOTS],
                        tor_control[index + PRODUCTION_TOR_SLOTS],
                    ),
                ],
                u64::from(slot),
            ))
        })
        .collect::<Result<Vec<_>>>()?;
    let i2p = sam
        .into_iter()
        .enumerate()
        .map(|(index, endpoint)| {
            let slot = u32::try_from(index + 1).context("I2P test slot overflow")?;
            Ok((
                slot,
                root.join(format!("i2pd-slot-{slot}")),
                endpoint,
                100 + u64::from(slot),
            ))
        })
        .collect::<Result<Vec<_>>>()?;
    RouterPool::new_reserved(tor_binary, tor, i2pd_binary, i2p, reservations)
}

fn allocate_loopback_endpoints(count: usize) -> Result<Vec<ReservedLoopbackEndpoint>> {
    (0..count)
        .map(|_| ReservedLoopbackEndpoint::allocate())
        .collect()
}

fn reserved_addresses(reservations: &[ReservedLoopbackEndpoint]) -> Result<Vec<SocketAddr>> {
    reservations
        .iter()
        .map(ReservedLoopbackEndpoint::address)
        .collect()
}

fn live_root(label: &str) -> PathBuf {
    std::env::temp_dir().join(format!("anonssh-live-{label}-{}", std::process::id()))
}

fn scale_topology_directory_size(root: &Path, slots_per_provider: usize) -> Result<u64> {
    let mut bytes = 0_u64;
    for side in ["server", "client"] {
        for slot in 1..=slots_per_provider {
            for prefix in ["tor-slot", "i2pd-slot"] {
                let path = root.join(side).join(format!("{prefix}-{slot}"));
                bytes = bytes
                    .checked_add(directory_size(&path)?)
                    .context("scale topology disk usage overflow")?;
            }
        }
    }
    Ok(bytes)
}

fn directory_size(path: &Path) -> Result<u64> {
    let mut bytes = 0_u64;
    for entry in fs::read_dir(path).with_context(|| format!("failed to read {}", path.display()))? {
        let entry = entry?;
        let file_type = entry.file_type()?;
        bytes = bytes.saturating_add(if file_type.is_dir() {
            directory_size(&entry.path())?
        } else {
            entry.metadata()?.len()
        });
    }
    Ok(bytes)
}

fn directory_size_while_running(path: &Path) -> Result<u64> {
    let entries = match fs::read_dir(path) {
        Ok(entries) => entries,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(0),
        Err(error) => {
            return Err(error).with_context(|| format!("failed to read {}", path.display()))
        }
    };
    let mut bytes = 0_u64;
    for entry in entries {
        let entry = match entry {
            Ok(entry) => entry,
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => continue,
            Err(error) => return Err(error.into()),
        };
        let file_type = match entry.file_type() {
            Ok(file_type) => file_type,
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => continue,
            Err(error) => return Err(error.into()),
        };
        let entry_bytes = if file_type.is_dir() {
            directory_size_while_running(&entry.path())?
        } else {
            match entry.metadata() {
                Ok(metadata) => metadata.len(),
                Err(error) if error.kind() == std::io::ErrorKind::NotFound => continue,
                Err(error) => return Err(error.into()),
            }
        };
        bytes = bytes.saturating_add(entry_bytes);
    }
    Ok(bytes)
}

fn remove_if_present(path: &Path) -> Result<()> {
    match fs::remove_dir_all(path) {
        Ok(()) => Ok(()),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(()),
        Err(error) => Err(error.into()),
    }
}

fn merge_result<T>(operation: Result<T>, cleanup: Result<()>) -> Result<T> {
    match (operation, cleanup) {
        (Ok(value), Ok(())) => Ok(value),
        (Err(error), Ok(())) => Err(error),
        (Ok(_), Err(error)) => Err(error),
        (Err(operation), Err(cleanup)) => Err(anyhow!(
            "{operation:#}; additional cleanup failure: {cleanup:#}"
        )),
    }
}

#[cfg(test)]
mod tests {
    use anonssh_bond::{FailureDomain, LaneConfig, LaneId, SchedulerConfig, SenderConfig};
    use anonssh_bond_tokio::{
        authenticate_client_lane, authenticate_server_lane,
        authenticate_server_lane_with_incarnation, BondRuntimeConfig, BondSession, BondSessionKey,
        LaneJoin, RuntimeLane, ServerIncarnation, SessionRole,
    };
    use std::collections::BTreeSet;
    use std::fs;
    use std::path::PathBuf;
    use std::sync::atomic::{AtomicBool, Ordering};
    use std::time::Duration;
    use tokio::sync::watch;

    use super::{
        allocate_endpoints, allocate_product_pool_endpoints, allocate_scale_pool_endpoints,
        complete_endurance_phase, endurance_contribution_observation, endurance_counter_delta,
        endurance_scaling_policy, fixed_scale_policy, i2p_pool_plan, live_error_report,
        load_endurance_history, minimum_scale_overlap_samples, mixed_plan, open_scale_bulk_stream,
        prepare_endurance_state, run_endurance_quiet_phase, run_scale_realtime_samples,
        scale_router_pool, transfer_scale_bulk_stream, wait_until_pair_acknowledged,
        write_endurance_checkpoint, write_endurance_history, write_scale_checkpoint,
        write_scale_formation_pressure, EnduranceConfig, EnduranceContributionObservation,
        EnduranceCurrentPhase, EnduranceEndpoint, EnduranceHistory, EnduranceLaneObservation,
        EnduranceLease, EnduranceObservation, EndurancePhase, EnduranceResourceObservation,
        EnduranceRuntimeDelta, EnduranceRuntimeObservation, EnduranceStateMetadata,
        EnduranceStopReason, Provider, RealtimeSampleConfig, ScaleCampaignConfig,
        ScaleCheckpointTrial, ScaleDirection, ScaleRoundProgress, ScaleRouterState,
        ENDURANCE_HISTORY_FILE, ENDURANCE_HISTORY_SCHEMA, ENDURANCE_INITIAL_OBSERVATIONS,
        ENDURANCE_LEGACY_HISTORY_SCHEMA, ENDURANCE_QUIET_REALTIME_SAMPLES,
        ENDURANCE_RECENT_OBSERVATIONS, ENDURANCE_SCHEMA, ENDURANCE_STATE_SCHEMA,
        ENDURANCE_V2_HISTORY_SCHEMA, SCALE_CARDINALITIES, SCALE_LARGE_PAYLOAD_BYTES,
        SCALE_PRESSURE_YIELD_BYTES, SCALE_REALTIME_SAMPLES, SCALE_SCENARIOS_PER_CARDINALITY,
        SCALE_SCHEMA, SCALE_SMALL_PAYLOAD_BYTES, SCALE_SUSTAINED_PAYLOAD_BYTES, SCALE_WORKLOADS,
    };
    use crate::router_pool::{PRODUCTION_I2P_SLOTS, PRODUCTION_TOR_CANDIDATES};

    #[test]
    fn live_error_artifact_preserves_terminal_runtime_cause() {
        let error = anyhow::Error::new(anonssh_bond_tokio::BondRuntimeError::StoppedWithCause(
            "bond stream 2 is not open".to_owned(),
        ))
        .context("campaign transfer failed");
        let artifact = live_error_report("anonssh.test-error.v1", &error);

        assert_eq!(artifact["schema"], "anonssh.test-error.v1");
        assert_eq!(artifact["status"], "error");
        assert_eq!(
            artifact["error"],
            "campaign transfer failed: bond runtime stopped after: bond stream 2 is not open"
        );
    }

    #[test]
    fn mixed_plan_has_honest_domains_and_two_bulk_providers() {
        let plan = mixed_plan().unwrap();
        assert_eq!(plan.len(), 4);
        assert_eq!(plan[0].provider, Provider::Tor);
        assert_eq!(plan[0].config.failure_domain, plan[1].config.failure_domain);
        assert_eq!(plan[2].config.failure_domain, plan[3].config.failure_domain);
        assert_ne!(plan[1].config.failure_domain, plan[2].config.failure_domain);
        assert_eq!(plan[0].config.provider_group, plan[1].config.provider_group);
        assert_eq!(plan[2].config.provider_group, plan[3].config.provider_group);
        assert_ne!(plan[1].config.provider_group, plan[2].config.provider_group);
        assert_eq!(
            [plan[1], plan[3]]
                .iter()
                .map(|lane| lane.provider)
                .collect::<BTreeSet<_>>()
                .len(),
            2
        );
    }

    #[test]
    fn managed_router_endpoints_do_not_overlap() {
        let endpoints = allocate_endpoints().unwrap();
        let unique = [
            endpoints.sam.address().unwrap(),
            endpoints.server_tor_socks.address().unwrap(),
            endpoints.server_tor_control.address().unwrap(),
            endpoints.client_tor_socks.address().unwrap(),
            endpoints.client_tor_control.address().unwrap(),
        ]
        .into_iter()
        .collect::<BTreeSet<_>>();
        assert_eq!(unique.len(), 5);
        assert!(unique.iter().all(|endpoint| endpoint.ip().is_loopback()));
    }

    #[test]
    fn product_pool_reserves_every_configured_router_endpoint() {
        let endpoints = allocate_product_pool_endpoints().unwrap();
        let unique = endpoints
            .server_sam
            .iter()
            .chain(&endpoints.server_tor_socks)
            .chain(&endpoints.server_tor_control)
            .chain(&endpoints.client_sam)
            .chain(&endpoints.client_tor_socks)
            .chain(&endpoints.client_tor_control)
            .copied()
            .collect::<BTreeSet<_>>();
        let per_endpoint = PRODUCTION_I2P_SLOTS + 2 * PRODUCTION_TOR_CANDIDATES;
        assert_eq!(unique.len(), 2 * per_endpoint);
        assert_eq!(endpoints.server_reservations.len(), per_endpoint);
        assert_eq!(endpoints.client_reservations.len(), per_endpoint);
        assert!(unique.iter().all(|endpoint| endpoint.ip().is_loopback()));
    }

    #[test]
    fn scale_topology_has_thirty_two_independent_slots_per_endpoint() {
        let endpoints = allocate_scale_pool_endpoints(16).unwrap();
        let unique = endpoints
            .server
            .sam
            .iter()
            .chain(&endpoints.server.tor_socks)
            .chain(&endpoints.server.tor_control)
            .chain(&endpoints.client.sam)
            .chain(&endpoints.client.tor_socks)
            .chain(&endpoints.client.tor_control)
            .copied()
            .collect::<BTreeSet<_>>();
        assert_eq!(unique.len(), 96);
        assert!(unique.iter().all(|endpoint| endpoint.ip().is_loopback()));

        let pool = scale_router_pool(
            &PathBuf::from("/tmp/anonssh-scale-topology-test"),
            PathBuf::from("tor"),
            PathBuf::from("i2pd"),
            endpoints.server,
        )
        .unwrap();
        assert_eq!(pool.tor_slots().len(), 16);
        assert_eq!(pool.tor_candidate_count(), 16);
        assert_eq!(pool.i2p_slots().len(), 16);
        let baseline = pool.prefix(8, 8).unwrap();
        assert_eq!(baseline.tor_slots().len(), 8);
        assert_eq!(baseline.i2p_slots().len(), 8);
    }

    #[test]
    fn scale_matrix_covers_every_cardinality_and_workload() {
        let config = ScaleCampaignConfig::new(16, 4).unwrap();
        let matrix = config.matrix();
        assert_eq!(
            matrix.len(),
            SCALE_CARDINALITIES.len() * SCALE_SCENARIOS_PER_CARDINALITY
        );
        assert_eq!(config.maximum_slots_per_provider(), 16);
        assert_eq!(config.rounds_per_trial, 4);
        assert_eq!(
            SCALE_WORKLOADS,
            [
                (SCALE_SMALL_PAYLOAD_BYTES, ScaleDirection::ClientToServer),
                (SCALE_LARGE_PAYLOAD_BYTES, ScaleDirection::ServerToClient),
                (SCALE_SUSTAINED_PAYLOAD_BYTES, ScaleDirection::Bidirectional),
            ]
        );
        let (matrix, remainder) = matrix.as_chunks::<SCALE_SCENARIOS_PER_CARDINALITY>();
        assert!(remainder.is_empty());
        for (cardinality_index, scenarios) in matrix.iter().enumerate() {
            for (scenario, workload) in scenarios.iter().zip(SCALE_WORKLOADS) {
                assert_eq!(
                    scenario.slots_per_provider,
                    SCALE_CARDINALITIES[cardinality_index]
                );
                assert_eq!((scenario.payload_bytes, scenario.direction), workload);
            }
        }
        assert!(ScaleCampaignConfig::new(3, 2).is_err());
        assert!(ScaleCampaignConfig::new(16, 0).is_err());
        assert!(ScaleCampaignConfig::new(16, 9).is_err());
        let evidence_policy = fixed_scale_policy(32);
        assert_eq!(evidence_policy.maximum_active_lanes, 32);
        assert_eq!(evidence_policy.maximum_admissions_per_interval, 32);
        assert_eq!(
            crate::product_config::ScalingPolicy::performance().maximum_active_lanes,
            16
        );
    }

    #[test]
    fn endurance_configuration_and_cycle_are_bounded() {
        let config = EnduranceConfig::new(
            PathBuf::from("/tmp/anonssh-endurance-state"),
            PathBuf::from("/tmp/anonssh-endurance-checkpoint.json"),
            0,
            16,
            32,
            120,
            2,
        )
        .unwrap();
        assert_eq!(config.payload_bytes, 32 * 1024 * 1024);
        assert_eq!(config.maximum_disk_bytes, 2 * 1024 * 1024 * 1024);
        assert_eq!(
            EndurancePhase::CYCLE,
            [
                EndurancePhase::ClientToServer,
                EndurancePhase::Bidirectional,
                EndurancePhase::ServerToClient,
                EndurancePhase::QuietRealtime,
            ]
        );
        assert_eq!(
            EndurancePhase::Bidirectional.scale_direction(),
            Some(ScaleDirection::Bidirectional)
        );
        assert_eq!(EndurancePhase::QuietRealtime.scale_direction(), None);
        let policy = endurance_scaling_policy(32);
        assert_eq!(policy.maximum_active_lanes, 32);
        assert_eq!(policy.maximum_admissions_per_interval, 4);
        assert_eq!(policy.maximum_drains_per_interval, 4);

        assert!(EnduranceConfig::new(
            PathBuf::from("/tmp/state"),
            PathBuf::from("/tmp/checkpoint"),
            0,
            4,
            32,
            120,
            2,
        )
        .is_err());
        assert!(EnduranceConfig::new(
            PathBuf::from("/tmp/state"),
            PathBuf::from("/tmp/checkpoint"),
            0,
            16,
            1,
            120,
            2,
        )
        .is_err());
        assert!(EnduranceConfig::new(
            PathBuf::from("/tmp/state"),
            PathBuf::from("/tmp/checkpoint"),
            0,
            16,
            32,
            1,
            2,
        )
        .is_err());
        assert!(EnduranceConfig::new(
            PathBuf::from("/tmp/state"),
            PathBuf::from("/tmp/checkpoint"),
            0,
            16,
            32,
            120,
            0,
        )
        .is_err());
    }

    #[tokio::test]
    async fn endurance_stop_finishes_the_active_exact_phase() {
        let stop = async {
            tokio::time::sleep(Duration::from_millis(1)).await;
            Ok::<_, anyhow::Error>(EnduranceStopReason::DurationElapsed)
        };
        tokio::pin!(stop);
        let started = std::time::Instant::now();
        let observation = async {
            tokio::time::sleep(Duration::from_millis(25)).await;
            Ok::<_, anyhow::Error>(7_u8)
        };
        let (value, stop_reason) = complete_endurance_phase(observation, stop.as_mut())
            .await
            .unwrap();
        assert_eq!(value, 7);
        assert_eq!(stop_reason, Some(EnduranceStopReason::DurationElapsed));
        assert!(started.elapsed() >= Duration::from_millis(20));
    }

    #[test]
    fn endurance_state_generation_and_lease_are_stable() {
        let root = std::env::temp_dir().join(format!(
            "anonssh-endurance-state-test-{}",
            std::process::id()
        ));
        let checkpoint = root.with_extension("checkpoint.json");
        let _ = fs::remove_dir_all(&root);
        let _ = fs::remove_file(&checkpoint);
        let config = EnduranceConfig::new(root.clone(), checkpoint, 1, 16, 8, 60, 1).unwrap();
        fs::create_dir_all(&root).unwrap();
        let lease = EnduranceLease::acquire(&root).unwrap();
        assert!(EnduranceLease::acquire(&root).is_err());
        let first = prepare_endurance_state(&config).unwrap();
        let second = prepare_endurance_state(&config).unwrap();
        assert_eq!(first.schema, ENDURANCE_STATE_SCHEMA);
        assert_eq!(first.generation, 1);
        assert_eq!(second.generation, 2);
        assert_eq!(first.created_unix_seconds, second.created_unix_seconds);
        lease.release().unwrap();
        EnduranceLease::acquire(&root).unwrap().release().unwrap();
        let stale_lease = root.join("campaign.lease");
        fs::create_dir(&stale_lease).unwrap();
        fs::write(stale_lease.join("pid"), format!("{}\n", u32::MAX)).unwrap();
        EnduranceLease::acquire(&root).unwrap().release().unwrap();

        let mismatched = EnduranceConfig::new(
            root.clone(),
            root.with_extension("other-checkpoint.json"),
            1,
            8,
            8,
            60,
            1,
        )
        .unwrap();
        assert!(prepare_endurance_state(&mismatched).is_err());
        fs::remove_dir_all(root).unwrap();
    }

    fn quiet_endurance_observation(sequence: u64) -> EnduranceObservation {
        EnduranceObservation {
            sequence,
            state_generation: 1,
            phase: EndurancePhase::QuietRealtime,
            run_elapsed_millis: sequence.saturating_mul(1_000),
            phase_elapsed_millis: 1_000,
            state_age_seconds: sequence,
            client_active_lanes: 4,
            server_active_lanes: 4,
            desired_lane_ids: vec![1, 2, 17, 18],
            pending_pressure_lane_ids: Vec::new(),
            adaptive_generation: sequence,
            adaptive_events_retained: 1,
            bulk: None,
            quiet_realtime_round_trip_micros: vec![100],
            quiet_realtime_round_trip_micros_p50: Some(100),
            quiet_realtime_round_trip_micros_p95: Some(100),
            quiet_realtime_round_trip_micros_max: Some(100),
            quiet_realtime_is_echo: true,
            realtime_redundancy: true,
            runtime: EnduranceRuntimeObservation {
                client: EnduranceRuntimeDelta {
                    redundant_realtime_frames: 2,
                    dropped_redundant_realtime_frames: 1,
                    retransmitted_frames: 1,
                    stream_backpressure_events: 2,
                    ..EnduranceRuntimeDelta::default()
                },
                server: EnduranceRuntimeDelta {
                    liveness_failures: 1,
                    ..EnduranceRuntimeDelta::default()
                },
            },
            contribution: EnduranceContributionObservation {
                tor_acknowledged_bytes: 600,
                i2p_acknowledged_bytes: 400,
                contributing_tor_lanes: 1,
                contributing_i2p_lanes: 1,
                maximum_lane_acknowledged_bytes: 600,
                maximum_lane_share_basis_points: 6_000,
            },
            resources: EnduranceResourceObservation {
                running_router_processes: 8,
                router_cpu_time_micros: sequence,
                router_resident_bytes: 1024,
                maximum_router_startup_millis: 10,
                persistent_state_bytes: 2048,
            },
            lanes: vec![EnduranceLaneObservation {
                endpoint: EnduranceEndpoint::Client,
                id: 1,
                provider: Provider::Tor,
                active: true,
                delivery_measured: true,
                reserved_for_low_latency: true,
                smoothed_round_trip_micros: 100,
                delivery_rate_bps: 1_000,
                bytes_scheduled: sequence,
                bytes_acknowledged: sequence,
                phase_bytes_scheduled: 1,
                phase_bytes_acknowledged: 1,
            }],
        }
    }

    #[test]
    fn endurance_phase_evidence_is_local_and_provider_aware() {
        let lane = |endpoint, id, provider, acknowledged| EnduranceLaneObservation {
            endpoint,
            id,
            provider,
            active: true,
            delivery_measured: true,
            reserved_for_low_latency: false,
            smoothed_round_trip_micros: 100,
            delivery_rate_bps: 1_000,
            bytes_scheduled: acknowledged,
            bytes_acknowledged: acknowledged,
            phase_bytes_scheduled: acknowledged,
            phase_bytes_acknowledged: acknowledged,
        };
        let lanes = vec![
            lane(EnduranceEndpoint::Client, 1, Provider::Tor, 600),
            lane(EnduranceEndpoint::Client, 17, Provider::I2p, 300),
            lane(EnduranceEndpoint::Server, 18, Provider::I2p, 100),
            lane(EnduranceEndpoint::Server, 2, Provider::Tor, 0),
        ];

        let contribution = endurance_contribution_observation(&lanes);
        assert_eq!(contribution.tor_acknowledged_bytes, 600);
        assert_eq!(contribution.i2p_acknowledged_bytes, 400);
        assert_eq!(contribution.contributing_tor_lanes, 1);
        assert_eq!(contribution.contributing_i2p_lanes, 2);
        assert_eq!(contribution.maximum_lane_acknowledged_bytes, 600);
        assert_eq!(contribution.maximum_lane_share_basis_points, 6_000);
        assert_eq!(endurance_counter_delta(15, 9, "test").unwrap(), 6);
        assert!(endurance_counter_delta(9, 15, "test").is_err());
    }

    #[test]
    fn endurance_history_and_checkpoint_remain_bounded() {
        let mut history = EnduranceHistory::default();
        for sequence in 1..=150 {
            history.observe(quiet_endurance_observation(sequence));
        }
        assert_eq!(history.completed_observations, 150);
        assert_eq!(
            history.initial_observations.len(),
            ENDURANCE_INITIAL_OBSERVATIONS
        );
        assert_eq!(
            history.recent_observations.len(),
            ENDURANCE_RECENT_OBSERVATIONS
        );
        assert_eq!(history.recent_observations.front().unwrap().sequence, 23);
        assert_eq!(history.recent_observations.back().unwrap().sequence, 150);
        assert_eq!(history.aggregates.quiet_realtime.observations, 150);
        assert_eq!(
            history.aggregates.quiet_realtime.redundant_realtime_frames,
            300
        );
        assert_eq!(
            history
                .aggregates
                .quiet_realtime
                .dropped_redundant_realtime_frames,
            150
        );
        assert_eq!(history.aggregates.quiet_realtime.retransmitted_frames, 150);
        assert_eq!(history.aggregates.quiet_realtime.liveness_failures, 150);
        assert_eq!(
            history.aggregates.quiet_realtime.stream_backpressure_events,
            300
        );
        assert_eq!(
            history.aggregates.quiet_realtime.tor_acknowledged_bytes,
            90_000
        );
        assert_eq!(
            history.aggregates.quiet_realtime.i2p_acknowledged_bytes,
            60_000
        );
        assert_eq!(
            history
                .aggregates
                .quiet_realtime
                .maximum_lane_share_basis_points,
            6_000
        );

        let root = std::env::temp_dir().join(format!(
            "anonssh-endurance-history-test-{}",
            std::process::id()
        ));
        let path = root.with_extension("checkpoint.json");
        let _ = fs::remove_dir_all(&root);
        let _ = fs::remove_file(&path);
        let config = EnduranceConfig::new(root.clone(), path.clone(), 1, 16, 8, 60, 1).unwrap();
        fs::create_dir_all(&root).unwrap();
        let state = EnduranceStateMetadata {
            schema: ENDURANCE_STATE_SCHEMA.to_owned(),
            created_unix_seconds: 1,
            generation: 2,
            slots_per_provider: 16,
        };
        write_endurance_history(&config, state.generation, &history).unwrap();
        let resumed = load_endurance_history(&config, &state).unwrap();
        assert_eq!(resumed.completed_observations, 150);
        assert_eq!(resumed.initial_observations[0].sequence, 1);
        assert_eq!(resumed.recent_observations.back().unwrap().sequence, 150);
        let history_path = root.join(ENDURANCE_HISTORY_FILE);
        let history_file: serde_json::Value =
            serde_json::from_slice(&fs::read(&history_path).unwrap()).unwrap();
        assert_eq!(history_file["schema"], ENDURANCE_HISTORY_SCHEMA);
        let config_report = config.report().unwrap();
        let current = EnduranceCurrentPhase {
            sequence: 151,
            phase: EndurancePhase::ClientToServer,
            started_elapsed_millis: 150_000,
        };
        write_endurance_checkpoint(
            &path,
            "running",
            &config_report,
            &state,
            1,
            Duration::from_secs(150),
            &history,
            Some(&current),
            None,
            false,
            None,
        )
        .unwrap();
        let checkpoint: serde_json::Value =
            serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
        assert_eq!(checkpoint["schema"], ENDURANCE_SCHEMA);
        assert_eq!(checkpoint["completed_observations"], 150);
        assert_eq!(
            checkpoint["initial_observations"].as_array().unwrap().len(),
            ENDURANCE_INITIAL_OBSERVATIONS
        );
        assert_eq!(
            checkpoint["recent_observations"].as_array().unwrap().len(),
            ENDURANCE_RECENT_OBSERVATIONS
        );
        assert_eq!(checkpoint["current_phase"]["sequence"], 151);
        assert!(!path.with_extension("tmp").exists());
        fs::remove_file(path).unwrap();
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn legacy_endurance_history_migrates_without_inventing_phase_evidence() {
        let root = std::env::temp_dir().join(format!(
            "anonssh-endurance-history-migration-test-{}",
            std::process::id()
        ));
        let checkpoint = root.with_extension("checkpoint.json");
        let _ = fs::remove_dir_all(&root);
        let _ = fs::remove_file(&checkpoint);
        let config = EnduranceConfig::new(root.clone(), checkpoint, 1, 16, 8, 60, 1).unwrap();
        fs::create_dir_all(&root).unwrap();
        let state = EnduranceStateMetadata {
            schema: ENDURANCE_STATE_SCHEMA.to_owned(),
            created_unix_seconds: 1,
            generation: 1,
            slots_per_provider: 16,
        };
        let mut history = EnduranceHistory::default();
        history.observe(quiet_endurance_observation(1));
        write_endurance_history(&config, state.generation, &history).unwrap();
        let path = root.join(ENDURANCE_HISTORY_FILE);
        let mut legacy: serde_json::Value =
            serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
        legacy["schema"] = ENDURANCE_LEGACY_HISTORY_SCHEMA.into();
        let history_value = legacy["history"].as_object_mut().unwrap();
        for collection in ["initial_observations", "recent_observations"] {
            for observation in history_value[collection].as_array_mut().unwrap() {
                let observation = observation.as_object_mut().unwrap();
                observation.remove("quiet_realtime_is_echo");
                observation.remove("realtime_redundancy");
                observation.remove("runtime");
                observation.remove("contribution");
                for lane in observation["lanes"].as_array_mut().unwrap() {
                    let lane = lane.as_object_mut().unwrap();
                    lane.remove("phase_bytes_scheduled");
                    lane.remove("phase_bytes_acknowledged");
                }
            }
        }
        for aggregate in history_value["aggregates"]
            .as_object_mut()
            .unwrap()
            .values_mut()
        {
            let aggregate = aggregate.as_object_mut().unwrap();
            for field in [
                "redundant_realtime_frames",
                "dropped_redundant_realtime_frames",
                "retransmitted_frames",
                "liveness_failures",
                "stream_backpressure_events",
                "tor_acknowledged_bytes",
                "i2p_acknowledged_bytes",
                "contributing_lanes_min",
                "contributing_lanes_max",
                "maximum_lane_share_basis_points",
            ] {
                aggregate.remove(field);
            }
        }
        fs::write(&path, serde_json::to_vec_pretty(&legacy).unwrap()).unwrap();

        let migrated = load_endurance_history(&config, &state).unwrap();
        let observation = migrated.recent_observations.back().unwrap();
        assert!(!observation.quiet_realtime_is_echo);
        assert!(!observation.realtime_redundancy);
        assert_eq!(observation.runtime.client.retransmitted_frames, 0);
        assert_eq!(observation.contribution.tor_acknowledged_bytes, 0);
        assert_eq!(observation.lanes[0].phase_bytes_acknowledged, 0);
        assert_eq!(migrated.aggregates.quiet_realtime.observations, 0);
        assert_eq!(migrated.aggregates.legacy_quiet_lifecycle.observations, 1);
        assert_eq!(
            migrated
                .aggregates
                .legacy_quiet_lifecycle
                .tor_acknowledged_bytes,
            0
        );
        write_endurance_history(&config, state.generation, &migrated).unwrap();
        let current: serde_json::Value = serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
        assert_eq!(current["schema"], ENDURANCE_HISTORY_SCHEMA);
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn v2_endurance_history_separates_legacy_quiet_measurements() {
        let root = std::env::temp_dir().join(format!(
            "anonssh-endurance-history-v2-migration-test-{}",
            std::process::id()
        ));
        let checkpoint = root.with_extension("checkpoint.json");
        let _ = fs::remove_dir_all(&root);
        let _ = fs::remove_file(&checkpoint);
        let config = EnduranceConfig::new(root.clone(), checkpoint, 1, 16, 8, 60, 1).unwrap();
        fs::create_dir_all(&root).unwrap();
        let state = EnduranceStateMetadata {
            schema: ENDURANCE_STATE_SCHEMA.to_owned(),
            created_unix_seconds: 1,
            generation: 1,
            slots_per_provider: 16,
        };
        let mut history = EnduranceHistory::default();
        history.observe(quiet_endurance_observation(1));
        write_endurance_history(&config, state.generation, &history).unwrap();
        let path = root.join(ENDURANCE_HISTORY_FILE);
        let mut v2: serde_json::Value = serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
        v2["schema"] = ENDURANCE_V2_HISTORY_SCHEMA.into();
        let history_value = v2["history"].as_object_mut().unwrap();
        history_value["aggregates"]
            .as_object_mut()
            .unwrap()
            .remove("legacy_quiet_lifecycle");
        for collection in ["initial_observations", "recent_observations"] {
            for observation in history_value[collection].as_array_mut().unwrap() {
                let observation = observation.as_object_mut().unwrap();
                observation.remove("quiet_realtime_is_echo");
                observation.remove("realtime_redundancy");
                let runtime = observation["runtime"].as_object_mut().unwrap();
                for endpoint in ["client", "server"] {
                    let endpoint = runtime[endpoint].as_object_mut().unwrap();
                    endpoint.remove("redundant_realtime_frames");
                    endpoint.remove("dropped_redundant_realtime_frames");
                }
            }
        }
        fs::write(&path, serde_json::to_vec_pretty(&v2).unwrap()).unwrap();

        let migrated = load_endurance_history(&config, &state).unwrap();
        assert_eq!(migrated.completed_observations, 1);
        assert_eq!(migrated.aggregates.quiet_realtime.observations, 0);
        assert_eq!(migrated.aggregates.legacy_quiet_lifecycle.observations, 1);
        assert!(!migrated.recent_observations[0].quiet_realtime_is_echo);
        assert!(!migrated.recent_observations[0].realtime_redundancy);
        assert_eq!(
            migrated.recent_observations[0]
                .runtime
                .client
                .redundant_realtime_frames,
            0
        );
        assert_eq!(
            migrated.recent_observations[0]
                .runtime
                .server
                .dropped_redundant_realtime_frames,
            0
        );
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn scale_router_state_distinguishes_cold_expansion_and_reuse() {
        assert_eq!(ScaleRouterState::classify(0, 1), ScaleRouterState::Fresh);
        assert_eq!(
            ScaleRouterState::classify(1, 2),
            ScaleRouterState::PartiallyRetained
        );
        assert_eq!(ScaleRouterState::classify(4, 4), ScaleRouterState::Retained);
    }

    #[test]
    fn short_scale_round_retains_slow_echo_without_weakening_sustained_overlap() {
        assert_eq!(
            minimum_scale_overlap_samples(
                ScaleDirection::ClientToServer,
                SCALE_SMALL_PAYLOAD_BYTES
            ),
            1
        );
        assert_eq!(
            minimum_scale_overlap_samples(
                ScaleDirection::ServerToClient,
                SCALE_LARGE_PAYLOAD_BYTES
            ),
            SCALE_REALTIME_SAMPLES / 2
        );
        assert_eq!(
            minimum_scale_overlap_samples(
                ScaleDirection::Bidirectional,
                SCALE_SUSTAINED_PAYLOAD_BYTES
            ),
            SCALE_REALTIME_SAMPLES / 2
        );
    }

    #[test]
    fn scale_checkpoint_atomically_retains_current_failure() {
        let path = std::env::temp_dir().join(format!(
            "anonssh-scale-checkpoint-test-{}.json",
            std::process::id()
        ));
        let temporary = path.with_extension("tmp");
        let _ = fs::remove_file(&path);
        let _ = fs::remove_file(&temporary);
        let config = ScaleCampaignConfig::new(16, 4).unwrap();
        let matrix = config.matrix();
        let scenario = matrix[8];
        write_scale_checkpoint(
            &path,
            "error",
            &config,
            matrix.len(),
            &[],
            Some(ScaleCheckpointTrial::new(
                9,
                scenario,
                ScaleRouterState::Retained,
            )),
            Some("round stalled after bulk close"),
        )
        .unwrap();

        let checkpoint: serde_json::Value =
            serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
        assert_eq!(checkpoint["schema"], SCALE_SCHEMA);
        assert_eq!(checkpoint["status"], "error");
        assert_eq!(checkpoint["completed_trials"], 0);
        assert_eq!(checkpoint["total_trials"], matrix.len());
        assert_eq!(checkpoint["maximum_slots_per_provider"], 16);
        assert_eq!(checkpoint["rounds_per_trial"], 4);
        assert_eq!(checkpoint["current_trial"]["sequence"], 9);
        assert_eq!(checkpoint["current_trial"]["direction"], "bidirectional");
        assert_eq!(checkpoint["current_trial"]["router_state"], "retained");
        assert_eq!(checkpoint["error"], "round stalled after bulk close");
        assert!(!temporary.exists());
        fs::remove_file(path).unwrap();
    }

    #[test]
    fn scale_round_timeout_progress_identifies_lifecycle_boundary() {
        let progress = ScaleRoundProgress::new(2);
        progress.bulk_payloads_written.store(1, Ordering::Release);
        progress
            .realtime_requests_started
            .store(8, Ordering::Release);
        progress.realtime_echoes.store(7, Ordering::Release);
        let summary = progress.summary();

        assert!(summary.contains("bulk_payloads_written=1/2"));
        assert!(summary.contains("bulk_writes_closed=0/2"));
        assert!(summary.contains("realtime_requests_started=8/8"));
        assert!(summary.contains("realtime_echoes=7/8"));
        assert!(summary.contains("acknowledgement_drain_complete=false"));
    }

    #[tokio::test]
    async fn fixed_cadence_realtime_requests_do_not_wait_for_slow_echoes() {
        let (client, server) = tokio::io::duplex(4 * 1024);
        let bulk_active = AtomicBool::new(true);
        let progress = ScaleRoundProgress::new(0);
        let observe_requests = async {
            tokio::time::timeout(Duration::from_millis(500), async {
                while progress.realtime_requests_started.load(Ordering::Acquire)
                    < SCALE_REALTIME_SAMPLES
                {
                    tokio::task::yield_now().await;
                }
            })
            .await
            .expect("all requests must start before the delayed first echo");
            assert_eq!(progress.realtime_echoes.load(Ordering::Acquire), 0);
            bulk_active.store(false, Ordering::Release);
            Ok::<_, anyhow::Error>(())
        };
        let transfer = run_scale_realtime_samples(
            client,
            server,
            RealtimeSampleConfig {
                round: 7,
                sample_count: SCALE_REALTIME_SAMPLES,
                sample_interval: Duration::from_millis(1),
                initial_echo_delay: Duration::from_secs(1),
            },
            &bulk_active,
            &progress,
        );

        let (latencies, ()) = tokio::try_join!(transfer, observe_requests).unwrap();
        assert_eq!(latencies.len(), SCALE_REALTIME_SAMPLES);
        assert_eq!(
            progress.realtime_echoes.load(Ordering::Acquire),
            SCALE_REALTIME_SAMPLES
        );
    }

    #[tokio::test]
    async fn endurance_quiet_phase_echoes_over_one_redundant_stream() {
        let session_id = 0x454e_4455_5245;
        let key = BondSessionKey::new([0x6d; 32]);
        let server_incarnation = ServerIncarnation::from_u64(0x454e_4455_5245).unwrap();
        let mut client_lanes = Vec::new();
        let mut server_lanes = Vec::new();
        for lane_number in 1..=2 {
            let lane = LaneConfig::new(
                LaneId::new(lane_number).unwrap(),
                FailureDomain::new(u64::from(lane_number)).unwrap(),
                Duration::from_millis(u64::from(lane_number) * 5),
                100_000_000,
            )
            .unwrap();
            let join = LaneJoin::new(session_id, lane.id, lane.failure_domain).unwrap();
            let (client_io, server_io) = tokio::io::duplex(64 * 1024);
            let (client_lane, server_lane) = tokio::join!(
                authenticate_client_lane(client_io, &key, join, Duration::from_secs(5)),
                authenticate_server_lane_with_incarnation(
                    server_io,
                    &key,
                    join,
                    server_incarnation,
                    Duration::from_secs(5),
                ),
            );
            client_lanes.push(RuntimeLane::from_authenticated(lane, client_lane.unwrap()));
            server_lanes.push(RuntimeLane::from_authenticated(lane, server_lane.unwrap()));
        }
        let config = BondRuntimeConfig {
            session_id,
            scheduler: SchedulerConfig {
                low_latency_lane_count: 2,
                ..SchedulerConfig::default()
            },
            sender: SenderConfig {
                redundant_realtime: true,
                ..SenderConfig::default()
            },
            max_reorder_bytes_per_stream: 1024 * 1024,
            max_receive_streams: 8,
            stream_receive_window: 1024 * 1024,
            max_ack_ranges: 16,
            require_stream_open: true,
            retransmit_after: Duration::from_secs(2),
            retransmit_scan_interval: Duration::from_millis(10),
        };
        let client = BondSession::spawn(config, client_lanes, SessionRole::Dialer).unwrap();
        let server = BondSession::spawn(config, server_lanes, SessionRole::Listener).unwrap();

        let latencies = run_endurance_quiet_phase(
            &client,
            &server,
            7,
            Duration::from_millis(u64::try_from(ENDURANCE_QUIET_REALTIME_SAMPLES - 1).unwrap()),
        )
        .await
        .unwrap();
        assert_eq!(latencies.len(), ENDURANCE_QUIET_REALTIME_SAMPLES);
        let (client_stats, server_stats) = wait_until_pair_acknowledged(&client, &server)
            .await
            .unwrap();
        for stats in [client_stats, server_stats] {
            assert!((1..=ENDURANCE_QUIET_REALTIME_SAMPLES as u64).contains(&stats.new_data_frames));
            assert_eq!(stats.redundant_realtime_frames, stats.new_data_frames);
            assert_eq!(stats.dropped_redundant_realtime_frames, 0);
            assert_eq!(stats.unacknowledged_bytes, 0);
            assert_eq!(stats.active_streams, 0);
            assert_eq!(stats.retired_stream_tombstones, 1);
        }

        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
    }

    #[tokio::test]
    async fn simultaneous_bulk_streams_preserve_distinct_payloads() {
        let session_id = 0x5343_414c_4501;
        let lane = LaneConfig::new(
            LaneId::new(1).unwrap(),
            FailureDomain::new(1).unwrap(),
            Duration::from_millis(5),
            100_000_000,
        )
        .unwrap();
        let join = LaneJoin::new(session_id, lane.id, lane.failure_domain).unwrap();
        let key = BondSessionKey::new([0x5c; 32]);
        let (client_io, server_io) = tokio::io::duplex(1024 * 1024);
        let (client_lane, server_lane) = tokio::join!(
            authenticate_client_lane(client_io, &key, join, Duration::from_secs(5)),
            authenticate_server_lane(server_io, &key, join, Duration::from_secs(5)),
        );
        let config = BondRuntimeConfig {
            session_id,
            scheduler: SchedulerConfig::default(),
            sender: SenderConfig {
                max_unacknowledged_bytes: 1024 * 1024,
                max_unacknowledged_chunks: 256,
                ..SenderConfig::default()
            },
            max_reorder_bytes_per_stream: 1024 * 1024,
            max_receive_streams: 8,
            stream_receive_window: 1024 * 1024,
            max_ack_ranges: 16,
            require_stream_open: true,
            retransmit_after: Duration::from_secs(2),
            retransmit_scan_interval: Duration::from_millis(10),
        };
        let client = BondSession::spawn(
            config,
            vec![RuntimeLane::from_authenticated(lane, client_lane.unwrap())],
            SessionRole::Dialer,
        )
        .unwrap();
        let server = BondSession::spawn(
            config,
            vec![RuntimeLane::from_authenticated(lane, server_lane.unwrap())],
            SessionRole::Listener,
        )
        .unwrap();

        let client_to_server = open_scale_bulk_stream(&client, &server, "client-to-server")
            .await
            .unwrap();
        let server_to_client = open_scale_bulk_stream(&server, &client, "server-to-client")
            .await
            .unwrap();
        let forward = vec![0x31; 256 * 1024];
        let reverse = vec![0xa7; 256 * 1024];
        let progress = ScaleRoundProgress::new(2);
        tokio::time::timeout(Duration::from_secs(10), async {
            tokio::try_join!(
                transfer_scale_bulk_stream(
                    client_to_server.0,
                    client_to_server.1,
                    &forward,
                    &progress,
                    "client-to-server",
                ),
                transfer_scale_bulk_stream(
                    server_to_client.0,
                    server_to_client.1,
                    &reverse,
                    &progress,
                    "server-to-client",
                ),
            )
        })
        .await
        .unwrap()
        .unwrap();
        wait_until_pair_acknowledged(&client, &server)
            .await
            .unwrap();
        assert_eq!(progress.bulk_payloads_written.load(Ordering::Acquire), 2);
        assert_eq!(progress.bulk_writes_closed.load(Ordering::Acquire), 2);
        assert_eq!(progress.bulk_eofs_received.load(Ordering::Acquire), 2);
        assert_eq!(progress.bulk_reverse_closes.load(Ordering::Acquire), 2);

        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
    }

    #[test]
    fn i2p_plan_uses_two_router_domains_for_bulk() {
        let plan = i2p_pool_plan().unwrap();
        assert!(plan.iter().all(|lane| lane.provider == Provider::I2p));
        assert_eq!(
            plan[1..]
                .iter()
                .map(|lane| lane.config.failure_domain)
                .collect::<BTreeSet<_>>()
                .len(),
            2
        );
    }

    #[tokio::test]
    async fn always_ready_formation_pressure_yields_to_its_observer() {
        let (stop, stop_rx) = watch::channel(false);
        let mut sink = tokio::io::sink();
        let chunk = vec![0_u8; 64 * 1024];
        let writer = write_scale_formation_pressure(&mut sink, stop_rx, &chunk);
        let observer = async {
            tokio::task::yield_now().await;
            tokio::task::yield_now().await;
            stop.send(true).unwrap();
            Ok::<(), anyhow::Error>(())
        };
        let (sent, ()) = tokio::time::timeout(Duration::from_secs(1), async {
            tokio::try_join!(writer, observer)
        })
        .await
        .expect("an always-ready pressure writer must not starve its observer")
        .unwrap();

        assert!(sent >= SCALE_PRESSURE_YIELD_BYTES as u64);
        assert_eq!(sent % SCALE_PRESSURE_YIELD_BYTES as u64, 0);
    }

    #[tokio::test]
    async fn blocked_formation_pressure_observes_stop_without_a_completed_write() {
        let (stop, stop_rx) = watch::channel(false);
        let (mut writer, _reader) = tokio::io::duplex(1);
        let chunk = vec![0_u8; 64 * 1024];
        let pressure = write_scale_formation_pressure(&mut writer, stop_rx, &chunk);
        let observer = async {
            tokio::task::yield_now().await;
            stop.send(true).unwrap();
            Ok::<(), anyhow::Error>(())
        };
        let (sent, ()) = tokio::time::timeout(Duration::from_secs(1), async {
            tokio::try_join!(pressure, observer)
        })
        .await
        .expect("a blocked pressure write must remain cancellation-safe")
        .unwrap();

        assert!(sent < chunk.len() as u64);
    }
}
