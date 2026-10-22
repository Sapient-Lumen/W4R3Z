#![forbid(unsafe_code)]

use portal_net_model::{Admission, ModelState, NetRequest, Operation, Outcome};

const BOUND: usize = 4;

#[derive(Clone, Copy, Debug)]
struct Step {
    req_id: &'static str,
    domain: &'static str,
    operation: OperationChoice,
    admission: AdmissionChoice,
}

#[derive(Clone, Copy, Debug)]
enum OperationChoice {
    Connect,
    ListenLocal,
}

#[derive(Clone, Copy, Debug)]
enum AdmissionChoice {
    Allow,
    Deny(&'static str),
}

impl OperationChoice {
    fn to_operation(self) -> Operation {
        match self {
            OperationChoice::Connect => Operation::Connect,
            OperationChoice::ListenLocal => Operation::ListenLocal,
        }
    }
}

impl AdmissionChoice {
    fn to_admission(self) -> Admission {
        match self {
            AdmissionChoice::Allow => Admission::Allow,
            AdmissionChoice::Deny(reason) => Admission::Deny(reason),
        }
    }
}

fn action_space() -> Vec<Step> {
    vec![
        Step {
            req_id: "r1",
            domain: "alpha.example",
            operation: OperationChoice::Connect,
            admission: AdmissionChoice::Allow,
        },
        Step {
            req_id: "r1",
            domain: "alpha.example",
            operation: OperationChoice::Connect,
            admission: AdmissionChoice::Deny("policy-deny"),
        },
        Step {
            req_id: "r1",
            domain: "beta.example",
            operation: OperationChoice::Connect,
            admission: AdmissionChoice::Allow,
        },
        Step {
            req_id: "r1",
            domain: "alpha.example",
            operation: OperationChoice::ListenLocal,
            admission: AdmissionChoice::Allow,
        },
        Step {
            req_id: "r2",
            domain: "alpha.example",
            operation: OperationChoice::Connect,
            admission: AdmissionChoice::Allow,
        },
        Step {
            req_id: "r2",
            domain: "beta.example",
            operation: OperationChoice::Connect,
            admission: AdmissionChoice::Allow,
        },
        Step {
            req_id: "r3",
            domain: "gamma.example",
            operation: OperationChoice::Connect,
            admission: AdmissionChoice::Allow,
        },
        Step {
            req_id: "r3",
            domain: "gamma.example",
            operation: OperationChoice::Connect,
            admission: AdmissionChoice::Deny("operator-deny"),
        },
    ]
}

fn apply_step(state: &mut ModelState, step: Step) -> Outcome {
    let req = NetRequest::new(
        step.req_id,
        "svc:portal.net",
        step.domain,
        step.operation.to_operation(),
    )
    .unwrap();
    state.apply(req, step.admission.to_admission())
}

fn run_sequence(seq: &[Step]) -> (Vec<Outcome>, ModelState) {
    let mut state = ModelState::default();
    let mut outcomes = Vec::with_capacity(seq.len());
    for step in seq {
        let before_len = state.accepted().len();
        let outcome = apply_step(&mut state, *step);
        match &outcome {
            Outcome::Accepted { commit_index, .. } => {
                assert_eq!(*commit_index as usize, before_len);
                assert_eq!(state.accepted().len(), before_len + 1);
            }
            Outcome::Replayed { .. } | Outcome::Denied(_) | Outcome::Rejected(_) => {
                assert_eq!(state.accepted().len(), before_len);
            }
        }
        assert_eq!(state.validate_invariants(), Ok(()));
        check_all_prefixes(&state);
        outcomes.push(outcome);
    }
    (outcomes, state)
}

fn check_all_prefixes(state: &ModelState) {
    for k in 0..=state.accepted().len() {
        let recovered = ModelState::replay_prefix(&state.accepted()[..k]).unwrap();
        assert_eq!(recovered.accepted(), &state.accepted()[..k]);
        assert_eq!(recovered.validate_invariants(), Ok(()));
    }
}

fn enumerate_sequences<F: FnMut(&[Step])>(bound: usize, mut f: F) {
    fn rec<F: FnMut(&[Step])>(space: &[Step], bound: usize, path: &mut Vec<Step>, f: &mut F) {
        f(path);
        if path.len() == bound {
            return;
        }
        for step in space {
            path.push(*step);
            rec(space, bound, path, f);
            path.pop();
        }
    }

    let space = action_space();
    let mut path = Vec::with_capacity(bound);
    rec(&space, bound, &mut path, &mut f);
}

#[test]
fn bounded_sequences_preserve_transition_invariants() {
    let mut seen = 0usize;
    enumerate_sequences(BOUND, |seq| {
        let (_outcomes, state) = run_sequence(seq);
        assert_eq!(state.validate_invariants(), Ok(()));
        check_all_prefixes(&state);
        seen += 1;
    });
    assert_eq!(seen, 4_681);
}

#[test]
fn bounded_sequences_are_deterministic() {
    enumerate_sequences(BOUND, |seq| {
        let (outcomes_a, state_a) = run_sequence(seq);
        let (outcomes_b, state_b) = run_sequence(seq);
        assert_eq!(outcomes_a, outcomes_b);
        assert_eq!(state_a, state_b);
    });
}

#[test]
fn replay_prefix_rejects_corrupted_commit_indexes() {
    let seq = [
        Step {
            req_id: "r1",
            domain: "alpha.example",
            operation: OperationChoice::Connect,
            admission: AdmissionChoice::Allow,
        },
        Step {
            req_id: "r2",
            domain: "beta.example",
            operation: OperationChoice::Connect,
            admission: AdmissionChoice::Allow,
        },
    ];
    let (_outcomes, state) = run_sequence(&seq);
    let mut corrupted = state.accepted().to_vec();
    corrupted[1].commit_index = 7;
    assert_eq!(
        ModelState::replay_prefix(&corrupted),
        Err("non-contiguous-commit-index")
    );
}

#[test]
fn replay_prefix_rejects_corrupted_post_state_fingerprints() {
    let seq = [
        Step {
            req_id: "r1",
            domain: "alpha.example",
            operation: OperationChoice::Connect,
            admission: AdmissionChoice::Allow,
        },
        Step {
            req_id: "r2",
            domain: "beta.example",
            operation: OperationChoice::Connect,
            admission: AdmissionChoice::Allow,
        },
    ];
    let (_outcomes, state) = run_sequence(&seq);
    let mut corrupted = state.accepted().to_vec();
    corrupted[0].post_state_fingerprint ^= 1;
    assert_eq!(
        ModelState::replay_prefix(&corrupted),
        Err("prefix-post-state-fingerprint-mismatch")
    );
}
