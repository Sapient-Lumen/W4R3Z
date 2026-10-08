# Scenario — Tower buffer-before-limit and limit-before-buffer must not share the same admission path

Tower documents that middleware order changes the effective in-flight surface.
This scenario keeps that order visible instead of flattening both stacks into “buffered + concurrency limited”.
