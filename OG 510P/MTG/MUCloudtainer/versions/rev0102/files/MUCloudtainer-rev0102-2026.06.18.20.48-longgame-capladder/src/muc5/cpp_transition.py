from __future__ import annotations

import shutil
import subprocess
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

from .action_schema import Action
from .cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_ORDER, CARD_OVERLORD
from .engine import GameState


@dataclass(frozen=True)
class CppTransitionToolStatus:
    gpp: str | None
    source_exists: bool
    binary_exists: bool
    usable: bool
    error: str | None = None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class TransitionMicroRecord:
    """Flat one-action transition record for the C++ microkernel.

    Rev0018 deliberately carries ordered library state and pending-choice state.
    That makes the differential harness stricter: C++ can now be checked on stack
    resolution and agent-facing choice transitions, not only on visible counts.
    Python remains authoritative; this record is just a transport for one stable
    micro-transition at a time.
    """

    case_id: str
    action_kind: str
    action_card: str
    action_mode: str
    action_payment: str
    action_pitch: str
    action_target_id: int
    action_target_player: str
    action_target_state: str
    action_to_player: int
    action_to_jace: int
    action_block_player: int
    action_block_jace: int
    action_effect: str
    action_discard: str
    action_put: str
    action_first_draw: str
    action_second_draw: str
    action_keep: str
    action_shuffle_csv: str
    pending_choice_player: int
    pending_choice_kind: str
    pending_choice_resume: str
    pending_choice_remaining: int
    pending_choice_triggers_remaining: int
    pending_choice_target_player: int
    pending_choice_old_loyalty: int
    pending_choice_old_used: int
    pending_choice_new_loyalty: int
    p0_library_csv: str
    p1_library_csv: str
    frame: str
    main_phase: str
    active_player: int
    priority_player: int
    actor: int
    land_played: int
    consecutive_passes: int
    next_spell_id: int
    pre_stack_frame: str
    winner: int
    pending_combat_attacker: int
    pending_combat_defender: int
    pending_combat_to_player: int
    pending_combat_to_jace: int
    stack_ids_csv: str
    stack_controllers_csv: str
    stack_cards_csv: str
    stack_modes_csv: str
    stack_target_ids_csv: str
    p0: str
    p1: str

    def to_tsv(self) -> str:
        return "\t".join(str(v) for v in asdict(self).values())


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def transition_source_path() -> Path:
    return project_root() / "cpp" / "muc5_transition_micro.cpp"


def transition_binary_path() -> Path:
    return project_root() / "build" / "muc5_transition_micro"


def build_transition_binary(*, force: bool = False) -> Path:
    src = transition_source_path()
    out = transition_binary_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    gpp = shutil.which("g++")
    if not gpp:
        raise RuntimeError("g++ not available in this cloudtainer")
    if not src.exists():
        raise RuntimeError(f"C++ transition source missing: {src}")
    if force or not out.exists() or src.stat().st_mtime > out.stat().st_mtime:
        cmd = [gpp, "-O3", "-std=c++17", str(src), "-o", str(out)]
        subprocess.run(cmd, cwd=str(project_root()), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return out


def cpp_transition_tool_status(*, try_build: bool = True) -> CppTransitionToolStatus:
    err: str | None = None
    usable = False
    try:
        if try_build:
            build_transition_binary()
        usable = transition_binary_path().exists()
    except Exception as exc:
        err = repr(exc)
    return CppTransitionToolStatus(
        gpp=shutil.which("g++"),
        source_exists=transition_source_path().exists(),
        binary_exists=transition_binary_path().exists(),
        usable=usable,
        error=err,
    )


def _csv(items: Iterable[object]) -> str:
    return ",".join(str(x) for x in items)


def _player_blob(state: GameState, idx: int) -> str:
    p = state.players[idx]
    library_counts = Counter(p.library)
    fields: list[object] = [
        p.life,
        p.mulligans_taken,
        len(p.library),
    ]
    for zone in (p.hand, p.graveyard, p.exile, library_counts):
        for card in CARD_ORDER:
            fields.append(int(zone.get(card, 0)))
    fields.extend(
        [
            p.islands_untapped,
            p.islands_tapped,
            -1 if p.jace_loyalty is None else int(p.jace_loyalty),
            1 if p.jace_used_this_turn else 0,
            p.overlord_ready,
            p.overlord_sick,
            p.overlord_tapped,
            p.impending_4,
            p.impending_3,
            p.impending_2,
            p.impending_1,
        ]
    )
    return ":".join(str(x) for x in fields)


def _library_csv(state: GameState, idx: int) -> str:
    # Engine convention: top of library is list[-1]. We preserve the exact
    # bottom-to-top order so C++ can draw/pop and Jace can bottom/top cards.
    return _csv(state.players[idx].library)


def _stack_parts(state: GameState) -> tuple[str, str, str, str, str]:
    ids: list[int] = []
    controllers: list[int] = []
    cards: list[str] = []
    modes: list[str] = []
    target_ids: list[int] = []
    for spell in state.stack:
        ids.append(int(spell.spell_id))
        controllers.append(int(spell.controller))
        cards.append(str(spell.card))
        modes.append(str(spell.mode))
        target_ids.append(int(spell.params.get("target_id", -1)))
    return _csv(ids), _csv(controllers), _csv(cards), _csv(modes), _csv(target_ids)


def _pending_fields(state: GameState) -> dict[str, object]:
    pc = state.pending_choice
    if pc is None:
        return {
            "pending_choice_player": -1,
            "pending_choice_kind": "",
            "pending_choice_resume": "",
            "pending_choice_remaining": 0,
            "pending_choice_triggers_remaining": 0,
            "pending_choice_target_player": -1,
            "pending_choice_old_loyalty": -1,
            "pending_choice_old_used": 0,
            "pending_choice_new_loyalty": -1,
        }
    data = pc.data
    return {
        "pending_choice_player": int(pc.player),
        "pending_choice_kind": str(pc.kind),
        "pending_choice_resume": str(data.get("resume", "")),
        "pending_choice_remaining": int(data.get("remaining", 0)),
        "pending_choice_triggers_remaining": int(data.get("overlord_triggers_remaining", 0)),
        "pending_choice_target_player": int(data.get("target_player", -1)),
        "pending_choice_old_loyalty": int(data.get("old_loyalty", -1)),
        "pending_choice_old_used": 1 if bool(data.get("old_used", False)) else 0,
        "pending_choice_new_loyalty": int(data.get("new_loyalty", -1)),
    }




def with_jace_ultimate_shuffle_transport(pre_state: GameState, action: Action, post_state: GameState) -> Action:
    """Return an action clone carrying explicit Jace-ultimate shuffle output.

    Jace ultimate shuffles the target player's hand into their new library. The
    Python engine remains authoritative for RNG. C++ differential checking should
    consume the resulting ordered library as an explicit transcript rather than
    trying to reproduce Python's random-number stream.
    """

    if action.kind != "ACTIVATE_JACE" or action.params.get("mode") != "ultimate":
        return action
    actor = pre_state.current_player()
    target = actor if action.params.get("target_player") == "self" else 1 - actor
    params = dict(action.params)
    params["cpp_shuffle_csv"] = _csv(post_state.players[target].library)
    return Action(action.kind, params)


def has_jace_ultimate_shuffle_transport(action: Action) -> bool:
    return action.kind == "ACTIVATE_JACE" and action.params.get("mode") == "ultimate" and "cpp_shuffle_csv" in action.params

def transition_record_from_state_action(state: GameState, action: Action, case_id: str) -> TransitionMicroRecord:
    if not is_supported_transition(state, action):
        raise ValueError(f"unsupported transition for C++ microkernel: frame={state.frame} action={action.compact()}")
    actor = state.current_player()
    stack_ids, stack_controllers, stack_cards, stack_modes, stack_target_ids = _stack_parts(state)
    pc_attacker = pc_defender = pc_to_player = pc_to_jace = -1
    if state.pending_combat is not None:
        pc_attacker = int(state.pending_combat.attacker)
        pc_defender = int(state.pending_combat.defender)
        pc_to_player = int(state.pending_combat.to_player)
        pc_to_jace = int(state.pending_combat.to_jace)
    params = action.params
    pf = _pending_fields(state)
    return TransitionMicroRecord(
        case_id=case_id,
        action_kind=str(action.kind),
        action_card=str(params.get("card", "")),
        action_mode=str(params.get("mode", "")),
        action_payment=str(params.get("payment", "")),
        action_pitch=str(params.get("pitch_card", "")),
        action_target_id=int(params.get("target_id", -1)),
        action_target_player=str(params.get("target_player", "")),
        action_target_state=str(params.get("target_state", "")),
        action_to_player=int(params.get("to_player", 0)),
        action_to_jace=int(params.get("to_jace", 0)),
        action_block_player=int(params.get("block_player_attackers", 0)),
        action_block_jace=int(params.get("block_jace_attackers", 0)),
        action_effect=str(params.get("effect", "")),
        action_discard=str(params.get("discard", "")),
        action_put=str(params.get("put", "")),
        action_first_draw=str(params.get("first_draw", "")),
        action_second_draw=str(params.get("second_draw", "")),
        action_keep=str(params.get("keep", "")),
        action_shuffle_csv=str(params.get("cpp_shuffle_csv", "")),
        pending_choice_player=int(pf["pending_choice_player"]),
        pending_choice_kind=str(pf["pending_choice_kind"]),
        pending_choice_resume=str(pf["pending_choice_resume"]),
        pending_choice_remaining=int(pf["pending_choice_remaining"]),
        pending_choice_triggers_remaining=int(pf["pending_choice_triggers_remaining"]),
        pending_choice_target_player=int(pf["pending_choice_target_player"]),
        pending_choice_old_loyalty=int(pf["pending_choice_old_loyalty"]),
        pending_choice_old_used=int(pf["pending_choice_old_used"]),
        pending_choice_new_loyalty=int(pf["pending_choice_new_loyalty"]),
        p0_library_csv=_library_csv(state, 0),
        p1_library_csv=_library_csv(state, 1),
        frame=str(state.frame),
        main_phase=str(state.main_phase),
        active_player=int(state.active_player),
        priority_player=-1 if state.priority_player is None else int(state.priority_player),
        actor=int(actor),
        land_played=1 if state.land_played_this_turn else 0,
        consecutive_passes=int(state.consecutive_passes),
        next_spell_id=int(state.next_spell_id),
        pre_stack_frame=str(state.pre_stack_frame),
        winner=-1 if state.winner is None else int(state.winner),
        pending_combat_attacker=pc_attacker,
        pending_combat_defender=pc_defender,
        pending_combat_to_player=pc_to_player,
        pending_combat_to_jace=pc_to_jace,
        stack_ids_csv=stack_ids,
        stack_controllers_csv=stack_controllers,
        stack_cards_csv=stack_cards,
        stack_modes_csv=stack_modes,
        stack_target_ids_csv=stack_target_ids,
        p0=_player_blob(state, 0),
        p1=_player_blob(state, 1),
    )


def is_supported_transition(state: GameState, action: Action) -> bool:
    if state.winner is not None:
        return False
    if state.pending_choice is not None:
        # These are all agent-facing choices, but not all are strategically equal.
        # Rev0018 covers the deterministic transitions and exact ordered-library
        # count changes. Jace ultimate remains excluded because it shuffles.
        return action.kind == "CHOOSE_FOR_EFFECT" and state.pending_choice.kind in {
            "discard",
            "cleanup_discard",
            "jace_plus2",
            "jace_brainstorm_putback",
            "jace_legend",
        }
    if action.kind == "PLAY_ISLAND" and state.frame == "MAIN":
        return True
    if action.kind == "CAST":
        card = action.params.get("card")
        if state.frame == "MAIN" and card in {CARD_JACE, CARD_OVERLORD}:
            return True
        if state.frame == "RESPONSE" and card in {CARD_COUNTERSPELL, CARD_FORCE}:
            return True
    if action.kind == "ACTIVATE_JACE" and state.frame == "MAIN":
        mode = action.params.get("mode")
        if mode in {"plus2", "zero", "minus1"}:
            return True
        if mode == "ultimate" and has_jace_ultimate_shuffle_transport(action):
            # Random shuffle output is supplied as an explicit transcript by the
            # Python reference engine. Legal menus do not carry this field; only
            # differential/replay checking actions do.
            return True
    if action.kind == "PASS" and state.frame == "RESPONSE":
        # Rev0018 adds stack pass/resolve, including Counterspell/Force, Jace,
        # and Overlord draw-discard entry triggers.
        return True
    if action.kind == "PASS" and state.frame == "MAIN" and state.main_phase in {"precombat", "postcombat"}:
        # Precombat just moves to ATTACK; postcombat may end the turn if cleanup
        # does not require discard. Cleanup discard is represented by a pending
        # choice and is covered separately.
        return True
    if action.kind == "PASS" and state.frame == "ATTACK":
        return True
    if action.kind == "ATTACK" and state.frame == "ATTACK":
        return True
    if state.frame == "BLOCK" and action.kind in {"PASS", "BLOCK"}:
        return True
    return False


def state_signature(state: GameState) -> str:
    stack_ids, stack_controllers, stack_cards, stack_modes, stack_target_ids = _stack_parts(state)
    pc_attacker = pc_defender = pc_to_player = pc_to_jace = -1
    if state.pending_combat is not None:
        pc_attacker = int(state.pending_combat.attacker)
        pc_defender = int(state.pending_combat.defender)
        pc_to_player = int(state.pending_combat.to_player)
        pc_to_jace = int(state.pending_combat.to_jace)
    pf = _pending_fields(state)
    fields: list[object] = [
        "SIGv2",
        state.frame,
        state.main_phase,
        state.active_player,
        -1 if state.priority_player is None else state.priority_player,
        1 if state.land_played_this_turn else 0,
        state.consecutive_passes,
        state.next_spell_id,
        state.pre_stack_frame,
        -1 if state.winner is None else state.winner,
        pc_attacker,
        pc_defender,
        pc_to_player,
        pc_to_jace,
        pf["pending_choice_player"],
        pf["pending_choice_kind"],
        pf["pending_choice_resume"],
        pf["pending_choice_remaining"],
        pf["pending_choice_triggers_remaining"],
        pf["pending_choice_target_player"],
        pf["pending_choice_old_loyalty"],
        pf["pending_choice_old_used"],
        pf["pending_choice_new_loyalty"],
        stack_ids,
        stack_controllers,
        stack_cards,
        stack_modes,
        stack_target_ids,
        _library_csv(state, 0),
        _library_csv(state, 1),
        _player_blob(state, 0),
        _player_blob(state, 1),
    ]
    return "|".join(str(x) for x in fields)


def cpp_transition_signatures(records: Sequence[TransitionMicroRecord], *, force_build: bool = False) -> list[str]:
    exe = build_transition_binary(force=force_build)
    payload = "\n".join(r.to_tsv() for r in records) + ("\n" if records else "")
    proc = subprocess.run(
        [str(exe)],
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
        cwd=str(project_root()),
    )
    lines = proc.stdout.splitlines()
    if len(lines) != len(records):
        raise RuntimeError(f"C++ transition returned {len(lines)} rows for {len(records)} records; stderr={proc.stderr}")
    return lines


def diff_transition_records(records: Sequence[TransitionMicroRecord], expected_signatures: Sequence[str]) -> list[dict[str, object]]:
    actual = cpp_transition_signatures(records)
    diffs: list[dict[str, object]] = []
    for i, (got, want) in enumerate(zip(actual, expected_signatures)):
        if got != want:
            diffs.append({"index": i, "case_id": records[i].case_id, "expected": want, "actual": got, "record": asdict(records[i])})
    return diffs
