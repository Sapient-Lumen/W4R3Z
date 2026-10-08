from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field


class Region(BaseModel):
    """A rectangular region in pixels."""

    x: int
    y: int
    w: int
    h: int


class StepBase(BaseModel):
    """Common step fields.

    Notes
    -----
    VHK is intended to grow toward an "AHK feel" where waiting/retry/diagnostics are
    ubiquitous. The base now includes lightweight retry/continue knobs so users do
    not need to hand-build retry loops around every flaky desktop action.
    """

    type: str
    enabled: bool = True
    comment: str | None = None

    # Common PMC-style knobs.
    delay_ms: int = 0
    repeat: int = 1

    # Robot-Framework-ish reliability knobs.
    retry_count: int = 0
    retry_delay_ms: int = 0
    retry_backoff: float = 1.0
    continue_on_error: bool = False


class StepDelay(StepBase):
    type: Literal["Delay"] = "Delay"
    ms: int | str = 0


class StepRandomWait(StepBase):
    """Wait a random duration (helps avoid brittle timing + detection heuristics)."""

    type: Literal["RandomWait"] = "RandomWait"
    min_ms: int | str
    max_ms: int | str


class StepLog(StepBase):
    type: Literal["Log"] = "Log"
    message: str


class StepSetVar(StepBase):
    type: Literal["SetVar"] = "SetVar"
    name: str
    value: Any


class StepRunShell(StepBase):
    type: Literal["RunShell"] = "RunShell"
    command: str
    check: bool = True


class StepIf(StepBase):
    type: Literal["If"] = "If"
    condition: str
    then_steps: list["Step"] = Field(default_factory=list)
    else_steps: list["Step"] = Field(default_factory=list)


class StepWhile(StepBase):
    """Top-tested loop with a safety iteration cap."""

    type: Literal["While"] = "While"
    condition: str
    steps: list["Step"] = Field(default_factory=list)
    max_iterations: int = 1000
    out_iterations: str = "while_iterations"


class StepTry(StepBase):
    """Run steps with optional catch/finally blocks."""

    type: Literal["Try"] = "Try"
    steps: list["Step"] = Field(default_factory=list)
    catch_steps: list["Step"] = Field(default_factory=list)
    finally_steps: list["Step"] = Field(default_factory=list)
    catch_pattern: str | None = None
    out_error: str = "last_error"


class StepBreak(StepBase):
    type: Literal["Break"] = "Break"


class StepContinue(StepBase):
    type: Literal["Continue"] = "Continue"


class StepReturn(StepBase):
    type: Literal["Return"] = "Return"
    value_expr: str | None = None
    out_var: str = "return_value"


# --- Vision (file-based MVP) -------------------------------------------------


class StepImageSearchFile(StepBase):
    type: Literal["ImageSearchFile"] = "ImageSearchFile"
    haystack_path: str
    needle_path: str
    region: Region | None = None
    threshold: float = 0.8
    out_x: str = "match_x"
    out_y: str = "match_y"
    out_score: str = "match_score"


class StepWaitForImageFile(StepBase):
    """Wait until a template match meets the threshold.

    This is intentionally separate from ImageSearchFile because tooling in the wild
    (Macro Recorder, Sikuli, etc.) has learned that a dedicated "wait" primitive is
    both more reliable and lower-CPU than putting Find inside an IF loop.
    """

    type: Literal["WaitForImageFile"] = "WaitForImageFile"
    haystack_path: str
    needle_path: str
    region: Region | None = None
    threshold: float = 0.8

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30

    out_x: str = "match_x"
    out_y: str = "match_y"
    out_score: str = "match_score"


class StepPixelSearchFile(StepBase):
    """Find the closest pixel matching a target color in an image file."""

    type: Literal["PixelSearchFile"] = "PixelSearchFile"
    image_path: str
    color: str | list[int]
    region: Region | None = None
    tolerance: float = 0.0

    out_x: str = "px_x"
    out_y: str = "px_y"
    out_dist: str = "px_dist"


class StepWaitForPixelFile(StepBase):
    """Wait until a pixel matching a target color appears."""

    type: Literal["WaitForPixelFile"] = "WaitForPixelFile"
    image_path: str
    color: str | list[int]
    region: Region | None = None
    tolerance: float = 0.0

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30

    out_x: str = "px_x"
    out_y: str = "px_y"
    out_dist: str = "px_dist"


class StepOcrReadTextFile(StepBase):
    type: Literal["OcrReadTextFile"] = "OcrReadTextFile"
    image_path: str
    out_var: str = "ocr_text"
    lang: str = "eng"


class StepCaptureScreenshot(StepBase):
    """Capture a screenshot to a file (region optional)."""

    type: Literal["CaptureScreenshot"] = "CaptureScreenshot"
    path: str | None = None
    region: Region | None = None
    out_var: str = "screenshot_path"

# --- Vision (screen-capture convenience) -------------------------------------


class StepImageSearch(StepBase):
    """Capture the screen (optionally a region) and search for a needle.

    This is a convenience wrapper around CaptureScreenshot + ImageSearchFile,
    mainly to enable waits/assertions without needing explicit loops.
    """

    type: Literal["ImageSearch"] = "ImageSearch"
    needle_path: str
    region: Region | None = None
    threshold: float = 0.8

    # If provided, VHK will write the capture here; otherwise it uses a file in
    # the run log directory.
    screenshot_path: str | None = None

    out_screenshot: str = "last_screenshot"
    out_x: str = "match_x"
    out_y: str = "match_y"
    out_score: str = "match_score"
    out_w: str = "match_w"
    out_h: str = "match_h"


class StepWaitForImage(StepBase):
    """Wait until a needle appears on the screen.

    Each poll captures a new screenshot, then runs template matching.
    """

    type: Literal["WaitForImage"] = "WaitForImage"
    needle_path: str
    region: Region | None = None
    threshold: float = 0.8

    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    out_x: str = "match_x"
    out_y: str = "match_y"
    out_score: str = "match_score"
    out_w: str = "match_w"
    out_h: str = "match_h"


class StepOcrReadText(StepBase):
    """Capture the screen (optionally a region) and OCR it."""

    type: Literal["OcrReadText"] = "OcrReadText"
    region: Region | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    out_var: str = "ocr_text"
    lang: str = "eng"


class StepWaitForText(StepBase):
    """Wait until OCR text matches a pattern (contains or regex)."""

    type: Literal["WaitForText"] = "WaitForText"
    region: Region | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    pattern: str
    match: Literal["contains", "regex"] = "contains"
    case_sensitive: bool = False
    lang: str = "eng"

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    out_text: str = "ocr_text"
    out_found: str = "text_found"


class StepAssertText(StepBase):
    """Assert that OCR text matches a pattern (contains or regex)."""

    type: Literal["AssertText"] = "AssertText"
    region: Region | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    pattern: str
    match: Literal["contains", "regex"] = "contains"
    case_sensitive: bool = False
    lang: str = "eng"

    out_text: str = "ocr_text"




class StepVisualAssert(StepBase):
    """Compare a captured region/screen against a baseline image.

    This is intentionally strict and explainable: same-size compare with optional
    openQA-style match/exclude areas from the baseline sidecar JSON.
    """

    type: Literal["VisualAssert"] = "VisualAssert"
    baseline_path: str
    region: Region | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    color_tolerance: int = 0
    max_changed_pixels: int | None = 0
    max_change_ratio: float = 0.0

    out_ok: str = "visual_ok"
    out_changed_pixels: str = "changed_pixels"
    out_total_pixels: str = "total_pixels"
    out_change_ratio: str = "change_ratio"
    out_max_channel_delta: str = "max_channel_delta"


class StepVisualVerify(StepBase):
    """Same as VisualAssert, but does not stop the macro on mismatch."""

    type: Literal["VisualVerify"] = "VisualVerify"
    baseline_path: str
    region: Region | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    color_tolerance: int = 0
    max_changed_pixels: int | None = 0
    max_change_ratio: float = 0.0

    out_ok: str = "visual_ok"
    out_changed_pixels: str = "changed_pixels"
    out_total_pixels: str = "total_pixels"
    out_change_ratio: str = "change_ratio"
    out_max_channel_delta: str = "max_channel_delta"


class StepWaitForRegionChange(StepBase):
    """Wait until a captured region changes relative to a baseline.

    If baseline_path is omitted, the first capture becomes the baseline.
    """

    type: Literal["WaitForRegionChange"] = "WaitForRegionChange"
    baseline_path: str | None = None
    region: Region | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"
    out_baseline: str = "baseline_screenshot"

    color_tolerance: int = 0
    min_changed_pixels: int = 1
    min_change_ratio: float = 0.0

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    out_changed_pixels: str = "changed_pixels"
    out_total_pixels: str = "total_pixels"
    out_change_ratio: str = "change_ratio"
    out_max_channel_delta: str = "max_channel_delta"


class StepMouseClickAt(StepBase):
    """Move the mouse to (x,y) and click."""

    type: Literal["MouseClickAt"] = "MouseClickAt"
    x: int | str
    y: int | str
    button: int | str = 1
    clearmodifiers: bool = False


class StepClickNeedle(StepBase):
    """Wait for a needle, then click it (openQA-ish).

    If the needle has openQA-style metadata (.json next to the .png), VHK will
    prefer a defined click point. Click point coordinates are relative to the
    match area they belong to.
    """

    type: Literal["ClickNeedle"] = "ClickNeedle"
    needle_path: str
    region: Region | None = None
    threshold: float = 0.8

    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    button: int | str = 1
    clearmodifiers: bool = False
    click_point_id: str | None = None
    offset_x: int | str = 0
    offset_y: int | str = 0

    out_match_x: str = "match_x"
    out_match_y: str = "match_y"
    out_match_score: str = "match_score"
    out_match_w: str = "match_w"
    out_match_h: str = "match_h"

    out_click_x: str = "click_x"
    out_click_y: str = "click_y"



# --- Input (X11 backend; currently xdotool) ---------------------------------


class StepKey(StepBase):
    """Send a key chord (e.g. "ctrl+l" or "Alt_L+Tab")."""

    type: Literal["Key"] = "Key"
    keys: str
    clearmodifiers: bool = False


class StepKeyDown(StepBase):
    type: Literal["KeyDown"] = "KeyDown"
    key: str
    clearmodifiers: bool = False


class StepKeyUp(StepBase):
    type: Literal["KeyUp"] = "KeyUp"
    key: str
    clearmodifiers: bool = False


class StepResetModifiers(StepBase):
    type: Literal["ResetModifiers"] = "ResetModifiers"


class StepTypeText(StepBase):
    type: Literal["TypeText"] = "TypeText"
    text: str
    delay_ms_per_char: int = 0
    clearmodifiers: bool = False

    # Practical text-injection modes inspired by tools like AutoKey:
    # - native: backend keyboard typing (xdotool / wtype / ydotool)
    # - clipboard: set clipboard then paste via a shortcut
    # - xvkbd: X11-only fallback that can feed text from a file/stdin
    # - auto: choose a sane default based on profile + available helpers
    backend: Literal["auto", "native", "clipboard", "xvkbd"] = "auto"
    selection: Literal["clipboard", "primary"] = "clipboard"
    preserve_clipboard: bool = True
    paste_shortcut: Literal["auto", "ctrl+v", "ctrl+shift+v", "shift+insert"] = "auto"


class StepMouseMove(StepBase):
    type: Literal["MouseMove"] = "MouseMove"
    x: int | str | None = None
    y: int | str | None = None
    dx: int | str | None = None
    dy: int | str | None = None
    relative: bool = False


class StepMouseClick(StepBase):
    type: Literal["MouseClick"] = "MouseClick"
    button: int | str = 1
    down: bool = False
    up: bool = False
    clearmodifiers: bool = False


class StepMouseDrag(StepBase):
    type: Literal["MouseDrag"] = "MouseDrag"
    x1: int | str
    y1: int | str
    x2: int | str
    y2: int | str
    button: int | str = 1
    clearmodifiers: bool = False


class StepMouseWheel(StepBase):
    type: Literal["MouseWheel"] = "MouseWheel"
    clicks: int | str = 1
    axis: Literal["vertical", "horizontal"] = "vertical"


class StepCursorHide(StepBase):
    type: Literal["CursorHide"] = "CursorHide"


class StepCursorShow(StepBase):
    type: Literal["CursorShow"] = "CursorShow"


# --- Desktop/system helpers --------------------------------------------------


class StepNotify(StepBase):
    type: Literal["Notify"] = "Notify"
    summary: str
    body: str | None = None
    urgency: Literal["low", "normal", "critical"] = "normal"


class StepClipboardRead(StepBase):
    type: Literal["ClipboardRead"] = "ClipboardRead"
    selection: Literal["clipboard", "primary"] = "clipboard"
    out_var: str = "clipboard_text"


class StepClipboardSet(StepBase):
    type: Literal["ClipboardSet"] = "ClipboardSet"
    text: str
    selection: Literal["clipboard", "primary"] = "clipboard"


class StepWaitForClipboardChange(StepBase):
    """Wait until clipboard contents differ from the initial snapshot."""

    type: Literal["WaitForClipboardChange"] = "WaitForClipboardChange"
    selection: Literal["clipboard", "primary"] = "clipboard"
    initial_text: str | None = None

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    out_text: str = "clipboard_text"
    out_changed: str = "clipboard_changed"


class StepPasteClipboard(StepBase):
    type: Literal["PasteClipboard"] = "PasteClipboard"
    selection: Literal["clipboard", "primary"] = "clipboard"
    clearmodifiers: bool = False


class StepOpenUrl(StepBase):
    type: Literal["OpenUrl"] = "OpenUrl"
    url: str


class StepComposeEmail(StepBase):
    type: Literal["ComposeEmail"] = "ComposeEmail"
    to: str | list[str]
    cc: str | list[str] | None = None
    bcc: str | list[str] | None = None
    subject: str | None = None
    body: str | None = None
    attachments: str | list[str] | None = None
    utf8: bool = True


class StepHttpRequest(StepBase):
    type: Literal["HttpRequest"] = "HttpRequest"
    method: str = "GET"
    url: str
    headers: dict[str, Any] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    body: str | None = None
    json_expr: str | None = None
    timeout_ms: int = 30_000
    allow_error_status: bool = False
    out_status: str = "http_status"
    out_reason: str = "http_reason"
    out_headers: str = "http_headers"
    out_text: str = "http_text"
    out_json: str | None = None
    out_url: str = "http_url"


class StepDownloadFile(StepBase):
    type: Literal["DownloadFile"] = "DownloadFile"
    url: str
    path: str
    headers: dict[str, Any] = Field(default_factory=dict)
    timeout_ms: int = 30_000
    create_parents: bool = True
    overwrite: bool = True
    out_path: str = "download_path"
    out_bytes: str = "download_bytes"


class StepShowMessage(StepBase):
    type: Literal["ShowMessage"] = "ShowMessage"
    text: str
    title: str | None = None
    level: Literal["info", "warning", "error"] = "info"


class StepAskYesNo(StepBase):
    type: Literal["AskYesNo"] = "AskYesNo"
    text: str
    title: str | None = None
    default_yes: bool = True
    out_var: str = "answer"


class StepInputBox(StepBase):
    type: Literal["InputBox"] = "InputBox"
    prompt: str
    title: str | None = None
    default: str | None = None
    password: bool = False
    out_var: str = "input_text"


class StepChooseFromList(StepBase):
    type: Literal["ChooseFromList"] = "ChooseFromList"
    items_expr: str
    title: str | None = None
    text: str | None = None
    multiple: bool = False
    out_var: str = "selection"


class StepStartProcess(StepBase):
    type: Literal["StartProcess"] = "StartProcess"
    command: str | list[str]
    shell: bool = False
    cwd: str | None = None
    env: dict[str, Any] = Field(default_factory=dict)
    out_pid: str = "process_pid"


class StepWaitForProcessExit(StepBase):
    type: Literal["WaitForProcessExit"] = "WaitForProcessExit"
    pid: int | str
    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    out_returncode: str = "process_returncode"
    out_exited: str = "process_exited"


class StepKillProcess(StepBase):
    type: Literal["KillProcess"] = "KillProcess"
    pid: int | str
    signal: str | int = "TERM"
    missing_ok: bool = True
    wait_ms: int = 0
    out_killed: str = "process_killed"


# --- Filesystem --------------------------------------------------------------




class StepRegexReplace(StepBase):
    type: Literal["RegexReplace"] = "RegexReplace"
    text: str
    pattern: str
    replacement: str
    flags: list[Literal["IGNORECASE", "MULTILINE", "DOTALL"]] = Field(default_factory=list)
    count: int = 0
    out_var: str = "text"


class StepTrimText(StepBase):
    type: Literal["TrimText"] = "TrimText"
    text: str
    chars: str | None = None
    mode: Literal["both", "left", "right"] = "both"
    out_var: str = "text"


class StepSplitText(StepBase):
    type: Literal["SplitText"] = "SplitText"
    text: str
    sep: str | None = None
    maxsplit: int = -1
    out_var: str = "parts"


class StepJoinText(StepBase):
    type: Literal["JoinText"] = "JoinText"
    items_expr: str
    sep: str = ""
    out_var: str = "text"


class StepForEach(StepBase):
    """Iterate over a list/tuple/dict and run child steps for each item."""

    type: Literal["ForEach"] = "ForEach"
    items_expr: str
    item_var: str = "item"
    index_var: str | None = "item_index"
    key_var: str | None = None
    steps: list["Step"] = Field(default_factory=list)


class StepReadCsv(StepBase):
    type: Literal["ReadCsv"] = "ReadCsv"
    path: str
    encoding: str = "utf-8"
    delimiter: str = ","
    has_header: bool = True
    out_var: str = "rows"
    out_row_count: str = "row_count"


class StepWriteCsv(StepBase):
    type: Literal["WriteCsv"] = "WriteCsv"
    path: str
    rows_expr: str
    encoding: str = "utf-8"
    delimiter: str = ","
    create_parents: bool = True
    append: bool = False
    include_header: bool = True
    fieldnames: list[str] | None = None


class StepReadJson(StepBase):
    type: Literal["ReadJson"] = "ReadJson"
    path: str
    encoding: str = "utf-8"
    out_var: str = "json_data"


class StepWriteJson(StepBase):
    type: Literal["WriteJson"] = "WriteJson"
    path: str
    value_expr: str
    encoding: str = "utf-8"
    indent: int = 2
    create_parents: bool = True


class StepReadFile(StepBase):
    type: Literal["ReadFile"] = "ReadFile"
    path: str
    encoding: str = "utf-8"
    out_var: str = "file_text"


class StepWriteFile(StepBase):
    type: Literal["WriteFile"] = "WriteFile"
    path: str
    text: str
    encoding: str = "utf-8"
    create_parents: bool = True


class StepAppendFile(StepBase):
    type: Literal["AppendFile"] = "AppendFile"
    path: str
    text: str
    encoding: str = "utf-8"
    create_parents: bool = True


class StepListDirectory(StepBase):
    type: Literal["ListDirectory"] = "ListDirectory"
    path: str
    pattern: str | None = None
    recursive: bool = False
    files_only: bool = False
    dirs_only: bool = False
    sort: Literal["name", "mtime"] = "name"
    out_var: str = "dir_entries"


class StepWaitForFile(StepBase):
    """Wait until a file exists, disappears, or changes."""

    type: Literal["WaitForFile"] = "WaitForFile"
    path: str
    condition: Literal["exists", "missing", "changed"] = "exists"

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    out_path: str = "file_path"
    out_exists: str = "file_exists"
    out_mtime_ns: str = "file_mtime_ns"
    out_size: str = "file_size"


class StepWaitForNewFile(StepBase):
    """Wait until a new file matching the pattern appears in a directory."""

    type: Literal["WaitForNewFile"] = "WaitForNewFile"
    directory: str
    pattern: str = "*"

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    out_path: str = "new_file_path"
    out_name: str = "new_file_name"
    out_size: str = "new_file_size"


# --- i3 IPC -----------------------------------------------------------------


class I3WindowSelector(BaseModel):
    """A minimal selector for an i3 tree node/window."""

    # sway uses app_id for native Wayland windows (xdg-shell). i3 won't set it.
    app_id: str | None = None
    app_id_regex: bool = False

    title: str | None = None
    title_regex: bool = False

    wm_class: str | None = Field(default=None, alias="class")
    instance: str | None = None

    urgent: bool | None = None
    focused: bool | None = None
    workspace: str | None = None


class StepI3Command(StepBase):
    type: Literal["I3Command"] = "I3Command"
    command: str
    out_var: str | None = None


class StepI3GetTree(StepBase):
    type: Literal["I3GetTree"] = "I3GetTree"
    out_var: str = "i3_tree"


class StepI3GetWorkspaces(StepBase):
    type: Literal["I3GetWorkspaces"] = "I3GetWorkspaces"
    out_var: str = "i3_workspaces"


class StepWaitForWindow(StepBase):
    """Wait for an i3 window/container that matches selector."""

    type: Literal["WaitForWindow"] = "WaitForWindow"
    selector: I3WindowSelector

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30

    out_var: str = "i3_window"
    out_con_id: str = "i3_con_id"

    focus: bool = False


class StepFocusWindow(StepBase):
    """Focus the first window matching selector."""

    type: Literal["FocusWindow"] = "FocusWindow"
    selector: I3WindowSelector


# --- Macro composition --------------------------------------------------------


class StepCallMacro(StepBase):
    """Call another macro in the same project.

    args: values are rendered (interpolated) in the parent context and passed into
          the child context.
    returns: mapping of child variable names to parent variable names.
    """

    type: Literal["CallMacro"] = "CallMacro"
    macro: str
    args: dict[str, Any] = Field(default_factory=dict)
    returns: dict[str, str] = Field(default_factory=dict)


Step = Annotated[
    Union[
        StepDelay,
        StepRandomWait,
        StepLog,
        StepSetVar,
        StepRunShell,
        StepIf,
        StepWhile,
        StepTry,
        StepBreak,
        StepContinue,
        StepReturn,
        StepImageSearchFile,
        StepWaitForImageFile,
        StepPixelSearchFile,
        StepWaitForPixelFile,
        StepOcrReadTextFile,
        StepCaptureScreenshot,
        StepImageSearch,
        StepWaitForImage,
        StepVisualAssert,
        StepVisualVerify,
        StepWaitForRegionChange,
        StepOcrReadText,
        StepWaitForText,
        StepAssertText,
        StepClickNeedle,
        StepKey,
        StepKeyDown,
        StepKeyUp,
        StepResetModifiers,
        StepTypeText,
        StepMouseMove,
        StepMouseClick,
        StepMouseDrag,
        StepMouseWheel,
        StepCursorHide,
        StepCursorShow,
        StepMouseClickAt,
        StepNotify,
        StepClipboardRead,
        StepClipboardSet,
        StepWaitForClipboardChange,
        StepPasteClipboard,
        StepOpenUrl,
        StepComposeEmail,
        StepHttpRequest,
        StepDownloadFile,
        StepShowMessage,
        StepAskYesNo,
        StepInputBox,
        StepChooseFromList,
        StepStartProcess,
        StepWaitForProcessExit,
        StepKillProcess,
        StepRegexReplace,
        StepTrimText,
        StepSplitText,
        StepJoinText,
        StepForEach,
        StepReadCsv,
        StepWriteCsv,
        StepReadJson,
        StepWriteJson,
        StepReadFile,
        StepWriteFile,
        StepAppendFile,
        StepListDirectory,
        StepWaitForFile,
        StepWaitForNewFile,
        StepI3Command,
        StepI3GetTree,
        StepI3GetWorkspaces,
        StepWaitForWindow,
        StepFocusWindow,
        StepCallMacro,
    ],
    Field(discriminator="type"),
]


class Macro(BaseModel):
    name: str
    steps: list[Step]


class HotkeyBinding(BaseModel):
    """A project-level hotkey mapping (for i3 config generation)."""

    keys: str
    macro: str
    description: str | None = None
    vars: dict[str, Any] = Field(default_factory=dict)

    # Optional i3 "criteria" (context) for bindsym.
    # When set, the hotkey triggers only when the focused window matches.
    when: I3WindowSelector | None = None


class ClipboardWatcher(BaseModel):
    """Project-level clipboard rule that triggers a macro on clipboard changes."""

    name: str
    macro: str
    enabled: bool = True
    selection: Literal["clipboard", "primary"] = "clipboard"
    pattern: str | None = None
    flags: list[Literal["IGNORECASE", "MULTILINE", "DOTALL"]] = Field(default_factory=list)
    debounce_ms: int = 150
    dedupe: bool = True
    continue_on_macro_error: bool = True
    vars: dict[str, Any] = Field(default_factory=dict)


class ProjectSettings(BaseModel):
    """Project defaults that influence the runner."""

    # Which desktop stack to target.
    # - auto: infer from XDG_SESSION_TYPE / WAYLAND_DISPLAY.
    # - x11: use X11 tooling (xdotool/maim/xclip).
    # - wayland: use Wayland tooling (grim/slurp/wl-clipboard/wtype/ydotool).
    desktop_backend: Literal["auto", "x11", "wayland"] = "auto"

    # A light-weight playback profile. "turbo" is intentionally simple:
    # keep waits/assertions intact, but reduce incidental delays and prefer
    # clipboard-paste text entry for larger printable payloads.
    runner_profile: Literal["normal", "turbo"] = "normal"
    turbo_delay_scale: float = 0.25
    turbo_type_clipboard_threshold: int = 80

    log_dir: str = "logs"
    event_log: bool = True
    screenshot_on_error: bool = False
    trace_wait_attempts: bool = True
    panic_file: str = "/tmp/vhk_panic"
    hide_cursor_during_run: bool = False

    # When enabled, VHK will not run external side-effects (shell, input, notify).
    dry_run: bool = False


class Project(BaseModel):
    name: str
    macros: dict[str, Macro]
    root_dir: str
    bindings: list[HotkeyBinding] = Field(default_factory=list)
    clipboard_watchers: list[ClipboardWatcher] = Field(default_factory=list)
    settings: ProjectSettings = Field(default_factory=ProjectSettings)


# Resolve forward references
StepIf.model_rebuild()
StepWhile.model_rebuild()
StepTry.model_rebuild()
StepForEach.model_rebuild()
