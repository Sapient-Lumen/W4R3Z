use std::collections::{BTreeMap, BTreeSet};
use std::error::Error;
use std::fmt;
use std::time::Duration;

use crate::{
    BondScheduler, BondSender, FailureDomain, LaneConfig, LaneId, Reassembler, ReassemblyError,
    SchedulerConfig, SchedulerError, SenderConfig, SenderError, StreamId, Timestamp, TrafficClass,
};

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct BondSelfTestReport {
    pub payload_bytes: usize,
    pub initial_frames: usize,
    pub retransmitted_frames: usize,
    pub bulk_lanes: usize,
    pub realtime_lane: LaneId,
    pub interactive_typing_lane: LaneId,
    pub interactive_bulk_lanes: usize,
    pub reorder_high_water: usize,
    pub scheduler_lanes: usize,
    pub scheduler_decisions: usize,
    pub scheduler_heap_scratch_bytes: usize,
}

pub fn embedded_self_test() -> Result<BondSelfTestReport, BondSelfTestError> {
    let scheduler_lanes = 8;
    let scheduler_decisions = 8_192;
    let mut scheduler_proof = BondScheduler::new(SchedulerConfig::default())?;
    for id in 1..=scheduler_lanes as u32 {
        scheduler_proof.add_lane(LaneConfig::new(
            LaneId::new(id)?,
            FailureDomain::new(u64::from(id))?,
            Duration::from_millis(u64::from(id) * 5),
            (4 + u64::from(id)) * 1_000_000,
        )?)?;
    }
    for index in 0..scheduler_decisions {
        let class = if index % 5 == 0 {
            TrafficClass::Realtime
        } else {
            TrafficClass::Bulk
        };
        scheduler_proof.schedule_excluding(
            class,
            16 * 1024,
            Timestamp::ZERO,
            (index % 7 == 0).then_some(LaneId::new(8)?),
        )?;
    }
    let scheduler_heap_scratch_bytes = scheduler_proof.decision_heap_scratch_bytes();
    if scheduler_heap_scratch_bytes != 0 {
        return Err(BondSelfTestError::Invariant(
            "scheduler decisions use heap-backed scratch",
        ));
    }

    let realtime_lane = LaneId::new(1)?;
    let failed_bulk_lane = LaneId::new(2)?;
    let surviving_bulk_lane = LaneId::new(3)?;
    let mut scheduler = BondScheduler::new(SchedulerConfig::default())?;
    for (id, rtt_ms, rate_mbps) in [(1, 5, 10), (2, 40, 8), (3, 60, 3)] {
        scheduler.add_lane(LaneConfig::new(
            LaneId::new(id)?,
            FailureDomain::new(id as u64)?,
            Duration::from_millis(rtt_ms),
            rate_mbps * 1_000_000,
        )?)?;
    }

    let realtime = scheduler.schedule(TrafficClass::Realtime, 128, Timestamp::ZERO)?;
    if realtime.lane_id != realtime_lane || !realtime.uses_low_latency_pool {
        return Err(BondSelfTestError::Invariant(
            "real-time data escaped the protected low-latency pool",
        ));
    }
    let mut interactive_scheduler = BondScheduler::new(SchedulerConfig::default())?;
    for (id, rtt_ms, rate_mbps) in [(1, 5, 10), (2, 40, 8), (3, 60, 3)] {
        interactive_scheduler.add_lane(LaneConfig::new(
            LaneId::new(id)?,
            FailureDomain::new(id as u64)?,
            Duration::from_millis(rtt_ms),
            rate_mbps * 1_000_000,
        )?)?;
    }
    let interactive_typing =
        interactive_scheduler.schedule(TrafficClass::Interactive, 256, Timestamp::ZERO)?;
    if interactive_typing.lane_id != realtime_lane || !interactive_typing.uses_low_latency_pool {
        return Err(BondSelfTestError::Invariant(
            "typing-sized interactive data escaped the protected low-latency pool",
        ));
    }
    let mut interactive_bulk_lanes = BTreeSet::new();
    for _ in 0..32 {
        let decision =
            interactive_scheduler.schedule(TrafficClass::Interactive, 4 * 1024, Timestamp::ZERO)?;
        if decision.uses_low_latency_pool {
            return Err(BondSelfTestError::Invariant(
                "sustained interactive data entered the protected low-latency pool",
            ));
        }
        interactive_bulk_lanes.insert(decision.lane_id);
    }
    if interactive_bulk_lanes != [failed_bulk_lane, surviving_bulk_lane].into() {
        return Err(BondSelfTestError::Invariant(
            "sustained interactive data did not stripe over the bulk lane pool",
        ));
    }

    let mut sender = BondSender::new(
        1,
        SenderConfig {
            max_chunk_payload: 4 * 1024,
            bulk_chunk: crate::BulkChunkConfig::fixed(4 * 1024),
            max_unacknowledged_bytes: 128 * 1024,
            ..SenderConfig::default()
        },
        scheduler,
    )?;
    let stream = StreamId::new(1)?;
    let payload: Vec<_> = (0..96 * 1024).map(|index| (index % 251) as u8).collect();
    let initial = sender.enqueue(stream, TrafficClass::Bulk, &payload, Timestamp::ZERO)?;
    let bulk_lanes: BTreeSet<_> = initial.iter().map(|frame| frame.lane_id).collect();
    if bulk_lanes != [failed_bulk_lane, surviving_bulk_lane].into() {
        return Err(BondSelfTestError::Invariant(
            "bulk data did not stripe over both non-reserved lanes",
        ));
    }

    let retransmitted = sender.fail_lane(failed_bulk_lane, Timestamp::from_micros(1_000_000))?;
    if retransmitted.is_empty()
        || retransmitted
            .iter()
            .any(|frame| frame.lane_id != surviving_bulk_lane)
    {
        return Err(BondSelfTestError::Invariant(
            "failed-lane data did not move to the surviving bulk lane",
        ));
    }

    let replacements: BTreeMap<_, _> = retransmitted
        .iter()
        .map(|frame| (frame.frame.header.offset, &frame.frame))
        .collect();
    let mut received: Vec<_> = initial
        .iter()
        .filter_map(|scheduled| {
            if scheduled.lane_id == failed_bulk_lane {
                replacements.get(&scheduled.frame.header.offset).copied()
            } else {
                Some(&scheduled.frame)
            }
        })
        .collect();
    received.reverse();

    let mut reassembler = Reassembler::new(0, payload.len())?;
    let mut delivered = Vec::with_capacity(payload.len());
    for frame in received {
        delivered.extend_from_slice(
            &reassembler
                .insert(frame.header.offset, &frame.payload)?
                .bytes,
        );
    }
    if delivered != payload {
        return Err(BondSelfTestError::Invariant(
            "striped payload did not reassemble exactly",
        ));
    }
    if sender
        .acknowledge(stream, payload.len() as u64)?
        .released_bytes
        != payload.len()
        || sender.unacknowledged_bytes() != 0
    {
        return Err(BondSelfTestError::Invariant(
            "bond acknowledgement did not release the send window",
        ));
    }

    Ok(BondSelfTestReport {
        payload_bytes: payload.len(),
        initial_frames: initial.len(),
        retransmitted_frames: retransmitted.len(),
        bulk_lanes: bulk_lanes.len(),
        realtime_lane,
        interactive_typing_lane: interactive_typing.lane_id,
        interactive_bulk_lanes: interactive_bulk_lanes.len(),
        reorder_high_water: reassembler.reorder_high_water(),
        scheduler_lanes,
        scheduler_decisions,
        scheduler_heap_scratch_bytes,
    })
}

#[derive(Debug)]
pub enum BondSelfTestError {
    Scheduler(SchedulerError),
    Sender(SenderError),
    Reassembly(ReassemblyError),
    Invariant(&'static str),
}

impl From<SchedulerError> for BondSelfTestError {
    fn from(value: SchedulerError) -> Self {
        Self::Scheduler(value)
    }
}

impl From<SenderError> for BondSelfTestError {
    fn from(value: SenderError) -> Self {
        Self::Sender(value)
    }
}

impl From<ReassemblyError> for BondSelfTestError {
    fn from(value: ReassemblyError) -> Self {
        Self::Reassembly(value)
    }
}

impl fmt::Display for BondSelfTestError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Scheduler(error) => error.fmt(formatter),
            Self::Sender(error) => error.fmt(formatter),
            Self::Reassembly(error) => error.fmt(formatter),
            Self::Invariant(message) => write!(formatter, "bond self-test failed: {message}"),
        }
    }
}

impl Error for BondSelfTestError {}

#[cfg(test)]
mod tests {
    use super::embedded_self_test;

    #[test]
    fn shipped_self_test_exercises_striping_and_recovery() {
        let report = embedded_self_test().unwrap();
        assert_eq!(report.bulk_lanes, 2);
        assert_eq!(report.interactive_typing_lane, report.realtime_lane);
        assert_eq!(report.interactive_bulk_lanes, 2);
        assert!(report.retransmitted_frames > 0);
        assert_eq!(report.payload_bytes, 96 * 1024);
        assert!(report.reorder_high_water > 0);
        assert_eq!(report.scheduler_lanes, 8);
        assert_eq!(report.scheduler_decisions, 8_192);
        assert_eq!(report.scheduler_heap_scratch_bytes, 0);
    }
}
