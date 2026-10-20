use std::collections::{BTreeMap, BTreeSet};
use std::error::Error;
use std::fmt;
use std::time::Duration;

use crate::{FailureDomain, LaneId};

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub struct ProviderId(u16);

impl ProviderId {
    pub fn new(value: u16) -> Result<Self, ScalingError> {
        if value == 0 {
            Err(ScalingError::ZeroProviderId)
        } else {
            Ok(Self(value))
        }
    }

    pub const fn get(self) -> u16 {
        self.0
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct ScalingConfig {
    pub minimum_active_lanes: usize,
    pub maximum_active_lanes: usize,
    pub minimum_lanes_per_provider: usize,
    pub scale_up_queue_delay: Duration,
    pub scale_down_queue_delay: Duration,
    pub scale_up_send_window_percent: u8,
    pub scale_down_send_window_percent: u8,
    pub minimum_marginal_goodput_bps: u64,
    pub replacement_gain_percent: u16,
    pub maximum_startup_latency: Duration,
    pub maximum_cpu_millicores: u32,
    pub maximum_memory_bytes: u64,
}

impl ScalingConfig {
    pub fn validate(self) -> Result<Self, ScalingError> {
        if self.minimum_active_lanes == 0
            || self.minimum_active_lanes > self.maximum_active_lanes
            || self.minimum_lanes_per_provider == 0
            || self.scale_down_queue_delay >= self.scale_up_queue_delay
            || self.scale_up_send_window_percent > 100
            || self.scale_down_send_window_percent >= self.scale_up_send_window_percent
            || self.minimum_marginal_goodput_bps == 0
            || self.replacement_gain_percent == 0
            || self.maximum_startup_latency.is_zero()
            || self.maximum_cpu_millicores == 0
            || self.maximum_memory_bytes == 0
        {
            return Err(ScalingError::InvalidConfig);
        }
        Ok(self)
    }
}

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct ScalingPressure {
    send_window_utilization_percent: u8,
    application_backpressure: bool,
}

impl ScalingPressure {
    pub fn new(send_window_utilization_percent: u8) -> Result<Self, ScalingError> {
        if send_window_utilization_percent > 100 {
            return Err(ScalingError::InvalidPressure);
        }
        Ok(Self {
            send_window_utilization_percent,
            application_backpressure: false,
        })
    }

    pub const fn with_application_backpressure(mut self, observed: bool) -> Self {
        self.application_backpressure = observed;
        self
    }

    pub const fn send_window_utilization_percent(self) -> u8 {
        self.send_window_utilization_percent
    }

    pub const fn application_backpressure(self) -> bool {
        self.application_backpressure
    }
}

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct ResourceUsage {
    pub cpu_millicores: u32,
    pub memory_bytes: u64,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct LaneScalingSample {
    pub id: LaneId,
    pub failure_domain: FailureDomain,
    pub provider: ProviderId,
    pub admitted: bool,
    pub healthy: bool,
    pub required: bool,
    pub protected_for_low_latency: bool,
    pub drain_eligible: bool,
    pub queue_delay: Duration,
    pub marginal_goodput_bps: u64,
    pub expected_goodput_bps: u64,
    pub startup_latency: Duration,
    pub cpu_millicores: u32,
    pub memory_bytes: u64,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ScalingReason {
    MinimumTopology,
    ProviderDiversity,
    QueuePressure,
    ResourcePressure,
    MarginalGoodput,
    Unhealthy,
    BetterCandidate,
    PressureCleared,
    Exploration,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ScalingAction {
    Hold,
    Admit {
        lane_id: LaneId,
        reason: ScalingReason,
    },
    Drain {
        lane_id: LaneId,
        reason: ScalingReason,
    },
    Replace {
        remove: LaneId,
        admit: LaneId,
        reason: ScalingReason,
    },
}

#[derive(Debug)]
pub struct AdaptiveScalingController {
    config: ScalingConfig,
}

impl AdaptiveScalingController {
    pub fn new(config: ScalingConfig) -> Result<Self, ScalingError> {
        Ok(Self {
            config: config.validate()?,
        })
    }

    pub fn evaluate(
        &self,
        lanes: &[LaneScalingSample],
        resources: ResourceUsage,
    ) -> Result<ScalingAction, ScalingError> {
        self.evaluate_with_pressure(lanes, resources, ScalingPressure::default())
    }

    pub fn evaluate_with_pressure(
        &self,
        lanes: &[LaneScalingSample],
        resources: ResourceUsage,
        pressure: ScalingPressure,
    ) -> Result<ScalingAction, ScalingError> {
        self.validate_samples(lanes)?;
        let admitted = lanes
            .iter()
            .filter(|lane| lane.admitted)
            .collect::<Vec<_>>();
        let inactive = lanes
            .iter()
            .filter(|lane| !lane.admitted && lane.healthy)
            .collect::<Vec<_>>();
        if admitted.len() > self.config.maximum_active_lanes {
            return self
                .drain_candidate(&admitted, ScalingReason::ResourcePressure)
                .map(Ok)
                .unwrap_or(Ok(ScalingAction::Hold));
        }

        if let Some(unhealthy) = admitted.iter().find(|lane| !lane.healthy) {
            let admission_resources = if unhealthy.required {
                resources
            } else {
                resources_after_removal(resources, unhealthy)
            };
            if let Some(candidate) = self.best_admission(
                inactive
                    .iter()
                    .copied()
                    .filter(|lane| lane.provider == unhealthy.provider),
                admission_resources,
            ) {
                if unhealthy.required {
                    return Ok(if admitted.len() < self.config.maximum_active_lanes {
                        ScalingAction::Admit {
                            lane_id: candidate.id,
                            reason: ScalingReason::Unhealthy,
                        }
                    } else {
                        ScalingAction::Hold
                    });
                }
                return Ok(ScalingAction::Replace {
                    remove: unhealthy.id,
                    admit: candidate.id,
                    reason: ScalingReason::Unhealthy,
                });
            }
            if !unhealthy.protected_for_low_latency
                && !unhealthy.required
                && admitted.len() > self.config.minimum_active_lanes
                && self.provider_count(&admitted, unhealthy.provider)
                    > self.config.minimum_lanes_per_provider
            {
                return Ok(ScalingAction::Drain {
                    lane_id: unhealthy.id,
                    reason: ScalingReason::Unhealthy,
                });
            }
        }

        let providers = lanes
            .iter()
            .map(|lane| lane.provider)
            .collect::<BTreeSet<_>>();
        for provider in providers {
            if self.provider_count(&admitted, provider) < self.config.minimum_lanes_per_provider {
                if let Some(candidate) = self.best_admission(
                    inactive
                        .iter()
                        .copied()
                        .filter(|lane| lane.provider == provider),
                    resources,
                ) {
                    return Ok(ScalingAction::Admit {
                        lane_id: candidate.id,
                        reason: ScalingReason::ProviderDiversity,
                    });
                }
            }
        }

        if admitted.len() < self.config.minimum_active_lanes {
            return Ok(self
                .best_admission(inactive.iter().copied(), resources)
                .map(|lane| ScalingAction::Admit {
                    lane_id: lane.id,
                    reason: ScalingReason::MinimumTopology,
                })
                .unwrap_or(ScalingAction::Hold));
        }

        if resources.cpu_millicores > self.config.maximum_cpu_millicores
            || resources.memory_bytes > self.config.maximum_memory_bytes
        {
            return Ok(self
                .drain_candidate(&admitted, ScalingReason::ResourcePressure)
                .unwrap_or(ScalingAction::Hold));
        }

        let maximum_queue_delay = maximum_queue_delay(&admitted);
        if admitted.len() < self.config.maximum_active_lanes
            && self.capacity_pressure(maximum_queue_delay, pressure)
        {
            return Ok(self
                .best_admission(inactive.iter().copied(), resources)
                .map(|lane| ScalingAction::Admit {
                    lane_id: lane.id,
                    reason: ScalingReason::QueuePressure,
                })
                .unwrap_or(ScalingAction::Hold));
        }

        if admitted.len() > self.config.minimum_active_lanes
            && maximum_queue_delay <= self.config.scale_down_queue_delay
            && pressure.send_window_utilization_percent
                <= self.config.scale_down_send_window_percent
            && !pressure.application_backpressure
            && admitted.iter().any(|lane| {
                !lane.protected_for_low_latency
                    && lane.drain_eligible
                    && lane.marginal_goodput_bps < self.config.minimum_marginal_goodput_bps
            })
        {
            return Ok(self
                .drain_candidate(&admitted, ScalingReason::MarginalGoodput)
                .unwrap_or(ScalingAction::Hold));
        }
        if maximum_queue_delay > self.config.scale_down_queue_delay
            || pressure.send_window_utilization_percent > self.config.scale_down_send_window_percent
            || pressure.application_backpressure
        {
            if let Some(action) = self.replacement_candidate(&admitted, &inactive, resources) {
                return Ok(action);
            }
        }
        Ok(ScalingAction::Hold)
    }

    pub fn has_capacity_pressure(
        &self,
        lanes: &[LaneScalingSample],
        pressure: ScalingPressure,
    ) -> Result<bool, ScalingError> {
        self.validate_samples(lanes)?;
        let admitted = lanes
            .iter()
            .filter(|lane| lane.admitted)
            .collect::<Vec<_>>();
        Ok(self.capacity_pressure(maximum_queue_delay(&admitted), pressure))
    }

    fn capacity_pressure(&self, maximum_queue_delay: Duration, pressure: ScalingPressure) -> bool {
        maximum_queue_delay >= self.config.scale_up_queue_delay
            || pressure.send_window_utilization_percent >= self.config.scale_up_send_window_percent
            || pressure.application_backpressure
    }

    pub fn evaluate_admission_batch(
        &self,
        lanes: &[LaneScalingSample],
        resources: ResourceUsage,
        pressure: ScalingPressure,
        maximum_admissions: usize,
    ) -> Result<Vec<ScalingAction>, ScalingError> {
        if maximum_admissions == 0 {
            return Err(ScalingError::ZeroAdmissionBatch);
        }
        let mut simulated = lanes.to_vec();
        let mut simulated_resources = resources;
        let mut actions = Vec::with_capacity(maximum_admissions);
        while actions.len() < maximum_admissions {
            let action = self.evaluate_with_pressure(&simulated, simulated_resources, pressure)?;
            let ScalingAction::Admit { reason, .. } = action else {
                if actions.is_empty() && action != ScalingAction::Hold {
                    actions.push(action);
                }
                break;
            };
            let action = self.balance_admission(action, &simulated, simulated_resources);
            let ScalingAction::Admit { lane_id, .. } = action else {
                unreachable!("admission balancing preserves the action kind");
            };
            let lane = simulated
                .iter_mut()
                .find(|lane| lane.id == lane_id)
                .expect("evaluated admission lane exists");
            lane.admitted = true;
            simulated_resources.cpu_millicores = simulated_resources
                .cpu_millicores
                .saturating_add(lane.cpu_millicores);
            simulated_resources.memory_bytes = simulated_resources
                .memory_bytes
                .saturating_add(lane.memory_bytes);
            actions.push(action);
            if !matches!(
                reason,
                ScalingReason::QueuePressure
                    | ScalingReason::MinimumTopology
                    | ScalingReason::ProviderDiversity
            ) {
                break;
            }
        }
        Ok(actions)
    }

    pub fn evaluate_marginal_drain_batch(
        &self,
        lanes: &[LaneScalingSample],
        resources: ResourceUsage,
        pressure: ScalingPressure,
        maximum_drains: usize,
    ) -> Result<Vec<ScalingAction>, ScalingError> {
        if maximum_drains == 0 {
            return Err(ScalingError::ZeroDrainBatch);
        }
        let mut simulated = lanes.to_vec();
        let mut simulated_resources = resources;
        let mut actions = Vec::with_capacity(maximum_drains);
        while actions.len() < maximum_drains {
            let action = self.evaluate_with_pressure(&simulated, simulated_resources, pressure)?;
            let ScalingAction::Drain {
                lane_id,
                reason: ScalingReason::MarginalGoodput,
            } = action
            else {
                break;
            };
            let lane = simulated
                .iter_mut()
                .find(|lane| lane.id == lane_id)
                .expect("evaluated drain lane exists");
            lane.admitted = false;
            simulated_resources = resources_after_removal(simulated_resources, lane);
            actions.push(action);
        }
        Ok(actions)
    }

    fn balance_admission(
        &self,
        action: ScalingAction,
        lanes: &[LaneScalingSample],
        resources: ResourceUsage,
    ) -> ScalingAction {
        let ScalingAction::Admit {
            lane_id: selected,
            reason,
        } = action
        else {
            return action;
        };
        let counts = lanes.iter().filter(|lane| lane.admitted).fold(
            BTreeMap::<ProviderId, usize>::new(),
            |mut counts, lane| {
                *counts.entry(lane.provider).or_default() += 1;
                counts
            },
        );
        let selected_provider = lanes
            .iter()
            .find(|lane| lane.id == selected)
            .expect("selected admission lane exists")
            .provider;
        let minimum = lanes
            .iter()
            .map(|lane| lane.provider)
            .collect::<BTreeSet<_>>()
            .into_iter()
            .map(|provider| counts.get(&provider).copied().unwrap_or(0))
            .min()
            .unwrap_or(0);
        if counts.get(&selected_provider).copied().unwrap_or(0) <= minimum {
            return action;
        }
        self.best_admission(
            lanes.iter().filter(|lane| {
                !lane.admitted
                    && lane.healthy
                    && counts.get(&lane.provider).copied().unwrap_or(0) == minimum
            }),
            resources,
        )
        .map(|lane| ScalingAction::Admit {
            lane_id: lane.id,
            reason,
        })
        .unwrap_or(action)
    }

    fn validate_samples(&self, lanes: &[LaneScalingSample]) -> Result<(), ScalingError> {
        if lanes.is_empty() {
            return Err(ScalingError::EmptyTopology);
        }
        let mut ids = BTreeSet::new();
        let mut domains = BTreeSet::new();
        for lane in lanes {
            if !ids.insert(lane.id) {
                return Err(ScalingError::DuplicateLane(lane.id));
            }
            if !domains.insert(lane.failure_domain) {
                return Err(ScalingError::DuplicateFailureDomain(lane.failure_domain));
            }
            if lane.startup_latency.is_zero() || lane.cpu_millicores == 0 || lane.memory_bytes == 0
            {
                return Err(ScalingError::InvalidSample(lane.id));
            }
        }
        Ok(())
    }

    fn provider_count(&self, active: &[&LaneScalingSample], provider: ProviderId) -> usize {
        active
            .iter()
            .filter(|lane| lane.provider == provider)
            .count()
    }

    fn best_admission<'a>(
        &self,
        candidates: impl Iterator<Item = &'a LaneScalingSample>,
        resources: ResourceUsage,
    ) -> Option<&'a LaneScalingSample> {
        candidates
            .filter(|lane| {
                lane.startup_latency <= self.config.maximum_startup_latency
                    && resources
                        .cpu_millicores
                        .checked_add(lane.cpu_millicores)
                        .is_some_and(|value| value <= self.config.maximum_cpu_millicores)
                    && resources
                        .memory_bytes
                        .checked_add(lane.memory_bytes)
                        .is_some_and(|value| value <= self.config.maximum_memory_bytes)
            })
            .min_by_key(|lane| {
                (
                    std::cmp::Reverse(path_utility(lane, lane.expected_goodput_bps)),
                    std::cmp::Reverse(lane.expected_goodput_bps),
                    lane.startup_latency,
                    lane.id,
                )
            })
    }

    fn drain_candidate(
        &self,
        active: &[&LaneScalingSample],
        reason: ScalingReason,
    ) -> Option<ScalingAction> {
        if active.len() <= self.config.minimum_active_lanes {
            return None;
        }
        active
            .iter()
            .copied()
            .filter(|lane| {
                !lane.required
                    && !lane.protected_for_low_latency
                    && (reason == ScalingReason::ResourcePressure || lane.drain_eligible)
                    && self.provider_count(active, lane.provider)
                        > self.config.minimum_lanes_per_provider
            })
            .min_by_key(|lane| {
                (
                    path_utility(lane, lane.marginal_goodput_bps),
                    lane.marginal_goodput_bps,
                    lane.queue_delay,
                    std::cmp::Reverse(lane.memory_bytes),
                    std::cmp::Reverse(lane.cpu_millicores),
                    lane.id,
                )
            })
            .map(|lane| ScalingAction::Drain {
                lane_id: lane.id,
                reason,
            })
    }

    fn replacement_candidate(
        &self,
        active: &[&LaneScalingSample],
        inactive: &[&LaneScalingSample],
        resources: ResourceUsage,
    ) -> Option<ScalingAction> {
        let mut active_by_provider = BTreeMap::new();
        for lane in active {
            if !lane.required && !lane.protected_for_low_latency && lane.drain_eligible {
                active_by_provider
                    .entry(lane.provider)
                    .and_modify(|current: &mut &LaneScalingSample| {
                        if (lane.marginal_goodput_bps, lane.id)
                            < (current.marginal_goodput_bps, current.id)
                        {
                            *current = lane;
                        }
                    })
                    .or_insert(*lane);
            }
        }
        active_by_provider
            .into_iter()
            .filter_map(|(provider, current)| {
                let candidate = self.best_admission(
                    inactive
                        .iter()
                        .copied()
                        .filter(|lane| lane.provider == provider),
                    resources_after_removal(resources, current),
                )?;
                let current_utility = path_utility(current, current.marginal_goodput_bps);
                let candidate_utility = path_utility(candidate, candidate.expected_goodput_bps);
                let required =
                    current_utility * u128::from(100 + self.config.replacement_gain_percent) / 100;
                (candidate_utility >= required).then_some((
                    std::cmp::Reverse(candidate_utility),
                    candidate.startup_latency,
                    current.id,
                    candidate.id,
                ))
            })
            .min()
            .map(|(_, _, remove, admit)| ScalingAction::Replace {
                remove,
                admit,
                reason: ScalingReason::BetterCandidate,
            })
    }
}

fn maximum_queue_delay(lanes: &[&LaneScalingSample]) -> Duration {
    lanes
        .iter()
        .map(|lane| lane.queue_delay)
        .max()
        .unwrap_or_default()
}

fn resources_after_removal(resources: ResourceUsage, lane: &LaneScalingSample) -> ResourceUsage {
    ResourceUsage {
        cpu_millicores: resources.cpu_millicores.saturating_sub(lane.cpu_millicores),
        memory_bytes: resources.memory_bytes.saturating_sub(lane.memory_bytes),
    }
}

fn path_utility(lane: &LaneScalingSample, goodput_bps: u64) -> u128 {
    let memory_mib = lane.memory_bytes.div_ceil(1024 * 1024);
    let startup_deciseconds =
        u64::try_from(lane.startup_latency.as_millis() / 100).unwrap_or(u64::MAX);
    let cost = u128::from(lane.cpu_millicores)
        .saturating_add(u128::from(memory_mib))
        .saturating_add(u128::from(startup_deciseconds))
        .max(1);
    u128::from(goodput_bps).saturating_mul(1_000_000) / cost
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ScalingError {
    ZeroProviderId,
    InvalidConfig,
    InvalidPressure,
    EmptyTopology,
    DuplicateLane(LaneId),
    DuplicateFailureDomain(FailureDomain),
    InvalidSample(LaneId),
    ZeroAdmissionBatch,
    ZeroDrainBatch,
}

impl fmt::Display for ScalingError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::ZeroProviderId => write!(formatter, "provider ID must be non-zero"),
            Self::InvalidConfig => write!(formatter, "invalid adaptive scaling configuration"),
            Self::InvalidPressure => write!(formatter, "invalid adaptive scaling pressure"),
            Self::EmptyTopology => write!(formatter, "adaptive scaling topology is empty"),
            Self::DuplicateLane(id) => write!(formatter, "duplicate scaling lane {}", id.get()),
            Self::DuplicateFailureDomain(domain) => write!(
                formatter,
                "duplicate scaling failure domain {}",
                domain.get()
            ),
            Self::InvalidSample(id) => {
                write!(formatter, "invalid scaling sample for lane {}", id.get())
            }
            Self::ZeroAdmissionBatch => write!(formatter, "admission batch must be non-zero"),
            Self::ZeroDrainBatch => write!(formatter, "drain batch must be non-zero"),
        }
    }
}

impl Error for ScalingError {}

#[cfg(test)]
mod tests {
    use std::time::Duration;

    use super::{
        AdaptiveScalingController, LaneScalingSample, ProviderId, ResourceUsage, ScalingAction,
        ScalingConfig, ScalingPressure, ScalingReason,
    };
    use crate::{FailureDomain, LaneId};

    fn config() -> ScalingConfig {
        ScalingConfig {
            minimum_active_lanes: 4,
            maximum_active_lanes: 8,
            minimum_lanes_per_provider: 1,
            scale_up_queue_delay: Duration::from_millis(50),
            scale_down_queue_delay: Duration::from_millis(5),
            scale_up_send_window_percent: 75,
            scale_down_send_window_percent: 10,
            minimum_marginal_goodput_bps: 100_000,
            replacement_gain_percent: 25,
            maximum_startup_latency: Duration::from_secs(60),
            maximum_cpu_millicores: 1_000,
            maximum_memory_bytes: 1024 * 1024 * 1024,
        }
    }

    fn lane(id: u32, provider: u16, admitted: bool) -> LaneScalingSample {
        LaneScalingSample {
            id: LaneId::new(id).unwrap(),
            failure_domain: FailureDomain::new(u64::from(id)).unwrap(),
            provider: ProviderId::new(provider).unwrap(),
            admitted,
            healthy: true,
            required: id <= 2,
            protected_for_low_latency: id <= 2,
            drain_eligible: true,
            queue_delay: Duration::from_millis(2),
            marginal_goodput_bps: 1_000_000,
            expected_goodput_bps: 1_000_000,
            startup_latency: Duration::from_secs(10),
            cpu_millicores: 100,
            memory_bytes: 64 * 1024 * 1024,
        }
    }

    #[test]
    fn restores_provider_diversity_before_optional_capacity() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let lanes = [
            lane(1, 1, true),
            lane(2, 1, true),
            lane(3, 1, true),
            lane(4, 2, false),
            lane(5, 1, false),
        ];
        let action = controller
            .evaluate(
                &lanes,
                ResourceUsage {
                    cpu_millicores: 300,
                    memory_bytes: 192 * 1024 * 1024,
                },
            )
            .unwrap();
        assert_eq!(
            action,
            ScalingAction::Admit {
                lane_id: LaneId::new(4).unwrap(),
                reason: ScalingReason::ProviderDiversity,
            }
        );
    }

    #[test]
    fn queue_pressure_uses_goodput_then_startup_and_respects_resource_budgets() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let mut lanes = [
            lane(1, 1, true),
            lane(2, 2, true),
            lane(3, 1, true),
            lane(4, 2, true),
            lane(5, 1, false),
            lane(6, 2, false),
            lane(7, 2, false),
            lane(8, 1, false),
        ];
        lanes[0].queue_delay = Duration::from_millis(80);
        lanes[4].expected_goodput_bps = 2_000_000;
        lanes[4].startup_latency = Duration::from_secs(20);
        lanes[5].expected_goodput_bps = 2_000_000;
        lanes[5].startup_latency = Duration::from_secs(5);
        lanes[6].expected_goodput_bps = 5_000_000;
        lanes[6].memory_bytes = 900 * 1024 * 1024;
        lanes[7].expected_goodput_bps = 6_000_000;
        lanes[7].cpu_millicores = 700;
        let action = controller
            .evaluate(
                &lanes,
                ResourceUsage {
                    cpu_millicores: 400,
                    memory_bytes: 256 * 1024 * 1024,
                },
            )
            .unwrap();
        assert_eq!(
            action,
            ScalingAction::Admit {
                lane_id: LaneId::new(6).unwrap(),
                reason: ScalingReason::QueuePressure,
            }
        );
    }

    #[test]
    fn admission_optimizes_expected_goodput_per_resource_cost() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let mut lanes = [
            lane(1, 1, true),
            lane(2, 2, true),
            lane(3, 1, true),
            lane(4, 2, true),
            lane(5, 1, false),
            lane(6, 2, false),
        ];
        lanes[0].queue_delay = Duration::from_millis(80);
        lanes[4].expected_goodput_bps = 3_000_000;
        lanes[4].cpu_millicores = 500;
        lanes[4].memory_bytes = 512 * 1024 * 1024;
        lanes[5].expected_goodput_bps = 2_000_000;
        lanes[5].cpu_millicores = 50;
        lanes[5].memory_bytes = 32 * 1024 * 1024;
        lanes[5].startup_latency = Duration::from_secs(5);

        assert_eq!(
            controller
                .evaluate(
                    &lanes,
                    ResourceUsage {
                        cpu_millicores: 400,
                        memory_bytes: 256 * 1024 * 1024,
                    },
                )
                .unwrap(),
            ScalingAction::Admit {
                lane_id: LaneId::new(6).unwrap(),
                reason: ScalingReason::QueuePressure,
            }
        );
    }

    #[test]
    fn saturated_send_window_admits_when_lane_queues_stay_short() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let lanes = [
            lane(1, 1, true),
            lane(2, 2, true),
            lane(3, 1, true),
            lane(4, 2, true),
            lane(5, 1, false),
        ];
        let action = controller
            .evaluate_with_pressure(
                &lanes,
                ResourceUsage {
                    cpu_millicores: 400,
                    memory_bytes: 256 * 1024 * 1024,
                },
                ScalingPressure::new(80).unwrap(),
            )
            .unwrap();
        assert_eq!(
            action,
            ScalingAction::Admit {
                lane_id: LaneId::new(5).unwrap(),
                reason: ScalingReason::QueuePressure,
            }
        );
    }

    #[test]
    fn capacity_pressure_reports_every_scale_up_signal() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let mut lanes = [
            lane(1, 1, true),
            lane(2, 2, true),
            lane(3, 1, true),
            lane(4, 2, true),
        ];
        assert!(!controller
            .has_capacity_pressure(&lanes, ScalingPressure::default())
            .unwrap());

        lanes[0].queue_delay = Duration::from_millis(50);
        assert!(controller
            .has_capacity_pressure(&lanes, ScalingPressure::default())
            .unwrap());
        lanes[0].queue_delay = Duration::default();

        assert!(controller
            .has_capacity_pressure(&lanes, ScalingPressure::new(75).unwrap())
            .unwrap());
        assert!(controller
            .has_capacity_pressure(
                &lanes,
                ScalingPressure::default().with_application_backpressure(true),
            )
            .unwrap());
    }

    #[test]
    fn send_window_hysteresis_prevents_premature_drain() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let mut lanes = [
            lane(1, 1, true),
            lane(2, 2, true),
            lane(3, 1, true),
            lane(4, 2, true),
            lane(5, 1, true),
        ];
        lanes[4].marginal_goodput_bps = 1;
        assert_eq!(
            controller
                .evaluate_with_pressure(
                    &lanes,
                    ResourceUsage {
                        cpu_millicores: 500,
                        memory_bytes: 320 * 1024 * 1024,
                    },
                    ScalingPressure::new(50).unwrap(),
                )
                .unwrap(),
            ScalingAction::Hold
        );
    }

    #[test]
    fn application_backpressure_admits_and_retains_capacity() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let mut lanes = [
            lane(1, 1, true),
            lane(2, 2, true),
            lane(3, 1, true),
            lane(4, 2, true),
            lane(5, 1, false),
        ];
        let resources = ResourceUsage {
            cpu_millicores: 400,
            memory_bytes: 256 * 1024 * 1024,
        };
        let pressure = ScalingPressure::new(0)
            .unwrap()
            .with_application_backpressure(true);
        assert!(matches!(
            controller
                .evaluate_with_pressure(&lanes, resources, pressure)
                .unwrap(),
            ScalingAction::Admit {
                lane_id,
                reason: ScalingReason::QueuePressure,
            } if lane_id == LaneId::new(5).unwrap()
        ));
        lanes[4].admitted = true;
        lanes[4].marginal_goodput_bps = 1;
        assert_eq!(
            controller
                .evaluate_with_pressure(&lanes, resources, pressure)
                .unwrap(),
            ScalingAction::Hold
        );
    }

    #[test]
    fn pressure_batches_provider_balanced_admissions_within_resources() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let lanes = [
            lane(1, 1, true),
            lane(2, 2, true),
            lane(3, 1, true),
            lane(4, 2, true),
            lane(5, 1, false),
            lane(6, 1, false),
            lane(7, 2, false),
            lane(8, 2, false),
        ];
        let pressure = ScalingPressure::new(80).unwrap();
        let actions = controller
            .evaluate_admission_batch(
                &lanes,
                ResourceUsage {
                    cpu_millicores: 400,
                    memory_bytes: 256 * 1024 * 1024,
                },
                pressure,
                4,
            )
            .unwrap();
        assert_eq!(
            actions,
            vec![
                ScalingAction::Admit {
                    lane_id: LaneId::new(5).unwrap(),
                    reason: ScalingReason::QueuePressure,
                },
                ScalingAction::Admit {
                    lane_id: LaneId::new(7).unwrap(),
                    reason: ScalingReason::QueuePressure,
                },
                ScalingAction::Admit {
                    lane_id: LaneId::new(6).unwrap(),
                    reason: ScalingReason::QueuePressure,
                },
                ScalingAction::Admit {
                    lane_id: LaneId::new(8).unwrap(),
                    reason: ScalingReason::QueuePressure,
                },
            ]
        );

        let constrained = ScalingConfig {
            maximum_cpu_millicores: 600,
            ..config()
        };
        assert_eq!(
            AdaptiveScalingController::new(constrained)
                .unwrap()
                .evaluate_admission_batch(
                    &lanes,
                    ResourceUsage {
                        cpu_millicores: 400,
                        memory_bytes: 256 * 1024 * 1024,
                    },
                    pressure,
                    4,
                )
                .unwrap()
                .len(),
            2
        );
    }

    #[test]
    fn quiet_topology_does_not_batch_and_zero_limit_fails_closed() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let lanes = [
            lane(1, 1, true),
            lane(2, 2, true),
            lane(3, 1, true),
            lane(4, 2, true),
            lane(5, 1, false),
        ];
        let resources = ResourceUsage {
            cpu_millicores: 400,
            memory_bytes: 256 * 1024 * 1024,
        };
        assert!(controller
            .evaluate_admission_batch(&lanes, resources, ScalingPressure::default(), 4)
            .unwrap()
            .is_empty());
        assert!(controller
            .evaluate_admission_batch(&lanes, resources, ScalingPressure::default(), 0)
            .is_err());
    }

    #[test]
    fn sustained_quiet_batches_drains_without_crossing_topology_floors() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let mut lanes = [
            lane(1, 1, true),
            lane(2, 2, true),
            lane(3, 1, true),
            lane(4, 2, true),
            lane(5, 1, true),
            lane(6, 2, true),
            lane(7, 1, true),
            lane(8, 2, true),
        ];
        for lane in &mut lanes[2..] {
            lane.marginal_goodput_bps = 1;
        }
        let resources = ResourceUsage {
            cpu_millicores: 800,
            memory_bytes: 512 * 1024 * 1024,
        };
        let actions = controller
            .evaluate_marginal_drain_batch(&lanes, resources, ScalingPressure::default(), 8)
            .unwrap();
        assert_eq!(
            actions,
            [3, 4, 5, 6]
                .into_iter()
                .map(|lane_id| ScalingAction::Drain {
                    lane_id: LaneId::new(lane_id).unwrap(),
                    reason: ScalingReason::MarginalGoodput,
                })
                .collect::<Vec<_>>()
        );
        assert!(controller
            .evaluate_marginal_drain_batch(&lanes, resources, ScalingPressure::default(), 0,)
            .is_err());
    }

    #[test]
    fn resource_pressure_drains_low_value_without_touching_protection_or_diversity() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let mut lanes = [
            lane(1, 1, true),
            lane(2, 2, true),
            lane(3, 1, true),
            lane(4, 2, true),
            lane(5, 1, true),
        ];
        lanes[2].marginal_goodput_bps = 90_000;
        lanes[3].marginal_goodput_bps = 80_000;
        lanes[4].marginal_goodput_bps = 10_000;
        let action = controller
            .evaluate(
                &lanes,
                ResourceUsage {
                    cpu_millicores: 1_100,
                    memory_bytes: 320 * 1024 * 1024,
                },
            )
            .unwrap();
        assert_eq!(
            action,
            ScalingAction::Drain {
                lane_id: LaneId::new(5).unwrap(),
                reason: ScalingReason::ResourcePressure,
            }
        );
    }

    #[test]
    fn unhealthy_lane_is_replaced_within_its_provider_and_budget() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let mut lanes = [
            lane(1, 1, true),
            lane(2, 2, true),
            lane(3, 1, true),
            lane(4, 2, true),
            lane(5, 1, false),
        ];
        lanes[2].healthy = false;
        let action = controller
            .evaluate(
                &lanes,
                ResourceUsage {
                    cpu_millicores: 400,
                    memory_bytes: 256 * 1024 * 1024,
                },
            )
            .unwrap();
        assert_eq!(
            action,
            ScalingAction::Replace {
                remove: LaneId::new(3).unwrap(),
                admit: LaneId::new(5).unwrap(),
                reason: ScalingReason::Unhealthy,
            }
        );
    }

    #[test]
    fn unhealthy_required_lane_adds_redundancy_without_draining_the_anchor() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let mut lanes = [
            lane(1, 1, true),
            lane(2, 2, true),
            lane(3, 1, true),
            lane(4, 2, true),
            lane(5, 1, false),
        ];
        lanes[0].healthy = false;
        assert_eq!(
            controller
                .evaluate(
                    &lanes,
                    ResourceUsage {
                        cpu_millicores: 400,
                        memory_bytes: 256 * 1024 * 1024,
                    },
                )
                .unwrap(),
            ScalingAction::Admit {
                lane_id: LaneId::new(5).unwrap(),
                reason: ScalingReason::Unhealthy,
            }
        );
    }

    #[test]
    fn materially_better_candidate_replaces_weak_lane_without_changing_provider() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let mut lanes = [
            lane(1, 1, true),
            lane(2, 2, true),
            lane(3, 1, true),
            lane(4, 2, true),
            lane(5, 1, false),
        ];
        lanes[2].marginal_goodput_bps = 100_000;
        lanes[4].expected_goodput_bps = 200_000;
        lanes[0].queue_delay = Duration::from_millis(10);
        let action = controller
            .evaluate(
                &lanes,
                ResourceUsage {
                    cpu_millicores: 400,
                    memory_bytes: 256 * 1024 * 1024,
                },
            )
            .unwrap();
        assert_eq!(
            action,
            ScalingAction::Replace {
                remove: LaneId::new(3).unwrap(),
                admit: LaneId::new(5).unwrap(),
                reason: ScalingReason::BetterCandidate,
            }
        );
    }

    #[test]
    fn idle_low_marginal_lane_drains_but_minimum_topology_holds() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let mut lanes = [
            lane(1, 1, true),
            lane(2, 2, true),
            lane(3, 1, true),
            lane(4, 2, true),
            lane(5, 1, true),
        ];
        lanes[4].marginal_goodput_bps = 1;
        assert_eq!(
            controller
                .evaluate(
                    &lanes,
                    ResourceUsage {
                        cpu_millicores: 500,
                        memory_bytes: 320 * 1024 * 1024,
                    },
                )
                .unwrap(),
            ScalingAction::Drain {
                lane_id: LaneId::new(5).unwrap(),
                reason: ScalingReason::MarginalGoodput,
            }
        );
        lanes[4].admitted = false;
        assert_eq!(
            controller
                .evaluate(
                    &lanes,
                    ResourceUsage {
                        cpu_millicores: 400,
                        memory_bytes: 256 * 1024 * 1024,
                    },
                )
                .unwrap(),
            ScalingAction::Hold
        );
    }

    #[test]
    fn newly_active_lane_gets_observation_dwell_before_marginal_drain() {
        let controller = AdaptiveScalingController::new(config()).unwrap();
        let mut lanes = [
            lane(1, 1, true),
            lane(2, 2, true),
            lane(3, 1, true),
            lane(4, 2, true),
            lane(5, 1, true),
        ];
        lanes[4].marginal_goodput_bps = 1;
        lanes[4].drain_eligible = false;
        let resources = ResourceUsage {
            cpu_millicores: 500,
            memory_bytes: 320 * 1024 * 1024,
        };
        assert_eq!(
            controller.evaluate(&lanes, resources).unwrap(),
            ScalingAction::Hold
        );
        lanes[4].drain_eligible = true;
        assert!(matches!(
            controller.evaluate(&lanes, resources).unwrap(),
            ScalingAction::Drain {
                lane_id,
                reason: ScalingReason::MarginalGoodput,
            } if lane_id == LaneId::new(5).unwrap()
        ));
    }
}
