use std::collections::{BTreeMap, BTreeSet, VecDeque};
use std::net::SocketAddr;
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex as StdMutex};
use std::time::{Duration, Instant};

use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};
use tokio::sync::Mutex;
use tokio::task::JoinSet;

use crate::product_config::ExternalTorService;
use crate::runtime::{
    AppConfig, I2pdManager, ManagedProcessUsage, ReservedLoopbackEndpoint, TorManager,
};

pub const PRODUCTION_TOR_SLOTS: usize = 8;
pub const PRODUCTION_TOR_CANDIDATES: usize = 16;
pub const PRODUCTION_I2P_SLOTS: usize = 8;
const ROUTER_START_ATTEMPTS: usize = 3;
const MAX_ROUTER_PROGRESS_EVENTS: usize = 128;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum RouterPoolRole {
    Server,
    Client,
}

impl RouterPoolRole {
    fn state_root(self, primary: &Path) -> PathBuf {
        match self {
            Self::Server => primary.to_owned(),
            Self::Client => primary
                .parent()
                .unwrap_or_else(|| Path::new("."))
                .join("client")
                .join(primary.file_name().unwrap_or_default()),
        }
    }
}

pub type TorCandidateSpec = (PathBuf, SocketAddr, SocketAddr);
pub type TorSlotSpec = (u32, Vec<TorCandidateSpec>, u64);
pub type I2pSlotSpec = (u32, PathBuf, SocketAddr, u64);

#[derive(Clone, Debug)]
pub struct ConfiguredRouterTopology {
    pub tor: Vec<TorSlotSpec>,
    pub i2p: Vec<I2pSlotSpec>,
}

impl ConfiguredRouterTopology {
    pub fn validate(&self) -> Result<()> {
        validate_pool_specs(&self.tor, &self.i2p)
    }
}

pub struct TorPoolSlot {
    pub slot: u32,
    pub failure_domain: u64,
    candidates: Vec<Arc<TorManager>>,
    selected: Mutex<Option<Arc<TorManager>>>,
    progress: Arc<RouterProgressTracker>,
}

#[derive(Clone)]
pub struct I2pPoolSlot {
    pub slot: u32,
    pub failure_domain: u64,
    pub sam_endpoint: SocketAddr,
    pub manager: Arc<I2pdManager>,
    progress: Arc<RouterProgressTracker>,
}

pub struct RouterPool {
    tor: Vec<Arc<TorPoolSlot>>,
    i2p: Vec<I2pPoolSlot>,
    progress: Arc<RouterProgressTracker>,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum RouterProvider {
    Tor,
    I2p,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum RouterProgressPhase {
    Idle,
    Starting,
    Repairing,
    RouterReady,
    Active,
    Backoff,
    Draining,
    Stopped,
    Failed,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum RouterProgressDetail {
    Configured,
    RouterStartup,
    RouterAvailable,
    IngressRouteReady,
    BondLaneReady,
    DirectRouteReady,
    StartupFailed,
    LaneEstablishmentFailed,
    RetryScheduled,
    DemandReleased,
    RouterStopped,
    StopFailed,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct RouterProgressEvent {
    pub sequence: u64,
    pub elapsed_millis: u64,
    pub provider: RouterProvider,
    pub slot: u32,
    pub phase: RouterProgressPhase,
    pub detail: RouterProgressDetail,
    pub attempt: u32,
    pub operation_deadline_millis: Option<u64>,
    pub retry_after_millis: Option<u64>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct RouterProgressSnapshot {
    pub schema: String,
    pub observed_millis: u64,
    pub slots: Vec<RouterProgressEvent>,
    pub recent_events: Vec<RouterProgressEvent>,
}

struct RouterProgressTracker {
    started_at: Instant,
    inner: StdMutex<RouterProgressInner>,
}

struct RouterProgressInner {
    next_sequence: u64,
    current: BTreeMap<(RouterProvider, u32), RouterProgressEvent>,
    recent: VecDeque<RouterProgressEvent>,
}

struct RouterProgressUpdate {
    provider: RouterProvider,
    slot: u32,
    phase: RouterProgressPhase,
    detail: RouterProgressDetail,
    attempt: u32,
    operation_deadline_millis: Option<u64>,
    retry_after_millis: Option<u64>,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct RouterProcessSample {
    pub provider: RouterProvider,
    pub slot: u32,
    pub usage: Option<ManagedProcessUsage>,
    pub startup_latency: Option<std::time::Duration>,
}

impl RouterProgressSnapshot {
    pub(crate) fn empty() -> Self {
        Self::default()
    }
}

impl Default for RouterProgressSnapshot {
    fn default() -> Self {
        Self {
            schema: "anonssh.router-progress.v1".to_owned(),
            observed_millis: 0,
            slots: Vec::new(),
            recent_events: Vec::new(),
        }
    }
}

impl RouterProgressTracker {
    fn new() -> Self {
        Self {
            started_at: Instant::now(),
            inner: StdMutex::new(RouterProgressInner {
                next_sequence: 1,
                current: BTreeMap::new(),
                recent: VecDeque::new(),
            }),
        }
    }

    fn register(&self, provider: RouterProvider, slot: u32) {
        self.record(RouterProgressUpdate {
            provider,
            slot,
            phase: RouterProgressPhase::Idle,
            detail: RouterProgressDetail::Configured,
            attempt: 0,
            operation_deadline_millis: None,
            retry_after_millis: None,
        });
    }

    fn begin(&self, provider: RouterProvider, slot: u32, deadline: Duration) -> u32 {
        let mut inner = self.lock();
        let attempt = inner
            .current
            .get(&(provider, slot))
            .map_or(1, |event| event.attempt.saturating_add(1));
        let phase = if attempt == 1 {
            RouterProgressPhase::Starting
        } else {
            RouterProgressPhase::Repairing
        };
        self.record_locked(
            &mut inner,
            RouterProgressUpdate {
                provider,
                slot,
                phase,
                detail: RouterProgressDetail::RouterStartup,
                attempt,
                operation_deadline_millis: Some(duration_millis(deadline)),
                retry_after_millis: None,
            },
        );
        attempt
    }

    fn update(
        &self,
        provider: RouterProvider,
        slot: u32,
        phase: RouterProgressPhase,
        detail: RouterProgressDetail,
        retry_after: Option<Duration>,
    ) {
        let mut inner = self.lock();
        let attempt = inner
            .current
            .get(&(provider, slot))
            .map_or(0, |event| event.attempt);
        self.record_locked(
            &mut inner,
            RouterProgressUpdate {
                provider,
                slot,
                phase,
                detail,
                attempt,
                operation_deadline_millis: None,
                retry_after_millis: retry_after.map(duration_millis),
            },
        );
    }

    fn record(&self, update: RouterProgressUpdate) {
        let mut inner = self.lock();
        self.record_locked(&mut inner, update);
    }

    fn record_locked(&self, inner: &mut RouterProgressInner, update: RouterProgressUpdate) {
        let event = RouterProgressEvent {
            sequence: inner.next_sequence,
            elapsed_millis: duration_millis(self.started_at.elapsed()),
            provider: update.provider,
            slot: update.slot,
            phase: update.phase,
            detail: update.detail,
            attempt: update.attempt,
            operation_deadline_millis: update.operation_deadline_millis,
            retry_after_millis: update.retry_after_millis,
        };
        inner.next_sequence = inner.next_sequence.saturating_add(1);
        inner
            .current
            .insert((update.provider, update.slot), event.clone());
        if inner.recent.len() == MAX_ROUTER_PROGRESS_EVENTS {
            inner.recent.pop_front();
        }
        inner.recent.push_back(event);
    }

    fn snapshot(
        &self,
        tor_slots: &BTreeSet<u32>,
        i2p_slots: &BTreeSet<u32>,
    ) -> RouterProgressSnapshot {
        let included = |event: &&RouterProgressEvent| match event.provider {
            RouterProvider::Tor => tor_slots.contains(&event.slot),
            RouterProvider::I2p => i2p_slots.contains(&event.slot),
        };
        let inner = self.lock();
        RouterProgressSnapshot {
            schema: "anonssh.router-progress.v1".to_owned(),
            observed_millis: duration_millis(self.started_at.elapsed()),
            slots: inner.current.values().filter(included).cloned().collect(),
            recent_events: inner.recent.iter().filter(included).cloned().collect(),
        }
    }

    fn lock(&self) -> std::sync::MutexGuard<'_, RouterProgressInner> {
        match self.inner.lock() {
            Ok(inner) => inner,
            Err(poisoned) => poisoned.into_inner(),
        }
    }
}

fn duration_millis(duration: Duration) -> u64 {
    u64::try_from(duration.as_millis()).unwrap_or(u64::MAX)
}

fn tor_slot_start_deadline(start_timeout: Duration) -> Duration {
    start_timeout.saturating_mul(u32::try_from(ROUTER_START_ATTEMPTS + 1).unwrap_or(u32::MAX))
}

impl TorPoolSlot {
    pub(crate) async fn ensure_running(&self) -> Result<String> {
        self.progress.begin(
            RouterProvider::Tor,
            self.slot,
            tor_slot_start_deadline(crate::runtime::tor_start_timeout()),
        );
        let result = self.ensure_running_inner().await;
        self.progress.update(
            RouterProvider::Tor,
            self.slot,
            if result.is_ok() {
                RouterProgressPhase::RouterReady
            } else {
                RouterProgressPhase::Failed
            },
            if result.is_ok() {
                RouterProgressDetail::RouterAvailable
            } else {
                RouterProgressDetail::StartupFailed
            },
            None,
        );
        result
    }

    async fn ensure_running_inner(&self) -> Result<String> {
        let mut selected = self.selected.lock().await;
        if let Some(manager) = selected.as_ref() {
            // Prefer retained state, but do not serialize its full retry budget ahead
            // of the reserve candidate race.
            if let Ok(endpoint) = manager.ensure_running().await {
                return Ok(endpoint);
            }
            *selected = None;
        }

        let mut starts = JoinSet::new();
        for (index, manager) in self.candidates.iter().cloned().enumerate() {
            let candidate = manager.clone();
            let slot = self.slot;
            starts.spawn(async move {
                let result = ensure_tor(&candidate, slot).await;
                (index, manager, result)
            });
        }
        let mut failures = Vec::new();
        while let Some(started) = starts.join_next().await {
            let (index, manager, result) = started.context("Tor candidate task failed")?;
            match result {
                Ok(endpoint) => {
                    starts.abort_all();
                    while starts.join_next().await.is_some() {}
                    for candidate in &self.candidates {
                        if !Arc::ptr_eq(candidate, &manager) {
                            candidate.stop().await.with_context(|| {
                                format!(
                                    "failed to stop unused Tor candidate for slot {}",
                                    self.slot
                                )
                            })?;
                        }
                    }
                    *selected = Some(manager);
                    return Ok(endpoint);
                }
                Err(error) => failures.push(format!("candidate {}: {error:#}", index + 1)),
            }
        }
        bail!(
            "all Tor candidates failed for slot {}: {}",
            self.slot,
            failures.join("; ")
        )
    }

    pub async fn manager(&self) -> Result<Arc<TorManager>> {
        self.selected
            .lock()
            .await
            .clone()
            .with_context(|| format!("Tor slot {} has no selected candidate", self.slot))
    }

    pub async fn state_root(&self) -> Result<PathBuf> {
        Ok(self.manager().await?.state_root().to_owned())
    }

    async fn stop(&self) -> Result<()> {
        self.progress.update(
            RouterProvider::Tor,
            self.slot,
            RouterProgressPhase::Draining,
            RouterProgressDetail::DemandReleased,
            None,
        );
        let mut failures = Vec::new();
        for (index, manager) in self.candidates.iter().enumerate() {
            if let Err(error) = manager.stop().await {
                failures.push(format!("candidate {}: {error:#}", index + 1));
            }
        }
        *self.selected.lock().await = None;
        if failures.is_empty() {
            self.progress.update(
                RouterProvider::Tor,
                self.slot,
                RouterProgressPhase::Stopped,
                RouterProgressDetail::RouterStopped,
                None,
            );
            Ok(())
        } else {
            self.progress.update(
                RouterProvider::Tor,
                self.slot,
                RouterProgressPhase::Failed,
                RouterProgressDetail::StopFailed,
                None,
            );
            bail!(
                "Tor slot {} cleanup failed: {}",
                self.slot,
                failures.join("; ")
            )
        }
    }

    pub(crate) async fn stop_selected(&self) -> Result<()> {
        self.stop_selected_if_running().await
    }

    pub(crate) async fn stop_selected_if_running(&self) -> Result<()> {
        self.progress.update(
            RouterProvider::Tor,
            self.slot,
            RouterProgressPhase::Draining,
            RouterProgressDetail::DemandReleased,
            None,
        );
        let manager = self.selected.lock().await.clone();
        let result = match manager {
            Some(manager) => manager.stop().await,
            None => Ok(()),
        };
        self.progress.update(
            RouterProvider::Tor,
            self.slot,
            if result.is_ok() {
                RouterProgressPhase::Stopped
            } else {
                RouterProgressPhase::Failed
            },
            if result.is_ok() {
                RouterProgressDetail::RouterStopped
            } else {
                RouterProgressDetail::StopFailed
            },
            None,
        );
        result
    }

    pub(crate) fn mark_active(&self) {
        self.progress.update(
            RouterProvider::Tor,
            self.slot,
            RouterProgressPhase::Active,
            RouterProgressDetail::BondLaneReady,
            None,
        );
    }

    pub(crate) fn mark_ingress_ready(&self) {
        self.progress.update(
            RouterProvider::Tor,
            self.slot,
            RouterProgressPhase::Active,
            RouterProgressDetail::IngressRouteReady,
            None,
        );
    }

    pub(crate) fn mark_backoff(&self, retry_after: Duration) {
        self.progress.update(
            RouterProvider::Tor,
            self.slot,
            RouterProgressPhase::Backoff,
            RouterProgressDetail::RetryScheduled,
            Some(retry_after),
        );
    }

    pub(crate) fn mark_direct_ready(&self) {
        self.progress.update(
            RouterProvider::Tor,
            self.slot,
            RouterProgressPhase::Active,
            RouterProgressDetail::DirectRouteReady,
            None,
        );
    }

    pub(crate) fn mark_lane_failure(&self) {
        self.progress.update(
            RouterProvider::Tor,
            self.slot,
            RouterProgressPhase::Failed,
            RouterProgressDetail::LaneEstablishmentFailed,
            None,
        );
    }

    fn candidate_count(&self) -> usize {
        self.candidates.len()
    }
}

impl I2pPoolSlot {
    pub(crate) async fn ensure_running(&self) -> Result<()> {
        self.progress.begin(
            RouterProvider::I2p,
            self.slot,
            crate::runtime::i2p_start_timeout()
                .saturating_mul(u32::try_from(ROUTER_START_ATTEMPTS).unwrap_or(u32::MAX)),
        );
        let result = ensure_i2p(&self.manager, self.slot).await;
        self.progress.update(
            RouterProvider::I2p,
            self.slot,
            if result.is_ok() {
                RouterProgressPhase::RouterReady
            } else {
                RouterProgressPhase::Failed
            },
            if result.is_ok() {
                RouterProgressDetail::RouterAvailable
            } else {
                RouterProgressDetail::StartupFailed
            },
            None,
        );
        result
    }

    pub(crate) async fn stop_if_running(&self) -> Result<()> {
        self.progress.update(
            RouterProvider::I2p,
            self.slot,
            RouterProgressPhase::Draining,
            RouterProgressDetail::DemandReleased,
            None,
        );
        let result = self.manager.stop().await;
        self.progress.update(
            RouterProvider::I2p,
            self.slot,
            if result.is_ok() {
                RouterProgressPhase::Stopped
            } else {
                RouterProgressPhase::Failed
            },
            if result.is_ok() {
                RouterProgressDetail::RouterStopped
            } else {
                RouterProgressDetail::StopFailed
            },
            None,
        );
        result
    }

    pub(crate) fn mark_active(&self) {
        self.progress.update(
            RouterProvider::I2p,
            self.slot,
            RouterProgressPhase::Active,
            RouterProgressDetail::BondLaneReady,
            None,
        );
    }

    pub(crate) fn mark_ingress_ready(&self) {
        self.progress.update(
            RouterProvider::I2p,
            self.slot,
            RouterProgressPhase::Active,
            RouterProgressDetail::IngressRouteReady,
            None,
        );
    }

    pub(crate) fn mark_backoff(&self, retry_after: Duration) {
        self.progress.update(
            RouterProvider::I2p,
            self.slot,
            RouterProgressPhase::Backoff,
            RouterProgressDetail::RetryScheduled,
            Some(retry_after),
        );
    }

    pub(crate) fn mark_direct_ready(&self) {
        self.progress.update(
            RouterProvider::I2p,
            self.slot,
            RouterProgressPhase::Active,
            RouterProgressDetail::DirectRouteReady,
            None,
        );
    }

    pub(crate) fn mark_lane_failure(&self) {
        self.progress.update(
            RouterProvider::I2p,
            self.slot,
            RouterProgressPhase::Failed,
            RouterProgressDetail::LaneEstablishmentFailed,
            None,
        );
    }
}

impl RouterPool {
    pub fn prefix(&self, tor_slots: usize, i2p_slots: usize) -> Result<Self> {
        if tor_slots == 0 && i2p_slots == 0 {
            bail!("router pool prefix requires at least one provider slot");
        }
        if tor_slots > self.tor.len() || i2p_slots > self.i2p.len() {
            bail!("router pool prefix exceeds the available topology");
        }
        Ok(Self {
            tor: self.tor[..tor_slots].to_vec(),
            i2p: self.i2p[..i2p_slots].to_vec(),
            progress: self.progress.clone(),
        })
    }

    pub fn production(
        config: &AppConfig,
        tor_binary: Option<PathBuf>,
        i2pd_binary: Option<PathBuf>,
        external_tor_services: &[ExternalTorService],
    ) -> Result<Self> {
        Self::production_for_role(
            config,
            tor_binary,
            i2pd_binary,
            external_tor_services,
            RouterPoolRole::Server,
        )
    }

    pub fn production_client(
        config: &AppConfig,
        tor_binary: Option<PathBuf>,
        i2pd_binary: Option<PathBuf>,
        external_tor_services: &[ExternalTorService],
    ) -> Result<Self> {
        Self::production_for_role(
            config,
            tor_binary,
            i2pd_binary,
            external_tor_services,
            RouterPoolRole::Client,
        )
    }

    fn production_for_role(
        config: &AppConfig,
        tor_binary: Option<PathBuf>,
        i2pd_binary: Option<PathBuf>,
        external_tor_services: &[ExternalTorService],
        role: RouterPoolRole,
    ) -> Result<Self> {
        let topology = configured_router_topology_for_role(
            config,
            tor_binary.is_some(),
            i2pd_binary.is_some(),
            role,
        )?;
        Self::new_selected(
            tor_binary,
            topology.tor,
            i2pd_binary,
            topology.i2p,
            None,
            true,
            external_tor_services,
        )
    }

    #[cfg(test)]
    pub fn new(
        tor_binary: PathBuf,
        tor: Vec<TorSlotSpec>,
        i2pd_binary: PathBuf,
        i2p: Vec<I2pSlotSpec>,
    ) -> Result<Self> {
        Self::new_selected(
            Some(tor_binary),
            tor,
            Some(i2pd_binary),
            i2p,
            None,
            false,
            &[],
        )
    }

    pub fn new_reserved(
        tor_binary: PathBuf,
        tor: Vec<TorSlotSpec>,
        i2pd_binary: PathBuf,
        i2p: Vec<I2pSlotSpec>,
        reservations: Vec<ReservedLoopbackEndpoint>,
    ) -> Result<Self> {
        Self::new_selected(
            Some(tor_binary),
            tor,
            Some(i2pd_binary),
            i2p,
            Some(reservations),
            false,
            &[],
        )
    }

    fn new_selected(
        tor_binary: Option<PathBuf>,
        tor: Vec<TorSlotSpec>,
        i2pd_binary: Option<PathBuf>,
        i2p: Vec<I2pSlotSpec>,
        reservations: Option<Vec<ReservedLoopbackEndpoint>>,
        reserve_configured_endpoints: bool,
        external_tor_services: &[ExternalTorService],
    ) -> Result<Self> {
        validate_pool_specs(&tor, &i2p)?;
        let progress = Arc::new(RouterProgressTracker::new());
        let tor_binary = if tor.is_empty() {
            None
        } else {
            Some(tor_binary.context("Tor slots require a Tor executable")?)
        };
        let i2pd_binary = if i2p.is_empty() {
            None
        } else {
            Some(i2pd_binary.context("I2P slots require an i2pd executable")?)
        };
        let require_reservations = reservations.is_some();
        let mut reservations = reservations
            .unwrap_or_default()
            .into_iter()
            .map(|reservation| Ok((reservation.address()?, reservation)))
            .collect::<Result<BTreeMap<_, _>>>()?;
        let mut tor_managers = Vec::with_capacity(tor.len());
        for (slot, candidates, failure_domain) in tor {
            let mut managers = Vec::with_capacity(candidates.len());
            for (data_dir, socks, control) in candidates {
                let binary = tor_binary
                    .as_ref()
                    .expect("validated Tor executable")
                    .clone();
                let manager = if require_reservations {
                    let socks_reservation = reservations
                        .remove(&socks)
                        .with_context(|| format!("Tor SOCKS endpoint {socks} is not reserved"))?;
                    let control_reservation = reservations.remove(&control).with_context(|| {
                        format!("Tor control endpoint {control} is not reserved")
                    })?;
                    TorManager::new_reserved(
                        data_dir,
                        binary,
                        socks_reservation,
                        control_reservation,
                    )?
                } else if reserve_configured_endpoints {
                    match external_tor_services
                        .iter()
                        .find(|service| service.socks == socks && service.control == control)
                    {
                        Some(service) => TorManager::new_external_at(
                            data_dir,
                            binary,
                            socks,
                            control,
                            service.cookie_file.clone(),
                        )?,
                        None => TorManager::new_at(data_dir, binary, socks, control)?,
                    }
                } else {
                    TorManager::new_at_unreserved(data_dir, binary, socks, control)?
                };
                managers.push(Arc::new(manager));
            }
            tor_managers.push(Arc::new(TorPoolSlot {
                slot,
                failure_domain,
                candidates: managers,
                selected: Mutex::new(None),
                progress: progress.clone(),
            }));
            progress.register(RouterProvider::Tor, slot);
        }
        let mut i2p_managers = Vec::with_capacity(i2p.len());
        for (slot, data_dir, sam_endpoint, failure_domain) in i2p {
            let binary = i2pd_binary
                .as_ref()
                .expect("validated i2pd executable")
                .clone();
            let manager = if require_reservations {
                let reservation = reservations
                    .remove(&sam_endpoint)
                    .with_context(|| format!("I2P SAM endpoint {sam_endpoint} is not reserved"))?;
                I2pdManager::new_reserved(data_dir, binary, reservation)?
            } else if reserve_configured_endpoints {
                I2pdManager::new(data_dir, binary, sam_endpoint)?
            } else {
                I2pdManager::new_unreserved(data_dir, binary, sam_endpoint)?
            };
            i2p_managers.push(I2pPoolSlot {
                slot,
                failure_domain,
                sam_endpoint,
                manager: Arc::new(manager),
                progress: progress.clone(),
            });
            progress.register(RouterProvider::I2p, slot);
        }
        if !reservations.is_empty() {
            bail!("router pool received reservations for undeclared endpoints");
        }
        tor_managers.sort_by_key(|router| router.slot);
        i2p_managers.sort_by_key(|router| router.slot);
        Ok(Self {
            tor: tor_managers,
            i2p: i2p_managers,
            progress,
        })
    }

    pub async fn stop(&self) -> Result<()> {
        let mut failures = Vec::new();
        for router in &self.i2p {
            if let Err(error) = router.stop_if_running().await {
                failures.push(format!("I2P slot {}: {error:#}", router.slot));
            }
        }
        for router in &self.tor {
            if let Err(error) = router.stop().await {
                failures.push(format!("Tor slot {}: {error:#}", router.slot));
            }
        }
        if failures.is_empty() {
            Ok(())
        } else {
            bail!("router pool cleanup failed: {}", failures.join("; "))
        }
    }

    pub async fn stop_i2p_slot(&self, slot: u32) -> Result<()> {
        self.i2p_slot(slot)?.stop_if_running().await
    }

    pub async fn ensure_i2p_slot(&self, slot: u32) -> Result<()> {
        self.i2p_slot(slot)?.ensure_running().await
    }

    pub async fn stop_tor_slot(&self, slot: u32) -> Result<()> {
        self.tor_slot(slot)?.stop_selected().await
    }

    pub async fn ensure_tor_slot(&self, slot: u32) -> Result<String> {
        self.tor_slot(slot)?.ensure_running().await
    }

    pub fn tor_slots(&self) -> &[Arc<TorPoolSlot>] {
        &self.tor
    }

    pub fn tor_candidate_count(&self) -> usize {
        self.tor.iter().map(|slot| slot.candidate_count()).sum()
    }

    pub fn tor_slot(&self, slot: u32) -> Result<&TorPoolSlot> {
        self.tor
            .iter()
            .find(|router| router.slot == slot)
            .map(Arc::as_ref)
            .with_context(|| format!("router pool has no Tor slot {slot}"))
    }

    pub fn i2p_slots(&self) -> &[I2pPoolSlot] {
        &self.i2p
    }

    pub fn i2p_slot(&self, slot: u32) -> Result<&I2pPoolSlot> {
        self.i2p
            .iter()
            .find(|router| router.slot == slot)
            .with_context(|| format!("router pool has no I2P slot {slot}"))
    }

    pub async fn process_samples(&self) -> Result<Vec<RouterProcessSample>> {
        let mut samples = Vec::with_capacity(self.tor.len() + self.i2p.len());
        for router in &self.tor {
            let manager = router
                .selected
                .try_lock()
                .ok()
                .and_then(|selected| selected.clone());
            let (usage, startup_latency) = match manager {
                Some(manager) => (manager.try_process_usage()?, manager.startup_latency()),
                None => (None, None),
            };
            samples.push(RouterProcessSample {
                provider: RouterProvider::Tor,
                slot: router.slot,
                usage,
                startup_latency,
            });
        }
        for router in &self.i2p {
            samples.push(RouterProcessSample {
                provider: RouterProvider::I2p,
                slot: router.slot,
                usage: router.manager.try_process_usage()?,
                startup_latency: router.manager.startup_latency(),
            });
        }
        Ok(samples)
    }

    pub fn progress_snapshot(&self) -> RouterProgressSnapshot {
        let tor_slots = self.tor.iter().map(|router| router.slot).collect();
        let i2p_slots = self.i2p.iter().map(|router| router.slot).collect();
        self.progress.snapshot(&tor_slots, &i2p_slots)
    }
}

async fn ensure_tor(manager: &TorManager, slot: u32) -> Result<String> {
    let mut failures = Vec::new();
    for attempt in 1..=ROUTER_START_ATTEMPTS {
        match manager.ensure_running().await {
            Ok(endpoint) => return Ok(endpoint),
            Err(error) => failures.push(format!("attempt {attempt}: {error:#}")),
        }
    }
    bail!(
        "failed to start Tor pool slot {slot} after {ROUTER_START_ATTEMPTS} attempts: {}",
        failures.join("; ")
    )
}

async fn ensure_i2p(manager: &I2pdManager, slot: u32) -> Result<()> {
    let mut failures = Vec::new();
    for attempt in 1..=ROUTER_START_ATTEMPTS {
        match manager.ensure_running().await {
            Ok(()) => return Ok(()),
            Err(error) => failures.push(format!("attempt {attempt}: {error:#}")),
        }
    }
    bail!(
        "failed to start I2P pool slot {} after {ROUTER_START_ATTEMPTS} attempts: {}",
        slot,
        failures.join("; ")
    )
}

pub fn configured_router_topology(
    config: &AppConfig,
    include_tor: bool,
    include_i2p: bool,
) -> Result<ConfiguredRouterTopology> {
    configured_router_topology_for_role(config, include_tor, include_i2p, RouterPoolRole::Server)
}

fn configured_router_topology_for_role(
    config: &AppConfig,
    include_tor: bool,
    include_i2p: bool,
    role: RouterPoolRole,
) -> Result<ConfiguredRouterTopology> {
    let (tor_socks_variable, tor_socks_port) = match role {
        RouterPoolRole::Server => ("ANONSSH_TOR_POOL_SOCKS_ADDRS", 19_050),
        RouterPoolRole::Client => ("ANONSSH_CLIENT_TOR_POOL_SOCKS_ADDRS", 20_050),
    };
    let (tor_control_variable, tor_control_port) = match role {
        RouterPoolRole::Server => ("ANONSSH_TOR_POOL_CONTROL_ADDRS", 19_150),
        RouterPoolRole::Client => ("ANONSSH_CLIENT_TOR_POOL_CONTROL_ADDRS", 20_150),
    };
    let (reserve_socks_variable, reserve_socks_port) = match role {
        RouterPoolRole::Server => ("ANONSSH_TOR_RESERVE_SOCKS_ADDRS", 19_250),
        RouterPoolRole::Client => ("ANONSSH_CLIENT_TOR_RESERVE_SOCKS_ADDRS", 20_250),
    };
    let (reserve_control_variable, reserve_control_port) = match role {
        RouterPoolRole::Server => ("ANONSSH_TOR_RESERVE_CONTROL_ADDRS", 19_350),
        RouterPoolRole::Client => ("ANONSSH_CLIENT_TOR_RESERVE_CONTROL_ADDRS", 20_350),
    };
    let (i2p_variable, i2p_port) = match role {
        RouterPoolRole::Server => ("ANONSSH_I2P_POOL_ADDRS", 7_656),
        RouterPoolRole::Client => ("ANONSSH_CLIENT_I2P_POOL_ADDRS", 8_656),
    };
    let tor_root = role.state_root(&config.tor_dir);
    let i2p_root = role.state_root(&config.i2pd_dir);
    let tor = if include_tor {
        let tor_socks =
            production_pool_endpoints(tor_socks_variable, PRODUCTION_TOR_SLOTS, tor_socks_port)?;
        let tor_controls = production_pool_endpoints(
            tor_control_variable,
            PRODUCTION_TOR_SLOTS,
            tor_control_port,
        )?;
        let reserve_socks = production_pool_endpoints(
            reserve_socks_variable,
            PRODUCTION_TOR_SLOTS,
            reserve_socks_port,
        )?;
        let reserve_controls = production_pool_endpoints(
            reserve_control_variable,
            PRODUCTION_TOR_SLOTS,
            reserve_control_port,
        )?;
        tor_socks
            .into_iter()
            .zip(tor_controls)
            .zip(reserve_socks.into_iter().zip(reserve_controls))
            .enumerate()
            .map(
                |(index, ((socks, control), (reserve_socks, reserve_control)))| {
                    let slot = u32::try_from(index + 1).context("Tor pool slot overflow")?;
                    Ok((
                        slot,
                        vec![
                            (tor_slot_data_dir(&tor_root, slot), socks, control),
                            (
                                tor_reserve_data_dir(&tor_root, slot),
                                reserve_socks,
                                reserve_control,
                            ),
                        ],
                        u64::from(slot),
                    ))
                },
            )
            .collect::<Result<Vec<_>>>()?
    } else {
        Vec::new()
    };
    let i2p = if include_i2p {
        production_pool_endpoints(i2p_variable, PRODUCTION_I2P_SLOTS, i2p_port)?
            .into_iter()
            .enumerate()
            .map(|(index, endpoint)| {
                let slot = u32::try_from(index + 1).context("I2P pool slot overflow")?;
                Ok((
                    slot,
                    i2p_slot_data_dir(&i2p_root, slot),
                    endpoint,
                    100 + u64::from(slot),
                ))
            })
            .collect::<Result<Vec<_>>>()?
    } else {
        Vec::new()
    };
    let topology = ConfiguredRouterTopology { tor, i2p };
    topology.validate()?;
    Ok(topology)
}

fn validate_pool_specs(tor: &[TorSlotSpec], i2p: &[I2pSlotSpec]) -> Result<()> {
    if tor.is_empty() && i2p.is_empty() {
        bail!("router pool requires at least one provider slot");
    }
    let mut slots = BTreeSet::new();
    let mut domains = BTreeSet::new();
    let mut endpoints = BTreeSet::new();
    let mut roots = BTreeSet::new();
    for (slot, candidates, failure_domain) in tor {
        if *slot == 0 || !slots.insert(("tor", *slot)) {
            bail!("Tor pool slots must be unique and non-zero");
        }
        if candidates.is_empty() {
            bail!("Tor pool slots require at least one candidate");
        }
        if *failure_domain == 0 || !domains.insert(*failure_domain) {
            bail!("router pool failure domains must be unique and non-zero");
        }
        for (data_dir, socks, control) in candidates {
            if !socks.ip().is_loopback()
                || socks.port() == 0
                || !control.ip().is_loopback()
                || control.port() == 0
            {
                bail!("router pool endpoints must be non-zero loopback sockets");
            }
            if !endpoints.insert(*socks) || !endpoints.insert(*control) {
                bail!("router pool endpoints must be unique");
            }
            if !roots.insert(data_dir) {
                bail!("router pool state roots must be unique");
            }
        }
    }
    for (slot, data_dir, sam_endpoint, failure_domain) in i2p {
        if *slot == 0 || !slots.insert(("i2p", *slot)) {
            bail!("I2P pool slots must be unique and non-zero");
        }
        if *failure_domain == 0 || !domains.insert(*failure_domain) {
            bail!("router pool failure domains must be unique and non-zero");
        }
        if !sam_endpoint.ip().is_loopback() || sam_endpoint.port() == 0 {
            bail!("router pool endpoints must be non-zero loopback sockets");
        }
        if !endpoints.insert(*sam_endpoint) {
            bail!("router pool endpoints must be unique");
        }
        if !roots.insert(data_dir) {
            bail!("router pool state roots must be unique");
        }
    }
    Ok(())
}

fn production_pool_endpoints(
    variable: &str,
    slots: usize,
    first_port: u16,
) -> Result<Vec<SocketAddr>> {
    let values = match std::env::var(variable) {
        Ok(value) => value
            .split(',')
            .map(str::trim)
            .filter(|value| !value.is_empty())
            .map(str::to_owned)
            .collect::<Vec<_>>(),
        Err(std::env::VarError::NotPresent) => (0..slots)
            .map(|index| {
                let offset = u16::try_from(index).context("router pool endpoint overflow")?;
                let port = first_port
                    .checked_add(offset)
                    .context("router pool endpoint overflow")?;
                Ok(format!("127.0.0.1:{port}"))
            })
            .collect::<Result<Vec<_>>>()?,
        Err(error) => return Err(error.into()),
    };
    if values.len() != slots {
        bail!("{variable} must contain exactly {slots} endpoints");
    }
    values
        .into_iter()
        .map(|value| {
            let endpoint: SocketAddr = value
                .parse()
                .with_context(|| format!("invalid endpoint in {variable}"))?;
            if !endpoint.ip().is_loopback() || endpoint.port() == 0 {
                bail!("{variable} entries must be non-zero loopback sockets");
            }
            Ok(endpoint)
        })
        .collect()
}

fn tor_slot_data_dir(primary: &Path, slot: u32) -> PathBuf {
    slot_data_dir(primary, "tor-slot", slot)
}

fn tor_reserve_data_dir(primary: &Path, slot: u32) -> PathBuf {
    let parent = primary.parent().unwrap_or_else(|| Path::new("."));
    parent.join(format!("tor-slot-{slot}-reserve"))
}

fn i2p_slot_data_dir(primary: &Path, slot: u32) -> PathBuf {
    slot_data_dir(primary, "i2pd-slot", slot)
}

fn slot_data_dir(primary: &Path, prefix: &str, slot: u32) -> PathBuf {
    if slot == 1 {
        return primary.to_owned();
    }
    let parent = primary.parent().unwrap_or_else(|| Path::new("."));
    parent.join(format!("{prefix}-{slot}"))
}

#[cfg(test)]
mod tests {
    use std::fs;
    use std::sync::Arc;
    use std::time::Duration;

    use super::{
        configured_router_topology_for_role, i2p_slot_data_dir, tor_reserve_data_dir,
        tor_slot_data_dir, tor_slot_start_deadline, RouterPool, RouterPoolRole,
        RouterProgressDetail, RouterProgressPhase, RouterProgressTracker, RouterProvider,
        TorPoolSlot, MAX_ROUTER_PROGRESS_EVENTS,
    };
    use crate::runtime::AppConfig;
    use tokio::sync::Mutex;

    #[test]
    fn production_slot_one_preserves_the_existing_state_root() {
        let primary = std::path::Path::new("/state/anonssh/i2pd");
        assert_eq!(i2p_slot_data_dir(primary, 1), primary);
        assert_eq!(
            i2p_slot_data_dir(primary, 2),
            std::path::Path::new("/state/anonssh/i2pd-slot-2")
        );
        let tor = std::path::Path::new("/state/anonssh/tor");
        assert_eq!(tor_slot_data_dir(tor, 1), tor);
        assert_eq!(
            tor_slot_data_dir(tor, 4),
            std::path::Path::new("/state/anonssh/tor-slot-4")
        );
        assert_eq!(
            tor_reserve_data_dir(tor, 1),
            std::path::Path::new("/state/anonssh/tor-slot-1-reserve")
        );
    }

    #[test]
    fn production_client_and_server_topologies_are_disjoint() {
        let config = AppConfig::temporary(std::path::Path::new("/state/anonssh-test"));
        let server =
            configured_router_topology_for_role(&config, true, true, RouterPoolRole::Server)
                .unwrap();
        let client =
            configured_router_topology_for_role(&config, true, true, RouterPoolRole::Client)
                .unwrap();

        let endpoints = |topology: &super::ConfiguredRouterTopology| {
            topology
                .tor
                .iter()
                .flat_map(|(_, candidates, _)| {
                    candidates
                        .iter()
                        .flat_map(|(_, socks, control)| [*socks, *control])
                })
                .chain(topology.i2p.iter().map(|(_, _, endpoint, _)| *endpoint))
                .collect::<std::collections::BTreeSet<_>>()
        };
        let roots = |topology: &super::ConfiguredRouterTopology| {
            topology
                .tor
                .iter()
                .flat_map(|(_, candidates, _)| candidates.iter().map(|(root, _, _)| root.clone()))
                .chain(topology.i2p.iter().map(|(_, root, _, _)| root.clone()))
                .collect::<std::collections::BTreeSet<_>>()
        };

        assert!(endpoints(&server).is_disjoint(&endpoints(&client)));
        assert!(roots(&server).is_disjoint(&roots(&client)));
        assert_eq!(server.tor[0].1[0].0, config.tor_dir);
        assert_eq!(server.i2p[0].1, config.i2pd_dir);
        assert_eq!(
            client.tor[0].1[0].0,
            config.tor_dir.parent().unwrap().join("client/tor")
        );
        assert_eq!(
            client.i2p[0].1,
            config.i2pd_dir.parent().unwrap().join("client/i2pd")
        );
    }

    #[test]
    fn tor_progress_deadline_covers_selected_attempt_then_candidate_race() {
        assert_eq!(
            tor_slot_start_deadline(Duration::from_secs(180)),
            Duration::from_secs(720)
        );
    }

    #[test]
    fn router_progress_is_ordered_bounded_redacted_and_repair_aware() {
        let progress = RouterProgressTracker::new();
        progress.register(RouterProvider::Tor, 1);
        progress.register(RouterProvider::I2p, 1);

        assert_eq!(
            progress.begin(RouterProvider::I2p, 1, std::time::Duration::from_secs(300)),
            1
        );
        progress.update(
            RouterProvider::I2p,
            1,
            RouterProgressPhase::Failed,
            RouterProgressDetail::StartupFailed,
            None,
        );
        progress.update(
            RouterProvider::I2p,
            1,
            RouterProgressPhase::Backoff,
            RouterProgressDetail::RetryScheduled,
            Some(std::time::Duration::from_secs(5)),
        );
        assert_eq!(
            progress.begin(RouterProvider::I2p, 1, std::time::Duration::from_secs(300)),
            2
        );
        progress.update(
            RouterProvider::I2p,
            1,
            RouterProgressPhase::RouterReady,
            RouterProgressDetail::RouterAvailable,
            None,
        );
        progress.update(
            RouterProvider::I2p,
            1,
            RouterProgressPhase::Active,
            RouterProgressDetail::IngressRouteReady,
            None,
        );
        progress.update(
            RouterProvider::I2p,
            1,
            RouterProgressPhase::Active,
            RouterProgressDetail::BondLaneReady,
            None,
        );
        progress.update(
            RouterProvider::I2p,
            1,
            RouterProgressPhase::Draining,
            RouterProgressDetail::DemandReleased,
            None,
        );
        progress.update(
            RouterProvider::I2p,
            1,
            RouterProgressPhase::Stopped,
            RouterProgressDetail::RouterStopped,
            None,
        );

        let tor = std::collections::BTreeSet::from([1]);
        let i2p = std::collections::BTreeSet::from([1]);
        let snapshot = progress.snapshot(&tor, &i2p);
        let i2p_events = snapshot
            .recent_events
            .iter()
            .filter(|event| event.provider == RouterProvider::I2p)
            .collect::<Vec<_>>();
        assert!(snapshot
            .recent_events
            .windows(2)
            .all(|events| events[0].sequence < events[1].sequence));
        assert_eq!(i2p_events[1].phase, RouterProgressPhase::Starting);
        assert_eq!(i2p_events[1].attempt, 1);
        assert_eq!(i2p_events[1].operation_deadline_millis, Some(300_000));
        assert_eq!(i2p_events[3].retry_after_millis, Some(5_000));
        assert_eq!(i2p_events[4].phase, RouterProgressPhase::Repairing);
        assert_eq!(i2p_events[4].attempt, 2);
        assert_eq!(
            i2p_events[6].detail,
            RouterProgressDetail::IngressRouteReady
        );
        assert_eq!(i2p_events[7].detail, RouterProgressDetail::BondLaneReady);
        assert!(i2p_events
            .iter()
            .any(|event| event.phase == RouterProgressPhase::Active && event.attempt == 2));
        assert_eq!(
            i2p_events.last().unwrap().phase,
            RouterProgressPhase::Stopped
        );
        let encoded = serde_json::to_string(&snapshot).unwrap();
        for forbidden in ["127.0.0.1", "/state/", "destination", "identity"] {
            assert!(!encoded.contains(forbidden));
        }

        for _ in 0..=MAX_ROUTER_PROGRESS_EVENTS {
            progress.update(
                RouterProvider::Tor,
                1,
                RouterProgressPhase::RouterReady,
                RouterProgressDetail::RouterAvailable,
                None,
            );
        }
        let snapshot = progress.snapshot(&tor, &i2p);
        assert_eq!(snapshot.recent_events.len(), MAX_ROUTER_PROGRESS_EVENTS);
    }

    #[test]
    fn pool_rejects_colliding_endpoints_roots_and_domains() {
        let executable = fs::canonicalize(std::env::current_exe().unwrap()).unwrap();
        let root = std::env::temp_dir().join(format!("anonssh-pool-test-{}", std::process::id()));
        let tor = (1_u32..=4)
            .map(|slot| {
                (
                    slot,
                    vec![
                        (
                            root.join(format!("tor-{slot}")),
                            format!("127.0.0.1:{}", 19_049 + slot).parse().unwrap(),
                            format!("127.0.0.1:{}", 19_149 + slot).parse().unwrap(),
                        ),
                        (
                            root.join(format!("tor-{slot}-reserve")),
                            format!("127.0.0.1:{}", 19_249 + slot).parse().unwrap(),
                            format!("127.0.0.1:{}", 19_349 + slot).parse().unwrap(),
                        ),
                    ],
                    u64::from(slot),
                )
            })
            .collect::<Vec<_>>();
        let i2p = (1_u32..=4)
            .map(|slot| {
                (
                    slot,
                    root.join(format!("i2p-{slot}")),
                    format!("127.0.0.1:{}", 7_655 + slot).parse().unwrap(),
                    100 + u64::from(slot),
                )
            })
            .collect::<Vec<_>>();
        let valid = RouterPool::new(
            executable.clone(),
            tor.clone(),
            executable.clone(),
            i2p.clone(),
        )
        .unwrap();
        assert_eq!(valid.tor_slots().len(), 4);
        assert_eq!(valid.tor_candidate_count(), 8);
        assert_eq!(valid.tor_slot(4).unwrap().candidate_count(), 2);
        assert_eq!(valid.i2p_slots().len(), 4);
        assert_eq!(valid.tor_slot(4).unwrap().failure_domain, 4);
        assert_eq!(
            valid.i2p_slot(4).unwrap().manager.state_root(),
            root.join("i2p-4")
        );
        assert!(valid.tor_slot(5).is_err());
        assert!(valid.i2p_slot(5).is_err());

        let tor_only = RouterPool::new(
            executable.clone(),
            tor.clone(),
            executable.clone(),
            Vec::new(),
        )
        .unwrap();
        assert_eq!(tor_only.tor_slots().len(), 4);
        assert!(tor_only.i2p_slots().is_empty());
        let i2p_only = RouterPool::new(
            executable.clone(),
            Vec::new(),
            executable.clone(),
            i2p.clone(),
        )
        .unwrap();
        assert!(i2p_only.tor_slots().is_empty());
        assert_eq!(i2p_only.i2p_slots().len(), 4);
        assert!(RouterPool::new(
            executable.clone(),
            Vec::new(),
            executable.clone(),
            Vec::new(),
        )
        .is_err());

        let mut colliding_roots = i2p.clone();
        colliding_roots[1].1 = colliding_roots[0].1.clone();
        assert!(RouterPool::new(
            executable.clone(),
            tor.clone(),
            executable.clone(),
            colliding_roots,
        )
        .is_err());

        let mut colliding_domains = i2p;
        colliding_domains[0].3 = tor[0].2;
        assert!(RouterPool::new(executable.clone(), tor, executable, colliding_domains,).is_err());
    }

    #[tokio::test]
    async fn pool_sampling_does_not_wait_for_tor_selection() {
        let progress = Arc::new(RouterProgressTracker::new());
        progress.register(RouterProvider::Tor, 1);
        let pool = RouterPool {
            tor: vec![Arc::new(TorPoolSlot {
                slot: 1,
                failure_domain: 1,
                candidates: Vec::new(),
                selected: Mutex::new(None),
                progress: progress.clone(),
            })],
            i2p: Vec::new(),
            progress,
        };
        let selection = pool.tor[0].selected.lock().await;
        let samples = pool.process_samples().await.unwrap();
        assert_eq!(samples.len(), 1);
        assert_eq!(samples[0].provider, RouterProvider::Tor);
        assert_eq!(samples[0].usage, None);
        drop(selection);
    }
}
