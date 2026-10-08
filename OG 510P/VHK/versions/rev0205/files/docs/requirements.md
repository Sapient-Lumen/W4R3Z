# VHK + Macro Creator for i3/X11
*A Pulover’s Macro Creator (PMC)-class visual macro builder + “VisualHotKey” studio for i3/X11, with first‑class visual automation.*

> This document is a requirements and feature inventory for building a unified, i3/X11‑native automation studio inspired by **Pulover’s Macro Creator** (macro recording + script generation + action palette) and “VHK” style **visual hotkey / macro construction tooling**.  
> It emphasizes “AHK power” through **visual targeting** (image/pixel/OCR), **structured targeting** (i3 + accessibility), and **excellent tooling** (inspect/record/compose/debug/run).

---

## 0) North star

### The job-to-be-done
- **Record** a workflow (or parts of it).
- **Replace brittle playback** with robust, inspectable steps:
  - “Wait until the thing exists.”
  - “Find the thing visually or structurally.”
  - “Click/type relative to it.”
  - “Branch on what you see.”
- **Debug** with confidence (step-through + overlays + logs).
- **Package** and **run** macros as a reliable tool, not a science fair project.

### Core principle
**The tool must be better at building scripts than users are.**  
Visual tooling (inspector + capture + step synthesis) is the product.

---

## 1) Product scope

### In-scope (v1)
- i3 **window/workspace** automation via i3 IPC.
- X11 input/output automation (keyboard/mouse, focus, windows).
- Visual automation: image search, pixel search, OCR.
- Accessibility automation (AT‑SPI) where available, plus a visual tree browser.
- Visual macro builder + recorder + debugger (PMC-class).
- A coherent **hotkey/hotstring** system (“VHK-class”), including context conditions.

### Explicitly out-of-scope (v1)
- Full Wayland support (architect for it, but don’t block v1).
- Full “Windows AHK compatibility” for scripts (we are building a Linux-native studio).

---

## 2) What we’re copying from PMC (feature inventory)

PMC is a good baseline because it is *already* a “macro creator + script generator” with:
- **Recorder**
- **Action palette / command windows**
- **Variables/expressions**
- **Image/pixel search + screenshot tooling**
- **OCR (Image to Text)**
- **Multiple macros + hotkeys**
- **Export to script + compile to EXE**

### 2.1 Recorder fidelity and options
PMC’s recorder includes several “real-world” toggles that matter for games/apps:

- **Key down/up capture** (vs just keystroke).  
  PMC explicitly supports “Capture key state (Down / Up)”.  
  Ref: https://www.macrocreator.com/docs/Record.html

- Record **ControlSend** and **ControlClick** attempts (background automation) with caveats.  
  Ref: https://www.macrocreator.com/docs/Record.html

- Mouse clicks include left/right/middle/X1/X2, wheel, moves, etc.  
  Ref: https://www.macrocreator.com/docs/Record.html

**Requirement:** v1 must record at least:
- keyboard down/up
- mouse down/up
- wheel
- mouse move with configurable sampling / “minimum idle to record final move”
- active window changes (focus events)
- optional “try background control action” capture where possible

### 2.2 Multiple macros, hotkeys, manual stepping (debug)
PMC supports:
- Multiple macros in one project, each with its own hotkeys.  
  Ref: https://www.macrocreator.com/docs/Playback.html

- **Manual hotkey** to execute step-by-step for debugging.  
  Ref: https://www.macrocreator.com/docs/Playback.html

- Built-in hotkey management, including hotstrings to trigger macros.  
  Ref: https://www.macrocreator.com/docs/Playback.html

**Requirement:** “Run-mode” must include:
- Play macro
- Step macro (manual/next)
- Pause/resume
- Stop/reset
- Toggle “Always active” hotkeys (PMC has this option; see FAQ).  
  Ref: https://www.macrocreator.com/docs/Faq.html

### 2.3 Context-sensitive hotkeys (VHK-class core)
PMC supports **Context Sensitive Hotkeys** globally and per-macro; it uses #If/#IfWinActive semantics.  
Ref: https://www.macrocreator.com/docs/Playback.html and https://www.macrocreator.com/docs/Export.html

**Requirement:** v1 must support:
- Hotkeys/hotstrings that only trigger under conditions:
  - active window matches selector
  - window exists
  - expression evaluates to true
- UI for defining those conditions (visual, click-to-pick window)

### 2.4 “Find a Command” + common fields
PMC has a “Find a Command” window and defines common fields (Repeat, Delay, Control, etc.).  
Ref: https://www.macrocreator.com/docs/Commands.html

**Requirement:** Provide:
- action search
- standardized step fields: repeat, delay, enable/disable, comment/label
- parameter editor that supports variables/expressions across the board

### 2.5 Image/Pixel search tooling (visual automation baseline)
PMC’s docs show mature “make a screenshot / define search area” workflow:
- screenshot rectangle can remain visible until confirm; adjustable with hotkeys  
  Ref: https://www.macrocreator.com/docs/Commands/Image_Search.html
- screenshot settings include “Press Enter to capture” and allow moving/resizing selection via keyboard  
  Ref: https://www.macrocreator.com/docs/Settings.html

PMC Pixel Search includes:
- found/not found behaviors, auto-add IF statement blocks, output variables, “adjust coords to center”  
  Ref: https://www.macrocreator.com/docs/Commands/Pixel_Search.html

**Requirement:** v1 must implement:
- *Asset capture*: rectangle selection, keyboard nudge/resize, persistent overlay until confirm
- *Search actions*: image search, pixel search, pixel get color
- *Output variables*: foundX/foundY, confidence score, match region
- *Flow integration*: auto-wrap selected steps in IF found/not-found blocks

### 2.6 OCR (Image to Text)
PMC provides **Image To Text** and bundles Tesseract/leptonica, supports OCR from screen region, file, or URL.  
Ref: https://www.macrocreator.com/docs/Commands/Image_to_Text.html  
PMC also announced bundling OCR via Vis2 + tesseract.  
Ref: https://www.macrocreator.com/2020/09/22/version-update-5-2-0/

**Requirement:** v1 must include:
- OCR step: `ReadText(region) -> var`
- WaitText/assertions: wait until OCR matches regex/contains string
- (Nice-to-have but very practical) text targeting: `FindText` / `ClickText` by OCR bounding box (implemented as `OcrFindText*` + `ClickText`).
- (Nice-to-have) multi-match OCR targeting: `FindTextAll` / `OcrFindTextAll` to return all bboxes matching a pattern (useful for lists, grids) + `ClickTextAll`.
- (Nice-to-have) fuzzy text matching for OCR (`match: fuzzy`) to tolerate minor recognition errors.
- Language packs management UI (like PMC)

### 2.7 Variables, arrays/objects, expressions
PMC supports variables and arrays/objects; docs:  
Ref: https://www.macrocreator.com/docs/Variables.html  
Changelog mentions multi-dimensional arrays and named keys, methods, etc.  
Ref: https://www.macrocreator.com/docs/About.html

**Requirement:** v1 must include:
- variable types: string, number, bool, list, dict
- expressions: arithmetic, comparison, boolean ops, regex
- string functions, math functions
- interpolation in step parameters
- “watch variables” panel like PMC “List Variables” (Main window).  
  Ref: https://www.macrocreator.com/docs/Main.html

### 2.8 External functions / libraries
PMC can call functions from external AHK files (limited), and supports a “Standard Library File” auto-loaded in the Functions window.  
Ref: https://www.macrocreator.com/docs/Commands/Functions.html and https://www.macrocreator.com/docs/Settings.html

**Requirement:** v1 needs an **extension model**, even if minimal:
- user-defined functions (in chosen embedded language) callable from steps
- packaging/import of function libraries per project
- safe sandboxing boundaries (see security section)

### 2.9 Export & packaging
PMC supports:
- Export to AHK script; “Edit Script” quick export; not a full script editor  
  Ref: https://www.macrocreator.com/docs/Main.html
- Compile to EXE via Ahk2Exe (Windows-specific)  
  Ref: https://www.macrocreator.com/docs/Export.html

**Linux translation requirement:**
- Export macro project to:
  - a standalone “package” (zip) containing workflow + assets + dependencies metadata
  - optionally a single-file runnable artifact (AppImage-like) *later*
- “Headless run” mode: run macro at startup / via CLI (PMC has -a).  
  Ref: https://www.macrocreator.com/docs/Main.html

### 2.10 Scheduling
PMC can schedule macros via Windows Task Scheduler integration.  
Ref: https://www.macrocreator.com/docs/Main.html

**Linux translation requirement:**
- Scheduler integration for:
  - systemd timers (preferred)
  - cron (fallback)
- UI that generates/installs timer units or cron lines
- “silent mode” execution, with logs/notifications

---

## 3) What we’re copying from AHK (capabilities needed for “visual problem solving”)

AHK’s “visual” capabilities aren’t a single feature; it’s a **toolchain**:
- coordinate modes
- pixel and image search
- sending input
- waiting and branching
- target window selection
- control-level automation (when possible)

### 3.1 Visual primitives (must-have parity)
- **ImageSearch**  
  Ref: AHK v2 docs: https://www.autohotkey.com/docs/v2/lib/ImageSearch.htm
- **PixelSearch**  
  Ref: https://www.autohotkey.com/docs/v2/lib/PixelSearch.htm
  Related: AutoIt PixelSearch `step` parameter: https://www.autoitscript.com/autoit3/docs/functions/PixelSearch.htm
- **PixelGetColor**  
  Ref: https://www.autohotkey.com/docs/v2/lib/PixelGetColor.htm
- **CoordMode** (screen vs window vs client)  
  Ref: https://www.autohotkey.com/docs/v2/lib/CoordMode.htm

  (implemented: `CoordMode` step; today supports `target=pixel|mouse` and `mode=screen|window|client` using active-window geometry from i3/sway/Hyprland)

**Requirement:** in our studio, each step must carry:
- coordinate frame + region definition
- multi-monitor addressing and scaling awareness
- deterministic “what image did you use” asset linking + versioning

### 3.2 Control-level / background automation (when available)
AHK has ControlSend and ControlClick for sending inputs without taking focus.  
Refs:
- ControlSend: https://www.autohotkey.com/docs/v2/lib/ControlSend.htm
- ControlClick: https://www.autohotkey.com/docs/v2/lib/ControlClick.htm

**Linux translation requirement:**
- Accessibility-tier actions:
  - click widget by role/name/path
  - set text/value
  - invoke action (“press”, “activate”)
- X11 fallback actions:
  - focus window then click/type
  - background send when safe/possible (limited)

---

## 4) i3/X11-native automation requirements

### 4.1 i3 as the authoritative window manager API
Use i3’s IPC to:
- query tree/workspaces
- focus/move/resize/mark windows
- subscribe to events

Ref: i3 IPC docs: https://i3wm.org/docs/ipc.html

**Requirement:** Provide a “Window Selector Builder” that emits stable selectors:
- class/instance/title, window id, pid, etc.
- click-to-pick window
- show a preview of matched windows

### 4.2 Hotkey binding pitfalls and the --release pattern
i3 warns that tools (like xdotool) may fail on KeyPress because the keyboard is grabbed; `--release` runs after keys are released.  
Ref: https://i3wm.org/docs/userguide.html

**Requirement:** The studio must:
- generate recommended i3 `bindsym --release ...` lines for macros
- optionally manage bindings automatically (write config fragments / include files)
- provide diagnostics when grabs/conflicts occur

### 4.3 X11 input injection (Send, mouse)
xdotool explicitly uses X11’s XTEST extension to simulate keyboard/mouse input.  
Ref: https://github.com/jordansissel/xdotool  
XTest library docs describe `XTestFakeKeyEvent`.  
Ref: https://www.x.org/releases/X11R7.6/doc/libXtst/xtestlib.pdf

**Requirement:** Provide:
- robust key injection (including modifiers)
- mouse move/click/drag/wheel
- “humanization” options: random jitter, variable delays (optional)
- avoid event loops / re-trigger (AHK has SendLevel/#InputLevel; see PMC FAQ note)  
  Ref: PMC FAQ snippet: https://www.macrocreator.com/docs/Faq.html

---

## 5) The “Studio” (the real product)

### 5.1 Visual Inspector (more than Window Spy)
You want a single “Inspector” panel that can produce targets for any step.

**Inspector needs multiple backends, shown side-by-side:**
1) **i3 selector** (best for window scope)
2) **X11 window props** (WM_CLASS, title, pid, geometry)
3) **AT-SPI element tree** (best for UI structure)
4) **Vision assets** (best when structure isn’t available)

**Precedents worth copying:**
- dogtail includes an AT-SPI Browser (“sniff”) that lets you browse the desktop element hierarchy and highlights widgets.  
  Ref: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/5/html/5.5_technical_notes/dogtail  
  (Ubuntu tutorial also notes sniff highlights widgets briefly.)  
  Ref: https://wiki.ubuntu.com/Testing/Automation/DogtailTutorial

### 5.2 Recorder that “lifts” raw input into robust steps
Raw recordings are the starting point, not the end.
- Example: turn “click at 431,212” into:
  - focus window (i3 selector)
  - wait window visible
  - locate UI element (AT-SPI if possible, else image)
  - click element center
  - assert next state

**Required recorder modes:**
- raw capture
- structured capture (uses inspector hints)
- hybrid: record raw then “convert to structured” with suggestions

### 5.3 Workflow editor (visual)
You’re building a PMC-class editor:
- step list with columns (type, details, repeat, delay, comment/label)
- grouping/folding (PMC groups)  
  Ref: https://www.macrocreator.com/docs/Main.html
- drag/drop reorder
- multi-select edits
- find/replace in parameters (PMC has this)  
  Ref: https://www.macrocreator.com/docs/Main.html

**Must-have control-flow blocks:**
- If / Else If / Else (PMC has Else doc; it wraps blocks)  
  Ref: https://www.macrocreator.com/docs/Commands/Else.html
- Loops: repeat N, while/until, foreach list/dict
- Break/Continue
- Goto/Label (consider supporting, but heavily discourage vs structured flow)
- Try/Catch/finally (error handling)

### 5.4 “Script view” and round-tripping
PMC provides a preview script and quick export, but isn’t a full editor.  
Ref: https://www.macrocreator.com/docs/Main.html

**Requirement:**
- A readable “script view” of the workflow (DSL)
- Round-trippable with the visual editor (source of truth = workflow graph)
- “Edit in code” can exist, but must not break the model

### 5.5 Runner UX (beautiful execution)
- step-through with:
  - current step highlight in editor
  - overlay on screen (region boxes, matched image box, element highlight)
  - variable watch + call stack
  - breakpoints
- failure artifacts:
  - screenshot at failure
  - OCR text dump
  - matched candidates list
  - timing trace (“what was waited for, how long, retries”)

---

## 6) Visual automation engine (Image/Pixel/OCR) — requirements

### 6.1 Image asset management
SikuliX frames the core workflow as “capture images you want to act on / wait for”.  
Ref: https://sikulix-2014.readthedocs.io/en/latest/basicinfo.html  
It is “WYSIWYS: What You See Is What You Script.”  
Ref: https://sikulix.github.io/docs/

**Requirements:**
- asset library with:
  - name, tags, variants
  - captured region metadata (coord mode, window scope, monitor)
  - per-asset match settings (similarity threshold, scaling, grayscale, mask/ignore)
- one-click “recapture asset” and update references
- ability to store multiple reference images for one element (theme/DPI states)

### 6.2 Matching capabilities
Minimum:
- exact-ish template match with tolerance/threshold
- find best match vs find all matches
- search within region; region can be:
  - absolute (screen)
  - relative to window (client)
  - relative to last match (“find the label then click 20px right”)

Nice-to-have:
- scaling-aware matching (SikuliX supports general resizing factors)  
  Ref: https://sikulix-2014.readthedocs.io/en/latest/scripting.html
- masks / transparency / ignore-color areas (AHK ImageSearch users rely on Trans/variation patterns; community discussions reflect how important this is)  
  Ref example discussions:
  - https://www.autohotkey.com/boards/viewtopic.php?t=64543
  - https://www.autohotkey.com/boards/viewtopic.php?t=48401

### 6.3 Pixel primitives
- PixelGetColor (single sample) (implemented: `PixelGetColor` / `PixelGetColorFile`)
- PixelSearch (scan region) (implemented: `PixelSearch` / `WaitForPixel` + file-based variants; optional `step` stride, and waits cycle phases when `step>1`)
- PixelSearch FindAll / click-all (implemented: `PixelSearchAll` / `PixelSearchAllFile` + `WaitForPixelAll` + `ClickPixelAll`, with optional connected-component grouping)
- “Wait for pixel color change”
- “Wait for region to change” (SikuliX has observe concepts)  
  Ref: https://sikulix.wordpress.com/

### 6.4 OCR primitives
PMC’s OCR relies on bundled tesseract and exposes OCR() as callable.  
Ref: https://www.macrocreator.com/docs/Commands/Image_to_Text.html

Requirements:
- OCR region selection with the same capture tooling as image search
- multi-language OCR
- normalization options (trim, replace, regex)
- “assert/branch on OCR output”

---

## 7) Accessibility (AT-SPI) automation — requirements

### 7.1 AT-SPI Browser (“sniff”) style tool
dogtail includes Script Recorder and AT-SPI Browser (“sniff”).  
Ref: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/5/html/5.5_technical_notes/dogtail

**Requirements:**
- browse app → window → element tree
- show roles/names/states/attributes/actions
- click node highlights it in real UI (like dogtail)
- copy selector to clipboard
- generate a robust selector:
  - path-based with fallbacks
  - attribute-based (role+name+index)
  - bounding box fallback → vision fallback

### 7.2 Accessibility actions
- click/activate element
- set text/value
- read text/value/state
- wait until element exists/visible/enabled
- “assert equals/contains”

---

## 8) Action catalog (what you need to ship)

PMC advertises “nearly 200 commands and functions.”  
Ref: https://www.macrocreator.com/

Below is a Linux/i3/X11-focused catalog.

### 8.1 Triggers & events (VHK core)
- hotkey pressed
- hotstring typed
- timer / schedule tick
- window focused/created/destroyed (i3 events)
- clipboard changed
- file changed (watch)
- image appeared/disappeared (vision observe)
- OCR text match appeared

### 8.2 Input (keyboard)
- send text (unicode)
- send key sequence
- key down / key up
- key chord / key sequence mode (“leader key”)
- set key delay / send speed
- block input / pass-through toggles
- remap key (layer system, optional v2)

### 8.3 Input (mouse)
- move to (x,y) with coord mode
- click/double click/right click/middle
- drag
- wheel
- relative movement
- “click found image center”
- “click element center”

### 8.4 i3 window/workspace actions
- focus window by selector
- move/resize container
- move to workspace; rename workspace
- mark/unmark; focus mark
- layout actions (split, tabbed, stacking)
- scratchpad show/hide
- “wait for window exists”
- query tree and store results

### 8.5 Vision actions
- find image → outputs (x,y,confidence)
- wait for image
- pixel get/search
- wait for pixel color / region change
- screenshot region to file
- OCR region/file/url

### 8.6 Clipboard & text processing
- read clipboard
- set clipboard
- paste from clipboard
- regex match/replace
- split/join/trim

### 8.7 Process & system
- run command (sync/async)
- kill process
- open URL
- notifications
- sound/beep

### 8.8 Filesystem
- read/write file
- append log
- copy/move/delete
- list directory
- watch file changes

### 8.9 UI helpers (prompts)
- message box / toast
- input box
- chooser / menu

### 8.10 Control flow & errors
- If/Else
- Switch
- loops (repeat/while/until/foreach)
- break/continue/return
- try/catch
- “retry step” on failure
- “timeout” wrapper

### 8.11 Observability
- log line
- structured event log
- screenshot-on-error
- trace timeline (waits/retries)

---

## 9) Project format & packaging

### 9.1 Project should include:
- workflows (multiple macros)
- hotkey/hotstring bindings
- shared libraries/functions
- assets (images, masks, OCR configs)
- settings (coord mode defaults, delays, retry policies)

### 9.2 Recommended internal model
- A workflow is a **graph** (even if displayed as a list):
  - nodes = steps
  - edges = next / branches / loops
- UI uses list view for linear flows but supports blocks and subflows.

---

## 10) Reliability requirements (the “AHK feel”)

### 10.1 Waiting is default
Every step should have:
- implicit waits (until target exists/ready)
- explicit wait actions
- timeouts and retry policies
- diagnostics

### 10.2 Explainability
The runner must be able to answer:
- Which window did I target?
- Which locator matched? (AT-SPI vs image vs fallback)
- What was the confidence?
- What changed between attempts?

---

## 11) MVP recommendation (to get to “wow” fast)

### MVP-0
- i3 IPC integration (focus/move/query)
- hotkeys via i3 bindsym template generation (`--release`)  
  Ref: https://i3wm.org/docs/userguide.html
- basic step editor (list + parameters)
- run/stop/pause
- screenshot capture rectangle tool

### MVP-1 (first AHK-like release)
- image search + wait for image
- pixel get/search + wait
- OCR region -> variable (tesseract)
- variables + IF/ELSE
- overlays + step-through debug

### MVP-2 (hard-problem capable)
- AT-SPI browser + selectors
- element click/set text/read state
- robust “auto-lift” recorder mode
- packaging + scheduled runs

---

---

## 12) Additional “clearly belongs” features (fresh dig)

This section captures **notable PMC/VHK-class behaviors** that weren’t fully spelled out above, but are important if we want parity with what makes PMC/AHK practical day-to-day.

### 12.1 Action palette taxonomy (PMC Command Windows table-of-contents)
PMC’s own Command Windows TOC is basically a **battle-tested category system** for the action palette. We should mirror this “shape” (even if implementations differ on Linux), because it matches how users think.  
Ref: https://www.macrocreator.com/docs/Commands.html

**PMC categories we should include as top-level palette groups:**
- Mouse (click/move/drag/wheel; click vs “SendEvent” fallback; random coordinate offset; relative clicks) — https://www.macrocreator.com/docs/Commands/Mouse.html
- Text (send text / paste / typing modes)
- Control (structured/background interaction where possible)
- Pause / KeyWait (wait for time, wait for key state)
- Message Box (message/confirm/input) with options like always-on-top/cancel/icon (see changelog) — https://www.macrocreator.com/docs/About.html
- Window (wait/activate/move/resize + window selection helpers)
- Image Search / Pixel Search / Image-to-Text (OCR)
- Run / File / String / Misc. (grab-bag “system primitives”) — https://www.macrocreator.com/docs/Commands/Run.html
- Loops (generic) + Loop FilePattern + Loop Parse + Loop Read + Loop Registry
- While-Loop, For Loop, Until
- Goto / Gosub, Label (legacy control-flow)
- Set Timer
- If Statements
- Variables / Arrays
- Functions / Array Methods
- Send Email
- Download Files
- Zip/Unzip Files
- “Internet Explorer / COM / PostMessage” groups (Windows-specific in PMC; see §12.7 for Linux mappings)

**Translation for i3/X11:** keep the same **mental model** even if the backends differ:
- “Control” becomes **AT-SPI first**, then “focus+vision,” then (optionally) X11 message hacks.
- “IE/COM” becomes **browser automation connectors** (WebDriver/DevTools) as optional plugins.

### 12.2 Recorder power-features that matter in practice
PMC’s recorder has several options that are small individually, but collectively make macros *usable*:
Ref: https://www.macrocreator.com/docs/Record.html

**Add these explicitly:**
- **Timed Intervals** recording (records idle time between actions for “precise replay”), with a **minimum delay threshold**.
- **Mouse Moves** sampling controls, including “minimum idle before recording the last move.”
- **Relative Record Key**: while a key is held (or toggled), mouse moves/clicks are recorded **relative to the initial position** (great for drag/draw).  
- Record **Window Class** and **Window Title** changes during recording (for later window scoping).
- Capture key down/up **for all keys** (not just modifiers) via “Capture key state (Down/Up).”
- Options to attempt **ControlSend / ControlClick** capture during record (even if imperfect), because it teaches users about “backgroundable” steps vs not.

### 12.3 Coordinate modes and multi-monitor/DPI: make it a first-class UX
PMC treats mouse coordinate mode as a global project decision and calls out “wrong coords” as a common pitfall:
- Settings: “Mouse Coordinates… active window, screen or client area” — https://www.macrocreator.com/docs/Settings.html
- FAQ: “Why am I getting wrong mouse coordinates?” — https://www.macrocreator.com/docs/Faq.html
- Changelog repeatedly references DPI/multi-monitor fixes — https://www.macrocreator.com/docs/About.html

**Add these requirements:**
- Project-level **CoordMode defaults** (screen/window/client), plus per-step overrides.
- Explicit **monitor + scaling** awareness:
  - per-monitor DPI / scaling differences
  - XRandR geometry changes while running
- “Target preview” overlays that show the coordinate frame you’re using *before* you run.

### 12.4 Screenshot tool quality-of-life (this is tooling, not a bonus)
PMC’s screenshot/area capture tooling is a big part of why its image/pixel search is usable:
Ref: https://www.macrocreator.com/docs/Settings.html

**We should include:**
- Configurable **draw button**, **line width**, **rectangle color**
- “Capture on release” *and* “Press Enter to capture” modes
- Keyboard nudge/resize of the selection:
  - Ctrl+Arrow to move
  - Shift+Arrow to resize
- A default screenshots directory and asset naming scheme
- “Screenshot options” button directly inside Image/Pixel/OCR command windows (PMC has this in changelog) — https://www.macrocreator.com/docs/About.html

### 12.5 Playback ergonomics: speed control, random delays, selected-row playback
From PMC changelog:
- “Random delays option for Playback”
- “Speed Control for exported scripts”
- “Play Selected Rows option”
- “Controls toolbar”
- “Manual play hotkey configurable”
Ref: https://www.macrocreator.com/docs/About.html

**We should include:**
- Playback speed slider (0.25×…4×) with hotkeys
- Optional randomization (“humanize”) on:
  - per-step delay
  - mouse coordinate offset (per mouse step) — https://www.macrocreator.com/docs/Commands/Mouse.html
- Run only:
  - selected steps
  - a block
  - from here
- A compact floating “controls toolbar” (record/play/pause/step/stop)
- “Run immediately” option for timers; timer start/stop controls

### 12.6 Hotkey capture robustness: virtual keys, key history, layout pitfalls
PMC explicitly provides:
- A **Virtual Keys** whitelist for what gets recognized during recording/capture
- A **Key History** workflow to discover VK/SC codes
Ref: https://www.macrocreator.com/docs/Settings.html

PMC FAQ also notes invalid hotkeys can stem from keyboard language/layout:
Ref: https://www.macrocreator.com/docs/Faq.html

**We should include:**
- A dedicated “capture a hotkey” dialog that:
  - shows physical key (scancode), symbolic key (keysym), modifiers
  - records device source if possible (keyboard A vs keyboard B)
  - detects conflicts immediately (and offers reassignment)
- A “key history / event monitor” panel for debugging input capture problems
- Layout-safe storage:
  - store both physical scancode *and* logical symbol, with a user toggle for “layout dependent” vs “layout independent”

### 12.7 “Windows-only” PMC features that still map cleanly to Linux
PMC includes IE automation, COM objects, PostMessage/SendMessage, registry loops.  
Ref: Command Windows list — https://www.macrocreator.com/docs/Commands.html

These still “belong” conceptually, but should be shipped as **Linux-native equivalents or plugins**:
- **D-Bus call** action (generalized IPC for desktop apps)
- **GSettings/dconf** read/write/iterate actions (registry-loop analog)
- **Web automation plugin**:
  - WebDriver (Selenium) or CDP (Chrome DevTools Protocol) workflows
- “SendMessage/PostMessage” analogs:
  - i3 IPC already covers WM-level actions
  - optional X11 client messages for power users (expert mode)

### 12.8 Editor UX: indentation, row colors, apply-without-closing, recent files
From PMC docs/changelog:
- “Show indentation for loops and statements” (toggle; double-click action header) — https://www.macrocreator.com/docs/Settings.html
- “shortcuts to paint selected rows with custom colors (Shift+1 to 0)” — https://www.macrocreator.com/docs/About.html
- “Apply button to command windows”
- “Recent Files submenu”
Ref: https://www.macrocreator.com/docs/About.html

**We should include:**
- Indented view + fold/collapse blocks
- Row color marks and comments/labels (for readability and debugging)
- Apply button in parameter dialogs (non-modal editing)
- Recent projects + autosave + crash recovery

### 12.9 Variable hygiene: avoid “reserved word” crashes (a real pitfall)
PMC warns that since it runs in the same AHK environment as user variables, naming collisions with internal variables can cause inconsistencies or crashes, and it recommends avoiding short/common names.  
Ref: https://www.macrocreator.com/docs/Variables.html

**We should include:**
- A namespaced variable system (`user.*`, `sys.*`, `step.*`) to avoid collisions by design
- Validation + linting for variable names
- A “reserved words” warning list (even if collisions are impossible, it helps imports)


### 12.10 Non-keyboard triggers: joystick/gamepad hotkeys
PMC added support for **Joystick Hotkeys** (useful for “gaming macro” workflows and for accessibility switches).  
Ref: https://www.macrocreator.com/docs/About.html

**We should include (Linux-native):**
- Gamepad button triggers
- Optional “device filter” (only this controller)
- Axis thresholds (e.g., LT > 0.7)

### 12.11 “Quality of life” project features that reduce friction
PMC includes a bunch of small but important usability features over time (from changelog):  
Ref: https://www.macrocreator.com/docs/About.html

**We should include:**
- Check for updates
- Recent files/projects
- Command windows with **Help (F1)** and context links
- “Apply” in command dialogs (edit without closing)
- Startup tips/help overlays (optional)

### 12.12 Permissions & environment diagnostics
PMC’s FAQ notes cases where macros/screenshots don’t work unless it’s run “as administrator,” and flags keyboard-layout-related “invalid hotkey” issues.  
Ref: https://www.macrocreator.com/docs/Faq.html

**Linux translation:**
- A “doctor” panel that checks and explains:
  - X11 access (DISPLAY, Xauthority)
  - capture/injection permissions
  - AT-SPI enabled and reachable
  - missing dependencies (OCR engine, etc.)
  - keyboard layout/keymap weirdness


## Appendix — Key references
Pulover’s Macro Creator:
- https://www.macrocreator.com/
- https://www.macrocreator.com/docs/

i3:
- https://i3wm.org/docs/userguide.html
- https://i3wm.org/docs/ipc.html

X11 input injection:
- https://github.com/jordansissel/xdotool
- https://www.x.org/releases/X11R7.6/doc/libXtst/xtestlib.pdf

AHK visual primitives:
- https://www.autohotkey.com/docs/v2/lib/ImageSearch.htm
- https://www.autohotkey.com/docs/v2/lib/PixelSearch.htm
- https://www.autohotkey.com/docs/v2/lib/PixelGetColor.htm
- https://www.autohotkey.com/docs/v2/lib/CoordMode.htm

SikuliX + dogtail:
- https://sikulix.github.io/docs/
- https://sikulix-2014.readthedocs.io/en/latest/basicinfo.html
- https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/5/html/5.5_technical_notes/dogtail

---

## 13) What other X11 macro tools teach us (low-hanging lessons to steal)

These aren’t “AHK-like studios,” but they solve the *mechanics* of recording, replaying, and visual targeting on X11. We should bake their lessons into our recorder/runner.

### 13.1 Synchronization is the hard part (XTEST alone isn’t enough)
The XTEST protocol itself explicitly notes it is **not intended** to support general journaling/playback, largely because synchronization between synthetic input and UI effects is difficult.  
Ref: https://www.x.org/docs/Xext/xtest.pdf

**Implication:** our runner must be “wait-driven,” not “sleep-driven.” Treat waits/retries/assertions as first-class, and auto-suggest them during recording/conversion.

### 13.2 Record more than input: record “readiness events” (Xnee approach)
GNU Xnee is explicit about why naïve record/replay fails: it records not just KeyPress/ButtonPress, but also protocol events/requests like **MapNotify**, allowing replay to be synchronized and avoiding “send keys before window is ready.”  
Refs:
- https://xnee.wordpress.com/documentation/introduction/technical-overview/
- https://www.freshports.org/x11/xnee/
- cnee manpage: https://manpages.ubuntu.com/manpages/focal/man1/cnee.1.html
- Linux Journal overview: https://www.linuxjournal.com/article/6660
- Xnee manual PDF: https://xnee.wordpress.com/wp-content/uploads/2012/10/xnee1.pdf

**Low-hanging fruit to implement:**
- During recording, capture:
  - active window changes + geometry
  - “window mapped/visible” milestones (MapNotify-like readiness proxies)
  - i3 events (window created/focused/moved)
- During replay, auto-insert:
  - `WaitWindow(selector, mapped=true)` before sending input
  - `WaitFocus(selector)` before typing
- Provide an “advanced recorder” mode that can optionally track X11 structure events (MapNotify, ConfigureNotify, etc.).  
  MapNotify background: https://tronche.com/gui/x/xlib/events/window-state-change/map.html

### 13.3 “Lexical macro recorders” (XMacro) are useful—but limited
XMacro (xmacrorec/xmacroplay) records and replays keyboard/mouse events using XTest.  
Ref: https://xmacro.sourceforge.net/

**Takeaway:** a simple lexical recorder is great for a quick MVP, but must be upgraded by the studio into:
- window scoping
- waits/synchronization
- robust targets (AT-SPI/image)

### 13.4 “Visual scraping” existed on X11 for years (xautomation + visgrep)
xautomation is a command-line suite that:
- uses XTest for input generation
- includes **visgrep**, which “greps for image in another image” and returns coordinates (a primitive ImageSearch).  
Refs:
- xautomation project page: https://www.hoopajoo.net/projects/xautomation.html
- package summary mentioning visgrep: https://linux.die.net/man/7/xautomation
- visgrep manpage: https://manpages.ubuntu.com/manpages/focal/man1/visgrep.1.html
- xte manpage: https://manpages.debian.org/stretch/xautomation/xte.1

**Low-hanging fruit to exploit immediately:**
- For early prototypes, implement ImageSearch by calling a “known-good” matcher (e.g., visgrep/OpenCV) behind the scenes.
- Keep the UX stable (asset capture, thresholds, regions) while the backend evolves.

### 13.5 Hotstring/Hotkey reality check (AutoKey)
AutoKey is a widely used Linux hotkey/hotstring tool on X11; it has active discussion/issue traffic highlighting:
- it’s fundamentally X11-oriented
- Wayland support is hard, with uinput often proposed as the workaround.  
Refs:
- Wayland/uinput discussion: https://github.com/autokey/autokey/discussions/598
- “Xorg application and will not function in a Wayland session” issue: https://github.com/autokey/autokey/issues/1061
- Hotkey grab behavioral differences X11 vs Wayland: https://github.com/autokey/autokey/issues/1005

**Takeaway:** even if v1 is i3/X11-only, we should:
- isolate capture/inject backends
- keep a path open for uinput-based backends later

---

## 14) Low-hanging fruit backlog (highest leverage, lowest complexity)

This is the “ship fast, feel powerful” list—features that create a lot of user value without requiring deep new research.

### 14.1 UX wins that are mostly glue
- **One hotkey = enter “Capture Mode”**  
  - click to pick window → i3 selector
  - drag to capture region → image asset
  - click element in AT-SPI tree → accessibility selector
- **“Convert recording to robust steps” wizard**  
  - find sleeps → recommend waits
  - find raw clicks → suggest image/AT-SPI targeting
  - detect window changes → auto-scope blocks

### 14.2 Debugger / runner polish (AHK “it just works” vibe)
- “Run selected steps / run from here” (PMC has this feature; it matters)  
  Ref: https://www.macrocreator.com/docs/About.html
- Always capture:
  - screenshot-on-failure
  - match candidates + confidence
  - the window selector that was used
- “Explain” view: **why** a selector matched, which fallback was used.

### 14.3 A “doctor” panel (save hours)
- Check and explain:
  - DISPLAY / Xauthority connectivity
  - ability to capture screen (screenshot)
  - ability to inject input (XTest)
  - AT-SPI available and enabled
  - OCR engine availability + language data
- Provide one-click fixes or copy/paste commands where possible.

### 14.4 “Macro snippets” (templates)
Ship a library of ready-to-customize workflows:
- “Wait for image → click → wait for next image”
- “Search pixel color → branch”
- “OCR a region → if regex match → notify”
- “i3: move focused window to workspace based on app class”
Templates are cheap and make the studio feel powerful immediately.

### 14.5 Asset recapture + theme/DPI resilience
- “Recapture all assets” mode (step through each image in the library)
- Allow per-asset variants (light/dark theme, DPI, localization)
- Quick test harness for an asset (“find it now” with overlay result)

### 14.6 Import/export & sharing (practical packaging)
- Export a macro “bundle”:
  - workflow JSON
  - assets (images/masks)
  - metadata (required deps)
- “Dry run” mode for imported bundles:
  - inspect steps and targets without executing
  - show required permissions/deps

### 14.7 Integrations that cost little but pay off
- i3: generate `bindsym --release` lines (recommended by i3 docs)  
  Ref: https://i3wm.org/docs/userguide.html
- Notifications via standard desktop mechanisms
- “Chooser/menu” step implemented via common launchers (rofi/dmenu) (implementation detail, but huge UX win)

---

## 15) “Be creative” feature ideas that still fit the low-hanging-fruit bar

These are “small inventions” that are mostly UI/flow work, not deep systems work.

### 15.1 Selector confidence meter
Show a live “robustness score” for a step target:
- AT-SPI selector present? Great.
- Image match with high similarity and small region? Good.
- Full-screen image search? Risky.
- Raw coordinates? Very risky.
Encourage users into better targets without lecturing.

### 15.2 Macro linting + autofix
A static analyzer that flags:
- sleeps with no waits
- unscoped clicks/typing (no window selector)
- image searches with huge regions
…and offers one-click fixes:
- wrap in WaitWindow/WaitImage
- suggest scoping block to active window during record

### 15.3 “Teach mode” during recording
While recording, show a subtle overlay:
- “This click could be: AT-SPI button ‘OK’ OR ImageSearch asset ‘ok_button.png’”
Let the user choose in the moment, creating robust scripts automatically.

### 15.4 A built-in “Inspector palette”
One panel with:
- window selector builder
- on-screen ruler / pixel color picker
- OCR preview
- AT-SPI tree browser
- image asset library
This reduces “tool hopping” and is uniquely valuable.

---

## 16) Research links added in this revision

- XTEST Protocol (limitations for journaling/playback): https://www.x.org/docs/Xext/xtest.pdf  
- GNU Xnee overview + synchronization motivation:  
  - https://xnee.wordpress.com/documentation/introduction/technical-overview/  
  - https://www.freshports.org/x11/xnee/  
  - https://manpages.ubuntu.com/manpages/focal/man1/cnee.1.html  
  - https://www.linuxjournal.com/article/6660  
  - https://xnee.wordpress.com/wp-content/uploads/2012/10/xnee1.pdf  
- XMacro: https://xmacro.sourceforge.net/  
- xautomation + visgrep/xte:  
  - https://www.hoopajoo.net/projects/xautomation.html  
  - https://linux.die.net/man/7/xautomation  
  - https://manpages.ubuntu.com/manpages/focal/man1/visgrep.1.html  
  - https://manpages.debian.org/stretch/xautomation/xte.1  
- AutoKey X11/Wayland/uinput lessons:  
  - https://github.com/autokey/autokey/discussions/598  
  - https://github.com/autokey/autokey/issues/1061  
  - https://github.com/autokey/autokey/issues/1005

---

## 17) Accessibility tooling: steal from Accerciser (AT‑SPI “Swiss Army Knife”)

Our doc already calls for a “sniff” / AT‑SPI browser (dogtail-style). The lowest-hanging upgrade is: **copy Accerciser’s feature shape**, because it’s a mature accessibility explorer built on AT‑SPI2 and explicitly supports custom plugin views.  
Refs:  
- Accerciser overview + plugin framework: https://github.com/GNOME/accerciser  (mirror)  
- Accerciser described as an interactive Python AT‑SPI explorer: https://manpages.ubuntu.com/manpages/focal/man1/accerciser.1.html  
- “Event monitor plugin” concept and filtering AT‑SPI events: https://thegnomejournal.wordpress.com/2007/06/24/exercising-your-application-with-accerciser/  
- Accerciser plugin list (interface viewer, validator, event monitor, API browser, IPython console): https://en.linuxadictos.com/accerciser-knows-a-program-to-carry-out-accessibility-tests.html  

### 17.1 “Accerciser parity” features to include in our inspector
- **Event Monitor** (filterable)
  - Show AT‑SPI events in real time (focus, state changes, text changes).
  - Filter by event type and by source subtree (selected app/window/widget).  
  - This directly supports our macro reliability goals: “wait until *this* event happens” instead of sleeps.

- **API/Interface Viewer**
  - For a selected widget, show:
    - supported interfaces
    - properties/attributes
    - available actions (“click”, “activate”, etc.)
  - One-click “generate step” from an action.

- **Quick selection / crosshair mode**
  - Keyboard shortcuts to pick the currently-focused widget and “pin” it into the tree.

- **Embedded console (REPL)**
  - Accerciser ships an IPython console plugin in some distros/articles; the *concept* is the win:
    - let power users poke the selected accessible object live
    - copy/paste snippets into custom function steps  
  - Even if we don’t ship Python, we should ship **a console** for our own runtime objects.

- **Validator**
  - Accerciser includes validator plugins; we can translate this into:
    - “Selector lint”: warn when a selector is fragile (uses index-only, deep paths, etc.)
    - “Accessibility lint”: warn when app doesn’t expose roles/names (help users choose vision fallback)

### 17.2 Low-hanging action types enabled by event monitoring
- **WaitA11yEvent(eventType, selector, timeout)**
- **WaitTextChanged(selector, contains/regex)**
- **WaitState(selector, enabled/visible/checked)**
- **OnA11yEvent(eventType, selector) -> run macro** (event trigger)

---

## 18) Vision automation: steal the SikuliX “Pattern/Region” model (it’s the right mental model)

SikuliX’s key design is: everything happens in a **Region**, and image assets become **Patterns** with parameters like similarity thresholds. It also supports waiting for images to appear/vanish and observing region changes.  
Refs:
- Region similarity notes: https://sikulix.github.io/docs/api/region  
- Pattern docs (default min similarity 0.7; Pattern associates image with attributes): https://sikulix-2014.readthedocs.io/en/latest/pattern.html  
- Observe feature (wait for appear/vanish or pixel changes; can run inline or in background): https://sikulix.wordpress.com/  

### 18.1 Add these “Pattern” knobs to our ImageSearch assets (low effort, huge payoff)
- **MinSimilarity** per asset (default ~0.7 like SikuliX).  
- **Search region** always explicit: full-screen search should be discouraged (slow + brittle).
- **Target offset**: click not necessarily center (e.g., click the “x” in a close button image).  
- **FindAll** mode: return all matches (useful for “click all checkboxes” macros).
  - Implemented (engine): `ImageSearchAll` / `ImageSearchAllFile` returning a list of matches.
  - Implemented (runner): `WaitForImageAll` (wait until N matches) and `ClickImageAll` (wait + click each match).
    Uses template-match thresholding + non-maximum suppression (NMS) to de-duplicate
    the overlapping detections that `matchTemplate` naturally produces.

### 18.2 Add these “Region” primitives
- **Observe / watch** a region:
  - wait for image appear
  - wait for image vanish
  - wait for region to change (pixel delta threshold)
- **Region-relative coordinates** as a first-class concept:
  - find image in region, then click at offset in same region

### 18.3 “FindFailed” UX (the thing that makes visual automation debuggable)
Sikuli users often struggle with “FindFailed” and similarity tuning; our studio should have an automatic “why didn’t it match?” debugger:
- show the screenshot of the region at failure
- show best match candidates + confidence heatmap
- suggest:
  - reduce similarity threshold
  - shrink search region
  - recapture asset
  - create an anchor (see §18.4)

### 18.4 Anchors: the simplest way to make image matching robust
Low-hanging, high impact:
- Allow a step to define an **Anchor** image.
- Subsequent image searches can be “relative to anchor’s match box”.
This reduces full-screen scanning and makes scripts theme/DPI-resilient.

---

## 19) “Visual assertions” (borrow from Ui.Vision RPA) — easy, powerful, test-like reliability

Ui.Vision’s visual UI testing commands (VisualAssert/VisualVerify/VisualSearch) emphasize that visual checks can validate whole regions and that their image comparison can be error-tolerant (ignore resolution/size/position differences).  
Ref: https://ui.vision/rpa/docs/visual-ui-testing

### 19.1 Add these step types (they’re low-hanging fruit)
- **VisualVerify(region, baselineAsset, tolerance, ignoreZones)**  
  Non-fatal; logs differences.
- **VisualAssert(region, baselineAsset, tolerance, ignoreZones)**  
  Fails macro if mismatch.
- **VisualSearch(region, asset) -> results**  
  Same as ImageSearch but packaged for “test style” flows.

### 19.2 Add “ignore zones” and “masking” to avoid flakiness
- Ignore timestamp areas, notification trays, cursor blinks, animations.
- Store ignore masks per baseline asset.

---

## 20) Data-driven macros (borrow the RPA world; cheap to implement, very high leverage)

Ui.Vision explicitly calls out CSV read/write and data-driven testing/workflows as a differentiator.  
Ref: https://ui.vision/rpa

### 20.1 Add a built-in “Data Table” panel
- import CSV → a table in the project
- macros can loop rows:
  - `ForEachRow(table)` with `${column}` parameter expansion
- export CSV logs (results, timestamps, screenshots path)

### 20.2 Low-hanging file actions that pair naturally with this
- Read/Write CSV
- Read/Write JSON
- Append log lines
- Save screenshots with templated names (`${macro}-${row.id}-${ts}.png`)

---

## 21) Portability and “project as folder” ergonomics (steal PMC’s portability trick)

PMC stores settings in INI files and supports “portable mode” by placing those files next to the executable (instead of user profile).  
Ref: https://www.macrocreator.com/docs/Settings.html

### 21.1 For our studio, make portability a first-class capability
- A project is a folder containing:
  - workflow definition
  - assets/
  - data/
  - logs/
  - settings.json (or ini)
- Provide “portable mode”:
  - store app config adjacent to the binary (opt-in)
- Provide “export project bundle” (zip) that round-trips cleanly.

---

## 22) Hotkey capture micro-UX (don’t underestimate this)

PMC hotkey capture has small but important UX decisions, e.g. Backspace clears hotkeys; press twice sets Backspace as the hotkey.  
Ref: https://www.macrocreator.com/docs/Playback.html

### 22.1 Apply this class of UX polish everywhere
- “Clear vs set” disambiguation for “special keys”
- immediate conflict detection + suggestions
- show “trigger context” live (which window selectors currently match)

---

## 23) Action catalog sanity check: Actiona proves what’s “minimum viable useful”

Actiona (Actionaz) is a cross-platform automation tool with a simple editor and optional JavaScript for customization. Its README lists a pragmatic action set (device emulation, pixel wait, image find, window wait/move/resize, file IO, clipboard, download, email, etc.).  
Ref: https://github.com/Jmgr/actiona

### 23.1 Use Actiona’s action list as a “reality filter”
If our v1 palette doesn’t include:
- wait for pixel color
- find image
- wait for window
- close/move/resize window
- clipboard read/write
- download file
- run/kill process
…then it won’t feel like a real macro studio.

---

## 24) Extra low-hanging “creative” features inspired by the above

### 24.1 “Event-based waits” wizard (Accerciser-inspired)
When a macro fails on timing, offer:
- convert sleeps into:
  - WaitA11yEvent
  - WaitImageAppear
  - WaitWindowMapped  
…and show a preview of the event stream in the inspector.

### 24.2 “Visual baseline builder” (Ui.Vision-inspired)
One click:
- capture baseline screenshot of region
- define ignore zones
- insert VisualAssert/Verify step

### 24.3 “Pattern tuning playground” (Sikuli-inspired)
For an image asset:
- interactive slider for similarity threshold
- live preview “match/no match” on current screen snapshot
- recommended default threshold saved per asset

---

## 25) Research links added in this revision

- Accerciser (AT‑SPI explorer + plugin framework): https://github.com/GNOME/accerciser  
- Accerciser manpage: https://manpages.ubuntu.com/manpages/focal/man1/accerciser.1.html  
- Accerciser event monitor concept: https://thegnomejournal.wordpress.com/2007/06/24/exercising-your-application-with-accerciser/  
- Accerciser plugin list (validator/event monitor/API browser/IPython console): https://en.linuxadictos.com/accerciser-knows-a-program-to-carry-out-accessibility-tests.html  
- SikuliX Region similarity: https://sikulix.github.io/docs/api/region  
- SikuliX Pattern docs: https://sikulix-2014.readthedocs.io/en/latest/pattern.html  
- SikuliX Observe feature: https://sikulix.wordpress.com/  
- Ui.Vision Visual UI Testing (VisualAssert/Verify/Search): https://ui.vision/rpa/docs/visual-ui-testing  
- Ui.Vision data-driven / CSV emphasis: https://ui.vision/rpa  
- PMC settings + portability: https://www.macrocreator.com/docs/Settings.html  
- PMC hotkey capture details: https://www.macrocreator.com/docs/Playback.html  
- Actiona action list: https://github.com/Jmgr/actiona

---

## 26) Input capture + hotkey/hotstring reliability: borrow from the “remapping daemon” world

If we want a “VHK/PMC studio” to feel like AHK, we need **rock-solid triggers** and (optionally) **true interception** for hotstrings and key layers. X11 grabs can work, but the Linux ecosystem has learned that the most reliable solutions live at the **evdev/uinput** layer.

### 26.1 Provide two backends (low effort, huge future-proofing)
1) **X11 backend** (easy; great for i3/X11 v1)
   - passive grabs for global hotkeys (and per-window hooks)
   - XInput2 raw events for capture/diagnostics (see §26.3)
2) **Kernel backend** (optional, but architect now)
   - intercept device events via **evdev**
   - re-inject via **uinput**
   - works across environments, and remains relevant if you ever touch Wayland later

### 26.2 Steal keyd’s shape for “global key logic”
**keyd** is a system-wide daemon that remaps keys using evdev/uinput, explicitly motivated by the fact that Linux otherwise requires a “medley of tools” and ends up tethered to a desktop environment. 

**Low-hanging fruit to copy:**
- a background daemon model (even if ours is user-level at first)
- clean separation of:
  - **capture** (inputs)
  - **interpretation** (hotkeys, sequences, layers)
  - **actions** (macros)
- “IPC hook” mindset: the daemon should be scriptable/extensible (keyd explicitly values this) 

### 26.3 Steal “RawKeyPress” for a great hotkey-capture UX
`xinput test-xi2 --root` shows RawKeyPress/RawKeyRelease plus KeyPress/KeyRelease for all sources, and it’s a great mental model for building a “Key History” panel. 

**Low-hanging features:**
- “Key History” / event stream panel (like PMC’s VK tools concept)
- store hotkeys as:
  - physical scancode + modifiers (layout-independent)
  - keysym + modifiers (layout-dependent)
- optional per-device binding (keyboard A vs B) for power users

### 26.4 Interception Tools: composable input pipelines (for hotstrings and device filtering)
**Interception Tools** provides `intercept` (capture to stdout) and `uinput` (re-inject from stdin), plus tools like `udevmon` to watch devices and run jobs. 

**Low-hanging fruit we should adopt:**
- “device-aware triggers” (“only this USB pedal triggers macro X”)
- a pipeline concept:
  - input → transform → output
- an internal “test harness” that replays captured input into the engine for debugging

---

## 27) Window control fallbacks: EWMH tooling is cheap leverage (wmctrl + xdotool)

Even on i3, it’s useful to have generic X11 window control fallbacks for:
- compatibility with non-i3 environments (test users)
- features outside i3’s model (some stacking hints, etc.)

### 27.1 wmctrl as a “universal window action” backend
**wmctrl** interacts with an EWMH/NetWM compatible X window manager and can list windows/desktops and request actions like activate, move/resize, maximize/minimize, sticky, above, etc. 

**Low-hanging action additions:**
- List windows/desktops (for selector debugging)
- Activate/close/move/resize
- Toggle always-on-top / sticky / fullscreen

### 27.2 xdotool as a proven primitive layer (and a warning label)
xdotool uses X11’s XTEST extension and other Xlib functions to simulate input and do basic window manipulation. 

But: sending input to background windows can be unreliable—some apps ignore synthetic events unless configured (or at all). 

**Low-hanging fruit we should implement:**
- per-step “must focus target first” toggle
- a “capability hint” in inspector:
  - “this app likely ignores background send; focus-first recommended”
- automatic fallback:
  - try background send → if no effect detected → focus-first retry (configurable)

---

## 28) Triggers beyond hotkeys: window events and “event-driven macros”

AHK feels powerful because it can respond to events. We can get a lot of that on X11 with minimal effort.

### 28.1 xdotool ‘behave’: window-event triggers we can mimic
xdotool includes a `behave` command that watches window events (mouse-enter, resize, etc.) and runs actions. 

**Low-hanging fruit:**
- “OnWindowEvent(selector, event)” triggers:
  - mouse-enter/leave
  - focus-in/out
  - resize/move
- a UI to attach these triggers to macros

### 28.2 Xnee’s biggest lesson: record “readiness” for synchronization
Xnee records not just user events but also X11 protocol events like **MapNotify**, enabling replay with synchronization. 

**Low-hanging additions:**
- record X11 window-state change events during capture (MapNotify, ConfigureNotify)
- auto-insert waits: `WaitWindowMapped`, `WaitWindowGeometryStable`
- show “readiness timeline” in debugger (what we waited for)

### 28.3 Distributed / multi-display macros (optional, but very cheap conceptually)
GNU Xnee can distribute events to multiple displays while recording/replaying. 

**Creative but low-hanging:**
- “Run on DISPLAY=:0 / :1” support for multi-seat or nested X servers
- remote-run via SSH wrapper (later), using the same project bundle format

---

## 29) Studio ergonomics: copy the “reload instantly” culture (sxhkd)

Fast iteration is half the magic. Hotkey daemons like sxhkd bake in “reload config” via signals, which is exactly the vibe we want for macro projects.

sxhkd supports reloading its config on SIGUSR1 (and toggling grabs on SIGUSR2). 

**Low-hanging features:**
- one-click “Reload project” (and bind it to a hotkey)
- “Safe reload”:
  - keep old bindings active until new config validates
- “Grab toggle” mode for debugging (“disable all hotkeys temporarily”)

---

## 30) Create an “X11 + i3 Doctor” that checks the real failure modes (cheap, saves hours)

These are common failure modes reflected across tooling communities:
- X connection/auth issues
- grabs conflicting
- apps ignoring synthetic events
- coordinate issues (multi-monitor, scaling)
- accessibility stack disabled

**Low-hanging checks and explanations (in plain English):**
- DISPLAY / Xauthority
- is XTEST available?
- can we screenshot?
- are AT‑SPI services reachable?
- are i3 IPC socket and subscriptions working?
- warn about “background send may not work in Chromium/terminals” style behavior 

---

## 31) Shortcut backends for early prototypes (ship UX first, swap engines later)

A recurring theme from older X11 automation tools is: **the primitives already exist**, but they’re not packaged into a studio.

- xautomation provides XTest-based input via `xte` and “visual scraping” via `visgrep` (find image in image, return coords). 
- xmacro can record/replay basic input events (a baseline lexical recorder). 

**Low-hanging strategy:**
- build the Studio UX + workflow model first
- implement early backends by calling known-good CLI tools (xdotool/xte/visgrep/wmctrl)
- replace internals over time without breaking the project format

---

## 32) Research links added in this revision

- keyd daemon motivation and evdev/uinput design: https://github.com/rvaiya/keyd   
- Interception Tools (intercept/uinput/udevmon): https://github.com/meicale/Interception-Tools   
- Interception Tools overview (ArchWiki): https://wiki.archlinux.org/title/Interception-tools   
- Interception Tools package description (lists intercept/uinput/mux/udevmon): https://launchpad.net/ubuntu/noble/+package/interception-tools   
- xinput test-xi2 RawKeyPress model: https://unix.stackexchange.com/questions/179901/how-to-capture-a-keyboard-shortcut   
- wmctrl description (EWMH window control): https://man.archlinux.org/man/wmctrl.1.en   
- xdotool man page (XTEST + EWMH support): https://manpages.ubuntu.com/manpages/trusty/man1/xdotool.1.html   
- xdotool behave (window-event trigger concept): https://github.com/jordansissel/xdotool/blob/master/cmd_behave.c   
- MapNotify event details: https://tronche.com/gui/x/xlib/events/window-state-change/map.html   
- Xnee synchronization via MapNotify: https://xnee.wordpress.com/documentation/introduction/technical-overview/   
- sxhkd reload on SIGUSR1: https://wiki.archlinux.org/title/Sxhkd

---

## 33) “Needles” and visual asset metadata: steal from openQA

openQA’s visual testing model is a goldmine for our “visual macro studio,” because it treats visual assets as **data + metadata**, not just a PNG. openQA uses *needles*: a PNG plus a JSON file with match areas, tags, and “exclude” zones to ignore unstable UI regions.

Refs:
- openQA docs on **exclude areas** in needle editor (red boxes; double-click to toggle exclude): https://open.qa/docs/  (search “Exclude areas”)  
- openQA current PDF docs mention **exclude areas** and **OCR areas** (orange boxes) for matching: https://open.qa/docs/current.pdf  
- Example explanation of needle = PNG + JSON metadata: https://tanjuachaleke.wordpress.com/2023/12/28/unraveling-the-needle-in-openqa-testing-a-tale-of-precision-and-visual-assertions/

### 33.1 Low-hanging fruit: adopt a “needle-like” internal format for our assets
For each visual asset, store:
- image file(s)
- metadata JSON:
  - **match areas** (one or more rectangles)
  - **exclude areas** / ignore masks
  - optional **OCR areas** (region where OCR is used instead of pixels)
  - tags / labels
  - expected DPI / scale range
  - min similarity / threshold defaults

This directly improves:
- robustness (avoid matching on animated/clock regions)
- debuggability (you know what region was meant to match)
- maintainability (“update needle” workflows)

### 33.2 Low-hanging UI: build a “Needle Editor”
- open asset → screenshot preview
- draw match areas + exclude areas (toggle by double-click, like openQA)
- test match against live screen or captured screen
- show confidence, best candidates, and a diff overlay when failing


---

## 34) Accessibility automation at scale: steal from LDTP + Mago

LDTP is an AT‑SPI-based desktop automation framework; Mago is a higher-level project built on top of LDTP to make tests consistent and maintainable.

Refs:
- LDTP tutorial PDF: https://ldtp.freedesktop.org/ldtp-tutorial.pdf  
- LDTP FAQ (“first test automation framework to use AT-SPI”): https://ldtp.freedesktop.org/wiki/FAQ/  
- LDTP source repo: https://github.com/ldtp/ldtp2  
- Mago overview (built on LDTP, consistent way of writing tests): https://wiki.ubuntu.com/Testing/Automation/Mago  
- Mago “how to write tests” guidance (wrappers, setup/teardown/cleanup): https://thegnomejournal.wordpress.com/2009/11/06/gnome-desktop-testing-automation-and-how-to-use-mago/

### 34.1 Low-hanging lesson: “App wrappers” are a maintainability multiplier
Mago’s recommendation is essentially:
- write an **application wrapper** once (selectors + common actions)
- write test suites / macros that reuse those wrappers

**For our studio:**  
Add a first-class concept of an **App Profile**:
- window selectors
- common UI element selectors (AT‑SPI + vision fallbacks)
- reusable actions (“open file”, “save”, “export”, etc.)
- stable “wait until ready” routines

Then your visual macros can be:
- mostly high-level steps calling profile actions
- less brittle to UI churn

### 34.2 Low-hanging UI: “Profile Builder”
- pick app window
- browse AT‑SPI tree
- capture a handful of key elements as named selectors
- optionally capture image fallbacks
- generate a reusable library automatically


---

## 35) Clipboard-driven automation: steal clipnotify + XFixes

AHK users love clipboard triggers (“copy this → do something”). On X11, you can get event-driven clipboard change notifications via XFixes. `clipnotify` is a tiny tool that blocks until clipboard selection changes and then exits, designed to avoid polling.

Refs:
- clipnotify repo (XFixes selection change): https://github.com/cdown/clipnotify  
- “Getting notified about clipboard content changes” discussion mentions clipnotify and PRIMARY vs CLIPBOARD nuance: https://unix.stackexchange.com/questions/651888/getting-notified-about-clipboard-content-changes  
- ArchWiki Clipboard page lists CLI tools and clipboard concepts: https://wiki.archlinux.org/title/Clipboard

### 35.1 Low-hanging features
- Trigger: **OnClipboardChange(selection=clipboard|primary)** → run macro
- Step: `GetClipboard`, `SetClipboard`, `PasteClipboard`
- “Clipboard inspector” panel:
  - show PRIMARY vs CLIPBOARD
  - show recent history (optional)
  - quick “copy variable to clipboard”

### 35.2 Low-hanging reliability detail: selection types
X11 has multiple “selections” (PRIMARY, CLIPBOARD, SECONDARY). Users frequently confuse them.
- Put the selection choice in the UI *explicitly*, with a default of CLIPBOARD (Ctrl+C/V).


---

## 36) Region selection as a primitive: steal slop + maim

A killer “studio feel” feature is an always-available, consistent region selection UX. Tools like **slop** (select operation) and **maim** (screenshot utility) prove how valuable it is: select a region or a window and get geometry back.

Refs:
- slop repo: https://github.com/naelstrof/slop  
- maim repo (supports interactive selection, window selection): https://github.com/naelstrof/maim  
- maim manpage (interactive selection mode): https://man.archlinux.org/man/extra/maim/maim.1.en

### 36.1 Low-hanging: “Capture Mode” should reuse one region selector everywhere
Use the same selector UI for:
- screenshot capture
- image asset capture
- pixel search region definition
- OCR region definition
- visual assertions baseline regions

### 36.2 Low-hanging: allow window picking as a region
slop supports “select an existing window” workflows; maim supports selecting a window before capture.
- This makes it trivial to say: “search only within this window’s client area” (critical for speed + reliability).


---

## 37) Visual scraping already existed: steal xautomation’s visgrep pipeline ideas

xautomation explicitly advertises “visual scraping,” and its `visgrep` tool finds an image inside another image and returns coordinates. That’s basically a minimal ImageSearch primitive.

Refs:
- xautomation homepage: https://www.hoopajoo.net/projects/xautomation.html  
- xautomation package summary (mentions “visual scraping” and XTest): https://www.freshports.org/x11/xautomation/  
- visgrep description and options: https://manpages.ubuntu.com/manpages/focal/man1/visgrep.1.html  
- older visgrep manpage notes scanning with offsets (useful anchor concept): https://rpm.pbone.net/manpage_idpl_135570578_numer_1_nazwa_visgrep.html

### 37.1 Low-hanging implementation strategy (again)
- Keep the Studio UX stable.
- For early versions, it’s totally acceptable to implement:
  - “find image” via OpenCV `matchTemplate` (see §37.2) or even calling visgrep behind the scenes.
- Replace backends later.

### 37.2 Low-hanging vision backend reference: OpenCV template matching
OpenCV’s template matching (`matchTemplate`) is the canonical baseline.
Ref: https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html

To make it more robust, multi-scale matching is a known trick:
Ref example walkthrough: https://pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/


---

## 38) Event-driven macros: steal Autopilot’s “assert internal state via DBus” mindset

Ubuntu’s Autopilot testing framework is a good conceptual model: simulate user actions, then verify internal state via introspection (DBus), written as Python unit tests.

Refs:
- Autopilot overview: https://wiki.ubuntu.com/Autopilot  
- Ubuntu Touch Autopilot testing page: https://wiki.ubuntu.com/Touch/Testing/Autopilot

### 38.1 Low-hanging translation for our studio
Introduce a plugin-style “Introspection step” that can:
- call DBus methods
- read DBus properties
- wait for a DBus signal

This lets you build automations that are both:
- user-visible (vision)
- structurally reliable (introspection)

Even if you don’t ship this in v1, **design the step model** so it fits later.


---

## 39) More low-hanging “creative” features inspired by the new research

### 39.1 “Needle refresh” workflow (openQA pain-point solved)
openQA users often have to update needles when fonts/antialiasing changes. We can make this less awful:
- detect which assets failed
- present a guided “update these 6 needles” flow
- keep old versions (asset versioning)
- diff view to show what changed

### 39.2 Accessibility-to-vision fallback generator (LDTP/Mago + openQA combo)
When you capture an AT‑SPI selector:
- automatically capture a small screenshot around it and store as a fallback needle
This is extremely low-hanging and makes scripts survive “accessibility gaps.”

### 39.3 Clipboard-powered micro-macros (clipnotify-inspired)
Ship templates:
- “Copy a URL → open it in a browser + add to notes”
- “Copy a file path → open terminal + cd there”
- “Copy a code block → run formatter”
…and encourage users to bind them to clipboard triggers.


---

## 40) Research links added in this revision

- openQA needles + exclude areas + OCR areas:
  - https://open.qa/docs/
  - https://open.qa/docs/current.pdf
  - https://tanjuachaleke.wordpress.com/2023/12/28/unraveling-the-needle-in-openqa-testing-a-tale-of-precision-and-visual-assertions/
- LDTP + Mago:
  - https://ldtp.freedesktop.org/ldtp-tutorial.pdf
  - https://ldtp.freedesktop.org/wiki/FAQ/
  - https://github.com/ldtp/ldtp2
  - https://wiki.ubuntu.com/Testing/Automation/Mago
  - https://thegnomejournal.wordpress.com/2009/11/06/gnome-desktop-testing-automation-and-how-to-use-mago/
- clipnotify + clipboard tooling:
  - https://github.com/cdown/clipnotify
  - https://unix.stackexchange.com/questions/651888/getting-notified-about-clipboard-content-changes
  - https://wiki.archlinux.org/title/Clipboard
- slop + maim region selection:
  - https://github.com/naelstrof/slop
  - https://github.com/naelstrof/maim
  - https://man.archlinux.org/man/extra/maim/maim.1.en
- xautomation/visgrep + OpenCV template matching:
  - https://www.hoopajoo.net/projects/xautomation.html
  - https://www.freshports.org/x11/xautomation/
  - https://manpages.ubuntu.com/manpages/focal/man1/visgrep.1.html
  - https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html
  - https://pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/
- Autopilot concept (introspection via DBus):
  - https://wiki.ubuntu.com/Autopilot
  - https://wiki.ubuntu.com/Touch/Testing/Autopilot

---

## 41) More “low-hanging fruit” learned from others online (X11+i3 edition)

This revision focuses on a set of **cheap additions** that consistently pay off in desktop automation: better asset semantics (“needles”), better capture UX (slop/maim), better triggers (clipboard events), and clearer realities about accessibility coverage.

### 41.1 Adopt openQA’s “needle” semantics (PNG + JSON) and steal its click-point trick
openQA’s documentation spells out three concepts that map *perfectly* to our studio:
- **Exclude areas** (ignore unstable regions; shown as red boxes in needle editor).
- **OCR areas** (regions matched via OCR; shown as orange boxes).
- **Click points** inside match areas (used by functions like `assert_and_click`).  
These are precisely the missing metadata that makes “visual automation” resilient.

Refs:
- openQA docs (exclude areas): https://open.qa/docs/
- openQA PDF (exclude areas, OCR areas, click points): https://open.qa/docs/current.pdf

**Add to our asset format (“needle-like”):**
- `match_areas[]` (rectangles; support multiple)
- `exclude_areas[]` (rectangles or masks)
- `ocr_areas[]` (rectangles with OCR params)
- `click_point` (per match area; relative x/y)
- tags, variants, DPI/scale expectations, similarity thresholds, anchors

**UI to build it (low-hanging):**
- a “Needle Editor” view with:
  - draw match/exclude/OCR areas
  - set click point
  - test match against live screen or last screenshot
  - “why didn’t it match?” diagnostics

**Bonus steal:** there’s already a Python needle editor project (“Needly”) for openQA which reinforces that “needle editing” is a real, useful workflow.
Ref: https://github.com/lruzicka/needly

### 41.2 Region selection UX: steal slop + maim concepts and make Capture Mode universal
**slop** is a tiny tool that grabs the mouse, lets the user drag a rectangle or click a window, and prints the selection geometry to stdout.  
Ref: https://www.mankier.com/1/slop

**maim** is a screenshot tool that supports predetermined regions/windows and interactive selection (it uses slop for selection visuals and settings).  
Refs:
- maim repo: https://github.com/naelstrof/maim
- maim man page (interactive mode uses slop): https://man.archlinux.org/man/extra/maim/maim.1.en

**Low-hanging product move:** implement a single, consistent **Capture Mode** overlay for:
- Image asset capture
- Pixel search region selection
- OCR region selection
- Visual assertions baseline capture
- “Ignore zone” and “Mask” drawing
- Window/monitor picking and “client-area only” capture

This makes the studio feel cohesive and dramatically reduces user frustration.

### 41.3 Clipboard triggers without polling: steal clipnotify
AHK users love “copy something → automation happens.”  
**clipnotify** is a simple program that uses the XFIXES extension to wait for a new selection and then exits (so you can loop it), specifically to avoid polling.  
Ref: https://github.com/cdown/clipnotify

There’s also a practical nuance from the community: clipnotify monitors PRIMARY events too (depending on how it’s built/used), which can be undesirable for “only Ctrl+C” workflows.  
Ref: https://unix.stackexchange.com/questions/651888/getting-notified-about-clipboard-content-changes

**Low-hanging features:**
- Trigger: `OnClipboardChange(selection=CLIPBOARD|PRIMARY)` → run macro
- Step: `GetClipboard`, `SetClipboard`, `PasteClipboard`
- “Clipboard inspector” panel:
  - show current PRIMARY vs CLIPBOARD
  - quick “copy var to clipboard”
  - optional history (can be deferred)

### 41.4 Reality check: accessibility coverage isn’t universal—plan graceful fallbacks
AT‑SPI2 is a protocol over D‑Bus used by toolkits to expose accessibility info.  
Ref: https://www.freedesktop.org/wiki/Accessibility/AT-SPI2/

In practice, not every app surfaces well through AT‑SPI. A concrete example: users have reported Firefox windows not appearing in AT‑SPI/Accerciser in certain setups.  
Ref: https://stackoverflow.com/questions/65946258/firefox-at-spi-support-in-ubuntu

**Low-hanging requirements:**
- The inspector should clearly show:
  - “AT‑SPI available for this app: yes/no”
  - if no: recommend vision fallback, and explain why
- Auto-generate accessibility→vision fallback needles:
  - when you pick an AT‑SPI element, also capture a small visual needle around it

### 41.5 “Visual scraping” predates modern tools: xautomation is proof, and it’s a great prototyping backend
xautomation is a suite that controls X via XTest and does “visual scraping”; it includes **visgrep** to find images inside images and return coordinates.  
Refs:
- xautomation homepage: https://www.hoopajoo.net/projects/xautomation.html
- xautomation man summary: https://linux.die.net/man/7/xautomation

A StackExchange answer highlights the exact value prop: XTest avoids certain problems where apps ignore sent events, and visgrep provides the coordinate-finding primitive.  
Ref: https://unix.stackexchange.com/questions/79226/interacting-with-x-applications-programmatically

**Low-hanging strategy (again):**
- Ship the Studio UX and workflow model early.
- Implement early backends by calling stable CLI tools:
  - visgrep for match coords
  - maim for screen capture
  - clipnotify for clipboard triggers
- Replace with native backends later without breaking projects.

### 41.6 Key input: copy the remapper-daemon mindset for robustness (optional v1, important architecture)
If you ever want “true interception” (hotstrings that don’t leak characters, layers, device filters), the Linux ecosystem solved it at evdev/uinput.
**keyd** is a prominent example: it’s a system-wide daemon that remaps keys using evdev/uinput because Linux otherwise needs a “medley of tools” and ends up tied to X11.  
Ref: https://github.com/rvaiya/keyd

Even if we do X11-only v1, our internal architecture should allow a second backend later.

### 41.7 Accessibility + vision fusion is a known best-practice (LDTP ecosystem hints at this)
The LDTP org has explicitly explored **integrating accessibility-based automation (LDTP/ATOMac) with image comparison automation (Sikuli)**.  
Ref: https://github.com/ldtp

This is effectively our core strategy:
- AT‑SPI when available
- vision when not
- unify inside one studio so users don’t need multiple tools

---

## 42) Small “creative” studio ideas enabled by the above (still low-hanging)

### 42.1 One “Needle-driven click” step type
A single step that:
1) asserts needle match
2) uses click point (or center) to click
3) captures failure screenshot + candidate matches

This replaces a common 3–5 step pattern and makes novices productive instantly.

### 42.2 “Clipboard macro packs”
Ship a pack of default macros triggered by clipboard changes:
- remove line breaks from copied PDFs
- auto-open copied URLs
- copy code → format via CLI tool  
(The AskUbuntu answer shows real people doing clipboard post-processing in bash already—our studio can make it friendlier.)  
Ref: https://askubuntu.com/questions/1167026/detect-clipboard-copy-paste-event-and-modify-clipboard-contents

### 42.3 “Capture everything” debugging hotkey
A global hotkey that, when pressed:
- dumps i3 tree snapshot
- captures screenshot of active monitor/window
- exports AT‑SPI subtree (if available)
- logs key history tail
This is massively helpful for bug reports and user support.

---

## 43) Better recording + “why this replay failed”: steal the X11 RECORD extension model

So far we’ve referenced XTest (inject) and Xnee (sync via MapNotify). The missing low-hanging piece is: **use the X11 RECORD extension** (or at least learn from its model) to build a more robust recorder and a better debugger.

### 43.1 RECORD is explicitly designed for journaling + synchronization
The X Record Extension protocol spec describes a recording/replay model where:
- you record “actions” (e.g., input events)
- you also record “consequence / synchronization information”
- and on playback you hold synthetic events until the matching sync condition occurs, often using **XTestFakeInput** to inject them.  
Ref: https://www.x.org/releases/X11R7.6/doc/recordproto/record.html

**Low-hanging implementation plan:**
- Offer a “Recorder Mode: Basic / Sync / Full Protocol”
  - **Basic**: hotkeys + input + i3 events (fast, low risk)
  - **Sync**: record window-state milestones (MapNotify/ConfigureNotify equivalents)
  - **Full Protocol** (expert): capture RECORD streams for gnarly apps
- In all modes, store a replay timeline that supports:
  - “pause until window is mapped/ready”
  - “pause until focus matches”
  - “pause until geometry stabilizes”

### 43.2 X Record library makes it practical
The X Record Extension Library spec notes the extension provides a mechanism for capturing **all events**, including input events that do not go to any clients.  
Ref: https://refspecs.linux-foundation.org/X11/recordlib.pdf

**Low-hanging debugger win:**
- When a macro fails, we can say:
  - “Your click didn’t land because the window wasn’t mapped yet”
  - “Your keystroke went to a different focused window”
…because we have an event timeline, not just sleeps.

---

## 44) Key capture + layout sanity: steal the xev/xmodmap culture for the “Doctor” panel

AHK users expect “KeyHistory” to be a one-click tool. On Linux/X11, people routinely use:
- `xev` to see X keycodes/keysyms
- `xmodmap` to remap keys
…and they often discover the keycode they need is the *X* keycode (not the kernel one).  
Ref: https://unix.stackexchange.com/questions/49650/how-to-get-keycodes-for-xmodmap

**Low-hanging studio features:**
- “Key History” panel that shows:
  - keycode
  - keysym
  - modifiers
  - device id (optional)
  - whether an event is synthetic (useful for debugging loops)
- “Layout/Mapping” helper:
  - show current XKB layout(s)
  - show warnings when a hotkey is layout-dependent
- “Capture hotkey” UI that stores:
  - physical (keycode/scancode-ish) binding option
  - symbolic (keysym) binding option

---

## 45) i3 window criteria & selector pitfalls: bake the known issues into the selector builder

### 45.1 i3’s own guide points users to xwininfo/xprop for window IDs/classes
The i3 User’s Guide references getting the X11 window ID via tools like `xwininfo`, and matching by X11 window class (WM_CLASS).  
Ref: https://i3wm.org/docs/userguide.html

### 45.2 The official “i3-get-window-criteria” script is great, and it documents a known quoting pitfall
The i3 FAQ points to a script that outputs all match criteria ready to copy/paste.  
Ref: https://faq.i3wm.org/question/2172/how-do-i-find-the-criteria-for-use-with-i3-config-commands-like-for_window-eg-to-force-splashscreens-and-dialogs-to-show-in-floating-mode.1.html

One widely shared version documents a real-world bug: quotes in WM_NAME fallback aren’t escaped properly due to xprop output, with an upstream bug reference.  
Ref (script): https://gist.github.com/PetePriority/9589fcf1820a36dd000a

**Low-hanging product move:**
- Implement our own selector builder that:
  - escapes quotes correctly
  - shows “when matching too early” warnings (some window properties may not be set yet)
  - recommends a fallback strategy:
    - prefer WM_CLASS
    - optionally also match title (regex) if needed

---

## 46) Screenshot + annotation tooling: steal Flameshot’s UI (it’s exactly what we need)

Flameshot’s product pitch is basically our “Needle/Region Editor” feature list:
- arrows
- highlight
- blur/pixelate (perfect for ignore zones!)
- text
- drawing
- rectangle/circle borders
- counters
- solid boxes  
Ref: https://flameshot.org/

The Flameshot ArchWiki page also emphasizes interactive selection where you can move/resize the capture window (good capture UX patterns).  
Ref: https://wiki.archlinux.org/title/Flameshot

**Low-hanging requirements:**
- In our Capture Mode / Needle Editor, include:
  - blur/pixelate tool for privacy (logs, bug reports)
  - numbered counters (for documentation and step labeling)
  - rectangle/circle tools that can double as “ignore zones” and “match zones”
- Allow keyboard move/resize of the selection (Flameshot supports this pattern; it’s a major productivity win).  
Ref: https://www.howtogeek.com/devops/how-to-use-flameshot-a-linux-screenshot-tool/

**Low-hanging “creative” feature:**
- “Explain screenshot” generator:
  - user captures region
  - adds counters and callouts
  - studio auto-inserts a “comment block” in the macro with the annotated image embedded/linked

---

## 47) Add a “tool-interop” layer: embrace proven CLI tools as first-class adapters

A recurring low-hanging strategy: ship the studio UX now, and implement backends via stable tools, then replace internals later.

Concrete adapters that can be integrated early:
- **slop/maim**: region/window selection and screenshots
- **clipnotify**: clipboard triggers (no polling)
- **visgrep**: image search primitive (until OpenCV backend is ready)
- **xdotool/wmctrl**: input + window actions
- **xev/xinput**: debug key capture and device IDs

This adapter layer should be a formal module:
- “backend capability detection”
- “doctor panel checks”
- consistent logs (“which backend performed this step?”)

---

## 48) Research links added in this revision
- X11 Record protocol spec (sync model with consequences): https://www.x.org/releases/X11R7.6/doc/recordproto/record.html
- X Record library spec: https://refspecs.linux-foundation.org/X11/recordlib.pdf
- X keycodes vs showkey, xev for xmodmap: https://unix.stackexchange.com/questions/49650/how-to-get-keycodes-for-xmodmap
- i3 user guide (xwininfo/WM_CLASS references): https://i3wm.org/docs/userguide.html
- i3 criteria FAQ: https://faq.i3wm.org/question/2172/how-do-i-find-the-criteria-for-use-with-i3-config-commands-like-for_window-eg-to-force-splashscreens-and-dialogs-to-show-in-floating-mode.1.html
- i3-get-window-criteria script (quote escaping caveat): https://gist.github.com/PetePriority/9589fcf1820a36dd000a
- Flameshot features: https://flameshot.org/
- Flameshot ArchWiki: https://wiki.archlinux.org/title/Flameshot
- Flameshot selection keyboard controls (user-facing explanation): https://www.howtogeek.com/devops/how-to-use-flameshot-a-linux-screenshot-tool/

---

## 49) Window “rules” are automation too: steal devilspie2’s lifecycle model

A lot of what people use AHK for on Windows is “make windows behave.” On Linux/X11, **devilspie2** is a proven pattern:
- it’s a window-matching utility
- it runs scripted actions when new windows are created
- it uses Lua (making it easier to extend than the original devilspie)  
Refs:
- devilspie2 repo (debug FIFO mode): https://github.com/dsalt/devilspie2
- devilspie2 overview (window matching utility; Lua): https://www.freshports.org/x11-wm/devilspie2/
- explanation of Lua rewrite: https://daniel-haek.medium.com/fixing-a-good-old-notes-app-on-linux-with-devilspie2-34dddaa695d4

### 49.1 Low-hanging feature: “Rule Builder” inside the Studio
Add a “Rules” tab that can generate:
- i3 `for_window` rules (preferred in i3)
- optional devilspie2 Lua snippets (for users who already use it)
- optional “apply once” actions (run rule now to fix your current session)

The Rule Builder should reuse our Inspector:
- click a window → capture WM_CLASS, instance, title regex, role
- pick actions:
  - float, move to workspace, set geometry, mark, focus, sticky/above (fallback via wmctrl)
- provide *explainability*:
  - show which rules match which windows

### 49.2 Known limitation: “window-title changes” are a thing
devilspie2 primarily reacts to window creation, and users ask how to handle changing titles.  
Ref: https://unix.stackexchange.com/questions/771939/positioning-multiple-windows-with-devilspie2

**Low-hanging workaround feature in our studio:**
- add an “OnWindowTitleChanged(selector)” trigger (X11 property notify)
- allow rules to re-apply when title changes (useful for browsers, terminals, apps with dynamic titles)

---

## 50) Hotkey binding manager: copy xbindkeys’ auto-reload behavior

Even if i3 handles many bindings, users often want global hotkeys outside i3 (or for non-i3 environments). **xbindkeys** is a long-lived X11 hotkey daemon with practical features:
- watches config file and reloads when modified
- can be forced to reload with a HUP signal (`killall -HUP xbindkeys`)  
Refs:
- ArchWiki xbindkeys (auto-reload + HUP): https://wiki.archlinux.org/title/Xbindkeys
- official xbindkeys site (HUP reload): https://www.nongnu.org/xbindkeys/
- manpage note about reload/HUP: https://linux.die.net/man/1/xbindkeys

### 50.1 Low-hanging studio features
- A “Bindings” page that can:
  - generate i3 bindsym `--release` lines (for i3)
  - generate xbindkeys config lines (for generic X11)
- One-click “Reload bindings”
  - for i3: `i3-msg reload`
  - for xbindkeys: send HUP (or restart)  
- Conflict detection:
  - show duplicates and grabs that fail
- A “temporarily disable all hotkeys” toggle for debugging (sxhkd-like concept already noted earlier)

---

## 51) Better bug reports & debugging: steal the GIF/Video capture workflow (Peek + ffmpeg x11grab)

People love tools like **Peek** because they make it trivial to capture “what happened”:
- record a selected screen area
- export to GIF or WebM  
Ref: Peek repo “record screen areas”: https://github.com/phw/peek

And **ffmpeg x11grab** is the underlying “power tool” for capturing X11 regions.  
Ref: ffmpeg devices docs (x11grab region offsets): https://www.ffmpeg.org/ffmpeg-devices.html

A key reality: x11grab records the area you specify and does *not* follow a moving window.  
Ref: AskUbuntu note: https://askubuntu.com/questions/1316669/screen-recording-with-ffmpeg

### 51.1 Low-hanging studio feature: “Record evidence” toggle
In Runner settings:
- Record a GIF/WebM of:
  - the active monitor, or
  - a selected region (Capture Mode), or
  - the target window geometry at start (best effort)
- Save alongside logs and failure screenshots.

### 51.2 Low-hanging “Support Bundle”
One button exports:
- project bundle
- logs (structured timeline)
- last failure screenshot + candidate matches
- optional last-run GIF/WebM
- i3 tree snapshot
This is extremely helpful for collaboration and debugging user scripts.

---

## 52) Screenshot backend options: steal shotgun’s “fast + geometry” constraints

**shotgun** is a minimal X11 screenshot utility built to be faster than maim:
- outputs PNG to file or stdout
- masks off-screen areas on multi-head setups
- supports selections by window ID and geometry  
Ref: https://github.com/neXromancers/shotgun

### 52.1 Low-hanging studio decision
Keep the Capture Mode UX constant, but allow multiple screenshot backends:
- maim (common)
- shotgun (fast)
- native backend later

This supports:
- faster vision pipelines
- better multi-head correctness
- easy “pipe image to matcher” workflows

---

## 53) “Geometry as data”: export selection geometry everywhere (Flameshot issue as a hint)

There’s a long-standing request to let Flameshot’s GUI print selection geometry so it can replace slop.  
Ref: Flameshot issue requesting selection geometry output: https://github.com/flameshot-org/flameshot/issues/425

### 53.1 Low-hanging studio feature
Any time the user selects a region/window:
- store the geometry in the step
- allow “copy geometry string” / “paste geometry” operations
- show it in the inspector (with coordinate mode)

This makes it much easier to:
- reproduce issues
- parameterize regions
- share “templates” of regions

---

## 54) “Library backend” option: libxdo as a higher-performance xdotool core

`libxdo` is the library behind xdotool; it exposes simulation of keyboard/mouse input and window management via X11/XTEST + Xlib.  
Ref: Ubuntu libxdo-dev description: https://launchpad.net/ubuntu/noble/+package/libxdo-dev  
Also xdotool man page description: https://man.archlinux.org/man/xdotool.1.en

### 54.1 Low-hanging plan
Even if early prototypes call out to CLI tools, add an internal abstraction for:
- “X11 Input Provider”
- “X11 Window Provider”
…and allow swapping in a libxdo-backed implementation for:
- lower latency
- fewer shell-outs
- cleaner error handling

---

## 55) Low-hanging backlog additions (prioritized)

### P0 (tiny, immediate, compounding)
- Rule Builder (generate i3 rules; inspect + copy/paste)
- Binding manager with reload + conflict detection (i3 + xbindkeys outputs)
- “Support Bundle” exporter (logs + screenshot + i3 tree snapshot)
- “Record evidence” toggle (GIF/WebM) for macro runs

### P1 (high ROI, still cheap)
- OnWindowTitleChanged trigger (property notify)
- Multiple screenshot backends (maim/shotgun) behind a single interface
- “Copy geometry” everywhere (regions/windows/assets)
- libxdo backend option (incremental performance win)

### P2 (creative quality of life)
- A “rules learned from recording” wizard:
  - detect that user always moves/floats same window → suggest persistent rule
- A “macro share link” exporter:
  - bundle project + assets + minimal readme + thumbnail GIF

---

## 56) Research links added in this revision
- xbindkeys auto-reload and HUP reload:
  - https://wiki.archlinux.org/title/Xbindkeys
  - https://www.nongnu.org/xbindkeys/
  - https://linux.die.net/man/1/xbindkeys
- devilspie2 window matching and debug FIFO:
  - https://github.com/dsalt/devilspie2
  - https://www.freshports.org/x11-wm/devilspie2/
  - https://daniel-haek.medium.com/fixing-a-good-old-notes-app-on-linux-with-devilspie2-34dddaa695d4
  - https://unix.stackexchange.com/questions/771939/positioning-multiple-windows-with-devilspie2
- Peek (record selected screen areas, GIF/WebM):
  - https://github.com/phw/peek
- ffmpeg x11grab device docs:
  - https://www.ffmpeg.org/ffmpeg-devices.html
  - x11grab fixed-area caveat: https://askubuntu.com/questions/1316669/screen-recording-with-ffmpeg
- shotgun screenshot backend:
  - https://github.com/neXromancers/shotgun
- Flameshot geometry request:
  - https://github.com/flameshot-org/flameshot/issues/425
- libxdo (library behind xdotool):
  - https://launchpad.net/ubuntu/noble/+package/libxdo-dev
  - https://man.archlinux.org/man/xdotool.1.en

---

## 57) Prompt steps and “mini UIs”: steal zenity/YAD/kdialog/whiptail

AHK scripts often ship with tiny GUIs (“InputBox”, chooser menus, confirmations). On Linux, there’s a mature ecosystem of “UI from shell” tools that we can exploit early *even before* a full native UI runtime is built.

### 57.1 Provide a unified “Prompt Step” with pluggable backends
Implement one step type in the workflow model:

- `Prompt.Form(fields…) -> variables`
- `Prompt.Choose(list…) -> value`
- `Prompt.FileOpen / FileSave`
- `Prompt.Password`
- `Prompt.Notify`

Then let the runner pick the best available backend:

- **Zenity**: GTK dialogs from shell scripts. 
- **YAD**: “Yet Another Dialog,” a fork of Zenity, explicitly designed for shell scripts and supports forms; documented as a Zenity fork. 
- **kdialog**: KDE/Qt dialogs from shell scripts (great for KDE users). 
- **whiptail/dialog**: TUI pseudo-graphical prompts (useful on minimal setups/SSH). 

### 57.2 Low-hanging UX: “Forms” are a big deal
A common request is multi-field forms; community answers point to YAD and zenity’s forms-like options. 

**Studio feature:** a Form Designer UI that generates a Prompt.Form step:
- text inputs
- dropdowns
- checkboxes
- file pickers
- validation rules (regex / required)

---

## 58) Clipboard power: integrate ideas from CopyQ and clipmenu

Instead of reinventing clipboard history and scripting, we can learn from (and optionally interop with) existing clipboard managers.

### 58.1 CopyQ: scripting + command line is exactly what macro users want
CopyQ is explicitly an “advanced clipboard manager with editing and scripting features,” and it provides a command line + scripting interface.   
Its docs include a full scripting API to “automatically handle clipboard changes” and more. 

**Low-hanging studio features inspired by CopyQ:**
- A “Clipboard tabbed history” panel (optional v1, but huge QoL)
- “Clipboard rules”:
  - when clipboard matches regex → transform → store
  - when clipboard changes → trigger macro
- A “Command import” idea: CopyQ has a commands repo and an easy “Paste Commands” workflow.   
  We should support “Paste Macro” (clipboard contains a macro bundle / YAML) → import.

### 58.2 clipmenu: lightweight history + XFixes monitoring + dmenu/rofi
clipmenu’s daemon **passively monitors X11 clipboard selections using XFixes (no polling)** and stores items to disk.   
It’s designed to pair with dmenu/rofi style launchers. 

**Low-hanging interop idea:**
- Support “Use clipmenu as clipboard backend”:
  - read history items
  - trigger macros on “selected from history”
- Or just copy its architecture: passive monitor + store + index.

---

## 59) Minimal X11 window primitives: steal wmutils/core as a backend option

wmutils’ core explicitly frames itself as “a set of tools for X windows manipulation,” where each tool does one thing to stay flexible and reliable. 

**Low-hanging value:**
- Use wmutils tools as an early backend for:
  - focused window id (`pfw`)
  - window attributes (`wattr`)
  - list windows (`lsw`)
  - move/resize (`wtp` etc. depending on toolset)
- Great for prototyping and for minimal environments.

---

## 60) Idle/lock/unlock triggers: steal xidlehook/xprintidle + xss-lock patterns

A huge class of “automations” are *time/idle driven* (dim lights, start focus mode, lock, pause macros, etc.). X11 has established tooling here.

### 60.1 OnIdle triggers with xidlehook/xprintidle
- **xprintidle** queries X server idle time and prints milliseconds. 
- **xidlehook** is a general-purpose replacement for xautolock that executes commands after idle thresholds. 

**Low-hanging studio features:**
- Trigger: `OnIdle(minutes=…)` → run macro
- Trigger: `OnActive()` after idle → run macro
- “Idle guard” options:
  - don’t fire when fullscreen / audio playing (xidlehook advertises such improvements vs xautolock) 

### 60.2 OnLock/OnUnlock triggers (xss-lock / session lock hooks)
xss-lock hooks a locker to the MIT screen saver extension and can integrate with systemd logind. 

**Low-hanging studio features:**
- Trigger: `OnSessionLock` / `OnSessionUnlock`
- Use cases:
  - pause macros on lock
  - clear sensitive clipboard
  - stop “always-on” hotkeys while locked

---

## 61) Ultra-low-hanging “creative” studio features unlocked by the above

### 61.1 A “Chooser” step backed by clipboard history
If you implement clipboard history (CopyQ/clipmenu-inspired), you get:
- `ChooseFromClipboardHistory(filter=regex)` → set clipboard → paste
This becomes a universal “snippet picker” and reduces typing in macros.

### 61.2 “Macro snippets” that generate rules automatically (devilspie2 lesson)
When a macro repeatedly moves/floats a window at start, suggest:
- “Convert this to a window rule”
and generate an i3 `for_window` rule or a rule macro.

### 61.3 “Project portability” with prompt backends
A project can declare:
- requires Prompt backend = {zenity|yad|kdialog|whiptail}
and the Doctor can check availability and propose install commands.

---

## 62) Research links added in this revision
- Zenity dialog concept: https://www.tecmint.com/zenity-create-gtk-dialog-boxes-in-linux/   
- YAD manpage (fork of zenity): https://man.archlinux.org/man/extra/yad/yad.1.en   
- kdialog docs: https://develop.kde.org/docs/administration/kdialog/   
- whiptail overview: https://en.wikibooks.org/wiki/Bash_Shell_Scripting/Whiptail   
- CopyQ scripting API: https://copyq.readthedocs.io/en/latest/scripting-api.html   
- CopyQ command line: https://hluk.github.io/CopyQ/   
- clipmenu passive monitoring with XFixes: https://github.com/cdown/clipmenu   
- wmutils core: https://github.com/wmutils/core   
- xprintidle: https://github.com/g0hl1n/xprintidle   
- xidlehook: https://github.com/jD91mZM2/xidlehook   
- xss-lock description: https://www.freshports.org/x11/xss-lock/

---

## 63) Add a “flow language” (text DSL) alongside the visual builder: steal TagUI’s approach

A visual editor is the main product, but **text mode** is incredibly valuable for:
- quick edits (search/replace, diff/merge)
- copy/paste sharing (“send me the flow”)
- generating flows from templates or AI later
- git-friendly reviews

**TagUI** is a strong precedent: it uses a simple “human language” of steps like `click` and `type`, and allows targeting web identifiers, image snapshots, screen coordinates, and even text via OCR. It also emphasizes cross-platform operation and a “turbo mode” to run much faster than normal human speed.  
Ref: TagUI README (language + identifiers + OCR + turbo): https://github.com/aisingapore/TagUI

### 63.1 Low-hanging feature spec
- Provide a “Flow” tab (text) that round-trips with the visual editor:
  - each visual step has a stable textual form
  - the visual editor remains the source of truth, but diffs are readable
- Include a minimal grammar:
  - `click <target>`
  - `type <target> as <text>`
  - `wait <condition>`
  - `if <expr> … else …`
  - `for each row in <table>`
- Targets can reference:
  - window selectors (i3 criteria)
  - accessibility selectors
  - needle assets
  - coordinates / regions
  - OCR text matches

### 63.2 “Turbo mode” for playback
TagUI calls out a dedicated turbo mode for speed.  
Ref: https://github.com/aisingapore/TagUI

**Our translation:** “Turbo mode” is simply a runner profile:
- no smooth mouse moves
- reduced default delays
- stricter use of waits/assertions (so speed doesn’t create flakiness)
- optional “type via clipboard paste” for large text

### 63.3 Cheap IDE integration
TagUI ships syntax highlighting via editor plugins (e.g., VS Code extension) as a distribution strategy.  
Ref: TagUI README mentions VS Code extension: https://github.com/aisingapore/TagUI

**Low-hanging for us:**
- ship a TextMate grammar + VS Code extension for our DSL
- ship snippets for common patterns (“wait image then click”)

---

## 64) “Interactive console” for macros: steal KWin’s live scripting console concept

KWin scripting provides an interactive console where you can send a script to the window manager and it is loaded and executed immediately, but only persists while the WM is running. It also has a packaging model with `metadata.json`.  
Ref: KWin scripting tutorial (interactive console + packaging/metadata): https://develop.kde.org/docs/plasma/kwin/

### 64.1 Low-hanging studio feature
Add a “Console” tab in the Studio:
- run one-off commands (“focus this window”, “dump selectors”, “test needle match”)
- shows results + logs immediately
- you can “promote” a console snippet into a macro step or a reusable function

### 64.2 Packaging metadata: steal the `metadata.json` discipline
KWin scripts require metadata with name/description/id/version/license/website.  
Ref: https://develop.kde.org/docs/plasma/kwin/

**Low-hanging requirement:** every macro bundle should include:
- `id`, `name`, `version`
- authorship + license (optional)
- required capabilities/backends (vision, a11y, clipboard triggers)
- UI icon + category tags

This enables:
- searchable template libraries
- safe import checks (Doctor can validate deps)
- eventually a “macro gallery” experience

---

## 65) Unicode and “typing that actually works”: add alternate text injection backends (xvkbd + clipboard)

A common failure mode of synthetic key injection is **Unicode / layout mapping weirdness**. On X11, tools like **xvkbd** exist specifically to send characters to other clients, including characters specified via command line options.  
Ref: xvkbd manpage: https://manpages.ubuntu.com/manpages/xenial/man1/xvkbd.1.html

### 65.1 Low-hanging runner feature
Create a “Type Text (robust)” step that can choose among:
1) XTEST key injection (normal typing)
2) clipboard set + paste (fast for large Unicode text)
3) xvkbd text injection (fallback for apps that mis-handle XTEST or keyboard mappings)

And expose it as:
- “Typing Backend” = auto / xtest / paste / xvkbd
- “Max safe chunk size” for paste

---

## 66) Event watchers as first-class tools: steal wmutils/opt wew (X event watcher)

The wmutils ecosystem includes an “opt” set that contains **wew**, an X event watcher used by power users to build bespoke automation and window management scripts.  
Ref: z3bra blog mentions wew as an X event watcher used with wmutils: https://blog.z3bra.org/2015/01/you-are-the-wm.html

### 66.1 Low-hanging studio feature
Add an “Event Stream” panel (like KeyHistory, but for windows):
- show X11 window events (map/unmap, configure, property notify)
- filter by selected window
- allow one-click “make trigger from this event”:
  - OnWindowMapped
  - OnWindowTitleChanged
  - OnWindowPropertyChanged

This will immediately improve:
- recorder synchronization
- trigger richness
- debugging (why did focus change?)

---

## 67) Clipboard ownership & persistence: treat it as a requirement, not a bug

On X11, clipboard selections are owned by a process; when that process exits, clipboard content can disappear unless a manager persists it. Tools like clipmenu emphasize passive monitoring and persistence to storage.  
Ref: clipmenu README (passive monitor + store/index): https://github.com/cdown/clipmenu

### 67.1 Low-hanging user-facing improvements
- In the Doctor panel, detect whether a clipboard manager is running (best-effort).
- Provide “Persist clipboard” option:
  - integrate with CopyQ/clipmenu if present
  - or implement a minimal “clipboard keeper” mode in our daemon
- In the clipboard inspector, show:
  - which selection we’re using (PRIMARY/CLIPBOARD)
  - whether it is currently owned by an app that is about to exit (best-effort)

---

## 68) Add “click points” and multi-click-point selection to needles (openQA shows why)

openQA needles can include **multiple click points**, each with an `id`, and the docs note that if a needle has multiple click points, you must pass it to select which click point to use.  
Ref: openQA current PDF: https://open.qa/docs/current.pdf

### 68.1 Low-hanging needle editor features
- Allow multiple click points per match area
- Allow naming click points (“ok_button”, “close_x”, “dropdown_arrow”)
- Allow step to specify:
  - click point by id
  - or “center” as default
- In debug overlay, show click point markers

---

## 69) Low-hanging backlog updates (what to build next)

### P0 (fast, compounding)
- Needle editor v1: match areas + exclude areas + click points + “test match now”
- Universal Capture Mode overlay used everywhere
- Console tab: run one-off commands, promote to steps
- Robust Type step with paste/xvkbd fallback
- Event Stream panel (X window events) + “make trigger” action

### P1 (still cheap, high value)
- Flow DSL tab (round-trips with visual editor)
- Template library that ships in-app + import/export
- Bundle metadata manifest + capability checks in Doctor

---

## 70) Research links added in this revision
- TagUI (simple DSL, images/coords/OCR, turbo mode): https://github.com/aisingapore/TagUI  
- KWin interactive console + packaging metadata: https://develop.kde.org/docs/plasma/kwin/  
- xvkbd manpage: https://manpages.ubuntu.com/manpages/xenial/man1/xvkbd.1.html  
- wmutils power-user setup + wew watcher mention: https://blog.z3bra.org/2015/01/you-are-the-wm.html  
- clipmenu passive monitoring & persistence: https://github.com/cdown/clipmenu  
- openQA click points & multi-click-point behavior: https://open.qa/docs/current.pdf

---

## 71) Sandbox + CI runs: steal i3’s own testsuite (Xephyr/Xvfb) and make it a first‑class feature

A **huge** usability win is letting people run macros safely in an isolated desktop so they can:
- test without trashing their real session
- reproduce bugs reliably
- run “macro tests” in CI

### 71.1 i3 already solved “run a whole i3 session in a separate X server”
The official i3 testsuite spins up a **separate X server instance** (Xephyr) and starts an i3 instance with an appropriate config, collecting logs per run. It also notes that tests are run under **Xvfb by default**.  
Ref: https://i3wm.org/docs/testsuite.html

**Low-hanging Studio feature (“Run in Sandbox”):**
- Button: **Run Macro in Sandbox**
  - start Xvfb (headless) or Xephyr (visible, nested)
  - start an i3 instance with a known config
  - run the macro
  - collect:
    - i3 log
    - macro log + screenshots + match diagnostics
    - optional video/GIF evidence (Peek/ffmpeg ideas from v10)

### 71.2 i3 IPC socket gotcha: don’t let the sandbox steal your real I3SOCK
i3 determines the IPC socket path from (in order) `ipc-socket` config directive, `I3SOCK` env var, and a runtime-dir default; it also offers `--get-socketpath`.  
Ref: https://i3wm.org/docs/ipc.html

There is a known failure mode when nesting i3: the inner i3 inherits `I3SOCK` and can unlink/overwrite the outer session’s socket, breaking tools.  
Refs:
- https://github.com/i3/i3/issues/4108  
- https://github.com/i3/i3/issues/4381

**Low-hanging mitigations (do these by default in our sandbox runner):**
- explicitly **unset `I3SOCK`** in the sandbox environment
- set a sandbox-only socket via:
  - `ipc-socket <unique_path>` in the sandbox i3 config, **or**
  - export a unique `I3SOCK` before launching sandbox i3
- for any i3 IPC client we spawn inside the sandbox (i3-msg/i3-input), pass the socket path explicitly or rely on `--get-socketpath` when possible.  
(Manpages show `i3 --get-socketpath` exists.) Ref: https://man.freebsd.org/cgi/man.cgi?query=i3&sektion=1

### 71.3 “Macro as Test”: treat flows like testcases
Mirror i3’s model:
- each macro run creates a run folder
- “latest/” symlink points to the most recent run
- artifacts go in a deterministic place

This makes:
- debugging
- sharing repro bundles
- CI integration
…much easier.

### 71.4 Bonus: a “one command repro” script
Ship a generated shell script alongside Support Bundles:
- launches Xvfb/Xephyr
- launches sandbox i3 + the target app
- runs the macro
- dumps artifacts

(There’s precedent for ephemeral X server wrappers used for xdotool tests.)  
Ref: https://www.semicomplete.com/blog/geekery/headless-wrapper-for-ephemeral-xservers/

---

## 72) Advanced debugging mode: X protocol tracers (xtrace, xscope, xtruss)

When a macro doesn’t work, sometimes you need to answer:
- “Did the client receive my synthetic event?”
- “Did the server reject it?”
- “Which requests/events are flowing when I click?”

### 72.1 xtrace
`xtrace` fakes an X server, forwards connections to a real X server, and displays the communication (requests/replies/events/errors).  
Ref: https://manpages.ubuntu.com/manpages/trusty/man1/xtrace.1.html

**Low-hanging Studio integration:**
- “Trace this app during macro run” toggle:
  - launch the target app under xtrace inside the sandbox
  - store the trace in the Support Bundle
- This is great for diagnosing weird focus/mapping sequencing issues.

### 72.2 xscope
`xscope` sits between an X11 client and server and prints the contents of each request/reply/error/event; it can decode core protocol plus multiple extensions (useful for perf/debug).  
Ref: https://www.x.org/releases/X11R7.6-RC1/doc/man/man1/xscope.1.xhtml

**Low-hanging Studio integration:**
- offer xscope as an alternative tracer backend when xtrace isn’t available.

### 72.3 xtruss (newer, “easier to use” tracing)
xtruss is explicitly pitched as an easy-to-use X protocol tracing program, akin to strace/truss but for X11.  
Ref: https://www.chiark.greenend.org.uk/~sgtatham/xtruss/

**Low-hanging benefit:**
- make it the default “friendly trace” if installed; store output in run artifacts.

---

## 73) Make the inspector smarter with existing X11 tools (cheap but delightful)

Even if we eventually implement everything natively, a lot of mature CLI tools provide “instant power”:

### 73.1 Click-to-pick window ID via xdotool
Users often do:
- `xdotool selectwindow getmouselocation --shell` and then click the window.  
Ref: https://unix.stackexchange.com/questions/154546/how-to-get-window-id-from-xdotool-window-stack

**Low-hanging Studio feature:**
- “Pick a window” tool that:
  - returns window id (decimal + hex)
  - returns geometry + screen
  - converts to i3 criteria + wmctrl selectors automatically

### 73.2 Geometry acquisition UX
A common trick:
- `eval $(xdotool getmouselocation --shell)` to extract X/Y.  
Ref: https://askubuntu.com/questions/20530/how-can-i-find-the-location-on-the-desktop-of-a-window-on-the-command-line

**Low-hanging Studio feature:**
- “Copy geometry string”
- “Copy point” (x,y) with current coord mode
- “Copy window rect” (x,y,w,h)

---

## 74) Nested X server ergonomics: make Xephyr painless

Xephyr is a nested X server that runs as an X application (useful for isolated testing).  
Ref: https://wiki.archlinux.org/title/Xephyr

There are UX realities:
- Xephyr’s grab/ungrab keyboard/mouse behavior often uses a Ctrl+Shift grab toggle (and it can conflict with user keybindings).  
Ref example discussion: https://superuser.com/questions/280375/how-to-change-default-behavior-of-xephyr-for-capturing-and-releasing-keyboard-mo

**Low-hanging Studio UX:**
- when running Xephyr sandbox, show a small “Sandbox Help” overlay:
  - how to grab/ungrab input
  - how to exit sandbox safely
- allow custom grab toggle binding in sandbox settings

---

## 75) Research links added in this revision
- i3 testsuite (Xephyr + Xvfb; run folders): https://i3wm.org/docs/testsuite.html  
- i3 IPC socket path sources: https://i3wm.org/docs/ipc.html  
- i3 nested socket issues: https://github.com/i3/i3/issues/4108 and https://github.com/i3/i3/issues/4381  
- i3 `--get-socketpath` manpage snippet: https://man.freebsd.org/cgi/man.cgi?query=i3&sektion=1  
- Ephemeral X server wrapper idea: https://www.semicomplete.com/blog/geekery/headless-wrapper-for-ephemeral-xservers/  
- xtrace manpage: https://manpages.ubuntu.com/manpages/trusty/man1/xtrace.1.html  
- xscope manpage: https://www.x.org/releases/X11R7.6-RC1/doc/man/man1/xscope.1.xhtml  
- xtruss: https://www.chiark.greenend.org.uk/~sgtatham/xtruss/  
- xdotool pick window id trick: https://unix.stackexchange.com/questions/154546/how-to-get-window-id-from-xdotool-window-stack  
- xdotool `getmouselocation --shell` geometry trick: https://askubuntu.com/questions/20530/how-can-i-find-the-location-on-the-desktop-of-a-window-on-the-command-line  
- Xephyr ArchWiki: https://wiki.archlinux.org/title/Xephyr

---

## 76) Workspace “Projects”: steal i3’s layout saving + i3‑resurrect’s “programs.json” model

A lot of AHK use is basically **environment orchestration**: open a bunch of windows, place them, then automate inside them.
On i3/X11, there’s *very* strong prior art we should bake into the Studio.

### 76.1 i3’s official layout saving/restoring is already a macro use-case
i3’s docs explicitly describe layout saving/restoring as a way to automate complex layouts (example: a grid of terminals running diagnostics commands), and explains the canonical workflow using **i3-save-tree** and **append_layout**.  
Ref: https://i3wm.org/docs/layout-saving.html

Key details we should treat as requirements:
- `i3-save-tree --workspace N > layout.json` produces the layout skeleton.  
- The output is **not useful until you edit** it to specify matching criteria (“swallow” rules) such as WM_CLASS/title/etc. (i3 includes properties commented out for you to choose).  
- Restoring creates **placeholder windows**, and when an app opens a matching window, it gets “swallowed” into the placeholder container.  
- `append_layout <path>` is the command used to load a layout file (typically via `i3-msg`).  
Ref: https://i3wm.org/docs/layout-saving.html

**Low-hanging Studio feature:** “Workspace Template Builder”
- one click: “Save current workspace as template”
  - runs i3-save-tree
  - launches an **interactive selector editor** for each placeholder:
    - suggest criteria from the Inspector (class/instance/title/role)
    - show a “fragility score” for each criterion (title-only = risky)
  - preview: “these criteria match these existing windows”
- one click: “Restore template”
  - runs `append_layout`
  - launches programs (see 76.2)

### 76.2 i3-resurrect proves users want layout + running programs (+ parameterization)
**i3-resurrect** adds what i3 layout saving does not: saving/restoring the running programs as well as the layout, with “profiles” and configurable swallow criteria (class/instance/title/window_role). It also supports scratchpad save/restore.  
Ref: https://github.com/JonnyHaystack/i3-resurrect

Notable low-hanging lessons to steal:
- “profiles” are a natural concept (save multiple setups per workspace)
- it explicitly warns that title matching often requires programs restored before applying layout, and it uses xdotool unmap/remap so i3 treats existing windows as new and will swallow them into placeholders (important edge-case knowledge).  
Ref: https://github.com/JonnyHaystack/i3-resurrect

**Low-hanging Studio features:**
- A “Workspace Project” = (layout template) + (program launch list) + (optional parameters)
- Provide a visual Programs editor like the blog example (command array + working directory + parameter substitution).
- Offer a “Restore order” strategy:
  - restore programs → wait windows mapped → apply layout
  - optionally apply layout-only or programs-only (i3-resurrect supports this distinction)

### 76.3 “Workspaces are projects” is a real user mental model
A user write-up frames the core desire as: “a group of windows and their states is a project,” and demonstrates scripting a dmenu prompt that selects a project, then restores an i3-resurrect profile with parameter substitution (feature name).  
Ref: https://thoughtsunificator.me/saving-my-workspace-with-i3/

**Low-hanging Studio features:**
- “Project Switcher” (in-app, or rofi/dmenu backed):
  - choose project
  - choose feature/env
  - restore layout + programs with substitutions
- A template variable system for programs and layouts:
  - `${project}`, `${feature}`, `${workspace}`, `${cwd}`, `${env.VAR}`

---

## 77) Layout files are “almost JSON”: support i3’s real-world format

i3 layout files are intended to be editable by humans; the docs even mention using a parser that supports i3’s deviations (comments/trailing commas) or transforming to strict JSON if needed.  
Ref: https://i3wm.org/docs/layout-saving.html

There’s also an i3 issue noting that stricter parsers don’t support comments/trailing commas/single quotes, which matters if we want to parse layout files ourselves.  
Ref: https://github.com/i3/i3/issues/6257

**Low-hanging requirement:**
- Our layout/template parser should accept i3’s “human-friendly JSON-ish” format.
- When exporting, offer:
  - “i3-friendly JSON” (with comments allowed)
  - “strict JSON” (for tooling/interop)

---

## 78) Smart “Save template from current state” workflows (cheap magic)

### 78.1 Auto-suggest swallow criteria from the Inspector
When you save a workspace template:
- for each container/window, propose:
  - `class+instance` as default (stable)
  - add `window_role` if present
  - add `title` only if user confirms (fragility warning)
This mirrors i3-resurrect’s swallow options (class/instance/title/window_role).  
Ref: https://github.com/JonnyHaystack/i3-resurrect

### 78.2 “Template health check”
Add a “Test Template” button that:
- spawns placeholder layout in sandbox (Xephyr/Xvfb)
- launches programs in dry-run mode (or a subset)
- reports:
  - which windows matched correctly
  - which placeholders remained unsatisfied
  - which criteria were too broad/narrow

This turns “layout templates” into an immediately debuggable artifact.

---

## 79) Window event watchers as building blocks (wmutils/wew ecosystem confirms the pattern)

Power users wrap `wew` (X event watcher) to build window placement and grouping scripts; for example, projects describe wrappers that do sloppy focus, window placement, and autogrouping around the watcher.  
Ref: https://github.com/lwilletts/fwm

And the wmutils “you are the WM” culture explicitly highlights wew as the X event watcher piece.  
Ref: https://blog.z3bra.org/2015/01/you-are-the-wm.html

**Low-hanging Studio features:**
- “OnWindowCreated(class/instance/title/role)” triggers (devilspie2-style, but with i3 integration)
- “Autogroup” action: when a window appears, move it to workspace X and apply a project template rule
- A “watch mode” panel that shows window lifecycle events live, and offers one-click “turn into rule/macro”

---

## 80) Concrete “low-hanging fruit” backlog for the next build slice

### 80.1 Project/Workspace features (high leverage)
- Workspace Template Builder (save i3 layouts + edit swallow criteria visually)
- Programs editor + parameter substitution
- Project Switcher (rofi/dmenu or in-app)
- Restore strategies (programs-only / layout-only / both, with ordering)
- Template health check + sandbox test

### 80.2 Tooling polish
- i3 layout parser: i3-friendly JSON-ish input, strict JSON export toggle
- “Swallow criteria linter”:
  - warn about title-only
  - warn about criteria matching multiple windows
- One-click “Generate i3 mode” for save/restore like i3-resurrect’s example (nice UX shortcut)

---

## 81) Research links added in this revision
- i3 layout saving/restoring (i3-save-tree, placeholder windows, append_layout): https://i3wm.org/docs/layout-saving.html  
- i3-resurrect (profiles, swallow criteria, save/restore programs, title edge cases): https://github.com/JonnyHaystack/i3-resurrect  
- “Workspaces are projects” scripting write-up: https://thoughtsunificator.me/saving-my-workspace-with-i3/  
- i3 parser strictness discussion (comments/trailing commas): https://github.com/i3/i3/issues/6257  
- wew watcher wrapper (autogrouping/placement): https://github.com/lwilletts/fwm  
- wmutils “you are the WM” (wew watcher): https://blog.z3bra.org/2015/01/you-are-the-wm.html

---

## 82) i3-native “prompt” and command composition: steal i3-input

For i3 users, the lowest-friction “mini UI” is **i3-input**: it prompts the user for a command (or part of one) and sends it to i3. It’s explicitly intended for commands like mark/goto, and you can cancel with Escape.  
Refs:
- i3-input manpage: https://man.archlinux.org/man/extra/i3-wm/i3-input.1.en
- i3 User Guide: https://i3wm.org/docs/userguide.html

### 82.1 Low-hanging Studio features
- A **Prompt backend** option: `Prompt.Command(prefix="mark ")` implemented via i3-input.
- Macro step: `I3.Input(prefix, placeholderText) -> userText` then `I3.Exec(prefix + userText)`.
- “Marks manager” UI:
  - list existing marks
  - jump to mark
  - set mark (with i3-input prompt)
- “Quick i3 command palette” (see also rofi below).

Why this is great:
- zero additional UI toolkit dependency
- consistent with i3 workflow
- perfect for “choose a name”, “choose a workspace”, “enter a command” steps


---

## 83) Rofi as the universal “chooser UI”: steal script mode and custom modi

Rofi’s docs explicitly describe an internal **script mode** that lets you add custom modes (`<name>:<script>`), and points to rofi-script(5) for the protocol.  
Refs:
- rofi manpage (script mode): https://davatorium.github.io/rofi/1.7.3/rofi.1/
- rofi-script(5): https://davatorium.github.io/rofi/1.7.3/rofi-script.5/

### 83.1 Low-hanging Studio integrations
- Prompt backend: `Prompt.Choose()` implemented via rofi `-dmenu`.
- Power backend: **custom “VHK” mode** implemented via rofi script mode:
  - `VHK:vhk_rofi.sh` where the script lists:
    - macros
    - templates
    - recently used assets
    - recent projects
    - “run in sandbox”
    - “open inspector”
  - selecting an item triggers an action.
- “Project Switcher” can be rofi-first (lowest friction):
  - list projects, list profiles, list features/env variants
  - restore workspace template + run macros.

### 83.2 Low-hanging UX pattern: search everywhere
The real value of rofi is “type to filter.” Use that pattern for:
- action palette search
- selecting a macro to run
- selecting an asset
- selecting a window mark / workspace / project


---

## 84) Notifications and progress: steal notify-send + dunstify

We need a first-class “tell the user what’s happening” story:
- quick notifications
- progress indicators
- “macro completed / failed” summaries

There’s a standard command line notification tool `notify-send` (libnotify), and Dunst ships `dunstify` as a notify-send compatible alternative with extra capabilities.  
Refs:
- notify-send manpage: https://manpages.debian.org/testing/libnotify-bin/notify-send.1.en.html
- Dunst docs: dunstify overview: https://dunst-project.org/documentation/dunstify/
- Dunst ArchWiki: https://wiki.archlinux.org/title/Dunst

### 84.1 Low-hanging Studio features
- Step: `Notify(summary, body, urgency, timeout)`
- Step: `Progress(id, percent, text)` (best effort; if daemon supports)
- Runner auto-notify:
  - on failure: include link to Support Bundle folder, last screenshot
  - on success: include runtime and key outputs
- Doctor checks:
  - is a notification daemon running?
  - does `notify-send` work?
  - if not, explain how to install/start one.

### 84.2 “Quiet mode”
- user can toggle “silent macros” (no notifications)
- but still log everything to artifacts


---

## 85) Clipboard reality and persistence: treat PRIMARY vs CLIPBOARD as first-class

On X11, there are multiple selections (PRIMARY vs CLIPBOARD is the common confusion). Tools like xclip and xsel can interact with either; community answers describe how PRIMARY is “select/middle click” and CLIPBOARD is “Ctrl+V.”  
Ref (comparison discussion): https://askubuntu.com/questions/705620/xclip-vs-xsel

Also: the selection contents are not stored “inside the server”; the owning app must stay alive (xclip/xsel often fork a background process to keep owning the selection).  
Refs:
- xsel/xclip persistence note: https://unix.stackexchange.com/questions/368775/how-do-command-line-clipboard-tools-like-xclip-and-xsel-persist-the-clipboar
- clipboard explanation: https://www.wassen.net/x11-clipboard.html

### 85.1 Low-hanging Studio features
- Clipboard inspector must show:
  - PRIMARY content
  - CLIPBOARD content
  - owner (best effort)
- Steps must allow selection choice explicitly:
  - `GetClipboard(selection)`
  - `SetClipboard(selection)`
- “Clipboard keeper” mode (optional):
  - when enabled, the Studio daemon persists clipboard contents so copying doesn’t vanish when the source app exits.
- Templates:
  - “On clipboard change → transform → set clipboard”


---

## 86) i3 keycodes vs keysyms: make hotkey storage explicit

The i3 User Guide explicitly states that bindings can be defined on **keycodes** or on **keysyms**, and you can mix them (with risk of overlaps).  
Ref: i3 user guide section on keyboard bindings: https://i3wm.org/docs/userguide.html

### 86.1 Low-hanging Studio features
- When capturing a hotkey, store:
  - keysym form (layout-dependent)
  - keycode form (layout-independent-ish)
- UI toggle per binding:
  - “portable across layouts” (prefer keycode)
  - “portable across keyboards” (prefer keysym)
- Conflict detection:
  - show overlaps that i3 will not protect you from
- Export:
  - i3 bindsym/bindcode lines
  - plus a “why” tooltip to educate the user


---

## 87) Low-hanging backlog updates from this revision

### P0 (fast, compounding)
- i3-input prompt steps (marks, goto, workspace naming)
- rofi chooser + rofi script mode “VHK palette”
- Notify/Progress steps + Doctor checks for notification daemon
- Clipboard inspector shows PRIMARY/CLIPBOARD + “clipboard keeper” option
- Hotkey storage: keysym + keycode, with a UI toggle

### P1 (still cheap, high value)
- “Export i3 mode” generator (bindings + help text)
- “Macro command palette” (rofi script mode)
- “Search everywhere” UI patterns adopted across editor/inspector


---

## 88) Research links added in this revision
- i3-input: https://man.archlinux.org/man/extra/i3-wm/i3-input.1.en  
- Rofi script mode:
  - https://davatorium.github.io/rofi/1.7.3/rofi.1/
  - https://davatorium.github.io/rofi/1.7.3/rofi-script.5/
- Notifications:
  - https://manpages.debian.org/testing/libnotify-bin/notify-send.1.en.html
  - https://dunst-project.org/documentation/dunstify/
  - https://wiki.archlinux.org/title/Dunst
- Clipboard selections & persistence:
  - https://askubuntu.com/questions/705620/xclip-vs-xsel
  - https://unix.stackexchange.com/questions/368775/how-do-command-line-clipboard-tools-like-xclip-and-xsel-persist-the-clipboar
  - https://www.wassen.net/x11-clipboard.html
- i3 keycodes vs keysyms:
  - https://i3wm.org/docs/userguide.html

---

## 89) Prevent “hotkey feedback loops” and synthetic-input self-triggering (AHK SendLevel analogue)

On X11+i3, it’s easy to accidentally create an infinite loop:
- i3 hotkey triggers a macro
- macro uses xdotool/XTest to synthesize the same hotkey
- i3 sees it again and triggers the macro again  
A real report describes an infinite loop where the hotkey never reaches the target app; it’s re-caught by i3 repeatedly.  
Ref: https://stackoverflow.com/questions/61272019/infinite-loop-of-keypresses-with-i3-bindsym-and-xdotool

**Low-hanging Studio requirements:**
- A global “**Ignore synthetic events**” switch for triggers.
  - For X11-level triggers: ignore events with `send_event` set, and/or filter XInput2 event flags when possible.
  - For kernel/uinput triggers (future): tag events by device and ignore events from the virtual injection device.
- A per-macro “**Input Level**” concept (AHK’s SendLevel / #InputLevel idea):
  - each trigger has a level
  - each injected event has a level
  - triggers can ignore events below/at/above a threshold
- An emergency **panic hotkey** that immediately disables all triggers and stops the runner.

**UX polish:**
- When user binds a macro to Ctrl+Shift+C (or any key sequence) and the macro contains a step that sends Ctrl+Shift+C, show a warning:  
  “This can self-trigger. Use ignore-synthetic or change trigger key.”

---

## 90) Import/export to “human readable macro scripts”: steal xmacro’s file format

A great low-hanging feature is **interop with existing record/replay formats** so users can:
- bootstrap from other tools
- diff changes
- generate scripts outside the UI
- run headless without the Studio

### 90.1 xmacro format is readable and proven
xmacro records X events into a text script like:

- `KeyStrPress <keysym>`
- `KeyStrRelease <keysym>`
- `Delay <ms>`
- `String <text>` (note limitations)  
Ref: xmacro README and command list: https://github.com/franciscod/xmacro

A practical write-up uses `xmacrorec2` to record to a file and pipes to `xmacroplay` to replay:
- `xmacrorec2 > recording.macro`
- `cat recording.macro | xmacroplay`  
Ref: https://intoli.com/blog/terminal-recorders/

### 90.2 Low-hanging Studio features
- Import step list from `.macro` (xmacroplay format) into our workflow graph.
- Export a workflow (or selection) to `.macro` for interoperability.
- A “macro speed” dial maps to the `Delay` values:
  - scale delays by factor
  - or clamp to a min/max
- Provide “insert delays automatically” options similar to `xmacrorec2 -d` (records delays automatically).  
Ref: xmacro docs mention `xmacrorec2 -d`: https://github.com/franciscod/xmacro
- Offer a “playback delay parameter” adapter (xmacroplay has a delay parameter used to slow down events).  
Ref: https://askubuntu.com/questions/1162460/how-do-i-make-xmacro-in-ubuntu-playback-at-the-same-speed

### 90.3 Practical caveat: text sending is tricky
xmacro’s `String` is implemented via a character table (historically Latin1; see README), which reinforces our “robust Type step” design:
- XTest typing (keys)
- clipboard paste
- xvkbd fallback
- (optional) IME-friendly typing later  
Ref: xmacro README: https://github.com/franciscod/xmacro

---

## 91) “TinyTask mode” recorder: steal atbswp’s simplicity as an alternate capture mode

There’s a class of users who want:
- record raw input
- replay raw input
- optionally repeat N times  
…and don’t need vision/a11y.

**atbswp** is a TinyTask-style recorder for Xorg that records keyboard/mouse events and can replay them on demand; it also supports saving a capture as a script that can run without the GUI.  
Refs:
- LinuxUprising overview: https://www.linuxuprising.com/2020/03/how-to-record-and-play-mouse-and.html
- atbswp project page: https://github.com/RMPR/atbswp
- atbswp site notes it uses `pynput` for recording and `pyautogui` for replay: https://atbswp.com/

### 91.1 Low-hanging Studio feature: “Simple Recorder”
Add a recorder mode explicitly for TinyTask workflows:
- minimal UI
- start/stop record hotkey
- play/repeat (N or infinite)
- export as a stand-alone script runner (our own format)

**Why it belongs:** it lowers the activation energy and gives you a “works even without vision” baseline.

### 91.2 Make it a ladder into the full Studio
Offer “Upgrade recording”:
- convert raw clicks into:
  - window-scoped clicks
  - needle-driven clicks
  - waits/assertions
This is how we bring users from “dumb replay” to robust automation.

---

## 92) Doctor checks for X extensions and degraded modes (Xnee’s lessons)

Some features depend on X server extensions:
- XTest (injection)
- RECORD (full protocol capture / synchronized replay)  
Xnee’s manual explicitly says you can replay without the RECORD extension **if synchronization is turned off**.  
Ref: https://xnee.wordpress.com/wp-content/uploads/2012/10/xnee1.pdf

There are also real-world reports of RECORD being broken in some Xorg versions and breaking Xnee until Xorg is fixed.  
Ref: https://forums.linuxmint.com/viewtopic.php?t=46952

### 92.1 Low-hanging Studio “Doctor” items
- Detect XTest extension availability (required for Send/click injection).
- Detect RECORD extension availability (required for advanced/sync recorder modes).
- If RECORD missing/broken:
  - disable “Full Protocol” recorder mode
  - allow “Basic recorder” + “Sync via i3/X events” mode
  - show a clear explanation (“advanced sync needs RECORD; you can still run in basic mode”)
- Offer a “verbose logs” toggle for bug reports, echoing how Xnee asks users to send verbose logs.  
Ref: Xnee manual bug reporting guidance: https://xnee.wordpress.com/wp-content/uploads/2012/10/xnee1.pdf

---

## 93) Low-hanging backlog updates (from this revision)

### P0
- Synthetic event filtering + InputLevel concept + panic hotkey
- xmacro import/export (plus speed scaling)
- TinyTask / Simple Recorder mode + “upgrade recording” wizard
- Doctor: detect XTest/RECORD; degrade gracefully; “verbose logs for support”

### P1
- “Macro as test” CI runner can accept `.macro` imports and run them in sandbox
- A recorder option to “auto-insert delays” (xmacrorec2 -d style) + convert-to-waits wizard

---

## 94) Research links added in this revision
- i3/xdotool self-trigger loop example: https://stackoverflow.com/questions/61272019/infinite-loop-of-keypresses-with-i3-bindsym-and-xdotool  
- xmacro format and commands: https://github.com/franciscod/xmacro  
- xmacro used for replayed macro scripts (and why): https://intoli.com/blog/terminal-recorders/  
- xmacroplay delay parameter example: https://askubuntu.com/questions/1162460/how-do-i-make-xmacro-in-ubuntu-playback-at-the-same-speed  
- atbswp overview (TinyTask clone): https://www.linuxuprising.com/2020/03/how-to-record-and-play-mouse-and.html  
- atbswp repo: https://github.com/RMPR/atbswp  
- atbswp site (pynput + pyautogui): https://atbswp.com/  
- Xnee manual (RECORD optional if sync off; verbose logs): https://xnee.wordpress.com/wp-content/uploads/2012/10/xnee1.pdf  
- RECORD broken report: https://forums.linuxmint.com/viewtopic.php?t=46952

---

## 100) Pixel & coordinate “eyedropper” tools: make visual targeting effortless (xcolor + xmag)

Visual automation lives or dies on how fast you can answer:
- “What exact color is that pixel?”
- “What are the coordinates relative to screen/window/client?”
- “What’s a tight region to search?”

### 100.1 Add a first-class “Pick Color / Pick Pixel” inspector tool
Two great X11 precedents:
- **xcolor**: a lightweight color picker; you click anywhere on screen and it prints the selected color (RGB) to stdout.  
  Refs: https://man.archlinux.org/man/extra/xcolor/xcolor.1.en and https://github.com/Soft/xcolor
- **xmag**: magnifies a selected region and shows it as a grid of pixels (useful for exact pixel coordinates + values).  
  Refs: https://man.archlinux.org/man/extra/xorg-xmag/xmag.1.en and “use xmag to get exact pixel coordinates” (AskUbuntu): https://askubuntu.com/questions/163783/tool-to-easily-select-a-pixel-on-screen-and-get-color-and-absolute-coordinates

**Low-hanging Studio features:**
- Inspector button: **Pick Color**
  - returns `#RRGGBB` (and optionally `rgb(r,g,b)`), with “copy to clipboard”
- Inspector button: **Pick Pixel**
  - returns `(x,y)` + color, and lets user choose coord mode:
    - Screen
    - Active window
    - Client area
- “Magnify while picking” option (xmag-style) for precision

### 100.2 “Pixel watch” step type (great for games and status LEDs)
- `WaitPixelColor(region/point, color, tolerance, timeout)`
- `WaitPixelChange(region/point, timeout)`
- “Record pixel watch”: pick pixel → insert wait step

This is extremely cheap and immediately useful.

---

## 101) Input injection realism: XSendEvent vs XTEST (and why many apps ignore “synthetic” events)

A recurring confusion in Linux automation is “why did my key send do nothing?”
The short version: **X has multiple ways to send events, and some mark events as synthetic** in a way that clients can (and often do) ignore.

### 101.1 The “send_event flag” matters
- X’s `SendEvent` request can generate synthetic events; clients can choose to discard them.  
  Ref: “X’s two ways to send events” explains how a flag indicates whether synthetic key/button events should be interpreted or discarded: https://utcc.utoronto.ca/~cks/space/blog/unix/XTwoWaysToSendEvents
- A practical X11 key transformation write-up notes that `XSendEvent` marks events as synthesized and many applications (e.g., xterm) ignore them; whereas there is only one reliable way to send key events: `XTestFakeKeyEvent`.  
  Ref: https://blog.zhanghai.me/key-sequence-transformation-in-x11/
- Autokey users hit this directly: an issue notes many programs observe the `send_event` flag and reject these events.  
  Ref: https://github.com/autokey/autokey/issues/405

### 101.2 Low-hanging Studio policy (make this explicit)
- **Never** use `XSendEvent` for “Send keys/mouse” steps by default.
- Prefer **XTEST** injection (the same primitive used by xdotool).  
  Ref: xdotool man page: https://manpages.ubuntu.com/manpages/trusty/man1/xdotool.1.html
- If a user chooses a “SendEvent” style backend (expert), label it as:
  - “May be ignored by many apps; prefer XTEST.”

### 101.3 Low-hanging UX: “Injection diagnostics”
When a send step fails repeatedly:
- show a help card:
  - “This app may ignore synthetic events or require focus.”
  - recommend:
    - focus-first
    - accessibility action
    - paste/xvkbd typing backend
    - uinput backend (future)

---

## 102) Make “xdotool best practices” the default behavior in our runner

Even if we don’t use xdotool internally, it encodes a lot of real-world lessons:
- focus the right window **and wait until it’s active**
- clear stuck modifiers
- avoid racing focus changes

### 102.1 Default to “focus+sync+send”
Examples and issues repeatedly use:
- `windowactivate --sync`
- `key --clearmodifiers ...`  
Refs:
- Example pattern from StackOverflow: https://stackoverflow.com/questions/12026953/automatic-web-page-refresh-using-xdotool-not-sending-key-after-window-focus
- xdotool `selectwindow` and `behave` documented in its man page: https://manpages.ubuntu.com/manpages/trusty/man1/xdotool.1.html

**Low-hanging Studio features:**
- Per-step option: “Require focus (recommended)” default ON
- Per-step option: “Clear modifiers” default ON
- Implicit wait: after focus request, wait until `active_window == target_window` (or timeout)

### 102.2 Doctor check: “xdotool search/window property failures”
An xdotool issue shows `_NET_WM_DESKTOP` property query failures can happen (`XGetWindowProperty[_NET_WM_DESKTOP] failed`).  
Ref: https://github.com/jordansissel/xdotool/issues/67

**Low-hanging Doctor behavior:**
- if EWMH properties are missing/broken:
  - warn user that some search/desktop-related functions may fail
  - prefer i3 IPC queries for window selection in i3 sessions
  - fall back to click-to-select (xdotool selectwindow-style) for picking a window

---

## 103) Use i3 binding modes as a first-class macro safety tool (pause modes, passthrough modes)

i3’s binding modes are a perfect mechanism for:
- avoiding collisions
- temporarily disabling bindings
- making a “macro control mode” with a small set of keys

### 103.1 Binding modes release bindings when switching
The i3 User’s Guide explains:
- you can have multiple sets of bindings (“binding modes”)
- switching modes releases bindings from the current mode and activates only bindings in the new mode
- the only predefined mode is `default`.  
Ref: https://i3wm.org/docs/userguide.html (section “Binding modes”)

### 103.2 Low-hanging Studio features built on modes
- **VHK Pause Mode**:
  - switch to `mode "vhk_paused"`
  - only bindings active:
    - resume / quit / help
- **Passthrough (Insert) Mode**:
  - switch to `mode "passthrough"`
  - used for apps like games/emacs where you don’t want i3 to catch keys
  - one key returns to `mode "default"`
  - This is a common community workaround pattern.  
    Ref (example discussion): https://www.reddit.com/r/i3wm/comments/8dovvj/disable_keybindings_for_a_certain_application_or/

- **Macro Run Mode**:
  - while a macro is running, switch to a mode that disables most macro triggers
  - prevents feedback loops and makes macros more deterministic

### 103.3 Auto-return to default mode
A common i3 trick is chaining `mode "default"` at the end of a command so i3 returns to normal bindings after a one-shot mode.  
Ref: https://unix.stackexchange.com/questions/338228/i3wm-more-than-10-workspaces-with-double-modifier-key

**Low-hanging Studio export feature:**
- when generating i3 bindings for our macros or control modes, automatically chain `; mode "default"` where appropriate.

---

## 104) Low-hanging backlog updates (from this revision)

### P0
- Pixel/Color picker inspector (xcolor/xmag-style) + “Pick Pixel” step generator
- Explicit injection policy: prefer XTEST; warn on SendEvent backend
- Focus+sync+clearmodifiers defaults in runner
- i3 binding mode integration:
  - pause mode
  - passthrough mode
  - macro-run safety mode (optional)
- Doctor checks for EWMH property issues and degraded selection strategies

### P1
- A small “compatibility DB” for apps:
  - “focus required” hints
  - “background send unreliable” hints
- Event log annotation for focus/sync waits (why we waited, for how long)

---

## 105) Research links added in this revision
- xcolor color picker: https://man.archlinux.org/man/extra/xcolor/xcolor.1.en and https://github.com/Soft/xcolor  
- xmag magnifier for pixel precision: https://man.archlinux.org/man/extra/xorg-xmag/xmag.1.en and https://askubuntu.com/questions/163783/tool-to-easily-select-a-pixel-on-screen-and-get-color-and-absolute-coordinates  
- SendEvent vs XTest reality:
  - https://utcc.utoronto.ca/~cks/space/blog/unix/XTwoWaysToSendEvents
  - https://blog.zhanghai.me/key-sequence-transformation-in-x11/
  - https://github.com/autokey/autokey/issues/405
- xdotool best practices and pitfalls:
  - https://manpages.ubuntu.com/manpages/trusty/man1/xdotool.1.html
  - https://stackoverflow.com/questions/12026953/automatic-web-page-refresh-using-xdotool-not-sending-key-after-window-focus
  - https://github.com/jordansissel/xdotool/issues/67
- i3 binding modes:
  - https://i3wm.org/docs/userguide.html
  - https://unix.stackexchange.com/questions/338228/i3wm-more-than-10-workspaces-with-double-modifier-key
  - https://www.reddit.com/r/i3wm/comments/8dovvj/disable_keybindings_for_a_certain_application_or/

---

## 106) Recovered: Gesture + file triggers (consolidate missing “automation glue”)

Earlier research surfaced two extremely cheap trigger categories that make a macro studio feel “alive”:

### 106.1 Gesture triggers (touchpad/touchscreen)
- **libinput-gestures** reads libinput gesture events and maps them to shell commands (commonly xdotool).  
  Ref: https://github.com/bulletmark/libinput-gestures
- **Touchégg** runs as a background gesture recognizer service; on many systems you enable/start it via systemd.  
  Refs:
  - https://github.com/JoseExposito/touchegg
  - https://wiki.archlinux.org/title/Touchegg

**Low-hanging Studio features:**
- Gesture binding UI:
  - swipe/pinch (finger count) → run macro / run i3 command
- “Gesture monitor” panel (like KeyHistory): observe → one-click “assign to macro”
- Doctor checks:
  - daemon present/running
  - conflicts (multiple gesture daemons)

### 106.2 File-system triggers (“inotify macros”)
- **inotifywait** efficiently waits for filesystem events (close_write/create/moved_to/etc.) and is designed for scripting.  
  Ref: https://linux.die.net/man/1/inotifywait
- **systemd.path** units can trigger services on path changes (PathChanged/PathModified/etc.).  
  Refs:
  - https://www.freedesktop.org/software/systemd/man/systemd.path.html
  - https://man.archlinux.org/man/systemd.path.5.en
- **incron** is often described as “inotify cron” (filesystem events → job).  
  Ref: https://www.linux.com/news/scheduling-jobs-based-filesystem-activity-incron/

**Low-hanging Studio features:**
- Trigger: `OnFileChange(path, events, filter, debounce)` → run macro
- Generator: export `macro.path` + `macro.service` (headless runner) for system-level reliability
- Optional: export incrontab lines for users who prefer incron

---

## 107) Cursor management (surprisingly important for vision reliability)

For image/pixel matching and for “evidence capture,” the mouse cursor is a frequent source of flakiness:
- it can occlude UI elements (image search misses)
- it introduces unexpected pixels into regions
- it can confuse baseline screenshots

### 107.1 Provide a “Hide cursor while running macro” runner option
Two proven approaches:
- **xbanish** hides cursor when typing; it uses the XFixes extension (`XFixesHideCursor` / `XFixesShowCursor`).  
  Ref: https://github.com/jcs/xbanish
- **unclutter-xfixes / unclutter** hides cursor after inactivity; newer variants include options like `--start-hidden` and `--hide-on-touch`.  
  Refs:
  - ArchWiki Unclutter: https://wiki.archlinux.org/title/Unclutter
  - unclutter man page lists `--hide-on-touch` and `--start-hidden`: https://man.archlinux.org/man/unclutter.1.en

**Low-hanging Studio features:**
- Runner toggle:
  - Hide cursor during macro run
  - Restore cursor at end (even on failure)
- Step type:
  - `Cursor.Hide()`, `Cursor.Show()`
- “Touchscreen mode” toggle:
  - hide cursor on touch (unclutter `--hide-on-touch`) for kiosk-style macros

### 107.2 Evidence capture: choose whether to include cursor
Many command-line screenshot tools intentionally do **not** capture the cursor (often desirable for vision). For evidence, sometimes you *do* want it.
- Discussion notes many CLI screenshot utilities do not include cursor by default.  
  Ref: https://askubuntu.com/questions/929981/how-can-i-include-the-mouse-pointer-using-a-command-line-screenshot-utility
**Low-hanging policy:**
- Default: cursor hidden during matching steps
- Optional: “Include cursor in evidence” by overlaying cursor later (advanced) or temporarily showing for capture-only frames

---

## 108) Clipboard synchronization tools (autocutsel) and why it belongs in the Doctor

X11 has multiple selections (PRIMARY vs CLIPBOARD). Some users *want* them synchronized; others hate it.
**autocutsel** is a long-standing tool that synchronizes cutbuffer and CLIPBOARD selection and is often used to sync X11 selections (and even VNC clipboard workflows).  
Ref: https://www.nongnu.org/autocutsel/

There are real user reports/questions about synchronizing selections and how it can break normal workflows if it syncs PRIMARY → CLIPBOARD unexpectedly.  
Ref: https://unix.stackexchange.com/questions/660024/whats-a-lightweight-way-to-synchronize-clipboard-primary-selections

**Low-hanging Studio features:**
- Doctor panel option:
  - “Do you want PRIMARY and CLIPBOARD kept in sync?”
  - If yes: suggest/install/autostart autocutsel (with warnings)
- Trigger enhancements:
  - `OnClipboardChange(PRIMARY)` vs `OnClipboardChange(CLIPBOARD)` clearly separated
- “Clipboard keeper” mode:
  - keep selection contents alive even if source app exits (where feasible)

---

## 109) Screenshot backends and pipelines (for vision + debug artifacts)

Vision automation depends on fast, consistent screen capture.

### 109.1 xwd + convert pipeline (ubiquitous fallback)
A common, widely installed approach:
- `xwd -root -out screenshot.xwd` then convert to PNG via ImageMagick (`convert xwd:- out.png`).  
  Ref: https://askubuntu.com/questions/226829/how-to-take-screenshot-of-an-x11-based-gui-from-a-text-terminal-such-as-tty1

This is a great “always available” fallback backend even if maim/shotgun aren’t installed.

### 109.2 scrot: scripted window/region capture
`scrot` is a simple CLI screen capture tool; it supports capture of a window (`-u`) or interactive selection (`-s`) and is designed to be scriptable.  
Refs:
- scrot man page (window/rect area capture): https://manpages.ubuntu.com/manpages/jammy/man1/scrot.1.html
- scrot usage article (window `-u`, select `-s`): https://opensource.com/article/17/11/taking-screen-captures-linux-command-line-scrot

### 109.3 Transparency + “black screenshots” gotcha (ImageMagick import)
When capturing windows with transparent regions, a common pitfall is “black areas” if the output format doesn’t preserve alpha; forcing `PNG32:` is a known workaround.  
Ref: https://stackoverflow.com/questions/28088524/black-screenshot-taken-with-import-imagemagick

**Low-hanging Studio features:**
- Screenshot backend abstraction:
  - maim / shotgun / scrot / xwd+convert
- Output metadata:
  - whether cursor included
  - whether alpha preserved
- “Fast capture” preference + fallback ladder

---

## 110) Modifier clearing pitfalls (xdotool’s clearmodifiers is not magic)

`--clearmodifiers` is commonly recommended to prevent stuck modifiers when sending keys, but it can itself have pitfalls:
- xdotool issue reports modifiers can become stuck after using `--clearmodifiers` because it doesn’t track changes in key state since saving modifiers.  
  Ref: https://github.com/jordansissel/xdotool/issues/43

**Low-hanging Studio requirements:**
- Prefer a “safe modifier reset” strategy:
  - track keydown/up states in our own engine where possible
  - release only modifiers we believe are down
- Provide “Reset modifiers” as an explicit step:
  - releases Shift/Ctrl/Alt/Super safely
- Doctor: if user reports “stuck keys,” suggest:
  - press modifiers manually
  - temporarily disable clearmodifiers
  - use focus-first + accessibility actions

---

## 111) Backlog updates from this revision (cursor + clipboard + capture)

### P0
- Cursor hide/show runner toggle + steps (xfixes-based)
- Pixel/color “eyedropper” + magnifier integration (already added conceptually; ensure shipped early)
- Screenshot backend ladder includes xwd+convert and scrot
- Doctor options for clipboard sync + warnings (autocutsel)
- Safer modifier clearing strategy + explicit “Reset modifiers” step

### P1
- Evidence capture mode:
  - optional cursor overlay
  - annotated “cursor hidden during match” markers in logs
- Screenshot alpha-awareness (“PNG32” forcing when needed)
- Clipboard keeper mode (minimal persistence)

---

## 112) Research links added in this revision
- autocutsel: https://www.nongnu.org/autocutsel/  
- clipboard sync pitfalls: https://unix.stackexchange.com/questions/660024/whats-a-lightweight-way-to-synchronize-clipboard-primary-selections  
- xwd screenshot pipeline: https://askubuntu.com/questions/226829/how-to-take-screenshot-of-an-x11-based-gui-from-a-text-terminal-such-as-tty1  
- scrot man page + usage: https://manpages.ubuntu.com/manpages/jammy/man1/scrot.1.html and https://opensource.com/article/17/11/taking-screen-captures-linux-command-line-scrot  
- xbanish: https://github.com/jcs/xbanish  
- Unclutter docs: https://wiki.archlinux.org/title/Unclutter and https://man.archlinux.org/man/unclutter.1.en  
- “include cursor in CLI screenshots” discussion: https://askubuntu.com/questions/929981/how-can-i-include-the-mouse-pointer-using-a-command-line-screenshot-utility  
- ImageMagick transparency/black screenshot: https://stackoverflow.com/questions/28088524/black-screenshot-taken-with-import-imagemagick  
- xdotool clearmodifiers stuck: https://github.com/jordansissel/xdotool/issues/43

---

## 113) “BlockInput” and safe user‑input suppression (AHK BlockInput analogue)

AHK’s `BlockInput` is a big part of “reliable automation” when you need to prevent accidental interference. On X11, the ecosystem already uses a few practical patterns.

### 113.1 Disable devices via xinput (“Device Enabled” / float / reattach)
People disable keyboards/touchpads using `xinput set-int-prop <id> "Device Enabled" 8 0` and re-enable with `... 8 1`.  
Ref: https://unix.stackexchange.com/questions/17115/disable-keyboard-mouse-temporarily

Another approach is `xinput float <id>` to detach from master, then `xinput reattach <id> <master>` to re-enable.  
Ref: https://askubuntu.com/questions/160945/is-there-a-way-to-disable-a-laptops-internal-keyboard

**Low-hanging Studio steps:**
- `Input.Block(devices=[keyboard|mouse|touchpad], method=disable|float, timeout?, failsafeHotkey?)`
- `Input.Unblock()`

### 113.2 Critical caveat: “key-up not sent” if you disable mid-press
If you disable a keyboard while a key is held down, the key-up never arrives, and you can get “stuck keys” (e.g., it behaves like Enter is held).  
Ref: https://stackoverflow.com/questions/10758473/releasing-all-keys-after-disabling-the-keyboard-in-x11-linux-using-xinput

**Low-hanging mitigations (should be automatic):**
- Only activate BlockInput on **key release** (i3 `bindsym --release` pattern already recommended).
- Add a short “arming delay” (e.g., 50–100ms) after trigger key release.
- Provide a “Reset modifiers / release keys” step at unblock time.

### 113.3 Alternative: passive grabs instead of disabling devices (safer v1)
For many macros, it’s enough to “grab” input so only our process sees it (without disabling devices). This is less invasive than xinput disabling and avoids stuck keys, but it can conflict with other grabs.

**Low-hanging policy:**
- Default BlockInput uses “grab mode” if possible.
- Use xinput device disabling only when the user opts in or when grabs fail.

---

## 114) Tap‑hold keys, layers, and chorded triggers (steal xcape + KMonad + keyd patterns)

A huge usability boost is turning “one key” into “many triggers” without needing weird multi-key chords.

### 114.1 xcape: “modifier when held, key when tapped”
xcape allows a modifier key to generate another key when pressed and released on its own (classic example: Left Ctrl acts like Esc when tapped). It also notes a behavioral caveat: it’s slightly slower because the press is only emitted on release.  
Refs:
- https://github.com/alols/xcape
- https://manpages.ubuntu.com/manpages/jammy/man1/xcape.1.html

**Low-hanging Studio features:**
- “Tap‑hold binding” UI:
  - choose a physical key
  - set “hold = modifier/layer”
  - set “tap = key/macro”
- Export an xcape command line snippet for users who want system-level behavior.
- Provide a “tap‑hold latency” slider (because xcape-style behavior has inherent release timing tradeoffs).

### 114.2 KMonad: layers + multi-tap + tap-hold (QMK-like) at the system level
KMonad explicitly provides advanced keyboard features: layers, multi-tap, tap-hold, etc., implemented via low-level input manipulation so it works with virtually any keyboard.  
Ref: https://github.com/kmonad/kmonad

**Low-hanging Studio integration idea:**
- Treat KMonad as an optional “keyboard engine backend”:
  - generate a KMonad config fragment from our binding UI
  - allow our macros to be triggered by “layered keys” defined by KMonad
- This gives power users ergonomic “keyboard layers” while keeping our macro engine focused on automation.

### 114.3 Why this belongs even for i3 users
i3 already supports binding modes; tap-hold layers are the keyboard analogue: quick, ergonomic “modal” behavior without collisions.

---

## 115) Mode-aware macros and i3 mode events (deeper use of binding modes)

We already use modes for pause/passthrough. The next low-hanging upgrade is to make macros **mode-aware** and allow **mode changes as triggers**.

### 115.1 i3 supports binding modes and advises switching back to default
The i3 docs describe `mode <name>` and note it’s advisable to define bindings to switch back to default mode.  
Ref: https://i3wm.org/docs/userguide.html

**Low-hanging features:**
- Trigger: `OnI3ModeChanged(name)` (subscribe to i3 “mode” events)
- Step: `I3.Mode(name)` and `I3.ModeDefault()`
- Visual “Mode Editor”:
  - define a mode with a small palette of macro bindings
  - export config snippet

### 115.2 “Macro Run Mode” (strong safety default)
When a macro starts:
- switch to a dedicated mode where triggers are limited
- expose only:
  - pause
  - stop
  - emergency unblock
When the macro ends:
- return to default mode automatically

This reduces:
- accidental re-triggers
- focus stealing races
- user interference

---

## 116) Low-hanging backlog updates (from this revision)

### P0
- BlockInput (grab + xinput disable fallback) + safe activation on key release
- Unblock + Reset modifiers step
- Tap-hold binding UI + export xcape snippet
- Optional KMonad config generation (power user feature; low risk if treated as external backend)
- Mode-aware triggers (OnI3ModeChanged) and a simple mode editor

### P1
- Per-device binding support (keyboard A triggers macro, keyboard B doesn’t)
- “Binding lint” warnings for xcape/KMonad timing pitfalls (tap-hold in fast typing contexts)

---

## 117) Research links added in this revision
- xcape README + caveat: https://github.com/alols/xcape  
- xcape man page: https://manpages.ubuntu.com/manpages/jammy/man1/xcape.1.html  
- KMonad features (layers, multi-tap, tap-hold): https://github.com/kmonad/kmonad  
- Disable devices via xinput: https://unix.stackexchange.com/questions/17115/disable-keyboard-mouse-temporarily  
- xinput float/reattach approach: https://askubuntu.com/questions/160945/is-there-a-way-to-disable-a-laptops-internal-keyboard  
- “key-up not sent” caveat when disabling: https://stackoverflow.com/questions/10758473/releasing-all-keys-after-disabling-the-keyboard-in-x11-linux-using-xinput  
- i3 binding modes docs: https://i3wm.org/docs/userguide.html

---

## 118) “System state triggers”: steal from the status-bar world (audio/media/network/power/lock)

A lot of automation is reactive: “when something changes, do something.”  
Linux already has a mature “monitor” ecosystem (status bars, widgets, daemons) that we can copy with very little effort.

### 118.1 Hot corners / screen edges (cheap, fun, surprisingly useful)
`xdotool` includes **behave_screen_edge**, which binds an action to events when the mouse hits a screen edge or corner, with debouncing controls like `--delay` and `--quiesce`.  
Refs:
- AskUbuntu excerpt of behave_screen_edge options: https://askubuntu.com/questions/601074/perform-action-when-moving-mouse-cursor-to-certain-position-in-lubuntu-hot-corn
- xdotool man page (behave_screen_edge): https://manpages.ubuntu.com/manpages/trusty/man1/xdotool.1.html

**Low-hanging Studio features:**
- Trigger: `OnScreenEdge(edge|corner, delay_ms, quiesce_ms)` → run macro
- Visual editor: choose edge/corner + slider for delay/quiesce (prevents accidental triggers)
- Template: “hot corner = show macro palette (rofi)”

### 118.2 Volume/mute triggers (pactl subscribe)
`pactl subscribe` outputs events when sinks/sources change. A common pattern is to grep for “sink” updates and trigger scripts.  
Ref: https://stackoverflow.com/questions/34936783/watch-for-volume-changes-in-alsa-pulseaudio

**Low-hanging Studio features:**
- Trigger: `OnAudioVolumeChanged(sink=default|id)` and `OnMuteChanged`
- Step: `SetVolume(percent|delta)` / `SetMute(on|off|toggle)`
- “Audio monitor” panel:
  - show current sink/source volume/mute
  - show event stream tail (for debugging)
- Doctor check:
  - ensure `pactl` works (PipeWire/PulseAudio compat), and explain common pitfalls when running from cron (missing environment, etc.).  
    Ref example pitfall: https://askubuntu.com/questions/526287/change-system-volume-using-crontab-pactl

### 118.3 Media triggers (MPRIS) via playerctl --follow (and playerctld)
**playerctl** is a CLI + library for controlling MPRIS media players; it supports `--follow` to print changes as they happen.  
Refs:
- playerctl README (`--follow` prints query whenever it changes): https://github.com/altdesktop/playerctl/blob/master/README.md
- playerctl man page (playerctld daemon tracks “most recent activity”): https://man.archlinux.org/man/playerctl.1.en
- ArchWiki MPRIS overview: https://wiki.archlinux.org/title/MPRIS

**Low-hanging Studio features:**
- Triggers:
  - `OnMediaPlaybackStatusChanged` (Playing/Paused/Stopped)
  - `OnTrackChanged` (title/artist/album)
  - `OnPlayerChanged` (active player switched)
- Steps:
  - `Media.PlayPause`, `Next`, `Previous`
  - `Media.SetPosition`, `Media.Seek`
  - `Media.GetMetadata -> vars`
- “Now Playing” inspector panel:
  - show active player and metadata
  - allow “bind this to hotkey/gesture” in one click

### 118.4 Network triggers via nmcli monitor
NetworkManager has a `nmcli monitor` mode that prints real-time updates about network state and connection changes.  
Refs:
- nmcli reference manual (monitor details): https://networkmanager.dev/docs/api/latest/nmcli.html
- AskUbuntu shows nmcli monitor output for connectivity changes: https://askubuntu.com/questions/717938/how-to-monitor-networkmanager-connectivity
- opensource.com also describes “Monitor provides commands to monitor NetworkManager activity”: https://opensource.com/article/20/7/nmcli

**Low-hanging Studio features:**
- Triggers:
  - `OnNetworkStateChanged` (connected/disconnected)
  - `OnWifiChanged` (optional v2)
- Steps:
  - `Network.ToggleWifi(on/off)`
  - `Network.Connect(name)` (optional v2; start with monitor-only)
- Doctor checks:
  - ensure NetworkManager is present; otherwise suggest alternative (out-of-scope v1)

### 118.5 Battery/power triggers via upower --monitor
`upower --monitor` prints events when power sources are added/removed/changed, and `--monitor-detail` prints full detail on each change.  
Refs:
- UPower reference manual: https://upower.freedesktop.org/docs/upower.1.html
- Red Hat docs also describe --monitor/--monitor-detail: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/7/html/power_management_guide/upower

**Low-hanging Studio features:**
- Triggers:
  - `OnBatteryLevelBelow(percent)`
  - `OnACPluggedIn` / `OnACUnplugged`
- Steps:
  - “enter power saver mode” (placeholder action; can become plugin later)
- Template macros:
  - “when battery < 15%: notify + reduce brightness (future plugin) + pause heavy macros”

### 118.6 Lock/unlock/suspend triggers (xss-lock model)
`xss-lock` hooks a locker to the MIT screen saver extension **and** to systemd logind, and executes the locker in response to those events.  
Refs:
- xss-lock man page: https://man.archlinux.org/man/xss-lock.1
- ArchWiki session lock page notes xss-lock subscribes to logind events like lock-session/unlock-session: https://wiki.archlinux.org/title/Session_lock

**Low-hanging Studio features:**
- Triggers:
  - `OnSessionLock`
  - `OnSessionUnlock`
  - `OnSuspend` / `OnHibernate` (optional v2)
- Default safety policy:
  - pause macros on lock
  - clear sensitive variables/clipboard if user enables “privacy mode”

---

## 119) “Monitor adapters” as a reusable abstraction (tiny architecture win)

All the above triggers share a pattern:
- run a monitor command (`pactl subscribe`, `nmcli monitor`, `upower --monitor`, `playerctl --follow`)
- parse lines
- emit structured events
- optionally allow debouncing/throttling

**Low-hanging Studio module:** `MonitorAdapter`
- declarative definition: command + regex → event
- reusable in:
  - triggers
  - Doctor diagnostics (“is it emitting events?”)
  - Event Stream panels

---

## 120) Backlog updates from this revision

### P0
- OnScreenEdge trigger (xdotool behave_screen_edge model)
- Audio triggers (pactl subscribe) + basic volume steps
- Media triggers (playerctl --follow) + play/pause steps
- Network triggers (nmcli monitor)
- Power triggers (upower --monitor)
- Lock/unlock triggers (xss-lock/logind model)
- MonitorAdapter module + event stream panels (audio/media/network/power)

### P1
- Templates for each trigger family (battery < X, wifi disconnect, media track change)
- “Rules + triggers” unification (e.g., “on app launch then on network change do…”)

---

## 121) Research links added in this revision
- xdotool behave_screen_edge: https://askubuntu.com/questions/601074/perform-action-when-moving-mouse-cursor-to-certain-position-in-lubuntu-hot-corn and https://manpages.ubuntu.com/manpages/trusty/man1/xdotool.1.html  
- pactl subscribe volume monitoring: https://stackoverflow.com/questions/34936783/watch-for-volume-changes-in-alsa-pulseaudio  
- playerctl --follow and playerctld: https://github.com/altdesktop/playerctl/blob/master/README.md and https://man.archlinux.org/man/playerctl.1.en  
- MPRIS overview: https://wiki.archlinux.org/title/MPRIS  
- nmcli monitor: https://networkmanager.dev/docs/api/latest/nmcli.html and https://askubuntu.com/questions/717938/how-to-monitor-networkmanager-connectivity and https://opensource.com/article/20/7/nmcli  
- upower monitor: https://upower.freedesktop.org/docs/upower.1.html and https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/7/html/power_management_guide/upower  
- xss-lock and session lock events: https://man.archlinux.org/man/xss-lock.1 and https://wiki.archlinux.org/title/Session_lock

---

## 122) App adapters: bypass vision by using apps’ native hooks/IPC (huge ROI)

A lot of “AHK power” comes from having *multiple targeting strategies*.  
On Linux/X11, one of the highest‑leverage (and lowest‑effort) strategies is: **use an app’s own scripting hooks/IPC** when it exists, and fall back to accessibility/vision only when it doesn’t.

### 122.1 sxiv “external prefix key” handler = a perfect automation protocol
sxiv has a built-in “external prefix key” hook that calls a user script (`exec/key-handler`):
- sxiv passes the **next key combo** as the first argument
- passes **a list of selected images** (marked images or current image) on stdin, one path per line
- **blocks until the script terminates**, then reloads modified images  
Ref: https://sources.debian.org/src/sxiv/26-1/exec/key-handler

**Low-hanging Studio idea: “Selection Hook Adapter”**
- define an adapter that receives:
  - list of items from stdin (files/URLs/etc.)
  - a “trigger key” label
- then runs a macro “per item” or “batch mode” with `${item.path}` available

This immediately enables:
- “batch OCR selected images”
- “rename/resize/watermark selected images”
- “run vision needle capture on each image”
…without any screen scraping.

### 122.2 kitty remote control: “send text to this window” with powerful matching
kitty ships a remote-control interface; `kitten @ send-text` can select target windows with `--match` using window title, cmdline of the running program, working directory, etc., and then send text (with unicode escapes).  
Ref: https://sw.kovidgoyal.net/kitty/remote-control/

**Low-hanging Studio features:**
- Adapter: “Kitty Remote Control”
  - step: `Kitty.SendText(match=..., text=...)`
  - step: `Kitty.Launch(...)` and `Kitty.Focus(...)` (optional)
- Inspector helper: “Pick kitty window” (by title/cmdline/cwd) and generate a match rule.

This is a better-than-vision path for “terminal automation.”

### 122.3 mpv JSON IPC: automation without simulating user input
mpv’s own manual explicitly recommends using `--input-ipc-server` for interactive control, exposing **JSON IPC over unix domain sockets**, instead of simulating user input.  
Ref: https://mpv.io/manual/stable/

**Low-hanging Studio features:**
- Adapter: “mpv IPC”
  - triggers: OnPlaybackStatusChanged / OnTimePos / OnTrackChanged (via observe)
  - steps: PlayPause, Seek, SetProperty, GetProperty
- Template macros:
  - “when a macro starts, pause mpv”
  - “on track change, show notification”

### 122.4 zathura exec + D-Bus: doc workflows without screen scraping
zathura supports executing external shell commands and also exposes a D-Bus interface (e.g., for SyncTeX workflows).  
Ref: https://pwmt.org/projects/zathura/documentation/

**Low-hanging Studio features:**
- Adapter: “zathura”
  - steps: `Zathura.Exec(cmd)` (where `$FILE` expands, etc.)
  - triggers: “Synctex position changed” (later; via D-Bus)
- Template:
  - “open current PDF in editor at current location”
  - “export current page as image then run OCR”

---

## 123) “Adapter-first” strategy: build a library of app integrations

### 123.1 Why this is low-hanging fruit
- Many apps already provide:
  - IPC (sockets, DBus)
  - hooks (call scripts with context)
  - well-defined selection models (file lists)
- Integrating these is often **simpler** than building a robust visual selector.

### 123.2 Proposed adapter interface (minimal, stable)
Each adapter declares:
- capabilities: steps/triggers it supports
- “pick target” helpers (optional)
- required binaries/services
- environment assumptions (DISPLAY, socket path)

**Example adapters to implement early:**
- kitty (remote control)
- mpv (IPC)
- zathura (exec / D-Bus later)
- sxiv selection hook (stdin list)
- “generic command adapter” (just run shell with structured args)

### 123.3 UX: adapters should appear as action categories
In the action palette:
- “Apps → kitty”
- “Apps → mpv”
- “Apps → zathura”
- “Apps → sxiv”

And templates should be adapter-aware (“install mpv adapter to use this”).

---

## 124) i3 binding generation: add proven fixes for X11 “stuck key” scenarios

### 124.1 When i3 hotkeys + xdotool don’t work: send keyup for the binding keys
A common failure is: the keybound shortcut remains logically “down,” and the injected key never behaves as expected. One workaround is to explicitly send `keyup` for keys in the binding before sending the next key.  
Ref: https://stackoverflow.com/questions/51180405/xdotool-commands-bound-to-key-shortcuts-doesnot-work

**Low-hanging Studio export feature:**
- When generating `bindsym` commands that call our runner (or xdotool-like backends), optionally add:
  - “release binding keys first” behavior
- This complements `bindsym --release` and helps in edge cases.

### 124.2 Undocumented repeat knobs (xdotool key repeat/repeat-delay)
There are community reports that xdotool’s `key/keydown/keyup` support `--repeat` and `--repeat-delay`, even if not documented in some manpages.  
Ref: https://ubuntu-mate.community/t/some-xdotool-tips/30689

**Low-hanging Studio features:**
- Add `repeat` and `repeat_delay` fields to “Send Key” steps.
- If using a CLI adapter backend, pass through the flags when available.
- If using a native backend, implement the equivalent natively.

---

## 125) “Unstick everything” panic button: use x11vnc -clear_keys as a recovery tool

When modifiers/keys get stuck and the desktop becomes unusable, a real field-tested trick is to run:
`x11vnc -deny_all -clear_keys -timeout 1` (often over ssh), which clears pressed keys.  
Ref: https://unix.stackexchange.com/questions/60007/how-to-force-release-of-a-keyboard-modifiers

**Low-hanging Studio feature:**
- Doctor panel: “Emergency: Clear stuck keys” (requires x11vnc installed)
- Provide the exact command with DISPLAY/XAUTHORITY hints
- Optionally run it automatically if user confirms (local only)

This is a huge quality-of-life win for macro development.

---

## 126) Window event watching backends: wmutils opt as a lightweight alternative

wmutils’ optional addons (“opt”) include tools for dealing with window events and names, reinforcing that “event watcher” is a power-user primitive.  
Refs:
- https://github.com/wmutils/opt
- https://www.freshports.org/x11/wmutils-opt/

**Low-hanging Studio integration:**
- Allow an optional “wmutils watcher backend” for:
  - simple event stream capture
  - quick window name/attr inspection
- Even if we build our own event watcher, wmutils provides a pragmatic fallback and a model for “do one job well.”

---

## 127) Backlog updates from this revision

### P0
- Adapter framework (capabilities + deps + templates)
- sxiv selection-hook adapter (stdin list → per-item macro)
- kitty remote control adapter (send-text + match builder)
- mpv IPC adapter (basic set/get/observe)
- zathura exec adapter (simple external command)
- i3 binding exporter: optional “release binding keys first” mode
- Doctor: “Emergency clear stuck keys” helper

### P1
- Adapter gallery (browse, install/enable, templates)
- “Pick target” UI for kitty/mpv/zathura (where possible)
- Adapter triggers (“OnTrackChanged”, etc.) into the Trigger palette

---

## 128) Research links added in this revision
- sxiv key-handler protocol (stdin list, blocks until complete, reload modified): https://sources.debian.org/src/sxiv/26-1/exec/key-handler  
- kitty remote control + send-text matching: https://sw.kovidgoyal.net/kitty/remote-control/  
- mpv JSON IPC recommendation: https://mpv.io/manual/stable/  
- zathura documentation (exec + D-Bus): https://pwmt.org/projects/zathura/documentation/  
- i3 + xdotool keyup workaround: https://stackoverflow.com/questions/51180405/xdotool-commands-bound-to-key-shortcuts-doesnot-work  
- xdotool repeat tips: https://ubuntu-mate.community/t/some-xdotool-tips/30689  
- x11vnc -clear_keys stuck modifiers recovery: https://unix.stackexchange.com/questions/60007/how-to-force-release-of-a-keyboard-modifiers  
- wmutils opt: https://github.com/wmutils/opt and https://www.freshports.org/x11/wmutils-opt/

---

## 129) Monitor/layout change is a first-class automation trigger (autorandr + RandR notify)

Multi-monitor changes are a constant source of macro brittleness:
- coordinates shift
- windows move between outputs
- your “search region” becomes wrong

We should treat display changes as **events** and provide “repair steps” and profiles.

### 129.1 autorandr: “display profiles” that auto-apply when monitors change
**autorandr** detects connected display hardware and loads a saved profile using `xrandr`; it also supports explicit profile names and auto-detect via `--change`.  
Refs:
- autorandr man page (profiles, auto-detect): https://manpages.ubuntu.com/manpages/jammy/man1/autorandr.1.html
- AskUbuntu recipe for save/restore with `autorandr --save` / `autorandr --change`: https://askubuntu.com/questions/754231/how-do-i-save-my-new-resolution-setting-with-xrandr
- Practical i3 multi-monitor write-up: https://amcrouch.medium.com/automatic-i3-multiple-monitor-configuration-with-autorandr-a5816d899ad0

**Low-hanging Studio features**
- Step: `Display.ApplyProfile(name|auto)` implemented as:
  - `autorandr --change` or `autorandr --load <name>`
- Project setting: “Run autorandr on startup” (optional)
- Trigger: `OnDisplayProfileChanged` (best-effort; detect from autorandr output or via event stream)

### 129.2 True event subscription: XRandR notifications (no polling)
At the Xlib level, you can subscribe to screen configuration changes with RandR:
- call `XRRSelectInput(..., RRScreenChangeNotifyMask)` and get `XRRScreenChangeNotifyEvent`.  
Ref: https://stackoverflow.com/questions/10400236/how-to-observe-changes-in-connected-monitors-via-xlib

**Low-hanging Studio feature**
- Trigger: `OnDisplayChanged` (fires on RandR events)
- Runner policy option:
  - “Pause macro if display changes” (safe default for long macros)
  - “Auto-recompute regions relative to window/client area” (where possible)

### 129.3 CLI notify helper: xrandr-notify
There’s a small utility **xrandr-notify** that subscribes to monitor/display property changes and prints events, designed for scripting.  
Ref: https://github.com/pjvds/xrandr-notify

**Low-hanging prototype path**
- implement `OnDisplayChanged` by running `xrandr-notify` in a MonitorAdapter
- swap to native XRandR event subscription later

---

## 130) Key repeat & typing rate control (xset): a cheap way to stabilize some macros

Some workflows (games, terminals, accessibility) are very sensitive to:
- key repeat delay
- repeat rate
- autorepeat on/off

`xset` supports `r rate <delay> <rate>` to set repeat delay/rate; the xset man page documents this.  
Ref: xset man page (autorepeat delay/rate): https://www.x.org/releases/current/doc/man/man1/xset.1.xhtml  
Community examples confirm `xset r rate MS_DELAY RATE`.  
Ref: https://bbs.archlinux.org/viewtopic.php?id=60233

**Low-hanging Studio features**
- Step: `Keyboard.SetRepeat(delay_ms, rate_hz)`
- Step: `Keyboard.DisableRepeat()` / `Keyboard.EnableRepeat()`
- Runner option: “Temporarily set repeat profile during macro run”
  - store previous values via `xset -q`
  - restore after run (even on failure)
- Doctor check: verify XKB availability and explain when settings don’t stick.

---

## 131) Geometry-only region selection: xrectsel as a great Capture Mode building block

We already plan a universal Capture Mode (slop/maim-inspired). Another very cheap, very useful primitive is **xrectsel**:
- user drags a rectangle and it prints geometry to stdout
- supports formatting output (`-f "--x=%x --y=%y --width=%w --height=%h"`)  
Refs:
- xrectsel repo (geometry output and formatting): https://github.com/ropery/xrectsel
- python-xrectsel readme (example output): https://github.com/digitronik/python-xrectsel

**Low-hanging Studio features**
- Backend option for “Select Region → geometry”:
  - use xrectsel when installed
  - fall back to slop otherwise
- “Copy geometry” format presets:
  - `WxH+X+Y`
  - `--x= --y= --width= --height=`
  - JSON object (for our own steps)
- Step builder affordance:
  - any step with a region can have a “Select Region…” button that uses xrectsel.

---

## 132) Backlog updates from this revision

### P0
- OnDisplayChanged trigger (xrandr-notify prototype → XRandR native later)
- Display.ApplyProfile step (autorandr integration) + template “fix monitors then restore workspace project”
- Pause/abort macro on display change (runner safety option)
- Keyboard repeat steps (SetRepeat/DisableRepeat/Restore)
- xrectsel region selector backend + geometry format presets

### P1
- Full XRandR event subscription (XRRSelectInput) + richer payload (outputs changed)
- “Display-aware regions” mode:
  - re-map regions when monitor scale/layout changes
  - warn when a region is tied to a missing output

---

## 133) Research links added in this revision
- autorandr profiles and auto-detect:
  - https://manpages.ubuntu.com/manpages/jammy/man1/autorandr.1.html
  - https://askubuntu.com/questions/754231/how-do-i-save-my-new-resolution-setting-with-xrandr
  - https://amcrouch.medium.com/automatic-i3-multiple-monitor-configuration-with-autorandr-a5816d899ad0
- RandR event subscription (XRRSelectInput): https://stackoverflow.com/questions/10400236/how-to-observe-changes-in-connected-monitors-via-xlib
- xrandr-notify: https://github.com/pjvds/xrandr-notify
- xset repeat delay/rate: https://www.x.org/releases/current/doc/man/man1/xset.1.xhtml and https://bbs.archlinux.org/viewtopic.php?id=60233
- xrectsel geometry selection:
  - https://github.com/ropery/xrectsel
  - https://github.com/digitronik/python-xrectsel

---

## 134) “Comfort controls” as macro steps: brightness + color temperature + monitor power

This is low-hanging fruit that immediately makes the tool feel like a *desktop automation studio*, not just “keyboard macros.”
People already bind these to hotkeys in i3; we should formalize them as steps/triggers and integrate them into the Doctor.

### 134.1 Internal display/backlight control
Common backends:
- **brightnessctl** (sysfs backlight devices; supports absolute/relative/percent sets)  
  Refs:
  - brightnessctl man page: https://man.archlinux.org/man/extra/brightnessctl/brightnessctl.1.en
  - ArchWiki Backlight: https://wiki.archlinux.org/title/Backlight
- **xbacklight** (RandR-based; often works for laptop panels; may not work for external monitors)  
  Refs:
  - StackOverflow usage: https://stackoverflow.com/questions/25588367/how-to-control-backlight-by-terminal-command
  - Notes that xbacklight uses RandR: https://www.freshports.org/x11/xbacklight/

**Low-hanging Studio steps:**
- `Backlight.Set(value)` where value supports:
  - `50%`, `+10%`, `-10%`, `+50`, etc. (brightnessctl-style semantics)
- `Backlight.Get() -> var`
- `Backlight.Smooth(to, duration)` (optional; brightnessctl docs mention smooth transitions in some articles)

**Doctor checks (practical):**
- list brightness devices (`brightnessctl -l`) and show the chosen device
- warn when no sysfs backlight device exists (common on desktops)

### 134.2 External monitor brightness via DDC/CI (ddcutil)
xbacklight generally won’t control external monitors; **DDC/CI** is the standard approach.

**ddcutil** provides `setvcp 10` (VCP code 10 = brightness) and supports relative adjustments:
- `ddcutil setvcp 10 + 5` / `ddcutil setvcp 10 - 5`  
  Ref: ddcutil setvcp examples: https://www.ddcutil.com/command_setvcp/
- A practical write-up notes you may need udev rules/i2c permissions to run without root.  
  Ref: https://def.lakaban.net/2021-06-25-ddcutil-controlling-the-brightness-of-an-external-monitor/

**Low-hanging Studio steps:**
- `Monitor.SetBrightness(monitor=auto|id, value|delta)`
  - internal monitor: brightnessctl backend
  - external monitor: ddcutil backend
- `Monitor.SetContrast(...)` (VCP 12 commonly; optional)
- `Monitor.ListDDC() -> table` and “Test now”

**Doctor checks:**
- detect DDC/CI capability
- explain permissions (i2c access) and provide udev guidance link
- warn users that not all displays support DDC/CI reliably

### 134.3 Color temperature (night mode) via redshift / gammastep
This belongs because it’s “one-line automation” users actually do.

- redshift: `redshift -O <temp>` sets temperature, `redshift -x` resets  
  Ref: https://askubuntu.com/questions/565963/how-can-i-set-a-certain-temperature-on-redshift  
  ArchWiki also documents `-P -O` usage: https://wiki.archlinux.org/title/Redshift
- gammastep: redshift alternative; CLI tool with documented options  
  Ref: https://manpages.ubuntu.com/manpages/noble/man1/gammastep.1.html

**Low-hanging Studio steps:**
- `Screen.SetColorTemp(kelvin)` (backend: redshift or gammastep)
- `Screen.ResetColorTemp()`

**Template macros:**
- “Focus mode”: set temp warmer + lower brightness + pause notifications
- “Video mode”: reset temp + raise brightness + disable hot corners

### 134.4 Monitor power (DPMS) steps
Turning the display off (without sleeping the whole machine) is a common ask.

- DPMS via xset: `xset dpms force off`  
  Ref: ArchWiki DPMS: https://wiki.archlinux.org/title/Display_Power_Management_Signaling  
  Also commonly referenced: https://forums.raspberrypi.com/viewtopic.php?t=281523
- Note: screens can turn back on due to activity/events, which users report.  
  Ref: https://unix.stackexchange.com/questions/4466/screen-turns-on-automatically-xset-dpms-force-off

**Low-hanging Studio steps:**
- `Display.PowerOff()` (xset dpms force off)
- `Display.PowerOn()` (best-effort; often any input wakes it)
- `Display.DisableDPMS()` / `Display.EnableDPMS()` (optional)

**Triggers:**
- Combine with OnIdle/OnLock triggers already in the doc:
  - “OnIdle → DPMS off”
  - “OnUnlock → DPMS on + restore brightness profile”

---

## 135) Status bar integration: steal i3blocks’ click+signal model

A killer UX feature is seeing “macro status” in your bar and being able to click it:
- running / paused
- last run success/failure
- quick open logs / stop macro

**i3blocks** explicitly supports:
- scheduling commands at intervals
- executing blocks upon **signal reception**
- executing blocks on **clicks**  
Ref: https://vivien.github.io/i3blocks/

### 135.1 Low-hanging Studio features
- Generate an i3blocks block that:
  - reads a small status file in the project/run directory
  - prints “VHK: idle/running/paused”
  - outputs color based on state (optional)
- On macro start/stop:
  - update the status file
  - send signal to i3blocks to refresh (i3blocks supports signal-based refresh)
- Click handlers:
  - Left click: open last run folder
  - Middle click: pause/resume
  - Right click: stop macro

### 135.2 “Bar-first” discoverability
If you ship a default i3blocks block for VHK:
- users discover macros by clicking the bar
- you get a consistent “control surface” even without opening the full UI

---

## 136) Backlog updates from this revision

### P0
- Brightness steps:
  - brightnessctl backend (internal)
  - ddcutil backend (external)
- Color temperature steps (redshift/gammastep backend auto-detect)
- DPMS steps (xset dpms force off)
- Doctor checks for:
  - backlight devices present
  - DDC/CI support + permissions
  - redshift/gammastep presence
- i3blocks integration:
  - generate block + status file
  - update+signal on macro state changes
  - click-to-control hooks

### P1
- “Brightness profile” support per workspace project (combine with autorandr)
- A “comfort preset” editor:
  - brightness + temp + DPMS
  - bind presets to gestures/hotkeys

---

## 137) Research links added in this revision
- brightnessctl & backlight:
  - https://man.archlinux.org/man/extra/brightnessctl/brightnessctl.1.en
  - https://wiki.archlinux.org/title/Backlight
- xbacklight basics: https://stackoverflow.com/questions/25588367/how-to-control-backlight-by-terminal-command and https://www.freshports.org/x11/xbacklight/
- ddcutil brightness (VCP 10) examples: https://www.ddcutil.com/command_setvcp/ and permissions note: https://def.lakaban.net/2021-06-25-ddcutil-controlling-the-brightness-of-an-external-monitor/
- redshift set/reset: https://askubuntu.com/questions/565963/how-can-i-set-a-certain-temperature-on-redshift and ArchWiki: https://wiki.archlinux.org/title/Redshift
- gammastep man page: https://manpages.ubuntu.com/manpages/noble/man1/gammastep.1.html
- DPMS: https://wiki.archlinux.org/title/Display_Power_Management_Signaling and wake caveat: https://unix.stackexchange.com/questions/4466/screen-turns-on-automatically-xset-dpms-force-off
- i3blocks signals+clicks: https://vivien.github.io/i3blocks/

---

## 138) “Focus mode / Do Not Disturb” as a first-class primitive (Dunst pause levels)

A huge fraction of “automation” is about controlling interruptions:
- pause notifications while a macro runs
- let only urgent notifications through
- resume and optionally replay missed notifications

**Dunst** supports both a simple paused state and a more nuanced **pause level**:
- `dunstctl set-paused true|false|toggle` and `dunstctl is-paused`  
  Ref: https://dunst-project.org/documentation/dunstctl/
- `dunstctl set-pause-level <0..100>` and `get-pause-level`, enabling “let urgent through” by configuring override levels.  
  Ref: https://dunst-project.org/documentation/dunstctl/  
  (ArchWiki also documents `dunstctl set-paused`/`is-paused`.)  
  Ref: https://wiki.archlinux.org/title/Dunst
- Dunst’s own README highlights pausing and mentions a numeric pause level concept.  
  Ref: https://github.com/dunst-project/dunst

### 138.1 Low-hanging Studio steps
- `Notifications.Pause()` / `Notifications.Resume()` / `Notifications.Toggle()`
- `Notifications.SetPauseLevel(level)` / `GetPauseLevel()`
- Runner option: **Auto Focus Mode while macro running**
  - on start: save pause state/level → set pause level (default 100)
  - on end: restore previous pause state/level
- Template macro:
  - “Focus mode”: pause notifications + lower brightness + warm color temp (see v24)

### 138.2 Cheap UX win: integrate with your bar
We already planned i3blocks integration; add a “DND indicator” block:
- click toggles dunst pause (common community pattern).  
  Ref example tutorial: https://trunc8.github.io/2021/07/29/tut-dunst-toggle

---

## 139) “Keep the machine awake while the macro runs” (systemd inhibitors + X screensaver settings)

Long macros (or automation-driven demos/kiosks) often fail because:
- the system sleeps
- the screen blanks
- the session locks

### 139.1 systemd-inhibit: the correct OS-level primitive
`systemd-inhibit` executes a program while holding an inhibitor lock against shutdown/sleep/idle handling, releasing it afterward.  
Refs:
- man page: https://www.freedesktop.org/software/systemd/man/systemd-inhibit.html  
- systemd inhibitor locks overview: https://systemd.io/INHIBITOR_LOCKS/

**Low-hanging Studio feature:** a runner wrapper:
- `RunMacro(with_inhibit=idle|sleep|shutdown|all)`
- Implementation:
  - launch macro runner through `systemd-inhibit --what=idle:sleep ... <runner>`
- Doctor note:
  - inhibitor locks can affect automatic idle handling; the effect depends on your desktop’s configuration.

### 139.2 X11-specific: disable screensaver/blanking during macro run (xset)
Even if the system doesn’t “sleep,” X can blank the screen.
`xset` can disable the X screensaver and DPMS blanking:
- `xset s off` (turn off screen saver) and `xset -dpms` (disable DPMS) are common recipes.  
  Refs:
  - xset man page (`s ... on/off`): https://www.x.org/archive/X11R7.5/doc/man/man1/xset.1.html  
  - SuperUser answer listing `xset s off`, `xset s noblank`, `xset -dpms`: https://superuser.com/questions/644804/disable-screensaver-screen-blank-via-command-line  
  - AskUbuntu note that `xset s off` is sometimes necessary to prevent compiled-in default blanking: https://askubuntu.com/questions/67355/how-do-i-completely-turn-off-screensaver-and-power-management
- A good deep-dive explains that X offers multiple blanking systems (BlankTime vs DPMS), queryable via `xset -q`.  
  Ref: https://shallowsky.com/linux/x-screen-blanking.html

**Low-hanging Studio steps:**
- `ScreenSaver.Disable()` / `ScreenSaver.Enable()` (xset s off/on)
- `DPMS.Disable()` / `DPMS.Enable()` (xset -dpms/+dpms)
- `BlankingProfile.Push()` / `BlankingProfile.Pop()`:
  - snapshot current `xset -q` state and restore at end
- Runner option:
  - “Prevent blanking while macro runs” (default ON for long-running macros)

---

## 140) Target windows by PID/process reliably (xdotool getwindowpid)

Window targeting is stronger when you can tie windows back to the owning process.

### 140.1 xdotool provides getwindowpid
The xdotool man page documents `getwindowpid` and shows using it in pipelines (e.g., find PIDs for windows found by search).  
Ref: https://manpages.ubuntu.com/manpages/trusty/man1/xdotool.1.html

There are also common recipes using `_NET_WM_PID` via xprop + xdotool’s focused window id.  
Ref: https://askubuntu.com/questions/245428/how-to-know-the-pid-of-active-window

**Low-hanging Studio features:**
- Inspector: show window PID + process name (best effort)
- Selector option: “bind to process pid/name”
  - useful for “only trigger macro in this process”
- Trigger: `OnProcessWindowFocused(process=...)` (composed from focus events + PID match)
- Step: `Window.KillProcess()` (dangerous; keep behind confirmation)
- Doctor: “_NET_WM_PID missing” warning
  - some apps/WMs don’t expose it reliably (fallback to i3 IPC tree + WM_CLASS)

---

## 141) Backlog updates from this revision

### P0
- Dunst adapter:
  - pause/resume/toggle
  - pause level set/get
  - runner “auto focus mode” wrapper
- systemd-inhibit wrapper for macros (idle/sleep/shutdown)
- X blanking wrapper (xset s off / -dpms) with snapshot/restore
- Inspector: show window PID/process, and process-based selectors

### P1
- “Macro Run Transaction” wrapper:
  - save/restore notifications pause level
  - save/restore blanking state
  - save/restore volume/brightness/temp (from earlier revisions)
  - one place to control “side effects”

---

## 142) Research links added in this revision
- Dunst pause controls and pause level:
  - https://dunst-project.org/documentation/dunstctl/
  - https://wiki.archlinux.org/title/Dunst
  - https://github.com/dunst-project/dunst
- systemd inhibitors:
  - https://www.freedesktop.org/software/systemd/man/systemd-inhibit.html
  - https://systemd.io/INHIBITOR_LOCKS/
- X blanking control:
  - https://www.x.org/archive/X11R7.5/doc/man/man1/xset.1.html
  - https://superuser.com/questions/644804/disable-screensaver-screen-blank-via-command-line
  - https://askubuntu.com/questions/67355/how-do-i-completely-turn-off-screensaver-and-power-management
  - https://shallowsky.com/linux/x-screen-blanking.html
- Window PID targeting:
  - https://manpages.ubuntu.com/manpages/trusty/man1/xdotool.1.html
  - https://askubuntu.com/questions/245428/how-to-know-the-pid-of-active-window
- i3bar notification toggle pattern example:
  - https://trunc8.github.io/2021/07/29/tut-dunst-toggle

---

## 143) Confirmations and “nag” prompts: steal i3‑nagbar (zero-dependency UX win)

When you need a quick user confirmation (especially while a macro is running), i3 already ships a built-in prompt UI: **i3-nagbar**.  
It supports message text and buttons that execute shell commands (example in the man page).  
Ref: https://man.archlinux.org/man/extra/i3-wm/i3-nagbar.1.en

### 143.1 Low-hanging Studio step types
- `Prompt.Confirm(message, ok_label="OK", cancel_label="Cancel") -> bool`
  - backend: i3-nagbar (default for i3 users)
- `Prompt.Choice(message, buttons=[(label, value), ...]) -> value`
- `Prompt.Nag(message, buttons=[...], timeout?, urgency?)` (non-blocking notice)

### 143.2 Safety guardrails (do this by default)
- For button actions, run a **Studio command** (IPC) rather than arbitrary shell by default:
  - i3-nagbar runs “button commands”; we should have those call `vhkctl <action>` so the Studio remains in control.
- Provide an “Allow shell commands” toggle only in advanced settings, with warnings.

### 143.3 Known UX gap (keyboard control)
There’s an open issue requesting keyboard navigation in i3-nagbar (arrow keys / vim keys / Enter/Escape).  
Ref: https://github.com/i3/i3/issues/4248  
**Implication:** keep alternative prompt backends (rofi, whiptail, etc.) available.

---

## 144) Workspace button programmability: i3bar “workspace buttons command” as a macro surface

Since **i3 4.23**, i3bar can run a program and use its stdout to define the workspace buttons displayed on the left side of the bar (rename, hide, reorder, show non-existent workspaces, etc.).  
Ref: https://i3wm.org/docs/userguide.html (section “Workspace buttons command”)

### 144.1 Low-hanging uses in our Studio
- **Project-aware workspace labels**
  - If a workspace is a “Workspace Project,” show a short project label/icon on its button.
- **Macro status on the workspace strip**
  - Show a tiny marker like `●` or `RUN` next to the active workspace while a macro is running there.
- **Template health indicator**
  - If a project template has missing/swallow-mismatch windows, show `!` on that workspace button.

### 144.2 Low-hanging generator feature
- “Generate workspace-buttons command script”
  - a small script that reads a Studio state file (run folder/status JSON) and prints the button JSON
  - the Studio updates the state file on macro start/stop

This complements i3blocks: i3blocks gives you a “status block,” while workspace-buttons gives you “workspace-aware status.”

---

## 145) Terminal automation adapters: tmux (and why it’s better than vision for terminals)

Terminals are a common macro target; vision is fragile here. **tmux** exposes a scriptable command interface that is far more reliable.

Refs:
- tmux man page (command interface, bindings overview): https://man7.org/linux/man-pages/man1/tmux.1.html  
- “Scripting tmux” notes send-keys target pitfalls and recommends explicit targets: https://tao-of-tmux.readthedocs.io/en/latest/manuscript/10-scripting.html  
- Capturing output via `capture-pane` is a common technique: https://stackoverflow.com/questions/12665625/how-to-get-the-result-of-send-keys-in-tmux

### 145.1 Low-hanging Studio adapter: “tmux”
Steps:
- `Tmux.SendKeys(target, keys, enter=true)`
- `Tmux.RunCommand(target, command)` (wrap send-keys)
- `Tmux.CapturePane(target, lines=200) -> text`
- `Tmux.SelectPane(target)` / `SelectWindow` / `SelectSession`
- `Tmux.NewSession(name, command?, cwd?)` (optional)
- `Tmux.SplitPane(target, direction, percent?)` (optional)

Triggers (optional v2):
- “OnTmuxPaneActivity” is non-trivial; defer unless using hooks.

### 145.2 Low-hanging “why it didn’t work” diagnostics
- If `send-keys` without `-t` sends to “current pane,” scripts can misbehave if the target is not the attached client (and keys can appear before the prompt).  
  Ref: https://tao-of-tmux.readthedocs.io/en/latest/manuscript/10-scripting.html  
**Studio policy:** always require/derive an explicit target.

---

## 146) Terminal automation adapters: WezTerm CLI (paste-like send-text)

WezTerm exposes `wezterm cli send-text` which sends text “as though it were pasted,” using bracketed paste when enabled.  
Ref: https://wezterm.org/cli/cli/send-text.html

WezTerm also supports focusing a pane via `wezterm cli activate-pane --pane-id`.  
Ref: https://wezterm.org/cli/cli/activate-pane.html

### 146.1 Low-hanging Studio adapter: “wezterm”
Steps:
- `Wezterm.SendText(pane_id|current, text, bracketed=true)`
- `Wezterm.ActivatePane(pane_id)`
- (optional) `Wezterm.ListPanes()` (needs further research of CLI listing commands; treat as v2)

**Why it’s great:** it bypasses X11 typing weirdness (it’s paste-like and aware of bracketed paste).

---

## 147) Browser automation without scraping: qutebrowser userscripts as a first-class adapter

qutebrowser is designed to be extended via **userscripts**, invoked via `:spawn --userscript` or key bindings.  
Refs:
- qutebrowser command docs for `:spawn`: https://qutebrowser.org/doc/help/commands.html  
- userscripts docs: scripts can read env vars and write commands to a FIFO; can be invoked via key binding and via hints to pass selected URLs: https://qutebrowser.org/doc/userscripts.html

### 147.1 Low-hanging Studio adapter: “qutebrowser”
- Step: `Qute.Userscript(name, args?, input?)`
- Step: `Qute.HintUserscript(...)` (“run this userscript on selected link(s)”)
- Trigger (optional):
  - userscript invoked → sends event back to Studio via IPC (because userscripts can write to FIFO; our userscript can also call `vhkctl event ...`)

### 147.2 Template macros (instant value)
- “Run userscript on highlighted links and collect results”
- “Open selected URLs in a different profile”
- “Copy page title/url to clipboard and format it”

---

## 148) Backlog updates from this revision

### P0
- i3-nagbar prompt steps (Confirm / Choice) + safe IPC button actions
- Workspace buttons command generator (project-aware workspace labels/status)
- tmux adapter (SendKeys + CapturePane) with explicit target policy
- WezTerm adapter (SendText + ActivatePane)
- qutebrowser adapter (userscripts + hints integration)

### P1
- A “Adapters Gallery” with install checks and templates (kitty/mpv/tmux/wezterm/qute)
- A “Workspace Projects UI” that can export:
  - i3 layout template
  - i3bar workspace buttons script
  - i3blocks status block (optional)
  - rofi palette entries

---

## 149) Research links added in this revision
- i3-nagbar: https://man.archlinux.org/man/extra/i3-wm/i3-nagbar.1.en  
- i3-nagbar keyboard nav issue: https://github.com/i3/i3/issues/4248  
- i3bar workspace buttons command: https://i3wm.org/docs/userguide.html  
- tmux scripting and capture:
  - https://man7.org/linux/man-pages/man1/tmux.1.html
  - https://tao-of-tmux.readthedocs.io/en/latest/manuscript/10-scripting.html
  - https://stackoverflow.com/questions/12665625/how-to-get-the-result-of-send-keys-in-tmux
- WezTerm CLI:
  - https://wezterm.org/cli/cli/send-text.html
  - https://wezterm.org/cli/cli/activate-pane.html
- qutebrowser commands/userscripts:
  - https://qutebrowser.org/doc/help/commands.html
  - https://qutebrowser.org/doc/userscripts.html

---

## 150) Keyboard-driven mouse for “visual targeting without a mouse”: steal keynav

A lot of macro building involves repeatedly:
- moving the cursor to a precise UI element
- selecting a tight region
- clicking small targets

For keyboard-heavy i3 users (and accessibility), **keynav** is a perfect “adapter”:
- it turns keyboard strokes into fast pointer movement using a binary-splitting UI (“move toward quadrant” style)  
Ref: https://www.semicomplete.com/projects/keynav/  
It’s also recommended in general “control mouse with keyboard” discussions.  
Ref: https://askubuntu.com/questions/276413/control-mouse-with-keyboard-and-web-browsing

### 150.1 Low-hanging Studio integration
- Adapter: `Keynav.Start()` / `Keynav.Stop()` (launch keynav and focus it)
- “Pick point with keyboard” tool:
  - start keynav
  - user navigates to point
  - Studio reads `xdotool getmouselocation --shell` and captures x/y (already referenced earlier)
- Use cases:
  - create a pixel watch point without touching a mouse
  - pick tiny hit targets to define click points for needles

### 150.2 Creative UX
- “Keynav-assisted Capture Mode”:
  - define region corners via two picked points (top-left, bottom-right)
  - this is extremely handy for precise OCR/pixel search regions

---

## 151) “Show keystrokes on screen” for debugging, demos, and template videos: steal screenkey

When a macro is being debugged or taught, one of the best ways to understand “what happened” is seeing the key stream on screen.

**screenkey** is a well-known tool that displays your keys, intended for screencasts.  
Ref: https://www.thregr.org/wavexx/software/screenkey/  
A practical note: screenkey is X11-centric; it won’t capture input directed to native Wayland programs, which is fine for our i3/X11 scope.  
Ref: https://www.omgubuntu.co.uk/screenkey-show-key-presses-screen-ubuntu

### 151.1 Low-hanging Studio features
- Runner toggle: “Show keys while running”:
  - launches screenkey with a profile (font size, position, timeout)
  - stops it automatically at end (even on failure)
- Recorder “annotation mode”:
  - while recording, optionally show a small key overlay to help the user avoid confusion
- Support Bundle option:
  - record a short GIF/WebM + keys overlay for perfect bug reports (pairs well with the evidence capture features)

---

## 152) Visual diff as a primitive (beyond “did it match?”): steal ImageMagick `compare`

We already added “VisualAssert/Verify” concepts. A low-effort way to make them great is to steal ImageMagick’s `compare` tool:
- it can produce a **difference image** plus **numeric metrics** about how different two images are  
Ref: ImageMagick Compare docs: https://imagemagick.org/script/compare.php  
Ref: example usage: https://usage.imagemagick.org/compare/  
And the “does diff exist for images” answer shows it as a canonical solution on Linux.  
Ref: https://askubuntu.com/questions/209517/does-diff-exist-for-images

### 152.1 Low-hanging Studio step types
- `Visual.Diff(region, baseline_needle, output_diff_path) -> metric`
  - stores:
    - diff image
    - metric (AE, RMSE, PSNR, etc. depending on backend)
- `Visual.AssertSame(...)` / `Visual.VerifySame(...)` with threshold

### 152.2 Low-hanging “small differences are hard to see” UX
ImageMagick users explicitly struggle to spot tiny differences; build UI affordances:
- auto-draw rectangles around diff clusters
- zoom to the first differing area
- “blink” baseline vs current

This makes “visual testing” actually usable.

### 152.3 How this connects to needles
Needles already have:
- exclude areas / ignore zones
So implement diff with:
- mask out ignore zones before comparing
- compare only within match areas where appropriate

---

## 153) Hot corners and screen edges: make behave_screen_edge robust and observable

Hot corners are a very popular “automation trigger” on X11.
`xdotool behave_screen_edge` supports `--delay` and `--quiesce` which are critical for debouncing.  
Ref: xdotool man page (behave_screen_edge options): https://man.archlinux.org/man/xdotool.1.en  
AskUbuntu includes an “event timeline” explanation (hit edge → wait delay → trigger → cooldown).  
Ref: https://askubuntu.com/questions/601074/perform-action-when-moving-mouse-cursor-to-certain-position-in-lubuntu-hot-corn

There are also reports and issues around behave_screen_edge behavior (timeouts, nested exec, etc.), which reinforces that we should treat it as a backend and not a spec.  
Ref: xdotool issue example: https://github.com/jordansissel/xdotool/issues/193

### 153.1 Low-hanging Studio features (polish the trigger)
- Trigger UI:
  - pick edge/corner visually (in Capture Mode overlay)
  - set delay/quiesce with sliders
  - show a “cooldown countdown” indicator when triggered (debug overlay)
- Add an “activity guard” option:
  - only fire if mouse is still in corner after delay
  - optionally require the edge dwell to be “stable” (no rapid leave/return)

### 153.2 Alternative backend (if behave_screen_edge is flaky)
Add a fallback implementation:
- subscribe to pointer motion events (or poll `getmouselocation` at low rate)
- implement delay/quiesce in our engine
This avoids external process issues and makes behavior consistent.

---

## 154) Backlog updates from this revision

### P0
- Keynav adapter + “keyboard pick point” tool
- Screenkey runner toggle + support-bundle integration
- ImageMagick compare backend for VisualDiff/Assert/Verify
- Hot corner trigger UI polish (delay/quiesce, cooldown overlay, capture-mode picker)
- Hot corner fallback backend implemented in-engine

### P1
- Needle diff viewer:
  - zoom to first difference
  - highlight clusters
  - “blink compare”
- Region selection via two keyboard-picked points (Keynav-assisted capture)

---

## 155) Research links added in this revision
- keynav: https://www.semicomplete.com/projects/keynav/ and AskUbuntu keynav mention: https://askubuntu.com/questions/276413/control-mouse-with-keyboard-and-web-browsing  
- screenkey: https://www.thregr.org/wavexx/software/screenkey/ and X11/Wayland note: https://www.omgubuntu.co.uk/screenkey-show-key-presses-screen-ubuntu  
- ImageMagick compare: https://imagemagick.org/script/compare.php and examples: https://usage.imagemagick.org/compare/ and AskUbuntu “diff for images”: https://askubuntu.com/questions/209517/does-diff-exist-for-images  
- behave_screen_edge options and timeline: https://man.archlinux.org/man/xdotool.1.en and https://askubuntu.com/questions/601074/perform-action-when-moving-mouse-cursor-to-certain-position-in-lubuntu-hot-corn and issue example: https://github.com/jordansissel/xdotool/issues/193

---

## 156) GUI inspiration: xdotool‑gui proves “record → edit → replay” UX is low-hanging

There’s already a maintained **GUI for xdotool** that records sequences and generates runnable command strings (“record xdotool sequences for X automation,” GTK3, Python 3).  
Ref: https://github.com/sickcodes/xdotool-gui

**Low-hanging Studio lessons to steal:**
- “Record → list of steps → replay” can be done with a simple timeline and a small palette.
- Provide one-click:
  - start/stop recording
  - save/load
  - replay selection
- Use the GUI to generate both:
  - visual workflow nodes
  - a text snippet users can paste into scripts (our DSL tab can output this)
- Treat xdotool‑style steps as a “backend adapter” early, then swap to native implementations later.

---

## 157) Separate “privileged helpers” are a proven pattern (Ui.Vision XModules)

Ui.Vision RPA runs as a browser extension but uses separate native helpers (“XModules”) for desktop automation. Their download page explicitly states there is a separate XModules installer for Windows/Mac/Linux, bundling modules like DesktopAutomation and ScreenCapture.  
Ref: https://ui.vision/rpa/x/download  
(Also summarized on their extension listing.) Ref: https://chromewebstore.google.com/detail/uivision/gcbalfbdmfieckjlnblleoemohcganoc

**Low-hanging architectural takeaway:**
- Keep the Studio “brain/UI” and the OS‑integration parts separable:
  - `vhk-ui` (safe, unprivileged, UI + editor)
  - `vhk-agent` (desktop automation + capture/injection + a11y)
  - optional `vhk-priv` helper (only if needed for uinput/ddcutil permissions)
- This makes:
  - packaging easier
  - security boundaries clearer
  - debugging simpler (restart agent without restarting UI)

**Low-hanging feature:** a “Modules” page that shows:
- which helpers are installed
- their versions
- what capabilities they provide
- test buttons (“can screenshot?”, “can inject?”, “can read a11y?”)

---

## 158) “Wait vs busy-loop” is a real product differentiator (macro recorder CPU burn lessons)

Two real-world data points worth baking into the spec:

1) Macro Recorder’s “Find image on screen” action is explicitly a **wait** action: it *pauses macro playback until it finds the image* in the search area.  
Ref: https://www.macrorecorder.com/doc/find/

2) Users of other macro recorders complain that an IF “image found” check can spin thousands of times and burn CPU because it’s implemented as a tight loop rather than a proper wait/backoff.  
Ref: https://stackoverflow.com/questions/70078520/jitbit-macro-recorder-if-image-statement-why-it-is-not-waiting-until-the-imag

**Low-hanging Studio requirements:**
- For any “Find/Detect” primitive (image/pixel/OCR/a11y):
  - provide both:
    - `Find` (one attempt)
    - `WaitUntilFound` (blocking with backoff + timeout)
- The visual editor should teach this pattern automatically:
  - when you add an IF based on image/pixel/OCR:
    - offer “convert to WaitUntilFound” or “add Wait before IF”
- Include a `RandomizeWait(min,max)` feature; Macro Recorder documents randomizing wait times.  
  Ref: https://www.macrorecorder.com/doc/wait/

---

## 159) Vision reliability “Doctor”: zoom and color filters break matching (Macro Recorder troubleshooting)

Visual matching (needles/image search) is sensitive to:
- browser zoom / UI scale
- color filters / night mode (redshift, f.lux-like)
Macro Recorder’s troubleshooting docs explicitly recommend keeping a consistent browser viewing scale and mention that blue-light filter software can affect the desktop color scheme and thus image-find reliability.  
Ref: https://www.macrorecorder.com/doc/troubleshooting/

**Low-hanging Studio “Vision Doctor” checks:**
- Detect (best-effort) whether:
  - redshift/gammastep is active (we already added steps; now add a warning link)
  - compositor effects or global filters are active (limited; at least warn users)
- Provide a “capture baseline at current zoom/scale” UX:
  - when capturing a needle, store:
    - scale factor
    - window size
    - browser zoom (if in-browser adapter exists later)
- Show a “Mismatch causes” panel on FindFailed:
  - “Did your zoom change?”
  - “Did your color temperature change?”
  - “Did your font/antialiasing change?”

This is cheap UI copy, but saves hours.

---

## 160) GUI binding editors exist and have footguns (xbindkeys‑config)

The xbindkeys ecosystem includes a GUI utility **xbindkeys-config**; a Linux.com article explicitly suggests it for GUI users, and warns it can crash when saving if you haven’t created a configuration file first.  
Ref: https://www.linux.com/news/start-programs-pro-xbindkeys/

**Low-hanging Studio features:**
- Treat “binding config” as a first-class artifact:
  - always create/save a project file before allowing binding export
- Provide “Export xbindkeys config” as a compatibility option:
  - helpful for users who already run xbindkeys and want our Studio to generate its bindings
- Provide app-specific hotkey patterns:
  - xbindkeys can be wrapped with “active window is X” checks (more complex; prefer i3 #HotIf-style logic in our own engine)
  - but include documentation and migration guidance.

---

## 161) uinput permission and socket pitfalls: bake them into the Doctor (ydotool lessons)

As you add deeper input injection backends (uinput / ydotool-style), you will run into:
- `/dev/uinput` permissions
- socket permission issues for helper daemons
A ydotool issue shows a real failure mode: the backend socket `/tmp/.ydotool_socket` created with permissions that block access even when the user is in the `input` group, motivating proper group/umask handling.  
Ref: https://github.com/ReimuNotMoe/ydotool/issues/73

**Low-hanging Studio actions:**
- Doctor “Input Injection” page:
  - checks:
    - can we open `/dev/uinput`? (if we support it)
    - are we in the right group?
    - is helper socket accessible?
  - output a *safe* remediation:
    - show exact permission issue
    - suggest least-privilege fixes (udev rules / group membership)
- If we ship a privileged helper:
  - ensure it creates sockets with group read/write and clear instructions.

---

## 162) Research links added in this revision
- xdotool-gui: https://github.com/sickcodes/xdotool-gui  
- Ui.Vision XModules:
  - https://ui.vision/rpa/x/download
  - https://chromewebstore.google.com/detail/uivision/gcbalfbdmfieckjlnblleoemohcganoc
- Macro Recorder “Find image pauses until found” and wait/randomize:
  - https://www.macrorecorder.com/doc/find/
  - https://www.macrorecorder.com/doc/wait/
  - troubleshooting (zoom + blue-light filters): https://www.macrorecorder.com/doc/troubleshooting/
- Busy-loop CPU burn example: https://stackoverflow.com/questions/70078520/jitbit-macro-recorder-if-image-statement-why-it-is-not-waiting-until-the-imag
- xbindkeys-config GUI warning: https://www.linux.com/news/start-programs-pro-xbindkeys/
- ydotool socket permission pitfall: https://github.com/ReimuNotMoe/ydotool/issues/73

---

## 163) Vision engine options: copy Macro Recorder’s “pixel vs feature matching vs auto” switch

We already plan template matching + multi-scale. A low-hanging, high-impact UX improvement is to explicitly expose **multiple detection methods** and let users pick per-needle (or per-step), like Macro Recorder does:

- Pixel-perfect bitmap comparison (fast but fragile)
- Feature matching (robust to DPI/zoom/rendering, but heavier and can false-positive)
- Auto (try to pick the suitable method)  
Ref: Macro Recorder “Image detection methods”: https://www.macrorecorder.com/doc/reference/image-detection-method/

Macro Recorder also clearly explains *why* pixel matching fails on modern desktops (font rendering differences, DPI scaling, anti-aliasing, subpixel rendering, GPU drivers, display profiles).  
Ref: https://www.macrorecorder.com/doc/reference/image-detection-method/

### 163.1 Low-hanging Studio feature spec
- Per-needle detection method:
  - `match_method = pixel | feature | auto`
- Per-needle match settings:
  - threshold (for pixel)
  - feature sensitivity / max candidates (for feature)
  - “prefer speed” vs “prefer robustness” (auto hint)
- Per-step override:
  - “use this method for this find”

### 163.2 Debug UI (make false positives visible)
Feature matching can return “close enough” matches. Add:
- “Show top N candidates” with confidence scores
- “Lock candidate” (choose which match to use if multiple)
- “Tighten region” suggestion (shrink search area)

---

## 164) Vision capture + troubleshooting: steal the hard-won “common mistakes” playbook

Macro Scheduler’s image-recognition troubleshooting list is basically a requirements checklist for any serious visual automation tool:
- always capture using the tool’s own capture system (color depth/format consistency)
- capture the object in the **same state** as runtime (focused vs unfocused, hover tooltip, pressed/selected states)
- don’t capture too much background (leads to many matches)
- handle multiple matches explicitly (don’t blindly click the first)
- timing/order matters; capture a screen image for diagnostics  
Ref: “Image Recognition Common Mistakes”: https://www.mjtnet.com/blog/2009/02/13/image-recognition-common-mistakes/

### 164.1 Low-hanging Studio “Vision Doctor” rules
- When a needle fails:
  - prompt: “Is the window focused/hovered state different than when you captured?”
  - offer: “Re-capture with delayed capture and focus setup”
- When a needle matches *multiple places*:
  - show “N matches found” and require a selection strategy:
    - first/best
    - nearest to anchor
    - inside a region
- When a needle includes a lot of flat background:
  - warn and suggest a tighter capture
- Always save “failure evidence”:
  - screenshot of the region at failure
  - diff vs needle (ImageMagick compare idea already added)
- Add “Delayed Capture” mode:
  - after user clicks “Capture,” wait 3–5 seconds so they can set focus/hover state, then capture.

### 164.2 Practical default: move cursor away before matching
The blog explicitly notes hover/tooltips and cursor-over states can change pixels.  
Ref: https://www.mjtnet.com/blog/2009/02/13/image-recognition-common-mistakes/

**Low-hanging runner default:**
- before ImageSearch steps:
  - move mouse to a known “safe corner” (or hide cursor, see cursor section)
  - optional: “ensure window focused/unfocused” matches capture metadata

---

## 165) “Test” button + overlay for every vision/a11y step (Macro Recorder UX)

Macro Recorder’s Find UI has:
- a bulb icon that overlays the selected region
- a Test button that runs the find with current settings
- search scope relative to desktop or active window  
Ref: Macro Recorder Find docs (scope + overlay/test): https://www.macrorecorder.com/doc/find/

### 165.1 Low-hanging Studio UX standard
Every step dialog that depends on targeting (needle, pixel, OCR, a11y) should include:
- **Preview region overlay**
- **Test now**
- “Show candidates” (if multiple results)
- “Insert wait wrapper” one-click

This makes macro construction much faster.

---

## 166) Voice triggers: integrate with Dragonfly2 (speech → macro) as an optional adapter

Voice control can be a huge productivity boost, and **Dragonfly** is a mature open-source voice automation framework that already supports X11 by using xdotool.  
Ref: Dragonfly Key/Text actions on X11 require xdotool and support Unicode keypoints: https://dragonfly2.readthedocs.io/en/stable/actions.html

### 166.1 Low-hanging Studio integration model
Do not reinvent speech recognition. Instead:
- Provide a CLI entrypoint: `vhkctl run <macro-id> [--args ...]`
- Provide a “Generate Dragonfly grammar” wizard:
  - user chooses macro(s)
  - assigns spoken phrases
  - wizard generates a python grammar file that calls `subprocess.run(["vhkctl","run",...])`
- Provide a “Voice adapter status” Doctor page:
  - checks:
    - dragonfly installed (optional)
    - recognizer engine configured (dragonfly supports multiple setups)
    - xdotool available (dragonfly’s X11 backend relies on it)

### 166.2 Creative feature: “voice-confirmed dangerous actions”
For steps like “Kill process” or “Clear stuck keys”:
- require a voice confirmation phrase (optional safety)
This is niche but very effective.

---

## 167) Recording smoothness and “redundant move thinning”: learn from Macro-Tool’s TODO

A small X11 macro tool explicitly calls out that recording should be smoother and “save only needed actions,” implying it currently records too many events (especially mouse moves).  
Ref: Macro-Tool README TODO: https://github.com/YatoVoid/Macro-Tool

### 167.1 Low-hanging recorder improvements (high ROI)
- Mouse move thinning:
  - record only when distance > N pixels or time > T ms
  - coalesce into “MoveTo(x,y)” at the end of a continuous gesture
- “Semantic collapse” pass:
  - compress repeated small delays into one delay
  - merge multiple “key press” into text where appropriate
- Provide a per-recording “smoothing preset”:
  - precise (more events)
  - normal
  - compact (fewer events; best for portability)

---

## 168) Permissions reality: some libraries need elevated access for global capture

Macro-Tool notes that PyAutoGUI/pynput may require root access for capturing input globally on Linux depending on environment.  
Ref: Macro-Tool README notes: https://github.com/YatoVoid/Macro-Tool

### 168.1 Low-hanging Studio “Doctor” messaging
- If global capture fails:
  - explain the likely reason (permissions/backend)
  - suggest:
    - switch to X11 capture backend (XInput2 / RECORD)
    - enable uinput backend later (with proper udev rules)
    - run sandbox mode for testing
- Avoid telling users to “run as root” as a default; prefer least-privilege solutions.

---

## 169) Backlog updates from this revision

### P0
- Needle match method selector (pixel/feature/auto) + candidate viewer
- Vision Doctor “common mistakes” wizard + delayed capture
- Test/overlay for every targeting dialog
- Recorder smoothing presets + mouse move thinning
- Dragonfly adapter:
  - `vhkctl run` stable CLI
  - grammar generator

### P1
- “capture metadata” stored with needles:
  - focus state
  - cursor hidden?
  - expected scale/DPI
- Feature matching backend implementation (ORB/AKAZE first; SIFT optional due to licensing/availability)

---

## 170) Research links added in this revision
- Macro Recorder image detection methods: https://www.macrorecorder.com/doc/reference/image-detection-method/
- Macro Recorder find UI (scope, overlay, test): https://www.macrorecorder.com/doc/find/
- Macro Scheduler image recognition mistakes: https://www.mjtnet.com/blog/2009/02/13/image-recognition-common-mistakes/
- Dragonfly X11 actions using xdotool, Unicode support: https://dragonfly2.readthedocs.io/en/stable/actions.html
- Macro-Tool (record smoothing TODO, permission note): https://github.com/YatoVoid/Macro-Tool

---

## 171) AT‑SPI “Doctor” and reliability: treat the accessibility bus like a real dependency

Our tool relies on AT‑SPI for structured UI automation when it’s available. In practice, AT‑SPI fails in a few predictable ways — and we can make that almost painless by baking the *actual bus architecture* into the Doctor and Inspector.

### 171.1 The accessibility bus is *not* the normal session bus
GNOME’s own at-spi2-core docs explain that accessibility runs on a **separate bus** (a separate `dbus-daemon` or equivalent like `dbus-broker`) because accessibility traffic is “very chatty.” The bus is launched and managed by `at-spi-bus-launcher`.  
Ref: https://raw.githubusercontent.com/GNOME/at-spi2-core/main/bus/README.md

Key details to use in our implementation:
- `at-spi-bus-launcher` owns **`org.a11y.Bus` on the *session bus*** and exports `/org/a11y/bus`. It provides:
  - `org.a11y.Bus.GetAddress` → returns the address of the **accessibility bus**.
  - `org.a11y.Status` → properties to query whether the accessibility bus is enabled and whether a screen reader is running.  
  Ref: https://raw.githubusercontent.com/GNOME/at-spi2-core/main/bus/README.md
- The registry daemon (`registryd`) claims **`org.a11y.atspi.Registry`** on the accessibility bus.  
  Ref: https://raw.githubusercontent.com/GNOME/at-spi2-core/main/bus/README.md

### 171.2 Doctor “Bus Check” should literally run the canonical probes
A very clear recipe is documented in a recent answer:
- call `GetAddress` on `org.a11y.Bus`
- connect to that returned bus address and list services / inspect the registry tree  
Ref: https://stackoverflow.com/questions/79842267/how-do-i-access-the-atspi-dbus-service

**Low-hanging Doctor actions:**
- Button: “Check accessibility bus”
  - run (or show) `busctl --user call org.a11y.Bus /org/a11y/bus org.a11y.Bus GetAddress`
  - then list services on that address and confirm `org.a11y.atspi.Registry` exists
- Button: “Open event monitor”
  - launches our AT‑SPI event monitor (Accerciser-style section) and verifies focus/state events flow.

### 171.3 Why the bus starts (and why it might not)
at-spi2-core documents two main launch paths:
- on-demand via `GetAddress`
- session startup if **`org.gnome.desktop.interface toolkit-accessibility`** is true (via XDG autostart), and a screen reader key may also drive it  
Ref: https://raw.githubusercontent.com/GNOME/at-spi2-core/main/bus/README.md

**Low-hanging Studio feature:** a “Start accessibility bus now” action:
- call `GetAddress` proactively (and optionally “launch-immediately” in controlled environments)

---

## 172) Making apps visible to AT‑SPI: XSETTINGS / GTK_MODULES / gsettings (the real knobs)

AT‑SPI visibility depends on the toolkit bridge being loaded.

GNOME’s (archived) mechanics doc explains:
- GTK can load accessibility modules via:
  - `GTK_MODULES=gail:atk-bridge` (older method)
  - XSETTINGS property “Gtk/Modules” (newer method; set by settings daemon)  
Ref: https://wiki.gnome.org/Accessibility%282f%29Documentation%282f%29GNOME2%282f%29Mechanics.html

A Red Hat bug report captures the practical failure mode: GTK apps don’t show up in AT‑SPI unless the modules/setting is enabled; it also notes that a proper fix is setting `org.gnome.desktop.interface.toolkit-accessibility`.  
Ref: https://bugzilla.redhat.com/show_bug.cgi?id=787195

**Low-hanging Studio features:**
- “Launch app with accessibility enabled” wrapper:
  - option A: set `GTK_MODULES=gail:atk-bridge` for that process
  - option B: ensure `gsettings set org.gnome.desktop.interface toolkit-accessibility true` (best effort)
- Inspector hint:
  - if an app has no AT‑SPI tree, show:
    - “This app may not be loading atk-bridge”
    - buttons: “Launch with a11y enabled” and “Show how to enable toolkit-accessibility”

---

## 173) When users disable accessibility for performance (NO_AT_BRIDGE): don’t break their setup

It’s common for people to disable at-spi/atk-bridge for performance/noise reasons.
GNOME docs state `NO_AT_BRIDGE` delays ATK bridge initialization (atk_bridge_init is not called when the module is loaded).  
Ref: https://wiki.gnome.org/Accessibility%282f%29Documentation%282f%29GNOME2%282f%29Mechanics.html

Arch forum threads show `NO_AT_BRIDGE=1` is a common “disable at-spi-bus-launcher” trick, and mention GNOME Shell historically unsetting it at startup in some setups.  
Ref: https://bbs.archlinux.org/viewtopic.php?id=237697

A GNOME Mutter MR describes that GNOME Shell sets `NO_AT_BRIDGE=1` during startup and then unsets it (hacky but real).  
Ref: https://gitlab.gnome.org/GNOME/mutter/-/merge_requests/1744

**Low-hanging Studio policy:**
- Our agent should not require users to set global env vars.
- If we detect `NO_AT_BRIDGE=1`, offer:
  - “Run Studio agent with accessibility enabled (override env for agent only)”
  - “Keep system-wide accessibility disabled” (we just use vision fallbacks)
- Make this an explicit toggle in the Doctor: “Prefer accessibility when available.”

---

## 174) Common AT‑SPI failure messages and what we should say (Doctor copy that saves hours)

### 174.1 “Error retrieving accessibility bus address … org.a11y.Bus not provided”
Arch forum users note this error occurs if the DBus service file is removed/moved:
`Error retrieving accessibility bus address: org.freedesktop.DBus.Error.ServiceUnknown: The name org.a11y.Bus was not provided by any .service files`  
Ref: https://bbs.archlinux.org/viewtopic.php?id=237697

**Doctor response:**
- explain that `org.a11y.Bus` is DBus-activated and needs its service file present
- suggest reinstalling at-spi2-core / restoring DBus service files
- offer “use vision fallback” until fixed

### 174.2 “GTK apps not visible in sniff/orca”
The Red Hat bug report describes exactly this scenario when GTK modules aren’t enabled.  
Ref: https://bugzilla.redhat.com/show_bug.cgi?id=787195

**Doctor response:**
- show the 2–3 likely fixes:
  - set `toolkit-accessibility` gsettings key
  - launch app with `GTK_MODULES=gail:atk-bridge`
  - confirm that the accessibility bus is reachable (`GetAddress`)

---

## 175) Backlog updates from this revision (AT‑SPI robustness)

### P0
- AT‑SPI Doctor page:
  - GetAddress probe + Registry presence check
  - event stream verification
  - actionable fixes for common errors
- “Launch app with accessibility enabled” wrapper (per-process)
- Inspector “a11y missing” hints + quick actions
- System-friendly policy for NO_AT_BRIDGE (agent-only override; no global changes required)

### P1
- A11y performance mode:
  - cache accessible trees
  - rate-limit event subscriptions
  - fall back to “query on demand” when event stream is noisy

---

## 176) Research links added in this revision
- at-spi2-core bus launcher design and GetAddress semantics: https://raw.githubusercontent.com/GNOME/at-spi2-core/main/bus/README.md  
- busctl GetAddress recipe for atspi registry: https://stackoverflow.com/questions/79842267/how-do-i-access-the-atspi-dbus-service  
- GNOME accessibility mechanics (GTK_MODULES, XSETTINGS, NO_AT_BRIDGE): https://wiki.gnome.org/Accessibility%282f%29Documentation%282f%29GNOME2%282f%29Mechanics.html  
- GTK apps invisible unless modules/setting enabled: https://bugzilla.redhat.com/show_bug.cgi?id=787195  
- NO_AT_BRIDGE as a common disable trick + org.a11y.Bus service error example: https://bbs.archlinux.org/viewtopic.php?id=237697  
- GNOME Shell NO_AT_BRIDGE hack mention (Mutter MR): https://gitlab.gnome.org/GNOME/mutter/-/merge_requests/1744

---

## 177) Window focus/raise and the EWMH “active window” reality (make the runner honest)

A big class of macro failures is “I tried to activate window X, but focus didn’t change.”
X11 has multiple layers:
- the client request to focus
- the WM policy (may deny focus stealing)
- EWMH hints for “active window”
We should bake this into:
- step semantics (best-effort)
- retries/timeouts
- diagnostics

### 177.1 `_NET_ACTIVE_WINDOW` and window activation semantics
EWMH defines how clients can request focus/activation via `_NET_ACTIVE_WINDOW`. Many tools (wmctrl/xdotool) rely on these hints.

**Low-hanging Studio features:**
- Step: `Window.Activate(selector, method=i3|ewmh|raise_only, timeout)`
- After activation attempt:
  - wait until active window matches target (timeout)
  - if it fails: capture reason hints in log:
    - target exists?
    - target mapped?
    - i3 focused container changed?
- Provide a “focus stealing” warning:
  - “Your WM may deny activation when another app is actively used.”

### 177.2 Use i3 IPC whenever possible (more deterministic)
In i3 sessions, prefer:
- `i3-msg [criteria] focus` (or focus by con_id)  
Ref: i3 IPC and criteria usage: https://i3wm.org/docs/userguide.html

Then use EWMH fallbacks for non-i3 or special windows.

---

## 178) i3 floating, marks, scratchpad: turn “WM tricks” into first-class steps

AHK users routinely build “window choreography.” i3 has very strong primitives that we should expose directly.

### 178.1 Marks as “variables for windows”
i3 marks allow naming containers and focusing them later; i3-input is commonly used to set mark names interactively.  
Refs:
- i3 docs (marks): https://i3wm.org/docs/userguide.html
- i3-input: https://man.archlinux.org/man/extra/i3-wm/i3-input.1.en

**Low-hanging steps:**
- `I3.Mark(name)` / `I3.Unmark(name?)`
- `I3.FocusMark(name)`
- `I3.ListMarks() -> list`
- `I3.MarkPrompt()` (uses i3-input)

### 178.2 Scratchpad workflows
Scratchpad is a “hidden workspace” for toggled windows; it’s perfect for automation control panels and floating toolboxes.

**Low-hanging steps:**
- `I3.MoveToScratchpad()`
- `I3.ScratchpadShow()`
- Template:
  - “Put VHK Console into scratchpad and toggle with hotkey”

---

## 179) “Mouse to keyboard” and keyboard to mouse: xdotool mousemove_relative + i3 focus follows mouse

There are a few i3+X11 interactions worth documenting:
- some users have focus follows mouse enabled; moving the mouse can change focus unexpectedly
- `mousemove_relative` is useful for games or relative movement (no coords)  
Ref: xdotool man page (mousemove_relative): https://manpages.ubuntu.com/manpages/trusty/man1/xdotool.1.html

**Low-hanging Studio features:**
- Runner option: “Freeze focus during macro”
  - if focus changes unexpectedly during a macro, pause and show diagnostics
- Steps:
  - `Mouse.MoveRelative(dx, dy)`
  - `Mouse.Nudge(direction, pixels)` (templated)
- Doctor:
  - detect focus-follows-mouse (best effort: parse i3 config or subscribe to focus events while moving mouse)
  - warn users if macros rely on focus stability

---

## 180) Macro composition: “submacros” and reuse (make profiles first-class)

We already planned templates and libraries. This revision adds a concrete, low-hanging way to make reuse real:

### 180.1 Submacro calls with argument mapping
- Step type: `CallMacro(macro_id, args, returns?)`
- Allow macro outputs:
  - return values (dict)
  - side effects (window mark set, files saved)
- Visual editor:
  - “Extract selection into macro”
  - “Inline macro steps” (reverse operation)

This is one of the biggest productivity multipliers and is mostly workflow-editor work.

### 180.2 App Profiles + Workspace Projects + Adapters unify nicely
- App Profile = selectors + reusable actions
- Workspace Project = layout + programs + macros to run
- Adapter = native IPC hooks
All three can share the same underlying “library & packaging” system.

---

## 181) “Time travel” logging: timeline with causal links (cheap but very helpful)

We already have support bundles. Upgrade the log format to include:
- timeline events:
  - “focused window changed”
  - “needle matched”
  - “wait started/ended”
  - “OCR result”
  - “a11y event”
- causal links:
  - “step 12 waited for needle X; after 1.2s matched at (x,y); click point used: ok_button”
This makes debugging complex macros dramatically easier, and it’s mostly logging schema + UI.

---

## 182) Backlog updates from this revision

### P0
- Window.Activate step with explicit method + honest timeouts + logs
- i3 marks + scratchpad step palette + templates
- “Extract selection into macro” / “CallMacro” step type
- Better run timeline logs with causal links

### P1
- Focus freeze mode (warn if focus changes unexpectedly)
- Focus-follows-mouse Doctor heuristics

---

## 183) Research links added in this revision
- i3 marks/scratchpad/criteria: https://i3wm.org/docs/userguide.html  
- i3-input: https://man.archlinux.org/man/extra/i3-wm/i3-input.1.en  
- xdotool mousemove_relative: https://manpages.ubuntu.com/manpages/trusty/man1/xdotool.1.html  

