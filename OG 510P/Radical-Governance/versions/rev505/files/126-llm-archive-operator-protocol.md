# LLM Archive Operator Protocol (Meta-Engineering)

**Purpose:** keep this archive coherent and small while using LLMs for ongoing research and revision.

**Audience:** anyone (human or AI) making changes to this repository.

**Core constraint:** *density over breadth*. Prefer one new high‑leverage memo over many medium ones. Prefer refactors that reduce duplication.

---

## Operator invariants

1. **Do not bloat.**
   - New files are rare; updates are preferred.
   - If you add a file, wire it into: `75-archive-map-and-entry-points.md`, `02-design-toolkit.md` (if relevant), and `102-revision-log.md`.

2. **Every new claim must be contestable.**
   - Put the “why” into a **receipt** or **test** (link `104` control loops, `107` test suite).
   - When in doubt: add a metric, a clock, or a contest lane.

3. **Prefer primitives over programs.**
   - Ship small, portable interfaces that many governance forms can adopt.
   - Avoid ideology; specify *mechanisms* and *failure-mode fixes*.

4. **Person-first lens.**
   - If a change doesn’t help a governed person navigate power safely, it’s suspect.
   - Tie system-level proposals back to `98-persons-path-and-accessibility-invariants.md`.

5. **Cite, don’t quote.**
   - Add **short citation keys** to `91-bibliography-extended.md` rather than importing large bodies of text.
   - Keep verbatim quotes minimal.
   - Strip UI-only citation artifacts (`cite…`, `turn…`, widget markers) before commit; archive markdown should contain durable bibliography keys, not chat-surface markup.

---

## Editing discipline

### Naming + numbering
- New memos use the next available number: `NNN-short-slug.md`.
- Keep slugs stable; prefer redirects via links rather than renames.

### Cross-link rules
- Each memo should link:
  - **Up** to the toolkit (`02`) or map (`75`) entry point.
  - **Sideways** to the nearest primitives (receipts/clocks/registries).
  - **Down** to any tests (`107`) that validate it.

### “Receipts” consistency
If you introduce a new receipt type:
- Use a 3–4 letter prefix + `-*` pattern (e.g., `CSR-*`, `CCR-*`, `DR-*`).
- State:
  - required fields
  - public vs private fields
  - clock/deadlines
  - appeal/contest hooks
  - minimal publishable metrics

### Avoiding duplicates
Before adding a memo:
- Search for overlap in existing primitives: records (`115`), time budgets (`108`), portability (`109`), dispute coordination (`114`), rule change (`118`), coercion (`116`), influence (`120`), whistleblowing (`121`), status (`125`).
- If overlap exists: patch the existing memo and add one paragraph linking the new angle.

---

## “Amnesia resistors” for LLM work

These are deliberately small but effective.

### 1) Maintain a stable kernel map
Treat `75-archive-map-and-entry-points.md` as the *canonical entry point* for:
- kernel anchors
- where to add new work
- what not to repeat

### 2) Keep the toolkit authoritative for primitives
Treat `02-design-toolkit.md` as the *one place* where primitive names and numbering live.
- Fix collisions immediately.
- Prefer adding **one new primitive** over introducing new terminology.

### 3) Revision log is the changelog of record
Treat `102-revision-log.md` as the canonical history:
- one section per revision
- what changed + why
- what got wired where

### 4) Default workflow for any new work
1. Identify the governance failure mode (capture, opacity, exclusion, delay, coercion, runaway exception).
2. Pick **one** portable interface to address it.
3. Add a test to `107` if it can be mechanically checked.
4. Wire to the map + toolkit; update revision log.

---

## Quality bar checklist (pre-zip)
- [ ] No more than ~1–2 new files unless necessary.
- [ ] Kernel map updated.
- [ ] Toolkit updated (if a primitive was added/changed).
- [ ] Revision log updated with rev + timestamp + codename.
- [ ] No large quotes copied in.
- [ ] UI-only citation artifacts stripped from committed markdown.
- [ ] Cross-scope applicability is explicit.

