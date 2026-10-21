# Micromax

## An editor whose automation can be understood

Micromax is a terminal editor for ordinary work that also lets its user inspect and reshape how the work happens. Open a project file, find a passage, edit several occurrences, undo a change, save, or recover interrupted work; then use the same small language to define commands, configuration and extensions. Its ambition is not merely a tiny language or a large test suite. It is an editor pleasant enough to inhabit and explicit enough to change deliberately.

The supplied rev1000 joins a Python reference VM, a headless editor model and a curses interface. The [tutorial](versions/rev1000/files/docs/70-tutorial.md) begins with that working editor, not a promise of a future one. The project's distinctive question is what happens when useful automation persists beyond the moment it was written: which code is running, what may it change, and what should survive when it fails?

## A small language inside a daily tool

The language is concatenative: values enter a stack and successive words transform them. `1 2 +` pushes two numbers and adds them; a named word can package a useful sequence. Quotations, written as bracketed code, are values that can be passed to control combinators or retained for callbacks. Wordlists and modules organize names; documentation and stack-effect metadata make a word inspectable.

That gives configuration, macros and plugins a shared automation vocabulary. Recorded editor macros are action and command steps replayed with their recorded provenance, not simply serialized language quotations. A reader can start with a short word, inspect its meaning, attach behavior to a command or hook, and follow the effect into the editor. The editor embedding routes effects through explicit host operations and policy; the standalone reference VM also provides local source loading. Inside the editor, editing, filesystem access, processes, clipboard and UI operations do not imply that every script inherits the operator's reach.

The [source-owner map](versions/rev1000/files/docs/02-repo-map.md) identifies these layers and their source owners. The reference VM and portability corpus describe observable semantics for other implementations; they do not mean a complete Rust or Wasm editor has already been delivered.

## One editor model, more than one way to see it

The curses UI, line-oriented interface and compact headless screen representation consume the same editor model. The point is not simply that the editor has tests. A command, its resulting selection, a failure message and the current buffer can be inspected without reconstructing them from terminal paint operations. Human-facing behavior and machine-readable observation are connected at the model.

The ordinary loop includes project and buffer pickers, search, query-replace, selections, multicursor editing, a command palette, help and Undo/Redo. The [current product account](versions/rev1000/files/README.md) explains their less visible choices. Query-replace plans against an identified source generation rather than repeatedly matching the text its own replacements create. Simultaneous edits use a common pre-edit document and reject ambiguous overlap before committing. These choices matter when an apparently simple command affects many places: “replace these occurrences” should not silently become a different operation halfway through.

Headless output is also not automatically success. Failed startup can still leave a live fallback buffer and useful screen data while returning a failure status for the requested open. A consumer must distinguish an inspectable state from achievement of the requested action.

## A gesture does not give an extension new authority

In restricted startup, plugin metadata can be inspected without evaluating its source. Loading approves a bounded captured package. Running callbacks use the committed bytes, not whatever happens to occupy the same filenames later. For a loaded plugin, approving replacement bytes and explicitly reloading them are separate steps.

The same distinction follows delayed work. A keybinding created by a plugin remains plugin-owned when someone later presses its key. The physical gesture does not turn that callback into unrestricted operator code. Saved macros, timers, hooks and active interactions raise related questions about which generation created them and whether that generation still has authority.

The [security contract](versions/rev1000/files/docs/security-boundaries.md) and [repository map](versions/rev1000/files/docs/02-repo-map.md) explain that lifecycle. Graceful unload may run a plugin's cleanup code; revocation instead removes managed runtime without invoking that lifecycle code. Cleanup and rollback have defined coverage, not a promise to reverse arbitrary filesystem or external effects.

The [host-owned execution budget](versions/rev1000/files/src/micromax_editor/plugin_execution_budget.py) makes another boundary concrete. A script's own budget controls cannot enlarge the surrounding host limit. But instruction fuel is not a universal timeout or memory limit: a blocking Python hostcall and native code require different treatment. This is an in-process application capability model, not an operating-system sandbox for hostile Python or native extensions.

## Recovery and confirmation belong to the actual state

Consider closing a dirty buffer. A remembered “yes, warned already” bit is inadequate if the document changed after the warning. Micromax's [discard guard](versions/rev1000/files/src/micromax_editor/discard_guard.py) compares the operation, live target identities, mutation versions, paths, dirty states and retained context. An unchanged second request can confirm; a changed target refreshes the warning. Even an edit later undone to identical text changes the mutation witness.

Interrupted saves receive another treatment. For eligible foreground saves, it attempts a private recovery checkpoint before commit; loss of that auxiliary protection is reported rather than making the document impossible to save. Recovery opens retained text into a dirty review buffer rather than silently overwriting the destination. A changed target still calls for an explicit force or save-as decision. Recovery is therefore an opportunity to inspect and choose, not a claim that everything has been restored automatically.

The larger design connects ordinary usability to exactness. A stale confirmation should not discard new work; an old plugin callback should not borrow a new grant; a replacement answer should not operate on a different buffer generation. Those are different mechanisms serving a recognizable editing experience.

## The self-criticism belongs after the product

The [rev1000 mission audit](versions/rev1000/files/REV1000_AUDIT.md) asks whether the project has become better at building a trust laboratory than at proving an editor worth adopting. It identifies real working software while challenging the accumulation of procedure, coordinator complexity and weak sustained-user evidence. It also separates the presence of a release manifest from current, internally consistent, complete and passed evidence.

That is not a reason to reduce the work to its shortcomings. It makes the tension legible: understandable automation and recoverable failure are valuable, but they do not by themselves establish taste, flow or sustained usefulness. The proposed next steps are historical project directions, not completed adoption results.

## Read by the question you bring

- For the actual editing loop, begin with the [tutorial](versions/rev1000/files/docs/70-tutorial.md), then the [current product account](versions/rev1000/files/README.md).
- For implementation and extension authority, read the [repository map](versions/rev1000/files/docs/02-repo-map.md) beside the [security boundaries](versions/rev1000/files/docs/security-boundaries.md).
- For the project's changing judgment, compare the [early language-and-editor account](versions/rev0106/files/README.md) with the [rev1000 audit](versions/rev1000/files/REV1000_AUDIT.md). The early snapshot already contains editor machinery; the later correction is not an origin story in which none existed before.
- Read beside [AnonSync](../AnonSync/README.md) for another project asking how technical rigor serves ordinary work, and [Rust](../Rust/README.md) for proposed tools judged by what they would let their users do.

## Version shelf and preservation

### Supplied snapshots

The reading route above is selective. This shelf retains every supplied snapshot and its original identity.

- [rev0106](versions/rev0106/README.md): 240 preserved members; `Micromax-rev0106-2026.03.05.03.03-pickerkinds-mdcode-citrinebadger.zip`.
- [rev0204](versions/rev0204/README.md): 317 preserved members; `Micromax-rev0204-2026.03.09.14.08-matchbracestyle-mapoverwrite-bracecue-wren.zip`.
- [rev0301](versions/rev0301/README.md): 410 preserved members; `Micromax-rev0301-2026.03.18.07.16-impactprimary-nextcut-firstcmd-fernotter.zip`.
- [rev0401](versions/rev0401/README.md): 514 preserved members; `Micromax-rev0401-2026.03.19.20.27-helpjumpfragmiss-trust-clear-larkspurjay.zip`.
- [rev0504](versions/rev0504/README.md): 617 preserved members; `Micromax-rev0504-2026.03.21.23.11-showrecentdirsample-recentdirdetail-trust-glenfox.zip`.
- [rev0607](versions/rev0607/README.md): 742 preserved members; `Micromax-rev0607-2026.03.23.12.18-showplugin-runtime-rootsummary-truth-trust-turnstone.zip`.
- [rev0712](versions/rev0712/README.md): 824 preserved members; `Micromax-rev0712-2026.03.28.13.51-macro-recordability-kind-helper-maplelapwing.zip`.
- [rev0799](versions/rev0799/README.md): 996 preserved members; `Micromax-rev0799-2026.06.05.05.58-clipboard-undo-persistauth-seal.zip`.
- [rev0893](versions/rev0893/README.md): 1,180 preserved members; `Micromax-rev0893-2026.06.18.18.30-stalemacro-timerbudget-macroslotrefactor-mapleoriole.zip`.
- [rev1000](versions/rev1000/README.md): 1,542 preserved members; `Micromax-rev1000-2026.08.01.02.39-mission-product-reality-evidence-honesty-oriole.zip`.

[Original identities](PROVENANCE.json) · [Back to OG 510P](../README.md)
