#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from fixture_plan_lib import (
    candidate_action,
    candidate_locator_hints,
    candidate_locator_root,
    candidate_locator_root_strategy,
    candidate_locator_strategy,
    metadata,
)
from native_message_budget_lib import fixture_payload_budget


def load_fixture(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    message = data.get("message")
    if isinstance(message, dict):
        payload = message.get("payload")
        if isinstance(payload, dict):
            return payload
    return data if isinstance(data.get("adapter"), str) else None


def top_field(items: list[Any], key: str) -> str | None:
    if not items or not isinstance(items[0], dict):
        return None
    value = items[0].get(key)
    return value if isinstance(value, str) else None


def top_label(items: list[Any]) -> str | None:
    return top_field(items, "label_text")


def top_accessible_name(items: list[Any]) -> str | None:
    return top_field(items, "accessible_name") or top_label(items)


def top_option_count(items: list[Any]) -> int | None:
    if not items or not isinstance(items[0], dict):
        return None
    value = items[0].get("option_count")
    return value if isinstance(value, int) else None


def top_selected_option(items: list[Any]) -> str | None:
    if not items or not isinstance(items[0], dict):
        return None
    selected = items[0].get("selected_options")
    if isinstance(selected, list) and selected and isinstance(selected[0], str):
        return selected[0]
    return None


def top_bool_field(items: list[Any], key: str) -> bool | None:
    if not items or not isinstance(items[0], dict):
        return None
    value = items[0].get(key)
    return value if isinstance(value, bool) else None


def top_int_field(items: list[Any], key: str) -> int | None:
    if not items or not isinstance(items[0], dict):
        return None
    value = items[0].get(key)
    return value if isinstance(value, int) else None


def top_list_field(items: list[Any], key: str) -> list[str]:
    if not items or not isinstance(items[0], dict):
        return []
    value = items[0].get(key)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def top_candidate(items: list[Any]) -> dict[str, Any] | None:
    if not items or not isinstance(items[0], dict):
        return None
    return items[0]


def top_locator_hints(items: list[Any], *, purpose: str) -> list[str]:
    candidate = top_candidate(items)
    if candidate is None:
        return []
    return candidate_locator_hints(candidate, purpose=purpose)


def top_action(items: list[Any], *, purpose: str) -> str | None:
    candidate = top_candidate(items)
    if candidate is None:
        return None
    return candidate_action(candidate, purpose=purpose)


def top_locator_strategy(items: list[Any], *, purpose: str) -> str | None:
    candidate = top_candidate(items)
    if candidate is None:
        return None
    return candidate_locator_strategy(candidate, purpose=purpose)


def top_locator_root(items: list[Any], *, purpose: str) -> str | None:
    candidate = top_candidate(items)
    if candidate is None:
        return None
    return candidate_locator_root(candidate, purpose=purpose)


def top_locator_root_strategy(items: list[Any], *, purpose: str) -> str | None:
    candidate = top_candidate(items)
    if candidate is None:
        return None
    return candidate_locator_root_strategy(candidate, purpose=purpose)


def top_submit_label(meta: dict[str, Any]) -> str | None:
    direct = meta.get("top_submit_label")
    if isinstance(direct, str):
        return direct
    submit_candidates = meta.get("submit_candidates")
    if isinstance(submit_candidates, list) and submit_candidates and isinstance(submit_candidates[0], dict):
        first = submit_candidates[0]
        for key in ("label_text", "text_sample"):
            value = first.get(key)
            if isinstance(value, str):
                return value
    return None


def top_submit_action(meta: dict[str, Any]) -> str | None:
    direct = meta.get("top_submit_action")
    if isinstance(direct, str):
        return direct
    submit_candidates = meta.get("submit_candidates")
    if isinstance(submit_candidates, list) and submit_candidates and isinstance(submit_candidates[0], dict):
        first = submit_candidates[0]
        for key in ("submit_action", "form_action"):
            value = first.get(key)
            if isinstance(value, str):
                return value
    return None




def top_submit_locator_hints(meta: dict[str, Any]) -> list[str]:
    submit_candidates = meta.get("submit_candidates")
    if isinstance(submit_candidates, list) and submit_candidates and isinstance(submit_candidates[0], dict):
        return candidate_locator_hints(submit_candidates[0], purpose="submit")
    label = top_submit_label(meta)
    if isinstance(label, str) and label:
        return [f'page.getByRole("button", {{ name: {json.dumps(label, ensure_ascii=False)} }})']
    return []


def top_submit_locator_strategy(meta: dict[str, Any]) -> str | None:
    submit_candidates = meta.get("submit_candidates")
    if isinstance(submit_candidates, list) and submit_candidates and isinstance(submit_candidates[0], dict):
        return candidate_locator_strategy(submit_candidates[0], purpose="submit")
    return "role" if top_submit_label(meta) else None


def semantic_outline(meta: dict[str, Any]) -> dict[str, list[str]]:
    outline = meta.get("semantic_outline")
    if not isinstance(outline, dict):
        return {}
    result: dict[str, list[str]] = {}
    for key in ("heading_outline", "prompt_labels", "accessible_names", "prompt_descriptions", "submit_labels", "form_names", "form_actions", "fieldset_legends", "dialog_names", "iframe_names", "iframe_titles", "frame_paths", "control_kinds", "option_labels", "choice_groups", "autocomplete_tokens", "state_flags", "constraint_hints", "link_hosts"):
        value = outline.get(key)
        if isinstance(value, list):
            result[key] = [item for item in value if isinstance(item, str)]
    return result


def summarize(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    candidates = payload.get("candidates") if isinstance(payload.get("candidates"), dict) else {}
    inputs = candidates.get("inputs") if isinstance(candidates.get("inputs"), list) else []
    outputs = candidates.get("outputs") if isinstance(candidates.get("outputs"), list) else []
    meta = metadata(payload)
    outline = semantic_outline(meta)
    budget = fixture_payload_budget(payload)
    return {
        "path": str(path),
        "adapter": payload.get("adapter"),
        "title": payload.get("title"),
        "url": payload.get("url"),
        "prompt_length": len(payload.get("prompt") or ""),
        "latest_output_length": len(payload.get("latest_output") or ""),
        "selection_length": len(payload.get("selection") or ""),
        "top_input_hint": inputs[0].get("selector_hint") if inputs and isinstance(inputs[0], dict) else None,
        "top_output_hint": outputs[0].get("selector_hint") if outputs and isinstance(outputs[0], dict) else None,
        "top_input_label": top_label(inputs),
        "top_input_accessible_name": top_accessible_name(inputs),
        "top_input_action": top_action(inputs, purpose="input"),
        "top_input_locator_strategy": top_locator_strategy(inputs, purpose="input"),
        "top_input_locator_root": top_locator_root(inputs, purpose="input"),
        "top_input_locator_root_strategy": top_locator_root_strategy(inputs, purpose="input"),
        "top_input_locator_hints": top_locator_hints(inputs, purpose="input"),
        "top_input_description": top_field(inputs, "description_text"),
        "top_output_label": top_accessible_name(outputs) or top_field(outputs, "text_sample") or meta.get("top_output_label"),
        "top_output_action": top_action(outputs, purpose="read"),
        "top_output_locator_strategy": top_locator_strategy(outputs, purpose="read"),
        "top_output_locator_root": top_locator_root(outputs, purpose="read"),
        "top_output_locator_root_strategy": top_locator_root_strategy(outputs, purpose="read"),
        "top_output_locator_hints": top_locator_hints(outputs, purpose="read"),
        "top_output_frame_path": top_field(outputs, "frame_path") or meta.get("top_output_frame_path"),
        "top_output_frame_depth": top_int_field(outputs, "frame_depth") if top_int_field(outputs, "frame_depth") is not None else meta.get("top_output_frame_depth"),
        "top_fieldset_legend": top_field(inputs, "fieldset_legend"),
        "top_dialog_name": top_field(inputs, "dialog_name") or (outline.get("dialog_names") or [None])[0],
        "top_form_name": top_field(inputs, "form_name") or (outline.get("form_names") or [None])[0],
        "top_input_frame_path": top_field(inputs, "frame_path") or meta.get("top_input_frame_path"),
        "top_input_frame_depth": top_int_field(inputs, "frame_depth") if top_int_field(inputs, "frame_depth") is not None else meta.get("top_input_frame_depth"),
        "top_option_count": top_option_count(inputs),
        "top_selected_option": top_selected_option(inputs),
        "top_checked_state": top_field(inputs, "checked_state"),
        "top_disabled": top_bool_field(inputs, "disabled"),
        "top_readonly": top_bool_field(inputs, "readonly"),
        "top_multiple": top_bool_field(inputs, "multiple"),
        "top_selected_count": top_int_field(inputs, "selected_count"),
        "top_autocomplete": top_field(inputs, "autocomplete"),
        "top_input_mode": top_field(inputs, "input_mode"),
        "top_choice_group": top_field(inputs, "choice_group"),
        "top_constraint_hints": top_list_field(inputs, "constraint_hints"),
        "top_constraint_flags": top_list_field(inputs, "constraint_flags"),
        "top_submit_label": top_submit_label(meta),
        "top_submit_action": top_submit_action(meta),
        "top_submit_frame_path": meta.get("top_submit_frame_path"),
        "top_submit_locator_strategy": top_submit_locator_strategy(meta),
        "top_submit_locator_root": top_locator_root(meta.get("submit_candidates") if isinstance(meta.get("submit_candidates"), list) else [], purpose="submit"),
        "top_submit_locator_root_strategy": top_locator_root_strategy(meta.get("submit_candidates") if isinstance(meta.get("submit_candidates"), list) else [], purpose="submit"),
        "top_submit_locator_hints": top_submit_locator_hints(meta),
        "first_form_action": (outline.get("form_actions") or [None])[0],
        "control_kinds": outline.get("control_kinds", []),
        "form_names": outline.get("form_names", []),
        "dialog_names": outline.get("dialog_names", []),
        "iframe_names": outline.get("iframe_names", []),
        "iframe_titles": outline.get("iframe_titles", []),
        "frame_paths": outline.get("frame_paths", []),
        "option_labels": outline.get("option_labels", []),
        "choice_groups": outline.get("choice_groups", []),
        "autocomplete_tokens": outline.get("autocomplete_tokens", []),
        "state_flags": outline.get("state_flags", []),
        "constraint_hints": outline.get("constraint_hints", []),
        "link_hosts": outline.get("link_hosts", []),
        "accessible_iframe_count": meta.get("accessible_iframe_count"),
        "blocked_iframe_count": meta.get("blocked_iframe_count"),
        "blocked_iframe_names": meta.get("blocked_iframe_names", []),
        "blocked_iframe_titles": meta.get("blocked_iframe_titles", []),
        "blocked_frame_paths": meta.get("blocked_frame_paths", []),
        "traversed_document_count": meta.get("traversed_document_count"),
        "total_iframe_count": meta.get("total_iframe_count"),
        "frame_capture_ratio": meta.get("frame_capture_ratio"),
        "frame_capture_status": meta.get("frame_capture_status"),
        "frame_capture_warning": meta.get("frame_capture_warning"),
        "max_frame_depth": meta.get("max_frame_depth"),
        "split_scope_detected": meta.get("split_scope_detected"),
        "native_message_payload_bytes": budget['payload_bytes'],
        "native_message_envelope_bytes": budget['envelope_bytes'],
        "native_message_status": budget['host_to_extension']['status'],
        "native_message_usage_ratio": budget['host_to_extension']['usage_ratio'],
        "native_message_remaining_bytes": budget['host_to_extension']['remaining_bytes'],
    }


def build_index(root: Path) -> dict[str, Any]:
    items = []
    for path in sorted(root.rglob("*.json")):
        payload = load_fixture(path)
        if payload:
            items.append(summarize(path, payload))
    by_adapter: dict[str, int] = {}
    for item in items:
        key = str(item.get("adapter") or "unknown")
        by_adapter[key] = by_adapter.get(key, 0) + 1
    return {"root": str(root), "count": len(items), "by_adapter": by_adapter, "fixtures": items}


def main() -> None:
    parser = argparse.ArgumentParser(description="Index saved GlassTTY fixture JSON files")
    parser.add_argument("root", nargs="?", default="fixtures")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build_index(Path(args.root)), indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
