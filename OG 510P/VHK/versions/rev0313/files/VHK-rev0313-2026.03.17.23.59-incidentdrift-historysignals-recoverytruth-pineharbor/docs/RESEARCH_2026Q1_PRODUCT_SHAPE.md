# Research notes (2026 Q1): shaping VHK into a Linux-native AHK + macro studio

This is a short product memo derived from current public docs/pages for:

- Pulover's Macro Creator
- AutoKey
- Espanso
- keyd / xremap-class remappers
- XDG portals + libei/EIS

The goal is not to clone any one tool. The goal is to understand which parts of
those tools are genuinely great and then re-express them in a Linux-native way.

---

## 1) What Pulover's Macro Creator gets right

Pulover's Macro Creator still represents the clearest mainstream example of a
"record first, then clean up, then scale up" automation tool.

VHK should copy these ideas:

- **single visible step list**
  - recorded actions land in an editable table immediately
  - users do not need to mentally switch between "recorder mode" and
    "programmer mode"
- **command discoverability**
  - image search, pixel search, waits, loops, variables, window actions, etc.
    are all visible as standard building blocks
- **cleanup after recording is expected**
  - the recorder is not the final truth; it is a draft generator
- **inspectors matter as much as the recorder**
  - window spy / control info / coordinate tools are part of the product, not
    side utilities

VHK implication:

- the future Studio should treat recording as **draft generation** and place a
  first-class **normalize/optimize/lint** pass right after recording.
- the engine should keep a strong distinction between:
  - raw captured events
  - editable semantic steps
  - exported portable bundles

---

## 2) What AutoKey gets right

AutoKey proves that Linux users value a blend of:

- hotkeys
- abbreviations / text expansion
- small scripts
- app/window filtering

Its strong idea is that **text workflows and automation workflows are not
separate products**.

VHK should copy these ideas:

- phrases + scripts should live next to macros in one project model
- triggers should include both hotkeys and typed expansions
- app-scoped rules should be explicit, not hacked in later
- metadata next to content is often worth it when the toolchain wants to stay
  filesystem-friendly

VHK implication:

- keep project folders editable and diffable
- grow `hotstrings`, app filters, and per-app behavior into a first-class rule
  model instead of treating them as exports only

---

## 3) What Espanso gets right

Espanso is strongest where many macro tools are weakest:

- structured text workflows
- forms
- variable injection
- regex triggers
- app include/exclude rules
- shell/script extension points

VHK should copy these ideas:

- **forms** should become a native concept for macro parameters, not just a
  future GUI nicety
- trigger matching should support both literal and regex-like cases
- app-specific enable/disable rules are worth preserving in the project format
- text workflows should be composable with scripts and command outputs

VHK implication:

- add a project-level concept like "prompted variables" / "macro forms"
- unify text expansion and macro dispatch around the same variable model
- think of many "macros" as structured templates with actions attached

---

## 4) What keyd / xremap / input-remapper style tools teach us

The Linux input stack rewards **layering**.

There is a big difference between:

- remapping keys at the evdev/uinput layer
- injecting events for automation
- binding global shortcuts
- recording and replaying semantic macros

VHK should not try to absorb every remapping use-case into the Python engine.

VHK should copy these ideas instead:

- keep remappers/hotkey daemons as **integration surfaces**
- generate configs for the good external tools
- use the bus/runtime as the glue between those tools and the macro engine

VHK implication:

- exporting to `keyd`, `kanata`, `kmonad`, compositor configs, and portal-based
  hotkeys is not a compromise; it is the correct Linux-native architecture
- latency-sensitive always-on capture should stay close to the kernel/compositor
  boundary, not inside a heavy app runtime

---

## 5) What portals + libei/EIS teach us

Wayland support is not one feature. It is a **matrix** of independently varying
capabilities.

Important splits:

- screenshot vs screencast
- input emulation vs input capture
- global hotkeys vs compositor-native binds
- window metadata vs cursor position vs screen geometry

VHK implication:

- always ask **which capability** is present, not whether "Wayland is supported"
- diagnostics, validation, and Studio UX should all speak capability language
- permissioned portal flows are often interactive and session-scoped; they are
  different from always-on automation helpers
- libei is promising, but it should probably arrive behind a helper binary or
  isolated backend module first

---

## 6) Concrete product directions for the next revisions

### A) Capability-aware validation + lint

A first piece of that is now implemented: `vhk validate` can warn when the
current session appears to be missing or limiting capabilities a project uses.
`vhk lint-project` now reuses the same model, so project review can show both
macro-hygiene issues and session-fit warnings in a single pass.

Next step: teach scaffold/help/init flows to use the same model more
pervasively and more contextually.

Examples of the warnings we want:

- project depends on global hotkeys but current session has no good hotkey path
- project depends on pointer injection but only text injection is available
- project depends on visual capture but current session only has partial portal
  support

### B) Recorder → cleanup pipeline

Make recorder output explicitly flow through:

1. capture
2. normalize
3. collapse/noise-reduce
4. selector upgrade
5. portability hints

### C) Prompted variables / forms

A first engine slice now exists: `PromptForm` writes a structured dict into the
macro context, prefers YAD's native multi-field form dialog when available, and
falls back to portable sequential prompts elsewhere.

`ChooseFromList` has now taken the same direction for single-pick flows: on X11
it prefers `rofi`/`dmenu`, and on Wayland it prefers `fuzzel`/`tofi`/`wofi`,
before dropping to dialog helpers. That is a small but important product move:
Linux users already expect searchable launcher-style choosers, not just modal
form dialogs.

Next layers to add:

- scaffold/templates that generate parameterized macros
- richer field types and validation
- Studio forms
- dispatcher UIs / palette launches

### D) App-scoped activation rules

Generalize existing window filters into a clearer project concept for:

- enable only in some apps/windows
- disable in terminals/VMs/remote sessions/etc.
- choose a safer backend per app class when needed

### E) Better recorder semantics

Prioritize semantic events over raw events whenever possible:

- drag intent
- text intent
- window wait intent
- selector intent

### F) Separate low-latency dispatch from authoring/runtime

Long term, VHK likely wants:

- a thin always-on trigger plane
- a deterministic execution plane
- a Studio/inspection plane

That separation would mirror how Linux tooling already wins in practice.

---

## 7) The core thesis

The most Linux-native version of VHK is probably **not**:

- one monolithic daemon that tries to own remapping, hotkeys, recording,
  injection, window metadata, and text expansion by itself

It is more likely:

- a great macro engine
- a great project format
- a great diagnostics surface
- a great Studio for authoring/debugging
- and a great set of adapters/exports into the strongest Linux-native tools

That would make VHK feel closer to what AHK achieved on Windows, while still
respecting the architecture Linux desktops actually have.

## 8) Fresh product lessons from the current ecosystem

A few newer details are worth carrying forward more explicitly into VHK:

- **AHK context matters as much as triggers.** AutoHotkey's `#HotIf` / context-
  sensitive hotkeys and hotstrings reinforce that activation rules are part of
  the authoring model, not an afterthought.
- **Espanso proves forms are a real product surface.** Structured prompts, regex
  triggers, shell/script expansion, and app include/exclude logic should push
  VHK toward first-class macro parameters rather than ad-hoc prompt steps.
- **xremap + keyd show that app-scoped behavior belongs near the trigger plane.**
  VHK should integrate with those layers and export to them, not try to bury
  their advantages inside a slower monolithic runtime.
- **Portal capability drift is normal.** Because different interfaces can be
  routed to different backends, the authoring UX should keep saying which
  capability is present and how strong it is, rather than caching one coarse
  desktop label.

That combination points toward a future Studio flow that looks like:

1. record or author a macro
2. lint it for hygiene
3. check it against current session capabilities
4. surface app-scoped activation and form parameters explicitly
5. export/integrate with the strongest Linux-native trigger layer available


A natural follow-on from launcher-native choosers is now implemented too: `vhk palette` turns the chooser stack into a project-level macro launcher. That matters because Linux launcher tools already normalize a searchable stdin/stdout picker workflow; the product lesson is to treat launchers as part of the runtime surface, not just as a convenient shell trick.

The next obvious step is saved parameter sets, and that is now a runtime concept too: one macro can define named presets such as `staging` and `prod`, which the palette exposes as separate launcher actions without cloning the step graph. That shape lines up well with Espanso-style forms/variables and with the way Linux users already build project launchers and workspace restore flows around named profiles.


That next step is now partially implemented too: presets can attach a small `prompt_form`, so a palette action like `deploy@prod` can preload stable vars and then ask for just the fields that should vary per run. This is much closer to how Linux users already combine launchers, dialogs, and small script parameters than a Windows-style monolithic recorder UI.

A further Linux-native refinement now exists too: remembered prompt answers and
named prompt profiles. This is a better fit for launcher/dialog workflows than
forcing authors to duplicate macros for every slightly different parameter set.
The product lesson is the same one visible in launcher ecosystems and tools like
i3-resurrect: named, reusable actions matter, but so do lightweight profiles and
last-used values that make repeated flows fast without turning the macro graph
into a pile of near-duplicates. The next refinement from that lesson is now in
place too: prompted presets can surface saved profile actions directly in the
palette, which is a closer match for how Linux launcher flows usually expose
named tasks than hiding everything behind secondary flags.


A further Linux-native lesson from current launcher ecosystems is that VHK should not stop at `dmenu`-style pickers. `.desktop` launchers remain the common integration format for menus, taskbars, and `drun`-style launchers, and the freedesktop spec explicitly supports additional application actions. That makes desktop-entry export a natural extension of the palette/preset/profile model: the same project actions that show up in `vhk palette` can also become launcher quick-actions without inventing a custom background daemon just to feel integrated.


## Launcher scripts as a first-class runtime surface

A lot of Linux automation tooling still assumes a script-first picker culture: pipe lines into a chooser, get one line back, then act on it. VHK should keep embracing that model. The project palette already gives VHK a stable `entry_id` layer; exporting a launcher script lets that same layer plug into rofi/wofi/fuzzel/tofi style workflows without inventing a separate GUI protocol.

A further lesson from the current launcher ecosystem is that not all picker integrations are equally expressive. Rofi script mode supports row-level metadata such as `info`, `meta`, `icon`, `active`, and `urgent`, and fuzzel explicitly supports Rofi's extended dmenu icon protocol in dmenu mode. That argues for a palette model that carries explicit icon/search metadata instead of flattening everything down to one human label too early.

Another Linux-native lesson is that launcher integration is not finished once the project can print a command. i3 and sway both expect `bindsym ... exec ...` style config snippets, while Hyprland uses `bind = ..., exec, ...` and increasingly documents `uwsm app -- ...` as a preferred application-launch path in some setups. That argues for a dedicated WM binding export layer on top of `.desktop`, launcher-script, and rofi-mode exports, rather than leaving users to translate command lines into compositor syntax by hand.

That same research also argues against pretending rofi discovers custom scripts from a magic directory alone: the actual integration surface is an explicit custom mode spec of the form `name:script`, so VHK should export a concrete command/manifest rather than vague placement advice.

A related lesson from current WM docs is that launcher integration on Linux is often two-tiered: one global binding opens a transient mode or submap, and that mode fans out into a small set of high-value actions. i3's default resize mode and Hyprland's submap docs both reinforce that pattern, while sway inherits the same block-oriented config style. That makes a palette-derived launcher mode/submap a good fit for VHK: the full palette remains available, but the most relevant recent macros/presets/profile actions can also live behind a leader-key layer without hard-coding permanent top-level binds for everything.

A follow-on lesson from the current WM docs is that “ready-to-paste snippet” is only half of the Linux story. i3 and sway both document `include`-style config composition, and Hyprland documents linear `source = ...` parsing with globbing. That means VHK should treat snippet placement as part of the product surface, not as an afterthought: users often want one generated file in a managed subtree and one stable line in the parent config, not an instruction to manually paste large blobs forever.

---

## 7) What the launcher / WM docs teach us

Linux launcher workflows are usually **composed**, not monolithic.

A real user workflow often spans:

- a picker helper (`rofi`, `wofi`, `fuzzel`, `tofi`, etc.)
- a WM bind or submode
- an include/source tree in the main WM config
- sometimes a desktop entry too

VHK implication:

- low-level exporters are still valuable
- but the product also needs **installer-grade composition helpers** that emit
  the helper, snippet, and bootstrap instructions together
- that is why the project now has `export-wm-bundle`, not only separate
  launcher/script/snippet exporters


## 9) New tool surface to support this thinking

A concrete engine/CLI slice now exists for the product-shape work: `vhk plan-project`.

That command is intentionally different from validate/lint/doctor:

- `doctor` asks what the current desktop can do
- `validate` asks whether the project parses and likely outruns the session
- `lint-project` asks whether the macro graph looks brittle
- `plan-project` asks what *kind* of Linux-native automation product this
  project is becoming and which trigger/integration strategy fits it

That gives VHK a place to encode the lessons above in a user-visible way instead
of leaving them only as architecture notes.


## 9) Turning research into a concrete planning surface

The next useful step after basic shape analysis is to emit **integration targets**
and a **prioritized roadmap**, not just prose recommendations.

That is now part of `vhk plan-project` as well. The command does not merely say
"this looks vision-heavy" or "this wants text expansion"; it now names likely
Linux-native landing zones such as:

- a thin trigger plane driven by WM/compositor binds
- a text tier with forms/presets/app scoping
- a selector asset pack for visual workflows
- event bridges/watchers for daemon-friendly projects
- a helper-backed adapter seam for Wayland injection
- remapper/export surfaces for keyd/kanata/kmonad/xremap-class tools

This matters because the future Studio should help authors decide **where a
workflow belongs** in the Linux stack, not merely whether the YAML parses.


## 7) Additional March 2026 lessons from current Linux automation surfaces

Recent public docs/issues reinforce a few product truths that are easy to miss
if we only think in terms of "macro features":

- **remappers win by being boring and close to input**
  - keyd/kanata/xremap-class tools are valued because they stay near evdev or
    compositor boundaries and keep latency low
- **Wayland app context is still uneven**
  - per-app logic often depends on compositor APIs, shell extensions, or helper
    bridges rather than a universal desktop API
- **portal support is per capability, not per desktop brand**
  - global shortcuts, input capture, and remote desktop each deserve their own
    deployment checklists
- **the Linux-native answer is usually layering, not purity**
  - exported configs, user services, helper boundaries, and project-local
    diagnostics are not temporary hacks; they are often the correct design

### Product consequence for VHK

`vhk plan-project` should keep moving toward three outputs:

1. **shape** — what kind of automation system this repo is becoming
2. **lanes** — which subsystem deserves first-class investment
3. **playbooks** — which commands or exports should be run next

That framing is more actionable than generic future-roadmap prose because it
lets teams compare alternatives (text tier vs remap surface vs selector pack)
without pretending Linux has one universal automation backend.


## New implementation consequence: architecture maps and stack profiles

The planning layer should not stop at recommendations. It should surface:

1. an **architecture map** describing which layer belongs in VHK core vs helpers/exports/services
2. a set of **stack profiles** describing the product shapes that current Linux tools already validate in practice

That is now part of `vhk plan-project`.
