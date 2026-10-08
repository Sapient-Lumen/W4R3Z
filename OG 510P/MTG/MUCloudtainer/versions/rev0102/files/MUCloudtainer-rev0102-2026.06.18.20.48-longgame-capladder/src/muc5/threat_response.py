from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random
from typing import Any, Iterable, Mapping, Sequence

from .action_schema import Action
from .cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE, CARD_OVERLORD
from .counter_response import COUNTER_GUARD_AGENT, GUARDED_COUNTER_AXIS
from .cpp_rollout import CppShadowGameSpec
from .decision import apply_decision_index, build_decision_frame
from .deckspace import DeckVector
from .engine import start_game
from .library_buffer_sweep import scale_deck_to_legal_size
from .mulligan_ranker import make_mulligan_agent
from .payoff import StrategyBundle, load_seed_decks
from .public_agents import make_public_agent
from .terminal_decomposition import CF34_MULLIGAN, THREAT_MULLIGAN
from .terminal_mechanisms import annotate_focus_target_from_seat, annotate_target_mechanism, mechanism_profile_rows, target_summary_rows, to_float, to_int
from .threat_closure import THREAT_CLOSURE_AGENT

THREAT_PRESSURE_AGENT = "threat_pressure"
CLOSURE_THREAT_AXIS = "library_aware_threat_closure_targetguarded"
PRESSURE_THREAT_AXIS = "jace_pressure_threat_response"


@dataclass(frozen=True)
class ThreatResponseArm:
    """Counter-guard candidate tested against stronger named threat baselines."""

    arm_id: str
    question: str
    target: StrategyBundle
    opponent: StrategyBundle
    counter_policy_axis: str
    threat_policy_axis: str
    size_axis: str
    interpretation: str

    def as_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["target"] = self.target.as_dict()
        out["opponent"] = self.opponent.as_dict()
        return out


def _bundle(strategy_id: str, deck_name: str, deck: DeckVector, agent: str, mulligan: str) -> StrategyBundle:
    return StrategyBundle(strategy_id, deck_name, deck, agent, mulligan)


def rev0066_threat_response_arms(seed_decks_path) -> list[ThreatResponseArm]:
    """Build a matched threat-policy response panel against ``counter_guard``.

    rev0065 rescued the counter-wall deck under a fixed ``threat_closure`` pilot.
    This panel asks whether that rescue survives two pressure changes: (1) the
    target-controller guard that prevents accidental self-countering, and (2) a
    Jace-pressure threat response that attacks opposing Jace and conserves library
    once bodies are online.
    """

    decks = load_seed_decks(seed_decks_path)
    counter60 = decks["sixty_counterwall_jace"]
    threat40 = decks["forty_overlord_impending"]
    counter40 = scale_deck_to_legal_size(counter60, 40)
    threat60 = scale_deck_to_legal_size(threat40, 60)

    def counter(size: int) -> StrategyBundle:
        deck = counter60 if size == 60 else counter40
        deck_name = "sixty_counterwall_jace" if size == 60 else "forty_counterwall_scaled_from60"
        return _bundle(f"guard_counter_wall{size}", deck_name, deck, COUNTER_GUARD_AGENT, CF34_MULLIGAN)

    def threat(size: int, policy: str) -> StrategyBundle:
        deck = threat40 if size == 40 else threat60
        deck_name = "forty_overlord_impending" if size == 40 else "sixty_overlord_scaled_from40"
        axis = "closure" if policy == THREAT_CLOSURE_AGENT else "pressure"
        return _bundle(f"pub_threat{size}_{axis}", deck_name, deck, policy, THREAT_MULLIGAN)

    plan = [
        ("A", 40, 40, "40-vs-40 counter_guard rescue cell from rev0065."),
        ("B", 60, 40, "60-vs-40 size-skew rescue cell from rev0065."),
        ("C", 60, 60, "60-vs-60 normalized rescue cell from rev0065."),
    ]
    arms: list[ThreatResponseArm] = []
    for prefix, counter_size, threat_size, question in plan:
        for policy, threat_axis in (
            (THREAT_CLOSURE_AGENT, CLOSURE_THREAT_AXIS),
            (THREAT_PRESSURE_AGENT, PRESSURE_THREAT_AXIS),
        ):
            pressure = policy == THREAT_PRESSURE_AGENT
            arms.append(
                ThreatResponseArm(
                    arm_id=f"{prefix}_{'pressure' if pressure else 'closure'}_counter{counter_size}_vs_threat{threat_size}",
                    question=question,
                    target=counter(counter_size),
                    opponent=threat(threat_size, policy),
                    counter_policy_axis=GUARDED_COUNTER_AXIS,
                    threat_policy_axis=threat_axis,
                    size_axis=f"counter{counter_size}_vs_threat{threat_size}",
                    interpretation=(
                        "Updated threat_closure with stack target ownership guard; this is the repaired rev0065 baseline."
                        if not pressure
                        else "Jace-pressure threat response: ownership guard plus more aggressive anti-Jace attacks and less redundant Overlord churn."
                    ),
                )
            )
    return arms


def threat_response_specs(
    arms: Sequence[ThreatResponseArm],
    *,
    simulator_revision: str,
    life_totals: Sequence[int] = (20, 40),
    reps: int = 3,
    base_seed: int = 6666000,
    max_decisions: int = 900,
) -> tuple[tuple[CppShadowGameSpec, ...], dict[str, dict[str, Any]]]:
    specs: list[CppShadowGameSpec] = []
    meta: dict[str, dict[str, Any]] = {}
    k = 0
    for arm in arms:
        for life in life_totals:
            for target_seat in (0, 1):
                left, right = (arm.target, arm.opponent) if target_seat == 0 else (arm.opponent, arm.target)
                for starting_player in (0, 1):
                    for rep in range(int(reps)):
                        gid = f"g{k:05d}_{arm.arm_id}_life{life}_seat{target_seat}_sp{starting_player}_r{rep}"
                        specs.append(
                            CppShadowGameSpec(
                                game_id=gid,
                                strategy0=left.strategy_id,
                                strategy1=right.strategy_id,
                                deck0_name=left.deck_name,
                                deck1_name=right.deck_name,
                                deck0=left.deck,
                                deck1=right.deck,
                                agent0=left.agent_name,
                                agent1=right.agent_name,
                                mulligan0=str(left.mulligan_policy),
                                mulligan1=str(right.mulligan_policy),
                                seed=int(base_seed + k),
                                starting_player=int(starting_player),
                                starting_life=int(life),
                                max_decisions=int(max_decisions),
                                simulator_revision=simulator_revision,
                            )
                        )
                        meta[gid] = {
                            "arm_id": arm.arm_id,
                            "question": arm.question,
                            "interpretation": arm.interpretation,
                            "target": arm.target.strategy_id,
                            "opponent": arm.opponent.strategy_id,
                            "target_deck": arm.target.deck_name,
                            "opponent_deck": arm.opponent.deck_name,
                            "target_agent": arm.target.agent_name,
                            "opponent_agent": arm.opponent.agent_name,
                            "target_mulligan": str(arm.target.mulligan_policy),
                            "opponent_mulligan": str(arm.opponent.mulligan_policy),
                            "target_deck_size": arm.target.deck.size,
                            "opponent_deck_size": arm.opponent.deck.size,
                            "target_island_count": arm.target.deck.island,
                            "target_counterspell_count": arm.target.deck.counterspell,
                            "target_force_count": arm.target.deck.force,
                            "target_jace_count": arm.target.deck.jace,
                            "target_overlord_count": arm.target.deck.overlord,
                            "opponent_island_count": arm.opponent.deck.island,
                            "opponent_counterspell_count": arm.opponent.deck.counterspell,
                            "opponent_force_count": arm.opponent.deck.force,
                            "opponent_jace_count": arm.opponent.deck.jace,
                            "opponent_overlord_count": arm.opponent.deck.overlord,
                            "target_seat": int(target_seat),
                            "threat_seat": int(1 - target_seat),
                            "rep": int(rep),
                            "counter_policy_axis": arm.counter_policy_axis,
                            "threat_policy_axis": arm.threat_policy_axis,
                            "size_axis": arm.size_axis,
                        }
                        k += 1
    return tuple(specs), meta



def threat_response_stress_specs(
    arms: Sequence[ThreatResponseArm],
    *,
    candidate_cells: Sequence[tuple[str, int]],
    simulator_revision: str,
    reps: int = 4,
    base_seed: int = 6666900,
    max_decisions: int = 900,
) -> tuple[tuple[CppShadowGameSpec, ...], dict[str, dict[str, Any]]]:
    """Generate a seed-disjoint follow-up for selected threat-response cells."""

    wanted = {(str(axis), int(life)) for axis, life in candidate_cells}
    specs: list[CppShadowGameSpec] = []
    meta: dict[str, dict[str, Any]] = {}
    k = 0
    for arm in arms:
        for axis, life in sorted(wanted):
            if arm.size_axis != axis:
                continue
            for target_seat in (0, 1):
                left, right = (arm.target, arm.opponent) if target_seat == 0 else (arm.opponent, arm.target)
                for starting_player in (0, 1):
                    for rep in range(int(reps)):
                        gid = f"s{k:05d}_{arm.arm_id}_life{life}_seat{target_seat}_sp{starting_player}_r{rep}"
                        specs.append(
                            CppShadowGameSpec(
                                game_id=gid,
                                strategy0=left.strategy_id,
                                strategy1=right.strategy_id,
                                deck0_name=left.deck_name,
                                deck1_name=right.deck_name,
                                deck0=left.deck,
                                deck1=right.deck,
                                agent0=left.agent_name,
                                agent1=right.agent_name,
                                mulligan0=str(left.mulligan_policy),
                                mulligan1=str(right.mulligan_policy),
                                seed=int(base_seed + k),
                                starting_player=int(starting_player),
                                starting_life=int(life),
                                max_decisions=int(max_decisions),
                                simulator_revision=simulator_revision,
                            )
                        )
                        meta[gid] = {
                            "arm_id": arm.arm_id,
                            "question": arm.question,
                            "interpretation": arm.interpretation,
                            "target": arm.target.strategy_id,
                            "opponent": arm.opponent.strategy_id,
                            "target_deck": arm.target.deck_name,
                            "opponent_deck": arm.opponent.deck_name,
                            "target_agent": arm.target.agent_name,
                            "opponent_agent": arm.opponent.agent_name,
                            "target_mulligan": str(arm.target.mulligan_policy),
                            "opponent_mulligan": str(arm.opponent.mulligan_policy),
                            "target_deck_size": arm.target.deck.size,
                            "opponent_deck_size": arm.opponent.deck.size,
                            "target_island_count": arm.target.deck.island,
                            "target_counterspell_count": arm.target.deck.counterspell,
                            "target_force_count": arm.target.deck.force,
                            "target_jace_count": arm.target.deck.jace,
                            "target_overlord_count": arm.target.deck.overlord,
                            "opponent_island_count": arm.opponent.deck.island,
                            "opponent_counterspell_count": arm.opponent.deck.counterspell,
                            "opponent_force_count": arm.opponent.deck.force,
                            "opponent_jace_count": arm.opponent.deck.jace,
                            "opponent_overlord_count": arm.opponent.deck.overlord,
                            "target_seat": int(target_seat),
                            "threat_seat": int(1 - target_seat),
                            "rep": int(rep),
                            "counter_policy_axis": arm.counter_policy_axis,
                            "threat_policy_axis": arm.threat_policy_axis,
                            "size_axis": arm.size_axis,
                            "stress_cell": f"{arm.size_axis}_life{life}",
                            "stress_seed_disjoint": True,
                        }
                        k += 1
    return tuple(specs), meta

def annotate_threat_response_rows(rows: Sequence[Mapping[str, Any]], meta: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    # Late import avoids making all historical terminal-mechanism tests pay for
    # policy-runtime hashing, while ensuring future generated population rows
    # carry enough identity to detect policy-code drift.
    from .population_replay_guard import annotate_policy_identity_rows

    for row in rows:
        gid = str(row.get("cpp_shadow_game_id", ""))
        merged = dict(row)
        merged.update(meta.get(gid, {}))
        out.append(annotate_focus_target_from_seat(merged))
    return annotate_policy_identity_rows(out)


def threat_response_summary_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return target_summary_rows(
        rows,
        group_keys=(
            "arm_id",
            "starting_life",
            "size_axis",
            "counter_policy_axis",
            "threat_policy_axis",
            "target_deck_size",
            "opponent_deck_size",
            "target",
            "opponent",
        ),
    )


def threat_response_mechanism_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return mechanism_profile_rows(rows, group_keys=("arm_id", "starting_life", "size_axis", "threat_policy_axis", "target", "opponent"))


def compare_threat_response_by_life(summary_rows: Iterable[Mapping[str, Any]]) -> list[dict[str, object]]:
    """Compare threat responses without converting missing evidence to zero."""

    by: dict[tuple[str, str, int], Mapping[str, Any]] = {}
    for row in summary_rows:
        by[(str(row.get("size_axis", "")), str(row.get("threat_policy_axis", "")), to_int(row.get("starting_life"), 0))] = row
    cells = sorted({(axis, life) for (axis, _threat, life) in by if axis and life})
    required_axes = (CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS)
    out: list[dict[str, object]] = []
    for axis, life in cells:
        rows_by_policy = {policy: by.get((axis, policy, life)) for policy in required_axes}
        missing = [policy for policy, row in rows_by_policy.items() if row is None]
        if missing:
            out.append(
                {
                    "size_axis": axis,
                    "starting_life": life,
                    "counter_guard_score_vs_repaired_closure": None,
                    "counter_guard_score_vs_threat_pressure": None,
                    "pressure_minus_closure_counter_score_delta": None,
                    "closure_target_library_out_wins": None,
                    "pressure_target_library_out_wins": None,
                    "closure_target_life_total_wins": None,
                    "pressure_target_life_total_wins": None,
                    "missing_threat_policy_axes": missing,
                    "provisional_read": "incomplete_matrix",
                }
            )
            continue

        closure = rows_by_policy[CLOSURE_THREAT_AXIS]
        pressure = rows_by_policy[PRESSURE_THREAT_AXIS]
        assert closure is not None and pressure is not None
        closure_score = to_float(closure.get("target_mean_score_draw_half"), 0.0)
        pressure_score = to_float(pressure.get("target_mean_score_draw_half"), 0.0)
        delta = pressure_score - closure_score
        if pressure_score <= 0.45 and delta <= -0.15:
            read = "threat_pressure_refutes_counter_rescue"
        elif pressure_score >= 0.60 and delta >= -0.10:
            read = "counter_guard_rescue_survives_pressure"
        elif pressure_score >= 0.50:
            read = "counter_guard_mixed_under_pressure"
        elif delta >= 0.15:
            read = "threat_pressure_backfires"
        else:
            read = "mixed_or_underpowered"
        out.append(
            {
                "size_axis": axis,
                "starting_life": life,
                "counter_guard_score_vs_repaired_closure": closure_score,
                "counter_guard_score_vs_threat_pressure": pressure_score,
                "pressure_minus_closure_counter_score_delta": delta,
                "closure_target_library_out_wins": to_int(closure.get("target_library_out_wins"), 0),
                "pressure_target_library_out_wins": to_int(pressure.get("target_library_out_wins"), 0),
                "closure_target_life_total_wins": to_int(closure.get("target_life_total_wins"), 0),
                "pressure_target_life_total_wins": to_int(pressure.get("target_life_total_wins"), 0),
                "missing_threat_policy_axes": [],
                "provisional_read": read,
            }
        )
    return out


def _target_spell_from_stack(obs: Mapping[str, object], action: Action) -> Mapping[str, object]:
    try:
        target_id = int(action.params.get("target_id", -1))
    except (TypeError, ValueError):
        return {}
    stack = obs.get("stack")
    if not isinstance(stack, list):
        return {}
    for item in stack:
        if not isinstance(item, Mapping):
            continue
        try:
            spell_id = int(item.get("spell_id", -2))
        except (TypeError, ValueError):
            continue
        if spell_id == target_id:
            return item
    return {}


def counter_target_ownership_features_from_spec(spec: CppShadowGameSpec, *, target_seat: int, threat_seat: int) -> dict[str, object]:
    """Rerun a game and count selected counter actions by target ownership.

    This audits the exact bug exposed while building rev0066: public scorers were
    ranking Counterspell/Force by target card only.  Because the legal menu allows
    self-countering, a threat pilot could spend cards countering its own Overlord.
    """

    agents = (make_public_agent(spec.agent0), make_public_agent(spec.agent1))
    mulligans = (make_mulligan_agent(spec.mulligan0), make_mulligan_agent(spec.mulligan1))
    state = start_game(
        spec.deck0,
        spec.deck1,
        seed=int(spec.seed),
        starting_player=int(spec.starting_player),
        starting_life=int(spec.starting_life),
        mulligan_agents=mulligans,
        record_log=False,
    )
    rng = Random(int(spec.seed) + 1000003)
    counts = {
        "cpp_shadow_game_id": spec.game_id,
        "seed": int(spec.seed),
        "starting_life": int(spec.starting_life),
        "target_seat": int(target_seat),
        "threat_seat": int(threat_seat),
        "selected_counter_actions": 0,
        "selected_own_spell_counters": 0,
        "target_selected_counter_actions": 0,
        "target_selected_own_spell_counters": 0,
        "threat_selected_counter_actions": 0,
        "threat_selected_own_spell_counters": 0,
        "threat_selected_own_overlord_counters": 0,
        "threat_selected_own_jace_counters": 0,
        "applied_decisions": 0,
        "terminal_winner": "",
        "terminal_loss_reason": "",
    }
    for decision in range(int(spec.max_decisions)):
        if state.winner is not None:
            break
        frame = build_decision_frame(state)
        actor = int(frame.player)
        action_index = agents[actor].choose_action_index(frame, rng)
        action = frame.legal_actions[action_index]
        if action.kind == "CAST" and str(action.params.get("card", "")) in {CARD_COUNTERSPELL, CARD_FORCE}:
            counts["selected_counter_actions"] += 1
            if actor == int(target_seat):
                counts["target_selected_counter_actions"] += 1
            if actor == int(threat_seat):
                counts["threat_selected_counter_actions"] += 1
            target_spell = _target_spell_from_stack(frame.observation, action)
            target_controller = target_spell.get("controller")
            try:
                owns_target = int(target_controller) == actor
            except (TypeError, ValueError):
                owns_target = False
            if owns_target:
                counts["selected_own_spell_counters"] += 1
                if actor == int(target_seat):
                    counts["target_selected_own_spell_counters"] += 1
                if actor == int(threat_seat):
                    counts["threat_selected_own_spell_counters"] += 1
                    target_card = str(action.params.get("target_card", ""))
                    if target_card == CARD_OVERLORD:
                        counts["threat_selected_own_overlord_counters"] += 1
                    if target_card == CARD_JACE:
                        counts["threat_selected_own_jace_counters"] += 1
        apply_decision_index(state, frame, action_index, rng)
        counts["applied_decisions"] = decision + 1
    counts["terminal_winner"] = "" if state.winner is None else int(state.winner)
    counts["terminal_loss_reason"] = str(state.loss_reason)
    return counts


def summarize_counter_ownership_rows(rows: Sequence[Mapping[str, object]], *, group_keys: Sequence[str]) -> list[dict[str, object]]:
    groups: dict[tuple[object, ...], list[Mapping[str, object]]] = {}
    for row in rows:
        groups.setdefault(tuple(row.get(k, "") for k in group_keys), []).append(row)
    out: list[dict[str, object]] = []
    for key, vals in sorted(groups.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
        item = {group_keys[i]: key[i] for i in range(len(group_keys))}
        item["games"] = len(vals)
        for field in (
            "selected_counter_actions",
            "selected_own_spell_counters",
            "target_selected_counter_actions",
            "target_selected_own_spell_counters",
            "threat_selected_counter_actions",
            "threat_selected_own_spell_counters",
            "threat_selected_own_overlord_counters",
            "threat_selected_own_jace_counters",
        ):
            item[f"sum_{field}"] = sum(to_int(v.get(field), 0) for v in vals)
        item["own_spell_counter_rate_per_game"] = item["sum_selected_own_spell_counters"] / max(1, len(vals))
        item["threat_own_spell_counter_rate_per_game"] = item["sum_threat_selected_own_spell_counters"] / max(1, len(vals))
        out.append(item)
    return out


def threat_response_gate_report(summary: Mapping[str, object], rows: Sequence[Mapping[str, object]], ownership_rows: Sequence[Mapping[str, object]], *, min_games: int = 120) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    if int(summary.get("games", 0)) < int(min_games):
        errors.append(f"fewer than {min_games} threat-response games")
    if int(summary.get("truncations", 0)) != 0:
        errors.append("terminal-clean gate failed: truncations present")
    if int(summary.get("python_errors", 0)) != 0:
        errors.append("python errors occurred during C++ shadow rollout")
    if int(summary.get("forensic_games", 0)) != int(summary.get("games", -1)):
        errors.append("forensic rerun did not cover every game")
    if int(summary.get("closure_feature_games", 0)) != int(summary.get("games", -1)):
        errors.append("closure feature rerun did not cover every game")
    if int(summary.get("counter_ownership_games", 0)) != int(summary.get("games", -1)):
        errors.append("counter ownership audit did not cover every game")
    cpp = summary.get("cpp_shadow_summary", {})
    if isinstance(cpp, Mapping):
        if int(cpp.get("mismatches", 0)) != 0:
            errors.append("C++ shadow mismatches present")
        if int(cpp.get("skipped_events", 0)) != 0:
            warnings.append("C++ shadow skipped events present")
    threat_axes = {str(r.get("threat_policy_axis")) for r in rows}
    for required in (CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS):
        if required not in threat_axes:
            errors.append(f"required threat policy missing: {required}")
    size_axes = {str(r.get("size_axis")) for r in rows}
    for required in ("counter40_vs_threat40", "counter60_vs_threat40", "counter60_vs_threat60"):
        if required not in size_axes:
            errors.append(f"required size axis missing: {required}")
    own_spell_counters = sum(to_int(r.get("selected_own_spell_counters"), 0) for r in ownership_rows)
    if own_spell_counters != 0:
        errors.append(f"selected own-spell counters remain after target-ownership guard: {own_spell_counters}")
    return {"passed": not errors, "errors": errors, "warnings": warnings}
