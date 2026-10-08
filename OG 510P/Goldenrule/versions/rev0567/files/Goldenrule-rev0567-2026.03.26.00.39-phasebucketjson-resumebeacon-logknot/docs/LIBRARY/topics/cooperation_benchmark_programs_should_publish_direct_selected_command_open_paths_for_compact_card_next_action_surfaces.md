# Compact-card next-action surfaces should publish direct selected-command open paths

The compact-card next-action surfaces should not stop at naming the machine target that a selected command verifies or refreshes.
An inheritor who just ran the selected next step or its first fallback should also get one stable retained path to open immediately afterward, without having to infer the rendered markdown sibling from naming conventions.

Therefore the next-action witness and primary next-action surface should, whenever the selected command target is a known compact-card report with a retained markdown companion:

1. publish one `selected_next_command_open_path` for the selected next command;
2. publish one `selected_fallback_command_open_path` for the first distinct fallback command;
3. mirror those values onto `primary_action.target_open_path` and `primary_action.fallback_open_path`; and
4. leave the fields null when no stable retained open path is available.

This keeps the first recovery ladder locally actionable: run the command, then open the surfaced retained document path and inspect the result.
