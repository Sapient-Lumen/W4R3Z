# RP-0060 — opaque whiteouts, phase order, and record denial

Official OCI v1.1.1 material was re-read for opaque-whiteout scope and application order. The crucial result is not merely that `.wh..wh..opq` hides lower children: whiteouts apply to pre-existing lower state before ordinary same-layer entries, regardless of tar-member order. That rule exposed a bug in the incoming sequential simulator and enabled P0004-D002 to put `NO APPEAL ON FILE` before a last-position opaque marker without losing the status file.

The checker now uses phase semantics and a project-local closed-world blob contract. D001 was cold-reviewed `revise_not_promote`; D002 remains same-turn unjudged. See `docs/40-audits/P0004_D001_COLD_REVIEW_D002_OPAQUE_PHASE_BLOB_CLOSURE_AUDIT_rev0068.md`.

No quality, admission, reader-response, or publication claim follows from specification conformance.
