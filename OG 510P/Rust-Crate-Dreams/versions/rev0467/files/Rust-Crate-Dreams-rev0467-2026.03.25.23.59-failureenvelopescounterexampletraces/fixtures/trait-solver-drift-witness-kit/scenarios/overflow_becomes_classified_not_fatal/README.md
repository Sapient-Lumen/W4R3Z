# Scenario: overflow becomes classified, not just fatal

This scenario keeps overflow behavior honest across solver lanes.

Current compiler docs explicitly note that overflow information can be surfaced differently when using `-Znext-solver`.
The artifact should preserve that this is not just generic failure text churn, but a real obligation-class / outcome-shape change.
