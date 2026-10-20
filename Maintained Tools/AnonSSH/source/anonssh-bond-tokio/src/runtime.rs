use std::collections::{BTreeMap, BTreeSet, VecDeque};
use std::error::Error;
use std::fmt;
use std::time::Duration;

use anonssh_bond::{
    AckRange, AcknowledgedChunk, BondScheduler, BondSender, CapabilityAdvertisement,
    CapabilityError, DeliverySample, Frame, FrameFlags, FrameKind, LaneConfig, LaneId,
    LaneSnapshot, Reassembler, ReassemblyError, ScheduledFrame, SchedulerConfig, SchedulerError,
    SelectiveAcknowledgement, SenderConfig, SenderError, StreamId, StreamOpen, StreamReset,
    Timestamp, TopologyAdvertisement, TopologyError, TrafficClass, TransmissionReason, HEADER_LEN,
    MAX_ACK_RANGES, MAX_TOPOLOGY_DESCRIPTORS,
};
use bytes::Bytes;
use tokio::sync::{mpsc, oneshot, watch};
use tokio::task::JoinHandle;
use tokio::time::{Instant, MissedTickBehavior};

use crate::handshake::{BondProtocolVersion, ServerIncarnation};
use crate::record::RecordError;

mod lane;

pub use lane::RuntimeLane;

use lane::{spawn_lane, LaneHandle};

const MAX_RUNTIME_LANES: usize = MAX_TOPOLOGY_DESCRIPTORS;
const LANE_QUEUE_CONTROL_RESERVE: usize = 256;
const CONTROL_BATCH_TARGET_BYTES: usize = 64 * 1024;
const ACK_FLUSH_INTERVAL: Duration = Duration::from_millis(10);
const MINIMUM_ADAPTIVE_RTO: Duration = Duration::from_secs(2);
const MINIMUM_LIVENESS_TIMEOUT: Duration = Duration::from_secs(30);
const MAXIMUM_LIVENESS_PROBE_INTERVAL: Duration = Duration::from_secs(10);

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct BondRuntimeConfig {
    pub session_id: u64,
    pub scheduler: SchedulerConfig,
    pub sender: SenderConfig,
    pub max_reorder_bytes_per_stream: usize,
    pub max_receive_streams: usize,
    pub stream_receive_window: usize,
    pub max_ack_ranges: usize,
    pub require_stream_open: bool,
    pub retransmit_after: Duration,
    pub retransmit_scan_interval: Duration,
}

impl Default for BondRuntimeConfig {
    fn default() -> Self {
        Self {
            session_id: 1,
            scheduler: SchedulerConfig::default(),
            sender: SenderConfig::default(),
            max_reorder_bytes_per_stream: 8 * 1024 * 1024,
            max_receive_streams: 256,
            stream_receive_window: 1024 * 1024,
            max_ack_ranges: 16,
            require_stream_open: true,
            retransmit_after: Duration::from_secs(5),
            retransmit_scan_interval: Duration::from_millis(250),
        }
    }
}

impl BondRuntimeConfig {
    pub(crate) fn validate(self) -> Result<Self, BondRuntimeError> {
        if self.session_id == 0 {
            return Err(BondRuntimeError::ZeroSessionId);
        }
        if self.max_reorder_bytes_per_stream == 0 {
            return Err(BondRuntimeError::ZeroReorderLimit);
        }
        if self.max_receive_streams == 0 {
            return Err(BondRuntimeError::ZeroStreamLimit);
        }
        if self.stream_receive_window == 0 {
            return Err(BondRuntimeError::ZeroReceiveWindow);
        }
        if self.max_ack_ranges == 0 || self.max_ack_ranges > MAX_ACK_RANGES {
            return Err(BondRuntimeError::InvalidAckRangeLimit(self.max_ack_ranges));
        }
        if self.retransmit_after.is_zero() || self.retransmit_scan_interval.is_zero() {
            return Err(BondRuntimeError::ZeroRetransmitDuration);
        }
        Ok(self)
    }

    fn lane_queue_capacities(self) -> Result<LaneQueueCapacities, BondRuntimeError> {
        let latency_sensitive = self
            .sender
            .max_unacknowledged_chunks
            .checked_add(LANE_QUEUE_CONTROL_RESERVE)
            .ok_or(BondRuntimeError::QueueCapacityOverflow)?;
        Ok(LaneQueueCapacities {
            latency_sensitive,
            bulk: self.sender.max_unacknowledged_chunks,
        })
    }

    fn control_batch_bytes(self) -> u64 {
        let receive_window_fraction = (self.stream_receive_window / 4).max(1);
        receive_window_fraction.min(CONTROL_BATCH_TARGET_BYTES) as u64
    }
}

#[derive(Clone, Copy)]
pub(super) struct LaneQueueCapacities {
    pub(super) latency_sensitive: usize,
    pub(super) bulk: usize,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ReceivedData {
    pub stream_id: StreamId,
    pub bytes: Bytes,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum RuntimeEvent {
    StreamOpened {
        stream_id: StreamId,
        class: TrafficClass,
    },
    Data(ReceivedData),
    StreamFinished {
        stream_id: StreamId,
    },
    StreamRetired {
        stream_id: StreamId,
    },
    StreamReset {
        stream_id: StreamId,
        code: u32,
    },
    TopologyAdvertised(TopologyAdvertisement),
    CapabilitiesAdvertised(CapabilityAdvertisement),
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct BondRuntimeStats {
    pub observed_at: Timestamp,
    pub lanes: Vec<LaneSnapshot>,
    pub received_by_lane: Vec<LaneReceiveStats>,
    pub new_data_frames: u64,
    pub redundant_realtime_frames: u64,
    pub dropped_redundant_realtime_frames: u64,
    pub retransmitted_frames: u64,
    pub ping_frames: u64,
    pub pong_frames: u64,
    pub liveness_failures: u64,
    pub acknowledgement_frames: u64,
    pub window_update_frames: u64,
    pub replayed_control_frames: u64,
    pub delivered_bytes: u64,
    pub reorder_high_water: usize,
    pub unacknowledged_bytes: usize,
    pub bulk_chunk_pressure_limit: usize,
    pub backpressured_streams: u64,
    pub stream_backpressure_events: u64,
    pub active_streams: usize,
    pub retired_stream_tombstones: usize,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct LaneReceiveStats {
    pub id: LaneId,
    pub unique_data_bytes: u64,
    pub unique_data_frames: u64,
}

pub struct BondRuntime {
    protocol_version: BondProtocolVersion,
    server_incarnation: Option<ServerIncarnation>,
    event_tx: mpsc::Sender<Event>,
    output_rx: mpsc::Receiver<RuntimeEvent>,
    send_progress_rx: watch::Receiver<u64>,
    terminal_error_rx: watch::Receiver<Option<String>>,
    actor: Option<JoinHandle<Result<(), BondRuntimeError>>>,
}

#[derive(Clone)]
pub struct BondRuntimeControl {
    protocol_version: BondProtocolVersion,
    server_incarnation: Option<ServerIncarnation>,
    event_tx: mpsc::Sender<Event>,
    send_progress_rx: watch::Receiver<u64>,
    terminal_error_rx: watch::Receiver<Option<String>>,
}

impl BondRuntimeControl {
    pub const fn protocol_version(&self) -> BondProtocolVersion {
        self.protocol_version
    }

    pub const fn server_incarnation(&self) -> Option<ServerIncarnation> {
        self.server_incarnation
    }

    pub(crate) fn terminal_cause(&self) -> Option<String> {
        self.terminal_error_rx.borrow().clone()
    }

    pub(crate) fn terminal_receiver(&self) -> watch::Receiver<Option<String>> {
        self.terminal_error_rx.clone()
    }

    pub(crate) fn send_progress_receiver(&self) -> watch::Receiver<u64> {
        self.send_progress_rx.clone()
    }

    pub(crate) fn stopped_error(&self) -> BondRuntimeError {
        match self.terminal_cause() {
            Some(error) => BondRuntimeError::StoppedWithCause(error),
            None => BondRuntimeError::Stopped,
        }
    }

    pub async fn open_stream(
        &self,
        stream_id: StreamId,
        class: TrafficClass,
    ) -> Result<(), BondRuntimeError> {
        let (reply_tx, reply_rx) = oneshot::channel();
        self.event_tx
            .send(Event::OpenStream {
                stream_id,
                class,
                reply: reply_tx,
            })
            .await
            .map_err(|_| self.stopped_error())?;
        reply_rx.await.map_err(|_| self.stopped_error())?
    }

    pub async fn send(
        &self,
        stream_id: StreamId,
        class: TrafficClass,
        bytes: Vec<u8>,
    ) -> Result<(), BondRuntimeError> {
        self.send_shared(stream_id, class, Bytes::from(bytes)).await
    }

    pub(crate) async fn send_shared(
        &self,
        stream_id: StreamId,
        class: TrafficClass,
        bytes: Bytes,
    ) -> Result<(), BondRuntimeError> {
        let (reply_tx, reply_rx) = oneshot::channel();
        self.event_tx
            .send(Event::Send {
                stream_id,
                class,
                bytes,
                reply: reply_tx,
            })
            .await
            .map_err(|_| self.stopped_error())?;
        reply_rx.await.map_err(|_| self.stopped_error())?
    }

    pub async fn release_receive_credit(
        &self,
        stream_id: StreamId,
        bytes: usize,
    ) -> Result<(), BondRuntimeError> {
        let (reply_tx, reply_rx) = oneshot::channel();
        self.event_tx
            .send(Event::ReleaseReceiveCredit {
                stream_id,
                bytes,
                reply: reply_tx,
            })
            .await
            .map_err(|_| self.stopped_error())?;
        reply_rx.await.map_err(|_| self.stopped_error())?
    }

    pub async fn close_stream(&self, stream_id: StreamId) -> Result<(), BondRuntimeError> {
        let (reply_tx, reply_rx) = oneshot::channel();
        self.event_tx
            .send(Event::CloseStream {
                stream_id,
                reply: reply_tx,
            })
            .await
            .map_err(|_| self.stopped_error())?;
        reply_rx.await.map_err(|_| self.stopped_error())?
    }

    pub async fn reset_stream(
        &self,
        stream_id: StreamId,
        code: u32,
    ) -> Result<(), BondRuntimeError> {
        let (reply_tx, reply_rx) = oneshot::channel();
        self.event_tx
            .send(Event::ResetStream {
                stream_id,
                code,
                reply: reply_tx,
            })
            .await
            .map_err(|_| self.stopped_error())?;
        reply_rx.await.map_err(|_| self.stopped_error())?
    }

    pub async fn fail_lane(&self, lane_id: LaneId) -> Result<(), BondRuntimeError> {
        let (reply_tx, reply_rx) = oneshot::channel();
        self.event_tx
            .send(Event::FailLane {
                lane_id,
                reply: reply_tx,
            })
            .await
            .map_err(|_| self.stopped_error())?;
        reply_rx.await.map_err(|_| self.stopped_error())?
    }

    pub async fn add_lane(&self, lane: RuntimeLane) -> Result<(), BondRuntimeError> {
        let (reply_tx, reply_rx) = oneshot::channel();
        self.event_tx
            .send(Event::AddLane {
                lane,
                reply: reply_tx,
            })
            .await
            .map_err(|_| self.stopped_error())?;
        reply_rx.await.map_err(|_| self.stopped_error())?
    }

    pub async fn declare_lane(&self, config: LaneConfig) -> Result<(), BondRuntimeError> {
        let (reply_tx, reply_rx) = oneshot::channel();
        self.event_tx
            .send(Event::DeclareLane {
                config,
                reply: reply_tx,
            })
            .await
            .map_err(|_| self.stopped_error())?;
        reply_rx.await.map_err(|_| self.stopped_error())?
    }

    pub async fn advertise_topology(
        &self,
        advertisement: TopologyAdvertisement,
    ) -> Result<(), BondRuntimeError> {
        let (reply_tx, reply_rx) = oneshot::channel();
        self.event_tx
            .send(Event::AdvertiseTopology {
                advertisement,
                reply: reply_tx,
            })
            .await
            .map_err(|_| self.stopped_error())?;
        reply_rx.await.map_err(|_| self.stopped_error())?
    }

    pub async fn advertise_capabilities(
        &self,
        advertisement: CapabilityAdvertisement,
    ) -> Result<(), BondRuntimeError> {
        let (reply_tx, reply_rx) = oneshot::channel();
        self.event_tx
            .send(Event::AdvertiseCapabilities {
                advertisement,
                reply: reply_tx,
            })
            .await
            .map_err(|_| self.stopped_error())?;
        reply_rx.await.map_err(|_| self.stopped_error())?
    }

    pub async fn statistics(&self) -> Result<BondRuntimeStats, BondRuntimeError> {
        let (reply_tx, reply_rx) = oneshot::channel();
        self.event_tx
            .send(Event::Statistics { reply: reply_tx })
            .await
            .map_err(|_| self.stopped_error())?;
        reply_rx.await.map_err(|_| self.stopped_error())?
    }

    pub async fn terminate(&self, cause: String) -> Result<(), BondRuntimeError> {
        self.event_tx
            .send(Event::Terminate { cause })
            .await
            .map_err(|_| self.stopped_error())
    }

    #[cfg(test)]
    pub(crate) async fn inject_inbound_for_test(
        &self,
        lane_id: LaneId,
        generation: u64,
        frame: Frame,
    ) -> Result<(), BondRuntimeError> {
        self.event_tx
            .send(Event::Inbound {
                lane_id,
                generation,
                frame,
            })
            .await
            .map_err(|_| self.stopped_error())
    }
}

impl BondRuntime {
    pub fn spawn(
        config: BondRuntimeConfig,
        lanes: Vec<RuntimeLane>,
    ) -> Result<Self, BondRuntimeError> {
        let mut config = config.validate()?;
        if lanes.is_empty() {
            return Err(BondRuntimeError::NoLanes);
        }
        if lanes.len() > MAX_RUNTIME_LANES {
            return Err(BondRuntimeError::LaneLimitExceeded(MAX_RUNTIME_LANES));
        }
        let protocol_version = lanes[0].protocol_version;
        let server_incarnation = lanes[0].server_incarnation;
        if let Some(lane) = lanes
            .iter()
            .find(|lane| lane.protocol_version != protocol_version)
        {
            return Err(BondRuntimeError::LaneProtocolVersionMismatch {
                expected: protocol_version,
                actual: lane.protocol_version,
            });
        }
        if let Some(lane) = lanes
            .iter()
            .find(|lane| lane.server_incarnation != server_incarnation)
        {
            return Err(BondRuntimeError::LaneServerIncarnationMismatch {
                expected: server_incarnation,
                actual: lane.server_incarnation,
            });
        }
        if protocol_version < BondProtocolVersion::V3 {
            config.sender.redundant_realtime = false;
        }

        let mut scheduler = BondScheduler::new(config.scheduler)?;
        for lane in &lanes {
            scheduler.add_lane(lane.config)?;
        }
        let sender = BondSender::new(config.session_id, config.sender, scheduler)?;
        let (event_tx, event_rx) = mpsc::channel(256);
        let (output_tx, output_rx) = mpsc::channel(64);
        let (send_progress_tx, send_progress_rx) = watch::channel(0_u64);
        let (terminal_error_tx, terminal_error_rx) = watch::channel(None);
        let started_at = Instant::now();
        let mut handles = BTreeMap::new();
        let mut lane_ids = BTreeSet::new();
        let mut received_by_lane = BTreeMap::new();
        let mut liveness = BTreeMap::new();
        let lane_queue_capacities = config.lane_queue_capacities()?;
        let mut next_lane_generation = 1_u64;
        for lane in lanes {
            let generation = next_lane_generation;
            next_lane_generation = next_lane_generation
                .checked_add(1)
                .ok_or(BondRuntimeError::LaneGenerationExhausted)?;
            lane_ids.insert(lane.config.id);
            received_by_lane.insert(lane.config.id, LaneReceiveCounters::default());
            liveness.insert(lane.config.id, LaneLiveness::new(Timestamp::ZERO));
            handles.insert(
                lane.config.id,
                spawn_lane(
                    lane.config.id,
                    generation,
                    lane.io,
                    lane.record_keys,
                    event_tx.clone(),
                    lane_queue_capacities,
                    config.retransmit_after,
                ),
            );
        }

        let actor = Actor {
            config,
            protocol_version,
            server_incarnation,
            started_at,
            sender,
            streams: BTreeMap::new(),
            retired_streams: BTreeMap::new(),
            retired_stream_order: VecDeque::new(),
            retired_stream_watermarks: [0; 2],
            lanes: handles,
            lane_ids,
            received_by_lane,
            output_tx,
            send_progress_tx,
            event_tx: event_tx.clone(),
            event_rx,
            stats: Counters::default(),
            dispatch_queue: VecDeque::with_capacity(1),
            acknowledged_chunks: Vec::new(),
            acknowledgement_ranges: Vec::with_capacity(config.max_ack_ranges),
            pending_acknowledgements: PendingAcknowledgements::new(config.max_receive_streams),
            delivery_history: DeliveryHistory::new(),
            liveness,
            shutdown_reply: None,
            local_close_requested: false,
            local_close_ack_received: false,
            peer_close_received: false,
            peer_close_ack_written_lanes: BTreeSet::new(),
            next_lane_generation,
            next_ping_token: 1,
            local_topology_generation: 0,
            local_topology: None,
            remote_topology_generation: 0,
            remote_topology: None,
            local_capability_generation: 0,
            local_capabilities: None,
            remote_capability_generation: 0,
            remote_capabilities: None,
            control_replay: VecDeque::new(),
            lane_queue_capacities,
        };
        let actor = tokio::spawn(async move {
            let result = actor.run().await;
            if let Err(error) = &result {
                terminal_error_tx.send_replace(Some(error.terminal_cause()));
            }
            result
        });
        Ok(Self {
            protocol_version,
            server_incarnation,
            event_tx,
            output_rx,
            send_progress_rx,
            terminal_error_rx,
            actor: Some(actor),
        })
    }

    pub async fn open_stream(
        &self,
        stream_id: StreamId,
        class: TrafficClass,
    ) -> Result<(), BondRuntimeError> {
        self.control().open_stream(stream_id, class).await
    }

    pub async fn send(
        &self,
        stream_id: StreamId,
        class: TrafficClass,
        bytes: Vec<u8>,
    ) -> Result<(), BondRuntimeError> {
        self.control().send(stream_id, class, bytes).await
    }

    pub async fn receive(&mut self) -> Option<ReceivedData> {
        while let Some(event) = self.output_rx.recv().await {
            if let RuntimeEvent::Data(data) = event {
                if self
                    .control()
                    .release_receive_credit(data.stream_id, data.bytes.len())
                    .await
                    .is_err()
                {
                    return None;
                }
                return Some(data);
            }
        }
        None
    }

    pub async fn receive_event(&mut self) -> Option<RuntimeEvent> {
        let event = self.output_rx.recv().await?;
        if let RuntimeEvent::Data(data) = &event {
            if self
                .control()
                .release_receive_credit(data.stream_id, data.bytes.len())
                .await
                .is_err()
            {
                return None;
            }
        }
        Some(event)
    }

    pub(crate) async fn receive_event_uncredited(
        &mut self,
    ) -> Result<RuntimeEvent, BondRuntimeError> {
        self.output_rx
            .recv()
            .await
            .ok_or_else(|| self.stopped_error())
    }

    pub async fn close_stream(&self, stream_id: StreamId) -> Result<(), BondRuntimeError> {
        self.control().close_stream(stream_id).await
    }

    pub async fn reset_stream(
        &self,
        stream_id: StreamId,
        code: u32,
    ) -> Result<(), BondRuntimeError> {
        self.control().reset_stream(stream_id, code).await
    }

    pub async fn fail_lane(&self, lane_id: LaneId) -> Result<(), BondRuntimeError> {
        self.control().fail_lane(lane_id).await
    }

    pub async fn add_lane(&self, lane: RuntimeLane) -> Result<(), BondRuntimeError> {
        self.control().add_lane(lane).await
    }

    pub async fn declare_lane(&self, config: LaneConfig) -> Result<(), BondRuntimeError> {
        self.control().declare_lane(config).await
    }

    pub async fn advertise_topology(
        &self,
        advertisement: TopologyAdvertisement,
    ) -> Result<(), BondRuntimeError> {
        self.control().advertise_topology(advertisement).await
    }

    pub async fn statistics(&self) -> Result<BondRuntimeStats, BondRuntimeError> {
        self.control().statistics().await
    }

    pub fn control(&self) -> BondRuntimeControl {
        BondRuntimeControl {
            protocol_version: self.protocol_version,
            server_incarnation: self.server_incarnation,
            event_tx: self.event_tx.clone(),
            send_progress_rx: self.send_progress_rx.clone(),
            terminal_error_rx: self.terminal_error_rx.clone(),
        }
    }

    fn stopped_error(&self) -> BondRuntimeError {
        match self.terminal_error_rx.borrow().as_ref() {
            Some(error) => BondRuntimeError::StoppedWithCause(error.clone()),
            None => BondRuntimeError::Stopped,
        }
    }

    pub async fn shutdown(mut self) -> Result<(), BondRuntimeError> {
        let (reply_tx, reply_rx) = oneshot::channel();
        self.event_tx
            .send(Event::Shutdown { reply: reply_tx })
            .await
            .map_err(|_| self.stopped_error())?;
        reply_rx.await.map_err(|_| self.stopped_error())??;
        let actor = self.actor.take().ok_or(BondRuntimeError::Stopped)?;
        actor
            .await
            .map_err(|error| BondRuntimeError::ActorJoin(error.to_string()))?
    }
}

impl Drop for BondRuntime {
    fn drop(&mut self) {
        if let Some(actor) = self.actor.take() {
            actor.abort();
        }
    }
}

enum Event {
    OpenStream {
        stream_id: StreamId,
        class: TrafficClass,
        reply: oneshot::Sender<Result<(), BondRuntimeError>>,
    },
    Send {
        stream_id: StreamId,
        class: TrafficClass,
        bytes: Bytes,
        reply: oneshot::Sender<Result<(), BondRuntimeError>>,
    },
    ReleaseReceiveCredit {
        stream_id: StreamId,
        bytes: usize,
        reply: oneshot::Sender<Result<(), BondRuntimeError>>,
    },
    Inbound {
        lane_id: LaneId,
        generation: u64,
        frame: Frame,
    },
    LaneClosed {
        lane_id: LaneId,
        generation: u64,
    },
    PingWritten {
        lane_id: LaneId,
        generation: u64,
        token: u64,
    },
    SessionCloseWritten {
        lane_id: LaneId,
        generation: u64,
        acknowledgement: bool,
    },
    FailLane {
        lane_id: LaneId,
        reply: oneshot::Sender<Result<(), BondRuntimeError>>,
    },
    AddLane {
        lane: RuntimeLane,
        reply: oneshot::Sender<Result<(), BondRuntimeError>>,
    },
    DeclareLane {
        config: LaneConfig,
        reply: oneshot::Sender<Result<(), BondRuntimeError>>,
    },
    AdvertiseTopology {
        advertisement: TopologyAdvertisement,
        reply: oneshot::Sender<Result<(), BondRuntimeError>>,
    },
    AdvertiseCapabilities {
        advertisement: CapabilityAdvertisement,
        reply: oneshot::Sender<Result<(), BondRuntimeError>>,
    },
    CloseStream {
        stream_id: StreamId,
        reply: oneshot::Sender<Result<(), BondRuntimeError>>,
    },
    ResetStream {
        stream_id: StreamId,
        code: u32,
        reply: oneshot::Sender<Result<(), BondRuntimeError>>,
    },
    Statistics {
        reply: oneshot::Sender<Result<BondRuntimeStats, BondRuntimeError>>,
    },
    Shutdown {
        reply: oneshot::Sender<Result<(), BondRuntimeError>>,
    },
    Terminate {
        cause: String,
    },
}

#[derive(Default)]
struct Counters {
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
    reorder_high_water: usize,
}

#[derive(Default)]
struct LaneReceiveCounters {
    unique_data_bytes: u64,
    unique_data_frames: u64,
}

#[derive(Clone, Copy)]
struct LaneLiveness {
    last_received_at: Timestamp,
    outstanding_ping: Option<OutstandingPing>,
}

#[derive(Clone, Copy)]
enum OutstandingPing {
    Queued { token: u64 },
    Sent { token: u64, sent_at: Timestamp },
}

impl LaneLiveness {
    const fn new(now: Timestamp) -> Self {
        Self {
            last_received_at: now,
            outstanding_ping: None,
        }
    }

    fn queue_ping(&mut self, token: u64) {
        self.outstanding_ping = Some(OutstandingPing::Queued { token });
    }

    fn mark_ping_written(&mut self, token: u64, sent_at: Timestamp) {
        if matches!(
            self.outstanding_ping,
            Some(OutstandingPing::Queued { token: queued }) if queued == token
        ) {
            self.outstanding_ping = Some(OutstandingPing::Sent { token, sent_at });
        }
    }

    fn response_deadline_started_at(&self) -> Option<Timestamp> {
        match self.outstanding_ping {
            Some(OutstandingPing::Sent { sent_at, .. }) => Some(sent_at),
            Some(OutstandingPing::Queued { .. }) | None => None,
        }
    }

    const fn has_outstanding_probe(&self) -> bool {
        self.outstanding_ping.is_some()
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct DeliveryCohort {
    lane_id: LaneId,
    bytes: usize,
    oldest_sent_at: Timestamp,
    newest_sent_at: Timestamp,
}

impl DeliveryCohort {
    fn sample(
        self,
        now: Timestamp,
        previous_delivery_at: Option<Timestamp>,
    ) -> Result<DeliverySample, SchedulerError> {
        let flight_elapsed = elapsed_since(now, self.oldest_sent_at);
        let elapsed = previous_delivery_at
            .filter(|previous| *previous >= self.oldest_sent_at && *previous < now)
            .and_then(|previous| now.duration_since(previous))
            .filter(|duration| !duration.is_zero())
            .map_or(flight_elapsed, |spacing| spacing.min(flight_elapsed));
        let round_trip_time = elapsed_since(now, self.newest_sent_at);
        DeliverySample::new(self.bytes, elapsed, round_trip_time)
    }
}

struct DeliveryCohorts {
    entries: [Option<DeliveryCohort>; MAX_RUNTIME_LANES],
    len: usize,
}

impl DeliveryCohorts {
    fn from_chunks(chunks: &[AcknowledgedChunk]) -> Result<Self, BondRuntimeError> {
        let mut cohorts = Self {
            entries: [None; MAX_RUNTIME_LANES],
            len: 0,
        };
        for chunk in chunks {
            if let Some(cohort) = cohorts.entries[..cohorts.len]
                .iter_mut()
                .flatten()
                .find(|cohort| cohort.lane_id == chunk.lane_id)
            {
                cohort.bytes = cohort
                    .bytes
                    .checked_add(chunk.bytes)
                    .ok_or(BondRuntimeError::CounterOverflow)?;
                cohort.oldest_sent_at = cohort.oldest_sent_at.min(chunk.last_sent_at);
                cohort.newest_sent_at = cohort.newest_sent_at.max(chunk.last_sent_at);
                continue;
            }
            if cohorts.len == MAX_RUNTIME_LANES {
                return Err(BondRuntimeError::LaneLimitExceeded(MAX_RUNTIME_LANES));
            }
            cohorts.entries[cohorts.len] = Some(DeliveryCohort {
                lane_id: chunk.lane_id,
                bytes: chunk.bytes,
                oldest_sent_at: chunk.last_sent_at,
                newest_sent_at: chunk.last_sent_at,
            });
            cohorts.len += 1;
        }
        Ok(cohorts)
    }

    fn iter(&self) -> impl Iterator<Item = DeliveryCohort> + '_ {
        self.entries[..self.len].iter().flatten().copied()
    }
}

#[derive(Clone, Copy)]
struct DeliveryObservation {
    lane_id: LaneId,
    at: Timestamp,
}

struct DeliveryHistory {
    entries: [Option<DeliveryObservation>; MAX_RUNTIME_LANES],
    len: usize,
}

impl DeliveryHistory {
    fn new() -> Self {
        Self {
            entries: [None; MAX_RUNTIME_LANES],
            len: 0,
        }
    }

    fn previous_and_record(
        &mut self,
        lane_id: LaneId,
        now: Timestamp,
    ) -> Result<Option<Timestamp>, BondRuntimeError> {
        if let Some(observation) = self.entries[..self.len]
            .iter_mut()
            .flatten()
            .find(|observation| observation.lane_id == lane_id)
        {
            let previous = observation.at;
            observation.at = now;
            return Ok(Some(previous));
        }
        if self.len == MAX_RUNTIME_LANES {
            return Err(BondRuntimeError::LaneLimitExceeded(MAX_RUNTIME_LANES));
        }
        self.entries[self.len] = Some(DeliveryObservation { lane_id, at: now });
        self.len += 1;
        Ok(None)
    }
}

fn elapsed_since(now: Timestamp, then: Timestamp) -> Duration {
    now.duration_since(then)
        .unwrap_or(Duration::from_micros(1))
        .max(Duration::from_micros(1))
}

fn validate_liveness_frame(frame: &Frame, kind: FrameKind) -> Result<(), BondRuntimeError> {
    if frame.header.kind != kind || frame.header.stream_id != 0 || !frame.payload.is_empty() {
        return Err(BondRuntimeError::MalformedControlFrame(kind));
    }
    Ok(())
}

struct PendingAcknowledgements {
    stream_ids: Vec<StreamId>,
    deadline: Option<Instant>,
}

impl PendingAcknowledgements {
    fn new(max_streams: usize) -> Self {
        Self {
            stream_ids: Vec::with_capacity(max_streams),
            deadline: None,
        }
    }

    fn queue(&mut self, stream_id: StreamId) {
        if self.stream_ids.is_empty() {
            self.deadline = Some(Instant::now() + ACK_FLUSH_INTERVAL);
        }
        self.stream_ids.push(stream_id);
    }

    fn deadline(&self) -> Option<Instant> {
        self.deadline
    }

    fn pop(&mut self) -> Option<StreamId> {
        let stream_id = self.stream_ids.pop();
        if self.stream_ids.is_empty() {
            self.deadline = None;
        }
        stream_id
    }

    fn remove(&mut self, stream_id: StreamId) {
        if let Some(index) = self
            .stream_ids
            .iter()
            .position(|queued| *queued == stream_id)
        {
            self.stream_ids.swap_remove(index);
        }
        if self.stream_ids.is_empty() {
            self.deadline = None;
        }
    }

    fn defer_until_lane_returns(&mut self) {
        self.deadline = None;
    }
}

struct StreamState {
    class: TrafficClass,
    opened_locally: bool,
    initial_local_window_end: u64,
    initial_remote_window_end: Option<u64>,
    receiver: Reassembler,
    remote_window_end: u64,
    local_window_end: u64,
    consumed_offset: u64,
    unacknowledged_received_bytes: u64,
    last_acknowledged_range_count: usize,
    acknowledgement_pending: bool,
    acknowledgement_queued: bool,
    last_advertised_window_end: u64,
    remote_final_offset: Option<u64>,
    remote_finished: bool,
    local_final_offset: Option<u64>,
    open_reply: Option<oneshot::Sender<Result<(), BondRuntimeError>>>,
    close_reply: Option<oneshot::Sender<Result<(), BondRuntimeError>>>,
}

#[derive(Clone, Copy)]
struct RetiredStreamState {
    class: TrafficClass,
    opened_locally: bool,
    initial_local_window_end: u64,
    initial_remote_window_end: u64,
    local_final_offset: u64,
    remote_final_offset: u64,
}

impl RetiredStreamState {
    fn from_finished(state: &StreamState) -> Self {
        Self {
            class: state.class,
            opened_locally: state.opened_locally,
            initial_local_window_end: state.initial_local_window_end,
            initial_remote_window_end: state
                .initial_remote_window_end
                .expect("retired stream completed its opening handshake"),
            local_final_offset: state
                .local_final_offset
                .expect("retired stream completed its local half-close"),
            remote_final_offset: state
                .remote_final_offset
                .expect("retired stream completed its remote half-close"),
        }
    }
}

impl StreamState {
    fn new(
        class: TrafficClass,
        opened_locally: bool,
        reorder_limit: usize,
        local_window_end: u64,
        initial_remote_window_end: Option<u64>,
    ) -> Result<Self, BondRuntimeError> {
        Ok(Self {
            class,
            opened_locally,
            initial_local_window_end: local_window_end,
            initial_remote_window_end,
            receiver: Reassembler::new(0, reorder_limit)?,
            remote_window_end: initial_remote_window_end.unwrap_or(0),
            local_window_end,
            consumed_offset: 0,
            unacknowledged_received_bytes: 0,
            last_acknowledged_range_count: 0,
            acknowledgement_pending: false,
            acknowledgement_queued: false,
            last_advertised_window_end: local_window_end,
            remote_final_offset: None,
            remote_finished: false,
            local_final_offset: None,
            open_reply: None,
            close_reply: None,
        })
    }
}

struct Actor {
    config: BondRuntimeConfig,
    protocol_version: BondProtocolVersion,
    server_incarnation: Option<ServerIncarnation>,
    started_at: Instant,
    sender: BondSender,
    streams: BTreeMap<StreamId, StreamState>,
    retired_streams: BTreeMap<StreamId, RetiredStreamState>,
    retired_stream_order: VecDeque<StreamId>,
    retired_stream_watermarks: [u64; 2],
    lanes: BTreeMap<LaneId, LaneHandle>,
    lane_ids: BTreeSet<LaneId>,
    received_by_lane: BTreeMap<LaneId, LaneReceiveCounters>,
    output_tx: mpsc::Sender<RuntimeEvent>,
    send_progress_tx: watch::Sender<u64>,
    event_tx: mpsc::Sender<Event>,
    event_rx: mpsc::Receiver<Event>,
    stats: Counters,
    dispatch_queue: VecDeque<ScheduledFrame>,
    acknowledged_chunks: Vec<AcknowledgedChunk>,
    acknowledgement_ranges: Vec<AckRange>,
    pending_acknowledgements: PendingAcknowledgements,
    delivery_history: DeliveryHistory,
    liveness: BTreeMap<LaneId, LaneLiveness>,
    shutdown_reply: Option<oneshot::Sender<Result<(), BondRuntimeError>>>,
    local_close_requested: bool,
    local_close_ack_received: bool,
    peer_close_received: bool,
    peer_close_ack_written_lanes: BTreeSet<LaneId>,
    next_lane_generation: u64,
    next_ping_token: u64,
    local_topology_generation: u64,
    local_topology: Option<TopologyAdvertisement>,
    remote_topology_generation: u64,
    remote_topology: Option<TopologyAdvertisement>,
    local_capability_generation: u64,
    local_capabilities: Option<CapabilityAdvertisement>,
    remote_capability_generation: u64,
    remote_capabilities: Option<CapabilityAdvertisement>,
    control_replay: VecDeque<Frame>,
    lane_queue_capacities: LaneQueueCapacities,
}

impl Actor {
    async fn run(mut self) -> Result<(), BondRuntimeError> {
        let mut interval = tokio::time::interval(self.config.retransmit_scan_interval);
        interval.set_missed_tick_behavior(MissedTickBehavior::Skip);
        interval.tick().await;
        loop {
            let acknowledgement_deadline = self.pending_acknowledgements.deadline();
            let acknowledgement_armed = acknowledgement_deadline.is_some();
            let acknowledgement_deadline = acknowledgement_deadline.unwrap_or_else(Instant::now);
            let stop = tokio::select! {
                event = self.event_rx.recv() => {
                    let Some(event) = event else { return Ok(()); };
                    self.handle_event(event).await?
                }
                _ = interval.tick() => {
                    self.check_lane_liveness()?;
                    let frames = self.sender.retransmit_due_adaptive(
                        self.now(),
                        self.minimum_retransmit_after(),
                        self.config.retransmit_after,
                    )?;
                    self.dispatch_scheduled(frames)?;
                    false
                }
                _ = tokio::time::sleep_until(acknowledgement_deadline), if acknowledgement_armed => {
                    self.flush_pending_acknowledgements()?;
                    false
                }
            };
            if stop {
                return Ok(());
            }
            self.flush_control_replay()?;
        }
    }

    async fn handle_event(&mut self, event: Event) -> Result<bool, BondRuntimeError> {
        match event {
            Event::OpenStream {
                stream_id,
                class,
                reply,
            } => self.begin_stream_open(stream_id, class, reply)?,
            Event::Send {
                stream_id,
                class,
                bytes,
                reply,
            } => {
                let result = self.send_stream_data(stream_id, class, bytes);
                let _ = reply.send(result);
            }
            Event::ReleaseReceiveCredit {
                stream_id,
                bytes,
                reply,
            } => {
                let result = self.release_receive_credit(stream_id, bytes).await;
                let _ = reply.send(result);
            }
            Event::Inbound {
                lane_id,
                generation,
                frame,
            } => {
                if !self.is_current_lane(lane_id, generation) {
                    return Ok(false);
                }
                if self.handle_inbound(lane_id, frame).await? {
                    return Ok(true);
                }
            }
            Event::LaneClosed {
                lane_id,
                generation,
            } => {
                if self.is_current_lane(lane_id, generation) {
                    let frames = self.fail_lane_internal(lane_id)?;
                    self.dispatch_scheduled(frames)?;
                    if self.finish_passive_shutdown_if_disconnected() {
                        return Ok(true);
                    }
                }
            }
            Event::PingWritten {
                lane_id,
                generation,
                token,
            } => {
                if self.is_current_lane(lane_id, generation) {
                    let now = self.now();
                    self.liveness
                        .get_mut(&lane_id)
                        .ok_or(BondRuntimeError::LaneUnavailable(lane_id))?
                        .mark_ping_written(token, now);
                }
            }
            Event::SessionCloseWritten {
                lane_id,
                generation,
                acknowledgement,
            } => {
                if self.is_current_lane(lane_id, generation) && acknowledgement {
                    self.peer_close_ack_written_lanes.insert(lane_id);
                    if self.finish_active_shutdown_if_complete() {
                        return Ok(true);
                    }
                }
            }
            Event::FailLane { lane_id, reply } => {
                let result = self
                    .fail_lane_internal(lane_id)
                    .and_then(|frames| self.dispatch_scheduled(frames));
                let _ = reply.send(result);
            }
            Event::AddLane { lane, reply } => {
                let result = self.add_lane_internal(lane).and_then(|frames| {
                    self.dispatch_scheduled(frames)?;
                    self.flush_pending_acknowledgements()
                });
                let _ = reply.send(result);
            }
            Event::DeclareLane { config, reply } => {
                let result = self.declare_lane_internal(config);
                let _ = reply.send(result);
            }
            Event::AdvertiseTopology {
                advertisement,
                reply,
            } => {
                let result = self.advertise_topology(advertisement);
                let _ = reply.send(result);
            }
            Event::AdvertiseCapabilities {
                advertisement,
                reply,
            } => {
                let result = self.advertise_capabilities(advertisement);
                let _ = reply.send(result);
            }
            Event::CloseStream { stream_id, reply } => {
                self.begin_stream_close(stream_id, reply)?;
            }
            Event::ResetStream {
                stream_id,
                code,
                reply,
            } => {
                let result = self.reset_stream(stream_id, code);
                let _ = reply.send(result);
            }
            Event::Statistics { reply } => {
                let _ = reply.send(self.statistics());
            }
            Event::Shutdown { reply } => {
                if !self.config.require_stream_open {
                    self.lanes.clear();
                    let _ = reply.send(Ok(()));
                    return Ok(true);
                }
                if self.begin_session_close(reply)? {
                    return Ok(true);
                }
            }
            Event::Terminate { cause } => {
                return Err(BondRuntimeError::StoppedWithCause(cause));
            }
        }
        Ok(false)
    }

    fn begin_stream_open(
        &mut self,
        stream_id: StreamId,
        class: TrafficClass,
        reply: oneshot::Sender<Result<(), BondRuntimeError>>,
    ) -> Result<(), BondRuntimeError> {
        if self.streams.contains_key(&stream_id)
            || self.retired_streams.contains_key(&stream_id)
            || self.is_evicted_retired_stream(stream_id)
        {
            let _ = reply.send(Err(BondRuntimeError::DuplicateStream(stream_id)));
            return Ok(());
        }
        if self.streams.len() >= self.config.max_receive_streams {
            let _ = reply.send(Err(BondRuntimeError::ReceiveStreamLimitExceeded(
                self.config.max_receive_streams,
            )));
            return Ok(());
        }
        let local_window = self.receive_window()?;
        let mut state = StreamState::new(
            class,
            true,
            self.config.max_reorder_bytes_per_stream,
            local_window,
            None,
        )?;
        state.open_reply = Some(reply);
        self.streams.insert(stream_id, state);
        let payload = StreamOpen::new(class, local_window)?
            .encode_payload()
            .to_vec();
        if let Err(error) = self.send_control(
            FrameKind::StreamOpen,
            FrameFlags::NONE,
            stream_id.get(),
            0,
            payload,
        ) {
            if let Some(mut state) = self.streams.remove(&stream_id) {
                if let Some(reply) = state.open_reply.take() {
                    let _ = reply.send(Err(error));
                }
            }
        }
        Ok(())
    }

    fn send_stream_data(
        &mut self,
        stream_id: StreamId,
        class: TrafficClass,
        bytes: Bytes,
    ) -> Result<(), BondRuntimeError> {
        if !self.streams.contains_key(&stream_id) && !self.config.require_stream_open {
            let window = self.receive_window()?;
            self.streams.insert(
                stream_id,
                StreamState::new(
                    class,
                    false,
                    self.config.max_reorder_bytes_per_stream,
                    window,
                    Some(u64::MAX),
                )?,
            );
        }
        let state = self
            .streams
            .get(&stream_id)
            .ok_or(BondRuntimeError::UnopenedStream(stream_id))?;
        if state.class != class {
            return Err(BondRuntimeError::TrafficClassMismatch(stream_id));
        }
        if state.open_reply.is_some() {
            return Err(BondRuntimeError::StreamOpening(stream_id));
        }
        if state.local_final_offset.is_some() {
            return Err(BondRuntimeError::StreamWriteClosed(stream_id));
        }
        let attempted = self
            .sender
            .next_offset(stream_id)
            .checked_add(u64::try_from(bytes.len()).map_err(|_| BondRuntimeError::OffsetOverflow)?)
            .ok_or(BondRuntimeError::OffsetOverflow)?;
        if attempted > state.remote_window_end {
            return Err(BondRuntimeError::FlowControlBlocked {
                stream_id,
                attempted,
                limit: state.remote_window_end,
            });
        }
        let now = self.now();
        if let Err(error) =
            self.sender
                .enqueue_shared_into(stream_id, class, bytes, now, &mut self.dispatch_queue)
        {
            self.dispatch_queue.clear();
            return Err(error.into());
        }
        self.dispatch_queued()
    }

    async fn release_receive_credit(
        &mut self,
        stream_id: StreamId,
        bytes: usize,
    ) -> Result<(), BondRuntimeError> {
        if !self.config.require_stream_open {
            return Ok(());
        }
        if bytes == 0 {
            return Err(BondRuntimeError::ZeroConsumedBytes);
        }
        let bytes = u64::try_from(bytes).map_err(|_| BondRuntimeError::OffsetOverflow)?;
        let should_advertise = {
            let stream = self
                .streams
                .get_mut(&stream_id)
                .ok_or(BondRuntimeError::UnopenedStream(stream_id))?;
            let consumed = stream
                .consumed_offset
                .checked_add(bytes)
                .ok_or(BondRuntimeError::OffsetOverflow)?;
            if consumed > stream.receiver.next_offset() {
                return Err(BondRuntimeError::ExcessReceiveCredit {
                    stream_id,
                    consumed,
                    delivered: stream.receiver.next_offset(),
                });
            }
            stream.consumed_offset = consumed;
            stream.local_window_end = stream
                .local_window_end
                .checked_add(bytes)
                .ok_or(BondRuntimeError::OffsetOverflow)?;
            stream
                .local_window_end
                .saturating_sub(stream.last_advertised_window_end)
                >= self.config.control_batch_bytes()
        };
        if should_advertise && self.sender.scheduler().active_lane_count() > 0 {
            self.send_window_update(stream_id)?;
        }
        self.retire_stream_if_complete(stream_id).await
    }

    fn begin_stream_close(
        &mut self,
        stream_id: StreamId,
        reply: oneshot::Sender<Result<(), BondRuntimeError>>,
    ) -> Result<(), BondRuntimeError> {
        let final_offset = self.sender.next_offset(stream_id);
        let state = match self.streams.get_mut(&stream_id) {
            Some(state) => state,
            None => {
                let _ = reply.send(Err(BondRuntimeError::UnopenedStream(stream_id)));
                return Ok(());
            }
        };
        if state.local_final_offset.is_some() {
            let _ = reply.send(Err(BondRuntimeError::StreamWriteClosed(stream_id)));
            return Ok(());
        }
        state.local_final_offset = Some(final_offset);
        state.close_reply = Some(reply);
        if let Err(error) = self.send_control(
            FrameKind::StreamClose,
            FrameFlags::NONE,
            stream_id.get(),
            final_offset,
            Vec::new(),
        ) {
            if let Some(state) = self.streams.get_mut(&stream_id) {
                state.local_final_offset = None;
                if let Some(reply) = state.close_reply.take() {
                    let _ = reply.send(Err(error));
                }
            }
        }
        Ok(())
    }

    fn reset_stream(&mut self, stream_id: StreamId, code: u32) -> Result<(), BondRuntimeError> {
        if !self.streams.contains_key(&stream_id) {
            return Err(BondRuntimeError::UnopenedStream(stream_id));
        }
        self.send_control(
            FrameKind::StreamReset,
            FrameFlags::NONE,
            stream_id.get(),
            0,
            StreamReset::new(code).encode_payload().to_vec(),
        )?;
        self.streams.remove(&stream_id);
        self.pending_acknowledgements.remove(stream_id);
        if self.sender.abandon_stream(stream_id)? > 0 {
            self.notify_send_progress();
        }
        Ok(())
    }

    fn begin_session_close(
        &mut self,
        reply: oneshot::Sender<Result<(), BondRuntimeError>>,
    ) -> Result<bool, BondRuntimeError> {
        if self.shutdown_reply.is_some() {
            let _ = reply.send(Err(BondRuntimeError::SessionClosing));
            return Ok(false);
        }
        if self.sender.unacknowledged_bytes() != 0 {
            let _ = reply.send(Err(BondRuntimeError::IncompleteDelivery(
                self.sender.unacknowledged_bytes(),
            )));
            return Ok(false);
        }
        if self.config.require_stream_open
            && self.streams.values().any(|stream| {
                stream.local_final_offset.is_none()
                    || stream.close_reply.is_some()
                    || !stream.remote_finished
            })
        {
            let _ = reply.send(Err(BondRuntimeError::StreamsStillOpen));
            return Ok(false);
        }
        if self.peer_close_received {
            if self.lanes.is_empty() {
                let _ = reply.send(Ok(()));
                return Ok(true);
            }
            self.shutdown_reply = Some(reply);
            return Ok(false);
        }
        self.send_control(FrameKind::SessionClose, FrameFlags::NONE, 0, 0, Vec::new())?;
        self.local_close_requested = true;
        self.shutdown_reply = Some(reply);
        Ok(false)
    }

    fn finish_passive_shutdown_if_disconnected(&mut self) -> bool {
        if !self.peer_close_received || self.local_close_requested || !self.lanes.is_empty() {
            return false;
        }
        let Some(reply) = self.shutdown_reply.take() else {
            return false;
        };
        let _ = reply.send(Ok(()));
        true
    }

    fn finish_active_shutdown_if_complete(&mut self) -> bool {
        if !self.local_close_ack_received
            || (self.peer_close_received && self.peer_close_ack_written_lanes.is_empty())
        {
            return false;
        }
        let Some(reply) = self.shutdown_reply.take() else {
            return false;
        };
        self.lanes.clear();
        let _ = reply.send(Ok(()));
        true
    }

    async fn handle_inbound(
        &mut self,
        lane_id: LaneId,
        frame: Frame,
    ) -> Result<bool, BondRuntimeError> {
        if frame.header.session_id != self.config.session_id {
            return Err(BondRuntimeError::UnexpectedSession {
                expected: self.config.session_id,
                received: frame.header.session_id,
            });
        }
        let now = self.now();
        if let Some(liveness) = self.liveness.get_mut(&lane_id) {
            liveness.last_received_at = now;
        }
        match frame.header.kind {
            FrameKind::Data => self.handle_data(lane_id, frame).await.map(|()| false),
            FrameKind::Acknowledgement => {
                self.handle_acknowledgement(lane_id, frame).map(|()| false)
            }
            FrameKind::WindowUpdate => self.handle_window_update(frame).map(|()| false),
            FrameKind::StreamOpen => self.handle_stream_open(frame).await.map(|()| false),
            FrameKind::StreamClose => self.handle_stream_close(frame).await.map(|()| false),
            FrameKind::StreamReset => self.handle_stream_reset(frame).await.map(|()| false),
            FrameKind::EndpointAdvertisement => self
                .handle_topology_advertisement(frame)
                .await
                .map(|()| false),
            FrameKind::CapabilityAdvertisement => self
                .handle_capability_advertisement(frame)
                .await
                .map(|()| false),
            FrameKind::Ping => self.handle_ping(lane_id, frame).map(|()| false),
            FrameKind::Pong => self.handle_pong(lane_id, frame).map(|()| false),
            FrameKind::SessionClose => self.handle_session_close(frame),
            kind => Err(BondRuntimeError::UnsupportedFrame(kind)),
        }
    }

    fn handle_ping(&mut self, lane_id: LaneId, frame: Frame) -> Result<(), BondRuntimeError> {
        validate_liveness_frame(&frame, FrameKind::Ping)?;
        let pong = Frame::new(
            FrameKind::Pong,
            FrameFlags::NONE,
            self.config.session_id,
            0,
            frame.header.offset,
            Vec::new(),
        )?;
        self.send_raw(lane_id, pong)?;
        self.stats.pong_frames = self
            .stats
            .pong_frames
            .checked_add(1)
            .ok_or(BondRuntimeError::CounterOverflow)?;
        Ok(())
    }

    fn handle_pong(&mut self, lane_id: LaneId, frame: Frame) -> Result<(), BondRuntimeError> {
        validate_liveness_frame(&frame, FrameKind::Pong)?;
        let now = self.now();
        let liveness = self
            .liveness
            .get_mut(&lane_id)
            .ok_or(BondRuntimeError::LaneUnavailable(lane_id))?;
        let Some(outstanding) = liveness.outstanding_ping else {
            return Err(BondRuntimeError::MalformedControlFrame(FrameKind::Pong));
        };
        let (token, sent_at) = match outstanding {
            OutstandingPing::Queued { token } => (token, None),
            OutstandingPing::Sent { token, sent_at } => (token, Some(sent_at)),
        };
        if token != frame.header.offset {
            return Err(BondRuntimeError::MalformedControlFrame(FrameKind::Pong));
        }
        liveness.outstanding_ping = None;
        if let Some(sent_at) = sent_at {
            self.sender
                .scheduler_mut()
                .record_round_trip_time(lane_id, elapsed_since(now, sent_at))?;
        }
        Ok(())
    }

    fn check_lane_liveness(&mut self) -> Result<(), BondRuntimeError> {
        let now = self.now();
        let minimum = self.minimum_retransmit_after();
        let mut failed = Vec::new();
        let mut probes = Vec::new();
        for lane_id in self.lanes.keys().copied() {
            let retransmission_timeout = self.sender.scheduler().retransmission_timeout(
                lane_id,
                minimum,
                self.config.retransmit_after,
            )?;
            let timeout =
                bounded_liveness_timeout(retransmission_timeout, self.config.retransmit_after);
            let probe_interval = (timeout / 2).min(MAXIMUM_LIVENESS_PROBE_INTERVAL);
            let state = self
                .liveness
                .get(&lane_id)
                .ok_or(BondRuntimeError::LaneUnavailable(lane_id))?;
            if let Some(sent_at) = state.response_deadline_started_at() {
                if now
                    .duration_since(sent_at)
                    .is_some_and(|age| age >= timeout)
                {
                    failed.push(lane_id);
                }
            } else if !state.has_outstanding_probe()
                && now
                    .duration_since(state.last_received_at)
                    .is_some_and(|idle| idle >= probe_interval)
            {
                probes.push(lane_id);
            }
        }

        for lane_id in failed {
            self.stats.liveness_failures = self
                .stats
                .liveness_failures
                .checked_add(1)
                .ok_or(BondRuntimeError::CounterOverflow)?;
            let frames = self.fail_lane_internal(lane_id)?;
            self.dispatch_scheduled(frames)?;
        }
        for lane_id in probes {
            let token = self.next_ping_token;
            self.next_ping_token = self
                .next_ping_token
                .checked_add(1)
                .ok_or(BondRuntimeError::CounterOverflow)?;
            let ping = Frame::new(
                FrameKind::Ping,
                FrameFlags::NONE,
                self.config.session_id,
                0,
                token,
                Vec::new(),
            )?;
            self.send_raw(lane_id, ping)?;
            self.liveness
                .get_mut(&lane_id)
                .ok_or(BondRuntimeError::LaneUnavailable(lane_id))?
                .queue_ping(token);
            self.stats.ping_frames = self
                .stats
                .ping_frames
                .checked_add(1)
                .ok_or(BondRuntimeError::CounterOverflow)?;
        }
        Ok(())
    }

    fn minimum_retransmit_after(&self) -> Duration {
        MINIMUM_ADAPTIVE_RTO.min(self.config.retransmit_after)
    }

    fn advertise_topology(
        &mut self,
        advertisement: TopologyAdvertisement,
    ) -> Result<(), BondRuntimeError> {
        if advertisement.generation <= self.local_topology_generation {
            return Err(BondRuntimeError::RegressingTopologyGeneration {
                previous: self.local_topology_generation,
                received: advertisement.generation,
            });
        }
        let generation = advertisement.generation;
        let payload = advertisement.encode_payload()?;
        self.send_control(
            FrameKind::EndpointAdvertisement,
            FrameFlags::NONE,
            0,
            generation,
            payload,
        )?;
        self.local_topology_generation = generation;
        self.local_topology = Some(advertisement);
        Ok(())
    }

    async fn handle_topology_advertisement(
        &mut self,
        frame: Frame,
    ) -> Result<(), BondRuntimeError> {
        if frame.header.stream_id != 0 {
            return Err(BondRuntimeError::MalformedControlFrame(
                FrameKind::EndpointAdvertisement,
            ));
        }
        let advertisement = TopologyAdvertisement::decode_payload(&frame.payload)?;
        if frame.header.offset != advertisement.generation {
            return Err(BondRuntimeError::TopologyGenerationMismatch {
                header: frame.header.offset,
                payload: advertisement.generation,
            });
        }
        if advertisement.generation < self.remote_topology_generation {
            return Ok(());
        }
        if advertisement.generation == self.remote_topology_generation {
            return match &self.remote_topology {
                Some(previous) if previous == &advertisement => Ok(()),
                _ => Err(BondRuntimeError::ConflictingTopologyReplay(
                    advertisement.generation,
                )),
            };
        }
        self.remote_topology_generation = advertisement.generation;
        self.remote_topology = Some(advertisement.clone());
        self.output_tx
            .send(RuntimeEvent::TopologyAdvertised(advertisement))
            .await
            .map_err(|_| BondRuntimeError::ApplicationReceiverClosed)
    }

    fn advertise_capabilities(
        &mut self,
        advertisement: CapabilityAdvertisement,
    ) -> Result<(), BondRuntimeError> {
        if self.protocol_version < BondProtocolVersion::V4 {
            return Err(BondRuntimeError::CapabilitiesRequireProtocolV4);
        }
        if advertisement.generation <= self.local_capability_generation {
            return Err(BondRuntimeError::RegressingCapabilityGeneration {
                previous: self.local_capability_generation,
                received: advertisement.generation,
            });
        }
        let generation = advertisement.generation;
        let payload = advertisement.encode_payload()?;
        self.send_control(
            FrameKind::CapabilityAdvertisement,
            FrameFlags::NONE,
            0,
            generation,
            payload,
        )?;
        self.local_capability_generation = generation;
        self.local_capabilities = Some(advertisement);
        Ok(())
    }

    async fn handle_capability_advertisement(
        &mut self,
        frame: Frame,
    ) -> Result<(), BondRuntimeError> {
        if self.protocol_version < BondProtocolVersion::V4 {
            return Err(BondRuntimeError::CapabilitiesRequireProtocolV4);
        }
        if frame.header.stream_id != 0 {
            return Err(BondRuntimeError::MalformedControlFrame(
                FrameKind::CapabilityAdvertisement,
            ));
        }
        let advertisement = CapabilityAdvertisement::decode_payload(&frame.payload)?;
        if frame.header.offset != advertisement.generation {
            return Err(BondRuntimeError::CapabilityGenerationMismatch {
                header: frame.header.offset,
                payload: advertisement.generation,
            });
        }
        if advertisement.generation < self.remote_capability_generation {
            return Ok(());
        }
        if advertisement.generation == self.remote_capability_generation {
            return match &self.remote_capabilities {
                Some(previous) if previous == &advertisement => Ok(()),
                _ => Err(BondRuntimeError::ConflictingCapabilityReplay(
                    advertisement.generation,
                )),
            };
        }
        self.remote_capability_generation = advertisement.generation;
        self.remote_capabilities = Some(advertisement.clone());
        self.output_tx
            .send(RuntimeEvent::CapabilitiesAdvertised(advertisement))
            .await
            .map_err(|_| BondRuntimeError::ApplicationReceiverClosed)
    }

    async fn handle_data(&mut self, lane_id: LaneId, frame: Frame) -> Result<(), BondRuntimeError> {
        let stream_id = StreamId::new(frame.header.stream_id)?;
        if let Some(retired) = self.retired_streams.get(&stream_id).copied() {
            let frame_end = frame
                .header
                .offset
                .checked_add(frame.payload.len() as u64)
                .ok_or(BondRuntimeError::OffsetOverflow)?;
            if frame_end > retired.remote_final_offset {
                return Err(BondRuntimeError::InvalidFinalOffset {
                    stream_id,
                    received: frame_end,
                    delivered: retired.remote_final_offset,
                });
            }
            return self.send_retired_acknowledgement(stream_id, retired.remote_final_offset);
        }
        if self.is_evicted_retired_stream(stream_id) {
            return Ok(());
        }
        if !self.streams.contains_key(&stream_id) {
            if self.config.require_stream_open {
                return Err(BondRuntimeError::UnopenedStream(stream_id));
            }
            if self.streams.len() >= self.config.max_receive_streams {
                return Err(BondRuntimeError::ReceiveStreamLimitExceeded(
                    self.config.max_receive_streams,
                ));
            }
            let window = self.receive_window()?;
            self.streams.insert(
                stream_id,
                StreamState::new(
                    TrafficClass::Bulk,
                    false,
                    self.config.max_reorder_bytes_per_stream,
                    window,
                    Some(u64::MAX),
                )?,
            );
        }
        let frame_end = frame
            .header
            .offset
            .checked_add(frame.payload.len() as u64)
            .ok_or(BondRuntimeError::OffsetOverflow)?;
        let acknowledge_on_arrival_lane = self.protocol_version >= BondProtocolVersion::V3
            && self
                .streams
                .get(&stream_id)
                .expect("stream exists")
                .class
                .is_redundant_realtime_candidate(frame.payload.len());
        let acknowledgement_batch_bytes = self.config.control_batch_bytes();
        let (delivery, remote_final, acknowledge_immediately, queue_acknowledgement) = {
            let stream = self.streams.get_mut(&stream_id).expect("stream exists");
            if frame_end > stream.local_window_end {
                return Err(BondRuntimeError::FlowControlExceeded {
                    stream_id,
                    received: frame_end,
                    limit: stream.local_window_end,
                });
            }
            let delivery = stream
                .receiver
                .insert_shared(frame.header.offset, frame.payload)?;
            let range_count = stream
                .receiver
                .acknowledgement_range_count(self.config.max_ack_ranges);
            stream.unacknowledged_received_bytes = stream
                .unacknowledged_received_bytes
                .checked_add(
                    u64::try_from(delivery.accepted_bytes)
                        .map_err(|_| BondRuntimeError::CounterOverflow)?,
                )
                .ok_or(BondRuntimeError::CounterOverflow)?;
            stream.acknowledgement_pending = true;
            let acknowledge_immediately = acknowledge_on_arrival_lane
                || delivery.accepted_bytes == 0
                || range_count != stream.last_acknowledged_range_count
                || stream.unacknowledged_received_bytes >= acknowledgement_batch_bytes;
            let queue_acknowledgement = !acknowledge_immediately && !stream.acknowledgement_queued;
            if queue_acknowledgement {
                stream.acknowledgement_queued = true;
            }
            (
                delivery,
                stream.remote_final_offset,
                acknowledge_immediately,
                queue_acknowledgement,
            )
        };
        self.stats.reorder_high_water = self
            .stats
            .reorder_high_water
            .max(delivery.reorder_high_water);
        if delivery.accepted_bytes > 0 {
            let counters = self
                .received_by_lane
                .get_mut(&lane_id)
                .ok_or(BondRuntimeError::LaneUnavailable(lane_id))?;
            counters.unique_data_bytes = counters
                .unique_data_bytes
                .checked_add(delivery.accepted_bytes as u64)
                .ok_or(BondRuntimeError::CounterOverflow)?;
            counters.unique_data_frames = counters
                .unique_data_frames
                .checked_add(1)
                .ok_or(BondRuntimeError::CounterOverflow)?;
        }

        if queue_acknowledgement {
            self.pending_acknowledgements.queue(stream_id);
        } else if acknowledge_immediately {
            if acknowledge_on_arrival_lane {
                self.send_acknowledgement_on(stream_id, lane_id)?;
            } else {
                self.send_acknowledgement(stream_id)?;
            }
        }

        if !delivery.bytes.is_empty() {
            self.stats.delivered_bytes = self
                .stats
                .delivered_bytes
                .checked_add(delivery.bytes.len() as u64)
                .ok_or(BondRuntimeError::CounterOverflow)?;
            self.output_tx
                .send(RuntimeEvent::Data(ReceivedData {
                    stream_id,
                    bytes: delivery.bytes,
                }))
                .await
                .map_err(|_| BondRuntimeError::ApplicationReceiverClosed)?;
        }
        if remote_final == Some(delivery.next_offset) {
            self.finish_remote_stream(stream_id).await?;
        }
        Ok(())
    }

    fn handle_acknowledgement(
        &mut self,
        lane_id: LaneId,
        frame: Frame,
    ) -> Result<(), BondRuntimeError> {
        let stream_id = StreamId::new(frame.header.stream_id)?;
        if let Some(retired) = self.retired_streams.get(&stream_id).copied() {
            SelectiveAcknowledgement::decode_payload_into(
                frame.header.offset,
                &frame.payload,
                &mut self.acknowledgement_ranges,
            )?;
            let received = self
                .acknowledgement_ranges
                .last()
                .map_or(frame.header.offset, |range| range.end);
            if received > retired.local_final_offset {
                return Err(SenderError::InvalidAcknowledgement {
                    previous: retired.local_final_offset,
                    received,
                    sent: retired.local_final_offset,
                }
                .into());
            }
            return Ok(());
        }
        SelectiveAcknowledgement::decode_payload_into(
            frame.header.offset,
            &frame.payload,
            &mut self.acknowledgement_ranges,
        )?;
        if self.is_evicted_retired_stream(stream_id) {
            return Ok(());
        }
        if !self.streams.contains_key(&stream_id) {
            return Err(BondRuntimeError::UnopenedStream(stream_id));
        }
        let now = self.now();
        self.sender.acknowledge_selective_from_lane_into(
            stream_id,
            frame.header.offset,
            &self.acknowledgement_ranges,
            lane_id,
            &mut self.acknowledged_chunks,
        )?;
        self.record_acknowledgement(now)
    }

    fn record_acknowledgement(&mut self, now: Timestamp) -> Result<(), BondRuntimeError> {
        let cohorts = DeliveryCohorts::from_chunks(&self.acknowledged_chunks)?;
        let mut samples = [None; MAX_RUNTIME_LANES];
        for (index, cohort) in cohorts.iter().enumerate() {
            let previous_delivery_at = self
                .delivery_history
                .previous_and_record(cohort.lane_id, now)?;
            samples[index] = Some((cohort.lane_id, cohort.sample(now, previous_delivery_at)?));
        }
        self.sender
            .scheduler_mut()
            .record_deliveries(samples.into_iter().flatten())?;
        if !self.acknowledged_chunks.is_empty() {
            self.notify_send_progress();
        }
        Ok(())
    }

    fn flush_pending_acknowledgements(&mut self) -> Result<(), BondRuntimeError> {
        if self.sender.scheduler().active_lane_count() == 0 {
            self.pending_acknowledgements.defer_until_lane_returns();
            return Ok(());
        }
        while let Some(stream_id) = self.pending_acknowledgements.pop() {
            let pending = match self.streams.get_mut(&stream_id) {
                Some(stream) => {
                    stream.acknowledgement_queued = false;
                    stream.acknowledgement_pending
                }
                None => false,
            };
            if pending {
                self.send_acknowledgement(stream_id)?;
            }
        }
        Ok(())
    }

    fn prepare_control_replay(&mut self) -> Result<(), BondRuntimeError> {
        let mut replay = VecDeque::new();
        if self.config.require_stream_open {
            for (stream_id, stream) in &self.streams {
                if stream.open_reply.is_some() {
                    replay.push_back(Frame::new(
                        FrameKind::StreamOpen,
                        FrameFlags::NONE,
                        self.config.session_id,
                        stream_id.get(),
                        0,
                        StreamOpen::new(stream.class, stream.initial_local_window_end)?
                            .encode_payload()
                            .to_vec(),
                    )?);
                    continue;
                }
                if !stream.opened_locally {
                    replay.push_back(Frame::new(
                        FrameKind::StreamOpen,
                        FrameFlags::ACKNOWLEDGEMENT,
                        self.config.session_id,
                        stream_id.get(),
                        0,
                        StreamOpen::new(stream.class, stream.initial_local_window_end)?
                            .encode_payload()
                            .to_vec(),
                    )?);
                }
                if !stream.remote_finished {
                    replay.push_back(Frame::new(
                        FrameKind::WindowUpdate,
                        FrameFlags::NONE,
                        self.config.session_id,
                        stream_id.get(),
                        stream.local_window_end,
                        Vec::new(),
                    )?);
                }
                if let Some(final_offset) =
                    stream.close_reply.as_ref().and(stream.local_final_offset)
                {
                    replay.push_back(Frame::new(
                        FrameKind::StreamClose,
                        FrameFlags::NONE,
                        self.config.session_id,
                        stream_id.get(),
                        final_offset,
                        Vec::new(),
                    )?);
                }
                if stream.remote_finished {
                    let final_offset = stream
                        .remote_final_offset
                        .expect("finished remote stream has a final offset");
                    replay.push_back(Frame::new(
                        FrameKind::StreamClose,
                        FrameFlags::ACKNOWLEDGEMENT,
                        self.config.session_id,
                        stream_id.get(),
                        final_offset,
                        Vec::new(),
                    )?);
                }
            }
            for (stream_id, stream) in &self.retired_streams {
                replay.push_back(Frame::new(
                    FrameKind::StreamClose,
                    FrameFlags::ACKNOWLEDGEMENT,
                    self.config.session_id,
                    stream_id.get(),
                    stream.remote_final_offset,
                    Vec::new(),
                )?);
            }
        }
        if let Some(advertisement) = &self.local_topology {
            replay.push_back(Frame::new(
                FrameKind::EndpointAdvertisement,
                FrameFlags::NONE,
                self.config.session_id,
                0,
                advertisement.generation,
                advertisement.encode_payload()?,
            )?);
        }
        if let Some(advertisement) = &self.local_capabilities {
            replay.push_back(Frame::new(
                FrameKind::CapabilityAdvertisement,
                FrameFlags::NONE,
                self.config.session_id,
                0,
                advertisement.generation,
                advertisement.encode_payload()?,
            )?);
        }
        if self.local_close_requested && self.shutdown_reply.is_some() {
            replay.push_back(Frame::new(
                FrameKind::SessionClose,
                FrameFlags::NONE,
                self.config.session_id,
                0,
                0,
                Vec::new(),
            )?);
        }
        if self.peer_close_received {
            replay.push_back(Frame::new(
                FrameKind::SessionClose,
                FrameFlags::ACKNOWLEDGEMENT,
                self.config.session_id,
                0,
                0,
                Vec::new(),
            )?);
        }
        self.control_replay = replay;
        Ok(())
    }

    fn flush_control_replay(&mut self) -> Result<(), BondRuntimeError> {
        while let Some(frame) = self.control_replay.front().cloned() {
            match self.send_control_frame(frame) {
                Ok(()) => {
                    self.control_replay.pop_front();
                    self.stats.replayed_control_frames = self
                        .stats
                        .replayed_control_frames
                        .checked_add(1)
                        .ok_or(BondRuntimeError::CounterOverflow)?;
                }
                Err(BondRuntimeError::LaneQueueFull(_))
                | Err(BondRuntimeError::Scheduler(SchedulerError::NoHealthyLane)) => return Ok(()),
                Err(BondRuntimeError::LaneUnavailable(lane_id)) => {
                    let frames = self.fail_lane_internal(lane_id)?;
                    self.dispatch_scheduled(frames)?;
                }
                Err(error) => return Err(error),
            }
        }
        Ok(())
    }

    fn send_acknowledgement(&mut self, stream_id: StreamId) -> Result<(), BondRuntimeError> {
        self.send_acknowledgement_via(stream_id, None)
    }

    fn send_acknowledgement_on(
        &mut self,
        stream_id: StreamId,
        lane_id: LaneId,
    ) -> Result<(), BondRuntimeError> {
        self.send_acknowledgement_via(stream_id, Some(lane_id))
    }

    fn send_acknowledgement_via(
        &mut self,
        stream_id: StreamId,
        lane_id: Option<LaneId>,
    ) -> Result<(), BondRuntimeError> {
        let next_offset = {
            let stream = self
                .streams
                .get(&stream_id)
                .ok_or(BondRuntimeError::UnopenedStream(stream_id))?;
            stream.receiver.acknowledgement_ranges_into(
                self.config.max_ack_ranges,
                &mut self.acknowledgement_ranges,
            );
            stream.receiver.next_offset()
        };
        let range_count = self.acknowledgement_ranges.len();
        let frame = Frame::new(
            FrameKind::Acknowledgement,
            FrameFlags::NONE,
            self.config.session_id,
            stream_id.get(),
            next_offset,
            SelectiveAcknowledgement::encode_payload_shared_parts(
                next_offset,
                &self.acknowledgement_ranges,
            )?,
        )?;
        if let Some(lane_id) = lane_id {
            if let Err(error) = self.send_raw(lane_id, frame.clone()) {
                match error {
                    BondRuntimeError::LaneQueueFull(_) | BondRuntimeError::LaneUnavailable(_) => {
                        self.send_control_frame(frame)?
                    }
                    error => return Err(error),
                }
            }
        } else {
            self.send_control_frame(frame)?;
        }
        let stream = self
            .streams
            .get_mut(&stream_id)
            .expect("acknowledged stream exists");
        stream.unacknowledged_received_bytes = 0;
        stream.last_acknowledged_range_count = range_count;
        stream.acknowledgement_pending = false;
        self.stats.acknowledgement_frames = self
            .stats
            .acknowledgement_frames
            .checked_add(1)
            .ok_or(BondRuntimeError::CounterOverflow)?;
        Ok(())
    }

    fn send_window_update(&mut self, stream_id: StreamId) -> Result<(), BondRuntimeError> {
        let new_window = self
            .streams
            .get(&stream_id)
            .ok_or(BondRuntimeError::UnopenedStream(stream_id))?
            .local_window_end;
        self.send_control(
            FrameKind::WindowUpdate,
            FrameFlags::NONE,
            stream_id.get(),
            new_window,
            Vec::new(),
        )?;
        self.streams
            .get_mut(&stream_id)
            .expect("updated stream exists")
            .last_advertised_window_end = new_window;
        self.stats.window_update_frames = self
            .stats
            .window_update_frames
            .checked_add(1)
            .ok_or(BondRuntimeError::CounterOverflow)?;
        Ok(())
    }

    fn handle_window_update(&mut self, frame: Frame) -> Result<(), BondRuntimeError> {
        if !frame.payload.is_empty() || frame.header.flags != FrameFlags::NONE {
            return Err(BondRuntimeError::MalformedControlFrame(
                FrameKind::WindowUpdate,
            ));
        }
        let stream_id = StreamId::new(frame.header.stream_id)?;
        if self.retired_streams.contains_key(&stream_id) {
            return Ok(());
        }
        if self.is_evicted_retired_stream(stream_id) {
            return Ok(());
        }
        let stream = self
            .streams
            .get_mut(&stream_id)
            .ok_or(BondRuntimeError::UnopenedStream(stream_id))?;
        if frame.header.offset <= stream.remote_window_end {
            // Absolute credit updates can reorder across bonded lanes. A stale
            // authenticated update cannot revoke credit, so it is idempotent.
            return Ok(());
        }
        stream.remote_window_end = frame.header.offset;
        self.notify_send_progress();
        Ok(())
    }

    async fn handle_stream_open(&mut self, frame: Frame) -> Result<(), BondRuntimeError> {
        if frame.header.offset != 0 {
            return Err(BondRuntimeError::MalformedControlFrame(
                FrameKind::StreamOpen,
            ));
        }
        let stream_id = StreamId::new(frame.header.stream_id)?;
        let open = StreamOpen::decode_payload(&frame.payload)?;
        if let Some(retired) = self.retired_streams.get(&stream_id).copied() {
            return self.handle_retired_stream_open(stream_id, open, frame.header.flags, retired);
        }
        if self.is_evicted_retired_stream(stream_id) {
            return Ok(());
        }
        if frame.header.flags.contains(FrameFlags::ACKNOWLEDGEMENT) {
            let stream = self
                .streams
                .get_mut(&stream_id)
                .ok_or(BondRuntimeError::UnopenedStream(stream_id))?;
            if !stream.opened_locally
                || stream.class != open.class
                || stream
                    .initial_remote_window_end
                    .is_some_and(|initial| initial != open.receive_window_end)
            {
                return Err(BondRuntimeError::UnexpectedStreamOpenAcknowledgement(
                    stream_id,
                ));
            }
            stream.initial_remote_window_end = Some(open.receive_window_end);
            stream.remote_window_end = stream.remote_window_end.max(open.receive_window_end);
            if let Some(reply) = stream.open_reply.take() {
                let _ = reply.send(Ok(()));
            }
            return Ok(());
        }
        if let Some(stream) = self.streams.get(&stream_id) {
            if stream.opened_locally
                || stream.class != open.class
                || stream.initial_remote_window_end != Some(open.receive_window_end)
            {
                return Err(BondRuntimeError::DuplicateStream(stream_id));
            }
            return self.send_control(
                FrameKind::StreamOpen,
                FrameFlags::ACKNOWLEDGEMENT,
                stream_id.get(),
                0,
                StreamOpen::new(stream.class, stream.initial_local_window_end)?
                    .encode_payload()
                    .to_vec(),
            );
        }
        if self.streams.len() >= self.config.max_receive_streams {
            return Err(BondRuntimeError::ReceiveStreamLimitExceeded(
                self.config.max_receive_streams,
            ));
        }
        let local_window = self.receive_window()?;
        self.streams.insert(
            stream_id,
            StreamState::new(
                open.class,
                false,
                self.config.max_reorder_bytes_per_stream,
                local_window,
                Some(open.receive_window_end),
            )?,
        );
        self.send_control(
            FrameKind::StreamOpen,
            FrameFlags::ACKNOWLEDGEMENT,
            stream_id.get(),
            0,
            StreamOpen::new(open.class, local_window)?
                .encode_payload()
                .to_vec(),
        )?;
        self.output_tx
            .send(RuntimeEvent::StreamOpened {
                stream_id,
                class: open.class,
            })
            .await
            .map_err(|_| BondRuntimeError::ApplicationReceiverClosed)
    }

    async fn handle_stream_close(&mut self, frame: Frame) -> Result<(), BondRuntimeError> {
        if !frame.payload.is_empty() {
            return Err(BondRuntimeError::MalformedControlFrame(
                FrameKind::StreamClose,
            ));
        }
        let stream_id = StreamId::new(frame.header.stream_id)?;
        if let Some(retired) = self.retired_streams.get(&stream_id).copied() {
            return self.handle_retired_stream_close(stream_id, frame, retired);
        }
        if self.is_evicted_retired_stream(stream_id) {
            return Ok(());
        }
        if frame.header.flags.contains(FrameFlags::ACKNOWLEDGEMENT) {
            let state = self
                .streams
                .get(&stream_id)
                .ok_or(BondRuntimeError::UnopenedStream(stream_id))?;
            if state.local_final_offset != Some(frame.header.offset) {
                return Err(BondRuntimeError::UnexpectedStreamCloseAcknowledgement(
                    stream_id,
                ));
            }
            if state.close_reply.is_none() {
                return Ok(());
            }
            let now = self.now();
            self.sender.acknowledge_into(
                stream_id,
                frame.header.offset,
                &mut self.acknowledged_chunks,
            )?;
            self.record_acknowledgement(now)?;
            let reply = self
                .streams
                .get_mut(&stream_id)
                .expect("validated stream exists")
                .close_reply
                .take()
                .expect("validated close reply exists");
            let _ = reply.send(Ok(()));
            self.retire_stream_if_complete(stream_id).await?;
            return Ok(());
        }

        let complete = {
            let state = self
                .streams
                .get_mut(&stream_id)
                .ok_or(BondRuntimeError::UnopenedStream(stream_id))?;
            if let Some(final_offset) = state.remote_final_offset {
                if final_offset != frame.header.offset {
                    return Err(BondRuntimeError::DuplicateStreamClose(stream_id));
                }
                if state.remote_finished {
                    self.send_stream_close_ack(stream_id, final_offset)?;
                }
                return Ok(());
            }
            if frame.header.offset < state.receiver.next_offset()
                || state
                    .receiver
                    .highest_buffered_end()?
                    .is_some_and(|end| end > frame.header.offset)
            {
                return Err(BondRuntimeError::InvalidFinalOffset {
                    stream_id,
                    received: frame.header.offset,
                    delivered: state.receiver.next_offset(),
                });
            }
            state.remote_final_offset = Some(frame.header.offset);
            state.receiver.next_offset() == frame.header.offset
        };
        if complete {
            self.finish_remote_stream(stream_id).await?;
        }
        Ok(())
    }

    async fn finish_remote_stream(&mut self, stream_id: StreamId) -> Result<(), BondRuntimeError> {
        let final_offset = {
            let state = self
                .streams
                .get_mut(&stream_id)
                .ok_or(BondRuntimeError::UnopenedStream(stream_id))?;
            if state.remote_finished {
                return Ok(());
            }
            let final_offset = state.remote_final_offset.ok_or(
                BondRuntimeError::UnexpectedStreamCloseAcknowledgement(stream_id),
            )?;
            if state.receiver.next_offset() != final_offset {
                return Ok(());
            }
            state.remote_finished = true;
            state.unacknowledged_received_bytes = 0;
            state.last_acknowledged_range_count = 0;
            state.acknowledgement_pending = false;
            final_offset
        };
        self.output_tx
            .send(RuntimeEvent::StreamFinished { stream_id })
            .await
            .map_err(|_| BondRuntimeError::ApplicationReceiverClosed)?;
        self.send_stream_close_ack(stream_id, final_offset)?;
        self.retire_stream_if_complete(stream_id).await
    }

    fn send_stream_close_ack(
        &mut self,
        stream_id: StreamId,
        final_offset: u64,
    ) -> Result<(), BondRuntimeError> {
        self.send_control(
            FrameKind::StreamClose,
            FrameFlags::ACKNOWLEDGEMENT,
            stream_id.get(),
            final_offset,
            Vec::new(),
        )
    }

    async fn handle_stream_reset(&mut self, frame: Frame) -> Result<(), BondRuntimeError> {
        if frame.header.flags != FrameFlags::NONE || frame.header.offset != 0 {
            return Err(BondRuntimeError::MalformedControlFrame(
                FrameKind::StreamReset,
            ));
        }
        let stream_id = StreamId::new(frame.header.stream_id)?;
        let reset = StreamReset::decode_payload(&frame.payload)?;
        if self.retired_streams.contains_key(&stream_id) {
            return Ok(());
        }
        if self.is_evicted_retired_stream(stream_id) {
            return Ok(());
        }
        if self.streams.remove(&stream_id).is_none() {
            return Err(BondRuntimeError::UnopenedStream(stream_id));
        }
        self.pending_acknowledgements.remove(stream_id);
        if self.sender.abandon_stream(stream_id)? > 0 {
            self.notify_send_progress();
        }
        self.output_tx
            .send(RuntimeEvent::StreamReset {
                stream_id,
                code: reset.code,
            })
            .await
            .map_err(|_| BondRuntimeError::ApplicationReceiverClosed)
    }

    fn handle_retired_stream_open(
        &mut self,
        stream_id: StreamId,
        open: StreamOpen,
        flags: FrameFlags,
        retired: RetiredStreamState,
    ) -> Result<(), BondRuntimeError> {
        let acknowledgement = flags.contains(FrameFlags::ACKNOWLEDGEMENT);
        if acknowledgement != retired.opened_locally
            || open.class != retired.class
            || open.receive_window_end != retired.initial_remote_window_end
        {
            return if acknowledgement {
                Err(BondRuntimeError::UnexpectedStreamOpenAcknowledgement(
                    stream_id,
                ))
            } else {
                Err(BondRuntimeError::DuplicateStream(stream_id))
            };
        }
        if acknowledgement {
            return Ok(());
        }
        self.send_control(
            FrameKind::StreamOpen,
            FrameFlags::ACKNOWLEDGEMENT,
            stream_id.get(),
            0,
            StreamOpen::new(retired.class, retired.initial_local_window_end)?
                .encode_payload()
                .to_vec(),
        )
    }

    fn handle_retired_stream_close(
        &mut self,
        stream_id: StreamId,
        frame: Frame,
        retired: RetiredStreamState,
    ) -> Result<(), BondRuntimeError> {
        if frame.header.flags.contains(FrameFlags::ACKNOWLEDGEMENT) {
            if frame.header.offset != retired.local_final_offset {
                return Err(BondRuntimeError::UnexpectedStreamCloseAcknowledgement(
                    stream_id,
                ));
            }
            return Ok(());
        }
        if frame.header.offset != retired.remote_final_offset {
            return Err(BondRuntimeError::DuplicateStreamClose(stream_id));
        }
        self.send_stream_close_ack(stream_id, retired.remote_final_offset)
    }

    fn send_retired_acknowledgement(
        &mut self,
        stream_id: StreamId,
        final_offset: u64,
    ) -> Result<(), BondRuntimeError> {
        let frame = Frame::new(
            FrameKind::Acknowledgement,
            FrameFlags::NONE,
            self.config.session_id,
            stream_id.get(),
            final_offset,
            SelectiveAcknowledgement::encode_payload_shared_parts(final_offset, &[])?,
        )?;
        self.send_control_frame(frame)?;
        self.stats.acknowledgement_frames = self
            .stats
            .acknowledgement_frames
            .checked_add(1)
            .ok_or(BondRuntimeError::CounterOverflow)?;
        Ok(())
    }

    async fn retire_stream_if_complete(
        &mut self,
        stream_id: StreamId,
    ) -> Result<(), BondRuntimeError> {
        let complete = self.streams.get(&stream_id).is_some_and(|state| {
            state.open_reply.is_none()
                && state.local_final_offset.is_some()
                && state.close_reply.is_none()
                && state.remote_finished
                && state.remote_final_offset == Some(state.consumed_offset)
        });
        if !complete {
            return Ok(());
        }
        let state = self
            .streams
            .remove(&stream_id)
            .expect("completed stream remains live until retirement");
        self.pending_acknowledgements.remove(stream_id);
        let retired = RetiredStreamState::from_finished(&state);
        if self.sender.abandon_stream(stream_id)? > 0 {
            self.notify_send_progress();
        }
        self.retired_streams.insert(stream_id, retired);
        self.retired_stream_order.push_back(stream_id);
        while self.retired_stream_order.len() > self.config.max_receive_streams {
            let evicted = self
                .retired_stream_order
                .pop_front()
                .expect("oversized retired stream queue is non-empty");
            self.retired_streams
                .remove(&evicted)
                .expect("retired stream order references a tombstone");
            let parity = (evicted.get() & 1) as usize;
            self.retired_stream_watermarks[parity] =
                self.retired_stream_watermarks[parity].max(evicted.get());
        }
        self.output_tx
            .send(RuntimeEvent::StreamRetired { stream_id })
            .await
            .map_err(|_| BondRuntimeError::ApplicationReceiverClosed)
    }

    fn handle_session_close(&mut self, frame: Frame) -> Result<bool, BondRuntimeError> {
        if frame.header.stream_id != 0 || frame.header.offset != 0 || !frame.payload.is_empty() {
            return Err(BondRuntimeError::MalformedControlFrame(
                FrameKind::SessionClose,
            ));
        }
        if frame.header.flags.contains(FrameFlags::ACKNOWLEDGEMENT) {
            if !self.local_close_requested {
                return Err(BondRuntimeError::UnexpectedSessionCloseAcknowledgement);
            }
            if self.shutdown_reply.is_none() {
                return Err(BondRuntimeError::UnexpectedSessionCloseAcknowledgement);
            }
            self.local_close_ack_received = true;
            return Ok(self.finish_active_shutdown_if_complete());
        }
        self.send_control(
            FrameKind::SessionClose,
            FrameFlags::ACKNOWLEDGEMENT,
            0,
            0,
            Vec::new(),
        )?;
        self.peer_close_received = true;
        Ok(false)
    }

    fn send_control(
        &mut self,
        kind: FrameKind,
        flags: FrameFlags,
        stream_id: u64,
        offset: u64,
        payload: Vec<u8>,
    ) -> Result<(), BondRuntimeError> {
        let frame = Frame::new(
            kind,
            flags,
            self.config.session_id,
            stream_id,
            offset,
            payload,
        )?;
        self.send_control_frame(frame)
    }

    fn send_control_frame(&mut self, frame: Frame) -> Result<(), BondRuntimeError> {
        let bytes = HEADER_LEN
            .checked_add(frame.payload.len())
            .ok_or(BondRuntimeError::QueueCapacityOverflow)?;
        let now = self.now();
        let decision = self
            .sender
            .scheduler_mut()
            .schedule(TrafficClass::Control, bytes, now)?;
        self.send_raw(decision.lane_id, frame)
    }

    fn receive_window(&self) -> Result<u64, BondRuntimeError> {
        u64::try_from(self.config.stream_receive_window)
            .map_err(|_| BondRuntimeError::OffsetOverflow)
    }

    fn fail_lane_internal(
        &mut self,
        lane_id: LaneId,
    ) -> Result<Vec<ScheduledFrame>, BondRuntimeError> {
        if self.lanes.remove(&lane_id).is_none() {
            return Ok(Vec::new());
        }
        self.liveness.remove(&lane_id);
        self.peer_close_ack_written_lanes.remove(&lane_id);
        let frames = self.sender.fail_lane(lane_id, self.now())?;
        self.prepare_control_replay()?;
        Ok(frames)
    }

    fn add_lane_internal(
        &mut self,
        lane: RuntimeLane,
    ) -> Result<Vec<ScheduledFrame>, BondRuntimeError> {
        let lane_id = lane.config.id;
        if lane.protocol_version != self.protocol_version {
            return Err(BondRuntimeError::LaneProtocolVersionMismatch {
                expected: self.protocol_version,
                actual: lane.protocol_version,
            });
        }
        if lane.server_incarnation != self.server_incarnation {
            return Err(BondRuntimeError::LaneServerIncarnationMismatch {
                expected: self.server_incarnation,
                actual: lane.server_incarnation,
            });
        }
        if !self.lane_ids.contains(&lane_id) {
            return Err(BondRuntimeError::UndeclaredLane(lane_id));
        }
        if self.lanes.contains_key(&lane_id) {
            return Err(BondRuntimeError::LaneAlreadyActive(lane_id));
        }
        let generation = self.next_lane_generation;
        let next_generation = self
            .next_lane_generation
            .checked_add(1)
            .ok_or(BondRuntimeError::LaneGenerationExhausted)?;
        let now = self.now();
        let stranded = self.sender.restore_lane(lane.config, now)?;
        self.next_lane_generation = next_generation;
        self.lanes.insert(
            lane_id,
            spawn_lane(
                lane_id,
                generation,
                lane.io,
                lane.record_keys,
                self.event_tx.clone(),
                self.lane_queue_capacities,
                self.config.retransmit_after,
            ),
        );
        self.liveness.insert(lane_id, LaneLiveness::new(now));
        self.prepare_control_replay()?;
        self.notify_send_progress();
        Ok(stranded)
    }

    fn declare_lane_internal(&mut self, config: LaneConfig) -> Result<(), BondRuntimeError> {
        if self.lane_ids.contains(&config.id) {
            return Err(BondRuntimeError::LaneAlreadyDeclared(config.id));
        }
        if self.lane_ids.len() >= MAX_RUNTIME_LANES {
            return Err(BondRuntimeError::LaneLimitExceeded(MAX_RUNTIME_LANES));
        }
        let now = self.now();
        self.sender.scheduler_mut().add_lane(config)?;
        self.sender
            .scheduler_mut()
            .set_lane_active(config.id, false, now)?;
        self.lane_ids.insert(config.id);
        self.received_by_lane
            .insert(config.id, LaneReceiveCounters::default());
        Ok(())
    }

    fn is_current_lane(&self, lane_id: LaneId, generation: u64) -> bool {
        self.lanes
            .get(&lane_id)
            .is_some_and(|lane| lane.generation == generation)
    }

    fn dispatch_scheduled(&mut self, frames: Vec<ScheduledFrame>) -> Result<(), BondRuntimeError> {
        debug_assert!(self.dispatch_queue.is_empty());
        self.dispatch_queue.extend(frames);
        self.dispatch_queued()
    }

    fn dispatch_queued(&mut self) -> Result<(), BondRuntimeError> {
        let result = self.dispatch_queued_inner();
        if result.is_err() {
            self.dispatch_queue.clear();
        }
        result
    }

    fn dispatch_queued_inner(&mut self) -> Result<(), BondRuntimeError> {
        while let Some(scheduled) = self.dispatch_queue.pop_front() {
            match scheduled.reason {
                TransmissionReason::NewData => {
                    self.stats.new_data_frames = self
                        .stats
                        .new_data_frames
                        .checked_add(1)
                        .ok_or(BondRuntimeError::CounterOverflow)?;
                }
                TransmissionReason::RealtimeRedundancy => {}
                TransmissionReason::LaneFailure | TransmissionReason::Timeout => {
                    self.stats.retransmitted_frames = self
                        .stats
                        .retransmitted_frames
                        .checked_add(1)
                        .ok_or(BondRuntimeError::CounterOverflow)?;
                }
            }
            let latency_sensitive = self.frame_is_latency_sensitive(&scheduled.frame)?;
            if let Some(lane) = self.lanes.get(&scheduled.lane_id) {
                match lane.try_send(scheduled.frame, latency_sensitive) {
                    Ok(()) => {
                        if scheduled.reason == TransmissionReason::RealtimeRedundancy {
                            self.stats.redundant_realtime_frames = self
                                .stats
                                .redundant_realtime_frames
                                .checked_add(1)
                                .ok_or(BondRuntimeError::CounterOverflow)?;
                        }
                        continue;
                    }
                    Err(mpsc::error::TrySendError::Full(_))
                    | Err(mpsc::error::TrySendError::Closed(_))
                        if scheduled.reason == TransmissionReason::RealtimeRedundancy =>
                    {
                        self.stats.dropped_redundant_realtime_frames = self
                            .stats
                            .dropped_redundant_realtime_frames
                            .checked_add(1)
                            .ok_or(BondRuntimeError::CounterOverflow)?;
                        continue;
                    }
                    Err(mpsc::error::TrySendError::Full(_)) => {
                        return Err(BondRuntimeError::LaneQueueFull(scheduled.lane_id));
                    }
                    Err(mpsc::error::TrySendError::Closed(_)) => {}
                }
            }
            if scheduled.reason == TransmissionReason::RealtimeRedundancy {
                self.stats.dropped_redundant_realtime_frames = self
                    .stats
                    .dropped_redundant_realtime_frames
                    .checked_add(1)
                    .ok_or(BondRuntimeError::CounterOverflow)?;
                continue;
            }
            let replacements = self.fail_lane_internal(scheduled.lane_id)?;
            self.dispatch_queue.extend(replacements);
        }
        Ok(())
    }

    fn frame_is_latency_sensitive(&self, frame: &Frame) -> Result<bool, BondRuntimeError> {
        if frame.header.kind != FrameKind::Data {
            return Ok(true);
        }
        let stream_id = StreamId::new(frame.header.stream_id)?;
        let stream = self
            .streams
            .get(&stream_id)
            .ok_or(BondRuntimeError::UnopenedStream(stream_id))?;
        Ok(stream.class.is_latency_sensitive(frame.payload.len()))
    }

    fn send_raw(&mut self, lane_id: LaneId, frame: Frame) -> Result<(), BondRuntimeError> {
        let lane = self
            .lanes
            .get(&lane_id)
            .ok_or(BondRuntimeError::LaneUnavailable(lane_id))?;
        match lane.try_send(frame, true) {
            Ok(()) => Ok(()),
            Err(mpsc::error::TrySendError::Full(_)) => {
                Err(BondRuntimeError::LaneQueueFull(lane_id))
            }
            Err(mpsc::error::TrySendError::Closed(_)) => {
                Err(BondRuntimeError::LaneUnavailable(lane_id))
            }
        }
    }

    fn statistics(&self) -> Result<BondRuntimeStats, BondRuntimeError> {
        let lanes = self
            .lane_ids
            .iter()
            .map(|id| self.sender.scheduler().snapshot(*id))
            .collect::<Result<Vec<_>, _>>()?;
        let received_by_lane = self
            .lane_ids
            .iter()
            .map(|id| {
                let counters = self
                    .received_by_lane
                    .get(id)
                    .expect("declared lane has receive counters");
                LaneReceiveStats {
                    id: *id,
                    unique_data_bytes: counters.unique_data_bytes,
                    unique_data_frames: counters.unique_data_frames,
                }
            })
            .collect();
        Ok(BondRuntimeStats {
            observed_at: self.now(),
            lanes,
            received_by_lane,
            new_data_frames: self.stats.new_data_frames,
            redundant_realtime_frames: self.stats.redundant_realtime_frames,
            dropped_redundant_realtime_frames: self.stats.dropped_redundant_realtime_frames,
            retransmitted_frames: self.stats.retransmitted_frames,
            ping_frames: self.stats.ping_frames,
            pong_frames: self.stats.pong_frames,
            liveness_failures: self.stats.liveness_failures,
            acknowledgement_frames: self.stats.acknowledgement_frames,
            window_update_frames: self.stats.window_update_frames,
            replayed_control_frames: self.stats.replayed_control_frames,
            delivered_bytes: self.stats.delivered_bytes,
            reorder_high_water: self.stats.reorder_high_water,
            unacknowledged_bytes: self.sender.unacknowledged_bytes(),
            bulk_chunk_pressure_limit: self.sender.bulk_chunk_pressure_limit(),
            backpressured_streams: 0,
            stream_backpressure_events: 0,
            active_streams: self.streams.len(),
            retired_stream_tombstones: self.retired_streams.len(),
        })
    }

    fn now(&self) -> Timestamp {
        Timestamp::from_micros(
            u64::try_from(self.started_at.elapsed().as_micros()).unwrap_or(u64::MAX),
        )
    }

    fn notify_send_progress(&self) {
        self.send_progress_tx
            .send_modify(|epoch| *epoch = epoch.wrapping_add(1));
    }

    fn is_evicted_retired_stream(&self, stream_id: StreamId) -> bool {
        let parity = (stream_id.get() & 1) as usize;
        stream_id.get() <= self.retired_stream_watermarks[parity]
    }
}

fn bounded_liveness_timeout(adaptive: Duration, maximum: Duration) -> Duration {
    adaptive
        .max(MINIMUM_LIVENESS_TIMEOUT.min(maximum))
        .min(maximum)
}

#[derive(Debug)]
pub enum BondRuntimeError {
    ZeroSessionId,
    Record(RecordError),
    TrailingRecordData,
    ZeroReorderLimit,
    ZeroStreamLimit,
    ZeroReceiveWindow,
    ZeroConsumedBytes,
    InvalidAckRangeLimit(usize),
    ZeroRetransmitDuration,
    LifecycleRequired,
    NoLanes,
    Stopped,
    StoppedWithCause(String),
    LaneClosed,
    LaneUnavailable(LaneId),
    UndeclaredLane(LaneId),
    LaneAlreadyDeclared(LaneId),
    LaneAlreadyActive(LaneId),
    LaneLimitExceeded(usize),
    LaneProtocolVersionMismatch {
        expected: BondProtocolVersion,
        actual: BondProtocolVersion,
    },
    LaneServerIncarnationMismatch {
        expected: Option<ServerIncarnation>,
        actual: Option<ServerIncarnation>,
    },
    LaneGenerationExhausted,
    LaneQueueFull(LaneId),
    LaneIo(String),
    ApplicationReceiverClosed,
    TopologyQueueFull,
    CapabilityQueueFull,
    DuplicateStream(StreamId),
    InvalidRemoteStreamId(StreamId),
    UnopenedStream(StreamId),
    StreamOpening(StreamId),
    StreamWriteClosed(StreamId),
    TrafficClassMismatch(StreamId),
    FlowControlBlocked {
        stream_id: StreamId,
        attempted: u64,
        limit: u64,
    },
    FlowControlExceeded {
        stream_id: StreamId,
        received: u64,
        limit: u64,
    },
    ExcessReceiveCredit {
        stream_id: StreamId,
        consumed: u64,
        delivered: u64,
    },
    RegressingWindow {
        stream_id: StreamId,
        previous: u64,
        received: u64,
    },
    InvalidFinalOffset {
        stream_id: StreamId,
        received: u64,
        delivered: u64,
    },
    UnexpectedStreamOpenAcknowledgement(StreamId),
    UnexpectedStreamCloseAcknowledgement(StreamId),
    DuplicateStreamClose(StreamId),
    MalformedControlFrame(FrameKind),
    SessionClosing,
    StreamsStillOpen,
    IncompleteDelivery(usize),
    UnexpectedSessionCloseAcknowledgement,
    OffsetOverflow,
    UnexpectedSession {
        expected: u64,
        received: u64,
    },
    RegressingTopologyGeneration {
        previous: u64,
        received: u64,
    },
    TopologyGenerationMismatch {
        header: u64,
        payload: u64,
    },
    ConflictingTopologyReplay(u64),
    CapabilitiesRequireProtocolV4,
    RegressingCapabilityGeneration {
        previous: u64,
        received: u64,
    },
    CapabilityGenerationMismatch {
        header: u64,
        payload: u64,
    },
    ConflictingCapabilityReplay(u64),
    UnsupportedFrame(FrameKind),
    CounterOverflow,
    QueueCapacityOverflow,
    ReceiveStreamLimitExceeded(usize),
    ActorJoin(String),
    Protocol(anonssh_bond::ProtocolError),
    FrameDecode(anonssh_bond::FrameDecodeError),
    Scheduler(SchedulerError),
    Sender(SenderError),
    Reassembly(ReassemblyError),
    Control(anonssh_bond::ControlError),
    Topology(TopologyError),
    Capability(CapabilityError),
}

impl From<anonssh_bond::ProtocolError> for BondRuntimeError {
    fn from(value: anonssh_bond::ProtocolError) -> Self {
        Self::Protocol(value)
    }
}

impl From<RecordError> for BondRuntimeError {
    fn from(value: RecordError) -> Self {
        Self::Record(value)
    }
}

impl From<anonssh_bond::FrameDecodeError> for BondRuntimeError {
    fn from(value: anonssh_bond::FrameDecodeError) -> Self {
        Self::FrameDecode(value)
    }
}

impl From<SchedulerError> for BondRuntimeError {
    fn from(value: SchedulerError) -> Self {
        Self::Scheduler(value)
    }
}

impl From<SenderError> for BondRuntimeError {
    fn from(value: SenderError) -> Self {
        Self::Sender(value)
    }
}

impl From<ReassemblyError> for BondRuntimeError {
    fn from(value: ReassemblyError) -> Self {
        Self::Reassembly(value)
    }
}

impl From<anonssh_bond::ControlError> for BondRuntimeError {
    fn from(value: anonssh_bond::ControlError) -> Self {
        Self::Control(value)
    }
}

impl From<TopologyError> for BondRuntimeError {
    fn from(value: TopologyError) -> Self {
        Self::Topology(value)
    }
}

impl From<CapabilityError> for BondRuntimeError {
    fn from(value: CapabilityError) -> Self {
        Self::Capability(value)
    }
}

impl fmt::Display for BondRuntimeError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::ZeroSessionId => write!(formatter, "runtime session ID must be non-zero"),
            Self::Record(error) => error.fmt(formatter),
            Self::TrailingRecordData => {
                write!(formatter, "encrypted bond record has trailing data")
            }
            Self::ZeroReorderLimit => write!(formatter, "runtime reorder limit must be non-zero"),
            Self::ZeroStreamLimit => write!(formatter, "runtime stream limit must be non-zero"),
            Self::ZeroReceiveWindow => write!(formatter, "runtime receive window must be non-zero"),
            Self::ZeroConsumedBytes => write!(formatter, "consumed byte count must be non-zero"),
            Self::InvalidAckRangeLimit(limit) => {
                write!(formatter, "invalid acknowledgement-range limit {limit}")
            }
            Self::ZeroRetransmitDuration => {
                write!(formatter, "runtime retransmit durations must be non-zero")
            }
            Self::LifecycleRequired => write!(formatter, "bond session requires stream lifecycle"),
            Self::NoLanes => write!(formatter, "bond runtime requires at least one lane"),
            Self::Stopped => write!(formatter, "bond runtime has stopped"),
            Self::StoppedWithCause(error) => {
                write!(formatter, "bond runtime stopped after: {error}")
            }
            Self::LaneClosed => write!(formatter, "bond lane closed"),
            Self::LaneUnavailable(id) => write!(formatter, "bond lane {} is unavailable", id.get()),
            Self::UndeclaredLane(id) => {
                write!(formatter, "bond lane {} was not declared", id.get())
            }
            Self::LaneAlreadyDeclared(id) => {
                write!(formatter, "bond lane {} is already declared", id.get())
            }
            Self::LaneAlreadyActive(id) => {
                write!(formatter, "bond lane {} is already active", id.get())
            }
            Self::LaneLimitExceeded(limit) => {
                write!(formatter, "bond runtime lane limit exceeded: {limit}")
            }
            Self::LaneProtocolVersionMismatch { expected, actual } => write!(
                formatter,
                "bond lane protocol version mismatch (session {}, lane {})",
                expected.get(),
                actual.get()
            ),
            Self::LaneServerIncarnationMismatch { expected, actual } => write!(
                formatter,
                "bond lane server incarnation mismatch (session {:?}, lane {:?})",
                expected.map(ServerIncarnation::get),
                actual.map(ServerIncarnation::get)
            ),
            Self::LaneGenerationExhausted => write!(formatter, "bond lane generation exhausted"),
            Self::LaneQueueFull(id) => write!(formatter, "bond lane {} queue is full", id.get()),
            Self::LaneIo(error) => write!(formatter, "bond lane I/O failed: {error}"),
            Self::ApplicationReceiverClosed => write!(formatter, "bond receiver was dropped"),
            Self::TopologyQueueFull => write!(formatter, "bond topology queue is full"),
            Self::CapabilityQueueFull => write!(formatter, "bond capability queue is full"),
            Self::DuplicateStream(id) => write!(formatter, "duplicate bond stream {}", id.get()),
            Self::InvalidRemoteStreamId(id) => {
                write!(formatter, "invalid remote bond stream ID {}", id.get())
            }
            Self::UnopenedStream(id) => write!(formatter, "bond stream {} is not open", id.get()),
            Self::StreamOpening(id) => {
                write!(formatter, "bond stream {} is still opening", id.get())
            }
            Self::StreamWriteClosed(id) => {
                write!(formatter, "bond stream {} is closed for writing", id.get())
            }
            Self::TrafficClassMismatch(id) => {
                write!(formatter, "bond stream {} traffic class changed", id.get())
            }
            Self::FlowControlBlocked {
                stream_id,
                attempted,
                limit,
            } => write!(
                formatter,
                "bond stream {} is flow-control blocked at {attempted} (limit {limit})",
                stream_id.get()
            ),
            Self::FlowControlExceeded {
                stream_id,
                received,
                limit,
            } => write!(
                formatter,
                "bond stream {} exceeded receive credit at {received} (limit {limit})",
                stream_id.get()
            ),
            Self::ExcessReceiveCredit {
                stream_id,
                consumed,
                delivered,
            } => write!(
                formatter,
                "bond stream {} consumed through {consumed} after delivering {delivered}",
                stream_id.get()
            ),
            Self::RegressingWindow {
                stream_id,
                previous,
                received,
            } => write!(
                formatter,
                "bond stream {} window regressed from {previous} to {received}",
                stream_id.get()
            ),
            Self::InvalidFinalOffset {
                stream_id,
                received,
                delivered,
            } => write!(
                formatter,
                "bond stream {} declared final offset {received} after delivering {delivered}",
                stream_id.get()
            ),
            Self::UnexpectedStreamOpenAcknowledgement(id) => write!(
                formatter,
                "unexpected stream-open acknowledgement for {}",
                id.get()
            ),
            Self::UnexpectedStreamCloseAcknowledgement(id) => write!(
                formatter,
                "unexpected stream-close acknowledgement for {}",
                id.get()
            ),
            Self::DuplicateStreamClose(id) => {
                write!(formatter, "duplicate stream close for {}", id.get())
            }
            Self::MalformedControlFrame(kind) => write!(formatter, "malformed {kind:?} frame"),
            Self::SessionClosing => write!(formatter, "bond session is already closing"),
            Self::StreamsStillOpen => write!(formatter, "bond session still has open streams"),
            Self::IncompleteDelivery(bytes) => {
                write!(formatter, "bond session has {bytes} unacknowledged bytes")
            }
            Self::UnexpectedSessionCloseAcknowledgement => {
                write!(formatter, "unexpected session-close acknowledgement")
            }
            Self::OffsetOverflow => write!(formatter, "bond runtime offset overflow"),
            Self::UnexpectedSession { expected, received } => write!(
                formatter,
                "unexpected bond session {received}; expected {expected}"
            ),
            Self::RegressingTopologyGeneration { previous, received } => write!(
                formatter,
                "topology generation regressed from {previous} to {received}"
            ),
            Self::TopologyGenerationMismatch { header, payload } => write!(
                formatter,
                "topology generation mismatch: header {header}, payload {payload}"
            ),
            Self::ConflictingTopologyReplay(generation) => write!(
                formatter,
                "topology generation {generation} was replayed with conflicting content"
            ),
            Self::CapabilitiesRequireProtocolV4 => {
                write!(formatter, "bond capabilities require protocol v4")
            }
            Self::RegressingCapabilityGeneration { previous, received } => write!(
                formatter,
                "capability generation regressed from {previous} to {received}"
            ),
            Self::CapabilityGenerationMismatch { header, payload } => write!(
                formatter,
                "capability generation mismatch: header {header}, payload {payload}"
            ),
            Self::ConflictingCapabilityReplay(generation) => write!(
                formatter,
                "capability generation {generation} was replayed with conflicting content"
            ),
            Self::UnsupportedFrame(kind) => write!(formatter, "unsupported frame {kind:?}"),
            Self::CounterOverflow => write!(formatter, "bond runtime counter overflow"),
            Self::QueueCapacityOverflow => write!(formatter, "bond lane queue capacity overflow"),
            Self::ReceiveStreamLimitExceeded(limit) => {
                write!(formatter, "bond receive-stream limit exceeded: {limit}")
            }
            Self::ActorJoin(error) => write!(formatter, "bond runtime task failed: {error}"),
            Self::Protocol(error) => error.fmt(formatter),
            Self::FrameDecode(error) => error.fmt(formatter),
            Self::Scheduler(error) => error.fmt(formatter),
            Self::Sender(error) => error.fmt(formatter),
            Self::Reassembly(error) => error.fmt(formatter),
            Self::Control(error) => error.fmt(formatter),
            Self::Topology(error) => error.fmt(formatter),
            Self::Capability(error) => error.fmt(formatter),
        }
    }
}

impl BondRuntimeError {
    pub(crate) fn terminal_cause(&self) -> String {
        match self {
            Self::StoppedWithCause(cause) => cause.clone(),
            _ => self.to_string(),
        }
    }
}

impl Error for BondRuntimeError {}

#[cfg(test)]
mod tests {
    use std::time::Duration;

    use crate::handshake::BondProtocolVersion;
    use anonssh_bond::{
        AcknowledgedChunk, CapabilityAdvertisement, CapabilityFeatures, EndpointDescriptor,
        EndpointProvider, FailureDomain, Frame, FrameFlags, FrameKind, LaneConfig, LaneId,
        ProviderCapability, SchedulerConfig, SelectiveAcknowledgement, SenderConfig, StreamId,
        StreamOpen, StreamReset, Timestamp, TopologyAction, TopologyAdvertisement, TrafficClass,
    };

    use super::{
        bounded_liveness_timeout, BondRuntime, BondRuntimeConfig, BondRuntimeError, DeliveryCohort,
        DeliveryCohorts, DeliveryHistory, Event, LaneLiveness, PendingAcknowledgements,
        RuntimeEvent, RuntimeLane, ACK_FLUSH_INTERVAL, LANE_QUEUE_CONTROL_RESERVE,
        MAX_RUNTIME_LANES, MINIMUM_ADAPTIVE_RTO, MINIMUM_LIVENESS_TIMEOUT,
    };

    #[tokio::test(start_paused = true)]
    async fn acknowledgement_deadline_is_demand_armed_and_reuses_capacity() {
        let mut pending = PendingAcknowledgements::new(8);
        let capacity = pending.stream_ids.capacity();
        assert_eq!(pending.deadline(), None);

        let first_deadline = tokio::time::Instant::now() + ACK_FLUSH_INTERVAL;
        pending.queue(StreamId::new(1).unwrap());
        assert_eq!(pending.deadline(), Some(first_deadline));

        tokio::time::advance(Duration::from_millis(5)).await;
        pending.queue(StreamId::new(3).unwrap());
        assert_eq!(pending.deadline(), Some(first_deadline));
        assert_eq!(pending.pop(), Some(StreamId::new(3).unwrap()));
        assert_eq!(pending.deadline(), Some(first_deadline));

        pending.defer_until_lane_returns();
        assert_eq!(pending.deadline(), None);
        assert_eq!(pending.pop(), Some(StreamId::new(1).unwrap()));
        assert_eq!(pending.stream_ids.capacity(), capacity);

        pending.queue(StreamId::new(5).unwrap());
        pending.remove(StreamId::new(5).unwrap());
        assert_eq!(pending.deadline(), None);
        assert_eq!(pending.stream_ids.capacity(), capacity);
    }

    #[test]
    fn split_lane_queues_preserve_the_previous_aggregate_bound() {
        let config = BondRuntimeConfig::default();
        let capacities = config.lane_queue_capacities().unwrap();

        assert_eq!(capacities.bulk, config.sender.max_unacknowledged_chunks);
        assert_eq!(
            capacities.latency_sensitive,
            config.sender.max_unacknowledged_chunks + LANE_QUEUE_CONTROL_RESERVE
        );
        assert_eq!(
            capacities.bulk + capacities.latency_sensitive,
            config.sender.max_unacknowledged_chunks * 2 + LANE_QUEUE_CONTROL_RESERVE
        );
    }

    #[tokio::test]
    async fn runtime_accepts_thirty_two_lanes_and_rejects_the_next() {
        let build_lanes = |count: usize| {
            let mut peers = Vec::with_capacity(count);
            let lanes = (1..=count)
                .map(|id| {
                    let id = u32::try_from(id).unwrap();
                    let config = LaneConfig::new(
                        LaneId::new(id).unwrap(),
                        FailureDomain::new(u64::from(id)).unwrap(),
                        Duration::from_millis(5),
                        1_000_000,
                    )
                    .unwrap();
                    let (io, peer) = tokio::io::duplex(1_024);
                    peers.push(peer);
                    RuntimeLane::new_for_test(config, io, [1; 32], [2; 32])
                })
                .collect::<Vec<_>>();
            (lanes, peers)
        };

        let (lanes, _peers) = build_lanes(MAX_RUNTIME_LANES);
        let runtime = BondRuntime::spawn(BondRuntimeConfig::default(), lanes).unwrap();
        assert_eq!(runtime.statistics().await.unwrap().lanes.len(), 32);
        drop(runtime);

        let (oversized, _peers) = build_lanes(MAX_RUNTIME_LANES + 1);
        assert!(matches!(
            BondRuntime::spawn(BondRuntimeConfig::default(), oversized),
            Err(BondRuntimeError::LaneLimitExceeded(32))
        ));
    }

    #[tokio::test]
    async fn rejects_mixed_protocol_versions_at_spawn_and_repair() {
        let first = LaneConfig::new(
            LaneId::new(1).unwrap(),
            FailureDomain::new(1).unwrap(),
            Duration::from_millis(5),
            1_000_000,
        )
        .unwrap();
        let second = LaneConfig::new(
            LaneId::new(2).unwrap(),
            FailureDomain::new(2).unwrap(),
            Duration::from_millis(5),
            1_000_000,
        )
        .unwrap();
        let (first_io, _) = tokio::io::duplex(1024);
        let (second_io, _) = tokio::io::duplex(1024);
        let mixed = BondRuntime::spawn(
            BondRuntimeConfig::default(),
            vec![
                RuntimeLane::new_for_test(first, first_io, [1; 32], [2; 32]),
                RuntimeLane::new_for_test(second, second_io, [3; 32], [4; 32])
                    .with_protocol_version_for_test(BondProtocolVersion::V1),
            ],
        );
        assert!(matches!(
            mixed,
            Err(BondRuntimeError::LaneProtocolVersionMismatch {
                expected: BondProtocolVersion::V6,
                actual: BondProtocolVersion::V1,
            })
        ));

        let (first_io, _peer) = tokio::io::duplex(1024);
        let runtime = BondRuntime::spawn(
            BondRuntimeConfig::default(),
            vec![RuntimeLane::new_for_test(first, first_io, [1; 32], [2; 32])],
        )
        .unwrap();
        runtime.declare_lane(second).await.unwrap();
        let (replacement, _peer) = tokio::io::duplex(1024);
        let error = runtime
            .add_lane(
                RuntimeLane::new_for_test(second, replacement, [3; 32], [4; 32])
                    .with_protocol_version_for_test(BondProtocolVersion::V1),
            )
            .await
            .unwrap_err();
        assert!(matches!(
            error,
            BondRuntimeError::LaneProtocolVersionMismatch {
                expected: BondProtocolVersion::V6,
                actual: BondProtocolVersion::V1,
            }
        ));
    }

    #[tokio::test]
    async fn rejects_mixed_server_incarnations_at_spawn_and_repair() {
        let first = LaneConfig::new(
            LaneId::new(1).unwrap(),
            FailureDomain::new(1).unwrap(),
            Duration::from_millis(5),
            1_000_000,
        )
        .unwrap();
        let second = LaneConfig::new(
            LaneId::new(2).unwrap(),
            FailureDomain::new(2).unwrap(),
            Duration::from_millis(5),
            1_000_000,
        )
        .unwrap();
        let (first_io, _) = tokio::io::duplex(1024);
        let (second_io, _) = tokio::io::duplex(1024);
        let mixed = BondRuntime::spawn(
            BondRuntimeConfig::default(),
            vec![
                RuntimeLane::new_for_test(first, first_io, [1; 32], [2; 32]),
                RuntimeLane::new_for_test(second, second_io, [3; 32], [4; 32])
                    .with_server_incarnation_for_test(2),
            ],
        );
        assert!(matches!(
            mixed,
            Err(BondRuntimeError::LaneServerIncarnationMismatch {
                expected: Some(expected),
                actual: Some(actual),
            }) if expected.get() == 1 && actual.get() == 2
        ));

        let (first_io, _peer) = tokio::io::duplex(1024);
        let runtime = BondRuntime::spawn(
            BondRuntimeConfig::default(),
            vec![RuntimeLane::new_for_test(first, first_io, [1; 32], [2; 32])],
        )
        .unwrap();
        runtime.declare_lane(second).await.unwrap();
        let (replacement, _peer) = tokio::io::duplex(1024);
        let error = runtime
            .add_lane(
                RuntimeLane::new_for_test(second, replacement, [3; 32], [4; 32])
                    .with_server_incarnation_for_test(2),
            )
            .await
            .unwrap_err();
        assert!(matches!(
            error,
            BondRuntimeError::LaneServerIncarnationMismatch {
                expected: Some(expected),
                actual: Some(actual),
            } if expected.get() == 1 && actual.get() == 2
        ));
    }

    #[test]
    fn product_liveness_has_a_wider_floor_than_payload_retransmission() {
        let maximum = Duration::from_secs(30);
        assert_eq!(MINIMUM_ADAPTIVE_RTO, Duration::from_secs(2));
        assert_eq!(MINIMUM_LIVENESS_TIMEOUT, Duration::from_secs(30));
        assert_eq!(
            bounded_liveness_timeout(MINIMUM_ADAPTIVE_RTO, maximum),
            MINIMUM_LIVENESS_TIMEOUT
        );
        assert_eq!(
            bounded_liveness_timeout(Duration::from_secs(12), maximum),
            MINIMUM_LIVENESS_TIMEOUT
        );
        assert_eq!(
            bounded_liveness_timeout(Duration::from_secs(45), Duration::from_secs(60)),
            Duration::from_secs(45)
        );
        assert_eq!(
            bounded_liveness_timeout(Duration::from_millis(300), Duration::from_millis(300)),
            Duration::from_millis(300)
        );
    }

    #[test]
    fn liveness_response_deadline_starts_only_after_the_probe_is_written() {
        let mut liveness = LaneLiveness::new(Timestamp::from_micros(1));
        assert!(!liveness.has_outstanding_probe());
        liveness.queue_ping(7);
        assert!(liveness.has_outstanding_probe());
        assert_eq!(liveness.response_deadline_started_at(), None);

        liveness.mark_ping_written(8, Timestamp::from_micros(20));
        assert!(liveness.has_outstanding_probe());
        assert_eq!(liveness.response_deadline_started_at(), None);

        let written_at = Timestamp::from_micros(30);
        liveness.mark_ping_written(7, written_at);
        assert!(liveness.has_outstanding_probe());
        assert_eq!(liveness.response_deadline_started_at(), Some(written_at));
    }

    #[test]
    fn acknowledgement_delivery_is_one_aggregate_cohort_per_lane() {
        let first_lane = LaneId::new(1).unwrap();
        let second_lane = LaneId::new(2).unwrap();
        let chunks = vec![
            AcknowledgedChunk {
                lane_id: first_lane,
                bytes: 16,
                last_sent_at: Timestamp::from_micros(100),
                transmission_count: 1,
            },
            AcknowledgedChunk {
                lane_id: second_lane,
                bytes: 32,
                last_sent_at: Timestamp::from_micros(90),
                transmission_count: 1,
            },
            AcknowledgedChunk {
                lane_id: first_lane,
                bytes: 64,
                last_sent_at: Timestamp::from_micros(120),
                transmission_count: 1,
            },
        ];
        let cohorts = DeliveryCohorts::from_chunks(&chunks).unwrap();

        let observations: Vec<_> = cohorts.iter().collect();
        assert_eq!(
            observations,
            vec![
                DeliveryCohort {
                    lane_id: first_lane,
                    bytes: 80,
                    oldest_sent_at: Timestamp::from_micros(100),
                    newest_sent_at: Timestamp::from_micros(120),
                },
                DeliveryCohort {
                    lane_id: second_lane,
                    bytes: 32,
                    oldest_sent_at: Timestamp::from_micros(90),
                    newest_sent_at: Timestamp::from_micros(90),
                },
            ]
        );
        let first_sample = observations[0]
            .sample(Timestamp::from_micros(220), None)
            .unwrap();
        assert_eq!(first_sample.bytes, 80);
        assert_eq!(first_sample.elapsed, Duration::from_micros(120));
        assert_eq!(first_sample.round_trip_time, Duration::from_micros(100));
        assert_eq!(
            observations
                .iter()
                .map(|cohort| cohort.bytes)
                .sum::<usize>(),
            112
        );
    }

    #[test]
    fn pipelined_delivery_uses_ack_spacing_without_idle_or_zero_interval_spikes() {
        let lane_id = LaneId::new(1).unwrap();
        let mut history = DeliveryHistory::new();
        assert_eq!(
            history
                .previous_and_record(lane_id, Timestamp::from_micros(1_050))
                .unwrap(),
            None
        );
        let previous = history
            .previous_and_record(lane_id, Timestamp::from_micros(1_150))
            .unwrap();
        let cohort = DeliveryCohort {
            lane_id,
            bytes: 64 * 1024,
            oldest_sent_at: Timestamp::from_micros(100),
            newest_sent_at: Timestamp::from_micros(150),
        };
        let now = Timestamp::from_micros(1_150);

        let first = cohort.sample(now, None).unwrap();
        assert_eq!(first.elapsed, Duration::from_micros(1_050));
        assert_eq!(first.round_trip_time, Duration::from_micros(1_000));

        let pipelined = cohort.sample(now, previous).unwrap();
        assert_eq!(pipelined.elapsed, Duration::from_micros(100));
        assert_eq!(pipelined.round_trip_time, first.round_trip_time);

        let idle = cohort
            .sample(now, Some(Timestamp::from_micros(50)))
            .unwrap();
        assert_eq!(idle.elapsed, first.elapsed);
        let zero_spacing = cohort.sample(now, Some(now)).unwrap();
        assert_eq!(zero_spacing.elapsed, first.elapsed);
    }

    fn strict_pair() -> (BondRuntime, BondRuntime) {
        let (client_io, server_io) = tokio::io::duplex(64 * 1024);
        let lane = LaneConfig::new(
            LaneId::new(1).unwrap(),
            FailureDomain::new(1).unwrap(),
            Duration::from_millis(5),
            100_000_000,
        )
        .unwrap();
        let config = BondRuntimeConfig {
            session_id: 77,
            scheduler: SchedulerConfig::default(),
            sender: SenderConfig {
                max_chunk_payload: 4,
                bulk_chunk: anonssh_bond::BulkChunkConfig::fixed(4),
                max_unacknowledged_bytes: 64,
                max_unacknowledged_chunks: 16,
                redundant_realtime: false,
            },
            max_reorder_bytes_per_stream: 64,
            max_receive_streams: 8,
            stream_receive_window: 8,
            max_ack_ranges: 4,
            require_stream_open: true,
            retransmit_after: Duration::from_secs(1),
            retransmit_scan_interval: Duration::from_millis(10),
        };
        (
            BondRuntime::spawn(
                config,
                vec![RuntimeLane::new_for_test(lane, client_io, [1; 32], [2; 32])],
            )
            .unwrap(),
            BondRuntime::spawn(
                config,
                vec![RuntimeLane::new_for_test(lane, server_io, [2; 32], [1; 32])],
            )
            .unwrap(),
        )
    }

    async fn next_event(runtime: &mut BondRuntime) -> RuntimeEvent {
        tokio::time::timeout(Duration::from_secs(2), runtime.receive_event())
            .await
            .expect("runtime event timed out")
            .expect("runtime stopped")
    }

    #[tokio::test]
    async fn terminal_actor_failure_preserves_its_cause() {
        let stream_id = StreamId::new(1).unwrap();
        let lane_id = LaneId::new(1).unwrap();
        let lane = LaneConfig::new(
            lane_id,
            FailureDomain::new(1).unwrap(),
            Duration::from_millis(5),
            100_000_000,
        )
        .unwrap();
        for (changed_class, changed_window) in
            [(TrafficClass::Realtime, 8), (TrafficClass::Bulk, 9)]
        {
            let (server_io, _held_peer) = tokio::io::duplex(64 * 1024);
            let mut server = BondRuntime::spawn(
                BondRuntimeConfig {
                    session_id: 77,
                    require_stream_open: true,
                    ..BondRuntimeConfig::default()
                },
                vec![RuntimeLane::new_for_test(lane, server_io, [2; 32], [1; 32])],
            )
            .unwrap();
            let stream_open = |class, window| {
                Frame::new(
                    FrameKind::StreamOpen,
                    FrameFlags::NONE,
                    77,
                    stream_id.get(),
                    0,
                    StreamOpen::new(class, window)
                        .unwrap()
                        .encode_payload()
                        .to_vec(),
                )
                .unwrap()
            };
            server
                .event_tx
                .send(Event::Inbound {
                    lane_id,
                    generation: 1,
                    frame: stream_open(TrafficClass::Bulk, 8),
                })
                .await
                .unwrap();
            assert!(matches!(
                next_event(&mut server).await,
                RuntimeEvent::StreamOpened { stream_id: opened, .. } if opened == stream_id
            ));
            server
                .event_tx
                .send(Event::Inbound {
                    lane_id,
                    generation: 1,
                    frame: stream_open(changed_class, changed_window),
                })
                .await
                .unwrap();

            let error =
                tokio::time::timeout(Duration::from_secs(2), server.receive_event_uncredited())
                    .await
                    .expect("runtime did not report terminal failure")
                    .unwrap_err();
            assert!(matches!(
                error,
                BondRuntimeError::StoppedWithCause(cause)
                    if cause == "duplicate bond stream 1"
            ));
        }
    }

    #[tokio::test]
    async fn explicit_termination_stops_the_runtime_with_its_cause() {
        let (mut client, server) = strict_pair();
        let control = client.control();
        control
            .terminate("server incarnation changed".to_owned())
            .await
            .unwrap();
        let error = tokio::time::timeout(Duration::from_secs(2), client.receive_event_uncredited())
            .await
            .expect("runtime did not terminate")
            .unwrap_err();
        assert!(matches!(
            error,
            BondRuntimeError::StoppedWithCause(cause) if cause == "server incarnation changed"
        ));
        drop(server);
    }

    #[tokio::test]
    async fn matching_stream_lifecycle_replays_are_idempotent() {
        let stream_id = StreamId::new(1).unwrap();
        let lane_id = LaneId::new(1).unwrap();
        let lane = LaneConfig::new(
            lane_id,
            FailureDomain::new(1).unwrap(),
            Duration::from_millis(5),
            100_000_000,
        )
        .unwrap();
        let (server_io, _held_peer) = tokio::io::duplex(64 * 1024);
        let mut server = BondRuntime::spawn(
            BondRuntimeConfig {
                session_id: 77,
                require_stream_open: true,
                ..BondRuntimeConfig::default()
            },
            vec![RuntimeLane::new_for_test(lane, server_io, [2; 32], [1; 32])],
        )
        .unwrap();
        let open = || {
            Frame::new(
                FrameKind::StreamOpen,
                FrameFlags::NONE,
                77,
                stream_id.get(),
                0,
                StreamOpen::new(TrafficClass::Bulk, 8)
                    .unwrap()
                    .encode_payload()
                    .to_vec(),
            )
            .unwrap()
        };
        for frame in [open(), open()] {
            server
                .event_tx
                .send(Event::Inbound {
                    lane_id,
                    generation: 1,
                    frame,
                })
                .await
                .unwrap();
        }
        assert_eq!(
            next_event(&mut server).await,
            RuntimeEvent::StreamOpened {
                stream_id,
                class: TrafficClass::Bulk,
            }
        );
        server.statistics().await.unwrap();
        assert!(
            tokio::time::timeout(Duration::from_millis(50), server.receive_event())
                .await
                .is_err()
        );

        let close = |offset| {
            Frame::new(
                FrameKind::StreamClose,
                FrameFlags::NONE,
                77,
                stream_id.get(),
                offset,
                Vec::new(),
            )
            .unwrap()
        };
        for frame in [close(0), close(0)] {
            server
                .event_tx
                .send(Event::Inbound {
                    lane_id,
                    generation: 1,
                    frame,
                })
                .await
                .unwrap();
        }
        assert_eq!(
            next_event(&mut server).await,
            RuntimeEvent::StreamFinished { stream_id }
        );
        server.statistics().await.unwrap();
        assert!(
            tokio::time::timeout(Duration::from_millis(50), server.receive_event())
                .await
                .is_err()
        );

        server
            .event_tx
            .send(Event::Inbound {
                lane_id,
                generation: 1,
                frame: close(1),
            })
            .await
            .unwrap();
        let error = tokio::time::timeout(Duration::from_secs(2), server.receive_event_uncredited())
            .await
            .expect("runtime did not reject a conflicting close replay")
            .unwrap_err();
        assert!(matches!(
            error,
            BondRuntimeError::StoppedWithCause(cause)
                if cause == "duplicate stream close for 1"
        ));
    }

    #[tokio::test]
    async fn retired_stream_lifecycle_replay_is_bounded_and_idempotent() {
        let stream_id = StreamId::new(1).unwrap();
        let lane_id = LaneId::new(1).unwrap();
        let (mut client, mut server) = strict_pair();
        let (opened, event) = tokio::join!(
            client.open_stream(stream_id, TrafficClass::Bulk),
            next_event(&mut server)
        );
        opened.unwrap();
        assert!(matches!(
            event,
            RuntimeEvent::StreamOpened { stream_id: opened, .. } if opened == stream_id
        ));

        let (client_closed, server_closed) = tokio::join!(
            client.close_stream(stream_id),
            server.close_stream(stream_id)
        );
        client_closed.unwrap();
        server_closed.unwrap();
        for runtime in [&mut client, &mut server] {
            assert_eq!(
                next_event(runtime).await,
                RuntimeEvent::StreamFinished { stream_id }
            );
            assert_eq!(
                next_event(runtime).await,
                RuntimeEvent::StreamRetired { stream_id }
            );
            let stats = runtime.statistics().await.unwrap();
            assert_eq!(stats.active_streams, 0);
            assert_eq!(stats.retired_stream_tombstones, 1);
        }

        let open = || {
            Frame::new(
                FrameKind::StreamOpen,
                FrameFlags::NONE,
                77,
                stream_id.get(),
                0,
                StreamOpen::new(TrafficClass::Bulk, 8)
                    .unwrap()
                    .encode_payload()
                    .to_vec(),
            )
            .unwrap()
        };
        let close = |offset| {
            Frame::new(
                FrameKind::StreamClose,
                FrameFlags::NONE,
                77,
                stream_id.get(),
                offset,
                Vec::new(),
            )
            .unwrap()
        };
        for frame in [open(), close(0)] {
            server
                .event_tx
                .send(Event::Inbound {
                    lane_id,
                    generation: 1,
                    frame,
                })
                .await
                .unwrap();
        }
        server.statistics().await.unwrap();
        assert!(
            tokio::time::timeout(Duration::from_millis(50), server.receive_event())
                .await
                .is_err()
        );

        server
            .event_tx
            .send(Event::Inbound {
                lane_id,
                generation: 1,
                frame: close(1),
            })
            .await
            .unwrap();
        let error = tokio::time::timeout(Duration::from_secs(2), server.receive_event_uncredited())
            .await
            .expect("retired stream did not reject a conflicting close replay")
            .unwrap_err();
        assert!(matches!(
            error,
            BondRuntimeError::StoppedWithCause(cause)
                if cause == "duplicate stream close for 1"
        ));
    }

    #[tokio::test]
    async fn evicted_retired_stream_frames_are_discarded_without_id_reuse() {
        let lane_id = LaneId::new(1).unwrap();
        let (mut client, mut server) = strict_pair();
        let first = StreamId::new(1).unwrap();
        for raw_id in (1..=17).step_by(2) {
            let stream_id = StreamId::new(raw_id).unwrap();
            let (opened, event) = tokio::join!(
                client.open_stream(stream_id, TrafficClass::Bulk),
                next_event(&mut server)
            );
            opened.unwrap();
            assert!(matches!(
                event,
                RuntimeEvent::StreamOpened { stream_id: opened, .. } if opened == stream_id
            ));
            let (client_closed, server_closed) = tokio::join!(
                client.close_stream(stream_id),
                server.close_stream(stream_id)
            );
            client_closed.unwrap();
            server_closed.unwrap();
            for runtime in [&mut client, &mut server] {
                assert_eq!(
                    next_event(runtime).await,
                    RuntimeEvent::StreamFinished { stream_id }
                );
                assert_eq!(
                    next_event(runtime).await,
                    RuntimeEvent::StreamRetired { stream_id }
                );
            }
        }
        for runtime in [&client, &server] {
            assert_eq!(
                runtime
                    .statistics()
                    .await
                    .unwrap()
                    .retired_stream_tombstones,
                8
            );
        }

        let stale_frames = [
            Frame::new(
                FrameKind::StreamOpen,
                FrameFlags::NONE,
                77,
                first.get(),
                0,
                StreamOpen::new(TrafficClass::Bulk, 8)
                    .unwrap()
                    .encode_payload()
                    .to_vec(),
            )
            .unwrap(),
            Frame::new(
                FrameKind::Data,
                FrameFlags::RETRANSMISSION,
                77,
                first.get(),
                0,
                vec![0x51],
            )
            .unwrap(),
            Frame::new(
                FrameKind::Acknowledgement,
                FrameFlags::NONE,
                77,
                first.get(),
                0,
                SelectiveAcknowledgement::encode_payload_parts(0, &[]).unwrap(),
            )
            .unwrap(),
            Frame::new(
                FrameKind::WindowUpdate,
                FrameFlags::NONE,
                77,
                first.get(),
                8,
                Vec::new(),
            )
            .unwrap(),
            Frame::new(
                FrameKind::StreamClose,
                FrameFlags::NONE,
                77,
                first.get(),
                0,
                Vec::new(),
            )
            .unwrap(),
            Frame::new(
                FrameKind::StreamReset,
                FrameFlags::NONE,
                77,
                first.get(),
                0,
                StreamReset::new(7).encode_payload().to_vec(),
            )
            .unwrap(),
        ];
        for frame in stale_frames {
            server
                .event_tx
                .send(Event::Inbound {
                    lane_id,
                    generation: 1,
                    frame,
                })
                .await
                .unwrap();
        }
        assert_eq!(
            server.statistics().await.unwrap().retired_stream_tombstones,
            8
        );
        assert!(matches!(
            client.open_stream(first, TrafficClass::Bulk).await,
            Err(BondRuntimeError::DuplicateStream(stream_id)) if stream_id == first
        ));

        let (client_result, server_result) = tokio::join!(client.shutdown(), server.shutdown());
        client_result.unwrap();
        server_result.unwrap();
    }

    #[tokio::test]
    async fn reordered_absolute_window_updates_are_idempotent() {
        let stream_id = StreamId::new(1).unwrap();
        let lane_id = LaneId::new(1).unwrap();
        let (client, mut server) = strict_pair();
        client
            .open_stream(stream_id, TrafficClass::Bulk)
            .await
            .unwrap();
        assert!(matches!(
            next_event(&mut server).await,
            RuntimeEvent::StreamOpened { stream_id: opened, .. } if opened == stream_id
        ));

        for offset in [128, 64, 128] {
            client
                .event_tx
                .send(Event::Inbound {
                    lane_id,
                    generation: 1,
                    frame: Frame::new(
                        FrameKind::WindowUpdate,
                        FrameFlags::NONE,
                        77,
                        stream_id.get(),
                        offset,
                        Vec::new(),
                    )
                    .unwrap(),
                })
                .await
                .unwrap();
        }

        client.statistics().await.unwrap();
        client
            .send(stream_id, TrafficClass::Bulk, vec![0x5a; 64])
            .await
            .unwrap();
    }

    #[tokio::test]
    async fn late_cumulative_topology_snapshot_does_not_replace_newer_state() {
        let lane_id = LaneId::new(1).unwrap();
        let (_client, mut server) = strict_pair();
        let descriptor = |id, action| {
            EndpointDescriptor::new(
                LaneId::new(id).unwrap(),
                FailureDomain::new(u64::from(id)).unwrap(),
                EndpointProvider::Tcp,
                action,
                format!("tcp://127.0.0.1:{}", 24_000 + id),
            )
            .unwrap()
        };
        let first =
            TopologyAdvertisement::new(1, vec![descriptor(2, TopologyAction::Add)]).unwrap();
        let second = TopologyAdvertisement::new(
            2,
            vec![
                descriptor(2, TopologyAction::Add),
                descriptor(3, TopologyAction::Add),
            ],
        )
        .unwrap();
        for advertisement in [second.clone(), first] {
            server
                .event_tx
                .send(Event::Inbound {
                    lane_id,
                    generation: 1,
                    frame: Frame::new(
                        FrameKind::EndpointAdvertisement,
                        FrameFlags::NONE,
                        77,
                        0,
                        advertisement.generation,
                        advertisement.encode_payload().unwrap(),
                    )
                    .unwrap(),
                })
                .await
                .unwrap();
        }

        assert_eq!(
            next_event(&mut server).await,
            RuntimeEvent::TopologyAdvertised(second)
        );
        server.statistics().await.unwrap();
        assert!(
            tokio::time::timeout(Duration::from_millis(50), server.receive_event())
                .await
                .is_err()
        );

        let conflicting =
            TopologyAdvertisement::new(2, vec![descriptor(4, TopologyAction::Add)]).unwrap();
        server
            .event_tx
            .send(Event::Inbound {
                lane_id,
                generation: 1,
                frame: Frame::new(
                    FrameKind::EndpointAdvertisement,
                    FrameFlags::NONE,
                    77,
                    0,
                    conflicting.generation,
                    conflicting.encode_payload().unwrap(),
                )
                .unwrap(),
            })
            .await
            .unwrap();
        let error = tokio::time::timeout(Duration::from_secs(2), server.receive_event_uncredited())
            .await
            .expect("runtime did not reject conflicting topology replay")
            .unwrap_err();
        assert!(matches!(
            error,
            BondRuntimeError::StoppedWithCause(cause)
                if cause == "topology generation 2 was replayed with conflicting content"
        ));
    }

    #[tokio::test]
    async fn capability_snapshots_ignore_regression_and_reject_conflicting_replay() {
        let lane_id = LaneId::new(1).unwrap();
        let (_client, mut server) = strict_pair();
        let capability = |generation, queue_delay_micros| {
            CapabilityAdvertisement::new(
                generation,
                CapabilityFeatures::CURRENT,
                1024 * 1024 * 1024,
                1_000,
                queue_delay_micros,
                4,
                8,
                1,
                vec![ProviderCapability::new(
                    EndpointProvider::Tor,
                    4,
                    1,
                    30_000,
                    queue_delay_micros,
                    1_000,
                )
                .unwrap()],
            )
            .unwrap()
        };
        let first = capability(1, 10_000);
        let second = capability(2, 20_000);
        for advertisement in [second.clone(), first] {
            server
                .event_tx
                .send(Event::Inbound {
                    lane_id,
                    generation: 1,
                    frame: Frame::new(
                        FrameKind::CapabilityAdvertisement,
                        FrameFlags::NONE,
                        77,
                        0,
                        advertisement.generation,
                        advertisement.encode_payload().unwrap(),
                    )
                    .unwrap(),
                })
                .await
                .unwrap();
        }
        assert_eq!(
            next_event(&mut server).await,
            RuntimeEvent::CapabilitiesAdvertised(second)
        );
        server.statistics().await.unwrap();
        assert!(
            tokio::time::timeout(Duration::from_millis(50), server.receive_event())
                .await
                .is_err()
        );

        let conflicting = capability(2, 30_000);
        server
            .event_tx
            .send(Event::Inbound {
                lane_id,
                generation: 1,
                frame: Frame::new(
                    FrameKind::CapabilityAdvertisement,
                    FrameFlags::NONE,
                    77,
                    0,
                    conflicting.generation,
                    conflicting.encode_payload().unwrap(),
                )
                .unwrap(),
            })
            .await
            .unwrap();
        let error = tokio::time::timeout(Duration::from_secs(2), server.receive_event_uncredited())
            .await
            .expect("runtime did not reject conflicting capability replay")
            .unwrap_err();
        assert!(matches!(
            error,
            BondRuntimeError::StoppedWithCause(cause)
                if cause == "capability generation 2 was replayed with conflicting content"
        ));
    }

    async fn send_after_credit(
        runtime: &BondRuntime,
        stream_id: StreamId,
        class: TrafficClass,
        bytes: &[u8],
    ) {
        tokio::time::timeout(Duration::from_secs(2), async {
            loop {
                match runtime.send(stream_id, class, bytes.to_vec()).await {
                    Ok(()) => return,
                    Err(BondRuntimeError::FlowControlBlocked { .. }) => {
                        tokio::time::sleep(Duration::from_millis(1)).await;
                    }
                    Err(error) => panic!("unexpected send error: {error}"),
                }
            }
        })
        .await
        .expect("flow-control credit did not resume");
    }

    async fn receive_bytes(
        runtime: &mut BondRuntime,
        stream_id: StreamId,
        expected: usize,
    ) -> Vec<u8> {
        let mut bytes = Vec::with_capacity(expected);
        while bytes.len() < expected {
            match next_event(runtime).await {
                RuntimeEvent::Data(data) if data.stream_id == stream_id => {
                    bytes.extend_from_slice(&data.bytes);
                }
                event => panic!("unexpected runtime event: {event:?}"),
            }
        }
        assert_eq!(bytes.len(), expected);
        bytes
    }

    #[tokio::test]
    async fn lifecycle_enforces_credit_half_close_and_clean_shutdown() {
        let (mut client, mut server) = strict_pair();
        let stream = StreamId::new(1).unwrap();
        assert!(matches!(
            client
                .send(stream, TrafficClass::Bulk, b"x".to_vec())
                .await,
            Err(BondRuntimeError::UnopenedStream(id)) if id == stream
        ));

        client
            .open_stream(stream, TrafficClass::Bulk)
            .await
            .unwrap();
        assert_eq!(
            next_event(&mut server).await,
            RuntimeEvent::StreamOpened {
                stream_id: stream,
                class: TrafficClass::Bulk,
            }
        );
        assert!(matches!(
            client.send(stream, TrafficClass::Bulk, vec![0; 9]).await,
            Err(BondRuntimeError::FlowControlBlocked { limit: 8, .. })
        ));

        client
            .send(stream, TrafficClass::Bulk, b"abcdefgh".to_vec())
            .await
            .unwrap();
        assert_eq!(receive_bytes(&mut server, stream, 8).await, b"abcdefgh");
        send_after_credit(&client, stream, TrafficClass::Bulk, b"ijklmnop").await;
        assert_eq!(receive_bytes(&mut server, stream, 8).await, b"ijklmnop");

        client.close_stream(stream).await.unwrap();
        assert_eq!(
            next_event(&mut server).await,
            RuntimeEvent::StreamFinished { stream_id: stream }
        );
        server
            .send(stream, TrafficClass::Bulk, b"reply".to_vec())
            .await
            .unwrap();
        assert_eq!(receive_bytes(&mut client, stream, 5).await, b"reply");
        server.close_stream(stream).await.unwrap();
        assert_eq!(
            next_event(&mut client).await,
            RuntimeEvent::StreamFinished { stream_id: stream }
        );

        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
    }

    #[tokio::test]
    async fn peer_close_before_local_shutdown_is_clean() {
        let (client, server) = strict_pair();
        let client_shutdown = tokio::spawn(client.shutdown());
        tokio::time::timeout(Duration::from_secs(2), client_shutdown)
            .await
            .expect("initiating shutdown timed out")
            .expect("initiating shutdown task failed")
            .unwrap();

        tokio::time::timeout(Duration::from_secs(2), server.shutdown())
            .await
            .expect("passive shutdown timed out")
            .unwrap();
    }

    #[tokio::test]
    async fn authenticated_probes_measure_idle_lanes_and_fail_a_silent_lane() {
        let lane = LaneConfig::new(
            LaneId::new(1).unwrap(),
            FailureDomain::new(1).unwrap(),
            Duration::from_millis(25),
            1_000_000,
        )
        .unwrap();
        let config = BondRuntimeConfig {
            session_id: 0x11_1e,
            retransmit_after: Duration::from_millis(300),
            retransmit_scan_interval: Duration::from_millis(10),
            ..BondRuntimeConfig::default()
        };
        let (client_io, server_io) = tokio::io::duplex(64 * 1024);
        let client = BondRuntime::spawn(
            config,
            vec![RuntimeLane::new_for_test(
                lane, client_io, [0x11; 32], [0x22; 32],
            )],
        )
        .unwrap();
        let server = BondRuntime::spawn(
            config,
            vec![RuntimeLane::new_for_test(
                lane, server_io, [0x22; 32], [0x11; 32],
            )],
        )
        .unwrap();
        tokio::time::timeout(Duration::from_secs(2), async {
            loop {
                let stats = client.statistics().await.unwrap();
                if stats.ping_frames > 0 && stats.lanes[0].delivery_measured {
                    assert_eq!(stats.liveness_failures, 0);
                    break;
                }
                tokio::time::sleep(Duration::from_millis(10)).await;
            }
        })
        .await
        .expect("idle authenticated probes did not complete");
        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();

        let (silent_io, _silent_peer) = tokio::io::duplex(64 * 1024);
        let silent = BondRuntime::spawn(
            BondRuntimeConfig {
                session_id: 0x51_1e,
                retransmit_after: Duration::from_millis(100),
                retransmit_scan_interval: Duration::from_millis(10),
                ..BondRuntimeConfig::default()
            },
            vec![RuntimeLane::new_for_test(
                lane, silent_io, [0x33; 32], [0x44; 32],
            )],
        )
        .unwrap();
        tokio::time::timeout(Duration::from_secs(1), async {
            loop {
                let stats = silent.statistics().await.unwrap();
                if !stats.lanes[0].active {
                    assert!(stats.ping_frames > 0);
                    assert_eq!(stats.liveness_failures, 1);
                    break;
                }
                tokio::time::sleep(Duration::from_millis(10)).await;
            }
        })
        .await
        .expect("silent lane was not failed by its liveness deadline");
    }

    #[tokio::test(start_paused = true)]
    async fn suspend_sized_time_jump_expires_only_a_written_probe_once() {
        let lane = LaneConfig::new(
            LaneId::new(1).unwrap(),
            FailureDomain::new(1).unwrap(),
            Duration::from_millis(25),
            1_000_000,
        )
        .unwrap();
        let (silent_io, _silent_peer) = tokio::io::duplex(64 * 1024);
        let runtime = BondRuntime::spawn(
            BondRuntimeConfig {
                session_id: 0x5a_5e,
                retransmit_after: Duration::from_millis(100),
                retransmit_scan_interval: Duration::from_millis(10),
                ..BondRuntimeConfig::default()
            },
            vec![RuntimeLane::new_for_test(
                lane, silent_io, [0x55; 32], [0xaa; 32],
            )],
        )
        .unwrap();

        let initial = runtime.statistics().await.unwrap();
        assert!(initial.lanes[0].active);
        tokio::task::yield_now().await;
        tokio::time::advance(Duration::from_secs(24 * 60 * 60)).await;
        for _ in 0..32 {
            tokio::task::yield_now().await;
        }
        let after_resume = runtime.statistics().await.unwrap();
        assert!(after_resume.lanes[0].active);
        assert_eq!(after_resume.ping_frames, 1);
        assert_eq!(after_resume.liveness_failures, 0);

        tokio::time::advance(Duration::from_millis(99)).await;
        for _ in 0..8 {
            tokio::task::yield_now().await;
        }
        assert!(runtime.statistics().await.unwrap().lanes[0].active);

        tokio::time::advance(Duration::from_millis(11)).await;
        for _ in 0..32 {
            tokio::task::yield_now().await;
        }
        let failed = runtime.statistics().await.unwrap();
        assert!(!failed.lanes[0].active);
        assert_eq!(failed.ping_frames, 1);
        assert_eq!(failed.liveness_failures, 1);

        tokio::time::advance(Duration::from_secs(24 * 60 * 60)).await;
        for _ in 0..8 {
            tokio::task::yield_now().await;
        }
        let settled = runtime.statistics().await.unwrap();
        assert_eq!(settled.ping_frames, 1);
        assert_eq!(settled.liveness_failures, 1);
    }

    #[tokio::test]
    async fn reset_is_stream_scoped_and_multiple_opens_survive() {
        let (mut client, mut server) = strict_pair();
        let first = StreamId::new(1).unwrap();
        let second = StreamId::new(2).unwrap();
        client
            .open_stream(first, TrafficClass::Realtime)
            .await
            .unwrap();
        assert!(matches!(
            next_event(&mut server).await,
            RuntimeEvent::StreamOpened { stream_id, .. } if stream_id == first
        ));
        server
            .open_stream(second, TrafficClass::Bulk)
            .await
            .unwrap();
        assert!(matches!(
            next_event(&mut client).await,
            RuntimeEvent::StreamOpened { stream_id, .. } if stream_id == second
        ));

        client.reset_stream(first, 42).await.unwrap();
        assert_eq!(
            next_event(&mut server).await,
            RuntimeEvent::StreamReset {
                stream_id: first,
                code: 42,
            }
        );
        server.reset_stream(second, 7).await.unwrap();
        assert_eq!(
            next_event(&mut client).await,
            RuntimeEvent::StreamReset {
                stream_id: second,
                code: 7,
            }
        );

        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
    }
}
