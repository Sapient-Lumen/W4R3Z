# Rev0952 — trusted default keymap authority

Date: 2026-07-11

This revision is a trust-first product repair. It does not widen plugin
capabilities, add an operating-system sandbox, or make a physical keypress a
blanket privilege grant. It restores a basic distinction that the editor's
startup path had accidentally erased: **the shipped editor baseline belongs to
the host/user product, while plugin callbacks retain plugin authority**.

## Executive judgment

The heart of Micromax is not “a secure plugin manager” and not merely “a tiny
terminal editor.” It is a small, inspectable language and VM in service of a
calm, serious editor whose automation has explicit effects, visible provenance,
bounded host work, and recoverable failure.

That mission fails at the first tactile layer if safe defaults make ordinary
editing unusable. Ctrl-S, Ctrl-O, Ctrl-Z, copy, paste, buffer switching, and the
command palette are not plugin privileges. They are the host product's default
user interface. Plugins may add lower-authority behavior; trusted user config
may deliberately replace defaults. Neither should cause the baseline itself to
run as an arbitrary workspace plugin.

The practical priority order remains:

1. **Trust:** boring startup, predictable default keys, safe save/open/replace,
   honest errors, contained plugin authority, and product-journey tests.
2. **Taste:** restrained hierarchy, highlight/theme discipline, and defaults
   that feel designed rather than accumulated.
3. **Flow:** fast project movement, low-friction edit loops, and fewer sharp
   edges across search, selections, multicursor, macros, buffers, and prompts.

## The severe failure

Before rev0952, full startup obtained almost the entire default keymap by loading
`plugins/core/init.mx`. Plugin evaluation correctly runs inside script/plugin
context, so every binding created there captured the core plugin's root,
generation, group, and `script_context=True` authority.

`Editor._run_key_binding()` also correctly preserves that captured authority
when a physical key is pressed later. That delayed-authority rule is essential
for arbitrary plugins: a user pressing a plugin key must not silently turn the
plugin callback into trusted host code. Combined with safe capability defaults,
however, it meant the product's own common keys inherited plugin restrictions.

A fully bootstrapped runtime reproduced the following behavior with all relevant
script capabilities left at their safe `false` defaults:

| Physical action | Incorrect result before rev0952 |
| --- | --- |
| Ctrl-Z after a user edit | `undo: script context cannot replay undo history (trusted registration)` |
| Ctrl-S | `save: disabled for scripts (cap.fs-save)` |
| Ctrl-O followed by prompt submit | `open: disabled for scripts (cap.fs-open)` |
| Ctrl-C / Ctrl-X / Ctrl-V | internal or external clipboard policy treated the action as plugin-originated |
| Ctrl-B / Ctrl-Space | picker/palette prompts captured plugin authority and could hit script read/list restrictions |

This contradicted the capability contract, which already said interactive users
could open, save, copy, paste, and otherwise edit normally while script-origin
operations remained gated.

## Root cause

The execution rule was not wrong. The ownership assignment was wrong.

A keybinding is a delayed executable object. It can outlive registration and be
triggered by a later physical event. Micromax therefore stores provenance on the
binding and, for modal interactions, separately stores provenance on the mode
activation. The lower-authority side wins when either object came from a script.
That prevents ambient user gestures from laundering plugin code into trusted
execution.

The shipped baseline had been modeled as one more plugin registration instead of
host product policy. Tests mostly checked that key/action pairs existed, not that
their authority metadata matched the intended user journey. The repository had
excellent lifecycle coverage around stale callbacks and rollback while everyday
Ctrl-S was broken under its own safe defaults.

## Why `core` is not special-cased as trusted

The plugin root intentionally prefers a caller-supplied or working-directory
`plugins/` tree. Trusting a plugin merely because its manifest name is `core`
would let workspace-controlled content claim a magic name and receive host
authority. It would also mix package identity with policy in a way that is hard
to audit.

The repair instead makes startup order explicit and name-independent:

1. construct the editor;
2. install the product keymap directly as host-owned data;
3. install hostcalls;
4. load or scan plugins according to workspace trust;
5. load trusted user init after plugins, so user config can intentionally rebind.

Restricted startup still installs the usable editor baseline even when no plugin
source is evaluated.

## Landed design

### One declarative host table

`src/micromax_editor/default_keybindings.py` defines immutable
`DefaultKeyBinding` rows:

- `CORE_MIRRORED_KEY_BINDINGS` is the complete global, prompt, and query-replace
  baseline mirrored by the bundled Micromax file;
- `INTERNAL_ONLY_KEY_BINDINGS` contains host-only external-URL confirmation rows;
- `DEFAULT_KEY_BINDINGS` is the complete product map;
- `install_default_keybindings()` installs those rows with
  `script_context=False`;
- `install_embed_bootstrap_keybindings()` preserves the old tiny subset needed by
  a bare headless `Editor()` to finish internal prompt/confirmation loops.

The full product map is not forced into every embed. `create_editor_runtime()`
opts into it before plugin evaluation, while minimal hosts keep the historical
small bootstrap unless they call `Editor.install_default_keybindings()`.

### Readable Micromax mirror

`plugins/core/init.mx` remains ordinary Micromax source containing the exact
public key rows. This matters for inspectability, portability, examples, and
small hosts that want to see the configuration language express the same map.

When product startup has already installed an identical trusted row,
`Editor.bind_key_checked()` treats the lower-authority exact repeat as an
idempotent no-op. The plugin does not replace the row and does not acquire its
future physical-key authority. A parity regression parses the Micromax file and
compares its ordered rows against the Python table, so the two checked-in views
cannot drift silently.

### Authority remains narrow

- A normal physical key resolving to a host/user binding executes outside script
  context.
- A plugin-created binding still records plugin root, generation, group, and
  script origin; a later physical press executes it through
  `run_script_origin_callback()`.
- A script-created active keymode remains a delayed authority object. Even a
  trusted binding selected through that mode executes under the mode's script
  origin.
- Synthetic script keypresses do not borrow trusted target authority. The
  `cap.keybinding-press` override permits replay of a protected spec, but the spec
  still runs under the caller's script context.
- Trusted user init runs after plugins and may intentionally replace defaults.
- Runtime reload rebuilds the keymap and restores product defaults before plugin
  reload, while preserving the distinction between bare embeds and full product
  startup.

A physical gesture is therefore an event, not an authority escalation.

## Product journeys now pinned

Focused headless tests cover behavior rather than only registration shape:

- default rows are unique and exactly mirror `plugins/core/init.mx`;
- core plugin load leaves host-owned rows trusted and ungrouped;
- Ctrl-Z replays a user edit while `cap.undo-redo` remains false;
- Ctrl-O opens a trusted prompt and opens a file while `cap.fs-open` remains
  false;
- Ctrl-S writes the edited file while `cap.fs-save` remains false;
- Ctrl-A/Ctrl-X/Ctrl-V complete an interactive clipboard loop with clipboard
  script capabilities false;
- Ctrl-B opens a trusted buffer picker and switches buffers;
- Ctrl-Space opens a trusted command palette;
- an arbitrary third-party F12 binding to `command:open ...` remains
  plugin-owned and is denied by `cap.fs-open`;
- trusted user init can rebind Ctrl-S with source-span provenance;
- runtime reload restores the trusted baseline before plugin reload;
- restricted startup retains Ctrl-S without evaluating plugin source;
- a bare embed keeps its minimal bootstrap until it explicitly opts into the
  product map, and repeated installation does not clobber later trusted config.

## Adjacent recovery defect caught by the broader lane

The focused lifecycle slice exposed a separate first-slot rollback bug. Recovery
restore used `int(value or -1)` for the captured jumplist index. Because zero is
the first valid slot but falsey in Python, successful plugin reload and failed
reload rollback could restore one jump row while reporting the current index as
`-1`. The owner seam now converts the captured value directly and falls back only
on a real type/value error. Existing reload and rollback journeys pin both cases.

This is a useful example of why zero/empty/error cases need canonical tests: the
row data was present, authority was correct, and only the small visible index
contract lied.

## What was missing or wasteful

### Registration tests without tactile journeys

The old default-key test proved that the core plugin loaded and that selected
specs resolved. It did not inspect `script_context`, plugin provenance, prompt
authority, or the result of pressing the keys with safe capabilities. For editor
trust, “binding exists” is a weaker claim than “the user can complete open,
edit, undo, save, and navigate under the documented defaults.”

### Duplicate defaults without a drift contract

Internal prompt/query-replace rows existed in Python while overlapping rows also
lived in Micromax. The duplication was implicit. Rev0952 names the two views,
keeps a minimal embed subset, and adds exact parity coverage for the public
mirror.

### Lifecycle gravity outran product reality

The archive has hundreds of detailed revision notes and strong machinery for
plugin rollback, retained state, budgets, and local evidence. That work is real,
but the live handoff had begun recommending the next registry-owner slice by
default while common editing keys were capability-denied. The living vision,
LLM guide, README, and worklist now return the sequence to product journeys;
older text remains archived and the revision index stays authoritative.

### Missing project movement

The editor can group recent files by project and complete known paths, but it has
no first-class bounded project-file picker. A serious daily editor should let the
user jump to any project file without prior MRU luck or typing a known path. That
is now the highest-leverage flow gap after the authority repair.

## Online research implications

The external comparison is intentionally narrow and based on official project
documentation:

- micro documents familiar default keys such as open, save, undo, clipboard, and
  navigation, and presents sane defaults as part of the product promise:
  https://github.com/micro-editor/micro/blob/master/runtime/help/defaultkeys.md
  and https://github.com/micro-editor/micro
- Helix gives file and workspace pickers first-class keymap positions, reinforcing
  that project movement is a core editing loop rather than an optional plugin:
  https://docs.helix-editor.com/keymap.html
- VS Code separates Restricted Mode from extension trust and explicitly warns
  that Workspace Trust is not containment for malicious extensions. Micromax
  should preserve the same honesty while keeping normal editor use available:
  https://code.visualstudio.com/docs/editing/workspaces/workspace-trust and
  https://code.visualstudio.com/docs/configure/extensions/extension-runtime-security
- Zed declares extension capabilities and returns errors for denied operations,
  supporting explicit grants rather than ambient authority inherited from user
  gestures: https://zed.dev/docs/extensions/capabilities

The common lesson is not to copy any one editor. It is that safe extension
policy and usable defaults must coexist. Restriction should constrain extension
effects, not make the host product feel broken.

## Next cuts

1. Add a bounded, headless-first project-file inventory and picker with clear
   root, ignore, row, byte, and wall-clock behavior.
2. Add startup/open/edit/save-conflict/recovery/restricted-plugin product journeys
   that exercise complete loops and failure messages.
3. Establish one restrained visual baseline for prompt, selection, syntax,
   status, diagnostics, and inactive information before growing theme machinery.
4. Design explicit per-plugin capability grant UX if plugins need broader effects;
   never treat a physical keypress as blanket approval.
5. Reduce `Editor` coordinator and revision-note gravity only through small owner
   modules or generated contracts with measured handoff improvement.
6. Keep the VM deterministic, replayable, and tiny; do not solve editor
   convenience by adding ambient filesystem/process authority to the language.

## Validation

The final bounded evidence is intentionally explicit:

- `166 passed` in the focused authority/startup/keymap/hostcall/plugin/resource
  slice;
- `32 passed` across revision/context/docs/effect/audit/archive checks, with the
  five effect-contract tests split into individual bounded runs after a combined
  process exceeded the command window without reporting an assertion failure;
- `156/156` portability cases passed;
- `make timely` passed all five stages: context, audit, lint, portability, and
  doctor;
- the generated installed effect/resource contract is current.

The package verifier is run against the final archive after creation. These
results do not claim a complete full-suite release manifest; `make
release-verify` remains the stronger completeness gate.
