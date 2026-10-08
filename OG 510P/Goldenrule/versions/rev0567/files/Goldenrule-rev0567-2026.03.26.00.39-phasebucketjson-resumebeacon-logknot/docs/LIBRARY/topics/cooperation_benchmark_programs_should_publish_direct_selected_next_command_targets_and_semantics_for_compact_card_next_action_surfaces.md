# Compact-card next-action surfaces should publish direct selected-next-command targets and semantics

When a compact benchmark program already emits a typed next-action witness and a typed next-action surface, the archive should not stop at the winning command string alone.

The inheritor still has to reconstruct what that command acts on and why it was chosen, especially in the common `verify_ready_surface` case where the chosen command verifies the fused control plane rather than the focus-lineage pack's first verify target.

So the archive should publish a tiny direct witness for the selected next command itself: its retained target path, its subject role, its one-line intent summary, its expected immediate outcome, and whether it is read-only or state-changing.

This keeps the chosen command locally legible and auditable without widening the card stack or creating another report family.
