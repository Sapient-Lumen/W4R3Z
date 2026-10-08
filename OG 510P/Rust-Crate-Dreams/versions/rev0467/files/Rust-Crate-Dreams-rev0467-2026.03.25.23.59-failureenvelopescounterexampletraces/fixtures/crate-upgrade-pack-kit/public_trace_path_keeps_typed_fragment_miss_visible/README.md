# Scenario: public trace path keeps typed fragment misses visible

This scenario captures a pack that looks almost ready for public freeze, but one exported summary claim still points at a route that cannot actually be followed on the public surface.
The root problem is not merely “a missing reference”; it is a **public trace-path fragment miss**.

The example keeps that miss typed instead of collapsing it into a generic validation error.
That way reviewers can tell that the pack failed on the public trace route itself: the summary is public, the intended supporting receipt is public, but the exact fragment or anchor being promised is absent on the exported surface.

This is the same honesty move that typed docs-jump failures make elsewhere: keep the failed surface visible on both success and failure.
