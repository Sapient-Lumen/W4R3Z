# Contributing

This repo is an archive of “missing crates” proposals with evidence and real planning.

## Add a new proposal
1. Copy `templates/proposal.md` to `proposals/<short-name>.md`.
2. Fill in the front matter:
   - `id` (next P-####)
   - `status`
   - `domains`
   - `last_reviewed`
   - `evidence` (>= 3 links)
3. Include:
   - clear problem statement
   - prior art scan (name existing crates/tools and why insufficient)
   - MVP + milestones
   - sustainability plan (maintenance + governance)

## Add a research entry
- Create `entries/YYYY-MM-DD.md` summarizing *new* signals and linking sources.

## Validation
CI runs `python scripts/validate_archive.py` to ensure:
- proposal front matter is present
- ids are unique
- INDEX includes all proposals/entries

If CI fails, fix the reported file.

