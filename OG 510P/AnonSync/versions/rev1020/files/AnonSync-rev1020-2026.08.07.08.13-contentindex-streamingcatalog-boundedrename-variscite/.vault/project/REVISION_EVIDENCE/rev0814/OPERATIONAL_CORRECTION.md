# Cloudtainer operational correction

Two abandoned build roots still had compiler processes consuming the constrained
cloudtainer while the authoritative full build was running. They were identified
by exact command/root, terminated, and excluded from all source and evidence.
The authoritative source, build, sanitizer, fresh-validation, and seal roots are
separate.

This revision also avoids delayed cleanup against `/mnt/data`. The final archive
is assembled under an isolated seal root and copied to `/mnt/data` only after
manifest generation and verification. Build trees, VCS metadata, compiler
outputs, Python bytecode, and stale work roots are excluded by package policy.
