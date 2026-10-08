# 282 — Reference Integrity and Canonical Link Remediation

**Purpose:** harden the merged archive against silent navigation failure by fixing stale internal references, documenting intentional legacy exceptions, and defining a repeatable link-integrity rule for future revisions.

**Why this matters:** a semantically strong archive still degrades if internal references drift after renumbering, canonicalization, or merge work. Broken memo references create *retrieval amnesia*: ideas still exist, but readers and future editors stop finding the right neighbors.

---

## What rev446 fixed

rev446 corrected stale or pre-merge references in active memos, including:

- scope synthesis and systems navigation (`176`, `280`)
- control-loop and participation memos (`104`, `111`)
- integrity / DPI / emergency / relocation / secrecy / resilience cluster (`163`, `164`, `165`, `166`, `168`, `169`)
- constitutional / labor / failure / dual-use / change-management cluster (`171`, `175`, `177`, `192`, `208`)
- war powers / drills / corrections (`222`, `223`, `232`)
- transitional justice retaliation link (`151`)

Typical failure classes:
1. **old-number survivors** after renumbering
2. **pre-canonical filenames** left behind after a memo was narrowed or renamed
3. **bridge-memo drift** where a surrounding cluster evolved but the cross-link did not
4. **historical labels mistaken for live file paths**

---

## Intentional exceptions (do not “fix” these away)

### 1. `271-worked-example-legacy-number-crosswalk.md`
This memo intentionally preserves rev380-era filename stems so older citations can still be resolved.  
Those stems are **historical lookup labels**, not active file paths.

### 2. `102-revision-log.md`
The revision log records historical filenames and earlier branch states. Some names in the log are not meant to resolve in the current tree.

### 3. Claude-feedback provenance memos (`100`, `101`) and source-relative references
These preserve provenance back to non-archive source material and should not be normalized into fake current archive paths.

---

## Canonical rule going forward

A revision that adds, merges, narrows, or renumbers memos is **not complete** until it does all four:

1. **fix active internal references**
2. **update `00-README.md`, `75-archive-map-and-entry-points.md`, and `102-revision-log.md`**
3. **record intentional legacy exceptions explicitly**
4. **re-run a stale-reference scan before zipping**

---

## Lightweight scan rule

Treat these as high-priority defects:
- backticked archive filenames that no longer exist
- attachment-guide references to non-canonical memo names
- “see also” blocks that route readers into dead ends

Treat these as low-priority / intentional:
- source-relative provenance paths
- revision-log historical names
- legacy crosswalk labels clearly marked as historical

---

## Anti-regret principle

When a merge creates tension between:
- preserving old retrieval clues, and
- keeping current navigation clean,

prefer this pattern:

- keep **one canonical current path**
- preserve **legacy lookup labels only in explicit crosswalks**
- do **not** let historical labels masquerade as current live references

That preserves salience without leaving future editors to guess which name is real.
