# Cold review protocol

A poem draft may be judged only after the turn in which it was written has closed and a new web pulse has been logged.

Allowed in rev0013:

- judge `P0001-D001`, because it was drafted in rev0012 turn 4;
- revise from that judgment;
- record the revision delta.

Forbidden in rev0013:

- judge `P0001-D002`, because it was drafted in rev0013 turn 5;
- promote `P0001-D002` to anthology or evidence status;
- treat quote-search, branch validation, or metrics as literary proof.

A valid judgment record must include `created_turn`, `target_created_turn`, and `firewall_ok`. The package validator checks that no judgment has `created_turn <= target_created_turn`.
