# crossbeam_select_ready_choice_is_random_without_biased_mode

Crossbeam `Select` documents that if multiple operations are ready at the same time, a random one is selected. It also documents `new_biased`, which instead selects the lowest index when multiple handles are ready.

This scenario exists to keep **underlying channel order** separate from **cross-surface ready-operation choice**.
