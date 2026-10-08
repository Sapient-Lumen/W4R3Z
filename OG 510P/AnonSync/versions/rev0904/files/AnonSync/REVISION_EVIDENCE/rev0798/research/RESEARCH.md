# Rev0798 research notes

SQLite's file-format specification defines a 100-byte database header. The
two-byte field at offset 16 encodes page size; 1 means 65,536 bytes. The
four-byte field at offset 28 is the database size in pages. That page count is
considered valid only when the file-change counter at offset 24 equals the
version-valid-for field at offset 92.

That validity rule is security-relevant for AnonSync: a stale page-count field
is observation but not exact file-extent authority. For a byte-sealed,
sidecar-free snapshot, rev0798 therefore accepts only a current header and
requires `page_count * page_size == exact descriptor bytes`.

The SQLite backup API copies the logical database page graph, not arbitrary
suffix bytes in the source file. The retained executable proof appends one full
page, observes ordinary SQLite read it successfully, then observes backup
normalize it away. The experiment is intentionally permanent in the test tree
rather than existing only as prose.

References:

- <https://www.sqlite.org/fileformat.html>
- <https://www.sqlite.org/backup.html>
- <https://www.sqlite.org/testing.html>
