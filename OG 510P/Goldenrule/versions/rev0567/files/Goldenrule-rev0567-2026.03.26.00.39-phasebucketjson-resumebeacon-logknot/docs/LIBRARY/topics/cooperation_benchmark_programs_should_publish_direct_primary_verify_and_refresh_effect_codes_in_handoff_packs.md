# Cooperation benchmark programs should publish direct primary verify and refresh effect codes in handoff packs

If a compact-card handoff pack already publishes a direct first verify command and a direct first refresh command, it should also publish one small effect-code witness for each of those commands.

The goal is to remove one more inheritor inference step: the inheritor should not have to guess from command spelling whether the first command is read-only or whether it mutates retained reports.

For the canonical compact-card handoff pack, that means publishing `primary_verify_effect_code` and `primary_refresh_effect_code` as strict aliases of the retained first verify and first refresh semantics already present in the pack. These fields are not a second command-selection policy. They are a compact interpretation aid for the direct primary commands already retained.
