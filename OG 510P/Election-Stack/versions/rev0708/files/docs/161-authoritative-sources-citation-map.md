# 161. Citation map (lockfile IDs → sources)

**Track:** Shared


This archive uses `evidence/lock/external-sources.toml` to pin authoritative external sources.
Normative docs SHOULD reference **lockfile IDs** rather than embedding fragile URLs.

## 161.1 How to cite a source in this archive

Preferred form in docs:

- `source: <lockfile id>`

Example:

- `source: rfc9162_txt`

## 161.2 Current pinned sources

See `docs/214-external-sources-index.md` (generated index) and the canonical lockfile `evidence/lock/external-sources.toml`.

The index is intentionally **no‑URL** and includes each lockfile ID, whether it is sha256‑pinned, the retrieval date, tags, and a short note.



## 161.3 Precedence order (recap)

When sources conflict, prefer:
1. binding law/regulation (jurisdiction-specific)
2. election authority certification standards (e.g., EAC/VVSG)
3. NIST publications and formats
4. IETF RFC Editor publications
5. peer-reviewed research
6. vendor blogs/whitepapers (informative only)

## 161.4 Drift triggers

If a pinned source changes (sha mismatch) or a new upstream version is published:
- file an ADR,
- update affected claims/evidence lanes,
- and bump `VERSION` if interoperability semantics could change.
