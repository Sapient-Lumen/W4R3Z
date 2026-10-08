# rev0080 choice request trace guard

The riskiest remaining replay seam was that traces proved the selected `LegalAction`, but not the choice surface from which that action was selected. A replay could therefore apply the same action even if action enumeration had silently changed around it.

rev0080 adds a small typed `ChoiceRequest` boundary instead of another registry. The engine now exposes `choice_request_for_player(...)`, `current_choice_request(...)`, and `choice_request_hash(...)`. The hash binds the StateCore hash, chooser, request kind, required-gate flag, and the ordered set of canonical legal-action hashes. Display labels remain excluded.

`apply_action(...)` samples this request before mutation and stores `choice_kind`, `choice_request_hash`, `choice_action_count`, and `choice_required` on the action receipt. `ActionTrace.v1` carries the same fields. During replay, a nonzero expected choice hash is checked before state-hash and apply-result checks, so choice-enumeration drift fails as `ChoiceRequestHashMismatch` without writing new journal rows.

The first required gate is pending-trigger stack placement: when pending triggers block priority, `current_choice_request(...)` reports `PendingTriggersToStack` with `required=true`. This is intentionally a foundation for later APNAP trigger-order choices, simultaneous choices, and hidden/optional choice requests without overbuilding those protocols in this revision.

A small build refactor keeps the monolithic C++ regression translation unit at `-O0` in Release. That is not gameplay semantics, but it prevents optimizer work on the test driver from crowding out substantive validation in linked cloudtainer revisions.
