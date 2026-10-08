# Rev0819 sealed-parent/current unlink-authority differential

The same C++20 harness is compiled against sealed rev0818 and rev0819. On Linux,
`--wrap=unlinkat` interposes the old failure cleanup. Immediately before the
actual deletion, the wrapper renames the writer-created temp inode away and
installs a foreign regular file at the checked pathname.

- rev0818 calls `unlinkat` once and deletes the foreign replacement. The harness
  exits 1 because `vulnerable=true`.
- rev0819 calls `unlinkat` zero times. Its independent in-tree regression also
  proves that failure sanitation follows the retained writer descriptor after
  the name is rebound. The harness exits 0 because `vulnerable=false`.

The compiled reproducer executables are intentionally excluded from the source
package. Build commands and machine-readable results are retained here.
