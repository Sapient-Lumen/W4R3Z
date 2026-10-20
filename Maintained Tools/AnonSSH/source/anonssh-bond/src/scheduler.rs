use std::collections::{BTreeMap, BTreeSet};
use std::error::Error;
use std::fmt;
use std::time::Duration;

use crate::scaling::ProviderId;

#[derive(Clone, Copy, Debug, Default, Eq, Ord, PartialEq, PartialOrd)]
pub struct Timestamp(u64);

impl Timestamp {
    pub const ZERO: Self = Self(0);

    pub const fn from_micros(micros: u64) -> Self {
        Self(micros)
    }

    pub const fn as_micros(self) -> u64 {
        self.0
    }

    pub fn duration_since(self, earlier: Self) -> Option<Duration> {
        self.0.checked_sub(earlier.0).map(Duration::from_micros)
    }

    fn checked_add_micros(self, micros: u64) -> Result<Self, SchedulerError> {
        self.0
            .checked_add(micros)
            .map(Self)
            .ok_or(SchedulerError::TimeOverflow)
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub struct LaneId(u32);

impl LaneId {
    pub fn new(value: u32) -> Result<Self, SchedulerError> {
        if value == 0 {
            Err(SchedulerError::ZeroLaneId)
        } else {
            Ok(Self(value))
        }
    }

    pub const fn get(self) -> u32 {
        self.0
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub struct FailureDomain(u64);

impl FailureDomain {
    pub fn new(value: u64) -> Result<Self, SchedulerError> {
        if value == 0 {
            Err(SchedulerError::ZeroFailureDomain)
        } else {
            Ok(Self(value))
        }
    }

    pub const fn get(self) -> u64 {
        self.0
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum TrafficClass {
    Control,
    Realtime,
    Interactive,
    Bulk,
}

pub const INTERACTIVE_REALTIME_MAX_BYTES: usize = 2 * 1024;

impl TrafficClass {
    const fn scheduling_class(self, bytes: usize) -> Self {
        match self {
            Self::Interactive if bytes <= INTERACTIVE_REALTIME_MAX_BYTES => Self::Realtime,
            Self::Interactive => Self::Bulk,
            class => class,
        }
    }

    pub const fn is_latency_sensitive(self, bytes: usize) -> bool {
        matches!(self.scheduling_class(bytes), Self::Control | Self::Realtime)
    }

    pub const fn is_redundant_realtime_candidate(self, bytes: usize) -> bool {
        bytes <= INTERACTIVE_REALTIME_MAX_BYTES
            && matches!(self, Self::Realtime | Self::Interactive)
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct SchedulerConfig {
    pub low_latency_lane_count: usize,
    pub low_latency_switch_hysteresis_percent: u8,
    pub minimum_rate_bps: u64,
    pub maximum_rate_bps: u64,
    pub bulk_probe_bytes_per_lane: u64,
    pub bulk_reprobe_interval: Duration,
}

impl Default for SchedulerConfig {
    fn default() -> Self {
        Self {
            low_latency_lane_count: 1,
            low_latency_switch_hysteresis_percent: 10,
            minimum_rate_bps: 8_000,
            maximum_rate_bps: 100_000_000_000,
            bulk_probe_bytes_per_lane: 16 * 1024,
            bulk_reprobe_interval: Duration::from_secs(15),
        }
    }
}

impl SchedulerConfig {
    fn validate(self) -> Result<Self, SchedulerError> {
        if self.low_latency_lane_count == 0 {
            return Err(SchedulerError::EmptyLowLatencyPool);
        }
        if self.low_latency_switch_hysteresis_percent >= 100 {
            return Err(SchedulerError::InvalidLowLatencySwitchHysteresis(
                self.low_latency_switch_hysteresis_percent,
            ));
        }
        if self.minimum_rate_bps == 0 || self.minimum_rate_bps > self.maximum_rate_bps {
            return Err(SchedulerError::InvalidRateBounds);
        }
        if self.bulk_probe_bytes_per_lane > 0 && self.bulk_reprobe_interval.is_zero() {
            return Err(SchedulerError::ZeroBulkReprobeInterval);
        }
        Ok(self)
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct LaneConfig {
    pub id: LaneId,
    pub failure_domain: FailureDomain,
    pub provider_group: Option<ProviderId>,
    pub initial_round_trip_time: Duration,
    pub initial_rate_bps: u64,
}

impl LaneConfig {
    pub fn new(
        id: LaneId,
        failure_domain: FailureDomain,
        initial_round_trip_time: Duration,
        initial_rate_bps: u64,
    ) -> Result<Self, SchedulerError> {
        if initial_round_trip_time.is_zero() {
            return Err(SchedulerError::ZeroRoundTripTime);
        }
        if initial_rate_bps == 0 {
            return Err(SchedulerError::ZeroDeliveryRate);
        }
        Ok(Self {
            id,
            failure_domain,
            provider_group: None,
            initial_round_trip_time,
            initial_rate_bps,
        })
    }

    pub const fn with_provider_group(mut self, provider_group: ProviderId) -> Self {
        self.provider_group = Some(provider_group);
        self
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct DeliverySample {
    pub bytes: usize,
    pub elapsed: Duration,
    pub round_trip_time: Duration,
}

impl DeliverySample {
    pub fn new(
        bytes: usize,
        elapsed: Duration,
        round_trip_time: Duration,
    ) -> Result<Self, SchedulerError> {
        if bytes == 0 {
            return Err(SchedulerError::EmptyDeliverySample);
        }
        if elapsed.is_zero() {
            return Err(SchedulerError::ZeroSampleDuration);
        }
        if round_trip_time.is_zero() {
            return Err(SchedulerError::ZeroRoundTripTime);
        }
        Ok(Self {
            bytes,
            elapsed,
            round_trip_time,
        })
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct ScheduleDecision {
    pub lane_id: LaneId,
    pub predicted_delivery_at: Timestamp,
    pub uses_low_latency_pool: bool,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct SizedScheduleDecision {
    pub decision: ScheduleDecision,
    pub payload_bytes: usize,
}

#[derive(Clone, Copy)]
enum PayloadSizing {
    Fixed(usize),
    AdaptiveBulk {
        minimum: usize,
        maximum: usize,
        remaining: usize,
    },
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct LaneSnapshot {
    pub id: LaneId,
    pub failure_domain: FailureDomain,
    pub provider_group: Option<ProviderId>,
    pub active: bool,
    pub delivery_measured: bool,
    pub reserved_for_low_latency: bool,
    pub smoothed_round_trip_time: Duration,
    pub delivery_rate_bps: u64,
    pub queued_through: Timestamp,
    pub bytes_scheduled: u64,
    pub bytes_acknowledged: u64,
}

#[derive(Clone, Debug)]
struct LaneState {
    failure_domain: FailureDomain,
    provider_group: Option<ProviderId>,
    active: bool,
    delivery_measured: bool,
    srtt_micros: u64,
    rate_bps: u64,
    queued_through: Timestamp,
    bytes_scheduled: u64,
    bytes_acknowledged: u64,
    probe_bytes_scheduled: u64,
    probe_window_started_at: Timestamp,
}

#[derive(Debug)]
pub struct BondScheduler {
    config: SchedulerConfig,
    lanes: BTreeMap<LaneId, LaneState>,
    bootstrap_low_latency: BTreeSet<LaneId>,
    reserved_low_latency: BTreeSet<LaneId>,
    reservation_seeded: bool,
    #[cfg(test)]
    reservation_refreshes: usize,
}

impl BondScheduler {
    pub fn new(config: SchedulerConfig) -> Result<Self, SchedulerError> {
        Ok(Self {
            config: config.validate()?,
            lanes: BTreeMap::new(),
            bootstrap_low_latency: BTreeSet::new(),
            reserved_low_latency: BTreeSet::new(),
            reservation_seeded: false,
            #[cfg(test)]
            reservation_refreshes: 0,
        })
    }

    pub fn add_lane(&mut self, lane: LaneConfig) -> Result<(), SchedulerError> {
        if self.lanes.contains_key(&lane.id) {
            return Err(SchedulerError::DuplicateLane(lane.id));
        }
        let srtt_micros = duration_micros(lane.initial_round_trip_time)?;
        let rate_bps = lane
            .initial_rate_bps
            .clamp(self.config.minimum_rate_bps, self.config.maximum_rate_bps);
        self.lanes.insert(
            lane.id,
            LaneState {
                failure_domain: lane.failure_domain,
                provider_group: lane.provider_group,
                active: true,
                delivery_measured: false,
                srtt_micros,
                rate_bps,
                queued_through: Timestamp::ZERO,
                bytes_scheduled: 0,
                bytes_acknowledged: 0,
                probe_bytes_scheduled: 0,
                probe_window_started_at: Timestamp::ZERO,
            },
        );
        self.refresh_low_latency_pool();
        Ok(())
    }

    pub fn restore_lane(&mut self, lane: LaneConfig, now: Timestamp) -> Result<(), SchedulerError> {
        let state = self
            .lanes
            .get_mut(&lane.id)
            .ok_or(SchedulerError::UnknownLane(lane.id))?;
        if state.active {
            return Err(SchedulerError::DuplicateLane(lane.id));
        }
        if state.failure_domain != lane.failure_domain {
            return Err(SchedulerError::LaneFailureDomainChanged(lane.id));
        }
        if state.provider_group != lane.provider_group {
            return Err(SchedulerError::LaneProviderGroupChanged(lane.id));
        }
        state.active = true;
        state.probe_bytes_scheduled = 0;
        state.probe_window_started_at = now;
        if state.queued_through < now {
            state.queued_through = now;
        }
        self.refresh_low_latency_pool();
        Ok(())
    }

    pub fn set_lane_active(
        &mut self,
        lane_id: LaneId,
        active: bool,
        now: Timestamp,
    ) -> Result<(), SchedulerError> {
        let lane = self
            .lanes
            .get_mut(&lane_id)
            .ok_or(SchedulerError::UnknownLane(lane_id))?;
        lane.active = active;
        if active && lane.queued_through < now {
            lane.queued_through = now;
        }
        self.refresh_low_latency_pool();
        Ok(())
    }

    pub fn record_delivery(
        &mut self,
        lane_id: LaneId,
        sample: DeliverySample,
    ) -> Result<(), SchedulerError> {
        self.record_deliveries([(lane_id, sample)])
    }

    pub fn record_deliveries(
        &mut self,
        samples: impl IntoIterator<Item = (LaneId, DeliverySample)>,
    ) -> Result<(), SchedulerError> {
        self.seed_low_latency_pool();
        let mut recorded = false;
        for (lane_id, sample) in samples {
            self.record_delivery_sample(lane_id, sample)?;
            recorded = true;
        }
        if recorded {
            self.refresh_low_latency_pool();
        }
        Ok(())
    }

    fn record_delivery_sample(
        &mut self,
        lane_id: LaneId,
        sample: DeliverySample,
    ) -> Result<(), SchedulerError> {
        let lane = self
            .lanes
            .get_mut(&lane_id)
            .ok_or(SchedulerError::UnknownLane(lane_id))?;
        lane.delivery_measured = true;
        let sample_rtt = duration_micros(sample.round_trip_time)?;
        lane.srtt_micros = weighted_average(lane.srtt_micros, sample_rtt, 7, 1)?;

        let elapsed_micros = duration_micros(sample.elapsed)?;
        let sample_rate = ((sample.bytes as u128) * 8 * 1_000_000 / elapsed_micros as u128)
            .min(u64::MAX as u128) as u64;
        let sample_rate =
            sample_rate.clamp(self.config.minimum_rate_bps, self.config.maximum_rate_bps);
        lane.rate_bps = weighted_average(lane.rate_bps, sample_rate, 3, 1)?;
        lane.bytes_acknowledged = lane
            .bytes_acknowledged
            .checked_add(sample.bytes as u64)
            .ok_or(SchedulerError::CounterOverflow)?;
        Ok(())
    }

    pub fn record_round_trip_time(
        &mut self,
        lane_id: LaneId,
        round_trip_time: Duration,
    ) -> Result<(), SchedulerError> {
        self.seed_low_latency_pool();
        let sample_rtt = duration_micros(round_trip_time)?;
        let lane = self
            .lanes
            .get_mut(&lane_id)
            .ok_or(SchedulerError::UnknownLane(lane_id))?;
        lane.delivery_measured = true;
        lane.srtt_micros = weighted_average(lane.srtt_micros, sample_rtt, 7, 1)?;
        self.refresh_low_latency_pool();
        Ok(())
    }

    pub fn retransmission_timeout(
        &self,
        lane_id: LaneId,
        minimum: Duration,
        maximum: Duration,
    ) -> Result<Duration, SchedulerError> {
        let lane = self
            .lanes
            .get(&lane_id)
            .ok_or(SchedulerError::UnknownLane(lane_id))?;
        Ok(Duration::from_micros(lane.srtt_micros)
            .saturating_mul(4)
            .clamp(minimum, maximum))
    }

    pub fn schedule(
        &mut self,
        class: TrafficClass,
        bytes: usize,
        now: Timestamp,
    ) -> Result<ScheduleDecision, SchedulerError> {
        self.schedule_excluding(class, bytes, now, None)
    }

    pub fn schedule_excluding(
        &mut self,
        class: TrafficClass,
        bytes: usize,
        now: Timestamp,
        excluded: Option<LaneId>,
    ) -> Result<ScheduleDecision, SchedulerError> {
        Ok(self
            .schedule_sized(class, PayloadSizing::Fixed(bytes), now, excluded)?
            .decision)
    }

    pub fn schedule_redundant_realtime(
        &mut self,
        class: TrafficClass,
        bytes: usize,
        now: Timestamp,
    ) -> Result<(ScheduleDecision, Option<ScheduleDecision>), SchedulerError> {
        let primary = self.schedule(class, bytes, now)?;
        if !class.is_redundant_realtime_candidate(bytes) {
            return Ok((primary, None));
        }
        let has_protected_standby = self.lanes.iter().any(|(lane_id, lane)| {
            lane.active && *lane_id != primary.lane_id && self.is_lane_reserved(*lane_id, lane)
        });
        if !has_protected_standby {
            return Ok((primary, None));
        }
        let redundant = self.schedule_excluding(class, bytes, now, Some(primary.lane_id))?;
        debug_assert!(redundant.uses_low_latency_pool);
        Ok((primary, Some(redundant)))
    }

    pub(crate) fn schedule_adaptive_bulk(
        &mut self,
        minimum: usize,
        maximum: usize,
        remaining: usize,
        now: Timestamp,
    ) -> Result<SizedScheduleDecision, SchedulerError> {
        self.schedule_sized(
            TrafficClass::Bulk,
            PayloadSizing::AdaptiveBulk {
                minimum,
                maximum,
                remaining,
            },
            now,
            None,
        )
    }

    fn schedule_sized(
        &mut self,
        class: TrafficClass,
        sizing: PayloadSizing,
        now: Timestamp,
        excluded: Option<LaneId>,
    ) -> Result<SizedScheduleDecision, SchedulerError> {
        let class = match sizing {
            PayloadSizing::Fixed(0) | PayloadSizing::AdaptiveBulk { remaining: 0, .. } => {
                return Err(SchedulerError::EmptyChunk);
            }
            PayloadSizing::Fixed(bytes) => class.scheduling_class(bytes),
            PayloadSizing::AdaptiveBulk {
                minimum, maximum, ..
            } => {
                if minimum == 0 || minimum > maximum {
                    return Err(SchedulerError::InvalidChunkBounds { minimum, maximum });
                }
                TrafficClass::Bulk
            }
        };
        self.seed_low_latency_pool();
        let has_preferred = self.lanes.iter().any(|(id, lane)| {
            lane.active
                && Some(*id) != excluded
                && preferred_for_class(class, self.is_lane_reserved(*id, lane))
        });
        let eligible = |lane_id: LaneId, lane: &LaneState| {
            lane.active
                && Some(lane_id) != excluded
                && (!has_preferred
                    || preferred_for_class(class, self.is_lane_reserved(lane_id, lane)))
        };

        let mut selected_probe: Option<(u64, LaneId, Timestamp, usize)> = None;
        let mut best: Option<(Timestamp, LaneId, usize)> = None;
        for (lane_id, lane) in &self.lanes {
            if !eligible(*lane_id, lane) {
                continue;
            }
            let bytes = match sizing {
                PayloadSizing::Fixed(bytes) => bytes,
                PayloadSizing::AdaptiveBulk {
                    minimum,
                    maximum,
                    remaining,
                } => adaptive_bulk_payload(lane, minimum, maximum, remaining, now),
            };
            let delivery = predicted_delivery(lane, bytes, now)?;
            if class == TrafficClass::Bulk && self.config.bulk_probe_bytes_per_lane > 0 {
                if let Some(progress) = bulk_probe_progress(lane, self.config, now) {
                    let candidate = (progress, *lane_id);
                    if selected_probe
                        .as_ref()
                        .is_none_or(|current| candidate < (current.0, current.1))
                    {
                        selected_probe = Some((progress, *lane_id, delivery, bytes));
                    }
                }
            }
            let candidate = (delivery, *lane_id);
            if best.is_none_or(|current| candidate < (current.0, current.1)) {
                best = Some((delivery, *lane_id, bytes));
            }
        }
        let (predicted_delivery_at, lane_id, payload_bytes) = selected_probe
            .map(|(_, lane_id, delivery, bytes)| (delivery, lane_id, bytes))
            .or(best)
            .ok_or(SchedulerError::NoHealthyLane)?;
        let uses_low_latency_pool = self.reserved_low_latency.contains(&lane_id);
        let lane = self.lanes.get_mut(&lane_id).expect("selected lane exists");
        let serialization = serialization_micros(payload_bytes, lane.rate_bps)?;
        lane.queued_through =
            Timestamp(lane.queued_through.0.max(now.0)).checked_add_micros(serialization)?;
        lane.bytes_scheduled = lane
            .bytes_scheduled
            .checked_add(payload_bytes as u64)
            .ok_or(SchedulerError::CounterOverflow)?;
        if class == TrafficClass::Bulk {
            if probe_window_expired(lane, self.config, now) {
                lane.probe_bytes_scheduled = 0;
                lane.probe_window_started_at = now;
            }
            lane.probe_bytes_scheduled = lane
                .probe_bytes_scheduled
                .checked_add(payload_bytes as u64)
                .ok_or(SchedulerError::CounterOverflow)?;
        }

        Ok(SizedScheduleDecision {
            decision: ScheduleDecision {
                lane_id,
                predicted_delivery_at,
                uses_low_latency_pool,
            },
            payload_bytes,
        })
    }

    pub const fn decision_heap_scratch_bytes(&self) -> usize {
        0
    }

    pub const fn decision_lane_pass_limit(&self) -> usize {
        2
    }

    pub fn low_latency_pool(&self) -> Vec<LaneId> {
        if self.reservation_seeded {
            self.reserved_low_latency
                .iter()
                .filter(|id| self.lanes.get(id).is_some_and(|lane| lane.active))
                .copied()
                .collect()
        } else {
            self.initial_low_latency_pool().into_iter().collect()
        }
    }

    fn initial_low_latency_pool(&self) -> BTreeSet<LaneId> {
        let target = self
            .config
            .low_latency_lane_count
            .min(self.lanes.values().filter(|lane| lane.active).count());
        let diversity_target = target.min(self.active_protection_group_count());
        let mut selected = BTreeSet::new();
        while selected.len() < target {
            let needs_new_group = selected_group_count(&self.lanes, &selected) < diversity_target;
            let candidate = self
                .lanes
                .iter()
                .filter(|(id, lane)| {
                    lane.active
                        && !selected.contains(id)
                        && (!needs_new_group
                            || !group_is_selected(&self.lanes, &selected, **id, lane))
                })
                .map(|(id, lane)| (lane.srtt_micros, *id))
                .min();
            let Some((_, lane_id)) = candidate else {
                break;
            };
            selected.insert(lane_id);
        }
        selected
    }

    fn seed_low_latency_pool(&mut self) {
        if self.reservation_seeded {
            return;
        }
        self.bootstrap_low_latency = self.initial_low_latency_pool();
        self.reserved_low_latency = self.bootstrap_low_latency.clone();
        self.reservation_seeded = true;
    }

    fn active_protection_group_count(&self) -> usize {
        self.lanes
            .iter()
            .filter(|(id, lane)| {
                lane.active
                    && !self.lanes.range(..**id).any(|(prior_id, prior)| {
                        prior.active
                            && protection_group(*prior_id, prior) == protection_group(**id, lane)
                    })
            })
            .count()
    }

    fn reserved_protection_group_count(&self) -> usize {
        self.reserved_low_latency
            .iter()
            .filter(|id| {
                let lane = self.lanes.get(id).expect("reserved lane exists");
                !self.reserved_low_latency.range(..**id).any(|prior_id| {
                    self.lanes.get(prior_id).is_some_and(|prior| {
                        protection_group(*prior_id, prior) == protection_group(**id, lane)
                    })
                })
            })
            .count()
    }

    fn group_is_reserved(&self, lane_id: LaneId, lane: &LaneState) -> bool {
        let group = protection_group(lane_id, lane);
        self.reserved_low_latency.iter().any(|reserved_id| {
            self.lanes
                .get(reserved_id)
                .is_some_and(|reserved| protection_group(*reserved_id, reserved) == group)
        })
    }

    fn replacement_preserves_diversity(&self, incumbent_id: LaneId, challenger_id: LaneId) -> bool {
        let incumbent = self.lanes.get(&incumbent_id).expect("incumbent exists");
        let challenger = self.lanes.get(&challenger_id).expect("challenger exists");
        let incumbent_group = protection_group(incumbent_id, incumbent);
        let challenger_group = protection_group(challenger_id, challenger);
        incumbent_group == challenger_group
            || self.reserved_low_latency.iter().any(|reserved_id| {
                *reserved_id != incumbent_id
                    && self.lanes.get(reserved_id).is_some_and(|reserved| {
                        protection_group(*reserved_id, reserved) == incumbent_group
                    })
            })
            || !self.group_is_reserved(challenger_id, challenger)
    }

    fn refresh_low_latency_pool(&mut self) {
        #[cfg(test)]
        {
            self.reservation_refreshes += 1;
        }
        if !self.reservation_seeded {
            return;
        }
        self.reserved_low_latency
            .retain(|id| self.lanes.get(id).is_some_and(|lane| lane.active));
        let target = self
            .config
            .low_latency_lane_count
            .min(self.lanes.values().filter(|lane| lane.active).count());
        let diversity_target = target.min(self.active_protection_group_count());

        while self.reserved_protection_group_count() < diversity_target {
            let candidate = self
                .lanes
                .iter()
                .filter(|(id, lane)| {
                    lane.active
                        && !self.reserved_low_latency.contains(id)
                        && !self.group_is_reserved(**id, lane)
                })
                .map(|(id, lane)| (lane.srtt_micros, *id))
                .min();
            let incumbent = self
                .reserved_low_latency
                .iter()
                .filter_map(|id| {
                    let lane = self.lanes.get(id)?;
                    self.reserved_low_latency
                        .iter()
                        .any(|other_id| {
                            other_id != id
                                && self.lanes.get(other_id).is_some_and(|other| {
                                    protection_group(*other_id, other)
                                        == protection_group(*id, lane)
                                })
                        })
                        .then_some((lane.srtt_micros, *id))
                })
                .max();
            let (Some((_, candidate_id)), Some((_, incumbent_id))) = (candidate, incumbent) else {
                break;
            };
            self.reserved_low_latency.remove(&incumbent_id);
            self.reserved_low_latency.insert(candidate_id);
        }

        while self.reserved_low_latency.len() < target {
            let needs_new_group = self.reserved_protection_group_count() < diversity_target;
            let evidence_available = self.lanes.iter().any(|(id, lane)| {
                lane.active
                    && !self.reserved_low_latency.contains(id)
                    && (!needs_new_group || !self.group_is_reserved(*id, lane))
                    && (lane.delivery_measured || self.bootstrap_low_latency.contains(id))
            });
            let candidate = self
                .lanes
                .iter()
                .filter(|(id, lane)| {
                    lane.active
                        && !self.reserved_low_latency.contains(id)
                        && (!needs_new_group || !self.group_is_reserved(**id, lane))
                        && (!evidence_available
                            || lane.delivery_measured
                            || self.bootstrap_low_latency.contains(id))
                })
                .map(|(id, lane)| (lane.srtt_micros, *id))
                .min();
            let Some((_, lane_id)) = candidate else {
                break;
            };
            self.reserved_low_latency.insert(lane_id);
        }

        loop {
            let mut replacement: Option<(u64, u64, LaneId, LaneId)> = None;
            for (challenger_id, challenger) in &self.lanes {
                if !challenger.active
                    || self.reserved_low_latency.contains(challenger_id)
                    || (!challenger.delivery_measured
                        && !self.bootstrap_low_latency.contains(challenger_id))
                {
                    continue;
                }
                for incumbent_id in &self.reserved_low_latency {
                    let incumbent = self.lanes.get(incumbent_id).expect("incumbent exists");
                    if !self.replacement_preserves_diversity(*incumbent_id, *challenger_id)
                        || !clears_hysteresis(
                            challenger.srtt_micros,
                            incumbent.srtt_micros,
                            self.config.low_latency_switch_hysteresis_percent,
                        )
                    {
                        continue;
                    }
                    let gain = incumbent.srtt_micros - challenger.srtt_micros;
                    let candidate = (gain, challenger.srtt_micros, *challenger_id, *incumbent_id);
                    if replacement.is_none_or(|current| {
                        gain > current.0
                            || (gain == current.0
                                && (challenger.srtt_micros, *challenger_id, *incumbent_id)
                                    < (current.1, current.2, current.3))
                    }) {
                        replacement = Some(candidate);
                    }
                }
            }
            let Some((_, _, challenger_id, incumbent_id)) = replacement else {
                break;
            };
            self.reserved_low_latency.remove(&incumbent_id);
            self.reserved_low_latency.insert(challenger_id);
        }
    }

    fn is_lane_reserved(&self, lane_id: LaneId, lane: &LaneState) -> bool {
        lane.active && self.reserved_low_latency.contains(&lane_id)
    }

    pub fn snapshot(&self, lane_id: LaneId) -> Result<LaneSnapshot, SchedulerError> {
        let lane = self
            .lanes
            .get(&lane_id)
            .ok_or(SchedulerError::UnknownLane(lane_id))?;
        Ok(LaneSnapshot {
            id: lane_id,
            failure_domain: lane.failure_domain,
            provider_group: lane.provider_group,
            active: lane.active,
            delivery_measured: lane.delivery_measured,
            reserved_for_low_latency: if self.reservation_seeded {
                self.is_lane_reserved(lane_id, lane)
            } else {
                self.initial_low_latency_pool().contains(&lane_id)
            },
            smoothed_round_trip_time: Duration::from_micros(lane.srtt_micros),
            delivery_rate_bps: lane.rate_bps,
            queued_through: lane.queued_through,
            bytes_scheduled: lane.bytes_scheduled,
            bytes_acknowledged: lane.bytes_acknowledged,
        })
    }

    pub fn active_lane_count(&self) -> usize {
        self.lanes.values().filter(|lane| lane.active).count()
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct ProtectionGroup(u8, u64);

fn protection_group(lane_id: LaneId, lane: &LaneState) -> ProtectionGroup {
    match lane.provider_group {
        Some(provider) => ProtectionGroup(0, u64::from(provider.get())),
        None => ProtectionGroup(1, u64::from(lane_id.get())),
    }
}

fn group_is_selected(
    lanes: &BTreeMap<LaneId, LaneState>,
    selected: &BTreeSet<LaneId>,
    lane_id: LaneId,
    lane: &LaneState,
) -> bool {
    let group = protection_group(lane_id, lane);
    selected.iter().any(|selected_id| {
        lanes
            .get(selected_id)
            .is_some_and(|selected_lane| protection_group(*selected_id, selected_lane) == group)
    })
}

fn selected_group_count(lanes: &BTreeMap<LaneId, LaneState>, selected: &BTreeSet<LaneId>) -> usize {
    selected
        .iter()
        .filter(|id| {
            let lane = lanes.get(id).expect("selected lane exists");
            !selected.range(..**id).any(|prior_id| {
                lanes.get(prior_id).is_some_and(|prior| {
                    protection_group(*prior_id, prior) == protection_group(**id, lane)
                })
            })
        })
        .count()
}

fn clears_hysteresis(challenger_rtt: u64, incumbent_rtt: u64, hysteresis_percent: u8) -> bool {
    u128::from(challenger_rtt) * 100
        <= u128::from(incumbent_rtt) * u128::from(100 - hysteresis_percent)
}

fn preferred_for_class(class: TrafficClass, reserved: bool) -> bool {
    match class {
        TrafficClass::Control | TrafficClass::Realtime => reserved,
        TrafficClass::Interactive => reserved,
        TrafficClass::Bulk => !reserved,
    }
}

fn bulk_probe_progress(lane: &LaneState, config: SchedulerConfig, now: Timestamp) -> Option<u64> {
    if probe_window_expired(lane, config, now) {
        Some(0)
    } else if lane.probe_bytes_scheduled < config.bulk_probe_bytes_per_lane {
        Some(lane.probe_bytes_scheduled)
    } else {
        None
    }
}

fn probe_window_expired(lane: &LaneState, config: SchedulerConfig, now: Timestamp) -> bool {
    now.duration_since(lane.probe_window_started_at)
        .is_some_and(|elapsed| elapsed >= config.bulk_reprobe_interval)
}

fn predicted_delivery(
    lane: &LaneState,
    bytes: usize,
    now: Timestamp,
) -> Result<Timestamp, SchedulerError> {
    let serialization = serialization_micros(bytes, lane.rate_bps)?;
    Timestamp(lane.queued_through.0.max(now.0))
        .checked_add_micros(serialization)?
        .checked_add_micros(lane.srtt_micros / 2)
}

fn adaptive_bulk_payload(
    lane: &LaneState,
    minimum: usize,
    maximum: usize,
    remaining: usize,
    now: Timestamp,
) -> usize {
    let bandwidth_delay_product =
        (lane.rate_bps as u128).saturating_mul(lane.srtt_micros as u128) / 8_000_000;
    let mut target = bandwidth_delay_product.clamp(minimum as u128, maximum as u128) as usize;

    let queue_delay = lane
        .queued_through
        .as_micros()
        .saturating_sub(now.as_micros());
    if queue_delay >= lane.srtt_micros.saturating_mul(2) {
        target = minimum;
    } else if queue_delay >= lane.srtt_micros {
        target = (target / 2).max(minimum);
    }
    target.min(remaining)
}

fn serialization_micros(bytes: usize, rate_bps: u64) -> Result<u64, SchedulerError> {
    if rate_bps == 0 {
        return Err(SchedulerError::ZeroDeliveryRate);
    }
    let bits_micros = (bytes as u128)
        .checked_mul(8)
        .and_then(|value| value.checked_mul(1_000_000))
        .ok_or(SchedulerError::TimeOverflow)?;
    let micros = bits_micros.div_ceil(rate_bps as u128).max(1);
    u64::try_from(micros).map_err(|_| SchedulerError::TimeOverflow)
}

fn duration_micros(duration: Duration) -> Result<u64, SchedulerError> {
    u64::try_from(duration.as_micros()).map_err(|_| SchedulerError::TimeOverflow)
}

fn weighted_average(
    current: u64,
    sample: u64,
    current_weight: u64,
    sample_weight: u64,
) -> Result<u64, SchedulerError> {
    let numerator =
        (current as u128) * (current_weight as u128) + (sample as u128) * (sample_weight as u128);
    let denominator = (current_weight + sample_weight) as u128;
    u64::try_from(numerator / denominator).map_err(|_| SchedulerError::CounterOverflow)
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum SchedulerError {
    ZeroLaneId,
    ZeroFailureDomain,
    EmptyLowLatencyPool,
    InvalidLowLatencySwitchHysteresis(u8),
    InvalidRateBounds,
    ZeroBulkReprobeInterval,
    ZeroRoundTripTime,
    ZeroDeliveryRate,
    EmptyDeliverySample,
    ZeroSampleDuration,
    EmptyChunk,
    InvalidChunkBounds { minimum: usize, maximum: usize },
    DuplicateLane(LaneId),
    LaneFailureDomainChanged(LaneId),
    LaneProviderGroupChanged(LaneId),
    UnknownLane(LaneId),
    NoHealthyLane,
    TimeOverflow,
    CounterOverflow,
}

impl fmt::Display for SchedulerError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::ZeroLaneId => write!(formatter, "lane ID must be non-zero"),
            Self::ZeroFailureDomain => write!(formatter, "failure domain must be non-zero"),
            Self::EmptyLowLatencyPool => {
                write!(formatter, "low-latency lane count must be non-zero")
            }
            Self::InvalidLowLatencySwitchHysteresis(percent) => write!(
                formatter,
                "low-latency switch hysteresis must be below 100 percent: {percent}"
            ),
            Self::InvalidRateBounds => write!(formatter, "invalid scheduler rate bounds"),
            Self::ZeroBulkReprobeInterval => {
                write!(formatter, "bulk reprobe interval must be non-zero")
            }
            Self::ZeroRoundTripTime => write!(formatter, "round-trip time must be non-zero"),
            Self::ZeroDeliveryRate => write!(formatter, "delivery rate must be non-zero"),
            Self::EmptyDeliverySample => write!(formatter, "delivery sample must not be empty"),
            Self::ZeroSampleDuration => write!(formatter, "delivery sample duration is zero"),
            Self::EmptyChunk => write!(formatter, "scheduled chunk must not be empty"),
            Self::InvalidChunkBounds { minimum, maximum } => write!(
                formatter,
                "invalid adaptive chunk bounds {minimum}..={maximum}"
            ),
            Self::DuplicateLane(id) => write!(formatter, "duplicate lane {}", id.get()),
            Self::LaneFailureDomainChanged(id) => {
                write!(formatter, "lane {} changed failure domain", id.get())
            }
            Self::LaneProviderGroupChanged(id) => {
                write!(formatter, "lane {} changed provider group", id.get())
            }
            Self::UnknownLane(id) => write!(formatter, "unknown lane {}", id.get()),
            Self::NoHealthyLane => write!(formatter, "no healthy lane is available"),
            Self::TimeOverflow => write!(formatter, "scheduler time overflow"),
            Self::CounterOverflow => write!(formatter, "scheduler counter overflow"),
        }
    }
}

impl Error for SchedulerError {}

#[cfg(test)]
mod tests {
    use std::collections::BTreeSet;
    use std::time::Duration;

    use super::{
        BondScheduler, DeliverySample, FailureDomain, LaneConfig, LaneId, ProviderId,
        SchedulerConfig, Timestamp, TrafficClass,
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

    fn provider_lane(id: u32, provider: u16, rtt_ms: u64) -> LaneConfig {
        lane(id, rtt_ms, 10)
            .with_provider_group(ProviderId::new(provider).expect("provider is non-zero"))
    }

    #[test]
    fn bulk_cannot_enter_the_protected_pool_when_an_alternative_exists() {
        let mut scheduler = BondScheduler::new(SchedulerConfig::default()).unwrap();
        scheduler.add_lane(lane(1, 10, 10)).unwrap();
        scheduler.add_lane(lane(2, 80, 10)).unwrap();

        let realtime = scheduler
            .schedule(TrafficClass::Realtime, 4_096, Timestamp::ZERO)
            .unwrap();
        let bulk = scheduler
            .schedule(TrafficClass::Bulk, 4_096, Timestamp::ZERO)
            .unwrap();

        assert_eq!(realtime.lane_id, LaneId::new(1).unwrap());
        assert!(realtime.uses_low_latency_pool);
        assert_eq!(bulk.lane_id, LaneId::new(2).unwrap());
        assert!(!bulk.uses_low_latency_pool);
    }

    #[test]
    fn protected_standby_remains_clean_and_takes_over_without_bulk_delay() {
        let mut scheduler = BondScheduler::new(SchedulerConfig {
            low_latency_lane_count: 2,
            ..SchedulerConfig::default()
        })
        .unwrap();
        scheduler.add_lane(lane(1, 10, 10)).unwrap();
        scheduler.add_lane(lane(2, 20, 10)).unwrap();
        scheduler.add_lane(lane(3, 80, 10)).unwrap();

        let realtime = scheduler
            .schedule(TrafficClass::Realtime, 64, Timestamp::ZERO)
            .unwrap();
        let bulk = scheduler
            .schedule(TrafficClass::Bulk, 64 * 1024, Timestamp::ZERO)
            .unwrap();
        assert_eq!(realtime.lane_id, LaneId::new(1).unwrap());
        assert_eq!(bulk.lane_id, LaneId::new(3).unwrap());
        assert_eq!(
            scheduler
                .snapshot(LaneId::new(2).unwrap())
                .unwrap()
                .bytes_scheduled,
            0
        );

        scheduler
            .set_lane_active(LaneId::new(1).unwrap(), false, Timestamp::from_micros(1))
            .unwrap();
        let failover = scheduler
            .schedule(TrafficClass::Realtime, 64, Timestamp::from_micros(1))
            .unwrap();
        assert_eq!(failover.lane_id, LaneId::new(2).unwrap());
        assert!(failover.uses_low_latency_pool);
    }

    #[test]
    fn realtime_redundancy_uses_two_protected_lanes_and_degrades_to_one() {
        let mut scheduler = BondScheduler::new(SchedulerConfig {
            low_latency_lane_count: 2,
            ..SchedulerConfig::default()
        })
        .unwrap();
        scheduler.add_lane(lane(1, 10, 10)).unwrap();
        scheduler.add_lane(lane(2, 20, 10)).unwrap();
        scheduler.add_lane(lane(3, 80, 10)).unwrap();

        let (primary, redundant) = scheduler
            .schedule_redundant_realtime(TrafficClass::Interactive, 64, Timestamp::ZERO)
            .unwrap();
        let redundant = redundant.expect("two protected lanes permit redundancy");
        assert_eq!(primary.lane_id, LaneId::new(1).unwrap());
        assert_eq!(redundant.lane_id, LaneId::new(2).unwrap());
        assert!(primary.uses_low_latency_pool);
        assert!(redundant.uses_low_latency_pool);
        assert_eq!(
            scheduler
                .snapshot(LaneId::new(3).unwrap())
                .unwrap()
                .bytes_scheduled,
            0
        );

        let (bulk, redundant) = scheduler
            .schedule_redundant_realtime(TrafficClass::Bulk, 64, Timestamp::from_micros(1))
            .unwrap();
        assert_eq!(bulk.lane_id, LaneId::new(3).unwrap());
        assert!(redundant.is_none());

        scheduler
            .set_lane_active(LaneId::new(2).unwrap(), false, Timestamp::from_micros(2))
            .unwrap();
        scheduler
            .set_lane_active(LaneId::new(3).unwrap(), false, Timestamp::from_micros(2))
            .unwrap();
        let (degraded, redundant) = scheduler
            .schedule_redundant_realtime(TrafficClass::Interactive, 64, Timestamp::from_micros(2))
            .unwrap();
        assert_eq!(degraded.lane_id, LaneId::new(1).unwrap());
        assert!(redundant.is_none());
    }

    #[test]
    fn mixed_realtime_redundancy_spans_provider_groups() {
        let mut scheduler = BondScheduler::new(SchedulerConfig {
            low_latency_lane_count: 2,
            ..SchedulerConfig::default()
        })
        .unwrap();
        scheduler.add_lane(provider_lane(1, 1, 10)).unwrap();
        scheduler.add_lane(provider_lane(2, 1, 20)).unwrap();
        scheduler.add_lane(provider_lane(3, 2, 500)).unwrap();
        scheduler.add_lane(provider_lane(4, 2, 600)).unwrap();

        assert_eq!(
            scheduler.low_latency_pool(),
            vec![LaneId::new(1).unwrap(), LaneId::new(3).unwrap()]
        );
        let (primary, redundant) = scheduler
            .schedule_redundant_realtime(TrafficClass::Realtime, 64, Timestamp::ZERO)
            .unwrap();
        assert_eq!(primary.lane_id, LaneId::new(1).unwrap());
        assert_eq!(
            redundant.expect("I2P standby is protected").lane_id,
            LaneId::new(3).unwrap()
        );
    }

    #[test]
    fn late_provider_activation_replaces_a_same_provider_standby() {
        let mut scheduler = BondScheduler::new(SchedulerConfig {
            low_latency_lane_count: 2,
            ..SchedulerConfig::default()
        })
        .unwrap();
        scheduler.add_lane(provider_lane(1, 1, 10)).unwrap();
        scheduler.add_lane(provider_lane(2, 1, 20)).unwrap();
        scheduler
            .schedule(TrafficClass::Realtime, 64, Timestamp::ZERO)
            .unwrap();
        assert_eq!(
            scheduler.low_latency_pool(),
            vec![LaneId::new(1).unwrap(), LaneId::new(2).unwrap()]
        );

        scheduler.add_lane(provider_lane(3, 2, 500)).unwrap();
        assert_eq!(
            scheduler.low_latency_pool(),
            vec![LaneId::new(1).unwrap(), LaneId::new(3).unwrap()]
        );
    }

    #[test]
    fn homogeneous_realtime_pool_keeps_its_two_fastest_lanes() {
        let mut scheduler = BondScheduler::new(SchedulerConfig {
            low_latency_lane_count: 2,
            ..SchedulerConfig::default()
        })
        .unwrap();
        scheduler.add_lane(provider_lane(1, 1, 10)).unwrap();
        scheduler.add_lane(provider_lane(2, 1, 20)).unwrap();
        scheduler.add_lane(provider_lane(3, 1, 30)).unwrap();

        assert_eq!(
            scheduler.low_latency_pool(),
            vec![LaneId::new(1).unwrap(), LaneId::new(2).unwrap()]
        );
    }

    #[test]
    fn interactive_chunks_protect_typing_and_stripe_sustained_payloads() {
        assert!(TrafficClass::Control.is_latency_sensitive(64 * 1024));
        assert!(TrafficClass::Realtime.is_latency_sensitive(64 * 1024));
        assert!(TrafficClass::Interactive.is_latency_sensitive(2 * 1024));
        assert!(!TrafficClass::Interactive.is_latency_sensitive(2 * 1024 + 1));
        assert!(!TrafficClass::Bulk.is_latency_sensitive(1));

        let mut scheduler = BondScheduler::new(SchedulerConfig::default()).unwrap();
        scheduler.add_lane(lane(1, 5, 10)).unwrap();
        scheduler.add_lane(lane(2, 40, 10)).unwrap();
        scheduler.add_lane(lane(3, 50, 10)).unwrap();

        let typing = scheduler
            .schedule(TrafficClass::Interactive, 256, Timestamp::ZERO)
            .unwrap();
        assert_eq!(typing.lane_id, LaneId::new(1).unwrap());
        assert!(typing.uses_low_latency_pool);

        let mut bulk_lanes = std::collections::BTreeSet::new();
        for _ in 0..8 {
            let decision = scheduler
                .schedule(TrafficClass::Interactive, 16 * 1024, Timestamp::ZERO)
                .unwrap();
            assert!(!decision.uses_low_latency_pool);
            bulk_lanes.insert(decision.lane_id);
        }
        assert_eq!(
            bulk_lanes,
            [LaneId::new(2).unwrap(), LaneId::new(3).unwrap()].into()
        );
    }

    #[test]
    fn a_single_lane_preserves_liveness_for_bulk() {
        let mut scheduler = BondScheduler::new(SchedulerConfig::default()).unwrap();
        scheduler.add_lane(lane(1, 10, 10)).unwrap();
        let bulk = scheduler
            .schedule(TrafficClass::Bulk, 1_024, Timestamp::ZERO)
            .unwrap();
        assert_eq!(bulk.lane_id, LaneId::new(1).unwrap());
        assert!(bulk.uses_low_latency_pool);
    }

    #[test]
    fn an_inactive_lane_can_return_only_in_its_original_domains() {
        let mut scheduler = BondScheduler::new(SchedulerConfig::default()).unwrap();
        let original = lane(1, 10, 10);
        scheduler.add_lane(original).unwrap();
        scheduler
            .set_lane_active(original.id, false, Timestamp::ZERO)
            .unwrap();

        scheduler
            .restore_lane(original, Timestamp::from_micros(50))
            .unwrap();
        assert!(scheduler.snapshot(original.id).unwrap().active);
        assert!(matches!(
            scheduler.restore_lane(original, Timestamp::from_micros(60)),
            Err(super::SchedulerError::DuplicateLane(_))
        ));

        scheduler
            .set_lane_active(original.id, false, Timestamp::ZERO)
            .unwrap();
        let changed_domain = LaneConfig::new(
            original.id,
            FailureDomain::new(999).unwrap(),
            original.initial_round_trip_time,
            original.initial_rate_bps,
        )
        .unwrap();
        assert!(matches!(
            scheduler.restore_lane(changed_domain, Timestamp::from_micros(70)),
            Err(super::SchedulerError::LaneFailureDomainChanged(_))
        ));

        let changed_provider =
            original.with_provider_group(ProviderId::new(1).expect("provider is non-zero"));
        assert!(matches!(
            scheduler.restore_lane(changed_provider, Timestamp::from_micros(80)),
            Err(super::SchedulerError::LaneProviderGroupChanged(_))
        ));
    }

    #[test]
    fn measurements_dynamically_change_the_reserved_lane() {
        let mut scheduler = BondScheduler::new(SchedulerConfig::default()).unwrap();
        scheduler.add_lane(lane(1, 10, 10)).unwrap();
        scheduler.add_lane(lane(2, 20, 10)).unwrap();
        let sample = DeliverySample::new(
            64 * 1024,
            Duration::from_millis(60),
            Duration::from_millis(1),
        )
        .unwrap();
        for _ in 0..8 {
            scheduler
                .record_delivery(LaneId::new(2).unwrap(), sample)
                .unwrap();
        }
        assert_eq!(scheduler.low_latency_pool(), vec![LaneId::new(2).unwrap()]);
    }

    #[test]
    fn delivery_batch_refreshes_the_protected_pool_once() {
        let mut scheduler = BondScheduler::new(SchedulerConfig::default()).unwrap();
        for id in 1..=4 {
            scheduler
                .add_lane(lane(id, u64::from(id) * 10, 10))
                .unwrap();
        }
        let sample = DeliverySample::new(
            16 * 1024,
            Duration::from_millis(20),
            Duration::from_millis(10),
        )
        .unwrap();
        let refreshes = scheduler.reservation_refreshes;

        scheduler
            .record_deliveries([1, 2, 3, 4].map(|id| (LaneId::new(id).unwrap(), sample)))
            .unwrap();

        assert_eq!(scheduler.reservation_refreshes, refreshes + 1);
        for id in 1..=4 {
            assert_eq!(
                scheduler
                    .snapshot(LaneId::new(id).unwrap())
                    .unwrap()
                    .bytes_acknowledged,
                16 * 1024
            );
        }
    }

    #[test]
    fn low_latency_reservation_ignores_noise_but_accepts_material_improvement() {
        let mut scheduler = BondScheduler::new(SchedulerConfig::default()).unwrap();
        scheduler.add_lane(lane(1, 10, 10)).unwrap();
        scheduler.add_lane(lane(2, 11, 10)).unwrap();
        scheduler
            .record_delivery(
                LaneId::new(1).unwrap(),
                DeliverySample::new(
                    64 * 1024,
                    Duration::from_millis(10),
                    Duration::from_millis(10),
                )
                .unwrap(),
            )
            .unwrap();

        let marginally_faster = DeliverySample::new(
            64 * 1024,
            Duration::from_millis(9),
            Duration::from_millis(9),
        )
        .unwrap();
        for _ in 0..8 {
            scheduler
                .record_delivery(LaneId::new(2).unwrap(), marginally_faster)
                .unwrap();
        }
        assert_eq!(scheduler.low_latency_pool(), vec![LaneId::new(1).unwrap()]);

        let materially_faster = DeliverySample::new(
            64 * 1024,
            Duration::from_millis(2),
            Duration::from_millis(2),
        )
        .unwrap();
        for _ in 0..8 {
            scheduler
                .record_delivery(LaneId::new(2).unwrap(), materially_faster)
                .unwrap();
        }
        assert_eq!(scheduler.low_latency_pool(), vec![LaneId::new(2).unwrap()]);

        scheduler
            .set_lane_active(LaneId::new(2).unwrap(), false, Timestamp::ZERO)
            .unwrap();
        assert_eq!(scheduler.low_latency_pool(), vec![LaneId::new(1).unwrap()]);
    }

    #[test]
    fn unmeasured_prior_cannot_displace_measured_realtime_lane() {
        let mut scheduler = BondScheduler::new(SchedulerConfig::default()).unwrap();
        scheduler.add_lane(lane(1, 10, 10)).unwrap();
        scheduler.add_lane(lane(2, 20, 10)).unwrap();
        let slow_measurement = DeliverySample::new(
            64 * 1024,
            Duration::from_millis(100),
            Duration::from_secs(1),
        )
        .unwrap();
        for _ in 0..8 {
            scheduler
                .record_delivery(LaneId::new(1).unwrap(), slow_measurement)
                .unwrap();
        }

        assert!(
            scheduler
                .snapshot(LaneId::new(1).unwrap())
                .unwrap()
                .delivery_measured
        );
        assert!(
            !scheduler
                .snapshot(LaneId::new(2).unwrap())
                .unwrap()
                .delivery_measured
        );
        assert_eq!(scheduler.low_latency_pool(), vec![LaneId::new(1).unwrap()]);
        assert_eq!(
            scheduler
                .schedule(TrafficClass::Realtime, 128, Timestamp::ZERO)
                .unwrap()
                .lane_id,
            LaneId::new(1).unwrap()
        );

        let fast_measurement = DeliverySample::new(
            64 * 1024,
            Duration::from_millis(100),
            Duration::from_millis(5),
        )
        .unwrap();
        scheduler
            .record_delivery(LaneId::new(2).unwrap(), fast_measurement)
            .unwrap();
        assert_eq!(scheduler.low_latency_pool(), vec![LaneId::new(2).unwrap()]);
    }

    #[test]
    fn asymmetric_bulk_scheduling_favors_capacity_without_starving_lanes() {
        let config = SchedulerConfig {
            low_latency_lane_count: 1,
            ..SchedulerConfig::default()
        };
        let mut scheduler = BondScheduler::new(config).unwrap();
        scheduler.add_lane(lane(1, 5, 10)).unwrap();
        scheduler.add_lane(lane(2, 40, 8)).unwrap();
        scheduler.add_lane(lane(3, 40, 2)).unwrap();
        let mut counts = [0_usize; 4];
        for _ in 0..100 {
            let decision = scheduler
                .schedule(TrafficClass::Bulk, 16 * 1024, Timestamp::ZERO)
                .unwrap();
            counts[decision.lane_id.get() as usize] += 1;
        }
        assert_eq!(counts[1], 0, "bulk entered the reserved lane");
        assert!(counts[2] > counts[3] * 2, "fast lane was not favored");
        assert!(counts[3] > 0, "slow lane was starved");
    }

    #[test]
    fn bulk_probes_every_lane_and_reprobes_a_restored_lane() {
        let mut scheduler = BondScheduler::new(SchedulerConfig::default()).unwrap();
        scheduler.add_lane(lane(1, 5, 10)).unwrap();
        scheduler.add_lane(lane(2, 10, 100)).unwrap();
        scheduler.add_lane(lane(3, 500, 1)).unwrap();
        scheduler.add_lane(lane(4, 750, 1)).unwrap();

        for _ in 0..3 {
            scheduler
                .schedule(TrafficClass::Bulk, 16 * 1024, Timestamp::ZERO)
                .unwrap();
        }
        assert_eq!(
            scheduler
                .snapshot(LaneId::new(1).unwrap())
                .unwrap()
                .bytes_scheduled,
            0
        );
        for id in 2..=4 {
            assert_eq!(
                scheduler
                    .snapshot(LaneId::new(id).unwrap())
                    .unwrap()
                    .bytes_scheduled,
                16 * 1024
            );
        }

        let restored = lane(4, 750, 1);
        scheduler
            .set_lane_active(restored.id, false, Timestamp::ZERO)
            .unwrap();
        scheduler
            .restore_lane(restored, Timestamp::from_micros(1_000_000))
            .unwrap();
        let before = scheduler.snapshot(restored.id).unwrap().bytes_scheduled;
        assert_eq!(
            scheduler
                .schedule(
                    TrafficClass::Bulk,
                    16 * 1024,
                    Timestamp::from_micros(1_000_000),
                )
                .unwrap()
                .lane_id,
            restored.id
        );
        assert_eq!(
            scheduler.snapshot(restored.id).unwrap().bytes_scheduled - before,
            16 * 1024
        );
    }

    #[test]
    fn bulk_periodically_reprobes_without_using_the_protected_lane() {
        let config = SchedulerConfig::default();
        let interval_micros = u64::try_from(config.bulk_reprobe_interval.as_micros()).unwrap();
        let mut scheduler = BondScheduler::new(config).unwrap();
        scheduler.add_lane(lane(1, 5, 10)).unwrap();
        scheduler.add_lane(lane(2, 20, 100)).unwrap();
        scheduler.add_lane(lane(3, 500, 1)).unwrap();

        for _ in 0..2 {
            scheduler
                .schedule(TrafficClass::Bulk, 16 * 1024, Timestamp::ZERO)
                .unwrap();
        }
        let before_fast = scheduler.snapshot(LaneId::new(2).unwrap()).unwrap();
        let before_slow = scheduler.snapshot(LaneId::new(3).unwrap()).unwrap();
        assert_eq!(before_fast.bytes_scheduled, 16 * 1024);
        assert_eq!(before_slow.bytes_scheduled, 16 * 1024);

        let before_expiry = Timestamp::from_micros(interval_micros - 1);
        assert_eq!(
            scheduler
                .schedule(TrafficClass::Bulk, 16 * 1024, before_expiry)
                .unwrap()
                .lane_id,
            LaneId::new(2).unwrap()
        );

        let expired = Timestamp::from_micros(interval_micros);
        let first = scheduler
            .schedule(TrafficClass::Bulk, 16 * 1024, expired)
            .unwrap();
        let second = scheduler
            .schedule(TrafficClass::Bulk, 16 * 1024, expired)
            .unwrap();
        assert_eq!(
            [first.lane_id, second.lane_id]
                .into_iter()
                .collect::<BTreeSet<_>>(),
            [LaneId::new(2).unwrap(), LaneId::new(3).unwrap()].into()
        );
        assert_eq!(
            scheduler
                .snapshot(LaneId::new(1).unwrap())
                .unwrap()
                .bytes_scheduled,
            0
        );
        assert_eq!(
            scheduler
                .snapshot(LaneId::new(3).unwrap())
                .unwrap()
                .bytes_scheduled
                - before_slow.bytes_scheduled,
            16 * 1024
        );
    }

    #[test]
    fn measured_capacity_changes_future_bulk_allocation() {
        let mut scheduler = BondScheduler::new(SchedulerConfig::default()).unwrap();
        scheduler.add_lane(lane(1, 5, 10)).unwrap();
        scheduler.add_lane(lane(2, 40, 8)).unwrap();
        scheduler.add_lane(lane(3, 40, 2)).unwrap();

        let faster = DeliverySample::new(
            128 * 1024,
            Duration::from_micros(52_429),
            Duration::from_millis(40),
        )
        .unwrap();
        for _ in 0..12 {
            scheduler
                .record_delivery(LaneId::new(3).unwrap(), faster)
                .unwrap();
        }

        let mut counts = [0_usize; 4];
        let after_old_queue = Timestamp::from_micros(10_000_000);
        for _ in 0..100 {
            let decision = scheduler
                .schedule(TrafficClass::Bulk, 16 * 1024, after_old_queue)
                .unwrap();
            counts[decision.lane_id.get() as usize] += 1;
        }
        assert!(counts[3] > counts[2] * 2, "new capacity was not learned");
    }

    #[test]
    fn adaptive_bulk_chunks_follow_bdp_and_back_down_for_queue_delay() {
        let mut scheduler = BondScheduler::new(SchedulerConfig::default()).unwrap();
        scheduler.add_lane(lane(1, 5, 100)).unwrap();
        scheduler.add_lane(lane(2, 40, 1)).unwrap();

        let initial = scheduler
            .schedule_adaptive_bulk(4 * 1024, 64 * 1024, 64 * 1024, Timestamp::ZERO)
            .unwrap();
        assert_eq!(initial.decision.lane_id, LaneId::new(2).unwrap());
        assert_eq!(initial.payload_bytes, 5_000);

        scheduler
            .record_delivery(
                LaneId::new(2).unwrap(),
                DeliverySample::new(
                    1024 * 1024,
                    Duration::from_millis(10),
                    Duration::from_millis(40),
                )
                .unwrap(),
            )
            .unwrap();
        let grown = scheduler
            .schedule_adaptive_bulk(4 * 1024, 64 * 1024, 64 * 1024, Timestamp::ZERO)
            .unwrap();
        assert_eq!(grown.payload_bytes, 32 * 1024);
        assert!(grown.payload_bytes > initial.payload_bytes);

        let mut pressured = grown;
        for _ in 0..64 {
            pressured = scheduler
                .schedule_adaptive_bulk(4 * 1024, 64 * 1024, 64 * 1024, Timestamp::ZERO)
                .unwrap();
            if pressured.payload_bytes == 4 * 1024 {
                break;
            }
        }
        assert_eq!(pressured.payload_bytes, 4 * 1024);
        assert_eq!(scheduler.decision_heap_scratch_bytes(), 0);
    }

    #[test]
    fn adaptive_bulk_chunk_bounds_fail_closed() {
        let mut scheduler = BondScheduler::new(SchedulerConfig::default()).unwrap();
        scheduler.add_lane(lane(1, 10, 10)).unwrap();

        assert!(matches!(
            scheduler.schedule_adaptive_bulk(8 * 1024, 4 * 1024, 16 * 1024, Timestamp::ZERO),
            Err(super::SchedulerError::InvalidChunkBounds { .. })
        ));
        assert_eq!(
            scheduler
                .schedule_adaptive_bulk(4 * 1024, 8 * 1024, 1_000, Timestamp::ZERO)
                .unwrap()
                .payload_bytes,
            1_000
        );
    }

    #[test]
    fn eight_lane_decisions_use_no_heap_backed_scratch() {
        let mut scheduler = BondScheduler::new(SchedulerConfig {
            low_latency_lane_count: 2,
            ..SchedulerConfig::default()
        })
        .unwrap();
        for id in 1..=8 {
            scheduler
                .add_lane(lane(id, u64::from(id) * 5, 4 + u64::from(id)))
                .unwrap();
        }
        assert_eq!(scheduler.decision_heap_scratch_bytes(), 0);
        assert_eq!(scheduler.decision_lane_pass_limit(), 2);

        let mut bulk_decisions = 0;
        let mut realtime_decisions = 0;
        for decision_index in 0..16_384 {
            let class = if decision_index % 5 == 0 {
                TrafficClass::Realtime
            } else {
                TrafficClass::Bulk
            };
            let excluded = (decision_index % 7 == 0).then_some(LaneId::new(8).unwrap());
            let decision = scheduler
                .schedule_excluding(class, 16 * 1024, Timestamp::ZERO, excluded)
                .unwrap();
            assert_ne!(Some(decision.lane_id), excluded);
            match class {
                TrafficClass::Bulk => {
                    assert!(!decision.uses_low_latency_pool);
                    bulk_decisions += 1;
                }
                TrafficClass::Realtime => {
                    assert!(decision.uses_low_latency_pool);
                    realtime_decisions += 1;
                }
                TrafficClass::Control | TrafficClass::Interactive => unreachable!(),
            }
        }
        for _ in 0..16_384 {
            let decision = scheduler
                .schedule_adaptive_bulk(4 * 1024, 64 * 1024, 64 * 1024, Timestamp::ZERO)
                .unwrap();
            assert!(!decision.decision.uses_low_latency_pool);
            assert!((4 * 1024..=64 * 1024).contains(&decision.payload_bytes));
        }
        assert!(bulk_decisions > 0);
        assert!(realtime_decisions > 0);
        assert_eq!(scheduler.decision_heap_scratch_bytes(), 0);
        assert_eq!(scheduler.decision_lane_pass_limit(), 2);
    }
}
