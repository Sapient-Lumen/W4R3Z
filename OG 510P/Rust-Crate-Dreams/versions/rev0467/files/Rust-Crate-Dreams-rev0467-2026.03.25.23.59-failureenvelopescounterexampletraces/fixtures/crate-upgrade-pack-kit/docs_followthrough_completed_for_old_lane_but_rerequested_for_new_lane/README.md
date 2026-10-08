# Scenario — docs follow-through was completed on an older lane but must be re-requested now

This scenario captures a migration family where documentation/example updates were completed on an earlier release pair, but a newer pair touches the same surface again.

The fixture should prove that:
- a retained migration step is not the same thing as an active request,
- an older completion receipt should not silently close the current lane,
- and the pack should make `rerequest_needed` explicit.
