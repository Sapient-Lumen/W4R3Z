# Rev547 — keep `showrecent PATH` exact path misses honest before Enter

Problem:
- `showrecent PATH|N|#N` already reported exact misses honestly after Enter as `showrecent: no such recent file: PATH`.
- rev545 taught nearby recent surfaces to keep visible-slot misses honest in picker rows and exact completion rows.
- but plain `showrecent /missing/path.txt` could still go blank in the command bar because completion only preserved typed raw tokens for slot-like `N|#N` inputs.

Small fix:
- preserve one raw first-argument candidate for `showrecent` whenever the user has typed a non-empty exact token and no existing recent candidate matches.
- let `_prompt_exact_recent_row(..., strict_missing=True)` surface `no such recent file` for that exact inspector row instead of the generic fallback hint.
- leave adjacent fuzzy recent pickers alone: this change is only for the side-effect-free exact inspector surface.

Why it matters:
- trust: exact inspectors should say the same miss truth before Enter and after Enter.
- flow: humans and future LLMs no longer have to press Enter just to confirm one typed recent-file path is not remembered.
- coherence: `showrecent` now matches the same exact-miss honesty already present in `showrecentdir`, `showjump`, and the recent picker slot surfaces.
