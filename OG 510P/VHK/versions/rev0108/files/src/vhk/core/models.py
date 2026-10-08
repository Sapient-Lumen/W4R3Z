from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, ConfigDict, model_validator


class Region(BaseModel):
    """A rectangular region in pixels.

    Notes
    -----
    Many automation systems encourage users to define a *region of interest*
    (ROI) to make searches faster and more stable.

    - Sikuli's core concept is a Region object that scopes image/text search and
      change-observation.
    - Pulover's Macro Creator exposes "Image Search" regions and UX to adjust a
      capture/search rectangle with hotkeys.
    """

    x: int
    y: int
    w: int
    h: int


# A region can be provided inline (mapping) or as a string reference.
#
# String forms are interpreted at runtime:
#   - "@name" or "name" (if present in project.yaml regions)
#   - "WxH+X+Y" (e.g. 640x480+10+20) for quick copy/paste.
RegionSpec = Region | str


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
    retry_jitter: Literal["none", "full"] = "none"
    retry_jitter_ms: int = 0
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
    region: RegionSpec | None = None
    threshold: float = 0.8
    scales: list[float] | None = None
    out_x: str = "match_x"
    out_y: str = "match_y"
    out_score: str = "match_score"


class StepImageSearchAllFile(StepBase):
    """Find all needle matches in a haystack image file.

    Returns a list of dicts (JSON-serializable) so users can iterate with
    ForEach and persist results via WriteJson.
    """

    type: Literal["ImageSearchAllFile"] = "ImageSearchAllFile"
    haystack_path: str
    needle_path: str
    region: RegionSpec | None = None
    threshold: float = 0.8
    scales: list[float] | None = None
    max_results: Annotated[int, Field(ge=1)] = 50
    overlap_threshold: Annotated[float, Field(ge=0.0, le=1.0)] = 0.3
    sort: Literal["score", "scan"] = "score"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"

    out_matches: str = "matches"


class StepWaitForImageFile(StepBase):
    """Wait until a template match meets the threshold.

    This is intentionally separate from ImageSearchFile because tooling in the wild
    (Macro Recorder, Sikuli, etc.) has learned that a dedicated "wait" primitive is
    both more reliable and lower-CPU than putting Find inside an IF loop.
    """

    type: Literal["WaitForImageFile"] = "WaitForImageFile"
    haystack_path: str
    needle_path: str
    region: RegionSpec | None = None
    threshold: float = 0.8
    scales: list[float] | None = None

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30

    use_events: bool = True

    out_x: str = "match_x"
    out_y: str = "match_y"
    out_score: str = "match_score"


class StepPixelSearchFile(StepBase):
    """Find the closest pixel matching a target color in an image file."""

    type: Literal["PixelSearchFile"] = "PixelSearchFile"
    image_path: str
    color: str | list[int]
    region: RegionSpec | None = None
    tolerance: float = 0.0
    tolerance_mode: Literal["euclidean", "per_channel"] = "euclidean"
    step: Annotated[int, Field(ge=1)] = 1
    match_strategy: Literal["best", "first"] = "best"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"

    out_x: str = "px_x"
    out_y: str = "px_y"
    out_dist: str = "px_dist"


class StepPixelSearchAllFile(StepBase):
    """Find **all** pixels (or pixel blobs) matching a target color in an image file.

    This is VHK's pragmatic "FindAll" for colors.

    When ``group='connected'``, VHK collapses contiguous pixels into connected
    components and returns one representative point per blob.
    """

    type: Literal["PixelSearchAllFile"] = "PixelSearchAllFile"
    image_path: str
    color: str | list[int]
    region: RegionSpec | None = None
    tolerance: float = 0.0
    tolerance_mode: Literal["euclidean", "per_channel"] = "euclidean"
    step: Annotated[int, Field(ge=1)] = 1
    group: Literal["none", "connected"] = "none"
    pick: Literal["center", "first", "best"] = "center"
    min_area: Annotated[int, Field(ge=1)] = 1
    max_results: Annotated[int, Field(ge=1)] = 200
    sort: Literal["scan", "dist"] = "scan"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"

    out_matches: str = "px_matches"
    out_count: str = "px_match_count"


class StepWaitForPixelFile(StepBase):
    """Wait until a pixel matching a target color appears."""

    type: Literal["WaitForPixelFile"] = "WaitForPixelFile"
    image_path: str
    color: str | list[int]
    region: RegionSpec | None = None
    tolerance: float = 0.0
    tolerance_mode: Literal["euclidean", "per_channel"] = "euclidean"
    step: Annotated[int, Field(ge=1)] = 1
    match_strategy: Literal["best", "first"] = "best"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30

    out_x: str = "px_x"
    out_y: str = "px_y"
    out_dist: str = "px_dist"


class StepPixelGetColorFile(StepBase):
    """Sample the color of a pixel at (x,y) from an image file."""

    type: Literal["PixelGetColorFile"] = "PixelGetColorFile"
    image_path: str
    x: int
    y: int
    region: RegionSpec | None = None

    # Output formats are chosen to be convenient for reuse in later steps.
    out_hex: str = "px_color"
    out_ahk_hex: str = "px_color_ahk"
    out_r: str = "px_r"
    out_g: str = "px_g"
    out_b: str = "px_b"


class StepOcrReadTextFile(StepBase):
    """OCR an image file to text.

    Optional OCR tuning: preprocess/scale/psm/oem/tess_config.
    """

    type: Literal["OcrReadTextFile"] = "OcrReadTextFile"
    image_path: str
    region: RegionSpec | None = None

    out_var: str = "ocr_text"
    lang: str = "eng"
    preprocess: str | None = None
    scale: float | int | None = 1.0
    psm: int | None = None
    oem: int | None = None
    tess_config: str | None = None


class StepCaptureScreenshot(StepBase):
    """Capture a screenshot to a file (region optional)."""

    type: Literal["CaptureScreenshot"] = "CaptureScreenshot"
    path: str | None = None
    region: RegionSpec | None = None
    out_var: str = "screenshot_path"


# --- Coordinate modes --------------------------------------------------------


class StepCoordMode(StepBase):
    """Set coordinate mode for subsequent steps (AHK-style).

    Notes
    -----
    This is a pragmatic subset of AutoHotkey's CoordMode. Today VHK supports
    coordinate translation for:
      - pixel/image/screenshot regions (target="pixel")
      - mouse coordinates (target="mouse")

    "screen" means absolute screen coordinates.
    "window" means coordinates relative to the active window's outer rect.
    "client" means coordinates relative to the active window's client rect.

    On i3/sway, "client" uses `window_rect` (relative to `rect`).
    """

    type: Literal["CoordMode"] = "CoordMode"
    target: Literal["pixel", "mouse"] = "pixel"
    mode: Literal["screen", "window", "client"] = "screen"

# --- Vision (screen-capture convenience) -------------------------------------


class StepImageSearch(StepBase):
    """Capture the screen (optionally a region) and search for a needle.

    This is a convenience wrapper around CaptureScreenshot + ImageSearchFile,
    mainly to enable waits/assertions without needing explicit loops.
    """

    type: Literal["ImageSearch"] = "ImageSearch"
    needle_path: str
    region: RegionSpec | None = None
    threshold: float = 0.8
    scales: list[float] | None = None

    # If provided, VHK will write the capture here; otherwise it uses a file in
    # the run log directory.
    screenshot_path: str | None = None

    # Optional cursor hygiene before screen capture.
    # - none: don't touch the cursor
    # - corner: move cursor to a safe corner to avoid hover/tooltip pixel diffs
    cursor_avoid: Literal["none", "corner"] = "none"
    cursor_corner: Literal["tl", "tr", "bl", "br"] = "tl"
    cursor_margin: Annotated[int, Field(ge=0)] = 2
    cursor_restore: bool = False

    out_screenshot: str = "last_screenshot"
    out_x: str = "match_x"
    out_y: str = "match_y"
    out_score: str = "match_score"
    out_w: str = "match_w"
    out_h: str = "match_h"


class StepImageSearchAll(StepBase):
    """Capture the screen and return **all** needle matches.

    This is the screen-capture convenience wrapper around ImageSearchAllFile.
    """

    type: Literal["ImageSearchAll"] = "ImageSearchAll"
    needle_path: str
    region: RegionSpec | None = None
    threshold: float = 0.8
    scales: list[float] | None = None
    max_results: Annotated[int, Field(ge=1)] = 50
    overlap_threshold: Annotated[float, Field(ge=0.0, le=1.0)] = 0.3
    sort: Literal["score", "scan"] = "score"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"

    screenshot_path: str | None = None

    # Optional cursor hygiene before screen capture.
    cursor_avoid: Literal["none", "corner"] = "none"
    cursor_corner: Literal["tl", "tr", "bl", "br"] = "tl"
    cursor_margin: Annotated[int, Field(ge=0)] = 2
    cursor_restore: bool = False
    out_screenshot: str = "last_screenshot"
    out_matches: str = "matches"


class StepWaitForImage(StepBase):
    """Wait until a needle appears on the screen.

    Each poll captures a new screenshot, then runs template matching.
    """

    type: Literal["WaitForImage"] = "WaitForImage"
    needle_path: str
    region: RegionSpec | None = None
    threshold: float = 0.8
    scales: list[float] | None = None

    screenshot_path: str | None = None

    # Optional cursor hygiene before screen capture.
    cursor_avoid: Literal["none", "corner"] = "none"
    cursor_corner: Literal["tl", "tr", "bl", "br"] = "tl"
    cursor_margin: Annotated[int, Field(ge=0)] = 2
    cursor_restore: bool = False

    # Optional debug evidence on timeout: write an annotated screenshot showing
    # the best match found (even if below threshold).
    debug_on_timeout: bool = False
    out_debug_screenshot: str | None = None
    out_screenshot: str = "last_screenshot"

    timeout_ms: int = 10_000
    # SikuliX has Settings.WaitScanRate (scans/sec). scan_rate_hz is a convenient
    # alternative to poll_ms and takes precedence when set.
    scan_rate_hz: Annotated[float | None, Field(gt=0.0)] = None
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    # Optional stabilization: require the match condition to remain true for a
    # minimum duration / number of consecutive polls before succeeding.
    stable_ms: Annotated[int, Field(ge=0)] = 0
    stable_attempts: Annotated[int, Field(ge=1)] = 1

    out_x: str = "match_x"
    out_y: str = "match_y"
    out_score: str = "match_score"
    out_w: str = "match_w"
    out_h: str = "match_h"


class StepWaitForImageAll(StepBase):
    """Wait until **one or more** needle matches appear on the screen.

    This is the multi-match counterpart to WaitForImage, designed for
    SikuliX/AutoIt-style "click all checkboxes" workflows.
    """

    type: Literal["WaitForImageAll"] = "WaitForImageAll"
    needle_path: str
    region: RegionSpec | None = None
    threshold: float = 0.8
    scales: list[float] | None = None
    max_results: Annotated[int, Field(ge=1)] = 50
    overlap_threshold: Annotated[float, Field(ge=0.0, le=1.0)] = 0.3
    sort: Literal["score", "scan"] = "score"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"

    min_count: Annotated[int, Field(ge=1)] = 1

    screenshot_path: str | None = None

    # Optional cursor hygiene before screen capture.
    cursor_avoid: Literal["none", "corner"] = "none"
    cursor_corner: Literal["tl", "tr", "bl", "br"] = "tl"
    cursor_margin: Annotated[int, Field(ge=0)] = 2
    cursor_restore: bool = False

    debug_on_timeout: bool = False
    out_debug_screenshot: str | None = None
    out_screenshot: str = "last_screenshot"

    timeout_ms: int = 10_000
    scan_rate_hz: Annotated[float | None, Field(gt=0.0)] = None
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    # Optional stabilization: require the match-count condition to remain true
    # for a minimum duration / number of consecutive polls.
    stable_ms: Annotated[int, Field(ge=0)] = 0
    stable_attempts: Annotated[int, Field(ge=1)] = 1

    out_matches: str = "matches"
    out_count: str = "match_count"


class StepWaitForImageVanish(StepBase):
    """Wait until a needle is no longer found on the screen.

    This mirrors SikuliX's `waitVanish()` ("wait until the pattern can no
    longer be found") and is useful for spinners, progress dialogs, and transient
    tooltips.

    By default, if the needle is already absent the step succeeds immediately.
    Set require_seen=true to require the needle to be observed at least once
    before considering a later absence a success ("wait for appear+vanish").
    """

    type: Literal["WaitForImageVanish"] = "WaitForImageVanish"
    needle_path: str
    region: RegionSpec | None = None
    threshold: float = 0.8
    scales: list[float] | None = None

    screenshot_path: str | None = None

    cursor_avoid: Literal["none", "corner"] = "none"
    cursor_corner: Literal["tl", "tr", "bl", "br"] = "tl"
    cursor_margin: Annotated[int, Field(ge=0)] = 2
    cursor_restore: bool = False

    debug_on_timeout: bool = False
    out_debug_screenshot: str | None = None
    out_screenshot: str = "last_screenshot"

    timeout_ms: int = 10_000
    scan_rate_hz: Annotated[float | None, Field(gt=0.0)] = None
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    stable_ms: Annotated[int, Field(ge=0)] = 0
    stable_attempts: Annotated[int, Field(ge=1)] = 1

    require_seen: bool = False

    out_seen: str = "vanish_seen"
    out_last_score: str = "vanish_last_score"
    out_last_seen_x: str = "vanish_last_seen_x"
    out_last_seen_y: str = "vanish_last_seen_y"
    out_last_seen_score: str = "vanish_last_seen_score"


class StepClickImageAll(StepBase):
    """Wait for needle matches, then click each match.

    Clicking uses the center of the match rectangle by default (Sikuli-ish).

    If the needle has openQA-style metadata (<needle>.json), VHK will prefer a
    defined click point when match areas exist. This mirrors ClickNeedle, but
    operates on *multiple* matches.
    """

    type: Literal["ClickImageAll"] = "ClickImageAll"
    needle_path: str
    region: RegionSpec | None = None
    threshold: float = 0.8
    scales: list[float] | None = None
    max_results: Annotated[int, Field(ge=1)] = 50
    overlap_threshold: Annotated[float, Field(ge=0.0, le=1.0)] = 0.3
    sort: Literal["score", "scan"] = "score"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"
    min_count: Annotated[int, Field(ge=1)] = 1

    screenshot_path: str | None = None

    # Optional cursor hygiene before screen capture.
    cursor_avoid: Literal["none", "corner"] = "none"
    cursor_corner: Literal["tl", "tr", "bl", "br"] = "tl"
    cursor_margin: Annotated[int, Field(ge=0)] = 2
    cursor_restore: bool = False
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
    delay_between_clicks_ms: int = 0

    out_matches: str = "matches"
    out_count: str = "match_count"
    out_clicks: str = "clicks"
    out_clicked_count: str = "clicked_count"
    out_last_click_x: str = "last_click_x"
    out_last_click_y: str = "last_click_y"


class StepPixelSearch(StepBase):
    """Capture the screen (optionally a region) and search for a target color.

    This is the screen-capture counterpart to PixelSearchFile, inspired by
    AHK/AutoIt-style PixelSearch workflows.
    """

    type: Literal["PixelSearch"] = "PixelSearch"
    color: str | list[int]
    region: RegionSpec | None = None
    tolerance: float = 0.0
    tolerance_mode: Literal["euclidean", "per_channel"] = "euclidean"
    step: Annotated[int, Field(ge=1)] = 1
    match_strategy: Literal["best", "first"] = "best"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"

    # If provided, VHK will write the capture here; otherwise it uses a file in
    # the run log directory.
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    out_x: str = "px_x"
    out_y: str = "px_y"
    out_dist: str = "px_dist"


class StepPixelSearchAll(StepBase):
    """Capture the screen and return **all** pixel hits within tolerance.

    This is the screen-capture convenience wrapper around PixelSearchAllFile.
    """

    type: Literal["PixelSearchAll"] = "PixelSearchAll"
    color: str | list[int]
    region: RegionSpec | None = None
    tolerance: float = 0.0
    tolerance_mode: Literal["euclidean", "per_channel"] = "euclidean"
    step: Annotated[int, Field(ge=1)] = 1
    group: Literal["none", "connected"] = "none"
    pick: Literal["center", "first", "best"] = "center"
    min_area: Annotated[int, Field(ge=1)] = 1
    max_results: Annotated[int, Field(ge=1)] = 200
    sort: Literal["scan", "dist"] = "scan"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"

    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    out_matches: str = "px_matches"
    out_count: str = "px_match_count"


class StepWaitForPixel(StepBase):
    """Wait until a target color appears on screen."""

    type: Literal["WaitForPixel"] = "WaitForPixel"
    color: str | list[int]
    region: RegionSpec | None = None
    tolerance: float = 0.0
    tolerance_mode: Literal["euclidean", "per_channel"] = "euclidean"
    step: Annotated[int, Field(ge=1)] = 1
    match_strategy: Literal["best", "first"] = "best"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"

    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    timeout_ms: int = 10_000
    scan_rate_hz: Annotated[float | None, Field(gt=0.0)] = None
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    out_x: str = "px_x"
    out_y: str = "px_y"
    out_dist: str = "px_dist"


class StepWaitForPixelAll(StepBase):
    """Wait until **one or more** pixel hits (or blobs) appear on screen."""

    type: Literal["WaitForPixelAll"] = "WaitForPixelAll"
    color: str | list[int]
    region: RegionSpec | None = None
    tolerance: float = 0.0
    tolerance_mode: Literal["euclidean", "per_channel"] = "euclidean"
    step: Annotated[int, Field(ge=1)] = 1
    group: Literal["none", "connected"] = "none"
    pick: Literal["center", "first", "best"] = "center"
    min_area: Annotated[int, Field(ge=1)] = 1
    max_results: Annotated[int, Field(ge=1)] = 200
    sort: Literal["scan", "dist"] = "scan"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"

    min_count: Annotated[int, Field(ge=1)] = 1

    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    timeout_ms: int = 10_000
    scan_rate_hz: Annotated[float | None, Field(gt=0.0)] = None
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    out_matches: str = "px_matches"
    out_count: str = "px_match_count"


class StepWaitForPixelVanish(StepBase):
    """Wait until a target color is no longer found on screen."""

    type: Literal["WaitForPixelVanish"] = "WaitForPixelVanish"
    color: str | list[int]
    region: RegionSpec | None = None
    tolerance: float = 0.0
    tolerance_mode: Literal["euclidean", "per_channel"] = "euclidean"
    step: Annotated[int, Field(ge=1)] = 1
    match_strategy: Literal["best", "first"] = "best"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"

    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    timeout_ms: int = 10_000
    scan_rate_hz: Annotated[float | None, Field(gt=0.0)] = None
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    stable_ms: Annotated[int, Field(ge=0)] = 0
    stable_attempts: Annotated[int, Field(ge=1)] = 1

    require_seen: bool = False

    out_seen: str = "vanish_seen"
    out_last_dist: str = "vanish_last_dist"
    out_last_seen_x: str = "vanish_last_seen_x"
    out_last_seen_y: str = "vanish_last_seen_y"
    out_last_seen_dist: str = "vanish_last_seen_dist"


class StepClickPixelAll(StepBase):
    """Wait for pixel hits/blobs, then click each match.

    This is to PixelSearchAll what ClickTextAll is to OCR.
    """

    type: Literal["ClickPixelAll"] = "ClickPixelAll"
    color: str | list[int]
    region: RegionSpec | None = None
    tolerance: float = 0.0
    tolerance_mode: Literal["euclidean", "per_channel"] = "euclidean"
    step: Annotated[int, Field(ge=1)] = 1
    group: Literal["none", "connected"] = "none"
    pick: Literal["center", "first", "best"] = "center"
    min_area: Annotated[int, Field(ge=1)] = 1
    max_results: Annotated[int, Field(ge=1)] = 200
    sort: Literal["scan", "dist"] = "scan"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"
    min_count: Annotated[int, Field(ge=1)] = 1

    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    button: int | str = 1
    clearmodifiers: bool = False
    offset_x: int | str = 0
    offset_y: int | str = 0
    delay_between_clicks_ms: int = 0

    out_matches: str = "px_matches"
    out_count: str = "px_match_count"
    out_clicks: str = "click_points"
    out_clicked_count: str = "click_count"
    out_last_click_x: str = "last_click_x"
    out_last_click_y: str = "last_click_y"


class StepPixelGetColor(StepBase):
    """Capture the screen (optionally a region) and sample a pixel at (x,y).

    If no region is provided, VHK captures a minimal 1x1 rectangle at (x,y) to
    keep this operation fast and deterministic.
    """

    type: Literal["PixelGetColor"] = "PixelGetColor"
    x: int
    y: int
    region: RegionSpec | None = None

    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    out_hex: str = "px_color"
    out_ahk_hex: str = "px_color_ahk"
    out_r: str = "px_r"
    out_g: str = "px_g"
    out_b: str = "px_b"


class StepOcrReadText(StepBase):
    """Capture the screen (optionally a region) and OCR it."""

    type: Literal["OcrReadText"] = "OcrReadText"
    region: RegionSpec | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    out_var: str = "ocr_text"
    lang: str = "eng"
    preprocess: str | None = None
    scale: float | int | None = 1.0
    psm: int | None = None
    oem: int | None = None
    tess_config: str | None = None



class StepOcrNeedleText(StepBase):
    """Find a needle, then OCR an area relative to it (openQA-ish).

    Why this exists
    ---------------
    In many real UIs the *text you care about* moves with a button / card /
    toast, but global OCR over the entire screen is noisy and slow. openQA
    addresses this with "ocr" areas inside needle metadata (foo.png + foo.json)
    where OCR is scoped to the relevant ROI.

    VHK uses needle match areas (and optional exclude areas) to locate the
    element, then applies Tesseract OCR to either:
      - the first OCR area in the needle metadata, or
      - a selected OCR area (by id/index), or
      - the match bbox as a fallback.
    """

    type: Literal["OcrNeedleText"] = "OcrNeedleText"
    needle_path: str
    region: RegionSpec | None = None
    threshold: float = 0.8
    scales: list[float] | None = None

    # Select which OCR area(s) to use from needle metadata.
    ocr_area_id: str | None = None
    ocr_area_index: int | None = None
    ocr_strategy: Literal["first", "concat"] = "first"
    ocr_join: str = "\n"
    fallback_to_match_bbox: bool = True

    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    lang: str = "eng"
    preprocess: str | None = None
    scale: float | int | None = 1.0
    psm: int | None = None
    oem: int | None = None
    tess_config: str | None = None

    out_text: str = "ocr_text"

    # Diagnostics
    out_match_x: str = "match_x"
    out_match_y: str = "match_y"
    out_match_score: str = "match_score"
    out_match_w: str = "match_w"
    out_match_h: str = "match_h"
    out_ocr_x: str = "ocr_x"
    out_ocr_y: str = "ocr_y"
    out_ocr_w: str = "ocr_w"
    out_ocr_h: str = "ocr_h"


class StepWaitForNeedleText(StepBase):
    """Wait until a needle is present and OCR text matches a pattern.

    Combines:
    - WaitForImage (needle match + stability knobs)
    - WaitForText (OCR + pattern matching)

    This is useful for "button appears, then label becomes READY" workflows.
    """

    type: Literal["WaitForNeedleText"] = "WaitForNeedleText"
    needle_path: str
    region: RegionSpec | None = None
    threshold: float = 0.8
    scales: list[float] | None = None

    # Needle OCR area selection (see OcrNeedleText).
    ocr_area_id: str | None = None
    ocr_area_index: int | None = None
    ocr_strategy: Literal["first", "concat"] = "first"
    ocr_join: str = "\n"
    fallback_to_match_bbox: bool = True

    pattern: str
    match: Literal["contains", "regex", "fuzzy"] = "contains"
    fuzzy_threshold: float | None = None
    fuzzy_mode: Literal["partial", "ratio"] = "partial"
    case_sensitive: bool = False

    lang: str = "eng"
    preprocess: str | None = None
    scale: float | int | None = 1.0
    psm: int | None = None
    oem: int | None = None
    tess_config: str | None = None

    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    timeout_ms: int = 10_000
    scan_rate_hz: Annotated[float | None, Field(gt=0.0)] = None
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    # Optional stabilization: require the *text match* to remain true for a
    # minimum duration / number of consecutive polls.
    stable_ms: Annotated[int, Field(ge=0)] = 0
    stable_attempts: Annotated[int, Field(ge=1)] = 1

    out_text: str = "ocr_text"
    out_found: str = "text_found"

    # Diagnostics
    out_match_x: str = "match_x"
    out_match_y: str = "match_y"
    out_match_score: str = "match_score"
    out_match_w: str = "match_w"
    out_match_h: str = "match_h"
    out_ocr_x: str = "ocr_x"
    out_ocr_y: str = "ocr_y"
    out_ocr_w: str = "ocr_w"
    out_ocr_h: str = "ocr_h"


class StepWaitForText(StepBase):
    """Wait until OCR text matches a pattern (contains or regex)."""

    type: Literal["WaitForText"] = "WaitForText"
    region: RegionSpec | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    pattern: str
    match: Literal["contains", "regex", "fuzzy"] = "contains"
    fuzzy_threshold: float | None = None
    fuzzy_mode: Literal["partial", "ratio"] = "partial"
    case_sensitive: bool = False
    lang: str = "eng"
    preprocess: str | None = None
    scale: float | int | None = 1.0
    psm: int | None = None
    oem: int | None = None
    tess_config: str | None = None

    timeout_ms: int = 10_000
    scan_rate_hz: Annotated[float | None, Field(gt=0.0)] = None
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    out_text: str = "ocr_text"
    out_found: str = "text_found"


class StepWaitForTextVanish(StepBase):
    """Wait until OCR text no longer matches a pattern.

    SikuliX's `waitVanish()` accepts a string that can be an image path *or* a
    plain text pattern and waits until it vanishes. In VHK, this is implemented
    as OCR + text matching.

    By default, if the text is already absent the step succeeds immediately.
    Set require_seen=true to require the text match to be observed at least
    once before considering a later absence a success.
    """

    type: Literal["WaitForTextVanish"] = "WaitForTextVanish"
    region: RegionSpec | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    pattern: str
    match: Literal["contains", "regex", "fuzzy"] = "contains"
    fuzzy_threshold: float | None = None
    fuzzy_mode: Literal["partial", "ratio"] = "partial"
    case_sensitive: bool = False

    lang: str = "eng"
    preprocess: str | None = None
    scale: float | int | None = 1.0
    psm: int | None = None
    oem: int | None = None
    tess_config: str | None = None

    timeout_ms: int = 10_000
    scan_rate_hz: Annotated[float | None, Field(gt=0.0)] = None
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    stable_ms: Annotated[int, Field(ge=0)] = 0
    stable_attempts: Annotated[int, Field(ge=1)] = 1

    require_seen: bool = False

    out_text: str = "ocr_text"
    out_seen: str = "vanish_seen"
    out_last_text: str = "vanish_last_text"
    out_last_present: str = "vanish_last_present"


class StepAssertText(StepBase):
    """Assert that OCR text matches a pattern (contains or regex)."""

    type: Literal["AssertText"] = "AssertText"
    region: RegionSpec | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    pattern: str
    match: Literal["contains", "regex", "fuzzy"] = "contains"
    fuzzy_threshold: float | None = None
    fuzzy_mode: Literal["partial", "ratio"] = "partial"
    case_sensitive: bool = False
    lang: str = "eng"
    preprocess: str | None = None
    scale: float | int | None = 1.0
    psm: int | None = None
    oem: int | None = None
    tess_config: str | None = None

    out_text: str = "ocr_text"


class StepOcrFindTextFile(StepBase):
    """OCR an image file and locate a word/line bounding box."""

    type: Literal["OcrFindTextFile"] = "OcrFindTextFile"
    image_path: str
    region: RegionSpec | None = None

    pattern: str
    match: Literal["contains", "regex", "fuzzy"] = "contains"
    fuzzy_threshold: float | None = None
    fuzzy_mode: Literal["partial", "ratio"] = "partial"
    case_sensitive: bool = False
    lang: str = "eng"
    preprocess: str | None = None
    scale: float | int | None = 1.0
    psm: int | None = None
    oem: int | None = None
    tess_config: str | None = None

    level: Literal["word", "line"] = "word"
    match_strategy: Literal["first", "best_conf"] = "first"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"

    out_x: str = "ocr_x"
    out_y: str = "ocr_y"
    out_w: str = "ocr_w"
    out_h: str = "ocr_h"
    out_text: str = "ocr_match_text"
    out_conf: str = "ocr_conf"


class StepOcrFindText(StepBase):
    """Capture the screen (optionally a region), OCR it, and locate a text bbox."""

    type: Literal["OcrFindText"] = "OcrFindText"
    region: RegionSpec | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    pattern: str
    match: Literal["contains", "regex", "fuzzy"] = "contains"
    fuzzy_threshold: float | None = None
    fuzzy_mode: Literal["partial", "ratio"] = "partial"
    case_sensitive: bool = False
    lang: str = "eng"
    preprocess: str | None = None
    scale: float | int | None = 1.0
    psm: int | None = None
    oem: int | None = None
    tess_config: str | None = None

    level: Literal["word", "line"] = "word"
    match_strategy: Literal["first", "best_conf"] = "first"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"

    out_x: str = "ocr_x"
    out_y: str = "ocr_y"
    out_w: str = "ocr_w"
    out_h: str = "ocr_h"
    out_text: str = "ocr_match_text"
    out_conf: str = "ocr_conf"


class StepOcrFindTextAllFile(StepBase):
    """OCR an image file and return all matching word/line bounding boxes."""

    type: Literal["OcrFindTextAllFile"] = "OcrFindTextAllFile"
    image_path: str
    region: RegionSpec | None = None

    pattern: str
    match: Literal["contains", "regex", "fuzzy"] = "contains"
    fuzzy_threshold: float | None = None
    fuzzy_mode: Literal["partial", "ratio"] = "partial"
    case_sensitive: bool = False
    lang: str = "eng"
    preprocess: str | None = None
    scale: float | int | None = 1.0
    psm: int | None = None
    oem: int | None = None
    tess_config: str | None = None

    level: Literal["word", "line"] = "word"
    sort: Literal["scan", "best_conf"] = "scan"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"
    max_results: int | None = None
    min_conf: float | None = None

    out_matches: str = "ocr_matches"
    out_count: str = "ocr_match_count"


class StepOcrFindTextAll(StepBase):
    """Capture the screen (optionally a region), OCR it, and return all matching bboxes."""

    type: Literal["OcrFindTextAll"] = "OcrFindTextAll"
    region: RegionSpec | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    pattern: str
    match: Literal["contains", "regex", "fuzzy"] = "contains"
    fuzzy_threshold: float | None = None
    fuzzy_mode: Literal["partial", "ratio"] = "partial"
    case_sensitive: bool = False
    lang: str = "eng"
    preprocess: str | None = None
    scale: float | int | None = 1.0
    psm: int | None = None
    oem: int | None = None
    tess_config: str | None = None

    level: Literal["word", "line"] = "word"
    sort: Literal["scan", "best_conf"] = "scan"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"
    max_results: int | None = None
    min_conf: float | None = None

    out_matches: str = "ocr_matches"
    out_count: str = "ocr_match_count"


class StepWaitForTextBox(StepBase):
    """Wait until OCR finds a word/line bounding box."""

    type: Literal["WaitForTextBox"] = "WaitForTextBox"
    region: RegionSpec | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    pattern: str
    match: Literal["contains", "regex", "fuzzy"] = "contains"
    fuzzy_threshold: float | None = None
    fuzzy_mode: Literal["partial", "ratio"] = "partial"
    case_sensitive: bool = False
    lang: str = "eng"
    preprocess: str | None = None
    scale: float | int | None = 1.0
    psm: int | None = None
    oem: int | None = None
    tess_config: str | None = None

    level: Literal["word", "line"] = "word"
    match_strategy: Literal["first", "best_conf"] = "first"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"

    timeout_ms: int = 10_000
    scan_rate_hz: Annotated[float | None, Field(gt=0.0)] = None
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    out_ocr_text: str = "ocr_text"
    out_found: str = "text_found"

    out_x: str = "ocr_x"
    out_y: str = "ocr_y"
    out_w: str = "ocr_w"
    out_h: str = "ocr_h"
    out_text: str = "ocr_match_text"
    out_conf: str = "ocr_conf"


class StepClickText(StepBase):
    """Wait for text (OCR) then click the center of its bounding box."""

    type: Literal["ClickText"] = "ClickText"
    region: RegionSpec | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    pattern: str
    match: Literal["contains", "regex", "fuzzy"] = "contains"
    fuzzy_threshold: float | None = None
    fuzzy_mode: Literal["partial", "ratio"] = "partial"
    case_sensitive: bool = False
    lang: str = "eng"
    preprocess: str | None = None
    scale: float | int | None = 1.0
    psm: int | None = None
    oem: int | None = None
    tess_config: str | None = None

    level: Literal["word", "line"] = "word"
    match_strategy: Literal["first", "best_conf"] = "first"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"

    timeout_ms: int = 10_000
    scan_rate_hz: Annotated[float | None, Field(gt=0.0)] = None
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    button: int | str = 1
    clearmodifiers: bool = False
    offset_x: int | str = 0
    offset_y: int | str = 0

    out_match_x: str = "ocr_x"
    out_match_y: str = "ocr_y"
    out_match_w: str = "ocr_w"
    out_match_h: str = "ocr_h"
    out_match_text: str = "ocr_match_text"
    out_match_conf: str = "ocr_conf"

    out_click_x: str = "click_x"
    out_click_y: str = "click_y"


class StepClickTextAll(StepBase):
    """Wait for OCR text matches, then click the center of each matched bbox."""

    type: Literal["ClickTextAll"] = "ClickTextAll"
    region: RegionSpec | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"

    pattern: str
    match: Literal["contains", "regex", "fuzzy"] = "contains"
    fuzzy_threshold: float | None = None
    fuzzy_mode: Literal["partial", "ratio"] = "partial"
    case_sensitive: bool = False
    lang: str = "eng"
    preprocess: str | None = None
    scale: float | int | None = 1.0
    psm: int | None = None
    oem: int | None = None
    tess_config: str | None = None

    level: Literal["word", "line"] = "word"
    sort: Literal["scan", "best_conf"] = "scan"
    scan_order: Literal["tlbr", "trbl", "bltr", "brtl"] = "tlbr"
    max_results: int | None = None
    min_conf: float | None = None

    timeout_ms: int = 10_000
    scan_rate_hz: Annotated[float | None, Field(gt=0.0)] = None
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    button: int | str = 1
    clearmodifiers: bool = False
    offset_x: int | str = 0
    offset_y: int | str = 0
    delay_between_clicks_ms: int = 0

    out_matches: str = "ocr_matches"
    out_count: str = "ocr_match_count"
    out_clicks: str = "click_points"
    out_clicked_count: str = "click_count"
    out_last_click_x: str = "last_click_x"
    out_last_click_y: str = "last_click_y"




class StepVisualAssert(StepBase):
    """Compare a captured region/screen against a baseline image.

    This is intentionally strict and explainable: same-size compare with optional
    openQA-style match/exclude areas from the baseline sidecar JSON.
    """

    type: Literal["VisualAssert"] = "VisualAssert"
    baseline_path: str
    region: RegionSpec | None = None
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
    region: RegionSpec | None = None
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
    region: RegionSpec | None = None
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

class StepWaitForRegionStable(StepBase):
    """Wait until a captured region becomes visually stable.

    This mirrors "stable screenshot detection" patterns used in visual
    regression testing frameworks: capture an initial baseline, then keep
    capturing and comparing until consecutive frames stop changing (within
    tolerance).

    If baseline_path is provided, VHK copies it into the run log directory
    first so rolling_baseline updates never modify project assets.
    """

    type: Literal["WaitForRegionStable"] = "WaitForRegionStable"
    baseline_path: str | None = None
    region: RegionSpec | None = None
    screenshot_path: str | None = None
    out_screenshot: str = "last_screenshot"
    out_baseline: str = "baseline_screenshot"

    # Optional cursor hygiene before screen capture.
    cursor_avoid: Literal["none", "corner"] = "none"
    cursor_corner: Literal["tl", "tr", "bl", "br"] = "tl"
    cursor_margin: Annotated[int, Field(ge=0)] = 2
    cursor_restore: bool = False

    debug_on_timeout: bool = False
    out_visual_diff: str = "last_visual_diff"

    color_tolerance: int = 0
    max_changed_pixels: int | None = 0
    max_change_ratio: float = 0.0

    # When True, update the baseline to the newest captured frame whenever the
    # compare indicates instability. This helps "ride out" animations and
    # loading transitions until the region settles.
    rolling_baseline: bool = True

    timeout_ms: int = 10_000
    scan_rate_hz: Annotated[float | None, Field(gt=0.0)] = None
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    stable_ms: Annotated[int, Field(ge=0)] = 0
    stable_attempts: Annotated[int, Field(ge=1)] = 1

    out_ok: str = "stable_ok"
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
    region: RegionSpec | None = None
    threshold: float = 0.8
    scales: list[float] | None = None

    screenshot_path: str | None = None

    # Optional cursor hygiene before screen capture.
    cursor_avoid: Literal["none", "corner"] = "none"
    cursor_corner: Literal["tl", "tr", "bl", "br"] = "tl"
    cursor_margin: Annotated[int, Field(ge=0)] = 2
    cursor_restore: bool = False

    debug_on_timeout: bool = False
    out_debug_screenshot: str | None = None
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

    # Optional movement smoothing (useful for "human-like" cursor motion or
    # for apps that ignore instantaneous teleports).
    duration_ms: int = 0
    smooth_steps: int = 0
    easing: Literal["linear", "ease_in_out"] = "linear"


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

    # Optional smoothing for the drag path. When set, VHK will hold the button
    # down and move across intermediate points.
    duration_ms: int = 0
    smooth_steps: int = 0
    easing: Literal["linear", "ease_in_out"] = "linear"


class StepMouseWheel(StepBase):
    type: Literal["MouseWheel"] = "MouseWheel"
    clicks: int | str = 1
    axis: Literal["vertical", "horizontal"] = "vertical"


class StepCursorHide(StepBase):
    type: Literal["CursorHide"] = "CursorHide"


class StepCursorShow(StepBase):
    type: Literal["CursorShow"] = "CursorShow"


class StepGetCursorPos(StepBase):
    """Get global cursor position (best-effort).

    Wayland sessions use compositor/tool-specific helpers when available.
    """

    type: Literal["GetCursorPos"] = "GetCursorPos"
    out_x: str = "cursor_x"
    out_y: str = "cursor_y"
    out_backend: str = "cursorpos_backend"


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


class StepWaitForClipboardEvent(StepBase):
    """Wait for a clipboard *event* and record whether the contents changed.

    Unlike WaitForClipboardChange, this can return even when the clipboard text
    is identical to the baseline (e.g. copying an empty string, or copying the
    same selection again) when a backend helper is available:

    - X11: clipnotify
    - Wayland: wl-paste --watch (when supported by the compositor)

    When no helper is available, VHK falls back to polling, in which case it can
    only detect content changes.
    """

    type: Literal["WaitForClipboardEvent"] = "WaitForClipboardEvent"
    selection: Literal["clipboard", "primary"] = "clipboard"
    initial_text: str | None = None

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    out_text: str = "clipboard_text"
    out_changed: str = "clipboard_changed"
    out_event: str = "clipboard_event"


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



class StepWaitForHttp(StepBase):
    """Poll an HTTP endpoint until a condition is met.

    This is a pragmatic "service is up" / "page is ready" primitive commonly used
    in CI pipelines and automation systems.

    You can either:
    - use the built-in checks (status range / text match), or
    - provide a flexible `condition` expression evaluated against the response.

    Condition environment:
      - http_status, http_reason, http_headers, http_text, http_url
      - http_json (only when needed / requested)

    Notes
    -----
    If the response includes a Retry-After header and `respect_retry_after` is
    enabled, VHK will prefer that delay between attempts.
    """

    type: Literal["WaitForHttp"] = "WaitForHttp"
    method: str = "GET"
    url: str
    headers: dict[str, Any] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    body: str | None = None
    json_expr: str | None = None
    timeout_ms: int = 30_000
    allow_error_status: bool = True

    # Success criteria (optional). If none are provided, defaults to HTTP 2xx.
    ok_statuses: list[int] | None = None
    status_min: int | None = 200
    status_max: int | None = 299
    text_contains: str | None = None
    text_regex: str | None = None
    condition: str | None = None
    respect_retry_after: bool = True

    poll_ms: int = 200
    max_poll_ms: int = 2_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    out_status: str = "http_status"
    out_reason: str = "http_reason"
    out_headers: str = "http_headers"
    out_text: str = "http_text"
    out_json: str | None = None
    out_url: str = "http_url"
    out_attempts: str = "http_attempts"
    out_elapsed_ms: str = "http_elapsed_ms"

class StepDownloadFile(StepBase):
    type: Literal["DownloadFile"] = "DownloadFile"
    url: str
    path: str
    headers: dict[str, Any] = Field(default_factory=dict)
    timeout_ms: int = 30_000
    create_parents: bool = True
    overwrite: bool = True
    atomic: bool = True
    tmp_suffix: str = ".part"
    sha256: str | None = None
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

    # Search subdirectories too (uses recursive glob and, when available,
    # inotifywait --recursive to sleep between scans).
    recursive: bool = False

    # By default VHK treats modifications of already-existing matching files as
    # candidates (useful for overwrite-style producers). Set this to false if
    # you want to only consider *new paths* in the directory tree.
    include_existing_changes: bool = True

    # Override the "since" timestamp used when include_existing_changes is enabled.
    # If omitted, VHK uses the run's start time. Set explicitly to null to
    # disable the existing-file modification heuristic.
    since_ns: int | str | None = None

    # Optional filters and safety knobs.
    #
    # Desktop downloads commonly create temporary files (e.g. "*.part",
    # "*.crdownload") before moving/renaming to a final filename. `exclude`
    # makes it easy to ignore those.
    exclude: str | list[str] | None = None
    # Require the file to be at least this many bytes before returning.
    # Useful for producers that create empty placeholders first.
    min_size: int = 0
    # Require the file's (size, mtime) to remain unchanged for this long.
    # Useful for large writes or non-atomic producers.
    stable_ms: int = 0

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    out_path: str = "new_file_path"
    out_name: str = "new_file_name"
    out_size: str = "new_file_size"
    out_mtime_ns: str = "new_file_mtime_ns"


class StepWaitForDownload(StepBase):
    """Wait for a download-like file to finish in a directory.

    This is a convenience wrapper around WaitForNewFile with defaults tuned for
    browser/download workflows:

    - ignores common partial-download suffixes (e.g. *.crdownload, *.part, *.download)
    - requires a non-empty file by default
    - optionally requires the file to be stable for a small window

    If you need fine-grained control (e.g. allow overwrites of an existing path),
    prefer WaitForNewFile.
    """

    type: Literal["WaitForDownload"] = "WaitForDownload"
    directory: str
    pattern: str = "*"

    recursive: bool = False

    # Optional extra excludes layered on top of VHK's built-ins.
    exclude: str | list[str] | None = None

    # By default we only consider *new paths* for downloads.
    include_existing_changes: bool = False
    since_ns: int | str | None = None

    # Safety knobs.
    min_size: int = 1
    stable_ms: int = 500

    timeout_ms: int = 30_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    max_attempts: int | None = None

    out_path: str = "download_path"
    out_name: str = "download_name"
    out_size: str = "download_size"
    out_mtime_ns: str = "download_mtime_ns"


# --- i3 IPC -----------------------------------------------------------------


class I3WindowSelector(BaseModel):
    """A minimal selector for an i3 tree node/window."""

    model_config = ConfigDict(populate_by_name=True)

    # sway uses app_id for native Wayland windows (xdg-shell). i3 won't set it.
    app_id: str | None = None
    app_id_regex: bool = False

    title: str | None = None
    title_regex: bool = False

    wm_class: str | None = Field(default=None, alias="class")
    instance: str | None = None
    window_role: str | None = None

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
    """Wait for a window that matches selector (i3/sway/Hyprland best-effort)."""

    type: Literal["WaitForWindow"] = "WaitForWindow"
    selector: I3WindowSelector

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    use_events: bool = True

    stable_ms: Annotated[int, Field(ge=0)] = 0
    stable_attempts: Annotated[int, Field(ge=1)] = 1

    out_var: str = "i3_window"
    out_con_id: str = "i3_con_id"
    out_workspace: str = "i3_workspace"

    focus: bool = False


class StepWaitForWindowVanish(StepBase):
    """Wait until a window matching selector no longer exists.

    Mirrors AutoHotkey's WinWaitClose(): wait until a matching window does not
    exist. Useful for modal dialogs and transient popups.

    By default, if the window is already absent the step succeeds immediately.
    Set require_seen=true to require the window to be observed at least once
    before considering a later absence a success.
    """

    type: Literal["WaitForWindowVanish"] = "WaitForWindowVanish"
    selector: I3WindowSelector

    timeout_ms: int = 10_000
    poll_ms: int = 200
    max_poll_ms: int = 1_000
    jitter_ms: int = 30
    use_events: bool = True

    stable_ms: Annotated[int, Field(ge=0)] = 0
    stable_attempts: Annotated[int, Field(ge=1)] = 1

    require_seen: bool = False

    out_seen: str = "vanish_seen"
    out_last_con_id: str = "vanish_last_con_id"
    out_last_workspace: str = "vanish_last_workspace"
    out_last_window: str = "vanish_last_window"


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
        StepImageSearchAllFile,
        StepWaitForImageFile,
        StepPixelSearchFile,
        StepPixelSearchAllFile,
        StepWaitForPixelFile,
        StepPixelGetColorFile,
        StepOcrReadTextFile,
        StepCaptureScreenshot,
        StepCoordMode,
        StepImageSearch,
        StepImageSearchAll,
        StepWaitForImage,
        StepWaitForImageAll,
        StepWaitForImageVanish,
        StepPixelSearch,
        StepPixelSearchAll,
        StepWaitForPixel,
        StepWaitForPixelAll,
        StepWaitForPixelVanish,
        StepPixelGetColor,
        StepVisualAssert,
        StepVisualVerify,
        StepWaitForRegionChange,
        StepWaitForRegionStable,
        StepOcrReadText,
        StepOcrNeedleText,
        StepWaitForNeedleText,
        StepWaitForText,
        StepWaitForTextVanish,
        StepAssertText,
        StepOcrFindTextFile,
        StepOcrFindTextAllFile,
        StepOcrFindText,
        StepOcrFindTextAll,
        StepWaitForTextBox,
        StepClickText,
        StepClickTextAll,
        StepClickPixelAll,
        StepClickImageAll,
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
        StepGetCursorPos,
        StepMouseClickAt,
        StepNotify,
        StepClipboardRead,
        StepClipboardSet,
        StepWaitForClipboardChange,
        StepWaitForClipboardEvent,
        StepPasteClipboard,
        StepOpenUrl,
        StepComposeEmail,
        StepHttpRequest,
        StepWaitForHttp,
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
        StepWaitForDownload,
        StepI3Command,
        StepI3GetTree,
        StepI3GetWorkspaces,
        StepWaitForWindow,
        StepWaitForWindowVanish,
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

    # Optional stable name used by exporters (bus dispatch, future Studio UI).
    name: str | None = None

    keys: str
    macro: str
    description: str | None = None
    vars: dict[str, Any] = Field(default_factory=dict)

    # Optional i3 "criteria" (context) for bindsym.
    # When set, the hotkey triggers only when the focused window matches.
    when: I3WindowSelector | None = None


class HotstringBinding(BaseModel):
    """A project-level hotstring binding for text expansion tooling.

    This is intentionally backend-agnostic: VHK does not attempt to implement global
    key interception itself (which is hard / impossible on Wayland and often best
    delegated to the compositor or a dedicated daemon). Instead, VHK can *export*
    these bindings to an external hotstring engine (e.g. espanso).

    The default "return" mode is designed for text expansion: the bound macro
    should end with a Return step, and `vhk run --print-return` will emit the
    returned value on stdout for the external engine to inject.
    """

    trigger: str
    macro: str
    description: str | None = None
    enabled: bool = True
    vars: dict[str, Any] = Field(default_factory=dict)

    # Optional context condition. Note: espanso's app-specific filtering is not
    # currently available on Wayland, so exporters may only support this on X11.
    when: I3WindowSelector | None = None

    mode: Literal["return", "side_effect"] = "return"
    return_var: str = "return_value"

    # Optional espanso-specific hints. We keep these optional so the project format
    # remains generic; exporters may choose to ignore them.
    force_mode: Literal["clipboard", "keys", "auto"] | None = None

    # Optional espanso "form" layout (multi-field prompt).
    # When provided, exporters may generate an Espanso form variable and inject
    # its fields into the VHK macro as initial vars.
    form_layout: str | None = None


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

    # How to interpret "duplicate" clipboard values.
    # - handled: compare against the last clipboard text that actually ran the macro.
    #            (This is useful for "open URL" style watchers where you often
    #            don't want to re-trigger on the same URL repeatedly.)
    # - seen: compare against the last seen clipboard value (consecutive duplicates).
    dedupe_scope: Literal["handled", "seen"] = "handled"

    # Optional: skip clipboard texts seen in the last N milliseconds.
    # Useful when the clipboard toggles rapidly between a small set of values.
    dedupe_window_ms: int = 0
    dedupe_max_entries: int = 128

    # Optional: throttle watcher-triggered macro runs. While in cooldown, events
    # are observed (and logged) but the macro is not executed.
    cooldown_ms: int = 0
    continue_on_macro_error: bool = True
    vars: dict[str, Any] = Field(default_factory=dict)




class BusWatcher(BaseModel):
    """Project-level IPC bus rule that triggers a macro on local events.

    This is a portable "escape hatch": anything that can send a UNIX socket
    datagram (or a simple text line) can trigger VHK automation.

    Typical uses:
      - WM config glue (Hyprland dispatchers, i3 binds, etc.)
      - scripts / cron / systemd user units
      - bridging external tools into VHK without writing Python plugins
    """

    name: str
    # Macro to run when a matching event arrives.
    #
    # If you set `dispatch: true`, this may be omitted: the watcher will
    # determine the macro to run from the incoming event's JSON payload.
    macro: str | None = None
    enabled: bool = True

    # Dispatch mode: interpret event payloads as "run macro X with vars Y".
    # This is the recommended pattern for hotkey exports that emit bus events:
    # it avoids defining one watcher per binding.
    dispatch: bool = False
    dispatch_macro_key: str = "macro"
    dispatch_vars_key: str = "vars"
    dispatch_require_window_key: str = "require_window"
    dispatch_binding_key: str = "binding"
    dispatch_keys_key: str = "keys"

    # Optional allow-list for dispatch macros. If set, only these macros may be
    # invoked via dispatch events.
    dispatch_allowed_macros: list[str] | None = None

    # Which bus event name should trigger this watcher.
    # Use "*" to accept any event (and filter with `pattern` if desired).
    event: str = "*"

    # When true, stop evaluation after this watcher handles an event.
    # This is useful when multiple watchers listen to the same bus event
    # and you want first-match semantics (rule-engine style).
    consume: bool = False

    # Optional content filter applied to a text representation of the event's data.
    pattern: str | None = None
    flags: list[Literal["IGNORECASE", "MULTILINE", "DOTALL"]] = Field(default_factory=list)

    debounce_ms: int = 0
    dedupe: bool = True

    # Optional: skip repeated event signatures seen in the last N milliseconds.
    dedupe_window_ms: int = 0
    dedupe_max_entries: int = 256

    # Optional: throttle watcher-triggered macro runs.
    cooldown_ms: int = 0

    # Optional context filter: only trigger when the focused window matches.
    when: I3WindowSelector | None = None

    continue_on_macro_error: bool = True
    vars: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_bus_watcher(self):
        if self.dispatch:
            # In dispatch mode, macro is optional.
            return self
        if not self.macro:
            raise ValueError("BusWatcher requires 'macro' unless dispatch=true")
        return self


class WindowWatcher(BaseModel):
    """Project-level window rule that triggers a macro on WM focus/workspace changes.

    The intent is similar to clipboard watchers: keep policy (what should trigger)
    in project.yaml, and reuse the normal Runner for side effects.

    Note: On Wayland, global window identification is compositor-specific.
    VHK implements i3/sway via IPC events and Hyprland via socket2 events.
    """

    name: str
    macro: str
    enabled: bool = True

    # Which high-level event should trigger the watcher.
    # - focus: active window changed
    # - workspace: focused workspace changed
    # - title: a window title changed
    # - urgent: a window became urgent or lost urgency
    # - custom: compositor-specific custom event (currently Hyprland socket2 `custom>>...`).
    event: Literal["focus", "workspace", "title", "urgent", "new", "close", "custom"] = "focus"

    # Optional context filter: for focus watchers, this matches against the
    # active window. For workspace watchers, it matches against the active window
    # as well (useful for per-app workspace routines).
    when: I3WindowSelector | None = None

    # Avoid noisy loops.
    debounce_ms: int = 0
    dedupe: bool = True

    # Optional: skip repeated window signatures seen in the last N milliseconds.
    dedupe_window_ms: int = 0
    dedupe_max_entries: int = 256

    # Optional: throttle watcher-triggered macro runs.
    cooldown_ms: int = 0

    # When false, the watcher stops on the first macro failure.
    continue_on_macro_error: bool = True

    # When true, include the previous active window in vars (when available).
    include_prev: bool = True

    # When true, emit one synthetic event at startup using the current active
    # window (if available).
    fire_on_start: bool = False

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

    # Optional: IPC event bus socket path. If unset, VHK chooses a per-project
    # path under XDG_RUNTIME_DIR when available, falling back to <project>/.vhk.
    bus_socket: str | None = None

    # Optional: when using systemd socket activation and multiple file descriptors
    # are passed to the service, VHK can select the correct one by name.
    #
    # systemd provides names via the LISTEN_FDNAMES env var, which can be set
    # from the *.socket unit using FileDescriptorName=.
    #
    # If unset, VHK will consume the first passed descriptor (fd 3).
    bus_fdname: str | None = None

    # Optional: bus event name that triggers a live reload of busd config.
    #
    # Convention: VHK reserves the `vhk.*` namespace for internal bus events.
    # Disable by setting this to null or an empty string.
    bus_reload_event: str | None = 'vhk.reload'


    # Optional: bus event name that requests busd shutdown.
    #
    # Convention: VHK reserves the `vhk.*` namespace for internal bus events.
    # Disable by setting this to null or an empty string.
    bus_stop_event: str | None = 'vhk.stop'

    hide_cursor_during_run: bool = False

    # When enabled, VHK will not run external side-effects (shell, input, notify).
    dry_run: bool = False


class Project(BaseModel):
    name: str
    macros: dict[str, Macro]
    root_dir: str
    # Named regions of interest.
    # Useful for scoping image/pixel/OCR searches to a stable rectangle.
    regions: dict[str, Region] = Field(default_factory=dict)
    bindings: list[HotkeyBinding] = Field(default_factory=list)
    hotstrings: list[HotstringBinding] = Field(default_factory=list)
    clipboard_watchers: list[ClipboardWatcher] = Field(default_factory=list)
    bus_watchers: list[BusWatcher] = Field(default_factory=list)
    window_watchers: list[WindowWatcher] = Field(default_factory=list)
    settings: ProjectSettings = Field(default_factory=ProjectSettings)


# Resolve forward references
StepIf.model_rebuild()
StepWhile.model_rebuild()
StepTry.model_rebuild()
StepForEach.model_rebuild()
