use std::collections::{BTreeMap, BTreeSet, VecDeque};
use std::sync::{Arc, Mutex as StdMutex};
use std::time::{Duration, Instant};

#[cfg(test)]
use anonssh_bond::ScalingConfig;
use anonssh_bond::{
    AdaptiveScalingController, CapabilityAdvertisement, CapabilityFeatures, CapabilityIntersection,
    EndpointDescriptor, EndpointProvider, FailureDomain, LaneConfig, LaneId, LaneScalingSample,
    ProviderCapability, ProviderId, ResourceUsage, ScalingAction, ScalingPressure, ScalingReason,
    SchedulerConfig, SenderConfig, TopologyAction, TopologyAdvertisement, TrafficClass,
};
use anonssh_bond_tokio::{
    authenticate_client_lane, fresh_session_id, prepare_server_lane, AuthenticatedLane,
    BondRuntimeConfig, BondRuntimeStats, BondSession, BondSessionControl, BondSessionKey, LaneJoin,
    PreparedClientLane, RuntimeLane, ServerIncarnation, SessionRole,
};
use anyhow::{bail, Context, Result};
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::{mpsc, watch, Mutex};
use tokio::task::{JoinHandle, JoinSet};
use tracing::{info, warn};
use zeroize::Zeroizing;

mod admission;
mod learning;
mod resource_governor;

use admission::{run_admission_coordinator, AdmissionCommand, PreparedIngressLane};
use learning::{LearnedScalingController, LearnedScalingSnapshot};
use resource_governor::PhysicalPathObservation;
pub(crate) use resource_governor::{ResourceGovernorSnapshot, SharedResourceGovernor};

use crate::data_stream;
use crate::identity::DerivedServerRecoveryIdentity;
use crate::product_config::ScalingPolicy;
use crate::router_pool::{I2pPoolSlot, RouterPool, TorPoolSlot};
use crate::runtime::i2p_start_timeout;
use crate::sam::{setup_timeout as sam_setup_timeout, SamConnector, SamListener};
use crate::tor_transport::{TorConnector, TorListener};

pub const BOND_SERVICE_PORT: u16 = 22_424;
const HANDSHAKE_TIMEOUT: Duration = Duration::from_secs(30);
const INITIAL_LANE_DEADLINE: Duration = Duration::from_secs(300);
const INITIAL_TOR_AUTH_ATTEMPTS: usize = 30;
const TOR_AUTH_ATTEMPTS: usize = 3;
const TOR_CONNECT_ATTEMPTS: usize = 3;
const TOR_RETRY_DELAY: Duration = Duration::from_secs(2);
const TOR_LANE_ESTABLISHMENT_DEADLINE: Duration = Duration::from_secs(80);
const I2P_CONNECT_ATTEMPTS: usize = 30;
const I2P_RETRY_DELAY: Duration = Duration::from_secs(10);
const INNER_DEADLINE_MARGIN: Duration = Duration::from_secs(60);
pub(crate) const TOR_ONLY_LANE_OFFSET: u32 = 16;
pub(crate) const I2P_ONLY_LANE_OFFSET: u32 = 24;
const POOL_HEALTH_INTERVAL: Duration = Duration::from_secs(1);
const POOL_REPAIR_RETRY_DELAY: Duration = Duration::from_secs(5);
const SLOT_REPAIR_BACKOFF_MIN: Duration = Duration::from_secs(1);
const SLOT_REPAIR_BACKOFF_MAX: Duration = Duration::from_secs(60);
const MAX_PENDING_SESSIONS: usize = 16;
const MAX_ACTIVE_SESSIONS: usize = 64;
const MAX_LEGACY_SESSION_JOIN_NONCES: usize = 256;
const SESSION_JOIN_REPLAY_WINDOW_BITS: usize = 256;
const MAX_INFLIGHT_HANDSHAKES: usize = 32;
const MAX_INFLIGHT_ADMISSION_COMPLETIONS: usize = 32;
const ADMISSION_CHANNEL_CAPACITY: usize = 64;
const COMPLETED_SESSION_CAPACITY: usize = 16;
const IMMEDIATE_SEND_PRESSURE_PERCENT: u8 = 75;
const SUSTAINED_SEND_PRESSURE_SAMPLES: u8 = 2;
const SCALING_UNHEALTHY_AFTER: Duration = Duration::from_secs(300);
const SCALING_DRAIN_DWELL: Duration = Duration::from_secs(60);
const SCALING_MARGINAL_DRAIN_SAMPLES: u8 = 6;
const SCALING_PENDING_CANCEL_SAMPLES: u8 = 2;
const MAX_SCALING_EVENTS: usize = 64;
const ESTIMATED_TOR_CPU_MILLICORES: u32 = 75;
const ESTIMATED_I2P_CPU_MILLICORES: u32 = 200;
const ESTIMATED_TOR_MEMORY_BYTES: u64 = 128 * 1024 * 1024;
const ESTIMATED_I2P_MEMORY_BYTES: u64 = 256 * 1024 * 1024;
const ESTIMATED_TOR_STARTUP: Duration = Duration::from_secs(30);
const ESTIMATED_I2P_STARTUP: Duration = Duration::from_secs(120);
const PRODUCT_SEND_WINDOW_BYTES: usize = 8 * 1024 * 1024;
const CAPABILITY_EXCHANGE_TIMEOUT: Duration = Duration::from_secs(30);
const SESSION_OUTAGE_DEADLINE: Duration = Duration::from_secs(30);

#[derive(Default)]
struct SessionOutageGuard {
    lost_since: Option<Instant>,
}

impl SessionOutageGuard {
    fn observe(&mut self, now: Instant, active_lanes: usize) -> bool {
        if active_lanes > 0 {
            self.lost_since = None;
            return false;
        }
        let lost_since = self.lost_since.get_or_insert(now);
        now.saturating_duration_since(*lost_since) >= SESSION_OUTAGE_DEADLINE
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Provider {
    Tor { slot: u32 },
    I2p { slot: u32 },
}

fn i2p_connect_deadline_for(sam_timeout: Duration) -> Duration {
    sam_timeout.saturating_add(INNER_DEADLINE_MARGIN)
}

fn i2p_attempt_timeout(remaining: Duration, sam_timeout: Duration) -> Duration {
    remaining.min(sam_timeout)
}

fn i2p_discovery_deadline_for(router_start_timeout: Duration, sam_timeout: Duration) -> Duration {
    router_start_timeout
        .saturating_add(sam_timeout)
        .saturating_add(INNER_DEADLINE_MARGIN)
}

fn discovery_publication_deadline(provider: Provider) -> Duration {
    match provider {
        Provider::Tor { .. } => INITIAL_LANE_DEADLINE,
        Provider::I2p { .. } => {
            i2p_discovery_deadline_for(i2p_start_timeout(), sam_setup_timeout())
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct PlannedLane {
    config: LaneConfig,
    provider: Provider,
}

struct LaneDemand {
    baseline: BTreeSet<LaneId>,
    senders: BTreeMap<LaneId, watch::Sender<bool>>,
    providers: BTreeMap<LaneId, Provider>,
    governor: Arc<SharedResourceGovernor>,
    session_id: u64,
}

#[derive(Clone)]
struct ClientLaneContext {
    key: Arc<BondSessionKey>,
    demand: Arc<LaneDemand>,
    server_incarnation: Option<ServerIncarnation>,
}

#[derive(Debug)]
struct ServerIncarnationChanged {
    expected: u64,
    actual: u64,
}

impl std::fmt::Display for ServerIncarnationChanged {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            formatter,
            "bond server process changed (expected incarnation {}, received {})",
            self.expected, self.actual
        )
    }
}

impl std::error::Error for ServerIncarnationChanged {}

fn validate_server_incarnation<T>(
    lane: &AuthenticatedLane<T>,
    expected: Option<ServerIncarnation>,
) -> Result<()> {
    let actual = lane.server_incarnation()?;
    if let (Some(expected), Some(actual)) = (expected, actual) {
        if expected != actual {
            return Err(ServerIncarnationChanged {
                expected: expected.get(),
                actual: actual.get(),
            }
            .into());
        }
    }
    Ok(())
}

#[derive(Default)]
struct PendingPressureAdmissions {
    lanes: BTreeSet<LaneId>,
    quiet_observations: u8,
}

impl PendingPressureAdmissions {
    fn record(&mut self, actions: &[ScalingAction]) {
        for action in actions {
            match *action {
                ScalingAction::Admit {
                    lane_id,
                    reason: ScalingReason::QueuePressure,
                } => {
                    self.lanes.insert(lane_id);
                }
                ScalingAction::Drain { lane_id, .. } => {
                    self.lanes.remove(&lane_id);
                }
                ScalingAction::Replace { remove, .. } => {
                    self.lanes.remove(&remove);
                }
                _ => {}
            }
        }
    }

    fn cancellation_actions(
        &mut self,
        active_lanes: &BTreeSet<LaneId>,
        pressure_active: bool,
    ) -> Vec<ScalingAction> {
        self.lanes.retain(|lane_id| !active_lanes.contains(lane_id));
        if self.lanes.is_empty() || pressure_active {
            self.quiet_observations = 0;
            return Vec::new();
        }
        self.quiet_observations = self.quiet_observations.saturating_add(1);
        if self.quiet_observations < SCALING_PENDING_CANCEL_SAMPLES {
            return Vec::new();
        }
        self.quiet_observations = 0;
        let actions = self
            .lanes
            .iter()
            .copied()
            .map(|lane_id| ScalingAction::Drain {
                lane_id,
                reason: ScalingReason::PressureCleared,
            })
            .collect();
        self.lanes.clear();
        actions
    }
}

#[derive(Clone, Debug)]
pub(crate) struct AdaptiveScalingEvent {
    pub generation: u64,
    pub elapsed_millis: u64,
    pub learned: LearnedScalingSnapshot,
    pub actions: Vec<ScalingAction>,
}

#[derive(Clone, Debug)]
pub(crate) struct AdaptiveScalingProgress {
    pub observed_millis: u64,
    pub desired_lane_ids: Vec<u32>,
    pub pending_pressure_lane_ids: Vec<u32>,
    pub learned: LearnedScalingSnapshot,
    pub events: Vec<AdaptiveScalingEvent>,
}

struct AdaptiveScalingTelemetry {
    started_at: Instant,
    desired_lanes: BTreeSet<LaneId>,
    pending_pressure_lanes: BTreeSet<LaneId>,
    learned: LearnedScalingSnapshot,
    events: VecDeque<AdaptiveScalingEvent>,
}

struct AdaptiveControllerContext<'a> {
    session: &'a BondSession,
    pool: &'a RouterPool,
    plan: Vec<PlannedLane>,
    demand: Arc<LaneDemand>,
    tor_destinations: Vec<String>,
    i2p_destinations: Vec<String>,
    telemetry: Arc<StdMutex<AdaptiveScalingTelemetry>>,
    policy: ScalingPolicy,
    peer_capabilities: Option<CapabilityAdvertisement>,
}

impl Default for AdaptiveScalingTelemetry {
    fn default() -> Self {
        Self {
            started_at: Instant::now(),
            desired_lanes: BTreeSet::new(),
            pending_pressure_lanes: BTreeSet::new(),
            learned: LearnedScalingSnapshot::default(),
            events: VecDeque::new(),
        }
    }
}

impl AdaptiveScalingTelemetry {
    fn initialize(&mut self, desired_lanes: BTreeSet<LaneId>) {
        self.started_at = Instant::now();
        self.desired_lanes = desired_lanes;
        self.pending_pressure_lanes.clear();
        self.learned = LearnedScalingSnapshot::default();
        self.events.clear();
    }

    fn record(
        &mut self,
        generation: u64,
        actions: &[ScalingAction],
        pending_pressure_lanes: &BTreeSet<LaneId>,
    ) {
        for action in actions {
            match *action {
                ScalingAction::Hold => {}
                ScalingAction::Admit { lane_id, .. } => {
                    self.desired_lanes.insert(lane_id);
                }
                ScalingAction::Drain { lane_id, .. } => {
                    self.desired_lanes.remove(&lane_id);
                }
                ScalingAction::Replace { remove, admit, .. } => {
                    self.desired_lanes.remove(&remove);
                    self.desired_lanes.insert(admit);
                }
            }
        }
        self.pending_pressure_lanes = pending_pressure_lanes.clone();
        if self.events.len() == MAX_SCALING_EVENTS {
            self.events.pop_front();
        }
        self.events.push_back(AdaptiveScalingEvent {
            generation,
            elapsed_millis: duration_millis(self.started_at.elapsed()),
            learned: self.learned,
            actions: actions.to_vec(),
        });
    }

    fn observe_pending_pressure(&mut self, pending_pressure_lanes: &BTreeSet<LaneId>) {
        self.pending_pressure_lanes = pending_pressure_lanes.clone();
    }

    fn observe_learning(&mut self, learned: LearnedScalingSnapshot) {
        self.learned = learned;
    }

    fn snapshot(&self) -> AdaptiveScalingProgress {
        AdaptiveScalingProgress {
            observed_millis: duration_millis(self.started_at.elapsed()),
            desired_lane_ids: self.desired_lanes.iter().map(|lane| lane.get()).collect(),
            pending_pressure_lane_ids: self
                .pending_pressure_lanes
                .iter()
                .map(|lane| lane.get())
                .collect(),
            learned: self.learned,
            events: self.events.iter().cloned().collect(),
        }
    }
}

fn duration_millis(duration: Duration) -> u64 {
    u64::try_from(duration.as_millis()).unwrap_or(u64::MAX)
}

#[derive(Clone, Copy)]
enum LaneSupervisionMode {
    Adaptive,
    FixedAll,
}

struct IngressDemand {
    baseline: BTreeSet<LaneId>,
    senders: BTreeMap<LaneId, watch::Sender<bool>>,
    providers: BTreeMap<LaneId, Provider>,
    sessions: Mutex<BTreeMap<u64, BTreeSet<LaneId>>>,
    governor: Arc<SharedResourceGovernor>,
}

impl IngressDemand {
    fn new(
        plan: &[PlannedLane],
        policy: ScalingPolicy,
    ) -> Result<(Self, BTreeMap<LaneId, watch::Receiver<bool>>)> {
        let baseline = baseline_lanes(plan);
        let providers = plan
            .iter()
            .map(|planned| (planned.config.id, planned.provider))
            .collect::<BTreeMap<_, _>>();
        let governor = Arc::new(SharedResourceGovernor::new(policy));
        governor.register_candidates(
            u64::MAX,
            baseline
                .iter()
                .map(|lane_id| {
                    providers
                        .get(lane_id)
                        .copied()
                        .context("ingress baseline omitted a physical provider")
                })
                .collect::<Result<BTreeSet<_>>>()?,
            providers.values().copied().collect(),
        )?;
        let mut senders = BTreeMap::new();
        let mut receivers = BTreeMap::new();
        for planned in plan {
            let enabled = baseline.contains(&planned.config.id);
            let (sender, receiver) = watch::channel(enabled);
            senders.insert(planned.config.id, sender);
            receivers.insert(planned.config.id, receiver);
        }
        Ok((
            Self {
                baseline,
                senders,
                providers,
                sessions: Mutex::new(BTreeMap::new()),
                governor,
            },
            receivers,
        ))
    }

    async fn set(&self, session_id: u64, lane_id: LaneId, enabled: bool) -> Result<()> {
        if !enabled && self.baseline.contains(&lane_id) {
            bail!("peer cannot drain baseline lane {}", lane_id.get());
        }
        if !self.senders.contains_key(&lane_id) {
            bail!("peer requested unknown lane {}", lane_id.get());
        }
        let mut sessions = self.sessions.lock().await;
        if !self.governor.contains_session(session_id)? {
            self.governor.register_candidates(
                session_id,
                BTreeSet::new(),
                self.providers.values().copied().collect(),
            )?;
        }
        let lanes = sessions.entry(session_id).or_default();
        if enabled {
            let provider = self
                .providers
                .get(&lane_id)
                .copied()
                .context("ingress demand omitted a physical provider")?;
            if !self.baseline.contains(&lane_id)
                && !self.governor.try_set(session_id, provider, true)?
            {
                return Ok(());
            }
            lanes.insert(lane_id);
        } else {
            lanes.remove(&lane_id);
            if !self.baseline.contains(&lane_id) {
                let provider = self
                    .providers
                    .get(&lane_id)
                    .copied()
                    .context("ingress demand omitted a physical provider")?;
                self.governor.try_set(session_id, provider, false)?;
            }
        }
        self.publish_effective(lane_id, &sessions)
    }

    async fn release(&self, session_id: u64) -> Result<()> {
        let mut sessions = self.sessions.lock().await;
        let removed = sessions.remove(&session_id).unwrap_or_default();
        self.governor.unregister(session_id)?;
        for lane_id in removed {
            self.publish_effective(lane_id, &sessions)?;
        }
        Ok(())
    }

    fn publish_effective(
        &self,
        lane_id: LaneId,
        sessions: &BTreeMap<u64, BTreeSet<LaneId>>,
    ) -> Result<()> {
        let enabled = self.baseline.contains(&lane_id)
            || sessions.values().any(|lanes| lanes.contains(&lane_id));
        self.senders
            .get(&lane_id)
            .context("ingress activation omitted a lane")?
            .send(enabled)
            .map_err(|_| anyhow::anyhow!("lane {} ingress supervisor stopped", lane_id.get()))
    }
}

impl LaneDemand {
    fn new(
        plan: &[PlannedLane],
        governor: Arc<SharedResourceGovernor>,
        session_id: u64,
    ) -> Result<(Self, BTreeMap<LaneId, watch::Receiver<bool>>)> {
        let baseline = baseline_lanes(plan);
        let providers = plan
            .iter()
            .map(|planned| (planned.config.id, planned.provider))
            .collect::<BTreeMap<_, _>>();
        let mut senders = BTreeMap::new();
        let mut receivers = BTreeMap::new();
        for planned in plan {
            let desired = baseline.contains(&planned.config.id);
            let (sender, receiver) = watch::channel(desired);
            senders.insert(planned.config.id, sender);
            receivers.insert(planned.config.id, receiver);
        }
        if !governor.contains_session(session_id)? {
            bail!("adaptive session has no shared resource claim")
        }
        governor.replace_desired(
            session_id,
            baseline
                .iter()
                .map(|lane_id| {
                    providers
                        .get(lane_id)
                        .copied()
                        .context("adaptive baseline omitted a physical provider")
                })
                .collect::<Result<BTreeSet<_>>>()?,
        )?;
        Ok((
            Self {
                baseline,
                senders,
                providers,
                governor,
                session_id,
            },
            receivers,
        ))
    }

    fn is_desired(&self, lane_id: LaneId) -> Result<bool> {
        self.senders
            .get(&lane_id)
            .map(|sender| *sender.borrow())
            .with_context(|| format!("adaptive controller omitted lane {}", lane_id.get()))
    }

    fn set(&self, lane_id: LaneId, desired: bool) -> Result<()> {
        if !desired && self.baseline.contains(&lane_id) {
            bail!(
                "adaptive controller cannot drain baseline lane {}",
                lane_id.get()
            );
        }
        self.senders
            .get(&lane_id)
            .with_context(|| format!("adaptive controller omitted lane {}", lane_id.get()))?
            .send(desired)
            .map_err(|_| anyhow::anyhow!("lane {} supervisor stopped", lane_id.get()))
    }

    fn set_all(&self) -> Result<()> {
        self.governor
            .replace_desired(self.session_id, self.providers.values().copied().collect())?;
        for (lane_id, sender) in &self.senders {
            sender
                .send(true)
                .map_err(|_| anyhow::anyhow!("lane {} supervisor stopped", lane_id.get()))?;
        }
        Ok(())
    }

    fn reserve_actions(
        &self,
        actions: &[ScalingAction],
    ) -> Result<resource_governor::ActionReservation> {
        self.governor
            .reserve_actions(self.session_id, &self.providers, actions)
    }

    fn report_observations(&self, observations: &[PhysicalPathObservation]) -> Result<()> {
        self.governor
            .report_observations(self.session_id, observations)
    }
}

fn baseline_lanes(plan: &[PlannedLane]) -> BTreeSet<LaneId> {
    let providers = plan
        .iter()
        .map(|planned| provider_id(planned.provider))
        .collect::<BTreeSet<_>>();
    let lanes_per_provider = if providers.len() > 1 { 2 } else { 4 };
    let mut selected = BTreeSet::new();
    for provider in providers {
        selected.extend(
            plan.iter()
                .filter(|planned| provider_id(planned.provider) == provider)
                .take(lanes_per_provider)
                .map(|planned| planned.config.id),
        );
    }
    selected
}

fn baseline_providers(plan: &[PlannedLane]) -> BTreeSet<Provider> {
    let baseline = baseline_lanes(plan);
    plan.iter()
        .filter(|planned| baseline.contains(&planned.config.id))
        .map(|planned| planned.provider)
        .collect()
}

fn discovery_lanes(plan: &[PlannedLane]) -> Vec<PlannedLane> {
    let mut providers = BTreeSet::new();
    plan.iter()
        .filter(|planned| providers.insert(provider_id(planned.provider)))
        .copied()
        .collect()
}

fn product_capabilities(
    generation: u64,
    protocol_version: anonssh_bond_tokio::BondProtocolVersion,
    plan: &[PlannedLane],
    policy: ScalingPolicy,
    stats: &BondRuntimeStats,
) -> Result<CapabilityAdvertisement> {
    let mut providers = Vec::new();
    for (provider, endpoint_provider, startup) in [
        (
            ProviderId::new(1)?,
            EndpointProvider::Tor,
            ESTIMATED_TOR_STARTUP,
        ),
        (
            ProviderId::new(2)?,
            EndpointProvider::I2p,
            ESTIMATED_I2P_STARTUP,
        ),
    ] {
        let candidates = plan
            .iter()
            .filter(|lane| provider_id(lane.provider) == provider)
            .collect::<Vec<_>>();
        if candidates.is_empty() {
            continue;
        }
        let snapshots = candidates
            .iter()
            .filter_map(|planned| stats.lanes.iter().find(|lane| lane.id == planned.config.id))
            .collect::<Vec<_>>();
        let ready = snapshots.iter().filter(|lane| lane.active).count();
        let queue_delay_micros = snapshots
            .iter()
            .filter_map(|lane| lane.queued_through.duration_since(stats.observed_at))
            .map(|delay| u32::try_from(delay.as_micros()).unwrap_or(u32::MAX))
            .max()
            .unwrap_or(0);
        let delivered_kbps = snapshots
            .iter()
            .map(|lane| lane.delivery_rate_bps / 1_000)
            .fold(0_u64, u64::saturating_add);
        providers.push(ProviderCapability::new(
            endpoint_provider,
            u8::try_from(candidates.len()).context("capability candidate count overflow")?,
            u8::try_from(ready).context("capability ready count overflow")?,
            u32::try_from(startup.as_millis()).unwrap_or(u32::MAX),
            queue_delay_micros,
            u32::try_from(delivered_kbps).unwrap_or(u32::MAX),
        )?);
    }
    let active_lanes = stats.lanes.iter().filter(|lane| lane.active).count();
    let max_active_lanes = policy.maximum_active_lanes.min(plan.len());
    CapabilityAdvertisement::new(
        generation,
        if protocol_version >= anonssh_bond_tokio::BondProtocolVersion::V6 {
            CapabilityFeatures::CURRENT
        } else {
            CapabilityFeatures::V5_CURRENT
        },
        policy.maximum_memory_bytes,
        policy.maximum_cpu_millicores,
        providers
            .iter()
            .map(|provider| provider.queue_delay_micros)
            .max()
            .unwrap_or(0),
        u16::try_from(max_active_lanes).context("capability lane ceiling overflow")?,
        u16::try_from(MAX_ACTIVE_SESSIONS).context("capability session ceiling overflow")?,
        u16::try_from(active_lanes).context("capability active lane count overflow")?,
        providers,
    )
    .map_err(Into::into)
}

fn constrained_plan(
    plan: &[PlannedLane],
    capabilities: &CapabilityIntersection,
) -> Result<Vec<PlannedLane>> {
    let limits = capabilities
        .providers
        .iter()
        .map(|provider| (provider.provider, usize::from(provider.candidates)))
        .collect::<BTreeMap<_, _>>();
    let mut selected = BTreeMap::<EndpointProvider, usize>::new();
    let mut constrained = Vec::new();
    for planned in plan {
        let provider = endpoint_provider(planned.provider);
        let selected_for_provider = selected.entry(provider).or_default();
        if *selected_for_provider < limits.get(&provider).copied().unwrap_or(0) {
            constrained.push(*planned);
            *selected_for_provider += 1;
        }
    }
    if constrained.is_empty() {
        bail!("negotiated bond capabilities have no usable lanes");
    }
    Ok(constrained)
}

fn negotiated_scaling_policy(
    local: ScalingPolicy,
    capabilities: &CapabilityIntersection,
) -> ScalingPolicy {
    let maximum_active_lanes = local
        .maximum_active_lanes
        .min(usize::from(capabilities.max_active_lanes));
    ScalingPolicy {
        maximum_active_lanes,
        maximum_admissions_per_interval: local
            .maximum_admissions_per_interval
            .min(maximum_active_lanes),
        maximum_drains_per_interval: local.maximum_drains_per_interval.min(maximum_active_lanes),
        maximum_cpu_millicores: local
            .maximum_cpu_millicores
            .min(capabilities.cpu_ceiling_millicores),
        maximum_memory_bytes: local
            .maximum_memory_bytes
            .min(capabilities.memory_ceiling_bytes),
        ..local
    }
}

fn endpoint_provider(provider: Provider) -> EndpointProvider {
    match provider {
        Provider::Tor { .. } => EndpointProvider::Tor,
        Provider::I2p { .. } => EndpointProvider::I2p,
    }
}

pub struct BondIngress {
    completed_rx: Mutex<mpsc::Receiver<BondSession>>,
    admission_tx: mpsc::Sender<AdmissionCommand>,
    demand: Arc<IngressDemand>,
    descriptors: BTreeMap<LaneId, EndpointDescriptor>,
    plan: Vec<PlannedLane>,
    scaling_policy: ScalingPolicy,
    negotiated_capabilities: Mutex<BTreeMap<u64, CapabilityIntersection>>,
    capability_generations: Mutex<BTreeMap<u64, u64>>,
    tasks: Vec<JoinHandle<()>>,
}

impl BondIngress {
    pub async fn publish(
        pool: &RouterPool,
        identity: &DerivedServerRecoveryIdentity,
    ) -> Result<Self> {
        Self::publish_inner(pool, identity, None, ScalingPolicy::performance()).await
    }

    pub(crate) async fn publish_with_scaling_policy(
        pool: &RouterPool,
        identity: &DerivedServerRecoveryIdentity,
        scaling_policy: ScalingPolicy,
    ) -> Result<Self> {
        Self::publish_inner(pool, identity, None, scaling_policy).await
    }

    pub async fn publish_with_direct_tor(
        pool: &RouterPool,
        identity: &DerivedServerRecoveryIdentity,
        direct_backend: std::net::SocketAddr,
        scaling_policy: ScalingPolicy,
    ) -> Result<Self> {
        Self::publish_inner(pool, identity, Some(direct_backend), scaling_policy).await
    }

    async fn publish_inner(
        pool: &RouterPool,
        identity: &DerivedServerRecoveryIdentity,
        direct_backend: Option<std::net::SocketAddr>,
        scaling_policy: ScalingPolicy,
    ) -> Result<Self> {
        validate_pool_identities(pool, identity.tor_pool.len(), identity.i2p_pool.len())?;
        let plan = production_plan(pool)?;
        let (demand, mut activation) = IngressDemand::new(&plan, scaling_policy)?;
        let demand = Arc::new(demand);
        let mut descriptors = BTreeMap::new();
        let key = Arc::new(BondSessionKey::new(*identity.bond_session_key));
        let (candidate_tx, candidate_rx) = mpsc::channel(ADMISSION_CHANNEL_CAPACITY);
        let (completed_tx, completed_rx) = mpsc::channel(COMPLETED_SESSION_CAPACITY);
        let (admission_tx, admission_rx) = mpsc::channel(ADMISSION_CHANNEL_CAPACITY);
        let mut tasks = Vec::with_capacity(pool.tor_slots().len() + pool.i2p_slots().len() + 1);
        let discoveries = discovery_lanes(&plan);
        if discoveries.is_empty() {
            bail!("bond plan has no discovery lane");
        }
        let discovery_ids = discoveries
            .iter()
            .map(|planned| planned.config.id)
            .collect::<BTreeSet<_>>();
        let (discovery_ready_tx, discovery_ready_rx) = mpsc::channel(discoveries.len());

        for router in pool.tor_slots() {
            let planned = plan
                .iter()
                .find(|lane| matches!(lane.provider, Provider::Tor { slot } if slot == router.slot))
                .copied()
                .context("bond plan omitted a Tor router slot")?;
            let derived = identity
                .tor_pool
                .get(router.slot as usize - 1)
                .context("server identity omitted a Tor pool slot")?;
            let slot = router.slot;
            let destination = derived.destination.clone();
            descriptors.insert(
                planned.config.id,
                EndpointDescriptor::new(
                    planned.config.id,
                    planned.config.failure_domain,
                    EndpointProvider::Tor,
                    TopologyAction::Add,
                    destination.clone(),
                )?,
            );
            let control_private_key = derived.control_private_key.clone();
            let active = activation
                .remove(&planned.config.id)
                .context("Tor ingress activation omitted a lane")?;
            let ready = discovery_ids
                .contains(&planned.config.id)
                .then(|| discovery_ready_tx.clone());
            tasks.push(tokio::spawn(supervise_tor_ingress(
                router.clone(),
                planned,
                destination,
                control_private_key,
                (slot == 1).then_some(direct_backend).flatten(),
                key.clone(),
                candidate_tx.clone(),
                ready,
                active,
            )));
        }
        for router in pool.i2p_slots() {
            let planned = plan
                .iter()
                .find(|lane| matches!(lane.provider, Provider::I2p { slot } if slot == router.slot))
                .copied()
                .context("bond plan omitted an I2P router slot")?;
            let derived = identity
                .i2p_pool
                .get(router.slot as usize - 1)
                .context("server identity omitted an I2P pool slot")?;
            let session_name = format!("anonssh-bond-slot-{}", router.slot);
            let private_key = derived.private_key.clone();
            descriptors.insert(
                planned.config.id,
                EndpointDescriptor::new(
                    planned.config.id,
                    planned.config.failure_domain,
                    EndpointProvider::I2p,
                    TopologyAction::Add,
                    derived.destination.clone(),
                )?,
            );
            let active = activation
                .remove(&planned.config.id)
                .context("I2P ingress activation omitted a lane")?;
            let ready = discovery_ids
                .contains(&planned.config.id)
                .then(|| discovery_ready_tx.clone());
            tasks.push(tokio::spawn(supervise_i2p_ingress(
                router.clone(),
                session_name,
                private_key,
                planned,
                key.clone(),
                candidate_tx.clone(),
                ready,
                active,
            )));
        }
        drop(discovery_ready_tx);
        drop(candidate_tx);
        let server_incarnation = ServerIncarnation::fresh()?;
        tasks.push(tokio::spawn(run_admission_coordinator(
            candidate_rx,
            admission_rx,
            completed_tx,
            key,
            plan.clone(),
            server_incarnation,
        )));
        let discovery_deadline = discoveries
            .iter()
            .map(|planned| discovery_publication_deadline(planned.provider))
            .max()
            .context("bond plan has no discovery publication deadline")?;
        await_discovery_publication(discovery_deadline, discovery_ready_rx, &tasks).await?;
        Ok(Self {
            completed_rx: Mutex::new(completed_rx),
            admission_tx,
            demand,
            descriptors,
            plan,
            scaling_policy,
            negotiated_capabilities: Mutex::new(BTreeMap::new()),
            capability_generations: Mutex::new(BTreeMap::new()),
            tasks,
        })
    }

    pub async fn accept_session(&self) -> Result<BondSession> {
        let session = self
            .completed_rx
            .lock()
            .await
            .recv()
            .await
            .context("bond admission coordinator stopped")?;
        if session.protocol_version() >= anonssh_bond_tokio::BondProtocolVersion::V4 {
            let advertisement = product_capabilities(
                1,
                session.protocol_version(),
                &self.plan,
                self.scaling_policy,
                &session.statistics().await?,
            )?;
            session.advertise_capabilities(advertisement).await?;
            self.capability_generations
                .lock()
                .await
                .insert(session.session_id(), 1);
        }
        Ok(session)
    }

    pub async fn release_session(&self, session_id: u64) -> Result<()> {
        self.negotiated_capabilities
            .lock()
            .await
            .remove(&session_id);
        self.capability_generations.lock().await.remove(&session_id);
        self.demand.release(session_id).await?;
        self.admission_tx
            .send(AdmissionCommand::Release { session_id })
            .await
            .context("bond admission coordinator stopped")
    }

    pub async fn apply_capability_request(
        &self,
        session: &BondSessionControl,
        advertisement: CapabilityAdvertisement,
    ) -> Result<CapabilityIntersection> {
        if session.protocol_version() < anonssh_bond_tokio::BondProtocolVersion::V4 {
            bail!("capability request arrived on a pre-v4 bond session");
        }
        let generation = self
            .capability_generations
            .lock()
            .await
            .get(&session.session_id())
            .copied()
            .unwrap_or(0)
            .checked_add(1)
            .context("server capability generation overflow")?;
        let local = product_capabilities(
            generation,
            session.protocol_version(),
            &self.plan,
            self.scaling_policy,
            &session.statistics().await?,
        )?;
        let intersection = local.intersect(&advertisement)?;
        constrained_plan(&self.plan, &intersection)?;
        session.advertise_capabilities(local).await?;
        self.capability_generations
            .lock()
            .await
            .insert(session.session_id(), generation);
        self.negotiated_capabilities
            .lock()
            .await
            .insert(session.session_id(), intersection.clone());
        Ok(intersection)
    }

    pub async fn apply_topology_request(
        &self,
        session: &BondSessionControl,
        advertisement: TopologyAdvertisement,
    ) -> Result<()> {
        let (allowed_lanes, maximum_active_lanes) =
            if session.protocol_version() >= anonssh_bond_tokio::BondProtocolVersion::V4 {
                let negotiated = self
                    .negotiated_capabilities
                    .lock()
                    .await
                    .get(&session.session_id())
                    .cloned()
                    .context("peer sent topology before capability negotiation")?;
                (
                    constrained_plan(&self.plan, &negotiated)?
                        .into_iter()
                        .map(|planned| planned.config.id)
                        .collect::<BTreeSet<_>>(),
                    usize::from(negotiated.max_active_lanes),
                )
            } else {
                (
                    self.descriptors.keys().copied().collect(),
                    self.scaling_policy.maximum_active_lanes,
                )
            };
        if advertisement.descriptors.len() != allowed_lanes.len() {
            bail!(
                "product topology snapshot declared {} of {} recoverable lanes",
                advertisement.descriptors.len(),
                allowed_lanes.len()
            );
        }
        let mut changes = Vec::with_capacity(advertisement.descriptors.len());
        for descriptor in advertisement.descriptors {
            if !allowed_lanes.contains(&descriptor.lane_id) {
                bail!(
                    "peer requested lane {} outside negotiated capabilities",
                    descriptor.lane_id.get()
                );
            }
            let expected = self.descriptors.get(&descriptor.lane_id).with_context(|| {
                format!("peer requested unknown lane {}", descriptor.lane_id.get())
            })?;
            if descriptor.failure_domain != expected.failure_domain
                || descriptor.provider != expected.provider
                || descriptor.endpoint != expected.endpoint
            {
                bail!("peer scaling descriptor does not match the recoverable topology");
            }
            let enabled = match descriptor.action {
                TopologyAction::Add => true,
                TopologyAction::Drain => false,
                TopologyAction::Replace => {
                    bail!("product scaling uses explicit add and drain descriptors")
                }
            };
            if !enabled && self.demand.baseline.contains(&descriptor.lane_id) {
                bail!("peer attempted to drain a baseline lane");
            }
            changes.push((descriptor.lane_id, enabled));
        }
        let requested_active = changes.iter().filter(|(_, enabled)| *enabled).count();
        if requested_active > maximum_active_lanes {
            bail!(
                "peer requested {requested_active} active lanes above negotiated ceiling {maximum_active_lanes}"
            );
        }
        for (lane_id, enabled) in changes.iter().copied().filter(|(_, enabled)| !*enabled) {
            self.demand
                .set(session.session_id(), lane_id, enabled)
                .await?;
            session.fail_lane(lane_id).await?;
        }
        for (lane_id, enabled) in changes.into_iter().filter(|(_, enabled)| *enabled) {
            self.demand
                .set(session.session_id(), lane_id, enabled)
                .await?;
        }
        Ok(())
    }
}

async fn await_discovery_publication(
    deadline: Duration,
    mut ready: mpsc::Receiver<()>,
    tasks: &[JoinHandle<()>],
) -> Result<()> {
    match tokio::time::timeout(deadline, ready.recv()).await {
        Ok(Some(())) => Ok(()),
        Ok(None) => {
            abort_tasks(tasks);
            bail!("bond discovery publication supervisor stopped before becoming ready")
        }
        Err(_) => {
            abort_tasks(tasks);
            bail!(
                "bond discovery publication exceeded its {}-second deadline",
                deadline.as_secs()
            )
        }
    }
}

fn abort_tasks(tasks: &[JoinHandle<()>]) {
    for task in tasks {
        task.abort();
    }
}

impl Drop for BondIngress {
    fn drop(&mut self) {
        abort_tasks(&self.tasks);
    }
}

#[allow(clippy::too_many_arguments)]
async fn supervise_tor_ingress(
    router: Arc<TorPoolSlot>,
    planned: PlannedLane,
    destination: String,
    control_private_key: Zeroizing<String>,
    direct_backend: Option<std::net::SocketAddr>,
    key: Arc<BondSessionKey>,
    candidate_tx: mpsc::Sender<PreparedIngressLane>,
    mut ready: Option<mpsc::Sender<()>>,
    mut desired: watch::Receiver<bool>,
) {
    let mut backoff = SLOT_REPAIR_BACKOFF_MIN;
    loop {
        while !*desired.borrow() {
            if desired.changed().await.is_err() {
                return;
            }
        }
        let established = match while_lane_desired(&mut desired, async {
            router.ensure_running().await?;
            let manager = router.manager().await?;
            let listener = TcpListener::bind("127.0.0.1:0").await?;
            let target = listener.local_addr()?;
            let mut routes = vec![(BOND_SERVICE_PORT, target)];
            if let Some(backend) = direct_backend {
                routes.push((22, backend));
            }
            let service = TorListener::new(manager.control_endpoint().await?)
                .listen_with_key_routes(&routes, &destination, &control_private_key)
                .await
                .with_context(|| format!("failed to publish Tor pool slot {}", router.slot))?;
            Ok::<_, anyhow::Error>((listener, service))
        })
        .await
        {
            DesiredOperation::Completed(result) => result,
            DesiredOperation::Drained => {
                if let Err(error) = router.stop_selected_if_running().await {
                    warn!(
                        slot = router.slot,
                        "failed to stop drained Tor router: {error:#}"
                    );
                }
                continue;
            }
            DesiredOperation::DemandClosed => return,
        };
        match established {
            Ok((listener, mut service)) => {
                if !*desired.borrow() {
                    drop(service);
                    drop(listener);
                    if let Err(error) = router.stop_selected_if_running().await {
                        warn!(
                            slot = router.slot,
                            "failed to stop Tor router drained during startup: {error:#}"
                        );
                    }
                    continue;
                }
                backoff = SLOT_REPAIR_BACKOFF_MIN;
                router.mark_ingress_ready();
                info!(slot = router.slot, "bond Tor ingress is ready");
                if let Some(sender) = ready.take() {
                    let _ = sender.try_send(());
                }
                let result = tokio::select! {
                    result = service.wait_closed() => result,
                    _ = run_tor_acceptor(listener, planned, key.clone(), candidate_tx.clone()) => {
                        Err(anyhow::anyhow!("Tor ingress acceptor stopped"))
                    },
                    changed = desired.wait_for(|enabled| !*enabled) => changed
                        .map(|_| ())
                        .map_err(|_| anyhow::anyhow!("Tor ingress demand stopped")),
                };
                if *desired.borrow() {
                    if let Err(error) = result {
                        warn!(slot = router.slot, "bond Tor ingress failed: {error:#}");
                    }
                }
            }
            Err(error) => {
                router.mark_lane_failure();
                warn!(
                    slot = router.slot,
                    "bond Tor ingress startup failed: {error:#}"
                );
            }
        }
        router.mark_backoff(backoff);
        if !*desired.borrow() {
            if let Err(error) = router.stop_selected_if_running().await {
                warn!(
                    slot = router.slot,
                    "failed to stop drained Tor router: {error:#}"
                );
            }
            continue;
        }
        tokio::time::sleep(backoff).await;
        backoff = next_repair_backoff(backoff);
    }
}

#[allow(clippy::too_many_arguments)]
async fn supervise_i2p_ingress(
    router: I2pPoolSlot,
    session_name: String,
    private_key: Zeroizing<String>,
    planned: PlannedLane,
    key: Arc<BondSessionKey>,
    candidate_tx: mpsc::Sender<PreparedIngressLane>,
    mut ready: Option<mpsc::Sender<()>>,
    mut desired: watch::Receiver<bool>,
) {
    let slot = router.slot;
    let sam_endpoint = router.sam_endpoint.to_string();
    let mut backoff = SLOT_REPAIR_BACKOFF_MIN;
    loop {
        while !*desired.borrow() {
            if desired.changed().await.is_err() {
                return;
            }
        }
        let established = match while_lane_desired(&mut desired, async {
            router.ensure_running().await?;
            SamListener::bind_zeroizing(
                sam_endpoint.clone(),
                session_name.clone(),
                private_key.clone(),
            )
            .await
            .with_context(|| format!("failed to publish I2P pool slot {slot}"))
        })
        .await
        {
            DesiredOperation::Completed(result) => result,
            DesiredOperation::Drained => {
                if let Err(error) = router.stop_if_running().await {
                    warn!(slot, "failed to stop drained I2P router: {error:#}");
                }
                continue;
            }
            DesiredOperation::DemandClosed => return,
        };
        match established {
            Ok(listener) => {
                if !*desired.borrow() {
                    drop(listener);
                    if let Err(error) = router.stop_if_running().await {
                        warn!(
                            slot,
                            "failed to stop I2P router drained during startup: {error:#}"
                        );
                    }
                    continue;
                }
                backoff = SLOT_REPAIR_BACKOFF_MIN;
                router.mark_ingress_ready();
                info!(slot, "bond I2P ingress is ready");
                if let Some(sender) = ready.take() {
                    let _ = sender.try_send(());
                }
                let result = tokio::select! {
                    result = run_i2p_acceptor(listener, planned, key.clone(), candidate_tx.clone()) => result,
                    changed = desired.wait_for(|enabled| !*enabled) => changed
                        .map(|_| ())
                        .map_err(|_| anyhow::anyhow!("I2P ingress demand stopped")),
                };
                if *desired.borrow() {
                    if let Err(error) = result {
                        warn!(slot, "bond I2P ingress failed: {error:#}");
                    }
                }
            }
            Err(error) => {
                router.mark_lane_failure();
                warn!(slot, "bond I2P ingress startup failed: {error:#}");
            }
        }
        router.mark_backoff(backoff);
        if !*desired.borrow() {
            if let Err(error) = router.stop_if_running().await {
                warn!(slot, "failed to stop drained I2P router: {error:#}");
            }
            continue;
        }
        tokio::time::sleep(backoff).await;
        backoff = next_repair_backoff(backoff);
    }
}

fn next_repair_backoff(current: Duration) -> Duration {
    current.saturating_mul(2).min(SLOT_REPAIR_BACKOFF_MAX)
}

enum DesiredOperation<T> {
    Completed(T),
    Drained,
    DemandClosed,
}

async fn while_lane_desired<T>(
    desired: &mut watch::Receiver<bool>,
    operation: impl std::future::Future<Output = T>,
) -> DesiredOperation<T> {
    tokio::select! {
        result = operation => DesiredOperation::Completed(result),
        changed = desired.wait_for(|enabled| !*enabled) => match changed {
            Ok(_) => DesiredOperation::Drained,
            Err(_) => DesiredOperation::DemandClosed,
        },
    }
}

async fn run_tor_acceptor(
    listener: TcpListener,
    planned: PlannedLane,
    key: Arc<BondSessionKey>,
    candidate_tx: mpsc::Sender<PreparedIngressLane>,
) {
    let mut handshakes = JoinSet::new();
    loop {
        tokio::select! {
            accepted = listener.accept(), if handshakes.len() < MAX_INFLIGHT_HANDSHAKES => {
                match accepted {
                    Ok((stream, _)) => spawn_preparation(
                        &mut handshakes,
                        stream,
                        planned,
                        key.clone(),
                        candidate_tx.clone(),
                    ),
                    Err(error) => {
                        warn!("bond Tor ingress accept failed: {error}");
                        tokio::time::sleep(POOL_REPAIR_RETRY_DELAY).await;
                    }
                }
            }
            joined = handshakes.join_next(), if !handshakes.is_empty() => {
                report_handshake_task(joined);
            }
        }
    }
}

async fn run_i2p_acceptor(
    listener: SamListener,
    planned: PlannedLane,
    key: Arc<BondSessionKey>,
    candidate_tx: mpsc::Sender<PreparedIngressLane>,
) -> Result<()> {
    let mut handshakes = JoinSet::new();
    loop {
        tokio::select! {
            accepted = listener.accept(), if handshakes.len() < MAX_INFLIGHT_HANDSHAKES => {
                match accepted {
                    Ok(stream) => spawn_preparation(
                        &mut handshakes,
                        stream,
                        planned,
                        key.clone(),
                        candidate_tx.clone(),
                    ),
                    Err(error) => return Err(error).context("bond I2P ingress accept failed"),
                }
            }
            joined = handshakes.join_next(), if !handshakes.is_empty() => {
                report_handshake_task(joined);
            }
        }
    }
}

fn spawn_preparation(
    handshakes: &mut JoinSet<()>,
    stream: TcpStream,
    planned: PlannedLane,
    key: Arc<BondSessionKey>,
    candidate_tx: mpsc::Sender<PreparedIngressLane>,
) {
    handshakes.spawn(async move {
        let result = async {
            data_stream::configure(&stream)
                .context("failed to configure anonymous ingress data stream")?;
            let prepared = prepare_server_lane(stream, &key, HANDSHAKE_TIMEOUT).await?;
            let join = prepared.join();
            if planned.config.id != join.lane_id
                || planned.config.failure_domain != join.failure_domain
            {
                bail!("authenticated lane arrived through the wrong provider");
            }
            candidate_tx
                .send(PreparedIngressLane::new(planned, prepared))
                .await
                .context("bond admission coordinator stopped")
        }
        .await;
        if let Err(error) = result {
            warn!("bond ingress handshake rejected: {error:#}");
        }
    });
}

fn report_handshake_task(joined: Option<std::result::Result<(), tokio::task::JoinError>>) {
    if let Some(Err(error)) = joined {
        warn!("bond ingress handshake task failed: {error}");
    }
}

#[cfg(test)]
async fn wait_for_active_lanes(
    session: &BondSession,
    lane_ids: &[LaneId],
    deadline: Duration,
    label: &str,
) -> Result<()> {
    tokio::time::timeout(deadline, async {
        loop {
            let stats = session.statistics().await?;
            if lane_ids.iter().all(|lane_id| {
                stats
                    .lanes
                    .iter()
                    .any(|lane| lane.id == *lane_id && lane.active)
            }) {
                return Ok::<(), anyhow::Error>(());
            }
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
    })
    .await
    .with_context(|| format!("{label} lanes did not become active before their deadline"))?
}

pub struct ClientBondSession {
    session: BondSession,
    key: Arc<BondSessionKey>,
    server_incarnation: Option<ServerIncarnation>,
    tor_destinations: Vec<String>,
    i2p_destinations: Vec<String>,
    // SAM data streams live only while their owning control session remains open.
    i2p_connectors: Vec<SamConnector>,
    scaling: Arc<StdMutex<AdaptiveScalingTelemetry>>,
    scaling_policy: ScalingPolicy,
    resource_governor: Arc<SharedResourceGovernor>,
    _resource_claim: resource_governor::SessionResourceClaim,
}

impl ClientBondSession {
    pub async fn connect(
        pool: &RouterPool,
        tor_socks: &[String],
        tor_destinations: &[String],
        i2p_destinations: &[String],
        key_bytes: [u8; 32],
    ) -> Result<Self> {
        Self::connect_with_scaling_policy(
            pool,
            tor_socks,
            tor_destinations,
            i2p_destinations,
            key_bytes,
            ScalingPolicy::performance(),
        )
        .await
    }

    pub(crate) async fn connect_with_scaling_policy(
        pool: &RouterPool,
        tor_socks: &[String],
        tor_destinations: &[String],
        i2p_destinations: &[String],
        key_bytes: [u8; 32],
        scaling_policy: ScalingPolicy,
    ) -> Result<Self> {
        Self::connect_with_resource_governor(
            pool,
            tor_socks,
            tor_destinations,
            i2p_destinations,
            key_bytes,
            scaling_policy,
            Arc::new(SharedResourceGovernor::new(scaling_policy)),
        )
        .await
    }

    pub(crate) async fn connect_with_resource_governor(
        pool: &RouterPool,
        tor_socks: &[String],
        tor_destinations: &[String],
        i2p_destinations: &[String],
        key_bytes: [u8; 32],
        scaling_policy: ScalingPolicy,
        resource_governor: Arc<SharedResourceGovernor>,
    ) -> Result<Self> {
        validate_pool_identities(pool, tor_destinations.len(), i2p_destinations.len())?;
        let plan = production_plan(pool)?;
        let i2p_connectors = pool
            .i2p_slots()
            .iter()
            .map(|router| SamConnector::new(router.sam_endpoint.to_string(), None))
            .collect::<Vec<_>>();
        let session_id = fresh_session_id()?;
        let resource_claim = resource_governor.claim(
            session_id,
            baseline_providers(&plan),
            plan.iter().map(|planned| planned.provider).collect(),
        )?;
        let key = Arc::new(BondSessionKey::new(key_bytes));
        let (discovery, discovery_lane) = connect_discovery_lane(
            DiscoveryRoutes {
                pool,
                plan: &plan,
                tor_socks,
                tor_destinations,
                i2p_destinations,
                i2p_connectors: &i2p_connectors,
            },
            key.clone(),
            session_id,
        )
        .await?;
        let server_incarnation = discovery_lane.server_incarnation()?;
        let session = BondSession::spawn(
            runtime_config(session_id),
            vec![RuntimeLane::from_authenticated(
                discovery.config,
                discovery_lane,
            )],
            SessionRole::Dialer,
        )?;
        match discovery.provider {
            Provider::Tor { slot } => pool.tor_slot(slot)?.mark_active(),
            Provider::I2p { slot } => pool.i2p_slot(slot)?.mark_active(),
        }
        for planned in plan
            .iter()
            .filter(|lane| lane.config.id != discovery.config.id)
        {
            session.authorize_lane(planned.config).await?;
        }
        if session.protocol_version() >= anonssh_bond_tokio::BondProtocolVersion::V4 {
            let advertisement = product_capabilities(
                1,
                session.protocol_version(),
                &plan,
                scaling_policy,
                &session.statistics().await?,
            )?;
            session.advertise_capabilities(advertisement).await?;
        }
        let mut scaling = AdaptiveScalingTelemetry::default();
        scaling.initialize(baseline_lanes(&plan));
        Ok(Self {
            session,
            key,
            server_incarnation,
            tor_destinations: tor_destinations.to_vec(),
            i2p_destinations: i2p_destinations.to_vec(),
            i2p_connectors,
            scaling: Arc::new(StdMutex::new(scaling)),
            scaling_policy,
            resource_governor,
            _resource_claim: resource_claim,
        })
    }

    pub async fn open_service_stream(
        &self,
        service: &crate::application_service::ServiceName,
        class: TrafficClass,
    ) -> Result<anonssh_bond_tokio::BondedStream> {
        if self.session.protocol_version() < anonssh_bond_tokio::BondProtocolVersion::V6 {
            if service.as_str() == crate::application_service::SSH_SERVICE
                && class == TrafficClass::Interactive
            {
                return Ok(self.session.open_stream(class).await?);
            }
            return Err(crate::application_service::ServiceSetupError::PeerIncompatible.into());
        }
        let mut stream = self.session.open_stream(class).await?;
        match tokio::time::timeout(
            crate::application_service::SETUP_TIMEOUT,
            crate::application_service::request_service(&mut stream, service),
        )
        .await
        {
            Ok(Ok(())) => Ok(stream),
            Ok(Err(error)) => {
                let _ = stream.reset(3).await;
                Err(error).context("peer service negotiation failed")
            }
            Err(_) => {
                let _ = stream.reset(3).await;
                Err(crate::application_service::ServiceSetupError::Timeout.into())
            }
        }
    }

    pub async fn open_ssh_stream(&self) -> Result<anonssh_bond_tokio::BondedStream> {
        self.open_service_stream(
            &crate::application_service::ServiceName::parse(
                crate::application_service::SSH_SERVICE,
            )?,
            TrafficClass::Interactive,
        )
        .await
    }

    pub const fn session(&self) -> &BondSession {
        &self.session
    }

    pub(crate) fn scaling_progress(&self) -> Result<AdaptiveScalingProgress> {
        self.scaling
            .lock()
            .map_err(|_| anyhow::anyhow!("adaptive scaling telemetry lock was poisoned"))
            .map(|telemetry| telemetry.snapshot())
    }

    pub async fn repair_i2p_lane(&self, pool: &RouterPool, slot: u32) -> Result<()> {
        let planned = production_plan(pool)?
            .into_iter()
            .find(|lane| matches!(lane.provider, Provider::I2p { slot: candidate } if candidate == slot))
            .with_context(|| format!("bond plan omitted I2P slot {slot}"))?;
        let destination = self
            .i2p_destinations
            .get(slot as usize - 1)
            .context("client identity omitted an I2P pool slot")?;
        let connector = self
            .i2p_connectors
            .get(slot as usize - 1)
            .context("client session omitted an I2P connector slot")?;
        self.session.fail_lane(planned.config.id).await?;
        let join = LaneJoin::new(
            self.session.session_id(),
            planned.config.id,
            planned.config.failure_domain,
        )?;
        let lane = connect_i2p_lane(connector, destination, slot, &self.key, join)
            .await
            .with_context(|| format!("failed to establish replacement I2P lane {slot}"))?;
        validate_server_incarnation(&lane, self.server_incarnation)?;
        self.session
            .add_lane(RuntimeLane::from_authenticated(planned.config, lane))
            .await?;
        Ok(())
    }

    pub async fn maintain_lanes(&self, pool: &RouterPool) -> Result<()> {
        self.maintain_lanes_with_mode(pool, LaneSupervisionMode::Adaptive)
            .await
    }

    pub(crate) async fn maintain_all_lanes(&self, pool: &RouterPool) -> Result<()> {
        self.maintain_lanes_with_mode(pool, LaneSupervisionMode::FixedAll)
            .await
    }

    async fn maintain_lanes_with_mode(
        &self,
        pool: &RouterPool,
        mode: LaneSupervisionMode,
    ) -> Result<()> {
        validate_pool_identities(
            pool,
            self.tor_destinations.len(),
            self.i2p_destinations.len(),
        )?;
        let full_plan = production_plan(pool)?;
        let (plan, scaling_policy, peer_capabilities) =
            if self.session.protocol_version() >= anonssh_bond_tokio::BondProtocolVersion::V4 {
                let peer = tokio::time::timeout(
                    CAPABILITY_EXCHANGE_TIMEOUT,
                    self.session.accept_capabilities(),
                )
                .await
                .context("peer capability advertisement timed out")??;
                let local = product_capabilities(
                    1,
                    self.session.protocol_version(),
                    &full_plan,
                    self.scaling_policy,
                    &self.session.statistics().await?,
                )?;
                let intersection = local.intersect(&peer)?;
                (
                    constrained_plan(&full_plan, &intersection)?,
                    negotiated_scaling_policy(self.scaling_policy, &intersection),
                    Some(peer),
                )
            } else {
                (full_plan, self.scaling_policy, None)
            };
        let (demand, mut activation) = LaneDemand::new(
            &plan,
            self.resource_governor.clone(),
            self.session.session_id(),
        )?;
        let demand = Arc::new(demand);
        let mut supervisors = JoinSet::new();
        for planned in &plan {
            let planned = *planned;
            let control = self.session.control();
            let key = self.key.clone();
            let active = activation
                .remove(&planned.config.id)
                .context("adaptive activation omitted a planned lane")?;
            match planned.provider {
                Provider::Tor { slot } => {
                    let router = pool
                        .tor_slots()
                        .iter()
                        .find(|router| router.slot == slot)
                        .cloned()
                        .with_context(|| format!("router pool omitted Tor slot {slot}"))?;
                    let destination = self
                        .tor_destinations
                        .get(slot as usize - 1)
                        .context("client identity omitted a Tor pool slot")?
                        .clone();
                    supervisors.spawn(supervise_client_tor_lane(
                        control,
                        router,
                        planned,
                        destination,
                        ClientLaneContext {
                            key,
                            demand: demand.clone(),
                            server_incarnation: self.server_incarnation,
                        },
                        active,
                    ));
                }
                Provider::I2p { slot } => {
                    let router = pool.i2p_slot(slot)?;
                    let destination = self
                        .i2p_destinations
                        .get(slot as usize - 1)
                        .context("client identity omitted an I2P pool slot")?
                        .clone();
                    let connector = self
                        .i2p_connectors
                        .get(slot as usize - 1)
                        .context("client session omitted an I2P connector slot")?
                        .clone();
                    supervisors.spawn(supervise_client_i2p_lane(
                        control,
                        router.clone(),
                        planned,
                        destination,
                        connector,
                        ClientLaneContext {
                            key,
                            demand: demand.clone(),
                            server_incarnation: self.server_incarnation,
                        },
                        active,
                    ));
                }
            }
        }
        if matches!(mode, LaneSupervisionMode::FixedAll) {
            activate_fixed_topology(
                &self.session.control(),
                &plan,
                &demand,
                &self.tor_destinations,
                &self.i2p_destinations,
            )
            .await?;
            self.scaling
                .lock()
                .map_err(|_| anyhow::anyhow!("adaptive scaling telemetry lock was poisoned"))?
                .initialize(plan.iter().map(|lane| lane.config.id).collect());
            return tokio::select! {
                result = enforce_session_outage_deadline(self.session.control()) => result,
                joined = supervisors.join_next() => match joined {
                    Some(Ok(result)) => result.context("fixed bond lane supervisor stopped"),
                    Some(Err(error)) => Err(anyhow::anyhow!(
                        "fixed bond lane supervisor failed: {error}"
                    )),
                    None => bail!("fixed bond lane supervision has no slots"),
                }
            };
        }
        let controller = run_adaptive_controller(
            self.session.control(),
            AdaptiveControllerContext {
                pool,
                plan,
                demand,
                tor_destinations: self.tor_destinations.clone(),
                i2p_destinations: self.i2p_destinations.clone(),
                telemetry: self.scaling.clone(),
                session: &self.session,
                policy: scaling_policy,
                peer_capabilities,
            },
        );
        tokio::select! {
            result = controller => result.context("adaptive bond controller stopped"),
            result = enforce_session_outage_deadline(self.session.control()) => result,
            joined = supervisors.join_next() => match joined {
                Some(Ok(result)) => result.context("bond lane supervisor stopped"),
                Some(Err(error)) => Err(anyhow::anyhow!("bond lane supervisor failed: {error}")),
                None => bail!("bond lane supervision has no slots"),
            }
        }
    }

    pub async fn shutdown(self) -> Result<()> {
        Ok(self.session.shutdown().await?)
    }
}

async fn enforce_session_outage_deadline(control: BondSessionControl) -> Result<()> {
    let mut guard = SessionOutageGuard::default();
    loop {
        tokio::time::sleep(POOL_HEALTH_INTERVAL).await;
        let active_lanes = control
            .statistics()
            .await?
            .lanes
            .iter()
            .filter(|lane| lane.active)
            .count();
        if guard.observe(Instant::now(), active_lanes) {
            let cause = format!(
                "bond session had no active lanes for {} seconds",
                SESSION_OUTAGE_DEADLINE.as_secs()
            );
            let _ = control.terminate(cause.clone()).await;
            bail!(cause);
        }
    }
}

async fn supervise_client_tor_lane(
    control: BondSessionControl,
    router: Arc<TorPoolSlot>,
    planned: PlannedLane,
    destination: String,
    context: ClientLaneContext,
    mut desired: watch::Receiver<bool>,
) -> Result<()> {
    let Provider::Tor { slot } = planned.provider else {
        bail!("Tor supervisor received a non-Tor lane");
    };
    let mut backoff = SLOT_REPAIR_BACKOFF_MIN;
    let mut isolation_epoch = 1_u64;
    loop {
        if !*desired.borrow() {
            if lane_is_active(&control, planned.config.id).await? {
                control.fail_lane(planned.config.id).await?;
            }
            if !context.demand.governor.is_demanded(planned.provider)? {
                router.stop_selected_if_running().await?;
            }
            desired
                .changed()
                .await
                .map_err(|_| anyhow::anyhow!("adaptive Tor lane demand stopped"))?;
            continue;
        }
        if lane_is_active(&control, planned.config.id).await? {
            backoff = SLOT_REPAIR_BACKOFF_MIN;
            tokio::select! {
                _ = tokio::time::sleep(POOL_HEALTH_INTERVAL) => {}
                changed = desired.changed() => {
                    changed.map_err(|_| anyhow::anyhow!("adaptive Tor lane demand stopped"))?;
                }
            }
            continue;
        }
        let current_isolation_epoch = isolation_epoch;
        isolation_epoch = isolation_epoch
            .checked_add(1)
            .context("Tor lane isolation epoch overflow")?;
        let result = match while_lane_desired(&mut desired, async {
            let socks = router.ensure_running().await?;
            let connector = TorConnector::new(socks);
            let join = LaneJoin::new(
                control.session_id(),
                planned.config.id,
                planned.config.failure_domain,
            )?;
            tokio::time::timeout(TOR_LANE_ESTABLISHMENT_DEADLINE, async {
                let mut failures = Vec::new();
                let lane = loop {
                    let attempt = failures.len() + 1;
                    let stream = connect_tor_lane(
                        &connector,
                        &destination,
                        planned.config.id,
                        current_isolation_epoch,
                        attempt,
                    )
                    .await?;
                    match authenticate_client_lane(stream, &context.key, join, HANDSHAKE_TIMEOUT)
                        .await
                    {
                        Ok(lane) => break lane,
                        Err(error) if attempt < TOR_AUTH_ATTEMPTS => {
                            failures.push(format!("attempt {attempt}: {error}"));
                        }
                        Err(error) => {
                            failures.push(format!("attempt {attempt}: {error}"));
                            bail!(
                                "failed to authenticate Tor lane {} after {TOR_AUTH_ATTEMPTS} attempts: {}",
                                planned.config.id.get(),
                                failures.join("; ")
                            );
                        }
                    }
                };
                validate_server_incarnation(&lane, context.server_incarnation)?;
                control
                    .add_lane(RuntimeLane::from_authenticated(planned.config, lane))
                    .await?;
                Ok::<(), anyhow::Error>(())
            })
            .await
            .with_context(|| {
                format!(
                    "Tor lane {} establishment exceeded its {}-second repair deadline",
                    planned.config.id.get(),
                    TOR_LANE_ESTABLISHMENT_DEADLINE.as_secs()
                )
            })??;
            Ok::<(), anyhow::Error>(())
        })
        .await
        {
            DesiredOperation::Completed(result) => result,
            DesiredOperation::Drained => {
                if !context.demand.governor.is_demanded(planned.provider)? {
                    router.stop_selected_if_running().await?;
                }
                continue;
            }
            DesiredOperation::DemandClosed => bail!("adaptive Tor lane demand stopped"),
        };
        match result {
            Ok(()) => {
                if *desired.borrow() {
                    router.mark_active();
                    info!(slot, "client Tor bond lane is active");
                }
                backoff = SLOT_REPAIR_BACKOFF_MIN;
            }
            Err(error) => {
                if error.downcast_ref::<ServerIncarnationChanged>().is_some() {
                    let _ = control.terminate(error.to_string()).await;
                    return Err(error);
                }
                router.mark_lane_failure();
                router.mark_backoff(backoff);
                warn!(slot, "client Tor bond lane repair failed: {error:#}");
                tokio::time::sleep(backoff).await;
                backoff = next_repair_backoff(backoff);
            }
        }
    }
}

async fn supervise_client_i2p_lane(
    control: BondSessionControl,
    router: I2pPoolSlot,
    planned: PlannedLane,
    destination: String,
    connector: SamConnector,
    context: ClientLaneContext,
    mut desired: watch::Receiver<bool>,
) -> Result<()> {
    let Provider::I2p { slot } = planned.provider else {
        bail!("I2P supervisor received a non-I2P lane");
    };
    let mut backoff = SLOT_REPAIR_BACKOFF_MIN;
    loop {
        if !*desired.borrow() {
            if lane_is_active(&control, planned.config.id).await? {
                control.fail_lane(planned.config.id).await?;
            }
            if !context.demand.governor.is_demanded(planned.provider)? {
                router.stop_if_running().await?;
            }
            desired
                .changed()
                .await
                .map_err(|_| anyhow::anyhow!("adaptive I2P lane demand stopped"))?;
            continue;
        }
        if lane_is_active(&control, planned.config.id).await? {
            backoff = SLOT_REPAIR_BACKOFF_MIN;
            tokio::select! {
                _ = tokio::time::sleep(POOL_HEALTH_INTERVAL) => {}
                changed = desired.changed() => {
                    changed.map_err(|_| anyhow::anyhow!("adaptive I2P lane demand stopped"))?;
                }
            }
            continue;
        }
        let result = match while_lane_desired(&mut desired, async {
            router.ensure_running().await?;
            let join = LaneJoin::new(
                control.session_id(),
                planned.config.id,
                planned.config.failure_domain,
            )?;
            let lane = connect_i2p_lane(&connector, &destination, slot, &context.key, join).await?;
            validate_server_incarnation(&lane, context.server_incarnation)?;
            control
                .add_lane(RuntimeLane::from_authenticated(planned.config, lane))
                .await?;
            Ok::<(), anyhow::Error>(())
        })
        .await
        {
            DesiredOperation::Completed(result) => result,
            DesiredOperation::Drained => {
                if !context.demand.governor.is_demanded(planned.provider)? {
                    router.stop_if_running().await?;
                }
                continue;
            }
            DesiredOperation::DemandClosed => bail!("adaptive I2P lane demand stopped"),
        };
        match result {
            Ok(()) => {
                if *desired.borrow() {
                    router.mark_active();
                    info!(slot, "client I2P bond lane is active");
                }
                backoff = SLOT_REPAIR_BACKOFF_MIN;
            }
            Err(error) => {
                if error.downcast_ref::<ServerIncarnationChanged>().is_some() {
                    let _ = control.terminate(error.to_string()).await;
                    return Err(error);
                }
                router.mark_lane_failure();
                router.mark_backoff(backoff);
                warn!(slot, "client I2P bond lane repair failed: {error:#}");
                tokio::time::sleep(backoff).await;
                backoff = next_repair_backoff(backoff);
            }
        }
    }
}

async fn activate_fixed_topology(
    control: &BondSessionControl,
    plan: &[PlannedLane],
    demand: &LaneDemand,
    tor_destinations: &[String],
    i2p_destinations: &[String],
) -> Result<()> {
    let descriptors = plan
        .iter()
        .map(|planned| {
            scaling_descriptor(
                plan,
                tor_destinations,
                i2p_destinations,
                planned.config.id,
                TopologyAction::Add,
            )
        })
        .collect::<Result<Vec<_>>>()?;
    control
        .advertise_topology(TopologyAdvertisement::new(1, descriptors)?)
        .await?;
    demand.set_all()
}

async fn run_adaptive_controller(
    control: BondSessionControl,
    context: AdaptiveControllerContext<'_>,
) -> Result<()> {
    let AdaptiveControllerContext {
        session,
        pool,
        plan,
        demand,
        tor_destinations,
        i2p_destinations,
        telemetry,
        policy,
        mut peer_capabilities,
    } = context;
    let mut learner = LearnedScalingController::default();
    let mut previous_acknowledged = BTreeMap::new();
    let mut previous_observation = None;
    let mut previous_cpu = BTreeMap::new();
    let mut unavailable_since = BTreeMap::new();
    let mut active_since = BTreeMap::new();
    let mut previous_backpressure_events = 0_u64;
    let mut consecutive_send_pressure = 0_u8;
    let mut pending_marginal_drain = None;
    let mut pending_pressure_admissions = PendingPressureAdmissions::default();
    let mut topology_generation = 0_u64;
    let controller_started = tokio::time::Instant::now();
    let mut next_interval = policy.control_interval();
    let mut current_policy = policy;
    let mut capability_generation = 1_u64;
    loop {
        if peer_capabilities.is_some() {
            tokio::select! {
                advertisement = session.accept_capabilities() => {
                    peer_capabilities = Some(advertisement?);
                    continue;
                }
                () = tokio::time::sleep(next_interval) => {}
            }
        } else {
            tokio::time::sleep(next_interval).await;
        }
        let stats = control.statistics().await?;
        if let Some(peer) = &peer_capabilities {
            capability_generation = capability_generation
                .checked_add(1)
                .context("client capability generation overflow")?;
            let local = product_capabilities(
                capability_generation,
                session.protocol_version(),
                &plan,
                policy,
                &stats,
            )?;
            let intersection = local.intersect(peer)?;
            if constrained_plan(&plan, &intersection)?.len() != plan.len() {
                bail!("peer capability update removed an active candidate set");
            }
            current_policy = negotiated_scaling_policy(policy, &intersection);
            control.advertise_capabilities(local).await?;
        }
        let process_samples = pool.process_samples().await?;
        let process_samples = process_samples
            .into_iter()
            .map(|sample| {
                let provider = match sample.provider {
                    crate::router_pool::RouterProvider::Tor => Provider::Tor { slot: sample.slot },
                    crate::router_pool::RouterProvider::I2p => Provider::I2p { slot: sample.slot },
                };
                (provider, sample)
            })
            .collect::<BTreeMap<_, _>>();
        let observed = tokio::time::Instant::now();
        let elapsed_micros = previous_observation
            .and_then(|previous: anonssh_bond::Timestamp| {
                stats.observed_at.duration_since(previous)
            })
            .map(|elapsed| u64::try_from(elapsed.as_micros()).unwrap_or(u64::MAX))
            .filter(|elapsed| *elapsed > 0);
        let mut resources = ResourceUsage::default();
        let mut samples = Vec::with_capacity(plan.len());
        let mut path_observations = Vec::with_capacity(plan.len());
        for planned in &plan {
            let snapshot = stats
                .lanes
                .iter()
                .find(|lane| lane.id == planned.config.id)
                .with_context(|| {
                    format!(
                        "adaptive controller runtime omitted lane {}",
                        planned.config.id.get()
                    )
                })?;
            let process = process_samples
                .get(&planned.provider)
                .context("adaptive controller omitted a router process slot")?;
            let (estimated_cpu, estimated_memory, estimated_startup) =
                estimated_router_cost(planned.provider);
            let (cpu_millicores, memory_bytes) = match process.usage {
                Some(usage) => {
                    let cpu = previous_cpu
                        .get(&planned.provider)
                        .and_then(
                            |(previous_cpu_time, previous_at): &(
                                Duration,
                                tokio::time::Instant,
                            )| {
                                let cpu_delta = usage.cpu_time.checked_sub(*previous_cpu_time)?;
                                let wall = observed.duration_since(*previous_at);
                                let wall_micros = wall.as_micros();
                                (wall_micros > 0).then(|| {
                                    u32::try_from(
                                        cpu_delta.as_micros().saturating_mul(1_000) / wall_micros,
                                    )
                                    .unwrap_or(u32::MAX)
                                })
                            },
                        )
                        .unwrap_or(estimated_cpu);
                    previous_cpu.insert(planned.provider, (usage.cpu_time, observed));
                    (cpu.max(1), usage.resident_bytes.max(1))
                }
                None => (estimated_cpu, estimated_memory),
            };
            let desired = demand.is_desired(planned.config.id)?;
            let healthy = observe_lane_health(
                planned.config.id,
                desired,
                snapshot.active,
                observed,
                &mut unavailable_since,
            );
            let drain_eligible = observe_lane_drain_eligibility(
                planned.config.id,
                desired,
                snapshot.active,
                observed,
                &mut active_since,
            );
            if process.usage.is_some() || desired {
                resources.cpu_millicores = resources.cpu_millicores.saturating_add(cpu_millicores);
                resources.memory_bytes = resources.memory_bytes.saturating_add(memory_bytes);
            }
            let previous_bytes = previous_acknowledged
                .insert(planned.config.id, snapshot.bytes_acknowledged)
                .unwrap_or(snapshot.bytes_acknowledged);
            let marginal_goodput_bps = elapsed_micros
                .map(|elapsed| {
                    u64::try_from(
                        u128::from(snapshot.bytes_acknowledged.saturating_sub(previous_bytes))
                            .saturating_mul(8)
                            .saturating_mul(1_000_000)
                            / u128::from(elapsed),
                    )
                    .unwrap_or(u64::MAX)
                })
                .unwrap_or(snapshot.delivery_rate_bps);
            let queue_delay = snapshot
                .queued_through
                .duration_since(stats.observed_at)
                .unwrap_or_default();
            let startup_latency = process.startup_latency.unwrap_or(estimated_startup);
            path_observations.push(PhysicalPathObservation {
                provider: planned.provider,
                measured_resources: process.usage.map(|_| (cpu_millicores, memory_bytes)),
                delivered_goodput_bps: marginal_goodput_bps,
                expected_goodput_bps: snapshot.delivery_rate_bps,
                queue_delay,
                startup_latency,
            });
            samples.push(LaneScalingSample {
                id: planned.config.id,
                failure_domain: planned.config.failure_domain,
                provider: provider_id(planned.provider),
                admitted: desired,
                healthy,
                required: demand.baseline.contains(&planned.config.id),
                protected_for_low_latency: snapshot.reserved_for_low_latency,
                drain_eligible,
                queue_delay,
                marginal_goodput_bps,
                expected_goodput_bps: snapshot.delivery_rate_bps,
                startup_latency,
                cpu_millicores,
                memory_bytes,
            });
        }
        demand.report_observations(&path_observations)?;
        previous_observation = Some(stats.observed_at);
        let application_backpressure = stats.backpressured_streams > 0
            || stats.stream_backpressure_events > previous_backpressure_events;
        previous_backpressure_events = stats.stream_backpressure_events;
        let send_window_utilization = send_window_utilization_percent(stats.unacknowledged_bytes);
        let send_pressure = sustained_send_pressure_percent(
            send_window_utilization,
            &mut consecutive_send_pressure,
        );
        let pressure = ScalingPressure::new(send_pressure)?
            .with_application_backpressure(application_backpressure);
        let active_lanes = stats
            .lanes
            .iter()
            .filter(|lane| lane.active)
            .map(|lane| lane.id)
            .collect::<BTreeSet<_>>();
        learner.observe(&samples, &active_lanes)?;
        learner.apply_priors(&mut samples);
        let pressure_hint = send_pressure > 0
            || application_backpressure
            || samples
                .iter()
                .filter(|sample| sample.admitted)
                .any(|sample| sample.queue_delay >= Duration::from_millis(10));
        let controller = AdaptiveScalingController::new(learner.scaling_config(
            plan.len(),
            current_policy,
            pressure_hint,
        ))?;
        let pressure_active = controller.has_capacity_pressure(&samples, pressure)?;
        next_interval =
            Duration::from_millis(learner.snapshot().next_control_interval_millis.max(1));
        telemetry
            .lock()
            .map_err(|_| anyhow::anyhow!("adaptive scaling telemetry lock was poisoned"))?
            .observe_learning(learner.snapshot());
        let mut actions =
            pending_pressure_admissions.cancellation_actions(&active_lanes, pressure_active);
        telemetry
            .lock()
            .map_err(|_| anyhow::anyhow!("adaptive scaling telemetry lock was poisoned"))?
            .observe_pending_pressure(&pending_pressure_admissions.lanes);
        if actions.is_empty() {
            actions = controller.evaluate_admission_batch(
                &samples,
                resources,
                pressure,
                current_policy.maximum_admissions_per_interval,
            )?;
            if actions.len() == 1 {
                let stable_action =
                    apply_scale_down_hysteresis(actions[0], &mut pending_marginal_drain);
                if stable_action == ScalingAction::Hold {
                    actions.clear();
                } else if matches!(
                    stable_action,
                    ScalingAction::Drain {
                        reason: ScalingReason::MarginalGoodput,
                        ..
                    }
                ) {
                    actions = controller.evaluate_marginal_drain_batch(
                        &samples,
                        resources,
                        pressure,
                        current_policy.maximum_drains_per_interval,
                    )?;
                } else {
                    actions[0] = stable_action;
                }
            } else {
                pending_marginal_drain = None;
            }
            if actions.is_empty() && !pressure_active {
                if let Some(exploration) = learner.exploration_action(
                    &samples,
                    controller_started.elapsed(),
                    current_policy,
                ) {
                    actions.push(exploration);
                    telemetry
                        .lock()
                        .map_err(|_| {
                            anyhow::anyhow!("adaptive scaling telemetry lock was poisoned")
                        })?
                        .observe_learning(learner.snapshot());
                }
            }
        } else {
            pending_marginal_drain = None;
        }
        if actions.is_empty() {
            continue;
        }
        topology_generation = topology_generation
            .checked_add(1)
            .context("adaptive topology generation overflow")?;
        let applied_actions = apply_scaling_actions(
            &control,
            &plan,
            &demand,
            &tor_destinations,
            &i2p_destinations,
            topology_generation,
            &actions,
        )
        .await?;
        if applied_actions.is_empty() {
            continue;
        }
        pending_pressure_admissions.record(&applied_actions);
        telemetry
            .lock()
            .map_err(|_| anyhow::anyhow!("adaptive scaling telemetry lock was poisoned"))?
            .record(
                topology_generation,
                &applied_actions,
                &pending_pressure_admissions.lanes,
            );
        info!(actions = ?applied_actions, "adaptive bond topology changed");
    }
}

fn observe_lane_health(
    lane_id: LaneId,
    admitted: bool,
    active: bool,
    observed: tokio::time::Instant,
    unavailable_since: &mut BTreeMap<LaneId, tokio::time::Instant>,
) -> bool {
    if !admitted || active {
        unavailable_since.remove(&lane_id);
        return true;
    }
    let unavailable = unavailable_since.entry(lane_id).or_insert(observed);
    observed.duration_since(*unavailable) < SCALING_UNHEALTHY_AFTER
}

fn observe_lane_drain_eligibility(
    lane_id: LaneId,
    admitted: bool,
    active: bool,
    observed: tokio::time::Instant,
    active_since: &mut BTreeMap<LaneId, tokio::time::Instant>,
) -> bool {
    if !admitted || !active {
        active_since.remove(&lane_id);
        return false;
    }
    let since = active_since.entry(lane_id).or_insert(observed);
    observed.duration_since(*since) >= SCALING_DRAIN_DWELL
}

#[allow(clippy::too_many_arguments)]
async fn apply_scaling_actions(
    control: &BondSessionControl,
    plan: &[PlannedLane],
    demand: &LaneDemand,
    tor_destinations: &[String],
    i2p_destinations: &[String],
    generation: u64,
    actions: &[ScalingAction],
) -> Result<Vec<ScalingAction>> {
    if actions.is_empty() || actions.iter().all(|action| *action == ScalingAction::Hold) {
        return Ok(Vec::new());
    }
    let reservation = demand.reserve_actions(actions)?;
    let actions = reservation.actions().to_vec();
    if actions.is_empty() {
        return Ok(Vec::new());
    }
    let descriptors = plan
        .iter()
        .map(|planned| {
            let desired = reservation.contains(planned.provider);
            scaling_descriptor(
                plan,
                tor_destinations,
                i2p_destinations,
                planned.config.id,
                if desired {
                    TopologyAction::Add
                } else {
                    TopologyAction::Drain
                },
            )
        })
        .collect::<Result<Vec<_>>>()?;
    control
        .advertise_topology(TopologyAdvertisement::new(generation, descriptors)?)
        .await?;
    for action in &actions {
        match *action {
            ScalingAction::Hold => {}
            ScalingAction::Admit { lane_id, .. } => demand.set(lane_id, true)?,
            ScalingAction::Drain { lane_id, .. } => {
                demand.set(lane_id, false)?;
            }
            ScalingAction::Replace { remove, admit, .. } => {
                demand.set(admit, true)?;
                demand.set(remove, false)?;
            }
        }
    }
    reservation.commit();
    for action in &actions {
        match *action {
            ScalingAction::Drain { lane_id, .. } => control.fail_lane(lane_id).await?,
            ScalingAction::Replace { remove, .. } => control.fail_lane(remove).await?,
            _ => {}
        }
    }
    Ok(actions)
}

fn scaling_descriptor(
    plan: &[PlannedLane],
    tor_destinations: &[String],
    i2p_destinations: &[String],
    lane_id: LaneId,
    action: TopologyAction,
) -> Result<EndpointDescriptor> {
    let planned = plan
        .iter()
        .find(|planned| planned.config.id == lane_id)
        .with_context(|| format!("adaptive topology omitted lane {}", lane_id.get()))?;
    let (provider, endpoint) = match planned.provider {
        Provider::Tor { slot } => (
            EndpointProvider::Tor,
            tor_destinations
                .get(slot as usize - 1)
                .context("adaptive topology omitted a Tor destination")?,
        ),
        Provider::I2p { slot } => (
            EndpointProvider::I2p,
            i2p_destinations
                .get(slot as usize - 1)
                .context("adaptive topology omitted an I2P destination")?,
        ),
    };
    Ok(EndpointDescriptor::new(
        planned.config.id,
        planned.config.failure_domain,
        provider,
        action,
        endpoint.clone(),
    )?)
}

#[cfg(test)]
fn adaptive_scaling_config(candidate_lanes: usize, policy: ScalingPolicy) -> ScalingConfig {
    let minimum_active_lanes = candidate_lanes.min(4);
    ScalingConfig {
        minimum_active_lanes,
        maximum_active_lanes: policy
            .maximum_active_lanes
            .min(candidate_lanes)
            .max(minimum_active_lanes),
        minimum_lanes_per_provider: 1,
        scale_up_queue_delay: Duration::from_millis(50),
        scale_down_queue_delay: Duration::from_millis(5),
        scale_up_send_window_percent: 1,
        scale_down_send_window_percent: 0,
        minimum_marginal_goodput_bps: 128_000,
        replacement_gain_percent: 25,
        maximum_startup_latency: Duration::from_secs(300),
        maximum_cpu_millicores: policy.maximum_cpu_millicores,
        maximum_memory_bytes: policy.maximum_memory_bytes,
    }
}

pub(crate) fn send_window_utilization_percent(unacknowledged_bytes: usize) -> u8 {
    if unacknowledged_bytes == 0 {
        return 0;
    }
    let percent = unacknowledged_bytes
        .saturating_mul(100)
        .saturating_add(PRODUCT_SEND_WINDOW_BYTES - 1)
        .checked_div(PRODUCT_SEND_WINDOW_BYTES)
        .unwrap_or(100);
    u8::try_from(percent.min(100)).unwrap_or(100)
}

fn sustained_send_pressure_percent(utilization: u8, consecutive: &mut u8) -> u8 {
    if utilization == 0 {
        *consecutive = 0;
        return 0;
    }
    *consecutive = consecutive.saturating_add(1);
    if utilization >= IMMEDIATE_SEND_PRESSURE_PERCENT
        || *consecutive >= SUSTAINED_SEND_PRESSURE_SAMPLES
    {
        utilization
    } else {
        0
    }
}

fn apply_scale_down_hysteresis(
    action: ScalingAction,
    pending: &mut Option<(LaneId, u8)>,
) -> ScalingAction {
    let ScalingAction::Drain {
        lane_id,
        reason: ScalingReason::MarginalGoodput,
    } = action
    else {
        *pending = None;
        return action;
    };
    let observations = match *pending {
        Some((candidate, observations)) if candidate == lane_id => observations.saturating_add(1),
        _ => 1,
    };
    *pending = Some((lane_id, observations));
    if observations < SCALING_MARGINAL_DRAIN_SAMPLES {
        ScalingAction::Hold
    } else {
        *pending = None;
        action
    }
}

fn estimated_router_cost(provider: Provider) -> (u32, u64, Duration) {
    match provider {
        Provider::Tor { .. } => (
            ESTIMATED_TOR_CPU_MILLICORES,
            ESTIMATED_TOR_MEMORY_BYTES,
            ESTIMATED_TOR_STARTUP,
        ),
        Provider::I2p { .. } => (
            ESTIMATED_I2P_CPU_MILLICORES,
            ESTIMATED_I2P_MEMORY_BYTES,
            ESTIMATED_I2P_STARTUP,
        ),
    }
}

fn provider_id(provider: Provider) -> ProviderId {
    ProviderId::new(match provider {
        Provider::Tor { .. } => 1,
        Provider::I2p { .. } => 2,
    })
    .expect("fixed provider IDs are non-zero")
}

async fn lane_is_active(control: &BondSessionControl, lane_id: LaneId) -> Result<bool> {
    control
        .statistics()
        .await?
        .lanes
        .into_iter()
        .find(|lane| lane.id == lane_id)
        .map(|lane| lane.active)
        .with_context(|| format!("runtime omitted declared lane {}", lane_id.get()))
}

enum InitialRoute {
    Tor {
        router: Arc<TorPoolSlot>,
        socks: Option<String>,
        destination: String,
    },
    I2p {
        router: I2pPoolSlot,
        connector: SamConnector,
        destination: String,
        slot: u32,
    },
}

fn initial_route(
    pool: &RouterPool,
    planned: PlannedLane,
    tor_socks: &[String],
    tor_destinations: &[String],
    i2p_destinations: &[String],
    i2p_connectors: &[SamConnector],
) -> Result<InitialRoute> {
    match planned.provider {
        Provider::Tor { slot } => Ok(InitialRoute::Tor {
            router: pool
                .tor_slots()
                .iter()
                .find(|router| router.slot == slot)
                .cloned()
                .context("client router pool omitted a Tor slot")?,
            socks: tor_socks.get(slot as usize - 1).cloned(),
            destination: tor_destinations
                .get(slot as usize - 1)
                .context("client identity omitted a Tor pool slot")?
                .clone(),
        }),
        Provider::I2p { slot } => Ok(InitialRoute::I2p {
            router: pool.i2p_slot(slot)?.clone(),
            connector: i2p_connectors
                .get(slot as usize - 1)
                .context("client connector omitted an I2P pool slot")?
                .clone(),
            destination: i2p_destinations
                .get(slot as usize - 1)
                .context("client identity omitted an I2P pool slot")?
                .clone(),
            slot,
        }),
    }
}

struct DiscoveryRoutes<'a> {
    pool: &'a RouterPool,
    plan: &'a [PlannedLane],
    tor_socks: &'a [String],
    tor_destinations: &'a [String],
    i2p_destinations: &'a [String],
    i2p_connectors: &'a [SamConnector],
}

async fn connect_discovery_lane(
    routes: DiscoveryRoutes<'_>,
    key: Arc<BondSessionKey>,
    session_id: u64,
) -> Result<(PlannedLane, AuthenticatedLane<TcpStream>)> {
    let discoveries = discovery_lanes(routes.plan);
    if discoveries.is_empty() {
        bail!("bond plan has no discovery lane");
    }
    let mut attempts = JoinSet::new();
    for planned in discoveries {
        let route = initial_route(
            routes.pool,
            planned,
            routes.tor_socks,
            routes.tor_destinations,
            routes.i2p_destinations,
            routes.i2p_connectors,
        )?;
        let key = key.clone();
        attempts.spawn(async move {
            let join = LaneJoin::new(session_id, planned.config.id, planned.config.failure_domain)?;
            let lane = connect_initial_lane(planned, route, &key, join)
                .await
                .with_context(|| {
                    format!(
                        "{} discovery lane {} failed",
                        provider_label(planned.provider),
                        planned.config.id.get()
                    )
                })?;
            Ok((planned, lane))
        });
    }
    first_success(attempts, "bond discovery").await
}

async fn first_success<T: Send + 'static>(
    mut attempts: JoinSet<Result<T>>,
    label: &str,
) -> Result<T> {
    let mut failures = Vec::new();
    while let Some(completed) = attempts.join_next().await {
        match completed {
            Ok(Ok(value)) => {
                attempts.abort_all();
                return Ok(value);
            }
            Ok(Err(error)) => failures.push(format!("{error:#}")),
            Err(error) => failures.push(format!("task failed: {error}")),
        }
    }
    bail!("every {label} candidate failed: {}", failures.join("; "))
}

fn provider_label(provider: Provider) -> &'static str {
    match provider {
        Provider::Tor { .. } => "Tor",
        Provider::I2p { .. } => "I2P",
    }
}

async fn connect_initial_lane(
    planned: PlannedLane,
    route: InitialRoute,
    key: &BondSessionKey,
    join: LaneJoin,
) -> Result<AuthenticatedLane<tokio::net::TcpStream>> {
    let (tor, tor_destination) = match route {
        InitialRoute::Tor {
            router,
            socks,
            destination,
        } => {
            let socks = match socks {
                Some(socks) => socks,
                None => router
                    .ensure_running()
                    .await
                    .context("failed to start Tor discovery router")?,
            };
            (TorConnector::new(socks), destination)
        }
        InitialRoute::I2p {
            router,
            connector,
            destination,
            slot,
        } => {
            router
                .ensure_running()
                .await
                .context("failed to start I2P discovery router")?;
            return connect_i2p_lane(&connector, &destination, slot, key, join).await;
        }
    };

    let deadline = tokio::time::Instant::now() + INITIAL_LANE_DEADLINE;
    let mut failures = Vec::new();
    for attempt in 1..=INITIAL_TOR_AUTH_ATTEMPTS {
        let remaining = deadline.saturating_duration_since(tokio::time::Instant::now());
        if remaining.is_zero() {
            break;
        }
        let isolation = format!("anonssh-bond-initial-{}-{attempt}", planned.config.id.get());
        let result = tokio::time::timeout(remaining, async {
            let stream = tor
                .connect_isolated(&tor_destination, BOND_SERVICE_PORT, Some(&isolation))
                .await?;
            Ok::<_, anyhow::Error>(
                authenticate_client_lane(stream, key, join, HANDSHAKE_TIMEOUT).await?,
            )
        })
        .await;
        match result {
            Ok(Ok(lane)) => return Ok(lane),
            Ok(Err(error)) => failures.push(format!("attempt {attempt}: {error:#}")),
            Err(_) => {
                failures.push(format!(
                    "attempt {attempt}: operation exceeded the remaining formation deadline"
                ));
                break;
            }
        }
        if failures.len() > 4 {
            failures.remove(0);
        }
        let remaining = deadline.saturating_duration_since(tokio::time::Instant::now());
        if remaining <= TOR_RETRY_DELAY {
            break;
        }
        tokio::time::sleep(TOR_RETRY_DELAY).await;
    }
    bail!(
        "failed to establish initial bond lane {} within {} seconds; recent failures: {}",
        planned.config.id.get(),
        INITIAL_LANE_DEADLINE.as_secs(),
        failures.join("; ")
    )
}

#[cfg(test)]
struct InactiveLanes {
    tor: Vec<PlannedLane>,
    i2p_slots: Vec<u32>,
}

#[cfg(test)]
fn inactive_lanes(pool: &RouterPool, stats: &BondRuntimeStats) -> Result<InactiveLanes> {
    let mut inactive = InactiveLanes {
        tor: Vec::new(),
        i2p_slots: Vec::new(),
    };
    for planned in production_plan(pool)? {
        let lane = stats
            .lanes
            .iter()
            .find(|lane| lane.id == planned.config.id)
            .with_context(|| format!("runtime omitted lane {}", planned.config.id.get()))?;
        if !lane.active {
            match planned.provider {
                Provider::Tor { .. } => inactive.tor.push(planned),
                Provider::I2p { slot } => inactive.i2p_slots.push(slot),
            }
        }
    }
    Ok(inactive)
}

async fn connect_tor_lane(
    connector: &TorConnector,
    destination: &str,
    lane_id: LaneId,
    isolation_epoch: u64,
    authentication_attempt: usize,
) -> Result<tokio::net::TcpStream> {
    let mut failures = Vec::new();
    for attempt in 1..=TOR_CONNECT_ATTEMPTS {
        let isolation = format!(
            "anonssh-bond-lane-{}-{isolation_epoch}-{authentication_attempt}-{attempt}",
            lane_id.get()
        );
        match connector
            .connect_isolated(destination, BOND_SERVICE_PORT, Some(&isolation))
            .await
        {
            Ok(stream) => return Ok(stream),
            Err(error) => failures.push(format!("attempt {attempt}: {error:#}")),
        }
        if attempt < TOR_CONNECT_ATTEMPTS {
            tokio::time::sleep(TOR_RETRY_DELAY).await;
        }
    }
    bail!(
        "failed to establish bonded Tor lane {} after {TOR_CONNECT_ATTEMPTS} attempts: {}",
        lane_id.get(),
        failures.join("; ")
    )
}

async fn connect_i2p_lane(
    connector: &SamConnector,
    destination: &str,
    slot: u32,
    key: &BondSessionKey,
    join: LaneJoin,
) -> Result<AuthenticatedLane<tokio::net::TcpStream>> {
    let sam_timeout = sam_setup_timeout();
    let deadline_duration = i2p_connect_deadline_for(sam_timeout);
    let deadline = tokio::time::Instant::now() + deadline_duration;
    let mut failures = Vec::new();
    for attempt in 1..=I2P_CONNECT_ATTEMPTS {
        let remaining = deadline.saturating_duration_since(tokio::time::Instant::now());
        if remaining.is_zero() {
            break;
        }
        let result = tokio::time::timeout(i2p_attempt_timeout(remaining, sam_timeout), async {
            let prepared = PreparedClientLane::new(key, join)?;
            let stream = connector
                .connect_with_initial_payload(
                    destination,
                    BOND_SERVICE_PORT,
                    prepared.initial_payload(),
                )
                .await?;
            Ok::<_, anyhow::Error>(prepared.finish(stream, key, HANDSHAKE_TIMEOUT).await?)
        })
        .await;
        match result {
            Ok(Ok(lane)) => return Ok(lane),
            Ok(Err(error)) => failures.push(format!("attempt {attempt}: {error:#}")),
            Err(_) => failures.push(format!(
                "attempt {attempt}: SAM connection exceeded its bounded attempt deadline"
            )),
        }
        if failures.len() > 4 {
            failures.remove(0);
        }
        let remaining = deadline.saturating_duration_since(tokio::time::Instant::now());
        if attempt == I2P_CONNECT_ATTEMPTS || remaining <= I2P_RETRY_DELAY {
            break;
        }
        tokio::time::sleep(I2P_RETRY_DELAY).await;
    }
    bail!(
        "failed to establish I2P lane slot {slot} within {} seconds; recent failures: {}",
        deadline_duration.as_secs(),
        failures.join("; ")
    )
}

fn validate_pool_identities(
    pool: &RouterPool,
    tor_identities: usize,
    i2p_identities: usize,
) -> Result<()> {
    if !pool.tor_slots().is_empty() && pool.tor_slots().len() != tor_identities {
        bail!(
            "router pool has {} Tor slots but the identity has {tor_identities}",
            pool.tor_slots().len()
        );
    }
    if !pool.i2p_slots().is_empty() && pool.i2p_slots().len() != i2p_identities {
        bail!(
            "router pool has {} I2P slots but the identity has {i2p_identities}",
            pool.i2p_slots().len()
        );
    }
    Ok(())
}

fn production_plan(pool: &RouterPool) -> Result<Vec<PlannedLane>> {
    let mut plan = Vec::with_capacity(pool.tor_slots().len() + pool.i2p_slots().len());
    let mixed = !pool.tor_slots().is_empty() && !pool.i2p_slots().is_empty();
    for router in pool.tor_slots() {
        let rtt_ms = 50_u64
            .checked_add(50_u64.saturating_mul(u64::from(router.slot - 1)))
            .context("Tor pool RTT estimate overflow")?;
        let lane_id = if mixed {
            router.slot
        } else {
            router
                .slot
                .checked_add(TOR_ONLY_LANE_OFFSET)
                .context("Tor-only lane ID overflow")?
        };
        plan.push(planned_lane(
            lane_id,
            router.failure_domain,
            rtt_ms,
            8,
            Provider::Tor { slot: router.slot },
        )?);
    }
    let tor_lanes = u32::try_from(pool.tor_slots().len()).context("Tor lane count overflow")?;
    for router in pool.i2p_slots() {
        let lane_id = if mixed {
            router
                .slot
                .checked_add(tor_lanes)
                .context("mixed I2P lane ID overflow")?
        } else {
            router
                .slot
                .checked_add(I2P_ONLY_LANE_OFFSET)
                .context("I2P-only lane ID overflow")?
        };
        plan.push(planned_lane(
            lane_id,
            router.failure_domain,
            500,
            4,
            Provider::I2p { slot: router.slot },
        )?);
    }
    Ok(plan)
}

pub(crate) fn i2p_lane_id(pool: &RouterPool, slot: u32) -> Result<LaneId> {
    let offset = if pool.tor_slots().is_empty() {
        I2P_ONLY_LANE_OFFSET
    } else {
        u32::try_from(pool.tor_slots().len()).context("Tor lane count overflow")?
    };
    Ok(LaneId::new(
        slot.checked_add(offset)
            .context("I2P pool lane ID overflow")?,
    )?)
}

fn planned_lane(
    id: u32,
    domain: u64,
    rtt_ms: u64,
    rate_mbps: u64,
    provider: Provider,
) -> Result<PlannedLane> {
    Ok(PlannedLane {
        config: LaneConfig::new(
            LaneId::new(id)?,
            FailureDomain::new(domain)?,
            Duration::from_millis(rtt_ms),
            rate_mbps * 1_000_000,
        )?
        .with_provider_group(provider_id(provider)),
        provider,
    })
}

fn runtime_config(session_id: u64) -> BondRuntimeConfig {
    BondRuntimeConfig {
        session_id,
        scheduler: SchedulerConfig {
            low_latency_lane_count: 2,
            ..SchedulerConfig::default()
        },
        sender: SenderConfig {
            max_chunk_payload: 16 * 1024,
            bulk_chunk: anonssh_bond::BulkChunkConfig::default(),
            max_unacknowledged_bytes: PRODUCT_SEND_WINDOW_BYTES,
            max_unacknowledged_chunks: 2_048,
            redundant_realtime: true,
        },
        max_reorder_bytes_per_stream: 8 * 1024 * 1024,
        max_receive_streams: 64,
        stream_receive_window: 4 * 1024 * 1024,
        max_ack_ranges: 32,
        require_stream_open: true,
        retransmit_after: Duration::from_secs(30),
        retransmit_scan_interval: Duration::from_secs(1),
    }
}

#[cfg(test)]
mod tests {
    use std::collections::{BTreeMap, BTreeSet};
    use std::fs;
    use std::sync::atomic::{AtomicBool, Ordering};
    use std::sync::Arc;
    use std::time::{Duration, Instant};

    use anonssh_bond::{
        CapabilityAdvertisement, CapabilityFeatures, EndpointProvider, LaneId, LaneSnapshot,
        ProviderCapability, ScalingAction, ScalingReason, Timestamp, TopologyAction,
        TopologyAdvertisement, TrafficClass,
    };
    use anonssh_bond_tokio::{
        authenticate_client_lane, prepare_server_lane, BondRuntimeStats, BondSession,
        BondSessionKey, LaneJoin, PreparedClientLane, RuntimeLane, ServerIncarnation, SessionRole,
    };
    use tokio::io::{AsyncReadExt, AsyncWriteExt};
    use tokio::net::{TcpListener, TcpStream};
    use tokio::sync::{mpsc, watch, Mutex, Notify};
    use tokio::task::JoinSet;

    use super::{
        adaptive_scaling_config, apply_scale_down_hysteresis, apply_scaling_actions,
        await_discovery_publication, baseline_lanes, baseline_providers, constrained_plan,
        discovery_lanes, first_success, i2p_attempt_timeout, i2p_connect_deadline_for,
        i2p_discovery_deadline_for, inactive_lanes, negotiated_scaling_policy,
        observe_lane_drain_eligibility, observe_lane_health, planned_lane, product_capabilities,
        production_plan, provider_id, run_admission_coordinator, runtime_config,
        scaling_descriptor, send_window_utilization_percent, sustained_send_pressure_percent,
        wait_for_active_lanes, while_lane_desired, AdaptiveScalingTelemetry, AdmissionCommand,
        BondIngress, DesiredOperation, IngressDemand, LaneDemand, PendingPressureAdmissions,
        PlannedLane, PreparedIngressLane, Provider, SessionOutageGuard, SharedResourceGovernor,
        ADMISSION_CHANNEL_CAPACITY, COMPLETED_SESSION_CAPACITY, ESTIMATED_TOR_STARTUP,
        HANDSHAKE_TIMEOUT, MAX_SCALING_EVENTS, PRODUCT_SEND_WINDOW_BYTES, SCALING_DRAIN_DWELL,
        SCALING_MARGINAL_DRAIN_SAMPLES, SCALING_UNHEALTHY_AFTER, SESSION_OUTAGE_DEADLINE,
        SLOT_REPAIR_BACKOFF_MIN, TOR_LANE_ESTABLISHMENT_DEADLINE,
    };
    use crate::product_config::ResourceProfile;
    use crate::router_pool::RouterPool;

    #[test]
    fn all_lane_outage_recovers_briefly_and_expires_at_its_deadline() {
        let started = Instant::now();
        let mut guard = SessionOutageGuard::default();
        assert!(!guard.observe(started, 1));
        assert!(!guard.observe(started + Duration::from_secs(1), 0));
        assert!(!guard.observe(started + SESSION_OUTAGE_DEADLINE, 0));
        assert!(guard.observe(
            started + Duration::from_secs(1) + SESSION_OUTAGE_DEADLINE,
            0
        ));

        assert!(!guard.observe(
            started + Duration::from_secs(2) + SESSION_OUTAGE_DEADLINE,
            1
        ));
        assert!(!guard.observe(
            started + Duration::from_secs(3) + SESSION_OUTAGE_DEADLINE,
            0
        ));
    }

    #[test]
    fn production_plan_has_sixteen_independent_router_domains() {
        let root = std::env::temp_dir().join(format!("anonssh-plan-test-{}", std::process::id()));
        let pool = test_pool(&root);
        let plan = production_plan(&pool).unwrap();
        assert_eq!(plan.len(), 16);
        assert_eq!(
            plan.iter()
                .map(|lane| lane.config.failure_domain)
                .collect::<std::collections::BTreeSet<_>>()
                .len(),
            16
        );
        assert!(matches!(plan[0].provider, Provider::Tor { slot: 1 }));
        assert!(matches!(plan[7].provider, Provider::Tor { slot: 8 }));
        assert!(matches!(plan[8].provider, Provider::I2p { slot: 1 }));
        assert!(matches!(plan[15].provider, Provider::I2p { slot: 8 }));
        assert!(
            plan[..8]
                .iter()
                .all(|lane| lane.config.provider_group
                    == Some(provider_id(Provider::Tor { slot: 1 })))
        );
        assert!(
            plan[8..]
                .iter()
                .all(|lane| lane.config.provider_group
                    == Some(provider_id(Provider::I2p { slot: 1 })))
        );
    }

    #[test]
    fn mixed_discovery_selects_one_policy_representative_per_provider() {
        let root = std::env::temp_dir().join(format!(
            "anonssh-discovery-plan-test-{}",
            std::process::id()
        ));
        let discoveries = discovery_lanes(&production_plan(&test_pool(&root)).unwrap());
        assert_eq!(discoveries.len(), 2);
        assert_eq!(discoveries[0].config.id, LaneId::new(1).unwrap());
        assert!(matches!(discoveries[0].provider, Provider::Tor { slot: 1 }));
        assert_eq!(discoveries[1].config.id, LaneId::new(9).unwrap());
        assert!(matches!(discoveries[1].provider, Provider::I2p { slot: 1 }));
    }

    struct CancellationProbe(Arc<AtomicBool>);

    impl Drop for CancellationProbe {
        fn drop(&mut self) {
            self.0.store(true, Ordering::SeqCst);
        }
    }

    #[tokio::test]
    async fn discovery_race_returns_first_success_and_cancels_stalled_provider() {
        let cancelled = Arc::new(AtomicBool::new(false));
        let (started_tx, started_rx) = tokio::sync::oneshot::channel();
        let mut attempts = JoinSet::new();
        let stalled_cancelled = cancelled.clone();
        attempts.spawn(async move {
            let _probe = CancellationProbe(stalled_cancelled);
            let _ = started_tx.send(());
            std::future::pending::<anyhow::Result<u8>>().await
        });
        started_rx.await.unwrap();
        attempts.spawn(async { Ok::<u8, anyhow::Error>(7) });

        assert_eq!(first_success(attempts, "test").await.unwrap(), 7);
        tokio::time::timeout(Duration::from_secs(1), async {
            while !cancelled.load(Ordering::SeqCst) {
                tokio::task::yield_now().await;
            }
        })
        .await
        .expect("losing discovery task was not cancelled");
    }

    #[test]
    fn resource_profiles_bound_the_live_adaptive_controller() {
        for (profile, maximum) in [
            (ResourceProfile::Low, 4),
            (ResourceProfile::Balanced, 8),
            (ResourceProfile::Performance, 16),
        ] {
            let policy = profile.policy();
            let config = adaptive_scaling_config(16, policy);
            assert_eq!(config.minimum_active_lanes, 4);
            assert_eq!(config.maximum_active_lanes, maximum);
            assert_eq!(config.maximum_cpu_millicores, policy.maximum_cpu_millicores);
            assert_eq!(config.maximum_memory_bytes, policy.maximum_memory_bytes);
        }

        let config = adaptive_scaling_config(8, ResourceProfile::Performance.policy());
        assert_eq!(config.maximum_active_lanes, 8);
    }

    #[test]
    fn aggregate_i2p_deadlines_outlive_every_enclosed_phase() {
        let router_start = Duration::from_secs(300);
        let sam_operation = Duration::from_secs(600);
        let connect_deadline = i2p_connect_deadline_for(sam_operation);
        assert!(connect_deadline > sam_operation);
        assert_eq!(
            i2p_attempt_timeout(connect_deadline, sam_operation),
            sam_operation
        );
        assert_eq!(
            i2p_attempt_timeout(Duration::from_secs(30), sam_operation),
            Duration::from_secs(30)
        );
        assert!(
            i2p_discovery_deadline_for(router_start, sam_operation)
                > router_start.saturating_add(sam_operation)
        );
    }

    #[test]
    fn tor_lane_repair_retries_before_adaptive_replacement() {
        let first_backoff = SLOT_REPAIR_BACKOFF_MIN;
        let second_backoff = super::next_repair_backoff(first_backoff);
        let three_attempt_budget = ESTIMATED_TOR_STARTUP
            .saturating_add(TOR_LANE_ESTABLISHMENT_DEADLINE.saturating_mul(3))
            .saturating_add(first_backoff)
            .saturating_add(second_backoff);

        assert_eq!(TOR_LANE_ESTABLISHMENT_DEADLINE, Duration::from_secs(80));
        assert!(three_attempt_budget < SCALING_UNHEALTHY_AFTER);
    }

    #[tokio::test]
    async fn discovery_deadline_cancels_every_started_supervisor() {
        let (_ready_tx, ready_rx) = tokio::sync::mpsc::channel(1);
        let tasks = vec![
            tokio::spawn(std::future::pending()),
            tokio::spawn(std::future::pending()),
        ];

        let error = await_discovery_publication(Duration::from_millis(1), ready_rx, &tasks)
            .await
            .unwrap_err();
        assert!(error
            .to_string()
            .contains("bond discovery publication exceeded"));
        for task in tasks {
            assert!(task.await.unwrap_err().is_cancelled());
        }
    }

    #[test]
    fn fixed_supervision_latches_every_declared_lane_without_changing_the_baseline() {
        let root =
            std::env::temp_dir().join(format!("anonssh-fixed-demand-test-{}", std::process::id()));
        let plan = production_plan(&test_pool(&root)).unwrap();
        let governor = Arc::new(SharedResourceGovernor::new(
            ResourceProfile::Performance.policy(),
        ));
        governor
            .register_candidates(
                1,
                baseline_providers(&plan),
                plan.iter().map(|planned| planned.provider).collect(),
            )
            .unwrap();
        let (demand, receivers) = LaneDemand::new(&plan, governor, 1).unwrap();
        assert!(receivers.values().any(|receiver| !*receiver.borrow()));

        demand.set_all().unwrap();

        assert!(receivers.values().all(|receiver| *receiver.borrow()));
        assert_eq!(demand.baseline, baseline_lanes(&plan));
    }

    #[test]
    fn product_send_window_pressure_is_bounded_and_proportional() {
        assert_eq!(send_window_utilization_percent(0), 0);
        assert_eq!(send_window_utilization_percent(1), 1);
        assert_eq!(
            send_window_utilization_percent(PRODUCT_SEND_WINDOW_BYTES / 2),
            50
        );
        assert_eq!(
            send_window_utilization_percent(PRODUCT_SEND_WINDOW_BYTES),
            100
        );
        assert_eq!(send_window_utilization_percent(usize::MAX), 100);
    }

    #[test]
    fn speculative_admissions_cancel_as_a_batch_after_sustained_quiet() {
        let fifth = LaneId::new(5).unwrap();
        let sixth = LaneId::new(6).unwrap();
        let mut pending = PendingPressureAdmissions::default();
        let admissions = [
            ScalingAction::Admit {
                lane_id: fifth,
                reason: ScalingReason::QueuePressure,
            },
            ScalingAction::Admit {
                lane_id: sixth,
                reason: ScalingReason::QueuePressure,
            },
        ];
        pending.record(&admissions);

        assert!(pending
            .cancellation_actions(&BTreeSet::new(), true)
            .is_empty());
        assert!(pending
            .cancellation_actions(&BTreeSet::new(), false)
            .is_empty());
        assert_eq!(
            pending.cancellation_actions(&BTreeSet::new(), false),
            vec![
                ScalingAction::Drain {
                    lane_id: fifth,
                    reason: ScalingReason::PressureCleared,
                },
                ScalingAction::Drain {
                    lane_id: sixth,
                    reason: ScalingReason::PressureCleared,
                },
            ]
        );

        pending.record(&admissions);
        let active = BTreeSet::from([fifth, sixth]);
        assert!(pending.cancellation_actions(&active, false).is_empty());
        assert!(pending.lanes.is_empty());

        pending.record(&[ScalingAction::Admit {
            lane_id: fifth,
            reason: ScalingReason::MinimumTopology,
        }]);
        assert!(pending.lanes.is_empty());
    }

    #[test]
    fn adaptive_scaling_telemetry_is_bounded_and_cumulative() {
        let baseline = LaneId::new(1).unwrap();
        let optional = LaneId::new(5).unwrap();
        let mut telemetry = AdaptiveScalingTelemetry::default();
        telemetry.initialize(BTreeSet::from([baseline]));
        let pending = BTreeSet::from([optional]);
        for generation in 1..=u64::try_from(MAX_SCALING_EVENTS + 1).unwrap() {
            telemetry.record(
                generation,
                &[ScalingAction::Admit {
                    lane_id: optional,
                    reason: ScalingReason::QueuePressure,
                }],
                &pending,
            );
        }

        let snapshot = telemetry.snapshot();
        assert_eq!(snapshot.events.len(), MAX_SCALING_EVENTS);
        assert_eq!(snapshot.events.first().unwrap().generation, 2);
        assert_eq!(
            snapshot.events.last().unwrap().generation,
            u64::try_from(MAX_SCALING_EVENTS + 1).unwrap()
        );
        assert_eq!(snapshot.desired_lane_ids, vec![1, 5]);
        assert_eq!(snapshot.pending_pressure_lane_ids, vec![5]);

        telemetry.observe_pending_pressure(&BTreeSet::new());
        let snapshot = telemetry.snapshot();
        assert_eq!(snapshot.desired_lane_ids, vec![1, 5]);
        assert!(snapshot.pending_pressure_lane_ids.is_empty());
        assert_eq!(snapshot.events.len(), MAX_SCALING_EVENTS);

        telemetry.record(
            u64::try_from(MAX_SCALING_EVENTS + 2).unwrap(),
            &[ScalingAction::Drain {
                lane_id: optional,
                reason: ScalingReason::PressureCleared,
            }],
            &BTreeSet::new(),
        );
        let snapshot = telemetry.snapshot();
        assert_eq!(snapshot.desired_lane_ids, vec![1]);
        assert!(snapshot.pending_pressure_lane_ids.is_empty());
    }

    #[test]
    fn marginal_scale_down_requires_stable_quiet_candidate() {
        let lane_id = LaneId::new(5).unwrap();
        let drain = ScalingAction::Drain {
            lane_id,
            reason: ScalingReason::MarginalGoodput,
        };
        let mut pending = None;
        for _ in 1..SCALING_MARGINAL_DRAIN_SAMPLES {
            assert_eq!(
                apply_scale_down_hysteresis(drain, &mut pending),
                ScalingAction::Hold
            );
        }
        assert_eq!(apply_scale_down_hysteresis(drain, &mut pending), drain);
        assert_eq!(pending, None);
    }

    #[test]
    fn scaling_pressure_resets_marginal_scale_down_without_delaying_urgent_actions() {
        let lane_id = LaneId::new(5).unwrap();
        let marginal = ScalingAction::Drain {
            lane_id,
            reason: ScalingReason::MarginalGoodput,
        };
        let mut pending = None;
        assert_eq!(
            apply_scale_down_hysteresis(marginal, &mut pending),
            ScalingAction::Hold
        );
        assert_eq!(
            apply_scale_down_hysteresis(ScalingAction::Hold, &mut pending),
            ScalingAction::Hold
        );
        assert_eq!(pending, None);

        let urgent = ScalingAction::Drain {
            lane_id,
            reason: ScalingReason::ResourcePressure,
        };
        assert_eq!(apply_scale_down_hysteresis(urgent, &mut pending), urgent);
    }

    #[test]
    fn product_send_pressure_requires_sustained_low_occupancy() {
        let mut consecutive = 0;
        assert_eq!(sustained_send_pressure_percent(1, &mut consecutive), 0);
        assert_eq!(consecutive, 1);
        assert_eq!(sustained_send_pressure_percent(1, &mut consecutive), 1);
        assert_eq!(sustained_send_pressure_percent(0, &mut consecutive), 0);
        assert_eq!(consecutive, 0);
        assert_eq!(sustained_send_pressure_percent(75, &mut consecutive), 75);
    }

    #[tokio::test]
    async fn draining_a_slot_cancels_its_inflight_operation() {
        let (demand_tx, mut demand_rx) = watch::channel(true);
        let drain = async move {
            tokio::task::yield_now().await;
            demand_tx.send(false).unwrap();
        };
        let operation = while_lane_desired(&mut demand_rx, std::future::pending::<()>());
        let (outcome, ()) = tokio::join!(operation, drain);
        assert!(matches!(outcome, DesiredOperation::Drained));
    }

    #[test]
    fn optional_lane_must_remain_active_before_drain_evaluation() {
        let lane = LaneId::new(3).unwrap();
        let started = tokio::time::Instant::now();
        let mut active_since = BTreeMap::new();
        assert!(!observe_lane_drain_eligibility(
            lane,
            true,
            true,
            started,
            &mut active_since,
        ));
        assert!(!observe_lane_drain_eligibility(
            lane,
            true,
            true,
            started + SCALING_DRAIN_DWELL - Duration::from_millis(1),
            &mut active_since,
        ));
        assert!(observe_lane_drain_eligibility(
            lane,
            true,
            true,
            started + SCALING_DRAIN_DWELL,
            &mut active_since,
        ));
        assert!(!observe_lane_drain_eligibility(
            lane,
            true,
            false,
            started + SCALING_DRAIN_DWELL,
            &mut active_since,
        ));
        assert!(!observe_lane_drain_eligibility(
            lane,
            true,
            true,
            started + SCALING_DRAIN_DWELL + Duration::from_secs(1),
            &mut active_since,
        ));
    }

    #[test]
    fn baseline_selects_two_lanes_per_provider_or_four_homogeneous_lanes() {
        let root =
            std::env::temp_dir().join(format!("anonssh-baseline-test-{}", std::process::id()));
        let mixed = production_plan(&test_pool(&root.join("mixed"))).unwrap();
        let tor = production_plan(&test_pool_for(&root.join("tor"), true, false)).unwrap();
        let i2p = production_plan(&test_pool_for(&root.join("i2p"), false, true)).unwrap();

        assert_eq!(
            baseline_lanes(&mixed)
                .into_iter()
                .map(|lane| lane.get())
                .collect::<Vec<_>>(),
            vec![1, 2, 9, 10]
        );
        assert_eq!(
            baseline_lanes(&tor)
                .into_iter()
                .map(|lane| lane.get())
                .collect::<Vec<_>>(),
            vec![17, 18, 19, 20]
        );
        assert_eq!(
            baseline_lanes(&i2p)
                .into_iter()
                .map(|lane| lane.get())
                .collect::<Vec<_>>(),
            vec![25, 26, 27, 28]
        );
    }

    #[test]
    fn product_runtime_protects_an_active_latency_lane_and_clean_standby() {
        let config = runtime_config(7);
        assert_eq!(config.scheduler.low_latency_lane_count, 2);
        assert!(config.sender.redundant_realtime);
    }

    #[test]
    fn admitted_lane_gets_bounded_startup_grace_before_it_is_unhealthy() {
        let lane_id = LaneId::new(7).unwrap();
        let started = tokio::time::Instant::now();
        let mut unavailable = BTreeMap::new();
        assert!(observe_lane_health(
            lane_id,
            true,
            false,
            started,
            &mut unavailable
        ));
        assert!(!observe_lane_health(
            lane_id,
            true,
            false,
            started + SCALING_UNHEALTHY_AFTER,
            &mut unavailable
        ));
        assert!(observe_lane_health(
            lane_id,
            true,
            true,
            started + SCALING_UNHEALTHY_AFTER,
            &mut unavailable
        ));
        assert!(unavailable.is_empty());
    }

    #[test]
    fn homogeneous_plans_offer_eight_independent_router_domains() {
        let root =
            std::env::temp_dir().join(format!("anonssh-homogeneous-test-{}", std::process::id()));
        let tor_plan = production_plan(&test_pool_for(&root.join("tor"), true, false)).unwrap();
        let i2p_plan = production_plan(&test_pool_for(&root.join("i2p"), false, true)).unwrap();

        for plan in [&tor_plan, &i2p_plan] {
            assert_eq!(plan.len(), 8);
            assert_eq!(
                plan.iter()
                    .map(|lane| lane.config.failure_domain)
                    .collect::<std::collections::BTreeSet<_>>()
                    .len(),
                8
            );
        }
        assert_eq!(
            tor_plan
                .iter()
                .map(|lane| lane.config.id.get())
                .collect::<Vec<_>>(),
            (17..=24).collect::<Vec<_>>()
        );
        assert_eq!(
            i2p_plan
                .iter()
                .map(|lane| lane.config.id.get())
                .collect::<Vec<_>>(),
            (25..=32).collect::<Vec<_>>()
        );
        assert_ne!(tor_plan[0].config.id, i2p_plan[0].config.id);
        assert!(tor_plan
            .iter()
            .all(|lane| matches!(lane.provider, Provider::Tor { .. })));
        assert!(i2p_plan
            .iter()
            .all(|lane| matches!(lane.provider, Provider::I2p { .. })));
    }

    #[tokio::test]
    async fn ingress_demand_unions_sessions_and_never_drains_the_baseline() {
        let root = std::env::temp_dir().join(format!("anonssh-demand-test-{}", std::process::id()));
        let plan = production_plan(&test_pool(&root)).unwrap();
        let (demand, receivers) =
            IngressDemand::new(&plan, ResourceProfile::Performance.policy()).unwrap();
        let baseline = LaneId::new(1).unwrap();
        let optional = LaneId::new(3).unwrap();

        assert!(*receivers.get(&baseline).unwrap().borrow());
        assert!(!*receivers.get(&optional).unwrap().borrow());
        demand.set(11, optional, true).await.unwrap();
        demand.set(22, optional, true).await.unwrap();
        assert!(*receivers.get(&optional).unwrap().borrow());
        demand.set(11, optional, false).await.unwrap();
        assert!(*receivers.get(&optional).unwrap().borrow());
        demand.release(22).await.unwrap();
        assert!(!*receivers.get(&optional).unwrap().borrow());
        assert!(demand.set(11, baseline, false).await.is_err());
        assert!(*receivers.get(&baseline).unwrap().borrow());
    }

    #[tokio::test]
    async fn ingress_demand_rejects_optional_processes_beyond_the_shared_profile() {
        let root = std::env::temp_dir().join(format!(
            "anonssh-bounded-ingress-demand-test-{}",
            std::process::id()
        ));
        let plan = production_plan(&test_pool(&root)).unwrap();
        let (demand, receivers) = IngressDemand::new(&plan, ResourceProfile::Low.policy()).unwrap();
        let optional = LaneId::new(3).unwrap();

        demand.set(11, optional, true).await.unwrap();

        assert!(!*receivers.get(&optional).unwrap().borrow());
        let snapshot = demand.governor.snapshot().unwrap();
        assert_eq!(snapshot.physical_slots, 4);
        assert_eq!(snapshot.denied_optional_admissions, 1);
    }

    #[test]
    fn bilateral_capabilities_remove_futile_providers_and_bound_resources() {
        let root = std::env::temp_dir().join(format!(
            "anonssh-capability-intersection-test-{}",
            std::process::id()
        ));
        let plan = production_plan(&test_pool(&root)).unwrap();
        let local = CapabilityAdvertisement::new(
            1,
            CapabilityFeatures::CURRENT,
            4 * 1024 * 1024 * 1024,
            8_000,
            5_000,
            16,
            64,
            1,
            vec![
                ProviderCapability::new(EndpointProvider::Tor, 8, 1, 30_000, 5_000, 1_000).unwrap(),
                ProviderCapability::new(EndpointProvider::I2p, 8, 0, 120_000, 0, 0).unwrap(),
            ],
        )
        .unwrap();
        let peer = CapabilityAdvertisement::new(
            7,
            CapabilityFeatures::CURRENT,
            768 * 1024 * 1024,
            900,
            40_000,
            2,
            3,
            1,
            vec![
                ProviderCapability::new(EndpointProvider::Tor, 3, 1, 45_000, 40_000, 800).unwrap(),
            ],
        )
        .unwrap();
        let intersection = local.intersect(&peer).unwrap();
        let constrained = constrained_plan(&plan, &intersection).unwrap();
        assert_eq!(constrained.len(), 3);
        assert!(constrained
            .iter()
            .all(|lane| matches!(lane.provider, Provider::Tor { .. })));
        let policy =
            negotiated_scaling_policy(ResourceProfile::Performance.policy(), &intersection);
        assert_eq!(policy.maximum_active_lanes, 2);
        assert_eq!(policy.maximum_cpu_millicores, 900);
        assert_eq!(policy.maximum_memory_bytes, 768 * 1024 * 1024);
    }

    #[tokio::test]
    async fn adaptive_add_and_drain_converge_over_the_encrypted_control_plane() {
        let plan = (1_u32..=8)
            .map(|slot| {
                planned_lane(
                    slot,
                    u64::from(slot),
                    10 * u64::from(slot),
                    8,
                    Provider::Tor { slot },
                )
                .unwrap()
            })
            .collect::<Vec<_>>();
        let key = Arc::new(BondSessionKey::new([0x83; 32]));
        let (candidate_tx, candidate_rx) = mpsc::channel(ADMISSION_CHANNEL_CAPACITY);
        let (completed_tx, mut completed_rx) = mpsc::channel(COMPLETED_SESSION_CAPACITY);
        let (command_tx, command_rx) = mpsc::channel(ADMISSION_CHANNEL_CAPACITY);
        let coordinator = tokio::spawn(run_admission_coordinator(
            candidate_rx,
            command_rx,
            completed_tx,
            key.clone(),
            plan.clone(),
            ServerIncarnation::from_u64(1).unwrap(),
        ));
        let session_id = 0xad_a7_1e;
        let discovery = connect_admitted_lane(plan[0], session_id, &key, &candidate_tx).await;
        let server = completed_rx.recv().await.unwrap();
        let client = BondSession::spawn(
            runtime_config(session_id),
            vec![discovery],
            SessionRole::Dialer,
        )
        .unwrap();
        for planned in &plan[1..] {
            client.authorize_lane(planned.config).await.unwrap();
        }

        let tor_destinations = (1..=8)
            .map(|slot| format!("tor://adaptive-lane-{slot}.onion"))
            .collect::<Vec<_>>();
        let governor = Arc::new(SharedResourceGovernor::new(
            ResourceProfile::Performance.policy(),
        ));
        governor
            .register_candidates(
                client.session_id(),
                baseline_providers(&plan),
                plan.iter().map(|planned| planned.provider).collect(),
            )
            .unwrap();
        let (client_demand, client_receivers) =
            LaneDemand::new(&plan, governor, client.session_id()).unwrap();
        let (server_demand, server_receivers) =
            IngressDemand::new(&plan, ResourceProfile::Performance.policy()).unwrap();
        let descriptors = plan
            .iter()
            .map(|planned| {
                (
                    planned.config.id,
                    scaling_descriptor(
                        &plan,
                        &tor_destinations,
                        &[],
                        planned.config.id,
                        TopologyAction::Add,
                    )
                    .unwrap(),
                )
            })
            .collect();
        let (_unused_completed_tx, unused_completed_rx) = mpsc::channel(1);
        let (unused_admission_tx, _unused_admission_rx) = mpsc::channel(1);
        let ingress = BondIngress {
            completed_rx: Mutex::new(unused_completed_rx),
            admission_tx: unused_admission_tx,
            demand: Arc::new(server_demand),
            descriptors,
            plan: plan.clone(),
            scaling_policy: ResourceProfile::Performance.policy(),
            negotiated_capabilities: Mutex::new(BTreeMap::new()),
            capability_generations: Mutex::new(BTreeMap::new()),
            tasks: Vec::new(),
        };
        let client_capabilities = product_capabilities(
            1,
            client.protocol_version(),
            &plan,
            ResourceProfile::Performance.policy(),
            &client.statistics().await.unwrap(),
        )
        .unwrap();
        ingress
            .apply_capability_request(&server.control(), client_capabilities)
            .await
            .unwrap();
        let partial = TopologyAdvertisement::new(
            99,
            vec![ingress.descriptors.values().next().unwrap().clone()],
        )
        .unwrap();
        let error = ingress
            .apply_topology_request(&server.control(), partial)
            .await
            .unwrap_err();
        assert!(error
            .to_string()
            .contains("product topology snapshot declared 1 of 8 recoverable lanes"));
        let optional = plan[4..]
            .iter()
            .map(|planned| planned.config.id)
            .collect::<Vec<_>>();
        for lane_id in &optional {
            assert!(!*client_receivers.get(lane_id).unwrap().borrow());
            assert!(!*server_receivers.get(lane_id).unwrap().borrow());
        }

        let admissions = optional
            .iter()
            .copied()
            .map(|lane_id| ScalingAction::Admit {
                lane_id,
                reason: ScalingReason::QueuePressure,
            })
            .collect::<Vec<_>>();
        apply_scaling_actions(
            &client.control(),
            &plan,
            &client_demand,
            &tor_destinations,
            &[],
            1,
            &admissions,
        )
        .await
        .unwrap();
        let advertisement = tokio::time::timeout(Duration::from_secs(2), server.accept_topology())
            .await
            .unwrap()
            .unwrap();
        assert_eq!(advertisement.descriptors.len(), plan.len());
        assert!(advertisement
            .descriptors
            .iter()
            .all(|descriptor| descriptor.action == TopologyAction::Add));
        let server_control = server.control();
        ingress
            .apply_topology_request(&server_control, advertisement)
            .await
            .unwrap();
        for lane_id in &optional {
            assert!(*client_receivers.get(lane_id).unwrap().borrow());
            assert!(*server_receivers.get(lane_id).unwrap().borrow());
        }

        let drains = optional
            .iter()
            .copied()
            .map(|lane_id| ScalingAction::Drain {
                lane_id,
                reason: ScalingReason::PressureCleared,
            })
            .collect::<Vec<_>>();
        apply_scaling_actions(
            &client.control(),
            &plan,
            &client_demand,
            &tor_destinations,
            &[],
            2,
            &drains,
        )
        .await
        .unwrap();
        let advertisement = tokio::time::timeout(Duration::from_secs(2), server.accept_topology())
            .await
            .unwrap()
            .unwrap();
        assert_eq!(advertisement.descriptors.len(), plan.len());
        for descriptor in &advertisement.descriptors {
            let expected = if optional.contains(&descriptor.lane_id) {
                TopologyAction::Drain
            } else {
                TopologyAction::Add
            };
            assert_eq!(descriptor.action, expected);
        }
        ingress
            .apply_topology_request(&server_control, advertisement)
            .await
            .unwrap();
        for lane_id in &optional {
            assert!(!*client_receivers.get(lane_id).unwrap().borrow());
            assert!(!*server_receivers.get(lane_id).unwrap().borrow());
        }

        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
        command_tx
            .send(AdmissionCommand::Release { session_id })
            .await
            .unwrap();
        drop(candidate_tx);
        drop(command_tx);
        coordinator.await.unwrap();
    }

    #[test]
    fn supervision_classifies_inactive_provider_lanes() {
        let root = std::env::temp_dir().join(format!("anonssh-health-test-{}", std::process::id()));
        let pool = test_pool(&root);
        let plan = production_plan(&pool).unwrap();
        let stats = BondRuntimeStats {
            observed_at: Timestamp::ZERO,
            lanes: plan
                .iter()
                .map(|planned| LaneSnapshot {
                    id: planned.config.id,
                    failure_domain: planned.config.failure_domain,
                    provider_group: planned.config.provider_group,
                    active: !matches!(planned.config.id.get(), 2 | 16),
                    delivery_measured: true,
                    reserved_for_low_latency: planned.config.id.get() == 1,
                    smoothed_round_trip_time: Duration::from_millis(10),
                    delivery_rate_bps: 1_000_000,
                    queued_through: Timestamp::ZERO,
                    bytes_scheduled: 0,
                    bytes_acknowledged: 0,
                })
                .collect(),
            received_by_lane: Vec::new(),
            new_data_frames: 0,
            redundant_realtime_frames: 0,
            dropped_redundant_realtime_frames: 0,
            retransmitted_frames: 0,
            ping_frames: 0,
            pong_frames: 0,
            liveness_failures: 0,
            acknowledgement_frames: 0,
            window_update_frames: 0,
            replayed_control_frames: 0,
            delivered_bytes: 0,
            reorder_high_water: 0,
            unacknowledged_bytes: 0,
            bulk_chunk_pressure_limit: 16 * 1024,
            backpressured_streams: 0,
            stream_backpressure_events: 0,
            active_streams: 0,
            retired_stream_tombstones: 0,
        };
        let inactive = inactive_lanes(&pool, &stats).unwrap();
        assert_eq!(inactive.tor.len(), 1);
        assert_eq!(inactive.tor[0].config.id, plan[1].config.id);
        assert_eq!(inactive.i2p_slots, vec![8]);
    }

    fn test_pool(root: &std::path::Path) -> RouterPool {
        test_pool_for(root, true, true)
    }

    fn test_pool_for(root: &std::path::Path, include_tor: bool, include_i2p: bool) -> RouterPool {
        let executable = fs::canonicalize(std::env::current_exe().unwrap()).unwrap();
        let tor = if include_tor {
            (1_u32..=8)
                .map(|slot| {
                    (
                        slot,
                        vec![(
                            root.join(format!("tor-{slot}")),
                            format!("127.0.0.1:{}", 29_049 + slot).parse().unwrap(),
                            format!("127.0.0.1:{}", 29_149 + slot).parse().unwrap(),
                        )],
                        u64::from(slot),
                    )
                })
                .collect()
        } else {
            Vec::new()
        };
        let i2p = if include_i2p {
            (1_u32..=8)
                .map(|slot| {
                    (
                        slot,
                        root.join(format!("i2p-{slot}")),
                        format!("127.0.0.1:{}", 27_655 + slot).parse().unwrap(),
                        100 + u64::from(slot),
                    )
                })
                .collect()
        } else {
            Vec::new()
        };
        RouterPool::new(executable.clone(), tor, executable, i2p).unwrap()
    }

    #[tokio::test]
    async fn i2p_only_topology_admits_and_transfers_from_its_discovery_lane() {
        let plan = (1_u32..=4)
            .map(|slot| {
                planned_lane(
                    slot,
                    100 + u64::from(slot),
                    20 * u64::from(slot),
                    8,
                    Provider::I2p { slot },
                )
                .unwrap()
            })
            .collect::<Vec<_>>();
        let key = Arc::new(BondSessionKey::new([0x49; 32]));
        let (candidate_tx, candidate_rx) = mpsc::channel(ADMISSION_CHANNEL_CAPACITY);
        let (completed_tx, mut completed_rx) = mpsc::channel(COMPLETED_SESSION_CAPACITY);
        let (command_tx, command_rx) = mpsc::channel(ADMISSION_CHANNEL_CAPACITY);
        let coordinator = tokio::spawn(run_admission_coordinator(
            candidate_rx,
            command_rx,
            completed_tx,
            key.clone(),
            plan.clone(),
            ServerIncarnation::from_u64(1).unwrap(),
        ));
        let session_id = 0x12_2f;
        let discovery = connect_admitted_lane(plan[0], session_id, &key, &candidate_tx).await;
        let mut server = tokio::time::timeout(Duration::from_secs(2), completed_rx.recv())
            .await
            .expect("discovery lane did not activate the session")
            .expect("admission coordinator stopped");
        let client = BondSession::spawn(
            runtime_config(session_id),
            vec![discovery],
            SessionRole::Dialer,
        )
        .unwrap();
        for planned in &plan[1..] {
            client.authorize_lane(planned.config).await.unwrap();
        }

        let initial_client_stats = client.statistics().await.unwrap();
        let initial_server_stats = server.statistics().await.unwrap();
        assert_eq!(initial_client_stats.lanes.len(), 4);
        assert_eq!(initial_server_stats.lanes.len(), 4);
        assert_eq!(
            initial_client_stats
                .lanes
                .iter()
                .filter(|lane| lane.active)
                .count(),
            1
        );
        assert_eq!(
            initial_server_stats
                .lanes
                .iter()
                .filter(|lane| lane.active)
                .count(),
            1
        );

        let payload = b"ordered i2p-only striped bond".repeat(16_384);
        assert_eq!(
            transfer(&client, &mut server, payload.clone()).await,
            payload
        );

        for planned in &plan[1..] {
            let lane = connect_admitted_lane(*planned, session_id, &key, &candidate_tx).await;
            client.add_lane(lane).await.unwrap();
        }
        wait_for_active_lanes(
            &server,
            &plan.iter().map(|lane| lane.config.id).collect::<Vec<_>>(),
            Duration::from_secs(2),
            "progressive test",
        )
        .await
        .unwrap();
        assert_eq!(
            server
                .statistics()
                .await
                .unwrap()
                .lanes
                .iter()
                .filter(|lane| lane.active)
                .count(),
            4
        );

        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
        command_tx
            .send(AdmissionCommand::Release { session_id })
            .await
            .unwrap();
        drop(candidate_tx);
        drop(command_tx);
        coordinator.await.unwrap();
    }

    #[tokio::test]
    async fn concurrent_admission_isolates_sessions_and_one_lane_replacement() {
        let plan = vec![
            planned_lane(1, 1, 5, 8, Provider::Tor { slot: 1 }).unwrap(),
            planned_lane(2, 2, 15, 8, Provider::Tor { slot: 2 }).unwrap(),
            planned_lane(3, 101, 20, 8, Provider::I2p { slot: 1 }).unwrap(),
            planned_lane(4, 102, 25, 8, Provider::I2p { slot: 2 }).unwrap(),
        ];
        let key = Arc::new(BondSessionKey::new([0x71; 32]));
        let (candidate_tx, candidate_rx) = mpsc::channel(ADMISSION_CHANNEL_CAPACITY);
        let (completed_tx, mut completed_rx) = mpsc::channel(COMPLETED_SESSION_CAPACITY);
        let (command_tx, command_rx) = mpsc::channel(ADMISSION_CHANNEL_CAPACITY);
        let coordinator = tokio::spawn(run_admission_coordinator(
            candidate_rx,
            command_rx,
            completed_tx,
            key.clone(),
            plan.clone(),
            ServerIncarnation::from_u64(1).unwrap(),
        ));

        let first_id = 0xa11ce;
        let second_id = 0xb0b;
        let mut first_lanes = Vec::new();
        let mut second_lanes = Vec::new();
        for planned in &plan {
            let first = connect_admitted_lane(*planned, first_id, &key, &candidate_tx).await;
            if planned.config.id.get() == 3 {
                drop(first);
                first_lanes
                    .push(connect_admitted_lane(*planned, first_id, &key, &candidate_tx).await);
            } else {
                first_lanes.push(first);
            }
            second_lanes
                .push(connect_admitted_lane(*planned, second_id, &key, &candidate_tx).await);
        }

        let mut servers = BTreeMap::new();
        for _ in 0..2 {
            let session = tokio::time::timeout(Duration::from_secs(2), completed_rx.recv())
                .await
                .unwrap()
                .unwrap();
            servers.insert(session.session_id(), session);
        }
        let mut first_server = servers.remove(&first_id).unwrap();
        let mut second_server = servers.remove(&second_id).unwrap();
        let first_client =
            BondSession::spawn(runtime_config(first_id), first_lanes, SessionRole::Dialer).unwrap();
        let second_client =
            BondSession::spawn(runtime_config(second_id), second_lanes, SessionRole::Dialer)
                .unwrap();

        let first_initial = transfer(
            &first_client,
            &mut first_server,
            b"first session before replacement".repeat(512),
        );
        let second_initial = transfer(
            &second_client,
            &mut second_server,
            b"second session remains independent".repeat(512),
        );
        let (first_received, second_received) = tokio::join!(first_initial, second_initial);
        assert!(first_received.starts_with(b"first session"));
        assert!(second_received.starts_with(b"second session"));

        let replaced = plan[3];
        first_client.fail_lane(replaced.config.id).await.unwrap();
        assert!(first_server
            .statistics()
            .await
            .unwrap()
            .lanes
            .iter()
            .find(|lane| lane.id == replaced.config.id)
            .is_some_and(|lane| lane.active));
        let replacement = connect_admitted_lane(replaced, first_id, &key, &candidate_tx).await;
        first_client.add_lane(replacement).await.unwrap();
        for planned in &plan[..3] {
            let (client_failed, server_failed) = tokio::join!(
                first_client.fail_lane(planned.config.id),
                first_server.fail_lane(planned.config.id),
            );
            client_failed.unwrap();
            server_failed.unwrap();
        }

        let first_payload = b"replacement-only first session".repeat(4_096);
        let second_payload = b"uninterrupted second session".repeat(4_096);
        let first_transfer = transfer(&first_client, &mut first_server, first_payload.clone());
        let second_transfer = transfer(&second_client, &mut second_server, second_payload.clone());
        let (first_received, second_received) = tokio::join!(first_transfer, second_transfer);
        assert_eq!(first_received, first_payload);
        assert_eq!(second_received, second_payload);
        let first_stats = first_server.statistics().await.unwrap();
        assert!(first_stats
            .lanes
            .iter()
            .find(|lane| lane.id == replaced.config.id)
            .is_some_and(|lane| lane.active && lane.bytes_scheduled > 0));
        assert!(second_server
            .statistics()
            .await
            .unwrap()
            .lanes
            .iter()
            .all(|lane| lane.active));

        let (
            first_client_shutdown,
            first_server_shutdown,
            second_client_shutdown,
            second_server_shutdown,
        ) = tokio::join!(
            first_client.shutdown(),
            first_server.shutdown(),
            second_client.shutdown(),
            second_server.shutdown(),
        );
        first_client_shutdown.unwrap();
        first_server_shutdown.unwrap();
        second_client_shutdown.unwrap();
        second_server_shutdown.unwrap();
        command_tx
            .send(AdmissionCommand::Release {
                session_id: first_id,
            })
            .await
            .unwrap();
        command_tx
            .send(AdmissionCommand::Release {
                session_id: second_id,
            })
            .await
            .unwrap();
        drop(candidate_tx);
        drop(command_tx);
        coordinator.await.unwrap();
    }

    #[tokio::test]
    async fn stalled_handshake_completion_does_not_block_another_session() {
        let plan = vec![
            planned_lane(1, 1, 5, 8, Provider::Tor { slot: 1 }).unwrap(),
            planned_lane(2, 2, 15, 8, Provider::Tor { slot: 2 }).unwrap(),
            planned_lane(3, 101, 20, 8, Provider::I2p { slot: 1 }).unwrap(),
            planned_lane(4, 102, 25, 8, Provider::I2p { slot: 2 }).unwrap(),
        ];
        let key = Arc::new(BondSessionKey::new([0x72; 32]));
        let (candidate_tx, candidate_rx) = mpsc::channel(ADMISSION_CHANNEL_CAPACITY);
        let (completed_tx, mut completed_rx) = mpsc::channel(COMPLETED_SESSION_CAPACITY);
        let (command_tx, command_rx) = mpsc::channel(ADMISSION_CHANNEL_CAPACITY);
        let coordinator = tokio::spawn(run_admission_coordinator(
            candidate_rx,
            command_rx,
            completed_tx,
            key.clone(),
            plan.clone(),
            ServerIncarnation::from_u64(1).unwrap(),
        ));

        let stalled_id = 0x5a11ed;
        let gate = Arc::new(Notify::new());
        let stalled_client =
            connect_gated_candidate(plan[0], stalled_id, &key, &candidate_tx, gate.clone()).await;
        tokio::task::yield_now().await;

        let healthy_id = 0x1a7e;
        let healthy_lanes = tokio::time::timeout(Duration::from_secs(2), async {
            let mut lanes = Vec::new();
            for planned in &plan {
                lanes.push(connect_admitted_lane(*planned, healthy_id, &key, &candidate_tx).await);
            }
            lanes
        })
        .await
        .expect("a stalled completion blocked independent admission");
        let mut healthy_server = tokio::time::timeout(Duration::from_secs(2), completed_rx.recv())
            .await
            .expect("healthy session was not admitted")
            .expect("admission coordinator stopped");
        assert_eq!(healthy_server.session_id(), healthy_id);
        let healthy_client = BondSession::spawn(
            runtime_config(healthy_id),
            healthy_lanes,
            SessionRole::Dialer,
        )
        .unwrap();
        let payload = b"independent admission bypassed a stalled handshake".repeat(512);
        assert_eq!(
            transfer(&healthy_client, &mut healthy_server, payload.clone()).await,
            payload
        );

        gate.notify_one();
        tokio::time::timeout(Duration::from_secs(2), stalled_client)
            .await
            .expect("gated handshake did not finish")
            .unwrap();
        let (client_shutdown, server_shutdown) =
            tokio::join!(healthy_client.shutdown(), healthy_server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
        command_tx
            .send(AdmissionCommand::Release {
                session_id: stalled_id,
            })
            .await
            .unwrap();
        command_tx
            .send(AdmissionCommand::Release {
                session_id: healthy_id,
            })
            .await
            .unwrap();
        drop(candidate_tx);
        drop(command_tx);
        coordinator.await.unwrap();
    }

    async fn connect_admitted_lane(
        planned: PlannedLane,
        session_id: u64,
        key: &Arc<BondSessionKey>,
        candidate_tx: &mpsc::Sender<PreparedIngressLane>,
    ) -> RuntimeLane {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let address = listener.local_addr().unwrap();
        let join =
            LaneJoin::new(session_id, planned.config.id, planned.config.failure_domain).unwrap();
        let client = async {
            let stream = TcpStream::connect(address).await.unwrap();
            authenticate_client_lane(stream, key, join, HANDSHAKE_TIMEOUT)
                .await
                .unwrap()
        };
        let server = async {
            let (stream, _) = listener.accept().await.unwrap();
            let prepared = prepare_server_lane(stream, key, HANDSHAKE_TIMEOUT)
                .await
                .unwrap();
            candidate_tx
                .send(PreparedIngressLane::new(planned, prepared))
                .await
                .unwrap();
        };
        let (client, ()) = tokio::join!(client, server);
        RuntimeLane::from_authenticated(planned.config, client)
    }

    async fn connect_gated_candidate(
        planned: PlannedLane,
        session_id: u64,
        key: &Arc<BondSessionKey>,
        candidate_tx: &mpsc::Sender<PreparedIngressLane>,
        gate: Arc<Notify>,
    ) -> tokio::task::JoinHandle<()> {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let address = listener.local_addr().unwrap();
        let join =
            LaneJoin::new(session_id, planned.config.id, planned.config.failure_domain).unwrap();
        let client_key = key.clone();
        let client = tokio::spawn(async move {
            let mut stream = TcpStream::connect(address).await.unwrap();
            let prepared = PreparedClientLane::new(&client_key, join).unwrap();
            stream.write_all(prepared.initial_payload()).await.unwrap();
            prepared
                .finish(stream, &client_key, HANDSHAKE_TIMEOUT)
                .await
                .unwrap();
        });
        let (stream, _) = listener.accept().await.unwrap();
        let prepared = prepare_server_lane(stream, key, HANDSHAKE_TIMEOUT)
            .await
            .unwrap();
        candidate_tx
            .send(PreparedIngressLane::new(planned, prepared).with_completion_gate(gate))
            .await
            .unwrap();
        client
    }

    async fn transfer(client: &BondSession, server: &mut BondSession, payload: Vec<u8>) -> Vec<u8> {
        let mut outbound = client.open_stream(TrafficClass::Bulk).await.unwrap();
        let mut inbound = server.accept_stream().await.unwrap();
        let send = async {
            outbound.write_all(&payload).await.unwrap();
            outbound.shutdown().await.unwrap();
            let mut response = Vec::new();
            outbound.read_to_end(&mut response).await.unwrap();
            assert!(response.is_empty());
        };
        let receive = async {
            let mut received = Vec::new();
            inbound.read_to_end(&mut received).await.unwrap();
            inbound.shutdown().await.unwrap();
            received
        };
        let ((), received) = tokio::join!(send, receive);
        received
    }
}
