# Selector Vector Branch Lattice

A selector-vector branch lattice extends the surface/apparatus split form. The readable surface contains selected branch lines and a shadow sentence. The external apparatus contains:

- a branch packet with rejected continuations;
- a selector map with exact selected-line text and character start/end positions;
- a selector vector mapping each selected-line span to a fixed slice of the shadow sentence.

The form exists because D003 made the apparatus reachable but not active enough. D004 makes addressability part of the poem object: exact spans fetch the shadow in ordered triplets.

Required checks:

- branch packet exists and has exactly one selected candidate per layer;
- selected line initials spell the declared path word;
- unselected final words spell the declared shadow sentence;
- selector map exact text and positions match the rendered draft;
- selector vector exists;
- selector vector shadow words match packet-derived shadow words;
- each selector vector span extracts the selected line from the source draft;
- each vector item maps to the correct shadow-word slice;
- same-turn quality judgment is prohibited for the current draft.

Primary validators: `tools/check_branch_selector.py`, `tools/check_selector_map.py`, `tools/check_selector_vector.py`, and `tools/check_judgment_firewall.py`.

Non-claim: selector-vector validation proves addressable construction only. It is not a poem-quality proof.
