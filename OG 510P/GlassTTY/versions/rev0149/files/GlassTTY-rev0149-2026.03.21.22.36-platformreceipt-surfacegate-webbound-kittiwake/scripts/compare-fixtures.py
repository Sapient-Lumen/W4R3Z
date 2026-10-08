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
)


def load_fixture(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"fixture at {path} is not a JSON object")
    message = data.get("message")
    if isinstance(message, dict):
        payload = message.get("payload")
        if isinstance(payload, dict):
            return payload
    if isinstance(data.get("adapter"), str):
        return data
    raise ValueError(f"fixture at {path} does not look like a GlassTTY fixture payload")


def top_hint(payload: dict[str, Any], bucket: str) -> str | None:
    candidates = payload.get("candidates")
    if not isinstance(candidates, dict):
        return None
    items = candidates.get(bucket)
    if not isinstance(items, list) or not items:
        return None
    first = items[0]
    if not isinstance(first, dict):
        return None
    hint = first.get("selector_hint")
    return hint if isinstance(hint, str) else None


def top_field(payload: dict[str, Any], bucket: str, key: str) -> str | None:
    candidates = payload.get("candidates")
    if not isinstance(candidates, dict):
        return None
    items = candidates.get(bucket)
    if not isinstance(items, list) or not items:
        return None
    first = items[0]
    if not isinstance(first, dict):
        return None
    value = first.get(key)
    return value if isinstance(value, str) else None


def top_label(payload: dict[str, Any], bucket: str) -> str | None:
    return top_field(payload, bucket, "label_text")


def top_accessible_name(payload: dict[str, Any], bucket: str) -> str | None:
    return top_field(payload, bucket, "accessible_name") or top_label(payload, bucket)


def top_output_label_value(payload: dict[str, Any]) -> str | None:
    direct = metadata(payload).get("top_output_label")
    if isinstance(direct, str) and direct:
        return top_accessible_name(payload, "outputs") or top_field(payload, "outputs", "text_sample") or direct
    return top_accessible_name(payload, "outputs") or top_field(payload, "outputs", "text_sample")


def top_option_count(payload: dict[str, Any], bucket: str) -> int | None:
    candidates = payload.get("candidates")
    if not isinstance(candidates, dict):
        return None
    items = candidates.get(bucket)
    if not isinstance(items, list) or not items:
        return None
    first = items[0]
    if not isinstance(first, dict):
        return None
    value = first.get("option_count")
    return value if isinstance(value, int) else None


def top_selected_option(payload: dict[str, Any], bucket: str) -> str | None:
    candidates = payload.get("candidates")
    if not isinstance(candidates, dict):
        return None
    items = candidates.get(bucket)
    if not isinstance(items, list) or not items:
        return None
    first = items[0]
    if not isinstance(first, dict):
        return None
    values = first.get("selected_options")
    if isinstance(values, list) and values and isinstance(values[0], str):
        return values[0]
    return None


def top_bool_field(payload: dict[str, Any], bucket: str, key: str) -> bool | None:
    candidates = payload.get("candidates")
    if not isinstance(candidates, dict):
        return None
    items = candidates.get(bucket)
    if not isinstance(items, list) or not items:
        return None
    first = items[0]
    if not isinstance(first, dict):
        return None
    value = first.get(key)
    return value if isinstance(value, bool) else None


def top_int_field(payload: dict[str, Any], bucket: str, key: str) -> int | None:
    candidates = payload.get("candidates")
    if not isinstance(candidates, dict):
        return None
    items = candidates.get(bucket)
    if not isinstance(items, list) or not items:
        return None
    first = items[0]
    if not isinstance(first, dict):
        return None
    value = first.get(key)
    return value if isinstance(value, int) else None


def top_list_field(payload: dict[str, Any], bucket: str, key: str) -> list[str]:
    candidates = payload.get("candidates")
    if not isinstance(candidates, dict):
        return []
    items = candidates.get(bucket)
    if not isinstance(items, list) or not items:
        return []
    first = items[0]
    if not isinstance(first, dict):
        return []
    value = first.get(key)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def top_candidate(payload: dict[str, Any], bucket: str) -> dict[str, Any] | None:
    candidates = payload.get("candidates")
    if not isinstance(candidates, dict):
        return None
    items = candidates.get(bucket)
    if not isinstance(items, list) or not items:
        return None
    first = items[0]
    return first if isinstance(first, dict) else None


def top_locator_hints(payload: dict[str, Any], bucket: str, *, purpose: str) -> list[str]:
    candidate = top_candidate(payload, bucket)
    if candidate is None:
        return []
    return candidate_locator_hints(candidate, purpose=purpose)


def top_action(payload: dict[str, Any], bucket: str, *, purpose: str) -> str | None:
    candidate = top_candidate(payload, bucket)
    if candidate is None:
        return None
    return candidate_action(candidate, purpose=purpose)


def top_locator_strategy(payload: dict[str, Any], bucket: str, *, purpose: str) -> str | None:
    candidate = top_candidate(payload, bucket)
    if candidate is None:
        return None
    return candidate_locator_strategy(candidate, purpose=purpose)


def top_locator_root(payload: dict[str, Any], bucket: str, *, purpose: str) -> str | None:
    candidate = top_candidate(payload, bucket)
    if candidate is None:
        return None
    return candidate_locator_root(candidate, purpose=purpose)


def top_locator_root_strategy(payload: dict[str, Any], bucket: str, *, purpose: str) -> str | None:
    candidate = top_candidate(payload, bucket)
    if candidate is None:
        return None
    return candidate_locator_root_strategy(candidate, purpose=purpose)


def metadata(payload: dict[str, Any]) -> dict[str, Any]:
    meta = payload.get("metadata")
    return meta if isinstance(meta, dict) else {}


def top_submit_label(payload: dict[str, Any]) -> str | None:
    meta = metadata(payload)
    direct = meta.get("top_submit_label")
    if isinstance(direct, str):
        return direct
    submit_candidates = meta.get("submit_candidates")
    if isinstance(submit_candidates, list) and submit_candidates:
        first = submit_candidates[0]
        if isinstance(first, dict):
            for key in ("label_text", "text_sample"):
                value = first.get(key)
                if isinstance(value, str):
                    return value
    return None


def top_submit_action(payload: dict[str, Any]) -> str | None:
    meta = metadata(payload)
    direct = meta.get("top_submit_action")
    if isinstance(direct, str):
        return direct
    submit_candidates = meta.get("submit_candidates")
    if isinstance(submit_candidates, list) and submit_candidates:
        first = submit_candidates[0]
        if isinstance(first, dict):
            for key in ("submit_action", "form_action"):
                value = first.get(key)
                if isinstance(value, str):
                    return value
    return None


def top_submit_locator_hints(payload: dict[str, Any]) -> list[str]:
    meta = metadata(payload)
    submit_candidates = meta.get("submit_candidates")
    if isinstance(submit_candidates, list) and submit_candidates and isinstance(submit_candidates[0], dict):
        return candidate_locator_hints(submit_candidates[0], purpose="submit")
    label = top_submit_label(payload)
    if isinstance(label, str) and label:
        return [f'page.getByRole("button", {{ name: {json.dumps(label, ensure_ascii=False)} }})']
    return []


def top_submit_locator_strategy(payload: dict[str, Any]) -> str | None:
    meta = metadata(payload)
    submit_candidates = meta.get("submit_candidates")
    if isinstance(submit_candidates, list) and submit_candidates and isinstance(submit_candidates[0], dict):
        return candidate_locator_strategy(submit_candidates[0], purpose="submit")
    return "role" if top_submit_label(payload) else None


def top_submit_locator_root(payload: dict[str, Any]) -> str | None:
    meta = metadata(payload)
    submit_candidates = meta.get("submit_candidates")
    if isinstance(submit_candidates, list) and submit_candidates and isinstance(submit_candidates[0], dict):
        return candidate_locator_root(submit_candidates[0], purpose="submit")
    return 'page' if top_submit_label(payload) else None


def top_submit_locator_root_strategy(payload: dict[str, Any]) -> str | None:
    meta = metadata(payload)
    submit_candidates = meta.get("submit_candidates")
    if isinstance(submit_candidates, list) and submit_candidates and isinstance(submit_candidates[0], dict):
        return candidate_locator_root_strategy(submit_candidates[0], purpose="submit")
    return 'page' if top_submit_label(payload) else None


def top_submit_action_kind(payload: dict[str, Any]) -> str | None:
    meta = metadata(payload)
    submit_candidates = meta.get("submit_candidates")
    if isinstance(submit_candidates, list) and submit_candidates and isinstance(submit_candidates[0], dict):
        return candidate_action(submit_candidates[0], purpose="submit")
    return "click" if top_submit_label(payload) else None


def first_form_action(payload: dict[str, Any]) -> str | None:
    meta = metadata(payload)
    for key in ("form_actions",):
        items = meta.get(key)
        if isinstance(items, list) and items:
            first = items[0]
            return first if isinstance(first, str) else None
    semantic_outline = meta.get("semantic_outline")
    if isinstance(semantic_outline, dict):
        items = semantic_outline.get("form_actions")
        if isinstance(items, list) and items:
            first = items[0]
            return first if isinstance(first, str) else None
    return None


def semantic_outline(payload: dict[str, Any]) -> dict[str, list[str]]:
    meta = metadata(payload)
    outline = meta.get("semantic_outline")
    if not isinstance(outline, dict):
        return {}
    normalized: dict[str, list[str]] = {}
    for key in ("heading_outline", "prompt_labels", "accessible_names", "prompt_descriptions", "submit_labels", "form_names", "form_actions", "fieldset_legends", "dialog_names", "iframe_names", "iframe_titles", "frame_paths", "control_kinds", "option_labels", "choice_groups", "autocomplete_tokens", "state_flags", "constraint_hints", "link_hosts"):
        value = outline.get(key)
        if isinstance(value, list):
            normalized[key] = [item for item in value if isinstance(item, str)]
    return normalized


def compare_payloads(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    prompt_left = str(left.get("prompt") or "")
    prompt_right = str(right.get("prompt") or "")
    output_left = str(left.get("latest_output") or "")
    output_right = str(right.get("latest_output") or "")
    selection_left = str(left.get("selection") or "")
    selection_right = str(right.get("selection") or "")
    left_outline = semantic_outline(left)
    right_outline = semantic_outline(right)
    left_form_action = first_form_action(left)
    right_form_action = first_form_action(right)
    return {
        "left": {
            "adapter": left.get("adapter"), "title": left.get("title"), "url": left.get("url"),
            "prompt_length": len(prompt_left), "latest_output_length": len(output_left), "selection_length": len(selection_left),
            "top_input_hint": top_hint(left, "inputs"), "top_output_hint": top_hint(left, "outputs"),
            "top_input_label": top_label(left, "inputs"), "top_input_accessible_name": top_accessible_name(left, "inputs"), "top_input_description": top_field(left, "inputs", "description_text"),
            "top_input_action": top_action(left, "inputs", purpose="input"), "top_input_locator_strategy": top_locator_strategy(left, "inputs", purpose="input"), "top_input_locator_root": top_locator_root(left, "inputs", purpose="input"), "top_input_locator_root_strategy": top_locator_root_strategy(left, "inputs", purpose="input"), "top_input_locator_hints": top_locator_hints(left, "inputs", purpose="input"),
            "top_output_label": top_output_label_value(left), "top_output_action": top_action(left, "outputs", purpose="read"), "top_output_locator_strategy": top_locator_strategy(left, "outputs", purpose="read"), "top_output_locator_root": top_locator_root(left, "outputs", purpose="read"), "top_output_locator_root_strategy": top_locator_root_strategy(left, "outputs", purpose="read"), "top_output_locator_hints": top_locator_hints(left, "outputs", purpose="read"), "top_output_frame_path": top_field(left, "outputs", "frame_path") or metadata(left).get("top_output_frame_path"), "top_output_frame_depth": top_int_field(left, "outputs", "frame_depth") if top_int_field(left, "outputs", "frame_depth") is not None else metadata(left).get("top_output_frame_depth"), "top_fieldset_legend": top_field(left, "inputs", "fieldset_legend"),
            "top_dialog_name": top_field(left, "inputs", "dialog_name") or ((left_outline.get("dialog_names") or [None])[0]), "top_form_name": top_field(left, "inputs", "form_name") or (left_outline.get("form_names", [None])[0]), "top_input_frame_path": top_field(left, "inputs", "frame_path") or metadata(left).get("top_input_frame_path"), "top_input_frame_depth": top_int_field(left, "inputs", "frame_depth") if top_int_field(left, "inputs", "frame_depth") is not None else metadata(left).get("top_input_frame_depth"), "top_option_count": top_option_count(left, "inputs"), "top_selected_option": top_selected_option(left, "inputs"),
            "top_checked_state": top_field(left, "inputs", "checked_state"), "top_disabled": top_bool_field(left, "inputs", "disabled"), "top_readonly": top_bool_field(left, "inputs", "readonly"), "top_multiple": top_bool_field(left, "inputs", "multiple"), "top_selected_count": top_int_field(left, "inputs", "selected_count"),
            "top_autocomplete": top_field(left, "inputs", "autocomplete"), "top_input_mode": top_field(left, "inputs", "input_mode"), "top_choice_group": top_field(left, "inputs", "choice_group"), "top_constraint_hints": top_list_field(left, "inputs", "constraint_hints"), "top_constraint_flags": top_list_field(left, "inputs", "constraint_flags"),
            "top_submit_label": top_submit_label(left), "top_submit_action": top_submit_action(left), "top_submit_frame_path": metadata(left).get("top_submit_frame_path"), "top_submit_action_kind": top_submit_action_kind(left), "top_submit_locator_strategy": top_submit_locator_strategy(left), "top_submit_locator_root": top_submit_locator_root(left), "top_submit_locator_root_strategy": top_submit_locator_root_strategy(left), "top_submit_locator_hints": top_submit_locator_hints(left), "first_form_action": left_form_action,
            "accessible_iframe_count": metadata(left).get("accessible_iframe_count"), "blocked_iframe_count": metadata(left).get("blocked_iframe_count"), "blocked_iframe_names": metadata(left).get("blocked_iframe_names"), "blocked_iframe_titles": metadata(left).get("blocked_iframe_titles"), "blocked_frame_paths": metadata(left).get("blocked_frame_paths"), "traversed_document_count": metadata(left).get("traversed_document_count"), "total_iframe_count": metadata(left).get("total_iframe_count"), "frame_capture_ratio": metadata(left).get("frame_capture_ratio"), "frame_capture_status": metadata(left).get("frame_capture_status"), "frame_capture_warning": metadata(left).get("frame_capture_warning"), "max_frame_depth": metadata(left).get("max_frame_depth"), "split_scope_detected": metadata(left).get("split_scope_detected"),
            "semantic_outline": left_outline,
        },
        "right": {
            "adapter": right.get("adapter"), "title": right.get("title"), "url": right.get("url"),
            "prompt_length": len(prompt_right), "latest_output_length": len(output_right), "selection_length": len(selection_right),
            "top_input_hint": top_hint(right, "inputs"), "top_output_hint": top_hint(right, "outputs"),
            "top_input_label": top_label(right, "inputs"), "top_input_accessible_name": top_accessible_name(right, "inputs"), "top_input_description": top_field(right, "inputs", "description_text"),
            "top_input_action": top_action(right, "inputs", purpose="input"), "top_input_locator_strategy": top_locator_strategy(right, "inputs", purpose="input"), "top_input_locator_root": top_locator_root(right, "inputs", purpose="input"), "top_input_locator_root_strategy": top_locator_root_strategy(right, "inputs", purpose="input"), "top_input_locator_hints": top_locator_hints(right, "inputs", purpose="input"),
            "top_output_label": top_output_label_value(right), "top_output_action": top_action(right, "outputs", purpose="read"), "top_output_locator_strategy": top_locator_strategy(right, "outputs", purpose="read"), "top_output_locator_root": top_locator_root(right, "outputs", purpose="read"), "top_output_locator_root_strategy": top_locator_root_strategy(right, "outputs", purpose="read"), "top_output_locator_hints": top_locator_hints(right, "outputs", purpose="read"), "top_output_frame_path": top_field(right, "outputs", "frame_path") or metadata(right).get("top_output_frame_path"), "top_output_frame_depth": top_int_field(right, "outputs", "frame_depth") if top_int_field(right, "outputs", "frame_depth") is not None else metadata(right).get("top_output_frame_depth"), "top_fieldset_legend": top_field(right, "inputs", "fieldset_legend"),
            "top_dialog_name": top_field(right, "inputs", "dialog_name") or ((right_outline.get("dialog_names") or [None])[0]), "top_form_name": top_field(right, "inputs", "form_name") or (right_outline.get("form_names", [None])[0]), "top_input_frame_path": top_field(right, "inputs", "frame_path") or metadata(right).get("top_input_frame_path"), "top_input_frame_depth": top_int_field(right, "inputs", "frame_depth") if top_int_field(right, "inputs", "frame_depth") is not None else metadata(right).get("top_input_frame_depth"), "top_option_count": top_option_count(right, "inputs"), "top_selected_option": top_selected_option(right, "inputs"),
            "top_checked_state": top_field(right, "inputs", "checked_state"), "top_disabled": top_bool_field(right, "inputs", "disabled"), "top_readonly": top_bool_field(right, "inputs", "readonly"), "top_multiple": top_bool_field(right, "inputs", "multiple"), "top_selected_count": top_int_field(right, "inputs", "selected_count"),
            "top_autocomplete": top_field(right, "inputs", "autocomplete"), "top_input_mode": top_field(right, "inputs", "input_mode"), "top_choice_group": top_field(right, "inputs", "choice_group"), "top_constraint_hints": top_list_field(right, "inputs", "constraint_hints"), "top_constraint_flags": top_list_field(right, "inputs", "constraint_flags"),
            "top_submit_label": top_submit_label(right), "top_submit_action": top_submit_action(right), "top_submit_frame_path": metadata(right).get("top_submit_frame_path"), "top_submit_action_kind": top_submit_action_kind(right), "top_submit_locator_strategy": top_submit_locator_strategy(right), "top_submit_locator_root": top_submit_locator_root(right), "top_submit_locator_root_strategy": top_submit_locator_root_strategy(right), "top_submit_locator_hints": top_submit_locator_hints(right), "first_form_action": right_form_action,
            "accessible_iframe_count": metadata(right).get("accessible_iframe_count"), "blocked_iframe_count": metadata(right).get("blocked_iframe_count"), "blocked_iframe_names": metadata(right).get("blocked_iframe_names"), "blocked_iframe_titles": metadata(right).get("blocked_iframe_titles"), "blocked_frame_paths": metadata(right).get("blocked_frame_paths"), "traversed_document_count": metadata(right).get("traversed_document_count"), "total_iframe_count": metadata(right).get("total_iframe_count"), "frame_capture_ratio": metadata(right).get("frame_capture_ratio"), "frame_capture_status": metadata(right).get("frame_capture_status"), "frame_capture_warning": metadata(right).get("frame_capture_warning"), "max_frame_depth": metadata(right).get("max_frame_depth"), "split_scope_detected": metadata(right).get("split_scope_detected"),
            "semantic_outline": right_outline,
        },
        "delta": {
            "same_adapter": left.get("adapter") == right.get("adapter"),
            "same_title": left.get("title") == right.get("title"),
            "same_url": left.get("url") == right.get("url"),
            "prompt_length_delta": len(prompt_right) - len(prompt_left),
            "latest_output_length_delta": len(output_right) - len(output_left),
            "selection_length_delta": len(selection_right) - len(selection_left),
            "input_hint_changed": top_hint(left, "inputs") != top_hint(right, "inputs"),
            "output_hint_changed": top_hint(left, "outputs") != top_hint(right, "outputs"),
            "input_label_changed": top_label(left, "inputs") != top_label(right, "inputs"),
            "input_accessible_name_changed": top_accessible_name(left, "inputs") != top_accessible_name(right, "inputs"),
            "input_description_changed": top_field(left, "inputs", "description_text") != top_field(right, "inputs", "description_text"),
            "input_action_changed": top_action(left, "inputs", purpose="input") != top_action(right, "inputs", purpose="input"),
            "input_locator_strategy_changed": top_locator_strategy(left, "inputs", purpose="input") != top_locator_strategy(right, "inputs", purpose="input"),
            "input_locator_root_changed": top_locator_root(left, "inputs", purpose="input") != top_locator_root(right, "inputs", purpose="input"),
            "input_locator_root_strategy_changed": top_locator_root_strategy(left, "inputs", purpose="input") != top_locator_root_strategy(right, "inputs", purpose="input"),
            "input_locator_hint_changed": top_locator_hints(left, "inputs", purpose="input") != top_locator_hints(right, "inputs", purpose="input"),
            "output_label_changed": top_output_label_value(left) != top_output_label_value(right),
            "output_action_changed": top_action(left, "outputs", purpose="read") != top_action(right, "outputs", purpose="read"),
            "output_locator_strategy_changed": top_locator_strategy(left, "outputs", purpose="read") != top_locator_strategy(right, "outputs", purpose="read"),
            "output_locator_root_changed": top_locator_root(left, "outputs", purpose="read") != top_locator_root(right, "outputs", purpose="read"),
            "output_locator_root_strategy_changed": top_locator_root_strategy(left, "outputs", purpose="read") != top_locator_root_strategy(right, "outputs", purpose="read"),
            "output_locator_hint_changed": top_locator_hints(left, "outputs", purpose="read") != top_locator_hints(right, "outputs", purpose="read"),
            "fieldset_legend_changed": top_field(left, "inputs", "fieldset_legend") != top_field(right, "inputs", "fieldset_legend"),
            "dialog_name_changed": (top_field(left, "inputs", "dialog_name") or ((left_outline.get("dialog_names") or [None])[0])) != (top_field(right, "inputs", "dialog_name") or ((right_outline.get("dialog_names") or [None])[0])),
            "form_name_changed": (top_field(left, "inputs", "form_name") or (left_outline.get("form_names", [None])[0])) != (top_field(right, "inputs", "form_name") or (right_outline.get("form_names", [None])[0])),
            "input_frame_path_changed": (top_field(left, "inputs", "frame_path") or metadata(left).get("top_input_frame_path")) != (top_field(right, "inputs", "frame_path") or metadata(right).get("top_input_frame_path")),
            "input_frame_depth_changed": (top_int_field(left, "inputs", "frame_depth") if top_int_field(left, "inputs", "frame_depth") is not None else metadata(left).get("top_input_frame_depth")) != (top_int_field(right, "inputs", "frame_depth") if top_int_field(right, "inputs", "frame_depth") is not None else metadata(right).get("top_input_frame_depth")),
            "output_frame_path_changed": (top_field(left, "outputs", "frame_path") or metadata(left).get("top_output_frame_path")) != (top_field(right, "outputs", "frame_path") or metadata(right).get("top_output_frame_path")),
            "output_frame_depth_changed": (top_int_field(left, "outputs", "frame_depth") if top_int_field(left, "outputs", "frame_depth") is not None else metadata(left).get("top_output_frame_depth")) != (top_int_field(right, "outputs", "frame_depth") if top_int_field(right, "outputs", "frame_depth") is not None else metadata(right).get("top_output_frame_depth")),
            "option_count_changed": top_option_count(left, "inputs") != top_option_count(right, "inputs"),
            "selected_option_changed": top_selected_option(left, "inputs") != top_selected_option(right, "inputs"),
            "checked_state_changed": top_field(left, "inputs", "checked_state") != top_field(right, "inputs", "checked_state"),
            "disabled_changed": top_bool_field(left, "inputs", "disabled") != top_bool_field(right, "inputs", "disabled"),
            "readonly_changed": top_bool_field(left, "inputs", "readonly") != top_bool_field(right, "inputs", "readonly"),
            "multiple_changed": top_bool_field(left, "inputs", "multiple") != top_bool_field(right, "inputs", "multiple"),
            "selected_count_changed": top_int_field(left, "inputs", "selected_count") != top_int_field(right, "inputs", "selected_count"),
            "autocomplete_changed": top_field(left, "inputs", "autocomplete") != top_field(right, "inputs", "autocomplete"),
            "input_mode_changed": top_field(left, "inputs", "input_mode") != top_field(right, "inputs", "input_mode"),
            "choice_group_changed": top_field(left, "inputs", "choice_group") != top_field(right, "inputs", "choice_group"),
            "constraint_hints_changed": top_list_field(left, "inputs", "constraint_hints") != top_list_field(right, "inputs", "constraint_hints"),
            "constraint_flags_changed": top_list_field(left, "inputs", "constraint_flags") != top_list_field(right, "inputs", "constraint_flags"),
            "submit_label_changed": top_submit_label(left) != top_submit_label(right),
            "submit_action_changed": top_submit_action(left) != top_submit_action(right),
            "submit_frame_path_changed": metadata(left).get("top_submit_frame_path") != metadata(right).get("top_submit_frame_path"),
            "submit_action_kind_changed": top_submit_action_kind(left) != top_submit_action_kind(right),
            "submit_locator_strategy_changed": top_submit_locator_strategy(left) != top_submit_locator_strategy(right),
            "submit_locator_root_changed": top_submit_locator_root(left) != top_submit_locator_root(right),
            "submit_locator_root_strategy_changed": top_submit_locator_root_strategy(left) != top_submit_locator_root_strategy(right),
            "submit_locator_hint_changed": top_submit_locator_hints(left) != top_submit_locator_hints(right),
            "form_action_changed": left_form_action != right_form_action,
            "heading_outline_changed": left_outline.get("heading_outline", []) != right_outline.get("heading_outline", []),
            "control_kinds_changed": left_outline.get("control_kinds", []) != right_outline.get("control_kinds", []),
            "form_names_changed": left_outline.get("form_names", []) != right_outline.get("form_names", []),
            "dialog_names_changed": left_outline.get("dialog_names", []) != right_outline.get("dialog_names", []),
            "iframe_names_changed": left_outline.get("iframe_names", []) != right_outline.get("iframe_names", []),
            "iframe_titles_changed": left_outline.get("iframe_titles", []) != right_outline.get("iframe_titles", []),
            "frame_paths_changed": left_outline.get("frame_paths", []) != right_outline.get("frame_paths", []),
            "accessible_iframe_count_changed": metadata(left).get("accessible_iframe_count") != metadata(right).get("accessible_iframe_count"),
            "blocked_iframe_count_changed": metadata(left).get("blocked_iframe_count") != metadata(right).get("blocked_iframe_count"),
            "blocked_iframe_names_changed": metadata(left).get("blocked_iframe_names") != metadata(right).get("blocked_iframe_names"),
            "blocked_iframe_titles_changed": metadata(left).get("blocked_iframe_titles") != metadata(right).get("blocked_iframe_titles"),
            "blocked_frame_paths_changed": metadata(left).get("blocked_frame_paths") != metadata(right).get("blocked_frame_paths"),
            "traversed_document_count_changed": metadata(left).get("traversed_document_count") != metadata(right).get("traversed_document_count"),
            "total_iframe_count_changed": metadata(left).get("total_iframe_count") != metadata(right).get("total_iframe_count"),
            "frame_capture_ratio_changed": metadata(left).get("frame_capture_ratio") != metadata(right).get("frame_capture_ratio"),
            "frame_capture_status_changed": metadata(left).get("frame_capture_status") != metadata(right).get("frame_capture_status"),
            "frame_capture_warning_changed": metadata(left).get("frame_capture_warning") != metadata(right).get("frame_capture_warning"),
            "max_frame_depth_changed": metadata(left).get("max_frame_depth") != metadata(right).get("max_frame_depth"),
            "split_scope_changed": metadata(left).get("split_scope_detected") != metadata(right).get("split_scope_detected"),
            "option_labels_changed": left_outline.get("option_labels", []) != right_outline.get("option_labels", []),
            "choice_groups_changed": left_outline.get("choice_groups", []) != right_outline.get("choice_groups", []),
            "autocomplete_tokens_changed": left_outline.get("autocomplete_tokens", []) != right_outline.get("autocomplete_tokens", []),
            "state_flags_changed": left_outline.get("state_flags", []) != right_outline.get("state_flags", []),
            "constraint_outline_changed": left_outline.get("constraint_hints", []) != right_outline.get("constraint_hints", []),
            "link_hosts_changed": left_outline.get("link_hosts", []) != right_outline.get("link_hosts", []),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two GlassTTY fixture JSON files")
    parser.add_argument("left")
    parser.add_argument("right")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(compare_payloads(load_fixture(Path(args.left)), load_fixture(Path(args.right))), indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
