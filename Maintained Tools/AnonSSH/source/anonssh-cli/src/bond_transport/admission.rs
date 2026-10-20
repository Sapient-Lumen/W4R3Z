use std::collections::{BTreeMap, BTreeSet};
use std::sync::Arc;

use anonssh_bond::LaneId;
use anonssh_bond_tokio::{
    AuthenticatedLane, BondSession, BondSessionControl, BondSessionKey, LaneJoin,
    PreparedServerLane, RuntimeLane, ServerIncarnation, SessionRole,
};
use anyhow::{bail, Context, Result};
use tokio::net::TcpStream;
use tokio::sync::mpsc;
use tokio::task::JoinSet;
use tokio::time::Instant;
use tracing::warn;

use super::{
    discovery_lanes, runtime_config, PlannedLane, INITIAL_LANE_DEADLINE, MAX_ACTIVE_SESSIONS,
    MAX_INFLIGHT_ADMISSION_COMPLETIONS, MAX_LEGACY_SESSION_JOIN_NONCES, MAX_PENDING_SESSIONS,
    POOL_HEALTH_INTERVAL, SESSION_JOIN_REPLAY_WINDOW_BITS,
};

const JOIN_REPLAY_WINDOW_WORDS: usize = SESSION_JOIN_REPLAY_WINDOW_BITS / u64::BITS as usize;

pub(super) struct PreparedIngressLane {
    pub(super) planned: PlannedLane,
    pub(super) prepared: PreparedServerLane<TcpStream>,
    #[cfg(test)]
    completion_gate: Option<Arc<tokio::sync::Notify>>,
}

impl PreparedIngressLane {
    pub(super) fn new(planned: PlannedLane, prepared: PreparedServerLane<TcpStream>) -> Self {
        Self {
            planned,
            prepared,
            #[cfg(test)]
            completion_gate: None,
        }
    }

    #[cfg(test)]
    pub(super) fn with_completion_gate(mut self, gate: Arc<tokio::sync::Notify>) -> Self {
        self.completion_gate = Some(gate);
        self
    }

    async fn finish(
        self,
        key: &BondSessionKey,
        incarnation: ServerIncarnation,
    ) -> Result<AuthenticatedLane<TcpStream>> {
        #[cfg(test)]
        if let Some(gate) = &self.completion_gate {
            gate.notified().await;
        }
        Ok(self
            .prepared
            .finish_with_versions_and_incarnation(
                key,
                anonssh_bond_tokio::BondProtocolVersions::CURRENT,
                incarnation,
                super::HANDSHAKE_TIMEOUT,
            )
            .await?)
    }
}

struct PendingAdmission {
    started: Instant,
    lanes: BTreeMap<LaneId, RuntimeLane>,
    attempts: BTreeMap<LaneId, u64>,
    replay: JoinReplayLedger,
}

struct ActiveAdmission {
    control: BondSessionControl,
    attempts: BTreeMap<LaneId, u64>,
    replay: JoinReplayLedger,
}

#[derive(Default)]
struct JoinReplayLedger {
    legacy_nonces: BTreeSet<[u8; 32]>,
    highest_sequence: Option<u64>,
    sequence_window: [u64; JOIN_REPLAY_WINDOW_WORDS],
}

impl JoinReplayLedger {
    fn reserve(&mut self, nonce: [u8; 32], join_sequence: Option<u64>, label: &str) -> Result<()> {
        if let Some(sequence) = join_sequence {
            return self.reserve_sequence(sequence, label);
        }
        if self.legacy_nonces.contains(&nonce) {
            bail!("{label} replayed a legacy client nonce");
        }
        if self.legacy_nonces.len() >= MAX_LEGACY_SESSION_JOIN_NONCES {
            bail!("{label} exhausted its bounded legacy client nonce ledger");
        }
        self.legacy_nonces.insert(nonce);
        Ok(())
    }

    fn reserve_sequence(&mut self, sequence: u64, label: &str) -> Result<()> {
        let Some(highest) = self.highest_sequence else {
            self.highest_sequence = Some(sequence);
            self.sequence_window[0] = 1;
            return Ok(());
        };
        if sequence > highest {
            self.shift_window(sequence - highest);
            self.highest_sequence = Some(sequence);
            self.sequence_window[0] |= 1;
            return Ok(());
        }

        let age = highest - sequence;
        if age >= SESSION_JOIN_REPLAY_WINDOW_BITS as u64 {
            bail!("{label} replayed a stale client join sequence");
        }
        let age = age as usize;
        let word = age / u64::BITS as usize;
        let bit = age % u64::BITS as usize;
        let mask = 1_u64 << bit;
        if self.sequence_window[word] & mask != 0 {
            bail!("{label} replayed a client join sequence");
        }
        self.sequence_window[word] |= mask;
        Ok(())
    }

    fn shift_window(&mut self, distance: u64) {
        if distance >= SESSION_JOIN_REPLAY_WINDOW_BITS as u64 {
            self.sequence_window.fill(0);
            return;
        }
        let distance = distance as usize;
        let word_shift = distance / u64::BITS as usize;
        let bit_shift = distance % u64::BITS as usize;
        let mut shifted = [0_u64; JOIN_REPLAY_WINDOW_WORDS];
        for (source, value) in self.sequence_window.iter().copied().enumerate() {
            let destination = source + word_shift;
            if destination >= JOIN_REPLAY_WINDOW_WORDS {
                break;
            }
            shifted[destination] |= value << bit_shift;
            if bit_shift != 0 && destination + 1 < JOIN_REPLAY_WINDOW_WORDS {
                shifted[destination + 1] |= value >> (u64::BITS as usize - bit_shift);
            }
        }
        self.sequence_window = shifted;
    }
}

struct AdmissionCompletion {
    planned: PlannedLane,
    join: LaneJoin,
    attempt_id: u64,
    result: Result<AuthenticatedLane<TcpStream>>,
}

#[derive(Clone)]
struct AdmissionHandshake {
    key: Arc<BondSessionKey>,
    incarnation: ServerIncarnation,
}

pub(super) enum AdmissionCommand {
    Release { session_id: u64 },
}

pub(super) async fn run_admission_coordinator(
    mut candidate_rx: mpsc::Receiver<PreparedIngressLane>,
    mut command_rx: mpsc::Receiver<AdmissionCommand>,
    completed_tx: mpsc::Sender<BondSession>,
    key: Arc<BondSessionKey>,
    plan: Vec<PlannedLane>,
    incarnation: ServerIncarnation,
) {
    let handshake = AdmissionHandshake { key, incarnation };
    let mut pending = BTreeMap::new();
    let mut active = BTreeMap::new();
    let mut completions = JoinSet::new();
    let mut next_attempt_id = 1_u64;
    let mut expiry = tokio::time::interval(POOL_HEALTH_INTERVAL);
    loop {
        tokio::select! {
            candidate = candidate_rx.recv(), if completions.len() < MAX_INFLIGHT_ADMISSION_COMPLETIONS => {
                let Some(candidate) = candidate else { return; };
                if let Err(error) = queue_admission_candidate(
                    candidate,
                    handshake.clone(),
                    &plan,
                    &mut pending,
                    &mut active,
                    &mut completions,
                    &mut next_attempt_id,
                ) {
                    warn!("bond lane admission rejected: {error:#}");
                }
            }
            completed = completions.join_next(), if !completions.is_empty() => {
                match completed {
                    Some(Ok(completion)) => {
                        if let Err(error) = apply_admission_completion(
                            completion,
                            &plan,
                            &completed_tx,
                            &mut pending,
                            &mut active,
                        ).await {
                            warn!("bond lane admission rejected: {error:#}");
                        }
                    }
                    Some(Err(error)) => warn!("bond admission completion task failed: {error}"),
                    None => {}
                }
            }
            command = command_rx.recv() => {
                let Some(AdmissionCommand::Release { session_id }) = command else { return; };
                active.remove(&session_id);
                pending.remove(&session_id);
            }
            _ = expiry.tick() => {
                pending.retain(|_, admission: &mut PendingAdmission| {
                    admission.started.elapsed() < INITIAL_LANE_DEADLINE
                });
            }
        }
    }
}

fn queue_admission_candidate(
    candidate: PreparedIngressLane,
    handshake: AdmissionHandshake,
    plan: &[PlannedLane],
    pending: &mut BTreeMap<u64, PendingAdmission>,
    active: &mut BTreeMap<u64, ActiveAdmission>,
    completions: &mut JoinSet<AdmissionCompletion>,
    next_attempt_id: &mut u64,
) -> Result<()> {
    let join = candidate.prepared.join();
    let nonce = candidate.prepared.client_nonce();
    let join_sequence = candidate.prepared.client_join_sequence()?;
    if let Some(admission) = active.get_mut(&join.session_id) {
        let attempt_id = reserve_admission_attempt(
            &mut admission.replay,
            &mut admission.attempts,
            join.lane_id,
            nonce,
            join_sequence,
            next_attempt_id,
            "bond session",
        )?;
        spawn_admission_completion(completions, candidate, handshake, attempt_id);
        return Ok(());
    }
    if let Some(admission) = pending.get_mut(&join.session_id) {
        if admission.lanes.is_empty() && !admission.attempts.is_empty() {
            bail!("pending bond session is already authenticating a discovery lane");
        }
        let attempt_id = reserve_admission_attempt(
            &mut admission.replay,
            &mut admission.attempts,
            join.lane_id,
            nonce,
            join_sequence,
            next_attempt_id,
            "pending bond session",
        )?;
        spawn_admission_completion(completions, candidate, handshake, attempt_id);
        return Ok(());
    }

    authorize_new_session_lane(plan, candidate.planned)?;
    if pending.len() >= MAX_PENDING_SESSIONS {
        bail!("pending bond-session admission limit reached");
    }
    let mut admission = PendingAdmission {
        started: Instant::now(),
        lanes: BTreeMap::new(),
        attempts: BTreeMap::new(),
        replay: JoinReplayLedger::default(),
    };
    let attempt_id = reserve_admission_attempt(
        &mut admission.replay,
        &mut admission.attempts,
        join.lane_id,
        nonce,
        join_sequence,
        next_attempt_id,
        "pending bond session",
    )?;
    pending.insert(join.session_id, admission);
    spawn_admission_completion(completions, candidate, handshake, attempt_id);
    Ok(())
}

fn reserve_admission_attempt(
    replay: &mut JoinReplayLedger,
    attempts: &mut BTreeMap<LaneId, u64>,
    lane_id: LaneId,
    nonce: [u8; 32],
    join_sequence: Option<u64>,
    next_attempt_id: &mut u64,
    label: &str,
) -> Result<u64> {
    replay.reserve(nonce, join_sequence, label)?;
    let attempt_id = *next_attempt_id;
    *next_attempt_id = next_attempt_id
        .checked_add(1)
        .context("bond admission attempt ID overflow")?;
    attempts.insert(lane_id, attempt_id);
    Ok(attempt_id)
}

fn spawn_admission_completion(
    completions: &mut JoinSet<AdmissionCompletion>,
    candidate: PreparedIngressLane,
    handshake: AdmissionHandshake,
    attempt_id: u64,
) {
    let join = candidate.prepared.join();
    let planned = candidate.planned;
    completions.spawn(async move {
        let result = candidate
            .finish(&handshake.key, handshake.incarnation)
            .await;
        AdmissionCompletion {
            planned,
            join,
            attempt_id,
            result,
        }
    });
}

async fn apply_admission_completion(
    completion: AdmissionCompletion,
    plan: &[PlannedLane],
    completed_tx: &mpsc::Sender<BondSession>,
    pending: &mut BTreeMap<u64, PendingAdmission>,
    active: &mut BTreeMap<u64, ActiveAdmission>,
) -> Result<()> {
    let session_id = completion.join.session_id;
    let lane_id = completion.join.lane_id;
    if let Some(mut admission) = pending.remove(&session_id) {
        if admission.attempts.get(&lane_id) != Some(&completion.attempt_id) {
            pending.insert(session_id, admission);
            return Ok(());
        }
        admission.attempts.remove(&lane_id);
        match completion.result {
            Ok(lane) => {
                admission.lanes.insert(
                    lane_id,
                    RuntimeLane::from_authenticated(completion.planned.config, lane),
                );
            }
            Err(error) => {
                if !admission.lanes.is_empty() || !admission.attempts.is_empty() {
                    pending.insert(session_id, admission);
                }
                return Err(error.context("initial bond lane completion failed"));
            }
        }
        let discovery_lane_ids = discovery_lanes(plan)
            .into_iter()
            .map(|planned| planned.config.id)
            .collect::<BTreeSet<_>>();
        if admission
            .lanes
            .keys()
            .all(|lane_id| !discovery_lane_ids.contains(lane_id))
        {
            pending.insert(session_id, admission);
            return Ok(());
        }
        activate_pending_session(session_id, admission, plan, completed_tx, active).await?;
        return Ok(());
    }

    if let Some(mut admission) = active.remove(&session_id) {
        if admission.attempts.get(&lane_id) != Some(&completion.attempt_id) {
            active.insert(session_id, admission);
            return Ok(());
        }
        admission.attempts.remove(&lane_id);
        let result = match completion.result {
            Ok(lane) => {
                install_authenticated_lane(
                    &admission.control,
                    RuntimeLane::from_authenticated(completion.planned.config, lane),
                )
                .await
            }
            Err(error) => Err(error.context("replacement bond lane completion failed")),
        };
        active.insert(session_id, admission);
        return result;
    }

    Ok(())
}

fn authorize_new_session_lane(plan: &[PlannedLane], candidate: PlannedLane) -> Result<()> {
    if discovery_lanes(plan)
        .into_iter()
        .any(|discovery| discovery == candidate)
    {
        Ok(())
    } else {
        bail!("unknown bond session did not arrive on a topology discovery lane")
    }
}

async fn install_authenticated_lane(control: &BondSessionControl, lane: RuntimeLane) -> Result<()> {
    let lane_id = lane.config.id;
    let active = control
        .statistics()
        .await?
        .lanes
        .iter()
        .find(|snapshot| snapshot.id == lane_id)
        .context("authenticated replacement targeted an undeclared lane")?
        .active;
    if active {
        control.fail_lane(lane_id).await?;
    }
    control.add_lane(lane).await?;
    Ok(())
}

async fn activate_pending_session(
    session_id: u64,
    admission: PendingAdmission,
    plan: &[PlannedLane],
    completed_tx: &mpsc::Sender<BondSession>,
    active: &mut BTreeMap<u64, ActiveAdmission>,
) -> Result<()> {
    if active.len() >= MAX_ACTIVE_SESSIONS {
        bail!("active bond-session admission limit reached");
    }
    let active_lane_ids = admission.lanes.keys().copied().collect::<BTreeSet<_>>();
    let session = BondSession::spawn(
        runtime_config(session_id),
        admission.lanes.into_values().collect(),
        SessionRole::Listener,
    )?;
    for planned in plan {
        if !active_lane_ids.contains(&planned.config.id) {
            session.authorize_lane(planned.config).await?;
        }
    }
    let active_admission = ActiveAdmission {
        control: session.control(),
        attempts: admission.attempts,
        replay: admission.replay,
    };
    completed_tx
        .try_send(session)
        .map_err(|_| anyhow::anyhow!("completed bond-session queue is full"))?;
    active.insert(session_id, active_admission);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use anonssh_bond_tokio::authenticate_client_lane;
    use tokio::net::TcpListener;

    fn discovery_test_plan() -> Vec<PlannedLane> {
        vec![
            super::super::planned_lane(1, 1, 50, 8, super::super::Provider::Tor { slot: 1 })
                .unwrap(),
            super::super::planned_lane(2, 2, 75, 8, super::super::Provider::Tor { slot: 2 })
                .unwrap(),
            super::super::planned_lane(3, 3, 500, 4, super::super::Provider::I2p { slot: 1 })
                .unwrap(),
            super::super::planned_lane(4, 4, 500, 4, super::super::Provider::I2p { slot: 2 })
                .unwrap(),
        ]
    }

    #[test]
    fn unknown_session_accepts_only_provider_discovery_representatives() {
        let plan = discovery_test_plan();
        assert!(authorize_new_session_lane(&plan, plan[0]).is_ok());
        assert!(authorize_new_session_lane(&plan, plan[2]).is_ok());
        assert!(authorize_new_session_lane(&plan, plan[1]).is_err());
        assert!(authorize_new_session_lane(&plan, plan[3]).is_err());
    }

    #[tokio::test]
    async fn unknown_session_serializes_provider_discovery_selection() {
        let plan = discovery_test_plan();
        let key = Arc::new(BondSessionKey::new([0x44; 32]));
        let session_id = 0xd15c_0a11;
        let (first, first_client) = prepared_candidate(plan[0], session_id, key.clone()).await;
        let (second, second_client) = prepared_candidate(plan[2], session_id, key.clone()).await;
        let handshake = AdmissionHandshake {
            key,
            incarnation: ServerIncarnation::from_u64(1).unwrap(),
        };
        let mut pending = BTreeMap::new();
        let mut active = BTreeMap::new();
        let mut completions = JoinSet::new();
        let mut next_attempt_id = 1;

        queue_admission_candidate(
            first,
            handshake.clone(),
            &plan,
            &mut pending,
            &mut active,
            &mut completions,
            &mut next_attempt_id,
        )
        .unwrap();
        let error = queue_admission_candidate(
            second,
            handshake,
            &plan,
            &mut pending,
            &mut active,
            &mut completions,
            &mut next_attempt_id,
        )
        .unwrap_err();
        assert!(error
            .to_string()
            .contains("already authenticating a discovery lane"));

        completions.abort_all();
        drop(completions);
        assert!(first_client.await.unwrap().is_err());
        assert!(second_client.await.unwrap().is_err());
    }

    async fn prepared_candidate(
        planned: PlannedLane,
        session_id: u64,
        key: Arc<BondSessionKey>,
    ) -> (
        PreparedIngressLane,
        tokio::task::JoinHandle<
            std::result::Result<
                AuthenticatedLane<TcpStream>,
                anonssh_bond_tokio::LaneHandshakeError,
            >,
        >,
    ) {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let address = listener.local_addr().unwrap();
        let join =
            LaneJoin::new(session_id, planned.config.id, planned.config.failure_domain).unwrap();
        let client_key = key.clone();
        let client = tokio::spawn(async move {
            let stream = TcpStream::connect(address).await.unwrap();
            authenticate_client_lane(stream, &client_key, join, super::super::HANDSHAKE_TIMEOUT)
                .await
        });
        let (stream, _) = listener.accept().await.unwrap();
        let prepared =
            anonssh_bond_tokio::prepare_server_lane(stream, &key, super::super::HANDSHAKE_TIMEOUT)
                .await
                .unwrap();
        (PreparedIngressLane::new(planned, prepared), client)
    }

    #[test]
    fn sequenced_admission_remains_bounded_beyond_the_legacy_limit() {
        let mut replay = JoinReplayLedger::default();
        let mut attempts = BTreeMap::new();
        let mut next_attempt_id = 1;
        let lane_id = LaneId::new(1).unwrap();

        for sequence in 1..=1_024 {
            let attempt = reserve_admission_attempt(
                &mut replay,
                &mut attempts,
                lane_id,
                [0; 32],
                Some(sequence),
                &mut next_attempt_id,
                "test session",
            )
            .unwrap();
            assert_eq!(attempt, sequence);
        }

        assert_eq!(replay.highest_sequence, Some(1_024));
        assert_eq!(replay.sequence_window, [u64::MAX; JOIN_REPLAY_WINDOW_WORDS]);
        assert!(replay.legacy_nonces.is_empty());
        assert_eq!(attempts.len(), 1);
        assert_eq!(next_attempt_id, 1_025);
    }

    #[test]
    fn sequence_window_accepts_reordering_and_rejects_replay() {
        let mut replay = JoinReplayLedger::default();
        replay.reserve([0; 32], Some(300), "test session").unwrap();
        replay.reserve([0; 32], Some(298), "test session").unwrap();

        let duplicate = replay
            .reserve([1; 32], Some(298), "test session")
            .unwrap_err();
        assert!(duplicate
            .to_string()
            .contains("replayed a client join sequence"));

        let stale = replay
            .reserve([2; 32], Some(44), "test session")
            .unwrap_err();
        assert!(stale
            .to_string()
            .contains("replayed a stale client join sequence"));

        replay.reserve([3; 32], Some(301), "test session").unwrap();
        assert_eq!(replay.highest_sequence, Some(301));
        assert_eq!(replay.sequence_window[0] & 0b1011, 0b1011);
    }

    #[test]
    fn legacy_admission_keeps_its_bounded_nonce_ledger() {
        let mut replay = JoinReplayLedger::default();
        for value in 0..MAX_LEGACY_SESSION_JOIN_NONCES {
            let mut nonce = [0_u8; 32];
            nonce[24..].copy_from_slice(&(value as u64).to_be_bytes());
            replay.reserve(nonce, None, "legacy session").unwrap();
        }

        let mut nonce = [0_u8; 32];
        nonce[24..].copy_from_slice(&(MAX_LEGACY_SESSION_JOIN_NONCES as u64).to_be_bytes());
        let error = replay.reserve(nonce, None, "legacy session").unwrap_err();
        assert!(error
            .to_string()
            .contains("exhausted its bounded legacy client nonce ledger"));
    }
}
