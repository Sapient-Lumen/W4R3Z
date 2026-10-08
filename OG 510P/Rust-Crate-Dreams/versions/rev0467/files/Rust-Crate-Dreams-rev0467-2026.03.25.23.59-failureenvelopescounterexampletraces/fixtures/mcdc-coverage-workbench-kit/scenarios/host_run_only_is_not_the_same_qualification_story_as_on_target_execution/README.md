# Scenario — host run only is not the same qualification story as on-target execution

This scenario protects the distinction between **useful evidence** and **the exact qualification story another reviewer may assume**.

A host-executed run can still be valuable for decision authority, construct support, and independence exploration.
But if the target deployment context differs materially, the crate must emit a conservative `qualification-basis.receipt.json` rather than quietly treating host execution as on-target qualification.
