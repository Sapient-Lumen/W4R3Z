#!/usr/bin/env python3
"""Build a small SQLite card catalog from local MTGSim card-definition JSON.

This is the first concrete DB hook for card metadata. It intentionally consumes
fictional/sample data by default; future importers can target MTGJSON/Scryfall
bulk exports without mixing Oracle text with engine rule conformance.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sqlite3
import time
from typing import Any

os.environ.setdefault("TZ", "America/New_York")
if hasattr(time, "tzset"):
    time.tzset()

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "cards" / "sample_cards.json"
DEFAULT_SCHEMA = ROOT / "data" / "cards" / "schema" / "card_catalog_schema.sql"
DEFAULT_DB = ROOT / "reports" / "cards" / "card_catalog.sqlite"
DEFAULT_REPORT = ROOT / "reports" / "cards" / "card_catalog_report_latest.json"

TYPE_MASKS = {
    "Artifact": 1 << 0,
    "Battle": 1 << 1,
    "Creature": 1 << 2,
    "Enchantment": 1 << 3,
    "Instant": 1 << 4,
    "Kindred": 1 << 5,
    "Land": 1 << 6,
    "Planeswalker": 1 << 7,
    "Sorcery": 1 << 8,
}
TARGET_MASKS = {"none": 0, "player": 1 << 0, "object": 1 << 1, "permanent": 1 << 1, "stack": 1 << 2, "spell": 1 << 2, "stack_object": 1 << 2, "any": (1 << 0) | (1 << 1)}
COLOR_MASKS = {
    "white": 1 << 0,
    "blue": 1 << 1,
    "black": 1 << 2,
    "red": 1 << 3,
    "green": 1 << 4,
}
ABILITY_MASKS = {
    "flying": 1 << 0,
    "reach": 1 << 1,
    "deathtouch": 1 << 2,
    "lifelink": 1 << 3,
    "vigilance": 1 << 4,
    "first_strike": 1 << 5,
    "firststrike": 1 << 5,
    "double_strike": 1 << 6,
    "doublestrike": 1 << 6,
    "trample": 1 << 7,
    "indestructible": 1 << 8,
    "haste": 1 << 9,
    "defender": 1 << 10,
    "hexproof": 1 << 11,
    "shroud": 1 << 12,
    "menace": 1 << 13,
    "flash": 1 << 14,
}
ATTACHMENT_KINDS = {"none", "aura", "equipment", "fortification"}
STATIC_EFFECT_SCOPES = {"source", "creatures_you_control", "creatures_opponents_control", "all_creatures", "permanents_you_control", "permanents_opponents_control", "all_permanents"}



def rel(path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def type_mask(types: list[str]) -> int:
    mask = 0
    for card_type in types:
        if card_type not in TYPE_MASKS:
            raise ValueError(f"unknown card type {card_type!r}")
        mask |= TYPE_MASKS[card_type]
    return mask


def ability_mask(keywords: list[str]) -> int:
    mask = 0
    for keyword in keywords:
        key = keyword.strip().lower()
        if not key:
            continue
        if key not in ABILITY_MASKS:
            raise ValueError(f"unknown keyword ability {keyword!r}")
        mask |= ABILITY_MASKS[key]
    return mask



def normalize_keyword_names(values: Any, *, field: str = "keywords") -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [part for part in values.replace("|", ",").split(",") if part]
    if not isinstance(values, list):
        raise ValueError(f"{field} must be a list or comma-separated string")
    out: list[str] = []
    for value in values:
        key = str(value).strip().lower()
        if not key:
            continue
        key = key.replace("-", "_").replace(" ", "_")
        if key not in ABILITY_MASKS:
            raise ValueError(f"unknown keyword ability {value!r}")
        if key not in out:
            out.append(key)
    return sorted(out)


def normalize_attachment_bonus(raw: Any) -> tuple[int, int]:
    if raw is None:
        return (0, 0)
    if isinstance(raw, str):
        token = raw.strip().lower().replace("+", "")
        if "/" not in token:
            raise ValueError("attachment bonus string must look like P/T")
        left, right = token.split("/", 1)
        return int(left), int(right)
    if isinstance(raw, list) and len(raw) == 2:
        return int(raw[0]), int(raw[1])
    if isinstance(raw, dict):
        return int(raw.get("power", raw.get("p", 0)) or 0), int(raw.get("toughness", raw.get("t", 0)) or 0)
    raise ValueError("attachment bonus must be a P/T string, two-item list, or object")

def normalize_loyalty_ability(raw: Any) -> dict[str, Any]:
    if raw is None or raw == {} or raw == "":
        return {"cost": 0, "kind": "none", "amount": 0, "target": "none"}
    if isinstance(raw, str):
        parts = raw.split(":")
        if len(parts) < 4:
            raise ValueError("loyalty ability string must be COST:KIND:AMOUNT:TARGET")
        return {"cost": int(parts[0]), "kind": parts[1].lower(), "amount": int(parts[2]), "target": parts[3].lower()}
    if isinstance(raw, dict):
        return {
            "cost": int(raw.get("cost", 0) or 0),
            "kind": str(raw.get("kind", raw.get("effect_kind", "none"))).lower(),
            "amount": int(raw.get("amount", raw.get("effect_amount", 0)) or 0),
            "target": str(raw.get("target", "none")).lower(),
        }
    raise ValueError("loyalty_ability must be an object or COST:KIND:AMOUNT:TARGET string")


def normalize_color_names(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [part for part in values.replace("|", ",").split(",") if part]
    if not isinstance(values, list):
        raise ValueError("colors must be a list or comma-separated string")
    out: list[str] = []
    for value in values:
        key = str(value).strip().lower()
        if not key:
            continue
        if key in {"w", "white"}:
            key = "white"
        elif key in {"u", "blue"}:
            key = "blue"
        elif key in {"b", "black"}:
            key = "black"
        elif key in {"r", "red"}:
            key = "red"
        elif key in {"g", "green"}:
            key = "green"
        else:
            raise ValueError(f"unknown color {value!r}")
        if key not in out:
            out.append(key)
    return sorted(out)


def colors_from_mana_cost(mana_cost: dict[str, Any]) -> list[str]:
    colors: list[str] = []
    for color in COLOR_MASKS:
        try:
            amount = int(mana_cost.get(color, 0) or 0)
        except (TypeError, ValueError):
            amount = 0
        if amount > 0:
            colors.append(color)
    return colors


def color_mask(colors: list[str]) -> int:
    mask = 0
    for color in colors:
        if color not in COLOR_MASKS:
            raise ValueError(f"unknown color {color!r}")
        mask |= COLOR_MASKS[color]
    return mask



def normalize_modes(raw: Any) -> list[dict[str, Any]]:
    if raw is None or raw == "":
        return []
    if not isinstance(raw, list):
        raise ValueError("modes must be a list of mode objects")
    modes: list[dict[str, Any]] = []
    for index, mode in enumerate(raw, start=1):
        if not isinstance(mode, dict):
            raise ValueError(f"mode #{index} must be an object")
        name = str(mode.get("name", f"mode_{index}")).strip() or f"mode_{index}"
        kind = str(mode.get("kind", mode.get("effect_kind", "none"))).lower()
        target = str(mode.get("target", "none")).lower()
        if target not in TARGET_MASKS:
            raise ValueError(f"mode {name!r} has unknown target mask {target!r}")
        modes.append({
            "name": name,
            "kind": kind,
            "amount": int(mode.get("amount", mode.get("effect_amount", 0)) or 0),
            "target": target,
            "counter_kind": str(mode.get("counter_kind", "plus_one_plus_one")).lower(),
            "created_token_definition_index": int(mode.get("created_token_definition_index", mode.get("token_definition_index", 0)) or 0),
        })
    return modes


def normalize_mana_pool_payload(raw: Any) -> dict[str, int]:
    pool = {"white": 0, "blue": 0, "black": 0, "red": 0, "green": 0, "colorless": 0}
    if raw is None or raw == "" or raw == "-" or raw == 0:
        return pool
    if isinstance(raw, str):
        token = raw.strip()
        i = 0
        while i < len(token):
            if token[i].isdigit():
                j = i
                while j < len(token) and token[j].isdigit():
                    j += 1
                pool["colorless"] += int(token[i:j])
                i = j
                continue
            ch = token[i].upper()
            if ch == "W":
                pool["white"] += 1
            elif ch == "U":
                pool["blue"] += 1
            elif ch == "B":
                pool["black"] += 1
            elif ch == "R":
                pool["red"] += 1
            elif ch == "G":
                pool["green"] += 1
            elif ch == "C":
                pool["colorless"] += 1
            else:
                raise ValueError(f"unknown mana production symbol {token[i]!r}")
            i += 1
        return pool
    if isinstance(raw, dict):
        aliases = {"w": "white", "u": "blue", "b": "black", "r": "red", "g": "green", "c": "colorless", "generic": "colorless"}
        for key, value in raw.items():
            normalized = aliases.get(str(key).strip().lower(), str(key).strip().lower())
            if normalized not in pool:
                raise ValueError(f"unknown mana production key {key!r}")
            pool[normalized] += int(value or 0)
        return pool
    raise ValueError("mana production must be a string or object")


def normalize_mana_abilities(raw: Any) -> list[dict[str, Any]]:
    if raw is None or raw == "":
        return []
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        raise ValueError("mana_abilities must be a list of ability objects")
    abilities: list[dict[str, Any]] = []
    for index, ability in enumerate(raw, start=1):
        if not isinstance(ability, dict):
            raise ValueError(f"mana ability #{index} must be an object")
        name = str(ability.get("name", f"mana_{index}")).strip() or f"mana_{index}"
        produces = normalize_mana_pool_payload(ability.get("produces", ability.get("mana", ability.get("add", {}))))
        if sum(produces.values()) <= 0:
            raise ValueError(f"mana ability {name!r} must produce mana")
        abilities.append({
            "name": name,
            "tap_cost": bool(ability.get("tap_cost", ability.get("tap", False))),
            "produces": produces,
            "produced_total": sum(produces.values()),
        })
    return abilities


def normalize_activated_abilities(raw: Any) -> list[dict[str, Any]]:
    if raw is None or raw == "":
        return []
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        raise ValueError("activated_abilities must be a list of ability objects")
    abilities: list[dict[str, Any]] = []
    for index, ability in enumerate(raw, start=1):
        if not isinstance(ability, dict):
            raise ValueError(f"activated ability #{index} must be an object")
        name = str(ability.get("name", f"ability_{index}")).strip() or f"ability_{index}"
        kind = str(ability.get("kind", ability.get("effect_kind", "none"))).lower()
        target = str(ability.get("target", "none")).lower()
        if target not in TARGET_MASKS:
            raise ValueError(f"activated ability {name!r} has unknown target mask {target!r}")
        mana_cost = ability.get("mana_cost", ability.get("cost", {})) or {}
        if isinstance(mana_cost, str):
            mana_cost = {"raw": mana_cost}
        if not isinstance(mana_cost, dict):
            raise ValueError(f"activated ability {name!r} mana_cost must be an object or string")
        abilities.append({
            "name": name,
            "kind": kind,
            "amount": int(ability.get("amount", ability.get("effect_amount", 0)) or 0),
            "target": target,
            "counter_kind": str(ability.get("counter_kind", "plus_one_plus_one")).lower(),
            "created_token_definition_index": int(ability.get("created_token_definition_index", ability.get("token_definition_index", 0)) or 0),
            "tap_cost": bool(ability.get("tap_cost", ability.get("tap", False))),
            "sorcery_speed": bool(ability.get("sorcery_speed", ability.get("sorcery", False))),
            "mana_cost": mana_cost,
        })
    return abilities

def normalize_static_effects(raw: Any) -> list[dict[str, Any]]:
    if raw is None or raw == "":
        return []
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        raise ValueError("static_effects must be a list of effect objects")
    effects: list[dict[str, Any]] = []
    for index, effect in enumerate(raw, start=1):
        if not isinstance(effect, dict):
            raise ValueError(f"static effect #{index} must be an object")
        name = str(effect.get("name", f"static_{index}")).strip() or f"static_{index}"
        scope = str(effect.get("scope", "creatures_you_control")).strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "self": "source",
            "your_creatures": "creatures_you_control",
            "controller_creatures": "creatures_you_control",
            "opponent_creatures": "creatures_opponents_control",
            "opponents_creatures": "creatures_opponents_control",
            "creatures": "all_creatures",
            "your_permanents": "permanents_you_control",
            "controller_permanents": "permanents_you_control",
            "opponent_permanents": "permanents_opponents_control",
            "opponents_permanents": "permanents_opponents_control",
            "permanents": "all_permanents",
        }
        scope = aliases.get(scope, scope)
        if scope not in STATIC_EFFECT_SCOPES:
            raise ValueError(f"static effect {name!r} has unknown scope {scope!r}")
        affected_types = effect.get("affected_types", effect.get("types", ["Creature"]))
        if isinstance(affected_types, str):
            affected_types = [part for part in affected_types.replace("|", ",").split(",") if part]
        if not isinstance(affected_types, list):
            raise ValueError(f"static effect {name!r} affected_types must be a list or string")
        granted_keywords = normalize_keyword_names(effect.get("granted_keywords", effect.get("grants", [])) or [], field="static_effect.grants")
        removed_keywords = normalize_keyword_names(effect.get("removed_keywords", effect.get("remove_keywords", effect.get("remove_abilities", []))) or [], field="static_effect.remove_keywords")
        power = int(effect.get("power_modifier", effect.get("power", effect.get("p", 0))) or 0)
        toughness = int(effect.get("toughness_modifier", effect.get("toughness", effect.get("t", 0))) or 0)
        set_pt_raw = effect.get("set_power_toughness", effect.get("set_pt", effect.get("base_pt", None)))
        sets_power_toughness = set_pt_raw is not None
        set_power = 0
        set_toughness = 0
        if sets_power_toughness:
            if isinstance(set_pt_raw, str):
                pieces = set_pt_raw.replace(",", "/").split("/")
            elif isinstance(set_pt_raw, list) and len(set_pt_raw) == 2:
                pieces = [str(set_pt_raw[0]), str(set_pt_raw[1])]
            else:
                raise ValueError(f"static effect {name!r} set_pt/base_pt must be P/T string or two-value list")
            if len(pieces) != 2:
                raise ValueError(f"static effect {name!r} set_pt/base_pt must have two values")
            set_power = int(pieces[0])
            set_toughness = int(pieces[1])

        def normalize_types_field(value: Any, *, field: str) -> list[str]:
            if value is None or value == "" or value == []:
                return []
            if isinstance(value, str):
                value = [part for part in value.replace("|", ",").split(",") if part]
            if not isinstance(value, list):
                raise ValueError(f"static effect {name!r} {field} must be a list or string")
            return sorted(str(part) for part in value if str(part).strip())

        added_types = normalize_types_field(effect.get("added_types", effect.get("add_types", [])), field="added_types")
        removed_types = normalize_types_field(effect.get("removed_types", effect.get("remove_types", [])), field="removed_types")
        set_colors = normalize_color_names(effect.get("set_colors", effect.get("set_color", None)))
        added_colors = normalize_color_names(effect.get("added_colors", effect.get("add_color", [])))
        removed_colors = normalize_color_names(effect.get("removed_colors", effect.get("remove_color", [])))
        dependencies_raw = effect.get("depends_on_effect_names", effect.get("depends_on", effect.get("dependencies", effect.get("depends", []))))
        if isinstance(dependencies_raw, str):
            dependencies_raw = [part for part in dependencies_raw.replace("|", ",").split(",") if part]
        if dependencies_raw is None:
            dependencies_raw = []
        if not isinstance(dependencies_raw, list):
            raise ValueError(f"static effect {name!r} dependencies must be a list or comma-separated string")
        dependency_names = []
        for dependency in dependencies_raw:
            dependency_name = str(dependency).strip().replace("_", " ")
            if dependency_name and dependency_name not in dependency_names:
                dependency_names.append(dependency_name)
        if power == 0 and toughness == 0 and not granted_keywords and not removed_keywords and not added_types and not removed_types and not set_colors and not added_colors and not removed_colors and not sets_power_toughness:
            raise ValueError(f"static effect {name!r} must modify type/color/P/T, grant/remove a keyword, or set base P/T")
        effects.append({
            "name": name,
            "scope": scope,
            "affected_types": sorted(str(value) for value in affected_types),
            "affected_type_mask": type_mask([str(value) for value in affected_types]),
            "added_types": added_types,
            "added_type_mask": type_mask(added_types) if added_types else 0,
            "removed_types": removed_types,
            "removed_type_mask": type_mask(removed_types) if removed_types else 0,
            "set_colors": set_colors,
            "sets_color": bool(set_colors),
            "set_color_mask": color_mask(set_colors),
            "added_colors": added_colors,
            "added_color_mask": color_mask(added_colors),
            "removed_colors": removed_colors,
            "removed_color_mask": color_mask(removed_colors),
            "sets_power_toughness": bool(sets_power_toughness),
            "set_power": set_power,
            "set_toughness": set_toughness,
            "power_modifier": power,
            "toughness_modifier": toughness,
            "granted_keywords": granted_keywords,
            "granted_ability_mask": ability_mask(granted_keywords),
            "removed_keywords": removed_keywords,
            "removed_ability_mask": ability_mask(removed_keywords),
            "depends_on_effect_names": sorted(dependency_names),
            "dependency_count": len(dependency_names),
        })
    return effects


def summarize_effect_layer_payloads(effects: list[dict[str, Any]]) -> dict[str, int]:
    granted = 0
    removed = 0
    added_types = 0
    removed_types = 0
    added_colors = 0
    removed_colors = 0
    set_color_count = 0
    set_pt_count = 0
    power_mod = 0
    toughness_mod = 0
    dependency_count = 0
    for effect in effects:
        granted |= int(effect.get("granted_ability_mask", 0))
        removed |= int(effect.get("removed_ability_mask", 0))
        added_types |= int(effect.get("added_type_mask", 0))
        removed_types |= int(effect.get("removed_type_mask", 0))
        added_colors |= int(effect.get("added_color_mask", 0))
        removed_colors |= int(effect.get("removed_color_mask", 0))
        if effect.get("sets_color"):
            set_color_count += 1
        if effect.get("sets_power_toughness"):
            set_pt_count += 1
        power_mod += int(effect.get("power_modifier", 0))
        toughness_mod += int(effect.get("toughness_modifier", 0))
        dependency_count += int(effect.get("dependency_count", len(effect.get("depends_on_effect_names", []))))
    return {
        "granted_ability_mask_union": granted,
        "removed_ability_mask_union": removed,
        "added_type_mask_union": added_types,
        "removed_type_mask_union": removed_types,
        "added_color_mask_union": added_colors,
        "removed_color_mask_union": removed_colors,
        "set_color_count": set_color_count,
        "set_pt_count": set_pt_count,
        "power_modifier_total": power_mod,
        "toughness_modifier_total": toughness_mod,
        "dependency_count": dependency_count,
    }


def normalize_card(raw: dict[str, Any], index: int, source: str) -> dict[str, Any]:
    name = str(raw.get("name", "")).strip()
    if not name:
        raise ValueError(f"card at index {index} has no name")
    types = raw.get("types", [])
    if not isinstance(types, list):
        raise ValueError(f"card {name!r} types must be a list")
    mana_cost = raw.get("mana_cost", {}) or {}
    if not isinstance(mana_cost, dict):
        raise ValueError(f"card {name!r} mana_cost must be an object")
    normalized_keywords = normalize_keyword_names(raw.get("keywords", []) or [], field="keywords")
    colors = normalize_color_names(raw.get("colors", raw.get("color", None)))
    if not colors:
        colors = colors_from_mana_cost(mana_cost)
    protection_colors = normalize_color_names(raw.get("protection_colors", raw.get("protection", None)))
    attachment_kind = str(raw.get("attachment_kind", raw.get("attachment", "none"))).strip().lower()
    if attachment_kind in {"equip", "equipment"}:
        attachment_kind = "equipment"
    elif attachment_kind in {"aura", "enchant"}:
        attachment_kind = "aura"
    elif attachment_kind in {"fortify", "fortification"}:
        attachment_kind = "fortification"
    elif attachment_kind in {"", "-", "none"}:
        attachment_kind = "none"
    if attachment_kind not in ATTACHMENT_KINDS:
        raise ValueError(f"card {name!r} has unknown attachment kind {attachment_kind!r}")
    attachment_power_bonus, attachment_toughness_bonus = normalize_attachment_bonus(
        raw.get("attachment_bonus", raw.get("attach_bonus", None))
    )
    attachment_granted_keywords = normalize_keyword_names(
        raw.get("attachment_granted_keywords", raw.get("grants", [])) or [],
        field="attachment_granted_keywords",
    )
    effect = raw.get("effect", {}) or {}
    if not isinstance(effect, dict):
        raise ValueError(f"card {name!r} effect must be an object")
    loyalty_ability = normalize_loyalty_ability(raw.get("loyalty_ability", raw.get("loyalty", {}).get("ability") if isinstance(raw.get("loyalty"), dict) else None))
    modes = normalize_modes(raw.get("modes", raw.get("modal_modes", [])))
    mana_abilities = normalize_mana_abilities(raw.get("mana_abilities", raw.get("mana_ability", [])))
    activated_abilities = normalize_activated_abilities(raw.get("activated_abilities", raw.get("activated", [])))
    static_effects = normalize_static_effects(raw.get("static_effects", raw.get("static", [])))
    continuous_effects = normalize_static_effects(raw.get("continuous_effects", raw.get("continuous_effect", raw.get("continuous", []))))
    continuous_duration = str(raw.get("continuous_effect_duration", raw.get("continuous_duration", "until_cleanup"))).strip().lower().replace("-", "_").replace(" ", "_")
    if continuous_effects and continuous_duration not in {"until_cleanup", "until_end_of_game"}:
        raise ValueError(f"card {name!r} has unknown continuous-effect duration {continuous_duration!r}")
    tap_mana = str(raw.get("tap_mana", "colorless" if raw.get("taps_for_mana") else "colorless")).lower()
    taps_for_mana = bool(raw.get("taps_for_mana", False) or "tap_mana" in raw)
    target = str(effect.get("target", raw.get("target", "none"))).lower()
    effect_kind = str(effect.get("kind", raw.get("effect_kind", "none"))).lower()
    modal_target_mask_union = 0
    for mode in modes:
        modal_target_mask_union |= TARGET_MASKS.get(mode["target"], 0)
    activated_target_mask_union = 0
    for ability in activated_abilities:
        activated_target_mask_union |= TARGET_MASKS.get(ability["target"], 0)
    static_summary = summarize_effect_layer_payloads(static_effects)
    continuous_summary = summarize_effect_layer_payloads(continuous_effects)
    static_granted_ability_mask_union = static_summary["granted_ability_mask_union"]
    static_removed_ability_mask_union = static_summary["removed_ability_mask_union"]
    static_added_type_mask_union = static_summary["added_type_mask_union"]
    static_removed_type_mask_union = static_summary["removed_type_mask_union"]
    static_added_color_mask_union = static_summary["added_color_mask_union"]
    static_removed_color_mask_union = static_summary["removed_color_mask_union"]
    static_set_color_count = static_summary["set_color_count"]
    static_set_pt_count = static_summary["set_pt_count"]
    return {
        "card_id": index + 1,
        "name": name,
        "type_mask": type_mask([str(value) for value in types]),
        "is_token": 1 if bool(raw.get("is_token", raw.get("token", False))) else 0,
        "power": int(raw.get("power", 0) or 0),
        "toughness": int(raw.get("toughness", 0) or 0),
        "loyalty": int((raw.get("loyalty", {}) if isinstance(raw.get("loyalty"), dict) else {"value": raw.get("loyalty", 0)}).get("value", 0) or 0),
        "printed_defense": int(raw.get("printed_defense", raw.get("defense", 0)) or 0),
        "loyalty_ability_json": json.dumps(loyalty_ability, sort_keys=True, separators=(",", ":")),
        "loyalty_ability_cost": loyalty_ability["cost"],
        "loyalty_ability_effect_kind": loyalty_ability["kind"],
        "loyalty_ability_effect_amount": loyalty_ability["amount"],
        "loyalty_ability_target_mask": TARGET_MASKS.get(loyalty_ability["target"], 0),
        "modes_json": json.dumps(modes, sort_keys=True, separators=(",", ":")),
        "mode_count": len(modes),
        "modal_target_mask_union": modal_target_mask_union,
        "activated_abilities_json": json.dumps(activated_abilities, sort_keys=True, separators=(",", ":")),
        "activated_ability_count": len(activated_abilities),
        "activated_target_mask_union": activated_target_mask_union,
        "activated_tap_cost_count": sum(1 for ability in activated_abilities if ability.get("tap_cost")),
        "activated_sorcery_speed_count": sum(1 for ability in activated_abilities if ability.get("sorcery_speed")),
        "mana_abilities_json": json.dumps(mana_abilities, sort_keys=True, separators=(",", ":")),
        "mana_ability_count": len(mana_abilities) + (1 if taps_for_mana else 0),
        "explicit_mana_ability_count": len(mana_abilities),
        "mana_ability_tap_cost_count": sum(1 for ability in mana_abilities if ability.get("tap_cost")) + (1 if taps_for_mana else 0),
        "mana_ability_produced_total": sum(int(ability.get("produced_total", 0)) for ability in mana_abilities) + (1 if taps_for_mana else 0),
        "static_effects_json": json.dumps(static_effects, sort_keys=True, separators=(",", ":")),
        "static_effect_count": len(static_effects),
        "static_dependency_count": static_summary["dependency_count"],
        "static_granted_ability_mask_union": static_granted_ability_mask_union,
        "static_removed_ability_mask_union": static_removed_ability_mask_union,
        "static_added_type_mask_union": static_added_type_mask_union,
        "static_removed_type_mask_union": static_removed_type_mask_union,
        "static_set_color_count": static_set_color_count,
        "static_added_color_mask_union": static_added_color_mask_union,
        "static_removed_color_mask_union": static_removed_color_mask_union,
        "static_set_pt_count": static_set_pt_count,
        "static_set_power_total": sum(int(effect.get("set_power", 0)) for effect in static_effects if effect.get("sets_power_toughness")),
        "static_set_toughness_total": sum(int(effect.get("set_toughness", 0)) for effect in static_effects if effect.get("sets_power_toughness")),
        "static_power_modifier_total": sum(int(effect.get("power_modifier", 0)) for effect in static_effects),
        "static_toughness_modifier_total": sum(int(effect.get("toughness_modifier", 0)) for effect in static_effects),
        "continuous_effects_json": json.dumps(continuous_effects, sort_keys=True, separators=(",", ":")),
        "continuous_effect_count": len(continuous_effects),
        "continuous_dependency_count": continuous_summary["dependency_count"],
        "continuous_duration": continuous_duration if continuous_effects else "until_cleanup",
        "continuous_granted_ability_mask_union": continuous_summary["granted_ability_mask_union"],
        "continuous_removed_ability_mask_union": continuous_summary["removed_ability_mask_union"],
        "continuous_added_type_mask_union": continuous_summary["added_type_mask_union"],
        "continuous_removed_type_mask_union": continuous_summary["removed_type_mask_union"],
        "continuous_set_color_count": continuous_summary["set_color_count"],
        "continuous_added_color_mask_union": continuous_summary["added_color_mask_union"],
        "continuous_removed_color_mask_union": continuous_summary["removed_color_mask_union"],
        "continuous_set_pt_count": continuous_summary["set_pt_count"],
        "continuous_power_modifier_total": continuous_summary["power_modifier_total"],
        "continuous_toughness_modifier_total": continuous_summary["toughness_modifier_total"],
        "mana_cost_json": json.dumps(mana_cost, sort_keys=True, separators=(",", ":")),
        "colors_json": json.dumps(sorted(colors), sort_keys=True, separators=(",", ":")),
        "color_mask": color_mask(colors),
        "keywords_json": json.dumps(sorted(normalized_keywords), sort_keys=True, separators=(",", ":")),
        "ability_mask": ability_mask(normalized_keywords),
        "protection_colors_json": json.dumps(sorted(protection_colors), sort_keys=True, separators=(",", ":")),
        "protection_color_mask": color_mask(protection_colors),
        "attachment_kind": attachment_kind,
        "attachment_power_bonus": attachment_power_bonus,
        "attachment_toughness_bonus": attachment_toughness_bonus,
        "attachment_granted_keywords_json": json.dumps(sorted(attachment_granted_keywords), sort_keys=True, separators=(",", ":")),
        "attachment_granted_ability_mask": ability_mask(attachment_granted_keywords),
        "taps_for_mana": 1 if taps_for_mana else 0,
        "tap_mana_symbol": tap_mana,
        "effect_kind": effect_kind,
        "effect_amount": int(effect.get("amount", raw.get("effect_amount", 0)) or 0),
        "target_mask": TARGET_MASKS.get(target, 0),
        "created_token_definition_index": int(effect.get("created_token_definition_index", effect.get("token_definition_index", raw.get("created_token_definition_index", 0))) or 0),
        "source": source,
    }


def load_cards(path: pathlib.Path) -> tuple[str, list[dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    cards = payload.get("cards", [])
    if not isinstance(cards, list):
        raise ValueError("top-level cards must be a list")
    notice = str(payload.get("notice", ""))
    return notice, [normalize_card(card, index, rel(path)) for index, card in enumerate(cards)]


def build_catalog(input_path: pathlib.Path, schema_path: pathlib.Path, db_path: pathlib.Path) -> dict[str, Any]:
    started = time.perf_counter()
    notice, cards = load_cards(input_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    schema = schema_path.read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema)
        conn.executemany(
            """
            INSERT INTO card_definitions(
              card_id, name, type_mask, is_token, power, toughness, loyalty, printed_defense,
              loyalty_ability_json, loyalty_ability_cost, loyalty_ability_effect_kind,
              loyalty_ability_effect_amount, loyalty_ability_target_mask, modes_json,
              mode_count, modal_target_mask_union, activated_abilities_json,
              activated_ability_count, activated_target_mask_union, activated_tap_cost_count,
              activated_sorcery_speed_count, mana_abilities_json, mana_ability_count,
              explicit_mana_ability_count, mana_ability_tap_cost_count, mana_ability_produced_total,
              static_effects_json, static_effect_count, static_dependency_count, static_granted_ability_mask_union,
              static_removed_ability_mask_union, static_added_type_mask_union,
              static_removed_type_mask_union, static_set_color_count,
              static_added_color_mask_union, static_removed_color_mask_union,
              static_set_pt_count, static_set_power_total, static_set_toughness_total,
              static_power_modifier_total, static_toughness_modifier_total, continuous_effects_json,
              continuous_effect_count, continuous_duration, continuous_granted_ability_mask_union,
              continuous_removed_ability_mask_union, continuous_added_type_mask_union,
              continuous_removed_type_mask_union, continuous_set_color_count,
              continuous_added_color_mask_union, continuous_removed_color_mask_union,
              continuous_set_pt_count, continuous_power_modifier_total,
              continuous_toughness_modifier_total, mana_cost_json,
              colors_json, color_mask, keywords_json, ability_mask,
              protection_colors_json, protection_color_mask, attachment_kind,
              attachment_power_bonus, attachment_toughness_bonus, attachment_granted_keywords_json,
              attachment_granted_ability_mask, taps_for_mana, tap_mana_symbol,
              effect_kind, effect_amount, target_mask, created_token_definition_index, source
            ) VALUES(
              :card_id, :name, :type_mask, :is_token, :power, :toughness, :loyalty, :printed_defense,
              :loyalty_ability_json, :loyalty_ability_cost, :loyalty_ability_effect_kind,
              :loyalty_ability_effect_amount, :loyalty_ability_target_mask, :modes_json,
              :mode_count, :modal_target_mask_union, :activated_abilities_json,
              :activated_ability_count, :activated_target_mask_union, :activated_tap_cost_count,
              :activated_sorcery_speed_count, :mana_abilities_json, :mana_ability_count,
              :explicit_mana_ability_count, :mana_ability_tap_cost_count, :mana_ability_produced_total,
              :static_effects_json, :static_effect_count, :static_dependency_count, :static_granted_ability_mask_union,
              :static_removed_ability_mask_union, :static_added_type_mask_union,
              :static_removed_type_mask_union, :static_set_color_count,
              :static_added_color_mask_union, :static_removed_color_mask_union,
              :static_set_pt_count, :static_set_power_total, :static_set_toughness_total,
              :static_power_modifier_total, :static_toughness_modifier_total, :continuous_effects_json,
              :continuous_effect_count, :continuous_duration, :continuous_granted_ability_mask_union,
              :continuous_removed_ability_mask_union, :continuous_added_type_mask_union,
              :continuous_removed_type_mask_union, :continuous_set_color_count,
              :continuous_added_color_mask_union, :continuous_removed_color_mask_union,
              :continuous_set_pt_count, :continuous_power_modifier_total,
              :continuous_toughness_modifier_total, :mana_cost_json,
              :colors_json, :color_mask, :keywords_json, :ability_mask,
              :protection_colors_json, :protection_color_mask, :attachment_kind,
              :attachment_power_bonus, :attachment_toughness_bonus, :attachment_granted_keywords_json,
              :attachment_granted_ability_mask, :taps_for_mana, :tap_mana_symbol,
              :effect_kind, :effect_amount, :target_mask, :created_token_definition_index, :source
            )
            """,
            cards,
        )
        conn.executemany(
            "INSERT OR REPLACE INTO metadata(key, value) VALUES(?, ?)",
            [
                ("schema", "mtgsim.card_catalog.v17"),
                ("created_at_local", time.strftime("%Y-%m-%dT%H:%M:%S%z")),
                ("input", rel(input_path)),
                ("notice", notice),
            ],
        )
        conn.commit()
        counts = {
            "cards": conn.execute("SELECT COUNT(*) FROM card_definitions").fetchone()[0],
            "creatures": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE (type_mask & ?) != 0", (TYPE_MASKS["Creature"],)).fetchone()[0],
            "lands": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE (type_mask & ?) != 0", (TYPE_MASKS["Land"],)).fetchone()[0],
            "planeswalkers": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE (type_mask & ?) != 0", (TYPE_MASKS["Planeswalker"],)).fetchone()[0],
            "battles": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE (type_mask & ?) != 0", (TYPE_MASKS["Battle"],)).fetchone()[0],
            "battle_defense_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE printed_defense > 0").fetchone()[0],
            "modal_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE mode_count > 0").fetchone()[0],
            "modal_modes": conn.execute("SELECT COALESCE(SUM(mode_count), 0) FROM card_definitions").fetchone()[0],
            "targeted_modal_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE modal_target_mask_union != 0").fetchone()[0],
            "activated_ability_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE activated_ability_count > 0").fetchone()[0],
            "activated_abilities": conn.execute("SELECT COALESCE(SUM(activated_ability_count), 0) FROM card_definitions").fetchone()[0],
            "targeted_activated_ability_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE activated_target_mask_union != 0").fetchone()[0],
            "tap_cost_activated_abilities": conn.execute("SELECT COALESCE(SUM(activated_tap_cost_count), 0) FROM card_definitions").fetchone()[0],
            "sorcery_speed_activated_abilities": conn.execute("SELECT COALESCE(SUM(activated_sorcery_speed_count), 0) FROM card_definitions").fetchone()[0],
            "loyalty_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE loyalty > 0").fetchone()[0],
            "loyalty_ability_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE loyalty_ability_effect_kind != 'none'").fetchone()[0],
            "mana_sources": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE mana_ability_count > 0").fetchone()[0],
            "builtin_tap_mana_sources": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE taps_for_mana = 1").fetchone()[0],
            "explicit_mana_ability_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE explicit_mana_ability_count > 0").fetchone()[0],
            "mana_abilities": conn.execute("SELECT COALESCE(SUM(mana_ability_count), 0) FROM card_definitions").fetchone()[0],
            "explicit_mana_abilities": conn.execute("SELECT COALESCE(SUM(explicit_mana_ability_count), 0) FROM card_definitions").fetchone()[0],
            "static_effect_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE static_effect_count > 0").fetchone()[0],
            "static_effects": conn.execute("SELECT COALESCE(SUM(static_effect_count), 0) FROM card_definitions").fetchone()[0],
            "static_dependency_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE static_dependency_count > 0").fetchone()[0],
            "static_dependencies": conn.execute("SELECT COALESCE(SUM(static_dependency_count), 0) FROM card_definitions").fetchone()[0],
            "static_ability_grant_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE static_granted_ability_mask_union != 0").fetchone()[0],
            "static_ability_remove_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE static_removed_ability_mask_union != 0").fetchone()[0],
            "static_type_add_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE static_added_type_mask_union != 0").fetchone()[0],
            "static_type_remove_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE static_removed_type_mask_union != 0").fetchone()[0],
            "static_color_set_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE static_set_color_count > 0").fetchone()[0],
            "static_color_add_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE static_added_color_mask_union != 0").fetchone()[0],
            "static_color_remove_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE static_removed_color_mask_union != 0").fetchone()[0],
            "static_base_pt_set_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE static_set_pt_count > 0").fetchone()[0],
            "static_set_power_total": conn.execute("SELECT COALESCE(SUM(static_set_power_total), 0) FROM card_definitions").fetchone()[0],
            "static_set_toughness_total": conn.execute("SELECT COALESCE(SUM(static_set_toughness_total), 0) FROM card_definitions").fetchone()[0],
            "static_power_modifier_total": conn.execute("SELECT COALESCE(SUM(static_power_modifier_total), 0) FROM card_definitions").fetchone()[0],
            "static_toughness_modifier_total": conn.execute("SELECT COALESCE(SUM(static_toughness_modifier_total), 0) FROM card_definitions").fetchone()[0],
            "continuous_effect_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE continuous_effect_count > 0").fetchone()[0],
            "continuous_effects": conn.execute("SELECT COALESCE(SUM(continuous_effect_count), 0) FROM card_definitions").fetchone()[0],
            "continuous_dependency_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE continuous_dependency_count > 0").fetchone()[0],
            "continuous_dependencies": conn.execute("SELECT COALESCE(SUM(continuous_dependency_count), 0) FROM card_definitions").fetchone()[0],
            "continuous_ability_grant_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE continuous_granted_ability_mask_union != 0").fetchone()[0],
            "continuous_ability_remove_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE continuous_removed_ability_mask_union != 0").fetchone()[0],
            "continuous_type_add_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE continuous_added_type_mask_union != 0").fetchone()[0],
            "continuous_color_set_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE continuous_set_color_count > 0").fetchone()[0],
            "continuous_base_pt_set_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE continuous_set_pt_count > 0").fetchone()[0],
            "continuous_power_modifier_total": conn.execute("SELECT COALESCE(SUM(continuous_power_modifier_total), 0) FROM card_definitions").fetchone()[0],
            "continuous_toughness_modifier_total": conn.execute("SELECT COALESCE(SUM(continuous_toughness_modifier_total), 0) FROM card_definitions").fetchone()[0],
            "keyword_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE ability_mask != 0").fetchone()[0],
            "flash_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE (ability_mask & ?) != 0", (ABILITY_MASKS["flash"],)).fetchone()[0],
            "colored_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE color_mask != 0").fetchone()[0],
            "protection_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE protection_color_mask != 0").fetchone()[0],
            "attachment_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE attachment_kind != 'none'").fetchone()[0],
            "aura_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE attachment_kind = 'aura'").fetchone()[0],
            "equipment_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE attachment_kind = 'equipment'").fetchone()[0],
            "attachment_grant_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE attachment_granted_ability_mask != 0").fetchone()[0],
            "token_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE is_token = 1").fetchone()[0],
            "create_token_effect_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE effect_kind IN ('create_token', 'create')").fetchone()[0],
            "exile_effect_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE effect_kind IN ('exile', 'exile_permanent')").fetchone()[0],
            "gain_control_effect_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE effect_kind IN ('gain_control', 'gain_control_permanent', 'control')").fetchone()[0],
            "copy_effect_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE effect_kind IN ('copy', 'become_copy', 'become_copy_permanent')").fetchone()[0],
            "counterspell_effect_cards": conn.execute("SELECT COUNT(*) FROM card_definitions WHERE effect_kind IN ('counterspell', 'counter_spell', 'counter_target_spell')").fetchone()[0],
        }
    return {
        "schema": "mtgsim.card_catalog_report.v1",
        "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "status": "passed",
        "duration_sec": time.perf_counter() - started,
        "input": rel(input_path),
        "schema_sql": rel(schema_path),
        "database": rel(db_path),
        "database_bytes": db_path.stat().st_size,
        "summary": counts,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=DEFAULT_INPUT)
    parser.add_argument("--schema", type=pathlib.Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--db", type=pathlib.Path, default=DEFAULT_DB)
    parser.add_argument("--report", type=pathlib.Path, default=DEFAULT_REPORT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    input_path = args.input if args.input.is_absolute() else ROOT / args.input
    schema_path = args.schema if args.schema.is_absolute() else ROOT / args.schema
    db_path = args.db if args.db.is_absolute() else ROOT / args.db
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    report = build_catalog(input_path, schema_path, db_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"card catalog: status={report['status']} cards={report['summary']['cards']} db={report['database']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
