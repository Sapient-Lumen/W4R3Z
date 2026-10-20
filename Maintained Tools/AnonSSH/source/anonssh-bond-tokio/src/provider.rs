use std::collections::{BTreeMap, BTreeSet, VecDeque};
use std::error::Error;
use std::fmt;
use std::future::Future;
use std::io;
use std::net::SocketAddr;
use std::pin::Pin;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Mutex as StdMutex};
use std::time::Duration;

use anonssh_bond::{
    EndpointDescriptor, EndpointProvider, LaneConfig, LaneId, TopologyAction,
    TopologyAdvertisement, TopologyError, MAX_TOPOLOGY_DESCRIPTORS,
};
use tokio::io::{AsyncRead, AsyncWrite, AsyncWriteExt};
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::{broadcast, Mutex, Semaphore};
use tokio::task::JoinSet;
use tokio::time::timeout;

use crate::handshake::{
    authenticate_server_lane_unbound_with_incarnation, authenticate_server_lane_with_incarnation,
    fresh_session_id, AuthenticatedLane, BondSessionKey, LaneHandshakeError, LaneJoin,
    LaneJoinRegistry, PreparedClientLane, ServerIncarnation,
};
use crate::{BondRuntimeConfig, BondRuntimeError, BondSession, RuntimeLane, SessionRole};

const PROGRESS_CAPACITY: usize = 128;

/// An authenticated lane's underlying reliable byte stream.
pub trait LaneIo: AsyncRead + AsyncWrite + Send + Unpin + 'static {}

impl<T> LaneIo for T where T: AsyncRead + AsyncWrite + Send + Unpin + 'static {}

pub type BoxLaneIo = Box<dyn LaneIo>;
pub type ProviderFuture<'a, T> = Pin<Box<dyn Future<Output = io::Result<T>> + Send + 'a>>;

/// Connects one explicitly authorized endpoint. Implementations must not proxy arbitrary targets.
pub trait LaneDialProvider: Send + Sync + 'static {
    fn provider(&self) -> EndpointProvider;
    fn dial<'a>(&'a self, endpoint: &'a str) -> ProviderFuture<'a, BoxLaneIo>;

    /// Connects while making `initial_payload` the first application bytes on the transport.
    ///
    /// Providers whose connection protocol carries early data, notably I2P SAM, must override
    /// this method so the remote stream can become acceptable without a handshake deadlock.
    fn dial_with_initial_payload<'a>(
        &'a self,
        endpoint: &'a str,
        initial_payload: &'a [u8],
    ) -> ProviderFuture<'a, BoxLaneIo> {
        Box::pin(async move {
            let mut io = self.dial(endpoint).await?;
            io.write_all(initial_payload).await?;
            io.flush().await?;
            Ok(io)
        })
    }
}

/// Accepts reliable streams for one bound provider endpoint.
pub trait LaneAcceptor: Send + 'static {
    fn local_endpoint(&self) -> &str;
    fn accept<'a>(&'a mut self) -> ProviderFuture<'a, BoxLaneIo>;
}

/// Binds one explicitly authorized endpoint.
pub trait LaneListenProvider: Send + Sync + 'static {
    fn provider(&self) -> EndpointProvider;
    fn bind<'a>(&'a self, endpoint: &'a str) -> ProviderFuture<'a, Box<dyn LaneAcceptor>>;
}

#[derive(Clone, Default)]
pub struct DialProviderSet {
    providers: BTreeMap<EndpointProvider, Arc<dyn LaneDialProvider>>,
}

impl DialProviderSet {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn register<P>(&mut self, provider: P) -> Result<(), BondProviderError>
    where
        P: LaneDialProvider,
    {
        let kind = provider.provider();
        if self.providers.insert(kind, Arc::new(provider)).is_some() {
            return Err(BondProviderError::DuplicateProvider(kind));
        }
        Ok(())
    }

    fn get(
        &self,
        provider: EndpointProvider,
    ) -> Result<Arc<dyn LaneDialProvider>, BondProviderError> {
        self.providers
            .get(&provider)
            .cloned()
            .ok_or(BondProviderError::MissingDialProvider(provider))
    }
}

#[derive(Clone, Default)]
pub struct ListenProviderSet {
    providers: BTreeMap<EndpointProvider, Arc<dyn LaneListenProvider>>,
}

impl ListenProviderSet {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn register<P>(&mut self, provider: P) -> Result<(), BondProviderError>
    where
        P: LaneListenProvider,
    {
        let kind = provider.provider();
        if self.providers.insert(kind, Arc::new(provider)).is_some() {
            return Err(BondProviderError::DuplicateProvider(kind));
        }
        Ok(())
    }

    fn get(
        &self,
        provider: EndpointProvider,
    ) -> Result<Arc<dyn LaneListenProvider>, BondProviderError> {
        self.providers
            .get(&provider)
            .cloned()
            .ok_or(BondProviderError::MissingListenProvider(provider))
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ProviderLane {
    config: LaneConfig,
    provider: EndpointProvider,
    endpoint: String,
}

impl ProviderLane {
    pub fn new(
        config: LaneConfig,
        provider: EndpointProvider,
        endpoint: impl Into<String>,
    ) -> Result<Self, BondProviderError> {
        let endpoint = endpoint.into();
        EndpointDescriptor::new(
            config.id,
            config.failure_domain,
            provider,
            TopologyAction::Add,
            endpoint.clone(),
        )?;
        Ok(Self {
            config,
            provider,
            endpoint,
        })
    }

    pub const fn config(&self) -> LaneConfig {
        self.config
    }

    pub const fn provider(&self) -> EndpointProvider {
        self.provider
    }

    pub fn endpoint(&self) -> &str {
        &self.endpoint
    }

    fn descriptor(&self, action: TopologyAction) -> Result<EndpointDescriptor, TopologyError> {
        EndpointDescriptor::new(
            self.config.id,
            self.config.failure_domain,
            self.provider,
            action,
            self.endpoint.clone(),
        )
    }

    fn key(&self) -> PolicyKey {
        PolicyKey {
            lane_id: self.config.id,
            provider: self.provider,
            endpoint: self.endpoint.clone(),
        }
    }
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct PolicyKey {
    lane_id: LaneId,
    provider: EndpointProvider,
    endpoint: String,
}

/// Exact endpoint and topology-action authorization for a provider-facing bond.
#[derive(Clone, Debug)]
pub struct ProviderPolicy {
    max_lanes: usize,
    max_parallel_operations: usize,
    allowed: BTreeMap<PolicyKey, ProviderLane>,
    allowed_actions: BTreeSet<TopologyAction>,
}

impl ProviderPolicy {
    pub fn exact(
        max_lanes: usize,
        max_parallel_operations: usize,
        lanes: impl IntoIterator<Item = ProviderLane>,
        allowed_actions: impl IntoIterator<Item = TopologyAction>,
    ) -> Result<Self, BondProviderError> {
        if max_lanes == 0 || max_lanes > MAX_TOPOLOGY_DESCRIPTORS {
            return Err(BondProviderError::InvalidLaneLimit(max_lanes));
        }
        if max_parallel_operations == 0 || max_parallel_operations > max_lanes {
            return Err(BondProviderError::InvalidParallelLimit(
                max_parallel_operations,
            ));
        }
        let mut allowed = BTreeMap::new();
        for lane in lanes {
            let key = lane.key();
            if allowed.insert(key, lane).is_some() {
                return Err(BondProviderError::DuplicatePolicyEndpoint);
            }
        }
        if allowed.is_empty() || allowed.len() > max_lanes {
            return Err(BondProviderError::InvalidLaneLimit(allowed.len()));
        }
        let allowed_actions = allowed_actions.into_iter().collect::<BTreeSet<_>>();
        Ok(Self {
            max_lanes,
            max_parallel_operations,
            allowed,
            allowed_actions,
        })
    }

    pub const fn max_lanes(&self) -> usize {
        self.max_lanes
    }

    pub const fn max_parallel_operations(&self) -> usize {
        self.max_parallel_operations
    }

    pub fn authorize_lane(&self, lane: &ProviderLane) -> Result<(), BondProviderError> {
        let Some(allowed) = self.allowed.get(&lane.key()) else {
            return Err(BondProviderError::EndpointDenied {
                lane_id: lane.config.id,
                provider: lane.provider,
                endpoint: lane.endpoint.clone(),
            });
        };
        if allowed.config != lane.config {
            return Err(BondProviderError::LaneConfigurationDenied(lane.config.id));
        }
        Ok(())
    }

    pub fn authorize_action(&self, action: TopologyAction) -> Result<(), BondProviderError> {
        if !self.allowed_actions.contains(&action) {
            return Err(BondProviderError::TopologyActionDenied(action));
        }
        Ok(())
    }

    fn validate_selection(&self, lanes: &[ProviderLane]) -> Result<(), BondProviderError> {
        if lanes.is_empty() || lanes.len() > self.max_lanes {
            return Err(BondProviderError::InvalidLaneCount(lanes.len()));
        }
        let mut ids = BTreeSet::new();
        for lane in lanes {
            self.authorize_lane(lane)?;
            if !ids.insert(lane.config.id) {
                return Err(BondProviderError::DuplicateLane(lane.config.id));
            }
        }
        Ok(())
    }

    fn validate_authorized_set(&self, lanes: &[ProviderLane]) -> Result<(), BondProviderError> {
        if lanes.is_empty() || lanes.len() > self.max_lanes {
            return Err(BondProviderError::InvalidLaneCount(lanes.len()));
        }
        for lane in lanes {
            self.authorize_lane(lane)?;
        }
        Ok(())
    }

    fn resolve_descriptor(
        &self,
        descriptor: &EndpointDescriptor,
    ) -> Result<ProviderLane, BondProviderError> {
        self.authorize_action(descriptor.action)?;
        let key = PolicyKey {
            lane_id: descriptor.lane_id,
            provider: descriptor.provider,
            endpoint: descriptor.endpoint.clone(),
        };
        let lane = self
            .allowed
            .get(&key)
            .ok_or_else(|| BondProviderError::EndpointDenied {
                lane_id: descriptor.lane_id,
                provider: descriptor.provider,
                endpoint: descriptor.endpoint.clone(),
            })?;
        if lane.config.failure_domain != descriptor.failure_domain {
            return Err(BondProviderError::LaneConfigurationDenied(
                descriptor.lane_id,
            ));
        }
        Ok(lane.clone())
    }

    fn authorize_bound_endpoint(
        &self,
        requested: &ProviderLane,
        bound: &ProviderLane,
    ) -> Result<(), BondProviderError> {
        self.authorize_lane(requested)?;
        if requested.config != bound.config || requested.provider != bound.provider {
            return Err(BondProviderError::UnexpectedBoundEndpoint {
                requested: requested.endpoint.clone(),
                bound: bound.endpoint.clone(),
            });
        }
        if requested.endpoint == bound.endpoint
            || is_matching_ephemeral_loopback(&requested.endpoint, &bound.endpoint)
        {
            return Ok(());
        }
        Err(BondProviderError::UnexpectedBoundEndpoint {
            requested: requested.endpoint.clone(),
            bound: bound.endpoint.clone(),
        })
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct BondProviderConfig {
    pub runtime: BondRuntimeConfig,
    pub connect_timeout: Duration,
    pub handshake_timeout: Duration,
}

impl BondProviderConfig {
    pub fn new(
        runtime: BondRuntimeConfig,
        connect_timeout: Duration,
        handshake_timeout: Duration,
    ) -> Result<Self, BondProviderError> {
        let config = Self {
            runtime,
            connect_timeout,
            handshake_timeout,
        };
        config.validate()?;
        Ok(config)
    }

    fn validate(self) -> Result<(), BondProviderError> {
        self.runtime.validate()?;
        if !self.runtime.require_stream_open {
            return Err(BondProviderError::StreamLifecycleRequired);
        }
        if self.connect_timeout.is_zero() || self.handshake_timeout.is_zero() {
            return Err(BondProviderError::ZeroOperationTimeout);
        }
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ProviderPhase {
    Binding,
    Bound,
    Dialing,
    Accepting,
    Authenticating,
    Active,
    Adding,
    Replacing,
    Draining,
    Rejected,
    Cancelled,
    SessionActive,
    Shutdown,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ProviderProgress {
    pub sequence: u64,
    pub phase: ProviderPhase,
    pub lane_id: Option<LaneId>,
    pub provider: Option<EndpointProvider>,
    pub endpoint: Option<String>,
}

struct ProgressReporter {
    sequence: AtomicU64,
    sender: broadcast::Sender<ProviderProgress>,
    history: StdMutex<VecDeque<ProviderProgress>>,
}

impl ProgressReporter {
    fn new() -> Arc<Self> {
        let (sender, _) = broadcast::channel(PROGRESS_CAPACITY);
        Arc::new(Self {
            sequence: AtomicU64::new(0),
            sender,
            history: StdMutex::new(VecDeque::with_capacity(PROGRESS_CAPACITY)),
        })
    }

    fn subscribe(&self) -> broadcast::Receiver<ProviderProgress> {
        self.sender.subscribe()
    }

    fn snapshot(&self) -> Vec<ProviderProgress> {
        self.history
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner())
            .iter()
            .cloned()
            .collect()
    }

    fn emit(&self, phase: ProviderPhase, lane: Option<&ProviderLane>) {
        let sequence = self
            .sequence
            .fetch_update(Ordering::AcqRel, Ordering::Acquire, |current| {
                current.checked_add(1)
            })
            .map_or(u64::MAX, |previous| previous + 1);
        let event = ProviderProgress {
            sequence,
            phase,
            lane_id: lane.map(|lane| lane.config.id),
            provider: lane.map(|lane| lane.provider),
            endpoint: lane.map(|lane| lane.endpoint.clone()),
        };
        let mut history = self
            .history
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner());
        if history.len() == PROGRESS_CAPACITY {
            history.pop_front();
        }
        history.push_back(event.clone());
        drop(history);
        let _ = self.sender.send(event);
    }
}

struct ProgressGuard {
    reporter: Arc<ProgressReporter>,
    lane: Option<ProviderLane>,
    completed: bool,
}

impl ProgressGuard {
    fn new(reporter: Arc<ProgressReporter>, lane: Option<ProviderLane>) -> Self {
        Self {
            reporter,
            lane,
            completed: false,
        }
    }

    fn finish(&mut self, phase: ProviderPhase) {
        self.reporter.emit(phase, self.lane.as_ref());
        self.completed = true;
    }
}

impl Drop for ProgressGuard {
    fn drop(&mut self) {
        if !self.completed {
            self.reporter
                .emit(ProviderPhase::Cancelled, self.lane.as_ref());
        }
    }
}

/// Safe built-in transport for tests and explicitly local integrations.
#[derive(Clone, Copy, Debug, Default)]
pub struct LoopbackTcpProvider;

impl LaneDialProvider for LoopbackTcpProvider {
    fn provider(&self) -> EndpointProvider {
        EndpointProvider::Tcp
    }

    fn dial<'a>(&'a self, endpoint: &'a str) -> ProviderFuture<'a, BoxLaneIo> {
        Box::pin(async move {
            let address = parse_loopback_tcp_endpoint(endpoint, false)?;
            let stream = TcpStream::connect(address).await?;
            stream.set_nodelay(true)?;
            Ok(Box::new(stream) as BoxLaneIo)
        })
    }
}

impl LaneListenProvider for LoopbackTcpProvider {
    fn provider(&self) -> EndpointProvider {
        EndpointProvider::Tcp
    }

    fn bind<'a>(&'a self, endpoint: &'a str) -> ProviderFuture<'a, Box<dyn LaneAcceptor>> {
        Box::pin(async move {
            let address = parse_loopback_tcp_endpoint(endpoint, true)?;
            let listener = TcpListener::bind(address).await?;
            let endpoint = format!("tcp://{}", listener.local_addr()?);
            Ok(Box::new(TcpLaneAcceptor { listener, endpoint }) as Box<dyn LaneAcceptor>)
        })
    }
}

struct TcpLaneAcceptor {
    listener: TcpListener,
    endpoint: String,
}

impl LaneAcceptor for TcpLaneAcceptor {
    fn local_endpoint(&self) -> &str {
        &self.endpoint
    }

    fn accept<'a>(&'a mut self) -> ProviderFuture<'a, BoxLaneIo> {
        Box::pin(async move {
            let (stream, _) = self.listener.accept().await?;
            stream.set_nodelay(true)?;
            Ok(Box::new(stream) as BoxLaneIo)
        })
    }
}

pub struct BondDialer {
    key: Arc<BondSessionKey>,
    config: BondProviderConfig,
    policy: ProviderPolicy,
    providers: DialProviderSet,
    progress: Arc<ProgressReporter>,
}

impl BondDialer {
    pub fn new(
        key: BondSessionKey,
        config: BondProviderConfig,
        policy: ProviderPolicy,
        providers: DialProviderSet,
    ) -> Result<Self, BondProviderError> {
        config.validate()?;
        Ok(Self {
            key: Arc::new(key),
            config,
            policy,
            providers,
            progress: ProgressReporter::new(),
        })
    }

    pub fn subscribe_progress(&self) -> broadcast::Receiver<ProviderProgress> {
        self.progress.subscribe()
    }

    pub fn progress_snapshot(&self) -> Vec<ProviderProgress> {
        self.progress.snapshot()
    }

    pub async fn connect(&self, lanes: &[ProviderLane]) -> Result<BondSession, BondProviderError> {
        self.policy.validate_selection(lanes)?;
        let mut guard = ProgressGuard::new(self.progress.clone(), None);
        let session_id = fresh_session_id()?;
        let result = self.dial_lanes(session_id, lanes).await;
        let authenticated = match result {
            Ok(authenticated) => authenticated,
            Err(error) => {
                guard.finish(ProviderPhase::Rejected);
                return Err(error);
            }
        };
        let formed = (|| {
            let mut registry = LaneJoinRegistry::new(
                session_id,
                lanes
                    .iter()
                    .map(|lane| (lane.config.id, lane.config.failure_domain)),
            )?;
            for (_, lane) in &authenticated {
                registry.register(lane)?;
            }
            let mut runtime_lanes = authenticated
                .into_iter()
                .map(|(lane, authenticated)| {
                    RuntimeLane::from_authenticated(lane.config, authenticated)
                })
                .collect::<Vec<_>>();
            runtime_lanes.sort_by_key(|lane| lane.config.id);
            let mut runtime = self.config.runtime;
            runtime.session_id = session_id;
            Ok(BondSession::spawn(
                runtime,
                runtime_lanes,
                SessionRole::Dialer,
            )?)
        })();
        match formed {
            Ok(session) => {
                guard.finish(ProviderPhase::SessionActive);
                Ok(session)
            }
            Err(error) => {
                guard.finish(ProviderPhase::Rejected);
                Err(error)
            }
        }
    }

    pub async fn apply_next_topology(
        &self,
        session: &BondSession,
    ) -> Result<AppliedTopology, BondProviderError> {
        let advertisement = timeout(self.config.connect_timeout, session.accept_topology())
            .await
            .map_err(|_| BondProviderError::OperationTimedOut("topology advertisement"))??;
        if advertisement.descriptors.len() != 1 {
            return Err(BondProviderError::InvalidTopologyDescriptorCount(
                advertisement.descriptors.len(),
            ));
        }
        let descriptor = &advertisement.descriptors[0];
        let lane = self.policy.resolve_descriptor(descriptor)?;
        let phase = phase_for_action(descriptor.action);
        self.progress.emit(phase, Some(&lane));
        if descriptor.action == TopologyAction::Drain {
            session.fail_lane(lane.config.id).await?;
            return Ok(AppliedTopology {
                generation: advertisement.generation,
                action: descriptor.action,
                lane,
            });
        }
        let authenticated = self.dial_lane(session.session_id(), lane.clone()).await?;
        if descriptor.action == TopologyAction::Add {
            session.authorize_lane(lane.config).await?;
        } else {
            session.fail_lane(lane.config.id).await?;
        }
        session
            .add_lane(RuntimeLane::from_authenticated(lane.config, authenticated))
            .await?;
        Ok(AppliedTopology {
            generation: advertisement.generation,
            action: descriptor.action,
            lane,
        })
    }

    async fn dial_lanes(
        &self,
        session_id: u64,
        lanes: &[ProviderLane],
    ) -> Result<Vec<(ProviderLane, AuthenticatedLane<BoxLaneIo>)>, BondProviderError> {
        let semaphore = Arc::new(Semaphore::new(self.policy.max_parallel_operations));
        let mut tasks = JoinSet::new();
        for lane in lanes.iter().cloned() {
            let permit_pool = semaphore.clone();
            let provider = self.providers.get(lane.provider)?;
            let key = self.key.clone();
            let config = self.config;
            let progress = self.progress.clone();
            tasks.spawn(async move {
                let _permit = permit_pool
                    .acquire_owned()
                    .await
                    .map_err(|_| BondProviderError::OperationCancelled)?;
                dial_authenticated(provider, key, config, progress, session_id, lane).await
            });
        }
        let mut authenticated = Vec::with_capacity(lanes.len());
        while let Some(result) = tasks.join_next().await {
            authenticated.push(result.map_err(join_error)??);
        }
        Ok(authenticated)
    }

    async fn dial_lane(
        &self,
        session_id: u64,
        lane: ProviderLane,
    ) -> Result<AuthenticatedLane<BoxLaneIo>, BondProviderError> {
        self.policy.authorize_lane(&lane)?;
        let provider = self.providers.get(lane.provider)?;
        let (_, authenticated) = dial_authenticated(
            provider,
            self.key.clone(),
            self.config,
            self.progress.clone(),
            session_id,
            lane,
        )
        .await?;
        Ok(authenticated)
    }
}

struct BoundLane {
    lane: ProviderLane,
    acceptor: Arc<Mutex<Box<dyn LaneAcceptor>>>,
}

pub struct BondListener {
    key: Arc<BondSessionKey>,
    config: BondProviderConfig,
    policy: ProviderPolicy,
    bound: BTreeMap<PolicyKey, BoundLane>,
    progress: Arc<ProgressReporter>,
    admission: Mutex<()>,
    incarnation: ServerIncarnation,
}

impl BondListener {
    pub async fn bind(
        key: BondSessionKey,
        config: BondProviderConfig,
        policy: ProviderPolicy,
        providers: ListenProviderSet,
        lanes: &[ProviderLane],
    ) -> Result<Self, BondProviderError> {
        config.validate()?;
        policy.validate_authorized_set(lanes)?;
        let progress = ProgressReporter::new();
        let semaphore = Arc::new(Semaphore::new(policy.max_parallel_operations));
        let mut tasks = JoinSet::new();
        for requested in lanes.iter().cloned() {
            let provider = providers.get(requested.provider)?;
            let permit_pool = semaphore.clone();
            let progress = progress.clone();
            tasks.spawn(async move {
                let _permit = permit_pool
                    .acquire_owned()
                    .await
                    .map_err(|_| BondProviderError::OperationCancelled)?;
                bind_lane(provider, config, progress, requested).await
            });
        }
        let mut bound = BTreeMap::new();
        while let Some(result) = tasks.join_next().await {
            let (requested, lane, acceptor) = result.map_err(join_error)??;
            policy.authorize_bound_endpoint(&requested, &lane)?;
            if bound
                .insert(
                    lane.key(),
                    BoundLane {
                        lane,
                        acceptor: Arc::new(Mutex::new(acceptor)),
                    },
                )
                .is_some()
            {
                return Err(BondProviderError::DuplicateBoundEndpoint);
            }
        }
        Ok(Self {
            key: Arc::new(key),
            config,
            policy,
            bound,
            progress,
            admission: Mutex::new(()),
            incarnation: ServerIncarnation::fresh()?,
        })
    }

    pub fn subscribe_progress(&self) -> broadcast::Receiver<ProviderProgress> {
        self.progress.subscribe()
    }

    pub fn progress_snapshot(&self) -> Vec<ProviderProgress> {
        self.progress.snapshot()
    }

    pub fn bound_lanes(&self) -> Vec<ProviderLane> {
        self.bound
            .values()
            .map(|bound| bound.lane.clone())
            .collect()
    }

    pub const fn server_incarnation(&self) -> ServerIncarnation {
        self.incarnation
    }

    pub async fn accept(&self, lanes: &[ProviderLane]) -> Result<BondSession, BondProviderError> {
        validate_unique_selection(lanes, self.policy.max_lanes)?;
        let _admission = self.admission.lock().await;
        let mut guard = ProgressGuard::new(self.progress.clone(), None);
        let accepted = match self.accept_lanes_unbound(lanes).await {
            Ok(accepted) => accepted,
            Err(error) => {
                guard.finish(ProviderPhase::Rejected);
                return Err(error);
            }
        };
        let formed = (|| {
            let session_id = accepted
                .first()
                .map(|(_, lane)| lane.join.session_id)
                .ok_or(BondProviderError::InvalidLaneCount(0))?;
            let mut registry = LaneJoinRegistry::new(
                session_id,
                lanes
                    .iter()
                    .map(|lane| (lane.config.id, lane.config.failure_domain)),
            )?;
            for (_, lane) in &accepted {
                registry.register(lane)?;
            }
            let mut runtime_lanes = accepted
                .into_iter()
                .map(|(lane, authenticated)| {
                    RuntimeLane::from_authenticated(lane.config, authenticated)
                })
                .collect::<Vec<_>>();
            runtime_lanes.sort_by_key(|lane| lane.config.id);
            let mut runtime = self.config.runtime;
            runtime.session_id = session_id;
            Ok(BondSession::spawn(
                runtime,
                runtime_lanes,
                SessionRole::Listener,
            )?)
        })();
        match formed {
            Ok(session) => {
                guard.finish(ProviderPhase::SessionActive);
                Ok(session)
            }
            Err(error) => {
                guard.finish(ProviderPhase::Rejected);
                Err(error)
            }
        }
    }

    pub async fn advertise_and_accept_lane(
        &self,
        session: &BondSession,
        lane: &ProviderLane,
        action: TopologyAction,
        generation: u64,
    ) -> Result<AppliedTopology, BondProviderError> {
        self.policy.authorize_action(action)?;
        let _admission = self.admission.lock().await;
        let bound = self.bound_lane(lane)?;
        let advertisement =
            TopologyAdvertisement::new(generation, vec![bound.lane.descriptor(action)?])?;
        timeout(
            self.config.connect_timeout,
            session.advertise_topology(advertisement),
        )
        .await
        .map_err(|_| BondProviderError::OperationTimedOut("topology advertisement"))??;
        self.progress.emit(phase_for_action(action), Some(lane));
        if action == TopologyAction::Drain {
            session.fail_lane(lane.config.id).await?;
            return Ok(AppliedTopology {
                generation,
                action,
                lane: lane.clone(),
            });
        }
        let authenticated = self.accept_lane_bound(session.session_id(), bound).await?;
        if action == TopologyAction::Add {
            session.authorize_lane(lane.config).await?;
        } else {
            session.fail_lane(lane.config.id).await?;
        }
        session
            .add_lane(RuntimeLane::from_authenticated(lane.config, authenticated))
            .await?;
        Ok(AppliedTopology {
            generation,
            action,
            lane: lane.clone(),
        })
    }

    pub async fn shutdown(self) {
        self.progress.emit(ProviderPhase::Shutdown, None);
    }

    fn bound_lane(&self, lane: &ProviderLane) -> Result<&BoundLane, BondProviderError> {
        self.bound
            .get(&lane.key())
            .filter(|bound| bound.lane.config == lane.config)
            .ok_or_else(|| BondProviderError::EndpointNotBound {
                lane_id: lane.config.id,
                provider: lane.provider,
                endpoint: lane.endpoint.clone(),
            })
    }

    async fn accept_lanes_unbound(
        &self,
        lanes: &[ProviderLane],
    ) -> Result<Vec<(ProviderLane, AuthenticatedLane<BoxLaneIo>)>, BondProviderError> {
        let semaphore = Arc::new(Semaphore::new(self.policy.max_parallel_operations));
        let mut tasks = JoinSet::new();
        for lane in lanes {
            let bound = self.bound_lane(lane)?;
            let lane = bound.lane.clone();
            let acceptor = bound.acceptor.clone();
            let permit_pool = semaphore.clone();
            let key = self.key.clone();
            let config = self.config;
            let progress = self.progress.clone();
            let incarnation = self.incarnation;
            tasks.spawn(async move {
                let _permit = permit_pool
                    .acquire_owned()
                    .await
                    .map_err(|_| BondProviderError::OperationCancelled)?;
                accept_authenticated_unbound(acceptor, key, config, progress, lane, incarnation)
                    .await
            });
        }
        let mut accepted = Vec::with_capacity(lanes.len());
        while let Some(result) = tasks.join_next().await {
            accepted.push(result.map_err(join_error)??);
        }
        Ok(accepted)
    }

    async fn accept_lane_bound(
        &self,
        session_id: u64,
        bound: &BoundLane,
    ) -> Result<AuthenticatedLane<BoxLaneIo>, BondProviderError> {
        let lane = bound.lane.clone();
        let mut guard = ProgressGuard::new(self.progress.clone(), Some(lane.clone()));
        self.progress.emit(ProviderPhase::Accepting, Some(&lane));
        let result = async {
            let io = {
                let mut acceptor = bound.acceptor.lock().await;
                timeout(self.config.connect_timeout, acceptor.accept())
                    .await
                    .map_err(|_| BondProviderError::OperationTimedOut("provider accept"))?
                    .map_err(|error| provider_io_error("accept", &lane, error))?
            };
            self.progress
                .emit(ProviderPhase::Authenticating, Some(&lane));
            let join = LaneJoin::new(session_id, lane.config.id, lane.config.failure_domain)?;
            authenticate_server_lane_with_incarnation(
                io,
                &self.key,
                join,
                self.incarnation,
                self.config.handshake_timeout,
            )
            .await
            .map_err(|error| BondProviderError::Handshake {
                lane_id: lane.config.id,
                error,
            })
        }
        .await;
        match result {
            Ok(authenticated) => {
                guard.finish(ProviderPhase::Active);
                Ok(authenticated)
            }
            Err(error) => {
                guard.finish(ProviderPhase::Rejected);
                Err(error)
            }
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct AppliedTopology {
    pub generation: u64,
    pub action: TopologyAction,
    pub lane: ProviderLane,
}

async fn bind_lane(
    provider: Arc<dyn LaneListenProvider>,
    config: BondProviderConfig,
    progress: Arc<ProgressReporter>,
    requested: ProviderLane,
) -> Result<(ProviderLane, ProviderLane, Box<dyn LaneAcceptor>), BondProviderError> {
    let mut guard = ProgressGuard::new(progress.clone(), Some(requested.clone()));
    progress.emit(ProviderPhase::Binding, Some(&requested));
    let result = async {
        let acceptor = timeout(config.connect_timeout, provider.bind(&requested.endpoint))
            .await
            .map_err(|_| BondProviderError::OperationTimedOut("provider bind"))?
            .map_err(|error| provider_io_error("bind", &requested, error))?;
        let bound = ProviderLane::new(
            requested.config,
            requested.provider,
            acceptor.local_endpoint(),
        )?;
        Ok((requested, bound, acceptor))
    }
    .await;
    match result {
        Ok(result) => {
            guard.finish(ProviderPhase::Bound);
            Ok(result)
        }
        Err(error) => {
            guard.finish(ProviderPhase::Rejected);
            Err(error)
        }
    }
}

async fn dial_authenticated(
    provider: Arc<dyn LaneDialProvider>,
    key: Arc<BondSessionKey>,
    config: BondProviderConfig,
    progress: Arc<ProgressReporter>,
    session_id: u64,
    lane: ProviderLane,
) -> Result<(ProviderLane, AuthenticatedLane<BoxLaneIo>), BondProviderError> {
    let mut guard = ProgressGuard::new(progress.clone(), Some(lane.clone()));
    progress.emit(ProviderPhase::Dialing, Some(&lane));
    let result = async {
        let join = LaneJoin::new(session_id, lane.config.id, lane.config.failure_domain)?;
        let prepared =
            PreparedClientLane::new(&key, join).map_err(|error| BondProviderError::Handshake {
                lane_id: lane.config.id,
                error,
            })?;
        let io = timeout(
            config.connect_timeout,
            provider.dial_with_initial_payload(&lane.endpoint, prepared.initial_payload()),
        )
        .await
        .map_err(|_| BondProviderError::OperationTimedOut("provider dial"))?
        .map_err(|error| provider_io_error("dial", &lane, error))?;
        progress.emit(ProviderPhase::Authenticating, Some(&lane));
        let authenticated = prepared
            .finish(io, &key, config.handshake_timeout)
            .await
            .map_err(|error| BondProviderError::Handshake {
                lane_id: lane.config.id,
                error,
            })?;
        Ok((lane, authenticated))
    }
    .await;
    match result {
        Ok(result) => {
            guard.finish(ProviderPhase::Active);
            Ok(result)
        }
        Err(error) => {
            guard.finish(ProviderPhase::Rejected);
            Err(error)
        }
    }
}

async fn accept_authenticated_unbound(
    acceptor: Arc<Mutex<Box<dyn LaneAcceptor>>>,
    key: Arc<BondSessionKey>,
    config: BondProviderConfig,
    progress: Arc<ProgressReporter>,
    lane: ProviderLane,
    incarnation: ServerIncarnation,
) -> Result<(ProviderLane, AuthenticatedLane<BoxLaneIo>), BondProviderError> {
    let mut guard = ProgressGuard::new(progress.clone(), Some(lane.clone()));
    progress.emit(ProviderPhase::Accepting, Some(&lane));
    let result = async {
        let io = {
            let mut acceptor = acceptor.lock().await;
            timeout(config.connect_timeout, acceptor.accept())
                .await
                .map_err(|_| BondProviderError::OperationTimedOut("provider accept"))?
                .map_err(|error| provider_io_error("accept", &lane, error))?
        };
        progress.emit(ProviderPhase::Authenticating, Some(&lane));
        let authenticated = authenticate_server_lane_unbound_with_incarnation(
            io,
            &key,
            lane.config.id,
            lane.config.failure_domain,
            incarnation,
            config.handshake_timeout,
        )
        .await
        .map_err(|error| BondProviderError::Handshake {
            lane_id: lane.config.id,
            error,
        })?;
        Ok((lane, authenticated))
    }
    .await;
    match result {
        Ok(result) => {
            guard.finish(ProviderPhase::Active);
            Ok(result)
        }
        Err(error) => {
            guard.finish(ProviderPhase::Rejected);
            Err(error)
        }
    }
}

fn validate_unique_selection(
    lanes: &[ProviderLane],
    max_lanes: usize,
) -> Result<(), BondProviderError> {
    if lanes.is_empty() || lanes.len() > max_lanes {
        return Err(BondProviderError::InvalidLaneCount(lanes.len()));
    }
    let mut ids = BTreeSet::new();
    for lane in lanes {
        if !ids.insert(lane.config.id) {
            return Err(BondProviderError::DuplicateLane(lane.config.id));
        }
    }
    Ok(())
}

fn phase_for_action(action: TopologyAction) -> ProviderPhase {
    match action {
        TopologyAction::Add => ProviderPhase::Adding,
        TopologyAction::Replace => ProviderPhase::Replacing,
        TopologyAction::Drain => ProviderPhase::Draining,
    }
}

fn parse_loopback_tcp_endpoint(endpoint: &str, allow_zero: bool) -> io::Result<SocketAddr> {
    let address = endpoint
        .strip_prefix("tcp://")
        .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, "expected tcp:// endpoint"))?
        .parse::<SocketAddr>()
        .map_err(|_| io::Error::new(io::ErrorKind::InvalidInput, "invalid TCP socket address"))?;
    if !address.ip().is_loopback() || (!allow_zero && address.port() == 0) {
        return Err(io::Error::new(
            io::ErrorKind::PermissionDenied,
            "loopback TCP provider denies this address",
        ));
    }
    Ok(address)
}

fn is_matching_ephemeral_loopback(requested: &str, bound: &str) -> bool {
    let Ok(requested) = parse_loopback_tcp_endpoint(requested, true) else {
        return false;
    };
    let Ok(bound) = parse_loopback_tcp_endpoint(bound, false) else {
        return false;
    };
    requested.port() == 0 && requested.ip() == bound.ip()
}

fn provider_io_error(
    operation: &'static str,
    lane: &ProviderLane,
    error: io::Error,
) -> BondProviderError {
    BondProviderError::ProviderIo {
        operation,
        lane_id: lane.config.id,
        provider: lane.provider,
        endpoint: lane.endpoint.clone(),
        error,
    }
}

fn join_error(error: tokio::task::JoinError) -> BondProviderError {
    BondProviderError::TaskJoin(error.to_string())
}

#[derive(Debug)]
pub enum BondProviderError {
    InvalidLaneLimit(usize),
    InvalidParallelLimit(usize),
    InvalidLaneCount(usize),
    InvalidTopologyDescriptorCount(usize),
    DuplicateLane(LaneId),
    DuplicateProvider(EndpointProvider),
    MissingDialProvider(EndpointProvider),
    MissingListenProvider(EndpointProvider),
    DuplicatePolicyEndpoint,
    DuplicateBoundEndpoint,
    TopologyActionDenied(TopologyAction),
    EndpointDenied {
        lane_id: LaneId,
        provider: EndpointProvider,
        endpoint: String,
    },
    EndpointNotBound {
        lane_id: LaneId,
        provider: EndpointProvider,
        endpoint: String,
    },
    LaneConfigurationDenied(LaneId),
    UnexpectedBoundEndpoint {
        requested: String,
        bound: String,
    },
    StreamLifecycleRequired,
    ZeroOperationTimeout,
    OperationTimedOut(&'static str),
    OperationCancelled,
    ProviderIo {
        operation: &'static str,
        lane_id: LaneId,
        provider: EndpointProvider,
        endpoint: String,
        error: io::Error,
    },
    Handshake {
        lane_id: LaneId,
        error: LaneHandshakeError,
    },
    HandshakeSetup(LaneHandshakeError),
    TaskJoin(String),
    Topology(TopologyError),
    Runtime(BondRuntimeError),
}

impl From<LaneHandshakeError> for BondProviderError {
    fn from(error: LaneHandshakeError) -> Self {
        Self::HandshakeSetup(error)
    }
}

impl From<TopologyError> for BondProviderError {
    fn from(error: TopologyError) -> Self {
        Self::Topology(error)
    }
}

impl From<BondRuntimeError> for BondProviderError {
    fn from(error: BondRuntimeError) -> Self {
        Self::Runtime(error)
    }
}

impl fmt::Display for BondProviderError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidLaneLimit(limit) => {
                write!(formatter, "invalid provider lane limit {limit}")
            }
            Self::InvalidParallelLimit(limit) => {
                write!(
                    formatter,
                    "invalid provider parallel-operation limit {limit}"
                )
            }
            Self::InvalidLaneCount(count) => {
                write!(formatter, "invalid provider lane count {count}")
            }
            Self::InvalidTopologyDescriptorCount(count) => {
                write!(
                    formatter,
                    "expected one topology descriptor, received {count}"
                )
            }
            Self::DuplicateLane(id) => write!(formatter, "duplicate provider lane {}", id.get()),
            Self::DuplicateProvider(provider) => {
                write!(formatter, "duplicate {provider:?} provider registration")
            }
            Self::MissingDialProvider(provider) => {
                write!(formatter, "no dial provider registered for {provider:?}")
            }
            Self::MissingListenProvider(provider) => {
                write!(formatter, "no listen provider registered for {provider:?}")
            }
            Self::DuplicatePolicyEndpoint => {
                write!(formatter, "duplicate provider policy endpoint")
            }
            Self::DuplicateBoundEndpoint => write!(formatter, "duplicate bound provider endpoint"),
            Self::TopologyActionDenied(action) => {
                write!(formatter, "topology action {action:?} is denied")
            }
            Self::EndpointDenied {
                lane_id,
                provider,
                endpoint,
            } => write!(
                formatter,
                "provider endpoint denied for lane {} ({provider:?} {endpoint})",
                lane_id.get()
            ),
            Self::EndpointNotBound {
                lane_id,
                provider,
                endpoint,
            } => write!(
                formatter,
                "provider endpoint is not bound for lane {} ({provider:?} {endpoint})",
                lane_id.get()
            ),
            Self::LaneConfigurationDenied(id) => {
                write!(
                    formatter,
                    "provider lane {} configuration is denied",
                    id.get()
                )
            }
            Self::UnexpectedBoundEndpoint { requested, bound } => write!(
                formatter,
                "provider bound unexpected endpoint {bound} for request {requested}"
            ),
            Self::StreamLifecycleRequired => {
                write!(formatter, "provider sessions require stream lifecycle")
            }
            Self::ZeroOperationTimeout => {
                write!(formatter, "provider operation timeouts must be non-zero")
            }
            Self::OperationTimedOut(operation) => write!(formatter, "{operation} timed out"),
            Self::OperationCancelled => write!(formatter, "provider operation was cancelled"),
            Self::ProviderIo {
                operation,
                lane_id,
                provider,
                endpoint,
                error,
            } => write!(
                formatter,
                "provider {operation} failed for lane {} ({provider:?} {endpoint}): {error}",
                lane_id.get()
            ),
            Self::Handshake { lane_id, error } => {
                write!(
                    formatter,
                    "lane {} authentication failed: {error}",
                    lane_id.get()
                )
            }
            Self::HandshakeSetup(error) => {
                write!(formatter, "bond authentication setup failed: {error}")
            }
            Self::TaskJoin(error) => write!(formatter, "provider task failed: {error}"),
            Self::Topology(error) => error.fmt(formatter),
            Self::Runtime(error) => error.fmt(formatter),
        }
    }
}

impl Error for BondProviderError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::ProviderIo { error, .. } => Some(error),
            Self::Handshake { error, .. } => Some(error),
            Self::HandshakeSetup(error) => Some(error),
            Self::Topology(error) => Some(error),
            Self::Runtime(error) => Some(error),
            _ => None,
        }
    }
}
