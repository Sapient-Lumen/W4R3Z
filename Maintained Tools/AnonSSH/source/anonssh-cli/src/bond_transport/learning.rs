use std::collections::{BTreeMap, BTreeSet};
use std::time::Duration;

use anonssh_bond::{LaneId, LaneScalingSample, ScalingAction, ScalingConfig, ScalingReason};
use anyhow::{bail, Result};

use crate::product_config::ScalingPolicy;

const MAX_PATH_PRIORS: usize = 32;
const EWMA_OLD_WEIGHT: u64 = 3;
const EWMA_TOTAL_WEIGHT: u64 = 4;
const MINIMUM_SCALE_UP_QUEUE: Duration = Duration::from_millis(10);
const MAXIMUM_SCALE_UP_QUEUE: Duration = Duration::from_millis(250);
const MINIMUM_SCALE_DOWN_QUEUE: Duration = Duration::from_millis(1);
const MINIMUM_MARGINAL_GOODPUT_BPS: u64 = 16_000;
const MAXIMUM_MARGINAL_GOODPUT_BPS: u64 = 4_000_000;
const DEFAULT_MARGINAL_GOODPUT_BPS: u64 = 128_000;
const MINIMUM_STARTUP_CEILING: Duration = Duration::from_secs(30);
const MAXIMUM_STARTUP_CEILING: Duration = Duration::from_secs(900);
const DEFAULT_STARTUP_CEILING: Duration = Duration::from_secs(300);
const MINIMUM_PRESSURE_INTERVAL: Duration = Duration::from_millis(500);
const MAXIMUM_PRESSURE_INTERVAL: Duration = Duration::from_secs(2);
const MINIMUM_LEARNING_INTERVAL: Duration = Duration::from_secs(1);
const MINIMUM_EXPLORATION_INTERVAL: Duration = Duration::from_secs(60);
const EXPLORATION_INTERVAL_MULTIPLIER: u32 = 6;
const EXPLORATION_OBSERVATIONS: u16 = 3;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct LearnedScalingSnapshot {
    pub generation: u64,
    pub paths_with_evidence: usize,
    pub average_confidence: u16,
    pub scale_up_queue_millis: u64,
    pub scale_down_queue_millis: u64,
    pub minimum_marginal_goodput_bps: u64,
    pub replacement_gain_percent: u16,
    pub maximum_startup_millis: u64,
    pub next_control_interval_millis: u64,
    pub exploration_lane_id: Option<u32>,
}

impl Default for LearnedScalingSnapshot {
    fn default() -> Self {
        Self {
            generation: 0,
            paths_with_evidence: 0,
            average_confidence: 0,
            scale_up_queue_millis: 50,
            scale_down_queue_millis: 5,
            minimum_marginal_goodput_bps: DEFAULT_MARGINAL_GOODPUT_BPS,
            replacement_gain_percent: 50,
            maximum_startup_millis: duration_millis(DEFAULT_STARTUP_CEILING),
            next_control_interval_millis: 10_000,
            exploration_lane_id: None,
        }
    }
}

#[derive(Clone, Copy, Debug, Default)]
struct PathPrior {
    observations: u16,
    goodput_bps: u64,
    queue_micros: u64,
    startup_millis: u64,
    cpu_millicores: u32,
    memory_bytes: u64,
}

#[derive(Default)]
pub(super) struct LearnedScalingController {
    generation: u64,
    paths: BTreeMap<LaneId, PathPrior>,
    last_exploration: Option<Duration>,
    snapshot: LearnedScalingSnapshot,
}

impl LearnedScalingController {
    pub(super) fn observe(
        &mut self,
        samples: &[LaneScalingSample],
        active_lanes: &BTreeSet<LaneId>,
    ) -> Result<()> {
        if samples.is_empty() || samples.len() > MAX_PATH_PRIORS {
            bail!("learned controller received an invalid candidate count")
        }
        let declared = samples
            .iter()
            .map(|sample| sample.id)
            .collect::<BTreeSet<_>>();
        if declared.len() != samples.len() {
            bail!("learned controller received duplicate lanes")
        }
        if !active_lanes.is_subset(&declared) {
            bail!("learned controller received an undeclared active lane")
        }
        self.paths.retain(|lane_id, _| declared.contains(lane_id));
        for sample in samples {
            if !active_lanes.contains(&sample.id) || !sample.healthy {
                continue;
            }
            let prior = self.paths.entry(sample.id).or_default();
            prior.observations = prior.observations.saturating_add(1);
            let goodput = sample.marginal_goodput_bps.max(sample.expected_goodput_bps);
            prior.goodput_bps = ewma(prior.goodput_bps, goodput, prior.observations);
            prior.queue_micros = ewma(
                prior.queue_micros,
                duration_micros(sample.queue_delay),
                prior.observations,
            );
            prior.startup_millis = ewma(
                prior.startup_millis,
                duration_millis(sample.startup_latency),
                prior.observations,
            );
            prior.cpu_millicores = u32::try_from(ewma(
                u64::from(prior.cpu_millicores),
                u64::from(sample.cpu_millicores),
                prior.observations,
            ))
            .unwrap_or(u32::MAX);
            prior.memory_bytes = ewma(prior.memory_bytes, sample.memory_bytes, prior.observations);
        }
        self.generation = self.generation.saturating_add(1);
        Ok(())
    }

    pub(super) fn apply_priors(&self, samples: &mut [LaneScalingSample]) {
        for sample in samples {
            let Some(prior) = self
                .paths
                .get(&sample.id)
                .filter(|prior| prior.observations > 0)
            else {
                continue;
            };
            if !sample.admitted {
                sample.expected_goodput_bps = prior.goodput_bps;
                sample.startup_latency = Duration::from_millis(prior.startup_millis.max(1));
                sample.cpu_millicores = prior.cpu_millicores.max(1);
                sample.memory_bytes = prior.memory_bytes.max(1);
            }
        }
    }

    pub(super) fn scaling_config(
        &mut self,
        candidate_lanes: usize,
        policy: ScalingPolicy,
        pressure: bool,
    ) -> ScalingConfig {
        let queues = self
            .paths
            .values()
            .filter(|prior| prior.observations > 0)
            .map(|prior| prior.queue_micros)
            .collect::<Vec<_>>();
        let goodputs = self
            .paths
            .values()
            .filter(|prior| prior.observations > 0 && prior.goodput_bps > 0)
            .map(|prior| prior.goodput_bps)
            .collect::<Vec<_>>();
        let startups = self
            .paths
            .values()
            .filter(|prior| prior.observations > 0)
            .map(|prior| prior.startup_millis)
            .collect::<Vec<_>>();
        let confidence_sum = self.paths.values().fold(0_u64, |sum, prior| {
            sum.saturating_add(u64::from(prior.observations))
        });
        let paths_with_evidence = self
            .paths
            .values()
            .filter(|prior| prior.observations > 0)
            .count();
        let average_confidence = if paths_with_evidence == 0 {
            0
        } else {
            u16::try_from(confidence_sum / paths_with_evidence as u64).unwrap_or(u16::MAX)
        };

        let scale_up_queue = percentile_duration_micros(&queues, 75)
            .map(|duration| duration.saturating_mul(2))
            .unwrap_or(Duration::from_millis(50))
            .clamp(MINIMUM_SCALE_UP_QUEUE, MAXIMUM_SCALE_UP_QUEUE);
        let scale_down_queue = percentile_duration_micros(&queues, 25)
            .map(|duration| duration / 2)
            .unwrap_or(Duration::from_millis(5))
            .clamp(
                MINIMUM_SCALE_DOWN_QUEUE,
                scale_up_queue.saturating_sub(Duration::from_millis(1)),
            );
        let minimum_marginal_goodput_bps = percentile(&goodputs, 50)
            .map(|goodput| goodput / 8)
            .unwrap_or(DEFAULT_MARGINAL_GOODPUT_BPS)
            .clamp(MINIMUM_MARGINAL_GOODPUT_BPS, MAXIMUM_MARGINAL_GOODPUT_BPS);
        let replacement_gain_percent = 50_u16
            .saturating_sub(average_confidence.min(8).saturating_mul(5))
            .max(10);
        let maximum_startup_latency = percentile(&startups, 90)
            .map(|millis| Duration::from_millis(millis).saturating_mul(2))
            .unwrap_or(DEFAULT_STARTUP_CEILING)
            .clamp(MINIMUM_STARTUP_CEILING, MAXIMUM_STARTUP_CEILING);
        let next_interval = control_interval(policy, pressure, average_confidence);
        self.snapshot = LearnedScalingSnapshot {
            generation: self.generation,
            paths_with_evidence,
            average_confidence,
            scale_up_queue_millis: duration_millis(scale_up_queue),
            scale_down_queue_millis: duration_millis(scale_down_queue),
            minimum_marginal_goodput_bps,
            replacement_gain_percent,
            maximum_startup_millis: duration_millis(maximum_startup_latency),
            next_control_interval_millis: duration_millis(next_interval),
            exploration_lane_id: None,
        };

        let minimum_active_lanes = candidate_lanes.min(4);
        ScalingConfig {
            minimum_active_lanes,
            maximum_active_lanes: policy
                .maximum_active_lanes
                .min(candidate_lanes)
                .max(minimum_active_lanes),
            minimum_lanes_per_provider: 1,
            scale_up_queue_delay: scale_up_queue,
            scale_down_queue_delay: scale_down_queue,
            scale_up_send_window_percent: 1,
            scale_down_send_window_percent: 0,
            minimum_marginal_goodput_bps,
            replacement_gain_percent,
            maximum_startup_latency,
            maximum_cpu_millicores: policy.maximum_cpu_millicores,
            maximum_memory_bytes: policy.maximum_memory_bytes,
        }
    }

    pub(super) fn exploration_action(
        &mut self,
        samples: &[LaneScalingSample],
        now: Duration,
        policy: ScalingPolicy,
    ) -> Option<ScalingAction> {
        let active = samples.iter().filter(|sample| sample.admitted).count();
        if active >= policy.maximum_active_lanes.min(samples.len()) {
            return None;
        }
        if samples.iter().any(|sample| {
            sample.admitted
                && !sample.required
                && self
                    .paths
                    .get(&sample.id)
                    .map(|prior| prior.observations)
                    .unwrap_or(0)
                    < EXPLORATION_OBSERVATIONS
        }) {
            return None;
        }
        let interval = policy
            .control_interval()
            .saturating_mul(EXPLORATION_INTERVAL_MULTIPLIER)
            .max(MINIMUM_EXPLORATION_INTERVAL);
        match self.last_exploration {
            Some(last) if now.saturating_sub(last) < interval => return None,
            None if now < interval => return None,
            _ => {}
        }
        let candidate = samples
            .iter()
            .filter(|sample| !sample.admitted && sample.healthy)
            .min_by_key(|sample| {
                let prior = self.paths.get(&sample.id).copied().unwrap_or_default();
                (
                    prior.observations,
                    std::cmp::Reverse(path_utility(sample)),
                    sample.id,
                )
            })?;
        self.last_exploration = Some(now);
        self.snapshot.exploration_lane_id = Some(candidate.id.get());
        Some(ScalingAction::Admit {
            lane_id: candidate.id,
            reason: ScalingReason::Exploration,
        })
    }

    pub(super) const fn snapshot(&self) -> LearnedScalingSnapshot {
        self.snapshot
    }
}

fn control_interval(policy: ScalingPolicy, pressure: bool, confidence: u16) -> Duration {
    let base = policy.control_interval();
    if pressure {
        return (base / 5).clamp(MINIMUM_PRESSURE_INTERVAL, MAXIMUM_PRESSURE_INTERVAL);
    }
    if confidence < 2 {
        return (base / 2).max(MINIMUM_LEARNING_INTERVAL);
    }
    base
}

fn path_utility(sample: &LaneScalingSample) -> u128 {
    let goodput = sample.expected_goodput_bps.max(sample.marginal_goodput_bps);
    let resource_cost = u128::from(sample.cpu_millicores)
        .saturating_add(u128::from(sample.memory_bytes / (1024 * 1024)))
        .max(1);
    u128::from(goodput).saturating_mul(1_000_000) / resource_cost
}

fn ewma(current: u64, sample: u64, observations: u16) -> u64 {
    if observations <= 1 {
        sample
    } else {
        current
            .saturating_mul(EWMA_OLD_WEIGHT)
            .saturating_add(sample)
            / EWMA_TOTAL_WEIGHT
    }
}

fn percentile(values: &[u64], percent: usize) -> Option<u64> {
    let mut values = values.to_vec();
    values.sort_unstable();
    let index = values.len().saturating_sub(1).saturating_mul(percent) / 100;
    values.get(index).copied()
}

fn percentile_duration_micros(values: &[u64], percent: usize) -> Option<Duration> {
    percentile(values, percent).map(Duration::from_micros)
}

fn duration_millis(duration: Duration) -> u64 {
    u64::try_from(duration.as_millis()).unwrap_or(u64::MAX)
}

fn duration_micros(duration: Duration) -> u64 {
    u64::try_from(duration.as_micros()).unwrap_or(u64::MAX)
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeSet;
    use std::time::Duration;

    use anonssh_bond::{
        FailureDomain, LaneId, LaneScalingSample, ProviderId, ScalingAction, ScalingReason,
    };

    use super::{LearnedScalingController, MAX_PATH_PRIORS};
    use crate::product_config::ResourceProfile;

    fn sample(id: u32, admitted: bool, goodput: u64, queue_millis: u64) -> LaneScalingSample {
        LaneScalingSample {
            id: LaneId::new(id).unwrap(),
            failure_domain: FailureDomain::new(u64::from(id)).unwrap(),
            provider: ProviderId::new(if id <= 16 { 1 } else { 2 }).unwrap(),
            admitted,
            healthy: true,
            required: id <= 4,
            protected_for_low_latency: id <= 2,
            drain_eligible: true,
            queue_delay: Duration::from_millis(queue_millis),
            marginal_goodput_bps: goodput,
            expected_goodput_bps: goodput,
            startup_latency: Duration::from_secs(u64::from(id)),
            cpu_millicores: 10_u32.saturating_mul(id),
            memory_bytes: 16 * 1024 * 1024 * u64::from(id),
        }
    }

    #[test]
    fn learned_thresholds_and_pressure_cadence_follow_observations() {
        let mut learner = LearnedScalingController::default();
        let samples = vec![
            sample(1, true, 8_000_000, 4),
            sample(2, true, 4_000_000, 8),
            sample(17, true, 2_000_000, 16),
            sample(18, true, 1_000_000, 32),
        ];
        let active = samples.iter().map(|sample| sample.id).collect();
        for _ in 0..8 {
            learner.observe(&samples, &active).unwrap();
        }
        let policy = ResourceProfile::Performance.policy();
        let quiet = learner.scaling_config(32, policy, false);
        let quiet_snapshot = learner.snapshot();
        assert_eq!(quiet.maximum_active_lanes, 16);
        assert_eq!(quiet.scale_up_queue_delay, Duration::from_millis(32));
        assert_eq!(quiet.scale_down_queue_delay, Duration::from_millis(2));
        assert_eq!(quiet.minimum_marginal_goodput_bps, 250_000);
        assert_eq!(quiet.replacement_gain_percent, 10);
        assert_eq!(quiet.maximum_startup_latency, Duration::from_secs(34));
        assert_eq!(quiet_snapshot.paths_with_evidence, 4);
        assert_eq!(quiet_snapshot.next_control_interval_millis, 10_000);

        learner.scaling_config(32, policy, true);
        assert_eq!(learner.snapshot().next_control_interval_millis, 2_000);
    }

    #[test]
    fn no_evidence_uses_conservative_bounds_without_targeting_the_ceiling() {
        let mut learner = LearnedScalingController::default();
        let policy = ResourceProfile::Performance.policy();
        let config = learner.scaling_config(16, policy, false);
        assert_eq!(config.minimum_active_lanes, 4);
        assert_eq!(config.maximum_active_lanes, 16);
        assert_eq!(config.scale_up_queue_delay, Duration::from_millis(50));
        assert_eq!(config.scale_down_queue_delay, Duration::from_millis(5));
        assert_eq!(config.minimum_marginal_goodput_bps, 128_000);
        assert_eq!(config.replacement_gain_percent, 50);
        assert_eq!(config.maximum_startup_latency, Duration::from_secs(300));
        assert_eq!(learner.snapshot().next_control_interval_millis, 5_000);
    }

    #[test]
    fn priors_are_bounded_and_reused_for_inactive_candidates() {
        let mut learner = LearnedScalingController::default();
        let mut samples = (1..=u32::try_from(MAX_PATH_PRIORS).unwrap())
            .map(|id| sample(id, true, u64::from(id) * 1_000_000, 1))
            .collect::<Vec<_>>();
        let active = samples.iter().map(|sample| sample.id).collect();
        learner.observe(&samples, &active).unwrap();
        samples[31].admitted = false;
        samples[31].expected_goodput_bps = 1;
        samples[31].cpu_millicores = 1;
        learner.apply_priors(&mut samples);
        assert_eq!(samples[31].expected_goodput_bps, 32_000_000);
        assert_eq!(samples[31].cpu_millicores, 320);

        let mut oversized = samples.clone();
        let mut extra = sample(32, false, 1, 1);
        extra.id = LaneId::new(33).unwrap();
        extra.failure_domain = FailureDomain::new(33).unwrap();
        oversized.push(extra);
        assert!(learner.observe(&oversized, &BTreeSet::new()).is_err());
    }

    #[test]
    fn exploration_is_periodic_singular_and_respects_the_active_ceiling() {
        let mut learner = LearnedScalingController::default();
        let policy = ResourceProfile::Performance.policy();
        let samples = vec![
            sample(1, true, 1_000_000, 1),
            sample(2, true, 1_000_000, 1),
            sample(3, true, 1_000_000, 1),
            sample(4, true, 1_000_000, 1),
            sample(5, false, 8_000_000, 1),
            sample(6, false, 2_000_000, 1),
        ];
        let active = samples[..4].iter().map(|sample| sample.id).collect();
        for _ in 0..3 {
            learner.observe(&samples, &active).unwrap();
        }
        assert!(learner
            .exploration_action(&samples, Duration::from_secs(59), policy)
            .is_none());
        assert_eq!(
            learner.exploration_action(&samples, Duration::from_secs(60), policy),
            Some(ScalingAction::Admit {
                lane_id: LaneId::new(5).unwrap(),
                reason: ScalingReason::Exploration,
            })
        );
        assert!(learner
            .exploration_action(&samples, Duration::from_secs(61), policy)
            .is_none());

        let mut maximum = (1..=16)
            .map(|id| sample(id, true, 1_000_000, 1))
            .collect::<Vec<_>>();
        maximum.push(sample(17, false, 10_000_000, 1));
        assert!(learner
            .exploration_action(&maximum, Duration::from_secs(600), policy)
            .is_none());
    }
}
