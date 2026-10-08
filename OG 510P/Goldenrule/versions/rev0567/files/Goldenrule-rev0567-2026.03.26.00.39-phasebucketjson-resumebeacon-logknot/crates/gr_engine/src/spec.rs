use serde::{Deserialize, Serialize};

fn default_schema_version() -> u32 {
    1
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Action {
    C,
    D,
    Exit,
}

impl Action {
    pub fn flipped(self) -> Self {
        match self {
            Action::C => Action::D,
            Action::D => Action::C,
            Action::Exit => Action::Exit,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Payoffs {
    pub r: f64,
    pub s: f64,
    pub t: f64,
    pub p: f64,
    #[serde(default = "default_exit_payoff")]
    pub exit: f64,
}

fn default_exit_payoff() -> f64 {
    0.0
}

impl Default for Payoffs {
    fn default() -> Self {
        Self {
            r: 3.0,
            s: 0.0,
            t: 5.0,
            p: 1.0,
            exit: 0.0,
        }
    }
}

impl Payoffs {
    pub fn payoff(&self, a: Action, b: Action) -> (f64, f64) {
        use Action::*;
        match (a, b) {
            (Exit, _) | (_, Exit) => (self.exit, self.exit),
            (C, C) => (self.r, self.r),
            (C, D) => (self.s, self.t),
            (D, C) => (self.t, self.s),
            (D, D) => (self.p, self.p),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum GameSpec {
    Ipd { payoffs: Payoffs },
}

impl Default for GameSpec {
    fn default() -> Self {
        GameSpec::Ipd {
            payoffs: Payoffs::default(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum NoiseModelSpec {
    None,
    ImplementationFlip {
        p: f64,
    },
    ObservationFlip {
        p: f64,
    },
    Iid {
        p_implementation: f64,
        p_observation: f64,
    },
    AsymmetricIid {
        p_implementation_a: f64,
        p_implementation_b: f64,
        p_observation_a: f64,
        p_observation_b: f64,
    },
}

impl Default for NoiseModelSpec {
    fn default() -> Self {
        NoiseModelSpec::None
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum TerminationRuleSpec {
    Fixed { rounds: u32 },
    Geometric { delta: f64, max_rounds: u32 },
}

impl Default for TerminationRuleSpec {
    fn default() -> Self {
        TerminationRuleSpec::Fixed { rounds: 200 }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorldSpec {
    pub id: String,
    #[serde(default)]
    pub game: GameSpec,
    #[serde(default)]
    pub noise: NoiseModelSpec,
    #[serde(default)]
    pub termination: TerminationRuleSpec,
    #[serde(default)]
    pub reputation: ReputationModelSpec,
    pub seed: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum ReputationModelSpec {
    None,
    SimpleStanding {
        initial_standing: f64,
        update_rule: StandingUpdateRule,
    },
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum StandingUpdateRule {
    /// Standing = P(C in last N rounds)
    ImageScoring,
    /// Standing drops if you defect against a 'Good' opponent, but not against a 'Bad' one.
    /// (Requires a threshold for 'Good')
    StandingNorm { threshold: f64 },
}

impl Default for ReputationModelSpec {
    fn default() -> Self {
        ReputationModelSpec::None
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "family", rename_all = "snake_case")]
pub enum StrategySpec {
    Builtin {
        id: String,
        kind: BuiltinKind,
        #[serde(default)]
        params: BuiltinParams,
    },
    MemoryOne {
        id: String,
        p0: f64,
        p_cc: f64,
        p_cd: f64,
        p_dc: f64,
        p_dd: f64,
    },
    MemoryOneExit {
        id: String,
        // p_c + p_d + p_exit must be <= 1.0 (remainder is Exit or we just normalize)
        // Let's use 2 parameters per state: p_c and p_d. p_exit = 1 - p_c - p_d.
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
    },
    Fsm {
        id: String,
        initial_state: u32,
        states: Vec<FsmState>,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FsmState {
    pub id: u32,
    pub output_c: f64, // Probability of C in this state
    pub trans_c: u32,  // State to transition to if opponent plays C
    pub trans_d: u32,  // State to transition to if opponent plays D
    #[serde(default)]
    pub trans_exit: u32, // State to transition to if opponent exits
    #[serde(default)]
    pub trans_signals: Vec<FsmSignalTransition>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FsmSignalTransition {
    pub signal: Signal,
    pub next_state: u32,
}

impl StrategySpec {
    pub fn id(&self) -> &str {
        match self {
            StrategySpec::Builtin { id, .. } => id,
            StrategySpec::MemoryOne { id, .. } => id,
            StrategySpec::MemoryOneExit { id, .. } => id,
            StrategySpec::Fsm { id, .. } => id,
        }
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BuiltinKind {
    AlwaysC,
    AlwaysD,
    TitForTat,
    WinStayLoseShift,
    Random,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BuiltinParams {
    #[serde(default = "default_p_cooperate")]
    pub p_cooperate: f64,
}

fn default_p_cooperate() -> f64 {
    0.5
}

impl Default for BuiltinParams {
    fn default() -> Self {
        Self {
            p_cooperate: default_p_cooperate(),
        }
    }
}

impl Default for WorldSpec {
    fn default() -> Self {
        Self {
            id: "default".to_string(),
            game: GameSpec::default(),
            noise: NoiseModelSpec::default(),
            termination: TerminationRuleSpec::default(),
            reputation: ReputationModelSpec::default(),
            seed: 0,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Signal {
    None,
    CoopIntent,
    PunishWarning,
    RepairRequest,
}

impl Default for Signal {
    fn default() -> Self {
        Signal::None
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskSpec {
    #[serde(default = "default_schema_version")]
    pub schema_version: u32,
    pub task_id: String,
    pub world: WorldSpec,
    pub strategy_a: StrategySpec,
    pub strategy_b: StrategySpec,
    pub match_seed: u64,
    #[serde(default = "default_standing")]
    pub standing_a: f64,
    #[serde(default = "default_standing")]
    pub standing_b: f64,
    #[serde(default)]
    pub trace_rounds: u32,
}

impl TaskSpec {
    pub fn new(id: &str, world: WorldSpec, a: StrategySpec, b: StrategySpec, seed: u64) -> Self {
        Self {
            schema_version: default_schema_version(),
            task_id: id.to_string(),
            world,
            strategy_a: a,
            strategy_b: b,
            match_seed: seed,
            standing_a: default_standing(),
            standing_b: default_standing(),
            trace_rounds: 0,
        }
    }
}

fn default_standing() -> f64 {
    1.0
}
