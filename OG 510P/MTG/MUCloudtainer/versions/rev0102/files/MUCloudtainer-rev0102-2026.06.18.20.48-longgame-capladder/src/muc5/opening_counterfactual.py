from __future__ import annotations

import copy
from collections import Counter
from dataclasses import asdict, dataclass
from random import Random
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from .action_schema import Action
from .cards import CARD_ORDER, STARTING_LIFE_OPTIONS
from .cpp_transition import (
    TransitionMicroRecord,
    cpp_transition_signatures,
    cpp_transition_tool_status,
    is_supported_transition,
    state_signature,
    transition_record_from_state_action,
    with_jace_ultimate_shuffle_transport,
)
from .decision import apply_decision_index, build_decision_frame
from .deckspace import DeckVector
from .engine import deck_to_library, start_game_from_pregame_state
from .mulligan import (
    MULLIGAN_KEEP,
    MULLIGAN_TAKE,
    MulliganAgent,
    MulliganObservation,
    RuleMulliganAgent,
    london_mulligan_agent_opening_hand,
)
from .mulligan_ranker import make_mulligan_agent, opening_hand_quality
from .public_agents import make_public_agent
from .reward_guard import reward_packet_from_state


@dataclass(frozen=True)
class ForcedFirstMulliganAgent:
    """Force the first keep/take decision, then delegate normal decisions.

    This makes an opening-hand counterfactual local: the two branches begin from
    the exact same first seven-card look.  After that forced first decision, the
    fallback mulligan agent handles future keep/take and bottom-card choices.
    """

    first_action: str  # keep or mulligan
    fallback: MulliganAgent
    name: str = "forced_first_mulligan"

    def __post_init__(self) -> None:
        if self.first_action not in {"keep", "mulligan"}:
            raise ValueError("first_action must be 'keep' or 'mulligan'")
        object.__setattr__(self, "name", f"forced_first_{self.first_action}_then_{self.fallback.name}")

    def choose_mulligan_action(self, obs: MulliganObservation, legal: Sequence[Action], rng: Random) -> Action:
        if obs.stage == "keep_or_mulligan" and obs.mulligans_taken == 0:
            if self.first_action == "keep":
                return MULLIGAN_KEEP
            if MULLIGAN_TAKE in legal:
                return MULLIGAN_TAKE
            return MULLIGAN_KEEP
        return self.fallback.choose_mulligan_action(obs, legal, rng)


@dataclass(frozen=True)
class OpeningBranch:
    branch: str
    hand: Dict[str, int]
    library: Tuple[str, ...]
    mulligans_taken: int
    kept_hand_size: int
    decision_events: Tuple[Dict[str, object], ...]
    mulligan_log_row: Dict[str, object]

    def hand_count(self, card: str) -> int:
        return int(self.hand.get(card, 0))


@dataclass(frozen=True)
class OpponentPregame:
    hand: Dict[str, int]
    library: Tuple[str, ...]
    mulligans_taken: int
    decision_events: Tuple[Dict[str, object], ...]
    mulligan_log_row: Dict[str, object]


@dataclass(frozen=True)
class CounterfactualPairSpec:
    pair_id: str
    deck0_name: str
    deck1_name: str
    deck0: DeckVector
    deck1: DeckVector
    agent0: str
    agent1: str
    fallback_mulligan0: str
    mulligan1: str
    starting_life: int
    starting_player: int
    seed: int
    max_decisions: int = 500


@dataclass(frozen=True)
class CounterfactualTransitionRow:
    pair_id: str
    branch: str
    step: int
    player: int
    frame: str
    pending_choice_kind: str
    stack_depth: int
    action_kind: str
    action: str
    supported_by_cpp: bool
    cpp_match: bool | None
    case_id: str

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CounterfactualRunResult:
    branch_rows: Tuple[Dict[str, object], ...]
    paired_rows: Tuple[Dict[str, object], ...]
    transition_rows: Tuple[CounterfactualTransitionRow, ...]
    summary: Dict[str, object]


def _counts_row(prefix: str, counts: Mapping[str, int]) -> Dict[str, int]:
    return {f"{prefix}_{card}": int(counts.get(card, 0) or 0) for card in CARD_ORDER}


def _counter_to_dict(counter: Mapping[str, int]) -> Dict[str, int]:
    return {card: int(counter.get(card, 0) or 0) for card in CARD_ORDER if int(counter.get(card, 0) or 0) > 0}


def make_forced_branch(
    *,
    branch: str,
    initial_library: Sequence[str],
    agent: MulliganAgent | str,
    player: int,
    seed: int,
    starting_life: int,
    deck_counts: Mapping[str, int],
) -> OpeningBranch:
    """Resolve one forced first-decision branch from the same library order."""

    fallback = make_mulligan_agent(agent)
    forced = ForcedFirstMulliganAgent(branch, fallback)
    library = list(initial_library)
    hand, result, events = london_mulligan_agent_opening_hand(
        library,
        Random(seed),
        forced,
        player=player,
        starting_life=starting_life,
        deck_counts=dict(deck_counts),
    )
    return OpeningBranch(
        branch=branch,
        hand=_counter_to_dict(hand),
        library=tuple(library),
        mulligans_taken=int(result.mulligans_taken),
        kept_hand_size=int(result.kept_hand_size),
        decision_events=tuple(e.to_row() for e in events),
        mulligan_log_row=result.to_row(),
    )


def make_opponent_pregame(
    *,
    initial_library: Sequence[str],
    agent: MulliganAgent | str,
    player: int,
    seed: int,
    starting_life: int,
    deck_counts: Mapping[str, int],
) -> OpponentPregame:
    library = list(initial_library)
    hand, result, events = london_mulligan_agent_opening_hand(
        library,
        Random(seed),
        make_mulligan_agent(agent),
        player=player,
        starting_life=starting_life,
        deck_counts=dict(deck_counts),
    )
    return OpponentPregame(
        hand=_counter_to_dict(hand),
        library=tuple(library),
        mulligans_taken=int(result.mulligans_taken),
        decision_events=tuple(e.to_row() for e in events),
        mulligan_log_row=result.to_row(),
    )


def _first_seven_counts(library: Sequence[str]) -> Dict[str, int]:
    # Top of library is list[-1].  The first opening look is the last seven cards.
    return _counter_to_dict(Counter(list(library)[-7:]))


def _score_for_player(winner: int | None, player: int) -> float:
    if winner is None:
        return 0.5
    return 1.0 if winner == player else 0.0


def _pending_kind(state) -> str:
    return "none" if state.pending_choice is None else str(state.pending_choice.kind)


def play_counterfactual_branch(
    spec: CounterfactualPairSpec,
    branch: OpeningBranch,
    opponent: OpponentPregame,
    *,
    transition_rows: List[CounterfactualTransitionRow],
    records: List[TransitionMicroRecord],
    expected: List[str],
    row_indices: List[int],
) -> Dict[str, object]:
    """Play one keep/mulligan branch while recording C++ transition checks."""

    state = start_game_from_pregame_state(
        spec.deck0,
        spec.deck1,
        library0=branch.library,
        hand0=branch.hand,
        mulligans0=branch.mulligans_taken,
        library1=opponent.library,
        hand1=opponent.hand,
        mulligans1=opponent.mulligans_taken,
        starting_player=spec.starting_player,
        starting_life=spec.starting_life,
        record_log=False,
        mulligan_log=[branch.mulligan_log_row, opponent.mulligan_log_row],
        mulligan_decision_log=[*branch.decision_events, *opponent.decision_events],
    )
    agents = [make_public_agent(spec.agent0), make_public_agent(spec.agent1)]
    transition_rng = Random(spec.seed)
    agent_rng = Random(spec.seed + 1000003)
    decisions = 0
    for decisions in range(1, spec.max_decisions + 1):
        if state.winner is not None:
            break
        frame = build_decision_frame(state)
        if frame.action_count <= 0:
            break
        action_index = agents[frame.player].choose_action_index(frame, agent_rng)
        if action_index < 0 or action_index >= frame.action_count:
            raise ValueError(f"{spec.pair_id}/{branch.branch}: illegal action index {action_index}/{frame.action_count}")
        action = frame.legal_actions[action_index]
        pre_state = copy.deepcopy(state)
        case_id = f"{spec.pair_id}_{branch.branch}_step{decisions}_{state.frame}_{_pending_kind(state)}_{action.kind}"
        apply_decision_index(state, frame, action_index, transition_rng)
        transported = with_jace_ultimate_shuffle_transport(pre_state, action, state)
        supported = is_supported_transition(pre_state, transported)
        row_index = len(transition_rows)
        if supported:
            records.append(transition_record_from_state_action(pre_state, transported, case_id))
            expected.append(state_signature(state))
            row_indices.append(row_index)
        transition_rows.append(
            CounterfactualTransitionRow(
                pair_id=spec.pair_id,
                branch=branch.branch,
                step=int(decisions),
                player=int(frame.player),
                frame=str(pre_state.frame),
                pending_choice_kind=_pending_kind(pre_state),
                stack_depth=len(pre_state.stack),
                action_kind=str(action.kind),
                action=action.compact(),
                supported_by_cpp=bool(supported),
                cpp_match=None,
                case_id=case_id,
            )
        )
    if state.winner is None:
        state.frame = "GAME_OVER"
        state.loss_reason = "max_decisions_reached"
    p0_packet = reward_packet_from_state(state, 0)
    p1_packet = reward_packet_from_state(state, 1)
    return {
        "pair_id": spec.pair_id,
        "branch": branch.branch,
        "strategy0": f"{spec.deck0_name}:{spec.agent0}:{spec.fallback_mulligan0}",
        "strategy1": f"{spec.deck1_name}:{spec.agent1}:{spec.mulligan1}",
        "deck0": spec.deck0_name,
        "deck1": spec.deck1_name,
        "agent0": spec.agent0,
        "agent1": spec.agent1,
        "fallback_mulligan0": spec.fallback_mulligan0,
        "mulligan1": spec.mulligan1,
        "starting_life": int(spec.starting_life),
        "starting_player": int(spec.starting_player),
        "seed": int(spec.seed),
        "transition_seed": int(spec.seed),
        "agent_seed": int(spec.seed + 1000003),
        "winner": "None" if state.winner is None else str(state.winner),
        "p0_score": _score_for_player(state.winner, 0),
        "p1_score": _score_for_player(state.winner, 1),
        "p0_terminal_win": 1.0 if state.winner == 0 else 0.0,
        "p1_terminal_win": 1.0 if state.winner == 1 else 0.0,
        "is_nonterminal_draw": state.winner is None,
        "is_truncation": state.loss_reason == "max_decisions_reached",
        "loss_reason": state.loss_reason,
        "decisions": int(decisions),
        "turn_number": int(state.turn_number),
        "branch_mulligans_taken": int(branch.mulligans_taken),
        "branch_kept_hand_size": int(branch.kept_hand_size),
        "opponent_mulligans_taken": int(opponent.mulligans_taken),
        "p0_terminal_only_score": "None" if p0_packet.terminal_only_score is None else p0_packet.terminal_only_score,
        "p1_terminal_only_score": "None" if p1_packet.terminal_only_score is None else p1_packet.terminal_only_score,
        **_counts_row("kept_hand", branch.hand),
    }


def build_counterfactual_specs(seed_decks: Mapping[str, DeckVector], *, samples_per_shell_life: int = 12, base_seed: int = 28000) -> Tuple[CounterfactualPairSpec, ...]:
    """Small fixed panel for rev0028 opening-hand branch tests."""

    shells = [
        ("fjace_vs_wall", "forty_force_jace_pressure", "sixty_counterwall_jace", "code_jace_lock_rev0013", "counter_happy", "mulligan_outcome_ranker_rev0027", "land_band_business"),
        ("overlord_vs_jace60", "forty_overlord_impending", "sixty_no_overlord_jace_only", "threat_rush", "code_jace_lock_rev0013", "mulligan_outcome_ranker_rev0027", "keep_always"),
        ("wall_vs_overlord", "sixty_counterwall_jace", "forty_overlord_impending", "outcome_ranker_blend_counter_rev0025", "threat_rush", "mulligan_ranker_rev0024", "land_band"),
    ]
    specs: List[CounterfactualPairSpec] = []
    k = 0
    for shell_id, d0_name, d1_name, a0, a1, m0, m1 in shells:
        for life in STARTING_LIFE_OPTIONS:
            for sample in range(samples_per_shell_life):
                for starting_player in (0, 1):
                    specs.append(
                        CounterfactualPairSpec(
                            pair_id=f"{shell_id}_life{life}_sp{starting_player}_s{sample:03d}",
                            deck0_name=d0_name,
                            deck1_name=d1_name,
                            deck0=seed_decks[d0_name],
                            deck1=seed_decks[d1_name],
                            agent0=a0,
                            agent1=a1,
                            fallback_mulligan0=m0,
                            mulligan1=m1,
                            starting_life=int(life),
                            starting_player=int(starting_player),
                            seed=base_seed + k,
                        )
                    )
                    k += 1
    return tuple(specs)


def run_opening_counterfactual_panel(specs: Sequence[CounterfactualPairSpec]) -> CounterfactualRunResult:
    branch_rows: List[Dict[str, object]] = []
    paired: List[Dict[str, object]] = []
    transition_rows: List[CounterfactualTransitionRow] = []
    records: List[TransitionMicroRecord] = []
    expected: List[str] = []
    row_indices: List[int] = []

    for spec in specs:
        deck_rng0 = Random(spec.seed + 11)
        deck_rng1 = Random(spec.seed + 97)
        initial_library0 = deck_to_library(spec.deck0, deck_rng0)
        initial_library1 = deck_to_library(spec.deck1, deck_rng1)
        first7 = _first_seven_counts(initial_library0)
        first7_quality = opening_hand_quality(first7, spec.deck0.counts(), spec.starting_life, 0)
        opponent = make_opponent_pregame(
            initial_library=initial_library1,
            agent=spec.mulligan1,
            player=1,
            seed=spec.seed + 1009,
            starting_life=spec.starting_life,
            deck_counts=spec.deck1.counts(),
        )
        branches = [
            make_forced_branch(
                branch="keep",
                initial_library=initial_library0,
                agent=spec.fallback_mulligan0,
                player=0,
                seed=spec.seed + 2003,
                starting_life=spec.starting_life,
                deck_counts=spec.deck0.counts(),
            ),
            make_forced_branch(
                branch="mulligan",
                initial_library=initial_library0,
                agent=spec.fallback_mulligan0,
                player=0,
                seed=spec.seed + 2003,
                starting_life=spec.starting_life,
                deck_counts=spec.deck0.counts(),
            ),
        ]
        by_branch: Dict[str, Dict[str, object]] = {}
        for branch in branches:
            row = play_counterfactual_branch(
                spec,
                branch,
                opponent,
                transition_rows=transition_rows,
                records=records,
                expected=expected,
                row_indices=row_indices,
            )
            row.update(
                {
                    "initial_hand_quality": first7_quality,
                    **_counts_row("initial_hand", first7),
                }
            )
            branch_rows.append(row)
            by_branch[branch.branch] = row
        keep_score = float(by_branch["keep"]["p0_score"])
        mull_score = float(by_branch["mulligan"]["p0_score"])
        paired.append(
            {
                "pair_id": spec.pair_id,
                "deck0": spec.deck0_name,
                "deck1": spec.deck1_name,
                "agent0": spec.agent0,
                "agent1": spec.agent1,
                "fallback_mulligan0": spec.fallback_mulligan0,
                "mulligan1": spec.mulligan1,
                "starting_life": int(spec.starting_life),
                "starting_player": int(spec.starting_player),
                "seed": int(spec.seed),
                "initial_hand_quality": first7_quality,
                **_counts_row("initial_hand", first7),
                "keep_score": keep_score,
                "mulligan_score": mull_score,
                "mulligan_minus_keep": mull_score - keep_score,
                "better_branch": "mulligan" if mull_score > keep_score else ("keep" if keep_score > mull_score else "tie"),
                "keep_mulligans_taken": by_branch["keep"]["branch_mulligans_taken"],
                "mulligan_mulligans_taken": by_branch["mulligan"]["branch_mulligans_taken"],
                "keep_decisions": by_branch["keep"]["decisions"],
                "mulligan_decisions": by_branch["mulligan"]["decisions"],
                "keep_truncation": by_branch["keep"]["is_truncation"],
                "mulligan_truncation": by_branch["mulligan"]["is_truncation"],
            }
        )

    mismatches = 0
    if records:
        actual = cpp_transition_signatures(records)
        for rec_i, (got, want) in enumerate(zip(actual, expected)):
            row_idx = row_indices[rec_i]
            old = transition_rows[row_idx]
            ok = got == want
            if not ok:
                mismatches += 1
            transition_rows[row_idx] = CounterfactualTransitionRow(
                pair_id=old.pair_id,
                branch=old.branch,
                step=old.step,
                player=old.player,
                frame=old.frame,
                pending_choice_kind=old.pending_choice_kind,
                stack_depth=old.stack_depth,
                action_kind=old.action_kind,
                action=old.action,
                supported_by_cpp=old.supported_by_cpp,
                cpp_match=ok,
                case_id=old.case_id,
            )
    events = len(transition_rows)
    supported = sum(1 for r in transition_rows if r.supported_by_cpp)
    summary: Dict[str, object] = {
        "revision": "rev0028",
        "specs": len(specs),
        "branch_games": len(branch_rows),
        "paired_rows": len(paired),
        "transition_events": events,
        "supported_cpp_events": supported,
        "skipped_cpp_events": events - supported,
        "cpp_mismatches": mismatches,
        "cpp_support_rate": 0.0 if events == 0 else supported / events,
        "cpp_match_rate_on_supported": 1.0 if supported == 0 else (supported - mismatches) / supported,
        "truncations": sum(1 for r in branch_rows if str(r.get("is_truncation")).lower() in {"true", "1"}),
        "mulligan_better_pairs": sum(1 for r in paired if r["better_branch"] == "mulligan"),
        "keep_better_pairs": sum(1 for r in paired if r["better_branch"] == "keep"),
        "tie_pairs": sum(1 for r in paired if r["better_branch"] == "tie"),
        "mean_mulligan_minus_keep": 0.0 if not paired else sum(float(r["mulligan_minus_keep"]) for r in paired) / len(paired),
        "tool_status": cpp_transition_tool_status().as_dict(),
    }
    return CounterfactualRunResult(
        branch_rows=tuple(branch_rows),
        paired_rows=tuple(paired),
        transition_rows=tuple(transition_rows),
        summary=summary,
    )
