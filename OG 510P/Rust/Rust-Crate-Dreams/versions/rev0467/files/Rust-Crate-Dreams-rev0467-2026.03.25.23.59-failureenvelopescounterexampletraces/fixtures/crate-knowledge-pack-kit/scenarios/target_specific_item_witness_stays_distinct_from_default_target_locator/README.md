# Scenario: target-specific item witness stays distinct from a default-target locator

Problem:
A crate exports different visible APIs or docs surfaces per target.
A downstream tool saw a default-target docs.rs page and is about to reuse it for a Windows-specific claim.

What this scenario proves:
Item witness records must keep target explicit, even when a convenient default-target route exists.

Good outcome:
The bundle records a separate witness for the Windows-target item and points at a target-aware locator plus a fallback locator.
