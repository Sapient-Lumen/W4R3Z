from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from random import Random
from statistics import mean
from typing import Any, Mapping, Sequence

from .action_schema import Action
from .cards import CARD_JACE, CARD_OVERLORD, OVERLORD_POWER
from .cpp_rollout import CppShadowGameSpec
from .decision import apply_decision_index, build_decision_frame
from .deckspace import DeckVector
from .engine import start_game
from .library_buffer_sweep import all_island_deck, scale_deck_to_legal_size
from .mulligan_ranker import make_mulligan_agent
from .payoff import StrategyBundle, load_seed_decks
from .public_agents import make_public_agent
from .terminal_decomposition import CF34_AGENT, CF34_MULLIGAN, THREAT_MULLIGAN
from .terminal_mechanisms import annotate_target_mechanism, mechanism_profile_rows, target_summary_rows, to_float, to_int

THREAT_RUSH_AGENT = "threat_rush"
THREAT_CLOSURE_AGENT = "threat_closure"


@dataclass(frozen=True)
class ThreatClosureArm:
    arm_id: str
    question: str
    target: StrategyBundle
    opponent: StrategyBundle
    threat_agent: str
    target_size_axis: str
    policy_axis: str
    interpretation: str

    def as_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["target"] = self.target.as_dict()
        out["opponent"] = self.opponent.as_dict()
        return out


def _bundle(strategy_id: str, deck_name: str, deck: DeckVector, agent: str, mulligan: str) -> StrategyBundle:
    return StrategyBundle(strategy_id, deck_name, deck, agent, mulligan)


def rev0063_threat_closure_arms(seed_decks_path) -> list[ThreatClosureArm]:
    """Focused current-vs-guarded threat closure controls.

    rev0062 showed that the original 40-card Overlord threat shell can lose to
    all-Island controls, especially at life 40.  This panel keeps the opponent
    deck fixed and changes only the public threat policy from ``threat_rush`` to
    the explicit library-aware ``threat_closure`` guard.  The focus score is the
    inert target's score, so a successful closure guard should *lower* the score.
    """

    decks = load_seed_decks(seed_decks_path)
    threat40_deck = decks["forty_overlord_impending"]
    threat60_deck = scale_deck_to_legal_size(threat40_deck, 60)
    buffer40 = all_island_deck(40)
    buffer60 = all_island_deck(60)

    def inert(size: int) -> StrategyBundle:
        deck = buffer40 if size == 40 else buffer60
        return _bundle(f"inert_buffer{size}", f"all_island_buffer{size}", deck, CF34_AGENT, CF34_MULLIGAN)

    def threat(size: int, agent: str) -> StrategyBundle:
        deck = threat40_deck if size == 40 else threat60_deck
        suffix = "rush" if agent == THREAT_RUSH_AGENT else "closure"
        return _bundle(
            f"threat{size}_{suffix}",
            "forty_overlord_impending" if size == 40 else "sixty_overlord_scaled_from40",
            deck,
            agent,
            THREAT_MULLIGAN,
        )

    arms: list[ThreatClosureArm] = []
    for target_size in (40, 60):
        for threat_size in (40, 60):
            if target_size == 60 and threat_size == 60:
                # Keep the panel focused: rev0062 already showed equalized 60-vs-60
                # buffer controls.  The new risk is whether the threat pilot, not
                # legal size alone, explains failure against inert controls.
                continue
            for agent in (THREAT_RUSH_AGENT, THREAT_CLOSURE_AGENT):
                arm_id = f"{('P' if agent == THREAT_RUSH_AGENT else 'Q')}_threat{threat_size}_{agent}_vs_buffer{target_size}"
                if threat_size == 60:
                    arm_id = f"{('R' if agent == THREAT_RUSH_AGENT else 'S')}_threat60_{agent}_vs_buffer{target_size}"
                arms.append(
                    ThreatClosureArm(
                        arm_id=arm_id,
                        question=f"Can {agent} close with threat{threat_size} against inert buffer{target_size}?",
                        target=inert(target_size),
                        opponent=threat(threat_size, agent),
                        threat_agent=agent,
                        target_size_axis=f"buffer{target_size}_vs_threat{threat_size}",
                        policy_axis="legacy_threat_rush" if agent == THREAT_RUSH_AGENT else "library_aware_threat_closure",
                        interpretation=(
                            "Legacy control: if the inert target wins here, the current threat policy is failing to close."
                            if agent == THREAT_RUSH_AGENT
                            else "Guarded-policy test: lower inert target score means closure improved without changing simulator semantics."
                        ),
                    )
                )
    return arms


def threat_closure_specs(
    arms: Sequence[ThreatClosureArm],
    *,
    simulator_revision: str,
    life_totals: Sequence[int] = (20, 40),
    reps: int = 3,
    base_seed: int = 6363000,
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
                            "threat_agent": arm.threat_agent,
                            "target_size_axis": arm.target_size_axis,
                            "policy_axis": arm.policy_axis,
                            "target_deck_size": arm.target.deck.size,
                            "opponent_deck_size": arm.opponent.deck.size,
                            "target_seat": int(target_seat),
                            "threat_seat": int(1 - target_seat),
                            "rep": int(rep),
                        }
                        k += 1
    return tuple(specs), meta


def annotate_threat_closure_rows(rows: Sequence[Mapping[str, Any]], meta: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        gid = str(row.get("cpp_shadow_game_id", ""))
        merged = dict(row)
        merged.update(meta.get(gid, {}))
        seat = to_int(merged.get("target_seat"), 0)
        merged["focus_target_seat"] = seat
        merged["focus_target_score"] = to_float(merged.get("p0_score" if seat == 0 else "p1_score"), 0.5)
        out.append(annotate_target_mechanism(merged))
    return out


def threat_closure_summary_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return target_summary_rows(
        rows,
        group_keys=(
            "arm_id",
            "starting_life",
            "target_size_axis",
            "policy_axis",
            "target_deck_size",
            "opponent_deck_size",
            "threat_agent",
        ),
    )


def threat_closure_mechanism_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return mechanism_profile_rows(rows, group_keys=("arm_id", "starting_life", "target_size_axis", "policy_axis", "threat_agent"))


def attack_draw_cost(action: Action) -> int:
    if action.kind != "ATTACK":
        return 0
    attackers = to_int(action.params.get("to_player"), 0) + to_int(action.params.get("to_jace"), 0)
    return 2 * max(0, attackers)


def attack_face_damage(action: Action) -> int:
    if action.kind != "ATTACK":
        return 0
    return OVERLORD_POWER * max(0, to_int(action.params.get("to_player"), 0))


def threat_closure_trace_features_from_spec(spec: CppShadowGameSpec, *, threat_seat: int, target_seat: int) -> dict[str, object]:
    """Run one game and extract closure-specific tactical features.

    This is intentionally narrower than ``trajectory_forensics_from_spec``.  It
    asks whether the threat pilot was losing to its own draw engine: Jace zero,
    Overlord ETB draws, attack-trigger draws, and especially attacks that would
    have been lethal if combat damage happened before the attack triggers.
    """

    transition_rng = Random(int(spec.seed))
    agent_rng = Random(int(spec.seed) + 1000003)
    state = start_game(
        spec.deck0,
        spec.deck1,
        seed=int(spec.seed),
        starting_player=int(spec.starting_player),
        starting_life=int(spec.starting_life),
        mulligan_agents=(make_mulligan_agent(spec.mulligan0), make_mulligan_agent(spec.mulligan1)),
        record_log=False,
    )
    agents = [make_public_agent(spec.agent0), make_public_agent(spec.agent1)]
    features: dict[str, object] = {
        "cpp_shadow_game_id": spec.game_id,
        "seed": int(spec.seed),
        "starting_life": int(spec.starting_life),
        "starting_player": int(spec.starting_player),
        "target_seat": int(target_seat),
        "threat_seat": int(threat_seat),
        "threat_declared_attack_actions": 0,
        "threat_declared_attackers_total": 0,
        "threat_declared_attackers_to_player": 0,
        "threat_declared_attack_draw_cost_total": 0,
        "threat_declared_lethal_attack_actions": 0,
        "threat_selfdeck_on_attack_trigger": 0,
        "threat_selfdeck_on_declared_lethal_attack": 0,
        "threat_overlord_cast_draw_events": 0,
        "threat_selfdeck_on_overlord_cast": 0,
        "threat_jace_zero_actions": 0,
        "threat_jace_zero_at_library_le_10": 0,
        "threat_selfdeck_on_jace_zero": 0,
        "threat_ultimate_self_actions": 0,
        "threat_ultimate_opponent_actions": 0,
        "threat_pass_attack_actions": 0,
        "threat_min_library_before_draw_burst": 9999,
        "threat_last_action_before_loss": "",
        "threat_loss_vector": "",
        "decisions": 0,
    }
    for step in range(1, int(spec.max_decisions) + 1):
        if state.winner is not None:
            break
        frame = build_decision_frame(state)
        if frame.action_count <= 0:
            break
        action_index = agents[frame.player].choose_action_index(frame, agent_rng)  # type: ignore[attr-defined]
        action = frame.legal_actions[action_index]
        pre_actor = int(frame.player)
        pre_actor_library = len(state.players[pre_actor].library)
        pre_defender = 1 - pre_actor
        pre_defender_life = int(state.players[pre_defender].life)
        pre_action_is_threat = pre_actor == int(threat_seat)
        draw_burst_cost = 0
        declared_lethal = False
        action_compact = action.compact()
        if pre_action_is_threat:
            if action.kind == "ATTACK":
                to_player = to_int(action.params.get("to_player"), 0)
                to_jace = to_int(action.params.get("to_jace"), 0)
                attackers = max(0, to_player + to_jace)
                draw_burst_cost = 2 * attackers
                damage = OVERLORD_POWER * max(0, to_player)
                declared_lethal = damage >= pre_defender_life and to_player > 0
                features["threat_declared_attack_actions"] = to_int(features["threat_declared_attack_actions"]) + 1
                features["threat_declared_attackers_total"] = to_int(features["threat_declared_attackers_total"]) + attackers
                features["threat_declared_attackers_to_player"] = to_int(features["threat_declared_attackers_to_player"]) + max(0, to_player)
                features["threat_declared_attack_draw_cost_total"] = to_int(features["threat_declared_attack_draw_cost_total"]) + draw_burst_cost
                if declared_lethal:
                    features["threat_declared_lethal_attack_actions"] = to_int(features["threat_declared_lethal_attack_actions"]) + 1
            elif action.kind == "PASS" and str(state.frame) == "ATTACK":
                features["threat_pass_attack_actions"] = to_int(features["threat_pass_attack_actions"]) + 1
            elif action.kind == "CAST" and str(action.params.get("card", "")) == CARD_OVERLORD:
                draw_burst_cost = 2
                features["threat_overlord_cast_draw_events"] = to_int(features["threat_overlord_cast_draw_events"]) + 1
            elif action.kind == "ACTIVATE_JACE":
                mode = str(action.params.get("mode", ""))
                target = str(action.params.get("target_player", ""))
                if mode == "zero":
                    draw_burst_cost = 3
                    features["threat_jace_zero_actions"] = to_int(features["threat_jace_zero_actions"]) + 1
                    if pre_actor_library <= 10:
                        features["threat_jace_zero_at_library_le_10"] = to_int(features["threat_jace_zero_at_library_le_10"]) + 1
                elif mode == "ultimate":
                    key = "threat_ultimate_opponent_actions" if target == "opponent" else "threat_ultimate_self_actions"
                    features[key] = to_int(features[key]) + 1
            if draw_burst_cost > 0:
                features["threat_min_library_before_draw_burst"] = min(to_int(features["threat_min_library_before_draw_burst"], 9999), pre_actor_library)
        apply_decision_index(state, frame, action_index, transition_rng)
        features["decisions"] = int(step)
        if pre_action_is_threat and state.winner is not None and state.winner == int(target_seat) and f"player_{threat_seat}_attempted_to_draw_from_empty_library" == state.loss_reason:
            features["threat_last_action_before_loss"] = action_compact
            if action.kind == "ATTACK":
                features["threat_selfdeck_on_attack_trigger"] = 1
                if declared_lethal:
                    features["threat_selfdeck_on_declared_lethal_attack"] = 1
            elif action.kind == "CAST" and str(action.params.get("card", "")) == CARD_OVERLORD:
                features["threat_selfdeck_on_overlord_cast"] = 1
            elif action.kind == "ACTIVATE_JACE" and str(action.params.get("mode", "")) == "zero":
                features["threat_selfdeck_on_jace_zero"] = 1
    if state.winner is None:
        state.frame = "GAME_OVER"
        state.loss_reason = "max_decisions_reached"
    target_score = 0.5 if state.winner is None else (1.0 if state.winner == int(target_seat) else 0.0)
    threat_score = 0.5 if state.winner is None else (1.0 if state.winner == int(threat_seat) else 0.0)
    if to_int(features["threat_min_library_before_draw_burst"], 9999) == 9999:
        features["threat_min_library_before_draw_burst"] = ""
    features.update(
        {
            "winner": "None" if state.winner is None else str(state.winner),
            "loss_reason": state.loss_reason,
            "target_score": target_score,
            "threat_score": threat_score,
            "threat_final_library": len(state.players[int(threat_seat)].library),
            "target_final_library": len(state.players[int(target_seat)].library),
            "threat_final_life": int(state.players[int(threat_seat)].life),
            "target_final_life": int(state.players[int(target_seat)].life),
            "threat_loss_vector": "selfdeck" if f"player_{threat_seat}_attempted_to_draw_from_empty_library" == state.loss_reason else ("life_total" if f"player_{threat_seat}_life_total_zero_or_less" == state.loss_reason else "other"),
        }
    )
    return features


def summarize_threat_closure_features(rows: Sequence[Mapping[str, Any]], *, group_keys: Sequence[str]) -> list[dict[str, object]]:
    buckets: dict[tuple[object, ...], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[tuple(row.get(k, "") for k in group_keys)].append(row)
    numeric = (
        "target_score",
        "threat_score",
        "decisions",
        "threat_declared_attack_actions",
        "threat_declared_attackers_total",
        "threat_declared_attackers_to_player",
        "threat_declared_attack_draw_cost_total",
        "threat_declared_lethal_attack_actions",
        "threat_selfdeck_on_attack_trigger",
        "threat_selfdeck_on_declared_lethal_attack",
        "threat_overlord_cast_draw_events",
        "threat_selfdeck_on_overlord_cast",
        "threat_jace_zero_actions",
        "threat_jace_zero_at_library_le_10",
        "threat_selfdeck_on_jace_zero",
        "threat_ultimate_self_actions",
        "threat_ultimate_opponent_actions",
        "threat_pass_attack_actions",
        "threat_final_library",
        "target_final_library",
        "threat_final_life",
        "target_final_life",
    )
    out: list[dict[str, object]] = []
    for group, group_rows in sorted(buckets.items()):
        row: dict[str, object] = {k: v for k, v in zip(group_keys, group)}
        row["games"] = len(group_rows)
        for field in numeric:
            vals = [to_float(r.get(field), 0.0) for r in group_rows]
            row[f"mean_{field}"] = mean(vals) if vals else 0.0
            if field.startswith("threat_selfdeck") or field in {"threat_jace_zero_at_library_le_10", "threat_ultimate_self_actions"}:
                row[f"sum_{field}"] = int(sum(vals))
        row["target_wins"] = int(sum(1 for r in group_rows if to_float(r.get("target_score"), 0.5) > 0.5))
        row["threat_wins"] = int(sum(1 for r in group_rows if to_float(r.get("threat_score"), 0.5) > 0.5))
        row["threat_selfdeck_losses"] = int(sum(1 for r in group_rows if str(r.get("threat_loss_vector")) == "selfdeck" and to_float(r.get("target_score"), 0.5) > 0.5))
        out.append(row)
    return out


def compare_threat_closure_by_life(summary_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, object]]:
    """Compare legacy vs guarded threat policies, failing closed if a row is absent."""

    by: dict[tuple[str, str, int], Mapping[str, Any]] = {}
    for row in summary_rows:
        by[(str(row.get("target_size_axis", "")), str(row.get("policy_axis", "")), to_int(row.get("starting_life"), 0))] = row
    cells = sorted({(axis, life) for (axis, _policy, life) in by if axis and life})
    required_axes = ("legacy_threat_rush", "library_aware_threat_closure")
    out: list[dict[str, object]] = []
    for axis, life in cells:
        rows_by_policy = {policy: by.get((axis, policy, life)) for policy in required_axes}
        missing = [policy for policy, row in rows_by_policy.items() if row is None]
        if missing:
            out.append(
                {
                    "target_size_axis": axis,
                    "starting_life": life,
                    "legacy_inert_target_score": None,
                    "guarded_inert_target_score": None,
                    "closure_guard_target_score_delta_guarded_minus_legacy": None,
                    "legacy_threat_selfdeck_event_rate": None,
                    "guarded_threat_selfdeck_event_rate": None,
                    "legacy_mean_jace_zero": None,
                    "guarded_mean_jace_zero": None,
                    "legacy_mean_attackers_to_player": None,
                    "guarded_mean_attackers_to_player": None,
                    "missing_policy_axes": missing,
                    "provisional_read": "incomplete_matrix",
                }
            )
            continue

        legacy = rows_by_policy["legacy_threat_rush"]
        guarded = rows_by_policy["library_aware_threat_closure"]
        assert legacy is not None and guarded is not None
        legacy_target = to_float(legacy.get("mean_target_score"), 0.0)
        guarded_target = to_float(guarded.get("mean_target_score"), 0.0)
        legacy_selfdeck = to_float(legacy.get("mean_threat_selfdeck_on_attack_trigger"), 0.0) + to_float(legacy.get("mean_threat_selfdeck_on_overlord_cast"), 0.0) + to_float(legacy.get("mean_threat_selfdeck_on_jace_zero"), 0.0)
        guarded_selfdeck = to_float(guarded.get("mean_threat_selfdeck_on_attack_trigger"), 0.0) + to_float(guarded.get("mean_threat_selfdeck_on_overlord_cast"), 0.0) + to_float(guarded.get("mean_threat_selfdeck_on_jace_zero"), 0.0)
        out.append(
            {
                "target_size_axis": axis,
                "starting_life": life,
                "legacy_inert_target_score": legacy_target,
                "guarded_inert_target_score": guarded_target,
                "closure_guard_target_score_delta_guarded_minus_legacy": guarded_target - legacy_target,
                "legacy_threat_selfdeck_event_rate": legacy_selfdeck,
                "guarded_threat_selfdeck_event_rate": guarded_selfdeck,
                "legacy_mean_jace_zero": to_float(legacy.get("mean_threat_jace_zero_actions"), 0.0),
                "guarded_mean_jace_zero": to_float(guarded.get("mean_threat_jace_zero_actions"), 0.0),
                "legacy_mean_attackers_to_player": to_float(legacy.get("mean_threat_declared_attackers_to_player"), 0.0),
                "guarded_mean_attackers_to_player": to_float(guarded.get("mean_threat_declared_attackers_to_player"), 0.0),
                "missing_policy_axes": [],
                "provisional_read": (
                    "guard_reduces_inert_edge" if guarded_target + 0.15 < legacy_target else
                    "guard_not_enough" if guarded_target >= legacy_target - 0.05 else
                    "small_guard_improvement"
                ),
            }
        )
    return out


def threat_closure_gate_report(summary: Mapping[str, object], rows: Sequence[Mapping[str, object]], *, min_games: int = 96) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    if int(summary.get("games", 0)) < int(min_games):
        errors.append(f"fewer than {min_games} threat-closure games")
    if int(summary.get("truncations", 0)) != 0:
        errors.append("terminal-clean gate failed: truncations present")
    if int(summary.get("python_errors", 0)) != 0:
        errors.append("python errors occurred during C++ shadow rollout")
    if int(summary.get("closure_feature_games", 0)) != int(summary.get("games", -1)):
        errors.append("closure feature rerun did not cover every game")
    cpp = summary.get("cpp_shadow_summary", {})
    if isinstance(cpp, Mapping):
        if int(cpp.get("mismatches", 0)) != 0:
            errors.append("C++ shadow mismatches present")
        if int(cpp.get("skipped_events", 0)) != 0:
            warnings.append("C++ shadow skipped events present")
    required_policies = {"legacy_threat_rush", "library_aware_threat_closure"}
    present_policies = {str(r.get("policy_axis")) for r in rows}
    missing = required_policies - present_policies
    for policy in sorted(missing):
        errors.append(f"required policy missing: {policy}")
    return {"passed": not errors, "errors": errors, "warnings": warnings}
