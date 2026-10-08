# renamed_multi_target_delegate_bridge

This scenario freezes the case where a reusable helper artifact is consumed under renamed multi-target dependency entries.

The important property is not merely that the renames are valid.
It is that the artifact-dependency bundle can explain the **delegate-helper bridge posture** instead of looking like an ordinary tool-binary dependency.
