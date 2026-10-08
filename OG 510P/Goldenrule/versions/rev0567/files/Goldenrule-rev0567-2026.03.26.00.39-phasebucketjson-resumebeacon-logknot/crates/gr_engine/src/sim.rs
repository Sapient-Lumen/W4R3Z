use crate::artifact::{MatchArtifact, MatchStats, RoundTrace, SeedStreams};
use crate::spec::{
    Action, BuiltinKind, NoiseModelSpec, Payoffs, StrategySpec, TaskSpec, TerminationRuleSpec,
};
use rand::Rng;
use rand::SeedableRng;
use rand_chacha::ChaCha8Rng;
use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum SimError {
    #[error("invalid probability {0} (expected in [0,1])")]
    InvalidProbability(f64),
    #[error("invalid termination: {0}")]
    InvalidTermination(String),
}

fn validate_probability(p: f64) -> Result<(), SimError> {
    if (0.0..=1.0).contains(&p) {
        Ok(())
    } else {
        Err(SimError::InvalidProbability(p))
    }
}

fn validate_noise(noise: &NoiseModelSpec) -> Result<(), SimError> {
    match *noise {
        NoiseModelSpec::None => Ok(()),
        NoiseModelSpec::ImplementationFlip { p } => validate_probability(p),
        NoiseModelSpec::ObservationFlip { p } => validate_probability(p),
        NoiseModelSpec::Iid {
            p_implementation,
            p_observation,
        } => {
            validate_probability(p_implementation)?;
            validate_probability(p_observation)?;
            Ok(())
        }
        NoiseModelSpec::AsymmetricIid {
            p_implementation_a,
            p_implementation_b,
            p_observation_a,
            p_observation_b,
        } => {
            validate_probability(p_implementation_a)?;
            validate_probability(p_implementation_b)?;
            validate_probability(p_observation_a)?;
            validate_probability(p_observation_b)?;
            Ok(())
        }
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
struct PlayerObs {
    last_opp_observed: Option<Action>,
    last_self_intended: Option<Action>,
    opponent_standing: f64,
    last_opp_signal: crate::spec::Signal,
}

impl PlayerObs {
    fn new(standing: f64) -> Self {
        Self {
            last_opp_observed: None,
            last_self_intended: None,
            opponent_standing: standing,
            last_opp_signal: crate::spec::Signal::None,
        }
    }
}

trait Strategy {
    fn select_action(
        &mut self,
        obs: PlayerObs,
        rng: &mut ChaCha8Rng,
    ) -> (Action, crate::spec::Signal, Option<String>);
}

struct BuiltinStrategy {
    kind: BuiltinKind,
    p_cooperate: f64,
}

impl Strategy for BuiltinStrategy {
    fn select_action(
        &mut self,
        obs: PlayerObs,
        rng: &mut ChaCha8Rng,
    ) -> (Action, crate::spec::Signal, Option<String>) {
        use Action::*;
        let action = match self.kind {
            BuiltinKind::AlwaysC => C,
            BuiltinKind::AlwaysD => D,
            BuiltinKind::TitForTat => match obs.last_opp_observed {
                Some(Exit) | None => C,
                Some(other) => other,
            },
            BuiltinKind::WinStayLoseShift => {
                let Some(last_self) = obs.last_self_intended else {
                    return (C, crate::spec::Signal::None, None);
                };
                let Some(last_opp) = obs.last_opp_observed else {
                    return (C, crate::spec::Signal::None, None);
                };

                if last_self == Exit || last_opp == Exit {
                    return (C, crate::spec::Signal::None, None);
                }

                // "Win" is mutual cooperation or successful defection; otherwise shift.
                let win = matches!((last_self, last_opp), (C, C) | (D, C));
                if win {
                    last_self
                } else {
                    last_self.flipped()
                }
            }
            BuiltinKind::Random => {
                if rng.gen_bool(self.p_cooperate.clamp(0.0, 1.0)) {
                    C
                } else {
                    D
                }
            }
        };
        (action, crate::spec::Signal::None, None)
    }
}

struct MemoryOneStrategy {
    p0: f64,
    p_cc: f64,
    p_cd: f64,
    p_dc: f64,
    p_dd: f64,
}

impl MemoryOneStrategy {
    fn validate(&self) -> Result<(), SimError> {
        for p in [self.p0, self.p_cc, self.p_cd, self.p_dc, self.p_dd] {
            if !(0.0..=1.0).contains(&p) {
                return Err(SimError::InvalidProbability(p));
            }
        }
        Ok(())
    }
}

impl Strategy for MemoryOneStrategy {
    fn select_action(
        &mut self,
        obs: PlayerObs,
        rng: &mut ChaCha8Rng,
    ) -> (Action, crate::spec::Signal, Option<String>) {
        use Action::*;

        let p = match (obs.last_self_intended, obs.last_opp_observed) {
            (None, None) => self.p0,
            (Some(C), Some(C)) => self.p_cc,
            (Some(C), Some(D)) => self.p_cd,
            (Some(D), Some(C)) => self.p_dc,
            (Some(D), Some(D)) => self.p_dd,
            _ => self.p0,
        };

        let action = if rng.gen_bool(p.clamp(0.0, 1.0)) {
            C
        } else {
            D
        };
        (action, crate::spec::Signal::None, None)
    }
}

struct MemoryOneExitStrategy {
    p0_c: f64,
    p0_d: f64,
    p_cc_c: f64,
    p_cc_d: f64,
    p_cd_c: f64,
    p_cd_d: f64,
    p_dc_c: f64,
    p_dc_d: f64,
    p_dd_c: f64,
    p_dd_d: f64,
}

impl MemoryOneExitStrategy {
    fn validate(&self) -> Result<(), SimError> {
        let pairs = [
            (self.p0_c, self.p0_d),
            (self.p_cc_c, self.p_cc_d),
            (self.p_cd_c, self.p_cd_d),
            (self.p_dc_c, self.p_dc_d),
            (self.p_dd_c, self.p_dd_d),
        ];
        for (pc, pd) in pairs {
            if pc < 0.0 || pd < 0.0 || (pc + pd) > 1.0000001 {
                return Err(SimError::InvalidProbability(pc + pd));
            }
        }
        Ok(())
    }
}

impl Strategy for MemoryOneExitStrategy {
    fn select_action(
        &mut self,
        obs: PlayerObs,
        rng: &mut ChaCha8Rng,
    ) -> (Action, crate::spec::Signal, Option<String>) {
        use Action::*;

        let (pc, pd) = match (obs.last_self_intended, obs.last_opp_observed) {
            (None, None) => (self.p0_c, self.p0_d),
            (Some(C), Some(C)) => (self.p_cc_c, self.p_cc_d),
            (Some(C), Some(D)) => (self.p_cd_c, self.p_cd_d),
            (Some(D), Some(C)) => (self.p_dc_c, self.p_dc_d),
            (Some(D), Some(D)) => (self.p_dd_c, self.p_dd_d),
            _ => (self.p0_c, self.p0_d),
        };

        let r: f64 = rng.gen();
        let action = if r < pc {
            C
        } else if r < pc + pd {
            D
        } else {
            Exit
        };
        (action, crate::spec::Signal::None, None)
    }
}

struct FsmStrategy {
    current_state: u32,
    states: std::collections::HashMap<u32, crate::spec::FsmState>,
}

impl Strategy for FsmStrategy {
    fn select_action(
        &mut self,
        obs: PlayerObs,
        rng: &mut ChaCha8Rng,
    ) -> (Action, crate::spec::Signal, Option<String>) {
        use Action::*;

        // 1. Transition based on LAST observation (Move AND Signal)
        if let Some(state) = self.states.get(&self.current_state) {
            let mut transitioned = false;

            // Signal transitions take priority (Dialogic logic)
            for t in &state.trans_signals {
                if t.signal == obs.last_opp_signal {
                    self.current_state = t.next_state;
                    transitioned = true;
                    break;
                }
            }

            if !transitioned {
                if let Some(last_opp) = obs.last_opp_observed {
                    self.current_state = match last_opp {
                        C => state.trans_c,
                        D => state.trans_d,
                        Exit => state.trans_exit,
                    };
                }
            }
        }

        // 2. Select action based on NEW state
        let res = if let Some(state) = self.states.get(&self.current_state) {
            let action = if rng.gen_bool(state.output_c.clamp(0.0, 1.0)) {
                C
            } else {
                D
            };
            // For now, FSMs emit Signal::None unless specified.
            (
                action,
                crate::spec::Signal::None,
                Some(format!("state:{}", self.current_state)),
            )
        } else {
            // Fallback if state missing
            (
                D,
                crate::spec::Signal::None,
                Some(format!("err_missing_state:{}", self.current_state)),
            )
        };
        res
    }
}

fn build_strategy(spec: &StrategySpec) -> Result<Box<dyn Strategy>, SimError> {
    match spec {
        StrategySpec::Builtin { kind, params, .. } => {
            if !(0.0..=1.0).contains(&params.p_cooperate) {
                return Err(SimError::InvalidProbability(params.p_cooperate));
            }
            Ok(Box::new(BuiltinStrategy {
                kind: *kind,
                p_cooperate: params.p_cooperate,
            }))
        }
        StrategySpec::MemoryOne {
            p0,
            p_cc,
            p_cd,
            p_dc,
            p_dd,
            ..
        } => {
            let s = MemoryOneStrategy {
                p0: *p0,
                p_cc: *p_cc,
                p_cd: *p_cd,
                p_dc: *p_dc,
                p_dd: *p_dd,
            };
            s.validate()?;
            Ok(Box::new(s))
        }
        StrategySpec::MemoryOneExit {
            p0_c,
            p0_d,
            p_cc_c,
            p_cc_d,
            p_cd_c,
            p_cd_d,
            p_dc_c,
            p_dc_d,
            p_dd_c,
            p_dd_d,
            ..
        } => {
            let s = MemoryOneExitStrategy {
                p0_c: *p0_c,
                p0_d: *p0_d,
                p_cc_c: *p_cc_c,
                p_cc_d: *p_cc_d,
                p_cd_c: *p_cd_c,
                p_cd_d: *p_cd_d,
                p_dc_c: *p_dc_c,
                p_dc_d: *p_dc_d,
                p_dd_c: *p_dd_c,
                p_dd_d: *p_dd_d,
            };
            s.validate()?;
            Ok(Box::new(s))
        }
        StrategySpec::Fsm {
            initial_state,
            states,
            ..
        } => {
            let mut map = std::collections::HashMap::new();
            for s in states {
                map.insert(s.id, s.clone());
            }
            Ok(Box::new(FsmStrategy {
                current_state: *initial_state,
                states: map,
            }))
        }
    }
}

fn payoffs_for_ipd(task: &TaskSpec) -> Result<Payoffs, SimError> {
    match &task.world.game {
        crate::spec::GameSpec::Ipd { payoffs } => Ok(payoffs.clone()),
    }
}

#[derive(Debug, Clone, Copy)]
enum Player {
    A,
    B,
}

fn p_implementation(noise: &NoiseModelSpec, player: Player) -> f64 {
    match *noise {
        NoiseModelSpec::None => 0.0,
        NoiseModelSpec::ImplementationFlip { p } => p,
        NoiseModelSpec::ObservationFlip { .. } => 0.0,
        NoiseModelSpec::Iid {
            p_implementation, ..
        } => p_implementation,
        NoiseModelSpec::AsymmetricIid {
            p_implementation_a,
            p_implementation_b,
            ..
        } => match player {
            Player::A => p_implementation_a,
            Player::B => p_implementation_b,
        },
    }
}

fn p_observation(noise: &NoiseModelSpec, observer: Player) -> f64 {
    match *noise {
        NoiseModelSpec::None => 0.0,
        NoiseModelSpec::ImplementationFlip { .. } => 0.0,
        NoiseModelSpec::ObservationFlip { p } => p,
        NoiseModelSpec::Iid { p_observation, .. } => p_observation,
        NoiseModelSpec::AsymmetricIid {
            p_observation_a,
            p_observation_b,
            ..
        } => match observer {
            Player::A => p_observation_a,
            Player::B => p_observation_b,
        },
    }
}

fn apply_implementation_noise(
    noise: &NoiseModelSpec,
    player: Player,
    action: Action,
    rng: &mut ChaCha8Rng,
) -> Action {
    let p = p_implementation(noise, player);

    if rng.gen_bool(p) {
        action.flipped()
    } else {
        action
    }
}

fn apply_observation_noise(
    noise: &NoiseModelSpec,
    observer: Player,
    observed_action: Action,
    rng: &mut ChaCha8Rng,
) -> Action {
    let p = p_observation(noise, observer);

    if rng.gen_bool(p) {
        observed_action.flipped()
    } else {
        observed_action
    }
}

fn update_standing(
    current: f64,
    action: Action,
    opp_standing: f64,
    rule: &crate::spec::StandingUpdateRule,
) -> f64 {
    use Action::*;
    match rule {
        crate::spec::StandingUpdateRule::ImageScoring => {
            // Simple moving average: S = 0.9*S + 0.1*(1 if C else 0)
            let val = if action == C { 1.0 } else { 0.0 };
            (0.9 * current + 0.1 * val).clamp(0.0, 1.0)
        }
        crate::spec::StandingUpdateRule::StandingNorm { threshold } => {
            // If you defect against someone 'Good' (>= thresh), your standing drops.
            // If you defect against someone 'Bad', it stays the same (justified).
            // Cooperation always helps standing.
            match action {
                C => (current + 0.1).min(1.0),
                D => {
                    if opp_standing >= *threshold {
                        (current - 0.2).max(0.0)
                    } else {
                        current // Justified
                    }
                }
                Exit => current,
            }
        }
    }
}

pub fn run_match(task: &TaskSpec) -> Result<MatchArtifact, SimError> {
    let payoffs = payoffs_for_ipd(task)?;
    validate_noise(&task.world.noise)?;

    let mut current_standing_a = task.standing_a;
    let mut current_standing_b = task.standing_b;

    let (termination_seed, termination) = match task.world.termination {
        TerminationRuleSpec::Fixed { .. } => (None, None),
        TerminationRuleSpec::Geometric { delta, max_rounds } => {
            validate_probability(delta)?;
            if max_rounds == 0 {
                return Err(SimError::InvalidTermination(
                    "geometric max_rounds must be > 0".to_string(),
                ));
            }
            let seed = crate::util::derive_seed_u64(task.match_seed, "termination");
            (Some(seed), Some((delta, max_rounds)))
        }
    };

    let seed_streams = SeedStreams {
        match_seed: task.match_seed,
        decision_a: crate::util::derive_seed_u64(task.match_seed, "decision_a"),
        decision_b: crate::util::derive_seed_u64(task.match_seed, "decision_b"),
        impl_a: crate::util::derive_seed_u64(task.match_seed, "impl_a"),
        impl_b: crate::util::derive_seed_u64(task.match_seed, "impl_b"),
        obs_a: crate::util::derive_seed_u64(task.match_seed, "obs_a"),
        obs_b: crate::util::derive_seed_u64(task.match_seed, "obs_b"),
        termination: termination_seed,
    };

    let mut rng_decision_a = ChaCha8Rng::seed_from_u64(seed_streams.decision_a);
    let mut rng_decision_b = ChaCha8Rng::seed_from_u64(seed_streams.decision_b);
    let mut rng_impl_a = ChaCha8Rng::seed_from_u64(seed_streams.impl_a);
    let mut rng_impl_b = ChaCha8Rng::seed_from_u64(seed_streams.impl_b);
    let mut rng_obs_a = ChaCha8Rng::seed_from_u64(seed_streams.obs_a);
    let mut rng_obs_b = ChaCha8Rng::seed_from_u64(seed_streams.obs_b);
    let mut rng_term = termination_seed.map(ChaCha8Rng::seed_from_u64);

    let mut strat_a = build_strategy(&task.strategy_a)?;
    let mut strat_b = build_strategy(&task.strategy_b)?;

    let mut obs_a = PlayerObs::new(task.standing_b);
    let mut obs_b = PlayerObs::new(task.standing_a);

    let mut total_a = 0.0;
    let mut total_b = 0.0;
    let mut coop_a = 0u32;
    let mut coop_b = 0u32;
    let mut mutual_c = 0u32;
    let mut mutual_d = 0u32;

    let mut trace = if task.trace_rounds > 0 {
        Some(Vec::with_capacity(task.trace_rounds as usize))
    } else {
        None
    };

    let max_rounds = match task.world.termination {
        TerminationRuleSpec::Fixed { rounds } => rounds,
        TerminationRuleSpec::Geometric { max_rounds, .. } => max_rounds,
    };

    let mut rounds_executed = 0u32;
    let mut correct_a = 0u32;
    let mut correct_b = 0u32;
    let mut honest_a = 0u32;
    let mut honest_b = 0u32;
    let mut pred_a = Action::C;
    let mut pred_b = Action::C;
    let mut last_sig_a = crate::spec::Signal::None;
    let mut last_sig_b = crate::spec::Signal::None;

    for round in 0..max_rounds {
        let (a_intended, a_signal, state_a) = strat_a.select_action(obs_a, &mut rng_decision_a);
        let (b_intended, b_signal, state_b) = strat_b.select_action(obs_b, &mut rng_decision_b);

        // Simple Legibility Check: Can we predict intent?
        if a_intended == pred_a {
            correct_a += 1;
        }
        if b_intended == pred_b {
            correct_b += 1;
        }

        // Honesty Check: Did intent match prior signal?
        // (Note: Signal in round N-1 predicts action in round N)
        if round > 0 {
            if (last_sig_a == crate::spec::Signal::CoopIntent && a_intended == Action::C)
                || (last_sig_a == crate::spec::Signal::PunishWarning && a_intended == Action::D)
            {
                honest_a += 1;
            }
            if (last_sig_b == crate::spec::Signal::CoopIntent && b_intended == Action::C)
                || (last_sig_b == crate::spec::Signal::PunishWarning && b_intended == Action::D)
            {
                honest_b += 1;
            }
        }

        let a_executed =
            apply_implementation_noise(&task.world.noise, Player::A, a_intended, &mut rng_impl_a);
        let b_executed =
            apply_implementation_noise(&task.world.noise, Player::B, b_intended, &mut rng_impl_b);

        let a_observed_opp =
            apply_observation_noise(&task.world.noise, Player::A, b_executed, &mut rng_obs_a);
        let b_observed_opp =
            apply_observation_noise(&task.world.noise, Player::B, a_executed, &mut rng_obs_b);

        // Signal observation (no noise yet)
        let a_observed_signal = b_signal;
        let b_observed_signal = a_signal;

        let (pay_a, pay_b) = payoffs.payoff(a_executed, b_executed);
        total_a += pay_a;
        total_b += pay_b;

        if a_executed == Action::C {
            coop_a += 1;
        }
        if b_executed == Action::C {
            coop_b += 1;
        }
        if a_executed == Action::C && b_executed == Action::C {
            mutual_c += 1;
        }
        if a_executed == Action::D && b_executed == Action::D {
            mutual_d += 1;
        }

        if let Some(t) = trace.as_mut() {
            if round < task.trace_rounds {
                t.push(RoundTrace {
                    round,
                    a_intended,
                    b_intended,
                    a_signal,
                    b_signal,
                    a_executed,
                    b_executed,
                    a_observed_opp,
                    b_observed_opp,
                    a_observed_signal,
                    b_observed_signal,
                    payoff_a: pay_a,
                    payoff_b: pay_b,
                    state_a,
                    state_b,
                    standing_a: current_standing_a,
                    standing_b: current_standing_b,
                });
            }
        }

        obs_a.last_self_intended = Some(a_intended);
        obs_a.last_opp_observed = Some(a_observed_opp);
        obs_a.last_opp_signal = a_observed_signal;
        obs_b.last_self_intended = Some(b_intended);
        obs_b.last_opp_observed = Some(b_observed_opp);
        obs_b.last_opp_signal = b_observed_signal;

        // Update Reputation (Standing)
        if let crate::spec::ReputationModelSpec::SimpleStanding { update_rule, .. } =
            &task.world.reputation
        {
            let next_a = update_standing(
                current_standing_a,
                a_executed,
                current_standing_b,
                update_rule,
            );
            let next_b = update_standing(
                current_standing_b,
                b_executed,
                current_standing_a,
                update_rule,
            );
            current_standing_a = next_a;
            current_standing_b = next_b;
        }

        // Pass dynamic standing to next round's observations
        obs_a.opponent_standing = current_standing_b;
        obs_b.opponent_standing = current_standing_a;

        // Update state for next round's checks
        pred_a = a_observed_opp; // Simple reciprocal prediction
        pred_b = b_observed_opp;
        last_sig_a = a_signal;
        last_sig_b = b_signal;

        rounds_executed += 1;
        if a_executed == Action::Exit || b_executed == Action::Exit {
            break;
        }

        if let Some((delta, maxr)) = termination {
            debug_assert_eq!(maxr, max_rounds);
            let Some(rng) = rng_term.as_mut() else {
                break;
            };
            if !rng.gen_bool(delta) {
                break;
            }
        }
    }

    let denom = rounds_executed.max(1) as f64;
    Ok(MatchArtifact {
        schema_version: task.schema_version,
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        task_id: task.task_id.clone(),
        input_hash: String::new(), // filled by CLI (hash over task bytes)
        world_id: task.world.id.clone(),
        world_seed: task.world.seed,
        strategy_a_id: task.strategy_a.id().to_string(),
        strategy_b_id: task.strategy_b.id().to_string(),
        match_seed: task.match_seed,
        seed_streams,
        stats: MatchStats {
            rounds: rounds_executed,
            total_payoff_a: total_a,
            total_payoff_b: total_b,
            avg_payoff_a: total_a / denom,
            avg_payoff_b: total_b / denom,
            coop_rate_a: coop_a as f64 / denom,
            coop_rate_b: coop_b as f64 / denom,
            mutual_coop_rate: mutual_c as f64 / denom,
            mutual_defect_rate: mutual_d as f64 / denom,
            payoff_diff: (total_a / denom - total_b / denom).abs(),
            legibility_a: correct_a as f64 / denom,
            legibility_b: correct_b as f64 / denom,
            honesty_a: honest_a as f64 / denom.max(1.0),
            honesty_b: honest_b as f64 / denom.max(1.0),
        },
        trace,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::spec::{
        BuiltinKind, BuiltinParams, GameSpec, NoiseModelSpec, Payoffs, ReputationModelSpec,
        StrategySpec, TaskSpec, TerminationRuleSpec, WorldSpec,
    };
    use pretty_assertions::assert_eq;

    #[test]
    fn determinism_same_seed_same_output() {
        let mut task = TaskSpec::new(
            "t1",
            WorldSpec {
                id: "ipd".to_string(),
                game: GameSpec::Ipd {
                    payoffs: Payoffs::default(),
                },
                noise: NoiseModelSpec::None,
                termination: TerminationRuleSpec::Fixed { rounds: 50 },
                reputation: ReputationModelSpec::None,
                seed: 123,
            },
            StrategySpec::Builtin {
                id: "tft".to_string(),
                kind: BuiltinKind::TitForTat,
                params: BuiltinParams::default(),
            },
            StrategySpec::Builtin {
                id: "rand".to_string(),
                kind: BuiltinKind::Random,
                params: BuiltinParams { p_cooperate: 0.37 },
            },
            999,
        );
        task.trace_rounds = 10;

        let a1 = run_match(&task).unwrap();
        let a2 = run_match(&task).unwrap();
        assert_eq!(
            serde_json::to_value(a1).unwrap(),
            serde_json::to_value(a2).unwrap()
        );
    }

    #[test]
    fn swap_players_swaps_totals_in_deterministic_no_noise_case() {
        let world = WorldSpec {
            id: "ipd".to_string(),
            game: GameSpec::Ipd {
                payoffs: Payoffs::default(),
            },
            noise: NoiseModelSpec::None,
            termination: TerminationRuleSpec::Fixed { rounds: 10 },
            reputation: ReputationModelSpec::None,
            seed: 123,
        };

        let always_c = StrategySpec::Builtin {
            id: "always_c".to_string(),
            kind: BuiltinKind::AlwaysC,
            params: BuiltinParams::default(),
        };
        let always_d = StrategySpec::Builtin {
            id: "always_d".to_string(),
            kind: BuiltinKind::AlwaysD,
            params: BuiltinParams::default(),
        };

        let task_ab = TaskSpec::new("ab", world.clone(), always_c.clone(), always_d.clone(), 999);
        let task_ba = TaskSpec::new("ba", world, always_d, always_c, 999);

        let ab = run_match(&task_ab).unwrap();
        let ba = run_match(&task_ba).unwrap();
        assert_eq!(ab.stats.total_payoff_a, ba.stats.total_payoff_b);
        assert_eq!(ab.stats.total_payoff_b, ba.stats.total_payoff_a);
    }

    #[test]
    fn invalid_noise_probability_errors() {
        let task = TaskSpec::new(
            "bad_noise",
            WorldSpec {
                id: "ipd".to_string(),
                game: GameSpec::Ipd {
                    payoffs: Payoffs::default(),
                },
                noise: NoiseModelSpec::ObservationFlip { p: 1.5 },
                termination: TerminationRuleSpec::Fixed { rounds: 1 },
                reputation: ReputationModelSpec::None,
                seed: 1,
            },
            StrategySpec::Builtin {
                id: "always_c".to_string(),
                kind: BuiltinKind::AlwaysC,
                params: BuiltinParams::default(),
            },
            StrategySpec::Builtin {
                id: "always_c".to_string(),
                kind: BuiltinKind::AlwaysC,
                params: BuiltinParams::default(),
            },
            1,
        );

        let err = run_match(&task).unwrap_err();
        assert!(matches!(err, SimError::InvalidProbability(p) if (p - 1.5).abs() < 1e-9));
    }

    #[test]
    fn invalid_asymmetric_noise_probability_errors() {
        let task = TaskSpec::new(
            "bad_asym_noise",
            WorldSpec {
                id: "ipd".to_string(),
                game: GameSpec::Ipd {
                    payoffs: Payoffs::default(),
                },
                noise: NoiseModelSpec::AsymmetricIid {
                    p_implementation_a: 0.0,
                    p_implementation_b: 2.0,
                    p_observation_a: 0.0,
                    p_observation_b: 0.0,
                },
                termination: TerminationRuleSpec::Fixed { rounds: 1 },
                reputation: ReputationModelSpec::None,
                seed: 1,
            },
            StrategySpec::Builtin {
                id: "always_c".to_string(),
                kind: BuiltinKind::AlwaysC,
                params: BuiltinParams::default(),
            },
            StrategySpec::Builtin {
                id: "always_c".to_string(),
                kind: BuiltinKind::AlwaysC,
                params: BuiltinParams::default(),
            },
            1,
        );

        let err = run_match(&task).unwrap_err();
        assert!(matches!(err, SimError::InvalidProbability(p) if (p - 2.0).abs() < 1e-9));
    }

    #[test]
    fn geometric_termination_delta_zero_runs_one_round() {
        let task = TaskSpec::new(
            "geo0",
            WorldSpec {
                id: "ipd".to_string(),
                game: GameSpec::Ipd {
                    payoffs: Payoffs::default(),
                },
                noise: NoiseModelSpec::None,
                termination: TerminationRuleSpec::Geometric {
                    delta: 0.0,
                    max_rounds: 50,
                },
                reputation: ReputationModelSpec::None,
                seed: 1,
            },
            StrategySpec::Builtin {
                id: "always_c".to_string(),
                kind: BuiltinKind::AlwaysC,
                params: BuiltinParams::default(),
            },
            StrategySpec::Builtin {
                id: "always_c".to_string(),
                kind: BuiltinKind::AlwaysC,
                params: BuiltinParams::default(),
            },
            999,
        );
        let a = run_match(&task).unwrap();
        assert_eq!(a.stats.rounds, 1);
        assert!(a.seed_streams.termination.is_some());
    }

    #[test]
    fn geometric_termination_delta_one_runs_to_max_rounds() {
        let task = TaskSpec::new(
            "geo1",
            WorldSpec {
                id: "ipd".to_string(),
                game: GameSpec::Ipd {
                    payoffs: Payoffs::default(),
                },
                noise: NoiseModelSpec::None,
                termination: TerminationRuleSpec::Geometric {
                    delta: 1.0,
                    max_rounds: 17,
                },
                reputation: ReputationModelSpec::None,
                seed: 1,
            },
            StrategySpec::Builtin {
                id: "always_c".to_string(),
                kind: BuiltinKind::AlwaysC,
                params: BuiltinParams::default(),
            },
            StrategySpec::Builtin {
                id: "always_c".to_string(),
                kind: BuiltinKind::AlwaysC,
                params: BuiltinParams::default(),
            },
            999,
        );
        let a = run_match(&task).unwrap();
        assert_eq!(a.stats.rounds, 17);
        assert!(a.seed_streams.termination.is_some());
    }
}
