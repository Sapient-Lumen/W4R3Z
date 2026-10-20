use std::collections::{BTreeMap, VecDeque};
use std::error::Error;
use std::fmt;
use std::time::Duration;

use bytes::Bytes;

use crate::control::{validate_ack_ranges, AckRange};
use crate::frame::{Frame, FrameFlags, FrameKind, ProtocolError, MAX_FRAME_PAYLOAD};
use crate::scheduler::{
    BondScheduler, LaneConfig, LaneId, ScheduleDecision, SchedulerError, Timestamp, TrafficClass,
};

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub struct StreamId(u64);

impl StreamId {
    pub fn new(value: u64) -> Result<Self, SenderError> {
        if value == 0 {
            Err(SenderError::ZeroStreamId)
        } else {
            Ok(Self(value))
        }
    }

    pub const fn get(self) -> u64 {
        self.0
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct BulkChunkConfig {
    pub minimum_payload: usize,
    pub maximum_payload: usize,
}

impl BulkChunkConfig {
    pub const fn fixed(payload: usize) -> Self {
        Self {
            minimum_payload: payload,
            maximum_payload: payload,
        }
    }

    fn validate(self) -> Result<Self, SenderError> {
        if self.minimum_payload == 0
            || self.minimum_payload > self.maximum_payload
            || self.maximum_payload > MAX_FRAME_PAYLOAD
        {
            return Err(SenderError::InvalidBulkChunkBounds {
                minimum: self.minimum_payload,
                maximum: self.maximum_payload,
            });
        }
        Ok(self)
    }
}

impl Default for BulkChunkConfig {
    fn default() -> Self {
        Self {
            minimum_payload: 16 * 1024,
            maximum_payload: MAX_FRAME_PAYLOAD,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct SenderConfig {
    pub max_chunk_payload: usize,
    pub bulk_chunk: BulkChunkConfig,
    pub max_unacknowledged_bytes: usize,
    pub max_unacknowledged_chunks: usize,
    pub redundant_realtime: bool,
}

impl Default for SenderConfig {
    fn default() -> Self {
        Self {
            max_chunk_payload: 16 * 1024,
            bulk_chunk: BulkChunkConfig::default(),
            max_unacknowledged_bytes: 8 * 1024 * 1024,
            max_unacknowledged_chunks: 4_096,
            redundant_realtime: false,
        }
    }
}

impl SenderConfig {
    fn validate(self) -> Result<Self, SenderError> {
        if self.max_chunk_payload == 0 || self.max_chunk_payload > MAX_FRAME_PAYLOAD {
            return Err(SenderError::InvalidChunkSize(self.max_chunk_payload));
        }
        let bulk_chunk = self.bulk_chunk.validate()?;
        if self.max_unacknowledged_bytes < self.max_chunk_payload.max(bulk_chunk.maximum_payload) {
            return Err(SenderError::InvalidUnacknowledgedLimit(
                self.max_unacknowledged_bytes,
            ));
        }
        if self.max_unacknowledged_chunks == 0 {
            return Err(SenderError::InvalidUnacknowledgedChunkLimit);
        }
        Ok(Self { bulk_chunk, ..self })
    }
}

#[derive(Debug)]
struct BulkChunkController {
    config: BulkChunkConfig,
    pressure_limit: usize,
    clean_acknowledged_bytes: usize,
}

impl BulkChunkController {
    fn new(config: BulkChunkConfig) -> Self {
        Self {
            config,
            pressure_limit: config.maximum_payload,
            clean_acknowledged_bytes: 0,
        }
    }

    const fn maximum_payload(&self) -> usize {
        self.pressure_limit
    }

    fn observe_acknowledgement(&mut self, bytes: usize, reordered: bool) {
        if bytes == 0 {
            return;
        }
        if reordered {
            self.apply_pressure();
            return;
        }
        if self.pressure_limit == self.config.maximum_payload {
            self.clean_acknowledged_bytes = 0;
            return;
        }
        self.clean_acknowledged_bytes = self.clean_acknowledged_bytes.saturating_add(bytes);
        loop {
            let growth_threshold = self.pressure_limit.saturating_mul(8);
            if self.clean_acknowledged_bytes < growth_threshold {
                break;
            }
            self.clean_acknowledged_bytes -= growth_threshold;
            self.pressure_limit = self
                .pressure_limit
                .saturating_mul(2)
                .min(self.config.maximum_payload);
            if self.pressure_limit == self.config.maximum_payload {
                self.clean_acknowledged_bytes = 0;
                break;
            }
        }
    }

    fn apply_pressure(&mut self) {
        self.pressure_limit = (self.pressure_limit / 2).max(self.config.minimum_payload);
        self.clean_acknowledged_bytes = 0;
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum TransmissionReason {
    NewData,
    RealtimeRedundancy,
    LaneFailure,
    Timeout,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ScheduledFrame {
    pub lane_id: LaneId,
    pub predicted_delivery_at: Timestamp,
    pub reason: TransmissionReason,
    pub transmission_count: u32,
    pub frame: Frame,
}

#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct Acknowledgement {
    pub released_bytes: usize,
    pub chunks: Vec<AcknowledgedChunk>,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct AcknowledgedChunk {
    pub lane_id: LaneId,
    pub bytes: usize,
    pub last_sent_at: Timestamp,
    pub transmission_count: u32,
}

#[derive(Clone, Debug)]
struct PendingChunk {
    class: TrafficClass,
    payload: Bytes,
    latest_lane: LaneId,
    redundant_lane: Option<LaneId>,
    last_sent_at: Timestamp,
    transmission_count: u32,
}

#[derive(Debug)]
pub struct BondSender {
    session_id: u64,
    config: SenderConfig,
    scheduler: BondScheduler,
    next_offsets: BTreeMap<StreamId, u64>,
    acknowledged_offsets: BTreeMap<StreamId, u64>,
    pending: BTreeMap<(StreamId, u64), PendingChunk>,
    acknowledgement_release_keys: Vec<(StreamId, u64)>,
    unacknowledged_bytes: usize,
    bulk_chunks: BulkChunkController,
    #[cfg(test)]
    last_acknowledgement_scan_chunks: usize,
}

impl BondSender {
    pub fn new(
        session_id: u64,
        config: SenderConfig,
        scheduler: BondScheduler,
    ) -> Result<Self, SenderError> {
        if session_id == 0 {
            return Err(SenderError::ZeroSessionId);
        }
        let config = config.validate()?;
        Ok(Self {
            session_id,
            config,
            scheduler,
            next_offsets: BTreeMap::new(),
            acknowledged_offsets: BTreeMap::new(),
            pending: BTreeMap::new(),
            acknowledgement_release_keys: Vec::new(),
            unacknowledged_bytes: 0,
            bulk_chunks: BulkChunkController::new(config.bulk_chunk),
            #[cfg(test)]
            last_acknowledgement_scan_chunks: 0,
        })
    }

    pub fn enqueue(
        &mut self,
        stream_id: StreamId,
        class: TrafficClass,
        bytes: &[u8],
        now: Timestamp,
    ) -> Result<Vec<ScheduledFrame>, SenderError> {
        self.enqueue_shared(stream_id, class, Bytes::copy_from_slice(bytes), now)
    }

    pub fn enqueue_shared(
        &mut self,
        stream_id: StreamId,
        class: TrafficClass,
        bytes: Bytes,
        now: Timestamp,
    ) -> Result<Vec<ScheduledFrame>, SenderError> {
        let mut scheduled =
            Vec::with_capacity(self.maximum_scheduled_frame_count(class, bytes.len()));
        self.enqueue_shared_with(stream_id, class, bytes, now, |frame| {
            scheduled.push(frame);
        })?;
        Ok(scheduled)
    }

    pub fn enqueue_shared_into(
        &mut self,
        stream_id: StreamId,
        class: TrafficClass,
        bytes: Bytes,
        now: Timestamp,
        scheduled: &mut VecDeque<ScheduledFrame>,
    ) -> Result<(), SenderError> {
        scheduled.clear();
        let result = self.enqueue_shared_with(stream_id, class, bytes, now, |frame| {
            scheduled.push_back(frame);
        });
        if result.is_err() {
            scheduled.clear();
        }
        result
    }

    fn enqueue_shared_with(
        &mut self,
        stream_id: StreamId,
        class: TrafficClass,
        bytes: Bytes,
        now: Timestamp,
        mut emit: impl FnMut(ScheduledFrame),
    ) -> Result<(), SenderError> {
        if bytes.is_empty() {
            return Ok(());
        }
        let attempted = self
            .unacknowledged_bytes
            .checked_add(bytes.len())
            .ok_or(SenderError::AccountingOverflow)?;
        if attempted > self.config.max_unacknowledged_bytes {
            return Err(SenderError::Backpressure {
                attempted,
                limit: self.config.max_unacknowledged_bytes,
            });
        }
        let new_chunks = self.maximum_new_chunk_count(class, bytes.len());
        let attempted_chunks = self
            .pending
            .len()
            .checked_add(new_chunks)
            .ok_or(SenderError::AccountingOverflow)?;
        if attempted_chunks > self.config.max_unacknowledged_chunks {
            return Err(SenderError::ChunkBackpressure {
                attempted: attempted_chunks,
                limit: self.config.max_unacknowledged_chunks,
            });
        }

        let start = self.next_offsets.get(&stream_id).copied().unwrap_or(0);
        let total_length = u64::try_from(bytes.len()).map_err(|_| SenderError::OffsetOverflow)?;
        let final_offset = start
            .checked_add(total_length)
            .ok_or(SenderError::OffsetOverflow)?;
        let mut offset = start;

        let mut cursor = 0;
        while cursor < bytes.len() {
            let remaining = bytes.len() - cursor;
            let (payload_bytes, decision, redundant) = if class.is_latency_sensitive(remaining) {
                let payload_bytes = remaining.min(self.config.max_chunk_payload);
                if self.config.redundant_realtime
                    && class.is_redundant_realtime_candidate(payload_bytes)
                {
                    let (primary, redundant) =
                        self.scheduler
                            .schedule_redundant_realtime(class, payload_bytes, now)?;
                    (payload_bytes, primary, redundant)
                } else {
                    (
                        payload_bytes,
                        self.scheduler.schedule(class, payload_bytes, now)?,
                        None,
                    )
                }
            } else {
                let sized = self.scheduler.schedule_adaptive_bulk(
                    self.config.bulk_chunk.minimum_payload,
                    self.bulk_chunks.maximum_payload(),
                    remaining,
                    now,
                )?;
                (sized.payload_bytes, sized.decision, None)
            };
            let end = cursor + payload_bytes;
            let payload = bytes.slice(cursor..end);
            let frame = Frame::new(
                FrameKind::Data,
                FrameFlags::NONE,
                self.session_id,
                stream_id.get(),
                offset,
                payload.clone(),
            )?;
            self.pending.insert(
                (stream_id, offset),
                PendingChunk {
                    class,
                    payload,
                    latest_lane: decision.lane_id,
                    redundant_lane: redundant.map(|decision| decision.lane_id),
                    last_sent_at: now,
                    transmission_count: 1,
                },
            );
            if let Some(redundant) = redundant {
                emit(scheduled_frame(
                    decision,
                    TransmissionReason::NewData,
                    1,
                    frame.clone(),
                ));
                emit(scheduled_frame(
                    redundant,
                    TransmissionReason::RealtimeRedundancy,
                    1,
                    frame,
                ));
            } else {
                emit(scheduled_frame(
                    decision,
                    TransmissionReason::NewData,
                    1,
                    frame,
                ));
            }
            offset = offset
                .checked_add((end - cursor) as u64)
                .ok_or(SenderError::OffsetOverflow)?;
            cursor = end;
        }

        self.next_offsets.insert(stream_id, final_offset);
        self.unacknowledged_bytes = attempted;
        Ok(())
    }

    fn maximum_new_chunk_count(&self, class: TrafficClass, bytes: usize) -> usize {
        let minimum = if class.is_latency_sensitive(bytes) {
            self.config.max_chunk_payload
        } else {
            self.config.bulk_chunk.minimum_payload
        };
        bytes.div_ceil(minimum)
    }

    fn maximum_scheduled_frame_count(&self, class: TrafficClass, bytes: usize) -> usize {
        let chunks = self.maximum_new_chunk_count(class, bytes);
        if self.config.redundant_realtime && class.is_redundant_realtime_candidate(bytes) {
            chunks.saturating_mul(2)
        } else {
            chunks
        }
    }

    pub fn acknowledge(
        &mut self,
        stream_id: StreamId,
        through_offset: u64,
    ) -> Result<Acknowledgement, SenderError> {
        self.acknowledge_selective(stream_id, through_offset, &[])
    }

    pub fn acknowledge_selective(
        &mut self,
        stream_id: StreamId,
        through_offset: u64,
        ranges: &[AckRange],
    ) -> Result<Acknowledgement, SenderError> {
        let mut chunks = Vec::new();
        let released_bytes = self.acknowledge_selective_attributed_into(
            stream_id,
            through_offset,
            ranges,
            None,
            &mut chunks,
        )?;
        Ok(Acknowledgement {
            released_bytes,
            chunks,
        })
    }

    pub fn acknowledge_into(
        &mut self,
        stream_id: StreamId,
        through_offset: u64,
        acknowledged: &mut Vec<AcknowledgedChunk>,
    ) -> Result<usize, SenderError> {
        self.acknowledge_selective_into(stream_id, through_offset, &[], acknowledged)
    }

    pub fn acknowledge_selective_into(
        &mut self,
        stream_id: StreamId,
        through_offset: u64,
        ranges: &[AckRange],
        acknowledged: &mut Vec<AcknowledgedChunk>,
    ) -> Result<usize, SenderError> {
        self.acknowledge_selective_attributed_into(
            stream_id,
            through_offset,
            ranges,
            None,
            acknowledged,
        )
    }

    pub fn acknowledge_selective_from_lane_into(
        &mut self,
        stream_id: StreamId,
        through_offset: u64,
        ranges: &[AckRange],
        acknowledgement_lane: LaneId,
        acknowledged: &mut Vec<AcknowledgedChunk>,
    ) -> Result<usize, SenderError> {
        self.acknowledge_selective_attributed_into(
            stream_id,
            through_offset,
            ranges,
            Some(acknowledgement_lane),
            acknowledged,
        )
    }

    fn acknowledge_selective_attributed_into(
        &mut self,
        stream_id: StreamId,
        through_offset: u64,
        ranges: &[AckRange],
        acknowledgement_lane: Option<LaneId>,
        acknowledged: &mut Vec<AcknowledgedChunk>,
    ) -> Result<usize, SenderError> {
        acknowledged.clear();
        self.acknowledgement_release_keys.clear();
        #[cfg(test)]
        {
            self.last_acknowledgement_scan_chunks = 0;
        }
        validate_ack_ranges(through_offset, ranges).map_err(SenderError::Control)?;
        let previous = self
            .acknowledged_offsets
            .get(&stream_id)
            .copied()
            .unwrap_or(0);
        let sent = self.next_offsets.get(&stream_id).copied().unwrap_or(0);
        let highest_received = ranges.last().map_or(through_offset, |range| range.end);
        if through_offset > sent || highest_received > sent {
            return Err(SenderError::InvalidAcknowledgement {
                previous,
                received: highest_received,
                sent,
            });
        }
        let mut released = 0_usize;
        let mut released_bulk_bytes = 0_usize;
        for (&key @ (_, offset), chunk) in
            self.pending.range((stream_id, 0)..=(stream_id, u64::MAX))
        {
            #[cfg(test)]
            {
                self.last_acknowledgement_scan_chunks += 1;
            }
            let end = offset
                .checked_add(
                    u64::try_from(chunk.payload.len())
                        .map_err(|_| SenderError::AccountingOverflow)?,
                )
                .ok_or(SenderError::AccountingOverflow)?;
            let cumulative_split = offset < through_offset && through_offset < end;
            let mut released_by_range = false;
            let mut range_split = false;
            for range in ranges {
                if range.end <= offset {
                    continue;
                }
                if range.start >= end {
                    break;
                }
                if range.contains(offset, end) {
                    released_by_range = true;
                } else {
                    range_split = true;
                }
            }
            if cumulative_split || range_split {
                self.acknowledgement_release_keys.clear();
                return Err(SenderError::PartialChunkAcknowledgement(through_offset));
            }
            if end <= through_offset || released_by_range {
                released = released
                    .checked_add(chunk.payload.len())
                    .ok_or(SenderError::AccountingOverflow)?;
                if !chunk.class.is_latency_sensitive(chunk.payload.len()) {
                    released_bulk_bytes = released_bulk_bytes
                        .checked_add(chunk.payload.len())
                        .ok_or(SenderError::AccountingOverflow)?;
                }
                self.acknowledgement_release_keys.push(key);
            }
        }
        let remaining = self
            .unacknowledged_bytes
            .checked_sub(released)
            .ok_or(SenderError::AccountingOverflow)?;
        acknowledged.reserve(self.acknowledgement_release_keys.len());
        for key in self.acknowledgement_release_keys.drain(..) {
            let chunk = self
                .pending
                .remove(&key)
                .expect("acknowledgement release key came from the pending ledger");
            let lane_id = acknowledgement_lane
                .filter(|lane_id| chunk.redundant_lane == Some(*lane_id))
                .unwrap_or(chunk.latest_lane);
            acknowledged.push(AcknowledgedChunk {
                lane_id,
                bytes: chunk.payload.len(),
                last_sent_at: chunk.last_sent_at,
                transmission_count: chunk.transmission_count,
            });
        }
        self.unacknowledged_bytes = remaining;
        self.acknowledged_offsets
            .insert(stream_id, previous.max(through_offset));
        self.bulk_chunks
            .observe_acknowledgement(released_bulk_bytes, !ranges.is_empty());
        Ok(released)
    }

    pub fn fail_lane(
        &mut self,
        lane_id: LaneId,
        now: Timestamp,
    ) -> Result<Vec<ScheduledFrame>, SenderError> {
        self.scheduler.set_lane_active(lane_id, false, now)?;
        if self.scheduler.active_lane_count() == 0 {
            return Ok(Vec::new());
        }
        let keys: Vec<_> = self
            .pending
            .iter()
            .filter(|(_, chunk)| chunk.latest_lane == lane_id)
            .map(|(key, _)| *key)
            .collect();
        self.retransmit(keys, now, TransmissionReason::LaneFailure, Some(lane_id))
    }

    pub fn restore_lane(
        &mut self,
        lane: LaneConfig,
        now: Timestamp,
    ) -> Result<Vec<ScheduledFrame>, SenderError> {
        let resumes_stranded_payload = self.scheduler.active_lane_count() == 0;
        self.scheduler.restore_lane(lane, now)?;
        if !resumes_stranded_payload {
            return Ok(Vec::new());
        }
        let keys = self.pending.keys().copied().collect();
        self.retransmit(keys, now, TransmissionReason::LaneFailure, None)
    }

    pub fn retransmit_due_adaptive(
        &mut self,
        now: Timestamp,
        minimum: Duration,
        maximum: Duration,
    ) -> Result<Vec<ScheduledFrame>, SenderError> {
        let mut keys = Vec::new();
        for (key, chunk) in &self.pending {
            let timeout =
                self.scheduler
                    .retransmission_timeout(chunk.latest_lane, minimum, maximum)?;
            let delay =
                u64::try_from(timeout.as_micros()).map_err(|_| SenderError::TimestampOverflow)?;
            if chunk
                .last_sent_at
                .as_micros()
                .checked_add(delay)
                .is_some_and(|deadline| deadline <= now.as_micros())
            {
                keys.push(*key);
            }
        }
        self.retransmit(keys, now, TransmissionReason::Timeout, None)
    }

    pub fn scheduler(&self) -> &BondScheduler {
        &self.scheduler
    }

    pub fn scheduler_mut(&mut self) -> &mut BondScheduler {
        &mut self.scheduler
    }

    pub const fn unacknowledged_bytes(&self) -> usize {
        self.unacknowledged_bytes
    }

    pub const fn bulk_chunk_pressure_limit(&self) -> usize {
        self.bulk_chunks.maximum_payload()
    }

    pub fn stream_unacknowledged_bytes(&self, stream_id: StreamId) -> usize {
        self.pending
            .iter()
            .filter(|((pending_stream, _), _)| *pending_stream == stream_id)
            .map(|(_, chunk)| chunk.payload.len())
            .sum()
    }

    pub fn abandon_stream(&mut self, stream_id: StreamId) -> Result<usize, SenderError> {
        let keys: Vec<_> = self
            .pending
            .range((stream_id, 0)..=(stream_id, u64::MAX))
            .map(|(key, _)| *key)
            .collect();
        let mut released = 0_usize;
        for key in keys {
            if let Some(chunk) = self.pending.remove(&key) {
                released = released
                    .checked_add(chunk.payload.len())
                    .ok_or(SenderError::AccountingOverflow)?;
            }
        }
        self.unacknowledged_bytes = self
            .unacknowledged_bytes
            .checked_sub(released)
            .ok_or(SenderError::AccountingOverflow)?;
        self.next_offsets.remove(&stream_id);
        self.acknowledged_offsets.remove(&stream_id);
        Ok(released)
    }

    pub fn next_offset(&self, stream_id: StreamId) -> u64 {
        self.next_offsets.get(&stream_id).copied().unwrap_or(0)
    }

    fn retransmit(
        &mut self,
        keys: Vec<(StreamId, u64)>,
        now: Timestamp,
        reason: TransmissionReason,
        failed_lane: Option<LaneId>,
    ) -> Result<Vec<ScheduledFrame>, SenderError> {
        if self.scheduler.active_lane_count() == 0 {
            return Ok(Vec::new());
        }
        if reason == TransmissionReason::Timeout
            && keys.iter().any(|key| {
                self.pending
                    .get(key)
                    .is_some_and(|chunk| !chunk.class.is_latency_sensitive(chunk.payload.len()))
            })
        {
            self.bulk_chunks.apply_pressure();
        }
        let mut scheduled = Vec::with_capacity(keys.len());
        for key @ (stream_id, offset) in keys {
            let chunk = self.pending.get(&key).expect("pending key exists");
            let excluded = failed_lane.or(Some(chunk.latest_lane));
            let decision = match self.scheduler.schedule_excluding(
                chunk.class,
                chunk.payload.len(),
                now,
                excluded,
            ) {
                Ok(decision) => decision,
                Err(SchedulerError::NoHealthyLane) if failed_lane.is_none() => self
                    .scheduler
                    .schedule(chunk.class, chunk.payload.len(), now)?,
                Err(error) => return Err(error.into()),
            };
            let chunk = self.pending.get_mut(&key).expect("pending key exists");
            chunk.latest_lane = decision.lane_id;
            chunk.redundant_lane = None;
            chunk.last_sent_at = now;
            chunk.transmission_count = chunk
                .transmission_count
                .checked_add(1)
                .ok_or(SenderError::TransmissionCountOverflow)?;
            let frame = Frame::new(
                FrameKind::Data,
                FrameFlags::RETRANSMISSION,
                self.session_id,
                stream_id.get(),
                offset,
                chunk.payload.clone(),
            )?;
            scheduled.push(scheduled_frame(
                decision,
                reason,
                chunk.transmission_count,
                frame,
            ));
        }
        Ok(scheduled)
    }
}

fn scheduled_frame(
    decision: ScheduleDecision,
    reason: TransmissionReason,
    transmission_count: u32,
    frame: Frame,
) -> ScheduledFrame {
    ScheduledFrame {
        lane_id: decision.lane_id,
        predicted_delivery_at: decision.predicted_delivery_at,
        reason,
        transmission_count,
        frame,
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum SenderError {
    ZeroSessionId,
    ZeroStreamId,
    InvalidChunkSize(usize),
    InvalidBulkChunkBounds {
        minimum: usize,
        maximum: usize,
    },
    InvalidUnacknowledgedLimit(usize),
    InvalidUnacknowledgedChunkLimit,
    Backpressure {
        attempted: usize,
        limit: usize,
    },
    ChunkBackpressure {
        attempted: usize,
        limit: usize,
    },
    InvalidAcknowledgement {
        previous: u64,
        received: u64,
        sent: u64,
    },
    PartialChunkAcknowledgement(u64),
    OffsetOverflow,
    TimestampOverflow,
    AccountingOverflow,
    TransmissionCountOverflow,
    Scheduler(SchedulerError),
    Protocol(ProtocolError),
    Control(crate::ControlError),
}

impl From<SchedulerError> for SenderError {
    fn from(value: SchedulerError) -> Self {
        Self::Scheduler(value)
    }
}

impl From<ProtocolError> for SenderError {
    fn from(value: ProtocolError) -> Self {
        Self::Protocol(value)
    }
}

impl fmt::Display for SenderError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::ZeroSessionId => write!(formatter, "bond sender session ID must be non-zero"),
            Self::ZeroStreamId => write!(formatter, "bond stream ID must be non-zero"),
            Self::InvalidChunkSize(size) => write!(formatter, "invalid bond chunk size {size}"),
            Self::InvalidBulkChunkBounds { minimum, maximum } => write!(
                formatter,
                "invalid adaptive bulk chunk bounds {minimum}..={maximum}"
            ),
            Self::InvalidUnacknowledgedLimit(limit) => {
                write!(formatter, "invalid unacknowledged-byte limit {limit}")
            }
            Self::InvalidUnacknowledgedChunkLimit => {
                write!(formatter, "unacknowledged-chunk limit must be non-zero")
            }
            Self::Backpressure { attempted, limit } => write!(
                formatter,
                "bond send window is full: attempted {attempted}, limit {limit}"
            ),
            Self::ChunkBackpressure { attempted, limit } => write!(
                formatter,
                "bond chunk window is full: attempted {attempted}, limit {limit}"
            ),
            Self::InvalidAcknowledgement {
                previous,
                received,
                sent,
            } => write!(
                formatter,
                "invalid acknowledgement {received}: previous {previous}, sent {sent}"
            ),
            Self::PartialChunkAcknowledgement(offset) => {
                write!(formatter, "acknowledgement {offset} splits a pending chunk")
            }
            Self::OffsetOverflow => write!(formatter, "bond stream offset overflow"),
            Self::TimestampOverflow => write!(formatter, "bond timestamp overflow"),
            Self::AccountingOverflow => write!(formatter, "bond byte accounting overflow"),
            Self::TransmissionCountOverflow => write!(formatter, "transmission count overflow"),
            Self::Scheduler(error) => error.fmt(formatter),
            Self::Protocol(error) => error.fmt(formatter),
            Self::Control(error) => error.fmt(formatter),
        }
    }
}

impl Error for SenderError {}

#[cfg(test)]
mod tests {
    use std::collections::{BTreeSet, VecDeque};
    use std::time::Duration;

    use bytes::Bytes;

    use crate::{
        AckRange, BondScheduler, FailureDomain, FrameFlags, LaneConfig, LaneId, Reassembler,
        SchedulerConfig, Timestamp, TrafficClass,
    };

    use super::{
        BondSender, BulkChunkConfig, SenderConfig, SenderError, StreamId, TransmissionReason,
    };

    fn lane(id: u32, rtt_ms: u64, rate_mbps: u64) -> LaneConfig {
        LaneConfig::new(
            LaneId::new(id).unwrap(),
            FailureDomain::new(id as u64).unwrap(),
            Duration::from_millis(rtt_ms),
            rate_mbps * 1_000_000,
        )
        .unwrap()
    }

    fn sender(lanes: &[LaneConfig], config: SenderConfig) -> BondSender {
        let mut scheduler = BondScheduler::new(SchedulerConfig::default()).unwrap();
        for lane in lanes {
            scheduler.add_lane(*lane).unwrap();
        }
        BondSender::new(9, config, scheduler).unwrap()
    }

    #[test]
    fn bulk_is_striped_and_reassembles_exactly_under_reordering() {
        let mut sender = sender(
            &[lane(1, 5, 10), lane(2, 40, 8), lane(3, 40, 2)],
            SenderConfig {
                max_chunk_payload: 4 * 1024,
                bulk_chunk: BulkChunkConfig::fixed(4 * 1024),
                max_unacknowledged_bytes: 256 * 1024,
                ..SenderConfig::default()
            },
        );
        let stream = StreamId::new(1).unwrap();
        let payload: Vec<_> = (0..128 * 1024).map(|index| (index % 251) as u8).collect();
        let scheduled = sender
            .enqueue(stream, TrafficClass::Bulk, &payload, Timestamp::ZERO)
            .unwrap();

        let used: BTreeSet<_> = scheduled.iter().map(|item| item.lane_id).collect();
        assert_eq!(
            used,
            [LaneId::new(2).unwrap(), LaneId::new(3).unwrap()].into()
        );
        assert!(scheduled
            .iter()
            .all(|item| item.lane_id != LaneId::new(1).unwrap()));

        let mut receiver = Reassembler::new(0, payload.len()).unwrap();
        let mut delivered = Vec::new();
        for item in scheduled.iter().rev() {
            delivered.extend_from_slice(
                &receiver
                    .insert(item.frame.header.offset, &item.frame.payload)
                    .unwrap()
                    .bytes,
            );
        }
        assert_eq!(delivered, payload);
    }

    #[test]
    fn adaptive_bulk_chunks_vary_by_path_and_reassemble_exactly() {
        let mut sender = sender(
            &[lane(1, 5, 100), lane(2, 40, 100), lane(3, 80, 2)],
            SenderConfig {
                max_chunk_payload: 16 * 1024,
                bulk_chunk: BulkChunkConfig {
                    minimum_payload: 4 * 1024,
                    maximum_payload: 64 * 1024,
                },
                max_unacknowledged_bytes: 512 * 1024,
                max_unacknowledged_chunks: 128,
                redundant_realtime: false,
            },
        );
        let stream = StreamId::new(2).unwrap();
        let payload: Vec<_> = (0..256 * 1024).map(|index| (index % 251) as u8).collect();
        let scheduled = sender
            .enqueue(stream, TrafficClass::Bulk, &payload, Timestamp::ZERO)
            .unwrap();

        let sizes: BTreeSet<_> = scheduled
            .iter()
            .map(|scheduled| scheduled.frame.payload.len())
            .collect();
        assert!(sizes.len() > 1, "adaptive sender emitted one fixed size");
        assert!(sizes.iter().all(|size| *size <= 64 * 1024));
        assert!(scheduled
            .iter()
            .all(|scheduled| scheduled.lane_id != LaneId::new(1).unwrap()));

        let mut receiver = Reassembler::new(0, payload.len()).unwrap();
        let mut delivered = Vec::new();
        for scheduled in scheduled.iter().rev() {
            delivered.extend_from_slice(
                &receiver
                    .insert(scheduled.frame.header.offset, &scheduled.frame.payload)
                    .unwrap()
                    .bytes,
            );
        }
        assert_eq!(delivered, payload);
    }

    #[test]
    fn selective_ack_pressure_reduces_then_clean_acks_restore_bulk_limit() {
        let mut sender = sender(
            &[lane(1, 5, 100), lane(2, 40, 100)],
            SenderConfig {
                max_chunk_payload: 16 * 1024,
                bulk_chunk: BulkChunkConfig {
                    minimum_payload: 4 * 1024,
                    maximum_payload: 16 * 1024,
                },
                max_unacknowledged_bytes: 128 * 1024,
                max_unacknowledged_chunks: 32,
                redundant_realtime: false,
            },
        );
        let stream = StreamId::new(4).unwrap();
        let initial = sender
            .enqueue(
                stream,
                TrafficClass::Bulk,
                &vec![0x5a; 32 * 1024],
                Timestamp::ZERO,
            )
            .unwrap();
        assert_eq!(initial.len(), 2);
        assert!(initial
            .iter()
            .all(|scheduled| scheduled.frame.payload.len() == 16 * 1024));

        sender
            .acknowledge_selective(stream, 0, &[AckRange::new(16 * 1024, 32 * 1024).unwrap()])
            .unwrap();
        assert_eq!(sender.bulk_chunk_pressure_limit(), 8 * 1024);
        sender.acknowledge(stream, 16 * 1024).unwrap();

        let recovery = sender
            .enqueue(
                stream,
                TrafficClass::Bulk,
                &vec![0x6b; 64 * 1024],
                Timestamp::from_micros(1_000_000),
            )
            .unwrap();
        assert!(recovery
            .iter()
            .all(|scheduled| scheduled.frame.payload.len() <= 8 * 1024));
        sender.acknowledge(stream, 96 * 1024).unwrap();
        assert_eq!(sender.bulk_chunk_pressure_limit(), 16 * 1024);
    }

    #[test]
    fn failed_lane_chunks_move_without_changing_offsets() {
        let mut sender = sender(
            &[lane(1, 5, 10), lane(2, 40, 10)],
            SenderConfig {
                max_chunk_payload: 4,
                bulk_chunk: BulkChunkConfig::fixed(4),
                max_unacknowledged_bytes: 32,
                ..SenderConfig::default()
            },
        );
        let stream = StreamId::new(3).unwrap();
        let initial = sender
            .enqueue(stream, TrafficClass::Bulk, b"abcdefgh", Timestamp::ZERO)
            .unwrap();
        assert!(initial
            .iter()
            .all(|item| item.lane_id == LaneId::new(2).unwrap()));

        let resent = sender
            .fail_lane(LaneId::new(2).unwrap(), Timestamp::from_micros(10))
            .unwrap();
        assert_eq!(resent.len(), initial.len());
        for (original, replacement) in initial.iter().zip(&resent) {
            assert_eq!(replacement.lane_id, LaneId::new(1).unwrap());
            assert_eq!(replacement.reason, TransmissionReason::LaneFailure);
            assert_eq!(
                replacement.frame.header.offset,
                original.frame.header.offset
            );
            assert_eq!(replacement.frame.payload, original.frame.payload);
            assert_eq!(
                replacement.frame.payload.as_ptr(),
                original.frame.payload.as_ptr()
            );
            assert!(replacement
                .frame
                .header
                .flags
                .contains(FrameFlags::RETRANSMISSION));
        }
    }

    #[test]
    fn realtime_redundancy_shares_payload_and_charges_one_logical_chunk() {
        let mut scheduler = BondScheduler::new(SchedulerConfig {
            low_latency_lane_count: 2,
            ..SchedulerConfig::default()
        })
        .unwrap();
        for config in [lane(1, 5, 10), lane(2, 20, 10), lane(3, 80, 10)] {
            scheduler.add_lane(config).unwrap();
        }
        let mut sender = BondSender::new(
            9,
            SenderConfig {
                max_chunk_payload: 2 * 1024,
                bulk_chunk: BulkChunkConfig::fixed(4),
                max_unacknowledged_bytes: 32 * 1024,
                max_unacknowledged_chunks: 128,
                redundant_realtime: true,
            },
            scheduler,
        )
        .unwrap();
        let stream = StreamId::new(3).unwrap();
        let payload = Bytes::from_static(b"typing");
        let scheduled = sender
            .enqueue_shared(
                stream,
                TrafficClass::Interactive,
                payload.clone(),
                Timestamp::ZERO,
            )
            .unwrap();

        assert_eq!(scheduled.len(), 2);
        assert_eq!(scheduled[0].reason, TransmissionReason::NewData);
        assert_eq!(scheduled[1].reason, TransmissionReason::RealtimeRedundancy);
        assert_eq!(scheduled[0].lane_id, LaneId::new(1).unwrap());
        assert_eq!(scheduled[1].lane_id, LaneId::new(2).unwrap());
        assert_eq!(scheduled[0].frame.header.offset, 0);
        assert_eq!(scheduled[1].frame.header.offset, 0);
        assert_eq!(scheduled[0].frame.payload, payload);
        assert_eq!(
            scheduled[0].frame.payload.as_ptr(),
            scheduled[1].frame.payload.as_ptr()
        );
        assert_eq!(sender.unacknowledged_bytes(), payload.len());

        let mut receiver = Reassembler::new(0, payload.len()).unwrap();
        let first = receiver
            .insert(
                scheduled[1].frame.header.offset,
                &scheduled[1].frame.payload,
            )
            .unwrap();
        assert_eq!(first.bytes, payload);
        let duplicate = receiver
            .insert(
                scheduled[0].frame.header.offset,
                &scheduled[0].frame.payload,
            )
            .unwrap();
        assert!(duplicate.bytes.is_empty());
        assert_eq!(duplicate.accepted_bytes, 0);

        let mut acknowledged = Vec::new();
        sender
            .acknowledge_selective_from_lane_into(
                stream,
                payload.len() as u64,
                &[],
                scheduled[1].lane_id,
                &mut acknowledged,
            )
            .unwrap();
        assert_eq!(acknowledged.len(), 1);
        assert_eq!(acknowledged[0].lane_id, scheduled[1].lane_id);
        assert_eq!(acknowledged[0].bytes, payload.len());
        assert_eq!(sender.unacknowledged_bytes(), 0);

        let bulk = sender
            .enqueue(stream, TrafficClass::Bulk, b"bulkbulk", Timestamp::ZERO)
            .unwrap();
        assert_eq!(bulk.len(), 2);
        assert!(bulk
            .iter()
            .all(|frame| frame.reason == TransmissionReason::NewData));
    }

    #[test]
    fn sole_lane_failure_defers_payload_until_the_lane_returns() {
        let only_lane = lane(1, 5, 10);
        let mut sender = sender(
            &[only_lane],
            SenderConfig {
                max_chunk_payload: 4,
                bulk_chunk: BulkChunkConfig::fixed(4),
                max_unacknowledged_bytes: 32,
                ..SenderConfig::default()
            },
        );
        let stream = StreamId::new(3).unwrap();
        let initial = sender
            .enqueue(stream, TrafficClass::Bulk, b"abcdefgh", Timestamp::ZERO)
            .unwrap();

        assert!(sender
            .fail_lane(only_lane.id, Timestamp::from_micros(10))
            .unwrap()
            .is_empty());
        assert_eq!(sender.unacknowledged_bytes(), 8);
        assert!(sender
            .retransmit_due_adaptive(
                Timestamp::from_micros(60_000_000),
                Duration::from_millis(1),
                Duration::from_secs(1),
            )
            .unwrap()
            .is_empty());

        let resumed = sender
            .restore_lane(only_lane, Timestamp::from_micros(20))
            .unwrap();
        assert_eq!(resumed.len(), initial.len());
        for (original, replacement) in initial.iter().zip(resumed) {
            assert_eq!(replacement.lane_id, only_lane.id);
            assert_eq!(replacement.reason, TransmissionReason::LaneFailure);
            assert_eq!(
                replacement.frame.header.offset,
                original.frame.header.offset
            );
            assert_eq!(replacement.frame.payload, original.frame.payload);
            assert_eq!(replacement.transmission_count, 2);
        }
    }

    #[test]
    fn retransmission_deadline_tracks_the_latest_lanes_rtt() {
        let mut sender = sender(
            &[lane(1, 50, 10)],
            SenderConfig {
                max_chunk_payload: 4,
                bulk_chunk: BulkChunkConfig {
                    minimum_payload: 4,
                    maximum_payload: 16,
                },
                max_unacknowledged_bytes: 32,
                ..SenderConfig::default()
            },
        );
        let stream = StreamId::new(5).unwrap();
        sender
            .enqueue(stream, TrafficClass::Bulk, b"data", Timestamp::ZERO)
            .unwrap();
        assert!(sender
            .retransmit_due_adaptive(
                Timestamp::from_micros(199_999),
                Duration::from_millis(20),
                Duration::from_secs(1),
            )
            .unwrap()
            .is_empty());
        let retransmitted = sender
            .retransmit_due_adaptive(
                Timestamp::from_micros(200_000),
                Duration::from_millis(20),
                Duration::from_secs(1),
            )
            .unwrap();
        assert_eq!(retransmitted.len(), 1);
        assert_eq!(retransmitted[0].reason, TransmissionReason::Timeout);
        assert_eq!(sender.bulk_chunk_pressure_limit(), 8);
    }

    #[test]
    fn sender_chunks_and_retransmissions_share_payload_storage() {
        let mut sender = sender(
            &[lane(1, 5, 10), lane(2, 40, 10)],
            SenderConfig {
                max_chunk_payload: 4,
                bulk_chunk: BulkChunkConfig {
                    minimum_payload: 4,
                    maximum_payload: 8,
                },
                max_unacknowledged_bytes: 32,
                ..SenderConfig::default()
            },
        );
        let stream = StreamId::new(7).unwrap();
        let payload = Bytes::from_static(b"abcdefgh");
        let first_payload_pointer = payload.as_ptr();
        let initial = sender
            .enqueue_shared(stream, TrafficClass::Bulk, payload, Timestamp::ZERO)
            .unwrap();
        assert_eq!(initial.len(), 1);
        assert_eq!(initial[0].frame.payload.as_ptr(), first_payload_pointer);

        let resent = sender
            .fail_lane(LaneId::new(2).unwrap(), Timestamp::from_micros(10))
            .unwrap();
        for (original, replacement) in initial.iter().zip(resent) {
            assert_eq!(
                original.frame.payload.as_ptr(),
                replacement.frame.payload.as_ptr()
            );
        }
    }

    #[test]
    fn caller_owned_schedule_queue_reuses_capacity() {
        let mut sender = sender(
            &[lane(1, 5, 10), lane(2, 40, 10)],
            SenderConfig {
                max_chunk_payload: 4,
                bulk_chunk: BulkChunkConfig::fixed(4),
                max_unacknowledged_bytes: 32,
                ..SenderConfig::default()
            },
        );
        let stream = StreamId::new(8).unwrap();
        let mut scheduled = VecDeque::with_capacity(2);
        let capacity = scheduled.capacity();

        sender
            .enqueue_shared_into(
                stream,
                TrafficClass::Bulk,
                Bytes::from_static(b"abcdefgh"),
                Timestamp::ZERO,
                &mut scheduled,
            )
            .unwrap();
        assert_eq!(scheduled.len(), 2);
        assert_eq!(scheduled.capacity(), capacity);

        let error = sender
            .enqueue_shared_into(
                stream,
                TrafficClass::Bulk,
                Bytes::from_static(b"this write exceeds the configured send window"),
                Timestamp::from_micros(5),
                &mut scheduled,
            )
            .unwrap_err();
        assert!(matches!(error, SenderError::Backpressure { .. }));
        assert!(scheduled.is_empty());
        assert_eq!(scheduled.capacity(), capacity);
        sender.acknowledge(stream, 8).unwrap();

        sender
            .enqueue_shared_into(
                stream,
                TrafficClass::Bulk,
                Bytes::from_static(b"ijklmnop"),
                Timestamp::from_micros(10),
                &mut scheduled,
            )
            .unwrap();
        assert_eq!(scheduled.len(), 2);
        assert_eq!(scheduled.capacity(), capacity);
        assert_eq!(scheduled[0].frame.header.offset, 8);
        assert_eq!(scheduled[1].frame.header.offset, 12);
    }

    #[test]
    fn send_window_applies_backpressure_and_acknowledgement_releases_it() {
        let mut byte_limited = sender(
            &[lane(1, 5, 10)],
            SenderConfig {
                max_chunk_payload: 4,
                bulk_chunk: BulkChunkConfig::fixed(4),
                max_unacknowledged_bytes: 8,
                max_unacknowledged_chunks: 2,
                redundant_realtime: false,
            },
        );
        let stream = StreamId::new(1).unwrap();
        byte_limited
            .enqueue(stream, TrafficClass::Bulk, b"abcdefgh", Timestamp::ZERO)
            .unwrap();
        assert!(matches!(
            byte_limited.enqueue(stream, TrafficClass::Bulk, b"i", Timestamp::ZERO),
            Err(SenderError::Backpressure {
                attempted: 9,
                limit: 8
            })
        ));
        assert_eq!(
            byte_limited.acknowledge(stream, 2),
            Err(SenderError::PartialChunkAcknowledgement(2))
        );
        let acknowledgement = byte_limited.acknowledge(stream, 4).unwrap();
        assert_eq!(acknowledgement.released_bytes, 4);
        assert_eq!(acknowledgement.chunks.len(), 1);
        assert_eq!(acknowledgement.chunks[0].lane_id, LaneId::new(1).unwrap());
        assert_eq!(byte_limited.unacknowledged_bytes(), 4);
        assert_eq!(
            byte_limited.acknowledge(stream, 0).unwrap(),
            super::Acknowledgement::default()
        );
        byte_limited
            .enqueue(stream, TrafficClass::Bulk, b"ijkl", Timestamp::ZERO)
            .unwrap();
        assert_eq!(byte_limited.next_offset(stream), 12);

        let mut chunk_limited = sender(
            &[lane(1, 5, 10)],
            SenderConfig {
                max_chunk_payload: 4,
                bulk_chunk: BulkChunkConfig::fixed(4),
                max_unacknowledged_bytes: 16,
                max_unacknowledged_chunks: 2,
                redundant_realtime: false,
            },
        );
        chunk_limited
            .enqueue(stream, TrafficClass::Bulk, b"abcdefgh", Timestamp::ZERO)
            .unwrap();
        assert!(matches!(
            chunk_limited.enqueue(stream, TrafficClass::Bulk, b"i", Timestamp::ZERO),
            Err(SenderError::ChunkBackpressure {
                attempted: 3,
                limit: 2
            })
        ));
    }

    #[test]
    fn selective_acknowledgements_release_sparse_whole_chunks() {
        let mut sender = sender(
            &[lane(1, 5, 10)],
            SenderConfig {
                max_chunk_payload: 4,
                bulk_chunk: BulkChunkConfig::fixed(4),
                max_unacknowledged_bytes: 16,
                max_unacknowledged_chunks: 4,
                redundant_realtime: false,
            },
        );
        let stream = StreamId::new(1).unwrap();
        sender
            .enqueue(stream, TrafficClass::Bulk, b"abcdefghijkl", Timestamp::ZERO)
            .unwrap();

        let mut acknowledged = Vec::with_capacity(4);
        let scratch_capacity = acknowledged.capacity();
        let sparse = sender
            .acknowledge_selective_into(
                stream,
                0,
                &[AckRange::new(4, 8).unwrap()],
                &mut acknowledged,
            )
            .unwrap();
        assert_eq!(sparse, 4);
        assert_eq!(acknowledged.len(), 1);
        assert_eq!(acknowledged[0].bytes, 4);
        assert_eq!(acknowledged.capacity(), scratch_capacity);
        assert_eq!(sender.unacknowledged_bytes(), 8);

        assert!(matches!(
            sender.acknowledge_selective_into(
                stream,
                0,
                &[AckRange::new(8, 11).unwrap()],
                &mut acknowledged,
            ),
            Err(SenderError::PartialChunkAcknowledgement(0))
        ));
        assert!(acknowledged.is_empty());
        assert_eq!(acknowledged.capacity(), scratch_capacity);
        assert!(sender
            .acknowledge_selective_into(
                stream,
                0,
                &[AckRange { start: 9, end: 8 }],
                &mut acknowledged,
            )
            .is_err());
        assert!(acknowledged.is_empty());
        assert_eq!(
            sender
                .acknowledge_into(stream, 4, &mut acknowledged)
                .unwrap(),
            4
        );
        assert_eq!(acknowledged.capacity(), scratch_capacity);
        assert_eq!(
            sender
                .acknowledge_into(stream, 12, &mut acknowledged)
                .unwrap(),
            4
        );
        assert_eq!(acknowledged.capacity(), scratch_capacity);
        assert_eq!(sender.unacknowledged_bytes(), 0);
    }

    #[test]
    fn acknowledgement_work_is_local_to_the_target_stream() {
        let mut sender = sender(
            &[lane(1, 5, 10)],
            SenderConfig {
                max_chunk_payload: 4,
                bulk_chunk: BulkChunkConfig::fixed(4),
                max_unacknowledged_bytes: 32,
                max_unacknowledged_chunks: 8,
                redundant_realtime: false,
            },
        );
        let first = StreamId::new(1).unwrap();
        let target = StreamId::new(2).unwrap();
        let third = StreamId::new(3).unwrap();
        for stream in [first, target, third] {
            sender
                .enqueue(stream, TrafficClass::Bulk, b"abcdefgh", Timestamp::ZERO)
                .unwrap();
        }

        let mut acknowledged = Vec::with_capacity(2);
        assert_eq!(
            sender
                .acknowledge_into(target, 8, &mut acknowledged)
                .unwrap(),
            8
        );
        assert_eq!(sender.last_acknowledgement_scan_chunks, 2);
        assert_eq!(sender.acknowledgement_release_keys.len(), 0);
        let release_capacity = sender.acknowledgement_release_keys.capacity();
        assert_eq!(sender.stream_unacknowledged_bytes(first), 8);
        assert_eq!(sender.stream_unacknowledged_bytes(target), 0);
        assert_eq!(sender.stream_unacknowledged_bytes(third), 8);

        assert_eq!(
            sender
                .acknowledge_into(first, 4, &mut acknowledged)
                .unwrap(),
            4
        );
        assert_eq!(sender.last_acknowledgement_scan_chunks, 2);
        assert_eq!(
            sender.acknowledgement_release_keys.capacity(),
            release_capacity
        );
        assert_eq!(sender.stream_unacknowledged_bytes(first), 4);
        assert_eq!(sender.stream_unacknowledged_bytes(third), 8);
    }

    #[test]
    fn abandoning_one_stream_releases_only_its_send_ledger() {
        let mut sender = sender(
            &[lane(1, 5, 10)],
            SenderConfig {
                max_chunk_payload: 4,
                bulk_chunk: BulkChunkConfig::fixed(4),
                max_unacknowledged_bytes: 16,
                max_unacknowledged_chunks: 4,
                redundant_realtime: false,
            },
        );
        let first = StreamId::new(1).unwrap();
        let second = StreamId::new(2).unwrap();
        sender
            .enqueue(first, TrafficClass::Bulk, b"abcdefgh", Timestamp::ZERO)
            .unwrap();
        sender
            .enqueue(second, TrafficClass::Bulk, b"ijkl", Timestamp::ZERO)
            .unwrap();

        assert_eq!(sender.stream_unacknowledged_bytes(first), 8);
        assert_eq!(sender.abandon_stream(first).unwrap(), 8);
        assert_eq!(sender.unacknowledged_bytes(), 4);
        assert_eq!(sender.next_offset(first), 0);
        assert_eq!(sender.next_offset(second), 4);
    }
}
