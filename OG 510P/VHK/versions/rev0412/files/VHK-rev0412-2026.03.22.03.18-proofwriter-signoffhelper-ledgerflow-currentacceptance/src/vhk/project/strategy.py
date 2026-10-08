from __future__ import annotations

"""Project-shape analysis and strategy recommendations.

This module turns a VHK project into a concise description of *what kind* of
automation surface it is becoming. The goal is not strict validation; VHK
already has validate/lint/doctor for that. Instead, this module answers:

- Which macro archetypes exist in the project?
- Which trigger surfaces are being used?
- Which Linux-native integration patterns should the author lean into?

The heuristics are intentionally simple and explainable so they can evolve as
VHK grows toward a fuller Studio.
"""

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path
import re
import shlex
from typing import Any
from types import SimpleNamespace

from vhk.project.claim_witness import claim_host_fit_for_target, claim_host_review_summary, claim_host_witness_contract, recommended_claim_level
from vhk.project.window_contracts import summarize_project_window_contract
from vhk.system import input as input_mod

_NESTED_FIELDS: tuple[str, ...] = ("steps", "then_steps", "else_steps", "catch_steps", "finally_steps")

_SCREEN_TYPES = {
    "CaptureScreenshot",
    "ImageSearchFile",
    "ImageSearchAllFile",
    "WaitForImageFile",
    "PixelSearchFile",
    "PixelSearchAllFile",
    "WaitForPixelFile",
    "PixelGetColorFile",
    "OcrReadTextFile",
    "OcrFindTextFile",
    "OcrFindTextAllFile",
    "ImageSearch",
    "ImageSearchAll",
    "WaitForImage",
    "WaitForImageAll",
    "WaitForImageVanish",
    "ClickImageAll",
    "PixelSearch",
    "PixelSearchAll",
    "WaitForPixel",
    "WaitForPixelAll",
    "WaitForPixelVanish",
    "ClickPixelAll",
    "PixelGetColor",
    "OcrReadText",
    "OcrNeedleText",
    "WaitForNeedleText",
    "WaitForText",
    "WaitForTextVanish",
    "AssertText",
    "OcrFindText",
    "OcrFindTextAll",
    "WaitForTextBox",
    "ClickText",
    "ClickTextAll",
    "VisualAssert",
    "VisualVerify",
    "WaitForRegionChange",
    "WaitForRegionStable",
    "ClickNeedle",
}

_TEXT_TYPES = {"TypeText", "PasteClipboard", "Key", "KeyDown", "KeyUp", "ResetModifiers"}
_POINTER_TYPES = {"MouseMove", "MouseClick", "MouseClickAt", "MouseDrag", "MouseWheel", "ClickNeedle", "ClickImageAll", "ClickPixelAll", "ClickText", "ClickTextAll"}
_WINDOW_TYPES = {"CoordMode", "WaitForWindow", "WaitForWindowVanish", "FocusWindow", "GetCursorPos", "GetActiveWindow", "GetWindowAtCursor", "GetWindowList"}
_PROMPT_TYPES = {"PromptForm", "InputBox", "ChooseFromList", "AskYesNo", "ShowMessage"}
_PROCESS_TYPES = {"StartProcess", "WaitForProcessExit", "KillProcess", "RunShell", "OpenUrl", "ComposeEmail", "GetSystemdUnitState", "WaitForSystemdUnitState"}
_DATA_TYPES = {
    "ReadCsv",
    "WriteCsv",
    "ReadJson",
    "WriteJson",
    "ReadFile",
    "WriteFile",
    "AppendFile",
    "ListDirectory",
    "WaitForFile",
    "WaitForNewFile",
    "WaitForFileEvent",
    "WaitForDownload",
    "HttpRequest",
    "DownloadFile",
}
_CONTROL_TYPES = {"If", "While", "Try", "ForEach", "Break", "Continue", "Return", "SetVar", "RandomWait", "Delay", "Log"}
_WATCHER_TYPES = {"WaitForClipboardChange", "WaitForClipboardEvent", "WaitForBusEvent", "WaitForWindowEvent", "WaitForFileEvent", "WaitForDbusSignal", "WaitForSystemdUnitState"}

_VISION_WAIT_TYPES = {"WaitForImage", "WaitForImageAll", "WaitForImageFile", "WaitForText", "WaitForTextBox", "WaitForTextVanish", "WaitForNeedleText", "WaitForPixel", "WaitForPixelAll", "WaitForPixelFile", "WaitForRegionChange", "WaitForRegionStable"}

_LIVE_CAPTURE_TYPES = {
    "CaptureScreenshot",
    "ImageSearch",
    "ImageSearchAll",
    "WaitForImage",
    "WaitForImageAll",
    "WaitForImageVanish",
    "ClickImageAll",
    "PixelSearch",
    "PixelSearchAll",
    "WaitForPixel",
    "WaitForPixelAll",
    "WaitForPixelVanish",
    "ClickPixelAll",
    "PixelGetColor",
    "OcrReadText",
    "OcrNeedleText",
    "WaitForNeedleText",
    "WaitForText",
    "WaitForTextVanish",
    "AssertText",
    "OcrFindText",
    "OcrFindTextAll",
    "WaitForTextBox",
    "ClickText",
    "ClickTextAll",
    "VisualAssert",
    "VisualVerify",
    "WaitForRegionChange",
    "WaitForRegionStable",
    "ClickNeedle",
}

_OCR_TYPES = {
    "OcrReadText",
    "OcrNeedleText",
    "WaitForNeedleText",
    "WaitForText",
    "WaitForTextVanish",
    "AssertText",
    "OcrFindText",
    "OcrFindTextAll",
    "WaitForTextBox",
    "ClickText",
    "ClickTextAll",
}

_EVENT_WAIT_TYPES = {
    "WaitForBusEvent",
    "WaitForDbusSignal",
    "WaitForWindowEvent",
    "WaitForFileEvent",
}

_HYBRID_WAIT_TYPES = {
    "WaitForClipboardEvent",
}


def _intish(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return int(default)
        return int(value)
    except Exception:
        return int(default)


def _floatish(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None

_TYPED_TEXT_THROUGHPUT_MIN_CHARS = 80
_STRUCTURED_TYPED_TEXT_MIN_CHARS = 24
_INTERP_PAT = re.compile(r"\$\{[^}]+\}")


def _literal_text_throughput(step: Any) -> dict[str, int]:
    if str(getattr(step, "type", "") or "") != "TypeText":
        return {}
    text = getattr(step, "text", None)
    if not isinstance(text, str) or not text:
        return {}
    backend = str(getattr(step, "backend", "auto") or "auto").strip().lower() or "auto"
    if backend in {"clipboard", "xvkbd"}:
        return {"clipboard_text_steps": 1, "clipboard_text_chars": len(text)}
    if int(getattr(step, "delay_ms_per_char", 0) or 0) != 0:
        return {}
    if _INTERP_PAT.search(text):
        return {}
    if not input_mod.text_looks_paste_friendly(text):
        return {}
    out = {
        "literal_type_steps": 1,
        "literal_type_chars": len(text),
    }
    if len(text) >= _TYPED_TEXT_THROUGHPUT_MIN_CHARS:
        out["long_literal_type_steps"] = 1
        out["long_literal_type_chars"] = len(text)
    if ("\n" in text or "\t" in text) and len(text) >= _STRUCTURED_TYPED_TEXT_MIN_CHARS:
        out["structured_literal_type_steps"] = 1
        out["structured_literal_type_chars"] = len(text)
    return out



def _iter_steps(steps: Iterable[Any], *, prefix: str = "steps") -> Iterable[tuple[Any, str]]:
    for i, step in enumerate(steps or []):
        path = f"{prefix}[{i}]"
        yield step, path
        step_type = getattr(step, "type", None)
        if step_type == "If":
            yield from _iter_steps(getattr(step, "then_steps", []) or [], prefix=f"{path}.then_steps")
            yield from _iter_steps(getattr(step, "else_steps", []) or [], prefix=f"{path}.else_steps")
        elif step_type == "While":
            yield from _iter_steps(getattr(step, "steps", []) or [], prefix=f"{path}.steps")
        elif step_type == "Try":
            yield from _iter_steps(getattr(step, "steps", []) or [], prefix=f"{path}.steps")
            yield from _iter_steps(getattr(step, "catch_steps", []) or [], prefix=f"{path}.catch_steps")
            yield from _iter_steps(getattr(step, "finally_steps", []) or [], prefix=f"{path}.finally_steps")
        elif step_type == "ForEach":
            yield from _iter_steps(getattr(step, "steps", []) or [], prefix=f"{path}.steps")


def _macro_triggers(project) -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    for binding in getattr(project, "bindings", []) or []:
        out[str(binding.macro)].append("hotkey")
    for hotstring in getattr(project, "hotstrings", []) or []:
        if getattr(hotstring, "enabled", True):
            out[str(hotstring.macro)].append("hotstring")
    for watcher in getattr(project, "clipboard_watchers", []) or []:
        out[str(watcher.macro)].append("clipboard-watcher")
    for watcher in getattr(project, "window_watchers", []) or []:
        out[str(watcher.macro)].append("window-watcher")
    for watcher in getattr(project, "bus_watchers", []) or []:
        macro = getattr(watcher, "macro", None)
        if macro:
            out[str(macro)].append("bus-watcher")
    for macro_name, macro in getattr(project, "macros", {}).items():
        if not out.get(str(macro_name)) and not getattr(macro, "hidden", False):
            out[str(macro_name)].append("palette")
    for macro_name in list(out):
        deduped: list[str] = []
        for item in out[macro_name]:
            if item not in deduped:
                deduped.append(item)
        out[macro_name] = deduped
    return out


def _classify_macro(*, macro, triggers: list[str]) -> dict[str, Any]:
    counts = Counter()
    step_types = Counter()
    issues = Counter()
    perf = Counter()
    total_steps = 0
    max_depth = 0

    for step, path in _iter_steps(getattr(macro, "steps", []) or []):
        total_steps += 1
        depth = path.count("[")
        max_depth = max(max_depth, depth)
        step_type = str(getattr(step, "type", "") or "")
        step_types[step_type] += 1
        if step_type in _SCREEN_TYPES:
            counts["screen"] += 1
        if step_type in _TEXT_TYPES:
            counts["text"] += 1
        if step_type in _POINTER_TYPES or step_type.startswith("Mouse"):
            counts["pointer"] += 1
        if step_type in _WINDOW_TYPES:
            counts["window"] += 1
        if step_type in _PROMPT_TYPES:
            counts["prompt"] += 1
        if step_type in _PROCESS_TYPES:
            counts["process"] += 1
        if step_type in _DATA_TYPES:
            counts["data"] += 1
        if step_type in _CONTROL_TYPES:
            counts["control"] += 1
        if step_type in _WATCHER_TYPES:
            counts["watch"] += 1
        if step_type in _VISION_WAIT_TYPES:
            counts["vision_wait"] += 1

        if step_type in _LIVE_CAPTURE_TYPES:
            perf["live_capture_steps"] += 1
            if getattr(step, "region", None) is None:
                perf["unscoped_live_capture_steps"] += 1
        if step_type in _OCR_TYPES:
            perf["ocr_steps"] += 1
        if step_type in _EVENT_WAIT_TYPES:
            perf["event_wait_steps"] += 1
        if step_type in _HYBRID_WAIT_TYPES:
            perf["hybrid_wait_steps"] += 1

        poll_ms = _intish(getattr(step, "poll_ms", None), default=0)
        scan_rate_hz = _floatish(getattr(step, "scan_rate_hz", None))
        if poll_ms > 0 or scan_rate_hz is not None:
            perf["polling_wait_steps"] += 1
            if (poll_ms > 0 and poll_ms <= 150) or (scan_rate_hz is not None and scan_rate_hz >= 8.0):
                perf["low_poll_wait_steps"] += 1
        timeout_ms = _intish(getattr(step, "timeout_ms", None), default=0)
        if timeout_ms > 0:
            perf["declared_wait_timeout_ms"] += timeout_ms

        if step_type == "Delay":
            ms = _intish(getattr(step, "ms", 0), default=0)
            perf["declared_delay_ms"] += ms
            if ms >= 1500:
                issues["long_delay"] += 1
                perf["long_delay_steps"] += 1
        if step_type == "MouseClickAt":
            issues["coord_click"] += 1
        if step_type in {"KeyDown", "KeyUp"}:
            issues["raw_key_events"] += 1

        for key, value in _literal_text_throughput(step).items():
            perf[key] += int(value)

    tags: list[str] = []
    if counts["screen"] >= 2 or (total_steps and counts["screen"] / float(total_steps) >= 0.3):
        tags.append("vision-heavy")
    if counts["text"] > 0 and counts["pointer"] == 0 and counts["screen"] == 0 and ("hotstring" in triggers or step_types.get("Return", 0) > 0):
        tags.append("text-expander")
    if counts["window"] > 0 and counts["screen"] <= 1:
        tags.append("wm-native")
    if counts["process"] > 0 and counts["screen"] == 0 and counts["pointer"] == 0:
        tags.append("orchestrator")
    if counts["prompt"] > 0 or getattr(macro, "presets", []):
        tags.append("parameterized")
    if counts["data"] > 0:
        tags.append("data-glue")
    if counts["control"] >= 3 or max_depth >= 3:
        tags.append("flow-heavy")
    if any(t.endswith("watcher") for t in triggers):
        tags.append("event-driven")
    if not tags and counts["pointer"] > 0:
        tags.append("interaction")
    if not tags:
        tags.append("utility")

    perf_tags: list[str] = []
    if perf["live_capture_steps"] >= 3 or (total_steps and perf["live_capture_steps"] / float(total_steps) >= 0.35):
        perf_tags.append("capture-heavy")
    if perf["ocr_steps"] >= 2 or (total_steps and perf["ocr_steps"] / float(total_steps) >= 0.2):
        perf_tags.append("ocr-heavy")
    if perf["unscoped_live_capture_steps"] > 0:
        perf_tags.append("unscoped-vision")
    if perf["polling_wait_steps"] >= 2 or perf["low_poll_wait_steps"] > 0:
        perf_tags.append("poll-heavy")
    if perf["event_wait_steps"] > 0:
        perf_tags.append("event-ready")
    if ("hotkey" in triggers or "bus-watcher" in triggers) and ("vision-heavy" in tags or perf["ocr_steps"] > 0 or perf["long_delay_steps"] > 0):
        perf_tags.append("dispatch-sensitive")
    if perf["long_literal_type_steps"] > 0 or perf["structured_literal_type_steps"] > 0:
        perf_tags.append("text-throughput")
    if perf["structured_literal_type_steps"] > 0:
        perf_tags.append("structured-text")

    risk_score = (
        int(perf["unscoped_live_capture_steps"]) * 6
        + int(perf["low_poll_wait_steps"]) * 4
        + int(perf["long_delay_steps"]) * 3
        + int(perf["ocr_steps"]) * 2
        + int(perf["polling_wait_steps"])
        + max(0, int(perf["live_capture_steps"]) - 2)
        + int(perf["long_literal_type_steps"]) * 2
        + (1 if int(perf["structured_literal_type_steps"]) > 0 else 0)
        + int(perf["long_literal_type_chars"]) // 400
    )
    if perf["event_wait_steps"] > 0:
        risk_score = max(0, risk_score - 1)
    if risk_score >= 12:
        risk_level = "high"
    elif risk_score >= 6:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "macro": str(getattr(macro, "name", "") or ""),
        "description": getattr(macro, "description", None),
        "group": getattr(macro, "group", None),
        "hidden": bool(getattr(macro, "hidden", False)),
        "triggers": triggers,
        "tags": tags,
        "step_count": total_steps,
        "max_depth": max_depth,
        "step_type_counts": dict(step_types),
        "feature_counts": dict(counts),
        "smells": dict(issues),
        "preset_count": len(getattr(macro, "presets", []) or []),
        "performance": {
            "tags": perf_tags,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "live_capture_steps": int(perf["live_capture_steps"]),
            "unscoped_live_capture_steps": int(perf["unscoped_live_capture_steps"]),
            "ocr_steps": int(perf["ocr_steps"]),
            "polling_wait_steps": int(perf["polling_wait_steps"]),
            "low_poll_wait_steps": int(perf["low_poll_wait_steps"]),
            "event_wait_steps": int(perf["event_wait_steps"]),
            "hybrid_wait_steps": int(perf["hybrid_wait_steps"]),
            "declared_delay_ms": int(perf["declared_delay_ms"]),
            "long_delay_steps": int(perf["long_delay_steps"]),
            "literal_type_steps": int(perf["literal_type_steps"]),
            "literal_type_chars": int(perf["literal_type_chars"]),
            "long_literal_type_steps": int(perf["long_literal_type_steps"]),
            "long_literal_type_chars": int(perf["long_literal_type_chars"]),
            "structured_literal_type_steps": int(perf["structured_literal_type_steps"]),
            "structured_literal_type_chars": int(perf["structured_literal_type_chars"]),
            "clipboard_text_steps": int(perf["clipboard_text_steps"]),
            "clipboard_text_chars": int(perf["clipboard_text_chars"]),
            "declared_wait_timeout_ms": int(perf["declared_wait_timeout_ms"]),
        },
    }



def _product_lanes(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    macro_profiles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    lanes: list[dict[str, Any]] = []

    def add(id: str, score: int, title: str, focus: str, summary: str, *, evidence: list[str] | None = None) -> None:
        lanes.append({
            "id": id,
            "score": max(0, min(int(score), 100)),
            "title": title,
            "focus": focus,
            "summary": summary,
            "evidence": list(evidence or []),
        })

    raw_key_events = sum(int((m.get("smells") or {}).get("raw_key_events") or 0) for m in macro_profiles)
    vision_macros = [m for m in macro_profiles if "vision-heavy" in (m.get("tags") or [])]
    text_macros = [m for m in macro_profiles if "text-expander" in (m.get("tags") or [])]
    event_macros = [m for m in macro_profiles if "event-driven" in (m.get("tags") or [])]
    orchestrators = [m for m in macro_profiles if "orchestrator" in (m.get("tags") or []) or "data-glue" in (m.get("tags") or []) or "flow-heavy" in (m.get("tags") or [])]

    trigger_score = min(100, int(overview.get("bindings") or 0) * 35 + int(overview.get("window_watchers") or 0) * 20 + int(overview.get("bus_watchers") or 0) * 20)
    if trigger_score:
        evidence: list[str] = []
        if overview.get("bindings"):
            evidence.append(f"{overview.get('bindings')} binding(s)")
        if overview.get("window_watchers"):
            evidence.append(f"{overview.get('window_watchers')} window watcher(s)")
        if overview.get("bus_watchers"):
            evidence.append(f"{overview.get('bus_watchers')} bus watcher(s)")
        add(
            "trigger-plane",
            trigger_score,
            "Trigger plane",
            "Low-latency dispatch and session entrypoints",
            "Keep global activation thin: WM/compositor binds, portal shortcuts when they really exist, or small hotkey helpers should wake the heavier runner only when needed.",
            evidence=evidence,
        )

    text_score = min(100, int(overview.get("hotstrings") or 0) * 40 + len(text_macros) * 25 + (15 if "parameterized" in project_tags else 0))
    if text_score:
        evidence = []
        if overview.get("hotstrings"):
            evidence.append(f"{overview.get('hotstrings')} hotstring(s)")
        evidence.extend(str(item.get("macro")) for item in text_macros[:3])
        add(
            "text-tier",
            text_score,
            "Text tier",
            "Snippet expansion, forms, and app-scoped writing flows",
            "Treat text automation as its own fast lane with variables, forms, and include/exclude rules instead of replaying every snippet through the full macro runtime.",
            evidence=evidence,
        )

    visual_score = min(100, len(vision_macros) * 40 + (20 if "selector-asset-heavy" in project_tags else 0))
    if visual_score:
        add(
            "visual-lane",
            visual_score,
            "Visual lane",
            "Selector assets, bounded search, and replay diagnostics",
            "Vision-heavy projects need needles, OCR boxes, named regions, and run inspection to become portable. Treat those assets like code, not throwaway screenshots.",
            evidence=[str(item.get("macro")) for item in vision_macros[:4]],
        )

    event_score = min(100, int(overview.get("bus_watchers") or 0) * 30 + int(overview.get("clipboard_watchers") or 0) * 20 + int(overview.get("file_watchers") or 0) * 20 + int(overview.get("window_watchers") or 0) * 25 + len(event_macros) * 15)
    if event_score:
        evidence = []
        if overview.get("bus_watchers"):
            evidence.append(f"{overview.get('bus_watchers')} bus watcher(s)")
        if overview.get("clipboard_watchers"):
            evidence.append(f"{overview.get('clipboard_watchers')} clipboard watcher(s)")
        if overview.get("file_watchers"):
            evidence.append(f"{overview.get('file_watchers')} file watcher(s)")
        if overview.get("window_watchers"):
            evidence.append(f"{overview.get('window_watchers')} window watcher(s)")
        add(
            "event-bridge",
            event_score,
            "Event bridge",
            "Watchers, daemons, and external emitters",
            "A Linux-native stack gets stronger when clipboard, DBus, window, and WM events arrive through dedicated watchers instead of constant polling inside the runner.",
            evidence=evidence,
        )

    remap_score = min(100, int(overview.get("bindings") or 0) * 25 + raw_key_events * 15)
    if remap_score:
        evidence = []
        if overview.get("bindings"):
            evidence.append(f"{overview.get('bindings')} binding(s)")
        if raw_key_events:
            evidence.append(f"{raw_key_events} raw key event(s)")
        add(
            "remap-surface",
            remap_score,
            "Remap surface",
            "External remappers and exported trigger configs",
            "Keep ergonomic remapping, tap-hold logic, and ultra-low-latency key interception close to evdev/compositor tools. VHK should integrate with that layer, not impersonate it poorly.",
            evidence=evidence,
        )

    orchestration_score = min(100, len(orchestrators) * 20)
    if orchestration_score:
        add(
            "orchestration",
            orchestration_score,
            "Orchestration",
            "Process glue, data handling, and flow control",
            "Projects that mix process launching, files, HTTP, prompts, and loops want reliable runtime state, not just hotkeys. Keep this lane explicit so it can grow into a stable automation engine.",
            evidence=[str(item.get("macro")) for item in orchestrators[:4]],
        )

    lanes.sort(key=lambda item: (-int(item.get("score") or 0), str(item.get("title") or "")))
    return lanes


def _implementation_playbooks(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    macro_profiles: list[dict[str, Any]],
    capability_matrix: Mapping[str, Any] | None = None,
    capability_issues: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    playbooks: list[dict[str, Any]] = []
    backend = str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "").strip().lower()
    capability_issues = list(capability_issues or [])
    root_q = shlex.quote(str(getattr(project, "root_dir", ".") or "."))

    def add(
        id: str,
        priority: str,
        title: str,
        goal: str,
        commands: list[str],
        *,
        related_targets: list[str] | None = None,
        evidence: list[str] | None = None,
    ) -> None:
        playbooks.append({
            "id": id,
            "priority": priority,
            "title": title,
            "goal": goal,
            "commands": list(commands),
            "related_targets": list(related_targets or []),
            "evidence": list(evidence or []),
        })

    vision_macros = [m for m in macro_profiles if "vision-heavy" in (m.get("tags") or [])]
    raw_key_events = sum(int((m.get("smells") or {}).get("raw_key_events") or 0) for m in macro_profiles)

    if backend == "wayland" or capability_issues:
        evidence = [f"desktop_backend={backend or 'unknown'}"]
        evidence.extend(str(item.get("capability")) for item in capability_issues[:3] if item.get("capability"))
        add(
            "deployment-audit",
            "high",
            "Lock down a target-desktop deployment profile.",
            "Capture the real capability matrix before you promise portability. This should become the first loop for every serious Wayland-facing project.",
            [
                "vhk doctor --json",
                f"vhk validate {root_q} --json",
                f"vhk plan-project {root_q} --json",
            ],
            related_targets=["trigger-plane", "wayland-injection"],
            evidence=evidence,
        )

    if overview.get("hotstrings") or any("text-expander" in (m.get("tags") or []) for m in macro_profiles):
        evidence = []
        if overview.get("hotstrings"):
            evidence.append(f"{overview.get('hotstrings')} hotstring(s)")
        add(
            "text-export-loop",
            "high",
            "Prototype the text tier as an exported package, not just inline macros.",
            "Keep snippet workflows fast and scoped. Export them, validate them, and iterate on forms/app filters independently from the rest of the project.",
            [
                f"vhk gen-espanso {root_q} --package-dir ./build/espanso_package",
                f"vhk validate {root_q} --json",
            ],
            related_targets=["text-tier"],
            evidence=evidence,
        )

    if vision_macros or "selector-asset-heavy" in project_tags:
        add(
            "selector-debug-loop",
            "high",
            "Turn visual macros into inspectable selector assets.",
            "Make the visual lane measurable: optimize the recorded draft, inspect a real run log, and preview selector matches against representative screenshots.",
            [
                f"vhk optimize-project {root_q}",
                f"vhk report --project {root_q} --latest --json",
                f"vhk preview-needle path/to/needle.png --project {root_q} --haystack path/to/screenshot.png --json --no-check",
            ],
            related_targets=["selector-pack"],
            evidence=[str(item.get("macro")) for item in vision_macros[:4]],
        )

    if overview.get("bindings") or raw_key_events:
        evidence = []
        if overview.get("bindings"):
            evidence.append(f"{overview.get('bindings')} binding(s)")
        if raw_key_events:
            evidence.append(f"{raw_key_events} raw key event(s)")
        add(
            "remap-export-loop",
            "medium",
            "Compare remap/export surfaces instead of hard-coding one trigger story.",
            "Generate candidate trigger configs for the remapper layer and choose the one that fits the target desktop/session instead of assuming the Python runner should own always-on key logic.",
            [
                f"vhk gen-keyd-config {root_q} --out ./build/vhk.keyd.conf",
                f"vhk gen-kanata-config {root_q} --out ./build/vhk.kanata.kbd",
                f"vhk gen-kmonad-config {root_q} --out ./build/vhk.kmonad.kbd",
            ],
            related_targets=["trigger-plane", "remap-surface"],
            evidence=evidence,
        )

    if "daemon-friendly" in project_tags:
        add(
            "dispatch-daemon-loop",
            "medium",
            "Package the watcher/event plane as user services.",
            "Systemd user units keep bus-driven automation reproducible. Generate service artifacts early so event-triggered projects do not depend on a hand-started terminal process forever.",
            [
                f"vhk gen-vhk-busd-service {root_q} --out-dir ./build/systemd-user",
                f"vhk gen-vhk-busd-socket-units {root_q} --out-dir ./build/systemd-user",
            ],
            related_targets=["event-bridge"],
            evidence=["watchers or event triggers present"],
        )

    return playbooks

def _recommendations(*, project, macro_profiles: list[dict[str, Any]], capability_usage: Mapping[str, list[dict[str, object]]], capability_matrix: Mapping[str, Any] | None = None, capability_issues: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    recs: list[dict[str, Any]] = []

    def add(id: str, category: str, severity: str, summary: str, details: str, *, evidence: list[str] | None = None) -> None:
        recs.append({
            "id": id,
            "category": category,
            "severity": severity,
            "summary": summary,
            "details": details,
            "evidence": list(evidence or []),
        })

    vision_macros = [m for m in macro_profiles if "vision-heavy" in (m.get("tags") or [])]
    text_macros = [m for m in macro_profiles if "text-expander" in (m.get("tags") or [])]
    parameterized = [m for m in macro_profiles if "parameterized" in (m.get("tags") or [])]
    watcher_macros = [m for m in macro_profiles if "event-driven" in (m.get("tags") or [])]
    raw_macro_smells = [m for m in macro_profiles if (m.get("smells") or {}).get("coord_click") or (m.get("smells") or {}).get("long_delay") or (m.get("smells") or {}).get("raw_key_events")]

    if watcher_macros or getattr(project, "bindings", []) or getattr(project, "bus_watchers", []) or getattr(project, "file_watchers", []) or getattr(project, "window_watchers", []):
        evidence = []
        if getattr(project, "bindings", []):
            evidence.append(f"{len(project.bindings)} hotkey binding(s)")
        if getattr(project, "window_watchers", []):
            evidence.append(f"{len(project.window_watchers)} window watcher(s)")
        if getattr(project, "bus_watchers", []):
            evidence.append(f"{len(project.bus_watchers)} bus watcher(s)")
        if getattr(project, "file_watchers", []):
            evidence.append(f"{len(project.file_watchers)} file watcher(s)")
        add(
            "dispatch-plane",
            "architecture",
            "info",
            "Separate low-latency triggers from the heavier authoring/runtime CLI.",
            "Lean on WM bindings, busd/watchers, and lightweight emitters for always-on triggers. Keep the main runner focused on sequencing, diagnostics, and reproducible macro execution.",
            evidence=evidence,
        )

    if text_macros or getattr(project, "hotstrings", []):
        evidence = [f"{len(project.hotstrings)} hotstring(s)"] if getattr(project, "hotstrings", []) else []
        evidence.extend(m.get("macro") for m in text_macros[:3])
        add(
            "text-tier",
            "product-shape",
            "info",
            "Treat text expansion as its own product tier inside VHK, not a side effect of full macro playback.",
            "Prefer return-value or clipboard-oriented text macros for hotstrings, preserve app/window scoping where possible, and keep structured PromptForm/preset flows available for parameter collection.",
            evidence=evidence,
        )

    if parameterized:
        evidence = [f"{sum(int(m.get('preset_count') or 0) for m in parameterized)} preset(s) across {len(parameterized)} macro(s)"]
        evidence.extend(m.get("macro") for m in parameterized[:3])
        add(
            "parameters-first",
            "authoring",
            "info",
            "Lean into presets, prompt profiles, and palette launches instead of copying similar macros.",
            "When a workflow differs by only a few stable variables, keep one macro graph and surface variants through presets plus small prompt overlays. This keeps projects diffable and studio-friendly.",
            evidence=evidence,
        )

    if vision_macros:
        evidence = [m.get("macro") for m in vision_macros[:4]]
        add(
            "selector-assets",
            "robustness",
            "warning",
            "This project is vision-heavy; invest in selector assets and bounded search regions early.",
            "Use named regions, needle metadata, OCR boxes, preview-needle, and post-recording cleanup. VHK should organize images and search scopes like first-class project assets, not loose screenshots.",
            evidence=evidence,
        )

    if raw_macro_smells:
        evidence = []
        for item in raw_macro_smells[:4]:
            smells = item.get("smells") or {}
            bits: list[str] = []
            if smells.get("long_delay"):
                bits.append(f"{smells.get('long_delay')} long delay(s)")
            if smells.get("coord_click"):
                bits.append(f"{smells.get('coord_click')} coordinate click(s)")
            if smells.get("raw_key_events"):
                bits.append(f"{smells.get('raw_key_events')} raw key event(s)")
            evidence.append(f"{item.get('macro')}: " + ", ".join(bits))
        add(
            "cleanup-loop",
            "tooling",
            "warning",
            "Some macros still look recorder-heavy and should go through the cleanup loop.",
            "Run optimize-project, scaffold-project, and lint-project after recording. The strong product loop here is record → collapse noise → add selectors/waits → inspect runs, not record → ship raw coordinates and sleeps.",
            evidence=evidence,
        )

    if capability_issues:
        issue = capability_issues[0]
        add(
            "session-mismatch",
            "deployment",
            str(issue.get("severity") or "warning"),
            str(issue.get("message") or "Current session looks mismatched for part of this project."),
            str(issue.get("suggestion") or "Use doctor/validate to confirm the active desktop's capture/injection/hotkey capabilities before treating this as portable automation."),
            evidence=list(issue.get("used_by") or []),
        )

    if capability_matrix:
        pointer = capability_matrix.get("pointer_injection") if isinstance(capability_matrix, Mapping) else None
        screen = capability_matrix.get("screen_capture") if isinstance(capability_matrix, Mapping) else None
        if isinstance(pointer, Mapping) and isinstance(screen, Mapping):
            if str(pointer.get("status") or "") in {"missing", "limited"} and str(screen.get("status") or "") == "ok":
                add(
                    "capture-without-pointer",
                    "linux-native",
                    "info",
                    "Current session can observe more reliably than it can inject pointer input.",
                    "Favor watcher-driven, window-driven, clipboard-driven, and text-centric workflows in this environment. When pointer playback is required, validate the exact helper/compositor path instead of assuming generic Wayland support.",
                    evidence=[f"pointer_injection={pointer.get('status')}", f"screen_capture={screen.get('status')}"] ,
                )

    if not recs:
        add(
            "steady-state",
            "overview",
            "info",
            "Project shape looks balanced.",
            "Keep validating against the target desktop, and prefer higher-level selectors or event-driven triggers whenever they are available.",
        )

    return recs


def _integration_targets(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    macro_profiles: list[dict[str, Any]],
    capability_usage: Mapping[str, list[dict[str, object]]],
    capability_matrix: Mapping[str, Any] | None = None,
    capability_issues: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    backend = str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "").strip().lower()
    capability_issues = list(capability_issues or [])

    def add(id: str, category: str, priority: str, title: str, tool: str, rationale: str, *, evidence: list[str] | None = None) -> None:
        targets.append({
            "id": id,
            "category": category,
            "priority": priority,
            "title": title,
            "tool": tool,
            "rationale": rationale,
            "evidence": list(evidence or []),
        })

    vision_macros = [m for m in macro_profiles if "vision-heavy" in (m.get("tags") or [])]
    watcher_macros = [m for m in macro_profiles if "event-driven" in (m.get("tags") or [])]
    parameterized = [m for m in macro_profiles if "parameterized" in (m.get("tags") or [])]
    recorderish = [
        m
        for m in macro_profiles
        if (m.get("smells") or {}).get("coord_click")
        or (m.get("smells") or {}).get("long_delay")
        or (m.get("smells") or {}).get("raw_key_events")
    ]

    if overview.get("bindings") or overview.get("window_watchers"):
        global_hotkeys = capability_matrix.get("global_hotkeys") if isinstance(capability_matrix, Mapping) else None
        recommended = str(global_hotkeys.get("recommended") or "").strip() if isinstance(global_hotkeys, Mapping) else ""
        status = str(global_hotkeys.get("status") or "").strip() if isinstance(global_hotkeys, Mapping) else ""
        if backend in {"i3", "sway", "hyprland", "kwin"}:
            tool = f"{backend}-native binds + VHK runner"
        elif recommended:
            tool = recommended
        elif status in {"missing", "limited"}:
            tool = "WM/compositor binds or sxhkd/keyd"
        else:
            tool = "WM/compositor-native hotkeys"
        evidence: list[str] = []
        if overview.get("bindings"):
            evidence.append(f"{overview.get('bindings')} binding(s)")
        if overview.get("window_watchers"):
            evidence.append(f"{overview.get('window_watchers')} window watcher(s)")
        add(
            "trigger-plane",
            "trigger-plane",
            "high",
            "Keep always-on triggers in a thin dispatch plane.",
            tool,
            "Favor WM/compositor-native binds, portal global shortcuts where they are truly available, or a tiny hotkey helper. Let VHK stay focused on sequencing and diagnostics instead of idling as a giant always-on keyboard hook.",
            evidence=evidence,
        )

    if overview.get("hotstrings") or any("text-expander" in (m.get("tags") or []) for m in macro_profiles):
        evidence = []
        if overview.get("hotstrings"):
            evidence.append(f"{overview.get('hotstrings')} hotstring(s)")
        evidence.extend([str(m.get("macro")) for m in macro_profiles if "text-expander" in (m.get("tags") or [])][:3])
        add(
            "text-tier",
            "text-tier",
            "high",
            "Treat phrases/snippets as a dedicated text-automation tier.",
            "VHK hotstrings with Espanso-style app scoping and forms",
            "Text workflows want fast dispatch, structured variables, regex-like triggers, and per-app enable/disable rules. Model them as a first-class tier instead of replaying them through heavyweight macro graphs whenever possible.",
            evidence=evidence,
        )

    if vision_macros or "selector-asset-heavy" in project_tags:
        evidence = [str(m.get("macro")) for m in vision_macros[:4]]
        add(
            "selector-pack",
            "robustness",
            "high",
            "Build a selector asset pack early for vision-heavy flows.",
            "Named regions + needles + OCR boxes + preview tooling",
            "Linux desktop automation gets much more portable when visual steps are organized as assets with bounded search areas and reusable metadata instead of one-off screenshots and full-screen polling.",
            evidence=evidence,
        )

    if watcher_macros or "daemon-friendly" in project_tags:
        evidence = []
        if overview.get("bus_watchers"):
            evidence.append(f"{overview.get('bus_watchers')} bus watcher(s)")
        if overview.get("clipboard_watchers"):
            evidence.append(f"{overview.get('clipboard_watchers')} clipboard watcher(s)")
        if overview.get("file_watchers"):
            evidence.append(f"{overview.get('file_watchers')} file watcher(s)")
        if overview.get("window_watchers"):
            evidence.append(f"{overview.get('window_watchers')} window watcher(s)")
        add(
            "event-bridge",
            "event-plane",
            "medium",
            "Lean on event bridges instead of polling everything from the runner.",
            "busd/window/clipboard watchers + small emitters",
            "A Linux-native automation stack works best when external events arrive through small dedicated watchers and only hand control to the runner when a real workflow needs to execute.",
            evidence=evidence,
        )

    pointer_usage = list(capability_usage.get("pointer_injection") or [])
    if backend == "wayland" and pointer_usage:
        pointer = capability_matrix.get("pointer_injection") if isinstance(capability_matrix, Mapping) else None
        text = capability_matrix.get("text_injection") if isinstance(capability_matrix, Mapping) else None
        recommended = str(pointer.get("recommended") or "").strip() if isinstance(pointer, Mapping) else ""
        pointer_status = str(pointer.get("status") or "").strip() if isinstance(pointer, Mapping) else "unknown"
        text_status = str(text.get("status") or "").strip() if isinstance(text, Mapping) else "unknown"
        priority = "high" if pointer_status in {"missing", "limited"} else "medium"
        tool = recommended or "helper-backed injection adapter (uinput/ydotool/libei-ready)"
        add(
            "wayland-injection",
            "linux-native",
            priority,
            "Keep pointer injection behind a swappable helper boundary on Wayland.",
            tool,
            "Wayland injection support is desktop-specific and often session-scoped. VHK should preserve a clean adapter seam so projects can swap among compositor-native paths, portal-mediated flows, and privileged helpers without changing macro logic.",
            evidence=[f"pointer_injection={pointer_status}", f"text_injection={text_status}", f"{len(pointer_usage)} pointer step(s)"],
        )

    if overview.get("bindings") or any((m.get("smells") or {}).get("raw_key_events") for m in macro_profiles):
        evidence = []
        if overview.get("bindings"):
            evidence.append(f"{overview.get('bindings')} binding(s)")
        raw = sum(int((m.get("smells") or {}).get("raw_key_events") or 0) for m in macro_profiles)
        if raw:
            evidence.append(f"{raw} raw key event(s)")
        add(
            "remap-surface",
            "integration",
            "medium",
            "Keep low-latency remapping distinct from macro execution.",
            "Exports/adapters for keyd, kanata, kmonad, or xremap-class tools",
            "Kernel/compositor-adjacent remappers win on latency and app-scoped key logic. VHK should integrate with them and generate configs where useful instead of forcing the Python runner to impersonate a remapper.",
            evidence=evidence,
        )

    # De-duplicate by id while preserving order.
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in targets:
        item_id = str(item.get("id") or "")
        if not item_id or item_id in seen:
            continue
        seen.add(item_id)
        unique.append(item)
    return unique


def _next_steps(
    *,
    project,
    project_tags: list[str],
    macro_profiles: list[dict[str, Any]],
    capability_matrix: Mapping[str, Any] | None = None,
    capability_issues: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    backend = str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "").strip().lower()
    capability_issues = list(capability_issues or [])

    def add(id: str, priority: str, title: str, details: str, *, related_targets: list[str] | None = None, evidence: list[str] | None = None) -> None:
        steps.append({
            "id": id,
            "priority": priority,
            "title": title,
            "details": details,
            "related_targets": list(related_targets or []),
            "evidence": list(evidence or []),
        })

    recorderish = []
    for item in macro_profiles:
        smells = item.get("smells") or {}
        if smells.get("coord_click") or smells.get("long_delay") or smells.get("raw_key_events"):
            recorderish.append(item)
    if recorderish:
        evidence = []
        for item in recorderish[:4]:
            smells = item.get("smells") or {}
            bits: list[str] = []
            if smells.get("coord_click"):
                bits.append(f"{smells.get('coord_click')} coord click")
            if smells.get("long_delay"):
                bits.append(f"{smells.get('long_delay')} long delay")
            if smells.get("raw_key_events"):
                bits.append(f"{smells.get('raw_key_events')} raw key")
            evidence.append(f"{item.get('macro')}: " + ", ".join(bits))
        add(
            "cleanup-drafts",
            "high",
            "Run the recorder-cleanup loop on the brittle macros first.",
            "Replace coordinate clicks with selectors, shrink long sleeps into explicit waits/retries, and normalize raw key up/down sequences into higher-level text or key steps where possible.",
            related_targets=["selector-pack"],
            evidence=evidence,
        )

    if "selector-asset-heavy" in project_tags:
        evidence = [str(item.get("macro")) for item in macro_profiles if "vision-heavy" in (item.get("tags") or [])][:4]
        add(
            "selector-assets",
            "high",
            "Organize selector assets as a project subsystem, not ad-hoc files.",
            "Create named regions, keep needles focused on stable UI fragments, and add preview/compare metadata so visual steps can be debugged and tuned systematically.",
            related_targets=["selector-pack"],
            evidence=evidence,
        )

    if "parameterized" in project_tags:
        evidence = [str(item.get("macro")) for item in macro_profiles if "parameterized" in (item.get("tags") or [])][:4]
        add(
            "expand-presets",
            "medium",
            "Promote repeated variants into presets and prompt profiles.",
            "Keep one macro graph per workflow and surface environment or customer differences through presets, palette launches, and prompt overlays instead of cloning the whole macro.",
            related_targets=["text-tier"],
            evidence=evidence,
        )

    if backend == "wayland":
        pointer = capability_matrix.get("pointer_injection") if isinstance(capability_matrix, Mapping) else None
        pointer_status = str(pointer.get("status") or "unknown") if isinstance(pointer, Mapping) else "unknown"
        priority = "high" if pointer_status in {"missing", "limited"} or capability_issues else "medium"
        evidence = []
        if pointer_status != "unknown":
            evidence.append(f"pointer_injection={pointer_status}")
        evidence.extend(str(item.get("capability")) for item in capability_issues[:3] if item.get("capability"))
        add(
            "desktop-profiles",
            priority,
            "Author explicit target-desktop profiles for Wayland sessions.",
            "Treat GNOME/KDE/wlroots/Hyprland-class environments as separate deployment profiles with their own hotkey, capture, and injection expectations. Validate each profile instead of claiming generic Wayland parity.",
            related_targets=["trigger-plane", "wayland-injection"],
            evidence=evidence,
        )

    if "text-expander-integration" in project_tags:
        add(
            "app-scoping",
            "medium",
            "Make app-scoped activation a first-class authoring feature.",
            "Extend the existing when/window filters into clearer include/exclude rules for snippets, hotstrings, and trigger exports so projects can behave more like mature Linux text automation tools.",
            related_targets=["text-tier", "trigger-plane"],
            evidence=["project already mixes hotstrings with macro logic"],
        )

    if "daemon-friendly" in project_tags:
        add(
            "emitters",
            "medium",
            "Add tiny emitters and adapters around the runner.",
            "Prefer small scripts or socket hooks that emit bus/window/clipboard events into VHK over embedding every integration into the runner itself.",
            related_targets=["event-bridge"],
            evidence=["watchers/event triggers present"],
        )

    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in steps:
        item_id = str(item.get("id") or "")
        if not item_id or item_id in seen:
            continue
        seen.add(item_id)
        unique.append(item)
    return unique


def _architecture_map(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    macro_profiles: list[dict[str, Any]],
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
    capability_matrix: Mapping[str, Any] | None = None,
    capability_issues: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    backend = str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "").strip().lower()
    capability_usage = capability_usage or {}
    capability_issues = list(capability_issues or [])
    components: list[dict[str, Any]] = []
    risks: list[dict[str, Any]] = []

    def add_component(
        id: str,
        priority: str,
        title: str,
        owner: str,
        tooling: str,
        summary: str,
        *,
        evidence: list[str] | None = None,
    ) -> None:
        components.append({
            "id": id,
            "priority": priority,
            "title": title,
            "owner": owner,
            "tooling": tooling,
            "summary": summary,
            "evidence": list(evidence or []),
        })

    def add_risk(id: str, severity: str, summary: str, *, evidence: list[str] | None = None) -> None:
        risks.append({
            "id": id,
            "severity": severity,
            "summary": summary,
            "evidence": list(evidence or []),
        })

    pointer_usage = list(capability_usage.get("pointer_injection") or [])
    text_usage = list(capability_usage.get("text_injection") or [])
    capture_usage = list(capability_usage.get("screen_capture") or [])
    hotkey_usage = list(capability_usage.get("global_hotkeys") or [])
    raw_key_events = sum(int((m.get("smells") or {}).get("raw_key_events") or 0) for m in macro_profiles)
    vision_macros = [m for m in macro_profiles if "vision-heavy" in (m.get("tags") or [])]
    watcher_macros = [m for m in macro_profiles if "event-driven" in (m.get("tags") or [])]

    stance_parts = ["thin dispatch"]
    if "text-expander-integration" in project_tags:
        stance_parts.append("exported text tier")
    if vision_macros:
        stance_parts.append("selector-driven runner")
    if watcher_macros or "daemon-friendly" in project_tags:
        stance_parts.append("event bridge")
    if backend == "wayland" and pointer_usage:
        stance_parts.append("Wayland helper boundary")
    if overview.get("bindings") or raw_key_events:
        stance_parts.append("external remap surface")

    add_component(
        "runner-core",
        "high",
        "Capability-aware runner core",
        "vhk-core",
        "macro runner + validate + report",
        "Keep sequencing, retries, diagnostics, and asset-aware automation in the core runtime. This is the place where VHK should feel like a Linux-native AHK rather than a pile of shell wrappers.",
        evidence=[f"{overview.get('macros') or 0} macro(s)", f"backend={backend or 'auto'}"],
    )

    if overview.get("bindings") or hotkey_usage or overview.get("window_watchers"):
        evidence = []
        if overview.get("bindings"):
            evidence.append(f"{overview.get('bindings')} binding(s)")
        if overview.get("window_watchers"):
            evidence.append(f"{overview.get('window_watchers')} window watcher(s)")
        if hotkey_usage:
            evidence.append(f"{len(hotkey_usage)} hotkey-bound step(s)")
        add_component(
            "dispatch-plane",
            "high",
            "Dispatch plane",
            "external/helper",
            "WM/compositor binds, portal shortcuts when available, sxhkd/keyd-class helpers",
            "Always-on activation should stay tiny and restartable. Let fast desktop-native trigger layers wake VHK instead of turning the Python process into the primary global hook.",
            evidence=evidence,
        )

    if "text-expander-integration" in project_tags:
        evidence = []
        if overview.get("hotstrings"):
            evidence.append(f"{overview.get('hotstrings')} hotstring(s)")
        if text_usage:
            evidence.append(f"{len(text_usage)} text step(s)")
        add_component(
            "text-tier",
            "high",
            "Text tier",
            "export + runner",
            "VHK hotstrings, forms, prompt profiles, Espanso-style package export",
            "Fast phrase expansion, structured forms, and app scoping deserve a dedicated surface. VHK should keep the macro runtime for the parts that are truly procedural.",
            evidence=evidence,
        )

    if vision_macros or capture_usage:
        evidence = [str(m.get("macro")) for m in vision_macros[:4]]
        if capture_usage:
            evidence.append(f"{len(capture_usage)} capture-bound step(s)")
        add_component(
            "selector-pack",
            "high",
            "Selector asset pack",
            "vhk-core assets",
            "named regions, needles, OCR boxes, preview + report loops",
            "Visual automation should be treated like a maintained asset pack with bounded search areas, previews, and diagnostics instead of recorder leftovers.",
            evidence=evidence,
        )

    if watcher_macros or "daemon-friendly" in project_tags:
        evidence = []
        if overview.get("bus_watchers"):
            evidence.append(f"{overview.get('bus_watchers')} bus watcher(s)")
        if overview.get("clipboard_watchers"):
            evidence.append(f"{overview.get('clipboard_watchers')} clipboard watcher(s)")
        if overview.get("file_watchers"):
            evidence.append(f"{overview.get('file_watchers')} file watcher(s)")
        if overview.get("window_watchers"):
            evidence.append(f"{overview.get('window_watchers')} window watcher(s)")
        add_component(
            "event-bridge",
            "medium",
            "Event bridge",
            "user service / small emitters",
            "busd, DBus, clipboard, WM, and socket-driven emitters",
            "Event-triggered projects get more reliable when tiny dedicated watchers emit clean events into the runner instead of forcing the runner to poll for everything itself.",
            evidence=evidence,
        )

    if backend == "wayland" and pointer_usage:
        pointer = capability_matrix.get("pointer_injection") if isinstance(capability_matrix, Mapping) else None
        pointer_status = str(pointer.get("status") or "unknown") if isinstance(pointer, Mapping) else "unknown"
        text = capability_matrix.get("text_injection") if isinstance(capability_matrix, Mapping) else None
        text_status = str(text.get("status") or "unknown") if isinstance(text, Mapping) else "unknown"
        add_component(
            "wayland-boundary",
            "high" if pointer_status in {"missing", "limited"} else "medium",
            "Wayland helper boundary",
            "adapter seam",
            "uinput/ydotool/wtype/libei-ready adapters + portal-aware fallbacks",
            "Wayland input support varies by compositor and session permissions. Keep injection behind a swappable adapter boundary so projects can survive backend churn without rewriting macro logic.",
            evidence=[f"pointer_injection={pointer_status}", f"text_injection={text_status}", f"{len(pointer_usage)} pointer step(s)"],
        )

    if overview.get("bindings") or raw_key_events:
        evidence = []
        if overview.get("bindings"):
            evidence.append(f"{overview.get('bindings')} binding(s)")
        if raw_key_events:
            evidence.append(f"{raw_key_events} raw key event(s)")
        add_component(
            "remap-surface",
            "medium",
            "Remap/export surface",
            "external/system",
            "keyd, kanata, kmonad, xremap-class exports",
            "Tap-hold, layer logic, and ultra-low-latency remapping belong close to evdev/compositor layers. VHK should integrate with that tier instead of trying to own it all in-process.",
            evidence=evidence,
        )

    if capability_issues:
        for issue in capability_issues[:4]:
            sev = str(issue.get("severity") or "warning")
            cap = str(issue.get("capability") or "session")
            msg = str(issue.get("message") or "session capability mismatch")
            add_risk(
                f"session-{cap}",
                sev,
                msg,
                evidence=[cap] + [str(x) for x in (issue.get("used_by") or [])[:3]],
            )

    if vision_macros:
        add_risk(
            "vision-brittleness",
            "warning",
            "Vision-heavy flows will stay brittle unless selector assets, named regions, and preview/report loops become part of the normal authoring cycle.",
            evidence=[str(m.get("macro")) for m in vision_macros[:4]],
        )

    if raw_key_events:
        add_risk(
            "raw-key-noise",
            "warning",
            "Recorder-style raw key events are a sign that the project may be mixing macro logic with remapper semantics that belong in a faster external layer.",
            evidence=[f"{raw_key_events} raw key event(s)"],
        )

    return {
        "stance": " + ".join(stance_parts),
        "components": components,
        "risks": risks,
    }


def _deployment_profiles(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    macro_profiles: list[dict[str, Any]],
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
    capability_matrix: Mapping[str, Any] | None = None,
    capability_issues: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    backend = str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "").strip().lower()
    capability_usage = capability_usage or {}
    capability_issues = list(capability_issues or [])
    profiles: list[dict[str, Any]] = []
    root_q = shlex.quote(str(getattr(project, "root_dir", ".") or "."))

    pointer_usage = list(capability_usage.get("pointer_injection") or [])
    text_usage = list(capability_usage.get("text_injection") or [])
    capture_usage = list(capability_usage.get("screen_capture") or [])
    vision_macros = [m for m in macro_profiles if "vision-heavy" in (m.get("tags") or [])]
    text_macros = [m for m in macro_profiles if "text-expander" in (m.get("tags") or [])]
    raw_key_events = sum(int((m.get("smells") or {}).get("raw_key_events") or 0) for m in macro_profiles)

    def fit_for(score: int) -> str:
        if score >= 70:
            return "strong"
        if score >= 40:
            return "conditional"
        return "exploratory"

    def add(
        id: str,
        score: int,
        title: str,
        summary: str,
        *,
        trigger_surface: str,
        execution_surface: str,
        export_surfaces: list[str] | None = None,
        commands: list[str] | None = None,
        blockers: list[str] | None = None,
        evidence: list[str] | None = None,
    ) -> None:
        score = max(0, min(int(score), 100))
        if score <= 0:
            return
        profiles.append({
            "id": id,
            "score": score,
            "fit": fit_for(score),
            "title": title,
            "summary": summary,
            "trigger_surface": trigger_surface,
            "execution_surface": execution_surface,
            "export_surfaces": list(export_surfaces or []),
            "commands": list(commands or []),
            "blocking_capabilities": list(blockers or []),
            "evidence": list(evidence or []),
        })

    text_score = min(100, int(overview.get("hotstrings") or 0) * 35 + len(text_macros) * 25 + (15 if "parameterized" in project_tags else 0) - len(pointer_usage) * 5)
    add(
        "text-first-export",
        text_score,
        "Text-first export profile",
        "Best for projects where snippets, forms, and app-scoped text flows are the visible product surface. Keep those flows fast and exportable while reserving the runner for the procedural edges.",
        trigger_surface="hotstrings + thin dispatch",
        execution_surface="prompt-aware text macros",
        export_surfaces=["espanso-style package export", "app include/exclude filters"],
        commands=[
            f"vhk gen-espanso {root_q} --package-dir ./build/espanso_package",
            f"vhk validate {root_q} --json",
        ],
        evidence=[f"{overview.get('hotstrings') or 0} hotstring(s)", f"{len(text_usage)} text step(s)"],
    )

    selector_score = min(100, len(vision_macros) * 35 + (20 if capture_usage else 0) + (15 if "selector-asset-heavy" in project_tags else 0))
    add(
        "selector-runner",
        selector_score,
        "Selector-driven runner profile",
        "Best for visual workflows that need explicit assets, retries, and diagnostics. The runner stays central, but only after selectors become a maintained subsystem.",
        trigger_surface="one-shot dispatch into the runner",
        execution_surface="selector assets + bounded capture + report loop",
        export_surfaces=["needle preview data", "named regions", "run reports"],
        commands=[
            f"vhk optimize-project {root_q}",
            f"vhk report --project {root_q} --latest --json",
            f"vhk preview-needle path/to/needle.png --project {root_q} --haystack path/to/screenshot.png --json --no-check",
        ],
        blockers=["screen_capture" if not capture_usage else ""],
        evidence=[str(m.get("macro")) for m in vision_macros[:4]],
    )

    daemon_score = min(100, int(overview.get("bus_watchers") or 0) * 30 + int(overview.get("clipboard_watchers") or 0) * 20 + int(overview.get("file_watchers") or 0) * 20 + int(overview.get("window_watchers") or 0) * 25)
    add(
        "watcher-daemon",
        daemon_score,
        "Watcher-daemon profile",
        "Best for automation that should wake up from real desktop events. Package watchers as services and treat them as an event plane, not as side effects hidden inside ad-hoc shell loops.",
        trigger_surface="DBus/window/clipboard/service emitters",
        execution_surface="busd + runner",
        export_surfaces=["systemd user service units", "socket activation"],
        commands=[
            f"vhk gen-vhk-busd-service {root_q} --out-dir ./build/systemd-user",
            f"vhk gen-vhk-busd-socket-units {root_q} --out-dir ./build/systemd-user",
        ],
        evidence=[
            f"{overview.get('bus_watchers') or 0} bus watcher(s)",
            f"{overview.get('clipboard_watchers') or 0} clipboard watcher(s)",
            f"{overview.get('file_watchers') or 0} file watcher(s)",
            f"{overview.get('window_watchers') or 0} window watcher(s)",
        ],
    )

    remap_score = min(100, int(overview.get("bindings") or 0) * 30 + raw_key_events * 15)
    add(
        "remap-integrated",
        remap_score,
        "Remap-integrated profile",
        "Best when the project needs ergonomic layers, tap-hold logic, or fast always-on key dispatch. Use VHK as the macro/orchestration brain and let a dedicated remapper own the interception layer.",
        trigger_surface="remapper/compositor binds",
        execution_surface="short external launch into VHK",
        export_surfaces=["keyd", "kanata", "kmonad", "xremap-class configs"],
        commands=[
            f"vhk gen-keyd-config {root_q} --out ./build/vhk.keyd.conf",
            f"vhk gen-kanata-config {root_q} --out ./build/vhk.kanata.kbd",
            f"vhk gen-kmonad-config {root_q} --out ./build/vhk.kmonad.kbd",
        ],
        evidence=[f"{overview.get('bindings') or 0} binding(s)", f"{raw_key_events} raw key event(s)"],
    )

    if backend == "wayland":
        pointer = capability_matrix.get("pointer_injection") if isinstance(capability_matrix, Mapping) else None
        pointer_status = str(pointer.get("status") or "unknown") if isinstance(pointer, Mapping) else "unknown"
        hotkeys = capability_matrix.get("global_hotkeys") if isinstance(capability_matrix, Mapping) else None
        hotkey_status = str(hotkeys.get("status") or "unknown") if isinstance(hotkeys, Mapping) else "unknown"
        score = min(100, 35 + len(pointer_usage) * 20 + len(capability_issues) * 10 + (15 if hotkey_status in {"missing", "limited"} else 0))
        blockers = []
        if pointer_status in {"missing", "limited"}:
            blockers.append("pointer_injection")
        if hotkey_status in {"missing", "limited"}:
            blockers.append("global_hotkeys")
        add(
            "wayland-helper-boundary",
            score,
            "Wayland helper-boundary profile",
            "Best for Wayland-facing projects that need pointer or global trigger behavior beyond what a single generic backend can guarantee. Treat permissions, helpers, and compositor quirks as first-class deployment inputs.",
            trigger_surface="WM binds or portal shortcuts when truly available",
            execution_surface="VHK runner behind helper/portal/uinput adapters",
            export_surfaces=["desktop profile manifests", "doctor/validate capability reports"],
            commands=[
                "vhk doctor --json",
                f"vhk validate {root_q} --json",
                f"vhk plan-project {root_q} --json",
            ],
            blockers=blockers,
            evidence=[f"pointer_injection={pointer_status}", f"global_hotkeys={hotkey_status}", f"{len(pointer_usage)} pointer step(s)"],
        )

    # Normalize empty blocker strings and sort by score.
    for item in profiles:
        item["blocking_capabilities"] = [str(x) for x in item.get("blocking_capabilities") or [] if str(x)]
    profiles.sort(key=lambda item: (-int(item.get("score") or 0), str(item.get("title") or "")))
    return profiles


def _fit_label(score: int) -> str:
    score = int(score or 0)
    if score >= 75:
        return "strong"
    if score >= 55:
        return "good"
    if score >= 35:
        return "conditional"
    return "weak"


def _desktop_targets(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    macro_profiles: list[dict[str, Any]],
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
    capability_matrix: Mapping[str, Any] | None = None,
    capability_issues: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    backend = str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "").strip().lower()
    capability_usage = capability_usage or {}
    capability_issues = list(capability_issues or [])
    root_dir = getattr(project, "root_dir", None) or "."
    root_q = shlex.quote(str(root_dir))

    pointer_usage = list(capability_usage.get("pointer_injection") or [])
    text_usage = list(capability_usage.get("text_injection") or [])
    capture_usage = list(capability_usage.get("screen_capture") or [])
    hotkey_usage = list(capability_usage.get("global_hotkeys") or [])
    raw_key_events = sum(int((m.get("smells") or {}).get("raw_key_events") or 0) for m in macro_profiles)

    pointer = capability_matrix.get("pointer_injection") if isinstance(capability_matrix, Mapping) else None
    pointer_status = str(pointer.get("status") or "unknown") if isinstance(pointer, Mapping) else "unknown"
    hotkeys = capability_matrix.get("global_hotkeys") if isinstance(capability_matrix, Mapping) else None
    hotkey_status = str(hotkeys.get("status") or "unknown") if isinstance(hotkeys, Mapping) else "unknown"
    screen = capability_matrix.get("screen_capture") if isinstance(capability_matrix, Mapping) else None
    screen_status = str(screen.get("status") or "unknown") if isinstance(screen, Mapping) else "unknown"
    text = capability_matrix.get("text_injection") if isinstance(capability_matrix, Mapping) else None
    text_status = str(text.get("status") or "unknown") if isinstance(text, Mapping) else "unknown"

    targets: list[dict[str, Any]] = []

    def add(
        id: str,
        score: int,
        title: str,
        summary: str,
        *,
        trigger_surface: str,
        input_surface: str,
        packaging: str,
        learn_from: list[str] | None = None,
        blockers: list[str] | None = None,
        commands: list[str] | None = None,
        evidence: list[str] | None = None,
    ) -> None:
        score = max(0, min(int(score), 100))
        targets.append({
            "id": id,
            "score": score,
            "fit": _fit_label(score),
            "title": title,
            "summary": summary,
            "trigger_surface": trigger_surface,
            "input_surface": input_surface,
            "packaging": packaging,
            "learn_from": list(learn_from or []),
            "blocking_capabilities": [str(x) for x in (blockers or []) if str(x)],
            "commands": list(commands or []),
            "evidence": list(evidence or []),
        })

    text_score = min(100, int(overview.get("hotstrings") or 0) * 35 + len(text_usage) * 8 + (18 if not pointer_usage else 0) + (12 if not capture_usage else 0) + (12 if "parameterized" in project_tags else 0))
    add(
        "portable-text-export",
        text_score,
        "Portable text/export target",
        "Best when the project's value is mostly text expansion, forms, or small return-value macros. Keep the runner for structured prompts and exports, but ship the day-to-day trigger path through a dedicated text surface.",
        trigger_surface="hotstrings, palette, and app-scoped text triggers",
        input_surface="direct text output, clipboard, and prompt forms",
        packaging="runner + espanso-style export package",
        learn_from=["Espanso-style app scoping", "forms/snippets split", "include/exclude package layering"],
        commands=[
            f"vhk gen-espanso {root_q} --out-dir ./build/espanso",
            f"vhk plan-project {root_q} --json",
        ],
        evidence=[f"{overview.get('hotstrings') or 0} hotstring(s)", f"{len(text_usage)} text-bound step(s)"],
    )

    x11_score = int(overview.get("bindings") or 0) * 20 + len(pointer_usage) * 8 + len(capture_usage) * 8 + raw_key_events * 6
    if backend == "x11":
        x11_score += 30
    elif backend == "wayland":
        x11_score -= 15
    if overview.get("window_watchers"):
        x11_score += 8
    add(
        "x11-tiling-native",
        x11_score,
        "X11 tiling-native target",
        "Best when you want classic desktop-automation behavior and are willing to target i3/X11 or another X11-first tiling stack explicitly. This is the least contorted route toward broad hotkey, pointer, and screen-driven automation.",
        trigger_surface="WM binds, sxhkd-class dispatch, or direct runner launch",
        input_surface="single-runner X11 playback and screen automation",
        packaging="project-local runner + WM binding export",
        learn_from=["i3/sxhkd-style dispatch", "single-runner desktop automation", "X11-first trigger ownership"],
        commands=[
            f"vhk gen-wm-config {root_q} --wm i3 --out ./build/vhk.i3.conf",
            f"vhk gen-sxhkd-config {root_q} --out ./build/vhk.sxhkdrc",
        ],
        evidence=[f"backend={backend or 'auto'}", f"{overview.get('bindings') or 0} binding(s)", f"{len(pointer_usage)} pointer step(s)"],
    )

    portal_score = 0
    if backend == "wayland":
        portal_score += 28
    if screen_status == "ok":
        portal_score += 18
    elif screen_status == "limited":
        portal_score += 8
    if hotkey_status == "ok":
        portal_score += 16
    elif hotkey_status == "limited":
        portal_score += 8
    if text_status == "ok":
        portal_score += 10
    portal_score += min(20, len(capture_usage) * 6 + int(overview.get("hotstrings") or 0) * 4)
    if pointer_usage and pointer_status in {"missing", "limited"}:
        portal_score -= 14
    add(
        "portal-wayland",
        portal_score,
        "Portal-centric Wayland target",
        "Best when the project can live inside explicit session and permission flows. This target prefers portal-routed capture and shortcuts, then keeps the runner focused on higher-level sequencing instead of pretending Wayland behaves like X11.",
        trigger_surface="portal/global-shortcut style triggers or compositor-native binds",
        input_surface="capture + text-centric flows with explicit consent",
        packaging="desktop profile manifest + doctor/validate loop",
        learn_from=["per-interface portal routing", "explicit request/session lifecycle", "capability matrix instead of one Wayland flag"],
        blockers=["screen_capture" if screen_status == "missing" else "", "global_hotkeys" if hotkey_status == "missing" and (overview.get("bindings") or hotkey_usage) else ""],
        commands=[
            "vhk doctor --json",
            f"vhk validate {root_q} --json",
            f"vhk plan-project {root_q} --json",
        ],
        evidence=[f"screen_capture={screen_status}", f"global_hotkeys={hotkey_status}", f"text_injection={text_status}"],
    )

    helper_score = 0
    if backend == "wayland":
        helper_score += 24
    helper_score += min(28, len(pointer_usage) * 8 + raw_key_events * 6 + int(overview.get("bindings") or 0) * 4)
    if pointer_status in {"missing", "limited"}:
        helper_score += 20
    if hotkey_status in {"missing", "limited"} and (overview.get("bindings") or hotkey_usage):
        helper_score += 10
    if capability_issues:
        helper_score += 10
    add(
        "helper-boundary-wayland",
        helper_score,
        "Helper-boundary Wayland target",
        "Best when the project still needs pointer-heavy or always-on input behavior on Wayland. Keep macro logic in VHK, but isolate injection and interception behind swappable helpers so desktop-specific churn does not leak into every macro.",
        trigger_surface="WM/compositor binds, remapper launches, or tiny emitters",
        input_surface="adapter seam for uinput/ydotool/wtype/libei-ready backends",
        packaging="runner core + helper boundary + capability audit",
        learn_from=["libei/EIS-ready adapter seam", "helper-specific injection backends", "small trigger layer outside the runner"],
        blockers=["pointer_injection" if pointer_status in {"missing", "limited"} and pointer_usage else "", "global_hotkeys" if hotkey_status == "missing" and (overview.get("bindings") or hotkey_usage) else ""],
        commands=[
            "vhk doctor --json",
            f"vhk gen-keyd-config {root_q} --out ./build/vhk.keyd.conf",
            f"vhk gen-wm-config {root_q} --wm hyprland --out ./build/vhk.hypr.conf",
        ],
        evidence=[f"pointer_injection={pointer_status}", f"{len(pointer_usage)} pointer step(s)", f"{raw_key_events} raw key event(s)"],
    )

    conservative_score = 0
    if backend == "wayland":
        conservative_score += 22
    conservative_score += min(20, int(overview.get("window_watchers") or 0) * 10 + int(overview.get("bus_watchers") or 0) * 10 + int(overview.get("clipboard_watchers") or 0) * 8 + int(overview.get("file_watchers") or 0) * 8)
    if overview.get("bindings"):
        conservative_score += 8
    if overview.get("hotstrings"):
        conservative_score += 8
    if pointer_status in {"missing", "limited"}:
        conservative_score += 14
    if hotkey_status in {"missing", "limited"} and (overview.get("bindings") or hotkey_usage):
        conservative_score += 8
    if capture_usage:
        conservative_score += 6
    add(
        "wlroots-hyprland-conservative",
        conservative_score,
        "wlroots/Hyprland conservative target",
        "Best when you want to support fast-moving compositor stacks without overpromising generic portal parity. Bias toward WM binds, event bridges, text surfaces, and explicit capability checks before declaring pointer/global-trigger support done.",
        trigger_surface="compositor binds, bus/window watchers, and launcher surfaces",
        input_surface="text/watcher-first with helper-gated pointer automation",
        packaging="desktop-specific playbooks and conservative capability promises",
        learn_from=["compositor-bound integration", "service + WM bind split", "conservative RemoteDesktop/InputCapture assumptions"],
        blockers=["pointer_injection" if pointer_status == "missing" and pointer_usage else "", "global_hotkeys" if hotkey_status == "missing" and (overview.get("bindings") or hotkey_usage) else ""],
        commands=[
            f"vhk gen-wm-config {root_q} --wm sway --out ./build/vhk.sway.conf",
            f"vhk gen-wm-config {root_q} --wm hyprland --out ./build/vhk.hypr.conf",
            f"vhk gen-vhk-busd-service {root_q} --out-dir ./build/systemd-user",
        ],
        evidence=[f"pointer_injection={pointer_status}", f"global_hotkeys={hotkey_status}", f"{overview.get('bus_watchers') or 0} bus watcher(s)"],
    )

    targets.sort(key=lambda item: (-int(item.get("score") or 0), str(item.get("title") or "")))
    return targets


def _portal_shortcut_catalog_analysis(
    *,
    project,
    macro_profiles: list[dict[str, Any]],
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
) -> dict[str, Any]:
    """Classify hotkey bindings into stable portal-catalog vs dynamic lanes.

    Portal shortcuts are strongest when they wake a reviewed, predeclared action
    catalog. This helper keeps that distinction explicit so the planner can
    separate stable session-owned shortcut ids from hotter or helper-sensitive
    trigger flows.
    """

    capability_usage = capability_usage or {}
    usage_by_macro: dict[str, set[str]] = defaultdict(set)
    for capability_name, refs in capability_usage.items():
        for ref in refs or []:
            if not isinstance(ref, Mapping):
                continue
            macro_name = str(ref.get('macro') or '').strip()
            if macro_name:
                usage_by_macro[macro_name].add(str(capability_name))

    profile_by_macro = {
        str(item.get('macro') or '').strip(): dict(item)
        for item in macro_profiles
        if isinstance(item, Mapping) and str(item.get('macro') or '').strip()
    }

    stable_bindings: list[dict[str, Any]] = []
    dynamic_bindings: list[dict[str, Any]] = []

    for binding in getattr(project, 'bindings', []) or []:
        macro_name = str(getattr(binding, 'macro', None) or '').strip()
        if not macro_name:
            continue
        profile = dict(profile_by_macro.get(macro_name) or {})
        triggers = {str(x or '').strip() for x in (profile.get('triggers') or []) if str(x or '').strip()}
        capabilities = {str(x or '').strip() for x in (usage_by_macro.get(macro_name) or set()) if str(x or '').strip()}
        reasons: list[str] = []
        if not profile:
            reasons.append('macro profile unavailable')
        if any(trigger.endswith('watcher') for trigger in triggers):
            reasons.append('watcher-driven macro')
        if capabilities.intersection({'pointer_injection', 'screen_capture', 'input_capture'}):
            reasons.append('helper-sensitive capability use')
        if profile and _is_remap_like_macro_profile(profile):
            reasons.append('remapper-tier fit')

        row = {
            'macro': macro_name,
            'keys': str(getattr(binding, 'keys', None) or '').strip() or None,
            'stable_catalog_fit': not reasons,
            'reasons': list(dict.fromkeys(str(x) for x in reasons if str(x))),
            'capabilities': sorted(capabilities),
        }
        if row['stable_catalog_fit']:
            stable_bindings.append(row)
        else:
            dynamic_bindings.append(row)

    return {
        'binding_count': len(stable_bindings) + len(dynamic_bindings),
        'stable_binding_count': len(stable_bindings),
        'dynamic_binding_count': len(dynamic_bindings),
        'stable_binding_macros': [str(item.get('macro') or '') for item in stable_bindings if str(item.get('macro') or '')],
        'dynamic_binding_macros': [str(item.get('macro') or '') for item in dynamic_bindings if str(item.get('macro') or '')],
        'stable_bindings': stable_bindings,
        'dynamic_bindings': dynamic_bindings,
    }


def _is_portal_catalog_macro(
    macro_name: str,
    *,
    portal_catalog: Mapping[str, Any] | None,
) -> bool:
    portal_catalog = portal_catalog or {}
    stable_names = {str(x or '').strip() for x in (portal_catalog.get('stable_binding_macros') or []) if str(x or '').strip()}
    return str(macro_name or '').strip() in stable_names


_APP_PROTOCOL_TARGETS: dict[str, dict[str, Any]] = {
    'kitty': {
        'aliases': {'kitty'},
        'learn_from': 'kitty remote control',
        'kind': 'terminal',
    },
    'wezterm': {
        'aliases': {'wezterm', 'org.wezfurlong.wezterm'},
        'learn_from': 'WezTerm CLI',
        'kind': 'terminal',
    },
    'mpv': {
        'aliases': {'mpv'},
        'learn_from': 'mpv JSON IPC',
        'kind': 'media',
    },
    'qutebrowser': {
        'aliases': {'qutebrowser'},
        'learn_from': 'qutebrowser userscripts',
        'kind': 'browser',
    },
}


def _app_protocol_pack_commands(root_q: str, target_ids: list[str]) -> list[str]:
    commands: list[str] = []
    if 'kitty' in target_ids:
        commands.append(f'vhk gen-kitty-pack {root_q} --out-dir ./build/kitty_pack')
    if 'wezterm' in target_ids:
        commands.append(f'vhk gen-wezterm-pack {root_q} --out-dir ./build/wezterm_pack')
    if 'mpv' in target_ids:
        commands.append(f'vhk gen-mpv-pack {root_q} --out-dir ./build/mpv_pack')
    if 'qutebrowser' in target_ids:
        commands.append(f'vhk gen-qutebrowser-pack {root_q} --out-dir ./build/qutebrowser_pack')
    commands.extend([
        f'vhk gen-design-pack {root_q} --quiet',
        f'vhk gen-target-route-pack {root_q} --quiet',
        f'vhk lint-project {root_q}',
        f'vhk window-spy --project {root_q} --json --no-check',
    ])
    return commands


def _selector_texts(selector: Any) -> list[str]:
    if selector is None:
        return []
    values = [
        getattr(selector, 'app_id', None),
        getattr(selector, 'wm_class', None),
        getattr(selector, 'instance', None),
        getattr(selector, 'title', None),
        getattr(selector, 'window_role', None),
    ]
    return [str(value).strip() for value in values if str(value or '').strip()]



def _app_protocol_target_analysis(*, project) -> dict[str, Any]:
    targets: dict[str, dict[str, Any]] = {}

    def record(value: str, source: str) -> None:
        normalized = str(value or '').strip().lower()
        if not normalized:
            return
        for target_id, meta in _APP_PROTOCOL_TARGETS.items():
            aliases = {str(x).strip().lower() for x in (meta.get('aliases') or set()) if str(x).strip()}
            if any(alias in normalized for alias in aliases):
                row = targets.setdefault(
                    target_id,
                    {
                        'id': target_id,
                        'kind': str(meta.get('kind') or ''),
                        'learn_from': str(meta.get('learn_from') or target_id),
                        'matched_values': [],
                        'sources': [],
                    },
                )
                if value not in row['matched_values']:
                    row['matched_values'].append(value)
                if source not in row['sources']:
                    row['sources'].append(source)
                break

    def record_selector(selector: Any, source: str) -> None:
        for text_value in _selector_texts(selector):
            record(text_value, source)

    for macro_name, macro in getattr(project, 'macros', {}).items():
        record_selector(getattr(macro, 'voice_when', None), f'macro:{macro_name}.voice_when')
        for preset in getattr(macro, 'presets', []) or []:
            record_selector(getattr(preset, 'voice_when', None), f'macro:{macro_name}.preset:{getattr(preset, "name", "")}.voice_when')
        for step, step_path in _iter_steps(getattr(macro, 'steps', []) or []):
            record_selector(getattr(step, 'selector', None), f'macro:{macro_name}.{step_path}.selector')
    for idx, binding in enumerate(getattr(project, 'bindings', []) or []):
        record_selector(getattr(binding, 'when', None), f'binding[{idx}].when')
    for idx, hotstring in enumerate(getattr(project, 'hotstrings', []) or []):
        record_selector(getattr(hotstring, 'when', None), f'hotstring[{idx}].when')
    for idx, watcher in enumerate(getattr(project, 'window_watchers', []) or []):
        record_selector(getattr(watcher, 'when', None), f'window_watcher[{idx}].when')
    for idx, watcher in enumerate(getattr(project, 'bus_watchers', []) or []):
        record_selector(getattr(watcher, 'when', None), f'bus_watcher[{idx}].when')

    rows = sorted(targets.values(), key=lambda item: str(item.get('id') or ''))
    return {
        'target_count': len(rows),
        'target_ids': [str(item.get('id') or '') for item in rows if str(item.get('id') or '')],
        'learn_from': [str(item.get('learn_from') or '') for item in rows if str(item.get('learn_from') or '')],
        'targets': rows,
    }



def _normalize_voice_phrase(value: str) -> str:
    phrase = str(value or '').strip().lower()
    if not phrase:
        return ''
    phrase = re.sub(r'[_-]+', ' ', phrase)
    phrase = re.sub(r'\s+', ' ', phrase)
    return phrase.strip()



def _voice_adapter_analysis(*, project) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    explicit_phrases: list[str] = []
    scoped_rows = 0

    def add_row(*, command_id: str, source: str, phrases: list[str], voice_context: Any) -> None:
        nonlocal scoped_rows
        normalized = [_normalize_voice_phrase(item) for item in phrases]
        normalized = [item for item in normalized if item]
        if voice_context is not None:
            scoped_rows += 1
        if not normalized and voice_context is None:
            return
        explicit_phrases.extend(normalized)
        rows.append({
            'command_id': command_id,
            'source': source,
            'phrases': normalized,
            'scoped': voice_context is not None,
        })

    for macro_name, macro in getattr(project, 'macros', {}).items():
        macro_phrases = [str(item) for item in (getattr(macro, 'voice_phrases', []) or []) if str(item or '').strip()]
        add_row(
            command_id=str(macro_name),
            source=f'macro:{macro_name}',
            phrases=macro_phrases,
            voice_context=getattr(macro, 'voice_when', None),
        )
        for preset in getattr(macro, 'presets', []) or []:
            preset_name = str(getattr(preset, 'name', '') or '').strip()
            preset_phrases = [str(item) for item in (getattr(preset, 'voice_phrases', []) or []) if str(item or '').strip()]
            add_row(
                command_id=f'{macro_name}@{preset_name}' if preset_name else str(macro_name),
                source=f'macro:{macro_name}.preset:{preset_name}',
                phrases=preset_phrases,
                voice_context=getattr(preset, 'voice_when', None) if getattr(preset, 'voice_when', None) is not None else getattr(macro, 'voice_when', None),
            )

    unique_phrases = list(dict.fromkeys(explicit_phrases))
    return {
        'entry_count': len(rows),
        'explicit_phrase_count': len(explicit_phrases),
        'unique_phrase_count': len(unique_phrases),
        'scoped_entry_count': scoped_rows,
        'command_ids': [str(item.get('command_id') or '') for item in rows if str(item.get('command_id') or '')],
        'rows': rows,
    }





def _mpris_service_analysis(*, project) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    players: list[str] = []
    buses: list[str] = []
    members: list[str] = []
    interfaces: list[str] = []

    def _extract_player_name(sender: str) -> str:
        normalized = str(sender or '').strip()
        prefix = 'org.mpris.MediaPlayer2.'
        if not normalized.startswith(prefix):
            return ''
        return normalized[len(prefix):].strip()

    for macro_name, macro in getattr(project, 'macros', {}).items():
        for step, step_path in _iter_steps(getattr(macro, 'steps', []) or []):
            if str(getattr(step, 'type', None) or '').strip() != 'WaitForDbusSignal':
                continue
            sender = str(getattr(step, 'sender', None) or '').strip()
            path = str(getattr(step, 'path', None) or '').strip()
            interface = str(getattr(step, 'interface', None) or '').strip()
            member = str(getattr(step, 'member', None) or '').strip()
            match = str(getattr(step, 'match', None) or '').strip()
            bus = str(getattr(step, 'bus', None) or 'session').strip()
            haystack = ' '.join(part for part in [sender, path, interface, member, match] if part).lower()
            if 'org.mpris.mediaplayer2' not in haystack and '/org/mpris/mediaplayer2' not in haystack:
                continue
            player_name = _extract_player_name(sender)
            rows.append({
                'macro': str(macro_name),
                'path': step_path,
                'bus': bus,
                'sender': sender or None,
                'path_name': path or None,
                'interface': interface or None,
                'member': member or None,
                'player': player_name or None,
            })
            if player_name and player_name not in players:
                players.append(player_name)
            if bus and bus not in buses:
                buses.append(bus)
            if member and member not in members:
                members.append(member)
            if interface and interface not in interfaces:
                interfaces.append(interface)

    return {
        'signal_count': len(rows),
        'player_count': len(players),
        'players': players,
        'buses': buses,
        'members': members,
        'interfaces': interfaces,
        'rows': rows,
    }



def _notification_feedback_analysis(*, project) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    notification_macros: list[str] = []
    buses: list[str] = []
    members: list[str] = []
    interfaces: list[str] = []
    urgencies: list[str] = []
    notify_count = 0
    show_message_count = 0
    signal_count = 0
    replaceable_count = 0
    timed_count = 0
    transient_count = 0
    actionable_count = 0
    progress_count = 0

    for macro_name, macro in getattr(project, 'macros', {}).items():
        macro_has_feedback = False
        for step, step_path in _iter_steps(getattr(macro, 'steps', []) or []):
            step_type = str(getattr(step, 'type', None) or '').strip()
            if step_type == 'Notify':
                notify_count += 1
                macro_has_feedback = True
                urgency = str(getattr(step, 'urgency', None) or 'normal').strip().lower()
                replace_id = getattr(step, 'replace_id', None)
                out_id = getattr(step, 'out_id', None)
                timeout_ms = getattr(step, 'timeout_ms', None)
                transient = bool(getattr(step, 'transient', False))
                actions = list(getattr(step, 'actions', []) or [])
                out_action = getattr(step, 'out_action', None)
                progress = getattr(step, 'progress', None)
                actionable = bool(actions or out_action)
                progress_enabled = progress is not None
                if replace_id is not None or out_id is not None:
                    replaceable_count += 1
                if timeout_ms is not None:
                    timed_count += 1
                if transient:
                    transient_count += 1
                if actionable:
                    actionable_count += 1
                if progress_enabled:
                    progress_count += 1
                rows.append({
                    'macro': str(macro_name),
                    'path': step_path,
                    'kind': 'notify',
                    'urgency': urgency or None,
                    'replaceable': replace_id is not None or out_id is not None,
                    'timed': timeout_ms is not None,
                    'transient': transient,
                    'actionable': actionable,
                    'progress': progress_enabled,
                })
                if urgency and urgency not in urgencies:
                    urgencies.append(urgency)
                continue
            if step_type == 'ShowMessage':
                show_message_count += 1
                macro_has_feedback = True
                level = str(getattr(step, 'level', None) or 'info').strip().lower()
                rows.append({
                    'macro': str(macro_name),
                    'path': step_path,
                    'kind': 'show-message',
                    'level': level or None,
                })
                continue
            if step_type != 'WaitForDbusSignal':
                continue
            sender = str(getattr(step, 'sender', None) or '').strip()
            path = str(getattr(step, 'path', None) or '').strip()
            interface = str(getattr(step, 'interface', None) or '').strip()
            member = str(getattr(step, 'member', None) or '').strip()
            match = str(getattr(step, 'match', None) or '').strip()
            bus = str(getattr(step, 'bus', None) or 'session').strip()
            haystack = ' '.join(part for part in [sender, path, interface, member, match] if part).lower()
            if 'org.freedesktop.notifications' not in haystack and '/org/freedesktop/notifications' not in haystack:
                continue
            signal_count += 1
            macro_has_feedback = True
            rows.append({
                'macro': str(macro_name),
                'path': step_path,
                'kind': 'notification-signal',
                'bus': bus,
                'sender': sender or None,
                'path_name': path or None,
                'interface': interface or None,
                'member': member or None,
            })
            if bus and bus not in buses:
                buses.append(bus)
            if member and member not in members:
                members.append(member)
            if interface and interface not in interfaces:
                interfaces.append(interface)
        if macro_has_feedback and str(macro_name) not in notification_macros:
            notification_macros.append(str(macro_name))

    return {
        'entry_count': notify_count + show_message_count,
        'notify_count': notify_count,
        'show_message_count': show_message_count,
        'signal_count': signal_count,
        'replaceable_count': replaceable_count,
        'timed_count': timed_count,
        'transient_count': transient_count,
        'actionable_count': actionable_count,
        'progress_count': progress_count,
        'macro_count': len(notification_macros),
        'macros': notification_macros,
        'buses': buses,
        'members': members,
        'interfaces': interfaces,
        'urgencies': urgencies,
        'rows': rows,
    }

def _surface_choices(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    macro_profiles: list[dict[str, Any]],
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
    capability_matrix: Mapping[str, Any] | None = None,
    capability_issues: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Score concrete Linux integration surfaces against the current project.

    This extends plan-project beyond high-level targets. Instead of only saying
    "use a text tier" or "keep a trigger plane", it compares the candidate
    surfaces teams actually have to choose among on Linux.
    """

    backend = str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "").strip().lower()
    capability_usage = capability_usage or {}
    capability_issues = list(capability_issues or [])
    root_dir = getattr(project, "root_dir", None) or "."
    root_q = shlex.quote(str(root_dir))

    pointer_usage = list(capability_usage.get("pointer_injection") or [])
    text_usage = list(capability_usage.get("text_injection") or [])
    hotkey_usage = list(capability_usage.get("global_hotkeys") or [])
    window_usage = list(capability_usage.get("window_introspection") or [])
    flow_macros = [m for m in macro_profiles if "flow-heavy" in (m.get("tags") or [])]
    prompt_macros = [
        m
        for m in macro_profiles
        if int(((m.get("feature_counts") or {}).get("prompt") or 0)) > 0 or int(m.get("preset_count") or 0) > 0
    ]
    raw_key_events = sum(int((m.get("smells") or {}).get("raw_key_events") or 0) for m in macro_profiles)
    watcher_count = int(overview.get("bus_watchers") or 0) + int(overview.get("clipboard_watchers") or 0) + int(overview.get("file_watchers") or 0) + int(overview.get("window_watchers") or 0)

    hotkeys = capability_matrix.get("global_hotkeys") if isinstance(capability_matrix, Mapping) else None
    hotkey_status = str(hotkeys.get("status") or "unknown") if isinstance(hotkeys, Mapping) else "unknown"
    pointer = capability_matrix.get("pointer_injection") if isinstance(capability_matrix, Mapping) else None
    pointer_status = str(pointer.get("status") or "unknown") if isinstance(pointer, Mapping) else "unknown"
    text = capability_matrix.get("text_injection") if isinstance(capability_matrix, Mapping) else None
    text_status = str(text.get("status") or "unknown") if isinstance(text, Mapping) else "unknown"

    portal_catalog = _portal_shortcut_catalog_analysis(
        project=project,
        macro_profiles=macro_profiles,
        capability_usage=capability_usage,
    )
    stable_portal_bindings = int(portal_catalog.get("stable_binding_count") or 0)
    dynamic_portal_bindings = int(portal_catalog.get("dynamic_binding_count") or 0)
    app_protocols = _app_protocol_target_analysis(project=project)
    app_protocol_target_count = int(app_protocols.get("target_count") or 0)
    app_protocol_learn_from = [str(x) for x in (app_protocols.get("learn_from") or []) if str(x)]
    app_protocol_target_ids = [str(x) for x in (app_protocols.get("target_ids") or []) if str(x)]
    app_protocol_commands = _app_protocol_pack_commands(root_q, app_protocol_target_ids)
    voice_adapters = _voice_adapter_analysis(project=project)
    voice_entry_count = int(voice_adapters.get("entry_count") or 0)
    voice_phrase_count = int(voice_adapters.get("explicit_phrase_count") or 0)
    voice_unique_phrase_count = int(voice_adapters.get("unique_phrase_count") or 0)
    voice_scoped_entry_count = int(voice_adapters.get("scoped_entry_count") or 0)
    mpris_services = _mpris_service_analysis(project=project)
    mpris_signal_count = int(mpris_services.get("signal_count") or 0)
    mpris_player_count = int(mpris_services.get("player_count") or 0)
    mpris_players = [str(x) for x in (mpris_services.get("players") or []) if str(x)]
    mpris_members = [str(x) for x in (mpris_services.get("members") or []) if str(x)]
    mpris_buses = [str(x) for x in (mpris_services.get("buses") or []) if str(x)]
    notification_feedback = _notification_feedback_analysis(project=project)
    notification_entry_count = int(notification_feedback.get("entry_count") or 0)
    notification_signal_count = int(notification_feedback.get("signal_count") or 0)
    notification_macro_count = int(notification_feedback.get("macro_count") or 0)
    notification_notify_count = int(notification_feedback.get("notify_count") or 0)
    notification_show_message_count = int(notification_feedback.get("show_message_count") or 0)
    notification_replaceable_count = int(notification_feedback.get("replaceable_count") or 0)
    notification_timed_count = int(notification_feedback.get("timed_count") or 0)
    notification_transient_count = int(notification_feedback.get("transient_count") or 0)
    notification_actionable_count = int(notification_feedback.get("actionable_count") or 0)
    notification_progress_count = int(notification_feedback.get("progress_count") or 0)
    notification_members = [str(x) for x in (notification_feedback.get("members") or []) if str(x)]
    notification_buses = [str(x) for x in (notification_feedback.get("buses") or []) if str(x)]
    notification_urgencies = [str(x) for x in (notification_feedback.get("urgencies") or []) if str(x)]
    text_mechanisms: list[str] = []
    text_recommended = ""

    candidates: list[dict[str, Any]] = []

    def add(
        id: str,
        category: str,
        score: int,
        title: str,
        summary: str,
        *,
        strengths: str,
        tradeoffs: str,
        commands: list[str] | None = None,
        learn_from: list[str] | None = None,
        evidence: list[str] | None = None,
    ) -> None:
        score = max(0, min(int(score), 100))
        candidates.append({
            "id": id,
            "category": category,
            "score": score,
            "fit": _fit_label(score),
            "title": title,
            "summary": summary,
            "strengths": strengths,
            "tradeoffs": tradeoffs,
            "commands": list(commands or []),
            "learn_from": list(learn_from or []),
            "evidence": list(evidence or []),
        })

    # Text surfaces
    espanso_score = int(overview.get("hotstrings") or 0) * 32 + len(text_usage) * 8 + (14 if "parameterized" in project_tags else 0) + (10 if backend == "wayland" else 0)
    if overview.get("hotstrings") or any("text-expander" in (m.get("tags") or []) for m in macro_profiles):
        add(
            "espanso-text-package",
            "text",
            espanso_score,
            "Espanso-style text package",
            "Use this when snippets, forms, and app-scoped text workflows are a major product lane. Exporting the text tier keeps fast expansions out of the heavier macro runner while preserving structured prompts and package boundaries.",
            strengths="Excellent fit for snippets, forms, and include/exclude app scoping.",
            tradeoffs="This is not a substitute for pointer-heavy desktop automation or long control-flow graphs.",
            commands=[
                f"vhk gen-espanso {root_q} --package-dir ./build/espanso_package",
                f"vhk validate {root_q} --json",
            ],
            learn_from=["Espanso forms", "app-specific configs", "include/exclude package layering"],
            evidence=[f"{overview.get('hotstrings') or 0} hotstring(s)", f"text_injection={text_status}", f"{overview.get('presets') or 0} preset(s)"],
        )

    if backend == "wayland" and (overview.get("hotstrings") or text_usage):
        text_mechanisms = [str(x).strip().lower() for x in (text.get("mechanisms") or []) if str(x).strip()] if isinstance(text, Mapping) else []
        text_recommended = str(text.get("recommended") or "").strip().lower() if isinstance(text, Mapping) else ""
        wtype_score = int(overview.get("hotstrings") or 0) * 18 + len(text_usage) * 9 + (10 if "parameterized" in project_tags else 0)
        if text_recommended == "wtype":
            wtype_score += 24
        elif "wtype" in text_mechanisms:
            wtype_score += 14
        elif text_status in {"ok", "limited"}:
            wtype_score += 6
        else:
            wtype_score -= 8
        add(
            "wtype-wayland-text",
            "text",
            wtype_score,
            "wtype-style Wayland text fast path",
            "Use this when a Wayland project has a narrow, reviewable typed-text lane and the target compositor actually exposes the virtual-keyboard path. This keeps fast literal typing explicit instead of pretending every Wayland session supports one generic injection backend.",
            strengths="Strong for fast typed-text paths when the target session already proves virtual-keyboard support.",
            tradeoffs="This is not a generic Wayland guarantee: virtual-keyboard support is compositor/protocol-shaped, so clipboard or helper-backed fallbacks still need to stay available.",
            commands=[
                f"vhk validate {root_q} --json",
                f"vhk gen-espanso {root_q} --package-dir ./build/espanso_package",
            ],
            learn_from=["wtype virtual keyboard", "narrow compositor protocol lane", "text fast path with explicit fallbacks"],
            evidence=[f"desktop_backend={backend}", f"text_injection={text_status}", f"{overview.get('hotstrings') or 0} hotstring(s)"],
        )

    if backend == "wayland" and (pointer_usage or text_usage):
        pointer_mechanisms = [str(x).strip().lower() for x in (pointer.get("mechanisms") or []) if str(x).strip()] if isinstance(pointer, Mapping) else []
        pointer_recommended = str(pointer.get("recommended") or "").strip().lower() if isinstance(pointer, Mapping) else ""
        daemon_score = len(pointer_usage) * 20 + len(text_usage) * 9 + (16 if backend == "wayland" else 0)
        daemon_signals = {pointer_recommended, text_recommended, *pointer_mechanisms, *text_mechanisms}
        if {"dotoolc", "dotool", "ydotool", "helper", "portal/helper"}.intersection(daemon_signals):
            daemon_score += 18
        if pointer_status in {"missing", "limited"}:
            daemon_score += 12
        if text_status in {"missing", "limited"}:
            daemon_score += 8
        add(
            "uinput-helper-daemon",
            "adapter",
            daemon_score,
            "Persistent uinput helper-daemon lane",
            "Use this when a Wayland project needs repeated typed-text or pointer playback and the honest route is a reviewed daemon/socket lane instead of pretending one-shot helpers are invisible implementation details. This keeps helper lifecycle, socket ownership, and uinput policy in the plan before deployment starts.",
            strengths="Strong for repeated helper-backed playback because daemonized virtual devices reduce setup latency and make the host contract reviewable.",
            tradeoffs="Still depends on `/dev/uinput`, service wiring, and helper choice (`dotoold`/`ydotoold`), so it should stay an explicit deployment lane rather than a generic Linux default.",
            commands=[
                "vhk doctor --json",
                "vhk gen-dotoold-service --out-dir ./build/systemd-user",
                "vhk gen-ydotoold-service --out-dir ./build/systemd-user",
                "vhk gen-udev-uinput --out-dir ./build/udev",
            ],
            learn_from=["dotoold/dotoolc", "ydotoold persistent device", "uinput helper service boundary"],
            evidence=[f"desktop_backend={backend}", f"pointer_injection={pointer_status}", f"text_injection={text_status}", f"pointer_usage={len(pointer_usage)}", f"text_usage={len(text_usage)}"],
        )

    if backend in {"x11", "i3"} and (overview.get("hotstrings") or overview.get("bindings") or text_usage):
        autokey_score = int(overview.get("hotstrings") or 0) * 26 + int(overview.get("bindings") or 0) * 14 + len(text_usage) * 10
        if backend == "x11":
            autokey_score += 18
        if int(overview.get("hotstrings") or 0) and int(overview.get("bindings") or 0):
            autokey_score += 10
        add(
            "autokey-x11-adapter",
            "adapter",
            autokey_score,
            "AutoKey-style X11 adapter pack",
            "Use this when an X11-first project wants reviewable text and hotkey handoff into a familiar Linux automation shell instead of treating VHK as the only resident trigger process. The adapter pack keeps VHK as the execution engine while exporting a diffable AutoKey folder tree.",
            strengths="Strong for X11-oriented phrase/hotkey workflows that benefit from a reviewable adapter handoff.",
            tradeoffs="AutoKey remains an X11 lane with a coarser title-or-class window filter than VHK selectors, so scoped exports must stay conservative.",
            commands=[
                f"vhk gen-autokey-pack {root_q} --out-dir ./build/autokey_pack",
                f"vhk lint-project {root_q}",
            ],
            learn_from=["AutoKey trigger shell", "reviewable script + metadata export", "X11-first adapter honesty"],
            evidence=[f"desktop_backend={backend}", f"{overview.get('hotstrings') or 0} hotstring(s)", f"{overview.get('bindings') or 0} binding(s)"],
        )

    palette_score = len(text_usage) * 6 + int(overview.get("presets") or 0) * 10 + (16 if "parameterized" in project_tags else 0) + watcher_count * 4 + (8 if int(overview.get("hotstrings") or 0) == 0 else 0)
    if int(overview.get("presets") or 0) or "parameterized" in project_tags or watcher_count:
        add(
            "vhk-palette-launcher",
            "launcher",
            palette_score,
            "VHK palette / prompt-profile launcher",
            "Use this when the project has reusable parameter sets, prompt overlays, or service-triggered entry points. The palette becomes a Linux-native control surface for prompted workflows that do not map cleanly to raw hotkeys.",
            strengths="Strong for preset-rich workflows, saved prompt profiles, and launcher entry points.",
            tradeoffs="Direct palette launches are not the lowest-latency answer for high-frequency remaps or pure text expansion.",
            commands=[
                f"vhk palette {root_q} --json",
                f"vhk list-prompt-profiles {root_q}",
            ],
            learn_from=["launcher-driven automation", "forms before playback", "saved variants instead of duplicated macros"],
            evidence=[f"{overview.get('presets') or 0} preset(s)", f"{watcher_count} watcher(s)", f"text_injection={text_status}"],
        )

    launcher_hub_score = int(overview.get("macros") or 0) * 10 + int(overview.get("presets") or 0) * 9 + watcher_count * 4 + (10 if "parameterized" in project_tags else 0)
    if int(overview.get("macros") or 0) >= 4 or int(overview.get("presets") or 0) >= 2 or ("parameterized" in project_tags and int(overview.get("macros") or 0) >= 2):
        add(
            "launcher-hub-surface",
            "launcher",
            launcher_hub_score,
            "Launcher / menu hub surface",
            "Use this when the project is growing into a small action catalog. Exporting discoverable launcher rows and WM launcher modes keeps dozens of macros/presets usable without turning the global keyspace into a maze.",
            strengths="Strong for discoverability, one-handed launch flows, and growing prompt/preset catalogs.",
            tradeoffs="This is a control-surface layer, not a substitute for low-latency remappers or a real pointer-injection backend.",
            commands=[
                f"vhk export-rofi-mode {root_q} ./build/vhk.rofi.sh",
                f"vhk export-wm-launcher-mode {root_q} ./build/vhk.launcher --wm sway",
                f"vhk export-wm-bundle {root_q} ./build/wm_bundle --wm i3 --kind launcher-mode --key Mod4+semicolon",
            ],
            learn_from=["Kando menu triggers", "Fly-Pie marking menus", "discoverable launcher hubs"],
            evidence=[f"{overview.get('macros') or 0} macro(s)", f"{overview.get('presets') or 0} preset(s)", f"{watcher_count} watcher(s)"],
        )
    if int(overview.get("presets") or 0) or prompt_macros:
        chooser_score = len(prompt_macros) * 18 + int(overview.get("presets") or 0) * 12 + (14 if "parameterized" in project_tags else 0) + (8 if backend == "wayland" else 4)
        add(
            "picker-native-chooser",
            "launcher",
            chooser_score,
            "Picker-native chooser lane",
            "Use this when prompted or chooser-heavy workflows want a native Linux picker surface instead of a bespoke always-on GUI. Exporting one reviewable launcher script keeps rofi/fuzzel/wofi-class pickers aligned with the same palette entry ids and prompt-profile actions.",
            strengths="Strong for parameterized, chooser-style, and preset-driven flows that benefit from searchable launcher UIs.",
            tradeoffs="Picker-native choosers are an entry surface, not the macro runtime itself, and available picker protocols still differ across X11 and Wayland desktops.",
            commands=[
                f"vhk export-launcher-script {root_q}",
                f"vhk export-rofi-mode {root_q} ./build/vhk.rofi.sh",
                f"vhk palette {root_q} --json",
            ],
            learn_from=["rofi script mode", "fuzzel dmenu", "wofi dmenu"],
            evidence=[
                f"prompt_macros={len(prompt_macros)}",
                f"{overview.get('presets') or 0} preset(s)",
                f"desktop_backend={backend or 'auto'}",
            ],
        )

    accessibility_surface_score = len(window_usage) * 18 + len(flow_macros) * 10 + watcher_count * 4 + (10 if backend == "wayland" else 6)
    if window_usage or flow_macros:
        add(
            "atspi-structured-ui",
            "context",
            accessibility_surface_score,
            "AT-SPI structured UI lane",
            "Use this when a project benefits from widget-aware lookup and action paths instead of relying only on desktop metadata or pixel coordinates. Treat accessibility as a separate Linux contract with its own bus, host checks, and per-app coverage rather than a generic always-on primitive.",
            strengths="Strong for structured application targeting when toolkits expose roles, text, actions, and component bounds through AT-SPI.",
            tradeoffs="Coverage varies by toolkit/app and the accessibility bus can be disabled or incomplete, so vision and desktop-metadata fallbacks still need to stay in the design.",
            commands=[
                "vhk doctor --json",
                f"vhk window-spy --project {root_q} --json --no-check",
                f"vhk gen-session-fit-pack {root_q} --quiet",
            ],
            learn_from=["AT-SPI separate bus", "Accerciser inspector", "dogtail structured UI automation"],
            evidence=[
                f"desktop_backend={backend or 'unknown'}",
                f"window_usage={len(window_usage)}",
                f"flow_macros={len(flow_macros)}",
                f"window_watchers={int(overview.get('window_watchers') or 0)}",
            ],
        )

    app_protocol_score = app_protocol_target_count * 24 + len(window_usage) * 10 + len(text_usage) * 8 + len(pointer_usage) * 10
    if backend == "wayland":
        app_protocol_score += 8
    elif backend == "x11":
        app_protocol_score += 4
    app_protocol_commands = _app_protocol_pack_commands(root_q, app_protocol_target_ids)
    if app_protocol_target_count:
        add(
            "app-native-control-adapter",
            "adapter",
            app_protocol_score,
            "App-native control protocol lane",
            "Use this when the project already targets applications that expose real control interfaces such as terminal remote-control APIs, pane CLIs, media-player IPC, or browser userscripts. Route those app-shaped actions through a reviewable adapter lane before reaching for generic key/pointer replay.",
            strengths="Strong for terminal, media, and browser targets that already publish stable control contracts, because the resulting automation is usually more semantic and less desktop-fragile than blind replay.",
            tradeoffs="This is intentionally not a generic desktop backend: every adapter is app-specific and still needs selector/match review plus fallback behavior for hosts where that app or protocol is absent.",
            commands=app_protocol_commands,
            learn_from=app_protocol_learn_from,
            evidence=[
                f"desktop_backend={backend or 'auto'}",
                f"app_protocol_targets={','.join(app_protocol_target_ids)}",
                f"window_usage={len(window_usage)}",
                f"text_usage={len(text_usage)}",
                f"pointer_usage={len(pointer_usage)}",
            ],
        )

    voice_adapter_score = voice_entry_count * 24 + voice_phrase_count * 8 + voice_scoped_entry_count * 12
    if backend == "x11":
        voice_adapter_score += 10
    elif backend == "wayland":
        voice_adapter_score += 6
    if voice_entry_count:
        add(
            "voice-command-adapter",
            "adapter",
            voice_adapter_score,
            "Voice command adapter lane",
            "Use this when the project already has deliberate spoken phrases or voice contexts and should export those commands into a reviewable speech-tool adapter instead of turning VHK into its own recognizer. Keep the speech engine in Talon/Dragonfly and let it call stable VHK command ids.",
            strengths="Strong for projects with a real spoken action catalog because Talon/Dragonfly can own recognition and app-context switching while VHK keeps the macro semantics and artifacts.",
            tradeoffs="Voice exports are intentionally adapter-shaped: phrase quality, per-tool context fidelity, and Linux session fit still belong to the target speech stack, so this should stay a reviewable export lane instead of a generic voice-support checkbox.",
            commands=[
                f"vhk gen-dragonfly-pack {root_q} --out-dir ./build/dragonfly_pack",
                f"vhk gen-talon-pack {root_q} --out-dir ./build/talon_pack",
                f"vhk lint-project {root_q}",
            ],
            learn_from=["Talon contexts", "Dragonfly grammars", "literal spoken command ledgers"],
            evidence=[
                f"desktop_backend={backend or 'auto'}",
                f"voice_commands={voice_entry_count}",
                f"voice_phrases={voice_phrase_count}",
                f"voice_scopes={voice_scoped_entry_count}",
                f"unique_voice_phrases={voice_unique_phrase_count}",
            ],
        )

    mpris_score = mpris_signal_count * 28 + mpris_player_count * 12 + len(flow_macros) * 8 + (6 if backend == "wayland" else 4 if backend == "x11" else 0)
    if mpris_signal_count:
        add(
            "mpris-media-bus-adapter",
            "adapter",
            mpris_score,
            "MPRIS media service-bus lane",
            "Use this when a project is already synchronizing with media-player state over D-Bus. Treat MPRIS/playerctl-class control and follow flows as a Linux-native adapter lane instead of replaying media keys or polling window titles for player state.",
            strengths="Strong for media transport, metadata, and state-change flows because the control path stays on the session bus instead of depending on focus or blind key replay.",
            tradeoffs="Still only fits players that actually expose the MPRIS contract, so it should remain an explicit adapter lane with fallback behavior for apps or hosts that do not publish those bus objects.",
            commands=[
                "vhk doctor --json",
                f"vhk gen-playerctl-pack {root_q} --out-dir ./build/playerctl_pack",
                f"vhk gen-session-fit-pack {root_q} --quiet",
                f"vhk gen-design-pack {root_q} --quiet",
                f"vhk lint-project {root_q}",
            ],
            learn_from=["MPRIS", "playerctl --follow", "playerctld recent-player daemon"],
            evidence=[
                f"desktop_backend={backend or 'auto'}",
                f"mpris_signals={mpris_signal_count}",
                f"mpris_players={','.join(mpris_players) if mpris_players else 'unknown'}",
                f"mpris_members={','.join(mpris_members) if mpris_members else 'unknown'}",
                f"dbus_buses={','.join(mpris_buses) if mpris_buses else 'unknown'}",
            ],
        )

    notification_score = notification_notify_count * 20 + notification_signal_count * 24 + notification_show_message_count * 6 + notification_macro_count * 8 + len(flow_macros) * 4 + (8 if backend == "wayland" else 6 if backend == "x11" else 0)
    if notification_notify_count or notification_signal_count:
        add(
            "desktop-notification-feedback",
            "feedback",
            notification_score,
            "Desktop notification feedback lane",
            "Use this when a project already emits passive status notifications or reacts to notification-daemon signals. Treat desktop notifications as a session-scoped feedback contract instead of flattening progress, alerts, and action prompts into modal UI or stderr chatter.",
            strengths="Strong for passive status, reviewable alerts, and daemon-shaped feedback because Linux desktops already expose a shared notification service instead of forcing every workflow into a custom tray or modal dialog.",
            tradeoffs="Notification capabilities still vary by host and daemon: replacement ids, actions, history, and portal semantics are not identical everywhere, so this should stay an explicit feedback lane with honest fallbacks.",
            commands=[
                "vhk doctor --json",
                f"vhk gen-setup-pack {root_q} --quiet",
                f"vhk gen-design-pack {root_q} --quiet",
                f"vhk lint-project {root_q}",
            ],
            learn_from=["Desktop Notifications spec", "dunstify / dunstctl", "XDG Notification portal"],
            evidence=[
                f"desktop_backend={backend or 'auto'}",
                f"notification_macros={notification_macro_count}",
                f"notify_steps={notification_notify_count}",
                f"show_messages={notification_show_message_count}",
                f"notification_signals={notification_signal_count}",
                f"replaceable_notifications={notification_replaceable_count}",
                f"timed_notifications={notification_timed_count}",
                f"transient_notifications={notification_transient_count}",
                f"actionable_notifications={notification_actionable_count}",
                f"progress_notifications={notification_progress_count}",
                f"notification_members={','.join(notification_members) if notification_members else 'none'}",
                f"notification_buses={','.join(notification_buses) if notification_buses else 'unknown'}",
                f"notify_urgencies={','.join(notification_urgencies) if notification_urgencies else 'normal'}",
            ],
        )

    # Trigger / dispatch surfaces
    wm_score = int(overview.get("bindings") or 0) * 26 + (18 if backend in {"x11", "i3", "sway", "hyprland", "kwin"} else 0) + (8 if hotkey_status in {"unknown", "ok"} else 0)
    if overview.get("bindings"):
        wm_name = backend if backend in {"i3", "sway", "hyprland", "kwin"} else "wm"
        add(
            "wm-native-dispatch",
            "trigger",
            wm_score,
            "WM/compositor-native dispatch",
            "Use this when hotkeys belong to the desktop itself. Thin WM/compositor bindings keep always-on trigger logic out of the main runner and match how Linux users already organize desktop automation.",
            strengths="Low-friction trigger ownership, especially on tiling/window-manager-centric setups.",
            tradeoffs="Desktop-specific exports and syntax become part of the deployment story.",
            commands=[
                f"vhk gen-wm-config {root_q} --wm {wm_name} --out ./build/vhk.{wm_name}.conf",
                f"vhk validate {root_q} --json",
            ],
            learn_from=["i3/sxhkd-style dispatch", "desktop-native binds", "thin trigger plane"],
            evidence=[f"{overview.get('bindings') or 0} binding(s)", f"desktop_backend={backend or 'unknown'}", f"global_hotkeys={hotkey_status}"],
        )

    modal_wm = backend if backend in {"i3", "sway", "hyprland"} else ("i3" if backend == "x11" else "")
    modal_trigger_score = int(overview.get("bindings") or 0) * 24 + int(overview.get("macros") or 0) * 8 + dynamic_portal_bindings * 12
    if backend in {"x11", "i3", "sway", "hyprland"}:
        modal_trigger_score += 22
    if int(overview.get("bindings") or 0) >= 4:
        modal_trigger_score += 12
    if int(overview.get("macros") or 0) >= 4:
        modal_trigger_score += 8
    if modal_wm and (int(overview.get("bindings") or 0) >= 3 or int(overview.get("macros") or 0) >= 5):
        add(
            "wm-modal-trigger-layer",
            "trigger",
            modal_trigger_score,
            "WM mode / submap trigger layer",
            "Use this when an X11/i3-class, sway, or Hyprland project is outgrowing a flat hotkey list. Grouping related actions behind one reviewed entry chord keeps the desktop-native trigger plane fast without pretending every macro deserves its own global binding.",
            strengths="Strong for grouped action families, one-shot command clusters, and reversible desktop-native trigger layers.",
            tradeoffs="Mode/submap UX is WM-specific and still needs reset paths plus fallback launcher surfaces, so it should stay an explicit target-desktop lane instead of a generic Linux trigger promise.",
            commands=[
                f"vhk gen-wm-config {root_q} --wm {modal_wm} --mode-enter Mod4+R --mode-name vhk",
                f"vhk export-wm-bundle {root_q} ./build/wm_bundle --wm {modal_wm} --kind launcher-mode --mode-enter Mod4+R",
                f"vhk validate {root_q} --json",
            ],
            learn_from=["i3 binding modes", "Hyprland submaps", "sxhkd chord chains"],
            evidence=[
                f"desktop_backend={backend}",
                f"{overview.get('bindings') or 0} binding(s)",
                f"{overview.get('macros') or 0} macro(s)",
                f"dynamic_shortcut_candidates={dynamic_portal_bindings}",
            ],
        )

    sxhkd_score = int(overview.get("bindings") or 0) * 20 + (24 if backend in {"x11", "i3"} else -10)
    if overview.get("bindings"):
        add(
            "sxhkd-dispatch",
            "trigger",
            sxhkd_score,
            "sxhkd-style hotkey daemon",
            "Use this when you want an explicit X11-first hotkey daemon instead of baking trigger ownership into the VHK process. It is especially useful for i3/bspwm-style environments and straightforward shell dispatch.",
            strengths="Simple X11-oriented always-on trigger path with familiar hotkey-daemon semantics.",
            tradeoffs="This is not a generic Wayland answer and inherits X11-oriented key naming and deployment constraints.",
            commands=[
                f"vhk gen-sxhkd-config {root_q} --out ./build/vhk.sxhkdrc",
            ],
            learn_from=["sxhkd hotkey daemons", "one trigger daemon, one runner", "X11-first deployment"],
            evidence=[f"{overview.get('bindings') or 0} binding(s)", f"desktop_backend={backend or 'unknown'}"],
        )

    portal_score = int(overview.get("bindings") or 0) * 18 + (18 if backend == "wayland" else 0)
    portal_score += stable_portal_bindings * 14
    portal_score -= dynamic_portal_bindings * 10
    if stable_portal_bindings and not dynamic_portal_bindings:
        portal_score += 10
    elif dynamic_portal_bindings and not stable_portal_bindings:
        portal_score -= 12
    if hotkey_status == "ok":
        portal_score += 22
    elif hotkey_status == "limited":
        portal_score += 8
    elif hotkey_status == "missing":
        portal_score -= 16
    if overview.get("bindings") or hotkey_usage:
        add(
            "portal-global-shortcuts",
            "trigger",
            portal_score,
            "Portal GlobalShortcuts path",
            "Use this when the target environment really supports portal-managed shortcut sessions and the project can predeclare a stable action catalog instead of assuming raw global hooks. Treat it as capability-aware trigger routing, not a generic Linux hotkey checkbox.",
            strengths="Best fit for desktops where explicit portal sessions are the intended integration surface and hotkeys map onto a stable action catalog.",
            tradeoffs="Availability and behavior vary by desktop/backend, and helper-sensitive or rapidly changing hotkey inventories still need compositor or launcher fallbacks.",
            commands=[
                "vhk doctor --json",
                f"vhk gen-portal-shortcuts-spec {root_q} --out ./build/vhk.portal-shortcuts.yml",
                f"vhk validate {root_q} --json",
                f"vhk plan-project {root_q} --json",
            ],
            learn_from=["portal session lifecycle", "stable action catalogs", "capability-aware hotkeys"],
            evidence=[
                f"global_hotkeys={hotkey_status}",
                f"desktop_backend={backend or 'unknown'}",
                f"stable_shortcut_candidates={stable_portal_bindings}",
                f"dynamic_shortcut_candidates={dynamic_portal_bindings}",
                f"{len(hotkey_usage)} hotkey step(s)",
            ],
        )

    # Remap / interception surfaces
    if overview.get("bindings") or raw_key_events:
        keyd_score = int(overview.get("bindings") or 0) * 16 + raw_key_events * 10 + (14 if backend == "wayland" else 6) + (10 if pointer_status in {"missing", "limited"} else 0)
        add(
            "keyd-remap",
            "remap",
            keyd_score,
            "keyd-style remap layer",
            "Use this when low-latency, system-wide key ownership matters more than rich macro graphs. It works well as a companion surface for launch keys, modal leader keys, and desktop-wide remaps that should not depend on the Python runner staying resident.",
            strengths="Very strong for low-latency system-wide remaps and launch keys.",
            tradeoffs="App-scoped behavior and macro richness should stay outside the remapper unless the target environment supports them cleanly.",
            commands=[
                f"vhk gen-keyd-config {root_q} --out ./build/vhk.keyd.conf",
            ],
            learn_from=["evdev/uinput ownership", "system daemon remapping", "launch keys outside the runner"],
            evidence=[f"{overview.get('bindings') or 0} binding(s)", f"{raw_key_events} raw key event(s)", f"pointer_injection={pointer_status}"],
        )

        kanata_score = int(overview.get("bindings") or 0) * 14 + raw_key_events * 11 + (18 if raw_key_events else 0) + (8 if backend == "wayland" else 4)
        add(
            "kanata-remap",
            "remap",
            kanata_score,
            "Kanata-style programmable remap layer",
            "Use this when the trigger/remap story needs richer layers, tap-hold behavior, or programmable key logic before VHK macro execution begins. It is a good companion when modal keyboard UX matters as much as macro playback.",
            strengths="Great fit for layers, tap-hold logic, and more expressive keyboard behavior.",
            tradeoffs="It adds another configuration language and should not become a shadow macro engine for everything.",
            commands=[
                f"vhk gen-kanata-config {root_q} --out ./build/vhk.kanata.kbd",
            ],
            learn_from=["layered remap UX", "advanced key behavior", "keyboard-first modal design"],
            evidence=[f"{overview.get('bindings') or 0} binding(s)", f"{raw_key_events} raw key event(s)"],
        )

        kmonad_score = int(overview.get("bindings") or 0) * 12 + raw_key_events * 10 + (10 if raw_key_events else 0) + (6 if backend == "wayland" else 4)
        add(
            "kmonad-remap",
            "remap",
            kmonad_score,
            "KMonad-style advanced keyboard layer",
            "Use this when you want a very explicit keyboard-management layer with deep customization and you are willing to pay a bit more setup/debug cost for it. It is a good fit for serious keyboard-centric users, less so for quick project deployment.",
            strengths="Strong for keyboard enthusiasts who want a dedicated advanced layer outside the runner.",
            tradeoffs="Steeper configuration/debug story than a lightweight remapper or WM bind export.",
            commands=[
                f"vhk gen-kmonad-config {root_q} --out ./build/vhk.kmonad.kbd",
            ],
            learn_from=["advanced keyboard manager", "dedicated keyboard layer", "deep customization before macro playback"],
            evidence=[f"{overview.get('bindings') or 0} binding(s)", f"{raw_key_events} raw key event(s)"],
        )

        xremap_score = int(overview.get("bindings") or 0) * 13 + raw_key_events * 9 + (16 if backend == "wayland" else 6) + (12 if hotkey_status in {"limited", "missing"} else 4)
        add(
            "xremap-remap",
            "remap",
            xremap_score,
            "xremap-style app-aware remap layer",
            "Use this when app-specific remapping, key sequences, or Wayland-capable remap ownership matter more than keeping every trigger inside the runner. It is a strong reference lane for Linux-native projects that now has an initial VHK exporter instead of living only as a contract note.",
            strengths="Strong for app-aware remaps, key-sequence dispatch, and Wayland-capable remap ownership.",
            tradeoffs="The first exporter is intentionally narrow: it focuses on launch-style bindings, app/window scoping, and runtime handoff to VHK rather than trying to become a shadow macro engine.",
            commands=[
                f"vhk gen-xremap-config {root_q} --out ./build/vhk.xremap.yml",
                f"vhk gen-route-selection-pack {root_q} --quiet",
            ],
            learn_from=["xremap app-specific remapping", "Wayland-capable evdev/uinput path", "key-sequence remap layer"],
            evidence=[f"{overview.get('bindings') or 0} binding(s)", f"{raw_key_events} raw key event(s)", f"global_hotkeys={hotkey_status}"],
        )

    if watcher_count:
        service_score = watcher_count * 24 + (10 if "daemon-friendly" in project_tags else 0) + (8 if capability_issues else 0)
        add(
            "watcher-services",
            "service",
            service_score,
            "Watcher/service deployment",
            "Use this when the project already depends on bus, clipboard, or window events. Packaging the watcher plane as user services makes the system feel Linux-native and keeps event-driven automation from depending on a manually started terminal session.",
            strengths="Best fit for event bridges, long-lived watchers, and service-managed automation.",
            tradeoffs="This is packaging/deployment work, not a replacement for selector cleanup or text-tier design.",
            commands=[
                f"vhk gen-vhk-busd-service {root_q} --out-dir ./build/systemd-user",
                f"vhk gen-vhk-busd-socket-units {root_q} --out-dir ./build/systemd-user",
            ],
            learn_from=["systemd user services", "event bridge packaging", "small always-on daemons"],
            evidence=[f"{watcher_count} watcher(s)", f"{len(capability_issues)} session issue(s)"],
        )

    candidates.sort(key=lambda item: (-int(item.get("score") or 0), str(item.get("category") or ""), str(item.get("title") or "")))
    return candidates


def _project_with_backend(project, backend: str):
    project_data = dict(getattr(project, "__dict__", {}))
    settings_data = dict(getattr(getattr(project, "settings", None), "__dict__", {}))
    settings_data["desktop_backend"] = backend
    project_data["settings"] = SimpleNamespace(**settings_data)
    return SimpleNamespace(**project_data)


def _capability_status(
    capability_matrix: Mapping[str, Any] | None,
    name: str,
    *,
    default: str = "unknown",
) -> str:
    item = capability_matrix.get(name) if isinstance(capability_matrix, Mapping) else None
    if isinstance(item, Mapping):
        return str(item.get("status") or default)
    return default


def _scenario_capability_matrix(
    scenario_id: str,
) -> tuple[dict[str, dict[str, object]], list[str], list[str], str]:
    def entry(
        status: str,
        *,
        recommended: str | None = None,
        mechanisms: list[str] | None = None,
        notes: list[str] | None = None,
        portal_backends: list[str] | None = None,
    ) -> dict[str, object]:
        return {
            "status": status,
            "mechanisms": list(mechanisms or ([] if recommended is None else [recommended])),
            "recommended": recommended,
            "notes": list(notes or []),
            "portal_backends": list(portal_backends or []),
        }

    scenarios: dict[str, tuple[dict[str, dict[str, object]], list[str], list[str], str]] = {
        "portable-text": (
            {
                "screen_capture": entry("limited", recommended="portal:Screenshot", mechanisms=["portal:Screenshot"], portal_backends=["generic"]),
                "text_injection": entry("ok", recommended="wtype", mechanisms=["wtype", "clipboard"]),
                "pointer_injection": entry("missing", mechanisms=[]),
                "global_hotkeys": entry("limited", recommended="launcher/palette", mechanisms=["launcher", "desktop-file"]),
                "window_introspection": entry("limited", recommended="launcher metadata", mechanisms=["launcher metadata"]),
                "input_capture": entry("missing", mechanisms=[]),
            },
            [
                "Treat this as the conservative baseline when you want the same project to ship across mixed desktops.",
                "Assume rich pointer automation is optional and text/forms carry most of the product value.",
            ],
            ["Espanso-style portability", "launcher-first distribution", "forms before pointer playback"],
            "Portable baseline that tests whether the project can survive as text, palette, and watcher surfaces before you depend on desktop-specific input guarantees.",
        ),
        "x11-i3": (
            {
                "screen_capture": entry("ok", recommended="mss", mechanisms=["mss", "x11grab"]),
                "text_injection": entry("ok", recommended="xdotool", mechanisms=["xdotool", "xte"]),
                "pointer_injection": entry("ok", recommended="xdotool", mechanisms=["xdotool"]),
                "global_hotkeys": entry("ok", recommended="wm-bind", mechanisms=["i3 bindsym", "sxhkd"]),
                "window_introspection": entry("ok", recommended="wmctrl", mechanisms=["wmctrl", "xprop"]),
                "input_capture": entry("ok", recommended="xinput", mechanisms=["xinput", "XRecord/XI2"]),
            },
            [
                "Model the classic fast-path: WM-native binds, broad pointer control, and X11 window/context tooling.",
                "Use this as the reference profile for AHK-like breadth rather than as a promise that every desktop behaves this way.",
            ],
            ["i3/sxhkd dispatch", "single-runner desktop automation", "X11-first ownership of hotkeys and pointers"],
            "Reference profile for the least constrained desktop-automation path: broad hotkeys, pointer control, and window inspection through X11-native surfaces.",
        ),
        "gnome-wayland": (
            {
                "screen_capture": entry("ok", recommended="portal:ScreenCast", mechanisms=["portal:ScreenCast", "portal:Screenshot"], portal_backends=["gnome"]),
                "text_injection": entry("ok", recommended="wtype", mechanisms=["wtype", "clipboard"]),
                "pointer_injection": entry("limited", recommended="portal/helper", mechanisms=["portal:RemoteDesktop(pointer)", "helper"], notes=["explicit consent/session lifecycle"], portal_backends=["gnome"]),
                "global_hotkeys": entry("limited", recommended="portal:GlobalShortcuts", mechanisms=["portal:GlobalShortcuts", "shell/WM bind"], notes=["desktop/version dependent"], portal_backends=["gnome"]),
                "window_introspection": entry("limited", recommended="shell metadata bridge", mechanisms=["shell metadata bridge"]),
                "input_capture": entry("limited", recommended="portal:InputCapture", mechanisms=["portal:InputCapture"], notes=["explicit session model"], portal_backends=["gnome"]),
            },
            [
                "Assume portals are the first stop for capture and shortcuts, but keep helper boundaries for pointer-heavy flows.",
                "Treat shell/window context as a narrower, desktop-shaped surface than on X11.",
            ],
            ["portal session lifecycle", "consent-aware capture", "helper boundary for pointer-heavy automation"],
            "Portal-forward Wayland profile with conservative assumptions around pointer injection and app/window context. Good for capture, text, and explicit-session workflows.",
        ),
        "kde-wayland": (
            {
                "screen_capture": entry("ok", recommended="portal:ScreenCast", mechanisms=["portal:ScreenCast", "portal:Screenshot"], portal_backends=["kde"]),
                "text_injection": entry("ok", recommended="wtype", mechanisms=["wtype", "clipboard"]),
                "pointer_injection": entry("limited", recommended="portal/helper", mechanisms=["portal:RemoteDesktop(pointer)", "helper"], notes=["desktop/version dependent"], portal_backends=["kde"]),
                "global_hotkeys": entry("ok", recommended="portal:GlobalShortcuts", mechanisms=["portal:GlobalShortcuts", "wm bind"], portal_backends=["kde"]),
                "window_introspection": entry("limited", recommended="window metadata bridge", mechanisms=["window metadata bridge"]),
                "input_capture": entry("limited", recommended="portal:InputCapture", mechanisms=["portal:InputCapture"], notes=["desktop/version dependent"], portal_backends=["kde"]),
            },
            [
                "Assume a strong portal story for shortcuts/capture, but keep pointer-heavy automation behind capability checks and helper seams.",
                "Use KDE as the optimistic portal-centric Wayland profile, not as a generic replacement for desktop-specific validation.",
            ],
            ["portal-centric deployment", "capability-aware shortcuts", "helper seam for the last mile"],
            "Optimistic portal-centric Wayland profile: stronger shortcut story than the conservative wlroots/Hyprland lanes, but still not a license to collapse everything into one backend.",
        ),
        "wlroots-sway-conservative": (
            {
                "screen_capture": entry("ok", recommended="portal:ScreenCast", mechanisms=["portal:ScreenCast", "grim/slurp"], portal_backends=["wlr"]),
                "text_injection": entry("ok", recommended="wtype", mechanisms=["wtype", "clipboard"]),
                "pointer_injection": entry("missing", mechanisms=[]),
                "global_hotkeys": entry("missing", mechanisms=[]),
                "window_introspection": entry("ok", recommended="swaymsg", mechanisms=["swaymsg", "IPC"]),
                "input_capture": entry("missing", mechanisms=[]),
            },
            [
                "Assume compositor-native binds and IPC are the stable trigger/context surfaces, while portal parity remains incomplete.",
                "This profile intentionally underrates generic pointer/global-shortcut promises so the plan stays deployable.",
            ],
            ["sway/wlroots IPC", "conservative portal expectations", "service + bind split"],
            "Conservative wlroots profile that rewards binds, watchers, launchers, and text tiers while treating pointer and generic global-capture stories as helper-only or missing.",
        ),
        "hyprland-conservative": (
            {
                "screen_capture": entry("ok", recommended="portal:ScreenCast", mechanisms=["portal:ScreenCast", "hyprpicker/grim"], portal_backends=["hyprland"]),
                "text_injection": entry("ok", recommended="wtype", mechanisms=["wtype", "clipboard"]),
                "pointer_injection": entry("missing", mechanisms=[]),
                "global_hotkeys": entry("limited", recommended="hyprland binds", mechanisms=["hyprland binds", "portal:GlobalShortcuts"], notes=["prefer compositor-native binds"], portal_backends=["hyprland"]),
                "window_introspection": entry("ok", recommended="hyprctl", mechanisms=["hyprctl"]),
                "input_capture": entry("missing", mechanisms=[]),
            },
            [
                "Assume Hyprland-native binds and metadata work better than a portal-only trigger story for automation projects today.",
                "Treat pointer and input-capture features as explicit helper-boundary work items, not default capabilities.",
            ],
            ["Hyprland-native binds", "hyprctl metadata bridges", "helper-boundary Wayland automation"],
            "Hyprland-specific conservative profile: strong compositor-native dispatch, good metadata bridges, but explicit caution around RemoteDesktop/InputCapture-class automation surfaces.",
        ),
    }
    return scenarios[scenario_id]


def _scenario_capability_issues(
    capability_usage: Mapping[str, list[dict[str, object]]] | None,
    capability_matrix: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    capability_usage = capability_usage or {}
    issues: list[dict[str, Any]] = []
    labels = {
        "screen_capture": "screen capture",
        "text_injection": "text injection",
        "pointer_injection": "pointer injection",
        "global_hotkeys": "global hotkeys",
        "window_introspection": "window introspection",
        "input_capture": "input capture",
    }
    for name, label in labels.items():
        uses = list(capability_usage.get(name) or [])
        if not uses:
            continue
        status = _capability_status(capability_matrix, name)
        if status not in {"missing", "limited"}:
            continue
        issues.append({
            "capability": name,
            "severity": "warning" if status == "limited" else "error",
            "message": f"{label} is {status} in this target environment",
            "suggestion": "Prefer text/export surfaces, compositor/WM binds, or helper boundaries for this environment.",
            "used_by": sorted({str(item.get("macro")) for item in uses if item.get("macro")}),
        })
    return issues


def _environment_diffs(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    macro_profiles: list[dict[str, Any]],
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
) -> list[dict[str, Any]]:
    capability_usage = capability_usage or {}
    scenario_defs = [
        ("portable-text", "Portable text baseline", "wayland"),
        ("x11-i3", "X11/i3 reference", "x11"),
        ("gnome-wayland", "GNOME Wayland conservative", "wayland"),
        ("kde-wayland", "KDE Wayland portal-first", "wayland"),
        ("wlroots-sway-conservative", "wlroots/sway conservative", "wayland"),
        ("hyprland-conservative", "Hyprland conservative", "wayland"),
    ]

    comparisons: list[dict[str, Any]] = []
    for scenario_id, title, backend in scenario_defs:
        matrix, assumptions, learn_from, summary = _scenario_capability_matrix(scenario_id)
        scenario_project = _project_with_backend(project, backend)
        issues = _scenario_capability_issues(capability_usage, matrix)
        profiles = _deployment_profiles(
            project=scenario_project,
            overview=overview,
            project_tags=project_tags,
            macro_profiles=macro_profiles,
            capability_usage=capability_usage,
            capability_matrix=matrix,
            capability_issues=issues,
        )
        desktop_targets = _desktop_targets(
            project=scenario_project,
            overview=overview,
            project_tags=project_tags,
            macro_profiles=macro_profiles,
            capability_usage=capability_usage,
            capability_matrix=matrix,
            capability_issues=issues,
        )
        surface_choices = _surface_choices(
            project=scenario_project,
            overview=overview,
            project_tags=project_tags,
            macro_profiles=macro_profiles,
            capability_usage=capability_usage,
            capability_matrix=matrix,
            capability_issues=issues,
        )

        top_profile = profiles[0] if profiles else {}
        top_target = desktop_targets[0] if desktop_targets else {}
        preferred_surfaces: list[dict[str, Any]] = []
        seen_categories: set[str] = set()
        for item in surface_choices:
            category = str(item.get("category") or "")
            if category in seen_categories:
                continue
            preferred_surfaces.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "category": category,
                "score": item.get("score"),
                "fit": item.get("fit"),
            })
            seen_categories.add(category)
            if len(preferred_surfaces) >= 4:
                break

        surface_scores = [int(item.get("score") or 0) for item in preferred_surfaces[:3]]
        profile_score = int(top_profile.get("score") or 0)
        target_score = int(top_target.get("score") or 0)
        average_surface = int(round(sum(surface_scores) / len(surface_scores))) if surface_scores else 0
        score = max(0, min(100, int(round((profile_score + target_score + average_surface) / 3))))

        blockers = sorted({
            *(str(x) for x in (top_profile.get("blocking_capabilities") or []) if str(x)),
            *(str(x) for x in (top_target.get("blocking_capabilities") or []) if str(x)),
            *(str(item.get("capability") or "") for item in issues if str(item.get("capability") or "")),
        })

        highlights: list[str] = []
        for name in ["screen_capture", "pointer_injection", "global_hotkeys", "window_introspection", "input_capture"]:
            if capability_usage.get(name):
                status = _capability_status(matrix, name)
                if status != "ok":
                    highlights.append(f"{name}={status}")
        if not highlights:
            highlights.append("no obvious capability blockers for the current project shape")

        commands: list[str] = []
        for cmd in [
            *((top_profile.get("commands") or [])[:2] if isinstance(top_profile, Mapping) else []),
            *((top_target.get("commands") or [])[:2] if isinstance(top_target, Mapping) else []),
        ]:
            if cmd and cmd not in commands:
                commands.append(str(cmd))
        for item in surface_choices[:3]:
            for cmd in (item.get("commands") or [])[:1]:
                if cmd and cmd not in commands:
                    commands.append(str(cmd))
            if len(commands) >= 6:
                break

        comparisons.append({
            "id": scenario_id,
            "title": title,
            "backend": backend,
            "score": score,
            "fit": _fit_label(score),
            "summary": summary,
            "assumptions": assumptions,
            "learn_from": learn_from,
            "capability_statuses": {name: _capability_status(matrix, name) for name in ["screen_capture", "text_injection", "pointer_injection", "global_hotkeys", "window_introspection", "input_capture"]},
            "top_profile": {
                "id": top_profile.get("id"),
                "title": top_profile.get("title"),
                "fit": top_profile.get("fit"),
                "score": top_profile.get("score"),
            },
            "top_target": {
                "id": top_target.get("id"),
                "title": top_target.get("title"),
                "fit": top_target.get("fit"),
                "score": top_target.get("score"),
            },
            "preferred_surfaces": preferred_surfaces,
            "blocking_capabilities": blockers,
            "diff_highlights": highlights,
            "commands": commands[:6],
        })

    comparisons.sort(key=lambda item: (-int(item.get("score") or 0), str(item.get("title") or "")))
    return comparisons




def _portability_gaps(
    environment_diffs: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Compare the strongest environment plan against more conservative ones.

    This keeps plan-project from stopping at "X11 looks best" or
    "Hyprland is conservative". It explains what *actually changes* when the
    same project moves between those targets.
    """

    environment_diffs = list(environment_diffs or [])
    if len(environment_diffs) < 2:
        return []

    def status_rank(status: str) -> int:
        return {"missing": 0, "limited": 1, "unknown": 1, "ok": 2}.get(str(status or "unknown"), 1)

    baseline = environment_diffs[0]
    base_statuses = dict(baseline.get("capability_statuses") or {})
    base_blockers = {str(x) for x in (baseline.get("blocking_capabilities") or []) if str(x)}
    base_surfaces = {str(item.get("category") or ""): item for item in (baseline.get("preferred_surfaces") or []) if str(item.get("category") or "")}

    gaps: list[dict[str, Any]] = []
    for candidate in environment_diffs[1:]:
        candidate_statuses = dict(candidate.get("capability_statuses") or {})
        candidate_blockers = {str(x) for x in (candidate.get("blocking_capabilities") or []) if str(x)}
        candidate_surfaces = {str(item.get("category") or ""): item for item in (candidate.get("preferred_surfaces") or []) if str(item.get("category") or "")}

        newly_blocked = sorted(candidate_blockers - base_blockers)
        relaxed_blockers = sorted(base_blockers - candidate_blockers)

        degraded_capabilities: list[str] = []
        for name in sorted(set(base_statuses) | set(candidate_statuses)):
            if status_rank(str(candidate_statuses.get(name) or "unknown")) < status_rank(str(base_statuses.get(name) or "unknown")):
                degraded_capabilities.append(name)

        keep_surfaces: list[dict[str, Any]] = []
        replace_surfaces: list[dict[str, Any]] = []
        new_preferred: list[dict[str, Any]] = []
        for category in sorted(set(base_surfaces) | set(candidate_surfaces)):
            base_item = base_surfaces.get(category)
            cand_item = candidate_surfaces.get(category)
            if base_item and cand_item and str(base_item.get("id")) == str(cand_item.get("id")):
                keep_surfaces.append({
                    "id": cand_item.get("id"),
                    "title": cand_item.get("title"),
                    "category": category,
                })
                continue
            if cand_item:
                new_preferred.append({
                    "id": cand_item.get("id"),
                    "title": cand_item.get("title"),
                    "category": category,
                })
            if base_item and cand_item:
                replace_surfaces.append({
                    "category": category,
                    "from": {"id": base_item.get("id"), "title": base_item.get("title")},
                    "to": {"id": cand_item.get("id"), "title": cand_item.get("title")},
                })
            elif base_item and not cand_item:
                replace_surfaces.append({
                    "category": category,
                    "from": {"id": base_item.get("id"), "title": base_item.get("title")},
                    "to": None,
                })

        score_delta = int(baseline.get("score") or 0) - int(candidate.get("score") or 0)
        if newly_blocked or degraded_capabilities or replace_surfaces or score_delta >= 10:
            actions: list[str] = []
            if "pointer_injection" in newly_blocked or "pointer_injection" in degraded_capabilities:
                actions.append("move pointer-heavy flows behind helper boundaries or replace them with text/selectors")
            if "global_hotkeys" in newly_blocked or "global_hotkeys" in degraded_capabilities:
                actions.append("shift always-on triggers into WM/compositor binds, remappers, or launcher surfaces")
            if "window_introspection" in degraded_capabilities:
                actions.append("prefer compositor metadata bridges or app-scoped text flows over deep window scripting")
            if not actions and replace_surfaces:
                actions.append("swap the trigger/integration surface while keeping macro logic in the runner core")
            if not actions:
                actions.append("treat this as a conservative deployment lane and validate capabilities before shipping")

            commands: list[str] = []
            for cmd in (candidate.get("commands") or [])[:4]:
                if cmd and cmd not in commands:
                    commands.append(str(cmd))

            gaps.append({
                "id": str(candidate.get("id") or ""),
                "title": str(candidate.get("title") or ""),
                "baseline": {
                    "id": baseline.get("id"),
                    "title": baseline.get("title"),
                    "score": baseline.get("score"),
                    "fit": baseline.get("fit"),
                },
                "score": candidate.get("score"),
                "fit": candidate.get("fit"),
                "score_delta": score_delta,
                "summary": candidate.get("summary"),
                "newly_blocked_capabilities": newly_blocked,
                "degraded_capabilities": degraded_capabilities,
                "relaxed_blockers": relaxed_blockers,
                "keep_surfaces": keep_surfaces[:4],
                "replace_surfaces": replace_surfaces[:4],
                "new_preferred_surfaces": new_preferred[:4],
                "migration_response": "; ".join(actions),
                "commands": commands,
                "learn_from": list(candidate.get("learn_from") or []),
            })

    gaps.sort(key=lambda item: (-int(item.get("score_delta") or 0), str(item.get("title") or "")))
    return gaps



def _portability_playbooks(
    *,
    project,
    portability_gaps: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Turn portability gaps into concrete export/install playbooks.

    `portability_gaps` explains *what* changes between environment targets. This
    helper goes a step further and suggests *which artifacts to generate* and
    *which validation loop to run* so the portability story becomes shippable.
    """

    portability_gaps = list(portability_gaps or [])
    if not portability_gaps:
        return []

    root_q = shlex.quote(str(getattr(project, "root_dir", ".") or "."))
    build_dir = "./build"

    env_to_wm = {
        "x11-i3": "i3",
        "wlroots-sway-conservative": "sway",
        "hyprland-conservative": "hyprland",
    }

    def _dedupe_keep_order(values: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in values:
            val = str(item or "").strip()
            if not val or val in seen:
                continue
            seen.add(val)
            out.append(val)
        return out

    playbooks: list[dict[str, Any]] = []
    for gap in portability_gaps:
        env_id = str(gap.get("id") or "")
        title = str(gap.get("title") or env_id or "Portability lane")
        baseline = gap.get("baseline") or {}
        new_blockers = [str(x) for x in (gap.get("newly_blocked_capabilities") or []) if str(x)]
        degraded = [str(x) for x in (gap.get("degraded_capabilities") or []) if str(x)]
        replace_surfaces = list(gap.get("replace_surfaces") or [])
        preferred_surfaces = list(gap.get("new_preferred_surfaces") or [])
        keep_surfaces = list(gap.get("keep_surfaces") or [])

        artifacts: list[dict[str, Any]] = []
        commands: list[str] = []
        install_checks: list[str] = []
        related_surfaces: list[str] = []

        def add_artifact(id: str, title: str, path_hint: str | None, reason: str) -> None:
            if not any(str(item.get("id") or "") == id for item in artifacts):
                artifacts.append({
                    "id": id,
                    "title": title,
                    "path_hint": path_hint,
                    "reason": reason,
                })

        def add_command(cmd: str) -> None:
            val = str(cmd or "").strip()
            if val and val not in commands:
                commands.append(val)

        def add_check(text: str) -> None:
            val = str(text or "").strip()
            if val and val not in install_checks:
                install_checks.append(val)

        def surface_records() -> list[dict[str, Any]]:
            rows: list[dict[str, Any]] = []
            for change in replace_surfaces:
                if isinstance(change, Mapping) and isinstance(change.get("to"), Mapping):
                    item = dict(change.get("to") or {})
                    item.setdefault("category", change.get("category"))
                    rows.append(item)
            for item in preferred_surfaces:
                if isinstance(item, Mapping):
                    rows.append(dict(item))
            for item in keep_surfaces:
                if isinstance(item, Mapping):
                    rows.append(dict(item))
            return rows

        for surface in surface_records():
            sid = str(surface.get("id") or "")
            cat = str(surface.get("category") or "")
            if sid:
                related_surfaces.append(sid)

            if sid == "espanso-text-package":
                add_artifact(
                    "espanso-package",
                    "Espanso package export",
                    f"{build_dir}/espanso_package",
                    "Keep text expansion portable and app-scoped even when richer desktop capabilities fall away.",
                )
                add_command(f"vhk gen-espanso {root_q} --package-dir {build_dir}/espanso_package")
                add_check("Install or compare the generated package under the user's Espanso packages directory before claiming snippet portability.")
            elif sid == "vhk-palette-launcher":
                add_artifact(
                    "desktop-entry",
                    "Desktop entry",
                    f"{build_dir}/vhk-project.desktop",
                    "Expose the project through a desktop-native launcher surface when global hotkeys become conditional.",
                )
                add_artifact(
                    "launcher-script",
                    "Launcher helper script",
                    f"{build_dir}/vhk-launch",
                    "Keep prompt-rich and preset-driven flows reachable without a persistent global hook.",
                )
                add_command(f"vhk export-desktop-entry {root_q} {build_dir}/vhk-project.desktop")
                add_command(f"vhk export-launcher-script {root_q} {build_dir}/vhk-launch")
                add_check("Verify the desktop entry's Exec path and any quick actions against the target session's launcher/menu behavior.")
            elif sid == "wm-native-dispatch":
                wm = env_to_wm.get(env_id)
                if wm:
                    add_artifact(
                        f"{wm}-bindings",
                        f"{wm} binding snippet",
                        f"{build_dir}/vhk.{wm}.conf",
                        "Move trigger ownership into the window manager/compositor when generic global shortcuts are weaker than desktop-native binds.",
                    )
                    add_command(f"vhk export-wm-bindings {root_q} {build_dir}/vhk.{wm}.conf --wm {wm} --launcher palette-command")
                    add_check(f"Include the generated {wm} snippet once in the parent config and reload the compositor before evaluating trigger reliability.")
            elif sid == "sxhkd-dispatch":
                add_artifact(
                    "sxhkd-config",
                    "sxhkd hotkey config",
                    f"{build_dir}/vhk.sxhkdrc",
                    "Keep an X11-first hotkey daemon option available when compositor-native bindings are not the right deployment surface.",
                )
                add_command(f"vhk gen-sxhkd-config {root_q} --out {build_dir}/vhk.sxhkdrc")
                add_check("Reload sxhkd after installing the generated config so the trigger path is tested exactly as deployed.")
            elif sid == "portal-global-shortcuts":
                add_artifact(
                    "portal-capability-audit",
                    "Portal capability audit",
                    None,
                    "Treat portal-managed shortcuts as a validated session capability, not as a generic Linux checkbox.",
                )
                add_check("Review the active portal routing and backend selection before treating portal hotkeys as part of the shipping story.")
            elif sid == "keyd-remap":
                add_artifact(
                    "keyd-config",
                    "keyd config",
                    f"{build_dir}/vhk.keyd.conf",
                    "Shift low-latency key ownership into a remapper when the target environment wants launch keys outside the runner.",
                )
                add_command(f"vhk gen-keyd-config {root_q} --out {build_dir}/vhk.keyd.conf")
                add_check("Test the generated keyd config with the target user/session wrapper, because user-session tools and portals often matter for the launched macro path.")
            elif sid == "kanata-remap":
                add_artifact(
                    "kanata-config",
                    "Kanata config",
                    f"{build_dir}/vhk.kanata.kbd",
                    "Carry layered/tap-hold trigger behavior into a programmable remap layer instead of re-implementing it in the runner.",
                )
                add_command(f"vhk gen-kanata-config {root_q} --out {build_dir}/vhk.kanata.kbd")
                add_check("Confirm command execution and layer semantics in the real target session; Kanata is a companion surface, not a substitute macro runtime.")
            elif sid == "kmonad-remap":
                add_artifact(
                    "kmonad-config",
                    "KMonad config",
                    f"{build_dir}/vhk.kmonad.kbd",
                    "Offer a deeper keyboard-management lane when the deployment story favors an explicit advanced key layer.",
                )
                add_command(f"vhk gen-kmonad-config {root_q} --out {build_dir}/vhk.kmonad.kbd")
                add_check("Validate the selected input/output expressions and leader behavior on the destination machine before presenting KMonad as the supported trigger surface.")
            elif sid == "xremap-remap":
                add_artifact(
                    "xremap-config",
                    "xremap config",
                    f"{build_dir}/vhk.xremap.yml",
                    "Carry app-aware remap ownership into an xremap lane while still letting VHK own the macro/runtime graph.",
                )
                add_command(f"vhk gen-xremap-config {root_q} --out {build_dir}/vhk.xremap.yml")
                add_check("Validate application/app_id naming on the target compositor before presenting the generated xremap config as the supported app-aware trigger surface.")
            elif sid == "watcher-services":
                add_artifact(
                    "systemd-user-units",
                    "systemd user units",
                    f"{build_dir}/systemd-user",
                    "Package watcher-driven automation as services so the event plane matches Linux-native deployment patterns.",
                )
                add_command(f"vhk gen-vhk-busd-service {root_q} --out-dir {build_dir}/systemd-user")
                add_command(f"vhk gen-vhk-busd-socket-units {root_q} --out-dir {build_dir}/systemd-user")
                add_check("Enable and test the generated user units under the target user's systemd manager instead of relying on a hand-started terminal session.")

        if "pointer_injection" in new_blockers or "pointer_injection" in degraded:
            add_artifact(
                "pointer-helper-boundary",
                "Pointer helper boundary review",
                None,
                "Pointer-heavy flows need an explicit helper/compositor seam in this target environment rather than an implied generic backend.",
            )
            add_command(f"vhk optimize-project {root_q}")
            add_command(f"vhk report --project {root_q} --latest --json")
            add_check("Demote any blanket pointer-support claims; keep pointer-heavy flows behind helper boundaries or replace them with text/selector paths on this target.")

        if "global_hotkeys" in new_blockers or "global_hotkeys" in degraded:
            add_check("Prefer WM/compositor binds, remapper launch keys, launcher actions, or palette entry points over a generic global-hook promise in this target.")
            if not any(str(item.get("id") or "") in {"desktop-entry", "launcher-script"} for item in artifacts):
                add_artifact(
                    "desktop-entry",
                    "Desktop entry",
                    f"{build_dir}/vhk-project.desktop",
                    "Provide a launcher fallback when always-on shortcut ownership becomes weaker or more desktop-specific.",
                )
                add_command(f"vhk export-desktop-entry {root_q} {build_dir}/vhk-project.desktop")

        if "window_introspection" in degraded:
            add_check("Reduce dependence on deep window scripting in this lane; prefer compositor metadata bridges, launcher flows, and app-scoped text surfaces where possible.")

        add_command("vhk doctor --json")
        add_command(f"vhk validate {root_q} --json")
        add_command(f"vhk plan-project {root_q} --json")

        priority = "high" if new_blockers or int(gap.get("score_delta") or 0) >= 15 else "medium"
        goal_bits: list[str] = []
        if new_blockers or degraded:
            goal_bits.append("replace desktop assumptions that no longer hold")
        if replace_surfaces:
            goal_bits.append("swap trigger/integration surfaces without rewriting macro logic")
        if not goal_bits:
            goal_bits.append("keep the project shippable on a more conservative desktop lane")

        playbooks.append({
            "id": env_id,
            "title": title,
            "priority": priority,
            "goal": f"Move from {baseline.get('title') or 'the baseline lane'} to {title} and " + ", ".join(goal_bits) + ".",
            "summary": str(gap.get("migration_response") or gap.get("summary") or ""),
            "artifacts": artifacts[:8],
            "commands": commands[:10],
            "install_checks": install_checks[:8],
            "related_surfaces": _dedupe_keep_order(related_surfaces)[:8],
            "learn_from": list(gap.get("learn_from") or []),
            "baseline": {
                "id": baseline.get("id"),
                "title": baseline.get("title"),
                "score": baseline.get("score"),
                "fit": baseline.get("fit"),
            },
        })

    playbooks.sort(key=lambda item: ({"high": 0, "medium": 1, "low": 2}.get(str(item.get("priority") or "medium"), 1), str(item.get("title") or "")))
    return playbooks



def _toolchain_choices(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    macro_profiles: list[dict[str, Any]],
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
    capability_matrix: Mapping[str, Any] | None = None,
    capability_issues: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Recommend concrete external toolchains for the current project shape.

    Earlier planning layers describe *where* a project should land (text tier,
    remap tier, helper boundary, WM dispatch, etc.). This layer answers a more
    operational question: which concrete Linux toolchains should VHK prefer for
    each capability, given the current backend, session capability matrix, and
    project shape?
    """

    capability_usage = capability_usage or {}
    capability_issues = list(capability_issues or [])
    capability_matrix = capability_matrix or {}

    backend = str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "").strip().lower()
    root_dir = getattr(project, "root_dir", None) or "."
    root_q = shlex.quote(str(root_dir))

    pointer_usage = list(capability_usage.get("pointer_injection") or [])
    text_usage = list(capability_usage.get("text_injection") or [])
    capture_usage = list(capability_usage.get("screen_capture") or [])
    hotkey_usage = list(capability_usage.get("global_hotkeys") or [])
    window_usage = list(capability_usage.get("window_introspection") or [])

    vision_macros = [m for m in macro_profiles if "vision-heavy" in (m.get("tags") or [])]
    text_macros = [m for m in macro_profiles if "text-expander" in (m.get("tags") or [])]
    flow_macros = [m for m in macro_profiles if "flow-heavy" in (m.get("tags") or [])]
    watcher_count = int(overview.get("clipboard_watchers") or 0) + int(overview.get("bus_watchers") or 0) + int(overview.get("window_watchers") or 0)
    issue_caps = {str(item.get("capability") or "") for item in capability_issues if str(item.get("capability") or "")}

    toolchains: list[dict[str, Any]] = []

    def _dedupe_keep_order(values: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in values:
            val = str(item or "").strip()
            if not val or val in seen:
                continue
            seen.add(val)
            out.append(val)
        return out

    def _matrix_entry(name: str) -> Mapping[str, Any]:
        item = capability_matrix.get(name) if isinstance(capability_matrix, Mapping) else None
        return item if isinstance(item, Mapping) else {}

    def _preferred_from_matrix(name: str) -> tuple[str | None, list[str], str]:
        item = _matrix_entry(name)
        recommended = str(item.get("recommended") or "").strip() or None
        mechanisms = [str(x).strip() for x in (item.get("mechanisms") or []) if str(x).strip()]
        status = str(item.get("status") or "unknown").strip().lower() or "unknown"
        return recommended, mechanisms, status

    def _defaults(name: str) -> tuple[str, list[str], list[str], str, str, list[str], list[str]]:
        if backend == "x11":
            mapping = {
                "text_injection": (
                    "xdotool",
                    ["xdotool", "xvkbd"],
                    ["xdotool", "xvkbd"],
                    "X11 text injection is mature enough that a direct XTEST-style toolchain is the fast path for typing-heavy macros.",
                    "This stays tied to X11 semantics and should not be treated as a portable Wayland answer.",
                    [f"vhk validate {root_q} --json", "vhk doctor --json"],
                    ["xdotool", "XTEST-backed input on X11"],
                ),
                "pointer_injection": (
                    "xdotool",
                    ["xdotool", "xte"],
                    ["xdotool", "xautomation/xte"],
                    "X11 pointer automation is broad and low-friction enough to keep pointer playback in the standard desktop toolchain.",
                    "Coordinate-heavy playback can still be brittle across themes, scaling, and XWayland boundaries.",
                    [f"vhk validate {root_q} --json", "vhk doctor --json"],
                    ["xdotool", "X11 pointer control"],
                ),
                "screen_capture": (
                    "mss",
                    ["mss", "maim/scrot", "x11grab"],
                    ["python-mss", "maim", "scrot"],
                    "Vision-heavy X11 projects can lean on direct screenshot tooling and in-process capture without a portal session boundary.",
                    "Raw screenshot speed does not remove the need for selector cleanup or retry discipline.",
                    ["vhk doctor --json", f"vhk preview-needle path/to/needle.png --project {root_q} --haystack path/to/screenshot.png --json --no-check"],
                    ["mss", "maim/scrot", "X11 capture path"],
                ),
                "global_hotkeys": (
                    "wm-bind/sxhkd",
                    ["i3 bindsym", "sxhkd", "launcher"],
                    ["sxhkd", "i3/sway config"],
                    "On X11 tiling setups, WM-native bindings and sxhkd-style dispatch are still the simplest low-latency trigger plane.",
                    "The bind layer should stay thin; do not re-implement rich macro logic inside hotkey configs.",
                    [f"vhk export-wm-bundle {root_q} ./build/wm_bundle --wm i3 --kind binding --key Mod4+semicolon", f"vhk gen-sxhkd-config {root_q} --out ./build/vhk.sxhkdrc"],
                    ["i3/sxhkd", "thin dispatch plane"],
                ),
                "window_introspection": (
                    "wmctrl",
                    ["wmctrl", "xprop", "xwininfo", "AT-SPI/Accerciser", "dogtail/pyatspi"],
                    ["wmctrl", "xprop", "xwininfo", "accerciser", "dogtail"],
                    "Window-sensitive X11 projects benefit from stable, scriptable context tools for focus/title/geometry, plus an explicit AT-SPI lane when structured widget targeting is healthier than raw window metadata alone.",
                    "Window metadata and accessibility coverage are both app/session-shaped, so keep semantic selectors and coordinate fallbacks behind reviewable seams instead of assuming one probe solves everything.",
                    ["vhk doctor --json", f"vhk window-spy --project {root_q} --json --no-check", f"vhk gen-session-fit-pack {root_q} --quiet"],
                    ["wmctrl/xprop", "AT-SPI/Accerciser", "dogtail structured UI automation"],
                ),
                "input_capture": (
                    "xinput",
                    ["xinput", "XI2/XRecord"],
                    ["xinput"],
                    "If the project eventually needs lower-level capture on X11, keep that separate from the main runner and reach for X11-native input tooling.",
                    "This is a specialized surface and should not become the default requirement for text or launcher-shaped projects.",
                    ["vhk doctor --json", f"vhk plan-project {root_q} --json --no-session-check"],
                    ["xinput", "X11 input capture"],
                ),
            }
            return mapping[name]

        mapping = {
            "text_injection": (
                "clipboard",
                ["wtype", "clipboard", "dotoolc", "ydotool"],
                ["wl-clipboard", "wtype", "dotool", "ydotool"],
                "For Wayland-class projects, treat fast text entry as a split lane: prefer package/clipboard-friendly flows by default, then add virtual-keyboard typing only on sessions that explicitly prove it.",
                "Virtual-keyboard support varies by compositor/protocol, so do not market `wtype` as a generic Wayland text guarantee; keep clipboard or daemon-backed uinput fallbacks available.",
                [f"vhk validate {root_q} --json", f"vhk gen-espanso {root_q} --package-dir ./build/espanso_package"],
                ["clipboard-first text lane", "wtype when virtual-keyboard exists", "dotoold/dotoolc", "text-first deployment"],
            ),
            "pointer_injection": (
                "helper/uinput seam",
                ["portal:RemoteDesktop(pointer)", "dotoolc", "ydotool", "libei-ready helper"],
                ["dotool", "ydotool", "xdg-desktop-portal"],
                "On Wayland, pointer automation should stay behind a helper boundary so VHK can adapt to portal consent flows, compositor-native paths, or daemon-backed uinput helpers.",
                "This is the least portable surface in the Linux desktop stack today; do not design the whole product around it by accident.",
                ["vhk doctor --json", f"vhk validate {root_q} --json", f"vhk plan-project {root_q} --json"],
                ["dotoold/dotoolc", "ydotoold", "portal RemoteDesktop", "helper boundary"],
            ),
            "screen_capture": (
                "portal:ScreenCast",
                ["portal:ScreenCast", "portal:Screenshot", "grim/slurp"],
                ["xdg-desktop-portal", "grim", "slurp"],
                "Portal-first capture keeps the planning model honest across mixed Wayland desktops while still leaving room for wlroots-native tools when they exist.",
                "Portal routing and consent are desktop-shaped, so screenshot/capture advice must stay capability-aware.",
                ["vhk doctor --json", f"vhk preview-needle path/to/needle.png --project {root_q} --haystack path/to/screenshot.png --json --no-check"],
                ["xdg-desktop-portal", "grim/slurp", "capture consent flow"],
            ),
            "global_hotkeys": (
                "portal/compositor binds",
                ["portal:GlobalShortcuts", "compositor-native binds", "launcher/palette"],
                ["xdg-desktop-portal", "desktop/compositor config"],
                "Triggers on Wayland should be split between portal-aware global shortcuts, compositor-native binds, and launcher surfaces instead of assumed to be one generic backend feature.",
                "Global shortcut availability is still desktop/version dependent, so keep a launcher path available for conservative targets.",
                [f"vhk export-wm-bundle {root_q} ./build/wm_bundle --wm sway --kind binding --key Mod4+semicolon", f"vhk gen-desktop-entry {root_q} ./build/vhk.desktop"],
                ["portal GlobalShortcuts", "compositor-native binds", "launcher fallback"],
            ),
            "window_introspection": (
                "compositor metadata bridge",
                ["hyprctl", "swaymsg", "kdotool", "AT-SPI/Accerciser", "dogtail/pyatspi", "shell metadata bridge"],
                ["hyprland", "sway/i3 IPC", "kdotool", "accerciser", "dogtail"],
                "Window-aware Wayland projects should combine desktop-specific metadata bridges with an explicit AT-SPI lane when app/toolkit semantics matter more than container/focus metadata.",
                "Desktop metadata and accessibility trees are both conditional on the target session/app stack, so keep semantic selectors behind a contract and preserve vision fallbacks for poor or disabled trees.",
                ["vhk doctor --json", f"vhk window-spy --project {root_q} --json --no-check", f"vhk gen-session-fit-pack {root_q} --quiet"],
                ["hyprctl/swaymsg/kdotool", "AT-SPI/Accerciser", "dogtail structured UI automation"],
            ),
            "input_capture": (
                "portal:InputCapture",
                ["portal:InputCapture", "helper-boundary capture"],
                ["xdg-desktop-portal", "libei/EIS-ready stack"],
                "Keep input capture separate from normal macro playback so desktop/session-specific consent and backend limitations stay explicit.",
                "Input capture support remains uneven, so this should be a planned extension seam rather than an assumed base capability.",
                ["vhk doctor --json", f"vhk plan-project {root_q} --json"],
                ["portal InputCapture", "libei/EIS"],
            ),
        }
        return mapping[name]

    def _status_bonus(status: str) -> int:
        return {"ok": 16, "limited": 8, "missing": 2, "unknown": 6}.get(status, 6)

    def add(
        name: str,
        title: str,
        category: str,
        base_score: int,
    ) -> None:
        recommended, mechanisms, status = _preferred_from_matrix(name)
        default_recommended, fallbacks, package_hints, why, risks, commands, learn_from = _defaults(name)
        chosen = recommended or default_recommended
        all_fallbacks = _dedupe_keep_order([x for x in mechanisms if x != chosen] + fallbacks)
        package_hints = _dedupe_keep_order(package_hints + [chosen] + all_fallbacks[:3])
        score = max(0, min(100, int(base_score) + _status_bonus(status) + (12 if name in issue_caps else 0)))
        toolchains.append({
            "id": name.replace("_", "-"),
            "title": title,
            "category": category,
            "capability": name,
            "score": score,
            "fit": _fit_label(score),
            "status": status,
            "recommended_toolchain": chosen,
            "fallback_toolchains": all_fallbacks[:5],
            "package_hints": package_hints[:6],
            "why": why,
            "risks": risks,
            "commands": _dedupe_keep_order(commands),
            "evidence": _dedupe_keep_order([
                f"backend={backend or 'unknown'}",
                f"{len(capability_usage.get(name) or [])} use(s)",
                f"status={status}",
            ]),
            "learn_from": _dedupe_keep_order(learn_from),
        })

    if text_usage or text_macros or overview.get("hotstrings"):
        base = 30 + min(26, len(text_usage) * 9) + min(14, len(text_macros) * 6)
        if "text-expander-integration" in project_tags:
            base += 12
        add("text_injection", "Text injection toolchain", "input", base)

    if pointer_usage or vision_macros:
        base = 28 + min(30, len(pointer_usage) * 10) + min(18, len(vision_macros) * 7)
        if "selector-asset-heavy" in project_tags:
            base += 10
        add("pointer_injection", "Pointer injection toolchain", "input", base)

    if capture_usage or vision_macros:
        base = 28 + min(30, len(capture_usage) * 9) + min(18, len(vision_macros) * 7)
        if "selector-asset-heavy" in project_tags:
            base += 10
        add("screen_capture", "Screen capture toolchain", "capture", base)

    if hotkey_usage or overview.get("bindings"):
        base = 26 + min(26, len(hotkey_usage) * 10) + min(12, int(overview.get("bindings") or 0) * 6)
        if "wm-integrated" in project_tags:
            base += 10
        add("global_hotkeys", "Trigger / hotkey toolchain", "trigger", base)

    if window_usage or watcher_count:
        base = 24 + min(24, len(window_usage) * 8) + min(16, watcher_count * 4)
        if flow_macros:
            base += min(8, len(flow_macros) * 2)
        add("window_introspection", "Window/context toolchain", "context", base)

    if backend == "wayland" or "wayland-helper" in project_tags or "input_capture" in issue_caps:
        base = 18 + (8 if backend == "wayland" else 0) + (10 if "input_capture" in issue_caps else 0)
        add("input_capture", "Input-capture extension seam", "capture", base)

    toolchains = [item for item in toolchains if int(item.get("score") or 0) > 0]
    toolchains.sort(key=lambda item: (-int(item.get("score") or 0), str(item.get("category") or ""), str(item.get("title") or "")))
    return toolchains



def _capability_coverage(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
    capability_matrix: Mapping[str, Any] | None = None,
    capability_issues: list[dict[str, Any]] | None = None,
    environment_diffs: list[dict[str, Any]] | None = None,
    toolchain_choices: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Summarize how each capability travels across Linux targets.

    Earlier planning layers answer *which* environment or toolchain fits the
    project. This layer makes the portability story explicit for each
    capability: where it is broadly portable, where it becomes conditional, and
    which seams should absorb the risk.
    """

    capability_usage = capability_usage or {}
    capability_matrix = capability_matrix or {}
    capability_issues = list(capability_issues or [])
    environment_diffs = list(environment_diffs or [])
    toolchain_choices = list(toolchain_choices or [])

    backend = str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "").strip().lower()
    issue_caps = {str(item.get("capability") or "") for item in capability_issues if str(item.get("capability") or "")}
    toolchain_by_cap = {str(item.get("capability") or ""): item for item in toolchain_choices if str(item.get("capability") or "")}

    scenario_order = [
        ("portable-text", "Portable text"),
        ("x11-i3", "X11/i3"),
        ("gnome-wayland", "GNOME Wayland"),
        ("kde-wayland", "KDE Wayland"),
        ("wlroots-sway-conservative", "Sway/wlroots"),
        ("hyprland-conservative", "Hyprland"),
    ]

    env_map = {str(item.get("id") or ""): item for item in environment_diffs if str(item.get("id") or "")}

    def _scenario_rows(name: str) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for scenario_id, fallback_title in scenario_order:
            env_item = env_map.get(scenario_id)
            if env_item:
                title = str(env_item.get("title") or fallback_title)
                statuses = env_item.get("capability_statuses") or {}
                status = str(statuses.get(name) or "unknown")
            else:
                matrix, _, _, _ = _scenario_capability_matrix(scenario_id)
                title = fallback_title
                status = _capability_status(matrix, name)
            rows.append({"id": scenario_id, "title": title, "status": status})
        return rows

    def _status_rank(status: str) -> int:
        return {"missing": 0, "limited": 1, "unknown": 1, "ok": 2}.get(str(status or "unknown"), 1)

    def _dedupe_keep_order(values: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in values:
            val = str(item or "").strip()
            if not val or val in seen:
                continue
            seen.add(val)
            out.append(val)
        return out

    capability_meta: dict[str, dict[str, Any]] = {
        "screen_capture": {
            "title": "Screen capture coverage",
            "category": "capture",
            "offload": [
                "keep capture behind portal/compositor seams instead of baking a single desktop path into core",
                "pair vision-heavy flows with selector asset preview and retry tuning instead of more clicks",
            ],
        },
        "text_injection": {
            "title": "Text injection coverage",
            "category": "input",
            "offload": [
                "promote snippet/forms-heavy flows into Espanso-style or clipboard-first exports where practical",
                "treat pointer playback as a fallback for text, not the primary path",
            ],
        },
        "pointer_injection": {
            "title": "Pointer injection coverage",
            "category": "input",
            "offload": [
                "keep pointer-heavy flows behind helper/uinput seams or explicit portal consent boundaries",
                "replace brittle coordinate clicks with selectors, prompts, or exported text surfaces when possible",
            ],
        },
        "global_hotkeys": {
            "title": "Global hotkey coverage",
            "category": "trigger",
            "offload": [
                "route always-on triggers through WM/compositor binds, portal shortcuts, or launcher fallbacks",
                "keep the bind layer thin so macro logic stays in VHK core",
            ],
        },
        "window_introspection": {
            "title": "Window/context coverage",
            "category": "context",
            "offload": [
                "prefer WM/compositor metadata bridges over deep window scripting when moving off X11",
                "use app scoping and dispatch surfaces to reduce dependence on rich window APIs",
            ],
        },
        "input_capture": {
            "title": "Input-capture coverage",
            "category": "capture",
            "offload": [
                "treat input capture as a helper/remapper seam instead of a default runner feature",
                "prefer exported remap/trigger surfaces unless a project truly needs raw capture",
            ],
        },
    }

    items: list[dict[str, Any]] = []
    for name, meta in capability_meta.items():
        usage_refs = list(capability_usage.get(name) or [])
        scenario_rows = _scenario_rows(name)
        ok_envs = [row["title"] for row in scenario_rows if row["status"] == "ok"]
        limited_envs = [row["title"] for row in scenario_rows if row["status"] == "limited"]
        missing_envs = [row["title"] for row in scenario_rows if row["status"] == "missing"]
        portable_status = next((row["status"] for row in scenario_rows if row["id"] == "portable-text"), "unknown")
        x11_status = next((row["status"] for row in scenario_rows if row["id"] == "x11-i3"), "unknown")
        wayland_rows = [row for row in scenario_rows if row["id"] in {"gnome-wayland", "kde-wayland", "wlroots-sway-conservative", "hyprland-conservative"}]
        wayland_ok = sum(1 for row in wayland_rows if row["status"] == "ok")
        wayland_missing = sum(1 for row in wayland_rows if row["status"] == "missing")

        if portable_status == "ok" and not missing_envs:
            coverage_class = "portable"
        elif name == "pointer_injection" and x11_status == "ok" and (wayland_missing or limited_envs):
            coverage_class = "helper-boundary"
        elif name == "global_hotkeys" and portable_status != "ok" and (limited_envs or missing_envs):
            coverage_class = "desktop-boundary"
        elif name == "input_capture" and len(ok_envs) <= 1:
            coverage_class = "experimental"
        elif x11_status == "ok" and wayland_ok == 0:
            coverage_class = "x11-first"
        elif missing_envs or limited_envs:
            coverage_class = "conditional"
        else:
            coverage_class = "broad"

        current_status = _capability_status(capability_matrix, name) if capability_matrix else "unknown"
        if not capability_matrix:
            current_status = "unknown"

        use_count = len(usage_refs)
        macro_names = _dedupe_keep_order(str(item.get("macro") or "") for item in usage_refs if str(item.get("macro") or ""))
        sources = Counter(str(item.get("source") or "") for item in usage_refs if str(item.get("source") or ""))
        source_bits = [f"{src}:{count}" for src, count in sources.most_common(3)]

        avg_rank = round(sum(_status_rank(row["status"]) for row in scenario_rows) / max(1, len(scenario_rows)) * 50)
        score = max(0, min(100, int(avg_rank)))
        if current_status == "ok":
            score = min(100, score + 5)
        elif current_status == "missing" and use_count:
            score = max(0, score - 20)
        elif current_status == "limited" and use_count:
            score = max(0, score - 10)

        pressure = "high" if use_count >= 3 else "medium" if use_count >= 1 else "low"
        if name in issue_caps and pressure != "high":
            pressure = "medium"

        toolchain = toolchain_by_cap.get(name) or {}
        recommended_toolchain = str(toolchain.get("recommended_toolchain") or "")
        fallback_toolchains = [str(x) for x in (toolchain.get("fallback_toolchains") or []) if str(x)]
        commands = [str(x) for x in (toolchain.get("commands") or [])[:3] if str(x)]

        if coverage_class == "portable":
            advice = "This capability survives the conservative portable-text lane, so VHK can keep it in shared exports and core flows."
        elif coverage_class == "helper-boundary":
            advice = "Keep this behind a helper boundary and design macro logic so the feature can degrade to selectors, text, or prompts on conservative desktops."
        elif coverage_class == "desktop-boundary":
            advice = "Treat this as a desktop/compositor integration surface: export thin binds and keep launcher fallbacks available."
        elif coverage_class == "experimental":
            advice = "Treat this as an opt-in capability with explicit validation rather than a baseline dependency for the project."
        elif coverage_class == "x11-first":
            advice = "This still behaves like an X11-first capability. Plan for replacement surfaces before claiming broad Linux portability."
        else:
            advice = "This capability is viable, but its shipping story should remain capability-aware across desktop families."

        evidence = [
            f"uses={use_count}",
            f"backend={backend or 'unknown'}",
            f"current={current_status}",
            f"ok={len(ok_envs)} limited={len(limited_envs)} missing={len(missing_envs)}",
            *source_bits,
        ]
        if name in issue_caps:
            evidence.append("session mismatch detected")

        items.append({
            "id": name.replace("_", "-"),
            "title": str(meta.get("title") or name),
            "category": str(meta.get("category") or "general"),
            "capability": name,
            "coverage_score": score,
            "coverage_class": coverage_class,
            "project_pressure": pressure,
            "usage_count": use_count,
            "used_by": macro_names,
            "current_status": current_status,
            "recommended_toolchain": recommended_toolchain,
            "fallback_toolchains": fallback_toolchains,
            "best_environments": ok_envs[:4],
            "limited_environments": limited_envs[:4],
            "blocking_environments": missing_envs[:4],
            "scenario_statuses": scenario_rows,
            "offload_paths": list(meta.get("offload") or []),
            "advice": advice,
            "commands": commands,
            "evidence": evidence[:6],
        })

    items.sort(key=lambda item: (-int(item.get("usage_count") or 0), -int(item.get("coverage_score") or 0), str(item.get("title") or "")))
    return items



def _reference_patterns(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    macro_profiles: list[dict[str, Any]],
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
    capability_matrix: Mapping[str, Any] | None = None,
    capability_issues: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Summarize which external product patterns VHK should borrow from.

    This turns the repo's research notes into a machine-readable planning layer.
    Instead of saying "learn from Espanso" only in prose, the planner scores
    which product patterns match the current project shape and what to borrow or
    avoid from each.
    """

    capability_usage = capability_usage or {}
    capability_issues = list(capability_issues or [])
    backend = str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "").strip().lower()
    root_dir = getattr(project, "root_dir", None) or "."
    root_q = shlex.quote(str(root_dir))
    modal_wm = backend if backend in {"i3", "sway", "hyprland"} else ("i3" if backend == "x11" else "")

    vision_macros = [m for m in macro_profiles if "vision-heavy" in (m.get("tags") or [])]
    text_macros = [m for m in macro_profiles if "text-expander" in (m.get("tags") or [])]
    parameterized_macros = [m for m in macro_profiles if "parameterized" in (m.get("tags") or [])]
    prompt_macros = [
        m
        for m in macro_profiles
        if int(((m.get("feature_counts") or {}).get("prompt") or 0)) > 0 or int(m.get("preset_count") or 0) > 0
    ]
    event_macros = [m for m in macro_profiles if "event-driven" in (m.get("tags") or [])]
    flow_macros = [m for m in macro_profiles if "flow-heavy" in (m.get("tags") or [])]
    data_or_orch = [
        m
        for m in macro_profiles
        if "orchestrator" in (m.get("tags") or []) or "data-glue" in (m.get("tags") or [])
    ]

    raw_key_events = sum(int((m.get("smells") or {}).get("raw_key_events") or 0) for m in macro_profiles)
    coord_clicks = sum(int((m.get("smells") or {}).get("coord_click") or 0) for m in macro_profiles)
    long_delays = sum(int((m.get("smells") or {}).get("long_delay") or 0) for m in macro_profiles)

    hotstrings = int(overview.get("hotstrings") or 0)
    bindings = int(overview.get("bindings") or 0)
    watchers = int(overview.get("clipboard_watchers") or 0) + int(overview.get("file_watchers") or 0) + int(overview.get("bus_watchers") or 0) + int(overview.get("window_watchers") or 0)
    presets = int(overview.get("presets") or 0)

    pointer_usage = list(capability_usage.get("pointer_injection") or [])
    text_usage = list(capability_usage.get("text_injection") or [])
    capture_usage = list(capability_usage.get("screen_capture") or [])
    hotkey_usage = list(capability_usage.get("global_hotkeys") or [])
    window_usage = list(capability_usage.get("window_introspection") or [])
    capability_blockers = {str(item.get("capability") or "") for item in capability_issues if str(item.get("capability") or "")}
    portal_catalog = _portal_shortcut_catalog_analysis(
        project=project,
        macro_profiles=macro_profiles,
        capability_usage=capability_usage,
    )
    stable_portal_bindings = int(portal_catalog.get("stable_binding_count") or 0)
    dynamic_portal_bindings = int(portal_catalog.get("dynamic_binding_count") or 0)
    app_protocols = _app_protocol_target_analysis(project=project)
    app_protocol_target_count = int(app_protocols.get("target_count") or 0)
    app_protocol_learn_from = [str(x) for x in (app_protocols.get("learn_from") or []) if str(x)]
    app_protocol_target_ids = [str(x) for x in (app_protocols.get("target_ids") or []) if str(x)]
    app_protocol_commands = _app_protocol_pack_commands(root_q, app_protocol_target_ids)
    voice_adapters = _voice_adapter_analysis(project=project)
    voice_entry_count = int(voice_adapters.get("entry_count") or 0)
    voice_phrase_count = int(voice_adapters.get("explicit_phrase_count") or 0)
    voice_scoped_entry_count = int(voice_adapters.get("scoped_entry_count") or 0)
    mpris_services = _mpris_service_analysis(project=project)
    mpris_signal_count = int(mpris_services.get("signal_count") or 0)
    mpris_players = [str(x) for x in (mpris_services.get("players") or []) if str(x)]
    mpris_members = [str(x) for x in (mpris_services.get("members") or []) if str(x)]
    notification_feedback = _notification_feedback_analysis(project=project)
    notification_entry_count = int(notification_feedback.get("entry_count") or 0)
    notification_signal_count = int(notification_feedback.get("signal_count") or 0)
    notification_notify_count = int(notification_feedback.get("notify_count") or 0)
    notification_show_message_count = int(notification_feedback.get("show_message_count") or 0)
    notification_replaceable_count = int(notification_feedback.get("replaceable_count") or 0)
    notification_timed_count = int(notification_feedback.get("timed_count") or 0)
    notification_transient_count = int(notification_feedback.get("transient_count") or 0)
    notification_members = [str(x) for x in (notification_feedback.get("members") or []) if str(x)]
    notification_urgencies = [str(x) for x in (notification_feedback.get("urgencies") or []) if str(x)]

    patterns: list[dict[str, Any]] = []

    def _dedupe_keep_order(values: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in values:
            val = str(item or "").strip()
            if not val or val in seen:
                continue
            seen.add(val)
            out.append(val)
        return out

    def add(
        id: str,
        title: str,
        pattern_type: str,
        score: int,
        summary: str,
        *,
        borrow: list[str] | None = None,
        avoid: list[str] | None = None,
        evidence: list[str] | None = None,
        commands: list[str] | None = None,
        learn_from: list[str] | None = None,
    ) -> None:
        score = max(0, min(int(score), 100))
        patterns.append({
            "id": id,
            "title": title,
            "pattern_type": pattern_type,
            "score": score,
            "fit": _fit_label(score),
            "summary": summary,
            "borrow": list(borrow or []),
            "avoid": list(avoid or []),
            "evidence": _dedupe_keep_order(evidence or []),
            "commands": _dedupe_keep_order(commands or []),
            "learn_from": _dedupe_keep_order(learn_from or []),
        })

    ahk_score = 28 + min(28, len(macro_profiles) * 7) + min(20, len(flow_macros) * 8) + min(18, len(data_or_orch) * 9)
    if vision_macros:
        ahk_score += min(12, len(vision_macros) * 4)
    if text_macros:
        ahk_score += min(10, len(text_macros) * 3)
    add(
        "ahk-runner-core",
        "AutoHotkey-style runner core",
        "runtime",
        ahk_score,
        "Keep the VHK runner expressive and fast when a project mixes flow control, data/process glue, prompts, and direct automation steps.",
        borrow=[
            "preserve a rich step vocabulary, variables, and control flow in the runner core",
            "treat hotkeys, hotstrings, prompts, and process glue as one automation language rather than separate mini-tools",
            "optimize the run/trace/report loop so macro authors can keep logic centralized without losing performance",
        ],
        avoid=[
            "do not assume Windows-only window models or shell integration semantics",
            "do not force Linux users into one always-on privileged daemon when thin dispatch or exports fit better",
        ],
        evidence=[
            f"{len(macro_profiles)} macro(s)",
            f"{len(flow_macros)} flow-heavy macro(s)",
            f"{len(data_or_orch)} orchestrator/data macro(s)",
        ],
        commands=[
            f"vhk plan-project {root_q} --json",
            f"vhk optimize-project {root_q} --profile balanced",
            f"vhk validate {root_q} --json",
        ],
        learn_from=["AutoHotkey"],
    )

    pulover_score = len(vision_macros) * 24 + presets * 6 + len(parameterized_macros) * 7 + len(capture_usage) * 8
    if coord_clicks:
        pulover_score += 8
    if long_delays:
        pulover_score += 6
    add(
        "pulover-visual-studio",
        "Pulover-style visual studio",
        "studio",
        pulover_score,
        "Lean into recorder cleanup, prompt-aware presets, selector previews, and asset organization when the project starts to look like a macro studio instead of a few scripts.",
        borrow=[
            "keep recording, selector cleanup, and preview tooling close to the authoring flow",
            "treat presets and prompt overlays as first-class visual-macro affordances",
            "organize needles, OCR boxes, and regions like named project assets instead of loose screenshots",
        ],
        avoid=[
            "do not let coordinate clicks and fixed delays become the default recording output",
            "do not make the studio dependent on one desktop backend before the runtime contracts are stable",
        ],
        evidence=[
            f"{len(vision_macros)} vision-heavy macro(s)",
            f"{presets} preset(s)",
            f"{coord_clicks} coordinate click smell(s)",
        ],
        commands=[
            f"vhk record-selectors {root_q} --duration-ms 3000",
            f"vhk preview-needle path/to/needle.png --project {root_q} --haystack path/to/screenshot.png --json --no-check",
            "vhk trace ./eventlog.json",
        ],
        learn_from=["Pulover's Macro Creator", "SikuliX"],
    )

    espanso_score = hotstrings * 34 + len(text_macros) * 16 + len(parameterized_macros) * 8
    if "text-expander-integration" in project_tags:
        espanso_score += 12
    add(
        "espanso-forms-text-tier",
        "Espanso-style text/forms tier",
        "text",
        espanso_score,
        "Offload repetitive text expansion and forms-shaped workflows into an exported package when the project has hotstrings, prompted snippets, or strong text-only paths.",
        borrow=[
            "treat forms, variables, and app-specific scoping as first-class text automation surfaces",
            "generate packageable text exports rather than forcing every snippet through the full runner",
            "keep script handoff optional so text flows stay fast and easy to ship",
        ],
        avoid=[
            "do not bury simple snippet workflows inside heavy visual or pointer automation stacks",
            "do not require users to understand the whole project graph to deploy a text-only subset",
        ],
        evidence=[
            f"{hotstrings} hotstring(s)",
            f"{len(text_macros)} text-expander macro(s)",
            f"{len(parameterized_macros)} parameterized macro(s)",
        ],
        commands=[
            f"vhk gen-espanso {root_q} --package-dir ./build/espanso_package",
            f"vhk lint-project {root_q}",
            f"vhk validate {root_q}",
        ],
        learn_from=["Espanso"],
    )

    if backend == "wayland" and (hotstrings or text_macros):
        wtype_score = hotstrings * 18 + len(text_macros) * 16 + len(parameterized_macros) * 6
        add(
            "wtype-narrow-wayland-text-lane",
            "wtype-style narrow Wayland text lane",
            "adapter",
            wtype_score,
            "Keep fast typed-text playback on a narrow, explicit Wayland lane when the target compositor proves virtual-keyboard support, while preserving package/clipboard fallbacks as the portable default.",
            borrow=[
                "treat compositor-backed virtual-keyboard typing as a narrow fast path instead of the whole Wayland text story",
                "keep text-package and clipboard routes first-class so snippet workflows still ship on desktops without that protocol path",
                "surface the exact helper/protocol assumption during planning instead of discovering it only after deployment",
            ],
            avoid=[
                "do not treat wtype as a generic Wayland promise across GNOME, KDE, wlroots, and future desktops",
                "do not force all text automation through uinput helpers when a simpler package/clipboard route fits the product better",
            ],
            evidence=[
                f"desktop backend={backend}",
                f"{hotstrings} hotstring(s)",
                f"{len(text_macros)} text-expander macro(s)",
            ],
            commands=[
                f"vhk validate {root_q} --json",
                f"vhk gen-espanso {root_q} --package-dir ./build/espanso_package",
            ],
            learn_from=["wtype"],
        )

    if backend == "wayland" and (pointer_usage or text_usage):
        helper_daemon_score = len(pointer_usage) * 16 + len(text_usage) * 10 + len(capture_usage) * 6
        if capability_blockers:
            helper_daemon_score += min(20, len(capability_blockers) * 6)
        add(
            "daemonized-uinput-helper-lane",
            "Daemonized uinput helper lane",
            "adapter",
            helper_daemon_score,
            "Keep helper-backed playback honest by planning around a reviewed daemon/socket lane when Wayland automation needs repeated text or pointer injection.",
            borrow=[
                "treat daemon startup, socket ownership, and uinput rules as first-class deployment artifacts",
                "prefer long-lived helper devices for repeated playback instead of paying setup cost at every macro edge",
                "keep the daemon outside the runner core so helper choice remains swappable",
            ],
            avoid=[
                "do not hide helper service lifecycle behind a generic 'Wayland support' claim",
                "do not make one-shot helper binaries the default answer for repeated automation without reviewing their registration overhead and permissions",
            ],
            evidence=[
                f"desktop backend={backend}",
                f"pointer usage={len(pointer_usage)}",
                f"text usage={len(text_usage)}",
                f"capability blockers={len(capability_blockers)}",
            ],
            commands=[
                "vhk doctor --json",
                "vhk gen-dotoold-service --out-dir ./build/systemd-user",
                "vhk gen-ydotoold-service --out-dir ./build/systemd-user",
                "vhk gen-udev-uinput --out-dir ./build/udev",
            ],
            learn_from=["dotool", "ydotool"],
        )

    if backend in {"x11", "i3"} and (hotstrings or bindings or text_macros):
        autokey_score = hotstrings * 26 + bindings * 14 + len(text_macros) * 16 + len(parameterized_macros) * 6
        if backend == "x11":
            autokey_score += 12
        add(
            "autokey-reviewable-adapter",
            "AutoKey-style reviewable X11 adapter",
            "adapter",
            autokey_score,
            "Export an explicit adapter pack when an X11-first project wants familiar Linux trigger/text surfaces without hiding the execution path inside AutoKey itself.",
            borrow=[
                "keep script bodies and trigger metadata reviewable as exported artifacts instead of burying them in one opaque runtime",
                "treat a Linux automation shell as an adapter lane that can hand off into VHK, not as the only place macro semantics live",
                "surface X11-only assumptions and selector-loss warnings before export so operator review stays honest",
            ],
            avoid=[
                "do not position AutoKey as a generic Wayland backend or a universal Linux support claim",
                "do not silently flatten VHK selector intersections into AutoKey's coarser title-or-class filter",
            ],
            evidence=[
                f"desktop backend={backend}",
                f"{hotstrings} hotstring(s)",
                f"{bindings} binding(s)",
            ],
            commands=[
                f"vhk gen-autokey-pack {root_q} --out-dir ./build/autokey_pack",
                f"vhk lint-project {root_q}",
                f"vhk validate {root_q}",
            ],
            learn_from=["AutoKey"],
        )

    accessibility_pattern_score = len(window_usage) * 18 + len(flow_macros) * 10 + watchers * 4 + (8 if backend == "wayland" else 4)
    if window_usage or flow_macros:
        add(
            "atspi-structured-selector-lane",
            "AT-SPI structured selector lane",
            "context",
            accessibility_pattern_score,
            "Model structured Linux UI targeting as its own lane: inspect the accessibility tree, prefer semantic widget actions when available, and keep explicit fallbacks when the tree is missing or shallow.",
            borrow=[
                "treat accessibility as a separate contract with bus health and per-app coverage checks instead of folding it into vague window support",
                "keep inspector-style exploration and event observation close to selector authoring so semantic targets stay reviewable",
                "prefer semantic actions and text roles when applications expose them, then fall back to desktop metadata and vision only where necessary",
            ],
            avoid=[
                "do not assume every Linux app or toolkit exposes a rich enough accessibility tree for automation",
                "do not let a disabled accessibility bus silently collapse structured selectors into flaky coordinate playback",
            ],
            evidence=[
                f"backend={backend or 'unknown'}",
                f"window_usage={len(window_usage)}",
                f"flow_macros={len(flow_macros)}",
                f"window_watchers={int(overview.get('window_watchers') or 0)}",
            ],
            commands=[
                "vhk doctor --json",
                f"vhk window-spy --project {root_q} --json --no-check",
                f"vhk gen-capability-audit-pack {root_q} --quiet",
            ],
            learn_from=["AT-SPI", "Accerciser", "dogtail"],
        )

    app_protocol_pattern_score = app_protocol_target_count * 24 + len(window_usage) * 10 + len(text_usage) * 8 + len(pointer_usage) * 10
    if backend == "wayland":
        app_protocol_pattern_score += 8
    if app_protocol_target_count:
        add(
            "app-native-protocol-lane",
            "App-native protocol lane",
            "adapter",
            app_protocol_pattern_score,
            "Route app-specific automation through the target program's own control contract whenever a known terminal, media, or browser target already exposes one.",
            borrow=[
                "prefer semantic app protocols over generic key/pointer replay when the target app already ships a remote-control, CLI, IPC, or userscript surface",
                "keep window/app selectors reviewable so adapter routing is tied to explicit target windows rather than folklore about the current desktop state",
                "treat app adapters as thin bridges that wake VHK or exchange structured state, not as a second hidden macro runtime",
            ],
            avoid=[
                "do not market app-specific protocols as generic Linux automation support",
                "do not keep replaying text or media controls blindly into apps that already expose better contracts",
            ],
            evidence=[
                f"backend={backend or 'auto'}",
                f"app_protocol_targets={','.join(app_protocol_target_ids)}",
                f"window_usage={len(window_usage)}",
                f"text_usage={len(text_usage)}",
                f"pointer_usage={len(pointer_usage)}",
            ],
            commands=app_protocol_commands,
            learn_from=app_protocol_learn_from,
        )

    voice_pattern_score = voice_entry_count * 24 + voice_phrase_count * 8 + voice_scoped_entry_count * 14
    if voice_entry_count:
        add(
            "voice-context-command-lane",
            "Voice adapter context lane",
            "adapter",
            voice_pattern_score,
            "Treat voice as a reviewable adapter lane: export literal spoken phrases plus app/title contexts into Talon/Dragonfly while keeping macro semantics, prompts, and diagnostics inside VHK.",
            borrow=[
                "keep one stable VHK action catalog and let voice tools call back into those command ids instead of re-encoding the macro graph in another speech runtime",
                "preserve app/title context boundaries in exported voice packs so spoken commands stay honest about where they activate",
                "use diffable ledgers and pack outputs so phrase churn, collisions, and context drift are reviewed like any other deployment artifact",
            ],
            avoid=[
                "do not turn VHK itself into a speech recognizer or hide engine-specific context limits behind a generic voice checkbox",
                "do not let spoken phrases become the only source of truth for macro names, prompt behavior, or runtime diagnostics",
            ],
            evidence=[
                f"voice commands={voice_entry_count}",
                f"voice phrases={voice_phrase_count}",
                f"voice contexts={voice_scoped_entry_count}",
                f"backend={backend or 'auto'}",
            ],
            commands=[
                f"vhk gen-dragonfly-pack {root_q} --out-dir ./build/dragonfly_pack",
                f"vhk gen-talon-pack {root_q} --out-dir ./build/talon_pack",
                f"vhk lint-project {root_q}",
            ],
            learn_from=["Talon contexts", "Dragonfly grammars", "voice command ledgers"],
        )

    mpris_pattern_score = mpris_signal_count * 40 + len(event_macros) * 8 + len(flow_macros) * 6
    if mpris_signal_count:
        add(
            "mpris-follow-control-lane",
            "MPRIS follow/control lane",
            "adapter",
            mpris_pattern_score,
            "Treat media-player automation as a standard bus contract when the project is already waiting on MPRIS signals or player-state changes.",
            borrow=[
                "prefer session-bus properties/signals and thin playerctl-style adapters over polling titles or replaying generic media keys",
                "keep the latest-player policy in a thin adapter layer so VHK still owns macro semantics while the bus tool owns target discovery",
                "treat metadata/status follow streams as orchestration input, not as ad-hoc shell text to parse everywhere",
            ],
            avoid=[
                "do not assume every media app or host publishes the same MPRIS objects without checking availability",
                "do not keep media state tied to focused-window guesses when the session bus already exposes a better contract",
            ],
            evidence=[
                f"mpris_signals={mpris_signal_count}",
                f"mpris_players={','.join(mpris_players) if mpris_players else 'unknown'}",
                f"mpris_members={','.join(mpris_members) if mpris_members else 'unknown'}",
                f"backend={backend or 'auto'}",
            ],
            commands=[
                "vhk doctor --json",
                f"vhk gen-playerctl-pack {root_q} --out-dir ./build/playerctl_pack",
                f"vhk gen-session-fit-pack {root_q} --quiet",
                f"vhk gen-design-pack {root_q} --quiet",
                f"vhk lint-project {root_q}",
            ],
            learn_from=["MPRIS", "playerctl --follow", "playerctld"],
        )

    notification_pattern_score = notification_notify_count * 20 + notification_signal_count * 26 + notification_show_message_count * 6 + len(event_macros) * 6 + len(flow_macros) * 4
    if notification_notify_count or notification_signal_count:
        add(
            "notification-daemon-feedback-lane",
            "Notification daemon feedback lane",
            "feedback",
            notification_pattern_score,
            "Treat passive status and notification-driven follow-up as a session-service lane when the project already emits desktop notifications or waits on notification-daemon signals.",
            borrow=[
                "keep passive alerts, progress, and lightweight operator feedback in a replaceable session-notification surface instead of inventing bespoke always-on UI",
                "treat notification actions and close events as thin daemon-owned signals while VHK keeps the real macro semantics and diagnostics",
                "separate passive notification feedback from blocking prompts so chooser/forms work and status toasts do not get conflated",
            ],
            avoid=[
                "do not assume every notification daemon supports the same action, history, or replacement semantics without checking capabilities",
                "do not confuse portal notifications with a generic round-trip signal channel, because sandboxed send/withdraw flows are intentionally narrower",
            ],
            evidence=[
                f"notification_entries={notification_entry_count}",
                f"notify_steps={notification_notify_count}",
                f"show_messages={notification_show_message_count}",
                f"notification_signals={notification_signal_count}",
                f"replaceable_notifications={notification_replaceable_count}",
                f"timed_notifications={notification_timed_count}",
                f"transient_notifications={notification_transient_count}",
                f"notification_members={','.join(notification_members) if notification_members else 'none'}",
                f"notify_urgencies={','.join(notification_urgencies) if notification_urgencies else 'normal'}",
                f"backend={backend or 'auto'}",
            ],
            commands=[
                "vhk doctor --json",
                f"vhk gen-design-pack {root_q} --quiet",
                f"vhk gen-setup-pack {root_q} --quiet",
                f"vhk lint-project {root_q}",
            ],
            learn_from=["org.freedesktop.Notifications", "dunstify", "XDG Notification portal"],
        )

    dispatch_score = bindings * 30 + watchers * 12
    if "wm-integrated" in project_tags:
        dispatch_score += 15
    if event_macros:
        dispatch_score += min(12, len(event_macros) * 4)
    add(
        "wm-bind-dispatch",
        "WM/compositor dispatch shell",
        "dispatch",
        dispatch_score,
        "Keep the always-on trigger layer thin by exporting launcher helpers and WM/compositor bindings while the runner owns macro logic and diagnostics.",
        borrow=[
            "treat keybindings and launcher rows as a dispatch plane, not the whole automation runtime",
            "prefer native WM/compositor integration for low-latency triggers and mode switching",
            "bundle helpers, snippets, and desktop entries so deployment is explicit and reversible",
        ],
        avoid=[
            "do not overload the bind layer with complex sequencing, state, or selector logic",
            "do not assume every desktop can offer one generic global-hotkey story",
        ],
        evidence=[
            f"{bindings} binding(s)",
            f"{watchers} watcher(s)",
            f"{len(event_macros)} event-driven macro(s)",
        ],
        commands=[
            f"vhk export-wm-bundle {root_q} ./build/wm_bundle --wm i3 --kind binding --key Mod4+semicolon",
            f"vhk gen-sxhkd-config {root_q} --out ./build/vhk.sxhkdrc",
            f"vhk gen-desktop-entry {root_q} ./build/vhk.desktop",
        ],
        learn_from=["i3/sway binds", "sxhkd", "launcher modes"],
    )

    modal_pattern_score = bindings * 24 + int(overview.get("macros") or 0) * 8 + dynamic_portal_bindings * 10
    if backend in {"x11", "i3", "sway", "hyprland"}:
        modal_pattern_score += 18
    if modal_wm and (bindings >= 3 or int(overview.get("macros") or 0) >= 5):
        add(
            "wm-modal-submap-lane",
            "WM modal/submap trigger lane",
            "trigger",
            modal_pattern_score,
            "Use WM-native modes/submaps when the project has enough related hotkeys that one reviewed entry chord is healthier than minting more always-on globals.",
            borrow=[
                "group related actions behind one explicit mode/submap entry chord and keep the bind layer thin",
                "always provide a reset/escape path and prefer one-shot exits for destructive or high-frequency actions",
                "keep launcher and palette fallbacks aligned with the same action ids so discoverability survives outside the mode layer",
            ],
            avoid=[
                "do not treat WM-specific modes as a universal desktop trigger story",
                "do not bury macro logic inside the bind layer just because grouped triggers feel convenient",
            ],
            evidence=[
                f"desktop backend={backend}",
                f"{bindings} binding(s)",
                f"{int(overview.get('macros') or 0)} macro(s)",
                f"dynamic_shortcut_candidates={dynamic_portal_bindings}",
            ],
            commands=[
                f"vhk gen-wm-config {root_q} --wm {modal_wm} --mode-enter Mod4+R --mode-name vhk",
                f"vhk export-wm-bundle {root_q} ./build/wm_bundle --wm {modal_wm} --kind launcher-mode --mode-enter Mod4+R",
                f"vhk gen-trigger-pack {root_q} --quiet",
            ],
            learn_from=["i3 binding modes", "Hyprland submaps", "sxhkd chord chains"],
        )

    launcher_hub_score = bindings * 8 + presets * 12 + int(overview.get("macros") or 0) * 7 + (10 if "parameterized" in project_tags else 0)
    if int(overview.get("macros") or 0) >= 4 or presets >= 2 or ("parameterized" in project_tags and int(overview.get("macros") or 0) >= 2):
        add(
            "launcher-hub-catalog",
            "Launcher / marking-menu hub",
            "launchers",
            launcher_hub_score,
            "Treat growing macro catalogs as a discoverable launcher surface rather than an ever-expanding hotkey matrix.",
            borrow=[
                "preserve stable action ids so launcher rows, modes, and menu surfaces can point at the same macro catalog",
                "treat launcher hubs as a usability layer for many macros, presets, and prompt-rich flows",
                "reuse exported WM launcher snippets instead of inventing one-off menu glue per desktop",
            ],
            avoid=[
                "do not turn launcher hubs into a hidden second macro engine",
                "do not confuse discoverable launch surfaces with low-latency remap ownership",
            ],
            evidence=[
                f"{int(overview.get('macros') or 0)} macro(s)",
                f"{presets} preset(s)",
                f"{bindings} binding(s)",
            ],
            commands=[
                f"vhk export-rofi-mode {root_q} ./build/vhk.rofi.sh",
                f"vhk export-wm-launcher-mode {root_q} ./build/vhk.launcher --wm sway",
                f"vhk export-wm-bundle {root_q} ./build/wm_bundle --wm hyprland --kind launcher-mode --key SUPER,semicolon",
            ],
            learn_from=["Kando", "Fly-Pie", "launcher-mode UX"],
        )
    if prompt_macros or presets:
        picker_pattern_score = len(prompt_macros) * 18 + presets * 12 + (10 if "parameterized" in project_tags else 0) + (6 if backend == "wayland" else 3)
        add(
            "script-mode-picker-lane",
            "Script-mode picker lane",
            "launchers",
            picker_pattern_score,
            "Route chooser-style and preset-rich workflows through one reviewable script-mode launcher surface so Linux pickers stay thin while VHK keeps the real macro semantics and action catalog.",
            borrow=[
                "preserve one stable palette entry id catalog so rofi modes, launcher scripts, and chooser flows all resolve the same actions",
                "treat chooser UIs as thin stdin/stdout or script-mode shells that wake VHK rather than as a second macro runtime",
                "keep prompt-profile actions, icons, and hidden search metadata aligned so picker integrations remain reviewable and portable",
            ],
            avoid=[
                "do not build a bespoke picker UI for every desktop when launcher-native protocols already cover chooser-style workflows",
                "do not force prompt-heavy launch flows through always-on global hotkeys when searchable picker entry points are the healthier Linux-native lane",
            ],
            evidence=[
                f"prompt_macros={len(prompt_macros)}",
                f"{presets} preset(s)",
                f"backend={backend or 'auto'}",
            ],
            commands=[
                f"vhk export-launcher-script {root_q}",
                f"vhk export-rofi-mode {root_q} ./build/vhk.rofi.sh",
                f"vhk gen-desktop-entry {root_q} ./build/vhk.desktop",
            ],
            learn_from=["rofi script mode", "fuzzel --dmenu", "wofi --show dmenu"],
        )
    if backend == "wayland" and bindings:
        portal_catalog_score = bindings * 14 + stable_portal_bindings * 18 - dynamic_portal_bindings * 8
        add(
            "portal-session-catalog-lane",
            "Portal shortcut action catalog",
            "trigger",
            portal_catalog_score,
            "Keep portal-managed shortcuts focused on a reviewed, predeclared action catalog while routing hotter or helper-sensitive flows through compositor or launcher fallbacks.",
            borrow=[
                "pre-register stable shortcut ids and keep them reviewable as a named action catalog",
                "treat portal bind/configure work as install-time trigger ownership, not a hidden runtime detail",
                "use launcher or compositor-native fallbacks for dynamic, recorder-driven, or helper-sensitive hotkeys",
            ],
            avoid=[
                "do not present portal sessions as the best fit for endlessly changing macro inventories",
                "do not force helper-sensitive or remapper-style bindings through the same catalog path just because the session is Wayland",
            ],
            evidence=[
                f"stable_shortcut_candidates={stable_portal_bindings}",
                f"dynamic_shortcut_candidates={dynamic_portal_bindings}",
                f"{bindings} binding(s)",
            ],
            commands=[
                f"vhk gen-portal-shortcuts-spec {root_q} --out ./build/vhk.portal-shortcuts.yml",
                f"vhk portal-hotkeys {root_q} --bind --listen",
                f"vhk gen-activation-pack {root_q} --quiet",
            ],
            learn_from=["XDG GlobalShortcuts portal", "Kando"],
        )

    remap_score = raw_key_events * 20 + len(hotkey_usage) * 8 + bindings * 6
    if "remap-export" in project_tags:
        remap_score += 15
    add(
        "remap-daemon-offload",
        "Remap-daemon offload",
        "remap",
        remap_score,
        "Use low-latency remapper layers for chords, tap-hold behavior, and always-on key semantics while keeping VHK focused on macro orchestration and exports.",
        borrow=[
            "move leader keys, tap-hold, layers, and raw key timing into purpose-built remapper configs",
            "let VHK generate or complement remapper artifacts instead of re-implementing low-level key state everywhere",
            "keep macro invocation paths explicit so remaps can hand off cleanly into VHK",
        ],
        avoid=[
            "do not stuff rich UI automation or selector logic into remapper configs",
            "do not require raw key injection for projects that are really text/package or launcher shaped",
        ],
        evidence=[
            f"{raw_key_events} raw key event smell(s)",
            f"{bindings} binding(s)",
            f"{len(hotkey_usage)} hotkey capability use(s)",
        ],
        commands=[
            f"vhk gen-keyd-config {root_q} --out ./build/vhk.keyd.conf",
            f"vhk gen-kanata-config {root_q} --out ./build/vhk.kanata.kbd",
            f"vhk gen-kmonad-config {root_q} --out ./build/vhk.kmonad.kbd",
        ],
        learn_from=["keyd", "Kanata", "KMonad", "xremap"],
    )

    helper_score = 0
    if backend == "wayland":
        helper_score += 25
    helper_score += len(pointer_usage) * 12 + len(capture_usage) * 8
    if capability_blockers:
        helper_score += min(30, len(capability_blockers) * 10)
    if "wayland-helper" in project_tags:
        helper_score += 15
    add(
        "portal-helper-boundary",
        "Portal/helper-boundary integration",
        "capability",
        helper_score,
        "Model Wayland-class features as a capability boundary: portal sessions, compositor metadata, helper tools, and exported trigger surfaces should be explicit seams instead of hidden assumptions.",
        borrow=[
            "treat screen capture, global shortcuts, and input injection as separate capabilities that may need different helpers",
            "keep session checks, validation, and deployment advice close to project planning",
            "prefer clear helper boundaries over optimistic backend claims when pointer or capture support is uneven",
        ],
        avoid=[
            "do not market one backend as uniform Wayland support when portal/compositor coverage varies",
            "do not make core macro logic depend on a helper that only exists on one desktop family",
        ],
        evidence=[
            f"desktop backend={backend or 'unknown'}",
            f"{len(pointer_usage)} pointer capability use(s)",
            f"{len(capability_blockers)} capability mismatch(es)",
        ],
        commands=[
            "vhk doctor --json",
            f"vhk validate {root_q} --json",
            f"vhk plan-project {root_q} --json",
        ],
        learn_from=["xdg-desktop-portal", "libei/EIS", "compositor-native helpers"],
    )

    patterns = [item for item in patterns if int(item.get("score") or 0) > 0]
    patterns.sort(key=lambda item: (-int(item.get("score") or 0), str(item.get("title") or "")))
    return patterns



def _verification_gates(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    capability_coverage: list[dict[str, Any]] | None = None,
    toolchain_choices: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Turn capability planning into concrete shipping gates.

    The planner already explains which Linux surfaces and desktops fit a
    project. This layer answers a more release-shaped question: what should a
    team verify before claiming a capability is ready to ship?

    The result is intentionally per-capability instead of per-environment so it
    can be re-used by future scaffold, CI, and studio flows.
    """

    capability_coverage = list(capability_coverage or [])
    toolchain_choices = list(toolchain_choices or [])

    backend = str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "").strip().lower()
    root_dir = getattr(project, "root_dir", None) or "."
    root_q = shlex.quote(str(root_dir))

    hotstrings = int(overview.get("hotstrings") or 0)
    bindings = int(overview.get("bindings") or 0)
    watchers = int(overview.get("clipboard_watchers") or 0) + int(overview.get("file_watchers") or 0) + int(overview.get("bus_watchers") or 0) + int(overview.get("window_watchers") or 0)

    toolchain_by_cap = {
        str(item.get("capability") or ""): item
        for item in toolchain_choices
        if str(item.get("capability") or "")
    }

    def _dedupe_keep_order(values: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in values:
            val = str(item or "").strip()
            if not val or val in seen:
                continue
            seen.add(val)
            out.append(val)
        return out

    def _priority(*, pressure: str, current_status: str, coverage_class: str, use_count: int) -> str:
        if pressure == "high":
            return "high"
        if use_count and current_status in {"missing", "limited"}:
            return "high"
        if use_count and coverage_class in {"helper-boundary", "desktop-boundary", "experimental", "x11-first"}:
            return "high"
        if use_count:
            return "medium"
        return "low"

    def _gate_type(coverage_class: str) -> str:
        return {
            "portable": "baseline",
            "broad": "baseline",
            "conditional": "capability",
            "helper-boundary": "helper-boundary",
            "desktop-boundary": "desktop-profile",
            "x11-first": "portability",
            "experimental": "opt-in",
        }.get(str(coverage_class or ""), "capability")

    def _artifacts_for(name: str) -> list[dict[str, str]]:
        if name == "text_injection":
            items = [
                {"id": "espanso-package", "title": "Espanso export package", "path_hint": "./build/espanso_package/"},
            ]
            if hotstrings:
                items.append({"id": "text-hotstring-manifest", "title": "Text trigger manifest", "path_hint": "project.yaml hotstrings"})
            return items
        if name == "pointer_injection":
            return [
                {"id": "selector-assets", "title": "Selector / needle assets", "path_hint": "assets/*.png"},
                {"id": "pointer-fallback-notes", "title": "Fallback surface notes", "path_hint": "docs/PROJECT_STRATEGY.md"},
            ]
        if name == "screen_capture":
            return [
                {"id": "capture-haystacks", "title": "Representative haystacks", "path_hint": "./tmp/screens/ or captured screenshots"},
                {"id": "needle-pack", "title": "Needle preview pack", "path_hint": "assets/*.png"},
            ]
        if name == "global_hotkeys":
            items = [
                {"id": "wm-bundle", "title": "WM/compositor bundle", "path_hint": "./build/wm_bundle/"},
                {"id": "launcher-entry", "title": "Desktop / launcher entry", "path_hint": "./build/vhk.desktop"},
            ]
            if backend == "x11" or bindings:
                items.append({"id": "sxhkd-config", "title": "sxhkd-style hotkey config", "path_hint": "./build/vhk.sxhkdrc"})
            return items
        if name == "window_introspection":
            return [
                {"id": "window-selector-samples", "title": "Window selector samples", "path_hint": "project bindings/watchers"},
            ]
        if name == "input_capture":
            return [
                {"id": "remap-config", "title": "Remapper/helper config", "path_hint": "./build/vhk.keyd.conf or ./build/vhk.kanata.kbd"},
            ]
        return []

    def _checks_and_commands(name: str, coverage_item: Mapping[str, Any], toolchain_item: Mapping[str, Any]) -> tuple[list[str], list[str], str]:
        coverage_class = str(coverage_item.get("coverage_class") or "conditional")
        current_status = str(coverage_item.get("current_status") or "unknown")
        offload_paths = [str(x) for x in (coverage_item.get("offload_paths") or []) if str(x)]
        fallback_toolchains = [str(x) for x in (toolchain_item.get("fallback_toolchains") or []) if str(x)]
        fallback = fallback_toolchains[0] if fallback_toolchains else (offload_paths[0] if offload_paths else "degrade to a thinner Linux-native surface")

        base_commands = [
            f"vhk validate {root_q} --json",
            f"vhk plan-project {root_q} --json",
        ]
        if current_status in {"missing", "limited"} or coverage_class in {"helper-boundary", "desktop-boundary", "experimental"} or backend == "wayland":
            base_commands.insert(0, "vhk doctor --json")

        if name == "text_injection":
            checks = [
                "typing-heavy macros complete through the preferred text path without depending on pointer playback",
                "snippet/forms flows have a text export or clipboard-friendly fallback for conservative desktops",
                "portable-text coverage is preserved for the user-facing text subset",
            ]
            commands = [
                *base_commands,
                f"vhk gen-espanso {root_q} --package-dir ./build/espanso_package",
            ]
            summary = f"Verify that text automation stays text-first and can fall back to {fallback} before pointer-heavy paths are considered required."
            return checks, _dedupe_keep_order(commands), summary

        if name == "pointer_injection":
            checks = [
                "critical click targets have selector/needle assets or an explicit helper-boundary plan",
                "a conservative desktop fallback exists for pointer-heavy macros",
                "session diagnostics are reviewed before shipping pointer automation as a baseline feature",
            ]
            commands = [
                *base_commands,
                f"vhk preview-needle path/to/needle.png --project {root_q} --haystack path/to/screenshot.png --json --no-check",
            ]
            summary = f"Verify pointer automation behind a helper boundary and prove the project can degrade to {fallback} when native pointer injection is weak."
            return checks, _dedupe_keep_order(commands), summary

        if name == "screen_capture":
            checks = [
                "capture output is good enough for selector preview and vision debugging",
                "vision-heavy macros do not rely only on fixed delays to survive capture latency",
                "capture routing is understood for the intended desktop family",
            ]
            commands = [
                *base_commands,
                f"vhk preview-needle path/to/needle.png --project {root_q} --haystack path/to/screenshot.png --json --no-check",
            ]
            summary = f"Verify the capture path early and keep selector/debug assets ready so vision flows can fall back to {fallback} instead of blind retries."
            return checks, _dedupe_keep_order(commands), summary

        if name == "global_hotkeys":
            checks = [
                "each user-facing trigger has at least one exported bind or launcher path",
                "a launcher/palette fallback exists when global shortcuts are missing or conditional",
                "the bind layer stays thin and hands control back to VHK for macro logic",
            ]
            commands = [
                *base_commands,
                f"vhk export-wm-bundle {root_q} ./build/wm_bundle --wm i3 --kind binding --key Mod4+semicolon",
                f"vhk gen-sxhkd-config {root_q} --out ./build/vhk.sxhkdrc",
            ]
            if backend == "wayland":
                commands.insert(1, f"vhk portal-hotkeys {root_q} --max-events 1")
            summary = f"Verify triggers as exported desktop surfaces, and keep {fallback} ready whenever a universal global-hotkey path is unavailable."
            return checks, _dedupe_keep_order(commands), summary

        if name == "window_introspection":
            checks = [
                "window/app selectors are tested on the intended desktop family",
                "focus/context detection is not treated as portable unless diagnostics prove it",
                "dispatch or app-scoping fallbacks exist when deep window APIs are missing",
            ]
            commands = [
                *base_commands,
                f"vhk window-spy --project {root_q} --json --no-check",
            ]
            summary = f"Verify window-context assumptions directly and be ready to fall back to {fallback} when rich desktop metadata is unavailable."
            return checks, _dedupe_keep_order(commands), summary

        if name == "input_capture":
            checks = [
                "raw input capture is opt-in and isolated from baseline project execution",
                "a remapper/export path exists for conservative desktops",
                "helper or daemon requirements are documented before claiming support",
            ]
            commands = [
                *base_commands,
                f"vhk gen-keyd-config {root_q} --out ./build/vhk.keyd.conf",
                f"vhk gen-kanata-config {root_q} --out ./build/vhk.kanata.kbd",
            ]
            summary = f"Verify capture only as an extension seam and keep {fallback} ready so the project is not blocked on raw-input support."
            return checks, _dedupe_keep_order(commands), summary

        checks = ["doctor/validate/plan-project agree on the target capability story before release"]
        return checks, _dedupe_keep_order(base_commands), "Verify the capability explicitly before treating it as portable."

    items: list[dict[str, Any]] = []
    for coverage_item in capability_coverage:
        capability = str(coverage_item.get("capability") or "")
        use_count = int(coverage_item.get("usage_count") or 0)
        current_status = str(coverage_item.get("current_status") or "unknown")
        if not capability:
            continue
        if use_count <= 0 and current_status == "unknown":
            continue

        pressure = str(coverage_item.get("project_pressure") or "low")
        coverage_class = str(coverage_item.get("coverage_class") or "conditional")
        toolchain_item = toolchain_by_cap.get(capability, {})
        priority = _priority(pressure=pressure, current_status=current_status, coverage_class=coverage_class, use_count=use_count)
        gate_type = _gate_type(coverage_class)
        checks, commands, summary = _checks_and_commands(capability, coverage_item, toolchain_item)

        target_envs = _dedupe_keep_order([
            *[str(x) for x in (coverage_item.get("best_environments") or [])[:2] if str(x)],
            *[str(x) for x in (coverage_item.get("limited_environments") or [])[:1] if str(x)],
            *[str(x) for x in (coverage_item.get("blocking_environments") or [])[:1] if str(x)],
        ])
        if not target_envs:
            target_envs = ["Current session"]

        artifacts = _artifacts_for(capability)
        evidence = _dedupe_keep_order([
            *[str(x) for x in (coverage_item.get("evidence") or [])[:4] if str(x)],
            *[f"toolchain={str(toolchain_item.get('recommended_toolchain') or 'n/a')}"],
            *[f"backend={backend or 'unknown'}"],
        ])

        items.append({
            "id": capability.replace("_", "-"),
            "title": str(coverage_item.get("title") or capability),
            "capability": capability,
            "category": str(coverage_item.get("category") or toolchain_item.get("category") or "general"),
            "priority": priority,
            "gate_type": gate_type,
            "summary": summary,
            "acceptance_checks": checks,
            "commands": commands[:5],
            "artifacts": artifacts,
            "target_environments": target_envs,
            "fallback_path": (toolchain_item.get("fallback_toolchains") or coverage_item.get("offload_paths") or [""])[0] if (toolchain_item.get("fallback_toolchains") or coverage_item.get("offload_paths")) else "",
            "recommended_toolchain": str(toolchain_item.get("recommended_toolchain") or coverage_item.get("recommended_toolchain") or ""),
            "evidence": evidence[:6],
        })

    items.sort(key=lambda item: ({"high": 0, "medium": 1, "low": 2}.get(str(item.get("priority") or "medium"), 1), -len(item.get("target_environments") or []), str(item.get("title") or "")))
    return items


def _implementation_waves(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    playbooks: list[dict[str, Any]] | None = None,
    portability_playbooks: list[dict[str, Any]] | None = None,
    toolchain_choices: list[dict[str, Any]] | None = None,
    capability_coverage: list[dict[str, Any]] | None = None,
    verification_gates: list[dict[str, Any]] | None = None,
    reference_patterns: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Turn strategy hints into a sequenced delivery plan.

    The planner already names targets, toolchains, and gates. This layer answers
    the next product question: in what order should a team *build* those pieces
    so a Linux-native automation project becomes runnable, inspectable, and
    portable without taking on every hard problem at once?

    The result is intentionally wave-based so future Studio/UI flows can render
    it as a roadmap, backlog seed, or setup wizard.
    """

    playbooks = list(playbooks or [])
    portability_playbooks = list(portability_playbooks or [])
    toolchain_choices = list(toolchain_choices or [])
    capability_coverage = list(capability_coverage or [])
    verification_gates = list(verification_gates or [])
    reference_patterns = list(reference_patterns or [])

    backend = str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "").strip().lower()
    root_dir = getattr(project, "root_dir", None) or "."
    root_q = shlex.quote(str(root_dir))

    hotstrings = int(overview.get("hotstrings") or 0)
    bindings = int(overview.get("bindings") or 0)
    watchers = int(overview.get("clipboard_watchers") or 0) + int(overview.get("file_watchers") or 0) + int(overview.get("bus_watchers") or 0) + int(overview.get("window_watchers") or 0)

    playbook_by_id = {str(item.get("id") or ""): item for item in playbooks if str(item.get("id") or "")}
    portability_by_id = {str(item.get("id") or ""): item for item in portability_playbooks if str(item.get("id") or "")}
    coverage_by_cap = {str(item.get("capability") or ""): item for item in capability_coverage if str(item.get("capability") or "")}
    gate_by_cap = {str(item.get("capability") or ""): item for item in verification_gates if str(item.get("capability") or "")}
    pattern_by_id = {str(item.get("id") or ""): item for item in reference_patterns if str(item.get("id") or "")}

    def _dedupe_keep_order(values: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in values:
            val = str(item or "").strip()
            if not val or val in seen:
                continue
            seen.add(val)
            out.append(val)
        return out

    def _commands_from(*items: Mapping[str, Any] | None) -> list[str]:
        commands: list[str] = []
        for item in items:
            if not isinstance(item, Mapping):
                continue
            commands.extend(str(x) for x in (item.get("commands") or []) if str(x))
        return _dedupe_keep_order(commands)

    def _checks_from(*items: Mapping[str, Any] | None) -> list[str]:
        checks: list[str] = []
        for item in items:
            if not isinstance(item, Mapping):
                continue
            checks.extend(str(x) for x in (item.get("acceptance_checks") or []) if str(x))
        return _dedupe_keep_order(checks)

    def _deliverables_from(*items: Mapping[str, Any] | None) -> list[dict[str, str]]:
        out: list[dict[str, str]] = []
        seen: set[tuple[str, str, str]] = set()
        for item in items:
            if not isinstance(item, Mapping):
                continue
            for artifact in (item.get("artifacts") or []):
                if not isinstance(artifact, Mapping):
                    continue
                aid = str(artifact.get("id") or "deliverable")
                title = str(artifact.get("title") or aid)
                path_hint = str(artifact.get("path_hint") or "")
                key = (aid, title, path_hint)
                if key in seen:
                    continue
                seen.add(key)
                out.append({"id": aid, "title": title, "path_hint": path_hint})
        return out

    def _pattern_refs(*ids: str) -> list[dict[str, str]]:
        refs: list[dict[str, str]] = []
        seen: set[str] = set()
        for pid in ids:
            key = str(pid or "").strip()
            if not key or key in seen:
                continue
            item = pattern_by_id.get(key, {})
            seen.add(key)
            refs.append({
                "id": key,
                "title": str(item.get("title") or key.replace("-", " ").title()),
                "fit": str(item.get("fit") or ""),
            })
        return refs

    waves: list[dict[str, Any]] = []

    def add_wave(
        wave_id: str,
        order: int,
        title: str,
        objective: str,
        *,
        priority: str = "medium",
        why_now: str = "",
        commands: list[str] | None = None,
        deliverables: list[dict[str, str]] | None = None,
        validation: list[str] | None = None,
        borrowed_patterns: list[dict[str, str]] | None = None,
        related_capabilities: list[str] | None = None,
        depends_on: list[str] | None = None,
    ) -> None:
        waves.append({
            "id": wave_id,
            "order": order,
            "priority": priority,
            "title": title,
            "objective": objective,
            "why_now": why_now,
            "commands": list(commands or []),
            "deliverables": list(deliverables or []),
            "validation": list(validation or []),
            "borrowed_patterns": list(borrowed_patterns or []),
            "related_capabilities": list(related_capabilities or []),
            "depends_on": list(depends_on or []),
        })

    foundation_commands = _commands_from(
        playbook_by_id.get("deployment-audit"),
        gate_by_cap.get("global_hotkeys"),
        gate_by_cap.get("text_injection"),
    )
    if not foundation_commands:
        foundation_commands = [
            "vhk doctor --json",
            f"vhk validate {root_q} --json",
            f"vhk plan-project {root_q} --json",
        ]
    foundation_deliverables = _deliverables_from(
        gate_by_cap.get("global_hotkeys"),
        gate_by_cap.get("text_injection"),
    )
    foundation_validation = _checks_from(
        gate_by_cap.get("global_hotkeys"),
        gate_by_cap.get("text_injection"),
    )
    if backend == "wayland" or any(str(item.get("current_status") or "") in {"missing", "limited"} for item in capability_coverage):
        foundation_priority = "high"
    else:
        foundation_priority = "medium"
    add_wave(
        "foundation-contract",
        1,
        "Wave 1 — capability contract and exported entry points",
        "Pick the real Linux target profile, lock in preferred toolchains, and make the initial trigger/text surfaces exportable before deeper macro work.",
        priority=foundation_priority,
        why_now="Linux automation portability usually fails at the capability boundary first, so the target desktop/session contract should be explicit before the project grows.",
        commands=foundation_commands[:6],
        deliverables=foundation_deliverables[:5],
        validation=foundation_validation[:4],
        borrowed_patterns=_pattern_refs("ahk-runner-core", "wm-bind-dispatch", "portal-helper-boundary"),
        related_capabilities=["global_hotkeys", "text_injection"],
    )

    if hotstrings or coverage_by_cap.get("text_injection"):
        add_wave(
            "text-and-prompt-tier",
            2,
            "Wave 2 — text/forms tier and launcher ergonomics",
            "Move snippet and prompt-heavy flows into a fast exported text tier while keeping VHK in charge of orchestration and structured prompts.",
            priority="high" if hotstrings else "medium",
            why_now="Text workflows are the easiest portable win on Linux, and they give the project a native-feeling surface early.",
            commands=_commands_from(
                playbook_by_id.get("text-export-loop"),
                gate_by_cap.get("text_injection"),
            )[:6],
            deliverables=_deliverables_from(
                gate_by_cap.get("text_injection"),
            )[:5],
            validation=_checks_from(
                gate_by_cap.get("text_injection"),
            )[:4],
            borrowed_patterns=_pattern_refs("espanso-forms-text-tier", "pulover-visual-studio"),
            related_capabilities=["text_injection"],
            depends_on=["foundation-contract"],
        )

    if coverage_by_cap.get("pointer_injection") or coverage_by_cap.get("screen_capture") or "selector-asset-heavy" in project_tags:
        add_wave(
            "visual-debug-loop",
            3,
            "Wave 3 — selector assets, capture quality, and pointer boundaries",
            "Turn pointer and vision macros into inspectable assets with explicit capture and fallback assumptions, rather than relying on blind timing.",
            priority="high",
            why_now="Visual automation becomes expensive fast, so selector quality and pointer fallbacks need to be measurable before the project scales.",
            commands=_commands_from(
                playbook_by_id.get("selector-debug-loop"),
                gate_by_cap.get("pointer_injection"),
                gate_by_cap.get("screen_capture"),
            )[:6],
            deliverables=_deliverables_from(
                gate_by_cap.get("pointer_injection"),
                gate_by_cap.get("screen_capture"),
            )[:6],
            validation=_checks_from(
                gate_by_cap.get("pointer_injection"),
                gate_by_cap.get("screen_capture"),
            )[:5],
            borrowed_patterns=_pattern_refs("ahk-runner-core", "portal-helper-boundary"),
            related_capabilities=["pointer_injection", "screen_capture"],
            depends_on=["foundation-contract"],
        )

    if bindings or watchers or coverage_by_cap.get("input_capture") or coverage_by_cap.get("global_hotkeys"):
        daemon_item = playbook_by_id.get("dispatch-daemon-loop")
        remap_item = playbook_by_id.get("remap-export-loop")
        portability_item = portability_by_id.get("hyprland-conservative") or portability_by_id.get("wlroots-sway-conservative")
        add_wave(
            "dispatch-and-daemons",
            4,
            "Wave 4 — dispatch shell, remap seams, and user services",
            "Push always-on triggers, watcher buses, and remap-heavy behavior into thin exported/service layers so the runner owns orchestration instead of raw interception.",
            priority="high" if (bindings or watchers) else "medium",
            why_now="Low-latency or always-on behavior is where Linux stacks diverge most, so service/remap seams should be separated from macro logic before release claims.",
            commands=_commands_from(
                remap_item,
                daemon_item,
                gate_by_cap.get("global_hotkeys"),
                gate_by_cap.get("input_capture"),
                portability_item,
            )[:7],
            deliverables=_deliverables_from(
                gate_by_cap.get("global_hotkeys"),
                gate_by_cap.get("input_capture"),
                portability_item,
            )[:7],
            validation=_checks_from(
                gate_by_cap.get("global_hotkeys"),
                gate_by_cap.get("input_capture"),
            )[:5],
            borrowed_patterns=_pattern_refs("wm-bind-dispatch", "remap-daemon-offload", "portal-helper-boundary"),
            related_capabilities=["global_hotkeys", "input_capture"],
            depends_on=["foundation-contract"],
        )

    release_commands = _dedupe_keep_order([
        *[str(x) for gate in verification_gates[:5] for x in (gate.get("commands") or [])],
        f"vhk validate {root_q} --json",
        f"vhk plan-project {root_q} --json",
    ])
    release_validation = _dedupe_keep_order([
        *[str(x) for gate in verification_gates[:5] for x in (gate.get("acceptance_checks") or [])],
        "exported surfaces and runtime macros agree on the same desktop capability story",
    ])
    release_deliverables = _deliverables_from(*verification_gates[:5])
    add_wave(
        "release-gates",
        5,
        "Wave 5 — verification, portability review, and release packaging",
        "Run the capability gates, confirm conservative-desktop fallbacks, and package the project only after the exported surfaces and runtime agree.",
        priority="high",
        why_now="A Linux-native automation tool needs proof that its exported surfaces, helper seams, and runtime macros tell the same truth before users depend on it.",
        commands=release_commands[:8],
        deliverables=release_deliverables[:8],
        validation=release_validation[:6],
        borrowed_patterns=_pattern_refs("ahk-runner-core", "portal-helper-boundary", "espanso-forms-text-tier"),
        related_capabilities=[str(item.get("capability") or "") for item in verification_gates[:5] if str(item.get("capability") or "")],
        depends_on=[wave["id"] for wave in waves],
    )

    waves.sort(key=lambda item: int(item.get("order") or 999))
    return waves



def _artifact_blueprint(
    *,
    project,
    portability_playbooks: list[dict[str, Any]] | None = None,
    verification_gates: list[dict[str, Any]] | None = None,
    implementation_waves: list[dict[str, Any]] | None = None,
    toolchain_choices: list[dict[str, Any]] | None = None,
    capability_coverage: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Turn planning surfaces into a concrete artifact/deployment map.

    `implementation_waves` explains *when* to build pieces and verification/
    portability surfaces explain *why*. This helper answers the next practical
    question: which files, exports, services, and audit artifacts should exist
    in the repo or build output if the project is going to feel Linux-native?

    The result is intentionally machine-readable so future scaffold/export/setup
    flows can converge on the same deployment story instead of inventing it
    command-by-command.
    """

    portability_playbooks = list(portability_playbooks or [])
    verification_gates = list(verification_gates or [])
    implementation_waves = list(implementation_waves or [])
    toolchain_choices = list(toolchain_choices or [])
    capability_coverage = list(capability_coverage or [])

    if not portability_playbooks and not verification_gates and not implementation_waves:
        return []

    root_dir = getattr(project, "root_dir", None) or "."
    root_q = shlex.quote(str(root_dir))

    def _dedupe_keep_order(values: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in values:
            val = str(item or "").strip()
            if not val or val in seen:
                continue
            seen.add(val)
            out.append(val)
        return out

    def _priority_rank(text: str) -> int:
        return {"high": 0, "medium": 1, "low": 2}.get(str(text or "medium"), 1)

    def _normalize_artifact(aid: str, title: str, path_hint: str) -> dict[str, str]:
        artifact_id = str(aid or "artifact").strip() or "artifact"
        normalized_path = str(path_hint or "").strip()
        normalized_title = str(title or artifact_id.replace("-", " ").title()).strip() or artifact_id.replace("-", " ").title()

        category = "support"
        ownership = "build-output"
        deployment_surface = "build artifact"
        install_hint = normalized_path or "./build/"
        rationale = "Keep the deployment story explicit instead of hiding it in ad-hoc setup steps."

        if artifact_id in {"espanso-package", "text-hotstring-manifest"}:
            category = "text-export"
            ownership = "export-surface"
            deployment_surface = "Espanso text package"
            install_hint = install_hint or "Run `espanso path packages` and install under that packages directory."
            rationale = "Portable text and snippet flows should ship as a first-class Linux text surface, not only as runner playback."
        elif artifact_id in {"desktop-entry", "launcher-entry"}:
            category = "launcher"
            ownership = "export-surface"
            deployment_surface = "desktop launcher / drun entry"
            install_hint = install_hint or "$XDG_DATA_HOME/applications/ (or ~/.local/share/applications/)"
            rationale = "A desktop entry keeps the project reachable even when global hooks are conditional or desktop-specific."
        elif artifact_id in {"launcher-script"}:
            category = "launcher"
            ownership = "export-surface"
            deployment_surface = "user launcher helper"
            install_hint = install_hint or "$XDG_BIN_HOME/ (or ~/.local/bin/)"
            rationale = "Launcher wrappers are a lightweight Linux-native bridge between menus/WM binds and the VHK runtime."
        elif artifact_id in {"wm-bundle", "i3-bindings", "sway-bindings", "hyprland-bindings", "sxhkd-config"}:
            category = "trigger-export"
            ownership = "desktop-config"
            deployment_surface = "window manager / hotkey config"
            install_hint = install_hint or "$XDG_CONFIG_HOME/<wm>/ or the target hotkey daemon config path"
            rationale = "Thin trigger exports are often a better Linux fit than promising one universal global-hotkey backend."
        elif artifact_id in {"keyd-config", "kanata-config", "kmonad-config", "xremap-config", "remap-config"}:
            category = "remap-export"
            ownership = "helper-boundary"
            deployment_surface = "remapper / low-latency key layer"
            install_hint = install_hint or "system or user remapper config, plus any wrapper needed to re-enter the desktop session"
            rationale = "Keep always-on key semantics in dedicated remapper layers when the runner should stay focused on orchestration."
        elif artifact_id in {"systemd-user-units"}:
            category = "service"
            ownership = "user-service"
            deployment_surface = "systemd user manager"
            install_hint = install_hint or "$XDG_CONFIG_HOME/systemd/user/ (or ~/.config/systemd/user/)"
            rationale = "Watcher- and bus-driven automation should deploy like native Linux user services, not shell sessions you hope stay open."
        elif artifact_id in {"selector-assets", "needle-pack", "capture-haystacks", "window-selector-samples"}:
            category = "asset-pack"
            ownership = "project-repo"
            deployment_surface = "project assets / debug corpus"
            install_hint = install_hint or "assets/ or a checked-in debug corpus"
            rationale = "Vision-heavy automation needs inspectable assets so it can be tuned and reviewed instead of relying on blind timing."
        elif artifact_id in {"pointer-fallback-notes", "pointer-helper-boundary", "portal-capability-audit", "fallback-surface-notes"}:
            category = "audit"
            ownership = "docs-and-review"
            deployment_surface = "capability audit / helper contract"
            install_hint = install_hint or "docs/ or release checklist"
            rationale = "Hard desktop capabilities should ship with an explicit contract, not an implied promise."
        elif artifact_id in {"needle-preview-pack"}:
            category = "asset-pack"
            ownership = "project-repo"
            deployment_surface = "needle preview corpus"
            install_hint = install_hint or "assets/ or preview fixtures"
            rationale = "Preview packs keep visual automation explainable across desktops and regressions."

        return {
            "id": artifact_id,
            "title": normalized_title,
            "path_hint": normalized_path,
            "category": category,
            "ownership": ownership,
            "deployment_surface": deployment_surface,
            "install_hint": install_hint,
            "rationale": rationale,
        }

    def _default_generator_commands(artifact_id: str, path_hint: str) -> list[str]:
        target = path_hint or "./build"
        if artifact_id == "espanso-package":
            return [f"vhk gen-espanso {root_q} --package-dir ./build/espanso_package"]
        if artifact_id in {"desktop-entry", "launcher-entry"}:
            target = path_hint or "./build/vhk-project.desktop"
            return [f"vhk export-desktop-entry {root_q} {target}"]
        if artifact_id == "launcher-script":
            target = path_hint or "./build/vhk-launch"
            return [f"vhk export-launcher-script {root_q} {target}"]
        if artifact_id == "sxhkd-config":
            target = path_hint or "./build/vhk.sxhkdrc"
            return [f"vhk gen-sxhkd-config {root_q} --out {target}"]
        if artifact_id == "keyd-config":
            target = path_hint or "./build/vhk.keyd.conf"
            return [f"vhk gen-keyd-config {root_q} --out {target}"]
        if artifact_id == "kanata-config":
            target = path_hint or "./build/vhk.kanata.kbd"
            return [f"vhk gen-kanata-config {root_q} --out {target}"]
        if artifact_id == "kmonad-config":
            target = path_hint or "./build/vhk.kmonad.kbd"
            return [f"vhk gen-kmonad-config {root_q} --out {target}"]
        if artifact_id == "xremap-config":
            target = path_hint or "./build/vhk.xremap.yml"
            return [f"vhk gen-xremap-config {root_q} --out {target}"]
        if artifact_id == "systemd-user-units":
            target = path_hint or "./build/systemd-user"
            return [
                f"vhk gen-vhk-busd-service {root_q} --out-dir {target}",
                f"vhk gen-vhk-busd-socket-units {root_q} --out-dir {target}",
            ]
        if artifact_id == "wm-bundle":
            return [f"vhk export-wm-bundle {root_q} ./build/wm_bundle --wm i3 --kind binding --key Mod4+semicolon"]
        if artifact_id == "i3-bindings":
            target = path_hint or "./build/vhk.i3.conf"
            return [f"vhk export-wm-bindings {root_q} {target} --wm i3 --launcher palette-command"]
        if artifact_id == "sway-bindings":
            target = path_hint or "./build/vhk.sway.conf"
            return [f"vhk export-wm-bindings {root_q} {target} --wm sway --launcher palette-command"]
        if artifact_id == "hyprland-bindings":
            target = path_hint or "./build/vhk.hyprland.conf"
            return [f"vhk export-wm-bindings {root_q} {target} --wm hyprland --launcher palette-command"]
        if artifact_id in {"selector-assets", "needle-pack", "capture-haystacks"}:
            return [
                f"vhk optimize-project {root_q}",
                f"vhk preview-needle path/to/needle.png --project {root_q} --haystack path/to/screenshot.png --json --no-check",
            ]
        if artifact_id in {"pointer-helper-boundary", "portal-capability-audit", "pointer-fallback-notes"}:
            return ["vhk doctor --json", f"vhk plan-project {root_q} --json"]
        if artifact_id == "remap-config":
            return [
                f"vhk gen-keyd-config {root_q} --out ./build/vhk.keyd.conf",
                f"vhk gen-kanata-config {root_q} --out ./build/vhk.kanata.kbd",
            ]
        return []

    records: dict[str, dict[str, Any]] = {}
    coverage_by_cap = {str(item.get("capability") or ""): item for item in capability_coverage if str(item.get("capability") or "")}
    toolchain_by_cap = {str(item.get("capability") or ""): item for item in toolchain_choices if str(item.get("capability") or "")}

    def _record(
        artifact: Mapping[str, Any],
        *,
        source_kind: str,
        source_id: str,
        source_title: str,
        source_priority: str = "medium",
        source_order: int | None = None,
        commands: list[str] | None = None,
        validation: list[str] | None = None,
        related_capabilities: list[str] | None = None,
        related_surfaces: list[str] | None = None,
    ) -> None:
        aid = str(artifact.get("id") or "artifact")
        title = str(artifact.get("title") or aid)
        path_hint = str(artifact.get("path_hint") or "")
        base = _normalize_artifact(aid, title, path_hint)
        entry = records.get(aid)
        if entry is None:
            entry = {
                **base,
                "priority": str(source_priority or "medium"),
                "first_wave": None,
                "source_refs": [],
                "source_kinds": [],
                "source_ids": [],
                "generator_commands": [],
                "validation_commands": [],
                "acceptance_notes": [],
                "related_capabilities": [],
                "related_surfaces": [],
                "toolchains": [],
                "environment_lanes": [],
            }
            records[aid] = entry
        else:
            if not entry.get("path_hint") and path_hint:
                entry["path_hint"] = path_hint
            if _priority_rank(str(source_priority or "medium")) < _priority_rank(str(entry.get("priority") or "medium")):
                entry["priority"] = str(source_priority or "medium")

        if source_order is not None:
            current_wave = entry.get("first_wave")
            if not isinstance(current_wave, dict) or int(current_wave.get("order") or 999) > int(source_order):
                entry["first_wave"] = {"id": source_id, "title": source_title, "order": int(source_order)}

        ref = f"{source_kind}:{source_id}"
        if ref not in entry["source_refs"]:
            entry["source_refs"].append(ref)
        if source_kind and source_kind not in entry["source_kinds"]:
            entry["source_kinds"].append(source_kind)
        if source_id and source_id not in entry["source_ids"]:
            entry["source_ids"].append(source_id)

        if source_kind == "playbook" and source_title and source_title not in entry["environment_lanes"]:
            entry["environment_lanes"].append(source_title)

        entry["generator_commands"] = _dedupe_keep_order([
            *[str(x) for x in entry.get("generator_commands") or []],
            *[str(x) for x in (commands or []) if str(x)],
        ])
        entry["validation_commands"] = _dedupe_keep_order([
            *[str(x) for x in entry.get("validation_commands") or []],
            *[str(x) for x in (validation or []) if str(x)],
        ])
        entry["related_capabilities"] = _dedupe_keep_order([
            *[str(x) for x in entry.get("related_capabilities") or []],
            *[str(x) for x in (related_capabilities or []) if str(x)],
        ])
        entry["related_surfaces"] = _dedupe_keep_order([
            *[str(x) for x in entry.get("related_surfaces") or []],
            *[str(x) for x in (related_surfaces or []) if str(x)],
        ])

    for wave in implementation_waves:
        source_id = str(wave.get("id") or "")
        source_title = str(wave.get("title") or source_id)
        source_priority = str(wave.get("priority") or "medium")
        source_order = int(wave.get("order") or 999)
        commands = [str(x) for x in (wave.get("commands") or []) if str(x)]
        validation = [str(x) for x in (wave.get("validation") or []) if str(x)]
        related_capabilities = [str(x) for x in (wave.get("related_capabilities") or []) if str(x)]
        for artifact in (wave.get("deliverables") or []):
            if isinstance(artifact, Mapping):
                _record(
                    artifact,
                    source_kind="wave",
                    source_id=source_id,
                    source_title=source_title,
                    source_priority=source_priority,
                    source_order=source_order,
                    commands=commands,
                    validation=validation,
                    related_capabilities=related_capabilities,
                )

    for gate in verification_gates:
        source_id = str(gate.get("id") or "")
        source_title = str(gate.get("title") or source_id)
        source_priority = str(gate.get("priority") or "medium")
        commands = [str(x) for x in (gate.get("commands") or []) if str(x)]
        validation = [str(x) for x in (gate.get("acceptance_checks") or []) if str(x)]
        related_capabilities = [str(gate.get("capability") or "")] if str(gate.get("capability") or "") else []
        for artifact in (gate.get("artifacts") or []):
            if isinstance(artifact, Mapping):
                _record(
                    artifact,
                    source_kind="gate",
                    source_id=source_id,
                    source_title=source_title,
                    source_priority=source_priority,
                    commands=commands,
                    validation=validation,
                    related_capabilities=related_capabilities,
                )

    for playbook in portability_playbooks:
        source_id = str(playbook.get("id") or "")
        source_title = str(playbook.get("title") or source_id)
        source_priority = str(playbook.get("priority") or "medium")
        commands = [str(x) for x in (playbook.get("commands") or []) if str(x)]
        validation = [str(x) for x in (playbook.get("install_checks") or []) if str(x)]
        related_surfaces = [str(x) for x in (playbook.get("related_surfaces") or []) if str(x)]
        for artifact in (playbook.get("artifacts") or []):
            if isinstance(artifact, Mapping):
                _record(
                    artifact,
                    source_kind="playbook",
                    source_id=source_id,
                    source_title=source_title,
                    source_priority=source_priority,
                    commands=commands,
                    validation=validation,
                    related_surfaces=related_surfaces,
                )

    items: list[dict[str, Any]] = []
    for aid, entry in records.items():
        related_caps = [str(x) for x in (entry.get("related_capabilities") or []) if str(x)]
        toolchains = _dedupe_keep_order([
            str((toolchain_by_cap.get(cap) or {}).get("recommended_toolchain") or "")
            for cap in related_caps
            if str((toolchain_by_cap.get(cap) or {}).get("recommended_toolchain") or "")
        ])
        if not toolchains:
            toolchains = _dedupe_keep_order([
                str((coverage_by_cap.get(cap) or {}).get("recommended_toolchain") or "")
                for cap in related_caps
                if str((coverage_by_cap.get(cap) or {}).get("recommended_toolchain") or "")
            ])
        entry["toolchains"] = toolchains[:4]

        default_cmds = _default_generator_commands(aid, str(entry.get("path_hint") or ""))
        entry["generator_commands"] = _dedupe_keep_order([
            *default_cmds,
            *[str(x) for x in (entry.get("generator_commands") or []) if str(x)],
        ])[:6]
        entry["validation_commands"] = _dedupe_keep_order([
            *[str(x) for x in (entry.get("validation_commands") or []) if str(x)],
            "vhk doctor --json",
            f"vhk validate {root_q} --json",
        ])[:6]

        if not entry.get("path_hint") and entry.get("install_hint"):
            entry["path_hint"] = str(entry.get("install_hint") or "")

        acceptance_bits = [str(x) for x in (entry.get("acceptance_notes") or []) if str(x)]
        if not acceptance_bits:
            acceptance_bits = [
                str(entry.get("rationale") or ""),
                "prefer thin exports/helpers around the runner instead of burying Linux deployment assumptions inside macro logic",
            ]
        entry["acceptance_notes"] = _dedupe_keep_order(acceptance_bits)[:4]

        items.append(entry)

    items.sort(
        key=lambda item: (
            _priority_rank(str(item.get("priority") or "medium")),
            int((item.get("first_wave") or {}).get("order") or 999),
            str(item.get("category") or ""),
            str(item.get("title") or ""),
        )
    )
    return items



def _deployable_surfaces(
    *,
    artifact_blueprint: list[dict[str, Any]] | None = None,
    surface_choices: list[dict[str, Any]] | None = None,
    verification_gates: list[dict[str, Any]] | None = None,
    portability_playbooks: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Group artifacts into end-user deployable surfaces.

    `artifact_blueprint` answers *which files/configs/services* should exist.
    This helper turns those artifacts back into the Linux-facing surfaces users
    actually install and interact with: text packages, launcher entrypoints, WM
    trigger layers, remapper seams, services, selector/debug packs, and helper
    boundary audits.

    The result keeps `plan-project` operational: teams can move from strategy and
    file-level outputs to concrete installable surfaces without reverse-
    engineering the repo layout by hand.
    """

    artifact_blueprint = list(artifact_blueprint or [])
    surface_choices = list(surface_choices or [])
    verification_gates = list(verification_gates or [])
    portability_playbooks = list(portability_playbooks or [])

    if not artifact_blueprint:
        return []

    def _dedupe_keep_order(values: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in values:
            val = str(item or '').strip()
            if not val or val in seen:
                continue
            seen.add(val)
            out.append(val)
        return out

    def _priority_rank(text: str) -> int:
        return {'high': 0, 'medium': 1, 'low': 2}.get(str(text or 'medium'), 1)

    def _fit_rank(text: str) -> int:
        return {'strong': 0, 'good': 1, 'conditional': 2, 'weak': 3}.get(str(text or 'good'), 1)

    artifacts_by_id = {str(item.get('id') or ''): item for item in artifact_blueprint if str(item.get('id') or '')}
    surfaces_by_id = {str(item.get('id') or ''): item for item in surface_choices if str(item.get('id') or '')}
    playbooks_by_id = {str(item.get('id') or ''): item for item in portability_playbooks if str(item.get('id') or '')}
    gate_by_cap = {str(item.get('capability') or ''): item for item in verification_gates if str(item.get('capability') or '')}

    def _pick_fit(*surface_ids: str, default: str = 'good') -> str:
        fits = [str((surfaces_by_id.get(sid) or {}).get('fit') or '') for sid in surface_ids if sid in surfaces_by_id]
        fits = [fit for fit in fits if fit]
        if not fits:
            return default
        fits.sort(key=_fit_rank)
        return fits[0]

    def _pick_priority(*artifact_ids: str, default: str = 'medium') -> str:
        vals = [str((artifacts_by_id.get(aid) or {}).get('priority') or '') for aid in artifact_ids if aid in artifacts_by_id]
        vals = [val for val in vals if val]
        if not vals:
            return default
        vals.sort(key=_priority_rank)
        return vals[0]

    def _gate_commands(caps: Iterable[str]) -> list[str]:
        out: list[str] = []
        for cap in caps:
            gate = gate_by_cap.get(str(cap or ''))
            if not gate:
                continue
            out.extend(str(x) for x in (gate.get('commands') or []) if str(x))
        return _dedupe_keep_order(out)

    def _gate_acceptance(caps: Iterable[str]) -> list[str]:
        out: list[str] = []
        for cap in caps:
            gate = gate_by_cap.get(str(cap or ''))
            if not gate:
                continue
            out.extend(str(x) for x in (gate.get('acceptance_checks') or []) if str(x))
        return _dedupe_keep_order(out)

    def _playbook_notes(playbook_ids: Iterable[str]) -> list[str]:
        out: list[str] = []
        for pid in playbook_ids:
            item = playbooks_by_id.get(str(pid or ''))
            if not item:
                continue
            goal = str(item.get('goal') or '')
            if goal:
                out.append(goal)
        return _dedupe_keep_order(out)

    items: list[dict[str, Any]] = []

    def add_surface(
        sid: str,
        title: str,
        *,
        category: str,
        entrypoint: str,
        summary: str,
        artifact_ids: Iterable[str],
        surface_ids: Iterable[str] = (),
        related_capabilities: Iterable[str] = (),
        playbook_ids: Iterable[str] = (),
        notes: Iterable[str] = (),
        default_fit: str = 'good',
        default_priority: str = 'medium',
    ) -> None:
        selected_artifacts = [artifacts_by_id[aid] for aid in artifact_ids if aid in artifacts_by_id]
        if not selected_artifacts:
            return

        related_caps = _dedupe_keep_order(str(x) for x in related_capabilities if str(x))
        first_wave = None
        ordered_waves = [item.get('first_wave') or {} for item in selected_artifacts if isinstance(item.get('first_wave'), dict)]
        if ordered_waves:
            first_wave = min(ordered_waves, key=lambda item: int(item.get('order') or 999))

        install_targets = _dedupe_keep_order(
            str(item.get('install_hint') or item.get('path_hint') or '') for item in selected_artifacts
        )
        generator_commands = _dedupe_keep_order([
            *[str(cmd) for item in selected_artifacts for cmd in (item.get('generator_commands') or []) if str(cmd)],
            *[str(cmd) for surface_id in surface_ids for cmd in ((surfaces_by_id.get(surface_id) or {}).get('commands') or []) if str(cmd)],
            *_gate_commands(related_caps),
        ])
        validation_commands = _dedupe_keep_order([
            *[str(cmd) for item in selected_artifacts for cmd in (item.get('validation_commands') or []) if str(cmd)],
            *_gate_commands(related_caps),
        ])
        acceptance_checks = _dedupe_keep_order([
            *[str(note) for item in selected_artifacts for note in (item.get('acceptance_notes') or []) if str(note)],
            *_gate_acceptance(related_caps),
        ])
        note_bits = _dedupe_keep_order([
            *[str(x) for x in notes if str(x)],
            *_playbook_notes(playbook_ids),
            *[str(item.get('rationale') or '') for item in selected_artifacts if str(item.get('rationale') or '')],
        ])

        items.append({
            'id': sid,
            'title': title,
            'category': category,
            'entrypoint': entrypoint,
            'summary': summary,
            'fit': _pick_fit(*surface_ids, default=default_fit),
            'priority': _pick_priority(*artifact_ids, default=default_priority),
            'artifacts': [
                {
                    'id': str(item.get('id') or ''),
                    'title': str(item.get('title') or ''),
                    'category': str(item.get('category') or ''),
                    'deployment_surface': str(item.get('deployment_surface') or ''),
                    'path_hint': str(item.get('path_hint') or ''),
                    'install_hint': str(item.get('install_hint') or ''),
                }
                for item in selected_artifacts
            ],
            'install_targets': install_targets[:5],
            'generator_commands': generator_commands[:8],
            'validation_commands': validation_commands[:8],
            'acceptance_checks': acceptance_checks[:6],
            'related_capabilities': related_caps,
            'related_surface_choices': [
                {
                    'id': surface_id,
                    'title': str((surfaces_by_id.get(surface_id) or {}).get('title') or ''),
                    'fit': str((surfaces_by_id.get(surface_id) or {}).get('fit') or ''),
                    'category': str((surfaces_by_id.get(surface_id) or {}).get('category') or ''),
                }
                for surface_id in surface_ids
                if surface_id in surfaces_by_id
            ],
            'first_wave': first_wave or {},
            'notes': note_bits[:5],
        })

    add_surface(
        'text-automation',
        'Text automation package',
        category='text',
        entrypoint='Espanso/package-managed text expansion',
        summary='Ship prompted snippets and expansion flows as a Linux-native text package instead of relying only on macro playback.',
        artifact_ids=('espanso-package', 'text-hotstring-manifest'),
        surface_ids=('espanso-text-package',),
        related_capabilities=('text_injection',),
        notes=('Best for reusable app-scoped text, prompt overlays, and low-friction snippet entry.',),
        default_fit='good',
        default_priority='high',
    )
    add_surface(
        'launcher-entrypoints',
        'Launcher and menu entrypoints',
        category='launcher',
        entrypoint='Desktop entry, drun item, or launcher wrapper',
        summary='Expose the project palette through menus, launchers, and saved entrypoints so trigger UX stays native even when global hooks vary by desktop.',
        artifact_ids=('desktop-entry', 'launcher-entry', 'launcher-script'),
        surface_ids=('vhk-palette-launcher',),
        related_capabilities=('global_hotkeys',),
        notes=('Useful when the safest cross-desktop surface is an explicit launcher or menu action instead of a universal hotkey promise.',),
        default_fit='good',
        default_priority='medium',
    )
    add_surface(
        'wm-trigger-layer',
        'WM/compositor trigger layer',
        category='trigger',
        entrypoint='Window-manager bindings or launcher mode',
        summary='Push low-latency dispatch into WM/compositor-native bindings so the runner stays focused on orchestration.',
        artifact_ids=('wm-bundle', 'i3-bindings', 'sway-bindings', 'hyprland-bindings', 'sxhkd-config'),
        surface_ids=('wm-native-dispatch', 'portal-global-shortcuts'),
        related_capabilities=('global_hotkeys', 'window_introspection'),
        notes=('Prefer compositor-native bindings when Wayland or conservative desktops make universal hotkeys conditional.',),
        default_fit='good',
        default_priority='high',
    )
    add_surface(
        'remap-helper-layer',
        'Remap/helper boundary',
        category='remap',
        entrypoint='Dedicated remapper or low-latency key layer',
        summary='Keep always-on key semantics and interception-heavy behavior in remapper/helper configs instead of burying them in the main runtime.',
        artifact_ids=('keyd-config', 'kanata-config', 'kmonad-config', 'xremap-config', 'remap-config'),
        surface_ids=('keyd-remap', 'kanata-remap', 'kmonad-remap', 'xremap-remap'),
        related_capabilities=('global_hotkeys', 'input_capture'),
        notes=('A clean helper seam is often the only honest way to approach AHK-like always-on behavior on Linux.',),
        default_fit='conditional',
        default_priority='medium',
    )
    add_surface(
        'watcher-services',
        'Watcher and bus services',
        category='service',
        entrypoint='Systemd user units and always-on daemons',
        summary='Deploy watchers and bus bridges as user services so event-driven automation survives beyond one terminal session.',
        artifact_ids=('systemd-user-units',),
        surface_ids=('watcher-services',),
        related_capabilities=('input_capture', 'global_hotkeys'),
        notes=('Service-style deployment matters whenever clipboard/window/bus automation should stay alive independently of the authoring shell.',),
        default_fit='good',
        default_priority='high',
    )
    add_surface(
        'selector-debug-pack',
        'Selector and debug asset pack',
        category='debug',
        entrypoint='Checked-in needles, baselines, and selector samples',
        summary='Treat visual selectors and debug captures as a deployable asset pack so tuning and portability reviews stay inspectable.',
        artifact_ids=('selector-assets', 'needle-pack', 'capture-haystacks', 'window-selector-samples'),
        related_capabilities=('screen_capture', 'pointer_injection', 'window_introspection'),
        notes=('This is the visual equivalent of source code: without it, cross-desktop review collapses back into timing guesses.',),
        default_fit='good',
        default_priority='high',
    )
    add_surface(
        'capability-audit-pack',
        'Capability audit and fallback pack',
        category='audit',
        entrypoint='Helper-boundary notes, portal audits, and fallback contracts',
        summary='Package the uncomfortable truths too: capability audits and fallback notes are part of the shipping surface on Linux.',
        artifact_ids=('pointer-helper-boundary', 'pointer-fallback-notes', 'portal-capability-audit', 'fallback-surface-notes'),
        related_capabilities=('pointer_injection', 'screen_capture', 'input_capture', 'global_hotkeys'),
        playbook_ids=('hyprland-conservative', 'wlroots-sway-conservative'),
        notes=('Use this pack to make desktop-specific limits explicit before claiming broad Wayland parity.',),
        default_fit='conditional',
        default_priority='high',
    )

    items.sort(
        key=lambda item: (
            _priority_rank(str(item.get('priority') or 'medium')),
            int((item.get('first_wave') or {}).get('order') or 999),
            _fit_rank(str(item.get('fit') or 'good')),
            str(item.get('title') or ''),
        )
    )
    return items


def _setup_recipes(
    *,
    deployable_surfaces: list[dict[str, Any]] | None = None,
    artifact_blueprint: list[dict[str, Any]] | None = None,
    verification_gates: list[dict[str, Any]] | None = None,
    portability_playbooks: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Turn deployable surfaces into explicit Linux setup/install recipes.

    `deployable_surfaces` tells teams *what* operator-facing surfaces a project
    wants to ship. This helper answers the follow-on Linux-native question:
    which concrete install/review recipe does an author or operator follow to
    make that surface real?

    The result is intentionally machine-readable so future init/scaffold/setup
    flows can move beyond advisory planning and start generating useful install
    handoff documents or setup wizards from the same data.
    """

    deployable_surfaces = list(deployable_surfaces or [])
    artifact_blueprint = list(artifact_blueprint or [])
    verification_gates = list(verification_gates or [])
    portability_playbooks = list(portability_playbooks or [])

    if not deployable_surfaces:
        return []

    def _dedupe_keep_order(values: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in values:
            val = str(item or '').strip()
            if not val or val in seen:
                continue
            seen.add(val)
            out.append(val)
        return out

    def _priority_rank(text: str) -> int:
        return {'high': 0, 'medium': 1, 'low': 2}.get(str(text or 'medium'), 1)

    surfaces_by_id = {str(item.get('id') or ''): item for item in deployable_surfaces if str(item.get('id') or '')}
    gates_by_cap = {str(item.get('capability') or ''): item for item in verification_gates if str(item.get('capability') or '')}
    artifacts_by_id = {str(item.get('id') or ''): item for item in artifact_blueprint if str(item.get('id') or '')}
    playbooks_by_id = {str(item.get('id') or ''): item for item in portability_playbooks if str(item.get('id') or '')}

    def _surface(sid: str) -> Mapping[str, Any] | None:
        item = surfaces_by_id.get(sid)
        if isinstance(item, Mapping):
            return item
        return None

    def _caps_for_surfaces(surface_ids: Iterable[str]) -> list[str]:
        out: list[str] = []
        for sid in surface_ids:
            surf = _surface(str(sid or ''))
            if not surf:
                continue
            out.extend(str(x) for x in (surf.get('related_capabilities') or []) if str(x))
        return _dedupe_keep_order(out)

    def _gate_checks(capabilities: Iterable[str]) -> list[str]:
        out: list[str] = []
        for cap in capabilities:
            gate = gates_by_cap.get(str(cap or ''))
            if not gate:
                continue
            out.extend(str(x) for x in (gate.get('acceptance_checks') or []) if str(x))
        return _dedupe_keep_order(out)

    def _gate_commands(capabilities: Iterable[str]) -> list[str]:
        out: list[str] = []
        for cap in capabilities:
            gate = gates_by_cap.get(str(cap or ''))
            if not gate:
                continue
            out.extend(str(x) for x in (gate.get('commands') or []) if str(x))
        return _dedupe_keep_order(out)

    def _playbook_titles(playbook_ids: Iterable[str]) -> list[str]:
        out: list[str] = []
        for pid in playbook_ids:
            playbook = playbooks_by_id.get(str(pid or ''))
            if not playbook:
                continue
            title = str(playbook.get('title') or '')
            if title:
                out.append(title)
        return _dedupe_keep_order(out)

    def _artifact_refs(surface_ids: Iterable[str]) -> list[dict[str, str]]:
        selected: list[dict[str, str]] = []
        seen: set[str] = set()
        for sid in surface_ids:
            surf = _surface(str(sid or ''))
            if not surf:
                continue
            for artifact in (surf.get('artifacts') or []):
                if not isinstance(artifact, Mapping):
                    continue
                aid = str(artifact.get('id') or '')
                if not aid or aid in seen:
                    continue
                seen.add(aid)
                base = artifacts_by_id.get(aid) or artifact
                selected.append({
                    'id': aid,
                    'title': str(base.get('title') or artifact.get('title') or aid),
                    'path_hint': str(base.get('path_hint') or artifact.get('path_hint') or ''),
                    'install_hint': str(base.get('install_hint') or artifact.get('install_hint') or ''),
                    'category': str(base.get('category') or artifact.get('category') or ''),
                })
        return selected

    def _install_targets(surface_ids: Iterable[str]) -> list[str]:
        out: list[str] = []
        for sid in surface_ids:
            surf = _surface(str(sid or ''))
            if not surf:
                continue
            out.extend(str(x) for x in (surf.get('install_targets') or []) if str(x))
        return _dedupe_keep_order(out)

    def _first_wave(surface_ids: Iterable[str]) -> dict[str, Any]:
        candidates: list[dict[str, Any]] = []
        for sid in surface_ids:
            surf = _surface(str(sid or ''))
            if isinstance(surf, Mapping) and isinstance(surf.get('first_wave'), dict):
                candidates.append(dict(surf.get('first_wave') or {}))
        if not candidates:
            return {}
        return min(candidates, key=lambda item: int(item.get('order') or 999))

    def _priority(surface_ids: Iterable[str], default: str = 'medium') -> str:
        vals: list[str] = []
        for sid in surface_ids:
            surf = _surface(str(sid or ''))
            if not surf:
                continue
            val = str(surf.get('priority') or '')
            if val:
                vals.append(val)
        if not vals:
            return default
        vals.sort(key=_priority_rank)
        return vals[0]

    def _install_steps_for(
        *,
        category: str,
        entrypoints: list[str],
        targets: list[str],
        generator_commands: list[str],
        artifacts: list[dict[str, str]],
    ) -> list[str]:
        steps: list[str] = []
        if generator_commands:
            steps.append(f"Generate the required artifacts with: {generator_commands[0]}")
        if artifacts:
            first = artifacts[0]
            title = str(first.get('title') or '')
            path_hint = str(first.get('path_hint') or '')
            if title and path_hint:
                steps.append(f"Review the generated {title} at {path_hint} before installing it.")
            elif title:
                steps.append(f"Review the generated {title} before installing it.")
        if targets:
            steps.append(f"Install or stage the outputs at: {', '.join(targets[:3])}")
        if entrypoints:
            steps.append(f"Wire the runtime through: {entrypoints[0]}")
        if category == 'service':
            steps.append('Enable and restart the user service after staging the units so the watcher/bus surface survives terminal exits.')
        elif category == 'remap':
            steps.append('Treat the remapper/helper config as a boundary layer: install it separately from the VHK project and keep rollback notes nearby.')
        elif category == 'trigger':
            steps.append('Bind the generated trigger surface from the compositor/WM instead of hiding hotkey ownership inside ad-hoc shell wrappers.')
        elif category == 'audit':
            steps.append('Review the fallback and portal/helper notes before advertising broad desktop support.')
        elif category == 'debug':
            steps.append('Check the selector/debug assets into the repo so review and portability work use the same evidence.')
        elif category == 'text':
            steps.append('Prefer package-managed text expansion for reusable snippets instead of replay-only typing where the desktop allows it.')
        elif category == 'launcher':
            steps.append('Expose the project palette through explicit menu or launcher entrypoints when universal hotkeys are not the strongest surface.')
        return _dedupe_keep_order(steps)

    recipes: list[dict[str, Any]] = []

    def add_recipe(
        rid: str,
        title: str,
        *,
        category: str,
        audience: str,
        when_to_use: str,
        summary: str,
        surface_ids: Iterable[str],
        notes: Iterable[str] = (),
        playbook_ids: Iterable[str] = (),
        extra_install_steps: Iterable[str] = (),
        extra_verify_steps: Iterable[str] = (),
        extra_rollback_steps: Iterable[str] = (),
        default_priority: str = 'medium',
    ) -> None:
        surface_ids = [str(sid or '') for sid in surface_ids if str(sid or '')]
        selected_surfaces = [surfaces_by_id[sid] for sid in surface_ids if sid in surfaces_by_id]
        if not selected_surfaces:
            return

        capabilities = _caps_for_surfaces(surface_ids)
        artifacts = _artifact_refs(surface_ids)
        targets = _install_targets(surface_ids)
        selected_artifact_ids = [str(item.get('id') or '') for item in artifacts if str(item.get('id') or '')]
        generator_commands = _dedupe_keep_order([
            *[
                str(cmd)
                for aid in selected_artifact_ids
                for cmd in ((artifacts_by_id.get(aid) or {}).get('generator_commands') or [])
                if str(cmd)
            ],
        ])
        validation_commands = _dedupe_keep_order([
            *[
                str(cmd)
                for aid in selected_artifact_ids
                for cmd in ((artifacts_by_id.get(aid) or {}).get('validation_commands') or [])
                if str(cmd)
            ],
            *_gate_commands(capabilities),
        ])
        acceptance_checks = _dedupe_keep_order([
            *[str(note) for surf in selected_surfaces for note in (surf.get('acceptance_checks') or []) if str(note)],
            *_gate_checks(capabilities),
            *[str(step) for step in extra_verify_steps if str(step)],
        ])
        entrypoints = _dedupe_keep_order(str(surf.get('entrypoint') or '') for surf in selected_surfaces if str(surf.get('entrypoint') or ''))
        install_steps = _dedupe_keep_order([
            *_install_steps_for(
                category=category,
                entrypoints=entrypoints,
                targets=targets,
                generator_commands=generator_commands,
                artifacts=artifacts,
            ),
            *[str(step) for step in extra_install_steps if str(step)],
        ])
        rollback_steps = _dedupe_keep_order([
            *[str(step) for step in extra_rollback_steps if str(step)],
        ])
        if not rollback_steps:
            if category == 'service':
                rollback_steps = ['Disable the user service, stop it, and remove the generated unit files if the watcher surface causes regressions.']
            elif category == 'remap':
                rollback_steps = ['Disable the remapper/helper config first, then fall back to launcher or text-export surfaces while investigating low-level issues.']
            elif category == 'trigger':
                rollback_steps = ['Remove the compositor/WM bindings and keep launcher entrypoints as the safe fallback trigger path.']
            elif category == 'audit':
                rollback_steps = ['Treat missing capabilities as unsupported on that desktop until the audit pack is refreshed and re-verified.']
            else:
                rollback_steps = ['Remove the generated surface artifacts and return to the last verified launcher/text/debug baseline if the install proves fragile.']

        recipes.append({
            'id': rid,
            'title': title,
            'category': category,
            'audience': audience,
            'priority': _priority(surface_ids, default=default_priority),
            'when_to_use': when_to_use,
            'summary': summary,
            'surface_ids': surface_ids,
            'surfaces': [
                {
                    'id': str(surf.get('id') or ''),
                    'title': str(surf.get('title') or ''),
                    'category': str(surf.get('category') or ''),
                    'fit': str(surf.get('fit') or ''),
                    'entrypoint': str(surf.get('entrypoint') or ''),
                }
                for surf in selected_surfaces
            ],
            'artifacts': artifacts,
            'install_targets': targets[:5],
            'generator_commands': generator_commands[:8],
            'validation_commands': validation_commands[:8],
            'acceptance_checks': acceptance_checks[:6],
            'install_steps': install_steps[:6],
            'verify_steps': acceptance_checks[:6],
            'rollback_steps': rollback_steps[:4],
            'related_capabilities': capabilities,
            'first_wave': _first_wave(surface_ids),
            'playbooks': _playbook_titles(playbook_ids),
            'notes': _dedupe_keep_order([
                *[str(x) for x in notes if str(x)],
                *[str((surf.get('summary') or '')) for surf in selected_surfaces if str(surf.get('summary') or '')],
            ])[:5],
        })

    add_recipe(
        'text-package-install',
        'Install text automation package',
        category='text',
        audience='author/operator',
        when_to_use='The project has reusable text expansion, prompts, or snippet workflows that should be app-scoped and low-friction.',
        summary='Generate and stage text-package outputs so reusable snippets ride a Linux-native expansion layer instead of depending only on macro playback.',
        surface_ids=('text-automation',),
        extra_install_steps=('Register or restart the text expansion service after staging package files so the snippets become live in user space.',),
        extra_verify_steps=('Confirm the expansion works in at least one target application and one fallback/plain-text field.',),
        default_priority='high',
    )
    add_recipe(
        'launcher-entrypoint-install',
        'Install launcher and menu entrypoints',
        category='launcher',
        audience='operator',
        when_to_use='The safest cross-desktop trigger surface is an explicit launcher, menu item, or palette wrapper.',
        summary='Ship the project through launcher-visible entrypoints so discoverability and trigger ownership stay native even when global bindings vary by session.',
        surface_ids=('launcher-entrypoints',),
        extra_verify_steps=('Confirm the launcher entrypoint appears in the target menu/launcher and that it reaches the intended palette or macro flow.',),
        default_priority='medium',
    )
    add_recipe(
        'wm-trigger-install',
        'Install WM/compositor trigger layer',
        category='trigger',
        audience='operator',
        when_to_use='Low-latency dispatch matters and the target desktop has a strong compositor/WM-native binding surface.',
        summary='Push hotkey ownership into compositor-native bindings so the runtime stays focused on orchestration instead of inventing one universal hotkey stack.',
        surface_ids=('wm-trigger-layer',),
        playbook_ids=('hyprland-conservative', 'wlroots-sway-conservative'),
        extra_verify_steps=('Confirm the binding fires from the WM/compositor and still reaches the intended VHK macro path after a reload or login.',),
        default_priority='high',
    )
    add_recipe(
        'remap-helper-install',
        'Install remap/helper boundary',
        category='remap',
        audience='operator',
        when_to_use='The project needs always-on semantics, interception-heavy behavior, or a low-latency helper seam beyond ordinary launcher bindings.',
        summary='Treat remapper/helper configs as a separate install story so low-level key semantics stay explicit, auditable, and reversible.',
        surface_ids=('remap-helper-layer',),
        playbook_ids=('hyprland-conservative', 'wlroots-sway-conservative'),
        extra_verify_steps=('Verify that the helper path coexists with the target keyboard layout and that rollback instructions are tested before wider rollout.',),
        default_priority='medium',
    )
    add_recipe(
        'watcher-service-install',
        'Install watcher and bus services',
        category='service',
        audience='operator',
        when_to_use='Clipboard/window/bus/watcher automation should survive terminal exits and login sessions.',
        summary='Install the bus/watcher layer as user services so event-driven automation becomes an operating surface, not just a development shell habit.',
        surface_ids=('watcher-services',),
        extra_verify_steps=('Confirm the service starts cleanly on login and that event-driven flows still fire after the original authoring terminal is gone.',),
        default_priority='high',
    )
    add_recipe(
        'selector-debug-review',
        'Stage selector and debug asset pack',
        category='debug',
        audience='author/reviewer',
        when_to_use='The project depends on visual selectors, image matching, OCR tuning, or portability review across desktops.',
        summary='Treat needles, baselines, and selector samples as a checked-in deployment asset so review is evidence-driven instead of timing-driven.',
        surface_ids=('selector-debug-pack',),
        extra_verify_steps=('Open at least one selector asset path and run a selector-oriented validation command before claiming portability for a visual workflow.',),
        default_priority='high',
    )
    add_recipe(
        'capability-audit-review',
        'Review capability audit and fallback pack',
        category='audit',
        audience='author/reviewer',
        when_to_use='The project targets constrained Wayland desktops or claims helper/portal-backed behavior that needs explicit caveats.',
        summary='Package fallback notes and helper-boundary audits as part of the release story so desktop limits are visible before users discover them the hard way.',
        surface_ids=('capability-audit-pack',),
        playbook_ids=('hyprland-conservative', 'wlroots-sway-conservative'),
        extra_verify_steps=('Review at least one fallback path and one desktop-specific audit note before treating the capability as release-ready.',),
        default_priority='high',
    )

    recipes.sort(
        key=lambda item: (
            _priority_rank(str(item.get('priority') or 'medium')),
            int((item.get('first_wave') or {}).get('order') or 999),
            str(item.get('category') or ''),
            str(item.get('title') or ''),
        )
    )
    return recipes





def _stack_profiles(
    *,
    deployment_profiles: list[dict[str, Any]],
    desktop_targets: list[dict[str, Any]],
    overview: Mapping[str, Any],
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
) -> list[dict[str, Any]]:
    """Turn deployment profiles into a more explicitly product-shaped stack view.

    `deployment_profiles` already capture the core recommendation, but callers
    often want the answer in the language of product architecture: which layer
    is thin, which layer is stateful, and what sort of Linux-native ownership
    split a team should expect.
    """

    capability_usage = capability_usage or {}
    target_by_id = {str(item.get('id') or ''): dict(item) for item in desktop_targets}
    profile_to_target = {
        'text-first-export': 'portable-text-export',
        'selector-runner': 'x11-tiling-native',
        'watcher-daemon': 'wlroots-hyprland-conservative',
        'remap-integrated': 'helper-boundary-wayland',
        'wayland-helper-boundary': 'helper-boundary-wayland',
    }
    profile_meta: dict[str, dict[str, Any]] = {
        'text-first-export': {
            'product_shape': 'export-first',
            'thin_layers': ['hotstring trigger surface'],
            'stateful_layers': ['prompt-aware runner', 'parameter store'],
            'ownership_split': 'Let a text-expander own always-on expansion while VHK owns structured prompts, variables, and diagnostics.',
            'latency_class': 'always-on text triggers outside the runner',
            'why_linux_native': 'Matches the way Linux text tools package app scoping, forms, and service lifecycle separately from macro logic.',
            'borrow_from': ['Espanso forms/packages', 'launcher-friendly prompt presets'],
        },
        'selector-runner': {
            'product_shape': 'runner-first',
            'thin_layers': ['one-shot trigger entrypoint'],
            'stateful_layers': ['selector assets', 'vision waits', 'retry/diagnostic loop'],
            'ownership_split': 'Keep the complex timing, retries, and evidence collection inside VHK instead of pushing that state into compositor helpers.',
            'latency_class': 'interactive burst workload',
            'why_linux_native': 'Visual automation on Linux needs inspectable assets and debug evidence because raw desktop APIs stay uneven across sessions.',
            'borrow_from': ['Pulover-style recorder cleanup', 'AHK-style wait/retry diagnostics'],
        },
        'watcher-daemon': {
            'product_shape': 'service-first',
            'thin_layers': ['event emitters', 'socket/systemd activation'],
            'stateful_layers': ['bus daemon', 'macro runtime'],
            'ownership_split': 'Let the desktop or system service wake the automation; let VHK decide what to do once awake.',
            'latency_class': 'background service plane',
            'why_linux_native': 'Clipboard, DBus, and window changes behave more like service events than like classic hotkeys.',
            'borrow_from': ['service-managed automation', 'event bridge architecture'],
        },
        'remap-integrated': {
            'product_shape': 'split-brain trigger/runtime',
            'thin_layers': ['remapper or compositor bind'],
            'stateful_layers': ['macro orchestration', 'prompt/selector state'],
            'ownership_split': 'Keep interception and tap-hold logic in dedicated remappers, but keep macro meaning in VHK.',
            'latency_class': 'sub-gesture dispatch at the edge',
            'why_linux_native': 'evdev/uinput-class tools win by staying narrow and fast; VHK should consume them, not become them.',
            'borrow_from': ['keyd/kanata/KMonad trigger layers', 'xremap app-aware remap shape'],
        },
        'wayland-helper-boundary': {
            'product_shape': 'capability-audited adapter stack',
            'thin_layers': ['portal/compositor/helper adapters'],
            'stateful_layers': ['runner core', 'capability audit'],
            'ownership_split': 'Isolate pointer/injection/capture edges behind swappable helpers so the project does not hard-code one fragile Wayland path.',
            'latency_class': 'mixed: bursty input plus explicit session consent',
            'why_linux_native': 'Wayland automation is a capability matrix. The stable product surface is the contract between helpers and the runner, not one giant backend promise.',
            'borrow_from': ['portal session model', 'helper-boundary architecture', 'future libei seam'],
        },
    }

    profiles: list[dict[str, Any]] = []
    for item in deployment_profiles:
        profile = dict(item)
        profile_id = str(profile.get('id') or '')
        meta = profile_meta.get(profile_id, {})
        target = target_by_id.get(profile_to_target.get(profile_id, ''), {})
        usage_hints: list[str] = []
        if profile_id == 'text-first-export' and (overview.get('hotstrings') or capability_usage.get('text_injection')):
            usage_hints.append('Text triggers and parameterized macros should ship as an exported surface, not only as internal runner commands.')
        if profile_id == 'selector-runner' and capability_usage.get('screen_capture'):
            usage_hints.append('Selector assets and review traces are part of the runtime contract for visual macros.')
        if profile_id == 'watcher-daemon' and (overview.get('bus_watchers') or overview.get('clipboard_watchers') or overview.get('file_watchers') or overview.get('window_watchers')):
            usage_hints.append('Service ownership matters because event-driven automation should survive shell exits and login/session churn.')
        if profile_id in {'remap-integrated', 'wayland-helper-boundary'} and capability_usage.get('pointer_injection'):
            usage_hints.append('Keep pointer- or trigger-sensitive logic at a narrow boundary and route richer sequencing back into VHK.')

        profiles.append({
            'id': profile_id,
            'title': str(profile.get('title') or ''),
            'score': int(profile.get('score') or 0),
            'fit': str(profile.get('fit') or _fit_label(int(profile.get('score') or 0))),
            'summary': str(profile.get('summary') or ''),
            'product_shape': str(meta.get('product_shape') or 'mixed-stack'),
            'thin_layers': list(meta.get('thin_layers') or []),
            'stateful_layers': list(meta.get('stateful_layers') or []),
            'ownership_split': str(meta.get('ownership_split') or ''),
            'latency_class': str(meta.get('latency_class') or ''),
            'why_linux_native': str(meta.get('why_linux_native') or ''),
            'borrow_from': list(meta.get('borrow_from') or []),
            'trigger_surface': str(profile.get('trigger_surface') or ''),
            'execution_surface': str(profile.get('execution_surface') or ''),
            'export_surfaces': [str(x) for x in list(profile.get('export_surfaces') or []) if str(x)],
            'commands': [str(x) for x in list(profile.get('commands') or []) if str(x)],
            'evidence': [str(x) for x in list(profile.get('evidence') or []) if str(x)],
            'blocking_capabilities': [str(x) for x in list(profile.get('blocking_capabilities') or []) if str(x)],
            'best_target': {
                'id': str(target.get('id') or ''),
                'title': str(target.get('title') or ''),
                'fit': str(target.get('fit') or ''),
            },
            'usage_hints': usage_hints,
        })

    profiles.sort(key=lambda item: (-int(item.get('score') or 0), str(item.get('title') or '')))
    return profiles



def _runtime_seams(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
    capability_matrix: Mapping[str, Any] | None = None,
    stack_profiles: list[dict[str, Any]] | None = None,
    toolchain_choices: list[dict[str, Any]] | None = None,
    surface_choices: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Describe the recommended runtime seams/layers for the project.

    This is more explicit than architecture maps: it names which surfaces should
    stay thin and which should hold sequencing state.
    """

    backend = str(getattr(getattr(project, 'settings', None), 'desktop_backend', None) or '').strip().lower()
    capability_usage = capability_usage or {}
    stack_profiles = list(stack_profiles or [])
    toolchain_choices = list(toolchain_choices or [])
    surface_choices = list(surface_choices or [])
    root_dir = getattr(project, 'root_dir', None) or '.'
    root_q = shlex.quote(str(root_dir))

    top_profile = stack_profiles[0] if stack_profiles else {}
    text_usage = list(capability_usage.get('text_injection') or [])
    pointer_usage = list(capability_usage.get('pointer_injection') or [])
    capture_usage = list(capability_usage.get('screen_capture') or [])
    hotkey_usage = list(capability_usage.get('global_hotkeys') or [])

    seams: list[dict[str, Any]] = []

    def add(
        seam_id: str,
        title: str,
        *,
        layer_kind: str,
        fit: str = 'good',
        responsibility: str,
        why_split: str,
        owner: str,
        latency: str,
        contracts: list[str] | None = None,
        artifacts: list[str] | None = None,
        commands: list[str] | None = None,
        anchored_profiles: list[str] | None = None,
        notes: list[str] | None = None,
    ) -> None:
        seams.append({
            'id': seam_id,
            'title': title,
            'layer_kind': layer_kind,
            'fit': fit,
            'responsibility': responsibility,
            'why_split': why_split,
            'owner': owner,
            'latency_class': latency,
            'contracts': [str(x) for x in list(contracts or []) if str(x)],
            'artifacts': [str(x) for x in list(artifacts or []) if str(x)],
            'commands': [str(x) for x in list(commands or []) if str(x)],
            'anchored_profiles': [str(x) for x in list(anchored_profiles or []) if str(x)],
            'notes': [str(x) for x in list(notes or []) if str(x)],
        })

    add(
        'runner-core',
        'Runner core',
        layer_kind='runtime',
        fit='strong',
        responsibility='Own sequencing, waits, retries, variables, prompt forms, diagnostics, and macro meaning.',
        why_split='AHK-class usefulness comes from a strong runtime contract, not from pushing every capability into the trigger layer.',
        owner='VHK runtime',
        latency='stateful orchestration',
        contracts=['macro semantics stay stable across desktop backends', 'logging/diagnostics are available regardless of trigger surface'],
        artifacts=['macros/', 'event logs', 'trace/report outputs'],
        commands=[f'vhk run {root_q} <macro>', f'vhk report --project {root_q} --latest --json'],
        anchored_profiles=[str(top_profile.get('id') or '')] if top_profile else [],
    )

    trigger_notes = []
    if backend == 'wayland':
        trigger_notes.append('Prefer explicit exported surfaces over pretending one generic in-process hook will own every session.')
    if hotkey_usage or overview.get('bindings'):
        trigger_notes.append('Always-on hotkeys should stay reviewable because ownership shifts across X11, portals, compositors, and remappers.')
    add(
        'trigger-surface',
        'Trigger and dispatch surface',
        layer_kind='dispatch',
        fit='strong' if (overview.get('bindings') or overview.get('hotstrings') or hotkey_usage) else 'conditional',
        responsibility='Wake the right macro quickly through hotstrings, launcher entries, WM binds, remapper keys, or event emitters.',
        why_split='Linux trigger ownership is desktop-shaped; treating it as a thin seam keeps the runtime portable.',
        owner='desktop/native exports',
        latency='fast wake-up / always-on edge',
        contracts=['the trigger surface launches or emits into VHK without re-implementing macro logic', 'bindings remain reviewable per desktop'],
        artifacts=['WM bind snippets', 'launcher entries', 'remapper configs'],
        commands=[f'vhk palette {root_q}', f'vhk export-wm-bundle {root_q} --out-dir ./build/wm-bundle'],
        anchored_profiles=[p['id'] for p in stack_profiles if p.get('id') in {'text-first-export', 'remap-integrated', 'watcher-daemon', 'wayland-helper-boundary'}],
        notes=trigger_notes,
    )

    if overview.get('hotstrings') or text_usage or 'parameterized' in project_tags:
        add(
            'text-surface',
            'Text/export surface',
            layer_kind='export',
            fit='strong',
            responsibility='Ship snippets, forms, and return-value flows through text-native tooling while keeping structured logic in VHK.',
            why_split='Text automation wants app scoping, package layering, and service lifecycle that are better owned by a text surface than by the runner alone.',
            owner='text expander / launcher package',
            latency='always-on text expansion',
            contracts=['forms and presets map cleanly onto exported text actions', 'clipboard/plain-text fallback exists for conservative desktops'],
            artifacts=['espanso package', 'prompt profiles', 'palette entries'],
            commands=[f'vhk gen-espanso {root_q} --out-dir ./build/espanso', f'vhk plan-project {root_q} --json'],
            anchored_profiles=[p['id'] for p in stack_profiles if p.get('id') == 'text-first-export'],
            notes=['Treat text packaging as a product surface, not an afterthought.'],
        )

    if capture_usage or pointer_usage or 'selector-asset-heavy' in project_tags:
        add(
            'selector-asset-pack',
            'Selector and evidence pack',
            layer_kind='asset',
            fit='good',
            responsibility='Keep needles, OCR regions, previews, baselines, and review traces inspectable so visual macros are evidence-driven.',
            why_split='Visual automation becomes expensive quickly; shipping the evidence pack keeps cleanup and portability review grounded.',
            owner='repo-managed assets',
            latency='interactive debug asset loop',
            contracts=['every visual flow can point to at least one selector asset or preview artifact', 'report/preview commands stay usable on target desktops'],
            artifacts=['assets/', 'preview screenshots', 'debug docs'],
            commands=[f'vhk preview-needle path/to/needle.png --project {root_q} --haystack path/to/screenshot.png --json --no-check', f'vhk report --project {root_q} --latest --json'],
            anchored_profiles=[p['id'] for p in stack_profiles if p.get('id') in {'selector-runner', 'wayland-helper-boundary'}],
            notes=['Do not hide visual fragility behind extra sleeps.'],
        )

    if overview.get('bus_watchers') or overview.get('clipboard_watchers') or overview.get('file_watchers') or overview.get('window_watchers'):
        add(
            'watcher-service-plane',
            'Watcher/service plane',
            layer_kind='service',
            fit='good',
            responsibility='Keep DBus, clipboard, window, or bus-driven wake-up logic alive as a user-service surface.',
            why_split='Event-driven automation should survive terminal exits and session restarts, so the service boundary is part of the product.',
            owner='systemd user service / emitter stack',
            latency='background event plane',
            contracts=['watcher entrypoints can be restarted independently from macro logic', 'bus services have explicit start/status/logging paths'],
            artifacts=['systemd user units', 'bus/socket manifests'],
            commands=[f'vhk gen-vhk-busd-service {root_q} --out-dir ./build/systemd-user', f'vhk gen-vhk-busd-socket-units {root_q} --out-dir ./build/systemd-user'],
            anchored_profiles=[p['id'] for p in stack_profiles if p.get('id') == 'watcher-daemon'],
        )

    helper_needed = backend == 'wayland' and bool(pointer_usage or hotkey_usage or capture_usage)
    if helper_needed:
        pointer = capability_matrix.get('pointer_injection') if isinstance(capability_matrix, Mapping) else None
        hotkeys = capability_matrix.get('global_hotkeys') if isinstance(capability_matrix, Mapping) else None
        pointer_status = str(pointer.get('status') or 'unknown') if isinstance(pointer, Mapping) else 'unknown'
        hotkey_status = str(hotkeys.get('status') or 'unknown') if isinstance(hotkeys, Mapping) else 'unknown'
        rec_toolchains = [str(item.get('recommended_toolchain') or '') for item in toolchain_choices if str(item.get('recommended_toolchain') or '')]
        rec_toolchains = [x for x in rec_toolchains if x]
        add(
            'helper-boundary',
            'Helper / compositor boundary',
            layer_kind='adapter',
            fit='strong' if (pointer_usage or hotkey_usage) else 'conditional',
            responsibility='Constrain pointer injection, global shortcuts, capture helpers, and future libei/EIS experiments behind a narrow adapter seam.',
            why_split='Wayland capability churn is healthier when only the edge adapter changes and the macro/runtime contract does not.',
            owner='helper adapters + capability audit',
            latency='desktop-specific edge path',
            contracts=['helper-backed features must advertise fallback paths', 'session capability checks gate release claims'],
            artifacts=['capability audit notes', 'helper scripts/config', 'desktop target manifests'],
            commands=['vhk doctor --json', f'vhk validate {root_q} --json'],
            anchored_profiles=[p['id'] for p in stack_profiles if p.get('id') in {'wayland-helper-boundary', 'remap-integrated'}],
            notes=[f'pointer_injection={pointer_status}', f'global_hotkeys={hotkey_status}', *rec_toolchains[:3]],
        )

    seams.sort(key=lambda item: ({'runtime': 0, 'dispatch': 1, 'export': 2, 'asset': 3, 'service': 4, 'adapter': 5}.get(str(item.get('layer_kind') or ''), 9), str(item.get('title') or '')))
    return seams



def _host_requirements(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
    capability_matrix: Mapping[str, Any] | None = None,
    stack_profiles: list[dict[str, Any]] | None = None,
    toolchain_choices: list[dict[str, Any]] | None = None,
    surface_choices: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Describe host-side requirements that sit between package hints and runtime claims.

    This keeps service lifecycle, permissions, and portal-routing expectations
    visible in planner output instead of collapsing them into raw package names.
    """

    backend = str(getattr(getattr(project, 'settings', None), 'desktop_backend', None) or '').strip().lower()
    capability_usage = capability_usage or {}
    capability_matrix = capability_matrix or {}
    stack_profiles = list(stack_profiles or [])
    toolchain_choices = list(toolchain_choices or [])
    surface_choices = list(surface_choices or [])
    root_dir = getattr(project, 'root_dir', None) or '.'
    root_q = shlex.quote(str(root_dir))

    text_usage = list(capability_usage.get('text_injection') or [])
    pointer_usage = list(capability_usage.get('pointer_injection') or [])
    capture_usage = list(capability_usage.get('screen_capture') or [])
    hotkey_usage = list(capability_usage.get('global_hotkeys') or [])
    input_capture_usage = list(capability_usage.get('input_capture') or [])
    watcher_count = int(overview.get('bus_watchers') or 0) + int(overview.get('clipboard_watchers') or 0) + int(overview.get('file_watchers') or 0) + int(overview.get('window_watchers') or 0)

    def _dedupe_keep_order(values: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in values:
            value = str(item or '').strip()
            if not value or value in seen:
                continue
            seen.add(value)
            out.append(value)
        return out

    def _toolchain_tokens() -> set[str]:
        bits: list[str] = []
        for item in toolchain_choices:
            if not isinstance(item, Mapping):
                continue
            bits.extend([
                str(item.get('title') or ''),
                str(item.get('recommended_toolchain') or ''),
                str(item.get('category') or ''),
                str(item.get('capability') or ''),
                *[str(x) for x in list(item.get('fallback_toolchains') or []) if str(x)],
                *[str(x) for x in list(item.get('package_hints') or []) if str(x)],
                *[str(x) for x in list(item.get('learn_from') or []) if str(x)],
            ])
        return {bit.strip().lower() for bit in bits if bit and str(bit).strip()}

    def _surface_ids() -> set[str]:
        return {str(item.get('id') or '').strip() for item in surface_choices if isinstance(item, Mapping) and str(item.get('id') or '').strip()}

    def _profile_ids() -> set[str]:
        return {str(item.get('id') or '').strip() for item in stack_profiles if isinstance(item, Mapping) and str(item.get('id') or '').strip()}

    def _cap_status(name: str) -> str:
        item = capability_matrix.get(name) if isinstance(capability_matrix, Mapping) else None
        return str(item.get('status') or 'unknown').strip().lower() if isinstance(item, Mapping) else 'unknown'

    def _portal_backends(name: str) -> list[str]:
        item = capability_matrix.get(name) if isinstance(capability_matrix, Mapping) else None
        if isinstance(item, Mapping):
            return [str(x) for x in list(item.get('portal_backends') or []) if str(x)]
        return []

    tool_tokens = _toolchain_tokens()
    surface_ids = _surface_ids()
    profile_ids = _profile_ids()

    needs_text_surface = bool(overview.get('hotstrings') or text_usage or 'text-first-export' in profile_ids)
    needs_watcher_service = watcher_count > 0 or 'watcher-daemon' in profile_ids
    needs_remapper = bool(surface_ids.intersection({'keyd-remap', 'kanata-remap', 'kmonad-remap', 'xremap-remap'})) or 'remap-integrated' in profile_ids or any(token in tool_tokens for token in {'keyd', 'kanata', 'kmonad', 'xremap', 'helper/uinput seam'})
    needs_uinput = backend != 'x11' and (needs_remapper or bool(pointer_usage) or any(token in tool_tokens for token in {'ydotool', 'dotool', 'dotoolc', 'helper/uinput seam', 'libei-ready helper'}))
    needs_dotoold = backend != 'x11' and any(token in tool_tokens for token in {'dotool', 'dotoolc', 'helper/uinput seam'}) and (bool(pointer_usage) or bool(text_usage) or _cap_status('pointer_injection') in {'missing', 'limited'} or _cap_status('text_injection') in {'missing', 'limited'})
    needs_ydotool = backend != 'x11' and any(token in tool_tokens for token in {'ydotool', 'helper/uinput seam', 'libei-ready helper'}) and (bool(pointer_usage) or bool(text_usage) or _cap_status('pointer_injection') in {'missing', 'limited'} or _cap_status('text_injection') in {'missing', 'limited'})
    needs_portal_hotkeys = backend != 'x11' and bool(hotkey_usage or overview.get('bindings') or 'portal:GlobalShortcuts' in tool_tokens)
    needs_portal_capture = backend != 'x11' and bool(capture_usage or 'portal:Screenshot' in tool_tokens or 'portal:ScreenCast' in tool_tokens)
    needs_portal_remote_desktop = backend != 'x11' and bool(pointer_usage or text_usage or 'portal:RemoteDesktop(pointer)' in tool_tokens or 'portal:RemoteDesktop(keyboard)' in tool_tokens)
    needs_input_capture = backend != 'x11' and bool(input_capture_usage or 'portal:InputCapture' in tool_tokens)

    requirements: list[dict[str, Any]] = []

    def add(
        req_id: str,
        title: str,
        *,
        requirement_type: str,
        priority: str,
        capability: str | None = None,
        applies_when: str,
        why: str,
        packages: list[str] | None = None,
        services: list[str] | None = None,
        service_scope: str | None = None,
        groups: list[str] | None = None,
        paths: list[str] | None = None,
        portal_interfaces: list[str] | None = None,
        portal_backend_hints: list[str] | None = None,
        verify_commands: list[str] | None = None,
        fixup_hints: list[str] | None = None,
        risks: list[str] | None = None,
        evidence: list[str] | None = None,
        alternative_group: str | None = None,
        alternative_title: str | None = None,
        alternative_policy: str | None = None,
        alternative_order: int | None = None,
    ) -> None:
        requirements.append({
            'id': req_id,
            'title': title,
            'requirement_type': requirement_type,
            'priority': priority,
            'capability': capability,
            'applies_when': applies_when,
            'why': why,
            'packages': [str(x) for x in list(packages or []) if str(x)],
            'services': [str(x) for x in list(services or []) if str(x)],
            'service_scope': service_scope,
            'groups': [str(x) for x in list(groups or []) if str(x)],
            'paths': [str(x) for x in list(paths or []) if str(x)],
            'portal_interfaces': [str(x) for x in list(portal_interfaces or []) if str(x)],
            'portal_backend_hints': [str(x) for x in list(portal_backend_hints or []) if str(x)],
            'verify_commands': [str(x) for x in list(verify_commands or []) if str(x)],
            'fixup_hints': [str(x) for x in list(fixup_hints or []) if str(x)],
            'risks': [str(x) for x in list(risks or []) if str(x)],
            'evidence': [str(x) for x in list(evidence or []) if str(x)],
            'alternative_group': str(alternative_group).strip() if alternative_group else None,
            'alternative_title': str(alternative_title).strip() if alternative_title else None,
            'alternative_policy': str(alternative_policy).strip() if alternative_policy else None,
            'alternative_order': alternative_order,
        })

    if needs_text_surface:
        add(
            'text-surface-service',
            'Text surface lifecycle',
            requirement_type='service',
            priority='recommended' if overview.get('hotstrings') else 'conditional',
            capability='text_injection',
            applies_when='The project exports hotstrings or text-first prompt flows into an always-on text surface.',
            why='Linux text expanders and launcher-facing text surfaces usually own always-on background lifecycle separately from the macro runner.',
            packages=['espanso', 'wl-clipboard'] if backend != 'x11' else ['espanso'],
            services=['espanso'],
            service_scope='user',
            verify_commands=[f'vhk gen-espanso {root_q} --package-dir ./build/espanso_package', f'vhk validate {root_q} --json'],
            fixup_hints=['Register/start the text surface as a user-session service instead of assuming macros alone make it always-on.', 'Keep an unmanaged launcher path available for conservative desktops or packaging experiments.'],
            risks=['Wayland text support and app scoping differ from X11, so exported text packages still need desktop-specific review.'],
            evidence=[f"hotstrings={int(overview.get('hotstrings') or 0)}", f'text_usage={len(text_usage)}'],
        )

    if needs_watcher_service:
        add(
            'watcher-user-service',
            'Watcher / bus user service',
            requirement_type='service',
            priority='required',
            capability='global_hotkeys' if hotkey_usage else None,
            applies_when='The project has bus, clipboard, or window watchers that should survive shell exits and login churn.',
            why='Event-driven automation needs an explicit user-service boundary so the desktop can restart or supervise it separately from one-shot macro runs.',
            services=['vhk-busd'],
            service_scope='user',
            verify_commands=[f'vhk gen-vhk-busd-service {root_q} --out-dir ./build/systemd-user', f'vhk gen-vhk-busd-socket-units {root_q} --out-dir ./build/systemd-user'],
            fixup_hints=['Generate and review user service/socket units before claiming the watcher path is deployable.', 'Make sure the trigger entrypoint and the long-lived service use the same project root and environment.'],
            risks=['Terminal-owned watcher processes will disappear on logout or shell restart.'],
            evidence=[f'watchers={watcher_count}'],
        )

    if needs_dotoold:
        add(
            'dotool-daemon',
            'Persistent dotool daemon',
            requirement_type='service',
            priority='required' if pointer_usage else 'recommended',
            capability='pointer_injection' if pointer_usage else 'text_injection',
            applies_when='Wayland helper-backed input injection uses the dotoold/dotoolc uinput lane for repeated playback.',
            why='One-shot dotool has virtual-device registration overhead, so repeated automation is usually healthier when dotoold keeps devices alive and dotoolc does the per-step dispatch.',
            packages=['dotool'],
            services=['dotoold'],
            service_scope='user_or_system',
            verify_commands=['vhk doctor --json', f'vhk validate {root_q} --json'],
            fixup_hints=['Prefer dotoold + dotoolc for repeated key/pointer playback instead of spawning one-shot dotool for every macro edge.', 'Review `/dev/uinput` policy alongside daemon startup because the same helper boundary still depends on host permissions.'],
            risks=['Requires `/dev/uinput` access and host-specific service wiring.'],
            evidence=[f'pointer_status={_cap_status("pointer_injection")}', f'text_status={_cap_status("text_injection")}'],
            alternative_group='wayland-uinput-helper-daemon',
            alternative_title='Wayland uinput helper daemon lane',
            alternative_policy='one_of',
            alternative_order=0,
        )

    if needs_ydotool:
        add(
            'ydotool-daemon',
            'Persistent ydotool daemon',
            requirement_type='service',
            priority='required' if pointer_usage else 'recommended',
            capability='pointer_injection' if pointer_usage else 'text_injection',
            applies_when='Wayland helper-backed input injection falls back to ydotool-style uinput playback.',
            why='uinput-backed playback needs a long-lived virtual device so the desktop has time to recognize it before macro playback begins.',
            packages=['ydotool'],
            services=['ydotoold'],
            service_scope='user_or_system',
            paths=['$XDG_RUNTIME_DIR/.ydotool_socket', '/tmp/.ydotool_socket'],
            verify_commands=['vhk doctor --json', f'vhk validate {root_q} --json'],
            fixup_hints=['Run ydotoold as a deliberate service and review where its socket lives on the target host.', 'Treat the daemon as an adapter seam; do not bake its lifecycle into the runner core.'],
            risks=['Requires `/dev/uinput` access and host-specific service wiring.'],
            evidence=[f'pointer_status={_cap_status("pointer_injection")}', f'text_status={_cap_status("text_injection")}'],
            alternative_group='wayland-uinput-helper-daemon',
            alternative_title='Wayland uinput helper daemon lane',
            alternative_policy='one_of',
            alternative_order=1,
        )

    if needs_uinput:
        add(
            'uinput-permissions',
            'uinput / raw-input permissions',
            requirement_type='permission',
            priority='required' if pointer_usage or needs_remapper else 'recommended',
            capability='pointer_injection' if pointer_usage else 'text_injection',
            applies_when='The project leans on helper-backed injection or remapper exports that use evdev/uinput-class access.',
            why='Fast Linux-native remappers and helper injectors stay narrow and low-level, which makes device permissions and group policy part of the deployment surface.',
            groups=['uinput', 'input'],
            paths=['/dev/uinput', '/dev/input/event*'],
            verify_commands=['vhk doctor --json'],
            fixup_hints=['Prefer a narrowly scoped service account or dedicated group policy over broad ad-hoc privilege escalation.', 'Document the target host udev/group policy next to any remapper/helper configs.'],
            risks=['Granting input/uinput access increases the blast radius of untrusted code on the host.'],
            evidence=[f'remap_surface={str(needs_remapper).lower()}', f'pointer_usage={len(pointer_usage)}'],
        )

    if needs_remapper:
        remap_group = 'remapper-trigger-lane'
        remap_title = 'Remapper trigger lane'
        remap_policy = 'one_of'
        remap_surfaces = ', '.join(sorted(surface_ids.intersection({'keyd-remap', 'kanata-remap', 'kmonad-remap', 'xremap-remap'}))) or 'surface=none'

        add(
            'keyd-remapper-service',
            'keyd remapper daemon',
            requirement_type='service',
            priority='recommended',
            capability='global_hotkeys',
            applies_when='The project wants a low-latency system-wide remapper lane that stays close to evdev/uinput primitives.',
            why='keyd keeps interception small and display-server-agnostic, which makes it a strong default lane for desktop-wide remaps and launch keys.',
            packages=['keyd'],
            services=['keyd'],
            service_scope='system',
            verify_commands=[f'vhk gen-keyd-config {root_q} --out ./build/vhk.keyd.conf', 'vhk doctor --json'],
            fixup_hints=['Install keyd as a reviewed system service instead of hiding it inside ad-hoc login scripts.', 'Keep the generated keyd config separate from runtime-owned macro logic and note the rollback path.'],
            risks=['System-wide remapper daemons need explicit permission and rollback review because they sit close to input ownership.'],
            evidence=[f'bindings={int(overview.get("bindings") or 0)}', remap_surfaces],
            alternative_group=remap_group,
            alternative_title=remap_title,
            alternative_policy=remap_policy,
            alternative_order=0,
        )

        add(
            'kanata-remapper-service',
            'Kanata remapper service',
            requirement_type='service',
            priority='recommended',
            capability='global_hotkeys',
            applies_when='The project wants a programmable keyboard-first remapper lane with layers, tap-hold logic, or richer pre-macro key behavior.',
            why='Kanata is a strong fit when keyboard UX design matters as much as launch latency, but it still needs an explicit service/lifecycle contract.',
            packages=['kanata'],
            services=['kanata'],
            service_scope='user_or_system',
            verify_commands=[f'vhk gen-kanata-config {root_q} --out ./build/vhk.kanata.kbd', 'vhk doctor --json'],
            fixup_hints=['Decide whether Kanata should run as a user service, a system service, or via distro-native packaging before calling the lane done.', 'Do not let a Kanata config turn into a shadow macro engine for logic that belongs in VHK.'],
            risks=['Programmable remapper layers can hide deployment drift if service placement and config ownership are not reviewed.'],
            evidence=[f'bindings={int(overview.get("bindings") or 0)}', remap_surfaces],
            alternative_group=remap_group,
            alternative_title=remap_title,
            alternative_policy=remap_policy,
            alternative_order=1,
        )

        add(
            'xremap-remapper-service',
            'xremap remapper session',
            requirement_type='service',
            priority='recommended',
            capability='global_hotkeys',
            applies_when='The project wants app-aware remaps or key-sequence ownership that can ride an xremap-style Wayland/X11 lane.',
            why='xremap validates the app-aware remapper tier on Linux, especially for Wayland sessions where per-app context matters.',
            packages=['xremap'],
            services=['xremap'],
            service_scope='user_or_system',
            verify_commands=[f'vhk gen-xremap-config {root_q} --out ./build/vhk.xremap.yml', 'vhk doctor --json', f'vhk gen-route-selection-pack {root_q} --quiet'],
            fixup_hints=['Treat xremap as a reviewed session lane with explicit startup and focused-app context checks.', 'Validate compositor-specific application names before shipping app-aware xremap rules broadly.'],
            risks=['Wayland support can depend on desktop-specific features or extensions, so this lane still needs per-host review.'],
            evidence=[f'bindings={int(overview.get("bindings") or 0)}', remap_surfaces],
            alternative_group=remap_group,
            alternative_title=remap_title,
            alternative_policy=remap_policy,
            alternative_order=2,
        )

        add(
            'kmonad-remapper-service',
            'KMonad remapper service',
            requirement_type='service',
            priority='recommended',
            capability='global_hotkeys',
            applies_when='The project wants a deep keyboard-management lane and is willing to accept a more advanced config/debug story.',
            why='KMonad is powerful for advanced keyboard layering, but that power comes with more explicit setup and service management costs.',
            packages=['kmonad'],
            services=['kmonad'],
            service_scope='user_or_system',
            verify_commands=[f'vhk gen-kmonad-config {root_q} --out ./build/vhk.kmonad.kbd', 'vhk doctor --json'],
            fixup_hints=['Keep KMonad installs reversible and separate from the main runtime deploy so the keyboard layer can fail independently.', 'Capture the chosen service/user model in install docs because keyboard-manager setups drift easily.'],
            risks=['Advanced keyboard-manager setups can be harder to debug than a thinner remapper or WM bind export.'],
            evidence=[f'bindings={int(overview.get("bindings") or 0)}', remap_surfaces],
            alternative_group=remap_group,
            alternative_title=remap_title,
            alternative_policy=remap_policy,
            alternative_order=3,
        )

    if needs_portal_hotkeys:
        add(
            'portal-global-shortcuts',
            'GlobalShortcuts portal session',
            requirement_type='portal',
            priority='required' if _cap_status('global_hotkeys') in {'limited', 'missing'} else 'recommended',
            capability='global_hotkeys',
            applies_when='The project needs Wayland-friendly global hotkeys that stay outside compositor-specific config when possible.',
            why='Global shortcuts on Wayland are session-bound and configured through portal binding flows instead of behaving like a universal in-process hook.',
            portal_interfaces=['org.freedesktop.portal.GlobalShortcuts'],
            portal_backend_hints=_portal_backends('global_hotkeys'),
            verify_commands=['vhk doctor --json', f'vhk validate {root_q} --json'],
            fixup_hints=['Review whether the target desktop should use portal shortcuts, compositor binds, or launcher fallback as the primary trigger surface.', 'Treat the portal bind/configure step as part of installation, not just a runtime side effect.'],
            risks=['Desktop/version support varies, so keep a launcher or compositor-native fallback path available.'],
            evidence=[f'status={_cap_status("global_hotkeys")}'],
        )

    if needs_portal_capture:
        add(
            'portal-capture-routing',
            'Screenshot / screencast portal routing',
            requirement_type='portal',
            priority='required' if _cap_status('screen_capture') in {'limited', 'missing'} else 'recommended',
            capability='screen_capture',
            applies_when='The project uses screenshots, selectors, or visual waits on Wayland-class desktops.',
            why='Capture on Wayland is shaped by portal backend routing and consent, even when compositor-native fallbacks exist.',
            portal_interfaces=['org.freedesktop.portal.Screenshot', 'org.freedesktop.portal.ScreenCast'],
            portal_backend_hints=_dedupe_keep_order([*_portal_backends('screen_capture')]),
            verify_commands=['vhk doctor --json', f'vhk preview-needle path/to/needle.png --project {root_q} --haystack path/to/screenshot.png --json --no-check'],
            fixup_hints=['Surface which portal backend the host routes Screenshot/ScreenCast to before blaming visual flakiness on the runner.', 'Keep wlroots/desktop-native capture fallbacks available when portal coverage is incomplete.'],
            risks=['Consent and backend routing can change between desktops and even between hosts of the same distro.'],
            evidence=[f'status={_cap_status("screen_capture")}', f'capture_usage={len(capture_usage)}'],
        )

    if needs_portal_remote_desktop:
        add(
            'portal-remote-desktop',
            'RemoteDesktop portal review',
            requirement_type='portal',
            priority='recommended' if _cap_status('pointer_injection') == 'ok' else 'required',
            capability='pointer_injection' if pointer_usage else 'text_injection',
            applies_when='The project needs a permissioned Wayland fallback for pointer or keyboard injection.',
            why='RemoteDesktop is a session/consent-based fallback, not a permanent always-on substitute for low-latency remappers or helper daemons.',
            portal_interfaces=['org.freedesktop.portal.RemoteDesktop'],
            portal_backend_hints=_dedupe_keep_order([*_portal_backends('pointer_injection'), *_portal_backends('text_injection')]),
            verify_commands=['vhk doctor --json', f'vhk validate {root_q} --json'],
            fixup_hints=['Decide explicitly whether the host should use portal-mediated consent flows or a helper/uinput seam for this project.', 'Keep portal-backed injection claims conservative because device availability and consent are session-specific.'],
            risks=['Pointer/keyboard availability can be partial even when the portal interface exists.'],
            evidence=[f'pointer_status={_cap_status("pointer_injection")}', f'text_status={_cap_status("text_injection")}'],
        )

    if needs_input_capture:
        add(
            'portal-input-capture',
            'InputCapture / libei seam',
            requirement_type='portal',
            priority='conditional',
            capability='input_capture',
            applies_when='The project explores true input capture instead of only trigger/export surfaces.',
            why='InputCapture on Wayland is asynchronous, trigger-based, and explicitly routed through libei/EIS transport rather than immediate capture.',
            portal_interfaces=['org.freedesktop.portal.InputCapture'],
            portal_backend_hints=_portal_backends('input_capture'),
            verify_commands=['vhk doctor --json', f'vhk plan-project {root_q} --json'],
            fixup_hints=['Treat input capture as a dedicated helper seam with explicit trigger logic and release claims.', 'Do not promise immediate capture semantics on desktops that only expose the portal contract.'],
            risks=['The portal only manages capture enable/disable state; actual transport and activation timing stay outside the runner.'],
            evidence=[f'status={_cap_status("input_capture")}', f'usage={len(input_capture_usage)}'],
        )

    if backend != 'x11' and (needs_portal_hotkeys or needs_portal_capture or needs_portal_remote_desktop or needs_input_capture):
        add(
            'portal-backend-config',
            'Portal backend routing config',
            requirement_type='portal',
            priority='recommended',
            applies_when='The project depends on one or more portal interfaces and the target host may have multiple backends installed.',
            why='On Linux, portal support is not just an API question. Backend routing is configured per interface and may differ by desktop or host overrides.',
            portal_interfaces=_dedupe_keep_order([
                *(['org.freedesktop.portal.GlobalShortcuts'] if needs_portal_hotkeys else []),
                *(['org.freedesktop.portal.Screenshot', 'org.freedesktop.portal.ScreenCast'] if needs_portal_capture else []),
                *(['org.freedesktop.portal.RemoteDesktop'] if needs_portal_remote_desktop else []),
                *(['org.freedesktop.portal.InputCapture'] if needs_input_capture else []),
            ]),
            portal_backend_hints=_dedupe_keep_order([*_portal_backends('global_hotkeys'), *_portal_backends('screen_capture'), *_portal_backends('pointer_injection'), *_portal_backends('text_injection'), *_portal_backends('input_capture')]),
            verify_commands=['vhk doctor --json'],
            fixup_hints=['Review `portals.conf` and desktop-specific backend overrides before declaring portal coverage stable.', 'Capture the chosen backend routing in support/install docs so operators are not forced to rediscover it.'],
            risks=['Installing a portal package does not guarantee the right backend is selected for the interfaces this project needs.'],
            evidence=[backend or 'backend=auto'],
        )

    requirements.sort(key=lambda item: ({'required': 0, 'recommended': 1, 'conditional': 2}.get(str(item.get('priority') or ''), 9), {'service': 0, 'permission': 1, 'portal': 2}.get(str(item.get('requirement_type') or ''), 9), str(item.get('title') or '')))
    return requirements


def _activation_routes(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    macro_profiles: list[dict[str, Any]] | None = None,
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
    capability_matrix: Mapping[str, Any] | None = None,
    stack_profiles: list[dict[str, Any]] | None = None,
    runtime_seams: list[dict[str, Any]] | None = None,
    host_requirements: list[dict[str, Any]] | None = None,
    surface_choices: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Describe concrete Linux activation lanes for the project."""

    backend = str(getattr(getattr(project, 'settings', None), 'desktop_backend', None) or '').strip().lower()
    capability_usage = capability_usage or {}
    stack_profiles = list(stack_profiles or [])
    runtime_seams = list(runtime_seams or [])
    host_requirements = list(host_requirements or [])
    surface_choices = list(surface_choices or [])
    root_dir = getattr(project, 'root_dir', None) or '.'
    root_q = shlex.quote(str(root_dir))

    seam_ids = {str(item.get('id') or '').strip() for item in runtime_seams if isinstance(item, Mapping)}
    surface_ids = {str(item.get('id') or '').strip() for item in surface_choices if isinstance(item, Mapping)}
    requirement_map = {
        str(item.get('id') or '').strip(): dict(item)
        for item in host_requirements
        if isinstance(item, Mapping) and str(item.get('id') or '').strip()
    }
    alternative_group_map: dict[str, dict[str, Any]] = {}
    for raw_requirement in requirement_map.values():
        group_id = str(raw_requirement.get('alternative_group') or '').strip()
        if not group_id:
            continue
        group = alternative_group_map.setdefault(
            group_id,
            {
                'id': group_id,
                'title': str(raw_requirement.get('alternative_title') or group_id).strip() or group_id,
                'policy': str(raw_requirement.get('alternative_policy') or 'one_of').strip() or 'one_of',
                'capability': str(raw_requirement.get('capability') or '').strip() or None,
                'members': [],
            },
        )
        group['members'].append(dict(raw_requirement))
    for group in alternative_group_map.values():
        members = [dict(item) for item in list(group.get('members') or []) if isinstance(item, Mapping)]
        members.sort(
            key=lambda item: (
                int(item.get('alternative_order')) if item.get('alternative_order') is not None else 999,
                {'required': 0, 'recommended': 1, 'conditional': 2}.get(str(item.get('priority') or 'conditional'), 2),
                str(item.get('title') or item.get('id') or ''),
            )
        )
        group['members'] = members
        preferred_member = members[0] if members else None
        group['preferred_member_id'] = str((preferred_member or {}).get('id') or '').strip() or None
        group['preferred_member_title'] = str((preferred_member or {}).get('title') or (preferred_member or {}).get('id') or '').strip() or None
    top_profile_ids = [str(item.get('id') or '').strip() for item in stack_profiles[:3] if str(item.get('id') or '').strip()]

    text_usage = list(capability_usage.get('text_injection') or [])
    pointer_usage = list(capability_usage.get('pointer_injection') or [])
    capture_usage = list(capability_usage.get('screen_capture') or [])
    hotkey_usage = list(capability_usage.get('global_hotkeys') or [])
    input_capture_usage = list(capability_usage.get('input_capture') or [])
    portal_catalog = _portal_shortcut_catalog_analysis(
        project=project,
        macro_profiles=macro_profiles,
        capability_usage=capability_usage,
    )
    stable_portal_bindings = int(portal_catalog.get('stable_binding_count') or 0)
    dynamic_portal_bindings = int(portal_catalog.get('dynamic_binding_count') or 0)

    routes: list[dict[str, Any]] = []

    def add(
        route_id: str,
        title: str,
        *,
        activation_kind: str,
        startup_owner: str,
        steady_state: str,
        entrypoint: str,
        why: str,
        fit: str = 'good',
        commands: list[str] | None = None,
        verification_commands: list[str] | None = None,
        depends_on_requirements: list[str] | None = None,
        depends_on_alternative_groups: list[str] | None = None,
        depends_on_seams: list[str] | None = None,
        related_surface_ids: list[str] | None = None,
        fallback_routes: list[str] | None = None,
        notes: list[str] | None = None,
        evidence: list[str] | None = None,
    ) -> None:
        requirement_ids = [
            str(x) for x in list(depends_on_requirements or [])
            if str(x) and str(x) in requirement_map
        ]
        alternative_group_ids = [
            str(x) for x in list(depends_on_alternative_groups or [])
            if str(x) and str(x) in alternative_group_map
        ]
        alternative_groups = [dict(alternative_group_map[group_id]) for group_id in alternative_group_ids]
        routes.append(
            {
                'id': route_id,
                'title': title,
                'activation_kind': activation_kind,
                'fit': fit,
                'startup_owner': startup_owner,
                'steady_state': steady_state,
                'entrypoint': entrypoint,
                'why': why,
                'commands': [str(x) for x in list(commands or []) if str(x)],
                'verification_commands': [str(x) for x in list(verification_commands or []) if str(x)],
                'depends_on_requirements': requirement_ids,
                'depends_on_alternative_groups': alternative_group_ids,
                'depends_on_seams': [str(x) for x in list(depends_on_seams or []) if str(x) and str(x) in seam_ids],
                'related_surface_ids': [str(x) for x in list(related_surface_ids or []) if str(x) and str(x) in surface_ids],
                'fallback_routes': [str(x) for x in list(fallback_routes or []) if str(x)],
                'notes': [str(x) for x in list(notes or []) if str(x)],
                'evidence': [str(x) for x in list(evidence or []) if str(x)],
                'anchored_profiles': list(top_profile_ids),
                'requirements': [
                    {
                        'id': req_id,
                        'title': str((requirement_map.get(req_id) or {}).get('title') or req_id),
                        'priority': str((requirement_map.get(req_id) or {}).get('priority') or ''),
                        'type': str((requirement_map.get(req_id) or {}).get('requirement_type') or ''),
                        'capability': str((requirement_map.get(req_id) or {}).get('capability') or ''),
                    }
                    for req_id in requirement_ids
                ],
                'alternative_requirement_groups': alternative_groups,
            }
        )

    add(
        'launcher-entrypoint',
        'Launcher / palette entrypoint',
        activation_kind='launcher',
        fit='strong',
        startup_owner='desktop launcher / shell / operator',
        steady_state='on-demand',
        entrypoint='vhk palette / desktop entry / launcher wrapper',
        why='Every Linux target needs one honest wake-up path that does not depend on low-level hooks or always-on daemons.',
        commands=[f'vhk palette {root_q}', f'vhk gen-desktop-entry {root_q}'],
        verification_commands=[f'vhk validate {root_q} --json'],
        depends_on_seams=['runner-core'],
        related_surface_ids=['launcher-entrypoints'],
        notes=['Treat this as the universal fallback route when hotter trigger surfaces are desktop-specific or blocked.'],
        evidence=[backend or 'backend=auto', f'macros={int(overview.get("macros") or 0)}'],
    )

    if overview.get('bindings') or hotkey_usage:
        add(
            'native-trigger-route',
            'Native trigger route',
            activation_kind='desktop_config',
            fit='strong' if backend in {'x11', 'wayland'} else 'good',
            startup_owner='WM/compositor config or launcher mode',
            steady_state='always-on desktop binding',
            entrypoint='window-manager bindings / launcher mode / explicit hotkey surface',
            why='Trigger ownership should stay thin and close to the desktop so VHK keeps orchestration state instead of becoming the hotkey daemon.',
            commands=[f'vhk export-wm-bundle {root_q} --out-dir ./build/wm-bundle', f'vhk gen-trigger-pack {root_q} --quiet'],
            verification_commands=[f'vhk plan-project {root_q} --json', f'vhk validate {root_q} --json'],
            depends_on_seams=['runner-core', 'trigger-surface'],
            related_surface_ids=['wm-trigger-layer', 'launcher-entrypoints'],
            fallback_routes=['launcher-entrypoint'],
            notes=['Prefer compositor/WM-native bindings before inventing one universal hotkey stack inside the runner.'],
            evidence=[f'bindings={int(overview.get("bindings") or 0)}', backend or 'backend=auto'],
        )

    if 'text-surface' in seam_ids or overview.get('hotstrings') or text_usage:
        add(
            'text-surface-route',
            'Text surface route',
            activation_kind='user_service',
            fit='strong',
            startup_owner='text expander / service manager',
            steady_state='always-on text expansion',
            entrypoint='espanso package / hotstring surface / prompted text entrypoint',
            why='Text expansion and prompt-backed snippets usually live best as a service-managed surface rather than as pure playback macros.',
            commands=[f'vhk gen-espanso {root_q} --out-dir ./build/espanso', f'vhk gen-setup-pack {root_q} --quiet'],
            verification_commands=[f'vhk validate {root_q} --json', f'vhk plan-project {root_q} --json'],
            depends_on_requirements=['text-surface-service'],
            depends_on_seams=['runner-core', 'text-surface'],
            related_surface_ids=['text-automation', 'launcher-entrypoints'],
            fallback_routes=['launcher-entrypoint'],
            notes=['Treat forms, presets, and app-scoped snippets as part of the text surface lifecycle.'],
            evidence=[f'hotstrings={int(overview.get("hotstrings") or 0)}', f'text_usage={len(text_usage)}'],
        )

    if 'watcher-service-plane' in seam_ids or overview.get('bus_watchers') or overview.get('clipboard_watchers') or overview.get('file_watchers') or overview.get('window_watchers'):
        add(
            'watcher-service-route',
            'Watcher / bus service route',
            activation_kind='user_service',
            fit='good',
            startup_owner='systemd user service or socket-activated service',
            steady_state='background event plane',
            entrypoint='vhk-busd service / emitted events / watcher restart loop',
            why='Event-driven automation should survive shell exits and session churn, so watcher ownership needs a restartable service lane.',
            commands=[f'vhk gen-vhk-busd-service {root_q} --out-dir ./build/systemd-user', f'vhk gen-vhk-busd-socket-units {root_q} --out-dir ./build/systemd-user'],
            verification_commands=[f'vhk doctor --json', f'vhk plan-project {root_q} --json'],
            depends_on_requirements=['watcher-user-service'],
            depends_on_seams=['runner-core', 'watcher-service-plane'],
            related_surface_ids=['watcher-services'],
            fallback_routes=['launcher-entrypoint'],
            notes=['Socket activation and non-systemd equivalents should stay possible without changing macro logic.'],
            evidence=[
                f'bus_watchers={int(overview.get("bus_watchers") or 0)}',
                f'clipboard_watchers={int(overview.get("clipboard_watchers") or 0)}',
                f'file_watchers={int(overview.get("file_watchers") or 0)}',
                f'window_watchers={int(overview.get("window_watchers") or 0)}',
            ],
        )

    if backend != 'x11' and 'portal-global-shortcuts' in requirement_map:
        portal_fit = 'good' if stable_portal_bindings and stable_portal_bindings >= dynamic_portal_bindings else 'conditional'
        add(
            'portal-shortcuts-route',
            'Portal shortcut session route',
            activation_kind='portal_session',
            fit=portal_fit,
            startup_owner='portal session + desktop consent/configure flow',
            steady_state='session-bound',
            entrypoint='org.freedesktop.portal.GlobalShortcuts session + bindings',
            why='Portal-managed shortcuts are session objects, so VHK should treat them as an explicit route for stable action catalogs instead of assuming they behave like always-on in-process hooks.',
            commands=[f'vhk doctor --json', f'vhk gen-portal-shortcuts-spec {root_q} --out ./build/vhk.portal-shortcuts.yml', f'vhk gen-host-contract-pack {root_q} --quiet'],
            verification_commands=[f'vhk doctor --json', f'vhk validate {root_q} --json'],
            depends_on_requirements=['portal-global-shortcuts', 'portal-backend-config'],
            depends_on_seams=['trigger-surface'],
            related_surface_ids=['wm-trigger-layer', 'launcher-entrypoints'],
            fallback_routes=['native-trigger-route', 'launcher-entrypoint'],
            notes=[
                'Keep a launcher or compositor-native fallback because portal availability and binding UX vary by desktop.',
                'Prefer this route for predeclared shortcut catalogs, not for every helper-sensitive or rapidly changing hotkey in the repo.',
            ],
            evidence=[backend or 'backend=auto', f'global_hotkey_usage={len(hotkey_usage)}', f'stable_shortcut_candidates={stable_portal_bindings}', f'dynamic_shortcut_candidates={dynamic_portal_bindings}'],
        )

    needs_remap_route = bool((overview.get('bindings') or 0) and ('helper-boundary' in seam_ids or 'remap-helper-layer' in surface_ids or input_capture_usage))
    if needs_remap_route:
        add(
            'remapper-route',
            'Remapper / low-latency key route',
            activation_kind='system_or_user_service',
            fit='conditional',
            startup_owner='remapper daemon / dedicated service user / low-latency key layer',
            steady_state='always-on interception layer',
            entrypoint='keyd / kanata / kmonad / equivalent remapper config',
            why='Low-latency key ownership often belongs in a remapper tier, but macro meaning and diagnostics should stay inside VHK.',
            commands=[f'vhk gen-trigger-pack {root_q} --quiet', f'vhk gen-host-contract-pack {root_q} --quiet'],
            verification_commands=[f'vhk doctor --json', f'vhk validate {root_q} --json'],
            depends_on_requirements=['uinput-permissions'],
            depends_on_alternative_groups=['remapper-trigger-lane'],
            depends_on_seams=['trigger-surface', 'helper-boundary'],
            related_surface_ids=['remap-helper-layer', 'wm-trigger-layer'],
            fallback_routes=['native-trigger-route', 'launcher-entrypoint'],
            notes=['Keep service-user, placement, and restart policy reviewable instead of pretending config generation is the whole deployment story.'],
            evidence=[f'bindings={int(overview.get("bindings") or 0)}', f'input_capture_usage={len(input_capture_usage)}'],
        )

    needs_helper_route = bool(pointer_usage or capture_usage or ('helper-boundary' in seam_ids and backend == 'wayland'))
    if needs_helper_route:
        reqs = ['uinput-permissions']
        alt_groups: list[str] = []
        if 'wayland-uinput-helper-daemon' in alternative_group_map:
            alt_groups.append('wayland-uinput-helper-daemon')
        elif 'dotool-daemon' in requirement_map:
            reqs.append('dotool-daemon')
        elif 'ydotool-daemon' in requirement_map:
            reqs.append('ydotool-daemon')
        if 'portal-remote-desktop' in requirement_map and backend != 'x11':
            reqs.append('portal-remote-desktop')
        if 'portal-backend-config' in requirement_map and backend != 'x11':
            reqs.append('portal-backend-config')
        add(
            'helper-input-route',
            'Helper / injected input route',
            activation_kind='helper_daemon',
            fit='conditional' if backend == 'wayland' else 'good',
            startup_owner='helper daemon / socket / capability-audited adapter',
            steady_state='background adapter or on-demand helper bridge',
            entrypoint='preferred helper daemon (`dotoold` / `ydotoold`) or portal-mediated injection fallback',
            why='Pointer and injected-input edges churn faster than macro logic, so the activation seam should stay narrow and replaceable.',
            commands=[f'vhk doctor --json', f'vhk gen-readiness-pack {root_q} --quiet'],
            verification_commands=[f'vhk doctor --json', f'vhk plan-project {root_q} --json'],
            depends_on_requirements=reqs,
            depends_on_alternative_groups=alt_groups,
            depends_on_seams=['runner-core', 'helper-boundary'],
            related_surface_ids=['remap-helper-layer', 'selector-debug-pack'],
            fallback_routes=['launcher-entrypoint'],
            notes=['Treat helper sockets, portal consent, and uinput access as host contract edges, not as runner internals.', 'When multiple Wayland helper daemons are viable, pick one reviewed lane and bootstrap filter instead of treating every helper as additive.'],
            evidence=[f'pointer_usage={len(pointer_usage)}', f'capture_usage={len(capture_usage)}', backend or 'backend=auto'],
        )

    order = {
        'launcher': 0,
        'desktop_config': 1,
        'portal_session': 2,
        'user_service': 3,
        'system_or_user_service': 4,
        'helper_daemon': 5,
    }
    routes.sort(key=lambda item: (order.get(str(item.get('activation_kind') or ''), 9), str(item.get('title') or '')))
    return routes


def _is_remap_like_macro_profile(item: Mapping[str, Any] | None) -> bool:
    item = item or {}
    step_count = int(item.get('step_count') or 0)
    if step_count <= 0 or step_count > 8:
        return False

    counts = item.get('feature_counts') or {}
    blocked = (
        int(counts.get('screen') or 0)
        or int(counts.get('pointer') or 0)
        or int(counts.get('window') or 0)
        or int(counts.get('prompt') or 0)
        or int(counts.get('process') or 0)
        or int(counts.get('data') or 0)
        or int(counts.get('watch') or 0)
        or int(counts.get('vision_wait') or 0)
    )
    if blocked:
        return False

    step_types = {str(key or '') for key in ((item.get('step_type_counts') or {}).keys())}
    allowed = {'Key', 'KeyDown', 'KeyUp', 'ResetModifiers', 'Delay'}
    if not step_types or any(step_type not in allowed for step_type in step_types):
        return False

    tags = {str(x or '') for x in (item.get('tags') or [])}
    if 'parameterized' in tags or 'flow-heavy' in tags or 'event-driven' in tags:
        return False

    return True


def _macro_route_profiles(
    *,
    project,
    overview: Mapping[str, Any],
    macro_profiles: list[dict[str, Any]],
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
    capability_matrix: Mapping[str, Any] | None = None,
    activation_routes: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    capability_usage = capability_usage or {}
    capability_matrix = capability_matrix or {}
    activation_routes = list(activation_routes or [])
    backend = str(getattr(getattr(project, 'settings', None), 'desktop_backend', None) or '').strip().lower()
    root_q = shlex.quote(str(getattr(project, 'root_dir', '.') or '.'))

    usage_by_macro: dict[str, set[str]] = defaultdict(set)
    for capability_name, refs in capability_usage.items():
        for ref in refs or []:
            if not isinstance(ref, Mapping):
                continue
            macro_name = str(ref.get('macro') or '').strip()
            if macro_name:
                usage_by_macro[macro_name].add(str(capability_name))

    activation_by_id: dict[str, dict[str, Any]] = {
        str(item.get('id') or ''): dict(item)
        for item in activation_routes
        if isinstance(item, Mapping) and str(item.get('id') or '').strip()
    }
    portal_catalog = _portal_shortcut_catalog_analysis(
        project=project,
        macro_profiles=macro_profiles,
        capability_usage=capability_usage,
    )

    def pick_activation(candidates: list[str]) -> tuple[str, dict[str, Any] | None]:
        ranked: list[tuple[int, int, str]] = []
        for index, route_id in enumerate(candidates):
            item = activation_by_id.get(str(route_id))
            if not isinstance(item, Mapping):
                continue
            status = str(item.get('route_status') or '')
            status_rank = {'ready': 0, 'planned': 1, 'degraded': 2}.get(status, 3)
            ranked.append((status_rank, index, str(route_id)))
        if not ranked:
            return '', None
        ranked.sort()
        route_id = ranked[0][2]
        item = activation_by_id.get(route_id)
        return route_id, dict(item) if isinstance(item, Mapping) else None

    def fit_for_route(base: str, route: Mapping[str, Any] | None) -> str:
        base_rank = {'weak': 0, 'conditional': 1, 'good': 2, 'strong': 3}.get(str(base or 'good'), 2)
        status = str((route or {}).get('route_status') or '')
        status_cap = {'degraded': 1, 'planned': 2, 'ready': 3}.get(status, 2)
        rank = min(base_rank, status_cap)
        return {0: 'weak', 1: 'conditional', 2: 'good', 3: 'strong'}.get(rank, 'good')

    rows: list[dict[str, Any]] = []
    for item in macro_profiles:
        name = str(item.get('macro') or '')
        if not name:
            continue
        tags = {str(x or '') for x in (item.get('tags') or [])}
        triggers = {str(x or '') for x in (item.get('triggers') or [])}
        perf = item.get('performance') or {}
        capabilities = sorted(str(x) for x in usage_by_macro.get(name) or [])
        has_hotkey = 'hotkey' in triggers
        has_hotstring = 'hotstring' in triggers
        has_watcher = any(x.endswith('watcher') for x in triggers)
        palette_only = bool(triggers) and triggers == {'palette'}
        remap_like = _is_remap_like_macro_profile(item)
        helper_sensitive = backend == 'wayland' and any(x in {'pointer_injection', 'screen_capture', 'input_capture'} for x in capabilities)
        portal_catalog_macro = backend == 'wayland' and _is_portal_catalog_macro(name, portal_catalog=portal_catalog)

        route_id = 'runner-core'
        title = 'Runner-core macro'
        owner_layer = 'runner core'
        execution_surface = 'VHK runner with normal sequencing and diagnostics'
        summary = 'Keep this macro in the main runner so it can use waits, variables, prompts, and diagnostics directly.'
        why = 'This macro does enough real automation work that collapsing it into a remapper or phrase layer would hide state and make Linux portability less honest.'
        learn_from = ['AutoHotkey', 'Pulover\'s Macro Creator']
        commands = [f'vhk optimize-project {root_q}', f'vhk gen-verification-pack {root_q} --quiet']
        evidence = [f"{int(item.get('step_count') or 0)} step(s)"]
        risks: list[str] = []
        activation_candidates = ['launcher-entrypoint']
        base_fit = 'good'

        if remap_like and (has_hotkey or 'global_hotkeys' in capabilities):
            route_id = 'remapper-tier'
            title = 'Remapper-tier macro'
            owner_layer = 'remapper/helper layer'
            execution_surface = 'keyd / kanata / xremap-class remapper export with VHK fallback'
            summary = 'This macro looks closer to a low-latency key transform than to a full automation program.'
            why = 'Linux remapper tools stay closer to evdev/compositor timing and usually provide better always-on key behavior than a general-purpose runner.'
            learn_from = ['keyd', 'xremap', 'kanata']
            commands = [
                f'vhk gen-keyd-config {root_q} --out ./build/vhk.keyd.conf',
                f'vhk gen-xremap-config {root_q} --out ./build/vhk.xremap.yml',
            ]
            evidence.append('remap-like key-only step shape')
            if 'window_introspection' in capabilities:
                evidence.append('window/app scope requested')
                risks.append('app-specific remap scope still depends on backend-specific selectors and helper support')
            activation_candidates = ['remapper-route', 'native-trigger-route', 'launcher-entrypoint']
            base_fit = 'strong' if backend != 'wayland' else 'good'
        elif has_hotstring or 'text-expander' in tags:
            route_id = 'text-tier'
            title = 'Text-tier macro'
            owner_layer = 'text tier'
            execution_surface = 'VHK hotstring / Espanso-style text package / clipboard-friendly lane'
            summary = 'Route this macro through the fast text tier first, then fall back to the full runner only when prompts or richer orchestration are needed.'
            why = 'Text expansion on Linux benefits from dedicated phrase/package semantics, app filters, and clipboard-aware throughput instead of replaying everything as heavyweight macro execution.'
            learn_from = ['Espanso', 'AutoKey']
            commands = [
                f'vhk gen-espanso {root_q} --package-dir ./build/espanso_package',
                f'vhk optimize-project {root_q}',
            ]
            if backend in {'x11', 'i3'}:
                commands.insert(1, f'vhk gen-autokey-pack {root_q} --out-dir ./build/autokey_pack')
            evidence.append('hotstring/text-expander trigger')
            if int(perf.get('structured_literal_type_steps') or 0) > 0:
                evidence.append('structured typed-text body present')
                risks.append('tab/enter-rich snippets should usually use the hybrid clipboard/text lane on Linux')
            if int(perf.get('long_literal_type_steps') or 0) > 0:
                evidence.append('long literal typed-text body present')
            activation_candidates = ['text-surface-route', 'launcher-entrypoint']
            base_fit = 'strong'
        elif has_watcher:
            route_id = 'watcher-service'
            title = 'Watcher-service macro'
            owner_layer = 'watcher / service layer'
            execution_surface = 'window/file/bus watcher service -> vhk run'
            summary = 'Treat this macro as a service-driven workflow that wakes the runner from an external event plane.'
            why = 'Linux automation gets more reliable when clipboard, DBus, file, or WM events arrive through dedicated watchers instead of being polled inside the same hotkey process.'
            learn_from = ['systemd --user', 'DBus / WM watcher tooling']
            commands = [
                f'vhk gen-vhk-busd-service {root_q} --out-dir ./build/systemd-user',
                f'vhk gen-readiness-pack {root_q} --quiet',
            ]
            evidence.append('watcher trigger present')
            activation_candidates = ['watcher-service-route', 'launcher-entrypoint']
            base_fit = 'strong'
        elif helper_sensitive:
            route_id = 'helper-boundary-runner'
            title = 'Helper-boundary runner macro'
            owner_layer = 'runner core + helper boundary'
            execution_surface = 'VHK runner behind helper-backed capture/input seams'
            summary = 'Keep macro semantics in VHK, but isolate the input/capture edges behind swappable Wayland helper routes.'
            why = 'Wayland pointer and capture behavior are still too desktop-specific to bake directly into the macro language as if they were universal Linux guarantees.'
            learn_from = ['xdg-desktop-portal', 'ydotool / dotool', 'AHK_X11']
            commands = [
                'vhk doctor --json',
                f'vhk gen-target-route-pack {root_q} --quiet',
            ]
            evidence.extend(capabilities)
            if has_hotkey:
                evidence.append('hotkey entry into helper-sensitive flow')
            if int(perf.get('live_capture_steps') or 0) > 0:
                risks.append('capture-heavy steps should stay bounded by named regions or explicit targets')
            if int(perf.get('unscoped_live_capture_steps') or 0) > 0:
                risks.append('unscoped capture makes helper and compositor variance more visible')
            if 'pointer_injection' in capabilities:
                risks.append('pointer injection remains the sharpest Wayland portability boundary')
            hotkey_candidates = ['portal-shortcuts-route', 'native-trigger-route', 'remapper-route', 'launcher-entrypoint'] if portal_catalog_macro else ['native-trigger-route', 'launcher-entrypoint', 'portal-shortcuts-route', 'remapper-route']
            activation_candidates = hotkey_candidates if has_hotkey else ['launcher-entrypoint']
            base_fit = 'conditional'
        elif palette_only or not triggers:
            route_id = 'launcher-entry'
            title = 'Launcher-entry macro'
            owner_layer = 'launcher / palette surface'
            execution_surface = 'palette, desktop entry, or launcher script -> vhk run'
            summary = 'This macro fits best as an explicit launcher or palette action instead of a resident trigger.'
            why = 'Many Linux automation tasks are easier to discover and safer to ship as launch surfaces than as more global always-on hotkeys.'
            learn_from = ['Kando', 'rofi / fuzzel / tofi launchers']
            commands = [
                f'vhk export-desktop-entry {root_q}',
                f'vhk export-launcher-script {root_q}',
            ]
            evidence.append('palette/manual entry surface')
            activation_candidates = ['launcher-entrypoint']
            base_fit = 'strong'
        else:
            if has_hotkey:
                if backend == 'wayland' and portal_catalog_macro:
                    activation_candidates = ['portal-shortcuts-route', 'native-trigger-route', 'remapper-route', 'launcher-entrypoint']
                elif backend == 'wayland':
                    activation_candidates = ['native-trigger-route', 'launcher-entrypoint', 'portal-shortcuts-route', 'remapper-route']
                else:
                    activation_candidates = ['native-trigger-route', 'portal-shortcuts-route', 'remapper-route', 'launcher-entrypoint']
                evidence.append('hotkey entry')
            else:
                activation_candidates = ['launcher-entrypoint']
            if 'vision-heavy' in tags:
                evidence.append('vision-heavy')
            if 'parameterized' in tags:
                evidence.append('parameterized')
            if 'flow-heavy' in tags or 'orchestrator' in tags or 'data-glue' in tags:
                evidence.append('stateful/orchestration logic present')
            if int(perf.get('long_delay_steps') or 0) > 0:
                risks.append('fixed delays still deserve replacement with waits or events')

        activation_route_id, activation_route = pick_activation(activation_candidates)
        fit = fit_for_route(base_fit, activation_route)
        if activation_route_id:
            evidence.append(f'activation route: {activation_route_id}')

        if capability_matrix and helper_sensitive:
            pointer = capability_matrix.get('pointer_injection') if isinstance(capability_matrix, Mapping) else None
            capture = capability_matrix.get('screen_capture') if isinstance(capability_matrix, Mapping) else None
            if isinstance(pointer, Mapping):
                risks.append(f"pointer session status: {str(pointer.get('status') or 'unknown')}")
            if isinstance(capture, Mapping):
                risks.append(f"capture session status: {str(capture.get('status') or 'unknown')}")

        rows.append(
            {
                'macro': name,
                'route_id': route_id,
                'title': title,
                'fit': fit,
                'owner_layer': owner_layer,
                'execution_surface': execution_surface,
                'primary_activation_route_id': activation_route_id or None,
                'activation_route_status': str((activation_route or {}).get('route_status') or '') or None,
                'summary': summary,
                'why': why,
                'learn_from': list(learn_from),
                'commands': list(commands),
                'capabilities': capabilities,
                'evidence': list(dict.fromkeys(str(x) for x in evidence if str(x))),
                'risks': list(dict.fromkeys(str(x) for x in risks if str(x))),
            }
        )

    rows.sort(key=lambda item: (
        {'strong': 0, 'good': 1, 'conditional': 2, 'weak': 3}.get(str(item.get('fit') or 'good'), 9),
        str(item.get('macro') or ''),
    ))
    return rows


def _macro_export_candidates(
    *,
    macro_route_profiles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def add(
        *,
        macro: str,
        route_id: str,
        export_surface_id: str,
        title: str,
        fit: str,
        reason: str,
        tool_family: list[str],
        commands: list[str],
        primary_activation_route_id: str | None,
        evidence: list[str] | None = None,
        risks: list[str] | None = None,
    ) -> None:
        rows.append({
            'macro': macro,
            'route_id': route_id,
            'export_surface_id': export_surface_id,
            'title': title,
            'fit': fit,
            'reason': reason,
            'tool_family': [str(x) for x in tool_family if str(x)],
            'commands': [str(x) for x in commands if str(x)],
            'primary_activation_route_id': primary_activation_route_id or None,
            'evidence': [str(x) for x in list(evidence or []) if str(x)],
            'risks': [str(x) for x in list(risks or []) if str(x)],
        })

    for item in macro_route_profiles:
        macro = str(item.get('macro') or '')
        route_id = str(item.get('route_id') or '')
        fit = str(item.get('fit') or 'good')
        activation_route_id = str(item.get('primary_activation_route_id') or '') or None
        evidence = list(item.get('evidence') or [])
        risks = list(item.get('risks') or [])
        commands = list(item.get('commands') or [])

        if route_id == 'remapper-tier':
            add(
                macro=macro,
                route_id=route_id,
                export_surface_id='remapper-export',
                title='Remapper export candidate',
                fit=fit,
                reason='Low-latency key transforms usually belong in a remapper/helper lane on Linux, with the VHK runner kept as a fallback for richer variants.',
                tool_family=['keyd', 'xremap', 'kanata'],
                commands=commands,
                primary_activation_route_id=activation_route_id,
                evidence=evidence,
                risks=risks,
            )
        elif route_id == 'text-tier':
            add(
                macro=macro,
                route_id=route_id,
                export_surface_id='text-package-export',
                title='Text package candidate',
                fit=fit,
                reason='Phrase-style snippets benefit from dedicated text packaging, app filters, and clipboard-aware throughput instead of always replaying inside the full runner.',
                tool_family=['Espanso', 'AutoKey'],
                commands=commands,
                primary_activation_route_id=activation_route_id,
                evidence=evidence,
                risks=risks,
            )
        elif route_id == 'watcher-service':
            add(
                macro=macro,
                route_id=route_id,
                export_surface_id='watcher-service-export',
                title='Watcher service candidate',
                fit=fit,
                reason='Event-driven flows fit best when the watch surface is explicit and the runner wakes from a service boundary instead of polling inside hotkey logic.',
                tool_family=['systemd --user', 'DBus / WM watchers'],
                commands=commands,
                primary_activation_route_id=activation_route_id,
                evidence=evidence,
                risks=risks,
            )
        elif route_id == 'helper-boundary-runner':
            add(
                macro=macro,
                route_id=route_id,
                export_surface_id='helper-route-dossier',
                title='Helper-boundary dossier candidate',
                fit=fit,
                reason='Keep the macro in VHK, but promote helper routes, capability checks, and session seams into first-class deployment artifacts.',
                tool_family=['xdg-desktop-portal', 'ydotool / dotool', 'AHK_X11'],
                commands=commands,
                primary_activation_route_id=activation_route_id,
                evidence=evidence,
                risks=risks,
            )
        elif route_id == 'launcher-entry':
            add(
                macro=macro,
                route_id=route_id,
                export_surface_id='launcher-surface-export',
                title='Launcher surface candidate',
                fit=fit,
                reason='Some Linux-native automations are easier to ship as an explicit launcher, desktop entry, or palette surface than as a global trigger.',
                tool_family=['desktop entry', 'rofi / fuzzel / tofi', 'Kando'],
                commands=commands,
                primary_activation_route_id=activation_route_id,
                evidence=evidence,
                risks=risks,
            )

    rows.sort(key=lambda item: (
        {'strong': 0, 'good': 1, 'conditional': 2, 'weak': 3}.get(str(item.get('fit') or 'good'), 9),
        str(item.get('macro') or ''),
        str(item.get('export_surface_id') or ''),
    ))
    return rows


def _ecosystem_lessons(
    *,
    project,
    overview: Mapping[str, Any],
    project_tags: list[str],
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
    capability_matrix: Mapping[str, Any] | None = None,
    stack_profiles: list[dict[str, Any]] | None = None,
    runtime_seams: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Summarize adjacent-tool lessons as concrete product guidance.

    The goal is to keep research from being stranded in docs. These are not
    citations; they are normalized product heuristics VHK can surface in JSON
    and generated packs.
    """

    backend = str(getattr(getattr(project, 'settings', None), 'desktop_backend', None) or '').strip().lower()
    capability_usage = capability_usage or {}
    stack_profiles = list(stack_profiles or [])
    runtime_seams = list(runtime_seams or [])
    root_dir = getattr(project, 'root_dir', None) or '.'
    root_q = shlex.quote(str(root_dir))
    modal_wm = backend if backend in {'i3', 'sway', 'hyprland'} else ('i3' if backend == 'x11' else '')

    top_profile_ids = {str(item.get('id') or '') for item in stack_profiles[:3]}
    seam_ids = {str(item.get('id') or '') for item in runtime_seams}
    pointer_usage = list(capability_usage.get('pointer_injection') or [])
    text_usage = list(capability_usage.get('text_injection') or [])
    capture_usage = list(capability_usage.get('screen_capture') or [])
    window_usage = list(capability_usage.get('window_introspection') or [])
    app_protocols = _app_protocol_target_analysis(project=project)
    app_protocol_target_count = int(app_protocols.get('target_count') or 0)
    app_protocol_learn_from = [str(x) for x in (app_protocols.get('learn_from') or []) if str(x)]
    app_protocol_target_ids = [str(x) for x in (app_protocols.get('target_ids') or []) if str(x)]
    app_protocol_commands = _app_protocol_pack_commands(root_q, app_protocol_target_ids)
    voice_adapters = _voice_adapter_analysis(project=project)
    voice_entry_count = int(voice_adapters.get('entry_count') or 0)
    voice_phrase_count = int(voice_adapters.get('explicit_phrase_count') or 0)
    voice_scoped_entry_count = int(voice_adapters.get('scoped_entry_count') or 0)
    mpris_services = _mpris_service_analysis(project=project)
    mpris_signal_count = int(mpris_services.get('signal_count') or 0)
    mpris_players = [str(x) for x in (mpris_services.get('players') or []) if str(x)]
    mpris_members = [str(x) for x in (mpris_services.get('members') or []) if str(x)]
    notification_feedback = _notification_feedback_analysis(project=project)
    notification_notify_count = int(notification_feedback.get('notify_count') or 0)
    notification_signal_count = int(notification_feedback.get('signal_count') or 0)
    notification_show_message_count = int(notification_feedback.get('show_message_count') or 0)
    notification_replaceable_count = int(notification_feedback.get('replaceable_count') or 0)
    notification_timed_count = int(notification_feedback.get('timed_count') or 0)
    notification_transient_count = int(notification_feedback.get('transient_count') or 0)
    notification_actionable_count = int(notification_feedback.get('actionable_count') or 0)
    notification_progress_count = int(notification_feedback.get('progress_count') or 0)
    notification_members = [str(x) for x in (notification_feedback.get('members') or []) if str(x)]
    watcher_count = int(overview.get('clipboard_watchers') or 0) + int(overview.get('file_watchers') or 0) + int(overview.get('bus_watchers') or 0) + int(overview.get('window_watchers') or 0)

    lessons: list[dict[str, Any]] = []

    def add(
        lesson_id: str,
        title: str,
        *,
        category: str,
        sources: list[str],
        summary: str,
        implication: str,
        fit: str = 'good',
        commands: list[str] | None = None,
        related_profiles: list[str] | None = None,
        related_seams: list[str] | None = None,
        evidence: list[str] | None = None,
    ) -> None:
        lessons.append({
            'id': lesson_id,
            'title': title,
            'category': category,
            'fit': fit,
            'source_tools': [str(x) for x in sources if str(x)],
            'summary': summary,
            'product_implication': implication,
            'commands': [str(x) for x in list(commands or []) if str(x)],
            'related_profiles': [str(x) for x in list(related_profiles or []) if str(x)],
            'related_seams': [str(x) for x in list(related_seams or []) if str(x)],
            'evidence': [str(x) for x in list(evidence or []) if str(x)],
        })

    add(
        'ahk-runner-diagnostics',
        'Keep the runtime rich, not the trigger layer',
        category='borrow',
        sources=['AutoHotkey'],
        summary='AHK feels powerful because waits, retries, variables, and diagnostics stay close to the runtime contract instead of being scattered across hotkey plumbing.',
        implication='VHK should keep sequencing and diagnostic state in the runner core even when triggers/export surfaces are split out.',
        fit='strong',
        commands=[f'vhk report --project {root_q} --latest --json'],
        related_profiles=[pid for pid in top_profile_ids if pid in {'selector-runner', 'text-first-export', 'wayland-helper-boundary'}],
        related_seams=['runner-core'],
        evidence=['runner-core seam present' if 'runner-core' in seam_ids else 'runner-core seam implied'],
    )

    add(
        'pulover-recorder-cleanup',
        'Treat recorder output as draft material',
        category='borrow',
        sources=["Pulover's Macro Creator"],
        summary='Pulover-style workflows stay productive because recording, inspection, visual steps, and cleanup are part of one authoring loop.',
        implication='VHK should keep selector assets, optimize/scaffold/report loops, and visual review artifacts first-class instead of pretending raw recordings are shippable.',
        fit='strong' if capture_usage or 'selector-asset-pack' in seam_ids else 'good',
        commands=[f'vhk optimize-project {root_q} --diff', f'vhk scaffold-project {root_q} --diff'],
        related_profiles=[pid for pid in top_profile_ids if pid in {'selector-runner'}],
        related_seams=['selector-asset-pack'] if 'selector-asset-pack' in seam_ids else [],
        evidence=[f'{len(capture_usage)} capture-related step(s)' if capture_usage else 'visual flow possible'],
    )

    if overview.get('hotstrings') or text_usage or 'text-surface' in seam_ids:
        add(
            'espanso-text-surface',
            'Ship text automation as a first-class exported surface',
            category='borrow',
            sources=['Espanso'],
            summary='Espanso demonstrates that forms, app scoping, packages, and service lifecycle are part of the product surface for text automation.',
            implication='VHK should keep prompts/presets in the runtime but export text-facing triggers and packaging explicitly.',
            fit='strong',
            commands=[f'vhk gen-espanso {root_q} --out-dir ./build/espanso'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'text-first-export'}],
            related_seams=['text-surface'] if 'text-surface' in seam_ids else [],
            evidence=[f"{overview.get('hotstrings') or 0} hotstring(s)", 'parameterized project' if 'parameterized' in project_tags else ''],
        )

    if backend == 'wayland' and (overview.get('hotstrings') or text_usage):
        add(
            'wtype-virtual-keyboard-boundary',
            'Treat virtual-keyboard text as a narrow Wayland lane',
            category='constraint',
            sources=['wtype'],
            summary='Wayland text typing tools like wtype are useful precisely because they are narrow: they depend on compositor-side virtual-keyboard support instead of offering one universal Linux text contract.',
            implication='VHK should surface wtype-class typing as an explicit fast path, keep clipboard/package exports first-class, and avoid promoting virtual-keyboard typing as a generic Wayland support claim.',
            fit='good',
            commands=[f'vhk validate {root_q} --json', f'vhk gen-espanso {root_q} --package-dir ./build/espanso_package'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'text-first-export', 'wayland-helper-boundary'}],
            related_seams=[sid for sid in ['text-surface', 'helper-boundary'] if sid in seam_ids],
            evidence=[f'backend={backend}', f"{overview.get('hotstrings') or 0} hotstring(s)", f'text_usage={len(text_usage)}'],
        )

    if backend in {'x11', 'i3'} and (overview.get('hotstrings') or overview.get('bindings') or text_usage):
        add(
            'autokey-reviewable-adapter',
            'Keep X11 adapter lanes reviewable',
            category='boundary',
            sources=['AutoKey'],
            summary='AutoKey still shows the value of a reviewable Linux automation shell: exported scripts, metadata, and trigger definitions stay visible instead of disappearing into one opaque runtime.',
            implication='VHK should keep AutoKey export as an explicit X11 adapter lane, preserve diffable script + metadata output, and warn whenever selector fidelity would be widened by AutoKey\'s coarse window filter.',
            fit='strong',
            commands=[f'vhk gen-autokey-pack {root_q} --out-dir ./build/autokey_pack', f'vhk lint-project {root_q}'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'text-first-export', 'remap-integrated'}],
            related_seams=[sid for sid in ['text-surface', 'trigger-surface'] if sid in seam_ids],
            evidence=[f'backend={backend}', f"{overview.get('hotstrings') or 0} hotstring(s)", f"{overview.get('bindings') or 0} binding(s)"],
        )

    if int(overview.get('macros') or 0) >= 4 or int(overview.get('presets') or 0) >= 2 or ('parameterized' in project_tags and int(overview.get('macros') or 0) >= 2):
        add(
            'menu-catalog-control-surface',
            'Keep growing macro catalogs discoverable',
            category='borrow',
            sources=['Kando', 'Fly-Pie'],
            summary='Menu-driven launchers and marking-menu tools keep large action catalogs usable by emphasizing discoverability and stable action identities instead of expecting every workflow to memorize another hotkey.',
            implication='VHK should keep palette entry ids, rofi-mode exports, and WM launcher modes aligned so future menu/radial surfaces can reuse one action catalog instead of inventing new glue per desktop.',
            fit='good',
            commands=[f'vhk export-rofi-mode {root_q} ./build/vhk.rofi.sh', f'vhk export-wm-launcher-mode {root_q} ./build/vhk.launcher --wm sway'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'text-first-export', 'watcher-daemon'}],
            related_seams=[sid for sid in ['trigger-surface', 'runner-core'] if sid in seam_ids],
            evidence=[f"{overview.get('macros') or 0} macro(s)", f"{overview.get('presets') or 0} preset(s)"],
        )
    if 'parameterized' in project_tags or int(overview.get('presets') or 0) or int(overview.get('hotstrings') or 0):
        add(
            'picker-protocol-thin-launch-surface',
            'Keep chooser UIs as thin picker protocols',
            category='borrow',
            sources=['rofi', 'fuzzel', 'wofi'],
            summary='Linux picker tools keep proving the same product lesson: chooser UIs work best as thin searchable entry surfaces that read options, return a selection, and let the real automation runtime live elsewhere.',
            implication='VHK should keep launcher-script and palette exports explicit, preserve one stable entry-id catalog across picker integrations, and avoid inventing a bespoke chooser runtime whenever script-mode or dmenu-style protocols already fit.',
            fit='good',
            commands=[f'vhk export-launcher-script {root_q}', f'vhk export-rofi-mode {root_q} ./build/vhk.rofi.sh', f'vhk palette {root_q} --json'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'text-first-export', 'watcher-daemon'}],
            related_seams=[sid for sid in ['trigger-surface', 'runner-core'] if sid in seam_ids],
            evidence=[f"presets={overview.get('presets') or 0}", f"hotstrings={overview.get('hotstrings') or 0}", f"backend={backend or 'auto'}"],
        )

    if backend in {'x11', 'i3', 'sway', 'hyprland'} and (int(overview.get('bindings') or 0) >= 3 or int(overview.get('macros') or 0) >= 5):
        add(
            'wm-modes-submaps-grouped-triggers',
            'Use WM modes/submaps as grouped trigger layers',
            category='borrow',
            sources=['i3', 'Hyprland', 'sxhkd'],
            summary='Modern Linux hotkey layers already have a useful middle ground between flat globals and full launcher menus: grouped modes/submaps/chord chains that open a temporary action family and then reset.',
            implication='VHK should keep WM mode/submap exports explicit, preserve reset semantics, and route the same action ids into launcher fallbacks so grouped triggers remain reviewable instead of becoming hidden keyboard state.',
            fit='good',
            commands=[f'vhk gen-wm-config {root_q} --wm {modal_wm or "i3"} --mode-enter Mod4+R --mode-name vhk', f'vhk export-wm-bundle {root_q} ./build/wm_bundle --wm {modal_wm or "i3"} --kind launcher-mode --mode-enter Mod4+R'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'remap-integrated', 'watcher-daemon'}],
            related_seams=[sid for sid in ['trigger-surface', 'runner-core'] if sid in seam_ids],
            evidence=[f'backend={backend}', f"{overview.get('bindings') or 0} binding(s)", f"{overview.get('macros') or 0} macro(s)"],
        )

    add(
        'autokey-session-honesty',
        'Be explicit about desktop/session scope',
        category='constraint',
        sources=['AutoKey'],
        summary='Adjacent Linux automation tools still have to be blunt about where they work well and where they do not.',
        implication='VHK support claims, setup docs, and release gates should name reference lanes and caveated lanes instead of implying generic Linux parity.',
        fit='strong',
        commands=['vhk doctor --json', f'vhk gen-claim-pack {root_q} --quiet'],
        related_profiles=[pid for pid in top_profile_ids if pid in {'wayland-helper-boundary', 'remap-integrated', 'watcher-daemon'}],
        related_seams=['helper-boundary'] if 'helper-boundary' in seam_ids else [],
        evidence=[f'backend={backend or "auto"}'],
    )

    if window_usage or int(overview.get('window_watchers') or 0):
        add(
            'atspi-separate-bus-structured-automation',
            'Treat accessibility as a first-class automation contract',
            category='borrow',
            sources=['at-spi2-core', 'Accerciser', 'dogtail'],
            summary='Linux accessibility automation is powerful precisely because it is explicit: AT-SPI lives on a separate bus, explorer tools inspect that tree, and automation wrappers like dogtail sit on top instead of pretending widget semantics are free.',
            implication='VHK should keep a11y health visible in doctor/planning output, model structured UI targeting as its own lane, and always pair AT-SPI-shaped selectors with desktop-metadata and vision fallbacks for apps that expose poor trees.',
            fit='good',
            commands=['vhk doctor --json', f'vhk window-spy --project {root_q} --json --no-check', f'vhk gen-session-fit-pack {root_q} --quiet'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'selector-runner', 'watcher-daemon', 'wayland-helper-boundary'}],
            related_seams=[sid for sid in ['selector-asset-pack', 'runner-core'] if sid in seam_ids],
            evidence=[f'backend={backend or "auto"}', f'window_usage={len(window_usage)}', f'watchers={watcher_count}'],
        )

    if app_protocol_target_count:
        add(
            'native-app-protocols-beat-input-replay',
            'Prefer app-native protocols over blind input replay when the target app already has one',
            category='borrow',
            sources=app_protocol_learn_from,
            summary='Some Linux apps already expose better automation contracts than simulated input: terminal panes can accept directed text, media players can expose socket IPC, and browser userscripts can hand commands through their own extension points.',
            implication='VHK should surface app-native adapter lanes during planning, tie them to explicit window/app selectors, and reserve generic text/pointer/vision replay for apps that do not expose comparable control contracts.',
            fit='strong' if app_protocol_target_count >= 2 else 'good',
            commands=app_protocol_commands,
            related_profiles=[pid for pid in top_profile_ids if pid in {'selector-runner', 'text-first-export', 'wayland-helper-boundary'}],
            related_seams=[sid for sid in ['runner-core', 'trigger-surface', 'selector-asset-pack'] if sid in seam_ids],
            evidence=[f'app_protocol_targets={",".join(app_protocol_target_ids)}', f'backend={backend or "auto"}', f'window_usage={len(window_usage)}', f'text_usage={len(text_usage)}'],
        )

    if voice_entry_count:
        add(
            'voice-tools-own-recognition-context',
            'Keep speech recognition and voice contexts on the adapter side',
            category='boundary',
            sources=['Talon', 'Dragonfly'],
            summary='The current Linux voice ecosystem already has real context models and command files: Talon activates `.talon` files by app/title criteria, while Dragonfly grammars and app contexts live in the speech stack itself rather than inside the automation target.',
            implication='VHK should keep exporting reviewable Talon/Dragonfly packs, preserve literal spoken-command ledgers, and avoid turning voice support into a second runtime or a fake cross-desktop promise.',
            fit='strong' if voice_scoped_entry_count else 'good',
            commands=[f'vhk gen-dragonfly-pack {root_q} --out-dir ./build/dragonfly_pack', f'vhk gen-talon-pack {root_q} --out-dir ./build/talon_pack', f'vhk lint-project {root_q}'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'selector-runner', 'text-first-export', 'watcher-daemon'}],
            related_seams=[sid for sid in ['runner-core', 'trigger-surface'] if sid in seam_ids],
            evidence=[f'voice_commands={voice_entry_count}', f'voice_phrases={voice_phrase_count}', f'voice_contexts={voice_scoped_entry_count}', f'backend={backend or "auto"}'],
        )

    if mpris_signal_count:
        add(
            'mpris-standard-media-bus',
            'Use standard media-player bus contracts before replaying media keys',
            category='borrow',
            sources=['MPRIS', 'playerctl'],
            summary='Linux media control already has a standard contract: MPRIS exposes common player methods, properties, and signals over D-Bus, while playerctl layers selection, follow mode, and a recent-player daemon on top of that instead of relying on focus-sensitive key replay.',
            implication='VHK should surface MPRIS/playerctl-class flows as an explicit service-bus lane, keep media follow/control logic reviewable, and reserve key replay for players that do not expose the standard contract.',
            fit='strong' if mpris_players else 'good',
            commands=['vhk doctor --json', f'vhk gen-playerctl-pack {root_q} --out-dir ./build/playerctl_pack', f'vhk gen-session-fit-pack {root_q} --quiet', f'vhk gen-design-pack {root_q} --quiet', f'vhk lint-project {root_q}'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'selector-runner', 'watcher-daemon', 'wayland-helper-boundary'}],
            related_seams=[sid for sid in ['runner-core', 'trigger-surface'] if sid in seam_ids],
            evidence=[f'mpris_signals={mpris_signal_count}', f'mpris_players={",".join(mpris_players) if mpris_players else "unknown"}', f'mpris_members={",".join(mpris_members) if mpris_members else "unknown"}', f'backend={backend or "auto"}'],
        )

    if notification_notify_count or notification_signal_count:
        add(
            'notifications-are-session-service-contract',
            'Treat desktop notifications as a session service contract',
            category='borrow',
            sources=['Desktop Notifications spec', 'dunst', 'XDG Notification portal'],
            summary='Linux desktop notifications are already a shared session service: the freedesktop spec defines one bus name/object for passive notifications and optional actions/close signals, while the portal notification API deliberately narrows sandboxed apps to send/withdraw without promising presentation feedback.',
            implication='VHK should surface notification feedback as an explicit lane, keep passive status and alert flows reviewable, and avoid pretending modal prompts, notification daemons, and sandbox portals are the same contract.',
            fit='strong' if notification_signal_count else 'good',
            commands=['vhk doctor --json', f'vhk gen-design-pack {root_q} --quiet', f'vhk gen-setup-pack {root_q} --quiet', f'vhk lint-project {root_q}'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'watcher-daemon', 'selector-runner', 'wayland-helper-boundary'}],
            related_seams=[sid for sid in ['runner-core', 'trigger-surface'] if sid in seam_ids],
            evidence=[f'notify_steps={notification_notify_count}', f'show_messages={notification_show_message_count}', f'notification_signals={notification_signal_count}', f'replaceable_notifications={notification_replaceable_count}', f'timed_notifications={notification_timed_count}', f'transient_notifications={notification_transient_count}', f'actionable_notifications={notification_actionable_count}', f'progress_notifications={notification_progress_count}', f'notification_members={",".join(notification_members) if notification_members else "none"}', f'backend={backend or "auto"}'],
        )

    if pointer_usage or overview.get('bindings'):
        add(
            'xremap-app-context-bridge',
            'App-scoped behavior needs context bridges',
            category='constraint',
            sources=['xremap'],
            summary='Per-app remapping and context-sensitive behavior on Linux often depends on compositor- or desktop-specific active-window context bridges.',
            implication='VHK should treat app/window scoping as a capability with backend-specific implementations and review steps, not as one global checkbox.',
            fit='good',
            commands=[f'vhk plan-project {root_q} --json', f'vhk gen-portability-pack {root_q} --quiet'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'remap-integrated', 'wayland-helper-boundary'}],
            related_seams=['trigger-surface', 'helper-boundary'] if 'helper-boundary' in seam_ids else ['trigger-surface'],
            evidence=[f"{overview.get('bindings') or 0} binding(s)", f'{len(pointer_usage)} pointer step(s)'],
        )

    if overview.get('bindings'):
        add(
            'keyd-thin-trigger-boundary',
            'Keep privileged remappers thin',
            category='boundary',
            sources=['keyd', 'Kanata', 'KMonad'],
            summary='Low-level remappers win by staying narrow: intercept keys quickly, then hand richer logic off elsewhere.',
            implication='VHK should export configs for fast trigger ownership, but keep prompts, variables, selectors, and diagnostics in user-space runtime layers.',
            fit='strong',
            commands=[f'vhk gen-keyd-config {root_q} --out ./build/vhk.keyd.conf', f'vhk gen-kanata-config {root_q} --out ./build/vhk.kanata.kbd'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'remap-integrated', 'wayland-helper-boundary'}],
            related_seams=['trigger-surface', 'runner-core'],
            evidence=[f"{overview.get('bindings') or 0} binding(s)"],
        )

    if backend == 'wayland':
        add(
            'portal-stable-action-catalog',
            'Use portal shortcuts for stable action catalogs, not endless dynamic macro churn',
            category='constraint',
            sources=['XDG GlobalShortcuts portal'],
            summary='Portal shortcuts are session-oriented and best when the app can pre-register stable actions.',
            implication='VHK should keep compositor binds and launcher surfaces first-class for dynamic or recorder-generated macro sets.',
            fit='good',
            commands=[f'vhk gen-portal-shortcuts-spec {root_q} --out ./build/vhk.portal-shortcuts.yml', f'vhk portal-hotkeys {root_q} --bind --listen'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'wayland-helper-boundary', 'text-first-export'}],
            related_seams=['trigger-surface', 'helper-boundary'] if 'helper-boundary' in seam_ids else ['trigger-surface'],
            evidence=['Wayland session target'],
        )

    if backend == 'wayland' and (pointer_usage or text_usage):
        add(
            'daemonized-helper-lifecycle',
            'Treat helper daemons as a deployable product lane',
            category='boundary',
            sources=['ydotool', 'dotool'],
            summary='uinput-backed Linux helpers become much more reliable when their virtual devices and sockets live behind a deliberate daemon lifecycle instead of being spawned fresh for every action.',
            implication='VHK should elevate helper services, socket paths, and uinput policy into planning output whenever repeated Wayland text/pointer playback is in scope, rather than treating daemon setup as an afterthought.',
            fit='strong' if pointer_usage else 'good',
            commands=['vhk doctor --json', 'vhk gen-dotoold-service --out-dir ./build/systemd-user', 'vhk gen-ydotoold-service --out-dir ./build/systemd-user', 'vhk gen-udev-uinput --out-dir ./build/udev'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'wayland-helper-boundary'}],
            related_seams=['helper-boundary'] if 'helper-boundary' in seam_ids else [],
            evidence=[f'{len(pointer_usage)} pointer step(s)', f'{len(text_usage)} text step(s)', 'Wayland session target'],
        )

    if backend == 'wayland' and (pointer_usage or capture_usage):
        add(
            'libei-helper-seam',
            'Keep future input-capture/injection work behind a helper seam',
            category='experiment',
            sources=['libei / InputCapture ecosystem'],
            summary='Input-capture-class stacks are promising but still operationally sensitive enough that they should be treated as isolated helper experiments first.',
            implication='VHK should preserve a narrow adapter seam so future libei/EIS work can be tested without rewriting macro semantics.',
            fit='good',
            commands=['vhk doctor --json', f'vhk gen-verification-pack {root_q} --quiet'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'wayland-helper-boundary'}],
            related_seams=['helper-boundary'] if 'helper-boundary' in seam_ids else [],
            evidence=[f'{len(pointer_usage)} pointer step(s)', f'{len(capture_usage)} capture step(s)'],
        )

    lessons.sort(key=lambda item: ({'borrow': 0, 'boundary': 1, 'constraint': 2, 'experiment': 3}.get(str(item.get('category') or ''), 9), {'strong': 0, 'good': 1, 'conditional': 2, 'weak': 3}.get(str(item.get('fit') or ''), 9), str(item.get('title') or '')))
    return lessons


def _performance_profile(
    *,
    overview: Mapping[str, Any],
    macro_profiles: list[dict[str, Any]],
) -> dict[str, Any]:
    totals = Counter()
    macro_rows: list[dict[str, Any]] = []
    direct_hotkey_heavy: list[str] = []

    for item in macro_profiles:
        perf = item.get("performance") or {}
        row = {
            "macro": str(item.get("macro") or ""),
            "triggers": list(item.get("triggers") or []),
            "step_count": int(item.get("step_count") or 0),
            "risk_level": str(perf.get("risk_level") or "low"),
            "risk_score": int(perf.get("risk_score") or 0),
            "tags": list(perf.get("tags") or []),
            "live_capture_steps": int(perf.get("live_capture_steps") or 0),
            "unscoped_live_capture_steps": int(perf.get("unscoped_live_capture_steps") or 0),
            "ocr_steps": int(perf.get("ocr_steps") or 0),
            "polling_wait_steps": int(perf.get("polling_wait_steps") or 0),
            "low_poll_wait_steps": int(perf.get("low_poll_wait_steps") or 0),
            "event_wait_steps": int(perf.get("event_wait_steps") or 0),
            "hybrid_wait_steps": int(perf.get("hybrid_wait_steps") or 0),
            "declared_delay_ms": int(perf.get("declared_delay_ms") or 0),
            "long_delay_steps": int(perf.get("long_delay_steps") or 0),
            "literal_type_steps": int(perf.get("literal_type_steps") or 0),
            "literal_type_chars": int(perf.get("literal_type_chars") or 0),
            "long_literal_type_steps": int(perf.get("long_literal_type_steps") or 0),
            "long_literal_type_chars": int(perf.get("long_literal_type_chars") or 0),
            "structured_literal_type_steps": int(perf.get("structured_literal_type_steps") or 0),
            "structured_literal_type_chars": int(perf.get("structured_literal_type_chars") or 0),
            "clipboard_text_steps": int(perf.get("clipboard_text_steps") or 0),
            "clipboard_text_chars": int(perf.get("clipboard_text_chars") or 0),
            "declared_wait_timeout_ms": int(perf.get("declared_wait_timeout_ms") or 0),
        }
        macro_rows.append(row)
        for key in (
            "live_capture_steps",
            "unscoped_live_capture_steps",
            "ocr_steps",
            "polling_wait_steps",
            "low_poll_wait_steps",
            "event_wait_steps",
            "hybrid_wait_steps",
            "declared_delay_ms",
            "long_delay_steps",
            "literal_type_steps",
            "literal_type_chars",
            "long_literal_type_steps",
            "long_literal_type_chars",
            "structured_literal_type_steps",
            "structured_literal_type_chars",
            "clipboard_text_steps",
            "clipboard_text_chars",
            "declared_wait_timeout_ms",
        ):
            totals[key] += int(row.get(key) or 0)
        if "hotkey" in row["triggers"] and (
            row["live_capture_steps"] > 0
            or row["ocr_steps"] > 0
            or row["declared_delay_ms"] >= 1500
            or row["step_count"] >= 6
        ):
            direct_hotkey_heavy.append(row["macro"])

    macro_rows.sort(
        key=lambda item: (
            {"high": 0, "medium": 1, "low": 2}.get(str(item.get("risk_level") or "low"), 9),
            -int(item.get("risk_score") or 0),
            str(item.get("macro") or ""),
        )
    )

    hotspots: list[dict[str, Any]] = []

    def add_hotspot(
        id: str,
        severity: str,
        title: str,
        count: int,
        macros: list[str],
        why: str,
        actions: list[str],
    ) -> None:
        hotspots.append(
            {
                "id": id,
                "severity": severity,
                "title": title,
                "count": int(count),
                "macros": list(macros),
                "why": why,
                "actions": list(actions),
            }
        )

    if totals["unscoped_live_capture_steps"]:
        macros = [
            str(item.get("macro") or "")
            for item in macro_rows
            if int(item.get("unscoped_live_capture_steps") or 0) > 0
        ][:6]
        add_hotspot(
            "unscoped-live-capture",
            "high",
            "Unscoped live capture",
            totals["unscoped_live_capture_steps"],
            macros,
            "Screen-backed image/OCR steps without a region force broader captures and make timing and compositor variance more expensive.",
            [
                "add named regions or inline region bounds to live image/OCR steps",
                "promote stable anchors into needle assets instead of polling the whole desktop",
            ],
        )
    if totals["low_poll_wait_steps"]:
        macros = [
            str(item.get("macro") or "")
            for item in macro_rows
            if int(item.get("low_poll_wait_steps") or 0) > 0
        ][:6]
        add_hotspot(
            "aggressive-polling",
            "high" if totals["low_poll_wait_steps"] >= 2 else "medium",
            "Aggressive polling waits",
            totals["low_poll_wait_steps"],
            macros,
            "Fast polling increases CPU wakeups and makes screenshot/OCR loops more expensive, especially when the wait is screen-backed.",
            [
                "raise poll_ms or use bounded scan_rate_hz where human-visible latency allows it",
                "replace polling with bus/window/file/dbus events when the platform can provide them",
            ],
        )
    if totals["ocr_steps"]:
        macros = [
            str(item.get("macro") or "")
            for item in macro_rows
            if int(item.get("ocr_steps") or 0) > 0
        ][:6]
        add_hotspot(
            "ocr-pressure",
            "medium",
            "OCR-heavy runtime path",
            totals["ocr_steps"],
            macros,
            "OCR is a powerful fallback, but it is usually more expensive and noisier than window/app selectors or template matching with bounded regions.",
            [
                "scope OCR to explicit regions or needle OCR areas",
                "prefer app/window selectors or exact visual anchors before global OCR",
            ],
        )
    if totals["long_delay_steps"]:
        macros = [
            str(item.get("macro") or "")
            for item in macro_rows
            if int(item.get("long_delay_steps") or 0) > 0
        ][:6]
        add_hotspot(
            "fixed-delay-budget",
            "medium",
            "Large fixed delays",
            totals["long_delay_steps"],
            macros,
            "Long fixed sleeps hide state changes and make macros feel slower than they need to be on fast hosts while still being brittle on slow ones.",
            [
                "replace long Delay steps with WaitUntil or event/window/file waits",
                "use report/trace output to tune waits against actual host behavior",
            ],
        )

    if totals["long_literal_type_steps"] or totals["structured_literal_type_steps"]:
        macros = [
            str(item.get("macro") or "")
            for item in macro_rows
            if int(item.get("long_literal_type_steps") or 0) > 0 or int(item.get("structured_literal_type_steps") or 0) > 0
        ][:6]
        severity = "medium" if totals["structured_literal_type_steps"] or totals["long_literal_type_chars"] >= 240 else "low"
        add_hotspot(
            "typed-text-throughput",
            severity,
            "Literal typed-text throughput",
            totals["long_literal_type_steps"] + totals["structured_literal_type_steps"],
            macros,
            "Large literal TypeText bodies are still easy to author, but replaying them through per-character typing can add noticeable latency versus a clipboard or hybrid paste lane.",
            [
                "promote clearly paste-friendly text to backend=clipboard or use optimize --promote-paste-text",
                "segment Tab/Enter-rich snippets with optimize --segment-paste-text so field separators stay explicit",
            ],
        )
    if totals["polling_wait_steps"] > max(1, totals["event_wait_steps"] + totals["hybrid_wait_steps"]):
        macros = [
            str(item.get("macro") or "")
            for item in macro_rows
            if int(item.get("polling_wait_steps") or 0) > int(item.get("event_wait_steps") or 0)
        ][:6]
        add_hotspot(
            "polling-dominant",
            "medium",
            "Polling dominates the wait model",
            totals["polling_wait_steps"],
            macros,
            "The project leans more on polling waits than on bus/window/file/dbus events, which usually means more wakeups and less honest synchronization.",
            [
                "push stable external state into WaitForBusEvent / WaitForDbusSignal / WaitForWindowEvent / WaitForFileEvent where possible",
                "keep vision waits as the fallback lane, not the default synchronization primitive",
            ],
        )
    if direct_hotkey_heavy:
        add_hotspot(
            "direct-hotkey-heavy-macros",
            "medium",
            "Heavy macros sit directly on hotkeys",
            len(direct_hotkey_heavy),
            direct_hotkey_heavy[:6],
            "Macros with capture, OCR, or long waits are bound directly to hotkeys, which can make the trigger path feel slower than a Linux-native dispatch plane.",
            [
                "prefer WM bindings or helper daemons that emit lightweight bus events for hotkey entry",
                "keep heavy macro orchestration behind vhk-emit or long-lived watcher services",
            ],
        )

    hotspots.sort(
        key=lambda item: (
            {"high": 0, "medium": 1, "low": 2}.get(str(item.get("severity") or "medium"), 9),
            -int(item.get("count") or 0),
            str(item.get("title") or ""),
        )
    )

    priority = "low"
    if any(str(item.get("severity") or "") == "high" for item in hotspots):
        priority = "high"
    elif hotspots:
        priority = "medium"

    summary_bits: list[str] = []
    if totals["unscoped_live_capture_steps"]:
        summary_bits.append(f"{totals['unscoped_live_capture_steps']} unscoped live capture step(s)")
    if totals["low_poll_wait_steps"]:
        summary_bits.append(f"{totals['low_poll_wait_steps']} aggressive poll wait(s)")
    if totals["ocr_steps"]:
        summary_bits.append(f"{totals['ocr_steps']} OCR step(s)")
    if totals["long_literal_type_steps"]:
        summary_bits.append(f"{totals['long_literal_type_steps']} long literal typed-text step(s)")
    if totals["structured_literal_type_steps"]:
        summary_bits.append(f"{totals['structured_literal_type_steps']} structured typed-text step(s)")
    if totals["event_wait_steps"]:
        summary_bits.append(f"{totals['event_wait_steps']} event wait(s)")
    if direct_hotkey_heavy:
        summary_bits.append(f"{len(direct_hotkey_heavy)} heavy hotkey-bound macro(s)")
    summary = "; ".join(summary_bits) if summary_bits else "Project shape is light enough that runtime cost is likely dominated by startup and host-specific helper behavior."

    budgets = {
        "live_capture_steps": int(totals["live_capture_steps"]),
        "unscoped_live_capture_steps": int(totals["unscoped_live_capture_steps"]),
        "ocr_steps": int(totals["ocr_steps"]),
        "polling_wait_steps": int(totals["polling_wait_steps"]),
        "low_poll_wait_steps": int(totals["low_poll_wait_steps"]),
        "event_wait_steps": int(totals["event_wait_steps"]),
        "hybrid_wait_steps": int(totals["hybrid_wait_steps"]),
        "declared_delay_ms": int(totals["declared_delay_ms"]),
        "long_delay_steps": int(totals["long_delay_steps"]),
        "literal_type_steps": int(totals["literal_type_steps"]),
        "literal_type_chars": int(totals["literal_type_chars"]),
        "long_literal_type_steps": int(totals["long_literal_type_steps"]),
        "long_literal_type_chars": int(totals["long_literal_type_chars"]),
        "structured_literal_type_steps": int(totals["structured_literal_type_steps"]),
        "structured_literal_type_chars": int(totals["structured_literal_type_chars"]),
        "clipboard_text_steps": int(totals["clipboard_text_steps"]),
        "clipboard_text_chars": int(totals["clipboard_text_chars"]),
        "declared_wait_timeout_ms": int(totals["declared_wait_timeout_ms"]),
        "direct_hotkey_heavy_macros": int(len(direct_hotkey_heavy)),
        "bindings": int(overview.get("bindings") or 0),
        "bus_watchers": int(overview.get("bus_watchers") or 0),
        "window_watchers": int(overview.get("window_watchers") or 0),
        "clipboard_watchers": int(overview.get("clipboard_watchers") or 0),
        "file_watchers": int(overview.get("file_watchers") or 0),
    }

    return {
        "priority": priority,
        "summary": summary,
        "budget": budgets,
        "hotspots": hotspots,
        "macro_runtime_profiles": macro_rows,
    }


def _input_lane_dossier(
    *,
    project,
    overview: Mapping[str, Any],
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
    capability_matrix: Mapping[str, Any] | None = None,
    performance_profile: Mapping[str, Any] | None = None,
    surface_choices: list[dict[str, Any]] | None = None,
    host_requirements: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Summarize Linux-native input routes by workload instead of by helper name."""

    backend = str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "").strip().lower()
    project_root_q = shlex.quote(str(Path(getattr(project, "root_dir", "."))))
    usage_map = {
        str(key): [dict(item) for item in list(value or []) if isinstance(item, Mapping)]
        for key, value in dict(capability_usage or {}).items()
        if str(key)
    }
    capability_items = {
        str(key): dict(value)
        for key, value in dict(capability_matrix or {}).items()
        if isinstance(value, Mapping)
    }
    budget = dict((performance_profile or {}).get("budget") or {})
    surface_ids = {str(item.get("id") or "") for item in list(surface_choices or []) if isinstance(item, Mapping)}
    requirements = [dict(item) for item in list(host_requirements or []) if isinstance(item, Mapping)]

    text_usage = usage_map.get("text_injection", [])
    pointer_usage = usage_map.get("pointer_injection", [])
    capture_usage = usage_map.get("screen_capture", [])
    input_capture_usage = usage_map.get("input_capture", [])

    def _cap_item(name: str) -> dict[str, Any]:
        return dict(capability_items.get(name) or {})

    def _cap_status(name: str) -> str:
        return str(_cap_item(name).get("status") or "unknown").strip().lower() or "unknown"

    def _cap_recommended(name: str) -> str:
        return str(_cap_item(name).get("recommended") or "").strip().lower()

    def _cap_mechanisms(name: str) -> list[str]:
        return [str(x).strip().lower() for x in list(_cap_item(name).get("mechanisms") or []) if str(x).strip()]

    def _usage_examples(capability: str, *, limit: int = 4) -> list[str]:
        examples: list[str] = []
        for item in usage_map.get(capability, []):
            macro = str(item.get("macro") or item.get("watcher") or item.get("source") or "").strip()
            step_type = str(item.get("step_type") or item.get("keys") or "").strip()
            label = ":".join(part for part in [macro, step_type] if part) or macro or step_type
            if label and label not in examples:
                examples.append(label)
            if len(examples) >= limit:
                break
        return examples

    def _lane_requirements(*ids: str, capability: str | None = None, requirement_type: str | None = None) -> list[str]:
        wanted = {str(x) for x in ids if str(x)}
        out: list[str] = []
        for item in requirements:
            item_id = str(item.get("id") or "")
            if wanted and item_id in wanted and item_id not in out:
                out.append(item_id)
                continue
            if capability and str(item.get("capability") or "") == capability:
                if requirement_type and str(item.get("requirement_type") or "") != requirement_type:
                    continue
                if item_id and item_id not in out:
                    out.append(item_id)
        return out

    long_literal_steps = int(budget.get("long_literal_type_steps") or 0)
    structured_literal_steps = int(budget.get("structured_literal_type_steps") or 0)
    clipboard_text_steps = int(budget.get("clipboard_text_steps") or 0)
    direct_hotkey_heavy = int(budget.get("direct_hotkey_heavy_macros") or 0)
    bindings = int(overview.get("bindings") or 0)
    hotstrings = int(overview.get("hotstrings") or 0)

    text_status = _cap_status("text_injection")
    pointer_status = _cap_status("pointer_injection")
    input_capture_status = _cap_status("input_capture")
    text_recommended = _cap_recommended("text_injection")
    pointer_recommended = _cap_recommended("pointer_injection")
    input_capture_recommended = _cap_recommended("input_capture")
    text_mechanisms = _cap_mechanisms("text_injection")
    pointer_mechanisms = _cap_mechanisms("pointer_injection")
    input_capture_mechanisms = _cap_mechanisms("input_capture")

    lanes: list[dict[str, Any]] = []

    def add_lane(
        lane_id: str,
        title: str,
        kind: str,
        score: int,
        why: str,
        recommended_for: list[str],
        cautions: list[str],
        commands: list[str],
        learn_from: list[str],
        evidence: list[str],
        session_capabilities: list[str],
        host_requirement_ids: list[str],
    ) -> None:
        score = max(0, min(int(score), 100))
        lanes.append(
            {
                "id": lane_id,
                "title": title,
                "kind": kind,
                "score": score,
                "fit": _fit_label(score),
                "why": why,
                "recommended_for": [str(x) for x in recommended_for if str(x)],
                "cautions": [str(x) for x in cautions if str(x)],
                "commands": [str(x) for x in commands if str(x)],
                "learn_from": [str(x) for x in learn_from if str(x)],
                "evidence": [str(x) for x in evidence if str(x)],
                "session_capabilities": [str(x) for x in session_capabilities if str(x)],
                "host_requirement_ids": [str(x) for x in host_requirement_ids if str(x)],
            }
        )

    clipboard_score = hotstrings * 20 + len(text_usage) * 8 + structured_literal_steps * 16 + long_literal_steps * 14 + clipboard_text_steps * 12
    if backend == "wayland":
        clipboard_score += 12
    elif backend in {"x11", "i3"}:
        clipboard_score += 8
    if text_recommended == "clipboard" or any("clipboard" in mech for mech in text_mechanisms):
        clipboard_score += 20
    elif hotstrings or structured_literal_steps or long_literal_steps:
        clipboard_score += 8
    add_lane(
        "clipboard-text-lane",
        "Clipboard-first text lane",
        "text",
        clipboard_score,
        "Long snippets, forms, and package-shaped text are usually healthier as a clipboard/text-surface lane than as literal key replay.",
        ["hotstrings and text packages", "prompt-built snippets", "long or structured literal text"],
        [
            "Window/app scoping still depends on the chosen text surface rather than the runner alone.",
            "Clipboard ownership and paste shortcuts still deserve per-desktop review for terminals and password fields.",
        ],
        [f"vhk gen-espanso {project_root_q} --package-dir ./build/espanso_package", f"vhk validate {project_root_q} --json"],
        ["Espanso", "clipboard-first text packaging"],
        [f"backend={backend or 'unknown'}", f"hotstrings={hotstrings}", f"text_usage={len(text_usage)}", f"structured_literal_steps={structured_literal_steps}", f"long_literal_steps={long_literal_steps}", *(f"uses={x}" for x in _usage_examples("text_injection"))],
        [f"text_injection={text_status}"],
        _lane_requirements("text-surface-service", capability="text_injection", requirement_type="service"),
    )

    wtype_score = 0
    if backend == "wayland" and text_usage:
        wtype_score = len(text_usage) * 10 + long_literal_steps * 8 + structured_literal_steps * 6
        if text_recommended == "wtype":
            wtype_score += 28
        elif "wtype" in text_mechanisms:
            wtype_score += 16
        elif text_status in {"ok", "limited"}:
            wtype_score += 6
        else:
            wtype_score -= 8
    add_lane(
        "virtual-keyboard-text-fastpath",
        "Virtual-keyboard text fast path",
        "text-fastpath",
        wtype_score,
        "On Wayland, compositor-backed virtual-keyboard typing is best treated as a narrow fast path for literal text bursts, not as the whole text story.",
        ["short literal typing bursts", "text where clipboard round-trips are awkward", "sessions that explicitly prove virtual-keyboard support"],
        [
            "Compositor/protocol support varies; this lane should stay conditional unless the session actually proves it.",
            "Pressed modifiers belong to the helper process lifecycle, so longer chord flows still need careful sequencing.",
        ],
        ["vhk doctor --json", f"vhk gen-espanso {project_root_q} --package-dir ./build/espanso_package"],
        ["wtype", "Wayland virtual-keyboard protocol"],
        [f"backend={backend or 'unknown'}", f"text_injection={text_status}", f"recommended={text_recommended or 'none'}", *(f"mechanism={x}" for x in text_mechanisms[:3]), *(f"uses={x}" for x in _usage_examples("text_injection"))],
        [f"text_injection={text_status}"],
        [],
    )

    daemon_score = 0
    if backend == "wayland" and (pointer_usage or text_usage):
        daemon_score = len(pointer_usage) * 18 + len(text_usage) * 7 + direct_hotkey_heavy * 12 + bindings * 4
        daemon_tokens = {pointer_recommended, text_recommended, *pointer_mechanisms, *text_mechanisms}
        if {"dotoolc", "dotool", "ydotool", "helper", "portal/helper"}.intersection(daemon_tokens):
            daemon_score += 22
        if "uinput-helper-daemon" in surface_ids:
            daemon_score += 14
        if pointer_status in {"missing", "limited"}:
            daemon_score += 8
    add_lane(
        "daemon-backed-uinput-playback",
        "Daemon-backed uinput playback",
        "helper-daemon",
        daemon_score,
        "Repeated pointer/text playback on Wayland is usually healthier when a reviewed daemon keeps virtual devices alive instead of paying setup cost on every macro edge.",
        ["repeated pointer automation", "repeated key playback", "dispatch-sensitive macros that should avoid per-step helper startup"],
        [
            "This lane depends on `/dev/uinput`, service wiring, and socket/device ownership, so it should stay an explicit host contract.",
            "It is a deployment lane, not a generic Linux default or a promise that every host should get raw input privileges.",
        ],
        ["vhk doctor --json", "vhk gen-dotoold-service --out-dir ./build/systemd-user", "vhk gen-ydotoold-service --out-dir ./build/systemd-user", "vhk gen-udev-uinput --out-dir ./build/udev"],
        ["dotoold/dotoolc", "ydotoold", "uinput helper lifecycle"],
        [f"backend={backend or 'unknown'}", f"pointer_usage={len(pointer_usage)}", f"text_usage={len(text_usage)}", f"direct_hotkey_heavy_macros={direct_hotkey_heavy}", f"pointer_injection={pointer_status}", *(f"uses={x}" for x in _usage_examples("pointer_injection"))],
        [f"pointer_injection={pointer_status}", f"text_injection={text_status}"],
        _lane_requirements("dotool-daemon", "ydotool-daemon", "uinput-permissions"),
    )

    portal_score = 0
    portal_signals = {pointer_recommended, input_capture_recommended, *pointer_mechanisms, *input_capture_mechanisms}
    if backend == "wayland" and (pointer_usage or capture_usage or input_capture_usage):
        portal_score = len(pointer_usage) * 9 + len(capture_usage) * 8 + len(input_capture_usage) * 12
        if any(token.startswith("portal:") for token in portal_signals if token):
            portal_score += 24
        if input_capture_status in {"ok", "limited"}:
            portal_score += 10
    add_lane(
        "portal-permissioned-input",
        "Portal-permissioned input lane",
        "portal-session",
        portal_score,
        "Portal-mediated input is the honest permissioned lane for capture/forward/control experiments on Wayland, especially when the compositor owns consent and session activation.",
        ["permissioned pointer control", "capture/forward flows", "sandbox-friendly or future libei/EIS experiments"],
        [
            "Consent and session activation remain part of the runtime contract; this is not an immediate always-on replacement for low-level helper paths.",
            "Portals expose transport and policy boundaries, so the operator still needs backend-specific review on the target desktop.",
        ],
        ["vhk doctor --json", f"vhk gen-capability-audit-pack {project_root_q} --quiet", f"vhk gen-verification-pack {project_root_q} --quiet"],
        ["XDG RemoteDesktop portal", "XDG InputCapture portal", "libei / EIS"],
        [f"backend={backend or 'unknown'}", f"pointer_usage={len(pointer_usage)}", f"capture_usage={len(capture_usage)}", f"input_capture_usage={len(input_capture_usage)}", f"pointer_injection={pointer_status}", f"input_capture={input_capture_status}", *(f"mechanism={x}" for x in list(dict.fromkeys(pointer_mechanisms + input_capture_mechanisms))[:4])],
        [f"pointer_injection={pointer_status}", f"input_capture={input_capture_status}"],
        _lane_requirements(capability="pointer_injection", requirement_type="portal") + _lane_requirements(capability="input_capture", requirement_type="portal"),
    )

    x11_score = 0
    if backend in {"x11", "i3"} and (text_usage or pointer_usage or bindings):
        x11_score = len(pointer_usage) * 14 + len(text_usage) * 10 + bindings * 12 + 24
    add_lane(
        "x11-native-replay",
        "X11-native replay lane",
        "x11-native",
        x11_score,
        "On X11, direct replay remains the most straightforward general lane, so helper complexity should only be added when it buys something real.",
        ["general key/pointer replay on X11", "window-manager-integrated hotkeys", "classic xdotool/xvkbd-style automation"],
        [
            "Do not project X11 comfort onto Wayland hosts; this lane is intentionally desktop-family specific.",
            "X11-native replay still deserves selector and timing review for long-lived or vision-heavy macros.",
        ],
        [f"vhk validate {project_root_q} --json", f"vhk gen-autokey-pack {project_root_q} --out-dir ./build/autokey_pack"],
        ["xdotool", "AutoKey", "AHK_X11"],
        [f"backend={backend or 'unknown'}", f"bindings={bindings}", f"pointer_usage={len(pointer_usage)}", f"text_usage={len(text_usage)}", *(f"uses={x}" for x in (_usage_examples("pointer_injection") + _usage_examples("text_injection"))[:4])],
        [f"pointer_injection={pointer_status}", f"text_injection={text_status}"],
        [],
    )

    lanes.sort(key=lambda item: (-int(item.get("score") or 0), str(item.get("title") or "")))
    recommended_lane_ids = [str(item.get("id") or "") for item in lanes if str(item.get("fit") or "") in {"strong", "good"}][:3]
    recommended_lane_ids = [lane_id for lane_id in recommended_lane_ids if lane_id]
    summary_parts: list[str] = []
    if recommended_lane_ids:
        title_map = {str(item.get("id") or ""): str(item.get("title") or item.get("id") or "lane") for item in lanes}
        top_titles = [title_map.get(lane_id, lane_id) for lane_id in recommended_lane_ids]
        if len(top_titles) == 1:
            summary_parts.append(f"Lead with {top_titles[0]}.")
        else:
            summary_parts.append(f"Lead with {', '.join(top_titles[:-1])}, and {top_titles[-1]}.")
    if backend == "wayland":
        summary_parts.append("Treat Wayland input as split lanes with explicit protocol, daemon, and portal boundaries.")
    elif backend in {"x11", "i3"}:
        summary_parts.append("Keep X11-native replay primary unless text packaging or adapter lanes clearly buy something.")
    else:
        summary_parts.append("Desktop backend is unspecified, so input-lane claims should stay review-oriented until the target session is pinned.")

    return {
        "summary": " ".join(part.strip() for part in summary_parts if part.strip()),
        "recommended_lane_ids": recommended_lane_ids,
        "lanes": lanes,
    }


def _route_portfolio(
    *,
    macro_route_profiles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}

    for item in macro_route_profiles:
        route_id = str(item.get('route_id') or '').strip()
        if not route_id:
            continue
        bucket = buckets.setdefault(route_id, {
            'route_id': route_id,
            'title': str(item.get('title') or route_id),
            'macro_count': 0,
            'fit_counts': Counter(),
            'activation_counts': Counter(),
            'surface_counts': Counter(),
            'macros': [],
            'learn_from': [],
            'evidence': [],
        })
        bucket['macro_count'] += 1
        fit = str(item.get('fit') or 'good').strip() or 'good'
        bucket['fit_counts'][fit] += 1
        activation_route_id = str(item.get('primary_activation_route_id') or '').strip()
        if activation_route_id:
            bucket['activation_counts'][activation_route_id] += 1
        execution_surface = str(item.get('execution_surface') or '').strip()
        if execution_surface:
            bucket['surface_counts'][execution_surface] += 1
        macro = str(item.get('macro') or '').strip()
        if macro:
            bucket['macros'].append(macro)
        for value in item.get('learn_from') or []:
            value = str(value).strip()
            if value and value not in bucket['learn_from']:
                bucket['learn_from'].append(value)
        for value in item.get('evidence') or []:
            value = str(value).strip()
            if value and value not in bucket['evidence']:
                bucket['evidence'].append(value)

    rows: list[dict[str, Any]] = []
    fit_rank = {'strong': 3, 'good': 2, 'conditional': 1, 'weak': 0}
    for bucket in buckets.values():
        fit_counts = dict(bucket.get('fit_counts') or {})
        activation_counts: Counter = bucket.get('activation_counts') or Counter()
        surface_counts: Counter = bucket.get('surface_counts') or Counter()
        dominant_fit = 'good'
        if fit_counts:
            dominant_fit = sorted(fit_counts.items(), key=lambda kv: (-int(kv[1]), -fit_rank.get(str(kv[0]), 0), str(kv[0])))[0][0]
        top_activation_routes = [route for route, _count in activation_counts.most_common(3)]
        top_surfaces = [surface for surface, _count in surface_counts.most_common(3)]
        rows.append({
            'route_id': str(bucket.get('route_id') or ''),
            'title': str(bucket.get('title') or ''),
            'macro_count': int(bucket.get('macro_count') or 0),
            'dominant_fit': dominant_fit,
            'fit_counts': fit_counts,
            'top_activation_routes': top_activation_routes,
            'top_execution_surfaces': top_surfaces,
            'example_macros': list(bucket.get('macros') or [])[:5],
            'learn_from': list(bucket.get('learn_from') or [])[:5],
            'evidence': list(bucket.get('evidence') or [])[:6],
        })

    rows.sort(key=lambda item: (-int(item.get('macro_count') or 0), str(item.get('title') or '')))
    return rows


def _export_promotion_plan(
    *,
    macro_export_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}

    def _priority_for(surface_id: str, fits: Counter) -> str:
        if surface_id in {'remapper-export', 'text-package-export'}:
            return 'high' if fits.get('strong') or fits.get('good') else 'medium'
        if surface_id == 'watcher-service-export':
            return 'high' if (fits.get('strong') or 0) >= 1 else 'medium'
        if surface_id == 'helper-route-dossier':
            return 'medium'
        return 'medium'

    for item in macro_export_candidates:
        surface_id = str(item.get('export_surface_id') or '').strip()
        if not surface_id:
            continue
        bucket = buckets.setdefault(surface_id, {
            'export_surface_id': surface_id,
            'title': str(item.get('title') or surface_id),
            'fit_counts': Counter(),
            'route_ids': Counter(),
            'macros': [],
            'tool_family': [],
            'commands': [],
            'activation_routes': Counter(),
            'reasons': [],
            'risks': [],
            'evidence': [],
        })
        fit = str(item.get('fit') or 'good').strip() or 'good'
        bucket['fit_counts'][fit] += 1
        route_id = str(item.get('route_id') or '').strip()
        if route_id:
            bucket['route_ids'][route_id] += 1
        macro = str(item.get('macro') or '').strip()
        if macro:
            bucket['macros'].append(macro)
        for value in item.get('tool_family') or []:
            value = str(value).strip()
            if value and value not in bucket['tool_family']:
                bucket['tool_family'].append(value)
        for value in item.get('commands') or []:
            value = str(value).strip()
            if value and value not in bucket['commands']:
                bucket['commands'].append(value)
        activation_route = str(item.get('primary_activation_route_id') or '').strip()
        if activation_route:
            bucket['activation_routes'][activation_route] += 1
        reason = str(item.get('reason') or '').strip()
        if reason and reason not in bucket['reasons']:
            bucket['reasons'].append(reason)
        for value in item.get('risks') or []:
            value = str(value).strip()
            if value and value not in bucket['risks']:
                bucket['risks'].append(value)
        for value in item.get('evidence') or []:
            value = str(value).strip()
            if value and value not in bucket['evidence']:
                bucket['evidence'].append(value)

    rows: list[dict[str, Any]] = []
    fit_rank = {'strong': 3, 'good': 2, 'conditional': 1, 'weak': 0}
    for bucket in buckets.values():
        fit_counts: Counter = bucket.get('fit_counts') or Counter()
        dominant_fit = 'good'
        if fit_counts:
            dominant_fit = sorted(fit_counts.items(), key=lambda kv: (-int(kv[1]), -fit_rank.get(str(kv[0]), 0), str(kv[0])))[0][0]
        route_ids = [route_id for route_id, _count in (bucket.get('route_ids') or Counter()).most_common(3)]
        activation_routes = [route_id for route_id, _count in (bucket.get('activation_routes') or Counter()).most_common(3)]
        surface_id = str(bucket.get('export_surface_id') or '')
        rows.append({
            'export_surface_id': surface_id,
            'title': str(bucket.get('title') or ''),
            'priority': _priority_for(surface_id, fit_counts),
            'macro_count': len(list(bucket.get('macros') or [])),
            'dominant_fit': dominant_fit,
            'fit_counts': dict(fit_counts),
            'route_ids': route_ids,
            'macros': list(bucket.get('macros') or [])[:8],
            'tool_family': list(bucket.get('tool_family') or [])[:6],
            'commands': list(bucket.get('commands') or [])[:6],
            'activation_routes': activation_routes,
            'reasons': list(bucket.get('reasons') or [])[:3],
            'risks': list(bucket.get('risks') or [])[:6],
            'evidence': list(bucket.get('evidence') or [])[:6],
        })

    priority_rank = {'high': 0, 'medium': 1, 'low': 2}
    rows.sort(key=lambda item: (priority_rank.get(str(item.get('priority') or 'medium'), 9), -int(item.get('macro_count') or 0), str(item.get('title') or '')))
    return rows




def _promotion_input_lane_plan(
    *,
    project,
    export_promotion_plan: list[dict[str, Any]],
    input_lane_dossier: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Map promotion surfaces to the Linux-native input lanes they should actually ship through.

    This keeps `plan-project` honest about which *lane* owns the shipped experience
    instead of only naming export surfaces. Some surfaces are primarily input lanes,
    while others are intentionally orthogonal (watcher services, launchers).
    """

    backend = str(getattr(getattr(project, 'settings', None), 'desktop_backend', None) or '').strip().lower()
    dossier = dict(input_lane_dossier or {})
    lane_rows = [dict(item) for item in list(dossier.get('lanes') or []) if isinstance(item, Mapping)]
    lanes_by_id = {str(item.get('id') or ''): item for item in lane_rows if str(item.get('id') or '').strip()}
    recommended_lane_ids = [str(x) for x in list(dossier.get('recommended_lane_ids') or []) if str(x)]
    recommended_set = set(recommended_lane_ids)

    def _candidate_lane_ids(surface_id: str) -> list[str]:
        if surface_id == 'text-package-export':
            return ['clipboard-text-lane', 'virtual-keyboard-text-fastpath', 'x11-native-replay']
        if surface_id == 'remapper-export':
            if backend in {'x11', 'i3'}:
                return ['x11-native-replay', 'daemon-backed-uinput-playback']
            return ['daemon-backed-uinput-playback', 'x11-native-replay', 'portal-permissioned-input']
        if surface_id == 'helper-route-dossier':
            if backend in {'x11', 'i3'}:
                return ['x11-native-replay', 'portal-permissioned-input', 'daemon-backed-uinput-playback']
            return ['portal-permissioned-input', 'daemon-backed-uinput-playback', 'virtual-keyboard-text-fastpath', 'clipboard-text-lane']
        if surface_id == 'launcher-surface-export':
            return ['clipboard-text-lane', 'x11-native-replay', 'virtual-keyboard-text-fastpath']
        return []

    def _lane_sort_key(lane: Mapping[str, Any], *, candidate_order: Mapping[str, int]) -> tuple[int, int, int, int, str]:
        lane_id = str(lane.get('id') or '')
        fit = str(lane.get('fit') or 'weak')
        fit_rank = {'strong': 0, 'good': 1, 'conditional': 2, 'weak': 3}
        candidate_rank = int(candidate_order.get(lane_id, 99))
        rec_rank = 0 if lane_id in recommended_set else 1
        score_rank = -int(lane.get('score') or 0)
        return (candidate_rank, fit_rank.get(fit, 9), rec_rank, score_rank, str(lane.get('title') or lane_id))

    def _pick_lanes(surface_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        candidate_ids = _candidate_lane_ids(surface_id)
        available = [lanes_by_id[lane_id] for lane_id in candidate_ids if lane_id in lanes_by_id]
        if not available:
            return {}, []
        candidate_order = {lane_id: index for index, lane_id in enumerate(candidate_ids)}
        non_weak = [lane for lane in available if str(lane.get('fit') or 'weak') != 'weak']
        ranked_pool = non_weak or available
        ordered = sorted(ranked_pool, key=lambda lane: _lane_sort_key(lane, candidate_order=candidate_order))
        primary = dict(ordered[0])
        alternate_pool = [lane for lane in available if str(lane.get('id') or '') != str(primary.get('id') or '')]
        alternates = [dict(item) for item in sorted(alternate_pool, key=lambda lane: _lane_sort_key(lane, candidate_order=candidate_order))[:2]]
        return primary, alternates

    def _surface_title(surface_id: str) -> str:
        titles = {
            'text-package-export': 'Text surface shipping lane',
            'remapper-export': 'Remapper shipping lane',
            'helper-route-dossier': 'Helper-route shipping lane',
            'watcher-service-export': 'Watcher ownership lane',
            'launcher-surface-export': 'Launcher ownership lane',
        }
        return titles.get(surface_id, surface_id)

    def _surface_summary(surface_id: str, primary: Mapping[str, Any] | None) -> str:
        primary_title = str((primary or {}).get('title') or (primary or {}).get('id') or 'no primary lane')
        if surface_id == 'text-package-export':
            return f'Ship text-heavy macros through {primary_title} first, then keep faster helper typing as an optional acceleration path instead of the default product surface.'
        if surface_id == 'remapper-export':
            return f'Treat the remapper export as adjacent to {primary_title}: low-latency key ownership belongs near the input lane, while richer workflow logic stays in VHK.'
        if surface_id == 'helper-route-dossier':
            return f'Keep the helper surface review-led and explicit around {primary_title}, with host checks and fallback routes written down before claiming broad Linux coverage.'
        if surface_id == 'watcher-service-export':
            return 'This surface is primarily service/event ownership, so input lanes are secondary and should be chosen per downstream macro rather than treated as the flagship story.'
        if surface_id == 'launcher-surface-export':
            return 'This surface is primarily a launcher/action-entry surface; input lanes matter only for whichever downstream macro the launcher wakes.'
        return 'Keep the shipping lane explicit instead of assuming one export surface speaks for all Linux sessions.'

    def _shipping_posture(surface_id: str, primary: Mapping[str, Any] | None) -> str:
        primary = primary or {}
        fit = str(primary.get('fit') or 'weak')
        if surface_id == 'watcher-service-export':
            return 'orthogonal'
        if surface_id == 'launcher-surface-export':
            return 'orthogonal'
        if surface_id == 'helper-route-dossier':
            return 'reviewed'
        if surface_id == 'remapper-export':
            if backend in {'x11', 'i3'} and fit in {'strong', 'good'}:
                return 'flagship'
            return 'specialist' if fit in {'strong', 'good'} else 'reviewed'
        if surface_id == 'text-package-export':
            return 'flagship' if fit in {'strong', 'good'} else 'reviewed'
        return 'reviewed' if fit in {'conditional', 'weak'} else 'specialist'

    def _merge_unique(*groups: Iterable[str]) -> list[str]:
        out: list[str] = []
        for group in groups:
            for value in group:
                value = str(value).strip()
                if value and value not in out:
                    out.append(value)
        return out

    rows: list[dict[str, Any]] = []
    for item in export_promotion_plan:
        surface_id = str(item.get('export_surface_id') or '').strip()
        if not surface_id:
            continue
        primary, alternates = _pick_lanes(surface_id)
        primary_id = str(primary.get('id') or '')
        alternate_ids = [str(alt.get('id') or '') for alt in alternates if str(alt.get('id') or '')]
        host_requirement_ids = _merge_unique(
            list(primary.get('host_requirement_ids') or []),
            *(list(alt.get('host_requirement_ids') or []) for alt in alternates),
        )
        commands = _merge_unique(
            list(item.get('commands') or []),
            list(primary.get('commands') or []),
            *(list(alt.get('commands') or []) for alt in alternates),
        )[:8]
        evidence = _merge_unique(
            list(item.get('evidence') or []),
            list(primary.get('evidence') or []),
            *(list(alt.get('evidence') or []) for alt in alternates),
        )[:8]
        cautions = _merge_unique(
            list(primary.get('cautions') or []),
            *(list(alt.get('cautions') or []) for alt in alternates),
        )[:6]
        learn_from = _merge_unique(
            list(item.get('tool_family') or []),
            list(primary.get('learn_from') or []),
            *(list(alt.get('learn_from') or []) for alt in alternates),
        )[:6]
        rows.append({
            'export_surface_id': surface_id,
            'title': _surface_title(surface_id),
            'shipping_posture': _shipping_posture(surface_id, primary),
            'primary_input_lane_id': primary_id or None,
            'primary_input_lane_title': str(primary.get('title') or primary_id or '') or None,
            'primary_input_lane_fit': str(primary.get('fit') or 'unknown') if primary_id else 'orthogonal',
            'alternate_input_lane_ids': alternate_ids,
            'recommended_input_lane_ids': _candidate_lane_ids(surface_id),
            'host_requirement_ids': host_requirement_ids,
            'commands': commands,
            'learn_from': learn_from,
            'evidence': evidence,
            'cautions': cautions,
            'summary': _surface_summary(surface_id, primary),
        })

    posture_rank = {'flagship': 0, 'specialist': 1, 'reviewed': 2, 'orthogonal': 3}
    rows.sort(key=lambda item: (posture_rank.get(str(item.get('shipping_posture') or 'reviewed'), 9), str(item.get('title') or '')))
    return rows



def _promotion_activation_route_plan(
    *,
    project,
    export_promotion_plan: list[dict[str, Any]],
    activation_routes: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Map promotion surfaces to the activation routes that actually own startup.

    Linux shipping posture is not only about *which input lane* a surface uses.
    Text packages, remapper exports, watcher services, portal sessions, and
    launchers all have different startup owners and steady-state expectations.
    This keeps those lifecycle routes explicit in planner output.
    """

    backend = str(getattr(getattr(project, 'settings', None), 'desktop_backend', None) or '').strip().lower()
    route_rows = [dict(item) for item in list(activation_routes or []) if isinstance(item, Mapping)]
    routes_by_id = {str(item.get('id') or ''): item for item in route_rows if str(item.get('id') or '').strip()}

    def _merge_unique(*groups: Iterable[str]) -> list[str]:
        out: list[str] = []
        for group in groups:
            for value in group:
                value = str(value).strip()
                if value and value not in out:
                    out.append(value)
        return out

    def _default_route_ids(surface_id: str) -> list[str]:
        if surface_id == 'text-package-export':
            return ['text-surface-route', 'launcher-entrypoint', 'native-trigger-route']
        if surface_id == 'remapper-export':
            return ['remapper-route', 'native-trigger-route', 'launcher-entrypoint']
        if surface_id == 'watcher-service-export':
            return ['watcher-service-route', 'launcher-entrypoint']
        if surface_id == 'helper-route-dossier':
            if backend == 'wayland':
                return ['portal-shortcuts-route', 'native-trigger-route', 'helper-input-route', 'launcher-entrypoint', 'remapper-route']
            return ['native-trigger-route', 'helper-input-route', 'launcher-entrypoint', 'remapper-route']
        if surface_id == 'launcher-surface-export':
            return ['launcher-entrypoint']
        return ['launcher-entrypoint']

    def _candidate_route_ids(surface_id: str, observed_ids: list[str]) -> list[str]:
        return _merge_unique(observed_ids, _default_route_ids(surface_id))

    def _route_sort_key(route: Mapping[str, Any], *, candidate_order: Mapping[str, int]) -> tuple[int, int, int, int, str]:
        route_id = str(route.get('id') or '')
        fit = str(route.get('fit') or 'weak')
        fit_rank = {'strong': 0, 'good': 1, 'conditional': 2, 'weak': 3}
        kind = str(route.get('activation_kind') or '')
        kind_rank = {'user_service': 0, 'system_or_user_service': 1, 'desktop_config': 2, 'portal_session': 3, 'helper_daemon': 4, 'launcher': 5}.get(kind, 9)
        candidate_rank = int(candidate_order.get(route_id, 99))
        return (candidate_rank, fit_rank.get(fit, 9), kind_rank, -int(route.get('score') or 0), str(route.get('title') or route_id))

    def _pick_routes(surface_id: str, observed_ids: list[str]) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
        candidate_ids = _candidate_route_ids(surface_id, observed_ids)
        available = [routes_by_id[route_id] for route_id in candidate_ids if route_id in routes_by_id]
        if not available:
            return {}, [], candidate_ids
        candidate_order = {route_id: index for index, route_id in enumerate(candidate_ids)}
        non_weak = [route for route in available if str(route.get('fit') or 'weak') != 'weak']
        ranked_pool = non_weak or available
        ordered = sorted(ranked_pool, key=lambda route: _route_sort_key(route, candidate_order=candidate_order))
        primary = dict(ordered[0])
        alternate_pool = [route for route in available if str(route.get('id') or '') != str(primary.get('id') or '')]
        alternates = [dict(item) for item in sorted(alternate_pool, key=lambda route: _route_sort_key(route, candidate_order=candidate_order))[:2]]
        return primary, alternates, candidate_ids

    def _surface_title(surface_id: str) -> str:
        titles = {
            'text-package-export': 'Text surface startup route',
            'remapper-export': 'Remapper startup route',
            'helper-route-dossier': 'Helper-route startup route',
            'watcher-service-export': 'Watcher startup route',
            'launcher-surface-export': 'Launcher startup route',
        }
        return titles.get(surface_id, surface_id)

    def _startup_posture(surface_id: str, primary: Mapping[str, Any] | None) -> str:
        primary = primary or {}
        kind = str(primary.get('activation_kind') or '')
        if surface_id == 'launcher-surface-export':
            return 'launcher-first'
        if kind == 'portal_session':
            return 'session-bound'
        if kind in {'user_service', 'system_or_user_service'}:
            return 'resident'
        if surface_id == 'helper-route-dossier' or kind == 'helper_daemon':
            return 'reviewed'
        if kind == 'launcher':
            return 'launcher-first'
        if surface_id == 'watcher-service-export':
            return 'resident'
        return 'reviewed' if kind == 'desktop_config' else 'orthogonal'

    def _surface_summary(surface_id: str, primary: Mapping[str, Any] | None) -> str:
        primary_title = str((primary or {}).get('title') or (primary or {}).get('id') or 'no primary activation route')
        if surface_id == 'text-package-export':
            return f'Ship the text surface through {primary_title} so snippets, packages, and app-scoped text stay under one service/startup contract instead of being reconstructed from generic hotkeys.'
        if surface_id == 'remapper-export':
            return f'Let {primary_title} own startup for low-latency remap behavior, while richer workflow meaning stays in VHK instead of being buried inside the remapper config.'
        if surface_id == 'watcher-service-export':
            return f'Own the watcher surface as {primary_title}, because the product value depends on background restarts, event intake, and service lifecycle more than on a generic trigger story.'
        if surface_id == 'helper-route-dossier':
            return f'Keep helper-sensitive startup explicit around {primary_title}, because portal sessions, helper daemons, and hotkey wake-up paths are separate Linux contracts that must stay reviewable.'
        if surface_id == 'launcher-surface-export':
            return f'Treat {primary_title} as the honest wake-up route for launcher-driven workflows, with downstream input handled by the selected macro rather than by the launcher itself.'
        return 'Keep startup ownership explicit per promotion surface instead of assuming one trigger model fits every Linux session.'

    rows: list[dict[str, Any]] = []
    for item in export_promotion_plan:
        surface_id = str(item.get('export_surface_id') or '').strip()
        if not surface_id:
            continue
        observed_ids = [str(x) for x in list(item.get('activation_routes') or []) if str(x)]
        primary, alternates, recommended_ids = _pick_routes(surface_id, observed_ids)
        primary_id = str(primary.get('id') or '').strip()
        alternate_ids = [str(alt.get('id') or '').strip() for alt in alternates if str(alt.get('id') or '').strip()]
        host_requirement_ids = _merge_unique(
            list(primary.get('depends_on_requirements') or []),
            *(list(alt.get('depends_on_requirements') or []) for alt in alternates),
        )
        alternative_group_ids = _merge_unique(
            list(primary.get('depends_on_alternative_groups') or []),
            *(list(alt.get('depends_on_alternative_groups') or []) for alt in alternates),
        )
        commands = _merge_unique(
            list(item.get('commands') or []),
            list(primary.get('commands') or []),
            list(primary.get('verification_commands') or []),
            *(list(alt.get('commands') or []) for alt in alternates),
            *(list(alt.get('verification_commands') or []) for alt in alternates),
        )[:8]
        evidence = _merge_unique(
            list(item.get('evidence') or []),
            list(primary.get('evidence') or []),
            *(list(alt.get('evidence') or []) for alt in alternates),
        )[:8]
        cautions = _merge_unique(
            list(item.get('risks') or []),
            list(primary.get('notes') or []),
            *(list(alt.get('notes') or []) for alt in alternates),
        )[:6]
        rows.append({
            'export_surface_id': surface_id,
            'title': _surface_title(surface_id),
            'startup_posture': _startup_posture(surface_id, primary),
            'primary_activation_route_id': primary_id or None,
            'primary_activation_route_title': str(primary.get('title') or primary_id or '') or None,
            'primary_activation_kind': str(primary.get('activation_kind') or 'unknown') if primary_id else 'orthogonal',
            'primary_activation_fit': str(primary.get('fit') or 'unknown') if primary_id else 'orthogonal',
            'startup_owner': str(primary.get('startup_owner') or '') or None,
            'steady_state': str(primary.get('steady_state') or '') or None,
            'entrypoint': str(primary.get('entrypoint') or '') or None,
            'alternate_activation_route_ids': alternate_ids,
            'recommended_activation_route_ids': recommended_ids,
            'host_requirement_ids': host_requirement_ids,
            'alternative_requirement_group_ids': alternative_group_ids,
            'commands': commands,
            'evidence': evidence,
            'cautions': cautions,
            'summary': _surface_summary(surface_id, primary),
        })

    posture_rank = {'resident': 0, 'session-bound': 1, 'launcher-first': 2, 'reviewed': 3, 'orthogonal': 4}
    rows.sort(key=lambda item: (posture_rank.get(str(item.get('startup_posture') or 'reviewed'), 9), str(item.get('title') or '')))
    return rows


def _promotion_operator_control_plan(
    *,
    project,
    export_promotion_plan: list[dict[str, Any]],
    promotion_input_lane_plan: list[dict[str, Any]] | None = None,
    promotion_activation_route_plan: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Map promotion surfaces to the operator-control lane that keeps them healthy.

    Shipping and startup posture still leave one Linux-native truth implicit: what an
    operator actually touches to inspect status, reload config, or recover drift.
    Text services, remappers, watcher daemons, portal sessions, and launchers all
    want different control loops, so planner output should make those explicit.
    """

    backend = str(getattr(getattr(project, 'settings', None), 'desktop_backend', None) or '').strip().lower()
    project_root_q = shlex.quote(str(Path(getattr(project, 'root_dir', '.'))))
    promotion_rows = [dict(item) for item in list(export_promotion_plan or []) if isinstance(item, Mapping)]
    input_rows = {
        str(item.get('export_surface_id') or ''): dict(item)
        for item in list(promotion_input_lane_plan or [])
        if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()
    }
    route_rows = {
        str(item.get('export_surface_id') or ''): dict(item)
        for item in list(promotion_activation_route_plan or [])
        if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()
    }

    def _merge_unique(*groups: Iterable[str]) -> list[str]:
        out: list[str] = []
        for group in groups:
            for value in group:
                value = str(value).strip()
                if value and value not in out:
                    out.append(value)
        return out

    def _surface_title(surface_id: str) -> str:
        titles = {
            'text-package-export': 'Text surface operator control',
            'remapper-export': 'Remapper operator control',
            'helper-route-dossier': 'Helper-route operator control',
            'watcher-service-export': 'Watcher operator control',
            'launcher-surface-export': 'Launcher operator control',
        }
        return titles.get(surface_id, surface_id)

    rows: list[dict[str, Any]] = []
    for item in promotion_rows:
        surface_id = str(item.get('export_surface_id') or '').strip()
        if not surface_id:
            continue
        input_item = dict(input_rows.get(surface_id) or {})
        route_item = dict(route_rows.get(surface_id) or {})
        primary_lane_id = str(input_item.get('primary_input_lane_id') or '').strip() or None
        primary_route_id = str(route_item.get('primary_activation_route_id') or '').strip() or None
        primary_route_kind = str(route_item.get('primary_activation_kind') or '').strip() or None
        base_commands = _merge_unique(
            list(item.get('commands') or []),
            list(input_item.get('commands') or []),
            list(route_item.get('commands') or []),
        )
        base_requirements = _merge_unique(
            list(input_item.get('host_requirement_ids') or []),
            list(route_item.get('host_requirement_ids') or []),
        )
        base_evidence = _merge_unique(
            list(item.get('evidence') or []),
            list(input_item.get('evidence') or []),
            list(route_item.get('evidence') or []),
        )
        cautions: list[str] = []
        commands: list[str] = []
        control_lane_id = None
        control_lane_title = None
        control_posture = 'reviewed'
        operator_owner = None
        status_surface = None
        reload_surface = None
        log_surface = None
        summary = ''

        if surface_id == 'text-package-export':
            control_lane_id = 'text-service-control'
            control_lane_title = 'Text service control lane'
            control_posture = 'service-managed'
            operator_owner = 'text expander service / package operator'
            status_surface = 'Espanso status/service health plus VHK readiness/setup review'
            reload_surface = 'Restart the text service after package or config refresh'
            log_surface = 'User-service logs or espanso runtime/error output'
            summary = 'Treat shipped text packages as a service-managed surface with explicit status and restart loops, not just as generated match files.'
            cautions = [
                'Clipboard ownership and app-specific include/exclude rules still need per-desktop review.',
                'Text packaging should stay the flagship path even when faster helper typing is available as an optional acceleration lane.',
            ]
            commands = _merge_unique(
                ['espanso status', 'espanso restart', f'vhk gen-espanso {project_root_q} --out-dir ./build/espanso', f'vhk gen-setup-pack {project_root_q} --quiet'],
                base_commands,
            )[:8]
        elif surface_id == 'remapper-export':
            if primary_route_id == 'remapper-route':
                control_lane_id = 'remapper-service-control'
                control_lane_title = 'Remapper service control lane'
                control_posture = 'daemon-reviewed'
                operator_owner = 'remapper daemon / low-latency key layer operator'
                status_surface = 'Remapper service state plus key-event monitoring on the target host'
                reload_surface = 'Reload remapper config or restart the remapper service after export changes'
                log_surface = 'System or user service logs plus route-selection/readiness docs'
                summary = 'Treat remapper shipping as a reviewed daemon/service loop with explicit reload and rollback ownership.'
                cautions = [
                    'Low-latency remappers can shadow the desktop quickly, so rollback and rescue sequences must stay visible.',
                    'Application-specific context still depends on target compositor or session naming conventions.',
                ]
                commands = _merge_unique(
                    base_commands,
                    ['sudo keyd reload', 'sudo journalctl -eu keyd', f'vhk gen-route-selection-pack {project_root_q} --quiet'],
                )[:8]
            else:
                control_lane_id = 'native-trigger-control'
                control_lane_title = 'Native trigger control lane'
                control_posture = 'reviewed'
                operator_owner = 'WM/compositor config operator'
                status_surface = 'Generated binding config plus target-session smoke checks'
                reload_surface = 'Reload the compositor/WM binding layer after config updates'
                log_surface = 'Desktop/session logs plus route-selection review docs'
                summary = 'When remapper exports ship through native triggers instead of a dedicated daemon, control stays in the desktop config lane.'
                cautions = [
                    'Reload semantics vary by compositor, so keep generated config reviewable before claiming hot-swap support.',
                ]
                commands = _merge_unique(base_commands, [f'vhk gen-trigger-pack {project_root_q} --quiet', f'vhk gen-route-selection-pack {project_root_q} --quiet'])[:8]
        elif surface_id == 'helper-route-dossier':
            if primary_route_kind == 'portal_session':
                control_lane_id = 'portal-session-control'
                control_lane_title = 'Portal session control lane'
                control_posture = 'session-managed'
                operator_owner = 'portal session + user consent flow'
                status_surface = 'Portal session/binding state plus doctor and host-contract review'
                reload_surface = 'Recreate the session and rebind shortcuts/devices when consent or desktop state changes'
                log_surface = 'Portal backend state and capability-audit/readiness artifacts'
                summary = 'Portal-backed helper surfaces should be operated like session objects with explicit recreate/rebind loops rather than as invisible always-on hooks.'
                cautions = [
                    'Portal sessions can be valid yet inactive until the compositor chooses to activate them.',
                    'Consent, session restore, and backend availability can drift independently of macro logic.',
                ]
                commands = _merge_unique(
                    base_commands,
                    [f'vhk doctor --json', f'vhk gen-host-contract-pack {project_root_q} --quiet', f'vhk gen-capability-audit-pack {project_root_q} --quiet'],
                )[:8]
            else:
                control_lane_id = 'helper-daemon-control'
                control_lane_title = 'Helper daemon control lane'
                control_posture = 'daemon-reviewed'
                operator_owner = 'helper daemon / socket-backed adapter owner'
                status_surface = 'Helper daemon readiness plus doctor snapshot'
                reload_surface = 'Restart the helper daemon or reattach the adapter when socket/device truth changes'
                log_surface = 'System/user service logs plus readiness/capability-audit docs'
                summary = 'Helper-backed surfaces should ship with daemon truth and socket truth visible, not only with helper binaries present on PATH.'
                cautions = [
                    'Daemon-ready and helper-installed are different truths and should stay reviewable.',
                    'Wayland helper viability still varies by compositor, permissions, and daemon lifecycle.',
                ]
                commands = _merge_unique(
                    base_commands,
                    [f'vhk doctor --json', f'vhk gen-readiness-pack {project_root_q} --quiet', f'vhk gen-capability-audit-pack {project_root_q} --quiet'],
                )[:8]
        elif surface_id == 'watcher-service-export':
            control_lane_id = 'watcher-service-control'
            control_lane_title = 'Watcher service control lane'
            control_posture = 'service-managed'
            operator_owner = 'systemd user service / watcher plane operator'
            status_surface = 'User-service status plus watcher/bus health review'
            reload_surface = 'Restart or socket-bounce the watcher service after config changes'
            log_surface = 'journalctl --user and host-dossier/rehearsal artifacts'
            summary = 'Watcher-heavy promotion surfaces should be run like service planes with explicit status, restart, and log collection ownership.'
            cautions = [
                'Socket activation can hide dormant failures until the first event lands, so cold-start checks still matter.',
            ]
            commands = _merge_unique(
                base_commands,
                [f'vhk gen-service-compose-pack {project_root_q} --quiet', f'vhk gen-host-dossier-pack {project_root_q} --quiet', f'vhk gen-host-rehearsal-pack {project_root_q} --quiet'],
            )[:8]
        elif surface_id == 'launcher-surface-export':
            control_lane_id = 'launcher-entry-control'
            control_lane_title = 'Launcher entry control lane'
            control_posture = 'manual-entry'
            operator_owner = 'desktop entry / launcher / palette operator'
            status_surface = 'Desktop-entry visibility plus validate/plan smoke checks'
            reload_surface = 'Regenerate launcher artifacts and refresh desktop metadata'
            log_surface = 'On-demand runner output and validation docs'
            summary = 'Launcher surfaces are operator-visible entrypoints, so their control loop is mostly generation, visibility, and smoke testing rather than daemon management.'
            cautions = [
                'Launchers only prove wake-up and discovery; downstream macro lanes still need their own runtime checks.',
            ]
            commands = _merge_unique(base_commands, [f'vhk gen-desktop-entry {project_root_q}', f'vhk validate {project_root_q} --json'])[:8]
        else:
            control_lane_id = 'review-control'
            control_lane_title = 'Review control lane'
            control_posture = 'reviewed'
            operator_owner = 'operator review loop'
            status_surface = 'Planner and readiness docs'
            reload_surface = 'Regenerate artifacts and re-run plan/review docs'
            log_surface = 'Review docs and runner logs'
            summary = 'Keep operator control explicit whenever no single Linux-native control lane dominates the promoted surface.'
            cautions = ['Do not assume one generic reload or status loop spans all desktops.']
            commands = _merge_unique(base_commands, [f'vhk plan-project {project_root_q} --json', f'vhk gen-promotion-pack {project_root_q} --quiet'])[:8]

        evidence = _merge_unique(
            base_evidence,
            [
                f'backend={backend or "unknown"}',
                f'primary_input_lane={primary_lane_id or "none"}',
                f'primary_activation_route={primary_route_id or "none"}',
                f'primary_activation_kind={primary_route_kind or "none"}',
            ],
        )[:8]

        rows.append({
            'export_surface_id': surface_id,
            'title': _surface_title(surface_id),
            'control_posture': control_posture,
            'primary_control_lane_id': control_lane_id,
            'primary_control_lane_title': control_lane_title,
            'primary_input_lane_id': primary_lane_id,
            'primary_activation_route_id': primary_route_id,
            'primary_activation_kind': primary_route_kind,
            'operator_owner': operator_owner,
            'status_surface': status_surface,
            'reload_surface': reload_surface,
            'log_surface': log_surface,
            'host_requirement_ids': base_requirements,
            'commands': commands,
            'cautions': cautions,
            'evidence': evidence,
            'summary': summary,
        })

    posture_rank = {'service-managed': 0, 'session-managed': 1, 'daemon-reviewed': 2, 'manual-entry': 3, 'reviewed': 4, 'orthogonal': 5}
    rows.sort(key=lambda item: (posture_rank.get(str(item.get('control_posture') or 'reviewed'), 9), str(item.get('title') or '')))
    return rows



def _promotion_recovery_plan(
    *,
    project,
    export_promotion_plan: list[dict[str, Any]],
    promotion_input_lane_plan: list[dict[str, Any]] | None = None,
    promotion_activation_route_plan: list[dict[str, Any]] | None = None,
    promotion_operator_control_plan: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Map promotion surfaces to the first-response and rollback lane they need."""

    backend = str(getattr(getattr(project, 'settings', None), 'desktop_backend', None) or '').strip().lower()
    project_root_q = shlex.quote(str(Path(getattr(project, 'root_dir', '.'))))
    promotion_rows = [dict(item) for item in list(export_promotion_plan or []) if isinstance(item, Mapping)]
    input_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_input_lane_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    route_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_activation_route_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    control_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_operator_control_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}

    def _merge_unique(*groups: Iterable[str]) -> list[str]:
        out: list[str] = []
        for group in groups:
            for value in group:
                value = str(value).strip()
                if value and value not in out:
                    out.append(value)
        return out

    def _surface_title(surface_id: str) -> str:
        return {
            'text-package-export': 'Text surface recovery lane',
            'remapper-export': 'Remapper recovery lane',
            'helper-route-dossier': 'Helper-route recovery lane',
            'watcher-service-export': 'Watcher recovery lane',
            'launcher-surface-export': 'Launcher recovery lane',
        }.get(surface_id, surface_id)

    rows: list[dict[str, Any]] = []
    for item in promotion_rows:
        surface_id = str(item.get('export_surface_id') or '').strip()
        if not surface_id:
            continue
        input_item = dict(input_rows.get(surface_id) or {})
        route_item = dict(route_rows.get(surface_id) or {})
        control_item = dict(control_rows.get(surface_id) or {})
        primary_lane_id = str(input_item.get('primary_input_lane_id') or '').strip() or None
        primary_route_id = str(route_item.get('primary_activation_route_id') or '').strip() or None
        primary_route_kind = str(route_item.get('primary_activation_kind') or '').strip() or None
        primary_control_lane_id = str(control_item.get('primary_control_lane_id') or '').strip() or None
        base_commands = _merge_unique(list(item.get('commands') or []), list(input_item.get('commands') or []), list(route_item.get('commands') or []), list(control_item.get('commands') or []))
        base_requirements = _merge_unique(list(input_item.get('host_requirement_ids') or []), list(route_item.get('host_requirement_ids') or []), list(control_item.get('host_requirement_ids') or []))
        base_evidence = _merge_unique(list(item.get('evidence') or []), list(input_item.get('evidence') or []), list(route_item.get('evidence') or []), list(control_item.get('evidence') or []))

        recovery_lane_id = 'review-recovery'
        recovery_lane_title = 'Review recovery lane'
        recovery_posture = 'review-led'
        failure_boundary = 'Planner/review boundary'
        first_response = 'Re-run planner and readiness docs, then fall back to the last verified launcher/text baseline before widening scope again.'
        rollback_surface = 'Regenerate reviewed artifacts and remove the fragile surface until a healthier lane is verified.'
        reentry_check = 'Re-run `vhk plan-project`, `vhk gen-promotion-pack`, and the relevant readiness docs before claiming the surface recovered.'
        summary = 'Keep recovery explicit whenever no single Linux-native rollback lane dominates the promoted surface.'
        cautions: list[str] = []
        commands: list[str] = []

        if surface_id == 'text-package-export':
            recovery_lane_id = 'text-service-recovery'; recovery_lane_title = 'Text service recovery lane'; recovery_posture = 'service-restart'
            failure_boundary = 'Text expander service, package config, and keyboard-layout drift'
            first_response = 'Check the text service status/logs, restart it, and verify one global plus one scoped expansion before debugging macro content.'
            rollback_surface = 'Stop/unregister the text service or remove the generated package and fall back to launcher/manual clipboard flows while the package is repaired.'
            reentry_check = 'Run `espanso status`, re-test a representative expansion, and refresh setup/readiness docs on the target desktop.'
            summary = 'Recover text shipping like a restartable service first, then fall back to clipboard/manual baselines instead of forcing literal replay under stress.'
            cautions = ['Wayland app-specific configs remain limited, so recovery sometimes means temporarily simplifying scope rather than fighting the compositor.', 'New keyboards or layout changes can require a text-service restart before expansions type cleanly again.']
            commands = _merge_unique(['espanso status', 'espanso log', 'espanso restart', 'espanso stop', f'vhk gen-setup-pack {project_root_q} --quiet'], base_commands)[:10]
        elif surface_id == 'remapper-export':
            if primary_route_id == 'remapper-route':
                recovery_lane_id = 'remapper-rollback-recovery'; recovery_lane_title = 'Remapper rollback lane'; recovery_posture = 'rollback-first'
                failure_boundary = 'Low-latency remapper daemon and global input ownership'
                first_response = 'Use the remapper rescue path, reload or stop the remapper, and restore desktop control before investigating feature regressions.'
                rollback_surface = 'Disable/remove the generated remapper config and return to launcher/native-trigger fallbacks while the remapper export is repaired.'
                reentry_check = 'Reload the remapper, verify one safe chord, then rerun route-selection/readiness review before re-enabling the full key layer.'
                summary = 'Remapper recovery should prioritize restoring desktop control and rollback clarity before feature debugging.'
                cautions = ['A bad remapper config can shadow the whole desktop, so keep the rescue chord or stop path visible in the shipped docs.', 'App-specific layers may still drift across compositor families even when the remapper daemon itself looks healthy.']
                commands = _merge_unique(['sudo keyd reload', 'sudo journalctl -eu keyd', f'vhk gen-route-selection-pack {project_root_q} --quiet'], base_commands)[:10]
            else:
                recovery_lane_id = 'desktop-config-recovery'; recovery_lane_title = 'Desktop config recovery lane'; recovery_posture = 'reload-and-smoke'
                failure_boundary = 'WM/compositor binding config and session reload semantics'
                first_response = 'Regenerate the native trigger config, reload the compositor/WM binding layer, and smoke-test one launcher fallback immediately.'
                rollback_surface = 'Remove the generated binding config and use launcher entrypoints while compositor-native bindings are repaired.'
                reentry_check = 'Reload the desktop binding layer, confirm one exported trigger, and refresh route-selection docs.'
                summary = 'When remapper-shaped shipping actually rides native bindings, recovery is a config reload plus smoke-test loop rather than daemon surgery.'
                cautions = ['Reload semantics vary by compositor, so keep a launcher fallback available during recovery.']
                commands = _merge_unique([f'vhk gen-trigger-pack {project_root_q} --quiet', f'vhk gen-route-selection-pack {project_root_q} --quiet'], base_commands)[:10]
        elif surface_id == 'helper-route-dossier':
            if primary_route_kind == 'portal_session':
                recovery_lane_id = 'portal-session-recovery'; recovery_lane_title = 'Portal session recovery lane'; recovery_posture = 'session-recreate'
                failure_boundary = 'Portal session, consent state, backend routing, and compositor activation'
                first_response = 'Recreate the portal session, rebind shortcuts/devices, and confirm the desktop/backend still exposes the same portal path before retrying automation.'
                rollback_surface = 'Disable the helper-boundary surface and fall back to launcher/text/manual lanes until consent and backend routing are proven again.'
                reentry_check = 'Refresh doctor/host-contract/capability-audit packs and verify the portal session can activate on the target desktop.'
                summary = 'Portal helper recovery is a session recreate/rebind loop, not a generic restart story.'
                cautions = ['Portal sessions can exist yet remain inactive until the compositor decides to activate them.', 'Consent state, backend routing, and helper transport can drift independently.']
                commands = _merge_unique([f'vhk doctor --json', f'vhk gen-host-contract-pack {project_root_q} --quiet', f'vhk gen-capability-audit-pack {project_root_q} --quiet'], base_commands)[:10]
            else:
                recovery_lane_id = 'helper-daemon-recovery'; recovery_lane_title = 'Helper daemon recovery lane'; recovery_posture = 'daemon-reset'
                failure_boundary = 'Helper daemon, socket/device readiness, and uinput permissions'
                first_response = 'Check daemon/socket truth, restart the helper daemon, and rerun one minimal helper smoke test before trusting repeated playback again.'
                rollback_surface = 'Disable the helper-backed surface and fall back to launcher/text/native-trigger lanes while daemon or permission drift is repaired.'
                reentry_check = 'Refresh doctor/readiness/capability-audit artifacts and verify the helper lane is ready, not merely installed.'
                summary = 'Helper-backed recovery should reset daemon/socket truth first instead of assuming PATH proves the route is healthy.'
                cautions = ['Installed helper binaries and ready helper lanes are different truths.', 'Wayland helper viability still varies by compositor, permissions, and daemon lifecycle.']
                commands = _merge_unique([f'vhk doctor --json', f'vhk gen-readiness-pack {project_root_q} --quiet', f'vhk gen-capability-audit-pack {project_root_q} --quiet'], base_commands)[:10]
        elif surface_id == 'watcher-service-export':
            recovery_lane_id = 'watcher-service-recovery'; recovery_lane_title = 'Watcher service recovery lane'; recovery_posture = 'service-restart'
            failure_boundary = 'Watcher user service, bus/file/window event stream, and backlog/overflow handling'
            first_response = 'Inspect user-service logs, restart the watcher plane, and confirm one representative event still reaches the intended macro path.'
            rollback_surface = 'Disable the watcher service artifacts and fall back to launcher/manual entrypoints until the event stream is trustworthy again.'
            reentry_check = 'Verify the watcher service is active, trigger a known event, and refresh host-dossier/rehearsal artifacts.'
            summary = 'Watcher-heavy surfaces should recover like service planes with explicit restart, event-flow, and rollback checks.'
            cautions = ['Socket activation can hide dormant failures until the first event lands, so recovery needs a real event-path smoke test.', 'Overflow or coalescing mistakes are easy to miss if recovery only checks service state and not delivered events.']
            commands = _merge_unique([f'vhk gen-service-compose-pack {project_root_q} --quiet', f'vhk gen-host-dossier-pack {project_root_q} --quiet', f'vhk gen-host-rehearsal-pack {project_root_q} --quiet'], base_commands)[:10]
        elif surface_id == 'launcher-surface-export':
            recovery_lane_id = 'launcher-smoke-recovery'; recovery_lane_title = 'Launcher smoke-test lane'; recovery_posture = 'manual-smoke'
            failure_boundary = 'Desktop entry visibility, palette indexing, and entrypoint argv correctness'
            first_response = 'Regenerate the launcher artifacts, refresh desktop metadata, and launch the entrypoint once before debugging macro internals.'
            rollback_surface = 'Remove the broken launcher entries and rely on direct `vhk run` or known-good CLI wrappers until discovery is fixed.'
            reentry_check = 'Confirm the launcher is visible, launch it once, and rerun `vhk validate` for the underlying project.'
            summary = 'Launcher recovery is mostly regenerate-plus-smoke-test work; it proves wake-up and discoverability, not deep runtime health.'
            cautions = ['A healthy launcher can still wake a broken downstream macro lane, so keep runtime checks separate from launcher repair.']
            commands = _merge_unique([f'vhk gen-desktop-entry {project_root_q}', f'vhk validate {project_root_q} --json'], base_commands)[:10]
        else:
            commands = _merge_unique([f'vhk plan-project {project_root_q} --json', f'vhk gen-promotion-pack {project_root_q} --quiet'], base_commands)[:10]

        evidence = _merge_unique(base_evidence, [f'backend={backend or "unknown"}', f'primary_input_lane={primary_lane_id or "none"}', f'primary_activation_route={primary_route_id or "none"}', f'primary_activation_kind={primary_route_kind or "none"}', f'primary_control_lane={primary_control_lane_id or "none"}'])[:8]
        rows.append({'export_surface_id': surface_id, 'title': _surface_title(surface_id), 'recovery_posture': recovery_posture, 'primary_recovery_lane_id': recovery_lane_id, 'primary_recovery_lane_title': recovery_lane_title, 'primary_input_lane_id': primary_lane_id, 'primary_activation_route_id': primary_route_id, 'primary_activation_kind': primary_route_kind, 'primary_control_lane_id': primary_control_lane_id, 'failure_boundary': failure_boundary, 'first_response': first_response, 'rollback_surface': rollback_surface, 'reentry_check': reentry_check, 'host_requirement_ids': base_requirements, 'commands': commands, 'cautions': cautions, 'evidence': evidence, 'summary': summary})

    posture_rank = {'rollback-first': 0, 'session-recreate': 1, 'daemon-reset': 2, 'service-restart': 3, 'reload-and-smoke': 4, 'manual-smoke': 5, 'review-led': 6}
    rows.sort(key=lambda item: (posture_rank.get(str(item.get('recovery_posture') or 'review-led'), 9), str(item.get('title') or '')))
    return rows


def _promotion_verification_plan(
    *,
    project,
    export_promotion_plan: list[dict[str, Any]],
    promotion_input_lane_plan: list[dict[str, Any]] | None = None,
    promotion_activation_route_plan: list[dict[str, Any]] | None = None,
    promotion_operator_control_plan: list[dict[str, Any]] | None = None,
    promotion_recovery_plan: list[dict[str, Any]] | None = None,
    verification_gates: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Map promotion surfaces to the smoke/proof loops that verify them on Linux.

    Capability verification already exists, but promoted surfaces still need an explicit
    proof loop that says what an operator should observe before treating that surface as
    shipped. This keeps surface-level proof distinct from startup, recovery, and day-2
    control ownership.
    """

    backend = str(getattr(getattr(project, 'settings', None), 'desktop_backend', None) or '').strip().lower()
    project_root_q = shlex.quote(str(Path(getattr(project, 'root_dir', '.') or '.')))
    input_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_input_lane_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    activation_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_activation_route_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    control_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_operator_control_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    recovery_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_recovery_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    gate_rows = {str(item.get('capability') or ''): dict(item) for item in list(verification_gates or []) if isinstance(item, Mapping) and str(item.get('capability') or '').strip()}

    def _surface_title(surface_id: str) -> str:
        titles = {
            'text-package-export': 'Text surface verification lane',
            'remapper-export': 'Remapper verification lane',
            'helper-route-dossier': 'Helper-route verification lane',
            'watcher-service-export': 'Watcher verification lane',
            'launcher-surface-export': 'Launcher verification lane',
        }
        return titles.get(surface_id, surface_id)

    def _merge_unique(*groups: Iterable[str]) -> list[str]:
        out: list[str] = []
        for group in groups:
            for value in group:
                value = str(value).strip()
                if value and value not in out:
                    out.append(value)
        return out

    def _wanted_gate_ids(surface_id: str) -> list[str]:
        if surface_id == 'text-package-export':
            return ['text_injection', 'global_hotkeys']
        if surface_id == 'remapper-export':
            return ['input_capture', 'global_hotkeys', 'pointer_injection']
        if surface_id == 'helper-route-dossier':
            return ['pointer_injection', 'screen_capture', 'input_capture', 'global_hotkeys']
        if surface_id == 'watcher-service-export':
            return ['window_introspection', 'global_hotkeys']
        if surface_id == 'launcher-surface-export':
            return ['global_hotkeys', 'text_injection']
        return []

    rows: list[dict[str, Any]] = []
    for item in export_promotion_plan:
        surface_id = str(item.get('export_surface_id') or '').strip()
        if not surface_id:
            continue
        input_row = input_rows.get(surface_id, {})
        activation_row = activation_rows.get(surface_id, {})
        control_row = control_rows.get(surface_id, {})
        recovery_row = recovery_rows.get(surface_id, {})
        primary_input_lane_id = str(input_row.get('primary_input_lane_id') or '').strip()
        primary_activation_route_id = str(activation_row.get('primary_activation_route_id') or '').strip()
        primary_activation_kind = str(activation_row.get('primary_activation_kind') or '').strip()
        primary_control_lane_id = str(control_row.get('primary_control_lane_id') or '').strip()
        primary_recovery_lane_id = str(recovery_row.get('primary_recovery_lane_id') or '').strip()
        host_requirement_ids = _merge_unique(
            list(input_row.get('host_requirement_ids') or []),
            list(activation_row.get('host_requirement_ids') or []),
            list(control_row.get('host_requirement_ids') or []),
            list(recovery_row.get('host_requirement_ids') or []),
        )
        gate_ids = [gate_id for gate_id in _wanted_gate_ids(surface_id) if gate_id in gate_rows]
        gate_items = [dict(gate_rows[gate_id]) for gate_id in gate_ids]
        gate_titles = [str(g.get('title') or g.get('capability') or '').strip() for g in gate_items if str(g.get('title') or g.get('capability') or '').strip()]
        gate_checks = _merge_unique(*(list(g.get('acceptance_checks') or []) for g in gate_items))[:6]
        gate_commands = _merge_unique(*(list(g.get('commands') or []) for g in gate_items))
        gate_evidence = _merge_unique(*(list(g.get('evidence') or []) for g in gate_items))[:6]
        base_commands = _merge_unique(list(item.get('commands') or []), list(input_row.get('commands') or []), list(activation_row.get('commands') or []), list(control_row.get('commands') or []), list(recovery_row.get('commands') or []), gate_commands)
        base_evidence = _merge_unique(list(item.get('evidence') or []), list(input_row.get('evidence') or []), list(activation_row.get('evidence') or []), list(control_row.get('evidence') or []), list(recovery_row.get('evidence') or []), gate_evidence)

        posture = 'review-proof'
        verification_lane_id = ''
        verification_lane_title = ''
        smoke_loop = 'Regenerate planner-backed artifacts, run the verification pack, and capture one representative operator-visible success signal before treating the surface as shipped.'
        live_probe = 'Run `vhk gen-verification-pack` and collect one surface-specific proof from the target desktop.'
        acceptance_boundary = 'Shipping proof should show both route readiness and one surface-specific success signal, not just artifact generation.'
        proof_surfaces: list[str] = []
        summary = 'Keep verification tied to the shipped surface, not only to underlying capability gates.'
        cautions: list[str] = []

        if surface_id == 'text-package-export':
            posture = 'service-smoke'
            verification_lane_id = 'text-surface-verification'
            verification_lane_title = 'Text surface verification lane'
            smoke_loop = 'Confirm the text service is running, list or execute a representative match, and verify the live config/runtime paths match the shipped package before treating snippets as ready.'
            live_probe = 'Check `espanso status`, inspect the active config/runtime paths, and run one representative `espanso match` flow or equivalent text smoke on the target desktop.'
            acceptance_boundary = 'Proof should show both daemon health and one real text expansion path, not only generated package files.'
            proof_surfaces = ['espanso status', 'espanso match list/exec', 'espanso path config/runtime']
            summary = 'Text-package promotion should prove that the shipped text lane is alive, using service status plus one representative expansion smoke.'
            cautions = ['A valid exported package is not the same thing as a running text surface.', 'Hotstring-like UX can drift if the wrong config/runtime directory is active.']
            base_commands = _merge_unique([
                'espanso status',
                'espanso path config',
                'espanso path runtime',
                'espanso match list',
                f'vhk gen-espanso {project_root_q} --package-dir ./build/espanso_package',
                f'vhk gen-verification-pack {project_root_q} --quiet',
            ], base_commands)
        elif surface_id == 'remapper-export':
            posture = 'input-event-smoke'
            verification_lane_id = 'remapper-verification'
            verification_lane_title = 'Remapper verification lane'
            smoke_loop = 'Reload the remapper config, observe one representative key path, and inspect service logs before treating low-latency key ownership as shipped.'
            live_probe = 'Run a remapper reload plus one monitor/log loop (`keyd monitor` or equivalent) and verify that a representative mapping emits the intended output.'
            acceptance_boundary = 'Proof should include one live input-event observation and one service/log check, not only generated remapper config files.'
            proof_surfaces = ['keyd monitor', 'keyd reload', 'journalctl -eu keyd']
            summary = 'Remapper promotion should prove one real input-event path, because low-latency key ownership lives closer to evdev/uinput than the runner.'
            cautions = ['A bad remapper config can degrade the whole session, so verification should stay reversible.', 'App-specific remaps may need compositor or device-specific proof, not only generic reload success.']
            base_commands = _merge_unique([
                f'vhk gen-keyd-config {project_root_q} --out ./build/vhk.keyd.conf',
                'sudo keyd reload',
                'sudo keyd monitor',
                'sudo journalctl -eu keyd -n 50 --no-pager',
                f'vhk gen-verification-pack {project_root_q} --quiet',
            ], base_commands)
        elif surface_id == 'helper-route-dossier':
            if primary_activation_kind == 'portal_session' or primary_input_lane_id == 'portal-permissioned-input':
                posture = 'portal-proof'
                verification_lane_id = 'portal-session-verification'
                verification_lane_title = 'Portal session verification lane'
                smoke_loop = 'Refresh doctor/capability-audit output, recreate the portal/session path if needed, and capture one activated session/proof signal before trusting the helper route.'
                live_probe = 'Verify the relevant portal session can be created and that the compositor exposes the expected activated/deactivated or enabled/active behavior for the target path.'
                acceptance_boundary = 'Proof should show portal/session truth on the target desktop, not just that helper docs were generated.'
                proof_surfaces = ['vhk doctor --json', 'VHK_CAPABILITY_AUDIT.md', 'portal session signals']
                summary = 'Portal-backed helper promotion should prove target-desktop session behavior, not only planner intent.'
                cautions = ['Portal sessions can be created yet remain inactive until the compositor decides to activate them.', 'Enabled and active are distinct states for InputCapture-style flows.']
                base_commands = _merge_unique([
                    'vhk doctor --json',
                    f'vhk gen-capability-audit-pack {project_root_q} --quiet',
                    f'vhk gen-verification-pack {project_root_q} --quiet',
                ], base_commands)
            else:
                posture = 'daemon-proof'
                verification_lane_id = 'helper-daemon-verification'
                verification_lane_title = 'Helper daemon verification lane'
                smoke_loop = 'Refresh doctor/readiness output, verify helper daemon or socket readiness, and run one minimal helper smoke before treating repeated playback as proven.'
                live_probe = 'Check daemon/socket truth and verify one helper-backed input path on the target desktop before claiming the helper route is usable.'
                acceptance_boundary = 'Proof should show readiness of the helper lane itself, not merely that the helper binary is installed.'
                proof_surfaces = ['vhk doctor --json', 'VHK_READINESS_REPORT.md', 'minimal helper smoke']
                summary = 'Helper-backed promotion should verify daemon/socket truth first, because PATH presence is not enough proof for repeated playback lanes.'
                cautions = ['Installed helpers and ready helper lanes are different truths.', 'Wayland helper viability still depends on compositor, permissions, and daemon lifecycle.']
                base_commands = _merge_unique([
                    'vhk doctor --json',
                    f'vhk gen-readiness-pack {project_root_q} --quiet',
                    f'vhk gen-capability-audit-pack {project_root_q} --quiet',
                    f'vhk gen-verification-pack {project_root_q} --quiet',
                ], base_commands)
        elif surface_id == 'watcher-service-export':
            posture = 'event-flow-smoke'
            verification_lane_id = 'watcher-service-verification'
            verification_lane_title = 'Watcher service verification lane'
            smoke_loop = 'Confirm the watcher service is active, tail the relevant user-service logs, and trigger one representative event that reaches the intended macro path.'
            live_probe = 'Use a journal/status loop plus one known event to prove that the event plane is alive, not just the service unit.'
            acceptance_boundary = 'Proof should show one delivered event, because service status alone can miss idle or coalescing failures.'
            proof_surfaces = ['systemctl --user status', 'journalctl --user', 'representative event trigger']
            summary = 'Watcher/service promotion should prove event delivery, not only service liveness.'
            cautions = ['Socket activation can hide dormant failures until the first event lands.', 'Overflow or coalescing bugs may only show up under a real delivered-event smoke test.']
            base_commands = _merge_unique([
                'systemctl --user status vhk-busd.service || true',
                'journalctl --user -u vhk-busd.service -n 50 --no-pager || true',
                f'vhk gen-host-rehearsal-pack {project_root_q} --quiet',
                f'vhk gen-verification-pack {project_root_q} --quiet',
            ], base_commands)
        elif surface_id == 'launcher-surface-export':
            posture = 'launch-smoke'
            verification_lane_id = 'launcher-entry-verification'
            verification_lane_title = 'Launcher entry verification lane'
            smoke_loop = 'Regenerate the launcher artifacts, confirm the desktop entry is visible to the target shell/menu, and launch it once before treating the surface as shipped.'
            live_probe = 'Verify the desktop entry exists in the expected location and can wake the intended downstream macro path once.'
            acceptance_boundary = 'Proof should include one visible launch path, not only a generated desktop file.'
            proof_surfaces = ['desktop entry visibility', 'one launch smoke', 'validate output']
            summary = 'Launcher promotion should prove discoverability and one real wake-up path before it is treated as release-ready.'
            cautions = ['A visible launcher can still wake a broken downstream route, so launch proof and runtime proof should stay separate.']
            base_commands = _merge_unique([
                f'vhk gen-desktop-entry {project_root_q}',
                f'vhk validate {project_root_q} --json',
                f'vhk gen-verification-pack {project_root_q} --quiet',
            ], base_commands)

        evidence = _merge_unique(base_evidence, [f'backend={backend or "unknown"}', f'primary_input_lane={primary_input_lane_id or "none"}', f'primary_activation_route={primary_activation_route_id or "none"}', f'primary_control_lane={primary_control_lane_id or "none"}', f'primary_recovery_lane={primary_recovery_lane_id or "none"}', *(f'verification_gate={gate_id}' for gate_id in gate_ids)])[:10]
        rows.append({
            'export_surface_id': surface_id,
            'title': _surface_title(surface_id),
            'verification_posture': posture,
            'primary_verification_lane_id': verification_lane_id,
            'primary_verification_lane_title': verification_lane_title,
            'primary_input_lane_id': primary_input_lane_id or None,
            'primary_activation_route_id': primary_activation_route_id or None,
            'primary_control_lane_id': primary_control_lane_id or None,
            'primary_recovery_lane_id': primary_recovery_lane_id or None,
            'verification_gate_ids': gate_ids,
            'verification_gate_titles': gate_titles,
            'smoke_loop': smoke_loop,
            'live_probe': live_probe,
            'acceptance_boundary': acceptance_boundary,
            'proof_surfaces': proof_surfaces,
            'acceptance_checks': gate_checks,
            'host_requirement_ids': host_requirement_ids,
            'commands': base_commands[:10],
            'cautions': cautions,
            'evidence': evidence,
            'summary': summary,
        })

    posture_rank = {'service-smoke': 0, 'input-event-smoke': 1, 'portal-proof': 2, 'daemon-proof': 3, 'event-flow-smoke': 4, 'launch-smoke': 5, 'review-proof': 6}
    rows.sort(key=lambda item: (posture_rank.get(str(item.get('verification_posture') or 'review-proof'), 9), str(item.get('title') or '')))
    return rows


def _promotion_verification_summary(
    *,
    promotion_verification_plan: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = [dict(item) for item in promotion_verification_plan if isinstance(item, Mapping)]
    postures = Counter(str(item.get('verification_posture') or 'review-proof') for item in rows)
    lane_counts = Counter(str(item.get('primary_verification_lane_id') or '') for item in rows if str(item.get('primary_verification_lane_id') or '').strip())
    return {
        'entry_count': len(rows),
        'service_smoke_count': int(postures.get('service-smoke') or 0),
        'input_event_smoke_count': int(postures.get('input-event-smoke') or 0),
        'portal_proof_count': int(postures.get('portal-proof') or 0),
        'daemon_proof_count': int(postures.get('daemon-proof') or 0),
        'event_flow_smoke_count': int(postures.get('event-flow-smoke') or 0),
        'launch_smoke_count': int(postures.get('launch-smoke') or 0),
        'review_proof_count': int(postures.get('review-proof') or 0),
        'primary_verification_lane_counts': dict(lane_counts),
        'ordered_primary_verification_lane_ids': [lane_id for lane_id, _count in sorted(lane_counts.items(), key=lambda pair: (-pair[1], pair[0]))],
    }


def _promotion_performance_plan(
    *,
    project,
    export_promotion_plan: list[dict[str, Any]],
    performance_profile: Mapping[str, Any] | None = None,
    promotion_input_lane_plan: list[dict[str, Any]] | None = None,
    promotion_activation_route_plan: list[dict[str, Any]] | None = None,
    promotion_operator_control_plan: list[dict[str, Any]] | None = None,
    promotion_verification_plan: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Map promoted surfaces to the latency/throughput envelope operators should protect.

    Earlier planner surfaces say which lane ships, starts, controls, recovers, and proves a
    promotion surface. This pass makes the performance envelope explicit so operators can see
    which surfaces win on low-latency edge paths, daemon warm paths, or throughput-oriented
    batching rather than inferring that from helper names.
    """

    backend = str(getattr(getattr(project, 'settings', None), 'desktop_backend', None) or '').strip().lower()
    project_root_q = shlex.quote(str(Path(getattr(project, 'root_dir', '.') or '.')))
    perf = dict(performance_profile or {})
    budget = dict(perf.get('budget') or {})
    hotspot_rows = [dict(item) for item in list(perf.get('hotspots') or []) if isinstance(item, Mapping)]
    hotspot_map = {str(item.get('id') or ''): dict(item) for item in hotspot_rows if str(item.get('id') or '').strip()}
    input_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_input_lane_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    activation_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_activation_route_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    control_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_operator_control_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    verification_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_verification_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}

    def _surface_title(surface_id: str) -> str:
        titles = {
            'text-package-export': 'Text surface performance envelope',
            'remapper-export': 'Remapper performance envelope',
            'helper-route-dossier': 'Helper-route performance envelope',
            'watcher-service-export': 'Watcher performance envelope',
            'launcher-surface-export': 'Launcher performance envelope',
        }
        return titles.get(surface_id, surface_id)

    def _merge_unique(*groups: Iterable[str]) -> list[str]:
        out: list[str] = []
        for group in groups:
            for value in group:
                value = str(value).strip()
                if value and value not in out:
                    out.append(value)
        return out

    def _surface_hotspot_ids(surface_id: str) -> list[str]:
        ordered: list[str] = []
        wanted: dict[str, list[str]] = {
            'text-package-export': ['typed-text-throughput', 'direct-hotkey-heavy-macros', 'fixed-delay-budget'],
            'remapper-export': ['direct-hotkey-heavy-macros', 'fixed-delay-budget'],
            'helper-route-dossier': ['unscoped-live-capture', 'aggressive-polling', 'ocr-pressure', 'polling-dominant'],
            'watcher-service-export': ['aggressive-polling', 'polling-dominant', 'fixed-delay-budget'],
            'launcher-surface-export': ['fixed-delay-budget', 'direct-hotkey-heavy-macros'],
        }
        for hotspot_id in wanted.get(surface_id, []):
            if hotspot_id in hotspot_map and hotspot_id not in ordered:
                ordered.append(hotspot_id)
        return ordered

    rows: list[dict[str, Any]] = []
    for item in export_promotion_plan:
        surface_id = str(item.get('export_surface_id') or '').strip()
        if not surface_id:
            continue
        input_row = input_rows.get(surface_id, {})
        activation_row = activation_rows.get(surface_id, {})
        control_row = control_rows.get(surface_id, {})
        verification_row = verification_rows.get(surface_id, {})
        primary_input_lane_id = str(input_row.get('primary_input_lane_id') or '').strip()
        primary_activation_route_id = str(activation_row.get('primary_activation_route_id') or '').strip()
        primary_control_lane_id = str(control_row.get('primary_control_lane_id') or '').strip()
        primary_verification_lane_id = str(verification_row.get('primary_verification_lane_id') or '').strip()
        host_requirement_ids = _merge_unique(
            list(input_row.get('host_requirement_ids') or []),
            list(activation_row.get('host_requirement_ids') or []),
            list(control_row.get('host_requirement_ids') or []),
            list(verification_row.get('host_requirement_ids') or []),
        )
        hotspot_ids = _surface_hotspot_ids(surface_id)
        hotspot_titles = [str((hotspot_map.get(hotspot_id) or {}).get('title') or hotspot_id) for hotspot_id in hotspot_ids]
        hotspot_actions = _merge_unique(*(list((hotspot_map.get(hotspot_id) or {}).get('actions') or []) for hotspot_id in hotspot_ids))[:6]
        hotspot_evidence = _merge_unique(*(list((hotspot_map.get(hotspot_id) or {}).get('macros') or []) for hotspot_id in hotspot_ids))[:6]
        base_commands = _merge_unique(list(item.get('commands') or []), list(input_row.get('commands') or []), list(activation_row.get('commands') or []), list(control_row.get('commands') or []), list(verification_row.get('commands') or []))
        base_evidence = _merge_unique(list(item.get('evidence') or []), list(input_row.get('evidence') or []), list(activation_row.get('evidence') or []), list(control_row.get('evidence') or []), list(verification_row.get('evidence') or []), hotspot_evidence)

        posture = 'review-measured'
        performance_lane_id = ''
        performance_lane_title = ''
        latency_class = 'mixed project envelope'
        hot_path = 'Keep the shipped surface close to its owning Linux-native lane and measure with one representative operator-visible loop.'
        batching_strategy = 'Prefer whichever shipped lane amortizes setup cost without hiding state changes.'
        throughput_boundary = 'Treat generated artifacts as necessary but insufficient; performance proof should include a representative live path.'
        acceptance_signals: list[str] = []
        summary = "Make the shipped surface's hot path explicit so latency and throughput decisions stay reviewable."
        cautions: list[str] = []

        if surface_id == 'text-package-export':
            posture = 'throughput-first'
            performance_lane_id = 'clipboard-text-throughput'
            performance_lane_title = 'Clipboard/text throughput lane'
            latency_class = 'always-on text expansion'
            long_literal_chars = int(budget.get('long_literal_type_chars') or 0)
            hot_path = 'Keep phrase expansion and literal text bursts inside the text/package lane so repeated entry amortizes daemon warm-up and avoids per-character replay.'
            batching_strategy = 'Favor match/package expansion and clipboard-friendly text bursts; keep interpolation-heavy or timing-sensitive fields explicit.'
            throughput_boundary = f'Large literal text bodies ({long_literal_chars} long-literal chars observed) should not silently fall back to heavyweight per-character replay when a package/clipboard lane exists.'
            acceptance_signals = ['espanso match resolves once', 'service status is healthy', 'active config/runtime paths match shipped package']
            summary = 'Text-package promotion should own throughput. The Linux-native win is a warm text service or package lane, not replaying every snippet through the runner.'
            cautions = ['Clipboard-friendly text and interpolation-heavy typed text are different performance shapes.', 'The wrong active config/runtime path can erase the expected throughput win even when package files were generated correctly.']
            base_commands = _merge_unique([
                'espanso status',
                'espanso match list',
                'vhk optimize . --promote-paste-text --dry-run || true',
                f'vhk gen-espanso {project_root_q} --package-dir ./build/espanso_package',
                f'vhk plan-project {project_root_q} --json',
            ], base_commands)
        elif surface_id == 'remapper-export':
            posture = 'low-latency-edge'
            performance_lane_id = 'sub-ms-remap-edge'
            performance_lane_title = 'Low-latency remap edge lane'
            latency_class = 'sub-gesture dispatch at the edge'
            hot_path = 'Keep hotkey ownership in the remapper/input tier so wake-up stays near evdev/uinput rather than pulling the full runner into every keystroke.'
            batching_strategy = 'Keep the edge path thin: remap, layer, or launch at the remapper boundary; hand off richer workflows after the key event is already decided.'
            throughput_boundary = 'Do not route capture-heavy or long-wait orchestration directly onto the low-latency remap path when a lighter launch/bus handoff exists.'
            acceptance_signals = ['reload is fast', 'one representative mapping emits on monitor', 'service logs stay clean after reload']
            summary = 'Remapper promotion should protect the low-latency edge path. The point is not just that remaps exist, but that key ownership stays closer to kernel/compositor primitives than the Python runner.'
            cautions = ['A remapper can feel fast while still waking a slow downstream workflow.', 'App-specific maps may need device/compositor-specific measurement rather than one global timing claim.']
            base_commands = _merge_unique([
                f'vhk gen-keyd-config {project_root_q} --out ./build/vhk.keyd.conf',
                'sudo keyd reload',
                'sudo keyd monitor',
                'sudo journalctl -eu keyd -n 50 --no-pager',
                f'vhk plan-project {project_root_q} --json',
            ], base_commands)
        elif surface_id == 'helper-route-dossier':
            if primary_input_lane_id == 'portal-permissioned-input' or str(activation_row.get('primary_activation_kind') or '').strip() == 'portal_session':
                posture = 'consent-bound-async'
                performance_lane_id = 'portal-session-envelope'
                performance_lane_title = 'Portal/session performance lane'
                latency_class = 'session-gated burst path'
                hot_path = 'Measure the helper route as a consent/session path where enable/activate boundaries dominate first-use latency more than raw helper execution.'
                batching_strategy = 'Amortize session setup where possible, but keep performance claims honest about activation being compositor-controlled.'
                throughput_boundary = 'Portal-backed input is not a universal low-latency path; activation and consent state can dominate the first useful event.'
                acceptance_signals = ['session enable/activate flow succeeds', 'one representative helper action completes after consent', 'zone/session truth matches audit output']
                summary = 'Portal-backed helper promotion should be measured as an asynchronous, consent-bound envelope rather than a raw helper binary speed claim.'
                cautions = ['Enabled and active are distinct states for InputCapture-style flows.', 'Portal sessions can be reusable, but first activation cost is not equivalent to warm daemon cost.']
                base_commands = _merge_unique([
                    'vhk doctor --json',
                    f'vhk gen-capability-audit-pack {project_root_q} --quiet',
                    f'vhk gen-verification-pack {project_root_q} --quiet',
                ], base_commands)
            else:
                posture = 'warm-daemon'
                performance_lane_id = 'daemon-amortized-helper'
                performance_lane_title = 'Daemon-amortized helper lane'
                latency_class = 'interactive burst workload'
                hot_path = 'Keep repeated pointer/text injection on a warm daemon-backed helper lane so virtual-device setup is amortized instead of paid on every action.'
                batching_strategy = 'Prefer daemon/client or persistent helper lifecycles for repeated playback; use one-shot helpers for fallback or sparse actions.'
                throughput_boundary = 'Helper PATH presence does not prove a warm path. The performance claim only holds when the daemon/socket/device is already ready.'
                acceptance_signals = ['daemon/socket is ready', 'one repeated playback action completes without cold-start setup', 'doctor/readiness surfaces agree on the helper lane']
                summary = 'Helper-backed promotion should explicitly protect warm-path wins: repeated playback only gets faster when daemon/device setup stops being part of every action.'
                cautions = ['A cold helper lane can erase the benefit of an otherwise strong uinput path.', 'Wayland helper throughput still depends on compositor policy and permissions.']
                base_commands = _merge_unique([
                    'vhk doctor --json',
                    f'vhk gen-readiness-pack {project_root_q} --quiet',
                    f'vhk gen-capability-audit-pack {project_root_q} --quiet',
                    f'vhk plan-project {project_root_q} --json',
                ], base_commands)
        elif surface_id == 'watcher-service-export':
            posture = 'event-pipeline'
            performance_lane_id = 'resident-event-pipeline'
            performance_lane_title = 'Resident event pipeline lane'
            latency_class = 'background service plane'
            hot_path = 'Keep the watcher surface resident so wake-up cost is paid once and live events flow through the bus/service path rather than repeated process startups.'
            batching_strategy = 'Prefer event-driven delivery and coalescing over fast polling when the desktop can provide a stable event plane.'
            throughput_boundary = 'A running service is not enough; the event pipeline must still deliver one representative event without falling back to heavy polling.'
            acceptance_signals = ['user service stays healthy', 'journal shows one delivered event', 'event-driven path wins over poll-heavy fallback']
            summary = 'Watcher promotion should protect the event pipeline. The performance win is resident event delivery, not just service liveness.'
            cautions = ['Poll-heavy watcher loops can consume the performance budget even when the service looks healthy.', 'Overflow/coalescing mistakes usually surface only under a real event stream.']
            base_commands = _merge_unique([
                'systemctl --user status vhk-busd.service || true',
                'journalctl --user -u vhk-busd.service -n 50 --no-pager || true',
                f'vhk gen-host-rehearsal-pack {project_root_q} --quiet',
                f'vhk plan-project {project_root_q} --json',
            ], base_commands)
        elif surface_id == 'launcher-surface-export':
            posture = 'launch-to-dispatch'
            performance_lane_id = 'launcher-wake-path'
            performance_lane_title = 'Launcher wake-path lane'
            latency_class = 'explicit wake-up path'
            hot_path = 'Optimize the path from launcher visibility to one downstream macro wake-up, keeping launcher startup thin while heavier logic stays behind the invoked route.'
            batching_strategy = 'Keep desktop-entry startup minimal and hand off richer work to the already-owned runtime/service lane after the first wake-up.'
            throughput_boundary = 'Discoverability is useful, but the launcher path should not silently become the only hot path for workflows that need a resident or low-latency owner.'
            acceptance_signals = ['desktop entry is visible', 'one launch wakes the intended route', 'downstream validation still passes']
            summary = 'Launcher promotion should be measured as wake-up latency plus discoverability, not as a substitute for resident or low-latency lanes.'
            cautions = ['A pretty launcher can hide a slow or cold downstream path.', 'Launch-path measurement should stay distinct from the runtime lane that owns repeated use.']
            base_commands = _merge_unique([
                f'vhk gen-desktop-entry {project_root_q}',
                f'vhk validate {project_root_q} --json',
                f'vhk plan-project {project_root_q} --json',
            ], base_commands)

        evidence = _merge_unique(base_evidence, [
            f'backend={backend or "unknown"}',
            f'primary_input_lane={primary_input_lane_id or "none"}',
            f'primary_activation_route={primary_activation_route_id or "none"}',
            f'primary_control_lane={primary_control_lane_id or "none"}',
            f'primary_verification_lane={primary_verification_lane_id or "none"}',
            *(f'performance_hotspot={hotspot_id}' for hotspot_id in hotspot_ids),
        ])[:10]
        rows.append({
            'export_surface_id': surface_id,
            'title': _surface_title(surface_id),
            'performance_posture': posture,
            'primary_performance_lane_id': performance_lane_id,
            'primary_performance_lane_title': performance_lane_title,
            'primary_input_lane_id': primary_input_lane_id or None,
            'primary_activation_route_id': primary_activation_route_id or None,
            'primary_control_lane_id': primary_control_lane_id or None,
            'primary_verification_lane_id': primary_verification_lane_id or None,
            'latency_class': latency_class,
            'hot_path': hot_path,
            'batching_strategy': batching_strategy,
            'throughput_boundary': throughput_boundary,
            'acceptance_signals': acceptance_signals,
            'performance_hotspot_ids': hotspot_ids,
            'performance_hotspot_titles': hotspot_titles,
            'recommended_actions': hotspot_actions,
            'host_requirement_ids': host_requirement_ids,
            'commands': base_commands[:10],
            'cautions': cautions,
            'evidence': evidence,
            'summary': summary,
        })

    posture_rank = {
        'low-latency-edge': 0,
        'throughput-first': 1,
        'warm-daemon': 2,
        'event-pipeline': 3,
        'consent-bound-async': 4,
        'launch-to-dispatch': 5,
        'review-measured': 6,
    }
    rows.sort(key=lambda item: (posture_rank.get(str(item.get('performance_posture') or 'review-measured'), 9), str(item.get('title') or '')))
    return rows


def _promotion_performance_summary(
    *,
    promotion_performance_plan: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = [dict(item) for item in promotion_performance_plan if isinstance(item, Mapping)]
    postures = Counter(str(item.get('performance_posture') or 'review-measured') for item in rows)
    lane_counts = Counter(str(item.get('primary_performance_lane_id') or '') for item in rows if str(item.get('primary_performance_lane_id') or '').strip())
    hotspot_counts = Counter(
        hotspot_id
        for item in rows
        for hotspot_id in [str(x) for x in list(item.get('performance_hotspot_ids') or []) if str(x)]
    )
    return {
        'entry_count': len(rows),
        'low_latency_edge_count': int(postures.get('low-latency-edge') or 0),
        'throughput_first_count': int(postures.get('throughput-first') or 0),
        'warm_daemon_count': int(postures.get('warm-daemon') or 0),
        'event_pipeline_count': int(postures.get('event-pipeline') or 0),
        'consent_bound_async_count': int(postures.get('consent-bound-async') or 0),
        'launch_to_dispatch_count': int(postures.get('launch-to-dispatch') or 0),
        'review_measured_count': int(postures.get('review-measured') or 0),
        'primary_performance_lane_counts': dict(lane_counts),
        'ordered_primary_performance_lane_ids': [lane_id for lane_id, _count in sorted(lane_counts.items(), key=lambda pair: (-pair[1], pair[0]))],
        'ordered_hotspot_ids': [hotspot_id for hotspot_id, _count in sorted(hotspot_counts.items(), key=lambda pair: (-pair[1], pair[0]))],
    }


def _promotion_dispatch_budget_plan(
    *,
    project,
    export_promotion_plan: list[dict[str, Any]],
    performance_profile: Mapping[str, Any] | None = None,
    promotion_input_lane_plan: list[dict[str, Any]] | None = None,
    promotion_activation_route_plan: list[dict[str, Any]] | None = None,
    promotion_operator_control_plan: list[dict[str, Any]] | None = None,
    promotion_verification_plan: list[dict[str, Any]] | None = None,
    promotion_performance_plan: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Describe the steady-state dispatch budget each promoted surface should defend.

    Promotion surfaces already name who ships, starts, controls, recovers, proves, and
    performs. This pass bridges startup and hot-path review by making the perceived dispatch
    budget explicit: which surfaces should stay resident at the edge, which can rely on warm
    services or daemons, and which inherently pay launch/session wake costs.
    """

    backend = str(getattr(getattr(project, 'settings', None), 'desktop_backend', None) or '').strip().lower()
    project_root_q = shlex.quote(str(Path(getattr(project, 'root_dir', '.') or '.')))
    perf = dict(performance_profile or {})
    hotspot_rows = [dict(item) for item in list(perf.get('hotspots') or []) if isinstance(item, Mapping)]
    hotspot_map = {str(item.get('id') or ''): dict(item) for item in hotspot_rows if str(item.get('id') or '').strip()}
    input_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_input_lane_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    activation_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_activation_route_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    control_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_operator_control_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    verification_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_verification_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    performance_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_performance_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}

    def _surface_title(surface_id: str) -> str:
        titles = {
            'text-package-export': 'Text surface dispatch budget',
            'remapper-export': 'Remapper dispatch budget',
            'helper-route-dossier': 'Helper-route dispatch budget',
            'watcher-service-export': 'Watcher dispatch budget',
            'launcher-surface-export': 'Launcher dispatch budget',
        }
        return titles.get(surface_id, surface_id)

    def _merge_unique(*groups: Iterable[str]) -> list[str]:
        out: list[str] = []
        for group in groups:
            for value in group:
                value = str(value).strip()
                if value and value not in out:
                    out.append(value)
        return out

    rows: list[dict[str, Any]] = []
    for item in export_promotion_plan:
        surface_id = str(item.get('export_surface_id') or '').strip()
        if not surface_id:
            continue
        input_row = dict(input_rows.get(surface_id) or {})
        activation_row = dict(activation_rows.get(surface_id) or {})
        control_row = dict(control_rows.get(surface_id) or {})
        verification_row = dict(verification_rows.get(surface_id) or {})
        performance_row = dict(performance_rows.get(surface_id) or {})

        primary_input_lane_id = str(input_row.get('primary_input_lane_id') or '').strip() or None
        primary_activation_route_id = str(activation_row.get('primary_activation_route_id') or '').strip() or None
        primary_control_lane_id = str(control_row.get('primary_control_lane_id') or '').strip() or None
        primary_verification_lane_id = str(verification_row.get('primary_verification_lane_id') or '').strip() or None
        primary_performance_lane_id = str(performance_row.get('primary_performance_lane_id') or '').strip() or None
        hotspot_ids = [str(x) for x in list(performance_row.get('performance_hotspot_ids') or []) if str(x)]
        hotspot_titles = [str(hotspot_map.get(hotspot_id, {}).get('title') or hotspot_id) for hotspot_id in hotspot_ids]
        host_requirement_ids = _merge_unique(
            [str(x) for x in list(input_row.get('host_requirement_ids') or []) if str(x)],
            [str(x) for x in list(activation_row.get('host_requirement_ids') or []) if str(x)],
            [str(x) for x in list(control_row.get('host_requirement_ids') or []) if str(x)],
            [str(x) for x in list(verification_row.get('host_requirement_ids') or []) if str(x)],
            [str(x) for x in list(performance_row.get('host_requirement_ids') or []) if str(x)],
        )[:10]
        base_commands = _merge_unique(
            [str(x) for x in list(input_row.get('commands') or []) if str(x)],
            [str(x) for x in list(activation_row.get('commands') or []) if str(x)],
            [str(x) for x in list(control_row.get('commands') or []) if str(x)],
            [str(x) for x in list(verification_row.get('commands') or []) if str(x)],
            [str(x) for x in list(performance_row.get('commands') or []) if str(x)],
        )
        base_evidence = _merge_unique(
            [str(x) for x in list(item.get('evidence') or []) if str(x)],
            [str(x) for x in list(input_row.get('evidence') or []) if str(x)],
            [str(x) for x in list(activation_row.get('evidence') or []) if str(x)],
            [str(x) for x in list(control_row.get('evidence') or []) if str(x)],
            [str(x) for x in list(verification_row.get('evidence') or []) if str(x)],
            [str(x) for x in list(performance_row.get('evidence') or []) if str(x)],
        )

        posture = 'review-budget'
        dispatch_lane_id = 'reviewed-dispatch-budget'
        dispatch_lane_title = 'Reviewed dispatch budget lane'
        cold_start_path = 'Treat cold-start and repeated dispatch as separate review questions instead of assuming one surface is automatically hot.'
        steady_state_path = 'Keep the steady-state dispatch path explicit and measured on the intended host.'
        first_use_expectation = 'Measure the first useful action on the real host before promising an AHK-class feel.'
        dispatch_guardrails = [
            'Keep startup/launch cost separate from repeated dispatch cost in release claims.',
            'Use report/trace output to confirm that the claimed hot path is actually the one users feel.',
        ]
        summary = 'Dispatch-budget review should say whether this surface is supposed to stay resident, warm, or explicitly cold.'
        cautions = ['A believable Linux-native hot path depends on the owning lane staying explicit.']

        performance_posture = str(performance_row.get('performance_posture') or '').strip()
        activation_posture = str(activation_row.get('startup_posture') or '').strip()

        if surface_id == 'text-package-export':
            posture = 'service-resident'
            dispatch_lane_id = 'resident-text-service'
            dispatch_lane_title = 'Resident text service budget'
            cold_start_path = 'Budget login-time service registration/start and backend attach outside the hot path; treat restarts as maintenance, not per-expansion work.'
            steady_state_path = 'Repeated text dispatch should flow through a resident text/package surface instead of paying runner startup or per-character orchestration on every expansion.'
            first_use_expectation = 'First use after login or after keyboard/backend churn can pay a service wake or restart cost; repeated snippets should stay warm and throughput-oriented.'
            dispatch_guardrails = [
                'Prefer package/clipboard-style text throughput for large bodies rather than per-character replay.',
                'Keep restart/re-register workflows visible when keyboard topology or backend state changes.',
            ]
            summary = 'Text-package promotion should feel warm because a resident text service owns dispatch, while restart/registration work stays outside the hot path.'
            cautions = ['A resident text surface can still regress if large literal text quietly falls back to slower typed-text replay.', 'Backend reattach or restart chores should not be mistaken for ordinary dispatch cost.']
            base_commands = _merge_unique([
                'espanso status || true',
                'espanso restart || true',
                f'vhk gen-espanso {project_root_q}',
            ], base_commands)
        elif surface_id == 'remapper-export':
            posture = 'edge-resident'
            dispatch_lane_id = 'resident-remapper-edge'
            dispatch_lane_title = 'Resident remapper edge budget'
            cold_start_path = 'Reloading or installing the remapper is a maintenance path; the user-visible dispatch budget starts only after the remapper owns the edge.'
            steady_state_path = 'Representative launch chords should stay at the low-latency edge rather than paying Python runner startup before the first meaningful event.'
            first_use_expectation = 'Once the remapper is live, every gesture should behave like an edge-owned shortcut instead of a launched macro process.'
            dispatch_guardrails = [
                'Keep capture-heavy follow-on work off the remapper edge when a lighter handoff lane exists.',
                'Document rescue/panic sequences separately from the steady-state dispatch claim.',
            ]
            summary = 'Remapper promotion should defend the edge-resident path: reload is maintenance, but repeated gestures must stay close to evdev/compositor ownership.'
            cautions = ['A remapper that launches heavy orchestration directly can erase the latency benefit of owning the edge.', 'Rollback and panic paths matter because the same low-latency lane can fail very aggressively.']
            base_commands = _merge_unique([
                'sudo keyd reload || true',
                'sudo journalctl -eu keyd -n 50 || true',
                f'vhk gen-keyd-config {project_root_q}',
            ], base_commands)
        elif surface_id == 'helper-route-dossier':
            if performance_posture == 'consent-bound-async' or activation_posture == 'session-bound':
                posture = 'session-resume'
                dispatch_lane_id = 'session-consent-resume'
                dispatch_lane_title = 'Session/consent resume budget'
                cold_start_path = 'Budget portal session creation, consent, and capability wake-up as explicit first-use work; do not promise edge-like behavior before the session exists.'
                steady_state_path = 'Once the session is alive, keep the interaction framed as a resumed session path rather than a globally resident remapper.'
                first_use_expectation = 'First use can pay session binding/consent overhead; repeated actions should be judged against a warm session, not a cold portal negotiation.'
                dispatch_guardrails = [
                    'Keep portal/session lifetime visible in release language and operator docs.',
                    'Do not compare consent-gated helper routes to always-on remapper lanes without saying which path is being measured.',
                ]
                summary = 'Portal-shaped helper routes should budget around session resume and consent, because first-use latency is often dominated by session lifecycle rather than raw execution time.'
                cautions = ['Session loss can push a once-warm path back onto a cold consent flow.', 'A valid helper route can still feel slow if consent/session wake costs are hidden from the claim.']
            else:
                posture = 'daemon-warm'
                dispatch_lane_id = 'warm-helper-daemon'
                dispatch_lane_title = 'Warm helper daemon budget'
                cold_start_path = 'Treat daemon/socket startup and permission checks as preconditions; the hot path begins only once the helper is warm.'
                steady_state_path = 'Repeated helper-backed actions should amortize daemon startup, device setup, and socket negotiation across many dispatches.'
                first_use_expectation = 'First action after login or daemon restart can cost noticeably more than repeated use; steady-state claims should assume a warm daemon.'
                dispatch_guardrails = [
                    'Prefer long-lived helper daemons over one-shot helper spawn paths for repeated input or capture flows.',
                    'Keep permission/socket health probes close to the helper lane so warm-path claims stay believable.',
                ]
                summary = 'Daemon-backed helper routes should be judged as warm-daemon paths: first-use costs are real, but repeated dispatch should amortize setup work.'
                cautions = ['One-shot helper spawn can erase the benefit of a daemon-backed lane.', 'Permission or socket drift can silently turn a warm path back into a cold troubleshooting path.']
        elif surface_id == 'watcher-service-export':
            posture = 'service-resident'
            dispatch_lane_id = 'resident-event-service'
            dispatch_lane_title = 'Resident event service budget'
            cold_start_path = 'Service install/restart belongs to startup review; event delivery latency should be judged after the watcher service is already resident.'
            steady_state_path = 'The visible budget is event-to-dispatch flow through a live watcher service, not process startup on every trigger.'
            first_use_expectation = 'Once the service is active, representative events should dispatch without a fresh process launch tax.'
            dispatch_guardrails = [
                'Keep poll-heavy or overflow-prone loops visible because they can consume the resident service budget.',
                'Prove one live delivered event before claiming the watcher path is warm.',
            ]
            summary = 'Watcher promotion should feel resident because the service owns the event plane continuously, while restart remains an operator concern.'
            cautions = ['A resident watcher can still feel cold if the event source is quiet until a heavy first sync path runs.', 'Socket activation does not guarantee the downstream event path is already warm.']
            base_commands = _merge_unique([
                'systemctl --user status vhk-busd.service || true',
                'journalctl --user -u vhk-busd.service -n 50 --no-pager || true',
            ], base_commands)
        elif surface_id == 'launcher-surface-export':
            posture = 'launch-cold'
            dispatch_lane_id = 'launcher-cold-dispatch'
            dispatch_lane_title = 'Launcher cold-start budget'
            cold_start_path = 'Treat menu/desktop entry launch as an intentionally cold path: process wake-up, shell/menu discovery, and downstream runner startup are part of the user-facing budget.'
            steady_state_path = 'A launcher can be discoverable and useful without pretending to be the low-latency owner for repeated workflows.'
            first_use_expectation = 'Every launch can pay shell/menu/process wake cost; that is acceptable only when the surface is framed as discoverability-first.'
            dispatch_guardrails = [
                'Do not substitute launcher-first wake-up paths for resident hotkey/remapper/service claims.',
                'Keep desktop-entry visibility and downstream runtime proof as separate acceptance checks.',
            ]
            summary = 'Launcher promotion should be reviewed as a cold discoverability path. It can be excellent UX without claiming edge-like dispatch.'
            cautions = ['A launcher path may mask a much colder downstream runtime than the menu itself suggests.', 'Users may blame VHK for shell/menu wake cost unless the cold-path story is explicit.']
            base_commands = _merge_unique([
                f'vhk export-desktop-entry {project_root_q}',
                f'vhk export-launcher-script {project_root_q}',
                f'vhk plan-project {project_root_q} --json',
            ], base_commands)

        evidence = _merge_unique(base_evidence, [
            f'backend={backend or "unknown"}',
            f'primary_input_lane={primary_input_lane_id or "none"}',
            f'primary_activation_route={primary_activation_route_id or "none"}',
            f'primary_control_lane={primary_control_lane_id or "none"}',
            f'primary_verification_lane={primary_verification_lane_id or "none"}',
            f'primary_performance_lane={primary_performance_lane_id or "none"}',
            *(f'performance_hotspot={hotspot_id}' for hotspot_id in hotspot_ids),
        ])[:10]
        rows.append({
            'export_surface_id': surface_id,
            'title': _surface_title(surface_id),
            'dispatch_posture': posture,
            'primary_dispatch_lane_id': dispatch_lane_id,
            'primary_dispatch_lane_title': dispatch_lane_title,
            'primary_input_lane_id': primary_input_lane_id or None,
            'primary_activation_route_id': primary_activation_route_id or None,
            'primary_control_lane_id': primary_control_lane_id or None,
            'primary_verification_lane_id': primary_verification_lane_id or None,
            'primary_performance_lane_id': primary_performance_lane_id or None,
            'cold_start_path': cold_start_path,
            'steady_state_path': steady_state_path,
            'first_use_expectation': first_use_expectation,
            'dispatch_guardrails': dispatch_guardrails,
            'performance_hotspot_ids': hotspot_ids,
            'performance_hotspot_titles': hotspot_titles,
            'host_requirement_ids': host_requirement_ids,
            'commands': base_commands[:10],
            'cautions': cautions,
            'evidence': evidence,
            'summary': summary,
        })

    posture_rank = {
        'edge-resident': 0,
        'service-resident': 1,
        'daemon-warm': 2,
        'session-resume': 3,
        'launch-cold': 4,
        'review-budget': 5,
    }
    rows.sort(key=lambda item: (posture_rank.get(str(item.get('dispatch_posture') or 'review-budget'), 9), str(item.get('title') or '')))
    return rows


def _promotion_dispatch_budget_summary(
    *,
    promotion_dispatch_budget_plan: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = [dict(item) for item in promotion_dispatch_budget_plan if isinstance(item, Mapping)]
    postures = Counter(str(item.get('dispatch_posture') or 'review-budget') for item in rows)
    lane_counts = Counter(str(item.get('primary_dispatch_lane_id') or '') for item in rows if str(item.get('primary_dispatch_lane_id') or '').strip())
    hotspot_counts = Counter(
        hotspot_id
        for item in rows
        for hotspot_id in [str(x) for x in list(item.get('performance_hotspot_ids') or []) if str(x)]
    )
    return {
        'entry_count': len(rows),
        'edge_resident_count': int(postures.get('edge-resident') or 0),
        'service_resident_count': int(postures.get('service-resident') or 0),
        'daemon_warm_count': int(postures.get('daemon-warm') or 0),
        'session_resume_count': int(postures.get('session-resume') or 0),
        'launch_cold_count': int(postures.get('launch-cold') or 0),
        'review_budget_count': int(postures.get('review-budget') or 0),
        'primary_dispatch_lane_counts': dict(lane_counts),
        'ordered_primary_dispatch_lane_ids': [lane_id for lane_id, _count in sorted(lane_counts.items(), key=lambda pair: (-pair[1], pair[0]))],
        'ordered_hotspot_ids': [hotspot_id for hotspot_id, _count in sorted(hotspot_counts.items(), key=lambda pair: (-pair[1], pair[0]))],
    }



def _promotion_authority_envelope_plan(
    *,
    project,
    export_promotion_plan: list[dict[str, Any]],
    promotion_input_lane_plan: list[dict[str, Any]] | None = None,
    promotion_activation_route_plan: list[dict[str, Any]] | None = None,
    promotion_operator_control_plan: list[dict[str, Any]] | None = None,
    promotion_dispatch_budget_plan: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Make Linux authority ownership explicit per promoted surface.

    Dispatch/startup/performance tell only part of the Linux-native story. The
    remaining question is: which layer actually *has authority* to own the
    surface — a user-session service, a portal-managed desktop session, an
    evdev/uinput remapper, or a helper daemon with socket/permission policy?
    """

    backend = str(getattr(getattr(project, 'settings', None), 'desktop_backend', None) or '').strip().lower()
    input_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_input_lane_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    activation_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_activation_route_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    control_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_operator_control_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    dispatch_rows = {str(item.get('export_surface_id') or ''): dict(item) for item in list(promotion_dispatch_budget_plan or []) if isinstance(item, Mapping) and str(item.get('export_surface_id') or '').strip()}
    project_root = getattr(project, 'root_dir', None) or '.'
    project_root_q = shlex.quote(str(project_root))

    def _merge_unique(*groups: Iterable[str]) -> list[str]:
        out: list[str] = []
        for group in groups:
            for value in group:
                value = str(value).strip()
                if value and value not in out:
                    out.append(value)
        return out

    def _surface_title(surface_id: str) -> str:
        titles = {
            'text-package-export': 'Text surface authority envelope',
            'remapper-export': 'Remapper authority envelope',
            'helper-route-dossier': 'Helper-route authority envelope',
            'watcher-service-export': 'Watcher authority envelope',
            'launcher-surface-export': 'Launcher authority envelope',
        }
        return titles.get(surface_id, surface_id)

    rows: list[dict[str, Any]] = []
    for item in export_promotion_plan:
        surface_id = str(item.get('export_surface_id') or '').strip()
        if not surface_id:
            continue
        input_row = input_rows.get(surface_id, {})
        activation_row = activation_rows.get(surface_id, {})
        control_row = control_rows.get(surface_id, {})
        dispatch_row = dispatch_rows.get(surface_id, {})
        primary_input_lane_id = str(input_row.get('primary_input_lane_id') or '').strip()
        primary_activation_route_id = str(activation_row.get('primary_activation_route_id') or '').strip()
        primary_activation_kind = str(activation_row.get('primary_activation_kind') or '').strip()
        primary_control_lane_id = str(control_row.get('primary_control_lane_id') or '').strip()
        dispatch_posture = str(dispatch_row.get('dispatch_posture') or '').strip()
        host_requirement_ids = _merge_unique(
            [str(x) for x in list(input_row.get('host_requirement_ids') or []) if str(x)],
            [str(x) for x in list(activation_row.get('host_requirement_ids') or []) if str(x)],
            [str(x) for x in list(control_row.get('host_requirement_ids') or []) if str(x)],
            [str(x) for x in list(dispatch_row.get('host_requirement_ids') or []) if str(x)],
        )
        base_commands = _merge_unique(
            [str(x) for x in list(item.get('commands') or []) if str(x)],
            [str(x) for x in list(input_row.get('commands') or []) if str(x)],
            [str(x) for x in list(activation_row.get('commands') or []) if str(x)],
            [str(x) for x in list(control_row.get('commands') or []) if str(x)],
            [str(x) for x in list(dispatch_row.get('commands') or []) if str(x)],
        )
        base_evidence = _merge_unique(
            [str(x) for x in list(item.get('evidence') or []) if str(x)],
            [str(x) for x in list(input_row.get('evidence') or []) if str(x)],
            [str(x) for x in list(activation_row.get('evidence') or []) if str(x)],
            [str(x) for x in list(control_row.get('evidence') or []) if str(x)],
            [str(x) for x in list(dispatch_row.get('evidence') or []) if str(x)],
        )
        cautions = _merge_unique(
            [str(x) for x in list(item.get('risks') or []) if str(x)],
            [str(x) for x in list(input_row.get('cautions') or []) if str(x)],
            [str(x) for x in list(activation_row.get('cautions') or []) if str(x)],
            [str(x) for x in list(control_row.get('cautions') or []) if str(x)],
            [str(x) for x in list(dispatch_row.get('cautions') or []) if str(x)],
        )[:6]

        posture = 'mixed-review'
        authority_lane_id = ''
        authority_lane_title = ''
        authority_owner = 'Review which Linux layer actually owns this surface before making parity or packaging claims.'
        authority_boundary = 'Authority crosses multiple Linux layers and remains review-bound until the shipping lane is chosen.'
        revocation_surface = 'Audit the selected trigger/helper/session boundary before treating this as a stable owned surface.'
        authority_guardrails = [
            'Keep startup, dispatch, and authority language separate so one warm path is not mistaken for broad permission or control.',
            'Name the user-session, portal, or privileged helper owner explicitly in release/install artifacts.',
        ]
        summary = 'Promotion review should say which Linux layer truly owns authority for the surface, not only how it starts or feels.'

        if surface_id == 'text-package-export':
            posture = 'session-userland'
            authority_lane_id = 'session-text-service-authority'
            authority_lane_title = 'Session text service authority'
            authority_owner = 'A user-session text service plus its config/match tree own expansion authority; the runner is upstream authoring/orchestration, not the always-on owner.'
            authority_boundary = 'Stay inside user-session authority: service lifecycle, config selection, and app/context filters matter more than privileged input ownership.'
            revocation_surface = 'Service stop/restart, wrong config path, or desktop/app-scoping drift can revoke the expected text surface without changing the macro YAML.'
            authority_guardrails = [
                'Do not treat text-service ownership as universal app-context authority on Wayland-class desktops.',
                'Keep snippet/package authority separate from rich runner prompts or interpolation-heavy fields.',
            ]
            summary = 'Text-package promotion is a session-userland surface: authority lives in the user text service and its active config, not in a privileged injector.'
            cautions = _merge_unique(cautions, ['Wayland app-specific scoping may be narrower than X11-style text shells.', 'A generated package is not the final authority unless the active service/runtime path actually loads it.'])[:6]
            base_commands = _merge_unique([
                'espanso status || true',
                'espanso path || true',
                f'vhk gen-espanso {project_root_q}',
            ], base_commands)
        elif surface_id == 'remapper-export':
            posture = 'input-edge-privileged'
            authority_lane_id = 'evdev-uinput-edge-authority'
            authority_lane_title = 'evdev/uinput edge authority'
            authority_owner = 'The remapper/input-edge service owns authority close to evdev/uinput or compositor-specific key-routing, while VHK keeps richer workflow meaning outside the remapper.'
            authority_boundary = 'This is an input-edge authority boundary with sharper privilege/service expectations than a normal user-session app: device access, uinput policy, and rescue posture all matter.'
            revocation_surface = 'Reload/panic/rollback, device access drift, or broken remapper config can revoke authority immediately at the keyboard edge.'
            authority_guardrails = [
                'Keep remapper exports thin so privileged/input-edge ownership does not absorb macro semantics or reviewable fallback logic.',
                'Document panic/recovery chords separately from ordinary operator controls.',
            ]
            summary = 'Remapper promotion is an input-edge authority story: the low-latency owner sits near evdev/uinput or compositor key routing, not in the main runner process.'
            cautions = _merge_unique(cautions, ['A fast remapper can still hand off into a slow downstream workflow.', 'The same edge authority that feels best in use can be the riskiest place to ship a broken config.'])[:6]
            base_commands = _merge_unique([
                'sudo keyd reload || true',
                'sudo keyd monitor || true',
                'sudo journalctl -eu keyd -n 50 --no-pager || true',
                f'vhk gen-keyd-config {project_root_q}',
            ], base_commands)
        elif surface_id == 'helper-route-dossier':
            if primary_input_lane_id == 'portal-permissioned-input' or primary_activation_kind == 'portal_session' or dispatch_posture == 'session-resume':
                posture = 'desktop-mediated'
                authority_lane_id = 'portal-session-authority'
                authority_lane_title = 'Portal/session authority'
                authority_owner = 'Authority is mediated by the desktop portal frontend/backend and an explicit session object rather than by a permanently privileged local daemon.'
                authority_boundary = 'Treat this as desktop-mediated authority: consent, backend routing, session lifetime, and desktop policy can narrow or revoke what the surface may do.'
                revocation_surface = 'Portal session close, consent loss, backend routing change, or session restart can revoke authority even while the project stays unchanged.'
                authority_guardrails = [
                    'Do not market portal/session ownership as equivalent to always-on remapper authority.',
                    'Keep backend routing and session lifecycle visible in operator and release docs.',
                ]
                summary = 'Portal-shaped helper routes are desktop-mediated surfaces: the desktop/session chooses when authority exists and how long it survives.'
                cautions = _merge_unique(cautions, ['Portal presence does not guarantee the right backend is routed for the needed interface.', 'A live session can disappear independently of the macro/runtime code.'])[:6]
                base_commands = _merge_unique([
                    'vhk doctor --json',
                    f'vhk gen-capability-audit-pack {project_root_q} --quiet',
                    f'vhk validate {project_root_q} --json',
                ], base_commands)
            else:
                posture = 'helper-daemon-privileged'
                authority_lane_id = 'uinput-helper-daemon-authority'
                authority_lane_title = 'uinput helper daemon authority'
                authority_owner = 'A helper daemon and its socket/uinput policy own repeated injection authority; VHK should stay the orchestrator and evidence layer, not pretend the daemon boundary is invisible.'
                authority_boundary = 'This surface depends on helper-daemon and uinput/socket authority, which is broader than a plain user app but narrower and more failure-prone than a first-party desktop protocol.'
                revocation_surface = 'Daemon stop, socket permission drift, missing /dev/uinput access, or helper package churn can revoke authority before the macro logic even runs.'
                authority_guardrails = [
                    'Keep socket path, service scope, and uinput policy reviewable instead of hiding them behind one helper name.',
                    'Prefer one warm daemon/client contract over mixed one-shot helper spawns when claiming repeated authority.',
                ]
                summary = 'Helper-sensitive promotion is a daemon/privilege story whenever repeated authority depends on a warm helper socket and /dev/uinput policy.'
                cautions = _merge_unique(cautions, ['A helper package can be installed while authority is still absent because the daemon or socket policy is wrong.', 'Warm helper authority is still an escape hatch, not proof of broad cross-desktop parity.'])[:6]
                base_commands = _merge_unique([
                    'vhk doctor --json',
                    f'vhk gen-udev-uinput --project {project_root_q} || true',
                    f'vhk validate {project_root_q} --json',
                ], base_commands)
        elif surface_id == 'watcher-service-export':
            posture = 'session-userland'
            authority_lane_id = 'resident-user-service-authority'
            authority_lane_title = 'Resident user service authority'
            authority_owner = 'A user-session watcher/bus service owns event intake and dispatch authority, while macros remain the payload behind that service boundary.'
            authority_boundary = 'This is ordinary user-session service authority: background residency and event subscriptions matter, but privileged input authority is not the main concern.'
            revocation_surface = 'Service stop, login/session churn, or lost bus/socket/event subscriptions revoke the surface even though no remapper/helper permissions changed.'
            authority_guardrails = [
                'Keep event subscriptions thin and restartable so user-session authority stays observable.',
                'Do not overstate watcher authority as if it were a global input/capture permission story.',
            ]
            summary = 'Watcher promotion is another session-userland surface, but its authority is about staying resident on the event plane rather than about owning keyboard/pointer privileges.'
            base_commands = _merge_unique([
                'systemctl --user status vhk-busd.service || true',
                'journalctl --user -u vhk-busd.service -n 50 --no-pager || true',
            ], base_commands)
        elif surface_id == 'launcher-surface-export':
            posture = 'launch-userland'
            authority_lane_id = 'desktop-entry-userland-authority'
            authority_lane_title = 'Desktop-entry userland authority'
            authority_owner = 'The desktop shell/launcher plus a user-session process launch own discoverability and execution authority; no privileged helper claim should be smuggled in through the launcher itself.'
            authority_boundary = 'This is plain launch-time userland authority shaped by desktop-entry registration and shell indexing, not by portal consent or privileged input seams.'
            revocation_surface = 'Missing desktop entry, broken launcher script, or shell index drift removes authority by making the action undiscoverable or unlaunchable.'
            authority_guardrails = [
                'Keep launcher authority claims discoverability-first; do not let a launcher stand in for resident hotkey or helper ownership.',
                'Review desktop-entry visibility separately from downstream runtime truth.',
            ]
            summary = 'Launcher promotion is a launch-userland surface: the shell grants discoverability and process start, but authority ends there unless another owned lane takes over.'
            base_commands = _merge_unique([
                f'vhk export-desktop-entry {project_root_q}',
                f'vhk export-launcher-script {project_root_q}',
            ], base_commands)

        evidence = _merge_unique(base_evidence, [
            f'backend={backend or "unknown"}',
            f'primary_input_lane={primary_input_lane_id or "none"}',
            f'primary_activation_route={primary_activation_route_id or "none"}',
            f'primary_control_lane={primary_control_lane_id or "none"}',
            f'dispatch_posture={dispatch_posture or "none"}',
        ])[:10]
        rows.append({
            'export_surface_id': surface_id,
            'title': _surface_title(surface_id),
            'authority_posture': posture,
            'primary_authority_lane_id': authority_lane_id,
            'primary_authority_lane_title': authority_lane_title,
            'primary_input_lane_id': primary_input_lane_id or None,
            'primary_activation_route_id': primary_activation_route_id or None,
            'primary_control_lane_id': primary_control_lane_id or None,
            'authority_owner': authority_owner,
            'authority_boundary': authority_boundary,
            'revocation_surface': revocation_surface,
            'authority_guardrails': authority_guardrails,
            'host_requirement_ids': host_requirement_ids,
            'commands': base_commands[:10],
            'cautions': cautions,
            'evidence': evidence,
            'summary': summary,
        })

    posture_rank = {
        'input-edge-privileged': 0,
        'desktop-mediated': 1,
        'helper-daemon-privileged': 2,
        'session-userland': 3,
        'launch-userland': 4,
        'mixed-review': 5,
    }
    rows.sort(key=lambda item: (posture_rank.get(str(item.get('authority_posture') or 'mixed-review'), 9), str(item.get('title') or '')))
    return rows


def _promotion_authority_envelope_summary(
    *,
    promotion_authority_envelope_plan: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = [dict(item) for item in promotion_authority_envelope_plan if isinstance(item, Mapping)]
    postures = Counter(str(item.get('authority_posture') or 'mixed-review') for item in rows)
    lane_counts = Counter(str(item.get('primary_authority_lane_id') or '') for item in rows if str(item.get('primary_authority_lane_id') or '').strip())
    review_ids = [str(item.get('export_surface_id') or '') for item in rows if str(item.get('authority_posture') or '') == 'mixed-review' and str(item.get('export_surface_id') or '').strip()]
    return {
        'entry_count': len(rows),
        'input_edge_privileged_count': int(postures.get('input-edge-privileged') or 0),
        'desktop_mediated_count': int(postures.get('desktop-mediated') or 0),
        'helper_daemon_privileged_count': int(postures.get('helper-daemon-privileged') or 0),
        'session_userland_count': int(postures.get('session-userland') or 0),
        'launch_userland_count': int(postures.get('launch-userland') or 0),
        'mixed_review_count': int(postures.get('mixed-review') or 0),
        'primary_authority_lane_counts': dict(lane_counts),
        'ordered_primary_authority_lane_ids': [lane_id for lane_id, _count in sorted(lane_counts.items(), key=lambda pair: (-pair[1], pair[0]))],
        'review_surface_ids': review_ids,
    }


def _promotion_waves(
    *,
    export_promotion_plan: list[dict[str, Any]],
    route_portfolio: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    route_meta: dict[str, dict[str, Any]] = {
        str(item.get('route_id') or ''): dict(item)
        for item in route_portfolio
        if isinstance(item, Mapping) and str(item.get('route_id') or '').strip()
    }

    wave_defs = [
        {
            'priority': 'high',
            'order': 1,
            'wave_id': 'wave-1-specialist-promotions',
            'title': 'Wave 1 — promote specialist export lanes',
            'goal': 'Promote the strongest text/remapper/service lanes into explicit Linux-native shipped surfaces before adding more runner-owned complexity.',
        },
        {
            'priority': 'medium',
            'order': 2,
            'wave_id': 'wave-2-helper-and-conditional-routes',
            'title': 'Wave 2 — stabilize helper and conditional lanes',
            'goal': 'Turn helper-sensitive or mixed-fit routes into explicit contracts, host checks, and reviewable fallback plans.',
        },
        {
            'priority': 'low',
            'order': 3,
            'wave_id': 'wave-3-auxiliary-shipping-surfaces',
            'title': 'Wave 3 — refine auxiliary shipping surfaces',
            'goal': 'Polish launcher and auxiliary exports once the stronger product lanes already have explicit ownership.',
        },
    ]
    buckets: dict[str, dict[str, Any]] = {
        str(item['priority']): {
            **item,
            'items': [],
            'route_ids': [],
            'commands': [],
            'macros': [],
            'evidence': [],
            'risks': [],
        }
        for item in wave_defs
    }

    for item in export_promotion_plan:
        priority = str(item.get('priority') or 'medium').strip().lower() or 'medium'
        bucket = buckets.get(priority)
        if bucket is None:
            continue
        bucket['items'].append(dict(item))
        for route_id in item.get('route_ids') or []:
            route_id = str(route_id).strip()
            if route_id and route_id not in bucket['route_ids']:
                bucket['route_ids'].append(route_id)
        for command in item.get('commands') or []:
            command = str(command).strip()
            if command and command not in bucket['commands']:
                bucket['commands'].append(command)
        for macro in item.get('macros') or []:
            macro = str(macro).strip()
            if macro and macro not in bucket['macros']:
                bucket['macros'].append(macro)
        for value in item.get('evidence') or []:
            value = str(value).strip()
            if value and value not in bucket['evidence']:
                bucket['evidence'].append(value)
        for value in item.get('risks') or []:
            value = str(value).strip()
            if value and value not in bucket['risks']:
                bucket['risks'].append(value)

    rows: list[dict[str, Any]] = []
    for priority in ['high', 'medium', 'low']:
        bucket = buckets[priority]
        items = [dict(item) for item in list(bucket.get('items') or []) if isinstance(item, Mapping)]
        if not items:
            continue
        route_summaries = []
        for route_id in list(bucket.get('route_ids') or []):
            route = route_meta.get(route_id) or {}
            route_summaries.append({
                'route_id': route_id,
                'title': str(route.get('title') or route_id),
                'macro_count': int(route.get('macro_count') or 0),
                'dominant_fit': str(route.get('dominant_fit') or 'good'),
                'example_macros': [str(x) for x in list(route.get('example_macros') or [])[:4] if str(x)],
            })
        rows.append({
            'wave_id': str(bucket.get('wave_id') or ''),
            'order': int(bucket.get('order') or 0),
            'priority': priority,
            'title': str(bucket.get('title') or ''),
            'goal': str(bucket.get('goal') or ''),
            'surface_count': len(items),
            'macro_count': len(list(bucket.get('macros') or [])),
            'export_surface_ids': [str(item.get('export_surface_id') or '') for item in items if str(item.get('export_surface_id') or '')],
            'surfaces': [str(item.get('title') or item.get('export_surface_id') or '') for item in items],
            'route_ids': list(bucket.get('route_ids') or []),
            'routes': route_summaries,
            'macros': list(bucket.get('macros') or [])[:10],
            'commands': list(bucket.get('commands') or [])[:8],
            'evidence': list(bucket.get('evidence') or [])[:10],
            'risks': list(bucket.get('risks') or [])[:10],
        })

    rows.sort(key=lambda item: int(item.get('order') or 99))
    return rows




def _promotion_readiness(
    *,
    project,
    export_promotion_plan: list[dict[str, Any]],
    route_portfolio: list[dict[str, Any]],
    capability_matrix: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    backend = str(getattr(getattr(project, 'settings', None), 'desktop_backend', None) or '').strip().lower()
    capability_matrix = capability_matrix or {}

    route_meta: dict[str, dict[str, Any]] = {
        str(item.get('route_id') or ''): dict(item)
        for item in route_portfolio
        if isinstance(item, Mapping) and str(item.get('route_id') or '').strip()
    }

    def cap_status(name: str) -> str:
        return _capability_status(capability_matrix, name, default='unknown')

    def merge_state(current: str, incoming: str) -> str:
        rank = {'ready': 0, 'review': 1, 'blocked': 2}
        return incoming if rank.get(incoming, 1) > rank.get(current, 1) else current

    def next_action_for(surface_id: str, state: str) -> str:
        if surface_id == 'text-package-export':
            if state == 'blocked':
                return 'Keep text flows in the runner/clipboard lane until a dependable text injection surface exists on the target desktop.'
            if state == 'review':
                return 'Validate text injection, package behavior, and app scoping on each target desktop before promoting snippets out of the runner.'
            return 'Promote the text lane into a packaged snippet surface and keep the runner for prompts/forms that exceed snippet semantics.'
        if surface_id == 'remapper-export':
            if state == 'blocked':
                return 'Keep remap-like flows inside VHK fallback paths until a stable remapper/export contract exists for the target session.'
            if state == 'review':
                return 'Generate remapper configs, then verify per-app context and fallback behavior on each target desktop.'
            return 'Promote low-latency key transforms into remapper exports and keep the runner only for richer follow-on flows.'
        if surface_id == 'watcher-service-export':
            return 'Package watcher ownership as a long-lived service and keep event payloads thin.'
        if surface_id == 'helper-route-dossier':
            if state == 'blocked':
                return 'Keep this surface as an explicit helper dossier until capture/input requirements are satisfied on the target session.'
            return 'Document helper seams, host checks, and fallback routes before shipping the macro as desktop-agnostic Linux automation.'
        if surface_id == 'launcher-surface-export':
            return 'Ship this flow as a launcher/palette surface with stable action ids and desktop-entry review.'
        return 'Keep promotion work staged and explicit rather than assuming one backend owns all Linux sessions.'

    rows: list[dict[str, Any]] = []
    for item in export_promotion_plan:
        surface_id = str(item.get('export_surface_id') or '').strip()
        if not surface_id:
            continue
        dominant_fit = str(item.get('dominant_fit') or 'good').strip() or 'good'
        priority = str(item.get('priority') or 'medium').strip() or 'medium'
        state = 'ready'
        if dominant_fit == 'weak':
            state = 'blocked'
        elif dominant_fit == 'conditional':
            state = 'review'

        blockers: list[str] = []
        review_notes: list[str] = []
        required_capabilities: list[str] = []
        missing_capabilities: list[str] = []

        evidence = [str(x) for x in list(item.get('evidence') or []) if str(x)]
        risks = [str(x) for x in list(item.get('risks') or []) if str(x)]
        route_ids = [str(x) for x in list(item.get('route_ids') or []) if str(x)]

        def require_cap(cap_name: str, *, blocked_when: set[str] | None = None, review_when: set[str] | None = None, note: str | None = None) -> None:
            nonlocal state
            if cap_name not in required_capabilities:
                required_capabilities.append(cap_name)
            status = cap_status(cap_name)
            if status in (blocked_when or {'missing'}):
                state = merge_state(state, 'blocked')
                missing_capabilities.append(cap_name)
                blockers.append(f'{cap_name} session status is {status}')
            elif status in (review_when or {'limited', 'degraded', 'planned', 'unknown'}):
                state = merge_state(state, 'review')
                text = note or f'{cap_name} session status is {status}'
                if text not in review_notes:
                    review_notes.append(text)

        if surface_id == 'text-package-export':
            require_cap('text_injection', note='text injection should be verified on the target desktop before promoting snippet work out of the runner')
            if backend == 'wayland':
                state = merge_state(state, 'review')
                review_notes.append('Wayland text expansion remains tool/compositor-sensitive; verify package behavior and app-scoping expectations explicitly')
        elif surface_id == 'remapper-export':
            if backend == 'wayland':
                state = merge_state(state, 'review')
                review_notes.append('Wayland remapper exports still depend on compositor/app-context bridges; validate per-desktop scope explicitly')
            if any('window/app scope' in risk or 'app-specific' in risk for risk in risks):
                state = merge_state(state, 'review')
                review_notes.append('app/window-specific remap scope needs desktop-specific context support')
        elif surface_id == 'watcher-service-export':
            if backend == 'wayland' and any(route_id == 'watcher-service' for route_id in route_ids):
                review_notes.append('watcher services are mostly desktop-agnostic, but operator packaging should still be checked per target session')
        elif surface_id == 'helper-route-dossier':
            state = merge_state(state, 'review')
            if 'pointer_injection' in evidence or any('pointer injection' in risk for risk in risks):
                require_cap('pointer_injection', note='pointer injection is a sharp Linux/Wayland portability boundary and should be host-verified')
            if 'screen_capture' in evidence or any('capture' in risk.lower() for risk in risks):
                require_cap('screen_capture', note='screen capture helpers and region bounds should be verified on the target session')
            if backend == 'wayland':
                review_notes.append('helper-boundary routes on Wayland should ship with explicit helper contracts instead of generic parity claims')
        elif surface_id == 'launcher-surface-export':
            if backend == 'wayland':
                review_notes.append('launcher surfaces are usually the safest Wayland lane, but desktop-entry registration still deserves review')

        if dominant_fit == 'weak' and 'dominant fit is weak' not in blockers:
            blockers.append('dominant fit is weak')

        route_summary = [
            {
                'route_id': route_id,
                'title': str((route_meta.get(route_id) or {}).get('title') or route_id),
                'macro_count': int((route_meta.get(route_id) or {}).get('macro_count') or 0),
                'dominant_fit': str((route_meta.get(route_id) or {}).get('dominant_fit') or dominant_fit),
            }
            for route_id in route_ids[:4]
        ]

        rows.append({
            'export_surface_id': surface_id,
            'title': str(item.get('title') or surface_id),
            'priority': priority,
            'dominant_fit': dominant_fit,
            'readiness_status': state,
            'macro_count': int(item.get('macro_count') or 0),
            'route_ids': route_ids,
            'routes': route_summary,
            'macros': [str(x) for x in list(item.get('macros') or [])[:8] if str(x)],
            'tool_family': [str(x) for x in list(item.get('tool_family') or [])[:6] if str(x)],
            'required_capabilities': required_capabilities,
            'missing_capabilities': list(dict.fromkeys(missing_capabilities)),
            'blockers': list(dict.fromkeys(blockers)),
            'review_notes': list(dict.fromkeys(review_notes)),
            'blocker_count': len(list(dict.fromkeys(blockers))),
            'next_action': next_action_for(surface_id, state),
            'commands': [str(x) for x in list(item.get('commands') or [])[:6] if str(x)],
            'evidence': evidence[:8],
            'risks': risks[:8],
        })

    status_rank = {'blocked': 0, 'review': 1, 'ready': 2}
    priority_rank = {'high': 0, 'medium': 1, 'low': 2}
    rows.sort(key=lambda item: (status_rank.get(str(item.get('readiness_status') or 'review'), 9), priority_rank.get(str(item.get('priority') or 'medium'), 9), -int(item.get('macro_count') or 0), str(item.get('title') or '')))
    return rows


def _promotion_readiness_summary(
    *,
    promotion_readiness: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = [dict(item) for item in promotion_readiness if isinstance(item, Mapping)]
    by_status = Counter(str(item.get('readiness_status') or 'review') for item in rows)
    high_priority_review = [
        str(item.get('export_surface_id') or '')
        for item in rows
        if str(item.get('priority') or '') == 'high' and str(item.get('readiness_status') or '') in {'review', 'blocked'} and str(item.get('export_surface_id') or '')
    ]
    return {
        'surface_count': len(rows),
        'ready_count': int(by_status.get('ready') or 0),
        'review_count': int(by_status.get('review') or 0),
        'blocked_count': int(by_status.get('blocked') or 0),
        'high_priority_review_surfaces': high_priority_review,
        'helper_review_count': sum(1 for item in rows if str(item.get('export_surface_id') or '') == 'helper-route-dossier' and str(item.get('readiness_status') or '') in {'review', 'blocked'}),
    }


def _promotion_gates(
    *,
    project,
    promotion_waves: list[dict[str, Any]],
    promotion_readiness: list[dict[str, Any]],
    readiness_summary: Mapping[str, Any],
) -> list[dict[str, Any]]:
    backend = str(getattr(getattr(project, 'settings', None), 'desktop_backend', None) or '').strip().lower()
    readiness_rows = [dict(item) for item in promotion_readiness if isinstance(item, Mapping)]
    wave_rows = [dict(item) for item in promotion_waves if isinstance(item, Mapping)]
    by_surface = {str(item.get('export_surface_id') or ''): item for item in readiness_rows if str(item.get('export_surface_id') or '').strip()}
    high_surfaces = [item for item in readiness_rows if str(item.get('priority') or '') == 'high']
    medium_surfaces = [item for item in readiness_rows if str(item.get('priority') or '') == 'medium']
    low_surfaces = [item for item in readiness_rows if str(item.get('priority') or '') == 'low']
    helper_surfaces = [item for item in readiness_rows if str(item.get('export_surface_id') or '') == 'helper-route-dossier']
    blocked_count = int(readiness_summary.get('blocked_count') or 0)
    review_count = int(readiness_summary.get('review_count') or 0)

    def gate_status(rows: list[dict[str, Any]], *, empty_status: str = 'pass') -> str:
        if not rows:
            return empty_status
        statuses = {str(item.get('readiness_status') or 'review') for item in rows}
        if 'blocked' in statuses:
            return 'fail'
        if 'review' in statuses:
            return 'review'
        return 'pass'

    def build_gate(
        gate_id: str,
        title: str,
        status: str,
        summary: str,
        rows: list[dict[str, Any]],
        *,
        rationale: str,
        commands: list[str] | None = None,
        wave_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        ready = [str(item.get('export_surface_id') or '') for item in rows if str(item.get('readiness_status') or '') == 'ready' and str(item.get('export_surface_id') or '')]
        review = [str(item.get('export_surface_id') or '') for item in rows if str(item.get('readiness_status') or '') == 'review' and str(item.get('export_surface_id') or '')]
        blocked = [str(item.get('export_surface_id') or '') for item in rows if str(item.get('readiness_status') or '') == 'blocked' and str(item.get('export_surface_id') or '')]
        affected = [str(item.get('export_surface_id') or '') for item in rows if str(item.get('export_surface_id') or '')]
        return {
            'gate_id': gate_id,
            'title': title,
            'status': status,
            'summary': summary,
            'rationale': rationale,
            'surface_count': len(affected),
            'affected_surfaces': affected,
            'ready_surfaces': ready,
            'review_surfaces': review,
            'blocking_surfaces': blocked,
            'commands': list(dict.fromkeys(str(x) for x in (commands or []) if str(x)))[:8],
            'wave_ids': [str(x) for x in list(dict.fromkeys(wave_ids or [])) if str(x)],
        }

    gates: list[dict[str, Any]] = []

    high_status = gate_status(high_surfaces, empty_status='review' if medium_surfaces or low_surfaces else 'pass')
    high_cmds = [
        cmd
        for item in high_surfaces
        for cmd in list(item.get('commands') or [])
        if str(cmd)
    ]
    high_wave_ids = [str(item.get('wave_id') or '') for item in wave_rows if str(item.get('priority') or '') == 'high' and str(item.get('wave_id') or '')]
    if not high_surfaces:
        high_summary = 'No specialist high-priority promotion surfaces are staged yet.'
    elif high_status == 'fail':
        high_summary = 'At least one high-priority Linux-native export surface is blocked.'
    elif high_status == 'review':
        high_summary = 'High-priority export surfaces exist, but at least one still needs session/tooling review.'
    else:
        high_summary = 'High-priority export surfaces look promotable with the current fit/capability signals.'
    gates.append(build_gate(
        'specialist-surface-gate',
        'Specialist surface gate',
        high_status,
        high_summary,
        high_surfaces,
        rationale='Promote text/remapper/service lanes first so Linux-native specialist surfaces are explicit before more helper-heavy work claims parity.',
        commands=['vhk plan-project . --json', *high_cmds],
        wave_ids=high_wave_ids,
    ))

    helper_status = gate_status(helper_surfaces, empty_status='pass')
    helper_cmds = [
        cmd
        for item in helper_surfaces
        for cmd in list(item.get('commands') or [])
        if str(cmd)
    ]
    helper_wave_ids = [str(item.get('wave_id') or '') for item in wave_rows if str(item.get('priority') or '') == 'medium' and str(item.get('wave_id') or '')]
    if not helper_surfaces:
        helper_summary = 'No helper-boundary promotion surface is currently prominent.'
    elif helper_status == 'fail':
        helper_summary = 'At least one helper-sensitive promotion surface is blocked and should stay dossier-only.'
    elif helper_status == 'review':
        helper_summary = 'Helper-sensitive promotion surfaces exist and should ship with explicit host/session review instead of generic Linux claims.'
    else:
        helper_summary = 'Helper-sensitive routes appear documented enough to stage with explicit contracts.'
    gates.append(build_gate(
        'helper-boundary-gate',
        'Helper-boundary gate',
        helper_status,
        helper_summary,
        helper_surfaces,
        rationale='Capture/injection helpers remain the sharpest Linux portability boundary, especially on Wayland, so these routes need explicit contracts and fallback stories.',
        commands=['vhk plan-project . --json', 'vhk gen-promotion-pack . --force --quiet', *helper_cmds],
        wave_ids=helper_wave_ids,
    ))

    sequencing_rows = [item for item in readiness_rows if str(item.get('priority') or '') in {'medium', 'low'}]
    later_ready = [item for item in sequencing_rows if str(item.get('readiness_status') or '') == 'ready']
    if high_status == 'fail' and later_ready:
        sequencing_status = 'review'
        sequencing_summary = 'Later-wave surfaces look ready while specialist lanes are still blocked; promotion order should stay explicit.'
    elif high_status == 'review' and later_ready:
        sequencing_status = 'review'
        sequencing_summary = 'Some later-wave surfaces look ready, but high-priority lanes still need review before broad Linux-native claims.'
    else:
        sequencing_status = 'pass'
        sequencing_summary = 'Promotion ordering looks disciplined: later-wave surfaces are not outpacing the stronger specialist lanes.'
    sequencing_wave_ids = [str(item.get('wave_id') or '') for item in wave_rows if str(item.get('wave_id') or '')]
    gates.append(build_gate(
        'promotion-sequencing-gate',
        'Promotion sequencing gate',
        sequencing_status,
        sequencing_summary,
        sequencing_rows,
        rationale='Linux-native surface work should stage strong specialist lanes first, then helper/auxiliary surfaces, so the repo does not promise breadth before depth.',
        commands=['vhk plan-project . --json', 'vhk gen-promotion-pack . --force --quiet'],
        wave_ids=sequencing_wave_ids,
    ))

    claim_status = 'pass'
    if blocked_count > 0:
        claim_status = 'fail'
    elif review_count > 0 or backend == 'wayland':
        claim_status = 'review' if readiness_rows else 'pass'
    claim_summary = 'Current Linux-native claims look aligned with the promotion/readiness signals.'
    if claim_status == 'fail':
        claim_summary = 'At least one export surface is blocked; release notes/docs should avoid broad Linux parity language.'
    elif claim_status == 'review':
        claim_summary = 'Some export surfaces still need review; docs and packaging should stay explicit about target sessions and fallbacks.'
    gates.append(build_gate(
        'claim-discipline-gate',
        'Claim discipline gate',
        claim_status,
        claim_summary,
        readiness_rows,
        rationale='Linux automation tools diverge sharply by desktop/session, so VHK should keep release claims matched to verified surfaces instead of promising generic parity.',
        commands=['vhk plan-project . --json', 'vhk gen-promotion-pack . --force --quiet', 'vhk lint-project . --no-session-check'],
        wave_ids=sequencing_wave_ids,
    ))

    rank = {'fail': 0, 'review': 1, 'pass': 2}
    gates.sort(key=lambda item: (rank.get(str(item.get('status') or 'review'), 9), str(item.get('title') or '')))
    return gates


def _promotion_gate_summary(
    *,
    promotion_gates: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = [dict(item) for item in promotion_gates if isinstance(item, Mapping)]
    by_status = Counter(str(item.get('status') or 'review') for item in rows)
    return {
        'gate_count': len(rows),
        'pass_count': int(by_status.get('pass') or 0),
        'review_count': int(by_status.get('review') or 0),
        'fail_count': int(by_status.get('fail') or 0),
        'failing_gate_ids': [str(item.get('gate_id') or '') for item in rows if str(item.get('status') or '') == 'fail' and str(item.get('gate_id') or '')],
        'review_gate_ids': [str(item.get('gate_id') or '') for item in rows if str(item.get('status') or '') == 'review' and str(item.get('gate_id') or '')],
    }


def _promotion_backlog(
    *,
    promotion_waves: list[dict[str, Any]],
    promotion_readiness: list[dict[str, Any]],
    promotion_gates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    wave_by_surface: dict[str, dict[str, Any]] = {}
    for wave in promotion_waves:
        if not isinstance(wave, Mapping):
            continue
        wave_row = dict(wave)
        for surface_id in list(wave_row.get('export_surface_ids') or []):
            text = str(surface_id or '').strip()
            if text and text not in wave_by_surface:
                wave_by_surface[text] = wave_row

    priority_rank = {'high': 0, 'medium': 1, 'low': 2}
    queue_rank = {'blocked': 0, 'review': 1, 'todo': 2, 'done': 3}

    rows: list[dict[str, Any]] = []

    def add_task(
        task_id: str,
        title: str,
        *,
        queue_state: str,
        kind: str,
        priority: str = 'medium',
        wave_id: str = '',
        wave_title: str = '',
        export_surface_id: str = '',
        gate_id: str = '',
        rationale: str = '',
        next_action: str = '',
        blockers: list[str] | None = None,
        review_notes: list[str] | None = None,
        commands: list[str] | None = None,
        required_capabilities: list[str] | None = None,
        related_routes: list[str] | None = None,
    ) -> None:
        rows.append({
            'task_id': task_id,
            'title': title,
            'queue_state': queue_state,
            'kind': kind,
            'priority': priority,
            'wave_id': wave_id,
            'wave_title': wave_title,
            'export_surface_id': export_surface_id,
            'gate_id': gate_id,
            'rationale': rationale,
            'next_action': next_action,
            'blockers': [str(x) for x in list(blockers or []) if str(x)][:6],
            'review_notes': [str(x) for x in list(review_notes or []) if str(x)][:6],
            'commands': [str(x) for x in list(commands or []) if str(x)][:6],
            'required_capabilities': [str(x) for x in list(required_capabilities or []) if str(x)][:6],
            'related_routes': [str(x) for x in list(related_routes or []) if str(x)][:6],
        })

    for item in promotion_readiness:
        if not isinstance(item, Mapping):
            continue
        row = dict(item)
        surface_id = str(row.get('export_surface_id') or '').strip()
        if not surface_id:
            continue
        status = str(row.get('readiness_status') or 'review').strip().lower() or 'review'
        priority = str(row.get('priority') or 'medium').strip().lower() or 'medium'
        wave = wave_by_surface.get(surface_id) or {}
        wave_id = str(wave.get('wave_id') or '')
        wave_title = str(wave.get('title') or '')
        surface_title = str(row.get('title') or surface_id)

        if status == 'ready':
            queue_state = 'todo'
            kind = 'promote'
            title = f'Promote {surface_title}'
            rationale = 'This surface is the strongest current Linux-native ownership candidate for the related macros.'
            next_action = str(row.get('next_action') or 'Generate the export surface and verify it on a target desktop.')
        elif status == 'blocked':
            queue_state = 'blocked'
            kind = 'unblock'
            title = f'Unblock {surface_title}'
            rationale = 'The planner sees missing capabilities or weak fit, so this surface should not ship until its blockers are explicit.'
            next_action = str(row.get('next_action') or 'Keep this surface behind fallback paths until the blocker list is resolved.')
        else:
            queue_state = 'review'
            kind = 'review'
            title = f'Review {surface_title}'
            rationale = 'This surface wants promotion, but it still needs desktop/session/tooling confirmation before it becomes a release promise.'
            next_action = str(row.get('next_action') or 'Run the review commands and confirm the target session story.')

        add_task(
            f'surface:{surface_id}',
            title,
            queue_state=queue_state,
            kind=kind,
            priority=priority,
            wave_id=wave_id,
            wave_title=wave_title,
            export_surface_id=surface_id,
            rationale=rationale,
            next_action=next_action,
            blockers=[str(x) for x in list(row.get('blockers') or []) if str(x)],
            review_notes=[str(x) for x in list(row.get('review_notes') or []) if str(x)],
            commands=[str(x) for x in list(row.get('commands') or []) if str(x)],
            required_capabilities=[str(x) for x in list(row.get('required_capabilities') or []) if str(x)],
            related_routes=[str(x) for x in list(row.get('route_ids') or []) if str(x)],
        )

    for item in promotion_gates:
        if not isinstance(item, Mapping):
            continue
        row = dict(item)
        status = str(row.get('status') or 'review').strip().lower() or 'review'
        if status == 'pass':
            continue
        gate_id = str(row.get('gate_id') or '').strip()
        if not gate_id:
            continue
        wave_ids = [str(x) for x in list(row.get('wave_ids') or []) if str(x)]
        wave_id = wave_ids[0] if wave_ids else ''
        wave = next((dict(item) for item in promotion_waves if isinstance(item, Mapping) and str(item.get('wave_id') or '') == wave_id), {})
        wave_title = str(wave.get('title') or '')
        queue_state = 'blocked' if status == 'fail' else 'review'
        priority = 'high' if status == 'fail' else 'medium'
        add_task(
            f'gate:{gate_id}',
            f"{str(row.get('title') or gate_id)} review",
            queue_state=queue_state,
            kind='gate',
            priority=priority,
            wave_id=wave_id,
            wave_title=wave_title,
            gate_id=gate_id,
            rationale=str(row.get('rationale') or 'Promotion claim/review work should stay in the same queue as the surfaces it governs.'),
            next_action=str(row.get('summary') or 'Review the affected surfaces and keep claims aligned with verified capabilities.'),
            blockers=[str(x) for x in list(row.get('blocking_surfaces') or []) if str(x)],
            review_notes=[str(x) for x in list(row.get('review_surfaces') or []) if str(x)],
            commands=[str(x) for x in list(row.get('commands') or []) if str(x)],
        )

    rows.sort(key=lambda item: (
        priority_rank.get(str(item.get('priority') or 'medium'), 9),
        queue_rank.get(str(item.get('queue_state') or 'review'), 9),
        str(item.get('wave_id') or ''),
        str(item.get('title') or ''),
    ))
    return rows


def _promotion_backlog_summary(
    *,
    promotion_backlog: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = [dict(item) for item in promotion_backlog if isinstance(item, Mapping)]
    by_state = Counter(str(item.get('queue_state') or 'review') for item in rows)
    by_kind = Counter(str(item.get('kind') or 'review') for item in rows)
    return {
        'task_count': len(rows),
        'blocked_count': int(by_state.get('blocked') or 0),
        'review_count': int(by_state.get('review') or 0),
        'todo_count': int(by_state.get('todo') or 0),
        'promote_count': int(by_kind.get('promote') or 0),
        'review_task_count': int(by_kind.get('review') or 0),
        'unblock_count': int(by_kind.get('unblock') or 0),
        'gate_task_count': int(by_kind.get('gate') or 0),
        'high_priority_task_ids': [str(item.get('task_id') or '') for item in rows if str(item.get('priority') or '') == 'high' and str(item.get('task_id') or '')][:8],
    }


def _promotion_evidence(
    *,
    project,
    promotion_readiness: list[dict[str, Any]],
    promotion_gates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    project_root = Path(str(getattr(project, 'root_dir', None) or '.')).expanduser().resolve()

    def rel_paths(paths: list[str]) -> tuple[list[str], list[str], list[str]]:
        required: list[str] = []
        present: list[str] = []
        missing: list[str] = []
        for raw in paths:
            text = str(raw or '').strip()
            if not text or text in required:
                continue
            required.append(text)
            if (project_root / text).exists():
                present.append(text)
            else:
                missing.append(text)
        return required, present, missing

    def build_entry(
        evidence_id: str,
        title: str,
        *,
        subject_kind: str,
        subject_id: str,
        posture: str,
        rationale: str,
        required_artifacts: list[str],
        commands: list[str] | None = None,
        blockers: list[str] | None = None,
        review_notes: list[str] | None = None,
    ) -> dict[str, Any]:
        required, present, missing = rel_paths(required_artifacts)
        if not required:
            status = 'complete'
        elif not missing:
            status = 'complete'
        elif present:
            status = 'partial'
        else:
            status = 'missing'
        return {
            'evidence_id': evidence_id,
            'title': title,
            'subject_kind': subject_kind,
            'subject_id': subject_id,
            'posture': posture,
            'evidence_status': status,
            'required_artifacts': required,
            'present_artifacts': present,
            'missing_artifacts': missing,
            'required_count': len(required),
            'present_count': len(present),
            'missing_count': len(missing),
            'rationale': rationale,
            'commands': [str(x) for x in list(dict.fromkeys(commands or [])) if str(x)][:8],
            'blockers': [str(x) for x in list(blockers or []) if str(x)][:6],
            'review_notes': [str(x) for x in list(review_notes or []) if str(x)][:6],
        }

    surface_artifacts: dict[str, list[str]] = {
        'text-package-export': [
            'docs/VHK_SETUP_GUIDE.md',
            'docs/VHK_CLAIM_GUIDE.md',
            'docs/VHK_VERIFICATION_GUIDE.md',
        ],
        'remapper-export': [
            'docs/VHK_ROUTE_SELECTION.md',
            'docs/VHK_SETUP_GUIDE.md',
            'docs/VHK_VERIFICATION_GUIDE.md',
        ],
        'watcher-service-export': [
            'docs/VHK_HOST_REQUIREMENTS.md',
            'docs/VHK_READINESS_REPORT.md',
            'docs/VHK_VERIFICATION_GUIDE.md',
        ],
        'helper-route-dossier': [
            'docs/VHK_TARGET_ROUTE_MATRIX.md',
            'docs/VHK_ROUTE_SELECTION.md',
            'docs/VHK_HOST_REQUIREMENTS.md',
            'docs/VHK_DESIGN_BRIEF.md',
        ],
        'launcher-surface-export': [
            'docs/VHK_SETUP_GUIDE.md',
            'docs/VHK_VERIFICATION_GUIDE.md',
            'docs/VHK_PUBLIC_SUPPORT.md',
        ],
    }
    gate_artifacts: dict[str, list[str]] = {
        'specialist-surface-gate': [
            'docs/VHK_SETUP_GUIDE.md',
            'docs/VHK_VERIFICATION_GUIDE.md',
            'docs/VHK_CLAIM_GUIDE.md',
        ],
        'helper-boundary-gate': [
            'docs/VHK_TARGET_ROUTE_MATRIX.md',
            'docs/VHK_ROUTE_SELECTION.md',
            'docs/VHK_HOST_REQUIREMENTS.md',
        ],
        'promotion-sequencing-gate': [
            'docs/VHK_PROMOTION_PLAN.md',
            'docs/VHK_PROMOTION_BACKLOG.md',
        ],
        'claim-discipline-gate': [
            'docs/VHK_CLAIM_GUIDE.md',
            'docs/VHK_TARGET_CLAIMS.yaml',
            'docs/VHK_PUBLIC_SUPPORT.md',
        ],
    }
    surface_rationales = {
        'text-package-export': 'Text-tier promotion should ship with setup, verification, and support-claim proof so snippet surfaces are not treated as generic Linux replay.',
        'remapper-export': 'Remapper promotion needs route selection plus verification/setup proof because low-latency key ownership is a different product lane from the runner.',
        'watcher-service-export': 'Watcher/service promotion needs host and readiness proof so long-lived Linux services are reviewable before they become a support promise.',
        'helper-route-dossier': 'Helper-sensitive routes need route, host, and design proof so capture/input boundaries stay explicit instead of turning into parity folklore.',
        'launcher-surface-export': 'Launcher promotion should carry setup, verification, and outward-facing support proof so desktop entrypoints inherit the same honesty as the runtime.',
    }
    gate_rationales = {
        'specialist-surface-gate': 'Strong specialist surfaces should have setup/verification/claim artifacts before they anchor release language.',
        'helper-boundary-gate': 'Helper-boundary claims need explicit route and host artifacts because Linux session behavior diverges sharply around capture and injection.',
        'promotion-sequencing-gate': 'Promotion ordering needs its own checked-in plan/backlog so later surfaces do not outrun stronger early lanes.',
        'claim-discipline-gate': 'Claim discipline needs claim/public-support artifacts so packaging and docs repeat the same support story the planner sees.',
    }

    rows: list[dict[str, Any]] = []
    for item in promotion_readiness:
        if not isinstance(item, Mapping):
            continue
        row = dict(item)
        surface_id = str(row.get('export_surface_id') or '').strip()
        if not surface_id:
            continue
        rows.append(build_entry(
            f'surface:{surface_id}',
            f"{str(row.get('title') or surface_id)} evidence",
            subject_kind='surface',
            subject_id=surface_id,
            posture=str(row.get('readiness_status') or 'review') or 'review',
            rationale=str(surface_rationales.get(surface_id) or 'Promotion surfaces should ship with explicit review artifacts, not just planner tables.'),
            required_artifacts=surface_artifacts.get(surface_id, ['docs/VHK_VERIFICATION_GUIDE.md', 'docs/VHK_CLAIM_GUIDE.md']),
            commands=[str(x) for x in list(row.get('commands') or []) if str(x)],
            blockers=[str(x) for x in list(row.get('blockers') or []) if str(x)],
            review_notes=[str(x) for x in list(row.get('review_notes') or []) if str(x)],
        ))

    for item in promotion_gates:
        if not isinstance(item, Mapping):
            continue
        row = dict(item)
        gate_id = str(row.get('gate_id') or '').strip()
        if not gate_id:
            continue
        rows.append(build_entry(
            f'gate:{gate_id}',
            f"{str(row.get('title') or gate_id)} evidence",
            subject_kind='gate',
            subject_id=gate_id,
            posture=str(row.get('status') or 'review') or 'review',
            rationale=str(gate_rationales.get(gate_id) or 'Promotion gates need checked-in proof artifacts so claim posture can be reviewed outside the terminal.'),
            required_artifacts=gate_artifacts.get(gate_id, ['docs/VHK_PROMOTION_PLAN.md']),
            commands=[str(x) for x in list(row.get('commands') or []) if str(x)],
            blockers=[str(x) for x in list(row.get('blocking_surfaces') or []) if str(x)],
            review_notes=[str(x) for x in list(row.get('review_surfaces') or []) if str(x)],
        ))

    status_rank = {'missing': 0, 'partial': 1, 'complete': 2}
    rows.sort(key=lambda item: (status_rank.get(str(item.get('evidence_status') or 'partial'), 9), str(item.get('subject_kind') or ''), str(item.get('title') or '')))
    return rows


def _promotion_evidence_summary(
    *,
    promotion_evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = [dict(item) for item in promotion_evidence if isinstance(item, Mapping)]
    by_status = Counter(str(item.get('evidence_status') or 'partial') for item in rows)
    return {
        'entry_count': len(rows),
        'complete_count': int(by_status.get('complete') or 0),
        'partial_count': int(by_status.get('partial') or 0),
        'missing_count': int(by_status.get('missing') or 0),
        'missing_ids': [str(item.get('evidence_id') or '') for item in rows if str(item.get('evidence_status') or '') == 'missing' and str(item.get('evidence_id') or '')][:10],
        'partial_ids': [str(item.get('evidence_id') or '') for item in rows if str(item.get('evidence_status') or '') == 'partial' and str(item.get('evidence_id') or '')][:10],
    }


def summarize_project_strategy(
    project,
    *,
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
    capability_matrix: Mapping[str, Any] | None = None,
    capability_issues: list[dict[str, Any]] | None = None,
    host_truth: Mapping[str, Any] | None = None,
    portal_route_contract: Mapping[str, Any] | None = None,
    evidence_lane_profile: str | None = None,
) -> dict[str, Any]:
    triggers = _macro_triggers(project)
    macro_profiles = [_classify_macro(macro=macro, triggers=triggers.get(name, [])) for name, macro in getattr(project, "macros", {}).items()]
    macro_profiles.sort(key=lambda item: (bool(item.get("hidden")), str(item.get("macro"))))

    tag_counter = Counter()
    for item in macro_profiles:
        for tag in item.get("tags") or []:
            tag_counter[str(tag)] += 1

    window_contract = summarize_project_window_contract(project)

    overview = {
        "macros": len(getattr(project, "macros", {}) or {}),
        "regions": len(getattr(project, "regions", {}) or {}),
        "bindings": len(getattr(project, "bindings", []) or []),
        "hotstrings": len(getattr(project, "hotstrings", []) or []),
        "clipboard_watchers": len(getattr(project, "clipboard_watchers", []) or []),
        "file_watchers": len(getattr(project, "file_watchers", []) or []),
        "bus_watchers": len(getattr(project, "bus_watchers", []) or []),
        "window_watchers": len(getattr(project, "window_watchers", []) or []),
        "presets": sum(len(getattr(m, "presets", []) or []) for m in getattr(project, "macros", {}).values()),
    }

    project_tags: list[str] = []
    if overview["hotstrings"]:
        project_tags.append("text-expander-integration")
    if overview["bindings"] or overview["window_watchers"]:
        project_tags.append("wm-integrated")
    if overview["bus_watchers"] or overview["clipboard_watchers"] or overview.get("file_watchers") or overview["window_watchers"]:
        project_tags.append("daemon-friendly")
    if tag_counter.get("vision-heavy"):
        project_tags.append("selector-asset-heavy")
    if tag_counter.get("parameterized") or overview["presets"]:
        project_tags.append("parameterized")
    if not project_tags:
        project_tags.append("general-purpose")

    product_lanes = _product_lanes(
        project=project,
        overview=overview,
        project_tags=project_tags,
        macro_profiles=macro_profiles,
    )
    recommendations = _recommendations(
        project=project,
        macro_profiles=macro_profiles,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        capability_issues=capability_issues or [],
    )
    integration_targets = _integration_targets(
        project=project,
        overview=overview,
        project_tags=project_tags,
        macro_profiles=macro_profiles,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        capability_issues=capability_issues or [],
    )
    next_steps = _next_steps(
        project=project,
        project_tags=project_tags,
        macro_profiles=macro_profiles,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues or [],
    )
    playbooks = _implementation_playbooks(
        project=project,
        overview=overview,
        project_tags=project_tags,
        macro_profiles=macro_profiles,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues or [],
    )
    architecture_map = _architecture_map(
        project=project,
        overview=overview,
        project_tags=project_tags,
        macro_profiles=macro_profiles,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        capability_issues=capability_issues or [],
    )
    deployment_profiles = _deployment_profiles(
        project=project,
        overview=overview,
        project_tags=project_tags,
        macro_profiles=macro_profiles,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        capability_issues=capability_issues or [],
    )
    desktop_targets = _desktop_targets(
        project=project,
        overview=overview,
        project_tags=project_tags,
        macro_profiles=macro_profiles,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        capability_issues=capability_issues or [],
    )
    stack_profiles = _stack_profiles(
        deployment_profiles=deployment_profiles,
        desktop_targets=desktop_targets,
        overview=overview,
        capability_usage=capability_usage or {},
    )
    surface_choices = _surface_choices(
        project=project,
        overview=overview,
        project_tags=project_tags,
        macro_profiles=macro_profiles,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        capability_issues=capability_issues or [],
    )
    environment_diffs = _environment_diffs(
        project=project,
        overview=overview,
        project_tags=project_tags,
        macro_profiles=macro_profiles,
        capability_usage=capability_usage or {},
    )
    portability_gaps = _portability_gaps(environment_diffs)
    portability_playbooks = _portability_playbooks(project=project, portability_gaps=portability_gaps)
    performance_profile = _performance_profile(
        overview=overview,
        macro_profiles=macro_profiles,
    )
    toolchain_choices = _toolchain_choices(
        project=project,
        overview=overview,
        project_tags=project_tags,
        macro_profiles=macro_profiles,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        capability_issues=capability_issues or [],
    )
    capability_coverage = _capability_coverage(
        project=project,
        overview=overview,
        project_tags=project_tags,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        capability_issues=capability_issues or [],
        environment_diffs=environment_diffs,
        toolchain_choices=toolchain_choices,
    )
    verification_gates = _verification_gates(
        project=project,
        overview=overview,
        project_tags=project_tags,
        capability_coverage=capability_coverage,
        toolchain_choices=toolchain_choices,
    )
    reference_patterns = _reference_patterns(
        project=project,
        overview=overview,
        project_tags=project_tags,
        macro_profiles=macro_profiles,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        capability_issues=capability_issues or [],
    )
    implementation_waves = _implementation_waves(
        project=project,
        overview=overview,
        project_tags=project_tags,
        playbooks=playbooks,
        portability_playbooks=portability_playbooks,
        toolchain_choices=toolchain_choices,
        capability_coverage=capability_coverage,
        verification_gates=verification_gates,
        reference_patterns=reference_patterns,
    )
    artifact_blueprint = _artifact_blueprint(
        project=project,
        portability_playbooks=portability_playbooks,
        verification_gates=verification_gates,
        implementation_waves=implementation_waves,
        toolchain_choices=toolchain_choices,
        capability_coverage=capability_coverage,
    )
    deployable_surfaces = _deployable_surfaces(
        artifact_blueprint=artifact_blueprint,
        surface_choices=surface_choices,
        verification_gates=verification_gates,
        portability_playbooks=portability_playbooks,
    )
    setup_recipes = _setup_recipes(
        deployable_surfaces=deployable_surfaces,
        artifact_blueprint=artifact_blueprint,
        verification_gates=verification_gates,
        portability_playbooks=portability_playbooks,
    )
    runtime_seams = _runtime_seams(
        project=project,
        overview=overview,
        project_tags=project_tags,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        stack_profiles=stack_profiles,
        toolchain_choices=toolchain_choices,
        surface_choices=surface_choices,
    )
    host_requirements = _host_requirements(
        project=project,
        overview=overview,
        project_tags=project_tags,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        stack_profiles=stack_profiles,
        toolchain_choices=toolchain_choices,
        surface_choices=surface_choices,
    )
    input_lane_dossier = _input_lane_dossier(
        project=project,
        overview=overview,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        performance_profile=performance_profile,
        surface_choices=surface_choices,
        host_requirements=host_requirements,
    )
    activation_routes = _activation_routes(
        project=project,
        overview=overview,
        project_tags=project_tags,
        macro_profiles=macro_profiles,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        stack_profiles=stack_profiles,
        runtime_seams=runtime_seams,
        host_requirements=host_requirements,
        surface_choices=surface_choices,
    )
    macro_route_profiles = _macro_route_profiles(
        project=project,
        overview=overview,
        macro_profiles=macro_profiles,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        activation_routes=activation_routes,
    )
    macro_export_candidates = _macro_export_candidates(
        macro_route_profiles=macro_route_profiles,
    )
    route_portfolio = _route_portfolio(
        macro_route_profiles=macro_route_profiles,
    )
    export_promotion_plan = _export_promotion_plan(
        macro_export_candidates=macro_export_candidates,
    )
    promotion_input_lane_plan = _promotion_input_lane_plan(
        project=project,
        export_promotion_plan=export_promotion_plan,
        input_lane_dossier=input_lane_dossier,
    )
    promotion_activation_route_plan = _promotion_activation_route_plan(
        project=project,
        export_promotion_plan=export_promotion_plan,
        activation_routes=activation_routes,
    )
    promotion_operator_control_plan = _promotion_operator_control_plan(
        project=project,
        export_promotion_plan=export_promotion_plan,
        promotion_input_lane_plan=promotion_input_lane_plan,
        promotion_activation_route_plan=promotion_activation_route_plan,
    )
    promotion_recovery_plan = _promotion_recovery_plan(
        project=project,
        export_promotion_plan=export_promotion_plan,
        promotion_input_lane_plan=promotion_input_lane_plan,
        promotion_activation_route_plan=promotion_activation_route_plan,
        promotion_operator_control_plan=promotion_operator_control_plan,
    )
    promotion_verification_plan = _promotion_verification_plan(
        project=project,
        export_promotion_plan=export_promotion_plan,
        promotion_input_lane_plan=promotion_input_lane_plan,
        promotion_activation_route_plan=promotion_activation_route_plan,
        promotion_operator_control_plan=promotion_operator_control_plan,
        promotion_recovery_plan=promotion_recovery_plan,
        verification_gates=verification_gates,
    )
    promotion_verification_summary = _promotion_verification_summary(
        promotion_verification_plan=promotion_verification_plan,
    )
    promotion_performance_plan = _promotion_performance_plan(
        project=project,
        export_promotion_plan=export_promotion_plan,
        performance_profile=performance_profile,
        promotion_input_lane_plan=promotion_input_lane_plan,
        promotion_activation_route_plan=promotion_activation_route_plan,
        promotion_operator_control_plan=promotion_operator_control_plan,
        promotion_verification_plan=promotion_verification_plan,
    )
    promotion_performance_summary = _promotion_performance_summary(
        promotion_performance_plan=promotion_performance_plan,
    )
    promotion_dispatch_budget_plan = _promotion_dispatch_budget_plan(
        project=project,
        export_promotion_plan=export_promotion_plan,
        performance_profile=performance_profile,
        promotion_input_lane_plan=promotion_input_lane_plan,
        promotion_activation_route_plan=promotion_activation_route_plan,
        promotion_operator_control_plan=promotion_operator_control_plan,
        promotion_verification_plan=promotion_verification_plan,
        promotion_performance_plan=promotion_performance_plan,
    )
    promotion_dispatch_budget_summary = _promotion_dispatch_budget_summary(
        promotion_dispatch_budget_plan=promotion_dispatch_budget_plan,
    )
    promotion_authority_envelope_plan = _promotion_authority_envelope_plan(
        project=project,
        export_promotion_plan=export_promotion_plan,
        promotion_input_lane_plan=promotion_input_lane_plan,
        promotion_activation_route_plan=promotion_activation_route_plan,
        promotion_operator_control_plan=promotion_operator_control_plan,
        promotion_dispatch_budget_plan=promotion_dispatch_budget_plan,
    )
    promotion_authority_envelope_summary = _promotion_authority_envelope_summary(
        promotion_authority_envelope_plan=promotion_authority_envelope_plan,
    )
    promotion_waves = _promotion_waves(
        export_promotion_plan=export_promotion_plan,
        route_portfolio=route_portfolio,
    )
    promotion_readiness = _promotion_readiness(
        project=project,
        export_promotion_plan=export_promotion_plan,
        route_portfolio=route_portfolio,
        capability_matrix=capability_matrix,
    )
    promotion_readiness_summary = _promotion_readiness_summary(
        promotion_readiness=promotion_readiness,
    )
    promotion_gates = _promotion_gates(
        project=project,
        promotion_waves=promotion_waves,
        promotion_readiness=promotion_readiness,
        readiness_summary=promotion_readiness_summary,
    )
    promotion_gate_summary = _promotion_gate_summary(
        promotion_gates=promotion_gates,
    )
    promotion_backlog = _promotion_backlog(
        promotion_waves=promotion_waves,
        promotion_readiness=promotion_readiness,
        promotion_gates=promotion_gates,
    )
    promotion_backlog_summary = _promotion_backlog_summary(
        promotion_backlog=promotion_backlog,
    )
    promotion_evidence = _promotion_evidence(
        project=project,
        promotion_readiness=promotion_readiness,
        promotion_gates=promotion_gates,
    )
    promotion_evidence_summary = _promotion_evidence_summary(
        promotion_evidence=promotion_evidence,
    )
    planner_target_claims: list[dict[str, Any]] = []
    host_truth = dict(host_truth or {})
    portal_route_contract = dict(portal_route_contract or {})
    for item in sorted(environment_diffs, key=lambda row: (-int(row.get("score") or 0), str(row.get("title") or ""))):
        level = recommended_claim_level(item)
        row = {
            "target": str(item.get("id") or ""),
            "title": str(item.get("title") or item.get("id") or "environment"),
            "score": int(item.get("score") or 0),
            "fit": str(item.get("fit") or "unknown"),
            "recommended_level": level,
            "blocking_capabilities": [str(x) for x in list(item.get("blocking_capabilities") or []) if str(x)],
            "preferred_surface_ids": [str((surface or {}).get("id") or "") for surface in list(item.get("preferred_surfaces") or []) if isinstance(surface, Mapping) and str((surface or {}).get("id") or "")],
        }
        current_host_fit = claim_host_fit_for_target(
            str(row.get("target") or ""),
            title=str(row.get("title") or row.get("target") or "target"),
            host_summary=host_truth,
            portal_route_contract=portal_route_contract,
        )
        if current_host_fit:
            row["current_host_fit"] = current_host_fit
        planner_target_claims.append(row)
    planner_claim_review = claim_host_review_summary(planner_target_claims)
    planner_claim_witness = claim_host_witness_contract(
        planner_target_claims,
        portal_route_contract=portal_route_contract,
        host_truth=host_truth,
    )
    planner_evidence_lane: dict[str, Any] = {}
    from vhk.project.target_fit_contract import build_target_fit_contract_from_lane, select_target_lane

    planner_evidence_lane_fit: dict[str, Any] = {}
    if host_truth or portal_route_contract:
        try:
            project_root = Path(getattr(project, "root_dir", "."))
            selected_lane = select_target_lane(
                project_root,
                bundle_target_profile=evidence_lane_profile,
                capability_usage={str(k): [dict(x) for x in list(v or []) if isinstance(x, Mapping)] for k, v in dict(capability_usage or {}).items() if str(k)},
            )
        except Exception:
            selected_lane = {}
        if selected_lane:
            planner_evidence_lane = {
                "profile_id": str(selected_lane.get("profile_id") or ""),
                "title": str(selected_lane.get("title") or selected_lane.get("profile_id") or "target"),
                "release_level": str(selected_lane.get("release_level") or ""),
                "backend": str(selected_lane.get("backend") or ""),
                "desktop_family": str(selected_lane.get("desktop_family") or ""),
                "trigger_route_id": str(selected_lane.get("trigger_route_id") or ""),
                "overall_status": str(selected_lane.get("overall_status") or ""),
                "selection_source": "explicit" if evidence_lane_profile else "flagship-default",
                "requested_profile_id": str(evidence_lane_profile or "").strip() or None,
            }
            planner_evidence_lane_fit = build_target_fit_contract_from_lane(
                selected_lane,
                host_truth=host_truth,
                host_requirements=host_requirements,
                portal_route_contract=portal_route_contract,
            )
            if planner_evidence_lane_fit:
                planner_evidence_lane_fit["selection_source"] = "explicit" if evidence_lane_profile else "flagship-default"
                planner_evidence_lane_fit["requested_profile_id"] = str(evidence_lane_profile or "").strip() or None
    ecosystem_lessons = _ecosystem_lessons(
        project=project,
        overview=overview,
        project_tags=project_tags,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        stack_profiles=stack_profiles,
        runtime_seams=runtime_seams,
    )

    return {
        "project": {
            "name": getattr(project, "name", None),
            "root_dir": getattr(project, "root_dir", None),
            "desktop_backend": getattr(getattr(project, "settings", None), "desktop_backend", None),
        },
        "overview": overview,
        "project_tags": project_tags,
        "macro_tag_counts": dict(tag_counter),
        "macro_profiles": macro_profiles,
        "performance_profile": performance_profile,
        "window_contract": window_contract,
        "product_lanes": product_lanes,
        "capability_usage": capability_usage,
        "session_capabilities": capability_matrix,
        "session_issues": capability_issues,
        "recommendations": recommendations,
        "integration_targets": integration_targets,
        "next_steps": next_steps,
        "playbooks": playbooks,
        "architecture_map": architecture_map,
        "deployment_profiles": deployment_profiles,
        "stack_profiles": stack_profiles,
        "desktop_targets": desktop_targets,
        "surface_choices": surface_choices,
        "environment_diffs": environment_diffs,
        "portability_gaps": portability_gaps,
        "portability_playbooks": portability_playbooks,
        "toolchain_choices": toolchain_choices,
        "capability_coverage": capability_coverage,
        "verification_gates": verification_gates,
        "reference_patterns": reference_patterns,
        "implementation_waves": implementation_waves,
        "artifact_blueprint": artifact_blueprint,
        "deployable_surfaces": deployable_surfaces,
        "setup_recipes": setup_recipes,
        "runtime_seams": runtime_seams,
        "host_requirements": host_requirements,
        "input_lane_dossier": input_lane_dossier,
        "activation_routes": activation_routes,
        "macro_route_profiles": macro_route_profiles,
        "macro_export_candidates": macro_export_candidates,
        "route_portfolio": route_portfolio,
        "export_promotion_plan": export_promotion_plan,
        "promotion_input_lane_plan": promotion_input_lane_plan,
        "promotion_activation_route_plan": promotion_activation_route_plan,
        "promotion_operator_control_plan": promotion_operator_control_plan,
        "promotion_recovery_plan": promotion_recovery_plan,
        "promotion_verification_plan": promotion_verification_plan,
        "promotion_verification_summary": promotion_verification_summary,
        "promotion_performance_plan": promotion_performance_plan,
        "promotion_performance_summary": promotion_performance_summary,
        "promotion_dispatch_budget_plan": promotion_dispatch_budget_plan,
        "promotion_dispatch_budget_summary": promotion_dispatch_budget_summary,
        "promotion_authority_envelope_plan": promotion_authority_envelope_plan,
        "promotion_authority_envelope_summary": promotion_authority_envelope_summary,
        "promotion_waves": promotion_waves,
        "promotion_readiness": promotion_readiness,
        "promotion_readiness_summary": promotion_readiness_summary,
        "promotion_gates": promotion_gates,
        "promotion_gate_summary": promotion_gate_summary,
        "promotion_backlog": promotion_backlog,
        "promotion_backlog_summary": promotion_backlog_summary,
        "promotion_evidence": promotion_evidence,
        "promotion_evidence_summary": promotion_evidence_summary,
        "host_truth": host_truth,
        "portal_route_contract": portal_route_contract,
        "planner_target_claims": planner_target_claims,
        "planner_claim_review": planner_claim_review if int(planner_claim_review.get("claims_with_current_host_review") or 0) > 0 else {},
        "planner_claim_witness": planner_claim_witness,
        "planner_evidence_lane": planner_evidence_lane,
        "planner_evidence_lane_fit": planner_evidence_lane_fit,
        "ecosystem_lessons": ecosystem_lessons,
    }
