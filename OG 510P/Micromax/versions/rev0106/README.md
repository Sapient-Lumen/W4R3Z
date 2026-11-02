# Micromax — rev0106

## Discover a command without losing the question

This early edition already treats finding an editor operation as part of using it. Its [prompt-completion design](files/docs/64-editor-prompt-completion.md) connects three neighboring activities: looking up a topic, inspecting a reachable keybinding and choosing a command or action. They share suggestion rows carrying an insertion value, a kind, a menu label and explanatory information. The same structured selection can therefore support a terminal menu and a script's inspection of the current item.

The distinction becomes concrete when browsing. Up and Down move the highlighted picker row without replacing the typed query; command and find prompts retain their history-navigation behavior. Accepting a topic opens help, while accepting a binding inspects its meaning rather than performing the bound action. In the command palette, choosing an action runs it, whereas choosing a command opens a prefilled command prompt. Similar-looking lists need not give Enter the same meaning. The [editor implementation](files/src/micromax_editor/editor.py#L5176-L5290) carries those different outcomes.

Read the [cookbook](files/docs/71-cookbook.md) next for two small extension ideas: attaching a human-readable label without changing the binding's behavior, and inspecting a selected row without rebuilding its ranking. Its examples mix available hostcalls with explicitly provisional patterns, so read them beside the implementation rather than treating every sketch as a finished feature. For the later product and its self-criticism, return to the [collection guide](../../README.md).

A concatenative language, reference VM and terminal-editor project with capability-scoped automation. Selected snapshots document a long progression toward a headless-plus-curses editor. Rev1000 distinguishes available release evidence from complete and passed evidence, and emphasizes product use over more auditing machinery. Its in-process capability model is not an OS sandbox for hostile native code.

## Read the supplied entry points

- [README.md](files/README.md)
- [LICENSE](files/LICENSE)

## Preservation and limits

Original upload bytes and extracted member bytes are retained. ZIP member CRCs were checked; SHA-256 inventories cover all extracted members. No supplied program, bootstrap, simulation, workflow or validation command was executed. Rights and notices remain applicable; no blanket license is added.

Internal inventory review: No mismatch was found in the limited inventory formats checked; this is not a claim that every internal manifest was validated.

- [Extracted-member inventory](INVENTORY.json)
- [Review scope](INTEGRITY.json)
- [Original Micromax-rev0106-2026.03.05.03.03-pickerkinds-mdcode-citrinebadger.zip](../../originals/Micromax-rev0106-2026.03.05.03.03-pickerkinds-mdcode-citrinebadger.zip)

Lumen added this guide beside the unchanged archive material.
