# Artifact dependency graph and control plane

The ready-but-not-closed state now has many files. A dependency graph prevents the maintainer from
reviewing them as isolated artifacts.

The graph does not prove that a service works. It shows which records depend on which validators and
which human-facing surfaces must be read together before any real-import closeout can change the
queue.

## Dependency states

| Code | Meaning |
|---|---|
| `DG0` | no graph exists |
| `DG1` | nodes are listed but not path-checked |
| `DG2` | nodes and edges are path-checked |
| `DG3` | every terminal gate has validator and human-artifact dependencies |
| `DG4` | graph is release-reviewed and tied to the live queue |
| `DGX` | graph is stale, cyclic in a harmful way, or missing a new gate |

## Required terminal gates

The graph must keep these gates visible:

- `FT-0181` live queue state;
- no-fake-real-import guard;
- synthetic/example source-status declaration;
- policy-exception register;
- release candidate state;
- release audit manifest;
- assurance case;
- control coverage matrix;
- evidence refresh calendar;
- human signoff quorum;
- closure evidence checklist.

## Review questions

1. Does every gate have at least one validator and at least one human-readable surface?
2. Does the graph distinguish release controls from service-effectiveness evidence?
3. Does the graph name the remaining real-world unblocker rather than hiding it in tooling?
4. Does a new schema or validator appear as a node before it is cited by a release claim?

See `examples/dependency-graphs/rev0224-control-plane-graph.json` and
`tools/check_artifact_dependency_graphs.py`.
