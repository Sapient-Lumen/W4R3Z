# Rev826 — command-dispatcher formatter/buffer seam extraction

Rev826 attacks the next concrete risk after the registry work: `install_default_commands` had become a large closure that mixed command behavior, detail-row formatting, live inventory summaries, file/buffer commands, and registration calls.

## What changed

Two behavior-preserving extraction modules were added:

```text
src/micromax_editor/command_formatters.py
src/micromax_editor/buffer_commands.py
```

`command_formatters.py` now owns exact detail-row formatting, inventory row formatting, cursor-target feedback strings, recent/jump/mark/plugin summary snippets, and the small parse/feedback helpers used by command handlers.

`buffer_commands.py` now owns the file/buffer/navigation command family:

```text
open/save/save!/saveas/revert/revert!/diff/diskstate
close/close!/closeall/closeall!/only/only!/prevbuf
recent/recentpick/recentdirpick/showrecent*/buffers/buffer
mark/markjump/marks/goto/jump/jumpback/jumpforward/pwd/cd
```

The public command names, docs, message strings, capability gates, and command dispatcher registrations are intentionally unchanged.

## Audit guard added

`tests/test_command_dispatcher_hygiene.py` now checks that default command names are unique, default command registrations have docs, and the default-command install closure does not grow formatting or buffer/file command families back into itself.

That matters because `CommandDispatcher.register()` intentionally supports overwriting for runtime/plugin command replacement. Default command registration therefore needs a separate cheap guard so a duplicate built-in name cannot silently mask an earlier built-in command.

## Size effect

After rev826:

```text
src/micromax_editor/command_dispatcher.py   3,636 -> 1,956 lines
src/micromax_editor/command_formatters.py   1,254 lines added
src/micromax_editor/buffer_commands.py        768 lines added
```

This is extraction-first. The next pass can split exact show/inspection commands and then plugin/macro subtrees without changing behavior.

## Validation

Focused command/prompt/buffer lanes passed after the extraction:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q \
  tests/test_command_dispatcher_hygiene.py \
  tests/test_command_cd.py \
  tests/test_editor_mx_commands_and_completion.py \
  tests/test_editor_buffer_mru_and_closeall.py \
  tests/test_editor_rawkeys_command.py \
  tests/test_editor_prompt_completion_hostcalls.py \
  tests/test_editor_command_authority.py \
  tests/test_editor_registration_groups.py \
  --durations=10
```

Result:

```text
371 passed in 12.91s
```
