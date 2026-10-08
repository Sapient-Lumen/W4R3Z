# Repository hygiene and scope audit

The verified rev0872 parent has 337 files in the verifier's active v2
projection. Rev0873 has 340. Exactly 13 active files differ: ten modifications,
three additions, and no removals. The additions are one time-fence header, one
production translation unit, and one focused runtime test.

The final scan found no `__pycache__`, `.pyc`, VCS metadata in the publication
tree, build directory, object/static/shared library, executable, core dump, or
symlink. Build and analyzer outputs are retained only as text/JSON evidence.

The schema adds two bounded columns to each outbox row rather than a growing
observation log. Legacy provenance is one explicit enum tag, not a fabricated
history record. The time fence remains one singleton row. These choices close
the correctness gap without creating unbounded audit storage.

The largest remaining waste is architectural: every owner mutation reloads and
reprojects full retained history and performs another staged full restore before
commit. This is valuable as a correctness oracle but should not become the
production hot path. Indexed point reads, exact conditional updates, and a
separate periodic full auditor are the next scaling refactor.
