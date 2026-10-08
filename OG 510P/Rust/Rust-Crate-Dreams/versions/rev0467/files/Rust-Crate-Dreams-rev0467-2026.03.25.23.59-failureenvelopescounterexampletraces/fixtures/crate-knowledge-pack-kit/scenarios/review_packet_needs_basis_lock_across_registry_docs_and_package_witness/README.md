# Scenario — review packet needs a basis lock across registry, docs, and packaged-state witnesses

Question:
- if another engineer receives a crate review packet, what compact lock tells them exactly which registry, docs, and packaged-state witnesses that packet stands on?

Why this belongs here:
- current official Rust surfaces now expose enough machine-readable structure that “we reviewed the crate” is no longer a sufficient artifact description;
- the reviewer needs to know whether the packet was based on a registry record, a packaged release, a hosted docs surface, or a loose repository browse;
- and those distinctions matter most in hard domains, restricted environments, and long-lived product lines.

Expected packet behavior:
- the knowledge pack should emit `basis-lock.manifest.json` as a compact inventory of witness members;
- the lock should keep registry release, docs witness, package witness, and imported trust surfaces distinct;
- the lock should record target filters, publication windows, and declared incompletenesses where relevant;
- the packet should keep `task_fit`, `runtime_performance`, and `safety_case` in manual-review zones unless explicit basis exists.

What this scenario guards against:
- pretending that a docs.rs page and a packaged release are interchangeable;
- mistaking trusted publishing or advisory imports for architecture approval;
- shipping a compact assistant packet that cannot say what evidence it stands on;
- giving another team a decision packet that cannot be replayed later.

Relevant sources:
- cargo metadata
- Cargo external tools
- cargo package
- Cargo registries / registry index
- docs.rs metadata
- docs.rs rustdoc JSON
- crates.io development update
