# Surface/Apparatus Split Branch Lattice

A surface/apparatus split branch lattice is a machine-native draft object with two inseparable surfaces:

1. A readable poem surface containing the selected path and a shadow sentence derived from rejected branches.
2. An external branch packet containing the full candidate lattice, selection states, rejection notes, and verification claims.

The form exists to prevent two opposite failures: hiding the machine process so the poem becomes a human-mask lyric, and printing the whole process so the poem becomes an audit report.

Required checks:

- branch packet exists;
- selected path has exactly one selected candidate per layer;
- selected candidate initials match the declared word;
- unselected final words match the declared shadow sentence;
- selected lines appear in the draft;
- full residue lattice is not printed inline;
- selector map exists for selected lines;
- disclosure condition is present;
- same-turn quality judgment is prohibited.

Primary validator: `tools/check_surface_apparatus_split.py`. Supporting validators: `tools/check_branch_selector.py`, `tools/check_selector_map.py`, `tools/check_judgment_firewall.py`.
