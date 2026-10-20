use std::future::pending;
use std::io;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::time::Duration;

use anonssh_bond::{
    EndpointProvider, FailureDomain, LaneConfig, LaneId, SchedulerConfig, SenderConfig,
    TopologyAction, TrafficClass,
};
use anonssh_bond_tokio::{
    BondDialer, BondListener, BondProviderConfig, BondProviderError, BondRuntimeConfig,
    BondSession, BondSessionKey, BoxLaneIo, DialProviderSet, LaneDialProvider, ListenProviderSet,
    LoopbackTcpProvider, ProviderFuture, ProviderLane, ProviderPhase, ProviderPolicy,
};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;

const TEST_TIMEOUT: Duration = Duration::from_secs(10);

#[tokio::test]
async fn public_provider_api_forms_streams_adds_replaces_and_shuts_down() {
    tokio::time::timeout(TEST_TIMEOUT, provider_lifecycle())
        .await
        .expect("provider lifecycle timed out");
}

async fn provider_lifecycle() {
    let requested = vec![
        provider_lane(1, 11, 8, "tcp://127.0.0.1:0"),
        provider_lane(2, 22, 20, "tcp://127.0.0.1:0"),
        provider_lane(3, 33, 40, "tcp://127.0.0.1:0"),
    ];
    let actions = [TopologyAction::Add, TopologyAction::Replace];
    let listener_policy = ProviderPolicy::exact(3, 2, requested.clone(), actions).unwrap();
    let mut listen_providers = ListenProviderSet::new();
    listen_providers.register(LoopbackTcpProvider).unwrap();
    let listener = BondListener::bind(
        BondSessionKey::new([0x61; 32]),
        provider_config(),
        listener_policy,
        listen_providers,
        &requested,
    )
    .await
    .unwrap();
    assert_ne!(listener.server_incarnation().get(), 0);

    let bound = listener.bound_lanes();
    assert_eq!(bound.len(), 3);
    assert_eq!(
        listener
            .progress_snapshot()
            .iter()
            .filter(|event| event.phase == ProviderPhase::Bound)
            .count(),
        3
    );
    assert!(bound.iter().all(|lane| !lane.endpoint().ends_with(":0")));
    let initial = bound
        .iter()
        .filter(|lane| lane.config().id.get() <= 2)
        .cloned()
        .collect::<Vec<_>>();
    let dynamic = bound
        .iter()
        .find(|lane| lane.config().id.get() == 3)
        .unwrap()
        .clone();

    let dial_policy = ProviderPolicy::exact(3, 2, bound.clone(), actions).unwrap();
    let initial_payloads = Arc::new(AtomicUsize::new(0));
    let mut dial_providers = DialProviderSet::new();
    dial_providers
        .register(InitialPayloadTcpProvider {
            observed: initial_payloads.clone(),
        })
        .unwrap();
    let dialer = BondDialer::new(
        BondSessionKey::new([0x61; 32]),
        provider_config(),
        dial_policy,
        dial_providers,
    )
    .unwrap();
    let mut dial_progress = dialer.subscribe_progress();
    let mut listen_progress = listener.subscribe_progress();

    let (client, server) = tokio::join!(dialer.connect(&initial), listener.accept(&initial));
    let client = client.unwrap();
    let server = server.unwrap();
    assert_eq!(client.session_id(), server.session_id());
    assert_eq!(
        client.server_incarnation(),
        Some(listener.server_incarnation())
    );
    assert_eq!(
        server.server_incarnation(),
        Some(listener.server_incarnation())
    );
    assert_eq!(initial_payloads.load(Ordering::Acquire), 2);

    exchange(
        &client,
        &server,
        TrafficClass::Interactive,
        b"latency-sensitive provider stream",
    )
    .await;
    exchange(
        &client,
        &server,
        TrafficClass::Bulk,
        &vec![0xA5; 256 * 1024],
    )
    .await;

    let (server_added, client_added) = tokio::join!(
        listener.advertise_and_accept_lane(&server, &dynamic, TopologyAction::Add, 1,),
        dialer.apply_next_topology(&client),
    );
    assert_eq!(server_added.unwrap().action, TopologyAction::Add);
    assert_eq!(client_added.unwrap().lane, dynamic);
    assert_eq!(initial_payloads.load(Ordering::Acquire), 3);

    let (server_replaced, client_replaced) = tokio::join!(
        listener.advertise_and_accept_lane(&server, &dynamic, TopologyAction::Replace, 2,),
        dialer.apply_next_topology(&client),
    );
    assert_eq!(server_replaced.unwrap().action, TopologyAction::Replace);
    assert_eq!(client_replaced.unwrap().generation, 2);
    assert_eq!(initial_payloads.load(Ordering::Acquire), 4);

    exchange(
        &client,
        &server,
        TrafficClass::Bulk,
        &vec![0x3C; 512 * 1024],
    )
    .await;
    assert!(client
        .statistics()
        .await
        .unwrap()
        .lanes
        .iter()
        .find(|lane| lane.id == dynamic.config().id)
        .is_some_and(|lane| lane.active));

    assert!(collect_phases(&mut dial_progress).contains(&ProviderPhase::SessionActive));
    let listener_phases = collect_phases(&mut listen_progress);
    assert!(listener_phases.contains(&ProviderPhase::Accepting));
    assert!(listener_phases.contains(&ProviderPhase::Replacing));

    let (client_result, server_result) = tokio::join!(client.shutdown(), server.shutdown());
    client_result.unwrap();
    server_result.unwrap();
    listener.shutdown().await;
}

#[tokio::test]
async fn provider_policy_is_exact_and_loopback_tcp_is_fail_closed() {
    let allowed = provider_lane(1, 11, 5, "tcp://127.0.0.1:12001");
    let denied = provider_lane(1, 11, 5, "tcp://127.0.0.1:12002");
    let policy = ProviderPolicy::exact(1, 1, [allowed.clone()], [TopologyAction::Add]).unwrap();
    assert!(matches!(
        policy.authorize_lane(&denied),
        Err(BondProviderError::EndpointDenied { .. })
    ));
    assert!(matches!(
        policy.authorize_action(TopologyAction::Replace),
        Err(BondProviderError::TopologyActionDenied(
            TopologyAction::Replace
        ))
    ));
    let static_policy = ProviderPolicy::exact(1, 1, [allowed], []).unwrap();
    assert!(matches!(
        static_policy.authorize_action(TopologyAction::Add),
        Err(BondProviderError::TopologyActionDenied(TopologyAction::Add))
    ));

    let error = match LoopbackTcpProvider.dial("tcp://192.0.2.1:22").await {
        Ok(_) => panic!("loopback provider accepted a non-loopback endpoint"),
        Err(error) => error,
    };
    assert_eq!(error.kind(), io::ErrorKind::PermissionDenied);
}

#[tokio::test]
async fn custom_provider_cancellation_releases_bounded_operations() {
    let state = Arc::new(ProviderProbe::default());
    let provider = PendingProvider {
        state: state.clone(),
    };
    let lanes = (1..=4)
        .map(|id| {
            provider_lane(
                id,
                u64::from(id),
                10,
                &format!("tcp://127.0.0.1:{}", 13_000 + id),
            )
        })
        .collect::<Vec<_>>();
    let policy = ProviderPolicy::exact(4, 2, lanes.clone(), [TopologyAction::Add]).unwrap();
    let mut providers = DialProviderSet::new();
    providers.register(provider).unwrap();
    let dialer = BondDialer::new(
        BondSessionKey::new([0x42; 32]),
        provider_config(),
        policy,
        providers,
    )
    .unwrap();
    let mut progress = dialer.subscribe_progress();

    assert!(
        tokio::time::timeout(Duration::from_millis(100), dialer.connect(&lanes))
            .await
            .is_err()
    );
    for _ in 0..100 {
        if state.active.load(Ordering::Acquire) == 0 {
            break;
        }
        tokio::task::yield_now().await;
    }
    assert_eq!(state.active.load(Ordering::Acquire), 0);
    assert_eq!(state.peak.load(Ordering::Acquire), 2);
    assert_eq!(state.started.load(Ordering::Acquire), 2);
    assert_eq!(state.cancelled.load(Ordering::Acquire), 2);
    assert!(collect_phases(&mut progress).contains(&ProviderPhase::Cancelled));
}

async fn exchange(client: &BondSession, server: &BondSession, class: TrafficClass, payload: &[u8]) {
    let mut outbound = client.open_stream(class).await.unwrap();
    let mut inbound = server.accept_stream().await.unwrap();
    let expected = payload.to_vec();
    let send = outbound.write_all(payload);
    let mut received = vec![0; payload.len()];
    let receive = inbound.read_exact(&mut received);
    let (sent, read) = tokio::join!(send, receive);
    sent.unwrap();
    read.unwrap();
    assert_eq!(received, expected);

    let response = format!("received:{}", payload.len()).into_bytes();
    let mut echoed = vec![0; response.len()];
    let (sent, read) = tokio::join!(
        inbound.write_all(&response),
        outbound.read_exact(&mut echoed)
    );
    sent.unwrap();
    read.unwrap();
    assert_eq!(echoed, response);
    let (outbound_closed, inbound_closed) = tokio::join!(outbound.shutdown(), inbound.shutdown());
    outbound_closed.unwrap();
    inbound_closed.unwrap();
}

fn provider_config() -> BondProviderConfig {
    BondProviderConfig::new(
        BondRuntimeConfig {
            session_id: 1,
            scheduler: SchedulerConfig::default(),
            sender: SenderConfig {
                max_chunk_payload: 8 * 1024,
                bulk_chunk: anonssh_bond::BulkChunkConfig::fixed(8 * 1024),
                max_unacknowledged_bytes: 2 * 1024 * 1024,
                max_unacknowledged_chunks: 512,
                redundant_realtime: false,
            },
            max_reorder_bytes_per_stream: 2 * 1024 * 1024,
            max_receive_streams: 16,
            stream_receive_window: 2 * 1024 * 1024,
            max_ack_ranges: 16,
            require_stream_open: true,
            retransmit_after: Duration::from_secs(2),
            retransmit_scan_interval: Duration::from_millis(20),
        },
        Duration::from_secs(2),
        Duration::from_secs(2),
    )
    .unwrap()
}

fn provider_lane(id: u32, failure_domain: u64, rtt_ms: u64, endpoint: &str) -> ProviderLane {
    ProviderLane::new(
        LaneConfig::new(
            LaneId::new(id).unwrap(),
            FailureDomain::new(failure_domain).unwrap(),
            Duration::from_millis(rtt_ms),
            100_000_000,
        )
        .unwrap(),
        EndpointProvider::Tcp,
        endpoint,
    )
    .unwrap()
}

fn collect_phases(
    progress: &mut tokio::sync::broadcast::Receiver<anonssh_bond_tokio::ProviderProgress>,
) -> Vec<ProviderPhase> {
    let mut phases = Vec::new();
    while let Ok(event) = progress.try_recv() {
        phases.push(event.phase);
    }
    phases
}

#[derive(Clone)]
struct InitialPayloadTcpProvider {
    observed: Arc<AtomicUsize>,
}

impl LaneDialProvider for InitialPayloadTcpProvider {
    fn provider(&self) -> EndpointProvider {
        EndpointProvider::Tcp
    }

    fn dial<'a>(&'a self, _endpoint: &'a str) -> ProviderFuture<'a, BoxLaneIo> {
        Box::pin(async {
            Err(io::Error::new(
                io::ErrorKind::Unsupported,
                "BondDialer bypassed the atomic initial-payload path",
            ))
        })
    }

    fn dial_with_initial_payload<'a>(
        &'a self,
        endpoint: &'a str,
        initial_payload: &'a [u8],
    ) -> ProviderFuture<'a, BoxLaneIo> {
        Box::pin(async move {
            if !initial_payload.starts_with(b"ABJ1") {
                return Err(io::Error::new(
                    io::ErrorKind::InvalidData,
                    "BondDialer omitted the authenticated client hello",
                ));
            }
            let address = endpoint.strip_prefix("tcp://").ok_or_else(|| {
                io::Error::new(io::ErrorKind::InvalidInput, "invalid test TCP endpoint")
            })?;
            let mut stream = TcpStream::connect(address).await?;
            stream.write_all(initial_payload).await?;
            stream.flush().await?;
            self.observed.fetch_add(1, Ordering::AcqRel);
            Ok(Box::new(stream) as BoxLaneIo)
        })
    }
}

#[derive(Default)]
struct ProviderProbe {
    active: AtomicUsize,
    peak: AtomicUsize,
    started: AtomicUsize,
    cancelled: AtomicUsize,
}

#[derive(Clone)]
struct PendingProvider {
    state: Arc<ProviderProbe>,
}

impl LaneDialProvider for PendingProvider {
    fn provider(&self) -> EndpointProvider {
        EndpointProvider::Tcp
    }

    fn dial<'a>(&'a self, _endpoint: &'a str) -> ProviderFuture<'a, BoxLaneIo> {
        Box::pin(async move {
            let active = self.state.active.fetch_add(1, Ordering::AcqRel) + 1;
            self.state.started.fetch_add(1, Ordering::AcqRel);
            self.state.peak.fetch_max(active, Ordering::AcqRel);
            let _guard = ActiveProviderCall {
                state: self.state.clone(),
            };
            pending::<()>().await;
            unreachable!("pending provider completed")
        })
    }
}

struct ActiveProviderCall {
    state: Arc<ProviderProbe>,
}

impl Drop for ActiveProviderCall {
    fn drop(&mut self) {
        self.state.active.fetch_sub(1, Ordering::AcqRel);
        self.state.cancelled.fetch_add(1, Ordering::AcqRel);
    }
}
