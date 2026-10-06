# RFC-0105: Remote cache threat model + mitigations

Status: Draft

## Summary

Define security boundaries for remote caches (CAS + action cache) and require verification so remote caches remain performance optimizers, not authorities.

## Motivation

Remote caching is common in large build systems, but it introduces poisoning and replay risks if the trust model is underspecified.

## Design sketch

- key lookups by `plan_digest` + target kind + builder ABI
- verify all returned blobs/trees by digest before import
- accept as “trusted” only after publish-domain signing + policy gates
- optional cache fetch receipts for audit/transparency

## References

- Bazel remote caching: https://bazel.build/remote/caching
- Bazel remote execution overview: https://bazel.build/remote/rbe
- Deep dive on remote caching security issues: https://blogsystem5.substack.com/p/bazel-remote-caching

