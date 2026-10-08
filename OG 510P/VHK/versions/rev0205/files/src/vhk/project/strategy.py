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
import shlex
from typing import Any
from types import SimpleNamespace

from vhk.project.window_contracts import summarize_project_window_contract

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
        if step_type == "Delay":
            try:
                ms = int(getattr(step, "ms", 0) or 0)
            except Exception:
                ms = 0
            if ms >= 1500:
                issues["long_delay"] += 1
        if step_type == "MouseClickAt":
            issues["coord_click"] += 1
        if step_type in {"KeyDown", "KeyUp"}:
            issues["raw_key_events"] += 1

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
    raw_key_events = sum(int((m.get("smells") or {}).get("raw_key_events") or 0) for m in macro_profiles)
    watcher_count = int(overview.get("bus_watchers") or 0) + int(overview.get("clipboard_watchers") or 0) + int(overview.get("file_watchers") or 0) + int(overview.get("window_watchers") or 0)

    hotkeys = capability_matrix.get("global_hotkeys") if isinstance(capability_matrix, Mapping) else None
    hotkey_status = str(hotkeys.get("status") or "unknown") if isinstance(hotkeys, Mapping) else "unknown"
    pointer = capability_matrix.get("pointer_injection") if isinstance(capability_matrix, Mapping) else None
    pointer_status = str(pointer.get("status") or "unknown") if isinstance(pointer, Mapping) else "unknown"
    text = capability_matrix.get("text_injection") if isinstance(capability_matrix, Mapping) else None
    text_status = str(text.get("status") or "unknown") if isinstance(text, Mapping) else "unknown"

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
            "Use this when the target environment really supports portal-managed shortcut sessions and you want an explicit permission/session lifecycle instead of assuming raw global hooks. Treat it as capability-aware trigger routing, not a generic Linux hotkey checkbox.",
            strengths="Best fit for desktops where explicit portal sessions are the intended integration surface.",
            tradeoffs="Availability and behavior vary by desktop/backend, so this needs doctor/validate discipline instead of blanket promises.",
            commands=[
                "vhk doctor --json",
                f"vhk validate {root_q} --json",
                f"vhk plan-project {root_q} --json",
            ],
            learn_from=["portal session lifecycle", "per-interface routing", "capability-aware hotkeys"],
            evidence=[f"global_hotkeys={hotkey_status}", f"desktop_backend={backend or 'unknown'}", f"{len(hotkey_usage)} hotkey step(s)"],
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
                    ["wmctrl", "xprop", "xwininfo"],
                    ["wmctrl", "xprop", "xwininfo"],
                    "Window-sensitive X11 projects benefit from stable, scriptable context tools that expose focus, titles, and geometry.",
                    "This model does not map cleanly to locked-down Wayland desktops, so keep it behind an adapter seam.",
                    ["vhk doctor --json", f"vhk window-spy --project {root_q} --json --no-check"],
                    ["wmctrl/xprop", "X11 window metadata"],
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
                "wtype",
                ["wtype", "clipboard", "dotool", "ydotool"],
                ["wtype", "wl-clipboard", "dotool", "ydotool"],
                "For Wayland-class projects, keep the fast path on virtual-keyboard or clipboard-friendly text injection instead of forcing every snippet through pointer automation.",
                "Virtual-keyboard support varies by compositor, so keep clipboard or uinput-style fallbacks available.",
                [f"vhk validate {root_q} --json", f"vhk gen-espanso {root_q} --package-dir ./build/espanso_package"],
                ["wtype", "clipboard fallback", "text-first deployment"],
            ),
            "pointer_injection": (
                "helper/uinput seam",
                ["portal:RemoteDesktop(pointer)", "dotool", "ydotool", "libei-ready helper"],
                ["ydotool", "dotool", "xdg-desktop-portal"],
                "On Wayland, pointer automation should stay behind a helper boundary so VHK can adapt to portal consent flows, compositor-native paths, or uinput helpers.",
                "This is the least portable surface in the Linux desktop stack today; do not design the whole product around it by accident.",
                ["vhk doctor --json", f"vhk validate {root_q} --json", f"vhk plan-project {root_q} --json"],
                ["ydotool/dotool", "portal RemoteDesktop", "helper boundary"],
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
                ["hyprctl", "swaymsg", "kdotool", "shell metadata bridge"],
                ["hyprland", "sway/i3 IPC", "kdotool"],
                "Window-aware Wayland projects should treat context lookup as a desktop-specific metadata bridge rather than a universal primitive.",
                "Desktop-specific metadata can be excellent locally but should stay behind a contract so projects remain portable.",
                ["vhk doctor --json", f"vhk window-spy --project {root_q} --json --no-check"],
                ["hyprctl/swaymsg/kdotool", "desktop-shaped context"],
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

    vision_macros = [m for m in macro_profiles if "vision-heavy" in (m.get("tags") or [])]
    text_macros = [m for m in macro_profiles if "text-expander" in (m.get("tags") or [])]
    parameterized_macros = [m for m in macro_profiles if "parameterized" in (m.get("tags") or [])]
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
    capture_usage = list(capability_usage.get("screen_capture") or [])
    hotkey_usage = list(capability_usage.get("global_hotkeys") or [])
    capability_blockers = {str(item.get("capability") or "") for item in capability_issues if str(item.get("capability") or "")}

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
        elif artifact_id in {"keyd-config", "kanata-config", "kmonad-config", "remap-config"}:
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
        artifact_ids=('keyd-config', 'kanata-config', 'kmonad-config', 'remap-config'),
        surface_ids=('keyd-remap', 'kanata-remap'),
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
    needs_remapper = bool(surface_ids.intersection({'keyd-remap', 'kanata-remap', 'kmonad-remap'})) or 'remap-integrated' in profile_ids or any(token in tool_tokens for token in {'keyd', 'kanata', 'kmonad', 'xremap', 'helper/uinput seam'})
    needs_uinput = backend != 'x11' and (needs_remapper or bool(pointer_usage) or any(token in tool_tokens for token in {'ydotool', 'dotool', 'helper/uinput seam', 'libei-ready helper'}))
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
        add(
            'remapper-lifecycle',
            'Remapper lifecycle and placement',
            requirement_type='service',
            priority='recommended',
            capability='global_hotkeys',
            applies_when='The project wants fast tap-hold layers or exported keyd/Kanata/KMonad-class trigger configs.',
            why='Low-latency remappers succeed by owning a narrow privileged edge. Their config placement, launch mode, and restart story are part of the install contract.',
            packages=[pkg for pkg in ['keyd', 'kanata', 'kmonad'] if pkg in tool_tokens or pkg in ''.join(tool_tokens)],
            services=['keyd', 'kanata', 'kmonad'],
            service_scope='system_or_dedicated_user',
            verify_commands=[f'vhk gen-keyd-config {root_q} --out ./build/vhk.keyd.conf', f'vhk gen-kanata-config {root_q} --out ./build/vhk.kanata.kbd', f'vhk gen-kmonad-config {root_q} --out ./build/vhk.kmonad.kbd'],
            fixup_hints=['Keep generated remapper configs separate from runtime-owned macro logic.', 'Review config placement, restart commands, and whether the target host expects a system daemon or a dedicated service user.'],
            risks=['Remapper installs are not just file generation; they need explicit lifecycle and permission review.'],
            evidence=[f'bindings={int(overview.get("bindings") or 0)}', ', '.join(sorted(surface_ids.intersection({'keyd-remap', 'kanata-remap', 'kmonad-remap'}))) or 'surface=none'],
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
    top_profile_ids = [str(item.get('id') or '').strip() for item in stack_profiles[:3] if str(item.get('id') or '').strip()]

    text_usage = list(capability_usage.get('text_injection') or [])
    pointer_usage = list(capability_usage.get('pointer_injection') or [])
    capture_usage = list(capability_usage.get('screen_capture') or [])
    hotkey_usage = list(capability_usage.get('global_hotkeys') or [])
    input_capture_usage = list(capability_usage.get('input_capture') or [])

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
        add(
            'portal-shortcuts-route',
            'Portal shortcut session route',
            activation_kind='portal_session',
            fit='conditional',
            startup_owner='portal session + desktop consent/configure flow',
            steady_state='session-bound',
            entrypoint='org.freedesktop.portal.GlobalShortcuts session + bindings',
            why='Portal-managed shortcuts are session objects, so VHK should treat them as an explicit route instead of assuming they behave like always-on in-process hooks.',
            commands=[f'vhk doctor --json', f'vhk gen-host-contract-pack {root_q} --quiet'],
            verification_commands=[f'vhk doctor --json', f'vhk validate {root_q} --json'],
            depends_on_requirements=['portal-global-shortcuts', 'portal-backend-config'],
            depends_on_seams=['trigger-surface'],
            related_surface_ids=['wm-trigger-layer', 'launcher-entrypoints'],
            fallback_routes=['native-trigger-route', 'launcher-entrypoint'],
            notes=['Keep a launcher or compositor-native fallback because portal availability and binding UX vary by desktop.'],
            evidence=[backend or 'backend=auto', f'global_hotkey_usage={len(hotkey_usage)}'],
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
            depends_on_requirements=['uinput-permissions', 'remapper-lifecycle'],
            depends_on_seams=['trigger-surface', 'helper-boundary'],
            related_surface_ids=['remap-helper-layer', 'wm-trigger-layer'],
            fallback_routes=['native-trigger-route', 'launcher-entrypoint'],
            notes=['Keep service-user, placement, and restart policy reviewable instead of pretending config generation is the whole deployment story.'],
            evidence=[f'bindings={int(overview.get("bindings") or 0)}', f'input_capture_usage={len(input_capture_usage)}'],
        )

    needs_helper_route = bool(pointer_usage or capture_usage or ('helper-boundary' in seam_ids and backend == 'wayland'))
    if needs_helper_route:
        reqs = ['uinput-permissions']
        if 'ydotool-daemon' in requirement_map:
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
            entrypoint='ydotoold / helper socket / portal-mediated injection fallback',
            why='Pointer and injected-input edges churn faster than macro logic, so the activation seam should stay narrow and replaceable.',
            commands=[f'vhk doctor --json', f'vhk gen-readiness-pack {root_q} --quiet'],
            verification_commands=[f'vhk doctor --json', f'vhk plan-project {root_q} --json'],
            depends_on_requirements=reqs,
            depends_on_seams=['runner-core', 'helper-boundary'],
            related_surface_ids=['remap-helper-layer', 'selector-debug-pack'],
            fallback_routes=['launcher-entrypoint'],
            notes=['Treat helper sockets, portal consent, and uinput access as host contract edges, not as runner internals.'],
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

    top_profile_ids = {str(item.get('id') or '') for item in stack_profiles[:3]}
    seam_ids = {str(item.get('id') or '') for item in runtime_seams}
    pointer_usage = list(capability_usage.get('pointer_injection') or [])
    text_usage = list(capability_usage.get('text_injection') or [])
    capture_usage = list(capability_usage.get('screen_capture') or [])

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
            commands=[f'vhk portal-hotkeys {root_q} --bind --listen'],
            related_profiles=[pid for pid in top_profile_ids if pid in {'wayland-helper-boundary', 'text-first-export'}],
            related_seams=['trigger-surface', 'helper-boundary'] if 'helper-boundary' in seam_ids else ['trigger-surface'],
            evidence=['Wayland session target'],
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


def summarize_project_strategy(
    project,
    *,
    capability_usage: Mapping[str, list[dict[str, object]]] | None = None,
    capability_matrix: Mapping[str, Any] | None = None,
    capability_issues: list[dict[str, Any]] | None = None,
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
    activation_routes = _activation_routes(
        project=project,
        overview=overview,
        project_tags=project_tags,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        stack_profiles=stack_profiles,
        runtime_seams=runtime_seams,
        host_requirements=host_requirements,
        surface_choices=surface_choices,
    )
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
        "activation_routes": activation_routes,
        "ecosystem_lessons": ecosystem_lessons,
    }
