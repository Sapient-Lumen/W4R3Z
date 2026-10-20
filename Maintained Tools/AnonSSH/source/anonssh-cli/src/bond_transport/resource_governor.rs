use std::collections::{BTreeMap, BTreeSet};
use std::sync::{Arc, Mutex};
use std::time::Duration;

use anonssh_bond::{LaneId, ScalingAction};
use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};

use super::{estimated_router_cost, Provider};
use crate::product_config::ScalingPolicy;
use crate::router_pool::RouterProvider;

const SNAPSHOT_SCHEMA: &str = "anonssh.resource-governor.v2";

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub(crate) struct ResourceGovernorSnapshot {
    pub schema: String,
    pub sessions: usize,
    pub physical_slots: usize,
    pub tor_slots: usize,
    pub i2p_slots: usize,
    pub estimated_cpu_millicores: u32,
    pub estimated_memory_bytes: u64,
    pub measured_physical_slots: usize,
    pub aggregate_delivered_goodput_bps: u64,
    pub denied_optional_admissions: u64,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(super) struct PhysicalPathObservation {
    pub provider: Provider,
    pub measured_resources: Option<(u32, u64)>,
    pub delivered_goodput_bps: u64,
    pub expected_goodput_bps: u64,
    pub queue_delay: Duration,
    pub startup_latency: Duration,
}

#[derive(Clone)]
struct SessionClaim {
    required: BTreeSet<Provider>,
    desired: BTreeSet<Provider>,
    candidates: BTreeSet<Provider>,
}

#[derive(Default)]
struct GovernorState {
    sessions: BTreeMap<u64, SessionClaim>,
    observations: BTreeMap<(u64, Provider), PhysicalPathObservation>,
    denied_optional_admissions: u64,
}

pub(crate) struct SharedResourceGovernor {
    policy: ScalingPolicy,
    state: Mutex<GovernorState>,
}

pub(super) struct ActionReservation {
    governor: Arc<SharedResourceGovernor>,
    session_id: u64,
    previous: BTreeSet<Provider>,
    desired: BTreeSet<Provider>,
    actions: Vec<ScalingAction>,
    committed: bool,
}

pub(super) struct SessionResourceClaim {
    governor: Arc<SharedResourceGovernor>,
    session_id: u64,
}

impl SharedResourceGovernor {
    pub(crate) fn new(policy: ScalingPolicy) -> Self {
        Self {
            policy,
            state: Mutex::new(GovernorState::default()),
        }
    }

    #[cfg(test)]
    pub(super) fn register(&self, session_id: u64, required: BTreeSet<Provider>) -> Result<()> {
        self.register_candidates(session_id, required.clone(), required)
    }

    pub(super) fn register_candidates(
        &self,
        session_id: u64,
        required: BTreeSet<Provider>,
        candidates: BTreeSet<Provider>,
    ) -> Result<()> {
        if session_id == 0 {
            bail!("resource governor session ID must be non-zero")
        }
        if !required.is_subset(&candidates) {
            bail!("resource governor candidates omit a required physical router slot")
        }
        let mut state = self.lock()?;
        if state.sessions.contains_key(&session_id) {
            bail!("resource governor session {session_id} is already registered")
        }
        let claim = SessionClaim {
            required: required.clone(),
            desired: required,
            candidates,
        };
        state.sessions.insert(session_id, claim);
        if !self.fits(&state) {
            state.sessions.remove(&session_id);
            bail!("required session baseline exceeds the shared resource policy")
        }
        Ok(())
    }

    pub(super) fn claim(
        self: &Arc<Self>,
        session_id: u64,
        required: BTreeSet<Provider>,
        candidates: BTreeSet<Provider>,
    ) -> Result<SessionResourceClaim> {
        self.register_candidates(session_id, required, candidates)?;
        Ok(SessionResourceClaim {
            governor: self.clone(),
            session_id,
        })
    }

    pub(super) fn unregister(&self, session_id: u64) -> Result<BTreeSet<Provider>> {
        let mut state = self.lock()?;
        let before = demanded_slots(&state);
        state.sessions.remove(&session_id);
        state
            .observations
            .retain(|(observed_session, _), _| *observed_session != session_id);
        let after = demanded_slots(&state);
        Ok(before.difference(&after).copied().collect())
    }

    pub(super) fn report_observations(
        &self,
        session_id: u64,
        observations: &[PhysicalPathObservation],
    ) -> Result<()> {
        let mut state = self.lock()?;
        let candidates = state
            .sessions
            .get(&session_id)
            .with_context(|| format!("resource governor omitted session {session_id}"))?
            .candidates
            .clone();
        let mut providers = BTreeSet::new();
        for observation in observations {
            if !candidates.contains(&observation.provider) {
                bail!("resource observation names an undeclared physical router slot")
            }
            if !providers.insert(observation.provider) {
                bail!("resource observation duplicates a physical router slot")
            }
            if observation.startup_latency.is_zero()
                || observation
                    .measured_resources
                    .is_some_and(|(cpu, memory)| cpu == 0 || memory == 0)
            {
                bail!("resource observation contains an invalid measurement")
            }
        }
        state
            .observations
            .retain(|(observed_session, _), _| *observed_session != session_id);
        state.observations.extend(
            observations
                .iter()
                .copied()
                .map(|observation| ((session_id, observation.provider), observation)),
        );
        Ok(())
    }

    pub(super) fn contains_session(&self, session_id: u64) -> Result<bool> {
        Ok(self.lock()?.sessions.contains_key(&session_id))
    }

    pub(super) fn try_set(
        &self,
        session_id: u64,
        provider: Provider,
        desired: bool,
    ) -> Result<bool> {
        let mut state = self.lock()?;
        let previous = state
            .sessions
            .get(&session_id)
            .with_context(|| format!("resource governor omitted session {session_id}"))?
            .desired
            .clone();
        let claim = state
            .sessions
            .get_mut(&session_id)
            .expect("checked resource governor session");
        if !claim.candidates.contains(&provider) {
            bail!("resource governor update names an undeclared physical router slot")
        }
        if !desired && claim.required.contains(&provider) {
            bail!("cannot release a required physical router slot")
        }
        if desired {
            claim.desired.insert(provider);
        } else {
            claim.desired.remove(&provider);
        }
        if self.fits(&state) {
            return Ok(true);
        }
        state
            .sessions
            .get_mut(&session_id)
            .expect("checked resource governor session")
            .desired = previous;
        state.denied_optional_admissions = state.denied_optional_admissions.saturating_add(1);
        Ok(false)
    }

    pub(super) fn reserve_actions(
        self: &Arc<Self>,
        session_id: u64,
        providers: &BTreeMap<LaneId, Provider>,
        actions: &[ScalingAction],
    ) -> Result<ActionReservation> {
        let mut state = self.lock()?;
        let previous = state
            .sessions
            .get(&session_id)
            .with_context(|| format!("resource governor omitted session {session_id}"))?
            .desired
            .clone();
        let mut desired = previous.clone();
        let required = state
            .sessions
            .get(&session_id)
            .expect("checked resource governor session")
            .required
            .clone();
        let mut accepted = Vec::with_capacity(actions.len());
        let mut denied = 0_u64;
        let mut ordered_actions = actions.to_vec();
        ordered_actions.sort_by_key(|action| action_priority(&state, providers, *action));
        for action in &ordered_actions {
            let mut candidate = desired.clone();
            match *action {
                ScalingAction::Hold => continue,
                ScalingAction::Admit { lane_id, .. } => {
                    let provider = provider_for(providers, lane_id)?;
                    if !state
                        .sessions
                        .get(&session_id)
                        .expect("checked resource governor session")
                        .candidates
                        .contains(&provider)
                    {
                        bail!("adaptive action names an undeclared physical router slot")
                    }
                    candidate.insert(provider);
                }
                ScalingAction::Drain { lane_id, .. } => {
                    let provider = provider_for(providers, lane_id)?;
                    if required.contains(&provider) {
                        bail!("adaptive action attempted to drain a required router slot")
                    }
                    candidate.remove(&provider);
                }
                ScalingAction::Replace { remove, admit, .. } => {
                    let removed = provider_for(providers, remove)?;
                    if required.contains(&removed) {
                        bail!("adaptive action attempted to replace a required router slot")
                    }
                    candidate.remove(&removed);
                    let admitted = provider_for(providers, admit)?;
                    if !state
                        .sessions
                        .get(&session_id)
                        .expect("checked resource governor session")
                        .candidates
                        .contains(&admitted)
                    {
                        bail!("adaptive action names an undeclared physical router slot")
                    }
                    candidate.insert(admitted);
                }
            }
            if self.fits_with_desired(&state, session_id, &candidate) {
                desired = candidate;
                accepted.push(*action);
            } else {
                denied = denied.saturating_add(1);
            }
        }
        state
            .sessions
            .get_mut(&session_id)
            .expect("checked resource governor session")
            .desired = desired.clone();
        state.denied_optional_admissions = state.denied_optional_admissions.saturating_add(denied);
        Ok(ActionReservation {
            governor: self.clone(),
            session_id,
            previous,
            desired,
            actions: accepted,
            committed: false,
        })
    }

    pub(super) fn replace_desired(
        &self,
        session_id: u64,
        desired: BTreeSet<Provider>,
    ) -> Result<()> {
        let mut state = self.lock()?;
        let claim = state
            .sessions
            .get(&session_id)
            .with_context(|| format!("resource governor omitted session {session_id}"))?;
        if !claim.required.is_subset(&desired) {
            bail!("resource governor update omitted required physical slots")
        }
        if !desired.is_subset(&claim.candidates) {
            bail!("resource governor update names an undeclared physical router slot")
        }
        let previous = claim.desired.clone();
        state
            .sessions
            .get_mut(&session_id)
            .expect("checked resource governor session")
            .desired = desired;
        if !self.fits(&state) {
            state
                .sessions
                .get_mut(&session_id)
                .expect("checked resource governor session")
                .desired = previous;
            bail!("requested physical topology exceeds the shared resource policy")
        }
        Ok(())
    }

    pub(super) fn is_demanded(&self, provider: Provider) -> Result<bool> {
        Ok(self
            .lock()?
            .sessions
            .values()
            .any(|claim| claim.desired.contains(&provider)))
    }

    pub(crate) fn snapshot(&self) -> Result<ResourceGovernorSnapshot> {
        let state = self.lock()?;
        let slots = demanded_slots(&state);
        let (estimated_cpu_millicores, estimated_memory_bytes) = resource_cost(&state, &slots);
        Ok(ResourceGovernorSnapshot {
            schema: SNAPSHOT_SCHEMA.to_owned(),
            sessions: state.sessions.len(),
            physical_slots: slots.len(),
            tor_slots: slots
                .iter()
                .filter(|provider| matches!(provider, Provider::Tor { .. }))
                .count(),
            i2p_slots: slots
                .iter()
                .filter(|provider| matches!(provider, Provider::I2p { .. }))
                .count(),
            estimated_cpu_millicores,
            estimated_memory_bytes,
            measured_physical_slots: slots
                .iter()
                .filter(|provider| measured_cost(&state, **provider).is_some())
                .count(),
            aggregate_delivered_goodput_bps: aggregate_delivered_goodput(&state, &slots),
            denied_optional_admissions: state.denied_optional_admissions,
        })
    }

    pub(crate) fn demanded_provider_slots(&self) -> Result<(usize, usize)> {
        let state = self.lock()?;
        let slots = demanded_slots(&state);
        Ok((
            slots
                .iter()
                .filter(|provider| matches!(provider, Provider::Tor { .. }))
                .count(),
            slots
                .iter()
                .filter(|provider| matches!(provider, Provider::I2p { .. }))
                .count(),
        ))
    }

    pub(crate) fn physical_slot_demanded(
        &self,
        provider: RouterProvider,
        slot: u32,
    ) -> Result<bool> {
        let provider = match provider {
            RouterProvider::Tor => Provider::Tor { slot },
            RouterProvider::I2p => Provider::I2p { slot },
        };
        self.is_demanded(provider)
    }

    fn fits(&self, state: &GovernorState) -> bool {
        let slots = demanded_slots(state);
        self.slots_fit_locked(state, &slots)
    }

    fn fits_with_desired(
        &self,
        state: &GovernorState,
        session_id: u64,
        desired: &BTreeSet<Provider>,
    ) -> bool {
        let mut slots = BTreeSet::new();
        for (registered_id, claim) in &state.sessions {
            if *registered_id == session_id {
                slots.extend(desired.iter().copied());
            } else {
                slots.extend(claim.desired.iter().copied());
            }
        }
        self.slots_fit_locked(state, &slots)
    }

    fn slots_fit_locked(&self, state: &GovernorState, slots: &BTreeSet<Provider>) -> bool {
        let (cpu, memory) = resource_cost(state, slots);
        slots.len() <= self.policy.maximum_active_lanes
            && cpu <= self.policy.maximum_cpu_millicores
            && memory <= self.policy.maximum_memory_bytes
    }

    fn lock(&self) -> Result<std::sync::MutexGuard<'_, GovernorState>> {
        self.state
            .lock()
            .map_err(|_| anyhow::anyhow!("shared resource governor lock was poisoned"))
    }
}

impl ActionReservation {
    pub(super) fn actions(&self) -> &[ScalingAction] {
        &self.actions
    }

    pub(super) fn contains(&self, provider: Provider) -> bool {
        self.desired.contains(&provider)
    }

    pub(super) fn commit(mut self) {
        self.committed = true;
    }
}

impl Drop for ActionReservation {
    fn drop(&mut self) {
        if self.committed {
            return;
        }
        if let Ok(mut state) = self.governor.state.lock() {
            if let Some(claim) = state.sessions.get_mut(&self.session_id) {
                if claim.desired == self.desired {
                    claim.desired = self.previous.clone();
                }
            }
        }
    }
}

impl Drop for SessionResourceClaim {
    fn drop(&mut self) {
        let _ = self.governor.unregister(self.session_id);
    }
}

fn provider_for(providers: &BTreeMap<LaneId, Provider>, lane_id: LaneId) -> Result<Provider> {
    providers
        .get(&lane_id)
        .copied()
        .with_context(|| format!("resource governor omitted lane {}", lane_id.get()))
}

fn demanded_slots(state: &GovernorState) -> BTreeSet<Provider> {
    state
        .sessions
        .values()
        .flat_map(|claim| claim.desired.iter().copied())
        .collect()
}

fn measured_cost(state: &GovernorState, provider: Provider) -> Option<(u32, u64)> {
    state
        .observations
        .values()
        .filter(|observation| observation.provider == provider)
        .filter_map(|observation| observation.measured_resources)
        .fold(None, |cost, (cpu, memory)| {
            Some(match cost {
                Some((maximum_cpu, maximum_memory)) => {
                    (maximum_cpu.max(cpu), maximum_memory.max(memory))
                }
                None => (cpu, memory),
            })
        })
}

fn provider_cost(state: &GovernorState, provider: Provider) -> (u32, u64) {
    measured_cost(state, provider).unwrap_or_else(|| {
        let (cpu, memory, _) = estimated_router_cost(provider);
        (cpu, memory)
    })
}

fn resource_cost(state: &GovernorState, slots: &BTreeSet<Provider>) -> (u32, u64) {
    slots
        .iter()
        .fold((0_u32, 0_u64), |(cpu, memory), provider| {
            let (slot_cpu, slot_memory) = provider_cost(state, *provider);
            (
                cpu.saturating_add(slot_cpu),
                memory.saturating_add(slot_memory),
            )
        })
}

fn aggregate_delivered_goodput(state: &GovernorState, slots: &BTreeSet<Provider>) -> u64 {
    state
        .observations
        .iter()
        .filter(|((session_id, provider), _)| {
            slots.contains(provider)
                && state
                    .sessions
                    .get(session_id)
                    .is_some_and(|claim| claim.desired.contains(provider))
        })
        .fold(0_u64, |goodput, (_, observation)| {
            goodput.saturating_add(observation.delivered_goodput_bps)
        })
}

fn provider_utility(state: &GovernorState, provider: Provider) -> u128 {
    let value = state
        .observations
        .values()
        .filter(|observation| observation.provider == provider)
        .fold(0_u128, |total, observation| {
            let goodput = observation
                .delivered_goodput_bps
                .max(observation.expected_goodput_bps);
            let queue_millis = observation.queue_delay.as_millis().min(900);
            total.saturating_add(
                u128::from(goodput).saturating_mul(100_u128.saturating_add(queue_millis)),
            )
        });
    let (cpu, memory) = provider_cost(state, provider);
    let cost = u128::from(cpu)
        .saturating_add(u128::from(memory / (1024 * 1024)))
        .max(1);
    value / cost
}

fn action_priority(
    state: &GovernorState,
    providers: &BTreeMap<LaneId, Provider>,
    action: ScalingAction,
) -> (u8, std::cmp::Reverse<u128>, u32) {
    match action {
        ScalingAction::Drain { lane_id, .. } => (0, std::cmp::Reverse(u128::MAX), lane_id.get()),
        ScalingAction::Replace { admit, .. } => (
            1,
            std::cmp::Reverse(
                providers
                    .get(&admit)
                    .map(|provider| provider_utility(state, *provider))
                    .unwrap_or_default(),
            ),
            admit.get(),
        ),
        ScalingAction::Admit { lane_id, .. } => (
            2,
            std::cmp::Reverse(
                providers
                    .get(&lane_id)
                    .map(|provider| provider_utility(state, *provider))
                    .unwrap_or_default(),
            ),
            lane_id.get(),
        ),
        ScalingAction::Hold => (3, std::cmp::Reverse(0), 0),
    }
}

#[cfg(test)]
mod tests {
    use std::collections::{BTreeMap, BTreeSet};
    use std::sync::Arc;
    use std::time::Duration;

    use anonssh_bond::{LaneId, ScalingAction, ScalingReason};

    use super::{PhysicalPathObservation, SharedResourceGovernor};
    use crate::bond_transport::Provider;
    use crate::product_config::{ResourceProfile, ScalingPolicy};

    fn providers() -> BTreeMap<LaneId, Provider> {
        [
            (1, Provider::Tor { slot: 1 }),
            (2, Provider::Tor { slot: 2 }),
            (3, Provider::Tor { slot: 3 }),
            (4, Provider::Tor { slot: 4 }),
            (5, Provider::Tor { slot: 5 }),
            (9, Provider::I2p { slot: 1 }),
            (10, Provider::I2p { slot: 2 }),
            (11, Provider::I2p { slot: 3 }),
            (12, Provider::I2p { slot: 4 }),
            (13, Provider::I2p { slot: 5 }),
        ]
        .into_iter()
        .map(|(lane, provider)| (LaneId::new(lane).unwrap(), provider))
        .collect()
    }

    fn mixed_baseline() -> BTreeSet<Provider> {
        [
            Provider::Tor { slot: 1 },
            Provider::Tor { slot: 2 },
            Provider::I2p { slot: 1 },
            Provider::I2p { slot: 2 },
        ]
        .into_iter()
        .collect()
    }

    fn observation(
        provider: Provider,
        cpu_millicores: u32,
        memory_mib: u64,
        goodput_bps: u64,
        queue_millis: u64,
    ) -> PhysicalPathObservation {
        PhysicalPathObservation {
            provider,
            measured_resources: Some((cpu_millicores, memory_mib * 1024 * 1024)),
            delivered_goodput_bps: goodput_bps,
            expected_goodput_bps: goodput_bps,
            queue_delay: Duration::from_millis(queue_millis),
            startup_latency: Duration::from_secs(1),
        }
    }

    #[test]
    fn required_registration_is_atomic_and_shared_slots_are_charged_once() {
        let governor = SharedResourceGovernor::new(ResourceProfile::Balanced.policy());
        governor.register(1, mixed_baseline()).unwrap();
        governor
            .register(
                2,
                [
                    Provider::Tor { slot: 1 },
                    Provider::Tor { slot: 2 },
                    Provider::Tor { slot: 3 },
                    Provider::Tor { slot: 4 },
                ]
                .into_iter()
                .collect(),
            )
            .unwrap();
        let snapshot = governor.snapshot().unwrap();
        assert_eq!(snapshot.sessions, 2);
        assert_eq!(snapshot.physical_slots, 6);
        assert_eq!(snapshot.tor_slots, 4);
        assert_eq!(snapshot.i2p_slots, 2);

        let low = SharedResourceGovernor::new(ResourceProfile::Low.policy());
        low.register(1, mixed_baseline()).unwrap();
        assert!(low
            .register(
                2,
                [
                    Provider::Tor { slot: 1 },
                    Provider::Tor { slot: 2 },
                    Provider::Tor { slot: 3 },
                    Provider::Tor { slot: 4 },
                ]
                .into_iter()
                .collect(),
            )
            .is_err());
        assert_eq!(low.snapshot().unwrap().sessions, 1);
        assert_eq!(low.snapshot().unwrap().physical_slots, 4);
    }

    #[test]
    fn disjoint_homogeneous_sessions_share_one_aggregate_budget() {
        let governor = SharedResourceGovernor::new(ResourceProfile::Balanced.policy());
        governor
            .register(
                1,
                (1..=4)
                    .map(|slot| Provider::Tor { slot })
                    .collect::<BTreeSet<_>>(),
            )
            .unwrap();
        governor
            .register(
                2,
                (1..=4)
                    .map(|slot| Provider::I2p { slot })
                    .collect::<BTreeSet<_>>(),
            )
            .unwrap();

        let snapshot = governor.snapshot().unwrap();
        assert_eq!(snapshot.sessions, 2);
        assert_eq!(snapshot.physical_slots, 8);
        assert_eq!(snapshot.tor_slots, 4);
        assert_eq!(snapshot.i2p_slots, 4);
        assert!(governor
            .register(3, [Provider::Tor { slot: 5 }].into_iter().collect())
            .is_err());
        assert_eq!(governor.snapshot().unwrap().sessions, 2);
    }

    #[test]
    fn optional_actions_are_bounded_transactional_and_final_release_is_exact() {
        let governor = Arc::new(SharedResourceGovernor::new(
            ResourceProfile::Balanced.policy(),
        ));
        let lanes = providers();
        let candidates = lanes.values().copied().collect();
        governor
            .register_candidates(1, mixed_baseline(), candidates)
            .unwrap();
        governor
            .register_candidates(2, mixed_baseline(), lanes.values().copied().collect())
            .unwrap();
        let actions = [
            ScalingAction::Admit {
                lane_id: LaneId::new(3).unwrap(),
                reason: ScalingReason::QueuePressure,
            },
            ScalingAction::Admit {
                lane_id: LaneId::new(4).unwrap(),
                reason: ScalingReason::QueuePressure,
            },
            ScalingAction::Admit {
                lane_id: LaneId::new(11).unwrap(),
                reason: ScalingReason::QueuePressure,
            },
            ScalingAction::Admit {
                lane_id: LaneId::new(12).unwrap(),
                reason: ScalingReason::QueuePressure,
            },
        ];
        {
            let reservation = governor.reserve_actions(1, &lanes, &actions).unwrap();
            assert_eq!(reservation.actions().len(), 4);
            assert_eq!(governor.snapshot().unwrap().physical_slots, 8);
        }
        assert_eq!(governor.snapshot().unwrap().physical_slots, 4);

        let reservation = governor.reserve_actions(1, &lanes, &actions).unwrap();
        reservation.commit();
        assert_eq!(governor.snapshot().unwrap().physical_slots, 8);
        for action in actions {
            let reservation = governor.reserve_actions(2, &lanes, &[action]).unwrap();
            assert_eq!(reservation.actions(), &[action]);
            reservation.commit();
        }
        assert_eq!(governor.snapshot().unwrap().physical_slots, 8);

        let denied = ScalingAction::Admit {
            lane_id: LaneId::new(5).unwrap(),
            reason: ScalingReason::QueuePressure,
        };
        let reservation = governor.reserve_actions(1, &lanes, &[denied]).unwrap();
        assert!(reservation.actions().is_empty());
        reservation.commit();
        assert_eq!(governor.snapshot().unwrap().denied_optional_admissions, 1);

        let drain = ScalingAction::Drain {
            lane_id: LaneId::new(3).unwrap(),
            reason: ScalingReason::MarginalGoodput,
        };
        let reservation = governor.reserve_actions(1, &lanes, &[drain]).unwrap();
        assert_eq!(reservation.actions(), &[drain]);
        reservation.commit();
        assert_eq!(governor.snapshot().unwrap().physical_slots, 8);

        let released = governor.unregister(2).unwrap();
        assert_eq!(released, [Provider::Tor { slot: 3 }].into_iter().collect());
        assert_eq!(governor.snapshot().unwrap().physical_slots, 7);

        let replacement = ScalingAction::Replace {
            remove: LaneId::new(4).unwrap(),
            admit: LaneId::new(5).unwrap(),
            reason: ScalingReason::BetterCandidate,
        };
        let reservation = governor.reserve_actions(1, &lanes, &[replacement]).unwrap();
        assert_eq!(reservation.actions(), &[replacement]);
        reservation.commit();
        assert!(!governor.is_demanded(Provider::Tor { slot: 4 }).unwrap());
        assert!(governor.is_demanded(Provider::Tor { slot: 5 }).unwrap());
        assert!(!governor
            .physical_slot_demanded(crate::router_pool::RouterProvider::Tor, 4)
            .unwrap());
        assert!(governor
            .physical_slot_demanded(crate::router_pool::RouterProvider::Tor, 5)
            .unwrap());
        assert_eq!(governor.demanded_provider_slots().unwrap(), (3, 4));

        let released = governor.unregister(1).unwrap();
        assert_eq!(released.len(), 7);
        assert_eq!(governor.snapshot().unwrap().physical_slots, 0);
    }

    #[test]
    fn malformed_action_batch_cannot_leak_a_partial_reservation() {
        let governor = Arc::new(SharedResourceGovernor::new(
            ResourceProfile::Balanced.policy(),
        ));
        governor
            .register_candidates(1, mixed_baseline(), providers().values().copied().collect())
            .unwrap();
        let first = ScalingAction::Admit {
            lane_id: LaneId::new(3).unwrap(),
            reason: ScalingReason::QueuePressure,
        };
        let unknown = ScalingAction::Admit {
            lane_id: LaneId::new(99).unwrap(),
            reason: ScalingReason::QueuePressure,
        };
        assert!(governor
            .reserve_actions(1, &providers(), &[first, unknown])
            .is_err());
        assert_eq!(governor.snapshot().unwrap().physical_slots, 4);
        assert_eq!(governor.snapshot().unwrap().denied_optional_admissions, 0);

        let required = ScalingAction::Drain {
            lane_id: LaneId::new(1).unwrap(),
            reason: ScalingReason::MarginalGoodput,
        };
        assert!(governor
            .reserve_actions(1, &providers(), &[first, required])
            .is_err());
        assert_eq!(governor.snapshot().unwrap().physical_slots, 4);
    }

    #[test]
    fn aggregate_memory_budget_blocks_a_cardinality_eligible_process() {
        let policy = ScalingPolicy {
            control_interval_millis: 1,
            maximum_active_lanes: 16,
            maximum_admissions_per_interval: 16,
            maximum_drains_per_interval: 16,
            maximum_cpu_millicores: u32::MAX,
            maximum_memory_bytes: 800 * 1024 * 1024,
        };
        let governor = Arc::new(SharedResourceGovernor::new(policy));
        governor
            .register_candidates(1, mixed_baseline(), providers().values().copied().collect())
            .unwrap();
        let action = ScalingAction::Admit {
            lane_id: LaneId::new(3).unwrap(),
            reason: ScalingReason::QueuePressure,
        };

        let reservation = governor
            .reserve_actions(1, &providers(), &[action])
            .unwrap();

        assert!(reservation.actions().is_empty());
        let snapshot = governor.snapshot().unwrap();
        assert_eq!(snapshot.physical_slots, 4);
        assert_eq!(snapshot.estimated_memory_bytes, 768 * 1024 * 1024);
    }

    #[test]
    fn measured_cost_can_admit_or_deny_beyond_provider_estimates() {
        let policy = ScalingPolicy {
            control_interval_millis: 1,
            maximum_active_lanes: 8,
            maximum_admissions_per_interval: 8,
            maximum_drains_per_interval: 8,
            maximum_cpu_millicores: u32::MAX,
            maximum_memory_bytes: 850 * 1024 * 1024,
        };
        let candidates = providers().values().copied().collect::<BTreeSet<_>>();
        let economical = Arc::new(SharedResourceGovernor::new(policy));
        economical
            .register_candidates(1, mixed_baseline(), candidates.clone())
            .unwrap();
        economical
            .report_observations(
                1,
                &[
                    observation(Provider::Tor { slot: 1 }, 20, 32, 1_000_000, 1),
                    observation(Provider::Tor { slot: 2 }, 20, 32, 1_000_000, 1),
                    observation(Provider::I2p { slot: 1 }, 40, 64, 1_000_000, 1),
                    observation(Provider::I2p { slot: 2 }, 40, 64, 1_000_000, 1),
                    observation(Provider::Tor { slot: 3 }, 20, 32, 1_000_000, 1),
                ],
            )
            .unwrap();
        let admit = ScalingAction::Admit {
            lane_id: LaneId::new(3).unwrap(),
            reason: ScalingReason::QueuePressure,
        };
        let reservation = economical
            .reserve_actions(1, &providers(), &[admit])
            .unwrap();
        assert_eq!(reservation.actions(), &[admit]);
        reservation.commit();
        let snapshot = economical.snapshot().unwrap();
        assert_eq!(snapshot.measured_physical_slots, 5);
        assert_eq!(snapshot.estimated_memory_bytes, 224 * 1024 * 1024);

        let expensive = Arc::new(SharedResourceGovernor::new(policy));
        expensive
            .register_candidates(1, mixed_baseline(), candidates)
            .unwrap();
        expensive
            .report_observations(
                1,
                &[
                    observation(Provider::Tor { slot: 1 }, 20, 32, 1_000_000, 1),
                    observation(Provider::Tor { slot: 2 }, 20, 32, 1_000_000, 1),
                    observation(Provider::I2p { slot: 1 }, 40, 64, 1_000_000, 1),
                    observation(Provider::I2p { slot: 2 }, 40, 64, 1_000_000, 1),
                    observation(Provider::Tor { slot: 3 }, 900, 700, 1_000_000, 1),
                ],
            )
            .unwrap();
        let reservation = expensive
            .reserve_actions(1, &providers(), &[admit])
            .unwrap();
        assert!(reservation.actions().is_empty());
    }

    #[test]
    fn aggregate_utility_ranks_admissions_independently_of_caller_order() {
        let policy = ScalingPolicy {
            control_interval_millis: 1,
            maximum_active_lanes: 5,
            maximum_admissions_per_interval: 2,
            maximum_drains_per_interval: 2,
            maximum_cpu_millicores: u32::MAX,
            maximum_memory_bytes: u64::MAX,
        };
        let governor = Arc::new(SharedResourceGovernor::new(policy));
        governor
            .register_candidates(1, mixed_baseline(), providers().values().copied().collect())
            .unwrap();
        governor
            .report_observations(
                1,
                &[
                    observation(Provider::Tor { slot: 3 }, 20, 32, 100_000, 1),
                    observation(Provider::I2p { slot: 3 }, 40, 64, 20_000_000, 100),
                ],
            )
            .unwrap();
        let lower_value_first = [
            ScalingAction::Admit {
                lane_id: LaneId::new(3).unwrap(),
                reason: ScalingReason::QueuePressure,
            },
            ScalingAction::Admit {
                lane_id: LaneId::new(11).unwrap(),
                reason: ScalingReason::QueuePressure,
            },
        ];

        let reservation = governor
            .reserve_actions(1, &providers(), &lower_value_first)
            .unwrap();
        assert_eq!(reservation.actions(), &[lower_value_first[1]]);
    }

    #[test]
    fn observations_are_bounded_to_declared_live_sessions() {
        let governor = SharedResourceGovernor::new(ResourceProfile::Balanced.policy());
        let baseline = mixed_baseline();
        governor
            .register_candidates(1, baseline.clone(), baseline.clone())
            .unwrap();
        governor
            .register_candidates(2, baseline.clone(), baseline.clone())
            .unwrap();
        let provider = Provider::Tor { slot: 1 };
        governor
            .report_observations(1, &[observation(provider, 20, 32, 10, 1)])
            .unwrap();
        governor
            .report_observations(2, &[observation(provider, 30, 64, 20, 1)])
            .unwrap();
        let snapshot = governor.snapshot().unwrap();
        assert_eq!(snapshot.aggregate_delivered_goodput_bps, 30);
        assert_eq!(snapshot.measured_physical_slots, 1);

        governor.unregister(1).unwrap();
        assert_eq!(
            governor.snapshot().unwrap().aggregate_delivered_goodput_bps,
            20
        );
        assert!(governor
            .report_observations(1, &[observation(provider, 1, 1, 1, 1)])
            .is_err());
        assert!(governor
            .report_observations(
                2,
                &[
                    observation(provider, 1, 1, 1, 1),
                    observation(provider, 1, 1, 1, 1),
                ],
            )
            .is_err());
        assert!(governor
            .report_observations(2, &[observation(Provider::Tor { slot: 99 }, 1, 1, 1, 1)],)
            .is_err());
        let mut zero_cost = observation(provider, 1, 1, 1, 1);
        zero_cost.measured_resources = Some((0, 1));
        assert!(governor.report_observations(2, &[zero_cost]).is_err());
    }
}
