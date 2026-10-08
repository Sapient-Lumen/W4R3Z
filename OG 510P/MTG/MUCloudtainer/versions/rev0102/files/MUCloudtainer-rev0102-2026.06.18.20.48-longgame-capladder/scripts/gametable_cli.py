from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.deckspace import DeckVector
from src.muc5.gametable import MUC5GameTable, SeatSpec, load_table, save_table
from src.muc5.mulligan import MULLIGAN_POLICY_NAMES

SEED_DECKS_PATH = ROOT / "data" / "seed_decks.json"
AGENT_NAMES = ("random", "heuristic", "counter_happy", "threat_rush")


def load_seed_deck_map() -> Dict[str, DeckVector]:
    payload = json.loads(SEED_DECKS_PATH.read_text())
    out: Dict[str, DeckVector] = {}
    for row in payload["seed_decks"]:
        c = row["counts"]
        deck = DeckVector(
            int(row["size"]),
            int(c.get("Island", 0)),
            int(c.get("Counterspell", 0)),
            int(c.get("ForceOfWill", 0)),
            int(c.get("JaceTheMindSculptor", 0)),
            int(c.get("OverlordOfTheFloodpits", 0)),
        )
        deck.validate()
        out[row["name"]] = deck
    return out


def parse_deck(spec: str) -> DeckVector:
    seeds = load_seed_deck_map()
    if spec in seeds:
        return seeds[spec]
    parts = [p.strip() for p in spec.replace(":", ",").split(",") if p.strip()]
    if len(parts) == 6:
        deck = DeckVector(*(int(x) for x in parts))
        deck.validate()
        return deck
    raise ValueError(
        f"unknown deck {spec!r}. Use a seed deck name or a literal 'size,island,counterspell,force,jace,overlord'."
    )


def parse_seat(spec: str) -> SeatSpec:
    normalized = spec.strip().lower().replace("-", "_")
    if normalized in {"external", "assistant", "me"}:
        return SeatSpec.external("assistant_external")
    if normalized in AGENT_NAMES:
        return SeatSpec.from_agent_name(normalized)
    raise ValueError(f"unknown seat {spec!r}; expected external or one of {AGENT_NAMES}")


def add_common_render_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--reveal", action="store_true", help="debug: reveal opponent hidden hand/library sample")
    parser.add_argument("--tail", type=int, default=10, help="number of transcript lines to print")


def cmd_list_decks(_args: argparse.Namespace) -> None:
    for name, deck in load_seed_deck_map().items():
        print(f"{name}: {deck.as_tuple()}")


def cmd_list_agents(_args: argparse.Namespace) -> None:
    print("external")
    for name in AGENT_NAMES:
        print(name)


def cmd_new(args: argparse.Namespace) -> None:
    table = MUC5GameTable(
        parse_deck(args.deck0),
        parse_deck(args.deck1),
        seats=(parse_seat(args.seat0), parse_seat(args.seat1)),
        seed=args.seed,
        starting_player=args.starting_player,
        starting_life=args.life,
        mulligan_policy=args.mulligan_policy,
        max_decisions=args.max_decisions,
    ).start()
    if args.save:
        save_table(table, args.save)
    perspective = args.perspective if args.perspective is not None else None
    print(table.render_markdown(perspective, reveal_hidden=args.reveal, transcript_tail=args.tail))
    if args.save:
        print(f"Saved table: {args.save}")


def cmd_show(args: argparse.Namespace) -> None:
    table = load_table(args.load)
    print(table.render_markdown(args.perspective, reveal_hidden=args.reveal, transcript_tail=args.tail))


def cmd_act(args: argparse.Namespace) -> None:
    table = load_table(args.load)
    table.apply_external_action(args.action)
    out = args.save or args.load
    save_table(table, out)
    print(table.render_markdown(args.perspective, reveal_hidden=args.reveal, transcript_tail=args.tail))
    print(f"Saved table: {out}")


def cmd_snapshot(args: argparse.Namespace) -> None:
    table = load_table(args.load)
    snap = table.snapshot(args.perspective, transcript_tail=args.tail).to_dict()
    print(json.dumps(snap, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Assistant-facing MUC-5 gametable CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list-decks")
    p.set_defaults(func=cmd_list_decks)

    p = sub.add_parser("list-agents")
    p.set_defaults(func=cmd_list_agents)

    p = sub.add_parser("new")
    p.add_argument("--deck0", default="forty_force_jace_pressure")
    p.add_argument("--deck1", default="sixty_overlord_heavy")
    p.add_argument("--seat0", default="external")
    p.add_argument("--seat1", default="heuristic")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--starting-player", type=int, choices=(0, 1), default=0)
    p.add_argument("--life", type=int, choices=(20, 40), default=20)
    p.add_argument("--mulligan-policy", choices=MULLIGAN_POLICY_NAMES, default="land_band")
    p.add_argument("--max-decisions", type=int, default=500)
    p.add_argument("--save", default="/tmp/muc5_gametable.pkl")
    p.add_argument("--perspective", type=int, choices=(0, 1), default=None)
    add_common_render_args(p)
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("show")
    p.add_argument("--load", required=True)
    p.add_argument("--perspective", type=int, choices=(0, 1), default=None)
    add_common_render_args(p)
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("act")
    p.add_argument("--load", required=True)
    p.add_argument("--action", type=int, required=True)
    p.add_argument("--save", default=None)
    p.add_argument("--perspective", type=int, choices=(0, 1), default=None)
    add_common_render_args(p)
    p.set_defaults(func=cmd_act)

    p = sub.add_parser("snapshot")
    p.add_argument("--load", required=True)
    p.add_argument("--perspective", type=int, choices=(0, 1), default=None)
    p.add_argument("--tail", type=int, default=10)
    p.set_defaults(func=cmd_snapshot)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
