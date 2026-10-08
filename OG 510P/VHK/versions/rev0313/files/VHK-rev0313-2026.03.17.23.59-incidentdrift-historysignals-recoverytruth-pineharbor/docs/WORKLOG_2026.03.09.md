- portal shortcut export now translates several common punctuation keys (`[`, `]`, `;`, etc.) into shortcuts-spec/xkbcommon identifiers, which closes a real Wayland/portal ergonomics gap for bindings that were previously skipped even though the freedesktop shortcuts spec can represent them
- `vhk lint-project` now also surfaces GlobalShortcuts export honesty before pack generation: it warns when a binding key chord cannot be expressed as a portal `preferred_trigger`, and it marks binding `when:` selectors as runtime-only because the portal activation itself is global by design
- extended `vhk lint-project` with voice-phrase quality guidance: explicit `voice_phrases` that normalize to nothing now warn, punctuation/case variants that export as a different literal phrase now show up as review notes, redundant variants that collapse together are flagged, and short one-word global voice commands now get a conservative nudge toward multi-word phrasing or `voice_when` scope
- added targeted tests covering the new voice-quality lint cases without regressing existing Dragonfly/Talon collision and context-export checks
- hardened `vhk gen-autokey-pack` around a newly verified AutoKey limitation: AutoKey window filters apply one regex to window title OR class, so VHK now skips scoped AutoKey exports by default, only allows simple `class`-only / `title`-only scope behind `--allow-window-filter-approximation`, and validates raw `title_regex` patterns before writing sidecar metadata
- added `vhk gen-autokey-pack`, a reviewable AutoKey/X11 adapter export that turns VHK hotstrings and bindings into script + sidecar metadata pairs under a generated `data/` tree, plus a local README and `pack.json` handoff
- kept that AutoKey lane honest: VHK remains the execution engine, return-mode hotstrings call `vhk run --print-return`, and selectors/hotkeys that AutoKey cannot express without broadening scope are skipped with explicit reasons
- added targeted tests covering AutoKey pack generation, CLI JSON manifests, script send-mode wiring, sidecar metadata, and skip reasons for unsupported window filters / AltGr-style hotkeys
- made voice-export phrase handling context-scoped instead of global: Dragonfly/Talon packs now use stable internal command ids, the same literal phrase can safely exist in multiple distinct `voice_when` contexts, and `vhk lint-project` now warns when phrases still collide inside the same effective backend scope
- added `voice_when` metadata for macros/presets plus context-aware Dragonfly/Talon pack generation, so reviewable voice exports can now stay app/title-scoped when that mapping is honest instead of being globally active by accident
- kept that lane conservative: unsupported selector fields (for example `workspace`, `focused`, `app_id`, regex-only matches) now cause the generated voice entry to be skipped rather than silently broadening command scope
- added targeted tests covering contextual Dragonfly grammars, split Talon `.talon` files, JSON manifest context payloads, and skip reasons for unsupported voice-context selectors
- added `vhk gen-talon-pack`, a second reviewable voice-adapter export that writes a Talon `.talon` command file, Python action module, JSON command ledger, and local README so spoken phrases can launch `vhk run ...` without re-encoding macro semantics in Talon
- kept that Talon lane adapter-shaped and conservative: it reuses macro/preset `voice_phrases`, skips prompt-overlay presets by default, and generates literal spoken commands that call back into one Python action instead of inventing custom grammar logic in YAML
- added targeted tests covering Talon pack generation, CLI JSON manifests, generated `.talon` command wiring, and Python action-module command dispatch stubs
- added `vhk gen-dragonfly-pack`, a reviewable voice-adapter export that writes a Dragonfly command module, JSON command ledger, and local README so spoken phrases can launch `vhk run ...` without re-encoding macro semantics in a second runtime
- added macro/preset `voice_phrases` metadata plus conservative export rules: prompt-overlay presets are skipped by default, spoken forms are normalized into literal phrases, and duplicate phrases are deduped deterministically
- added targeted tests covering Dragonfly pack generation, explicit voice phrases, prompt-overlay skipping, JSON manifest output, and generated module command wiring
- added a new optimizer lane for structured form text: `vhk optimize --segment-paste-text` (plus matching `optimize-project` / `record-x11` flags) can now split one literal `TypeText` with embedded `Tab` / `Enter` boundaries into a hybrid sequence of explicit `Key(tab|enter)` steps plus clipboard-paste `TypeText` chunks for large field bodies
- added an explicit optimizer/recorder bridge for the typing-vs-pasting distinction: `vhk optimize --promote-paste-text` (plus matching `record-x11 --optimize-promote-paste-text`) can now rewrite long literal single-line `TypeText` steps into `backend=clipboard` when authors want throughput instead of per-character typing semantics
- kept that paste-promotion lane conservative on purpose: `${...}` text, `delay_ms_per_char`, and Tab/Enter-rich snippets stay in the typed lane so recorder cleanup does not erase form-navigation semantics or clipboard-sensitive author intent
- added targeted optimizer tests proving paste promotion works for long literal text and compressed key runs, while refusing to rewrite dynamic text and Return/Tab-rich snippets
- pushed the text-run optimizer one more step toward human editing semantics by teaching it whole-word cleanup (`Ctrl+Backspace` / `Ctrl+Delete`) plus boundary-selection replacement (`Shift+Home` / `Shift+End`), so recordings that fix larger local mistakes can now still collapse into one final `TypeText(...)` step when the caret/selection proof stays honest
- extended `WaitForClipboardChange` and `WaitForClipboardEvent` with optional `pattern` / `flags` / `condition` filtering plus regex match outputs, so clipboard-driven parsing loops can stay declarative instead of wrapping waits inside extra `While` glue
- taught clipboard waits to retry across non-matching clipboard events until the timeout budget is exhausted, preserving helper-backed event semantics while letting macros wait for a specific clipboard payload shape
- added `clipboard_watcher.event_mode` (`change` vs `event`), so project-level watchers can now react to repeated same-text copy owner-events when helper-backed backends exist
- watcher-triggered macros now receive `clipboard_changed`, `clipboard_event`, and `clipboard_event_mode`, and watcher JSONL logs record `event_mode` plus whether the clipboard text actually changed
- added targeted tests covering filtered clipboard waits, condition-based retrying, watcher `event_mode` loading, and same-text event-mode watcher execution
- updated clipboard/project-format docs so the new clipboard event/filter contract is explicit instead of living only in code/tests
- taught the optimizer to treat shifted printable chords as text (`shift+h` -> `H`, `shift+1` -> `!`) and to collapse zero-gap key runs after chord compression, so `vhk optimize --compress-text` and `vhk record-x11 --optimize --optimize-compress-text` can now turn recordings like `Hello!` into one `TypeText` step
- added targeted optimizer tests covering shifted text compaction and making sure real shortcuts like `ctrl+shift+p` still stay semantic `Key` chords instead of being mistaken for text
- taught the optimizer to reconstruct simple edited text runs too, so sequences like `hex` + `Backspace` + `llo` now collapse into one `TypeText(text="hello")` step, and Enter/Tab-rich literal text runs can stay in the same text-first lane
- added targeted optimizer tests covering backspace-aware text reconstruction and Enter/Tab collapsing so this more human recorder-cleanup loop stays explicit and safe
- extended that edited-text lane to handle short cursor-local corrections too (`Left`/`Right`/`Home`/`End`/`Delete`), so recordings like `helo` + `Left` + `Left` + `l` + `Right` + `Right` can now collapse to `TypeText(text="hello")` when the final caret returns to the logical end of the text
- added targeted optimizer tests proving those cursor-local corrections collapse when safe and remain as explicit key steps when the final caret position would still matter
- extended the edited-text optimizer lane one more step so short shift-selection replacement patterns (for example `hellp` + `Shift+Left` + `o`) can now collapse into one `TypeText` step, while runs that still end with a live selection remain explicit key steps
- added focused tests proving the new selection-replacement path collapses when safe and refuses to collapse when selection state still matters at the end of the run

- hardened `vhk gen-espanso --package-dir` around Espanso's current one-active-app-config rule: config files now sort by specificity, the exporter can synthesize composite scoped configs for simple overlapping class/title filter sets, and package dirs now include a local `README.md` plus `pack.json` so the precedence/include graph is reviewable
- added targeted tests covering synthetic Espanso composite configs, inherited includes for more-specific scopes, and the new package-dir manifest/readme outputs

## export-honesty lint for adapter lanes

Added new project-level lint warnings so export loss shows up during design review instead of only inside generated packs:

- `VOICE_CONTEXT_EXPORT_GAP` for Dragonfly/Talon `voice_when` selectors that cannot be exported honestly
- `VOICE_PROMPT_EXPORT_OPT_IN` for preset voice entries that are skipped by default because they open prompt overlays
- `AUTOKEY_SCOPE_APPROXIMATION_REQUIRED` / `AUTOKEY_SCOPE_EXPORT_GAP` for AutoKey window filters that would widen or drop meaning
- `ESPANSO_APP_SCOPE_WAYLAND`, `ESPANSO_SCOPE_EXPORT_GAP`, and `ESPANSO_SCOPE_COMPOSITE_CONFIG` for scoped-hotstring plans that clash with Espanso's Wayland/app-config constraints

Targeted validation covered the new lint cases plus the adjacent Espanso/AutoKey/Dragonfly/Talon export suites.


## xremap regex-aware scoping + pre-export lint

- taught `vhk gen-xremap-config` to preserve `title_regex` and `app_id_regex` as native xremap `/regex/` filters while keeping exact `title` values anchored as regex window filters
- added project-level `XREMAP_SCOPE_EXPORT_GAP` lint output so bindings that still depend on `workspace`, `pid`, or state flags show up as runtime-only xremap gaps before export
- added targeted tests covering regex-aware xremap filter generation and the new xremap export-honesty lint case


## trigger-lane export honesty for keyd / Kanata / KMonad / sxhkd

- added `KEYD_SCOPE_RUNTIME_ONLY`, `KANATA_SCOPE_RUNTIME_ONLY`, `KMONAD_SCOPE_RUNTIME_ONLY`, and `SXHKD_SCOPE_RUNTIME_ONLY` project-lint warnings so daemon/remapper exports stop looking more app-aware than they really are
- added `SXHKD_X11_ONLY` when a Wayland-marked project still points at the sxhkd lane
- added `KMONAD_TRIGGER_SHAPE_CHANGE` plus `KMONAD_COLLISION_SELECTOR_LAYER` so the leader/layer and selector-sublayer behavior is visible before export
- refreshed docs/README/research notes to reflect current remapper lessons from keyd, keyd-fork, Kanata, KMonad, and sxhkd
- targeted validation covered lint-project plus keyd/Kanata/KMonad/sxhkd generator suites, followed by a broader lint/schema/xremap/trigger-pack sweep
