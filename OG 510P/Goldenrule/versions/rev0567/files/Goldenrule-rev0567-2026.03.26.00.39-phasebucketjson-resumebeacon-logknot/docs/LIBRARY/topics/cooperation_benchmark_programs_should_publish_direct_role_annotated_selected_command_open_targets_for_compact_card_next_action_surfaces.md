# Compact-card next-action surfaces should publish direct role-annotated selected-command open targets

The compact-card next-action surfaces should not stop at publishing bare open-path strings for the selected next command and its first fallback.
Once those inspect-after-run paths are part of the handoff ladder, inheritors and validators should be able to treat them as typed retained objects rather than untyped prose.

Therefore the next-action witness and primary next-action surface should, whenever a selected command publishes a retained open path:

1. publish one `selected_next_command_open_target` alongside `selected_next_command_open_path`;
2. publish one `selected_fallback_command_open_target` alongside `selected_fallback_command_open_path`;
3. mirror those values onto `primary_action.target_open_target` and `primary_action.fallback_open_target`; and
4. attach stable role codes that explain whether the retained document is the selected next-step inspect target or the first-fallback inspect target.

This keeps the post-command inspect step machine-checkable: run the command, then open the surfaced retained target object and know why it is the right first document to inspect.
