# Scenario — `lldb-dap` and `lldb` CLI need an explicit comparison basis

This scenario exists because LLDB’s current docs split the user-facing stack into separate components:
LLDB itself, `lldb-dap`, and IDE integrations.

A green value rendering from `lldb` CLI and a green value rendering from `lldb-dap` plus an IDE integration may share an underlying engine but still differ in frontend surface, request path, and presentation behavior.

The point of this fixture is therefore to keep **comparison basis** explicit instead of flattening the two observations into one generic “LLDB passed” claim.
