# private_edit_rebuilds_dependents_without_interface_proof

A private upstream edit in a crate causes reverse dependencies to rebuild.

This scenario exists so P-0469 reports the **observed fanout** while staying honest that it still lacks stable proof of public-interface change.
The report may mark some dependents as `relink_candidate_possible`, but it must not overclaim.
