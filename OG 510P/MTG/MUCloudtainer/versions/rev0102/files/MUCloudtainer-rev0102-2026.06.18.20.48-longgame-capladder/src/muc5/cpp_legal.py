from __future__ import annotations

import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from .cards import (
    CARD_COUNTERSPELL,
    CARD_FORCE,
    CARD_ISLAND,
    CARD_JACE,
    CARD_OVERLORD,
)
from .engine import GameState, StackSpell, legal_actions


@dataclass(frozen=True)
class CppLegalToolStatus:
    gpp: str | None
    source_exists: bool
    binary_exists: bool
    usable: bool
    error: str | None = None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class LegalMenuRecord:
    """Flat state summary consumed by the C++ legal-menu oracle.

    This is intentionally narrower than GameState. It contains only the fields
    the stable MUC-5 macro-action generator needs. Python remains authoritative;
    the C++ tool is a differential port target for the long-haul referee.
    """

    frame: str
    main_phase: str
    pending_kind: str
    land_played: int
    h_island: int
    h_counter: int
    h_force: int
    h_jace: int
    h_overlord: int
    untapped: int
    life: int
    jace_loyalty: int
    jace_used: int
    self_ready: int
    self_sick: int
    self_tapped: int
    opp_jace_loyalty: int
    opp_ready: int
    opp_sick: int
    opp_tapped: int
    stack_ids_csv: str
    stack_cards_csv: str
    combat_to_player: int
    combat_to_jace: int
    defender_ready: int

    def to_tsv(self) -> str:
        return "\t".join(str(v) for v in asdict(self).values())


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def legal_menu_source_path() -> Path:
    return project_root() / "cpp" / "muc5_legal_menu.cpp"


def legal_menu_binary_path() -> Path:
    return project_root() / "build" / "muc5_legal_menu"


def build_legal_menu_binary(*, force: bool = False) -> Path:
    src = legal_menu_source_path()
    out = legal_menu_binary_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    gpp = shutil.which("g++")
    if not gpp:
        raise RuntimeError("g++ not available in this cloudtainer")
    if not src.exists():
        raise RuntimeError(f"C++ legal-menu source missing: {src}")
    if force or not out.exists() or src.stat().st_mtime > out.stat().st_mtime:
        cmd = [gpp, "-O3", "-std=c++17", str(src), "-o", str(out)]
        subprocess.run(cmd, cwd=str(project_root()), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return out


def cpp_legal_tool_status(*, try_build: bool = True) -> CppLegalToolStatus:
    err: str | None = None
    usable = False
    try:
        if try_build:
            build_legal_menu_binary()
        usable = legal_menu_binary_path().exists()
    except Exception as exc:  # status reporting must not explode audits
        err = repr(exc)
    return CppLegalToolStatus(
        gpp=shutil.which("g++"),
        source_exists=legal_menu_source_path().exists(),
        binary_exists=legal_menu_binary_path().exists(),
        usable=usable,
        error=err,
    )


def _stack_csv(stack: Sequence[StackSpell]) -> Tuple[str, str]:
    return ",".join(str(s.spell_id) for s in stack), ",".join(str(s.card) for s in stack)


def legal_record_from_state(state: GameState) -> LegalMenuRecord:
    actor = state.current_player()
    player = state.players[actor]
    opponent = state.players[state.opponent(actor)]
    stack_ids, stack_cards = _stack_csv(state.stack)
    pending_kind = "" if state.pending_choice is None else str(state.pending_choice.kind)
    combat_to_player = 0
    combat_to_jace = 0
    defender_ready = player.overlord_ready
    if state.pending_combat is not None:
        combat_to_player = int(state.pending_combat.to_player)
        combat_to_jace = int(state.pending_combat.to_jace)
        defender_ready = int(player.overlord_ready)
    return LegalMenuRecord(
        frame=str(state.frame),
        main_phase=str(state.main_phase),
        pending_kind=pending_kind,
        land_played=1 if state.land_played_this_turn else 0,
        h_island=player.hand_count(CARD_ISLAND),
        h_counter=player.hand_count(CARD_COUNTERSPELL),
        h_force=player.hand_count(CARD_FORCE),
        h_jace=player.hand_count(CARD_JACE),
        h_overlord=player.hand_count(CARD_OVERLORD),
        untapped=int(player.islands_untapped),
        life=int(player.life),
        jace_loyalty=-1 if player.jace_loyalty is None else int(player.jace_loyalty),
        jace_used=1 if player.jace_used_this_turn else 0,
        self_ready=int(player.overlord_ready),
        self_sick=int(player.overlord_sick),
        self_tapped=int(player.overlord_tapped),
        opp_jace_loyalty=-1 if opponent.jace_loyalty is None else int(opponent.jace_loyalty),
        opp_ready=int(opponent.overlord_ready),
        opp_sick=int(opponent.overlord_sick),
        opp_tapped=int(opponent.overlord_tapped),
        stack_ids_csv=stack_ids,
        stack_cards_csv=stack_cards,
        combat_to_player=combat_to_player,
        combat_to_jace=combat_to_jace,
        defender_ready=defender_ready,
    )


def python_legal_menu_strings(state: GameState) -> Tuple[str, ...]:
    return tuple(a.compact() for a in legal_actions(state))


def cpp_legal_menus(records: Sequence[LegalMenuRecord], *, force_build: bool = False) -> List[Tuple[str, ...]]:
    exe = build_legal_menu_binary(force=force_build)
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
    menus: List[Tuple[str, ...]] = []
    for line in proc.stdout.splitlines():
        if line.strip() == "":
            menus.append(tuple())
        else:
            menus.append(tuple(line.split("||")))
    if len(menus) != len(records):
        raise RuntimeError(f"C++ legal menu returned {len(menus)} rows for {len(records)} records")
    return menus


def diff_legal_menus(records: Sequence[LegalMenuRecord], expected: Sequence[Sequence[str]]) -> List[dict[str, object]]:
    actual = cpp_legal_menus(records)
    diffs: List[dict[str, object]] = []
    for i, (got, want) in enumerate(zip(actual, expected)):
        want_t = tuple(want)
        if got != want_t:
            diffs.append(
                {
                    "index": i,
                    "expected_count": len(want_t),
                    "actual_count": len(got),
                    "expected": list(want_t),
                    "actual": list(got),
                    "record": asdict(records[i]),
                }
            )
    return diffs
