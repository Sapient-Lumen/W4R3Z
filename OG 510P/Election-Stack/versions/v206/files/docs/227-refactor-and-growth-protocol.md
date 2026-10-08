# 227. Refactor and growth protocol (keep the archive small, stable, and maintainable)

**Track:** Shared

This archive is designed to survive long-horizon maintenance by humans and LLMs.
That only works if refactors are **predictable**, references are **stable**, and growth is **disciplined**.

This doc is a compact protocol for:
- making structural changes without breaking readers/tools, and
- adding material without inflating the archive or duplicating prose.


## 227.1 Non-negotiables

1) **Doc numbers are the API.**
   - References like `DOC:docs/173...` and `DOC:docs/193...` are treated as stable.
   - If you change filenames, do not change the doc number.

2) **Do not break links.**
   - If a file is renamed or a doc is merged, leave a **tombstone alias** (see `docs/TOMBSTONES.md`).
   - Tombstones contain **no normative content**; they only point.

3) **Avoid “archive bloat by copy.”**
   - Prefer **registries / templates / checklists / schemas** over duplicative prose.
   - Prefer a 1–2 line pointer over repeating an explanation in multiple places.

4) **Refactors must be mechanically reviewable.**
   - A refactor that cannot be reviewed as “mostly move/rename, no semantics” is not a refactor.
   - If semantics change, treat it as a semantic change (see 227.2).


## 227.2 Refactor classes (and what they require)

| Class | What changes | Allowed to change meaning? | Minimum required updates |
|---|---|---:|---|
| **R0: Formatting** | whitespace, heading hygiene, spelling | No | run doc link checks; no changelog entry unless wide-ranging |
| **R1: Navigation** | indexes, READMEs, bundle ordering | No | update `docs/13` / track READMEs as needed; keep links stable |
| **R2: Structural** | rename/move files, split/merge docs | No (unless explicitly upgraded) | tombstones + index updates + release gate |
| **R3: Semantic** | normative requirements, schemas, envelopes | Yes (explicitly) | claims/boundaries review + ADR if needed + versioning + examples + release gate |

Notes:
- **R2 is the danger zone**: it looks non-semantic, but it’s where link-rot and “lost canonical doc” failures happen.
- If you start in R2 and discover you need R3, stop and re-scope the change as R3.


## 227.3 Stable references (how to rename without breaking)

### 227.3.1 Renaming a numbered doc file

Example: renaming a numbered doc file for clarity (keeping the same doc number),
and leaving the old filename as a tombstone alias.

Protocol:
1) Ensure the **canonical** file exists and is the intended target.
2) Create/keep the **old filename** as a tombstone:
   - Title begins with `Tombstone:`
   - Body contains only a short pointer to the canonical doc.
3) Run the tombstone index generator: `python3 scripts/gen_tombstone_index.py`.
4) Run the doc link checks + release gate.

### 227.3.2 Splitting a doc

- Keep the original doc number as the canonical “interface” doc.
- Put deeper material into:
  - a new numbered doc **only if** it introduces a new stable surface, OR
  - a checklist/template/registry if the content is list-like or operational.
- Add 1–2 line pointers (no duplicated prose).

### 227.3.3 Merging docs

- Choose one canonical doc number.
- The deprecated doc becomes a tombstone that points to the canonical doc.
- Do **not** keep two docs that both claim to be canonical for the same interface.


## 227.4 Growth discipline (how to add without exploding size)

### 227.4.1 The “registry-first” heuristic

If a change creates:
- a list of codes → add a **registry** (CSV) + generated doc if needed.
- a repeated operational step → add a **checklist**.
- a repeated publication artifact → add a **template**.
- a new object shape → add a **schema** + minimal example packet.

Only add new prose if it:
- removes ambiguity that tools/checklists cannot capture, or
- defines a stable interface that other docs must reference.

### 227.4.2 Keep additions tight

Default targets (soft caps):
- A new section: ~2 screens.
- A new doc: “short spec + bullets,” not an essay.
- Prefer **citations** (`source:` / `xref:`) over pasted external text.

### 227.4.3 Delete to add

If you add prose, delete or compress nearby redundant prose in the same change.
If you can’t identify redundancy to delete, you probably shouldn’t be adding prose.


## 227.5 Mechanical checklist (before you cut a release)

- Update navigation surfaces:
  - `docs/13-artifact-index.md`
  - `ARCHIVE_INDEX.md` and `README.md` (when the change affects entrypoints)
  - track READMEs/bundles if Track A/B/C entrypoints changed

- Run the release gate:
  - `python3 scripts/release_gate.py`

- If the release gate regenerated artifacts, regenerate the manifest:
  - `python3 scripts/build_manifest.py`

- Update:
  - `CHANGELOG.md` (top entry)
  - `VERSION`
  - `docs/START_HERE.md` recent-additions range (see `scripts/check_version_consistency.py`)


## 227.6 “When in doubt” rules

- If the change is mostly moving things around: do it as **R2** with tombstones.
- If you touch schemas, envelope semantics, verifier outputs, or claim boundaries: it’s **R3**.
- If you’re tempted to paste long background: add a `source:` pin and write a 3–8 bullet synthesis instead.

