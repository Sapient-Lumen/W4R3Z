# Rev657 - Macro count blocker precedence for missing slots

Problem:
- runtime `macro play|run NAME COUNT` already rejects recording/playback blockers before it checks whether `NAME` exists
- exact prompt rows for `macro play|run NAME COUNT` were mostly truthful after rev650/rev653/rev656, but one narrow mismatch remained
- when a user typed a missing slot while recording or playback was already active, the exact count row could still preview `no such macro` even though Enter would actually stop earlier with the live blocker

What changed:
- `_prompt_macro_count_row(...)` now preserves the existing `missing macro` detail column while giving blocker state precedence in the message column
- `macro run ghost 2` now previews `recording · live (1 step) · stop or cancel first` or `playing · demo (1 step) · wait for playback` when those are the first real runtime blockers
- focused prompt/runtime tests pin both recording-blocked and playback-blocked missing-slot count paths

Why it matters:
- exact prompt rows should show the first real reason Enter would stop
- later validation errors are still useful, but only when runtime can actually reach them
- this keeps the command bar aligned with dispatcher behavior in a tiny but high-trust automation seam
